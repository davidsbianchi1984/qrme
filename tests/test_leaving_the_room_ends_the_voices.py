"""Leaving the screen ends the voices.

    asked     what happens to a playing voice when its screen goes away
    mattered  a voice with no screen is a speaker nobody can stop

The twin product found it first, on its conversation screens; the same
defect lived here in three rooms. The Agent orb's relight-after-reply
contract kept re-opening the recogniser under a screen that no longer
exists; the room's ear kept reading the OLD room's turns after a switch
(its handle was a local in the loop); the chat overlay's reply and its
device fallback both played on after navigation. Every screen that
starts a voice now holds a handle it can stop, and stops it on the way
out.
"""

from __future__ import annotations

import re
from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "app/src/screens"


def test_the_orb_tears_down_on_unmount():
    src = (APP / "Agent.tsx").read_text(encoding="utf-8")
    m = re.search(r"useEffect\(\(\) => \(\) => \{([\s\S]*?)\}, \[\]\)", src)
    assert m and "stopVoice()" in m.group(1), (
        "Agent.tsx has no unmount teardown — the relight contract keeps "
        "the recogniser opening under a screen that no longer exists")
    assert "dictation.current?.stop()" in m.group(1), (
        "stopVoice never owned the dictation recogniser — the teardown "
        "must stop it by hand")


def test_the_ears_queue_dies_with_the_room():
    src = (APP / "Inside.tsx").read_text(encoding="utf-8")
    assert "earRun.current++" in src and "run !== earRun.current" in src, (
        "the ear's queue has no run counter — switching rooms keeps it "
        "reading the old room's turns into the new one")
    m = re.search(r"useEffect\(\(\) => \(\) => \{([\s\S]*?)\}, \[open\]\)",
                  src)
    assert m and "nowSaying.current?.stop()" in m.group(1), (
        "the room-change cleanup no longer stops the playing turn")
    assert "dictation.current?.stop()" in m.group(1), (
        "the room-change cleanup no longer stops the dictation")


def test_the_chat_reply_dies_with_the_screen():
    src = (APP / "Chat.tsx").read_text(encoding="utf-8")
    m = re.search(r"useEffect\(\(\) => \(\) => \{([\s\S]*?)\}, \[\]\)", src)
    assert m and "saying.current?.stop()" in m.group(1), (
        "Chat.tsx no longer stops the reply on unmount")
    assert "speechSynthesis.cancel()" in m.group(1), (
        "the device fallback outlives the screen — cancel it too")
