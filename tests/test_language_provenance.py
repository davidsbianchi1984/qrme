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


# ---- setup gateway, translate mode, and the translate tool ------------------

def test_create_profile_with_language_at_the_gateway(client):
    r = client.post("/profiles", json={
        "owner_id": "owner-1", "kind": "self", "display_name": "Rosa",
        "persona": "A gardener.", "language": "es",
        "verification": {"birthdate": "1984-06-01"}})
    assert r.status_code == 201, r.text
    out = r.json()
    assert out["language"] == "es"
    pref = client.get(f"/profiles/{out['id']}/language").json()
    assert pref["language"] == "es" and pref["mode"] == "pre"


def test_create_profile_rejects_unknown_language(client):
    r = client.post("/profiles", json={
        "owner_id": "owner-1", "kind": "self", "display_name": "Rosa",
        "persona": "A gardener.", "language": "klingon",
        "verification": {"birthdate": "1984-06-01"}})
    assert r.status_code == 422


def test_on_demand_mode_keeps_the_original_voice(client, profile_id):
    from qrme import db, persona
    client.put(f"/profiles/{profile_id}/language",
               json={"language": "fr", "mode": "on_demand"})
    profile = dict(db.connect().execute(
        "SELECT * FROM profiles WHERE id=?", (profile_id,)).fetchone())
    prompt = persona.build_system_prompt(profile, None, None)
    assert "Français" not in prompt      # original voice kept
    client.put(f"/profiles/{profile_id}/language",
               json={"language": "fr", "mode": "pre"})
    prompt = persona.build_system_prompt(profile, None, None)
    assert "Français" in prompt          # pre mode speaks it natively


def test_translate_tool_is_owner_gated_and_stub_honest(client, profile_id):
    client.put(f"/profiles/{profile_id}/language", json={"language": "es"})
    r = client.post(f"/profiles/{profile_id}/translate",
                    json={"text": "a message from a stranger"}).json()
    assert r["engine"] == "stub" and "cannot translate" in r["note"]
    assert r["translation"] == "a message from a stranger"
    # Unknown target refused; missing auth refused.
    r = client.post(f"/profiles/{profile_id}/translate",
                    json={"text": "hi", "to": "xx"})
    assert r.status_code == 422
    r = client.post(f"/profiles/{profile_id}/translate",
                    json={"text": "hi"}, headers={"authorization": ""})
    assert r.status_code in (401, 403)
