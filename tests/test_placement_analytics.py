"""Placement analytics: what each adult venue earns. Per-venue scan counts
split walled vs. verified with a daily trend, plus the profile funnel —
resolutions → verified views → unique chatters. Owner-only; viewers are
counted, never identified."""

ADULT = {"birthdate": "1984-06-01"}


def _rated_profile(client):
    r = client.post("/profiles", json={
        "owner_id": "owner-1", "kind": "fictional",
        "display_name": "Velvet Ivy", "adult_mode": True,
        "persona": "A flirtatious cabaret hostess persona for adult "
                   "audiences.", "maturity": "open",
        "verification": ADULT})
    out = r.json()
    client.headers["authorization"] = f"Bearer {out['owner_token']}"
    client.put(f"/profiles/{out['id']}/handle", json={"handle": "velvet_ivy"})
    return out["id"]


def _interactor(client, birthdate):
    r = client.post("/interactors",
                    json={"display_name": "Viewer", "birthdate": birthdate})
    return r.json()["id"], {"authorization": f"Bearer {r.json()['token']}"}


def test_funnel_counts_walls_verified_views_and_chatters(client):
    pid = _rated_profile(client)
    placement = client.post(f"/profiles/{pid}/placements",
                            json={"venue": "onlyfans"}).json()
    beacon = placement["beacon_id"]
    _, adult = _interactor(client, "1990-01-01")
    adult_id = adult["authorization"]

    # Two anonymous scans hit the wall; one verified adult gets through.
    for _ in range(2):
        client.get("/summon", params={"ref": beacon},
                   headers={"authorization": ""})
    client.get("/summon", params={"ref": beacon}, headers=adult)
    # One anonymous direct @handle summon — its own row, no beacon.
    client.get("/summon", params={"ref": "@velvet_ivy"},
               headers={"authorization": ""})
    # The verified adult converts to a chat.
    interactor_id, _ = _interactor(client, "1991-05-05")
    client.post(f"/profiles/{pid}/chat",
                json={"interactor_id": interactor_id, "message": "hello"})

    a = client.get(f"/profiles/{pid}/placements/analytics").json()
    venue = a["venues"][0]
    assert venue["venue_name"] == "OnlyFans"
    assert venue["scans"] == 3
    assert venue["walled"] == 2 and venue["verified"] == 1
    assert venue["by_day"] and venue["by_day"][0]["scans"] == 3

    assert a["direct"] == {"walled": 1, "verified": 0}
    f = a["funnel"]
    assert f["resolutions"] == 4 and f["verified_views"] == 1
    assert f["unique_chatters"] == 1
    assert f["verified_rate"] == 0.25 and f["chat_rate"] == 1.0


def test_analytics_split_per_venue(client):
    pid = _rated_profile(client)
    only = client.post(f"/profiles/{pid}/placements",
                       json={"venue": "onlyfans"}).json()
    fans = client.post(f"/profiles/{pid}/placements",
                       json={"venue": "fansly"}).json()
    client.get("/summon", params={"ref": only["beacon_id"]},
               headers={"authorization": ""})
    _, adult = _interactor(client, "1990-01-01")
    for _ in range(2):
        client.get("/summon", params={"ref": fans["beacon_id"]},
                   headers=adult)

    a = client.get(f"/profiles/{pid}/placements/analytics").json()
    by_venue = {v["venue"]: v for v in a["venues"]}
    assert by_venue["onlyfans"]["walled"] == 1
    assert by_venue["onlyfans"]["verified"] == 0
    assert by_venue["fansly"]["walled"] == 0
    assert by_venue["fansly"]["verified"] == 2


def test_analytics_are_owner_only_and_empty_when_unmarketed(client):
    pid = _rated_profile(client)
    a = client.get(f"/profiles/{pid}/placements/analytics").json()
    assert a["venues"] == [] and a["funnel"]["resolutions"] == 0
    assert a["funnel"]["verified_rate"] is None
    r = client.get(f"/profiles/{pid}/placements/analytics",
                   headers={"authorization": ""})
    assert r.status_code in (401, 403)


def test_non_rated_profiles_record_no_events(client, profile_id):
    client.put(f"/profiles/{profile_id}/handle", json={"handle": "dana"})
    client.get("/summon", params={"ref": "@dana"},
               headers={"authorization": ""})
    from qrme import db
    n = db.connect().execute(
        "SELECT COUNT(*) AS n FROM rated_events").fetchone()["n"]
    assert n == 0                     # ordinary profiles leave no trail