"""Hosting posture: reachable from a LAN or from the internet, safely.

The same deployment serves a laptop on Wi-Fi and a published instance the
operator and their colleagues reach from anywhere. What changes between the
two is what pairing advertises and whether profile creation is gated.
"""

from qrme import mobile


def test_pairing_advertises_the_published_url_when_hosted(client, monkeypatch):
    """A hosted deployment's QR must point at the address the phone can
    actually reach — its public URL, not a LAN address the phone can't see."""
    monkeypatch.setenv("QRME_PUBLIC_URL", "https://studio.example.com/")
    body = client.get("/pair").json()
    assert body["hosted"] is True
    assert body["console_url"] == "https://studio.example.com/app/"
    assert body["reachable"] is True
    assert "HTTPS" in body["note"]


def test_pairing_falls_back_to_lan_when_not_published(client, monkeypatch):
    """No public URL = the laptop posture, unchanged."""
    monkeypatch.delenv("QRME_PUBLIC_URL", raising=False)
    monkeypatch.setenv("QRME_LAN_HOST", "192.168.1.42")
    body = client.get("/pair").json()
    assert body["hosted"] is False
    assert body["console_url"].startswith("http://192.168.1.42:")
    assert "local network only" in body["note"].lower()


def test_public_base_normalises_trailing_slash(monkeypatch):
    monkeypatch.setenv("QRME_PUBLIC_URL", "https://studio.example.com/")
    assert mobile.public_base() == "https://studio.example.com"
    monkeypatch.delenv("QRME_PUBLIC_URL")
    assert mobile.public_base() is None


def _profile_body():
    return {"owner_id": "owner-1", "kind": "self", "display_name": "Ada",
            "persona": "A careful engineer.",
            "verification": {"birthdate": "1990-01-01",
                             "id_document": "passport",
                             "liveness_check": True}}


def test_signup_key_gates_profile_creation_when_set(client, monkeypatch):
    """A published instance stays the operator's: without the key, no new
    profiles; with it, creation works normally."""
    monkeypatch.setenv("QRME_SIGNUP_KEY", "let-me-in")
    refused = client.post("/profiles", json=_profile_body())
    assert refused.status_code == 403
    assert "signup key" in refused.json()["detail"]

    wrong = client.post("/profiles", json=_profile_body(),
                        headers={"x-signup-key": "guess"})
    assert wrong.status_code == 403

    ok = client.post("/profiles", json=_profile_body(),
                     headers={"x-signup-key": "let-me-in"})
    assert ok.status_code == 201
    assert ok.json()["owner_token"]


def test_no_signup_key_leaves_local_use_open(client, monkeypatch):
    """Unset = the LAN/laptop default: reaching it is enough."""
    monkeypatch.delenv("QRME_SIGNUP_KEY", raising=False)
    assert client.post("/profiles", json=_profile_body()).status_code == 201


def test_signup_key_does_not_gate_talking_to_a_profile(client, monkeypatch):
    """The gate is on creating an account here, not on public surfaces —
    chatting with a profile stays open by design."""
    monkeypatch.delenv("QRME_SIGNUP_KEY", raising=False)
    pid = client.post("/profiles", json=_profile_body()).json()["id"]
    monkeypatch.setenv("QRME_SIGNUP_KEY", "let-me-in")
    interactor = client.post("/interactors", json={"display_name": "Sam"})
    assert interactor.status_code == 201
    r = client.post(f"/profiles/{pid}/chat",
                    json={"interactor_id": interactor.json()["id"],
                          "message": "hello"})
    assert r.status_code == 200
