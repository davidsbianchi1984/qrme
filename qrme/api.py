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

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from . import avatars as avatar_assets
from . import i18n, llm, mobile, offline, tiers
from . import terms as terms_mod
from .cloud import CloudModelClient
from .pdi_client import PDIClient
from .routers import (accounts as account_routes,
                      apps, assistant, audience, avatars, commerce,
                      community, connections,
                      desks, displays, dock, earnings, exchange, feedback,
                      friends,
                      gamelobby, gaming,
                      governance,
                      identity, intelligence, interaction, licensing, models,
                      organizations as organization_routes,
                      overlays as overlay_routes, packs, pages, placemic,
                      frontpage, profiles, research, revisions, robots,
                      sharing, signatures,
                      social, steering,
                      summon, tiers as tier_routes, tutorial,
                      viewfinder as viewfinder_routes, wall,
                      watch, watchparty, watermarks)


def create_app(pdi_client: PDIClient | None = None,
               cloud_client: CloudModelClient | None = None) -> FastAPI:
    # The membership gate is an application-wide dependency rather than a call
    # at the top of each paid handler. One table, one chokepoint: a capability
    # cannot be added to the product and forgotten at one of its routes,
    # because no route opts in. See qrme/tiers.py for the table and for why
    # browsing stays open.
    app = FastAPI(title="QRME", version="0.30.4",
                  dependencies=[Depends(tiers.gate)])

    @app.get("/terms")
    def terms() -> dict:
        """The Terms of Service every client displays at the gateway:
        version, key points, and where the full text lives. Acceptance is
        recorded (version + timestamp) on profile creation."""
        return {"version": terms_mod.TERMS_VERSION,
                "key_points": terms_mod.KEY_POINTS,
                "document": terms_mod.DOCUMENT}

    @app.get("/health")
    def health() -> dict:
        """Service liveness, sibling-style: which tandems are configured.
        (JIM-mini and PDI always had one; QRME's front-ends probed
        /openapi.json instead — now they don't have to.)"""
        # The version is here so a desktop shell can tell whether the backend
        # answering the port is its own. A stale backend from an older
        # install answers /health perfectly well and then serves an older
        # API — which is how a user who installed three upgrades kept
        # meeting the first version's signup.
        return {"status": "ok", "version": app.version,
                "pdi": app.state.pdi is not None,
                "cloud": app.state.cloud is not None,
                "offline": offline.enabled(),
                "console": mobile.console_dir() is not None}

    # -- run it from your phone ---------------------------------------------

    @app.get("/pair")
    def pair(request: Request) -> dict:
        """How to open the studio on a phone: the console's URL on this
        local network, ready to type or scan. Same Wi-Fi, no app store."""
        return mobile.pairing(port=request.url.port or 8000)

    @app.get("/pair/qr.svg")
    def pair_qr(request: Request) -> Response:
        """The console URL as a QR code — point the phone's camera at it."""
        import io

        import segno
        buf = io.BytesIO()
        url = mobile.pairing(port=request.url.port or 8000)["console_url"]
        segno.make(url, error="q").save(
            buf, kind="svg", scale=8, border=2,
            dark="#0d0a20", light="#ffffff")
        return Response(content=buf.getvalue(), media_type="image/svg+xml")

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
    app.include_router(frontpage.router)
    app.include_router(interaction.router)
    app.include_router(intelligence.router)
    app.include_router(connections.router)
    app.include_router(friends.router)
    app.include_router(identity.router)
    app.include_router(placemic.router)
    app.include_router(overlay_routes.router)
    app.include_router(gamelobby.router)
    app.include_router(displays.router)
    app.include_router(tutorial.router)
    app.include_router(dock.router)
    app.include_router(tier_routes.router)
    app.include_router(viewfinder_routes.router)
    app.include_router(pages.router)
    app.include_router(wall.router)
    app.include_router(exchange.router)
    app.include_router(watchparty.router)
    app.include_router(sharing.router)
    app.include_router(revisions.router)
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
    app.include_router(organization_routes.router)
    app.include_router(watch.router)
    app.include_router(watermarks.router)
    app.include_router(avatars.router)
    app.include_router(steering.router)
    app.include_router(feedback.router)
    app.include_router(account_routes.router)
    app.include_router(gaming.router)
    app.include_router(models.router)
    app.include_router(robots.router)
    app.include_router(signatures.router)
    app.include_router(desks.router)
    # Last on purpose: these paths are generic (`/{kind}/{id}/like`), so every
    # concrete route above gets first refusal on a match.
    app.include_router(commerce.router)
    app.include_router(audience.router)

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

    # Every refusal, in the language of whoever is reading it.
    #
    # One handler rather than a call at the top of each route, for the reason
    # the membership gate is one dependency: a sentence cannot be added to the
    # product and forgotten at one of its raise sites, because no raise site
    # opts in. `qrme/i18n.py` carries the whole argument — whose language it
    # is, why the credential answers that and neither the path nor the browser
    # header does, and why `get_language` rather than `effective_language`.
    #
    # Untranslated sentences pass through as English, which is a visible gap
    # rather than a confident error, and is recorded in
    # `tests/refusals_untranslated.txt` rather than left to be noticed.
    @app.exception_handler(HTTPException)
    async def _refusal_in_the_readers_language(
            request: Request, refusal: HTTPException):
        language = i18n.refusal_language(request)
        if language != i18n.DEFAULT:
            refusal = HTTPException(
                refusal.status_code,
                i18n.localize_detail(refusal.detail, language),
                headers=refusal.headers)
        return await http_exception_handler(request, refusal)

    # The refusal FastAPI renders itself, which is the one a person meets most
    # often: a mistyped form is a 422. `RequestValidationError` is not an
    # `HTTPException`, so it went out past the handler above — in English, and
    # carrying pydantic's `input` key, which on a missing field is the entire
    # submitted body handed straight back to the caller. See `qrme/i18n.py`;
    # the sibling products returned a journal entry and a plaintext vault
    # value the same way.
    # `message` rides alongside because `detail` is a list, and a list is not
    # something any of this product's nine clients could show a person. The
    # consoles printed it as JSON, the Android shells did the same by
    # coercion, and the iOS and Windows shells asked for a string, got an
    # array, and fell back to "HTTP 422".
    #
    #     asked     is the refusal translated
    #     mattered  is the refusal a sentence
    #
    # `detail` keeps its shape: it is the FastAPI contract, it is what the
    # driven tests read, and a machine reading this API has every right to the
    # rows. The sentence carries nothing the rows do not — see
    # `qrme/i18n.py:validation_message`.
    @app.exception_handler(RequestValidationError)
    async def _rejected_input_stays_with_its_sender(
            request: Request, invalid: RequestValidationError):
        language = i18n.refusal_language(request)
        rows = i18n.validation_detail(invalid.errors(), language)
        return JSONResponse(
            status_code=422,
            content={"detail": rows,
                     "message": i18n.validation_message(rows, language)})

    # Bring-your-own model key: ``x-llm-api-key`` rides the request into a
    # context variable the provider layer reads — the caller's generations run
    # on their credential, which is never persisted and never logged. Requests
    # without one use the deployment's env key (the operator lending theirs).
    @app.middleware("http")
    async def _llm_request_key(request: Request, call_next):
        token = llm.set_request_key(request.headers.get("x-llm-api-key"))
        try:
            return await call_next(request)
        finally:
            llm.reset_request_key(token)

    # The starter portraits. Mounted unconditionally: unlike the studio, these
    # ship inside the package, so if the directory is missing something is
    # wrong with the install rather than merely unbuilt.
    _portraits = avatar_assets.portraits_dir()
    if _portraits.is_dir():
        from fastapi.staticfiles import StaticFiles
        app.mount(avatar_assets.ASSET_ROUTE,
                  StaticFiles(directory=str(_portraits)),
                  name="portraits")
    # Real photographs, served apart from the burned synthetic faces — see
    # avatars.PHOTO_ROUTE for why they are not the same kind of asset.
    _photos = avatar_assets.photos_dir()
    if _photos.is_dir():
        from fastapi.staticfiles import StaticFiles
        app.mount(avatar_assets.PHOTO_ROUTE,
                  StaticFiles(directory=str(_photos)), name="photos")
    # The anonymous silhouette — neither a burned portrait nor a photograph,
    # so a third mount rather than a file smuggled into either tree. See
    # avatars.FIGURE_ROUTE.
    _figures = avatar_assets.figures_dir()
    if _figures.is_dir():
        from fastapi.staticfiles import StaticFiles
        app.mount(avatar_assets.FIGURE_ROUTE,
                  StaticFiles(directory=str(_figures)), name="figures")

    # User uploads (qrme/media.py): the wall's photos and footage, served
    # read-only from the deployment's own media directory. Created up front
    # because StaticFiles refuses to mount a directory that is not there yet.
    from . import media as media_mod
    _media = media_mod.media_dir()
    _media.mkdir(parents=True, exist_ok=True)
    from fastapi.staticfiles import StaticFiles as _StaticFiles
    app.mount(media_mod.ROUTE, _StaticFiles(directory=str(_media)),
              name="media")

    # The studio itself, served from this API so a phone loads the UI and
    # calls the API on one origin (no CORS, nothing to configure). Mounted
    # last so it can never shadow an API route; absent until app/ is built.
    _console = mobile.console_dir()
    if _console is not None:
        from fastapi.staticfiles import StaticFiles
        app.mount("/app", StaticFiles(directory=str(_console), html=True),
                  name="console")

    # Heal what an upgrade left blank. Deployments seeded before the
    # portraits shipped sat on initials with 34 faces in the package, because
    # the repair lived behind a seed button nobody knows is a repair.
    # Blank-only and existing-profiles-only (see seed.repair), and a failed
    # repair must not keep the API from answering — the faces can wait,
    # the vault check-ins cannot.
    from . import seed as seed_mod
    try:
        seed_mod.repair()
    except Exception:
        pass

    return app


app = create_app()
