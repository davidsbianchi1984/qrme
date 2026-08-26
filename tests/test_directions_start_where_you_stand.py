"""The guide knows where you are standing (qrme/productmap.py, STANDING).

Field report, with screenshots from two devices in one morning: asked
where to attach a file, a profile described the Chat composer's
briefcase — to somebody standing in a ROOM, whose file door is the
paperclip by the Type box. Asked again, it sent him comparing a
chain-link to a briefcase that was not there. Every door it named
existed; none of them were where the person was.

The product map told the profile what the console holds and nothing
about where the person is holding it from. These hold the other half:
the client says which screen the person is looking at, the prompt says
it in one sentence, and each surface's sender actually sends it.

    asked     does the profile know the console's doors
    mattered  does it know which room the person is asking from
"""

from __future__ import annotations

from pathlib import Path

from qrme import persona, productmap

APP = Path(__file__).resolve().parents[1] / "app" / "src"
CHAT = (APP / "screens" / "Chat.tsx").read_text(encoding="utf-8")


def test_every_standing_key_reaches_the_prompt_as_its_place():
    for key, place in productmap.STANDING.items():
        first = productmap.lines("", standing=key)[0]
        assert place in first and "RIGHT NOW" in first, (
            f"standing={key!r} does not open the block with its place")


def test_an_unknown_standing_says_nothing_rather_than_guessing():
    assert productmap.lines("", standing="the moon") == productmap.lines("")
    assert productmap.lines("", standing=None) == productmap.lines("")


def test_a_turn_among_seats_is_a_room_turn_without_being_told():
    """`among` already says where the person is — the room's reply path
    (routers/community.py) predates `standing` and must not need a second
    parameter to be located."""
    profile = {"anonymous": False, "display_name": "Vivienne",
               "kind": "fictional", "persona": "a stage act",
               "adult_mode": 0, "id": "prf_test",
               "demographics": "{}", "appearance": "",
               "interaction_scope": "reactive", "aging_enabled": 0,
               "base_age": None, "created_at": "2026-01-01T00:00:00Z"}
    system = persona.build_system_prompt(profile, None, None, among=[])
    assert productmap.STANDING["room"] in system


def test_the_chat_screen_says_which_of_its_two_faces_is_up():
    """The talk face and the typed screen are different rooms to give
    directions in — the send names whichever is up."""
    assert 'standing: talking ? "talk" : "chat"' in CHAT, (
        "the chat screen no longer says where the person is standing")


def test_the_agent_prompt_stands_on_the_agent_screen():
    src = (Path(__file__).resolve().parents[1] / "qrme"
           / "authoring.py").read_text(encoding="utf-8")
    assert 'productmap.block(said, standing="agent")' in src


def test_the_wire_carries_standing_apart_from_surface():
    """`surface` names a registered display and refuses unknown ones;
    `standing` names a screen and must never be routed through that
    refusal."""
    from qrme.models import ChatRequest

    req = ChatRequest(interactor_id="usr_x", message="where is the file door",
                      standing="room")
    assert req.standing == "room" and req.surface is None
