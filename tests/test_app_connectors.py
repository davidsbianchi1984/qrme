"""Connected-app connectors: a profile connects a catalog app and its agents
collect context, act, or produce through it."""


def _connect(client, profile_id, **body):
    r = client.post(f"/profiles/{profile_id}/apps", json=body)
    assert r.status_code == 201, r.text
    return r.json()


def test_connect_grants_catalog_capabilities(client, profile_id):
    conn = _connect(client, profile_id, provider="apple", app="photos")
    assert conn["provider"] == "apple"
    assert "semantic-search" in conn["capabilities"]   # granted all by default
    assert "collect" in conn["directions"]
    assert client.get(f"/profiles/{profile_id}/apps").json()[0]["id"] == conn["id"]


def test_unknown_app_and_capability_refused(client, profile_id):
    assert client.post(f"/profiles/{profile_id}/apps",
                       json={"provider": "apple", "app": "spaceship"}).status_code == 404
    assert client.post(f"/profiles/{profile_id}/apps",
                       json={"provider": "apple", "app": "photos",
                             "capabilities": ["mind-reading"]}).status_code == 422


def test_collect_builds_the_profile(client, profile_id):
    conn = _connect(client, profile_id, provider="apple", app="photos",
                    capabilities=["semantic-search"])
    r = client.post(f"/apps/{conn['id']}/collect", json={"items": [
        {"content": "Niece's birthday party photos", "title": "album"},
        {"content": "Beach trip, July"},
    ]})
    assert r.status_code == 201, r.text
    assert r.json()["ingested"] == 2
    sources = client.get(f"/profiles/{profile_id}/sources").json()
    assert sum(1 for s in sources if s["kind"] == "linked_account") == 2
    assert client.get(f"/profiles/{profile_id}/apps").json()[0]["collected"] == 2


def test_invoke_a_granted_capability(client, profile_id):
    conn = _connect(client, profile_id, provider="canva", app="magic_studio")
    r = client.post(f"/apps/{conn['id']}/invoke",
                    json={"capability": "magic-design", "input": "a birthday poster"})
    assert r.status_code == 201, r.text
    out = r.json()
    assert out["status"] == "performed"
    assert out["capability"] == "magic-design"
    assert client.get(f"/profiles/{profile_id}/apps").json()[0]["actions"] == 1

    # A capability the connector wasn't granted is refused.
    conn2 = _connect(client, profile_id, provider="apple", app="shortcuts",
                     capabilities=["intelligent-actions"])
    assert client.post(f"/apps/{conn2['id']}/invoke",
                       json={"capability": "on-device-model"}).status_code == 422


def test_collect_requires_collect_direction(client, profile_id):
    # Paint only produces — it can't collect context.
    conn = _connect(client, profile_id, provider="microsoft", app="paint")
    assert client.post(f"/apps/{conn['id']}/collect",
                       json={"items": [{"content": "x"}]}).status_code == 409


def test_revoke_stops_use(client, profile_id):
    conn = _connect(client, profile_id, provider="google", app="gmail")
    assert client.delete(f"/apps/{conn['id']}").json()["status"] == "revoked"
    assert client.post(f"/apps/{conn['id']}/collect",
                       json={"items": [{"content": "x"}]}).status_code == 409
    assert client.post(f"/apps/{conn['id']}/invoke",
                       json={"capability": "summaries"}).status_code == 409
