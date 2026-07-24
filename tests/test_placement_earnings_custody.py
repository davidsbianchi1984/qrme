"""Placement earnings & custody: a verified view through a venue placement
credits the creator's ledger, and when a PDI vault is configured every
rated-resolution event is sealed there — provable through PDI's audit chain,
the same custody standard as tandem exchanges."""

import json

import pytest
from fastapi.testclient import TestClient

from qrme import db
from qrme.rated import PLACEMENT_VIEW_RATE

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


def _adult_headers(client, birthdate="1990-01-01"):
    r = client.post("/interactors",
                    json={"display_name": "Viewer", "birthdate": birthdate})
    return {"authorization": f"Bearer {r.json()['token']}"}


def test_verified_venue_views_credit_the_ledger(client):
    pid = _rated_profile(client)
    placement = client.post(f"/profiles/{pid}/placements",
                            json={"venue": "onlyfans"}).json()
    adult = _adult_headers(client)

    # Two walled scans earn nothing; two verified views earn the rate each.
    for _ in range(2):
        client.get("/summon", params={"ref": placement["beacon_id"]},
                   headers={"authorization": ""})
    for _ in range(2):
        client.get("/summon", params={"ref": placement["beacon_id"]},
                   headers=adult)

    s = client.get(f"/profiles/{pid}/earnings").json()
    placements = [e for e in s["entries"] if e["kind"] == "placement"]
    assert len(placements) == 2
    assert all(e["ref"] == placement["placement_id"] for e in placements)
    assert "OnlyFans" in placements[0]["memo"]
    assert s["totals"]["by_kind"]["placement"] == round(
        2 * PLACEMENT_VIEW_RATE, 2)


def test_direct_handle_views_earn_nothing(client):
    pid = _rated_profile(client)
    client.post(f"/profiles/{pid}/placements", json={"venue": "onlyfans"})
    adult = _adult_headers(client)
    # A verified @handle summon has no venue behind it — no credit.
    client.get("/summon", params={"ref": "@velvet_ivy"}, headers=adult)
    s = client.get(f"/profiles/{pid}/earnings").json()
    assert "placement" not in s["totals"]["by_kind"]


class _Resp:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


class FakePDIHttp:
    def __init__(self):
        self.store = {}

    def put(self, path, json=None, headers=None):
        self.store[json["key"]] = json["value"]
        return _Resp(200, {"key": json["key"]})

    def get(self, path, headers=None):
        if path == "/audit/verify":
            return _Resp(200, {"intact": True})
        key = path[len("/records/"):]
        if key in self.store:
            return _Resp(200, {"key": key, "value": self.store[key]})
        return _Resp(404, {})

    def delete(self, path, headers=None):
        return _Resp(204 if self.store.pop(path[len("/records/"):], None)
                     is not None else 404, None)


@pytest.fixture()
def pdi_pair(tmp_path, monkeypatch):
    monkeypatch.setenv("QRME_DB", str(tmp_path / "custody-test.db"))
    monkeypatch.setenv("QRME_LLM", "stub")
    db.reset()
    from qrme.api import create_app
    from qrme.pdi_client import PDIClient

    fake = FakePDIHttp()
    with TestClient(create_app(
            pdi_client=PDIClient(token="pdi_test", client=fake))) as c:
        yield c, fake
    db.reset()


def test_rated_events_sealed_and_custody_provable(pdi_pair):
    client, fake = pdi_pair
    pid = _rated_profile(client)
    placement = client.post(f"/profiles/{pid}/placements",
                            json={"venue": "fansly"}).json()
    adult = _adult_headers(client)
    client.get("/summon", params={"ref": placement["beacon_id"]},
               headers={"authorization": ""})       # walled — sealed too
    client.get("/summon", params={"ref": placement["beacon_id"]},
               headers=adult)                        # verified — sealed

    custody = client.get(f"/profiles/{pid}/placements/custody").json()
    assert custody["count"] == 2
    assert custody["chain_intact"] is True
    kinds = {r["kind"] for r in custody["records"]}
    assert kinds == {"wall", "verified_view"}

    # The sealed payload in the vault carries the placement attribution.
    key = custody["records"][0]["pdi_key"]
    sealed = json.loads(fake.store[key])
    assert sealed["profile_id"] == pid
    assert sealed["placement_id"] == placement["placement_id"]
    assert sealed["venue"] == "fansly"


def test_custody_needs_a_vault_and_the_owner(client):
    pid = _rated_profile(client)
    # No vault configured on the plain client — custody can't be claimed.
    assert client.get(
        f"/profiles/{pid}/placements/custody").status_code == 409
    r = client.get(f"/profiles/{pid}/placements/custody",
                   headers={"authorization": ""})
    assert r.status_code in (401, 403)
