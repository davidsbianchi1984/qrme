"""Rated (18+) placement: adult-mode profiles marketed at adult venues via
QR beacons, @handles, and #tags — with the age wall traveling on every
discovery surface, no matter where the ref was published."""

ADULT = {"birthdate": "1984-06-01"}


def _rated_profile(client, handle="velvet_ivy"):
    r = client.post("/profiles", json={
        "owner_id": "owner-1", "kind": "fictional",
        "display_name": "Velvet Ivy", "adult_mode": True,
        "persona": "A flirtatious cabaret hostess persona for adult "
                   "audiences.", "maturity": "open",
        "verification": ADULT})
    assert r.status_code == 201, r.text
    out = r.json()
    client.headers["authorization"] = f"Bearer {out['owner_token']}"
    client.put(f"/profiles/{out['id']}/handle", json={"handle": handle})
    return out["id"]


def _interactor(client, birthdate):
    r = client.post("/interactors",
                    json={"display_name": "Viewer", "birthdate": birthdate})
    return {"authorization": f"Bearer {r.json()['token']}"}


def test_adult_mode_never_for_another_real_person(client):
    r = client.post("/profiles", json={
        "owner_id": "owner-1", "kind": "other_person",
        "display_name": "Someone Else", "adult_mode": True,
        "persona": "x", "verification": ADULT,
        "consent": {"basis": "subject_consent", "attestor": "owner-1"}})
    assert r.status_code == 403
    assert "another real person" in r.json()["detail"]


def test_venues_catalog_lists_willing_hosts(client):
    venues = {v["key"]: v for v in client.get("/venues").json()}
    assert {"onlyfans", "fansly", "xrated_directory"} <= set(venues)
    assert venues["onlyfans"]["hosts"] == ["profile", "beacon"]
    assert venues["xrated_directory"]["hosts"] == ["beacon"]
    assert all(v["age_wall"] for v in venues.values())


def test_placement_mints_an_age_walled_beacon(client):
    pid = _rated_profile(client)
    r = client.post(f"/profiles/{pid}/placements",
                    json={"venue": "onlyfans", "label": "bio link"})
    assert r.status_code == 201, r.text
    placement = r.json()
    assert placement["venue"]["name"] == "OnlyFans"
    assert placement["rated"] is True
    assert placement["handle"] == "@velvet_ivy"
    assert placement["qr_svg"].endswith("/qr.svg")

    # The printable QR exists…
    qr = client.get(placement["qr_svg"])
    assert qr.status_code == 200 and b"<svg" in qr.content

    # …and scanning it as an unverified viewer hits the wall, scan counted.
    scan = client.get("/summon", params={"ref": placement["beacon_id"]},
                      headers={"authorization": ""}).json()
    assert scan["scans"] == 1
    assert scan["profile"]["age_wall"] is True
    assert scan["profile"]["chat"] is None
    assert scan["profile"]["display_name"] == "age-restricted profile"

    listed = client.get(f"/profiles/{pid}/placements").json()
    assert len(listed) == 1 and listed[0]["venue_name"] == "OnlyFans"
    assert listed[0]["scans"] == 1

    # Unknown venue and non-rated profiles are refused.
    assert client.post(f"/profiles/{pid}/placements",
                       json={"venue": "nope"}).status_code == 404


def test_placement_requires_adult_mode(client, profile_id):
    r = client.post(f"/profiles/{profile_id}/placements",
                    json={"venue": "onlyfans"})
    assert r.status_code == 422
    assert "adult-mode" in r.json()["detail"]


def test_age_wall_travels_with_every_ref(client):
    pid = _rated_profile(client)
    client.post(f"/profiles/{pid}/placements", json={"venue": "fansly"})
    conn_headers_none = {"authorization": ""}
    adult = _interactor(client, "1990-01-01")
    minor = _interactor(client, "2012-01-01")

    # @handle: wall for anonymous and minors, card for verified adults.
    for headers in (conn_headers_none, minor):
        card = client.get("/summon", params={"ref": "@velvet_ivy"},
                          headers=headers).json()["profile"]
        assert card["age_wall"] is True and card["chat"] is None
    card = client.get("/summon", params={"ref": "@velvet_ivy"},
                      headers=adult).json()["profile"]
    assert card.get("age_wall") is None
    assert card["display_name"] == "Velvet Ivy"
    assert card["rated"] is True and card["chat"]


def test_tag_browse_omits_rated_for_unverified(client):
    pid = _rated_profile(client)
    import json as _json
    from qrme import db
    conn = db.connect()
    conn.execute(
        "INSERT INTO marketplace (profile_id, tags, blurb, listed_at)"
        " VALUES (?,?,?,?)",
        (pid, _json.dumps(["cabaret", "adult"]), "after dark", db.utcnow()))
    conn.commit()

    anon = client.get("/summon", params={"ref": "#cabaret"},
                      headers={"authorization": ""}).json()
    assert anon["profiles"] == []                # not even a hint in browse
    adult = _interactor(client, "1990-01-01")
    found = client.get("/summon", params={"ref": "#cabaret"},
                       headers=adult).json()["profiles"]
    assert len(found) == 1 and found[0]["rated"] is True


def test_marketplace_browse_hides_rated_listings(client):
    pid = _rated_profile(client)
    client.post("/marketplace/listings", json={
        "kind": "profile", "title": "Velvet Ivy — after dark",
        "tags": ["cabaret"], "provider_name": "Velvet Ivy",
        "profile_id": pid})
    anon = client.get("/marketplace/listings", headers={"authorization": ""})
    assert anon.json() == []
    adult = _interactor(client, "1990-01-01")
    seen = client.get("/marketplace/listings", headers=adult).json()
    assert len(seen) == 1 and seen[0]["title"].startswith("Velvet Ivy")


def test_removed_placement_stops_summoning(client):
    pid = _rated_profile(client)
    placement = client.post(f"/profiles/{pid}/placements",
                            json={"venue": "onlyfans"}).json()
    r = client.delete(f"/placements/{placement['placement_id']}")
    assert r.status_code == 200 and r.json()["beacon_active"] is False
    scan = client.get("/summon", params={"ref": placement["beacon_id"]},
                      headers={"authorization": ""})
    assert scan.status_code == 410               # picked up — gone
    assert client.get(f"/profiles/{pid}/placements").json() == []
