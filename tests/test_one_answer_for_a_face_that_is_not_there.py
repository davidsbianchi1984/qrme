"""One picture for a profile with no face, not three.

`render()` returned `asset: None` for a portrait-less profile and left each
surface to invent a fallback. Three of them did, differently:

* initials on Home and in a Top 8,
* an abstract blue orb on the talk surface,
* the empty frame, but only for an anonymous profile.

So one profile had three faces, and the one on the conversation screen —
the surface whose whole subject is the face — made every portrait-less
person look identical to every other and read as a thing rather than as
something to fill.

    asked     does a profile with no face have something to show
    mattered  does it show the same thing everywhere

`avatars.py` had already argued this when the anonymous placeholder was
settled: *two defaults meant two things that could disagree about the same
profile, which is the shape of bug this codebase keeps finding.* That was
written about two. There were three.
"""

from __future__ import annotations

from pathlib import Path

from qrme import avatars

REPO = Path(__file__).resolve().parents[1]


def test_the_frame_that_ships_is_the_frame_that_is_served():
    """A served path pointing at no file is a broken picture on every
    surface at once, which is a worse failure than the one this replaced."""
    assert avatars.ADD_PHOTO.startswith(avatars.FIGURE_ROUTE + "/")
    name = avatars.ADD_PHOTO.rsplit("/", 1)[1]
    assert (avatars.figures_dir() / name).is_file(), avatars.ADD_PHOTO


def test_a_row_and_a_render_agree_about_a_faceless_profile():
    """`shown` is the cheap half of `render`'s decision, for list payloads
    that cannot afford a full render per row. If the two ever disagree, a
    friends list and the profile page it links to draw different things."""
    assert avatars.shown(None) == avatars.ADD_PHOTO
    assert avatars.shown("") == avatars.ADD_PHOTO
    # And a real asset passes straight through, untouched.
    assert avatars.shown("/portraits/osei.webp") == "/portraits/osei.webp"


def test_no_list_builder_hands_out_a_bare_avatar_column():
    """The defect was four payloads returning `r["avatar"]` raw, so the
    fallback became each client's problem and each client solved it
    differently. Structural, because the alternative is finding the fifth one
    in a screenshot."""
    offenders = []
    for path in sorted(REPO.glob("qrme/**/*.py")):
        if path.name in ("avatars.py", "db.py"):
            continue
        for n, line in enumerate(path.read_text().splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            if '"avatar": r["avatar"]' in line or \
               '"avatar": info["avatar"]' in line:
                offenders.append(f"{path.relative_to(REPO)}:{n}")
    assert not offenders, (
        f"{len(offenders)} payload(s) hand out the raw column — wrap them in "
        "avatars.shown() so every surface draws the same thing:\n    "
        + "\n    ".join(offenders))


def test_the_console_no_longer_draws_its_own_fallback():
    """The two shapes the console invented: an orb element, and initials
    sliced off a display name into a filled bubble. Both are gone, and this
    fails if either comes back."""
    app = REPO / "app" / "src"
    bad = []
    for path in sorted(app.rglob("*.tsx")) + sorted(app.rglob("*.ts")):
        text = path.read_text()
        for n, line in enumerate(text.splitlines(), 1):
            if "talk-orb" in line or "orbfill" in line:
                bad.append(f"{path.relative_to(REPO)}:{n}: {line.strip()}")
    assert not bad, (
        "the console is drawing its own answer for a missing face again — "
        "`render()` sends the frame, so there is nothing to fall back "
        "from:\n    " + "\n    ".join(bad))


def test_the_orb_is_gone_from_the_stylesheet_too():
    """A rule with nothing using it is the invitation to use it again."""
    css = (REPO / "app" / "src" / "styles.css").read_text()
    assert ".talk-orb" not in css
    assert ".presence-bubble.orbfill" not in css
