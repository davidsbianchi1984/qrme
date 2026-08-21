"""The room can be heard without pressing, and spoken to without typing.

Field report over the room screen: the 🔊 press-per-turn was liked, and
sent back anyway — "you should be able to hear the audio anyways without
having to press the button", the composer should take speech and not only
typing, and a button that is only a send "could be a lot smaller".

    asked     can the room be in your ears and your voice in the room
    mattered  a conversation surface that only reads and types is a
              transcript with a delay

The shape that keeps the autoplay rules honest: hearing the room is a
toggle — one press, the gesture the browser wants — and after it every
profile turn that ARRIVES speaks in its bound voice. This file pins the
edges that made that honest rather than merely loud.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
INSIDE = (REPO / "app/src/screens/Inside.tsx").read_text(encoding="utf-8")


def test_hearing_the_room_is_a_remembered_choice():
    assert 'localStorage.getItem("qrme.room.hear")' in INSIDE
    assert 'localStorage.removeItem("qrme.room.hear")' in INSIDE, (
        "the toggle can be switched on but never off — that is not a "
        "choice, it is a ratchet pointed at the person")


def test_the_backlog_stays_silent():
    """Switching the ear on speaks what comes next, not the scrollback: the
    enable records the last turn already on screen as already heard."""
    m = re.search(r"function flipHearAll\(\)(.*?)\n  \}", INSIDE, re.S)
    assert m, "flipHearAll is gone from the room screen"
    assert "transcript[transcript.length - 1].id" in m.group(1), (
        "enabling the ear does not mark the backlog heard — switching it "
        "on would replay everything ever said in the room")


def test_one_voice_at_a_time():
    assert "speaking.current" in INSIDE, (
        "the speak queue has no lock — a reload mid-playback starts a "
        "second voice over the first")


def test_a_withheld_autoplay_ends_quietly():
    assert re.search(r"sound\.play\(\)\.catch\(", INSIDE), (
        "a rejected play crashes the queue — the browser is allowed to "
        "say no, and the per-turn button is the answer when it does")


def test_the_press_per_turn_survives():
    """The toggle is an addition, not a replacement: every profile line
    keeps its own 🔊, which is also the fallback when autoplay refuses."""
    assert 'tr("ins.hear", lang)' in INSIDE


def test_dictation_types_and_never_sends():
    m = re.search(r"function flipDictation\(\)(.*?)\n  \}", INSIDE, re.S)
    assert m, "flipDictation is gone from the room screen"
    assert "sayInRoom" not in m.group(1), (
        "dictation sends into the room on its own — speech should land "
        "in the box, and the send stays a decision: a room has other "
        "people in it")
    assert "setDraft" in m.group(1)


def test_the_dead_control_rule():
    """No recogniser (iOS Safari), no button — absent, not disabled."""
    assert "canDictate && (" in INSIDE, (
        "the dictation button renders unconditionally — on iOS Safari it "
        "would be a dead control, a broken promise drawn as a button")


def test_the_send_keeps_its_name():
    """The send shrank to a glyph; the name lives on for screen readers."""
    m = re.search(r"aria-label=\{tr\(\"ins.sayit\", lang\)\}", INSIDE)
    assert m, (
        "the compact send lost its accessible name — smaller may not "
        "mean anonymous")
