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
#: The stylesheet with its comments taken out.
#:
#: A guard that greps the raw file reads its own explanation of a mistake as
#: the mistake. This file now says `clamp(72px, 13vh, 132px)` in prose, to
#: record what was removed and why, and the check that removal held has to
#: look at rules rather than at the paragraph describing them.
RULES = re.sub(r"/\*.*?\*/", "", CSS, flags=re.S)
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


def test_the_room_does_not_take_the_window():
    """A room is a card on the page, and the frames keep their own size.

    This guard used to assert the opposite — `max-width: none` and
    `100dvh` — and it was wrong about what had been asked for. The ask was
    one thing: move the transparent bar and its controls down off the
    faces, into the small-font band below them. What got built was that
    AND a full-screen place, with the tiles stretched to fill whatever was
    left over.

        asked     where does the strip sit
        mattered  did the strip have to take the window with it

    Field report, holding up the screen from before the change: "I thought
    I asked just for the users frames in that transparent text box to drop
    down to where that small font text is, because in this photo the
    frames are perfect size and scale." They were — they are the sizes
    read off docs/screens/103-audio-room.svg — and stretching them was a
    second change riding along with a first one that was right.
    """
    block = CSS[CSS.index(".screen.room-place {"):]
    block = block[:block.index("}")]
    assert "100dvh" not in block, (
        "the room claims the window's height again — a card on a page is "
        "what was asked for")
    assert "max-width: none" not in block, (
        "the room escapes the page width again")



def test_the_shelf_copy_goes_when_the_room_arrives():
    """The title and pitch say what this screen is FOR — read by somebody
    deciding whether to open it. A person already in the room decided."""
    assert '{!inRoom && <h2>{tr("ins.title", lang)}</h2>}' in INSIDE
    assert '{!inRoom && <p className="muted small">{tr("ins.pitch", lang)}</p>}' \
        in INSIDE


def test_being_in_a_room_is_going_in():
    """This guard's claim was replaced on purpose, and the old one is
    written down rather than quietly dropped.

    It used to assert `inRoom = Boolean(open)` — having a room id WAS
    being in the room. So the moment an id existed, typed or remembered or
    handed in by another screen, this component joined and drew the faces.
    Field report, from a phone: "it shouldn't even be shown yet. I don't
    think it should dive straight into the room."

        asked     do you have a room id
        mattered  have you gone in

    Having somebody's address is not being in their house, and frames that
    arrive before the press make the button below them look like it has
    already been pressed. Going in is now a press.
    """
    assert "const inRoom = entered && Boolean(open);" in INSIDE, (
        "an id is being treated as arrival again")
    assert "setEntered(true)" in INSIDE, "nothing ever goes in"
    assert "setEntered(false)" in INSIDE, "nothing ever comes back out"


def test_nothing_joins_a_room_you_have_not_entered():
    """The dive had a second cost: the join effect ran on `[open, token]`,
    so every keystroke in the id box tried to join a half-typed room."""
    block = INSIDE[INSIDE.index("useEffect(() => { if (entered) load(); }"):]
    block = block[:block.index(";")]
    assert "if (entered)" in block


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


def test_the_door_is_painted_inside_the_room():
    """The guards above all passed while there was no way out of a room.

    `.room-out` is `position: absolute`, and `.screen.room-place` carried
    no `position` — so the button resolved against whatever was positioned
    further up the tree and painted itself outside the room entirely. The
    element existed, `onLeave` was wired, the click worked, and a person in
    a full-screen room could not get out: "there's no close button to take
    you back to the main menu."

        asked     is there a door
        mattered  is the door where a person can reach it

    Existing in the JSX is not the claim worth guarding. Being reachable
    is. The same defect `.rs-chatstrip` had, fixed on the stage and not
    looked for on its sibling — so this checks the containing block rather
    than the element, which is the half that was actually missing.
    """
    door = CSS[CSS.index(".room-out {"):]
    door = door[:door.index("}")]
    # Rewritten as its own last line instructed. The door is FIXED now:
    # anchored to the container it was still under the footsteps chip
    # (fixed at the same corner, higher layer) and it scrolled away with
    # the page — the second field report asked for a way home while
    # standing in a room whose ✕ was nominally rendered. Fixed resolves
    # against the viewport, which cannot scroll it away and cannot paint
    # it outside the screen, so the containing-block half of the old
    # guard has nothing left to hold; what is worth holding now is that
    # the door sits BELOW the chip's corner instead of under it.
    assert "position: fixed" in door, (
        "the door moved off fixed positioning — reachability now depends "
        "on what it resolves against; rewrite this guard with the new "
        "reasoning rather than deleting it")
    m = re.search(r"top:\s*(\d+)px", door)
    assert m and int(m.group(1)) >= 26, (
        "the door is back in the footsteps chip's corner — the chip is "
        "fixed at top 6px on a higher layer and sat exactly on top of it")


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
    the markup, because a page reads top to bottom. In a room it pushed the
    faces below the fold, which was the original complaint and is still
    worth holding — the ordering survived the full-screen build being
    taken back out, because it was never the part that was wrong."""
    block = CSS[CSS.index(".screen.room-place > .room-stage"):]
    block = block[:block.index("}")]
    assert "order: -1" in block, (
        "the faces are still drawn under whatever the page put above them")



def test_the_seats_keep_the_grid_every_other_screen_uses():
    """No room-only column count.

    Two fixed columns existed to fill a viewport the room is no longer
    filling. `.room-scene`'s own `auto-fill minmax(128px, 1fr)` is what
    every other surface draws, and it is what the photographed screen was
    drawing when the frames were called perfect.
    """
    assert ".screen.room-place .room-scene {" not in RULES, (
        "the room overrides the seat grid again — a seat should be the "
        "same seat here as everywhere else")



def test_the_face_is_the_size_it_is_drawn_at():
    """72px, everywhere.

    There were rules here growing the portrait with the viewport
    (`clamp(72px, 13vh, 132px)`) so that a full-screen room would not draw
    page-sized faces in a window ten times the area. With the room back on
    the page there is no such window, and the clamp made the frames the
    thing somebody had to ask to have put back.
    """
    assert ".screen.room-place .rs-face," not in RULES, (
        "the room resizes the portrait again")
    assert "13vh" not in RULES, (
        "the face is still scaling with the viewport")



def test_the_tile_keeps_its_height():
    """179px, as `.rs-tile` declares it.

    The overrides that took this to 150px, and to 118px on a short window,
    existed so six seats would fit a viewport the room was filling. It is
    not filling one, so a seat is the seat — which is what "perfect size
    and scale" was describing.
    """
    assert ".screen.room-place .rs-tile {" not in RULES, (
        "the room shrinks the seat again")



def test_the_scene_heading_goes_when_the_room_arrives():
    """It labels a section on a page, and there is no page left."""
    assert '{!inRoom && <h3>{tr("ins.scene", lang)}</h3>}' in INSIDE
    assert '"card" + (inRoom ? " room-stage" : "")' in INSIDE


# -- the strip along the bottom ----------------------------------------------

def test_the_strip_has_the_controls_the_drawing_has():
    """Screen 103 draws five round controls beside the composer. The field
    report named them on the way past, and threw one out.

    Then the owner threw out a second: the strip's 📎 clicked the same
    picker as the composer's 📎, inches away — two buttons, one act — and
    "since there's already a paper clip, remove the paper clip that's
    right by the green microphone." The DOOR is untouched: the composer's
    button still opens it, and the assert below holds that half so the
    capability cannot leave with its duplicate."""
    for cls in ("rs-round link", "rs-round mic",
                "rs-round invite", "rs-round share"):
        assert f'"{cls}' in INSIDE, f"{cls} is missing from the room's strip"
    assert '"rs-round files' not in INSIDE, (
        "the strip's duplicate paperclip is back beside the composer's")
    assert "sharePick.current?.click()" in INSIDE, (
        "the share door has no button at all — the duplicate left and "
        "took the capability with it")


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
    # `sharePick.current?.click()` left this list with the strip's
    # duplicate paperclip — the composer's button holds that door now,
    # and the guard above holds the door.
    for wired in ("setDraft(", "flipTalking",
                  "setAsking(true)", "clipboard",
                  # Lending the profiles your microphone. It had a card of
                  # its own; the card is gone and the door is here, beside
                  # the handover it sits next to in meaning — both hand
                  # something of yours to somebody else.
                  "api.lendMicInRoom(", "api.takeBackMicInRoom("):
        assert wired in strip, f"the strip has a control with no {wired}"


def test_the_paperclip_takes_photos_video_and_files():
    """One door rather than three buttons doing nearly the same thing."""
    picker = INSIDE[INSIDE.index("ref={sharePick}"):]
    picker = picker[:picker.index(">")]
    for kind in ("image/*", "video/*", ".pdf"):
        assert kind in picker, f"the attach picker refuses {kind}"


def test_live_is_the_green_state():
    """Green means live, red means muted — the owner's NEWEST call, and the
    second reversal of this pair, both on the record.

    First cut: green-hot (nobody's call). His first correction:
    recording-light — red is hot, green is safe to sneeze. Then rooms
    started opening live (1.8.6), he met the red ring on arrival and read
    it as muted: "it should show green and the microphone is live and
    running when you show up; it only shows red when a user presses it
    and the microphone becomes muted." A traffic-light reading beat a
    recording-light reading in the moment that counts — arrival — and the
    reading the room's owner reaches for is the one this holds.

        asked     which state is the alarming one
        mattered  an open microphone is not a thing to be vague about —
                  and if this pair reverses a third time, the answer is
                  words on the button, not another swap
    """
    live = CSS[CSS.index(".rs-round.mic.live"):]
    live = live[:live.index("}")]
    assert "123, 196, 127" in live, "a live microphone does not read as go"
    block = CSS[CSS.index(".rs-round.mic:not(.live)"):]
    block = block[:block.index("}")]
    assert "224, 85, 85" in block, "muted does not read as stopped"


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


def test_a_short_window_does_not_get_its_own_room():
    """No height-driven reflow, because nothing is being fitted to a height.

    Two columns of tall tiles in a short wide window was a room seen
    through a letterbox — a real problem for a place that had claimed
    `100dvh` and therefore could not scroll. A card on a page scrolls, so
    the fix for a short window is the page doing what pages do, and a
    room-only three-column reflow with `22vh` portraits is one more way for
    the frames to stop being the size they are drawn at.
    """
    block = RULES[RULES.index("@media (max-height: 560px)"):]
    block = block[:block.index("}")]
    assert "22vh" not in block, "the portrait shrinks with the window again"
    assert "room-scene" not in block, "the room reflows its own grid again"



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
    # A FIXED height, not a maximum. This guard asked for `max-height` and
    # got what it asked for, and the strip below the box still travelled
    # 135px down the page between the first turn and the fifth — measured
    # in a browser, not argued about — which on a phone put it under the
    # bottom edge. Field report: "as the conversation starts to pile up
    # five rows it pushes down the buttons."
    #
    #     asked     does the log stop growing
    #     mattered  does the strip stop moving
    #
    # A maximum stops the first and not the second. The property was never
    # the spelling of the property; it is that the box is one size from an
    # empty room onwards.
    assert re.search(r"(?<!max-)height:\s*\d", block), (
        "the transcript box has no height, so it cannot have a fold")
    assert "max-height" not in block, (
        "the box is capped rather than fixed, so it still grows from empty "
        "to full — and everything under it moves down by that much")


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


# -- the strip sits under the faces, not on them -----------------------------

def test_the_strip_is_a_sibling_of_the_scene_not_a_child():
    """Reported three times, each time as the bar "resting on top of the
    frames" — and twice "fixed" by adjusting a reserved constant.

        asked     where does the strip sit
        mattered  can it ever sit on top of the faces

    It lived inside `.room-scene`, absolutely positioned, with the stage
    reserving a hardcoded 104px underneath. That number was right the day
    it was written and wrong the moment the transcript grew to four
    scrolling rows: a reserved constant is a guess about somebody else's
    height, and a guess drifts every time the thing it guesses about
    changes. As a sibling the strip takes the room it needs and the scene
    shrinks by exactly that much, so the two cannot overlap however either
    one grows later.
    """
    start = INSIDE.index('<div className="room-scene">')
    # Walk the tags and find where the scene actually closes, rather than
    # counting them — a count says nothing about order, and order is the
    # whole claim.
    depth, closed_at, i = 0, None, start
    while i < len(INSIDE):
        opened = INSIDE.find("<div", i)
        shut = INSIDE.find("</div>", i)
        if shut == -1:
            break
        if opened != -1 and opened < shut:
            depth += 1
            i = opened + 4
            continue
        depth -= 1
        i = shut + 6
        if depth == 0:
            closed_at = shut
            break
    assert closed_at is not None, "the room scene never closes"
    strip = INSIDE.index("{spokenRoom ? voiceBar : chatStrip}", start)
    assert strip > closed_at, (
        "the strip is still inside the scene it is supposed to sit below")


def test_the_room_reserves_no_guessed_height():
    """The constant is the defect, not its value."""
    block = CSS[CSS.index(".screen.room-place > .room-stage {"):]
    block = block[:block.index("}")]
    assert "padding-bottom: 104px" not in block, (
        "the stage is guessing the strip's height again")


def test_the_strip_stops_floating_in_a_room():
    block = CSS[CSS.index(".screen.room-place .rs-chatstrip,"):]
    block = block[:block.index("}")]
    assert "position: static" in block, (
        "the strip is still an overlay in a room, so it can ride up over "
        "the seats when it grows")
    assert "flex: 0 0 auto" in block, (
        "the strip can be squeezed by the scene instead of the other way "
        "round")


def test_the_flat_page_keeps_its_containing_block():
    """The strip riding the scene is the gallery's design on the flat page
    (screens 96-98) and is deliberately kept. Now that the strip is a
    sibling, the card has to be what it positions against — otherwise it
    resolves further up the tree and lands outside, which is exactly how
    the way out of a room went missing."""
    assert ".card:has(> .room-scene)" in CSS
    block = CSS[CSS.index(".card:has(> .room-scene)"):]
    block = block[:block.index("}")]
    assert "position: relative" in block


# -- the room's name, from inside it -----------------------------------------

def test_the_room_can_be_named_from_inside_it():
    """"That's a good place to edit your room name while you're already
    in, and the button that says Go in — I just need to say Save."" """
    assert "ins.roomname" in INSIDE
    assert "api.renameRoom(" in INSIDE, "the Save button saves nothing"


def test_the_same_card_does_both_jobs():
    """Outside a room it asks which one; inside it names the one you are
    in. One place, because that is where a person already is when they
    notice the name is wrong."""
    block = INSIDE[INSIDE.index('{inRoom ? tr("ins.roomname"'):]
    block = block[:block.index("{!token && (")]
    assert 'tr("ins.whichroom"' in block
    assert 'tr("ins.goin"' in block, "the way into a room was replaced"
    assert 'tr("ins.roomname.save"' in block


def test_the_name_box_shows_the_name_it_will_replace():
    """An empty field asks somebody to guess the current value."""
    assert "setRoomName(r.topic" in INSIDE


# -- one control, one place --------------------------------------------------

def test_no_control_is_offered_twice():
    """Two cards repeated buttons the strip already carries: "Ask somebody
    into the room" duplicated 👤+, and the microphone card duplicated what
    is now the lend control.

        asked     is the control on screen
        mattered  is it on screen TWICE

    A second copy of a button is not more discoverable, it is one more
    thing to read past — and the strip is where a person's hand already
    is. The doors are unchanged; only the copies are gone.
    """
    assert 'tr("ins.ask.go"' not in INSIDE, (
        "the invite card is back, beside the strip's own invite")
    assert 'tr("ins.microphones"' not in INSIDE, (
        "the microphone card is back, beside the strip's own lend control")
    # The doors themselves must survive the cards being removed.
    for door in ("api.inviteToRoom(", "api.lendMicInRoom(",
                 "api.takeBackMicInRoom("):
        assert door in INSIDE, f"{door} left with the card that held it"


def test_lending_says_which_way_it_points():
    """Lending and taking back are different acts, and one label for both
    tells you nothing about which way the microphone is currently
    pointing."""
    # `rs-worded` joined the class when the toggle went from glyph to
    # words — the glyph read as "a person in a doorway" on a Windows
    # handheld, the third strip control in two rounds whose meaning
    # lived in a tooltip no phone shows.
    block = INSIDE[INSIDE.index('className={"rs-round rs-worded lend"'):]
    block = block[:block.index("</button>")]
    assert 'tr("ins.takeback"' in block and 'tr("ins.lendmic"' in block
    assert "aria-pressed={lentByMe}" in block
    # The label IS the state: both sentences are rendered as the button's
    # text, not only as aria strings.
    assert block.count('tr("ins.lendmic"') >= 2 or "lentByMe ? tr(" in block


def test_a_lent_microphone_is_visible_across_the_room():
    """The same argument the mute mark makes: an open microphone somebody
    else can hear through is the state worth seeing without asking."""
    block = CSS[CSS.index(".rs-round.lend.live"):]
    block = block[:block.index("}")]
    assert "box-shadow" in block or "border-color" in block


def test_the_oldest_line_fades_rather_than_being_cut_square() -> None:
    """"Fade away the top line, but you should be able to scroll back if
    you need to reread it."

    Both halves matter and they pull against each other: a fade drawn by
    painting a solid bar over the top edge would hide the line AND block
    the scroll to it. A mask fades the pixels and leaves the box scrolling
    underneath, so the oldest line is dimmed at the fold and whole again
    once you drag it down.
    """
    block = CSS[CSS.index(".rs-chatlog {"):]
    block = block[:block.index(".rs-chatline {")]
    assert "mask-image" in block, (
        "the oldest line is cut off square at the top of the box")
    assert "-webkit-mask-image" in block, (
        "Safari — which is every iPhone — draws no fade at all without the "
        "prefixed property, and iPhone is where this was reported")
    assert "transparent 0" in block, (
        "the mask does not start transparent, so nothing fades")


def test_a_short_conversation_sits_next_to_the_pill() -> None:
    """A fixed box and one message would leave the line stranded at the top
    with dead air between it and where you type.

    `margin-top: auto` on the first line rather than `justify-content:
    flex-end` on the box: the second makes overflowing content unreachable
    at the top in some browsers, and scrolling back to it is the other half
    of what was asked for.
    """
    assert re.search(r"\.rs-chatlog\s*>\s*:first-child\s*\{[^}]*margin-top:\s*auto",
                     CSS), (
        "a lone message floats at the top of an empty box")
    # Comments stripped first. The rule above explains *why* it is not
    # `justify-content: flex-end`, so a guard reading raw text finds the
    # phrase in the note written to prevent it — which is the second time
    # this file has caught itself reading its own documentation as code.
    block = RULES[RULES.index(".rs-chatlog {"):]
    block = block[:block.index(".rs-chatline {")]
    assert "justify-content: flex-end" not in block, (
        "flex-end on a scrolling column can strand the oldest lines out of "
        "reach above the top — which is exactly what must stay reachable")


def test_the_seats_controls_never_change_the_seat() -> None:
    """Three reports, one bug.

    "The buttons at the bottom disappear mid conversation." "The frames get
    smaller" when the controls are hidden. The strip cropped on a handheld.
    All the same thing: `.rs-controls` was a normal flex child, so seven
    chips and a mask picker wrapped onto three rows and the TILE grew by
    them — measured in a browser at 132px on a 1280x800 handheld and 148px
    on a phone, with the composer and the seven round controls moving down
    by exactly as much. The frames were never small; they had been inflated.

        asked     do the controls fit
        mattered  does the tile change size when they appear

    The camera tile has always overlaid its own controls. The fix existed
    in this file and the ordinary tile never got it.
    """
    block = re.search(
        r"\.screen\.room-place \.rs-tile \.rs-controls\s*\{([^}]*)\}", RULES)
    assert block, (
        "the seat's controls are back in the tile's flow, so opening them "
        "resizes the seat and everything under it moves")
    said = block.group(1)
    assert "position: absolute" in said, (
        "the controls take room in the tile rather than riding over it")
    # Taller than the tile must scroll, not stretch: the one thing this rule
    # may never do is change the tile's height again.
    assert "max-height" in said and "overflow-y" in said, (
        "a control strip taller than the tile would stretch it, which is the "
        "bug wearing the fix's clothes")
