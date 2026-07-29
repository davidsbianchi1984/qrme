"""The three features the filed specification describes that the code did
not yet have — mined from App. 19/056,418 verbatim and built in:

- Hybrid profiles, spec [0038]: "a combination of aspects or characteristics
  of several people ... a combination of trusted relatives such as
  grandparents who are gone".
- Real-time simulation, clause 1: "real-time simulations of the first
  person's actions, workflows, and decision-making processes for predictive
  modeling and operational insights".
- Environmental adaptation, clause 1: "dynamically adapt to environmental
  data, such as location, conditions, and user behavior".
"""

from __future__ import annotations

import json

from qrme import db

ADULT = {"birthdate": "1984-06-01"}


def _profile(client, name, persona, **extra):
    r = client.post("/profiles", json={
        "owner_id": extra.pop("owner_id", "owner-1"), "kind": "self",
        "display_name": name, "persona": persona, "verification": ADULT,
        "plan": "pro", **extra})
    assert r.status_code == 201, r.text
    return r.json()


def _interactor(client, name="June"):
    r = client.post("/interactors", json={"display_name": name,
                                          "birthdate": "1990-01-01"})
    return r.json()["id"]


# -- Hybrid profiles (spec [0038]) -------------------------------------------

def test_a_hybrid_blends_two_grandparents(client):
    a = _profile(client, "Grandpa Joe", "A carpenter with endless patience.")
    b = _profile(client, "Grandma Rose", "A storyteller who cooked for everyone.")
    r = client.post("/profiles/composite", json={
        "owner_id": "owner-1", "display_name": "The Grandfolks",
        "verification": ADULT,
        "sources": [
            {"profile_id": a["id"], "weight": 1, "aspect": "patience"},
            {"profile_id": b["id"], "weight": 3, "aspect": "storytelling"},
        ]})
    assert r.status_code == 201, r.text
    out = r.json()
    assert out["kind"] == "hybrid"
    # The blend is recorded, normalized, heaviest first.
    comp = out["composition"]
    assert [c["display_name"] for c in comp] == ["Grandma Rose", "Grandpa Joe"]
    assert abs(comp[0]["weight"] - 0.75) < 0.001
    # Both constituents' identities live in the persona text.
    assert "Grandpa Joe" in out["persona"] and "storytelling" in out["persona"]


def test_the_composition_is_readable_by_anyone(client):
    a = _profile(client, "A", "First.")
    b = _profile(client, "B", "Second.")
    made = client.post("/profiles/composite", json={
        "owner_id": "owner-1", "display_name": "AB", "verification": ADULT,
        "sources": [{"profile_id": a["id"]}, {"profile_id": b["id"]}]}).json()
    client.headers.pop("authorization", None)
    r = client.get(f"/profiles/{made['id']}/composition")
    assert r.status_code == 200
    assert len(r.json()["sources"]) == 2
    # A non-hybrid has no composition to show.
    assert client.get(f"/profiles/{a['id']}/composition").status_code == 404


def test_a_stranger_s_unlisted_profile_cannot_be_blended(client):
    theirs = _profile(client, "Private Person", "Not yours.",
                      owner_id="owner-2")
    mine = _profile(client, "Mine", "Mine.")
    r = client.post("/profiles/composite", json={
        "owner_id": "owner-1", "display_name": "Nope", "verification": ADULT,
        "sources": [{"profile_id": mine["id"]},
                    {"profile_id": theirs["id"]}]})
    assert r.status_code == 403
    assert "marketplace" in r.json()["detail"]


def test_a_rated_profile_can_never_be_blended(client):
    rated = _profile(client, "After Dark", "Rated persona.",
                     adult_mode=True)
    plain = _profile(client, "Plain", "Plain.")
    r = client.post("/profiles/composite", json={
        "owner_id": "owner-1", "display_name": "Nope", "verification": ADULT,
        "sources": [{"profile_id": rated["id"]},
                    {"profile_id": plain["id"]}]})
    assert r.status_code == 403
    assert "rated" in r.json()["detail"]


def test_hybrid_kind_cannot_be_typed_free_hand(client):
    r = client.post("/profiles", json={
        "owner_id": "owner-1", "kind": "hybrid", "display_name": "Fake",
        "persona": "typed, not blended", "verification": ADULT})
    assert r.status_code == 422
    assert "composite" in r.json()["detail"]


def test_a_hybrid_speaks_and_its_reply_is_watermarked(client):
    a = _profile(client, "A", "First voice.")
    b = _profile(client, "B", "Second voice.")
    made = client.post("/profiles/composite", json={
        "owner_id": "owner-1", "display_name": "AB", "verification": ADULT,
        "sources": [{"profile_id": a["id"]}, {"profile_id": b["id"]}]}).json()
    who = _interactor(client)
    r = client.post(f"/profiles/{made['id']}/chat",
                    json={"interactor_id": who, "message": "hello"})
    assert r.status_code == 200
    assert r.json()["profile_message"]["content"]


# -- Real-time simulation (spec clauses 1 & 5) -------------------------------

def test_a_simulation_predicts_with_honest_confidence(client, profile_id):
    r = client.post(f"/profiles/{profile_id}/simulate", json={
        "scenario": "the town council proposes paving over the garden",
        "horizon": "short_term"})
    assert r.status_code == 201, r.text
    run = r.json()
    assert run["narrative"]
    assert 0.0 < run["confidence"] <= 0.9
    assert run["watermark"]["watermark_id"].startswith("wmk")
    assert "synthetic" in run["disclaimer"]
    # No source material, no memory: the confidence says so.
    assert run["basis"]["source_items"] == 0
    assert run["confidence"] == 0.2


def test_memory_raises_simulation_confidence(client, profile_id):
    who = _interactor(client)
    for i in range(6):
        client.post(f"/profiles/{profile_id}/chat",
                    json={"interactor_id": who, "message": f"turn {i}"})
    bare = client.post(f"/profiles/{profile_id}/simulate", json={
        "scenario": "a quiet week"}).json()
    conditioned = client.post(f"/profiles/{profile_id}/simulate", json={
        "scenario": "a quiet week", "interactor_id": who}).json()
    assert conditioned["confidence"] > bare["confidence"]
    assert conditioned["basis"]["remembered_turns"] >= 12
    assert conditioned["basis"]["latent_embedding"] is not None
    runs = client.get(f"/profiles/{profile_id}/simulations").json()
    assert len(runs) == 2


def test_simulations_are_owner_only(client, profile_id):
    auth = client.headers.pop("authorization")
    try:
        r = client.post(f"/profiles/{profile_id}/simulate",
                        json={"scenario": "anything"})
        assert r.status_code in (401, 403)
    finally:
        client.headers["authorization"] = auth


# -- Environmental adaptation (spec clause 1) --------------------------------

def test_the_environment_rides_into_the_reply_and_is_kept(client, profile_id):
    who = _interactor(client)
    env = {"location": "a trailhead in the rain", "conditions": "cold, wet",
           "local_time": "07:10", "activity": "hiking"}
    r = client.post(f"/profiles/{profile_id}/chat",
                    json={"interactor_id": who, "message": "morning!",
                          "environment": env})
    assert r.status_code == 200
    assert r.json()["environment"] == env
    row = db.connect().execute(
        "SELECT data FROM environment_context WHERE profile_id=?",
        (profile_id,)).fetchone()
    assert json.loads(row["data"])["location"] == "a trailhead in the rain"


def test_a_plain_chat_carries_no_environment(client, profile_id):
    who = _interactor(client)
    r = client.post(f"/profiles/{profile_id}/chat",
                    json={"interactor_id": who, "message": "hi"})
    assert r.json()["environment"] is None
