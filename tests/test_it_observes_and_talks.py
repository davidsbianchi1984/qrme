"""A lobby that observes and talks, and two ways to hand a conversation on.

The gaming lobby's whole design is one sentence it publishes about itself:
**everything in this lobby observes and talks; nothing in it plays.** The
`never` list spells that out a dozen ways, and the interesting half is not the
obvious entries — it is the four that close routes somebody would otherwise
argue for:

* its **own hardware** — "a second machine does not turn a bot into a player;
  it just moves where the bot is running";
* a **second controller** — "the same bot with a shorter cable";
* a **Bluetooth pad** paired to it;
* a **capture card** feeding it the picture.

Each of those is a decision with a reason, and "no cheating" is not the same
statement. So this file asserts the list keeps its arguments rather than
collapsing into a slogan, and that the console renders them rather than
retyping a summary.

The second half is the pair of ways to pass a conversation on, which are
different on purpose and easy to conflate:

============  ==================================  ======================
              referral                            handoff
============  ==================================  ======================
authorised    a device signature over the bytes   explicit consent
lifetime      one open, ever                      until revoked
on revoke     —                                   the package is purged
============  ==================================  ======================

Neither substitutes for the other, and a product offering only the heavier one
would push people to skip it.
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


def _owner(client, account="acct_lobby"):
    p = client.post("/profiles", json={
        "owner_id": account, "kind": "fictional", "display_name": "Player",
        "purpose": "companion_coach", "persona": "p",
        "verification": {"birthdate": "1990-01-01"}}).json()
    head = {"authorization": f"Bearer {p['owner_token']}"}
    client.post(f"/memberships/{account}", json={"plan": "pro"}, headers=head)
    return p, head


def _session(client, account="acct_lobby"):
    p, head = _owner(client, account)
    s = client.post(f"/profiles/{p['id']}/gaming/sessions",
                    json={"game": "Elden Ring", "platform": "pc"},
                    headers=head).json()
    return p, head, s["id"]


# --- the line -------------------------------------------------------------

def test_the_lobby_says_what_nothing_in_it_will_do(client):
    vocab = client.get("/gaming/lobby/vocabulary").json()
    things = {n["thing"] for n in vocab["never"]}
    assert {"input", "aim", "macro", "automation", "player_slot"} <= things


@pytest.mark.parametrize("thing", ["own_hardware", "second_controller",
                                   "bluetooth_input", "player_slot"])
def test_the_hardware_arguments_are_closed_by_name(thing, client):
    """The entries that make this more than a slogan.

    Each closes a route somebody would otherwise argue for — its own
    console, a second pad, a paired controller — and each carries the
    sentence saying why it changes nothing. Dropping one would leave the
    list looking complete and the argument unmade.
    """
    never = {n["thing"]: n["means"]
             for n in client.get("/gaming/lobby/vocabulary").json()["never"]}
    assert thing in never, (
        f"{thing} is no longer refused by name, so the obvious workaround "
        "is unanswered")
    assert len(never[thing]) > 60, f"{thing} is refused without a reason"


def test_the_fair_play_sentence_is_one_paragraph_not_a_flag(client):
    """It is prose because it is an argument. A boolean would be a setting,
    and `gamelobby.py` says plainly that this is a property of the code."""
    vocab = client.get("/gaming/lobby/vocabulary").json()
    assert "observes and talks" in vocab["fair_play"]
    assert "property of the code rather than a setting" in vocab["fair_play"]


def test_the_roster_says_which_members_are_synthetic(client):
    """Everyone in a match is owed this, so it is per member rather than a
    count in a corner."""
    p, head, sid = _session(client, "acct_roster")
    roster = client.get(f"/gaming/sessions/{sid}/lobby", headers=head).json()
    assert roster["members"], "the session's own profile is not seated"
    for m in roster["members"]:
        assert "synthetic" in m and m["is"], (
            "a member with no statement of what it is")
    assert roster["profiles"] >= 1
    assert roster["synthetic_seats_left"] + roster["profiles"] \
        + roster["agents"] == vocab_max(client)


def vocab_max(client) -> int:
    return client.get("/gaming/lobby/vocabulary").json()["max_synthetic"]


def test_the_context_tells_a_member_the_others_may_be_synthetic(client):
    """The uncomfortable one, and the reason it is shown to the owner.

    A model that believes every callsign is a person addresses them as
    people, and a lobby that reads as five friends when it is one player and
    four generated voices is the impression this product exists to prevent.
    """
    p, head, sid = _session(client, "acct_ctx")
    ctx = client.get(f"/gaming/sessions/{sid}/lobby/context",
                     headers=head).json()
    assert "synthetic" in ctx["instruction"]
    assert "cannot press a button" in ctx["instruction"]
    assert ctx["synthetic_here"] >= 1


# --- who may seat whom ------------------------------------------------------

def test_a_person_seats_only_themselves(client):
    """An id in a request body is a claim. A seat taken on somebody's behalf
    is a claim that they are in a match they may not have joined."""
    p, head, sid = _session(client, "acct_seatme")
    r = client.post(f"/gaming/sessions/{sid}/lobby", headers=head, json={
        "member_kind": "player", "member_id": "somebody-else",
        "role": "teammate"})
    assert r.status_code == 403
    assert "that is not you" in r.json()["detail"]


def test_a_sibling_profile_may_be_seated_and_a_stranger_may_not(client):
    """One person's several profiles is exactly the case this is for.
    Somebody else's is a two-party question, and the refusal points at the
    routes that already ask both sides rather than half-answering it."""
    p, head, sid = _session(client, "acct_sib")
    mine = client.post("/profiles", json={
        "owner_id": "acct_sib", "kind": "fictional", "display_name": "Coach",
        "purpose": "companion_coach", "persona": "p",
        "verification": {"birthdate": "1990-01-01"}}).json()
    ok = client.post(f"/gaming/sessions/{sid}/lobby", headers=head, json={
        "member_kind": "profile", "member_id": mine["id"], "role": "coach",
        "callsign": "Coach"})
    assert ok.status_code == 201, ok.text

    theirs = client.post("/profiles", json={
        "owner_id": "somebody_else", "kind": "fictional",
        "display_name": "Stranger", "purpose": "companion_coach",
        "persona": "p", "verification": {"birthdate": "1990-01-01"}}).json()
    no = client.post(f"/gaming/sessions/{sid}/lobby", headers=head, json={
        "member_kind": "profile", "member_id": theirs["id"],
        "role": "spotter"})
    assert no.status_code == 403
    assert "two-party" in no.json()["detail"]


def test_the_write_calls_it_member_kind(client):
    """The read says `member_kind` and so does the write, but the vocabulary
    says `kind` — three names near enough to swap, and the wrong one is a
    422 for a missing field."""
    p, head, sid = _session(client, "acct_kindname")
    mine = client.post("/profiles", json={
        "owner_id": "acct_kindname", "kind": "fictional",
        "display_name": "Coach", "purpose": "companion_coach", "persona": "p",
        "verification": {"birthdate": "1990-01-01"}}).json()
    wrong = client.post(f"/gaming/sessions/{sid}/lobby", headers=head, json={
        "kind": "profile", "member_id": mine["id"], "role": "coach"})
    assert wrong.status_code == 422
    assert "member_kind" in wrong.text


def test_leaving_needs_a_body_saying_who(client):
    p, head, sid = _session(client, "acct_leave")
    mine = client.post("/profiles", json={
        "owner_id": "acct_leave", "kind": "fictional", "display_name": "Coach",
        "purpose": "companion_coach", "persona": "p",
        "verification": {"birthdate": "1990-01-01"}}).json()
    client.post(f"/gaming/sessions/{sid}/lobby", headers=head, json={
        "member_kind": "profile", "member_id": mine["id"], "role": "coach"})
    assert client.request("DELETE", f"/gaming/sessions/{sid}/lobby",
                          headers=head).status_code == 422
    gone = client.request("DELETE", f"/gaming/sessions/{sid}/lobby",
                          headers=head, json={"member_id": mine["id"]})
    assert gone.status_code == 200 and gone.json()["seated"] is False


# --- the handoff ------------------------------------------------------------

def _handoff(client, account="acct_hand"):
    p, head = _owner(client, account)
    who = client.post("/interactors", json={"display_name": "Pat"}).json()
    ihead = {"authorization": f"Bearer {who['token']}"}
    client.post(f"/profiles/{p['id']}/chat", headers=ihead,
                json={"interactor_id": who["id"], "message": "leaky tap"})
    provider = client.post("/providers", json={
        "name": "Bath Plumb", "area": "plumbing", "location": "Bath",
        "contact": "p@example", "business": True}).json()
    return p, who, ihead, provider


def test_a_handoff_without_consent_is_refused(client):
    """Consent is a field on the request, so an unchecked box is refused by
    the server rather than only by a disabled button."""
    p, who, ihead, provider = _handoff(client, "acct_noconsent")
    r = client.post("/handoffs", headers=ihead, json={
        "interactor_id": who["id"], "provider_id": provider["id"],
        "profile_id": p["id"], "consent": False})
    assert r.status_code == 403
    assert "explicit consent" in r.json()["detail"]


def test_revoking_purges_the_package_rather_than_hiding_it(client):
    """The difference from a referral. A referral is one-time and signed;
    this is revocable, and revoking takes the words back rather than just
    the key to them."""
    p, who, ihead, provider = _handoff(client, "acct_revoke")
    made = client.post("/handoffs", headers=ihead, json={
        "interactor_id": who["id"], "provider_id": provider["id"],
        "profile_id": p["id"], "consent": True}).json()

    seen = client.get(f"/handoffs/{made['id']}?token={made['token']}")
    assert seen.status_code == 200
    assert seen.json()["package"]["recent_exchange"]

    assert client.delete(f"/handoffs/{made['id']}",
                         headers=ihead).json()["revoked"] is True
    after = client.get(f"/handoffs/{made['id']}?token={made['token']}")
    assert after.status_code == 403


def test_the_handoff_says_whether_it_was_sealed(client):
    """`sealed` is the custody fact. False means the package is sitting in
    this deployment's database until somebody revokes it, and the screen
    says so rather than implying a vault that is not there."""
    p, who, ihead, provider = _handoff(client, "acct_sealed")
    made = client.post("/handoffs", headers=ihead, json={
        "interactor_id": who["id"], "provider_id": provider["id"],
        "profile_id": p["id"], "consent": True}).json()
    assert "sealed" in made


def test_a_wrong_token_does_not_open_a_handoff(client):
    p, who, ihead, provider = _handoff(client, "acct_wrongtok")
    made = client.post("/handoffs", headers=ihead, json={
        "interactor_id": who["id"], "provider_id": provider["id"],
        "profile_id": p["id"], "consent": True}).json()
    assert client.get(f"/handoffs/{made['id']}?token=nope").status_code == 403


# --- the console half -------------------------------------------------------

def _src(rel: str) -> str:
    return (REPO / rel).read_text(encoding="utf-8")


def test_the_lobby_screen_exists():
    assert (REPO / "app/src/screens/Lobby.tsx").exists()


@pytest.mark.parametrize("binding", [
    "api.lobbyVocabulary(", "api.lobby(", "api.takeSeat(", "api.leaveLobby(",
    "api.lobbyContext(", "api.handoff(", "api.openHandoff(",
    "api.revokeHandoff(",
])
def test_the_lobby_screen_calls_it(binding):
    assert binding in _src("app/src/screens/Lobby.tsx")


def test_the_never_list_is_rendered_rather_than_summarised():
    """Twelve arguments, and a console that shortened them to "no cheating"
    would be dropping the reasoning that makes them credible."""
    import re

    src = _src("app/src/screens/Lobby.tsx")
    assert "vocab.never.map" in src, (
        "the refusals are no longer drawn one by one")
    markup = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    markup = re.sub(r"^\s*//.*$", "", markup, flags=re.M)
    assert "shorter cable" not in markup, (
        "an argument has been copied into the console; render the server's "
        "sentence so there is one copy of it")


def test_the_instruction_is_shown_to_the_owner():
    assert "context.instruction" in _src("app/src/screens/Lobby.tsx"), (
        "what a synthetic member is told is no longer checkable by the "
        "person responsible for it")


def test_the_seat_binding_sends_member_kind():
    api = _src("app/src/api.ts")
    i = api.index("takeSeat:")
    assert "member_kind: string" in api[i:i + 400]
