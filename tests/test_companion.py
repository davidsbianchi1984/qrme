"""Companion features: genesis interview, proactive outreach, honesty about
multiplicity, embodiments, graceful departure."""

from tests.test_capabilities import make_interactor, make_profile, pdi_pair  # noqa: F401

ADULT = {"birthdate": "1984-06-01"}

ANSWERS = {"social_style": "warm but needs quiet evenings",
           "humor": "dry, gentle teasing",
           "what_matters": "honesty and the garden",
           "comfort": "sits with you and listens first"}


def test_genesis_interview_and_self_naming(client):
    r = client.post("/profiles/genesis", json={
        "owner_id": "owner-1", "verification": ADULT, "answers": ANSWERS})
    assert r.status_code == 201
    born = r.json()
    assert born["display_name"]                       # it chose a name
    assert "quiet evenings" in born["persona"]        # interview shaped it
    assert born["purpose"] == "companion_coach"

    # Deterministic: the same answers produce the same self-chosen name.
    again = client.post("/profiles/genesis", json={
        "owner_id": "owner-1", "verification": ADULT, "answers": ANSWERS}).json()
    assert again["display_name"] == born["display_name"]

    # An explicit name is honored instead.
    named = client.post("/profiles/genesis", json={
        "owner_id": "owner-1", "verification": ADULT, "answers": ANSWERS,
        "display_name": "Samantha"}).json()
    assert named["display_name"] == "Samantha"


def test_proactive_requires_owner_opt_in(client):
    reactive = make_profile(client)
    user = make_interactor(client)
    r = client.post(f"/profiles/{reactive['id']}/proactive/{user}")
    assert r.status_code == 403

    willing = make_profile(client, interaction_scope="proactive")
    r = client.post(f"/profiles/{willing['id']}/proactive/{user}")
    assert r.status_code == 200
    body = r.json()
    assert body["message"]["status"] == "approved"
    assert body["message"]["content"]
    # The unprompted message lands in shared memory like any other turn.
    memory = client.get(f"/profiles/{willing['id']}/memory/{user}").json()
    assert len(memory) == 1 and memory[0]["role"] == "profile"


def test_transparency_about_multiplicity(client):
    p = make_profile(client)
    a, b = make_interactor(client, "A"), make_interactor(client, "B")
    for user in (a, b):
        client.post(f"/profiles/{p['id']}/chat",
                    json={"interactor_id": user, "message": "hello"})
    t = client.get(f"/profiles/{p['id']}/transparency").json()
    assert t["active_relationships"] == 2
    assert "truthfully" in t["policy"]


def test_embodiments_including_robots(client):
    p = make_profile(client)
    user = make_interactor(client)
    client.post(f"/profiles/{p['id']}/embodiments", json={
        "name": "companion_bot", "kind": "humanoid", "has_llm": True})
    client.post(f"/profiles/{p['id']}/embodiments", json={
        "name": "earpiece", "kind": "earpiece"})
    listed = client.get(f"/profiles/{p['id']}/embodiments").json()
    assert {e["kind"] for e in listed} == {"humanoid", "earpiece"}

    # Chat can arrive from an embodiment; unknown surfaces still fail.
    ok = client.post(f"/profiles/{p['id']}/chat", json={
        "interactor_id": user, "message": "hi", "surface": "companion_bot"})
    assert ok.status_code == 200
    bad = client.post(f"/profiles/{p['id']}/chat", json={
        "interactor_id": user, "message": "hi", "surface": "toaster"})
    assert bad.status_code == 422


def test_graceful_departure(pdi_pair):
    client, fake = pdi_pair
    p = make_profile(client)
    a, b = make_interactor(client, "A"), make_interactor(client, "B")
    for user in (a, b):
        client.put(f"/profiles/{p['id']}/relationships/{user}",
                   json={"relationship_type": "friend"})
        client.post(f"/profiles/{p['id']}/chat",
                    json={"interactor_id": user, "message": "hey"})

    r = client.post(f"/profiles/{p['id']}/sunset").json()
    assert r["status"] == "departed" and r["farewells"] == 2
    assert r["archive_key"] in fake.store            # archive sealed in PDI

    # Chat closes gently; memory and export remain.
    gone = client.post(f"/profiles/{p['id']}/chat",
                       json={"interactor_id": a, "message": "hello?"})
    assert gone.status_code == 410
    memory = client.get(f"/profiles/{p['id']}/memory/{a}").json()
    assert memory[-1]["role"] == "profile"           # the farewell is there
    assert client.get(f"/profiles/{p['id']}/export").status_code == 200

    # Departing twice is a conflict, not a re-run.
    assert client.post(f"/profiles/{p['id']}/sunset").status_code == 409
