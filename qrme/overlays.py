"""Wearing a character over your own camera.

A person points a camera at themselves and appears as something else — a mask,
a full character, a puppet driven by their own face, a replaced background.
Ordinary, fun, and on this platform it lands directly on the one argument
everything else here is built from: **a synthetic thing must say so.**

An overlay is synthetic media composited onto a real human face in real time.
That is the definition of the thing the AI mark exists for, and the fact that
the person underneath consented does not change what the viewer is looking at.
So the rule is not "overlays are allowed" or "overlays are banned". It is:

**An overlay is disclosed to the people who can see it, always, and it can
never be the thing that makes a truthful badge false.**

Three consequences, and the third is the one that took the most thinking.

**Disclosure rides with the stream, not with the settings screen.** :func:`worn`
is what a surface renders, and it carries the mark. A viewer who joined late,
or who is watching on a client nobody here wrote, still sees that the face is
not the face.

**No overlay may depict a real, identifiable person.** Not a catalogue gap —
a refusal. A live-driven likeness of somebody who is not in the room is the
exact artefact this whole codebase argues against, and "it was only a filter"
is how it would arrive. :data:`REFUSED` names the classes with the reason.

**A live desk cannot wear one at all.** This is the sharp case. A desk's badge
reads *"Live person — not AI"* (``desks.DESIGNATION``) and its whole premise is
that a real human is behind it — the badge is inverted precisely because there
is a person there. Put a character over that face and the badge becomes a false
statement, made by the platform, on the one surface whose entire value is that
the statement is true. The overlay is refused rather than the badge weakened,
because a desk that cannot promise a real person is not a desk.

Rendering is on the device, like capture. What lives here is which overlay a
person is wearing where, what it is allowed to be, and what every viewer must
be told about it.
"""

from __future__ import annotations

from . import db

# What a person may put over their own face, and what each actually is.
#
# The split that matters is not stylistic. `mask` and `character` replace the
# face; `puppet` drives an invented figure from it; `touch_up` and `backdrop`
# leave it alone. They are disclosed differently below because they are
# different claims about what the viewer is seeing.
KINDS: dict[str, dict] = {
    "mask": {"covers_face": True,
             "means": "a mask or helmet drawn over your face"},
    "character": {"covers_face": True,
                  "means": "an invented character replacing your face"},
    "creature": {"covers_face": True,
                 "means": "an animal or creature, driven by your expressions"},
    "puppet": {"covers_face": True,
               "means": "an avatar you drive — it moves when you move"},
    "helmet_hud": {"covers_face": True,
                   "means": "a visor or helmet with a readout over it"},
    "touch_up": {"covers_face": False,
                 "means": "lighting and smoothing — still your face"},
    "backdrop": {"covers_face": False,
                 "means": "a replaced background — your face is untouched"},
}

# What no overlay may be, with the reason each is refused. Published by name
# rather than left out of the catalogue: an absence reads as a gap somebody
# files a bug about, and every one of these is a decision.
REFUSED: dict[str, str] = {
    "real_person": "a live-driven likeness of a real, identifiable person is "
                   "the artefact this platform exists to argue against, and "
                   "'it was only a filter' is how it would arrive",
    "public_figure": "the same thing with a better-known face, and a worse "
                     "outcome — words put in a real mouth, moving",
    "another_user": "somebody else's profile portrait is theirs, and wearing "
                    "it is impersonation with the platform's help",
    "age_shift": "an overlay that makes an adult look like a child, or a "
                 "child like an adult, defeats the only check standing "
                 "between the two",
    "badge_mimic": "drawing the AI mark, the verified mark or a live-desk "
                   "badge into the picture forges the one thing a viewer is "
                   "supposed to be able to rely on",
}

# Where an overlay may be worn. Every one of these already carries a disclosure
# a viewer reads, so one more line on it is a line in a place people look.
SURFACES: dict[str, str] = {
    "room": "a room — voice, video, AR, VR or 3-D",
    "party": "a watch party",
    "connection": "a one-to-one connection",
    "stream": "your own posted video or live session",
}

# The one surface that may never wear one, and why. Kept as data rather than an
# `if` so the refusal can be published with its reason.
FORBIDDEN_SURFACES: dict[str, str] = {
    "desk": "a live desk's badge reads 'Live person — not AI' and its whole "
            "premise is that a real human is behind it. A character over that "
            "face makes the badge a false statement, on the one surface whose "
            "value is that it is true",
}

MAX_PER_SURFACE = 1


class OverlayError(ValueError):
    """An overlay that must not be worn. Text meant for a person."""


def catalogue() -> dict:
    """What can be worn, where, and what is refused — with reasons."""
    return {
        "kinds": [{"kind": k, **v} for k, v in KINDS.items()],
        "surfaces": [{"surface": k, "means": v} for k, v in SURFACES.items()],
        "never": [{"surface": k, "why": v}
                  for k, v in FORBIDDEN_SURFACES.items()],
        "refused": [{"kind": k, "why": v} for k, v in REFUSED.items()],
        "rules": [
            "everyone who can see you is told you are wearing one",
            "it can never depict a real, identifiable person",
            "it can never be a live desk — that badge says a real person",
            "it cannot draw a mark or badge into the picture",
            "you take it off yourself, and it comes off when you leave",
        ],
    }


def _check(surface: str, kind: str) -> None:
    if surface in FORBIDDEN_SURFACES:
        raise OverlayError(FORBIDDEN_SURFACES[surface])
    if surface not in SURFACES:
        raise OverlayError(
            f"unknown surface {surface!r} — one of {', '.join(SURFACES)}")
    if kind in REFUSED:
        raise OverlayError(REFUSED[kind])
    if kind not in KINDS:
        raise OverlayError(
            f"unknown overlay {kind!r} — one of {', '.join(KINDS)}")


def wear(interactor_id: str, surface: str, surface_id: str, kind: str,
         title: str, asset: str | None = None,
         depicts_real_person: bool = False) -> dict:
    """Put an overlay on, here.

    ``depicts_real_person`` is asked rather than guessed. Nothing in this
    module can look at an asset and tell whether the face in it belongs to
    somebody — that is a judgement about the world, not about a file. So it is
    a declaration the wearer makes, refused when true, and recorded either way:
    a false declaration then has a name and a timestamp on it, which is the
    difference between a rule and a hope.
    """
    _check(surface, kind)
    if depicts_real_person:
        raise OverlayError(REFUSED["real_person"])
    title = (title or "").strip()
    if not title:
        raise OverlayError(
            "give it a name — it is what the other people are shown")

    conn = db.connect()
    conn.execute(
        "UPDATE overlays SET removed_at=? WHERE interactor_id=? AND surface=?"
        " AND surface_id=? AND removed_at IS NULL",
        (db.utcnow(), interactor_id, surface, surface_id))
    overlay_id = db.new_id("ovl")
    conn.execute(
        "INSERT INTO overlays (id, interactor_id, surface, surface_id, kind,"
        " title, asset, worn_at) VALUES (?,?,?,?,?,?,?,?)",
        (overlay_id, interactor_id, surface, surface_id, kind, title, asset,
         db.utcnow()))
    conn.commit()
    return {**worn_one(overlay_id), "wearing": True}


def take_off(interactor_id: str, surface: str, surface_id: str) -> dict:
    """Yours to remove, alone and at any moment."""
    conn = db.connect()
    row = conn.execute(
        "SELECT id FROM overlays WHERE interactor_id=? AND surface=?"
        " AND surface_id=? AND removed_at IS NULL",
        (interactor_id, surface, surface_id)).fetchone()
    if row is None:
        return {"wearing": False, "note": "you were not wearing one"}
    conn.execute("UPDATE overlays SET removed_at=? WHERE id=?",
                 (db.utcnow(), row["id"]))
    conn.commit()
    return {"wearing": False, "id": row["id"]}


def close_place(surface: str, surface_id: str) -> int:
    """Everyone's overlay comes off when the place ends, so a disguise cannot
    outlive the conversation it was worn in."""
    conn = db.connect()
    n = conn.execute(
        "SELECT COUNT(*) AS n FROM overlays WHERE surface=? AND surface_id=?"
        " AND removed_at IS NULL", (surface, surface_id)).fetchone()["n"]
    conn.execute(
        "UPDATE overlays SET removed_at=? WHERE surface=? AND surface_id=?"
        " AND removed_at IS NULL", (db.utcnow(), surface, surface_id))
    conn.commit()
    return n


def _disclosure(kind: str, title: str) -> str:
    """The line a viewer is shown, in words rather than a flag.

    A face-covering overlay and a background replacement are not the same
    claim, so they do not get the same sentence. Saying "filter applied" over
    a replaced face understates it; saying "this is not their face" over a
    blurred background is a lie in the other direction, and a disclosure that
    cries wolf is one people learn to skip.
    """
    if KINDS[kind]["covers_face"]:
        return (f"not their face — {title}, drawn over the camera in real "
                "time. A real person is underneath")
    return f"{title} — their own face, unaltered"


def worn_one(overlay_id: str) -> dict:
    row = db.connect().execute("SELECT * FROM overlays WHERE id=?",
                               (overlay_id,)).fetchone()
    if row is None:
        return {}
    return _read(row)


def _read(row) -> dict:
    return {
        "id": row["id"],
        "interactor_id": row["interactor_id"],
        "surface": row["surface"],
        "surface_id": row["surface_id"],
        "kind": row["kind"],
        "title": row["title"],
        "asset": row["asset"],
        "covers_face": KINDS[row["kind"]]["covers_face"],
        # The disclosure travels with the thing being rendered rather than
        # sitting in a settings screen the viewer never opens — the same reason
        # `avatars.render` attaches the AI mark to the portrait.
        "disclosure": _disclosure(row["kind"], row["title"]),
        "since": row["worn_at"],
    }


def worn(surface: str, surface_id: str) -> dict:
    """Who here is wearing what — what a surface renders.

    Readable by everyone present, and that is the point: an overlay is a claim
    about what a viewer is looking at, so the viewers are exactly who it is
    addressed to.
    """
    rows = db.connect().execute(
        "SELECT * FROM overlays WHERE surface=? AND surface_id=?"
        " AND removed_at IS NULL ORDER BY worn_at, rowid",
        (surface, surface_id)).fetchall()
    people = [_read(r) for r in rows]
    return {
        "surface": surface,
        "surface_id": surface_id,
        "overlays": people,
        "note": ("nobody here is wearing an overlay" if not people else
                 f"{len(people)} person(s) here are wearing one. A face drawn "
                 "over a camera is still a real person underneath, and every "
                 "one of them is named as wearing it"),
    }


def wearing(interactor_id: str, surface: str, surface_id: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM overlays WHERE interactor_id=? AND surface=?"
        " AND surface_id=? AND removed_at IS NULL",
        (interactor_id, surface, surface_id)).fetchone()
    return _read(row) if row else None
