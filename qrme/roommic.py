"""Lending a room's profiles a wearable microphone.

In a voice or video room the participant's own microphone is doing the
obvious job — carrying their voice to the other people in the room. The
synthetic profiles in that room are reading text. They have no ear of their
own, so anything the participant says *aloud but not typed* is invisible to
them, and asking a profile something means stopping, typing it, and breaking
the thing everyone else is listening to.

A watch already on the wrist has a microphone that nothing else is using.
This is the surface that lends it to the room's profiles, for context, while
the primary is busy being the participant's voice.

The JIM-mini counterpart (``jim/mic.py``) lends the same wearable to the
Guardian while its user is on a call. Same shape, and one genuinely different
question: **a room has other people in it.**

That difference is the whole of the design here.

**Everyone present is told.** A room's participants can each see that a
microphone has been lent and by whom (:func:`disclosure`). In a one-to-one
call the other party is a stranger to this product and cannot be told, which
is why ``jim/mic.py`` refuses speakerphone outright. In a room they are
participants, they can be told, and telling them is the price of the feature.

**Only the lender's own wearable, and only their own voice.** The grant is
per-participant. It never becomes the room's microphone, because a
participant cannot consent on behalf of the people they can hear.

**It ends with the room.** A grant is scoped to one room and closed when that
room closes, so a permission cannot outlive the conversation that justified
it and quietly apply to the next one.

Permission and state only — capture is on the device, like everywhere else.
"""

from __future__ import annotations

from . import db


class RoomMicError(ValueError):
    """A grant that must not happen. Text meant for a person."""


def _room(room_id: str) -> dict | None:
    row = db.connect().execute("SELECT * FROM rooms WHERE id=?",
                               (room_id,)).fetchone()
    return dict(row) if row else None


def _is_participant(room_id: str, interactor_id: str) -> bool:
    return db.connect().execute(
        "SELECT 1 FROM room_participants WHERE room_id=? AND kind='user'"
        " AND ref_id=?", (room_id, interactor_id)).fetchone() is not None


def lend(room_id: str, interactor_id: str, device: str) -> dict:
    """Lend this room's profiles the wearable's microphone.

    Refused outside a live room, from a non-participant, or in a text room —
    in a chat room nobody's microphone is occupied, so there is nothing for a
    second one to work around.
    """
    room = _room(room_id)
    if room is None:
        raise RoomMicError("no such room")
    if room["status"] != "active":
        raise RoomMicError("that room has closed")
    if room["channel"] not in ("voice", "video", "ar", "vr"):
        raise RoomMicError(
            f"this is a {room['channel']} room — nobody's microphone is busy, "
            "so the profiles can already read everything you send")
    if not _is_participant(room_id, interactor_id):
        raise RoomMicError("only a participant can lend a microphone")

    conn = db.connect()
    existing = conn.execute(
        "SELECT * FROM room_mics WHERE room_id=? AND interactor_id=?"
        " AND ended_at IS NULL", (room_id, interactor_id)).fetchone()
    if existing:
        return {**dict(existing), "already_lent": True}

    grant_id = db.new_id("rmic")
    conn.execute(
        "INSERT INTO room_mics (id, room_id, interactor_id, device,"
        " started_at) VALUES (?,?,?,?,?)",
        (grant_id, room_id, interactor_id, device, db.utcnow()))
    conn.commit()
    return {"id": grant_id, "room_id": room_id, "device": device,
            "lending": True,
            "note": "the profiles in this room can hear you on your "
                    f"{device.replace('_', ' ')}. Everyone here is shown "
                    "that you lent it"}


def take_back(room_id: str, interactor_id: str) -> dict:
    conn = db.connect()
    row = conn.execute(
        "SELECT * FROM room_mics WHERE room_id=? AND interactor_id=?"
        " AND ended_at IS NULL", (room_id, interactor_id)).fetchone()
    if row is None:
        return {"lending": False, "note": "you were not lending one"}
    conn.execute("UPDATE room_mics SET ended_at=? WHERE id=?",
                 (db.utcnow(), row["id"]))
    conn.commit()
    return {"lending": False, "id": row["id"]}


def close_room(room_id: str) -> int:
    """End every grant in a room. Called when the room closes, so a
    permission never outlives the conversation that justified it."""
    conn = db.connect()
    rows = conn.execute(
        "SELECT id FROM room_mics WHERE room_id=? AND ended_at IS NULL",
        (room_id,)).fetchall()
    conn.execute("UPDATE room_mics SET ended_at=? WHERE room_id=?"
                 " AND ended_at IS NULL", (db.utcnow(), room_id))
    conn.commit()
    return len(rows)


def disclosure(room_id: str) -> dict:
    """Who in this room has lent a microphone — readable by anyone in it.

    Not an owner-only audit trail: the people who need this are the other
    participants, and a disclosure only the lender can see is not one.
    """
    rows = db.connect().execute(
        "SELECT * FROM room_mics WHERE room_id=? AND ended_at IS NULL"
        " ORDER BY started_at, rowid", (room_id,)).fetchall()
    lent = [{"interactor_id": r["interactor_id"], "device": r["device"],
             "since": r["started_at"]} for r in rows]
    return {
        "room_id": room_id,
        "microphones_lent": lent,
        "note": ("no one has lent the profiles a microphone" if not lent else
                 f"{len(lent)} participant(s) have lent the profiles a "
                 "microphone; the profiles hear them, not the room"),
    }


def heard_by_profiles(room_id: str) -> list[str]:
    """Interactor ids whose voice the room's profiles currently receive."""
    return [r["interactor_id"] for r in db.connect().execute(
        "SELECT interactor_id FROM room_mics WHERE room_id=?"
        " AND ended_at IS NULL", (room_id,)).fetchall()]
