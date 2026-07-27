"""The README's gallery and the drawings on disk, held in step.

Every defect this file exists to catch has already happened at least once in
this repo, and none of them was caught by looking:

- a screen was renumbered and six stale SVGs kept rendering in the README,
  because nothing deletes a file the builder stopped writing;
- a screen was added and never put in the gallery, so it existed and nobody
  could see it;
- inserting one screen into a three-wide row pushed the last cell out of the
  row and the number it displaced vanished from the page entirely.

The last one is why the numeric check is here and not just the existence
check. Every reference resolved, every file was referenced, and 82 was still
gone — the row it lived in had been rewritten around it. A gallery is a
sequence, so the test reads it as one.

These assertions are cheap and they are about *files*, not about drawing, so
they run in the ordinary suite rather than behind the builder. A contributor
who adds a screen and forgets the README finds out here.
"""

import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README = os.path.join(ROOT, "README.md")
SCREENS = os.path.join(ROOT, "docs", "screens")


def _readme() -> str:
    with open(README, encoding="utf-8") as fh:
        return fh.read()


def _referenced(src: str) -> list[str]:
    """Screen filenames the README points at, in the order it points at them.

    Order is kept because the gallery is a sequence and the numeric check
    below depends on reading it as one. `<img>` and `<a href>` name the same
    file twice per cell, so duplicates are dropped while the first position of
    each is preserved.
    """
    seen: dict[str, None] = {}
    for name in re.findall(r"docs/screens/([\w\-.]+\.svg)", src):
        seen.setdefault(name, None)
    return list(seen)


def _on_disk() -> set[str]:
    return {f for f in os.listdir(SCREENS) if f.endswith(".svg")}


def test_every_referenced_screen_exists():
    """A broken image in a README is invisible to whoever wrote it — it
    renders as a small box on somebody else's machine."""
    missing = sorted(set(_referenced(_readme())) - _on_disk())
    assert not missing, ("the README points at screens that are not on disk:\n  "
                         + "\n  ".join(missing))


def test_every_screen_is_shown_somewhere():
    """The other direction, and the one that catches a shelved feature coming
    back: screen 81 was built, held, and returned, and nothing but this would
    have noticed if it had returned without a place to be seen."""
    unshown = sorted(_on_disk() - set(_referenced(_readme())))
    assert not unshown, ("screens exist that the README never shows:\n  "
                         + "\n  ".join(unshown))


def test_the_gallery_runs_in_order_and_skips_nothing():
    """The check the other two cannot make.

    Adding 81 to a full three-wide row pushed 82 out of it. Every file still
    existed and every reference still resolved — 82 was simply no longer on
    the page, in a row that read 79, 80, 81, then 83. A number that stops
    appearing is exactly what nobody re-reads a 1,800-line README to find.
    """
    numbers: list[int] = []
    for name in _referenced(_readme()):
        head = name.split("-", 1)[0]
        if head.isdigit():
            n = int(head)
            if n not in numbers:
                numbers.append(n)

    expected = list(range(1, max(numbers) + 1))
    assert sorted(numbers) == expected, (
        "the gallery skips: "
        + ", ".join(str(n) for n in expected if n not in numbers))
