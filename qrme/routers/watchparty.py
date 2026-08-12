"""Watching a posted video together, with synthetic profiles in the room.

Mounted at ``/watch-parties``. The two endpoints worth reading before the rest
are ``/context`` and ``/seek``: the first is everything a synthetic profile in
the party is allowed to know — which pointedly does not include the video —
and the second is the host-only control that stops a shared player becoming a
fight over the scrubber.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from .. import db, watchparty
from ..auth import principal
from ..common import require_self

router = APIRouter()


def _fail(exc: Exception) -> HTTPException:
    return HTTPException(422, str(exc))


def _party_or_404(party_id: str) -> dict:
    try:
        return watchparty.get(party_id)
    except watchparty.PartyError as exc:
        raise HTTPException(404, str(exc)) from None


def _require_member(party_id: str, request: Request) -> str:
    """The caller must be in the room. Party chat is a conversation between
    the people watching, not a public timeline attached to a guessable id."""
    _party_or_404(party_id)
    who = principal(request)
    if who is None:
        raise HTTPException(401, "authentication required")
    inside = {m["member_id"] for m in watchparty.members(party_id)}
    if who["subject_id"] not in inside:
        raise HTTPException(403, "you are not in this watch party")
    return who["subject_id"]


def _owns_profile(profile_id: str, subject_id: str) -> bool:
    """Whether this caller holds that profile's owner capability.

    An owner token's subject *is* the profile id — holding the token is the
    capability, and `profiles.owner_id` is the account label it was created
    with rather than anything a token carries. Comparing against `owner_id`
    was the first version of this and it refused the profile's actual owner.
    """
    row = db.connect().execute("SELECT 1 FROM profiles WHERE id=?",
                               (profile_id,)).fetchone()
    return row is not None and profile_id == subject_id


class StartIn(BaseModel):
    post_id: str = ""
    video_url: str = ""
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
def start(body: StartIn, request: Request) -> dict:
    """Open a party around a posted video, or straight from a video link.

    A post-anchored party inherits its author's rating, its moderation
    verdict, and the allowlist check the link faced when it was posted. A
    `video_url` faces the same allowlist on the way in and hangs off the
    party itself — no post is fabricated to hold it. A URL pasted into
    `post_id` is recognised for what it is, because that is the field every
    client's one input box sends.
    """
    require_self(body.host_id, request)
    try:
        return watchparty.start(body.video_url.strip() or body.post_id,
                                body.host_id, body.title)
    except watchparty.PartyError as exc:
        raise _fail(exc) from None


@router.get("/watch-parties/{party_id}")
def read(party_id: str, request: Request) -> dict:
    """Who is in the room and where it has got to — members only."""
    _require_member(party_id, request)
    return watchparty.get(party_id)


@router.post("/watch-parties/{party_id}/members", status_code=201)
def join(party_id: str, body: JoinIn, request: Request) -> dict:
    """Bring in a person or a synthetic profile. Both are listed as what they
    are — `synthetic` travels with every member."""
    _party_or_404(party_id)
    who = principal(request)
    if who is None:
        raise HTTPException(401, "authentication required")
    if body.kind == "profile":
        # Bringing a synthetic profile into a room speaks in its voice, so it
        # is its owner's call and nobody else's.
        if not _owns_profile(body.member_id, who["subject_id"]):
            raise HTTPException(
                403, "only a profile's owner can bring it into a room")
    else:
        require_self(body.member_id, request)
    try:
        return watchparty.join(party_id, body.member_id, body.kind, body.role)
    except watchparty.PartyError as exc:
        raise _fail(exc) from None


@router.delete("/watch-parties/{party_id}/members/{member_id}")
def leave(party_id: str, member_id: str, request: Request) -> dict:
    """Leave, or be removed by the host."""
    party = _party_or_404(party_id)
    who = principal(request)
    if who is None:
        raise HTTPException(401, "authentication required")
    if who["subject_id"] not in (member_id, party["host_id"]) \
            and not _owns_profile(member_id, who["subject_id"]):
        raise HTTPException(403, "that is not yours to remove")
    try:
        return watchparty.leave(party_id, member_id)
    except watchparty.PartyError as exc:
        raise _fail(exc) from None


@router.post("/watch-parties/{party_id}/seek")
def seek(party_id: str, body: SeekIn, request: Request) -> dict:
    """Move the room's position — the host only, and everyone follows.

    This moves a number. It does not press play on anybody's device: each
    viewer's own player still starts when they start it, which is what keeps
    the embed promise from being broken twenty times at once.
    """
    _party_or_404(party_id)
    require_self(body.host_id, request)
    try:
        return watchparty.seek(party_id, body.host_id, body.position_s,
                               body.playing)
    except watchparty.PartyError as exc:
        raise _fail(exc) from None


@router.post("/watch-parties/{party_id}/chat", status_code=201)
def say(party_id: str, body: SayIn, request: Request) -> dict:
    """A line in the party chat, stamped with the position it was said at."""
    _party_or_404(party_id)
    who = principal(request)
    if who is None:
        raise HTTPException(401, "authentication required")
    # A line is either yours, or your profile's — putting words in a third
    # party's mouth is the one thing a chat endpoint must refuse.
    if who["subject_id"] != body.member_id \
            and not _owns_profile(body.member_id, who["subject_id"]):
        raise HTTPException(403, "that is not yours to say")
    try:
        return watchparty.say(party_id, body.member_id, body.body,
                              at_position_s=body.at_position_s)
    except watchparty.PartyError as exc:
        raise _fail(exc) from None


@router.get("/watch-parties/{party_id}/chat")
def chat(party_id: str, request: Request, limit: int = 100) -> dict:
    """The room's conversation — members only."""
    _require_member(party_id, request)
    return {"party_id": party_id, "lines": watchparty.chat(party_id, limit)}


@router.post("/watch-parties/{party_id}/end")
def end(party_id: str, request: Request, body: SeekIn | None = None,
        host_id: str = "") -> dict:
    """Close the party, and with it anything lent inside it. Host only."""
    party = _party_or_404(party_id)
    require_self(party["host_id"], request)
    who = host_id or (body.host_id if body else "") or party["host_id"]
    try:
        return watchparty.end(party_id, who)
    except watchparty.PartyError as exc:
        raise _fail(exc) from None


@router.get("/watch-parties/{party_id}/context")
def context(party_id: str, request: Request) -> dict:
    """Everything a synthetic profile in this party is allowed to know.

    Deliberately small, and explicit about what is missing: no description, no
    transcript, and `you_have_not_seen_it` with the instruction that goes into
    the prompt. A model handed only chat lines will otherwise fill the gap with
    a plausible opinion about footage nobody showed it — which is the most
    ordinary-looking lie this product could tell.
    """
    _require_member(party_id, request)
    return watchparty.prompt_context(party_id)
