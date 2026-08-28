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

    A container whose model failed to load answers honestly here rather
    than failing on somebody's photograph — the same posture the ears
    keep. `ready` false with a reason is a working answer.
    """
    try:
        import mediapipe  # noqa: F401
        return {"status": "ok", "ready": True, "shots": list(SHOTS)}
    except Exception as exc:
        return {"status": "ok", "ready": False,
                "why": f"the landmarker is not loaded: {exc}"}


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
