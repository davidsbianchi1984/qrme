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

from .cloud import CloudModelClient
from .pdi_client import PDIClient
from .routers import intelligence, interaction, profiles


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
    if cloud_client is None and os.environ.get("QRME_CLOUD_URL"):
        cloud_client = CloudModelClient(
            token=os.environ.get("QRME_CLOUD_TOKEN", ""),
            base_url=os.environ["QRME_CLOUD_URL"])
    app.state.cloud = cloud_client

    app.include_router(profiles.router)
    app.include_router(interaction.router)
    app.include_router(intelligence.router)
    return app


app = create_app()
