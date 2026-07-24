"""Rated (18+) commerce: the age wall covers buying, not just viewing.
Rated packs are invisible to unverified callers and install only onto
adult-mode profiles; a rated profile's license offer and acquisition both
require an age-verified party."""

from qrme.packs import RATED_PACK

ADULT = {"birthdate": "1984-06-01"}


def _adult_profile(client):
    r = client.post("/profiles", json={
        "owner_id": "owner-1", "kind": "fictional",
        "display_name": "Velvet Ivy", "adult_mode": True,
        "persona": "A flirtatious cabaret hostess persona for adult "
                   "audiences.", "maturity": "open",
        "verification": ADULT})
    assert r.status_code == 201, r.text
    out = r.json()
    return out["id"], {"authorization": f"Bearer {out['owner_token']}"}


def _interactor(client, birthdate):
    r = client.post("/interactors",
                    json={"display_name": "Viewer", "birthdate": birthdate})
    return r.json()["id"], {"authorization": f"Bearer {r.json()['token']}"}


def test_rated_pack_invisible_without_age_verification(client, profile_id):
    client.post("/packs/seed")
    # Anonymous, a minor interactor, and a non-adult profile's owner all
    # see a catalog without the rated pack.
    _, minor = _interactor(client, "2012-01-01")
    for headers in ({"authorization": ""}, minor, None):
        catalog = (client.get("/packs", headers=headers) if headers
                   else client.get("/packs")).json()
        assert all(not p["rated"] for p in catalog)

    _, adult = _interactor(client, "1990-01-01")
    rated = [p for p in client.get("/packs", headers=adult).json()
             if p["rated"]]
    assert len(rated) == 1
    assert rated[0]["title"] == RATED_PACK[1]
    assert rated[0]["price"] == RATED_PACK[2]

    # Detail: walled for the unverified, open shop window for adults.
    r = client.get(f"/packs/{rated[0]['id']}", headers={"authorization": ""})
    assert r.status_code == 403 and "18+" in r.json()["detail"]
    detail = client.get(f"/packs/{rated[0]['id']}", headers=adult).json()
    assert len(detail["item_titles"]) == 3


def test_rated_pack_never_listed_on_the_open_marketplace(client):
    client.post("/packs/seed")
    _, adult = _interactor(client, "1990-01-01")
    listings = client.get("/marketplace/listings", params={"tag": "pack"},
                          headers=adult).json()
    assert all(RATED_PACK[1] not in l["title"] for l in listings)


def test_rated_pack_installs_only_onto_adult_mode_profiles(client, profile_id):
    client.post("/packs/seed")
    _, adult = _interactor(client, "1990-01-01")
    pack = next(p for p in client.get("/packs", headers=adult).json()
                if p["rated"])

    # A regular profile is refused, price consent or not.
    r = client.post(f"/packs/{pack['id']}/install",
                    json={"profile_id": profile_id, "accept_price": True})
    assert r.status_code == 403
    assert "adult-mode" in r.json()["detail"]

    # An adult-mode profile buys it with the usual explicit consent —
    # and its owner token sees rated commerce (adult proven at creation).
    pid, owner = _adult_profile(client)
    client.headers["authorization"] = owner["authorization"]
    visible = [p for p in client.get("/packs").json() if p["rated"]]
    assert len(visible) == 1
    r = client.post(f"/packs/{pack['id']}/install",
                    json={"profile_id": pid})
    assert r.status_code == 402                    # priced: consent first
    r = client.post(f"/packs/{pack['id']}/install",
                    json={"profile_id": pid, "accept_price": True})
    assert r.status_code == 201 and r.json()["price_paid"] == RATED_PACK[2]
    sources = client.get(f"/profiles/{pid}/sources").json()
    assert sum(1 for s in sources if s["kind"] == "pack") == 3


def test_rated_license_offer_is_age_gated(client):
    pid, owner = _adult_profile(client)
    client.headers["authorization"] = owner["authorization"]
    client.put(f"/profiles/{pid}/license",
               json={"kind": "consult", "price": 49.0,
                     "terms": "adult persona consult"})

    r = client.get(f"/profiles/{pid}/license", headers={"authorization": ""})
    assert r.status_code == 403 and "18+" in r.json()["detail"]
    _, minor = _interactor(client, "2012-01-01")
    assert client.get(f"/profiles/{pid}/license",
                      headers=minor).status_code == 403
    _, adult = _interactor(client, "1990-01-01")
    offer = client.get(f"/profiles/{pid}/license", headers=adult).json()
    assert offer["price"] == 49.0


def test_rated_license_acquisition_requires_verified_adult(client):
    pid, owner = _adult_profile(client)
    client.headers["authorization"] = owner["authorization"]
    client.put(f"/profiles/{pid}/license",
               json={"kind": "consult", "price": 49.0})

    _, minor = _interactor(client, "2012-01-01")
    r = client.post(f"/profiles/{pid}/license/acquire", headers=minor)
    assert r.status_code == 403
    assert "verified-18+" in r.json()["detail"]

    _, adult = _interactor(client, "1990-01-01")
    r = client.post(f"/profiles/{pid}/license/acquire", headers=adult)
    assert r.status_code == 201, r.text
    assert r.json()["kind"] == "consult"


def test_rated_pack_content_stays_consent_forward():
    _, _, _, items = RATED_PACK
    text = " ".join(f"{title} {content}" for title, content in items)
    assert "Consent" in text
    assert "'no' or a pause as a full answer" in text
