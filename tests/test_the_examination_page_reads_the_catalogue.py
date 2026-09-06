"""The examined rows on the examination page are the reader's rows.

`docs/examination.md` ends with ten positions shown three ways: what the
family alone led with, what the reader returns now, and the group that
made the difference. A table like that is typed once and true once. This
guard rebuilds every cell from `qrme.occupations.find` and the pool's own
family blocks, and fails when the page and the pool disagree — the same
posture as the README guards, applied to the page written to be checked.

    asked     does the page show the repaired rows
    mattered  are they the rows the reader returns today

It also holds the two numbers in the page's highlight row for the
catalogue against the build: how many groups, how many positions they
reach. A number in prose that nothing reads is the drift this estate
keeps finding in itself.
"""

import json
import re
from pathlib import Path

from qrme import occupations

from . import ratchets

REPO = Path(__file__).resolve().parent.parent
PAGE = REPO / "docs" / "examination.md"
DATA = REPO / "qrme" / "data" / "occupations.json"

START = "<!-- catalogue-examined:start -->"
END = "<!-- catalogue-examined:end -->"


def _page_rows() -> list[list[str]]:
    text = PAGE.read_text(encoding="utf-8")
    block = text[text.index(START) + len(START):text.index(END)]
    rows = [ln for ln in block.strip().splitlines() if ln.startswith("|")]
    body = rows[2:]                                   # header and rule
    return [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in body]


def _expected(title: str, families: dict) -> list[str]:
    row = occupations.find(title)
    assert row is not None, f"{title!r} is not in the pool"
    fam = row["family"]
    before = " / ".join(families[fam]["s"][:3])
    now = " / ".join(row["skills"][:3])
    if row["written"]:
        group = "— (written by hand)"
    elif row.get("group"):
        group = row["group"]
    else:
        group = "— (no group yet)"
    return [title, fam, group, before, now]


def test_every_examined_row_is_the_readers_row():
    families = json.loads(DATA.read_text(encoding="utf-8"))["families"]
    rows = _page_rows()
    assert len(rows) >= ratchets.floor("examination.catalogue_rows"), (
        "the examined table has lost rows")
    for cells in rows:
        assert cells == _expected(cells[0], families), (
            f"the page's row for {cells[0]!r} is not what the reader returns:\n"
            f"  page:   {cells}\n  reader: {_expected(cells[0], families)}")


def test_the_examined_rows_show_all_three_outcomes():
    """A repaired row, a written row the group stays silent on, and a gap.

    The page says the table shows the design holding, not only the design
    winning. Each of the three has to be present or the sentence is not
    true.
    """
    groups = [cells[2] for cells in _page_rows()]
    assert any(g == "— (written by hand)" for g in groups)
    assert any(g == "— (no group yet)" for g in groups)
    repaired = sum(1 for g in groups if not g.startswith("—"))
    assert repaired >= ratchets.floor("examination.catalogue_repairs"), (
        "the examined table shows fewer repairs than it did")


def test_the_highlight_row_carries_the_builds_numbers():
    raw = json.loads(DATA.read_text(encoding="utf-8"))
    groups = len(raw["groups"])
    covered = sum(1 for p in raw["positions"] if p.get("g"))
    total = len(raw["positions"])
    text = PAGE.read_text(encoding="utf-8")
    line = next(ln for ln in text.splitlines()
                if ln.startswith("| A position says what it does"))
    assert f"{groups} groups reach {covered:,} positions ({100*covered/total:.1f}%)" in line, (
        "the examination page's catalogue row does not carry the build's "
        f"numbers: {groups} groups, {covered:,} of {total:,}")
    assert f"{total:,} positions" in line
