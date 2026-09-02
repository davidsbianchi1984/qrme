"""Profile portraits — the visual half of a synthetic identity.

Reads are public for the same reason the watermark endpoint is: a face that
a stranger can see is a face a stranger should be able to check. Every
response carries the AI badge and the likeness record, so a surface cannot
show the picture without also having been handed the disclosure.
"""

from __future__ import annotations

import base64
import json

import os

from pydantic import BaseModel, Field

from fastapi import APIRouter, Depends, HTTPException, Request

from .. import (auth, avatarforge, avatarreg, avatars, filming, media,
                modelshop,
                portraitist,
                presentation, skins)
from ..common import profile_or_404, require_owner
from .. import i18n

router = APIRouter()


class AvatarSet(BaseModel):
    asset: str = Field(min_length=1, max_length=500,
                       description="Asset reference or URL of the rendered "
                                   "portrait.")
    motion_style: str | None = Field(
        default=None, max_length=20,
        description="How the portrait moves: still, breathe, or lively. "
                    "The animation itself follows the interaction history.")
    presentation_kind: str | None = Field(
        default=None, max_length=10,
        description="What the asset is — image, video, model or scene — for "
                    "an asset whose address does not say. Leave it off and "
                    "the address decides, which is right for anything with "
                    "an extension on it.")


@router.get("/profiles/{profile_id}/avatar")
def get_avatar(profile_id: str) -> dict:
    """The profile's portrait as it must be displayed — asset, AI badge, and
    whose likeness it is. 2-D, 3-D, VR and AR surfaces all read this."""
    profile_or_404(profile_id)
    return avatars.render(profile_id)


@router.put("/profiles/{profile_id}/avatar")
def set_avatar(profile_id: str, body: AvatarSet, request: Request) -> dict:
    """Owner attaches a rendered portrait — and, optionally, how it moves."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    if body.motion_style is not None:
        try:
            avatars.set_motion(profile_id, body.motion_style)
        except ValueError as exc:
            raise HTTPException(422, i18n.raised(exc)) from None
    # An empty string clears the override and hands the question back to the
    # address, which is what an owner who mis-declared once needs.
    if body.presentation_kind is not None:
        try:
            presentation.set_kind(profile_id,
                                  body.presentation_kind.strip() or None)
        except ValueError as exc:
            raise HTTPException(422, i18n.raised(exc)) from None
    return avatars.set_avatar(profile_id, body.asset)


class AvatarImport(BaseModel):
    source: str = Field(min_length=1, max_length=40,
                        description="An import source from GET /avatars/market,"
                                    " or 'photos' / 'capture' for the owner's"
                                    " own face.")
    asset: str = Field(min_length=1, max_length=500,
                       description="Media reference from the upload door, or a"
                                   " direct URL to the avatar image.")
    extra: list[str] = Field(default_factory=list, max_length=12,
                             description="Additional frames — the selfie"
                                         " capture posts every angle it took.")
    torso: str | None = Field(default=None, max_length=500,
                              description="The upper-torso form of the same"
                                          " avatar — the figure that stands"
                                          " in a live feed or AR at 1:1.")
    provider_asset_id: str | None = Field(
        default=None, max_length=120,
        description="The provider's own id for this avatar — an owner"
                    " linking their ElevenLabs avatar records it here, so"
                    " the face's provenance names the exact record it"
                    " came from.")


@router.get("/avatars/forge")
def forge_doors() -> dict:
    """Whether a photograph can become a face on this deployment, and how
    it may be framed.

    Public, and answered before anybody uploads anything: a console that
    draws the upload road on a deployment with no forge is a button that
    fails, and a person who has just chosen a photo of themselves is the
    worst possible moment to discover it.
    """
    return avatarforge.doors()


@router.get("/video/doors")
def video_doors() -> dict:
    """Whether a described scene can become video on this deployment.

    Public and answered before anybody writes a prompt, for the same
    reason the forge's door is: a console that draws the road on a
    deployment that has none is a button that fails, and somebody who
    has just written the scene they wanted is the worst moment to find
    out.

    It is shut everywhere today, and `why` says so in words rather than
    leaving a screen to invent an explanation for a false flag.
    """
    return filming.doors()


class Road(BaseModel):
    road: str = Field(description="photo, avatar or video — which road this "
                                  "profile's presence takes.")
    daily_seconds: int | None = Field(default=None, ge=0, le=3600,
                                      description="Seconds of finished "
                                                  "footage per day. What "
                                                  "makes choosing video "
                                                  "safe.")
    provider: str | None = Field(default=None,
                                 description="Which video service renders "
                                             "this profile. Omitted leaves "
                                             "the choice as it stands; "
                                             "\"none\" hands it back to the "
                                             "deployment.")


@router.get("/video/road/{profile_id}")
def video_road(profile_id: str, request: Request) -> dict:
    """Which road this profile takes, its ceiling, and what is left today.

    Owner-only, and not for tidiness: the answer carries the daily
    ceiling, the seconds spent, and the render service — a profile's
    money posture, which is nobody's read but its owner's. The sibling
    POST guards the same thing because it *sets* it; this guards it
    because it *shows* it, and a spend a stranger can read is a spend a
    stranger is halfway to steering.
    """
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    return {**filming.road_of(profile_id), **filming.budget(profile_id),
            "roads": list(filming.ROADS),
            "providers": [p for p in filming.PROVIDERS if p != "none"]}


@router.post("/video/road/{profile_id}")
def video_set_road(profile_id: str, body: Road, request: Request) -> dict:
    """Choose the road, the ceiling that makes video safe, and the service.

    Owner-only. This door sets what a profile's presence *costs* — the
    video road spends real money per turn, capped by the daily ceiling
    set right here — and points it at a render provider. It shipped
    taking neither a token nor a ``Request``, so anybody holding a
    profile id (they ride on printed stickers) could put a profile on
    the video road, lift its ceiling to the hour, or repoint its
    provider, and spend its owner's budget by doing so. Every other
    mutation in this router calls ``require_owner``; this one now does
    too.
    """
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        filming.set_road(profile_id, body.road, body.daily_seconds,
                         film_provider=body.provider)
    except filming.FilmingError as exc:
        raise HTTPException(status_code=400,
                            detail=i18n.raised(exc)) from None
    return {**filming.road_of(profile_id), **filming.budget(profile_id),
            "roads": list(filming.ROADS),
            "providers": [p for p in filming.PROVIDERS if p != "none"]}


@router.get("/video/latest/{profile_id}")
def video_latest(profile_id: str) -> dict:
    """The most recent render for this profile, however it ended.

    What a screen asks on opening, and the reason it has to exist: a
    render outlives the page that started it. The console tells somebody
    "it keeps going without this page open, and appears here when you
    come back" — and coming back only works if there is something to ask.
    Without this the sentence is a promise nothing keeps.

    Answers `{"scene": null}` rather than a 404 when there has never been
    one: no footage is the ordinary case on every road but video, and a
    screen should not have to catch an error to learn it.
    """
    return {"scene": filming.latest(profile_id)}


@router.get("/video/render/{render_id}")
def video_follow(render_id: str) -> dict:
    """Whether a render started by a turn has finished.

    What a screen polls. A settled render is returned as it stands rather
    than asked about again — the service bills per call on some plans,
    and a finished job does not become unfinished.
    """
    got = filming.follow(render_id)
    if got is None:
        raise HTTPException(status_code=404, detail="no such render")
    return got


class Direction(BaseModel):
    surface: str | None = Field(default=None,
                                description="window or fullscreen — where "
                                            "they were when they asked. "
                                            "Recorded, never acted on: both "
                                            "read and write the same row.")
    asked: str = Field(min_length=1, max_length=500,
                       description="What the owner wants changed about how "
                                   "their scenes look, in their own words — "
                                   "\"it's too dark, let's have this on the "
                                   "beach\". Applied, not negotiated with.")


@router.get("/video/direction/{profile_id}")
def video_direction(profile_id: str) -> dict:
    """How this profile's scenes are shot, and what it would be if the
    owner started over."""
    # `default` is what starting over returns to — the profile's own
    # composed sheet, not the stranger's wide shot.
    return {"direction": filming.direction_of(profile_id),
            "default": filming.composed_direction(profile_id),
            "max_length": filming.MAX_DIRECTION}


@router.post("/video/direction/{profile_id}")
def video_direct(profile_id: str, body: Direction) -> dict:
    """Change how the scenes look, in the owner's own words.

    Rewrites the standing direction rather than appending to it, and the
    answer carries `was` so a screen can show what it replaced — an
    amendment nobody can see the effect of is one nobody can undo.
    """
    try:
        return filming.amend(profile_id, body.asked, body.surface)
    except filming.FilmingError as exc:
        raise HTTPException(status_code=400,
                            detail=i18n.raised(exc)) from None


@router.get("/video/direction/{profile_id}/log")
def video_direction_log(profile_id: str, limit: int = 20) -> dict:
    """What was asked of this scene, newest first.

    `surface` says whether the change came from the frame or from full
    screen. Not because the two behave differently — they read and write
    the same row, which is why leaving full screen loses nothing — but
    because "I changed that while it was full screen" is how a person
    remembers doing it.
    """
    return {"log": filming.direction_log(profile_id, limit)}


@router.delete("/video/direction/{profile_id}")
def video_undirect(profile_id: str) -> dict:
    """Back to the default. Every standing thing here has a way out that
    is one press, and this is not the exception."""
    return {"direction": filming.forget_direction(profile_id)}


class Scene(BaseModel):
    prompt: str = Field(min_length=1, max_length=2000,
                        description="What the scene is. Sent to the "
                                    "rendering service as written.")
    seconds: int = Field(default=5, ge=1, le=filming.MAX_SECONDS,
                         description="How long the finished clip runs. It "
                                     "bills by this, and the wait scales "
                                     "with it.")
    shape: str = Field(default="landscape",
                       description="portrait, landscape or square.")
    profile_id: str | None = Field(default=None,
                                   description="Whose standing scene "
                                               "direction to shoot this "
                                               "under. Without one the "
                                               "passage is sent bare.")
    wait: bool = Field(default=False,
                       description="Hold the request open until the render "
                                   "finishes. False — the default — hands "
                                   "back a job to follow, because a render "
                                   "is minutes and a held request is not.")


@router.post("/video/render")
def video_render(body: Scene) -> dict:
    """Render a described scene as video.

    Defaults to NOT waiting. A render takes minutes, and a console that
    holds a request open for one has turned a slow feature into a broken
    one — the job comes back with the quote attached so a screen can say
    how long and let the person decide whether to stay.
    """
    try:
        return filming.render(body.prompt, seconds=body.seconds,
                              shape=body.shape, wait=body.wait,
                              directed_for=body.profile_id)
    except filming.FilmingError as exc:
        raise HTTPException(status_code=400,
                            detail=i18n.raised(exc)) from None




class ForgeFace(BaseModel):
    photo: str = Field(min_length=1,
                       description="The photograph, base64. It is used to "
                                   "build the face and not stored as the "
                                   "upload — what is kept is the head it "
                                   "became.")
    shot: str = Field("face", max_length=10,
                      description="How the photo is framed: face, upper "
                                  "(torso) or full (body).")


@router.post("/profiles/{profile_id}/avatar/forge", status_code=201)
def forge_face(profile_id: str, body: ForgeFace, request: Request) -> dict:
    """A photograph becomes this profile's face — geometry, skin and a
    mouth — on this deployment's own hardware.

    The road the avatar market never was: not an import of somebody
    else's render, but a face made here, from a picture, with morph
    targets a renderer can drive. Ready Player Me was the alternative
    and Netflix closed it; the paid replacements start at eight hundred
    dollars a month. This runs on the box the rest of the stack runs on.

    The likeness is **the owner's own**, and so the AI mark is not
    burned into it: stamping an authentic face as synthetic is the very
    failure the mark exists to prevent, run backwards. What is synthetic
    is this profile speaking through the face, and that credential rides
    the presentation and watermark layers every surface already reads.
    """
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    import base64 as _b64
    try:
        photo = _b64.b64decode(body.photo, validate=True)
    except Exception:
        raise HTTPException(422, i18n.tr_public(
            "the photograph is not valid base64", i18n.DEFAULT)) from None
    try:
        made = avatarforge.from_photo(photo, shot=body.shot,
                                      on_behalf_of=profile_id)
    except avatarforge.ForgeError as exc:
        raise HTTPException(422, i18n.raised(exc)) from None

    # The still and the model are stored as this profile's own media, and
    # the registry row carries both: the portrait as the asset every
    # surface already draws, the `.glb` in the row's variants, so a face
    # that has a body is the same row as one that does not.
    portrait = media.save(profile_id, made["portrait"], name="portrait.png",
                          alt="a portrait built from a photograph")
    model = media.save(profile_id, made["model"], name="head.glb",
                       alt="a head built from a photograph")
    row = avatarreg.mint(
        asset=portrait["url"], source="uploaded", provider="forge",
        label=None, owner_account_id=None, likeness="self",
        basis="built from the owner's own photograph in this deployment's "
              "forge")
    avatarreg.set_variant(row["id"], "model", model["url"])
    avatarreg.claim(row["id"], profile_id)
    return {"registry_id": row["id"], "portrait": portrait["url"],
            "model": model["url"],
            "blendshapes": made["blendshapes"],
            "avatar": avatars.render(profile_id)}


@router.post("/profiles/{profile_id}/avatar/speaking", status_code=201)
def speaking_face(profile_id: str, body: ForgeFace,
                  request: Request) -> dict:
    """The profile's own photograph, given a mouth that moves.

    ## Why this is the door and the head is not

    `/avatar/forge` builds a head, and a head from 478 face points has no
    skull, no hair and no ears. Textured and lit perfectly it is still a
    mask — the field looked at one and said *"that isn't the photo I
    uploaded, that's a white moving skeleton frame"*, which is an exact
    description of a landmark mesh.

        asked     let the avatar speak
        mattered  let it still be them while it does

    So nothing is rebuilt here. The forge measures the picture and hands
    back where the face's points sit, how they join up, and how a mouth
    moves in the picture's own plane. The console lays that over the
    photograph it already has and drives it with the voice already in the
    ear: at rest the mesh is a copy of the picture over the picture and
    cannot be seen, and the only thing that ever moves is a mouth.

    The measurements are stored as a variant on the same registry row the
    portrait rides, so a speaking face is the same face — one record, one
    likeness, one provenance — rather than a second identity for the same
    person.
    """
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    import base64 as _b64
    try:
        photo = _b64.b64decode(body.photo, validate=True)
    except Exception:
        raise HTTPException(422, i18n.tr_public(
            "the photograph is not valid base64", i18n.DEFAULT)) from None
    try:
        made = avatarforge.speech_map(photo, shot=body.shot,
                                      on_behalf_of=profile_id)
    except avatarforge.ForgeError as exc:
        raise HTTPException(422, i18n.raised(exc)) from None

    # The photograph itself becomes the portrait, because it IS the
    # portrait — the whole point of this road is that nothing is redrawn.
    portrait = media.save(profile_id, photo, name="portrait.png",
                          alt="the owner's own photograph")
    measured = media.save(
        profile_id, json.dumps(made).encode("utf-8"),
        name="speaking.txt",
        alt="where this face's points sit, so its mouth can move")
    row = avatarreg.mint(
        asset=portrait["url"], source="uploaded", provider="forge",
        label=None, owner_account_id=None, likeness="self",
        basis="the owner's own photograph, measured in this deployment's "
              "forge so its mouth can move")
    avatarreg.set_variant(row["id"], "speaking", measured["url"])
    avatarreg.claim(row["id"], profile_id)
    return {"registry_id": row["id"], "portrait": portrait["url"],
            "speaking": measured["url"],
            "mouth_shapes": sorted(made.get("shapes") or {}),
            "avatar": avatars.render(profile_id)}


@router.get("/avatars/market")
def avatar_market() -> dict:
    """The import shelf of the avatar deck: avatar systems a person may
    already have a face in, each with how to export it. Imports, not
    integrations — the provider's license governs the avatar, and QRME never
    holds a provider credential."""
    return {"skin_sources": list(avatars.MARKET),
            "note": "export your avatar on the provider's own surface, then "
                    "import the image or link here — the AI badge and the "
                    "likeness record ride on it like any other portrait"}


@router.post("/profiles/{profile_id}/avatar/import", status_code=201)
def import_avatar(profile_id: str, body: AvatarImport,
                  request: Request) -> dict:
    """Owner brings a face from outside the starter collection — their own
    photos, the selfie capture's frames, or an avatar exported from a market
    system — and it becomes the profile's portrait with its provenance
    written onto the record."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        return avatars.import_avatar(
            profile_id, source=body.source, asset=body.asset,
            extra=body.extra, torso=body.torso,
            provider_asset_id=body.provider_asset_id,
            pdi=request.app.state.pdi)
    except ValueError as e:
        raise HTTPException(422, i18n.raised(e))


class ModelConvert(BaseModel):
    model: str = Field(..., description="The .fbx, or the provider's zip"
                                        " with one inside it, base64.")
    name: str | None = Field(default=None, max_length=200,
                             description="The file's own name, so the .glb"
                                         " that comes out keeps it.")


@router.get("/avatars/convert")
def convert_doors() -> dict:
    """Whether an FBX can be converted here, said before anybody uploads.

    The shelf's instructions read one way when the app can do this and
    another when it cannot, and a screen that promises a conversion this
    deployment has no forge for is worse than one that asks for a `.glb`.
    """
    return {"configured": modelshop.configured(),
            "takes": list(modelshop.TAKES),
            "max_bytes": modelshop.MAX_BYTES}


@router.post("/profiles/{profile_id}/avatar/convert", status_code=201)
def convert_model(profile_id: str, body: ModelConvert,
                  request: Request) -> dict:
    """An FBX export in, a stored `.glb` out, ready to import as a face.

        asked     do the conversion in the app
        mattered  the upload door could not even ACCEPT what the provider
                  hands over

    `media.save` proves a file's format from its bytes, and an FBX matches
    nothing it knows — so before this door existed an FBX upload was
    refused as an unrecognized file, and the shelf's answer was a page of
    Blender menus. What comes back is a `.glb` stored the ordinary way,
    which the existing import door then takes like any other asset.

    The counts ride back with it. A conversion that dropped half the
    morph targets would still return a model, and the only place anybody
    would notice is a mouth that no longer moves.
    """
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        data = base64.b64decode(body.model, validate=True)
    except Exception:
        raise HTTPException(422, "the model is not valid base64") from None
    try:
        return modelshop.convert_and_store(profile_id, data, body.name)
    except modelshop.ConversionError as exc:
        raise HTTPException(422, exc.said) from None
    except media.MediaError as exc:
        raise HTTPException(exc.status, exc.message) from None


# -- the avatar registry: one face ledger, three roads in --------------------
# (qrme/avatarreg.py). Every door below is a data operation on the ledger;
# the render pipeline is untouched and every surface keeps reading the one
# shape it always read.

class RegistryClaim(BaseModel):
    registry_id: str = Field(min_length=1, max_length=64)


class Painted(BaseModel):
    direction: str = Field(default="", max_length=300,
                       description="The owner's own direction, added to the "
                                   "house style and the profile's brief.")


class Retire(BaseModel):
    because: str = Field(min_length=1, max_length=300)


@router.get("/avatars/library")
def avatar_library() -> dict:
    """The deployment's shelf, plus the starter collection so the picker
    never empties — the same rule the voice library keeps."""
    return {"shelf": avatarreg.shelf(),
            "starters": avatars.catalog()}


@router.post("/avatars/library", status_code=201,
             dependencies=[Depends(auth.require_signup_key)])
async def stock_library(request: Request, provider: str = "elevenlabs",
                        provider_asset_id: str = "",
                        label: str = "") -> dict:
    """The operator stocks the deployment's shelf — raw image bytes,
    exported once from the provider's own surface (ElevenLabs offers no
    listing API for its avatars; the export is the road). Synthetic by
    definition, so the AI mark is burned at mint."""
    data = await request.body()
    if not data:
        raise HTTPException(422, i18n.tr_public(
            "the upload arrived empty", i18n.DEFAULT))
    return avatarreg.mint(data=data, source="curated_library",
                          provider=provider,
                          provider_asset_id=provider_asset_id or None,
                          label=label or None, likeness="invented")


@router.post("/avatars/library/pull")
def pull_library(request: Request, provider: str = "elevenlabs") -> dict:
    """Fill the deployment shelf from the provider's own catalog — the
    operator's one-button road, honest about the door that isn't open.

    ElevenLabs ships avatars in its studio today and no listing API
    beside them (the voices catalog got /v1/voices; the avatars got a
    gallery). So this door TRIES, and reports what it found: the day the
    provider opens /v1/avatars, this same button fills the shelf,
    provider_asset_id and all. Until then the export road stands —
    download the renders from the studio and stock the shelf by upload —
    and the answer says so in a machine word the console can translate
    rather than a sentence pretending to be data."""
    auth.require_signup_key(request)
    if provider != "elevenlabs":
        raise HTTPException(422, "only elevenlabs is wired for pulling")
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key:
        raise HTTPException(503, i18n.raised(RuntimeError(
            "this deployment has no ELEVENLABS_API_KEY configured — the "
            "binding exists, the engine does not")))
    import json as _json
    import urllib.request as _rq
    try:
        with _rq.urlopen(_rq.Request(
                "https://api.elevenlabs.io/v1/avatars",
                headers={"xi-api-key": key}), timeout=10) as r:
            rows = _json.loads(r.read().decode("utf-8")).get("avatars", [])
    except Exception:
        return {"pulled": 0, "note": "provider_door_closed"}
    minted = 0
    for row in rows:
        url = row.get("image_url") or row.get("preview_url")
        if not url:
            continue
        avatarreg.mint(asset=url, source="curated_library",
                       provider="elevenlabs",
                       provider_asset_id=row.get("avatar_id"),
                       label=row.get("name"), likeness="invented")
        minted += 1
    return {"pulled": minted, "note": "stocked"}


@router.get("/accounts/{account_id}/avatars")
def account_shelf(account_id: str, request: Request) -> dict:
    """Somebody's own shelf. The account's token, nothing else."""
    auth.require(request, "account", account_id)
    return {"shelf": avatarreg.shelf(account_id)}


@router.post("/accounts/{account_id}/avatars", status_code=201)
async def stock_own_shelf(account_id: str, request: Request,
                          likeness: str = "invented",
                          provider: str = "internal",
                          provider_asset_id: str = "",
                          label: str = "") -> dict:
    """A face onto your own shelf — your own provider export, or your own
    photograph. `likeness=self` says it is really you, and an authentic
    photograph is never AI-marked; anything invented is, at mint."""
    auth.require(request, "account", account_id)
    if likeness not in avatarreg.LIKENESS:
        raise HTTPException(422, "likeness must be one of "
                                 + ", ".join(avatarreg.LIKENESS))
    data = await request.body()
    if not data:
        raise HTTPException(422, "the upload arrived empty")
    return avatarreg.mint(data=data, source="uploaded", provider=provider,
                          provider_asset_id=provider_asset_id or None,
                          label=label or None,
                          owner_account_id=account_id, likeness=likeness,
                          store_for=account_id)


@router.post("/profiles/{profile_id}/avatar/claim")
def claim_face(profile_id: str, body: RegistryClaim,
               request: Request) -> dict:
    """Point this profile at a ledger row — the deployment's shelf or
    your own. A retired or disputed face refuses; a takedown reaches
    every claimant at once because this link exists."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        return avatarreg.claim(body.registry_id, profile_id)
    except avatarreg.RowUnavailable as exc:
        raise HTTPException(409, i18n.raised(exc)) from None
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from None


@router.post("/profiles/{profile_id}/avatar/painted", status_code=201)
def paint_face(profile_id: str, body: Painted, request: Request) -> dict:
    """Painted from words — the prompted road (qrme/portraitist.py).

    House style, the profile's own brief, and its age as it is today.
    Fictional profiles only: a real face arrives by photograph and
    recorded grant, never by prompt.

    Who may prompt: the owner always, and — while the profile's
    `guest_styling` switch is on, which it is by default — anyone signed
    in and standing in front of it. The people a profile talks with get
    to dress it; the owner's PATCH flips the switch when they'd rather
    keep the wardrobe to themselves. The deepfake line above is not part
    of the switch: it holds for every prompter including the owner."""
    profile = profile_or_404(profile_id)
    who = auth.principal(request)
    if who != {"role": "owner", "subject_id": profile_id}:
        if who is None:
            raise HTTPException(401, "authentication required")
        if not profile.get("guest_styling", 1):
            raise HTTPException(403, i18n.raised(RuntimeError(
                "the owner keeps this wardrobe closed — only they can "
                "restyle this avatar")))
    if profile["kind"] != "fictional":
        raise HTTPException(403, i18n.raised(RuntimeError(
            "a real person's face is never painted from words — attach a "
            "photograph under a recorded grant instead")))
    try:
        data, prompt, params = portraitist.paint(profile, body.direction)
    except portraitist.PaintingUnavailable as exc:
        raise HTTPException(503, i18n.raised(exc)) from None
    minted = avatarreg.mint(data=data, source="prompted",
                            prompt_text=prompt, generation_params=params,
                            likeness="invented", store_for=profile_id)
    return avatarreg.claim(minted["id"], profile_id)


@router.delete("/avatars/registry/{registry_id}")
def retire_face(registry_id: str, body: Retire, request: Request) -> dict:
    """The takedown, as a data operation: the row keeps its record and
    every profile it was backing falls back to the placeholder. The
    operator's key retires shelf rows; an account retires its own."""
    try:
        row = avatarreg.row(registry_id)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from None
    if row["owner_account_id"] is None:
        auth.require_signup_key(request)
        return avatarreg.retire(registry_id, because=body.because)
    auth.require(request, "account", row["owner_account_id"])
    return avatarreg.retire(registry_id, because=body.because,
                            owner_account_id=row["owner_account_id"])


@router.get("/avatars/briefs")
def list_briefs() -> dict:
    """The starter collection's art direction, generation-ready.

    Public because it is the honest version of "where did these faces come
    from": every starter portrait is an invented person, and the brief that
    produced it says so in its own constraints.
    """
    return {
        "style": avatars.STYLE,
        "briefs": avatars.catalog(),
        # The standing figures, on the same door for the same reason the
        # presentation block rides `render()`: a second route would let a
        # caller hold half the collection's art direction and not know the
        # other half existed. `undrawn` is the honest headline — today it is
        # the whole collection, and a surface that wants bodies should be
        # able to read that rather than discover it one starter at a time.
        "figure_style": skins.FIGURE_STYLE,
        "figures": skins.catalog(),
        "figures_undrawn": skins.missing(),
    }


@router.get("/avatars/briefs/{handle}")
def get_brief(handle: str) -> dict:
    brief = avatars.brief(handle)
    if brief is None:
        raise HTTPException(404, i18n.fill(i18n.NO_PORTRAIT_BRIEF, handle=handle))
    return brief
