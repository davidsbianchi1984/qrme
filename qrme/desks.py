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

import os
from datetime import datetime, timedelta, timezone

from . import auth, db, i18n, inbox


def _public_base() -> str:
    """Where this deployment is reachable from outside.

    Same environment variable the summon beacons read, deliberately: a desk
    code and a profile code are printed by the same person onto the same wall,
    and two sources of truth for "where is this deployment" is how one of them
    ends up pointing at localhost on a sticker.
    """
    return os.environ.get("QRME_PUBLIC_URL", "https://qrme.app").rstrip("/")

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
            i18n.fill(i18n.UNKNOWN_CHOICE_EXPECTED, field="view style", got=repr(view_style), choices=', '.join(VIEW_STYLES)))
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
            i18n.fill(i18n.UNKNOWN_CHOICE_EXPECTED, field="presence", got=repr(presence), choices=', '.join(PRESENCE)))
    conn = db.connect()
    conn.execute("UPDATE desks SET presence=?, last_seen=? WHERE id=?",
                 (presence, db.utcnow(), desk_id))
    conn.commit()
    if presence == "closed":
        # Any microphone lent to this desk's profiles goes back when the desk
        # closes. Scoped to the session that justified it — a grant that
        # survived closing would be live again the next time the desk opened,
        # for a conversation nobody has had yet.
        from . import roommic
        roommic.close_place("desk", desk_id)
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
        # Absolute, because `scan_url` is a description of what the printed QR
        # encodes — and the QR encodes an absolute URL, because a code on a
        # shop door has no origin to be relative to. Returning a bare path
        # here made the two disagree, and a console rendering it as a link
        # resolved it against its *own* origin: the desk screen's "open the
        # scan page" link went nowhere every time the console was served from
        # anywhere but the API, which is every packaged build. The summon
        # beacon next door has always returned this absolute.
        "scan_url": f"{_public_base()}/d/{row['id']}",
        # Still a path: this one is fetched as an `<img src>` against the API
        # the client is already talking to, not printed on anything.
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


# --- coming up on stream --------------------------------------------------
#
# Joining has two shapes, and conflating them would be the mistake. Watching
# and commenting is something a viewer simply does. Appearing *on* the stream
# is something the host lets them do — it puts a second person into a
# broadcast the host is answerable for, and there is no version of that which
# should happen without their yes.

JOIN_MODES = ("audience", "guest")
GUEST_STATES = ("requested", "accepted", "declined", "left")


def request_guest(desk_id: str, guest_id: str, display_name: str | None = None,
                  note: str | None = None) -> dict:
    """Ask to come up on stream. Nothing happens until the host accepts."""
    row = _row(desk_id)
    if row is None:
        raise DeskError("no such desk")
    if row["presence"] == "closed":
        raise DeskError("this stream is closed right now")

    conn = db.connect()
    open_req = conn.execute(
        "SELECT id FROM desk_guests WHERE desk_id=? AND guest_id=? AND"
        " status IN ('requested','accepted')", (desk_id, guest_id)).fetchone()
    if open_req is not None:
        raise DeskError(
            "you already have a hand up on this stream — one at a time, so a "
            "host reading the queue sees people rather than repeats")

    req_id = db.new_id("gst")
    conn.execute(
        "INSERT INTO desk_guests (id, desk_id, guest_id, display_name, note,"
        " status, requested_at, decided_at)"
        " VALUES (?,?,?,?,?, 'requested', ?, NULL)",
        (req_id, desk_id, guest_id, display_name, note, db.utcnow()))
    conn.commit()
    return guest_request(req_id)


def guest_request(req_id: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM desk_guests WHERE id=?", (req_id,)).fetchone()
    if row is None:
        return None
    return {
        "id": row["id"], "desk_id": row["desk_id"], "guest_id": row["guest_id"],
        "display_name": row["display_name"], "note": row["note"],
        "status": row["status"], "requested_at": row["requested_at"],
        "decided_at": row["decided_at"],
        "on_stream": row["status"] == "accepted",
    }


def guests(desk_id: str, pending_only: bool = False) -> list[dict]:
    sql = "SELECT id FROM desk_guests WHERE desk_id=?"
    if pending_only:
        sql += " AND status='requested'"
    rows = db.connect().execute(sql + " ORDER BY requested_at, rowid",
                                (desk_id,)).fetchall()
    return [guest_request(r["id"]) for r in rows]


def decide_guest(desk_id: str, req_id: str, accept: bool) -> dict:
    """The host's answer. Only they can give it — the router checks the token."""
    conn = db.connect()
    row = conn.execute(
        "SELECT * FROM desk_guests WHERE id=? AND desk_id=?",
        (req_id, desk_id)).fetchone()
    if row is None:
        raise DeskError("no such request")
    if row["status"] != "requested":
        raise DeskError(i18n.fill(i18n.REQUEST_ALREADY, status=i18n.Term(row['status'])))
    conn.execute("UPDATE desk_guests SET status=?, decided_at=? WHERE id=?",
                 ("accepted" if accept else "declined", db.utcnow(), req_id))
    conn.commit()
    # Acceptance reaches the guest's inbox; a decline does not. The yes is
    # an invitation to act — come up on stream — while telling somebody a
    # host said no delivers nothing they can do anything with.
    if accept:
        desk = conn.execute("SELECT owner_id FROM desks WHERE id=?",
                            (desk_id,)).fetchone()
        if desk is not None:
            inbox.note(row["guest_id"], "guest_accepted", desk["owner_id"],
                       desk_id)
    return guest_request(req_id)


def leave_stream(desk_id: str, guest_id: str) -> dict:
    """Step back down. A guest can always end their own appearance."""
    conn = db.connect()
    row = conn.execute(
        "SELECT id FROM desk_guests WHERE desk_id=? AND guest_id=? AND"
        " status='accepted'", (desk_id, guest_id)).fetchone()
    if row is None:
        raise DeskError("you are not on this stream")
    conn.execute("UPDATE desk_guests SET status='left', decided_at=?"
                 " WHERE id=?", (db.utcnow(), row["id"]))
    conn.commit()
    return guest_request(row["id"])


def on_stream(desk_id: str) -> list[dict]:
    return [g for g in guests(desk_id) if g["status"] == "accepted"]


def join(desk_id: str, mode: str = "audience") -> dict:
    """Join the live stream. Mints the room on first arrival.

    A room rather than a one-to-one call because that is what a stream is:
    whoever is here is here together, and the profile-room machinery already
    knows how to carry that.

    ``mode`` picks which of the two joins this is. ``audience`` is immediate.
    ``guest`` only *asks* — it returns the pending request, and the caller is
    in the audience until the host says yes. Returning a room that behaved as
    if the request had been granted would be the worst possible default.
    """
    if mode not in JOIN_MODES:
        raise DeskError(
            i18n.fill(i18n.UNKNOWN_CHOICE_EXPECTED, field="join mode", got=repr(mode), choices=', '.join(JOIN_MODES)))
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
        "mode": mode,
        # Both joins land in the same room; the difference is whether you are
        # *on* the stream or watching it. Reported so a client renders the
        # right thing without inferring it from the absence of something.
        "on_stream": False,
        "overlay": overlay(desk_id),
        "note": ("They are here." if row["presence"] == "attended"
                 else "They are away — ring the bell and they will see it."),
    }


def overlay(desk_id: str) -> dict:
    """What renders *over* the video rather than beside it.

    A live stream's chat, likes and gifts belong on top of the picture — that
    is where a viewer is already looking, and moving their eyes to a panel
    means missing the thing they came for. This returns the layer, so every
    client draws the same one instead of each inventing its own.
    """
    from . import audience, commerce

    room = _row(desk_id)
    room_id = room["room_id"] if room else None
    comments = []
    if room_id:
        rows = db.connect().execute(
            "SELECT sender_id, content FROM room_messages WHERE room_id=? AND"
            " status='approved' ORDER BY created_at DESC, rowid DESC LIMIT 6",
            (room_id,)).fetchall()
        comments = [{"who": r["sender_id"], "said": r["content"]}
                    for r in reversed(rows)]
    return {
        # Semi-transparent by design: the picture stays readable underneath,
        # which is the whole reason to put them here rather than in a panel.
        "style": {"opacity": 0.82, "over_video": True,
                  "anchor": "bottom-left"},
        "comments": comments,
        "likes": audience.likes("desk", desk_id),
        "shares": audience.share_count("desk", desk_id),
        "gifts": commerce.gifts_for("desk", desk_id)[:5],
        "gift_total": commerce.gift_total("desk", desk_id),
        "on_stream": on_stream(desk_id),
        "waiting": _waiting(desk_id),
    }


# --------------------------------------------------------------------------
# The service itself: connections across the counter.
#
# Everything above this line lets a person *reach* the desk — the card, the
# bell, the stream. None of it let the desk do the job it exists for. A
# repair counter's whole trade is "hand me the thing": the staffer takes the
# caller's screen, their machine, a program, and works on it. This is that,
# with the counter's physics kept: the desk may only *offer* to take
# something, the caller's accept is what hands it over, and either side can
# take it back at any moment.

CONNECTION_KINDS = ("screen_share", "remote_control", "app_access",
                    "file_drop")

#: What each kind means, in the words both parties are shown before either
#: agrees to it. Kept beside the code that enforces it so the sentence and
#: the behaviour cannot drift apart in two files.
KIND_MEANS = {
    "screen_share":   "they can see the screen you share, and nothing else",
    "remote_control": "they can operate the machine you name, within the "
                      "written scope, until either of you ends it",
    "app_access":     "they can use the named program on your behalf for "
                      "this session",
    "file_drop":      "they can send you files and receive the ones you "
                      "choose to hand over",
}


def _session_row(session_id: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM desk_sessions WHERE id=?", (session_id,)).fetchone()
    return dict(row) if row else None


def _connection_row(connection_id: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM desk_connections WHERE id=?",
        (connection_id,)).fetchone()
    return dict(row) if row else None


def _shape_connection(c: dict, *, with_token: bool = False) -> dict:
    out = {k: c[k] for k in ("id", "session_id", "kind", "target", "scope",
                             "status", "offered_at", "answered_at",
                             "ended_at", "ended_by")}
    out["means"] = KIND_MEANS.get(c["kind"])
    if with_token and c["status"] == "active":
        out["token"] = c["token"]
    return out


def open_session(desk_id: str, caller_id: str,
                 ring_id: str | None = None) -> dict:
    """The staffer answers: a session with one named caller.

    The caller must exist — a session is a pair of people, and half a pair
    is a monologue. If a ring is named it must be this desk's, so a session
    cannot launder a different desk's queue into its own history.
    """
    from .common import interactor_or_404  # local: avoid a module cycle
    if _row(desk_id) is None:
        raise DeskError("no such desk")
    try:
        interactor_or_404(caller_id)
    except Exception:
        raise DeskError("no such caller — sessions are with a real "
                        "interactor, not a free-typed name")
    if ring_id is not None:
        ring_row = db.connect().execute(
            "SELECT desk_id FROM desk_rings WHERE id=?",
            (ring_id,)).fetchone()
        if ring_row is None or ring_row["desk_id"] != desk_id:
            raise DeskError("that ring is not this desk's")
    session_id = db.new_id("dsn")
    conn = db.connect()
    conn.execute(
        "INSERT INTO desk_sessions (id, desk_id, caller_id, ring_id,"
        " opened_at) VALUES (?,?,?,?,?)",
        (session_id, desk_id, caller_id, ring_id, db.utcnow()))
    conn.commit()
    return session(session_id)


def session(session_id: str, *, for_caller: bool = False) -> dict:
    s = _session_row(session_id)
    if s is None:
        raise DeskError("no such session")
    rows = db.connect().execute(
        "SELECT * FROM desk_connections WHERE session_id=?"
        " ORDER BY offered_at", (session_id,)).fetchall()
    desk = _row(s["desk_id"])
    return {
        **{k: s[k] for k in ("id", "desk_id", "caller_id", "ring_id",
                             "status", "opened_at", "closed_at",
                             "closed_by")},
        "desk_name": desk["display_name"] if desk else None,
        "trade": desk["trade"] if desk else None,
        # The token rides only to the caller: it is *their* machine the desk
        # is being let into, so the secret that opens it is theirs to hold
        # and to hand to their own tooling. The desk's view shows status.
        "connections": [_shape_connection(dict(r), with_token=for_caller)
                        for r in rows],
    }


def sessions_for_desk(desk_id: str) -> list[dict]:
    rows = db.connect().execute(
        "SELECT id FROM desk_sessions WHERE desk_id=? ORDER BY opened_at"
        " DESC", (desk_id,)).fetchall()
    return [session(r["id"]) for r in rows]


def sessions_for_caller(caller_id: str) -> list[dict]:
    rows = db.connect().execute(
        "SELECT id FROM desk_sessions WHERE caller_id=? ORDER BY opened_at"
        " DESC", (caller_id,)).fetchall()
    return [session(r["id"], for_caller=True) for r in rows]


def offer_connection(session_id: str, kind: str, target: str,
                     scope: str | None = None) -> dict:
    """The desk proposes to connect something. A proposal is all it is:
    the row is born `offered`, carries no token, and grants nothing.

    `remote_control` requires a written scope. Driving somebody's machine
    under "whatever needs doing" is how a repair story becomes a horror
    story, and the scope is what the caller is shown when asked to agree.
    """
    s = _session_row(session_id)
    if s is None:
        raise DeskError("no such session")
    if s["status"] != "open":
        raise DeskError("this session is closed")
    if kind not in CONNECTION_KINDS:
        raise DeskError(i18n.fill(i18n.UNKNOWN_CHOICE_EXPECTED, field="connection kind", got=repr(kind), choices=', '.join(CONNECTION_KINDS)))
    if not (target or "").strip():
        raise DeskError("name what is being connected — a machine, a "
                        "program, a screen")
    if kind == "remote_control" and not (scope or "").strip():
        raise DeskError("remote control needs a written scope: what on the "
                        "machine may be touched, in words the caller will "
                        "be shown")
    cid = db.new_id("dcx")
    conn = db.connect()
    conn.execute(
        "INSERT INTO desk_connections (id, session_id, kind, target, scope,"
        " offered_at) VALUES (?,?,?,?,?,?)",
        (cid, session_id, kind, (target or "").strip(),
         (scope or "").strip() or None, db.utcnow()))
    conn.commit()
    return _shape_connection(_connection_row(cid))


def answer_connection(session_id: str, connection_id: str,
                      accept: bool) -> dict:
    """The caller's yes or no. Accepting mints the link token — the first
    moment one exists — and it is returned to the caller alone."""
    c = _connection_row(connection_id)
    if c is None or c["session_id"] != session_id:
        raise DeskError("no such connection in this session")
    s = _session_row(session_id)
    if s["status"] != "open":
        raise DeskError("this session is closed")
    if c["status"] != "offered":
        raise DeskError(i18n.fill(i18n.CONNECTION_NOT_AWAITING, status=i18n.Term(c['status'])))
    conn = db.connect()
    if not accept:
        conn.execute(
            "UPDATE desk_connections SET status='declined', answered_at=?"
            " WHERE id=?", (db.utcnow(), connection_id))
        conn.commit()
        return _shape_connection(_connection_row(connection_id))
    token = db.new_id("dlk")
    conn.execute(
        "UPDATE desk_connections SET status='active', token=?, answered_at=?"
        " WHERE id=?", (token, db.utcnow(), connection_id))
    conn.commit()
    return _shape_connection(_connection_row(connection_id), with_token=True)


def end_connection(session_id: str, connection_id: str, by: str) -> dict:
    """Either side hangs up. The token is NULLed, not flagged — an ended
    connection has no secret left to present."""
    c = _connection_row(connection_id)
    if c is None or c["session_id"] != session_id:
        raise DeskError("no such connection in this session")
    if c["status"] != "active":
        raise DeskError(i18n.fill(i18n.CONNECTION_NOT_ACTIVE, status=i18n.Term(c['status'])))
    conn = db.connect()
    conn.execute(
        "UPDATE desk_connections SET status='ended', token=NULL, ended_at=?,"
        " ended_by=? WHERE id=?", (db.utcnow(), by, connection_id))
    conn.commit()
    return _shape_connection(_connection_row(connection_id))


def close_session(session_id: str, by: str) -> dict:
    """Either side closes the counter. Every live connection ends with it —
    a session is the reason the links exist, and links must not outlive
    their reason. The same rule reaches the *skill grants* lent on this
    session: `sharing.close_surface` is called here the way exchanges and
    watch parties already call it, because leaving that to each caller to
    remember is how one of them forgets."""
    from . import sharing
    s = _session_row(session_id)
    if s is None:
        raise DeskError("no such session")
    if s["status"] == "closed":
        return session(session_id)
    conn = db.connect()
    for row in conn.execute(
            "SELECT id FROM desk_connections WHERE session_id=? AND"
            " status='active'", (session_id,)).fetchall():
        end_connection(session_id, row["id"], by)
    conn.execute(
        "UPDATE desk_sessions SET status='closed', closed_at=?, closed_by=?"
        " WHERE id=?", (db.utcnow(), by, session_id))
    conn.commit()
    sharing.close_surface("desk_session", session_id)
    return session(session_id)


def connection_token_live(token: str) -> bool:
    """Whether a presented link token opens anything right now. The check a
    desk's own tooling makes before letting a hand onto a machine."""
    row = db.connect().execute(
        "SELECT id FROM desk_connections WHERE token=? AND status='active'",
        (token,)).fetchone()
    return row is not None
