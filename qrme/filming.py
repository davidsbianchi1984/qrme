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


def _ask(url: str, body: dict | None = None,
         on_behalf_of: str | None = None) -> dict:
    """One call to the service, with its refusals passed through.

    A vendor's own wording is better than ours — "the prompt was rejected
    by our safety filter" is something a person can act on, and
    "the render failed" is not.

    Offline mode is checked here rather than in `render`, and that is the
    correction: the gate sat one level up, so starting a render refused
    on an offline host and *polling* one did not. A poll carries a job id
    rather than somebody's words, but it still opens a socket to a
    service that is by definition not on this machine, and "nothing
    leaves the host" has to be true of every way out or it is not a
    property of the code.

        asked     does the render consult offline mode
        mattered  does everything that reaches the service consult it

    This is the only way out of this module, so gating it gates all of
    them.
    """
    from . import offline
    offline.allow(url, "the video service", on_behalf_of)

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
           directed_for: str | None = None,
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

    # The standing direction rides in front of the passage. Length was
    # derived from the passage alone, above, and stays that way: the
    # direction says how it looks, not how long it runs, and letting it
    # move the clock would make "put us on the beach" cost more money.
    prompt = compose(directed_for, scene) if directed_for else scene

    # The service this PROFILE renders on, not whichever one the box was
    # started with. Resolved once and used for the body, the answers and
    # the give-up message alike, so every sentence about this render names
    # the same company.
    using = provider_for(directed_for or on_behalf_of)

    began = time.monotonic()
    started = _ask(endpoint(), {"provider": using, "prompt": prompt,
                                "seconds": seconds, "shape": shape},
                   on_behalf_of=on_behalf_of)
    if started.get("video_url"):
        return {"video_url": started["video_url"], "provider": using,
                "seconds": seconds, "waited": 0}

    job = started.get("id")
    if not job:
        raise FilmingError(
            "the video service answered without a render or a job to "
            "follow — nothing here can be shown or waited for")
    if not wait:
        return {"id": job, "pending": True, "provider": using,
                **estimate(seconds)}

    while time.monotonic() - began < GIVE_UP_AFTER:
        time.sleep(POLL_EVERY)
        state = _ask(f"{endpoint()}/{job}", on_behalf_of=on_behalf_of)
        status = (state.get("status") or "").lower()
        if status == "done" and state.get("video_url"):
            return {"video_url": state["video_url"], "provider": using,
                    "seconds": seconds,
                    "waited": round(time.monotonic() - began)}
        if status == "failed":
            raise FilmingError(
                state.get("detail") or "the render failed at the service")

    raise FilmingError(i18n.fill(i18n.RENDER_GAVE_UP,
                                 minutes=GIVE_UP_AFTER // 60,
                                 provider=using, job=job))


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


# --------------------------------------------------------------------------- #
# The standing direction
# --------------------------------------------------------------------------- #

#: What a scene looks like before anybody has said otherwise. Deliberately
#: thin: enough that the first render is not a lottery, little enough that
#: the person's own words replace rather than argue with it.
DEFAULT_DIRECTION = (
    "A cinematic wide shot. The speaker is in frame, lit naturally, "
    "in a setting that suits what they are saying.")

#: How long a direction may run. A ceiling rather than a budget — the
#: direction rides every prompt, so one that grows without limit starts
#: crowding out the passage it is supposed to be framing.
MAX_DIRECTION = 600


def direction_of(profile_id: str) -> str:
    """How this profile's scenes are shot, in the owner's own words.

    The default until somebody says otherwise, and then whatever they
    said — carried from one render to the next, which is the whole point
    of it being stored rather than typed each time.
    """
    from . import db
    row = db.connect().execute(
        "SELECT direction FROM scene_direction WHERE profile_id=?",
        (profile_id,)).fetchone()
    return row["direction"] if row else DEFAULT_DIRECTION


def set_direction(profile_id: str, direction: str, *,
                  asked: str | None = None,
                  surface: str | None = None) -> str:
    """Write the direction verbatim, and log what it replaced.

    The road :func:`amend` ends on, and the one a caller takes when it
    already has the words it wants. Every write goes through here, which
    is why the log cannot fall out of step with the direction: there is
    no second place that sets one.
    """
    from . import db
    text = (direction or "").strip()[:MAX_DIRECTION]
    if not text:
        raise FilmingError("say how the scene should look, or clear it")
    was = direction_of(profile_id)
    conn = db.connect()
    now = db.utcnow()
    conn.execute(
        "INSERT INTO scene_direction (profile_id, direction, updated_at)"
        " VALUES (?,?,?) ON CONFLICT (profile_id) DO UPDATE SET"
        " direction=excluded.direction, updated_at=excluded.updated_at",
        (profile_id, text, now))
    conn.execute(
        "INSERT INTO scene_direction_log (id, profile_id, asked, was,"
        " became, surface, created_at) VALUES (?,?,?,?,?,?,?)",
        (db.new_id("scn"), profile_id, asked, was, text, surface, now))
    conn.commit()
    return text


def direction_log(profile_id: str, limit: int = 20) -> list[dict]:
    """What was asked of this scene, newest first.

    The direction is one row that gets overwritten, which is right for a
    standing setting and useless as an account of one. Somebody who has
    amended five times cannot otherwise tell which request caused the
    thing they now dislike, or step back one.

    `surface` says whether it was asked from the frame or from full
    screen — not because the two behave differently, they read and write
    the same row, but because "I changed that while it was full screen"
    is how a person remembers doing it.
    """
    from . import db
    rows = db.connect().execute(
        "SELECT asked, was, became, surface, created_at"
        " FROM scene_direction_log WHERE profile_id=?"
        " ORDER BY created_at DESC, rowid DESC LIMIT ?",
        (profile_id, max(1, min(200, limit)))).fetchall()
    return [dict(r) for r in rows]


def forget_direction(profile_id: str, surface: str | None = None) -> str:
    """Back to the default. Every standing thing in this platform has a
    way out that is one press, and this is not the exception.

    Logged like any other change. Starting over is a thing somebody did,
    and a log that records five amendments and not the reset reads as
    though the last amendment is still in force.
    """
    from . import db
    was = direction_of(profile_id)
    conn = db.connect()
    conn.execute("DELETE FROM scene_direction WHERE profile_id=?",
                 (profile_id,))
    if was != DEFAULT_DIRECTION:
        conn.execute(
            "INSERT INTO scene_direction_log (id, profile_id, asked, was,"
            " became, surface, created_at) VALUES (?,?,?,?,?,?,?)",
            (db.new_id("scn"), profile_id, None, was, DEFAULT_DIRECTION,
             surface, db.utcnow()))
    conn.commit()
    return DEFAULT_DIRECTION


def amend(profile_id: str, asked: str,
          surface: str | None = None) -> dict:
    """The person says what they want changed; the direction is rewritten.

    Not appended. Appending is the obvious implementation and it degrades
    fast: "it's too dark", then "still too dark", then "actually the beach
    was better" — twenty corrections become a transcript of complaints
    that contradict each other, and the renderer is handed all of it.

        asked     what did they want changed
        mattered  what does the scene look like now

    So the model is given the standing direction and the request and asked
    for the *resulting* direction, which stays one readable paragraph
    somebody can check. It is the person's own words that are authoritative
    — the request is applied, not negotiated with.
    """
    from . import llm
    want = (asked or "").strip()
    if not want:
        raise FilmingError("say what you would like changed about the scene")

    standing = direction_of(profile_id)
    system = (
        "You maintain the standing camera direction for one speaker's "
        "rendered scenes. You are given the current direction and a change "
        "the owner asked for. Answer with the COMPLETE new direction and "
        "nothing else — no preamble, no explanation, no quotation marks.\n"
        "Rules: apply what they asked rather than debating it. Keep "
        "everything they did not ask to change. Describe only the setting, "
        "the framing and the light — never what the speaker says or who "
        "they are. Stay under 80 words, in plain prose.")
    messages = [{"role": "user", "content":
                 f"Current direction:\n{standing}\n\nThey asked for:\n{want}"}]
    try:
        written = llm.provider_for_profile(profile_id).generate(system,
                                                               messages)
    except Exception:
        raise FilmingError(
            "the model that keeps the scene direction could not be "
            "reached — the direction is unchanged") from None

    written = (written or "").strip().strip('"')
    if not written:
        raise FilmingError(
            "the model answered with an empty direction — the scene is "
            "unchanged rather than blank")
    return {"direction": set_direction(profile_id, written, asked=want,
                                       surface=surface),
            "was": standing, "asked": want}


def compose(profile_id: str, passage: str) -> str:
    """The prompt actually sent: how it looks, then what is said.

    The direction leads because it is the frame the passage sits inside,
    and a renderer reading them the other way round tends to treat the
    setting as an afterthought.
    """
    return f"{direction_of(profile_id)}\n\n{(passage or '').strip()}"


# --------------------------------------------------------------------------- #
# The road, the ceiling, and rendering without being asked
# --------------------------------------------------------------------------- #

#: The three roads a presence takes. `photo` leads because it is what a
#: profile has before anybody chooses, and what every other road falls
#: back to when it is not ready.
ROADS = ("photo", "avatar", "video")
DEFAULT_ROAD = "photo"

#: How many seconds of finished footage one profile may render in a day
#: unless its owner says otherwise. At the going rate this is a few
#: dollars — enough to see the feature work, small enough that a room
#: left running overnight is an annoyance rather than an incident.
DEFAULT_DAILY_SECONDS = 60


def road_of(profile_id: str) -> dict:
    """Which road this profile's presence takes, its ceiling, and its service.

    ``provider`` is always a name a caller can act on: the profile's own
    choice when it made one, and the deployment's otherwise. ``provider_set``
    is how a screen tells those apart, so it can show a picked service
    differently from an inherited one instead of claiming the owner chose
    something they never touched.
    """
    from . import db
    row = db.connect().execute(
        "SELECT road, daily_seconds, provider FROM presence_road"
        " WHERE profile_id=?", (profile_id,)).fetchone()
    if row is None:
        return {"road": DEFAULT_ROAD, "daily_seconds": DEFAULT_DAILY_SECONDS,
                "set": False, "provider": provider(), "provider_set": False}
    picked = row["provider"] if row["provider"] in PROVIDERS else None
    return {"road": row["road"], "daily_seconds": row["daily_seconds"],
            "set": True, "provider": picked or provider(),
            "provider_set": bool(picked)}


def provider_for(profile_id: str | None) -> str:
    """The service that renders THIS profile, falling back to the box's.

    One place answers this, because the name has to be the same in the
    body that is sent and in the row that records what was sent. Two
    lookups is how a console ends up reporting a render against a service
    that did not make it.
    """
    return road_of(profile_id)["provider"] if profile_id else provider()


def set_road(profile_id: str, road: str,
             daily_seconds: int | None = None,
             film_provider: str | None = None) -> dict:
    """Choose the road, the ceiling that makes choosing video safe, and the
    service that renders it.

    ``film_provider`` is left alone when None — the three settings live in
    one row and one route, and a screen that sends the road has not
    thereby said anything about the service. Passing ``"none"`` is how an
    owner hands the choice back to the deployment.

        asked     which video company will render this
        mattered  does pressing the name change what gets sent

    The endpoint and the credential stay deployment-wide. This module
    speaks one submit-and-poll protocol and the model name rides in the
    body, so an owner picking a service spends no new secret and reaches
    nothing the operator did not already point at.
    """
    from . import db
    if road not in ROADS:
        raise FilmingError(
            "a presence takes one of these roads — " + ", ".join(ROADS))
    cap = road_of(profile_id)["daily_seconds"] if daily_seconds is None \
        else int(daily_seconds)
    if cap < 0:
        raise FilmingError("a ceiling below zero is not a ceiling")
    if film_provider is not None and film_provider not in PROVIDERS:
        raise FilmingError(
            "this platform renders on one of these — "
            + ", ".join(p for p in PROVIDERS if p != "none"))
    # "none" is a real answer meaning "whatever the deployment named", so it
    # is stored as NULL rather than as the string: a row holding "none"
    # would later read as a profile that chose to render nowhere.
    keep = None if film_provider in (None, "none") else film_provider
    conn = db.connect()
    if film_provider is None:
        conn.execute(
            "INSERT INTO presence_road (profile_id, road, daily_seconds,"
            " updated_at) VALUES (?,?,?,?)"
            " ON CONFLICT (profile_id) DO UPDATE SET"
            " road=excluded.road, daily_seconds=excluded.daily_seconds,"
            " updated_at=excluded.updated_at",
            (profile_id, road, cap, db.utcnow()))
    else:
        conn.execute(
            "INSERT INTO presence_road (profile_id, road, daily_seconds,"
            " provider, updated_at) VALUES (?,?,?,?,?)"
            " ON CONFLICT (profile_id) DO UPDATE SET"
            " road=excluded.road, daily_seconds=excluded.daily_seconds,"
            " provider=excluded.provider, updated_at=excluded.updated_at",
            (profile_id, road, cap, keep, db.utcnow()))
    conn.commit()
    return road_of(profile_id)


def spent_today(profile_id: str) -> int:
    """Seconds of footage this profile has ordered today.

    Counts renders that are still PENDING as well as finished ones. Two
    turns in quick succession would otherwise both pass a ceiling neither
    had spent yet — the money is committed when the job starts, not when
    the video arrives.
    """
    from . import db
    row = db.connect().execute(
        "SELECT COALESCE(SUM(seconds), 0) AS spent FROM scene_render"
        " WHERE profile_id=? AND status != 'failed'"
        " AND substr(created_at, 1, 10) = substr(?, 1, 10)",
        (profile_id, db.utcnow())).fetchone()
    return int(row["spent"])


def budget(profile_id: str) -> dict:
    """What is left today, said in the terms the ceiling is set in."""
    settings = road_of(profile_id)
    spent = spent_today(profile_id)
    return {"daily_seconds": settings["daily_seconds"], "spent": spent,
            "left": max(0, settings["daily_seconds"] - spent)}


def auto_render(profile_id: str, passage: str,
                shape: str = "landscape") -> dict | None:
    """Render this reply as footage, if that is the road and there is room.

    The turn calls this and moves on. Nothing is waited for: a render is
    minutes and a reply is not, so what comes back is a row a screen can
    poll rather than a video.

        asked     should this reply become footage
        mattered  can it, today, without spending what nobody agreed to

    Answers None — never raises — when the road is not video, when the
    ceiling is reached, or when no service is configured. A turn is not
    the place to fail: the reply already happened, the person is reading
    it, and a video that did not get made is a smaller thing than an
    answer that did not arrive.
    """
    from . import db

    settings = road_of(profile_id)
    if settings["road"] != "video" or not configured():
        return None

    seconds = length_for(passage)
    left = budget(profile_id)["left"]
    if seconds > left:
        # Recorded rather than silent. An owner who set a ceiling and then
        # stopped seeing video is owed the reason, and "you reached the
        # limit you set" is a different sentence from "it broke".
        return {"status": "capped", "seconds": seconds, "left": left,
                "daily_seconds": settings["daily_seconds"]}

    row_id = db.new_id("ren")
    conn = db.connect()
    conn.execute(
        "INSERT INTO scene_render (id, profile_id, passage, seconds, status,"
        " created_at) VALUES (?,?,?,?,'pending',?)",
        (row_id, profile_id, passage.strip()[:2000], seconds, db.utcnow()))
    conn.commit()

    try:
        started = render(passage, seconds=seconds, shape=shape,
                         directed_for=profile_id, on_behalf_of=profile_id,
                         wait=False)
    except FilmingError as exc:
        settle(row_id, status="failed", detail=i18n.raised(exc))
        return {"id": row_id, "status": "failed",
                "detail": i18n.raised(exc)}

    if started.get("video_url"):
        settle(row_id, status="done", video_url=started["video_url"])
    else:
        conn.execute("UPDATE scene_render SET job=? WHERE id=?",
                     (started.get("id"), row_id))
        conn.commit()
    return latest(profile_id)


def settle(render_id: str, *, status: str, video_url: str | None = None,
           detail: str | None = None) -> None:
    """Write how a render ended. Called once; a settled row stays settled.

    Guarded in SQL rather than by reading first: two pollers finishing the
    same job would otherwise both write, and the second would overwrite a
    `done` with whatever it saw.
    """
    from . import db
    conn = db.connect()
    conn.execute(
        "UPDATE scene_render SET status=?, video_url=?, detail=?,"
        " settled_at=? WHERE id=? AND status='pending'",
        (status, video_url, detail, db.utcnow(), render_id))
    conn.commit()


def latest(profile_id: str) -> dict | None:
    """The most recent render for this profile, however it ended."""
    from . import db
    row = db.connect().execute(
        "SELECT id, seconds, job, video_url, status, detail, created_at"
        " FROM scene_render WHERE profile_id=?"
        " ORDER BY created_at DESC, rowid DESC LIMIT 1",
        (profile_id,)).fetchone()
    return dict(row) if row else None


def follow(render_id: str) -> dict | None:
    """Ask the service whether a pending render has finished.

    What a screen polls. A render that is already settled is returned as
    it stands rather than asked about again — the service is billed per
    call on some plans, and a finished job does not become unfinished.
    """
    from . import db
    row = db.connect().execute(
        "SELECT id, profile_id, job, status, video_url, seconds, detail"
        " FROM scene_render WHERE id=?", (render_id,)).fetchone()
    if row is None:
        return None
    if row["status"] != "pending" or not row["job"]:
        return dict(row)
    try:
        state = _ask(f"{endpoint()}/{row['job']}",
                     on_behalf_of=row["profile_id"])
    except FilmingError as exc:
        # A poll that could not reach the service is not a failed render.
        # The job may well be running; saying it failed would throw away a
        # video somebody has already paid for.
        return {**dict(row), "detail": i18n.raised(exc)}
    status = (state.get("status") or "").lower()
    if status == "done" and state.get("video_url"):
        settle(row["id"], status="done", video_url=state["video_url"])
    elif status == "failed":
        settle(row["id"], status="failed",
               detail=state.get("detail") or "the render failed at the service")
    return dict(db.connect().execute(
        "SELECT id, profile_id, job, status, video_url, seconds, detail"
        " FROM scene_render WHERE id=?", (render_id,)).fetchone())
