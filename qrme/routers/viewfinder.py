"""Channel 3 — a live view through somebody's camera.

Two-party throughout. A session names a holder and a viewer, and both ids
arrive in a request body, which makes them a **claim** rather than a fact —
so every route that acts on one goes through `require_self` or
`require_one_of`. This repository has already shipped three routers where that
was missing and an anonymous caller could forge both sides of a two-party
agreement; the sweep test that caught it covers these routes too.

The disclosure route is open to the surface's participants rather than to
anybody holding an id. `roommic` learned that the hard way: its disclosure
docstring claimed "readable by anyone in the room" while the code checked
nothing, and a room id travels on printed stickers.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from .. import viewfinder
from ..common import require_one_of, require_self
from .. import i18n

router = APIRouter()


class OpenSession(BaseModel):
    holder_id: str = Field(description="whose camera this is")
    surface: str = Field(description="room | connection | desk | exchange")
    surface_id: str
    subject: str = Field(description="object | place | document | person")
    viewer_kind: str = Field(description="person | profile")
    viewer_id: str
    minutes: int = viewfinder.DEFAULT_MINUTES
    record: bool = False
    bystanders_declared: str | None = None
    note: str | None = None


class CloseSession(BaseModel):
    actor_id: str = Field(description="the holder, or the viewer")


@router.get("/camera/vocabulary")
def vocabulary() -> dict:
    """Subjects, who may watch what, and everything a viewer never gets.

    Public, and the refusals are published by name: a client that knew only
    the allowed combinations would draw a refused one as a missing feature
    rather than a decision.
    """
    return viewfinder.vocabulary()


@router.get("/camera/bystanders/{subject}")
def bystanders(subject: str) -> dict:
    """What this cannot solve, for the subject in question."""
    try:
        return viewfinder.bystander_guidance(subject)
    except viewfinder.ViewfinderError as exc:
        raise HTTPException(404, i18n.raised(exc)) from None


@router.post("/camera/sessions", status_code=201)
def open_session(body: OpenSession, request: Request) -> dict:
    """Start a live view.

    Only the holder may start one. A session opened *for* somebody by somebody
    else would be a camera turned on remotely, which is the thing
    `NEVER["background_start"]` exists to deny.
    """
    require_self(body.holder_id, request)
    try:
        return viewfinder.open_session(
            body.holder_id, body.surface, body.surface_id, body.subject,
            body.viewer_kind, body.viewer_id, body.minutes, body.record,
            body.bystanders_declared, body.note)
    except viewfinder.ViewfinderError as exc:
        raise HTTPException(422, i18n.raised(exc)) from None


@router.get("/camera/sessions/{session_id}")
def read_session(session_id: str, request: Request) -> dict:
    """One session. Either party may read it."""
    try:
        found = viewfinder.session(session_id)
    except viewfinder.ViewfinderError as exc:
        raise HTTPException(404, i18n.raised(exc)) from None
    require_one_of([found["holder_id"], found["viewer_id"]], request)
    return found


@router.post("/camera/sessions/{session_id}/close")
def close_session(session_id: str, body: CloseSession,
                  request: Request) -> dict:
    """End it. Two to open, one to close — see `viewfinder.close`."""
    try:
        found = viewfinder.session(session_id)
    except viewfinder.ViewfinderError as exc:
        raise HTTPException(404, i18n.raised(exc)) from None
    require_self(body.actor_id, request)
    try:
        return viewfinder.close(session_id, body.actor_id)
    except viewfinder.ViewfinderError as exc:
        raise HTTPException(403, i18n.raised(exc)) from None
    finally:
        del found


@router.get("/camera/live/{holder_id}")
def live_for_holder(holder_id: str, request: Request,
                    include_ended: bool = False) -> list[dict]:
    """Every camera this person currently has open.

    Theirs alone. "Which of somebody's cameras are live right now" is not a
    question a third party gets to ask, and it is the whole of what
    `NEVER["silent_run"]` promises the holder.
    """
    require_self(holder_id, request)
    return viewfinder.for_holder(holder_id, include_ended)


@router.get("/camera/disclosure/{surface}/{surface_id}")
def disclosure(surface: str, surface_id: str, request: Request) -> dict:
    """What everybody on this surface is shown.

    Readable by the parties to a live session on it — deliberately not by
    anybody who merely holds the id. A room id rides on printed beacon
    stickers, and "who has a camera live in there, and is it recording" is
    precisely the thing a stranger who scanned a sticker must not be able to
    ask.
    """
    live = viewfinder.live_on(surface, surface_id)
    if not live:
        return viewfinder.disclosure_on(surface, surface_id)
    parties: list[str] = []
    for s in live:
        parties += [s["holder_id"], s["viewer_id"]]
    require_one_of(parties, request)
    return viewfinder.disclosure_on(surface, surface_id)
