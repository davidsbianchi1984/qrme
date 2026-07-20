"""Objection / takedown flow and the restricted & terminated states."""

from tests.test_capabilities import ADULT, make_interactor, make_profile


def _third_party(client, **extra):
    """A profile *of another real person*, which needs a consent basis."""
    body = {"owner_id": "owner-1", "kind": "other_person",
            "display_name": "Real Person", "persona": "A public commentator.",
            "verification": ADULT,
            "consent": {"basis": "subject_consent", "attestor": "the subject"}}
    body.update(extra)
    r = client.post("/profiles", json=body)
    assert r.status_code == 201, r.text
    out = r.json()
    client.headers["authorization"] = f"Bearer {out['owner_token']}"
    return out


def test_opening_an_objection_restricts_the_profile(client):
    p = _third_party(client)
    obj = client.post("/objections", json={
        "profile_id": p["id"], "objector_ref": "id-doc-123",
        "reason": "that's me and I did not consent"}).json()
    assert obj["status"] == "open"
    assert obj["profile_status"] == "restricted"
    # The profile card now shows restricted and is not publicly reachable.
    assert client.get(f"/profiles/{p['id']}").json()["status"] == "restricted"


def test_restricted_profile_blocks_new_interactors_and_discovery(client):
    p = _third_party(client)
    # An existing relationship, established before the objection.
    old_user = make_interactor(client)
    client.put(f"/profiles/{p['id']}/relationships/{old_user}",
               json={"relationship_type": "friend"})
    client.post(f"/profiles/{p['id']}/marketplace",
                json={"tags": ["news"], "blurb": "commentary"})

    client.post("/objections", json={
        "profile_id": p["id"], "objector_ref": "id-doc-123"})

    # New interactor is turned away; the prior relationship may continue.
    new_user = make_interactor(client, name="Newcomer")
    blocked = client.post(f"/profiles/{p['id']}/chat", json={
        "interactor_id": new_user, "message": "hi"})
    assert blocked.status_code == 403
    ok = client.post(f"/profiles/{p['id']}/chat", json={
        "interactor_id": old_user, "message": "still here"})
    assert ok.status_code == 200
    # And it disappears from public discovery.
    assert client.get("/marketplace").json() == []


def test_dismissing_an_objection_restores_the_profile(client):
    p = _third_party(client)
    obj = client.post("/objections", json={
        "profile_id": p["id"], "objector_ref": "ref"}).json()
    client.post(
        f"/profiles/{p['id']}/objections/{obj['id']}/attest")   # owner re-attests

    resolved = client.post(f"/objections/{obj['id']}/resolve",
                           json={"outcome": "dismiss"}).json()
    assert resolved["status"] == "dismissed"
    assert resolved["profile_status"] == "active"
    assert client.get(f"/profiles/{p['id']}").json()["status"] == "active"


def test_upholding_an_objection_terminates_the_profile(client):
    p = _third_party(client)
    user = make_interactor(client)
    client.put(f"/profiles/{p['id']}/relationships/{user}",
               json={"relationship_type": "friend"})
    obj = client.post("/objections", json={
        "profile_id": p["id"], "objector_ref": "ref"}).json()

    resolved = client.post(f"/objections/{obj['id']}/resolve",
                           json={"outcome": "uphold"}).json()
    assert resolved["profile_status"] == "terminated"
    # Terminated: content erased, chat gone (410) even for a prior relationship.
    assert client.get(f"/profiles/{p['id']}").json()["status"] == "terminated"
    assert client.post(f"/profiles/{p['id']}/chat", json={
        "interactor_id": user, "message": "hello?"}).status_code == 410
    # A resolved objection cannot be resolved again.
    assert client.post(f"/objections/{obj['id']}/resolve",
                       json={"outcome": "dismiss"}).status_code == 409


def test_subject_can_withdraw_consent_and_force_termination(client):
    p = _third_party(client)
    obj = client.post("/objections", json={
        "profile_id": p["id"], "objector_ref": "ref"}).json()
    # The subject withdraws consent — honored immediately, mid-review.
    done = client.post(f"/objections/{obj['id']}/withdraw").json()
    assert done["status"] == "withdrawn"
    assert done["profile_status"] == "terminated"


def test_withdraw_rejected_for_non_subject_consent_basis(client):
    p = _third_party(client, consent={"basis": "public_figure_commentary",
                                      "attestor": "editorial desk"})
    obj = client.post("/objections", json={
        "profile_id": p["id"], "objector_ref": "ref"}).json()
    # Public-figure basis: no unilateral withdrawal — must go through review.
    assert client.post(
        f"/objections/{obj['id']}/withdraw").status_code == 409


def test_cannot_object_to_a_terminated_profile(client):
    p = _third_party(client)
    obj = client.post("/objections", json={
        "profile_id": p["id"], "objector_ref": "ref"}).json()
    client.post(f"/objections/{obj['id']}/withdraw")            # → terminated
    again = client.post("/objections", json={
        "profile_id": p["id"], "objector_ref": "ref2"})
    assert again.status_code == 409
