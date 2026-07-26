"""Medical referral: matched by expertise, released by a real signature.

`POST /handoffs` releases a session summary on `consent: true` — a boolean the
client sets. These cover the stricter path, where the thing that authorises a
health conversation leaving the product is a verified WebAuthn assertion over
the exact bytes being sent.

The assertions worth reading are the refusals: a replayed signature, a summary
edited after signing, and a link opened twice.
"""

import pytest

from tests.test_signatures import Authenticator


@pytest.fixture()
def setup(client):
    """A profile, an interactor with a signing credential, and a session."""
    prof = client.post("/profiles", json={
        "owner_id": "o1", "kind": "fictional",
        "display_name": "Dr. Amara Osei", "persona": "A physician.",
        "verification": {"birthdate": "1980-01-01"}}).json()
    owner = {"authorization": f"Bearer {prof['owner_token']}"}

    it = client.post("/interactors", json={"display_name": "Dana Reyes",
                                           "birthdate": "1990-03-02"}).json()
    me = {"authorization": f"Bearer {it['token']}"}

    # A conversation to refer.
    client.post(f"/profiles/{prof['id']}/chat", headers=owner, json={
        "interactor_id": it["id"], "message": "my chest has been tight"})

    # The interactor enrols a device-bound, document-proofed credential —
    # what the `high` tier a referral signs at requires.
    auth = Authenticator()
    opts = client.post("/signatures/enroll/options",
                       json={"display_name": "Dana Reyes"},
                       headers=me).json()
    body = auth.register(opts["challenge"])
    body.update({"proofing_level": "document", "display_name": "Dana Reyes",
                 "proofing_attestor": "clinic-registrar"})
    assert client.post("/signatures/enroll", json=body,
                       headers=me).status_code == 201

    prov = client.post("/providers", json={
        "name": "Riverside Cardiology", "area": "medical",
        "location": "Leeds", "contact": "0113 000 0000"}).json()
    return {"client": client, "profile": prof, "interactor": it, "me": me,
            "auth": auth, "provider": prov}


def _prepare(s, provider_id=None):
    return s["client"].post("/referrals/prepare", headers=s["me"], json={
        "interactor_id": s["interactor"]["id"],
        "profile_id": s["profile"]["id"],
        "provider_id": provider_id or s["provider"]["id"]})


def _sign(s, challenge, envelope_id):
    assertion = s["auth"].assert_(challenge)
    r = s["client"].post("/signatures/sign", headers=s["me"],
                         json={"envelope_id": envelope_id, **assertion})
    assert r.status_code == 201, r.text
    return r.json()["signature_id"]


# -- matching ---------------------------------------------------------------

def test_expertise_filters_and_geography_only_ranks(client):
    """A cardiologist two streets away is not a substitute for a
    psychiatrist. Sorting by distance first is how that swap happens."""
    client.post("/providers", json={"name": "Near Therapy", "area": "mental_health",
                                    "location": "Leeds"})
    client.post("/providers", json={"name": "Far Cardio", "area": "medical",
                                    "location": "Truro"})
    client.post("/providers", json={"name": "Near Cardio", "area": "medical",
                                    "location": "Leeds"})

    out = client.get("/referrals/match?area=medical&location=Leeds").json()
    assert [p["name"] for p in out] == ["Near Cardio", "Far Cardio"]
    assert out[0]["in_your_area"] is True
    assert out[0]["match"] == "area and location"
    assert out[1]["match"] == "area of expertise"
    assert "Near Therapy" not in [p["name"] for p in out]


def test_no_match_returns_nothing_rather_than_a_near_miss(client):
    client.post("/providers", json={"name": "Near Therapy",
                                    "area": "mental_health", "location": "Leeds"})
    assert client.get("/referrals/match?area=oncology&location=Leeds").json() == []


# -- preparing --------------------------------------------------------------

def test_prepare_shows_the_package_and_releases_nothing(setup):
    s = setup
    out = _prepare(s).json()
    assert out["clinician"] == "Riverside Cardiology"
    assert out["package"]["recent_exchange"]
    # The specialist is named as synthetic inside the document itself: a
    # clinician reading a transcript must never have to work out which voice
    # was a person.
    assert out["package"]["specialist"]["synthetic"] is True
    assert "not a clinician" in out["package"]["specialist"]["note"]
    # What the user is shown, recorded verbatim.
    assert "Riverside Cardiology" in out["display_text"]
    assert out["sign"]["user_verification"] == "required"
    assert out["sign"]["tier"] == "high"

    # Nothing is readable yet — no token exists.
    assert s["client"].get(
        f"/referrals/{out['referral_id']}?token=anything").status_code == 403


def test_a_referral_with_nothing_to_refer_is_refused(client):
    prof = client.post("/profiles", json={
        "owner_id": "o1", "kind": "fictional", "display_name": "Dr. Osei",
        "persona": "A physician.",
        "verification": {"birthdate": "1980-01-01"}}).json()
    it = client.post("/interactors", json={"display_name": "Dana",
                                           "birthdate": "1990-03-02"}).json()
    prov = client.post("/providers", json={"name": "Clinic",
                                           "area": "medical"}).json()
    r = client.post("/referrals/prepare",
                    headers={"authorization": f"Bearer {it['token']}"},
                    json={"interactor_id": it["id"], "profile_id": prof["id"],
                          "provider_id": prov["id"]})
    assert r.status_code == 422
    assert "nothing to refer" in r.json()["detail"]


def test_an_account_with_no_high_tier_credential_is_told_why(client):
    """Silently dropping to a weaker tier would be the checkbox again wearing
    a signature's name."""
    prof = client.post("/profiles", json={
        "owner_id": "o1", "kind": "fictional", "display_name": "Dr. Osei",
        "persona": "A physician.",
        "verification": {"birthdate": "1980-01-01"}}).json()
    owner = {"authorization": f"Bearer {prof['owner_token']}"}
    it = client.post("/interactors", json={"display_name": "Dana",
                                           "birthdate": "1990-03-02"}).json()
    me = {"authorization": f"Bearer {it['token']}"}
    client.post(f"/profiles/{prof['id']}/chat", headers=owner,
                json={"interactor_id": it["id"], "message": "hello"})
    prov = client.post("/providers", json={"name": "Clinic",
                                           "area": "medical"}).json()

    r = client.post("/referrals/prepare", headers=me, json={
        "interactor_id": it["id"], "profile_id": prof["id"],
        "provider_id": prov["id"]})
    assert r.status_code == 422
    assert "no credential enrolled to the 'high' tier" in r.json()["detail"]


# -- releasing --------------------------------------------------------------

def test_the_signature_releases_it_and_the_link_opens_once(setup):
    s = setup
    prep = _prepare(s).json()
    rid = prep["referral_id"]
    sig = _sign(s, prep["sign"]["challenge"], prep["sign"]["envelope_id"])

    rel = s["client"].post(f"/referrals/{rid}/release", headers=s["me"],
                           json={"signature_id": sig}).json()
    assert rel["one_time"] is True
    assert rel["signed_by"]["proofing_level"] == "document"

    opened = s["client"].get(f"/referrals/{rid}?token={rel['token']}")
    assert opened.status_code == 200
    assert opened.json()["package"]["recent_exchange"]

    again = s["client"].get(f"/referrals/{rid}?token={rel['token']}")
    assert again.status_code == 410
    assert "works once" in again.json()["detail"]


def test_release_needs_a_signature_not_a_claim(setup):
    """There is no consent boolean on this path at all — the only way through
    is an assertion that verifies."""
    s = setup
    rid = _prepare(s).json()["referral_id"]
    r = s["client"].post(f"/referrals/{rid}/release", headers=s["me"],
                         json={"signature_id": "sig_made_up"})
    assert r.status_code == 403
    assert "no such signature" in r.json()["detail"]


def test_a_signature_for_something_else_cannot_release_a_referral(setup):
    """The envelope is bound to this referral, so a valid assertion raised
    for another purpose is not a skeleton key."""
    s = setup
    rid = _prepare(s).json()["referral_id"]

    # A perfectly good signature — over an unrelated document.
    env = s["client"].post("/signatures/request", headers=s["me"], json={
        "document": "something else entirely", "meaning": "I attest",
        "tier": "high", "display_text": "Unrelated"}).json()
    other = _sign(s, env["challenge"], env["envelope_id"])

    r = s["client"].post(f"/referrals/{rid}/release", headers=s["me"],
                         json={"signature_id": other})
    assert r.status_code == 403
    assert "authorises something else" in r.json()["detail"]


def test_a_second_referral_cannot_ride_the_first_ones_signature(setup):
    s = setup
    first = _prepare(s).json()
    sig = _sign(s, first["sign"]["challenge"], first["sign"]["envelope_id"])
    s["client"].post(f"/referrals/{first['referral_id']}/release",
                     headers=s["me"], json={"signature_id": sig})

    second = _prepare(s).json()
    r = s["client"].post(f"/referrals/{second['referral_id']}/release",
                         headers=s["me"], json={"signature_id": sig})
    assert r.status_code == 403
    assert "authorises something else" in r.json()["detail"]


def test_releasing_twice_is_refused(setup):
    s = setup
    prep = _prepare(s).json()
    rid = prep["referral_id"]
    sig = _sign(s, prep["sign"]["challenge"], prep["sign"]["envelope_id"])
    s["client"].post(f"/referrals/{rid}/release", headers=s["me"],
                     json={"signature_id": sig})
    r = s["client"].post(f"/referrals/{rid}/release", headers=s["me"],
                         json={"signature_id": sig})
    assert r.status_code == 403
    assert "already been released" in r.json()["detail"]


def test_a_summary_edited_after_signing_cannot_be_sent(setup):
    """The guarantee is arithmetic: the release re-hashes the package and
    compares it to what the signature covered."""
    s = setup
    prep = _prepare(s).json()
    rid = prep["referral_id"]
    sig = _sign(s, prep["sign"]["challenge"], prep["sign"]["envelope_id"])

    # Tamper with the stored package after the signature was collected.
    from qrme import db
    conn = db.connect()
    conn.execute("UPDATE referrals SET package=? WHERE id=?",
                 ('{"user": "Dana", "recent_exchange": ["everything"]}', rid))
    conn.commit()

    r = s["client"].post(f"/referrals/{rid}/release", headers=s["me"],
                         json={"signature_id": sig})
    assert r.status_code == 403
    assert "changed after it was signed" in r.json()["detail"]


# -- who may do what --------------------------------------------------------

def test_another_interactor_cannot_prepare_or_release_yours(setup):
    s = setup
    prep = _prepare(s).json()
    mal = s["client"].post("/interactors", json={
        "display_name": "Mal", "birthdate": "1990-01-01"}).json()
    mal_h = {"authorization": f"Bearer {mal['token']}"}

    assert s["client"].post("/referrals/prepare", headers=mal_h, json={
        "interactor_id": s["interactor"]["id"],
        "profile_id": s["profile"]["id"],
        "provider_id": s["provider"]["id"]}).status_code == 403
    assert s["client"].post(
        f"/referrals/{prep['referral_id']}/release", headers=mal_h,
        json={"signature_id": "x"}).status_code == 403


def test_a_wrong_link_does_not_open_it(setup):
    s = setup
    prep = _prepare(s).json()
    rid = prep["referral_id"]
    sig = _sign(s, prep["sign"]["challenge"], prep["sign"]["envelope_id"])
    s["client"].post(f"/referrals/{rid}/release", headers=s["me"],
                     json={"signature_id": sig})

    assert s["client"].get(f"/referrals/{rid}?token=ref_wrong").status_code == 403


def test_the_patient_can_see_what_they_released_and_whether_it_was_opened(setup):
    s = setup
    prep = _prepare(s).json()
    rid = prep["referral_id"]
    sig = _sign(s, prep["sign"]["challenge"], prep["sign"]["envelope_id"])
    rel = s["client"].post(f"/referrals/{rid}/release", headers=s["me"],
                           json={"signature_id": sig}).json()

    iid = s["interactor"]["id"]
    before = s["client"].get(f"/interactors/{iid}/referrals",
                             headers=s["me"]).json()
    assert before[0]["released"] is True and before[0]["opened_at"] is None

    s["client"].get(f"/referrals/{rid}?token={rel['token']}")
    after = s["client"].get(f"/interactors/{iid}/referrals",
                            headers=s["me"]).json()
    assert after[0]["opened_at"] is not None
