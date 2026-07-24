"""The creator ledger: every priced sale accrues to its creator at
transaction time — pack sales (rated included), license fees — and the
owner statement + simulated payout make the accounting visible."""

ADULT = {"birthdate": "1984-06-01"}


def _profile(client, owner="creator-1", name="Priya Raman", **extra):
    r = client.post("/profiles", json={
        "owner_id": owner, "kind": "fictional", "display_name": name,
        "persona": "A pragmatic software architect.",
        "verification": ADULT, **extra})
    assert r.status_code == 201, r.text
    out = r.json()
    return out["id"], f"Bearer {out['owner_token']}"


def test_pack_sale_accrues_to_the_publisher(client):
    seller_pid, seller_tok = _profile(client)
    pub = client.post("/packs", json={
        "industry": "technology", "title": "Distributed Systems Pro Pack",
        "price": 29.99, "publisher": "Priya Raman Consulting",
        "publisher_owner_id": "creator-1",
        "items": [{"title": "Idempotency keys", "content": "Do it once."}]})
    pack_id = pub.json()["id"]

    buyer_pid, buyer_tok = _profile(client, owner="buyer-1", name="Dana")
    client.headers["authorization"] = buyer_tok
    r = client.post(f"/packs/{pack_id}/install",
                    json={"profile_id": buyer_pid, "accept_price": True})
    assert r.status_code == 201, r.text

    client.headers["authorization"] = seller_tok
    s = client.get(f"/profiles/{seller_pid}/earnings").json()
    assert s["owner_id"] == "creator-1"
    assert len(s["entries"]) == 1
    entry = s["entries"][0]
    assert entry["kind"] == "pack_sale" and entry["amount"] == 29.99
    assert entry["memo"] == "Distributed Systems Pro Pack"
    assert entry["status"] == "accrued"
    assert s["totals"]["accrued"] == 29.99 and s["totals"]["paid"] == 0

    # Free downloads are never money events.
    free = client.post("/packs", json={
        "industry": "technology", "title": "Free Notes", "price": 0,
        "publisher_owner_id": "creator-1",
        "items": [{"title": "n", "content": "c"}]}).json()["id"]
    client.headers["authorization"] = buyer_tok
    client.post(f"/packs/{free}/install", json={"profile_id": buyer_pid})
    client.headers["authorization"] = seller_tok
    assert len(client.get(f"/profiles/{seller_pid}/earnings"
                          ).json()["entries"]) == 1


def test_license_fee_accrues_at_acquisition(client):
    pid, tok = _profile(client)
    client.headers["authorization"] = tok
    client.put(f"/profiles/{pid}/license",
               json={"kind": "consult", "price": 49.0,
                     "terms": "hourly consult"})
    buyer = client.post("/interactors", json={
        "display_name": "Buyer", "birthdate": "1990-01-01"}).json()
    r = client.post(f"/profiles/{pid}/license/acquire",
                    headers={"authorization": f"Bearer {buyer['token']}"})
    assert r.status_code == 201

    s = client.get(f"/profiles/{pid}/earnings").json()
    assert s["totals"]["by_kind"] == {"license_fee": 49.0}
    assert "consult license · Priya Raman" in s["entries"][0]["memo"]


def test_payout_sweeps_accrued_to_paid(client):
    pid, tok = _profile(client)
    client.headers["authorization"] = tok
    client.put(f"/profiles/{pid}/license", json={"kind": "consult",
                                                 "price": 20.0})
    for birthdate in ("1990-01-01", "1985-03-03"):
        buyer = client.post("/interactors", json={
            "display_name": "B", "birthdate": birthdate}).json()
        client.post(f"/profiles/{pid}/license/acquire",
                    headers={"authorization": f"Bearer {buyer['token']}"})

    receipt = client.post(f"/profiles/{pid}/earnings/payout")
    assert receipt.status_code == 201, receipt.text
    out = receipt.json()
    assert out["total"] == 40.0 and out["entries"] == 2

    s = client.get(f"/profiles/{pid}/earnings").json()
    assert s["totals"]["accrued"] == 0 and s["totals"]["paid"] == 40.0
    assert s["totals"]["lifetime"] == 40.0
    assert all(e["payout_id"] == out["payout_id"] for e in s["entries"])
    # An empty balance cannot be paid out.
    assert client.post(f"/profiles/{pid}/earnings/payout").status_code == 409


def test_rated_commerce_lands_in_the_same_ledger(client):
    pid, tok = _profile(client, owner="qrme-starter", name="Steward",
                        adult_mode=True)
    client.post("/packs/seed")
    buyer_pid, buyer_tok = _profile(client, owner="buyer-2", name="Ivy",
                                    adult_mode=True)
    client.headers["authorization"] = buyer_tok
    rated = next(p for p in client.get("/packs").json() if p["rated"])
    client.post(f"/packs/{rated['id']}/install",
                json={"profile_id": buyer_pid, "accept_price": True})

    client.headers["authorization"] = tok
    s = client.get(f"/profiles/{pid}/earnings").json()
    assert any(e["kind"] == "pack_sale" and e["amount"] == 6.99
               for e in s["entries"])


def test_registry_sales_accrue_to_the_registry(client):
    client.post("/packs/registries/llmmods/sync")
    buyer_pid, buyer_tok = _profile(client, owner="buyer-3", name="Sam")
    client.headers["authorization"] = buyer_tok
    speak = next(p for p in client.get("/packs").json()
                 if p["title"] == "Public Speaking Mod")
    client.post(f"/packs/{speak['id']}/install",
                json={"profile_id": buyer_pid, "accept_price": True})
    from qrme import ledger
    s = ledger.statement("llmmods")
    assert s["totals"]["accrued"] == 3.49


def test_earnings_are_owner_only(client, profile_id):
    r = client.get(f"/profiles/{profile_id}/earnings",
                   headers={"authorization": ""})
    assert r.status_code in (401, 403)
