"""The inbox — the routes.

Both routes are the owner's, and only theirs: an inbox is the record of
what was done *to* this person, which is exactly the kind of list that is
nobody else's to read. The write is a single verb — "I have looked" —
because the inbox is a window, not a to-do list.
"""

from __future__ import annotations

from fastapi import APIRouter, Request

from .. import auth, inbox

router = APIRouter()


@router.get("/profiles/{profile_id}/inbox")
def read_inbox(profile_id: str, request: Request) -> dict:
    auth.require(request, "owner", profile_id)
    return inbox.events(profile_id)


@router.post("/profiles/{profile_id}/inbox/seen")
def mark_seen(profile_id: str, request: Request) -> dict:
    auth.require(request, "owner", profile_id)
    return inbox.mark_seen(profile_id)
