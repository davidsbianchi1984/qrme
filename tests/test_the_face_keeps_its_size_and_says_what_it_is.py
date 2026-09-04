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
    assert CHAT.count("<TalkMark avatar={talkAvatar}") == 2, (
        "both avatar forms — the circular face and the standing torso — "
        "have to carry it; a mark on one of two is a mark somebody can get "
        "a face without")
    assert ".talk-wm" in CSS, "the mark has no styling, so it is not legible"


def test_the_mark_does_not_repeat_the_name_printed_under_it():
    """The default designation is "✦ AI · <name>", and `.talk-name` prints
    that name two lines below the face. On the picture it wrapped to two
    lines and covered the chin to say a second time what the screen had
    already said — "he doesn't need to show the name twice".

        asked     does the picture carry the mark
        mattered  does the picture carry anything the screen has not said

    Only the trailing " · <name>" comes off, and only when it is the name
    beside it: a designation an owner wrote themselves keeps every word."""
    assert 'wm.label || "").split(" · ")[0]' in CHAT, (
        "the band draws the whole watermark line again, so the picture "
        "repeats the name printed under it")
    assert "session.profile?.display_name" not in CHAT.split(
        "function earTroubleLine")[0], (
        "the trim reads a name off the session, which a resumed console "
        "does not carry — that version trimmed nothing and shipped")


def test_the_face_is_introduced_by_more_than_a_name():
    """Asked for: "I think there should be a profession under the name."
    The profile carries the field it works in and every other surface that
    lists profiles shows it; the one surface you actually talk to did not."""
    assert 'className="talk-trade"' in CHAT, (
        "the talk surface names the profile and never says what it does")
    assert "p.job_title" in CHAT, (
        "the face says which field but never which job — the position is "
        "the half a person choosing between thirty faces reads")
    assert "api.getProfile(pid)" in CHAT and "p.industry" in CHAT, (
        "the line under the name is not read from the profile's own field "
        "through the profile door — `session.profile` is absent on a "
        "console resumed from storage, which is most of them")
    assert ".trade {" in CSS, "the trade line has no styling"


def test_the_badge_is_one_badge_everywhere():
    """"Make that standard across everybody's profile that requires a
    badge." The talk face, the room seat and the full-screen stage each had
    their own — one a bottom band, one a 7px tint, one a grey pill — so the
    same fact about the same kind of profile looked like three different
    facts. The look is `.ai-pill` now and the surfaces set only size and
    corner.

        asked     does the picture carry a badge
        mattered  does a reader have to learn it more than once"""
    assert ".ai-pill {" in CSS, "there is no shared badge to be standard on"
    wearers = {"screens/Chat.tsx": 1, "AvatarStage.tsx": 1,
               "screens/Inside.tsx": 3, "screens/Discover.tsx": 1,
               "screens/Circle.tsx": 1}
    for path, count in wearers.items():
        text = (APP / path).read_text(encoding="utf-8")
        assert text.count('"ai-pill ') == count, (
            f"{path} draws a mark on a profile that is not the standard "
            f"badge (expected {count}, found {text.count(chr(34) + 'ai-pill ')})")


def test_the_card_badge_cannot_swallow_the_face_again():
    """The AI mark moved back onto the card's picture, which is where it was
    before a field report showed a pill swallowing the face once a phone's
    font boosting inflated its 9px text.

    Moving it back without answering that report would be reintroducing the
    defect, so both halves are pinned: the text refuses boosting, and the
    pill hangs off a corner so what growth remains goes outward. This is
    the assertion that neither is quietly dropped."""
    rule = _rule(".dc-ai")
    assert "text-size-adjust: none" in rule, (
        "the card badge can be inflated by a phone's font boosting — the "
        "exact thing that got it moved off the picture the first time")
    assert "position: absolute" in rule and "right:" in rule, (
        "the badge is not hung off a corner, so anything that does grow "
        "it grows it across the face")


def test_the_trade_is_drawn_by_one_component_everywhere():
    """"That needs to be implemented across the board." A line copied onto
    four screens is four lines that will disagree, so the talk surface, the
    pool card, the circle card and the friends row all draw the same
    component, and the room's seat has carried its own `role` line since it
    was built."""
    shared = (APP / "Trade.tsx").read_text(encoding="utf-8")
    assert "export function Trade(" in shared and "tradeOf" in shared
    assert "trade-job" in shared and "trade-field" in shared, (
        "the shared component draws one of the two lines, so a screen "
        "wanting both would go back to writing its own")
    users = ["screens/Chat.tsx", "screens/Discover.tsx",
             "screens/Circle.tsx", "screens/Friends.tsx"]
    missing = [u for u in users
               if 'from "../Trade"' not in (APP / u).read_text(encoding="utf-8")]
    assert not missing, (
        f"these draw a profile and do not draw its trade: {missing}")


def test_the_share_menu_opens_before_the_talk_control():
    """Asked for: the row ran out of room on a phone with the plus last."""
    plus = CHAT.index('className="agent-plusbtn"')
    toggle = CHAT.index('tr("chat.talk.again", lang)')
    assert plus < toggle, (
        "the share button still renders after the talk control; it was "
        "asked to sit before it")
