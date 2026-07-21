"""Suite gateway — the three products behind **one backend origin**.

QRME, JIM-mini, and PDI stay three independent apps (as the tandem architecture
intends); the gateway simply mounts each under a path prefix so the whole suite
is reachable at a single origin:

    /qrme/...     the QRME synthetic-profile API
    /jim/...      the JIM-mini guardian API
    /pdi/...      the PDI vault API

and adds a thin suite layer:

    GET  /suite/health    which products are mounted, and live
    POST /suite/session   unified sign-on — provision one identity across all
                          three in a single call, returning the per-product
                          tokens the suite launcher then uses.

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


async def _call(app: FastAPI, method: str, path: str, **kw) -> httpx.Response:
    """Call a mounted app in-process (shared DB, no network)."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://suite") as c:
        return await c.request(method, path, **kw)


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

    for prefix, app in _MOUNTS.items():
        gw.mount(f"/{prefix}", app)

    return gw


app = create_gateway()
