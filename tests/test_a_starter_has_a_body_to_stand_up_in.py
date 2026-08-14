"""Every starter has a face; none of them had a body.

Thirty-five portraits ship under ``/portraits`` — one per handle, marked and
checksummed. ``avatar_torsos`` had no row for any of them, and `torso_of`
returned None for all thirty-four, so on a surface that stands the avatar up
at full figure every starter fell back to a circular face or an orb.

    asked     does a starter have a face
    mattered  does it have a body to stand up in

The import shelf cannot close it: bringing a skin from Ready Player Me is an
owner's move, and nobody owns Dr. Osei. What ships with the product has to
ship with the product.
"""

from __future__ import annotations

from qrme import avatars, skins


def test_every_starter_with_a_portrait_has_a_pose():
    """The two collections move together or the figure round quietly covers
    thirty of thirty-four and nobody notices which four are missing."""
    missing = sorted(set(avatars.BRIEFS) - set(skins.POSES))
    assert not missing, (
        f"{len(missing)} starter(s) have a portrait brief and no pose:\n    "
        + "\n    ".join(missing))


def test_no_pose_describes_a_starter_that_does_not_exist():
    """The other direction. A pose for a handle nobody has is a line that
    will never be drawn and will never be noticed."""
    extra = sorted(set(skins.POSES) - set(avatars.BRIEFS))
    assert not extra, (
        f"{len(extra)} pose(s) name a starter that is not in the "
        "collection:\n    " + "\n    ".join(extra))


def test_a_figure_brief_carries_the_character_from_the_portrait():
    """Composed, not restated. Two independent descriptions of one person is
    how the picture on the beacon page and the figure in the room end up
    being different people."""
    b = skins.brief("dr_amara_osei")
    assert b is not None
    assert b["character"] == avatars.BRIEFS["dr_amara_osei"]
    # And the prompt a generator receives holds all three parts.
    assert b["character"] in b["prompt"]
    assert b["pose"] in b["prompt"]
    assert b["style"] in b["prompt"]


def test_the_rated_figure_stays_outside_the_cyan_system():
    """Its portrait already does, for a reason that has not changed: it never
    appears in a grid with the others."""
    rated = skins.brief("vivienne_sable")
    assert rated is not None
    assert rated["style"] == skins.RATED_FIGURE_STYLE
    assert rated["style"] != skins.FIGURE_STYLE


def test_the_rated_figure_is_dressed():
    """Age-walled for tone, not for skin. The brief has to say so, because
    the brief is what a generator is handed."""
    rated = skins.brief("vivienne_sable")
    assert "covered" in rated["pose"] or "gown" in rated["pose"]
    assert "dressed" in rated["style"]


def test_no_figure_borrows_a_costume():
    """The same rule the portraits carry, and a standing figure is a bigger
    render than a portrait rather than a lesser one."""
    assert "trademarked costume" in skins.FIGURE_STYLE


def test_a_figure_that_has_not_shipped_is_none_rather_than_a_broken_path():
    """None is a real answer: `render` falls back to the portrait, and a
    surface that wanted a body gets a face instead of a broken image."""
    assert skins.skin_path("nobody_at_all") is None
    for b in skins.catalog():
        # Either a served path under the figures' own route, or nothing.
        assert b["asset"] is None or b["asset"].startswith(skins.SKIN_ROUTE)


def test_the_catalog_covers_the_whole_collection():
    assert len(skins.catalog()) == len(avatars.BRIEFS)


def test_the_collection_can_say_how_much_of_it_is_still_undrawn():
    """A surface that wants bodies should be able to ask rather than discover
    it one starter at a time. Today the answer is all of them, and that is
    the honest state rather than a failure."""
    undrawn = skins.missing()
    assert set(undrawn) <= set(avatars.BRIEFS)
    assert len(undrawn) == sum(1 for b in skins.catalog()
                               if b["asset"] is None)


def test_the_figures_have_their_own_route(tmp_path):
    """Not `/figures`, which is interface furniture — the emblems and the
    add-photo frame. Mixing a character render in would put an unburned
    drawing inside a tree whose manifest check walks every file."""
    assert skins.SKIN_ROUTE != avatars.FIGURE_ROUTE
    assert skins.SKIN_ROUTE != avatars.ASSET_ROUTE
    assert skins.SKIN_ROUTE != avatars.PHOTO_ROUTE
