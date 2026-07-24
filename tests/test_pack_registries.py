"""Federated pack registries: Robotmods.net (robot task mods) and
LLMmods.com (persona knowledge mods) publish into the marketplace. Synced
packs carry their origin on the label and behave exactly like local ones."""

from qrme.pack_sources import REGISTRIES


def test_registries_are_listed_with_sync_state(client):
    regs = {r["key"]: r for r in client.get("/packs/registries").json()}
    assert set(regs) == {"robotmods", "llmmods"}
    assert regs["robotmods"]["name"] == "Robotmods.net"
    assert regs["robotmods"]["url"] == "https://robotmods.net"
    assert regs["robotmods"]["audience"] == "robot"
    assert regs["llmmods"]["name"] == "LLMmods.com"
    assert regs["llmmods"]["audience"] == "profile"
    assert all(r["synced"] == 0 and r["available"] == 2 for r in regs.values())

    client.post("/packs/registries/robotmods/sync")
    regs = {r["key"]: r for r in client.get("/packs/registries").json()}
    assert regs["robotmods"]["synced"] == 2 and regs["llmmods"]["synced"] == 0


def test_sync_imports_with_origin_and_is_idempotent(client):
    first = client.post("/packs/registries/robotmods/sync")
    assert first.status_code == 201, first.text
    assert first.json()["created"] == 2
    second = client.post("/packs/registries/robotmods/sync").json()
    assert second["created"] == 0 and second["skipped"] == 2

    catalog = client.get("/packs", params={"audience": "robot"}).json()
    assert {p["title"] for p in catalog} == {"Pet Care Mod",
                                            "Workshop Assistant Mod"}
    assert all(p["origin"] == "robotmods" and
               p["origin_url"] == "https://robotmods.net" for p in catalog)
    assert all(p["publisher"] == "Robotmods.net" for p in catalog)

    # Marketplace browse finds them under the registry tag.
    listings = client.get("/marketplace/listings",
                          params={"tag": "robotmods"}).json()
    assert len(listings) == 2
    assert all(l["provider_name"] == "Robotmods.net" for l in listings)

    assert client.post("/packs/registries/nope/sync").status_code == 404


def test_robotmods_pack_installs_like_any_robot_pack(client, profile_id):
    client.post("/packs/registries/robotmods/sync")
    robot_id = client.post(f"/profiles/{profile_id}/robots",
                           json={"model": "neo"}).json()["id"]
    pet = next(p for p in client.get("/packs").json()
               if p["title"] == "Pet Care Mod")
    r = client.post(f"/packs/{pet['id']}/install",
                    json={"profile_id": profile_id, "robot_id": robot_id})
    assert r.status_code == 201, r.text
    r = client.post(f"/robots/{robot_id}/command",
                    json={"command": "feed_pets"})
    assert r.status_code == 201
    assert r.json()["pack"] == "Pet Care Mod"
    assert "never free-feed" in r.json()["procedure"]

    # The priced Workshop mod keeps the buy-consent flow.
    shop = next(p for p in client.get("/packs").json()
                if p["title"] == "Workshop Assistant Mod")
    assert shop["price"] == 4.99
    r = client.post(f"/packs/{shop['id']}/install",
                    json={"profile_id": profile_id, "robot_id": robot_id})
    assert r.status_code == 402
    r = client.post(f"/packs/{shop['id']}/install",
                    json={"profile_id": profile_id, "robot_id": robot_id,
                          "accept_price": True})
    assert r.status_code == 201 and r.json()["price_paid"] == 4.99


def test_llmmods_pack_grounds_the_persona(client, profile_id, interactor_id):
    client.post("/packs/registries/llmmods/sync")
    nego = next(p for p in client.get("/packs").json()
                if p["title"] == "Negotiation Mod")
    assert nego["free"] and nego["audience"] == "profile"
    r = client.post(f"/packs/{nego['id']}/install",
                    json={"profile_id": profile_id})
    assert r.status_code == 201, r.text

    reply = client.post(f"/profiles/{profile_id}/chat",
                        json={"interactor_id": interactor_id,
                              "message": "how do I negotiate rent?"}).json()
    assert reply["provenance"]["grounded_in"]["by_kind"]["pack"] == 3

    speak = next(p for p in client.get("/packs").json()
                 if p["title"] == "Public Speaking Mod")
    assert speak["price"] == 3.49
    assert client.post(f"/packs/{speak['id']}/install",
                       json={"profile_id": profile_id}).status_code == 402


def test_registry_safety_lines_hold():
    robot_packs = REGISTRIES["robotmods"]["packs"]
    workshop = next(p for p in robot_packs
                    if p["title"] == "Workshop Assistant Mod")
    text = " ".join(procedure for *_, procedure in workshop["items"])
    assert "power tools are never touched" in text
    assert "never hold the workpiece" in text
