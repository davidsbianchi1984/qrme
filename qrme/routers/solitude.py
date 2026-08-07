"""The one place a person can ask how much of their talking here was synthetic.

Scoped to the person and nobody else. There is deliberately **no** route that
lists this across accounts, no route that lets a profile's owner read it about
somebody who talks to their profile, and no moderation view of it — the count
is a fact about one person's own use of the software, and the moment it is
readable by a second party it becomes a tool for the thing it exists to
disclose.

Both routes are pulls. Nothing here fires on a schedule and nothing sends.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .. import solitude

router = APIRouter()


class HandoffBody(BaseModel):
    #: No default. Taking the door and closing it are both decisions, and a
    #: field that defaults to `True` would turn an empty POST into a consent
    #: nobody typed.
    accept: bool


@router.get("/interactors/{interactor_id}/solitude")
def shape(interactor_id: str) -> dict:
    """Counts from this account's own logs, and — above the threshold — a door.

    Answers with the same body whether or not the offer applies, so the
    presence of this route in a client is not itself a signal about the
    person reading it.
    """
    return solitude.shape(interactor_id)


@router.post("/interactors/{interactor_id}/solitude/handoff")
def handoff(interactor_id: str, body: HandoffBody) -> dict:
    """Accept the JIM-mini door, or decline it. Declining is recorded too."""
    try:
        return solitude.handoff(interactor_id, body.accept)
    except solitude.SolitudeError as exc:
        raise HTTPException(status_code=exc.status, detail=exc.message)


@router.get("/interactors/{interactor_id}/solitude/referral")
def referral(interactor_id: str) -> dict:
    """What would travel, readable here before it does.

    A referral somebody cannot look at before it moves is a referral they did
    not really consent to.
    """
    out = solitude.referral(interactor_id)
    if out is None:
        raise HTTPException(status_code=404, detail="no referral was issued")
    return out
