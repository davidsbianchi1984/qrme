"""A missing field was reported as a broken signature.

Seven signature routes had no console door: enrol a credential, revoke one,
read the policy, mint an envelope, sign it, and check a package handed over
from outside. The console could *list* credentials and reproof one, and could
do nothing else — `Referrals` even wrote the gap down as a sentence, *None
enrolled. The ceremony can enrol one*, under a heading with no button behind
it. The ceremony page existed and posts the raw assertion back to its host;
nothing in the console was listening, so the message went nowhere.

Building the listener found the defect, and it is in the one place this
feature cannot afford one.

`verify_package` runs eight checks in order. Any exception anywhere in that
sequence used to run ``checks["signature"] = False`` and append ``str(exc)``.
So a package missing `display_text` — trimmed in transit, or a summary
forwarded instead of the package — came back saying **the signature is
invalid**, when the signature had verified perfectly well several lines
earlier. That is the strongest and most damaging thing this endpoint can say,
it was false, and the reason offered was ``'display_text'``: a Python
`KeyError` repr, sitting beside two notes written as full sentences.

The argument was already written down in the same file. `qrme/routers/
signatures.py` says of its own refusals: *the message is the reason, because
a signature that is turned away without one is impossible to fix from the
outside.* A counterparty is exactly the outside.

Two rules now hold, and this file pins both:

* a check that already **passed** is never retroactively failed by a later
  failure — only the check that actually broke is reported broken;
* a check that never **ran** is not a pass. `valid` is false whenever any of
  the eight is absent, because ``all()`` over a half-run dictionary is a
  verdict on a question nobody asked.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_signatures import Authenticator, _token  # noqa: E402

from qrme import signatures  # noqa: E402


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()


def _package(client) -> tuple[dict, dict]:
    """A real, valid evidence package — real key, real ECDSA signature."""
    head = _token(client)
    opts = client.post("/signatures/enroll/options",
                       json={"display_name": "Dana Reyes"},
                       headers=head).json()
    auth = Authenticator()
    body = auth.register(opts["challenge"])
    body.update({"proofing_level": "document", "display_name": "Dana Reyes",
                 "proofing_attestor": "clinic-registrar"})
    assert client.post("/signatures/enroll", json=body,
                       headers=head).status_code == 201

    env = client.post("/signatures/request", json={
        "document": "the handoff", "meaning": "I attest", "tier": "high",
        "display_text": "Handoff for M.R."}, headers=head).json()
    res = client.post("/signatures/sign",
                      json={"envelope_id": env["envelope_id"],
                            **auth.assert_(env["challenge"])}, headers=head)
    assert res.status_code == 201, res.text
    pkg = client.get(f"/signatures/{res.json()['signature_id']}").json()
    return head, pkg


def _verdict(client, pkg: dict) -> dict:
    r = client.post("/signatures/verify", json={"package": pkg})
    assert r.status_code == 200, r.text
    return r.json()


def _without(pkg: dict, field: str) -> dict:
    out = json.loads(json.dumps(pkg))
    del out[field]
    return out


# --- the defect -------------------------------------------------------------

def test_a_missing_field_does_not_impeach_the_signature(client):
    """The whole round, in one assertion.

    `display_text` is read at the second-to-last check. Deleting it cannot
    make the ECDSA verification at the top untrue, and saying so was the
    single most consequential lie this endpoint could tell.
    """
    _head, pkg = _package(client)
    assert _verdict(client, pkg)["valid"] is True

    v = _verdict(client, _without(pkg, "display_text"))
    assert v["checks"]["signature"] is True, (
        "the signature verified before the missing field was ever reached; "
        "reporting it false tells a counterparty they hold a forgery")
    assert v["valid"] is False, "an unchecked package is still not a valid one"


def test_the_check_that_could_not_run_is_absent_rather_than_passed(client):
    _head, pkg = _package(client)
    v = _verdict(client, _without(pkg, "display_text"))
    assert "display_text_matches" not in v["checks"]
    assert "user_verified" not in v["checks"], (
        "everything after the failure is unrun too, and unrun is not passed")


def test_the_reason_is_a_sentence_and_not_a_repr(client):
    _head, pkg = _package(client)
    notes = " ".join(_verdict(client, _without(pkg, "display_text"))["notes"])
    assert "display_text" in notes
    assert notes.strip() != "'display_text'"
    assert "nothing here to check against" in notes
    assert "not checked all the way through" in notes


def test_every_expected_check_is_named(client):
    """`valid` is false when anything is unrun, which only works if the list
    of what a complete verification does is written down rather than inferred
    from whichever keys happen to be present."""
    _head, pkg = _package(client)
    assert set(_verdict(client, pkg)["checks"]) == set(
        signatures.VERIFICATION_CHECKS)


def test_a_broken_signature_is_still_reported_broken(client):
    """The fix must not soften the one failure that matters most."""
    _head, pkg = _package(client)
    bad = json.loads(json.dumps(pkg))
    bad["assertion"]["signature"] = "AAAA" + bad["assertion"]["signature"][4:]
    v = _verdict(client, bad)
    assert v["checks"]["signature"] is False
    assert v["valid"] is False


def test_nothing_resembling_a_package_fails_the_signature_check(client):
    v = _verdict(client, {"a": 1})
    assert v["checks"] == {"signature": False}
    assert v["valid"] is False
    assert any("assertion" in n for n in v["notes"])


def test_a_tampered_document_names_the_binding_not_the_signature(client):
    """Swapping the document leaves a real signature over the old one, so the
    check that fails is the binding — this was already right and stays right."""
    _head, pkg = _package(client)
    swapped = json.loads(json.dumps(pkg))
    swapped["document_sha256"] = "0" * 64
    v = _verdict(client, swapped)
    assert v["checks"]["signature"] is True
    assert v["checks"]["payload_binds_document"] is False
    assert v["valid"] is False


# --- the routes the console could not reach ---------------------------------

def test_the_policy_is_readable_without_an_account(client):
    r = client.get("/signatures/policy")
    assert r.status_code == 200
    body = r.json()
    assert body["limits"], "the limits are the point of publishing the policy"
    assert "not a qualified electronic signature" in body["standard"]


def test_verifying_asks_nothing_of_us(client):
    """No token, and no lookup. A verification that needed this deployment's
    blessing would be us vouching, which is what the evidence replaces."""
    _head, pkg = _package(client)
    assert client.post("/signatures/verify",
                       json={"package": pkg}).status_code == 200


def test_enrolling_needs_a_token(client):
    assert client.post("/signatures/enroll/options",
                       json={"display_name": "x"}).status_code == 401


def test_only_the_owner_revokes_a_credential(client):
    head, _pkg = _package(client)
    row = client.get("/signatures/credentials",
                     headers=head).json()["credentials"][0]
    other = client.post("/profiles", json={
        "owner_id": "z9", "kind": "fictional", "display_name": "Zed",
        "persona": "x", "verification": {"birthdate": "1980-01-01"}}).json()
    theirs = {"authorization": f"Bearer {other['owner_token']}"}
    assert client.delete(f"/signatures/credentials/{row['id']}",
                         headers=theirs).status_code == 403
    assert client.delete(
        f"/signatures/credentials/{row['id']}").status_code == 401
    assert client.delete(f"/signatures/credentials/{row['id']}",
                         headers=head).status_code == 200


def test_a_revoked_credential_stops_at_the_envelope(client):
    """Revoking refuses at mint time rather than at signing time, which is the
    kinder place: nothing is generated that cannot be used."""
    head, _pkg = _package(client)
    row = client.get("/signatures/credentials",
                     headers=head).json()["credentials"][0]
    client.delete(f"/signatures/credentials/{row['id']}", headers=head)
    r = client.post("/signatures/request", json={
        "document": "d", "meaning": "I attest", "tier": "high",
        "display_text": "after revoke"}, headers=head)
    assert r.status_code == 422
    assert "no credential enrolled" in r.json()["detail"]


def test_a_signature_already_made_survives_revocation(client):
    """Its public key lives in the evidence, not in the credential table — so
    revoking cannot be used to disown something already signed."""
    head, pkg = _package(client)
    row = client.get("/signatures/credentials",
                     headers=head).json()["credentials"][0]
    client.delete(f"/signatures/credentials/{row['id']}", headers=head)
    assert _verdict(client, pkg)["valid"] is True


# --- the console half -------------------------------------------------------

def _screen() -> str:
    return (REPO / "app/src/screens/Signing.tsx").read_text(encoding="utf-8")


def _markup() -> str:
    s = _screen()
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    return re.sub(r"^\s*//.*$", "", s, flags=re.M)


def test_the_screen_calls_all_seven_bindings():
    src = _screen()
    for binding in ("api.signingPolicy(", "api.enrollOptions(",
                    "api.enrollCredential(", "api.revokeCredential(",
                    "api.requestSignature(", "api.signEnvelope(",
                    "api.verifyPackage("):
        assert binding in src, f"{binding} is still called by nothing"


def test_the_screen_listens_for_the_ceremony():
    """The page posts one message and stops. Opening the window without a
    listener is how these two calls stayed unreachable with the ceremony
    already built and already working."""
    src = _markup()
    assert 'window.addEventListener("message"' in src
    assert 'window.removeEventListener("message"' in src


def test_the_enrolment_carries_its_own_challenge():
    """The ceremony posts the assertion and not the challenge, so a screen
    reading it back off the message would send an empty one and be refused
    for answering no challenge at all."""
    src = _markup()
    assert "challenge: job.challenge" in src


def test_the_screen_draws_an_unrun_check_as_unrun():
    """The rendering half of the defect. A screen that drew absent as a tick
    would put the old lie back on the glass with the backend fixed."""
    flat = " ".join(_markup().split())
    assert "did not run, so it is not a pass" in flat
    assert "v === undefined" in flat


def test_the_screen_shows_the_checks_and_not_only_the_verdict():
    src = _markup()
    assert "verdict.checks[k]" in src
    assert "verdict.notes.map" in src


def test_the_limits_are_rendered_rather_than_summarised():
    """Each line is a claim somebody would otherwise make about a signature
    and be wrong, so the screen prints them rather than paraphrasing."""
    src = _markup()
    assert "policy.limits.map" in src
    assert "policy.standard" in src
