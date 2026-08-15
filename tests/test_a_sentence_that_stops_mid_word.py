"""The post ended `…not what an agent *can` and said nothing about it.

Reported from the live wall with a screenshot. A profile had been asked for a
specification and answered at length; the wall took the first two thousand
characters and the reader got a sentence that stopped inside a word. Underneath
it, in the thread, was the reader asking the profile to finish — and the whole
document took **five** of those continuations to come out.

    asked     does the post fit
    mattered  does the reader know when it did not

Two things were wrong and only one of them was the number.

**The number.** 2000 was set when the only author was a person at a keyboard,
and nothing technical held it there: `posts.content` is TEXT, which SQLite caps
at a gigabyte; no full-text index reads it; nothing searches it with LIKE. Five
continuations is a measurement, not a guess — the thing being posted was ten
times the ceiling. It is 20000 now.

**The honesty.** A raised ceiling is a ceiling somebody writes past later, so
raising it alone would have bought one document's worth of time. `parts()` is
the half that has to hold: past the cap, text becomes a numbered series where
every piece says where it sits and every piece but the last says it continues.
A reader who lands on part three knows they have missed two.

The estate has met this shape before and always answers it the same way — the
refusal that names its cause, the custody note that lists its limits, the
`still` renderer that says it cannot draw a model rather than drawing a poster
and letting the owner believe otherwise. A cut is allowed. A silent one is not.
"""

from __future__ import annotations

from qrme import wall


def test_the_cap_holds_what_was_actually_being_posted():
    """Five continuations at two thousand characters each. The ceiling has to
    clear that in one post or the report repeats verbatim."""
    assert wall.MAX_BODY >= 5 * 2000, (
        f"MAX_BODY is {wall.MAX_BODY} — the document that was reported took "
        "five continuations to come out, so anything under ten thousand "
        "reproduces the defect on the same input")


def test_a_short_post_is_left_alone():
    """The overwhelming majority. A 'Part 1 of 1' on somebody's two-line note
    would be the cure being worse than the disease."""
    assert wall.parts("just a thought") == ["just a thought"]
    assert wall.parts("") == []


def test_a_long_body_comes_back_as_a_series():
    """The fix, directly."""
    body = ("This is a paragraph that says something. " * 40 + "\n\n") * 20
    pieces = wall.parts(body)
    assert len(pieces) > 1, (
        f"{len(body)} characters came back as one piece — the splitter is not "
        "splitting and the cap will simply refuse it instead")
    assert all(len(p) <= wall.MAX_BODY for p in pieces), (
        "a part is longer than a post may be, so the very thing that splits "
        "it produces something the door refuses")


def test_every_part_says_where_it_sits():
    """A reader who arrives at part three has to know they missed two."""
    body = "x" * 200 + ". "
    pieces = wall.parts(body * 400)
    total = len(pieces)
    for i, piece in enumerate(pieces, 1):
        assert piece.startswith(f"Part {i} of {total}"), (
            f"part {i} does not name itself: {piece[:40]!r}")


def _prose(piece: str) -> str:
    """One part with its header and continuation mark taken back off.

    The round-trip checks below compare words, not characters, so this only
    has to remove what `parts` added — anything it misses shows up as a
    spurious word and fails loudly rather than quietly passing.
    """
    body = piece.split("\n\n", 1)[1] if "\n\n" in piece else piece
    return body.removesuffix("\n\n→ continues").strip()


def test_every_part_but_the_last_says_it_continues():
    """The whole of the report. The reader had to *ask* whether there was
    more, five times."""
    pieces = wall.parts("A sentence with several words in it. " * 2000)
    assert len(pieces) > 2
    for piece in pieces[:-1]:
        assert piece.rstrip().endswith("continues"), (
            "a part ends without saying another follows — which is the "
            "reported defect with a part number stapled to the front")
    assert not pieces[-1].rstrip().endswith("continues"), (
        "the last part claims a sequel, so the reader waits for a post that "
        "is never coming")


def test_no_part_ends_inside_a_word():
    """`…not what an agent *can` — the exact reported symptom.

    A cut inside a sentence is merely unlovely. A cut inside a word is what
    made the post look broken rather than long.

    Checked as a round trip over *words* rather than by inspecting the tail of
    each piece. The first version of this test read the last character of a
    part and tried to look it up in the original — with the part header still
    attached, so the index was meaningless and it reported a break inside
    `floccinaucinihilipilification`, a word the splitter had in fact kept
    whole. Comparing the word sequence catches a broken token *and* a dropped
    one, and cannot be fooled by an off-by-a-header.
    """
    body = ("supercalifragilistic expialidocious antidisestablishmentarianism "
            "floccinaucinihilipilification ") * 300
    pieces = wall.parts(body)
    assert len(pieces) > 1
    rejoined = " ".join(_prose(p) for p in pieces).split()
    assert rejoined == body.split(), (
        "the words that came out are not the words that went in — a part "
        "ends inside a token, or text was dropped at a seam")


def test_one_unbroken_run_still_terminates():
    """A guard on the guard, and on an easy infinite loop.

    Text with no space, line break or full stop anywhere in it — a base64
    blob, a minified script — has no boundary to prefer. The splitter has to
    cut it at the ceiling rather than search forever for a break that is not
    there.
    """
    pieces = wall.parts("A" * (wall.MAX_BODY * 3))
    assert len(pieces) >= 3
    assert all(len(p) <= wall.MAX_BODY for p in pieces)


def test_the_series_publisher_and_the_typed_door_disagree_on_purpose():
    """`publish` refuses over-length; `publish_series` splits it.

    Not an inconsistency. Somebody at a keyboard who has written past the
    ceiling should be told, not silently cut in half or quietly turned into a
    thread they did not ask for. A profile answering at length has no keyboard
    to be told at — and what it did instead was trim to fit and stop mid-word.
    """
    import inspect
    assert "MAX_BODY" in inspect.getsource(wall.publish), (
        "publish no longer checks the ceiling, so the typed door stopped "
        "telling anybody they went over")
    assert "parts(" in inspect.getsource(wall.publish_series)
