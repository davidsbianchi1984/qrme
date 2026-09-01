"""An FBX export becomes a `.glb` the console can load — here, not in Blender.

## What this replaces

The avatar shelf has told people, in writing, for months:

    A .glb can be pasted or uploaded here as it is; an FBX export needs
    converting to .glb first (Blender: File → Import → FBX, then File →
    Export → glTF 2.0, leaving Shape Keys checked so the mouth survives).

MetaPerson's credit tier exports FBX, and the console loads `.glb`. So
the shelf's first row — the only one that hands over a MODEL rather than
a picture — ended in an instruction to go and install a 1GB desktop
application and learn two of its menus. An upload door that cannot accept
what the provider actually gives you is a door with a manual taped to it.

    asked     do the conversion in the app
    mattered  does the mouth still move afterwards

## Why the forge, and why Blender inside it

The forge already builds and holds 3-D faces, so the conversion lives
beside the thing it produces rather than in a fourth container.

Blender is what the instruction above already named, so the automatic
path and the documented path cannot produce different faces. Measured
against `assimp`, which is a tenth the size: round-tripping a real
MetaPerson avatar, assimp returned 111 of 114 morph targets — the three
missing from `AvatarHead` and `AvatarTeethLower`, the two meshes that
move when a face speaks — and none of their names at all, because its
glTF writer emits no `extras.targetNames`. The console drives the mouth
BY NAME (`jawOpen`, `CH`, `DD`, `E`, `FF`), so a nameless target is one
no viseme can find. Blender reproduced the provider's own export exactly:
114 targets, 114 names, 82 nodes, one skin.

## What comes in

Both shapes, because both are real: a bare `.fbx` from somebody with
their own pipeline, and the `.zip` the provider hands you — which is what
a person actually has after pressing export, and unpacking it by hand is
one more instruction this exists to delete.
"""

from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.request

from . import avatarforge, media, offline

#: What this door takes. A `.glb` is already loadable and never comes
#: here; these are the two that are not.
TAKES = (".fbx", ".zip")

#: The ceiling, matching the forge's own. A MetaPerson FBX is about 7MB.
MAX_BYTES = 64 * 1024 * 1024


class ConversionError(Exception):
    """Said in a person's words, because they are the one who fixes it."""

    def __init__(self, said: str) -> None:
        super().__init__(said)
        self.said = said


def configured() -> bool:
    """Whether an FBX could be converted here at all.

    False is an answer the screen shows — "a .glb, please" — rather than
    a button that fails. It shares `QRME_FORGE_URL` with the face maker
    because it is the same container; a deployment that has one has both.
    """
    return bool(avatarforge.forge_url())


def wants_converting(name: str | None) -> bool:
    """Whether this file is one this door exists for."""
    return bool(name) and name.lower().strip().endswith(TAKES)


def to_glb(data: bytes, *, name: str | None = None,
           on_behalf_of: str | None = None) -> dict:
    """The bytes of an FBX or its zip, in; the bytes of a `.glb`, out.

    Returns the model and what survived it — how many morph targets and
    how many still carry names — so a caller can say so rather than
    assert it. A conversion that halves either is one somebody would
    otherwise learn about from a mouth that does not move.
    """
    if not configured():
        raise ConversionError(
            "this deployment cannot convert an FBX — upload a .glb, or "
            "set QRME_FORGE_URL to a forge that can")
    if not data:
        raise ConversionError("the model arrived empty")
    if len(data) > MAX_BYTES:
        raise ConversionError(
            f"that model is larger than the {MAX_BYTES // (1024 * 1024)}MB "
            "this door takes")

    # The forge is a container on this stack's own network and the model
    # never leaves the host — but that is a property of how somebody
    # deployed it, not of this code, and `QRME_FORGE_URL` can name any
    # host at all. Offline mode is the estate's answer to exactly that
    # gap: the check is on the URL rather than on an assumption about it.
    offline.allow(avatarforge.forge_url(), "the forge's converter",
                  on_behalf_of)
    body = json.dumps({"model": base64.b64encode(data).decode("ascii")})
    request = urllib.request.Request(
        f"{avatarforge.forge_url()}/convert", data=body.encode("utf-8"),
        method="POST", headers={"content-type": "application/json"})
    try:
        # Measured at under three seconds for a MetaPerson avatar. The
        # ceiling is for a far heavier rig on a busy box, and is the
        # forge's own timeout plus room to answer.
        with urllib.request.urlopen(request, timeout=180) as answer:
            made = json.loads(answer.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        # The forge's refusals are already worded for a person — "that zip
        # holds no .fbx" is theirs to fix. Passed through rather than
        # flattened into a status nobody can act on.
        try:
            said = json.loads(exc.read().decode("utf-8")).get("detail")
        except Exception:
            said = None
        raise ConversionError(said or "the conversion was refused") from None
    except Exception:
        raise ConversionError(
            "the converter could not be reached just now") from None

    try:
        glb = base64.b64decode(made["glb"], validate=True)
    except Exception:
        raise ConversionError("the converter answered without a model") from None
    if glb[:4] != b"glTF":
        raise ConversionError("the converter answered with something that "
                              "is not a model")
    return {"glb": glb, "from": made.get("from", "fbx"),
            "meshes": int(made.get("meshes", 0)),
            "targets": int(made.get("targets", 0)),
            "named": int(made.get("named", 0)),
            "name": _glb_name(name)}


def convert_and_store(profile_id: str, data: bytes,
                      name: str | None = None,
                      on_behalf_of: str | None = None) -> dict:
    """Convert, then keep the result the way every other upload is kept.

    The `.glb` goes through `media.save`, which proves the format from the
    bytes themselves — so what is stored is a model because it IS one, not
    because this module said so. The FBX is not kept: it is the crate the
    avatar arrived in, and the product has no use for it afterwards.
    """
    made = to_glb(data, name=name, on_behalf_of=on_behalf_of)
    stored = media.save(profile_id, made["glb"], made["name"])
    return {**{k: v for k, v in made.items() if k != "glb"},
            "asset": stored.get("url"), "media_id": stored.get("id"),
            "bytes": len(made["glb"])}


def _glb_name(name: str | None) -> str:
    """The same file name, wearing the extension it now deserves."""
    stem = (name or "avatar").rsplit("/", 1)[-1]
    for ending in TAKES:
        if stem.lower().endswith(ending):
            stem = stem[: -len(ending)]
            break
    return (stem.strip() or "avatar") + ".glb"
