"""The checked-likeness mark belongs to the human seat, never the AI one.

## The defect, photographed and sent back in one line

    asked     verified is on the wrong seat, it should be on the one
              that says You
    mattered  it was on the seat that says AI

A room held two seats with the same name: a person, and the synthetic
profile built in their likeness. The synthetic one wore the sparkle that
says *this is a rendering* AND the gold plate that says *this likeness is
checked*, on the same circle. The human beside it, showing an actual
photograph of an actual person, wore nothing.

On this platform that is not a cosmetic fault. The gold plate is the one
claim the product exists to make carefully, and a seat that has already
declared itself synthetic cannot make it.

Two separate rules were wrong at once:

* a **profile** seat was marked from the profile's own verification
  record, without asking what the seat was drawing — and in a room a
  profile seat draws its AI portrait;
* a **person's** seat was marked only from a picture put up through the
  room, so somebody who set their face on the Identity screen — whose
  seat draws from `pictures_in` — was never even asked about.

## What this pins

That the mark follows the FACE the seat is drawing, and that no seat
carrying the AI mark can ever also carry the gold one. The second is the
one worth a test on its own: every other rule here could be rewritten for
a good reason, and that one cannot.
"""

from __future__ import annotations

import pytest

from qrme import accounts, auth, avatars, db, roomface, seed, verification
from qrme.routers.community import _verified


@pytest.fixture()
def room(tmp_path, monkeypatch):
    """A person and their synthetic twin, seated together."""
    monkeypatch.setenv("QRME_DB", str(tmp_path / "seats.db"))
    db.reset()
    seed.seed()
    conn = db.connect()

    def profile_of(handle: str) -> str:
        row = conn.execute("SELECT profile_id FROM handles WHERE handle=?",
                           (handle,)).fetchone()
        assert row is not None, f"no {handle} in the starter collection"
        return row["profile_id"]

    twin = profile_of(seed.FOUNDER_HANDLE)
    likeness = profile_of(seed.VERIFIED_HANDLE)

    accounts.signup("seat@example.test", "a-long-enough-password", "David")
    account = conn.execute("SELECT id FROM accounts WHERE email=?",
                           ("seat@example.test",)).fetchone()["id"]
    person = accounts.interactor_for(account, "David")

    room_id = db.new_id("room")
    conn.execute(
        "INSERT INTO rooms (id, topic, channel, status, created_at)"
        " VALUES (?,?,'chat','active',?)",
        (room_id, "Rounds", db.utcnow()))
    for kind, ref in (("user", person["id"]), ("profile", twin)):
        conn.execute(
            "INSERT OR IGNORE INTO room_participants (room_id, kind, ref_id)"
            " VALUES (?,?,?)", (room_id, kind, ref))
    conn.commit()
    return {"room": room_id, "person": person["id"], "twin": twin,
            "likeness": likeness, "account": account, "conn": conn}


def _checked(profile_id: str) -> None:
    verification.verify(profile_id, "document",
                        attestor="A named attestor", method="passport")


def test_a_synthetic_seat_never_wears_the_gold_plate(room):
    """Even with a verification record of its own. Especially then."""
    _checked(room["twin"])
    assert verification.status(room["twin"])["verified"], (
        "the record has to exist for this test to mean anything")
    assert _verified("profile", room["twin"], room["room"]) is False


def test_the_person_showing_their_checked_likeness_wears_it(room):
    """The picture that follows them between rooms is asked about too."""
    _checked(room["likeness"])
    room["conn"].execute(
        "UPDATE interactors SET avatar_url=? WHERE id=?",
        (f"{avatars.PHOTO_ROUTE}/{seed.VERIFIED_HANDLE}.webp",
         room["person"]))
    room["conn"].commit()
    assert _verified("user", room["person"], room["room"]) is True


def test_a_person_with_no_checked_likeness_wears_nothing(room):
    """The plate is a fact about a face, not a courtesy to a human.

    The record comes off rather than the picture: the starter collection
    ships this handle already checked — that is what the handle is FOR —
    so pointing a seat at some other photograph would prove the file name
    matters rather than that the record does.
    """
    room["conn"].execute("DELETE FROM profile_verification WHERE profile_id=?",
                         (room["likeness"],))
    room["conn"].commit()
    assert not verification.status(room["likeness"])["verified"], (
        "the record has to be gone for this test to mean anything")
    room["conn"].execute(
        "UPDATE interactors SET avatar_url=? WHERE id=?",
        (f"{avatars.PHOTO_ROUTE}/{seed.VERIFIED_HANDLE}.webp",
         room["person"]))
    room["conn"].commit()
    assert _verified("user", room["person"], room["room"]) is False


def test_a_seat_on_camera_makes_no_claim(room):
    """There is no still face to have checked."""
    _checked(room["likeness"])
    room["conn"].execute(
        "UPDATE interactors SET avatar_url=? WHERE id=?",
        (f"{avatars.PHOTO_ROUTE}/{seed.VERIFIED_HANDLE}.webp",
         room["person"]))
    room["conn"].commit()
    roomface.set_showing(room["room"], room["person"], "camera")
    assert _verified("user", room["person"], room["room"]) is False


def test_a_person_showing_something_else_is_not_making_the_claim(room):
    """A put-up picture that is not the checked likeness carries no plate."""
    _checked(room["likeness"])
    roomface.set_showing(room["room"], room["person"], "photo",
                         media_url="/media/some-other-picture.webp")
    assert _verified("user", room["person"], room["room"]) is False
