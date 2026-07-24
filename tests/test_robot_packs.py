"""Robot task packs: marketplace expertise for the bodies profiles embody.
Installing a pack teaches a bound robot new commandable tasks — capability-
checked at install, allowlisted and audited like built-in commands."""

from qrme.packs import ROBOT_PACKS


def _bind(client, profile_id, model="neo"):
    r = client.post(f"/profiles/{profile_id}/robots", json={"model": model})
    assert r.status_code == 201, r.text
    return r.json()["id"]


def _pack(client, industry):
    rows = client.get("/packs", params={"industry": industry,
                                        "audience": "robot"}).json()
    assert len(rows) == 1
    return rows[0]


def test_robot_pack_teaches_commandable_tasks(client, profile_id):
    client.post("/packs/seed")
    robot_id = _bind(client, profile_id)          # NEO: humanoid

    # Before the pack, the task is not a permitted command.
    r = client.post(f"/robots/{robot_id}/command",
                    json={"command": "sort_laundry"})
    assert r.status_code == 422

    pack = _pack(client, "household")
    r = client.post(f"/packs/{pack['id']}/install",
                    json={"profile_id": profile_id, "robot_id": robot_id})
    assert r.status_code == 201, r.text
    assert set(r.json()["installed_tasks"]) == {
        "sort_laundry", "water_plants", "set_table"}

    skills = client.get(f"/robots/{robot_id}/skills").json()
    assert {s["task"] for s in skills} == {
        "sort_laundry", "water_plants", "set_table"}
    assert all(s["pack_title"] == "Household Tasks Pack" for s in skills)

    # The learned task is now commandable, carries its procedure, and lands
    # in the audit trail like any built-in command.
    r = client.post(f"/robots/{robot_id}/command",
                    json={"command": "sort_laundry"})
    assert r.status_code == 201, r.text
    out = r.json()
    assert out["status"] == "queued" and out["skill"] == "Sort laundry"
    assert "ask-first" in out["procedure"]
    log = client.get(f"/robots/{robot_id}/commands").json()
    assert log[-1]["command"] == "sort_laundry"

    # Unknown verbs are still refused — packs extend, never open, the gate.
    assert client.post(f"/robots/{robot_id}/command",
                       json={"command": "juggle"}).status_code == 422


def test_capability_check_protects_the_wrong_body(client, profile_id):
    client.post("/packs/seed")
    vacuum = _bind(client, profile_id, model="saros_20")
    household = _pack(client, "household")
    # A vacuum has no manipulation: the pack is refused, nothing installs.
    r = client.post(f"/packs/{household['id']}/install",
                    json={"profile_id": profile_id, "robot_id": vacuum})
    assert r.status_code == 422
    assert "manipulation" in r.json()["detail"]
    assert client.get(f"/robots/{vacuum}/skills").json() == []

    # The sentry pack fits a camera-patrol vacuum.
    sentry = _pack(client, "safety")
    r = client.post(f"/packs/{sentry['id']}/install",
                    json={"profile_id": profile_id, "robot_id": vacuum})
    assert r.status_code == 201, r.text
    r = client.post(f"/robots/{vacuum}/command",
                    json={"command": "hazard_scan"})
    assert r.status_code == 201
    assert "never attempt to intervene" in r.json()["procedure"]


def test_priced_robot_pack_requires_purchase_consent(client, profile_id):
    client.post("/packs/seed")
    robot_id = _bind(client, profile_id)
    culinary = _pack(client, "culinary")
    assert culinary["free"] is False
    r = client.post(f"/packs/{culinary['id']}/install",
                    json={"profile_id": profile_id, "robot_id": robot_id})
    assert r.status_code == 402
    r = client.post(f"/packs/{culinary['id']}/install",
                    json={"profile_id": profile_id, "robot_id": robot_id,
                          "accept_price": True})
    assert r.status_code == 201
    assert r.json()["price_paid"] == ROBOT_PACKS["culinary"][1]
    installed = client.get(f"/profiles/{profile_id}/packs").json()
    assert installed[0]["robot_id"] == robot_id


def test_audience_routing_is_strict(client, profile_id):
    client.post("/packs/seed")
    robot_id = _bind(client, profile_id)
    # Robot pack without a robot → told to pass one.
    sentry = _pack(client, "safety")
    r = client.post(f"/packs/{sentry['id']}/install",
                    json={"profile_id": profile_id})
    assert r.status_code == 422 and "robot_id" in r.json()["detail"]
    # Profile knowledge pack aimed at a robot → refused.
    knowledge = client.get("/packs", params={"industry": "finance"}).json()[0]
    r = client.post(f"/packs/{knowledge['id']}/install",
                    json={"profile_id": profile_id, "robot_id": robot_id})
    assert r.status_code == 422 and "omit robot_id" in r.json()["detail"]
    # A robot that isn't this profile's → not found.
    r = client.post(f"/packs/{sentry['id']}/install",
                    json={"profile_id": profile_id, "robot_id": "rob_ghost"})
    assert r.status_code == 404


def test_uninstall_revokes_the_tasks(client, profile_id):
    client.post("/packs/seed")
    robot_id = _bind(client, profile_id)
    pack = _pack(client, "care")
    client.post(f"/packs/{pack['id']}/install",
                json={"profile_id": profile_id, "robot_id": robot_id})
    assert client.post(f"/robots/{robot_id}/command",
                       json={"command": "comfort_checkin"}).status_code == 201
    r = client.delete(f"/robots/{robot_id}/packs/{pack['id']}")
    assert r.status_code == 200 and r.json()["removed_tasks"] == 3
    # Revoked immediately: the verb is no longer commandable.
    assert client.post(f"/robots/{robot_id}/command",
                       json={"command": "comfort_checkin"}).status_code == 422
    assert client.get(f"/robots/{robot_id}/skills").json() == []
    # Double install after uninstall works again (fresh purchase).
    assert client.post(f"/packs/{pack['id']}/install",
                       json={"profile_id": profile_id,
                             "robot_id": robot_id}).status_code == 201


def test_care_pack_keeps_its_safety_lines():
    _, _, tasks = ROBOT_PACKS["care"]
    by_task = {task: procedure for task, _, _, procedure in tasks}
    assert "never dispense" in by_task["medication_reminder"]
    assert "never physical support" in by_task["escort_walk"]
    assert "never a substitute for human contact" in by_task["comfort_checkin"]
