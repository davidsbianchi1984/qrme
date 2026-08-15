"""Everybody in the room got a box, and a box could hold one thing.

## The finding

The room scene draws every participant in their own square and lights the
square of whoever spoke last. A square held two initials and a name. There was
no way to put a camera in it, no way to put a photograph in it, and the mask
machinery that has existed since `overlays.py` shipped was reachable only from
a separate screen where you type a surface name and a room id by hand.

    asked     everyone in the room in their own box
    mattered  and the box is where you decide what people see of you

## All three are a box

`voice`, `photo` and `camera` are three answers to one question and they are
the same size on screen. A person who has their camera off keeps their box, in
place, at full size — a scene that drops the quiet people answers *who is
talking* and loses *who is here*, and the second question is what a room is
for. The tests below check the quiet case explicitly, because it is the one an
optimisation would remove.

## The fact, not the pixels

`camera` records that a camera is on. Capture and rendering are the device's,
the same division `overlays` draws. What the shared row buys is that every
other client in the room draws the same scene rather than each person drawing
their own state and guessing at everybody else's — so the read is checked here
from a *second* person's token, which is the only way that claim means
anything.

## Two records, not one

A mask is not a fourth value of `showing`. You can wear a wolf on a live
camera or on nothing at all, so `overlays` keeps owning what is worn and this
keeps owning what is shown. `GET /rooms/{id}/faces` returns both, because a
client that had to make a second call to know whether a face is a face would
draw one frame without the disclosure.
"""

from __future__ import annotations


def _person(client, name="P", birthdate="1990-01-01"):
    row = client.post("/interactors", json={
        "display_name": name, "birthdate": birthdate}).json()
    return row["id"], {"authorization": f"Bearer {row['token']}"}


def _profile(client, account, name="Iris"):
    p = client.post("/profiles", json={
        "owner_id": account, "kind": "fictional", "display_name": name,
        "purpose": "enterprise_agent", "persona": "a calm host",
        "verification": {"birthdate": "1988-03-03"}}).json()
    return p["id"], {"authorization": f"Bearer {p['owner_token']}"}


def _room(client, people, pid, channel="video"):
    """A room holding every person in `people` and one profile."""
    parts = [{"kind": "user", "id": uid} for uid, _h in people]
    parts.append({"kind": "profile", "id": pid})
    r = client.post("/rooms", headers=people[0][1], json={
        "topic": "the roof", "channel": channel, "participants": parts})
    assert r.status_code == 201, r.text
    return r.json()["id"]


# A one-pixel PNG. Real bytes, because the upload path decides the kind from
# the magic numbers and a string named "photo.png" would prove nothing.
PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
    "890000000a49444154789c6300010000050001" "0d0a2db4" "00000000"
    "49454e44ae426082")


# --- the default is a box ---------------------------------------------------

def test_somebody_who_has_set_nothing_is_showing_their_name(client):
    """No row is not no box. The seats come from the room; this only says
    what is in them."""
    uid, ada = _person(client, "Ada")
    host, _o = _profile(client, "acct_f1")
    rid = _room(client, [(uid, ada)], host)

    r = client.get(f"/rooms/{rid}/faces", headers=ada)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["default"] == "voice"
    assert body["faces"] == {}, "a fresh room should carry no decisions"
    assert body["on_camera"] == 0
    assert "nobody here has turned a camera on" in body["note"]


def test_the_vocabulary_names_all_three(client):
    """Published rather than left for a client to guess, so a client cannot
    offer two of the three and call it the feature."""
    uid, ada = _person(client, "Ada")
    host, _o = _profile(client, "acct_f2")
    rid = _room(client, [(uid, ada)], host)

    said = {v["showing"] for v in
            client.get(f"/rooms/{rid}/faces", headers=ada).json()["vocabulary"]}
    assert said == {"voice", "photo", "camera"}, said


# --- turning a camera on ----------------------------------------------------

def test_a_person_can_turn_their_camera_on(client):
    uid, ada = _person(client, "Ada")
    host, _o = _profile(client, "acct_f3")
    rid = _room(client, [(uid, ada)], host)

    r = client.put(f"/rooms/{rid}/face", headers=ada,
                   json={"interactor_id": uid, "showing": "camera"})
    assert r.status_code == 200, r.text
    assert r.json()["showing"] == "camera"
    assert r.json()["ai_marked"] is False, (
        "a person's own camera is not synthetic media and must not be marked")


def test_everybody_in_the_room_sees_who_is_on_camera(client):
    """The claim the shared row exists to make, checked from the other
    person's token. A scene each client draws from its own state alone is not
    a scene."""
    a_id, ada = _person(client, "Ada")
    b_id, bo = _person(client, "Bo", "1991-02-02")
    host, _o = _profile(client, "acct_f4")
    rid = _room(client, [(a_id, ada), (b_id, bo)], host)

    client.put(f"/rooms/{rid}/face", headers=ada,
               json={"interactor_id": a_id, "showing": "camera"})

    seen = client.get(f"/rooms/{rid}/faces", headers=bo).json()
    assert seen["faces"][a_id]["showing"] == "camera", seen
    assert seen["on_camera"] == 1
    # And Bo, who has decided nothing, is not in the table and is still here.
    assert b_id not in seen["faces"]
    assert "a name in a box is a person in the room" in seen["note"]


def test_going_back_to_voice_keeps_you_in_the_scene(client):
    """The rule this whole surface is built around. Turning a camera off is
    not leaving."""
    uid, ada = _person(client, "Ada")
    host, _o = _profile(client, "acct_f5")
    rid = _room(client, [(uid, ada)], host)

    client.put(f"/rooms/{rid}/face", headers=ada,
               json={"interactor_id": uid, "showing": "camera"})
    back = client.put(f"/rooms/{rid}/face", headers=ada,
                      json={"interactor_id": uid, "showing": "voice"})
    assert back.status_code == 200, back.text
    assert back.json()["showing"] == "voice"

    faces = client.get(f"/rooms/{rid}/faces", headers=ada).json()
    assert faces["faces"][uid]["showing"] == "voice", (
        "the row is still here — a quiet person keeps their box")
    assert faces["on_camera"] == 0


# --- putting a picture up ---------------------------------------------------

def test_a_picture_goes_up_in_one_press(client):
    """Uploading is showing. Two presses where the first has no visible
    effect is how a control ends up looking broken."""
    uid, ada = _person(client, "Ada")
    host, _o = _profile(client, "acct_f6")
    rid = _room(client, [(uid, ada)], host)

    r = client.post(f"/rooms/{rid}/face/photo?interactor_id={uid}"
                    "&filename=me.png", headers=ada, content=PNG)
    assert r.status_code == 201, r.text
    assert r.json()["showing"] == "photo"
    assert r.json()["media_url"].startswith("/media/"), r.json()


def test_a_persons_own_photograph_carries_no_ai_mark(client):
    """The line `media.limits` already draws, at a second door that stores
    one. Stamping the synthetic-media mark into an authentic picture is a
    false statement in the direction the mark exists to prevent."""
    uid, ada = _person(client, "Ada")
    host, _o = _profile(client, "acct_f7")
    rid = _room(client, [(uid, ada)], host)

    up = client.post(f"/rooms/{rid}/face/photo?interactor_id={uid}",
                     headers=ada, content=PNG)
    assert up.json()["ai_marked"] is False, up.json()


def test_a_box_holds_a_picture_and_not_a_document(client):
    """The whitelist `media` applies, narrowed. A room box is not a place to
    serve a PDF."""
    uid, ada = _person(client, "Ada")
    host, _o = _profile(client, "acct_f8")
    rid = _room(client, [(uid, ada)], host)

    r = client.post(f"/rooms/{rid}/face/photo?interactor_id={uid}"
                    "&filename=notes.pdf", headers=ada,
                    content=b"%PDF-1.4 not a face")
    assert r.status_code == 422, r.text
    assert "picture" in r.json()["detail"]


def test_asking_for_a_photo_with_no_picture_says_which_half_is_missing(client):
    uid, ada = _person(client, "Ada")
    host, _o = _profile(client, "acct_f9")
    rid = _room(client, [(uid, ada)], host)

    r = client.put(f"/rooms/{rid}/face", headers=ada,
                   json={"interactor_id": uid, "showing": "photo"})
    assert r.status_code == 422, r.text
    assert "upload a picture first" in r.json()["detail"]


def test_the_picture_survives_turning_the_camera_on_and_off(client):
    """Somebody who turns a camera on and off again should find their photo
    where they left it. A state change is not a deletion."""
    uid, ada = _person(client, "Ada")
    host, _o = _profile(client, "acct_f10")
    rid = _room(client, [(uid, ada)], host)

    up = client.post(f"/rooms/{rid}/face/photo?interactor_id={uid}",
                     headers=ada, content=PNG).json()
    client.put(f"/rooms/{rid}/face", headers=ada,
               json={"interactor_id": uid, "showing": "camera"})
    back = client.put(f"/rooms/{rid}/face", headers=ada,
                      json={"interactor_id": uid, "showing": "photo"})
    assert back.status_code == 200, back.text
    assert back.json()["media_url"] == up["media_url"]


def test_taking_your_face_down_takes_the_picture_with_it(client):
    uid, ada = _person(client, "Ada")
    host, _o = _profile(client, "acct_f11")
    rid = _room(client, [(uid, ada)], host)
    client.post(f"/rooms/{rid}/face/photo?interactor_id={uid}",
                headers=ada, content=PNG)

    gone = client.request("DELETE", f"/rooms/{rid}/face?interactor_id={uid}",
                          headers=ada)
    assert gone.status_code == 200, gone.text
    assert gone.json()["showing"] == "voice"
    assert client.get(f"/rooms/{rid}/faces",
                      headers=ada).json()["faces"] == {}


# --- whose box it is --------------------------------------------------------

def test_nobody_decides_what_somebody_elses_box_shows(client):
    """Not a control this product offers anybody. The id in the body is
    checked against the token rather than believed."""
    a_id, ada = _person(client, "Ada")
    b_id, bo = _person(client, "Bo", "1991-02-02")
    host, _o = _profile(client, "acct_f12")
    rid = _room(client, [(a_id, ada), (b_id, bo)], host)

    r = client.put(f"/rooms/{rid}/face", headers=bo,
                   json={"interactor_id": a_id, "showing": "camera"})
    assert r.status_code in (401, 403), r.text


def test_somebody_outside_the_room_cannot_show_anything_in_it(client):
    a_id, ada = _person(client, "Ada")
    host, _o = _profile(client, "acct_f13")
    rid = _room(client, [(a_id, ada)], host)
    out_id, out = _person(client, "Stranger", "1985-05-05")

    r = client.put(f"/rooms/{rid}/face", headers=out,
                   json={"interactor_id": out_id, "showing": "camera"})
    assert r.status_code == 403, r.text
    assert "not in this room" in r.json()["detail"]


def test_an_unidentified_caller_cannot_read_the_scene(client):
    """A room id rides on beacons and printed stickers, so knowing one is not
    being here — the exact distinction `roommic` documented and did not
    check."""
    a_id, ada = _person(client, "Ada")
    host, _o = _profile(client, "acct_f14")
    rid = _room(client, [(a_id, ada)], host)

    assert client.get(f"/rooms/{rid}/faces").status_code == 401


def test_somebody_outside_the_room_cannot_read_the_scene(client):
    a_id, ada = _person(client, "Ada")
    host, _o = _profile(client, "acct_f15")
    rid = _room(client, [(a_id, ada)], host)
    _out_id, out = _person(client, "Stranger", "1985-05-05")

    r = client.get(f"/rooms/{rid}/faces", headers=out)
    assert r.status_code == 403, r.text


# --- the mask rides along ---------------------------------------------------

def test_the_scene_carries_who_is_wearing_what(client):
    """One call, because a client that needed a second one would draw a frame
    without the disclosure — and one frame is the whole of some rooms."""
    a_id, ada = _person(client, "Ada")
    host, _o = _profile(client, "acct_f16")
    rid = _room(client, [(a_id, ada)], host)

    client.put(f"/rooms/{rid}/face", headers=ada,
               json={"interactor_id": a_id, "showing": "camera"})
    worn = client.post(f"/places/room/{rid}/overlay", headers=ada, json={
        "interactor_id": a_id, "kind": "mask", "title": "The Wolf"})
    assert worn.status_code == 201, worn.text

    scene = client.get(f"/rooms/{rid}/faces", headers=ada).json()
    assert len(scene["wearing"]) == 1, scene
    mine = scene["wearing"][0]
    assert mine["interactor_id"] == a_id
    assert mine["covers_face"] is True
    assert "not their face" in mine["disclosure"], mine


def test_a_mask_is_not_a_way_of_showing(client):
    """Two records of two facts. Taking a mask off and turning a camera off
    are different actions and stay different actions."""
    a_id, ada = _person(client, "Ada")
    host, _o = _profile(client, "acct_f17")
    rid = _room(client, [(a_id, ada)], host)

    client.put(f"/rooms/{rid}/face", headers=ada,
               json={"interactor_id": a_id, "showing": "camera"})
    client.post(f"/places/room/{rid}/overlay", headers=ada, json={
        "interactor_id": a_id, "kind": "mask", "title": "The Wolf"})
    client.request("DELETE", f"/places/room/{rid}/overlay", headers=ada,
                   json={"interactor_id": a_id})

    scene = client.get(f"/rooms/{rid}/faces", headers=ada).json()
    assert scene["wearing"] == []
    assert scene["faces"][a_id]["showing"] == "camera", (
        "taking the mask off turned the camera off")


def test_an_invented_way_of_showing_is_refused(client):
    uid, ada = _person(client, "Ada")
    host, _o = _profile(client, "acct_f18")
    rid = _room(client, [(uid, ada)], host)

    r = client.put(f"/rooms/{rid}/face", headers=ada,
                   json={"interactor_id": uid, "showing": "hologram"})
    assert r.status_code == 422, r.text


def test_a_closed_room_takes_no_new_faces(client):
    uid, ada = _person(client, "Ada")
    host, _o = _profile(client, "acct_f19")
    rid = _room(client, [(uid, ada)], host)
    from qrme import db
    db.connect().execute("UPDATE rooms SET status='closed' WHERE id=?", (rid,))
    db.connect().commit()

    r = client.put(f"/rooms/{rid}/face", headers=ada,
                   json={"interactor_id": uid, "showing": "camera"})
    assert r.status_code == 409, r.text
