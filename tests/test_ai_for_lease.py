"""AI for lease: an organization seats somebody else's licensed specialist.

The commercial model the Private Data Infrastructure proposal describes,
with behavior: the specialist must be offered for license, the lease fee
accrues to its owner at seating time, the leased desk contributes to
coordinations like any department — and the owner's hand stays on the
switch: revoking the lease leaves the department standing but silent,
named in every plan it no longer speaks in.
"""

from tests.test_capabilities import as_owner, make_profile


def _specialist(client, persona="A veteran fleet-dispatch optimizer."):
    """Somebody else's profile, offered for license. Returns (profile, its
    owner token)."""
    p = make_profile(client, persona=persona, owner_id="specialist-owner")
    as_owner(client, p)
    client.put(f"/profiles/{p['id']}/license",
               json={"kind": "consult", "price": 75})
    client.post(f"/profiles/{p['id']}/sources", json={
        "kind": "knowledge", "title": "headways",
        "content": "Short headways beat big buses on crowded corridors."})
    return p, client.headers["authorization"]


def _org(client):
    """A second account with an organization and one staffed department.
    Leaves the client authenticated as the org's owner."""
    mine = make_profile(client, persona="An operations lead.",
                        owner_id="metro-owner")
    as_owner(client, mine)
    org = client.post("/organizations", json={"name": "Houston Metro"}).json()
    client.post(f"/organizations/{org['id']}/departments", json={
        "name": "Dispatch", "role": "runs the day-to-day board",
        "profile_id": mine["id"]})
    return org, mine


def test_an_org_leases_a_specialist_and_the_owner_is_paid(client):
    spec, owner_auth = _specialist(client)
    org, _ = _org(client)

    r = client.post(f"/organizations/{org['id']}/lease", json={
        "profile_id": spec["id"], "name": "Route Planning",
        "role": "advises on corridor design"})
    assert r.status_code == 201, r.text
    lease = r.json()
    assert lease["lease_id"].startswith("lse")
    depts = {d["name"]: d for d in lease["org"]["departments"]}
    assert depts["Route Planning"]["leased"] is True
    assert depts["Route Planning"]["lease_revoked"] is False
    assert depts["Dispatch"]["leased"] is False

    # The fee accrued to the specialist's owner at seating time.
    client.headers["authorization"] = owner_auth
    earnings = client.get(f"/profiles/{spec['id']}/earnings").json()
    assert any(e["kind"] == "lease_fee" and e["amount"] == 75
               for e in earnings["entries"])
    # And the owner sees the lease on their licenses list, named to the org.
    grants = client.get(f"/profiles/{spec['id']}/licenses").json()
    lease_rows = [g for g in grants if g["kind"] == "lease"]
    assert lease_rows and lease_rows[0]["buyer_id"] == "Houston Metro"


def test_the_leased_desk_speaks_in_coordinations_until_revoked(client):
    spec, owner_auth = _specialist(client)
    org, mine = _org(client)
    lease = client.post(f"/organizations/{org['id']}/lease", json={
        "profile_id": spec["id"], "name": "Route Planning",
        "role": "advises on corridor design"}).json()
    dispatch = next(d for d in lease["org"]["departments"]
                    if d["name"] == "Dispatch")

    run = client.post(f"/organizations/{org['id']}/coordinate", json={
        "goal": "cut peak-hour bunching on line 82",
        "from_department": dispatch["id"]}).json()
    assert {c["department"] for c in run["contributions"]} == {
        "Dispatch", "Route Planning"}
    assert run["silenced"] == []

    # The specialist's owner pulls the switch.
    client.headers["authorization"] = owner_auth
    assert client.delete(f"/licenses/{lease['lease_id']}").json()["revoked"]

    as_org_owner = {"authorization": f"Bearer {mine['owner_token']}"}
    run = client.post(f"/organizations/{org['id']}/coordinate", json={
        "goal": "same goal, after revocation",
        "from_department": dispatch["id"]}, headers=as_org_owner).json()
    assert {c["department"] for c in run["contributions"]} == {"Dispatch"}
    assert run["silenced"] == [{"department_id": next(
        d["id"] for d in lease["org"]["departments"]
        if d["name"] == "Route Planning"),
        "department": "Route Planning", "profile_status": "lease_revoked"}]
    # The org view says so too.
    view = client.get(f"/organizations/{org['id']}",
                      headers=as_org_owner).json()
    leased = next(d for d in view["departments"]
                  if d["name"] == "Route Planning")
    assert leased["lease_revoked"] is True


def test_a_lease_needs_an_offer_and_a_stranger(client):
    # Unoffered: nothing to lease under.
    unoffered = make_profile(client, persona="Keeps their counsel.")
    org, mine = _org(client)
    r = client.post(f"/organizations/{org['id']}/lease", json={
        "profile_id": unoffered["id"], "name": "X", "role": "y"})
    assert r.status_code == 422 and "not offered" in r.json()["detail"]

    # The org's own profile is staffing, not leasing.
    r = client.post(f"/organizations/{org['id']}/lease", json={
        "profile_id": mine["id"], "name": "X", "role": "y"})
    assert r.status_code == 422 and "organization's own" in r.json()["detail"]
