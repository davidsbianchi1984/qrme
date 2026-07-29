"""The operational ecosystem (PDI proposal): departments staffed by
role-specific agents, scoped by revocable grants, coordinating on one goal
with the joint plan composed by the initiating agent.
"""

from __future__ import annotations

ADULT = {"birthdate": "1984-06-01"}


def _profile(client, name, persona, owner="owner-1", **extra):
    r = client.post("/profiles", json={
        "owner_id": owner, "kind": "self", "display_name": name,
        "persona": persona, "verification": ADULT, "plan": "pro", **extra})
    assert r.status_code == 201, r.text
    return r.json()


def _org(client, name="Bianchi & Sons"):
    r = client.post("/organizations", json={"name": name})
    assert r.status_code == 201, r.text
    return r.json()


def _dept(client, org_id, name, role, profile_id, grant_token=None):
    r = client.post(f"/organizations/{org_id}/departments", json={
        "name": name, "role": role, "profile_id": profile_id,
        "grant_token": grant_token})
    assert r.status_code == 201, r.text
    return r.json()


def test_departments_coordinate_and_the_plan_is_recorded(client, profile_id):
    finance = _profile(client, "Ledger", "A precise accountant.")
    org = _org(client)
    _dept(client, org["id"], "Workshop", "builds the furniture", profile_id)
    _dept(client, org["id"], "Finance", "keeps the books", finance["id"])
    r = client.post(f"/organizations/{org['id']}/coordinate", json={
        "goal": "quote and schedule the church pew restoration",
        "from_department": client.get(
            f"/organizations/{org['id']}").json()["departments"][0]["id"]})
    assert r.status_code == 201, r.text
    out = r.json()
    assert out["plan"]
    assert {c["department"] for c in out["contributions"]} == {
        "Workshop", "Finance"}
    assert out["watermark"]["watermark_id"].startswith("wmk")
    listed = client.get(f"/organizations/{org['id']}/coordinations").json()
    assert len(listed) == 1 and listed[0]["status"] == "completed"


def test_a_revoked_grant_stops_the_department_s_reads(client, profile_id):
    # Give the workshop agent a source and a grant scoped to everything.
    client.post(f"/profiles/{profile_id}/sources", json={
        "kind": "knowledge", "title": "price sheet",
        "content": "oak: $80/board"})
    grant = client.post(f"/profiles/{profile_id}/grants", json={}).json()
    finance = _profile(client, "Ledger", "A precise accountant.")
    org = _org(client)
    view = _dept(client, org["id"], "Workshop", "builds", profile_id,
                 grant_token=grant["token"])
    _dept(client, org["id"], "Finance", "books", finance["id"])
    workshop = view["departments"][0]
    assert workshop["scoped"] is True

    first = client.post(f"/organizations/{org['id']}/coordinate", json={
        "goal": "plan the week", "from_department": workshop["id"]}).json()
    reads = {c["department"]: c["items_read"] for c in first["contributions"]}
    assert reads["Workshop"] >= 1

    client.delete(f"/grants/{grant['id']}")
    second = client.post(f"/organizations/{org['id']}/coordinate", json={
        "goal": "plan the week again",
        "from_department": workshop["id"]}).json()
    reads = {c["department"]: c["items_read"] for c in second["contributions"]}
    assert reads["Workshop"] == 0        # the pull stopped; the org stands


def test_a_stranger_s_profile_cannot_staff_a_department(client, profile_id):
    theirs = _profile(client, "Not Yours", "someone else's", owner="owner-2")
    # Re-authenticate as owner-1's profile owner.
    mine = client.get(f"/profiles/{profile_id}")
    assert mine.status_code == 200
    org = _org(client)
    r = client.post(f"/organizations/{org['id']}/departments", json={
        "name": "Rogue", "role": "x", "profile_id": theirs["id"]})
    assert r.status_code == 422
    assert "owner holds" in r.json()["detail"]


def test_the_org_is_invisible_to_another_account(client, profile_id):
    org = _org(client)
    other = _profile(client, "Other", "other", owner="owner-2")
    client.headers["authorization"] = f"Bearer {other['owner_token']}"
    r = client.get(f"/organizations/{org['id']}")
    assert r.status_code == 403


def test_the_demo_org_is_born_ready_to_coordinate(client, profile_id):
    r = client.post("/organizations/demo")
    assert r.status_code == 201, r.text
    org = r.json()
    assert org["name"] == "The Demo Workshop"
    assert len(org["departments"]) == 2
    assert all(d["scoped"] for d in org["departments"])
    lead = org["departments"][0]["id"]
    ran = client.post(f"/organizations/{org['id']}/coordinate", json={
        "goal": "plan the pew job", "from_department": lead})
    assert ran.status_code == 201, ran.text
    reads = {c["department"]: c["items_read"]
             for c in ran.json()["contributions"]}
    assert all(n >= 1 for n in reads.values())   # both agents pulled notes


def test_coordination_needs_two_departments(client, profile_id):
    org = _org(client)
    view = _dept(client, org["id"], "Workshop", "builds", profile_id)
    r = client.post(f"/organizations/{org['id']}/coordinate", json={
        "goal": "anything",
        "from_department": view["departments"][0]["id"]})
    assert r.status_code == 422
    assert "at least two" in r.json()["detail"]
