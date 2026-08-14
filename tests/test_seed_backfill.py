"""Re-seeding repairs a starter that predates its portrait.

The seed is idempotent by @handle, and idempotent used to mean "do nothing".
So every deployment created before the portraits shipped was stuck showing
initials on a profile whose face is sitting in the package — and running the
seed again, the obvious repair, did nothing at all.
"""

from qrme import avatars, db, landing, seed as seed_mod
from qrme.seed import seed


def _profile(name):
    return dict(db.connect().execute(
        "SELECT * FROM profiles WHERE display_name=?", (name,)).fetchone())


def test_reseeding_restores_a_missing_portrait(client):
    seed()
    conn = db.connect()
    conn.execute("UPDATE profiles SET avatar=NULL, appearance=''"
                 " WHERE display_name IN ('Marcus Bell','Dr. Sana Iqbal')")
    conn.commit()
    assert _profile("Marcus Bell")["avatar"] is None

    out = seed()
    assert out["created"] == 0                  # still idempotent
    assert out["repaired"] == 2
    assert "marcus_bell" in out["repaired_handles"]
    assert _profile("Marcus Bell")["avatar"] == "/portraits/marcus_bell.webp"
    assert _profile("Marcus Bell")["appearance"]


def test_a_repaired_profile_shows_its_face(client):
    """The screenshot this fixes: three starter cards with no portrait.

    The "before" assertion used to look for `class="initials"`, from when a
    face-less profile fell back to a monogram. It now falls back to the empty
    frame every surface shows — so the check is that the *portrait* is
    missing, which is the thing the backfill repairs, rather than which
    stand-in was drawn in its place.
    """
    seed()
    conn = db.connect()
    conn.execute("UPDATE profiles SET avatar=NULL WHERE display_name='Marcus Bell'")
    conn.commit()

    before = landing.profile_page(_profile("Marcus Bell"), "teller window 4",
                                  "https://example.test")
    assert avatars.ADD_PHOTO in before
    assert "marcus_bell.webp" not in before

    seed()
    after = landing.profile_page(_profile("Marcus Bell"), "teller window 4",
                                 "https://example.test")
    assert "marcus_bell.webp" in after
    assert avatars.ADD_PHOTO not in after


def test_backfill_never_overwrites_what_an_owner_set(client):
    """A repair, not a reset."""
    seed()
    conn = db.connect()
    conn.execute("UPDATE profiles SET avatar='/portraits/mine.webp',"
                 " appearance='my own words' WHERE display_name='Marcus Bell'")
    conn.commit()

    out = seed()
    assert "marcus_bell" not in out["repaired_handles"]
    p = _profile("Marcus Bell")
    assert p["avatar"] == "/portraits/mine.webp"
    assert p["appearance"] == "my own words"


def test_startup_repair_heals_without_the_button(client):
    """The field report: weeks on initials with 34 faces in the package,
    because the repair lived behind a seed button nobody knows is a repair.
    ``seed.repair()`` runs at app startup instead — including for the
    founder's two profiles, which the starter backfill never reaches."""
    seed()
    conn = db.connect()
    conn.execute("UPDATE profiles SET avatar=NULL")
    conn.commit()

    out = seed_mod.repair()
    assert out["repaired"] >= 34
    assert "david_bianchi_ai" in out["repaired_handles"]
    assert "david_bianchi" in out["repaired_handles"]
    assert _profile("Marcus Bell")["avatar"] == "/portraits/marcus_bell.webp"
    # The photographed half comes back from the photo tree, not the portrait
    # tree — repairing it with a burned AI portrait would be the false claim
    # avatars.py exists to prevent. By handle: his two profiles share a
    # display name on purpose, so a name lookup can answer with either.
    row = conn.execute(
        "SELECT p.avatar FROM profiles p JOIN handles h ON h.profile_id=p.id"
        " WHERE h.handle='david_bianchi'").fetchone()
    assert row["avatar"] == "/photos/david_bianchi.webp"


def test_startup_repair_never_installs_the_collection(client):
    """A deployment that chose not to install the starters stays without
    them — repair heals what exists, it does not stock the shelf."""
    before = db.connect().execute("SELECT COUNT(*) AS n FROM profiles").fetchone()["n"]
    out = seed_mod.repair()
    assert out["repaired"] == 0
    after = db.connect().execute("SELECT COUNT(*) AS n FROM profiles").fetchone()["n"]
    assert after == before
