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
import hmac
import json
import os
import re

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
        "SELECT display_name, anonymous, watermark_design FROM profiles"
        " WHERE id=?", (profile_id,)).fetchone()
    # An anonymous profile's name is withheld everywhere else it could be
    # seen (summon cards, marketplace listings). The default watermark is
    # built from that name and rides on every render the profile produces —
    # so without this it was the one surface that gave it away.
    from . import identity
    name = (identity.shown_name(row, profile_id)
            if row else profile_id)
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
    # Deposit the recoverable half too (see `recover` below): the exact hash
    # proves a known credential, the keyed windows find the author when the
    # text arrives on its own and edited.
    index(watermark_id, content)
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


# --------------------------------------------------------------------------- #
# Recovering the mark from the text itself
# --------------------------------------------------------------------------- #
#
# The field drawing (message m + sequence S^N + security key K^D → watermark W
# → embed → *attack* → extract W' → reconstruct m') asks for something the
# exact-hash credential above cannot do: given a piece of text and no
# watermark id, say who produced it — and keep saying it after the text has
# been edited.
#
# The mechanism is deliberately boring arithmetic rather than a learned
# detector: normalize the text, cut it into overlapping five-word windows,
# HMAC each window with the deployment's key, and store them. Recovery hashes
# a candidate the same way and asks which stamp shares the most windows.
# Paraphrase a sentence and its windows change; leave four sentences alone and
# theirs still match, so the author is still recoverable and the score states
# how much drifted.
#
# The key is what makes it a watermark rather than a fingerprint: without it,
# nobody can compute matching windows, so a credential cannot be forged or
# transplanted onto text QRME never wrote.

SHINGLE_WORDS = 5

# Below this share of matched windows a hit is a coincidence, not a
# recovery — two texts about the same subject share ordinary phrases.
RECOVER_THRESHOLD = 0.25


def _key() -> bytes:
    """The deployment's watermark key (K^D).

    ``QRME_WATERMARK_KEY`` in production. Unset, it derives a stable key from
    the database path so a local install still recovers its own marks — that
    is a working default, not a secret, and the docstring says so rather than
    letting an operator assume otherwise.
    """
    configured = os.environ.get("QRME_WATERMARK_KEY")
    if configured:
        return configured.encode()
    return hashlib.sha256(f"qrme-watermark::{db.db_path()}".encode()).digest()


_WORD = re.compile(r"[a-z0-9']+")


def _normalize(text: str) -> list[str]:
    """Words only, lowercased — so casing, punctuation and whitespace churn
    do not count as tampering."""
    return _WORD.findall((text or "").lower())


def _shingles(text: str) -> set[str]:
    """Keyed hashes of overlapping word windows."""
    words = _normalize(text)
    if not words:
        return set()
    key = _key()
    if len(words) <= SHINGLE_WORDS:
        windows = [" ".join(words)]
    else:
        windows = [" ".join(words[i:i + SHINGLE_WORDS])
                   for i in range(len(words) - SHINGLE_WORDS + 1)]
    return {hmac.new(key, w.encode(), hashlib.sha256).hexdigest()[:32]
            for w in windows}


def index(watermark_id: str, content: str) -> int:
    """Deposit a stamped text's windows. Returns how many were stored."""
    marks = _shingles(content)
    if not marks:
        return 0
    conn = db.connect()
    conn.executemany(
        "INSERT OR IGNORE INTO watermark_shingles (watermark_id, shingle)"
        " VALUES (?,?)", [(watermark_id, m) for m in marks])
    conn.commit()
    return len(marks)


def recover(content: str) -> dict:
    """Extract and reconstruct: who produced this text, if anyone here did.

    Answers from the text alone — no watermark id required — and survives
    editing. The reply always states the evidence: how many windows matched,
    out of how many, and whether the text is verbatim or altered.
    """
    candidate = _shingles(content)
    if not candidate:
        return {"recovered": False, "reason": "no text to examine"}

    conn = db.connect()
    placeholders = ",".join("?" * len(candidate))
    rows = conn.execute(
        f"SELECT watermark_id, COUNT(*) AS hits FROM watermark_shingles"
        f" WHERE shingle IN ({placeholders})"
        f" GROUP BY watermark_id ORDER BY hits DESC LIMIT 5",
        tuple(candidate)).fetchall()
    if not rows:
        return {"recovered": False,
                "reason": "no stamped work shares any wording with this text",
                "examined_windows": len(candidate)}

    best, best_score, best_stored = None, 0.0, 0
    for row in rows:
        stored = conn.execute(
            "SELECT COUNT(*) AS n FROM watermark_shingles WHERE watermark_id=?",
            (row["watermark_id"],)).fetchone()["n"]
        union = stored + len(candidate) - row["hits"]
        score = row["hits"] / union if union else 0.0
        if score > best_score:
            best, best_score, best_stored = row, score, stored

    if best is None or best_score < RECOVER_THRESHOLD:
        return {"recovered": False,
                "reason": ("some wording overlaps stamped work, but not enough "
                           "to name an author — ordinary phrases are shared by "
                           "unrelated texts"),
                "best_similarity": round(best_score, 3),
                "threshold": RECOVER_THRESHOLD,
                "examined_windows": len(candidate)}

    row = lookup(best["watermark_id"])
    verbatim = row is not None and _hash(content) == row["content_hash"]
    return {
        "recovered": True,
        # The reconstructed message m': which profile produced this.
        "profile_id": row["profile_id"] if row else None,
        "watermark_id": best["watermark_id"],
        "kind": row["kind"] if row else None,
        "issued_at": row["issued_at"] if row else None,
        "verbatim": verbatim,
        "similarity": round(best_score, 3),
        "matched_windows": best["hits"],
        "stored_windows": best_stored,
        "examined_windows": len(candidate),
        "state": "unaltered" if verbatim else "altered but traceable",
        "disclosure": DISCLOSURE,
        "display": design(row["profile_id"]) if row else None,
        "method": ("keyed five-word windows, HMAC'd with this deployment's "
                   "watermark key and compared by overlap — arithmetic, not a "
                   "learned detector, so the score can be checked by hand"),
    }
