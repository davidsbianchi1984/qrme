"""Community layer: mixed rooms across channels, marketplace listings,
providers, and consented session handoffs."""

import json

from tests.test_capabilities import (as_interactor, make_interactor,  # noqa: F401
                                     make_profile, pdi_pair)


def test_mixed_room_users_and_profiles(client):
    user = make_interactor(client, "Theo", "1990-01-01")
    dana = make_profile(client)
    echo = make_profile(client, display_name="Echo", kind="fictional",
                        persona="A thoughtful fictional conversationalist.")
    room = client.post("/rooms", json={
        "topic": "what memory means", "channel": "chat",
        "participants": [{"kind": "user", "id": user},
                         {"kind": "profile", "id": dana["id"]},
                         {"kind": "profile", "id": echo["id"]}]}).json()
    assert len(room["participants"]) == 3

    mine = as_interactor(user)
    r = client.post(f"/rooms/{room['id']}/messages", headers=mine, json={
        "sender_id": user, "message": "do machines remember, or just store?"})
    assert r.status_code == 201
    body = r.json()
    assert body["message"]["status"] == "approved"
    assert len(body["replies"]) == 2                 # both profiles answered
    assert all(reply["status"] == "approved" for reply in body["replies"])

    transcript = client.get(f"/rooms/{room['id']}/messages",
                            headers=mine).json()
    assert [m["sender_kind"] for m in transcript] == ["user", "profile", "profile"]
    # Only participants may speak — and it is the *token* that says who is
    # asking. Sending a participant's id from outside used to be enough.
    outsider = make_interactor(client, "Nosy")
    assert client.post(f"/rooms/{room['id']}/messages",
                       headers=as_interactor(outsider),
                       json={"sender_id": outsider,
                             "message": "hi"}).status_code == 403
    assert client.post(f"/rooms/{room['id']}/messages",
                       headers=as_interactor(outsider),
                       json={"sender_id": user,
                             "message": "hi"}).status_code == 403


def test_profile_to_profile_room_advance(client):
    dana = make_profile(client)
    echo = make_profile(client, display_name="Echo", kind="fictional",
                        persona="A thoughtful fictional conversationalist.")
    room = client.post("/rooms", json={
        "topic": "gardens", "channel": "voice",
        "participants": [{"kind": "profile", "id": dana["id"]},
                         {"kind": "profile", "id": echo["id"]}]}).json()
    # A profile-only room has no user participant to press the button, so
    # the advance and the read both go out as a profile's owner — which is
    # exactly the case `_require_in_room` accepts an owner token for.
    head = {"authorization": f"Bearer {dana['owner_token']}"}
    for _ in range(2):
        r = client.post(f"/rooms/{room['id']}/advance", headers=head)
        assert r.status_code == 201
        assert len(r.json()["replies"]) == 2
    transcript = client.get(f"/rooms/{room['id']}/messages",
                            headers=head).json()
    assert len(transcript) == 4
    assert {m["from"] for m in transcript} == {"Dana", "Echo"}


def test_room_channels_video_ar_vr(client):
    a = make_interactor(client, "A", "1990-01-01")
    b = make_interactor(client, "B", "1991-01-01")
    for channel, hint in (("video", "avatars"), ("ar", "augmented"),
                          ("vr", "virtual")):
        room = client.post("/rooms", json={
            "topic": "catch up", "channel": channel,
            "participants": [{"kind": "user", "id": a},
                             {"kind": "user", "id": b}]}).json()
        assert room["channel"] == channel
        assert hint in room["presence"]


def test_room_with_minor_runs_strict(client):
    minor = make_interactor(client, "Teen", "2012-06-01")
    dana = make_profile(client)
    room = client.post("/rooms", json={
        "topic": "homework", "channel": "chat",
        "participants": [{"kind": "user", "id": minor},
                         {"kind": "profile", "id": dana["id"]}]}).json()
    r = client.post(f"/rooms/{room['id']}/messages",
                    headers=as_interactor(minor),
                    json={"sender_id": minor,
                          "message": "someone sent me something nsfw"}).json()
    assert r["message"]["status"] == "blocked"       # strict, minor present
    assert r["replies"] == []                        # blocked input → no turns


def test_marketplace_listings(client):
    dana = make_profile(client)
    client.post("/marketplace/listings", json={
        "kind": "profile", "title": "Dana — legacy storyteller",
        "tags": ["legacy"], "provider_name": "the Bianchi family",
        "profile_id": dana["id"]})
    client.post("/marketplace/listings", json={
        "kind": "expertise", "title": "Retirement planning consults",
        "tags": ["finance", "stocks"], "area": "finance",
        "provider_name": "Marino Wealth", "business": True})
    client.post("/marketplace/listings", json={
        "kind": "service", "title": "Family therapy intake",
        "area": "relationships", "provider_name": "Riverside Counseling",
        "business": True})

    assert len(client.get("/marketplace/listings").json()) == 3
    finance = client.get("/marketplace/listings",
                         params={"area": "finance"}).json()
    assert finance[0]["business"] is True
    assert client.get("/marketplace/listings",
                      params={"kind": "profile"}).json()[0]["profile_id"] == dana["id"]
    # Profile listings require the profile.
    assert client.post("/marketplace/listings", json={
        "kind": "profile", "title": "x",
        "provider_name": "y"}).status_code == 422


def test_consented_handoff_to_local_provider(pdi_pair):
    client, fake = pdi_pair
    user = make_interactor(client, "Theo", "1990-01-01")
    doc = make_profile(client, display_name="Dr. Rivera",
                       persona="A calm mental-health specialist.",
                       purpose="companion_coach")
    client.post(f"/profiles/{doc['id']}/chat",
                json={"interactor_id": user, "message": "the panic is back"})
    provider = client.post("/providers", json={
        "name": "Riverside Behavioral Health", "area": "mental_health",
        "location": "12 Main St", "contact": "+1 555 0100"}).json()
    assert client.get("/providers",
                      params={"area": "mental_health"}).json()[0]["name"] == \
        "Riverside Behavioral Health"

    # No consent → no handoff, full stop.
    refused = client.post("/handoffs", json={
        "interactor_id": user, "provider_id": provider["id"],
        "profile_id": doc["id"]})
    assert refused.status_code == 403

    handoff = client.post("/handoffs", json={
        "interactor_id": user, "provider_id": provider["id"],
        "profile_id": doc["id"], "consent": True}).json()
    assert handoff["sealed"] is True                 # package in the PDI vault
    assert f"qrme/handoffs/{handoff['id']}" in fake.store

    # The provider redeems the token and gets the session package.
    package = client.get(f"/handoffs/{handoff['id']}",
                         params={"token": handoff["token"]}).json()["package"]
    assert package["specialist"] == "Dr. Rivera"
    assert package["sessions"] >= 1
    assert any("panic" in m["content"] for m in package["recent_exchange"])
    assert client.get(f"/handoffs/{handoff['id']}",
                      params={"token": "wrong"}).status_code == 403

    # Revocation purges the sealed package and kills the token.
    client.delete(f"/handoffs/{handoff['id']}")
    assert f"qrme/handoffs/{handoff['id']}" not in fake.store
    assert client.get(f"/handoffs/{handoff['id']}",
                      params={"token": handoff["token"]}).status_code == 403
