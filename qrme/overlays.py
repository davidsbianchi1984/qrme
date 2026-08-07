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

**A live desk may wear one, and the badge stays true.** This was refused at
first, on the reasoning that a character over the face makes ``desks.DESIGNATION``
— *"Live person — not AI"* — a false statement. That conflated two different
claims. The badge does not say *this face is unmodified*; it says **a real
person is behind this**, which is exactly as true of somebody in a mask as of
somebody without one. A costume is not a synthesis. Refusing it protected
nothing and cost the one group who most need to work without showing their
face.

So the desk keeps its badge, and the badge does not mention the costume.
:func:`live_person_mark` returns :data:`LIVE_MARK` — *NOT AI · REAL PERSON* —
whatever is on the wearer's face. A viewer is on a **named account's** live or
room, with the handle at the top left; they chose it to get there and they know
whose stream it is. The open question on that page is never *is that his real
nose*, it is *is there a person here at all*.

That also removes a quiet penalty. Somebody who covers their face because of
dysmorphia, or because their work makes showing it unsafe, was being handed a
badge that announced the fact on every frame while the person beside them got a
clean one. Same claim, same mark, whatever you are wearing.

**The mark is bound to the account that owns the stream.** It is issued
against the desk, not asserted by the client, so it cannot be pasted onto a
stream that never earned it — the same reason the AI mark is burned into a
portrait rather than composited by whoever renders it.

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
    # -- worn over the face ---------------------------------------------------
    "mask": {"covers_face": True,
             "means": "a mask or helmet drawn over your face"},
    "half_mask": {"covers_face": True,
                  "means": "a domino or half mask — your eyes and mouth show"},
    "character": {"covers_face": True,
                  "means": "an invented character replacing your face"},
    "creature": {"covers_face": True,
                 "means": "an animal or creature, driven by your expressions"},
    "puppet": {"covers_face": True,
               "means": "an avatar you drive — it moves when you move"},
    "avatar_2d": {"covers_face": True,
                  "means": "a drawn 2-D face that follows yours"},
    "avatar_3d": {"covers_face": True,
                  "means": "a modelled 3-D head that follows yours"},
    "helmet_hud": {"covers_face": True,
                   "means": "a visor or helmet with a readout over it"},
    "paint": {"covers_face": True,
              "means": "face paint, markings or tattoos over your features"},
    "makeup": {"covers_face": True,
               "means": "stage makeup — your face, styled"},
    "hair": {"covers_face": True,
             "means": "hair, a wig or a beard drawn on"},
    "headwear": {"covers_face": True,
                 "means": "a hat, hood, veil or headdress"},
    "eyewear": {"covers_face": True,
                "means": "glasses, goggles or a visor over your eyes"},
    "prosthetic": {"covers_face": True,
                   "means": "sculpted features — a nose, a brow, a jaw"},
    "stylised": {"covers_face": True,
                 "means": "a rendered style over your own face — ink, cel, "
                          "clay, pixel"},
    "obscured": {"covers_face": True,
                 "means": "your face blurred, pixelated or blacked out"},
    "silhouette": {"covers_face": True,
                   "means": "you as an outline, lit from behind"},

    # -- your own face, left alone --------------------------------------------
    "touch_up": {"covers_face": False,
                 "means": "lighting and smoothing — still your face"},
    "backdrop": {"covers_face": False,
                 "means": "a replaced background — your face is untouched"},
}

# The face-covering ones, derived rather than listed twice.
FACE_KINDS = tuple(k for k, v in KINDS.items() if v["covers_face"])

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
    "desk": "a live desk's stream — the badge stays, see live_person_mark",
}

# Nowhere is forbidden any more. Kept as an empty mapping rather than deleted
# because the refusal machinery is the right shape and the next surface that
# genuinely cannot carry a disclosure should land here rather than in an `if`.
FORBIDDEN_SURFACES: dict[str, str] = {}

# Where the picture behind you came from. The kind says what happened to your
# face; this says what happened to the room, and they are separate claims that
# a single "filter applied" would run together.
#
# `generated` is the one that matters. An AI-generated background **is**
# synthetic media, and the fact that the person in front of it is real does not
# make the room real. Both get said, in that order, because the person is the
# thing a viewer is deciding about.
BACKDROP_SOURCES: dict[str, dict] = {
    "own": {"synthetic": False,
            "means": "a photo they took or already had"},
    "imported": {"synthetic": False,
                 "means": "an image they brought in from somewhere else"},
    "generated": {"synthetic": True,
                  "means": "an AI-generated scene"},
    "blur": {"synthetic": False,
             "means": "their real room, blurred"},
}

# The burned mark a live stream carries, and it does not change when somebody
# puts a face on.
#
# An earlier version composed the badge with the costume — *"Live person — not
# AI · wearing The Wolf"* — on the reasoning that a viewer needs to know the
# face is not the face. They do not, and saying it was answering a question
# nobody had: **a viewer is on a named account's live or room.** The handle is
# at the top left, they arrived by choosing it, and they know whose stream this
# is. The open question on that page is never *is that his real nose*, it is
# *is there a person here at all* — and that is the only thing this mark
# answers.
#
# Dropping the costume half also removes a quiet penalty. Somebody who covers
# their face because of dysmorphia, or because their work makes showing it
# unsafe, was being given a badge that announced the fact on every frame while
# the person beside them got a clean one. Same claim, same mark, whatever is on
# your face.
#
# Burned rather than composited, for the reason every mark in this codebase is:
# a badge drawn by the client survives neither a screenshot nor a re-host, and
# those are the journeys a stream frame actually takes.
LIVE_MARK = "NOT AI · REAL PERSON"

MAX_PER_SURFACE = 1


class OverlayError(ValueError):
    """An overlay that must not be worn. Text meant for a person."""


def catalogue() -> dict:
    """What can be worn, where, and what is refused — with reasons."""
    return {
        "kinds": [{"kind": k, **v} for k, v in KINDS.items()],
        "surfaces": [{"surface": k, "means": v} for k, v in SURFACES.items()],
        "backgrounds": [{"source": k, **v}
                        for k, v in BACKDROP_SOURCES.items()],
        "never": [{"surface": k, "why": v}
                  for k, v in FORBIDDEN_SURFACES.items()],
        "refusals": [{"kind": k, "why": v} for k, v in REFUSED.items()],
        "rules": [
            "everyone who can see you is told you are wearing one",
            "it can never depict a real, identifiable person",
            "a live desk keeps its 'real person' badge and shows both facts",
            "it cannot draw a mark or badge into the picture",
            "an AI-generated background says so, even though you are real",
            "an imported image needs the rights to use it",
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
         depicts_real_person: bool = False, source: str | None = None,
         holds_rights: bool = True) -> dict:
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

    # Where the picture behind them came from. Required for a backdrop and
    # meaningless on a mask, so it is validated rather than defaulted — a
    # background silently recorded as `own` when it was generated is exactly
    # the disclosure this feature exists to make.
    if kind == "backdrop":
        if source is None:
            raise OverlayError(
                "say where the background came from — one of "
                f"{', '.join(BACKDROP_SOURCES)}. A generated scene and a photo "
                "of your own kitchen are different claims")
        if source not in BACKDROP_SOURCES:
            raise OverlayError(
                f"unknown background source {source!r} — one of "
                f"{', '.join(BACKDROP_SOURCES)}")
        if source == "imported" and not holds_rights:
            # Asked, not guessed: nothing here can look at an image and know
            # who owns it. Declaring you do not is the one answer that has an
            # obvious consequence, so it is the one that is enforced.
            raise OverlayError(
                "an imported image needs the rights to use it. Bring one you "
                "hold, generate one, or use your own room")
    elif source is not None:
        raise OverlayError(
            f"{kind!r} does not have a background — `source` describes the "
            "picture behind you, and this one is on your face")
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
        " title, asset, source, worn_at) VALUES (?,?,?,?,?,?,?,?,?)",
        (overlay_id, interactor_id, surface, surface_id, kind, title, asset,
         source, db.utcnow()))
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


def _disclosure(kind: str, title: str, source: str | None = None) -> str:
    """The line a viewer is shown, in words rather than a flag.

    Three different claims, and they get three different sentences. Saying
    "filter applied" over a replaced face understates it; saying "this is not
    their face" over a blurred background is a lie in the other direction; and
    an **AI-generated background** is synthetic media that the other two
    sentences would say nothing about at all. A disclosure that cries wolf is
    one people learn to skip, and one that stays quiet where it matters is
    worse than none.

    The order is deliberate on the generated case: the person comes first,
    because the viewer is deciding about the person. The room comes second,
    because it is the part that was made.
    """
    if KINDS[kind]["covers_face"]:
        return (f"not their face — {title}, drawn over the camera in real "
                "time. A real person is underneath")
    if kind == "backdrop" and source and BACKDROP_SOURCES[source]["synthetic"]:
        return (f"their own face, unaltered — the background behind them is "
                f"AI-generated ({title})")
    if kind == "backdrop" and source == "blur":
        return "their own face, unaltered — their real room, blurred"
    if kind == "backdrop":
        return f"their own face, unaltered — the background is {title}"
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
        "source": row["source"],
        # Whether anything in this picture was generated. False for a mask,
        # which is a costume rather than a synthesis; True for an AI-made
        # background, whose subject is a real person in a room that is not.
        "background_generated": bool(
            row["source"] and BACKDROP_SOURCES.get(row["source"], {})
            .get("synthetic")),
        # The disclosure travels with the thing being rendered rather than
        # sitting in a settings screen the viewer never opens — the same reason
        # `avatars.render` attaches the AI mark to the portrait.
        "disclosure": _disclosure(row["kind"], row["title"],
                                  row["source"]),
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


def wearing_on_desk(desk_id: str) -> dict | None:
    """The overlay live on this desk, whoever put it there.

    A desk has one stream, so it has at most one face on it. Keyed on the desk
    rather than on a person because the viewer's question is about the picture
    in front of them, not about which account is driving it.
    """
    row = db.connect().execute(
        "SELECT * FROM overlays WHERE surface='desk' AND surface_id=?"
        " AND removed_at IS NULL ORDER BY worn_at DESC, rowid DESC LIMIT 1",
        (desk_id,)).fetchone()
    return _read(row) if row else None


def live_person_mark(desk_id: str) -> dict:
    """The badge a live desk carries while somebody on it wears an overlay:
    **a real person, and they are wearing something.**

    Both halves, always, because neither is any use alone. *"Live person — not
    AI"* over a mask invites the reading that the mask is their face. *"Wearing
    an overlay"* without it invites the reading that the whole picture is
    generated — the opposite error, and the one this platform exists to
    prevent. The pair is the disclosure; either half alone is a different and
    wrong claim.

    **Issued against the desk, never asserted by the client.** The mark is read
    from the desk row and its attestation, so a stream that never earned it
    cannot paste it on — the same reason the AI mark is burned into a portrait
    rather than composited by whoever happens to be rendering it. A desk with
    no attestation gets no mark rather than a weaker one.

    The *not AI* half is not softened by the overlay and must not be. A costume
    is not a synthesis: what is behind the camera is a person either way, which
    is the only thing that badge ever claimed.
    """
    from . import desks

    row = db.connect().execute(
        "SELECT owner_id, attestor, attestation_basis, attested_at"
        "  FROM desks WHERE id=?", (desk_id,)).fetchone()
    if row is None:
        return {}

    from . import identity

    # Whose stream this is, carried *with* the mark rather than left to a
    # second call. The mark can afford to say nothing about the costume only
    # because the viewer knows whose account they are on — so the two facts
    # ship together, and a client cannot render one without having been handed
    # the other.
    who = identity.whose("desk", desk_id)

    return {
        "desk_id": desk_id,
        # Bound to the account that owns the stream, which is what makes this
        # unforgeable by anybody else's client.
        "owner_id": row["owner_id"],
        "whose": who,
        # The whole mark, and it does not vary. See LIVE_MARK.
        "line": LIVE_MARK,
        "designation": desks.DESIGNATION,
        "real_person": True,
        "burned": True,
        "attestor": row["attestor"],
        "attestation_basis": row["attestation_basis"],
        "attested_at": row["attested_at"],
        "note": desks.ATTESTATION_NOTE,
        "means": "a real person is behind this stream",
    }
