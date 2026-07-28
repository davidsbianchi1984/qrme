"""Medical referral: matched by expertise, released by a real signature.

`POST /handoffs` releases a session summary on `consent: true` — a boolean the
client sets. These cover the stricter path, where the thing that authorises a
health conversation leaving the product is a verified WebAuthn assertion over
the exact bytes being sent.

The assertions worth reading are the refusals: a replayed signature, a summary
edited after signing, and a link opened twice.
"""

import pytest

from tests.test_capabilities import pdi_pair  # noqa: F401
from tests.test_signatures import Authenticator


@pytest.fixture()
def setup(client):
    """A profile, an interactor with a signing credential, and a session."""
    prof = client.post("/profiles", json={
        "owner_id": "o1", "kind": "fictional", "plan": "basic",
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
        "owner_id": "o1", "kind": "fictional", "plan": "basic", "display_name": "Dr. Osei",
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
        "owner_id": "o1", "kind": "fictional", "plan": "basic", "display_name": "Dr. Osei",
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


# -- the clinician writes back ----------------------------------------------
#
# The reason this channel exists is that the patient should not have to retell
# their situation from the top. The reason it is not a `source_items` row is
# that a synthetic profile must never acquire a clinical opinion it can recite
# as its own.

def _released(s):
    prep = _prepare(s).json()
    rid = prep["referral_id"]
    sig = _sign(s, prep["sign"]["challenge"], prep["sign"]["envelope_id"])
    rel = s["client"].post(f"/referrals/{rid}/release", headers=s["me"],
                           json={"signature_id": sig}).json()
    return rid, rel["token"]


def test_opening_it_yields_a_reply_token(setup):
    """Open once, reply once — the summary link stays burnt."""
    s = setup
    rid, token = _released(s)
    opened = s["client"].get(f"/referrals/{rid}?token={token}").json()
    assert opened["reply_token"]
    assert "never spoken as the profile's own" in opened["reply_note"]


def test_the_note_reaches_the_profile_as_the_clinicians_words(setup):
    s = setup
    rid, token = _released(s)
    reply_token = s["client"].get(
        f"/referrals/{rid}?token={token}").json()["reply_token"]

    posted = s["client"].post(
        f"/referrals/{rid}/reply?token={reply_token}",
        json={"content": "Reviewed. Likely costochondritis, not cardiac. "
                         "Booked for review in two weeks."})
    assert posted.status_code == 201

    from qrme import persona, referral as ref_mod
    notes = ref_mod.notes_for(s["profile"]["id"], s["interactor"]["id"])
    assert notes[0]["from"] == "Riverside Cardiology"
    assert "costochondritis" in notes[0]["content"]

    # The prompt carries it attributed, and says plainly whose words they are.
    from qrme import db
    profile = dict(db.connect().execute(
        "SELECT * FROM profiles WHERE id=?", (s["profile"]["id"],)).fetchone())
    system = persona.build_system_prompt(profile, None, None,
                                         clinical_notes=notes)
    assert "Riverside Cardiology" in system
    assert "costochondritis" in system
    assert "not yours" in system
    assert "never present this as your own assessment" in system
    # And the reason it is carried at all.
    assert "need not explain it again" in system


def test_a_note_is_never_source_material(setup):
    """Source material is what a profile recalls *as its own*, and it is what
    a workflow's `research` phase reads. A clinical opinion in there could be
    recited as the profile's own knowledge — and drafted from."""
    s = setup
    rid, token = _released(s)
    reply_token = s["client"].get(
        f"/referrals/{rid}?token={token}").json()["reply_token"]
    s["client"].post(f"/referrals/{rid}/reply?token={reply_token}",
                     json={"content": "Likely costochondritis."})

    from qrme import db
    rows = db.connect().execute(
        "SELECT * FROM source_items WHERE profile_id=?",
        (s["profile"]["id"],)).fetchall()
    assert all("costochondritis" not in (r["content"] or "") for r in rows)

    from qrme import workflows
    items, ok = workflows._scoped_items(s["profile"]["id"], None, None)
    assert ok
    assert all("costochondritis" not in (i.get("content") or "") for i in items)


def test_a_clinician_writes_back_once(setup):
    s = setup
    rid, token = _released(s)
    reply_token = s["client"].get(
        f"/referrals/{rid}?token={token}").json()["reply_token"]
    first = s["client"].post(f"/referrals/{rid}/reply?token={reply_token}",
                             json={"content": "Reviewed."})
    assert first.status_code == 201
    second = s["client"].post(f"/referrals/{rid}/reply?token={reply_token}",
                              json={"content": "And another thing."})
    assert second.status_code == 403
    assert "already written back" in second.json()["detail"]


def test_a_wrong_reply_link_is_refused(setup):
    s = setup
    rid, token = _released(s)
    s["client"].get(f"/referrals/{rid}?token={token}")
    r = s["client"].post(f"/referrals/{rid}/reply?token=rpl_wrong",
                         json={"content": "hello"})
    assert r.status_code == 403


def test_nobody_can_write_back_before_it_is_opened(setup):
    s = setup
    rid, _ = _released(s)          # released, but never opened
    r = s["client"].post(f"/referrals/{rid}/reply?token=rpl_guess",
                         json={"content": "hello"})
    assert r.status_code == 403
    assert "not been opened" in r.json()["detail"]


def test_an_empty_note_is_refused(setup):
    s = setup
    rid, token = _released(s)
    reply_token = s["client"].get(
        f"/referrals/{rid}?token={token}").json()["reply_token"]
    r = s["client"].post(f"/referrals/{rid}/reply?token={reply_token}",
                         json={"content": "   "})
    assert r.status_code == 403


def test_the_note_belongs_to_one_conversation_only(setup):
    """It is that person's medical information. Another interactor talking to
    the same profile must never see it."""
    s = setup
    rid, token = _released(s)
    reply_token = s["client"].get(
        f"/referrals/{rid}?token={token}").json()["reply_token"]
    s["client"].post(f"/referrals/{rid}/reply?token={reply_token}",
                     json={"content": "Likely costochondritis."})

    other = s["client"].post("/interactors", json={
        "display_name": "Mal", "birthdate": "1990-01-01"}).json()
    from qrme import referral as ref_mod
    assert ref_mod.notes_for(s["profile"]["id"], other["id"]) == []

    # And they cannot read it through the API either.
    r = s["client"].get(
        f"/profiles/{s['profile']['id']}/clinical-notes/{s['interactor']['id']}",
        headers={"authorization": f"Bearer {other['token']}"})
    assert r.status_code == 403


def test_the_patient_can_read_what_the_clinician_wrote(setup):
    s = setup
    rid, token = _released(s)
    reply_token = s["client"].get(
        f"/referrals/{rid}?token={token}").json()["reply_token"]
    s["client"].post(f"/referrals/{rid}/reply?token={reply_token}",
                     json={"content": "Likely costochondritis."})

    out = s["client"].get(
        f"/profiles/{s['profile']['id']}/clinical-notes/{s['interactor']['id']}",
        headers=s["me"]).json()
    assert out[0]["from"] == "Riverside Cardiology"
    assert "costochondritis" in out[0]["content"]


def test_the_note_is_sealed_in_the_pdi_vault(pdi_pair):
    """The same treatment source material gets: the content lives in the
    vault, QRME keeps only a key reference, and it resolves on read."""
    client, fake = pdi_pair
    prof = client.post("/profiles", json={
        "owner_id": "o1", "kind": "fictional", "plan": "basic",
        "display_name": "Dr. Amara Osei", "persona": "A physician.",
        "verification": {"birthdate": "1980-01-01"}}).json()
    owner = {"authorization": f"Bearer {prof['owner_token']}"}
    it = client.post("/interactors", json={"display_name": "Dana Reyes",
                                           "birthdate": "1990-03-02"}).json()
    me = {"authorization": f"Bearer {it['token']}"}
    client.post(f"/profiles/{prof['id']}/chat", headers=owner, json={
        "interactor_id": it["id"], "message": "my chest has been tight"})

    auth = Authenticator()
    opts = client.post("/signatures/enroll/options",
                       json={"display_name": "Dana Reyes"},
                       headers=me).json()
    body = auth.register(opts["challenge"])
    body.update({"proofing_level": "document", "display_name": "Dana Reyes",
                 "proofing_attestor": "clinic-registrar"})
    client.post("/signatures/enroll", json=body, headers=me)
    prov = client.post("/providers", json={"name": "Riverside Cardiology",
                                           "area": "medical",
                                           "location": "Leeds"}).json()

    prep = client.post("/referrals/prepare", headers=me, json={
        "interactor_id": it["id"], "profile_id": prof["id"],
        "provider_id": prov["id"]}).json()
    assertion = auth.assert_(prep["sign"]["challenge"])
    sig = client.post("/signatures/sign", headers=me, json={
        "envelope_id": prep["sign"]["envelope_id"], **assertion}).json()
    rel = client.post(f"/referrals/{prep['referral_id']}/release", headers=me,
                      json={"signature_id": sig["signature_id"]}).json()
    reply_token = client.get(
        f"/referrals/{prep['referral_id']}?token={rel['token']}"
    ).json()["reply_token"]

    posted = client.post(
        f"/referrals/{prep['referral_id']}/reply?token={reply_token}",
        json={"content": "Likely costochondritis, not cardiac."}).json()
    assert posted["sealed"] is True

    # In the vault, under a qrme/ key PDI attributes to QRME.
    key = f"qrme/{prof['id']}/clinical/{posted['id']}"
    assert "costochondritis" in fake.store[key]

    # And not in QRME's own database.
    from qrme import db as qdb
    row = qdb.connect().execute(
        "SELECT content, pdi_key FROM clinical_notes WHERE id=?",
        (posted["id"],)).fetchone()
    assert row["content"] is None
    assert row["pdi_key"] == key

    # Resolved on read, so the profile still gets caught up.
    out = client.get(
        f"/profiles/{prof['id']}/clinical-notes/{it['id']}",
        headers=me).json()
    assert "costochondritis" in out[0]["content"]
