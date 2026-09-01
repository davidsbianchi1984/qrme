"""The stack's forge — a photograph in, a face that can speak out.

POST /forge {"photo": base64, "shot": "face|upper|full"} answers a 3-D
head built from that one photograph: the geometry personalized to the
face in the picture, the picture itself as its skin, and the morph
targets that let a mouth move. A portrait render comes back beside it,
because every surface in this product already knows how to draw a still.

    asked     can somebody have a face here without paying rent
    mattered  whose machine it is made on

## Why this exists at all

The avatar market used to be a list of other people's services and the
honest verb was *import*: export a picture there, paste it here. The
owner asked for the real thing — an avatar built from an uploaded photo,
rendered over the messages — and the road we picked was Ready Player Me,
which Netflix bought and shut off on 31 January 2026, developer APIs and
all. The replacements both price their API at eight hundred dollars a
month.

So the default road runs here, on the deployment's own hardware, for the
same reason the ears do: a face is not a subscription, and a company that
can be acquired should not be able to take everybody's face with it.
A vendor stays available as an *upgrade* for anybody who brings their own
key — the forge is the floor, never the ceiling.

## What it makes, honestly

MediaPipe's face landmarker finds the face and its canonical mesh; the
photograph becomes the texture through the model's own fixed UVs; and the
morph targets are generated from the canonical topology — a jaw that
opens, lips that part and round — so the room's existing audio can move
the mouth without a second machine learning model in the loop.

It is a **head**, and it says so. A full-body figure from one photograph
is a different problem and a different claim; this door does not pretend
to solve it, and `shot` decides framing rather than promising legs that
were never in the picture.

**The forge looks at what it is handed and nothing else.** No URL is
fetched here — bytes arrive in the request or there is no work — so
nothing in this container can be aimed at the stack behind it. The
photograph is used and dropped: only the model and the render leave.
"""

import base64
import io
import json
import os
import struct
import subprocess
import tempfile
import zipfile

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

#: How a photograph may be framed. The owner's own three: *"whether it's
#: full body, upper torso or just face"*. All three build a head — that
#: is what one photograph honestly supports — and the framing decides how
#: much of the picture is face to begin with, which is what the landmarker
#: needs to know before it looks.
SHOTS = ("face", "upper", "full")

#: The ceiling on an incoming photograph. A picture, not a poster.
MAX_PHOTO_BYTES = 12 * 1024 * 1024


class ForgeIn(BaseModel):
    photo: str = Field(..., description="The photograph, base64.")
    shot: str = Field("face", description="face | upper | full")


def _decode(photo: str) -> bytes:
    try:
        data = base64.b64decode(photo, validate=True)
    except Exception:
        raise HTTPException(422, "the photograph is not valid base64")
    if not data:
        raise HTTPException(422, "the photograph arrived empty")
    if len(data) > MAX_PHOTO_BYTES:
        raise HTTPException(422, "that photograph is larger than the "
                                 "forge takes")
    return data


@app.get("/health")
def health() -> dict:
    """Whether the forge can actually work, said before it is asked.

    This used to import `mediapipe` and call that a yes. It is not one:
    MediaPipe 1.0 loads its native bindings through ctypes at FIRST USE,
    so a container missing `libEGL.so.1` imports the module happily and
    throws the moment a photograph arrives — which is how this door
    answered "ready": true while every upload came back "could not build
    a head". A check that passes when the thing is broken is worse than
    no check, because it sends somebody looking at their own photograph
    for the fault.

    So it builds a landmarker over a tiny synthetic image — the whole
    road, in miniature — and reports what actually happened.
    """
    try:
        import numpy as np
        import mediapipe as mp
        from mediapipe.tasks import python as mp_python
        from mediapipe.tasks.python import vision

        frame = mp.Image(image_format=mp.ImageFormat.SRGB,
                         data=np.zeros((32, 32, 3), dtype=np.uint8))
        options = vision.FaceLandmarkerOptions(
            base_options=mp_python.BaseOptions(
                model_asset_path=os.environ.get(
                    "FORGE_MODEL", "/srv/face_landmarker.task")),
            num_faces=1)
        with vision.FaceLandmarker.create_from_options(options) as looker:
            looker.detect(frame)          # no face in it, and that is fine
        # The maker's own imports too — a forge that can see and cannot
        # build is still a forge that cannot work.
        from facebuild import build_head  # noqa: F401
        return {"status": "ok", "ready": True, "shots": list(SHOTS),
                "converts": _can_convert()}
    except Exception as exc:
        return {"status": "ok", "ready": False,
                "why": f"{type(exc).__name__}: {exc}",
                "converts": _can_convert()}


def _can_convert() -> bool:
    """Whether an FBX could actually be opened, not whether Blender runs.

        asked     is the converter ready
        mattered  `blender --version` answers on a Blender that cannot
                  import a single FBX

    The importer is a Python addon and it does `import numpy` at the top
    of `import_fbx`. An image built with `--no-install-recommends` and no
    `python3-numpy` therefore has a Blender that starts, prints its
    version, registers the addon — and throws `ModuleNotFoundError` at
    the first file. This container shipped that way for exactly one
    build, which is the same trap `/health` above already exists to avoid
    for MediaPipe.

    So the check OPENS the importer, in the same headless Blender the
    conversion uses, and reports what happened rather than what is
    installed.
    """
    try:
        done = subprocess.run(
            ["blender", "--background", "--factory-startup",
             "--python-expr", "import io_scene_fbx.import_fbx"],
            capture_output=True, timeout=60)
        return done.returncode == 0 and b"Error" not in done.stderr
    except Exception:
        return False


@app.post("/forge")
def forge(body: ForgeIn) -> dict:
    """One photograph into one speakable head.

    Answers ``{glb, portrait, blendshapes}``: the model as base64, a
    portrait render as base64 PNG, and the names of the morph targets the
    renderer may drive. Every failure is a refusal in words — a face the
    landmarker could not find is the common one, and it is the person's
    to fix by sending a clearer picture.
    """
    if body.shot not in SHOTS:
        raise HTTPException(
            422, "say how the photo is framed — just the face, the upper "
                 "torso, or the full body")
    photo = _decode(body.photo)

    try:
        from facebuild import build_head           # the forge's own maker
    except Exception as exc:                        # pragma: no cover
        raise HTTPException(
            503, f"the forge's maker is not loaded: {exc}") from None

    try:
        made = build_head(photo, shot=body.shot)
    except LookupError:
        # The one refusal a person can act on: no face in the picture.
        raise HTTPException(
            422, "no face was found in that photograph — a clearer, "
                 "front-facing picture is what this needs") from None
    except Exception:
        raise HTTPException(
            500, "the forge could not build a head from that "
                 "photograph") from None

    return {
        "glb": base64.b64encode(made["glb"]).decode("ascii"),
        "portrait": base64.b64encode(made["portrait"]).decode("ascii"),
        "blendshapes": made["blendshapes"],
        "shot": body.shot,
    }


@app.post("/speak")
def speak(body: ForgeIn) -> dict:
    """The photograph's own measurements, so it can be made to speak.

    Answers ``{points, triangles, shapes, mouth, width, height}`` — where
    the face's points sit in the picture, how they join up, and how the
    mouth moves in the picture's own plane. No model, no texture, no copy
    of the photograph: the console already has the picture, and this is
    the small amount of arithmetic that lets it move.

    ## Why this door exists beside /forge

    `/forge` builds a head, and a head from 478 face points has no skull,
    no hair and no ears — it can only ever be a mask, and a mask is not
    the person. Laid flat over the photograph the same measurements stop
    being a mask and become the photograph: at rest the mesh is a copy of
    the picture over the picture, and the only thing that ever moves is a
    mouth.

        asked     let the avatar speak
        mattered  let it still be them while it does

    Both doors stay. This one is what a person is shown.
    """
    if body.shot not in SHOTS:
        raise HTTPException(
            422, "say how the photo is framed — just the face, the upper "
                 "torso, or the full body")
    photo = _decode(body.photo)

    try:
        from facebuild import build_speaking       # the forge's own maker
    except Exception as exc:                        # pragma: no cover
        raise HTTPException(
            503, f"the forge's maker is not loaded: {exc}") from None

    try:
        return build_speaking(photo, shot=body.shot)
    except LookupError:
        raise HTTPException(
            422, "no face was found in that photograph — a clearer, "
                 "front-facing picture is what this needs") from None
    except Exception:
        raise HTTPException(
            500, "the forge could not measure that photograph") from None


#: What a model may weigh coming in. A MetaPerson FBX is about 7MB and
#: its zip about 6; a rig from somebody's own pipeline is legitimately
#: larger than a photograph, so this is not the photo ceiling.
MAX_MODEL_BYTES = 64 * 1024 * 1024

#: And what it may weigh once unpacked. A zip that expands a thousandfold
#: is not an avatar.
MAX_UNPACKED_BYTES = 256 * 1024 * 1024

#: How long Blender gets. The measured conversion of a MetaPerson avatar
#: is under three seconds; a minute is room for a far heavier rig and a
#: cold cache, and a wall for a file that has sent the importer somewhere
#: it will not come back from.
CONVERT_SECONDS = 120

#: Where the conversion script lives inside the image.
_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "to_glb.py")


class ConvertIn(BaseModel):
    model: str = Field(..., description="The .fbx or .zip, base64.")


def _what_is_it(data: bytes) -> str:
    """Read the bytes, not the file name.

        asked     take the export the provider hands over
        mattered  a name is a claim, and the door is the wrong place to
                  believe one

    A zip announces itself, and so does a binary FBX — Kaydara's writer
    stamps its own name into the first twenty bytes. An ASCII FBX says so
    in a comment near the top. Anything else is not something this door
    converts, and saying so beats handing Blender a file to be surprised
    by.
    """
    # An archive with nothing in it writes the end-of-central-directory
    # signature and no local header, and one written across volumes
    # writes a third. All three are zips, and a person handed "that is
    # not a zip" about a file that plainly is would go looking in the
    # wrong place — the honest answer for an empty one is that it holds
    # no model.
    if data[:4] in (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"):
        return "zip"
    if data[:20] == b"Kaydara FBX Binary  ":
        return "fbx"
    if b"FBXHeaderExtension" in data[:4096]:
        return "fbx"
    return "?"


def _fbx_out_of(data: bytes) -> bytes:
    """The one model inside the archive, and nothing else out of it.

    MetaPerson hands over `avatar/model.fbx` inside a zip, which is what
    somebody actually has to drag in — so the door takes the zip. That
    means opening an archive somebody else made, and every rule below is
    there because an archive is not a file:

    * exactly one `.fbx` member, so there is no question which model was
      meant;
    * no member whose path escapes the directory it is unpacked into —
      `..` or a leading slash — which is the oldest bug in unzipping;
    * no symlinks, which are the same bug wearing a hat;
    * a ceiling on the unpacked size, so a small archive cannot become a
      full disk.

    Only the FBX's bytes are read. Nothing is written to disk here at
    all, so a path that escapes is refused rather than merely landing
    somewhere harmless.
    """
    try:
        bundle = zipfile.ZipFile(io.BytesIO(data))
    except Exception:
        raise HTTPException(422, "that zip could not be opened")

    models, total = [], 0
    for item in bundle.infolist():
        name = item.filename
        if name.endswith("/"):
            continue
        if name.startswith("/") or ".." in name.replace("\\", "/").split("/"):
            raise HTTPException(422, "that zip holds a path that points "
                                     "outside itself")
        # The high bits of `external_attr` carry the unix mode; 0xA000 is
        # a symlink.
        if (item.external_attr >> 16) & 0xF000 == 0xA000:
            raise HTTPException(422, "that zip holds a link rather than "
                                     "a file")
        total += item.file_size
        if total > MAX_UNPACKED_BYTES:
            raise HTTPException(422, "that zip unpacks to more than the "
                                     "forge takes")
        if name.lower().endswith(".fbx"):
            models.append(item)

    if not models:
        raise HTTPException(422, "that zip holds no .fbx — MetaPerson's "
                                 "export has one inside a folder called "
                                 "avatar")
    if len(models) > 1:
        raise HTTPException(422, "that zip holds more than one .fbx, so "
                                 "which one is the avatar is not this "
                                 "door's guess to make")
    with bundle.open(models[0]) as handle:
        return handle.read(MAX_UNPACKED_BYTES + 1)


def _facts(glb: bytes) -> dict:
    """What came out, counted — so a caller never has to trust the door.

    The numbers that decide whether a face can speak: how many morph
    targets survived and how many of them still have names. A conversion
    that silently halves either is a conversion somebody would only find
    out about from a mouth that does not move.
    """
    try:
        length, = struct.unpack("<I", glb[12:16])
        scene = json.loads(glb[20:20 + length])
    except Exception:
        return {"meshes": 0, "targets": 0, "named": 0}
    targets = sum(len(p.get("targets", []))
                  for m in scene.get("meshes", [])
                  for p in m.get("primitives", []))
    named = sum(len((m.get("extras") or {}).get("targetNames", []))
                for m in scene.get("meshes", []))
    return {"meshes": len(scene.get("meshes", [])),
            "targets": targets, "named": named}


@app.post("/convert")
def convert(body: ConvertIn) -> dict:
    """An FBX in, a `.glb` the console can load out.

        asked     do the conversion in the app
        mattered  the shelf's answer was "go and install Blender"

    Both shapes, because both are real: a bare `.fbx` for somebody with
    their own pipeline, and the `.zip` for somebody who has just pressed
    export at MetaPerson and has whatever that gave them.
    """
    try:
        data = base64.b64decode(body.model, validate=True)
    except Exception:
        raise HTTPException(422, "the model is not valid base64")
    if not data:
        raise HTTPException(422, "the model arrived empty")
    if len(data) > MAX_MODEL_BYTES:
        raise HTTPException(422, "that model is larger than the forge takes")

    kind = _what_is_it(data)
    if kind == "zip":
        fbx = _fbx_out_of(data)
    elif kind == "fbx":
        fbx = data
    else:
        raise HTTPException(422, "that is neither an .fbx nor a zip with "
                                 "one inside it")

    with tempfile.TemporaryDirectory() as room:
        src = os.path.join(room, "in.fbx")
        dst = os.path.join(room, "out.glb")
        with open(src, "wb") as handle:
            handle.write(fbx)
        try:
            done = subprocess.run(
                ["blender", "--background", "--factory-startup",
                 "--python", _SCRIPT, "--", src, dst],
                capture_output=True, timeout=CONVERT_SECONDS)
        except subprocess.TimeoutExpired:
            raise HTTPException(504, "the conversion did not finish in "
                                     f"{CONVERT_SECONDS} seconds")
        if not os.path.exists(dst):
            # Blender's own last words, not a shrug. The importer is the
            # part that fails on a file it does not like, and its message
            # names the reason.
            why = (done.stderr or done.stdout or b"").decode(
                "utf-8", "replace").strip().splitlines()
            raise HTTPException(
                422, "that model could not be converted"
                     + (f": {why[-1][:300]}" if why else ""))
        with open(dst, "rb") as handle:
            glb = handle.read()

    return {"glb": base64.b64encode(glb).decode(), "from": kind,
            "bytes": len(glb), **_facts(glb)}
