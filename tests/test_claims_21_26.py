"""Coverage for claims 21–26: latent persona embeddings, attention
conditioning, real-time biometrics, specialist switching, revocable-grant
tasks over the vault, and offline fine-tuning."""

import json

from tests.test_capabilities import (
    FakePDIHttp, as_owner, make_interactor, make_profile,  # noqa: F401
    pdi_pair,
)


def test_embedding_persists_and_versions_across_sessions(client):
    """Claim 21: latent persona embedding in a persistent memory module."""
    p = make_profile(client)
    user = make_interactor(client)
    client.post(f"/profiles/{p['id']}/chat",
                json={"interactor_id": user, "message": "hello there"})
    first = client.get(f"/profiles/{p['id']}/embedding/{user}").json()
    assert set(first["vector"]) == {"engagement", "warmth", "depth",
                                    "positivity", "stress", "continuity"}
    long_message = ("Let me tell you properly about the old garden: " * 8).strip()
    client.post(f"/profiles/{p['id']}/chat",
                json={"interactor_id": user, "message": long_message})
    second = client.get(f"/profiles/{p['id']}/embedding/{user}").json()
    assert second["version"] > first["version"]
    assert second["vector"]["depth"] > first["vector"]["depth"]


def test_embedding_tracks_relationship_warmth(client):
    """Claim 22 input: the vector that conditions attention reflects state."""
    p = make_profile(client)
    kin = make_interactor(client, "Maya")
    client.put(f"/profiles/{p['id']}/relationships/{kin}",
               json={"relationship_type": "family"})
    client.post(f"/profiles/{p['id']}/chat",
                json={"interactor_id": kin, "message": "hi grandma"})
    warm = client.get(f"/profiles/{p['id']}/embedding/{kin}").json()

    anon = make_interactor(client, "Visitor")
    client.post(f"/profiles/{p['id']}/chat",
                json={"interactor_id": anon, "message": "hi grandma"})
    cold = client.get(f"/profiles/{p['id']}/embedding/{anon}").json()
    assert warm["vector"]["warmth"] > cold["vector"]["warmth"]


def test_biometrics_received_and_remembered(client):
    """Claim 23: real-time monitoring data arrives with the interaction."""
    p = make_profile(client)
    user = make_interactor(client)
    r = client.post(f"/profiles/{p['id']}/chat", json={
        "interactor_id": user, "message": "I feel off today",
        "biometrics": {"heart_rate": 112, "stress_level": 0.8}})
    assert r.status_code == 200
    embedding = client.get(f"/profiles/{p['id']}/embedding/{user}").json()
    assert embedding["vector"]["stress"] > 0


def test_specialist_switch_on_biometrics(client):
    """Claim 24: monitoring signals route the reply to a domain specialist."""
    p = make_profile(client)
    calm = make_profile(client, display_name="Dr. Rivera",
                        persona="A calm mental-health specialist.",
                        purpose="companion_coach")
    as_owner(client, p)   # configure the specialist as p's owner
    client.put(f"/profiles/{p['id']}/specialists", json={
        "domain": "mental_health", "specialist_profile_id": calm["id"]})
    user = make_interactor(client)

    routine = client.post(f"/profiles/{p['id']}/chat", json={
        "interactor_id": user, "message": "hello"}).json()
    assert routine["handoff"] is None

    stressed = client.post(f"/profiles/{p['id']}/chat", json={
        "interactor_id": user, "message": "everything is too much",
        "biometrics": {"stress_level": 0.9, "condition": "anxiety"}}).json()
    assert stressed["handoff"] == {
        "domain": "mental_health", "specialist_profile_id": calm["id"],
        "reason": "real-time monitoring signals", "state": "engaged"}
    assert stressed["profile_message"]["status"] == "approved"

    # The handoff is sustained: a follow-up turn with NO biometrics still
    # routes to the specialist rather than snapping back to the profile.
    still = client.post(f"/profiles/{p['id']}/chat", json={
        "interactor_id": user, "message": "what should I do?"}).json()
    assert still["handoff"]["state"] == "sustained"
    assert still["handoff"]["specialist_profile_id"] == calm["id"]

    # Recovery signals hand control back to the primary profile.
    recovered = client.post(f"/profiles/{p['id']}/chat", json={
        "interactor_id": user, "message": "feeling better now",
        "biometrics": {"stress_level": 0.1}}).json()
    assert recovered["handoff"]["state"] == "returned"

    # And subsequent calm turns speak as the profile again (no handoff).
    back = client.post(f"/profiles/{p['id']}/chat", json={
        "interactor_id": user, "message": "thanks"}).json()
    assert back["handoff"] is None


def test_tasks_run_under_revocable_grant(pdi_pair):
    """Claim 25: multi-step task over the vault; no raw data retained;
    revoking the grant kills execution."""
    client, fake = pdi_pair
    p = make_profile(client)
    client.post(f"/profiles/{p['id']}/sources", json={
        "kind": "life_event", "title": "wedding 1972",
        "content": "We danced until the band gave up and went home."})
    grant = client.post(f"/profiles/{p['id']}/grants", json={}).json()

    r = client.post(f"/profiles/{p['id']}/tasks", json={
        "topic": "an anniversary note", "grant_token": grant["token"]})
    assert r.status_code == 201
    task = r.json()
    assert task["status"] == "completed" and task["output"]
    step_names = [s["step"] for s in task["steps"]]
    assert step_names == ["grant_check", "vault_read", "compose", "moderation"]
    assert task["steps"][1]["vaulted"] == 1
    # The stored task log retains summaries only — never the raw vault data.
    stored = client.get(f"/profiles/{p['id']}/tasks").json()[0]
    assert "danced" not in json.dumps(stored["steps"])

    client.delete(f"/grants/{grant['id']}")
    denied = client.post(f"/profiles/{p['id']}/tasks", json={
        "topic": "another note", "grant_token": grant["token"]})
    assert denied.status_code == 403


def test_offline_finetune_seals_artifact(pdi_pair):
    """Claim 26: encrypted offline fine-tuning; nothing leaves the host."""
    client, fake = pdi_pair
    p = make_profile(client)
    user = make_interactor(client)
    for msg in ("hello", "tell me about the garden", "and the roses?"):
        client.post(f"/profiles/{p['id']}/chat",
                    json={"interactor_id": user, "message": msg})
    run = client.post(f"/profiles/{p['id']}/finetune").json()
    assert run["messages_processed"] == 3
    assert run["external_transmission"] is False
    assert run["sealed_in_vault"] is True
    artifact = json.loads(fake.store[run["vault_key"]])
    assert user in artifact
    # The recomputed embedding is now the live cross-session state.
    assert client.get(f"/profiles/{p['id']}/embedding/{user}").status_code == 200

    deleted = client.delete(f"/profiles/{p['id']}").json()["deleted"]
    assert deleted["finetune_runs"] == 1
    assert run["vault_key"] not in fake.store   # artifact purged too


def test_finetune_works_without_pdi(client):
    p = make_profile(client)
    user = make_interactor(client)
    client.post(f"/profiles/{p['id']}/chat",
                json={"interactor_id": user, "message": "hi"})
    run = client.post(f"/profiles/{p['id']}/finetune").json()
    assert run["sealed_in_vault"] is False
    assert run["external_transmission"] is False
