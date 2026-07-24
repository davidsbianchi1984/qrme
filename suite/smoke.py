"""One-command cross-product smoke check.

    python -m suite.smoke

Boots all three products **in-process** (TestClient — no ports, no
network), seeds everything, wires the tandems, and drives one live
end-to-end exchange: a JIM user's financial-stress detection routed to the
QRME starter specialist @marcus_bell, with the exchange sealed in the PDI
vault and its provenance verified back through JIM's custody window.

Prints a JSON report of every step; exit code 0 means the whole suite is
green. Needs the ``jim-mini`` and ``pdi`` packages importable alongside
``qrme`` (the same requirement as the suite gateway); a missing sibling is
reported, not crashed on.
"""

from __future__ import annotations

import base64
import json
import os
import tempfile


def run(workdir: str | None = None) -> dict:
    steps: list[dict] = []

    def step(name: str, detail: dict) -> None:
        steps.append({"name": name, "ok": True, "detail": detail})

    try:
        from jim import db as jim_db
        from jim.api import create_app as create_jim
        from jim.pdi_client import PDIClient
        from jim.qrme_client import QRMEClient
        from pdi import db as pdi_db
        from pdi.api import create_app as create_pdi
    except ImportError as e:
        return {"ok": False, "steps": [
            {"name": "imports", "ok": False,
             "detail": f"missing sibling package: {e} — install jim-mini "
                       "and pdi alongside qrme"}]}

    from fastapi.testclient import TestClient

    from qrme import db as qrme_db
    from qrme.api import create_app as create_qrme

    workdir = workdir or tempfile.mkdtemp(prefix="suite-smoke-")
    os.environ["QRME_DB"] = os.path.join(workdir, "qrme.db")
    os.environ["QRME_LLM"] = "stub"
    os.environ["JIM_DB"] = os.path.join(workdir, "jim.db")
    os.environ["JIM_LLM"] = "stub"
    os.environ["PDI_DB"] = os.path.join(workdir, "pdi.db")
    os.environ.setdefault(
        "PDI_MASTER_KEY", base64.b64encode(os.urandom(32)).decode())
    for stale in ("JIM_QRME_URL", "JIM_PDI_URL", "JIM_PDI_TOKEN",
                  "PDI_ADMIN_TOKEN", "QRME_OFFLINE"):
        os.environ.pop(stale, None)
    qrme_db.reset(); jim_db.reset(); pdi_db.reset()

    clients: list = []
    try:
        pdi = TestClient(create_pdi()); pdi.__enter__(); clients.append(pdi)
        qrme = TestClient(create_qrme()); qrme.__enter__(); clients.append(qrme)

        # -- PDI: the vault comes up, seeds, and issues JIM its tenancy ----
        r = pdi.post("/seed")
        assert r.status_code == 201, f"pdi seed: {r.status_code} {r.text}"
        step("pdi_starter_vault", {"created": r.json()["created"],
                                   "tenant": r.json().get("name")})
        r = pdi.post("/tenants", json={"name": "jim-mini"})
        assert r.status_code == 201, f"pdi tenant: {r.status_code} {r.text}"
        tenant = r.json()
        step("pdi_jim_tenant", {"tenant_id": tenant["id"]})

        # -- QRME: marketplace, packs, and the federated registries --------
        r = qrme.post("/marketplace/seed")
        assert r.status_code == 201, f"qrme seed: {r.status_code} {r.text}"
        profiles = r.json()["created"]
        r = qrme.post("/packs/seed")
        assert r.status_code == 201, f"packs seed: {r.status_code} {r.text}"
        packs = r.json()["created"]
        synced = 0
        for key in ("robotmods", "llmmods"):
            rr = qrme.post(f"/packs/registries/{key}/sync")
            assert rr.status_code == 201, f"registry {key}: {rr.text}"
            synced += rr.json()["created"]
        step("qrme_seeded", {"profiles": profiles, "packs": packs,
                             "registry_packs": synced})

        # -- JIM: booted in tandem with both siblings ----------------------
        jim = TestClient(create_jim(
            qrme_client=QRMEClient(client=qrme),
            pdi_client=PDIClient(token=tenant["token"], client=pdi)))
        jim.__enter__(); clients.append(jim)
        health = jim.get("/health").json()
        assert health["tandem"] and health["pdi"], f"jim health: {health}"
        step("jim_tandem_up", health)

        r = jim.post("/specialists/seed")
        assert r.status_code == 201, f"specialists: {r.text}"
        r = jim.post("/specialists/seed/tandem")
        assert r.status_code == 201, f"tandem hookup: {r.text}"
        linked = r.json()["linked"]
        assert linked >= 5, f"expected 5+ tandem links, got {linked}"
        step("jim_specialists_wired", {"linked": linked})

        # -- The live exchange: JIM -> QRME persona -> sealed in PDI -------
        r = jim.post("/enroll", json={"display_name": "Suite Smoke",
                                      "birthdate": "1990-01-01",
                                      "terms_consent": True})
        assert r.status_code == 201, f"enroll: {r.text}"
        user = r.json()
        jim.headers["authorization"] = f"Bearer {user['user_token']}"
        r = jim.post(f"/monitor/{user['id']}",
                     json={"note": "I lost my job and can't pay rent"})
        assert r.status_code == 200, f"monitor: {r.text}"
        g = r.json()["guidance"]
        assert g["source"] == "tandem", f"expected tandem guidance: {g}"
        assert g["custody"]["vaulted"] is True, f"custody: {g.get('custody')}"
        step("end_to_end_tandem", {
            "condition": r.json()["condition"],
            "specialist": g.get("specialist"),
            "qrme_profile_id": g["qrme_profile_id"],
            "sealed_key": g["custody"]["pdi_key"]})

        # -- Provable custody: read the PDI provenance back through JIM ----
        r = jim.get(f"/custody/{user['id']}/provenance",
                    params={"key": g["custody"]["pdi_key"]})
        assert r.status_code == 200, f"provenance: {r.text}"
        prov = r.json()
        assert "JIM" in prov["origin"], f"origin: {prov['origin']}"
        assert prov["chain"]["intact"] is True, f"chain: {prov['chain']}"
        step("custody_provenance", {"origin": prov["origin"],
                                    "chain_intact": True})

        return {"ok": all(s["ok"] for s in steps), "steps": steps,
                "workdir": workdir}
    except Exception as e:  # report where it died, never crash the runner
        steps.append({"name": "aborted", "ok": False, "detail": repr(e)})
        return {"ok": False, "steps": steps, "workdir": workdir}
    finally:
        for c in reversed(clients):
            try:
                c.__exit__(None, None, None)
            except Exception:
                pass


if __name__ == "__main__":
    report = run()
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["ok"] else 1)
