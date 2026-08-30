"""A described scene, rendered as video by a service that is not this one.

The door is **open**. It is slow, and that is the person's call to make
rather than ours.

    asked     is it fast enough to ship
    mattered  whose decision is it whether to wait

Thirty seconds of 4K takes minutes today, not moments. The first draft of
this module treated that as a reason to keep the road shut, which is a
product decision dressed as an engineering one: somebody who wants a
scene badly enough to wait four minutes for it is not confused, and a
platform that refuses on their behalf has decided their time is worth
less than its own tidiness. So the wait is *quoted* — :func:`estimate`
answers before anybody commits — and then it is theirs.

## Why it is a list and not a vendor

OpenAI deprecated Sora 2 on 26 April 2026 and shuts its API down on
24 September 2026. Ready Player Me was bought and closed on 31 January
2026, which is the event that taught this codebase the lesson the first
time (`qrme/avatarforge.py`, `docker/forge/`). Two shutdowns inside
fifteen months, in the two markets this platform would most like to buy
from.

So :data:`PROVIDERS` names several, none of them load-bearing, and Sora is
absent on purpose: a shelf that sends somebody to a service with a
published end date is worse than a shelf one row shorter. The same call
`avatars.MARKET` made when Ready Player Me went.

## The shape this speaks

`QRME_FILM_URL` points at something that speaks **submit-and-poll JSON**,
the way `QRME_FORGE_URL` points at our own sidecar:

    POST  {url}         {"provider", "prompt", "seconds", "shape"}
          -> {"video_url": ...}            a render that finished at once
          -> {"id": ...}                   a render that did not
    GET   {url}/{id}    -> {"status": "pending" | "done" | "failed",
                            "video_url": ..., "detail": ...}

That is the shape the aggregators hosting these models already use, and
it is one adapter away from any vendor whose own API differs. Naming the
shape is the honest version of "supports seven providers": this module
speaks one protocol, and the provider name rides in the body so whatever
is on the other end knows which model to run.

## What this module will never do quietly

A generated video is synthetic media outright, so anything that comes
back is marked at the moment it is stored — :func:`save` calls
`media.save` with ``ai_marked=True`` and there is no argument that turns
it off. A video is the most persuasive artifact this platform can produce
and the one most likely to be met with no context around it, which makes
the mark more load-bearing here than anywhere else, not less.

It also costs real money per second of output — ten to fifteen cents a
second at the going rate, so a half-minute clip is three to four dollars.
:data:`MAX_SECONDS` is a ceiling on one render rather than a budget; a
deployment that opens this door wants a spend limit above it.

## Length is derived, not dialled

There is no slider. :func:`length_for` works out how long a passage takes
to say and renders it for that long, because a dial makes the video fit
the setting instead of the content — two sentences padded out to thirty
seconds, or a paragraph hurried into five, footage stretched or clipped
to hit a number nobody meant. The console shows the number it arrived at;
it does not offer to change it.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request

from . import i18n

#: The roads this module can speak. ``none`` leads because it is what a
#: deployment gets unless somebody chooses otherwise, and an unknown name
#: reads as ``none`` — a misspelled provider must not become a working one.
#:
#: Ordered by where each stood when this was written, which is a fact with
#: a short shelf life and is why nothing downstream reads the order.
PROVIDERS = (
    "none",
    "seedance",     # ByteDance. 2.5 does 30s of native 4K with audio.
    "happyhorse",   # Alibaba ATH. Arrived April 2026 near the top.
    "veo",          # Google DeepMind. Veo 3.1, audio, ~$0.15/sec fast.
    "kling",        # Kuaishou. 3.0 does 4K/60, and a cheaper Turbo.
    "ltx",          # Lightricks. 2.3 is 22B, 4K/50 with stereo.
    "luma",         # Luma. Ray3 was the first with native 16-bit HDR.
    "runway",       # Runway. The one most studios already have a seat at.
)

#: How long one render may be asked for. Not a budget — a ceiling on a
#: single call, so a runaway script cannot order a five-minute film.
MAX_SECONDS = 30

#: The floor. Below this a clip is a flicker rather than a shot.
MIN_SECONDS = 2

#: Unhurried speech. Used to work out how long a passage takes to say,
#: which is how long its video should run.
WORDS_PER_MINUTE = 150

#: Roughly how long a second of finished video takes to render, used to
#: quote a wait before anybody commits to one. Deliberately pessimistic:
#: a quote that comes in under is a pleasant surprise, and a quote that
#: comes in over is the reason somebody stops trusting the number.
SECONDS_PER_SECOND = 12

#: How long :func:`render` will keep asking before it gives up. Generous
#: on purpose — the person was told the wait and chose it, so timing out
#: under the quote would make the quote a lie.
GIVE_UP_AFTER = 15 * 60

#: How often to ask whether it is done. Slow enough not to hammer a
#: vendor's rate limit over a render measured in minutes.
POLL_EVERY = 3

#: What a scene may be asked for in. Named for what a person would say
#: rather than for a resolution, because the resolutions move.
SHAPES = ("portrait", "landscape", "square")


class FilmingError(RuntimeError):
    """A refusal from this road, worded for the person who asked."""


def provider() -> str:
    """Which service this deployment renders on. ``none`` unless an
    operator names one, and ``none`` again if they name one this module
    does not know."""
    named = os.environ.get("QRME_FILM_PROVIDER", "none").strip().lower()
    return named if named in PROVIDERS else "none"


def endpoint() -> str:
    return os.environ.get("QRME_FILM_URL", "").strip().rstrip("/")


def keyed() -> bool:
    """Whether a credential is present. The key itself is never returned,
    logged, or reported by :func:`doors` — only whether there is one."""
    return bool(os.environ.get("QRME_FILM_KEY", "").strip())


def configured() -> bool:
    """Whether a scene could actually be rendered here.

    False is an answer a screen shows rather than a button that fails,
    which is the same posture `avatarforge.configured` takes. All three
    have to be true: a provider chosen, somewhere to send it, and a key
    to send it with.
    """
    return provider() != "none" and bool(endpoint()) and keyed()


def why_not() -> str | None:
    """What to tell a person who asks why this cannot be done here.

    Specific about which of the three is missing — an operator reading
    "not configured" learns nothing about what to do next, which is how a
    door stays shut by accident rather than by decision.
    """
    if configured():
        return None
    if provider() == "none":
        return ("This deployment has not chosen a video service. The road "
                "is built and nobody has pointed it anywhere — set "
                "QRME_FILM_PROVIDER, QRME_FILM_URL and QRME_FILM_KEY.")
    if not endpoint():
        return (f"A provider is named ({provider()}) but there is nowhere "
                f"to send the scene — set QRME_FILM_URL.")
    return (f"A provider is named ({provider()}) and there is no key to "
            f"reach it with — set QRME_FILM_KEY.")


def length_for(text: str) -> int:
    """How long a passage takes to say, which is how long to render it.

    Length is **not** a control a person is given. A dial makes the video
    fit the setting instead of the content: two sentences padded out to
    thirty seconds, or a paragraph hurried into five, and in both cases
    the footage is stretched or clipped to hit a number nobody meant.

        asked     how long should this video be
        mattered  how long is the thing it is a video of

    So it is derived and then shown. The ceiling still applies, and
    :func:`too_long` is how a caller finds out it was hit rather than
    discovering a sentence went missing.
    """
    words = len((text or "").split())
    spoken = round(words / (WORDS_PER_MINUTE / 60))
    return max(MIN_SECONDS, min(MAX_SECONDS, spoken))


def too_long(text: str) -> bool:
    """Whether this passage needs more than one scene can hold.

    Answered rather than silently truncated: a video that quietly drops
    its last sentence is worse than one that was never made, because
    nobody watching can tell.
    """
    words = len((text or "").split())
    return round(words / (WORDS_PER_MINUTE / 60)) > MAX_SECONDS


def estimate(seconds: int) -> dict:
    """What to say before anybody commits to a wait.

    The whole reason this door is open rather than shut: the person is
    told what it will cost them in time and decides. A screen that starts
    a four-minute render without saying so is where the original instinct
    to close this came from.
    """
    return {
        "seconds": seconds,
        "wait_seconds": seconds * SECONDS_PER_SECOND,
        "give_up_after": GIVE_UP_AFTER,
        "worth_leaving": seconds * SECONDS_PER_SECOND > 60,
    }


def doors() -> dict:
    """What this deployment offers, said before anybody writes a prompt.

    The console draws the road only when there is one and says why when
    there is not, exactly as it does for the forge.
    """
    return {
        "provider": provider(),
        "configured": configured(),
        "why": why_not(),
        "providers": [p for p in PROVIDERS if p != "none"],
        # Length is derived from the passage, not chosen — see
        # `length_for`. These are reported so a screen can SHOW the number
        # it arrived at, never so it can offer a dial.
        "max_seconds": MAX_SECONDS,
        "min_seconds": MIN_SECONDS,
        "words_per_minute": WORDS_PER_MINUTE,
        "length_is_derived": True,
        "seconds_per_second": SECONDS_PER_SECOND,
        "give_up_after": GIVE_UP_AFTER,
        "shapes": list(SHAPES),
        # Stated in the answer rather than left to the caller to
        # remember: whatever comes back is synthetic media and is marked
        # at the moment it is stored.
        "marked": True,
    }


def check(scene: str, *, seconds: int = 5, shape: str = "landscape") -> None:
    """Everything that can be refused before a socket is opened.

    Split out so the console can validate a form on a deployment that has
    chosen no provider, and so the refusals stay testable without one.
    """
    if not (scene or "").strip():
        raise FilmingError("say what the scene is before asking for it")
    if shape not in SHAPES:
        raise FilmingError(i18n.fill(i18n.SCENE_SHAPE,
                                     choices=", ".join(SHAPES)))
    if seconds < 1:
        raise FilmingError("a scene shorter than a second is a still")
    if seconds > MAX_SECONDS:
        raise FilmingError(i18n.fill(i18n.SCENE_TOO_LONG,
                                     seconds=seconds, max=MAX_SECONDS))


def _ask(url: str, body: dict | None = None) -> dict:
    """One call to the service, with its refusals passed through.

    A vendor's own wording is better than ours — "the prompt was rejected
    by our safety filter" is something a person can act on, and
    "the render failed" is not.
    """
    key = os.environ.get("QRME_FILM_KEY", "").strip()
    headers = {"authorization": f"Bearer {key}"}
    data = None
    if body is not None:
        headers["content-type"] = "application/json"
        data = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        url, data=data, method="POST" if data else "GET", headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=60) as answer:
            return json.loads(answer.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        try:
            said = json.loads(exc.read().decode("utf-8")).get("detail")
        except Exception:
            said = None
        raise FilmingError(said or "the video service refused that scene") \
            from None
    except Exception:
        raise FilmingError(
            "the video service could not be reached from here") from None


def render(scene: str, *, seconds: int | None = None,
           shape: str = "landscape",
           on_behalf_of: str | None = None,
           wait: bool = True) -> dict:
    """One described scene, as video.

    Answers ``{"video_url", "provider", "seconds", "waited"}`` when it
    finishes, or ``{"id", "pending": True}`` when ``wait`` is False and
    the caller would rather poll from a screen than hold a request open
    for four minutes.
    """
    # Derived from the passage unless a caller insists. The console never
    # insists — there is no control for it — so this is the road every
    # ordinary render takes.
    seconds = length_for(scene) if seconds is None else seconds
    check(scene, seconds=seconds, shape=shape)
    if not configured():
        raise FilmingError(why_not() or "this deployment renders no video")

    # Offline mode's own rule, applied the way the forge applies it: the
    # check is on the HOST. A prompt describing a scene is somebody's
    # words, and a render service is by definition not on this machine,
    # so an offline deployment refuses here rather than discovering it
    # mid-upload.
    from . import offline
    offline.allow(endpoint(), "the video service's prompt", on_behalf_of)

    began = time.monotonic()
    started = _ask(endpoint(), {"provider": provider(), "prompt": scene,
                                "seconds": seconds, "shape": shape})
    if started.get("video_url"):
        return {"video_url": started["video_url"], "provider": provider(),
                "seconds": seconds, "waited": 0}

    job = started.get("id")
    if not job:
        raise FilmingError(
            "the video service answered without a render or a job to "
            "follow — nothing here can be shown or waited for")
    if not wait:
        return {"id": job, "pending": True, "provider": provider(),
                **estimate(seconds)}

    while time.monotonic() - began < GIVE_UP_AFTER:
        time.sleep(POLL_EVERY)
        state = _ask(f"{endpoint()}/{job}")
        status = (state.get("status") or "").lower()
        if status == "done" and state.get("video_url"):
            return {"video_url": state["video_url"], "provider": provider(),
                    "seconds": seconds,
                    "waited": round(time.monotonic() - began)}
        if status == "failed":
            raise FilmingError(
                state.get("detail") or "the render failed at the service")

    raise FilmingError(i18n.fill(i18n.RENDER_GAVE_UP,
                                 minutes=GIVE_UP_AFTER // 60,
                                 provider=provider(), job=job))


def save(profile_id: str, data: bytes, *, name: str = "scene.mp4") -> dict:
    """Store a finished render against a profile, marked.

    The one entry point that puts a generated video into this platform's
    own media store, so the mark is applied in one place rather than at
    each caller that might forget. There is no argument that turns it
    off, which is the difference between a rule and a default.
    """
    from . import media
    return media.save(profile_id, data, name=name,
                      alt="a rendered scene", ai_marked=True)
