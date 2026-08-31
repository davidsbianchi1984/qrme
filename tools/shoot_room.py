"""Photograph the room — the rail, the stage, and the three formats.

## Why this is its own harness

`shoot_screens.py` walks the console's tabs and photographs each one as a
person meets it. A room is not a tab. It needs a room to exist, two
profiles with faces sitting in it, an interactor holding a token, and a
press on Go — and then it needs the same room photographed three times
over, once per format, at two widths.

That is a recipe, not a tab, and wedging it into the tab walker would put
a page of room-specific setup inside a loop that is about drawers and
`active` classes.

## What it photographs

The room draws in three formats and the format is the viewer's own:

    audio    the still, big — an audio turn has no second thing to show
    avatar   the AvatarSDK figure in the frame, with its four controls
    video    the turn's footage, or the honest state when there is none

Each at a desktop width, where the rail runs down the left and the frame
takes the rest, and at a phone width, where the frame comes first and the
rail is a row you push sideways.

## What it does NOT do

It does not invent a room. Two profiles ship with three-dimensional
models — `david_bianchi_ai` and `dr_amara_osei` — and those are the two
seats besides the person. There is no third avatar, so there is no third
figure in these pictures.

It does not start a render. Every video provider is behind a key this
machine does not have. The `scene_render` row is inserted the way
`auto_render` inserts it, and the console draws it by polling the real
route — so what is photographed is a state the product reaches on its
own, from a shorter distance than a person reaches it.

    asked     does the room have three formats
    mattered  does each one DRAW
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

# `tools` is not a package, so the directory itself goes on the path and
# the sibling is imported by its own name. Adding an `__init__.py` would
# make every script in here importable as `tools.x`, which is a change to
# how the repo is laid out and not something a screenshot run should do.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from shoot_screens import (  # noqa: E402
    BASE, answer_the_notice, build_console, open_tab, start_backend,
    tuck_the_widgets,
)

OUT = REPO / "docs" / "scenes"

#: Two widths, and the names are what the README calls them. Desktop is
#: 1280 because that is where the rail-and-stage grid turns on (720px) with
#: room to spare, and a capture at exactly the breakpoint documents the
#: edge case rather than the layout.
WIDTHS = {
    "desktop": {"width": 1280, "height": 900},
    "phone": {"width": 430, "height": 932},
}
SCALE = 2

#: The three formats, and the framings inside the avatar one. Written out
#: rather than read off the module, because a harness that derives its
#: expectations from the code it is testing agrees with that code by
#: construction.
FORMATS = ("audio", "avatar", "video")
FRAMINGS = ("face", "upper", "full")


def seed(db_path: str) -> dict:
    """A verified account, an interactor, and a room holding the two
    profiles that ship with faces.

    The interactor is not optional and it is the piece that was missed the
    first time: without one the console says "Sign in as a person first"
    and Go stays disabled, so the harness photographed the door instead of
    the room and filed it under the room's name.

    The channel is `chat` and that is not arbitrary. `models.Channel` is a
    validated `Literal` at the API door, and a row written straight into
    `rooms` skips it — a harness that seeded `text` produced a room whose
    join 500s on `_CHANNEL_NOTES[room["channel"]]`. Seeding below the door
    means keeping the door's rules by hand.
    """
    os.environ["QRME_DB"] = db_path
    from qrme import accounts, auth, avatars, db, filming, seed as starters

    db.reset()
    starters.seed()

    stamp = str(int(time.time()))
    email = f"room+{stamp}@example.test"
    accounts.signup(email, "a-long-enough-password", "David Bianchi")
    conn = db.connect()
    conn.execute("UPDATE accounts SET verified_at=? WHERE email=?",
                 (db.utcnow(), email))
    conn.commit()
    account = conn.execute("SELECT id FROM accounts WHERE email=?",
                           (email,)).fetchone()["id"]
    person = accounts.interactor_for(account, "David Bianchi")

    def by_handle(handle: str) -> str:
        row = conn.execute(
            "SELECT profile_id FROM handles WHERE handle=?",
            (handle,)).fetchone()
        if row is None:
            raise SystemExit(f"the starter collection has no {handle}")
        return row["profile_id"]

    founder = by_handle("david_bianchi_ai")
    amara = by_handle("dr_amara_osei")
    # A third voice in the room.
    #
    #     asked     how many seats does the app open with
    #     mattered  how many does a SCREENSHOT need
    #
    # The app opens two and an empty chair, which is the right default
    # and a thin picture: two boxes and a blank say nothing about what a
    # room is for. The owner's call — "for the screenshots and the readme
    # files, I want three people in the conversation like in the photo."
    #
    # A third starter rather than an invented one: she is in the
    # collection, she has a field, and nothing here is drawn that the
    # product could not seat.
    lena = by_handle("dr_lena_whitcomb")
    # And three more, to fill the table.
    #
    #     asked     show two rows of four
    #     mattered  have eight boxes to put in them
    #
    # A room is most itself when it is full, and the shape the seats take
    # at eight is the shape worth photographing. All three are in the
    # starter collection with a portrait and a field, so nothing here is
    # drawn that the product could not seat.
    others = [by_handle(h) for h in ("dr_marcus_adeyemi",
                                     "cmdr_ellen_park",
                                     "chef_henri_laurent")]
    # The account takes both starters.
    #
    #     asked     is there an avatar in the frame
    #     mattered  can the person in front of it press the four controls
    #
    # `AvatarStage` draws the wardrobe, body, framing and expand controls
    # only for an owner, and correctly — editing a face you do not own is
    # not a thing this product offers. A starter belongs to `qrme-starter`,
    # so a harness that left them there would photograph the frame with
    # the controls missing and file it as the feature.
    #
    # Owning more than one profile is a state any account reaches; this
    # one reaches it by the shortest road rather than through the studio.
    for owned in [founder, amara, lena] + others:
        conn.execute("UPDATE profiles SET owner_id=? WHERE id=?",
                     (account, owned))
    conn.commit()

    # The person's seat wears the PHOTOGRAPH of David; the profile seat
    # wears the AI rendering of him.
    #
    #     asked     seat the founder in the room
    #     mattered  which of the two Davids is which
    #
    # Both are in the collection on purpose — the platform's whole
    # argument is that a synthetic thing must say so, hence a rendered
    # David marked AI in his own pixels and a photographed David who is
    # not. In the room they came out as the same face twice, once
    # labelled "You" and once "Technology", which for somebody reading
    # the README is the single confusion this product exists to prevent.
    person_pic = "/photos/david_bianchi.webp"

    room_id = db.new_id("room")
    conn.execute(
        "INSERT INTO rooms (id, topic, channel, status, created_at)"
        " VALUES (?,?,'chat','active',?)",
        (room_id, "Rounds", db.utcnow()))
    for kind, ref in ([("user", person["id"]), ("profile", founder),
                       ("profile", amara), ("profile", lena)]
                      + [("profile", o) for o in others]):
        conn.execute(
            "INSERT OR IGNORE INTO room_participants (room_id, kind, ref_id)"
            " VALUES (?,?,?)", (room_id, kind, ref))
    conn.commit()

    # `set_showing` is the product's own road: it is what putting your
    # picture up in a room does.
    from qrme import roomface
    roomface.set_showing(room_id, person["id"], "photo",
                         media_url=person_pic)

    # A turn apiece, so the transcript is a conversation and the light has
    # somebody to sit on. Approved, because a blocked turn draws
    # differently and that is a different picture.
    # Enough turns that the transcript reads as a conversation rather
    # than as a demo of one. Three voices, and the last word decides who
    # the frame opens on.
    said = [
        ("user", person["id"],
         "My mother's discharge notes mention a follow-up nobody booked. "
         "Is that on us or on them?"),
        ("profile", lena,
         "Before the logistics — how is she taking it? A missed follow-up "
         "lands differently when somebody is already worried."),
        ("profile", founder,
         "Both, and the vault keeps the paper trail either way: whoever "
         "owns the referral, the record of asking is yours."),
        ("profile", amara,
         "Usually on the discharging team, and usually it is a gap rather "
         "than a decision. Ring the ward clerk with the discharge date and "
         "ask who owns the referral — that is the sentence that gets it "
         "booked."),
        ("user", person["id"],
         "She is eighty-one and she will not ring them herself. Can I do "
         "it on her behalf?"),
        ("profile", others[0],
         "You can, and say that plainly when you call — a proxy who names "
         "themselves gets further than one who does not."),
        ("profile", lena,
         "And tell her you have done it. The waiting is most of what is "
         "wearing on her, not the appointment."),
        ("profile", others[1],
         "Write the date and the clerk's name down before you dial. Every "
         "checklist I ever wrote existed because somebody trusted their "
         "memory on the phone."),
        ("profile", founder,
         "It goes in the vault either way — hers, not ours, and she can "
         "take it with her or burn it."),
    ]
    for kind, ref, words in said:
        conn.execute(
            "INSERT INTO room_messages (id, room_id, sender_kind, sender_id,"
            " content, status, created_at) VALUES (?,?,?,?,?,'approved',?)",
            (db.new_id("msg"), room_id, kind, ref, words, db.utcnow()))
    conn.commit()

    # The video road on the profile that speaks last, and one render on it
    # — the row `auto_render` inserts, reached by the console's own poll.
    filming.set_road(amara, "video", 60)
    conn.execute(
        "INSERT INTO scene_render (id, profile_id, passage, seconds, status,"
        " created_at) VALUES (?,?,?,?,'pending',?)",
        (db.new_id("ren"), amara, said[-1][2], 8, db.utcnow()))
    conn.commit()

    base = {
        "accountId": account,
        "accountToken": auth.issue("account", account),
        "accountEmail": email,
        "interactorId": person["id"],
        "interactorToken": auth.issue("interactor", person["id"]),
    }
    return {
        "roomId": room_id,
        "base": base,
        "who": {
            "david": {"id": founder, "name": "David Bianchi",
                      "model": avatars.model_of(founder),
                      "token": auth.issue("owner", founder)},
            "amara": {"id": amara, "name": "Dr. Amara Osei",
                      "model": avatars.model_of(amara),
                      "token": auth.issue("owner", amara)},
        },
    }


def speaks(profile_id: str, room_id: str, words: str) -> None:
    """One more approved turn, so the frame moves to this profile.

    `onStage` is whoever spoke last while the room is quiet, so the way to
    photograph a second person's frame is to let them say something —
    which is the product's own rule, not a switch the harness reaches
    past it for.
    """
    from qrme import db
    conn = db.connect()
    conn.execute(
        "INSERT INTO room_messages (id, room_id, sender_kind, sender_id,"
        " content, status, created_at) VALUES (?,?,'profile',?,?,"
        "'approved',?)",
        (db.new_id("msg"), room_id, profile_id, words, db.utcnow()))
    conn.commit()


def go_in(page, session: dict, room_id: str) -> bool:
    """Reach the room the way a person does: the Inside tab, the id, Go.

    Returns False rather than raising, and the caller writes no file — a
    missing picture is a gap somebody notices, a picture of the wrong
    screen is a gap nobody notices.
    """
    page.evaluate("s => localStorage.setItem('qrme.session', s)",
                  json.dumps(session))
    if not open_tab(page, "inside"):
        print("  ? could not open the Inside tab")
        return False
    answer_the_notice(page)
    tuck_the_widgets(page)
    page.wait_for_timeout(600)

    box = page.query_selector(".screen input[placeholder]")
    if box is None:
        print("  ? no room-id box on the Inside screen")
        return False
    box.fill(room_id)
    page.wait_for_timeout(300)
    for button in page.query_selector_all(".screen button"):
        if (button.inner_text() or "").strip().lower().startswith("go"):
            if button.is_disabled():
                print("  ? Go is disabled — is there an interactor?")
                return False
            button.click()
            break
    else:
        print("  ? no Go button")
        return False
    page.wait_for_timeout(2500)
    # Proof of arrival is a SEAT, not the frame.
    #
    # It was `.room-focus`, which is the box on the right — and that box
    # does not render on the audio road any more, because there was
    # nothing to put in it that the seats were not already showing. So
    # every audio pass reported "never reached the room" from inside the
    # room. A seat is the thing a room always has.
    return page.query_selector(".rs-tile") is not None


def press_format(page, key: str, who: str) -> bool:
    """Set the format the way a person does: the seat's own two glyphs.

        asked     press the format chip
        mattered  press the thing the product actually has

    There were three chips above the rail — Audio, Avatar, Video — and
    the harness pressed them by their words. They are gone: the format
    is set per seat now, by the standing figure and the movie camera
    beside each face, and pressing a lit one puts the room back to
    voices and photographs.

    So this presses the roads on the seat being photographed. `audio` is
    not a button; it is the state you are in when neither road is lit,
    which is exactly what the product says and what this now checks.
    """
    tile = _tile_for(page, who)
    if tile is None:
        return False
    roads = tile.query_selector_all(".rs-road")
    if len(roads) < 2:
        return False
    avatar, video = roads[0], roads[1]
    want = {"avatar": avatar, "video": video}.get(key)

    if key == "audio":
        # Release whichever is lit; if neither is, the room is already
        # showing voices and photographs.
        for road in (avatar, video):
            if road.get_attribute("aria-pressed") == "true":
                road.evaluate("el => el.click()")
                page.wait_for_timeout(900)
        return all(r.get_attribute("aria-pressed") != "true"
                   for r in (avatar, video))

    if want is None:
        return False
    if want.get_attribute("aria-pressed") != "true":
        want.evaluate("el => el.click()")
        page.wait_for_timeout(1400)
    return want.get_attribute("aria-pressed") == "true"


def _tile_for(page, who: str):
    """The rail card carrying this name."""
    for tile in page.query_selector_all(".rs-tile"):
        name = tile.query_selector(".rs-name")
        if name and (name.inner_text() or "").strip() == who:
            return tile
    return None


#: Each framing's own word, in the language the harness runs in. Matched
#: on the visible text because the chips carry no data attribute — and if
#: one is ever added, this is the line that changes.
_WORDS = {"face": "face", "upper": "upper", "full": "full"}


def _is(button, key: str) -> bool:
    return _WORDS[key] in (button.inner_text() or "").strip().lower()


def press_framing(page, key: str) -> bool:
    """Face, upper torso, full body — pressed on the frame itself.

    These were a fourth row of chips above the rail and are now where
    they belong: on the stage that draws the figure, which is the only
    place they mean anything. `.stage-shots` is that row.
    """
    for button in page.query_selector_all(".stage-shots button"):
        if _is(button, key):
            # `el.click()` rather than Playwright's, for the same reason
            # `open_tab` uses it: changing the framing rebuilds the scene
            # and reloads a 13 MB model on software GL, which blocks the
            # main thread long past the actionability check's patience.
            # The press itself is fine; waiting for the page to look calm
            # afterwards is what times out.
            button.evaluate("el => el.click()")
            page.wait_for_timeout(4000)
            return button.get_attribute("aria-pressed") == "true"
    return False


def shoot(page, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / f"{name}.png"
    page.screenshot(path=str(target))
    print(f"  ✓ {target.relative_to(REPO)}")


def main() -> None:
    from playwright.sync_api import sync_playwright

    build_console()
    backend = start_backend()
    try:
        made = seed("/tmp/shots.db")  # the path start_backend serves
        room = made["roomId"]
        with sync_playwright() as play:
            browser = play.chromium.launch(
                executable_path="/opt/pw-browsers/chromium")
            for who, said in (("amara", None),
                              ("david",
                               "That is the shape of it, and it is why the "
                               "vault sits underneath rather than beside.")):
                person = made["who"][who]
                if person["model"] is None:
                    print(f"  ! {person['name']} has no model — skipped")
                    continue
                if said:
                    speaks(person["id"], room, said)
                session = dict(made["base"],
                               profileId=person["id"],
                               ownerToken=person["token"])
                print(f"{person['name']} — {person['model']}")
                for width_name, viewport in WIDTHS.items():
                    page = browser.new_page(viewport=viewport,
                                            device_scale_factor=SCALE)
                    page.goto(BASE + "/", wait_until="networkidle")
                    if not go_in(page, session, room):
                        print(f"  ! never reached the room at {width_name}")
                        page.close()
                        continue
                    # Read off the RAIL, not the frame.
                    #
                    #     asked     is the right person on the stage
                    #     mattered  where does the screen say who that is
                    #
                    # This read `.rf-who`, which was the frame's heading
                    # back when the frame repeated the name the rail had
                    # already given. The frame says what it is SHOWING
                    # now — "This turn, in their own voice" — and the
                    # name lives once, on the lit seat. The check moved
                    # with it rather than being deleted: a pass that
                    # photographs the wrong person under the right
                    # filename is the failure this guard exists for, and
                    # it caught exactly that on the first run after the
                    # heading changed.
                    on = page.query_selector(".rs-tile.talking .rs-name")
                    got = (on.inner_text() if on else "").strip()
                    if got != person["name"]:
                        print(f"  ! the lit seat says {got!r}, not "
                              f"{person['name']!r}")
                        page.close()
                        continue
                    for fmt in FORMATS:
                        if not press_format(page, fmt, person["name"]):
                            print(f"  ? {fmt} chip did not take "
                                  f"at {width_name}")
                            continue
                        if fmt != "avatar":
                            page.wait_for_timeout(1400)
                            shoot(page, f"room-{fmt}-{who}-{width_name}")
                            continue
                        # The figure takes a while on software GL: the
                        # shipped models are 13 MB and there is no GPU.
                        page.wait_for_timeout(12000)
                        for framing in FRAMINGS:
                            if not press_framing(page, framing):
                                print(f"  ? {framing} did not take")
                                continue
                            page.wait_for_timeout(3000)
                            shoot(page,
                                  f"room-avatar-{framing}-{who}-{width_name}")
                    page.close()
            browser.close()
    finally:
        backend.terminate()


if __name__ == "__main__":
    main()
