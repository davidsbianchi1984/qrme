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

from .. import db, i18n, overlays
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
    if surface == "desk":
        # A desk is staffed by its owner, and the owner is who may put a face
        # on its stream.
        row = db.connect().execute("SELECT owner_id FROM desks WHERE id=?",
                                   (surface_id,)).fetchone()
        return [row["owner_id"]] if row else []
    if surface == "stream":
        # Your own posted video or live session: the stream id *is* its
        # owner's, so the only person who can put a face on it is its owner.
        return [surface_id]
    return _members(surface, surface_id)


def _present(surface: str, surface_id: str, request: Request) -> str:
    if surface not in overlays.SURFACES:
        raise HTTPException(
            422, i18n.fill(i18n.UNKNOWN_SURFACE, surface=surface,
                           choices=", ".join(overlays.SURFACES)))
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
    # Where the picture behind you came from — required for a `backdrop`,
    # refused on anything that covers a face. A generated scene and a photo of
    # your own kitchen are different claims and get different disclosures.
    source: str | None = None
    # Asked for an imported image, for the same reason as the face question:
    # nothing here can look at a file and know who owns it.
    holds_rights: bool = True


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


@router.get("/desks/{desk_id}/live-person")
def live_person(desk_id: str) -> dict:
    """A desk's badge, and whether somebody on it is wearing something.

    Public, because it is the disclosure — the people it is for are the ones
    watching. Both facts in one payload: **a real person is behind this**, and
    **they are wearing X**. Either half alone is a different and wrong claim,
    so neither is available on its own.

    Read from the desk row and its attestation rather than accepted from a
    client, which is what stops a stream that never earned the badge from
    pasting it on.
    """
    mark = overlays.live_person_mark(desk_id)
    if not mark:
        raise HTTPException(404, "no such desk")
    return mark


@router.post("/places/{surface}/{surface_id}/overlay", status_code=201)
def wear(surface: str, surface_id: str, body: WearIn,
         request: Request) -> dict:
    """Put one on, here. Your own face only.

    A **live desk** may wear one now. Its badge says *a real person is behind
    this*, which stays true of somebody in a mask — a costume is not a
    synthesis — so the badge stands and the overlay is disclosed beside it.
    See `GET /desks/{id}/live-person`.
    """
    if surface in overlays.FORBIDDEN_SURFACES:
        raise HTTPException(422, overlays.FORBIDDEN_SURFACES[surface])
    _present(surface, surface_id, request)
    require_self(body.interactor_id, request)
    try:
        return overlays.wear(body.interactor_id, surface, surface_id,
                             body.kind, body.title, body.asset,
                             body.depicts_real_person, body.source,
                             body.holds_rights)
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
