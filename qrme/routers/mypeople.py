"""Your own people, and the briefing that arrives before they do — endpoints.

Both halves belong to the **interactor**, not the profile: these are the
person's own professionals and the person's own material, and a profile's
owner has no business reading either. So every route here takes
``require_interactor`` rather than ``require_owner``, which is the opposite
of most of this package and is the point.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from .. import briefing, mypeople, tasks
from ..common import interactor_or_404, profile_or_404, require_interactor
from ..models import BriefingPreview, PersonAttach

router = APIRouter()


@router.get("/interactors/{interactor_id}/people")
def my_people(interactor_id: str, request: Request,
              area: str | None = None) -> list[dict]:
    """Everybody this person has kept, preferred first inside each area."""
    interactor_or_404(interactor_id)
    require_interactor(interactor_id, request)
    return mypeople.mine(interactor_id, area)


@router.get("/interactors/{interactor_id}/people/for-area")
def people_for_area(interactor_id: str, area: str, request: Request,
                    location: str | None = None, limit: int = 5) -> list[dict]:
    """Who a profile should offer for this area: yours first, then the search.

    Every row says which it is. *Yours* and *found for you* are different
    claims, and somebody about to send their history is entitled to know
    which one they are looking at.
    """
    interactor_or_404(interactor_id)
    require_interactor(interactor_id, request)
    return mypeople.for_area(interactor_id, area, location, limit)


@router.post("/interactors/{interactor_id}/people", status_code=201)
def attach_person(interactor_id: str, body: PersonAttach,
                  request: Request) -> dict:
    """Keep somebody as yours. The area comes off the provider, never off
    this request — see qrme/mypeople.py."""
    interactor_or_404(interactor_id)
    require_interactor(interactor_id, request)
    try:
        return mypeople.attach(interactor_id, body.provider_id, body.note,
                               body.preferred)
    except mypeople.NotYourPerson as exc:
        raise HTTPException(404, str(exc)) from None


@router.post("/interactors/{interactor_id}/people/{provider_id}/prefer")
def prefer_person(interactor_id: str, provider_id: str,
                  request: Request) -> dict:
    """Make this the one a profile reaches for first in their area. The
    others in that area stay yours — a second opinion is still a choice."""
    interactor_or_404(interactor_id)
    require_interactor(interactor_id, request)
    try:
        return mypeople.prefer(interactor_id, provider_id)
    except mypeople.NotYourPerson as exc:
        raise HTTPException(404, str(exc)) from None


@router.delete("/interactors/{interactor_id}/people/{provider_id}")
def detach_person(interactor_id: str, provider_id: str,
                  request: Request) -> dict:
    interactor_or_404(interactor_id)
    require_interactor(interactor_id, request)
    try:
        return mypeople.detach(interactor_id, provider_id)
    except mypeople.NotYourPerson as exc:
        raise HTTPException(404, str(exc)) from None


@router.post("/briefings/preview", status_code=201)
def preview_briefing(body: BriefingPreview, request: Request) -> dict:
    """Exactly what would reach this provider, before anybody is contacted.

    **Nothing is sent here.** The point of the route is that a person can
    read the whole thing first — the attachments counted out loud, the
    specialist named as synthetic, the matter in their own words — and
    decline it while declining is still free.
    """
    interactor = interactor_or_404(body.interactor_id)
    require_interactor(body.interactor_id, request)
    profile = profile_or_404(body.profile_id)
    try:
        person = mypeople._mine_row(body.interactor_id, body.provider_id)
    except mypeople.NotYourPerson:
        raise HTTPException(
            404, "bring somebody into your people before briefing them — a "
                 "file does not travel to a professional nobody chose"
        ) from None
    try:
        package = briefing.assemble(
            interactor, profile, {"name": person["name"], "area": person["area"]},
            body.matter, body.grant_token, pdi=request.app.state.pdi)
    except tasks.NothingGranted as exc:
        raise HTTPException(403, str(exc)) from None
    except briefing.NothingToBrief as exc:
        raise HTTPException(422, str(exc)) from None
    return {"package": package, "reads": briefing.display_text(package)}
