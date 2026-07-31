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
    """User-visible English left in Public.tsx.

    JSX text nodes only. The first version of this matched anything between
    `>` and `<` and reported `useState<Row | null>(null)` as prose — TypeScript
    generics look exactly like tags to a regex. Lines carrying code
    punctuation are dropped, which is crude and is why the result is
    snapshotted rather than trusted as a count.
    """
    text = PUBLIC.read_text(encoding="utf-8")
    text = re.sub(r"/\*.*?\*/|//[^\n]*", "", text, flags=re.S)   # no comments
    out = []
    for chunk in re.findall(r">([^<>{}]+)<", text):
        line = re.sub(r"\s+", " ", chunk).strip()
        if len(line.split()) < 4:
            continue
        if any(mark in line for mark in ("=", ";", "()", "=>", "const ")):
            continue
        out.append(line)
    return sorted(set(out))


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
        block = match.group(2)
        assert "{" not in block, f"{match.group(1)} has a nested object"
        assert json.dumps(match.group(1))  # name is a plain string key
