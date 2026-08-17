"""When the profile cannot resolve it — endpoints.

Every route here belongs to the **interactor**: it is their emergency, their
waiver and their money. So they take ``require_interactor``, and the profile's
owner reads none of it.

The seal is not enforced in this file. It lives at the last hop in
``qrme/escalation.py``, and these routes only translate what comes back —
because a refusal that lived here is a refusal a second caller walks past.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from .. import escalation
from ..common import interactor_or_404, profile_or_404, require_interactor
from ..models import DialArm, Unresolved

router = APIRouter()


@router.get("/interactors/{interactor_id}/dialer")
def dialer_posture(interactor_id: str, request: Request) -> dict:
    """Whether the press would be answered, and the words that would be signed.

    Readable before arming, deliberately: a person deciding whether to sign
    should be able to read what they would be signing, and a person who has
    signed should be able to re-read it. It also says plainly whether this
    deployment's dialer is sealed, so that is known now rather than discovered
    at the worst moment.
    """
    interactor_or_404(interactor_id)
    require_interactor(interactor_id, request)
    return escalation.armed(interactor_id)


@router.post("/interactors/{interactor_id}/dialer/arm", status_code=201)
def arm_dialer(interactor_id: str, body: DialArm, request: Request) -> dict:
    """Sign the emergency-services charges waiver, ahead of time.

    In calm conditions, over the exact words, with a real signature rather
    than a checkbox — nobody reads a liability paragraph during an emergency.
    """
    interactor_or_404(interactor_id)
    require_interactor(interactor_id, request)
    try:
        return escalation.arm(interactor_id, body.signature_id)
    except escalation.NotArmed as exc:
        raise HTTPException(422, str(exc)) from None


@router.post("/profiles/{profile_id}/unresolved", status_code=201)
def cannot_resolve(profile_id: str, body: Unresolved,
                   request: Request) -> dict:
    """The profile has reached its limit on this matter. Write it down."""
    profile_or_404(profile_id)
    interactor_or_404(body.interactor_id)
    require_interactor(body.interactor_id, request)
    try:
        return escalation.unresolved(profile_id, body.interactor_id,
                                     body.matter)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from None


@router.get("/interactors/{interactor_id}/unresolved")
def my_escalations(interactor_id: str, request: Request) -> list[dict]:
    interactor_or_404(interactor_id)
    require_interactor(interactor_id, request)
    return escalation.for_interactor(interactor_id)


@router.post("/escalations/{escalation_id}/dial")
def dial(escalation_id: str, request: Request,
         interactor_id: str) -> dict:
    """The explicit press.

    While the deployment's dialer is sealed this **always** refuses, and the
    refusal says no call was placed and gives the number to dial. It never
    reports success it cannot back: the rule the beacon-alarm round settled is
    that an alarm claiming help was called must have called it, and the way to
    keep that true here is to never make the claim.

    503 rather than 500: the path is real and the deployment has shut it, which
    is a posture rather than a fault.
    """
    interactor_or_404(interactor_id)
    require_interactor(interactor_id, request)
    try:
        escalation.dial(escalation_id, interactor_id)
    except escalation.Sealed as exc:
        raise HTTPException(503, str(exc)) from None
    except escalation.NotArmed as exc:
        raise HTTPException(403, str(exc)) from None
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from None
    # Unreachable while any deployment is sealed, and left here rather than
    # removed: the day a carrier is configured, this is the only place that
    # may say a call was placed.
    return escalation.get(escalation_id)                    # pragma: no cover
