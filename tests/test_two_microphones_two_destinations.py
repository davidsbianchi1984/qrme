"""The microphone fills the bar; the wave hands over the conversation.

Both voice controls on the chat screen called `openTalk`, so they did the
same thing and neither did dictation — there was no way to speak a message
and then read it back before sending it.

    asked     does the microphone open
    mattered  where do the words it hears go

They are different jobs. The microphone beside the composer fills a field
somebody is looking at and can correct. The wave beside Send leaves the text
surface for a voice-only conversation. One handle for both would have been
the same defect the talk overlay already had: two sessions writing to one
piece of state.
"""

import re
from pathlib import Path


def _repo() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


APP = _repo() / "app" / "src"
CHAT = (APP / "screens/Chat.tsx").read_text(encoding="utf-8")


def test_the_microphone_dictates_rather_than_opening_the_overlay():
    m = re.search(r'aria-label=\{tr\("chat\.mic", lang\)\}(.*?)>🎤</button>',
                  CHAT, re.S)
    assert m, "no microphone button to read"
    assert "dictate" in m.group(1), (
        "the composer's microphone does not dictate")
    assert "openTalk" not in m.group(1), (
        "the composer's microphone still opens the talk overlay, so the "
        "screen has two controls doing one job and no dictation at all")


def test_the_wave_opens_the_voice_conversation_after_send():
    assert 'tr("chat.audio", lang)' in CHAT, "no wave control"
    m = re.search(r'aria-label=\{tr\("chat\.audio", lang\)\}(.*?)</button>',
                  CHAT, re.S)
    assert m and "openTalk" in m.group(1), (
        "the wave does not open the voice conversation")
    assert CHAT.index('tr("chat.send", lang)') < CHAT.index('tr("chat.audio", lang)'), (
        "the wave renders before Send; it was asked to sit after it")


def test_the_two_ears_do_not_share_a_handle():
    """The talk overlay's ear and the composer's dictation are separate
    recognisers with separate state — the defect that closed the overlay's
    ear was two sessions writing to one flag."""
    assert "dictRec" in CHAT and "talkRec" in CHAT, (
        "the two microphones do not have separate handles")
    body = re.search(r"function dictate\(\) \{(.*?)\n  \}", CHAT, re.S)
    assert body, "no dictate() to read"
    assert "talkRec" not in body.group(1) and "wantsEar" not in body.group(1), (
        "dictation touches the talk overlay's own state")


def test_the_bar_is_ready_for_the_words():
    """Asked for, then asked again the other way. The first field call put
    the caret in the bar so dictated words landed where the person was
    looking — and the second watched the on-screen keyboard ride that caret
    up over the conversation: "when you press the audio button ... I want
    the recording feature, but no keyboard popping up."

        asked     where do the dictated words land
        mattered  does asking to speak summon a keyboard

    So the bar draws the recording (the voice-memo strip), the words land
    in the field when it stops, and only a tap into the field itself takes
    the caret."""
    assert "chat-recbar" in CHAT, "the recording bar is gone"
    body = re.search(r"function dictate\(\) \{(.*?)\n  \}", CHAT, re.S)
    assert body, "no dictate() to read"
    assert ".focus()" not in body.group(1), (
        "dictation focuses the field — on a touch device that summons the "
        "keyboard the owner asked to keep down")


def test_the_safety_doors_are_folded_and_not_deleted():
    """Asked for: the two cards off the screen. They are the escalation to
    emergency services and the handoff to a real person — moved, not
    removed."""
    assert '<details className="chat-doors">' in CHAT, (
        "the doors are not folded behind a control")
    for door in ('tr("esc.hdr", lang)', 'tr("real.hdr", lang)'):
        assert door in CHAT, f"a safety door was deleted rather than folded: {door}"
