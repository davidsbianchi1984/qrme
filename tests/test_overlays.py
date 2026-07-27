"""Wearing a character over your own camera.

The feature is ordinary — a mask, a creature, a replaced background — and it
lands directly on the argument everything else in this codebase is built from:
a synthetic thing must say so. An overlay is synthetic media composited onto a
real human face in real time, and the fact that the person underneath agreed
does not change what the *viewer* is looking at.

So the tests that matter are not about the catalogue. They are the three
refusals, and the live desk is the sharpest of them.
"""

import pytest

from qrme import db, overlays
from tests.test_capabilities import auth_header, make_profile


def _interactor(client, name="Sam"):
    r = client.post("/interactors", json={"display_name": name,
                                          "birthdate": "1990-01-01"})
    assert r.status_code == 201, r.text
    return r.json()


def _as(token):
    return {"authorization": f"Bearer {token}"}


def _room(client, profile, *users, channel="video"):
    body = {"topic": "the read-through", "channel": channel,
            "participants": [{"kind": "profile", "id": profile["id"]}]
            + [{"kind": "user", "id": u["id"]} for u in users]}
    r = client.post("/rooms", json=body)
    assert r.status_code == 201, r.text
    return r.json()["id"]


# -- wearing one --------------------------------------------------------------

def test_you_can_wear_a_character_over_your_own_camera(client):
    p = make_profile(client)
    sam = _interactor(client)
    rid = _room(client, p, sam)

    r = client.post(f"/places/room/{rid}/overlay",
                    json={"interactor_id": sam["id"], "kind": "creature",
                          "title": "Blue Fox"}, headers=_as(sam["token"]))
    assert r.status_code == 201, r.text
    assert r.json()["wearing"] is True


def test_everyone_present_is_told_what_they_are_looking_at(client):
    """The disclosure is why the feature is allowed to exist, so it is
    addressed to the people it is about — the ones looking at the face."""
    p = make_profile(client)
    sam = _interactor(client, "Sam")
    mal = _interactor(client, "Mal")
    rid = _room(client, p, sam, mal)
    client.post(f"/places/room/{rid}/overlay",
                json={"interactor_id": sam["id"], "kind": "character",
                      "title": "The Bailiff"}, headers=_as(sam["token"]))

    seen = client.get(f"/places/room/{rid}/overlay",
                      headers=_as(mal["token"])).json()
    assert [o["interactor_id"] for o in seen["overlays"]] == [sam["id"]]
    assert "not their face" in seen["overlays"][0]["disclosure"]
    assert "real person is underneath" in seen["overlays"][0]["disclosure"]


def test_a_background_is_not_disclosed_as_a_replaced_face(client):
    """A disclosure that cries wolf is one people learn to skip. Saying "this
    is not their face" over a blurred background is a lie in the other
    direction from the one the mark exists to prevent."""
    p = make_profile(client)
    sam = _interactor(client)
    rid = _room(client, p, sam)
    out = client.post(f"/places/room/{rid}/overlay",
                      json={"interactor_id": sam["id"], "kind": "backdrop",
                            "title": "A library"},
                      headers=_as(sam["token"])).json()
    assert out["covers_face"] is False
    assert "their own face, unaltered" in out["disclosure"]
    assert "not their face" not in out["disclosure"]


# -- the three refusals -------------------------------------------------------

def test_a_live_desk_can_never_wear_one(client):
    """The sharp case.

    A desk's badge reads "Live person — not AI" and its whole premise is that
    a real human is behind it — the badge is *inverted* precisely because
    there is a person there. Put a character over that face and the badge
    becomes a false statement, made by the platform, on the one surface whose
    entire value is that the statement is true. The overlay is refused rather
    than the badge weakened, because a desk that cannot promise a real person
    is not a desk.
    """
    from qrme import desks
    assert desks.DESIGNATION == "Live person — not AI"

    with pytest.raises(overlays.OverlayError) as exc:
        overlays.wear("usr_1", "desk", "dsk_1", "mask", "Anything")
    assert "Live person — not AI" in str(exc.value)

    sam = _interactor(client)
    r = client.post("/places/desk/dsk_1/overlay",
                    json={"interactor_id": sam["id"], "kind": "mask",
                          "title": "Anything"}, headers=_as(sam["token"]))
    assert r.status_code == 422
    assert "false statement" in r.json()["detail"]


def test_no_overlay_may_depict_a_real_person(client):
    """A live-driven likeness of somebody who is not in the room is the exact
    artefact this codebase argues against, and "it was only a filter" is how
    it would arrive."""
    p = make_profile(client)
    sam = _interactor(client)
    rid = _room(client, p, sam)
    r = client.post(f"/places/room/{rid}/overlay",
                    json={"interactor_id": sam["id"], "kind": "character",
                          "title": "Someone real",
                          "depicts_real_person": True},
                    headers=_as(sam["token"]))
    assert r.status_code == 422
    assert "argue against" in r.json()["detail"]


def test_the_refused_classes_are_named_with_their_reasons(client):
    """An absent option reads as a gap somebody files a bug about, or works
    around. Every one of these is a decision, so it is published as one."""
    out = client.get("/overlays/catalogue").json()
    refused = {r["kind"]: r["why"] for r in out["refused"]}
    for expected in ("real_person", "public_figure", "another_user",
                     "age_shift", "badge_mimic"):
        assert expected in refused and refused[expected]
    assert out["never"][0]["surface"] == "desk"


def test_an_age_shifting_overlay_is_refused_by_name(client):
    """It defeats the only check standing between an adult and a child."""
    p = make_profile(client)
    sam = _interactor(client)
    rid = _room(client, p, sam)
    r = client.post(f"/places/room/{rid}/overlay",
                    json={"interactor_id": sam["id"], "kind": "age_shift",
                          "title": "Younger"}, headers=_as(sam["token"]))
    assert r.status_code == 422
    assert "defeats the only check" in r.json()["detail"]


def test_a_badge_cannot_be_drawn_into_the_picture(client):
    """Forging the AI mark, the verified mark or a live-desk badge in pixels
    counterfeits the one thing a viewer is supposed to be able to rely on."""
    p = make_profile(client)
    sam = _interactor(client)
    rid = _room(client, p, sam)
    r = client.post(f"/places/room/{rid}/overlay",
                    json={"interactor_id": sam["id"], "kind": "badge_mimic",
                          "title": "Verified-looking"},
                    headers=_as(sam["token"]))
    assert r.status_code == 422


# -- whose face it is ---------------------------------------------------------

def test_nobody_can_put_an_overlay_on_you(client):
    """An overlay somebody else can apply is not a costume, it is a puppet —
    and the person whose face is underneath is the one whose consent counts."""
    p = make_profile(client)
    sam = _interactor(client, "Sam")
    mal = _interactor(client, "Mal")
    rid = _room(client, p, sam, mal)
    r = client.post(f"/places/room/{rid}/overlay",
                    json={"interactor_id": sam["id"], "kind": "mask",
                          "title": "Something"}, headers=_as(mal["token"]))
    assert r.status_code == 403


def test_an_outsider_cannot_see_who_is_wearing_what(client):
    p = make_profile(client)
    sam = _interactor(client, "Sam")
    outsider = _interactor(client, "Nosy")
    rid = _room(client, p, sam)
    assert client.get(f"/places/room/{rid}/overlay",
                      headers={"authorization": ""}).status_code == 401
    assert client.get(f"/places/room/{rid}/overlay",
                      headers=_as(outsider["token"])).status_code == 403


def test_you_take_your_own_off(client):
    p = make_profile(client)
    sam = _interactor(client)
    rid = _room(client, p, sam)
    client.post(f"/places/room/{rid}/overlay",
                json={"interactor_id": sam["id"], "kind": "puppet",
                      "title": "Tin Man"}, headers=_as(sam["token"]))
    out = client.request("DELETE", f"/places/room/{rid}/overlay",
                         json={"interactor_id": sam["id"]},
                         headers=_as(sam["token"])).json()
    assert out["wearing"] is False
    assert client.get(f"/places/room/{rid}/overlay",
                      headers=_as(sam["token"])).json()["overlays"] == []


def test_wearing_a_second_one_replaces_the_first(client):
    """Two faces at once is not a state anybody can render, and a stack would
    make the disclosure ambiguous about which one is being shown."""
    p = make_profile(client)
    sam = _interactor(client)
    rid = _room(client, p, sam)
    client.post(f"/places/room/{rid}/overlay",
                json={"interactor_id": sam["id"], "kind": "mask",
                      "title": "First"}, headers=_as(sam["token"]))
    client.post(f"/places/room/{rid}/overlay",
                json={"interactor_id": sam["id"], "kind": "creature",
                      "title": "Second"}, headers=_as(sam["token"]))
    seen = client.get(f"/places/room/{rid}/overlay",
                      headers=_as(sam["token"])).json()["overlays"]
    assert len(seen) == 1 and seen[0]["title"] == "Second"


def test_it_comes_off_when_the_place_ends(client):
    """A disguise must not outlive the conversation it was worn in."""
    p = make_profile(client)
    sam = _interactor(client)
    rid = _room(client, p, sam)
    client.post(f"/places/room/{rid}/overlay",
                json={"interactor_id": sam["id"], "kind": "mask",
                      "title": "Gone soon"}, headers=_as(sam["token"]))
    assert overlays.close_place("room", rid) == 1
    assert overlays.worn("room", rid)["overlays"] == []


def test_the_record_survives_the_overlay_coming_off(client):
    """A viewer who saw a face and later wants to know what they were actually
    looking at should have an answer — so removal stamps a time rather than
    deleting the row."""
    p = make_profile(client)
    sam = _interactor(client)
    rid = _room(client, p, sam)
    out = client.post(f"/places/room/{rid}/overlay",
                      json={"interactor_id": sam["id"], "kind": "mask",
                            "title": "Was here"},
                      headers=_as(sam["token"])).json()
    client.request("DELETE", f"/places/room/{rid}/overlay",
                   json={"interactor_id": sam["id"]}, headers=_as(sam["token"]))
    row = db.connect().execute("SELECT * FROM overlays WHERE id=?",
                               (out["id"],)).fetchone()
    assert row is not None and row["removed_at"] is not None
    assert row["title"] == "Was here"
