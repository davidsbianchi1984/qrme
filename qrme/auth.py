"""Capability-token authentication.

Identity in QRME is proven by holding a bearer token, not by asserting an id
in a request body. Two kinds of capability exist:

- **owner** — minted once when a profile is created (and returned once, in the
  create response). Whoever holds it controls that profile: edit, sources,
  surfaces, moderation queue, export, erasure, departure. ``owner_id`` becomes
  a grouping/display attribute, no longer a security boundary.
- **interactor** — minted when an interactor is created. It proves "I am this
  interactor" for the private, per-interactor surfaces (reading one's own
  memory).

Only the SHA-256 hash of a token is persisted, so the raw token is
unrecoverable from the database — it is shown to the caller exactly once.

Public surfaces (chatting with a profile, browsing the marketplace, summoning
by handle/tag/beacon) require no token: talking to a synthetic profile is open
by design, the same way scanning a QR code in the world is.
"""

from __future__ import annotations

import hashlib
import os
import secrets

from fastapi import HTTPException, Request

from . import db


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def issue(role: str, subject_id: str) -> str:
    """Mint a token for ``subject_id`` in ``role`` and return it once."""
    token = secrets.token_urlsafe(32)
    db.connect().execute(
        "INSERT INTO api_tokens (token_hash, role, subject_id, created_at)"
        " VALUES (?,?,?,?)",
        (_hash(token), role, subject_id, db.utcnow()),
    )
    db.connect().commit()
    return token


def bearer(request: Request) -> str | None:
    """Extract the bearer token from the Authorization header, if present."""
    header = request.headers.get("authorization", "")
    if header.lower().startswith("bearer "):
        return header[7:].strip() or None
    return None


def principal(request: Request) -> dict | None:
    """Resolve the caller's token to ``{role, subject_id}``, or None."""
    token = bearer(request)
    if not token:
        return None
    row = db.connect().execute(
        "SELECT role, subject_id FROM api_tokens WHERE token_hash=?",
        (_hash(token),),
    ).fetchone()
    return dict(row) if row else None


def require(request: Request, role: str, subject_id: str) -> None:
    """Authorize the caller for (``role``, ``subject_id``) or raise.

    401 when no valid token is presented, 403 when a valid token is presented
    but it grants a different capability.
    """
    who = principal(request)
    if who is None:
        raise HTTPException(401, "authentication required")
    if who["role"] != role or who["subject_id"] != subject_id:
        raise HTTPException(403, "not authorized for this resource")


def require_reviewer(request: Request) -> None:
    """Guard the objection-review path. A dedicated reviewer role sits outside
    profile ownership (an owner must not adjudicate an objection against their
    own profile); it is held via ``QRME_ADMIN_TOKEN``. Unset = development mode
    (open, for local use only), matching PDI's admin convention."""
    required = os.environ.get("QRME_ADMIN_TOKEN")
    if not required:
        return
    token = bearer(request)
    if not token:
        raise HTTPException(401, "reviewer token required")
    if not secrets.compare_digest(token, required):
        raise HTTPException(403, "invalid reviewer token")


def revoke_subject(subject_id: str) -> None:
    """Drop every token for a subject (called when the subject is deleted)."""
    conn = db.connect()
    conn.execute("DELETE FROM api_tokens WHERE subject_id=?", (subject_id,))
    conn.commit()
