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

**It keys on its wearer and it runs near-field.** Two bounds, deliberately
separate, and together they are what makes "the profiles hear them, not the
room" true of the capture rather than true of a sentence in a note.

:data:`VOICE_FOCUS` is the filter: the channel locks onto the lender and drops
the rest, which in a room is the other participants. :data:`ROOM_GAIN` is the
limit: the grant runs near-field however the lender has their dial set. In JIM
that cap applies while a call is in progress; a room is that condition
permanently, so the grant is capped for its whole life. The lender's own dial
is not overwritten — it is theirs and it comes back — but a room is the one
place it cannot be honoured, because the people it would reach are sitting
right there.

Both, and not just the filter, because a filter can fail and the people it
would fail on did not choose to be in range.

Permission and state only — capture is on the device, like everywhere else.
"""

from __future__ import annotations

from . import db


# What may be lent, and what may not. Kept in step with `jim/mic.py`'s
# MIC_TYPES by hand — the two products do not import each other, the same way
# docs/tandem.md is byte-identical in three repos rather than shared.
#
# The axis is who the microphone is pointed at, not how it attaches. A room
# already has other people in it; lending one aimed at all of them would be
# lending their voices, which is not the lender's to give.
MIC_TYPES: dict[str, bool] = {          # name -> personal?
    "watch": True, "earbuds": True, "headset": True, "lapel": True,
    "clip_on": True, "bone_conduction": True, "glasses": True,
    "collar_tag": True, "handheld": True,
    "speakerphone": False, "conference": False, "console": False,
    "laptop": False, "room_array": False, "doorbell": False,
}
PERSONAL_TYPES = tuple(k for k, v in MIC_TYPES.items() if v)

# The same hardware, under the name the *pairing* registry gives it.
#
# `qrme/wearables.py` is where a person registers the devices they own, and it
# calls them `lapel_mic` and `clip_on_mic`; this module is kept in step with
# `jim/mic.py` by hand, and that one calls them `lapel` and `clip_on`. Two
# vocabularies for one collar clip, and for a while nothing joined them: you
# could pair a lapel mic and then be told `lapel_mic` was an unknown
# microphone type when you tried to lend it. The registry existed *for* this
# feature — `wearables.KINDS` says so in its own comment — and the feature
# arrived speaking a different language.
#
# Translated rather than renamed. Renaming here would desync the table from
# `jim/mic.py`, which is maintained by hand precisely because the two products
# do not import each other; renaming there would break paired rows. A test
# asserts every microphone-bearing kind in the registry has a landing place.
FROM_WEARABLE: dict[str, str] = {
    "watch": "watch",
    "earbuds": "earbuds",
    "headset": "headset",
    "lapel_mic": "lapel",
    "clip_on_mic": "clip_on",
    "glasses": "glasses",
}

# How wide the lent channel listens — also kept in step with `jim/mic.py` by
# hand. Every level is **the lender at some distance**, never a level of
# company: there is no setting whose answer to "what does it pick up" is "more
# people", and in a room that would be the whole objection to the feature.
#
# `reaches_others` does not mean the others are transcribed — VOICE_FOCUS
# handles that — it means another voice is physically inside the pickup pattern
# at that width. Focus is a filter and a filter can fail, so the width is kept
# as a second bound rather than folded into the first.
GAIN_LEVELS: dict[str, dict] = {
    "near_field": {"reaches_others": False,
                   "describes": "you, speaking close to the microphone"},
    "normal": {"reaches_others": True,
               "describes": "you, at arm's length or across a desk"},
    "wide": {"reaches_others": True,
             "describes": "you, from anywhere in the room"},
}

# The lent channel keys on the lender's voice and drops the rest. Not a
# setting, and in a room that matters more than anywhere else: the chatter a
# wider channel would pick up is other participants, and their voices were
# never the lender's to give.
VOICE_FOCUS = True
# What a room grant runs at, always. JIM caps channel 2 while a call is in
# progress; a room is that condition for its whole duration, so there is no
# state in which a wider one would be honest here.
ROOM_GAIN = "near_field"


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


def lend(room_id: str, interactor_id: str, device: str,
         mic_type: str = "watch", gain: str = ROOM_GAIN) -> dict:
    """Lend this room's profiles the wearable's microphone.

    Refused outside a live room, from a non-participant, or in a text room —
    in a chat room nobody's microphone is occupied, so there is nothing for a
    second one to work around.

    ``gain`` is accepted so a client can send the user's own setting without
    knowing which product it is talking to, but a room grant always runs
    near-field. It is capped rather than rejected for the same reason JIM caps
    it mid-call: the lender's preference is not wrong, the room is simply the
    one place it cannot be honoured.
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
    # A device may arrive under the name it was paired with. See FROM_WEARABLE:
    # the registry and this table are two vocabularies for one collar clip, and
    # the person lending it should not have to know which module they are
    # talking to.
    mic_type = FROM_WEARABLE.get(mic_type, mic_type)
    if mic_type not in MIC_TYPES:
        # A kind the pairing registry refuses outright gets the refusal it
        # earned, not "unknown". They are the room-facing devices, and the
        # reason they are absent is a decision — "unknown" reads as a gap
        # somebody will file a bug about, or worse, work around.
        from . import wearables
        if mic_type in wearables.REFUSED:
            raise RoomMicError(
                f"a {mic_type.replace('_', ' ')} is "
                f"{wearables.REFUSED[mic_type]}: it would pick up the people "
                "around you, and their voices are not yours to lend. A worn "
                "or clipped-on one can: "
                f"{', '.join(t.replace('_', ' ') for t in PERSONAL_TYPES)}")
        raise RoomMicError(
            f"unknown microphone type {mic_type!r} — one of "
            f"{', '.join(sorted(MIC_TYPES))}")
    if not MIC_TYPES[mic_type]:
        raise RoomMicError(
            f"a {mic_type.replace('_', ' ')} microphone is pointed at the "
            "room, not at you. It would pick up the people around you, and "
            "their voices are not yours to lend. A worn or clipped-on one "
            f"can: {', '.join(t.replace('_', ' ') for t in PERSONAL_TYPES)}")
    if gain not in GAIN_LEVELS:
        raise RoomMicError(
            f"unknown gain {gain!r} — one of {', '.join(GAIN_LEVELS)}")

    conn = db.connect()
    existing = conn.execute(
        "SELECT * FROM room_mics WHERE room_id=? AND interactor_id=?"
        " AND ended_at IS NULL", (room_id, interactor_id)).fetchone()
    if existing:
        return {**dict(existing), "already_lent": True}

    # One local, used for both the row and the answer, so what is reported can
    # never drift from what was recorded.
    effective = ROOM_GAIN

    grant_id = db.new_id("rmic")
    conn.execute(
        "INSERT INTO room_mics (id, room_id, interactor_id, device,"
        " mic_type, requested_gain, gain, started_at) VALUES (?,?,?,?,?,?,?,?)",
        (grant_id, room_id, interactor_id, device, mic_type, gain, effective,
         db.utcnow()))
    conn.commit()
    out = {"id": grant_id, "room_id": room_id, "device": device,
           "mic_type": mic_type, "lending": True,
           "gain": effective, "capped": gain != effective,
           "voice_focus": VOICE_FOCUS,
           "note": "the profiles in this room can hear you on your "
                   f"{device.replace('_', ' ')} — it keys on your voice and "
                   "drops the rest, including the others here. Everyone in "
                   "the room is shown that you lent it"}
    if out["capped"]:
        out["requested_gain"] = gain
        out["because"] = (
            "there are other people in this room, so your microphone stays "
            "narrow however you have it set — it picks up you, not them. Your "
            "setting is still yours everywhere else")
    return out


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
    # The room is shown the gain each grant *runs at*, never the one its lender
    # asked for. What protects the other participants is how wide the channel
    # actually is; a rejected preference is the lender's business, and putting
    # it here would tell the room something prejudicial and untrue of the
    # capture in the same breath.
    lent = [{"interactor_id": r["interactor_id"], "device": r["device"],
             "mic_type": r["mic_type"], "gain": r["gain"],
             "hears": GAIN_LEVELS[r["gain"]]["describes"],
             "since": r["started_at"]}
            for r in rows]
    return {
        "room_id": room_id,
        "microphones_lent": lent,
        "gain": ROOM_GAIN,
        "voice_focus": VOICE_FOCUS,
        "note": ("no one has lent the profiles a microphone" if not lent else
                 f"{len(lent)} participant(s) have lent the profiles a "
                 "microphone. Each one keys on its own wearer and is set "
                 "narrow enough to reach only them; the profiles hear them, "
                 "not the room"),
    }


def heard_by_profiles(room_id: str) -> list[str]:
    """Interactor ids whose voice the room's profiles currently receive."""
    return [r["interactor_id"] for r in db.connect().execute(
        "SELECT interactor_id FROM room_mics WHERE room_id=?"
        " AND ended_at IS NULL", (room_id,)).fetchall()]


# --------------------------------------------------------------------------- #
# Channel 2 on the surfaces that are not a room
# --------------------------------------------------------------------------- #

# Where else a wearable can be lent, and — the only question that decides it —
# **can the other people present be told?**
#
# That is the whole rule, and it is what made a room different from a phone
# call in the first place. `jim/mic.py` refuses speakerphone outright because
# the other party on a call is a stranger to this product: there is no surface
# on which to show them a disclosure, so their voice cannot be part of the
# bargain. A room's participants *can* be shown one, so a worn microphone is
# allowed there and telling them is the price.
#
# Every surface below passes that test — each has a member list and a place to
# render the disclosure to it. A surface that does not have both must not be
# added here, whatever else is convenient about it.
PLACES: dict[str, str] = {
    "party": "a watch party — the other members are listed and can be shown",
    "desk": "a live desk's stream — its visitors are present and can be shown",
    "connection": "a one-to-one connection — the other person is a user here",
}


def _place(surface: str) -> None:
    if surface == "room":
        raise RoomMicError(
            "a room lends through its own routes — POST /rooms/{id}/mic. Two "
            "storage paths for one surface is how a live microphone ends up "
            "undisclosed")
    if surface not in PLACES:
        raise RoomMicError(
            f"unknown surface {surface!r} — one of {', '.join(PLACES)}")


def lend_on(surface: str, surface_id: str, interactor_id: str, device: str,
            mic_type: str = "watch", gain: str = ROOM_GAIN) -> dict:
    """Lend the profiles here your wearable's microphone.

    The room rules apply unchanged, because the reasons for them do not depend
    on the surface being a room: only a worn microphone (a room-facing one
    lends the voices of people who did not agree), always near-field (there are
    other people present, by definition of every surface in :data:`PLACES`),
    keyed on its wearer, disclosed to everyone present, and ended with the
    place.
    """
    _place(surface)
    mic_type = FROM_WEARABLE.get(mic_type, mic_type)
    if mic_type not in MIC_TYPES:
        from . import wearables
        if mic_type in wearables.REFUSED:
            raise RoomMicError(
                f"a {mic_type.replace('_', ' ')} is "
                f"{wearables.REFUSED[mic_type]}: it would pick up the people "
                "around you, and their voices are not yours to lend")
        raise RoomMicError(f"unknown microphone type {mic_type!r}")
    if not MIC_TYPES[mic_type]:
        raise RoomMicError(
            f"a {mic_type.replace('_', ' ')} microphone is pointed at the "
            "room, not at you. It would pick up the people around you, and "
            "their voices are not yours to lend")
    if gain not in GAIN_LEVELS:
        raise RoomMicError(f"unknown gain {gain!r}")

    conn = db.connect()
    existing = conn.execute(
        "SELECT * FROM place_mics WHERE surface=? AND surface_id=?"
        " AND interactor_id=? AND ended_at IS NULL",
        (surface, surface_id, interactor_id)).fetchone()
    if existing:
        return {**dict(existing), "already_lent": True}

    effective = ROOM_GAIN
    grant_id = db.new_id("pmic")
    conn.execute(
        "INSERT INTO place_mics (id, surface, surface_id, interactor_id,"
        " device, mic_type, requested_gain, gain, started_at)"
        " VALUES (?,?,?,?,?,?,?,?,?)",
        (grant_id, surface, surface_id, interactor_id, device, mic_type,
         gain, effective, db.utcnow()))
    conn.commit()
    out = {"id": grant_id, "surface": surface, "surface_id": surface_id,
           "device": device, "mic_type": mic_type, "lending": True,
           "gain": effective, "capped": gain != effective,
           "voice_focus": VOICE_FOCUS,
           "note": f"the profiles here can hear you on your "
                   f"{device.replace('_', ' ')} — it keys on your voice and "
                   "drops the rest. Everyone here is shown that you lent it"}
    if out["capped"]:
        out["requested_gain"] = gain
        out["because"] = (
            "there are other people here, so your microphone stays narrow "
            "however you have it set. Your setting is still yours elsewhere")
    return out


def take_back_on(surface: str, surface_id: str, interactor_id: str) -> dict:
    """Yours to end, alone and at any moment."""
    _place(surface)
    conn = db.connect()
    row = conn.execute(
        "SELECT id FROM place_mics WHERE surface=? AND surface_id=?"
        " AND interactor_id=? AND ended_at IS NULL",
        (surface, surface_id, interactor_id)).fetchone()
    if row is None:
        return {"lending": False, "note": "you were not lending one"}
    conn.execute("UPDATE place_mics SET ended_at=? WHERE id=?",
                 (db.utcnow(), row["id"]))
    conn.commit()
    return {"lending": False, "id": row["id"]}


def close_place(surface: str, surface_id: str) -> int:
    """End every grant here. Called when the party ends, the desk closes or
    the connection drops — a permission must not outlive the thing that
    justified it and quietly apply to the next one."""
    conn = db.connect()
    rows = conn.execute(
        "SELECT id FROM place_mics WHERE surface=? AND surface_id=?"
        " AND ended_at IS NULL", (surface, surface_id)).fetchall()
    conn.execute(
        "UPDATE place_mics SET ended_at=? WHERE surface=? AND surface_id=?"
        " AND ended_at IS NULL", (db.utcnow(), surface, surface_id))
    conn.commit()
    return len(rows)


def disclosure_on(surface: str, surface_id: str) -> dict:
    """Who here has lent one — readable by everyone present, by design."""
    _place(surface)
    rows = db.connect().execute(
        "SELECT * FROM place_mics WHERE surface=? AND surface_id=?"
        " AND ended_at IS NULL ORDER BY started_at, rowid",
        (surface, surface_id)).fetchall()
    # The effective gain, never the requested one — same reason as a room's.
    lent = [{"interactor_id": r["interactor_id"], "device": r["device"],
             "mic_type": r["mic_type"], "gain": r["gain"],
             "hears": GAIN_LEVELS[r["gain"]]["describes"],
             "since": r["started_at"]} for r in rows]
    return {
        "surface": surface, "surface_id": surface_id,
        "microphones_lent": lent,
        "gain": ROOM_GAIN, "voice_focus": VOICE_FOCUS,
        "note": ("no one has lent the profiles a microphone" if not lent else
                 f"{len(lent)} person(s) have lent the profiles a microphone. "
                 "Each keys on its own wearer and is set narrow enough to "
                 "reach only them"),
    }


def heard_by_profiles_on(surface: str, surface_id: str) -> list[str]:
    """Interactor ids whose voice the profiles here currently receive."""
    return [r["interactor_id"] for r in db.connect().execute(
        "SELECT interactor_id FROM place_mics WHERE surface=? AND surface_id=?"
        " AND ended_at IS NULL", (surface, surface_id)).fetchall()]
