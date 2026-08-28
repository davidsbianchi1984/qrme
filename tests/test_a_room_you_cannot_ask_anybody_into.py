"""A room could be opened and walked into, and nobody could be asked in.

## The finding

Rooms had `POST /rooms` to open one, `POST /rooms/{id}/join` to step into a
live one, a microphone, messages and an advance. The standing rooms are
listed for anybody to walk into, which is what the lobby is for.

None of that gets a *particular* person into a *particular* room. The only
ways were to name them in the create body — which requires knowing their id
before the room exists — or to send them the room id by some means this
product does not provide.

    asked     can I open a room
    mattered  can I ask somebody into it

## The invite is the inbox event

There is no invites table. `kind` is `room_invite` and `ref` is the room, so
the row the person reads and the row `accept` checks are the same row. Two
records of one fact is how a withdrawn invite stays acceptable, and how an
accepted one still shows as pending.

## Both halves, or neither

An invite with no acceptance is a notification. `join` seats *interactors*,
so an invited profile could read that it had been asked and have no route to
say yes — the news would arrive and dead-end. The accept is authorized as the
**guest**: a host who could seat somebody from their own screen would make
"invite" a word for something that is not one.
"""

from __future__ import annotations


def _person(client, name="P", birthdate="1990-01-01"):
    row = client.post("/interactors", json={
        "display_name": name, "birthdate": birthdate}).json()
    return row["id"], {"authorization": f"Bearer {row['token']}"}


def _profile(client, account, name="Iris"):
    p = client.post("/profiles", json={
        "owner_id": account, "kind": "fictional", "display_name": name,
        "purpose": "enterprise_agent", "persona": "a calm host",
        "verification": {"birthdate": "1988-03-03"}}).json()
    return p["id"], {"authorization": f"Bearer {p['owner_token']}"}


def _room(client, uid, head, pid, channel="chat"):
    r = client.post("/rooms", headers=head, json={
        "topic": "the roof", "channel": channel,
        "participants": [{"kind": "user", "id": uid},
                         {"kind": "profile", "id": pid}]})
    assert r.status_code == 201, r.text
    return r.json()["id"]


# --- the round trip ---------------------------------------------------------

def test_a_person_in_the_room_can_ask_a_profile_in(client):
    """The agentic join. The owner's field report, verbatim: "invites are
    just sent — no responses and nobody joins... They are agentic, and
    they should respond and jump in on their own with their own frame."
    So the ask IS the arrival: the profile seats itself, speaks an
    arrival turn, and the record lands in its owner's inbox — humans
    keep an inbox; profiles answer for themselves."""
    uid, ada = _person(client, "Ada")
    host, _own = _profile(client, "acct_host")
    rid = _room(client, uid, ada, host)
    guest, guest_own = _profile(client, "acct_guest", "Wren")

    asked = client.post(f"/rooms/{rid}/invite", headers=ada,
                        json={"profile_id": guest})
    assert asked.status_code == 201, asked.text
    assert asked.json()["invited"] is True
    assert asked.json()["seated"] is True
    # The frame jumped in: an arrival turn from the invited profile.
    arrival = asked.json()["arrival"]
    assert arrival and arrival[0]["sender_kind"] == "profile"

    from qrme import db
    seats = db.connect().execute(
        "SELECT ref_id FROM room_participants WHERE room_id=? AND"
        " kind='profile'", (rid,)).fetchall()
    assert any(row["ref_id"] == guest for row in seats)

    # The owner's record: their profile answered an invitation itself.
    box = client.get(f"/profiles/{guest}/inbox", headers=guest_own)
    assert box.status_code == 200, box.text
    joins = [e for e in box.json()["events"] if e["kind"] == "room_joined"]
    assert len(joins) == 1 and joins[0]["ref"] == rid, box.json()
    assert joins[0]["actor_name"] == "Ada", joins[0]


def test_a_profiles_owner_in_the_room_can_ask_somebody_in(client):
    """The other identity `_require_in_room` admits. A room holds two kinds of
    participant and either one is in it."""
    uid, ada = _person(client, "Ada")
    host, host_own = _profile(client, "acct_h2")
    rid = _room(client, uid, ada, host)
    guest, _g = _profile(client, "acct_g2", "Wren")

    asked = client.post(f"/rooms/{rid}/invite", headers=host_own,
                        json={"profile_id": guest})
    assert asked.status_code == 201, asked.text
    assert asked.json()["asked_by"] == host


# --- who may ask ------------------------------------------------------------

def test_somebody_outside_the_room_cannot_ask_anybody_in(client):
    """Inviting into a room you are not in is how a room id becomes a way to
    send mail to strangers."""
    uid, ada = _person(client, "Ada")
    host, _own = _profile(client, "acct_h3")
    rid = _room(client, uid, ada, host)
    guest, _g = _profile(client, "acct_g3", "Wren")
    _sid, stranger = _person(client, "Stranger")

    r = client.post(f"/rooms/{rid}/invite", headers=stranger,
                    json={"profile_id": guest})
    assert r.status_code == 403, r.text
    assert "not in this room" in r.json()["detail"]


def test_an_unidentified_caller_cannot_ask_anybody_in(client):
    uid, ada = _person(client, "Ada")
    host, _own = _profile(client, "acct_h4")
    rid = _room(client, uid, ada, host)
    guest, _g = _profile(client, "acct_g4", "Wren")

    assert client.post(f"/rooms/{rid}/invite",
                       json={"profile_id": guest}).status_code == 401


# --- who may accept ---------------------------------------------------------

def test_the_host_cannot_accept_on_the_guests_behalf(client):
    """The half that makes it an invitation. If the person who sent it could
    also take it up, it would be a seating chart."""
    uid, ada = _person(client, "Ada")
    host, _own = _profile(client, "acct_h5")
    rid = _room(client, uid, ada, host)
    guest, _g = _profile(client, "acct_g5", "Wren")
    client.post(f"/rooms/{rid}/invite", headers=ada,
                json={"profile_id": guest})

    r = client.post(f"/rooms/{rid}/invites/accept", headers=ada,
                    json={"profile_id": guest})
    assert r.status_code in (401, 403), r.text


def test_accepting_without_being_asked_is_refused(client):
    """The room id is on beacons and printed stickers. Holding one is not
    being invited, and this is the route where that would have paid off."""
    uid, ada = _person(client, "Ada")
    host, _own = _profile(client, "acct_h6")
    rid = _room(client, uid, ada, host)
    guest, guest_own = _profile(client, "acct_g6", "Wren")

    r = client.post(f"/rooms/{rid}/invites/accept", headers=guest_own,
                    json={"profile_id": guest})
    assert r.status_code == 403, r.text
    assert "not been asked" in r.json()["detail"]


# --- what a second press does -----------------------------------------------

def test_asking_twice_does_not_send_the_news_twice(client):
    """Under the agentic join the first press already seated them, so a
    second press is the already-in-this-room refusal — and the owner's
    inbox still carries exactly one record of the joining."""
    uid, ada = _person(client, "Ada")
    host, _own = _profile(client, "acct_h7")
    rid = _room(client, uid, ada, host)
    guest, guest_own = _profile(client, "acct_g7", "Wren")

    first = client.post(f"/rooms/{rid}/invite", headers=ada,
                        json={"profile_id": guest})
    assert first.status_code == 201 and first.json()["seated"] is True
    again = client.post(f"/rooms/{rid}/invite", headers=ada,
                        json={"profile_id": guest})
    assert again.status_code == 409, again.text

    box = client.get(f"/profiles/{guest}/inbox", headers=guest_own).json()
    assert len([e for e in box["events"] if e["kind"] == "room_joined"]) == 1


def test_asking_somebody_already_in_the_room_is_refused(client):
    uid, ada = _person(client, "Ada")
    host, _own = _profile(client, "acct_h8")
    rid = _room(client, uid, ada, host)

    r = client.post(f"/rooms/{rid}/invite", headers=ada,
                    json={"profile_id": host})
    assert r.status_code == 409, r.text
    assert "already in this room" in r.json()["detail"]


def test_the_seat_holds_exactly_once(client):
    """However many roads lead to the seat — the agentic join, a stale
    accept from an older client — the room holds one seat per profile,
    and an accept after the join is answered honestly rather than
    doubling the frame."""
    uid, ada = _person(client, "Ada")
    host, _own = _profile(client, "acct_h9")
    rid = _room(client, uid, ada, host)
    guest, guest_own = _profile(client, "acct_g9", "Wren")
    client.post(f"/rooms/{rid}/invite", headers=ada,
                json={"profile_id": guest})

    # The join already answered the invitation, so a late accept finds
    # nothing left to accept.
    late = client.post(f"/rooms/{rid}/invites/accept", headers=guest_own,
                       json={"profile_id": guest})
    assert late.status_code == 403, late.text

    from qrme import db
    seats = db.connect().execute(
        "SELECT ref_id FROM room_participants WHERE room_id=? AND"
        " kind='profile' AND ref_id=?", (rid, guest)).fetchall()
    assert len(seats) == 1


# --- the room's own state ---------------------------------------------------

def test_a_closed_room_takes_no_invitations(client):
    uid, ada = _person(client, "Ada")
    host, _own = _profile(client, "acct_h10")
    rid = _room(client, uid, ada, host)
    guest, _g = _profile(client, "acct_g10", "Wren")
    from qrme import db
    db.connect().execute("UPDATE rooms SET status='closed' WHERE id=?", (rid,))
    db.connect().commit()

    r = client.post(f"/rooms/{rid}/invite", headers=ada,
                    json={"profile_id": guest})
    assert r.status_code == 409, r.text


def test_a_departed_profile_is_not_asked_anywhere(client):
    """The same check `create_room` makes about a named participant, at the
    other door that can seat one."""
    uid, ada = _person(client, "Ada")
    host, _own = _profile(client, "acct_h11")
    rid = _room(client, uid, ada, host)
    guest, _g = _profile(client, "acct_g11", "Wren")
    from qrme import db
    db.connect().execute("UPDATE profiles SET status='departed' WHERE id=?",
                         (guest,))
    db.connect().commit()

    r = client.post(f"/rooms/{rid}/invite", headers=ada,
                    json={"profile_id": guest})
    assert r.status_code == 410, r.text


# --- your own stable needs no invitation -------------------------------------
#
# The dance above is for somebody ELSE's profile, whose owner answers from
# their own inbox. When the host's account owns the guest, both consents are
# in the one press — and the dance was a person mailing themselves a question
# nothing would answer. Field report, from the invite panel: "I selected a
# profile to add them and no extra frame showed up." No seat, no error, an
# invitation rotting in an inbox the presser cannot see; the console only
# ever holds one profile's owner token at a time, so a client-side accept
# could never cover a stable.


def test_your_own_profile_is_seated_by_the_press(client):
    from .conftest import enrol

    uid, mine = _person(client, "David")
    account = enrol(uid)
    host, _own = _profile(client, account, "First")
    rid = _room(client, uid, mine, host)
    second, _tok = _profile(client, account, "Second")

    r = client.post(f"/rooms/{rid}/invite", headers=mine,
                    json={"profile_id": second})
    assert r.status_code == 201, r.text
    assert r.json()["seated"] is True
    from qrme import db

    seats = db.connect().execute(
        "SELECT ref_id FROM room_participants WHERE room_id=? AND"
        " kind='profile'", (rid,)).fetchall()
    assert any(row["ref_id"] == second for row in seats), (
        "the press said seated and the room does not hold the seat")


def test_somebody_elses_profile_answers_the_invitation_itself(client):
    """The deliberate reversal of the old consent dance, on the owner's
    word: "they should respond and jump in on their own." A profile from
    another account seats itself the moment it is asked; what its owner
    keeps is the RECORD — `room_joined` in the profile's inbox, naming
    who asked — and the standing remedies: leave the room, wind the
    profile down. The ten-turn governor bounds what any seat can spend."""
    from .conftest import enrol

    uid, mine = _person(client, "David")
    enrol(uid)
    host, _own = _profile(client, "acct_other_h", "Host")
    rid = _room(client, uid, mine, host)
    guest, guest_own = _profile(client, "acct_other_g", "Wren")

    r = client.post(f"/rooms/{rid}/invite", headers=mine,
                    json={"profile_id": guest})
    assert r.status_code == 201, r.text
    assert r.json()["seated"] is True
    from qrme import db

    seats = db.connect().execute(
        "SELECT ref_id FROM room_participants WHERE room_id=? AND"
        " kind='profile'", (rid,)).fetchall()
    assert any(row["ref_id"] == guest for row in seats)
    box = client.get(f"/profiles/{guest}/inbox", headers=guest_own).json()
    assert any(e["kind"] == "room_joined" and e["ref"] == rid
               for e in box["events"]), (
        "the owner was left without the record of where their profile "
        "has been seated")
