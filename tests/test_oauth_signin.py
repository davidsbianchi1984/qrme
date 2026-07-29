"""Sign in with Google/Apple: configuration decides whether the doors are
live, the provider's word verifies the inbox, and the parked session is
claimable exactly once.
"""

import base64
import json

from qrme import oauth


def _id_token(email, name="Signer"):
    payload = base64.urlsafe_b64encode(
        json.dumps({"email": email, "email_verified": True,
                    "name": name}).encode()).rstrip(b"=").decode()
    return f"h.{payload}.s"


def test_unconfigured_providers_say_so(client):
    listed = client.get("/auth/oauth/providers").json()["providers"]
    assert {p["provider"] for p in listed} == {"google", "apple"}
    for p in listed:
        assert p["configured"] is False and "setup" in p
    r = client.post("/auth/oauth/google/start", json={})
    assert r.status_code == 503
    assert "not configured" in r.json()["detail"]


def test_the_full_door_swings_once(client, monkeypatch):
    monkeypatch.setenv("QRME_GOOGLE_CLIENT_ID", "cid-123")
    monkeypatch.setenv("QRME_GOOGLE_CLIENT_SECRET", "sec-456")

    started = client.post("/auth/oauth/google/start", json={}).json()
    assert "accounts.google.com" in started["url"]
    assert "cid-123" in started["url"] and started["state"] in started["url"]

    # The provider redirects back; the exchange is stubbed — the shape of
    # what Google returns, without the network.
    monkeypatch.setattr(oauth, "_exchange", lambda spec, code, uri: {
        "id_token": _id_token("dana@example.com", "Dana")})
    r = client.get("/auth/oauth/google/callback",
                   params={"code": "authcode", "state": started["state"]})
    assert r.status_code == 200 and "dana@example.com" in r.text

    claimed = client.get("/auth/oauth/claim",
                         params={"state": started["state"]}).json()
    assert claimed["ready"] is True
    assert claimed["email"] == "dana@example.com"
    assert claimed["account_token"]

    # Provider-verified means signed in without ever touching the emailed
    # code — and a typed password fails closed on a passwordless account.
    r = client.post("/signin", json={"email": "dana@example.com",
                                     "password": "any-guess-at-all"})
    assert r.status_code == 403

    # The state is spent: neither a second claim nor a replayed callback.
    assert client.get("/auth/oauth/claim",
                      params={"state": started["state"]}).status_code == 403
    r = client.get("/auth/oauth/callback".replace("/callback",
                   "/google/callback"),
                   params={"code": "authcode", "state": started["state"]})
    assert r.status_code == 403


def test_an_existing_email_account_is_the_same_account(client, monkeypatch):
    monkeypatch.setenv("QRME_GOOGLE_CLIENT_ID", "cid")
    monkeypatch.setenv("QRME_GOOGLE_CLIENT_SECRET", "sec")
    client.post("/signup", json={"email": "same@example.com",
                                 "password": "longenough8"})

    started = client.post("/auth/oauth/google/start", json={}).json()
    monkeypatch.setattr(oauth, "_exchange", lambda spec, code, uri: {
        "id_token": _id_token("same@example.com")})
    client.get("/auth/oauth/google/callback",
               params={"code": "c", "state": started["state"]})
    claimed = client.get("/auth/oauth/claim",
                         params={"state": started["state"]}).json()

    # Same address, same account — and the provider's word verified it, so
    # the original password still works after the email dance is skipped.
    from qrme import db
    rows = db.connect().execute(
        "SELECT id, verified_at FROM accounts WHERE email='same@example.com'"
    ).fetchall()
    assert len(rows) == 1 and rows[0]["id"] == claimed["account_id"]
    assert rows[0]["verified_at"]
    r = client.post("/signin", json={"email": "same@example.com",
                                     "password": "longenough8"})
    assert r.status_code == 200
