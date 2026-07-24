"""Per-profile language + content provenance.

A profile speaks its owner-set language on every surface (the directive rides
on the persona system prompt, so chat, compose, rooms, and robot speech all
inherit it), and every piece of persona-generated content — chat replies,
composed posts — carries its derivation trail: which model produced it,
what it was grounded in, any licensed lineage, and the moderation verdict.
"""


def test_language_catalog_and_choice(client, profile_id):
    cat = client.get("/languages").json()
    assert cat["default"] == "en"
    assert any(l["code"] == "es" and l["label"] == "Español"
               for l in cat["languages"])

    assert client.get(
        f"/profiles/{profile_id}/language").json()["language"] == "en"
    r = client.put(f"/profiles/{profile_id}/language",
                   json={"language": "klingon"})
    assert r.status_code == 422
    r = client.put(f"/profiles/{profile_id}/language",
                   json={"language": "es"}).json()
    assert r["language"] == "es"
    assert client.get(
        f"/profiles/{profile_id}/language").json()["label"] == "Español"


def test_language_rides_on_the_persona_prompt(client, profile_id):
    from qrme import db, persona
    client.put(f"/profiles/{profile_id}/language", json={"language": "fr"})
    profile = dict(db.connect().execute(
        "SELECT * FROM profiles WHERE id=?", (profile_id,)).fetchone())
    prompt = persona.build_system_prompt(profile, None, None)
    # Every surface that builds a system prompt through persona inherits it.
    assert "Français" in prompt


def test_chat_reply_carries_provenance(client, profile_id, interactor_id):
    r = client.post(f"/profiles/{profile_id}/chat",
                    json={"interactor_id": interactor_id,
                          "message": "hello there"}).json()
    p = r["provenance"]
    assert p["generated_by"]
    assert p["grounded_in"]["persona"] is True
    assert p["moderation"]["status"]
    assert p["licensed_from"] is None      # original persona, no lineage
    assert "character speaking" in p["disclaimer"]


def test_compose_carries_provenance_with_grounding_counts(client, profile_id):
    client.post(f"/profiles/{profile_id}/sources",
                json={"kind": "writing", "title": "garden notes",
                      "content": "I love tomatoes."})
    r = client.post(f"/profiles/{profile_id}/compose",
                    json={"topic": "spring planting"}).json()
    p = r["provenance"]
    assert p["grounded_in"]["source_items"] >= 1
    assert p["grounded_in"]["by_kind"].get("writing", 0) >= 1
    assert p["moderation"]["status"] in ("approved", "pending")
    assert p["language"] == "en"
