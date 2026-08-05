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
