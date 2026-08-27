"""Profile portraits — the visual half of a synthetic identity.

Reads are public for the same reason the watermark endpoint is: a face that
a stranger can see is a face a stranger should be able to check. Every
response carries the AI badge and the likeness record, so a surface cannot
show the picture without also having been handed the disclosure.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from fastapi import APIRouter, Depends, HTTPException, Request

from .. import auth, avatarreg, avatars, portraitist, presentation, skins
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


@router.get("/avatars/market")
def avatar_market() -> dict:
    """The import shelf of the avatar deck: avatar systems a person may
    already have a face in, each with how to export it. Imports, not
    integrations — the provider's license governs the avatar, and QRME never
    holds a provider credential."""
    return {"sources": list(avatars.MARKET),
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
            pdi=request.app.state.pdi)
    except ValueError as e:
        raise HTTPException(422, i18n.raised(e))


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
    recorded grant, never by prompt."""
    profile = profile_or_404(profile_id)
    require_owner(profile_id, request)
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
