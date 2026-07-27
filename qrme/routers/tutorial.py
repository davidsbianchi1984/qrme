"""The guided walkthrough.

Everything here is a **read**. No route in this router writes to anything but
the learner's own progress, and that is the whole safety story: a tutorial that
placed a beacon or sent a message "to show you how" would be acting on somebody's
account before they understood what the account was. Every lesson says what to
tap; none of them taps it.

The walkthrough itself is public — it describes the product, not anybody's
data — and progress is per learner, keyed on whoever asked. There is no
authorization on progress beyond the id the caller supplies, deliberately:
knowing which step of a tutorial somebody is on is not a secret worth a check
that would stop a stranger scanning a beacon from being walked through the thing
they just scanned.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from .. import tutorial

router = APIRouter()


class MarkIn(BaseModel):
    learner_id: str
    lesson: str
    mode: str = "text"


@router.get("/tutorial")
def outline(mode: str = Query("text")) -> dict:
    """The whole walkthrough, chaptered. Public.

    Offered whole as well as step by step, because a guided tour you cannot see
    the shape of is one people leave — and the person most likely to leave is
    the one who already knows half of it.
    """
    try:
        return tutorial.outline(mode)
    except tutorial.TutorialError as exc:
        raise HTTPException(422, str(exc)) from None


@router.get("/tutorial/steps/{key}")
def step(key: str, mode: str = Query("text")) -> dict:
    """One named step, for a screen that wants to explain itself."""
    try:
        return tutorial.step(key, mode)
    except tutorial.TutorialError as exc:
        raise HTTPException(404, str(exc)) from None


@router.get("/tutorial/for-screen/{number}")
def for_screen(number: int, mode: str = Query("text")) -> dict:
    """The lesson covering a given screen.

    What lets the help button on screen 81 say *this is the microphone one*
    rather than opening the tour at the beginning.
    """
    found = tutorial.for_screen(number, mode)
    if found is None:
        raise HTTPException(404, "no lesson covers that screen")
    return found


@router.post("/tutorial/start")
def start(body: MarkIn) -> dict:
    """Begin, or begin again from the top."""
    try:
        return tutorial.start(body.learner_id, body.mode)
    except tutorial.TutorialError as exc:
        raise HTTPException(422, str(exc)) from None


@router.get("/tutorial/progress/{learner_id}")
def progress(learner_id: str, mode: str = Query("text")) -> dict:
    """Where this learner is, and what is next."""
    try:
        return tutorial.where(learner_id, mode)
    except tutorial.TutorialError as exc:
        raise HTTPException(422, str(exc)) from None


@router.post("/tutorial/done")
def mark(body: MarkIn) -> dict:
    """Mark one step done and hand back the next."""
    try:
        return tutorial.mark(body.learner_id, body.lesson, body.mode)
    except tutorial.TutorialError as exc:
        raise HTTPException(404, str(exc)) from None
