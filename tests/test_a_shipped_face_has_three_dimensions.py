"""A model on disk that no surface could ask for is a file, not a face.

`avatars.model_of` read the avatar registry and nothing else. A registry
row is what a *forged* face gets — somebody uploads a photograph, the
forge builds a head, `avatarreg.mint` writes the row. A starter has never
had one: its portrait is found by handle in the asset tree, not by a
lookup. So the collection could ship a `.glb` beside a starter's `.webp`
and every console asking that starter for its model would be told there
wasn't one.

    asked     has somebody forged a face for this profile
    mattered  does this profile have a face in three dimensions

The portrait half of this question has always been answered by looking on
disk. This is the same answer for the other half, and the tests below are
mostly about the parts that are easy to get wrong once a second road
exists: the registry still winning where it answers, a takedown still
meaning gone, and a profile with no model still saying so rather than
guessing.
"""

import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture()
def seeded(monkeypatch):
    monkeypatch.setenv("QRME_DB", tempfile.mkdtemp() + "/models.db")
    from qrme import db, seed
    db.reset()
    db.connect()
    seed.seed()
    yield db.connect()
    db.reset()


def _profile(conn, handle: str) -> str:
    row = conn.execute("SELECT profile_id FROM handles WHERE handle=?",
                       (handle,)).fetchone()
    assert row is not None, f"no profile seeded for @{handle}"
    return row["profile_id"]


def test_the_route_is_its_own_and_not_the_portraits():
    """A `.glb` served from the portrait mount is a model in a tree that
    promises pictures, and the first surface to draw it as an image would
    be right to."""
    from qrme import avatars
    assert avatars.MODEL_ROUTE != avatars.ASSET_ROUTE
    assert avatars.MODEL_ROUTE != avatars.PHOTO_ROUTE
    assert avatars.MODEL_ROUTE != avatars.FIGURE_ROUTE


def test_a_handle_with_a_file_on_disk_has_a_model_path():
    from qrme import avatars
    shipped = sorted(p.stem for p in avatars.models_dir().glob("*.glb")) \
        if avatars.models_dir().is_dir() else []
    if not shipped:
        pytest.skip("this deployment ships no models")
    for handle in shipped:
        assert avatars.model_path(handle) == f"/models/{handle}.glb"


def test_a_handle_with_no_file_says_so_rather_than_guessing():
    """The failure this replaces would have been a 404 in a room."""
    from qrme import avatars
    assert avatars.model_path("nobody_by_this_name") is None


def test_every_shipped_model_belongs_to_a_profile_that_exists(seeded):
    """A `.glb` named for a handle nobody holds is a file that will never
    be served — the same gap `ui_screens.txt` exists to close, one tree
    over."""
    from qrme import avatars
    if not avatars.models_dir().is_dir():
        pytest.skip("this deployment ships no models")
    orphans = [
        p.stem for p in sorted(avatars.models_dir().glob("*.glb"))
        if seeded.execute("SELECT 1 FROM handles WHERE handle=?",
                          (p.stem,)).fetchone() is None
    ]
    assert not orphans, (
        f"models on disk for handles no profile holds: {orphans}")


def test_a_starter_that_ships_a_model_reports_it(seeded):
    from qrme import avatars
    shipped = sorted(p.stem for p in avatars.models_dir().glob("*.glb")) \
        if avatars.models_dir().is_dir() else []
    if not shipped:
        pytest.skip("this deployment ships no models")
    handle = shipped[0]
    got = avatars.model_of(_profile(seeded, handle))
    assert got == f"/models/{handle}.glb"


def test_a_starter_with_no_model_still_reports_none(seeded):
    """The bug this guards is a fallback that answers for everybody."""
    from qrme import avatars
    bare = [h for h in ("marcus_bell", "priya_raman", "elena_vasquez")
            if avatars.model_path(h) is None]
    assert bare, "every candidate ships a model — pick another for this check"
    for handle in bare:
        assert avatars.model_of(_profile(seeded, handle)) is None


def test_the_render_carries_the_model_to_the_surface(seeded):
    """`model_of` being right is worth nothing if `render` drops it: the
    render is the only shape a console ever sees."""
    from qrme import avatars
    shipped = sorted(p.stem for p in avatars.models_dir().glob("*.glb")) \
        if avatars.models_dir().is_dir() else []
    if not shipped:
        pytest.skip("this deployment ships no models")
    drawn = avatars.render(_profile(seeded, shipped[0]))
    assert drawn["model"] == f"/models/{shipped[0]}.glb"
    # The still is still there. A surface that cannot run a model shows
    # the portrait, and losing it would break the fallback rather than
    # the feature — which is the quieter failure of the two.
    assert drawn["asset"]


def test_a_forged_face_is_not_overruled_by_the_shipped_one(seeded):
    """An owner who built their own face keeps it. The shipped model is
    the collection's default, not an override."""
    from qrme import avatars, avatarreg
    shipped = sorted(p.stem for p in avatars.models_dir().glob("*.glb")) \
        if avatars.models_dir().is_dir() else []
    if not shipped:
        pytest.skip("this deployment ships no models")
    profile_id = _profile(seeded, shipped[0])
    minted = avatarreg.mint(asset="/media/theirs.webp", source="uploaded",
                            likeness="invented")
    seeded.execute(
        "UPDATE avatar_registry SET render_variants=? WHERE id=?",
        ('{"portrait": "/media/theirs.webp", "model": "/media/theirs.glb"}',
         minted["id"]))
    seeded.execute("UPDATE profiles SET avatar_ref=? WHERE id=?",
                   (minted["id"], profile_id))
    seeded.commit()
    assert avatars.model_of(profile_id) == "/media/theirs.glb"


def test_a_retired_face_takes_its_model_with_it(seeded):
    """A takedown that left the shipped model showing would be the
    fallback undoing the takedown."""
    from qrme import avatars, avatarreg
    shipped = sorted(p.stem for p in avatars.models_dir().glob("*.glb")) \
        if avatars.models_dir().is_dir() else []
    if not shipped:
        pytest.skip("this deployment ships no models")
    profile_id = _profile(seeded, shipped[0])
    minted = avatarreg.mint(asset="/media/theirs.webp", source="uploaded",
                            likeness="invented")
    seeded.execute("UPDATE profiles SET avatar_ref=? WHERE id=?",
                   (minted["id"], profile_id))
    seeded.execute("UPDATE avatar_registry SET status='retired' WHERE id=?",
                   (minted["id"],))
    seeded.commit()
    assert avatars.model_of(profile_id) is None
