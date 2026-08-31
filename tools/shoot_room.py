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
    for owned in (founder, amara):
        conn.execute("UPDATE profiles SET owner_id=? WHERE id=?",
                     (account, owned))
    conn.commit()

    room_id = db.new_id("room")
    conn.execute(
        "INSERT INTO rooms (id, topic, channel, status, created_at)"
        " VALUES (?,?,'chat','active',?)",
        (room_id, "Rounds", db.utcnow()))
    for kind, ref in (("user", person["id"]), ("profile", founder),
                      ("profile", amara)):
        conn.execute(
            "INSERT OR IGNORE INTO room_participants (room_id, kind, ref_id)"
            " VALUES (?,?,?)", (room_id, kind, ref))
    conn.commit()

    # A turn apiece, so the transcript is a conversation and the light has
    # somebody to sit on. Approved, because a blocked turn draws
    # differently and that is a different picture.
    said = [
        ("user", person["id"], "Where did we land on the discharge gap?"),
        ("profile", amara,
         "Usually on the discharging team, and usually it is a gap rather "
         "than a decision."),
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
    return page.query_selector(".room-focus") is not None


def press_format(page, key: str) -> bool:
    """Press one of the three format chips, and check it took."""
    for button in page.query_selector_all(".rs-format"):
        if (button.get_attribute("aria-pressed") is not None
                and _is(button, key)):
            button.click()
            page.wait_for_timeout(600)
            return button.get_attribute("aria-pressed") == "true"
    return False


#: The chip's own word, per format, in the language the harness runs in.
#: Matched on the visible text because the chips carry no data attribute —
#: and if one is ever added, this is the line that changes.
_WORDS = {"audio": "audio", "avatar": "avatar", "video": "video",
          "face": "face", "upper": "upper", "full": "full"}


def _is(button, key: str) -> bool:
    return _WORDS[key] in (button.inner_text() or "").strip().lower()


def press_framing(page, key: str) -> bool:
    for button in page.query_selector_all(".rs-framing .rs-format"):
        if _is(button, key):
            button.click()
            page.wait_for_timeout(900)
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
                    on = page.query_selector(".rf-who")
                    got = (on.inner_text() if on else "").strip()
                    if got != person["name"]:
                        # The frame is showing somebody else, so every
                        # capture in this pass would carry the wrong name
                        # under the right filename.
                        print(f"  ! the frame says {got!r}, not "
                              f"{person['name']!r}")
                        page.close()
                        continue
                    for fmt in FORMATS:
                        if not press_format(page, fmt):
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
