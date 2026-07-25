"""Live desks: a real person, and the mark that must not be on them.

Most of this file is one invariant checked from both sides. A synthetic
profile always carries the AI watermark; a desk never does. Getting either
direction wrong makes the mark worthless — an unmarked synthetic face is the
failure everyone expects, and marking a real human is the one nobody checks
for, so both are tested here together.

The rest is the bell, which exists because the sign on the chair says to ring
it and a visitor looking at an empty chair on a screen cannot.
"""

from qrme import desks


def _desk(client, **over):
    body = {"owner_id": "o1", "display_name": "Ray Coleman",
            "trade": "locksmith", "attestor": "shop-manager",
            "basis": "met in person, saw the trade licence",
            "location": "the counter"}
    body.update(over)
    return client.post("/desks", json=body)


def _token(created):
    return {"authorization": f"Bearer {created['desk_token']}"}


# --- the invariant, both directions --------------------------------------

def test_a_desk_never_carries_the_ai_watermark(client):
    """Stamping AI on a real person is not a cautious default. It tells the
    visitor the human they are waiting for does not exist."""
    card = _desk(client).json()
    assert card["ai"] is False
    assert card["human"] is True
    assert "watermark" not in card
    assert card["feed"]["watermark"] is None
    assert card["feed"]["ai"] is False


def test_a_synthetic_profile_still_always_does(client):
    """The other half of the same rule, checked in the same file so neither
    can be relaxed without someone noticing the pair."""
    created = client.post("/profiles", json={
        "owner_id": "o1", "kind": "fictional", "display_name": "Dr. Amara Osei",
        "persona": "A physician.",
        "verification": {"birthdate": "1980-01-01", "id_document": "passport",
                         "liveness_check": True}}).json()
    art = client.get(f"/profiles/{created['id']}/avatar").json()
    assert art["watermark"]["always_displayed"] is True
    assert "AI" in art["watermark"]["label"]


def test_the_claim_is_positive_not_merely_the_absence_of_a_mark(client):
    """An unmarked card could equally be an AI whose badge was dropped, so a
    desk says what it is rather than leaving it to be inferred."""
    card = _desk(client).json()
    assert card["designation"] == desks.DESIGNATION
    assert "not AI" in card["designation"]


def test_a_desk_cannot_be_opened_without_saying_who_vouches(client):
    """A 'not AI' badge nobody stands behind is worse than no badge, because
    it would be believed."""
    res = _desk(client, attestor="   ")
    assert res.status_code == 422
    assert "attests" in res.text


def test_the_attestation_says_recorded_rather_than_proven(client):
    card = _desk(client).json()
    assert card["attestation"]["attestor"] == "shop-manager"
    assert card["attestation"]["signed"] is False
    assert "recorded, not proven" in card["attestation"]["note"]


def test_a_signed_attestation_is_reported_as_such(client):
    """The signature scheme is what raises the claim from a record to
    something a counterparty can check."""
    from tests.test_signatures import Authenticator, _enroll, _token as prof_token
    headers = prof_token(client)
    auth, _ = _enroll(client, headers)
    card = _desk(client).json()

    env = client.post("/signatures/request", json={
        "document": f"desk {card['desk_id']} is staffed by a real person",
        "meaning": "I attest a real person staffs this desk", "tier": "high",
        "display_text": "shown", "binding_kind": "desk_human_attestation",
        "binding_ref": card["desk_id"]}, headers=headers).json()
    assertion = auth.assert_(env["challenge"])
    client.post("/signatures/sign",
                json={"envelope_id": env["envelope_id"], **assertion},
                headers=headers)

    again = client.get(f"/desks/{card['desk_id']}").json()
    assert again["attestation"]["signed"] is True
    assert again["attestation"]["signature_id"].startswith("sig_")


# --- the view -------------------------------------------------------------

def test_the_view_is_served_and_is_not_claimed_to_be_live(client):
    """A still frame presented as a live feed would be the same class of lie
    as marking a human as AI."""
    card = _desk(client).json()
    assert card["feed"]["live"] is False
    assert "not live" in card["feed"]["note"]

    res = client.get(card["feed"]["url"])
    assert res.status_code == 200
    assert res.headers["content-type"] == "image/webp"
    assert res.headers["cache-control"] == "no-store"


def test_a_desk_has_no_portrait_of_the_person_by_default(client):
    """We do not have their photograph and do not go looking for one."""
    card = _desk(client).json()
    assert card["portrait"] is None


def test_the_owner_may_attach_their_own_portrait(client):
    created = _desk(client).json()
    res = client.put(f"/desks/{created['desk_id']}/portrait",
                     json={"asset": "https://example.test/ray.jpg"},
                     headers=_token(created))
    assert res.status_code == 200
    assert res.json()["portrait"] == "https://example.test/ray.jpg"
    # Still not AI, and still no watermark anywhere near it.
    assert res.json()["ai"] is False


def test_only_the_desk_may_change_its_own_presence(client):
    created = _desk(client).json()
    assert client.put(f"/desks/{created['desk_id']}/presence",
                      json={"presence": "attended"}).status_code == 401
    ok = client.put(f"/desks/{created['desk_id']}/presence",
                    json={"presence": "attended"}, headers=_token(created))
    assert ok.status_code == 200
    assert ok.json()["presence"] == "attended"


# --- the bell -------------------------------------------------------------

def test_a_visitor_can_ring_the_bell_without_an_account(client):
    """The person looking at an empty chair is exactly the person who has no
    account — requiring one would be requiring it at the worst moment."""
    created = _desk(client).json()
    res = client.post(f"/desks/{created['desk_id']}/bell",
                      json={"note": "need a key cut"})
    assert res.status_code == 201
    body = res.json()
    assert body["waiting"] == 1
    assert "get back" in body["note"]


def test_the_bell_is_rate_limited_so_it_is_not_a_doorbell_prank(client):
    created = _desk(client).json()
    assert client.post(f"/desks/{created['desk_id']}/bell",
                       json={}).status_code == 201
    again = client.post(f"/desks/{created['desk_id']}/bell", json={})
    assert again.status_code == 422
    assert "just rung" in again.text


def test_a_closed_desk_has_no_bell(client):
    created = _desk(client).json()
    client.put(f"/desks/{created['desk_id']}/presence",
               json={"presence": "closed"}, headers=_token(created))
    card = client.get(f"/desks/{created['desk_id']}").json()
    assert card["bell"]["available"] is False
    res = client.post(f"/desks/{created['desk_id']}/bell", json={})
    assert res.status_code == 422
    assert "nobody would hear it" in res.text


def test_ringing_an_attended_desk_still_works_and_says_so(client):
    """They are here but looking elsewhere. That is still a reason to ring."""
    created = _desk(client).json()
    client.put(f"/desks/{created['desk_id']}/presence",
               json={"presence": "attended"}, headers=_token(created))
    body = client.post(f"/desks/{created['desk_id']}/bell", json={}).json()
    assert "at the desk" in body["note"].lower()


def test_the_owner_sees_who_rang_and_can_clear_it(client):
    created = _desk(client).json()
    client.post(f"/desks/{created['desk_id']}/bell",
                json={"caller_id": "int_1", "note": "spare key"})
    rings = client.get(f"/desks/{created['desk_id']}/rings",
                       headers=_token(created)).json()["rings"]
    assert len(rings) == 1 and rings[0]["note"] == "spare key"

    client.post(f"/desks/{created['desk_id']}/rings/{rings[0]['id']}/ack",
                headers=_token(created))
    assert client.get(f"/desks/{created['desk_id']}").json()["bell"]["waiting"] == 0


def test_rings_are_not_public(client):
    """Who called on a tradesperson is theirs, not a visitor's to browse."""
    created = _desk(client).json()
    assert client.get(f"/desks/{created['desk_id']}/rings").status_code == 401


def test_an_unknown_desk_is_a_404_not_a_stack_trace(client):
    assert client.get("/desks/dsk_nope").status_code == 404
    assert client.post("/desks/dsk_nope/bell", json={}).status_code == 404


# --- 18+ streams ----------------------------------------------------------
#
# Not a separate tier. A rated desk is the same live stream behind the same
# verified-adult gate every other 18+ surface already uses — reusing it rather
# than writing a second one, because a second gate is a second thing to get
# wrong and the weaker one always wins.

ADULT = "1984-06-01"
MINOR = "2012-06-01"


def _viewer(client, birthdate):
    r = client.post("/interactors",
                    json={"display_name": "Viewer", "birthdate": birthdate})
    return {"authorization": f"Bearer {r.json()['token']}"}


def _stream(client, **over):
    body = {"owner_id": "perf-1", "display_name": "Sable", "trade": "performer",
            "attestor": "perf-1", "basis": "self-attested, verified adult",
            "rated": True, "view_style": "stage"}
    body.update(over)
    return client.post("/desks", json=body)


def test_an_18_plus_stream_can_only_be_opened_by_the_person_on_it(client):
    """The repo's hard line is that adult mode is never available for a
    profile of another real person. A stream *is* a real person, so the same
    line lands as: nobody else can put them on one."""
    res = _stream(client, attestor="somebody-else")
    assert res.status_code == 422
    assert "only be opened by the person on it" in res.text


def test_an_unverified_viewer_gets_an_age_wall_and_nothing_else(client):
    created = _stream(client).json()
    card = client.get(f"/desks/{created['desk_id']}").json()
    assert card["age_wall"] is True
    assert card["rated"] is True
    # Existence acknowledged; nothing that identifies or locates them.
    assert "display_name" not in card
    assert "location" not in card
    assert "feed" not in card
    # Still never marked as AI — a real person is on the other end.
    assert card["ai"] is False and card["human"] is True


def test_a_minor_is_refused_exactly_as_an_anonymous_caller_is(client):
    created = _stream(client).json()
    headers = _viewer(client, MINOR)
    assert client.get(f"/desks/{created['desk_id']}",
                      headers=headers).json()["age_wall"] is True
    assert client.get(f"/desks/{created['desk_id']}/view.webp",
                      headers=headers).status_code == 403


def test_a_verified_adult_sees_the_stream(client):
    created = _stream(client).json()
    headers = _viewer(client, ADULT)
    card = client.get(f"/desks/{created['desk_id']}", headers=headers).json()
    assert card["age_wall"] is False
    assert card["display_name"] == "Sable"
    assert card["ai"] is False
    assert card["feed"]["watermark"] is None

    view = client.get(f"/desks/{created['desk_id']}/view.webp", headers=headers)
    assert view.status_code == 200
    assert view.headers["content-type"] == "image/webp"


def test_where_they_physically_are_is_never_on_a_rated_card(client):
    """Withheld even from a verified adult. A performer's whereabouts has
    nothing to do with watching them."""
    created = _stream(client, location="123 Real Street").json()
    card = client.get(f"/desks/{created['desk_id']}",
                      headers=_viewer(client, ADULT)).json()
    assert card["location"] is None


def test_the_bell_on_a_rated_stream_is_not_an_anonymous_ping_channel(client):
    """Public on an ordinary desk, gated here: handing anyone a way to buzz an
    adult performer from anywhere is not a thing to hand out."""
    created = _stream(client).json()
    assert client.post(f"/desks/{created['desk_id']}/bell",
                       json={}).status_code == 403
    ok = client.post(f"/desks/{created['desk_id']}/bell", json={},
                     headers=_viewer(client, ADULT))
    assert ok.status_code == 201
    assert "get back" in ok.json()["note"]


def test_joining_the_stream_needs_the_same_verification(client):
    created = _stream(client).json()
    assert client.post(f"/desks/{created['desk_id']}/join").status_code == 403

    joined = client.post(f"/desks/{created['desk_id']}/join",
                         headers=_viewer(client, ADULT))
    assert joined.status_code == 201
    body = joined.json()
    assert body["room_id"].startswith("rm_")
    assert body["channel"] == "video"
    assert body["ai"] is False
    assert "away" in body["note"]


def test_the_room_is_minted_once_and_shared(client):
    """A stream is whoever is here, together — not a call per viewer."""
    created = _stream(client).json()
    a = client.post(f"/desks/{created['desk_id']}/join",
                    headers=_viewer(client, ADULT)).json()
    b = client.post(f"/desks/{created['desk_id']}/join",
                    headers=_viewer(client, ADULT)).json()
    assert a["room_id"] == b["room_id"]


def test_the_stage_view_is_served_for_a_stage_style_desk(client):
    created = _stream(client).json()
    headers = _viewer(client, ADULT)
    stage = client.get(f"/desks/{created['desk_id']}/view.webp",
                       headers=headers).content

    desk = _desk(client).json()
    office = client.get(f"/desks/{desk['desk_id']}/view.webp").content
    assert stage != office, "the two view styles serve the same frame"


def test_an_unknown_view_style_is_refused(client):
    res = _stream(client, view_style="hologram")
    assert res.status_code == 422
    assert "unknown view style" in res.text


def test_an_ordinary_desk_stays_public(client):
    """Gating the 18+ case must not quietly gate the locksmith."""
    created = _desk(client).json()
    assert client.get(f"/desks/{created['desk_id']}").json()["rated"] is False
    assert client.get(f"/desks/{created['desk_id']}/view.webp").status_code == 200
    assert client.post(f"/desks/{created['desk_id']}/bell",
                       json={}).status_code == 201


# --- gaps the pre-release audit turned up --------------------------------

def test_a_desk_can_be_pointed_at_its_own_camera(client):
    """`feed.live` was read from a column nothing could write, so the live
    branch was unreachable and every desk was a sample view forever."""
    created = _desk(client).json()
    assert created["feed"]["live"] is False

    res = client.put(f"/desks/{created['desk_id']}/camera",
                     json={"url": "https://cam.example/desk.mjpg"},
                     headers=_token(created))
    assert res.status_code == 200
    assert res.json()["feed"]["live"] is True
    assert "A live view" in res.json()["feed"]["note"]

    cleared = client.put(f"/desks/{created['desk_id']}/camera", json={},
                         headers=_token(created))
    assert cleared.json()["feed"]["live"] is False


def test_only_the_desk_can_turn_its_own_camera_on(client):
    """A camera on a person is not something a platform turns on for them."""
    created = _desk(client).json()
    assert client.put(f"/desks/{created['desk_id']}/camera",
                      json={"url": "https://cam.example/x"}).status_code == 401
