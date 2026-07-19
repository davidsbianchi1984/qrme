"""Capability-token authentication: owner control is gated behind the owner
token minted at creation; public surfaces stay open; interactors reach only
their own private memory."""

from tests.test_capabilities import ADULT, make_interactor


def _create(client, **extra):
    """Create a profile via the raw client, returning its JSON (including the
    one-time owner_token) without mutating the client's default headers."""
    body = {"owner_id": "owner-1", "kind": "self", "display_name": "Dana",
            "persona": "A retired teacher who loves gardening.",
            "verification": ADULT}
    body.update(extra)
    r = client.post("/profiles", json=body, headers={})
    assert r.status_code == 201, r.text
    return r.json()


def test_create_returns_owner_token_once(client):
    p = _create(client)
    assert p["owner_token"]
    # The token is not persisted in retrievable form: the public card omits it.
    card = client.get(f"/profiles/{p['id']}", headers={}).json()
    assert "owner_token" not in card


def test_owner_endpoint_requires_a_token(client):
    p = _create(client)
    # No credential at all → 401.
    assert client.get(f"/profiles/{p['id']}/export", headers={}).status_code == 401
    assert client.delete(f"/profiles/{p['id']}", headers={}).status_code == 401
    assert client.post(f"/profiles/{p['id']}/sources", headers={},
                       json={"kind": "writing", "title": "x",
                             "content": "y"}).status_code == 401


def test_wrong_owner_token_is_forbidden(client):
    p = _create(client)
    other = _create(client, display_name="Someone Else")
    wrong = {"authorization": f"Bearer {other['owner_token']}"}
    # A valid token for a different profile → 403, not 401.
    assert client.get(f"/profiles/{p['id']}/export", headers=wrong).status_code == 403
    assert client.get(f"/profiles/{p['id']}/stats", headers=wrong).status_code == 403
    # A garbage token → 401.
    assert client.get(f"/profiles/{p['id']}/export",
                      headers={"authorization": "Bearer nope"}).status_code == 401


def test_correct_owner_token_authorizes(client):
    p = _create(client)
    ok = {"authorization": f"Bearer {p['owner_token']}"}
    assert client.get(f"/profiles/{p['id']}/export", headers=ok).status_code == 200
    r = client.post(f"/profiles/{p['id']}/sources", headers=ok,
                    json={"kind": "writing", "title": "note", "content": "hi"})
    assert r.status_code == 201
    assert client.get(f"/profiles/{p['id']}/sources",
                      headers=ok).status_code == 200


def test_public_surfaces_need_no_token(client):
    p = _create(client)
    user = make_interactor(client)
    # Chatting with a profile is open by design.
    r = client.post(f"/profiles/{p['id']}/chat", headers={},
                    json={"interactor_id": user, "message": "hi"})
    assert r.status_code == 200
    # Browsing the marketplace and reading a profile card are open.
    assert client.get("/marketplace", headers={}).status_code == 200
    assert client.get(f"/profiles/{p['id']}", headers={}).status_code == 200


def test_delete_revokes_the_owner_token(client):
    p = _create(client)
    ok = {"authorization": f"Bearer {p['owner_token']}"}
    assert client.delete(f"/profiles/{p['id']}", headers=ok).status_code == 200
    # The profile is gone and the token no longer resolves to anything.
    assert client.get(f"/profiles/{p['id']}/export", headers=ok).status_code == 404


def test_memory_reachable_by_owner_or_that_interactor(client):
    p = _create(client)
    owner = {"authorization": f"Bearer {p['owner_token']}"}
    who = client.post("/interactors",
                      json={"display_name": "Mara", "birthdate": "1990-01-01"},
                      headers={}).json()
    user, user_tok = who["id"], who["token"]
    client.post(f"/profiles/{p['id']}/chat", headers={},
                json={"interactor_id": user, "message": "hello"})

    mem = f"/profiles/{p['id']}/memory/{user}"
    assert client.get(mem, headers={}).status_code == 401          # anonymous
    assert client.get(mem, headers=owner).status_code == 200       # the owner
    assert client.get(                                             # that user
        mem, headers={"authorization": f"Bearer {user_tok}"}).status_code == 200

    # A different interactor cannot read this conversation.
    other = client.post("/interactors",
                        json={"display_name": "Nia"}, headers={}).json()
    assert client.get(
        mem, headers={"authorization": f"Bearer {other['token']}"}
    ).status_code == 403
