"""The inbox: the platform tells you what happened while you were away.

Every event here is something *somebody else did to you* — a message sent,
a comment left under your post, a friendship extended, an exchange signed,
a place on a stream granted. The 0.42.x rounds built each of those doors,
and every one of them shared a silence: the thing happened, and the person
it happened to found out only by going to look. A capability nobody is
told about is reachable the way a doorless route is — technically.

    asked     can the platform do this to a person
    mattered  does the person ever hear about it

Two rules, both deliberate:

**The inbox names the deed, never the words.** A row carries a kind, an
actor and a reference — "somebody sent you a message" — and the message
itself stays behind the owner's door where it already lives. So the inbox
can be listed cheaply, rendered by any client from its own vocabulary,
and leaks nothing a shoulder-surfer shouldn't have: the words wait where
the reader chose to keep them.

**Your own deeds never land in your own inbox.** ``note`` drops the event
silently when recipient and actor are the same profile — telling somebody
what they just did is noise wearing the coat of news.

A blocked comment is the third, quieter rule: no event at all. The comment
is invisible to everyone but its author, and an inbox row saying "somebody
commented" about a thing the recipient can never see would be the filter
advertising its own catch — see the hook in ``audience.comment``.
"""

from __future__ import annotations

from . import db

#: The deeds the inbox knows how to name. A closed set on purpose: adding
#: one is a decision made here, where clients' vocabularies must follow,
#: rather than a string that quietly becomes load-bearing.
KINDS = (
    "message",         # somebody sent you a message
    "comment",         # somebody commented under something of yours
    "friend",          # somebody added you as a friend
    "exchange_signed",  # the other party signed your exchange
    "guest_accepted",  # a host gave you your place on their stream
)


class InboxError(ValueError):
    pass


def note(recipient_id: str, kind: str, actor_id: str,
         ref: str | None = None) -> None:
    """Record that something happened to ``recipient_id``.

    Called from inside the deed, after it has succeeded — never from a
    router, so every path to the deed notes it or none does. Best-effort
    by design is exactly what this is **not**: a failed insert should fail
    the deed's transaction visibly rather than lose the news quietly.
    """
    if kind not in KINDS:
        raise InboxError(
            f"unknown inbox kind {kind!r}; the kinds are "
            f"{', '.join(KINDS)}")
    if recipient_id == actor_id:
        return
    conn = db.connect()
    conn.execute(
        "INSERT INTO inbox_events (id, profile_id, kind, actor_id, ref,"
        " created_at) VALUES (?,?,?,?,?,?)",
        (db.new_id("ibx"), recipient_id, kind, actor_id, ref, db.utcnow()))
    conn.commit()


def events(profile_id: str, limit: int = 50) -> dict:
    """The inbox, newest first, with the unseen count a badge needs.

    Each row carries the actor's display name alongside the id, so a list
    is a list without n lookups — the same courtesy ``social.threads``
    extends. The *sentence* is the client's to compose from its own
    vocabulary: the backend hands over a kind, not prose, which is what
    lets ten languages live in the clients where the other labels already
    are.
    """
    conn = db.connect()
    rows = conn.execute(
        "SELECT e.*, p.display_name AS actor_name FROM inbox_events e"
        " LEFT JOIN profiles p ON p.id = e.actor_id"
        " WHERE e.profile_id=? ORDER BY e.created_at DESC LIMIT ?",
        (profile_id, limit)).fetchall()
    unseen = conn.execute(
        "SELECT COUNT(*) FROM inbox_events WHERE profile_id=? AND"
        " seen_at IS NULL", (profile_id,)).fetchone()[0]
    return {
        "events": [{"id": r["id"], "kind": r["kind"],
                    "actor_id": r["actor_id"],
                    "actor_name": r["actor_name"], "ref": r["ref"],
                    "created_at": r["created_at"],
                    "seen": r["seen_at"] is not None} for r in rows],
        "unseen": unseen,
    }


def mark_seen(profile_id: str) -> dict:
    """The reader has looked. Everything unseen becomes seen, at once —
    per-row acknowledgement would make the inbox a second to-do list,
    and it is a window, not a chore."""
    conn = db.connect()
    cur = conn.execute(
        "UPDATE inbox_events SET seen_at=? WHERE profile_id=? AND"
        " seen_at IS NULL", (db.utcnow(), profile_id))
    conn.commit()
    # `marked_seen`, not `seen`. The row beside it uses `seen` for a boolean —
    # *has this item been seen* — and one name meaning both the state and a
    # count of it is a field no client can read without knowing which route
    # it came from. `InboxPage.unseen` next door already had the instinct.
    return {"marked_seen": cur.rowcount}
