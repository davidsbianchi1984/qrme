"""A surface the user can see must have a drawing, or be admitted not to.

`test_docs_gallery.py` checks screens against the README in both directions —
a reference with no file, a file with no reference, a gap in the numbering.
All of it starts from the screens. None of it asks the opposite question:
*does this surface have a screen at all?* So a feature can ship with nothing
drawn, nothing taught, and nothing for the in-app helper to point at, and the
suite stays green.

That is not hypothetical. It has happened three times. Voice cloning, the
recoverable watermark and the chat role picker each shipped with no screen and
stayed that way for two versions, needing a dedicated catch-up round. Then the
error-reporting card and its first-run notice went out in 0.19.0 exactly the
same way — while the release notes described the feature at length.

The shape of the flaw is the one this suite has found twice elsewhere: a guard
that only walks the relation in the direction where the answers already exist.
The doorless audit was the same (a route with no client door), and so was the
redaction check that read a shrinking snapshot and would have gone vacuous the
day it emptied.

`ui_screens.txt` is the missing direction, and the test that matters is the
first one below: a component nobody has classified fails, immediately, in the
round that introduces it.
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
# Beside this file rather than under a named `tests/`: the suite lives at
# `tests/` in one repo and `{pkg}/tests/` in the other two, exactly as
# clientpaths.py and the redaction guard already have to account for.
MANIFEST = Path(__file__).resolve().parent / "ui_screens.txt"
SRC = REPO / "app" / "src"

# Top-level .tsx files that are not user-facing surfaces. Named individually
# rather than pattern-matched, so adding one is a decision somebody makes here
# rather than a filename that quietly slips past.
NOT_A_SURFACE = {
    "main",         # the entry point; renders App and nothing of its own
    "App",          # the frame — nav and routing, drawn as part of every screen
    "store",        # a context provider, no markup
    "api",          # not a component at all
    "l10n",         # not a component at all
    "Help",         # the help box, a tab on the edge dock over every screen
    "WatchLights",  # the agent lights, a tab on the dock; its own gallery lives in the watch faces
    # The edge dock itself: the stack the three tabs above stand in, on the
    # right edge of every screen, movable up and down. Chrome by the same
    # reasoning as the version guard — and photographed open, with the
    # agent lights' face beside its tab, at screen 211 in the gallery.
    "EdgeDock",
    "VersionGuard", # a failure banner, deliberately not part of the tour
    "AgentTalk",    # the agent conversation, drawn inside Agent and Studio
    # The walk-along strip: a bar pinned to the bottom of the viewport while
    # a conversation is being carried, over every screen and never somewhere
    # anybody navigates to. Chrome by the same reasoning as the version
    # guard above, and — like the task window — not `undrawn`, which is for
    # a surface that ought to have a drawing and has not got one yet.
    #
    # What makes it unlike the other chrome is that it holds a live
    # microphone, and that is exactly the thing a drawing would not have
    # held it to. The terms are in
    # `test_a_conversation_you_can_take_with_you.py` instead: it is only
    # ever started by a press, it says which of listening, answering and
    # stopped it is, ending it is its first control, and being put away
    # closes it and says so.
    "WalkAlong",
    # The loudness rail: the dial-down for spoken audio, fixed to the right
    # edge over every screen since it left the Voice card for the shell.
    # Chrome by the same reasoning as the corner counter above — and unlike
    # the walk-along strip it holds no microphone: it is play-only, and the
    # only thing it changes is the volume of the piece already in the ear
    # (spoken.ts is the one place that applies it). While it lived inside
    # Voice.tsx it was covered by screen 147; moving files did not make it
    # a destination.
    "LoudnessRail",
    # The crash boundary. It draws a card, and the card is a failure
    # notice — the same category as the version guard above, and for the
    # same reason it is not `undrawn`: a drawing of it would be a picture
    # of something going wrong, which is not a place anybody navigates to
    # and not a thing the tour is for. What it is held to instead lives in
    # `test_a_screen_that_falls_over_does_not_take_the_app.py`: the rest
    # of the console keeps working, the notice says so, and the failure is
    # posted to the problem log rather than left as somebody's memory of a
    # white page.
    "Boundary",
}


def _surfaces() -> set[str]:
    """Every component a person can look at."""
    found = {p.stem for p in (SRC / "screens").glob("*.tsx")}
    found |= {p.stem for p in SRC.glob("*.tsx") if p.stem not in NOT_A_SURFACE}
    return found


def _manifest() -> dict[str, str]:
    rows = {}
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        line = line.split("#")[0].strip()
        if not line:
            continue
        name, _, status = line.partition(" ")
        rows[name.strip()] = status.strip()
    return rows


def test_every_surface_is_accounted_for():
    """The one that would have caught 0.19.0.

    A component nobody has classified is a component nobody has decided about.
    It fails here rather than being noticed two versions later.
    """
    listed, actual = set(_manifest()), _surfaces()
    unlisted = sorted(actual - listed)
    assert not unlisted, (
        f"these surfaces are in the console and not in ui_screens.txt: "
        f"{unlisted}\nGive each one a screen number, or the word 'undrawn' if "
        "it genuinely has no drawing yet — but note that 'undrawn' is "
        "ratcheted, so adding one there fails the next test until the backlog "
        "is paid down elsewhere. That friction is deliberate."
    )


def test_the_manifest_has_not_gone_stale():
    """The other direction: a component that was deleted or renamed leaves an
    entry behind, and a manifest full of ghosts is one nobody trusts."""
    listed, actual = set(_manifest()), _surfaces()
    ghosts = sorted(listed - actual)
    assert not ghosts, (
        f"ui_screens.txt names surfaces that no longer exist: {ghosts}")


def test_every_declared_screen_exists():
    """A mapping that points at nothing is worse than no mapping, because it
    reads as a promise that the surface was drawn."""
    # Photographs count, and increasingly they are the only thing that
    # should: the drawings in this folder were mockups presented as the
    # product, and the owner's correction was blunt — "they never
    # rendered that way, only actual snapshots of what the application
    # looks like". `tools/shoot_screens.py` runs the real console and
    # photographs it; a `.png` here is one of those, and it satisfies
    # this check exactly as a drawing did.
    on_disk = {int(m.group(1))
               for pattern in ("*.svg", "*.png")
               for p in (REPO / "docs" / "screens").glob(pattern)
               if (m := re.match(r"(\d+)-", p.name))}
    broken = {}
    for name, status in _manifest().items():
        if status in ("undrawn", "unaudited"):
            continue
        missing = [n for n in status.split(",") if int(n) not in on_disk]
        if missing:
            broken[name] = missing
    assert not broken, f"these entries name screens that do not exist: {broken}"


def _ceilings() -> dict[str, int]:
    """The ratchet's high-water marks, declared by each repo's own manifest.

    Not hardcoded here: this file is byte-identical in three repositories with
    different backlogs, and a single number would be the largest of the three
    — leaving the other two free to grow into the slack, which is the opposite
    of a ratchet.
    """
    text = MANIFEST.read_text(encoding="utf-8")
    match = re.search(r"^#\s*ceiling:\s*undrawn=(\d+)\s+unaudited=(\d+)\s*$",
                      text, re.M)
    assert match, ("ui_screens.txt has no `# ceiling:` line — without one "
                   "nothing bounds the backlog and this whole file is "
                   "decoration")
    return {"undrawn": int(match.group(1)), "unaudited": int(match.group(2))}


def test_the_undrawn_backlog_does_not_grow():
    """The ratchet, and the reason the first test has teeth.

    Without this, classifying a new surface as `undrawn` would silence the
    first test while changing nothing. With it, shipping a surface without a
    drawing costs something — you either draw it, or you draw something else
    first and lower the ceiling.

    Raising the ceiling is possible, deliberately: it is one line in a diff
    that says plainly that the backlog grew, which is the conversation worth
    having rather than one a test can win on its own.
    """
    ceilings = _ceilings()
    for status, limit in ceilings.items():
        count = sum(1 for v in _manifest().values() if v == status)
        assert count <= limit, (
            f"{count} surfaces are '{status}', above the ceiling of {limit} "
            f"declared in ui_screens.txt. Draw one, or raise the ceiling and "
            "say why.")


def test_the_ceiling_is_not_left_slack_after_the_backlog_falls():
    """A ceiling that stays high after the backlog drops is a ratchet that
    stopped ratcheting — it quietly re-opens room to grow back."""
    ceilings = _ceilings()
    for status, limit in ceilings.items():
        count = sum(1 for v in _manifest().values() if v == status)
        assert limit == count, (
            f"the '{status}' ceiling is {limit} but only {count} remain — "
            f"lower it to {count} so the ground gained is kept")


def test_the_statuses_are_ones_this_file_defines():
    """A typo'd status would otherwise read as 'not undrawn' and pass."""
    allowed = re.compile(r"^(undrawn|unaudited|\d+(,\d+)*)$")
    bad = {n: s for n, s in _manifest().items() if not allowed.match(s)}
    assert not bad, (
        f"unrecognised statuses in ui_screens.txt: {bad} — expected a "
        "comma-separated list of screen numbers, 'undrawn', or 'unaudited'")
