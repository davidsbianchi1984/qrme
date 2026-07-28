"""Channel 3: pointing your camera at the thing, so somebody else can see it.

Channel 2 lent the profiles an ear. This lends an eye — a live view through
the camera in your hand, for the enormous class of problems where describing
the thing is the hard part and showing it is trivial. A mechanic looking at
your engine bay. A plumber watching you point at the joint. An electrician
reading the plate on a consumer unit. A vet watching a dog walk.

:mod:`qrme.capture` in JIM-mini is the still, sealed, asynchronous version of
this idea, and the difference is the whole module. **A photograph is one framed
moment somebody chose. A live camera is whatever happens to be behind it** —
the rest of the room, the post on the table, the other people in the house, the
child in the doorway. Somebody who agrees to "show you the leak" has not agreed
to any of that, and a session that treats the two as the same thing is a
surveillance feature with a helpful name.

**What the camera is pointed at decides the rules, not who is watching.**

That is the design, and it is the inversion of the obvious approach. The
obvious approach asks *is the viewer a person or a profile* and gates on that.
It gets the mechanic case wrong — a synthetic profile that can see an engine is
genuinely useful and the stakes are a car — and it gets the medical case wrong
in the other direction, because a real stranger watching a live view of
somebody's body is not made safe by being human. So :data:`SUBJECTS` is
declared per session and :data:`MAY_WATCH` is read from it.

**The viewer never controls the camera.** No remote zoom, no torch, no
capture trigger, no "hold still". The person holding the phone points it, and
:data:`NEVER` says so out loud. A remote party who can operate the camera on
somebody's device has something categorically different from a view, and it is
the thing people are actually afraid of when they decline.

**Ephemeral unless somebody says otherwise.** A live view is not a recording,
and `record` is a separate decision with its own consent — refused outright
where the subject is a person and the viewer is synthetic. A session that
quietly kept what it saw would make every future "can you show me" a worse
bargain than it looked.

**It ends, and it ends from the holder's side.** A duration cap, an explicit
stop, and the session dies with the surface it was opened on — the same rule
`roommic` applies to a lent microphone, for the same reason: a permission that
outlives the conversation justifying it is not a permission, it is an
installation.

**Bystanders are the unsolved part, and the module says so** rather than
implying otherwise. Nothing here can tell whether somebody walked into frame.
What it can do is refuse to pretend: :func:`open_session` records what the
holder declared, the disclosure names it, and the guidance is written for the
person holding the camera because they are the only one who can actually see
the room.
"""

from __future__ import annotations

from . import db

# What the camera is pointed at. Declared by the person holding it, because
# they are the only party who knows — and everything else reads from this.
SUBJECTS: dict[str, dict] = {
    "object": {
        "means": "a thing — an engine, a boiler, a board, a leak, a part",
        "bystander_risk": "low: a thing does not have a face, though a "
                          "workshop might",
    },
    "place": {
        "means": "a room, a site, a property, a yard",
        "bystander_risk": "high: whoever is in the room is in the shot, and "
                          "they did not agree to anything",
    },
    "document": {
        "means": "paper, a screen, a serial plate, a meter reading",
        "bystander_risk": "low, but a document carries names, numbers and "
                          "addresses that a photograph of an engine does not",
    },
    "person": {
        "means": "a body, a face, an injury, how somebody is moving",
        "bystander_risk": "the subject *is* a person — see MAY_WATCH",
    },
}

# Who may watch what. Read from the subject, not from the viewer's convenience.
#
# The mechanic case is the one that justifies this module and it is fully
# open: a synthetic profile looking at an engine bay is useful and the stakes
# are a car. The `person` row is the one that matters — a live view of
# somebody's body goes to a human being who is accountable for what they do
# with it, or it goes nowhere. JIM-mini reaches the same conclusion from the
# other direction in `jim/capture.py`, where a still photograph of a rash is
# never handed to an agent.
MAY_WATCH: dict[str, dict] = {
    "object": {"person": True, "profile": True},
    "document": {"person": True, "profile": True},
    "place": {"person": True, "profile": True},
    "person": {"person": True, "profile": False},
}

REFUSAL_PROFILE_ON_PERSON = (
    "a live view of somebody's body goes to a person, not to a synthetic "
    "profile. A profile watching a body in real time would be making "
    "judgements about it with no examination, no accountability and nobody to "
    "answer for being wrong — and unlike a still, there is no moment somebody "
    "chose to send. Invite a real person to this session, or use a still and "
    "send it to a clinician."
)

# Where a session can be opened. The same surface vocabulary as `overlays` and
# `roommic`, deliberately — three features naming the same places three ways
# is how a disclosure ends up on the wrong one.
SURFACES: dict[str, str] = {
    "room": "a room — voice, video, AR, VR or 3-D",
    "connection": "a one-to-one connection",
    "desk": "a live desk's stream",
    "exchange": "an agreed exchange of work",
}

VIEWERS = ("person", "profile")

# What a viewer never gets, whoever they are. Published so a client can say so
# before somebody decides, rather than after.
NEVER: dict[str, str] = {
    "camera_control": "the viewer cannot zoom, focus, switch lens or turn on "
                      "the torch — the person holding the phone points it",
    "capture_trigger": "the viewer cannot take a photograph or start a "
                       "recording from their side",
    "other_cameras": "sharing yours does not open theirs, and does not reach "
                     "any other camera on your device or network",
    "location": "the view carries no coordinates; where you are is not part "
                "of what you agreed to show",
    "background_start": "a session cannot begin without the holder starting "
                        "it in the moment — there is no standing permission",
    "silent_run": "the holder's own screen shows the session live for its "
                  "whole duration; there is no state where it is on and not "
                  "visible to them",
}

# A cap, and a reason. Long enough to look at an engine properly, short enough
# that a forgotten session is measured in minutes rather than a working day.
MAX_MINUTES = 45
DEFAULT_MINUTES = 15

STATES = ("live", "ended", "expired")


class ViewfinderError(ValueError):
    """A camera share that cannot be opened. Text meant for a person."""


def may_watch(subject: str, viewer: str) -> bool:
    if subject not in SUBJECTS:
        raise ViewfinderError(
            f"unknown subject {subject!r}; one of {', '.join(SUBJECTS)}")
    if viewer not in VIEWERS:
        raise ViewfinderError(
            f"unknown viewer kind {viewer!r}; one of {', '.join(VIEWERS)}")
    return MAY_WATCH[subject][viewer]


def vocabulary() -> dict:
    """Everything a client needs to draw the flow, refusals included by name.

    A client that knew only the allowed combinations would render a refused
    one as a missing feature rather than a decision, which is the same
    argument `roommic` makes for publishing its refused microphone types.
    """
    return {
        "subjects": SUBJECTS,
        "may_watch": MAY_WATCH,
        "viewers": list(VIEWERS),
        "surfaces": SURFACES,
        "never": NEVER,
        "max_minutes": MAX_MINUTES,
        "default_minutes": DEFAULT_MINUTES,
        "records_by_default": False,
        "refusals": {"profile_on_person": REFUSAL_PROFILE_ON_PERSON},
        "bystanders": bystander_guidance("place"),
    }


def bystander_guidance(subject: str) -> dict:
    """What this cannot solve, said plainly.

    Nothing here can tell whether somebody walked into frame. Pretending
    otherwise — a "bystander detection" toggle, a promise about blurring —
    would be worse than the gap, because it would be relied on. So the honest
    version is a note addressed to the only party who can actually see the
    room.
    """
    if subject not in SUBJECTS:
        raise ViewfinderError(f"unknown subject {subject!r}")
    return {
        "subject": subject,
        "risk": SUBJECTS[subject]["bystander_risk"],
        "we_cannot": "tell whether somebody has walked into shot, or blur "
                     "them if they have",
        "you_can": "look at the room before you start, and stop the session "
                   "the moment it stops being about the thing",
        "why_it_is_yours": "you are the only party who can see the room; a "
                           "promise from us about who is in frame would be a "
                           "promise about something we cannot observe",
    }


def open_session(holder_id: str, surface: str, surface_id: str,
                 subject: str, viewer_kind: str, viewer_id: str,
                 minutes: int = DEFAULT_MINUTES, record: bool = False,
                 bystanders_declared: str | None = None,
                 note: str | None = None) -> dict:
    """Start a live view. Ephemeral, capped, and the holder's to end."""
    if surface not in SURFACES:
        raise ViewfinderError(
            f"unknown surface {surface!r}; one of {', '.join(SURFACES)}")
    if not surface_id:
        raise ViewfinderError("a session belongs to a place — name it")
    if subject not in SUBJECTS:
        raise ViewfinderError(
            f"unknown subject {subject!r}; one of {', '.join(SUBJECTS)}")
    if viewer_kind not in VIEWERS:
        raise ViewfinderError(
            f"unknown viewer kind {viewer_kind!r}; one of {', '.join(VIEWERS)}")
    if not may_watch(subject, viewer_kind):
        raise ViewfinderError(REFUSAL_PROFILE_ON_PERSON)
    if not 1 <= minutes <= MAX_MINUTES:
        raise ViewfinderError(
            f"a session runs between 1 and {MAX_MINUTES} minutes")
    if record and subject == "person" and viewer_kind == "profile":
        # Unreachable while `may_watch` refuses the pair, and kept anyway: a
        # second guard costs nothing and the day somebody widens the table is
        # exactly the day this matters.
        raise ViewfinderError(REFUSAL_PROFILE_ON_PERSON)

    session_id = db.new_id("vwf")
    conn = db.connect()
    conn.execute(
        "INSERT INTO camera_sessions (id, holder_id, surface, surface_id,"
        " subject, viewer_kind, viewer_id, minutes, recording, bystanders,"
        " note, state, opened_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,'live',?)",
        (session_id, holder_id, surface, surface_id, subject, viewer_kind,
         viewer_id, minutes, int(bool(record)), bystanders_declared, note,
         db.utcnow()))
    conn.commit()
    return session(session_id)


def session(session_id: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM camera_sessions WHERE id=?", (session_id,)).fetchone()
    if row is None:
        raise ViewfinderError("no such session")
    d = dict(row)
    d["recording"] = bool(d["recording"])
    d["subject_means"] = SUBJECTS[d["subject"]]["means"]
    d["live"] = d["state"] == "live"
    d["never"] = dict(NEVER)
    d["bystanders_note"] = bystander_guidance(d["subject"])
    return d


def close(session_id: str, by: str) -> dict:
    """End it. The holder may always; the viewer may end their own watching.

    Asymmetric on purpose, and the same shape `sharing.py` uses for a lent
    skill: two parties to open, one to close. Symmetric consent to start makes
    it a loan; asymmetric consent to end is what stops it being a trap.
    """
    row = session(session_id)
    if by not in (row["holder_id"], row["viewer_id"]):
        raise ViewfinderError("only the holder or the viewer can end this")
    conn = db.connect()
    conn.execute("UPDATE camera_sessions SET state='ended', ended_at=?,"
                 " ended_by=? WHERE id=? AND state='live'",
                 (db.utcnow(), by, session_id))
    conn.commit()
    return session(session_id)


def close_place(surface: str, surface_id: str) -> int:
    """Every session on a surface that has ended.

    A camera share must not outlive the room it was opened in — `roommic`
    closes a lent microphone the same way, for the reason that applies harder
    to a lens: nobody remembers a permission granted inside a conversation
    that finished.
    """
    conn = db.connect()
    cur = conn.execute(
        "UPDATE camera_sessions SET state='expired', ended_at=?,"
        " ended_by='surface' WHERE surface=? AND surface_id=? AND"
        " state='live'", (db.utcnow(), surface, surface_id))
    conn.commit()
    return cur.rowcount


def live_on(surface: str, surface_id: str) -> list[dict]:
    rows = db.connect().execute(
        "SELECT id FROM camera_sessions WHERE surface=? AND surface_id=? AND"
        " state='live' ORDER BY opened_at", (surface, surface_id)).fetchall()
    return [session(r["id"]) for r in rows]


def disclosure_on(surface: str, surface_id: str) -> dict:
    """What everybody on this surface is shown.

    The disclosure is the design, so it is a first-class read rather than
    something a client assembles: a camera that is live and undisclosed is the
    entire failure mode, and `roommic` learned that its own disclosure route
    had no authorization on it precisely because it was treated as decoration.
    """
    live = live_on(surface, surface_id)
    return {
        "surface": surface,
        "surface_id": surface_id,
        "live": [
            {"session_id": s["id"], "holder_id": s["holder_id"],
             "showing": s["subject"], "means": s["subject_means"],
             "watched_by": s["viewer_id"], "viewer_kind": s["viewer_kind"],
             "recording": s["recording"], "since": s["opened_at"]}
            for s in live],
        "any_live": bool(live),
        "any_recording": any(s["recording"] for s in live),
        "note": ("a camera is live on this surface — the holder points it, "
                 "and no viewer can control it" if live else
                 "no camera is being shared here"),
    }


def for_holder(holder_id: str, include_ended: bool = False) -> list[dict]:
    sql = "SELECT id FROM camera_sessions WHERE holder_id=?"
    if not include_ended:
        sql += " AND state='live'"
    rows = db.connect().execute(sql + " ORDER BY opened_at DESC",
                                (holder_id,)).fetchall()
    return [session(r["id"]) for r in rows]
