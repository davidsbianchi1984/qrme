"""An FBX export becomes a face here, and the mouth comes through with it.

## What this replaces

The avatar shelf's first row — the only one handing over a MODEL rather
than a picture — used to end in an instruction:

    an FBX export needs converting to .glb first (Blender: File → Import
    → FBX, then File → Export → glTF 2.0, leaving Shape Keys checked so
    the mouth survives)

Every word of it was true, and it was still a shelf row with a manual
taped to it. Worse, the upload door could not accept an FBX even from
somebody willing: `media.save` proves a format from its bytes, an FBX
matches nothing it knows, and the answer was "unrecognized file".

    asked     do the conversion in the app
    mattered  does the mouth still move afterwards

## Why the counts are the test

A conversion that dropped half the morph targets still returns a model,
and it still loads. The only place anybody would find out is a face that
has stopped being able to speak — which is not a bug report somebody can
write, because from the outside it looks like the voice is broken.

So the door returns what survived, and these pin it. Measured against a
real MetaPerson export and the provider's own `.glb` of the same avatar:
114 morph targets, 114 of them named, across 8 meshes. `assimp` returns
111 and none, which is why the forge carries Blender.
"""

from __future__ import annotations

import base64
import json
import zipfile
import io

import pytest

from qrme import modelshop


class _Answer:
    def __init__(self, payload: dict) -> None:
        self._payload = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


#: A glTF binary's first four bytes are the format's own, which is what
#: `media.save` and this module both prove a model by.
_GLB = b"glTF" + b"\x00" * 60


def test_a_deployment_with_no_forge_says_so_rather_than_failing(monkeypatch):
    monkeypatch.setenv("QRME_FORGE_URL", "")
    assert modelshop.configured() is False
    with pytest.raises(modelshop.ConversionError) as raised:
        modelshop.to_glb(b"Kaydara FBX Binary  \x00", name="a.fbx")
    assert "upload a .glb" in raised.value.said


@pytest.mark.parametrize("name,wanted", [
    ("model.fbx", True), ("MODEL.FBX", True),
    ("avatar.zip", True), ("  avatar.ZIP  ", True),
    ("avatar.glb", False), ("portrait.png", False), (None, False),
])
def test_the_door_knows_which_files_are_its_own(name, wanted):
    assert modelshop.wants_converting(name) is wanted


@pytest.mark.parametrize("given,expected", [
    ("model.fbx", "model.glb"),
    ("avatar/model.fbx", "model.glb"),
    ("avatar.zip", "avatar.glb"),
    (None, "avatar.glb"),
    ("", "avatar.glb"),
])
def test_the_name_keeps_its_stem(given, expected):
    """A file called `model.fbx` comes back as `model.glb`, not `blob`."""
    assert modelshop._glb_name(given) == expected


def test_what_survived_rides_back_with_the_model(monkeypatch):
    """The counts are the point — a caller must never have to assume."""
    monkeypatch.setenv("QRME_FORGE_URL", "http://forge:8600")
    seen = {}

    def _fake(request, timeout=None):
        seen["url"] = request.full_url
        seen["body"] = json.loads(request.data.decode("utf-8"))
        return _Answer({"glb": base64.b64encode(_GLB).decode(),
                        "from": "zip", "meshes": 8,
                        "targets": 114, "named": 114})

    monkeypatch.setattr(modelshop.urllib.request, "urlopen", _fake)
    made = modelshop.to_glb(b"PK\x03\x04 pretend zip", name="avatar.zip")
    assert seen["url"].endswith("/convert")
    assert made["targets"] == 114 and made["named"] == 114
    assert made["meshes"] == 8 and made["from"] == "zip"
    assert made["glb"][:4] == b"glTF"
    assert made["name"] == "avatar.glb"


def test_the_converters_own_words_reach_the_person(monkeypatch):
    """"that zip holds no .fbx" is theirs to fix, so it is not flattened."""
    monkeypatch.setenv("QRME_FORGE_URL", "http://forge:8600")
    import urllib.error

    def _refuse(request, timeout=None):
        raise urllib.error.HTTPError(
            request.full_url, 422, "no", {},
            io.BytesIO(json.dumps({"detail": "that zip holds no .fbx"})
                       .encode()))

    monkeypatch.setattr(modelshop.urllib.request, "urlopen", _refuse)
    with pytest.raises(modelshop.ConversionError) as raised:
        modelshop.to_glb(b"PK\x03\x04", name="a.zip")
    assert raised.value.said == "that zip holds no .fbx"


def test_an_answer_that_is_not_a_model_is_refused(monkeypatch):
    """The door proves the format rather than trusting the converter."""
    monkeypatch.setenv("QRME_FORGE_URL", "http://forge:8600")

    def _wrong(request, timeout=None):
        return _Answer({"glb": base64.b64encode(b"<html>nope</html>").decode()})

    monkeypatch.setattr(modelshop.urllib.request, "urlopen", _wrong)
    with pytest.raises(modelshop.ConversionError) as raised:
        modelshop.to_glb(b"Kaydara FBX Binary  \x00", name="a.fbx")
    assert "not a model" in raised.value.said


def test_a_model_larger_than_the_door_is_refused(monkeypatch):
    monkeypatch.setenv("QRME_FORGE_URL", "http://forge:8600")
    with pytest.raises(modelshop.ConversionError) as raised:
        modelshop.to_glb(b"x" * (modelshop.MAX_BYTES + 1), name="a.fbx")
    assert "larger than" in raised.value.said


def test_the_shelf_no_longer_sends_anybody_to_blender():
    """The row that used to end in two menus.

    Named rather than left to a reader: this is the instruction the whole
    conversion exists to delete, and a future edit that reinstates it
    would be reinstating the defect.
    """
    from qrme import avatars

    row = [m for m in avatars.MARKET if m["key"] == "metaperson"][0]
    how = row["how"].lower()
    assert "blender" not in how
    assert "shape keys" not in how
    # And it says what a person actually has in their downloads folder.
    assert ".zip" in how and ".fbx" in how and ".glb" in how
