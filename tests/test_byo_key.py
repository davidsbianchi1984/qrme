"""Bring-your-own model key: ``x-llm-api-key`` rides the request.

The caller's generations run on their credential; the deployment's env key
(the operator lending theirs out) is the fallback; the key is request-scoped
— never persisted, gone when the request ends.
"""

from __future__ import annotations

from qrme import llm


def test_a_request_key_makes_the_chosen_provider_usable(client, profile_id):
    """With no env keys at all, an explicit choice + a caller key resolves to
    that provider instead of being dropped for the default."""
    r = client.put(f"/profiles/{profile_id}/model",
                   json={"provider": "anthropic"},
                   headers={"x-llm-api-key": "sk-their-own"})
    assert r.status_code == 200, r.text
    assert r.json()["effective"] == "anthropic"


def test_without_a_key_the_unconfigured_choice_still_falls_back(client, profile_id):
    r = client.put(f"/profiles/{profile_id}/model",
                   json={"provider": "anthropic"})
    assert r.status_code == 200, r.text
    assert r.json()["effective"] == "stub"


def test_a_key_with_auto_defaults_to_a_real_model_not_the_stub(
        client, profile_id, monkeypatch):
    # The test env pins QRME_LLM=stub — an explicit operator choice that
    # outranks auto. A fresh install has no such pin; simulate that here.
    monkeypatch.delenv("QRME_LLM", raising=False)
    r = client.get(f"/profiles/{profile_id}/model",
                   headers={"x-llm-api-key": "sk-their-own"})
    assert r.status_code == 200
    assert r.json()["effective"] == "anthropic"
    # And the same request without the key answers stub — the key was
    # request-scoped, not remembered.
    assert client.get(
        f"/profiles/{profile_id}/model").json()["effective"] == "stub"


def test_the_key_reaches_the_provider_build(client, profile_id, monkeypatch):
    """The generation path constructs the provider with the caller's key."""
    seen: dict = {}

    class FakeAnthropic:
        def __init__(self, api_key=None):
            seen["api_key"] = api_key
            raise RuntimeError("stop here — construction is the assertion")

    import sys
    import types

    monkeypatch.setitem(sys.modules, "anthropic",
                        types.SimpleNamespace(Anthropic=FakeAnthropic))
    monkeypatch.delenv("QRME_LLM", raising=False)   # drop the test stub pin

    client.put(f"/profiles/{profile_id}/model", json={"provider": "anthropic"},
               headers={"x-llm-api-key": "sk-their-own"})
    me = client.post("/interactors", json={"display_name": "Visitor"}).json()
    r = client.post(f"/profiles/{profile_id}/chat",
                    json={"interactor_id": me["id"],
                          "message": "Hello there, how are you today?"},
                    headers={"x-llm-api-key": "sk-their-own"})
    # The failed construction degrades to the stub — the reply still comes.
    assert r.status_code == 200, r.text
    assert seen["api_key"] == "sk-their-own"


def test_the_key_is_never_persisted(client, profile_id):
    client.put(f"/profiles/{profile_id}/model", json={"provider": "anthropic"},
               headers={"x-llm-api-key": "sk-their-own"})
    from qrme import db
    assert llm.request_key() is None               # the key is gone
    dump = "\n".join(db.connect().iterdump())
    assert "sk-their-own" not in dump