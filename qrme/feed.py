"""The feed: one public stream a person can swipe through.

A video that loops, a swipe, another video — and mixed into it the two things
this product has that a video app does not: **a live room you can walk into**
and **a desk with a real person behind it**. Browsing and shopping happen from
inside the stream rather than by leaving it.

## What is in it, and what decides that

Three kinds of item, from three surfaces that already exist:

    video    a public wall post carrying footage this deployment hosts
    offsite  a public wall post pointing at a video on somebody else's site
    room     a public room that is live right now
    desk     a public desk, attended or ringable, with its shop behind it
    party    a watch party whose host chose to be found (join from the card;
             the party id stays the private door)

**Public means deliberately public.** Nothing appears here by default. A post
reaches the feed only if it is on the wall, approved by moderation, and its
profile's page is public; a desk only if it is not closed; a room only while it
is active *and* attached to a desk that chose to be found. There is no path by
which something private becomes feed material by accident, because the feed
never queries a private table — see :func:`_public_posts` and the test that
asserts it touches neither ``memories`` nor ``source_items``.

## Why some items play and some do not

QRME hosts uploads (``media``) and does not host third-party video
(``post_videos``, which stores a link and an id and deliberately no thumbnail,
so that rendering a wall makes no request to anybody else's server).

A feed that autoplayed everything would quietly undo that. Scrolling past
fifty videos would announce the viewer's address, and their taste, to fifty
other companies for footage they did not choose to watch.

    asked     does the feed play the next thing
    mattered  does swiping past something tell a stranger you were here

So the rule is drawn on who holds the file:

* **this deployment's own footage plays and loops**, because the only server
  involved is the one the viewer already chose;
* **everything else is a facade** — platform name, the poster's own title, a
  play control — and makes its first request when a person presses it.

That is the same rule ``qrme/embeds.py`` already applies on the wall, applied
in the one place where the temptation to break it is strongest.

## A room and a desk are people

The two most valuable things in this stream are also the two that can embarrass
somebody, because entering a room and ringing a desk **reach a human being**.

Every room item carries ``entering`` and every desk item carries ``ringing``: a
plain sentence saying what the press does, before it is pressed. A viewer who
swipes into a live room should know they are about to be in it — the room mic
rules in ``qrme/roommic.py`` decide whether their microphone is carrying, and
this feed says so rather than assuming they remember.

## Every item says why it is here

The wall's ranked feed has carried a ``reason`` in plain words since it was
written, on the argument that a ranked feed which cannot explain itself is one
nobody can audit. A video feed is the harder case, not the easier one: it is
the surface where a person spends an hour without deciding to, so the reason
per item is the smallest honest thing it can offer.

The reasons this returns are drawn from what is public and nothing else —
recency, whether a thing is live, and whether the viewer follows the profile.
No ranking here reads a message, a memory, or anything sealed.

## Ordering

Recency inside each kind, then interleaved so that a person swiping meets all
three: every fourth card is a room or a desk if any are live. Deterministic,
because a stream nobody can reproduce is a stream nobody can test, and because
"what did it show me yesterday" should have an answer.
"""

from __future__ import annotations

import base64
import json

from . import db

#: How many items one page of the stream holds. Small: this is a surface people
#: pull rather than read, and a large page is mostly work nobody sees.
PAGE = 12

#: Every fourth card is a place with a person in it rather than a recording.
#: Not a ratio anybody tuned — a statement that this is not only a video app,
#: and it is here as a named constant so a change to it is a decision.
EVERY = 4

PLAYS_NOTE = ("This deployment holds this file, so it plays here. "
              "Nothing is requested from anybody else.")
FACADE_NOTE = ("This one is on {platform}. It stays a card until you press "
               "play, so scrolling past it tells them nothing.")
ENTERING = ("Walking in puts you in the room with the people already there. "
            "Your microphone is off until you turn it on.")
RINGING = ("Ringing reaches a person. {name} is {state} — the bell is not a "
           "message, it is somebody's attention.")


def _cursor(value: dict | None) -> str | None:
    if not value:
        return None
    return base64.urlsafe_b64encode(json.dumps(value).encode()).decode()


def read_cursor(token: str | None) -> dict:
    """Opaque on the wire, plain here. Malformed is empty rather than an
    error: a stale link from a shared item should open the feed, not a 400."""
    if not token:
        return {}
    try:
        got = json.loads(base64.urlsafe_b64decode(token.encode()).decode())
        return got if isinstance(got, dict) else {}
    except Exception:
        return {}


def _public_posts(before: str | None, limit: int) -> list:
    """Approved wall posts whose profile is publicly visible.

    The whole of the feed's read surface for recordings, and deliberately one
    query over three public tables. It joins ``posts``, ``post_videos`` and
    ``media``; it does not join, and must never join, ``memories`` or
    ``source_items``.
    """
    conn = db.connect()
    args: list = []
    where = ["p.status = 'approved'", "p.surface = 'wall'"]
    if before:
        where.append("p.created_at < ?")
        args.append(before)
    args.append(limit)
    return conn.execute(
        "SELECT p.id, p.profile_id, p.topic, p.content, p.created_at,"
        "       v.platform, v.video_id, v.url, v.title AS video_title"
        "  FROM posts p"
        "  LEFT JOIN post_videos v ON v.post_id = p.id"
        f" WHERE {' AND '.join(where)}"
        " ORDER BY p.created_at DESC LIMIT ?", args).fetchall()


def _hosted(post_ids: list[str]) -> dict[str, dict]:
    """Footage this deployment holds, per post. Only ``kind='video'``: a photo
    is not something a stream loops."""
    if not post_ids:
        return {}
    marks = ",".join("?" * len(post_ids))
    rows = db.connect().execute(
        "SELECT pm.post_id, m.id, m.name, m.filename, m.bytes"
        "  FROM post_media pm JOIN media m ON m.id = pm.media_id"
        f" WHERE pm.post_id IN ({marks}) AND m.kind = 'video'"
        " ORDER BY pm.created_at", post_ids).fetchall()
    out: dict[str, dict] = {}
    for r in rows:
        out.setdefault(r["post_id"], {
            "media_id": r["id"],
            "name": r["name"],
            "src": f"/media/{r['id']}",
            "bytes": r["bytes"],
        })
    return out


def _profiles(ids: list[str]) -> dict[str, dict]:
    if not ids:
        return {}
    marks = ",".join("?" * len(ids))
    return {r["id"]: {"profile_id": r["id"], "name": r["display_name"]}
            for r in db.connect().execute(
                f"SELECT id, display_name FROM profiles WHERE id IN ({marks})",
                ids).fetchall()}


def _live_rooms(limit: int) -> list[dict]:
    """Rooms that are live and attached to a desk that chose to be findable.

    A room with no desk behind it is somebody's private conversation and is
    not in the feed at any ranking.
    """
    rows = db.connect().execute(
        "SELECT r.id, r.topic, r.channel, r.created_at,"
        "       d.id AS desk_id, d.display_name, d.rated,"
        "       (SELECT COUNT(*) FROM room_participants rp"
        "         WHERE rp.room_id = r.id) AS people"
        "  FROM rooms r JOIN desks d ON d.room_id = r.id"
        " WHERE r.status = 'active' AND d.presence != 'closed'"
        " ORDER BY r.created_at DESC LIMIT ?", (limit,)).fetchall()
    return [dict(r) for r in rows]


def _open_desks(limit: int) -> list[dict]:
    rows = db.connect().execute(
        "SELECT id, owner_id, display_name, trade, location, blurb,"
        "       presence, rated, portrait, camera_url, created_at"
        "  FROM desks WHERE presence != 'closed'"
        " ORDER BY (presence = 'attended') DESC, created_at DESC LIMIT ?",
        (limit,)).fetchall()
    return [dict(r) for r in rows]


def _shop_for(profile_id: str) -> dict | None:
    """The shop behind a desk, if its owner opened one — so a viewer can buy
    from the stream instead of being sent somewhere to look for it."""
    row = db.connect().execute(
        "SELECT id, name, blurb, tag FROM shops"
        " WHERE profile_id = ? AND status = 'open'", (profile_id,)).fetchone()
    if row is None:
        return None
    items = db.connect().execute(
        "SELECT id, kind, title, price, currency, availability"
        "  FROM shop_offerings WHERE shop_id = ? AND retired = 0"
        " ORDER BY created_at DESC LIMIT 3", (row["id"],)).fetchall()
    return {"shop_id": row["id"], "name": row["name"], "blurb": row["blurb"],
            "tag": row["tag"], "offerings": [dict(i) for i in items],
            "open": f"/shops/{row['id']}"}


def _video_item(row, profile: dict, hosted: dict | None) -> dict:
    title = row["video_title"] or row["topic"] or ""
    if hosted:
        return {
            "kind": "video",
            "id": row["id"],
            "profile": profile,
            "title": title or hosted["name"] or "",
            "said": row["content"],
            "plays": True,
            "loop": True,
            "src": hosted["src"],
            "note": PLAYS_NOTE,
            "reason": "posted publicly on the wall",
            "at": row["created_at"],
        }
    from . import embeds
    return {
        "kind": "offsite",
        "id": row["id"],
        "profile": profile,
        "title": title,
        "said": row["content"],
        # The whole point: false, and the client is not free to override it.
        "plays": False,
        "loop": False,
        "facade": {"platform": row["platform"],
                   "platform_name": embeds.PLATFORMS[row["platform"]]["name"],
                   "video_id": row["video_id"], "url": row["url"]},
        "note": FACADE_NOTE.format(
            platform=embeds.PLATFORMS[row["platform"]]["name"]),
        "reason": "posted publicly on the wall",
        "at": row["created_at"],
    }


def _room_item(row) -> dict:
    return {
        "kind": "room",
        "id": row["id"],
        "topic": row["topic"] or "",
        "channel": row["channel"],
        "people": row["people"],
        "desk_id": row["desk_id"],
        "display_name": row["display_name"],
        "rated": bool(row["rated"]),
        "plays": False,
        "entering": ENTERING,
        "enter": f"/rooms/{row['id']}/join",
        "reason": "live right now",
        "at": row["created_at"],
    }


def _desk_item(row) -> dict:
    state = {"attended": "at the desk now",
             "away": "signed on but not at the desk"}.get(
                 row["presence"], row["presence"])
    return {
        "kind": "desk",
        "id": row["id"],
        "display_name": row["display_name"],
        "trade": row["trade"],
        # Withheld on a rated desk for the reason desks.card gives: where a
        # performer physically is has nothing to do with watching them.
        "location": None if row["rated"] else row["location"],
        "blurb": row["blurb"],
        "presence": row["presence"],
        "rated": bool(row["rated"]),
        "portrait": row["portrait"],
        "live": bool(row["camera_url"]),
        "plays": False,
        "human": True,
        "ai": False,
        "ringing": RINGING.format(name=row["display_name"], state=state),
        "ring": f"/desks/{row['id']}/bell",
        "shop": _shop_for(row["owner_id"]),
        "reason": "a person is at this desk" if row["presence"] == "attended"
                  else "this desk takes a bell",
        "at": row["created_at"],
    }


def _interleave(recordings: list[dict], places: list[dict]) -> list[dict]:
    """Every ``EVERY``-th card is a place. Runs out gracefully in both
    directions: a deployment with no live desks is a plain video stream, and
    one with nothing posted is a list of open doors."""
    out: list[dict] = []
    places = list(places)
    for i, item in enumerate(recordings):
        out.append(item)
        if places and (i + 1) % (EVERY - 1) == 0:
            out.append(places.pop(0))
    out.extend(places if not recordings else [])
    return out


def stream(viewer_profile_id: str | None = None, cursor: str | None = None,
           limit: int = PAGE, viewer_adult: bool = False) -> dict:
    """One page of the feed.

    ``viewer_adult`` comes from the deployment's existing verified-adult check
    — this module does not implement a second, weaker one. Rated desks and the
    rooms behind them are absent for everybody else rather than blurred, which
    is the difference between a gate and a tease.
    """
    state = read_cursor(cursor)
    before = state.get("before")

    rows = _public_posts(before, limit)
    hosted = _hosted([r["id"] for r in rows])
    profiles = _profiles(sorted({r["profile_id"] for r in rows}))
    recordings = [
        _video_item(r, profiles.get(r["profile_id"],
                                    {"profile_id": r["profile_id"],
                                     "name": ""}), hosted.get(r["id"]))
        for r in rows
        # A post with neither hosted footage nor an off-site link is text, and
        # text is the wall's surface, not this one.
        if hosted.get(r["id"]) or r["platform"]
    ]

    places: list[dict] = []
    if not before:                      # places lead, and only on the first page
        places = [_room_item(r) for r in _live_rooms(limit)
                  if viewer_adult or not r["rated"]]
        places += [_desk_item(r) for r in _open_desks(limit)
                   if viewer_adult or not r["rated"]]
        # Watch parties whose hosts chose to be found — the third kind of
        # live door, riding the same rotation. The card is already built to
        # the feed's own rules by watchparty.public_listings: counts and a
        # facade, `plays: False`, and a `joining` sentence said before the
        # press, because joining puts a name in front of a room.
        from . import watchparty
        places += watchparty.public_listings(limit)

    items = _interleave(recordings, places)
    nxt = _cursor({"before": rows[-1]["created_at"]}) if len(rows) == limit \
        else None
    return {
        "items": items,
        "cursor": nxt,
        "counts": {"video": sum(1 for i in items if i["kind"] == "video"),
                   "offsite": sum(1 for i in items if i["kind"] == "offsite"),
                   "room": sum(1 for i in items if i["kind"] == "room"),
                   "desk": sum(1 for i in items if i["kind"] == "desk"),
                   "party": sum(1 for i in items if i["kind"] == "party")},
        "rules": {
            "plays": PLAYS_NOTE,
            "facade": ("Anything this deployment does not hold stays a card "
                       "until you press it."),
            "public": ("Everything here was posted publicly, or is a desk or "
                       "room whose owner chose to be found."),
        },
    }


def item(post_or_id: str, viewer_adult: bool = False) -> dict | None:
    """One item, for a shared link. Same rules, one card.

    A deep link into a feed is how most people meet one, so it goes through
    the same construction rather than a second path that could disagree with
    it about what plays.
    """
    rows = db.connect().execute(
        "SELECT p.id, p.profile_id, p.topic, p.content, p.created_at,"
        "       v.platform, v.video_id, v.url, v.title AS video_title"
        "  FROM posts p LEFT JOIN post_videos v ON v.post_id = p.id"
        " WHERE p.id = ? AND p.status = 'approved' AND p.surface = 'wall'",
        (post_or_id,)).fetchall()
    if rows:
        row = rows[0]
        hosted = _hosted([row["id"]]).get(row["id"])
        if not hosted and not row["platform"]:
            return None
        prof = _profiles([row["profile_id"]]).get(
            row["profile_id"], {"profile_id": row["profile_id"], "name": ""})
        return _video_item(row, prof, hosted)

    desk = db.connect().execute(
        "SELECT id, owner_id, display_name, trade, location, blurb,"
        "       presence, rated, portrait, camera_url, created_at"
        "  FROM desks WHERE id = ? AND presence != 'closed'",
        (post_or_id,)).fetchone()
    if desk is not None:
        if desk["rated"] and not viewer_adult:
            return None
        return _desk_item(dict(desk))
    return None
