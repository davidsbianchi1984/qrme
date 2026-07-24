"""Terms of Service: version, key points, and the acceptance contract.

The full text lives in docs/terms.md; the API serves the version and key
points at GET /terms so every client can display them, and profile
creation records the accepted version + timestamp — clickwrap with a
server-side receipt. Bump TERMS_VERSION when the document materially
changes; new acceptances record the new version.
"""

from __future__ import annotations

TERMS_VERSION = "1.0"

DOCUMENT = "docs/terms.md"

KEY_POINTS = [
    "Profiles are AI-generated synthetic content — not the statements of a "
    "real person, and never professional (medical/legal/financial) advice.",
    "In an emergency call 911; in crisis call or text 988 (US).",
    "You assume the risks of interacting with AI personas, other users, and "
    "connected devices, and release the operator except for gross "
    "negligence or willful misconduct.",
    "Creators are responsible for third-party rights, age/identity honesty, "
    "and their published content; the objection/takedown flow is binding.",
    "18+ features require verified age; the age wall travels with content.",
    "The service is provided as-is; liability is capped; you indemnify the "
    "operator for claims arising from your content and profiles.",
    "Marketplace money is simulated in this version.",
]
