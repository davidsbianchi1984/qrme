#!/usr/bin/env python3
"""Mint ``QRME_APPLE_CLIENT_SECRET`` — and say when it dies.

Google's client secret is a string you copy once and keep. Apple's is not a
secret at all in that sense: it is an **ES256 JWT you sign yourself**, from a
``.p8`` private key, and Apple caps its lifetime at six months. There is no
renewal notice, no warning banner, and nothing in the sign-in flow degrades
early. On the day it expires the token exchange starts answering
``invalid_client`` and "Sign in with Apple" simply stops working, for
everyone, with a message that points at the client rather than the calendar.

That is the failure this file exists to prevent, so it does two things:

``mint``
    Sign a fresh secret from the ``.p8``. Refuses a lifetime Apple will
    reject rather than minting a token that fails at the exchange.

``check``
    Read an existing secret — the one in the deployment's environment right
    now — and print the days left. No key needed: the expiry is in the
    payload, which is base64url, not encryption.

Neither subcommand talks to Apple. Minting is local signing; nothing leaves
the host.

## The two gotchas, both real

**The signature is raw, not DER.** ``cryptography`` returns ECDSA signatures
DER-encoded, which is correct for X.509 and wrong for JWS. JWS wants the two
integers concatenated, fixed-width, 32 bytes each — 64 bytes total. A DER
signature is well-formed, verifies with the wrong tool, and is rejected by
Apple with the same ``invalid_client`` an expired token gives you.

**The `.p8` is the key, and it is the only copy.** Apple lets you download it
once. It is not in this repo, it does not belong in this repo, and this
script reads it from a path rather than taking it as an argument so it does
not end up in a shell history.

Usage::

    python scripts/mint_apple_secret.py mint \\
        --team-id A1B2C3D4E5 --key-id F6G7H8I9J0 \\
        --services-id app.qrme.signin \\
        --key ~/keys/AuthKey_F6G7H8I9J0.p8

    python scripts/mint_apple_secret.py check --secret "$QRME_APPLE_CLIENT_SECRET"

See ``docs/sign-in.md`` for where each of those three identifiers is found in
Apple's console, and for the Google half.
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import sys
from pathlib import Path

#: Apple's own ceiling: "the value must not be greater than 6 months from the
#: current time". 15777000 seconds is the figure Apple's documentation uses —
#: half a Julian year. A token minted past it is refused at the exchange, not
#: at minting time, which is the worst place to find out.
MAX_LIFETIME_SECONDS = 15777000

#: Apple's audience, fixed. Not a deployment setting: a token signed for any
#: other audience is a token for somebody else.
AUDIENCE = "https://appleid.apple.com"

#: How long before expiry this script starts calling the secret a problem.
#: Thirty days is enough to notice, find the `.p8`, and re-mint without the
#: sign-in door being shut while you look.
WARN_WITHIN_DAYS = 30


def _b64(raw: bytes) -> str:
    """base64url, unpadded — what JWS uses everywhere."""
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def _unb64(segment: str) -> bytes:
    return base64.urlsafe_b64decode(segment + "=" * (-len(segment) % 4))


def mint(*, team_id: str, key_id: str, services_id: str, private_key_pem: str,
         lifetime_seconds: int = MAX_LIFETIME_SECONDS,
         issued_at: int | None = None) -> str:
    """The signed client secret, as a compact JWS.

    ``services_id`` is the Services ID — the same value that goes in
    ``QRME_APPLE_CLIENT_ID``. Apple checks that ``sub`` and the ``client_id``
    sent to the token endpoint are the same string; a mismatch is another
    ``invalid_client``.
    """
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ec, utils

    if lifetime_seconds > MAX_LIFETIME_SECONDS:
        raise ValueError(
            f"{lifetime_seconds}s is longer than Apple's six-month ceiling "
            f"({MAX_LIFETIME_SECONDS}s). Apple refuses the token at the "
            "exchange, so a longer lifetime buys nothing and costs a "
            "sign-in door that looks configured and is not.")
    if lifetime_seconds <= 0:
        raise ValueError("a secret that has already expired is not a secret")

    key = serialization.load_pem_private_key(private_key_pem.encode(),
                                             password=None)
    if not isinstance(key, ec.EllipticCurvePrivateKey):
        raise ValueError(
            "that .p8 does not hold an elliptic-curve key — Apple's "
            "Sign in with Apple keys are P-256, and ES256 cannot be signed "
            "with anything else")
    if key.curve.name != "secp256r1":
        raise ValueError(
            f"the key is on curve {key.curve.name}; ES256 means P-256 "
            "(secp256r1) and Apple issues no other kind")

    now = int(dt.datetime.now(dt.timezone.utc).timestamp()) \
        if issued_at is None else issued_at
    header = {"alg": "ES256", "kid": key_id, "typ": "JWT"}
    payload = {
        "iss": team_id,
        "iat": now,
        "exp": now + lifetime_seconds,
        "aud": AUDIENCE,
        "sub": services_id,
    }
    signing_input = ".".join([
        _b64(json.dumps(header, separators=(",", ":")).encode()),
        _b64(json.dumps(payload, separators=(",", ":")).encode()),
    ])

    der = key.sign(signing_input.encode(), ec.ECDSA(hashes.SHA256()))
    r, s = utils.decode_dss_signature(der)
    # Fixed-width, 32 bytes each. `to_bytes` pads on the left, which is what
    # JWS wants; a short r written without padding shifts every byte of s and
    # produces a signature that is the right length only most of the time.
    raw = r.to_bytes(32, "big") + s.to_bytes(32, "big")
    return f"{signing_input}.{_b64(raw)}"


def inspect(secret: str, *, now: int | None = None) -> dict:
    """What an existing secret says about itself.

    Signature unchecked on purpose: this answers "when does the deployment's
    sign-in stop working", and that answer is in the payload. Verifying would
    need the `.p8`, which is exactly what the person checking an expiry does
    not want to have to find.
    """
    parts = secret.strip().split(".")
    if len(parts) != 3:
        raise ValueError(
            "that is not a JWT — a client secret has three dot-separated "
            "parts. If it looks like a filename, pass the file's contents.")
    try:
        header = json.loads(_unb64(parts[0]))
        payload = json.loads(_unb64(parts[1]))
    except Exception as exc:                     # noqa: BLE001 - reported
        raise ValueError(f"the token's segments do not decode: {exc}") from exc

    at = int(dt.datetime.now(dt.timezone.utc).timestamp()) if now is None \
        else now
    exp = int(payload.get("exp", 0))
    remaining = exp - at
    return {
        "team_id": payload.get("iss"),
        "services_id": payload.get("sub"),
        "key_id": header.get("kid"),
        "audience": payload.get("aud"),
        "algorithm": header.get("alg"),
        "expires_at": dt.datetime.fromtimestamp(
            exp, dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "seconds_remaining": remaining,
        "days_remaining": remaining // 86400,
        "expired": remaining <= 0,
        "expiring_soon": 0 < remaining <= WARN_WITHIN_DAYS * 86400,
    }


def _mint_cmd(args: argparse.Namespace) -> int:
    key_path = Path(args.key).expanduser()
    if not key_path.exists():
        print(f"no key at {key_path}. Apple lets you download the .p8 once; "
              "if it is gone, revoke that key in the developer console and "
              "create a new one — the Key ID changes with it.",
              file=sys.stderr)
        return 2
    secret = mint(team_id=args.team_id, key_id=args.key_id,
                  services_id=args.services_id,
                  private_key_pem=key_path.read_text(encoding="utf-8"),
                  lifetime_seconds=args.days * 86400)
    facts = inspect(secret)
    print(secret)
    print(f"\n  expires {facts['expires_at']} "
          f"({facts['days_remaining']} days). Re-mint before then — nothing "
          "warns you.\n"
          "  Set it as QRME_APPLE_CLIENT_SECRET, alongside "
          f"QRME_APPLE_CLIENT_ID={args.services_id}", file=sys.stderr)
    return 0


def _check_cmd(args: argparse.Namespace) -> int:
    facts = inspect(args.secret)
    width = max(len(k) for k in facts)
    for key, value in facts.items():
        print(f"  {key:<{width}}  {value}")
    if facts["expired"]:
        print("\n  EXPIRED. Sign in with Apple is refusing every exchange on "
              "this deployment with invalid_client.", file=sys.stderr)
        return 1
    if facts["expiring_soon"]:
        print(f"\n  Expires in {facts['days_remaining']} days. Re-mint now; "
              "the failure mode is total and silent until it happens.",
              file=sys.stderr)
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="mint_apple_secret",
        description=__doc__.split("\n\n")[0],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    subs = parser.add_subparsers(dest="command", required=True)

    m = subs.add_parser("mint", help="sign a fresh client secret from a .p8")
    m.add_argument("--team-id", required=True,
                   help="the ten-character Team ID, top right of "
                        "developer.apple.com (Membership details)")
    m.add_argument("--key-id", required=True,
                   help="the Key ID of the Sign in with Apple key — it is "
                        "also in the .p8 filename, AuthKey_<KEYID>.p8")
    m.add_argument("--services-id", required=True,
                   help="the Services ID identifier, e.g. app.qrme.signin — "
                        "the same value as QRME_APPLE_CLIENT_ID")
    m.add_argument("--key", required=True,
                   help="path to the .p8 file (never a literal key: this "
                        "keeps it out of your shell history)")
    m.add_argument("--days", type=int, default=MAX_LIFETIME_SECONDS // 86400,
                   help="lifetime in days (default: Apple's maximum)")
    m.set_defaults(func=_mint_cmd)

    c = subs.add_parser("check",
                        help="report the expiry of an existing secret")
    c.add_argument("--secret", required=True,
                   help='the current QRME_APPLE_CLIENT_SECRET')
    c.set_defaults(func=_check_cmd)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except ValueError as exc:
        print(f"{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":                      # pragma: no cover
    raise SystemExit(main())
