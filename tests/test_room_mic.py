"""Lending a room's profiles a wearable microphone.

In a voice room the participant's own microphone is carrying their voice to
the other people. The profiles are reading text and have no ear of their own.

The difference from `jim/mic.py` — which lends the same wearable to the
Guardian during a call — is that **a room has other people in it**. That is
the whole of the design here, and the disclosure test is the one that matters.
"""

from tests.test_capabilities import auth_header, make_profile


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

    before = client.get(f"/rooms/{room['id']}/mic",
                        headers=_as(mal["token"])).json()
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
    assert client.get(f"/rooms/{room['id']}/mic",
                      headers=_as(sam["token"])).json()["microphones_lent"] == []


def test_the_disclosure_stops_at_the_people_it_protects(client):
    """"Anyone in the room" was the design and "anyone at all" was the code.

    The route checked nothing, so it answered any caller holding a room id —
    and a room id is not a secret. It rides in beacons and on printed QR
    stickers, which is what they are for. That turned a privacy feature into
    its opposite: who is wearing a live microphone, on what, and since when,
    published to whoever scanned the sticker.

    Both halves are asserted, and the second is the one that matters — a test
    that only tried an anonymous caller would pass against a system that
    hands a room's disclosure to any signed-in stranger.
    """
    p = make_profile(client)
    sam = _interactor(client, "Sam")
    outsider = _interactor(client, "Nosy")
    room = _room(client, p, sam)
    client.post(f"/rooms/{room['id']}/mic", json={"interactor_id": sam["id"]},
                headers=_as(sam["token"]))

    assert client.get(f"/rooms/{room['id']}/mic",
                      headers={"authorization": ""}).status_code == 401
    assert client.get(f"/rooms/{room['id']}/mic",
                      headers=_as(outsider["token"])).status_code == 403
    assert client.get(f"/rooms/{room['id']}/mic",
                      headers=_as(sam["token"])).status_code == 200


def test_the_profiles_owner_can_read_the_disclosure_too(client):
    """The profiles are the side being lent the microphone, so their owner is
    exactly who the disclosure is addressed to — being in the room as a
    `profile` participant has to count as being in the room."""
    p = make_profile(client)
    sam = _interactor(client)
    room = _room(client, p, sam)
    client.post(f"/rooms/{room['id']}/mic", json={"interactor_id": sam["id"]},
                headers=_as(sam["token"]))

    seen = client.get(f"/rooms/{room['id']}/mic", headers=auth_header(p))
    assert seen.status_code == 200
    assert [m["interactor_id"]
            for m in seen.json()["microphones_lent"]] == [sam["id"]]


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
    assert "close to the microphone" in lent["hears"]
    assert "requested_gain" not in lent
    assert "narrow enough" in seen["note"] and "not the room" in seen["note"]


def test_every_level_is_the_lender_at_a_distance_never_more_people(client):
    """A dial whose wide end means "more voices" would be the whole objection
    to this feature, wearing a different name."""
    from qrme import roommic
    for spec in roommic.GAIN_LEVELS.values():
        assert spec["describes"].startswith("you"), spec


def test_the_lent_channel_keys_on_its_wearer(client):
    """Focus is not a setting. In a room the chatter a wider channel would
    pick up is the other participants, and their voices were never the
    lender's to give."""
    from qrme import roommic

    p = make_profile(client)
    sam = _interactor(client, "Sam")
    mal = _interactor(client, "Mal")
    room = _room(client, p, sam, mal)

    out = client.post(f"/rooms/{room['id']}/mic",
                      json={"interactor_id": sam["id"]},
                      headers=_as(sam["token"])).json()
    assert out["voice_focus"] is True
    assert "keys on your voice and drops the rest" in out["note"]

    seen = client.get(f"/rooms/{room['id']}/mic",
                      headers=_as(mal["token"])).json()
    assert seen["voice_focus"] is True
    assert "keys on its own wearer" in seen["note"]
    assert roommic.VOICE_FOCUS is True


def test_focus_does_not_stand_in_for_the_cap(client):
    """Both bounds, not just the filter — a filter can fail, and the people it
    would fail on did not choose to be in range."""
    p = make_profile(client)
    sam = _interactor(client, "Sam")
    mal = _interactor(client, "Mal")
    room = _room(client, p, sam, mal)

    out = client.post(f"/rooms/{room['id']}/mic",
                      json={"interactor_id": sam["id"], "gain": "wide"},
                      headers=_as(sam["token"])).json()
    assert out["voice_focus"] is True     # still keyed on the lender
    assert out["gain"] == "near_field"    # and still narrowed anyway
    assert out["capped"] is True


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
    assert roommic.VOICE_FOCUS is True


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


# -- the pairing registry and the lending vocabulary --------------------------

def test_a_device_can_be_lent_under_the_name_it_was_paired_with(client):
    """Two vocabularies for one collar clip, and for a while nothing joined
    them.

    `qrme/wearables.py` is where somebody registers the devices they own and
    it calls them `lapel_mic` and `clip_on_mic`; this module is kept in step
    with `jim/mic.py` by hand and calls them `lapel` and `clip_on`. So you
    could pair a lapel mic and then be told `lapel_mic` was an unknown
    microphone type when you tried to lend it — and the registry exists *for*
    this feature, which its own comment says.
    """
    p = make_profile(client)
    sam = _interactor(client)
    room = _room(client, p, sam)

    out = client.post(f"/rooms/{room['id']}/mic",
                      json={"interactor_id": sam["id"], "mic_type": "lapel_mic",
                            "device": "lapel_mic"},
                      headers=_as(sam["token"]))
    assert out.status_code == 201, out.text
    assert out.json()["mic_type"] == "lapel"      # stored under one name


def test_every_microphone_bearing_paired_kind_can_be_lent(client):
    """The join, asserted rather than hoped for. A kind somebody can pair and
    cannot lend is a dead end they find at the moment they try to use it.

    The mic-bearing kinds are written out here rather than derived from
    `FROM_WEARABLE`, which would make this test agree with whatever that table
    happens to say. Every kind in the registry has to appear on one side or
    the other, so adding one to `wearables.KINDS` fails here until somebody
    decides whether it carries a microphone — which is the moment to decide
    it, not the moment a user tries to lend it.
    """
    from qrme import roommic, wearables

    BEARING = {"watch", "earbuds", "headset", "lapel_mic", "clip_on_mic",
               "glasses",
               # The 2.9.7 widening's head-worn kinds all carry one.
               "vr_headset", "ar_glasses", "hearing_aids",
               "audio_earrings"}
    SILENT = {"band", "ring", "pendant",
              # An alert button carries a two-way voice channel, and it is
              # still SILENT here on purpose: that microphone belongs to the
              # emergency service's loop, not to the owner's gift. Lending it
              # to a room would put the room between a person and their help.
              "chest_strap", "health_patch", "headband", "ankle_monitor",
              "insoles", "alert_button", "smart_clothing"}

    unclassified = set(wearables.KINDS) - BEARING - SILENT
    assert not unclassified, (
        "pairable devices nobody has said carry a microphone or not: "
        f"{sorted(unclassified)}")

    for kind in BEARING:
        landed = roommic.FROM_WEARABLE.get(kind, kind)
        assert landed in roommic.MIC_TYPES, (
            f"{kind!r} can be paired but has nowhere to land")
        assert roommic.MIC_TYPES[landed] is True, (
            f"{kind!r} is pairable as a worn device but lends as room-facing")


def test_a_refused_pairing_kind_gets_its_reason_not_unknown(client):
    """"Unknown microphone type" reads as a gap somebody files a bug about, or
    works around. The reason those devices are absent is the whole argument of
    this module, so it is what comes back."""
    p = make_profile(client)
    sam = _interactor(client)
    room = _room(client, p, sam)

    r = client.post(f"/rooms/{room['id']}/mic",
                    json={"interactor_id": sam["id"],
                          "mic_type": "smart_speaker"},
                    headers=_as(sam["token"]))
    assert r.status_code == 403
    detail = r.json()["detail"]
    assert "unknown" not in detail.lower()
    assert "not yours to lend" in detail


def test_the_vocabulary_route_lists_what_can_and_cannot_be_lent(client):
    out = client.get("/microphones/vocabulary").json()
    assert "watch" in out["personal"]
    refused = {r["kind"] for r in out["refusals"]}
    assert "speakerphone" in refused and "room_array" in refused
    assert all(r["why"] for r in out["refusals"])
    assert out["room_gain"] == "near_field" and out["voice_focus"] is True
