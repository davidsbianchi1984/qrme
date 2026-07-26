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
    assert out["grounded"] == 33          # all but the rated one; see below

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
    assert len(_sources(marcus["id"])) <= 4


def test_the_rated_starter_is_left_alone(client):
    """There is no adult-industry Field Pack, and inventing a substitute would
    be putting words in a profile the age wall exists to contain."""
    _seeded(client)
    vivienne = _profile("Vivienne Sable")
    assert vivienne["adult_mode"] == 1
    assert list(_sources(vivienne["id"])) == []


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
    assert titles == ["my own notes"]


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
    assert list(_sources(marcus["id"])) == []

    client.post("/packs/seed")
    out = client.post("/marketplace/seed").json()
    assert out["created"] == 0                # nothing new
    assert out["grounded"] == 33              # but everything grounded
    assert len(_sources(marcus["id"])) == 3


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
    assert list(_sources(marcus["id"])) == []
    assert "marcus_bell" not in out["grounded_handles"]
    # Everyone whose pack is still free is unaffected.
    assert out["grounded"] == 32
