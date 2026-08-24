"""An ear that opens stays open.

`SpeechRecognition.continuous` defaults to **false**, and the specification
is explicit about what that means: the engine stops after the first utterance
or the first pause. A recogniser started without setting it listens for about
a second and shuts itself.

    asked     did the microphone open
    mattered  is it still open while somebody is speaking

That is what the chat screen did. It set `lang`, `onresult`, `onend` and
`onerror` and nothing else, read only `e.results[0][0]` — the very first
phrase the engine ever settled — and its `onend` dropped straight back to
"tap to talk" while the person was mid-sentence. The room's dictation has
set `continuous` since it was written; the chat screen was a worse copy of
a listener that already worked here.

These read the console's own source, because the defect is a property that
was never written rather than behaviour that can be called: there is no
`SpeechRecognition` in a test runner, and a stub would only prove that the
stub was configured.
"""

import re
from pathlib import Path


def _repo() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


APP = _repo() / "app" / "src"

#: Every console screen that constructs a recogniser meant to hear a person
#: speak a whole thought, and the function that does it.
LISTENERS = [
    ("screens/Chat.tsx", "talkListen"),
    ("screens/Inside.tsx", None),
]


def _body(path: str, func: str | None) -> str:
    src = (APP / path).read_text(encoding="utf-8")
    if func is None:
        return src
    i = src.index(f"function {func}(")
    j = src.index("\n  }", i)
    return src[i:j]


def test_every_listener_asks_to_stay_open():
    """The property whose absence is the whole defect."""
    missing = [p for p, f in LISTENERS
               if not re.search(r"\.continuous\s*=\s*true", _body(p, f))]
    assert not missing, (
        "these open a microphone without setting `continuous = true`, so the "
        f"engine stops after one utterance: {missing}")


def test_the_chat_listener_keeps_what_it_has_already_heard():
    """`e.results[0][0]` is the first phrase and only ever the first phrase.
    A continuous session appends, so the reader has to walk what is new."""
    body = _body("screens/Chat.tsx", "talkListen")
    assert "e.results[0][0]" not in body, (
        "the listener reads only the first result, so a second sentence "
        "replaces nothing and is lost")
    assert re.search(r"for\s*\(", body), \
        "a continuous session hands back a growing list; this reads one item"


def test_the_chat_listener_can_be_closed_on_purpose():
    """A microphone that reopens itself needs a way to be told to stop, or
    it is one that cannot be closed."""
    src = (APP / "screens" / "Chat.tsx").read_text(encoding="utf-8")
    assert "function talkStop(" in src, "no deliberate way to close the ear"
    assert "wantsEar" in src, (
        "nothing separates 'the engine timed out' from 'the person asked to "
        "stop', so a reopening listener cannot tell the two apart")
    # And put-away must clear the wish too, or the restart fights the
    # handler that exists to put the microphone down.
    i = src.index("whenPutAway(")
    assert "wantsEar.current = false" in src[i:i + 300], \
        "put-away stops the recogniser but leaves it wanting to reopen"


def test_leaving_the_screen_closes_the_microphone():
    """The teardown stopped the voice and left the ear open — a tab kept the
    recording indicator lit on a screen that was no longer there."""
    src = (APP / "screens" / "Chat.tsx").read_text(encoding="utf-8")
    i = src.index("useEffect(() => () => {")
    teardown = src[i:src.index("}, []);", i)]
    assert "talkRec.current" in teardown, \
        "unmount does not close the recogniser"


def test_the_avatar_picker_is_not_on_the_talk_screen():
    """`idn.deck.market` is the avatar deck's own label. It was rendered as a
    button on the face screen, where it read as a stray box of text under the
    controls."""
    src = (APP / "screens" / "Chat.tsx").read_text(encoding="utf-8")
    assert "idn.deck.market" not in src, \
        "the avatar deck's label is back on the chat screen"


def test_the_talk_screen_can_share():
    """A photo, a video, the camera and a document — from the screen somebody
    is actually on while talking, not only from the composer below it."""
    src = (APP / "screens" / "Chat.tsx").read_text(encoding="utf-8")
    for key in ("chat.share.photo", "chat.share.video", "chat.share.file"):
        assert key in src, f"{key} is not offered"
    assert "talkPlus" in src, "the talk overlay has no share menu"
    for ref in ("libRef", "vidRef", "docRef", "camRef"):
        assert f"{ref}.current?.click()" in src, f"{ref} is never opened"
