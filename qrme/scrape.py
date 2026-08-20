"""Going to the imported link, instead of waiting for a paste.

## The finding

A `collect` connection has always known the account it points at — platform
and handle, enough to build the public URL — and has never once visited it.
`POST /social/{cid}/collect` stores whatever the owner pastes into the box,
which means the door named *pull the account's content in* was in truth
*retype the account's content in*. A profile grown from someone's real
footprint was being grown from someone's patience.

    asked     can collected content enter the profile
    mattered  can the connection fetch it from the address it was given

## What this module is

The fetch half: given the public URL a connection already implies, get the
page and reduce it to the words a person would read there — the title, the
bio line the platform puts in its metadata, and the visible text, capped.
The route that calls this stores the result as an ordinary ``social_post``
source item (sealed into the PDI vault when one is configured), exactly like
a pasted item, with the URL and the fetch time written into the content so
the provenance travels with the words.

## What it refuses

* **Offline deployments do not fetch.** ``offline.enabled()`` is the same
  switch every other outbound path honours; a vault that promises nothing
  leaves this machine cannot quietly open sockets because a button was
  pressed. The refusal says so instead of timing out.
* **A connection without a handle has no address.** The summon-page fallback
  the beacons use is *our* page; fetching it would teach the profile its own
  reflection. 400, with the fix in the sentence.
* **Only public pages, as a browser sees them.** No credentials, no cookies,
  no API tokens — this reads what anyone on earth could read at that URL.
  Platforms that render nothing without JavaScript yield their metadata
  (title and description), which is still the account's own words.
"""

from __future__ import annotations

import html as _html
import json
import os
import re
import urllib.request

from . import offline

#: Size cap on what is read from the wire. A profile page that a person
#: reads is kilobytes of words; half a megabyte is generous for markup.
_MAX_BYTES = 512 * 1024

#: What is kept of the visible text. Source items are training material,
#: not archives; the persona budget renders items whole.
_MAX_TEXT = 4000

_TIMEOUT = 10.0

#: What is kept of a *rendered* reading. Rendered pages are the point —
#: a console's whole surface — so the cap is generous next to _MAX_TEXT,
#: and the distiller downstream still reduces it to one digest.
_MAX_RENDERED = 20000


#: URL suffixes that name a recording rather than a page — the canonical
#: list; the lookout reads it from here. Deduced from the path alone
#: (query stripped): a page that merely contains a player is still a page.
_MEDIA_SUFFIXES = (".mp3", ".mp4", ".m4a", ".wav", ".ogg", ".webm", ".mov",
                   ".mkv", ".flac", ".aac", ".opus")


def is_recording(url: str) -> bool:
    path = url.split("?", 1)[0].split("#", 1)[0].lower()
    return path.endswith(_MEDIA_SUFFIXES)


def fetch_transcribed(url: str, on_behalf_of: str | None = None) -> dict | None:
    """The words said in a recording, from the stack's transcription
    sidecar (``QRME_EARS_URL``) — or None, so the caller can decide what
    honesty looks like without ears. For the briefcase that is *held, not
    read*: unlike a page, where the shell the server sends is still the
    page's own text, the bytes of a recording are not its words, and no
    fallback fetch can stand in.

    None covers every kind of missing ears the same way: no sidecar
    configured, one that refused (it will not listen to private or
    stack-internal addresses), one that timed out, one that heard no
    speech. The offline gate vets the target before anything is asked —
    the target is what leaves; the sidecar is stack infrastructure.
    """
    base = os.environ.get("QRME_EARS_URL", "").strip()
    if not base:
        return None
    offline.allow(url, "the transcribed fetch", on_behalf_of)
    req = urllib.request.Request(
        base.rstrip("/") + "/transcribe",
        data=json.dumps({"url": url}).encode("utf-8"),
        headers={"content-type": "application/json"}, method="POST")
    try:
        # Downloading a recording and transcribing it on CPU takes real
        # time — the generous timeout is the sidecar's own media cap
        # doing the bounding, not this line.
        with urllib.request.urlopen(req, timeout=300) as resp:
            out = json.loads(resp.read(_MAX_BYTES * 4)
                             .decode("utf-8", errors="replace"))
    except Exception:  # noqa: BLE001 — missing ears are the caller's decision
        return None
    text = (out.get("text") or "").strip()
    if not text:
        return None
    return {"text": text[:_MAX_RENDERED],
            "duration_seconds": out.get("duration_seconds"),
            "language": out.get("language")}


def transcribe_bytes(data: bytes, on_behalf_of: str | None = None) -> dict | None:
    """The words said in a recording already in hand — an upload — via
    the ears' bytes door, or None so the caller keeps the held-not-read
    posture. The gate sees the sidecar's own address: a stack-internal
    host passes even offline (the Ollama rule — nothing leaves the
    machine), the visit is witnessed against the profile the upload
    belongs to, and a deployment that points QRME_EARS_URL somewhere
    that *would* leave the host is refused like any other way out.
    """
    base = os.environ.get("QRME_EARS_URL", "").strip()
    if not base or not data:
        return None
    offline.allow(base, "the ears' bytes door", on_behalf_of)
    req = urllib.request.Request(
        base.rstrip("/") + "/transcribe-file", data=data,
        headers={"content-type": "application/octet-stream"},
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            out = json.loads(resp.read(_MAX_BYTES * 4)
                             .decode("utf-8", errors="replace"))
    except Exception:  # noqa: BLE001 — missing ears are the caller's decision
        return None
    text = (out.get("text") or "").strip()
    if not text:
        return None
    return {"text": text[:_MAX_RENDERED],
            "duration_seconds": out.get("duration_seconds"),
            "language": out.get("language")}


def fetch_rendered(url: str, on_behalf_of: str | None = None) -> dict | None:
    """The page as a person meets it, from the stack's rendering sidecar
    (``QRME_RENDERER_URL``) — or None, so the caller can fall back to
    :func:`fetch` and carry the reading it actually got.

    None covers every kind of missing eyes the same way: no sidecar
    configured, a sidecar that refused (it will not look at private or
    stack-internal addresses), one that timed out, one that answered
    empty. The offline gate vets the target before anything is asked —
    the target is what leaves; the sidecar is stack infrastructure.
    """
    base = os.environ.get("QRME_RENDERER_URL", "").strip()
    if not base:
        return None
    offline.allow(url, "the rendered page fetch", on_behalf_of)
    req = urllib.request.Request(
        base.rstrip("/") + "/render",
        data=json.dumps({"url": url}).encode("utf-8"),
        headers={"content-type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            out = json.loads(resp.read(_MAX_BYTES * 4)
                             .decode("utf-8", errors="replace"))
    except Exception:  # noqa: BLE001 — missing eyes are a fallback, not a crash
        return None
    text = (out.get("text") or "").strip()
    if not text:
        return None
    return {"title": (out.get("title") or "").strip() or None,
            "text": text[:_MAX_RENDERED]}


def fetch(url: str, on_behalf_of: str | None = None) -> str:
    """The page as a browser would receive it, capped and decoded leniently.

    The gate lives here, in the function that opens the socket, not only in
    the route above it — a second caller added tomorrow inherits the check
    instead of remembering it. The same argument now carries a second
    passenger: ``on_behalf_of`` is the profile this errand belongs to, and it
    is what lets the visit be recorded against somebody and what makes a
    stand-down on this host bind here rather than at the route.
    """
    offline.allow(url, "the profile-page fetch", on_behalf_of)
    req = urllib.request.Request(
        url, headers={"User-Agent": "QRME-profile-import/1.0"})
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        raw = resp.read(_MAX_BYTES)
    return raw.decode("utf-8", errors="replace")


_STRIP = re.compile(r"<(script|style|noscript)\b.*?</\1>", re.S | re.I)
_TAGS = re.compile(r"<[^>]+>")
_WS = re.compile(r"\s+")


def _meta(html: str, *names: str) -> str | None:
    """First matching <meta property/name=… content=…>, either attribute order."""
    for name in names:
        for pat in (
            r'<meta[^>]+(?:property|name)=["\']%s["\'][^>]+content=["\']([^"\']+)',
            r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\']%s["\']',
        ):
            m = re.search(pat % re.escape(name), html, re.I)
            if m:
                return _html.unescape(m.group(1)).strip()
    return None


def extract(html: str) -> dict:
    """{title, description, text} — the words a reader would take away."""
    title = _meta(html, "og:title", "twitter:title")
    if not title:
        m = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
        title = _html.unescape(m.group(1)).strip() if m else None
    description = _meta(html, "og:description", "twitter:description",
                        "description")
    body = _TAGS.sub(" ", _STRIP.sub(" ", html))
    text = _WS.sub(" ", _html.unescape(body)).strip()[:_MAX_TEXT]
    return {"title": title, "description": description, "text": text}


# What a platform's front door says instead of showing the profile. The
# phrases are checked against the page's *title*, because that is where a
# wall announces itself — "Log into Facebook", "Login • Instagram",
# "Sign Up | LinkedIn" — while a real profile page titles itself with the
# person. Kept deliberately short: a profile whose bio merely mentions
# signing in must not be refused over its own words.
_WALL = re.compile(
    r"\b(log ?in|log into|sign ?in|sign ?up|create an account"
    r"|join facebook)\b", re.I)


def wall(page: dict) -> bool:
    """True when the fetched page is a login wall, not the profile.

    The field report behind it: a Facebook import "succeeded" and what
    it stored — what the persona then quoted back in chat — was the
    login page, because that is all Facebook shows a signed-out
    visitor. A wall's words are the platform's, not the person's, and
    material that feeds a profile's training must never be them.
    """
    title = page.get("title") or ""
    return bool(_WALL.search(title))
