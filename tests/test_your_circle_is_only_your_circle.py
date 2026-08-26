"""Your circle is only your circle.

Field direction, mid-build and overriding the first cut: *"I don't think
when a user wants to view his friends we should be showing ones that
aren't his friends and offering to add them."* The first cut had pointed
"See all" at Discover — everybody on the deployment, described, with an
offer on every card.

    asked     show me all my friends, and what they do
    mattered  the only screens that said what anybody does also
              offered strangers

So the circle is its own screen: friends only, in the descriptive card
style, and no add button anywhere — everybody here has already been
added. The one door out is on the empty state, where Discover is exactly
the right answer.
"""

from __future__ import annotations

import re
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "app" / "src"
CIRCLE = (SRC / "screens" / "Circle.tsx").read_text(encoding="utf-8")
HOME = (SRC / "screens" / "Home.tsx").read_text(encoding="utf-8")
DISCOVER = (SRC / "screens" / "Discover.tsx").read_text(encoding="utf-8")
APP = (SRC / "App.tsx").read_text(encoding="utf-8")


def _stripped(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"^\s*//.*$", "", text, flags=re.M)


def test_the_circle_offers_nothing():
    """No add button, no befriend, no storefront verbs. A screen of people
    you already have does not sell you people."""
    code = _stripped(CIRCLE)
    for verb in ("befriend", "addFriend", "dsc.addfriend"):
        assert verb not in code, (
            f"`{verb}` is in the circle — an offer on a screen that is "
            "supposed to hold only what was already accepted")


def test_the_circle_is_built_from_the_friends_list():
    """Friends in, everything else joined on — never the pool filtered
    down, which would quietly show the pool when the filter broke."""
    code = _stripped(CIRCLE)
    assert "api.friends(" in code, "the circle does not read the friends list"
    assert "mine.friends.map" in code, (
        "the rows are not mapped from the friends list itself")


def test_see_all_opens_the_circle_not_the_shop():
    code = _stripped(HOME)
    m = re.search(r'hom\.seeall.*', code, re.S)
    assert m, "the See all door is gone from the homepage"
    assert 'go("circle")' in code, (
        "See all does not open the circle")
    assert code.index('go("circle")') < code.index("hom.seeall"), (
        "the See all press does not go to the circle — read the button")


def test_the_circle_is_reachable():
    code = _stripped(APP)
    assert 'tab === "circle"' in code, "nothing renders the circle"
    assert "<Circle" in code, "the circle is imported and never drawn"


def test_the_storefront_says_friends_on_a_friends_card():
    """The second half of the same field report: Discover offered "Add
    friend" to people already added. The label is the state."""
    code = _stripped(DISCOVER)
    assert "pals.has(c.profile_id)" in code, (
        "the storefront no longer checks who is already a friend")
    assert "dsc.friends" in code, (
        "an added friend's card has no state label")


def test_a_fresh_add_flips_the_card_without_a_reload():
    code = _stripped(DISCOVER)
    body = re.search(r"async function befriend\(.*?\n  \}", code, re.S)
    assert body, "befriend moved — this guard reads it by name"
    assert "setPals" in body.group(0), (
        "a card still offers to add somebody who was just added")
