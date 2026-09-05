"""The occupation pool: complete rows, and a search bar that finds them.

    asked     does the pool contain the job
    mattered  can somebody who does not know its name find it

The Company Builder's fallback used to be three canned seats — "Industry
lead", "Front desk", "Bookkeeper" — on a platform whose promise is a
person for any job on earth. The pool is the answer to that, and a pool
nobody can search is the same failure wearing a bigger number.

So the guard here is not "how many rows". It is a list of the way people
actually ask, each with the row it has to reach: "reads scans" is the
radiologist, "puts out fires" is the firefighter. Every one of these was
a miss at some point while the ranking was being built, and each is here
because it broke rather than because it read well.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from qrme import occupations

ROOT = Path(__file__).resolve().parent.parent
LISTS = ROOT / "tools" / "data"


#: What somebody types, and the row it has to put first. These are the
#: phrasings that failed: no stemming missed the welder, over-stemming
#: turned "planes" into three planners, a summed score let one strong
#: keyword beat two weak ones and answered "looks after old people" with
#: a scaffolder, and a common word in a title outranked a rare one in the
#: keywords until rarity was weighed — "cleans teeth" found a building
#: cleaner.
ASKED = [
    ("reads scans", "Radiologist"),
    ("flies planes", "Airline pilot"),
    ("defends people in court", "Criminal defence lawyer"),
    ("looks after old people", "Care home manager"),
    ("puts out fires", "Firefighter"),
    ("fixes cars", "Auto mechanic"),
    ("delivers babies", "Midwife"),
    ("sells houses", "Estate agent"),
    ("welding", "Welder"),
    ("cuts hair", "Hairdresser"),
    ("bakes bread", "Baker"),
    ("teaches children", "Primary school teacher"),
    ("guides planes", "Air traffic controller"),
    ("designs bridges", "Civil engineer"),
    ("cleans teeth", "Dental Hygienist"),
]


@pytest.mark.parametrize("question,wanted", ASKED)
def test_the_way_people_ask_reaches_the_job(question, wanted):
    hits = occupations.search(question, limit=5)
    assert hits, f"{question!r} finds nothing at all"
    assert hits[0]["title"] == wanted, (
        f"{question!r} answers with {hits[0]['title']!r}; the pool has "
        f"{wanted!r} and that is what somebody asking this wants:\n    "
        + "\n    ".join(h["title"] for h in hits))


def test_a_name_finds_itself():
    """Typing a job's own name must beat every near neighbour.

    Written rows outrank strength outright — without that, forty thousand
    reported titles bury them — so the exact name has to outrank the
    written row in turn, or a taxonomy title could never be found by its
    own name. Singular and plural are the same job, not two: the pool
    carries "Dental Hygienist" and "Dental Hygienists" both.
    """
    for title in ("Welders and flamecutters", "Fire-fighters",
                  "Dental Hygienists", "Commercial Pilots", "Radiologist",
                  "Zumba Instructor", "Whistle Punk", "911 Dispatcher",
                  "Grease Monkey", "Zipline Guide"):
        found = occupations.search(title, limit=1)[0]["title"]
        assert occupations.same_name(found, title), f"{title!r} found {found!r}"


def test_every_row_can_fill_a_seat():
    """A row with no skills is a title, not a position: it would open a
    seat the app could say nothing about."""
    thin = [r["title"] for r in occupations._pool()
            if not r["skills"] or not r["connections"] or not r["keywords"]]
    assert not thin, (
        "positions carrying no skills, connections or search terms — a "
        "seat opened on one of these has nothing to show:\n    "
        + "\n    ".join(thin[:20]))


def test_no_position_is_in_the_pool_twice():
    seen = {}
    for row in occupations._pool():
        key = row["title"].lower()
        assert key not in seen, f"{row['title']!r} appears twice"
        seen[key] = True


def test_every_title_on_the_lists_reaches_the_pool():
    """A taxonomy title is either its own row or already covered by a
    written one. Silently dropping it would be the quiet failure: the
    pool would claim a list it does not carry."""
    from tools.build_occupations import PAREN, _norm  # noqa: PLC0415

    have = {_norm(r["title"]) for r in occupations._pool()}
    missing = []
    for path in sorted(LISTS.glob("*_titles.txt")):
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            # A reported title carries its own expansion — "AC Installer
            # (Air Conditioning Installer)" — and the expansion becomes
            # search words rather than part of the name.
            match = PAREN.match(line)
            title = match.group(1).strip() if match else line
            if title and _norm(title) not in have:
                missing.append(f"{path.name}: {line}")
    assert not missing, (
        "titles on the shipped lists that no row answers:\n    "
        + "\n    ".join(missing[:20]))


def test_the_families_are_stored_once_not_on_every_row():
    """The shared half lives in the family block. Written onto every row
    it tripled the file and said nothing new, and the pool has to stay
    small enough to ship."""
    raw = json.loads((ROOT / "qrme" / "data" / "occupations.json")
                     .read_text(encoding="utf-8"))
    assert isinstance(raw["families"], dict)
    for fam in raw["families"].values():
        assert fam["s"] and fam["c"]
    carried = sum(len(r.get("s", [])) for r in raw["positions"])
    shared = sum(len(f["s"]) for f in raw["families"].values())
    assert carried < shared * len(raw["positions"]) / 4, (
        "rows are carrying their family's skills again")


def test_suggesting_a_roster_is_not_capped_by_the_headcount():
    """`MAX_HEADCOUNT` governs how many seats a company may open, never
    how many it may be shown. Truncating the suggestions to the headcount
    hid the roles a founder had not thought of."""
    from qrme.company import MAX_HEADCOUNT  # noqa: PLC0415

    offered = occupations.for_trade("software company", limit=MAX_HEADCOUNT * 2)
    assert len(offered) > MAX_HEADCOUNT


def test_the_roster_leads_with_the_trade_not_the_founders_adjectives():
    """`for_trade` ranks the founder's own words *within* the trade.

    Scored together with the trade they outranked it: "a small artisan
    bakery on the high street" put a university lecturer second in a
    bakery, on the strength of the word "high", and both a bakery and an
    app studio hired an outdoor power equipment mechanic off the word
    "small".
    """
    rows = occupations.for_trade(
        "bakery", limit=8, described="a small artisan bakery on the high street")
    assert rows[0]["title"] == "Baker", [r["title"] for r in rows]
    families = {r["family"] for r in rows}
    assert families == {"Hospitality, food & retail"}, (
        "a bakery's roster reached outside food and retail:\n    "
        + "\n    ".join(f"{r['title']} — {r['family']}" for r in rows))


def test_the_founders_words_still_rank_inside_the_trade():
    """Ranked within the trade, not ignored: a studio that says it makes
    games should be offered the game developer."""
    rows = occupations.for_trade(
        "software", limit=6, described="a studio making mobile games")
    assert "Game developer" in [r["title"] for r in rows]


def test_a_roster_is_never_a_filing_label():
    """A taxonomy files what it could not place under "All Other" and
    "not elsewhere classified". Those stay searchable — somebody looking
    for one should find it — but handing a founder "Construction and
    Related Workers, All Other" hands them a filing label, not a job."""
    for trade in ("bakery", "software", "construction", "haulage", "care home"):
        for row in occupations.for_trade(trade, limit=20):
            assert not occupations._residual(row["title"]), (
                f"{trade!r} was offered {row['title']!r}")
    assert occupations.search("Construction and Related Workers, All Other",
                              limit=1), "the residual rows left the pool entirely"


def test_the_builder_no_longer_falls_back_to_three_canned_seats():
    """What "Industry lead / Front desk / Bookkeeper" was replaced by.

    Those three were what a founder saw whenever the study did not parse
    — most often on a deployment with no model to ask at all — and the
    owner's photograph of the Company Builder showed exactly them.
    """
    from qrme.company import _from_pool  # noqa: PLC0415

    rows = _from_pool({"industry": "bakery", "headcount": 6},
                      "an artisan bakery")
    assert len(rows) == 6
    assert [r["title"] for r in rows][:1] == ["Baker"]
    assert "Industry lead" not in [r["title"] for r in rows]
    for row in rows:
        assert row["skills"] and row["connections"], (
            f"{row['title']} would open a seat with nothing on its card")


def test_a_suggested_seat_arrives_knowing_what_the_job_needs():
    """A seat the model named still gets the pool's skills where the pool
    has the role — a suggestion used to be three strings, so a founder
    chose a title without being told what the work would take."""
    from qrme.company import _with_pool  # noqa: PLC0415

    row = _with_pool({"title": "Baker", "department": "Kitchen", "why": "bread"})
    assert row["skills"] and row["connections"]
    assert row["known_as"] == "Baker"
