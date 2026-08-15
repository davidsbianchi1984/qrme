"""Thirty-four friends pictures, one blank page behind all of them.

## The finding

A profile's friends list renders a grid of faces, and a face is a link: it
opens that friend's homepage. The Starter Collection ships thirty-four
profiles who are on each other's friends lists by design — the dossiers
install colleague friendships in both directions — so the collection is the
one place on a fresh deployment where that grid is full.

Every one of those faces opened `social._DEFAULT_DOC`: a blank headline, a
blank about, no links, no top friends, and the same purple. The page was
reachable, public, and empty.

    asked     the friends picture should open their profile homepage
    mattered  it did, and there was nothing on the other side

## What a homepage is composed of, and why not written

`dossiers.homepage_doc` builds the page out of the dossier the same starter
is already grounded in — expertise and services as the about, the first
three skill chips as the headline, a palette chosen by the family of trade.
Nothing here is a second copy of anything: a hand-written page beside a
dossier is two statements about one profile, and the way a page ends up
claiming something its persona has never heard of.

Two absences are deliberate and are checked below as absences, so a later
round cannot fill them by accident:

* **No links.** A fictional physician has no website. An invented URL either
  goes nowhere or goes somewhere real that has nothing to do with her, and
  both are worse than an empty field.
* **No hand-picked colour per starter.** Seven families, not thirty-four
  opinions — and `FAMILY_OF` must name every industry on the roster, so a
  starter added later fails here rather than falling back to the default.

## Two-directional, like every roster check in this suite

A starter with no homepage fails; a `FAMILY_OF` entry for an industry no
starter has fails. A mapping nothing reads sits correct and unreachable.
"""

from __future__ import annotations

import pytest

from qrme import dossiers, seed, social


ALL_HANDLES = [row[0] for row in seed.STARTERS + seed.RATED]
INDUSTRY_OF = {row[0]: row[1] for row in seed.STARTERS + seed.RATED}


# --- the roster and the palette map are the same set ------------------------

def test_every_starter_industry_has_a_family():
    missing = sorted({i for i in INDUSTRY_OF.values()
                      if i not in dossiers.FAMILY_OF})
    assert not missing, (
        "industries with no theme family — their starters would fall back to "
        "the default purple every other blank page has:\n    "
        + "\n    ".join(missing))


def test_no_family_entry_is_for_an_industry_nobody_has():
    on_roster = set(INDUSTRY_OF.values())
    stray = sorted(i for i in dossiers.FAMILY_OF if i not in on_roster)
    assert not stray, (
        "theme families for industries no starter has — correct and "
        "unreachable:\n    " + "\n    ".join(stray))


def test_every_family_names_a_palette():
    missing = sorted({f for f in dossiers.FAMILY_OF.values()
                      if f not in dossiers._PALETTES})
    assert not missing, "families with no palette:\n    " + "\n    ".join(missing)


# --- the document itself ----------------------------------------------------

@pytest.mark.parametrize("handle", ALL_HANDLES)
def test_the_page_says_something(handle):
    doc = dossiers.homepage_doc(handle, INDUSTRY_OF[handle])
    assert doc["headline"].strip(), f"{handle}'s homepage has no headline"
    assert len(doc["headline"]) <= 120, (
        f"{handle}'s headline is longer than the field holds and would be "
        "silently truncated by set_homepage")
    # No length floor here. The first draft asserted `len(about) > 400`, which
    # is a number nothing compares against what it measures — and the two
    # containment checks below say the same thing exactly: the about is the
    # two dossier texts, so it is as long as they are. A magic number beside
    # a direct check is the weaker of the two pretending to add something.
    for text in (dossiers.DOSSIERS[handle]["expertise"],
                 dossiers.DOSSIERS[handle]["services"]):
        assert text in doc["about"], (
            f"{handle}'s page and dossier disagree — the page is supposed to "
            "be composed from it, not written beside it")


@pytest.mark.parametrize("handle", ALL_HANDLES)
def test_the_page_carries_no_invented_links(handle):
    doc = dossiers.homepage_doc(handle, INDUSTRY_OF[handle])
    assert doc["links"] == [], (
        f"{handle} has links on an invented person's homepage — a URL here "
        "either goes nowhere or goes somewhere real that is not theirs")


def test_the_collection_is_not_one_colour():
    themes = {tuple(sorted(dossiers.homepage_doc(h, INDUSTRY_OF[h])["theme"]
                           .items()))
              for h in ALL_HANDLES}
    assert len(themes) == len(dossiers._PALETTES), (
        f"{len(themes)} distinct themes across the collection, expected "
        f"{len(dossiers._PALETTES)} — a family whose starters all moved out "
        "is a palette nothing renders")
    default = tuple(sorted(social._DEFAULT_DOC["theme"].items()))
    assert default not in themes, (
        "a starter still carries the blank page's purple")


# --- installed, not merely composed -----------------------------------------

@pytest.fixture(scope="module")
def seeded(tmp_path_factory):
    import os
    from qrme import db

    old = os.environ.get("QRME_DB")
    os.environ["QRME_DB"] = str(tmp_path_factory.mktemp("homepage") / "q.db")
    os.environ.setdefault("QRME_LLM", "stub")
    db.reset()
    report = seed.seed()
    yield report
    db.reset()
    if old is not None:
        os.environ["QRME_DB"] = old
    else:
        os.environ.pop("QRME_DB", None)


def test_seed_installs_every_homepage(seeded):
    assert seeded["homed"] == len(ALL_HANDLES), seeded["homed_handles"]


def test_a_stranger_reads_a_real_page(seeded):
    """What somebody who clicked a face actually gets — read back through the
    public path, with `viewer_is_owner` false, for every starter."""
    from qrme import db

    conn = db.connect()
    for handle in ALL_HANDLES:
        pid = conn.execute("SELECT profile_id FROM handles WHERE handle=?",
                           (handle,)).fetchone()["profile_id"]
        page = social.homepage(pid)
        assert page["headline"].strip(), f"{handle}'s page is blank to a visitor"
        assert page["about"].strip(), f"{handle}'s about is blank to a visitor"
        assert not page["editable"]
        # The colleagues, standing on the page. Fewer than the dossier lists
        # is allowed — a top friend must be an actual friend — but none at
        # all means the friendship pass and this one disagree.
        assert page["top_friends"], (
            f"{handle}'s page names no top friends, though the dossier gives "
            f"it {len(dossiers.DOSSIERS[handle]['colleagues'])} colleagues")


def test_top_friends_are_real_friends(seeded):
    """The rule `set_homepage` enforces, checked from the other side: every
    face on the page is somebody the graph agrees is a friend."""
    from qrme import db

    conn = db.connect()
    for handle in ALL_HANDLES:
        pid = conn.execute("SELECT profile_id FROM handles WHERE handle=?",
                           (handle,)).fetchone()["profile_id"]
        for friend in social.homepage(pid)["top_friends"]:
            assert social.are_friends(pid, friend["profile_id"]), (
                f"{handle}'s page shows {friend['display_name']} as a top "
                "friend and the graph does not")


def test_reseeding_does_not_overwrite_somebody_s_own_page(seeded):
    """Blank-only, like every other repair in `seed`. An owner who wrote
    their own page has made a decision, and re-running the seed at deploy
    must not argue with it."""
    from qrme import db

    conn = db.connect()
    pid = conn.execute("SELECT profile_id FROM handles WHERE handle=?",
                       ("priya_raman",)).fetchone()["profile_id"]
    social.set_homepage(pid, {"headline": "under construction",
                              "about": "back soon",
                              "theme": {"bg": "#000000", "accent": "#ffffff"}})
    again = seed.seed()
    assert again["homed"] == 0, again["homed_handles"]
    assert social.homepage(pid)["headline"] == "under construction"
