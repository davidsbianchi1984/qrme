"""User-to-user connections: anonymous matchmaking in friendly and rated
tiers, with age gates and per-tier moderation."""

from tests.test_capabilities import make_interactor


def test_friendly_match_and_anonymous_chat(client):
    a = make_interactor(client, "Theo", "1990-01-01")
    b = make_interactor(client, "Cat", "1992-02-02")

    first = client.post("/connections/join", json={
        "interactor_id": a, "alias": "NightOwl"}).json()
    assert first["status"] == "waiting"

    second = client.post("/connections/join", json={
        "interactor_id": b, "alias": "EarlyBird"}).json()
    assert second["status"] == "matched"
    assert second["matched_with"] == "NightOwl"
    cid = second["connection_id"]

    client.post(f"/connections/{cid}/messages", json={
        "interactor_id": a, "message": "hi — long day?"})
    client.post(f"/connections/{cid}/messages", json={
        "interactor_id": b, "message": "the longest. you?"})

    seen_by_a = client.get(f"/connections/{cid}/messages",
                           params={"interactor_id": a}).json()
    assert [m["from"] for m in seen_by_a] == ["you", "EarlyBird"]
    # Aliases only — real names never appear.
    import json
    assert "Cat" not in json.dumps(seen_by_a) and "Theo" not in json.dumps(seen_by_a)

    # Outsiders can't read the thread.
    outsider = make_interactor(client, "Nosy")
    r = client.get(f"/connections/{cid}/messages",
                   params={"interactor_id": outsider})
    assert r.status_code == 403


def test_rated_tier_requires_verified_adults(client):
    minor = make_interactor(client, "Kid", "2012-01-01")
    r = client.post("/connections/join", json={
        "interactor_id": minor, "tier": "rated"})
    assert r.status_code == 403

    unverified = make_interactor(client, "NoBirthdate", None)
    r = client.post("/connections/join", json={
        "interactor_id": unverified, "tier": "rated"})
    assert r.status_code == 403

    a = make_interactor(client, "A", "1990-01-01")
    b = make_interactor(client, "B", "1988-05-05")
    client.post("/connections/join", json={"interactor_id": a, "tier": "rated"})
    match = client.post("/connections/join", json={
        "interactor_id": b, "tier": "rated"}).json()
    assert match["status"] == "matched"

    # Between verified consenting adults, the rated tier runs open.
    r = client.post(f"/connections/{match['connection_id']}/messages", json={
        "interactor_id": a, "message": "fair warning, this gets nsfw"}).json()
    assert r["status"] == "approved"


def test_friendly_tier_shields_minors(client):
    adult = make_interactor(client, "Adult", "1990-01-01")
    minor = make_interactor(client, "Teen", "2012-06-01")
    client.post("/connections/join", json={"interactor_id": adult})
    match = client.post("/connections/join", json={
        "interactor_id": minor}).json()
    cid = match["connection_id"]

    blocked = client.post(f"/connections/{cid}/messages", json={
        "interactor_id": adult, "message": "want something nsfw?"}).json()
    assert blocked["status"] == "blocked"
    # The blocked message never reaches the minor.
    seen = client.get(f"/connections/{cid}/messages",
                      params={"interactor_id": minor}).json()
    assert seen == []


def test_either_side_can_end_it(client):
    a = make_interactor(client, "A", "1990-01-01")
    b = make_interactor(client, "B", "1991-01-01")
    client.post("/connections/join", json={"interactor_id": a})
    cid = client.post("/connections/join",
                      json={"interactor_id": b}).json()["connection_id"]

    client.post(f"/connections/{cid}/end", params={"interactor_id": b})
    r = client.post(f"/connections/{cid}/messages", json={
        "interactor_id": a, "message": "still there?"})
    assert r.status_code == 410
