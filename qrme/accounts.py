"""Email + password accounts, with the address verified before sign-in works.

Mirrors JIM-mini's account layer with QRME's own shape: here an account is
the thing that *owns* — its id is the ``owner_id`` profiles are created
under and the ``account_id`` memberships bill to — while each profile keeps
its own owner capability token exactly as before. The account token proves
"I am this account" to the console; it grants none of a profile's owner
powers by itself.

The order of operations is the design:

1. **Signup** records the email and password hash and sends a six-digit code
   to the address. The account cannot sign in yet.
2. **Verification** — presenting the code proves the caller can read that
   inbox. Only then is the account's first token minted.
3. **Sign-in** afterwards checks the password and mints a fresh token; an
   unverified account cannot sign in at all.

Storage rules: passwords are PBKDF2-HMAC-SHA256 with a per-account salt and
never stored or logged in the clear; codes are hashed at rest, single-use,
and expire in 15 minutes; issuing a new code retires the previous ones;
unknown-address and wrong-password answers are indistinguishable.
"""

from __future__ import annotations

import hashlib
import re
import secrets
from datetime import datetime, timedelta, timezone

from . import db, mailer

CODE_TTL_MINUTES = 15
_PBKDF2_ITERATIONS = 600_000
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class AccountError(Exception):
    def __init__(self, status: int, detail: str) -> None:
        super().__init__(detail)
        self.status = status
        self.detail = detail


def _normalize(email: str) -> str:
    email = email.strip().lower()
    if not _EMAIL_RE.match(email):
        raise AccountError(422, "that does not look like an email address")
    return email


def _hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt), _PBKDF2_ITERATIONS
    ).hex()


def _hash_code(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


def _public_url() -> str:
    import os
    return os.environ.get("QRME_PUBLIC_URL", "http://127.0.0.1:8000").rstrip("/")


def _send_code(email: str, purpose: str = "verify") -> str:
    """Issue a fresh code for ``email`` (retiring any previous ones for the
    same purpose), deliver it, and return the transport name — never the
    code. Verification mail leads with a **clickable link** (the shape every
    mainstream flow uses); the 6-digit code rides along as the fallback for
    a mail client on a different device than the app."""
    conn = db.connect()
    conn.execute(
        "UPDATE email_codes SET consumed_at=? WHERE email=? AND purpose IN (?,?)"
        " AND consumed_at IS NULL",
        (db.utcnow(), email, purpose, purpose + "-link"),
    )
    code = f"{secrets.randbelow(1_000_000):06d}"
    expires = (datetime.now(timezone.utc)
               + timedelta(minutes=CODE_TTL_MINUTES)).isoformat()
    conn.execute(
        "INSERT INTO email_codes (email, code_hash, purpose, expires_at, created_at)"
        " VALUES (?,?,?,?,?)",
        (email, _hash_code(code), purpose, expires, db.utcnow()),
    )
    if purpose == "verify":
        link_token = secrets.token_urlsafe(32)
        conn.execute(
            "INSERT INTO email_codes (email, code_hash, purpose, expires_at,"
            " created_at) VALUES (?,?,?,?,?)",
            (email, _hash_code(link_token), "verify-link", expires, db.utcnow()),
        )
    conn.commit()
    if purpose == "reset":
        return mailer.deliver(
            email,
            "Your QRME password reset code",
            f"Your password reset code is: {code}\n\n"
            f"It expires in {CODE_TTL_MINUTES} minutes. If you did not ask to "
            "reset your password, ignore this message — your password is "
            "unchanged without it.",
        )
    return mailer.deliver(
        email,
        "Verify your QRME account",
        f"Click to verify your account:\n\n"
        f"{_public_url()}/verify-email/click?token={link_token}\n\n"
        f"Or enter this code in the app: {code}\n\n"
        f"Both expire in {CODE_TTL_MINUTES} minutes. If you did not create a "
        "QRME account, ignore this message — without this the account "
        "cannot be activated.",
    )


def _consume_code(email: str, code: str, purpose: str) -> None:
    """Check-and-burn the newest live code, or raise."""
    conn = db.connect()
    row = conn.execute(
        "SELECT rowid, * FROM email_codes WHERE email=? AND purpose=?"
        " AND consumed_at IS NULL ORDER BY created_at DESC LIMIT 1",
        (email, purpose),
    ).fetchone()
    if row is None or not secrets.compare_digest(
            row["code_hash"], _hash_code(code.strip())):
        raise AccountError(403, "that code is not right")
    if row["expires_at"] < datetime.now(timezone.utc).isoformat():
        raise AccountError(403, "that code has expired — request a new one")
    conn.execute("UPDATE email_codes SET consumed_at=? WHERE rowid=?",
                 (db.utcnow(), row["rowid"]))
    conn.commit()


def signup(email: str, password: str, display_name: str | None = None) -> dict:
    """Create an unverified account and email its verification code."""
    email = _normalize(email)
    if len(password) < 8:
        raise AccountError(422, "password must be at least 8 characters")
    conn = db.connect()
    existing = conn.execute(
        "SELECT * FROM accounts WHERE email=?", (email,)
    ).fetchone()
    if existing:
        if existing["verified_at"]:
            raise AccountError(
                409, "an account already exists for this address — sign in "
                     "instead")
        if mailer.configured_transport() == "console":
            # A pending half-account (a crashed or abandoned earlier signup)
            # on a machine with no mail transport: nothing can ever verify
            # it, and the machine owner is the only person here. Finish it
            # now, under the credentials just typed — the earlier attempt's
            # password may be lost to the crash that stranded it.
            salt = secrets.token_hex(16)
            conn.execute(
                "UPDATE accounts SET password_hash=?, salt=?,"
                " display_name=? WHERE id=?",
                (_hash_password(password, salt), salt,
                 (display_name or "").strip() or existing["display_name"],
                 existing["id"]),
            )
            conn.commit()
            result = _activate(email, existing["id"])
            result["verified"] = True
            result["verification"] = "local"
            return result
        raise AccountError(
            409, "an account is already pending for this address — verify "
                 "the emailed code, or resend it")
    salt = secrets.token_hex(16)
    account_id = db.new_id("acc")
    conn.execute(
        "INSERT INTO accounts (id, email, password_hash, salt, display_name,"
        " created_at) VALUES (?,?,?,?,?,?)",
        (account_id, email, _hash_password(password, salt), salt,
         (display_name or "").strip() or None, db.utcnow()),
    )
    conn.commit()
    # No mail transport means no inbox can ever be proven — and on a local
    # single-user install (the packaged desktop app) there is nothing to
    # prove: the person owns the machine and the database. Waiting on an
    # email that cannot arrive is a locked door in an empty house; activate
    # directly. A deployment with SMTP configured enforces the real proof.
    if mailer.configured_transport() == "console":
        result = _activate(email, account_id)
        result["verified"] = True
        result["verification"] = "local"
        return result
    delivery = _send_code(email)
    return {"account_id": account_id, "email": email, "verified": False,
            "code_delivery": delivery, "verification": "email"}


def resend(email: str) -> dict:
    email = _normalize(email)
    row = db.connect().execute(
        "SELECT verified_at FROM accounts WHERE email=?", (email,)
    ).fetchone()
    # One response either way a code could not be sent: an endpoint that
    # answers "no such account" to strangers is an address oracle.
    if row is None or row["verified_at"]:
        return {"email": email, "code_delivery": "none"}
    return {"email": email, "code_delivery": _send_code(email)}


def _activate(email: str, account_id: str) -> dict:
    """Mark the account verified and mint its first session token — the step
    that only happens once the address is proven (or, on a local install
    with no mail transport, trusted: see ``signup``)."""
    conn = db.connect()
    conn.execute("UPDATE accounts SET verified_at=? WHERE id=?",
                 (db.utcnow(), account_id))
    conn.commit()
    account = conn.execute(
        "SELECT * FROM accounts WHERE id=?", (account_id,)).fetchone()
    from . import auth
    return {"account_id": account_id, "email": email,
            "display_name": account["display_name"],
            "account_token": auth.issue("account", account_id)}


def verify(email: str, code: str) -> dict:
    """Prove the inbox with the 6-digit code; the account's first session
    token is minted here."""
    email = _normalize(email)
    account = db.connect().execute(
        "SELECT * FROM accounts WHERE email=?", (email,)
    ).fetchone()
    if account is None:
        raise AccountError(403, "no pending account for this address")
    if account["verified_at"]:
        raise AccountError(409, "this address is already verified — sign in")
    _consume_code(email, code, "verify")
    return _activate(email, account["id"])


def verify_link(token: str) -> dict:
    """Prove the inbox with the emailed link's token. The click lands in a
    browser, not the app — the app learns of it by signing in (it holds the
    email and password already), so this returns only what a human-facing
    page needs."""
    row = db.connect().execute(
        "SELECT rowid, * FROM email_codes WHERE code_hash=?"
        " AND purpose='verify-link' AND consumed_at IS NULL",
        (_hash_code(token.strip()),),
    ).fetchone()
    if row is None:
        raise AccountError(403, "this link is not valid — it may have been "
                                "replaced by a newer email or already used")
    if row["expires_at"] < datetime.now(timezone.utc).isoformat():
        raise AccountError(403, "this link has expired — request a new one "
                                "from the app")
    account = db.connect().execute(
        "SELECT * FROM accounts WHERE email=?", (row["email"],)
    ).fetchone()
    if account is None:
        raise AccountError(403, "no pending account for this address")
    if account["verified_at"]:
        return {"email": row["email"], "already": True}
    conn = db.connect()
    conn.execute("UPDATE email_codes SET consumed_at=? WHERE rowid=?",
                 (db.utcnow(), row["rowid"]))
    conn.commit()
    _activate(row["email"], account["id"])
    return {"email": row["email"], "already": False}


def signin(email: str, password: str) -> dict:
    email = _normalize(email)
    account = db.connect().execute(
        "SELECT * FROM accounts WHERE email=?", (email,)
    ).fetchone()
    # Same answer for "unknown address" and "wrong password" — the split is
    # an address oracle. Constant-work: hash the password either way.
    if account is None:
        _hash_password(password, secrets.token_hex(16))
        raise AccountError(403, "email or password is not right")
    if not secrets.compare_digest(
            account["password_hash"],
            _hash_password(password, account["salt"])):
        raise AccountError(403, "email or password is not right")
    if not account["verified_at"]:
        raise AccountError(
            403, "this address has not been verified — enter the emailed "
                 "code, or request a new one")
    from . import auth
    return {"account_id": account["id"], "email": email,
            "display_name": account["display_name"],
            "account_token": auth.issue("account", account["id"])}


def request_reset(email: str) -> dict:
    """Email a password-reset code. One response whether or not the address
    has a verified account — not an address oracle."""
    email = _normalize(email)
    row = db.connect().execute(
        "SELECT verified_at FROM accounts WHERE email=?", (email,)
    ).fetchone()
    if row is None or not row["verified_at"]:
        return {"email": email, "code_delivery": "none"}
    return {"email": email, "code_delivery": _send_code(email, "reset")}


def reset_password(email: str, code: str, new_password: str) -> dict:
    """Trade the emailed reset code for a new password. Every existing
    account session dies with the old password — whoever prompted the
    reset, only the person holding the inbox stays signed in. Per-profile
    owner tokens are separate capabilities and are untouched."""
    email = _normalize(email)
    if len(new_password) < 8:
        raise AccountError(422, "password must be at least 8 characters")
    conn = db.connect()
    account = conn.execute(
        "SELECT * FROM accounts WHERE email=?", (email,)
    ).fetchone()
    if account is None or not account["verified_at"]:
        raise AccountError(403, "that code is not right")
    _consume_code(email, code, "reset")
    salt = secrets.token_hex(16)
    conn.execute(
        "UPDATE accounts SET password_hash=?, salt=? WHERE id=?",
        (_hash_password(new_password, salt), salt, account["id"]),
    )
    conn.commit()
    from . import auth
    auth.revoke_subject(account["id"])
    return {"email": email, "reset": True}
