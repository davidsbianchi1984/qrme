"""The 2.9.7 widening: every worn thing in America can be added, and every
addition answered its questions the day it landed.

    asked     offer all the ones that are available in America — AR, VR,
              watches, rings, pendants, and ankle monitors, and any others
    mattered  a kind in the menu with an unanswered question is a dead end
              somebody finds at the moment they try to use it

Three tables now describe a kind: KINDS says it exists and where it is
worn, SCREENS says whether the console can show itself on it, CATALOG says
what people actually own. These tests hold the three together — a kind in
one table and missing from another is the gap each one guards against.
The microphone question has its own guard in tests/test_room_mic.py.
"""

from __future__ import annotations

from qrme import wearables


def test_every_kind_has_a_catalog_row_even_an_empty_one():
    """An absent row and an empty row read the same to a client and mean
    different things to a maintainer: absent is a kind nobody thought
    about, empty is a decision that no menu is worth offering. Every kind
    gets a row so the difference stays visible here."""
    missing = set(wearables.KINDS) - set(wearables.CATALOG)
    assert not missing, (
        f"kinds nobody wrote a catalogue decision for: {sorted(missing)}")


def test_the_catalog_names_only_kinds_that_exist():
    stray = set(wearables.CATALOG) - set(wearables.KINDS)
    assert not stray, (
        f"catalogue rows for kinds that cannot be paired: {sorted(stray)}")


def test_a_screen_is_a_fact_about_a_pairable_kind():
    stray = set(wearables.SCREENS) - set(wearables.KINDS)
    assert not stray, (
        f"screens claimed for kinds that cannot be paired: {sorted(stray)}")
    refused = set(wearables.SCREENS) & set(wearables.REFUSED)
    assert not refused, (
        "a refused device class cannot also be a render surface: "
        f"{sorted(refused)}")


def test_the_asked_for_kinds_are_all_in_the_menu():
    """The list from the field, verbatim: AR, VR, watches, rings, pendants,
    ankle monitors. Each one pairable, none quietly dropped."""
    for kind in ("ar_glasses", "vr_headset", "watch", "ring", "pendant",
                 "ankle_monitor"):
        assert kind in wearables.KINDS, f"{kind} fell out of the menu"


def test_the_eyes_covering_kinds_are_render_surfaces():
    """The whole point of pairing a headset to a product with a room's
    stage. A VR headset or AR glasses that pair as presence alone is the
    dead end the widening exists to remove."""
    for kind in ("vr_headset", "ar_glasses"):
        assert kind in wearables.SCREENS, f"{kind} has no surface"


def test_the_limit_stays_above_the_menu():
    """MAX_WEARABLES's own comment makes the promise; this holds it: a
    limit below the catalogue is a rule that contradicts the menu it is
    printed next to."""
    assert wearables.MAX_WEARABLES > len(wearables.KINDS), (
        f"{len(wearables.KINDS)} kinds and a limit of "
        f"{wearables.MAX_WEARABLES} — somebody owning one of each "
        "cannot add a second watch")
