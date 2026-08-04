"""Thirty-four specialists who could not answer for their own trade.

## The finding

The Starter Collection's grounding stopped at one Field Pack per industry —
three items, installed in 0.3.1 so a physician persona would stop answering
from tone alone. That fixed the cold start and no more: ask Dr. Osei what
she actually knows, what she can do for you, or who she works with, and the
honest answer was three pamphlets. The persona budget renders
``sources[:8]``, so five of her eight seats were empty.

    asked     does the starter have source material
    mattered  can the starter answer for its own trade

## What the dossiers add, and how this file holds them

`qrme/dossiers.py` names all thirty-four starters — the thirty-three and the
rated one — and gives each three source items (what I know, skills and
services, colleagues), skill chips beyond the marketplace's three tags, and
a colleague graph installed as *real friendships*. The colleagues prose is
composed from the same list as the graph, so the sentence the persona says
and the API's friends list cannot disagree.

The checks below are two-directional the way every roster check here is: a
starter without a dossier fails, and a dossier for a starter that does not
exist fails — a dossier nothing installs would sit correct and unreachable,
which is the `grantee_name` lesson from the field-label table.
"""

from __future__ import annotations

import json

import pytest

from qrme import dossiers, seed


ALL_HANDLES = [row[0] for row in seed.STARTERS + seed.RATED]
NAME_OF = {row[0]: row[2] for row in seed.STARTERS + seed.RATED}


# --- the roster and the dossiers are the same set ---------------------------

def test_every_starter_has_a_dossier():
    missing = [h for h in ALL_HANDLES if h not in dossiers.DOSSIERS]
    assert not missing, (
        "starters with no dossier — they cannot answer for their trade:\n    "
        + "\n    ".join(missing))


def test_no_dossier_names_a_starter_that_does_not_exist():
    orphans = [h for h in dossiers.DOSSIERS if h not in ALL_HANDLES]
    assert not orphans, (
        "dossiers nothing will ever install:\n    " + "\n    ".join(orphans))


def test_the_rated_starter_is_not_exempt():
    """Vivienne is part of the collection, and 'wholesome knowledge' includes
    the 18+ tier — behind its age wall, not absent."""
    assert "vivienne_sable" in dossiers.DOSSIERS


@pytest.mark.parametrize("handle", ALL_HANDLES)
def test_the_dossier_is_substantial(handle):
    """A dossier is depth, not a checkbox. The floors are low enough to
    leave the writing free and high enough that a one-liner fails."""
    d = dossiers.DOSSIERS[handle]
    assert len(d["expertise"]) >= 350, (
        f"{handle}: expertise is {len(d['expertise'])} chars — a specialist "
        "should have more to say about their own trade")
    assert len(d["services"]) >= 250, f"{handle}: services too thin"
    assert 2 <= len(d["colleagues"]) <= 5, (
        f"{handle}: {len(d['colleagues'])} colleagues — a network of one is "
        "not a network, and one of thirty is not a referral")
    assert len(d["skills"]) >= 4, f"{handle}: fewer than 4 skill chips"


@pytest.mark.parametrize("handle", ALL_HANDLES)
def test_colleagues_resolve_and_nobody_refers_to_themselves(handle):
    d = dossiers.DOSSIERS[handle]
    for colleague in d["colleagues"]:
        assert colleague in ALL_HANDLES, (
            f"{handle} refers to {colleague}, who is not in the collection")
        assert colleague != handle, f"{handle} refers to themselves"


def test_the_colleague_prose_names_the_same_people_as_the_graph():
    """Composed, not written twice — this is the property that makes 'who
    are your connections' have one answer in chat and in the API."""
    for handle in ALL_HANDLES:
        prose = dossiers.colleague_prose(handle, NAME_OF)
        for colleague in dossiers.DOSSIERS[handle]["colleagues"]:
            assert NAME_OF[colleague] in prose, (
                f"{handle}'s colleague prose does not name "
                f"{NAME_OF[colleague]}")


# --- installed, not merely written ------------------------------------------

@pytest.fixture(scope="module")
def seeded(tmp_path_factory):
    import os
    from qrme import db

    old = os.environ.get("QRME_DB")
    os.environ["QRME_DB"] = str(tmp_path_factory.mktemp("dossier") / "q.db")
    os.environ.setdefault("QRME_LLM", "stub")
    db.reset()
    report = seed.seed()
    yield report
    db.reset()
    if old is not None:
        os.environ["QRME_DB"] = old
    else:
        os.environ.pop("QRME_DB", None)


def test_seed_installs_every_dossier(seeded):
    assert seeded["dossiered"] == len(ALL_HANDLES), seeded["dossiered_handles"]


def test_a_starter_carries_knowledge_skills_and_connections(seeded):
    """The three questions, answered from the database for every starter:
    what do you know, what can you do, who do you work with."""
    from qrme import db

    conn = db.connect()
    for handle in ALL_HANDLES:
        pid = conn.execute("SELECT profile_id FROM handles WHERE handle=?",
                           (handle,)).fetchone()["profile_id"]
        titles = {r["title"] for r in conn.execute(
            "SELECT title FROM source_items WHERE profile_id=?",
            (pid,)).fetchall()}
        for title in dossiers.TITLES:
            assert title in titles, f"{handle} is missing {title!r}"
        tags = json.loads(conn.execute(
            "SELECT tags FROM marketplace WHERE profile_id=?",
            (pid,)).fetchone()["tags"])
        assert len(tags) >= 8, (
            f"{handle} shows {len(tags)} skill chips — the dossier should "
            "have widened them")
        # Not a count. The first draft asserted `friends >= 2`, and an
        # injection that removed the colleague loop entirely stayed green —
        # the two founder profiles alone satisfy a floor of two. The question
        # that matters is whether *these* colleagues are friends.
        #
        #     asked     does the starter have two friends
        #     mattered  are the named colleagues among them
        friend_ids = {r["friend_id"] for r in conn.execute(
            "SELECT friend_id FROM friendships WHERE profile_id=? AND"
            " state='active'", (pid,)).fetchall()}
        for colleague in dossiers.DOSSIERS[handle]["colleagues"]:
            cpid = conn.execute(
                "SELECT profile_id FROM handles WHERE handle=?",
                (colleague,)).fetchone()["profile_id"]
            assert cpid in friend_ids, (
                f"{handle} names {colleague} as a colleague and the graph "
                "does not show the friendship")


def test_the_knowledge_reaches_the_prompt(seeded):
    """Installed is not spoken. The persona renders ``sources[:8]``; the pack
    takes three seats and the dossier three, so all of it must fit — and a
    distinctive phrase from the dossier must actually appear in the prompt
    the model is handed."""
    from qrme import db, persona

    conn = db.connect()
    pid = conn.execute("SELECT profile_id FROM handles WHERE handle=?",
                       ("marcus_bell",)).fetchone()["profile_id"]
    profile = dict(conn.execute("SELECT * FROM profiles WHERE id=?",
                                (pid,)).fetchone())
    sources = [dict(r) for r in conn.execute(
        "SELECT * FROM source_items WHERE profile_id=? ORDER BY created_at",
        (pid,)).fetchall()]
    assert len(sources) <= 8, (
        f"{len(sources)} sources — past the prompt budget, so something "
        "written would go unspoken")
    prompt = persona.build_system_prompt(profile, None, None,
                                         sources=sources)
    assert "fee-only financial planning" in prompt, (
        "the expertise dossier did not reach the prompt")
    assert "Harold Jenkins" in prompt, (
        "the colleague graph did not reach the prompt — 'who are your "
        "connections' would be answered from tone")


def test_the_friendship_is_mutual(seeded):
    """Referrals go both ways in the graph, as they do in the prose."""
    from qrme import db

    conn = db.connect()
    pid = {h: conn.execute("SELECT profile_id FROM handles WHERE handle=?",
                           (h,)).fetchone()["profile_id"]
           for h in ("marcus_bell", "harold_jenkins")}
    for a, b in ((pid["marcus_bell"], pid["harold_jenkins"]),
                 (pid["harold_jenkins"], pid["marcus_bell"])):
        row = conn.execute(
            "SELECT 1 FROM friendships WHERE profile_id=? AND friend_id=?"
            " AND state='active'", (a, b)).fetchone()
        assert row is not None, "the referral only went one way"


def test_reseeding_adds_nothing_twice(seeded):
    """Idempotent by title, tag and friendship — a second seed press must
    not stack dossiers."""
    from qrme import db

    again = seed.seed()
    assert again["dossiered"] == 0, again["dossiered_handles"]
    conn = db.connect()
    pid = conn.execute("SELECT profile_id FROM handles WHERE handle=?",
                       ("dr_amara_osei",)).fetchone()["profile_id"]
    n = conn.execute(
        "SELECT COUNT(*) AS n FROM source_items WHERE profile_id=? AND"
        " title=?", (pid, dossiers.TITLES[0])).fetchone()["n"]
    assert n == 1, f"{n} copies of the expertise item after re-seeding"
