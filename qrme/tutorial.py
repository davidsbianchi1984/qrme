"""The help assistant, walking you through the whole app.

:mod:`qrme.help` answers a question somebody thought to ask. This is the other
half of the same surface: a **guided walkthrough** for somebody who does not
yet know what there is to ask about. Same assistant, same posture, and the
posture is the point — it is furniture, not a thirty-fifth character:

* **No name and no face**, for the reason `help.py` gives at length. A tutorial
  guide with a persona would be the most convincing synthetic profile on the
  platform, met by every user on their first minute, at the exact moment they
  have the least idea what is synthetic here.
* **It never speaks as anybody**, and it hands persona questions back the same
  way `help.ask` does.
* **It writes nothing.** A tutorial that placed a beacon or sent a message "to
  show you how" would be a tutorial that acted on somebody's account before
  they understood what the account was. Every lesson says *what to tap*; none
  of them taps it.

**The lessons are written prose and work with no model configured**, like
`help.TOPICS`. A walkthrough that needs an API key is a walkthrough that is
missing on a self-hosted deployment, which is a supported setup here rather
than a degraded one.

**Voice and text are the same lesson, rendered differently, not two scripts.**
:func:`say` is the only place that difference lives. Spoken, a screen number is
noise — *"screen eighty-one"* helps nobody who is listening — so voice drops
the numbers and the route names and keeps the sentence. Two hand-written
versions would drift, and the spoken one would be the one nobody re-read.

**The walkthrough cannot quietly fall behind the app.** :data:`LESSONS` names
the screens each step is about, and a test asserts every screen in the gallery
is claimed by some lesson. Add a feature, draw its screen, and the tutorial
fails until somebody has said what it is for — which is the only way a guided
tour of a moving product stays true.
"""

from __future__ import annotations

from . import db

# The disclosure the walkthrough carries, matching `help.DISCLOSURE` in spirit:
# this is the product talking about itself, not a character.
GUIDE = ("This is QRME's own guide — not a profile, and not a person. It has "
         "no name and no face on purpose, because everything here that looks "
         "like somebody is marked as AI, and a guide with a face would be the "
         "first thing you met that was not.")

# The walkthrough, in order. Each lesson is:
#   chapter   — which part of the app
#   title     — what this function is called
#   what      — what it does, in a sentence somebody can act on
#   screens   — the screen numbers it is about (the binding to the gallery)
#   try_it    — one concrete thing to do next
#
# Ordered so that nothing refers to a thing that has not been introduced: you
# are a profile before you have a room, and in a room before you lend it a
# microphone.
LESSONS: tuple[dict, ...] = (
    dict(key="welcome", chapter="Getting started", title="What QRME is",
         what="QRME makes AI synthetic profiles — characters with a persona, a "
              "memory, and a relationship with each person who talks to them. "
              "Every one is marked as AI, and the mark is burned into the "
              "portrait's pixels so it survives a screenshot.",
         screens=(1, 2, 19), try_it="Look at the mark on any portrait here."),
    dict(key="make_one", chapter="Getting started", title="Making a profile",
         what="You describe who it is and it answers in character from the "
              "first message. Genesis builds one from four questions if you "
              "would rather be asked than write.",
         screens=(3, 4, 5, 16),
         try_it="Create one, or open Genesis and answer the four."),
    dict(key="talk", chapter="Getting started", title="Talking to it",
         what="Every reply is explained: what it drew on, and why. A profile "
              "remembers you specifically, and treats you according to the "
              "relationship you have with it.",
         screens=(6, 7, 8, 9), try_it="Send one message and open the why."),
    dict(key="health", chapter="Getting started", title="How it is doing",
         what="Profile health, stats, and the transparency page — what it "
              "knows, where that came from, and what it is allowed to do.",
         screens=(10, 18, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30),
         try_it="Open Profile Health and read the sources list."),
    dict(key="control", chapter="You are in control", title="The controls",
         what="Moderation, steering, boundaries, and the switches that turn "
              "any of it off. Nothing here runs without an owner enabling it.",
         screens=(14, 15, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40),
         try_it="Open the Control Center and turn one dial."),
    dict(key="market", chapter="Out in the world", title="The marketplace",
         what="Share or license a profile, sell a knowledge pack, take a "
              "placement. Money here is simulated and every response says so.",
         screens=(11, 12, 13, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50),
         try_it="Browse the marketplace and open one listing."),
    dict(key="reach", chapter="Out in the world", title="Being found",
         what="A handle, a tag, or a printed QR beacon left somewhere the "
              "profile is useful. A scan lands a stranger on its front page.",
         screens=(17, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60),
         try_it="Claim a handle, then look at the beacon page it makes."),
    dict(key="desks", chapter="Out in the world", title="Live desks",
         what="A real person behind a stream, badged *Live person — not AI* — "
              "the mark inverted, because there is somebody there.",
         screens=(61, 62, 63, 64, 65, 66, 67, 68, 69, 70),
         try_it="Open a live desk and ring the bell."),
    dict(key="social", chapter="People", title="Friends, pages and the feed",
         what="A friends list, a page you build yourself in real HTML, and a "
              "feed that tells you why each thing is in front of you.",
         screens=(71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 82, 83, 84, 85, 86,
                  87, 88, 89),
         try_it="Open your page and change the theme."),
    dict(key="mic", chapter="People", title="Lending a microphone",
         what="In a voice room your microphone is busy carrying your voice. "
              "This lends the profiles the one on your watch, so they hear you "
              "as well as read you. Everyone in the room is shown that you "
              "did, it stays narrow enough to reach only you, and it ends when "
              "the room does.",
         screens=(81, 120),
         try_it="Lend it, then look at what the room sees."),
    dict(key="fullscreen", chapter="Watching", title="Full screen and sideways",
         what="Any live surface fills the phone. A long press dims everything "
              "but the controls and brings the help button back; turning the "
              "phone gives you it sideways.",
         screens=tuple(range(90, 113)),
         try_it="Press and hold on a live video."),
    dict(key="together", chapter="Watching", title="Watching together",
         what="A watch party shares a position rather than a player, and a "
              "synthetic profile in the room is told it has not seen the "
              "video — so it says so instead of inventing an opinion.",
         screens=(113, 114, 115),
         try_it="Start a party from a posted video."),
    dict(key="work", chapter="Working", title="Agreeing before work moves",
         what="An exchange lists what crosses in each direction, what is "
              "included and what is not. Both sign, and any change to the "
              "document voids both signatures.",
         screens=(116, 117), try_it="Draft one and read the manifest."),
    dict(key="games", chapter="Working", title="Playing alongside",
         what="A profile can sit beside you in a game as a companion or a "
              "coach. Nothing in the lobby ever plays: no input, no second "
              "controller, no console of its own.",
         screens=(122, 125), try_it="Open a lobby and read what it cannot do."),
    dict(key="face", chapter="Being yourself", title="Your face, or not",
         what="Wear a character over your camera, change what is behind you, "
              "or stay anonymous under a fixed name nobody can change. A "
              "generated background says so; a real person is still marked as "
              "real underneath a mask.",
         screens=(118, 119, 121, 123, 124),
         try_it="Try an overlay, then look at what viewers are told."),
    dict(key="screens", chapter="Being yourself", title="On other screens",
         what="A watch on your wrist, a wall panel, a kiosk, a pane of glass. "
              "A fixed screen shows less than a watch does, because a wall is "
              "read by whoever walks past.",
         screens=(126,), try_it="Place one and choose what it shows."),
    dict(key="plans", chapter="Being yourself", title="What it costs",
         what="Basic is $20 a month and is the entry to making things: your "
              "own profiles and your own agent. Pro is $130 a month and adds "
              "everything that leaves your account — the marketplace, "
              "connectors, skills, downloads, connections, and every builder. "
              "Reading is free and always was: a scanned beacon needs no "
              "account at all. Billing here is simulated and no real funds "
              "move.",
         screens=(130, 131),
         try_it="Open Choose a Plan and read what Basic already includes."),
    dict(key="guide", chapter="Being yourself", title="This guide",
         what="The walkthrough you are in. It has no name and no face, it "
              "works with no model configured, and it never taps anything for "
              "you — it says what to tap. The helper button in the corner is "
              "also the handle for a small pane that shows the watch faces "
              "without a watch, and if you already know what you want, ask "
              "where it is and the guide names the screen instead of "
              "describing the feature.",
         screens=(127, 128, 129),
         try_it="Ask it where to change your background."),
)

CHAPTERS = tuple(dict.fromkeys(lesson["chapter"] for lesson in LESSONS))
MODES = ("text", "voice")


class TutorialError(ValueError):
    """A step that does not exist. Text meant for a person."""


def _index(key: str) -> int:
    for i, lesson in enumerate(LESSONS):
        if lesson["key"] == key:
            return i
    raise TutorialError(f"no such step {key!r}")


def say(lesson: dict, mode: str = "text") -> dict:
    """One lesson, rendered for reading or for listening.

    The only place the two differ. Spoken, a screen number is noise — nobody
    listening is helped by *"screen eighty-one"* — so voice drops the numbers
    and keeps the sentence. Two hand-written versions would drift, and the
    spoken one would be the one nobody re-read.
    """
    if mode not in MODES:
        raise TutorialError(f"unknown mode {mode!r} — one of {', '.join(MODES)}")
    out = {
        "key": lesson["key"],
        "chapter": lesson["chapter"],
        "title": lesson["title"],
        "try_it": lesson["try_it"],
        "mode": mode,
    }
    if mode == "voice":
        out["speak"] = f"{lesson['title']}. {lesson['what']} {lesson['try_it']}"
        out["screens"] = []
    else:
        out["what"] = lesson["what"]
        out["screens"] = list(lesson["screens"])
    return out


def outline(mode: str = "text") -> dict:
    """The whole walkthrough at once, for somebody who would rather skim.

    Offered because a guided tour you cannot see the shape of is one people
    leave — and the person most likely to leave is the one who already knows
    half of it.
    """
    return {
        "guide": GUIDE,
        "chapters": [
            {"chapter": c,
             "steps": [say(le, mode) for le in LESSONS if le["chapter"] == c]}
            for c in CHAPTERS],
        "steps": len(LESSONS),
    }


def start(learner_id: str, mode: str = "text") -> dict:
    """Begin, or begin again from the top."""
    conn = db.connect()
    conn.execute("DELETE FROM tutorial_progress WHERE learner_id=?",
                 (learner_id,))
    conn.commit()
    return where(learner_id, mode)


def where(learner_id: str, mode: str = "text") -> dict:
    """The step this learner is on, with what is behind and ahead."""
    done = _done(learner_id)
    remaining = [le for le in LESSONS if le["key"] not in done]
    finished = not remaining
    current = None if finished else say(remaining[0], mode)
    return {
        "learner_id": learner_id,
        "guide": GUIDE,
        "step": current,
        "done": len(done),
        "total": len(LESSONS),
        "finished": finished,
        "note": ("that is all of it — the guide is on every screen if you want "
                 "one part again" if finished else
                 f"step {len(done) + 1} of {len(LESSONS)}"),
    }


def _done(learner_id: str) -> set[str]:
    rows = db.connect().execute(
        "SELECT lesson FROM tutorial_progress WHERE learner_id=?",
        (learner_id,)).fetchall()
    return {r["lesson"] for r in rows}


def mark(learner_id: str, key: str, mode: str = "text") -> dict:
    """Mark one step done and hand back the next.

    Recorded per step rather than as a cursor, so somebody who skipped ahead
    and came back is not told they have finished things they never saw.
    """
    _index(key)
    conn = db.connect()
    conn.execute(
        "INSERT INTO tutorial_progress (learner_id, lesson, done_at)"
        " VALUES (?,?,?) ON CONFLICT (learner_id, lesson) DO NOTHING",
        (learner_id, key, db.utcnow()))
    conn.commit()
    return where(learner_id, mode)


def step(key: str, mode: str = "text") -> dict:
    """One named step, for a screen that wants to explain itself."""
    return say(LESSONS[_index(key)], mode)


def for_screen(number: int, mode: str = "text") -> dict | None:
    """The lesson that covers a given screen, if any.

    What lets the help button on screen 81 say *"this is the microphone one"*
    rather than opening a tour at the beginning.
    """
    for lesson in LESSONS:
        if number in lesson["screens"]:
            return say(lesson, mode)
    return None
