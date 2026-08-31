"""What a room lets the synthetic people in it reach.

A profile's owner decides what that profile can ever do. That was the
only key this product had, and it is not enough — a profile in a room is
very often somebody else's. A starter is outsourced from the account that
made it; a specialist is invited in by a person who does not own it. The
owner's grant says *this profile may drive a browser*. It does not say
*for you, now, in here*.

So the room holds a second key, and the tests below are about the seam
between the two: that ticking is the room's business and granting is the
owner's, that neither can stand in for the other, and that a person in a
room can never widen what somebody else's profile is able to do.
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


def _connect(client, profile, provider="google", app="gmail"):
    r = client.post(f"/profiles/{profile['id']}/apps",
                    json={"provider": provider, "app": app},
                    headers=auth_header(profile))
    assert r.status_code == 201, r.text
    return r.json()


# -- what the panel is looking at --------------------------------------------

def _app(body, provider="google", app="gmail", seat=0):
    """One row out of the catalog the panel draws."""
    for group in body["profiles"][seat]["providers"]:
        for row in group["apps"]:
            if (row["provider"], row["app"]) == (provider, app):
                return row
    raise AssertionError(f"{provider}/{app} is not in the catalog")


def test_the_room_lists_the_whole_catalog_under_every_seat(client):
    """Not only what a profile happens to hold.

    "What could this synthetic person reach" and "what has its owner
    actually wired up" are different questions, and a list that only ever
    shows the second cannot answer the first. The dark rows are what make
    the lit ones mean something."""
    from qrme import catalog

    p = make_profile(client)
    sam = _interactor(client)
    room = _room(client, p, sam)

    body = client.get(f"/rooms/{room['id']}/reach",
                      headers=_as(sam["token"])).json()
    assert [row["profile_id"] for row in body["profiles"]] == [p["id"]]
    row = body["profiles"][0]
    assert row["display"], "a box with no name on it is not a box"

    drawn = [a for g in row["providers"] for a in g["apps"]]
    assert len(drawn) == len(catalog.CONNECTORS) == row["app_count"]
    assert len(row["providers"]) == len(
        {c["provider"] for c in catalog.CONNECTORS})
    assert row["connected_count"] == 0
    assert all(not a["connected"] for a in drawn)


def test_a_row_its_owner_has_not_connected_cannot_be_ticked(client):
    """The room's key does not conjure the owner's. Allowing an app that
    nobody has connected would be a permission for something that cannot
    happen — the kind of yes that later reads as consent to something
    real."""
    p = make_profile(client)
    sam = _interactor(client)
    room = _room(client, p, sam)

    body = client.get(f"/rooms/{room['id']}/reach",
                      headers=_as(sam["token"])).json()
    row = _app(body)
    assert row["connected"] is False
    assert row["key"] is None, (
        "a row with no connector behind it must carry no key to tick")


def test_a_connection_arrives_switched_off(client):
    """Absent means no. A connector the owner just made is a thing the
    profile CAN reach, not a thing this room has agreed it may."""
    p = make_profile(client)
    sam = _interactor(client)
    room = _room(client, p, sam)
    _connect(client, p)

    body = client.get(f"/rooms/{room['id']}/reach",
                      headers=_as(sam["token"])).json()
    got = _app(body)
    assert got["connected"] is True and got["key"]
    assert got["allowed"] is False


def test_ticking_a_box_lets_it_through_and_unticking_takes_it_back(client):
    """Both directions through the same door — "untick this" is the half
    of a permission that has to work."""
    from qrme import roomreach

    p = make_profile(client)
    sam = _interactor(client)
    room = _room(client, p, sam)
    app = _connect(client, p)

    on = client.put(f"/rooms/{room['id']}/reach", headers=_as(sam["token"]),
                    json={"profile_id": p["id"], "kind": "app",
                          "key": app["id"], "allowed": True})
    assert on.status_code == 200, on.text
    assert on.json()["allowed"] is True
    assert roomreach.allows(room["id"], p["id"], "app", app["id"])

    off = client.put(f"/rooms/{room['id']}/reach", headers=_as(sam["token"]),
                     json={"profile_id": p["id"], "kind": "app",
                           "key": app["id"], "allowed": False})
    assert off.status_code == 200
    assert not roomreach.allows(room["id"], p["id"], "app", app["id"])


def test_the_tick_says_who_turned_it(client):
    """"Who let it do that" has to have a name in it."""
    p = make_profile(client)
    sam = _interactor(client)
    room = _room(client, p, sam)
    app = _connect(client, p)

    out = client.put(f"/rooms/{room['id']}/reach", headers=_as(sam["token"]),
                     json={"profile_id": p["id"], "kind": "app",
                           "key": app["id"], "allowed": True}).json()
    assert out["decided_by"] == sam["id"]
    assert out["decided_at"]


# -- the seam between the two keys -------------------------------------------

def test_the_rooms_key_never_touches_the_owners(client):
    """A person in a room can narrow what somebody else's profile does in
    front of them. They cannot widen what it is able to do at all."""
    p = make_profile(client)
    sam = _interactor(client)
    room = _room(client, p, sam)
    app = _connect(client, p)

    client.put(f"/rooms/{room['id']}/reach", headers=_as(sam["token"]),
               json={"profile_id": p["id"], "kind": "app",
                     "key": app["id"], "allowed": True})

    owned = client.get(f"/profiles/{p['id']}/apps",
                       headers=auth_header(p)).json()
    assert [a["id"] for a in owned] == [app["id"]]
    assert owned[0]["status"] == "active", (
        "the room's tick rewrote the owner's connector")


def test_a_revoked_connector_takes_its_box_with_it(client):
    """The owner's key turning back off ends it, whatever the room said.
    A reach reads both sides every time rather than trusting the tick."""
    p = make_profile(client)
    sam = _interactor(client)
    room = _room(client, p, sam)
    app = _connect(client, p)
    client.put(f"/rooms/{room['id']}/reach", headers=_as(sam["token"]),
               json={"profile_id": p["id"], "kind": "app",
                     "key": app["id"], "allowed": True})

    client.delete(f"/apps/{app['id']}", headers=auth_header(p))

    body = client.get(f"/rooms/{room['id']}/reach",
                      headers=_as(sam["token"])).json()
    row = _app(body)
    assert row["connected"] is False and row["key"] is None


def test_a_remade_connection_does_not_inherit_the_old_yes(client):
    """Keyed on the connector's id, not on its name. Revoking Gmail and
    connecting Gmail again is a new thing to say yes to."""
    p = make_profile(client)
    sam = _interactor(client)
    room = _room(client, p, sam)
    first = _connect(client, p)
    client.put(f"/rooms/{room['id']}/reach", headers=_as(sam["token"]),
               json={"profile_id": p["id"], "kind": "app",
                     "key": first["id"], "allowed": True})
    client.delete(f"/apps/{first['id']}", headers=auth_header(p))

    again = _connect(client, p)
    assert again["id"] != first["id"]
    body = client.get(f"/rooms/{room['id']}/reach",
                      headers=_as(sam["token"])).json()
    assert _app(body)["allowed"] is False


# -- who may look, and who may turn ------------------------------------------

def test_a_stranger_holding_the_room_id_sees_nothing(client):
    """A room id travels on printed stickers. What the people in a room
    have permitted is for the people in the room."""
    p = make_profile(client)
    sam = _interactor(client)
    room = _room(client, p, sam)
    outsider = _interactor(client, "Nell")

    r = client.get(f"/rooms/{room['id']}/reach",
                   headers=_as(outsider["token"]))
    assert r.status_code == 403, r.text


def test_a_stranger_cannot_tick_a_box(client):
    p = make_profile(client)
    sam = _interactor(client)
    room = _room(client, p, sam)
    app = _connect(client, p)
    outsider = _interactor(client, "Nell")

    r = client.put(f"/rooms/{room['id']}/reach",
                   headers=_as(outsider["token"]),
                   json={"profile_id": p["id"], "kind": "app",
                         "key": app["id"], "allowed": True})
    assert r.status_code == 403


def test_a_box_cannot_be_ticked_for_a_profile_that_is_not_here(client):
    """A permission attached to nothing."""
    p = make_profile(client)
    elsewhere = make_profile(client, handle="elsewhere")
    sam = _interactor(client)
    room = _room(client, p, sam)

    r = client.put(f"/rooms/{room['id']}/reach", headers=_as(sam["token"]),
                   json={"profile_id": elsewhere["id"], "kind": "app",
                         "key": "app_whatever", "allowed": True})
    assert r.status_code == 404


def test_a_room_allows_an_app_or_a_skill_and_nothing_else(client):
    p = make_profile(client)
    sam = _interactor(client)
    room = _room(client, p, sam)

    r = client.put(f"/rooms/{room['id']}/reach", headers=_as(sam["token"]),
                   json={"profile_id": p["id"], "kind": "everything",
                         "key": "*", "allowed": True})
    assert r.status_code == 422


def test_a_capability_is_a_narrower_yes_inside_the_apps_yes(client):
    """"Read the mail" and "send it" are not the same permission, and a
    panel that cannot tell them apart is a panel that grants both."""
    p = make_profile(client)
    sam = _interactor(client)
    room = _room(client, p, sam)
    app = _connect(client, p)

    body = client.get(f"/rooms/{room['id']}/reach",
                      headers=_as(sam["token"])).json()
    caps = _app(body)["capabilities"]
    assert caps and all(c["granted"] for c in caps)
    assert all(c["allowed"] is False for c in caps)

    one = caps[0]["name"]
    r = client.put(f"/rooms/{room['id']}/reach", headers=_as(sam["token"]),
                   json={"profile_id": p["id"], "kind": "cap",
                         "key": f"{app['id']}:{one}", "allowed": True})
    assert r.status_code == 200, r.text

    body = client.get(f"/rooms/{room['id']}/reach",
                      headers=_as(sam["token"])).json()
    got = {c["name"]: c["allowed"] for c in _app(body)["capabilities"]}
    assert got[one] is True
    assert sum(got.values()) == 1, "one yes became several"


# -- eyes, hands, and the difference between them ----------------------------

def _grant(client, profile, verbs, places=("mail.google.com",)):
    r = client.post(f"/profiles/{profile['id']}/hands/grants",
                    headers=auth_header(profile),
                    json={"surface": "computer", "places": list(places),
                          "verbs": list(verbs), "minutes": 30, "steps": 40})
    assert r.status_code in (200, 201), r.text
    return r.json()


def test_a_live_grant_is_a_box_and_arrives_switched_off(client):
    p = make_profile(client)
    sam = _interactor(client)
    room = _room(client, p, sam)
    grant = _grant(client, p, ["look", "press", "type", "done"])

    body = client.get(f"/rooms/{room['id']}/reach",
                      headers=_as(sam["token"])).json()
    skills = body["profiles"][0]["skills"]
    assert [s["key"] for s in skills] == [grant["id"]]
    assert skills[0]["surface"] == "computer"
    assert skills[0]["allowed"] is False


def test_a_looking_grant_says_it_only_looks(client):
    """Worth saying on the box. "You may read my screen" and "you may
    drive it" are the two sides of this panel, and making somebody read
    four verbs to tell them apart is how the wrong box gets ticked."""
    p = make_profile(client)
    sam = _interactor(client)
    room = _room(client, p, sam)
    _grant(client, p, ["look", "wait", "done"])
    _grant(client, p, ["look", "press", "type", "done"])

    body = client.get(f"/rooms/{room['id']}/reach",
                      headers=_as(sam["token"])).json()
    eyes = {s["eyes_only"] for s in body["profiles"][0]["skills"]}
    assert eyes == {True, False}


def test_a_revoked_grant_takes_its_box_with_it(client):
    p = make_profile(client)
    sam = _interactor(client)
    room = _room(client, p, sam)
    grant = _grant(client, p, ["look", "done"])
    client.put(f"/rooms/{room['id']}/reach", headers=_as(sam["token"]),
               json={"profile_id": p["id"], "kind": "skill",
                     "key": grant["id"], "allowed": True})

    client.delete(f"/profiles/{p['id']}/hands/grants/{grant['id']}",
                  headers=auth_header(p))

    body = client.get(f"/rooms/{room['id']}/reach",
                      headers=_as(sam["token"])).json()
    assert body["profiles"][0]["skills"] == []
