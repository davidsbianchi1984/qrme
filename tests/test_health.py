"""Service liveness: /health answers with tandem flags, sibling-style."""


def test_health_reports_status_and_tandems(client):
    body = client.get("/health").json()
    assert body["status"] == "ok"
    # Plain test client: no PDI, no cloud, not offline.
    assert body["pdi"] is False
    assert body["cloud"] is False
    assert body["offline"] is False


def test_the_footsteps_count_people_and_only_when_verified(client, monkeypatch):
    """The counter in the corner: how many people hold accounts here.

    An aggregate, never a roster — the payload carries the number and nothing
    else about anybody. A signup that never verified its address does not
    move it, because an unverified row is a mistyped address as often as a
    person.
    """
    from tests.test_accounts import _capture_mail, _code_from, _signup

    before = client.get("/health").json()["footsteps"]

    sent = _capture_mail(monkeypatch)
    _signup(client, email="walker@example.test")
    # Signed up, not verified: the ground has not been walked on yet.
    assert client.get("/health").json()["footsteps"] == before

    client.post("/verify-email", json={
        "email": "walker@example.test", "code": _code_from(sent[0])})
    joined = 1
    assert client.get("/health").json()["footsteps"] == before + joined
