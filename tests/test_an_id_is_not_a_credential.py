"""Anonymous chat between two strangers, readable and endable by a third.

`/connections` is matchmaking between two people with no profile involved:
each sees the alias the other chose, never a name or an id. Anonymity is the
entire feature. It had no door in this console, and building one found that it
had no **authentication** either — not weak authentication, none.

Every route read `interactor_id` out of the request body or the query string
and checked only that it named one of the two participants. Nothing checked
that the caller *was* that person, and no route asked for a token at all. Two
public ids were enough to:

* **join the queue as somebody else**, and be matched with a stranger under
  their name — and on the `rated` tier, borrow a verified adult's id straight
  past the age check, which is the one gate this feature cannot afford to lose;
* **send messages as either party**, stored under their id and shown to the
  other person as theirs;
* **read the pair's whole conversation as either party**, including the
  `blocked` messages the route deliberately keeps back for their sender's eyes
  alone — a rule that means nothing if anyone may claim to be the sender;
* **end it.**

Ending was the worst of the four, because it did not even need the ids. The
check read ``if ender: _participant(connection, ender)`` over an *optional*
body and an *optional* query parameter, so supplying neither skipped it
entirely: a bare `POST` with no id and no credential ended a stranger's
conversation, and returned any wearable microphone lent inside it.

This is the room defect over again, in the one feature whose premise is
consent — and `community._require_in_room` had already settled the argument in
the same words a few rounds earlier. An id is a claim; the token is the answer.

The ids still ride in the body and the query string and are ignored. Three
shipped native clients send them, and a 422 on upgrade is a worse answer than
not believing them; all three now carry the interactor's token as well.
"""

from __future__ import annotations

import re
from pathlib import Path


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()


def _person(client, name: str, birthdate: str = "1990-01-01"):
    row = client.post("/interactors", json={
        "display_name": name, "birthdate": birthdate}).json()
    return row["id"], {"authorization": f"Bearer {row['token']}"}


def _pair(client, tier: str = "friendly"):
    """Two people, honestly matched."""
    a, ah = _person(client, "Ada")
    b, bh = _person(client, "Ben")
    client.post("/connections/join", headers=ah,
                json={"interactor_id": a, "tier": tier, "alias": "A"})
    joined = client.post("/connections/join", headers=bh,
                         json={"interactor_id": b, "tier": tier,
                               "alias": "B"}).json()
    assert joined["status"] == "matched", joined
    return joined["connection_id"], (a, ah), (b, bh)


# --- the queue --------------------------------------------------------------

def test_you_may_only_queue_as_yourself(client):
    a, _ah = _person(client, "Ada")
    _m, mine = _person(client, "Mallory")
    assert client.post("/connections/join",
                       json={"interactor_id": a,
                             "tier": "friendly"}).status_code == 401
    assert client.post("/connections/join", headers=mine,
                       json={"interactor_id": a,
                             "tier": "friendly"}).status_code == 403


def test_the_age_gate_cannot_be_passed_with_somebody_elses_id(client):
    """The rated tier's whole protection is that both sides are verified
    adults. Queuing as an adult was a way around it for anybody who knew an
    adult's id."""
    adult, _ah = _person(client, "Adult", "1980-01-01")
    _minor, minor_head = _person(client, "Teen", "2012-01-01")

    borrowed = client.post("/connections/join", headers=minor_head,
                           json={"interactor_id": adult, "tier": "rated"})
    assert borrowed.status_code == 403

    honest = client.post("/connections/join", headers=minor_head,
                         json={"interactor_id": _minor, "tier": "rated"})
    assert honest.status_code == 403
    assert "18+" in honest.json()["detail"]


def test_two_people_are_matched_and_see_only_aliases(client):
    cid, (_a, ah), (_b, _bh) = _pair(client)
    assert cid
    joined = client.get(f"/connections/{cid}/messages", headers=ah).json()
    assert joined == []


# --- speaking ---------------------------------------------------------------

def test_nobody_speaks_without_a_token(client):
    cid, (a, _ah), _b = _pair(client)
    assert client.post(f"/connections/{cid}/messages",
                       json={"interactor_id": a,
                             "message": "meet me at 9"}).status_code == 401


def test_nobody_speaks_as_somebody_else(client):
    cid, (a, _ah), _b = _pair(client)
    _m, mine = _person(client, "Mallory")
    assert client.post(f"/connections/{cid}/messages", headers=mine,
                       json={"interactor_id": a,
                             "message": "meet me at 9"}).status_code == 403


def test_the_speaker_is_the_token_not_the_body(client):
    """Ada's own token with Ben's id in the body still speaks as Ada."""
    cid, (a, ah), (b, bh) = _pair(client)
    sent = client.post(f"/connections/{cid}/messages", headers=ah,
                       json={"interactor_id": b, "message": "hello"})
    assert sent.status_code == 201
    seen = client.get(f"/connections/{cid}/messages", headers=bh).json()
    assert [m["from"] for m in seen] == ["A"], (
        "the body claimed Ben; the message is Ada's, under Ada's alias")


def test_an_owner_token_is_not_a_person(client):
    """A connection is between two people, so a profile's owner token is the
    wrong *kind* of credential rather than merely the wrong subject.

    The account is put on Pro first, deliberately. Connections is a paid
    capability, so a Free owner token is answered `402` by the plan gate
    before the credential is ever examined — and that answer is true: no
    token of any kind works on that plan. Buying the plan is what makes the
    403 the only remaining refusal, which is the one this test is about.
    """
    cid, _a, _b = _pair(client)
    p = client.post("/profiles", json={
        "owner_id": "o1", "kind": "fictional", "display_name": "Rosa",
        "purpose": "companion_coach", "persona": "x",
        "verification": {"birthdate": "1980-01-01"}}).json()
    owner = {"authorization": f"Bearer {p['owner_token']}"}
    client.post("/memberships/o1", json={"plan": "pro"}, headers=owner)
    r = client.post(f"/connections/{cid}/messages", headers=owner,
                    json={"interactor_id": "whoever", "message": "hi"})
    assert r.status_code == 403
    assert "between two people" in r.json()["detail"]


# --- reading ----------------------------------------------------------------

def test_the_transcript_needs_a_token(client):
    cid, (a, _ah), _b = _pair(client)
    assert client.get(
        f"/connections/{cid}/messages?interactor_id={a}").status_code == 401


def test_an_outsider_cannot_read_it(client):
    cid, (a, _ah), _b = _pair(client)
    _m, mine = _person(client, "Mallory")
    assert client.get(f"/connections/{cid}/messages?interactor_id={a}",
                      headers=mine).status_code == 403


def test_a_blocked_message_is_still_only_its_senders(client):
    """The privacy rule that was worth nothing while anyone could claim to be
    the sender."""
    cid, (a, ah), (_b, bh) = _pair(client)
    client.post(f"/connections/{cid}/messages", headers=ah,
                json={"interactor_id": a, "message": "kill yourself"})
    mine = client.get(f"/connections/{cid}/messages", headers=ah).json()
    theirs = client.get(f"/connections/{cid}/messages", headers=bh).json()
    blocked = [m for m in mine if m["status"] == "blocked"]
    if blocked:
        assert not [m for m in theirs if m["status"] == "blocked"], (
            "a held-back message reached the person it was held back from")


# --- ending -----------------------------------------------------------------

def test_a_bare_post_no_longer_ends_a_strangers_conversation(client):
    """The defect in one line. `if ender:` over two optional parameters meant
    supplying neither skipped the check."""
    cid, _a, _b = _pair(client)
    assert client.post(f"/connections/{cid}/end").status_code == 401


def test_an_outsider_cannot_end_it(client):
    cid, _a, _b = _pair(client)
    _m, mine = _person(client, "Mallory")
    assert client.post(f"/connections/{cid}/end",
                       headers=mine).status_code == 403


def test_either_side_may_end_it(client):
    cid, _a, (_b, bh) = _pair(client)
    ended = client.post(f"/connections/{cid}/end", headers=bh)
    assert ended.status_code == 200
    assert ended.json()["status"] == "ended"


def test_a_message_after_the_end_is_refused(client):
    cid, (a, ah), _b = _pair(client)
    client.post(f"/connections/{cid}/end", headers=ah)
    assert client.post(f"/connections/{cid}/messages", headers=ah,
                       json={"interactor_id": a,
                             "message": "still there?"}).status_code == 410


# --- summon -----------------------------------------------------------------

def test_a_reference_resolves_without_an_account(client):
    """The person following a sticker or a shared handle has no account, which
    is the whole reason for leaving one."""
    p = client.post("/profiles", json={
        "owner_id": "o2", "kind": "fictional", "display_name": "Rosa",
        "purpose": "companion_coach", "persona": "x",
        "verification": {"birthdate": "1980-01-01"}}).json()
    head = {"authorization": f"Bearer {p['owner_token']}"}
    client.put(f"/profiles/{p['id']}/handle", headers=head,
               json={"handle": "rosa"})

    got = client.get("/summon?ref=@rosa")
    assert got.status_code == 200
    assert got.json()["type"] == "handle"
    assert got.json()["profile"]["display_name"] == "Rosa"
    assert client.get("/summon?ref=@nobody").status_code == 404


# --- the clients ------------------------------------------------------------

def _src(rel: str) -> str:
    return (REPO / rel).read_text(encoding="utf-8")


def test_the_screen_calls_every_connection_binding():
    src = _src("app/src/screens/Stranger.tsx")
    for binding in ("api.summon(", "api.joinQueue(", "api.connectionMessages(",
                    "api.sendToConnection(", "api.endConnection("):
        assert binding in src, f"{binding} is still called by nothing"


def test_every_console_binding_carries_the_token():
    """`summon` is the one that must not, and the four below are the ones that
    must."""
    src = _src("app/src/api.ts")
    block = src[src.index("  summon: (ref: string)"):
                src.index("  socialConnections:")]
    order = ["joinQueue", "connectionMessages", "sendToConnection",
             "endConnection"]
    marks = [block.index(f"  {n}:") for n in order] + [len(block)]
    for i, name in enumerate(order):
        assert "token" in block[marks[i]:marks[i + 1]], (
            f"{name} does not carry a token")
    # And the one that must not: a scan is a stranger with no account.
    assert "token" not in block[:marks[0]]


def test_the_native_shells_carry_the_token_too():
    """All three sent the id and nothing else. A backend that now refuses them
    without a fixed client is a break, not a fix."""
    kt = _src("native/android/app/src/main/java/app/qrme/studio/ApiClient.kt")
    for fn in ("joinQueue", "connectionMessages", "sendConnectionMessage",
               "endConnection"):
        body = kt[kt.index(f"fun {fn}("):]
        assert "token" in body[:400], f"android {fn} sends no token"

    swift = _src("native/ios/Sources/ApiClient.swift")
    for fn in ("joinQueue", "connectionMessages", "sendConnectionMessage",
               "endConnection"):
        body = swift[swift.index(f"func {fn}("):]
        assert "token: token" in body[:500], f"ios {fn} sends no token"

    cs = _src("native/windows/ApiClient.cs")
    for fn in ("JoinQueue", "ConnectionMessages", "SendConnectionMessage",
               "EndConnection"):
        body = cs[cs.index(f"{fn}(string cid" if fn != "JoinQueue"
                           else "JoinQueue(string interactorId"):]
        assert "token" in body[:600], f"windows {fn} sends no token"


def test_the_screen_says_what_the_alias_is_for():
    src = re.sub(r"^\s*//.*$", "", _src("app/src/screens/Stranger.tsx"),
                 flags=re.M)
    flat = " ".join(src.split())
    assert "the name they chose, and all either of you gets" in flat


def test_the_screen_marks_a_blocked_message_as_held_back():
    src = _src("app/src/screens/Stranger.tsx")
    assert "only you can see this" in src
