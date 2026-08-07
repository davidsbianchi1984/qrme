"""Wearing a character over your own camera.

The feature is ordinary — a mask, a creature, a replaced background — and it
lands directly on the argument everything else in this codebase is built from:
a synthetic thing must say so. An overlay is synthetic media composited onto a
real human face in real time, and the fact that the person underneath agreed
does not change what the *viewer* is looking at.

So the tests that matter are not about the catalogue. They are the refusals,
and the disclosures that have to distinguish three different claims: a face
replaced, a face untouched, and a real face in a room that was generated.

The live desk is the case that changed. It was refused outright at first, on
reasoning that turned out to conflate *this face is unmodified* with *a real
person is behind this*. Only the second is what the badge ever claimed, and a
costume does not make it false.
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
                            "title": "A library", "source": "own"},
                      headers=_as(sam["token"])).json()
    assert out["covers_face"] is False
    assert "their own face, unaltered" in out["disclosure"]
    assert "not their face" not in out["disclosure"]


# -- the three refusals -------------------------------------------------------

def _desk(client, owner):
    now = db.utcnow()
    did = db.new_id("desk")
    db.connect().execute(
        "INSERT INTO desks (id, owner_id, display_name, trade, attestor,"
        " attestation_basis, attested_at, created_at, last_seen)"
        " VALUES (?,?,?,?,?,?,?,?,?)",
        (did, owner["id"], "Sam's desk", "locksmith", "Sam",
         "self-attested", now, now, now))
    db.connect().commit()
    return did


def test_a_live_desk_wears_one_and_keeps_its_badge(client):
    """The refusal here was wrong twice over.

    First it conflated *this face is unmodified* with *a real person is behind
    this* — only the second is what the badge ever claimed, and a costume is
    not a synthesis. Then the fix over-corrected, composing the badge with the
    costume, which answered a question nobody had.
    """
    sam = _interactor(client)
    did = _desk(client, sam)
    r = client.post(f"/places/desk/{did}/overlay",
                    json={"interactor_id": sam["id"], "kind": "mask",
                          "title": "The Wolf"}, headers=_as(sam["token"]))
    assert r.status_code == 201, r.text

    mark = client.get(f"/desks/{did}/live-person").json()
    assert mark["real_person"] is True
    assert mark["line"] == overlays.LIVE_MARK
    assert mark["burned"] is True


def test_the_mark_never_mentions_the_costume(client):
    """A viewer is on a **named account's** live or room — the handle is at the
    top left and they chose it to get there. The open question on that page is
    never *is that his real nose*, it is *is there a person here at all*, and
    that is the only thing this mark answers.

    It also removes a quiet penalty: somebody covering their face because of
    dysmorphia, or because their work makes showing it unsafe, was being handed
    a badge that announced the fact on every frame while the person beside them
    got a clean one.
    """
    sam = _interactor(client)
    did = _desk(client, sam)

    bare = client.get(f"/desks/{did}/live-person").json()["line"]
    client.post(f"/places/desk/{did}/overlay",
                json={"interactor_id": sam["id"], "kind": "character",
                      "title": "Corvid"}, headers=_as(sam["token"]))
    masked = client.get(f"/desks/{did}/live-person").json()

    assert masked["line"] == bare == overlays.LIVE_MARK
    assert "Corvid" not in str(masked)
    assert "NOT AI" in masked["line"] and "REAL PERSON" in masked["line"]


def test_the_whole_facial_catalogue_is_available(client):
    """Named as a need rather than a nicety: somebody with dysmorphia has to be
    able to appear without appearing. One mask and a shrug is not that."""
    p = make_profile(client)
    sam = _interactor(client)
    rid = _room(client, p, sam)

    assert len(overlays.FACE_KINDS) >= 15
    for kind in ("obscured", "silhouette", "avatar_2d", "avatar_3d",
                 "stylised", "prosthetic", "half_mask"):
        assert kind in overlays.FACE_KINDS
        r = client.post(f"/places/room/{rid}/overlay",
                        json={"interactor_id": sam["id"], "kind": kind,
                              "title": kind.replace("_", " ")},
                        headers=_as(sam["token"]))
        assert r.status_code == 201, f"{kind}: {r.text}"


def test_the_mark_is_bound_to_the_account_that_owns_the_stream(client):
    """Issued against the desk, never asserted by a client — the same reason
    the AI mark is burned into a portrait rather than composited by whoever
    happens to be rendering it. A stream that never earned it cannot paste it
    on."""
    sam = _interactor(client)
    did = _desk(client, sam)
    mark = client.get(f"/desks/{did}/live-person").json()
    assert mark["owner_id"] == sam["id"]
    assert mark["attestor"] == "Sam"
    assert client.get("/desks/dsk_nothing/live-person").status_code == 404


def test_only_the_desks_owner_puts_a_face_on_its_stream(client):
    sam = _interactor(client)
    other = _interactor(client, "Nosy")
    did = _desk(client, sam)
    r = client.post(f"/places/desk/{did}/overlay",
                    json={"interactor_id": other["id"], "kind": "mask",
                          "title": "Anything"}, headers=_as(other["token"]))
    assert r.status_code == 403


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
    refused = {r["kind"]: r["why"] for r in out["refusals"]}
    for expected in ("real_person", "public_figure", "another_user",
                     "age_shift", "badge_mimic"):
        assert expected in refused and refused[expected]
    # Nowhere is forbidden any more — the desk came off this list, and the
    # machinery stays for the next surface that genuinely cannot disclose.
    assert out["never"] == []
    assert "desk" in {s["surface"] for s in out["surfaces"]}


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


# -- backgrounds --------------------------------------------------------------

def test_a_generated_background_says_so_even_though_you_are_real(client):
    """An AI-generated background **is** synthetic media, and the person in
    front of it being real does not make the room real. The order is
    deliberate: the person first, because that is what a viewer is deciding
    about; the room second, because that is the part that was made."""
    p = make_profile(client)
    sam = _interactor(client)
    rid = _room(client, p, sam)
    out = client.post(f"/places/room/{rid}/overlay",
                      json={"interactor_id": sam["id"], "kind": "backdrop",
                            "title": "a quiet library", "source": "generated"},
                      headers=_as(sam["token"])).json()
    assert out["background_generated"] is True
    assert "their own face, unaltered" in out["disclosure"]
    assert "AI-generated" in out["disclosure"]


def test_your_own_photo_is_not_called_generated(client):
    """A disclosure that cries wolf is one people learn to skip."""
    p = make_profile(client)
    sam = _interactor(client)
    rid = _room(client, p, sam)
    out = client.post(f"/places/room/{rid}/overlay",
                      json={"interactor_id": sam["id"], "kind": "backdrop",
                            "title": "my kitchen", "source": "own"},
                      headers=_as(sam["token"])).json()
    assert out["background_generated"] is False
    assert "AI-generated" not in out["disclosure"]


def test_a_background_must_say_where_it_came_from(client):
    """Silently recording a generated scene as somebody's own room is exactly
    the disclosure this feature exists to make."""
    p = make_profile(client)
    sam = _interactor(client)
    rid = _room(client, p, sam)
    r = client.post(f"/places/room/{rid}/overlay",
                    json={"interactor_id": sam["id"], "kind": "backdrop",
                          "title": "somewhere"}, headers=_as(sam["token"]))
    assert r.status_code == 422
    assert "where the background came from" in r.json()["detail"]


def test_an_imported_image_needs_the_rights_to_it(client):
    """Asked, not guessed — nothing here can look at an image and know who
    owns it, so the one answer with an obvious consequence is the one that is
    enforced."""
    p = make_profile(client)
    sam = _interactor(client)
    rid = _room(client, p, sam)
    r = client.post(f"/places/room/{rid}/overlay",
                    json={"interactor_id": sam["id"], "kind": "backdrop",
                          "title": "a film still", "source": "imported",
                          "holds_rights": False}, headers=_as(sam["token"]))
    assert r.status_code == 422
    assert "rights" in r.json()["detail"]


def test_a_mask_has_no_background_to_describe(client):
    """`source` says what happened to the room. A face-covering overlay does
    not have one, and accepting the field there would record a claim about
    something that is not in the picture."""
    p = make_profile(client)
    sam = _interactor(client)
    rid = _room(client, p, sam)
    r = client.post(f"/places/room/{rid}/overlay",
                    json={"interactor_id": sam["id"], "kind": "mask",
                          "title": "Blue Fox", "source": "generated"},
                    headers=_as(sam["token"]))
    assert r.status_code == 422
    assert "does not have a background" in r.json()["detail"]


def test_the_catalogue_lists_where_a_background_can_come_from(client):
    out = client.get("/overlays/catalogue").json()
    sources = {b["source"]: b["synthetic"] for b in out["backgrounds"]}
    assert sources == {"own": False, "imported": False,
                       "generated": True, "blur": False}
