import pytest
from fastapi.testclient import TestClient

from jim import db as jim_db


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """JIM-mini running standalone (no tandem)."""
    monkeypatch.setenv("JIM_DB", str(tmp_path / "jim.db"))
    monkeypatch.setenv("JIM_LLM", "stub")
    monkeypatch.delenv("JIM_QRME_URL", raising=False)
    jim_db.reset()
    from jim.api import create_app

    with TestClient(create_app()) as c:
        yield c
    jim_db.reset()


@pytest.fixture()
def tandem(tmp_path, monkeypatch):
    """JIM-mini wired to a real in-process QRME over the client boundary.

    Returns (jim_client, qrme_client-as-TestClient). The QRME instance is a
    genuine separate app; JIM reaches it only through QRMEClient.
    """
    monkeypatch.setenv("JIM_DB", str(tmp_path / "jim.db"))
    monkeypatch.setenv("JIM_LLM", "stub")
    monkeypatch.setenv("QRME_DB", str(tmp_path / "qrme.db"))
    monkeypatch.setenv("QRME_LLM", "stub")

    import qrme.db as qrme_db
    jim_db.reset()
    qrme_db.reset()

    from qrme.api import create_app as create_qrme
    from jim.api import create_app as create_jim
    from jim.qrme_client import QRMEClient

    qrme_tc = TestClient(create_qrme())
    qrme_tc.__enter__()
    jim_tc = TestClient(create_jim(qrme_client=QRMEClient(client=qrme_tc)))
    jim_tc.__enter__()
    try:
        yield jim_tc, qrme_tc
    finally:
        jim_tc.__exit__(None, None, None)
        qrme_tc.__exit__(None, None, None)
        jim_db.reset()
        qrme_db.reset()


def enroll(client, **extra):
    body = {"display_name": "Jordan", "birthdate": "1995-05-05",
            "terms_consent": True, "resting_heart_rate": 60}
    body.update(extra)
    r = client.post("/enroll", json=body)
    assert r.status_code == 201, r.text
    return r.json()["id"]
