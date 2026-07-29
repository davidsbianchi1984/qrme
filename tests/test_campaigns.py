"""Crowdfunding with proceeds routed where the user said (spec [0020],
example two): designations that must sum to 100, campaigns that cannot
exist before a designation, donations that split onto the ledger, and the
whole thing continuing after the profile departs — which is the point.
"""

from __future__ import annotations


def _designate(client, profile_id, designees=None):
    r = client.put(f"/profiles/{profile_id}/proceeds", json={
        "designees": designees or [
            {"name": "June Bianchi", "kind": "loved_one", "share": 60,
             "account_id": "acct-june"},
            {"name": "The Trail Fund", "kind": "organization", "share": 40},
        ]})
    assert r.status_code == 200, r.text
    return r.json()


def _campaign(client, profile_id, title="Keep the garden going"):
    r = client.post(f"/profiles/{profile_id}/campaigns",
                    json={"title": title, "goal": 1000.0,
                          "cause": "the garden he kept"})
    assert r.status_code == 201, r.text
    return r.json()


def test_shares_must_sum_to_exactly_100(client, profile_id):
    r = client.put(f"/profiles/{profile_id}/proceeds", json={
        "designees": [{"name": "A", "kind": "loved_one", "share": 60},
                      {"name": "B", "kind": "organization", "share": 39}]})
    assert r.status_code == 422
    assert "100" in r.json()["detail"]


def test_no_campaign_before_a_designation(client, profile_id):
    r = client.post(f"/profiles/{profile_id}/campaigns",
                    json={"title": "x", "goal": 100.0})
    assert r.status_code == 422
    assert "where the money goes" in r.json()["detail"]


def test_a_donation_splits_onto_the_ledger_by_share(client, profile_id):
    _designate(client, profile_id)
    campaign = _campaign(client, profile_id)
    r = client.post(f"/campaigns/{campaign['id']}/donate",
                    json={"amount": 100.0, "on_behalf_of": "Wild West Films"})
    assert r.status_code == 201, r.text
    split = {s["name"]: s["amount"] for s in r.json()["split"]}
    assert split == {"June Bianchi": 60.0, "The Trail Fund": 40.0}
    # June has a platform account: her cut is on her own statement.
    from qrme import ledger
    june = ledger.statement("acct-june")
    assert june["totals"]["accrued"] == 60.0
    # The card shows progress and, always, where the money goes.
    card = client.get(f"/campaigns/{campaign['id']}").json()
    assert card["raised"] == 100.0 and card["donors"] == 1
    assert [p["name"] for p in card["proceeds_to"]] == [
        "June Bianchi", "The Trail Fund"]


def test_odd_cents_still_add_up(client, profile_id):
    _designate(client, profile_id, [
        {"name": "A", "kind": "loved_one", "share": 33},
        {"name": "B", "kind": "loved_one", "share": 33},
        {"name": "C", "kind": "loved_one", "share": 34}])
    campaign = _campaign(client, profile_id)
    r = client.post(f"/campaigns/{campaign['id']}/donate",
                    json={"amount": 0.05})
    parts = [s["amount"] for s in r.json()["split"]]
    assert round(sum(parts), 2) == 0.05


def test_donations_keep_flowing_after_departure(client, profile_id):
    """Sunset is the living owner's own act — donations continue and the
    owner keeps the pen on where they go."""
    _designate(client, profile_id)
    campaign = _campaign(client, profile_id)
    r = client.post(f"/profiles/{profile_id}/sunset")
    assert r.status_code == 200, r.text
    give = client.post(f"/campaigns/{campaign['id']}/donate",
                       json={"amount": 25.0})
    assert give.status_code == 201, give.text


def test_succession_hands_the_pen_to_the_chosen_person(client):
    """Verified owner death: the old token dies with /succeed, so the
    departed owner's designation can only be amended by their successor —
    'leave it in good hands', enforced by the token lifecycle."""
    r = client.post("/profiles", json={
        "owner_id": "owner-s", "kind": "self", "display_name": "Grandpa",
        "persona": "the actor", "successor_owner": "acct-june", "plan": "pro",
        "verification": {"birthdate": "1944-06-01"}})
    assert r.status_code == 201, r.text
    pid = r.json()["id"]
    client.headers["authorization"] = f"Bearer {r.json()['owner_token']}"
    _designate(client, pid)
    campaign = _campaign(client, pid)
    handed = client.post(f"/profiles/{pid}/succeed",
                         json={"verification_ref": "death-cert-001"}).json()
    assert handed["succeeded"] is True
    # The old pen is dead; donations still flow to the designated names.
    locked = client.put(f"/profiles/{pid}/proceeds", json={
        "designees": [{"name": "Somebody Else", "kind": "loved_one",
                       "share": 100}]})
    assert locked.status_code in (401, 403)
    give = client.post(f"/campaigns/{campaign['id']}/donate",
                       json={"amount": 10.0})
    assert give.status_code == 201, give.text


def test_rated_profiles_get_no_campaign(client):
    r = client.post("/profiles", json={
        "owner_id": "owner-r", "kind": "self", "display_name": "After Dark",
        "persona": "rated", "adult_mode": True, "plan": "pro",
        "verification": {"birthdate": "1984-06-01"}})
    assert r.status_code == 201, r.text
    client.headers["authorization"] = f"Bearer {r.json()['owner_token']}"
    pid = r.json()["id"]
    _designate(client, pid)
    refused = client.post(f"/profiles/{pid}/campaigns",
                          json={"title": "x", "goal": 10.0})
    assert refused.status_code == 422
    assert "rated" in refused.json()["detail"]


def test_the_cap_and_the_close(client, profile_id):
    _designate(client, profile_id)
    campaign = _campaign(client, profile_id)
    too_big = client.post(f"/campaigns/{campaign['id']}/donate",
                          json={"amount": 500.01})
    assert too_big.status_code == 422
    closed = client.post(f"/campaigns/{campaign['id']}/close")
    assert closed.status_code == 200
    after = client.post(f"/campaigns/{campaign['id']}/donate",
                        json={"amount": 5.0})
    assert after.status_code == 422
    assert "closed" in after.json()["detail"]
