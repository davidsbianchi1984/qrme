"""Offline-first mode: with QRME_OFFLINE set, nothing can leave the host —
inference is local, the cloud is refused even if injected, and adaptation
(embeddings / fine-tuning) is recomputed locally."""

import pytest
from fastapi.testclient import TestClient

from qrme import db
from tests.test_capabilities import make_profile
from tests.test_cloud import FakeCloudHttp


@pytest.fixture()
def offline_client(tmp_path, monkeypatch):
    """A QRME app booted in offline mode, with a cloud client *injected* to
    prove offline refuses it."""
    monkeypatch.setenv("QRME_DB", str(tmp_path / "off.db"))
    monkeypatch.setenv("QRME_LLM", "stub")
    monkeypatch.setenv("QRME_OFFLINE", "1")
    db.reset()
    from qrme.api import create_app
    from qrme.cloud import CloudModelClient

    cloud = CloudModelClient(client=FakeCloudHttp())
    with TestClient(create_app(cloud_client=cloud)) as c:
        yield c
    db.reset()


def test_offline_status_reports_no_external_transmission(offline_client):
    s = offline_client.get("/offline/status").json()
    assert s["offline"] is True
    assert s["external_transmission_possible"] is False
    assert s["cloud_attached"] is False
    assert "no cloud gateway calls" in s["guarantees"]


def test_offline_refuses_the_injected_cloud(offline_client):
    # Even though a cloud client was injected, offline drops it.
    assert offline_client.get("/cloud/status").json()["cloud"] is False


def test_offline_chat_and_local_finetune_work(offline_client):
    client = offline_client
    p = make_profile(client)
    user = client.post("/interactors", json={"display_name": "Ada"}).json()["id"]
    r = client.post(f"/profiles/{p['id']}/chat",
                    json={"interactor_id": user, "message": "hello"})
    assert r.status_code == 200 and r.json()["profile_message"]["content"]

    ft = client.post(f"/profiles/{p['id']}/finetune").json()
    assert ft["external_transmission"] is False
    assert ft["offline_mode"] is True


def test_offline_contribution_is_inert(offline_client):
    client = offline_client
    p = make_profile(client, cloud_contribution=True)
    user = client.post("/interactors", json={"display_name": "Bo"}).json()["id"]
    client.post(f"/profiles/{p['id']}/chat",
                json={"interactor_id": user, "message": "hi"})
    fb = client.post(
        f"/profiles/{p['id']}/interactions/{user}/feedback",
        json={"rating": "up"}).json()
    # No cloud attached → nothing is ever contributed.
    assert fb["contributed"] is False


def test_online_default_allows_external_transmission(client):
    # The normal (non-offline) app reports that external transmission is
    # possible (the local provider is still the fallback).
    s = client.get("/offline/status").json()
    assert s["offline"] is False
    assert s["external_transmission_possible"] is True
