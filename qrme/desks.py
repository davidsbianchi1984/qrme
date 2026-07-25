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

import html
import json
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
           blurb: str | None = None) -> dict:
    """Open a desk. The human attestation is required at creation.

    A desk that could be created without one would be an unmarked profile with
    a "not AI" badge on it — strictly worse than no badge, because it would be
    believed.
    """
    if not attestor.strip() or not basis.strip():
        raise DeskError(
            "a desk claims a real person staffs it, so it cannot be opened "
            "without recording who attests that and on what basis")
    if not display_name.strip():
        raise DeskError("a desk needs a name a visitor can read")

    desk_id = db.new_id("dsk")
    token = auth.issue("desk", desk_id)
    conn = db.connect()
    conn.execute(
        "INSERT INTO desks (id, owner_id, display_name, trade, location,"
        " blurb, presence, portrait, attestor, attestation_basis,"
        " attested_at, created_at, last_seen)"
        " VALUES (?,?,?,?,?,?,'away',NULL,?,?,?,?,?)",
        (desk_id, owner_id, display_name.strip(), trade.strip(), location,
         blurb, attestor.strip(), basis.strip(), db.utcnow(), db.utcnow(),
         db.utcnow()))
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
    to the placeholder. Never populated on their behalf."""
    conn = db.connect()
    conn.execute("UPDATE desks SET portrait=? WHERE id=?", (asset, desk_id))
    conn.commit()
    return card(desk_id)


def card(desk_id: str) -> dict | None:
    """What a visitor is shown. Parallel in shape to a profile's card, and
    deliberately different in the one field that matters."""
    row = _row(desk_id)
    if row is None:
        return None
    from . import signatures

    signed = signatures.signatures_for("desk_human_attestation", desk_id)
    return {
        "desk_id": row["id"],
        "display_name": row["display_name"],
        "trade": row["trade"],
        "location": row["location"],
        "blurb": row["blurb"],
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

    A desk with its own camera would resolve here; until one is configured
    every desk falls back to the sample frame, and :func:`card` reports that
    rather than letting a client assume it is looking at a live view.
    """
    return assets_dir() / SAMPLE_FRAME


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


def listing(desk_id: str) -> str:
    """A compact JSON blob for embedding, kept parallel to the profile card so
    a surface can render either without branching on more than ``ai``."""
    return json.dumps(card(desk_id))
