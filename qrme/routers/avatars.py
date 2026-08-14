"""Profile portraits — the visual half of a synthetic identity.

Reads are public for the same reason the watermark endpoint is: a face that
a stranger can see is a face a stranger should be able to check. Every
response carries the AI badge and the likeness record, so a surface cannot
show the picture without also having been handed the disclosure.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from fastapi import APIRouter, HTTPException, Request

from .. import avatars, presentation
from ..common import profile_or_404, require_owner

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
            raise HTTPException(422, str(exc)) from None
    # An empty string clears the override and hands the question back to the
    # address, which is what an owner who mis-declared once needs.
    if body.presentation_kind is not None:
        try:
            presentation.set_kind(profile_id,
                                  body.presentation_kind.strip() or None)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from None
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
        raise HTTPException(422, str(e))


@router.get("/avatars/briefs")
def list_briefs() -> dict:
    """The starter collection's art direction, generation-ready.

    Public because it is the honest version of "where did these faces come
    from": every starter portrait is an invented person, and the brief that
    produced it says so in its own constraints.
    """
    return {"style": avatars.STYLE, "briefs": avatars.catalog()}


@router.get("/avatars/briefs/{handle}")
def get_brief(handle: str) -> dict:
    brief = avatars.brief(handle)
    if brief is None:
        raise HTTPException(404, f"no portrait brief for @{handle}")
    return brief
