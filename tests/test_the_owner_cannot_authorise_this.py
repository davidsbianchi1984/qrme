"""A beginning, an ending, what a profile is taught, and a press from a wrist.

The last five routes with no door, and the one worth reading twice is
succession.

**An owner token cannot be the gate on it.** The signal this route answers is
that the owner has died or cannot act, so requiring their authorisation would
be requiring the one thing known to be unavailable. A reviewer holds it
instead — outside profile ownership, against a verification reference kept out
of band. With somebody named, control passes and a fresh owner token is
minted. With nobody, the profile sunsets to memorial: **frozen rather than
orphaned**, because a profile whose owner has died and which nobody can reach
is worse than one that has plainly stopped.

A contested identity cannot be handed on. An open objection blocks succession
with a 409 — inheriting a profile somebody is disputing would settle the
dispute by transfer rather than by resolving it.

## And a route that asked for nothing at all

`POST /packs` took no token. Anybody could publish a pack to the marketplace,
name any string as the `publisher`, and name any account in
`publisher_owner_id` as the one sales accrue to. The argument against that was
already written down one module over, about gifts — *a body-supplied
beneficiary would let anyone direct a gift meant for a performer into their own
balance* — and this route was making the opposite choice. The account is now
read from the caller's own token.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()


REVIEWER = "a-reviewer-token-for-these-tests"


@pytest.fixture()
def reviewed(monkeypatch):
    """A deployment that has actually configured a reviewer.

    Without `QRME_ADMIN_TOKEN` set, `require_reviewer` takes its documented
    development path and lets any *local* caller through — which is every
    caller under TestClient. Succession would then appear to accept an owner
    token, and a test written against that would be asserting the dev mode
    rather than the rule.
    """
    monkeypatch.setenv("QRME_ADMIN_TOKEN", REVIEWER)
    return {"authorization": f"Bearer {REVIEWER}"}


def _profile(client, account="acct_pass", **extra):
    body = {"owner_id": account, "kind": "fictional", "display_name": "Rosa",
            "purpose": "companion_coach", "persona": "warm", "plan": "pro",
            "verification": {"birthdate": "1990-01-01"}}
    body.update(extra)
    p = client.post("/profiles", json=body).json()
    return p, {"authorization": f"Bearer {p['owner_token']}"}


# --- being born -------------------------------------------------------------

def test_a_profile_can_name_itself(client):
    """Leave the name blank and it picks one from the answers. A persona
    assembled from what somebody said about themselves should not then be
    handed a label by a form field."""
    r = client.post("/profiles/genesis", json={
        "owner_id": "acct_born",
        "verification": {"birthdate": "1990-01-01"},
        "answers": {"social_style": "warm but needs quiet evenings",
                    "humor": "dry, gentle teasing",
                    "what_matters": "family, honesty, the garden",
                    "comfort": "sits with you rather than fixing it"}})
    assert r.status_code == 201, r.text
    assert r.json()["display_name"], "it was born without a name"


def test_a_given_name_wins(client):
    r = client.post("/profiles/genesis", json={
        "owner_id": "acct_named2", "display_name": "Marguerite",
        "verification": {"birthdate": "1990-01-01"},
        "answers": {"social_style": "s", "humor": "h",
                    "what_matters": "w", "comfort": "c"}})
    assert r.json()["display_name"] == "Marguerite"


def test_a_minor_owner_needs_a_guardian(client):
    r = client.post("/profiles/genesis", json={
        "owner_id": "acct_minor2",
        "verification": {"birthdate": "2014-01-01"},
        "answers": {"social_style": "s", "humor": "h",
                    "what_matters": "w", "comfort": "c"}})
    assert r.status_code == 403
    assert "guardian consent" in r.json()["detail"]


def test_the_persona_is_built_from_the_answers(client):
    """Not stored as four fields and forgotten. If the interview did not
    reach the persona the questions would be theatre."""
    r = client.post("/profiles/genesis", json={
        "owner_id": "acct_persona",
        "verification": {"birthdate": "1990-01-01"},
        "answers": {"social_style": "warm but needs quiet evenings",
                    "humor": "dry, gentle teasing",
                    "what_matters": "the garden",
                    "comfort": "sits with you"}}).json()
    assert "garden" in r["persona"] or "quiet" in r["persona"]


# --- passing it on ----------------------------------------------------------

def test_the_owner_cannot_authorise_their_own_succession(client, reviewed):
    """The shape of the whole route. Requiring the owner's token would be
    requiring the one thing the signal says is unavailable."""
    p, head = _profile(client, "acct_succ")
    r = client.post(f"/profiles/{p['id']}/succeed", headers=head,
                    json={"verification_ref": "death-cert-1"})
    assert r.status_code in (401, 403), (
        "an owner token opened succession — which means anybody holding it "
        "can hand the profile away, and the dead cannot object")


def test_nobody_at_all_certainly_cannot(client, reviewed):
    p, _ = _profile(client, "acct_succ2")
    assert client.post(f"/profiles/{p['id']}/succeed",
                       json={"verification_ref": "x"}).status_code in (401, 403)


def test_a_reviewer_can_and_it_needs_a_reference(client, reviewed):
    p, _ = _profile(client, "acct_succ3")
    assert client.post(f"/profiles/{p['id']}/succeed", headers=reviewed,
                       json={}).status_code == 422


def test_with_nobody_named_it_freezes_rather_than_orphans(client, reviewed):
    """The default, and the kinder one. A profile whose owner has died and
    which nobody can reach is worse than one that has plainly stopped."""
    p, _ = _profile(client, "acct_freeze")
    r = client.post(f"/profiles/{p['id']}/succeed", headers=reviewed,
                    json={"verification_ref": "death-cert-2"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body.get("owner_token") in (None, ""), (
        "a fresh owner token was minted with nobody to give it to")
    assert "memorial" in str(body).lower() or body.get("status")


def test_an_open_objection_blocks_it(client, reviewed):
    """Inheriting a profile somebody is disputing would settle the dispute
    by transfer rather than by resolving it."""
    p, head = _profile(client, "acct_contested")
    opened = client.post("/objections", json={
        "profile_id": p["id"], "objector_ref": "passport-9",
        "reason": "this is my mother"})
    assert opened.status_code == 201, opened.text
    r = client.post(f"/profiles/{p['id']}/succeed", headers=reviewed,
                    json={"verification_ref": "death-cert-3"})
    assert r.status_code == 409
    assert "objection" in r.json()["detail"]


def test_it_cannot_happen_twice(client, reviewed):
    p, _ = _profile(client, "acct_twice2")
    client.post(f"/profiles/{p['id']}/succeed", headers=reviewed,
                json={"verification_ref": "ref"})
    again = client.post(f"/profiles/{p['id']}/succeed", headers=reviewed,
                        json={"verification_ref": "ref"})
    assert again.status_code == 409


def test_the_screen_says_who_may_open_it():
    src = _prose("app/src/screens/Passing.tsx")
    assert "reviewer" in src.lower()
    assert "frozen rather than orphaned" in src


# --- what it can be taught --------------------------------------------------

def test_publishing_needs_a_token(client):
    """It needed none. Anybody could publish under any publisher name."""
    r = client.post("/packs", json={
        "industry": "trades", "title": "Roofing", "price": 0,
        "publisher": "Bianchi",
        "items": [{"title": "flashing", "content": "where water gets in"}]})
    assert r.status_code == 401


def test_the_account_sales_accrue_to_comes_from_the_token(client):
    """Not from the body. A `publisher_owner_id` naming somebody else's
    account is how money ends up where it was not earned."""
    p, head = _profile(client, "acct_seller")
    made = client.post("/packs", headers=head, json={
        "industry": "trades", "title": "Roofing", "price": 25,
        "publisher": "Someone Else Entirely",
        "publisher_owner_id": "acct_victim",
        "items": [{"title": "flashing", "content": "water"}]})
    assert made.status_code == 201, made.text

    from qrme import db

    row = db.connect().execute(
        "SELECT publisher_owner_id FROM knowledge_packs WHERE id=?",
        (made.json()["id"],)).fetchone()
    assert row["publisher_owner_id"] == "acct_seller", (
        "the body's publisher_owner_id was taken at its word")


@pytest.mark.parametrize("body,says", [
    ({"industry": "t", "title": "T", "items": []},
     "at least one knowledge item"),
    ({"industry": "t", "title": "T", "price": -5,
      "items": [{"title": "a", "content": "b"}]}, "cannot be negative"),
    ({"industry": "t", "title": "T", "audience": "robot",
      "items": [{"title": "a", "content": "b"}]}, "needs a task"),
])
def test_each_refusal_names_what_is_missing(client, body, says):
    p, head = _profile(client, f"acct_ref{len(says)}")
    r = client.post("/packs", headers=head, json=body)
    assert r.status_code == 422
    assert says in r.json()["detail"]


def test_seeding_is_idempotent_and_reports_both_sides(client):
    """A press that reported only `created` would look like it had failed
    the second time rather than like there was nothing left to do."""
    first = client.post("/packs/seed").json()
    again = client.post("/packs/seed").json()
    assert first["created"] > 0
    assert again["created"] == 0 and again["skipped"] == first["created"]
    assert again["industries"] == first["industries"]


def test_the_screen_shows_both_counts():
    src = _markup("app/src/screens/Passing.tsx")
    assert "seeded.created" in src and "seeded.skipped" in src


# --- one press from the wrist -----------------------------------------------

def test_the_wrist_uses_the_same_door_as_everything_else(client):
    """No token, no action. A shortcut that skipped auth would be a second,
    weaker way in — which is exactly what a wrist should not be."""
    p, head = _profile(client, "acct_wrist")
    assert client.post(f"/profiles/{p['id']}/watch/act",
                       json={"target": "workflow", "id": "wf_x",
                             "action": "advance"}).status_code == 401


def test_assist_from_the_wrist_needs_input(client):
    """The paused phase asked for something. Sending nothing would advance
    past the question rather than answer it."""
    p, head = _profile(client, "acct_assist")
    wf = client.post(f"/profiles/{p['id']}/workflows", headers=head, json={
        "goal": "book the appointment"}).json()
    r = client.post(f"/profiles/{p['id']}/watch/act", headers=head, json={
        "target": "workflow", "id": wf.get("id", "wf_x"), "action": "assist"})
    assert r.status_code in (404, 422)
    if r.status_code == 422:
        assert "needs input" in r.json()["detail"]


def test_the_screen_says_the_wrist_is_not_a_shortcut():
    src = _prose("app/src/screens/Passing.tsx")
    assert "same paths" in src or "weaker way in" in src


# --- the console half -------------------------------------------------------

def _src(rel: str) -> str:
    return (REPO / rel).read_text(encoding="utf-8")


def _markup(rel: str) -> str:
    s = re.sub(r"/\*.*?\*/", "", _src(rel), flags=re.S)
    return re.sub(r"^\s*//.*$", "", s, flags=re.M)


def _prose(rel: str) -> str:
    """Comment-stripped markup with its wrapping collapsed.

    JSX prose is line-wrapped by the formatter, so a sentence a reader sees
    as one phrase is several tokens with newlines and indentation between
    them. Asserting on the raw text checks the formatter's choices as much
    as the writing.
    """
    return re.sub(r"\s+", " ", _markup(rel))


def test_the_screen_exists():
    assert (REPO / "app/src/screens/Passing.tsx").exists()


@pytest.mark.parametrize("binding", [
    "api.genesis(", "api.succeed(", "api.publishPack(", "api.seedPacks(",
    "api.watchAct(",
])
def test_the_screen_calls_it(binding):
    assert binding in _src("app/src/screens/Passing.tsx")


def test_succession_is_sent_with_a_reviewer_token_not_the_owners():
    """The console holds an owner token. Sending it here would be a 403 the
    user cannot act on, and would suggest the wrong mental model besides."""
    import sys

    sys.path.insert(0, str(REPO / "tests"))
    import clientpaths as cp

    src = _src("app/src/screens/Passing.tsx")
    start = src.index("api.succeed(") + len("api.succeed")
    call = cp._call_body(src, start)
    assert "reviewerToken" in call
    assert "ownerToken" not in call
