"""A microphone that has stopped must not still be drawn as listening.

A field report, with a photograph: tabs dropping into the background
mid-conversation. What happens underneath is not a crash. The browser
throttles a hidden page's timers, suspends its audio, and ends its speech
recogniser; a frozen tab stops running at all. None of that arrives as an
error, so the console keeps every light it had lit — the orb saying it is
listening, the mic button lit in the room, the line saying the room hears
you — over a microphone that stopped some minutes ago.

    asked     does the console stop listening when it is put away
    mattered  does it stop *saying* it is listening

The first half already happened, without being asked and without being
reported. The second is the defect, and it is the same shape as several
this suite has caught: a failure that is both total and unreported
survives, and the unreported half is what lets it. Silence and deafness
look identical on screen and are opposite facts — one means nobody spoke,
the other means nobody could be heard.

Two of this console's three ears made it worse than quiet. The orb's
`onend` and the room's `onend` both relight, on purpose: the browser ends
a recogniser on its own schedule and the person's decision has not
changed. A backgrounded tab is not that. Relighting there stood a fresh
recogniser into a page that could not run one, which ended immediately,
which relit — for as long as the tab stayed away, with the surface saying
it was listening throughout. The room's own comment named the case
("a tab blur") and treated it as the ordinary one.

The rule these guards hold: an ear may relight itself, but never without
asking first, and never without the screen saying which of the two it is.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()
SRC = REPO / "app" / "src"
AWAY = SRC / "away.ts"
SCREENS = SRC / "screens"

#: Every screen that holds a live recogniser, and the sentence its surface
#: owes somebody whose tab went to sleep under it. Chat's overlay listens
#: one turn per press and has nothing to stand back up, so it drops the
#: light and says nothing — a press is not a thing to replay on somebody's
#: behalf when they come back.
EARS = {
    "Agent.tsx": "agent.ear.asleep",
    "Inside.tsx": "ins.voice.asleep",
    "Chat.tsx": None,
}


def _stripped(path: Path) -> str:
    """Source with comments gone.

    Each of these files documents the mistake in the words the fix uses,
    and a guard that counts a mention as a use invents a defect out of the
    documentation written to prevent it — this suite has already had one
    guard trip on its own docstring.
    """
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"^\s*//.*$", "", text, flags=re.M)


def test_the_console_has_somewhere_to_ask_whether_it_was_put_away() -> None:
    """One module answers it, so no screen has to remember the answer."""
    assert AWAY.exists(), "app/src/away.ts is where the suspension says its name"
    code = _stripped(AWAY)
    assert "export function putAway" in code, "nothing can ask *am I away now*"
    assert "export function whenPutAway" in code, (
        "nothing can be told when that changes")
    assert "visibilitychange" in code, (
        "a page that never listens for its own suspension cannot report it")
    assert "removeEventListener" in code, (
        "whenPutAway must hand back a release, or every screen leaks a watcher")


@pytest.mark.parametrize("screen", sorted(EARS))
def test_every_screen_holding_a_microphone_hears_about_the_tab(
        screen: str) -> None:
    """A screen that never subscribes cannot know, whatever else it does."""
    code = _stripped(SCREENS / screen)
    assert "whenPutAway" in code, (
        f"{screen} holds a live recogniser and never asks to be told the page "
        "was put away — the light it drew stays drawn")


@pytest.mark.parametrize("screen", ["Agent.tsx", "Inside.tsx"])
def test_no_ear_relights_itself_without_asking(screen: str) -> None:
    """The relight loops, which are the whole reason this was more than
    a stale light.

    Both are correct in their ordinary case and were written for it. The
    hidden tab is the case where restarting cannot work and stopping is
    not reported, so the loop spins with nothing to show for it.
    """
    code = _stripped(SCREENS / screen)
    relights = [m.group(1) for m in
                re.finditer(r"onend = \(\) => \{(.*?)\n    \};", code, flags=re.S)]
    restarting = [b for b in relights
                  if re.search(r"start(?:Voice|Talking)\(", b)]
    assert restarting, (
        f"{screen} has no relighting onend any more — read the shape again "
        "before deleting this guard")
    for body in restarting:
        assert "dozing" in body, (
            f"{screen} relights its recogniser from onend without asking "
            "whether the page is away — that is the loop that ran until the "
            "tab came back, with the surface saying it was listening")


@pytest.mark.parametrize("screen", sorted(EARS))
def test_no_ear_is_started_into_a_page_that_is_already_asleep(
        screen: str) -> None:
    """The second door into the same loop.

    A reply that finished speaking after the tab went away relights the
    orb; a voice room entered in a background tab stands its ear. Neither
    passes through `onend`, so guarding only the relight leaves the start
    itself free to open a microphone nobody can be heard through.
    """
    assert "putAway()" in _stripped(SCREENS / screen), (
        f"{screen} starts a recogniser without asking whether the page is "
        "already in the background")


@pytest.mark.parametrize("screen,key",
                         [(s, k) for s, k in sorted(EARS.items()) if k])
def test_the_surface_says_asleep_rather_than_saying_listening(
        screen: str, key: str) -> None:
    """Taking the light down is half of it.

    A person who was talking and got nothing back needs to know which of
    the two happened, and *this tab is in the background* is a sentence
    with something to do about it. An empty caption is not.
    """
    code = _stripped(SCREENS / screen)
    assert key in code, (
        f"{screen} takes its microphone down when the tab sleeps and says "
        f"nothing about it — {key} is the sentence it owes")
    rows = (SRC / "l10n.ts").read_text(encoding="utf-8")
    assert f'"{key}"' in rows, f"{key} has no row in l10n.ts"


def test_a_press_is_not_replayed_on_somebodys_behalf() -> None:
    """What comes back, and what does not.

    A standing ear was a decision and stands itself up again. Dictation
    was a press into a text box, and re-opening a microphone somebody did
    not ask for a second time — while they are looking at another tab —
    is the opposite failure to the one being fixed here.
    """
    for screen in ("Agent.tsx", "Inside.tsx"):
        code = _stripped(SCREENS / screen)
        watch = re.search(r"whenPutAway\((.*?)\n    \}\)", code, flags=re.S)
        assert watch, f"{screen}'s put-away watch moved — this guard reads it"
        leaving, _, returning = watch.group(1).partition("},")
        assert re.search(r"[Dd]ictation", leaving), (
            f"{screen} leaves dictation holding the microphone when the tab "
            "sleeps")
        assert not re.search(r"startDictation\(|setDictating\(true\)",
                             returning), (
            f"{screen} re-opens dictation when the tab comes back — nobody "
            "pressed it twice")
