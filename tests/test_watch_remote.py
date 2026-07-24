"""The watch: a wrist extension and remote. Green = working, orange =
needing assistance, red = stopped — and every remote action reuses the
same paths (and the same auth and allowlists) the full apps use."""

ADULT = {"birthdate": "1984-06-01"}


def _profile(client, moderation_mode="auto"):
    r = client.post("/profiles", json={
        "owner_id": "owner-1", "kind": "fictional", "display_name": "Ava",
        "persona": "A helpful studio persona.",
        "moderation_mode": moderation_mode, "verification": ADULT})
    out = r.json()
    client.headers["authorization"] = f"Bearer {out['owner_token']}"
    return out["id"]


def test_agent_lights_follow_the_workflow_lifecycle(client):
    pid = _profile(client)
    wf = client.post(f"/profiles/{pid}/workflows",
                     json={"goal": "ship the notes",
                           "plan": ["draft", "confirm"]}).json()

    face = client.get(f"/profiles/{pid}/watch").json()
    agent = face["agents"][0]
    assert agent["light"] == "green" and agent["status"] == "running"
    assert face["summary"]["working"] == 1 and face["haptic"] is None

    # draft runs; confirm pauses the agent — the wrist shows orange and taps.
    client.post(f"/profiles/{pid}/watch/act",
                json={"target": "workflow", "id": wf["id"],
                      "action": "advance"})
    client.post(f"/profiles/{pid}/watch/act",
                json={"target": "workflow", "id": wf["id"],
                      "action": "advance"})
    face = client.get(f"/profiles/{pid}/watch").json()
    agent = face["agents"][0]
    assert agent["light"] == "orange" and agent["awaiting"]
    assert face["summary"]["needing_assistance"] == 1
    assert face["haptic"] == "alert"

    # Assist from the wrist needs the asked-for input.
    r = client.post(f"/profiles/{pid}/watch/act",
                    json={"target": "workflow", "id": wf["id"],
                          "action": "assist"})
    assert r.status_code == 422
    r = client.post(f"/profiles/{pid}/watch/act",
                    json={"target": "workflow", "id": wf["id"],
                          "action": "assist", "input": "client accepted"})
    assert r.status_code == 201
    face = client.get(f"/profiles/{pid}/watch").json()
    assert face["agents"][0]["light"] == "done"

    # A cancelled agent goes red — stopped, visible at a glance.
    wf2 = client.post(f"/profiles/{pid}/workflows",
                      json={"goal": "second job", "plan": ["draft"]}).json()
    client.post(f"/profiles/{pid}/watch/act",
                json={"target": "workflow", "id": wf2["id"],
                      "action": "cancel"})
    face = client.get(f"/profiles/{pid}/watch").json()
    lights = {a["id"]: a["light"] for a in face["agents"]}
    assert lights[wf2["id"]] == "red"
    assert face["summary"]["stopped"] == 1 and face["haptic"] == "alert"


def test_robot_remote_ring_and_learned_tasks(client):
    pid = _profile(client)
    robot = client.post(f"/profiles/{pid}/robots",
                        json={"model": "neo"}).json()

    face = client.get(f"/profiles/{pid}/watch").json()
    wrist_robot = face["robots"][0]
    assert wrist_robot["light"] == "idle"          # docked
    assert wrist_robot["quick_commands"] == ["come_here", "patrol",
                                             "dock", "stop"]

    # Quick ring from the wrist: activate, then dock again.
    r = client.post(f"/profiles/{pid}/watch/act",
                    json={"target": "robot", "id": robot["id"],
                          "action": "come_here"})
    assert r.status_code == 201
    assert r.json()["result"]["status"] == "queued"
    assert client.get(f"/profiles/{pid}/watch"
                      ).json()["robots"][0]["light"] == "green"
    client.post(f"/profiles/{pid}/watch/act",
                json={"target": "robot", "id": robot["id"],
                      "action": "dock"})
    assert client.get(f"/profiles/{pid}/watch"
                      ).json()["robots"][0]["light"] == "idle"

    # Learned task-pack verbs surface on the wrist and run through the
    # same allowlist; unknown verbs are refused there too.
    client.post("/packs/seed")
    pack = client.get("/packs", params={"industry": "household",
                                        "audience": "robot"}).json()[0]
    client.post(f"/packs/{pack['id']}/install",
                json={"profile_id": pid, "robot_id": robot["id"]})
    face = client.get(f"/profiles/{pid}/watch").json()
    assert "sort_laundry" in face["robots"][0]["learned_tasks"]
    r = client.post(f"/profiles/{pid}/watch/act",
                    json={"target": "robot", "id": robot["id"],
                          "action": "sort_laundry"})
    assert r.status_code == 201
    assert r.json()["result"]["skill"] == "Sort laundry"
    assert client.post(f"/profiles/{pid}/watch/act",
                       json={"target": "robot", "id": robot["id"],
                             "action": "juggle"}).status_code == 422


def test_pending_approval_turns_the_profile_chip_orange(client):
    pid = _profile(client, moderation_mode="manual")
    interactor = client.post("/interactors", json={
        "display_name": "Sam", "birthdate": "1995-01-01"}).json()["id"]
    client.post(f"/profiles/{pid}/chat",
                json={"interactor_id": interactor, "message": "hello"})

    face = client.get(f"/profiles/{pid}/watch").json()
    assert face["profile"]["light"] == "orange"
    assert face["profile"]["pending_approvals"] == 1
    assert face["haptic"] == "alert"

    from qrme import db
    msg_id = db.connect().execute(
        "SELECT id FROM messages WHERE profile_id=? AND status='pending'",
        (pid,)).fetchone()["id"]
    r = client.post(f"/profiles/{pid}/watch/act",
                    json={"target": "approval", "id": msg_id,
                          "action": "approve"})
    assert r.status_code == 201
    face = client.get(f"/profiles/{pid}/watch").json()
    assert face["profile"]["light"] == "green"
    assert face["profile"]["pending_approvals"] == 0
    assert face["haptic"] is None


def test_watch_is_owner_only(client, profile_id):
    r = client.get(f"/profiles/{profile_id}/watch",
                   headers={"authorization": ""})
    assert r.status_code in (401, 403)