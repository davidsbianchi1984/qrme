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
    if not text or looped(text):
        return None
    return {"text": text[:_MAX_RENDERED],
            "duration_seconds": out.get("duration_seconds"),
            "language": out.get("language")}


#: A transcript can come back as one short thing said over and over —
#: "Nghei, Nghei, Nghei, …" thirty times, "de typedas" ten times. That is
#: not somebody speaking. It is what a recogniser does when it is handed
#: near-silence or a loudspeaker playing back into the microphone: it
#: locks onto a fragment and repeats it until the audio runs out.
#:
#:     asked     did the ears answer
#:     mattered  did the ears answer with speech
#:
#: It matters more here than in most places because these words go into a
#: room *as that person's own message*. A wall of nonsense under somebody's
#: name is worse than no message at all, and every client — the console and
#: the three shells — reaches the ears through this module, so the check
#: lives here rather than in a screen.
_LOOP_MIN_WORDS = 8
_LOOP_SHARE = 0.5
_LOOP_MIN_PAIRS = 6
_LOOP_PAIR_SHARE = 0.4
_LOOP_TOKEN_MAX = 14
_LOOP_MIN_VOCAB_WORDS = 12
_LOOP_MIN_PAIR_HITS = 4
_LOOP_VOCAB = 0.5


def looped(text: str) -> bool:
    """True when a transcript is one fragment repeated rather than speech.

    Two shapes, because the recogniser produces both: a single word
    hammered (``Nghei, Nghei, Nghei…``) and a short phrase hammered
    (``de typedas 3 - 7 % de typedas 4 - 7 %…``), which no single-word
    count would catch.

    The thresholds are half and two-fifths rather than a tenth on
    purpose. Somebody really does say "no, no, no" and a name really does
    get repeated in a room; those land well under half. A recogniser
    stuck on a fragment lands well over it. Tokens longer than
    :data:`_LOOP_TOKEN_MAX` are exempt, because a word rare enough to be
    that long is not the shape this describes.
    """
    from collections import Counter
    words = [w for w in re.findall(r"[\w'%-]+", (text or "").lower()) if w]
    if len(words) >= _LOOP_MIN_WORDS:
        token, count = Counter(words).most_common(1)[0]
        if len(token) <= _LOOP_TOKEN_MAX and count / len(words) >= _LOOP_SHARE:
            return True
    pairs = [" ".join(words[i:i + 2]) for i in range(len(words) - 1)]
    if len(pairs) >= _LOOP_MIN_PAIRS:
        _pair, count = Counter(pairs).most_common(1)[0]
        if count / len(pairs) >= _LOOP_PAIR_SHARE:
            return True
        # The interleaved shape, which neither count above catches: a
        # phrase repeated with a changing number wedged into it —
        # "de typedas 3 - 7 % de typedas 4 - 7 % de typedas 5 - 8 %".
        # The phrase is only a fifth of the pairs because the fillers
        # dilute it, so the second half of the test is the vocabulary:
        # real speech of this length does not say the same few words
        # over and over.
        if (len(words) >= _LOOP_MIN_VOCAB_WORDS
                and count >= _LOOP_MIN_PAIR_HITS
                and len(set(words)) / len(words) < _LOOP_VOCAB):
            return True
    return False


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
    if not text or looped(text):
        return None
    return {"text": text[:_MAX_RENDERED],
            "duration_seconds": out.get("duration_seconds"),
            "language": out.get("language")}


#: How many frames of a viewing travel onward to a describer. The sidecar
#: sends up to eight; a caller that pays per image keeps the cap here.
MAX_FRAMES = 8


def _viewing_from(out: dict) -> dict | None:
    """The shared shape of both watch doors' answers: words when there was
    speech, frames when there were pictures, None when the sidecar's
    answer holds neither — the caller keeps the held-not-watched posture."""
    text = (out.get("text") or "").strip()
    frames = [f for f in (out.get("frames") or []) if f][:MAX_FRAMES]
    if not text and not frames:
        return None
    return {"text": text[:_MAX_RENDERED], "frames": frames,
            "duration_seconds": out.get("duration_seconds"),
            "language": out.get("language")}


def watch_url(url: str, on_behalf_of: str | None = None) -> dict | None:
    """The whole viewing of a recording — the words said in it AND a
    handful of frames showing what is on its screen — from the same ears
    sidecar, through its ``/watch`` door. Or None, covering every kind of
    missing machinery the same way the transcribed fetch does: no sidecar,
    a refusal, a timeout, a file that yields neither sound nor pictures."""
    base = os.environ.get("QRME_EARS_URL", "").strip()
    if not base:
        return None
    offline.allow(url, "the watched fetch", on_behalf_of)
    req = urllib.request.Request(
        base.rstrip("/") + "/watch",
        data=json.dumps({"url": url}).encode("utf-8"),
        headers={"content-type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            out = json.loads(resp.read(_MAX_BYTES * 32)
                             .decode("utf-8", errors="replace"))
    except Exception:  # noqa: BLE001 — missing eyes are the caller's decision
        return None
    return _viewing_from(out)


def watch_bytes(data: bytes, on_behalf_of: str | None = None) -> dict | None:
    """The same viewing for a recording already in hand — an upload —
    via the sidecar's ``/watch-file`` door, with the transcribe-bytes
    posture throughout: the gate sees the sidecar's own address, and a
    missing answer is None, never an invention."""
    base = os.environ.get("QRME_EARS_URL", "").strip()
    if not base or not data:
        return None
    offline.allow(base, "the eyes' bytes door", on_behalf_of)
    req = urllib.request.Request(
        base.rstrip("/") + "/watch-file", data=data,
        headers={"content-type": "application/octet-stream"},
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            out = json.loads(resp.read(_MAX_BYTES * 32)
                             .decode("utf-8", errors="replace"))
    except Exception:  # noqa: BLE001 — missing eyes are the caller's decision
        return None
    return _viewing_from(out)


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
