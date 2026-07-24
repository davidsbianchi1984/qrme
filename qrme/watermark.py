"""Synthetic-media watermarking: generated content that leaves the platform
carries a verifiable credential — and a visible mark.

Every piece of AI-generated work, textual or visual — chat turns, public
posts, room turns, game and robot lines, creative works, task outputs, and
any non-text modality a reply renders in (voice, image, video) — is
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
import json

from . import db

DISCLOSURE = ("AI-generated synthetic media — produced by a QRME synthetic "
              "profile, not a real person")

DEFAULT_MARK = "✦"


def _hash(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()


def design(profile_id: str) -> dict:
    """The profile's display watermark — the visible mark that rides on every
    render of its generated work, textual or visual. Owners may design their
    own (mark + label via PUT /profiles/{id}/watermark), but the AI
    designation is invariant: whatever the custom label says, the rendered
    line always carries "AI"."""
    row = db.connect().execute(
        "SELECT display_name, watermark_design FROM profiles WHERE id=?",
        (profile_id,)).fetchone()
    name = row["display_name"] if row else profile_id
    custom = json.loads(row["watermark_design"]) if (
        row and row["watermark_design"]) else {}
    mark = custom.get("mark") or DEFAULT_MARK
    label = custom.get("label") or f"AI · {name}"
    # Non-negotiable: the label as rendered always declares AI.
    if "ai" not in label.lower():
        label = f"AI · {label}"
    return {
        "mark": mark,
        "label": label,
        "line": f"{mark} {label}",
        "custom": bool(custom),
        "always_displayed": True,
        "disclosure": DISCLOSURE,
    }


def set_design(profile_id: str, mark: str | None, label: str | None) -> dict:
    """Store the owner's custom watermark design (or reset when both empty)."""
    conn = db.connect()
    value = None
    if mark or label:
        value = json.dumps({k: v for k, v in
                            (("mark", mark), ("label", label)) if v})
    conn.execute("UPDATE profiles SET watermark_design=? WHERE id=?",
                 (value, profile_id))
    conn.commit()
    return design(profile_id)


def brief(watermark_id: str | None) -> dict | None:
    """The compact block a stored render carries: id, verify path, disclosure,
    and the profile's display watermark — enough for any surface to show the
    mark and let a viewer check the credential."""
    if not watermark_id:
        return None
    row = lookup(watermark_id)
    if row is None:
        return None
    return {
        "watermark_id": row["id"],
        "kind": row["kind"],
        "disclosure": DISCLOSURE,
        "display": design(row["profile_id"]),
        "verify": f"/watermarks/{watermark_id}",
    }


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
        "display": design(profile_id),
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
        "display": design(row["profile_id"]),
    }
    if content is not None:
        out["content_match"] = _hash(content) == row["content_hash"]
        if not out["content_match"]:
            out["note"] = ("this content does not match the media the "
                           "credential was issued for — it has been altered "
                           "or substituted")
    return out
