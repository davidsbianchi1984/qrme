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
            # Pro, where the product default is Basic — see the note on
            # tests/test_capabilities.py:make_profile. The membership gate is
            # tested on its own accounts in test_tiers.py.
            "plan": "pro",
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


@pytest.fixture()
def interactor_head(client, interactor_id):
    """Sam's own token, as a header.

    Separate from `interactor_id` so a test has to reach for it deliberately.
    Several surfaces about a person — their rating, their engagement record —
    were readable and writable with no token at all, and the tests did not
    notice because they had none to send.
    """
    row = client.get(f"/interactors/{interactor_id}")
    if row.status_code == 200 and row.json().get("token"):
        return {"authorization": f"Bearer {row.json()['token']}"}
    from qrme import auth
    return {"authorization": f"Bearer {auth.issue('interactor', interactor_id)}"}
