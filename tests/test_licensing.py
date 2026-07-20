"""Training-data licensing: offer expertise, acquire a license, derive a
specialist agent with provenance, and revoke."""

from tests.test_capabilities import as_owner, make_profile


def _buyer(client, birthdate="1990-01-01"):
    """An interactor acting as a buyer; returns (id, auth-header)."""
    who = client.post("/interactors", json={
        "display_name": "Buyer", "birthdate": birthdate}).json()
    return who["id"], {"authorization": f"Bearer {who['token']}"}


def test_offer_and_public_terms(client):
    p = make_profile(client, persona="A master sommelier's palate and lore.")
    r = client.put(f"/profiles/{p['id']}/license", json={
        "kind": "finetune", "price": 49, "terms": "non-exclusive, 1 year"})
    assert r.status_code == 200 and r.json()["allow_derivatives"] is True
    # Public terms are visible to prospective buyers (no auth).
    terms = client.get(f"/profiles/{p['id']}/license", headers={}).json()
    assert terms["kind"] == "finetune" and terms["price"] == 49


def test_consult_license_forbids_derivation(client):
    p = make_profile(client)
    client.put(f"/profiles/{p['id']}/license", json={"kind": "consult"})
    buyer_id, hdr = _buyer(client)
    g = client.post(f"/profiles/{p['id']}/license/acquire", headers=hdr).json()
    assert g["can_derive"] is False
    r = client.post(f"/profiles/{p['id']}/license/{g['grant_id']}/derive",
                    headers=hdr)
    assert r.status_code == 403


def test_acquire_and_derive_a_specialist_agent(client):
    p = make_profile(client, persona="A calm CBT therapist's approach.")
    as_owner(client, p)
    client.put(f"/profiles/{p['id']}/license", json={
        "kind": "finetune", "price": 20})
    buyer_id, hdr = _buyer(client)

    g = client.post(f"/profiles/{p['id']}/license/acquire", headers=hdr).json()
    assert g["can_derive"] is True and g["token"].startswith("lic_")

    derived = client.post(
        f"/profiles/{p['id']}/license/{g['grant_id']}/derive", headers=hdr).json()
    assert derived["licensed_from"] == p["id"]
    assert derived["owner_id"] == buyer_id
    assert derived["owner_token"]

    # The derived agent is a real, buyer-owned profile with provenance, and it
    # chats in-character.
    child = client.get(f"/profiles/{derived['derived_profile_id']}").json()
    assert child["licensed_from"] == p["id"] and child["owner_id"] == buyer_id
    user = client.post("/interactors", json={"display_name": "U"}).json()["id"]
    reply = client.post(f"/profiles/{child['id']}/chat",
                        json={"interactor_id": user, "message": "help me"})
    assert reply.status_code == 200

    # Deriving twice from the same grant is a conflict.
    again = client.post(
        f"/profiles/{p['id']}/license/{g['grant_id']}/derive", headers=hdr)
    assert again.status_code == 409

    # The owner can see who licensed it.
    as_owner(client, p)
    lics = client.get(f"/profiles/{p['id']}/licenses").json()
    assert lics[0]["buyer_id"] == buyer_id
    assert lics[0]["derived_profile_id"] == derived["derived_profile_id"]


def test_revoked_license_cannot_derive(client):
    p = make_profile(client)
    as_owner(client, p)
    client.put(f"/profiles/{p['id']}/license", json={"kind": "clone"})
    buyer_id, hdr = _buyer(client)
    g = client.post(f"/profiles/{p['id']}/license/acquire", headers=hdr).json()

    as_owner(client, p)
    assert client.delete(f"/licenses/{g['grant_id']}").status_code == 200
    r = client.post(f"/profiles/{p['id']}/license/{g['grant_id']}/derive",
                    headers=hdr)
    assert r.status_code == 403


def test_minor_buyer_cannot_derive(client):
    p = make_profile(client)
    as_owner(client, p)
    client.put(f"/profiles/{p['id']}/license", json={"kind": "clone"})
    minor_id, hdr = _buyer(client, birthdate="2015-01-01")
    g = client.post(f"/profiles/{p['id']}/license/acquire", headers=hdr).json()
    r = client.post(f"/profiles/{p['id']}/license/{g['grant_id']}/derive",
                    headers=hdr)
    assert r.status_code == 403


def test_acquire_requires_a_buyer_token(client):
    p = make_profile(client)
    as_owner(client, p)
    client.put(f"/profiles/{p['id']}/license", json={"kind": "consult"})
    # No token → 401; an owner token (not an interactor) → 403.
    assert client.post(f"/profiles/{p['id']}/license/acquire",
                       headers={"authorization": ""}).status_code == 401
    assert client.post(f"/profiles/{p['id']}/license/acquire").status_code == 403
