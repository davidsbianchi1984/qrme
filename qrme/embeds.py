"""Video posted from somewhere else — YouTube, Vimeo, Twitch and the rest.

People do not only post their own footage. They post a link to a thing they
watched, and the platform is expected to show it in place rather than as a bare
URL. So a wall post can carry a video from another site.

Three decisions make that safe to do here rather than merely possible.

**Nothing is copied.** What is stored is the platform, the video's id on that
platform, and the title the poster typed — never the file, never a scraped
title, never a downloaded thumbnail. Re-hosting somebody else's video is a
copyright problem, and a scraped thumbnail is a copy of an image nobody granted.
The video stays where its owner put it, on the terms its owner agreed to.

**No third-party request until the viewer asks for one.** This is the part that
matters on a platform whose promise is that data does not leave a vault.
A normal embed loads the other site's player as soon as the page renders, which
tells that company you looked — before you decided to. So what renders is a
*facade*: the platform's name, the poster's own words, and a play control, all
served from here. Pressing play is the moment the request happens, and
:func:`facade` says so in words the viewer can read. A privacy promise that
holds only until an embed loads is not one.

**The allowlist is a list, not a pattern.** Anything not on it is refused,
because "looks like a video URL" is how an open redirect becomes a feature. Each
entry knows how to recognise its own links and how to build a watch URL back;
a platform nobody has thought about yet is not assumed harmless.

The age gate is inherited rather than re-judged. A video post is a post, and a
post already carries its author's rating through
:func:`qrme.audience.is_rated` — so an adult profile's video is walled out of an
ordinary feed by the machinery that was already there. What this module adds is
the opposite direction: a platform's *own* rating is not visible from a link, so
nothing here claims a video is suitable. The poster's rating is the only claim
this system is in a position to make, and it is the one it makes.
"""

from __future__ import annotations

import re
from urllib.parse import parse_qs, urlparse

from . import db


class EmbedError(ValueError):
    """A video link that cannot be attached."""


# Each platform: how its links look, and how to build one back. `watch` takes
# the id; `embed` is the player URL a press of play would open. Both are
# constructed from the id rather than kept from the pasted string, which is what
# stops a tracking query, an open redirect or a lookalike host riding along.
PLATFORMS: dict[str, dict] = {
    "youtube": {
        "name": "YouTube",
        "hosts": ("youtube.com", "www.youtube.com", "m.youtube.com",
                  "youtu.be", "www.youtu.be"),
        "id": re.compile(r"^[A-Za-z0-9_-]{11}$"),
        "watch": "https://www.youtube.com/watch?v={id}",
        "embed": "https://www.youtube-nocookie.com/embed/{id}",
    },
    "vimeo": {
        "name": "Vimeo",
        "hosts": ("vimeo.com", "www.vimeo.com", "player.vimeo.com"),
        "id": re.compile(r"^[0-9]{6,12}$"),
        "watch": "https://vimeo.com/{id}",
        "embed": "https://player.vimeo.com/video/{id}",
    },
    "twitch": {
        "name": "Twitch",
        "hosts": ("twitch.tv", "www.twitch.tv", "m.twitch.tv"),
        "id": re.compile(r"^[0-9]{6,12}$"),
        "watch": "https://www.twitch.tv/videos/{id}",
        "embed": "https://player.twitch.tv/?video={id}",
    },
    "dailymotion": {
        "name": "Dailymotion",
        "hosts": ("dailymotion.com", "www.dailymotion.com", "dai.ly"),
        "id": re.compile(r"^[A-Za-z0-9]{6,12}$"),
        "watch": "https://www.dailymotion.com/video/{id}",
        "embed": "https://www.dailymotion.com/embed/video/{id}",
    },
    "rumble": {
        "name": "Rumble",
        "hosts": ("rumble.com", "www.rumble.com"),
        "id": re.compile(r"^[A-Za-z0-9_-]{4,40}$"),
        "watch": "https://rumble.com/{id}.html",
        "embed": "https://rumble.com/embed/{id}/",
    },
}

MAX_TITLE = 120

# The sentence a viewer reads before anything is fetched. Kept as one constant
# because it is a promise, and a promise phrased differently on each surface is
# one somebody can be argued out of.
LEAVING = ("nothing is requested from {name} until you press play — then the "
           "video loads from their servers and they can see that you did")


def _host(url: str) -> str:
    return (urlparse(url).hostname or "").lower()


def _video_id(platform: str, url: str) -> str | None:
    """Pull the id out of a link, per platform, or None if it is not there."""
    parts = urlparse(url)
    path = (parts.path or "").strip("/")
    host = _host(url)

    if platform == "youtube":
        if host.endswith("youtu.be"):
            return path.split("/")[0] or None
        if path.startswith("shorts/") or path.startswith("embed/"):
            return path.split("/")[1] if "/" in path else None
        vs = parse_qs(parts.query or "").get("v")
        return vs[0] if vs else None
    if platform == "twitch":
        # Only a recorded video has a stable id; a channel link points at
        # whatever happens to be live, which is not a thing anybody posted.
        if path.startswith("videos/"):
            return path.split("/")[1] if "/" in path else None
        return None
    if platform == "dailymotion":
        if host == "dai.ly":
            return path.split("/")[0] or None
        if path.startswith("video/"):
            return path.split("/")[1].split("_")[0] if "/" in path else None
        return None
    if platform == "rumble":
        seg = path.split("/")[0]
        return seg[:-5] if seg.endswith(".html") else (seg or None)
    # vimeo, and anything else whose id is simply the first path segment
    seg = path.split("/")[0]
    return seg or None


def parse(url: str) -> dict:
    """Recognise a video link, or refuse it.

    Returns the platform key, its display name, the video id, and canonical
    watch and embed URLs rebuilt from that id — never the pasted string. A link
    on no listed platform is refused by name rather than silently ignored, so
    somebody pasting a URL learns why it did not take.
    """
    url = (url or "").strip()
    if not url:
        raise EmbedError("a video needs a link")
    if not url.lower().startswith(("http://", "https://")):
        raise EmbedError("a video link must be http or https")

    host = _host(url)
    for key, spec in PLATFORMS.items():
        if host in spec["hosts"]:
            vid = _video_id(key, url)
            if not vid or not spec["id"].match(vid):
                raise EmbedError(
                    f"that looks like a {spec['name']} link but there is no "
                    f"video in it")
            return {"platform": key, "platform_name": spec["name"],
                    "video_id": vid,
                    "url": spec["watch"].format(id=vid),
                    "embed_url": spec["embed"].format(id=vid)}
    raise EmbedError(
        "videos can be posted from "
        + ", ".join(s["name"] for s in PLATFORMS.values())
        + f" — {host or 'that link'} is not one of them")


def attach(post_id: str, url: str, title: str = "") -> dict:
    """Hang a video off a post. One per post.

    A new table rather than a column on ``posts``: this schema has no
    migrations, only ``CREATE TABLE IF NOT EXISTS``, so a column added to an
    existing table reaches a fresh database and silently misses every one that
    already exists.
    """
    video = parse(url)
    title = (title or "").strip()
    if len(title) > MAX_TITLE:
        raise EmbedError(f"a video title is at most {MAX_TITLE} characters")

    conn = db.connect()
    if conn.execute("SELECT 1 FROM post_videos WHERE post_id=?",
                    (post_id,)).fetchone():
        raise EmbedError("that post already has a video")
    conn.execute(
        "INSERT INTO post_videos (post_id, platform, video_id, url, title,"
        " created_at) VALUES (?,?,?,?,?,?)",
        (post_id, video["platform"], video["video_id"], video["url"],
         title or None, db.utcnow()))
    conn.commit()
    return facade(post_id)


def facade(post_id: str) -> dict | None:
    """What is drawn before anybody presses play.

    Everything in here is served from this side: the platform's name, the
    poster's own title, and the link. No thumbnail, because fetching one is the
    request this is designed not to make, and storing one is a copy of an image
    nobody granted.
    """
    row = db.connect().execute(
        "SELECT * FROM post_videos WHERE post_id=?", (post_id,)).fetchone()
    return row_facade(row)


def row_facade(row) -> dict | None:
    """The same thing, from a row somebody else already fetched.

    Split out so a page of posts can be hydrated in one query instead of one
    per post — see :func:`qrme.wall._hydrate`. The formatting lives here rather
    than being duplicated at the call site, so there is still exactly one place
    that decides what a facade contains.
    """
    if row is None:
        return None
    spec = PLATFORMS[row["platform"]]
    return {
        "platform": row["platform"],
        "platform_name": spec["name"],
        "video_id": row["video_id"],
        "url": row["url"],
        "embed_url": spec["embed"].format(id=row["video_id"]),
        "title": row["title"],
        # Deliberately absent: a thumbnail. Its absence is the feature.
        "thumbnail": None,
        "loads_on_press": True,
        "note": LEAVING.format(name=spec["name"]),
    }
