"""The helper dock — the pane in the corner of the app.

Every route here is a **read**, except the one that saves where the owner put
the pane. There is no route that acts on anything the dock displays, and that
is the module's whole safety story rather than an omission to be filled in
later: see `qrme/dock.py` for why a control floating over a live stream is a
mis-tap on somebody's broadcast.

The vocabulary and the routing table are public — they describe the product's
shape, not anybody's data, and the helper needs the routing table to answer
*where do I change my background* for somebody who has not signed in. Anything
keyed to an account is owner-only.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from .. import dock
from ..common import profile_or_404, require_owner
from .. import i18n

router = APIRouter()


class DockConfig(BaseModel):
    corner: str | None = Field(None, description="bottom_right | bottom_left")
    state: str | None = Field(None, description="hidden | handle | open")
    face: str | None = Field(None, description="which face it opens on")
    faces: list[str] | None = Field(
        None, description="the faces this dock will cycle through")


# Registered before `/dock/{profile_id}` so a profile can never be named
# "faces" or "where" and shadow them. The repository has a test that catches
# this class of collision; the ordering here is what it is asserting.
@router.get("/dock/faces")
def vocabulary() -> dict:
    """Everything needed to draw the pane, including what it refuses to cast
    and why. Public — this is the product's shape, not a user's data."""
    return dock.vocabulary()


@router.get("/dock/where/{face}")
def where(face: str) -> dict:
    """The screen that can actually do this face's job.

    The dock is read-only, so every face carries a way out of it. This is the
    same table `help.where_is` answers from, which is what stops the pane and
    the assistant disagreeing about where a feature lives.
    """
    try:
        return dock.route(face)
    except dock.DockError as exc:
        raise HTTPException(404, i18n.raised(exc)) from None


@router.get("/dock/{profile_id}")
def settings(profile_id: str, request: Request,
             surface: str | None = Query(None),
             platform: str = Query(dock.DEFAULT_PLATFORM)) -> dict:
    """Where this account's pane sits, and how it opens *here*.

    `surface` matters: on a surface that is being broadcast the pane opens
    tucked whatever the preference says, because it is inside the capture. The
    preference is returned alongside as `wanted`, so the setting screen and the
    pane cannot disagree about what was chosen.
    """
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        return dock.opens_as(profile_id, surface, platform)
    except dock.DockError as exc:
        raise HTTPException(422, i18n.raised(exc)) from None


@router.put("/dock/{profile_id}")
def configure(profile_id: str, body: DockConfig, request: Request) -> dict:
    """Move it, tuck it, hide it, or change which faces it carries."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        return dock.configure(profile_id, body.corner, body.state, body.face,
                              body.faces)
    except dock.DockError as exc:
        raise HTTPException(422, i18n.raised(exc)) from None


@router.get("/dock/{profile_id}/face/{name}")
def face(profile_id: str, name: str, request: Request,
         surface: str | None = Query(None),
         surface_id: str | None = Query(None)) -> dict:
    """One face, as the pane would draw it.

    Owner-only. The pane reports on the account it belongs to, and "what am I
    currently presenting as" is exactly the question a stranger should not be
    able to ask about somebody else.
    """
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        return dock.face(profile_id, name, surface, surface_id)
    except dock.DockError as exc:
        raise HTTPException(422, i18n.raised(exc)) from None
