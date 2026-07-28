import pathlib
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


def test_no_screen_is_named_something_a_url_cannot_carry():
    """A screen filename becomes a URL in the README's `<img src>`.

    "Where Is It?" produced `129-where-is-it?.svg`, where the `?` starts a
    query string: the browser asks for `129-where-is-it` and draws a broken
    icon. A comma had already reached a filename the same way. Both came from
    the title being slugged by hand in two places that disagreed, so the
    builder now has one `slug()` and this is the assertion that it is used.

    Checked against the files rather than the builder, because the failure is
    a file on disk that the README cannot address.
    """
    bad = sorted(f for f in _on_disk()
                 if not re.fullmatch(r"[0-9a-z][0-9a-z\-.]*\.svg", f))
    assert not bad, ("screen files whose names are unsafe in a URL:\n  "
                     + "\n  ".join(bad))


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


# -- the README's own arithmetic -----------------------------------------------

def test_every_test_count_the_readme_claims_is_true():
    """The README says "`module.py`, N tests" in a dozen places, and five of
    them were wrong when this was written — `storage.py` claimed 23 with 38,
    `dock.py` claimed 30 with 34, and JIM-mini's three were all short.

    A number in prose is a duplicate of something the repository already
    knows, and duplicates drift the moment somebody adds a test. Nothing fails
    when a file grows a function, so nothing did — for several releases, in a
    document whose whole pitch is that its claims are checked.

    The counting is deliberately the dumb kind: `def test_` at column zero, in
    every file matching the module's name. A cleverer measure would be a
    second thing to keep in step.
    """
    import re

    root = pathlib.Path(__file__).resolve().parent.parent
    readme = (root / "README.md").read_text()
    claims = re.findall(
        r"`((?:qrme|jim)/[\w/]+\.py)`[^\n]{0,40}?(\d+) tests", readme)
    assert claims, "no test-count claims found — has the README format changed?"
    for module, claimed in claims:
        stem = pathlib.Path(module).stem
        files = sorted(root.rglob(f"test_{stem}*.py"))
        assert files, f"README cites {module} but no test_{stem}*.py exists"
        actual = sum(len(re.findall(r"^def test_", f.read_text(), re.M))
                     for f in files)
        assert actual == int(claimed), (
            f"README says {module} has {claimed} tests; "
            f"{', '.join(f.name for f in files)} hold {actual}")


def test_the_desktop_app_version_matches_the_api():
    """Three releases shipped installers labelled 0.3.3 from 0.4.x tags.

    `app/package.json` carries its own version and no cut ever bumped it — the
    0.4.0 and 0.4.1 releases both attached installers named 0.3.3, built from
    the right tag but stamped with the stale number. The filename and the
    About box are cosmetic; the auto-updater is not, because it compares
    package versions and will tell an installed app there is nothing newer.

    Same disease as the stale test counts: a duplicated number with nothing to
    fail when the other copy moves. The versions must move together now.
    """
    import json
    import re

    root = pathlib.Path(__file__).resolve()
    while not (root / "app" / "package.json").exists():
        root = root.parent
    api_src = (root / "qrme/api.py").read_text()
    lock = json.loads((root / "app" / "package-lock.json").read_text())
    # The releasing checklist names five places a cut must move; each has
    # drifted at least once (pyproject sat at 0.4.0 through the 0.4.1 cut,
    # the lockfile roots at 0.3.3 through two). Check all five against each
    # other, not one pair.
    versions = {
        "qrme/api.py": re.search(r'version="([\d.]+)"', api_src).group(1),
        "app/package.json":
            json.loads((root / "app" / "package.json").read_text())["version"],
        "app/package-lock.json (root)": lock["version"],
        "app/package-lock.json (packages.'')":
            lock["packages"][""]["version"],
        "pyproject.toml": re.search(
            r'^version = "([\d.]+)"',
            (root / "pyproject.toml").read_text(), re.M).group(1),
    }
    assert len(set(versions.values())) == 1, (
        f"version strings disagree: {versions} — the installer filenames and "
        "the auto-updater follow app/package.json, the release tag follows "
        "qrme/api.py, and pip follows pyproject.toml")
