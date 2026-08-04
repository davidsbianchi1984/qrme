"""Starters arrive knowing something.

`qrme/packs.py` describes the starter packs as *"one free Field Pack per
industry, matching the Starter Collection"* — and the pairing was never wired.
All 34 starters shipped with **zero source material** while 37 packs sat in the
marketplace, so a physician persona answered from tone alone.

The interesting assertions are the ones about *not* pushing material onto a
profile whose owner has made a decision about it.
"""

from qrme import db


def _seeded(client):
    """Packs first — grounding can only install what exists."""
    client.post("/packs/seed")
    return client.post("/marketplace/seed").json()


def _sources(profile_id):
    return db.connect().execute(
        "SELECT * FROM source_items WHERE profile_id=? ORDER BY rowid",
        (profile_id,)).fetchall()


def _profile(name):
    return dict(db.connect().execute(
        "SELECT * FROM profiles WHERE display_name=?", (name,)).fetchone())


# -- the grounding itself ----------------------------------------------------

def test_every_starter_gets_its_own_industry_pack(client):
    out = _seeded(client)
    assert out["grounded"] == 34          # every starter, the rated one included

    rows = db.connect().execute(
        "SELECT p.id, p.display_name, COUNT(s.id) n FROM profiles p"
        " LEFT JOIN source_items s ON s.profile_id=p.id"
        " WHERE p.adult_mode=0 GROUP BY p.id").fetchall()
    assert rows and all(r["n"] > 0 for r in rows), \
        [r["display_name"] for r in rows if not r["n"]]


def test_the_material_matches_the_persona(client):
    """The whole point: a finance persona gets finance material, not whatever
    pack happened to sort first."""
    _seeded(client)
    marcus = _profile("Marcus Bell")
    titles = " ".join(s["title"] for s in _sources(marcus["id"]))
    assert "Finance" in titles

    sana = _profile("Dr. Sana Iqbal")
    titles = " ".join(s["title"] for s in _sources(sana["id"]))
    assert "Climate" in titles or "Sustainability" in titles


def test_the_pack_actually_reaches_the_prompt(client):
    """Source material that never gets rendered is material the specialist
    does not have."""
    from qrme import persona
    from qrme.common import source_items

    _seeded(client)
    marcus = _profile("Marcus Bell")
    sources = source_items(marcus["id"], None)
    system = persona.build_system_prompt(marcus, None, None, sources=sources)
    assert "Finance Field Pack" in system
    # And it is rendered as knowledge, under this profile's own label.
    assert "[pack]" in system


def test_one_pack_leaves_room_in_the_prompt_budget(client):
    """`build_system_prompt` renders `sources[:8]`. Installing one pack per
    starter uses three of that, so an owner adding their own material is not
    immediately competing with the grounding."""
    _seeded(client)
    marcus = _profile("Marcus Bell")
    # Three pack items and, since 0.42.1, the three dossier items — six of
    # the eight seats, with two still left for an owner's own material.
    assert len(_sources(marcus["id"])) == 6


def test_the_rated_starter_is_grounded_like_every_other(client):
    """She used to be the only starter with no source material at all.

    The old rule read "there is no adult-industry Field Pack, and inventing a
    substitute would be putting words in a profile the age wall exists to
    contain" — which ran two things together. The wall gates *who may talk to
    her*; it was never a reason for her to know less about her own subject.
    The Cabaret & Burlesque Field Pack is theatre history and stagecraft, free
    and unrated like the other thirty-three, and it reaches her through exactly
    the same path.
    """
    _seeded(client)
    vivienne = _profile("Vivienne Sable")
    assert vivienne["adult_mode"] == 1          # still age-walled
    titles = [s["title"] for s in _sources(vivienne["id"])]
    # The pack, and since 0.42.1 her dossier — grounded like every other
    # starter in both halves.
    assert len(titles) == 6
    assert sum(t.startswith("Cabaret & Burlesque Field Pack")
               for t in titles) == 3
    assert "What I know" in titles and "Skills and services" in titles


def test_her_pack_is_history_and_craft_not_content(client):
    """The wall is on the conversation, not on the reading list. If this pack
    ever drifts toward explicit material it stops being grounding and becomes
    the thing the wall exists for."""
    _seeded(client)
    rows = _sources(_profile("Vivienne Sable")["id"])
    body = " ".join(f'{s["title"]} {s["content"]}' for s in rows)
    assert "Ziegfeld" in body and "Folies" in body and "timing" in body.lower()


def test_the_two_adult_packs_are_not_the_same_pack(client):
    """One grounds her for free; the other is $6.99 commerce for any adult-mode
    persona. Conflating them is how a duplicate gets shipped."""
    from qrme.packs import RATED_PACK, STARTER_PACKS
    assert STARTER_PACKS["adult"][0] == "Cabaret & Burlesque Field Pack"
    assert RATED_PACK[1] == "After Dark Companion Pack"
    assert RATED_PACK[0] == "after_dark"        # a different industry key
    assert RATED_PACK[2] > 0                    # and priced, so never auto-installed


# -- not pushing material onto somebody's decision ---------------------------

def test_reseeding_does_not_install_twice(client):
    _seeded(client)
    before = db.connect().execute(
        "SELECT COUNT(*) n FROM source_items").fetchone()["n"]
    again = client.post("/marketplace/seed").json()
    after = db.connect().execute(
        "SELECT COUNT(*) n FROM source_items").fetchone()["n"]
    assert again["grounded"] == 0
    assert after == before


def test_an_owner_who_added_their_own_material_is_not_topped_up(client):
    """Blank-only, the same rule the portrait backfill follows. A profile with
    material has an owner who has made a decision about it."""
    client.post("/marketplace/seed")      # the old world: starters, no packs
    client.post("/packs/seed")
    marcus = _profile("Marcus Bell")

    # This owner wrote their own material before the grounding ever ran.
    conn = db.connect()
    conn.execute(
        "INSERT INTO source_items (id, profile_id, kind, title, content,"
        " pdi_key, pack_id, created_at) VALUES (?,?,?,?,?,NULL,NULL,?)",
        (db.new_id("src"), marcus["id"], "writing", "my own notes",
         "What I actually think about index funds.", db.utcnow()))
    conn.commit()

    out = client.post("/marketplace/seed").json()
    assert marcus["display_name"] not in out["grounded_handles"]
    titles = [s["title"] for s in _sources(marcus["id"])]
    # The pack stayed out — that is the decision being respected. The three
    # dossier items were already installed by the *first* seed, before the
    # owner wrote anything, so nothing was pushed onto their decision; what
    # matters is that re-seeding added no pack and no duplicates.
    assert "my own notes" in titles
    assert not any("Field Pack" in t for t in titles), titles
    assert len(titles) == 4, titles


def test_an_owner_who_removed_the_pack_does_not_get_it_back(client):
    """Uninstalling is a decision too. Re-seeding must not undo it — which is
    the same property, reached from the other direction."""
    _seeded(client)
    marcus = _profile("Marcus Bell")
    conn = db.connect()
    conn.execute("DELETE FROM source_items WHERE profile_id=?",
                 (marcus["id"],))
    conn.execute(
        "INSERT INTO source_items (id, profile_id, kind, title, content,"
        " pdi_key, pack_id, created_at) VALUES (?,?,?,?,?,NULL,NULL,?)",
        (db.new_id("src"), marcus["id"], "writing", "a note", "x",
         db.utcnow()))
    conn.commit()

    client.post("/marketplace/seed")
    assert [s["title"] for s in _sources(marcus["id"])] == ["a note"]


def test_no_packs_seeded_means_no_grounding_and_no_error(client):
    """A deployment that seeds the collection without seeding packs still
    works — it just has ungrounded starters, as before."""
    out = client.post("/marketplace/seed").json()
    assert out["created"] == 34
    assert out["grounded"] == 0


# -- the repair path ---------------------------------------------------------

def test_a_deployment_seeded_before_this_gets_grounded_on_rerun(client):
    """Every existing deployment has 34 starters with nothing. They cannot be
    fixed by hand at that count, so the repair path has to carry it — the same
    route the missing portraits took."""
    client.post("/marketplace/seed")          # the old world: no packs yet
    marcus = _profile("Marcus Bell")
    # The dossier needs no pack, so it lands even in the packless world —
    # three items where there used to be none.
    titles = [s["title"] for s in _sources(marcus["id"])]
    assert len(titles) == 3 and not any("Field Pack" in t for t in titles)

    client.post("/packs/seed")
    out = client.post("/marketplace/seed").json()
    assert out["created"] == 0                # nothing new
    assert out["grounded"] == 34              # but everything grounded
    # The pack, and the dossier that rides the same repair path.
    assert len(_sources(marcus["id"])) == 6


# -- money -------------------------------------------------------------------

def test_grounding_is_free_and_credits_nobody(client):
    """A deployment grounding its own starters is not a purchase. A priced
    pack stays a decision for whoever owns the profile."""
    _seeded(client)
    conn = db.connect()
    paid = conn.execute(
        "SELECT COALESCE(SUM(price_paid), 0) t FROM pack_installs"
    ).fetchone()["t"]
    assert paid == 0

    entries = conn.execute(
        "SELECT COUNT(*) n FROM ledger WHERE kind='pack_sale'"
    ).fetchone()["n"]
    assert entries == 0


def test_a_priced_pack_is_never_auto_installed(client):
    """Grounding must not spend on an owner's behalf. All the *seeded* Field
    Packs are free, so this makes one cost money — otherwise the guard is
    real and nothing exercises it."""
    client.post("/packs/seed")
    conn = db.connect()
    conn.execute(
        "UPDATE knowledge_packs SET price=1200 WHERE industry='finance'"
        " AND audience='profile'")
    conn.commit()

    out = client.post("/marketplace/seed").json()
    marcus = _profile("Marcus Bell")
    # No pack was bought on the owner's behalf. The dossier still arrives —
    # it is the deployment's own writing, not a purchase.
    titles = [s["title"] for s in _sources(marcus["id"])]
    assert not any("Field Pack" in t for t in titles), titles
    assert "What I know" in titles
    assert "marcus_bell" not in out["grounded_handles"]
    # Everyone whose pack is still free is unaffected.
    assert out["grounded"] == 33
