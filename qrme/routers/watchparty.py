"""Watching a posted video together, with synthetic profiles in the room.

Mounted at ``/watch-parties``. The two endpoints worth reading before the rest
are ``/context`` and ``/seek``: the first is everything a synthetic profile in
the party is allowed to know — which pointedly does not include the video —
and the second is the host-only control that stops a shared player becoming a
fight over the scrubber.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .. import watchparty

router = APIRouter()


def _fail(exc: Exception) -> HTTPException:
    return HTTPException(422, str(exc))


class StartIn(BaseModel):
    post_id: str
    host_id: str
    title: str = ""


class JoinIn(BaseModel):
    member_id: str
    kind: str = "person"
    role: str = "guest"


class SeekIn(BaseModel):
    host_id: str
    position_s: int
    playing: bool | None = None


class SayIn(BaseModel):
    member_id: str
    body: str = Field(min_length=1, max_length=watchparty.MAX_LINE)
    at_position_s: int | None = None


@router.post("/watch-parties", status_code=201)
def start(body: StartIn) -> dict:
    """Open a party around a posted video.

    Anchored to the post rather than a raw URL, so the party inherits its
    author's rating, its moderation verdict, and the fact that the link was
    checked against the platform allowlist when it was posted.
    """
    try:
        return watchparty.start(body.post_id, body.host_id, body.title)
    except watchparty.PartyError as exc:
        raise _fail(exc) from None


@router.get("/watch-parties/{party_id}")
def read(party_id: str) -> dict:
    try:
        return watchparty.get(party_id)
    except watchparty.PartyError as exc:
        raise HTTPException(404, str(exc)) from None


@router.post("/watch-parties/{party_id}/members", status_code=201)
def join(party_id: str, body: JoinIn) -> dict:
    """Bring in a person or a synthetic profile. Both are listed as what they
    are — `synthetic` travels with every member."""
    try:
        return watchparty.join(party_id, body.member_id, body.kind, body.role)
    except watchparty.PartyError as exc:
        raise _fail(exc) from None


@router.delete("/watch-parties/{party_id}/members/{member_id}")
def leave(party_id: str, member_id: str) -> dict:
    try:
        return watchparty.leave(party_id, member_id)
    except watchparty.PartyError as exc:
        raise _fail(exc) from None


@router.post("/watch-parties/{party_id}/seek")
def seek(party_id: str, body: SeekIn) -> dict:
    """Move the room's position — the host only, and everyone follows.

    This moves a number. It does not press play on anybody's device: each
    viewer's own player still starts when they start it, which is what keeps
    the embed promise from being broken twenty times at once.
    """
    try:
        return watchparty.seek(party_id, body.host_id, body.position_s,
                               body.playing)
    except watchparty.PartyError as exc:
        raise _fail(exc) from None


@router.post("/watch-parties/{party_id}/chat", status_code=201)
def say(party_id: str, body: SayIn) -> dict:
    """A line in the party chat, stamped with the position it was said at."""
    try:
        return watchparty.say(party_id, body.member_id, body.body,
                              at_position_s=body.at_position_s)
    except watchparty.PartyError as exc:
        raise _fail(exc) from None


@router.get("/watch-parties/{party_id}/chat")
def chat(party_id: str, limit: int = 100) -> dict:
    return {"party_id": party_id, "lines": watchparty.chat(party_id, limit)}


@router.get("/watch-parties/{party_id}/context")
def context(party_id: str) -> dict:
    """Everything a synthetic profile in this party is allowed to know.

    Deliberately small, and explicit about what is missing: no description, no
    transcript, and `you_have_not_seen_it` with the instruction that goes into
    the prompt. A model handed only chat lines will otherwise fill the gap with
    a plausible opinion about footage nobody showed it — which is the most
    ordinary-looking lie this product could tell.
    """
    try:
        return watchparty.prompt_context(party_id)
    except watchparty.PartyError as exc:
        raise HTTPException(404, str(exc)) from None
