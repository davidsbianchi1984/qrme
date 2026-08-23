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
