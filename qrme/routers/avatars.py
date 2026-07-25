"""Profile portraits — the visual half of a synthetic identity.

Reads are public for the same reason the watermark endpoint is: a face that
a stranger can see is a face a stranger should be able to check. Every
response carries the AI badge and the likeness record, so a surface cannot
show the picture without also having been handed the disclosure.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from fastapi import APIRouter, HTTPException, Request

from .. import avatars
from ..common import profile_or_404, require_owner

router = APIRouter()


class AvatarSet(BaseModel):
    asset: str = Field(min_length=1, max_length=500,
                       description="Asset reference or URL of the rendered "
                                   "portrait.")


@router.get("/profiles/{profile_id}/avatar")
def get_avatar(profile_id: str) -> dict:
    """The profile's portrait as it must be displayed — asset, AI badge, and
    whose likeness it is. 2-D, 3-D, VR and AR surfaces all read this."""
    profile_or_404(profile_id)
    return avatars.render(profile_id)


@router.put("/profiles/{profile_id}/avatar")
def set_avatar(profile_id: str, body: AvatarSet, request: Request) -> dict:
    """Owner attaches a rendered portrait."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    return avatars.set_avatar(profile_id, body.asset)


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
