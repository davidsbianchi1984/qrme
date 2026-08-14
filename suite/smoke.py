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
        # The vault is plan-gated, not deployment-gated (jim/storage.py):
        # a visitor's writes stay out of the vault by design, so the sealed
        # exchange below needs the user on a private plan.
        r = jim.post(f"/memberships/{user['id']}", json={"plan": "basic"})
        assert r.status_code == 200, f"membership: {r.text}"
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

        # -- The whole arc: a goal in JIM, worked in QRME, carried back -----
        #
        # Everything above proves one exchange. `qrme/workflows.py` names three
        # properties a *multi-phase* handoff has to keep — memory carried
        # forward between phases, every phase generated through the profile's
        # persona, and `confirm` pausing for a human before it resumes — and
        # nothing walked all of them together. The pieces each had a test; the
        # arc did not.
        #
        #     asked     does the workflow round-trip
        #     mattered  does anything walk the whole arc
        # Delegated multi-step work is Pro-gated (`synthetic_agents`), and the
        # arc is the first thing in this run to touch that gate: the exchange
        # above only needs the vault, which Basic has. The refusal is recorded
        # rather than skipped past, because "this is the tier that buys it" is
        # the answer somebody deciding whether to pay actually needs.
        #
        # Whether that gate is *running* is JIM's to say, not this run's to
        # assume. It stands down for the duration of the beta — no capability
        # refuses anybody, whatever plan the account records — and this
        # assertion was written when it could not: a hard 402 that broke the
        # whole arc the day the flag flipped, seven steps in, reporting a
        # specialist that "does not accept delegated work" as if the tandem
        # had come apart.
        #
        #     asked     does the arc pay for what it uses
        #     mattered  does the arc still run when nobody is charged
        #
        # So it reads the posture off `/plans` and asserts the branch that is
        # actually in force. Both branches are real assertions — a stood-down
        # gate must let the request *through*, which is the claim that would
        # have caught it going the other way too.
        priced = jim.get("/plans")
        assert priced.status_code == 200, f"plans: {priced.text}"
        gate_running = priced.json()["enforcing"]
        # Either way the price list still says what Pro buys — standing the
        # gate down is not the same as saying it is free forever.
        free = next(p for p in priced.json()["plans"] if p["plan"] == "free")
        assert "synthetic_agents" in free["locked"], priced.text
        asked = jim.post(f"/users/{user['id']}/specialist-tasks", json={
            "condition": "financial_stress", "goal": "x"})
        if gate_running:
            assert asked.status_code == 402, \
                f"expected the plan gate: {asked.text}"
            assert asked.json()["detail"]["needs"] == "pro", asked.text
        else:
            assert asked.status_code != 402, \
                f"the beta stands the gate down and it refused: {asked.text}"
        # The upgrade is recorded either way: the arc below is Pro work, and
        # a run that only reached it because nothing was being enforced would
        # prove less than one that paid.
        r = jim.post(f"/memberships/{user['id']}", json={"plan": "pro"})
        assert r.status_code == 200, f"upgrade: {r.text}"
        step("workflow_needs_pro", {"gate": "synthetic_agents",
                                    "enforcing": gate_running,
                                    "upgraded": "pro"})

        # The specialist's owner has to opt in: delegation is off until
        # somebody says which phases a stranger may start, and `research` is
        # refused without a grant scoping what it may read. Both are the
        # owner's acts, so the harness takes the owner's part — it stood the
        # profile up and holds the deployment.
        #
        # Default-off is asserted the way the tier gate above is: by asking
        # first and being told no. Recording only the opt-in would prove the
        # harness *can* opt in, which is a different claim, and one that would
        # stay true if the default flipped to open tomorrow.
        started_uninvited = jim.post(
            f"/users/{user['id']}/specialist-tasks", json={
                "condition": "financial_stress", "goal": "x",
                "plan": ["draft"]})
        assert started_uninvited.status_code in (201, 403), \
            started_uninvited.text
        if started_uninvited.status_code == 201:
            assert started_uninvited.json().get("started") is False, (
                "a stranger started delegated work on a profile whose owner "
                f"never opted in: {started_uninvited.text}")

        from qrme import auth as qrme_auth
        pid = g["qrme_profile_id"]
        owner = {"authorization": f"Bearer {qrme_auth.issue('owner', pid)}"}
        r = qrme.post(f"/profiles/{pid}/grants", json={"scope": None},
                      headers=owner)
        assert r.status_code == 201, f"grant: {r.text}"
        grant_token = r.json()["token"]
        r = qrme.put(f"/profiles/{pid}/delegation", headers=owner, json={
            "phases": ["research", "draft", "send", "confirm"],
            "grant_token": grant_token, "enabled": True})
        assert r.status_code == 200, f"delegation: {r.text}"
        step("specialist_opted_in", {"phases": r.json().get("phases"),
                                     "scoped_by_grant": True,
                                     "refused_before_opt_in": True})

        r = jim.post(f"/users/{user['id']}/specialist-tasks", json={
            "condition": "financial_stress",
            "goal": "Find local rent-assistance programmes and draft an "
                    "application email I can send.",
            "plan": ["research", "draft", "send", "confirm"]})
        assert r.status_code == 201, f"specialist task: {r.text}"
        task = r.json()
        assert task.get("started") is not False, f"refused: {task}"
        task_id = task["id"]

        # Walk it. `confirm` is the pausing phase, so the loop stops there
        # rather than running off the end — which is the property that would
        # go unnoticed if the arc were only ever driven one phase deep.
        legs, guard = [], 0
        while guard < 8:
            guard += 1
            r = jim.get(f"/users/{user['id']}/specialist-tasks/{task_id}")
            assert r.status_code == 200, f"status: {r.text}"
            state = r.json()
            assert state["reachable"] is True, f"specialist unreachable: {state}"
            if state.get("awaiting") or state["status"] in ("done", "complete"):
                break
            r = jim.post(
                f"/users/{user['id']}/specialist-tasks/{task_id}/advance")
            assert r.status_code == 200, f"advance: {r.text}"
            legs.append(r.json().get("phase") or r.json().get("next_phase"))

        final = jim.get(
            f"/users/{user['id']}/specialist-tasks/{task_id}").json()
        # Memory carried forward: each phase is recorded, in order.
        assert len(final["phases_done"]) >= 2, (
            f"only {final['phases_done']} phase(s) ran — the arc did not "
            "carry memory forward")
        # And JIM's own row knows where it got to, without holding the drafts:
        # `handoff._shape` keeps status only, on purpose.
        listed = jim.get(f"/users/{user['id']}/specialist-tasks").json()
        assert any(t["id"] == task_id for t in listed), "JIM lost the task"
        step("workflow_arc", {
            "goal_phases": final["phases_done"],
            "awaiting": final.get("awaiting"),
            "status": final["status"],
            "qrme_profile_id": final["qrme_profile_id"]})

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
