"""The feed's endpoints.

Reads are public, for the reason the desk endpoints are: somebody who followed
a shared link has no token and should still be able to see what they were sent.
Nothing here writes.

The 18+ gate is the deployment's existing verified-adult check
(``rated.viewer_is_adult``) rather than a second, weaker one — a rated desk and
the room behind it are **absent** for everybody else rather than blurred, which
is the difference between a gate and a tease.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from .. import feed, rated

router = APIRouter()


@router.get("/feed")
def stream(request: Request, cursor: str | None = None,
           limit: int = feed.PAGE, viewer: str | None = None) -> dict:
    """One page of the public stream.

    ``viewer`` is a profile id when the caller has one and is absent when they
    do not, because a person who arrived from a sticker on a shop window is a
    reader like any other. It is not required and never will be: a feed that
    demanded an account to be looked at would make the public half of this
    product private.
    """
    limit = max(1, min(limit, 50))
    return feed.stream(viewer_profile_id=viewer, cursor=cursor, limit=limit,
                       viewer_adult=rated.viewer_is_adult(request))


@router.get("/feed/{item_id}")
def one(item_id: str, request: Request) -> dict:
    """A single card, for a link somebody was sent.

    404 rather than an empty card when the item is rated and the reader is not
    verified: the existence of a rated item is itself something the age gate
    withholds, and a 403 would announce it.
    """
    got = feed.item(item_id, viewer_adult=rated.viewer_is_adult(request))
    if got is None:
        raise HTTPException(status_code=404, detail="no such feed item")
    return got
