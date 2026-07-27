"""A profile's friends list.

Reads are public: a friends list is the part of a profile that says who it
stands with, and a viewer deciding whether to talk to a synthetic profile is
exactly who that is for. Writes are owner-gated, because the list is a claim
about the owner's profile and nobody else gets to make it.

The founder rides at position one on every list — see :mod:`qrme.friends` for
why he is a real, removable row rather than something the renderer draws.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from .. import friends, verification
from ..common import profile_or_404, require_owner

router = APIRouter()


@router.get("/profiles/{profile_id}/verification")
def get_verification(profile_id: str) -> dict:
    """Whether anybody checked the identity behind this profile, and how hard.

    Public, for the same reason the watermark endpoint is: a claim a stranger
    can see is a claim a stranger should be able to check. Always returns the
    level and what it means alongside the badge — "verified" on its own is a
    word, and the level is the fact.
    """
    profile_or_404(profile_id)
    return verification.status(profile_id)


class FriendAdd(BaseModel):
    friend_id: str = Field(min_length=1, max_length=64,
                           description="Profile id to add to the list.")


@router.get("/profiles/{profile_id}/friends")
def list_friends(profile_id: str) -> dict:
    """The list, founder first, then everyone else oldest-first."""
    profile_or_404(profile_id)
    entries = friends.friends_of(profile_id)
    return {
        "profile_id": profile_id,
        "count": len(entries),
        "friends": entries,
        # Said out loud rather than left to be inferred from position, so a
        # client does not have to know the convention to render the badge.
        "founder_handles": list(friends.FOUNDER_HANDLES),
    }


@router.post("/profiles/{profile_id}/friends")
def add_friend(profile_id: str, body: FriendAdd, request: Request) -> dict:
    """Owner adds somebody to the list."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        return friends.befriend(profile_id, body.friend_id)
    except friends.FriendError as exc:
        raise HTTPException(422, str(exc)) from None


@router.delete("/profiles/{profile_id}/friends/{friend_id}")
def remove_friend(profile_id: str, friend_id: str, request: Request) -> dict:
    """Owner removes somebody.

    The founder's two profiles are fixed and refuse with 409 — a product
    decision by the platform's owner, and one the list marks with ``pinned``
    so a client can render those rows without a remove control rather than
    offering one that fails.
    """
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        return friends.unfriend(profile_id, friend_id)
    except friends.PinnedFriend as exc:
        raise HTTPException(409, str(exc)) from None
