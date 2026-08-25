"""Two guards the shells did not have, from the round that localized their
first screen.

## The ten-language check only ever looked at one prefix

`test_the_strangers_language_on_a_phone.py` has checked since the
accountless-screen round that every row is in every language. It checks it of
`pub.*` — the rows that round ported — because that was the set that existed.
The shells' tables now carry `nw.*` and `ns.*` too, and a row with three
languages passes any check that only asks whether the key is there.

The console learned this at 0.45.8, when an injected defect fired nothing
because the only completeness check in the repository was over `nav.*`. This
is the same finding on the other side of the wire, so the check is written
the way the console's was: **every row**, not every row of one prefix.

## A call in an argument list does not parse

`ProblemReportingCard()` sat between two arguments of a `Text(…)` call in
`Screens.kt`:

    Text(L10n.t("tab.settings", vm.language), color = Qrme.Txt, fontSize = 22.sp,
    ProblemReportingCard()
        fontWeight = FontWeight.Bold)

Kotlin does not accept that, so the Android shell did not compile — and the
parentheses balance, so nothing that counts brackets would have said so. It
was found by reading the file while localizing it, which is not a method.

    asked     do the shells' strings come from the table
    mattered  does the shell build

There is no Kotlin compiler in this suite and adding one is a different
round's work. What is cheap is the shape: two arguments with nothing between
them. A `{` reopens statement context — `vm.call({ … oauthState = st … })` is
ordinary code and was the first draft's two false positives — so the check
only fires when the enclosing bracket is a parenthesis.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from . import ratchets


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()

LANGS = ("en", "es", "fr", "de", "pt", "it", "ja", "zh", "hi", "ar")

#: One row per line in all three tables, in three syntaxes.
TABLES = {
    "ios": "native/ios/Sources/L10n.swift",
    "android": "native/android/app/src/main/java/app/qrme/studio/L10n.kt",
    "windows": "native/windows/L10n.cs",
}

#: `"key": […]` / `"key" to mapOf(…)` / `["key"] = new() {…}`
_ROW = re.compile(r'^\s*\[?"([\w.]+)"\]?\s*(?::|to|=)')


def _rows(shell: str) -> dict[str, str]:
    """One string per row, continuation lines joined.

    The first draft read a line at a time and called fourteen complete rows
    incomplete: the tab labels were wrapped across three lines when they were
    written, so everything after the first line was invisible to it. A check
    that reports missing translations that are right there would have had
    somebody delete and retype them.
    """
    text = (REPO / TABLES[shell]).read_text(encoding="utf-8")
    out: dict[str, str] = {}
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        m = _ROW.match(lines[i])
        if not m:
            i += 1
            continue
        buf = lines[i]
        # A row is closed when the brackets opened on its first line are.
        while buf.count("[") + buf.count("(") + buf.count("{") > (
                buf.count("]") + buf.count(")") + buf.count("}")):
            i += 1
            if i >= len(lines):
                break
            buf += " " + lines[i].strip()
        if '"en"' in buf:
            out[m.group(1)] = buf
        i += 1
    return out


@pytest.mark.parametrize("shell", sorted(TABLES))
def test_the_row_scan_is_finding_rows(shell):
    """A guard on the guard. A pattern that stopped matching would report
    every row complete by finding none — which is how this whole audit's
    false passes have looked every time."""
    assert len(_rows(shell)) >= ratchets.floor(
            f"shellstable.rows.{shell}"), (
        f"only {len(_rows(shell))} row(s) parsed out of {TABLES[shell]}")


@pytest.mark.parametrize("shell", sorted(TABLES))
def test_every_row_is_in_every_language(shell):
    """Not every `pub.*` row — every row. Seven readers are answered in
    English by a row that is missing them, and the key being present is not
    the same claim."""
    thin = []
    for key, line in _rows(shell).items():
        missing = [c for c in LANGS
                   if not re.search(rf'"{c}"\s*(?::|to|\])\s*=?\s*"', line)]
        if missing:
            thin.append(f"{key}: missing {', '.join(missing)}")
    assert not thin, (
        f"{len(thin)} row(s) in {TABLES[shell]} are not in every language:"
        "\n    " + "\n    ".join(thin))


@pytest.mark.parametrize("shell", sorted(TABLES))
def test_every_slot_survives_translation(shell):
    """A row whose English carries `{name}` and whose German does not renders
    a sentence with the value missing from the middle of it."""
    wrong = []
    for key, line in _rows(shell).items():
        by_lang = dict(re.findall(r'"(\w\w)"\s*(?::|to|\])\s*=?\s*"((?:[^"\\]|\\.)*)"',
                                  line))
        if "en" not in by_lang:
            continue
        want = set(re.findall(r"\{(\w+)\}", by_lang["en"]))
        for lang, text in by_lang.items():
            if lang in LANGS and set(re.findall(r"\{(\w+)\}", text)) != want:
                wrong.append(f"{key}/{lang}: slots differ from en {sorted(want)}")
    assert not wrong, (
        "these rows lose or invent a slot in translation:\n    "
        + "\n    ".join(wrong))


# --- the shell that did not compile ------------------------------------------

def _unseparated_arguments(text: str) -> list[tuple[int, str]]:
    """`foo(…)` and then another named argument, with no comma between them.

    Tracks `{` as well as `(` because a lambda reopens statement context:
    `vm.call({ … oauthState = st … })` is ordinary code, and the first draft
    of this called both of those a defect.
    """
    stack: list[str] = []
    hits: list[tuple[int, str]] = []
    for i, ch in enumerate(text):
        if ch in "({":
            stack.append(ch)
        elif ch in ")}":
            if stack:
                stack.pop()
            if ch == ")" and stack and stack[-1] == "(":
                m = re.match(r"\)\s*\n\s*(\w+)\s*=[^=]", text[i:])
                if m:
                    hits.append((text[:i].count("\n") + 1, m.group(1)))
    return hits


def test_the_separator_scan_can_find_one():
    """The check, driven on the shape it exists for — the real one, from
    `SettingsScreen`, before it was moved out."""
    broken = (
        'fun S() {\n'
        '    Text(L10n.t("tab.settings", vm.language), color = Qrme.Txt, fontSize = 22.sp,\n'
        '    ProblemReportingCard()\n'
        '        fontWeight = FontWeight.Bold)\n'
        '}\n')
    assert _unseparated_arguments(broken), "the scan cannot find its own case"


def test_a_lambda_body_is_not_an_argument_list():
    """The two false positives, kept as a test so the fix for them is not
    quietly undone by a stricter-looking rewrite."""
    fine = (
        'fun S() {\n'
        '    vm.call({\n'
        '        val (st, url) = ApiClient.oauthStart(doors.first())\n'
        '        oauthState = st\n'
        '    })\n'
        '}\n')
    assert not _unseparated_arguments(fine)


@pytest.mark.parametrize("suffix", [".kt", ".swift", ".cs"])
def test_no_call_sits_between_two_arguments(suffix):
    hits = []
    for path in sorted((REPO / "native").rglob(f"*{suffix}")):
        for line, name in _unseparated_arguments(
                path.read_text(encoding="utf-8", errors="ignore")):
            hits.append(f"{path.relative_to(REPO)}:{line} — then `{name} =`")
    assert not hits, (
        "two arguments with nothing between them; this does not parse:\n    "
        + "\n    ".join(hits))
