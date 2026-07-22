"""Safe knowledge excursions.

When a profile's model meets an unfamiliar topic — it needs to study, gather
tools, or get more familiar to help with a request — it can go and fetch
**general knowledge** without carrying the owner's private data out with it.

Two guarantees make that safe:

1. **The outbound brief is sanitized.** The profile's own name, the people it
   talks to (relationship interactors), its handle, and any caller-marked
   private terms are redacted before anything is gathered. Exactly what could
   leave is recorded, so the excursion is auditable.
2. **Nothing private leaves the host.** Offline (``QRME_OFFLINE=1``) the gather
   runs on the local deterministic provider — no network at all. Even with a
   cloud model attached, only the sanitized brief is sent.

Findings come back as general knowledge (no private data) and can be folded into
the profile as a learned ``knowledge`` source. The local model then answers using
those findings together with the private context that never left.
"""

from __future__ import annotations

import re

from . import db, llm, offline

REDACTION = "[private]"

_RESEARCH_SYSTEM = (
    "You are a research assistant gathering general background on a topic. The "
    "brief below has been stripped of all private data. Return concise, general "
    "notes that would help someone learn the topic. Never ask for or infer any "
    "personal details."
)


def _private_terms(profile_id: str) -> list[str]:
    """The owner's private terms for this profile: its display name, the people
    it talks to, and its handle. These must never appear in an outbound brief."""
    conn = db.connect()
    terms: set[str] = set()
    prof = conn.execute("SELECT display_name FROM profiles WHERE id=?",
                        (profile_id,)).fetchone()
    if prof and prof["display_name"]:
        terms.add(prof["display_name"])
    for row in conn.execute(
        "SELECT i.display_name AS name FROM relationships rel"
        " JOIN interactors i ON i.id = rel.interactor_id WHERE rel.profile_id=?",
            (profile_id,)):
        if row["name"]:
            terms.add(row["name"])
    handle = conn.execute("SELECT handle FROM handles WHERE profile_id=?",
                         (profile_id,)).fetchone()
    if handle and handle["handle"]:
        terms.add(handle["handle"])
    return [t for t in terms if len(t) >= 2]


def sanitize(profile_id: str, text: str, extra: list[str] | None = None) -> tuple[str, int]:
    """Redact private terms from ``text``. Returns (sanitized, redaction_count)."""
    terms = set(_private_terms(profile_id)) | set(extra or [])
    out, total = text, 0
    for term in sorted(terms, key=len, reverse=True):
        if not term:
            continue
        out, n = re.compile(rf"\b{re.escape(term)}\b", re.I).subn(REDACTION, out)
        total += n
    return out, total


def would_leave(cloud) -> bool:
    """Whether the gather actually reaches an external host. Offline: never.
    Otherwise only when a cloud model is attached (and then, only the sanitized
    brief is sent)."""
    return (not offline.enabled()) and (cloud is not None)


def gather(brief: str, cloud=None) -> str:
    """Gather general knowledge from the sanitized brief. Offline uses the local
    deterministic provider — no network."""
    provider = llm.get_provider(None if offline.enabled() else cloud)
    return provider.generate(_RESEARCH_SYSTEM, [{"role": "user", "content": brief}])
