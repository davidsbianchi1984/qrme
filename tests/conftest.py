import os

import pytest
from fastapi.testclient import TestClient

from qrme import db


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("QRME_DB", str(tmp_path / "test.db"))
    monkeypatch.setenv("QRME_LLM", "stub")
    db.reset()
    from qrme.api import create_app

    with TestClient(create_app()) as test_client:
        yield test_client
    db.reset()


ADULT_VERIFICATION = {"birthdate": "1984-06-01"}


@pytest.fixture()
def profile_id(client):
    response = client.post(
        "/profiles",
        json={
            "owner_id": "owner-1",
            "kind": "self",
            "display_name": "Dana",
            "persona": "A retired teacher who loves gardening and dry humor.",
            "verification": ADULT_VERIFICATION,
        },
    )
    assert response.status_code == 201, response.text
    body = response.json()
    # Authenticate the client as this profile's owner for owner-only endpoints.
    client.headers["authorization"] = f"Bearer {body['owner_token']}"
    return body["id"]


@pytest.fixture()
def interactor_id(client):
    response = client.post(
        "/interactors",
        json={"display_name": "Sam", "birthdate": "2000-01-15"},
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]
