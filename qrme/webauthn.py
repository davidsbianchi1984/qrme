"""WebAuthn primitives: parse what an authenticator returns, and verify it.

This is the layer that turns "the app says the user agreed" into something a
third party can check. Everything here operates on the raw bytes the
authenticator produced — no trust in the client that relayed them.

Deliberately dependency-light. WebAuthn uses CBOR in exactly two places
(the COSE public key and the attestation object) and needs a very small
subset of it: unsigned ints, negative ints, byte strings, text strings,
arrays, and maps. :func:`cbor_decode` implements that subset rather than
pulling in a CBOR library, and rejects anything outside it instead of
guessing — an authenticator sending a float where a key type belongs is a
thing to refuse, not to coerce.

Signature verification itself is real cryptography and uses ``cryptography``.
A module that parsed assertions but did not verify them would be worse than
no module at all: it would produce records that *look* like evidence.
"""

from __future__ import annotations

import base64
import hashlib
import json
import struct

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, padding, rsa
from cryptography.hazmat.primitives.asymmetric.utils import (
    encode_dss_signature)

# COSE algorithm identifiers we accept. ES256 is what every platform
# authenticator (Face ID, Touch ID, Optic ID, Android StrongBox) produces;
# RS256 appears on some older security keys.
ES256 = -7
RS256 = -257
SUPPORTED_ALGS = (ES256, RS256)

# Authenticator data flag bits.
FLAG_UP = 0x01   # user present (a tap)
FLAG_UV = 0x04   # user verified (the biometric or PIN) — the one that matters
FLAG_BE = 0x08   # backup eligible: this credential is allowed to sync
FLAG_BS = 0x10   # backed up: it currently exists in more than one place
FLAG_AT = 0x40   # attested credential data present (registration)
FLAG_ED = 0x80   # extension data present


class WebAuthnError(ValueError):
    """Anything malformed, unsupported, or failing verification."""


# --- base64url ------------------------------------------------------------

def b64url_decode(value: str) -> bytes:
    """Decode base64url without requiring the caller to have padded it —
    browsers and native SDKs disagree about the padding."""
    if not isinstance(value, str):
        raise WebAuthnError("expected a base64url string")
    pad = "=" * (-len(value) % 4)
    try:
        return base64.urlsafe_b64decode(value + pad)
    except Exception as exc:                       # pragma: no cover - defensive
        raise WebAuthnError(f"not valid base64url: {exc}") from exc


def b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


# --- minimal CBOR ---------------------------------------------------------

def _cbor_item(data: bytes, i: int) -> tuple[object, int]:
    if i >= len(data):
        raise WebAuthnError("CBOR ended mid-item")
    major, info = data[i] >> 5, data[i] & 0x1F
    i += 1

    if info < 24:
        value = info
    elif info == 24:
        value, i = data[i], i + 1
    elif info == 25:
        value, i = struct.unpack_from(">H", data, i)[0], i + 2
    elif info == 26:
        value, i = struct.unpack_from(">I", data, i)[0], i + 4
    elif info == 27:
        value, i = struct.unpack_from(">Q", data, i)[0], i + 8
    else:
        # Indefinite lengths, floats, and simple values. WebAuthn does not
        # use them; refusing is safer than improvising.
        raise WebAuthnError(f"unsupported CBOR additional info {info}")

    if major == 0:                                  # unsigned int
        return value, i
    if major == 1:                                  # negative int
        return -1 - value, i
    if major == 2:                                  # byte string
        return data[i:i + value], i + value
    if major == 3:                                  # text string
        return data[i:i + value].decode("utf-8"), i + value
    if major == 4:                                  # array
        items = []
        for _ in range(value):
            item, i = _cbor_item(data, i)
            items.append(item)
        return items, i
    if major == 5:                                  # map
        out: dict = {}
        for _ in range(value):
            key, i = _cbor_item(data, i)
            val, i = _cbor_item(data, i)
            if isinstance(key, bytes):
                raise WebAuthnError("CBOR map key must be int or text")
            out[key] = val
        return out, i
    raise WebAuthnError(f"unsupported CBOR major type {major}")


def cbor_decode(data: bytes) -> object:
    """Decode one CBOR item. Trailing bytes are an error — an attestation
    object with something appended is not an attestation object."""
    value, end = _cbor_item(data, 0)
    if end != len(data):
        raise WebAuthnError("trailing bytes after CBOR item")
    return value


def cbor_decode_prefix(data: bytes) -> tuple[object, int]:
    """Decode one CBOR item and report where it ended. Needed for the COSE
    key, which sits at the tail of attested credential data with no length
    prefix of its own."""
    return _cbor_item(data, 0)


# --- authenticator data ---------------------------------------------------

def parse_authenticator_data(raw: bytes) -> dict:
    """Break out the fixed header, the flags, and (on registration) the
    attested credential data.

    Layout: 32-byte rpIdHash, 1 flag byte, 4-byte big-endian signCount, then
    optionally 16-byte AAGUID, 2-byte credential id length, the credential
    id, and the COSE public key.
    """
    if len(raw) < 37:
        raise WebAuthnError("authenticator data is too short")
    flags = raw[32]
    out: dict = {
        "rp_id_hash": raw[:32],
        "flags": flags,
        "user_present": bool(flags & FLAG_UP),
        "user_verified": bool(flags & FLAG_UV),
        "backup_eligible": bool(flags & FLAG_BE),
        "backed_up": bool(flags & FLAG_BS),
        "sign_count": struct.unpack_from(">I", raw, 33)[0],
        "aaguid": None,
        "credential_id": None,
        "public_key": None,
    }
    if not flags & FLAG_AT:
        return out

    if len(raw) < 55:
        raise WebAuthnError("attested credential data is truncated")
    cred_len = struct.unpack_from(">H", raw, 53)[0]
    end = 55 + cred_len
    if len(raw) < end:
        raise WebAuthnError("credential id runs past the end of the data")
    out["aaguid"] = raw[37:53].hex()
    out["credential_id"] = raw[55:end]
    key, consumed = cbor_decode_prefix(raw[end:])
    if not isinstance(key, dict):
        raise WebAuthnError("COSE key is not a map")
    out["public_key"] = key
    # Extension data may follow the key; anything else is malformed.
    if not flags & FLAG_ED and end + consumed != len(raw):
        raise WebAuthnError("unexpected trailing bytes after the COSE key")
    return out


# --- COSE keys ------------------------------------------------------------

def cose_alg(key: dict) -> int:
    alg = key.get(3)
    if alg not in SUPPORTED_ALGS:
        raise WebAuthnError(
            f"unsupported COSE algorithm {alg!r}; this deployment accepts "
            "ES256 (-7) and RS256 (-257)")
    return alg


def cose_public_key(key: dict):
    """Build a verifying key from a COSE key map."""
    alg = cose_alg(key)
    if alg == ES256:
        if key.get(1) != 2 or key.get(-1) != 1:
            raise WebAuthnError("ES256 key must be EC2 over P-256")
        x, y = key.get(-2), key.get(-3)
        if not isinstance(x, bytes) or not isinstance(y, bytes):
            raise WebAuthnError("ES256 key is missing its coordinates")
        return ec.EllipticCurvePublicNumbers(
            int.from_bytes(x, "big"), int.from_bytes(y, "big"),
            ec.SECP256R1()).public_key()
    if key.get(1) != 3:
        raise WebAuthnError("RS256 key must be of type RSA")
    n, e = key.get(-1), key.get(-2)
    if not isinstance(n, bytes) or not isinstance(e, bytes):
        raise WebAuthnError("RS256 key is missing its modulus or exponent")
    return rsa.RSAPublicNumbers(int.from_bytes(e, "big"),
                                int.from_bytes(n, "big")).public_key()


def cose_key_to_json(key: dict) -> str:
    """Store the COSE key as JSON so a signature stays verifiable after the
    credential itself is deleted. Byte values become hex; the integer keys
    become strings, because that is what JSON permits."""
    return json.dumps({str(k): (v.hex() if isinstance(v, bytes) else v)
                       for k, v in sorted(key.items(), key=lambda kv: str(kv[0]))})


def cose_key_from_json(blob: str) -> dict:
    raw = json.loads(blob)
    return {int(k): (bytes.fromhex(v) if isinstance(v, str) else v)
            for k, v in raw.items()}


# --- verification ---------------------------------------------------------

def verify_signature(key: dict, signature: bytes, signed: bytes) -> None:
    """Raise :class:`WebAuthnError` unless ``signature`` covers ``signed``."""
    alg = cose_alg(key)
    public = cose_public_key(key)
    try:
        if alg == ES256:
            public.verify(signature, signed, ec.ECDSA(hashes.SHA256()))
        else:
            public.verify(signature, signed, padding.PKCS1v15(),
                          hashes.SHA256())
    except InvalidSignature as exc:
        raise WebAuthnError(
            "the signature does not verify against this credential's public "
            "key — the assertion was not produced by this authenticator, or "
            "the signed data has been altered") from exc


def signed_bytes(authenticator_data: bytes, client_data_json: bytes) -> bytes:
    """What an authenticator actually signs: the authenticator data,
    concatenated with the SHA-256 of the client data."""
    return authenticator_data + hashlib.sha256(client_data_json).digest()


def parse_client_data(raw: bytes, expected_type: str, expected_challenge: str,
                      allowed_origins: list[str] | None = None) -> dict:
    """Validate the client data blob against what we asked for.

    The challenge comparison is the load-bearing one: it is what ties this
    assertion to the specific thing being signed rather than to any earlier
    ceremony the same credential performed.
    """
    try:
        data = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise WebAuthnError(f"client data is not JSON: {exc}") from exc
    if data.get("type") != expected_type:
        raise WebAuthnError(
            f"client data type is {data.get('type')!r}, expected "
            f"{expected_type!r} — an assertion from a sign-in ceremony cannot "
            "stand in for a signing ceremony")
    if data.get("challenge") != expected_challenge:
        raise WebAuthnError(
            "the challenge in the client data is not the one this envelope "
            "issued — this assertion signs something else")
    if allowed_origins and data.get("origin") not in allowed_origins:
        raise WebAuthnError(
            f"origin {data.get('origin')!r} is not permitted for this "
            "deployment")
    return data


def der_from_raw_ecdsa(raw: bytes) -> bytes:
    """Convert a 64-byte r||s signature to DER.

    Web clients hand back DER already. Some native SDKs (and test harnesses
    built on raw primitives) produce the fixed-width form, so accept both
    rather than failing on a signature that is perfectly valid.
    """
    if len(raw) != 64:
        raise WebAuthnError("raw ECDSA signature must be 64 bytes")
    return encode_dss_signature(int.from_bytes(raw[:32], "big"),
                                int.from_bytes(raw[32:], "big"))
