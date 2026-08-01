"""The credential that stops working on a date nobody wrote down.

## The finding

`qrme/oauth.py` treats both providers the same way: two environment
variables, and a grey button with the reason if they are missing. That is
right for Google, whose client secret is a string you copy once.

It is wrong for Apple, and the difference is not cosmetic.
`QRME_APPLE_CLIENT_SECRET` is an **ES256 JWT you sign yourself**, and Apple
caps its lifetime at six months. Nothing renews it. Nothing warns. The
console's own honesty check — `providers()` — asks whether the variable is
*set*, which stays true forever:

    asked     is Apple sign-in configured
    mattered  is Apple sign-in going to work tomorrow

An expired secret is a configured secret. Every check in this repo reported
the door open while the token exchange answered `invalid_client` to every
person who pressed the button.

## What this file checks

`scripts/mint_apple_secret.py` mints the thing and reads its expiry. The
tests below exercise the two places it can be quietly wrong:

* **The signature encoding.** `cryptography` returns ECDSA signatures
  DER-encoded; JWS wants raw `r || s`, fixed at 32 bytes each. A DER
  signature is the right length often enough to pass a length check and is
  refused by Apple with the same `invalid_client` an expired token gives.
  So the test *verifies the signature with the public key* rather than
  measuring it.
* **The ceiling.** A lifetime past six months mints fine and fails at the
  exchange — the worst place to learn it.
"""

from __future__ import annotations

import base64
import datetime as dt
import importlib.util
import json
from pathlib import Path

import pytest

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, utils


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()
SCRIPT = REPO / "scripts" / "mint_apple_secret.py"


def _module():
    """Loaded by path: `scripts/` is a directory of operator tools, not a
    package, and making it importable would put it on the install surface."""
    spec = importlib.util.spec_from_file_location("mint_apple_secret", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def minter():
    return _module()


@pytest.fixture(scope="module")
def keypair():
    """A P-256 key of the shape Apple issues. Generated here — no `.p8` from
    a real account is in this repo, and none should be."""
    private = ec.generate_private_key(ec.SECP256R1())
    pem = private.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption()).decode()
    return private.public_key(), pem


def _segments(token: str) -> tuple[dict, dict, bytes]:
    def un(part: str) -> bytes:
        return base64.urlsafe_b64decode(part + "=" * (-len(part) % 4))
    head, body, sig = token.split(".")
    return json.loads(un(head)), json.loads(un(body)), un(sig)


def test_apple_would_accept_the_signature(minter, keypair):
    """The check the length test cannot make.

    Apple verifies this signature with the public half of the `.p8`. So does
    this test, against the same bytes Apple hashes — the `header.payload`
    string, not the token. A DER signature reaches here intact and fails,
    which is the whole point of not measuring it instead.
    """
    public, pem = keypair
    token = minter.mint(team_id="A1B2C3D4E5", key_id="F6G7H8I9J0",
                        services_id="app.qrme.signin", private_key_pem=pem)
    _, _, raw = _segments(token)
    assert len(raw) == 64, (
        f"the signature is {len(raw)} bytes. JWS ES256 is exactly 64 — two "
        "32-byte integers. A DER-encoded signature lands around 70 and is "
        "refused by Apple as invalid_client, indistinguishable from an "
        "expired secret.")

    signing_input = token.rsplit(".", 1)[0].encode()
    der = utils.encode_dss_signature(
        int.from_bytes(raw[:32], "big"), int.from_bytes(raw[32:], "big"))
    public.verify(der, signing_input, ec.ECDSA(hashes.SHA256()))


def test_the_claims_are_the_ones_apple_reads(minter, keypair):
    """Each of these five has its own failure, and all five fail the same
    way at the exchange, so they are checked by name rather than by count."""
    _, pem = keypair
    now = 1_800_000_000
    token = minter.mint(team_id="A1B2C3D4E5", key_id="F6G7H8I9J0",
                        services_id="app.qrme.signin", private_key_pem=pem,
                        issued_at=now)
    header, payload, _ = _segments(token)
    assert header["alg"] == "ES256"
    assert header["kid"] == "F6G7H8I9J0", (
        "the Key ID lives in the header, not the payload — Apple uses it to "
        "pick which of your keys to verify with, and a missing one means it "
        "cannot pick at all")
    assert payload["iss"] == "A1B2C3D4E5", "iss is the Team ID"
    assert payload["sub"] == "app.qrme.signin", (
        "sub is the Services ID, and must equal the client_id sent to the "
        "token endpoint — QRME_APPLE_CLIENT_ID")
    assert payload["aud"] == "https://appleid.apple.com", (
        "a token signed for another audience is a token for somebody else")
    assert payload["iat"] == now
    assert payload["exp"] == now + minter.MAX_LIFETIME_SECONDS


def test_a_lifetime_apple_refuses_is_refused_here(minter, keypair):
    """Minting is local, so an over-long token mints happily and dies at the
    exchange. Better to refuse where the operator is looking."""
    _, pem = keypair
    with pytest.raises(ValueError, match="six-month ceiling"):
        minter.mint(team_id="A1B2C3D4E5", key_id="K", services_id="s",
                    private_key_pem=pem,
                    lifetime_seconds=minter.MAX_LIFETIME_SECONDS + 1)
    with pytest.raises(ValueError, match="already expired"):
        minter.mint(team_id="A1B2C3D4E5", key_id="K", services_id="s",
                    private_key_pem=pem, lifetime_seconds=0)


def test_the_wrong_kind_of_key_is_named_as_such(minter):
    """An RSA `.p8` from a different Apple service loads fine and cannot sign
    ES256. The message should say which key was expected, not raise from
    inside the signing call."""
    from cryptography.hazmat.primitives.asymmetric import rsa
    pem = rsa.generate_private_key(
        public_exponent=65537, key_size=2048).private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption()).decode()
    with pytest.raises(ValueError, match="elliptic-curve"):
        minter.mint(team_id="A", key_id="K", services_id="s",
                    private_key_pem=pem)


def test_the_expiry_can_be_read_without_the_key(minter, keypair):
    """The operator checking whether sign-in is about to break has the
    environment variable and not the `.p8`. That has to be enough."""
    _, pem = keypair
    now = 1_800_000_000
    token = minter.mint(team_id="A1B2C3D4E5", key_id="F6G7H8I9J0",
                        services_id="app.qrme.signin", private_key_pem=pem,
                        issued_at=now, lifetime_seconds=40 * 86400)
    fresh = minter.inspect(token, now=now)
    assert fresh["days_remaining"] == 40
    assert not fresh["expired"] and not fresh["expiring_soon"]
    assert fresh["services_id"] == "app.qrme.signin"
    assert fresh["key_id"] == "F6G7H8I9J0"

    soon = minter.inspect(token, now=now + 20 * 86400)
    assert soon["expiring_soon"] and not soon["expired"], (
        "twenty days out is inside the warning window; a secret that only "
        "reports trouble once it is already broken reports it too late")

    dead = minter.inspect(token, now=now + 41 * 86400)
    assert dead["expired"] and dead["days_remaining"] < 0


def test_something_that_is_not_a_token_says_so(minter):
    with pytest.raises(ValueError, match="not a JWT"):
        minter.inspect("/Users/me/AuthKey_F6G7H8I9J0.p8")


def test_the_check_subcommand_exits_nonzero_on_an_expired_secret(minter,
                                                                 keypair,
                                                                 capsys):
    """This is what a deployment's health check would call. An expiry that
    prints a warning and exits 0 is a warning nothing reads.

    The mint path is not driven here — it needs a `.p8` on disk — but the
    exit code is the contract an operator wires into cron.
    """
    _, pem = keypair
    past = int(dt.datetime.now(dt.timezone.utc).timestamp()) - 10 * 86400
    token = minter.mint(team_id="A1B2C3D4E5", key_id="F6G7H8I9J0",
                        services_id="app.qrme.signin", private_key_pem=pem,
                        issued_at=past - 86400, lifetime_seconds=86400)
    assert minter.main(["check", "--secret", token]) == 1
    out = capsys.readouterr()
    assert "invalid_client" in out.err, (
        "the failure Apple actually reports should be in the message — an "
        "operator searching their logs for invalid_client should land here")

    good = minter.mint(team_id="A1B2C3D4E5", key_id="F6G7H8I9J0",
                       services_id="app.qrme.signin", private_key_pem=pem)
    assert minter.main(["check", "--secret", good]) == 0


def test_no_private_key_has_wandered_into_the_repo():
    """A guard on the process rather than the code.

    Apple lets you download the `.p8` once, which is exactly the pressure
    that puts it somewhere convenient — and this repo is public. The file is
    small, unremarkable, and grep-invisible unless somebody looks for it.
    """
    strays = [p for p in REPO.rglob("*.p8")
              if ".git" not in p.parts and "node_modules" not in p.parts]
    assert not strays, (
        "these look like Apple private keys and are inside the repository:\n"
        + "\n".join(f"    {p.relative_to(REPO)}" for p in strays)
        + "\n  Revoke the key in the developer console before removing the "
          "file — a committed key is disclosed whether or not the commit is "
          "reverted.")
