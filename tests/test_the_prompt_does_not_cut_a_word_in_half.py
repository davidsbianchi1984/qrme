"""Nothing assembled into a prompt is cut inside a word, and a cut says so.

    asked     does the text fit
    mattered  what does the part that fits say

`wall.parts` learned this for posts a person writes: *a cut inside a word is
what was reported and is the one outcome this refuses*. Everything that
assembles a PROMPT went on slicing with a bare `[:n]` — which is the same
defect facing the model instead of a reader, and worse there, because a reader
sees a word end mid-air and distrusts it while a model reads straight on.

Two places in the profile's own prompt, and they are not equally serious.

**Life material** was cut at 160 characters. That is a sentence fragment, and
one ending mid-word read as the profile's memory of itself trailing off.

**A clinician's letter** was cut at 400. This is the one place in the whole
prompt where a truncation can INVERT what was written: four hundred characters
can land inside *no history of cardiac arrhythmia* and hand the profile the
opposite of the sentence, under a heading that tells it it is up to speed.

A word boundary does not fix the second one — *"no history of"* is itself a
clean whole-word cut. So the boundary is the smaller half of this, and the
MARKER is the half that does the work: something has to say plainly that a
qualification may sit in the part nobody can see.
"""

from __future__ import annotations

from qrme import persona
from qrme.common import clipped

from tests.test_capabilities import (make_interactor, make_profile,  # noqa: F401
                                     pdi_pair)

NOTE = ("The patient reports no history of cardiac arrhythmia, and the "
        "most recent panel was entirely clean. " * 40)
ITEM = ("A long entry about the years spent restoring wooden boats on the "
        "north coast, and what that taught about patience. " * 10)


# -- the clipper ----------------------------------------------------------

def test_a_word_is_never_cut_in_half():
    """Swept across every cap rather than checked at one.

    A single cap tests the sentence as much as the code: the first version
    of this picked one number, and the number happened to land on a space,
    so it passed against a build with the boundary search taken out. The
    sweep has nowhere to be lucky.
    """
    line = "The patient reports no history of arrhythmia and slept well."
    for cap in range(10, len(line)):
        out, cut = clipped(line, cap)
        assert cut is True and line.startswith(out), cap
        assert line[len(out)] in " .", f"cap {cap} cut inside a word: {out!r}"


def test_text_that_fits_is_returned_untouched():
    assert clipped("short enough", 100) == ("short enough", False)


def test_one_unbroken_run_is_cut_at_the_ceiling_rather_than_looping():
    """A URL, a chemical name, an identifier. There is no boundary to find,
    and the caller's marker is what keeps that honest."""
    out, cut = clipped("x" * 200, 30)
    assert cut is True and len(out) == 30


def test_the_cut_is_reported_and_not_guessed_at():
    """The flag exists because only the caller knows how to word it for
    where the text is going — a source item and a clinician's letter want
    different sentences."""
    assert clipped("a" * 10, 5)[1] is True
    assert clipped("a" * 10, 50)[1] is False


# -- and in the prompt ----------------------------------------------------

def _prompt(client, **kw):
    """A real profile row, not a hand-built dict: the prompt builder reads
    fields a stub forgets, and a test that stubs them is testing its own
    idea of a profile."""
    from qrme import db

    dana = make_profile(client)
    row = dict(db.connect().execute(
        "SELECT * FROM profiles WHERE id=?", (dana["id"],)).fetchone())
    return persona.build_system_prompt(row, None, None, **kw)


def test_a_shortened_life_entry_says_it_continues(client):
    said = _prompt(client, sources=[{"kind": "memory", "title": "Boats",
                             "content": ITEM}])
    assert "this entry continues" in said, (
        "a life entry is cut with nothing saying so, so the profile reads "
        "its own memory trailing off mid-thought as the whole of it"
    )


def test_a_life_entry_that_fits_says_nothing(client):
    said = _prompt(client, sources=[{"kind": "memory", "title": "Boats",
                             "content": "Restored a dinghy in 1998."}])
    assert "this entry continues" not in said


def test_a_shortened_clinical_letter_says_a_negation_may_be_missing(client):
    """The whole point of the block is that the patient should not have to
    retell everything. A letter cut mid-way means they do — and worse, the
    profile does not know it."""
    said = _prompt(client, clinical_notes=[{"from": "Dr Okafor", "at": "2026-08-01",
                                    "content": NOTE}])
    assert "THE REST OF THIS LETTER IS NOT SHOWN" in said
    assert "negation" in said and "Ask rather than conclude" in said


def test_a_clinical_letter_that_fits_is_left_alone(client):
    short = "Seen today. Blood pressure normal. Continue as before."
    said = _prompt(client, clinical_notes=[{"from": "Dr Okafor", "at": "2026-08-01",
                                    "content": short}])
    assert short in said
    assert "NOT SHOWN" not in said


def test_the_clinical_letter_gets_more_room_than_a_life_entry(client):
    """They are not the same kind of thing. A life entry is one of eight and
    is meant to be a prompt for recall; a clinician's letter is a document
    somebody wrote about a person, and cutting it is the risk above."""
    said = _prompt(client, clinical_notes=[{"from": "Dr Okafor", "at": "2026-08-01",
                                    "content": NOTE}])
    body = said[said.index("Dr Okafor"):]
    # Not a number of its own: the claim is the *relationship* between the two
    # caps, so it is asserted against them. A bare 400 here would be a floor
    # nothing compares against what it measures — see tests/ratchets.py.
    assert len(body) > persona.LIFE_SNIPPET_CHARS, (
        "a clinician's letter is still held to the life-entry ceiling"
    )
    assert persona.CLINICAL_LETTER_CHARS > persona.LIFE_SNIPPET_CHARS


# -- and the person's own words, which are the last two ---------------------
#
# A clinician's letter and a life entry are material ABOUT somebody. These two
# are what the person themselves typed, and both reach a prompt: the note
# arrives as "They said: …" under the document it describes, and the caption
# lands in the transcript every profile in the room reads. Cut bare they ended
# mid-word, which reads to a model as somebody trailing off rather than as a
# sentence this product shortened.

import inspect  # noqa: E402
import re  # noqa: E402

from qrme import briefcase  # noqa: E402
from qrme.routers import community  # noqa: E402

#: A slice with a number big enough to be prose. `at[:10]` is an ISO date;
#: `note[:400]` is a person's sentence being guillotined.
_BARE_SLICE = re.compile(r"\[:\s*(\d{2,})\s*\]")
_NOT_PROSE = {10, 160}   # a date; and `title[:160]`, which is a filename


def test_the_note_on_a_document_is_not_cut_bare():
    source = inspect.getsource(briefcase.add)
    bare = [int(n) for n in _BARE_SLICE.findall(source)
            if int(n) not in _NOT_PROSE]
    assert not bare, f"a person's note is cut with a bare slice at {bare}"
    assert "clipped(" in source


def test_a_long_note_says_they_wrote_more(client):
    item = briefcase.add("p1", "i1", kind="document", title="Filing",
                         text="Some text.", read=True,
                         note="It matters because " * 60)
    assert item["note"].endswith("(they wrote more than is kept here)")
    assert not item["note"].split("…")[0].rstrip().endswith("becaus")


def test_a_short_note_is_left_exactly_alone(client):
    said = "The second application, filed last March."
    item = briefcase.add("p1", "i1", kind="document", title="Filing",
                         text="Some text.", read=True, note=said)
    assert item["note"] == said


def test_the_caption_on_a_share_is_not_cut_bare():
    source = inspect.getsource(community.share_into_room) if hasattr(
        community, "share_into_room") else None
    if source is None:
        # The route is named differently; read the module and find the caption
        # handling rather than guessing at a function name.
        source = (community.__file__ and open(community.__file__).read())
    assert 'clipped(caption or ""' in source, (
        "a person's caption on a share is still cut with a bare slice"
    )
    assert "they wrote more than the room kept" in source
