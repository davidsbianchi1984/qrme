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
    uid, ada = _person(client, "Ada")
    host, _own = _profile(client, "acct_host")
    rid = _room(client, uid, ada, host)
    guest, guest_own = _profile(client, "acct_guest", "Wren")

    asked = client.post(f"/rooms/{rid}/invite", headers=ada,
                        json={"profile_id": guest})
    assert asked.status_code == 201, asked.text
    assert asked.json()["invited"] is True
    assert asked.json()["already_invited"] is False

    # It arrives as news, in the guest's own inbox, naming who asked.
    box = client.get(f"/profiles/{guest}/inbox", headers=guest_own)
    assert box.status_code == 200, box.text
    invites = [e for e in box.json()["events"] if e["kind"] == "room_invite"]
    assert len(invites) == 1, box.json()
    assert invites[0]["ref"] == rid
    # The actor is a *person*, not a profile — the inbox join has to reach
    # the interactors table or this reads as a bare id.
    assert invites[0]["actor_name"] == "Ada", invites[0]

    seated = client.post(f"/rooms/{rid}/invites/accept", headers=guest_own,
                         json={"profile_id": guest})
    assert seated.status_code == 201, seated.text
    assert any(p["kind"] == "profile" and p["id"] == guest
               for p in seated.json()["participants"]), seated.json()


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
    """A button that can be pressed repeatedly into somebody's inbox is a
    button for filling somebody's inbox."""
    uid, ada = _person(client, "Ada")
    host, _own = _profile(client, "acct_h7")
    rid = _room(client, uid, ada, host)
    guest, guest_own = _profile(client, "acct_g7", "Wren")

    first = client.post(f"/rooms/{rid}/invite", headers=ada,
                        json={"profile_id": guest})
    again = client.post(f"/rooms/{rid}/invite", headers=ada,
                        json={"profile_id": guest})
    assert first.json()["already_invited"] is False
    assert again.json()["already_invited"] is True

    box = client.get(f"/profiles/{guest}/inbox", headers=guest_own).json()
    assert len([e for e in box["events"] if e["kind"] == "room_invite"]) == 1


def test_asking_somebody_already_in_the_room_is_refused(client):
    uid, ada = _person(client, "Ada")
    host, _own = _profile(client, "acct_h8")
    rid = _room(client, uid, ada, host)

    r = client.post(f"/rooms/{rid}/invite", headers=ada,
                    json={"profile_id": host})
    assert r.status_code == 409, r.text
    assert "already in this room" in r.json()["detail"]


def test_accepting_twice_is_being_there_once(client):
    uid, ada = _person(client, "Ada")
    host, _own = _profile(client, "acct_h9")
    rid = _room(client, uid, ada, host)
    guest, guest_own = _profile(client, "acct_g9", "Wren")
    client.post(f"/rooms/{rid}/invite", headers=ada,
                json={"profile_id": guest})

    client.post(f"/rooms/{rid}/invites/accept", headers=guest_own,
                json={"profile_id": guest})
    again = client.post(f"/rooms/{rid}/invites/accept", headers=guest_own,
                        json={"profile_id": guest})
    assert again.status_code == 201, again.text
    seated = [p for p in again.json()["participants"]
              if p["kind"] == "profile" and p["id"] == guest]
    assert len(seated) == 1, again.json()


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
