"""Lending a skill inside a place two people already share.

Mounted at ``/skill-grants``. Every route names the person acting, because the
asymmetry is the feature: two people to open a grant, either one alone to close
it.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .. import sharing

router = APIRouter()


def _fail(exc: Exception) -> HTTPException:
    return HTTPException(422, str(exc))


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
def offer(body: OfferIn) -> dict:
    """Offer a skill into a shared surface. Nothing is usable until accepted."""
    try:
        return sharing.offer(body.lender_id, body.borrower_id, body.surface,
                             body.surface_id, body.skill_kind, body.skill_ref,
                             body.title, body.note, body.fee)
    except sharing.SharingError as exc:
        raise _fail(exc) from None


@router.get("/skill-grants/{grant_id}")
def read(grant_id: str) -> dict:
    try:
        return sharing.get(grant_id)
    except sharing.SharingError as exc:
        raise HTTPException(404, str(exc)) from None


@router.post("/skill-grants/{grant_id}/accept")
def accept(grant_id: str, body: ActorIn) -> dict:
    """The second half of the consent. Only now is anything usable."""
    try:
        return sharing.accept(grant_id, body.actor_id)
    except sharing.SharingError as exc:
        raise _fail(exc) from None


@router.post("/skill-grants/{grant_id}/decline")
def decline(grant_id: str, body: ActorIn) -> dict:
    try:
        return sharing.decline(grant_id, body.actor_id)
    except sharing.SharingError as exc:
        raise _fail(exc) from None


@router.post("/skill-grants/{grant_id}/close")
def close(grant_id: str, body: ActorIn) -> dict:
    """End it — either side, alone, without the other's agreement.

    Requiring both would mean somebody who has changed their mind needs the
    agreement of the person benefiting, which is exactly when withdrawal has to
    work.
    """
    try:
        return sharing.close(grant_id, body.actor_id, body.reason)
    except sharing.SharingError as exc:
        raise _fail(exc) from None


@router.post("/skill-grants/{grant_id}/use", status_code=201)
def use(grant_id: str, body: UseIn) -> dict:
    """Invoke a lent skill once, and write it down.

    Checked here rather than at grant time, so closing a grant stops the next
    call rather than only preventing new grants. Returns the reference the
    borrower may act through — nothing is installed on their account.
    """
    try:
        return sharing.use(grant_id, body.borrower_id, body.what,
                           body.surface_id)
    except sharing.SharingError as exc:
        raise _fail(exc) from None


@router.get("/skill-grants/{grant_id}/uses")
def uses(grant_id: str, limit: int = 100) -> dict:
    """The lender's log."""
    return {"grant_id": grant_id, "uses": sharing.uses(grant_id, limit)}


# Namespaced rather than `/{surface}/{surface_id}/…`: a two-variable
# prefix matches any three-segment path, which is how `/profiles/{id}/posts`
# once started returning another router's rows.
@router.get("/surfaces/{surface}/{surface_id}/skill-grants")
def in_surface(surface: str, surface_id: str) -> dict:
    """Everything lent in one place — what a room can see about itself."""
    if surface not in sharing.SURFACES:
        raise HTTPException(404, f"no surface {surface!r}")
    return {"surface": surface, "surface_id": surface_id,
            "grants": sharing.in_surface(surface, surface_id)}


@router.get("/people/{person_id}/skill-grants")
def for_person(person_id: str) -> dict:
    """Everything somebody is lending, and everything they are borrowing."""
    return sharing.for_person(person_id)
