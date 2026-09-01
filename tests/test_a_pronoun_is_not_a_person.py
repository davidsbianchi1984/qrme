"""Nobody is called "You", and nobody sits in a room who was never there.

## The defect, from a live room

    asked     when I step into an existing room it shows an ON AIR inside
              the frames, but not all of them
    mattered  those frames were PEOPLE, and they were called "You"

A room came back holding four participants: one synthetic profile, the
owner's real seat — `display_name: 'David Bianchi'`, with an account —
and two interactors with `account_id: None`, no picture, and the stored
name `'You'`. Both drew a red ON AIR circle for somebody who had never
been in the room.

Three separate things were wrong, and each one alone would have been
enough:

* the console's onboarding called `POST /interactors` with the literal
  `display_name: "You"` — the word the SURFACE uses for the reader's own
  seat, which is right from exactly one chair and wrong from every other;
* it called it on every pass, with no account to be idempotent on, so
  each visit minted another human being. `accounts.interactor_for` is
  careful about precisely this and says so in its docstring; this door
  simply was not that door;
* nothing on the way in refused the word, so a client could write a
  pronoun into a name column and the room would draw it.

## What this pins

That neither door stores a pronoun, in any of the ten languages the
console ships in, and that a person who has one keeps it. The repair is
pinned separately, and pinned narrowly: it must take out the seats nobody
is in and leave anybody who ever spoke exactly where they are.
"""

from __future__ import annotations

import pytest

from qrme import accounts, db, seed


@pytest.fixture()
def fresh(tmp_path, monkeypatch):
    monkeypatch.setenv("QRME_DB", str(tmp_path / "people.db"))
    db.reset()
    return db.connect()


@pytest.mark.parametrize("given", [
    "You", "you", "  YOU  ", "Tú", "Vous", "Du", "Você", "Tu",
    "あなた", "你", "आप", "أنت", "me", "Myself", "", "   ", None,
])
def test_a_pronoun_never_becomes_a_name(given):
    """Ten languages, because a guard that knows English moves the bug."""
    assert accounts.a_person_name(given) == accounts.UNNAMED


@pytest.mark.parametrize("given", [
    "David Bianchi", "Amara", "Yousef", "Tuomas", "Duncan", "  Lena  ",
])
def test_a_name_survives_the_guard(given):
    """Including names that merely START with a pronoun."""
    assert accounts.a_person_name(given) == given.strip()


def test_the_account_door_stores_a_name_not_a_pronoun(fresh):
    accounts.signup("p@example.test", "a-long-enough-password", "David")
    account = fresh.execute("SELECT id FROM accounts WHERE email=?",
                            ("p@example.test",)).fetchone()["id"]
    person = accounts.interactor_for(account, "You")
    assert person["display_name"] == accounts.UNNAMED

    other = accounts.interactor_for(account, "David Bianchi")
    assert other["id"] == person["id"], (
        "one account, one person — this is the idempotence the other door "
        "did not have")


def test_the_public_door_stores_a_name_not_a_pronoun(fresh):
    from fastapi.testclient import TestClient

    from qrme.api import create_app

    client = TestClient(create_app())
    got = client.post("/interactors", json={"display_name": "You"})
    assert got.status_code == 201, got.text
    assert got.json()["display_name"] == accounts.UNNAMED
    stored = fresh.execute(
        "SELECT display_name FROM interactors WHERE id=?",
        (got.json()["id"],)).fetchone()["display_name"]
    assert stored == accounts.UNNAMED


def test_a_door_that_is_told_no_name_still_opens(fresh):
    """A caller who does not know somebody's name says so."""
    from fastapi.testclient import TestClient

    from qrme.api import create_app

    client = TestClient(create_app())
    got = client.post("/interactors", json={})
    assert got.status_code == 201, got.text
    assert got.json()["display_name"] == accounts.UNNAMED


def _seat(conn, room_id: str, who: str, name: str, account=None) -> None:
    conn.execute(
        "INSERT INTO interactors (id, display_name, account_id, created_at)"
        " VALUES (?,?,?,?)", (who, name, account, db.utcnow()))
    conn.execute(
        "INSERT INTO room_participants (room_id, kind, ref_id)"
        " VALUES (?,'user',?)", (room_id, who))
    conn.commit()


def _room(conn) -> str:
    room_id = db.new_id("room")
    conn.execute(
        "INSERT INTO rooms (id, topic, channel, status, created_at)"
        " VALUES (?,'The Front Porch','chat','active',?)",
        (room_id, db.utcnow()))
    conn.commit()
    return room_id


def test_the_repair_takes_the_empty_seats_out(fresh):
    room_id = _room(fresh)
    _seat(fresh, room_id, "usr_ghost_a", "You")
    _seat(fresh, room_id, "usr_ghost_b", "You")
    fresh.execute(
        "INSERT INTO room_faces (room_id, interactor_id, showing, updated_at)"
        " VALUES (?,?,'camera',?)", (room_id, "usr_ghost_a", db.utcnow()))
    fresh.commit()

    assert seed._unseat_the_nameless(fresh) == 2
    left = fresh.execute(
        "SELECT COUNT(*) AS n FROM room_participants WHERE room_id=?",
        (room_id,)).fetchone()["n"]
    assert left == 0
    # And the camera state that drew ON AIR goes with the seat.
    assert fresh.execute(
        "SELECT COUNT(*) AS n FROM room_faces WHERE interactor_id=?",
        ("usr_ghost_a",)).fetchone()["n"] == 0


def test_the_repair_leaves_a_real_person_where_they_are(fresh):
    room_id = _room(fresh)
    _seat(fresh, room_id, "usr_real", "David Bianchi", account="acc_1")
    _seat(fresh, room_id, "usr_named", "Amara")
    assert seed._unseat_the_nameless(fresh) == 0
    left = fresh.execute(
        "SELECT COUNT(*) AS n FROM room_participants WHERE room_id=?",
        (room_id,)).fetchone()["n"]
    assert left == 2


def test_somebody_who_spoke_is_somebody(fresh):
    """Even nameless and account-less. Speech is the proof of a person."""
    room_id = _room(fresh)
    _seat(fresh, room_id, "usr_spoke", "You")
    fresh.execute(
        "INSERT INTO room_messages (id, room_id, sender_kind, sender_id,"
        " content, status, created_at) VALUES (?,?,'user',?,?,'approved',?)",
        (db.new_id("msg"), room_id, "usr_spoke", "I was here", db.utcnow()))
    fresh.commit()
    assert seed._unseat_the_nameless(fresh) == 0
