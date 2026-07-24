"""HTTP API — app factory wiring the routers and tandem clients.

Endpoints live in ``qrme/routers/``:

- ``profiles``     — owner CRUD, sources, surfaces, stats, marketplace,
                     export, erasure
- ``interaction``  — interactors, relationships, chat, compose, feedback,
                     memory, moderation queue
- ``intelligence`` — embeddings, specialists, grants/tasks, fine-tuning,
                     cloud model status
"""

from __future__ import annotations

import os

from fastapi import FastAPI

from . import offline
from .cloud import CloudModelClient
from .pdi_client import PDIClient
from .routers import (apps, assistant, community, connections, earnings,
                      governance, intelligence, interaction, licensing,
                      models, packs, profiles, research, robots, social,
                      summon, watch)


def create_app(pdi_client: PDIClient | None = None,
               cloud_client: CloudModelClient | None = None) -> FastAPI:
    app = FastAPI(title="QRME", version="0.1.0")

    # PDI tandem: profile source material is sealed in the encrypted vault
    # when configured (QRME_PDI_URL + QRME_PDI_TOKEN, or an injected client).
    if pdi_client is None and os.environ.get("QRME_PDI_URL"):
        pdi_client = PDIClient(token=os.environ.get("QRME_PDI_TOKEN", ""),
                               base_url=os.environ["QRME_PDI_URL"])
    app.state.pdi = pdi_client

    # Cloud Model Gateway: greater-model inference with local fallback, and
    # the opt-in contribution intake (QRME_CLOUD_URL + QRME_CLOUD_TOKEN).
    # Offline mode refuses the cloud outright — even an injected client — so no
    # request can reach an external host.
    if cloud_client is None and os.environ.get("QRME_CLOUD_URL"):
        cloud_client = CloudModelClient(
            token=os.environ.get("QRME_CLOUD_TOKEN", ""),
            base_url=os.environ["QRME_CLOUD_URL"])
    app.state.cloud = None if offline.enabled() else cloud_client

    app.include_router(profiles.router)
    app.include_router(interaction.router)
    app.include_router(intelligence.router)
    app.include_router(connections.router)
    app.include_router(social.router)
    app.include_router(apps.router)
    app.include_router(research.router)
    app.include_router(summon.router)
    app.include_router(community.router)
    app.include_router(assistant.router)
    app.include_router(governance.router)
    app.include_router(licensing.router)
    app.include_router(packs.router)
    app.include_router(earnings.router)
    app.include_router(watch.router)
    app.include_router(models.router)
    app.include_router(robots.router)

    # Optional CORS for a packaged desktop/mobile front-end that calls the API
    # from a different origin (e.g. the Electron app in app/). Off by default;
    # set QRME_CORS_ORIGINS to a comma-separated allowlist, or "*" for any.
    origins = os.environ.get("QRME_CORS_ORIGINS")
    if origins:
        from fastapi.middleware.cors import CORSMiddleware
        allow = ["*"] if origins.strip() == "*" else [
            o.strip() for o in origins.split(",") if o.strip()]
        app.add_middleware(
            CORSMiddleware, allow_origins=allow, allow_credentials=False,
            allow_methods=["*"], allow_headers=["*"])
    return app


app = create_app()
