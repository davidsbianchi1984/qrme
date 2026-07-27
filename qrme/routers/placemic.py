"""Channel 2 on the surfaces that are not a room.

A watch party, a live desk's stream, a one-to-one connection — the same lent
wearable, under the same rules, because none of those rules depended on the
surface being a room.

**Membership is checked against the surface's own table**, never taken on
trust. That is the whole of the authorization here: lending is a first-person
act bound to the caller's token (`require_self`), and the disclosure is
readable by everyone present and nobody else. A room's version of this route
shipped with no check at all and answered anybody holding the id — and an id
is not a secret on any of these surfaces either. A party id travels in an
invite, a desk id is printed on a QR sticker.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from .. import db, roommic
from ..auth import principal
from ..common import require_self

router = APIRouter()


class LendIn(BaseModel):
    interactor_id: str
    device: str = "smart_watch"
    mic_type: str = "watch"
    gain: str = roommic.ROOM_GAIN


class TakeBackIn(BaseModel):
    interactor_id: str


def _members(surface: str, surface_id: str) -> list[str]:
    """Who is present, read from the surface's own table.

    Returns the ids that count as "here". An empty list means the surface does
    not exist or nobody is in it, and both answer 404 — a caller who is not a
    member must not be able to tell a real id from an invented one by the
    status code they get back.
    """
    conn = db.connect()
    if surface == "party":
        # `left_at IS NULL` matters: somebody who walked out of the party is
        # not present, and counting them would let a former member keep
        # reading who is wearing a live microphone in a room they left.
        rows = conn.execute(
            "SELECT member_id FROM watch_party_members WHERE party_id=?"
            " AND left_at IS NULL", (surface_id,)).fetchall()
        return [r["member_id"] for r in rows]
    if surface == "desk":
        row = conn.execute("SELECT owner_id FROM desks WHERE id=?",
                           (surface_id,)).fetchone()
        return [row["owner_id"]] if row else []
    if surface == "connection":
        # An ended connection is not a place — the same reason a closed room
        # takes no new grant.
        row = conn.execute(
            "SELECT interactor_a, interactor_b FROM connections"
            " WHERE id=? AND status='active'", (surface_id,)).fetchone()
        return [row["interactor_a"], row["interactor_b"]] if row else []
    return []


def _present(surface: str, surface_id: str, request: Request) -> str:
    if surface not in roommic.PLACES:
        raise HTTPException(
            422, f"unknown surface {surface!r} — one of "
                 f"{', '.join(roommic.PLACES)}"
            + (". A room lends through POST /rooms/{id}/mic"
               if surface == "room" else ""))
    here = _members(surface, surface_id)
    if not here:
        raise HTTPException(404, "no such place")
    who = principal(request)
    if who is None:
        raise HTTPException(401, "authentication required — this is for the "
                                 "people who are here")
    if who["subject_id"] not in here:
        raise HTTPException(403, "you are not here")
    return who["subject_id"]


@router.get("/microphones/places")
def places() -> dict:
    """Where a wearable may be lent besides a room, and the test each passes.

    Open, because it describes the feature. The test is published rather than
    the list alone: **can the other people present be told?** A surface with a
    member list and somewhere to render a disclosure to it qualifies; one
    without both must never be added, whatever else is convenient about it.
    That is the same question that makes `jim/mic.py` refuse speakerphone on a
    call — the other party there is a stranger to this product, so their voice
    could never be part of the bargain.
    """
    return {
        "places": [{"surface": k, "why": v} for k, v in
                   roommic.PLACES.items()],
        "room": "lends through POST /rooms/{id}/mic — its own routes",
        "test": "the other people present must have a member list and a "
                "surface on which to be shown the disclosure",
        "rules": [
            "only a worn or clipped-on microphone, and only your own",
            "always near-field — there are other people here by definition",
            "it keys on your voice and drops the rest",
            "everyone here is shown that you lent it",
            "it ends when the place does",
        ],
    }


@router.post("/places/{surface}/{surface_id}/microphone", status_code=201)
def lend(surface: str, surface_id: str, body: LendIn,
         request: Request) -> dict:
    """Lend the profiles here your wearable. First-person only."""
    _present(surface, surface_id, request)
    require_self(body.interactor_id, request)
    try:
        return roommic.lend_on(surface, surface_id, body.interactor_id,
                               body.device, body.mic_type, body.gain)
    except roommic.RoomMicError as exc:
        raise HTTPException(422, str(exc)) from None


@router.delete("/places/{surface}/{surface_id}/microphone")
def take_back(surface: str, surface_id: str, body: TakeBackIn,
              request: Request) -> dict:
    """Yours to end, alone and at any moment."""
    _present(surface, surface_id, request)
    require_self(body.interactor_id, request)
    try:
        return roommic.take_back_on(surface, surface_id, body.interactor_id)
    except roommic.RoomMicError as exc:
        raise HTTPException(422, str(exc)) from None


@router.get("/places/{surface}/{surface_id}/microphone")
def disclosure(surface: str, surface_id: str, request: Request) -> dict:
    """Who here has lent one — readable by everyone present.

    Not owner-only and not lender-only: the people who need to know a
    microphone is live are the others in the place, and a disclosure only its
    subject can see is not a disclosure.
    """
    _present(surface, surface_id, request)
    return roommic.disclosure_on(surface, surface_id)
