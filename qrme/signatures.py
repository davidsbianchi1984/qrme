"""Signatures: the same Face ID gesture, an artifact that survives dispute.

The design is specified in [docs/signatures.md](../docs/signatures.md). This
module implements it. Three ideas carry the whole thing:

**The challenge is the document.** In sign-in, a challenge is a random nonce
proving freshness. Here it is the SHA-256 of a canonical payload that names
the document hash, the meaning of the signature, the signer, and an expiry.
The authenticator signs over that, so the resulting assertion binds a
verified human gesture to *this record and no other*. Change one byte of the
document and verification fails.

**Enrollment is what makes the key stand for a person.** A passkey proves a
credential was used; it says nothing about who used it. So proofing level is
recorded at enrollment and checked against a per-tier minimum before a
signature is accepted — a self-asserted credential cannot sign a care
handoff, and it fails at the server rather than in a policy document.

**The evidence outlives the credential.** The public key is copied into the
signature row. A user who deletes their passkey tomorrow does not thereby
make everything they ever signed unverifiable, which is what would happen if
verification depended on a lookup.

What this does *not* prove is in the spec, and stays there: chiefly that
WebAuthn has no trusted display, so nothing here can attest to what appeared
on the signer's screen. :func:`request` stores the exact rendered text so a
dispute reproduces the screen instead of arguing about it, and the high tier
requires a second device — a surface the presenting app cannot paint over.
"""

from __future__ import annotations

import hashlib
import json
import secrets
from datetime import datetime, timedelta, timezone

from . import db, i18n, webauthn

# --- policy ---------------------------------------------------------------

# Ordered weakest to strongest. A tier's minimum is satisfied by its own
# level or anything above it.
PROOFING_LEVELS = ("self_asserted", "federated", "document", "in_person")

TIERS: dict[str, dict] = {
    # Good for nothing that will be disputed, and says so.
    "basic": {
        "min_proofing": "self_asserted",
        "device_bound": False,
        "hybrid_required_in_xr": False,
        "trusted_timestamp": False,
    },
    # OSHA-style logs, care-plan acknowledgements, terms, licensing.
    "standard": {
        "min_proofing": "federated",
        "device_bound": False,
        "hybrid_required_in_xr": False,
        "trusted_timestamp": False,
    },
    # Care handoffs, BAA execution, key release, likeness releases.
    "high": {
        "min_proofing": "document",
        "device_bound": True,
        "hybrid_required_in_xr": True,
        "trusted_timestamp": True,
    },
}

# Headsets render everything the wearer can see, so at the high tier the
# confirmation has to happen somewhere the immersive app cannot draw over.
#
# That argument only bites where there is no platform authenticator. visionOS
# exposes Optic ID as one, and its prompt is composited by the system rather
# than by the app — the same position an iPhone is in with Face ID, and we do
# not send iPhones to a second device. So Vision Pro signs on-device and the
# hybrid requirement falls on headsets that would need a second device anyway.
XR_PLATFORM_AUTHENTICATORS = {"visionos"}
XR_HYBRID_REQUIRED = {"quest", "androidxr", "xr"}
XR_PLATFORMS = XR_PLATFORM_AUTHENTICATORS | XR_HYBRID_REQUIRED

CHALLENGE_TTL_SECONDS = 120


class SignatureError(ValueError):
    """A refusal with a reason worth showing the caller."""


def _level_rank(level: str) -> int:
    try:
        return PROOFING_LEVELS.index(level)
    except ValueError as exc:
        raise SignatureError(
            i18n.fill(i18n.UNKNOWN_CHOICE_EXPECTED, field="proofing level", got=repr(level), choices=', '.join(PROOFING_LEVELS))) from exc


def tier_or_error(tier: str) -> dict:
    if tier not in TIERS:
        raise SignatureError(
            i18n.fill(i18n.UNKNOWN_CHOICE_EXPECTED, field="tier", got=repr(tier), choices=', '.join(TIERS)))
    return TIERS[tier]


# --- canonicalisation -----------------------------------------------------

def canonical(payload: dict) -> bytes:
    """The exact bytes that get hashed into the challenge.

    Sorted keys, no insignificant whitespace, UTF-8. Canonicalisation is not
    a detail: a verifier that reserialises differently computes a different
    hash and rejects a valid signature.
    """
    return json.dumps(payload, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def sha256_hex(raw: bytes | str) -> str:
    if isinstance(raw, str):
        raw = raw.encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


# --- enrollment -----------------------------------------------------------

def enroll_options(account_id: str, display_name: str, rp_id: str,
                   rp_name: str = "QRME") -> dict:
    """Registration options for a new signing credential.

    ``userVerification: "required"`` is the load-bearing setting — without it
    the user can satisfy the ceremony with a button press and the assertion
    still verifies, which would make every "signature" a tap.
    """
    challenge = webauthn.b64url_encode(secrets.token_bytes(32))
    return {
        "challenge": challenge,
        "rp": {"id": rp_id, "name": rp_name},
        "user": {
            "id": webauthn.b64url_encode(account_id.encode()),
            "name": account_id,
            "displayName": display_name,
        },
        "pubKeyCredParams": [{"type": "public-key", "alg": alg}
                             for alg in webauthn.SUPPORTED_ALGS],
        "timeout": CHALLENGE_TTL_SECONDS * 1000,
        "authenticatorSelection": {
            "userVerification": "required",
            "residentKey": "required",
        },
        # Direct attestation so the AAGUID is captured and the evidence can
        # say which authenticator model produced a signature.
        "attestation": "direct",
        "extensions": {"credProps": True},
    }


def enroll(account_id: str, credential_id: str, attestation_object: str,
           client_data_json: str, expected_challenge: str, rp_id: str,
           proofing_level: str, display_name: str | None = None,
           proofing_method: str | None = None,
           proofing_ref: str | None = None,
           proofing_attestor: str | None = None,
           allowed_origins: list[str] | None = None) -> dict:
    """Verify a registration and store the credential with its proofing.

    ``proofing_ref`` is a reference to evidence held elsewhere. Never store
    the identity document itself here, and never a biometric template — the
    face stays on the user's device, which is the entire point.
    """
    rank = _level_rank(proofing_level)
    if rank > 0 and not proofing_attestor:
        raise SignatureError(
            i18n.fill(i18n.PROOFING_NEEDS_ATTESTOR, level=repr(proofing_level)))

    raw_client = webauthn.b64url_decode(client_data_json)
    webauthn.parse_client_data(raw_client, "webauthn.create",
                               expected_challenge, allowed_origins)

    attestation = webauthn.cbor_decode(
        webauthn.b64url_decode(attestation_object))
    if not isinstance(attestation, dict) or "authData" not in attestation:
        raise SignatureError("attestation object has no authenticator data")
    auth = webauthn.parse_authenticator_data(attestation["authData"])

    if auth["rp_id_hash"] != hashlib.sha256(rp_id.encode()).digest():
        raise SignatureError(
            "this credential was registered for a different relying party")
    if not auth["user_verified"]:
        raise SignatureError(
            "the authenticator reported no user verification — enrollment "
            "must use the biometric or PIN, not a presence tap")
    if auth["public_key"] is None:
        raise SignatureError("registration carried no public key")

    alg = webauthn.cose_alg(auth["public_key"])
    conn = db.connect()
    row_id = db.new_id("scr")
    conn.execute(
        "INSERT INTO signing_credentials (id, account_id, credential_id,"
        " public_key, aaguid, alg, sign_count, backup_eligible, backed_up,"
        " proofing_level, proofing_method, proofing_ref, proofing_attestor,"
        " display_name, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (row_id, account_id, credential_id,
         webauthn.cose_key_to_json(auth["public_key"]), auth["aaguid"], alg,
         auth["sign_count"], int(auth["backup_eligible"]),
         int(auth["backed_up"]), proofing_level, proofing_method,
         proofing_ref, proofing_attestor, display_name, db.utcnow()))
    conn.commit()
    return credential(row_id)


def credential(row_id: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM signing_credentials WHERE id=?", (row_id,)).fetchone()
    return _credential_out(row) if row else None


def _credential_out(row) -> dict:
    return {
        "id": row["id"],
        "account_id": row["account_id"],
        "credential_id": row["credential_id"],
        "aaguid": row["aaguid"],
        "alg": row["alg"],
        "proofing_level": row["proofing_level"],
        "proofing_method": row["proofing_method"],
        "proofing_attestor": row["proofing_attestor"],
        "display_name": row["display_name"],
        # Surfaced rather than buried: a syncable credential exists on every
        # device in the user's cloud account, which weakens "only I could
        # have signed this". The tier policy uses it; a reader should see it.
        "backup_eligible": bool(row["backup_eligible"]),
        "backed_up": bool(row["backed_up"]),
        "device_bound": not bool(row["backup_eligible"]),
        "created_at": row["created_at"],
        "revoked_at": row["revoked_at"],
        "can_sign": [tier for tier, cfg in TIERS.items()
                     if _credential_meets(row, cfg)],
    }


def _credential_meets(row, cfg: dict) -> bool:
    if row["revoked_at"]:
        return False
    if _level_rank(row["proofing_level"]) < _level_rank(cfg["min_proofing"]):
        return False
    return not (cfg["device_bound"] and row["backup_eligible"])


def credentials_for(account_id: str) -> list[dict]:
    rows = db.connect().execute(
        "SELECT * FROM signing_credentials WHERE account_id=?"
        " ORDER BY created_at", (account_id,)).fetchall()
    return [_credential_out(r) for r in rows]


def reproof(row_id: str, level: str, attestor: str,
            method: str | None = None, ref: str | None = None) -> dict | None:
    """Raise (or lower) a credential's proofing level after enrollment.

    The spec promised this and nothing implemented it, which left every
    credential stuck at whatever it was enrolled with — and both mobile apps
    enroll self-asserted, so nothing they created could ever sign above the
    basic tier.

    The new level applies from now on and **never retroactively**: a signature
    already made copied its level into the evidence at signing time, so raising
    the credential today cannot quietly upgrade what it signed yesterday.
    """
    rank = _level_rank(level)
    if rank > 0 and not attestor:
        raise SignatureError(
            i18n.fill(i18n.PROOFING_NEEDS_ATTESTOR, level=repr(level)))
    conn = db.connect()
    if conn.execute("SELECT 1 FROM signing_credentials WHERE id=?",
                    (row_id,)).fetchone() is None:
        return None
    conn.execute(
        "UPDATE signing_credentials SET proofing_level=?, proofing_method=?,"
        " proofing_ref=?, proofing_attestor=? WHERE id=?",
        (level, method, ref, attestor or None, row_id))
    conn.commit()
    return credential(row_id)


def revoke(row_id: str) -> dict | None:
    """Revoke a credential going forward. Past signatures stay verifiable —
    their public key was copied into the evidence at signing time."""
    conn = db.connect()
    conn.execute("UPDATE signing_credentials SET revoked_at=? WHERE id=?",
                 (db.utcnow(), row_id))
    conn.commit()
    return credential(row_id)


# --- requesting a signature ----------------------------------------------

def request(account_id: str, document: str, meaning: str, tier: str,
            display_text: str, binding_kind: str | None = None,
            binding_ref: str | None = None, rp_id: str = "qrme.app") -> dict:
    """Mint an envelope: the challenge that *is* this document.

    ``display_text`` is what the signer will be shown. It is stored verbatim
    and hashed into the payload, because WebAuthn cannot attest to what was
    on screen and the next best thing is a record of what we rendered.
    """
    cfg = tier_or_error(tier)
    if not meaning.strip():
        raise SignatureError(
            "a signature needs a stated meaning — what the signer is "
            "attesting to belongs inside the signed bytes")
    if not display_text.strip():
        raise SignatureError(
            "display_text is required: it is the record of what the signer "
            "was shown")

    usable = [c for c in credentials_for(account_id) if tier in c["can_sign"]]
    if not usable:
        raise SignatureError(
            f"this account has no credential enrolled to the {tier!r} tier "
            f"(needs proofing at {cfg['min_proofing']!r} or above"
            + (", on a device-bound credential" if cfg["device_bound"] else "")
            + ")")

    now = datetime.now(timezone.utc)
    expires = now + timedelta(seconds=CHALLENGE_TTL_SECONDS)
    envelope_id = db.new_id("env")
    doc_hash = sha256_hex(document)
    display_hash = sha256_hex(display_text)

    payload = {
        "v": 1,
        "envelope": envelope_id,
        "doc_sha256": doc_hash,
        "display_sha256": display_hash,
        "meaning": meaning,
        "signer": account_id,
        "tier": tier,
        "issued_at": now.isoformat().replace("+00:00", "Z"),
        "expires_at": expires.isoformat().replace("+00:00", "Z"),
        "rp": rp_id,
    }
    raw = canonical(payload)
    challenge = webauthn.b64url_encode(hashlib.sha256(raw).digest())

    conn = db.connect()
    conn.execute(
        "INSERT INTO signature_envelopes (id, account_id, tier, meaning,"
        " document_sha256, display_text, display_sha256, payload, challenge,"
        " binding_kind, binding_ref, issued_at, expires_at)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (envelope_id, account_id, tier, meaning, doc_hash, display_text,
         display_hash, raw.decode(), challenge, binding_kind, binding_ref,
         payload["issued_at"], payload["expires_at"]))
    conn.commit()

    return {
        "envelope_id": envelope_id,
        "challenge": challenge,
        "payload": payload,
        "display_text": display_text,
        "display_sha256": display_hash,
        "document_sha256": doc_hash,
        "meaning": meaning,
        "tier": tier,
        "expires_at": payload["expires_at"],
        "allowed_credentials": [c["credential_id"] for c in usable],
        "user_verification": "required",
    }


# --- signing --------------------------------------------------------------

def sign(envelope_id: str, credential_id: str, signature: str,
         authenticator_data: str, client_data_json: str,
         rp_id: str = "qrme.app", transport: str = "internal",
         platform: str | None = None,
         allowed_origins: list[str] | None = None,
         pdi=None) -> dict:
    """Verify an assertion against its envelope and seal the evidence."""
    conn = db.connect()
    env = conn.execute("SELECT * FROM signature_envelopes WHERE id=?",
                       (envelope_id,)).fetchone()
    if env is None:
        raise SignatureError("no such envelope")
    if env["consumed_at"]:
        raise SignatureError(
            "this envelope has already been signed — one challenge signs one "
            "document, once")
    if _expired(env["expires_at"]):
        raise SignatureError(
            "this envelope has expired; request a new one and re-display the "
            "document before asking for the signature again")

    cred = conn.execute(
        "SELECT * FROM signing_credentials WHERE credential_id=?",
        (credential_id,)).fetchone()
    if cred is None:
        raise SignatureError("unknown credential")
    if cred["account_id"] != env["account_id"]:
        raise SignatureError(
            "this credential belongs to a different account than the envelope")
    if cred["revoked_at"]:
        raise SignatureError("this credential has been revoked")

    cfg = tier_or_error(env["tier"])
    if not _credential_meets(cred, cfg):
        raise SignatureError(
            f"this credential does not meet the {env['tier']!r} tier")
    if (cfg["hybrid_required_in_xr"] and (platform or "").lower() in
            XR_HYBRID_REQUIRED and transport != "hybrid"):
        raise SignatureError(
            "at this tier a signature made from this headset must use the "
            "cross-device (hybrid) path: it exposes no platform authenticator, "
            "and an immersive app renders everything the wearer can see, so "
            "the confirmation has to happen on a screen it cannot draw over")

    raw_auth = webauthn.b64url_decode(authenticator_data)
    raw_client = webauthn.b64url_decode(client_data_json)
    raw_sig = webauthn.b64url_decode(signature)

    webauthn.parse_client_data(raw_client, "webauthn.get", env["challenge"],
                               allowed_origins)
    auth = webauthn.parse_authenticator_data(raw_auth)
    if auth["rp_id_hash"] != hashlib.sha256(rp_id.encode()).digest():
        raise SignatureError("this assertion was made for a different site")
    if not auth["user_verified"]:
        raise SignatureError(
            "the authenticator reported no user verification — a presence tap "
            "is not a signature")

    key = webauthn.cose_key_from_json(cred["public_key"])
    if len(raw_sig) == 64 and cred["alg"] == webauthn.ES256:
        raw_sig = webauthn.der_from_raw_ecdsa(raw_sig)
    webauthn.verify_signature(key, raw_sig,
                              webauthn.signed_bytes(raw_auth, raw_client))

    # A counter that goes backwards suggests a cloned authenticator. It is
    # not conclusive — synced passkeys legitimately report zero — so it is
    # recorded rather than used to refuse.
    regressed = (auth["sign_count"] > 0 and cred["sign_count"] > 0
                 and auth["sign_count"] <= cred["sign_count"])

    signed_at = db.utcnow()
    sig_id = db.new_id("sig")
    conn.execute(
        "INSERT INTO signatures (id, envelope_id, account_id, credential_id,"
        " public_key, aaguid, alg, signature, authenticator_data,"
        " client_data_json, user_verified, backup_eligible, backed_up,"
        " sign_count, sign_count_regressed, transport, platform,"
        " proofing_level, tier, signer_name, binding_kind, binding_ref,"
        " sealed_ref, signed_at)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (sig_id, envelope_id, env["account_id"], credential_id,
         cred["public_key"], cred["aaguid"], cred["alg"], signature,
         authenticator_data, client_data_json, int(auth["user_verified"]),
         int(auth["backup_eligible"]), int(auth["backed_up"]),
         auth["sign_count"], int(regressed), transport, platform,
         cred["proofing_level"], env["tier"], cred["display_name"],
         env["binding_kind"], env["binding_ref"], None, signed_at))
    conn.execute("UPDATE signature_envelopes SET consumed_at=? WHERE id=?",
                 (signed_at, envelope_id))
    if auth["sign_count"] > cred["sign_count"]:
        conn.execute(
            "UPDATE signing_credentials SET sign_count=?, backed_up=?"
            " WHERE credential_id=?",
            (auth["sign_count"], int(auth["backed_up"]), credential_id))
    conn.commit()

    _seal(sig_id, pdi)
    return package(sig_id)


def _expired(expires_at: str) -> bool:
    try:
        deadline = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
    except ValueError:
        return True
    return datetime.now(timezone.utc) > deadline


def _seal(sig_id: str, pdi) -> None:
    """Seal the evidence into PDI when a vault is configured.

    Best-effort by design, matching how rated events are sealed: a vault
    outage must not lose a signature that has already verified. The row is
    the record; the vault copy is the tamper-evident one, chained into PDI's
    audit log so the existence and order of signatures is protected by
    something other than the table they live in.
    """
    if pdi is None:
        return
    key = f"qrme/signatures/{sig_id}"
    try:
        pdi.put(key, json.dumps(package(sig_id)))
    except Exception:                       # pragma: no cover - vault down
        return
    conn = db.connect()
    conn.execute("UPDATE signatures SET sealed_ref=? WHERE id=?",
                 (key, sig_id))
    conn.commit()


# --- reading and re-verifying --------------------------------------------

def package(sig_id: str) -> dict | None:
    """The evidence package: everything a third party needs, and the result
    of checking it again right now."""
    conn = db.connect()
    row = conn.execute("SELECT * FROM signatures WHERE id=?",
                       (sig_id,)).fetchone()
    if row is None:
        return None
    env = conn.execute("SELECT * FROM signature_envelopes WHERE id=?",
                       (row["envelope_id"],)).fetchone()
    out = {
        "signature_id": row["id"],
        "envelope_id": row["envelope_id"],
        "signer": {
            "account_id": row["account_id"],
            "name": row["signer_name"],
            "proofing_level": row["proofing_level"],
        },
        "meaning": env["meaning"] if env else None,
        "document_sha256": env["document_sha256"] if env else None,
        "display_text": env["display_text"] if env else None,
        "display_sha256": env["display_sha256"] if env else None,
        "payload": json.loads(env["payload"]) if env else None,
        "challenge": env["challenge"] if env else None,
        "tier": row["tier"],
        "binding": {"kind": row["binding_kind"], "ref": row["binding_ref"]},
        "credential": {
            "credential_id": row["credential_id"],
            "aaguid": row["aaguid"],
            "alg": row["alg"],
            "public_key": json.loads(row["public_key"]),
            "backup_eligible": bool(row["backup_eligible"]),
            "backed_up": bool(row["backed_up"]),
            "device_bound": not bool(row["backup_eligible"]),
        },
        "assertion": {
            "signature": row["signature"],
            "authenticator_data": row["authenticator_data"],
            "client_data_json": row["client_data_json"],
        },
        "user_verified": bool(row["user_verified"]),
        "sign_count": row["sign_count"],
        "sign_count_regressed": bool(row["sign_count_regressed"]),
        "transport": row["transport"],
        "platform": row["platform"],
        "signed_at": row["signed_at"],
        "sealed_ref": row["sealed_ref"],
        "limits": LIMITS,
    }
    out["verification"] = verify_package(out)
    return out


# Every check a complete verification performs, in the order it performs
# them. Named as a list rather than left implicit because a package that
# stops halfway leaves the rest *unrun*, and an unrun check is not a passed
# one — `all()` over the checks that happened to execute would call a
# half-read package valid.
VERIFICATION_CHECKS = (
    "signature", "challenge_matches", "ceremony_is_signing",
    "challenge_binds_payload", "payload_binds_document",
    "payload_binds_display", "display_text_matches", "user_verified",
)


def _unreadable(exc: Exception) -> str:
    """Why the package could not be read, as a sentence.

    The two notes below this function are sentences a counterparty can act
    on, and the router says the same thing about its refusals: *the message
    is the reason, because a signature that is turned away without one is
    impossible to fix from the outside*. `str(KeyError("assertion"))` is
    `"'assertion'"`, which is a Python repr wearing the same field.
    """
    if isinstance(exc, KeyError):
        field = exc.args[0] if exc.args else "?"
        return (f"this package has no `{field}` field, so there is nothing "
                "here to check against — it may have been trimmed in transit, "
                "or be a summary of a package rather than the package")
    return (f"part of this package could not be read ({type(exc).__name__}), "
            f"so the check it belongs to did not run: {exc}")


def verify_package(pkg: dict) -> dict:
    """Re-verify an evidence package from its own contents.

    Takes no database lookups on purpose: this is the function a counterparty
    runs, and it must work on a package handed to them as JSON.

    A failure part-way through says so as a failure *of that check*. It used
    to force ``signature: false``, which for a package whose signature had
    already verified was the most consequential thing this function can say
    and false: a missing `display_text` reported the cryptography as broken
    and named the field in a bare repr. Nothing about the signature changes
    because a later field is absent.
    """
    checks: dict[str, bool] = {}
    notes: list[str] = []
    try:
        raw_auth = webauthn.b64url_decode(
            pkg["assertion"]["authenticator_data"])
        raw_client = webauthn.b64url_decode(
            pkg["assertion"]["client_data_json"])
        raw_sig = webauthn.b64url_decode(pkg["assertion"]["signature"])
        key = {int(k): (bytes.fromhex(v) if isinstance(v, str) else v)
               for k, v in pkg["credential"]["public_key"].items()}

        if len(raw_sig) == 64 and pkg["credential"]["alg"] == webauthn.ES256:
            raw_sig = webauthn.der_from_raw_ecdsa(raw_sig)
        webauthn.verify_signature(key, raw_sig,
                                  webauthn.signed_bytes(raw_auth, raw_client))
        checks["signature"] = True

        client = json.loads(raw_client)
        checks["challenge_matches"] = client.get("challenge") == pkg["challenge"]
        checks["ceremony_is_signing"] = client.get("type") == "webauthn.get"

        # The challenge must be the hash of the payload — this is the link
        # from "a signature happened" to "it was over this document".
        payload_hash = webauthn.b64url_encode(
            hashlib.sha256(canonical(pkg["payload"])).digest())
        checks["challenge_binds_payload"] = payload_hash == pkg["challenge"]
        checks["payload_binds_document"] = (
            pkg["payload"].get("doc_sha256") == pkg["document_sha256"])
        checks["payload_binds_display"] = (
            pkg["payload"].get("display_sha256") == pkg["display_sha256"])
        checks["display_text_matches"] = (
            sha256_hex(pkg["display_text"] or "") == pkg["display_sha256"])
        checks["user_verified"] = bool(pkg.get("user_verified"))
    except Exception as exc:
        # Only the signature check itself may be *failed* here. If it already
        # ran and passed, it stays passed — the thing that broke is whatever
        # came after, and that is reported as unrun rather than as a forged
        # signature.
        checks.setdefault("signature", False)
        notes.append(_unreadable(exc))

    unrun = [c for c in VERIFICATION_CHECKS if c not in checks]
    if unrun:
        notes.append(
            "this package was not checked all the way through — "
            + ", ".join(unrun)
            + " did not run, so it cannot be called valid on what did")

    if pkg.get("sign_count_regressed"):
        notes.append("the authenticator's signature counter did not advance — "
                     "possible cloned credential, or a synced passkey that "
                     "does not maintain one")
    if pkg.get("credential", {}).get("backup_eligible"):
        notes.append("this credential is syncable, so it may exist on more "
                     "than one device in the signer's cloud account")
    return {"valid": not unrun and all(checks.values()),
            "checks": checks, "notes": notes}


def certificate(sig_id: str) -> dict | None:
    """The human-readable manifestation: printed name, date and time, and
    meaning. Part 11 requires this next to the record; it is worth having
    regardless, because it is what makes a signature legible to a person."""
    pkg = package(sig_id)
    if pkg is None:
        return None
    return {
        "signature_id": pkg["signature_id"],
        "printed_name": pkg["signer"]["name"] or pkg["signer"]["account_id"],
        "signed_at": pkg["signed_at"],
        "meaning": pkg["meaning"],
        "document_sha256": pkg["document_sha256"],
        "what_was_shown": pkg["display_text"],
        "identity_verified_as": pkg["signer"]["proofing_level"],
        "tier": pkg["tier"],
        "valid": pkg["verification"]["valid"],
        "verify_at": f"/signatures/{sig_id}",
        "standard": STANDARD,
        "limits": LIMITS,
    }


def signatures_for(binding_kind: str, binding_ref: str) -> list[dict]:
    rows = db.connect().execute(
        "SELECT id FROM signatures WHERE binding_kind=? AND binding_ref=?"
        " ORDER BY signed_at", (binding_kind, binding_ref)).fetchall()
    return [package(r["id"]) for r in rows]


STANDARD = ("ESIGN/UETA — intent recorded in the signed meaning, consent at "
            "enrollment, attribution by proofed enrollment, retention in the "
            "sealed evidence package. Not a 21 CFR Part 11 signature and not "
            "a qualified electronic signature under eIDAS.")

# Shipped inside every package so a reader cannot receive the guarantee
# without the limits attached to it.
LIMITS = [
    "Proves the credential was used with user verification over this exact "
    "document — not that a particular human was physically present.",
    "Does not attest to what appeared on the signer's screen: WebAuthn has "
    "no trusted display. The rendered text is recorded here instead.",
    "The time is this deployment's clock unless a trusted timestamp is "
    "attached.",
    "A syncable credential may exist on several devices; backup_eligible "
    "says whether this one could.",
]
