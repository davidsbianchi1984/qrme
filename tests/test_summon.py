"""Summoning: @handles, #tags, and QR beacons for leaving profiles behind."""

from tests.test_capabilities import make_interactor, make_profile, pdi_pair  # noqa: F401


def test_claim_and_summon_by_handle(client):
    p = make_profile(client)
    r = client.put(f"/profiles/{p['id']}/handle", json={"handle": "@Dana_G"})
    assert r.status_code == 200
    assert r.json()["handle"] == "@dana_g"          # normalized lowercase

    card = client.get("/summon", params={"ref": "@dana_g"}).json()
    assert card["type"] == "handle"
    assert card["profile"]["profile_id"] == p["id"]
    assert card["profile"]["chat"] == f"/profiles/{p['id']}/chat"
    assert "persona" not in card["profile"]         # public card only

    # Handles are unique: another profile can't take it.
    other = make_profile(client, display_name="Echo")
    taken = client.put(f"/profiles/{other['id']}/handle",
                       json={"handle": "dana_g"})
    assert taken.status_code == 409
    # But re-claiming your own handle is fine.
    assert client.put(f"/profiles/{p['id']}/handle",
                      json={"handle": "dana_g"}).status_code == 200

    assert client.get("/summon",
                      params={"ref": "@nobody"}).status_code == 404


def test_summon_by_hashtag(client):
    garden = make_profile(client)
    client.post(f"/profiles/{garden['id']}/marketplace",
                json={"tags": ["Gardening", "legacy"]})
    fiction = make_profile(client, display_name="Nyx", kind="fictional",
                           anonymous=True)
    client.post(f"/profiles/{fiction['id']}/marketplace",
                json={"tags": ["fiction"]})

    hit = client.get("/summon", params={"ref": "#gardening"}).json()
    assert hit["type"] == "tag"
    assert [c["profile_id"] for c in hit["profiles"]] == [garden["id"]]

    anon = client.get("/summon", params={"ref": "#fiction"}).json()
    assert anon["profiles"][0]["display_name"] == "anonymous persona"


def test_beacon_left_behind_and_scanned(client):
    p = make_profile(client)
    beacon = client.post(f"/profiles/{p['id']}/beacons", json={
        "label": "Rosa's garden bench",
        "location": "Riverside Park, third bench past the willow"}).json()
    assert beacon["summon_url"].endswith(f"/summon?ref={beacon['id']}")

    # A real, printable QR code.
    qr = client.get(beacon["qr_svg"])
    assert qr.status_code == 200
    assert qr.headers["content-type"].startswith("image/svg+xml")
    assert b"<svg" in qr.content

    # Scanning summons the profile and counts the visit.
    for expected in (1, 2):
        hit = client.get("/summon", params={"ref": beacon["id"]}).json()
        assert hit["type"] == "beacon"
        assert hit["label"] == "Rosa's garden bench"
        assert hit["scans"] == expected
        assert hit["profile"]["profile_id"] == p["id"]

    # Picked up → the placed code stops summoning.
    client.delete(f"/beacons/{beacon['id']}")
    assert client.get("/summon",
                      params={"ref": beacon["id"]}).status_code == 410


def test_departed_beacon_becomes_memorial(pdi_pair):
    client, _ = pdi_pair
    p = make_profile(client)
    user = make_interactor(client)
    client.put(f"/profiles/{p['id']}/relationships/{user}",
               json={"relationship_type": "family"})
    beacon = client.post(f"/profiles/{p['id']}/beacons",
                         json={"label": "memorial plaque"}).json()
    client.post(f"/profiles/{p['id']}/sunset")

    hit = client.get("/summon", params={"ref": beacon["id"]}).json()
    assert hit["profile"]["status"] == "departed"
    assert hit["profile"]["chat"] is None
    assert "memory remains" in hit["profile"]["note"]
