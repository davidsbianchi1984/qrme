"""A profile's front page: what it can do, what it has done, what people said.

Split from `profiles.py` because it is a *visitor's* surface rather than an
owner's, and the auth reads differently: the page itself is public, experience
is owner-only, and a review needs an interactor who has actually been here.
"""

from fastapi import APIRouter, HTTPException, Request

from .. import auth, frontpage, help as help_mod
from ..models import ExperienceSet, HelpAsk, ReviewIn
from .profiles import profile_or_404, require_owner
from .. import i18n

router = APIRouter(tags=["front page"])


@router.get("/profiles/{profile_id}/front")
def get_front_page(profile_id: str, request: Request) -> dict:
    """Everything a visitor's first screen needs, in one call — because the
    caller is a scan page on cellular and five round trips is how a page
    arrives in pieces."""
    profile_or_404(profile_id)
    who = auth.principal(request)
    viewer = who["subject_id"] if who and who["role"] == "interactor" else None
    page = frontpage.front_page(profile_id, viewer)
    if page is None:
        raise HTTPException(404, "no such profile")
    return page


@router.put("/profiles/{profile_id}/experience")
def set_experience(profile_id: str, body: ExperienceSet,
                   request: Request) -> dict:
    """Replace the experience list. Owner only.

    Refused on a profile that depicts a real person unless the rights basis
    covering the persona is on file — an experience entry there is a
    credential asserted on somebody's behalf.
    """
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        entries = frontpage.set_experience(
            profile_id, [e.model_dump() for e in body.entries])
    except frontpage.FrontPageError as exc:
        raise HTTPException(422, i18n.raised(exc))
    return {"profile_id": profile_id, "experience": entries}


@router.get("/profiles/{profile_id}/reviews")
def list_reviews(profile_id: str, request: Request) -> dict:
    profile_or_404(profile_id)
    who = auth.principal(request)
    viewer = who["subject_id"] if who and who["role"] == "interactor" else None
    return {"profile_id": profile_id,
            "rating_summary": frontpage.rating(profile_id),
            "reviews": frontpage.reviews(profile_id, viewer)}


@router.post("/profiles/{profile_id}/reviews", status_code=201)
def leave_review(profile_id: str, body: ReviewIn, request: Request) -> dict:
    """Leave or replace a review. Requires having actually talked to it."""
    profile_or_404(profile_id)
    auth.require(request, "interactor", body.interactor_id)
    try:
        return frontpage.review(profile_id, body.interactor_id, body.rating,
                                body.body)
    except frontpage.FrontPageError as exc:
        raise HTTPException(422, i18n.raised(exc))


@router.get("/help/topics")
def help_topics() -> dict:
    """What the help box can answer, so a UI can offer them rather than
    leaving somebody staring at an empty field."""
    return {"topics": help_mod.topics(), "disclosure": help_mod.DISCLOSURE}


@router.post("/help")
def ask_help(body: HelpAsk) -> dict:
    """The help box that sits on every screen.

    Public on purpose: every screen here can be somebody's first — a beacon
    scan lands a stranger on a profile page — and requiring an account to ask
    "what is this?" would gate the one question that arrives before one exists.

    It writes nothing. There is no path from this endpoint to a change.

    Asking it to *show you around* starts the guided walkthrough here rather
    than handing back a paragraph about tours — and `mode="voice"` renders
    that first step for listening, so somebody who cannot read the screen gets
    the tour itself rather than a link to it.
    """
    return help_mod.ask(body.question, mode=body.mode)
