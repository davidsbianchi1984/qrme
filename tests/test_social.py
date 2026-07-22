"""Social-platform connections: collect (build the profile) and publish
(run it on the platform, reachable by QR beacon)."""


def _connect(client, profile_id, **body):
    r = client.post(f"/profiles/{profile_id}/social", json=body)
    assert r.status_code == 201, r.text
    return r.json()


def test_collect_builds_the_profile(client, profile_id):
    conn = _connect(client, profile_id, platform="instagram",
                    direction="collect", handle="@dana.grows", scope=["posts"])
    assert conn["direction"] == "collect"
    assert conn["handle"] == "@dana.grows"
    assert conn["beacon"] is None            # collect connections have no beacon

    r = client.post(f"/social/{conn['id']}/collect", json={"items": [
        {"content": "Tomatoes are in — finally.", "title": "post"},
        {"content": "Compost tea is the secret."},
    ]})
    assert r.status_code == 201, r.text
    out = r.json()
    assert out["ingested"] == 2
    assert out["total_sources"] >= 2

    # The collected items are now source material the profile is built from.
    sources = client.get(f"/profiles/{profile_id}/sources").json()
    kinds = [s["kind"] for s in sources]
    assert kinds.count("social_post") == 2

    # And the connection remembers how much it has pulled in.
    listed = client.get(f"/profiles/{profile_id}/social").json()
    assert listed[0]["collected"] == 2


def test_publish_runs_on_the_platform(client, profile_id):
    conn = _connect(client, profile_id, platform="x", direction="publish",
                    handle="dana")
    assert conn["beacon"] == f"/social/{conn['id']}/beacon"

    r = client.post(f"/social/{conn['id']}/publish",
                    json={"content": "Fresh basil, fresh takes.", "topic": "garden"})
    assert r.status_code == 201, r.text
    post = r.json()
    assert post["status"] == "approved"
    assert post["surface"] == "social:x"
    assert post["content"] == "Fresh basil, fresh takes."

    assert client.get(f"/profiles/{profile_id}/social").json()[0]["published"] == 1


def test_publish_is_moderated(client, profile_id):
    conn = _connect(client, profile_id, platform="reddit", direction="publish")
    r = client.post(f"/social/{conn['id']}/publish",
                    json={"content": "here is my ssn 123-45-6789"})
    assert r.status_code == 201, r.text
    post = r.json()
    assert post["status"] == "rejected"
    assert post["flag_reason"]
    assert post["content"] is None
    # A rejected post does not count as published.
    assert client.get(f"/profiles/{profile_id}/social").json()[0]["published"] == 0


def test_beacon_and_qr(client, profile_id):
    conn = _connect(client, profile_id, platform="tiktok", direction="publish",
                    handle="dana.grows")
    beacon = client.get(f"/social/{conn['id']}/beacon").json()
    assert beacon["presence_url"] == "https://tiktok.com/@dana.grows"
    assert beacon["qr_svg"] == f"/social/{conn['id']}/qr.svg"

    qr = client.get(f"/social/{conn['id']}/qr.svg")
    assert qr.status_code == 200
    assert qr.headers["content-type"] == "image/svg+xml"
    assert b"<svg" in qr.content


def test_direction_guards(client, profile_id):
    collect = _connect(client, profile_id, platform="facebook", direction="collect")
    publish = _connect(client, profile_id, platform="linkedin", direction="publish")

    # Wrong direction is refused both ways.
    assert client.post(f"/social/{collect['id']}/publish",
                       json={"content": "hi"}).status_code == 409
    assert client.post(f"/social/{publish['id']}/collect",
                       json={"items": [{"content": "x"}]}).status_code == 409
    # Beacons only exist for publish connections.
    assert client.get(f"/social/{collect['id']}/beacon").status_code == 409


def test_revoke_stops_collection(client, profile_id):
    conn = _connect(client, profile_id, platform="threads", direction="collect")
    assert client.delete(f"/social/{conn['id']}").json()["status"] == "revoked"
    r = client.post(f"/social/{conn['id']}/collect", json={"items": [{"content": "x"}]})
    assert r.status_code == 409


def test_publish_registers_a_surface(client, profile_id):
    conn = _connect(client, profile_id, platform="youtube", direction="publish")
    surfaces = client.get(f"/profiles/{profile_id}/surfaces").json()["surfaces"]
    assert "social:youtube" in surfaces
    # Revoking the only publisher retires the surface.
    client.delete(f"/social/{conn['id']}")
    surfaces = client.get(f"/profiles/{profile_id}/surfaces").json()["surfaces"]
    assert "social:youtube" not in surfaces
