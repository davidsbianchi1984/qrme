"""Knowledge packs: downloadable clusters of curated expertise. Installing
one genuinely grows the profile — the items become source material that
grounds the persona's knowledge base and shows up in provenance."""

from qrme.packs import STARTER_PACKS

TRIO = {"mental_health", "psychiatry", "counseling"}


def test_starter_packs_cover_every_industry():
    from qrme.seed import STARTERS
    industries = {industry for _, industry, *_ in STARTERS}
    assert set(STARTER_PACKS) == industries       # one pack per industry
    for title, items in STARTER_PACKS.values():
        assert len(items) >= 3
        assert all(content for _, content in items)


def test_seed_populates_catalog_and_marketplace(client):
    from qrme.packs import ROBOT_PACKS
    total = len(STARTER_PACKS) + len(ROBOT_PACKS)
    r = client.post("/packs/seed")
    assert r.status_code == 201, r.text
    out = r.json()
    assert out["created"] == total + 1 and out["skipped"] == 0  # +1 rated

    # The rated pack never appears in an unverified catalog.
    catalog = client.get("/packs").json()
    assert len(catalog) == total
    profile_packs = [p for p in catalog if p["audience"] == "profile"]
    assert len(profile_packs) == len(STARTER_PACKS)
    assert all(p["free"] and p["items"] >= 3 for p in profile_packs)

    # Narrow by industry; detail shows titles, never contents.
    fin = client.get("/packs", params={"industry": "finance"}).json()
    assert len(fin) == 1
    detail = client.get(f"/packs/{fin[0]['id']}").json()
    assert len(detail["item_titles"]) == fin[0]["items"]
    assert "content" not in detail and "contents" not in detail

    # Packs surface in the marketplace browse under the pack tag.
    listings = client.get("/marketplace/listings", params={"tag": "pack"}).json()
    assert len(listings) == total
    assert all(l["kind"] == "expertise" for l in listings)

    second = client.post("/packs/seed").json()
    assert second["created"] == 0 and second["skipped"] == total + 1


def test_free_install_grows_the_knowledge_base(client, profile_id, interactor_id):
    client.post("/packs/seed")
    pack = client.get("/packs", params={"industry": "culinary"}).json()[0]
    r = client.post(f"/packs/{pack['id']}/install",
                    json={"profile_id": profile_id})
    assert r.status_code == 201, r.text
    out = r.json()
    assert out["installed_items"] == pack["items"] and out["price_paid"] == 0

    sources = client.get(f"/profiles/{profile_id}/sources").json()
    pack_items = [s for s in sources if s["kind"] == "pack"]
    assert len(pack_items) == pack["items"]

    # The persona's system prompt now carries the pack knowledge…
    from qrme import db, persona
    from qrme.common import source_items
    profile = dict(db.connect().execute(
        "SELECT * FROM profiles WHERE id=?", (profile_id,)).fetchone())
    prompt = persona.build_system_prompt(
        profile, None, None, sources=source_items(profile_id, None))
    assert "Salt is a decision" in prompt

    # …and chat provenance counts the pack grounding honestly.
    reply = client.post(f"/profiles/{profile_id}/chat",
                        json={"interactor_id": interactor_id,
                              "message": "how should I season a soup?"}).json()
    assert reply["provenance"]["grounded_in"]["by_kind"]["pack"] == pack["items"]

    # Installed list reflects it; double-install is refused.
    installed = client.get(f"/profiles/{profile_id}/packs").json()
    assert [p["id"] for p in installed] == [pack["id"]]
    assert client.post(f"/packs/{pack['id']}/install",
                       json={"profile_id": profile_id}).status_code == 409


def test_priced_pack_requires_explicit_purchase(client, profile_id):
    pub = client.post("/packs", json={
        "industry": "technology", "title": "Distributed Systems Pro Pack",
        "blurb": "Battle-tested patterns.", "price": 29.99,
        "publisher": "Priya Raman Consulting",
        "items": [{"title": "Idempotency keys",
                   "content": "Every retryable request carries a client key; "
                              "the server does each key's work once."},
                  {"title": "Backpressure",
                   "content": "Bound every queue; a system that cannot say "
                              "'slow down' says 'fall over' instead."}]})
    assert pub.status_code == 201, pub.text
    pack = pub.json()
    assert pack["free"] is False

    r = client.post(f"/packs/{pack['id']}/install",
                    json={"profile_id": profile_id})
    assert r.status_code == 402                    # payment consent required
    r = client.post(f"/packs/{pack['id']}/install",
                    json={"profile_id": profile_id, "accept_price": True})
    assert r.status_code == 201
    assert r.json()["price_paid"] == 29.99
    installed = client.get(f"/profiles/{profile_id}/packs").json()
    assert installed[0]["price_paid"] == 29.99


def test_uninstall_shrinks_the_knowledge_base(client, profile_id):
    client.post("/packs/seed")
    pack = client.get("/packs", params={"industry": "music"}).json()[0]
    client.post(f"/packs/{pack['id']}/install", json={"profile_id": profile_id})
    r = client.delete(f"/profiles/{profile_id}/packs/{pack['id']}")
    assert r.status_code == 200
    assert r.json()["removed_items"] == pack["items"]
    sources = client.get(f"/profiles/{profile_id}/sources").json()
    assert not any(s["kind"] == "pack" for s in sources)
    assert client.get(f"/profiles/{profile_id}/packs").json() == []
    # Not installed → 404, and the catalog entry is untouched.
    assert client.delete(
        f"/profiles/{profile_id}/packs/{pack['id']}").status_code == 404
    assert client.get(f"/packs/{pack['id']}").status_code == 200


def test_wellbeing_packs_keep_the_care_line():
    for industry in TRIO:
        _, items = STARTER_PACKS[industry]
        text = " ".join(content for _, content in items)
        assert "988" in text                      # crisis path always named
    assert "Education, not treatment." in " ".join(
        c for _, c in STARTER_PACKS["mental_health"][1])


def test_install_requires_the_owner(client, profile_id):
    client.post("/packs/seed")
    pack = client.get("/packs").json()[0]
    r = client.post(f"/packs/{pack['id']}/install",
                    json={"profile_id": profile_id},
                    headers={"authorization": ""})
    assert r.status_code in (401, 403)
