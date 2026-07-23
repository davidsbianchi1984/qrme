"""Robotic embodiment: catalog, binding, allowlisted commands, and identity
consistency across the physical body."""


def test_catalog_lists_all_platforms(client):
    cat = client.get("/robotics/catalog").json()
    models = {r["model"] for r in cat["robots"]}
    assert {"isaac_1", "neo", "u1_lite", "u1_pro", "u1_ultra", "memo",
            "saros_20", "saros_20_sonic", "qrevo_curv_2_flow"} <= models
    assert {"Weave Robotics", "1X Technologies", "UBTech Robotics",
            "Sunday Robotics", "Roborock"} <= set(cat["by_maker"])
    assert "fetch" in cat["commands"]["humanoid"]
    assert "fetch" not in cat["commands"]["vacuum"]


def test_bind_creates_an_embodiment(client, profile_id):
    r = client.post(f"/profiles/{profile_id}/robots",
                    json={"model": "neo", "name": "kitchen NEO"})
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["maker"] == "1X Technologies"
    assert body["kind"] == "humanoid"
    # Defaults to the profile's model preference ('auto' when unset).
    assert body["llm_provider"] == "auto"
    # The binding shows up as a normal embodiment, and the public identity
    # consistency view covers the robot body.
    forms = client.get(f"/profiles/{profile_id}/embodiments").json()
    assert any(f["name"] == "kitchen NEO" and f["kind"] == "humanoid"
               for f in forms)
    cons = client.get(f"/profiles/{profile_id}/embodiment-consistency").json()
    assert any(f["name"] == "kitchen NEO" for f in cons["embodiments"])


def test_bind_honors_an_explicit_llm_choice(client, profile_id):
    r = client.post(f"/profiles/{profile_id}/robots",
                    json={"model": "isaac_1", "llm_provider": "grok"})
    assert r.status_code == 201
    assert r.json()["llm_provider"] == "grok"


def test_non_llm_platform_refuses_a_provider(client, profile_id):
    r = client.post(f"/profiles/{profile_id}/robots",
                    json={"model": "qrevo_curv_2_flow", "llm_provider": "openai"})
    assert r.status_code == 422


def test_unknown_model_404s(client, profile_id):
    assert client.post(f"/profiles/{profile_id}/robots",
                       json={"model": "terminator"}).status_code == 404


def test_vacuum_cannot_fetch(client, profile_id):
    rob = client.post(f"/profiles/{profile_id}/robots",
                      json={"model": "saros_20"}).json()
    r = client.post(f"/robots/{rob['id']}/command",
                    json={"command": "fetch", "arg": "slippers"})
    assert r.status_code == 422
    ok = client.post(f"/robots/{rob['id']}/command",
                     json={"command": "clean", "arg": "kitchen"})
    assert ok.status_code == 201
    assert ok.json()["status"] == "queued"


def test_say_speaks_in_character_and_is_logged(client, profile_id):
    rob = client.post(f"/profiles/{profile_id}/robots",
                      json={"model": "neo"}).json()
    r = client.post(f"/robots/{rob['id']}/command",
                    json={"command": "say", "arg": "the garden this morning"})
    assert r.status_code == 201, r.text
    assert r.json()["status"] == "spoken"
    assert r.json()["spoken"]                    # the stub generated a line

    log = client.get(f"/robots/{rob['id']}/commands").json()
    assert [e["command"] for e in log] == ["say"]
    assert log[0]["result"]["status"] == "spoken"


def test_bind_and_command_require_owner(client, profile_id):
    rob = client.post(f"/profiles/{profile_id}/robots",
                      json={"model": "memo"}).json()
    client.headers.pop("authorization", None)
    assert client.post(f"/profiles/{profile_id}/robots",
                       json={"model": "neo"}).status_code in (401, 403)
    assert client.post(f"/robots/{rob['id']}/command",
                       json={"command": "tidy"}).status_code in (401, 403)


def test_unbind_removes_the_embodiment(client, profile_id):
    rob = client.post(f"/profiles/{profile_id}/robots",
                      json={"model": "u1_pro", "name": "hall U1"}).json()
    assert client.delete(f"/robots/{rob['id']}").json()["unbound"] is True
    forms = client.get(f"/profiles/{profile_id}/embodiments").json()
    assert not any(f["name"] == "hall U1" for f in forms)
