"""A component nothing mounts is a feature nobody has.

This file exists because of a specific escape. `Avatar3D` — the 3-D head
the forge builds, with the mouth that moves to the voice — was written,
given a census row in `ui_screens.txt`, given a door in
`productmap.DOORS`, shipped in a release, and **imported by nothing**.
Every guard it passed asked whether it was *catalogued*. None asked
whether it was *drawn*.

That is the same failure `test_the_avatar_takes_the_screen.py` already
records once, in its own words: *"a component full of finished features
that nothing mounted"*. That guard fixed it for one screen by naming
Identity's deck explicitly. Naming one screen catches one escape; this
catches the shape.

    asked     is the component accounted for
    mattered  does any screen actually draw it

The rule is deliberately narrow: a component in `app/src` that no other
file imports is either dead or unmounted, and both are worth a failing
test. A file that is genuinely a leaf on purpose goes in `STANDALONE`
with the reason — a list of decisions rather than of leftovers.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "app" / "src"

#: Files that legitimately nobody imports, with why. Entry points and
#: bundler-owned files: `main.tsx` is what the page loads, and the rest
#: are configuration the toolchain reads rather than code a screen calls.
STANDALONE = {
    "main.tsx": "the console's entry point — the page loads it",
    "vite-env.d.ts": "type declarations for the bundler, imported by tsc",
}


def _components() -> list[Path]:
    return [p for p in SRC.glob("*.tsx") if p.name not in STANDALONE]


def test_every_component_is_mounted_by_something():
    """A drawing nothing calls is a drawing nobody sees."""
    everything = list(SRC.rglob("*.tsx")) + list(SRC.rglob("*.ts"))
    orphans = []
    for part in _components():
        stem = part.stem
        # Any import of this module, from anywhere but itself.
        wanted = re.compile(rf'from\s+["\'][^"\']*/{re.escape(stem)}["\']'
                            rf'|from\s+["\']\./{re.escape(stem)}["\']')
        if not any(wanted.search(other.read_text(encoding="utf-8"))
                   for other in everything if other != part):
            orphans.append(part.name)
    assert not orphans, (
        "these components are imported by nothing, so whatever they draw "
        "reaches no one:\n    " + "\n    ".join(sorted(orphans))
        + "\n  Mount it on the screen it belongs to, or add it to "
          "STANDALONE with the reason it is a leaf on purpose.")


def test_the_head_the_forge_builds_is_actually_drawn():
    """The specific escape, named — the general rule above would catch it,
    and a guard that only holds in general is one a refactor can quietly
    talk out of. The head belongs on the stage it takes over and on the
    seat that speaks it."""
    stage = (SRC / "AvatarStage.tsx").read_text(encoding="utf-8")
    inside = (SRC / "screens" / "Inside.tsx").read_text(encoding="utf-8")
    assert "<Avatar3D" in stage, (
        "the avatar stage draws a still where the forge built a head")
    # The room mounts the head through the stage rather than reaching past
    # it. It used to render `<Avatar3D>` inline beside a second copy of
    # the stage's framing controls; one stage, mounted once, is what put
    # the face and the shots that frame it in the same place.
    assert "<AvatarStage" in inside, (
        "a room's seats draw a still where the forge built a head")
    # And the mouth is driven by the voice already in the air rather than
    # a second fetch of the same speech. Once, in the stage: the room
    # asked for it separately back when it mounted its own `<Avatar3D>`
    # beside the stage's, and two readers of one playing voice is the
    # duplication that mounting the stage once removed.
    assert "nowPlaying()" in stage
