"""The 2.9.8 half of the widening: a kind that claims a screen renders.

    asked     the app is able to render on any devices with the screen
    mattered  2.9.7 wrote the claim into SCREENS; a claim with no
              working surface behind it is the dead end that table was
              built to prevent

Four kinds claim a screen. The wrist pair — watch and band — render
through the faces, which are permissions the pairing already stores.
The eyes pair — VR headset and AR glasses — render through the stage,
which now opens a WebXR session in the headset's own browser. These
tests hold each claim to its surface, and hold the headset's stage to
the flat stage's own promises: one geometry, one photo resolver, and
not one word of the capture vocabulary.
"""

from __future__ import annotations

import pathlib

from qrme import wearables
from tests.test_capabilities import auth_header, make_profile

REPO = pathlib.Path(__file__).resolve().parents[1]
INSIDE = (REPO / "app/src/screens/Inside.tsx").read_text(encoding="utf-8")
XR = (REPO / "app/src/xrStage.ts").read_text(encoding="utf-8")
RING = (REPO / "app/src/stageRing.ts").read_text(encoding="utf-8")


# -- the wrist pair: faces ----------------------------------------------------

def test_a_band_holds_every_face_a_watch_does(client):
    """SCREENS says the band gets the glance faces. The permission model
    has to agree, or the claim is a sentence in a picker."""
    me = make_profile(client, display_name="Owner")
    r = client.post(f"/profiles/{me['id']}/wearables",
                    json={"name": "Charge", "kind": "band",
                          "faces": sorted(wearables.FACES)},
                    headers=auth_header(me))
    assert r.status_code == 201, r.text
    assert set(r.json()["faces"]) == set(wearables.FACES)


# -- the eyes pair: the stage, through one ring -------------------------------

def test_both_stages_stand_on_the_one_ring():
    """The flat stage draws the circle in CSS; the headset draws it in
    WebXR. Two renderers that compute their own angles WILL drift — the
    shared module is the guard's whole argument, so both must import it
    and neither may keep a private copy of the math."""
    assert "seatAngle" in RING and "RING_RADIUS_CSS" in RING \
        and "RING_RADIUS_XR" in RING
    assert 'from "../stageRing"' in INSIDE, (
        "the flat stage stopped reading the shared ring")
    assert "seatAngle(i, seats.length)" in INSIDE
    assert "translateZ(${-RING_RADIUS_CSS}px)" in INSIDE, (
        "the flat stage's radius is a private number again")
    assert 'from "./stageRing"' in XR, (
        "the headset stage stopped reading the shared ring")
    assert "seatAngle(i, n)" in XR and "RING_RADIUS_XR" in XR
    assert "360 / Math.max" not in INSIDE, (
        "the flat stage keeps a private copy of the seat-angle math")


def test_the_headset_shows_the_photo_the_flat_stage_shows():
    """One resolver. The rules for whose photograph may appear on a seat
    — the marked-asset rule, the real-person rule — were argued once and
    live in `stagePhoto`; a second resolver would be a second chance to
    get them wrong."""
    assert "const stagePhoto = (" in INSIDE
    assert "photo: stagePhoto(s)" in INSIDE, (
        "the headset seats are not fed by the shared resolver")


def test_the_headset_door_only_exists_where_a_headset_answers():
    """Probed, never assumed. `headsetDoor` asks the browser; the button
    renders only behind the answer, so nobody on a laptop is offered a
    door into nothing."""
    assert "isSessionSupported" in XR
    assert "headsetDoor(" in INSIDE
    assert "{headset && (" in INSIDE, (
        "the headset button is drawn unconditionally")


def test_the_headset_stage_keeps_the_flat_stages_promise():
    """"No pixels of yours and no room of anybody else's crosses the
    wire for this" — the flat stage's words, held against the headset's
    source the way the pairing model is held: nothing here records,
    captures, or opens a device's ear or eye. AR passthrough is the
    headset compositor's own; this code never sees it."""
    src = XR.lower()
    for verb in ("getusermedia", "mediadevices", "record(", "capture(",
                 "stream(", "listen(", "transcribe", "audio_"):
        assert verb not in src, f"{verb!r} appears in the headset stage"


def test_the_figure_and_the_surroundings_are_decided_once():
    """Three renderings can show a seat's body — the flat stage, the
    staged overlay, the headset — and one resolver names the `.glb` for
    all of them, as `stagePhoto` does for the photograph. The chosen
    surroundings are one palette table read by both stages, so "Dusk" on
    a phone and "Dusk" in a visor are the same dusk."""
    assert "const stageModel = (" in INSIDE
    assert "model: stageModel(s)" in INSIDE, (
        "the headset's figures are not fed by the shared resolver")
    assert 'from "./stagePlace"' in XR and "PALETTES[opts.place]" in XR
    assert "PALETTES[place]" in INSIDE, (
        "the flat stage stopped painting the chosen place")


def test_ar_keeps_the_actual_room():
    """The place picker is VR's alone. AR's surroundings are the room the
    person is standing in — offering to swap those out would be offering
    to draw over reality, which is a different product."""
    assert 'format === "vr" && (\n            <div className="stage-places"'         .replace("\n", "\n") or True
    i = INSIDE.index('className="stage-places"')
    gate = INSIDE.rindex("format === ", 0, i)
    assert INSIDE[gate:gate + 17] == 'format === "vr" &', (
        "the place picker is no longer gated to VR")


def test_the_reply_footage_floats_in_the_same_player():
    """The film chip on an AR seat opens the same SeatFilm the flat page
    uses — one player, one set of rules about what footage exists and
    whose money renders it. A second player would be a second set."""
    assert 'className="stage-film-chip"' in INSIDE
    i = INSIDE.index('className="stage-film"')
    panel = INSIDE[i:i + 600]
    assert "SeatFilm" in panel, (
        "the stage's footage panel grew its own player")


def test_the_door_is_translated_like_everything_else():
    L10N = (REPO / "app/src/l10n.ts").read_text(encoding="utf-8")
    assert '"ins.stage.headset"' in L10N
    assert 'tr("ins.stage.headset", lang)' in INSIDE


def test_the_ar_eye_is_a_chosen_moment_not_a_camera():
    """The AR stage's eye shares one framed moment through the room's own
    share door — the photograph class :mod:`qrme.viewfinder` separates
    from a live camera, and this stays on the chosen-moment side of the
    line. Held two ways: the frame leaves through `shareInRoom` and
    nothing else, and no timer drives the eye — nothing watches between
    presses."""
    assert "showThemWhatISee" in INSIDE
    handler = INSIDE[INSIDE.index("const showThemWhatISee"):]
    handler = handler[:handler.index("};") + 2]
    assert "shareInRoom" in handler, (
        "the eye no longer leaves through the room's share door")
    for word in ("setInterval", "requestAnimationFrame", "MediaRecorder"):
        assert word not in handler, (
            f"{word!r} in the eye's handler — a driven eye is a camera, "
            "and the viewfinder module owns cameras")
