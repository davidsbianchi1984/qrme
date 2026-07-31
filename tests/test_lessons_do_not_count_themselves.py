"""No lesson states how many lessons there are.

Written the moment the mistake was made. The lesson introducing the
walkthrough said it was "thirty-eight written steps" — true when the sentence
was typed, false one line later, because adding that lesson made thirty-nine.

The shape is worth a guard rather than a correction. A count in prose is a fact
about the collection embedded in a member of it, so **the act of adding a
member falsifies it**, and nothing about writing the next lesson prompts anyone
to re-read the earlier ones. It is the same defect as a docstring promising
more than its code enforces, with a shorter fuse: at least the docstring only
goes stale when somebody edits the function.

The live number is available where it belongs — `GET /tutorial/progress/{id}`
returns `total`, and the screen renders that. Prose says what kind of thing the
walkthrough is; the API says how big it is today.

This also covers the ordinary version of the mistake: `qrme/help.py` and the
README both describe the tutorial, and a count written into either would drift
the same way.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from qrme import tutorial


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()

# Numbers written as words, up to a plausible ceiling for a walkthrough. Digits
# are covered separately — `screens=(160,)` makes a bare digit search useless
# inside the module, so the two halves are checked differently.
_WORD_NUMBERS = (
    "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty",
    "ninety", "hundred",
)


@pytest.mark.parametrize("lesson", tutorial.LESSONS, ids=lambda le: le["key"])
def test_no_lesson_says_how_many_lessons_there_are(lesson):
    """A member of a collection must not state the collection's size."""
    prose = f"{lesson['what']} {lesson['try_it']}".lower()
    # Only flag a number when it is near a word for the thing being counted —
    # "thirty-eight steps", "39 lessons". A lesson may legitimately mention
    # other quantities ("$20 a month", "sixteen industries").
    for word in _WORD_NUMBERS:
        for noun in ("step", "lesson", "chapter"):
            pattern = rf"{word}[\w-]*\s+(?:written\s+)?{noun}"
            assert not re.search(pattern, prose), (
                f"{lesson['key']} states how many {noun}s there are. Adding "
                f"the next lesson makes that false, and nothing about writing "
                f"it would prompt anybody to re-read this one. The live count "
                f"is `total` on GET /tutorial/progress/{{id}}.")
    for noun in ("steps", "lessons", "chapters"):
        assert not re.search(rf"\d+\s+(?:written\s+)?{noun}", prose), (
            f"{lesson['key']} states a numeric count of {noun}")


def test_the_walkthrough_publishes_its_own_size():
    """The guard above is only reasonable because the number is available.

    Refusing prose a fact is fine when the fact is served somewhere better.
    If `total` ever stopped being returned, hard-coding a count would start
    being the least-bad option again — so this asserts the alternative
    exists.
    """
    assert hasattr(tutorial, "LESSONS")
    assert len(tutorial.LESSONS) > 0
    # `where` is what GET /tutorial/progress/{id} returns; it carries the size.
    progress = tutorial.where("nobody-in-particular")
    assert "total" in progress, (
        "nothing serves the lesson count, so prose has nowhere better to get it")
    assert progress["total"] == len(tutorial.LESSONS)


def test_the_prose_around_the_tutorial_does_not_count_it_either():
    """The same fact, embedded somewhere further away and even easier to miss.

    `help.py` and the README both describe the walkthrough. A count written
    into either drifts on exactly the same trigger, and is further from the
    thing that would remind somebody.
    """
    for rel in ("qrme/help.py", "qrme/tutorial.py", "README.md"):
        text = (REPO / rel).read_text(encoding="utf-8").lower()
        for word in _WORD_NUMBERS:
            for noun in ("step", "lesson"):
                hit = re.search(rf"{word}[\w-]*\s+(?:written\s+)?{noun}s?\b",
                                text)
                assert not hit, f"{rel} counts the lessons: {hit.group(0)!r}"
