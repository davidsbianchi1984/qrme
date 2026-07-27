"""The helper dock — the pane in the corner of the app.

The tests that matter here are the structural ones. A floating pane is the
easiest surface in the product to quietly grow: it is always on screen, so
every feature wants a button on it, and every button on it is a button sitting
on top of a live stream. So the rules are asserted rather than documented —
that it casts the same faces as the wrist, that it never acts, and that
nothing in `NEVER` can reach it.
"""

import inspect
import pathlib
import re

import pytest

from qrme import dock, help as help_mod, tutorial, wearables
from tests.test_capabilities import auth_header, make_profile


# -- the bindings that keep it honest -----------------------------------------

def test_every_wrist_face_is_cast_or_refused_by_name(client):
    """Two catalogues of the same glances would drift, and the one nobody
    re-reads wins. A face added to the watch must appear in the pane or be
    turned away here with a reason a client can render."""
    for face in wearables.FACES:
        assert face in dock.FACES or face in dock.REFUSED, (
            f"{face!r} is on the wrist and neither cast nor refused in the "
            "dock — add it to dock.FACES or say why in dock.REFUSED")
    for face in dock.FACES:
        assert face in wearables.FACES or face == dock.HELPER_FACE, (
            f"{face!r} is in the dock but not on the wrist")


def test_the_cast_faces_are_described_by_the_wrist_not_beside_it(client):
    """The `identity.shown_name` lesson: the decision lives in one place or it
    lives in fifteen. The dock's descriptions are the wrist's."""
    for face, what in dock.FACES.items():
        if face == dock.HELPER_FACE:
            continue
        assert what == wearables.FACES[face]


def test_every_face_has_a_route_to_a_screen_that_exists(client):
    """A read-only pane whose faces went nowhere would be a dead end. Every
    face carries a way out, and the screen it names has to be drawn."""
    root = pathlib.Path(__file__).resolve().parent.parent / "docs" / "screens"
    drawn = {int(p.name.split("-", 1)[0]) for p in root.glob("*.svg")
             if p.name.split("-", 1)[0].isdigit()}
    for face in dock.FACES:
        route = dock.route(face)
        assert route["screen"] in drawn, (
            f"the {face} face routes to screen {route['screen']}, "
            "which is not drawn")
        assert route["path"].startswith("/")


def test_the_helper_can_direct_somebody_to_every_lesson(client):
    """"Where is it" is the question the help box gets most and used to answer
    worst. A lesson with no directions is a feature the assistant cannot point
    at, however well the walkthrough covers it."""
    for lesson in tutorial.LESSONS:
        assert lesson["key"] in help_mod.DIRECTIONS, (
            f"no phrasing reaches {lesson['key']!r} — add one to "
            "help.DIRECTIONS")


def test_directions_never_name_a_lesson_that_is_gone(client):
    for key in help_mod.DIRECTIONS:
        tutorial._index(key)          # raises if the lesson was renamed away


# -- it shows and it routes; it never acts ------------------------------------

def test_the_dock_writes_nothing_but_where_it_sits(client):
    """The rule that makes a pane floating over a live stream safe. A control
    here is a control on top of the thing it would stop."""
    src = inspect.getsource(dock)
    # The table each write verb actually names, rather than a line-at-a-time
    # substring hunt — an upsert's `DO UPDATE SET` continuation is not a second
    # statement, and a guard that cannot tell the difference is one somebody
    # silences instead of satisfying.
    written = set(re.findall(r"(?:INSERT INTO|DELETE FROM)\s+(\w+)", src))
    written |= set(re.findall(r"(?<!DO )\bUPDATE\s+(\w+)\s+SET", src))
    assert written <= {"dock_prefs"}, (
        f"the dock writes outside its own preferences: {written}")


def test_no_route_in_the_dock_router_acts(client):
    """Asserted against the router rather than the module, because the easy
    way to add a button here is a new endpoint, not a new function."""
    from qrme.routers import dock as router_mod

    src = inspect.getsource(router_mod)
    methods = set(re.findall(r"@router\.(get|post|put|patch|delete)", src))
    assert methods <= {"get", "put"}, (
        f"the dock router gained {methods - {'get', 'put'}} — the only write "
        "it may do is saving where the pane sits")
    # And the one write is the preferences route, by name.
    assert src.count("@router.put") == 1
    assert "def configure" in src


def test_every_face_says_it_does_not_act(client):
    me = make_profile(client)
    for face in dock.FACES:
        kwargs = {"surface_id": "sur_1"} if face in dock.PER_SURFACE else {}
        assert dock.face(me["id"], face, **kwargs)["acts"] is False
    assert dock.vocabulary()["acts"] is False


def test_control_is_refused_with_a_reason_a_client_can_show(client):
    """Not merely absent. A client that knew only the allowed list would draw
    `control` as a missing feature rather than a decision."""
    assert "control" in wearables.FACES        # it is a real wrist face
    assert "control" not in dock.FACES
    assert "Control Center" in dock.REFUSED["control"]
    with pytest.raises(dock.DockError):
        dock.route("control")


# -- the corner ----------------------------------------------------------------

def test_the_pane_can_only_sit_at_the_bottom(client):
    """The top-left carries whose surface this is and the top-right carries the
    recording light. A pane that could cover either could hide who you are
    watching, or whether you are live."""
    assert set(dock.CORNERS) == {"bottom_right", "bottom_left"}
    me = make_profile(client)
    with pytest.raises(dock.DockError):
        dock.configure(me["id"], corner="top_left")


def test_a_left_handed_grip_is_a_supported_corner(client):
    me = make_profile(client)
    out = dock.configure(me["id"], corner="bottom_left")
    assert out["corner"] == "bottom_left"


def test_the_desktop_starts_open_on_the_lights_and_the_phone_tucked(client):
    """The desktop corner already held a pinned lights panel with no lid. It is
    now the dock, and the panel's own reason is what makes the default differ:
    a desktop user has no wrist, and amber and red are the states nobody thinks
    to go looking for. On a phone the pane covers content there is none to
    spare of."""
    me = make_profile(client)
    assert dock.settings(me["id"], "desktop")["state"] == "open"
    assert dock.settings(me["id"], "desktop")["face"] == "agents"
    assert dock.settings(me["id"], "phone")["state"] == "handle"
    assert dock.settings(me["id"], "phone")["face"] == dock.HELPER_FACE


def test_a_choice_travels_between_platforms(client):
    """The defaults differ because the first-run guess differs, not because the
    pane is two features. Once somebody has moved it, their row wins."""
    me = make_profile(client)
    dock.configure(me["id"], state="hidden")
    for platform in dock.DEFAULT_STATE_ON:
        assert dock.settings(me["id"], platform)["state"] == "hidden"


def test_an_unknown_platform_is_refused(client):
    me = make_profile(client)
    with pytest.raises(dock.DockError):
        dock.settings(me["id"], "fridge")


def test_the_desktop_mockups_all_carry_the_dock(client):
    """Drawn in the shared render path rather than per view, because a handle
    that appeared on the three views somebody remembered is exactly the
    documented-but-not-implemented gap this repo keeps finding."""
    root = pathlib.Path(__file__).resolve().parent.parent / "docs" / "desktop"
    svgs = sorted(root.rglob("*.svg"))
    assert len(svgs) == 28
    for path in svgs:
        src = path.read_text()
        assert "open Agents" in src, f"{path.name} has no dock pane"
        # The handle, at the geometry dock.BOX specifies — so the mockup
        # cannot drift from what a client is told to draw.
        assert 'r="22"' in src, f"{path.name} has no dock handle"


def test_it_draws_before_anybody_has_touched_it(client):
    """The pane has to render on first launch. A client that had to know the
    defaults would be a second place they were written down."""
    me = make_profile(client)
    out = dock.settings(me["id"])
    assert out["set"] is False
    assert out["corner"] == dock.DEFAULT_CORNER
    assert out["state"] == dock.DEFAULT_STATE
    assert out["face"] == dock.HELPER_FACE


# -- it is inside the capture --------------------------------------------------

def test_it_tucks_itself_on_a_surface_that_is_going_out(client):
    """A pane pinned to the frame is in every screenshot and every screen
    share, including the one being broadcast right now."""
    me = make_profile(client)
    dock.configure(me["id"], state="open")
    for surface in dock.TUCKED:
        out = dock.opens_as(me["id"], surface)
        assert out["state"] == "handle" and out["tucked"] is True
        assert "capture" in out["why"]


def test_tucking_caps_the_preference_rather_than_rewriting_it(client):
    """The same shape as roommic's capped gain: a preference that was
    overridden is still the owner's, and silently changing it would mean the
    settings screen and the pane disagreed about what was chosen."""
    me = make_profile(client)
    dock.configure(me["id"], state="open")
    on_air = dock.opens_as(me["id"], "stream")
    assert on_air["state"] == "handle"
    assert on_air["wanted"] == "open"
    assert dock.settings(me["id"])["state"] == "open"    # untouched on disk
    assert dock.opens_as(me["id"], "feed")["state"] == "open"


def test_hidden_is_a_real_state_and_not_just_tucked(client):
    """Somebody presenting, recording, or handing their phone over wants the
    corner empty. "Just do not tap it" is not an answer for a thing that is in
    every frame they capture."""
    me = make_profile(client)
    out = dock.configure(me["id"], state="hidden")
    assert out["state"] == "hidden"
    assert dock.opens_as(me["id"], "stream")["state"] == "hidden"


def test_what_may_never_be_in_the_pane_is_published(client):
    for key in ("message_bodies", "memory", "agent_names", "viewer_names"):
        assert key in dock.NEVER
    assert set(dock.vocabulary()["never"]) == set(dock.NEVER)


# -- a face about a place needs the place --------------------------------------

def test_a_per_surface_face_refuses_to_guess(client):
    """Which live, which game, which room. The pane is floating over one, so it
    can be told — and answering about the wrong one would be worse than
    refusing."""
    me = make_profile(client)
    for face in dock.PER_SURFACE:
        with pytest.raises(dock.DockError):
            dock.face(me["id"], face)
        assert dock.face(me["id"], face, "live", "sur_1")["surface_id"] == "sur_1"


def test_an_unknown_face_is_refused(client):
    me = make_profile(client)
    with pytest.raises(dock.DockError):
        dock.face(me["id"], "nonsense")
    with pytest.raises(dock.DockError):
        dock.configure(me["id"], faces=["nonsense"])


def test_the_face_it_opens_on_has_to_be_one_it_carries(client):
    me = make_profile(client)
    with pytest.raises(dock.DockError):
        dock.configure(me["id"], face="lobby", faces=["helper", "identity"])


def test_a_pane_with_no_faces_is_the_button_on_its_own(client):
    me = make_profile(client)
    with pytest.raises(dock.DockError):
        dock.configure(me["id"], faces=[])


# -- over the wire -------------------------------------------------------------

def test_the_vocabulary_and_the_routing_table_are_public(client):
    """The helper answers "where is it" for somebody who has not signed in,
    and a beacon scan lands strangers on screens with the button on them."""
    plain = {"authorization": ""}
    assert client.get("/dock/faces", headers=plain).status_code == 200
    r = client.get("/dock/where/identity", headers=plain)
    assert r.status_code == 200 and r.json()["screen"] == 119
    assert client.get("/dock/where/control", headers=plain).status_code == 404


def test_the_pane_itself_is_owner_only(client):
    """"What am I currently presenting as" is exactly the question a stranger
    must not be able to ask about somebody else."""
    me = make_profile(client)
    # Somebody else's real owner token, not a garbage string — a forged token
    # is turned away by the parser and proves nothing about whether this
    # surface checks *which* owner is asking.
    other = make_profile(client, owner_id="owner-2", display_name="Rae")
    theirs = auth_header(other)
    assert client.get(f"/dock/{me['id']}", headers=theirs).status_code == 403
    assert client.put(f"/dock/{me['id']}", json={"state": "open"},
                      headers=theirs).status_code == 403
    assert client.get(f"/dock/{me['id']}/face/identity",
                      headers=theirs).status_code == 403

    assert client.get(f"/dock/{me['id']}",
                      headers={"authorization": ""}).status_code == 401

    ok = auth_header(me)
    assert client.get(f"/dock/{me['id']}", headers=ok).status_code == 200


def test_the_named_routes_are_not_shadowed_by_a_profile_id(client):
    """`/dock/faces` and `/dock/where/x` are registered before
    `/dock/{profile_id}`; a profile whose id was "faces" must not capture
    them."""
    out = client.get("/dock/faces").json()
    assert "corners" in out and "profile_id" not in out


def test_moving_it_round_trips_over_http(client):
    me = make_profile(client)
    r = client.put(f"/dock/{me['id']}",
                   json={"corner": "bottom_left", "state": "open",
                         "face": "identity",
                         "faces": ["helper", "identity", "screens"]},
                   headers=auth_header(me))
    assert r.status_code == 200, r.text
    out = client.get(f"/dock/{me['id']}", headers=auth_header(me)).json()
    assert out["corner"] == "bottom_left" and out["face"] == "identity"

    on_air = client.get(f"/dock/{me['id']}?surface=live",
                        headers=auth_header(me)).json()
    assert on_air["tucked"] is True


def test_a_bad_corner_is_a_422_with_the_reason(client):
    me = make_profile(client)
    r = client.put(f"/dock/{me['id']}", json={"corner": "top_right"},
                   headers=auth_header(me))
    assert r.status_code == 422
    assert "bottom corner" in r.json()["detail"]


# -- the assistant pointing at things -----------------------------------------

def test_asking_where_something_is_gets_directions_not_a_description(client):
    """Somebody asking where a thing is has not asked what it is. A correct
    paragraph about backgrounds is the wrong reply."""
    out = client.post("/help",
                      json={"question": "where do I change my background"}).json()
    assert out["directions"]["lesson"] == "face"
    assert 124 in out["directions"]["screens"]
    assert "Your Background" in out["answer"] or "Your face" in out["answer"]


def test_directions_mention_the_pane_when_the_face_is_in_it(client):
    out = help_mod.where_is("where is the game lobby")
    assert out["lesson"] == "games"
    assert out["dock"]["face"] == "lobby"
    assert "corner" in out["say"]


def test_show_me_around_still_starts_the_tour_rather_than_pointing(client):
    """The walkthrough match runs before directions: "where do I start" is a
    request for the tour, not a request for a screen number."""
    out = client.post("/help", json={"question": "where do I start"}).json()
    assert out.get("walkthrough", {}).get("started") is True
    assert "directions" not in out


def test_directions_do_not_swallow_an_ordinary_question(client):
    out = client.post("/help", json={"question": "is this a real person"}).json()
    assert "directions" not in out
    assert "synthetic" in out["answer"].lower()


def test_asking_the_guide_to_be_somebody_is_still_refused_first(client):
    out = client.post("/help",
                      json={"question": "pretend you are my friend"}).json()
    assert out["refused"] is True
    assert "directions" not in out
