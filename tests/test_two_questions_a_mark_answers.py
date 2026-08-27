"""What a mark says, and what a screen must not shorten it to.

Checking a credential asks **two separate questions**:

* was this issued by this deployment — ``valid``;
* is this the content it was issued for — ``content_match``.

They can disagree, and the interesting case is exactly the one where they do: a
genuine credential whose content has since been altered comes back
``valid: true, content_match: false``, with a ``note`` saying so in words. A
screen that reported ``valid`` alone would tell somebody the thing in front of
them is genuine at the precise moment the server said it had been changed —
which is the one failure a provenance check must not have, because it is worse
than having no check at all.

The rest of this file covers the surface that check sits on: the assistant's
own work (triage, proofreading, composing), the wearables its watch faces run
on, the reviews left by people who actually talked to it, and the correction of
something you said yourself.

Two of those carry an argument the console renders verbatim rather than
summarising:

* **a room-facing microphone is refused with a paragraph.** A smart speaker
  "hears whoever walks into the room, and they did not pair it, were not asked,
  and may have a right not to be recorded". "Unsupported device" would be a
  console throwing away somebody's reasoning;
* **triage returns the reason each item survived**, with its score. A pile
  sorted by a number nobody can see is a pile somebody has to re-check by hand,
  which is the work triage was supposed to do.
"""

from __future__ import annotations

from pathlib import Path

import pytest


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()


def _owner(client, account="acct_assist"):
    p = client.post("/profiles", json={
        "owner_id": account, "kind": "fictional", "display_name": "Helper",
        "purpose": "companion_coach", "persona": "p",
        "verification": {"birthdate": "1990-01-01"},
    }).json()
    token = p["owner_token"]
    client.post(f"/memberships/{account}", json={"plan": "pro"},
                headers={"authorization": f"Bearer {token}"})
    return p, {"authorization": f"Bearer {token}"}


def _talker(client, profile_id):
    """Somebody who has actually talked to it — the review gate needs one."""
    who = client.post("/interactors", json={"display_name": "Sam"}).json()
    head = {"authorization": f"Bearer {who['token']}"}
    client.post(f"/profiles/{profile_id}/chat",
                json={"interactor_id": who["id"], "message": "hello there"},
                headers=head)
    return who, head


# --- the mark ---------------------------------------------------------------

def test_a_real_credential_on_altered_content_says_both_things(client):
    """The case the whole file is named for.

    `valid` stays true — the credential was issued here and is intact. What
    changed is the content, and `content_match` is the only field that says
    so. Reporting one without the other is reporting the opposite of what
    happened.
    """
    p, head = _owner(client, "acct_mark")
    work = client.post(f"/profiles/{p['id']}/assist/compose",
                       json={"kind": "note", "moment": "the first frost"},
                       headers=head).json()
    wid = work["watermark"]["watermark_id"]

    same = client.post("/watermarks/verify",
                       json={"watermark_id": wid,
                             "content": work["content"]}).json()
    assert same["valid"] is True and same["content_match"] is True

    altered = client.post("/watermarks/verify",
                          json={"watermark_id": wid,
                                "content": work["content"] + " and more"}).json()
    assert altered["valid"] is True, (
        "the credential is intact; it is the content that changed")
    assert altered["content_match"] is False
    assert altered.get("note"), (
        "a mismatch with no sentence — the screen has nothing to say to "
        "somebody holding altered content")


def test_an_unknown_mark_says_it_was_not_issued_here(client):
    r = client.post("/watermarks/verify",
                    json={"watermark_id": "wmk_nope", "content": "x"})
    assert r.status_code == 404
    assert "not credentialed by this" in r.json()["detail"]


def test_the_record_alone_makes_no_claim_about_content(client):
    """`GET /watermarks/{id}` answers the first question only. It has no
    content to compare against, so it must not carry `content_match` — a
    field absent is honest, a field defaulting to true is not."""
    p, head = _owner(client, "acct_record")
    work = client.post(f"/profiles/{p['id']}/assist/compose",
                       json={"kind": "note", "moment": "a moment"},
                       headers=head).json()
    rec = client.get(f"/watermarks/{work['watermark']['watermark_id']}").json()
    assert rec["valid"] is True
    assert "content_match" not in rec, (
        "the bare record is claiming something about content it never saw")


# --- the assistant ----------------------------------------------------------

def test_triage_says_why_each_survivor_survived(client):
    """The ranking is deliberately transparent — `_score` in `assistant.py`
    is arithmetic anybody can read. A result that gave an order and no
    reasons would put the checking back on the person."""
    p, head = _owner(client, "acct_triage")
    r = client.post(f"/profiles/{p['id']}/assist/triage", headers=head, json={
        "items": [{"id": "a", "text": "Led the rebuild and shipped it."},
                  {"id": "b", "text": "ok"},
                  {"id": "c", "text": "Grew the team and delivered three."}],
        "keep": 2, "criteria": "leadership delivery"})
    assert r.status_code == 200, r.text
    out = r.json()
    assert out["reviewed"] == 3 and len(out["kept"]) == 2
    for kept in out["kept"]:
        assert kept["reason"], f"{kept['id']} was kept for no stated reason"
        assert "score" in kept["reason"], (
            "the reason no longer quotes the score, so the ranking stopped "
            "being arguable")
    assert out["discarded_ids"] == ["b"]


def test_proofreading_gives_the_change_and_the_reason(client):
    p, head = _owner(client, "acct_proof")
    out = client.post(f"/profiles/{p['id']}/assist/proofread",
                      json={"text": "we was going too the shop"},
                      headers=head).json()
    assert out["original"] == "we was going too the shop"
    assert out["edited"]
    assert isinstance(out["suggestions"], list)
    assert out["watermark"]["watermark_id"], (
        "a rewrite with no mark — generated text that does not say it is")


def test_a_composed_work_is_kept_and_marked(client):
    p, head = _owner(client, "acct_work")
    made = client.post(f"/profiles/{p['id']}/assist/compose",
                       json={"kind": "poem", "moment": "the allotment"},
                       headers=head).json()
    works = client.get(f"/profiles/{p['id']}/assist/works",
                       headers=head).json()
    assert [w["id"] for w in works] == [made["id"]]
    assert works[0]["watermark"]["display"]["line"]


# --- wearables --------------------------------------------------------------

def test_a_room_facing_microphone_is_refused_with_the_reason(client):
    """The sentence is the feature. Whoever walks into the room did not pair
    the thing, was not asked, and may have a right not to be recorded — and
    the console renders that rather than "unsupported device"."""
    p, head = _owner(client, "acct_mic")
    r = client.post(f"/profiles/{p['id']}/wearables",
                    json={"name": "kitchen puck", "kind": "smart_speaker"},
                    headers=head)
    assert r.status_code == 422
    detail = r.json()["detail"]
    assert "did not pair it" in detail
    assert "right not to be recorded" in detail


def test_the_refusals_are_published_before_anybody_tries(client):
    """Listed on the read, so the screen can show why a device is missing
    from the picker instead of letting somebody find out by failing."""
    p, head = _owner(client, "acct_micpub")
    view = client.get(f"/profiles/{p['id']}/wearables", headers=head).json()
    assert view["refusal_reasons"], "nothing is published as refused any more"
    for kind, why in view["refusal_reasons"].items():
        assert kind not in view["kinds_worn"], (
            f"{kind} is offered and refused at the same time")
        assert len(why) > 40, f"{kind} is refused without a reason"


def test_unpairing_keeps_the_row(client):
    """A device that was on somebody's wrist is a fact about the past. It is
    revoked, not deleted, and the row says when."""
    p, head = _owner(client, "acct_unpair")
    client.post(f"/profiles/{p['id']}/wearables",
                json={"name": "ring", "kind": "ring"}, headers=head)
    gone = client.delete(f"/profiles/{p['id']}/wearables/ring",
                         headers=head).json()
    assert gone["paired"] is False and gone["revoked_at"]

    # Gone from the default view, which is right — it is not on a wrist.
    live = client.get(f"/profiles/{p['id']}/wearables", headers=head).json()
    assert live["wearables"] == []

    # And still on the record, which is the promise. `include_revoked` is
    # the only way to see it, so a console that never asks makes a kept
    # promise invisible.
    kept = client.get(f"/profiles/{p['id']}/wearables?include_revoked=true",
                      headers=head).json()
    assert [w["name"] for w in kept["wearables"]] == ["ring"]
    assert kept["wearables"][0]["revoked_at"]


def test_a_wearable_is_addressed_by_name_not_id(client):
    """The route takes the name, and the row carries an id — the two are
    easy to swap, and swapping them 404s."""
    p, head = _owner(client, "acct_byname")
    made = client.post(f"/profiles/{p['id']}/wearables",
                       json={"name": "my watch", "kind": "watch"},
                       headers=head).json()
    assert client.delete(f"/profiles/{p['id']}/wearables/{made['id']}",
                         headers=head).status_code == 404
    assert client.delete(f"/profiles/{p['id']}/wearables/my%20watch",
                         headers=head).status_code == 200


# --- reviews ----------------------------------------------------------------

def test_a_review_needs_somebody_who_actually_talked(client):
    p, head = _owner(client, "acct_rev")
    stranger = client.post("/interactors",
                           json={"display_name": "Nobody"}).json()
    r = client.post(f"/profiles/{p['id']}/reviews", headers={
        "authorization": f"Bearer {stranger['token']}"},
        json={"interactor_id": stranger["id"], "rating": 5})
    assert r.status_code == 422
    assert "actually talked" in r.json()["detail"]


def test_the_empty_rating_carries_a_sentence_rather_than_a_zero(client):
    """`average` is null and `count` is 0 — the screen has nothing to
    average. A `note` says so, because "0.0 from 0 reviews" reads as a bad
    score rather than an absent one."""
    p, _ = _owner(client, "acct_norev")
    rating = client.get(f"/profiles/{p['id']}/reviews").json()["rating_summary"]
    assert rating["average"] is None and rating["count"] == 0
    assert rating.get("note"), "nothing to show instead of a phantom zero"


def test_a_review_from_somebody_who_talked_lands(client):
    p, _ = _owner(client, "acct_revok")
    who, head = _talker(client, p["id"])
    r = client.post(f"/profiles/{p['id']}/reviews", headers=head,
                    json={"interactor_id": who["id"], "rating": 5,
                          "body": "very helpful"})
    assert r.status_code == 201, r.text
    view = client.get(f"/profiles/{p['id']}/reviews").json()
    assert view["rating_summary"]["average"] == 5.0 and view["rating_summary"]["count"] == 1
    assert view["rating_summary"]["distribution"]["5"] == 1


# --- correcting your own turn ------------------------------------------------

def test_an_edit_marks_the_reply_that_answered_the_old_wording(client):
    """The reason the thread carries `answers_stale_text` at all.

    A conversation that silently rewrote itself would be worse than one that
    admits the answer above is to an older question, so the flag exists and
    the screen draws it.
    """
    p, _ = _owner(client, "acct_edit")
    who, head = _talker(client, p["id"])
    thread = client.get(f"/profiles/{p['id']}/thread/{who['id']}",
                        headers=head).json()
    mine = next(m for m in thread["thread_turns"] if m["role"] == "interactor")

    client.patch(f"/profiles/{p['id']}/messages/{mine['id']}", headers=head,
                 json={"interactor_id": who["id"],
                       "content": "hello there, actually"})
    after = client.get(f"/profiles/{p['id']}/thread/{who['id']}",
                       headers=head).json()["thread_turns"]
    edited = next(m for m in after if m["id"] == mine["id"])
    assert edited["edited"] is True and edited["content"].endswith("actually")
    assert any(m["answers_stale_text"] for m in after
               if m["role"] == "profile"), (
        "a reply written before the edit is no longer marked as answering "
        "the older wording")


def test_retracting_needs_a_body_saying_who(client):
    """A DELETE that carries a body, which several HTTP clients drop. It
    422s rather than guessing who is retracting — worth a test, because a
    client that silently sends no body would look like it worked."""
    p, _ = _owner(client, "acct_retract")
    who, head = _talker(client, p["id"])
    thread = client.get(f"/profiles/{p['id']}/thread/{who['id']}",
                        headers=head).json()
    mine = next(m for m in thread["thread_turns"] if m["role"] == "interactor")

    bodyless = client.request(
        "DELETE", f"/profiles/{p['id']}/messages/{mine['id']}", headers=head)
    assert bodyless.status_code == 422

    ok = client.request("DELETE", f"/profiles/{p['id']}/messages/{mine['id']}",
                        headers=head, json={"interactor_id": who["id"]})
    assert ok.status_code == 200, ok.text


# --- the console half -------------------------------------------------------

def _src(rel: str) -> str:
    return (REPO / rel).read_text(encoding="utf-8")


def test_the_assist_screen_exists():
    assert (REPO / "app/src/screens/Assist.tsx").exists()


@pytest.mark.parametrize("binding", [
    "api.triage(", "api.proofread(", "api.compose(", "api.works(",
    "api.wearables(", "api.pairWearable(", "api.unpairWearable(",
    "api.reviews(", "api.leaveReview(", "api.thread(", "api.editMessage(",
    "api.retractMessage(", "api.verifyWatermark(", "uploadMedia(",
])
def test_the_assist_screen_calls_it(binding):
    assert binding in _src("app/src/screens/Assist.tsx")


def test_the_screen_asks_both_questions_of_a_mark():
    """The defect this file is named for, guarded on the console side.

    Rendering `valid` and not `content_match` would compile, look right, and
    be wrong in exactly the case somebody checks a mark for.
    """
    src = _src("app/src/screens/Assist.tsx")
    assert "verdict.content_match" in src, (
        "the screen no longer asks whether the content matches — it would "
        "call altered content genuine")


def test_the_refusal_paragraphs_are_rendered_not_retyped():
    import re
    src = _src("app/src/screens/Assist.tsx")
    assert "devices.refusal_reasons" in src
    # Comments stripped: the docstring quotes the sentence on purpose, to say
    # why it is never retyped. It is the markup that must hold one copy.
    markup = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    markup = re.sub(r"^\s*//.*$", "", markup, flags=re.M)
    assert "did not pair it" not in markup, (
        "the room-microphone argument has been copied into the console; "
        "render the server's sentence so there is one copy of it")


def test_the_stale_answer_flag_is_drawn():
    """Checked at the render site, not anywhere in the file.

    The flag's name also appears in the docstring and in the type, so a
    substring search over the whole file passes even after the markup stops
    reading it — which is the same vacuous-guard shape this suite has now
    found twice.
    """
    import re

    src = _src("app/src/screens/Assist.tsx")
    markup = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    markup = re.sub(r"^\s*//.*$", "", markup, flags=re.M)
    assert re.search(r"\{m\.answers_stale_text\s*&&", markup), (
        "a reply to an edited message is no longer marked, so the thread "
        "quietly reads as if it had always said that")


def test_the_retract_binding_sends_a_body():
    api = _src("app/src/api.ts")
    i = api.index("retractMessage:")
    stanza = api[i:i + 400]
    assert "interactor_id: interactorId" in stanza, (
        "the DELETE no longer carries who is retracting, and the route 422s")


def test_the_media_upload_does_not_go_through_the_json_helper():
    """`req()` serialises JSON. A photo sent through it arrives as a JSON
    string of a File object, which the server would happily store."""
    api = _src("app/src/api.ts")
    i = api.index("export async function uploadMedia")
    stanza = api[i:i + 700]
    assert "body: file" in stanza
    assert "JSON.stringify" not in stanza
