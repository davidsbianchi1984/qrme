"""The second ring, and the screen the avatar takes when it is tapped.

The owner's brief, across three messages: a second circle beside the
portrait, bound to the avatar — "you can click either one" — and the tap
opens the render full screen "just like uploading a photo as the
background", with a rail of hidden windows down the edge: the prompt, the
wardrobe, the body. In the AR and VR rooms the figure stands in the
environment rather than on a black card. And the people a profile talks
with may restyle it — on by default, the owner's switch to close.

These are markup guards in the house style: the screens are read as text,
because a binding that no screen calls is the defect this suite exists to
find, and a control that exists only in a commit message is the same
defect one layer up.
"""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STAGE = (REPO / "app" / "src" / "AvatarStage.tsx").read_text()
INSIDE = (REPO / "app" / "src" / "screens" / "Inside.tsx").read_text()
CHAT = (REPO / "app" / "src" / "screens" / "Chat.tsx").read_text()
IDENTITY = (REPO / "app" / "src" / "screens" / "Identity.tsx").read_text()


def test_the_deck_is_on_the_screen_people_actually_open():
    """The defect a whole deploy night found: a component full of
    finished features that nothing mounted. Asserting markup inside a
    file proves the file, not the product — so the defaults grid, the
    one-tap claim, the operator's pull and the provider-id box must
    live in Identity.tsx, a screen the shell actually routes to."""
    for needle in ("idn.deck.defaults", "claimFace", "pullShelf",
                   "idn.deck.pid.ph", "shelf-grid"):
        assert needle in IDENTITY, f"Identity lost {needle}"


def test_the_ring_stands_on_the_seats_and_the_chat_header():
    # The room: a profile seat with a portrait carries the TWIN circles —
    # "no clear circles... I meant an entire profile photo circle, but
    # for avatar" — the portrait opening the picture big, the avatar
    # opening the stage. The small ring survives only where full-bleed
    # pixels or an empty seat leave the pair no room.
    assert "rs-pair" in INSIDE
    assert "face-light" in INSIDE, "the portrait circle lost its lightbox"
    assert "rs-avring" in INSIDE
    assert "AvatarStage" in INSIDE
    # A pair is two whole 72px circles, not a circle and a 34px badge:
    # the avatar circle must be drawn in the seat's own face class, and
    # the badge class must not appear inside the pair block.
    pair = INSIDE.split('className="rs-pair"')[1].split("</div>")[0]
    assert "rs-avring" not in pair
    assert "rs-photo" in pair
    # The direct chat's header wears the ring, opening the same stage.
    assert "chat-head-ring" in CHAT
    assert "AvatarStage" in CHAT


def test_the_stage_is_a_rail_of_hidden_windows():
    # The three windows and the wheel — prompt, wardrobe, body — each a
    # filter over the same card, never a second painting system.
    for key in ("stage.prompt", "stage.ward", "stage.body", "stage.wheel"):
        assert key in STAGE, f"the rail lost {key}"
    assert STAGE.count("api.paintFace") == 1, (
        "every wardrobe road must pass the one painting door")


def test_the_figure_stands_in_the_environment():
    # The whole figure when the platform holds one; and in AR/VR rooms the
    # scene shows through instead of a black takeover.
    assert "torso" in STAGE
    assert "standing" in STAGE
    assert '"ar"' in INSIDE.split("AvatarStage")[1][:400] or \
        "channel === \"ar\"" in INSIDE, (
        "the AR room's stage no longer clears to the environment")


def test_the_wardrobe_says_who_it_opens_for():
    # The visitor with a closed wardrobe reads the sentence; the owner
    # holds the switch, wired to the profile PATCH.
    assert "ward.locked" in STAGE
    assert "ward.guests" in STAGE
    assert "guest_styling" in STAGE
    assert "editProfile" in STAGE
