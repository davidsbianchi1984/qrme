"""Safe knowledge excursions: the model studies a topic without carrying the
owner's private data out, then brings general knowledge back."""


def _interactor(client):
    r = client.post("/interactors", json={"display_name": "Grandpa Joe",
                                          "birthdate": "1950-01-01"})
    assert r.status_code == 201, r.text
    return r.json()["id"]


def test_brief_is_sanitized(client, profile_id):
    # 'Dana' is the profile's name; relate an interactor whose name must also go.
    iid = _interactor(client)
    client.put(f"/profiles/{profile_id}/relationships/{iid}",
               json={"relationship_type": "family", "nickname": "Gramps"})

    r = client.post(f"/profiles/{profile_id}/excursions", json={
        "topic": "managing arthritis pain",
        "question": "Dana wants tips to help Grandpa Joe with his arthritis.",
    })
    assert r.status_code == 201, r.text
    exc = r.json()
    # The outbound brief carries neither the profile nor the interactor name.
    assert "Dana" not in exc["brief"]
    assert "Grandpa Joe" not in exc["brief"]
    assert "[private]" in exc["brief"]
    assert exc["redactions"] >= 2
    # Findings come back and also carry no private terms (they derive from the
    # sanitized brief).
    assert exc["findings"]
    assert "Dana" not in exc["findings"]
    assert "Grandpa Joe" not in exc["findings"]


def test_caller_marked_private_terms_redacted(client, profile_id):
    r = client.post(f"/profiles/{profile_id}/excursions", json={
        "topic": "budgeting",
        "question": "How to save for a trip to Ardenville with account 55123?",
        "private": ["Ardenville", "55123"],
    })
    exc = r.json()
    assert "Ardenville" not in exc["brief"]
    assert "55123" not in exc["brief"]


def test_nothing_leaves_the_host_by_default(client, profile_id):
    exc = client.post(f"/profiles/{profile_id}/excursions",
                      json={"topic": "sourdough", "question": "how to start a starter"}).json()
    # No cloud attached in the default posture -> the gather ran locally and
    # nothing left the host.
    assert exc["left_host"] is False


def test_offline_gathers_locally(client, profile_id, monkeypatch):
    monkeypatch.setenv("QRME_OFFLINE", "1")
    exc = client.post(f"/profiles/{profile_id}/excursions",
                      json={"topic": "knots", "question": "how to tie a bowline"}).json()
    assert exc["left_host"] is False
    assert exc["findings"]                 # still gathered, on the local model


def test_learn_folds_findings_into_a_source(client, profile_id):
    exc = client.post(f"/profiles/{profile_id}/excursions",
                      json={"topic": "composting", "question": "how to balance a bin"}).json()
    r = client.post(f"/excursions/{exc['id']}/learn")
    assert r.status_code == 201, r.text
    src_id = r.json()["source_id"]

    sources = client.get(f"/profiles/{profile_id}/sources").json()
    learned = [s for s in sources if s["id"] == src_id]
    assert learned and learned[0]["kind"] == "knowledge"
    assert learned[0]["title"] == "Learned: composting"

    # The excursion now shows as learned; learning again is idempotent.
    assert client.get(f"/excursions/{exc['id']}").json()["learned"] is True
    assert client.post(f"/excursions/{exc['id']}/learn").json()["already_learned"] is True
