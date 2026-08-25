"""The helper dock: the wrist's faces, cast into a box inside the app.

:mod:`qrme.wearables` puts a face on a watch. :mod:`qrme.displays` puts one on
a wall. Both answer *what am I currently presenting as* without making somebody
leave what they are doing — and both need hardware. **Most people have
neither.** The dock is the same answer for somebody holding only the phone: a
small pane in the bottom corner of the app itself, with no watch frame around
it, that tucks away behind the helper button when it is not wanted.

It is deliberately the *same* faces rather than a new set. :data:`FACES` is
built from `wearables.FACES` and a test binds the two, so a face added to the
wrist appears here or is explicitly refused here — the alternative is two
catalogues of glances that drift, and the one nobody re-reads wins.

**It shows, and it routes. It never acts.**

That is the exact inversion of the watch's one exception, and the inversion is
the point. Watch face 05 can *end* a lent microphone, because the watch is the
device doing the listening and a permission you cannot revoke from the thing
running it is not really yours. Nothing here is the device. The real screen is
one tap away in the same app, so a control in the dock would buy nothing — and
it would cost something, because this pane floats over live video, and a button
that ends a stream sitting a thumb's width from the thing that pauses it is a
mis-tap on somebody's broadcast. So: every face carries a **route** to the
screen that can act, and no face acts. One rule, no exceptions, which is what
makes it checkable.

**It is inside every screenshot.** `displays.NEVER` exists because a wall is
read by whoever walks past. This exists for a different reason that lands in
the same place: a pane pinned to the app frame is captured by every screenshot,
every screen recording and every screen share, including the ones the user is
broadcasting *right now*. Whatever is in the dock is in the stream. So
:data:`NEVER` is the vault list — message bodies, memory, agent names, who is
watching — and on a surface that is being broadcast the dock opens
:data:`TUCKED` by default, because the safe default for a pane you might be
transmitting is *closed*.

**The bottom corner is a constraint, not a preference.** The top-left is where
the profile's name sits on every live surface, and covering the one piece of
chrome that says whose room this is would undo `identity.whose`. The top-right
is the recording indicator. :data:`CORNERS` has two entries and both are at the
bottom.

**The helper button is the handle.** Not a second floating control — the app
already has one thing in that corner, and adding another would be two. Tapping
it opens the dock on the helper face, which is why the helper can answer *where
do I change my background* with somewhere to go: :func:`route` is the same
table `help.where_is` reads.
"""

from __future__ import annotations

import json

from . import db, i18n, wearables

# Where the pane may sit. Both at the bottom, for the reason in the module
# note: the top-left carries the name of whoever's surface this is, and the
# top-right carries the recording dot. A floating pane that can cover either is
# a floating pane that can hide who you are watching or whether you are live.
#
# Two rather than one because "bottom right" is a right-hander's default. A
# thumb rests over that corner on a phone held in the left hand, and the pane
# would spend its life being opened by accident.
CORNERS: dict[str, str] = {
    "bottom_right": "the default — under the right thumb",
    "bottom_left": "for a left-handed grip, or to uncover something",
}
DEFAULT_CORNER = "bottom_right"

# How much of it is showing.
#
# `hidden` is a real state and not the same as `handle`: somebody presenting,
# recording a demo, or handing their phone to another person wants the corner
# empty, and telling them to "just not tap it" is not an answer for a thing
# that is in every frame they capture.
STATES: dict[str, str] = {
    "hidden": "nothing in the corner at all",
    "handle": "the helper button only — tucked away",
    "open": "the pane, showing one face",
}

# How it starts on each platform, before anybody has moved it.
#
# Not the same everywhere, and the difference is argued rather than assumed. On
# a phone the pane covers content on a screen that has none to spare, so it
# starts tucked. On a desktop it starts open on the agent lights, because that
# is what the pinned lights panel already did and its reason still holds: a
# desktop user has no wrist to glance at, and amber and red are precisely the
# states nobody thinks to go looking for.
#
# A watch is not here because a watch *is* a face — `wearables.FACES` — rather
# than a place to put one.
DEFAULT_STATE_ON: dict[str, str] = {
    "phone": "handle",
    "desktop": "open",
}
DEFAULT_PLATFORM = "phone"
DEFAULT_STATE = DEFAULT_STATE_ON[DEFAULT_PLATFORM]

# What the pane opens on when it opens by itself. Desktop starts on the lights
# for the reason above; the phone starts on the helper, because a pane somebody
# opened deliberately is a pane they opened to ask something.
DEFAULT_FACE_ON: dict[str, str] = {
    "phone": "helper",
    "desktop": "agents",
}

# The one size. Not an oversight and not a limitation to be lifted later: a
# resizable pane floating over video is one people enlarge until it covers the
# video, and then blame the video. A glance that needs more room than this is a
# screen, and every face here has one to route to.
BOX = {"width": 168, "height": 132, "handle": 44, "inset": 16}

# The faces the dock refuses to cast, with the reason returned to the caller.
#
# `control` is the whole of it. On the wrist it is assist/halt/approve, and it
# is safe there because the wrist is the owner's and holds nothing else. In a
# pane hovering over a live stream it is three destructive buttons on top of
# the thing they would destroy — and unlike the watch, the Control Center is
# one tap away, so the dock loses nothing by sending you there.
REFUSED: dict[str, str] = {
    "control": "assist, halt and approve are actions, and the dock does not "
               "act — it is a pane floating over the thing those buttons "
               "would stop. The Control Center is one tap away.",
}

# The helper itself, which is the face the handle opens on. Not a wrist face:
# a watch that could hold a conversation would be a watch you talk to, and the
# reason this surface exists at all is to point at screens.
HELPER_FACE = "helper"

# What may never appear in the pane, and why, in the words the refusal uses.
#
# The reason is not the wall's reason. A wall panel is read by passers-by; this
# is read by anyone the user is screen-sharing, streaming or sending a
# screenshot to — an audience the user chose, but chose for the *surface*, not
# for the pane pinned on top of it. A dock that showed an unread message would
# put it in the broadcast the moment it arrived.
NEVER: dict[str, str] = {
    "message_bodies": "a message that arrives mid-stream would be read out to "
                      "the stream",
    "memory": "what a profile remembers of somebody is the Memory Vault's, "
              "and the vault is not a glance",
    "agent_names": "the same rule watch face 01 already follows — lights and "
                   "counts, never which agent",
    "viewer_names": "who is watching is the viewers' business, not the "
                    "broadcast's",
    "owner_tokens": "nothing that authorises anything belongs on a surface "
                    "that is being captured",
    "handles_of_anonymous": "an anonymous profile's handle is withheld "
                            "everywhere else; a pane is not an exception",
}

# Surfaces where the dock opens tucked however the owner has it set. Being on
# one of these means the screen is going somewhere, and the safe default for a
# pane you might be transmitting is closed.
#
# Capped rather than overridden, in the same shape as `roommic`'s gain: the
# preference is the owner's and applies everywhere else. They can still open
# it — this is a default, not a lock, because a user who decides their own
# stream may show their own dock is not wrong.
TUCKED: tuple[str, ...] = ("stream", "live", "party", "desk")

# Which faces need to know *which* surface, because the answer is about a
# place rather than about the account. You are on a live, in a game, in a
# room — and the dock is floating over that one, so it can be told.
PER_SURFACE: tuple[str, ...] = ("camera", "lobby", "microphone")

# Where the full screen for each face lives. The dock's whole job on the
# routing side, and the table `help.where_is` reads — so "where do I change my
# background" and "what does this pane open" cannot answer differently.
ROUTES: dict[str, dict] = {
    HELPER_FACE: {"screen": 127, "path": "/help", "title": "Show Me Around"},
    "agents": {"screen": 83, "path": "/agents", "title": "Agents"},
    "activity": {"screen": 86, "path": "/activity", "title": "Activity"},
    "profile": {"screen": 10, "path": "/profile", "title": "Profile Health"},
    "microphone": {"screen": 81, "path": "/microphone",
                   "title": "Lend a Microphone"},
    "identity": {"screen": 119, "path": "/identity", "title": "Your Profiles"},
    "camera": {"screen": 121, "path": "/camera", "title": "Wear a Character"},
    "lobby": {"screen": 122, "path": "/lobby", "title": "Game Lobby"},
    "screens": {"screen": 126, "path": "/screens", "title": "On a Screen"},
    "proceeds": {"screen": 145, "path": "/campaigns",
                 "title": "Where the Money Goes"},
    "coordination": {"screen": 146, "path": "/org", "title": "The Ecosystem"},
}

# The catalogue, built from the wrist rather than restated beside it. Two
# hand-written lists of the same glances would drift, and `identity.shown_name`
# is the standing lesson here: the decision lives in one place or it lives in
# fifteen.
FACES: dict[str, str] = {
    HELPER_FACE: "the guide — ask it anything, or let it show you around",
    **{face: what for face, what in wearables.FACES.items()
       if face not in REFUSED},
}
DEFAULT_FACE = HELPER_FACE


class DockError(ValueError):
    """A dock that cannot be drawn. Text meant for a person."""


def vocabulary() -> dict:
    """Everything a client needs to draw the pane, published.

    Including the refusals **by name with the reason**, because a client that
    knew only the allowed list would render `control` as a missing feature
    rather than a decision.
    """
    return {
        "faces": FACES,
        "refusal_reasons": REFUSED,
        "corners": CORNERS,
        "states": STATES,
        "default_state_on": DEFAULT_STATE_ON,
        "default_face_on": DEFAULT_FACE_ON,
        "box": BOX,
        "never": NEVER,
        "tucked_on": list(TUCKED),
        "per_surface": list(PER_SURFACE),
        "routes": ROUTES,
        "acts": False,
    }


def route(face: str) -> dict:
    """Where the screen that can actually do this lives.

    The dock's other half. Every face carries one, which is what lets the pane
    be read-only without being a dead end — and what lets the helper answer
    *where do I change my background* with a place rather than a description.
    """
    if face in REFUSED:
        raise DockError(REFUSED[face])
    if face not in ROUTES:
        raise DockError(i18n.fill(i18n.NO_SUCH_FACE, got=repr(face), choices=', '.join(FACES)))
    return {"face": face, **ROUTES[face], "opens_dock_face": face}


def _check_face(face: str) -> None:
    if face in REFUSED:
        raise DockError(REFUSED[face])
    if face not in FACES:
        raise DockError(i18n.fill(i18n.NO_SUCH_FACE, got=repr(face), choices=', '.join(FACES)))


def settings(profile_id: str, platform: str = DEFAULT_PLATFORM) -> dict:
    """This account's dock, with the platform's defaults applied.

    Returns a full answer for somebody who has never touched it, rather than
    an empty row — the pane has to draw on first launch, and a client that had
    to know the defaults would be a second place they are written down.

    Once somebody has moved it, their choice travels: the stored row wins on
    every platform. The defaults differ because the first-run guess differs,
    not because the pane is two features.
    """
    if platform not in DEFAULT_STATE_ON:
        raise DockError(
            i18n.fill(i18n.UNKNOWN_CHOICE, field="platform", got=repr(platform), choices=', '.join(DEFAULT_STATE_ON)))
    row = db.connect().execute(
        "SELECT * FROM dock_prefs WHERE profile_id=?", (profile_id,)).fetchone()
    if row is None:
        return {"profile_id": profile_id, "corner": DEFAULT_CORNER,
                "state": DEFAULT_STATE_ON[platform],
                "face": DEFAULT_FACE_ON[platform],
                "faces": list(FACES), "platform": platform, "set": False}
    return {"profile_id": profile_id, "corner": row["corner"],
            "state": row["state"], "face": row["face"],
            "faces": json.loads(row["faces"]), "platform": platform,
            "set": True}


def configure(profile_id: str, corner: str | None = None,
              state: str | None = None, face: str | None = None,
              faces: list[str] | None = None,
              platform: str = DEFAULT_PLATFORM) -> dict:
    """Move it, tuck it, or change which faces it will cycle through."""
    now = settings(profile_id, platform)
    corner = now["corner"] if corner is None else corner
    state = now["state"] if state is None else state
    face = now["face"] if face is None else face
    chosen = list(now["faces"] if faces is None else faces)

    if corner not in CORNERS:
        raise DockError(
            i18n.fill(i18n.PANE_BOTTOM_CORNER_LIGHT, choices=', '.join(CORNERS)))
    if state not in STATES:
        raise DockError(i18n.fill(i18n.UNKNOWN_CHOICE, field="state", got=repr(state), choices=', '.join(STATES)))
    for f in chosen:
        _check_face(f)
    if not chosen:
        raise DockError("a pane with no faces is the helper button on its own "
                        "— set the state to 'handle' instead")
    _check_face(face)
    if face not in chosen:
        raise DockError(i18n.fill(i18n.FACE_NOT_CARRIED, got=repr(face)))

    conn = db.connect()
    conn.execute(
        "INSERT INTO dock_prefs (profile_id, corner, state, face, faces,"
        " updated_at) VALUES (?,?,?,?,?,?)"
        " ON CONFLICT (profile_id) DO UPDATE SET corner=excluded.corner,"
        " state=excluded.state, face=excluded.face, faces=excluded.faces,"
        " updated_at=excluded.updated_at",
        (profile_id, corner, state, face, json.dumps(chosen), db.utcnow()))
    conn.commit()
    return settings(profile_id, platform)


def opens_as(profile_id: str, surface: str | None = None,
             platform: str = DEFAULT_PLATFORM) -> dict:
    """The state the pane should draw in, here, right now.

    Where :data:`TUCKED` is applied. The owner's preference is returned
    alongside what it actually opens as, in the same shape `roommic` reports a
    capped gain: a preference that was overridden is still the owner's, and
    silently rewriting it would mean the setting screen and the pane disagreed
    about what the setting was.
    """
    now = settings(profile_id, platform)
    wanted = now["state"]
    tucked = surface in TUCKED and wanted == "open"
    return {
        **now,
        "surface": surface,
        "wanted": wanted,
        "state": "handle" if tucked else wanted,
        "tucked": tucked,
        "why": ("this surface is being broadcast, and the pane is inside the "
                "capture — open it yourself if you want it in shot"
                if tucked else None),
    }


def face(profile_id: str, name: str, surface: str | None = None,
         surface_id: str | None = None) -> dict:
    """One face, as the pane would draw it.

    Read-only by construction: this function returns what to show and where to
    go, and there is no counterpart that changes anything. A test asserts the
    module writes to nothing but its own preferences row.
    """
    _check_face(name)
    if name in PER_SURFACE and not surface_id:
        raise DockError(
            i18n.fill(i18n.FACE_ABOUT_A_PLACE, face=name))
    return {
        "face": name,
        "shows": FACES[name],
        "profile_id": profile_id,
        "surface": surface,
        "surface_id": surface_id,
        "route": route(name),
        "acts": False,
        "box": BOX,
        "never": list(NEVER),
    }
