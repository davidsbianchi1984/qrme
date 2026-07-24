"""Synthetic-media watermarking: generated content that leaves the platform
carries a verifiable credential.

Every outward-facing piece of generated media — public posts, and any
non-text modality a chat reply renders in (voice, image, video) — is
stamped at creation with a **synthetic-media credential**: a watermark id,
the producing profile, the content's SHA-256, an issue timestamp, and a
plain-language disclosure. The credential is stored server-side, so anyone
holding a piece of content can verify (a) that QRME produced it and
(b) that it hasn't been altered since — and content that *claims* a
watermark it doesn't have simply fails the lookup.

This is provenance watermarking, not steganography: the credential rides
*alongside* the content (platforms and viewers can display or check it),
which is what makes it verifiable rather than merely embedded.
"""

from __future__ import annotations

import hashlib

from . import db

DISCLOSURE = ("AI-generated synthetic media — produced by a QRME synthetic "
              "profile, not a real person")


def _hash(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()


def stamp(profile_id: str, kind: str, content: str) -> dict:
    """Issue a credential for one piece of generated media and return the
    block that rides with it. ``kind`` names the surface: post | voice |
    image | video | …"""
    conn = db.connect()
    watermark_id = db.new_id("wmk")
    issued_at = db.utcnow()
    conn.execute(
        "INSERT INTO media_watermarks (id, profile_id, kind, content_hash,"
        " issued_at) VALUES (?,?,?,?,?)",
        (watermark_id, profile_id, kind, _hash(content), issued_at))
    conn.commit()
    return {
        "watermark_id": watermark_id,
        "kind": kind,
        "profile_id": profile_id,
        "content_sha256": _hash(content),
        "issued_at": issued_at,
        "disclosure": DISCLOSURE,
        "verify": f"/watermarks/{watermark_id}",
    }


def lookup(watermark_id: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM media_watermarks WHERE id=?",
        (watermark_id,)).fetchone()
    return dict(row) if row else None


def verify(watermark_id: str, content: str | None = None) -> dict | None:
    """Resolve a credential; when the content itself is presented, also say
    whether it still matches the hash issued at creation."""
    row = lookup(watermark_id)
    if row is None:
        return None
    out = {
        "watermark_id": row["id"],
        "valid": True,
        "kind": row["kind"],
        "profile_id": row["profile_id"],
        "content_sha256": row["content_hash"],
        "issued_at": row["issued_at"],
        "disclosure": DISCLOSURE,
    }
    if content is not None:
        out["content_match"] = _hash(content) == row["content_hash"]
        if not out["content_match"]:
            out["note"] = ("this content does not match the media the "
                           "credential was issued for — it has been altered "
                           "or substituted")
    return out
