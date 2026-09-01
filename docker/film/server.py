"""The stack's camera — one door onto whichever video house is chosen.

``filming.py`` speaks one shape and only one, deliberately::

    POST /            {"provider", "prompt", "seconds", "shape"}
          -> {"video_url": ...}          a render that finished at once
          -> {"id": ...}                 a render that did not
    GET  /{id}        -> {"status": "pending" | "done" | "failed",
                          "video_url": ..., "detail": ...}

No vendor speaks that. Every one of them has its own body, its own
polling convention and its own name for the file that comes back. The
module said as much from the day it was written — "one adapter away from
any vendor whose own API differs" — and then the adapter was never
built, so ``QRME_FILM_URL`` had nothing on the box to point at and the
video road answered "no footage for this turn yet" forever.

    asked     why is seedance not rendering video
    mattered  there was nothing at the other end of the wire

This is that end of the wire. It is the third sidecar on the same
pattern as ``docker/ears`` and ``docker/forge``: a thin translator with
one job, so the product's image stays lean and a vendor swap is a change
in one file rather than through the whole codebase.

## Why fal, and why that is not a bet

fal hosts most of this shelf behind one queue API and one key, which
means ten providers cost one credential rather than ten. That is a
convenience, not a dependency: :data:`MODELS` is the whole of what is
vendor-specific, every row is overridable by environment variable, and
an operator whose model id has been renamed fixes it without a rebuild.

The lesson is already written down twice in this repository — Ready
Player Me closed in January 2026, Sora's API shuts in September — so
nothing here is allowed to be load-bearing. If fal goes the way of those
two, this file is replaced and nothing upstream of it changes.

## What it will not do

It does not hold the ceiling, count the spend or decide the length —
those are the product's decisions and they are made in ``filming.py``
before a request ever arrives here. This translates, and it refuses
loudly when it cannot.
"""

import os
import time
import urllib.error
import urllib.request
import json

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

#: Where fal's queue lives.
QUEUE = os.environ.get("FILM_QUEUE_URL", "https://queue.fal.run").rstrip("/")

#: Each provider's model id, and the whole of what is vendor-specific.
#:
#: Overridable one at a time — ``FILM_MODEL_VEO`` beats the row below it
#: — because a hosted model id is somebody else's string and they rename
#: them. An operator who finds a 404 in the logs edits their `.env`
#: rather than waiting for a release.
MODELS = {
    "veo": "fal-ai/veo3",
    "runway": "fal-ai/runway-gen3/turbo/text-to-video",
    "luma": "fal-ai/luma-dream-machine",
    "pika": "fal-ai/pika/v2/turbo/text-to-video",
    "moonvalley": "fal-ai/moonvalley/marey/text-to-video",
    "seedance": "fal-ai/bytedance/seedance/v1/pro/text-to-video",
    "happyhorse": "fal-ai/wan/v2.2-a14b/text-to-video",
    "kling": "fal-ai/kling-video/v2/master/text-to-video",
    "ltx": "fal-ai/ltx-video-13b-distilled",
}

#: What each shape is called on the wire. Named for what a person would
#: say upstream; resolved to a ratio here, because that is the vendor's
#: vocabulary and not the product's.
RATIOS = {"portrait": "9:16", "landscape": "16:9", "square": "1:1"}

#: A render this old is abandoned rather than followed forever. Well past
#: `filming.GIVE_UP_AFTER`, so the product gives up first and this is
#: only a floor under a leak.
MAX_AGE = 45 * 60


def model_for(provider: str) -> str:
    """The hosted model id for a provider name, environment first."""
    named = os.environ.get(f"FILM_MODEL_{provider.upper()}", "").strip()
    if named:
        return named
    if provider not in MODELS:
        raise HTTPException(
            400, f"this adapter has no model for {provider!r} — set "
                 f"FILM_MODEL_{provider.upper()} to the hosted id, or "
                 f"choose one of: {', '.join(sorted(MODELS))}")
    return MODELS[provider]


def key() -> str:
    got = os.environ.get("FAL_KEY", "").strip()
    if not got:
        raise HTTPException(
            503, "this adapter has no credential for the video house — "
                 "set FAL_KEY on the film container")
    return got


def _call(url: str, body: dict | None = None) -> dict:
    """One request to the queue, with the key attached and never logged."""
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url, data=data,
        headers={"Authorization": f"Key {key()}",
                 "Content-Type": "application/json",
                 "Accept": "application/json"},
        method="POST" if data is not None else "GET")
    try:
        with urllib.request.urlopen(req, timeout=60) as answer:
            return json.loads(answer.read().decode() or "{}")
    except urllib.error.HTTPError as exc:
        detail = ""
        try:
            detail = exc.read().decode()[:400]
        except Exception:                                # pragma: no cover
            pass
        # The status is echoed rather than swallowed: a 401 and a 404 send
        # an operator to two completely different places, and "the render
        # failed" sends them to neither.
        raise HTTPException(
            502, f"the video house answered {exc.code}"
                 + (f": {detail}" if detail else "")) from None
    except urllib.error.URLError as exc:
        raise HTTPException(
            502, f"the video house could not be reached: {exc.reason}") \
            from None


#: Jobs this process has started, so a poll knows which model to ask.
#: fal's status URL is per-model, and `filming.follow` only carries the
#: id — so the pairing has to live somewhere, and the somewhere is here
#: rather than in the product's database, which should not have to learn
#: a vendor's routing.
#:
#: In memory on purpose. A restart loses the pairing and the poll answers
#: "failed", which is honest and recoverable: the render is one turn's
#: footage, not a document, and the alternative is a schema for somebody
#: else's URL layout.
_JOBS: dict[str, tuple[str, float]] = {}


def _forget_old() -> None:
    stale = [j for j, (_, at) in _JOBS.items() if time.time() - at > MAX_AGE]
    for job in stale:
        _JOBS.pop(job, None)


class Scene(BaseModel):
    provider: str = Field(default="veo")
    prompt: str
    seconds: int = Field(default=5, ge=1, le=60)
    shape: str = Field(default="landscape")


@app.get("/health")
def health() -> dict:
    """Whether this adapter could render, and the shelf it can render on.

    `keyed` rather than the key: the credential is never returned,
    logged or reported, the same rule `filming.keyed` follows.
    """
    return {"ok": True, "keyed": bool(os.environ.get("FAL_KEY", "").strip()),
            "providers": sorted(MODELS), "queue": QUEUE}


@app.post("/")
def submit(body: Scene) -> dict:
    """Start a render, and answer the way `filming.render` expects."""
    model = model_for(body.provider)
    started = _call(f"{QUEUE}/{model}", {
        "prompt": body.prompt,
        "duration": body.seconds,
        "aspect_ratio": RATIOS.get(body.shape, "16:9"),
    })
    # Some models on some days answer complete on the first call. Both
    # roads are the product's own two answers, so neither is a surprise
    # upstream.
    direct = _video_in(started)
    if direct:
        return {"video_url": direct}
    job = started.get("request_id") or started.get("id")
    if not job:
        raise HTTPException(
            502, "the video house answered without a render or a job to "
                 "follow — nothing here can be shown or waited for")
    _forget_old()
    _JOBS[job] = (model, time.time())
    return {"id": job}


def _video_in(payload: dict) -> str | None:
    """The finished file, wherever this model chose to put it.

    Vendors disagree about this even between models on one host: a
    `video` object, a `video_url` string, a `videos` list. Asking in one
    place beats discovering the third shape in production.
    """
    if not isinstance(payload, dict):
        return None
    got = payload.get("video")
    if isinstance(got, dict) and got.get("url"):
        return got["url"]
    if isinstance(got, str) and got:
        return got
    if payload.get("video_url"):
        return payload["video_url"]
    videos = payload.get("videos")
    if isinstance(videos, list) and videos:
        first = videos[0]
        if isinstance(first, dict) and first.get("url"):
            return first["url"]
        if isinstance(first, str):
            return first
    return None


@app.get("/{job}")
def follow(job: str) -> dict:
    """Whether a started render has finished, in the product's words."""
    known = _JOBS.get(job)
    if known is None:
        # Not a 404: `filming.follow` reads a status, and a job this
        # process no longer knows about is a render that will never
        # arrive — which is `failed`, said plainly.
        return {"status": "failed",
                "detail": "this adapter has no record of that render — it "
                          "was started before the container restarted, or "
                          "it is older than the hour it is kept for"}
    model, _ = known
    state = _call(f"{QUEUE}/{model}/requests/{job}/status")
    status = (state.get("status") or "").upper()
    if status in ("IN_QUEUE", "IN_PROGRESS"):
        return {"status": "pending"}
    if status != "COMPLETED":
        return {"status": "failed",
                "detail": state.get("error") or f"the house said {status!r}"}
    result = _call(f"{QUEUE}/{model}/requests/{job}")
    url = _video_in(result)
    if not url:
        return {"status": "failed",
                "detail": "the render finished with no file in the answer"}
    _JOBS.pop(job, None)
    return {"status": "done", "video_url": url}
