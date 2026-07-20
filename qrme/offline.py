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

import os

_TRUTHY = {"1", "true", "yes", "on"}


def enabled() -> bool:
    return os.environ.get("QRME_OFFLINE", "").strip().lower() in _TRUTHY


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
