"""The four panels meet you in the chat, at the size of the face.

Two field reports off one screenshot. The rail of four — who they are,
what they hold, what you are to each other, how they behave — was
reachable only inside the talk overlay, which made it a voice feature by
accident of placement; the owner circled the spot for it in the main
chat: the right edge, docked under the loudness rail. And the chat
banner: "this is way too large — make it smaller to match the scaling of
the photo." A 52px face beside page-title type is a header at war with
itself.
"""

from __future__ import annotations

import re
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "app" / "src"
CHAT = (SRC / "screens" / "Chat.tsx").read_text(encoding="utf-8")
CSS = (SRC / "styles.css").read_text(encoding="utf-8")


def test_the_rail_is_in_the_main_chat_not_only_the_overlay():
    stripped = re.sub(r"/\*.*?\*/", "", CHAT, flags=re.S)
    stripped = re.sub(r"^\s*//.*$", "", stripped, flags=re.M)
    at = stripped.index('className="chat-rail-dock"')
    assert "<TalkRail" in stripped[at:at + 600], (
        "the dock stands and its rail is gone")
    assert "<TalkRail" in stripped[:at], (
        "the overlay lost its rail — the dock is now the only telling")
    assert "!talking" in stripped[at - 200:at], (
        "the dock draws under the overlay's own rail while talking")


def test_the_dock_is_a_fixed_column_under_the_rail():
    block = CSS[CSS.index(".chat-rail-dock .talk-rail"):]
    block = block[:block.index("}")]
    assert "position: fixed" in block
    assert "flex-direction: column" in block, (
        "the dock lies flat and eats the composer instead of sitting "
        "under the dial")


def test_the_chat_banner_holds_the_faces_scale():
    assert ".chat-head-words h2" in CSS, (
        "the banner is back at page-title size beside a 52px face")


def test_the_rail_reaches_the_rooms_too():
    """"Those four extra boxes should be located in all the chats,
    including rooms." With several profiles seated, the chips above the
    column say whose panels are open — and the owner's panels are offered
    only for the profile the session actually owns, so no button opens
    onto a refusal."""
    inside = (SRC / "screens" / "Inside.tsx").read_text(encoding="utf-8")
    assert "<TalkRail" in inside, "the rooms lost the four panels"
    assert "room-dock-picker" in inside, (
        "a room with two profiles has one unnamed rail — whose panels?")
    assert '=== session.profileId' in inside, (
        "the owner token is handed to profiles the session does not own — "
        "two of the four buttons become refusals")


def test_the_panel_has_its_exits():
    """Field report: "the only way to exit is pressing the same button you
    used to get in." Two exits now — a tap anywhere outside (the scrim),
    and the red close a person can see at the top."""
    rail = (SRC / "TalkRail.tsx").read_text(encoding="utf-8")
    stripped = re.sub(r"/\*.*?\*/", "", rail, flags=re.S)
    scrim_at = stripped.index("talk-panel-scrim")
    assert "setOpen(null)" in stripped[scrim_at:scrim_at + 200], (
        "the scrim no longer closes the panel — tap-outside is decoration")
    close_at = stripped.index("talk-panel-close")
    assert "setOpen(null)" in stripped[close_at:close_at + 300], (
        "the red close no longer closes the panel")
    block = CSS[CSS.index(".talk-panel-close"):]
    block = block[:block.index("}")]
    assert "224, 85, 85" in block, (
        'the close lost its red — "a little red at the top" was the ask')
    scrim = CSS[CSS.index(".talk-panel-scrim"):]
    scrim = scrim[:scrim.index("}")]
    assert "fixed" in scrim and "inset: 0" in scrim, (
        "the scrim no longer covers the screen, so outside is not tappable")


def test_the_paperclip_is_the_phones_own_chooser():
    """Second telling of the same report: "I wanted it just onboard,
    window only — not the full screen at the bottom." The paperclip opens
    the device's chooser (the accept-less input is what makes a phone
    offer photo, camera and file), the handover says so in a line, and
    the carried-things card opens only when asked — with a red close."""
    stripped = re.sub(r"/\*.*?\*/", "", CHAT, flags=re.S)
    stripped = re.sub(r"\{/\*.*?\*/\}", "", stripped, flags=re.S)
    clip = stripped.index("📎")
    assert "docRef.current?.click()" in stripped[clip - 300:clip + 300], (
        "the paperclip is back to a trip to the card at the bottom")
    assert "setBcOpen(true)" not in stripped.replace(
        "setBcOpen((o) => !o)", ""), (
        "a handover still jumps the person to the card")
    card = stripped.index("bc-card")
    assert "talk-panel-close" in stripped[card:card + 400], (
        "the carried-things card has no way out again")
