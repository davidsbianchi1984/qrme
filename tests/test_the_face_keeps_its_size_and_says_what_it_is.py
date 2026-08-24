"""The talking face keeps its size, and says what it is.

Opening any of the four panels beside the talk overlay made the avatar a
little flatter, and opening four made it a slit. The overlay is a column
flex container; `.talk-face` was given a width and a height and nothing
else, and in a column the main axis is the *vertical* one — so `flex-shrink`
defaults to 1 and applies to exactly the dimension that was supposed to be
fixed. Every panel that opened took its room out of the one child willing to
give it.

    asked     is the face given a size
    mattered  can anything take it back

A fixed width and height are not a size unless the box is also told not to
lend them out. Nothing reported it because nothing was measuring it: the
face got smaller by the amount the layout needed, which is always exactly
enough to avoid an overflow anybody would have noticed.

## The mark

`Avatar.watermark` carries the designation line and the type calls it
"always displayed, by the product's own rule". The talk overlay showed the
face at its largest, mid-conversation, and displayed it nowhere — the screen
where a synthetic person is most convincing was the one screen not saying
so. In a product whose subject is exactly that, an unmarked talking face is
not a cosmetic gap.
"""

import re
from pathlib import Path


def _repo() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


APP = _repo() / "app" / "src"
CSS = (APP / "styles.css").read_text(encoding="utf-8")
CHAT = (APP / "screens/Chat.tsx").read_text(encoding="utf-8")


def _rule(selector: str) -> str:
    m = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", CSS)
    assert m, f"no CSS rule for {selector}"
    return m.group(1)


def test_the_face_does_not_lend_its_height_to_the_panels_below_it():
    """The defect, directly: a sized box in a column flex container that has
    not been told to keep what it was given."""
    missing = [sel for sel in (".talk-face", ".talk-torso", ".talk-torso-wrap")
               if not re.search(r"flex:\s*0\s+0\s+auto|flex-shrink:\s*0",
                                _rule(sel))]
    assert not missing, (
        "these sit in the talk overlay's column and can still be shrunk by "
        f"anything opened below them: {missing}")


def test_the_overlay_scrolls_rather_than_squeezing():
    """Where the fixed sizes no longer fit, the column has to put the extra
    somewhere. Scrolling is somewhere; the face is not."""
    rule = _rule(".talk-overlay")
    assert "overflow-y: auto" in rule, (
        "the talk overlay cannot scroll, so content taller than the screen "
        "has nowhere to go but into its children's height")
    assert "safe center" in rule, (
        "plain `center` with a scrollbar can put the top of the column out "
        "of reach — the close button is up there")


def test_the_talking_face_carries_its_designation():
    """`Avatar.watermark` is documented as always displayed. This is the
    screen that was not displaying it."""
    assert "function TalkMark(" in CHAT, "the talk overlay has no mark to draw"
    assert "avatar.watermark" in CHAT, (
        "the mark is not read from the avatar's own watermark, so a "
        "customised designation would not reach this screen")
    assert CHAT.count("<TalkMark avatar={talkAvatar} />") == 2, (
        "both avatar forms — the circular face and the standing torso — "
        "have to carry it; a mark on one of two is a mark somebody can get "
        "a face without")
    assert ".talk-wm" in CSS, "the mark has no styling, so it is not legible"


def test_the_share_menu_opens_before_the_talk_control():
    """Asked for: the row ran out of room on a phone with the plus last."""
    plus = CHAT.index('className="agent-plusbtn"')
    toggle = CHAT.index('tr("chat.talk.again", lang)')
    assert plus < toggle, (
        "the share button still renders after the talk control; it was "
        "asked to sit before it")
