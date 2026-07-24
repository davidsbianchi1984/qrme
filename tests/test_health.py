"""Service liveness: /health answers with tandem flags, sibling-style."""


def test_health_reports_status_and_tandems(client):
    body = client.get("/health").json()
    assert body["status"] == "ok"
    # Plain test client: no PDI, no cloud, not offline.
    assert body["pdi"] is False
    assert body["cloud"] is False
    assert body["offline"] is False
