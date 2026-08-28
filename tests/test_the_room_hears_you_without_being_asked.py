"""The room hears you without being asked.

A voice room already arrived speaking — the 🔊 press was retired when a
field report pointed out that a room you are standing in should not need
permission to be audible. The other half of that press stayed: to SAY
anything you held down a microphone, and to send it you pressed an arrow.

Two field reports, one round:

* "everything seems to be working fine as long as users are in the room.
  They shouldn't have to press the microphone button."
* "while speaking, we should have like 4 to 5 seconds of silence will
  send instead of having to press this button."

    asked     can you talk in this room
    mattered  do you have to ask permission to start, and to finish

Being in a voice room is the intent to speak in it. So the ear opens on
the way in and the control becomes a MUTE, and a person's own silence —
not an arrow — is what commits a sentence to the room.

## The defect this round must not reintroduce

An open microphone in a room where several profiles speak aloud through
the same speaker is exactly the shape that broke JIM's coach sphere:
"it's picking up its own voice and triggering itself and not letting it
finish." One voice did it there; a room can have four.

Going deaf while the room speaks is the easy fix and the wrong one —
interrupting a profile mid-sentence is what a voice room is FOR. So
`app/src/echo.ts` answers the narrower question: are these the room's own
words coming back? It is executed here through node rather than pinned by
regex, because a threshold nobody runs is a threshold nobody has tested.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
INSIDE = (REPO / "app/src/screens/Inside.tsx").read_text(encoding="utf-8")
ECHO = REPO / "app/src/echo.ts"

_RUNNER = """
const ts = require("typescript");
const fs = require("fs");
const src = fs.readFileSync("src/echo.ts", "utf8");
const js = ts.transpileModule(src, {
  compilerOptions: { module: ts.ModuleKind.CommonJS },
}).outputText;
const mod = { exports: {} };
new Function("exports", "module", js)(mod.exports, mod);
const cases = JSON.parse(fs.readFileSync(0, "utf8"));
console.log(JSON.stringify(
  cases.map((c) => mod.exports.isEcho(c[0], c[1]))));
"""


def _run(cases: list[tuple[str, str]]) -> list[bool]:
    done = subprocess.run(
        ["node", "-e", _RUNNER], cwd=REPO / "app", input=json.dumps(cases),
        capture_output=True, text=True, timeout=60)
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout)


# -- the real guard, executed ------------------------------------------------

def test_the_rooms_own_words_are_not_taken_as_a_persons_turn():
    said = "I have been reading about the harbour and the old ferry line."
    heard, mine = _run([
        (said, said),
        ("reading about the harbour and the old ferry", said),
    ])
    assert heard, "the room's own sentence came back and was not recognised"
    assert mine, ("a transcriber's imperfect copy of the room's voice is "
                  "still the room's voice")


def test_a_short_interruption_is_always_a_person():
    """The asymmetry the threshold is chosen for. Cutting a profile off is
    the thing a voice room is for, and the words people cut in with are
    short ones that a long turn is likely to contain."""
    said = "Yes, I think so — no, wait, stop me if this is wrong."
    got = _run([("yes", said), ("no", said), ("stop", said),
                ("wait, stop", said)])
    assert not any(got), (
        "a one- or two-word interruption was swallowed as an echo, which "
        "is the one thing a person in a room must always be able to do")


def test_a_persons_own_sentence_survives_a_talkative_room():
    said = ("The harbour was rebuilt twice. The ferry ran until the "
            "bridge opened. Nobody uses the old pier now.")
    got = _run([("my grandfather worked on that bridge", said)])
    assert not got[0], "a person's own sentence was dropped as an echo"


def test_nothing_said_means_nothing_can_echo():
    got = _run([("anything at all", ""), ("", "")])
    assert not any(got)


# -- the ear stands open -----------------------------------------------------

def test_entering_any_room_opens_the_ear():
    """Every room now, not only the spoken ones.

    The first version of this pair held chat rooms exempt — "the medium
    there is typing, and an ear opening itself would be the product taking
    a liberty nobody asked for" — and the owner overruled it in his own
    words: "when you jump in a room, I shouldn't have to press any
    buttons... you should be able to just speak right away. The text bar
    is there for the blind or people that just like to type." A room is a
    place you speak; typing is the alternative, not the default. What
    stays guarded is the shape of the liberty: the ear opens on ENTRY to
    a place the person chose to walk into, the mic button is the mute,
    and put-away closes everything.
    """
    assert re.search(r"if \(!canDictate\) return;\s*\n\s*"
                     r"byHand\.current = false;\s*\n\s*"
                     r"startTalking\(\);", INSIDE), (
        "nothing opens the microphone on the way into a room — the press "
        "the field reports asked to remove, twice, is still the only way in")


def test_the_first_touch_is_the_grant_the_phone_wanted():
    """iOS opens no microphone a touch didn't carry, so the entry above is
    refused there with `not-allowed` — the phone waiting for a hand, not a
    person saying no. The room's first touch anywhere is that hand: the
    refusal of a machine-started ear raises `earWaiting` instead of a
    fault, a pulsing chip says tap-anywhere in the reader's language, and
    the root's pointer capture starts the ear inside the gesture. Without
    each half of this the iPhone enters every room deaf, which is the
    field report this exists for."""
    assert "setEarWaiting(true)" in INSIDE, (
        "a machine-started refusal must wait for a hand, not report a fault")
    assert re.search(r"onPointerDownCapture=\{[^}]*\n?[^}]*earWaiting", INSIDE), (
        "no touch anywhere opens the waiting ear")
    assert 'tr("ins.ear.tap", lang)' in INSIDE, (
        "the waiting ear says nothing — a person cannot know their tap "
        "is the grant")


def test_the_take_lives_in_the_bar_and_lands_in_the_box():
    """The 🎤 by the paperclip, on the phone's own terms: pressing it turns
    the text bar into a recording strip — cancel, a level that moves when
    you do, stop — and the words land in the draft box, still yours to
    read and edit before the arrow sends them. The earlier design sent
    them as a turn the moment they arrived, and the field report asked
    for this shape instead."""
    assert 'className="rs-chatpill dict-strip"' in INSIDE, (
        "no strip replaces the bar while a take is open")
    assert "recordAsked(me, token, (lvl) => setDictLevel(lvl))" in INSIDE, (
        "the strip's level is decoration — nothing feeds it the microphone")
    assert re.search(r"dictDropped\.current\)\s*\{\s*\n\s*"
                     r"setDraft", INSIDE), (
        "the words no longer land in the box")
    assert "if (text) await sendText(text);" not in INSIDE, (
        "a take still sends itself — the words must wait in the box")


def test_all_four_rail_buttons_stand_without_the_key():
    """"There should be four." A session without the owner's key used to
    lose two rail buttons silently, which reads from a phone as broken
    rather than locked. The buttons stand, and the panel says what opens
    them."""
    rail = (REPO / "app/src/TalkRail.tsx").read_text(encoding="utf-8")
    assert "OWNERS.includes(p)) return !!ownerToken" not in rail, (
        "the owner panels vanish again without the key")
    assert 'tr("rail.locked", lang)' in rail, (
        "a locked panel opens onto nothing instead of the way to the key")
    assert "!spokenRoom || !canDictate" not in INSIDE, (
        "the chat-room exemption is back; the owner removed it by name")


def test_the_silence_that_sends_is_in_the_range_that_was_asked_for():
    m = re.search(r"const SILENCE_SENDS_MS = (\d+);", INSIDE)
    assert m, "no silence window — the send is still a press"
    assert 4000 <= int(m.group(1)) <= 5000, (
        f"{m.group(1)}ms is outside the 4-to-5 seconds the report asked "
        "for")


def test_the_silence_timer_is_restarted_by_every_heard_fragment():
    """Otherwise a long sentence sends its first half while somebody is
    still saying the second."""
    assert re.search(r"window\.clearTimeout\(silence\.current\);\s*\n\s*"
                     r"silence\.current = window\.setTimeout\(", INSIDE), (
        "the silence window is not restarted when more speech arrives")


def test_what_is_being_heard_is_shown_before_it_is_sent():
    assert "setDraft(pending.current)" in INSIDE, (
        "an open microphone with no visible output is one people repeat "
        "themselves into")


def test_the_ear_restarts_itself_when_the_browser_gives_up():
    """Chrome ends recognition on its own — a quiet stretch, a backgrounded
    tab. A standing ear that died on the platform's schedule would put the
    press straight back."""
    assert re.search(r"if \(wantTalking\.current\) \{ startTalking\(\); "
                     r"return; \}", INSIDE)


def test_the_guard_stands_between_the_words_and_the_room():
    """At the send, not at each fragment: a person's sentence and the
    room's voice can land in the same buffer."""
    say = INSIDE[INSIDE.index("function sendPending"):]
    say = say[:say.index("function startTalking")]
    assert "isEcho(said, roomSaid.current.join(\" \"))" in say
    assert say.index("isEcho") < say.index("api.sayInRoom"), (
        "the turn reaches the room before anything asks whether it was "
        "the room's own voice")


def test_the_room_remembers_what_it_said_before_it_says_it():
    """The microphone is open the whole time a voice is in the air, so the
    words must be in the window before they can come back through it.

    Read through `roomSpeaks` rather than by looking for the assignment
    inline. This guard used to require `roomSaid.current = [` inside the
    playback block and failed the moment that line moved into the one
    function every playback path now calls — which was the fix for a REAL
    version of this bug, where the per-line 🔊 button announced nothing at
    all. A guard that fails when the claim gets safer is reading the shape.
    """
    announce = re.search(r"function roomSpeaks\([^)]*\)\s*\{(.*?)\n  \}",
                         INSIDE, re.S)
    assert announce, "roomSpeaks is gone — nothing records what the room said"
    assert "roomSaid.current = [" in announce.group(1), (
        "the room's own words never enter the echo window")
    # `s = await speakInPieces` rather than `const s = ...`: the assignment
    # moved inside a try when the bound-voice refusal grew a device-voice
    # fallback, and the claim here is about ordering, not declaration form.
    play = INSIDE[INSIDE.index("s = await speakInPieces"):]
    play = play[:play.index("await s.done")]
    assert "roomSpeaks(" in play, (
        "the backlog plays a turn without recording that the room said it")
    assert play.index("roomSpeaks(") < play.index("setVoicing"), (
        "the room starts playing a turn before it remembers saying it")


# -- and lets go -------------------------------------------------------------

def test_leaving_clears_the_decision_before_stopping_the_recogniser():
    """`onend` restarts the ear while `wantTalking` is true, so stopping
    without clearing it spawns a fresh microphone into a room nobody is
    standing in."""
    teardown = INSIDE[INSIDE.index("earRun.current++;"):]
    teardown = teardown[:teardown.index("}, [open]);")]
    for line in ("wantTalking.current = false", "talkRec.current?.stop()"):
        assert line in teardown, f"{line} missing from the room teardown"
    assert teardown.index("wantTalking.current = false") \
        < teardown.index("talkRec.current?.stop()"), (
        "the recogniser is stopped while the decision still says restart")
    assert "clearTimeout(silence.current)" in teardown, (
        "a pending send survives the room being left")


def test_muting_says_what_was_already_heard():
    """Somebody who finished a sentence and reached for the button meant
    to say it."""
    stop = INSIDE[INSIDE.index("function stopTalking"):]
    stop = stop[:stop.index("/** The control is now a mute")]
    assert "sendPending();" in stop
