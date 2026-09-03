"""The houses — one row per phone company, and the whole of what is
vendor-specific about ringing a person.

``server.py`` next door speaks one shape: JIM's line envelope in, a
spoken prompt with a keypad or a spoken answer out, and one of six words
for how the call ended. No phone company speaks that. Each has its own
REST call to start a call, its own markup for what the line should do
next (TwiML, cXML, TeXML, Plivo XML, NCCO), its own webhook parameters,
its own way of signing those webhooks, and its own vocabulary for
``busy``. This package is where those differences live, and stop.

    asked     which phone company rings the contact
    mattered  that the answer is a row here, never a branch upstream

The rows follow the film sidecar's ``MODELS`` discipline, widened from
one string to six methods: ``create_call``, ``verify``, ``parse``,
``render``, ``standing`` and ``lang``. A base URL is overridable by
``VOICE_<HOUSE>_API`` and a language tag by ``VOICE_LANG_<XX>`` because
those are somebody else's strings and they rename them. :data:`HOUSES`
is the only place the five names appear; JIM's ``dialer.PROVIDERS`` is
the same set, and a test in this repository holds the two equal.

Every row maps its own terminal words onto JIM's six — ``answered`` for a
pickup, then ``completed | voicemail | no-answer | busy | failed |
canceled`` — inside :meth:`House.parse`, so the cascade only ever sees
its own vocabulary. And every row's :meth:`House.verify` checks the
house's own signature over the URL the house actually signed; there is
no switch to turn that off, and a row that cannot verify (no key
configured) refuses rather than trusts.

Nothing here opens a socket. A row is handed the one HTTP function
``server.py`` owns and calls it; tests hand in a fake and read what the
row would have sent.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import urllib.parse
from dataclasses import dataclass
from typing import Callable
from xml.sax.saxutils import escape

from fastapi import Response

#: JIM's words for how a leg ended — the only vocabulary the cascade hears.
TERMINAL = ("completed", "voicemail", "no-answer", "busy", "failed",
            "canceled")

#: The four things JIM's line envelope may ask the line to do next.
THEN = ("gather_digit", "speak_first", "gather_speech", "hangup")

#: JIM's language codes, in the tag each house's speech engine takes.
#: Overridable one at a time — ``VOICE_LANG_EN=en-GB`` beats the row —
#: for the same reason a model id is: a tag is the house's string.
LANG = {
    "en": "en-US", "es": "es-ES", "fr": "fr-FR", "de": "de-DE",
    "pt": "pt-BR", "it": "it-IT", "ja": "ja-JP", "zh": "zh-CN",
    "hi": "hi-IN", "ar": "ar-XA",
}


def lang_tag(code: str | None) -> str:
    code = (code or "en").strip().lower()[:2] or "en"
    named = os.environ.get(f"VOICE_LANG_{code.upper()}", "").strip()
    return named or LANG.get(code, LANG["en"])


# --------------------------------------------------------------------------- #
# what a row can say went wrong, in the product's words
# --------------------------------------------------------------------------- #

class HouseError(Exception):
    """A row could not do what it was asked; ``server.py`` turns each kind
    into the status JIM expects."""


class Refused(HouseError):
    """The house would not ring this number — invalid, unroutable, or
    unverified on a trial account. A 422 upstream, quoting the house."""


class Answered(HouseError):
    """The house answered something other than a call: a 401, a 5xx.
    A 502 upstream, echoing the status so an operator goes to the right
    place."""

    def __init__(self, code: int, detail: str = ""):
        super().__init__(detail)
        self.code = code
        self.detail = detail


class Unreachable(HouseError):
    """The house could not be reached at all: DNS, a refused connection,
    a timeout. A 502 upstream with the reason."""


class NoCall(HouseError):
    """The house said yes and named no call to follow."""


class Misconfigured(HouseError):
    """A credential is present and unusable — a PEM that is not a PEM.
    A 503 upstream, naming the variable."""


# --------------------------------------------------------------------------- #
# the shapes the rows take in and hand back
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class Config:
    """The sidecar's environment, read once per request so a test's
    ``monkeypatch.setenv`` is seen. Never printed."""
    provider: str
    secret: str
    jim_url: str
    public_url: str
    from_: str
    account: str
    token: str
    webhook_key: str
    house_ref: str


@dataclass
class Event:
    """One webhook, in the product's words.

    ``status`` is one of :data:`TERMINAL` or None when the event is not
    the end of the call (ringing, initiated, answered) — the status door
    posts nothing to JIM for those. ``answered_by`` starts with
    ``machine`` or ``fax`` when the house's detection says so.
    """
    kind: str = "answer"
    digit: str | None = None
    speech: str | None = None
    status: str | None = None
    answered_by: str | None = None
    seconds: int = 0
    vendor_ref: str | None = None
    detail: str = ""
    #: On a call that came in: who is calling, and which number they rang.
    caller: str | None = None
    called: str | None = None


#: The one HTTP function a row is handed: ``(method, url, *, headers,
#: body, timeout) -> (status, text)``; raises :class:`Unreachable`.
Http = Callable[..., tuple[int, str]]


def action_urls(urls: dict, counters: dict) -> dict:
    """The callback URLs with this leg's counters on them.

    The sidecar keeps no state per call: which try this is, whether one
    silence has already passed, and which turn of the conversation comes
    next all ride the URL the house will post back to.
    """
    out = dict(urls)
    out["gather"] = f'{urls["gather"]}&try={int(counters.get("try", 1))}'
    turn = int(counters.get("turn", 0))
    if counters.get("first"):
        out["speech"] = f'{urls["speech"]}&first=1&turn={turn}'
    else:
        out["speech"] = (f'{urls["speech"]}&silence='
                         f'{int(counters.get("silence", 0))}&turn={turn}')
    return out


def form(raw_body: bytes) -> dict[str, str]:
    """A form-encoded body as one value per field, blanks kept — a
    ``Digits=`` with nothing after it is the house saying nobody pressed
    anything, which is different from the field being absent."""
    parsed = urllib.parse.parse_qs(raw_body.decode("utf-8", "replace"),
                                   keep_blank_values=True)
    return {k: v[0] for k, v in parsed.items() if v}


def json_body(raw_body: bytes | str) -> dict:
    """A JSON body as a dict, and an empty dict for anything else."""
    try:
        got = json.loads(raw_body or b"{}")
    except (ValueError, TypeError):
        return {}
    return got if isinstance(got, dict) else {}


def basic_auth(user: str, password: str) -> str:
    return "Basic " + base64.b64encode(f"{user}:{password}".encode()).decode()


def b64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def b64url_decode(text: str) -> bytes:
    text = text.strip()
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def attr(value: str) -> str:
    """A URL as an XML attribute value: ``&try=1`` has to read
    ``&amp;try=1`` or the document is not XML."""
    return escape(value, {'"': "&quot;"})


def as_int(value) -> int:
    try:
        return int(float(value or 0))
    except (TypeError, ValueError):
        return 0


def twilio_signature(token: str, url: str, params: dict) -> str:
    """Twilio's scheme, which SignalWire shares: base64 of an HMAC-SHA1
    with the auth token over the URL as the house signed it followed by
    every POST field, sorted by name, name and value run together."""
    tail = "".join(k + v for k in sorted(params)
                   for v in sorted(params[k] if isinstance(params[k], list)
                                   else [params[k]]))
    digest = hmac.new(token.encode(), (url + tail).encode(),
                      hashlib.sha1).digest()
    return base64.b64encode(digest).decode()


# --------------------------------------------------------------------------- #
# the interface
# --------------------------------------------------------------------------- #

class House:
    """One phone company, as six methods.

    Class attributes say what the credential slots mean at this house, so
    a refusal can name them: ``account_means`` None means the house has no
    account id (Telnyx keys alone), ``house_ref_means`` set means the
    house needs a routing handle (a SignalWire space, a TeXML application),
    ``webhook_key_means`` set means webhooks are verified with something
    other than the token (a Telnyx public key, a Vonage signature secret).
    """

    name = ""
    #: The default base URL; ``VOICE_<NAME>_API`` beats it.
    api = ""
    account_means: str | None = "account SID"
    token_means = "auth token"
    house_ref_means: str | None = None
    webhook_key_means: str | None = None
    #: Whether this house dials E.164 with the plus, or bare digits.
    plus = True

    def __init__(self, cfg: Config, http: Http):
        self.cfg = cfg
        self.http = http

    @property
    def base(self) -> str:
        named = os.environ.get(f"VOICE_{self.name.upper()}_API", "").strip()
        return (named or self.api).rstrip("/")

    def lang(self, code: str | None) -> str:
        """The house's tag for one of JIM's language codes."""
        return lang_tag(code)

    def number(self, e164: str) -> str:
        return e164 if self.plus else e164.lstrip("+")

    def masked_account(self) -> str:
        """The account, masked to its last four — the only form it is
        ever reported in."""
        return "..." + self.cfg.account[-4:]

    # -- the six --------------------------------------------------------------

    def create_call(self, to: str, from_: str, urls: dict,
                    limits: dict) -> str:
        """Start the call; answer the house's id for it."""
        raise NotImplementedError

    def verify(self, signed_url: str, headers: dict, raw_body: bytes) -> bool:
        """Whether this webhook was signed by the house, over the URL the
        house actually posted to. False when nothing to check with."""
        raise NotImplementedError

    def parse(self, headers: dict, raw_body: bytes) -> Event:
        """The webhook, in the product's words."""
        raise NotImplementedError

    def render(self, line: dict, urls: dict, counters: dict) -> Response:
        """JIM's line envelope, in the house's dialect."""
        raise NotImplementedError

    def standing(self) -> tuple[str, str]:
        """One cheap authenticated round trip: ``(word, detail)`` with the
        word one of ready | refused | house_unreachable."""
        raise NotImplementedError

    def inbound_pointed(self, voice_url: str) -> bool | None:
        """Whether the From number is pointed at the inbound door. None —
        the default — means this house cannot be asked, and the runbook's
        curl is the proof."""
        return None

    # -- shared readings of a house's answer ---------------------------------

    def standing_word(self, status: int, text: str = "") -> tuple[str, str]:
        if 200 <= status < 300:
            return "ready", (f"the house answered for account "
                             f"{self.masked_account()}")
        if status in (401, 403):
            return "refused", (f"the house answered {status} — the auth "
                               "token is wrong")
        if status == 404:
            return "refused", ("the house answered 404 — the account id is "
                               "not one the house knows")
        return "house_unreachable", f"the house answered {status}"


#: The table. A name here is a file in this directory and a row in JIM's
#: ``dialer.PROVIDERS``; nothing upstream lists them twice.
HOUSES: dict[str, type[House]] = {}

from . import twilio, signalwire, telnyx, plivo, vonage  # noqa: E402

for _row in (twilio.Twilio, signalwire.SignalWire, telnyx.Telnyx,
             plivo.Plivo, vonage.Vonage):
    HOUSES[_row.name] = _row
