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


def test_the_seat_is_one_face_with_four_roads_beside_it():
    """The twin circles are gone, and that was the correction.

    A seat used to carry two whole circles — the portrait opening the
    picture and a second one opening the stage — and the owner's reply to
    it was four words: "I don't like the way it looks." A person is ONE
    face. The formats are things you can DO with them, and things you can
    do belong beside the face rather than competing with it for the
    middle of the tile.

    So: one portrait, which still opens the picture big, and the road
    glyphs stacked straight down its right. Two when this was written —
    the avatar and the film — and four now that AR and VR moved out of
    their own "step in" button and onto the seat, in the same column:
    "VR and AR will become glyph next to video and avatar... straight up
    and down." What this guard protects is that no road is quietly
    dropped and that the portrait keeps its lightbox.
    """
    assert "rs-circle-btn rs-solo" in INSIDE, (
        "the seat lost its single portrait circle")
    assert "face-light" in INSIDE, "the portrait circle lost its lightbox"
    assert "rs-pair" not in INSIDE, (
        "the twin circles are back — a person is one face")
    assert "AvatarStage" in INSIDE

    # All four roads, on the seat, each pressing into a format.
    roads = INSIDE.split('className="rs-side"')[1].split("</div>")[0]
    assert roads.count('className={"rs-road"') == 4, (
        "a seat carries four roads: the avatar, the film, AR and VR")
    for fmt in ('"avatar"', '"video"', '"ar"', '"vr"'):
        assert fmt in roads, f"the {fmt} road is not on the seat"

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
