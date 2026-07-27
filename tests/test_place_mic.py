"""Channel 2 on the surfaces that are not a room.

The room version answers one question — *can the other people present be told?*
— and everything else follows from it. These tests are about whether that
answer still holds when the place is a watch party, a live desk or a one-to-one
connection, and about the two things that went wrong the first time: a
disclosure readable by anybody holding the id, and a grant that outlived the
place that justified it.
"""

from qrme import db, roommic
from tests.test_capabilities import auth_header, make_profile


def _interactor(client, name="Sam"):
    r = client.post("/interactors", json={"display_name": name,
                                          "birthdate": "1990-01-01"})
    assert r.status_code == 201, r.text
    return r.json()


def _as(token):
    return {"authorization": f"Bearer {token}"}


def _party(client, *members):
    """A watch party with these interactors in it, written directly.

    The party's own routes need a video post and a host profile; none of that
    is what these tests are about, and going through them would make a
    microphone test fail when an embed rule changes.
    """
    conn = db.connect()
    pid = db.new_id("pty")
    conn.execute(
        "INSERT INTO watch_parties (id, post_id, host_id, position_s,"
        " playing, created_at) VALUES (?,?,?,0,0,?)",
        (pid, "pst_x", members[0]["id"], db.utcnow()))
    for m in members:
        conn.execute(
            "INSERT INTO watch_party_members (id, party_id, member_id, kind,"
            " role, joined_at) VALUES (?,?,?,'person','guest',?)",
            (db.new_id("wpm"), pid, m["id"], db.utcnow()))
    conn.commit()
    return pid


# -- the same rules, in a different place -------------------------------------

def test_a_member_can_lend_their_wearable_in_a_watch_party(client):
    sam = _interactor(client)
    mal = _interactor(client, "Mal")
    pty = _party(client, sam, mal)

    r = client.post(f"/places/party/{pty}/microphone",
                    json={"interactor_id": sam["id"]}, headers=_as(sam["token"]))
    assert r.status_code == 201, r.text
    assert r.json()["lending"] is True


def test_a_room_facing_microphone_is_refused_here_too(client):
    """The reason never depended on the surface being a room: it would pick up
    the people around the lender, and their voices are not theirs to give."""
    sam = _interactor(client)
    pty = _party(client, sam)
    r = client.post(f"/places/party/{pty}/microphone",
                    json={"interactor_id": sam["id"],
                          "mic_type": "conference"}, headers=_as(sam["token"]))
    assert r.status_code == 422
    assert "not yours to lend" in r.json()["detail"]


def test_it_runs_near_field_whatever_the_lender_set(client):
    """Every surface in PLACES has other people in it by definition, so there
    is no state in which a wider channel would be honest."""
    sam = _interactor(client)
    pty = _party(client, sam)
    out = client.post(f"/places/party/{pty}/microphone",
                      json={"interactor_id": sam["id"], "gain": "wide"},
                      headers=_as(sam["token"])).json()
    assert out["gain"] == "near_field"
    assert out["capped"] is True and out["requested_gain"] == "wide"


def test_a_paired_device_name_works_here_as_well(client):
    sam = _interactor(client)
    pty = _party(client, sam)
    out = client.post(f"/places/party/{pty}/microphone",
                      json={"interactor_id": sam["id"],
                            "mic_type": "lapel_mic"},
                      headers=_as(sam["token"])).json()
    assert out["mic_type"] == "lapel"


# -- who may read it ----------------------------------------------------------

def test_the_disclosure_is_readable_by_everyone_present(client):
    sam = _interactor(client, "Sam")
    mal = _interactor(client, "Mal")
    pty = _party(client, sam, mal)
    client.post(f"/places/party/{pty}/microphone",
                json={"interactor_id": sam["id"]}, headers=_as(sam["token"]))

    seen = client.get(f"/places/party/{pty}/microphone",
                      headers=_as(mal["token"])).json()
    assert [m["interactor_id"] for m in seen["microphones_lent"]] == [sam["id"]]


def test_the_disclosure_stops_at_the_people_it_protects(client):
    """The room version shipped answering anybody who held the id, and an id
    is not a secret on these surfaces either — a party id travels in an
    invite, a desk id is printed on a sticker. Both cases, and the signed-in
    stranger is the one a token-less test would miss."""
    sam = _interactor(client, "Sam")
    outsider = _interactor(client, "Nosy")
    pty = _party(client, sam)
    client.post(f"/places/party/{pty}/microphone",
                json={"interactor_id": sam["id"]}, headers=_as(sam["token"]))

    assert client.get(f"/places/party/{pty}/microphone",
                      headers={"authorization": ""}).status_code == 401
    assert client.get(f"/places/party/{pty}/microphone",
                      headers=_as(outsider["token"])).status_code == 403


def test_somebody_who_left_is_not_still_present(client):
    """Otherwise a former member goes on reading who is wearing a live
    microphone in a place they walked out of."""
    sam = _interactor(client, "Sam")
    gone = _interactor(client, "Gone")
    pty = _party(client, sam, gone)
    db.connect().execute(
        "UPDATE watch_party_members SET left_at=? WHERE party_id=?"
        " AND member_id=?", (db.utcnow(), pty, gone["id"]))
    db.connect().commit()

    assert client.get(f"/places/party/{pty}/microphone",
                      headers=_as(gone["token"])).status_code == 403


def test_you_cannot_lend_somebody_elses_microphone(client):
    """Lending is a first-person act: a grant somebody else can create in your
    name is not consent, it is the opposite."""
    sam = _interactor(client, "Sam")
    mal = _interactor(client, "Mal")
    pty = _party(client, sam, mal)
    r = client.post(f"/places/party/{pty}/microphone",
                    json={"interactor_id": sam["id"]}, headers=_as(mal["token"]))
    assert r.status_code == 403


def test_an_unknown_place_is_a_404_not_a_403(client):
    """A caller who is not a member must not be able to tell a real id from an
    invented one by the status code."""
    sam = _interactor(client)
    assert client.get("/places/party/pty_nothing/microphone",
                      headers=_as(sam["token"])).status_code == 404


# -- ending -------------------------------------------------------------------

def test_taking_it_back_removes_it(client):
    sam = _interactor(client)
    pty = _party(client, sam)
    client.post(f"/places/party/{pty}/microphone",
                json={"interactor_id": sam["id"]}, headers=_as(sam["token"]))
    out = client.request("DELETE", f"/places/party/{pty}/microphone",
                         json={"interactor_id": sam["id"]},
                         headers=_as(sam["token"])).json()
    assert out["lending"] is False
    assert client.get(f"/places/party/{pty}/microphone",
                      headers=_as(sam["token"])).json()["microphones_lent"] == []


def test_closing_the_place_ends_every_grant(client):
    """A permission must not outlive the thing that justified it and quietly
    apply to the next one."""
    sam = _interactor(client, "Sam")
    mal = _interactor(client, "Mal")
    pty = _party(client, sam, mal)
    for who in (sam, mal):
        client.post(f"/places/party/{pty}/microphone",
                    json={"interactor_id": who["id"]}, headers=_as(who["token"]))

    assert roommic.close_place("party", pty) == 2
    assert roommic.heard_by_profiles_on("party", pty) == []


def test_lending_twice_does_not_stack(client):
    sam = _interactor(client)
    pty = _party(client, sam)
    first = client.post(f"/places/party/{pty}/microphone",
                        json={"interactor_id": sam["id"]},
                        headers=_as(sam["token"])).json()
    again = client.post(f"/places/party/{pty}/microphone",
                        json={"interactor_id": sam["id"]},
                        headers=_as(sam["token"])).json()
    assert again["already_lent"] is True and again["id"] == first["id"]


# -- the boundary with rooms --------------------------------------------------

def test_a_room_is_refused_here_and_pointed_at_its_own_routes(client):
    """Two storage paths for one surface is how a disclosure ends up reading
    one table while the grant sits in the other — and a microphone that is
    live but undisclosed is the worst failure this feature has."""
    import pytest
    with pytest.raises(roommic.RoomMicError) as exc:
        roommic.lend_on("room", "rm_1", "usr_1", "smart_watch")
    assert "/rooms/{id}/mic" in str(exc.value)

    sam = _interactor(client)
    r = client.get("/places/room/rm_1/microphone", headers=_as(sam["token"]))
    assert r.status_code == 422
    assert "/rooms/{id}/mic" in r.json()["detail"]


def test_every_place_has_a_member_list_and_can_show_a_disclosure(client):
    """The test a surface has to pass to be in PLACES at all, asserted rather
    than left in a comment. `_members` is the member list; a surface that
    returns nothing for a real id cannot tell anybody anything, so it must not
    be on the list."""
    from qrme.routers.placemic import _members

    sam = _interactor(client, "Sam")
    mal = _interactor(client, "Mal")
    made = {
        "party": _party(client, sam, mal),
        "connection": _connection(client, sam, mal),
        "desk": _desk(client, sam),
    }
    assert set(made) == set(roommic.PLACES), (
        "a surface in PLACES with no way to enumerate who is present")
    for surface, sid in made.items():
        assert _members(surface, sid), f"{surface} lists nobody"


def _connection(client, a, b):
    conn = db.connect()
    cid = db.new_id("con")
    conn.execute(
        "INSERT INTO connections (id, interactor_a, interactor_b, tier,"
        " status, created_at) VALUES (?,?,?,'direct','active',?)",
        (cid, a["id"], b["id"], db.utcnow()))
    conn.commit()
    return cid


def _desk(client, owner):
    conn = db.connect()
    did = db.new_id("desk")
    now = db.utcnow()
    conn.execute(
        "INSERT INTO desks (id, owner_id, display_name, trade, attestor,"
        " attestation_basis, attested_at, created_at, last_seen)"
        " VALUES (?,?,?,?,?,?,?,?,?)",
        (did, owner["id"], "Sam's desk", "plumber", "Sam",
         "self-attested", now, now, now))
    conn.commit()
    return did


def test_an_ended_connection_is_not_a_place(client):
    """The same reason a closed room takes no new grant."""
    sam = _interactor(client, "Sam")
    mal = _interactor(client, "Mal")
    cid = _connection(client, sam, mal)
    db.connect().execute("UPDATE connections SET status='ended' WHERE id=?",
                         (cid,))
    db.connect().commit()
    assert client.get(f"/places/connection/{cid}/microphone",
                      headers=_as(sam["token"])).status_code == 404


# -- the place ending actually ends the grant ---------------------------------

def test_ending_a_watch_party_returns_the_microphones(client):
    """`close_place` existing is not the same as anything calling it. This is
    the difference between a rule and a rule that runs."""
    from qrme import watchparty
    sam = _interactor(client, "Sam")
    pty = _party(client, sam)
    client.post(f"/places/party/{pty}/microphone",
                json={"interactor_id": sam["id"]}, headers=_as(sam["token"]))

    out = watchparty.end(pty, sam["id"])
    assert out["microphones_returned"] == 1
    assert roommic.heard_by_profiles_on("party", pty) == []


def test_closing_a_desk_returns_them_too(client):
    """A grant that survived closing would be live again next time the desk
    opened, for a conversation nobody has had yet."""
    from qrme import desks
    sam = _interactor(client, "Sam")
    did = _desk(client, sam)
    client.post(f"/places/desk/{did}/microphone",
                json={"interactor_id": sam["id"]}, headers=_as(sam["token"]))
    assert roommic.heard_by_profiles_on("desk", did) == [sam["id"]]

    desks.set_presence(did, "closed")
    assert roommic.heard_by_profiles_on("desk", did) == []


def test_ending_a_connection_returns_them(client):
    sam = _interactor(client, "Sam")
    mal = _interactor(client, "Mal")
    cid = _connection(client, sam, mal)
    client.post(f"/places/connection/{cid}/microphone",
                json={"interactor_id": sam["id"]}, headers=_as(sam["token"]))

    out = client.post(f"/connections/{cid}/end",
                      json={"interactor_id": sam["id"], "message": "bye"},
                      headers=_as(sam["token"]))
    assert out.status_code == 200, out.text
    assert roommic.heard_by_profiles_on("connection", cid) == []
