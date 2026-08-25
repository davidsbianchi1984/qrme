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

from .. import friends, i18n, verification
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


@router.get("/people")
def find_people(q: str = "") -> dict:
    """Who is here, by the name you already know. Public, like the friends
    list above it, and made of the same already-public rows — see
    :func:`qrme.friends.find` for the two exclusions that matter."""
    try:
        return {"q": (q or "").strip(), "found": friends.find(q)}
    except friends.FriendError as exc:
        raise HTTPException(422, i18n.raised(exc)) from exc


@router.get("/people/browse")
def browse_people() -> dict:
    """Everyone here — the pool and the head count. Public like /people:
    made of rows every profile already shows, with listing on by default
    and the owner's private switch as the door out. See
    :func:`qrme.friends.browse`."""
    return friends.browse()


class ListingSet(BaseModel):
    listed: bool


@router.get("/profiles/{profile_id}/listing")
def get_listing(profile_id: str, request: Request) -> dict:
    """Whether this profile stands in the browse pool. Owner's read — the
    pool itself is the public answer to the same question."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    return friends.listing(profile_id)


@router.put("/profiles/{profile_id}/listing")
def set_listing(profile_id: str, body: ListingSet, request: Request) -> dict:
    """The owner lists the profile, or takes it private — out of the
    browse pool and the name search both, until they come back."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    return friends.set_listing(profile_id, body.listed)


@router.get("/profiles/{profile_id}/friends/suggested")
def suggested(profile_id: str, limit: int = 10) -> dict:
    """People this profile might want to know, and why each one.

    Ranked on the friend graph and shared subjects — the same public signals
    the feed uses. Never source material or memories: an introduction built
    from somebody's private writing would be the platform reading a diary to
    make it.
    """
    profile_or_404(profile_id)
    return {"profile_id": profile_id,
            "suggested": friends.suggestions(profile_id, limit=limit),
            "ranked_on": ["friends in common", "subjects you both work in"],
            "never_ranked_on": ["source material", "memories", "vaulted data"],
            "excluded": "anyone already on your list, in either state — a "
                        "friend you removed is not a suggestion"}


@router.post("/profiles/{profile_id}/friends")
def add_friend(profile_id: str, body: FriendAdd, request: Request) -> dict:
    """Owner adds somebody to the list."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        return friends.befriend(profile_id, body.friend_id)
    except friends.FriendError as exc:
        raise HTTPException(422, i18n.raised(exc)) from None


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
