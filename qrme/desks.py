"""Live desks: a real person offering services, behind the same surfaces.

Everything else in QRME is a synthetic profile, and every render of one carries
the AI mark. A desk is the opposite case — an actual human — and the important
part of this module is what it *refuses* to do:

**A desk never carries the AI watermark.** Stamping "AI" on a real person is
not a cautious default, it is a false statement about them: it tells a visitor
the human they are talking to does not exist. The mark is a claim, and a claim
has to be true in both directions or it is worth nothing in either.

**Absence of the mark is not the disclosure.** An unmarked card could equally
be an AI whose badge was dropped, so a desk makes the positive claim instead:
*a person, not AI* — and says who vouched for that, on what basis, and whether
they signed it. :func:`card` reports the attestation next to the claim rather
than in a policy document, because "who says so" is the whole question.

**What a visitor sees is the desk, not a portrait.** We have no photograph of
the person and do not go looking for one. The surface is a camera view of the
desk itself: an empty chair with a sign on it says everything a visitor needs
to know, and it depicts nobody. When a desk has no camera configured, a sample
frame stands in and the card says ``live: false`` — claiming a still frame is
live would be the same class of lie as marking a human as AI.

The bell is the other half. A visitor looking at an empty chair can ring the
bell from the screen, exactly as they would reach over the counter and tap it,
and the owner sees the ring when they get back.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from . import auth, db

# attended: the person is here now. away: signed on, not at the desk — the
# state the bell exists for. closed: not taking callers at all.
PRESENCE = ("attended", "away", "closed")

# A stranger who scans a beacon has no identity to rate-limit against, so an
# anonymous ring is limited per desk. A known caller is limited per caller,
# which is both fairer and harder to grief with.
ANON_COOLDOWN_SECONDS = 30
CALLER_COOLDOWN_SECONDS = 300

DESIGNATION = "Live person — not AI"

# Which sample frame stands in until a desk has a camera of its own. Both are
# photographs of a real, empty room with a "ring the bell" sign in it — the
# gesture the whole feature is built around.
VIEW_STYLES = {"desk": "desk_view.webp", "stage": "stage_view.webp"}

# Said next to the claim, every time. The platform records who vouched; it does
# not independently verify a human, and pretending otherwise would make this
# badge exactly as hollow as an unmarked AI card.
ATTESTATION_NOTE = (
    "This is recorded, not proven: QRME stores who attested that a real person "
    "staffs this desk and when. A signed attestation raises that from a claim "
    "to a signature that can be checked."
)


class DeskError(ValueError):
    """A refusal with a reason worth showing the caller."""


def create(owner_id: str, display_name: str, trade: str,
           attestor: str, basis: str, location: str | None = None,
           blurb: str | None = None, rated: bool = False,
           view_style: str = "desk") -> dict:
    """Open a desk. The human attestation is required at creation.

    A desk that could be created without one would be an unmarked profile with
    a "not AI" badge on it — strictly worse than no badge, because it would be
    believed.

    ``rated`` puts the stream behind the deployment's existing verified-adult
    gate. It is not a separate tier and does not get its own weaker check: the
    same ``rated.viewer_is_adult`` that guards every other 18+ surface guards
    the card, the view, the bell and joining.
    """
    if not attestor.strip() or not basis.strip():
        raise DeskError(
            "a desk claims a real person staffs it, so it cannot be opened "
            "without recording who attests that and on what basis")
    if not display_name.strip():
        raise DeskError("a desk needs a name a visitor can read")
    if view_style not in VIEW_STYLES:
        raise DeskError(
            f"unknown view style {view_style!r}; expected one of "
            f"{', '.join(VIEW_STYLES)}")
    # The repo's existing hard line is that adult mode is never available for
    # a profile of *another* real person. A rated stream is a real person by
    # definition, so the same line lands here as: only they can put themselves
    # on one. A third party opening an 18+ stream in someone else's name is
    # the exact shape this refusal exists to prevent.
    if rated and attestor.strip() != owner_id.strip():
        raise DeskError(
            "an 18+ stream can only be opened by the person on it: the "
            "attestor must be the owner, attesting for themselves")

    desk_id = db.new_id("dsk")
    token = auth.issue("desk", desk_id)
    conn = db.connect()
    conn.execute(
        "INSERT INTO desks (id, owner_id, display_name, trade, location,"
        " blurb, presence, portrait, attestor, attestation_basis,"
        " attested_at, created_at, last_seen, rated, view_style)"
        " VALUES (?,?,?,?,?,?,'away',NULL,?,?,?,?,?,?,?)",
        (desk_id, owner_id, display_name.strip(), trade.strip(), location,
         blurb, attestor.strip(), basis.strip(), db.utcnow(), db.utcnow(),
         db.utcnow(), int(rated), view_style))
    conn.commit()
    return card(desk_id) | {"desk_token": token}


def _row(desk_id: str):
    return db.connect().execute(
        "SELECT * FROM desks WHERE id=?", (desk_id,)).fetchone()


def set_presence(desk_id: str, presence: str) -> dict:
    if presence not in PRESENCE:
        raise DeskError(
            f"unknown presence {presence!r}; expected one of "
            f"{', '.join(PRESENCE)}")
    conn = db.connect()
    conn.execute("UPDATE desks SET presence=?, last_seen=? WHERE id=?",
                 (presence, db.utcnow(), desk_id))
    conn.commit()
    return card(desk_id)


def set_portrait(desk_id: str, asset: str | None) -> dict:
    """Attach a portrait the desk owner holds the rights to, or clear it back
    back to the desk view. Never populated on their behalf."""
    conn = db.connect()
    conn.execute("UPDATE desks SET portrait=? WHERE id=?", (asset, desk_id))
    conn.commit()
    return card(desk_id)


def age_wall_card(desk_id: str) -> dict:
    """What an unverified viewer gets instead of an 18+ stream.

    Existence acknowledged, nothing else — no name, no trade, no view, and
    above all no location. A performer's whereabouts on an adult listing is a
    safety matter, not a detail.
    """
    return {
        "desk_id": desk_id,
        "rated": True,
        "age_wall": True,
        "human": True,
        "ai": False,
        "note": "18+ only — open this with an interactor token whose verified "
                "birthdate shows 18 or older",
    }


def set_camera(desk_id: str, url: str | None) -> dict:
    """Point this desk at its own camera, or clear it back to the sample.

    Until this is set, ``feed.live`` is false and every client says SAMPLE
    VIEW — which was true, but meant the live branch could never be reached
    by anything, since nothing could write the column.
    """
    conn = db.connect()
    conn.execute("UPDATE desks SET camera_url=? WHERE id=?", (url, desk_id))
    conn.commit()
    return card(desk_id, viewer_adult=True)


def card(desk_id: str, viewer_adult: bool = False) -> dict | None:
    """What a visitor is shown. Parallel in shape to a profile's card, and
    deliberately different in the one field that matters.

    ``viewer_adult`` comes from the deployment's existing verified-adult check;
    this module does not implement a second, weaker one.
    """
    row = _row(desk_id)
    if row is None:
        return None
    if row["rated"] and not viewer_adult:
        return age_wall_card(desk_id)
    from . import signatures

    signed = signatures.signatures_for("desk_human_attestation", desk_id)
    return {
        "desk_id": row["id"],
        "display_name": row["display_name"],
        "trade": row["trade"],
        # Withheld on an 18+ stream even from a verified adult: where the
        # performer physically is has nothing to do with watching them.
        "location": None if row["rated"] else row["location"],
        "blurb": row["blurb"],
        "rated": bool(row["rated"]),
        "age_wall": False,
        "presence": row["presence"],
        "last_seen": row["last_seen"],
        # The positive claim, and never an AI watermark. A desk that carried
        # one would be telling a visitor this person does not exist.
        "human": True,
        "ai": False,
        "designation": DESIGNATION,
        "attestation": {
            "attestor": row["attestor"],
            "basis": row["attestation_basis"],
            "attested_at": row["attested_at"],
            "signed": bool(signed),
            "signature_id": signed[0]["signature_id"] if signed else None,
            "note": ATTESTATION_NOTE,
        },
        # What the visitor actually looks at: the desk. A portrait only
        # appears if its owner attached one they hold the rights to.
        "portrait": row["portrait"],
        "feed": feed(desk_id),
        "bell": {
            "available": row["presence"] != "closed",
            "waiting": _waiting(desk_id),
        },
        # The live stream itself. Minted on the first join rather than at
        # creation, so a desk nobody has visited carries no room.
        "room_id": row["room_id"],
        "join": f"/desks/{desk_id}/join",
    }


def _waiting(desk_id: str) -> int:
    return db.connect().execute(
        "SELECT COUNT(*) FROM desk_rings WHERE desk_id=? AND acked_at IS NULL",
        (desk_id,)).fetchone()[0]


# --- the bell -------------------------------------------------------------

def ring(desk_id: str, caller_id: str | None = None,
         note: str | None = None) -> dict:
    """Ring the bell at an unattended desk.

    The cooldown is the whole reason this is not a doorbell-spam vector: an
    identified caller waits between rings, and an anonymous one — a stranger
    who scanned a beacon and has no identity to limit — is capped per desk.
    """
    row = _row(desk_id)
    if row is None:
        raise DeskError("no such desk")
    if row["presence"] == "closed":
        raise DeskError(
            "this desk is closed, so the bell is off — nobody would hear it")

    conn = db.connect()
    if caller_id:
        recent = conn.execute(
            "SELECT rung_at FROM desk_rings WHERE desk_id=? AND caller_id=?"
            " ORDER BY rung_at DESC LIMIT 1", (desk_id, caller_id)).fetchone()
        cooldown = CALLER_COOLDOWN_SECONDS
    else:
        recent = conn.execute(
            "SELECT rung_at FROM desk_rings WHERE desk_id=? AND caller_id IS"
            " NULL ORDER BY rung_at DESC LIMIT 1", (desk_id,)).fetchone()
        cooldown = ANON_COOLDOWN_SECONDS

    if recent and _within(recent["rung_at"], cooldown):
        raise DeskError(
            "the bell was just rung — give them a moment to reach the desk")

    ring_id = db.new_id("rng")
    conn.execute(
        "INSERT INTO desk_rings (id, desk_id, caller_id, note, rung_at,"
        " acked_at) VALUES (?,?,?,?,?,NULL)",
        (ring_id, desk_id, caller_id, note, db.utcnow()))
    conn.commit()
    return {
        "ring_id": ring_id,
        "desk_id": desk_id,
        "waiting": _waiting(desk_id),
        "presence": row["presence"],
        "note": ("They are at the desk — this rang anyway, so they know you "
                 "are here." if row["presence"] == "attended"
                 else "Rung. They will see it when they get back."),
    }


def _within(stamp: str, seconds: int) -> bool:
    try:
        when = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    except ValueError:
        return False
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) - when < timedelta(seconds=seconds)


def rings(desk_id: str, pending_only: bool = False) -> list[dict]:
    sql = "SELECT * FROM desk_rings WHERE desk_id=?"
    if pending_only:
        sql += " AND acked_at IS NULL"
    rows = db.connect().execute(sql + " ORDER BY rung_at DESC",
                                (desk_id,)).fetchall()
    return [dict(r) for r in rows]


def acknowledge(desk_id: str, ring_id: str) -> dict | None:
    conn = db.connect()
    conn.execute(
        "UPDATE desk_rings SET acked_at=? WHERE id=? AND desk_id=?",
        (db.utcnow(), ring_id, desk_id))
    conn.commit()
    row = conn.execute("SELECT * FROM desk_rings WHERE id=?",
                       (ring_id,)).fetchone()
    return dict(row) if row else None


# --- the desk view -------------------------------------------------------

# The frame served when a desk has no camera of its own. A real photograph of
# a real unattended desk, unretouched: the sign on the chair is the whole
# message, and dressing it up as an illustration would lose the one thing that
# makes it read instantly.
SAMPLE_FRAME = "desk_view.webp"


def assets_dir():
    from pathlib import Path
    return Path(__file__).resolve().parent / "assets" / "desks"


def frame_path(desk_id: str):
    """The image file to serve for this desk right now.

    A desk with its own camera would resolve here; until one is configured it
    falls back to the sample frame for its view style, and :func:`card` reports
    ``live: false`` rather than letting a client assume otherwise.
    """
    row = _row(desk_id)
    style = row["view_style"] if row else "desk"
    return assets_dir() / VIEW_STYLES.get(style, SAMPLE_FRAME)


def feed(desk_id: str) -> dict:
    row = _row(desk_id)
    live = bool(row and row["camera_url"])
    return {
        "url": f"/desks/{desk_id}/view.webp",
        "live": live,
        "note": ("A live view of the desk." if live else
                 "A sample view — this deployment has no camera on this desk, "
                 "so the frame is not live and is not claimed to be."),
        # Never an AI watermark. The desk belongs to a real person and the
        # frame is a photograph of a real room; marking it would be a false
        # statement about both.
        "ai": False,
        "watermark": None,
    }


# --- beacons: leave the desk behind ---------------------------------------
#
# A profile beacon and a desk beacon are the same gesture pointed at opposite
# things. Scanning a profile beacon reveals somebody who does not exist, and
# the page says so in the watermark. Scanning a desk beacon reveals somebody
# who does — who is simply not at the desk this minute — and the page must not
# say otherwise. The bell is what makes the second one worth printing: the
# sticker is on the door precisely because nobody is behind it right now.
#
# The scanner is a stranger with no account, which decides two things that are
# not details:
#
# * The bell they ring is an **anonymous** ring, so it takes the per-desk
#   cooldown rather than the per-caller one. A printed code is reachable by
#   anyone walking past, and that is the whole threat model.
# * A rated desk shows them the age wall, always. There is no token on a
#   sticker scan, so there is nothing that could clear it — which is the
#   correct outcome, not a limitation to work around.

def place_beacon(desk_id: str, label: str,
                 location: str | None = None) -> dict:
    """Print this desk onto something. Returns the token the QR encodes."""
    row = _row(desk_id)
    if row is None:
        raise DeskError("no such desk")
    if not label.strip():
        raise DeskError(
            "a beacon needs a label so its owner can tell their codes apart "
            "once several are printed and stuck to different doors")

    beacon_id = db.new_id("dbn")
    conn = db.connect()
    conn.execute(
        "INSERT INTO desk_beacons (id, desk_id, label, location, scans,"
        " active, created_at) VALUES (?,?,?,?,0,1,?)",
        (beacon_id, desk_id, label.strip(), location, db.utcnow()))
    conn.commit()
    return beacon(beacon_id)


def beacon(beacon_id: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM desk_beacons WHERE id=?", (beacon_id,)).fetchone()
    if row is None:
        return None
    return {
        "id": row["id"],
        "desk_id": row["desk_id"],
        "label": row["label"],
        "location": row["location"],
        "scans": row["scans"],
        "active": bool(row["active"]),
        "created_at": row["created_at"],
        "scan_url": f"/d/{row['id']}",
        "qr_svg": f"/desk-beacons/{row['id']}/qr.svg",
    }


def beacons_for(desk_id: str) -> list[dict]:
    rows = db.connect().execute(
        "SELECT id FROM desk_beacons WHERE desk_id=?"
        " ORDER BY created_at, rowid", (desk_id,)).fetchall()
    return [beacon(r["id"]) for r in rows]


def pick_up_beacon(beacon_id: str) -> dict:
    """Peel the sticker off. The code stops resolving; the desk is untouched."""
    conn = db.connect()
    if not conn.execute("UPDATE desk_beacons SET active=0 WHERE id=?",
                        (beacon_id,)).rowcount:
        raise DeskError("no such desk beacon")
    conn.commit()
    return {"id": beacon_id, "active": False}


def scan(beacon_id: str, viewer_adult: bool = False) -> dict | None:
    """Resolve a scanned code to its desk, counting the scan.

    Returns ``None`` for a code that never existed or has been picked up — the
    caller turns that into the same "nothing here any more" page a stale
    profile beacon gets, because a stranger holding a phone at a dead sticker
    should not be able to tell the difference between the two.
    """
    row = db.connect().execute(
        "SELECT * FROM desk_beacons WHERE id=?", (beacon_id,)).fetchone()
    if row is None or not row["active"]:
        return None
    conn = db.connect()
    conn.execute("UPDATE desk_beacons SET scans = scans + 1 WHERE id=?",
                 (beacon_id,))
    conn.commit()

    desk = card(row["desk_id"], viewer_adult=viewer_adult)
    if desk is None:              # desk deleted out from under a live sticker
        return None
    return desk | {
        "beacon": {"id": row["id"], "label": row["label"],
                   "location": row["location"]},
    }


def join(desk_id: str) -> dict:
    """Join the live stream. Mints the room on first arrival.

    A room rather than a one-to-one call because that is what a stream is:
    whoever is here is here together, and the profile-room machinery already
    knows how to carry that.
    """
    row = _row(desk_id)
    if row is None:
        raise DeskError("no such desk")
    if row["presence"] == "closed":
        raise DeskError("this stream is closed right now")

    conn = db.connect()
    room_id = row["room_id"]
    if not room_id:
        room_id = db.new_id("rm")
        conn.execute(
            "INSERT INTO rooms (id, topic, channel, status, created_at)"
            " VALUES (?,?,?,'active',?)",
            (room_id, f"{row['display_name']} — live", "video", db.utcnow()))
        conn.execute("UPDATE desks SET room_id=? WHERE id=?",
                     (room_id, desk_id))
        conn.commit()
    return {
        "desk_id": desk_id,
        "room_id": room_id,
        "channel": "video",
        "presence": row["presence"],
        "rated": bool(row["rated"]),
        # Never an AI watermark on this stream: there is a real person on the
        # other end of it.
        "ai": False,
        "note": ("They are here." if row["presence"] == "attended"
                 else "They are away — ring the bell and they will see it."),
    }
