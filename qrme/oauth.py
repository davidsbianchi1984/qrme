"""Sign in with Google or Apple — the account door for people without a
password to type.

Configuration, not code, decides whether the buttons are live: the deployment
operator registers an OAuth client with the provider and sets the environment
variables below. Unconfigured providers say so honestly — a grey button with
the reason beats a working-looking button that dead-ends.

The flow is the desktop-friendly authorization-code shape:

1. ``start()`` mints a state and hands back the provider's authorize URL. The
   console opens it in the system browser.
2. The provider redirects to this API's ``/auth/oauth/{provider}/callback``
   (loopback works for Google's desktop clients; Apple requires a registered
   https return URL, which the note says plainly). The code is exchanged for
   an ``id_token`` **directly with the provider over TLS** — which is why
   parsing its payload without a signature check is sound here: the token
   arrives from the issuer itself, not from the user.
3. The email arrives provider-verified, so the account skips the emailed-code
   dance — the provider already did that work. The result parks under the
   state, and the console claims it once at ``/auth/oauth/claim``.

Passwordless accounts get a random unguessable password hash: ``signin()``
with any typed password fails closed, and the password-reset flow remains the
one way to add a typed password later.
"""

from __future__ import annotations

import base64
import json
import os
import secrets
import urllib.parse
import urllib.request

from . import db

_STATE_TTL_MIN = 10


class OAuthError(Exception):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(message)


def _env(name: str) -> str | None:
    value = os.environ.get(name, "").strip()
    return value or None


def _providers() -> dict[str, dict]:
    return {
        "google": {
            "name": "Google",
            "client_id": _env("QRME_GOOGLE_CLIENT_ID"),
            "client_secret": _env("QRME_GOOGLE_CLIENT_SECRET"),
            "authorize": "https://accounts.google.com/o/oauth2/v2/auth",
            "token": "https://oauth2.googleapis.com/token",
            "scope": "openid email profile",
            "setup": "register an OAuth client at console.cloud.google.com "
                     "and set QRME_GOOGLE_CLIENT_ID / "
                     "QRME_GOOGLE_CLIENT_SECRET",
        },
        "apple": {
            "name": "Apple",
            "client_id": _env("QRME_APPLE_CLIENT_ID"),
            "client_secret": _env("QRME_APPLE_CLIENT_SECRET"),
            "authorize": "https://appleid.apple.com/auth/authorize",
            "token": "https://appleid.apple.com/auth/token",
            "scope": "email",
            "setup": "register a Services ID at developer.apple.com, mint "
                     "the client-secret JWT, and set QRME_APPLE_CLIENT_ID / "
                     "QRME_APPLE_CLIENT_SECRET — Apple also requires an "
                     "https return URL, so the deployment must be reachable "
                     "over https",
        },
    }


def providers() -> dict:
    """Which doors are live on this deployment, and how to open the rest."""
    out = []
    for key, spec in _providers().items():
        configured = bool(spec["client_id"] and spec["client_secret"])
        entry = {"provider": key, "name": spec["name"],
                 "configured": configured}
        if not configured:
            entry["setup"] = spec["setup"]
        out.append(entry)
    return {"providers": out}


def _spec(provider: str) -> dict:
    spec = _providers().get(provider)
    if spec is None:
        raise OAuthError(404, f"no such provider {provider!r}")
    if not (spec["client_id"] and spec["client_secret"]):
        raise OAuthError(503, f"{spec['name']} sign-in is not configured on "
                              f"this deployment — {spec['setup']}")
    return spec


def start(provider: str, redirect_uri: str) -> dict:
    """Mint a state and the provider's authorize URL."""
    spec = _spec(provider)
    state = secrets.token_urlsafe(24)
    conn = db.connect()
    conn.execute(
        "INSERT INTO oauth_states (state, provider, redirect_uri, created_at)"
        " VALUES (?,?,?,?)", (state, provider, redirect_uri, db.utcnow()))
    conn.commit()
    params = {
        "client_id": spec["client_id"],
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": spec["scope"],
        "state": state,
    }
    if provider == "apple":
        params["response_mode"] = "query"
    return {"provider": provider, "state": state,
            "url": f"{spec['authorize']}?{urllib.parse.urlencode(params)}"}


def _exchange(spec: dict, code: str, redirect_uri: str) -> dict:
    """Trade the code for tokens at the provider — the one outbound call."""
    from . import offline
    if offline.enabled():
        raise OAuthError(503, "offline mode: no request leaves this host, "
                              "including a token exchange")
    body = urllib.parse.urlencode({
        "client_id": spec["client_id"],
        "client_secret": spec["client_secret"],
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
    }).encode()
    req = urllib.request.Request(
        spec["token"], data=body,
        headers={"content-type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=15) as resp:   # noqa: S310
        return json.loads(resp.read().decode())


def _id_token_claims(id_token: str) -> dict:
    """The payload of an id_token that just arrived from the issuer itself
    over TLS — see the module docstring for why no signature check here."""
    try:
        payload = id_token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        return json.loads(base64.urlsafe_b64decode(payload))
    except Exception as exc:
        raise OAuthError(502, "the provider's token could not be read") from exc


def callback(provider: str, code: str, state: str,
             exchange=None) -> dict:
    """Complete the flow: verify the state, exchange the code, land the
    account, and park the session for the console to claim."""
    spec = _spec(provider)
    conn = db.connect()
    row = conn.execute(
        "SELECT * FROM oauth_states WHERE state=? AND provider=?"
        " AND claimed_at IS NULL AND result IS NULL",
        (state, provider)).fetchone()
    if row is None:
        raise OAuthError(403, "unknown or already-used state — start over "
                              "from the sign-in screen")

    tokens = (exchange or _exchange)(spec, code, row["redirect_uri"])
    claims = _id_token_claims(tokens.get("id_token", ""))
    email = (claims.get("email") or "").strip().lower()
    if not email:
        raise OAuthError(502, f"{spec['name']} returned no email address")

    from . import accounts, auth
    account = conn.execute("SELECT * FROM accounts WHERE email=?",
                           (email,)).fetchone()
    if account is None:
        account_id = db.new_id("act")
        # A random hash nothing can ever match: password sign-in fails
        # closed until the user sets one through the reset flow.
        salt = secrets.token_hex(16)
        conn.execute(
            "INSERT INTO accounts (id, email, password_hash, salt,"
            " display_name, verified_at, created_at) VALUES (?,?,?,?,?,?,?)",
            (account_id, email,
             accounts._hash_password(secrets.token_urlsafe(32), salt), salt,
             claims.get("name"), db.utcnow(), db.utcnow()))
    else:
        account_id = account["id"]
        if not account["verified_at"]:
            # The provider vouched for the inbox; that is the verification.
            conn.execute("UPDATE accounts SET verified_at=? WHERE id=?",
                         (db.utcnow(), account_id))

    result = {"account_id": account_id, "email": email,
              "display_name": claims.get("name"),
              "account_token": auth.issue("account", account_id)}
    conn.execute("UPDATE oauth_states SET result=? WHERE state=?",
                 (json.dumps(result), state))
    conn.commit()
    return {"provider": provider, "email": email}


def claim(state: str) -> dict:
    """One-time pickup of a completed sign-in, then the state is spent."""
    conn = db.connect()
    row = conn.execute(
        "SELECT * FROM oauth_states WHERE state=? AND claimed_at IS NULL",
        (state,)).fetchone()
    if row is None:
        raise OAuthError(403, "unknown or already-claimed state")
    if not row["result"]:
        return {"ready": False}
    conn.execute("UPDATE oauth_states SET claimed_at=? WHERE state=?",
                 (db.utcnow(), state))
    conn.commit()
    return {"ready": True, **json.loads(row["result"])}
