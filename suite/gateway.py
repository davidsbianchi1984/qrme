"""Suite gateway — the three products behind **one backend origin**.

QRME, JIM-mini, and PDI stay three independent apps (as the tandem architecture
intends); the gateway simply mounts each under a path prefix so the whole suite
is reachable at a single origin:

    /qrme/...     the QRME synthetic-profile API
    /jim/...      the JIM-mini guardian API
    /pdi/...      the PDI vault API

and adds a thin cross-cutting suite layer over the three:

    GET  /suite/health        which products are mounted, and live
    POST /suite/session       unified sign-on — provision one identity across
                              all three in a single call, returning the
                              per-product tokens the launcher then uses
    POST /suite/erase         right to be forgotten, suite-wide: fan the
                              deletion out to every product; return a receipt
    POST /suite/export        data portability: one bundle with the identity's
                              data from every product
    PUT  /suite/consent       centralized consent — sealed in the PDI vault and
                              enforced across products
    POST /suite/consent/read  read the authoritative consent document back
    POST /suite/usage         usage metering hooks for a suite-wide subscription

These fan out over the per-product tokens the caller already holds, so the
gateway stays stateless and stores no credential of its own.

Run:  SUITE_CORS_ORIGINS='*' uvicorn suite.gateway:app

The full suite needs all three packages importable (``pip install -e .`` here
plus the jim-mini and pdi packages). Any product that can't be imported is
simply skipped, so the gateway still comes up with whatever is present.
"""

from __future__ import annotations

import os

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Each product is its own FastAPI app; the same instance is both mounted (for
# the launcher's per-product calls) and used in-process by /suite/session.
_MOUNTS: dict[str, FastAPI] = {}


def _load(prefix: str, module: str) -> None:
    try:
        mod = __import__(module, fromlist=["create_app"])
        _MOUNTS[prefix] = mod.create_app()
    except Exception:  # noqa: BLE001 — a missing product must not break the rest
        pass


class SuiteEnroll(BaseModel):
    display_name: str
    birthdate: str            # ISO date, used for age checks in each product
    persona: str | None = None


class SuiteHandles(BaseModel):
    """The per-product identity + tokens returned by ``/suite/session`` — the
    caller (the launcher) holds these and hands them back so the suite layer
    can act on the identity across products without itself storing credentials.
    Each is the product's slice of the session's ``products`` map."""
    qrme: dict | None = None   # {profile_id, owner_token, interactor_id, ...}
    jim: dict | None = None    # {user_id, user_token}
    pdi: dict | None = None    # {tenant_id, tenant_token}


class SuiteConsent(SuiteHandles):
    """A consent update spanning all three products. The consent document is
    sealed in the identity's PDI vault (encrypted + audited); toggling
    ``cloud_contribution`` off also revokes it in QRME."""
    consent: dict = {}         # e.g. {cloud_contribution, proactive_outreach, ...}


CONSENT_KEY = "consent/suite"   # where the suite consent doc lives in the vault


async def _call(app: FastAPI, method: str, path: str, **kw) -> httpx.Response:
    """Call a mounted app in-process (shared DB, no network)."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://suite") as c:
        return await c.request(method, path, **kw)


def _bearer(token: str | None) -> dict:
    return {"authorization": f"Bearer {token}"} if token else {}


def create_gateway() -> FastAPI:
    _MOUNTS.clear()
    _load("qrme", "qrme.api")
    _load("jim", "jim.api")
    _load("pdi", "pdi.api")

    gw = FastAPI(title="Suite Gateway", version="0.1.0")

    origins = os.environ.get("SUITE_CORS_ORIGINS", "*")
    from fastapi.middleware.cors import CORSMiddleware
    allow = ["*"] if origins.strip() == "*" else [
        o.strip() for o in origins.split(",") if o.strip()]
    gw.add_middleware(CORSMiddleware, allow_origins=allow, allow_credentials=False,
                      allow_methods=["*"], allow_headers=["*"])

    @gw.get("/suite/health")
    async def suite_health() -> dict:
        products: dict[str, dict] = {}
        for name, app in _MOUNTS.items():
            live = True
            try:
                # QRME has no /health; its openapi.json proves it's up.
                probe = "/health" if name != "qrme" else "/openapi.json"
                r = await _call(app, "GET", probe)
                live = r.status_code == 200
            except Exception:  # noqa: BLE001
                live = False
            products[name] = {"mounted": True, "live": live, "base": f"/{name}"}
        return {"origin": "one", "products": products}

    @gw.post("/suite/session", status_code=201)
    async def suite_session(body: SuiteEnroll) -> dict:
        """Unified sign-on. Provisions the same person across every mounted
        product and returns the per-product identity + tokens. One login, one
        identity, three products."""
        out: dict[str, dict] = {}

        if "qrme" in _MOUNTS:
            app = _MOUNTS["qrme"]
            r = await _call(app, "POST", "/profiles", json={
                "owner_id": f"suite:{body.display_name}", "kind": "self",
                "display_name": body.display_name,
                "persona": body.persona or f"A digital version of {body.display_name}.",
                "verification": {"birthdate": body.birthdate},
                "purpose": "companion_coach"})
            if r.status_code >= 400:
                raise HTTPException(502, f"qrme provisioning failed: {r.text}")
            prof = r.json()
            i = await _call(app, "POST", "/interactors", json={
                "display_name": body.display_name, "birthdate": body.birthdate})
            inter = i.json()
            await _call(app, "PUT",
                        f"/profiles/{prof['id']}/relationships/{inter['id']}",
                        json={"relationship_type": "friend", "tone": "warm"},
                        headers={"authorization": f"Bearer {prof['owner_token']}"})
            out["qrme"] = {"profile_id": prof["id"], "owner_token": prof["owner_token"],
                           "interactor_id": inter["id"], "interactor_token": inter["token"]}

        if "jim" in _MOUNTS:
            r = await _call(_MOUNTS["jim"], "POST", "/enroll", json={
                "display_name": body.display_name, "birthdate": body.birthdate,
                "terms_consent": True})
            if r.status_code >= 400:
                raise HTTPException(502, f"jim provisioning failed: {r.text}")
            u = r.json()
            out["jim"] = {"user_id": u["id"], "user_token": u["user_token"]}

        if "pdi" in _MOUNTS:
            r = await _call(_MOUNTS["pdi"], "POST", "/tenants", json={
                "name": f"suite:{body.display_name}", "retention": "forever"})
            if r.status_code >= 400:
                raise HTTPException(502, f"pdi provisioning failed: {r.text}")
            t = r.json()
            out["pdi"] = {"tenant_id": t["id"], "tenant_token": t["token"]}

        return {"identity": body.display_name, "products": out}

    # -- cross-cutting suite control plane ----------------------------------
    # One identity spans three products, so the suite-level concerns — the
    # right to be forgotten, data portability, and consent — must span them
    # too. These fan out over the per-product tokens the caller already holds;
    # the gateway stays stateless and never stores a credential of its own.

    @gw.post("/suite/erase")
    async def suite_erase(body: SuiteHandles) -> dict:
        """Right to be forgotten, suite-wide. Deleting the identity here
        deletes it *everywhere*: the erasure is fanned out to every product the
        caller holds a handle for, and a per-product receipt is returned so a
        partial failure is visible rather than silently swallowed."""
        receipt: dict[str, dict] = {}

        if "qrme" in _MOUNTS and body.qrme:
            pid, tok = body.qrme.get("profile_id"), body.qrme.get("owner_token")
            r = await _call(_MOUNTS["qrme"], "DELETE", f"/profiles/{pid}",
                            headers=_bearer(tok))
            receipt["qrme"] = {"status": r.status_code, "ok": r.status_code < 400}

        if "jim" in _MOUNTS and body.jim:
            uid, tok = body.jim.get("user_id"), body.jim.get("user_token")
            r = await _call(_MOUNTS["jim"], "DELETE", f"/data/{uid}",
                            headers=_bearer(tok))
            receipt["jim"] = {"status": r.status_code, "ok": r.status_code < 400}

        if "pdi" in _MOUNTS and body.pdi:
            # Erase via the tenant's own write token — no admin needed: drop
            # every sealed record (consent doc included).
            tok = body.pdi.get("tenant_token")
            listing = await _call(_MOUNTS["pdi"], "GET", "/records",
                                  headers=_bearer(tok))
            keys = listing.json().get("keys", []) if listing.status_code < 400 else []
            erased = 0
            for k in keys:
                d = await _call(_MOUNTS["pdi"], "DELETE", f"/records/{k}",
                                headers=_bearer(tok))
                erased += 1 if d.status_code < 400 else 0
            receipt["pdi"] = {"status": listing.status_code,
                              "ok": listing.status_code < 400,
                              "records_erased": erased}

        return {"erased": receipt,
                "complete": bool(receipt) and all(v["ok"] for v in receipt.values())}

    @gw.post("/suite/export")
    async def suite_export(body: SuiteHandles) -> dict:
        """Data portability, suite-wide: one bundle with the identity's data
        from every product (QRME full export, JIM progress report, PDI
        ciphertext snapshot). GDPR Article 20 across the tandem."""
        bundle: dict[str, dict] = {}

        if "qrme" in _MOUNTS and body.qrme:
            pid, tok = body.qrme.get("profile_id"), body.qrme.get("owner_token")
            r = await _call(_MOUNTS["qrme"], "GET", f"/profiles/{pid}/export",
                            headers=_bearer(tok))
            bundle["qrme"] = r.json() if r.status_code < 400 else {"error": r.status_code}

        if "jim" in _MOUNTS and body.jim:
            uid, tok = body.jim.get("user_id"), body.jim.get("user_token")
            r = await _call(_MOUNTS["jim"], "GET", f"/report/{uid}",
                            headers=_bearer(tok))
            bundle["jim"] = r.json() if r.status_code < 400 else {"error": r.status_code}

        if "pdi" in _MOUNTS and body.pdi:
            tok = body.pdi.get("tenant_token")
            r = await _call(_MOUNTS["pdi"], "GET", "/snapshot", headers=_bearer(tok))
            bundle["pdi"] = r.json() if r.status_code < 400 else {"error": r.status_code}

        return {"format": "suite-export/v1", "products": bundle}

    @gw.put("/suite/consent")
    async def set_consent(body: SuiteConsent) -> dict:
        """Centralized consent spanning all three products. The consent
        document is sealed in the identity's PDI vault (encrypted at rest,
        recorded on the tamper-evident audit chain), so there is one
        authoritative, auditable record of what the person agreed to. Toggling
        ``cloud_contribution`` off also revokes it in QRME, so a withdrawn
        consent takes effect, not just gets logged."""
        import json as _json
        applied: dict[str, dict] = {}

        if "pdi" in _MOUNTS and body.pdi:
            tok = body.pdi.get("tenant_token")
            r = await _call(_MOUNTS["pdi"], "PUT", "/records", headers=_bearer(tok),
                            json={"key": CONSENT_KEY, "value": _json.dumps(body.consent)})
            applied["pdi"] = {"sealed": r.status_code < 400, "status": r.status_code}

        # Withdrawn cloud-contribution consent is enforced in QRME, not just stored.
        if (body.consent.get("cloud_contribution") is False
                and "qrme" in _MOUNTS and body.qrme):
            pid, tok = body.qrme.get("profile_id"), body.qrme.get("owner_token")
            r = await _call(_MOUNTS["qrme"], "POST",
                            f"/profiles/{pid}/cloud-contribution/revoke",
                            headers=_bearer(tok))
            applied["qrme"] = {"cloud_contribution_revoked": r.status_code < 400}

        return {"consent": body.consent, "applied": applied}

    @gw.post("/suite/consent/read")
    async def get_consent(body: SuiteHandles) -> dict:
        """Read the authoritative suite consent document back from the vault."""
        import json as _json
        if "pdi" not in _MOUNTS or not body.pdi:
            return {"consent": None, "note": "no vault handle supplied"}
        tok = body.pdi.get("tenant_token")
        r = await _call(_MOUNTS["pdi"], "GET", f"/records/{CONSENT_KEY}",
                        headers=_bearer(tok))
        if r.status_code >= 400:
            return {"consent": None, "note": "no consent recorded yet"}
        return {"consent": _json.loads(r.json()["value"])}

    @gw.post("/suite/usage")
    async def suite_usage(body: SuiteHandles) -> dict:
        """Usage metering hooks for a suite-wide subscription. Aggregates a
        few cheap counters per product into a single meter a billing system
        can read. (Metering only — actual rating/charging is out of v1.)"""
        meters: dict[str, dict] = {}

        if "qrme" in _MOUNTS and body.qrme:
            pid, tok = body.qrme.get("profile_id"), body.qrme.get("owner_token")
            r = await _call(_MOUNTS["qrme"], "GET", f"/profiles/{pid}/stats",
                            headers=_bearer(tok))
            meters["qrme"] = r.json() if r.status_code < 400 else {"error": r.status_code}

        if "jim" in _MOUNTS and body.jim:
            uid, tok = body.jim.get("user_id"), body.jim.get("user_token")
            r = await _call(_MOUNTS["jim"], "GET", f"/events/{uid}",
                            headers=_bearer(tok))
            events = r.json() if r.status_code < 400 else []
            meters["jim"] = {"events": len(events) if isinstance(events, list) else 0}

        if "pdi" in _MOUNTS and body.pdi:
            tok = body.pdi.get("tenant_token")
            r = await _call(_MOUNTS["pdi"], "GET", "/records", headers=_bearer(tok))
            keys = r.json().get("keys", []) if r.status_code < 400 else []
            meters["pdi"] = {"sealed_records": len(keys)}

        return {"meter": "suite-usage/v1", "note": "metering hooks only; "
                "rating/charging out of v1", "products": meters}

    for prefix, app in _MOUNTS.items():
        gw.mount(f"/{prefix}", app)

    return gw


app = create_gateway()
