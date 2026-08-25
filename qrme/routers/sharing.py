"""Lending a skill inside a place two people already share.

Mounted at ``/skill-grants``. Every route names the person acting, because the
asymmetry is the feature: two people to open a grant, either one alone to close
it.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from .. import sharing
from ..auth import principal
from ..common import require_one_of, require_self
from .. import i18n

router = APIRouter()


def _fail(exc: Exception) -> HTTPException:
    return HTTPException(422, str(exc))


def _parties(grant_id: str) -> list[str]:
    """The two people on a grant, or 404. Read before authorizing, so 403 and
    404 cannot be used to probe which grant ids exist."""
    try:
        row = sharing.get(grant_id)
    except sharing.SharingError as exc:
        raise HTTPException(404, i18n.raised(exc)) from None
    return [row["lender_id"], row["borrower_id"]]


class OfferIn(BaseModel):
    lender_id: str
    borrower_id: str
    surface: str
    surface_id: str
    skill_kind: str
    skill_ref: str
    title: str = Field(min_length=1, max_length=160)
    note: str = ""
    fee: float = 0.0


class ActorIn(BaseModel):
    actor_id: str
    reason: str = ""


class UseIn(BaseModel):
    borrower_id: str
    what: str = ""
    surface_id: str | None = None


@router.get("/skill-grants/vocabulary")
def vocabulary() -> dict:
    """Where a skill can be lent, what can be lent, and on what terms.

    There is deliberately no "everywhere" surface and no "my account" one: a
    grant with no place is a permission nobody can see the edges of.
    """
    return {
        "surfaces": [{"key": k, "means": v} for k, v in sharing.SURFACES.items()],
        "skill_kinds": [{"key": k, "means": v}
                        for k, v in sharing.SKILL_KINDS.items()],
        "states": list(sharing.STATES),
        "terms": [
            "two people open a grant; either one alone closes it",
            "the skill is used, never copied — no install, no licence",
            "a grant lives in one place and ends when that place does",
            "every use is written down and visible to the lender",
        ],
    }


@router.post("/skill-grants", status_code=201)
def offer(body: OfferIn, request: Request) -> dict:
    """Offer a skill into a shared surface. Nothing is usable until accepted.

    Only the lender may offer their own skill. Somebody else offering it on
    their behalf is not a loan, it is a forgery with their name on it.
    """
    require_self(body.lender_id, request)
    try:
        return sharing.offer(body.lender_id, body.borrower_id, body.surface,
                             body.surface_id, body.skill_kind, body.skill_ref,
                             body.title, body.note, body.fee)
    except sharing.SharingError as exc:
        raise _fail(exc) from None


@router.get("/skill-grants/{grant_id}")
def read(grant_id: str, request: Request) -> dict:
    """The two people involved only — it names what somebody owns and lends."""
    require_one_of(_parties(grant_id), request)
    return sharing.get(grant_id)


@router.post("/skill-grants/{grant_id}/accept")
def accept(grant_id: str, body: ActorIn, request: Request) -> dict:
    """The second half of the consent. Only now is anything usable.

    Bound to the caller's token: an acceptance somebody else can send is not a
    second consent, it is the first one typed twice.
    """
    _parties(grant_id)
    require_self(body.actor_id, request)
    try:
        return sharing.accept(grant_id, body.actor_id)
    except sharing.SharingError as exc:
        raise _fail(exc) from None


@router.post("/skill-grants/{grant_id}/decline")
def decline(grant_id: str, body: ActorIn, request: Request) -> dict:
    _parties(grant_id)
    require_self(body.actor_id, request)
    try:
        return sharing.decline(grant_id, body.actor_id)
    except sharing.SharingError as exc:
        raise _fail(exc) from None


@router.post("/skill-grants/{grant_id}/close")
def close(grant_id: str, body: ActorIn, request: Request) -> dict:
    """End it — either side, alone, without the other's agreement.

    Requiring both would mean somebody who has changed their mind needs the
    agreement of the person benefiting, which is exactly when withdrawal has to
    work.
    """
    _parties(grant_id)
    require_self(body.actor_id, request)
    try:
        return sharing.close(grant_id, body.actor_id, body.reason)
    except sharing.SharingError as exc:
        raise _fail(exc) from None


@router.post("/skill-grants/{grant_id}/use", status_code=201)
def use(grant_id: str, body: UseIn, request: Request) -> dict:
    """Invoke a lent skill once, and write it down.

    Checked here rather than at grant time, so closing a grant stops the next
    call rather than only preventing new grants. Returns the reference the
    borrower may act through — nothing is installed on their account.
    """
    _parties(grant_id)
    require_self(body.borrower_id, request)
    try:
        return sharing.use(grant_id, body.borrower_id, body.what,
                           body.surface_id)
    except sharing.SharingError as exc:
        raise _fail(exc) from None


@router.get("/skill-grants/{grant_id}/uses")
def uses(grant_id: str, request: Request, limit: int = 100) -> dict:
    """The lender's log — and the borrower's, who is entitled to see what is
    being recorded about them."""
    require_one_of(_parties(grant_id), request)
    return {"grant_id": grant_id, "uses": sharing.uses(grant_id, limit)}


# Namespaced rather than `/{surface}/{surface_id}/…`: a two-variable
# prefix matches any three-segment path, which is how `/profiles/{id}/posts`
# once started returning another router's rows.
@router.get("/surfaces/{surface}/{surface_id}/skill-grants")
def in_surface(surface: str, surface_id: str, request: Request) -> dict:
    """What *you* are lending or borrowing in one place.

    Narrower than it first was. The intent was "what the room can see about
    itself", but there is no room-membership check to hang that on, and without
    one it listed every grant in any surface to anybody who guessed the id —
    who is lending what to whom. Filtered to the caller's own grants until
    membership is something this can actually ask about.
    """
    if surface not in sharing.SURFACES:
        raise HTTPException(404, i18n.fill(i18n.NO_SURFACE_PLAIN, got=repr(surface)))
    who = principal(request)
    if who is None:
        raise HTTPException(401, "authentication required")
    mine = [g for g in sharing.in_surface(surface, surface_id)
            if who["subject_id"] in (g["lender_id"], g["borrower_id"])]
    return {"surface": surface, "surface_id": surface_id, "grants": mine,
            "note": "your own grants in this place — a room-wide view needs a "
                    "membership check that does not exist yet"}


@router.get("/people/{person_id}/skill-grants")
def for_person(person_id: str, request: Request) -> dict:
    """Everything somebody is lending, and everything they are borrowing.
    Themselves only."""
    require_self(person_id, request)
    return sharing.for_person(person_id)
