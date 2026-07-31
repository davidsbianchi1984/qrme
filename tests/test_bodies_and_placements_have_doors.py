"""Two surfaces the web console never had, and the traps in each.

The native shells already drove the robot catalogue, the binding and a command
button, so the routes that describe what a body has *become* — how it is
steered, what it has learned, what it has been told — had no caller anywhere.
Rated placement had no caller at all.

Both were built by driving the running server, and both turned up things a
route signature does not show. The ones guarded here are the ones where a
wrong screen would have looked completely correct:

* **three list-shaped things with almost the same name.** `robot.commands` is
  what the model of body accepts; `GET /robots/{id}/commands` is the audit log
  of what it was told; `GET /robots/{id}/skills` is installed task modules that
  *extend* the first list. A console that built its buttons from the log would
  typecheck and show an empty row of nothing;
* **the steering write takes `values`, not `dials`.** The request model has a
  default of `{}`, so a body keyed anything else is accepted, ignored, and
  answered `200` with the dials unchanged. There is no error to notice — the
  only way to see it is to read back what you wrote, which is what the first
  test here does;
* **`funnel.chat_rate` is null, not zero**, until something has got through the
  age wall. `(null).toFixed()` is not a crash in JavaScript, it is `0`, so a
  screen would quietly publish a conversion rate that does not exist;
* **the placement create and list shapes differ.** Create carries the urls and
  the QR path; list carries the counts and none of them;
* **taking a placement down deactivates the beacon rather than deleting it**,
  which is the entire safety property: a code already printed at a venue stops
  resolving instead of being reissued to point somewhere new.

And the venue note, which is the argument the whole feature rests on and the
one sentence here that must never be paraphrased.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()


def _paid_owner(client, account: str):
    p = client.post("/profiles", json={
        "owner_id": account, "kind": "fictional", "display_name": "Anchor",
        "purpose": "companion_coach", "persona": "p",
        "verification": {"birthdate": "1990-01-01"},
    }).json()
    token = p["owner_token"]
    client.post(f"/memberships/{account}", json={"plan": "pro"},
                headers={"authorization": f"Bearer {token}"})
    return p, token


def _robot(client, account="acct_body"):
    p, token = _paid_owner(client, account)
    head = {"authorization": f"Bearer {token}"}
    r = client.post(f"/profiles/{p['id']}/robots",
                    json={"name": "Helper", "model": "u1_ultra"}, headers=head)
    assert r.status_code == 201, r.text
    return r.json(), head


def _adult(client, account="acct_rated"):
    _, anchor = _paid_owner(client, account)
    a = client.post("/profiles", json={
        "owner_id": account, "kind": "fictional", "display_name": "Nocturne",
        "purpose": "creator_persona", "persona": "p", "adult_mode": True,
        "verification": {"birthdate": "1990-01-01"},
    }).json()
    assert a.get("adult_mode"), a
    return a, {"authorization": f"Bearer {a['owner_token']}"}


# --- bodies -----------------------------------------------------------------

def test_the_steering_write_reads_back(client):
    """The trap with no error.

    `SteeringSet` is `{values: dict}` with a default of `{}`. A body keyed
    `dials` — which is what the *read* calls the catalogue, so it is the
    obvious guess — is accepted, ignored, and answered 200. The dials are
    unchanged and nothing says so. Writing then reading is the only way to
    know, so that is what this asserts.
    """
    robot, head = _robot(client, "acct_steer")
    r = client.put(f"/robots/{robot['id']}/steering",
                   json={"values": {"autonomy": 20, "pace": 80}}, headers=head)
    assert r.status_code == 200, r.text
    assert r.json()["values"]["autonomy"] == 20, (
        "the steering write no longer takes effect, and still answers 200")
    assert client.get(f"/robots/{robot['id']}/steering",
                      headers=head).json()["values"]["pace"] == 80


def test_a_dial_is_clamped_rather_than_refused(client):
    robot, head = _robot(client, "acct_clamp")
    r = client.put(f"/robots/{robot['id']}/steering",
                   json={"values": {"autonomy": 900}}, headers=head).json()
    assert r["values"]["autonomy"] == 100


def test_intimacy_is_never_a_body_dial(client):
    """A body is steered on pace, autonomy and manner. The 18+ dial belongs to
    a persona and is dropped here — asserted rather than assumed, because a
    console offering it would be offering something the server discards."""
    robot, head = _robot(client, "acct_intim")
    got = client.get(f"/robots/{robot['id']}/steering", headers=head).json()
    assert not [d for d in got["dials"] if d["group"] == "intimacy"]
    after = client.put(f"/robots/{robot['id']}/steering",
                       json={"values": {"intimacy": 90}}, headers=head).json()
    assert after["values"].get("intimacy", 0) == 0


def test_the_dials_become_something_a_body_does(client):
    """`behavior_profile` is the derived half — what the dials actually mean
    to a machine that moves. It is the difference between a slider and an
    explanation, and the screen draws it beside them."""
    robot, head = _robot(client, "acct_derive")
    r = client.put(f"/robots/{robot['id']}/steering",
                   json={"values": {"pace": 90, "autonomy": 10}},
                   headers=head).json()
    assert r["behavior_profile"]["motion_eagerness"] == 90
    assert r["behavior_profile"]["initiative"] == 10


def test_the_three_lists_stay_three_different_things(client):
    """The naming trap, asserted as a shape.

    If `GET /commands` ever started returning the allowlist, a console built
    on it would look right and silently stop being an audit log.
    """
    robot, head = _robot(client, "acct_lists")
    rid = robot["id"]
    assert robot["commands"], "the body accepts nothing at all"
    assert client.get(f"/robots/{rid}/commands", headers=head).json() == [], (
        "the command log is pre-populated — it is a history, not a menu")
    assert client.get(f"/robots/{rid}/skills", headers=head).json() == []

    client.post(f"/robots/{rid}/command", json={"command": "tidy"},
                headers=head)
    log = client.get(f"/robots/{rid}/commands", headers=head).json()
    assert len(log) == 1 and log[0]["command"] == "tidy"
    # And the menu did not grow because something was done.
    assert client.get(f"/profiles/{robot['profile_id']}/robots",
                      headers=head).json()[0]["commands"] == robot["commands"]


def test_a_command_the_body_cannot_do_is_refused_by_name(client):
    """The refusal lists what *is* allowed, which is why the screen can show a
    row of buttons rather than a text box and a shrug."""
    robot, head = _robot(client, "acct_refuse")
    r = client.post(f"/robots/{robot['id']}/command",
                    json={"command": "dance"}, headers=head)
    assert r.status_code == 422
    assert "allowed" in r.json()["detail"]


def test_unbinding_says_it_unbound_rather_than_deleted(client):
    robot, head = _robot(client, "acct_unbind")
    r = client.delete(f"/robots/{robot['id']}", headers=head).json()
    assert r["unbound"] is True


# --- placements -------------------------------------------------------------

def test_every_venue_carries_the_sentence_the_feature_rests_on(client):
    """The wall does not move to the venue.

    Advertising a rated profile on somebody else's platform is only defensible
    because the age check stays here. Every venue carries that sentence, the
    screen renders it verbatim, and a paraphrase would drop the load-bearing
    half — *regardless of where the QR or handle was found*.
    """
    venues = client.get("/venues").json()
    assert venues, "no venues at all"
    for v in venues:
        assert v["age_wall"] is True
        assert "regardless of where" in v["note"], (
            f"{v['key']} no longer says the wall holds wherever the code was "
            "found — which is the only reason this feature is defensible")


def test_only_an_adult_mode_profile_is_placed(client):
    p, token = _paid_owner(client, "acct_notadult")
    r = client.post(f"/profiles/{p['id']}/placements",
                    json={"venue": "onlyfans"},
                    headers={"authorization": f"Bearer {token}"})
    assert r.status_code == 422
    assert "adult-mode" in r.json()["detail"]


def test_the_created_placement_carries_both_urls_and_they_differ(client):
    """`summon_url` is the JSON surface clients read; `scan_url` is where a
    phone camera lands and what the printed code encodes. Publishing the
    wrong one hands somebody a page of JSON, so the screen labels them and
    this keeps them distinguishable."""
    a, head = _adult(client, "acct_urls")
    made = client.post(f"/profiles/{a['id']}/placements",
                       json={"venue": "onlyfans"}, headers=head).json()
    assert made["scan_url"] != made["summon_url"]
    assert made["qr_svg"].startswith("/beacons/")
    for field in ("placement_id", "venue", "beacon_id", "rated", "note"):
        assert field in made


def test_the_list_is_a_different_shape_from_the_create(client):
    """Stated rather than discovered later: the list carries the counts and
    none of the urls, so a screen has to derive what it shows."""
    a, head = _adult(client, "acct_shapes")
    client.post(f"/profiles/{a['id']}/placements", json={"venue": "fansly"},
                headers=head)
    row = client.get(f"/profiles/{a['id']}/placements", headers=head).json()[0]
    assert {"id", "venue_name", "beacon_id", "scans", "active"} <= set(row)
    assert "scan_url" not in row and "qr_svg" not in row


def test_the_conversion_rate_is_absent_rather_than_zero(client):
    """`chat_rate` is null until something has got through the wall.

    In JavaScript `Number(null).toFixed(0)` is `"0"`, so a screen that did not
    check would publish a 0% conversion that has not been measured. The
    difference between "nobody converts" and "nothing has happened yet" is
    the whole point of an analytics screen.
    """
    a, head = _adult(client, "acct_funnel")
    client.post(f"/profiles/{a['id']}/placements", json={"venue": "onlyfans"},
                headers=head)
    funnel = client.get(f"/profiles/{a['id']}/placements/analytics",
                        headers=head).json()["funnel"]
    assert funnel["chat_rate"] is None, (
        "the funnel now reports a rate with nothing behind it")


def test_the_analytics_split_walled_from_verified(client):
    a, head = _adult(client, "acct_split")
    made = client.post(f"/profiles/{a['id']}/placements",
                       json={"venue": "onlyfans"}, headers=head).json()
    client.get(f"/summon?ref={made['beacon_id']}")
    v = client.get(f"/profiles/{a['id']}/placements/analytics",
                   headers=head).json()["venues"][0]
    assert v["scans"] == 1
    assert v["walled"] + v["verified"] == v["scans"], (
        "a resolution that is neither walled nor verified — the screen shows "
        "these as the two halves of one number")


def test_taking_a_placement_down_kills_the_printed_code(client):
    """The safety property, and the reason the screen says it before you
    press: a QR already at a venue stops resolving rather than being reissued
    to point somewhere new."""
    a, head = _adult(client, "acct_takedown")
    made = client.post(f"/profiles/{a['id']}/placements",
                       json={"venue": "onlyfans"}, headers=head).json()
    r = client.delete(f"/placements/{made['placement_id']}",
                      headers=head).json()
    assert r["removed"] is True
    assert r["beacon_active"] is False
    assert client.get(f"/summon?ref={made['beacon_id']}").status_code == 410


def test_the_custody_refusal_is_a_sentence_a_screen_can_show(client):
    """No vault configured is a posture, not a failure. The screen reports it
    rather than showing a red error, so it has to arrive as prose."""
    a, head = _adult(client, "acct_custody")
    r = client.get(f"/profiles/{a['id']}/placements/custody", headers=head)
    if r.status_code == 409:
        assert isinstance(r.json()["detail"], str) and r.json()["detail"]


# --- the console half -------------------------------------------------------

def _src(rel: str) -> str:
    return (REPO / rel).read_text(encoding="utf-8")


@pytest.mark.parametrize("screen", ["Robots", "Placements"])
def test_the_screen_exists(screen):
    assert (REPO / f"app/src/screens/{screen}.tsx").exists()


@pytest.mark.parametrize("binding", [
    "api.robotCatalogue(", "api.robots(", "api.bindRobot(", "api.unbindRobot(",
    "api.commandRobot(", "api.robotCommandLog(", "api.robotSkills(",
    "api.robotSteering(", "api.setRobotSteering(",
])
def test_the_bodies_screen_calls_it(binding):
    assert binding in _src("app/src/screens/Robots.tsx")


@pytest.mark.parametrize("binding", [
    "api.venues(", "api.placements(", "api.placeAtVenue(",
    "api.placementAnalytics(", "api.placementCustody(", "api.removePlacement(",
])
def test_the_placement_screen_calls_it(binding):
    assert binding in _src("app/src/screens/Placements.tsx")


def test_the_steering_write_sends_values():
    """The console half of the silent-ignore trap. `{dials: …}` would be
    accepted and do nothing, and no runtime test here would fail."""
    api = _src("app/src/api.ts")
    m = re.search(r"setRobotSteering:.*?\n\s*req<RobotSteeringSet>.*?\}\),",
                  api, re.S)
    assert m, "setRobotSteering is gone"
    assert "body: { values }" in m.group(0), (
        "the steering write no longer sends `values` — the server would "
        "accept the request, change nothing, and answer 200")


def test_the_placement_screen_checks_the_null_rate():
    """`(null).toFixed()` is `0` in JavaScript, not an error, so nothing else
    would catch a screen publishing a rate that was never measured."""
    src = _src("app/src/screens/Placements.tsx")
    assert "chat_rate === null" in src, (
        "the screen no longer distinguishes 'no rate yet' from 0%")


def test_the_venue_note_is_rendered_and_not_retyped():
    """Rendered from the payload. A hand-written 18+ line in the console is a
    second copy of an argument that is maintained in one place."""
    src = _src("app/src/screens/Placements.tsx")
    assert "{v.note}" in src
    # Comments are stripped first: the docstring quotes the sentence on
    # purpose, to say why it is never retyped. It is markup that must not
    # contain a second copy, not the file.
    markup = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    markup = re.sub(r"^\s*//.*$", "", markup, flags=re.M)
    assert "regardless of where" not in markup, (
        "the venue sentence has been copied into the console; render "
        "`v.note` instead so there is one copy of it")
