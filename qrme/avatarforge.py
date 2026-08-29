"""The forge — a photograph becomes a face this platform can speak with.

## The lesson this module is named after

The avatar market (`qrme/avatars.py`) was an *import* list, honest about
it: export a picture from somebody else's service, paste it here. The
owner asked for the real thing, and the road we chose first was Ready
Player Me — which Netflix had already bought and shut down, developer
APIs and all, on 31 January 2026. The two production replacements both
price their API at eight hundred dollars a month.

So the road that MAKES a face runs on this deployment's own hardware,
for the same reason the ears do, and the reason is not thrift:

    asked     can somebody have a face here
    mattered  whose company has to still exist next year for it to work

A vendor is a **slot**, never the foundation. `PROVIDERS` is the list of
roads this module can speak; ``forge`` is ours and is the default, and a
paid provider is an upgrade for whoever brings their own key. The day a
vendor is acquired, a deployment changes one environment variable.

## What the forge makes

The sidecar (`docker/forge/`) runs MediaPipe's face landmarker on one
photograph and answers a 3-D head: geometry personalized to that face,
the photograph itself as its skin, and morph targets named exactly as
ARKit names them — ``jawOpen``, ``mouthPucker``, the smiles, the blinks.

The names are the interoperability. A renderer that drives ``jawOpen``
on one of our heads drives ``jawOpen`` on any vendor's model, so the
console's mouth code never learns a second vocabulary and the upgrade
path costs nothing on this side.

## The likeness, and the mark

A head built from somebody's own photograph is **their own likeness**,
not an invented person, and it is not stamped: the AI mark exists to
stop a synthetic face passing as real, and burning it into an authentic
one is that same failure run backwards (`avatarreg.mint`). What IS
synthetic is a profile *speaking* through that face, and the credential
on that already rides the presentation and watermark layers that every
surface reads.

## Honesty

Every road out of here returns None or raises a worded refusal. A
deployment with no forge configured says it has no forge. A photograph
with no face in it says so, in words the person can act on — send a
clearer picture — rather than a placeholder head nobody asked for.
"""

from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.request

#: The roads this module can speak. Ours leads because it is the one
#: that cannot be discontinued; the rest are named so a deployment can
#: choose one without this file changing again.
PROVIDERS = ("forge", "none")

#: How a photograph may be framed — the owner's own three, carried
#: through to the sidecar unchanged: *"whether it's full body, upper
#: torso or just face"*.
SHOTS = ("face", "upper", "full")

#: What a photograph may weigh on the way in. The sidecar keeps its own
#: ceiling too; this one exists so an oversized upload is refused at the
#: door rather than after a round trip.
MAX_PHOTO_BYTES = 12 * 1024 * 1024


class ForgeError(RuntimeError):
    """A refusal from this road, worded for the person who asked."""


def provider() -> str:
    """Which road this deployment makes faces on. ``forge`` unless the
    operator names another; an unknown name reads as none, because a
    misspelled provider must not silently become a working one."""
    named = os.environ.get("QRME_AVATAR_PROVIDER", "forge").strip()
    return named if named in PROVIDERS else "none"


def forge_url() -> str:
    return os.environ.get("QRME_FORGE_URL", "").strip().rstrip("/")


def configured() -> bool:
    """Whether a photograph can actually become a face here. False is an
    answer the screen shows rather than a button that fails."""
    return provider() == "forge" and bool(forge_url())


def doors() -> dict:
    """What this deployment offers, said before anybody uploads
    anything — the console draws the upload road only when there is one,
    and says why when there is not."""
    return {"provider": provider(),
            "configured": configured(),
            "shots": list(SHOTS),
            # The shapes a renderer may drive on whatever comes back.
            # ARKit's names on purpose (see the module docstring), so a
            # vendor model and one of ours animate identically.
            "blendshapes": ["jawOpen", "mouthPucker", "mouthSmileLeft",
                            "mouthSmileRight", "eyeBlinkLeft",
                            "eyeBlinkRight"]}


def from_photo(photo: bytes, *, shot: str = "face",
               on_behalf_of: str | None = None) -> dict:
    """One photograph into one speakable head.

    Answers ``{"portrait": bytes, "model": bytes, "blendshapes": [...]}``
    — the still every surface already draws, the ``.glb`` the seats draw
    in three dimensions, and what its mouth can be told to do.
    """
    if shot not in SHOTS:
        raise ForgeError(
            "say how the photo is framed — just the face, the upper "
            "torso, or the full body")
    if not photo:
        raise ForgeError("the upload arrived empty")
    if len(photo) > MAX_PHOTO_BYTES:
        raise ForgeError(
            "that photograph is larger than the forge takes — twelve "
            "megabytes is the ceiling")
    if not configured():
        raise ForgeError(
            "this deployment has no avatar forge configured — the door "
            "exists, the machinery does not")

    # Offline mode's own rule, and the forge passes it the way the ears
    # do: the check is on the HOST, not a blanket refusal. A stack-
    # internal sidecar is on this side of the wire, so an offline
    # deployment still builds faces — what it refuses is a forge somebody
    # pointed at the open web, which would carry a photograph off the
    # machine. `nothing leaves the host` has to be true of this door too.
    from . import offline
    # Named on somebody's behalf, like every other errand that leaves
    # this process: a face is built FOR a profile, and an outbound path
    # that cannot say whose it is cannot be accounted for afterwards.
    offline.allow(forge_url(), "the forge's photograph", on_behalf_of)

    body = json.dumps({
        "photo": base64.b64encode(photo).decode("ascii"),
        "shot": shot,
    }).encode("utf-8")
    request = urllib.request.Request(
        f"{forge_url()}/forge", data=body, method="POST",
        headers={"content-type": "application/json"})
    try:
        # A head takes real seconds to build and a person is watching a
        # spinner while it does; the ceiling is generous rather than
        # optimistic, because a timeout here reads as a broken product.
        with urllib.request.urlopen(request, timeout=120) as answer:
            made = json.loads(answer.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        # The forge's own refusals are already worded for a person — a
        # photograph with no face in it is the common one, and it is
        # theirs to fix. Pass it through rather than flattening it into
        # a status nobody can act on.
        try:
            said = json.loads(exc.read().decode("utf-8")).get("detail")
        except Exception:
            said = None
        raise ForgeError(
            said or "the forge refused that photograph") from None
    except Exception:
        raise ForgeError(
            "the forge could not be reached from here") from None

    try:
        portrait = base64.b64decode(made["portrait"])
        model = base64.b64decode(made["glb"])
    except Exception:
        raise ForgeError(
            "the forge answered with something this end cannot "
            "read") from None
    if not portrait or not model:
        raise ForgeError("the forge answered with an empty face")
    return {"portrait": portrait, "model": model,
            "blendshapes": made.get("blendshapes") or []}


def speech_map(photo: bytes, *, shot: str = "face",
               on_behalf_of: str | None = None) -> dict:
    """The photograph's own measurements, so the console can make it speak.

    Answers ``{points, triangles, shapes, mouth, width, height}``: where
    the face's points sit in the picture, how they join up, and how the
    mouth moves in the picture's own plane.

    ## Why this is the door a person is shown, and `from_photo` is not

    `from_photo` builds a head, and a head from 478 face points has no
    skull, no hair and no ears. However well it is textured and lit, it
    is a mask — the field looked at one and said "that isn't the photo I
    uploaded, that's a white moving skeleton frame", which is exactly
    right about what a landmark mesh is.

        asked     let the avatar speak
        mattered  let it still be them while it does

    Laid flat over the photograph the same measurements stop being a mask
    and become the photograph: the mesh is a copy of the picture, at the
    places it was measured, over the picture. At rest it cannot be seen.
    The only thing that ever moves is a mouth, and everything that is not
    a mouth is never touched — which is why the person on screen goes on
    being the person in the photo.

    No picture comes back. It is already on the profile, and a second
    copy of somebody's face travelling for no reason is a cost with no
    benefit attached.
    """
    if shot not in SHOTS:
        raise ForgeError(
            "say how the photo is framed — just the face, the upper "
            "torso, or the full body")
    if not photo:
        raise ForgeError("the upload arrived empty")
    if len(photo) > MAX_PHOTO_BYTES:
        raise ForgeError(
            "that photograph is larger than the forge takes — twelve "
            "megabytes is the ceiling")
    if not configured():
        raise ForgeError(
            "this deployment has no avatar forge configured — the door "
            "exists, the machinery does not")

    from . import offline
    offline.allow(forge_url(), "the forge's photograph", on_behalf_of)

    body = json.dumps({
        "photo": base64.b64encode(photo).decode("ascii"),
        "shot": shot,
    }).encode("utf-8")
    request = urllib.request.Request(
        f"{forge_url()}/speak", data=body, method="POST",
        headers={"content-type": "application/json"})
    try:
        # Measuring is much cheaper than building — no mesh is written,
        # no texture encoded — so the ceiling is a fraction of the head's.
        with urllib.request.urlopen(request, timeout=45) as answer:
            made = json.loads(answer.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        try:
            said = json.loads(exc.read().decode("utf-8")).get("detail")
        except Exception:
            said = None
        raise ForgeError(
            said or "the forge refused that photograph") from None
    except Exception:
        raise ForgeError(
            "the forge could not be reached from here") from None

    if not made.get("points") or not made.get("triangles"):
        raise ForgeError("the forge answered with nothing to move")
    return made
