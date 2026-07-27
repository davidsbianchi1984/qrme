"""Wearing a character over your own camera.

Two properties shape every route here.

**Wearing one is first-person.** `require_self` binds it to the caller's token
— an overlay somebody else can put on you is not a costume, it is a puppet, and
the person whose face is underneath is the one whose consent matters.

**Seeing who is wearing one is everyone's.** The disclosure is the whole reason
this feature is allowed to exist, so it is readable by every person present. An
overlay whose disclosure only its wearer can see would be a disguise the
platform helped with and then kept quiet about.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from .. import db, overlays
from ..auth import principal
from ..common import require_self
from .placemic import _members

router = APIRouter()


def _here(surface: str, surface_id: str) -> list[str]:
    """Who is present, read from the surface's own table.

    Overlays and microphones do not span the same surfaces — a **room** can
    wear a character and cannot lend through the generic mic path, a **desk**
    is the reverse — so this has its own list rather than borrowing the mic's.
    Where they overlap it defers to `placemic._members`, so "who is in this
    party" has one answer rather than two that drift.
    """
    if surface == "room":
        rows = db.connect().execute(
            "SELECT ref_id FROM room_participants WHERE room_id=?"
            " AND kind='user'", (surface_id,)).fetchall()
        return [r["ref_id"] for r in rows]
    if surface == "stream":
        # Your own posted video or live session: the stream id *is* its
        # owner's, so the only person who can put a face on it is its owner.
        return [surface_id]
    return _members(surface, surface_id)


def _present(surface: str, surface_id: str, request: Request) -> str:
    if surface not in overlays.SURFACES:
        raise HTTPException(
            422, f"unknown surface {surface!r} — one of "
                 f"{', '.join(overlays.SURFACES)}")
    here = _here(surface, surface_id)
    if not here:
        raise HTTPException(404, "no such place")
    who = principal(request)
    if who is None:
        raise HTTPException(401, "authentication required")
    if who["subject_id"] not in here:
        raise HTTPException(403, "you are not here")
    return who["subject_id"]


class WearIn(BaseModel):
    interactor_id: str
    kind: str
    title: str = Field(min_length=1, max_length=80)
    asset: str | None = None
    # Asked rather than guessed: nothing here can look at a file and tell
    # whether the face in it belongs to somebody. Declaring it true is refused,
    # and the declaration is recorded either way — a false one then has a name
    # and a timestamp on it.
    depicts_real_person: bool = False


class TakeOffIn(BaseModel):
    interactor_id: str


@router.get("/overlays/catalogue")
def catalogue() -> dict:
    """What can be worn, where, what is refused, and why.

    Open — it describes the feature, not anybody's face. The refusals are
    published **by name with the reason**, because every one of them is a
    decision and an absent option reads as a gap somebody works around.
    """
    return overlays.catalogue()


@router.post("/places/{surface}/{surface_id}/overlay", status_code=201)
def wear(surface: str, surface_id: str, body: WearIn,
         request: Request) -> dict:
    """Put one on, here. Your own face only."""
    if surface in overlays.FORBIDDEN_SURFACES:
        raise HTTPException(422, overlays.FORBIDDEN_SURFACES[surface])
    _present(surface, surface_id, request)
    require_self(body.interactor_id, request)
    try:
        return overlays.wear(body.interactor_id, surface, surface_id,
                             body.kind, body.title, body.asset,
                             body.depicts_real_person)
    except overlays.OverlayError as exc:
        raise HTTPException(422, str(exc)) from None


@router.delete("/places/{surface}/{surface_id}/overlay")
def take_off(surface: str, surface_id: str, body: TakeOffIn,
             request: Request) -> dict:
    """Take it off. Yours alone, at any moment."""
    _present(surface, surface_id, request)
    require_self(body.interactor_id, request)
    return overlays.take_off(body.interactor_id, surface, surface_id)


@router.get("/places/{surface}/{surface_id}/overlay")
def worn(surface: str, surface_id: str, request: Request) -> dict:
    """Who here is wearing what — readable by everyone present.

    The disclosure is the reason the feature is allowed at all, so it is
    addressed to the people it is about: the ones looking at the face.
    """
    _present(surface, surface_id, request)
    return overlays.worn(surface, surface_id)
