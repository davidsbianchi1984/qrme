"""Live desks: the endpoints a real person's storefront answers on.

Reads are public for the same reason a profile card is: someone who scanned a
sticker on a shop counter has no token and should still learn who they have
reached — and, crucially, *that it is a person*. Writes need the desk's own
token, minted once at creation.
"""

from __future__ import annotations

import io

from pydantic import BaseModel, Field

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, Response

from .. import auth, desks, landing, rated

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
    # 18+ stream. Not a separate tier: it puts this desk behind the same
    # verified-adult gate every other rated surface already uses.
    rated: bool = False
    view_style: str = "desk"


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


def _adult(request: Request) -> bool:
    """The deployment's existing verified-adult check. Deliberately reused
    rather than re-implemented: a second gate is a second thing to get wrong,
    and the weaker one always wins."""
    return rated.viewer_is_adult(request)


def _gate_rated(desk_id: str, request: Request) -> None:
    """Refuse a rated desk's non-card surfaces to an unverified caller."""
    card = desks.card(desk_id, viewer_adult=True)
    if card is None:
        raise HTTPException(404, "no such desk")
    if card.get("rated") and not _adult(request):
        raise HTTPException(
            403, "18+ only — present an interactor token whose verified "
                 "birthdate shows 18 or older")


@router.post("/desks", status_code=201)
def open_desk(body: DeskCreate) -> dict:
    """Open a desk. Returns the desk token once, here."""
    try:
        return desks.create(
            owner_id=body.owner_id, display_name=body.display_name,
            trade=body.trade, attestor=body.attestor, basis=body.basis,
            location=body.location, blurb=body.blurb, rated=body.rated,
            view_style=body.view_style)
    except desks.DeskError as exc:
        raise _fail(exc) from exc


@router.get("/desks/{desk_id}")
def desk_card(desk_id: str, request: Request) -> dict:
    """Who this is, whether they are here, and — stated positively — that they
    are a person rather than a synthetic profile.

    A rated stream resolves to an age wall unless the caller is a verified
    adult: existence acknowledged, and nothing else.
    """
    card = desks.card(desk_id, viewer_adult=_adult(request))
    if card is None:
        raise HTTPException(404, "no such desk")
    return card


@router.get("/desks/{desk_id}/view.webp")
def desk_view(desk_id: str, request: Request) -> Response:
    """The camera view of the desk — what a visitor waits in front of.

    Carries **no AI watermark**, deliberately: it is a photograph of a real
    room belonging to a real person, and marking it would be a false statement
    about both. ``no-store`` because a desk view is a moment, not an asset.
    """
    _gate_rated(desk_id, request)
    path = desks.frame_path(desk_id)
    if not path.is_file():
        raise HTTPException(404, "no view available for this desk")
    return Response(path.read_bytes(), media_type="image/webp",
                    headers={"cache-control": "no-store"})


@router.put("/desks/{desk_id}/presence")
def set_presence(desk_id: str, body: PresenceSet, request: Request) -> dict:
    """Step away, come back, or close up."""
    if desks.card(desk_id, viewer_adult=True) is None:
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
    tradesperson's photograph, and the desk view depicts nobody.
    """
    if desks.card(desk_id, viewer_adult=True) is None:
        raise HTTPException(404, "no such desk")
    _require_desk(desk_id, request)
    return desks.set_portrait(desk_id, body.asset)


class CameraSet(BaseModel):
    url: str | None = Field(default=None, max_length=500)


@router.put("/desks/{desk_id}/camera")
def set_camera(desk_id: str, body: CameraSet, request: Request) -> dict:
    """Point the desk at its own camera, or clear it back to the sample view.

    Theirs to set: a camera on a person is not something a platform turns on
    for them.
    """
    if desks.card(desk_id, viewer_adult=True) is None:
        raise HTTPException(404, "no such desk")
    _require_desk(desk_id, request)
    return desks.set_camera(desk_id, body.url)


@router.post("/desks/{desk_id}/bell", status_code=201)
def ring_bell(desk_id: str, body: RingIn, request: Request) -> dict:
    """Ring the bell.

    Public for an ordinary desk: the visitor at an empty chair is exactly the
    person who has no account yet. An 18+ stream is the exception — an
    anonymous ping channel to an adult performer is not something to hand out,
    so it takes the same verified-adult token as everything else there.
    """
    if desks.card(desk_id, viewer_adult=True) is not None:
        _gate_rated(desk_id, request)
    try:
        return desks.ring(desk_id, caller_id=body.caller_id, note=body.note)
    except desks.DeskError as exc:
        if str(exc) == "no such desk":
            raise HTTPException(404, "no such desk") from exc
        raise _fail(exc) from exc


@router.get("/desks/{desk_id}/rings")
def list_rings(desk_id: str, request: Request, pending: bool = False) -> dict:
    """Who rang while they were away."""
    if desks.card(desk_id, viewer_adult=True) is None:
        raise HTTPException(404, "no such desk")
    _require_desk(desk_id, request)
    return {"rings": desks.rings(desk_id, pending_only=pending)}


@router.post("/desks/{desk_id}/rings/{ring_id}/ack")
def ack_ring(desk_id: str, ring_id: str, request: Request) -> dict:
    """Mark a ring as answered."""
    if desks.card(desk_id, viewer_adult=True) is None:
        raise HTTPException(404, "no such desk")
    _require_desk(desk_id, request)
    acked = desks.acknowledge(desk_id, ring_id)
    if acked is None:
        raise HTTPException(404, "no such ring")
    return acked


@router.post("/desks/{desk_id}/join", status_code=201)
def join_stream(desk_id: str, request: Request) -> dict:
    """Join the live stream — the room whoever is watching shares."""
    _gate_rated(desk_id, request)
    try:
        return desks.join(desk_id)
    except desks.DeskError as exc:
        if str(exc) == "no such desk":
            raise HTTPException(404, "no such desk") from exc
        raise _fail(exc) from exc


# --- beacons: the desk as a printed code ----------------------------------

class DeskBeaconCreate(BaseModel):
    label: str = Field(max_length=120)
    location: str | None = Field(default=None, max_length=120)


@router.post("/desks/{desk_id}/beacons", status_code=201)
def place_desk_beacon(desk_id: str, body: DeskBeaconCreate,
                      request: Request) -> dict:
    """Print this desk onto something — the sticker for the shop door.

    Owner-only. Anyone who could place a beacon for a desk they do not hold
    could put a stranger's face and location on a code and stick it anywhere,
    which is a worse outcome than the feature is worth.
    """
    _require_desk(desk_id, request)
    try:
        return desks.place_beacon(desk_id, body.label, body.location)
    except desks.DeskError as exc:
        if str(exc) == "no such desk":
            raise HTTPException(404, "no such desk") from exc
        raise _fail(exc) from exc


@router.get("/desks/{desk_id}/beacons")
def list_desk_beacons(desk_id: str, request: Request) -> dict:
    """Every code printed for this desk, with its scan count."""
    _require_desk(desk_id, request)
    return {"beacons": desks.beacons_for(desk_id)}


@router.delete("/desk-beacons/{beacon_id}")
def pick_up_desk_beacon(beacon_id: str, request: Request) -> dict:
    """Peel the sticker off. The code stops resolving; the desk is untouched."""
    existing = desks.beacon(beacon_id)
    if existing is None:
        raise HTTPException(404, "no such desk beacon")
    _require_desk(existing["desk_id"], request)
    return desks.pick_up_beacon(beacon_id)


@router.get("/desk-beacons/{beacon_id}/qr.svg")
def desk_beacon_qr(beacon_id: str) -> Response:
    """The printable code. Public: it is going on a door."""
    existing = desks.beacon(beacon_id)
    if existing is None:
        raise HTTPException(404, "no such desk beacon")
    import segno

    from ..routers.summon import _public_base

    buf = io.BytesIO()
    segno.make(f"{_public_base()}/d/{beacon_id}", error="m").save(
        buf, kind="svg", scale=8, dark="#0d0a20", light=None)
    return Response(buf.getvalue(), media_type="image/svg+xml")


@router.get("/d/{beacon_id}", response_class=HTMLResponse)
def scan_desk_beacon(beacon_id: str, request: Request) -> HTMLResponse:
    """What a phone's camera app opens when someone scans the sticker.

    Public and tokenless by definition. A rated desk therefore always lands on
    the age wall here — there is no token on a sticker scan that could clear
    it, which is the right answer rather than a gap.
    """
    scanned = desks.scan(beacon_id, viewer_adult=_adult(request))
    if scanned is None:
        return HTMLResponse(landing.gone("desk code"), status_code=404)
    if scanned.get("age_wall"):
        return HTMLResponse(landing.desk_age_wall(), status_code=200)
    return HTMLResponse(landing.desk_page(
        scanned, scanned["beacon"]["location"]))


@router.get("/d/{beacon_id}/card")
def scan_desk_beacon_card(beacon_id: str, request: Request) -> dict:
    """The same scan, as JSON — what the native apps read when their camera
    recognises the code and draws the overlay in place."""
    scanned = desks.scan(beacon_id, viewer_adult=_adult(request))
    if scanned is None:
        raise HTTPException(404, "no such desk beacon")
    return scanned
