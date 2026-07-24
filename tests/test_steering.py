"""Steering: the owner shapes a profile's / robot's presentation with dials.
They shape style/pace/behavior and ride on the persona prompt; intimacy is
18+-only and hard-clamped off elsewhere; robots read their dials as motion
behavior. Owner-only, and never touching identity or the allowlist."""

from qrme import db, persona, steering

ADULT = {"birthdate": "1984-06-01"}


def _profile(client, adult_mode=False):
    r = client.post("/profiles", json={
        "owner_id": "owner-1", "kind": "fictional", "display_name": "Ava",
        "persona": "A studio persona.", "adult_mode": adult_mode,
        "maturity": "open" if adult_mode else "balanced",
        "verification": ADULT})
    out = r.json()
    client.headers["authorization"] = f"Bearer {out['owner_token']}"
    return out["id"]


def _prompt(profile_id):
    profile = dict(db.connect().execute(
        "SELECT * FROM profiles WHERE id=?", (profile_id,)).fetchone())
    return persona.build_system_prompt(profile, None, None)


def test_steering_defaults_to_neutral_and_say_nothing(client):
    pid = _profile(client)
    r = client.get(f"/profiles/{pid}/steering").json()
    assert all(v == 50 for v in r["values"].values())
    assert {d["name"] for d in r["dials"]} >= {
        "pace", "autonomy", "verbosity", "warmth", "formality", "humor",
        "assertiveness"}
    # No intimacy dial on a non-adult profile.
    assert all(d["name"] != "intimacy" for d in r["dials"])
    assert "Your current steering" not in _prompt(pid)   # neutral = silent


def test_sliders_shape_the_persona_prompt(client):
    pid = _profile(client)
    client.put(f"/profiles/{pid}/steering",
               json={"values": {"pace": 90, "humor": 15, "warmth": 80}})
    prompt = _prompt(pid)
    assert "Your current steering" in prompt
    assert "Pace: lean toward fast" in prompt
    assert "Humor: lean toward serious" in prompt
    assert "Warmth: lean toward warm" in prompt
    # A mid-band dial stays silent.
    assert "Formality" not in prompt
    # Clamped to range.
    client.put(f"/profiles/{pid}/steering", json={"values": {"pace": 999}})
    assert client.get(f"/profiles/{pid}/steering").json()["values"]["pace"] == 100


def test_intimacy_is_18plus_only(client):
    # Non-adult profile: dial absent, and any attempt is clamped to 0.
    pid = _profile(client, adult_mode=False)
    assert "intimacy" not in [d["name"]
                              for d in client.get(f"/profiles/{pid}/steering"
                                                  ).json()["dials"]]
    r = client.put(f"/profiles/{pid}/steering",
                   json={"values": {"intimacy": 100}}).json()
    assert r["values"]["intimacy"] == 0
    assert "Intimacy" not in _prompt(pid)

    # Adult-mode profile: dial present and effective, within boundaries.
    apid = _profile(client, adult_mode=True)
    idials = {d["name"]: d for d in client.get(f"/profiles/{apid}/steering"
                                               ).json()["dials"]}
    assert idials["intimacy"]["adult_only"] is True
    client.put(f"/profiles/{apid}/steering", json={"values": {"intimacy": 90}})
    prompt = _prompt(apid)
    assert "Intimacy is dialed up" in prompt
    assert "within your stated boundaries" in prompt
    assert "never explicit" in prompt


def test_robot_dials_map_to_a_behavior_profile(client):
    pid = _profile(client)
    robot = client.post(f"/profiles/{pid}/robots",
                        json={"model": "neo"}).json()["id"]
    r = client.get(f"/robots/{robot}/steering").json()
    # A robot is dialed on pace/autonomy/behavior — never intimacy.
    assert all(d["group"] != "intimacy" for d in r["dials"])
    out = client.put(f"/robots/{robot}/steering",
                     json={"values": {"pace": 80, "autonomy": 20,
                                      "assertiveness": 70,
                                      "intimacy": 100}}).json()
    prof = out["behavior_profile"]
    assert prof["motion_eagerness"] == 80 and prof["initiative"] == 20
    assert prof["firmness"] == 70
    assert "intimacy" not in out["values"] or out["values"].get("intimacy") == 0
    # Profile and robot dials are independent subjects.
    assert steering.get(pid)["pace"] == 50


def test_watch_shows_the_live_throttle(client):
    pid = _profile(client)
    client.put(f"/profiles/{pid}/steering",
               json={"values": {"pace": 85, "autonomy": 40}})
    face = client.get(f"/profiles/{pid}/watch").json()
    assert face["profile"]["throttle"] == {"pace": 85, "autonomy": 40}


def test_steering_is_owner_only(client, profile_id):
    r = client.put(f"/profiles/{profile_id}/steering",
                   json={"values": {"pace": 90}},
                   headers={"authorization": ""})
    assert r.status_code in (401, 403)
