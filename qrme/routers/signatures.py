"""Signature endpoints: enroll a passkey, sign a document, verify a package.

The account a signature belongs to is the caller's own token subject — never
a value from the request body. An endpoint that accepted `{"signer": "..."}`
would let anyone sign as anyone, which is the failure this whole feature
exists to prevent.

``POST /signatures/verify`` is the exception to the token rule and is public
on purpose: a counterparty must be able to check a signature without holding
an account here. That is the difference between a record we vouch for and a
record that stands on its own.
"""

from __future__ import annotations

import os

from pydantic import BaseModel, Field

from fastapi import APIRouter, HTTPException, Request

from .. import auth, signatures

router = APIRouter()


def _rp_id() -> str:
    """The relying party id — the domain a credential is bound to. A
    credential registered for one rp cannot sign for another, which is what
    stops a phished assertion from being replayed here."""
    return os.environ.get("QRME_RP_ID", "qrme.app")


def _allowed_origins() -> list[str] | None:
    raw = os.environ.get("QRME_RP_ORIGINS", "").strip()
    return [o.strip() for o in raw.split(",") if o.strip()] or None


def _account(request: Request) -> str:
    who = auth.principal(request)
    if who is None:
        raise HTTPException(401, "authentication required")
    return f"{who['role']}:{who['subject_id']}"


def _fail(exc: signatures.SignatureError):
    # 422 rather than 400: the request was well-formed, its contents were
    # refused. The message is the reason, because a signature that is turned
    # away without one is impossible to fix from the outside.
    return HTTPException(422, str(exc))


class EnrollOptionsIn(BaseModel):
    display_name: str = Field(max_length=120)


class EnrollIn(BaseModel):
    credential_id: str
    attestation_object: str
    client_data_json: str
    challenge: str
    proofing_level: str = "self_asserted"
    proofing_method: str | None = Field(default=None, max_length=120)
    proofing_ref: str | None = Field(default=None, max_length=200)
    proofing_attestor: str | None = Field(default=None, max_length=120)
    display_name: str | None = Field(default=None, max_length=120)


class RequestIn(BaseModel):
    document: str
    meaning: str = Field(max_length=300)
    display_text: str
    tier: str = "standard"
    binding_kind: str | None = Field(default=None, max_length=60)
    binding_ref: str | None = Field(default=None, max_length=120)


class SignIn(BaseModel):
    envelope_id: str
    credential_id: str
    signature: str
    authenticator_data: str
    client_data_json: str
    transport: str = "internal"
    platform: str | None = Field(default=None, max_length=40)


@router.get("/signatures/policy")
def policy() -> dict:
    """What each tier requires, and what the scheme does not prove. Public:
    a counterparty deciding whether to accept a signature should be able to
    read the rules without an account."""
    return {
        "tiers": signatures.TIERS,
        "proofing_levels": list(signatures.PROOFING_LEVELS),
        "xr_platform_authenticators": sorted(
            signatures.XR_PLATFORM_AUTHENTICATORS),
        "xr_hybrid_required": sorted(signatures.XR_HYBRID_REQUIRED),
        "standard": signatures.STANDARD,
        "limits": signatures.LIMITS,
    }


@router.post("/signatures/enroll/options")
def enroll_options(body: EnrollOptionsIn, request: Request) -> dict:
    """Registration options for a new signing credential. Returns the
    challenge to be echoed back to `/signatures/enroll`."""
    return signatures.enroll_options(_account(request), body.display_name,
                                     _rp_id())


@router.post("/signatures/enroll", status_code=201)
def enroll(body: EnrollIn, request: Request) -> dict:
    """Verify a registration and bind the credential to this account at the
    stated proofing level."""
    try:
        return signatures.enroll(
            account_id=_account(request), credential_id=body.credential_id,
            attestation_object=body.attestation_object,
            client_data_json=body.client_data_json,
            expected_challenge=body.challenge, rp_id=_rp_id(),
            proofing_level=body.proofing_level,
            display_name=body.display_name,
            proofing_method=body.proofing_method,
            proofing_ref=body.proofing_ref,
            proofing_attestor=body.proofing_attestor,
            allowed_origins=_allowed_origins())
    except signatures.SignatureError as exc:
        raise _fail(exc) from exc
    except ValueError as exc:
        raise HTTPException(422, f"registration could not be read: {exc}") \
            from exc


@router.get("/signatures/credentials")
def list_credentials(request: Request) -> dict:
    """This account's signing credentials, each with the tiers it can sign
    at and whether it is syncable."""
    return {"credentials": signatures.credentials_for(_account(request))}


@router.delete("/signatures/credentials/{row_id}")
def revoke_credential(row_id: str, request: Request) -> dict:
    """Revoke a credential going forward. Signatures already made with it
    stay verifiable — their public key lives in the evidence."""
    existing = signatures.credential(row_id)
    if existing is None:
        raise HTTPException(404, "no such credential")
    if existing["account_id"] != _account(request):
        raise HTTPException(403, "not your credential")
    return signatures.revoke(row_id)


class ReproofIn(BaseModel):
    proofing_level: str
    proofing_attestor: str = Field(max_length=120)
    proofing_method: str | None = Field(default=None, max_length=120)
    proofing_ref: str | None = Field(default=None, max_length=200)


@router.post("/signatures/credentials/{row_id}/proofing")
def reproof(row_id: str, body: ReproofIn, request: Request) -> dict:
    """Record a fresh identity check against an existing credential.

    Enrollment fixes a level; this is how it moves. Applies going forward
    only — signatures already made carry the level they were made at.
    """
    existing = signatures.credential(row_id)
    if existing is None:
        raise HTTPException(404, "no such credential")
    if existing["account_id"] != _account(request):
        raise HTTPException(403, "not your credential")
    try:
        return signatures.reproof(
            row_id, body.proofing_level, body.proofing_attestor,
            body.proofing_method, body.proofing_ref)
    except signatures.SignatureError as exc:
        raise _fail(exc) from exc


@router.post("/signatures/request")
def request_signature(body: RequestIn, request: Request) -> dict:
    """Mint an envelope whose challenge is the hash of this document."""
    try:
        return signatures.request(
            account_id=_account(request), document=body.document,
            meaning=body.meaning, tier=body.tier,
            display_text=body.display_text, binding_kind=body.binding_kind,
            binding_ref=body.binding_ref, rp_id=_rp_id())
    except signatures.SignatureError as exc:
        raise _fail(exc) from exc


@router.post("/signatures/sign", status_code=201)
def sign(body: SignIn, request: Request) -> dict:
    """Verify the assertion against its envelope and seal the evidence."""
    account = _account(request)
    try:
        result = signatures.sign(
            envelope_id=body.envelope_id, credential_id=body.credential_id,
            signature=body.signature,
            authenticator_data=body.authenticator_data,
            client_data_json=body.client_data_json, rp_id=_rp_id(),
            transport=body.transport, platform=body.platform,
            allowed_origins=_allowed_origins(),
            pdi=getattr(request.app.state, "pdi", None))
    except signatures.SignatureError as exc:
        raise _fail(exc) from exc
    except ValueError as exc:
        raise HTTPException(422, f"assertion could not be read: {exc}") from exc
    if result["signer"]["account_id"] != account:
        raise HTTPException(403, "not your envelope")
    return result


@router.get("/signatures/{sig_id}")
def get_signature(sig_id: str) -> dict:
    """The evidence package, re-verified on the way out."""
    pkg = signatures.package(sig_id)
    if pkg is None:
        raise HTTPException(404, "no such signature")
    return pkg


@router.get("/signatures/{sig_id}/certificate")
def certificate(sig_id: str) -> dict:
    """The human-readable manifestation: printed name, date and time, and
    the meaning of the signature."""
    cert = signatures.certificate(sig_id)
    if cert is None:
        raise HTTPException(404, "no such signature")
    return cert


class VerifyIn(BaseModel):
    package: dict


@router.post("/signatures/verify")
def verify(body: VerifyIn) -> dict:
    """Verify a package presented from outside — no token, no lookup, no
    trust in this deployment beyond the arithmetic."""
    try:
        return signatures.verify_package(body.package)
    except Exception as exc:
        raise HTTPException(
            422, f"this does not look like an evidence package: {exc}") \
            from exc
