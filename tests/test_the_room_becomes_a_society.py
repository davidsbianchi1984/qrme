"""The room becomes a society — the 2.0.1 round, in the owner's words.

Aimed turns instead of eight simultaneous answers; rotation by seat that
carries on past the person's silent chair; the agentic join; the summons;
the ten-turn governor with a words-only release. Every rule here is a
sentence of the owner's, quoted where it is enforced — see
qrme/society.py for the full set.
"""

from __future__ import annotations

import pytest

from qrme import db, llm, society
from tests.test_community import as_interactor, make_interactor, make_profile


def _mixed_room(client, *names):
    """One person and named profiles, seated in order."""
    user = make_interactor(client, "Theo", "1990-01-01")
    profiles = [make_profile(client, display_name=n, kind="fictional",
                             persona=f"{n}, a thoughtful conversationalist.")
                for n in names]
    room = client.post("/rooms", json={
        "topic": "the long view", "channel": "chat",
        "participants": [{"kind": "user", "id": user}]
        + [{"kind": "profile", "id": p["id"]} for p in profiles]}).json()
    return user, profiles, room


# -- the aim ------------------------------------------------------------------

CAST = [{"ref_id": "p1", "display": "Ada Lovelace"},
        {"ref_id": "p2", "display": "Echo"},
        {"ref_id": "p3", "display": "Ada Palmer"}]


def test_a_message_aims_by_name():
    assert society.aim_of("Echo: what do you think?", CAST)["ref_id"] == "p2"
    assert society.aim_of("echo, your turn", CAST)["ref_id"] == "p2"
    assert society.aim_of("I agree with @echo here", CAST)["ref_id"] == "p2"
    assert society.aim_of("what does Echo make of it", CAST)["ref_id"] == "p2"


def test_a_shared_first_name_falls_back_to_the_room():
    """Two Adas: guessing between them would answer as the wrong person,
    so the message goes to the room and rotation decides."""
    assert society.aim_of("Ada: which of you said that?", CAST) is None
    assert society.aim_of("morning everyone", CAST) is None
    assert society.aim_of("", CAST) is None


def test_the_longest_name_wins():
    assert society.aim_of("Ada Lovelace: the engine, please",
                          CAST)["ref_id"] == "p1"


# -- the markers a profile's turn carries -------------------------------------

def test_the_aim_marker_is_parsed_off_the_front():
    content, aim = society.split_aim("[to: Echo] I think the garden wins.")
    assert aim == "Echo"
    assert content == "I think the garden wins."
    content, aim = society.split_aim("no marker here")
    assert aim is None and content == "no marker here"


def test_the_summons_marker_is_parsed_out():
    content, names = society.split_summons(
        "We need a historian. [invite: Ada Palmer] She would know.")
    assert names == ["Ada Palmer"]
    assert "[invite:" not in content


# -- who speaks next ----------------------------------------------------------

def _hist(*rows):
    return [{"sender_kind": k, "sender_id": s, "aimed_at": a}
            for k, s, a in rows]


def test_an_aimed_message_is_answered_by_its_target():
    history = _hist(("user", "u1", "Echo"))
    assert society.next_speaker(CAST, history, {}, False)["ref_id"] == "p2"


def test_rotation_takes_the_seat_after_the_last_speaker():
    history = _hist(("user", "u1", None), ("profile", "p2", None))
    assert society.next_speaker(CAST, history, {}, False)["ref_id"] == "p3"
    # ...and wraps past the last seat back to the first.
    history = _hist(("profile", "p3", None))
    assert society.next_speaker(CAST, history, {}, False)["ref_id"] == "p1"


def test_a_profile_does_not_answer_its_own_aim():
    """Echo aimed a question at nobody-in-particular-by-name that matched
    itself — the rotation moves on rather than letting a seat soliloquise
    through the aim rule."""
    history = _hist(("profile", "p2", "Echo"))
    chosen = society.next_speaker(CAST, history, {}, False)
    assert chosen["ref_id"] != "p2"


def test_the_governor_skips_a_seat_at_ten_and_pauses_at_all_ten():
    counts = {"p1": society.GOVERNOR, "p2": 3, "p3": society.GOVERNOR}
    history = _hist(("profile", "p3", None))
    assert society.next_speaker(CAST, history, counts, False)["ref_id"] == "p2"
    counts["p2"] = society.GOVERNOR
    assert society.next_speaker(CAST, history, counts, False) is None
    # "Or is told to be left uncapped... then it's on the user's choice
    # and dime."
    assert society.next_speaker(CAST, history, counts, True) is not None


# -- the words that replaced the toggle ---------------------------------------

def test_the_control_words_are_pinned():
    """The exact sentences, because they ARE the interface: "users can
    just tell them to talk with each other if they need to, or just
    quietly sit out." A drifted phrase list is a control that stopped
    working with nobody told."""
    assert society.said_talk("you two can talk with each other for a bit")
    assert society.said_release("run in the background while I cook")
    assert society.said_release("no limit tonight")
    assert society.said_pause("ok that's enough for now")
    assert not society.said_release("we have limits to discuss")
    assert not society.said_pause("the pause button era is over")


# -- the routes ---------------------------------------------------------------

def test_an_aimed_message_gets_one_reply_from_its_target(client):
    user, (dana, echo), room = _mixed_room(client, "Dana", "Echo")
    mine = as_interactor(user)
    r = client.post(f"/rooms/{room['id']}/messages", headers=mine,
                    json={"sender_id": user,
                          "message": "Echo: what do you make of this?"})
    assert r.status_code == 201
    replies = r.json()["replies"]
    assert len(replies) == 1
    assert replies[0]["from"] == "Echo"
    assert r.json()["message"]["aimed_at"] == "Echo"


def test_the_governor_pauses_the_room_and_a_person_resumes_it(client):
    user, (dana, echo), room = _mixed_room(client, "Dana", "Echo")
    mine = as_interactor(user)
    client.post(f"/rooms/{room['id']}/messages", headers=mine,
                json={"sender_id": user, "message": "settle in, you two"})
    # The message spent one turn; the advances spend the rest. Ten apiece:
    # twenty unprompted turns stand, and the twenty-first waits.
    for _ in range(2 * society.GOVERNOR - 1):
        r = client.post(f"/rooms/{room['id']}/advance", headers=mine)
        assert r.status_code == 201 and r.json()["paused"] is False
    r = client.post(f"/rooms/{room['id']}/advance", headers=mine)
    assert r.json() == {"replies": [], "paused": True}
    # "Then pauses and waits for user's response to either continue or
    # remains paused" — any word from the person is the continue.
    client.post(f"/rooms/{room['id']}/messages", headers=mine,
                json={"sender_id": user, "message": "carry on"})
    r = client.post(f"/rooms/{room['id']}/advance", headers=mine)
    assert r.json()["paused"] is False


def test_the_release_words_lift_the_governor_and_the_pause_words_restore_it(
        client):
    user, (dana, echo), room = _mixed_room(client, "Dana", "Echo")
    mine = as_interactor(user)
    client.post(f"/rooms/{room['id']}/messages", headers=mine,
                json={"sender_id": user,
                      "message": "run in the background, I'll read later"})
    row = db.connect().execute("SELECT free_run FROM rooms WHERE id=?",
                               (room["id"],)).fetchone()
    assert row["free_run"] == 1
    # Past both governors' worth of turns, because the person said so.
    for _ in range(2 * society.GOVERNOR + 2):
        r = client.post(f"/rooms/{room['id']}/advance", headers=mine)
        assert r.json()["paused"] is False
    client.post(f"/rooms/{room['id']}/messages", headers=mine,
                json={"sender_id": user, "message": "that's enough"})
    row = db.connect().execute("SELECT free_run FROM rooms WHERE id=?",
                               (room["id"],)).fetchone()
    assert row["free_run"] == 0


def test_a_profiles_aimed_turn_hands_the_next_turn_to_its_target(
        client, monkeypatch):
    """The instigated back-and-forth: Dana aims at Echo, so the next
    advance is Echo's — "rotation will continue, even though user isn't
    taking his turn, and will instigate a back-and-forth anyways." """
    user, (dana, echo), room = _mixed_room(client, "Dana", "Echo")
    mine = as_interactor(user)

    class Aimer:
        def generate(self, system, messages):
            return "[to: Echo] Echo, you first."

    monkeypatch.setattr(llm, "get_provider", lambda **kw: Aimer())
    r = client.post(f"/rooms/{room['id']}/advance", headers=mine)
    first = r.json()["replies"][0]
    assert first["aimed_at"] == "Echo"
    assert "[to:" not in first["content"], "the marker leaked into the room"

    class Plain:
        def generate(self, system, messages):
            return "Here I am."

    monkeypatch.setattr(llm, "get_provider", lambda **kw: Plain())
    r = client.post(f"/rooms/{room['id']}/advance", headers=mine)
    assert r.json()["replies"][0]["from"] == "Echo"


def test_a_summons_seats_the_named_profile(client, monkeypatch):
    """"Offer to or be prompted to invite other synthetic profiles of
    relevance to need or topic." The marker seats them — the agentic
    join — and the owner's inbox carries the record."""
    user, (dana, echo), room = _mixed_room(client, "Dana", "Echo")
    wren = make_profile(client, display_name="Wren", kind="fictional",
                        persona="Wren, who knows gardens.")
    mine = as_interactor(user)

    class Summoner:
        def generate(self, system, messages):
            return "We need Wren for this. [invite: Wren]"

    monkeypatch.setattr(llm, "get_provider", lambda **kw: Summoner())
    r = client.post(f"/rooms/{room['id']}/advance", headers=mine)
    assert r.status_code == 201
    assert "[invite:" not in r.json()["replies"][0]["content"]
    seats = db.connect().execute(
        "SELECT ref_id FROM room_participants WHERE room_id=? AND"
        " kind='profile'", (room["id"],)).fetchall()
    assert any(row["ref_id"] == wren["id"] for row in seats), (
        "the summons was an offer nothing honored")


def test_the_prompt_teaches_the_turn_rules(client, monkeypatch):
    """The cast note rides every room prompt: the aim marker, the
    summons, and the collaboration standing — 'as many as users want.'"""
    seen = {}

    class Reader:
        def generate(self, system, messages):
            seen["system"] = system
            return "noted."

    monkeypatch.setattr(llm, "get_provider", lambda **kw: Reader())
    user, (dana, echo), room = _mixed_room(client, "Dana", "Echo")
    client.post(f"/rooms/{room['id']}/advance",
                headers=as_interactor(user))
    assert "[to: Ada]" in seen["system"]
    assert "[invite:" in seen["system"]
    assert "collaborate" in seen["system"]
    assert "Dana" in seen["system"] and "Echo" in seen["system"]


def test_the_summons_respects_the_eight_seats():
    note = society.cast_note([{"ref_id": "x", "display": "X"}])
    assert "[invite:" in note
    assert society.SEATS == 8, "the owner's correction: eight, not six"
    assert society.GOVERNOR == 10, "the owner's number, verbatim"
