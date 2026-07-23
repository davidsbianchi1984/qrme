"""Per-profile LLM provider selection (GET /models, GET/PUT profile model)."""


def test_list_models_includes_all_providers(client):
    body = client.get("/models").json()
    names = {p["name"] for p in body["providers"]}
    assert {"stub", "anthropic", "openai", "grok", "perplexity", "gemini"} <= names
    # In the test env only the stub is configured; the default resolves to it.
    stub = next(p for p in body["providers"] if p["name"] == "stub")
    assert stub["configured"] is True
    assert body["default"] == "stub"


def test_profile_defaults_to_auto(client, profile_id):
    body = client.get(f"/profiles/{profile_id}/model").json()
    assert body["provider"] == "auto"
    assert body["effective"] == "stub"  # nothing else configured in tests


def test_owner_can_set_provider(client, profile_id):
    r = client.put(f"/profiles/{profile_id}/model", json={"provider": "openai"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["provider"] == "openai"
    # OpenAI has no key in the test env, so it degrades to the stub.
    assert body["effective"] == "stub"

    # Persisted and surfaced on read.
    assert client.get(f"/profiles/{profile_id}/model").json()["provider"] == "openai"


def test_choice_shows_up_in_transparency(client, profile_id):
    client.put(f"/profiles/{profile_id}/model", json={"provider": "gemini"})
    t = client.get(f"/profiles/{profile_id}/transparency").json()
    assert t["model_provider"] == "gemini"
    assert t["model_effective"] == "stub"


def test_unknown_provider_rejected(client, profile_id):
    r = client.put(f"/profiles/{profile_id}/model", json={"provider": "not-a-model"})
    assert r.status_code == 422


def test_set_provider_requires_owner(client, profile_id):
    # Drop the owner credential the fixture installed.
    client.headers.pop("authorization", None)
    r = client.put(f"/profiles/{profile_id}/model", json={"provider": "openai"})
    assert r.status_code in (401, 403)


def test_chat_still_works_with_a_chosen_provider(client, profile_id, interactor_id):
    # Choosing an unconfigured provider must never break generation — it
    # degrades to the deterministic stub.
    client.put(f"/profiles/{profile_id}/model", json={"provider": "grok"})
    r = client.post(
        f"/profiles/{profile_id}/chat",
        json={"interactor_id": interactor_id, "message": "hello"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["profile_message"]["content"]
