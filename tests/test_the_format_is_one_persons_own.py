"""The room format belongs to the viewer, and must not leave their browser.

## The correction

The per-seat video window was built with the seat's stored road deciding
what a viewer sees. The owner said otherwise, and was right:

    "when that video button gets pressed it changed the shape and format
     of just the user screen. It doesn't affect everybody else's own chat
     room screens so two real users are in there. If I'm in the video
     format it won't affect it. The other user if they're in the audio
     format, it just renders formatting differently per user"

Two people in one room, two formats, neither moving the other's.

    asked     which format is this room in
    mattered  which format is this PERSON in

## Why a test and not a comment

The failure this guards against is silent and one-directional. A format
posted to the server is a value one person writes and another person's
screen reads — and it would look completely correct to whoever made the
change, because on their own screen it does exactly what they wanted. It
only shows up as a defect on somebody else's screen, in a room, with two
real people in it: the hardest thing in this product to be looking at
when a regression lands.

So the rule is checked where it can be: the module that holds the format
talks to `localStorage` and to nothing else, and no route carries it.

## What this does NOT say

It says nothing about `presence_road`, which is server-side on purpose.
That decides whether a profile's replies are rendered into footage at
all, spending the owner's money against a ceiling they set — a decision
that belongs to the person paying for it and has to outlive any one
browser. The two are different things and the module says so:

    the road      does footage get made, and on whose budget
    the format    do I want to look at footage, avatars or photos
"""

from __future__ import annotations

import re
from pathlib import Path


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()
MODULE = REPO / "app/src/roomFormat.ts"


def test_the_format_module_exists():
    """A guard on the guard: the checks below pass trivially on a file
    that is not there."""
    assert MODULE.exists(), (
        "app/src/roomFormat.ts is gone — the format has moved somewhere "
        "this test can no longer see it, which is the state this file "
        "exists to prevent")


def test_the_format_never_leaves_the_browser():
    """It reaches localStorage and nothing else.

    Not a style rule. A `fetch` or an `api.` call in here is the format
    becoming a thing one person can write and another can read.
    """
    text = MODULE.read_text(encoding="utf-8")
    for reaching in ("fetch(", "api.", "XMLHttpRequest", "WebSocket",
                     "navigator.sendBeacon"):
        assert reaching not in text, (
            f"roomFormat.ts reaches {reaching!r}. The format is one "
            "person's own screen: the moment it travels, two people in a "
            "room stop being able to sit in different formats.")
    assert "localStorage" in text, (
        "roomFormat.ts no longer remembers anything — the format would "
        "reset on every reload")


def test_reading_the_format_cannot_throw():
    """Storage is not always there.

    A private window, cleared site data, or a browser set to block it all
    make `localStorage` raise on access rather than return null. A screen
    that cannot remember the choice still has to draw.
    """
    from tests import ratchets

    text = MODULE.read_text(encoding="utf-8")
    assert text.count("try {") >= ratchets.floor(
        "console.room_format_guards"), (
        "roomFormat.ts reads or writes storage without catching — a "
        "browser that blocks it would take the room down with it")


def test_no_route_carries_a_room_format():
    """The other direction, checked against the server.

    A field named for this on any request model would mean somebody had
    started sending it, whatever the module does.
    """
    offenders = []
    for path in sorted((REPO / "qrme").rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        for hit in re.finditer(r"^\s*(room_format|view_format|seat_format)"
                               r"\s*:", text, re.M):
            offenders.append(f"{path.relative_to(REPO)}: {hit.group(1)}")
    assert not offenders, (
        "the server has a field for the room format:\n    "
        + "\n    ".join(offenders)
        + "\n  It belongs to the viewer's own browser. A stored format is "
          "one person's screen deciding another person's.")
