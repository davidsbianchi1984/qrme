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
import os
import struct
import tempfile

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
        return {"status": "ok", "ready": True, "shots": list(SHOTS)}
    except Exception as exc:
        return {"status": "ok", "ready": False,
                "why": f"{type(exc).__name__}: {exc}"}


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
