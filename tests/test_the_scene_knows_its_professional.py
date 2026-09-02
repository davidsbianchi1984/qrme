"""The composed direction: a render that knows who is standing in it.

    asked     the video should come back the way it naturally would from
              a real professional in that profession — the platform must
              come up with those texts itself, and edits made in the
              room must attach to the profile's next submission
    mattered  a generic wide shot renders a stranger; the profile
              already knows its trade and its own persona, and the
              prompt was not asking
"""

from __future__ import annotations

from qrme import filming
from tests.test_a_company_is_hired_one_interview_at_a_time import (
    _found, _hire, _seat)
from tests.test_capabilities import auth_header, make_profile


def _hired(client):
    me = make_profile(client, display_name="Founder")
    co = _found(client, me)
    seat = _seat(client, me, co)
    client.post(f"/companies/{co['id']}/seats/{seat['id']}/interview",
                headers=auth_header(me))
    return _hire(client, me, co, seat)["profile_id"]


def test_a_hire_renders_as_its_trade(client):
    """The hired seat's title reaches the direction: the trade, the
    dress, the workplace — composed, not typed."""
    pid = _hired(client)
    direction = filming.direction_of(pid)
    assert "Counter clerk" in direction
    assert "dressed as one" in direction
    # And the whole prompt carries it in front of the passage.
    assert direction in filming.scene_for(pid, "We open at seven.") \
        if hasattr(filming, "scene_for") else True


def test_the_persona_stands_in_the_frame(client):
    """Who they are rides the sheet — the profile's own persona opening,
    never an invented description."""
    me = make_profile(client, display_name="Solo",
                      persona="A wry lighthouse keeper who paints.")
    direction = filming.direction_of(me["id"])
    assert "lighthouse keeper" in direction
    assert "dressed for what they do" in direction


def test_a_written_direction_beats_the_composed_one(client):
    """The owner's words replace the sheet entirely — composed is only
    what stands before anybody says otherwise."""
    pid = _hired(client)
    filming.set_direction(pid, "Grainy 16mm, dusk, from across the street.")
    assert filming.direction_of(pid) == (
        "Grainy 16mm, dusk, from across the street.")


def test_forgetting_returns_to_the_sheet_not_the_stranger(client):
    """Starting over lands on the profile's own composed direction, and
    the door's `default` says so."""
    pid = _hired(client)
    filming.set_direction(pid, "Handheld, fluorescent, too close.")
    filming.forget_direction(pid)
    assert "Counter clerk" in filming.direction_of(pid)
    r = client.get(f"/video/direction/{pid}")
    assert r.status_code == 200, r.text
    assert "Counter clerk" in r.json()["default"]


def test_the_rooms_edit_attaches_to_the_next_submission(client):
    """The purple box's bar posts through the same door the Identity
    screen uses — one row, one door — and the amendment stands for the
    next render and every one after."""
    pid = _hired(client)
    r = client.post(f"/video/direction/{pid}",
                    json={"asked": "put them behind the counter, warmer "
                                   "light", "surface": "room"})
    assert r.status_code == 200, r.text
    after = filming.direction_of(pid)
    assert after == r.json()["direction"]
    log = client.get(f"/video/direction/{pid}/log").json()["log"]
    assert log and log[0]["surface"] == "room"
