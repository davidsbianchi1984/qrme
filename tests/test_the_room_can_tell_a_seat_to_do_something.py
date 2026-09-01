"""Telling a synthetic seat, out loud in a room, to go and do something.

`roomreach` decided what a profile in a room *may* reach. That is a
permission nobody could spend: the machinery to act — write an authority
from a sentence, open a reach, see and move — was reachable only by an
owner, so a room could agree that a seat may drive a browser and had no
way to ask it to.

    asked     the profiles with connections should be verbally commanded
              or prompted to take action — cursor, screen, eyes, hands
    mattered  a permission nobody can spend does nothing

The tests below are about what an errand may and may not do with the two
keys. The headline is the one that makes this safe at all: a person can
ask a profile they do not own to act for them, and cannot thereby obtain
anything its owner did not already write down.
"""

from __future__ import annotations

from tests.test_capabilities import auth_header, make_profile


def _interactor(client, name="Sam"):
    r = client.post("/interactors", json={"display_name": name,
                                          "birthdate": "1990-01-01"})
    assert r.status_code == 201, r.text
    return r.json()


def _as(token):
    return {"authorization": f"Bearer {token}"}


def _room(client, profile, *users):
    r = client.post("/rooms", json={
        "topic": "the quarterly numbers", "channel": "chat",
        "participants": [{"kind": "profile", "id": profile["id"]}]
        + [{"kind": "user", "id": u["id"]} for u in users]})
    assert r.status_code == 201, r.text
    return r.json()


def _grant(client, profile, verbs, places=("mail.google.com",)):
    r = client.post(f"/profiles/{profile['id']}/hands/grants",
                    headers=auth_header(profile),
                    json={"surface": "computer", "places": list(places),
                          "verbs": list(verbs), "minutes": 30, "steps": 40})
    assert r.status_code in (200, 201), r.text
    return r.json()


def _tick(client, room, profile, grant, sam, allowed=True):
    r = client.put(f"/rooms/{room['id']}/reach", headers=_as(sam["token"]),
                   json={"profile_id": profile["id"], "kind": "skill",
                         "key": grant["id"], "allowed": allowed})
    assert r.status_code == 200, r.text


def _errand(client, room, profile, sam, said):
    return client.post(f"/rooms/{room['id']}/errand", headers=_as(sam["token"]),
                       json={"profile_id": profile["id"], "said": said})


# -- both keys, spent --------------------------------------------------------

def test_a_seat_with_both_keys_puts_its_hands_on_the_surface(client):
    p = make_profile(client)
    sam = _interactor(client)
    room = _room(client, p, sam)
    g = _grant(client, p, ["look", "press", "type", "done"])
    _tick(client, room, p, g, sam)

    r = _errand(client, room, p, sam, "open mail.google.com and reply to Dana")
    assert r.status_code == 201, r.text
    out = r.json()
    assert out["grant_id"] == g["id"]
    assert out["room_id"] == room["id"]
    assert out["asked_by"] == sam["id"], (
        "an errand a profile ran for somebody has to say for whom")
    assert out["eyes_only"] is False


def test_the_owner_key_alone_does_nothing(client):
    """Granted, never ticked. The refusal says which key is missing and
    where the box is, because "it won't do it" is the answer that makes
    somebody try the same sentence five times."""
    p = make_profile(client)
    sam = _interactor(client)
    room = _room(client, p, sam)
    _grant(client, p, ["look", "press", "done"])

    r = _errand(client, room, p, sam, "open mail.google.com")
    assert r.status_code == 422
    assert "this room has not allowed" in r.json()["detail"]


def test_the_rooms_key_alone_does_nothing(client):
    """Nothing granted, so there is nothing to tick — and the refusal
    says so rather than pointing at a box that would not help."""
    p = make_profile(client)
    sam = _interactor(client)
    room = _room(client, p, sam)

    r = _errand(client, room, p, sam, "open mail.google.com")
    assert r.status_code == 422
    assert "its owner has not given this profile hands" in r.json()["detail"]


def test_the_owner_revoking_ends_it_whatever_the_room_said(client):
    """Both keys are read fresh every time. An owner can revoke while a
    room is talking, and a tick outlives nothing."""
    p = make_profile(client)
    sam = _interactor(client)
    room = _room(client, p, sam)
    g = _grant(client, p, ["look", "press", "done"])
    _tick(client, room, p, g, sam)

    client.delete(f"/profiles/{p['id']}/hands/grants/{g['id']}",
                  headers=auth_header(p))

    r = _errand(client, room, p, sam, "open mail.google.com")
    assert r.status_code == 422
    assert "its owner has not given this profile hands" in r.json()["detail"]


def test_unticking_ends_it_without_touching_the_owners_grant(client):
    p = make_profile(client)
    sam = _interactor(client)
    room = _room(client, p, sam)
    g = _grant(client, p, ["look", "press", "done"])
    _tick(client, room, p, g, sam)
    assert _errand(client, room, p, sam, "open mail.google.com").status_code == 201

    _tick(client, room, p, g, sam, allowed=False)
    assert _errand(client, room, p, sam,
                   "open mail.google.com").status_code == 422

    live = client.get(f"/profiles/{p['id']}/hands/grants",
                      headers=auth_header(p)).json()["grants"]
    assert any(x["id"] == g["id"] and x["live"] for x in live), (
        "unticking in a room revoked the owner's grant")


# -- words narrow, and never widen ------------------------------------------

def test_words_naming_somewhere_the_grant_does_not_allow_are_refused(client):
    """Not a narrower version of the grant — a different one. The refusal
    names what it may reach instead."""
    p = make_profile(client)
    sam = _interactor(client)
    room = _room(client, p, sam)
    g = _grant(client, p, ["look", "press", "done"],
               places=["mail.google.com"])
    _tick(client, room, p, g, sam)

    r = _errand(client, room, p, sam, "open calendar.google.com and clear it")
    assert r.status_code == 422
    assert "mail.google.com" in r.json()["detail"]


def test_an_eyes_only_grant_opens_a_watching_reach_however_it_is_asked(client):
    """The mode is the grant's, not the sentence's. A sentence that could
    widen a permission is the one thing this shape must never allow."""
    p = make_profile(client)
    sam = _interactor(client)
    room = _room(client, p, sam)
    g = _grant(client, p, ["look", "wait", "done"])
    _tick(client, room, p, g, sam)

    out = _errand(client, room, p, sam,
                  "type my password into mail.google.com").json()
    assert out["eyes_only"] is True
    assert out["mode"] == "watching"


def test_the_smallest_grant_that_carries_the_errand_is_the_one_spent(client):
    """Two keys open the same door; the narrower is spent. An errand a
    watching grant can carry should not spend one that can type."""
    p = make_profile(client)
    sam = _interactor(client)
    room = _room(client, p, sam)
    eyes = _grant(client, p, ["look", "wait", "done"])
    hands_ = _grant(client, p, ["look", "press", "type", "done"])
    _tick(client, room, p, eyes, sam)
    _tick(client, room, p, hands_, sam)

    out = _errand(client, room, p, sam, "read mail.google.com to me").json()
    assert out["grant_id"] == eyes["id"]
    assert out["eyes_only"] is True


# -- who may ask -------------------------------------------------------------

def test_a_stranger_holding_the_room_id_cannot_send_an_errand(client):
    p = make_profile(client)
    sam = _interactor(client)
    room = _room(client, p, sam)
    g = _grant(client, p, ["look", "press", "done"])
    _tick(client, room, p, g, sam)
    outsider = _interactor(client, "Nell")

    r = client.post(f"/rooms/{room['id']}/errand", headers=_as(outsider["token"]),
                    json={"profile_id": p["id"], "said": "open mail.google.com"})
    assert r.status_code == 403


def test_a_profile_that_is_not_seated_takes_no_errand(client):
    p = make_profile(client)
    elsewhere = make_profile(client, handle="elsewhere")
    sam = _interactor(client)
    room = _room(client, p, sam)

    r = client.post(f"/rooms/{room['id']}/errand", headers=_as(sam["token"]),
                    json={"profile_id": elsewhere["id"], "said": "look"})
    assert r.status_code == 404


def test_nothing_said_is_not_an_errand(client):
    p = make_profile(client)
    sam = _interactor(client)
    room = _room(client, p, sam)
    g = _grant(client, p, ["look", "done"])
    _tick(client, room, p, g, sam)

    assert _errand(client, room, p, sam, "   ").status_code == 422
