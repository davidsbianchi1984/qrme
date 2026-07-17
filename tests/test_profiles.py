from tests.conftest import ADULT_VERIFICATION


def test_create_self_profile(client):
    response = client.post(
        "/profiles",
        json={
            "owner_id": "owner-1",
            "kind": "self",
            "display_name": "Dana",
            "persona": "A retired teacher.",
            "demographics": {"language": "en", "location": "US"},
            "verification": ADULT_VERIFICATION,
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["kind"] == "self"
    assert body["demographics"] == {"language": "en", "location": "US"}


def test_minor_owner_requires_guardian_consent(client):
    payload = {
        "owner_id": "owner-2",
        "kind": "self",
        "display_name": "Kid",
        "persona": "A teenager.",
        "verification": {"birthdate": "2012-01-01"},
    }
    assert client.post("/profiles", json=payload).status_code == 403

    payload["verification"]["guardian_consent"] = True
    assert client.post("/profiles", json=payload).status_code == 201


def test_other_person_profile_requires_consent(client):
    payload = {
        "owner_id": "owner-1",
        "kind": "other_person",
        "display_name": "Grandpa Joe",
        "persona": "A great-grandfather who told long stories.",
        "verification": ADULT_VERIFICATION,
    }
    assert client.post("/profiles", json=payload).status_code == 422

    payload["consent"] = {"basis": "estate_authorization", "attestor": "owner-1"}
    assert client.post("/profiles", json=payload).status_code == 201


def test_adult_mode_requires_adult_owner(client):
    payload = {
        "owner_id": "owner-3",
        "kind": "self",
        "display_name": "Teen",
        "persona": "x",
        "adult_mode": True,
        "verification": {"birthdate": "2012-01-01", "guardian_consent": True},
    }
    assert client.post("/profiles", json=payload).status_code == 403


def test_aging_reports_effective_age(client):
    response = client.post(
        "/profiles",
        json={
            "owner_id": "owner-1",
            "kind": "fictional",
            "display_name": "Ada",
            "persona": "x",
            "aging_enabled": True,
            "base_age": 30,
            "verification": ADULT_VERIFICATION,
        },
    )
    assert response.json()["effective_age"] == 30  # just created
