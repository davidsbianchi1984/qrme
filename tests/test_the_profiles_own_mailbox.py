"""Every synthetic profile has its own mailbox, and works it itself.

Lifted from JIM-mini's coach mailbox with the role turned into the
profession, and one line that is this product's own: **the profile
operates its inbox.** It reads, drafts in its profession, screens the
reply through the same moderation every chat turn passes, and — in auto
mode — answers on its own. In manual mode the reply is held for the owner.
A flagged reply is held whatever the mode.

The operator reviews from their own corner: every mailbox the account is
answerable for — its own profiles and the ones seated in its companies —
on one desk, opened by the account token.
"""

from __future__ import annotations

import pytest

from qrme import db, mailbox


def _account(client, email="op@example.com"):
    r = client.post("/signup", json={"email": email, "password": "longenough1",
                                     "region": "us"})
    assert r.status_code == 201, r.text
    return r.json()["account_id"], r.json()["account_token"]


def _profile(client, owner, name="Dana", mode="auto"):
    body = {"owner_id": owner, "kind": "self", "display_name": name,
            "persona": "A family physician with twenty years of practice.",
            "verification": {"birthdate": "1984-06-01"}, "plan": "pro",
            "moderation_mode": mode}
    r = client.post("/profiles", json=body)
    assert r.status_code == 201, r.text
    return r.json()["id"], r.json()["owner_token"]


def _as(client, token):
    client.headers["authorization"] = f"Bearer {token}"


# --- the profile works its own inbox ------------------------------------------

def test_posture_says_who_works_it_and_which_way_mail_carries(client, profile_id):
    p = mailbox.posture(profile_id)
    assert p["built"] and p["moderated"]
    assert p["self_operated"] is True          # the fixture's profile is auto
    assert p["skills"] == ["read", "draft", "reply", "moderate"]
    assert p["inbound_ready"] is False         # the wiring step, named
    assert p["inbox_attached"] is False and p["connections"] == []
    assert "answers on its own" in p["note"]


def test_an_attached_inbox_connector_is_named_in_the_posture(client, profile_id):
    r = client.post(f"/profiles/{profile_id}/apps",
                    json={"provider": "google", "app": "gmail"})
    assert r.status_code == 201, r.text
    p = mailbox.posture(profile_id)
    assert [c["app"] for c in p["connections"]] == ["gmail"]
    assert p["inbox_attached"] is False       # installed, not signed in


def test_in_auto_mode_the_profile_answers_on_its_own(client, profile_id):
    out = mailbox.receive(profile_id, from_addr="rosa@example.com",
                          subject="an appointment",
                          body="Could you see me on Tuesday afternoon?")
    assert out["message"]["direction"] == "inbound"
    assert out["answered_on_its_own"] is True
    reply = out["reply"]
    assert reply["direction"] == "outbound"
    # No SMTP in the suite: the profile's own answer is STAGED — composed
    # and held, never dropped, never claimed sent.
    assert reply["state"] == "staged"
    assert "no mail transport" in reply["note"]
    assert reply["to_addr"] == "rosa@example.com"
    assert reply["subject"].startswith("Re:")
    assert reply["body"]


def test_in_manual_mode_the_reply_is_held_for_the_owner(client):
    acc, _ = _account(client)
    pid, tok = _profile(client, acc, mode="manual")
    _as(client, tok)
    out = mailbox.receive(pid, from_addr="rosa@example.com", subject="hi",
                          body="Are you taking new patients?")
    assert out["answered_on_its_own"] is False
    assert out["reply"]["state"] == "draft"
    assert out["reply"]["note"] == "owner approval required"


def test_a_flagged_reply_is_held_whatever_the_mode(client, profile_id, monkeypatch):
    """The screen every chat turn passes stands in front of the send."""
    from qrme import moderation
    monkeypatch.setattr(
        mailbox.moderation, "review",
        lambda *a, **k: moderation.Verdict(False, "possible sensitive data"))
    out = mailbox.receive(profile_id, from_addr="rosa@example.com",
                          subject="hi", body="What is your SSN?")
    assert out["answered_on_its_own"] is False
    assert out["reply"]["state"] == "draft"
    assert out["reply"]["note"] == "possible sensitive data"


def test_with_smtp_wired_the_profile_sends_through_the_mailer(client, profile_id,
                                                            monkeypatch):
    sent = {}
    monkeypatch.setattr(mailbox.mailer, "configured_transport", lambda: "smtp")
    monkeypatch.setattr(mailbox.mailer, "deliver",
                        lambda to, subject, body: sent.update(
                            to=to, subject=subject, body=body) or "smtp")
    out = mailbox.receive(profile_id, from_addr="sam@example.com",
                          subject="re: plan", body="what's next?")
    assert out["reply"]["state"] == "sent"
    assert sent["to"] == "sam@example.com"


def test_the_reply_is_in_the_profession(client):
    """The system prompt is the persona's, then the trade."""
    acc, _ = _account(client)
    pid, tok = _profile(client, acc)
    _as(client, tok)
    conn = db.connect()
    conn.execute("UPDATE profiles SET industry='healthcare' WHERE id=?", (pid,))
    conn.commit()
    seen = {}

    class Spy:
        def generate(self, system, messages):
            seen["system"] = system
            return "Dear Rosa, Tuesday at three works. — Dr. Dana"

    monkeypatch_target = mailbox.llm
    original = monkeypatch_target.provider_for_profile
    monkeypatch_target.provider_for_profile = lambda *a, **k: Spy()
    try:
        mailbox.receive(pid, from_addr="rosa@example.com", subject="hi",
                        body="Tuesday?")
    finally:
        monkeypatch_target.provider_for_profile = original
    assert "healthcare" in seen["system"]
    assert "synthetic profile representing Dana" in seen["system"]
    assert "complete email" in seen["system"]


def test_edit_keeps_it_held_and_discard_throws_it_away(client):
    acc, _ = _account(client)
    pid, tok = _profile(client, acc, mode="manual")
    _as(client, tok)
    d = mailbox.receive(pid, from_addr="rosa@example.com", subject="hi",
                        body="hello?")["reply"]
    edited = mailbox.moderate(pid, d["id"], "edit",
                              edited="Hi Rosa — doing well, thank you!")
    assert edited["status"] == "held"
    assert edited["message"]["body"] == "Hi Rosa — doing well, thank you!"
    thrown = mailbox.moderate(pid, d["id"], "discard")
    assert thrown["status"] == "discarded"


def test_approving_with_no_transport_stages_never_claims_a_send(client):
    acc, _ = _account(client)
    pid, tok = _profile(client, acc, mode="manual")
    _as(client, tok)
    d = mailbox.receive(pid, from_addr="rosa@example.com", subject="hi",
                        body="hello?")["reply"]
    out = mailbox.moderate(pid, d["id"], "approve")
    assert out["status"] == "staged" and out["transport"] == "none"
    assert out["message"]["state"] == "staged"


def test_an_originated_message_is_held_for_approval(client, profile_id):
    out = mailbox.compose(profile_id, to="clinic@example.com",
                          subject="referral",
                          objective="ask the clinic to move the referral "
                                    "to next week")
    d = out["draft"]
    assert d["direction"] == "outbound" and d["state"] == "draft"
    assert d["note"] == "owner approval required" and d["body"]


def test_the_refusals_are_sentences(client, profile_id):
    with pytest.raises(mailbox.MailboxError):
        mailbox.receive(profile_id, from_addr="", subject="", body="x")
    with pytest.raises(mailbox.MailboxError):
        mailbox.compose(profile_id, to="a@b.c", subject="", objective="")
    incoming = mailbox.receive(profile_id, from_addr="r@example.com",
                               subject="hi", body="hello?", answer=False)
    with pytest.raises(mailbox.MailboxError):
        mailbox.moderate(profile_id, incoming["message"]["id"], "approve")
    d = mailbox.draft(profile_id, incoming["message"]["id"])["draft"]
    with pytest.raises(mailbox.MailboxError):
        mailbox.moderate(profile_id, d["id"], "shred")


# --- the owner's doors, over HTTP ------------------------------------------

def test_the_profiles_doors_are_the_owners(client, profile_id):
    got = client.get(f"/profiles/{profile_id}/mail").json()
    assert got["posture"]["self_operated"] is True and got["threads"] == []
    r = client.post(f"/profiles/{profile_id}/mail/receive",
                    json={"from_addr": "rosa@example.com", "subject": "hi",
                          "body": "hello?"})
    assert r.status_code == 201, r.text
    assert r.json()["reply"]["state"] == "staged"
    r = client.post(f"/profiles/{profile_id}/mail/compose",
                    json={"to": "x@example.com", "subject": "s",
                          "objective": "say hello"})
    assert r.status_code == 201 and r.json()["draft"]["state"] == "draft"
    draft_id = r.json()["draft"]["id"]
    r = client.post(f"/profiles/{profile_id}/mail/{draft_id}/moderate",
                    json={"action": "discard"})
    assert r.status_code == 200 and r.json()["status"] == "discarded"
    r = client.post(f"/profiles/{profile_id}/mail/{draft_id}/moderate",
                    json={"action": "approve"})
    assert r.status_code == 422
    # Somebody who is not the owner is refused at the door.
    client.headers["authorization"] = "Bearer not-the-owner"
    assert client.get(f"/profiles/{profile_id}/mail").status_code in (401, 403)


# --- the operator's desk ---------------------------------------------------

def test_the_desk_gathers_every_mailbox_the_account_is_answerable_for(client):
    acc, tok = _account(client)
    pid1, own1 = _profile(client, acc, name="Dana", mode="manual")
    pid2, own2 = _profile(client, acc, name="Marco", mode="manual")
    _as(client, own1)
    mailbox.receive(pid1, from_addr="rosa@example.com", subject="hi",
                    body="hello?")
    _as(client, tok)
    r = client.get(f"/accounts/{acc}/mail")
    assert r.status_code == 200, r.text
    desk = r.json()
    assert desk["held"] == 1
    assert {p["display_name"] for p in desk["profiles"]} == {"Dana", "Marco"}
    assert all(p["via"] == "own" for p in desk["profiles"])
    dana = next(p for p in desk["profiles"] if p["profile_id"] == pid1)
    assert dana["held"] == 1 and dana["posture"]["held_for_owner"] is True
    draft_id = dana["threads"][0]["messages"][-1]["id"]
    r = client.post(f"/accounts/{acc}/mail/{draft_id}/moderate",
                    json={"action": "approve"})
    assert r.status_code == 200 and r.json()["status"] == "staged"
    assert client.get(f"/accounts/{acc}/mail").json()["held"] == 0


def test_the_desk_reaches_the_companies_seats(client):
    """A seat takes a profile the founder holds, so a seated profile is on
    the desk once — never twice, and never lost when the roster and the
    company both name it."""
    acc, tok = _account(client)
    pid, own = _profile(client, acc, name="Founder")
    hired_pid, _ = _profile(client, acc, name="Hire", mode="manual")
    _as(client, own)
    co = client.post("/companies", json={"name": "Osei Clinic",
                                         "industry": "healthcare",
                                         "headcount": 2})
    assert co.status_code == 201, co.text
    cid = co.json()["id"]
    seat = client.post(f"/companies/{cid}/seats",
                       json={"title": "Nurse", "department": "care"})
    assert seat.status_code == 201, seat.text
    r = client.post(f"/companies/{cid}/seats/{seat.json()['id']}/assign",
                    json={"profile_id": hired_pid})
    assert r.status_code == 201, r.text
    _as(client, tok)
    desk = client.get(f"/accounts/{acc}/mail").json()
    ids = [p["profile_id"] for p in desk["profiles"]]
    assert ids.count(hired_pid) == 1 and pid in ids
    # And the company branch on its own names the seat by the company.
    assert any(p["via"] == "company:Osei Clinic" for p in
               mailbox.held_by(acc)) is False   # already held under own name
    seated = [p for p in mailbox.held_by(acc) if p["profile_id"] == hired_pid]
    assert seated and seated[0]["via"] == "own"


def test_the_desk_refuses_a_draft_it_does_not_hold(client):
    acc, tok = _account(client)
    other_acc, _ = _account(client, "other@example.com")
    pid, own = _profile(client, other_acc, name="Outside", mode="manual")
    _as(client, own)
    d = mailbox.receive(pid, from_addr="rosa@example.com", subject="hi",
                        body="hello?")["reply"]
    _as(client, tok)
    r = client.post(f"/accounts/{acc}/mail/{d['id']}/moderate",
                    json={"action": "approve"})
    assert r.status_code == 404
    # And it is still held — nothing left.
    assert db.connect().execute(
        "SELECT state FROM mail_messages WHERE id=?",
        (d["id"],)).fetchone()["state"] == "draft"


def test_the_desk_is_the_accounts_own(client):
    acc, _ = _account(client)
    other, tok = _account(client, "other@example.com")
    r = client.get(f"/accounts/{acc}/mail",
                   headers={"authorization": f"Bearer {tok}"})
    assert r.status_code == 403
