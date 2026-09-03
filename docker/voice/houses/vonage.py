"""Vonage — JSON both ways.

The call is started with a JSON POST under a JWT this row mints itself:
RS256, signed with the application's private key (``VOICE_TOKEN`` holds
the PEM, or ``VOICE_TOKEN_FILE`` a path to it), claiming the application
id in ``VOICE_ACCOUNT``. What the line does next is an NCCO — a JSON list
of actions: ``talk``, ``input`` (dtmf or speech), and ``notify``, which
posts to a URL and takes the answer as the next NCCO and so stands in
for a redirect, which NCCO does not have. An NCCO that ends ends the
call, which is how ``hangup`` is said.

Webhooks carry a JWT of their own in ``Authorization``: HS256 under the
signature secret in ``VOICE_WEBHOOK_KEY``, with a ``payload_hash`` claim
that has to equal the SHA-256 of the raw body — a signature that covers
the bytes and not only the door.

The credential check is ``GET /v1/calls?page_size=1`` under the minted
JWT rather than the account balance: the balance door takes the account
API key and secret, which this sidecar deliberately does not hold, and a
round trip proven with a credential you do not have proves nothing.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import time

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from fastapi import Response

from . import (Answered, Event, House, Misconfigured, NoCall, Refused,
               Unreachable, action_urls, as_int, b64url, b64url_decode,
               json_body)

#: Vonage's event statuses, in JIM's words. Everything else (started,
#: ringing, answered, human, input, record) is not the end of the call.
STATUS_WORDS = {
    "completed": "completed", "busy": "busy", "unanswered": "no-answer",
    "timeout": "no-answer", "failed": "failed", "rejected": "busy",
    "cancelled": "canceled", "canceled": "canceled", "machine": "voicemail",
}


class Vonage(House):
    name = "vonage"
    api = "https://api.nexmo.com"
    account_means = "application id"
    token_means = "private key (PEM)"
    webhook_key_means = "signature secret"
    plus = False

    def _jwt(self) -> str:
        try:
            key = serialization.load_pem_private_key(
                self.cfg.token.encode(), password=None)
        except (ValueError, TypeError) as exc:
            raise Misconfigured(
                "VOICE_TOKEN is not a PEM private key for vonage — set "
                "JIM_VOICE_TOKEN to the application's private key, the "
                "PEM's full text (the compose template forwards that one "
                "variable; VOICE_TOKEN_FILE is for a mounted file)") from exc
        now = int(time.time())
        head = b64url(json.dumps({"alg": "RS256", "typ": "JWT"}).encode())
        claims = b64url(json.dumps({
            "application_id": self.cfg.account, "iat": now, "exp": now + 300,
            "jti": secrets.token_hex(8)}).encode())
        signing = f"{head}.{claims}"
        signature = key.sign(signing.encode(), padding.PKCS1v15(),
                             hashes.SHA256())
        return f"{signing}.{b64url(signature)}"

    def _headers(self, content: str | None = None) -> dict:
        got = {"Authorization": f"Bearer {self._jwt()}",
               "Accept": "application/json"}
        if content:
            got["Content-Type"] = content
        return got

    def create_call(self, to: str, from_: str, urls: dict,
                    limits: dict) -> str:
        body = {
            "to": [{"type": "phone", "number": self.number(to)}],
            "from": {"type": "phone", "number": self.number(from_)},
            "answer_url": [urls["answer"]],
            "answer_method": "POST",
            "event_url": [urls["status"]],
            "event_method": "POST",
            "ringing_timer": int(limits.get("ring_seconds", 25)),
            "length_timer": int(limits.get("max_call_seconds", 600)),
        }
        if limits.get("machine_detection", True):
            body["machine_detection"] = "hangup"
        status, text = self.http(
            "POST", f"{self.base}/v1/calls",
            headers=self._headers("application/json"),
            body=json.dumps(body).encode())
        got = json_body(text)
        words = " ".join(str(x) for x in (
            got.get("title") or got.get("error_title"),
            got.get("detail") or got.get("error")) if x) or text[:400]
        if status == 400:
            raise Refused(words)
        if not 200 <= status < 300:
            raise Answered(status, words)
        uuid = got.get("uuid")
        if not uuid:
            raise NoCall()
        return str(uuid)

    def verify(self, signed_url: str, headers: dict, raw_body: bytes) -> bool:
        auth = headers.get("authorization") or ""
        if not auth.lower().startswith("bearer ") or not self.cfg.webhook_key:
            return False
        parts = auth[7:].strip().split(".")
        if len(parts) != 3:
            return False
        try:
            head = json_body(b64url_decode(parts[0]))
            if head.get("alg") != "HS256":
                return False
            want = hmac.new(self.cfg.webhook_key.encode(),
                            f"{parts[0]}.{parts[1]}".encode(),
                            hashlib.sha256).digest()
            if not hmac.compare_digest(want, b64url_decode(parts[2])):
                return False
            claims = json_body(b64url_decode(parts[1]))
        except (ValueError, TypeError):
            return False
        # A signed webhook is good for minutes, not forever: a captured one
        # must not replay a day later.
        now = time.time()
        try:
            iat = float(claims.get("iat") or 0)
            exp = float(claims.get("exp") or 0)
        except (TypeError, ValueError):
            return False
        if not iat or abs(now - iat) > 300:
            return False
        if exp and exp < now - 60:
            return False
        given = str(claims.get("payload_hash") or "")
        return hmac.compare_digest(given.encode(),
                                   hashlib.sha256(raw_body).hexdigest().encode())

    def parse(self, headers: dict, raw_body: bytes) -> Event:
        body = json_body(raw_body)
        dtmf = body.get("dtmf")
        speech = body.get("speech")
        payload = body.get("payload")
        raw = str(body.get("status") or "")
        status = STATUS_WORDS.get(raw.lower())
        digit = text = None
        if isinstance(dtmf, dict):
            digit = str(dtmf.get("digits") or "")
            kind = "digit"
        elif isinstance(speech, dict):
            results = speech.get("results") or []
            first = results[0] if results and isinstance(results[0], dict) \
                else {}
            text = str(first.get("text") or "")
            kind = "speech"
        elif isinstance(payload, dict) and payload.get("leg") == "speech":
            kind = "speech"
        elif raw:
            kind = "status"
        else:
            kind = "answer"
        answered_by = ("machine" if raw.lower() == "machine"
                       else "human" if kind == "answer" else None)
        detail = ";".join(f"{k}={body[k]}" for k in ("status", "detail",
                                                      "reason")
                          if body.get(k) not in (None, ""))
        return Event(kind=kind, digit=digit, speech=text, status=status,
                     answered_by=answered_by,
                     seconds=as_int(body.get("duration")),
                     vendor_ref=str(body.get("uuid") or "") or None,
                     detail=detail,
                     caller=str(body.get("from") or "") or None,
                     called=str(body.get("to") or "") or None)

    def render(self, line: dict, urls: dict, counters: dict) -> Response:
        act = action_urls(urls, counters)
        say = (line.get("say") or "").strip()
        then = line.get("then")
        lang = self.lang(line.get("language"))
        ncco: list[dict] = []
        if say:
            talk = {"action": "talk", "text": say, "language": lang}
            if then in ("gather_digit", "gather_speech"):
                talk["bargeIn"] = True
            ncco.append(talk)
        if then == "gather_digit":
            ncco.append({"action": "input", "type": ["dtmf"],
                         "dtmf": {"maxDigits": 1, "timeOut": 7},
                         "eventUrl": [act["gather"]], "eventMethod": "POST"})
        elif then == "speak_first":
            ncco.append({"action": "notify", "payload": {"leg": "speech"},
                         "eventUrl": [act["speech"]], "eventMethod": "POST"})
        elif then == "gather_speech":
            ncco.append({"action": "input", "type": ["speech"],
                         "speech": {"language": lang, "endOnSilence": 1.5},
                         "eventUrl": [act["speech"]], "eventMethod": "POST"})
        # hangup: the NCCO ends, and with it the call.
        return Response(json.dumps(ncco), media_type="application/json")

    def standing(self) -> tuple[str, str]:
        try:
            status, text = self.http("GET", f"{self.base}/v1/calls?page_size=1",
                                     headers=self._headers(), timeout=3)
        except Misconfigured as exc:
            return "unkeyed", str(exc)
        except Unreachable as exc:
            return "house_unreachable", f"the house could not be reached: {exc}"
        if 200 <= status < 300:
            return "ready", (f"the house answered for application "
                             f"{self.masked_account()}")
        return self.standing_word(status, text)
