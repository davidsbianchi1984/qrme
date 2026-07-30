"""The Cloud Model Gateway HTTP API — the contract in docs/cloud-model.md.

    POST /v1/generate              inference on the hosted tier
    GET  /v1/model                 what this gateway serves
    POST /v1/contributions         anonymized contribution intake  → 202
    POST /v1/contributions/revoke  delete previously contributed items
    POST /v1/problems              content-free error reports       → 202
    GET  /v1/problems              what is breaking, worst first

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
from fastapi.middleware.cors import CORSMiddleware

from . import model, problems, screening, store

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


def _readers() -> set[str]:
    """Caller names allowed to read the error aggregate.

    Unset means the local developer and nobody else — the same fail-closed
    default as the token check above, and for the same reason: an operator who
    has not decided yet should get "no", not "everyone".
    """
    raw = os.environ.get("CLOUDGW_PROBLEM_READERS", "").strip()
    return {n.strip() for n in raw.split(",") if n.strip()} or {"local-dev"}


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


def create_app(provider=None, vault=None, aggregate=None) -> FastAPI:
    app = FastAPI(title="Cloud Model Gateway", version="0.1.0")

    # Cross-origin, from any origin, without credentials.
    #
    # Not laziness, and not a weakening: the callers are desktop consoles. An
    # Electron renderer's origin is `null` (it loads from file://) and a dev
    # console's is whatever port Vite picked, so there is no allowlist that
    # could be written and stay true. Without this the browser's preflight
    # gets a 405 and every report fails — silently, since the sender swallows
    # failures, which is the worst way for a feature to be dead.
    #
    # What CORS actually protects is *ambient* authority: a hostile page using
    # a session cookie the browser attaches for you. There is none here. Every
    # endpoint needs a bearer token presented explicitly, and
    # `allow_credentials=False` keeps it that way — a page that already has
    # the token could call this from a server anyway, and one that does not
    # gains nothing.
    app.add_middleware(
        CORSMiddleware, allow_origins=["*"], allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"], allow_headers=["*"])

    app.state.provider = provider or model.provider_from_env()
    app.state.vault = vault if vault is not None else store.vault_from_env()
    app.state.problems = (aggregate if aggregate is not None
                          else problems.aggregate_from_env())

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok",
                "model": app.state.provider.name,
                "intake": app.state.vault.describe(),
                "problems": app.state.problems.describe()}

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

    @app.post("/v1/problems", status_code=202)
    async def report_problems(request: Request,
                              caller: str = Depends(_caller)) -> dict:
        """What broke, from consoles that have a collector configured.

        Accepted or refused whole. A partial accept would leave the sender
        believing its redaction is fine while the gateway silently binned the
        half that proved otherwise — see `problems.py` for why that matters
        more here than anywhere else on this gateway.
        """
        try:
            payload = problems.screen(await request.json())
        except problems.Rejected as exc:
            raise HTTPException(422, str(exc)) from exc
        folded = app.state.problems.add(payload)
        return {"accepted": True, "problems": len(payload["problems"]),
                "failures": folded}

    @app.get("/v1/problems")
    def list_problems(caller: str = Depends(_caller)) -> dict:
        """The aggregate, worst first — for whoever is fixing the bugs.

        Behind a *narrower* gate than the intake, which is the whole reason
        this is not one permission. The token that posts reports is compiled
        into every installer, so it is public the moment the first user
        downloads one; treating "may report" and "may read the report" as the
        same right would publish a live map of every route that fails on every
        version to anyone who unzips an app.

        Writing is safe to hand out because a wrong write costs a wrong
        counter. Reading is not, so it stays with named callers.
        """
        if caller not in _readers():
            raise HTTPException(
                403, "this token may post error reports but not read them; "
                     "add its name to CLOUDGW_PROBLEM_READERS to change that")
        return {"rows": app.state.problems.rows()}

    return app


app = create_app()
