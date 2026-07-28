"""Channel 3 — pointing your camera at the thing.

The test that carries the design is
`test_what_is_in_shot_decides_not_who_is_watching`. The obvious way to build
this gates on the viewer — *is it a person or a profile* — and that gets the
mechanic case wrong in one direction and the medical case wrong in the other.
A profile looking at an engine bay is useful and the stakes are a car; a
stranger watching a live view of somebody's body is not made safe by being
human.

The rest of the file is the difference between a live camera and a still. A
photograph is one framed moment somebody chose. A live view is whatever
happens to be behind it.
"""

import inspect
import re

import pytest

from qrme import viewfinder
from tests.test_capabilities import auth_header, make_profile


def _two(client):
    """A holder and a viewer, each with their own token.

    Profiles rather than interactors, matching `test_two_party_auth`: an owner
    token's subject is the profile id, which is what `require_self` compares
    against.
    """
    holder = make_profile(client, owner_id="owner-holder", display_name="Sam")
    viewer = make_profile(client, owner_id="owner-viewer", display_name="Rae")
    return holder, viewer


# -- the design ----------------------------------------------------------------

def test_what_is_in_shot_decides_not_who_is_watching(client):
    """The inversion the module is built on."""
    # A profile may look at a thing — this is the mechanic case, and it is the
    # reason the feature exists.
    assert viewfinder.may_watch("object", "profile") is True
    assert viewfinder.may_watch("document", "profile") is True
    assert viewfinder.may_watch("place", "profile") is True
    # And never at a body.
    assert viewfinder.may_watch("person", "profile") is False
    # A person may watch any of it — accountability is the difference.
    for subject in viewfinder.SUBJECTS:
        assert viewfinder.may_watch(subject, "person") is True


def test_a_profile_watching_a_body_is_refused_with_the_reason(client):
    holder, _ = _two(client)
    with pytest.raises(viewfinder.ViewfinderError) as exc:
        viewfinder.open_session(holder["id"], "connection", "con_1", "person",
                                "profile", "prf_1")
    msg = str(exc.value)
    assert "no examination" in msg and "no accountability" in msg
    assert "clinician" in msg          # it points somewhere useful


def test_the_mechanic_case_works_end_to_end(client):
    """The engine bay. If this is awkward the module has failed at its job."""
    holder, _ = _two(client)
    s = viewfinder.open_session(holder["id"], "connection", "con_2", "object",
                                "profile", "prf_mech", minutes=20,
                                note="knocking under load")
    assert s["live"] is True
    assert s["subject"] == "object" and s["viewer_kind"] == "profile"
    assert s["recording"] is False


def test_recording_a_body_for_a_profile_is_refused_twice(client):
    """Unreachable while `may_watch` refuses the pair, and guarded anyway —
    the day somebody widens the table is exactly the day it matters."""
    src = inspect.getsource(viewfinder.open_session)
    assert src.count("REFUSAL_PROFILE_ON_PERSON") == 2


def test_an_unknown_subject_or_viewer_is_refused(client):
    with pytest.raises(viewfinder.ViewfinderError):
        viewfinder.may_watch("aura", "person")
    with pytest.raises(viewfinder.ViewfinderError):
        viewfinder.may_watch("object", "hologram")


# -- the viewer never controls the camera --------------------------------------

def test_what_a_viewer_never_gets_is_published(client):
    """A remote party who can operate the camera on somebody's device has
    something categorically different from a view — and it is the thing people
    are actually afraid of when they decline."""
    out = client.get("/camera/vocabulary").json()
    for key in ("camera_control", "capture_trigger", "other_cameras",
                "location", "background_start", "silent_run"):
        assert key in out["never"], key
    assert "cannot zoom" in out["never"]["camera_control"]


def test_no_route_lets_a_viewer_act_on_the_camera(client):
    """Asserted against the router, because the easy way to add a zoom button
    is a new endpoint rather than a new argument."""
    from qrme.routers import viewfinder as router_mod

    src = inspect.getsource(router_mod)
    paths = set(re.findall(r'@router\.\w+\("([^"]+)"', src))
    for path in paths:
        for verb in ("zoom", "focus", "torch", "capture", "snapshot",
                     "record", "flip"):
            assert verb not in path, f"{path} looks like camera control"


def test_the_module_holds_no_frame(client):
    """Permission and state. The video never touches this database, and there
    is no column it could land in."""
    from qrme import db

    cols = {r[1] for r in db.connect().execute(
        "PRAGMA table_info(camera_sessions)").fetchall()}
    for forbidden in ("frame", "still", "thumbnail", "content", "image",
                      "data"):
        assert forbidden not in cols, f"camera_sessions has {forbidden!r}"


def test_it_writes_nothing_but_its_own_table(client):
    src = inspect.getsource(viewfinder)
    written = set(re.findall(r"(?:INSERT INTO|DELETE FROM)\s+(\w+)", src))
    written |= set(re.findall(r"(?<!DO )\bUPDATE\s+(\w+)\s+SET", src))
    assert written <= {"camera_sessions"}, f"writes elsewhere: {written}"


# -- ephemeral, capped, and the holder's to end --------------------------------

def test_it_does_not_record_unless_somebody_says_so(client):
    holder, _ = _two(client)
    s = viewfinder.open_session(holder["id"], "room", "rm_1", "object",
                                "person", "int_x")
    assert s["recording"] is False
    assert viewfinder.vocabulary()["records_by_default"] is False


def test_a_session_is_capped(client):
    holder, _ = _two(client)
    for bad in (0, viewfinder.MAX_MINUTES + 1):
        with pytest.raises(viewfinder.ViewfinderError):
            viewfinder.open_session(holder["id"], "room", "rm_2", "object",
                                    "person", "int_x", minutes=bad)
    ok = viewfinder.open_session(holder["id"], "room", "rm_2", "object",
                                 "person", "int_x",
                                 minutes=viewfinder.MAX_MINUTES)
    assert ok["minutes"] == viewfinder.MAX_MINUTES


def test_two_to_open_and_one_to_close(client):
    """The shape `sharing.py` uses for a lent skill: symmetric consent to
    start makes it a loan, asymmetric consent to end stops it being a trap."""
    holder, viewer = _two(client)
    s = viewfinder.open_session(holder["id"], "connection", "con_3", "object",
                                "person", viewer["id"])
    assert viewfinder.close(s["id"], viewer["id"])["state"] == "ended"

    s2 = viewfinder.open_session(holder["id"], "connection", "con_4", "object",
                                 "person", viewer["id"])
    assert viewfinder.close(s2["id"], holder["id"])["state"] == "ended"


def test_a_stranger_cannot_close_a_session(client):
    holder, viewer = _two(client)
    s = viewfinder.open_session(holder["id"], "room", "rm_3", "object",
                                "person", viewer["id"])
    with pytest.raises(viewfinder.ViewfinderError):
        viewfinder.close(s["id"], "somebody-else")


def test_a_camera_does_not_outlive_the_room(client):
    """Nobody remembers a permission granted inside a conversation that
    finished — the rule `roommic` applies to a lent microphone, applying
    harder to a lens."""
    holder, viewer = _two(client)
    viewfinder.open_session(holder["id"], "room", "rm_close", "object",
                            "person", viewer["id"])
    viewfinder.open_session(holder["id"], "room", "rm_close", "document",
                            "person", viewer["id"])
    assert len(viewfinder.live_on("room", "rm_close")) == 2

    assert viewfinder.close_place("room", "rm_close") == 2
    assert viewfinder.live_on("room", "rm_close") == []


# -- the disclosure is the design ----------------------------------------------

def test_the_surface_is_told_a_camera_is_live_and_whether_it_records(client):
    holder, viewer = _two(client)
    viewfinder.open_session(holder["id"], "room", "rm_d", "place", "person",
                            viewer["id"], record=True)
    out = viewfinder.disclosure_on("room", "rm_d")
    assert out["any_live"] is True and out["any_recording"] is True
    assert out["live"][0]["showing"] == "place"
    assert out["live"][0]["watched_by"] == viewer["id"]
    assert "no viewer can control it" in out["note"]


def test_the_disclosure_is_not_readable_by_anybody_holding_the_id(client):
    """A room id rides on printed beacon stickers. "Who has a camera live in
    there, and is it recording" is exactly what a stranger who scanned one
    must not be able to ask — the mistake `roommic` shipped once."""
    holder, viewer = _two(client)
    viewfinder.open_session(holder["id"], "room", "rm_secret", "place",
                            "person", viewer["id"])
    outsider = make_profile(client, owner_id="owner-nosy",
                            display_name="Nosy")

    r = client.get("/camera/disclosure/room/rm_secret",
                   headers=auth_header(outsider))
    assert r.status_code == 403, r.text
    ok = client.get("/camera/disclosure/room/rm_secret",
                    headers=auth_header(viewer))
    assert ok.status_code == 200 and ok.json()["any_live"] is True


def test_an_empty_surface_discloses_nothing_and_needs_no_token(client):
    """With no session live there is nothing to protect, and requiring a token
    would make "is a camera on in here" unanswerable to the person most
    entitled to ask."""
    r = client.get("/camera/disclosure/room/rm_empty",
                   headers={"authorization": ""})
    assert r.status_code == 200
    assert r.json()["any_live"] is False


# -- bystanders: what it cannot do ---------------------------------------------

def test_it_does_not_pretend_to_see_the_room(client):
    """A "bystander detection" toggle would be worse than the gap, because it
    would be relied on."""
    out = client.get("/camera/bystanders/place").json()
    assert "tell whether somebody has walked into shot" in out["we_cannot"]
    assert "blur" in out["we_cannot"]
    assert "you are the only party" in out["why_it_is_yours"].lower()
    assert "high" in out["risk"]
    # And it never claims a capability it does not have.
    assert "detect" not in str(out).lower()


def test_every_subject_carries_its_own_bystander_risk(client):
    for subject in viewfinder.SUBJECTS:
        note = viewfinder.bystander_guidance(subject)
        assert note["risk"]
    assert "workshop" in viewfinder.SUBJECTS["object"]["bystander_risk"]
    assert "names, numbers" in viewfinder.SUBJECTS["document"]["bystander_risk"]


def test_what_the_holder_declared_is_kept(client):
    holder, viewer = _two(client)
    s = viewfinder.open_session(holder["id"], "room", "rm_by", "place",
                                "person", viewer["id"],
                                bystanders_declared="two colleagues present")
    assert s["bystanders"] == "two colleagues present"


# -- over the wire -------------------------------------------------------------

def test_only_the_holder_can_start_a_session(client):
    """A session opened *for* somebody is a camera turned on remotely."""
    holder, viewer = _two(client)
    body = {"holder_id": holder["id"], "surface": "connection",
            "surface_id": "con_w", "subject": "object",
            "viewer_kind": "person", "viewer_id": viewer["id"]}
    forged = client.post("/camera/sessions", json=body,
                         headers=auth_header(viewer))
    assert forged.status_code == 403, forged.text

    ok = client.post("/camera/sessions", json=body,
                     headers=auth_header(holder))
    assert ok.status_code == 201, ok.text


def test_a_third_party_cannot_read_a_session(client):
    holder, viewer = _two(client)
    s = client.post("/camera/sessions",
                    json={"holder_id": holder["id"], "surface": "room",
                          "surface_id": "rm_r", "subject": "object",
                          "viewer_kind": "person", "viewer_id": viewer["id"]},
                    headers=auth_header(holder)).json()
    outsider = make_profile(client, owner_id="owner-nosy2",
                            display_name="Nosy2")
    assert client.get(f"/camera/sessions/{s['id']}",
                      headers=auth_header(outsider)).status_code == 403
    assert client.get(f"/camera/sessions/{s['id']}",
                      headers=auth_header(viewer)).status_code == 200


def test_your_live_cameras_are_yours_alone(client):
    """"Which of somebody's cameras are on right now" is not a question a
    third party gets to ask."""
    holder, viewer = _two(client)
    client.post("/camera/sessions",
                json={"holder_id": holder["id"], "surface": "room",
                      "surface_id": "rm_l", "subject": "object",
                      "viewer_kind": "person", "viewer_id": viewer["id"]},
                headers=auth_header(holder))
    assert client.get(f"/camera/live/{holder['id']}",
                      headers=auth_header(viewer)).status_code == 403
    mine = client.get(f"/camera/live/{holder['id']}",
                      headers=auth_header(holder))
    assert mine.status_code == 200 and len(mine.json()) == 1


def test_a_refused_pair_is_a_422_with_the_reason(client):
    holder, _ = _two(client)
    r = client.post("/camera/sessions",
                    json={"holder_id": holder["id"], "surface": "connection",
                          "surface_id": "con_x", "subject": "person",
                          "viewer_kind": "profile", "viewer_id": "prf_1"},
                    headers=auth_header(holder))
    assert r.status_code == 422
    assert "no accountability" in r.json()["detail"]


def test_the_vocabulary_publishes_the_refusals_by_name(client):
    out = client.get("/camera/vocabulary").json()
    assert out["may_watch"]["person"]["profile"] is False
    assert "profile_on_person" in out["refusals"]
    assert out["max_minutes"] == viewfinder.MAX_MINUTES


def test_closing_over_http_needs_to_be_you(client):
    holder, viewer = _two(client)
    s = client.post("/camera/sessions",
                    json={"holder_id": holder["id"], "surface": "room",
                          "surface_id": "rm_c", "subject": "object",
                          "viewer_kind": "person", "viewer_id": viewer["id"]},
                    headers=auth_header(holder)).json()
    forged = client.post(f"/camera/sessions/{s['id']}/close",
                         json={"actor_id": holder["id"]},
                         headers=auth_header(viewer))
    assert forged.status_code == 403

    ok = client.post(f"/camera/sessions/{s['id']}/close",
                     json={"actor_id": viewer["id"]},
                     headers=auth_header(viewer))
    assert ok.status_code == 200 and ok.json()["state"] == "ended"


def test_the_surface_vocabulary_matches_its_neighbours(client):
    """Three features naming the same places three ways is how a disclosure
    ends up on the wrong one."""
    from qrme import overlays

    assert set(viewfinder.SURFACES) <= set(overlays.SURFACES) | {"exchange"}


def test_making_a_profile_still_works(client):
    """The gate added last round covers every route; a new router must not
    have collided with it."""
    me = make_profile(client)
    assert me["id"]
