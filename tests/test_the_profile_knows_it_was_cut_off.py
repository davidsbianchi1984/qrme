"""A profile answering an interruption knows where it was cut off.

    asked     did the person interrupt
    mattered  how much had they heard when they did

Cutting a profile off mid-paragraph leaves the person holding a PREFIX of
what it said. The reply they get next is built from a transcript that, until
now, showed the whole turn as though they had sat through it — so the
profile either carried on from a point they never reached, or answered as if
its unheard sentences had landed. Both are the model talking past somebody
rather than to them.

The fact rides on the interrupted turn itself rather than beside it: it is a
fact about that turn, every profile in the room reads the same transcript,
and it survives a reload. The client knows it because the voice is played
sentence by sentence, so an interruption lands on a known boundary and
`Speaking.heard()` reports exactly what reached the room.

Optional on the wire, and ignorable. A client that never sends it — the
three native shells, anything older — is describing a room where nothing was
interrupted, which is the ordinary case.
"""

from __future__ import annotations

import pytest

from tests.test_capabilities import (as_interactor, make_interactor,  # noqa: F401
                                     make_profile, pdi_pair)


@pytest.fixture()
def room(client):
    user = make_interactor(client, "Theo", "1990-01-01")
    dana = make_profile(client)
    r = client.post("/rooms", json={"channel": "chat", "participants": [
        {"kind": "user", "id": user},
        {"kind": "profile", "id": dana["id"]}]})
    assert r.status_code == 201, r.text
    return user, dana["id"], r.json()["id"], as_interactor(user)


def _say(client, room, text, cut=None):
    user, _, rid, mine = room
    body = {"sender_id": user, "message": text}
    if cut:
        body["cut_off_id"], body["cut_off_heard"] = cut
    r = client.post(f"/rooms/{rid}/messages", json=body, headers=mine)
    assert r.status_code == 201, r.text
    return r.json()


def test_an_uninterrupted_room_records_nothing(client, room):
    """The ordinary case stays ordinary: no flag, no sentence, nothing for
    a profile to account for."""
    from qrme import db

    _say(client, room, "hello")
    heard = [r["heard"] for r in db.connect().execute(
        "SELECT heard FROM room_messages")]
    assert heard and all(h is None for h in heard)


def test_the_interrupted_turn_carries_what_was_heard(client, room):
    from qrme import db

    said = _say(client, room, "tell me about sleep")
    reply = said["replies"][0]
    _say(client, room, "stop, different question",
         cut=(reply["id"], "The first thing I would ask is"))
    got = db.connect().execute(
        "SELECT heard FROM room_messages WHERE id=?", (reply["id"],)).fetchone()
    assert got["heard"] == "The first thing I would ask is"


def test_only_a_profiles_turn_can_be_marked_cut_off(client, room):
    """A person's own message is not something they interrupted, and
    accepting an id without checking would let a client rewrite a row it
    picked out of the transcript."""
    from qrme import db

    mine = _say(client, room, "hello")["message"]
    _say(client, room, "again", cut=(mine["id"], "hel"))
    got = db.connect().execute(
        "SELECT heard FROM room_messages WHERE id=?", (mine["id"],)).fetchone()
    assert got["heard"] is None


def test_a_turn_in_another_room_cannot_be_marked(client, room):
    """The room id is part of the write, so a client holding one room's
    token cannot reach into another's transcript."""
    from qrme import db

    said = _say(client, room, "tell me about sleep")
    reply = said["replies"][0]

    other_user = make_interactor(client, "Sam", "1990-01-01")
    other_profile = make_profile(client)
    other = client.post("/rooms", json={"channel": "chat", "participants": [
        {"kind": "user", "id": other_user},
        {"kind": "profile", "id": other_profile["id"]}]}).json()["id"]
    client.post(f"/rooms/{other}/messages",
                json={"sender_id": other_user, "message": "hi",
                      "cut_off_id": reply["id"], "cut_off_heard": "nope"},
                headers=as_interactor(other_user))
    got = db.connect().execute(
        "SELECT heard FROM room_messages WHERE id=?", (reply["id"],)).fetchone()
    assert got["heard"] is None


def test_the_profile_reads_that_it_was_cut_off(client, room, monkeypatch):
    """The whole point: the next reply is built from a history that says so.

    Read at the model rather than trusting the column — a fact recorded and
    never handed to the model is a fact that changes nothing. So take a real
    turn and inspect the transcript that actually went out.
    """
    from qrme.routers import community

    said = _say(client, room, "tell me about sleep")
    reply = said["replies"][0]

    seen: list = []

    class Provider:
        def generate(self, system, turns):
            seen.append(turns)
            return "Understood — let me start again."

    monkeypatch.setattr(community.llm, "get_provider",
                        lambda *a, **k: Provider())
    _say(client, room, "stop \u2014 different question",
         cut=(reply["id"], "The first thing I would ask"))
    assert seen, "no profile turn was taken"
    handed = " ".join(t["content"] for t in seen[-1])
    assert "interrupted" in handed, (
        "the profile's next reply is built from a history that shows the "
        "whole turn, as though the person had heard all of it")
    assert "The first thing I would ask" in handed, (
        "the history says it was interrupted and not where, so the profile "
        "cannot tell which part reached them")


def test_a_turn_heard_to_the_end_is_not_reported_as_a_loss(client, room,
                                                           monkeypatch):
    """A person who lets the last sentence land and then talks over the
    silence interrupted nothing they missed. Saying "all they heard was"
    there would have the profile apologise for a gap that is not there."""
    from qrme.routers import community

    said = _say(client, room, "tell me about sleep")
    reply = said["replies"][0]

    seen: list = []

    class Provider:
        def generate(self, system, turns):
            seen.append(turns)
            return "Go on."

    monkeypatch.setattr(community.llm, "get_provider",
                        lambda *a, **k: Provider())
    _say(client, room, "one more thing", cut=(reply["id"], reply["content"]))
    assert seen, "no profile turn was taken"
    handed = " ".join(t["content"] for t in seen[-1])
    assert "all they heard was" not in handed
    assert "just as you finished" in handed
