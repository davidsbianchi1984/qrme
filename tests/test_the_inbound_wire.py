"""Mail arrives in a profile's mailbox on its own.

3.0.3 built the mailbox and said, honestly, that inbound was the wiring
step: a message got in only when the operator handed it in. This is the
wire, in two shapes, and the posture that says which is connected:

* **the inbound address** — a per-profile webhook any mail provider's
  inbound-parse can post to, opened by a token the owner minted (shown
  once, hashed at rest, rotated by minting again), reading the field
  names SendGrid, Mailgun, Postmark and a plain JSON post all use;
* **the poll** — the attached Gmail, Outlook or Mail connector read over
  IMAP with the credential it was authorized with, sealed in the vault;
  on a press, or on the deployment's own poller when
  ``QRME_MAIL_POLL_MINUTES`` is set.

Either way the message lands through :func:`mailbox.receive`, so the
profile works it exactly as one handed in — drafts in its profession,
screens, answers on its own in auto mode, holds for the owner in manual.
"""

from __future__ import annotations

import json

import pytest

from qrme import db, mailbox


def _account(client, email="op@example.com"):
    r = client.post("/signup", json={"email": email, "password": "longenough1"})
    assert r.status_code == 201, r.text
    return r.json()["account_id"], r.json()["account_token"]


def _profile(client, owner, mode="auto"):
    r = client.post("/profiles", json={
        "owner_id": owner, "kind": "self", "display_name": "Dana",
        "persona": "A family physician.", "moderation_mode": mode,
        "verification": {"birthdate": "1984-06-01"}, "plan": "pro"})
    assert r.status_code == 201, r.text
    client.headers["authorization"] = f"Bearer {r.json()['owner_token']}"
    return r.json()["id"]


# --- the inbound address ---------------------------------------------------

def test_a_fresh_mailbox_has_no_inbound_wire(client, profile_id):
    p = mailbox.posture(profile_id)
    assert p["inbound_ready"] is False
    assert p["inbound"]["webhook_set"] is False
    assert p["inbound"]["pollable"] is False
    assert p["inbound"]["webhook_url"].endswith(f"/mail/inbound/{profile_id}")
    assert p["inbound"]["poll_minutes"] == 0


def test_the_token_is_minted_once_hashed_at_rest_and_rotates(client, profile_id):
    r = client.post(f"/profiles/{profile_id}/mail/inbound-token")
    assert r.status_code == 201, r.text
    first = r.json()
    assert first["shown_once"] is True and first["token"].startswith("mib_")
    assert first["url"].endswith(f"/mail/inbound/{profile_id}")
    held = db.connect().execute(
        "SELECT mail_inbound_token FROM profiles WHERE id=?",
        (profile_id,)).fetchone()["mail_inbound_token"]
    assert held and held != first["token"]          # the hash, not the token
    assert mailbox.posture(profile_id)["inbound_ready"] is True
    second = client.post(f"/profiles/{profile_id}/mail/inbound-token").json()
    assert mailbox.inbound_opens(profile_id, second["token"])
    assert not mailbox.inbound_opens(profile_id, first["token"])


def test_a_providers_post_lands_and_the_profile_works_it(client, profile_id):
    token = client.post(f"/profiles/{profile_id}/mail/inbound-token").json()["token"]
    # No credential on the client: this is the provider's call, not the owner's.
    client.headers.pop("authorization", None)
    r = client.post(f"/mail/inbound/{profile_id}",
                    headers={"x-mail-inbound-token": token},
                    json={"from": "Rosa <rosa@example.com>",
                          "subject": "an appointment",
                          "text": "Could you see me Tuesday?"})
    assert r.status_code == 201, r.text
    got = r.json()
    assert got["message"]["from_addr"] == "rosa@example.com"
    assert got["answered_on_its_own"] is True          # auto mode, staged
    assert got["reply"]["state"] == "staged"


def test_the_form_shapes_the_providers_use_all_land(client, profile_id):
    token = client.post(f"/profiles/{profile_id}/mail/inbound-token").json()["token"]
    client.headers.pop("authorization", None)
    # Mailgun's route: urlencoded, `sender` and `body-plain`.
    r = client.post(f"/mail/inbound/{profile_id}?token={token}",
                    data={"sender": "sam@example.com", "subject": "re: plan",
                          "body-plain": "what's next?"})
    assert r.status_code == 201, r.text
    assert r.json()["message"]["from_addr"] == "sam@example.com"
    # Postmark's: JSON with capitalised keys.
    r = client.post(f"/mail/inbound/{profile_id}",
                    headers={"x-mail-inbound-token": token},
                    json={"From": "lee@example.com", "Subject": "hello",
                          "TextBody": "hi there"})
    assert r.status_code == 201, r.text
    assert r.json()["message"]["subject"] == "hello"


def test_the_wrong_token_or_none_is_refused(client, profile_id):
    token = client.post(f"/profiles/{profile_id}/mail/inbound-token").json()["token"]
    client.headers.pop("authorization", None)
    body = {"from": "rosa@example.com", "text": "hello?"}
    assert client.post(f"/mail/inbound/{profile_id}", json=body).status_code == 403
    assert client.post(f"/mail/inbound/{profile_id}", json=body,
                       headers={"x-mail-inbound-token": "mib_wrong"}
                       ).status_code == 403
    assert client.post(f"/mail/inbound/{profile_id}", json=body,
                       headers={"x-mail-inbound-token": token}
                       ).status_code == 201


def test_a_post_with_no_sender_or_body_is_refused_in_words(client, profile_id):
    token = client.post(f"/profiles/{profile_id}/mail/inbound-token").json()["token"]
    client.headers.pop("authorization", None)
    r = client.post(f"/mail/inbound/{profile_id}",
                    headers={"x-mail-inbound-token": token},
                    json={"subject": "empty"})
    assert r.status_code == 422
    assert "sender address" in r.text


def test_the_token_is_the_owners_to_mint(client, profile_id):
    client.headers["authorization"] = "Bearer not-the-owner"
    assert client.post(f"/profiles/{profile_id}/mail/inbound-token"
                       ).status_code in (401, 403)


# --- the poll ----------------------------------------------------------------

class _Vault:
    """A vault with one sealed credential in it."""
    def __init__(self, ref, account, secret):
        self.ref, self.account, self.secret = ref, account, secret

    def get(self, key):
        if key == self.ref:
            return json.dumps({"account": self.account, "secret": self.secret})
        return None


def _attach(client, profile_id, app="gmail", provider="google", signed_in=True):
    r = client.post(f"/profiles/{profile_id}/apps",
                    json={"provider": provider, "app": app})
    assert r.status_code == 201, r.text
    cid = r.json()["id"]
    ref = f"qrme/{profile_id}/connectors/{cid}"
    if signed_in:
        conn = db.connect()
        conn.execute("UPDATE app_connectors SET authorized_at=?, secret_ref=?"
                     " WHERE id=?", (db.utcnow(), ref, cid))
        conn.commit()
    return cid, ref


def test_an_unsigned_connector_is_skipped_and_says_why(client, profile_id):
    _attach(client, profile_id, signed_in=False)
    got = mailbox.poll(profile_id)
    assert got["fetched"] == 0
    assert got["connectors"][0]["skipped"].startswith("not signed in")
    assert mailbox.posture(profile_id)["inbound"]["pollable"] is False


def test_no_vault_means_no_credential_and_the_poll_says_so(client, profile_id):
    _attach(client, profile_id)
    assert mailbox.posture(profile_id)["inbound"]["pollable"] is True
    got = mailbox.poll(profile_id, pdi=None)
    assert got["connectors"][0]["skipped"] == \
        "its credential could not be read from the vault"


def test_the_poll_reads_the_inbox_with_the_sealed_credential(client, profile_id):
    cid, ref = _attach(client, profile_id)
    vault = _Vault(ref, "dana@gmail.com", "app-password")
    seen = {}

    def fake_fetch(host, account, secret):
        seen.update(host=host, account=account, secret=secret)
        return [{"from_addr": "rosa@example.com", "subject": "hi",
                 "body": "Tuesday?"},
                {"from_addr": "", "subject": "junk", "body": "no sender"}]

    got = mailbox.poll(profile_id, pdi=vault, fetcher=fake_fetch)
    assert seen == {"host": "imap.gmail.com", "account": "dana@gmail.com",
                    "secret": "app-password"}
    assert got["fetched"] == 1 and got["answered"] == 1   # auto mode
    threads = mailbox.inbox(profile_id)
    assert threads[0]["correspondent"] == "rosa@example.com"
    assert threads[0]["messages"][-1]["state"] == "staged"


def test_in_manual_mode_polled_mail_is_held(client):
    acc, _ = _account(client)
    pid = _profile(client, acc, mode="manual")
    cid, ref = _attach(client, pid, app="outlook", provider="work")
    vault = _Vault(ref, "dana@outlook.com", "pw")
    got = mailbox.poll(pid, pdi=vault, fetcher=lambda *a: [
        {"from_addr": "rosa@example.com", "subject": "hi", "body": "hello?"}])
    assert got["held"] == 1 and got["answered"] == 0


def test_an_unreachable_inbox_is_said_not_hidden(client, profile_id):
    cid, ref = _attach(client, profile_id)
    vault = _Vault(ref, "dana@gmail.com", "pw")

    def broken(*a):
        raise ConnectionError("no route to host")

    got = mailbox.poll(profile_id, pdi=vault, fetcher=broken)
    assert got["connectors"][0]["skipped"] == \
        "the inbox could not be read: ConnectionError"
    assert got["fetched"] == 0


def test_offline_mode_keeps_the_poll_home(client, profile_id, monkeypatch):
    cid, ref = _attach(client, profile_id)
    vault = _Vault(ref, "dana@gmail.com", "pw")
    monkeypatch.setenv("QRME_OFFLINE", "1")
    got = mailbox.poll(profile_id, pdi=vault, fetcher=lambda *a: [
        {"from_addr": "rosa@example.com", "subject": "hi", "body": "hello?"}])
    assert got["fetched"] == 0
    assert "LeftTheHost" in got["connectors"][0]["skipped"]


def test_the_poll_door_is_the_owners(client, profile_id):
    r = client.post(f"/profiles/{profile_id}/mail/poll")
    assert r.status_code == 200, r.text
    assert r.json()["connectors"] == []
    client.headers["authorization"] = "Bearer not-the-owner"
    assert client.post(f"/profiles/{profile_id}/mail/poll").status_code in (401, 403)


# --- the poller ---------------------------------------------------------------

def test_the_poller_rounds_every_pollable_profile(client, profile_id):
    cid1, ref1 = _attach(client, profile_id)        # as the fixture's owner
    acc, _ = _account(client)
    other = _profile(client, acc)                    # now signed in as Dana's
    cid2, ref2 = _attach(client, other, app="mail", provider="apple")
    assert set(mailbox.pollable_profiles()) == {profile_id, other}

    class Both:
        def get(self, key):
            return json.dumps({"account": "a@b.c", "secret": "s"})

    got = mailbox.poll_all(pdi=Both(), fetcher=lambda *a: [
        {"from_addr": "rosa@example.com", "subject": "hi", "body": "hello?"}])
    assert got["profiles"] == 2 and got["fetched"] == 2


def test_the_poller_is_off_unless_the_deployment_says(monkeypatch):
    monkeypatch.delenv("QRME_MAIL_POLL_MINUTES", raising=False)
    assert mailbox.poll_minutes() == 0
    monkeypatch.setenv("QRME_MAIL_POLL_MINUTES", "15")
    assert mailbox.poll_minutes() == 15
    monkeypatch.setenv("QRME_MAIL_POLL_MINUTES", "soon")
    assert mailbox.poll_minutes() == 0

    class App:
        class state:
            pdi = None
            cloud = None

    monkeypatch.setenv("QRME_MAIL_POLL_MINUTES", "")
    assert mailbox.start_poller(App()) is None


def test_the_inbound_parse_takes_the_address_out_of_a_display_name():
    got = mailbox.parse_inbound({"From": "Rosa Díaz <rosa@example.com>",
                                 "Subject": "hi", "TextBody": "hello"})
    assert got == {"from_addr": "rosa@example.com", "subject": "hi",
                   "body": "hello"}


def test_a_multipart_post_lands_without_a_parser_this_image_lacks(client, profile_id):
    """SendGrid's Inbound Parse posts multipart/form-data. The image carries
    no form-parsing dependency, and does not need one: a multipart body is
    MIME, and the mail parser already here reads it."""
    token = client.post(f"/profiles/{profile_id}/mail/inbound-token").json()["token"]
    client.headers.pop("authorization", None)
    boundary = "xYzZY"
    body = (
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"from\"\r\n\r\n"
        f"Rosa <rosa@example.com>\r\n"
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"subject\"\r\n\r\n"
        f"parsed\r\n"
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"text\"\r\n\r\n"
        f"hello from a multipart post\r\n"
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"attachment1\"; "
        f"filename=\"a.txt\"\r\nContent-Type: text/plain\r\n\r\nignored\r\n"
        f"--{boundary}--\r\n").encode()
    r = client.post(f"/mail/inbound/{profile_id}",
                    headers={"x-mail-inbound-token": token,
                             "content-type": f"multipart/form-data; boundary={boundary}"},
                    content=body)
    assert r.status_code == 201, r.text
    assert r.json()["message"]["from_addr"] == "rosa@example.com"
    assert r.json()["message"]["body"] == "hello from a multipart post"
