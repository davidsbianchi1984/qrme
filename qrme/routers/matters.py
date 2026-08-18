"""Somebody's matter — endpoints.

The remit these serve is written out in :mod:`qrme.matters`. Three things
about the routes themselves:

**Raising takes no account.** ``POST /matters`` accepts an anonymous caller on
purpose, because the person whose matter is *I cannot sign in* is precisely
the person an authenticated support door is closed to. What comes back to them
is a claim, once.

**The claim travels in a header, never in the path or the query.** A query
string is written to the access log of every proxy it passes, and this one
opens somebody's account complaint. ``X-Matter-Claim`` is optional — a
signed-in raiser is found by who they are — and every client that has a door
here sends it.

**The queue route is declared before the id route.** ``/matters/queue`` and
``/matters/{matter_id}`` are the same shape to a router that matches in
declaration order, and the wrong order gives a reviewer a 404 for a matter
called "queue" rather than the queue.
"""

from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException, Request

from .. import auth, i18n, matters
from ..models import MatterRaise, MatterSettle, MatterStep

router = APIRouter()


def _raiser(request: Request) -> str:
    who = auth.principal(request)
    return f"{who['role']}:{who['subject_id']}" if who else "anonymous"


def _refuse(exc: matters.MatterError) -> HTTPException:
    return HTTPException(404, i18n.NO_SUCH_MATTER) \
        if isinstance(exc, matters.NoSuchMatter) else HTTPException(422,
                                                                    str(exc))


@router.post("/matters", status_code=201)
def raise_matter(body: MatterRaise, request: Request) -> dict:
    """Say what is wrong. Answered here and now if the help box knows it."""
    if body.concerns not in matters.CONCERNS:
        raise HTTPException(422, i18n.fill(
            i18n.MUST_BE_ONE_OF, field="concerns",
            choices=", ".join(matters.CONCERNS)))
    if not (body.trouble or "").strip():
        raise HTTPException(422, i18n.MATTER_NEEDS_WORDS)
    return matters.raise_it(body.trouble, body.concerns, _raiser(request))


@router.get("/matters")
def my_matters(request: Request) -> dict:
    """Everything the caller raised. Empty for a caller with no account —
    an anonymous matter is reachable by its claim and by nothing else."""
    return {"my_matters": matters.mine(_raiser(request)),
            "concerns": list(matters.CONCERNS),
            "standings": list(matters.STANDINGS)}


@router.get("/matters/queue")
def matter_queue(request: Request, standing: str = "") -> dict:
    """Everything unsettled, oldest first — for whoever answers them.

    Behind the reviewer gate, which fails closed. This is not the failure map:
    that is counters with nobody in them, and these are people's own words
    about their own accounts.
    """
    auth.require_reviewer(request)
    if standing and standing not in matters.STANDINGS:
        raise HTTPException(422, i18n.fill(
            i18n.MUST_BE_ONE_OF, field="standing",
            choices=", ".join(matters.STANDINGS)))
    return {"unsettled": matters.queue(standing), "standing": standing,
            "standings": list(matters.STANDINGS)}


@router.get("/matters/{matter_id}")
def read_matter(matter_id: str, request: Request,
                claim: str = Header("", alias="X-Matter-Claim")) -> dict:
    """One matter, for the person whose matter it is."""
    try:
        return matters.read(matter_id, _raiser(request), claim)
    except matters.MatterError as exc:
        raise _refuse(exc) from exc


@router.post("/matters/{matter_id}/take")
def take_matter(matter_id: str, request: Request) -> dict:
    """A person has picked it up, and the raiser can see that they have."""
    auth.require_reviewer(request)
    try:
        return matters.took_it(matter_id)
    except matters.MatterError as exc:
        raise _refuse(exc) from exc


@router.post("/matters/{matter_id}/used")
def record_step(matter_id: str, body: MatterStep, request: Request) -> dict:
    """Write down that one of the roster's powers was used on this matter.

    Recorded here, exercised behind its own door in ``qrme.privileges``. A
    support record that could also spend somebody's grants would be a second
    door onto every power in that roster.
    """
    auth.require_reviewer(request)
    if body.did not in matters.STEPS:
        raise HTTPException(422, i18n.fill(
            i18n.MUST_BE_ONE_OF, field="did",
            choices=", ".join(matters.STEPS)))
    try:
        return matters.used(matter_id, body.did, body.note)
    except matters.MatterError as exc:
        raise _refuse(exc) from exc


@router.post("/matters/{matter_id}/not-it")
def reject_answer(matter_id: str, request: Request,
                  claim: str = Header("", alias="X-Matter-Claim")) -> dict:
    """The raiser says the answer waiting on it was not the answer.

    Theirs to press and nobody else's, so it takes the same reading check as
    the matter itself rather than the reviewer gate.
    """
    try:
        matters.read(matter_id, _raiser(request), claim)
        return matters.not_it(matter_id)
    except matters.MatterError as exc:
        raise _refuse(exc) from exc


@router.post("/matters/{matter_id}/settle")
def settle_matter(matter_id: str, body: MatterSettle, request: Request,
                  claim: str = Header("", alias="X-Matter-Claim")) -> dict:
    """Settle it, saying who settled it.

    The raiser may settle their own — they were handed a model's sentence, or
    they worked it out, or it stopped mattering — and that is recorded as
    ``the_person`` rather than flattened into *closed*, because a queue that
    cannot tell the two apart cannot tell whether anybody is being helped.
    """
    try:
        seen = matters.read(matter_id, _raiser(request), claim)
        # The raiser may say it was the answer the help box offered. Nothing
        # else can put `help` there: a keyword deciding that a matter is over
        # is the defect this module was reshaped around.
        by = "help" if (body.helped and seen["standing"] == "answered") \
            else "the_person"
    except matters.MatterError:
        auth.require_reviewer(request)
        by = "a_person"
    if not (body.answer or "").strip():
        raise HTTPException(422, i18n.MATTER_NEEDS_AN_ANSWER)
    try:
        return matters.settle(matter_id, body.answer, by)
    except matters.MatterError as exc:
        raise _refuse(exc) from exc
