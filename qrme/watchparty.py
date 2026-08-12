"""Watching something together — people and profiles in the same room.

A watch party is a posted video plus everyone who turned up for it. The video
is the one from :mod:`qrme.embeds`, hosted somewhere else; the party adds a
shared position, a chat, and the thing that makes this platform's version
different from everyone else's: **synthetic profiles can be in the room.**

That last part is where the honesty problem is, and it is worth being exact
about rather than hand-waving past.

**A profile has not seen the video.** It cannot. Nothing here fetches the
video, nothing transcribes it, and a profile that said *"the bit at four
minutes was great"* would be fabricating — the most ordinary-looking lie this
product could tell, and the one nobody would think to check. So
:func:`prompt_context` hands the profile only what actually exists on this
side: the title the poster typed, the platform, where the party has got to, and
what the humans in the room have said. And it states the limit in the prompt,
in the second person, so the model is told rather than merely starved:

    you have not watched this and cannot see it; talk about what people are
    saying, and if somebody asks what you thought of a moment, say you have
    not seen it

Starving a model of context and hoping is not a safeguard. Telling it the
truth about its own position is.

**Nothing loads on anybody's behalf.** The party has a position, and the
position is a number the host moves — it does not press play for you. Each
viewer's own player starts when *they* press it, which keeps the promise
`embeds.py` makes: no request reaches YouTube until the person watching asks
for one. A watch party that pre-loaded the video for twenty people would have
quietly made twenty requests nobody agreed to.

**The host holds the position; nobody else does.** Otherwise the last person to
scrub controls what everybody sees, which is how a shared player becomes a
fight.

Chat is moderated exactly as anywhere else — a profile's turn goes through
:mod:`qrme.moderation` before anyone sees it, and a party with a minor in it
runs strict, the same rule rooms already use.
"""

from __future__ import annotations

from . import db, embeds, moderation, sharing

MAX_PARTY = 50
MAX_LINE = 600

# What a participant is. `profile` is a synthetic one; `person` is a real
# account. Kept apart because almost every rule below differs between them.
KINDS = ("person", "profile")
ROLES = ("host", "guest")

# The sentence a synthetic profile is given about its own position. Not a
# suggestion — it is prepended to the party context on every turn.
BLINDNESS = (
    "you have not watched this video and cannot see it. Talk about what the "
    "others in the room are saying and about what the video is titled. If "
    "somebody asks what you thought of a moment in it, say you have not seen "
    "it rather than inventing one."
)


class PartyError(ValueError):
    """A watch party that cannot stand."""


def _party(party_id: str):
    return db.connect().execute("SELECT * FROM watch_parties WHERE id=?",
                                (party_id,)).fetchone()


def start(post_id: str, host_id: str, title: str = "") -> dict:
    """Open a party around a posted video, or straight from a pasted link.

    Anchored to a post when given one, so the party inherits everything a
    post already carries — its author's rating, its moderation verdict, the
    fact that the link was checked against the platform allowlist when it
    was posted. A pasted video link is met too, because it is the most
    natural thing to put in the one field this screen has: the field report
    that forced the issue was a screenshot of a YouTube link answered with
    "that post has no video to watch" — technically true and humanly
    useless. A link that reaches this function by either name goes through
    :func:`start_from_url`.
    """
    anchor = (post_id or "").strip()
    if anchor.lower().startswith(("http://", "https://")):
        return start_from_url(anchor, host_id, title)
    post = db.connect().execute("SELECT status FROM posts WHERE id=?",
                                (anchor,)).fetchone()
    if post is None:
        # Checked before the video lookup, so the answer names what is
        # actually wrong. The old order answered a pasted URL with "that
        # post has no video to watch", which blamed a post nobody named.
        raise PartyError("nothing posted has that id — give the id of a "
                         "posted video, or paste the video's own link")
    if post["status"] != "approved":
        raise PartyError("that post is not visible, so it cannot be watched "
                         "together")
    video = embeds.facade(anchor)
    if video is None:
        raise PartyError("that post has no video to watch")

    pid = db.new_id("wpt")
    db.connect().execute(
        "INSERT INTO watch_parties (id, post_id, host_id, title, position_s,"
        " playing, created_at) VALUES (?,?,?,?,0,0,?)",
        (pid, anchor, host_id, (title or "").strip() or None, db.utcnow()))
    db.connect().commit()
    join(pid, host_id, kind="person", role="host")
    return get(pid)


def start_from_url(url: str, host_id: str, title: str = "") -> dict:
    """Open a party straight from a video link, with no post behind it.

    The link faces exactly the gate a wall post's video faces —
    :func:`embeds.parse`, the platform allowlist — so nothing plays here
    that could not have been posted. The video hangs off the party's own id
    in ``post_videos`` rather than off a fabricated post, so nobody's wall
    grows an entry they never wrote. What a post-anchored party inherits
    and this one cannot — an author and their rating — is covered where it
    already lives: the room's maturity is decided by who is in it
    (:func:`_maturity`), not by who posted the video.
    """
    try:
        embeds.parse(url)
    except embeds.EmbedError as exc:
        raise PartyError(str(exc)) from None
    pid = db.new_id("wpt")
    db.connect().execute(
        "INSERT INTO watch_parties (id, post_id, host_id, title, position_s,"
        " playing, created_at) VALUES (?,?,?,?,0,0,?)",
        (pid, pid, host_id, (title or "").strip() or None, db.utcnow()))
    db.connect().commit()
    # Keyed by the party's own id: `facade(post_id)` serves it unchanged,
    # and no posts row exists for it, so it can never surface on a wall.
    embeds.attach(pid, url, "")
    join(pid, host_id, kind="person", role="host")
    return get(pid)


def join(party_id: str, who_id: str, kind: str = "person",
         role: str = "guest") -> dict:
    """Add a person or a synthetic profile to the room."""
    row = _party(party_id)
    if row is None:
        raise PartyError("no such watch party")
    if kind not in KINDS:
        raise PartyError(f"kind is one of {', '.join(KINDS)}")
    if role not in ROLES:
        raise PartyError(f"role is one of {', '.join(ROLES)}")
    conn = db.connect()
    if kind == "profile":
        if conn.execute("SELECT 1 FROM profiles WHERE id=?",
                        (who_id,)).fetchone() is None:
            raise PartyError("no such profile")
    n = conn.execute(
        "SELECT COUNT(*) AS n FROM watch_party_members WHERE party_id=? AND"
        " left_at IS NULL", (party_id,)).fetchone()["n"]
    if n >= MAX_PARTY:
        raise PartyError(f"{MAX_PARTY} is the limit for one party")
    conn.execute(
        "INSERT INTO watch_party_members (id, party_id, member_id, kind, role,"
        " joined_at) VALUES (?,?,?,?,?,?)"
        " ON CONFLICT(party_id, member_id) DO UPDATE SET left_at=NULL",
        (db.new_id("wpm"), party_id, who_id, kind, role, db.utcnow()))
    conn.commit()
    return get(party_id)


def leave(party_id: str, who_id: str) -> dict:
    db.connect().execute(
        "UPDATE watch_party_members SET left_at=? WHERE party_id=? AND"
        " member_id=?", (db.utcnow(), party_id, who_id))
    db.connect().commit()
    return get(party_id)


def end(party_id: str, host_id: str) -> dict:
    """Close the party, and with it anything lent inside it.

    The teardown is here rather than left to whoever closes the room, because
    "remember to revoke the grants" is the kind of instruction one caller
    eventually forgets — and the thing forgotten is a permission still standing
    after the place that justified it is gone.
    """
    row = _party(party_id)
    if row is None:
        raise PartyError("no such watch party")
    if row["host_id"] != host_id:
        raise PartyError("only the host ends the party")
    conn = db.connect()
    conn.execute("UPDATE watch_party_members SET left_at=? WHERE party_id=?"
                 " AND left_at IS NULL", (db.utcnow(), party_id))
    conn.commit()
    from . import roommic
    return {"party_id": party_id, "ended": True,
            "grants_closed": sharing.close_surface("party", party_id),
            # A lent microphone is scoped to this party and dies with it. A
            # permission that outlives the thing which justified it is one
            # that quietly applies to the next thing.
            "microphones_returned": roommic.close_place("party", party_id)}


def members(party_id: str) -> list[dict]:
    rows = db.connect().execute(
        "SELECT m.*, p.display_name, p.avatar FROM watch_party_members m"
        "  LEFT JOIN profiles p ON p.id = m.member_id"
        " WHERE m.party_id=? AND m.left_at IS NULL ORDER BY m.joined_at",
        (party_id,)).fetchall()
    return [{"member_id": r["member_id"], "kind": r["kind"], "role": r["role"],
             "display_name": r["display_name"], "avatar": r["avatar"],
             # The mark travels into the party. A room where you cannot tell
             # which of the six names is a person is the room this platform
             # exists not to build.
             "synthetic": r["kind"] == "profile",
             "joined_at": r["joined_at"]} for r in rows]


def seek(party_id: str, host_id: str, position_s: int,
         playing: bool | None = None) -> dict:
    """Move the shared position. The host only.

    Everyone else follows. Letting any member scrub means the last one to touch
    it decides what the room is looking at, which is a fight rather than a
    feature.
    """
    row = _party(party_id)
    if row is None:
        raise PartyError("no such watch party")
    if row["host_id"] != host_id:
        raise PartyError("only the host moves the room's position")
    if position_s < 0:
        raise PartyError("a position cannot be negative")
    db.connect().execute(
        "UPDATE watch_parties SET position_s=?, playing=? WHERE id=?",
        (int(position_s),
         int(row["playing"] if playing is None else bool(playing)), party_id))
    db.connect().commit()
    return get(party_id)


def say(party_id: str, who_id: str, body: str, author: dict | None = None,
        at_position_s: int | None = None) -> dict:
    """A line in the party chat, from a person or a profile.

    Moderated on the way in like every other utterance here, and stamped with
    the position it was said at so a comment about a moment stays attached to
    that moment.
    """
    row = _party(party_id)
    if row is None:
        raise PartyError("no such watch party")
    body = (body or "").strip()
    if not body:
        raise PartyError("say something")
    if len(body) > MAX_LINE:
        raise PartyError(f"a line is at most {MAX_LINE} characters")
    member = db.connect().execute(
        "SELECT * FROM watch_party_members WHERE party_id=? AND member_id=?"
        " AND left_at IS NULL", (party_id, who_id)).fetchone()
    if member is None:
        raise PartyError("join the party before talking in it")

    # Strict whenever a minor is present, the same rule a room runs on. The
    # party does not get to be the surface where that relaxes.
    verdict = moderation.review(body, None, author or {"birthdate": None},
                                maturity=_maturity(party_id))
    status = "approved" if verdict.approved else "blocked"
    line_id = db.new_id("wpl")
    db.connect().execute(
        "INSERT INTO watch_party_lines (id, party_id, member_id, kind, body,"
        " position_s, status, flag_reason, created_at)"
        " VALUES (?,?,?,?,?,?,?,?,?)",
        (line_id, party_id, who_id, member["kind"], body,
         int(row["position_s"] if at_position_s is None else at_position_s),
         status, None if verdict.approved else verdict.reason, db.utcnow()))
    db.connect().commit()
    return {"id": line_id, "party_id": party_id, "member_id": who_id,
            "body": body, "status": status,
            "blocked_reason": None if verdict.approved else verdict.reason}


def _maturity(party_id: str) -> str:
    """`strict` if anybody in the room is a minor, otherwise `general`."""
    rows = db.connect().execute(
        "SELECT i.birthdate FROM watch_party_members m"
        "  JOIN interactors i ON i.id = m.member_id"
        " WHERE m.party_id=? AND m.left_at IS NULL", (party_id,)).fetchall()
    for r in rows:
        age = moderation._age_of(r["birthdate"])
        if age is not None and age < 18:
            return "strict"
    return "general"


def chat(party_id: str, limit: int = 100) -> list[dict]:
    rows = db.connect().execute(
        "SELECT l.*, p.display_name FROM watch_party_lines l"
        "  LEFT JOIN profiles p ON p.id = l.member_id"
        " WHERE l.party_id=? AND l.status='approved'"
        " ORDER BY l.created_at, l.rowid LIMIT ?", (party_id, limit)).fetchall()
    return [{"id": r["id"], "member_id": r["member_id"],
             "display_name": r["display_name"], "kind": r["kind"],
             "synthetic": r["kind"] == "profile",
             "body": r["body"], "position_s": r["position_s"],
             "created_at": r["created_at"]} for r in rows]


def prompt_context(party_id: str, limit: int = 20) -> dict:
    """Everything a synthetic profile in this party is allowed to know.

    Deliberately small, and deliberately explicit about what is missing. The
    profile gets the title somebody typed, the platform, where the room has got
    to, and the recent conversation — and it is *told* it has not seen the
    video, because a model given only chat lines will otherwise fill the gap
    with a plausible opinion about footage nobody showed it.
    """
    row = _party(party_id)
    if row is None:
        raise PartyError("no such watch party")
    video = embeds.facade(row["post_id"]) or {}
    lines = chat(party_id, limit=limit)
    return {
        "watching": {
            "title": video.get("title"),
            "platform": video.get("platform_name"),
            # Named for what it is. This is not a description of the video,
            # because nothing on this side has one.
            "description_available": False,
            "transcript_available": False,
        },
        "position_s": row["position_s"],
        "playing": bool(row["playing"]),
        "recent": [{"who": ln["display_name"] or ln["member_id"],
                    "said": ln["body"], "at": ln["position_s"]}
                   for ln in lines[-limit:]],
        "you_have_not_seen_it": True,
        "instruction": BLINDNESS,
    }


def get(party_id: str) -> dict:
    row = _party(party_id)
    if row is None:
        raise PartyError("no such watch party")
    people = members(party_id)
    return {
        "id": row["id"], "post_id": row["post_id"], "host_id": row["host_id"],
        "title": row["title"],
        "video": embeds.facade(row["post_id"]),
        "position_s": row["position_s"], "playing": bool(row["playing"]),
        "members": people,
        "people": sum(1 for m in people if m["kind"] == "person"),
        "profiles": sum(1 for m in people if m["kind"] == "profile"),
        "created_at": row["created_at"],
        # The two promises, carried with the object.
        "loads_on_press": True,
        "note": ("the room shares a position, not a player — your video still "
                 "loads only when you press play"),
    }
