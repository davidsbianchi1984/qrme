"""Live desks: the endpoints a real person's storefront answers on.

Reads are public for the same reason a profile card is: someone who scanned a
sticker on a shop counter has no token and should still learn who they have
reached — and, crucially, *that it is a person*. Writes need the desk's own
token, minted once at creation.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response

from .. import auth, desks

router = APIRouter()


class DeskCreate(BaseModel):
    owner_id: str = Field(max_length=80)
    display_name: str = Field(max_length=120)
    trade: str = Field(max_length=80)
    # Required, and enforced in desks.create rather than only here: a desk
    # asserts a real person staffs it, and an unattributed assertion is worth
    # less than none.
    attestor: str = Field(max_length=120)
    basis: str = Field(max_length=200)
    location: str | None = Field(default=None, max_length=120)
    blurb: str | None = Field(default=None, max_length=300)


class PresenceSet(BaseModel):
    presence: str


class PortraitSet(BaseModel):
    asset: str | None = Field(default=None, max_length=500)


class RingIn(BaseModel):
    caller_id: str | None = Field(default=None, max_length=80)
    note: str | None = Field(default=None, max_length=200)


def _require_desk(desk_id: str, request: Request) -> None:
    auth.require(request, "desk", desk_id)


def _fail(exc: desks.DeskError):
    return HTTPException(422, str(exc))


@router.post("/desks", status_code=201)
def open_desk(body: DeskCreate) -> dict:
    """Open a desk. Returns the desk token once, here."""
    try:
        return desks.create(
            owner_id=body.owner_id, display_name=body.display_name,
            trade=body.trade, attestor=body.attestor, basis=body.basis,
            location=body.location, blurb=body.blurb)
    except desks.DeskError as exc:
        raise _fail(exc) from exc


@router.get("/desks/{desk_id}")
def desk_card(desk_id: str) -> dict:
    """Who this is, whether they are here, and — stated positively — that they
    are a person rather than a synthetic profile."""
    card = desks.card(desk_id)
    if card is None:
        raise HTTPException(404, "no such desk")
    return card


@router.get("/desks/{desk_id}/view.webp")
def desk_view(desk_id: str) -> Response:
    """The camera view of the desk — what a visitor waits in front of.

    Carries **no AI watermark**, deliberately: it is a photograph of a real
    room belonging to a real person, and marking it would be a false statement
    about both. ``no-store`` because a desk view is a moment, not an asset.
    """
    if desks.card(desk_id) is None:
        raise HTTPException(404, "no such desk")
    path = desks.frame_path(desk_id)
    if not path.is_file():
        raise HTTPException(404, "no view available for this desk")
    return Response(path.read_bytes(), media_type="image/webp",
                    headers={"cache-control": "no-store"})


@router.put("/desks/{desk_id}/presence")
def set_presence(desk_id: str, body: PresenceSet, request: Request) -> dict:
    """Step away, come back, or close up."""
    if desks.card(desk_id) is None:
        raise HTTPException(404, "no such desk")
    _require_desk(desk_id, request)
    try:
        return desks.set_presence(desk_id, body.presence)
    except desks.DeskError as exc:
        raise _fail(exc) from exc


@router.put("/desks/{desk_id}/portrait")
def set_portrait(desk_id: str, body: PortraitSet, request: Request) -> dict:
    """Attach a portrait the desk owner holds the rights to, or clear it.

    Only ever the owner's own doing. QRME does not go looking for a
    tradesperson's photograph, and the placeholder depicts nobody.
    """
    if desks.card(desk_id) is None:
        raise HTTPException(404, "no such desk")
    _require_desk(desk_id, request)
    return desks.set_portrait(desk_id, body.asset)


@router.post("/desks/{desk_id}/bell", status_code=201)
def ring_bell(desk_id: str, body: RingIn) -> dict:
    """Ring the bell. Public: a visitor at an unattended desk is exactly the
    person who has no account yet."""
    try:
        return desks.ring(desk_id, caller_id=body.caller_id, note=body.note)
    except desks.DeskError as exc:
        if str(exc) == "no such desk":
            raise HTTPException(404, "no such desk") from exc
        raise _fail(exc) from exc


@router.get("/desks/{desk_id}/rings")
def list_rings(desk_id: str, request: Request, pending: bool = False) -> dict:
    """Who rang while they were away."""
    if desks.card(desk_id) is None:
        raise HTTPException(404, "no such desk")
    _require_desk(desk_id, request)
    return {"rings": desks.rings(desk_id, pending_only=pending)}


@router.post("/desks/{desk_id}/rings/{ring_id}/ack")
def ack_ring(desk_id: str, ring_id: str, request: Request) -> dict:
    """Mark a ring as answered."""
    if desks.card(desk_id) is None:
        raise HTTPException(404, "no such desk")
    _require_desk(desk_id, request)
    acked = desks.acknowledge(desk_id, ring_id)
    if acked is None:
        raise HTTPException(404, "no such ring")
    return acked
