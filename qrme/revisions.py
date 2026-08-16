"""Editing and retracting something you already said.

A conversation is not a transcript of a courtroom. People mistype, they say a
thing badly, they give the wrong year for something and want it fixed — and on
this platform that matters more than usual, because what somebody said is also
what the profile will reason from next time. A typo that reaches the prompt
does not just look untidy; it becomes something the profile believes.

So an interactor can **edit** or **retract** their own turn, and the change
carries forward. That last part is free rather than clever: the chat path
rebuilds history from ``messages`` on every turn, so a corrected row is simply
what the next prompt sees. Nothing has to be re-indexed, and there is no
snapshot to go stale.

Four rules hold it together.

**You can only change your own turn.** An interactor edits what they said; they
cannot touch the profile's replies. Being able to rewrite the other side of a
conversation is not editing, it is fabrication — and on a platform whose whole
business is synthetic people saying things, putting words in a profile's mouth
is the one edit that must never be possible.

**An edit is moderated like a new message.** Otherwise the edit box is a way to
smuggle past a filter the original had to clear: post something harmless, then
change it to what you meant.

**Retracting is not deleting.** The row stays and its status becomes
``retracted``, which the history query already excludes, because it only ever
selected ``approved``. The text stops reaching the profile and stops being
shown, and the record of it having existed survives for the moderation trail.

**A reply that was written before an edit is marked stale.** This is the part
worth being careful about. When somebody corrects a question, the answer under
it was a response to the *old* wording, and quietly leaving it there implies
the profile answered the new one. It did not. :func:`thread` flags those
replies rather than hiding them — the honest version is "this was answered
before you changed it", not a silent rewrite of history.
"""

from __future__ import annotations

from . import db, moderation

MAX_EDITS = 20          # per message; a hundred revisions is a different problem


class RevisionError(ValueError):
    """An edit that cannot stand."""


def _message(message_id: str) -> dict | None:
    row = db.connect().execute("SELECT * FROM messages WHERE id=?",
                               (message_id,)).fetchone()
    return dict(row) if row else None


def _count(message_id: str) -> int:
    return db.connect().execute(
        "SELECT COUNT(*) AS n FROM message_revisions WHERE message_id=?",
        (message_id,)).fetchone()["n"]


def edit(message_id: str, new_content: str, actor_id: str,
         author: dict | None = None) -> dict:
    """Replace what an interactor said, and let it carry forward.

    ``actor_id`` is the interactor doing the editing; it must match the
    message's author. The new text goes through moderation exactly as a fresh
    message would.
    """
    new_content = (new_content or "").strip()
    if not new_content:
        raise RevisionError("an edit needs something in it — retract instead")

    msg = _message(message_id)
    if msg is None:
        raise RevisionError("message not found")
    if msg["role"] != "interactor":
        raise RevisionError(
            "only your own turn can be edited — a profile's reply is not "
            "yours to rewrite")
    if msg["interactor_id"] != actor_id:
        raise RevisionError("that message belongs to somebody else")
    if msg["status"] == "retracted":
        raise RevisionError("that message was retracted")
    if _count(message_id) >= MAX_EDITS:
        raise RevisionError(f"a message can be edited {MAX_EDITS} times")
    if new_content == msg["content"]:
        return thread_entry(message_id)

    profile = db.connect().execute(
        "SELECT adult_mode FROM profiles WHERE id=?",
        (msg["profile_id"],)).fetchone()
    verdict = moderation.review(
        new_content, None, author or {"birthdate": None},
        maturity="adult" if profile and profile["adult_mode"] else "general")
    status = "approved" if verdict.approved else "rejected"

    conn = db.connect()
    conn.execute(
        "INSERT INTO message_revisions (id, message_id, was, became, reason,"
        " edited_at) VALUES (?,?,?,?,?,?)",
        (db.new_id("rev"), message_id, msg["content"], new_content,
         None if verdict.approved else verdict.reason, db.utcnow()))
    conn.execute("UPDATE messages SET content=?, status=? WHERE id=?",
                 (new_content, status, message_id))
    conn.commit()
    return thread_entry(message_id)


def retract(message_id: str, actor_id: str) -> dict:
    """Take back something said. The row survives; the text stops counting.

    Deliberately not a DELETE. The moderation trail is the reason a blocked
    message is kept at all, and a retraction that erased the row would be a way
    to remove one.
    """
    msg = _message(message_id)
    if msg is None:
        raise RevisionError("message not found")
    if msg["role"] != "interactor":
        raise RevisionError("only your own turn can be retracted")
    if msg["interactor_id"] != actor_id:
        raise RevisionError("that message belongs to somebody else")
    if msg["status"] == "retracted":
        return thread_entry(message_id)

    conn = db.connect()
    conn.execute(
        "INSERT INTO message_revisions (id, message_id, was, became, reason,"
        " edited_at) VALUES (?,?,?,NULL,'retracted',?)",
        (db.new_id("rev"), message_id, msg["content"], db.utcnow()))
    # `retracted` is not `approved`, and the chat path only ever selected
    # approved rows — so this drops out of the prompt with no query change.
    conn.execute("UPDATE messages SET status='retracted' WHERE id=?",
                 (message_id,))
    conn.commit()
    return thread_entry(message_id)


def revisions(message_id: str) -> list[dict]:
    rows = db.connect().execute(
        "SELECT was, became, reason, edited_at FROM message_revisions"
        " WHERE message_id=? ORDER BY edited_at, rowid", (message_id,)
    ).fetchall()
    return [{"was": r["was"], "became": r["became"], "reason": r["reason"],
             "edited_at": r["edited_at"],
             "retraction": r["became"] is None} for r in rows]


def thread_entry(message_id: str) -> dict:
    msg = _message(message_id) or {}
    revs = revisions(message_id)
    return {"id": message_id, "content": msg.get("content"),
            "status": msg.get("status"), "edited": bool(revs),
            "edit_count": len(revs), "revisions": revs}


def thread(profile_id: str, interactor_id: str) -> list[dict]:
    """The conversation, with edits and staleness visible.

    A profile reply written *before* an edit answered the old wording. It is
    flagged rather than hidden: pretending the answer was to the new question
    would be a quieter lie than showing it and saying so.
    """
    conn = db.connect()
    rows = conn.execute(
        "SELECT * FROM messages WHERE profile_id=? AND interactor_id=?"
        " ORDER BY created_at, rowid", (profile_id, interactor_id)).fetchall()

    # When each message was last edited, so a later reply can be compared.
    last_edit = {}
    for r in conn.execute(
            "SELECT message_id, MAX(edited_at) AS at FROM message_revisions"
            " GROUP BY message_id").fetchall():
        last_edit[r["message_id"]] = r["at"]

    out, pending_edit = [], None
    for r in rows:
        entry = {"id": r["id"], "role": r["role"], "content": r["content"],
                 "status": r["status"], "created_at": r["created_at"],
                 "edited": r["id"] in last_edit,
                 "edit_count": 0, "answers_stale_text": False}
        if r["id"] in last_edit:
            entry["edit_count"] = len(revisions(r["id"]))
            entry["edited_at"] = last_edit[r["id"]]
        if r["role"] == "interactor":
            pending_edit = last_edit.get(r["id"])
        elif pending_edit and r["created_at"] < pending_edit:
            # This reply predates the edit above it, so it answered the old
            # wording. Say so rather than letting the pairing imply otherwise.
            entry["answers_stale_text"] = True
            entry["stale_note"] = ("written before the message above was "
                                   "edited — it answered the earlier wording")
        out.append(entry)
    return out
