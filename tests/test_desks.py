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


# --- beacons: the desk as a printed code ---------------------------------
#
# A profile beacon and a desk beacon are the same gesture aimed at opposite
# things, so these tests mostly check that the differences survived: no AI
# mark, a positive human claim, a reachable bell, and an age wall that a
# tokenless scan can never get past.

def _beacon(client, created, **over):
    body = {"label": "shop door", "location": "Mill Yard"}
    body.update(over)
    return client.post(f"/desks/{created['desk_id']}/beacons",
                       json=body, headers=_token(created))


def test_a_desk_can_be_left_behind_as_a_printed_code(client):
    created = _desk(client).json()
    placed = _beacon(client, created)
    assert placed.status_code == 201
    body = placed.json()
    assert body["desk_id"] == created["desk_id"]
    assert body["active"] is True and body["scans"] == 0
    # Absolute, and it was not always. `scan_url` describes what the printed
    # code encodes — and the code encodes an absolute URL, because a sticker
    # on a shop door has no origin to be relative to. A bare path here made
    # the two disagree, and a console rendering it as a link resolved it
    # against its own origin, which is not the API's in any packaged build.
    assert body["scan_url"].startswith("http")
    assert body["scan_url"].endswith(f"/d/{body['id']}")
    # Still a path: fetched against the API this client is already talking
    # to, rather than printed on anything.
    assert client.get(body["qr_svg"]).headers["content-type"] == "image/svg+xml"


def test_only_the_desks_owner_can_print_it(client):
    """Anyone who could place a beacon for a desk they do not hold could put a
    stranger's name and whereabouts on a code and stick it anywhere."""
    created = _desk(client).json()
    assert client.post(f"/desks/{created['desk_id']}/beacons",
                       json={"label": "door"}).status_code == 401
    other = _desk(client, owner_id="o2").json()
    assert client.post(f"/desks/{created['desk_id']}/beacons",
                       json={"label": "door"},
                       headers=_token(other)).status_code == 403


def test_scanning_the_code_shows_a_person_not_an_ai(client):
    """The whole point. The profile landing page marks the portrait AI; this
    one must make the opposite claim, and must not look like the same badge."""
    created = _desk(client).json()
    placed = _beacon(client, created).json()

    page = client.get(f"/d/{placed['id']}")
    assert page.status_code == 200
    assert 'class="mark"' not in page.text      # the AI badge, never here
    assert 'class="human"' in page.text
    assert desks.DESIGNATION in page.text
    # Who vouched is on the page, not in a policy document elsewhere.
    assert "met in person, saw the trade licence" in page.text


def test_the_scanned_card_says_person_in_json_too(client):
    """Native clients draw their overlay from this, not from the HTML."""
    created = _desk(client).json()
    placed = _beacon(client, created).json()

    card = client.get(f"/d/{placed['id']}/card").json()
    assert card["ai"] is False and card["human"] is True
    assert card["designation"] == desks.DESIGNATION
    assert card["beacon"]["label"] == "shop door"
    assert card["feed"]["watermark"] is None


def test_a_stranger_can_reach_the_bell_from_the_sticker(client):
    """The sticker is on the door precisely because nobody is behind it."""
    created = _desk(client).json()
    placed = _beacon(client, created).json()
    page = client.get(f"/d/{placed['id']}").text
    assert 'id="bell"' in page
    # The page must post to this desk's bell, relatively — an absolute public
    # base would ring a bell on another host when scanned over a LAN.
    assert f'"/desks/{created["desk_id"]}/bell"' in page

    rung = client.post(f"/desks/{created['desk_id']}/bell", json={})
    assert rung.status_code == 201
    assert rung.json()["waiting"] == 1


def test_a_closed_desk_offers_no_bell_on_the_page(client):
    created = _desk(client).json()
    client.put(f"/desks/{created['desk_id']}/presence",
               json={"presence": "closed"}, headers=_token(created))
    placed = _beacon(client, created).json()
    page = client.get(f"/d/{placed['id']}").text
    assert 'id="bell"' not in page
    assert "bell is off" in page


def test_scans_are_counted(client):
    created = _desk(client).json()
    placed = _beacon(client, created).json()
    client.get(f"/d/{placed['id']}")
    client.get(f"/d/{placed['id']}/card")

    listed = client.get(f"/desks/{created['desk_id']}/beacons",
                        headers=_token(created)).json()["beacons"]
    assert listed[0]["scans"] == 2


def test_a_picked_up_code_stops_resolving(client):
    """A stale sticker on a wall outlives the desk it advertised."""
    created = _desk(client).json()
    placed = _beacon(client, created).json()
    assert client.delete(f"/desk-beacons/{placed['id']}",
                         headers=_token(created)).status_code == 200

    page = client.get(f"/d/{placed['id']}")
    assert page.status_code == 404
    assert "Nothing here" in page.text
    assert client.get(f"/d/{placed['id']}/card").status_code == 404


def test_a_rated_desks_code_always_hits_the_age_wall(client):
    """Every sticker scan is tokenless, so there is nothing that could clear
    this gate — which is the correct outcome, not a limitation."""
    created = _desk(client, owner_id="perf", attestor="perf",
                    display_name="Vivienne Marlowe", rated=True,
                    location="Studio 9, Kings Road").json()
    placed = _beacon(client, created, label="stage door").json()

    page = client.get(f"/d/{placed['id']}")
    assert "18+ only" in page.text
    assert "Vivienne" not in page.text
    # Whereabouts on an adult listing is a safety matter, and a sticker is by
    # definition somewhere physical.
    assert "Kings Road" not in page.text

    card = client.get(f"/d/{placed['id']}/card").json()
    assert card["age_wall"] is True
    assert "location" not in card and "display_name" not in card


def test_the_bell_script_is_valid_javascript(client):
    """The %-formatting that injects the endpoint is one stray literal % away
    from producing a page whose only interactive element silently dies."""
    import re
    import shutil
    import subprocess

    created = _desk(client).json()
    placed = _beacon(client, created).json()
    script = re.search(r"<script>(.*?)</script>",
                       client.get(f"/d/{placed['id']}").text, re.S).group(1)
    node = shutil.which("node")
    if node is None:                       # pragma: no cover - CI has node
        import pytest
        pytest.skip("node not available to syntax-check the bell script")
    proc = subprocess.run([node, "--check", "-"], input=script,
                          capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr


def test_a_beacon_needs_a_label_and_a_real_desk(client):
    created = _desk(client).json()
    assert _beacon(client, created, label="  ").status_code == 422
    assert client.post("/desks/dsk_nope/beacons", json={"label": "x"},
                       headers=_token(created)).status_code in (403, 404)


# --- coming up on stream -------------------------------------------------
#
# Joining has two shapes and they are not the same act. Watching and
# commenting is something a viewer does; appearing *on* the stream is
# something the host lets them do. Most of these tests are about keeping that
# distinction from quietly collapsing into "join".

def _watcher(client, name="Bea", birthdate="1990-01-01"):
    made = client.post("/interactors", json={
        "display_name": name, "birthdate": birthdate, "verified": True}).json()
    return {"authorization": f"Bearer {made['token']}"}


def test_joining_as_audience_is_immediate(client):
    created = _desk(client).json()
    out = client.post(f"/desks/{created['desk_id']}/join",
                      json={"mode": "audience"}, headers=_watcher(client)).json()
    assert out["mode"] == "audience"
    assert out["on_stream"] is False
    assert out["room_id"]


def test_joining_as_a_guest_only_asks(client):
    """Returning a room that behaved as if the request had been granted would
    be the worst possible default."""
    created = _desk(client).json()
    out = client.post(f"/desks/{created['desk_id']}/join",
                      json={"mode": "guest"}, headers=_watcher(client)).json()
    assert out["mode"] == "guest"
    assert out["on_stream"] is False
    assert out["guest_request"]["status"] == "requested"


def test_coming_up_needs_an_account(client):
    """The host is deciding about a person, not an anonymous request."""
    created = _desk(client).json()
    assert client.post(f"/desks/{created['desk_id']}/join",
                       json={"mode": "guest"}).status_code == 401
    assert client.post(f"/desks/{created['desk_id']}/guests",
                       json={}).status_code == 401


def test_one_hand_up_at_a_time(client):
    created = _desk(client).json()
    who = _watcher(client)
    assert client.post(f"/desks/{created['desk_id']}/guests", json={},
                       headers=who).status_code == 201
    again = client.post(f"/desks/{created['desk_id']}/guests", json={},
                        headers=who)
    assert again.status_code == 422
    assert "already have a hand up" in again.json()["detail"]


def test_only_the_host_sees_the_queue_or_answers_it(client):
    """Who asked to appear on someone's stream is theirs to see."""
    created = _desk(client).json()
    did = created["desk_id"]
    who = _watcher(client)
    req = client.post(f"/desks/{did}/guests", json={}, headers=who).json()

    assert client.get(f"/desks/{did}/guests", headers=who).status_code == 403
    assert client.get(f"/desks/{did}/guests").status_code == 401
    assert client.post(f"/desks/{did}/guests/{req['id']}/accept",
                       headers=who).status_code == 403

    listed = client.get(f"/desks/{did}/guests", headers=_token(created)).json()
    assert len(listed["guests"]) == 1


def test_the_host_can_bring_someone_up(client):
    created = _desk(client).json()
    did = created["desk_id"]
    who = _watcher(client)
    req = client.post(f"/desks/{did}/guests", json={}, headers=who).json()

    accepted = client.post(f"/desks/{did}/guests/{req['id']}/accept",
                           headers=_token(created)).json()
    assert accepted["status"] == "accepted"
    assert accepted["on_stream"] is True
    assert len(client.get(f"/desks/{did}/guests",
                          headers=_token(created)).json()["on_stream"]) == 1


def test_a_decision_is_made_once(client):
    created = _desk(client).json()
    did = created["desk_id"]
    req = client.post(f"/desks/{did}/guests", json={},
                      headers=_watcher(client)).json()
    client.post(f"/desks/{did}/guests/{req['id']}/accept",
                headers=_token(created))
    again = client.post(f"/desks/{did}/guests/{req['id']}/decline",
                        headers=_token(created))
    assert again.status_code == 422
    assert "already accepted" in again.json()["detail"]


def test_a_guest_can_always_step_back_down(client):
    """Needing the host's permission to *stop* being on camera would be the
    wrong way round."""
    created = _desk(client).json()
    did = created["desk_id"]
    who = _watcher(client)
    req = client.post(f"/desks/{did}/guests", json={}, headers=who).json()
    client.post(f"/desks/{did}/guests/{req['id']}/accept",
                headers=_token(created))

    left = client.request("DELETE", f"/desks/{did}/guests/me", headers=who)
    assert left.status_code == 200 and left.json()["status"] == "left"
    assert client.get(f"/desks/{did}/guests",
                      headers=_token(created)).json()["on_stream"] == []


def test_a_rated_desk_gates_guests_too(client):
    """A guest on a rated stream is a person going live on an 18+ broadcast,
    not merely watching one."""
    created = _desk(client, owner_id="perf", attestor="perf",
                    display_name="Vivienne Marlowe", rated=True,
                    view_style="stage").json()
    did = created["desk_id"]
    minor = _watcher(client, "Kid", "2015-01-01")
    assert client.post(f"/desks/{did}/guests", json={},
                       headers=minor).status_code == 403
    assert client.post(f"/desks/{did}/guests", json={},
                       headers=_watcher(client)).status_code == 201


def test_a_closed_desk_takes_no_hands(client):
    created = _desk(client).json()
    client.put(f"/desks/{created['desk_id']}/presence",
               json={"presence": "closed"}, headers=_token(created))
    assert client.post(f"/desks/{created['desk_id']}/guests", json={},
                       headers=_watcher(client)).status_code == 422


def test_an_unknown_join_mode_is_refused(client):
    created = _desk(client).json()
    out = client.post(f"/desks/{created['desk_id']}/join",
                      json={"mode": "backstage"}, headers=_watcher(client))
    assert out.status_code == 422


# --- the overlay ---------------------------------------------------------

def test_the_overlay_carries_what_renders_over_the_video(client):
    """One definition, so every client draws the same layer instead of each
    inventing its own."""
    created = _desk(client).json()
    did = created["desk_id"]
    who = _watcher(client)
    client.post(f"/desks/{did}/like", headers=who)
    client.post(f"/desks/{did}/share", json={})
    client.post(f"/desks/{did}/gift", json={"amount": 5}, headers=who)

    ov = client.get(f"/desks/{did}/overlay").json()
    assert ov["likes"] == 1 and ov["shares"] == 1
    assert ov["gift_total"] == 5.0 and len(ov["gifts"]) == 1
    # Semi-transparent and over the video — the picture stays readable, which
    # is the whole reason these live here rather than in a side panel.
    assert ov["style"]["over_video"] is True
    assert 0 < ov["style"]["opacity"] < 1


def test_the_overlay_is_behind_the_age_wall_on_a_rated_desk(client):
    created = _desk(client, owner_id="perf", attestor="perf", rated=True,
                    view_style="stage").json()
    did = created["desk_id"]
    assert client.get(f"/desks/{did}/overlay").status_code == 403
    assert client.get(f"/desks/{did}/overlay",
                      headers=_watcher(client)).status_code == 200


def test_joining_hands_back_the_overlay(client):
    """So a client can draw the stream and its reactions from one response."""
    created = _desk(client).json()
    out = client.post(f"/desks/{created['desk_id']}/join", json={},
                      headers=_watcher(client)).json()
    assert "overlay" in out and "style" in out["overlay"]
