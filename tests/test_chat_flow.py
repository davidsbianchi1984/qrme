from tests.conftest import ADULT_VERIFICATION


def test_chat_reply_is_relationship_aware(client, profile_id, interactor_id):
    client.put(
        f"/profiles/{profile_id}/relationships/{interactor_id}",
        json={
            "relationship_type": "grandchild",
            "nickname": "kiddo",
            "tone": "playful",
        },
    )
    response = client.post(
        f"/profiles/{profile_id}/chat",
        json={"interactor_id": interactor_id, "message": "Tell me about your garden!"},
    )
    assert response.status_code == 200
    reply = response.json()["profile_message"]
    assert reply["status"] == "approved"
    assert "kiddo" in reply["content"]      # nickname from relationship config
    assert "playful" in reply["content"]    # tone hint reached the provider


def test_memory_persists_and_can_be_cleared(client, profile_id, interactor_id):
    for text in ["Hi!", "Remember me?"]:
        client.post(
            f"/profiles/{profile_id}/chat",
            json={"interactor_id": interactor_id, "message": text},
        )
    memory = client.get(f"/profiles/{profile_id}/memory/{interactor_id}").json()
    assert len(memory) == 4  # two interactor turns + two profile replies

    assert (
        client.delete(f"/profiles/{profile_id}/memory/{interactor_id}").status_code
        == 204
    )
    assert client.get(f"/profiles/{profile_id}/memory/{interactor_id}").json() == []


def test_engagement_tracks_messages_and_feedback(client, profile_id, interactor_id):
    client.post(
        f"/profiles/{profile_id}/chat",
        json={"interactor_id": interactor_id, "message": "Hello there"},
    )
    before = client.get(
        f"/profiles/{profile_id}/engagement/{interactor_id}"
    ).json()
    assert before["interactions"] == 1

    client.post(
        f"/profiles/{profile_id}/interactions/{interactor_id}/feedback",
        json={"rating": "up"},
    )
    after = client.get(f"/profiles/{profile_id}/engagement/{interactor_id}").json()
    assert after["feedback_pos"] == 1
    assert after["score"] > before["score"]


def test_adult_mode_gates_minor_interactors(client):
    profile = client.post(
        "/profiles",
        json={
            "owner_id": "owner-1",
            "kind": "self",
            "display_name": "Adult Persona",
            "persona": "x",
            "adult_mode": True,
            "verification": ADULT_VERIFICATION,
        },
    ).json()
    minor = client.post(
        "/interactors", json={"display_name": "Teen", "birthdate": "2013-05-05"}
    ).json()
    response = client.post(
        f"/profiles/{profile['id']}/chat",
        json={"interactor_id": minor["id"], "message": "hi"},
    )
    assert response.status_code == 403
