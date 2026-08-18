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

from . import db, llm, offline, privileges

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


def excursion(profile_id: str, topic: str, question: str,
              private: list[str] | None = None, cloud=None, pdi=None) -> str:
    """Go and study something, and write down what could have left.

    This lived in the router until the privilege roster arrived, and a check
    that lives in a route is a check the second caller walks past. Going out to
    read is a thing the owner said the agent may do, so the permission is
    asked here — on the path that sanitizes, gathers and records — rather than
    at the door above it.

    Returns the excursion id. The row is the audit trail: the sanitized brief
    is exactly what could have left, beside the count of what was taken out.
    """
    privileges.require(profile_id, "study_the_web")
    brief, redactions = sanitize(profile_id, f"{topic}\n{question}", private)
    left_host = would_leave(cloud)
    findings = gather(brief, cloud)
    cid = db.new_id("exc")
    conn = db.connect()
    conn.execute(
        "INSERT INTO excursions (id, profile_id, topic, brief, redactions,"
        " left_host, findings, learned_src, created_at)"
        " VALUES (?,?,?,?,?,?,?,NULL,?)",
        (cid, profile_id, topic, brief, redactions, int(left_host),
         findings, db.utcnow()))
    conn.commit()
    # The study writes its own ledger row into the vault's tables
    # (qrme/recollection.py → PDI resident): what was studied and what it
    # cost in redactions, queryable in the PDI console — never the findings
    # themselves, which stay in this row under this deployment's custody.
    from . import recollection
    recollection.tabulate(pdi, "qrme_studies",
                          [{"excursion": cid, "topic": topic,
                            "redactions": redactions,
                            "left_host": int(left_host)}],
                          source_ref=profile_id)
    return cid
