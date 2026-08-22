"""The room passes things around, under the transcript's own rules.

Field request, over a two-seat room: "you should be able to share
pictures, photos, videos, and files between the people in the chat room."

    asked     can a room hand a file around
    mattered  under whose rules — the transcript's, or looser ones

The share door reuses everything that already knew how to be careful:
`media.save` decides the kind from the file's own magic numbers and holds
the byte caps, the sharer must be a user participant held by their own
token (a room id on a printed sticker is still not a way to speak), a
caption rides through moderation like any said thing, and the upload
lands as a room message readable by exactly the people the transcript
already answers to.
"""

from __future__ import annotations

from tests.test_capabilities import (as_interactor, make_interactor,  # noqa: F401
                                     make_profile, pdi_pair)

# The smallest honest PNG: signature + a minimal IHDR chunk. media._sniff
# reads the magic, not the name.
PNG = (b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\rIHDR"
       + b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00"
       + b"\x1f\x15\xc4\x89" + b"\x00" * 16)


def _room(client):
    user = make_interactor(client, "Theo", "1990-01-01")
    dana = make_profile(client)
    room = client.post("/rooms", json={
        "topic": "show and tell", "channel": "chat",
        "participants": [{"kind": "user", "id": user},
                         {"kind": "profile", "id": dana["id"]}]}).json()
    return user, room


def test_a_picture_lands_as_a_turn(client):
    user, room = _room(client)
    mine = as_interactor(user)
    r = client.post(
        f"/rooms/{room['id']}/share?interactor_id={user}"
        "&filename=sunset.png&caption=look at this",
        headers=mine, content=PNG)
    assert r.status_code == 201, r.text
    msg = r.json()["shared"]
    assert msg["status"] == "approved"
    assert msg["content"] == "look at this"
    assert msg["media"]["kind"] == "image"
    assert msg["media"]["url"].startswith("/")

    transcript = client.get(f"/rooms/{room['id']}/messages",
                            headers=mine).json()
    assert transcript[-1]["media"]["kind"] == "image"


def test_sharing_does_not_make_the_profiles_speak(client):
    """"Let them talk" stays the button it is: a person can put three
    pictures up before inviting a word about them."""
    user, room = _room(client)
    r = client.post(
        f"/rooms/{room['id']}/share?interactor_id={user}&filename=a.png",
        headers=as_interactor(user), content=PNG)
    assert r.status_code == 201
    assert "replies" not in r.json()
    transcript = client.get(f"/rooms/{room['id']}/messages",
                            headers=as_interactor(user)).json()
    assert [m["sender_kind"] for m in transcript] == ["user"]


def test_a_stranger_with_the_room_id_cannot_share(client):
    user, room = _room(client)
    outsider = make_interactor(client, "Nosy")
    r = client.post(
        f"/rooms/{room['id']}/share?interactor_id={outsider}"
        "&filename=a.png",
        headers=as_interactor(outsider), content=PNG)
    assert r.status_code == 403


def test_the_bytes_decide_and_the_junk_is_refused(client):
    user, room = _room(client)
    r = client.post(
        f"/rooms/{room['id']}/share?interactor_id={user}"
        "&filename=innocent.png",
        headers=as_interactor(user), content=b"\x00\x01\x02\x03\xff\xfe")
    assert r.status_code == 422, r.text


def test_a_profile_is_told_something_was_shown():
    """A profile that cannot see pixels should still know something was
    shown — the labelled history says so, instead of handing the model an
    empty turn to lose the thread over."""
    from pathlib import Path

    src = (Path(__file__).resolve().parents[1]
           / "qrme/routers/community.py").read_text(encoding="utf-8")
    turns = src[src.index("def _profile_turns"):]
    turns = turns[:turns.index("\n@router")]
    assert "[shared a" in turns, (
        "a shared attachment reaches the model as an empty message — "
        "the turn should state that something was shown")


# -- the room's name, changed from inside it ---------------------------------

def test_a_participant_can_name_the_room(client):
    user, room = _room(client)
    r = client.patch(f"/rooms/{room['id']}", headers=as_interactor(user),
                     json={"interactor_id": user, "topic": "Tuesday call"})
    assert r.status_code == 200, r.text
    assert r.json()["topic"] == "Tuesday call"
    back = client.post(f"/rooms/{room['id']}/join",
                       headers=as_interactor(user)).json()
    assert back["topic"] == "Tuesday call", "the name did not survive"


def test_a_stranger_with_the_room_id_cannot_name_it(client):
    """The same closed door speaking uses: a room id rides on printed
    stickers, and naming somebody else's room from outside is not a thing
    this product offers."""
    user, room = _room(client)
    outsider = make_interactor(client, "Nosy")
    r = client.patch(f"/rooms/{room['id']}", headers=as_interactor(outsider),
                     json={"interactor_id": outsider, "topic": "mine now"})
    assert r.status_code == 403


def test_a_room_is_not_named_nothing(client):
    user, room = _room(client)
    r = client.patch(f"/rooms/{room['id']}", headers=as_interactor(user),
                     json={"interactor_id": user, "topic": "   "})
    assert r.status_code == 422
