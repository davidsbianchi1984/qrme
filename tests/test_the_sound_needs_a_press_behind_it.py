"""A phone plays what a press started, and nothing else.

Field report, from the device this product is mostly used on: *"I'm pretty
sure on the mobile device it's not playing voice audio whatsoever."* Not the
wrong voice. Not a delay. Nothing — and no error anywhere saying so.

Two rules, and this product broke both in the same eight lines.

## A fresh element has no permission

A phone withholds autoplay unless the playback descends from a real press.
The grant lands on an **element** a person started, and it outlives the
gesture — so one element opened at the door plays every later piece without
asking again.

`spoken.ts` built a `new Audio()` per piece, each one constructed *after* an
await on the synthesis fetch. By then the press that started the turn was
long over and the new element carried no activation of its own, so every
piece was refused. A laptop allows all of it, which is exactly why this
survived every round of testing.

## A refusal that resolves is a lie

`play().catch(() => over())` treated *the platform refused* as *this piece is
finished*. The loop walked every sentence, played none, and resolved like a
reply that had been heard — so the callers' device-voice fallback, which
exists for precisely this case, was unreachable. **A caller cannot fall back
from a success.**

    asked     did the platform play this
    mattered  does anybody find out when it did not

That second one is why this is a guard and not just a fix. The silence was
total *and* unreported, and of those two the unreported half is what made it
survive: a bug that shows up as an error gets found on the first phone.
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
SPOKEN = REPO / "app" / "src" / "spoken.ts"

#: Every screen that speaks a profile's bound voice. Each must be able to
#: hear a rejection, because that is now how "the platform refused" arrives.
SPEAKERS = ("Chat.tsx", "Inside.tsx", "Agent.tsx")


def _src() -> str:
    return SPOKEN.read_text(encoding="utf-8")


def _code(text: str) -> str:
    """Source with `//` line comments and `/* */` blocks removed.

    The prose in this module describes the very mistake it exists to
    prevent — `new Audio(URL.createObjectURL(blob))` appears verbatim in
    the header explaining why it is wrong. A reader that counts a mention
    as a use invents a defect out of its own documentation.
    """
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
    return re.sub(r'^\s*//[^\n]*$', '', text, flags=re.M)


#: The only two things this module may build an element around. `SILENCE`
#: is the opener's inaudible clip, played inside a press so the element
#: carries the grant; the bare one stands in for a screen that never
#: pressed. Anything else is a piece being given its own element.
ALLOWED_AUDIO_ARGS = ("", "SILENCE")


def test_a_piece_is_not_played_through_a_brand_new_element():
    """The regression, named exactly.

    An element built per piece, after an await, is the shape that was
    broken. The first draft of this guard looked for
    `new Audio(URL.createObjectURL(...))` and **passed against the very
    source it was written to fail** — the broken line was
    `const sound = new Audio(src)`, with the blob one variable away. A
    guard that matches the defect's spelling rather than its shape is a
    guard that catches the defect it already knows about.

    So the rule is stated positively: there are exactly two things this
    module may build an element around, and a piece is not one of them.
    """
    code = _code(_src())
    built = [a.strip() for a in re.findall(r'new Audio\(([^)]*)\)', code)]
    wrong = [a for a in built if a not in ALLOWED_AUDIO_ARGS]
    assert not wrong, (
        f"new Audio({wrong[0]}) — an element built around something other "
        f"than {' or '.join(x or 'nothing' for x in ALLOWED_AUDIO_ARGS)}. "
        "If that is a piece, a phone refuses it: the press that could have "
        "permitted it ended at the await above. Set `.src` on the element "
        "a press opened instead.")


def test_the_ear_is_opened_by_a_press_and_reused():
    """One long-lived element, and a press that opens it."""
    code = _code(_src())
    assert "export function openTheEar" in code, (
        "no openTheEar(): there is nothing for a press to open, so the "
        "first piece is the first time this page asks to make a sound — "
        "which is the one moment a phone says no")
    assert re.search(r'^armTheEar\(\);', code, re.M), (
        "openTheEar exists but nothing arms it. Wiring it into each "
        "screen's press handlers is the version of this that ships with "
        "one screen forgotten; arm it once, on any press.")
    assert re.search(r'\.src = ', code), (
        "nothing assigns `.src` — pieces are not being played through a "
        "reused element")


def test_a_refused_first_piece_reaches_the_caller():
    """A refusal must reject, not resolve.

    Checked by shape rather than by running a browser: the promise that
    wraps `play()` must have a rejection path, and the first piece must be
    played inside the `try` whose `catch` re-throws — which is what puts
    the refusal in front of a caller while it can still fall back.
    """
    code = _code(_src())
    assert re.search(r'\.play\(\)\.catch\(\s*\(\s*\w+\s*\)\s*=>\s*\{[^}]*'
                     r'refused\(', code), (
        "play()'s rejection is not routed to a reject — if it resolves, a "
        "reply nobody heard is indistinguishable from one that played out")
    assert "throw why" in code, (
        "the first piece's refusal is swallowed rather than re-thrown; a "
        "caller cannot fall back from a success")


def test_every_speaking_screen_can_hear_a_refusal():
    """Each caller keeps a fallback for the rejection.

    `speakInPieces` rejects for two reasons now — the first piece could not
    be fetched, or could not be played — and to a listener those are the
    same event. A call site with no catch turns either one into a screen
    that quietly says nothing.
    """
    missing = []
    for name in SPEAKERS:
        src = (REPO / "app" / "src" / "screens" / name).read_text(
            encoding="utf-8")
        for m in re.finditer(r'speakInPieces\(', src):
            after = src[m.start():m.start() + 1400]
            before = src[max(0, m.start() - 900):m.start()]
            if "catch" not in after and "try {" not in before:
                line = src[:m.start()].count("\n") + 1
                missing.append(f"{name}:{line}")
    assert not missing, (
        "speakInPieces can reject — no binding, no engine, or a platform "
        "that refused to play — and these call sites have no catch, so the "
        f"screen goes quiet with nothing said about it:\n    "
        + "\n    ".join(missing))
