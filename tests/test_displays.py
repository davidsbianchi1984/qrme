"""A profile on a screen that stays where it is.

Same idea as the watch faces — a closed set of things a screen may show — and
the tests that matter are the ones about why the set is *shorter*. A watch is
on one person's wrist; they chose it and they are the only one reading it. A
wall panel is read by whoever walks past, and nobody in that corridor opted
into anything.
"""

import pytest

from qrme import displays
from tests.test_capabilities import auth_header, make_profile


def _screen(client, p, **over):
    body = {"kind": "wall_panel", "label": "the lobby panel"}
    body.update(over)
    return client.post(f"/profiles/{p['id']}/displays", json=body,
                       headers=auth_header(p))


# -- small or full, glass or not ----------------------------------------------

def test_a_profile_can_go_on_a_wall(client):
    p = make_profile(client, display_name="Otis Marsh")
    r = _screen(client, p)
    assert r.status_code == 201, r.text
    out = r.json()
    assert out["kind"] == "wall_panel" and out["live"] is True
    assert out["faces"] == list(displays.DEFAULT_FACES)


def test_every_size_and_finish_is_available(client):
    p = make_profile(client)
    for size in displays.SIZES:
        for finish in displays.FINISHES:
            faces = ["presence"] if size == "badge" else None
            r = _screen(client, p, size=size, finish=finish, faces=faces,
                        label=f"{size}-{finish}")
            assert r.status_code == 201, f"{size}/{finish}: {r.text}"


def test_a_beacon_needs_the_whole_surface(client):
    """Not neatness. A QR at strip height is a QR nobody's camera resolves, and
    a code that cannot be scanned looks broken rather than absent."""
    p = make_profile(client)
    r = _screen(client, p, size="badge", faces=["beacon"])
    assert r.status_code == 422
    assert "too small for a phone to read" in r.json()["detail"]
    assert _screen(client, p, size="full", faces=["beacon"],
                   label="door kiosk").status_code == 201


# -- the reason the list is shorter than the watch's --------------------------

def test_nothing_private_may_go_on_a_wall(client):
    """The whole argument. A watch is read by its wearer; a wall by whoever
    walks past — a courier, a child, somebody visiting the person whose
    profile it shows."""
    p = make_profile(client)
    for face in ("messages", "memory", "friends", "notifications"):
        r = _screen(client, p, faces=[face], label=face)
        assert r.status_code == 422, face
        assert r.json()["detail"] == displays.NEVER[face]


def test_agent_names_never_reach_a_corridor(client):
    """Watch face 01 already shows counts and not names, for one person's own
    wrist. A corridor is not that, so the same rule applies harder."""
    p = make_profile(client)
    assert _screen(client, p, faces=["agent_names"]).status_code == 422
    ok = _screen(client, p, faces=["agents"], label="counts only")
    assert ok.status_code == 201
    assert displays.FACES["agents"]["shows"].endswith("never agent names")


def test_there_is_no_control_face(client):
    """Assist, halt and approve are safe on a wrist because the wrist is the
    owner's. A button on a wall is pressed by whoever reaches it."""
    from qrme import wearables

    assert "control" in wearables.FACES        # the watch has one
    assert "control" not in displays.FACES     # the wall does not
    r = _screen(client, p := make_profile(client), faces=["control"])
    assert r.status_code == 422
    assert "whoever reaches it" in r.json()["detail"]


def test_every_face_on_the_list_is_public(client):
    """The check on the whole design: `GET /displays/{id}` is public, so if it
    could leak anything, the wrong thing is on the face list."""
    assert all(not f["private"] for f in displays.FACES.values())


def test_a_screen_showing_nothing_is_a_screen_turned_off(client):
    p = make_profile(client)
    assert _screen(client, p, faces=[]).status_code == 422


# -- the mark has to survive the glass ----------------------------------------

def test_the_mark_gets_a_plate_on_glass(client):
    """A transparent panel's background is a corridor, and a moving one, so
    contrast is not something the renderer controls. A mark that vanishes
    against a bright wall is worse than no mark, because the rest of the card
    still reads as a person."""
    p = make_profile(client)
    glass = _screen(client, p, finish="transparent", label="window").json()
    assert glass["mark"]["backing_plate"] is True
    assert "moves" in glass["mark"]["why"]

    solid = _screen(client, p, finish="opaque", label="lobby").json()
    assert solid["mark"]["backing_plate"] is False
    assert solid["mark"]["min_contrast"] == glass["mark"]["min_contrast"]


# -- who may place, change and read -------------------------------------------

def test_only_the_owner_puts_a_profile_on_a_wall(client):
    """Where a profile is shown is a decision about the profile — a screen
    bolted to a wall is a beacon with a plug in it."""
    p = make_profile(client, owner_id="o1", display_name="Mine")
    other = make_profile(client, owner_id="o2", display_name="Theirs")
    r = client.post(f"/profiles/{p['id']}/displays",
                    json={"kind": "kiosk", "label": "anywhere"},
                    headers=auth_header(other))
    assert r.status_code == 403
    assert client.post(f"/profiles/{p['id']}/displays",
                       json={"kind": "kiosk", "label": "anywhere"},
                       headers={"authorization": ""}).status_code == 401


def test_where_the_screens_are_is_not_public(client):
    """A list of physical places associated with a person — the same reason
    the beacon listing is withheld."""
    p = make_profile(client, owner_id="o1")
    other = make_profile(client, owner_id="o2")
    _screen(client, p, location="reception, second floor")
    assert client.get(f"/profiles/{p['id']}/displays",
                      headers=auth_header(other)).status_code == 403
    assert client.get(f"/profiles/{p['id']}/displays",
                      headers={"authorization": ""}).status_code == 401
    mine = client.get(f"/profiles/{p['id']}/displays", headers=auth_header(p))
    assert mine.status_code == 200


def test_what_a_screen_shows_is_public_on_purpose(client):
    """A fixture in a corridor displays to whoever walks past, so what it is
    displaying cannot be a secret from them."""
    p = make_profile(client)
    did = _screen(client, p).json()["id"]
    seen = client.get(f"/displays/{did}", headers={"authorization": ""})
    assert seen.status_code == 200
    assert seen.json()["faces"] == list(displays.DEFAULT_FACES)


def test_a_stranger_cannot_take_your_panel_down(client):
    """The beacon pick-up problem with a bigger screen."""
    p = make_profile(client, owner_id="o1")
    other = make_profile(client, owner_id="o2")
    did = _screen(client, p).json()["id"]
    assert client.delete(f"/displays/{did}",
                         headers=auth_header(other)).status_code == 403
    assert client.delete(f"/displays/{did}",
                         headers=auth_header(p)).status_code == 200
    assert displays.read(did)["live"] is False


def test_taking_it_down_keeps_the_record(client):
    """Like an unpaired wearable: a profile that was on a lobby wall for a
    year should still be able to say where it was."""
    p = make_profile(client)
    did = _screen(client, p, location="reception").json()["id"]
    client.delete(f"/displays/{did}", headers=auth_header(p))
    gone = displays.for_profile(p["id"], include_removed=True)
    assert [d["id"] for d in gone] == [did]
    assert gone[0]["location"] == "reception"
    assert displays.for_profile(p["id"]) == []


def test_only_the_owner_changes_what_it_shows(client):
    p = make_profile(client, owner_id="o1")
    other = make_profile(client, owner_id="o2")
    did = _screen(client, p).json()["id"]
    assert client.put(f"/displays/{did}/faces", json={"faces": ["presence"]},
                      headers=auth_header(other)).status_code == 403
    ok = client.put(f"/displays/{did}/faces", json={"faces": ["presence"]},
                    headers=auth_header(p))
    assert ok.status_code == 200 and ok.json()["faces"] == ["presence"]


def test_a_private_face_cannot_be_swapped_in_later(client):
    """The check has to be on the change as well as on the placement — the
    usual way a rule gets around is the second door."""
    p = make_profile(client)
    did = _screen(client, p).json()["id"]
    r = client.put(f"/displays/{did}/faces", json={"faces": ["messages"]},
                   headers=auth_header(p))
    assert r.status_code == 422
    assert displays.read(did)["faces"] == list(displays.DEFAULT_FACES)


def test_the_vocabulary_publishes_what_a_wall_may_never_show(client):
    """A limit nobody can read is a limit nobody can rely on. Every entry is
    something that *is* allowed on the watch or the phone."""
    out = client.get("/displays/vocabulary").json()
    never = {n["thing"] for n in out["never"]}
    assert never == set(displays.NEVER)
    assert all(n["why"] for n in out["never"])
    assert "a wall has no idea who is in front of it" in " ".join(out["rules"])
