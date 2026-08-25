"""A profile on a screen that stays where it is.

A wall panel in a lobby, a kiosk by a door, a counter screen, a pane of glass
with something behind it. The same idea as the watch faces in
:mod:`qrme.wearables` — a closed set of things a screen may show — and the same
reason for the set being closed: *what may be displayed* is a permission, and a
permission with open-ended values is one nobody can audit.

**But a stationary screen is not a small watch, and the difference is the whole
module.** A watch is on one person's wrist. They chose it, they are the only
one who reads it, and they can turn it over. A wall panel is read by **whoever
walks past** — a courier, a child, somebody visiting the person whose profile
it shows. Nobody in that corridor opted into anything.

That is the same argument that makes `qrme/roommic.py` refuse a room-facing
microphone, arriving from the other direction: there, a device that *hears*
people who did not agree; here, a device that *shows* things to people who did
not ask. So the rule is stricter than the watch's, not looser:

**Only what a stranger may read.** :data:`FACES` is a shorter list than
`wearables.FACES`, and every entry on it is something already public — a
profile's front page, a desk's presence, a beacon. Anything personal appears as
a **count** or not at all, which is the rule watch face 01 already follows for
agent names, applied harder because the audience is wider.

**The disclosure survives the glass.** A transparent panel has whatever is
behind it for a background — a corridor, a window, a moving person — so
contrast is not something the renderer controls. The AI mark is the one thing
on that screen that must stay legible, and on a transparent finish it gets a
backing plate. A mark that disappears against a bright wall is worse than no
mark, because the rest of the card still reads as a person.

**Placing one is a decision about a place**, like a beacon, so it is the
owner's alone. `docs/beacons.md` says not to leave a profile somewhere its
subject is not equipped for; a screen bolted to a wall is that with a plug in
it.
"""

from __future__ import annotations

from . import db, i18n

# What kind of fixed screen this is. Grouped by who is standing in front of it,
# because that is what decides what may be on it — not the hardware.
KINDS: dict[str, dict] = {
    "wall_panel": {"passers_by": True,
                   "means": "mounted in a corridor, lobby or shopfront"},
    "kiosk": {"passers_by": True,
              "means": "a standing screen somebody walks up to"},
    "counter_screen": {"passers_by": True,
                       "means": "facing across a desk or counter"},
    "window_pane": {"passers_by": True,
                    "means": "a shop window, read from the street"},
    "desk_display": {"passers_by": False,
                     "means": "on your own desk, facing you"},
    "table_top": {"passers_by": False,
                  "means": "a small screen in your own room"},
    # The three the owner asked after by name: a screen you cast to, one
    # paired over Bluetooth, one plugged straight in. All private-side —
    # the grouping is who stands in front, and these live in your own
    # space; a cast sink in a lobby is a wall_panel wearing a dongle.
    "cast_sink": {"passers_by": False,
                  "means": "a TV or monitor you cast to over the network "
                           "(AirPlay, Cast)"},
    "bluetooth_device": {"passers_by": False,
                         "means": "a nearby device paired over Bluetooth"},
    "attached_device": {"passers_by": False,
                        "means": "a screen plugged straight into this "
                                 "machine (USB, HDMI)"},
}

# Small or full, and it is not only a size. A `badge` is a strip — a name, a
# light, a state — and can sit under something else on the same glass. A `full`
# screen is the whole surface and is the only size a beacon's QR is legible at.
SIZES: dict[str, str] = {
    "badge": "a strip: the name, the state, and nothing that needs reading",
    "half": "a panel beside whatever else is on the glass",
    "full": "the whole surface",
}

# Opaque, or see-through with the room behind it.
FINISHES: dict[str, str] = {
    "opaque": "a screen with a background of its own",
    "transparent": "glass, with whatever is behind it showing through",
}

# What a fixed screen may show. Shorter than `wearables.FACES` on purpose: a
# watch is read by its wearer, a wall panel by whoever walks past, and every
# entry here is something that is already public.
#
# There is no `control` face. The watch has one — assist, halt, approve — and it
# is safe there because the wrist it is strapped to belongs to the owner. A
# button on a wall is pressed by whoever reaches it.
FACES: dict[str, dict] = {
    "front_page": {"private": False,
                   "shows": "the profile's public front page — portrait, "
                            "headline, the AI mark"},
    "presence": {"private": False,
                 "shows": "a live desk's attended/away state, and the bell"},
    "beacon": {"private": False,
               "shows": "the profile's QR, which a phone can scan"},
    "agents": {"private": False,
               "shows": "the status lights as counts — never agent names"},
    "hours": {"private": False,
              "shows": "when somebody is usually here"},
    "greeting": {"private": False,
                 "shows": "a line the owner wrote, moderated like any other"},
}
DEFAULT_FACES = ("front_page",)

# Named, so the refusal is a decision somebody can read rather than a gap they
# work around. Each of these is on the watch, or on the phone, and none of them
# belongs on a wall.
NEVER: dict[str, str] = {
    "messages": "a conversation on a wall is a conversation with an audience "
                "the other person did not agree to",
    "memory": "somebody's vaulted material, on a screen in a corridor",
    "friends": "who somebody stands with is theirs to show, not a fixture's",
    "agent_names": "the watch shows counts and not names for one person's own "
                   "wrist. A corridor is not that",
    "control": "assist, halt and approve are safe on a wrist because the wrist "
               "is the owner's. A button on a wall is pressed by whoever "
               "reaches it",
    "notifications": "an alert is addressed to a person, and a wall cannot "
                     "tell whether they are the one reading it",
}

MAX_PER_OWNER = 24


class DisplayError(ValueError):
    """A screen that must not show that. Text meant for a person."""


def vocabulary() -> dict:
    """What a fixed screen can be, and what it may never show."""
    return {
        "kinds": [{"kind": k, **v} for k, v in KINDS.items()],
        "sizes": [{"size": k, "means": v} for k, v in SIZES.items()],
        "finishes": [{"finish": k, "means": v} for k, v in FINISHES.items()],
        "faces": [{"face": k, **v} for k, v in FACES.items()],
        "default_faces": list(DEFAULT_FACES),
        "never": [{"thing": k, "why": v} for k, v in NEVER.items()],
        "rules": [
            "only what a stranger may read — a wall has no idea who is "
            "in front of it",
            "anything personal is a count, or it is not there",
            "the AI mark gets a backing plate on glass, so it survives "
            "whatever is behind it",
            "there is no control face: a button on a wall is pressed by "
            "whoever reaches it",
            "placing one is the owner's decision, like a beacon",
        ],
    }


def _check(kind: str, size: str, finish: str, faces: list[str]) -> None:
    if kind not in KINDS:
        raise DisplayError(
            i18n.fill(i18n.UNKNOWN_CHOICE_DASH, field="screen", got=repr(kind), choices=', '.join(KINDS)))
    if size not in SIZES:
        raise DisplayError(i18n.fill(i18n.UNKNOWN_CHOICE_DASH, field="size", got=repr(size), choices=', '.join(SIZES)))
    if finish not in FINISHES:
        raise DisplayError(
            i18n.fill(i18n.UNKNOWN_CHOICE_DASH, field="finish", got=repr(finish), choices=', '.join(FINISHES)))
    for face in faces:
        if face in NEVER:
            raise DisplayError(NEVER[face])
        if face not in FACES:
            raise DisplayError(
                i18n.fill(i18n.UNKNOWN_CHOICE_DASH, field="face", got=repr(face), choices=', '.join(FACES)))
    if "beacon" in faces and size == "badge":
        # Not a rule about neatness. A QR at strip height is a QR nobody's
        # camera resolves, and a code that cannot be scanned is a code that
        # looks broken rather than one that is absent.
        raise DisplayError(
            "a beacon needs the whole surface — a QR on a strip is too small "
            "for a phone to read, and an unscannable code looks broken rather "
            "than missing")


def place(profile_id: str, kind: str, label: str, size: str = "full",
          finish: str = "opaque", faces: list[str] | None = None,
          location: str | None = None) -> dict:
    """Put this profile on a screen somewhere.

    ``label`` is what the owner calls it — *"the lobby panel"* — so a list of
    twelve screens is a list they can act on rather than a column of ids.
    """
    # `None` means "use the defaults"; `[]` means "show nothing" and is a
    # different request. `faces or DEFAULT_FACES` collapsed the two, so an
    # explicit empty list was silently answered with a front page — the check
    # below could never fire and a caller asking for a blank screen got the
    # opposite of what they asked for.
    faces = list(DEFAULT_FACES if faces is None else faces)
    if not faces:
        raise DisplayError("a screen showing nothing is a screen turned off")
    _check(kind, size, finish, faces)

    conn = db.connect()
    live = conn.execute(
        "SELECT COUNT(*) AS n FROM displays WHERE profile_id=?"
        " AND removed_at IS NULL", (profile_id,)).fetchone()["n"]
    if live >= MAX_PER_OWNER:
        raise DisplayError(i18n.fill(i18n.SCREENS_LIMIT, max=MAX_PER_OWNER))

    import json
    display_id = db.new_id("dsp")
    conn.execute(
        "INSERT INTO displays (id, profile_id, kind, label, location, size,"
        " finish, faces, placed_at) VALUES (?,?,?,?,?,?,?,?,?)",
        (display_id, profile_id, kind, label, location, size, finish,
         json.dumps(faces), db.utcnow()))
    conn.commit()
    return read(display_id)


def read(display_id: str) -> dict:
    import json

    row = db.connect().execute("SELECT * FROM displays WHERE id=?",
                               (display_id,)).fetchone()
    if row is None:
        raise DisplayError("no such screen")
    faces = json.loads(row["faces"])
    return {
        "id": row["id"],
        "profile_id": row["profile_id"],
        "kind": row["kind"],
        "label": row["label"],
        "location": row["location"],
        "size": row["size"],
        "finish": row["finish"],
        "faces": faces,
        "passers_by": KINDS[row["kind"]]["passers_by"],
        "live": row["removed_at"] is None,
        "mark": mark(row["finish"]),
        "placed_at": row["placed_at"],
    }


def mark(finish: str) -> dict:
    """How the AI disclosure is drawn at this finish.

    On glass the background is a corridor — a moving one — so contrast is not
    something the renderer controls. The mark gets a plate behind it, and that
    is not a style preference: a mark that vanishes against a bright wall is
    worse than no mark at all, because the rest of the card still reads as a
    person and the one thing correcting that impression is the thing that
    disappeared.
    """
    plated = finish == "transparent"
    return {
        "backing_plate": plated,
        "why": ("the background is whatever is behind the glass, and it moves"
                if plated else "the screen supplies its own background"),
        "min_contrast": 4.5,
        "note": "the mark is the last thing on this screen allowed to become "
                "hard to read",
    }


def faces_for(display_id: str) -> list[dict]:
    """What this screen is showing, each with whether it is public."""
    return [{"face": f, **FACES[f]} for f in read(display_id)["faces"]]


def set_faces(display_id: str, faces: list[str]) -> dict:
    import json

    current = read(display_id)
    if not faces:
        raise DisplayError("a screen showing nothing is a screen turned off")
    _check(current["kind"], current["size"], current["finish"], faces)
    conn = db.connect()
    conn.execute("UPDATE displays SET faces=? WHERE id=?",
                 (json.dumps(list(faces)), display_id))
    conn.commit()
    return read(display_id)


def take_down(display_id: str) -> dict:
    """Take the screen down. The row survives, like an unpaired wearable, so a
    profile that was on a wall for a year can still say where."""
    read(display_id)
    conn = db.connect()
    conn.execute("UPDATE displays SET removed_at=? WHERE id=? "
                 "AND removed_at IS NULL", (db.utcnow(), display_id))
    conn.commit()
    return read(display_id)


def for_profile(profile_id: str, include_removed: bool = False) -> list[dict]:
    rows = db.connect().execute(
        "SELECT id FROM displays WHERE profile_id=?"
        + ("" if include_removed else " AND removed_at IS NULL")
        + " ORDER BY placed_at, rowid", (profile_id,)).fetchall()
    return [read(r["id"]) for r in rows]
