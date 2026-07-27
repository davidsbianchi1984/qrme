"""A profile on a screen that stays where it is.

Placing one is **owner-only**, for the same reason placing a beacon is: where a
profile is shown is a decision about the profile, and a screen bolted to a wall
is a beacon with a plug in it.

Reading what a screen shows is **public**, and that is the point rather than an
oversight — a fixture in a corridor displays to whoever walks past, so what it
is displaying cannot be a secret from them. The list of an owner's screens is
not public: that is a list of physical places, the same thing the beacon
listing withholds.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from .. import displays
from ..common import profile_or_404, require_owner

router = APIRouter()


class PlaceIn(BaseModel):
    kind: str
    label: str = Field(min_length=1, max_length=60)
    location: str | None = Field(default=None, max_length=120)
    size: str = "full"
    finish: str = "opaque"
    faces: list[str] | None = None


class FacesIn(BaseModel):
    faces: list[str]


@router.get("/displays/vocabulary")
def vocabulary() -> dict:
    """What a fixed screen can be, and what it may never show.

    Open — it describes the feature. `never` is the part worth publishing: a
    limit nobody can read is a limit nobody can rely on, and every entry is
    something that *is* allowed on the watch or the phone and deliberately is
    not allowed on a wall.
    """
    return displays.vocabulary()


@router.post("/profiles/{profile_id}/displays", status_code=201)
def place(profile_id: str, body: PlaceIn, request: Request) -> dict:
    """Put this profile on a screen somewhere. Owner-only."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        return displays.place(profile_id, body.kind, body.label, body.size,
                              body.finish, body.faces, body.location)
    except displays.DisplayError as exc:
        raise HTTPException(422, str(exc)) from None


@router.get("/profiles/{profile_id}/displays")
def listing(profile_id: str, request: Request) -> dict:
    """Every screen this profile is on. Owner-only.

    A list of physical places associated with a person — the same reason the
    beacon listing is not public.
    """
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    return {"profile_id": profile_id,
            "displays": displays.for_profile(profile_id)}


@router.get("/displays/{display_id}")
def read(display_id: str) -> dict:
    """What this screen is showing. Public by design.

    A fixture in a corridor displays to whoever walks past, so what it is
    displaying cannot be a secret from them — and everything on `FACES` is
    already public anyway. Which is the check: if this route could leak
    something, the wrong thing is on the face list.
    """
    try:
        return displays.read(display_id)
    except displays.DisplayError as exc:
        raise HTTPException(404, str(exc)) from None


@router.put("/displays/{display_id}/faces")
def set_faces(display_id: str, body: FacesIn, request: Request) -> dict:
    """Change what it shows. Owner-only."""
    try:
        current = displays.read(display_id)
    except displays.DisplayError as exc:
        raise HTTPException(404, str(exc)) from None
    require_owner(current["profile_id"], request)
    try:
        return displays.set_faces(display_id, body.faces)
    except displays.DisplayError as exc:
        raise HTTPException(422, str(exc)) from None


@router.delete("/displays/{display_id}")
def take_down(display_id: str, request: Request) -> dict:
    """Take it down. Owner-only — a stranger switching off somebody's lobby
    panel is the beacon pick-up problem with a bigger screen."""
    try:
        current = displays.read(display_id)
    except displays.DisplayError as exc:
        raise HTTPException(404, str(exc)) from None
    require_owner(current["profile_id"], request)
    return displays.take_down(display_id)
