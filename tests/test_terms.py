"""Terms of Service at the gateway: served with a version, accepted by
clickwrap, recorded with a receipt — and an explicit refusal is refused."""

from qrme import db
from qrme.terms import TERMS_VERSION
from tests.conftest import ADULT_VERIFICATION


def test_terms_are_served_versioned(client):
    t = client.get("/terms").json()
    assert t["version"] == TERMS_VERSION
    assert t["document"] == "docs/terms.md"
    assert any("synthetic" in p for p in t["key_points"])
    assert any("911" in p for p in t["key_points"])


def test_acceptance_is_recorded_and_refusal_refused(client):
    body = {"owner_id": "owner-1", "kind": "self", "display_name": "Dana",
            "persona": "A retired teacher.",
            "verification": ADULT_VERIFICATION}

    refused = client.post("/profiles", json={**body, "terms_consent": False})
    assert refused.status_code == 403
    assert "Terms of Service" in refused.json()["detail"]

    created = client.post("/profiles", json={**body, "terms_consent": True})
    assert created.status_code == 201
    row = db.connect().execute(
        "SELECT terms_version, terms_accepted_at FROM profiles WHERE id=?",
        (created.json()["id"],)).fetchone()
    assert row["terms_version"] == TERMS_VERSION
    assert row["terms_accepted_at"]      # timestamped receipt
