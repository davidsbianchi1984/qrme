"""A robot is another motor on the same wire, and the safety margin is not.

`qrme/robotics.py` has carried a catalogue of bodies for several
releases — platforms, kinds, and a per-kind command allowlist — and none
of it was ever attached to a grant, a reach, a ledger or a refusal. The
hands built all four for screens. Wiring them together is a short
afternoon and the wrong one to have.

    asked     can a profile work a body the way it works a screen
    mattered  what does not carry over

Everything that bounds a screen bounds it because a mis-click is undone
with a keystroke. Four of those bounds mean something different, or
nothing, on something that can move in a room:

    a list of app names          is not a place a body may be
    a step budget                does not say how hard a step is
    a corner of the screen       is not within reach of somebody standing
                                 beside a robot
    the motor's own word         is a restatement of the request, not
                                 evidence that anything happened

So `body` is a surface here, `watching` on one is allowed, and `acting`
is refused with all four named. Shipping the transmit path first and the
envelope afterwards is how the envelope ends up shaped by whatever was
easy to transmit.
"""

from __future__ import annotations

import pytest

from qrme import hands, robotics


def _grant(profile_id, **kw):
    kw.setdefault("surface", "body")
    kw.setdefault("places", ["optimus"])
    kw.setdefault("verbs", ["look"])
    return hands.grant(profile_id, profile_id, **kw)


def test_a_body_is_a_surface_this_product_admits_to(client):
    """A surface a product silently does not support is indistinguishable
    from one it forgot about."""
    assert "body" in hands.SURFACES


def test_moving_a_body_is_refused_and_says_all_four_reasons(client,
                                                            profile_id):
    granted = _grant(profile_id)
    with pytest.raises(hands.HandError) as raised:
        hands.open_reach(profile_id, granted["id"], errand="fetch the post",
                         platform="linux", mode="acting")
    said = raised.value.message
    assert raised.value.status == 403
    for reason in hands.BODY_UNDECIDED:
        assert reason in said, f"the refusal does not mention: {reason}"
    # And it says what it *can* do, so the answer is not just "no".
    assert "watch" in said


def test_watching_through_a_body_is_allowed(client, profile_id):
    """Seeing through a robot and saying what is there carries none of
    the four. Refusing it too would be caution aimed at nothing."""
    granted = _grant(profile_id)
    reach = hands.open_reach(profile_id, granted["id"],
                             errand="what is in the kitchen",
                             platform="linux", mode="watching")
    assert reach["state"] == "open"
    assert reach["surface"] == "body"


def test_the_four_reasons_are_about_bodies_and_not_screens(client):
    """Each one has to be a bound that a screen genuinely does not need,
    or the list is padding and a reader will learn to skim it."""
    said = " ".join(hands.BODY_UNDECIDED)
    assert "app names" in said        # places mean something else here
    assert "force" in said            # a step budget is not a force cap
    assert "stop" in said             # the mouse corner is out of reach
    assert "sensor" in said           # the mover is not a witness
    assert len(hands.BODY_UNDECIDED) == 4


def test_the_catalogue_is_still_the_only_list_of_bodies(client):
    """The bodies a grant can name are the catalogue's, and the commands
    are its per-kind allowlist. A second list would be a second answer to
    the question of what a vacuum can be told to do."""
    assert robotics.COMMANDS["vacuum"] == ["clean", "spot_clean", "patrol",
                                           "dock", "locate", "stop"]
    assert "fetch" not in robotics.COMMANDS["vacuum"]
    # Nothing here has quietly grown a second vocabulary.
    assert "clean" not in hands.VERBS
