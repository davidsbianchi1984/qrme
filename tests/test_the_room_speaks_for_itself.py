"""The room can be heard without pressing, and spoken to without typing.

Field report over the room screen: the 🔊 press-per-turn was liked, and
sent back anyway — "you should be able to hear the audio anyways without
having to press the button", the composer should take speech and not only
typing, and a button that is only a send "could be a lot smaller".

    asked     can the room be in your ears and your voice in the room
    mattered  a conversation surface that only reads and types is a
              transcript with a delay

The shape that keeps the autoplay rules honest: hearing the room is a
toggle — one press, the gesture the browser wants — and after it every
profile turn that ARRIVES speaks in its bound voice. This file pins the
edges that made that honest rather than merely loud.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
INSIDE = (REPO / "app/src/screens/Inside.tsx").read_text(encoding="utf-8")


def test_hearing_the_room_is_a_remembered_choice():
    assert 'localStorage.getItem("qrme.room.hear")' in INSIDE
    assert 'localStorage.removeItem("qrme.room.hear")' in INSIDE, (
        "the toggle can be switched on but never off — that is not a "
        "choice, it is a ratchet pointed at the person")


def test_the_backlog_stays_silent():
    """Switching the ear on speaks what comes next, not the scrollback: the
    enable records the last turn already on screen as already heard."""
    m = re.search(r"function flipHearAll\(\)(.*?)\n  \}", INSIDE, re.S)
    assert m, "flipHearAll is gone from the room screen"
    assert "transcript[transcript.length - 1].id" in m.group(1), (
        "enabling the ear does not mark the backlog heard — switching it "
        "on would replay everything ever said in the room")


def test_one_voice_at_a_time():
    assert "speaking.current" in INSIDE, (
        "the speak queue has no lock — a reload mid-playback starts a "
        "second voice over the first")


def test_a_withheld_autoplay_ends_quietly():
    # The play call moved into the shared piece-by-piece helper
    # (app/src/spoken.ts) when replies stopped being one utterance; the
    # property protected here rides with it.
    spoken = (REPO / "app/src/spoken.ts").read_text(encoding="utf-8")
    assert re.search(r"sound\.play\(\)\.catch\(", spoken), (
        "a rejected play crashes the queue — the browser is allowed to "
        "say no, and the per-turn button is the answer when it does")


def test_the_press_per_turn_survives():
    """The toggle is an addition, not a replacement: every profile line
    keeps its own 🔊, which is also the fallback when autoplay refuses."""
    assert 'tr("ins.hear", lang)' in INSIDE


def test_a_voice_room_is_a_voice_room():
    """Field report, holding a `voice` room up against what it drew:
    "this is supposed to be audio chat only — get rid of the type bar and
    the transparent chat text and go back to hearing the voices." The
    channel was chosen on the way in and then ignored: every room wore
    the chat furniture, and hearing was an opt-in press."""
    assert 'const spokenRoom = channel === "voice"' in INSIDE, (
        "the room screen no longer asks what kind of room it is — the "
        "channel is a badge on the way in and nothing after it")
    assert "spokenRoom ? voiceBar : chatStrip" in INSIDE, (
        "a voice room wears the typed chat strip again")
    assert INSIDE.count("spokenRoom ? voiceBar : chatStrip") == 2, (
        "the flat scene and the stage must agree — stepping onto the "
        "stage is not stepping back into a chat room")
    assert "{!spokenRoom && (" in INSIDE, (
        "the card's typed composer is offered in a voice room")


def test_a_voice_room_arrives_speaking():
    """Going in is itself the press the autoplay rules want, so a room
    whose whole pitch is sound must not also demand the 🔊 toggle."""
    m = re.search(r"useEffect\(\(\) => \{\s*if \(spokenRoom\) "
                  r"setHearAll\(true\);\s*\}, \[spokenRoom, open\]\)", INSIDE)
    assert m, ("a voice room no longer turns its own ear on — it arrives "
               "silent with a toggle nobody was told to press")


def test_talking_into_a_voice_room_reaches_the_room():
    """Dictation's "the send stays a decision" bargain is right for a room
    people TYPE in. Here speaking IS the medium, and a send button between
    a spoken sentence and the room is the keyboard wearing a hat.

    Re-pointed when the ear became a STANDING one. The claim is unchanged
    and still the point — what the recogniser hears reaches the room — but
    it is no longer one function's job: `startTalking` opens the ear and
    `sendPending` commits what it heard after the person's silence, so
    `flipTalking` is now a two-line mute. A guard pinned to the old shape
    was testing the shape rather than the claim.
    """
    start = re.search(r"function startTalking\(\)([\s\S]*?)\n  \}", INSIDE)
    assert start, "the talk control is gone from the room screen"
    send = re.search(r"function sendPending\(\)([\s\S]*?)\n  \}", INSIDE)
    assert send, "nothing commits what the ear heard"
    assert "api.sayInRoom(" in send.group(1), (
        "what the recogniser hears must reach the room, not a draft box")
    assert "sendPending" in start.group(1), (
        "the ear hears and nothing carries it to the room")
    assert "dictation.current?.stop()" in start.group(1), (
        "one microphone: starting to talk must stop dictation, or two "
        "recognisers fight over it")


def test_a_browser_with_no_recogniser_still_has_a_way_in():
    """iOS Safari ships none. A voice room with no way to speak and no
    way to type is a locked door with a picture of a room behind it."""
    assert 'tr("ins.voice.notalk", lang)' in INSIDE, (
        "the no-recogniser case says nothing — the person is left with a "
        "silent room and no explanation")
    bar = INSIDE[INSIDE.index("const voiceBar = ("):]
    bar = bar[:bar.index("\n  );")]
    fallback = bar[bar.index("canDictate ? ("):]
    assert "rs-chatpill" in fallback, (
        "the typed pill must come back where the recogniser is absent")
    assert "rs-talk" in bar[:bar.index("canDictate ? (") + 400], (
        "the talk control is gone from the voice bar")


def test_the_talk_control_lets_go_with_the_room():
    m = re.search(r"useEffect\(\(\) => \(\) => \{([\s\S]*?)\}, \[open\]\)",
                  INSIDE)
    assert m and "talkRec.current?.stop()" in m.group(1), (
        "leaving or switching rooms leaves the microphone held open")


def test_the_room_keeps_itself_current():
    """Without the poll, another person's turn arrived only when the
    viewer did something — a room you have to poke to hear is not a room.
    The ear and the talking light both feed on the transcript, so this is
    also what makes them live."""
    assert re.search(
        r"setInterval\([\s\S]{0,200}?api\.roomMessages\(open, token\)"
        r"\.then\(setTranscript\)", INSIDE), (
        "the transcript no longer refreshes on its own — turns from the "
        "other people in the room wait for the viewer to act")
    m = re.search(r"setInterval\(([\s\S]*?)\}, (\d+)\)", INSIDE)
    assert m and "setError" not in m.group(1), (
        "a failing poll must stay quiet — an error banner repainted every "
        "few seconds is a nag, not a diagnosis")


def test_the_light_follows_the_voice():
    """While a backlog is being read aloud, the transcript's last line is
    not who is speaking — three queued turns would light the wrong square
    until the reading caught up. The voice being HEARD wins the light,
    and the transcript's last line is only the fallback."""
    assert "voicing !== null" in INSIDE, (
        "isTalking reads only the transcript again — the talking light "
        "drifts off the voice whenever turns queue")
    assert re.search(
        r"setVoicing\(\{ kind: \"profile\", id[\s\S]{0,80}?await s\.done",
        INSIDE), (
        "the ear's queue no longer marks whose turn it is reading before "
        "it plays")
    assert INSIDE.count("setVoicing(null)") >= 3, (
        "every way a voice ends — queue drained, press played out, press "
        "failed — must put the light back on the transcript's answer")


def test_dictation_types_and_never_sends():
    m = re.search(r"function flipDictation\(\)(.*?)\n  \}", INSIDE, re.S)
    assert m, "flipDictation is gone from the room screen"
    assert "sayInRoom" not in m.group(1), (
        "dictation sends into the room on its own — speech should land "
        "in the box, and the send stays a decision: a room has other "
        "people in it")
    assert "setDraft" in m.group(1)


def test_the_dead_control_rule():
    """No recogniser (iOS Safari), no button — absent, not disabled."""
    assert "canDictate && (" in INSIDE, (
        "the dictation button renders unconditionally — on iOS Safari it "
        "would be a dead control, a broken promise drawn as a button")


def test_the_send_keeps_its_name():
    """The send shrank to a glyph; the name lives on for screen readers."""
    m = re.search(r"aria-label=\{tr\(\"ins.sayit\", lang\)\}", INSIDE)
    assert m, (
        "the compact send lost its accessible name — smaller may not "
        "mean anonymous")


# -- the gallery's transparent chat, delivered ------------------------------

def test_the_conversation_rides_the_scene_and_the_stage():
    """The gallery drew the chat ON the room (screens 96-98, 105) and the
    live screen parked it in a card below — a field report held the two
    side by side. The strip is one element worn in both places."""
    # Spelled `spokenRoom ? voiceBar : chatStrip` since a voice room
    # started wearing the talk control in the strip's place. The property
    # is unchanged: whatever the conversation looks like, both the flat
    # scene and the stage wear it.
    assert INSIDE.count("chatStrip}") == 2, (
        "the transparent chat strip is not worn by both the flat scene "
        "and the immersive stage")
    assert "rs-chatstrip" in INSIDE
    assert 'tr("ins.type.ph", lang)' in INSIDE


def test_the_light_follows_the_speaker_not_the_name():
    """A person in a room with their own synthetic twin shares a display
    name with it, so the profile's square lit while the person spoke.
    The light keys on sender identity now, and never on the name."""
    assert "talking === s.display" not in INSIDE, (
        "a seat is lit by display-name match again — two participants "
        "can share a name, and one of them is a person")
    assert INSIDE.count("isTalking(s)") >= 3
    assert "lastSaid.sender_id === s.id" in INSIDE


def test_a_profile_is_told_who_said_what():
    """With a person and two profiles in one room, unlabelled history
    collapses into one anonymous interlocutor. Every turn that is not the
    profile's own arrives labelled with its speaker, and the cast is
    named in the system prompt — kinds included."""
    community = (REPO / "qrme/routers/community.py").read_text(
        encoding="utf-8")
    turns = community[community.index("def _profile_turns"):]
    turns = turns[:turns.index("\n@router")]
    assert re.search(
        r"_display\(r\['sender_kind'\], r\['sender_id'\]\)", turns), (
        "the history handed to a profile is unlabelled again — in a "
        "three-party room it cannot know who it is talking to")
    assert "another synthetic profile" in turns
    assert "never speak for anybody but yourself" in turns


def test_somebody_can_be_asked_in_from_the_room():
    assert "api.inviteToRoom(" in INSIDE
    assert "api.acceptRoomInvite(" in INSIDE, (
        "an owned profile cannot be seated from the room screen — the "
        "invite would be fire-and-forget even for your own profile")
