"""A door with the key filed off.

Field report: *"my friends list should appear and be able to choose from the
friends list to add other friends and profiles to the chat."*

The invite itself has worked since it was built — the host asks, the guest's
owner accepts, and for a profile this person owns the console holds both
tokens and does the whole round trip. What it asked for was a **profile id**,
typed into a box. `prf_3735f90003ba`. Nobody has that, and nothing on any
screen showed it.

    asked     can you ask somebody into the room
    mattered  can you ask somebody whose id you do not know

So the feature was complete and unusable, which is a shape worth naming
because it does not look like a bug from the inside: every part works, the
tests pass, and the only person who finds out is the one holding the phone.
It is the same finding as the name search — *two beta testers who know each
other by name had no way to become friends* — one room over.

The rows are the friends list, read from the door the Friends screen already
reads. Anybody already seated is shown and not pressable: a row that
re-invites somebody sitting in the room is a press that cannot mean
anything. The id box stays, second, because an id from somewhere else is
still a real way in.
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
INSIDE = REPO / "app" / "src" / "screens" / "Inside.tsx"
CSS = REPO / "app" / "src" / "styles.css"


def _stripped(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"^\s*//.*$", "", text, flags=re.M)


def _panel() -> str:
    """The invite panel's markup, by the title it is drawn under."""
    code = _stripped(INSIDE)
    start = code.index('tr("ins.ask.title"')
    return code[start:code.index('tr("ins.ask.send"', start)]


def test_the_room_reads_the_list_you_already_have() -> None:
    """The same door the Friends screen reads. A second source of truth for
    who your friends are is how the two drift apart."""
    code = _stripped(INSIDE)
    assert "api.friends(" in code, (
        "the room never asks who your friends are, so the panel can only ask "
        "you to type an id")


def test_the_panel_offers_the_names_before_the_id() -> None:
    """Order is the whole fix.

    The id box was not wrong; it was alone. A person who has to scroll past
    a text field wanting `prf_...` to reach the list has been told what this
    screen thinks the normal way in is.
    """
    panel = _panel()
    assert "ins.ask.yours" in panel, (
        "the invite panel does not draw your friends list at all")
    assert panel.index("ins.ask.yours") < panel.index("ins.ask.orid"), (
        "the id box comes before the list — that is the door with the key "
        "filed off, moved down a line")
    assert "ins.ask.ph" in panel, (
        "the id box was removed entirely; an id from somewhere else is still "
        "a real way in and the list not covering it is not a reason to take "
        "the box away")


def test_a_row_carries_the_press_itself() -> None:
    """Picking is the point. A list that shows names and still makes you
    type the id is a directory, not a door."""
    panel = _panel()
    assert re.search(r"askIn\(\s*f\.profile_id\s*\)", panel), (
        "the rows do not invite anybody — the list is decoration")


def test_somebody_already_in_the_room_is_shown_and_not_offered() -> None:
    """Two ways to get this wrong, and the guard holds both.

    Dropping seated friends from the list makes the list stop matching the
    list you know, and a person hunts for a name that is right there in the
    room. Leaving them pressable offers an invite that cannot mean anything.
    """
    panel = _panel()
    assert re.search(r"seats\.some\(", panel), (
        "the panel does not check who is already seated")
    assert "ins.ask.here" in panel, (
        "a friend already in the room is offered as though they were not, or "
        "hidden as though they were not on your list")
    assert re.search(r"disabled=\{[^}]*seated", panel), (
        "the row for somebody already in the room is still pressable")


def test_an_empty_list_says_so_rather_than_showing_nothing() -> None:
    """A blank space under a heading reads as something that failed to load.
    It also has to point somewhere: the Friends screen is where a list gets
    filled, and the id box is right below."""
    panel = _panel()
    assert "ins.ask.nofriends" in panel, (
        "an empty friends list draws a heading over nothing")


def test_a_list_that_will_not_load_does_not_take_the_invite_with_it() -> None:
    """The friends read is a convenience on top of a door that works.

    Failing it into an error would mean a friends list nobody can fetch
    stops a person inviting somebody by id — a new way to be unable to ask
    anybody into a room, introduced by the fix for not being able to ask
    anybody into a room.
    """
    code = _stripped(INSIDE)
    call = re.search(r"api\.friends\([^;]*?;", code, re.S)
    assert call, "the friends read moved — this guard reads it by name"
    assert ".catch(" in call.group(0), (
        "a friends list that will not load has no fallback, so the panel "
        "breaks instead of degrading to the id box")
    assert "setError" not in call.group(0), (
        "a friends list that will not load raises the room's error — the "
        "invite still works and should still be offered")


def test_the_rows_have_somewhere_to_scroll() -> None:
    """Forty friends is still a panel, not a page — and the id box under the
    list has to stay reachable."""
    css = re.sub(r"/\*.*?\*/", "", CSS.read_text(encoding="utf-8"), flags=re.S)
    block = re.search(r"\.rh-list\s*\{([^}]*)\}", css)
    assert block, ".rh-list has no rules — the list grows the panel off-screen"
    assert "overflow-y" in block.group(1) and "max-height" in block.group(1), (
        "the list is unbounded, so a long one pushes the id box and the send "
        "button past the bottom of the screen")
