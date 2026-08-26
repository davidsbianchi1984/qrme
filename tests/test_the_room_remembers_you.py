"""A friend you walk in with is not a stranger.

Field report: *"I had already given a bunch of files to the synthetic
profile in a previous chat, so I open up a new room and the synthetic
profile could not remember the previous chat."* Same profile, same person —
met as a stranger.

    asked     does my profile remember me in a room
    mattered  the chat door carries the pair's history on every turn and
              the room door never made either call

Two calls, both existing since their own rounds: `briefcase.block` (what
this person handed this profile) and `recollection.chat_block` (moments
the profile remembers this person telling it, vault-backed). The room now
makes both — the history enters the room behind the scenes when the pair
walks in together.

## The line, and why it is a line

Only when the room's one human IS the other half of the pair.
recollection.py's rule — what Alice told it must never surface in its
reply to Bob — reaches its limit the moment Bob is in the room hearing
the reply. A room with a second human carries no pair memory at all:
privacy over continuity.
"""

from __future__ import annotations

from qrme import briefcase, recollection

from tests.test_capabilities import (as_interactor, make_interactor,  # noqa: F401
                                     make_profile)


class Speaks:
    def __init__(self):
        self.systems: list[str] = []

    def generate(self, system, turns):
        self.systems.append(system)
        return "Good to see you again."


def _remembering_room(client, monkeypatch, extra_user=None):
    from qrme.routers import community
    made = Speaks()
    monkeypatch.setattr(community.llm, "get_provider",
                        lambda *a, **k: made)
    user = make_interactor(client, "Theo", "1990-01-01")
    prof = make_profile(client)
    briefcase.add(prof["id"], user, kind="document",
                  title="Quarterly filing", text="Revenue held flat.",
                  read=True)
    joiners = [{"kind": "user", "id": user},
               {"kind": "profile", "id": prof["id"]}]
    if extra_user:
        joiners.append({"kind": "user", "id": extra_user})
    room = client.post("/rooms", json={
        "topic": "catching up", "channel": "chat",
        "participants": joiners}).json()
    return made, user, prof, room


def test_the_pair_briefcase_enters_a_room_of_two(client, monkeypatch):
    made, user, prof, room = _remembering_room(client, monkeypatch)
    r = client.post(f"/rooms/{room['id']}/messages",
                    headers=as_interactor(user),
                    json={"message": "remember that filing?",
                          "sender_id": user})
    assert r.status_code == 201, r.text
    assert made.systems, "no turn was taken"
    assert "Quarterly filing" in made.systems[-1], (
        "the person's own filings are forgotten the moment they open a room")


def test_a_second_human_keeps_the_pair_memory_out(client, monkeypatch):
    """Privacy over continuity: what Alice handed it must not be read out
    in front of Bob."""
    bob = None

    def build(client_, monkeypatch_):
        nonlocal bob
        bob = make_interactor(client_, "Bob", "1991-01-01")
        return _remembering_room(client_, monkeypatch_, extra_user=bob)

    made, user, prof, room = build(client, monkeypatch)
    client.post(f"/rooms/{room['id']}/messages", headers=as_interactor(user),
                json={"message": "remember that filing?", "sender_id": user})
    assert made.systems, "no turn was taken"
    assert "Quarterly filing" not in made.systems[-1], (
        "a pair briefcase was read into a room with a second human in it")


def test_recalled_moments_walk_in_too(client, monkeypatch):
    monkeypatch.setattr(
        recollection, "chat_block",
        lambda pdi, profile_id, interactor_id, message:
            "Moments you remember: they prefer Tuesdays.")
    made, user, prof, room = _remembering_room(client, monkeypatch)
    client.post(f"/rooms/{room['id']}/messages", headers=as_interactor(user),
                json={"message": "when should we meet?", "sender_id": user})
    assert "they prefer Tuesdays" in made.systems[-1], (
        "the vault-backed recall never reached the room prompt")


def test_a_vault_gone_quiet_does_not_cost_the_turn(client, monkeypatch):
    """recall() already swallows a dead vault and answers with nothing —
    proven at the door, so a room turn survives what the vault does not."""
    made, user, prof, room = _remembering_room(client, monkeypatch)
    r = client.post(f"/rooms/{room['id']}/messages",
                    headers=as_interactor(user),
                    json={"message": "hello again", "sender_id": user})
    assert r.status_code == 201, r.text
    assert r.json()["replies"], "the turn died with the vault"
