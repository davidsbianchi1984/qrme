"""The watching — the platform's own eyes, made at home.

The owner saw a plugin sold on a video feed as "Claude can now watch
videos" and said the whole design brief in four words: **"Let's make our
own then."** There is no secret under a tool like that — pull frames,
hear the soundtrack, hand both to a model — and every part of it was
already in this house: the ears sidecar had ffmpeg, the briefcase had a
comment saying *"these are ears, not eyes"*, and the watch party had a
blindness sentence waiting to be lifted honestly.

What these tests hold:

* the eyes only ever claim what was actually seen — a platform page that
  hands over a player cannot be "watched", a stack without the machinery
  answers held-not-read, and the party's instruction names which senses
  were used;
* a viewing happens once per subject, because a room of eight profiles
  must not watch the same video eight times on the owner's dime;
* every screen that talks grew a way to show — the room's share pill, the
  watch party's panel, the agent's plus menu — and the person is always
  shown what the eyes read.
"""

from __future__ import annotations

import base64
from pathlib import Path

import pytest

from qrme import briefcase, i18n, llm, scrape, watching, watchparty
from tests.test_capabilities import auth_header, make_profile
from tests.test_watchparty import _video_post

REPO = Path(__file__).resolve().parents[1]
EARS = (REPO / "docker" / "ears" / "server.py").read_text()
SCRAPE = (REPO / "qrme" / "scrape.py").read_text()
INSIDE = (REPO / "app" / "src" / "screens" / "Inside.tsx").read_text()
PARTY_TSX = (REPO / "app" / "src" / "screens" / "WatchParty.tsx").read_text()
AGENT_TSX = (REPO / "app" / "src" / "screens" / "Agent.tsx").read_text()
API_TS = (REPO / "app" / "src" / "api.ts").read_text()

#: A one-pixel PNG is a real picture as far as the magic bytes go.
PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4nGNgY"
    "GD4DwABBAEAX+XLSQAAAABJRU5ErkJggg==")


# -- the sidecar grew the doors ----------------------------------------------

def test_the_ears_sidecar_grew_eyes():
    """The frames come from the same container the words do — ffmpeg was
    already there, and one download serves both halves."""
    for needle in ('@app.post("/watch")', '@app.post("/watch-file")',
                   "_frames_from", "ffprobe", "WATCH_FRAMES"):
        assert needle in EARS, f"the sidecar lost {needle}"
    # Centered sampling: neither a title card nor a black closing frame
    # stands for the whole video.
    assert "(2 * i + 1)" in EARS


def test_the_client_pair_matches_the_transcribe_pair():
    assert "def watch_url(" in SCRAPE
    assert "def watch_bytes(" in SCRAPE
    # No sidecar configured answers None — the caller keeps the
    # held-not-watched posture, never an invention.
    import os
    old = os.environ.pop("QRME_EARS_URL", None)
    try:
        assert scrape.watch_url("https://example.com/a.mp4") is None
        assert scrape.watch_bytes(b"x") is None
    finally:
        if old is not None:
            os.environ["QRME_EARS_URL"] = old


# -- what the eyes will and will not read ------------------------------------

def test_the_eyes_know_their_pictures():
    assert watching.image_kind(PNG) == "image/png"
    assert watching.image_kind(b"\xff\xd8\xff\xe0rest") == "image/jpeg"
    assert watching.image_kind(b"RIFF????WEBPrest") == "image/webp"
    # RIFF is shared ground — a WAV is a recording, not a picture.
    assert watching.image_kind(b"RIFF????WAVErest") is None
    assert watching.image_kind(b"GIF89a") is None
    assert watching.image_kind(b"%PDF-1.7") is None


def test_a_platform_page_cannot_be_watched():
    """Fetching youtube.com yields markup, not the recording — a viewing
    built on it would be the lie this module exists to avoid. The refusal
    is the registered sentence, translated like every refusal."""
    with pytest.raises(watching.NothingToWatch) as caught:
        watching.watch_link("https://youtu.be/dQw4w9WgXcQ")
    sentence = str(caught.value)
    assert "hands over a player" in sentence
    assert sentence in i18n._PUBLIC, "the refusal is not registered"


def test_a_viewing_happens_once_per_subject(client, monkeypatch):
    """`client` for the fresh database it brings — a viewing stored in a
    previous run's database is exactly what this test must not read."""
    calls = {"n": 0}

    def fake_watch(url, on_behalf_of=None):
        calls["n"] += 1
        return {"text": "the words", "frames": ["QUJD"],
                "duration_seconds": 12.0, "language": "en"}

    monkeypatch.setattr(scrape, "watch_url", fake_watch)
    monkeypatch.setattr(llm, "look", lambda *a, **k: "a chart on a wall")
    first = watching.watch_link("https://example.com/talk-once.mp4")
    again = watching.watch_link("https://example.com/talk-once.mp4")
    assert calls["n"] == 1, "the same video was fetched twice"
    assert first["heard"] == "the words"
    assert first["seen"] == "a chart on a wall"
    assert again["watched_at"] == first["watched_at"]


def test_missing_machinery_stays_honest(client, monkeypatch):
    monkeypatch.setattr(scrape, "watch_url", lambda *a, **k: None)
    assert watching.watch_link("https://example.com/gone.mp4") is None


# -- the briefcase reads what it held ----------------------------------------

def test_a_shared_picture_is_read(monkeypatch):
    """The branch that answered `held, not read` unconditionally for
    years. A screenshot is the phone's way of handing over its screen."""
    monkeypatch.setattr(watching, "see_picture",
                        lambda data: "a settings page, dark mode on")
    kind, text, read = briefcase.read_file(PNG, "shot.png")
    assert (kind, read) == ("photo", True)
    assert "settings page" in text


def test_a_blind_stack_keeps_the_old_posture(monkeypatch):
    monkeypatch.setattr(watching, "see_picture", lambda data: "")
    kind, text, read = briefcase.read_file(PNG, "shot.png")
    assert (kind, text, read) == ("photo", "", False)


def test_a_shared_video_carries_both_halves(monkeypatch):
    monkeypatch.setattr(watching, "observe_bytes",
                        lambda data, who=None: ("the words said",
                                                "a person at a desk"))
    fake_mp4 = b"\x00\x00\x00\x18ftypmp42" + b"\x00" * 32
    kind, text, read = briefcase.read_file(fake_mp4, "clip.mp4")
    assert (kind, read) == ("video", True)
    assert "the words said" in text
    assert "What is on screen: a person at a desk" in text


# -- the party's blindness lifts in honest steps ------------------------------

def test_the_instruction_names_the_senses_used(client, monkeypatch):
    me, post = _video_post(client)
    party = watchparty.start(post["id"], "person_1")
    url = party["video"]["url"]

    # Unwatched: the blindness sentence, exactly as it always was.
    ctx = watchparty.prompt_context(party["id"])
    assert ctx["you_have_not_seen_it"] is True
    assert ctx["instruction"] == watchparty.BLINDNESS

    # Heard only: the profile is told it heard, not saw.
    watching._store(url, "the soundtrack's words", "", 60.0, "en")
    ctx = watchparty.prompt_context(party["id"])
    assert ctx["you_have_not_seen_it"] is True
    assert ctx["instruction"] == watchparty.HEARING
    assert ctx["watching"]["transcript_available"] is True
    assert ctx["watching"]["description_available"] is False
    assert ctx["watching"]["heard"] == "the soundtrack's words"

    # Seen: watched, and told what it actually holds.
    watching._store(url, "the soundtrack's words",
                    "a whiteboard filling with arrows", 60.0, "en")
    ctx = watchparty.prompt_context(party["id"])
    assert ctx["you_have_not_seen_it"] is False
    assert ctx["instruction"] == watchparty.SIGHT
    assert ctx["watching"]["description_available"] is True
    assert "whiteboard" in ctx["watching"]["seen"]
    # The outer shape never changed — the strict-set guard in
    # test_watchparty.py holds in every state.
    assert set(ctx) == {"watching", "position_s", "playing", "recent",
                        "you_have_not_seen_it", "instruction"}


def test_the_party_watch_door_refuses_a_player(client):
    me, post = _video_post(client)
    party = watchparty.start(post["id"], me["id"])
    r = client.post(f"/watch-parties/{party['id']}/watch",
                    headers=auth_header(me))
    assert r.status_code == 422
    assert "hands over a player" in r.json()["detail"]


def test_the_party_watch_door_is_members_only(client):
    me, post = _video_post(client)
    party = watchparty.start(post["id"], "person_1")
    stranger = make_profile(client, display_name="Outside")
    r = client.post(f"/watch-parties/{party['id']}/watch",
                    headers=auth_header(stranger))
    assert r.status_code == 403


# -- the agent's eye ----------------------------------------------------------

def test_the_agent_refuses_what_its_eyes_cannot_read(client):
    me = make_profile(client, display_name="Owner")
    r = client.post(f"/profiles/{me['id']}/authoring/turn",
                    json={"said": "look at this",
                          "shown": base64.b64encode(b"%PDF-1.7 junk")
                                   .decode("ascii")},
                    headers=auth_header(me))
    assert r.status_code == 422
    assert "JPEG, PNG and WebP" in r.json()["detail"]


def test_the_agent_says_when_the_seeing_door_is_closed(client, monkeypatch):
    monkeypatch.setattr(watching, "see_picture", lambda data: "")
    me = make_profile(client, display_name="Owner")
    r = client.post(f"/profiles/{me['id']}/authoring/turn",
                    json={"said": "look at this",
                          "shown": base64.b64encode(PNG).decode("ascii")},
                    headers=auth_header(me))
    assert r.status_code == 503
    assert "seeing door is closed" in r.json()["detail"]


def test_the_agent_answers_to_what_is_on_the_picture(client, monkeypatch):
    """The account rides WITH the words, labelled for what it is, and it
    comes back beside the reply so the person can read exactly what their
    agent was told."""
    told = {}

    def fake_converse(said, history, **kw):
        told["said"] = said
        return {"reply": "I see it.", "acted": [], "stopped": None,
                "asks": None}

    from qrme import authoring
    monkeypatch.setattr(watching, "see_picture",
                        lambda data: "an error dialog, code 500")
    monkeypatch.setattr(authoring, "converse", fake_converse)
    me = make_profile(client, display_name="Owner")
    r = client.post(f"/profiles/{me['id']}/authoring/turn",
                    json={"said": "what is wrong here?",
                          "shown": base64.b64encode(PNG).decode("ascii")},
                    headers=auth_header(me))
    assert r.status_code == 200
    assert r.json()["seen"] == "an error dialog, code 500"
    assert "error dialog, code 500" in told["said"]
    assert "as read by the platform's eyes" in told["said"]
    assert told["said"].startswith("what is wrong here?"), (
        "the person's own words must come first, unrewritten")


# -- every screen that talks grew a way to show -------------------------------

def test_the_doors_stand_on_the_screens():
    # The room: the share pill's screen button, gated on the browser
    # actually holding the door (iOS Safari does not).
    assert "ins.screen" in INSIDE
    assert "getDisplayMedia" in INSIDE
    # The party: the watch chip and the viewing it renders.
    for needle in ("wp.watch", "watchPartyWatch", "wp.seen", "wp.heard"):
        assert needle in PARTY_TSX, f"the party panel lost {needle}"
    # The agent: both show doors, and the account read back to the person.
    for needle in ("agent.show.pic", "agent.show.screen", "seenNote"):
        assert needle in AGENT_TSX, f"the agent lost {needle}"
    # One binding each, on the wire.
    assert "watchPartyWatch" in API_TS
    assert "shown" in API_TS


def test_a_grab_is_a_frame_not_a_feed():
    """Both grab doors stop the tracks the moment the still is taken —
    showing a screen is a statement, not a surveillance stream."""
    for screen in (INSIDE, AGENT_TSX):
        grab = screen.split("getDisplayMedia", 2)[-1]
        assert ".stop()" in grab[:1600], "the capture was left running"


def test_the_refusals_speak_ten_languages():
    for sentence in (
        "that platform hands over a player, not the recording — only "
        "a direct video or audio link can be watched",
        "the deployment's ears are not answering — the recording "
        "stays held, not watched",
        "the eyes read JPEG, PNG and WebP pictures — this file "
        "is none of them",
        "this deployment's seeing door is closed — no vision "
        "key is configured",
        "this party has no video link to watch",
    ):
        assert sentence in i18n._PUBLIC, f"unregistered: {sentence}"
        assert len(i18n._PUBLIC[sentence]) == 9, f"missing tongues: {sentence}"
