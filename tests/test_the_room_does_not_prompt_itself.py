"""A microphone open while the room is speaking has nothing to offer.

Field report, from Windows and after the text guard had already shipped:
*"the voice that's coming from my speaker, that is the synthetic profile
talking to me, is being picked up on my microphone as a prompt."*

    asked     did the room hear something
    mattered  was it somebody in it

`isEcho` compares what was heard against what the room just said and needs
70% of the words to line up. That catches a clean echo. It does not catch a
misheard one — the microphone hears the speaker across the room, the
recogniser guesses at it, and a guess about a sentence is not 70% the same
sentence. The mangled version cleared the guard and was sent as though a
person had said it, so the profile answered itself, in a conversation about
somebody's psychiatric care.

The certain test is not what the words were, it is **when they arrived**.
`speaking` says exactly that, and it was sitting in this component unread
while the text matcher did all the work alone. The sibling standing ear in
JIM has had `if (!text || speakingNow()) return;` since it was written.

Both nets stay, because they fail in different directions: a text match
misses a mangled echo, and a clock misses a late one.
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


def _stripped() -> str:
    text = INSIDE.read_text(encoding="utf-8")
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"^\s*//.*$", "", text, flags=re.M)


def _fn(name: str) -> str:
    code = _stripped()
    m = re.search(r"function %s\(.*?\n  \}" % re.escape(name), code, re.S)
    assert m, f"{name} moved — this guard reads it by name"
    return m.group(0)


def test_nothing_heard_while_the_room_speaks_becomes_a_prompt() -> None:
    """The send is the last place it could be stopped, so it is checked
    here even though the ear should already have dropped it."""
    body = _fn("sendPending")
    assert "speaking.current" in body, (
        "what the room says out loud can still be sent back to it as though "
        "a person had said it — the profile prompts itself")


def test_the_ear_drops_it_rather_than_the_send() -> None:
    """Gating only at the send would still put the room's own sentence in
    the person's draft box on the way past. Watching the profile type its
    last line into your composer is the same bug with a worse view."""
    body = _fn("startTalking")
    heard = body[body.index("const heard"):body.index("pending.current =")]
    assert "speaking.current" in heard, (
        "the room's own voice reaches the draft box before anything checks "
        "whether the room was the one talking")


def test_the_tail_covers_a_speaker_still_decaying() -> None:
    """`speaking` goes false the instant the last piece ends. The sound in
    the room does not, and a recogniser delivers a result it formed a moment
    earlier — so the frame right after the voice stops is exactly when a
    late echo lands."""
    code = _stripped()
    assert "disbelieveUntil" in code, "there is no tail after the voice stops"
    assert re.search(r"ECHO_TAIL_MS\s*=\s*\d+", code), (
        "the tail has no length")
    assert re.search(r"speaking\.current = false;\s*\n\s*disbelieveUntil",
                     code), (
        "the tail does not start when the voice stops, so it protects "
        "nothing")


def test_the_text_net_is_still_there() -> None:
    """Two nets, kept. Removing `isEcho` because the clock now catches most
    of it would leave a clean echo arriving after the tail with nothing in
    front of it."""
    assert "isEcho(" in _stripped(), (
        "the text guard was removed — a late echo has nothing to stop it")


def test_every_voice_in_the_room_goes_through_the_same_door() -> None:
    """The miss that made the first fix look like it worked.

    The room has two ways to put a profile's voice in the air: the 🔊 toggle
    that reads the backlog, and the 🔊 on every line. The first release of
    this guard set the flag inside the backlog path only — so a person using
    the per-line button had no time gate AND no `roomSaid` window, which is
    both nets blind at once, and the profile's own speech walked back in as
    a prompt. Reported from a Windows handheld where the recogniser works
    perfectly and heard the speaker beautifully.

        asked     is the room speaking
        mattered  which button started it

    The answer must not depend on the second question. So this counts the
    `speakInPieces` call sites and requires every one of them to announce
    itself — a third way to speak cannot be added without tripping here.
    """
    code = _stripped()
    plays = [m.start() for m in re.finditer(r"speakInPieces\(", code)]
    assert len(plays) >= 2, (
        "the room has fewer voices than it used to — read the shape again "
        "before deleting this guard")
    for at in plays:
        window = code[max(0, at - 600):at + 600]
        assert "roomSpeaks(" in window, (
            "a `speakInPieces` call puts a voice in the room without saying "
            "so, so the microphone hears it with nothing in the way")


def test_the_room_falls_quiet_even_when_the_voice_failed() -> None:
    """A flag left standing deafens the room until it is reloaded.

    Worse than the bug it guards against: that one lets an echo in, this
    one would drop everything a person says for the rest of the session.
    """
    code = _stripped()
    for at in [m.start() for m in re.finditer(r"\.catch\(", code)]:
        window = code[at:at + 400]
        if "roomSpeaks(" in code[max(0, at - 900):at] and "setVoicing" in window:
            assert "roomFellQuiet()" in window, (
                "a voice that failed leaves the room marked as speaking, so "
                "nothing the person says afterwards is believed")


# --- the half the echo fix took away, given back --------------------------

def test_a_person_can_still_interrupt_the_room() -> None:
    """The cost 1.4.1 paid, and the reason it does not have to be paid.

    Dropping everything heard while the room speaks is the only safe rule
    for an ear with no analyser — a recogniser cannot tell somebody leaning
    into the microphone from a speaker across the table. So barge-in went
    with the echo, and the profile talks over you.

        asked     was that sound the room's own voice
        mattered  or somebody interrupting it

    A meter answers it, and it costs nothing to run: it is open only while
    the voice is in the air, records nothing, and sends nothing.
    """
    code = _stripped()
    assert "meterWhileSpeaking(" in code, (
        "nothing measures the room while it speaks, so every sound during a "
        "profile's turn is treated as its echo — including you")
    speaks = re.search(r"function roomSpeaks\([^)]*\)\s*\{(.*?)\n  \}",
                       code, re.S)
    assert speaks and "meterWhileSpeaking(" in speaks.group(1), (
        "the meter is not opened where the room starts speaking, so it "
        "listens at the wrong times or not at all")
    quiet = re.search(r"function roomFellQuiet\(\)\s*\{(.*?)\n  \}", code, re.S)
    assert quiet and "closeMeter" in quiet.group(1), (
        "the meter outlives the voice — a microphone left open after the "
        "room went quiet")


def test_the_send_believes_an_interruption() -> None:
    """A meter that reports and is not read is a microphone open for
    nothing."""
    code = _stripped()
    send = re.search(r"function sendPending\([^)]*\)(.*?)\n  \}", code, re.S)
    assert send, "sendPending moved — this guard reads it by name"
    assert "barged.current" in send.group(1), (
        "the send never asks whether somebody interrupted, so the meter "
        "changes nothing")
    assert "barged.current = false" in send.group(1), (
        "the interruption is not spent, so one raised voice would make the "
        "room believe every echo that followed it")


def test_barging_in_stops_the_voice() -> None:
    """Believing the words while the profile keeps talking over them is
    half an interruption, and the half nobody asked for."""
    code = _stripped()
    meter = re.search(r"meterWhileSpeaking\(\(\) => \{(.*?)\}\)", code, re.S)
    assert meter, "the barge-in handler moved — this guard reads it by name"
    assert "nowSaying.current?.stop()" in meter.group(1), (
        "somebody interrupts and the profile carries on speaking")


def test_the_meter_goes_down_when_you_leave() -> None:
    """A microphone open in a room nobody is standing in."""
    code = _stripped()
    teardown = code[code.index("earRun.current++"):]
    teardown = teardown[:teardown.index("}, [open])")]
    assert "closeMeter" in teardown, (
        "leaving the room leaves the barge-in meter holding the microphone")


def test_the_meter_never_opens_a_microphone_nobody_asked_for() -> None:
    """The question the first version of this meter did not ask.

        asked     can we tell an interruption from an echo
        mattered  whose microphone are we opening to find out

    It opened a stream whenever the room spoke — so somebody reading a room
    with the voices on, who had never pressed the microphone, got a
    recording light they never asked for. That is worse than the problem it
    solves, and no amount of "it records nothing" makes an unasked-for
    microphone acceptable.

    `wantTalking` is the person having already said yes to this room
    hearing them. Under that decision the meter adds nothing new; without
    it, it is the product taking a liberty. Somebody listening in silence
    loses nothing — they were not talking, so there is no interruption to
    recognise.
    """
    code = _stripped()
    speaks = re.search(r"function roomSpeaks\([^)]*\)\s*\{(.*?)\n  \}",
                       code, re.S)
    assert speaks, "roomSpeaks moved — this guard reads it by name"
    gate = re.search(r"if \(([^)]*)\)\s*\{[^}]*meterWhileSpeaking",
                     speaks.group(1), re.S)
    assert gate, "the meter is opened without any condition in front of it"
    assert "wantTalking" in gate.group(1), (
        "the meter opens a microphone for somebody who never pressed one — "
        "a recording light nobody asked for, to solve a problem they do not "
        "have")
