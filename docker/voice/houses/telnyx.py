"""Telnyx — TeXML, which is TwiML with a different front door.

The markup and the webhook fields are Twilio's dialect, so ``render`` and
``parse`` are inherited. What differs: the call is started with a JSON
POST to the TeXML application named by ``VOICE_HOUSE_REF`` under a bearer
API key (no account id); the credential check is ``GET /v2/whoami``; and
webhooks are signed with Ed25519 rather than an HMAC — the house's public
key, pasted from its portal into ``VOICE_WEBHOOK_KEY``, verifies
``telnyx-signature-ed25519`` over ``"{telnyx-timestamp}|{raw body}"``,
and a timestamp more than five minutes from now is refused whatever the
signature says, so a captured webhook cannot be replayed later.
"""

from __future__ import annotations

import base64
import json
import time

from cryptography.hazmat.primitives.asymmetric import ed25519

from . import Answered, NoCall, Refused, Unreachable, json_body
from .twilio import Twilio


class Telnyx(Twilio):
    name = "telnyx"
    api = "https://api.telnyx.com"
    account_means = None
    token_means = "API key"
    house_ref_means = "TeXML application id"
    webhook_key_means = "Telnyx public key"
    #: How far a webhook's timestamp may sit from this clock, in seconds.
    SKEW = 300

    def _auth(self) -> str:
        return f"Bearer {self.cfg.token}"

    def create_call(self, to: str, from_: str, urls: dict,
                    limits: dict) -> str:
        body = {
            "To": self.number(to),
            "From": self.number(from_),
            "Url": urls["answer"],
            "UrlMethod": "POST",
            "StatusCallback": urls["status"],
            "StatusCallbackMethod": "POST",
            "StatusCallbackEvent": "completed",
            "Timeout": int(limits.get("ring_seconds", 25)),
            "TimeLimit": int(limits.get("max_call_seconds", 600)),
        }
        if limits.get("machine_detection", True):
            body["MachineDetection"] = "Enable"
        status, text = self.http(
            "POST", f"{self.base}/v2/texml/calls/{self.cfg.house_ref}",
            headers=self._headers("application/json"),
            body=json.dumps(body).encode(), timeout=10)
        got = json_body(text)
        data = got.get("data") if isinstance(got.get("data"), dict) else {}
        if status in (400, 422):
            errors = got.get("errors") or []
            first = errors[0] if errors and isinstance(errors[0], dict) else {}
            words = " ".join(str(x) for x in (
                first.get("code"), first.get("detail") or first.get("title"))
                if x)
            raise Refused(words or text[:400])
        if not 200 <= status < 300:
            raise Answered(status, text[:400])
        sid = (data.get("sid") or data.get("call_sid") or got.get("sid")
               or got.get("call_sid"))
        if not sid:
            raise NoCall()
        return str(sid)

    def verify(self, signed_url: str, headers: dict, raw_body: bytes) -> bool:
        given = headers.get("telnyx-signature-ed25519")
        stamp = headers.get("telnyx-timestamp")
        if not given or not stamp or not self.cfg.webhook_key:
            return False
        try:
            at = int(stamp)
        except ValueError:
            return False
        if abs(time.time() - at) > self.SKEW:
            return False
        try:
            key = ed25519.Ed25519PublicKey.from_public_bytes(
                base64.b64decode(self.cfg.webhook_key))
            key.verify(base64.b64decode(given),
                       f"{stamp}|".encode() + raw_body)
        except Exception:
            return False
        return True

    def standing(self) -> tuple[str, str]:
        try:
            status, text = self.http("GET", f"{self.base}/v2/whoami",
                                     headers=self._headers(), timeout=3)
        except Unreachable as exc:
            return "house_unreachable", f"the house could not be reached: {exc}"
        if 200 <= status < 300:
            data = json_body(text).get("data") or {}
            ref = str(data.get("organization_id") or data.get("user_id")
                      or "") if isinstance(data, dict) else ""
            return "ready", (f"the house answered for organization "
                             f"...{ref[-4:]}" if ref else "the house answered")
        return self.standing_word(status, text)
