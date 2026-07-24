"""The steering hub: one surface for everything the owner shapes — the
tone/pace/manner dials, the profile's age, and its appearance. The
dedicated features still stand alone; the hub composes them."""

from qrme import db, persona

ADULT = {"birthdate": "1984-06-01"}


def _profile(client, adult_mode=False, base_age=None):
    body = {"owner_id": "owner-1", "kind": "fictional", "display_name": "Ava",
            "persona": "A studio persona.", "adult_mode": adult_mode,
            "maturity": "open" if adult_mode else "balanced",
            "verification": ADULT}
    if base_age is not None:
        body["base_age"] = base_age
    r = client.post("/profiles", json=body)
    out = r.json()
    client.headers["authorization"] = f"Bearer {out['owner_token']}"
    return out["id"]


def _prompt(pid):
    profile = dict(db.connect().execute(
        "SELECT * FROM profiles WHERE id=?", (pid,)).fetchone())
    return persona.build_system_prompt(profile, None, None)


def test_hub_gathers_dials_age_and_appearance(client):
    pid = _profile(client, base_age=30)
    hub = client.get(f"/profiles/{pid}/steering/hub").json()
    assert {d["name"] for d in hub["dials"]} >= {"pace", "warmth", "humor"}
    assert hub["age"] == {"base_age": 30, "aging_enabled": False,
                          "effective_age": 30}
    assert hub["appearance"] == {"description": "", "demographics": {}}


def test_hub_sets_every_section_and_they_ride_the_prompt(client):
    pid = _profile(client, base_age=25)
    r = client.put(f"/profiles/{pid}/steering/hub", json={
        "values": {"pace": 90, "warmth": 85},
        "age": {"base_age": 41, "aging_enabled": True},
        "appearance": {"description": "silver-haired, tailored navy suit",
                       "demographics": {"build": "tall"}}})
    assert r.status_code == 200, r.text
    hub = r.json()
    assert hub["values"]["pace"] == 90
    assert hub["age"]["base_age"] == 41 and hub["age"]["aging_enabled"] is True
    assert hub["age"]["effective_age"] >= 41
    assert "silver-haired" in hub["appearance"]["description"]
    assert hub["appearance"]["demographics"] == {"build": "tall"}

    prompt = _prompt(pid)
    assert "Your current steering" in prompt        # dials
    assert "Pace: lean toward fast" in prompt
    assert "silver-haired, tailored navy suit" in prompt  # appearance
    assert "41 years old" in prompt or "years old" in prompt


def test_hub_partial_update_leaves_the_rest(client):
    pid = _profile(client, base_age=30)
    client.put(f"/profiles/{pid}/steering/hub",
               json={"appearance": {"description": "freckled, red curls"}})
    hub = client.get(f"/profiles/{pid}/steering/hub").json()
    # Appearance set, age untouched, dials still neutral.
    assert hub["appearance"]["description"] == "freckled, red curls"
    assert hub["age"]["base_age"] == 30
    assert all(v == 50 for v in hub["values"].values())


def test_hub_respects_the_intimacy_gate(client):
    pid = _profile(client, adult_mode=False)
    # No intimacy dial for a non-adult profile, and it can't be raised.
    hub = client.get(f"/profiles/{pid}/steering/hub").json()
    assert all(d["name"] != "intimacy" for d in hub["dials"])
    r = client.put(f"/profiles/{pid}/steering/hub",
                   json={"values": {"intimacy": 100}}).json()
    assert r["values"]["intimacy"] == 0


def test_hub_rejects_bad_age_and_is_owner_only(client):
    pid = _profile(client)
    assert client.put(f"/profiles/{pid}/steering/hub",
                      json={"age": {"base_age": -5}}).status_code == 422
    r = client.get(f"/profiles/{pid}/steering/hub",
                   headers={"authorization": ""})
    assert r.status_code in (401, 403)


def test_dedicated_dials_endpoint_still_works(client):
    # The hub composes; the standalone steering endpoint is unchanged.
    pid = _profile(client)
    client.put(f"/profiles/{pid}/steering", json={"values": {"humor": 10}})
    assert client.get(f"/profiles/{pid}/steering"
                      ).json()["values"]["humor"] == 10
    assert client.get(f"/profiles/{pid}/steering/hub"
                      ).json()["values"]["humor"] == 10
