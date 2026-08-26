"""A person has their own picture, and a background is not a face.

Field report, over a two-seat room where both seats were named the same
thing: "I don't know why both profile photos don't show up, one says You
with a Y on it. It should be my image that I have on my profile photo,
but also it's not letting me double tap to open up the windows to add a
photo as my background or turn on my camera."

Three separate defects under one sentence, and they had one root: only
PROFILES had portraits.

    asked     can a person show a face
    mattered  whose face is it

## What was wrong

A human seat had a display name and two initials. The only way to put a
face on one was to borrow the portrait of the profile bound to the
session — gated on `avatars.likeness().real_person`, which is False for
any profile whose `kind` is "fictional", and `kind` DEFAULTS to fictional
(`models.py`; only onboarding sets "self"). So the gate refused, the seat
drew initials, and the borrowed picture appeared on the SYNTHETIC seat
beside it instead. Two seats, same name, and the person's own face on the
one that was not them.

The gate was right. A generated portrait passing unmarked as a human's
face is the thing it exists to prevent, and a fictional-by-default profile
is exactly what it guards. The borrow was wrong.

## What a background is

Not a face. `photo` REPLACES the person; a background sits UNDER whatever
the seat is showing and leaves them on top of it. Field request: "I still
wanna allow users to change the photo not just of their picture but of
the background". Before this there was no such state — so a person who
wanted a room behind them and pressed the only picture button available
replaced themselves with it.

Never applied over a live camera. Cutting somebody out of their own video
frame needs real segmentation, and a background pasted behind an uncut
frame is a picture nobody can see.

## The gesture

The controls were gated on `faceLive` — a camera or picture ALREADY
showing — so the one state where you need them was the one state where the
handler was `undefined`.
"""

from __future__ import annotations

from pathlib import Path

from tests.test_capabilities import (as_interactor, make_interactor,  # noqa: F401
                                     make_profile, pdi_pair)

ROOT = Path(__file__).resolve().parents[1]
INSIDE = (ROOT / "app/src/screens/Inside.tsx").read_text(encoding="utf-8")
IDENTITY = (ROOT / "app/src/screens/Identity.tsx").read_text(encoding="utf-8")
CSS = (ROOT / "app/src/styles.css").read_text(encoding="utf-8")

PNG = (b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\rIHDR"
       + b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00"
       + b"\x1f\x15\xc4\x89" + b"\x00" * 16)


def _room(client):
    user = make_interactor(client, "Theo", "1990-01-01")
    dana = make_profile(client)
    room = client.post("/rooms", json={
        "topic": "faces", "channel": "chat",
        "participants": [{"kind": "user", "id": user},
                         {"kind": "profile", "id": dana["id"]}]}).json()
    return user, room


# -- the picture is the person's ---------------------------------------------

def test_a_person_can_put_their_own_picture_up(client):
    user = make_interactor(client, "Theo", "1990-01-01")
    r = client.post(f"/interactors/{user}/picture?filename=me.png",
                    headers=as_interactor(user), content=PNG)
    assert r.status_code == 201, r.text
    assert r.json()["url"]
    assert r.json()["ai_marked"] is False, (
        "a photograph of somebody's own face was stamped as synthetic media")


def test_the_picture_is_read_back_by_its_owner_alone(client):
    user = make_interactor(client, "Theo", "1990-01-01")
    client.post(f"/interactors/{user}/picture?filename=me.png",
                headers=as_interactor(user), content=PNG)
    nosy = make_interactor(client, "Nosy")
    r = client.get(f"/interactors/{user}/picture", headers=as_interactor(nosy))
    assert r.status_code in (401, 403), (
        "somebody else's photograph is readable to anyone holding an id")


def test_taking_it_down_takes_it_down(client):
    user = make_interactor(client, "Theo", "1990-01-01")
    mine = as_interactor(user)
    client.post(f"/interactors/{user}/picture?filename=me.png",
                headers=mine, content=PNG)
    assert client.delete(f"/interactors/{user}/picture",
                         headers=mine).status_code == 200
    assert client.get(f"/interactors/{user}/picture",
                      headers=mine).json()["url"] is None


def test_it_follows_the_person_into_a_room(client):
    """The whole difference between this and a room face: a room face is
    what you are showing HERE, this is who you are in all of them."""
    user, room = _room(client)
    mine = as_interactor(user)
    client.post(f"/interactors/{user}/picture?filename=me.png",
                headers=mine, content=PNG)
    faces = client.get(f"/rooms/{room['id']}/faces", headers=mine).json()
    assert faces["pictures"].get(user), (
        "the room does not carry the person's own picture, so a seat can "
        "only draw initials")


def test_a_stranger_to_the_room_is_not_in_its_pictures(client):
    """Scoped to the people seated here. The room read is already the
    narrower door; this must not be wider than it."""
    user, room = _room(client)
    outsider = make_interactor(client, "Nosy")
    client.post(f"/interactors/{outsider}/picture?filename=me.png",
                headers=as_interactor(outsider), content=PNG)
    faces = client.get(f"/rooms/{room['id']}/faces",
                       headers=as_interactor(user)).json()
    assert outsider not in faces["pictures"]


def test_the_seat_draws_the_person_not_a_borrowed_profile_portrait():
    assert "ownPic(s.id)" in INSIDE, (
        "the human seat is not drawing the person's own picture")
    assert "myFace.likeness?.real_person ? (" not in INSIDE, (
        "the seat still borrows a profile's portrait, gated on a likeness "
        "record that is False for every fictional-by-default profile")


def test_an_uploaded_picture_fills_the_frame():
    """"The pictures they upload will fill the whole frame." A face in a
    small circle with a wide empty tile around it is the drawing the
    camera already stopped doing."""
    block = INSIDE[INSIDE.index("ownPic(s.id) ? ("):]
    block = block[:block.index("/>")]
    assert "rs-fullbleed" in block


# -- a background is behind you, not instead of you --------------------------

def test_a_background_does_not_replace_the_person(client):
    user, room = _room(client)
    mine = as_interactor(user)
    r = client.post(
        f"/rooms/{room['id']}/face/background?interactor_id={user}"
        "&filename=beach.png", headers=mine, content=PNG)
    assert r.status_code == 201, r.text
    assert r.json()["showing"] == "voice", (
        "putting scenery up changed what the person is showing — a "
        "background is behind you, not instead of you")
    assert r.json()["background_url"]


def test_a_background_survives_the_camera_going_on_and_off(client):
    """Same argument the portrait already had: a state change is not a
    deletion, and turning a camera off should not throw away the room you
    chose to sit in."""
    user, room = _room(client)
    mine = as_interactor(user)
    client.post(f"/rooms/{room['id']}/face/background?interactor_id={user}"
                "&filename=beach.png", headers=mine, content=PNG)
    client.put(f"/rooms/{room['id']}/face", headers=mine,
               json={"interactor_id": user, "showing": "camera"})
    r = client.put(f"/rooms/{room['id']}/face", headers=mine,
                   json={"interactor_id": user, "showing": "voice"})
    assert r.json()["background_url"], "the background was thrown away"


def test_a_background_is_a_picture_and_junk_is_refused(client):
    user, room = _room(client)
    r = client.post(
        f"/rooms/{room['id']}/face/background?interactor_id={user}"
        "&filename=innocent.png", headers=as_interactor(user),
        content=b"\x00\x01\x02\x03\xff\xfe")
    assert r.status_code == 422, r.text


def test_a_stranger_with_the_room_id_cannot_set_a_background(client):
    user, room = _room(client)
    outsider = make_interactor(client, "Nosy")
    r = client.post(
        f"/rooms/{room['id']}/face/background?interactor_id={outsider}"
        "&filename=beach.png", headers=as_interactor(outsider), content=PNG)
    assert r.status_code == 403


def test_no_background_behind_a_live_camera():
    """Segmentation this deployment does not do. A background pasted
    behind an uncut video frame is a picture nobody can see."""
    assert 'behind && face?.showing !== "camera"' in INSIDE


def test_the_background_is_drawn_under_everything_else():
    block = CSS[CSS.index(".rs-behind {"):]
    block = block[:block.index("}")]
    assert "z-index: 0" in block
    assert "object-fit: cover" in block, (
        "the background letterboxes instead of filling the tile")


# -- the gesture that opens the controls -------------------------------------

def test_the_controls_open_on_an_empty_seat():
    """The defect: gated on a camera or picture ALREADY showing, so the one
    state where you need the options was the one state where the handler
    was undefined and the tap did nothing."""
    block = INSIDE[INSIDE.index("onDoubleClick={isMe"):]
    block = block[:block.index(">")]
    assert "faceLive" not in block, (
        "the seat's controls still require a face before they will open")


def test_the_controls_are_your_own_seats_only():
    """Somebody else's seat has no controls of yours on it."""
    for handler in ("onDoubleClick={isMe", "onPointerDown={isMe ?"):
        assert handler in INSIDE, f"{handler} is not anchored to your own seat"


def test_each_picture_has_its_own_control_where_it_belongs():
    """Three destinations, three controls — and one of them moved house.

    The first version of this guard held that all three buttons live in the
    room's controls, and for two of them that is still right: what you show
    in THIS room, and what stands behind you here, are the room's own
    decisions. The person's own picture is not — it follows them into every
    room — and in the room it sat beside "put a picture up" doing what
    reads as the same thing. The owner asked for it gone by name: the seat
    DEFAULTS to the person's picture, and the picture is set once, on the
    Identity screen, where it always had a control of its own.

        asked     does each destination have its own control
        mattered  is each control where somebody would look for it

    So the room holds two, the Identity screen holds the third, and the
    concern the first version protected — one button quietly doing three
    jobs, which is how the background ended up replacing people — is held
    by the doors staying distinct, not by the buttons sharing a row. The
    room block must NOT grow the own-picture button back: two buttons for
    one visible outcome is a menu.

    Then "put a picture up" left too, same reasoning one round later and
    in the owner's own words: "delete put a picture up because background
    already does that." The seat's face is the person's own picture, set
    on Identity; the room's remaining decoration is what stands BEHIND
    them. So the room now holds ONE picture control — the background —
    and the guard holds the door count down the way it once held it up:
    neither retired button comes back.
    """
    block = INSIDE[INSIDE.index('<div className="rs-controls">'):]
    block = block[:block.index("</select>")]
    assert "ins.face.background" in block, (
        "the background has no control in the room")
    assert "api.uploadRoomBackground" in block, (
        "api.uploadRoomBackground is not wired to anything")
    assert "ins.face.photo" not in block, (
        '"put a picture up" is back in the room — the owner removed it '
        "because the background button already carries the room's "
        "decorating, and the seat's face is the person's own picture")
    # Quoted, because `ins.face.mine` is a substring of `ins.face.mineoff`
    # — the take-it-down button, which stays. The third guard today whose
    # first draft matched more than it meant.
    assert 'tr("ins.face.mine"' not in block, (
        "the own-picture button is back in the room, beside a button that "
        "reads as the same thing — the seat defaults to the person's "
        "picture, and its control lives on the Identity screen")
    assert "idn.mypic" in IDENTITY and "api.setOwnPicture" in IDENTITY, (
        "the person's own picture has no control anywhere: it left the "
        "room and the Identity screen is not carrying it either")
