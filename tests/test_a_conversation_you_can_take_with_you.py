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


# ---------------------------------------------------------------------------
# The ear that survives a minimised window, and the correction behind it.
#
# This file first held that the strip could not survive being put away, and
# that a minimised browser was a native shell's problem. That was half right
# and the wrong half was load-bearing.
#
# `away.ts` is correct that a backgrounded page has its *recogniser* ended by
# the browser. It is not correct about `getUserMedia`: an open capture keeps
# the tab alive, keeps recording while the window is minimised, and makes the
# browser show its own recording indicator throughout — the same bargain iOS
# makes with its orange dot.
#
#     asked     does a hidden page stop hearing
#     mattered  which of the two ways of hearing was it using
#
# So the strip records where it can, and the recogniser is the fallback that
# says what it costs rather than the default that does not.


def test_the_strip_records_where_it_can():
    assert "MediaRecorder" in STRIP and "getUserMedia" in STRIP, (
        "the strip has only the recogniser, which is ended by the browser "
        "the moment the window is minimised")
    assert "w.hears" in STRIP or "who.hears" in STRIP, (
        "nothing uses the way of hearing the screen handed over")
    # The choice is made, not hoped for.
    assert "if (who.hears) void record(who); else listen(who);" in STRIP, (
        "the strip does not prefer the surviving path when it has one")


def test_being_put_away_closes_only_the_path_the_browser_closes():
    """The correction, held in place. Closing the recorder here would be the
    component inventing a failure the browser did not have; leaving the
    recogniser open would be claiming to hear when it cannot."""
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
    assert "!walking()?.hears" in call, (
        "being put away closes the ear whatever kind it is — one of the two "
        "survives, and closing it is inventing a failure the browser did "
        "not have")
    assert 'tr("walk.aloft"' in STRIP, (
        "the strip cannot say it is still listening while the window is "
        "minimised, which leaves the person with no idea the microphone is "
        "open")
    assert 'tr("walk.asleep"' in STRIP, (
        "the strip cannot say it stopped, which is still the truth for the "
        "recogniser path")


def test_the_ear_is_spent_against_the_persons_own_identity():
    """Transcription costs the deployment something, and a route that took
    any id would be a way for a stranger to spend it."""
    for name, src in _surfaces().items():
        call = _braced(src, src.index("startWalking({") + len("startWalking("))
        assert "api.heard(iid, audio, itok)" in call, (
            f"{name} hands over an ear that does not carry this person's "
            "own token")
        assert "iid && itok" in call, (
            f"{name} hands over an ear even with no identity to spend it "
            "against, so the walk starts and the first thing said is refused")


def test_the_route_is_gated_on_that_identity():
    router = (_repo() / "qrme" / "routers" / "interaction.py").read_text(
        encoding="utf-8")
    i = router.index('@router.post("/interactors/{interactor_id}/heard")')
    body = router[i:i + 2600]
    assert "require_interactor(interactor_id, request)" in body, (
        "the general ear is not gated on the interactor's own token, so any "
        "id is a way to spend this deployment's transcription")
    # The raise, not the number. The docstring above the route explains the
    # 503, so asserting the digits passed with the route returning an empty
    # string and the prose still describing a refusal it no longer makes.
    assert "raise HTTPException(\n            503," in body, (
        "a deployment with no ears does not refuse — silence reads as *it "
        "didn't hear me* to somebody who has just spoken into their phone, "
        "and the true answer is one an owner can act on")


# ---------------------------------------------------------------------------
# The platform that does not survive, found on a phone.
#
# A field report, from an iPhone: walk, swipe up to the home screen, come back
# to Safari, and the conversation had stopped without a word. iOS Safari
# suspends the whole page the moment you leave it — capture included — so the
# survival this strip relies on elsewhere is a desktop fact and an Android
# fact, and there it is simply false. It had been written down as though it
# were true everywhere, which is the kind of claim that reads as tested.
#
#     asked     did the capture survive being put away
#     mattered  does the strip find out when it did not
#
# The strip cannot know which platform it is on in advance and must not guess.
# What it owes is to check on the way back — because stopping without a word
# is the failure this whole component is written against, and a platform doing
# the stopping is no excuse for the silence.


def test_coming_back_notices_an_ear_that_did_not_survive():
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
    # The return handler is the second argument, and it must do more than
    # clear a flag: on a platform that suspended the page, clearing the flag
    # leaves the strip drawn exactly as it was over an ear that is gone.
    assert "wants.current" in call, (
        "coming back does not check whether the ear actually survived, so a "
        "browser that stopped listening while away leaves the strip saying "
        "nothing happened")
    assert 'tr("walk.away.stopped"' in call, (
        "the strip has no way to say the browser stopped listening while the "
        "person was away — which is the silence the field report found")
    # And it must not restart by itself. A microphone that reopens because a
    # tab regained focus is one nobody pressed for.
    assert "record(" not in call and "listen(" not in call, (
        "coming back reopens the microphone itself rather than offering it")


def test_the_way_back_is_offered_and_not_only_announced():
    """A strip that says it stopped and offers nothing is a dead end — and
    on the platform this exists for, the person has just come back into the
    app to find it."""
    assert 'tr("walk.again"' in STRIP, (
        "nothing offers the conversation back after the browser stopped it")
    # The control is gated on the trouble, so it appears when there is
    # something to recover from rather than sitting there always.
    i = STRIP.index('tr("walk.again"')
    assert "trouble &&" in STRIP[:i], (
        "the resume control is not tied to the failure it recovers from")


def test_the_claim_about_surviving_names_its_exception():
    """The docstring said an open capture keeps recording while the window is
    minimised, full stop. It does not, on the one platform the reporter was
    holding. A comment that overstates what was tested is how the next person
    stops testing it."""
    store = (APP / "walk.ts").read_text(encoding="utf-8")
    assert "iOS Safari" in store, (
        "`walk.ts` still claims the capture survives being put away without "
        "naming the platform where it does not")
    for wrong in ("keeps recording while the window is minimised,\n",):
        assert wrong not in store, (
            "the unqualified claim is still there")


# ---------------------------------------------------------------------------
# Two field reports from a Windows machine, one root cause.
#
# The strip transcribed its own answer and sent it back as the next thing the
# person said; and it spoke in the browser's built-in robot rather than the
# voice somebody chose and is paying for. Both were this component doing its
# own thing while the console next door already had the machinery — the exact
# drift this file's own docstring warns about, committed anyway.
#
#     asked     did the reply get spoken and the next turn heard
#     mattered  in whose voice, and into whose silence


def test_the_ear_does_not_open_under_the_reply():
    """The recorder posts fixed slices rather than listening continuously,
    so an ear open while the answer plays records the answer. Echo
    cancellation thins what the speakers put back into the microphone; it
    does not remove it."""
    assert "saying" in STRIP, (
        "nothing tracks whether the reply is playing, so the recorder opens "
        "under it")
    # The guard is at the top of `record`, before anything opens. `.{0,400}`
    # with a `\n` terminator matched only the signature line — a lazy
    # quantifier stops at the first newline it can, which is the one right
    # after the brace. Take a fixed slice of the body instead.
    i = STRIP.index("async function record(w: Walking) {")
    head = STRIP[i:i + 700]
    assert "if (saying.current) return;" in head, (
        "`record` opens the microphone without asking whether the answer is "
        "still playing into the room")
    # And the reopen happens after the speaking, in `turnTaken`'s `finally`,
    # rather than beside it.
    j = STRIP.index("async function turnTaken(")
    body = STRIP[j:]
    tail = body[body.index("} finally {"):body.index("\n  }", body.index("} finally {"))]
    assert "record(w)" in tail or "listen(w)" in tail, (
        "the ear is not reopened after the answer finishes, so either it "
        "never reopens or it reopens beside the voice")


def test_what_comes_back_as_the_reply_is_not_answered():
    """Belt to the braces. A slice that caught the tail of an answer
    transcribes as somebody saying that answer, and answering it starts a
    conversation the profile is having with itself."""
    assert "isEcho(" in STRIP, (
        "the strip does not check whether what it heard is its own reply "
        "coming back — the console has had `isEcho` since the rooms grew ears")
    assert 'from "./echo"' in STRIP, "isEcho is not the console's own"
    assert "lastSaid" in STRIP, (
        "nothing remembers what was said, so there is nothing to compare a "
        "suspicious transcript against")


def test_the_walk_speaks_in_the_voice_somebody_chose():
    """`SpeechSynthesisUtterance` is the browser's robot. The profile's own
    bound voice is two hundred lines up in the screen that started the walk,
    and the strip shipped never asking for it."""
    store = (APP / "walk.ts").read_text(encoding="utf-8")
    assert "say?:" in store, (
        "the walk carries no way to speak in the screen's own voice")
    # And the strip reaches for it first. A sabotage that deleted the
    # `w.say` branch — leaving the type, leaving both screens handing a
    # voice over, and quietly using the browser's robot for all of it —
    # passed every other assertion here. Handed over and never used is the
    # same silence as never handed over.
    assert "if (w.say) await w.say(text);" in STRIP, (
        "the strip does not use the voice the screen handed it, so every "
        "reply comes out in the browser's built-in one anyway")
    for name, src in _surfaces().items():
        call = _braced(src, src.index("startWalking({") + len("startWalking("))
        assert "say:" in call, (
            f"{name} hands over no voice, so the strip falls back to the "
            "browser's built-in one and a person reasonably concludes the "
            "voice key is broken")
        assert "speakInPieces(" in call, (
            f"{name}'s walk speaks by some other means than the piece-by-"
            "piece bound voice the screen itself uses")


def test_the_browser_voice_is_the_fallback_and_is_awaited():
    """It stays, for a screen that handed none over. What it must not do is
    return before the speaking ends — that is what let the ear open under
    the reply in the first place."""
    # It lives in `spoken.ts` beside the real voice it stands in for, and
    # is shared with the two screens rather than being the strip's private
    # copy — the guard next door wants every `speakInPieces` call site to
    # have somewhere to fall back to, and three copies of one fallback is
    # how two of them drift.
    spoken = (APP / "spoken.ts").read_text(encoding="utf-8")
    assert "export function plainVoice" in spoken, (
        "the fallback voice is gone; a screen that hands over no voice, or "
        "whose voice was refused, now says nothing at all")
    m = re.search(r"export function plainVoice\(.*?\n\}", spoken, re.S)
    assert m and "u.onend" in m.group(0), (
        "the fallback voice is not awaited, so the ear reopens the moment "
        "speaking starts rather than when it ends")
    assert "plainVoice(" in STRIP, "the strip never reaches its fallback"
