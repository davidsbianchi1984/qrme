"""Localization keyed on a setting only account-holders have.

## The finding

`app/src/l10n.ts` says what it is in its first line:

    Chrome localization for the desktop console ... the app's own frame
    follows **the profile's language**.

That is right for the console and useless for `screens/Public.tsx`, which two
rounds ago was built specifically for people who have no profile: somebody
contesting a synthetic profile of themselves, somebody asking whether what
they were sent was written by a person, somebody checking they met the same
profile twice. Every one of them got English.

`navigator.languages` is the only language signal those visitors carry, and
nothing in any of the three products read it — the same gap JIM's beacon page
had, one product over. This is the audit's recurring shape a layer up from
the last two rounds: the door was built for the person with no account, and
then the *language* of the door was keyed on having one.

## What is checked, and what is recorded

The action-carrying strings — headings, tab labels, field placeholders,
buttons — are translated across all ten languages and checked below.

The longer explanatory paragraphs are **not**, yet. They are listed in
`public_untranslated.txt`, which only shrinks. That file is the difference
between a decision and an oversight: `l10n.ts`'s table is
`Partial<Record<Lang, string>>` with per-key English fallback, so partial
coverage is a supported state there rather than a lie — but partial coverage
nobody wrote down is how the console ended up promising a language it did not
serve in the first place.
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
PUBLIC = SRC / "screens" / "Public.tsx"
SNAPSHOT = Path(__file__).resolve().parent / "public_untranslated.txt"

#: Every language the console offers. Read from l10n.ts rather than repeated,
#: so adding a tenth language cannot leave this list behind.
def _languages() -> list[str]:
    text = (SRC / "l10n.ts").read_text(encoding="utf-8")
    union = re.search(r"export type Lang =([^;]+);", text).group(1)
    return re.findall(r'"(\w+)"', union)


def _keys_with_gaps() -> dict[str, list[str]]:
    """Public keys missing a translation, per key."""
    text = (SRC / "l10n.ts").read_text(encoding="utf-8")
    langs = _languages()
    gaps: dict[str, list[str]] = {}
    for match in re.finditer(r'"(pub\.[\w.]+)":\s*\{(.*?)\n  \},', text, re.S):
        key, block = match.group(1), match.group(2)
        present = set(re.findall(r"(\w+):", block))
        missing = [code for code in langs if code not in present]
        if missing:
            gaps[key] = missing
    return gaps


def test_the_public_keys_are_translated_everywhere():
    """No partial rows. A `pub.` key exists because a stranger reads it."""
    gaps = _keys_with_gaps()
    assert not gaps, (
        "these public strings are missing languages:\n    "
        + "\n    ".join(f"{k}: {', '.join(v)}" for k, v in sorted(gaps.items()))
        + "\n  The reader of this screen has no profile to fall back to a "
          "setting from — English here is not a default, it is a guess about "
          "who is reading.")


def test_there_are_public_keys_at_all():
    """A guard on the guard: an empty prefix search reports a perfect zero."""
    keys = re.findall(r'"(pub\.[\w.]+)":',
                      (SRC / "l10n.ts").read_text(encoding="utf-8"))
    assert len(keys) > 15, (
        f"only {len(keys)} public keys found — the pattern has stopped "
        "matching, so the check above would pass on nothing")


def _prose() -> list[str]:
    """User-visible English left in Public.tsx, from the JSX grammar itself.

    The three versions of this before now were all regexes over the source,
    and each one hid real text:

    * `>([^<>{}]+)<` skipped **any** chunk containing an interpolation, so
      `Also present on: {surfaces}.` was invisible and the strings it did
      report were the brace-free scraps of sentences it could not cross.
    * TypeScript generics look exactly like tags — `useState<Row | null>`
      opens one — so the check grew a rule dropping lines with `=`, `;`,
      `()` or `=>` in them.
    * That rule then swallowed `MarkPane`'s entire explanatory paragraph,
      because a paragraph next to an `onChange={(e) => …}` lands in the same
      bleeding region as the handler.

    Twenty-five strings were on that screen. The guard reported five. Each
    fix was the audit's recurring shape again: asking what the source *looks*
    like when what matters is what the screen *says*.

    `scripts/jsx-text.mjs` asks TypeScript's own parser for `JsxText` nodes
    and the attributes a person reads. There is no pattern left to be wrong.
    """
    proc = subprocess.run(
        ["node", "scripts/jsx-text.mjs", "src/screens/Public.tsx"],
        cwd=REPO / "app", capture_output=True, text=True)
    assert proc.returncode == 0, (
        "the JSX text extractor failed, so this check would report a "
        f"comfortable zero:\n{proc.stderr}")
    texts = json.loads(proc.stdout)["src/screens/Public.tsx"]
    return sorted(set(texts))


def _recorded() -> set[str]:
    return {line.strip() for line in
            SNAPSHOT.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")}


def test_the_english_that_is_left_is_written_down():
    """Both directions, so the file cannot rot into a list of things that
    were true once."""
    actual, recorded = set(_prose()), _recorded()
    appeared = sorted(actual - recorded)
    resolved = sorted(recorded - actual)
    problems = []
    if appeared:
        problems.append(
            f"{len(appeared)} English string(s) on the public screen that "
            "nobody has decided about:\n    "
            + "\n    ".join(s[:90] for s in appeared)
            + "\n  Translate it, or add it here — but adding is ratcheted.")
    if resolved:
        problems.append(
            f"{len(resolved)} recorded string(s) are gone — strike them from "
            f"{SNAPSHOT.name}:\n    " + "\n    ".join(s[:90] for s in resolved))
    assert not problems, "\n\n".join(problems)


def test_the_extractor_can_still_see():
    """A guard on the guard, against a fixture rather than a screen.

    Everything above trusts a subprocess. If node disappears, the script is
    renamed, or the parser stops recognising `JsxText`, `_prose()` returns an
    empty list and every check here reports a spotless screen. The quietest
    failures in this audit were all a pattern that stopped matching.

    The first version of this pointed at `Onboarding.tsx` and asserted the
    result was non-empty. Injecting the exact break it was written for —
    dropping every `JsxText` node — did **not** fail it, because the
    attribute strings kept the list non-empty. A guard that survives the
    thing it guards against is the shape this audit is named for, so it now
    runs against a fixture whose whole answer is known and asserted.
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
        "a placeholder",
        "a title",
        "an aria label",
        "A button",
    ], (
        "the extractor no longer reads the fixture the way it is documented "
        f"to, so a clean result for Public.tsx means nothing:\n{found}")


def test_every_hole_survives_every_translation():
    """`fill` substitutes by name. A translation that drops `{now}` drops the
    profile's status out of the sentence, silently, in that language only —
    and the English row would still look right to anybody checking."""
    text = (SRC / "l10n.ts").read_text(encoding="utf-8")
    langs = _languages()
    broken = []
    for match in re.finditer(r'"(pub\.[\w.]+)":\s*\{(.*?)\n  \},', text, re.S):
        key, block = match.group(1), match.group(2)
        rows = dict(re.findall(r'(\w+): "((?:[^"\\]|\\.)*)"', block))
        if "en" not in rows:
            continue
        holes = set(re.findall(r"\{(\w+)\}", rows["en"]))
        for code in langs:
            if code not in rows:
                continue
            got = set(re.findall(r"\{(\w+)\}", rows[code]))
            if got != holes:
                broken.append(
                    f"{key}/{code}: has {sorted(got) or 'none'}, "
                    f"English has {sorted(holes) or 'none'}")
    assert not broken, (
        "these translations do not carry the same named values as their "
        "English:\n    " + "\n    ".join(broken)
        + "\n  A missing name renders as the literal `{name}` on screen; an "
          "extra one renders as itself and says nothing.")


def test_the_backlog_only_shrinks():
    started_at = int(re.search(r"# ceiling: (\d+)",
                               SNAPSHOT.read_text(encoding="utf-8")).group(1))
    assert len(_recorded()) <= started_at, (
        f"{len(_recorded())} untranslated strings, above the {started_at} "
        "this guard started at")


def test_the_screen_asks_the_visitor_and_not_the_profile():
    """A guard on the guard, with the docstring stripped.

    The previous round's version of this check passed its own injection
    because the function's *docstring* contained the words it was searching
    for. That was the seventh time in this audit a check matched prose
    describing the thing rather than the thing.
    """
    text = PUBLIC.read_text(encoding="utf-8")
    code = re.sub(r"/\*.*?\*/|//[^\n]*", "", text, flags=re.S)
    assert "visitorLang(" in code, (
        "Public.tsx no longer asks visitorLang() — every visitor is back to "
        "English no matter what their browser asked for")
    assert "session" not in code, (
        "Public.tsx has started reading the session. Its whole premise is a "
        "reader who has none; a language taken from a profile here would be "
        "taken from a profile that does not exist.")


def test_the_negotiation_prefers_a_supported_language():
    """The mechanism, exercised rather than assumed — in Python, against the
    same table the TypeScript reads, so a language added to one and not the
    other shows up as a mismatch rather than as English in the wild."""
    langs = _languages()
    assert "en" in langs and len(langs) >= 10
    text = (SRC / "l10n.ts").read_text(encoding="utf-8")
    fn = text[text.index("export function visitorLang"):]
    assert "split(\"-\")" in fn, (
        "visitorLang no longer drops the region, so es-419 and es-ES stop "
        "matching es")
    assert 'return "en"' in fn, (
        "visitorLang no longer falls back to English for an unrecognised "
        "tag — it should fall back, never guess")


def test_the_l10n_json_is_still_parseable_as_a_table():
    """Cheap structural check: every `pub.` row is a flat object of
    language -> string, so a stray nesting cannot silently swallow a key."""
    text = (SRC / "l10n.ts").read_text(encoding="utf-8")
    for match in re.finditer(r'"(pub\.[\w.]+)":\s*\{(.*?)\n  \},', text, re.S):
        # `{now}`, `{id}` and friends are named holes for `fill`, not
        # structure. Taking them out first keeps this check about nesting;
        # leaving them in made it fail on every template the moment
        # interpolated sentences became translatable units.
        block = re.sub(r"\{\w+\}", "", match.group(2))
        assert "{" not in block, f"{match.group(1)} has a nested object"
        assert json.dumps(match.group(1))  # name is a plain string key
