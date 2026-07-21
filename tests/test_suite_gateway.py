"""Suite gateway — one origin fronting QRME + JIM + PDI, with unified sign-on."""

import base64
import importlib.util
import os

import pytest
from fastapi.testclient import TestClient

# The suite gateway fronts all three products; these tests only run when the
# jim-mini and pdi packages are installed alongside qrme (the full-suite dev
# setup). In a qrme-only checkout they're skipped, not failed.
_missing = [m for m in ("jim.api", "pdi.api") if importlib.util.find_spec(m) is None]
pytestmark = pytest.mark.skipif(
    bool(_missing), reason=f"suite packages not installed: {_missing}")


@pytest.fixture()
def gateway(tmp_path, monkeypatch):
    # Isolated DBs for each product; deterministic PDI key; stub LLMs.
    monkeypatch.setenv("QRME_DB", str(tmp_path / "qrme.db"))
    monkeypatch.setenv("JIM_DB", str(tmp_path / "jim.db"))
    monkeypatch.setenv("PDI_DB", str(tmp_path / "pdi.db"))
    monkeypatch.setenv("QRME_LLM", "stub")
    monkeypatch.setenv("JIM_LLM", "stub")
    monkeypatch.setenv("PDI_MASTER_KEY", base64.b64encode(os.urandom(32)).decode())
    for mod in ("qrme.db", "jim.db", "pdi.db"):
        try:
            __import__(mod, fromlist=["reset"]).reset()
        except Exception:
            pass
    from suite.gateway import create_gateway
    with TestClient(create_gateway()) as c:
        yield c


def test_one_origin_mounts_all_three(gateway):
    h = gateway.get("/suite/health").json()
    assert h["origin"] == "one"
    assert set(h["products"]) == {"qrme", "jim", "pdi"}
    assert all(p["live"] for p in h["products"].values())
    # Each product answers under its own prefix on the single origin.
    assert gateway.get("/pdi/health").json()["status"] == "ok"
    assert gateway.get("/jim/health").json()["status"] == "ok"
    assert gateway.get("/qrme/openapi.json").status_code == 200


def test_unified_signon_provisions_all_three(gateway):
    r = gateway.post("/suite/session", json={
        "display_name": "Dana", "birthdate": "1984-06-01"})
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["identity"] == "Dana"
    p = body["products"]
    assert p["qrme"]["owner_token"] and p["qrme"]["profile_id"].startswith("prf_")
    assert p["jim"]["user_token"] and p["jim"]["user_id"].startswith("usr_")
    assert p["pdi"]["tenant_token"] and p["pdi"]["tenant_id"].startswith("ten_")

    # The provisioned identity works through the single origin, per product:
    # QRME — the profile exists and is chattable.
    prof = gateway.get(f"/qrme/profiles/{p['qrme']['profile_id']}")
    assert prof.status_code == 200 and prof.json()["display_name"] == "Dana"
    chat = gateway.post(f"/qrme/profiles/{p['qrme']['profile_id']}/chat", json={
        "interactor_id": p["qrme"]["interactor_id"], "message": "hello"})
    assert chat.status_code == 200

    # JIM — the enrolled user can be monitored with the returned token.
    mon = gateway.post(f"/jim/monitor/{p['jim']['user_id']}",
                       headers={"authorization": f"Bearer {p['jim']['user_token']}"},
                       json={"heart_rate": 110, "stress_level": 0.8})
    assert mon.status_code == 200 and mon.json()["detected"] is True

    # PDI — the tenant can seal a record with the returned token.
    rec = gateway.put("/pdi/records",
                      headers={"authorization": f"Bearer {p['pdi']['tenant_token']}"},
                      json={"key": "suite/hello", "value": "secret"})
    assert rec.status_code == 200 and rec.json()["stored"] is True


def test_session_is_one_call_across_products(gateway):
    # A single POST creates identity everywhere — the "unified login".
    before = gateway.get("/suite/health").json()
    assert before["products"]["pdi"]["live"]
    gateway.post("/suite/session", json={"display_name": "Sam", "birthdate": "1990-02-02"})
    # PDI now has the suite tenant.
    ret = gateway.get("/pdi/retention").json()
    names = [t["name"] for t in ret["record_retention"]]
    assert "suite:Sam" in names
