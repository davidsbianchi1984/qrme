"""The community wall, and the feed that decides what you see of it.

Publishing is the easy half: a profile writes a post, it passes moderation, it
exists. Everything below is about the other half — which of them reach you, and
why — because that is the decision a feed actually is.

**What the ranking is allowed to know.**

A For You feed is a new use of a person's data, and QRME's data promise is
specific enough that "ranked on your data" would quietly stop being true of it.
So the line is drawn narrowly and stated here rather than left implied:

    The feed ranks on what you have *done in public* — who you are friends
    with, whose posts you liked, which profiles you have talked to and what
    they are tagged with.

    It never reads a profile's memories, its source material, or anything
    sealed in a vault. Those belong to the person they are about, and
    "improving your feed" is not consent to read them.

That is not a soft rule; :func:`for_you` only ever queries the friendships,
reactions and engagement tables, and a test asserts it never touches
``source_items`` or ``memories``.

**Every post says why it is in front of you.** Each entry carries a ``reason``
in plain words — *a friend posted this*, *you talked to this profile*, *popular
with people here*. A ranked feed that cannot explain itself is one nobody can
audit, including the person who built it, and the explanation costs a string.

**Recency is a tiebreak, not the ranking.** A pure reverse-chronological wall
is not what was asked for, but a feed that buries a friend's post under a
stranger's because the stranger posted more recently is the failure mode people
actually complain about.
"""

from __future__ import annotations

from datetime import datetime, timezone

from . import audience, db, embeds, moderation

MAX_BODY = 2000

# Wall posts live in the existing `posts` table, marked by surface. There was
# already one — social.py publishes through it — and it carried an author,
# content, a surface and a moderation verdict, which is the whole of what a
# wall post is. A second posts table would have drifted from it inside a round,
# and the near-miss is recorded here because `CREATE TABLE IF NOT EXISTS` made
# the duplicate silent rather than loud.
SURFACE = "wall"

# What each signal is worth. Deliberately small integers rather than tuned
# floats: this is a ranking somebody has to be able to read and argue with, and
# a weight nobody can explain is a weight nobody can defend.
W_FRIEND = 100          # you chose to stand with them
W_TALKED = 60           # you have actually spoken to this profile
W_TAG = 25              # it works in something you engage with
W_LIKES = 2             # per like, capped below
W_LIKES_CAP = 40        # popularity contributes, it does not decide
RECENCY_HOURS = 72      # the window recency is scored across


class WallError(ValueError):
    """A post that cannot stand."""


def publish(profile_id: str, body: str, author: dict | None = None,
            listing_id: str | None = None, video_url: str | None = None,
            video_title: str = "") -> dict:
    """Write a post to the wall. Moderated on the way in.

    A blocked post is kept and returned to its author with the reason, and is
    invisible to everyone else — the shape the audience layer already uses for
    a comment, for the same reason: dropping it silently teaches the author
    nothing, while showing it teaches everyone else the filter does not work.
    """
    body = (body or "").strip()
    if not body:
        raise WallError("a post needs something in it")
    if len(body) > MAX_BODY:
        raise WallError(f"a post is at most {MAX_BODY} characters")
    row = db.connect().execute("SELECT adult_mode FROM profiles WHERE id=?",
                               (profile_id,)).fetchone()
    if row is None:
        raise WallError("no such profile")

    verdict = moderation.review(
        body, None, author or {"birthdate": None},
        maturity="adult" if row["adult_mode"] else "general")
    status = "approved" if verdict.approved else "blocked"

    # What the post is promoting, if anything. A reference to a listing rather
    # than a copy of one: a price written into a post is a price that goes
    # stale the moment the listing changes, and nobody edits the post.
    if listing_id is not None:
        listed = db.connect().execute(
            "SELECT profile_id FROM listings WHERE id=?",
            (listing_id,)).fetchone()
        if listed is None:
            raise WallError("no such listing")
        if listed["profile_id"] != profile_id:
            raise WallError(
                "a post can only promote its own profile's listing")

    # Checked before the post is written, not after. Attaching afterwards would
    # leave a bad link as an orphan post somebody has to go and delete.
    if video_url is not None:
        embeds.parse(video_url)

    post_id = db.new_id("pst")
    db.connect().execute(
        "INSERT INTO posts (id, profile_id, surface, topic, content, status,"
        " flag_reason, created_at) VALUES (?,?,?,NULL,?,?,?,?)",
        (post_id, profile_id, SURFACE, body, status,
         None if verdict.approved else verdict.reason, db.utcnow()))
    if listing_id is not None:
        db.connect().execute(
            "INSERT INTO post_attachments (post_id, listing_id, created_at)"
            " VALUES (?,?,?)", (post_id, listing_id, db.utcnow()))
    db.connect().commit()
    video = embeds.attach(post_id, video_url, video_title) \
        if video_url is not None else None
    return {"id": post_id, "profile_id": profile_id, "body": body,
            "listing_id": listing_id, "video": video,
            "status": status,
            "blocked_reason": None if verdict.approved else verdict.reason}


def _hours_since(stamp: str) -> float:
    try:
        then = datetime.fromisoformat(stamp)
    except ValueError:                                   # pragma: no cover
        return RECENCY_HOURS
    if then.tzinfo is None:
        then = then.replace(tzinfo=timezone.utc)
    return max(0.0, (datetime.now(timezone.utc) - then).total_seconds() / 3600)


def _signals(viewer_profile_id: str) -> tuple[set[str], set[str], set[str]]:
    """What the viewer has done in public, and nothing else.

    Three sets: profiles they are friends with, profiles they have talked to,
    and the tags on those profiles. Every one of these comes from an action the
    viewer took deliberately and in the open.
    """
    conn = db.connect()
    friends_of = {r["friend_id"] for r in conn.execute(
        "SELECT friend_id FROM friendships WHERE profile_id=? AND"
        " state='active'", (viewer_profile_id,)).fetchall()}

    # "Talked to" is read from the viewer's own engagement rows, which is the
    # same table the review gate uses for "were you actually there".
    talked = {r["profile_id"] for r in conn.execute(
        "SELECT DISTINCT e.profile_id FROM engagement e"
        "  JOIN interactors i ON i.id = e.interactor_id"
        " WHERE e.interactions > 0 AND i.id IN ("
        "   SELECT interactor_id FROM engagement WHERE profile_id=?)",
        (viewer_profile_id,)).fetchall()}

    import json
    tags: set[str] = set()
    for pid in friends_of | talked:
        row = conn.execute("SELECT tags FROM marketplace WHERE profile_id=?",
                           (pid,)).fetchone()
        if row and row["tags"]:
            try:
                tags.update(json.loads(row["tags"]))
            except ValueError:
                pass
    return friends_of, talked, tags


def for_you(viewer_profile_id: str, limit: int = 25,
            adult_ok: bool = False) -> list[dict]:
    """The feed: what this viewer sees, most relevant first, and why.

    Only ever reads friendships, engagement, marketplace tags and reactions —
    public actions. Never source material, memories, or anything vaulted.
    """
    import json
    conn = db.connect()
    friends_of, talked, tags = _signals(viewer_profile_id)

    rows = conn.execute(
        "SELECT o.id, o.profile_id, o.content AS body, o.created_at,"
        "       p.display_name,"
        "       p.avatar, p.adult_mode, m.tags AS author_tags,"
        "       (SELECT COUNT(*) FROM reactions r WHERE r.target_kind='post'"
        "          AND r.target_id = o.id) AS likes"
        "  FROM posts o"
        "  JOIN profiles p ON p.id = o.profile_id"
        "  LEFT JOIN marketplace m ON m.profile_id = o.profile_id"
        " WHERE o.surface=? AND o.status='approved' AND o.profile_id != ?"
        " ORDER BY o.created_at DESC LIMIT 500", (SURFACE, viewer_profile_id)
    ).fetchall()

    out = []
    for r in rows:
        if r["adult_mode"] and not adult_ok:
            continue
        score, reasons = 0, []
        if r["profile_id"] in friends_of:
            score += W_FRIEND
            reasons.append("a friend posted this")
        if r["profile_id"] in talked:
            score += W_TALKED
            reasons.append("you have talked to this profile")
        if not reasons and r["author_tags"] and tags:
            try:
                shared = tags & set(json.loads(r["author_tags"]))
            except ValueError:
                shared = set()
            if shared:
                score += W_TAG
                reasons.append(f"you engage with {sorted(shared)[0]}")
        likes = r["likes"] or 0
        if likes:
            score += min(likes * W_LIKES, W_LIKES_CAP)
            if not reasons:
                reasons.append("popular with people here")
        # Recency is the tiebreak. A friend's post from yesterday should not
        # sit under a stranger's from ten minutes ago.
        age = _hours_since(r["created_at"])
        score += max(0, RECENCY_HOURS - age) / RECENCY_HOURS * 10

        out.append({
            "id": r["id"], "profile_id": r["profile_id"],
            "display_name": r["display_name"], "avatar": r["avatar"],
            "body": r["body"], "created_at": r["created_at"],
            "likes": likes,
            "promoting": _attachment(r["id"]),
            "video": embeds.facade(r["id"]),
            "score": round(score, 1),
            # Never empty. A feed that cannot say why something is in front of
            # you is one nobody can audit, including its author.
            "reason": reasons[0] if reasons else "new on the wall",
        })

    out.sort(key=lambda p: (-p["score"], p["created_at"]), reverse=False)
    return out[:limit]


def _attachment(post_id: str) -> dict | None:
    """The listing a post is promoting, read live rather than copied."""
    row = db.connect().execute(
        "SELECT l.id, l.kind, l.title, l.blurb, l.area FROM post_attachments a"
        "  JOIN listings l ON l.id = a.listing_id WHERE a.post_id=?",
        (post_id,)).fetchone()
    return dict(row) if row else None


def wall(profile_id: str, limit: int = 50, owner: bool = False) -> list[dict]:
    """One profile's own posts, newest first.

    The owner sees blocked posts with the reason; nobody else does.
    """
    rows = db.connect().execute(
        "SELECT o.*, (SELECT COUNT(*) FROM reactions r WHERE"
        "   r.target_kind='post' AND r.target_id=o.id) AS likes"
        "  FROM posts o WHERE o.profile_id=? AND o.surface=?"
        " ORDER BY o.created_at DESC LIMIT ?",
        (profile_id, SURFACE, limit)).fetchall()
    out = []
    for r in rows:
        if r["status"] != "approved" and not owner:
            continue
        entry = {"id": r["id"], "profile_id": r["profile_id"],
                 "body": r["content"], "created_at": r["created_at"],
                 "likes": r["likes"] or 0, "status": r["status"],
                 "promoting": _attachment(r["id"]),
                 "video": embeds.facade(r["id"])}
        if owner and r["status"] == "blocked":
            entry["blocked_reason"] = r["flag_reason"]
        out.append(entry)
    return out
