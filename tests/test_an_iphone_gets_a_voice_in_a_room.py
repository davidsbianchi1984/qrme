"""The door an iPhone needs.

The room has listened through the browser's own recogniser and nothing else.
On iOS the `webkitSpeechRecognition` constructor exists and the service
always refuses, so a person holding the phone this product is mostly used on
could hear a room and never speak in one. Reported twice. 1.4.1 could only
make the refusal say its own name, which is honest and is not a voice.

    asked     can this browser hear you
    mattered  can this browser reach a transcriber

`POST /rooms/{id}/heard` is the second answer: recorded speech in, words out,
audio not stored. The console records through `getUserMedia` — which is also
where the browser's own echo cancellation lives, and an analyser to tell a
person leaning in from a speaker across the table — and posts the bytes here.

Deliberately **only** the hearing. What comes back goes through the existing
say door, so moderation, the echo window and the speaking rules stay in the
one place that owns them. A route that heard and said in one breath would be
a second way into the transcript carrying its own copy of those rules to
drift out of step with.
"""

from __future__ import annotations

import pytest

from tests.test_capabilities import (as_interactor, make_interactor,  # noqa: F401
                                     make_profile, pdi_pair)

AUDIO = b"\x1aE\xdf\xa3" + b"pretend webm" * 32


@pytest.fixture()
def room(client):
    """A room with a person in it, and that person's own token.

    The speaker is authorised as the *interactor*, not as the profile's
    owner — the same door the share test walks through, and the reason a
    room id on a sticker is not a way to spend somebody's transcription.
    """
    user = make_interactor(client, "Theo", "1990-01-01")
    dana = make_profile(client)
    r = client.post("/rooms", json={"channel": "chat", "participants": [
        {"kind": "user", "id": user},
        {"kind": "profile", "id": dana["id"]}]})
    assert r.status_code == 201, r.text
    return user, r.json()["id"], as_interactor(user)


def test_a_deployment_with_no_ears_says_so(client, room):
    """Silence would be read as "it didn't hear me" by somebody who has just
    spoken into their phone. The true answer — that this deployment has
    nowhere to send the audio — is one an owner can act on and a guest
    cannot guess."""
    user, rid, mine = room
    r = client.post(f"/rooms/{rid}/heard",
                    params={"interactor_id": user}, content=AUDIO, headers=mine)
    assert r.status_code == 503, r.text
    said = r.json()["detail"]
    assert "QRME_EARS_URL" in said, (
        "the refusal does not name what is missing, so the owner cannot fix it")
    assert "type instead" in said, (
        "the refusal does not say what still works — a person who cannot "
        "speak in a room can still write in it")


def test_the_words_come_back(client, room, monkeypatch):
    from qrme import scrape
    monkeypatch.setattr(scrape, "transcribe_bytes",
                        lambda data, on_behalf_of=None: {"text": "I sleep badly."})
    user, rid, mine = room
    r = client.post(f"/rooms/{rid}/heard",
                    params={"interactor_id": user}, content=AUDIO, headers=mine)
    assert r.status_code == 200, r.text
    assert r.json()["text"] == "I sleep badly."


def test_hearing_does_not_say(client, room, monkeypatch):
    """The transcript is the say door's business.

    One door for speaking. A route that both heard and said would own a
    second copy of the moderation and echo rules, and the copy is the one
    that goes stale.
    """
    from qrme import scrape
    monkeypatch.setattr(scrape, "transcribe_bytes",
                        lambda data, on_behalf_of=None: {"text": "I sleep badly."})
    user, rid, mine = room
    before = client.get(f"/rooms/{rid}/transcript").json()
    client.post(f"/rooms/{rid}/heard", params={"interactor_id": user},
                content=AUDIO, headers=mine)
    after = client.get(f"/rooms/{rid}/transcript").json()
    assert after == before, (
        "hearing put words in the transcript — that is the say door's job, "
        "and its rules")


def test_empty_audio_is_refused(client, room):
    user, rid, mine = room
    r = client.post(f"/rooms/{rid}/heard",
                    params={"interactor_id": user}, content=b"", headers=mine)
    assert r.status_code == 422


def test_a_stranger_cannot_spend_the_deployments_transcription(client, room):
    """The same door sharing a file draws. A room id on a printed sticker is
    not a way to put words in a transcript, and it is not a way to spend
    somebody else's transcription bill either."""
    _, rid, _ = room
    outsider = make_interactor(client, "Sam", "1990-01-01")
    r = client.post(f"/rooms/{rid}/heard",
                    params={"interactor_id": outsider}, content=AUDIO,
                    headers=as_interactor(outsider))
    assert r.status_code == 403, r.text


def test_a_closed_room_does_not_listen(client, room):
    from qrme import db

    user, rid, mine = room
    # Closed straight in the table, the way this suite's other closed-room
    # cases do it — what is under test is what a closed room refuses, not
    # which door closed it.
    conn = db.connect()
    conn.execute("UPDATE rooms SET status='closed' WHERE id=?", (rid,))
    conn.commit()
    r = client.post(f"/rooms/{rid}/heard",
                    params={"interactor_id": user}, content=AUDIO, headers=mine)
    assert r.status_code == 409, r.text


# --- the console side: two ears, and the one that works is chosen ---------

import re  # noqa: E402
from pathlib import Path  # noqa: E402


def _root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


SRC = _root() / "app" / "src"


def _stripped(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"^\s*//.*$", "", text, flags=re.M)


def test_the_microphone_button_asks_whether_you_can_be_heard() -> None:
    """Not whether a constructor exists.

        asked     does this browser have a recogniser
        mattered  can this person speak in the room

    iOS answers yes to the first and no to the second, and the button was
    reading the first — so the phone this product is mostly used on was
    shown a room it could not talk in.
    """
    code = _stripped(SRC / "screens" / "Inside.tsx")
    gate = re.search(r"const canDictate = ([^;]+);", code)
    assert gate, "canDictate moved — this guard reads it by name"
    assert "canRecord()" in gate.group(1), (
        "the microphone button appears only where a recogniser exists, so a "
        "browser that could record perfectly well is shown no way to speak")


def test_a_platform_that_refuses_its_recogniser_hands_over(root=None) -> None:
    """`service-not-allowed` is iOS every time. With a second ear standing
    by, that is a fork in the road rather than a dead end — and the person
    is told nothing, because nothing was lost."""
    code = _stripped(SRC / "screens" / "Inside.tsx")
    assert re.search(r'service-not-allowed"\s*&&\s*canRecord\(\)', code), (
        "a platform refusing its own recogniser still ends the ear, even "
        "where this console could have recorded instead")
    assert "recorderOnly" in code, (
        "nothing remembers that this platform refuses, so every press pays "
        "to discover it again")


def test_the_recorded_ear_never_restarts_into_a_refusal() -> None:
    """The defect this room has had twice, once per ear: a microphone that
    reopens into a refusal, forever, with the light on."""
    code = _stripped(SRC / "screens" / "Inside.tsx")
    loop = re.search(r"async function standRecordedEar\(\)([\s\S]*?)\n  \}",
                     code)
    assert loop, "the recorded ear moved — this guard reads it by name"
    body = loop.group(1)
    assert "wantTalking.current = false" in body, (
        "a failure in the recorded ear leaves the person's decision "
        "standing, so the loop opens the microphone again into the same "
        "refusal")
    assert "nothing was heard in that" in body, (
        "the recorded ear treats quiet as a failure and stops — a standing "
        "ear opens again when nobody spoke")


def test_a_recorded_turn_keeps_its_barge_in() -> None:
    """The whole reason to record rather than only to transcribe.

    The time gate exists because the recogniser has no analyser and cannot
    tell a person leaning in from a speaker across the table. The recorded
    ear has one and already ruled, so applying the gate to it would throw
    away the interruption it just correctly recognised.
    """
    code = _stripped(SRC / "screens" / "Inside.tsx")
    send = re.search(r"function sendPending\(([^)]*)\)([\s\S]*?)\n  \}", code)
    assert send, "sendPending moved — this guard reads it by name"
    assert send.group(1).strip(), (
        "sendPending cannot tell which ear brought the words, so the "
        "recorded ear's barge-in is dropped by a gate written for the other")
    assert re.search(r"!barged\s*&&", send.group(2)), (
        "the time gate is applied to every ear, including the one with an "
        "analyser in front of it")
    assert "isEcho(" in send.group(2), (
        "the text net was dropped — it still catches what the clock misses")


def test_the_recording_asks_for_echo_cancellation_by_name() -> None:
    """The one echo defence that works on sound rather than on words or on
    clocks. It only exists on a stream this console opened, which is the
    other reason recording is worth having where a recogniser works."""
    ear = _stripped(SRC / "roomear.ts")
    assert "echoCancellation: true" in ear, (
        "the recorded stream does not ask for echo cancellation, so the "
        "speaker bleeds into the microphone with nothing in the way")
    assert "BARGE_PEAK" in ear and "QUIET_FLOOR" in ear, (
        "one threshold whether or not the room is speaking means the "
        "profile's own voice reads as somebody talking")


def test_silence_never_reaches_the_transcriber() -> None:
    """A transcriber invents words out of silence — the sibling product
    watched a specialist answer "thank you" to an empty room, each invented
    turn resetting the clock that should have closed it."""
    ear = _stripped(SRC / "roomear.ts")
    stop = re.search(r"rec\.onstop = async \(\) => \{([\s\S]*?)\n    \};", ear)
    assert stop, "the recording's stop handler moved"
    assert "voiced" in stop.group(1), (
        "a recording the analyser never saw cross the voice threshold is "
        "still sent to be transcribed")
