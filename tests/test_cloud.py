"""Cloud Model Gateway: greater-model inference with local fallback, and the
opt-in, anonymized contribution loop."""

import json

import pytest
from fastapi.testclient import TestClient

from qrme import db
from tests.test_capabilities import _Resp, make_interactor, make_profile


class FakeCloudHttp:
    """The gateway at the HTTP-client boundary."""

    def __init__(self, fail=False):
        self.fail = fail
        self.contributions = []

    def post(self, path, json=None, headers=None):
        if path == "/v1/generate":
            if self.fail:
                return _Resp(503, {})
            tail = json["messages"][-1]["content"][:40]
            return _Resp(200, {"content": f"[cloud:claude-fable-5] {tail}",
                               "model": "claude-fable-5"})
        if path == "/v1/contributions":
            self.contributions.append(json)
            return _Resp(202, {"accepted": True})
        if path == "/v1/contributions/revoke":
            refs = set(json["refs"])
            self.contributions = [c for c in self.contributions
                                  if c.get("ref") not in refs]
            return _Resp(200, {"deleted": True})
        return _Resp(404, {})

    def get(self, path, headers=None):
        return _Resp(200, {"model": "claude-fable-5", "tier": "cloud"})


@pytest.fixture()
def cloud_pair(tmp_path, monkeypatch):
    monkeypatch.setenv("QRME_DB", str(tmp_path / "cloud-test.db"))
    monkeypatch.setenv("QRME_LLM", "stub")
    db.reset()
    from qrme.api import create_app
    from qrme.cloud import CloudModelClient

    def make(fail=False):
        fake = FakeCloudHttp(fail=fail)
        client = TestClient(create_app(
            cloud_client=CloudModelClient(token="cld_test", client=fake)))
        client.__enter__()
        return client, fake

    made = []
    def factory(fail=False):
        pair = make(fail)
        made.append(pair[0])
        return pair
    yield factory
    for c in made:
        c.__exit__(None, None, None)
    db.reset()


def test_chat_uses_the_greater_model(cloud_pair):
    client, fake = cloud_pair()
    p = make_profile(client)
    user = make_interactor(client)
    r = client.post(f"/profiles/{p['id']}/chat",
                    json={"interactor_id": user, "message": "hello"}).json()
    assert r["profile_message"]["content"].startswith("[cloud:claude-fable-5]")

    status = client.get("/cloud/status").json()
    assert status["cloud"] is True
    assert status["model"]["model"] == "claude-fable-5"


def test_gateway_down_falls_back_to_local(cloud_pair):
    client, fake = cloud_pair(fail=True)
    p = make_profile(client)
    user = make_interactor(client)
    r = client.post(f"/profiles/{p['id']}/chat",
                    json={"interactor_id": user, "message": "hello"}).json()
    msg = r["profile_message"]["content"]
    assert msg and "[cloud" not in msg          # stub answered instead


def test_contribution_requires_opt_in_and_is_anonymized(cloud_pair):
    client, fake = cloud_pair()
    consenting = make_profile(client, cloud_contribution=True,
                              purpose="companion_coach")
    private = make_profile(client, display_name="Quiet")
    user = make_interactor(client)

    for pid in (consenting["id"], private["id"]):
        client.post(f"/profiles/{pid}/chat",
                    json={"interactor_id": user, "message": "I loved that story, Dana"})

    up = client.post(
        f"/profiles/{consenting['id']}/interactions/{user}/feedback",
        json={"rating": "up"}).json()
    assert up["contributed"] is True
    payload = fake.contributions[0]
    blob = json.dumps(payload)
    assert payload["source"] == "qrme" and payload["quality"] == "positive"
    assert consenting["id"] not in blob         # no profile id
    assert user not in blob                     # no interactor id
    assert "Dana" not in blob                   # display name stripped
    assert "PERSONA" in blob

    # No consent → nothing leaves, even on a thumbs-up.
    quiet = client.post(
        f"/profiles/{private['id']}/interactions/{user}/feedback",
        json={"rating": "up"}).json()
    assert quiet["contributed"] is False
    assert len(fake.contributions) == 1

    # Down-votes are never contributed either.
    client.post(f"/profiles/{consenting['id']}/chat",
                json={"interactor_id": user, "message": "hm"})
    down = client.post(
        f"/profiles/{consenting['id']}/interactions/{user}/feedback",
        json={"rating": "down"}).json()
    assert down["contributed"] is False
    assert len(fake.contributions) == 1


def test_status_without_gateway(client):
    status = client.get("/cloud/status").json()
    assert status["cloud"] is False and status["model"] is None
