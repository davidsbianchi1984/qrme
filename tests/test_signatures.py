"""Signatures: does the artifact actually survive being disputed?

These tests do real cryptography. A fake authenticator is built on top of a
genuine P-256 key: it produces real authenticator data, real client data, and
a real ECDSA signature over `authData || SHA-256(clientDataJSON)`. Nothing is
stubbed on the verification path, because a test that mocked the signature
check would prove only that the mock returns True — which is precisely the
failure mode this whole feature exists to eliminate.

The interesting tests are the negative ones. A signature scheme that accepts
valid input is table stakes; what matters is whether it refuses a document
swapped after signing, an assertion replayed onto a second document, a
presence tap dressed up as a biometric, and a credential that was never
proofed to the level the record demands.
"""

import hashlib
import json
import struct

import pytest
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec

from qrme import signatures, webauthn

RP_ID = "qrme.app"


# --- a fake authenticator, with a real key -------------------------------

class Authenticator:
    """Everything a passkey does, in-process — including actually signing."""

    def __init__(self, *, user_verified=True, backup_eligible=False,
                 backed_up=False, rp_id=RP_ID):
        self.key = ec.generate_private_key(ec.SECP256R1())
        self.credential_id = b"cred-" + hashlib.sha256(
            self.key.public_key().public_bytes_raw()
            if hasattr(self.key.public_key(), "public_bytes_raw")
            else b"x").digest()[:12]
        self.user_verified = user_verified
        self.backup_eligible = backup_eligible
        self.backed_up = backed_up
        self.rp_id = rp_id
        self.sign_count = 0

    # -- COSE / CBOR encoding (only what an authenticator emits) --

    def _cose_key(self) -> bytes:
        nums = self.key.public_key().public_numbers()
        x = nums.x.to_bytes(32, "big")
        y = nums.y.to_bytes(32, "big")
        # {1: 2, 3: -7, -1: 1, -2: x, -3: y}
        return (b"\xa5"
                + b"\x01\x02"
                + b"\x03\x26"
                + b"\x20\x01"
                + b"\x21" + _cbor_bytes(x)
                + b"\x22" + _cbor_bytes(y))

    def _flags(self, attested: bool) -> int:
        flags = webauthn.FLAG_UP
        if self.user_verified:
            flags |= webauthn.FLAG_UV
        if self.backup_eligible:
            flags |= webauthn.FLAG_BE
        if self.backed_up:
            flags |= webauthn.FLAG_BS
        if attested:
            flags |= webauthn.FLAG_AT
        return flags

    def _auth_data(self, attested: bool) -> bytes:
        self.sign_count += 1
        data = (hashlib.sha256(self.rp_id.encode()).digest()
                + bytes([self._flags(attested)])
                + struct.pack(">I", self.sign_count))
        if attested:
            data += (b"\x00" * 16
                     + struct.pack(">H", len(self.credential_id))
                     + self.credential_id
                     + self._cose_key())
        return data

    def _client_data(self, ceremony: str, challenge: str,
                     origin="https://qrme.app") -> bytes:
        return json.dumps({"type": ceremony, "challenge": challenge,
                           "origin": origin}).encode()

    # -- the two ceremonies --

    def register(self, challenge: str) -> dict:
        auth_data = self._auth_data(attested=True)
        attestation = (b"\xa3"
                       + b"\x63fmt" + b"\x64none"
                       + b"\x67attStmt" + b"\xa0"
                       + b"\x68authData" + _cbor_bytes(auth_data))
        return {
            "credential_id": webauthn.b64url_encode(self.credential_id),
            "attestation_object": webauthn.b64url_encode(attestation),
            "client_data_json": webauthn.b64url_encode(
                self._client_data("webauthn.create", challenge)),
            "challenge": challenge,
        }

    def assert_(self, challenge: str, ceremony="webauthn.get",
                origin="https://qrme.app") -> dict:
        auth_data = self._auth_data(attested=False)
        client = self._client_data(ceremony, challenge, origin)
        signed = auth_data + hashlib.sha256(client).digest()
        sig = self.key.sign(signed, ec.ECDSA(hashes.SHA256()))
        return {
            "credential_id": webauthn.b64url_encode(self.credential_id),
            "signature": webauthn.b64url_encode(sig),
            "authenticator_data": webauthn.b64url_encode(auth_data),
            "client_data_json": webauthn.b64url_encode(client),
        }


def _cbor_bytes(raw: bytes) -> bytes:
    if len(raw) < 24:
        return bytes([0x40 | len(raw)]) + raw
    if len(raw) < 256:
        return b"\x58" + bytes([len(raw)]) + raw
    return b"\x59" + struct.pack(">H", len(raw)) + raw


# --- helpers --------------------------------------------------------------

def _token(client):
    """A real capability token: a profile owner's."""
    created = client.post("/profiles", json={
        "owner_id": "o1", "kind": "fictional", "display_name": "Dr. Amara Osei",
        "persona": "A physician.",
        "verification": {"birthdate": "1980-01-01", "id_document": "passport",
                         "liveness_check": True}}).json()
    return {"authorization": f"Bearer {created['owner_token']}"}


def _enroll(client, headers, level="document", **kw):
    auth = Authenticator(**kw)
    opts = client.post("/signatures/enroll/options",
                       json={"display_name": "Dana Reyes"},
                       headers=headers).json()
    body = auth.register(opts["challenge"])
    body.update({"proofing_level": level, "display_name": "Dana Reyes",
                 "proofing_attestor": "clinic-registrar"}
                if level != "self_asserted" else
                {"proofing_level": level, "display_name": "Dana Reyes"})
    res = client.post("/signatures/enroll", json=body, headers=headers)
    return auth, res


def _sign(client, headers, auth, document="the handoff", meaning="I attest",
          tier="high", display="Handoff for M.R., 4mg, 22:00", **sign_kw):
    env = client.post("/signatures/request", json={
        "document": document, "meaning": meaning, "tier": tier,
        "display_text": display}, headers=headers).json()
    assertion = auth.assert_(env["challenge"])
    body = {"envelope_id": env["envelope_id"], **assertion}
    body.update(sign_kw)
    return env, client.post("/signatures/sign", json=body, headers=headers)


# --- enrollment -----------------------------------------------------------

def test_a_credential_enrolls_and_reports_what_it_can_sign(client):
    headers = _token(client)
    _, res = _enroll(client, headers, level="document")
    assert res.status_code == 201, res.text
    cred = res.json()
    assert cred["proofing_level"] == "document"
    assert cred["device_bound"] is True
    assert set(cred["can_sign"]) == {"basic", "standard", "high"}


def test_a_syncable_credential_cannot_sign_at_the_high_tier(client):
    """Passkeys sync. A key present on every device in a cloud account is a
    weaker claim of exclusive possession, and the top tier says so."""
    headers = _token(client)
    _, res = _enroll(client, headers, level="document",
                     backup_eligible=True, backed_up=True)
    cred = res.json()
    assert cred["backup_eligible"] is True
    assert cred["device_bound"] is False
    assert "high" not in cred["can_sign"]
    assert "standard" in cred["can_sign"]


def test_enrollment_without_user_verification_is_refused(client):
    """If the ceremony can be satisfied by a button press, every signature
    made with the credential is a tap."""
    headers = _token(client)
    _, res = _enroll(client, headers, user_verified=False)
    assert res.status_code == 422
    assert "user verification" in res.text


def test_a_proofed_level_needs_an_attestor(client):
    """Who checked the identity is part of the record."""
    headers = _token(client)
    auth = Authenticator()
    opts = client.post("/signatures/enroll/options",
                       json={"display_name": "D"}, headers=headers).json()
    body = auth.register(opts["challenge"])
    body["proofing_level"] = "document"
    res = client.post("/signatures/enroll", json=body, headers=headers)
    assert res.status_code == 422
    assert "attestor" in res.text


def test_registration_for_another_relying_party_is_refused(client):
    headers = _token(client)
    _, res = _enroll(client, headers, rp_id="evil.example")
    assert res.status_code == 422
    assert "different relying party" in res.text


def test_enrollment_requires_a_token(client):
    assert client.post("/signatures/enroll/options",
                       json={"display_name": "D"}).status_code == 401


# --- signing --------------------------------------------------------------

def test_a_signature_verifies_end_to_end(client):
    headers = _token(client)
    auth, _ = _enroll(client, headers)
    env, res = _sign(client, headers, auth)
    assert res.status_code == 201, res.text
    pkg = res.json()
    assert pkg["verification"]["valid"] is True
    assert pkg["user_verified"] is True
    assert pkg["meaning"] == "I attest"
    assert pkg["document_sha256"] == signatures.sha256_hex("the handoff")


def test_the_challenge_is_the_document(client):
    """The whole design in one assertion: the thing signed is the hash of a
    payload naming this document, not an unrelated nonce."""
    headers = _token(client)
    auth, _ = _enroll(client, headers)
    env, res = _sign(client, headers, auth)
    pkg = res.json()
    expected = webauthn.b64url_encode(
        hashlib.sha256(signatures.canonical(pkg["payload"])).digest())
    assert expected == pkg["challenge"]
    assert pkg["payload"]["doc_sha256"] == pkg["document_sha256"]
    assert pkg["verification"]["checks"]["challenge_binds_payload"] is True


def test_altering_the_document_after_signing_breaks_verification(client):
    """The dispute this feature exists for."""
    headers = _token(client)
    auth, _ = _enroll(client, headers)
    _, res = _sign(client, headers, auth)
    pkg = res.json()
    assert pkg["verification"]["valid"] is True

    pkg["document_sha256"] = signatures.sha256_hex("a different handoff")
    out = client.post("/signatures/verify", json={"package": pkg}).json()
    assert out["valid"] is False
    assert out["checks"]["payload_binds_document"] is False


def test_altering_the_payload_breaks_the_challenge_binding(client):
    headers = _token(client)
    auth, _ = _enroll(client, headers)
    _, res = _sign(client, headers, auth)
    pkg = res.json()
    pkg["payload"]["meaning"] = "I was merely reviewing this"
    out = client.post("/signatures/verify", json={"package": pkg}).json()
    assert out["valid"] is False
    assert out["checks"]["challenge_binds_payload"] is False


def test_an_envelope_signs_once(client):
    """One challenge, one document, one use — enforced at the server, not by
    the client's good manners."""
    headers = _token(client)
    auth, _ = _enroll(client, headers)
    env = client.post("/signatures/request", json={
        "document": "d", "meaning": "m", "tier": "high",
        "display_text": "shown"}, headers=headers).json()
    assertion = auth.assert_(env["challenge"])
    body = {"envelope_id": env["envelope_id"], **assertion}
    assert client.post("/signatures/sign", json=body,
                       headers=headers).status_code == 201
    again = client.post("/signatures/sign", json=body, headers=headers)
    assert again.status_code == 422
    assert "already been signed" in again.text


def test_an_assertion_cannot_be_replayed_onto_another_envelope(client):
    """A signature over document A must not stand in for document B."""
    headers = _token(client)
    auth, _ = _enroll(client, headers)
    first = client.post("/signatures/request", json={
        "document": "consent to share records", "meaning": "I agree",
        "tier": "high", "display_text": "A"}, headers=headers).json()
    second = client.post("/signatures/request", json={
        "document": "transfer of guardianship", "meaning": "I agree",
        "tier": "high", "display_text": "B"}, headers=headers).json()

    stolen = auth.assert_(first["challenge"])
    res = client.post("/signatures/sign",
                      json={"envelope_id": second["envelope_id"], **stolen},
                      headers=headers)
    assert res.status_code == 422
    assert "signs something else" in res.text


def test_a_signin_assertion_is_not_a_signature(client):
    """`webauthn.get` from a login flow must not be laundered into a
    signature, even if the challenge somehow matched."""
    headers = _token(client)
    auth, _ = _enroll(client, headers)
    env = client.post("/signatures/request", json={
        "document": "d", "meaning": "m", "tier": "high",
        "display_text": "shown"}, headers=headers).json()
    assertion = auth.assert_(env["challenge"], ceremony="webauthn.create")
    res = client.post("/signatures/sign",
                      json={"envelope_id": env["envelope_id"], **assertion},
                      headers=headers)
    assert res.status_code == 422


def test_a_presence_tap_is_not_a_signature(client):
    headers = _token(client)
    auth, _ = _enroll(client, headers)
    auth.user_verified = False              # enrolled with UV, now signing without
    _, res = _sign(client, headers, auth)
    assert res.status_code == 422
    assert "presence tap" in res.text


def test_a_forged_signature_is_refused(client):
    """The core claim: a client that fabricates the assertion gets nowhere."""
    headers = _token(client)
    auth, _ = _enroll(client, headers)
    env = client.post("/signatures/request", json={
        "document": "d", "meaning": "m", "tier": "high",
        "display_text": "shown"}, headers=headers).json()
    assertion = auth.assert_(env["challenge"])
    # Someone else's key over the same data.
    impostor = Authenticator()
    forged = impostor.assert_(env["challenge"])
    assertion["signature"] = forged["signature"]
    res = client.post("/signatures/sign",
                      json={"envelope_id": env["envelope_id"], **assertion},
                      headers=headers)
    assert res.status_code == 422
    assert "does not verify" in res.text


def test_a_weakly_proofed_credential_cannot_sign_a_high_tier_record(client):
    """A passkey proves a credential was used, not whose it is."""
    headers = _token(client)
    auth, res = _enroll(client, headers, level="self_asserted")
    assert res.status_code == 201
    env = client.post("/signatures/request", json={
        "document": "care handoff", "meaning": "I attest", "tier": "high",
        "display_text": "shown"}, headers=headers)
    assert env.status_code == 422
    assert "proofing" in env.text


def test_a_signature_needs_a_stated_meaning(client):
    headers = _token(client)
    _enroll(client, headers)
    res = client.post("/signatures/request", json={
        "document": "d", "meaning": "   ", "tier": "high",
        "display_text": "shown"}, headers=headers)
    assert res.status_code == 422
    assert "meaning" in res.text


# --- XR -------------------------------------------------------------------

def test_high_tier_signing_from_a_headset_requires_the_second_device(client):
    """In a headset the app renders everything the wearer can see, so the
    confirmation has to happen somewhere it cannot draw over."""
    headers = _token(client)
    auth, _ = _enroll(client, headers)
    _, res = _sign(client, headers, auth, platform="quest",
                   transport="internal")
    assert res.status_code == 422
    assert "hybrid" in res.text


def test_the_hybrid_path_from_a_headset_is_accepted_and_recorded(client):
    headers = _token(client)
    auth, _ = _enroll(client, headers)
    _, res = _sign(client, headers, auth, platform="quest",
                   transport="hybrid")
    assert res.status_code == 201
    pkg = res.json()
    assert pkg["transport"] == "hybrid"
    assert pkg["platform"] == "quest"


def test_vision_pro_signs_on_device_because_optic_id_is_a_platform_key(client):
    """visionOS exposes Optic ID as a platform authenticator whose prompt the
    system composites — the same position an iPhone is in with Face ID. It is
    an XR platform and still signs on-device, at every tier."""
    headers = _token(client)
    auth, _ = _enroll(client, headers)
    _, res = _sign(client, headers, auth, platform="visionos",
                   transport="internal")
    assert res.status_code == 201, res.text
    assert res.json()["platform"] == "visionos"


# --- the evidence package -------------------------------------------------

def test_the_package_verifies_standalone_without_a_token(client):
    """A counterparty must be able to check a signature without an account
    here — otherwise it is a record we vouch for, not one that stands up."""
    headers = _token(client)
    auth, _ = _enroll(client, headers)
    _, res = _sign(client, headers, auth)
    pkg = res.json()
    out = client.post("/signatures/verify", json={"package": pkg})
    assert out.status_code == 200
    assert out.json()["valid"] is True


def test_revoking_a_credential_leaves_past_signatures_verifiable(client):
    """Deleting a passkey must not retroactively unmake what it signed."""
    headers = _token(client)
    auth, enrolled = _enroll(client, headers)
    _, res = _sign(client, headers, auth)
    sig_id = res.json()["signature_id"]

    client.delete(f"/signatures/credentials/{enrolled.json()['id']}",
                  headers=headers)
    again = client.get(f"/signatures/{sig_id}")
    assert again.status_code == 200
    assert again.json()["verification"]["valid"] is True


def test_a_revoked_credential_cannot_sign_again(client):
    headers = _token(client)
    auth, enrolled = _enroll(client, headers)
    client.delete(f"/signatures/credentials/{enrolled.json()['id']}",
                  headers=headers)
    res = client.post("/signatures/request", json={
        "document": "d", "meaning": "m", "tier": "high",
        "display_text": "shown"}, headers=headers)
    assert res.status_code == 422


def test_the_package_carries_its_own_limits(client):
    """The guarantee must not travel without them."""
    headers = _token(client)
    auth, _ = _enroll(client, headers)
    _, res = _sign(client, headers, auth)
    pkg = res.json()
    joined = " ".join(pkg["limits"]).lower()
    assert "trusted display" in joined
    assert "not that a particular human was physically present" in joined


def test_the_certificate_is_readable_by_a_person(client):
    headers = _token(client)
    auth, _ = _enroll(client, headers)
    _, res = _sign(client, headers, auth)
    cert = client.get(
        f"/signatures/{res.json()['signature_id']}/certificate").json()
    assert cert["printed_name"] == "Dana Reyes"
    assert cert["meaning"] == "I attest"
    assert cert["what_was_shown"] == "Handoff for M.R., 4mg, 22:00"
    assert cert["valid"] is True
    assert "ESIGN/UETA" in cert["standard"]
    # Never claimed, because it is not true.
    assert "Part 11" in cert["standard"] and "Not a 21 CFR" in cert["standard"]


def test_policy_is_public(client):
    """Someone deciding whether to accept a signature should be able to read
    the rules without an account."""
    res = client.get("/signatures/policy")
    assert res.status_code == 200
    assert res.json()["tiers"]["high"]["device_bound"] is True


def test_a_signature_is_bound_to_the_record_it_signs(client):
    headers = _token(client)
    auth, _ = _enroll(client, headers)
    env = client.post("/signatures/request", json={
        "document": "the release", "meaning": "I grant the likeness",
        "tier": "high", "display_text": "shown",
        "binding_kind": "likeness_release",
        "binding_ref": "pro_123"}, headers=headers).json()
    assertion = auth.assert_(env["challenge"])
    client.post("/signatures/sign",
                json={"envelope_id": env["envelope_id"], **assertion},
                headers=headers)
    found = signatures.signatures_for("likeness_release", "pro_123")
    assert len(found) == 1
    assert found[0]["meaning"] == "I grant the likeness"


# --- the parsing layer ----------------------------------------------------

def test_cbor_refuses_what_it_does_not_understand():
    """Refusing beats improvising: a float where a key type belongs is a
    thing to reject, not coerce."""
    with pytest.raises(webauthn.WebAuthnError):
        webauthn.cbor_decode(b"\xfb\x40\x09\x21\xfb\x54\x44\x2d\x18")
    with pytest.raises(webauthn.WebAuthnError):
        webauthn.cbor_decode(b"\xa0\x00")          # trailing bytes


def test_truncated_authenticator_data_is_refused():
    with pytest.raises(webauthn.WebAuthnError):
        webauthn.parse_authenticator_data(b"\x00" * 20)


def test_base64url_survives_missing_padding():
    raw = b"the quick brown fox"
    unpadded = webauthn.b64url_encode(raw)
    assert "=" not in unpadded
    assert webauthn.b64url_decode(unpadded) == raw


# --- the sequence the apps actually perform -------------------------------
#
# Every test above enrols at `document` level, which is why none of them saw
# that both mobile clients enrol `self_asserted` and then immediately ask for
# `standard` — a happy path that always failed at the server. These walk the
# client's real order.

def test_the_default_client_flow_enrol_then_sign_succeeds(client):
    headers = _token(client)
    auth, enrolled = _enroll(client, headers, level="self_asserted")
    assert enrolled.json()["can_sign"] == ["basic"]

    _, res = _sign(client, headers, auth, tier="basic")
    assert res.status_code == 201, res.text
    assert res.json()["verification"]["valid"] is True


def test_a_credential_can_be_reproofed_to_reach_a_higher_tier(client):
    """The spec promised this and nothing implemented it, which left every
    credential stuck at whatever it enrolled with."""
    headers = _token(client)
    auth, enrolled = _enroll(client, headers, level="self_asserted")
    row_id = enrolled.json()["id"]
    assert "high" not in enrolled.json()["can_sign"]

    res = client.post(f"/signatures/credentials/{row_id}/proofing", json={
        "proofing_level": "document", "proofing_attestor": "clinic-registrar",
        "proofing_method": "government ID + liveness"}, headers=headers)
    assert res.status_code == 200
    assert set(res.json()["can_sign"]) == {"basic", "standard", "high"}

    _, signed = _sign(client, headers, auth, tier="high")
    assert signed.status_code == 201


def test_reproofing_needs_an_attestor_like_enrolment_does(client):
    headers = _token(client)
    _, enrolled = _enroll(client, headers, level="self_asserted")
    res = client.post(
        f"/signatures/credentials/{enrolled.json()['id']}/proofing",
        json={"proofing_level": "document", "proofing_attestor": ""},
        headers=headers)
    assert res.status_code == 422
    assert "attestor" in res.text


def test_reproofing_never_rewrites_what_was_already_signed(client):
    """The level travels into the evidence at signing time, so raising the
    credential today cannot quietly upgrade yesterday's signature."""
    headers = _token(client)
    auth, enrolled = _enroll(client, headers, level="self_asserted")
    _, first = _sign(client, headers, auth, tier="basic")
    sig_id = first.json()["signature_id"]

    client.post(f"/signatures/credentials/{enrolled.json()['id']}/proofing",
                json={"proofing_level": "document",
                      "proofing_attestor": "registrar"}, headers=headers)

    pkg = client.get(f"/signatures/{sig_id}").json()
    assert pkg["signer"]["proofing_level"] == "self_asserted"
    assert pkg["tier"] == "basic"


def test_reproofing_someone_elses_credential_is_refused(client):
    headers = _token(client)
    _, enrolled = _enroll(client, headers, level="self_asserted")
    other = _token(client)
    res = client.post(
        f"/signatures/credentials/{enrolled.json()['id']}/proofing",
        json={"proofing_level": "document", "proofing_attestor": "x"},
        headers=other)
    assert res.status_code == 403
