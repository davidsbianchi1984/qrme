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


class _Vault:
    """Enough of a PDI client to hold a credential."""

    def __init__(self):
        self.kept = {}

    def put(self, key, value):
        self.kept[key] = value


def _authorized(client, profile_id, **body):
    """A connector with its credential given, ready to reach the far side."""
    client.app.state.pdi = _Vault()
    conn = _connect(client, profile_id, **body)
    r = client.post(f"/apps/{conn['id']}/authorize", json={"secret": "s3cr3t"})
    assert r.status_code == 200, r.text
    return r.json()


def test_invoke_a_granted_capability(client, profile_id):
    conn = _authorized(client, profile_id, provider="canva", app="magic_studio")
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


# -- the lock is a posture, not a picture -------------------------------------

def test_invoking_a_connector_nobody_signed_in_to_is_refused(client, profile_id):
    """The correction this round is about.

    `invoke` used to answer `performed` for every row on the board, having
    reached nothing at all — a Gmail connector with no Google account behind
    it reported that it had summarised the inbox.

        asked     did the call succeed
        mattered  did anything happen on the other end
    """
    conn = _connect(client, profile_id, provider="work", app="gmail")
    assert conn["needs"] == "sign-in"
    assert conn["authorized"] is False
    r = client.post(f"/apps/{conn['id']}/invoke", json={"capability": "send"})
    assert r.status_code == 409
    # And it says what to go and do, naming the app the way the person sees it.
    assert "Gmail" in r.json()["detail"]


def test_a_public_connector_needs_nothing_and_says_so(client, profile_id):
    """Half the point of the posture: a lock on every row is not a signal."""
    conn = _connect(client, profile_id, provider="scrape", app="instagram")
    assert conn["needs"] == "nothing"
    assert conn["authorized"] is True
    # There is nothing to sign in to, so offering the door would be the lie.
    assert client.post(f"/apps/{conn['id']}/authorize",
                       json={"secret": "x"}).status_code == 409


def test_a_credential_is_sealed_and_never_lands_in_this_database(client,
                                                                 profile_id):
    vault = _Vault()
    client.app.state.pdi = vault
    conn = _connect(client, profile_id, provider="work", app="slack")
    r = client.post(f"/apps/{conn['id']}/authorize",
                    json={"secret": "xoxb-hunter2", "account": "dana"})
    assert r.status_code == 200, r.text
    assert r.json()["authorized"] is True
    assert list(vault.kept) == [f"qrme/{profile_id}/connectors/{conn['id']}"]

    from qrme import db
    rows = db.connect().execute(
        "SELECT * FROM app_connectors WHERE id=?", (conn["id"],)).fetchone()
    assert "hunter2" not in " ".join(str(v) for v in tuple(rows))


def test_no_vault_means_the_credential_is_not_kept_at_all(client, profile_id):
    """Free is platform custody over plain HTTPS, which is a fine posture for
    a wall post and not one for somebody's account credential."""
    client.app.state.pdi = None
    conn = _connect(client, profile_id, provider="work", app="slack")
    r = client.post(f"/apps/{conn['id']}/authorize", json={"secret": "x"})
    assert r.status_code == 409
    assert client.get(f"/profiles/{profile_id}/apps").json()[-1][
        "authorized"] is False


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
