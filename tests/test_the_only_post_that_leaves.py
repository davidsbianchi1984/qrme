"""The post that actually left carried no credential.

`POST /social/{cid}/publish` writes a profile's words to a platform QRME does
not run. It is the one route in this product where synthetic media genuinely
**leaves the building** — and it stored that post with `watermark_id` NULL,
while `compose_post`, the in-app equivalent, stamped one every single time.

`compose_post` even says why, in a sentence that describes this route more
exactly than the one it is written above:

    A public post is synthetic media leaving the platform: it carries a
    verifiable synthetic-media credential from the moment it exists.

So the only posts going out unmarked were the ones actually going out.

The same route ran `profile["maturity"]` as its moderation filter, where
`compose_post` forces `strict` with the note *public posts face the widest
audience: always the strict filter*. A profile whose owner set it to `open`
was therefore held to the loosest rule on the way to an audience QRME cannot
see, and to the strictest one when posting where it can. Both directions of
that are wrong and they were wrong in the same function.

This file also closes the audit. With the eighteen routes this round doored,
QRME's console backlog reaches **zero** and every `api.ts` binding has a
caller — so both record files are empty rather than merely short, and the
tests that read them now assert emptiness.
"""

from __future__ import annotations

from pathlib import Path

from qrme import db


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()


def _publisher(client, maturity="open", account="acct_out"):
    """A profile with a publish connection, set as permissive as it goes."""
    p = client.post("/profiles", json={
        "owner_id": account, "kind": "fictional", "display_name": "Rosa",
        "purpose": "creator_persona", "persona": "a neighbour",
        "maturity": maturity, "plan": "pro",
        "verification": {"birthdate": "1980-01-01"}}).json()
    head = {"authorization": f"Bearer {p['owner_token']}"}
    conn = client.post(f"/profiles/{p['id']}/social", headers=head, json={
        "platform": "mastodon", "handle": "@rosa", "direction": "publish"})
    assert conn.status_code == 201, conn.text
    return p["id"], head, conn.json()["id"]


def _last_post(profile_id: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM posts WHERE profile_id=? ORDER BY rowid DESC LIMIT 1",
        (profile_id,)).fetchone()
    return dict(row) if row else {}


# --- the credential ---------------------------------------------------------

def test_a_post_that_leaves_carries_a_credential(client):
    """The defect in one assertion."""
    pid, head, cid = _publisher(client)
    out = client.post(f"/social/{cid}/publish", headers=head,
                      json={"topic": "morning", "content": "hello everyone"})
    assert out.status_code == 201, out.text
    assert _last_post(pid)["watermark_id"], (
        "a post going to a platform we do not run was stored unmarked, while "
        "the same profile posting in-app was stamped")


def test_the_credential_comes_back_with_the_post(client):
    """Handed to the caller so whatever posts it onward can carry the
    disclosure, rather than having to go and look it up."""
    _pid, head, cid = _publisher(client, account="acct_hand")
    body = client.post(f"/social/{cid}/publish", headers=head,
                       json={"topic": "morning", "content": "hello"}).json()
    assert body["watermark"]["watermark_id"]
    assert "AI" in body["watermark"]["disclosure"]


def test_it_matches_what_the_in_app_path_does(client):
    """Two routes, one act. They should not disagree about whether the thing
    they made is marked."""
    pid, head, cid = _publisher(client, account="acct_match")
    client.post(f"/social/{cid}/publish", headers=head,
                json={"topic": "a", "content": "outward"})
    outward = _last_post(pid)
    client.post(f"/profiles/{pid}/compose", headers=head,
                json={"topic": "a"})
    inward = _last_post(pid)
    assert bool(outward["watermark_id"]) == bool(inward["watermark_id"]) is True


def test_the_credential_verifies(client):
    """Not merely present — checkable, which is the whole point of stamping
    rather than labelling."""
    _pid, head, cid = _publisher(client, account="acct_verify")
    body = client.post(f"/social/{cid}/publish", headers=head,
                       json={"topic": "morning",
                             "content": "hello everyone"}).json()
    checked = client.post("/watermarks/verify", json={
        "watermark_id": body["watermark"]["watermark_id"],
        "content": "hello everyone"})
    assert checked.status_code == 200
    assert checked.json()["valid"] is True


# --- the filter -------------------------------------------------------------

def test_the_strict_filter_runs_on_the_way_out(client):
    """A profile set to `open` does not get the open filter when the words are
    leaving for an audience we cannot see."""
    pid, head, cid = _publisher(client, maturity="open", account="acct_strict")
    out = client.post(f"/social/{cid}/publish", headers=head, json={
        "topic": "x", "content": "kill yourself, seriously"})
    assert out.status_code == 201
    body = out.json()
    assert body["status"] == "rejected", (
        "the profile's own maturity was being used, so `open` let this out "
        "of the building")
    assert body["content"] is None
    assert body["flag_reason"]


def test_a_rejected_post_is_not_counted_as_published(client):
    _pid, head, cid = _publisher(client, account="acct_count")
    client.post(f"/social/{cid}/publish", headers=head,
                json={"topic": "x", "content": "kill yourself, seriously"})
    rows = client.get(f"/profiles/{_pid}/social", headers=head).json()
    assert [r for r in rows if r["id"] == cid][0]["published"] == 0


# --- the connection's two directions ---------------------------------------

def test_a_publish_connection_does_not_collect(client):
    _pid, head, cid = _publisher(client, account="acct_dir")
    wrong = client.post(f"/social/{cid}/collect", headers=head,
                        json={"items": [{"content": "something"}]})
    assert wrong.status_code == 409
    assert "for publishing, not collecting" in wrong.json()["detail"]


def test_only_the_owner_publishes(client):
    _pid, _head, cid = _publisher(client, account="acct_own")
    other = client.post("/profiles", json={
        "owner_id": "acct_own2", "kind": "fictional", "display_name": "Sal",
        "purpose": "creator_persona", "persona": "x", "plan": "pro",
        "verification": {"birthdate": "1980-01-01"}}).json()
    theirs = {"authorization": f"Bearer {other['owner_token']}"}
    body = {"topic": "x", "content": "hello"}
    assert client.post(f"/social/{cid}/publish",
                       json=body).status_code == 401
    assert client.post(f"/social/{cid}/publish", headers=theirs,
                       json=body).status_code == 403


# --- the audit reaches zero -------------------------------------------------

def test_the_console_backlog_record_is_empty():
    """Not short — empty. Every route in the app is reachable from the
    desktop console on its own, without borrowing a phone."""
    rec = (REPO / "tests/console_doorless.txt").read_text().strip()
    assert rec == "", f"still recorded as doorless:\n{rec}"


def test_the_unused_binding_record_is_empty():
    """And every binding written in `api.ts` has a screen that calls it, so
    the two halves of the audit agree."""
    rec = (REPO / "tests/unused_bindings.txt").read_text().strip()
    assert rec == "", f"still called by nothing:\n{rec}"


def test_the_screen_calls_the_last_of_them():
    src = (REPO / "app/src/screens/Remainder.tsx").read_text(encoding="utf-8")
    for binding in ("api.feedback(", "api.sendFeedback(", "api.packRegistries(",
                    "api.syncRegistry(", "api.pack(", "api.profileApps(",
                    "api.connectApp(", "api.excursions(", "api.startExcursion(",
                    "api.learnFromExcursion(", "api.steeringHub(",
                    "api.setSteeringHub(", "api.gameSessions(",
                    "api.startGameSession(", "api.gameCallout(",
                    "api.endGameSession(", "api.collectSocial(",
                    "api.publishSocial("):
        assert binding in src, f"{binding} is still called by nothing"


def test_the_screen_shows_what_the_excursion_cost():
    """`redactions` and `left_host` are the feature. A screen that showed the
    findings and dropped those two would show the answer and hide the price
    of having asked."""
    src = (REPO / "app/src/screens/Remainder.tsx").read_text(encoding="utf-8")
    assert "t.redactions" in src and "t.left_host" in src


def test_the_screen_says_the_strict_filter_runs_outward():
    # The sentence moved into the l10n table when the screen was localized;
    # the screen must still look it up, and the table must still say it.
    src = (REPO / "app/src/screens/Remainder.tsx").read_text(encoding="utf-8")
    assert 'tr("rem.pub.pitch", lang)' in src
    flat = " ".join(
        (REPO / "app/src/l10n.ts").read_text(encoding="utf-8").split())
    assert "not the profile's own setting" in flat
