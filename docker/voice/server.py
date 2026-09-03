"""The stack's phone line — one door onto whichever phone house is chosen,
for JIM's calls to a person's emergency contacts.

JIM's reach-out cascade (``jim/reachout.py``) rings a trusted person,
asks them to press 1 to hear the message, and then talks — the model's
own words, grounded in what happened. Every one of those steps was built
and tested by driving the handlers a phone company's webhooks would one
day call, and then no phone company was ever wired: ``JIM_VOICE_URL``
had nothing on the box to point at, every contact call came back
*prepared*, and the cascade walked its whole ladder without a phone
ringing anywhere.

    asked     did JIM call anybody
    mattered  there was nothing at the other end of the wire

This is that end of the wire, on the same pattern as ``docker/film``: a
thin translator with one job, so the product's image holds no vendor
credential and a vendor swap is a row in ``houses/`` rather than a change
through the whole codebase.

## Two faces

Toward JIM, on the compose network only and never published by Caddy:
``GET /health`` (open, booleans only), ``GET /standing`` and
``POST /calls`` (both under ``Authorization: Bearer VOICE_SECRET``).
Toward the phone house, published under ``/voice/*``:
``GET /voice/ping`` and ``POST /voice/{house}/{call_id}/answer | gather
| speech | status``. The paths are the whole difference: ``/calls`` is
not under ``/voice``, so the internet cannot ask this box to ring a
number even with the secret.

## Three locks, and the one it will never open

The secret gates JIM's doors both ways. Every vendor URL carries a
per-call capability — an HMAC of the call id under the same secret,
minted at placement and compared on return — and every vendor door then
checks the house's own signature over the URL the house actually signed,
rebuilt from ``VOICE_PUBLIC_URL`` and never from a ``Host`` header. There
is no switch to turn the second check off. And any number whose digits
are an emergency short code is refused here at 422 before a house is
asked, the lock under JIM's own — this door rings people, never
dispatchers, and JIM's 911 send stays held shut in its own source.

## Stateless on purpose

The sidecar keeps nothing it cannot afford to lose. Which try this is,
whether one silence has passed, and which turn comes next all ride the
callback URL; every sentence the contact hears comes from JIM's ``line``
envelope; and :data:`_LINES` remembers the last envelope only for the
branches that are the sidecar's alone — the one re-prompt, the silence
prompt, the closing, the trouble line. On a miss it asks JIM instead of
inventing, so a restart mid-call costs one polite phrase and never a leg.

## Overrides, in the film sidecar's discipline

A house's base URL is ``VOICE_<HOUSE>_API`` (``VOICE_TWILIO_API``,
``VOICE_SIGNALWIRE_API``, ...), a language tag ``VOICE_LANG_<XX>``, and
``VOICE_TOKEN_FILE`` names a file holding the credential (a Vonage
private key) instead of ``VOICE_TOKEN``. Documented here rather than in
the deploy page's template because they are repairs, not settings.
"""

import hashlib
import hmac
import json
import logging
import os
import pathlib
import re
import secrets
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request, Response
from starlette.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

HERE = pathlib.Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import houses  # noqa: E402
from houses import HOUSES, Config, Event, House  # noqa: E402

app = FastAPI()
log = logging.getLogger("voice")

#: Digits this door will not ring, with or without a leading 1 or +, after
#: spaces, dashes, dots and parentheses are stripped. The same table as
#: JIM's ``telephony.EMERGENCY_NUMBERS``; the lock under its lock.
EMERGENCY_NUMBERS = frozenset({"911", "112", "999", "000", "111", "119",
                               "110", "122", "15", "17", "18"})

#: How long JIM gets to answer, in seconds. The speech leg waits longer
#: because a model turn sits behind it; the phone house itself waits about
#: fifteen seconds for markup, so the deploy page sets JIM_LLM_TIMEOUT to
#: ten on a box with a line.
JIM_TIMEOUT = 12.0
SAY_TIMEOUT = 12.0

#: How long a probe of the house or the public URL waits.
PROBE_TIMEOUT = 3.0
#: How long the house gets to take a call. Shorter than JIM's wait on
#: /calls (10 s), which is shorter than this door's wait on JIM's call-id
#: doors (12 s), which fits inside the 15 s a house gives a webhook — so a
#: slow answer is never recorded as no answer at any link of the chain.
HOUSE_TIMEOUT = 8.0
#: The most a vendor may post to a public door before either lock is read.
MAX_BODY = 64 * 1024

#: How long the standing probes are believed before they are made again.
STANDING_CACHE_S = 60

#: How long a remembered line is kept. Well past any call's ceiling, so it
#: is only ever a floor under a leak.
MAX_AGE = 30 * 60

_STRIP = str.maketrans("", "", " -.()")
_E164 = re.compile(r"^\+[1-9][0-9]{6,14}$")
_CALL_ID = re.compile(r"^[A-Za-z0-9_.-]{1,80}$")


# --------------------------------------------------------------------------- #
# the environment, read at the request and never printed
# --------------------------------------------------------------------------- #

def _env(name: str) -> str:
    return os.environ.get(name, "").strip()


def _token() -> str:
    """The house credential: ``VOICE_TOKEN``, or the contents of the file
    ``VOICE_TOKEN_FILE`` names (a PEM is easier mounted than pasted)."""
    got = _env("VOICE_TOKEN")
    if got:
        return got
    path = _env("VOICE_TOKEN_FILE")
    if path:
        try:
            return pathlib.Path(path).read_text(encoding="utf-8").strip()
        except OSError:
            return ""
    return ""


def _config() -> Config:
    return Config(
        provider=(_env("VOICE_PROVIDER") or "twilio").lower(),
        secret=_env("VOICE_SECRET"),
        jim_url=(_env("VOICE_JIM_URL") or "http://jim:8200").rstrip("/"),
        public_url=_env("VOICE_PUBLIC_URL").rstrip("/"),
        from_=_env("VOICE_FROM"),
        account=_env("VOICE_ACCOUNT"),
        token=_token(),
        webhook_key=_env("VOICE_WEBHOOK_KEY"),
        house_ref=_env("VOICE_HOUSE_REF"),
    )


def _public_url_well_formed(url: str) -> bool:
    return (url.startswith("https://") or url.startswith("http://")) \
        and url.rstrip("/").endswith("/voice")


# --------------------------------------------------------------------------- #
# numbers
# --------------------------------------------------------------------------- #

def normalize(to: str) -> str:
    """The same shaping JIM applies before it asks: strip spaces, dashes,
    dots and parentheses; ``00`` becomes ``+``; a bare North American ten
    digits gains ``+1``."""
    got = (to or "").strip().translate(_STRIP)
    if got.startswith("00"):
        got = "+" + got[2:]
    if re.fullmatch(r"[0-9]{10}", got):
        got = "+1" + got
    return got


def is_emergency(to: str) -> bool:
    """Whether the digits are an emergency short code, with or without a
    leading 1 or +: ``911``, ``+1911``, ``9-1-1`` and `` 999 `` are all
    caught."""
    # Both before and after the international rewrite: `000` is a short
    # code too, and `00` is also how a person types `+`.
    stripped = (to or "").strip().translate(_STRIP).lstrip("+")
    for digits in (stripped, normalize(to).lstrip("+")):
        if not digits.isdigit():
            continue
        if digits in EMERGENCY_NUMBERS or (
                digits.startswith("1") and digits[1:] in EMERGENCY_NUMBERS):
            return True
    return False


# --------------------------------------------------------------------------- #
# the two wires out, one function each, so a test can hold both
# --------------------------------------------------------------------------- #

def _house_http(method: str, url: str, *, headers: dict | None = None,
                body: bytes | None = None,
                timeout: float = HOUSE_TIMEOUT) -> tuple[int, str]:
    """The one request toward the internet: the house's API, and the
    box's own public name for the webhooks probe. Answers ``(status,
    text)`` for anything the far end said, and raises
    :class:`houses.Unreachable` when nothing did. Headers carry the
    credential and are never part of any message this raises."""
    req = urllib.request.Request(url, data=body, method=method,
                                 headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as answer:
            return answer.status, answer.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        try:
            text = exc.read().decode("utf-8", "replace")
        except Exception:                                # pragma: no cover
            text = ""
        return exc.code, text
    except OSError as exc:
        reason = getattr(exc, "reason", None) or exc
        raise houses.Unreachable(str(reason)) from None


def _jim(method: str, url: str, *, headers: dict, data: bytes | None,
         timeout: float) -> tuple[int, dict]:
    """The one request toward JIM. Answers ``(status, body)`` for anything
    JIM said — a 401, a 404, a 409 are answers — and ``(0, {detail})``
    when JIM could not be reached, so a caller sees one shape either way.
    Tests replace this and read the bearer off ``headers``."""
    req = urllib.request.Request(url, data=data, method=method,
                                 headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as answer:
            return answer.status, _json(answer.read())
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read()
        except Exception:                                # pragma: no cover
            body = b""
        return exc.code, _json(body)
    except OSError as exc:
        reason = getattr(exc, "reason", None) or exc
        return 0, {"detail": f"JIM could not be reached: {reason}"}


def _json(raw: bytes) -> dict:
    try:
        got = json.loads(raw or b"{}")
    except ValueError:
        return {"detail": raw.decode("utf-8", "replace")[:400]}
    return got if isinstance(got, dict) else {"detail": got}


def _ask(method: str, path: str, body: dict | None = None,
         timeout: float = JIM_TIMEOUT) -> tuple[int, dict]:
    """One request to JIM's call-id doors, with the bearer attached.
    ``VOICE_JIM_URL`` is a compose literal and is never taken from a
    request."""
    cfg = _config()
    headers = {"Content-Type": "application/json",
               "Accept": "application/json"}
    if cfg.secret:
        headers["Authorization"] = f"Bearer {cfg.secret}"
    data = json.dumps(body).encode() if body is not None else None
    status, got = _jim(method, cfg.jim_url + path, headers=headers,
                       data=data, timeout=timeout)
    if status != 200:
        # Logged with the status and the path, never the body's words
        # (a 403 here is a secret mismatch, and evidence).
        log.warning("JIM answered %s to %s %s", status or "nothing",
                    method, path)
    return status, got


# --------------------------------------------------------------------------- #
# the locks
# --------------------------------------------------------------------------- #

def _sig(secret: str, call_id: str) -> str:
    """The per-call capability carried in every vendor URL."""
    return hmac.new(secret.encode(), call_id.encode(),
                    hashlib.sha256).hexdigest()[:32]


def _require_bearer(cfg: Config, request: Request) -> None:
    if not cfg.secret:
        raise HTTPException(
            503, "this adapter has no secret to check JIM against — set "
                 "VOICE_SECRET on the voice container (JIM_VOICE_SECRET in "
                 ".env)")
    header = request.headers.get("authorization", "")
    token = header[7:].strip() if header.lower().startswith("bearer ") else ""
    if not token:
        raise HTTPException(401, "voice adapter token required")
    if not secrets.compare_digest(token.encode(), cfg.secret.encode()):
        raise HTTPException(403, "invalid voice adapter token")


def _house_name(cfg: Config) -> str:
    if cfg.provider not in HOUSES:
        raise HTTPException(
            503, f"this adapter does not know the house {cfg.provider!r} — "
                 f"set JIM_TELEPHONY_PROVIDER to one of: "
                 f"{', '.join(sorted(HOUSES))}")
    return cfg.provider


def _unkeyed(cfg: Config, row: House) -> tuple[str, str] | None:
    """The first credential missing, as (detail, fix), or None."""
    if not cfg.token:
        fix = ("set VOICE_TOKEN on the voice container (JIM_VOICE_TOKEN in "
               ".env)")
        return (f"this adapter has no credential for {row.name} — {fix}", fix)
    if row.account_means and not cfg.account:
        fix = f"set JIM_VOICE_ACCOUNT to the {row.name} {row.account_means}"
        return (f"this adapter has no account id for {row.name} — {fix}", fix)
    if row.webhook_key_means and not cfg.webhook_key:
        fix = (f"set JIM_VOICE_WEBHOOK_KEY to the {row.name} "
               f"{row.webhook_key_means}")
        return (f"this adapter cannot verify {row.name} webhooks — {fix}", fix)
    return None


def _unaddressed(cfg: Config, row: House) -> tuple[str, str] | None:
    """The first address missing, as (detail, fix), or None."""
    if not cfg.from_:
        return ("this adapter has no From number — set JIM_VOICE_FROM",
                "set JIM_VOICE_FROM")
    if not cfg.public_url:
        return ("this adapter has no public URL — set JIM_VOICE_PUBLIC_URL",
                "set JIM_VOICE_PUBLIC_URL to https://<jim host>/voice")
    if not _public_url_well_formed(cfg.public_url):
        return ("JIM_VOICE_PUBLIC_URL must end in /voice — the Caddy route "
                "forwards that prefix and nothing else",
                "set JIM_VOICE_PUBLIC_URL to https://<jim host>/voice")
    if row.house_ref_means and not cfg.house_ref:
        fix = f"set JIM_VOICE_HOUSE_REF to the {row.house_ref_means}"
        return (f"this adapter has no {row.house_ref_means} — {fix}", fix)
    return None


def _require_configured(cfg: Config, row: House) -> None:
    for wrong in (_unkeyed(cfg, row), _unaddressed(cfg, row)):
        if wrong:
            raise HTTPException(503, wrong[0])


def _urls(cfg: Config, house: str, call_id: str) -> dict:
    sig = _sig(cfg.secret, call_id)
    base = f"{cfg.public_url}/{house}/{call_id}"
    return {leg: f"{base}/{leg}?sig={sig}"
            for leg in ("answer", "gather", "speech", "status")}


# --------------------------------------------------------------------------- #
# what is remembered, and for how long
# --------------------------------------------------------------------------- #

#: The last line JIM handed back per call, for the branches that are the
#: sidecar's alone. In memory on purpose — see the module docstring.
_LINES: dict[str, tuple[dict, float]] = {}


def _remember(call_id: str, line: dict) -> None:
    stale = [c for c, (_, at) in _LINES.items() if time.time() - at > MAX_AGE]
    for c in stale:
        _LINES.pop(c, None)
    _LINES[call_id] = (line, time.time())


def _recall(call_id: str) -> dict | None:
    got = _LINES.get(call_id)
    if got is None:
        return None
    line, at = got
    if time.time() - at > MAX_AGE:
        _LINES.pop(call_id, None)
        return None
    return line


#: The standing probes, each believed for STANDING_CACHE_S.
_PROBES: dict[str, tuple[float, object]] = {}


def _probe(key: str, make, force: bool = False):
    known = _PROBES.get(key)
    if known and not force and time.time() - known[0] < STANDING_CACHE_S:
        return known[1]
    got = make()
    _PROBES[key] = (time.time(), got)
    return got


# --------------------------------------------------------------------------- #
# JIM's face
# --------------------------------------------------------------------------- #

class Limits(BaseModel):
    ring_seconds: int = Field(default=25, ge=5, le=600)
    max_call_seconds: int = Field(default=600, ge=30, le=14400)
    machine_detection: bool = True


class CallOrder(BaseModel):
    call_id: str = Field(min_length=1, max_length=80)
    to: str = Field(min_length=1, max_length=40)
    opening: str = ""
    language: str = "en"
    provider: str | None = None
    limits: Limits = Field(default_factory=Limits)


@app.get("/health")
def health() -> dict:
    """Whether this adapter could ring, as booleans. `keyed` rather than
    the key, `secret_set` rather than the secret: nothing here is a
    credential, the rule `film.health` follows."""
    cfg = _config()
    return {
        "ok": True,
        "provider": cfg.provider,
        "providers": sorted(HOUSES),
        "secret_set": bool(cfg.secret),
        "keyed": bool(cfg.token),
        "from_number_set": bool(cfg.from_),
        "public_url_set": bool(cfg.public_url),
        "public_url_well_formed": _public_url_well_formed(cfg.public_url),
    }


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@app.get("/standing")
def standing(request: Request, force: str = "", provider: str = "") -> dict:
    """The proof, not the promise: one authenticated round trip to the
    house, one GET of the public URL through the front door, and one
    probe of JIM's own door with this secret — each believed for a
    minute. Always 200 with a word; only a bad bearer is refused, because
    a posture read must never look like a transport fault."""
    cfg = _config()
    _require_bearer(cfg, request)
    forced = force.lower() in ("1", "true", "yes")
    out = {"word": "ready", "provider": cfg.provider, "authenticated": None,
           "from_number": bool(cfg.from_), "webhooks": None, "detail": "",
           "fix": None, "jim_secret_accepted": None, "checked_at": _now()}

    def settle(word: str, detail: str, fix: str | None) -> dict:
        out.update(word=word, detail=detail, fix=fix)
        out["jim_secret_accepted"] = _probe("jim", _jim_probe, forced)
        return out

    asked = provider.strip().lower()
    if cfg.provider not in HOUSES or (asked and asked != cfg.provider):
        other = asked or cfg.provider
        return settle(
            "mismatched",
            f"this adapter is keyed for {cfg.provider}, not {other}",
            "set JIM_TELEPHONY_PROVIDER to match" if asked else
            f"set JIM_TELEPHONY_PROVIDER to one of: "
            f"{', '.join(sorted(HOUSES))}")
    row = HOUSES[cfg.provider](cfg, _house_http)
    wrong = _unkeyed(cfg, row)
    if wrong:
        return settle("unkeyed", *wrong)
    wrong = _unaddressed(cfg, row)
    if wrong:
        return settle("unaddressed", *wrong)

    def house_probe():
        return (*row.standing(), _now())

    word, detail, at = _probe("house", house_probe, forced)
    out["checked_at"] = at
    out["authenticated"] = word == "ready"
    if word != "ready":
        fix = (detail if word in ("refused", "house_unreachable")
               else None)
        return settle(word, detail, fix)
    out["webhooks"] = _probe("ping", lambda: _ping(cfg), forced)
    if not out["webhooks"]:
        return settle(
            "webhooks_unreachable",
            f"{cfg.public_url}/ping did not answer through the front door",
            "the public URL does not answer through the front door — check "
            "the Caddy /voice route and JIM_VOICE_PUBLIC_URL, and that this "
            "host can reach its own public name")
    return settle("ready", f"{detail} at {at}", None)


def _ping(cfg: Config) -> bool:
    """Whether the box's own public name reaches this door: the path a
    webhook takes, walked from inside."""
    try:
        status, text = _house_http("GET", f"{cfg.public_url}/ping",
                                   headers={"Accept": "application/json"},
                                   timeout=PROBE_TIMEOUT)
    except houses.Unreachable:
        return False
    return status == 200 and bool(_json(text.encode()).get("voice"))


def _jim_probe() -> bool | None:
    """Whether JIM accepts this secret: a POST to an event door for a call
    JIM never minted, expecting its 404. A 401, 403 or 503 there means the
    two containers hold different secrets (or JIM has none); anything
    else is unknown."""
    status, _ = _ask("POST", "/reachout/call/rcl_probe/event",
                     {"event": "completed", "seconds": 0,
                      "detail": "standing probe"}, timeout=PROBE_TIMEOUT)
    if status == 404:
        return True
    if status in (401, 403, 503):
        return False
    return None


@app.post("/calls", status_code=201)
def calls(body: CallOrder, request: Request) -> dict:
    """Ring a person. The bearer first, then the emergency rule, then the
    provider match, then every variable the call needs — each refusal a
    sentence naming what to set — and only then the house."""
    cfg = _config()
    _require_bearer(cfg, request)
    to = normalize(body.to)
    if is_emergency(to):
        raise HTTPException(422, "this door does not ring emergency numbers")
    house = _house_name(cfg)
    asked = (body.provider or house).strip().lower()
    if asked != house:
        raise HTTPException(
            409, f"this adapter is keyed for {house}, not {asked} — set "
                 f"JIM_TELEPHONY_PROVIDER to match")
    if not _CALL_ID.match(body.call_id):
        raise HTTPException(422, "the call id is not one this door can "
                                 "carry in a URL")
    if not _E164.match(to):
        raise HTTPException(422, "the contact's channel is not a phone "
                                 "number this transport can dial")
    row = HOUSES[house](cfg, _house_http)
    _require_configured(cfg, row)
    urls = _urls(cfg, house, body.call_id)
    try:
        ref = row.create_call(to, cfg.from_, urls, body.limits.model_dump())
    except houses.Refused as exc:
        raise HTTPException(422, f"the house refused this number: {exc}") \
            from None
    except houses.NoCall:
        raise HTTPException(
            502, "the house answered without a call to follow") from None
    except houses.Answered as exc:
        raise HTTPException(
            502, f"the house answered {exc.code}"
                 + (f": {exc.detail}" if exc.detail else "")) from None
    except houses.Unreachable as exc:
        raise HTTPException(
            502, f"the house could not be reached: {exc}") from None
    except houses.Misconfigured as exc:
        raise HTTPException(503, str(exc)) from None
    # Nothing about this call is kept: the id and the sig ride the URLs.
    return {"placed": True, "provider": house, "provider_call_id": ref,
            "status": "queued"}


# --------------------------------------------------------------------------- #
# the house's face
# --------------------------------------------------------------------------- #

class Forbidden(Exception):
    """A vendor door refused: 403 with an empty body, logged with the house
    and the path, nothing posted to JIM, nothing spoken."""


@app.exception_handler(Forbidden)
async def _forbidden(request: Request, exc: Forbidden) -> Response:
    return Response(status_code=403)


@app.get("/voice/ping")
def ping() -> dict:
    """The public probe's target — what `/standing` fetches through the
    front door to prove the Caddy route and the public name."""
    return {"ok": True, "voice": True}


def _signed_url(cfg: Config, request: Request) -> str:
    """The URL the house signed: the public URL plus the path after
    `/voice` plus the query exactly as sent. Never `Host` and never
    `X-Forwarded-*` — Caddy terminates TLS, and a spoofed header must not
    help a forged webhook."""
    path = request.url.path
    tail = path[len("/voice"):] if path.startswith("/voice") else path
    query = request.scope.get("query_string", b"").decode("latin-1")
    return cfg.public_url + tail + (f"?{query}" if query else "")


async def _admit(house: str, call_id: str,
                 request: Request) -> tuple[House, Event]:
    """Both locks, before a field is read."""
    cfg = _config()
    if house not in HOUSES:
        raise HTTPException(404, "no such house")
    declared = request.headers.get("content-length") or "0"
    if not declared.isdigit() or int(declared) > MAX_BODY:
        raise HTTPException(413, "too large for a webhook")
    raw = await request.body()
    if len(raw) > MAX_BODY:
        raise HTTPException(413, "too large for a webhook")
    given = request.query_params.get("sig", "")
    if not cfg.secret or not given or not hmac.compare_digest(
            given.encode(), _sig(cfg.secret, call_id).encode()):
        log.warning("refused %s %s: the call capability did not match",
                    house, request.url.path)
        raise Forbidden()
    row = HOUSES[house](cfg, _house_http)
    headers = {k.lower(): v for k, v in request.headers.items()}
    if not row.verify(_signed_url(cfg, request), headers, raw):
        log.warning("refused %s %s: the house's signature did not verify",
                    house, request.url.path)
        raise Forbidden()
    return row, row.parse(headers, raw)


def _counter(request: Request, name: str, default: int = 0) -> int:
    try:
        return int(request.query_params.get(name, default))
    except (TypeError, ValueError):
        return default


def _line_from(status: int, body: dict) -> dict | None:
    """JIM's line envelope out of an answer, or None when there is none
    to speak from — a refusal, a 409, a 404, a silence."""
    line = body.get("line") if status == 200 else None
    if not isinstance(line, dict) or line.get("then") not in houses.THEN:
        return None
    return {"say": line.get("say") or "", "then": line["then"],
            "language": line.get("language") or "en",
            "again": line.get("again"), "close": line.get("close"),
            "trouble": line.get("trouble")}


def _play(row: House, call_id: str, line: dict, **counters) -> Response:
    """One line envelope, rendered in the house's dialect with the next
    leg's counters on its URLs."""
    cfg = row.cfg
    return row.render(line, _urls(cfg, row.name, call_id), counters)


def _hangup(row: House, call_id: str, say: str = "",
            language: str | None = None) -> Response:
    return _play(row, call_id, {"say": say, "then": "hangup",
                                "language": language or "en"})


def _trouble(row: House, call_id: str) -> Response:
    """JIM could not be reached, or would not answer: the remembered
    trouble line, or a bare hangup when there is nothing to speak."""
    cached = _recall(call_id) or {}
    return _hangup(row, call_id, cached.get("trouble") or "",
                   cached.get("language"))


def _speak(row: House, call_id: str, status: int, body: dict,
           **counters) -> Response:
    line = _line_from(status, body)
    if line is None:
        return _trouble(row, call_id)
    _remember(call_id, line)
    if line["then"] == "speak_first":
        return _play(row, call_id, line, first=1, turn=0)
    return _play(row, call_id, line, **counters)


# Every vendor door reads its body on the event loop and does the rest — the
# two locks are already checked by then — in a worker thread. The rest is
# blocking: a request to JIM that may itself place the next contact's call
# back through this door's POST /calls. On the loop, that round trip would
# wait on itself until both timeouts fired and the next leg read
# "unplaced" while the house rang it.

@app.post("/voice/{house}/{call_id}/answer")
async def answer(house: str, call_id: str, request: Request) -> Response:
    row, ev = await _admit(house, call_id, request)
    return await run_in_threadpool(_answer, row, ev, call_id)


def _answer(row: House, ev: Event, call_id: str) -> Response:
    """The far end picked up. A machine or a fax is hung up on before a
    word of health text is spoken, and JIM is told `voicemail`; a person
    is told JIM's opening and asked for a key."""
    who = (ev.answered_by or "").lower()
    if who.startswith(("machine", "fax")):
        _ask("POST", f"/reachout/call/{call_id}/event",
             {"event": "voicemail", "seconds": 0,
              "detail": ev.detail or f"AnsweredBy={who}"})
        return _hangup(row, call_id)
    status, body = _ask("POST", f"/reachout/call/{call_id}/event",
                        {"event": "answered", "seconds": 0,
                         "detail": ev.detail or f"AnsweredBy={who or 'human'}"})
    line = _line_from(status, body)
    if line is None:
        # No line yet to draw a trouble phrase from; the status callback
        # still decides the leg.
        return _hangup(row, call_id)
    _remember(call_id, line)
    return _play(row, call_id, line, **{"try": 1})


def _consent(row: House, call_id: str, digit: str) -> Response:
    status, body = _ask("POST", f"/reachout/call/{call_id}/consent",
                        {"digit": digit})
    return _speak(row, call_id, status, body, **{"try": 1})


@app.post("/voice/{house}/{call_id}/gather")
async def gather(house: str, call_id: str, request: Request) -> Response:
    row, ev = await _admit(house, call_id, request)
    return await run_in_threadpool(_gather, row, ev, call_id,
                                   _counter(request, "try", 1))


def _gather(row: House, ev: Event, call_id: str, attempt: int) -> Response:
    """The keypad choice. 1 and 2 go to JIM at once; anything else gets
    one re-prompt from the remembered line (try=2) before it is sent as
    pressed — a mis-press is not an opt-out."""
    digit = (ev.digit or "").strip()
    if digit in ("1", "2"):
        return _consent(row, call_id, digit)
    if attempt < 2:
        cached = _recall(call_id)
        if cached and cached.get("again"):
            return _play(row, call_id,
                         {**cached, "say": cached["again"],
                          "then": "gather_digit"}, **{"try": 2})
    return _consent(row, call_id, digit)


def _say(row: House, call_id: str, heard: str, turn: int) -> Response:
    status, body = _ask("POST", f"/reachout/call/{call_id}/say",
                        {"heard": heard}, timeout=SAY_TIMEOUT)
    return _speak(row, call_id, status, body, silence=0, turn=turn + 1)


@app.post("/voice/{house}/{call_id}/speech")
async def speech(house: str, call_id: str, request: Request) -> Response:
    row, ev = await _admit(house, call_id, request)
    return await run_in_threadpool(
        _speech, row, ev, call_id, _counter(request, "first", 0),
        _counter(request, "silence", 0), _counter(request, "turn", 0))


def _speech(row: House, ev: Event, call_id: str, first: int, silence: int,
            turn: int) -> Response:
    """The conversation. `first=1` is the leg after consent, where JIM
    speaks before the contact has said anything; a spoken answer goes to
    JIM as heard; a silence gets one prompt from the remembered line and
    a second silence the closing."""
    heard = (ev.speech or "").strip()
    if first or heard:
        return _say(row, call_id, "" if first else heard, turn)
    cached = _recall(call_id)
    if cached is None:
        # Restart amnesia: ask JIM rather than invent a phrase.
        return _say(row, call_id, "", turn)
    if silence < 1 and cached.get("again"):
        return _play(row, call_id,
                     {**cached, "say": cached["again"],
                      "then": "gather_speech"}, silence=1, turn=turn)
    return _hangup(row, call_id, cached.get("close") or "",
                   cached.get("language"))


@app.post("/voice/{house}/{call_id}/status")
async def status_callback(house: str, call_id: str,
                          request: Request) -> Response:
    row, ev = await _admit(house, call_id, request)
    return await run_in_threadpool(_status, row, ev, call_id)


def _status(row: House, ev: Event, call_id: str) -> Response:
    """How the call ended, in JIM's words. 204 once JIM has heard it —
    whatever JIM decided, including `already`, and including a 404 for a
    call JIM never minted. A 502 only when JIM did not hear it at all
    (unreachable, or a 5xx), so a house that retries retries into an
    idempotent door rather than losing the word. JIM decides reached or
    unreached; this door decides nothing."""
    if ev.status is None:
        return Response(status_code=204)
    status, _ = _ask("POST", f"/reachout/call/{call_id}/event",
                     {"event": ev.status, "seconds": int(ev.seconds or 0),
                      "detail": ev.detail})
    _LINES.pop(call_id, None)
    if not status or status >= 500:
        return Response(status_code=502)
    return Response(status_code=204)
