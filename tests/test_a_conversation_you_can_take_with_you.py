"""The conversation you took with you, and what it owes you for coming.

`{tab === "chat" && <Chat/>}` — the screen unmounts on every tab change and
the voice goes with it. That is right for navigating away and wrong for
walking away on purpose: the same event to React, opposite events to the
person. One means they left the conversation; the other means they took it.

    asked     did the screen unmount
    mattered  did the person mean to end the conversation

So one ear in this console outlives its screen. Every other ear is torn down
on unmount, deliberately, because a microphone open on a screen that no
longer exists is a recording indicator nobody can account for — and this
file exists to hold the exception to exactly the terms that make it one:

  * nothing starts it but a press;
  * the strip says on screen that it is listening;
  * ending it is the first control on the strip;
  * and when the browser puts the page away and ends the recogniser, the
    strip says *that* rather than going on claiming to listen.

The last one is not decoration. `away.ts` was written because a backgrounded
page stops hearing without saying so, and silence and deafness look
identical on screen while being opposite facts. An ear that survives a
screen change would be the easiest place in the console to reintroduce that.
"""

import re
from pathlib import Path


def _repo() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


APP = _repo() / "app" / "src"
STRIP = (APP / "WalkAlong.tsx").read_text(encoding="utf-8")
CHAT = (APP / "screens/Chat.tsx").read_text(encoding="utf-8")
SHELL = (APP / "App.tsx").read_text(encoding="utf-8")
STORE = (APP / "walk.ts").read_text(encoding="utf-8")


def test_it_is_mounted_above_the_thing_it_has_to_outlive():
    """Inside the tab switch it would unmount with every other screen, which
    is the whole defect it exists to answer."""
    assert "<WalkAlong />" in SHELL, "the strip is not mounted"
    # Before `<main>`, not merely before the first `tab ===` line. The first
    # draft of this compared it against `{tab === "home"` and passed happily
    # with the strip moved *inside* the content element one line above it —
    # a sabotage that put it exactly where it must not be.
    i = SHELL.index("<WalkAlong />")
    j = SHELL.index('<main className="content"')
    assert i < j, (
        "the strip renders inside the content element that holds the tab "
        "switch; it has to be outside it, or it unmounts with the screen it "
        "was meant to survive")


def test_nothing_opens_it_without_a_press():
    """The exception is earned by being asked for."""
    assert "onClick=" in CHAT and "startWalking({" in CHAT, (
        "nothing hands a conversation to the strip from a button")
    # The store must not start itself.
    assert "startWalking" in STORE and "addEventListener" not in STORE, (
        "the walking store subscribes to something; it is meant to be moved "
        "only by a caller")


def test_the_strip_says_it_is_listening_and_offers_the_way_out():
    for owed in ('tr("walk.listening"', 'tr("walk.quiet"', 'tr("walk.end"'):
        assert owed in STRIP, f"the strip never renders {owed}"
    assert STRIP.index('tr("walk.end"') < STRIP.index('walk-who'), (
        "ending the conversation is not the first control on the strip")


def test_being_put_away_stops_it_and_says_so():
    """The failure `away.ts` was written about, in the one place best placed
    to bring it back."""
    assert "whenPutAway(" in STRIP, "the strip never asks whether it is away"
    m = re.search(r"whenPutAway\(\s*\(\) => \{([^}]*)\}", STRIP)
    assert m and "close()" in m.group(1), (
        "being put away does not close the ear")
    assert 'tr("walk.asleep"' in STRIP, (
        "the strip has no way to say it stopped because the page was put "
        "away — which leaves silence and deafness looking identical again")


def test_coming_back_does_not_reopen_it_by_itself():
    """A microphone that restarts because a tab regained focus is one nobody
    pressed for."""
    # The whole call, brace-matched, rather than a regex that stops at the
    # first `)`. The first draft did stop there, and a sabotage that put
    # `listen(who)` inside a braced return handler sailed past it.
    i = STRIP.index("whenPutAway(")
    depth, j = 0, i
    while j < len(STRIP):
        if STRIP[j] == "(":
            depth += 1
        elif STRIP[j] == ")":
            depth -= 1
            if depth == 0:
                break
        j += 1
    call = STRIP[i:j + 1]
    assert "close()" in call, "being put away does not close the ear"
    assert "listen(" not in call, (
        "the put-away handling restarts the ear itself — a microphone that "
        "reopens because a tab regained focus is one nobody pressed for")
