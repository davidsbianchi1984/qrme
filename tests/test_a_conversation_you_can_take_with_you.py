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


# ---------------------------------------------------------------------------
# The second surface, and what it cost the first one.
#
# The strip was written for one caller and held that caller's wire: a profile
# id and an interactor id, which it posted to `/profiles/{id}/chat` itself.
# Then the console's agent asked for the same button and answered through a
# different endpoint entirely, and the strip had no way to carry it without
# learning a second wire — and a third and a fourth behind that, since JIM's
# two surfaces answer through their own coach.
#
#     asked     can the strip carry this conversation
#     mattered  does the strip have to know what kind it is
#
# So the screen hands over how to take a turn and the strip stays ignorant.
# These hold that: the strip must not learn a wire back, and a surface that
# offers the button must bring its own.


def _braced(src: str, at: int) -> str:
    """The whole `{...}` starting at `at`, brace-matched.

    A regex stopping at the first `}` reads a nested object as the end of the
    call, which in these files is most of them.
    """
    depth, j = 0, at
    while j < len(src):
        if src[j] == "{":
            depth += 1
        elif src[j] == "}":
            depth -= 1
            if depth == 0:
                return src[at:j + 1]
        j += 1
    raise AssertionError("unbalanced braces from the call site")


def _surfaces() -> dict[str, str]:
    """The console's conversations that can be carried."""
    return {name: (APP / f"screens/{name}").read_text(encoding="utf-8")
            for name in ("Chat.tsx", "Agent.tsx")}


def test_the_strip_does_not_know_what_kind_of_conversation_it_carries():
    """The moment it does, a fifth surface is a fifth branch inside it."""
    for wire in ("profileId", "interactorId", "interactorToken"):
        assert wire not in STORE, (
            f"the walking store carries `{wire}` — that is one surface's "
            "wire, and holding it here is what made a second surface need a "
            "second branch")
    assert "from \"./api\"" not in STRIP, (
        "the strip imports the console's api; it is meant to take turns "
        "through the callback the screen handed it, not to know an endpoint")
    assert "w.take(" in STRIP, "the strip never uses the turn it was handed"


def test_every_surface_that_offers_the_walk_hands_over_its_own_turn():
    """A caller that starts a walk without a `take` hands the strip a
    conversation it cannot continue — and the strip finds out at the first
    thing the person says, which is the worst moment to find out."""
    for name, src in _surfaces().items():
        for m in re.finditer(r"startWalking\(\{", src):
            i = m.end() - 1
            depth, j = 0, i
            while j < len(src):
                if src[j] == "{":
                    depth += 1
                elif src[j] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            call = src[i:j + 1]
            assert "take:" in call, (
                f"{name} starts a walk without handing over how to take a "
                "turn")
            assert "shownName:" in call, (
                f"{name} starts a walk without saying who the person is "
                "walking with")


def test_both_of_the_consoles_conversations_offer_it():
    """The agent is not the synthetic profile — different wire, same person
    wanting to leave the screen without leaving the conversation."""
    for name, src in _surfaces().items():
        assert "startWalking({" in src, (
            f"{name} is a conversation this console can hold and offers no "
            "way to take it along")
        assert 'tr("chat.walk"' in src, (
            f"{name}'s walk control is unlabelled or labelled in one "
            "language")


# ---------------------------------------------------------------------------
# Who answered, when the deployment has no model.
#
# `generated_by` is who *actually* wrote a turn rather than who the profile is
# set to, and the field exists because an owner whose own key had expired read
# stub-written text labelled with the model they had chosen. The console shows
# an amber banner for that. Out on the walking strip there is no banner and no
# screen — the person is somewhere else entirely.
#
#     asked     did the turn come back
#     mattered  who wrote it


def test_the_turn_carries_who_answered_it():
    assert "export type Said" in STORE, (
        "a turn is still a bare string, so nothing can say who wrote it")
    assert "offline?: boolean" in STORE


def test_the_strip_says_when_the_fallback_answered():
    assert 'tr("walk.offline"' in STRIP, (
        "the strip never says an answer came from the local fallback, so it "
        "reads as the model the profile is set to")
    assert re.search(r"setOffline\(Boolean\(\s*answer\.offline\s*\)\)", STRIP), (
        "the strip sets the flag from something other than what the screen "
        "handed it — a component that decided this itself would be guessing "
        "about somebody else's endpoint")


def test_the_agent_does_not_claim_a_model_answered():
    """The authoring turn reports no provenance. Saying `offline: false`
    there would be a claim nothing checked, which is the failure this whole
    file keeps finding."""
    src = _surfaces()["Agent.tsx"]
    call = _braced(src, src.index("startWalking({") + len("startWalking("))
    # The property, not the word: the comment there explains why the
    # property is absent, and a check that banned the word would fail on
    # its own explanation.
    assert "offline:" not in call, (
        "the agent's walk asserts who answered, and its wire does not "
        "report that")


def test_the_profile_walk_reads_its_own_wire():
    src = _surfaces()["Chat.tsx"]
    call = _braced(src, src.index("startWalking({") + len("startWalking("))
    # The access, not the name. The comment above the expression mentions
    # `degraded_from` too, so asserting the bare word would pass with the
    # field dropped from the expression and the comment left explaining a
    # read that no longer happens.
    assert "prov?.degraded_from" in call, (
        "the profile's walk does not read the field that exists precisely "
        "for a key that went dead mid-conversation")
    assert "r.provenance" in call, (
        "the walk reads provenance off the message rather than off the "
        "reply, where the record of who wrote it lives")
