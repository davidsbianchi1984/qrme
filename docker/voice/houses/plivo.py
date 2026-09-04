"""Plivo — its own XML, its own field names, the same six words.

The call is started with a JSON POST under basic auth (auth id, auth
token); the answer and hangup webhooks are form-encoded; what the line
does next is Plivo's markup — ``<GetInput>`` for a keypad press or a
spoken answer, ``<Speak>``, ``<Redirect>``, ``<Hangup/>``. ``<GetInput>``
has no equivalent of TwiML's ``actionOnEmptyResult``, so a ``<Redirect>``
to the same action follows it: an unanswered prompt still reaches the
door with an empty field, which is what the re-prompt keys on.

Webhooks carry ``X-Plivo-Signature-V2``: base64 of an HMAC-SHA256 with
the auth token over the URL and the ``X-Plivo-Signature-V2-Nonce``. The
house's published V2 scheme signs the URL without its query string (the
SDK's ``validate_v2_signature`` strips it); the design text names the
full URL. Both are the same secret's proof over the same door, so both
are accepted — the runbook's capture step confirms which one the house
sends before a box relies on it.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import urllib.parse

from fastapi import Response

from . import (Answered, Event, House, NoCall, Refused, Unreachable,
               action_urls, attr, as_int, basic_auth, escape, form,
               json_body)

#: Plivo's hangup ``CallStatus`` values, in JIM's words.
STATUS_WORDS = {
    "completed": "completed", "busy": "busy", "no-answer": "no-answer",
    "timeout": "no-answer", "failed": "failed", "cancel": "canceled",
    "canceled": "canceled",
}


class Plivo(House):
    name = "plivo"
    api = "https://api.plivo.com"
    account_means = "auth id"
    token_means = "auth token"
    plus = False

    def _headers(self, content: str | None = None) -> dict:
        got = {"Authorization": basic_auth(self.cfg.account, self.cfg.token),
               "Accept": "application/json"}
        if content:
            got["Content-Type"] = content
        return got

    def create_call(self, to: str, from_: str, urls: dict,
                    limits: dict) -> str:
        body = {
            "to": self.number(to),
            "from": self.number(from_),
            "answer_url": urls["answer"],
            "answer_method": "POST",
            "hangup_url": urls["status"],
            "hangup_method": "POST",
            "ring_timeout": int(limits.get("ring_seconds", 25)),
            "time_limit": int(limits.get("max_call_seconds", 600)),
        }
        if limits.get("machine_detection", True):
            body["machine_detection"] = "hangup"
            body["machine_detection_time"] = 8000
        status, text = self.http(
            "POST", f"{self.base}/v1/Account/{self.cfg.account}/Call/",
            headers=self._headers("application/json"),
            body=json.dumps(body).encode(), timeout=10)
        got = json_body(text)
        if status == 400:
            raise Refused(str(got.get("error") or text[:400]))
        if not 200 <= status < 300:
            raise Answered(status, str(got.get("error") or text[:400]))
        ref = got.get("request_uuid")
        if not ref:
            raise NoCall()
        return str(ref)

    def verify(self, signed_url: str, headers: dict, raw_body: bytes) -> bool:
        given = headers.get("x-plivo-signature-v2")
        nonce = headers.get("x-plivo-signature-v2-nonce")
        if not given or not nonce or not self.cfg.token:
            return False
        parts = urllib.parse.urlsplit(signed_url)
        bare = urllib.parse.urlunsplit(
            (parts.scheme, parts.netloc, parts.path, "", ""))
        for url in (bare, signed_url):
            want = base64.b64encode(hmac.new(
                self.cfg.token.encode(), (url + nonce).encode(),
                hashlib.sha256).digest()).decode()
            if hmac.compare_digest(want.encode(), given.encode()):
                return True
        return False

    def parse(self, headers: dict, raw_body: bytes) -> Event:
        f = form(raw_body)
        machine = (f.get("Machine") or "").strip().lower() == "true"
        status = STATUS_WORDS.get((f.get("CallStatus") or "").lower())
        if status and machine:
            # The house hung up on a machine itself; the leg is voicemail.
            status = "voicemail"
        if "Digits" in f:
            kind = "digit"
        elif "Speech" in f:
            kind = "speech"
        elif status:
            kind = "status"
        else:
            kind = "answer"
        answered_by = ("machine" if machine
                       else "human" if kind == "answer" else None)
        detail = ";".join(f"{k}={f[k]}" for k in
                          ("CallStatus", "HangupCauseName", "HangupCause",
                           "Machine") if f.get(k))
        return Event(kind=kind, digit=f.get("Digits"), speech=f.get("Speech"),
                     status=status, answered_by=answered_by,
                     seconds=as_int(f.get("Duration")),
                     vendor_ref=f.get("CallUUID"), detail=detail)

    def render(self, line: dict, urls: dict, counters: dict) -> Response:
        act = action_urls(urls, counters)
        say = (line.get("say") or "").strip()
        then = line.get("then")
        lang = self.lang(line.get("language"))
        speak = f'<Speak language="{lang}">{escape(say)}</Speak>' if say else ""
        parts = ['<?xml version="1.0" encoding="UTF-8"?>', "<Response>"]
        if then == "gather_digit":
            parts.append(
                f'<GetInput action="{attr(act["gather"])}" method="POST" '
                f'inputType="dtmf" numDigits="1" executionTimeout="7" '
                f'redirect="true">{speak}</GetInput>')
            parts.append(f'<Redirect method="POST">{escape(act["gather"])}'
                         f'</Redirect>')
        elif then == "speak_first":
            parts.append(speak)
            parts.append(f'<Redirect method="POST">{escape(act["speech"])}'
                         f'</Redirect>')
        elif then == "gather_speech":
            parts.append(speak)
            parts.append(
                f'<GetInput action="{attr(act["speech"])}" method="POST" '
                f'inputType="speech" executionTimeout="6" language="{lang}" '
                f'redirect="true"/>')
            parts.append(f'<Redirect method="POST">{escape(act["speech"])}'
                         f'</Redirect>')
        else:
            parts.append(speak)
            parts.append("<Hangup/>")
        parts.append("</Response>")
        return Response("".join(parts), media_type="application/xml")

    def standing(self) -> tuple[str, str]:
        try:
            status, text = self.http(
                "GET", f"{self.base}/v1/Account/{self.cfg.account}/",
                headers=self._headers(), timeout=3)
        except Unreachable as exc:
            return "house_unreachable", f"the house could not be reached: {exc}"
        return self.standing_word(status, text)
