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
    return mailer.public_url()


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


def signin(email: str, password: str,
           adopt_interactor_id: str | None = None) -> dict:
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
    # A stranger who has been talking becomes this account's person, rather
    # than being replaced by a fresh one who has met nobody.
    if adopt_interactor_id:
        who = adopt(account["id"], adopt_interactor_id)
    else:
        who = interactor_for(account["id"], account["display_name"])
    return {"account_id": account["id"], "email": email,
            "display_name": account["display_name"],
            "account_token": auth.issue("account", account["id"]),
            # The person, not the browser. Folded into this response rather
            # than given a route of its own: a client that has just signed in
            # is exactly the client that needs it, and a second door would be
            # one more thing a shell could forget to knock on — which is how
            # one client ends up the odd one out.
            "interactor_id": who["id"],
            "interactor_token": auth.issue("interactor", who["id"])}


def interactor_for(account_id: str, display_name: str | None = None) -> dict:
    """This account's person, made once and returned thereafter.

    Memory is keyed on (profile, interactor). While an interactor was minted
    per device and kept in local storage, a profile remembered the browser
    rather than the human: sign in on a phone after a week on the desktop and
    a starter you had talked to for an hour had never met you.

        asked     does the profile remember the conversation
        mattered  does it remember the person

    Idempotent on purpose. Signing in twice must not produce two people, or
    the fix would reintroduce the defect with extra steps — the second one
    would be a stranger again.
    """
    conn = db.connect()
    row = conn.execute(
        "SELECT * FROM interactors WHERE account_id=?"
        " ORDER BY created_at LIMIT 1", (account_id,)).fetchone()
    if row is not None:
        return dict(row)
    interactor_id = db.new_id("usr")
    conn.execute(
        "INSERT INTO interactors (id, display_name, account_id, created_at)"
        " VALUES (?,?,?,?)",
        (interactor_id, (display_name or "").strip() or "You", account_id,
         db.utcnow()))
    conn.commit()
    return dict(conn.execute("SELECT * FROM interactors WHERE id=?",
                             (interactor_id,)).fetchone())


def adopt(account_id: str, interactor_id: str) -> dict:
    """Bind an interactor this device already had to the account signing in.

    The upgrade path, and the reason it matters: somebody talks to three
    starters as a stranger, then makes an account. Minting a fresh person at
    that moment would throw away every conversation they had just had — the
    account would be the moment their history was deleted, which is the worst
    possible time for it.

    Refused when the interactor already belongs to somebody else. An
    unattached interactor is a device's; one with an account is a person's,
    and moving it would hand one person's remembered conversations to
    another.
    """
    conn = db.connect()
    row = conn.execute("SELECT * FROM interactors WHERE id=?",
                       (interactor_id,)).fetchone()
    if row is None:
        raise AccountError(404, "no such person on this device")
    if row["account_id"] and row["account_id"] != account_id:
        raise AccountError(403, "that person belongs to another account")
    conn.execute("UPDATE interactors SET account_id=? WHERE id=?",
                 (account_id, interactor_id))
    conn.commit()
    return dict(conn.execute("SELECT * FROM interactors WHERE id=?",
                             (interactor_id,)).fetchone())


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


def held_profiles(account_id: str) -> dict:
    """Every profile this account holds — the roster, reached by signing in.

    ``identity.roster`` already answers this question and is already the most
    sensitive read in that module: one call that links a person's profiles to
    each other is the whole of what anonymity between them protects. Its route
    therefore refuses to be keyed on ``owner_id``, and says why — *`owner_id`
    is a string somebody chooses, not a secret* — so it asks for a profile
    whose owner token the caller already holds and derives the account from
    that.

    Which leaves the person who holds none. Owner tokens are minted once, at
    profile creation, and handed to whichever client did the creating; there
    was no way to ask for another. Somebody who reinstalled, or who created
    the profile in the phone app and is now standing in front of the console,
    could not enumerate their own profiles and could not open a single one.

        asked     where do I find my owner token
        mattered  the roster was reachable only by holding one already

    This is the same read through the credential such a person *does* have.
    The account token is minted by signing in with an email and a password —
    a secret, unlike ``owner_id`` — so the objection to keying on the account
    is answered by what proves the caller, not by what is in the path.
    """
    from . import identity
    return identity.roster(account_id)


def owner_token_for(account_id: str, profile_id: str) -> dict:
    """Mint a fresh owner capability for a profile this account holds.

    Deliberately not part of the listing above. A roster is a read and this is
    a grant, and the moment they travel together every screen that shows a
    person their own profiles is also handing out the capability to control
    them — which is the shape ``qrme/dock.py`` already refuses in one line:
    *nothing that authorises anything belongs on a surface*.

    Additive, never a rotation. The tokens already out there — in the phone
    that created the profile, in a Guardian that was linked last year — keep
    working, because a person recovering access to a profile has not said
    anything about the devices already holding it. Revoking everything is a
    different intent with a different door (``auth.revoke_subject``), and
    conflating the two would mean recovering access on a laptop silently
    unlinked their Guardian.
    """
    from . import auth
    row = db.connect().execute(
        "SELECT owner_id FROM profiles WHERE id=?", (profile_id,)).fetchone()
    if row is None:
        raise AccountError(404, "no such profile")
    if row["owner_id"] != account_id:
        # Same answer as a missing profile, and for the usual reason: a
        # distinguishable 403 turns this into an oracle for which profile ids
        # exist on a deployment.
        raise AccountError(404, "no such profile")
    return {"profile_id": profile_id,
            "owner_token": auth.issue("owner", profile_id),
            "shown_once": True}
