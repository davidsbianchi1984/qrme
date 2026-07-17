"""JIM-mini / Guardian tandem-layer tests."""

from qrme import conditions
from tests.conftest import ADULT_VERIFICATION


def _make_specialist(client, condition, name):
    """Create a QRME fictional profile and register it as a condition specialist."""
    profile = client.post(
        "/profiles",
        json={
            "owner_id": "clinic",
            "kind": "fictional",
            "display_name": name,
            "persona": f"A calm, evidence-based {name} who supports people kindly.",
            "verification": ADULT_VERIFICATION,
        },
    ).json()
    reg = client.post(
        "/guardian/specialists",
        json={"condition": condition, "profile_id": profile["id"]},
    )
    assert reg.status_code == 200, reg.text
    return profile["id"]


def _enroll(client, interactor_id, **extra):
    body = {"terms_consent": True, "resting_heart_rate": 65}
    body.update(extra)
    r = client.post(f"/guardian/enroll/{interactor_id}", json=body)
    assert r.status_code == 200, r.text
    return r.json()


# -- condition detection (unit) --------------------------------------------

def test_detect_panic_from_biometrics():
    d = conditions.detect(
        {"heart_rate": 130, "resting_heart_rate": 65, "respiratory_rate": 24}
    )
    assert d is not None and d.condition == conditions.ANXIETY
    assert d.severity in {"guidance", "critical"}


def test_detect_low_blood_oxygen_is_critical():
    d = conditions.detect({"blood_oxygen": 86})
    assert d.condition == conditions.PHYSICAL_DISTRESS and d.severity == "critical"


def test_detect_financial_stress_from_text():
    d = conditions.detect({}, "I'm broke and can't pay rent, total financial crisis")
    assert d.condition == conditions.FINANCIAL_STRESS


def test_crisis_language_escalates():
    d = conditions.detect({}, "I don't want to live anymore")
    assert d.severity == "critical"


def test_normal_sample_no_detection():
    assert conditions.detect({"heart_rate": 72, "blood_oxygen": 98}) is None


# -- Guardian orchestration (API) ------------------------------------------

def test_enroll_requires_terms_consent(client, interactor_id):
    r = client.post(f"/guardian/enroll/{interactor_id}", json={"terms_consent": False})
    assert r.status_code == 403


def test_monitor_triggers_specialist_and_delivers_guidance(client, interactor_id):
    _make_specialist(client, "anxiety", "Anxiety Specialist")
    _enroll(client, interactor_id)

    r = client.post(
        f"/guardian/monitor/{interactor_id}",
        json={"heart_rate": 128, "respiratory_rate": 22},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["detected"] is True
    assert body["condition"] == "anxiety"
    g = body["guidance"]
    assert g["delivered"] is True
    assert g["specialist_name"] == "Anxiety Specialist"
    # Guidance is conditioned on the monitored situation (claim 6).
    assert "anxiety" in g["content"].lower()


def test_monitor_without_specialist_reports_gap(client, interactor_id):
    _enroll(client, interactor_id)
    body = client.post(
        f"/guardian/monitor/{interactor_id}",
        json={"note": "I'm having a panic attack"},
    ).json()
    assert body["detected"] is True
    assert body["guidance"]["delivered"] is False
    assert "no specialist" in body["guidance"]["reason"]


def test_critical_event_escalates_to_emergency_contact(client, interactor_id):
    _make_specialist(client, "physical_distress", "First Aid Guide")
    _enroll(
        client, interactor_id,
        emergency_name="Alex", emergency_phone="+1-555-0100", contact_consent=True,
    )
    body = client.post(
        f"/guardian/monitor/{interactor_id}", json={"blood_oxygen": 85}
    ).json()
    assert body["severity"] == "critical"
    esc = body["escalation"]
    assert esc["escalated"] is True
    assert esc["notified_emergency_contact"] is True
    assert esc["emergency_contact"]["name"] == "Alex"


def test_monitor_requires_enrollment(client, interactor_id):
    r = client.post(f"/guardian/monitor/{interactor_id}", json={"heart_rate": 130})
    assert r.status_code == 409


def test_event_timeline_records_the_loop(client, interactor_id):
    _make_specialist(client, "anxiety", "Anxiety Specialist")
    _enroll(client, interactor_id)
    client.post(
        f"/guardian/monitor/{interactor_id}",
        json={"heart_rate": 150, "respiratory_rate": 26},
    )
    events = client.get(f"/guardian/events/{interactor_id}").json()
    types = [e["type"] for e in events]
    assert "biometric" in types
    assert "detection" in types
    assert "guidance" in types
    assert "escalation" in types  # +85 over resting => critical
