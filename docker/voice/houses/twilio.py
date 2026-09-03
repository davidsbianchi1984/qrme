"""Twilio — the default row, and the one smoke-tested live this round.

The call is started with one form-encoded POST to the REST API under
HTTP basic auth; every webhook comes back form-encoded and signed with
``X-Twilio-Signature``, an HMAC-SHA1 with the auth token over the URL the
house posted to followed by the sorted POST fields; and what the line
does next is TwiML. SignalWire's cXML and Telnyx's TeXML are dialects of
that markup, which is why those two rows subclass this one.

Machine detection is asked for at placement (``MachineDetection=Enable``)
and reported in the answer webhook's ``AnsweredBy``, which is the one
field the sidecar reads before it lets JIM's opening be spoken: an
opening names the person and the concern, and it is never spoken into a
voicemail.
"""

from __future__ import annotations

import hmac
import urllib.parse

from fastapi import Response

from . import (Answered, Event, House, NoCall, Refused, Unreachable,
               action_urls, attr, as_int, basic_auth, escape, form,
               json_body, twilio_signature)

#: Twilio's terminal ``CallStatus`` values, in JIM's words. Everything
#: else (queued, initiated, ringing, in-progress) is not the end of the
#: call and posts nothing.
STATUS_WORDS = {
    "completed": "completed", "busy": "busy", "no-answer": "no-answer",
    "failed": "failed", "canceled": "canceled",
}


class Twilio(House):
    name = "twilio"
    api = "https://api.twilio.com/2010-04-01"
    account_means = "account SID"
    token_means = "auth token"
    #: The header carrying the house's signature; SignalWire has its own.
    signature_headers = ("x-twilio-signature",)

    def _auth(self) -> str:
        return basic_auth(self.cfg.account, self.cfg.token)

    def _headers(self, content: str | None = None) -> dict:
        got = {"Authorization": self._auth(), "Accept": "application/json"}
        if content:
            got["Content-Type"] = content
        return got

    # -- create_call ----------------------------------------------------------

    def create_call(self, to: str, from_: str, urls: dict,
                    limits: dict) -> str:
        fields = {
            "To": self.number(to),
            "From": self.number(from_),
            "Url": urls["answer"],
            "Method": "POST",
            "StatusCallback": urls["status"],
            "StatusCallbackMethod": "POST",
            # The final callback carries completed | busy | no-answer |
            # failed | canceled; initiated and ringing are noise.
            "StatusCallbackEvent": "completed",
            "Timeout": str(int(limits.get("ring_seconds", 25))),
            "TimeLimit": str(int(limits.get("max_call_seconds", 600))),
        }
        if limits.get("machine_detection", True):
            fields["MachineDetection"] = "Enable"
            fields["MachineDetectionTimeout"] = "8"
        status, text = self.http(
            "POST", f"{self.base}/Accounts/{self.cfg.account}/Calls.json",
            headers=self._headers("application/x-www-form-urlencoded"),
            body=urllib.parse.urlencode(fields).encode())
        return self._placed(status, text)

    def _placed(self, status: int, text: str) -> str:
        got = json_body(text)
        if status == 400:
            # 21211 invalid To, 21214 unroutable, 21608 unverified on a
            # trial: the house's words, quoted, so the leg says why.
            words = " ".join(str(x) for x in (got.get("code"),
                                              got.get("message")) if x)
            raise Refused(words or text[:400])
        if not 200 <= status < 300:
            raise Answered(status, str(got.get("message") or text[:400]))
        sid = got.get("sid")
        if not sid:
            raise NoCall()
        return str(sid)

    # -- verify ---------------------------------------------------------------

    def verify(self, signed_url: str, headers: dict, raw_body: bytes) -> bool:
        given = next((headers.get(h) for h in self.signature_headers
                      if headers.get(h)), None)
        if not given or not self.cfg.token:
            return False
        params = urllib.parse.parse_qs(raw_body.decode("utf-8", "replace"),
                                       keep_blank_values=True)
        want = twilio_signature(self.cfg.token, signed_url, params)
        return hmac.compare_digest(want.encode(), given.encode())

    # -- parse ----------------------------------------------------------------

    def parse(self, headers: dict, raw_body: bytes) -> Event:
        f = form(raw_body)
        raw = f.get("CallStatus")
        status = STATUS_WORDS.get((raw or "").lower())
        if "Digits" in f:
            kind = "digit"
        elif "SpeechResult" in f:
            kind = "speech"
        elif status:
            kind = "status"
        else:
            kind = "answer"
        answered_by = f.get("AnsweredBy")
        if kind == "answer" and not answered_by:
            answered_by = "unknown"
        detail = ";".join(f"{k}={f[k]}" for k in
                          ("CallStatus", "AnsweredBy", "SipResponseCode")
                          if f.get(k))
        return Event(kind=kind, digit=f.get("Digits"),
                     speech=f.get("SpeechResult"), status=status,
                     answered_by=answered_by,
                     seconds=as_int(f.get("CallDuration")),
                     vendor_ref=f.get("CallSid"), detail=detail)

    # -- render ---------------------------------------------------------------

    def render(self, line: dict, urls: dict, counters: dict) -> Response:
        return Response(self.markup(line, action_urls(urls, counters)),
                        media_type="application/xml")

    def markup(self, line: dict, act: dict) -> str:
        """TwiML for one line envelope. ``actionOnEmptyResult`` makes the
        house POST the action with an empty field instead of falling
        through, so an unanswered prompt still reaches the door."""
        say = (line.get("say") or "").strip()
        then = line.get("then")
        lang = self.lang(line.get("language"))
        talk = f'<Say language="{lang}">{escape(say)}</Say>' if say else ""
        parts = ['<?xml version="1.0" encoding="UTF-8"?>', "<Response>"]
        if then == "gather_digit":
            parts.append(
                f'<Gather input="dtmf" numDigits="1" timeout="7" '
                f'actionOnEmptyResult="true" method="POST" '
                f'action="{attr(act["gather"])}">{talk}</Gather>')
        elif then == "speak_first":
            parts.append(talk)
            parts.append(f'<Redirect method="POST">{escape(act["speech"])}'
                         f'</Redirect>')
        elif then == "gather_speech":
            parts.append(talk)
            parts.append(
                f'<Gather input="speech" speechTimeout="auto" timeout="6" '
                f'language="{lang}" actionOnEmptyResult="true" '
                f'method="POST" action="{attr(act["speech"])}"/>')
        else:
            parts.append(talk)
            parts.append("<Hangup/>")
        parts.append("</Response>")
        return "".join(parts)

    # -- standing -------------------------------------------------------------

    def standing(self) -> tuple[str, str]:
        try:
            status, text = self.http(
                "GET", f"{self.base}/Accounts/{self.cfg.account}.json",
                headers=self._headers(), timeout=3)
        except Unreachable as exc:
            return "house_unreachable", f"the house could not be reached: {exc}"
        return self.standing_word(status, text)

