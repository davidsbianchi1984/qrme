"""A head built from somebody's photograph has to look like them.

## What shipped

The forge built a head, the console mounted it, and what a person saw was
a featureless white blob with a little facet shading on it. Two separate
reasons, and each would have been enough on its own:

**The texture was labelled a lie.** The uploaded bytes went into the glTF
as-is under a declared `image/png`, and almost every photograph anybody
uploads is a JPEG. A reader is entitled to believe that declaration; the
ones that do get a decode failure and draw the head with no skin at all.
This is the same failure `qrme/media.py` was written against — a kind
taken from a label rather than proved from the bytes — one layer out.

**And the lighting ate what was left.** Ambient 1.6 plus a 0.6 key over
a lit material multiplies the photograph by more than two, so every pixel
above about four-tenths brightness clipped to white.

    asked     is the face lit
    mattered  is the photograph still visible after lighting it

Both are guarded here at the source, because the machinery that would
prove it at runtime — MediaPipe, pygltflib — lives in the forge's own
container and a test that skips is a test that proves nothing.
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
RENDER = (REPO / "app" / "src" / "Avatar3D.tsx").read_text(encoding="utf-8")


# --------------------------------------------------------------------------
# The skin


def test_the_texture_is_encoded_not_asserted():
    """`image/png` is declared in the file, so PNG is what has to be in
    it — proved by an encoder rather than by hoping the upload was one."""
    assert 'mimeType="image/png"' in FORGE, (
        "the declaration moved; this guard is about it being true")
    assert "def _as_png(" in FORGE
    body = FORGE.split("def build_head(")[1]
    assert "_as_png(photo)" in body, (
        "the raw upload goes into the file under a declared PNG again")
    assert 'format="PNG"' in FORGE.split("def _as_png(")[1].split("\ndef ")[0]


def test_the_bytes_that_are_embedded_are_the_ones_that_were_encoded():
    """A re-encode that the writer then ignores is worse than none: it
    reads as fixed."""
    body = FORGE.split("def build_head(")[1]
    call = re.search(r"_glb\(positions, uvs, faces, morphs, (\w+)\)", body)
    assert call, "the glb call changed shape"
    assert call.group(1) == "skin", (
        f"_glb is handed {call.group(1)!r}, not the encoded texture")


# --------------------------------------------------------------------------
# The light


def test_a_photographed_face_is_not_lit_twice():
    """The material carrying the photograph is unlit, so the skin is drawn
    at the brightness it was taken at."""
    assert "MeshBasicMaterial" in RENDER, (
        "the photograph is back on a lit material, which is what washed "
        "it out to white")
    swap = RENDER[RENDER.index("MeshBasicMaterial") - 400:]
    swap = swap[:swap.index("}")]
    assert "map: lit.map" in swap, "the swap drops the photograph"


def test_the_lights_that_remain_cannot_blow_out_a_texture():
    """They only reach a head that arrived without a photograph, and they
    are kept under one between them so that head is lit rather than
    over-exposed."""
    amounts = [float(m) for m in re.findall(
        r"THREE\.(?:Ambient|Directional)Light\(0xffffff, ([\d.]+)\)", RENDER)]
    assert amounts, "the lights are gone entirely"
    assert sum(amounts) <= 1.3, (
        f"the lights total {sum(amounts)}, which multiplies a photograph "
        "past white — this is the defect, in numbers")


def test_the_old_material_is_released():
    """A material swapped out and not disposed is GPU memory nothing will
    come back for — the same rule the renderer's own teardown keeps."""
    assert "lit.dispose()" in RENDER


# --------------------------------------------------------------------------
# What the renderer still has to do


def test_the_jaw_still_moves():
    """The swap is to a material that carries morph targets. A skin that
    arrived at the cost of a still face would be a bad trade."""
    assert "morphTargetInfluences" in RENDER
    assert "jawOpen" in RENDER
