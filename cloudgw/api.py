"""The Cloud Model Gateway HTTP API — the contract in docs/cloud-model.md.

    POST /v1/generate              inference on the hosted tier
    GET  /v1/model                 what this gateway serves
    POST /v1/contributions         anonymized contribution intake  → 202
    POST /v1/contributions/revoke  delete previously contributed items

Authentication is a bearer token per contributing deployment
(``CLOUDGW_TOKENS``). It fails closed the same way PDI's admin surface does:
no tokens configured is development mode, honoured only for callers on this
machine. A gateway reachable from the internet with open inference is
somebody else's model bill and an unattributable corpus.
"""

from __future__ import annotations

import os
import secrets

from fastapi import Depends, FastAPI, Header, HTTPException, Request

from . import model, screening, store

# Starlette's in-process sentinel names no socket, so no network peer can
# present it.
_LOCAL_CALLERS = {"127.0.0.1", "::1", "localhost", "testclient"}


def _tokens() -> dict[str, str]:
    """``name:token`` pairs, so the audit trail records *which* deployment
    contributed rather than only that something did."""
    raw = os.environ.get("CLOUDGW_TOKENS", "").strip()
    out = {}
    for pair in raw.split(","):
        if ":" in pair:
            name, _, token = pair.partition(":")
            out[token.strip()] = name.strip()
    return out


def _caller(request: Request, authorization: str = Header(default="")) -> str:
    """Which deployment is calling. Returns its name for attribution."""
    configured = _tokens()
    if not configured:
        host = request.client.host if request.client else ""
        if host in _LOCAL_CALLERS:
            return "local-dev"
        raise HTTPException(
            503, "this gateway is reachable beyond localhost but has no "
                 "CLOUDGW_TOKENS configured — inference and intake stay "
                 "closed until they are (see docs/cloud-model.md)")
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "gateway bearer token required")
    presented = authorization[len("Bearer "):]
    for token, name in configured.items():
        # Constant-time, and over every configured token, so a wrong token
        # cannot be recovered by timing which comparison returned early.
        if secrets.compare_digest(presented, token):
            return name
    raise HTTPException(403, "invalid gateway token")


def create_app(provider=None, vault=None) -> FastAPI:
    app = FastAPI(title="Cloud Model Gateway", version="0.1.0")
    app.state.provider = provider or model.provider_from_env()
    app.state.vault = vault if vault is not None else store.vault_from_env()

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok",
                "model": app.state.provider.name,
                "intake": app.state.vault.describe()}

    @app.get("/v1/model")
    def model_info(_: str = Depends(_caller)) -> dict:
        """What this gateway serves. Clients call it to show users which model
        is answering — so it must name the real one, not a marketing tier."""
        return {"model": app.state.provider.name,
                "tier": app.state.provider.tier}

    @app.post("/v1/generate")
    async def generate(request: Request, caller: str = Depends(_caller)) -> dict:
        body = await request.json()
        system, messages = body.get("system", ""), body.get("messages") or []
        if not messages:
            raise HTTPException(422, "messages must not be empty")
        try:
            content = app.state.provider.generate(system, messages)
        except Exception as exc:
            # The client falls back to its local provider on any failure, so
            # 503 here is a routine outcome, not an incident. Say what broke.
            raise HTTPException(503, f"upstream model unavailable: {exc}") from exc
        return {"content": content, "model": app.state.provider.name}

    @app.post("/v1/contributions", status_code=202)
    async def contribute(request: Request,
                         caller: str = Depends(_caller)) -> dict:
        payload = await request.json()
        try:
            screening.screen(payload)
        except screening.Rejected as exc:
            # 422, not a quiet sanitize: the contributing deployment has a bug
            # that is leaking identity, and it needs to know.
            raise HTTPException(422, str(exc)) from exc
        stored = app.state.vault.put(payload["source"], payload["ref"],
                                     {**payload, "contributed_by": caller})
        return {"accepted": True, "ref": payload["ref"], "sealed": stored}

    @app.post("/v1/contributions/revoke")
    async def revoke(request: Request, caller: str = Depends(_caller)) -> dict:
        """Delete contributed items by ref.

        The refs carry no identity — only the contributor's own log maps them
        back — so a user withdrawing consent never has to identify themselves
        to the gateway to be forgotten by it.
        """
        refs = (await request.json()).get("refs") or []
        deleted = app.state.vault.delete(refs)
        return {"requested": len(refs), "deleted": deleted}

    return app


app = create_app()
