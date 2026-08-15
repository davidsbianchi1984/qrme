"""What each person in a room is showing.

The room scene draws everybody in their own box. Until now a box could hold
exactly one thing: two initials and a name. That is what a box looks like when
nobody has decided what goes in it, and it made the scene a legend for a
conversation rather than the conversation.

    asked     everyone in the room in their own box
    mattered  and the box is where you decide what people see of you

Three answers, and **all three are a box**:

``voice``
    Your name and nothing else. The default, and it is not an absence — a
    person who has their camera off, or who is muted, keeps their box, at the
    same size, in the same place. A scene that removes the quiet people is a
    scene that answers *who is talking* and loses *who is here*, and the
    second question is the one a room is for.

``photo``
    A still they uploaded. A person's own photograph, and therefore **never AI
    marked** — the rule `media.limits` already states and the reason it states
    it: burning the synthetic-media mark into an authentic picture is a false
    statement in the exact direction the mark exists to prevent. A *profile*
    in the room is a different case and keeps its mark; see `showing_in`.

``camera``
    Their camera, live. What is stored here is the **fact**, not the pixels:
    capture and rendering are on the device, the same division `overlays` draws
    and for the same reason. Storing the fact is what lets every other client
    in the room draw the same scene — a tile that is live rather than still,
    and a name under it either way.

A mask is a fourth thing and deliberately not a fourth value. `overlays` already
owns what somebody is wearing over their face, on the ``room`` surface, with a
disclosure sentence per wearer and a published list of what may never be worn.
Showing and wearing are separate questions — you can wear a wolf on a live
camera or on nothing at all — so they stay two records, and the scene reads
both.

**Everyone in the room may read everyone's.** A scene each person draws from
their own state alone is not a scene. The read is held to being *in the room*
rather than *knowing the room id*, which is the lesson `roommic` learned the
hard way: its docstring claimed the disclosure was for the people in the room
while the code checked nothing, and a room id travels on printed stickers.
"""

from __future__ import annotations

from . import db

# What a box can be. The values are the client's rendering instruction and the
# person's own words for it, kept together so a client cannot invent a fourth.
SHOWING: dict[str, str] = {
    "voice": "your name, and nothing else — you are here and not on camera",
    "photo": "a picture you uploaded, standing in for you",
    "camera": "your camera, live",
}

DEFAULT = "voice"

# A face is a picture. The upload path accepts what `media` accepts and this
# narrows it: a room box is not a place to serve a PDF.
FACE_KINDS = ("image",)


class RoomFaceError(ValueError):
    """A face that cannot be set. Text meant for a person."""


def set_showing(room_id: str, interactor_id: str, showing: str,
                media_id: str | None = None,
                media_url: str | None = None) -> dict:
    """Decide what your box holds. Yours alone — the route authorizes it.

    ``photo`` needs a picture, and the check is here rather than at the route
    so a client that forgets one is told which of the two halves is missing.
    Switching to ``voice`` or ``camera`` keeps the picture on the row: somebody
    who turns their camera on and off again should find their photo where they
    left it, and a state change is not a deletion.
    """
    if showing not in SHOWING:
        raise RoomFaceError(
            f"unknown {showing!r} — one of {', '.join(SHOWING)}")

    conn = db.connect()
    row = conn.execute(
        "SELECT * FROM room_faces WHERE room_id=? AND interactor_id=?",
        (room_id, interactor_id)).fetchone()

    if media_id or media_url:
        keep_id, keep_url = media_id, media_url
    else:
        keep_id = row["media_id"] if row else None
        keep_url = row["media_url"] if row else None

    if showing == "photo" and not keep_url:
        raise RoomFaceError(
            "upload a picture first — 'photo' is a box with a picture in it, "
            "and there is none on this room yet")

    now = db.utcnow()
    if row is None:
        conn.execute(
            "INSERT INTO room_faces (room_id, interactor_id, showing,"
            " media_id, media_url, updated_at) VALUES (?,?,?,?,?,?)",
            (room_id, interactor_id, showing, keep_id, keep_url, now))
    else:
        conn.execute(
            "UPDATE room_faces SET showing=?, media_id=?, media_url=?,"
            " updated_at=? WHERE room_id=? AND interactor_id=?",
            (showing, keep_id, keep_url, now, room_id, interactor_id))
    conn.commit()
    return one(room_id, interactor_id)


def clear(room_id: str, interactor_id: str) -> dict:
    """Back to a name in a box. The picture goes with it — taking your face
    down is the one action where keeping the file would be the surprise."""
    conn = db.connect()
    conn.execute("DELETE FROM room_faces WHERE room_id=? AND interactor_id=?",
                 (room_id, interactor_id))
    conn.commit()
    return {"room_id": room_id, "interactor_id": interactor_id,
            "showing": DEFAULT, "means": SHOWING[DEFAULT]}


def one(room_id: str, interactor_id: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM room_faces WHERE room_id=? AND interactor_id=?",
        (room_id, interactor_id)).fetchone()
    if row is None:
        return {"room_id": room_id, "interactor_id": interactor_id,
                "showing": DEFAULT, "means": SHOWING[DEFAULT],
                "media_url": None, "media_id": None, "ai_marked": False}
    return _read(row)


def _read(row) -> dict:
    return {
        "room_id": row["room_id"],
        "interactor_id": row["interactor_id"],
        "showing": row["showing"],
        "means": SHOWING[row["showing"]],
        "media_id": row["media_id"],
        "media_url": row["media_url"],
        # A person's own photograph, and a person's own camera. Neither is
        # synthetic media and neither carries the mark. The profiles sharing
        # this room do carry theirs, from `avatars` — the mark belongs to what
        # is being depicted, not to the box it is drawn in.
        "ai_marked": False,
        "since": row["updated_at"],
    }


def showing_in(room_id: str) -> dict:
    """Everybody's box, for everybody in the room.

    Returned as a mapping keyed on the person so a client can draw a seat
    whose face nobody has set — the seats are the room's list, not this
    table's. A person with no row here is showing ``voice``, which is a box.
    """
    rows = db.connect().execute(
        "SELECT * FROM room_faces WHERE room_id=? ORDER BY updated_at, rowid",
        (room_id,)).fetchall()
    faces = {r["interactor_id"]: _read(r) for r in rows}
    on_camera = sum(1 for f in faces.values() if f["showing"] == "camera")
    return {
        "room_id": room_id,
        "faces": faces,
        "default": DEFAULT,
        "vocabulary": [{"showing": k, "means": v} for k, v in SHOWING.items()],
        "on_camera": on_camera,
        # Said in words rather than left for a client to compose, because the
        # sentence is the point: the quiet people are still here.
        "note": ("nobody here has turned a camera on" if not on_camera else
                 f"{on_camera} camera(s) live in this room. Everybody else "
                 "has a box too — a name in a box is a person in the room"),
    }


# No `close_room` here, deliberately. `overlays.close_place` exists because
# desks, parties and connections all have a route that ends them, and a
# disguise must not outlive the conversation it was worn in. A room has a
# `closed` status in its schema and **nothing in this codebase sets it** —
# there is no close route to hook a sweep to. Writing one anyway would be a
# rule with no enforcement point, which reads as protection and is not; the
# day a room learns how to close, the sweep belongs in that route.

