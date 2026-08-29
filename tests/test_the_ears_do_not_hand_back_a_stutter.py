"""A recogniser stuck on a fragment is not somebody speaking.

## The finding

Two voice memos came back from the ears as this, posted into a room under
the person's own name:

    Nghei, Nghei, Nghei, Nghei, Nghei, … (thirty times) … to comply.
    1 % de typedas 3 – 7 % de typedas 4 – 7 % de typedas 5 – 8 % de typedas …

Neither is speech. It is what a transcriber does when it is handed
near-silence, or a loudspeaker playing the room's own voices back into the
microphone: it locks onto a fragment and repeats it until the audio ends.

    asked     did the ears answer
    mattered  did the ears answer with speech

The stakes are higher than a bad paragraph because these words enter a
room **as that person's message**. A wall of nonsense under somebody's
name is worse than no message at all — and the person cannot tell what
happened, because from their side they simply spoke.

`qrme/scrape.looped` is the check, and it lives beside both ears doors so
the console and all three shells inherit it rather than each screen
guessing. The refusal is `None`, which is the held-not-read posture the
module already keeps for every other kind of missing hearing.
"""

from __future__ import annotations

from qrme import scrape


# The two the field actually produced.
STUTTERS = [
    "Nghei, " * 30 + "to comply.",
    "1 % de typedas 3 - 7 % de typedas 4 - 7 % de typedas 5 - 8 % de "
    "typedas 5-8 % de typedas 9-9 % de typedas",
    "you you you you you you you you you you you you",
    "thank you. thank you. thank you. thank you. thank you. thank you.",
]

# Speech, including the shapes that look repetitive and are not.
SPEECH = [
    "Hey Harold, I don't want to broker to sign the real thing at all. "
    "Always checking with Aisha.",
    "I'll take that as a compliment, but I have to hand part of it back. "
    "I can spec your network to the last patch cable — segmentation, "
    "encryption, diverse paths.",
    "yes",
    "no",
    "I said no, no, no and then I left the room",
    "Aisha, Aisha, can you hear me now that the line is finally open",
    "we need milk, eggs, bread, milk, eggs, bread for the week ahead",
    "",
]


def test_a_fragment_repeated_is_not_speech():
    for text in STUTTERS:
        assert scrape.looped(text), text[:60]


def test_real_speech_is_left_alone():
    """Both halves matter. A guard that ate a real sentence would be a
    worse failure than the one it was written for — somebody's words
    disappearing with no sign they were ever said."""
    for text in SPEECH:
        assert not scrape.looped(text), text[:60]


def test_somebody_can_repeat_themselves():
    """A person really does say a name twice and really does chant. The
    thresholds are half and two-fifths for that reason, not a tenth."""
    assert not scrape.looped("no no no no I told you already that it is "
                             "not what we agreed on last week")
    assert not scrape.looped("David, David, are you there, David can you "
                             "hear me at all right now")


def test_both_ears_doors_check_it(monkeypatch):
    """The uploaded recording and the fetched one. A check on one door is
    a check somebody routes around by using the other."""
    import inspect
    for name in ("transcribe_bytes", "transcribe_url"):
        fn = getattr(scrape, name, None)
        if fn is None:
            continue
        assert "looped(text)" in inspect.getsource(fn), name


def test_a_stutter_becomes_no_words_at_all(monkeypatch):
    """`None`, not an empty string and not the stutter — the caller's
    held-not-read posture, which every reader of this module already
    knows how to draw."""
    monkeypatch.setenv("QRME_EARS_URL", "http://127.0.0.1:9/ears")

    class _Answer:
        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def read(self, _n=None):
            import json
            return json.dumps({"text": "Nghei, " * 30}).encode()

    monkeypatch.setattr(scrape.urllib.request, "urlopen",
                        lambda *a, **k: _Answer())
    assert scrape.transcribe_bytes(b"pretend-audio") is None
