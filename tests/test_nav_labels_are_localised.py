"""Every sidebar tab has a word, in every language the console offers.

`l10n.ts` documents its fallback chain as "keys fall back to English so a
missing translation shows words, never a blank". That is true of a *translation*
and false of a missing key: `t()` ends with `|| key`, so a tab with no entry at
all renders its own identifier. Four of them did — Marketplace, Delegation, Desk
and Voice read `nav.market`, `nav.delegate`, `nav.desk` and `nav.voice` in the
sidebar, in English too.

Worth naming precisely, because the near-miss is the interesting part. `NAV` in
`App.tsx` carries an English `label` on every entry, sitting one line above the
icon — and nothing reads it. The English word was right there, unused, while the
identifier went on screen. A design that keeps the correct value next to the
wrong one and shows the wrong one is not a typo; it is two sources of truth
where the unused one looks authoritative.

It also failed in the direction that hides: a blank label looks broken and gets
reported, where `nav.market` looks like a label somebody chose. Nobody files a
bug about a tab that has a name.

So: every id in `NAV` must have a `nav.<id>` key, and every key must carry every
language in `Lang`. The second half matters because a partial row is exactly the
case the documented fallback *does* handle correctly, and asserting it keeps the
two behaviours from being confused again.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()
APP = REPO / "app/src/App.tsx"
L10N = REPO / "app/src/l10n.ts"


def _nav_ids() -> list[str]:
    src = APP.read_text(encoding="utf-8")
    block = re.search(r"const NAV[^=]*=\s*\[(.*?)\n\];", src, re.S)
    assert block, "no NAV array in App.tsx"
    return re.findall(r'\{\s*id:\s*"(\w+)"', block.group(1))


def _table() -> dict[str, set[str]]:
    """Each `nav.*` key mapped to the language codes it actually carries."""
    src = L10N.read_text(encoding="utf-8")
    out: dict[str, set[str]] = {}
    for key, body in re.findall(r'"(nav\.\w+)":\s*\{(.*?)\}', src, re.S):
        out[key] = set(re.findall(r"\b([a-z]{2}):", body))
    return out


def _languages() -> set[str]:
    src = L10N.read_text(encoding="utf-8")
    decl = re.search(r"export type Lang\s*=(.*?);", src, re.S)
    assert decl, "no Lang union in l10n.ts"
    return set(re.findall(r'"(\w+)"', decl.group(1)))


def test_every_tab_has_a_label():
    """The check the sidebar needed and did not have."""
    table = _table()
    missing = [i for i in _nav_ids() if f"nav.{i}" not in table]
    assert not missing, (
        "these tabs render their own key in the sidebar rather than a word: "
        + ", ".join(f"nav.{m}" for m in missing))


def test_no_tab_is_missing_a_language():
    """A partial row is the case the fallback really does handle — asserted
    so the two failure modes stay told apart."""
    langs, table = _languages(), _table()
    gaps = {k: sorted(langs - v) for k, v in table.items() if langs - v}
    assert not gaps, f"nav labels missing translations: {gaps}"


def _table_rows() -> dict[str, dict[str, str]]:
    """Every key in `CHROME`, mapped to its language → sentence."""
    src = L10N.read_text(encoding="utf-8")
    body = src[src.index("const CHROME: Table = {"):src.index("\n};\n\nexport function t(")]
    heads = [(m.start(), m.group(1))
             for m in re.finditer(r'^  "([\w.]+)":\s*\{', body, re.M)]
    out: dict[str, dict[str, str]] = {}
    for i, (pos, key) in enumerate(heads):
        end = heads[i + 1][0] if i + 1 < len(heads) else len(body)
        out[key] = dict(re.findall(r'\b([a-z]{2}):\s*"((?:[^"\\]|\\.)*)"',
                                   body[pos:end]))
    return out


#: A quotation mark in any of the scripts the table uses. A Latin word
#: touching one of these is being named, not spoken.
_QUOTES = "「」『』\"'`“”‘’《》〈〉"


def _bare_latin(sentence: str) -> list[str]:
    """Lowercase Latin words standing on their own in a sentence.

    Holes are removed first (`{name}` is Latin by construction and always
    will be), capitalised words are skipped (`QRME`, `OAuth`, `Bianchi` are
    names), and anything glued to a dot, slash or at-sign is skipped
    (`smtp.gmail.com` is an address, not a sentence).
    """
    sentence = re.sub(r"\{\w+\}", " ", sentence)
    out = []
    for m in re.finditer(r"[A-Za-z]{4,}", sentence):
        word = m.group()
        if word != word.lower():
            continue
        before = sentence[m.start() - 1] if m.start() else " "
        after = sentence[m.end()] if m.end() < len(sentence) else " "
        if before in _QUOTES or after in _QUOTES:
            continue
        if before in ".@_-/" or after in ".@_-/":
            continue
        out.append(word)
    return out


def _every_row() -> dict[str, set[str]]:
    """Every key in `CHROME`, mapped to the languages its row carries.

    Split on the row headers rather than brace-matched, and string literals
    are blanked first — otherwise a two-letter word followed by a colon
    inside a translation ("así: ", "そこで: ") reads as a language code and
    the audit reports gaps that are not there.
    """
    src = L10N.read_text(encoding="utf-8")
    body = src[src.index("const CHROME: Table = {"):src.index("\n};\n\nexport function t(")]
    heads = [(m.start(), m.group(1))
             for m in re.finditer(r'^  "([\w.]+)":\s*\{', body, re.M)]
    out: dict[str, set[str]] = {}
    for i, (pos, key) in enumerate(heads):
        end = heads[i + 1][0] if i + 1 < len(heads) else len(body)
        chunk = re.sub(r'"(?:[^"\\]|\\.)*"', '""', body[pos:end])
        out[key] = set(re.findall(r"\b([a-z]{2}):", chunk))
    return out


def test_no_row_of_the_table_is_missing_a_language():
    """The check above, for the other 1471 keys.

    `test_no_tab_is_missing_a_language` reads `nav.*` and nothing else, and
    that was the whole table when it was written — `l10n.ts` opens by calling
    itself "chrome localization for the desktop console" and for a long time
    it was. It is now 1519 keys: forty-six screens moved into it one release
    at a time, and every one of those rounds added rows that no completeness
    check could see.

    The gap is quiet in the way that matters. A key with no row at all renders
    its own identifier — `org.title` in the heading — and somebody reports it.
    A key missing one language falls back to English, which looks *deliberate*:
    a Hindi reader sees an English heading on a Hindi page and has no way to
    tell an untranslated string from a forgotten one. Nobody files that bug
    either, and the ratchet cannot catch it, because the ratchet asks whether
    the screen looks the key up, not whether the row answers in ten languages.

        asked     is the sidebar translated everywhere
        mattered  is the table translated everywhere

    It was true when this test was added — all 1519 rows complete — so this
    is a latch on work already done rather than a new backlog.
    """
    langs = _languages()
    gaps = {k: sorted(langs - v) for k, v in _every_row().items() if langs - v}
    assert not gaps, (
        f"{len(gaps)} row(s) of the console table are short a language, so "
        "those readers get English and cannot tell it was an oversight:\n    "
        + "\n    ".join(f"{k}: no {', '.join(v)}" for k, v in sorted(gaps.items())))


#: Lowercase Latin tokens that are not English prose even though they look
#: like it: a URI scheme, and the CJK rows are the only place they appear
#: bare. Kept short on purpose — this is an exemption list, and every entry
#: is a claim that a word is a name rather than a sentence.
_NOT_PROSE = {"http", "https"}


def test_no_translation_is_carrying_an_english_word():
    """A row that is translated except for one word left in English.

    Every check up to here asks whether a row *exists* and whether it has
    its ten languages. None of them can tell a finished Japanese sentence
    from one with `travels` still sitting in the middle of it, because both
    are non-empty strings in the `ja` slot.

    That is not hypothetical. Two rows were drafted with an English word
    stranded inside the CJK text in the release this check was added in —
    one `someone`, one `travels` — and both were caught by re-reading, which
    is the review method that works right up until the day it doesn't. A
    Japanese reader would have seen a clean sentence with one foreign word
    in it, and had no way to tell a deliberate quotation from a slip.

        asked     is the row translated
        mattered  is the row translated all the way through

    The rule is narrow so it can be trusted: only `ja` and `zh`, only a
    lowercase Latin word of four letters or more, only when the same word
    is in the row's own English, only when it is *bare* — not touching a
    quote mark, and not part of a dotted or slashed token — and only in
    rows whose English is prose rather than a list.

    That last clause is what keeps the check honest. A handful of rows are
    nothing but literal values a person is meant to type or recognise:
    `pas.action.ph` is *advance, assist, cancel*, `rem.play.platform.ph`
    is *steam, xbox, playstation*, `pas.assist` is the enum `assist`
    itself. Those words are the same in every language because they are
    names, and demanding they be translated or bracketed would make a
    placeholder harder to use in service of a rule about sentences. Five
    English words is the line: below it the row is a list, above it it is
    something somebody reads.

    Quoting is what makes the difference in the rows that *are* prose, and
    the table already relies on it: `desk.there.pitch` names the API's own
    `away` and `closed` states inside 「」. A word in brackets is being
    *named*; a word in the open is being *read*. So when this fires the fix
    is one of two things — translate the word, or quote it and mean it.
    """
    hits = []
    for key, row in _table_rows().items():
        english = row.get("en", "")
        # Words, not tokens: "advance / assist / cancel" is three values and
        # two slashes, and counting the slashes would call it a sentence.
        if len(re.findall(r"[A-Za-z]+", english)) < 5:
            continue
        english = {w.lower() for w in re.findall(r"[A-Za-z]{4,}", english)}
        for lang in ("ja", "zh"):
            for word in _bare_latin(row.get(lang, "")):
                if word in english and word not in _NOT_PROSE:
                    hits.append(f"{key}/{lang}: {word!r}")
    assert not hits, (
        f"{len(hits)} translation(s) still carry an English word from their "
        "own English row:\n    " + "\n    ".join(sorted(hits))
        + "\n  Translate the word, or quote it — 「away」 reads as a name, "
          "away reads as an oversight.")


def test_the_unused_english_label_still_agrees():
    """`NAV` keeps an English `label` that nothing renders.

    Deleting it would be tidier and is somebody's call, not this test's. What
    this refuses is the version that already bit: the two drifting apart while
    the unused one looks like the answer. If both exist, they say the same
    thing in English.
    """
    src = APP.read_text(encoding="utf-8")
    block = re.search(r"const NAV[^=]*=\s*\[(.*?)\n\];", src, re.S).group(1)
    labels = dict(re.findall(r'\{\s*id:\s*"(\w+)",\s*label:\s*"([^"]+)"', block))
    l10n = L10N.read_text(encoding="utf-8")
    for tab, label in labels.items():
        row = re.search(rf'"nav\.{tab}":\s*\{{\s*\n?\s*en:\s*"([^"]+)"', l10n)
        assert row, f"nav.{tab} has no English entry"
        assert row.group(1) == label, (
            f"nav.{tab}: NAV says {label!r}, l10n says {row.group(1)!r} — "
            "the sidebar shows the second and the code reads like the first")


@pytest.mark.parametrize("tab", ["exchanges", "grants", "party"])
def test_the_new_tabs_are_wired_end_to_end(tab):
    """A door needs all three joins, and the middle one is easy to forget.

    A tab in `NAV` with no branch in the render is a button that does nothing;
    a component imported but never branched to is dead code that still passes
    a typecheck. Both have happened elsewhere in this suite's history, so the
    three joins are asserted together rather than assumed from the first.
    """
    src = APP.read_text(encoding="utf-8")
    assert f'id: "{tab}"' in src, f"{tab} is not in NAV"
    assert f'tab === "{tab}"' in src, f"{tab} has no branch in the render"


# --------------------------------------------------------------------------- #
# The general case, arrived at from the sibling
# --------------------------------------------------------------------------- #
#
# The two checks below came back from JIM-mini, where the same defect turned up
# again a dozen releases after this file closed it here: a `presence` tab with
# no `nav.presence` row, reading its own key between two real words. This file
# had the tab half and not the general one.
#
#     asked     does every tab have a label
#     mattered  does every key any screen asks for exist
#
# A sidebar is one place a console looks a key up. This console looks keys up
# in fifty-odd files, and nothing was checking the other forty-nine.

from .ratchets import floor  # noqa: E402


def _console_sources() -> list[Path]:
    src = REPO / "app/src"
    return [f for f in list(src.rglob("*.tsx")) + list(src.rglob("*.ts"))
            if f.name != "l10n.ts"]


def _all_keys() -> set[str]:
    return set(re.findall(r'^  "([\w.]+)":', L10N.read_text("utf-8"), re.M))


def test_the_tab_scan_is_finding_tabs():
    """A guard on the guard: a walk that stopped matching would report every
    tab labelled by finding none of them."""
    assert len(_nav_ids()) >= floor("console.nav_tabs"), (
        f"only {len(_nav_ids())} tab(s) parsed out of NAV — this console has "
        "more, and every check above would pass on almost nothing")


def test_no_literal_lookup_is_missing_its_row():
    """Every key a screen spells out, across the whole console.

    Only literal keys — `t("a.b", lang)` — because a composed key cannot be
    resolved without running the app, and a check that guessed at those would
    fail on working code.

    The comma at the end of the pattern is what makes "literal" mean it. PDI,
    where this check went next, builds some lookups by concatenation —
    `t("pos.cap." + k, lang)` — and a pattern stopping at the closing quote
    read `pos.cap.` as a key of its own and reported six missing rows that
    were not rows at all.
    """
    table, asked = _all_keys(), set()
    for f in _console_sources():
        asked |= set(re.findall(r'\b(?:t|tr|L)\(\s*"([\w.]+)"\s*,',
                                f.read_text(encoding="utf-8")))
    missing = sorted(asked - table)
    assert not missing, (
        f"{len(missing)} key(s) are looked up and have no row:\n    "
        + "\n    ".join(missing)
        + "\n  `t()` falls back to the key, so each renders as its own name "
          "on screen, in every language.")
