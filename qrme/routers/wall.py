"""The community wall and the For You feed.

Mounted at ``/profiles/{id}/wall`` rather than ``/posts``: ``interaction.py``
already owns that path for composed posts, and shadowing it made this route
return the other one's rows — which looked like a serialisation bug rather than
a collision.

Likes, comments and shares are not here — `post` is a target kind in the
audience layer, so `POST /posts/{id}/like` already works and is the same row
shape as a like on a profile.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from .. import embeds, media as media_mod, wall
from ..common import profile_or_404, require_owner

router = APIRouter()


class PostCreate(BaseModel):
    body: str = Field(min_length=1, max_length=wall.MAX_BODY)
    video_url: str | None = None
    video_title: str = ""
    media_ids: list[str] = Field(default_factory=list, max_length=8)


@router.post("/profiles/{profile_id}/wall", status_code=201)
def create_post(profile_id: str, body: PostCreate, request: Request) -> dict:
    """Publish to the wall. Moderated on the way in; a blocked post comes back
    to its author with the reason and is invisible to everyone else.

    ``video_url`` attaches a video from another platform. The link is stored,
    never the file, and what renders is a facade — no request reaches the other
    platform until a viewer presses play.
    """
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        return wall.publish(profile_id, body.body, video_url=body.video_url,
                            video_title=body.video_title,
                            media_ids=body.media_ids)
    except (wall.WallError, embeds.EmbedError) as exc:
        raise HTTPException(422, str(exc)) from None
    except media_mod.MediaError as exc:
        raise HTTPException(exc.status, exc.message) from None


@router.post("/profiles/{profile_id}/media", status_code=201)
async def upload_media(profile_id: str, request: Request) -> dict:
    """One photo or video, raw in the request body — the user's own pixels.

    Raw rather than multipart on purpose: the console sends the file bytes
    directly, nothing new to depend on, and the kind is read from the bytes
    either way (media.py's whitelist). Authentic media is never AI-marked.
    """
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    data = await request.body()
    try:
        return media_mod.save(profile_id, data)
    except media_mod.MediaError as exc:
        raise HTTPException(exc.status, exc.message) from None


@router.get("/media/limits")
def media_limits() -> dict:
    """Caps and accepted types, published so a client can say so before an
    upload fails rather than after."""
    return media_mod.limits()


@router.get("/videos/platforms")
def platforms() -> dict:
    """Where a video may be posted from, and what is promised about it.

    Published rather than kept internal so a client can offer the list up front
    instead of letting somebody paste a link and find out it was refused.
    """
    return {
        "platforms": [{"key": k, "name": v["name"], "hosts": list(v["hosts"])}
                      for k, v in embeds.PLATFORMS.items()],
        "stored": ["the platform", "the video id", "the title you type"],
        "never_stored": ["the video file", "a scraped title",
                         "a cached thumbnail"],
        "loads_on_press": True,
        "note": embeds.LEAVING.format(name="the platform"),
    }


@router.get("/profiles/{profile_id}/wall")
def list_posts(profile_id: str) -> dict:
    """One profile's wall, newest first."""
    profile_or_404(profile_id)
    return {"profile_id": profile_id, "posts": wall.wall(profile_id)}


@router.get("/profiles/{profile_id}/feed")
def feed(profile_id: str, limit: int = 25, adult: bool = False) -> dict:
    """The For You feed, most relevant first — and why each one is there.

    Ranked on public actions only: friendships, engagement, marketplace tags
    and likes. Never source material, memories, or anything vaulted. The
    weights are returned so the ranking can be argued with rather than merely
    accepted.
    """
    profile_or_404(profile_id)
    return {
        "profile_id": profile_id,
        "posts": wall.for_you(profile_id, limit=limit, adult_ok=adult),
        "ranked_on": ["friends", "profiles you have talked to",
                      "tags you engage with", "likes", "recency"],
        "never_ranked_on": ["source material", "memories", "vaulted data"],
        "weights": {"friend": wall.W_FRIEND, "talked": wall.W_TALKED,
                    "tag": wall.W_TAG, "like": wall.W_LIKES,
                    "like_cap": wall.W_LIKES_CAP},
    }
