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
