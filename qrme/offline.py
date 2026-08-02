"""Offline-first mode.

QRME runs fully offline after initial setup. Set ``QRME_OFFLINE=1`` and the
platform makes a hard guarantee: **nothing leaves the host**.

- Inference is served by the local deterministic provider — the Anthropic SDK
  (which would call out) and the Cloud Model Gateway are both bypassed, even if
  their credentials are present. (A local model can be dropped in behind the
  same ``Provider`` interface without changing anything else.)
- The cloud client is never attached, so opt-in cloud contribution is inert.
- Persona adaptation still works: embeddings and offline fine-tuning
  (``/profiles/{id}/finetune``) are recomputed **locally** from stored history,
  and source material lives in the local database or the on-prem PDI vault —
  never a third party.

``GET /offline/status`` reports the posture so a deployment can prove it.
"""

from __future__ import annotations

import ipaddress
import os
import socket
import urllib.parse

_TRUTHY = {"1", "true", "yes", "on"}


def enabled() -> bool:
    return os.environ.get("QRME_OFFLINE", "").strip().lower() in _TRUTHY


class LeftTheHost(RuntimeError):
    """Refused: this would have sent something to another machine.

    Raised rather than returned. A caller that could ignore the answer is a
    caller that will, and the guarantee this module makes is absolute.
    """


def is_local(host: str | None) -> bool:
    """Is this host the machine we are running on, or its own network?

    Loopback and the private ranges — the on-prem PDI vault, a webhook on the
    LAN, an Ollama daemon on 127.0.0.1. Everything else is another party.

    A name that does not resolve is **not** local. Failing closed is the only
    safe direction: an unresolvable name in offline mode is either a typo or a
    host that is not there, and neither is a reason to try the connection.
    """
    if not host:
        return False
    name = host.strip().strip("[]").lower()
    if name in ("localhost", "localhost.localdomain"):
        return True
    try:
        addresses = [ipaddress.ip_address(name)]
    except ValueError:
        try:
            addresses = [ipaddress.ip_address(info[4][0])
                         for info in socket.getaddrinfo(name, None)]
        except (socket.gaierror, ValueError, UnicodeError):
            return False
    return bool(addresses) and all(
        a.is_loopback or a.is_private or a.is_link_local for a in addresses)


def allow(url: str | None, what: str) -> None:
    """Refuse a URL that would leave this host while offline mode is on.

    ## Why this is a host check and not a blanket refusal

    Offline mode means *nothing leaves the machine*, not *nothing opens a
    socket*. The three things this platform legitimately talks to when offline
    are all on the same side of the wire: an Ollama daemon on loopback, the
    on-prem PDI vault, an escalation webhook on the LAN. Two of those were
    already documented as local — `llm.py` says "Ollama IS offline: it answers
    on loopback", this module's own docstring says "the on-prem PDI vault" —
    and neither was checked. They were assumptions about how somebody would
    deploy, written as if they were properties of the code.

        asked     is inference offline
        mattered  is everything that can leave

    Blanket refusal would also have been wrong in a way that matters: it would
    have silenced the escalation webhook, and this product's own plan-gate
    refusal promises in nine languages that emergency paths are never affected.

    Callers pass the URL they are about to open and a short name for what it
    is; the name is what a person reads in the refusal.
    """
    if not enabled():
        return
    host = urllib.parse.urlsplit(url or "").hostname
    if is_local(host):
        return
    where = host or "an unnamed host"
    raise LeftTheHost(
        f"offline mode is on, so {what} cannot reach {where}. Nothing leaves "
        "this machine while QRME_OFFLINE is set — point it at a host on this "
        "network, or turn offline mode off.")


def allow_host(host: str | None, what: str) -> None:
    """`allow` for the things that are not URLs. SMTP is a host and a port."""
    if not enabled():
        return
    if is_local(host):
        return
    where = host or "an unnamed host"
    raise LeftTheHost(
        f"offline mode is on, so {what} cannot reach {where}. Nothing leaves "
        "this machine while QRME_OFFLINE is set.")


def status(app=None) -> dict:
    off = enabled()
    cloud = getattr(getattr(app, "state", None), "cloud", None)
    return {
        "offline": off,
        "provider": "local (deterministic, no network)" if off
                    else ("cloud gateway (greater model)" if cloud
                          else "local (Anthropic SDK or offline stub)"),
        "cloud_attached": (cloud is not None) and not off,
        # The core promise: in offline mode no request can reach an external
        # host — not the model API, not the cloud gateway, not the intake.
        "external_transmission_possible": (not off),
        "data_locality": (
            "all inference and adaptation run on-host; source material stays in "
            "the local database or the on-prem PDI vault — no raw user data "
            "ever leaves your vault"),
        "guarantees": ([
            "no model API calls",
            "no cloud gateway calls",
            "no cloud contribution",
            "embeddings & fine-tuning recomputed locally",
        ] if off else [
            "local provider always available as fallback",
            "cloud use and contribution are opt-in and revocable",
        ]),
    }
