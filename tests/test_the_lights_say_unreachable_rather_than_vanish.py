"""The agent lights' own docstring promises "always on screen". It wasn't.

## The finding

A field report: the agent-lights pop-up — bottom-left, minimizable,
expandable — simply gone. The component was mounted, the route answered,
the CSS was intact; driving the console with a browser showed the widget
alive and well over a healthy backend.

The disappearance lives on one path: `WatchLights` fetched the face,
caught any error with "keep the last face; a blip must not blank it" —
and when the *first* fetch fails there is no last face to keep, so the
widget renders nothing, forever. A stored base address pointing at a
backend too old to have `/profiles/{id}/watch` (the same stale-backend
family as the version-mismatch banner's field report) turns that "blip"
into a permanent absence that reads as the feature being removed.

    asked     does the widget survive a fetch error
    mattered  does it survive the FIRST fetch error

## The fix this file pins

Unreachable is a state the widget shows, not one it hides in: with a
session present and no face, a failed fetch renders the minimized dot,
unlit gray, titled in the reader's language, and pressing it retries.
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
WIDGET = (REPO / "app/src/WatchLights.tsx").read_text(encoding="utf-8")
L10N = (REPO / "app/src/l10n.ts").read_text(encoding="utf-8")

LANGS = ("en", "es", "fr", "de", "pt", "it", "ja", "zh", "hi", "ar")


def test_the_widget_is_mounted_in_the_shell():
    """Ported from the sibling. Every check in this file reads the component's
    own source, so all of them keep passing on a component nothing renders —
    unmounting `<WatchLights />` from the shell would orphan the file and the
    suite would call the orphan healthy."""
    app = (REPO / "app/src/App.tsx").read_text(encoding="utf-8")
    assert "<WatchLights />" in app, (
        "the watch lights are no longer part of the shell")


def test_a_failed_first_fetch_leaves_a_dot_not_a_blank():
    """The structural claim: in the no-face branch the *only* bare exit is
    the guarded one, so the unlit dot is reachable — a branch that merely
    contains the dot below an unconditional `return null` would pass a
    presence check and still vanish (the injection that shaped this
    assertion did exactly that)."""
    m = re.search(r"if \(!face\) \{(.*?)\n  \}", WIDGET, re.S)
    assert m, "WatchLights no longer has a no-face branch to check"
    branch = m.group(1)
    assert "wl-dot-off" in branch, (
        "the no-face branch renders nothing — a first fetch that fails "
        "removes the widget from every screen, silently")
    nulls = re.findall(r"^\s*(.*return null.*)$", branch, re.M)
    assert len(nulls) == 1 and "!unreachable" in nulls[0], (
        "the no-face branch returns null on a path other than the guarded "
        "one — the unlit dot is written but unreachable:\n    "
        + "\n    ".join(nulls))


def test_the_failure_is_tracked_not_swallowed():
    assert "setUnreachable(true)" in WIDGET, (
        "the catch swallows the error again; with no face yet that is a "
        "permanent, silent absence")


def test_the_dot_retries_when_pressed():
    """A dot that only sits there is a lamp for a dead bulb. The press is
    the retry — same reload the poll would eventually do, on demand."""
    m = re.search(r"if \(!face\) \{(.*?)\n  \}", WIDGET, re.S)
    assert m and re.search(r"onClick=\{load\}", m.group(1)), (
        "the unreachable dot no longer retries on press")


def test_the_unlit_dot_has_its_own_color():
    css = (REPO / "app/src/styles.css").read_text(encoding="utf-8")
    assert ".wl-dot-off" in css, (
        "the unreachable dot has no style of its own — it would wear a "
        "live light's color while the backend is unreachable")


def test_the_title_speaks_the_readers_language():
    block = re.search(r'"lights\.unreachable":\s*\{(.*?)\n  \}', L10N, re.S)
    assert block, "lights.unreachable is not on the console's table"
    for lang in LANGS:
        assert re.search(rf"\b{lang}:", block.group(1)), (
            f"lights.unreachable has no {lang} translation")
    assert 'tr("lights.unreachable"' in WIDGET, (
        "the widget no longer draws its unreachable title from the table")
