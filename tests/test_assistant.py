"""Assistant & perception: triage/curation, proofreading, real-time
perception with hands-free guidance, and original creative composition."""

from tests.test_capabilities import make_profile


def test_triage_keeps_the_best(client):
    """Curate a large pile down to the best N."""
    p = make_profile(client)
    items = [{"id": f"e{i}", "text": "ok"} for i in range(20)]
    items += [
        {"id": "star1", "text": "Led and delivered the launch that grew "
                                 "revenue and won an award for results"},
        {"id": "star2", "text": "Built and shipped the platform; promoted "
                                 "after I solved the scaling problem"},
    ]
    r = client.post(f"/profiles/{p['id']}/assist/triage", json={
        "items": items, "keep": 2, "criteria": "strongest work"}).json()
    assert r["reviewed"] == 22
    kept = {k["id"] for k in r["kept"]}
    assert kept == {"star1", "star2"}
    assert len(r["discarded_ids"]) == 20
    assert all("score" in k["reason"] for k in r["kept"])


def test_proofread_edits_and_suggests(client):
    p = make_profile(client)
    r = client.post(f"/profiles/{p['id']}/assist/proofread", json={
        "text": "  i went to the store and i bought bread  "}).json()
    assert r["status"] == "approved"
    assert r["edited"]
    assert "collapse double spaces" in r["suggestions"]
    assert "trim leading/trailing whitespace" in r["suggestions"]
    assert "capitalize the pronoun 'I'" in r["suggestions"]


def test_perceive_recognizes_scene_and_guides(client):
    """See a real-time scene and guide hands-free."""
    p = make_profile(client)
    r = client.post(f"/profiles/{p['id']}/perceive", json={
        "objects": ["ticket booth", "carousel", "exit sign"],
        "people": ["a child waving"], "gestures": ["waving"],
        "place": "a crowded carnival",
        "goal": "guide me to the exit with my eyes closed"}).json()
    assert r["status"] == "approved"
    assert r["recognized"]["place"] == "a crowded carnival"
    assert r["recognized_count"] == 5           # 3 objects + 1 person + 1 gesture
    assert r["goal"].startswith("guide me")
    assert r["guidance"]

    # Perception without a goal just shares the moment.
    shared = client.post(f"/profiles/{p['id']}/perceive", json={
        "objects": ["the ocean", "a sunset"], "place": "the beach"}).json()
    assert shared["goal"] is None and shared["guidance"]


def test_compose_creative_work(client):
    """An original work capturing a moment, kept as an artifact."""
    p = make_profile(client)
    music = client.post(f"/profiles/{p['id']}/assist/compose", json={
        "kind": "music",
        "moment": "what it feels like to be on the beach with you right now"})
    assert music.status_code == 201
    work = music.json()
    assert work["kind"] == "music" and work["content"]
    assert "beach" in work["moment"]

    client.post(f"/profiles/{p['id']}/assist/compose", json={
        "kind": "poem", "moment": "a photograph of our relationship"})
    works = client.get(f"/profiles/{p['id']}/assist/works").json()
    assert {w["kind"] for w in works} == {"music", "poem"}


def test_assistant_works_purged_on_delete(client):
    p = make_profile(client)
    client.post(f"/profiles/{p['id']}/assist/compose",
                json={"kind": "note", "moment": "our first walk"})
    client.post(f"/profiles/{p['id']}/perceive",
                json={"objects": ["a door"], "goal": "find the door"})
    deleted = client.delete(f"/profiles/{p['id']}").json()["deleted"]
    assert deleted["creative_works"] == 1
    assert deleted["perceptions"] == 1
