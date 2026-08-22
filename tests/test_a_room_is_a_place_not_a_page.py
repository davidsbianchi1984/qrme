"""A room is a place, not a page.

Field report, twice. The first time: "when you enter a room, you should
leave the homepage and enter a full-blown screen like this second photo
not like the first one" — the second photo being the gallery's own screen
105. The second time, after it had not been built: "the chat becomes the
full screen instead of in a little blue box".

    asked     is the room on screen
    mattered  is the room the screen

Every other screen in this console is a page — a 720px column of cards in
a padded area beside the sidebar. That is right for settings and rosters
and anything a person reads. A room is the one surface that is somewhere
you ARE, and the page treatment made it a postcard of itself: the faces in
a small box, the navigation you arrived through still taking a fifth of
the window.

## What this does not do

It does not call the Fullscreen API and it does not touch a sensor. Those
stay a deliberate press — `immersed` in Inside.tsx — because going
fullscreen and turning a camera on are decisions a person makes rather
than properties a room has. Filling the window with a room somebody
already walked into is not one of those, and conflating the two is how the
first version of this talked itself out of the fix.

## The door

Hiding the sidebar removes the way out, so the room grows its own. A
full-screen place with no door is a trap, and the guard below is mostly
about that: the door exists, it is wired to something that actually
leaves, and it is drawn before anything else in the frame.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
APP = (REPO / "app/src/App.tsx").read_text(encoding="utf-8")
INSIDE = (REPO / "app/src/screens/Inside.tsx").read_text(encoding="utf-8")
CSS = (REPO / "app/src/styles.css").read_text(encoding="utf-8")
L10N = (REPO / "app/src/l10n.ts").read_text(encoding="utf-8")


# -- the room takes the window ----------------------------------------------

def test_the_shell_knows_when_a_room_is_open():
    assert 'const inRoom = tab === "inside" && Boolean(insideRoom);' in APP, (
        "nothing in the shell distinguishes standing in a room from any "
        "other tab, so the room cannot be given the window")
    assert '"app" + (inRoom ? " in-room" : "")' in APP


def test_the_navigation_steps_out_of_the_way():
    block = CSS[CSS.index(".app.in-room"):]
    block = block[:block.index(".screen.room-place")]
    for gone in (".sidebar", ".menu-fab", ".menu-scrim"):
        assert gone in block, (
            f"{gone} still occupies the window while somebody is standing "
            "in a room")
    assert "grid-template-columns: 1fr" in block, (
        "the sidebar's column is still reserved, so hiding it leaves a "
        "232px hole rather than giving the room the width")


def test_the_room_is_not_capped_at_the_page_width():
    """`.screen` is 720px, which is the box the field report photographed."""
    block = CSS[CSS.index(".screen.room-place {"):]
    block = block[:block.index("}")]
    assert "max-width: none" in block
    assert "100dvh" in block, "the room does not claim the window's height"


def test_the_shelf_copy_goes_when_the_room_arrives():
    """The title and pitch say what this screen is FOR — read by somebody
    deciding whether to open it. A person already in the room decided."""
    assert '{!inRoom && <h2>{tr("ins.title", lang)}</h2>}' in INSIDE
    assert '{!inRoom && <p className="muted small">{tr("ins.pitch", lang)}</p>}' \
        in INSIDE


def test_being_in_a_room_is_having_one_open():
    assert "const inRoom = Boolean(open);" in INSIDE, (
        "the room's own idea of being in a room is not the room being open")


# -- and it has a door -------------------------------------------------------

def test_the_room_has_a_way_out():
    assert "onLeave?: () => void;" in INSIDE, (
        "the room takes the window and offers no way back — the sidebar "
        "that used to be the exit is hidden")
    assert 'className="room-out"' in INSIDE


def test_the_door_is_drawn_before_the_room():
    """Under the fold with the room's other controls is not a door
    somebody in trouble can find."""
    # The whole frame, not a fixed slice of it: the held overlay and the
    # gesture layer now sit between the door and the title, and a 2000-char
    # window stopped reaching the thing being compared against.
    frame = INSIDE[INSIDE.index('<div className={"screen" + (inRoom'):]
    frame = frame[:frame.index('<Refusal error={error}')]
    assert frame.index("room-out") < frame.index('tr("ins.title"'), (
        "the way out is drawn after the room's own furniture")


def test_the_door_actually_leaves():
    assert re.search(r"onLeave=\{\(\) => \{ setInsideRoom\(\"\"\); "
                     r"setTab\(\"home\"\); \}\}", APP), (
        "the leave control is wired to something that does not clear the "
        "room, so leaving and returning lands back inside it")


def test_the_door_is_translated_like_everything_else():
    row = L10N[L10N.index('"ins.leave": {'):]
    row = row[:row.index("},")]
    for lang in ("en", "es", "fr", "de", "pt", "it", "ja", "zh", "hi", "ar"):
        assert f"{lang}:" in row, f"ins.leave has no {lang}"


# -- what it deliberately leaves alone ---------------------------------------

def test_fullscreen_and_the_sensors_are_still_a_press():
    """The reasoning that kept them a press is still right, and this round
    must not be read as overturning it."""
    assert "const [immersed, setImmersed] = useState(false);" in INSIDE
    block = CSS[CSS.index("/* ---- a room is a place"):]
    block = block[:block.index("@media (max-height")]
    assert "requestFullscreen" not in block

# -- the faces are the room --------------------------------------------------

def test_the_seats_come_first_in_the_room():
    """The participant card with its camera and mask controls is first in
    the markup, because on a page that reads top to bottom. In a room it
    pushed the faces below the fold, which was the whole complaint."""
    block = CSS[CSS.index(".screen.room-place > .room-stage"):]
    block = block[:block.index("}")]
    assert "order: -1" in block, (
        "the faces are still drawn under whatever the page put above them")
    assert "flex: 1 1 auto" in block, "the stage does not take the height"


def test_the_seats_are_two_columns_not_a_strip_of_thumbnails():
    """`auto-fill minmax(128px)` turns six people into a row of stamps on a
    wide window. Screen 103 draws two columns of large faces."""
    block = CSS[CSS.index(".screen.room-place .room-scene {"):]
    block = block[:block.index("}")]
    assert "repeat(2, minmax(0, 1fr))" in block
    assert "auto-fill" not in block


def test_the_face_grows_with_the_room_and_is_bounded():
    block = CSS[CSS.index(".screen.room-place .rs-face,"):]
    block = block[:block.index("}")]
    assert "clamp(" in block, (
        "the portrait is a fixed 72px, so a full-screen room draws page-"
        "sized faces in a window ten times the area")
    assert "13vh" in block


def test_the_tile_stops_carrying_a_pages_minimum_height():
    block = CSS[CSS.index(".screen.room-place .rs-tile {"):]
    block = block[:block.index("}")]
    assert "min-height: 0" in block, (
        "179px per tile means six people stack past the window instead of "
        "filling it")


def test_the_scene_heading_goes_when_the_room_arrives():
    """It labels a section on a page, and there is no page left."""
    assert '{!inRoom && <h3>{tr("ins.scene", lang)}</h3>}' in INSIDE
    assert '"card" + (inRoom ? " room-stage" : "")' in INSIDE


# -- the strip along the bottom ----------------------------------------------

def test_the_strip_has_the_controls_the_drawing_has():
    """Screen 103 draws five round controls beside the composer. The field
    report named them on the way past, and threw one out."""
    for cls in ("rs-round link", "rs-round files", "rs-round mic",
                "rs-round invite", "rs-round share"):
        assert f'"{cls}' in INSIDE, f"{cls} is missing from the room's strip"


def test_the_heart_did_not_survive_and_should_not_come_back():
    """"Who all is gonna like the chat, just the people in the chat." A like
    is for an audience that is not in the room, and everybody here is —
    and QRME has no reaction door, table or count behind one anyway."""
    strip = INSIDE[INSIDE.index('<div className="rs-strip">'):]
    strip = strip[:strip.index("</div>")]
    for absent in ("heart", "like", "\u2764"):
        assert absent not in strip.lower(), (
            f"a {absent} is back in the strip with nothing behind it")


def test_every_control_in_the_strip_does_something():
    """The defect this estate keeps finding: a button that lights up and
    changes nothing anybody else can see."""
    strip = INSIDE[INSIDE.index('<div className="rs-strip">'):]
    strip = strip[:strip.index("      </div>")]
    for wired in ("setDraft(", "sharePick.current?.click()", "flipTalking",
                  "setAsking(true)", "clipboard"):
        assert wired in strip, f"the strip has a control with no {wired}"


def test_the_paperclip_takes_photos_video_and_files():
    """One door rather than three buttons doing nearly the same thing."""
    picker = INSIDE[INSIDE.index("ref={sharePick}"):]
    picker = picker[:picker.index(">")]
    for kind in ("image/*", "video/*", ".pdf"):
        assert kind in picker, f"the attach picker refuses {kind}"


def test_muted_is_the_loud_state():
    """Whether your own microphone is off is the thing worth seeing from
    across a room."""
    block = CSS[CSS.index(".rs-round.mic:not(.live)"):]
    block = block[:block.index("}")]
    assert "224, 104, 122" in block, "muted does not read as muted"


def test_the_seat_marks_are_only_drawn_where_the_fact_exists():
    """Camera is a real per-seat field. Mute is not — `microphones_lent` is
    a borrowed wearable, which is a different fact and not its opposite."""
    assert 'face?.showing === "camera" && (' in INSIDE
    assert "isMe && !talking && (" in INSIDE, (
        "a mic-off badge is being drawn for seats whose microphone state "
        "this deployment does not know")
    assert 'const isMe = s.kind === "user" && s.id === me;' in INSIDE, (
        "the mic-off badge is no longer anchored to your own seat")


# -- press and hold, on a phone ----------------------------------------------

def test_both_gestures_open_the_held_options():
    """Neither is discoverable, and two chances beat one — the same pair
    screen 104 names and the camera controls on this screen already use."""
    block = INSIDE[INSIDE.index('className="room-gestures"'):]
    block = block[:block.index("/>")]
    assert "onDoubleClick" in block
    assert "onTouchStart" in block


def test_a_drag_is_a_scroll_not_a_press():
    """Without this, reading the transcript brings the overlay up under
    your thumb."""
    block = INSIDE[INSIDE.index('className="room-gestures"'):]
    block = block[:block.index("/>")]
    assert "onTouchMove" in block, (
        "a scroll still counts as a long press")


def test_the_held_options_are_the_three_the_drawing_names():
    block = INSIDE[INSIDE.index('<div className="room-held"'):]
    block = block[:block.index("</div>\n      )}")]
    for key in ("ins.held.help", "ins.held.landscape", "ins.held.back"):
        assert key in block, f"{key} is missing from the held overlay"
    assert "ins.held.tapaway" in block


def test_tapping_away_is_the_way_out():
    """The scrim carries it, rather than a fourth button that would need
    explaining."""
    assert '<div className="room-held" onClick={() => setHeld(false)}>' in INSIDE
    assert "onClick={(e) => e.stopPropagation()}" in INSIDE, (
        "pressing one of the three options also dismisses through the "
        "scrim, so the press races its own overlay")


def test_the_overlay_is_a_phone_affordance_only():
    """A computer has a window edge, a tab strip and a back button, and is
    landscape already."""
    assert "{inRoom && onAPhone && (" in INSIDE
    assert 'window.matchMedia("(pointer: coarse)").matches' in INSIDE, (
        "the phone test asks about screen size rather than about the "
        "input, which is what the gesture is actually about")


def test_turning_sideways_asks_for_fullscreen_because_it_has_to():
    """Orientation can only be locked from fullscreen — the platform's
    rule. This is the one press on this screen that says the word."""
    fn = INSIDE[INSIDE.index("async function goSideways"):]
    fn = fn[:fn.index("/** Send what has been heard")]
    assert "requestFullscreen" in fn
    assert 'lock("landscape")' in fn


def test_a_browser_that_will_not_turn_says_so():
    """iOS does not implement the lock. A button that does nothing and
    reports nothing is the one people press four times before giving up."""
    fn = INSIDE[INSIDE.index("async function goSideways"):]
    fn = fn[:fn.index("/** Send what has been heard")]
    assert "ins.held.turnfail" in fn


def test_sideways_reflows_to_three_columns():
    """Two columns of tall tiles in a short wide window is a room seen
    through a letterbox."""
    block = CSS[CSS.index("@media (max-height: 560px)"):]
    block = block[:block.index("/* ---- press and hold")]
    assert "repeat(3, minmax(0, 1fr))" in block
    assert "22vh" in block, "the portrait does not shrink for a short window"


# -- the transcript scrolls rather than forgets -------------------------------

def test_the_older_lines_go_above_the_fold_not_out_of_the_room():
    """`slice(-3)` did not hide the fourth turn, it deleted it — there was
    nothing to scroll back to. Field report: "I want at least three or four
    rows of back-and-forth text but I want them to start vanishing on the
    fifth, users can scroll up and down if they want to see it"."""
    assert "{transcript.slice(-3).map(" not in INSIDE, (
        "the strip is still dropping older turns instead of scrolling them")
    assert "{transcript.slice(-30).map(" in INSIDE
    block = CSS[CSS.index(".rs-chatlog {"):]
    block = block[:block.index(".rs-chatline {")]
    assert "overflow-y: auto" in block, "the transcript box does not scroll"
    assert "max-height" in block, (
        "the transcript box has no height, so it cannot have a fold")


def test_a_long_line_wraps_instead_of_being_clipped():
    """The other half of the same report — "when it goes past the first
    line as it's talking it just doesn't keep scrolling". It was
    `white-space: nowrap` with an ellipsis, so a sentence ended in a dot
    and stayed there."""
    block = CSS[CSS.index(".rs-chatline {"):]
    block = block[:block.index("}")]
    assert "nowrap" not in block, "a spoken line is still cut off mid-sentence"
    assert "text-overflow" not in block


def test_the_newest_line_stays_in_view_unless_you_are_reading():
    """It has to follow the speaker, and it has to stop following the
    moment somebody scrolls up — otherwise the four-second poll yanks the
    reader back down every time anybody says anything."""
    assert "box.scrollTop = box.scrollHeight" in INSIDE, (
        "the transcript does not follow the newest line")
    fn = INSIDE[INSIDE.index("function watchScroll()"):]
    fn = fn[:fn.index("useEffect")]
    assert "pinned.current" in fn, (
        "scrolling up does not stop the box from being pulled to the bottom")


def test_the_transcript_box_does_not_eat_the_double_tap():
    """This estate's own regression, once already: an overlay spanning the
    scene with `pointer-events` on swallows the gesture that opens a
    camera. The lines take the touch; the box around them does not."""
    block = CSS[CSS.index(".rs-chatlog {"):]
    block = block[:block.index(".rs-chatline {")]
    assert "pointer-events: none" in block
