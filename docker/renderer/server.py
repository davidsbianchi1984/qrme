"""The stack's eyes — one door: POST /render {"url"} answers the page's
text as a person meets it, rendered in a real browser.

The vault's ``fetch.render`` tool (pdi/renderer.py) asks here, named by
``PDI_RENDERER_URL``. The browser lives in this container so the vault's
own image stays lean, and so a page's scripts run at arm's length from the
process that holds the keys.

    asked     what does the page say
    mattered  what a person would see, not what the server sent first

**The eyes look outward only.** A rendering browser fetches far more than
the one address it was given — every script, image and beacon the page
names — so this sidecar refuses private, loopback, link-local and
stack-internal addresses twice: once for the target itself, and again for
every subresource the page tries to load, via route interception. A page
on the open web cannot use these eyes to peer at the stack behind them.

A browser per request is deliberate: slower, but every render starts from
nothing — no cookies, no storage, no session bleeding between tenants'
lookouts.
"""

import ipaddress
import socket
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException
from playwright.sync_api import sync_playwright
from pydantic import BaseModel

app = FastAPI()

# The stack's own names, and the ways a container reaches its host. A
# single-label name (no dot) is refused outright — the eyes have no
# business on anyone's intranet.
BLOCKED_NAMES = {"pdi", "qrme", "jim", "cloudgw", "bootstrap", "renderer",
                 "backup", "caddy", "localhost", "host.docker.internal"}
MAX_TEXT = 800_000


class RenderAsk(BaseModel):
    url: str


def _looks_inward(host: str | None) -> bool:
    h = (host or "").strip().lower().rstrip(".")
    if not h or h in BLOCKED_NAMES or "." not in h:
        return True
    try:
        return any(
            ipaddress.ip_address(info[4][0]).is_private
            or ipaddress.ip_address(info[4][0]).is_loopback
            or ipaddress.ip_address(info[4][0]).is_link_local
            for info in socket.getaddrinfo(h, None))
    except OSError:
        # A name that does not resolve renders nothing anyway; refusing it
        # here gives the caller one honest reason instead of a timeout.
        return True


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "eyes": True}


@app.post("/render")
def render(ask: RenderAsk) -> dict:
    parsed = urlparse(ask.url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(422, "render needs an http(s) url")
    if _looks_inward(parsed.hostname):
        raise HTTPException(403, "the eyes do not look inward: private and "
                                 "stack-internal addresses are refused")
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox"])
        try:
            page = browser.new_page()

            def gate(route):
                sub = urlparse(route.request.url)
                if (sub.scheme in ("http", "https")
                        and _looks_inward(sub.hostname)):
                    return route.abort()
                return route.continue_()

            page.route("**/*", gate)
            page.goto(ask.url, wait_until="networkidle", timeout=30_000)
            title = page.title()
            text = page.inner_text("body")
        finally:
            browser.close()
    return {"url": ask.url, "title": title, "text": text[:MAX_TEXT]}
