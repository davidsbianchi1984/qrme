"""Extensions to the objection/takedown flow: PDI-sealed audit trail, estate
revocation, and the interaction with memorial + succession states."""

from tests.test_capabilities import (ADULT, make_interactor, make_profile,
                                     pdi_pair)  # noqa: F401 — pytest fixture


def _third_party(client, basis="subject_consent", **extra):
    body = {"owner_id": "owner-1", "kind": "other_person",
            "display_name": "Real Person", "persona": "A public commentator.",
            "verification": ADULT,
            "consent": {"basis": basis, "attestor": "the standing party"}}
    body.update(extra)
    r = client.post("/profiles", json=body)
    assert r.status_code == 201, r.text
    out = r.json()
    client.headers["authorization"] = f"Bearer {out['owner_token']}"
    return out


# --- audit trail ---------------------------------------------------------- #

def test_lifecycle_writes_an_audit_trail(client):
    p = _third_party(client)
    obj = client.post("/objections", json={
        "profile_id": p["id"], "objector_ref": "ref",
        "reason": "that's me"}).json()
    client.post(f"/profiles/{p['id']}/objections/{obj['id']}/attest")
    client.post(f"/objections/{obj['id']}/resolve", json={"outcome": "dismiss"})

    audit = client.get(f"/objections/{obj['id']}/audit").json()
    events = [e["event"] for e in audit["events"]]
    assert events == ["opened", "reattested", "dismissed"]
    assert {e["actor"] for e in audit["events"]} == {"objector", "owner", "reviewer"}
    # No PDI configured in this test app, so nothing is vault-sealed.
    assert audit["vault_backed"] is False
    assert all(e["sealed"] is False for e in audit["events"])


def test_uphold_records_uphold_and_termination_events(client):
    p = _third_party(client)
    obj = client.post("/objections", json={
        "profile_id": p["id"], "objector_ref": "ref"}).json()
    client.post(f"/objections/{obj['id']}/resolve", json={"outcome": "uphold"})
    events = [e["event"] for e in
              client.get(f"/objections/{obj['id']}/audit").json()["events"]]
    assert events == ["opened", "upheld", "terminated"]


def test_audit_is_owner_or_reviewer_gated(client, monkeypatch):
    p = _third_party(client)
    obj = client.post("/objections", json={
        "profile_id": p["id"], "objector_ref": "ref"}).json()
    # With a reviewer role required (production posture), a request carrying
    # neither the owner token nor the reviewer token is refused; the owner's
    # own token still works.
    monkeypatch.setenv("QRME_ADMIN_TOKEN", "reviewer-secret")
    owner = dict(client.headers)
    client.headers.pop("authorization", None)
    assert client.get(f"/objections/{obj['id']}/audit").status_code in (401, 403)
    client.headers.update(owner)
    assert client.get(f"/objections/{obj['id']}/audit").status_code == 200


def test_events_are_sealed_into_the_pdi_vault(pdi_pair):
    client, fake = pdi_pair
    body = {"owner_id": "owner-1", "kind": "other_person",
            "display_name": "Real Person", "persona": "A commentator.",
            "verification": ADULT,
            "consent": {"basis": "subject_consent", "attestor": "subject"}}
    p = client.post("/profiles", json=body).json()
    client.headers["authorization"] = f"Bearer {p['owner_token']}"
    obj = client.post("/objections", json={
        "profile_id": p["id"], "objector_ref": "ref"}).json()

    audit = client.get(f"/objections/{obj['id']}/audit").json()
    assert audit["vault_backed"] is True
    opened = audit["events"][0]
    assert opened["sealed"] is True
    # The sealed copy is really in the vault under the reported key.
    assert opened["pdi_key"] in fake.store


# --- estate revocation ---------------------------------------------------- #

def test_estate_can_revoke_authorization(client):
    p = _third_party(client, basis="estate_authorization")
    obj = client.post("/objections", json={
        "profile_id": p["id"], "objector_ref": "estate-letter-9"}).json()
    done = client.post(f"/objections/{obj['id']}/revoke").json()
    assert done["status"] == "revoked"
    assert done["profile_status"] == "terminated"
    assert client.get(f"/profiles/{p['id']}").json()["status"] == "terminated"


def test_revoke_rejected_for_public_figure_basis(client):
    p = _third_party(client, basis="public_figure_commentary")
    obj = client.post("/objections", json={
        "profile_id": p["id"], "objector_ref": "ref"}).json()
    # Commentary has no consent/authorization to revoke — review only.
    assert client.post(f"/objections/{obj['id']}/revoke").status_code == 409


def test_subject_can_also_use_revoke(client):
    p = _third_party(client, basis="subject_consent")
    obj = client.post("/objections", json={
        "profile_id": p["id"], "objector_ref": "ref"}).json()
    assert client.post(f"/objections/{obj['id']}/revoke").json()["status"] == "revoked"


# --- memorial + succession interaction ------------------------------------ #

def test_memorial_can_be_objected_and_dismissal_restores_it(client):
    # A departed (memorial) third-party profile.
    p = _third_party(client, successor_owner=None)
    client.post(f"/profiles/{p['id']}/sunset")
    assert client.get(f"/profiles/{p['id']}").json()["status"] == "departed"

    obj = client.post("/objections", json={
        "profile_id": p["id"], "objector_ref": "estate"}).json()
    assert obj["profile_status"] == "restricted"
    assert obj["prior_status"] == "departed"
    # Memorial view is suspended while restricted.
    assert client.get(f"/profiles/{p['id']}/memorial").status_code == 409

    # Dismissed → the memorial is restored, not made active.
    r = client.post(f"/objections/{obj['id']}/resolve",
                    json={"outcome": "dismiss"}).json()
    assert r["profile_status"] == "departed"
    assert client.get(f"/profiles/{p['id']}/memorial").status_code == 200


def test_upholding_an_objection_on_a_memorial_tears_it_down(client):
    p = _third_party(client)
    client.post(f"/profiles/{p['id']}/sunset")
    obj = client.post("/objections", json={
        "profile_id": p["id"], "objector_ref": "estate"}).json()
    client.post(f"/objections/{obj['id']}/resolve", json={"outcome": "uphold"})
    assert client.get(f"/profiles/{p['id']}").json()["status"] == "terminated"
    assert client.get(f"/profiles/{p['id']}/memorial").status_code == 409


def test_open_objection_blocks_succession(client):
    # Named successor, but a live objection is in the way.
    p = make_profile(client, successor_owner="daughter-1")
    obj = client.post("/objections", json={
        "profile_id": p["id"], "objector_ref": "ref"}).json()
    blocked = client.post(f"/profiles/{p['id']}/succeed",
                          json={"verification_ref": "death-cert"})
    assert blocked.status_code == 409

    # Once dismissed, succession can proceed.
    client.post(f"/objections/{obj['id']}/resolve", json={"outcome": "dismiss"})
    ok = client.post(f"/profiles/{p['id']}/succeed",
                     json={"verification_ref": "death-cert"})
    assert ok.status_code == 200
