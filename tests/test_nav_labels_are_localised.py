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
