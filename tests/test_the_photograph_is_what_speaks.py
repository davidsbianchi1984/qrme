"""The face that speaks is the photograph, not a head built to replace it.

## The finding

The forge built a head from MediaPipe's 478 face landmarks. A landmark
set is a face region — no skull, no hair, no ears, no neck — so the mesh
is a shield-shaped patch, and however well it is textured and lit it can
only ever be a mask. The field looked at one and said it exactly:

    "That isn't the photo I uploaded, that just seems like a white
     moving skeleton frame that goes behind the image."

That is a correct description of a landmark mesh, and the two real bugs
underneath it — a texture labelled `image/png` that was a JPEG, and
lighting that multiplied the skin past white — were fixed and still left
a mask.

    asked     let the avatar speak
    mattered  let it still be them while it does

So nothing is rebuilt any more. The forge *measures* the picture; the
console lays that mesh over the photograph it already has, with the
picture as its own texture at the places it was measured. At rest the
mesh is a copy of the picture over the picture and cannot be seen. The
only thing that ever moves is a mouth.

Both doors stay — `/forge` still builds a head for anybody who wants
one — but only one of them is put in front of a person.
"""

from __future__ import annotations

import re
from pathlib import Path


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()
FORGE = (REPO / "docker" / "forge" / "facebuild.py").read_text(encoding="utf-8")
SERVER = (REPO / "docker" / "forge" / "server.py").read_text(encoding="utf-8")
CLIENT = (REPO / "qrme" / "avatarforge.py").read_text(encoding="utf-8")
RENDER = (REPO / "app" / "src" / "SpeakingPortrait.tsx").read_text(
    encoding="utf-8")
STAGE = (REPO / "app" / "src" / "AvatarStage.tsx").read_text(encoding="utf-8")
IDENTITY = (REPO / "app" / "src" / "screens" / "Identity.tsx").read_text(
    encoding="utf-8")


# --------------------------------------------------------------------------
# The measurement


def test_the_forge_can_measure_without_building(client):
    assert "def build_speaking(" in FORGE
    assert '@app.post("/speak")' in SERVER


def test_the_photograph_does_not_come_back(client):
    """It is already on the profile. A second copy of somebody's face
    travelling for no reason is a cost with no benefit attached."""
    body = FORGE.split("def build_speaking(")[1].split("\ndef ")[0]
    # Not `^`-anchored: two of them share a line, and a guard that reads
    # only the first key on each line is a guard with a blind spot.
    keys = set(re.findall(r'"(\w+)":\s', body))
    assert keys == {"points", "triangles", "shapes", "mouth",
                    "width", "height"}, keys


def test_the_mouth_moves_in_the_picture_plane(client):
    """`_morphs` moves a head in a scene, where y counts upward and there
    is depth. There is no depth in a photograph, and inventing one is how
    the mask got built."""
    body = FORGE.split("def _plane_shapes(")[1].split("\ndef ")[0]
    assert "jawOpen" in body and "mouthPucker" in body
    # Two numbers per point, not three. A z here would be a mask coming
    # back through the door it was shown out of.
    assert re.search(r"jaw\.append\(\[int\(index\), 0\.0, ", body)


def test_only_the_mouth_is_ever_moved(client):
    """Everything that is not a mouth is never touched — which is the
    whole reason the person on screen goes on being the person."""
    body = FORGE.split("def _plane_shapes(")[1].split("\ndef ")[0]
    for group in ("_LOWER_LIP", "_JAW", "_MOUTH"):
        assert group in body
    for elsewhere in ("_LEFT_UPPER_LID", "_RIGHT_UPPER_LID"):
        assert elsewhere not in body, (
            f"{elsewhere} is being moved on a photograph — a blink drawn "
            "by displacing a picture of an open eye is a smear")


# --------------------------------------------------------------------------
# The road through the stack


def test_the_client_has_a_measuring_door(client):
    assert "def speech_map(" in CLIENT
    body = CLIENT.split("def speech_map(")[1]
    assert '/speak' in body
    # Same gate as every other outbound path, named on somebody's behalf.
    assert "offline.allow(forge_url()" in body


def test_the_measurement_rides_the_same_record_as_the_face(client,
                                                           profile_id):
    """One record, one likeness, one provenance. A speaking face is the
    same face — not a second identity for the same person."""
    route = (REPO / "qrme" / "routers" / "avatars.py").read_text()
    body = route.split("def speaking_face(")[1].split("\n@router")[0]
    assert 'set_variant(row["id"], "speaking"' in body
    assert 'likeness="self"' in body
    assert "avatarreg.claim(" in body


def test_a_retired_face_stops_speaking(client):
    """The measurement follows the portrait out, exactly as the model
    does — a takedown that left the mouth behind would be a takedown of
    the picture only."""
    avatars = (REPO / "qrme" / "avatars.py").read_text()
    body = avatars.split("def speaking_of(")[1].split("\ndef ")[0]
    assert 'got["status"] != "active"' in body
    assert "return None" in body


def test_an_anonymous_profile_does_not_ship_its_face_map(client):
    """Where somebody's face sits in their own picture is a picture of
    somebody — withheld for the same reason the torso and the model
    are."""
    avatars = (REPO / "qrme" / "avatars.py").read_text()
    assert '"speaking": None if anonymous else speaking_of(profile_id),' \
        in avatars


# --------------------------------------------------------------------------
# What is drawn


def test_the_mesh_is_flat_and_wears_the_picture(client):
    """Its texture coordinates ARE its positions, so at rest it is a copy
    of the picture laid over the picture and cannot be seen."""
    assert "OrthographicCamera" in RENDER, "a perspective on a photograph"
    assert "MeshBasicMaterial" in RENDER, "a lit photograph is the old bug"
    # The picture, whole, behind the moving face.
    assert "PlaneGeometry(1, 1)" in RENDER
    # And the one flip that has to be right or the face lands upside down.
    assert "0.5 - y" in RENDER


def test_the_photograph_is_preferred_over_the_head(client):
    """The head is still drawn for a face that only has one. It is not
    what anybody is shown when there is a choice."""
    order = STAGE.index("SpeakingPortrait src=")
    head = STAGE.index("<Avatar3D src=")
    assert order < head, "the mask is being drawn in front of the person"


def test_the_photo_door_builds_the_speaking_face(client):
    """Both doors exist; only one is put in front of a person."""
    assert "api.speakingFace(" in IDENTITY
    assert "api.forgeFace(" not in IDENTITY, (
        "the head build is back on the screen people meet")


def test_the_renderer_lets_go_of_the_gpu(client):
    for freed in ("geometry.dispose()", "texture.dispose()",
                  "renderer.forceContextLoss()", "cancelAnimationFrame"):
        assert freed in RENDER, freed
