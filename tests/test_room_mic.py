"""Lending a room's profiles a wearable microphone.

In a voice room the participant's own microphone is carrying their voice to
the other people. The profiles are reading text and have no ear of their own.

The difference from `jim/mic.py` — which lends the same wearable to the
Guardian during a call — is that **a room has other people in it**. That is
the whole of the design here, and the disclosure test is the one that matters.
"""

from tests.test_capabilities import make_profile


def _interactor(client, name="Sam"):
    r = client.post("/interactors", json={"display_name": name,
                                          "birthdate": "1990-01-01"})
    assert r.status_code == 201, r.text
    return r.json()


def _as(token):
    return {"authorization": f"Bearer {token}"}


def _room(client, profile, *users, channel="voice"):
    body = {"topic": "the quarterly numbers", "channel": channel,
            "participants": [{"kind": "profile", "id": profile["id"]}]
            + [{"kind": "user", "id": u["id"]} for u in users]}
    r = client.post("/rooms", json=body)
    assert r.status_code == 201, r.text
    return r.json()


# -- lending -----------------------------------------------------------------

def test_a_participant_can_lend_their_wearable(client):
    p = make_profile(client)
    sam = _interactor(client)
    room = _room(client, p, sam)

    out = client.post(f"/rooms/{room['id']}/mic",
                      json={"interactor_id": sam["id"]},
                      headers=_as(sam["token"]))
    assert out.status_code == 201
    body = out.json()
    assert body["lending"] is True
    assert "hear you on your smart watch" in body["note"]


def test_a_text_room_has_no_occupied_microphone(client):
    """Nothing is competing for the primary, so the profiles can already read
    everything sent. A second one would be a microphone for its own sake."""
    p = make_profile(client)
    sam = _interactor(client)
    room = _room(client, p, sam, channel="chat")

    r = client.post(f"/rooms/{room['id']}/mic",
                    json={"interactor_id": sam["id"]},
                    headers=_as(sam["token"]))
    assert r.status_code == 403
    assert "nobody's microphone is busy" in r.json()["detail"]


def test_a_non_participant_cannot_lend_one(client):
    p = make_profile(client)
    sam = _interactor(client)
    outsider = _interactor(client, "Outsider")
    room = _room(client, p, sam)

    r = client.post(f"/rooms/{room['id']}/mic",
                    json={"interactor_id": outsider["id"]},
                    headers=_as(outsider["token"]))
    assert r.status_code == 403
    assert "only a participant" in r.json()["detail"]


def test_one_interactor_cannot_lend_anothers_microphone(client):
    p = make_profile(client)
    sam = _interactor(client, "Sam")
    mal = _interactor(client, "Mal")
    room = _room(client, p, sam, mal)

    r = client.post(f"/rooms/{room['id']}/mic",
                    json={"interactor_id": sam["id"]},
                    headers=_as(mal["token"]))
    assert r.status_code == 403


def test_lending_twice_does_not_stack(client):
    p = make_profile(client)
    sam = _interactor(client)
    room = _room(client, p, sam)
    first = client.post(f"/rooms/{room['id']}/mic",
                        json={"interactor_id": sam["id"]},
                        headers=_as(sam["token"])).json()
    again = client.post(f"/rooms/{room['id']}/mic",
                        json={"interactor_id": sam["id"]},
                        headers=_as(sam["token"])).json()
    assert again["already_lent"] is True
    assert again["id"] == first["id"]


# -- everyone present is told ------------------------------------------------

def test_the_disclosure_is_readable_by_the_whole_room(client):
    """A disclosure only its subject can see is not a disclosure. The people
    who need this are the *other* participants."""
    p = make_profile(client)
    sam = _interactor(client, "Sam")
    mal = _interactor(client, "Mal")
    room = _room(client, p, sam, mal)

    before = client.get(f"/rooms/{room['id']}/mic").json()
    assert before["microphones_lent"] == []
    assert "no one has lent" in before["note"]

    client.post(f"/rooms/{room['id']}/mic", json={"interactor_id": sam["id"]},
                headers=_as(sam["token"]))

    # Mal — who lent nothing — can see that Sam did.
    after = client.get(f"/rooms/{room['id']}/mic",
                       headers=_as(mal["token"])).json()
    assert [m["interactor_id"] for m in after["microphones_lent"]] == [sam["id"]]
    assert "not the room" in after["note"]


def test_taking_it_back_removes_it_from_the_disclosure(client):
    p = make_profile(client)
    sam = _interactor(client)
    room = _room(client, p, sam)
    client.post(f"/rooms/{room['id']}/mic", json={"interactor_id": sam["id"]},
                headers=_as(sam["token"]))

    out = client.delete(f"/rooms/{room['id']}/mic/{sam['id']}",
                        headers=_as(sam["token"])).json()
    assert out["lending"] is False
    assert client.get(f"/rooms/{room['id']}/mic").json()["microphones_lent"] == []


# -- what the profiles are told ----------------------------------------------

def test_the_profiles_are_told_they_hear_only_the_lender(client):
    """The temptation is to behave as though the whole room is audible when
    exactly one person chose to be."""
    from qrme import roommic

    p = make_profile(client)
    sam = _interactor(client, "Sam")
    mal = _interactor(client, "Mal")
    room = _room(client, p, sam, mal)
    client.post(f"/rooms/{room['id']}/mic", json={"interactor_id": sam["id"]},
                headers=_as(sam["token"]))

    heard = roommic.heard_by_profiles(room["id"])
    assert heard == [sam["id"]]
    assert mal["id"] not in heard

    # And the room turn tells the profile exactly that.
    client.post(f"/rooms/{room['id']}/advance")
    # The prompt text is asserted through the module the router builds it
    # from; the wording is checked here so it cannot quietly soften.
    disclosure = roommic.disclosure(room["id"])
    assert "not the room" in disclosure["note"]


def test_no_lender_means_the_profiles_are_told_nothing(client):
    from qrme import roommic
    p = make_profile(client)
    sam = _interactor(client)
    room = _room(client, p, sam)
    assert roommic.heard_by_profiles(room["id"]) == []


# -- it ends with the room ---------------------------------------------------

def test_closing_the_room_ends_every_grant(client):
    """A permission must not outlive the conversation that justified it."""
    from qrme import roommic

    p = make_profile(client)
    sam = _interactor(client, "Sam")
    mal = _interactor(client, "Mal")
    room = _room(client, p, sam, mal)
    for who in (sam, mal):
        client.post(f"/rooms/{room['id']}/mic",
                    json={"interactor_id": who["id"]},
                    headers=_as(who["token"]))
    assert len(roommic.heard_by_profiles(room["id"])) == 2

    assert roommic.close_room(room["id"]) == 2
    assert roommic.heard_by_profiles(room["id"]) == []


def test_a_closed_room_will_not_take_a_new_grant(client):
    from qrme import db

    p = make_profile(client)
    sam = _interactor(client)
    room = _room(client, p, sam)
    conn = db.connect()
    conn.execute("UPDATE rooms SET status='closed' WHERE id=?", (room["id"],))
    conn.commit()

    r = client.post(f"/rooms/{room['id']}/mic",
                    json={"interactor_id": sam["id"]},
                    headers=_as(sam["token"]))
    assert r.status_code == 403
    assert "has closed" in r.json()["detail"]


def test_a_room_facing_microphone_cannot_be_lent_to_a_room(client):
    """The sharpest version of the rule: in a room, a room-facing microphone
    would pick up the other participants — and their voices are not the
    lender's to give."""
    p = make_profile(client)
    sam = _interactor(client, "Sam")
    mal = _interactor(client, "Mal")
    room = _room(client, p, sam, mal)

    r = client.post(f"/rooms/{room['id']}/mic",
                    json={"interactor_id": sam["id"], "device": "desk_puck",
                          "mic_type": "conference"},
                    headers=_as(sam["token"]))
    assert r.status_code == 403
    assert "not yours to lend" in r.json()["detail"]
    assert client.get(f"/rooms/{room['id']}/mic").json()["microphones_lent"] == []


def test_a_room_grant_runs_narrow_whatever_the_lender_set(client):
    """The gain is what makes "the profiles hear them, not the room" true of
    the capture rather than true of a sentence in a note. JIM caps channel 2
    while a call is in progress; a room is that condition for its whole life.
    """
    p = make_profile(client)
    sam = _interactor(client, "Sam")
    mal = _interactor(client, "Mal")
    room = _room(client, p, sam, mal)

    out = client.post(f"/rooms/{room['id']}/mic",
                      json={"interactor_id": sam["id"], "gain": "wide"},
                      headers=_as(sam["token"])).json()
    assert out["gain"] == "near_field"
    assert out["capped"] is True
    assert out["requested_gain"] == "wide"
    assert "other people in this room" in out["because"]
    assert "still yours everywhere else" in out["because"]


def test_a_near_field_lender_is_not_told_they_were_capped(client):
    """Nothing was overridden, so saying so would be noise."""
    p = make_profile(client)
    sam = _interactor(client)
    room = _room(client, p, sam)
    out = client.post(f"/rooms/{room['id']}/mic",
                      json={"interactor_id": sam["id"]},
                      headers=_as(sam["token"])).json()
    assert out["gain"] == "near_field" and out["capped"] is False
    assert "because" not in out


def test_the_room_is_told_what_the_microphone_actually_hears(client):
    """What protects the other participants is how wide the channel is, so the
    disclosure carries it — the *effective* gain, never the request. A rejected
    preference is the lender's business and is not true of the capture."""
    p = make_profile(client)
    sam = _interactor(client, "Sam")
    mal = _interactor(client, "Mal")
    room = _room(client, p, sam, mal)
    client.post(f"/rooms/{room['id']}/mic",
                json={"interactor_id": sam["id"], "gain": "wide"},
                headers=_as(sam["token"]))

    seen = client.get(f"/rooms/{room['id']}/mic",
                      headers=_as(mal["token"])).json()
    lent = seen["microphones_lent"][0]
    assert lent["gain"] == "near_field"
    assert "your own voice" in lent["hears"]
    assert "requested_gain" not in lent
    assert "narrow enough" in seen["note"] and "not the room" in seen["note"]


def test_an_unknown_gain_is_rejected(client):
    p = make_profile(client)
    sam = _interactor(client)
    room = _room(client, p, sam)
    r = client.post(f"/rooms/{room['id']}/mic",
                    json={"interactor_id": sam["id"], "gain": "maximum"},
                    headers=_as(sam["token"]))
    assert r.status_code == 422        # rejected by the schema


def test_the_gain_levels_match_jim(client):
    """The two products do not import each other, the same way docs/tandem.md
    is byte-identical in three repos rather than shared. If they drift, one of
    them is telling a user something the other does not do."""
    from qrme import roommic
    assert set(roommic.GAIN_LEVELS) == {"near_field", "normal", "wide"}
    assert roommic.GAIN_LEVELS["near_field"]["reaches_others"] is False
    assert all(roommic.GAIN_LEVELS[g]["reaches_others"]
               for g in ("normal", "wide"))
    assert roommic.ROOM_GAIN == "near_field"


def test_any_worn_microphone_can_be_lent(client):
    p = make_profile(client)
    sam = _interactor(client, "Sam")
    room = _room(client, p, sam)
    r = client.post(f"/rooms/{room['id']}/mic",
                    json={"interactor_id": sam["id"], "device": "lapel_mic",
                          "mic_type": "lapel"},
                    headers=_as(sam["token"]))
    assert r.status_code == 201
    assert r.json()["mic_type"] == "lapel"
