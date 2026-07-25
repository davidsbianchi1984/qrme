"""The intake's last line of defence.

Contribution payloads arrive already anonymized — the contributing deployment
strips ids and names before anything leaves it, which is the only place that
*can* do it properly, since only that deployment knows what the identifiers
are. This module assumes that worked and checks anyway.

The reasoning: a gateway accumulates a training corpus from many deployments
it does not control, running versions it did not ship. One client bug, one
stale build, one field added upstream without thought, and the corpus has
real names in it — discovered much later, if ever, and unfixable in any
satisfying way once training has run.

So the intake **refuses** what looks like identity rather than stripping it.
Sanitizing quietly would hide the client bug that produced it; a 422 tells
the operator of the contributing deployment that their build is leaking, in
time to fix it.
"""

from __future__ import annotations

import re

# Field names that carry identity in these products' schemas. Checked at every
# depth, because a nested exchange is exactly where one hides.
IDENTIFYING_FIELDS = {
    "profile_id", "owner_id", "interactor_id", "user_id", "guardian_id",
    "tenant_id", "display_name", "name", "email", "phone", "handle",
    "birthdate", "address", "token", "owner_token", "user_token",
    "medical_id", "contact", "emergency_contact",
}

# Opaque local ids from the three products. A contribution's own `ref` is
# random and carries no identity; anything *else* shaped like a product id is
# a leak, since the whole point is that the gateway cannot link items back.
_ID_PATTERN = re.compile(
    r"\b(?:prf|usr|itr|rec|tnt|gdn|evt)_[0-9a-f]{8,}\b", re.IGNORECASE)

_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")

# Contribution kinds the products actually send (docs/cloud-model.md). An
# unknown kind is refused rather than stored uninterpreted: a corpus of things
# nobody can describe is not an asset.
KINDS = {"rated_exchange", "guidance_outcome"}
SOURCES = {"qrme", "jim-mini", "pdi"}


class Rejected(Exception):
    """The payload was refused. The message names the offending field so the
    contributing deployment can find the bug."""


def _walk(node, path="") -> list[tuple[str, object]]:
    """Every (path, value) pair in a nested payload."""
    out = []
    if isinstance(node, dict):
        for k, v in node.items():
            here = f"{path}.{k}" if path else k
            out.append((here, v))
            out.extend(_walk(v, here))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            out.extend(_walk(v, f"{path}[{i}]"))
    return out


def screen(payload: dict) -> None:
    """Raise :class:`Rejected` if this contribution should not be stored.

    Refusing is the point — see the module docstring. Nothing here is a
    substitute for the client-side anonymization; it is the check that the
    client-side anonymization is still working.
    """
    if payload.get("source") not in SOURCES:
        raise Rejected(f"unknown source {payload.get('source')!r} — "
                       f"expected one of {sorted(SOURCES)}")
    if payload.get("kind") not in KINDS:
        raise Rejected(f"unknown contribution kind {payload.get('kind')!r} — "
                       f"expected one of {sorted(KINDS)}")
    if not payload.get("ref"):
        raise Rejected("contributions need a ref, or they cannot be revoked "
                       "later without deanonymizing the contributor")

    for path, value in _walk(payload):
        field = path.rsplit(".", 1)[-1].split("[")[0]
        if field in IDENTIFYING_FIELDS:
            raise Rejected(
                f"{path!r} is an identifying field — this deployment's "
                "anonymization is not stripping it. Refused rather than "
                "sanitized, so the leak is visible where it can be fixed.")
        if isinstance(value, str):
            if path != "ref" and _ID_PATTERN.search(value):
                raise Rejected(
                    f"{path!r} contains what looks like a product id; "
                    "contributed items must not be linkable back")
            if _EMAIL.search(value):
                raise Rejected(f"{path!r} contains an email address")
