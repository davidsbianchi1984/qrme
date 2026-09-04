"""SignalWire — Twilio's dialect, spoken from a space of your own.

cXML (LaML) is TwiML, and the webhook signature is the same HMAC-SHA1
scheme under a different header, so this row is the Twilio row with
three things swapped: the base URL, which lives under the space named by
``VOICE_HOUSE_REF``; the credential slots, which hold a project id and a
token; and the header name. Renderer, parser and standing are inherited
unchanged, which is the whole point of the subclass — nothing about the
line machine is repeated to add a house.
"""

from __future__ import annotations

import os

from .twilio import Twilio


class SignalWire(Twilio):
    name = "signalwire"
    account_means = "project id"
    token_means = "API token"
    house_ref_means = "SignalWire space name"
    #: SignalWire signs under its own header and, for compatibility,
    #: Twilio's; the first one present is checked.
    signature_headers = ("x-signalwire-signature", "x-twilio-signature")

    @property
    def base(self) -> str:
        named = os.environ.get("VOICE_SIGNALWIRE_API", "").strip()
        if named:
            return named.rstrip("/")
        return (f"https://{self.cfg.house_ref}.signalwire.com"
                "/api/laml/2010-04-01")
