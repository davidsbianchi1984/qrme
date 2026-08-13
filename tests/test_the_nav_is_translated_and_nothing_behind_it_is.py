"""Forty-six translated labels, forty-six English screens behind them.

## The finding

`app/src/l10n.ts` carries 128 keys in ten languages. Forty-six of them are
`nav.*` — one per entry in `App.tsx`'s sidebar — and `App.tsx` builds each
label with ``t(`nav.${n.id}`, lang)``, so the navigation genuinely answers in
the profile's language.

Every one of those labels opens a screen. All forty-six screens are English,
end to end: 1577 distinct strings, none of them reachable by any translation
this repo ships.

    asked     is the chrome localized
    mattered  is anything behind the chrome localized

Three rounds of language audit ran before this one and each widened correctly
*inside* the scope l10n.ts declares in its own first line — "chrome
localization for the desktop console". `Public.tsx`, then `Onboarding.tsx`,
then the native shells' `L10n` tables. Every one of those rounds ended with a
passing guard and a truthful record. None of them asked what was on the other
side of the forty-six translated words, because the sentence at the top of the
file read as a boundary rather than as the thing to question.

## Why this is worse than a console with no translations at all

JIM's console had no `l10n.ts` when the equivalent round found it. That is a
gap; this is a promise. A uniformly English console tells a Spanish reader the
truth on the first screen they see. This one puts *Mercado*, *Amigos* and
*Ajustes* in the sidebar — the app apparently answering in their language —
and then hands them English the moment they click. The part that was localized
is exactly the part that advertises localization.

The gated reader also makes it sharper than the accountless case. They have a
profile, the profile has a language, and the backend already honours it on
every answer it generates. So the model replies in Portuguese inside a frame
that cannot.

## What this file is, and is not

A measurement, ratcheted, in `console_untranslated.txt`. It does not claim the
console is localized; it claims somebody knows it is not, and by how much —
the same ratchet `public_untranslated.txt` and `native_untranslated.txt` use.

The one thing it does structurally is `test_the_two_records_partition_the_console`
below, which is aimed at this defect's actual mechanism rather than at its
symptom. Both language records now derive their screen sets from the directory
and must together cover it exactly. A screen cannot be added to this console
without landing in one of the two counts, and neither file can be narrowed
without the other's check failing. That is the part that would have caught this
three rounds ago.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()
SRC = REPO / "app" / "src"
SCREENS = SRC / "screens"
SNAPSHOT = Path(__file__).resolve().parent / "console_untranslated.txt"

#: The two screens `App.tsx` renders before a profile exists. They are
#: measured by `test_the_stranger_has_a_language_too.py` against
#: `public_untranslated.txt`, and their argument is a different one: their
#: reader has no stored language to honour, so English there is a guess rather
#: than a shortfall.
#:
#: Named here rather than in a list of gated screens, deliberately. A new
#: screen added to this console must default to *being counted*; the only way
#: out of the count is to be one of these two, by name.
PRE_SESSION = ("Public.tsx", "Onboarding.tsx")


def _gated() -> list[str]:
    """Every screen behind the sign-in, from the directory rather than a list.

    This is the whole structural point. A hard-coded tuple is how
    `public_untranslated.txt` measured one screen for three releases while a
    second sat next to it on disk.
    """
    return sorted(p.name for p in SCREENS.glob("*.tsx")
                  if p.name not in PRE_SESSION)


def _prose() -> list[str]:
    """User-visible English on the gated screens, from TypeScript's parser.

    Not a regex. Three separate regexes over this same source each hid real
    text — the lesson is written out at length in
    `test_the_stranger_has_a_language_too.py`; this borrows the extractor.
    """
    gated = _gated()
    proc = subprocess.run(
        ["node", "scripts/jsx-text.mjs"] + [f"src/screens/{s}" for s in gated],
        cwd=REPO / "app", capture_output=True, text=True)
    assert proc.returncode == 0, (
        "the JSX text extractor failed, so this check would report a "
        f"comfortable zero:\n{proc.stderr}")
    found = json.loads(proc.stdout)
    # Empty strings are dropped, and three of those come from `alt=""` on
    # decorative avatars in Wall.tsx — the correct accessibility marking
    # rather than a missing translation, since an empty alt tells a screen
    # reader to skip the image.
    #
    # **Strings with no letter are dropped too, reversing this file's earlier
    # rule.** It used to say: *"Whitespace-bearing strings are kept: `" · "`
    # is a separator somebody reads."* That was a deliberate decision and it
    # conflated two things. A separator is *rendered*; it is not *unreadable
    # to a non-English speaker*. There is no Portuguese for `·`, and none for
    # `⚠`, `%`, `.` or `—` either.
    #
    #     asked     is this string rendered to somebody
    #     mattered  is this string one a non-English reader cannot read
    #
    # 117 of the rows in the record were punctuation, so the count this file
    # exists to state honestly was overstated by that much. The sibling
    # product hit the identical thing one release earlier with
    # `"\(dim): \(n)%"` in the shells, and this is the same correction.
    return sorted({f"{s.removesuffix('.tsx')}: {text}"
                   for s in gated for text in found[f"src/screens/{s}"]
                   if re.search(r"[A-Za-z]", text)})


def _recorded() -> set[str]:
    return {line.strip() for line in
            SNAPSHOT.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")}


def test_the_english_behind_the_nav_is_written_down():
    """Both directions, so the record cannot rot into a list of things that
    were true once — and so translating a screen shows up as progress rather
    than as a mismatch nobody explains."""
    actual, recorded = set(_prose()), _recorded()
    appeared = sorted(actual - recorded)
    resolved = sorted(recorded - actual)
    problems = []
    if appeared:
        problems.append(
            f"{len(appeared)} English string(s) on the gated console that "
            "nobody has decided about:\n    "
            + "\n    ".join(s[:90] for s in appeared[:40])
            + "\n  Translate it, or add it here — but adding is ratcheted.")
    if resolved:
        problems.append(
            f"{len(resolved)} recorded string(s) are gone — strike them from "
            f"{SNAPSHOT.name}:\n    "
            + "\n    ".join(s[:90] for s in resolved[:40]))
    assert not problems, "\n\n".join(problems)


def test_the_backlog_only_shrinks():
    ceiling = int(re.search(r"# ceiling: (\d+)",
                            SNAPSHOT.read_text(encoding="utf-8")).group(1))
    assert len(_recorded()) <= ceiling, (
        f"{len(_recorded())} untranslated strings, above the {ceiling} this "
        "guard started at")


def test_the_two_records_partition_the_console():
    """The structural half, and the only part of this file that is a fix.

    Everything else here records a shortfall. This asserts that the two
    language records cover `screens/` exactly — no screen in both, none in
    neither — with both sets derived from the directory.

        asked     is the surface this file names localized
        mattered  is every surface named by some file

    A screen added to this console tomorrow lands in a count whether or not
    anybody remembers these files exist. That is what was missing when
    `public_untranslated.txt` measured one screen out of forty-eight for three
    releases and reported the pre-session surface clean.
    """
    import importlib.util

    sibling = Path(__file__).resolve().parent / "test_the_stranger_has_a_language_too.py"
    spec = importlib.util.spec_from_file_location("_stranger_language", sibling)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    public_set = module.PRE_SESSION

    on_disk = {p.name for p in SCREENS.glob("*.tsx")}
    public = {s.split("/")[-1] for s in public_set}
    gated = set(_gated())

    both = sorted(public & gated)
    neither = sorted(on_disk - public - gated)
    stale = sorted((public | gated) - on_disk)
    assert not both, (
        f"{both} are measured by both language records — a string translated "
        "on one will read as an unexplained disappearance on the other")
    assert not neither, (
        f"{neither} are rendered by this console and measured by neither "
        "language record. That is exactly the state this file was written "
        "about: a screen whose English nobody has counted.")
    assert not stale, (
        f"{stale} are named by a language record and no longer exist")


def test_the_nav_really_is_translated():
    """The premise the finding rests on.

    If the `nav.*` keys were themselves absent, this would be recording a
    console that is uniformly English — a gap, and a milder one. The finding
    is that the sidebar answers in the reader's language and nothing behind it
    does, so the sidebar's translations are checked here rather than assumed.
    """
    text = (SRC / "l10n.ts").read_text(encoding="utf-8")
    union = re.search(r"export type Lang =([^;]+);", text).group(1)
    langs = re.findall(r'"(\w+)"', union)
    assert len(langs) == 10, f"{len(langs)} languages, not ten: {langs}"

    nav = dict(re.findall(r'"nav\.([\w.]+)":\s*\{(.*?)\n  \},', text, re.S))
    assert len(nav) >= 40, (
        f"only {len(nav)} nav keys found — the pattern has stopped matching, "
        "so this check would pass on almost nothing")
    gaps = {k: [c for c in langs if c not in set(re.findall(r"(\w+):", v))]
            for k, v in nav.items()}
    gaps = {k: v for k, v in gaps.items() if v}
    assert not gaps, (
        "these nav labels are missing languages:\n    "
        + "\n    ".join(f"{k}: {', '.join(v)}" for k, v in sorted(gaps.items())))

    app = (SRC / "App.tsx").read_text(encoding="utf-8")
    assert "t(`nav.${n.id}`" in app, (
        "App.tsx no longer builds its labels from the nav table — the sidebar "
        "has gone back to hard-coded English, which makes this file's finding "
        "the wrong one rather than a fixed one")


def test_every_translated_label_opens_a_measured_screen():
    """Each `nav.*` key names a tab; each tab renders a screen; every one of
    those screens is in the count.

    Written the long way on purpose. Comparing the two totals would pass on
    forty-six of each that happened not to be the same forty-six.
    """
    app = (SRC / "App.tsx").read_text(encoding="utf-8")
    nav_ids = set(re.findall(r'\{\s*id:\s*"([\w]+)"', app))
    assert len(nav_ids) >= 40, (
        f"only {len(nav_ids)} nav entries parsed out of App.tsx — the pattern "
        "has stopped matching")
    rendered = dict(re.findall(r'tab === "(\w+)" && <(\w+)', app))
    measured = {s.removesuffix(".tsx") for s in _gated()}

    unrendered = sorted(i for i in nav_ids if i not in rendered)
    assert not unrendered, (
        f"{unrendered} are labelled in the sidebar and render nothing")
    unmeasured = sorted(rendered[i] for i in nav_ids
                        if rendered[i] not in measured)
    assert not unmeasured, (
        f"{unmeasured} are opened by a translated label and counted by no "
        "language record — the exact combination this file is named for")


def test_the_extractor_can_still_see():
    """A guard on the guard, against a fixture whose answer is known.

    Everything above trusts a subprocess. If node disappears or the parser
    stops recognising `JsxText`, `_prose()` returns an empty list and 1577
    strings look translated. The quietest failures in this audit were all a
    pattern that stopped matching.
    """
    proc = subprocess.run(
        ["node", "scripts/jsx-text.mjs", "scripts/jsx-text.fixture.tsx"],
        cwd=REPO / "app", capture_output=True, text=True)
    assert proc.returncode == 0, f"the extractor will not run:\n{proc.stderr}"
    found = json.loads(proc.stdout)["scripts/jsx-text.fixture.tsx"]
    assert found == [
        "A heading",
        "A paragraph that runs across several lines of source and is "
        "nonetheless one sentence to whoever reads it.",
        "Wrapped around",
        "an interpolated value.",
        # Chosen at render time and laid out as text all the same: the shape
        # a field report caught the PDI vault light hiding two English words
        # in, and the shape this extractor could not see until it did.
        "a chosen branch",
        "the other branch",
        "a guarded phrase",
        "a placeholder",
        "a title",
        "an aria label",
        "A button",
    ], f"the extractor no longer reads the fixture as documented:\n{found}"
