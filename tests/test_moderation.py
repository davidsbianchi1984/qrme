from qrme import moderation
from tests.conftest import ADULT_VERIFICATION


def test_deny_pattern_is_flagged():
    verdict = moderation.review(
        "Sure, just send me your social security number.",
        relationship=None,
        interactor={"birthdate": None},
    )
    assert not verdict.approved
    assert "sensitive" in verdict.reason


def test_relationship_boundary_topics_are_flagged():
    relationship = {"boundaries": '["politics"]'}
    verdict = moderation.review(
        "Let me tell you my views on politics.",
        relationship=relationship,
        interactor={"birthdate": None},
    )
    assert not verdict.approved
    assert "politics" in verdict.reason


def test_manual_mode_holds_replies_for_owner_approval(client, interactor_id):
    profile = client.post(
        "/profiles",
        json={
            "owner_id": "owner-1",
            "kind": "self",
            "display_name": "Careful Carl",
            "persona": "x",
            "moderation_mode": "manual",
            "verification": ADULT_VERIFICATION,
        },
    ).json()
    client.headers["authorization"] = f"Bearer {profile['owner_token']}"

    response = client.post(
        f"/profiles/{profile['id']}/chat",
        json={"interactor_id": interactor_id, "message": "hello"},
    )
    reply = response.json()["profile_message"]
    assert reply["status"] == "pending"
    assert reply["content"] is None  # held content is hidden from interactors

    queue = client.get(f"/profiles/{profile['id']}/moderation/queue").json()
    assert len(queue) == 1
    assert queue[0]["content"]  # the owner sees the held content

    approved = client.post(f"/moderation/{queue[0]['id']}/approve").json()
    assert approved["status"] == "approved"

    memory = client.get(
        f"/profiles/{profile['id']}/memory/{interactor_id}"
    ).json()
    profile_msgs = [m for m in memory if m["role"] == "profile"]
    assert profile_msgs[0]["status"] == "approved"
    assert profile_msgs[0]["content"] is not None


def test_rejecting_a_pending_message(client, interactor_id):
    profile = client.post(
        "/profiles",
        json={
            "owner_id": "owner-1",
            "kind": "self",
            "display_name": "Careful Carla",
            "persona": "x",
            "moderation_mode": "manual",
            "verification": ADULT_VERIFICATION,
        },
    ).json()
    client.headers["authorization"] = f"Bearer {profile['owner_token']}"
    client.post(
        f"/profiles/{profile['id']}/chat",
        json={"interactor_id": interactor_id, "message": "hello"},
    )
    queue = client.get(f"/profiles/{profile['id']}/moderation/queue").json()
    rejected = client.post(f"/moderation/{queue[0]['id']}/reject").json()
    assert rejected["status"] == "rejected"

    # A resolved message can't be re-resolved.
    assert client.post(f"/moderation/{queue[0]['id']}/approve").status_code == 409
