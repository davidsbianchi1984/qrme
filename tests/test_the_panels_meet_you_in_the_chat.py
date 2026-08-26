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
    assert stripped.count("<TalkRail") >= 2, (
        "the four panels are back to being a voice-only feature")
    dock = stripped[stripped.index('className="chat-rail-dock"') - 200:
                    stripped.index('className="chat-rail-dock"')]
    assert "!talking" in dock, (
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
