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

Above the per-capability layer sits an optional **deployment gate**. On a
laptop or a LAN, anyone who can reach the API can create a profile — that is
the right default when reaching it already means being in the house. A
deployment published to the internet is different: without a gate, whoever
finds the URL can create profiles on it. Setting ``QRME_SIGNUP_KEY`` requires
that key to create a profile, so a hosted instance stays the operator's and
their colleagues', not the internet's. Unset, nothing changes.
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


# Starlette's in-process sentinel names no socket, so no network peer can
# present it. Same set the cloud gateway uses, for the same reason.
_LOCAL_CALLERS = frozenset({"127.0.0.1", "::1", "localhost", "testclient"})


def require_reviewer(request: Request) -> None:
    """Guard the objection-review path.

    A dedicated reviewer role sits outside profile ownership — an owner must
    not adjudicate an objection against their own profile — and is held via
    ``QRME_ADMIN_TOKEN``.

    **Unset is development mode, and development mode now means localhost.**
    It previously meant *everybody*: with no token configured this returned
    unconditionally, for any caller from any address. The docstring said "for
    local use only" and nothing enforced the local part, which is the same
    shape of defect as a validator whose message promises more than its
    pattern checks.

    What sits behind this gate is why it is worth the four lines. Upholding an
    objection **terminates a profile and erases its content**; succession
    **hands a profile to a different owner**. On a deployment where somebody
    forgot the variable — the exact deployment least likely to notice — those
    were reachable by an anonymous caller on the internet.

    So it fails closed the way ``cloudgw`` already did, which the old
    docstring claimed to match and did not: a local caller still gets the open
    development path, and a remote one gets a 503 naming the variable to set.
    An operator who has not decided yet should get "no", not "everyone".
    """
    required = os.environ.get("QRME_ADMIN_TOKEN")
    if not required:
        host = request.client.host if request.client else ""
        if host in _LOCAL_CALLERS:
            return
        raise HTTPException(
            503, "this deployment is reachable beyond localhost but has no "
                 "QRME_ADMIN_TOKEN configured — objection review and "
                 "succession stay closed until it is")
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


def require_signup_key(request: Request) -> None:
    """Deployment-level gate for creating a profile.

    Unset ``QRME_SIGNUP_KEY`` means open, which is what a laptop or LAN
    deployment wants. When it is set — the sensible posture for anything
    published — the caller must present it as ``x-signup-key``. This is a
    gate on *who may create an account here*, not a replacement for the
    per-capability tokens: everything after creation is still authorized by
    the owner or interactor token.
    """
    required = os.environ.get("QRME_SIGNUP_KEY")
    if not required:
        return
    presented = request.headers.get("x-signup-key", "")
    # Constant-time compare so a wrong key can't be recovered by timing.
    if not (presented and secrets.compare_digest(presented, required)):
        raise HTTPException(
            403, "this deployment requires a signup key to create a profile "
                 "— send it as the x-signup-key header")
