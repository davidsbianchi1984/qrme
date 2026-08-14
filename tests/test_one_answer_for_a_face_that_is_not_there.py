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

There were five. Counting the console's three stopped at the surfaces a
`.tsx` grep reaches, and two more were drawing their own answer outside it:

* the beacon landing page, which a stranger meets before any client does,
  kept an `if art["asset"]` branch that fell to initials;
* the in-camera overlay, which was *handed* initials by `/b/{id}/card` — so
  iOS drew a monogram while the image loaded, and Android drew one always,
  never fetching the portrait at all.

Android is the sharper half. It was not a fallback that fired rarely: the
overlay had no portrait path in it, so scanning one sticker on a phone and
on a laptop showed two different things every time, and on a profile whose
name is hidden it showed initials of the hidden name.
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


def test_no_server_surface_draws_initials():
    """The landing page and the overlay card, which the `.tsx` sweep above
    cannot see. `landing.py` built a monogram from the display name; the card
    handed one to every native overlay. Both are the same defect as the orb,
    one layer further out."""
    bad = []
    for name in ("landing.py", "routers/summon.py"):
        path = REPO / "qrme" / name
        for n, line in enumerate(path.read_text().splitlines(), 1):
            if line.strip().startswith("#"):
                continue
            if "initials" in line:
                bad.append(f"qrme/{name}:{n}: {line.strip()}")
    assert not bad, (
        "a monogram of the display name is being drawn or shipped — "
        "`render()` sends the frame, and on a profile with a hidden name a "
        "monogram is the hidden name:\n    " + "\n    ".join(bad))


def test_the_phones_draw_the_portrait_they_are_sent():
    """Android's overlay never read `portrait` at all: it drew initials in
    every case, so one sticker looked like two different profiles depending
    on what scanned it. This fails if either shell goes back to inventing a
    face, and if Android stops drawing the one it is given."""
    native = REPO / "native"
    ios = (native / "ios/Sources/Views/BeaconScannerView.swift").read_text()
    android = (native / "android/app/src/main/java/app/qrme/studio"
                        "/ui/BeaconScanner.kt").read_text()

    for what, text in (("iOS", ios), ("Android", android)):
        offenders = [f"{what}:{n}: {ln.strip()}"
                     for n, ln in enumerate(text.splitlines(), 1)
                     if "initials" in ln and not ln.strip().startswith(
                         ("//", "*", "/*"))]
        assert not offenders, "\n    ".join(offenders)

    assert "AsyncImage" in android and "shown.portrait" in android, (
        "the Android overlay is not drawing the portrait the card carries")
