"""The starter collection: one synthetic profile per industry, seeded so a
fresh marketplace has profiles to immerse with before users publish their
own. Each starter gets a claimed @handle, a marketplace listing, and works
end-to-end through summoning and chat like any user profile."""

from qrme.seed import STARTERS


def test_starters_cover_every_industry_exactly_once():
    industries = [industry for _, industry, *_ in STARTERS]
    assert len(industries) == len(set(industries))    # one per industry
    assert len(industries) >= 30
    handles = [handle for handle, *_ in STARTERS]
    assert len(handles) == len(set(handles))


def test_seed_populates_the_marketplace(client):
    r = client.post("/marketplace/seed")
    assert r.status_code == 201, r.text
    out = r.json()
    assert out["created"] == len(STARTERS) and out["skipped"] == 0

    listings = client.get("/marketplace/listings").json()
    assert len(listings) >= len(STARTERS)
    by_area = {l["area"] for l in listings}
    assert {"healthcare", "finance", "technology", "legal",
            "agriculture", "cybersecurity", "music"} <= by_area
    assert all(l["provider_name"] == "QRME Starter Collection"
               for l in listings if l["area"] in by_area)

    # Browse narrows by tag, the immersion entry point.
    fitness = client.get("/marketplace/listings", params={"tag": "fitness"}).json()
    assert any("Dana Reyes" in l["title"] for l in fitness)


def test_seed_is_idempotent(client):
    first = client.post("/marketplace/seed").json()
    second = client.post("/marketplace/seed").json()
    assert first["created"] == len(STARTERS)
    assert second["created"] == 0 and second["skipped"] == len(STARTERS)
    listings = client.get("/marketplace/listings").json()
    assert len(listings) == len(STARTERS)             # no duplicates


def test_starters_are_summonable_by_handle_and_tag(client):
    client.post("/marketplace/seed")
    r = client.get("/summon", params={"ref": "@dr_amara_osei"}).json()
    assert r["type"] == "handle"
    assert r["profile"]["display_name"] == "Dr. Amara Osei"
    assert r["profile"]["chat"]                        # reachable

    r = client.get("/summon", params={"ref": "#healthcare"}).json()
    assert any(p["display_name"] == "Dr. Amara Osei" for p in r["profiles"])


def test_visitors_can_immerse_with_a_starter(client):
    client.post("/marketplace/seed")
    pid = client.get("/summon", params={"ref": "@chef_henri_laurent"}
                     ).json()["profile"]["profile_id"]
    interactor = client.post(
        "/interactors", json={"display_name": "Sam",
                              "birthdate": "2000-01-15"}).json()["id"]
    r = client.post(f"/profiles/{pid}/chat",
                    json={"interactor_id": interactor,
                          "message": "How do I make a pan sauce?"})
    assert r.status_code == 200, r.text
    reply = r.json()
    assert reply["profile_message"]["status"] == "approved"
    # Same provenance guarantees as any user profile.
    assert reply["provenance"]["grounded_in"]["persona"] is True
