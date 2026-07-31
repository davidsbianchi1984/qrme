"""Handing a conversation to a clinician, and what the signature covers.

A profile is not a clinician. The whole feature exists so that a person who has
been talking to one about a symptom can hand that conversation to somebody
qualified — and every part of it is built to be awkward in the places where the
easy version would be wrong:

* **prepare releases nothing.** It assembles the summary and raises a
  challenge whose value *is the hash of those bytes*, so signing it signs this
  summary rather than a checkbox — and a summary edited afterwards cannot ride
  the old signature;
* **the link works once.** A second attempt says *when* the first happened
  rather than quietly working, because a replayed link is something the patient
  should be able to discover;
* **the package says what the specialist is** before it says anything else:
  an AI profile, not a clinician, and nothing in it is a diagnosis.

Three pairs here are one wrong variable away from a bug that looks like
success, and each has a test:

* the **referral token** opens it; the **reply token** answers it, and does not
  exist until the link has been opened;
* `envelope_id` is what gets signed; `signature_id` is what release checks;
* a credential's **proofing level** is not its **tier** — `can_sign` is the
  join, and a self-asserted credential cannot carry a referral.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()
sys.path.insert(0, str(Path(__file__).resolve().parent))

# The fake authenticator that already exists for the signature suite. Reused
# rather than rebuilt: a second copy would drift, and this one is the shape
# the real ceremony produces.
from test_signatures import Authenticator  # noqa: E402


def _setup(client, account="o_ref"):
    """A profile, somebody who has talked to it, a clinician, and a device."""
    p = client.post("/profiles", json={
        "owner_id": account, "kind": "fictional", "display_name": "Doc",
        "purpose": "companion_coach", "persona": "p",
        "verification": {"birthdate": "1980-01-01"}}).json()
    head = {"authorization": f"Bearer {p['owner_token']}"}
    client.post(f"/memberships/{account}", json={"plan": "pro"}, headers=head)

    who = client.post("/interactors", json={"display_name": "Pat"}).json()
    ihead = {"authorization": f"Bearer {who['token']}"}
    client.post(f"/profiles/{p['id']}/chat", headers=ihead,
                json={"interactor_id": who["id"],
                      "message": "my knee hurts on stairs"})

    provider = client.post("/providers", json={
        "name": "Bath Physio", "area": "physiotherapy", "location": "Bath",
        "contact": "hello@example", "business": True}).json()
    return p, head, who, ihead, provider


def _enrol(client, ihead, level="document"):
    auth = Authenticator()
    opts = client.post("/signatures/enroll/options",
                       json={"display_name": "Pat"}, headers=ihead).json()
    body = auth.register(opts["challenge"])
    body.update({"proofing_level": level, "display_name": "Pat"}
                if level == "self_asserted" else
                {"proofing_level": level, "display_name": "Pat",
                 "proofing_attestor": "clinic-registrar"})
    return auth, client.post("/signatures/enroll", json=body,
                             headers=ihead).json()


def _released(client, account="o_rel"):
    """The whole flow, up to a link in a clinician's hand."""
    p, head, who, ihead, provider = _setup(client, account)
    auth, _ = _enrol(client, ihead)
    prep = client.post("/referrals/prepare", headers=ihead, json={
        "interactor_id": who["id"], "profile_id": p["id"],
        "provider_id": provider["id"]}).json()
    sign = prep["sign"]
    sig = client.post("/signatures/sign", headers=ihead, json={
        "envelope_id": sign["envelope_id"],
        **auth.assert_(sign["challenge"])}).json()
    rel = client.post(f"/referrals/{prep['referral_id']}/release",
                      json={"signature_id": sig["signature_id"]},
                      headers=ihead).json()
    return p, head, who, ihead, prep, sig, rel


# --- what the signature is over -------------------------------------------

def test_preparing_releases_nothing(client):
    """The reason prepare is a separate step: somebody reads the summary
    before any of it can leave."""
    p, _, who, ihead, provider = _setup(client, "o_prep")
    _enrol(client, ihead)
    prep = client.post("/referrals/prepare", headers=ihead, json={
        "interactor_id": who["id"], "profile_id": p["id"],
        "provider_id": provider["id"]})
    assert prep.status_code == 201, prep.text
    body = prep.json()
    assert "token" not in body, "prepare handed out a link"
    history = client.get(f"/interactors/{who['id']}/referrals",
                         headers=ihead).json()
    assert all(not h["released"] for h in history)


def test_the_package_says_it_is_not_a_clinician_first(client):
    """The single most important sentence on the screen, and it comes from
    the server so there is one copy of it."""
    p, _, who, ihead, provider = _setup(client, "o_says")
    _enrol(client, ihead)
    prep = client.post("/referrals/prepare", headers=ihead, json={
        "interactor_id": who["id"], "profile_id": p["id"],
        "provider_id": provider["id"]}).json()
    spec = prep["package"]["specialist"]
    assert spec["synthetic"] is True
    assert "not a clinician" in spec["note"]
    assert "diagnosis" in spec["note"]


def test_the_challenge_is_the_hash_of_what_was_shown(client):
    """`display_sha256` in the payload covers the words on the screen, not
    just the document. A signature over a document nobody saw is a signature
    over nothing, and this is the field that makes it otherwise."""
    p, _, who, ihead, provider = _setup(client, "o_hash")
    _enrol(client, ihead)
    prep = client.post("/referrals/prepare", headers=ihead, json={
        "interactor_id": who["id"], "profile_id": p["id"],
        "provider_id": provider["id"]}).json()
    payload = prep["sign"]["payload"]
    assert payload["doc_sha256"] and payload["display_sha256"]
    assert payload["tier"] == "high"
    assert prep["sign"]["display_text"] == prep["display_text"], (
        "the text being signed over is no longer the text being shown")


def test_a_self_asserted_credential_cannot_carry_a_referral(client):
    """Proofing level is not tier — `can_sign` is the join, and the screen
    shows that list rather than explaining the rules."""
    p, _, who, ihead, provider = _setup(client, "o_weak")
    _, cred = _enrol(client, ihead, level="self_asserted")
    assert cred["can_sign"] == ["basic"]
    r = client.post("/referrals/prepare", headers=ihead, json={
        "interactor_id": who["id"], "profile_id": p["id"],
        "provider_id": provider["id"]})
    assert r.status_code == 422
    assert "high" in r.json()["detail"]


def test_recording_a_document_check_opens_the_high_tier(client):
    """What `POST /signatures/credentials/{row}/proofing` is for, and the
    visible consequence the screen renders."""
    p, _, who, ihead, provider = _setup(client, "o_reproof")
    _, cred = _enrol(client, ihead, level="self_asserted")
    after = client.post(f"/signatures/credentials/{cred['id']}/proofing",
                        headers=ihead,
                        json={"proofing_level": "document",
                              "proofing_attestor": "clinic-registrar",
                              "proofing_method": "passport"}).json()
    assert "high" in after["can_sign"]
    assert client.post("/referrals/prepare", headers=ihead, json={
        "interactor_id": who["id"], "profile_id": p["id"],
        "provider_id": provider["id"]}).status_code == 201


# --- the link -------------------------------------------------------------

def test_the_link_opens_once_and_says_when_it_did(client):
    """A replayed link is something the patient should be able to discover,
    so the second attempt carries the time of the first rather than a bare
    refusal — and certainly rather than working again."""
    _, _, _, _, _, _, rel = _released(client, "o_once")
    first = client.get(f"/referrals/{rel['id']}?token={rel['token']}")
    assert first.status_code == 200, first.text

    again = client.get(f"/referrals/{rel['id']}?token={rel['token']}")
    assert again.status_code == 410
    assert "already opened" in again.json()["detail"]


def test_the_reply_token_is_not_the_one_that_opened_it(client):
    """Two tokens, arriving at different moments, one letter apart in a
    variable name. Answering with the wrong one 403s, which is the good
    outcome — but only a test proves the right one is the other."""
    _, _, _, _, _, _, rel = _released(client, "o_two")
    opened = client.get(f"/referrals/{rel['id']}?token={rel['token']}").json()
    assert opened["reply_token"] != rel["token"]

    wrong = client.post(f"/referrals/{rel['id']}/reply?token={rel['token']}",
                        json={"content": "Seen."})
    assert wrong.status_code == 403

    right = client.post(
        f"/referrals/{rel['id']}/reply?token={opened['reply_token']}",
        json={"content": "Seen. Six weeks of loading exercises."})
    assert right.status_code == 201, right.text


def test_the_clinicians_words_stay_theirs(client):
    """Recorded and attributed, and never something the profile can recite
    as its own knowledge."""
    p, head, who, ihead, _, _, rel = _released(client, "o_words")
    opened = client.get(f"/referrals/{rel['id']}?token={rel['token']}").json()
    assert "never spoken as the profile's own" in opened["reply_note"]
    client.post(f"/referrals/{rel['id']}/reply?token={opened['reply_token']}",
                json={"content": "Seen. Six weeks of loading."})
    notes = client.get(f"/profiles/{p['id']}/clinical-notes/{who['id']}",
                       headers=ihead).json()
    assert len(notes) == 1
    assert notes[0]["from"] == "Bath Physio"
    assert "loading" in notes[0]["content"]


def test_a_clinical_note_is_readable_only_by_the_pair(client):
    """The person it is about, and the profile's owner. Nobody else — it is
    that person's medical information."""
    p, _, who, _, _, _, rel = _released(client, "o_private")
    opened = client.get(f"/referrals/{rel['id']}?token={rel['token']}").json()
    client.post(f"/referrals/{rel['id']}/reply?token={opened['reply_token']}",
                json={"content": "Seen."})
    stranger = client.post("/interactors",
                           json={"display_name": "Nosy"}).json()
    r = client.get(f"/profiles/{p['id']}/clinical-notes/{who['id']}",
                   headers={"authorization": f"Bearer {stranger['token']}"})
    assert r.status_code in (401, 403)


# --- matching -------------------------------------------------------------

def test_expertise_filters_and_geography_only_ranks(client):
    """A cardiologist two streets away is not a substitute for a
    psychiatrist. Sorting by distance first is how that swap happens
    quietly, so area is a filter and location is not."""
    client.post("/providers", json={
        "name": "Near Cardio", "area": "cardiology", "location": "Bath",
        "contact": "c@example", "business": True})
    client.post("/providers", json={
        "name": "Far Physio", "area": "physiotherapy", "location": "Leeds",
        "contact": "p@example", "business": True})
    out = client.get("/referrals/match?area=physiotherapy&location=Bath").json()
    assert all(c["area"] == "physiotherapy" for c in out), (
        "a different speciality came back because it was closer")


def test_no_match_is_an_empty_list_rather_than_a_near_miss(client):
    """A confident wrong referral is somebody phoning a clinic that cannot
    help them."""
    assert client.get("/referrals/match?area=nothing-like-this").json() == []


def test_a_match_explains_itself_in_words(client):
    """`match` is a sentence, not a score — a number would imply a precision
    the data does not have."""
    client.post("/providers", json={
        "name": "Bath Physio", "area": "physiotherapy", "location": "Bath",
        "contact": "h@example", "business": True})
    hit = client.get(
        "/referrals/match?area=physiotherapy&location=Bath").json()[0]
    assert hit["match"] and not isinstance(hit["match"], (int, float))
    assert hit["in_your_area"] is True


# --- the certificate ------------------------------------------------------

def test_the_certificate_keeps_the_words_that_were_shown(client):
    _, _, _, _, _, sig, _ = _released(client, "o_cert")
    cert = client.get(f"/signatures/{sig['signature_id']}/certificate").json()
    assert cert["valid"] is True
    assert cert["tier"] == "high"
    assert cert["identity_verified_as"] == "document"
    assert cert["what_was_shown"], (
        "the certificate no longer carries what the signer read, so it "
        "attests to a hash of something nobody can see")
    assert cert["document_sha256"]
    assert "ESIGN" in cert["standard"]


def test_the_ceremony_page_refuses_without_a_challenge(client):
    """It is a page, not a request, and the one thing it cannot do without
    is the thing being signed over."""
    assert client.get("/signatures/ceremony").status_code == 422
    assert client.get(
        "/signatures/ceremony?mode=sign&challenge=abc").status_code == 200


def test_the_ceremony_page_takes_no_token(client):
    """A bearer token in a query string ends up in logs and history. The
    page runs the ceremony and posts the raw assertion to its host, and the
    host makes the authenticated call."""
    r = client.get("/signatures/ceremony?mode=sign&challenge=abc")
    assert r.status_code == 200
    assert "authorization" not in r.text.lower() or "Bearer" not in r.text


# --- the console half -----------------------------------------------------

def _src(rel: str) -> str:
    return (REPO / rel).read_text(encoding="utf-8")


def test_the_referral_screen_exists():
    assert (REPO / "app/src/screens/Referrals.tsx").exists()


@pytest.mark.parametrize("binding", [
    "api.clinicians(", "api.providers(", "api.addProvider(",
    "api.prepareReferral(", "api.releaseReferral(", "api.openReferral(",
    "api.replyToReferral(", "api.myReferrals(", "api.clinicalNotes(",
    "api.signingCredentials(", "api.reproof(", "api.certificate(",
    "openCeremony(",
])
def test_the_referral_screen_calls_it(binding):
    assert binding in _src("app/src/screens/Referrals.tsx")


def test_the_reply_uses_the_reply_token():
    """The console half of the two-token trap. Passing the opening token
    compiles, reads naturally, and 403s every time."""
    src = _src("app/src/screens/Referrals.tsx")
    assert "opened.reply_token" in src, (
        "the reply is being sent with something other than the reply token")


def test_the_ceremony_url_is_visible_to_the_route_audit():
    """A page the browser navigates to is still a door.

    The literal has to start with `/` for the extractor to resolve it, so
    `getBase() + \\`/signatures/ceremony…\\`` rather than a template opening
    with an interpolation — otherwise this door goes on counting as missing
    while working perfectly.
    """
    api = _src("app/src/api.ts")
    assert 'getBase() + `/signatures/ceremony?' in api


def test_the_screen_shows_what_a_credential_can_sign():
    """`can_sign` rather than the tier table: it is the fact somebody needs
    when the button is greyed out."""
    assert "can_sign" in _src("app/src/screens/Referrals.tsx")
