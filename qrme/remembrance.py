"""Remembering past the window.

## The finding

Chat context is the last ``MEMORY_WINDOW`` approved turns with one person.
The thirty-first-oldest message does not fade — it vanishes: nothing that
fell off the window could ever reach a prompt again, however much it
mattered. A profile that heard about a diagnosis, a wedding, a falling-out
in week one spoke in week ten as if none of it had been said.

    asked     does the profile carry memory of this person
    mattered  does the memory reach further back than one screen of chat

## What this module is

The fold: when approved turns exist that are older than the window and not
yet covered, they are distilled — by the profile's *own* provider, the same
one that speaks its replies — into one running paragraph per (profile,
interactor), stored beside the messages and carried into every prompt. The
paragraph is folded forward, never rebuilt: each pass reads only the turns
that aged out since the last, so the remembrance grows the way memory does,
by keeping what was kept.

## What it refuses to do

* **Break the conversation.** A distillation failure returns whatever was
  already remembered; the reply the person is waiting on never fails
  because a summary could not be made.
* **Outlive an erasure.** ``DELETE /profiles/{id}/memory/{interactor}``
  deletes this row with the messages — the erase-all promise is one
  promise, not one per table.
* **Remember what was never approved.** Pending and rejected turns are not
  memory; only the transcript both sides actually saw is folded.
"""

from __future__ import annotations

from . import db

#: The stored paragraph's cap. Memory is a précis, not an archive — the
#: archive is the messages table, readable at its own door.
_MAX_CONTENT = 2000

#: What each aged-out turn contributes to the fold, at most.
_MAX_TURN = 300

_DISTILLER = (
    "You keep a synthetic profile's long memory of one person. Fold the "
    "older conversation turns below into the running remembrance: one plain "
    "paragraph of at most 150 words, keeping names, facts, plans, promises "
    "and preferences, dropping greetings and filler. Never invent anything "
    "that is not in the turns or the existing remembrance. Write only the "
    "paragraph."
)


def get(profile_id: str, interactor_id: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM remembrances WHERE profile_id=? AND interactor_id=?",
        (profile_id, interactor_id),
    ).fetchone()
    return dict(row) if row else None


def clear(profile_id: str, interactor_id: str) -> None:
    conn = db.connect()
    conn.execute(
        "DELETE FROM remembrances WHERE profile_id=? AND interactor_id=?",
        (profile_id, interactor_id),
    )
    conn.commit()


def refresh(profile_id: str, interactor_id: str, window: int,
            provider) -> str | None:
    """The current remembrance, folding in any turns that aged out.

    Returns the paragraph to carry in the prompt, or ``None`` when nothing
    has aged out yet. ``provider`` is the profile's own — the voice that
    speaks is the voice that remembers.
    """
    conn = db.connect()
    total = conn.execute(
        "SELECT COUNT(*) AS n FROM messages"
        " WHERE profile_id=? AND interactor_id=? AND status='approved'",
        (profile_id, interactor_id),
    ).fetchone()["n"]
    target = total - window
    existing = get(profile_id, interactor_id)
    if target <= 0:
        return existing["content"] if existing else None
    covered = existing["covers"] if existing else 0
    if covered >= target:
        return existing["content"] if existing else None

    aged_out = conn.execute(
        "SELECT role, content FROM messages"
        " WHERE profile_id=? AND interactor_id=? AND status='approved'"
        " ORDER BY created_at, rowid LIMIT ? OFFSET ?",
        (profile_id, interactor_id, target - covered, covered),
    ).fetchall()
    transcript = "\n".join(
        ("the person" if row["role"] == "interactor" else "you")
        + ": " + row["content"][:_MAX_TURN]
        for row in aged_out
    )
    prompt = (
        ("Running remembrance so far:\n" + existing["content"] + "\n\n"
         if existing else "")
        + "Turns that have just aged out of the recent transcript:\n"
        + transcript
    )
    try:
        content = provider.generate(
            _DISTILLER, [{"role": "user", "content": prompt}]).strip()
    except Exception:
        # The reply the person is waiting on never fails because a summary
        # could not be made; fold again on a later turn.
        return existing["content"] if existing else None
    if not content:
        return existing["content"] if existing else None
    content = content[:_MAX_CONTENT]
    conn.execute(
        "INSERT INTO remembrances (profile_id, interactor_id, content,"
        " covers, updated_at) VALUES (?,?,?,?,?)"
        " ON CONFLICT(profile_id, interactor_id)"
        " DO UPDATE SET content=excluded.content, covers=excluded.covers,"
        " updated_at=excluded.updated_at",
        (profile_id, interactor_id, content, target, db.utcnow()),
    )
    conn.commit()
    return content
