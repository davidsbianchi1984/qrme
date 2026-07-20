"""Sustained in-conversation specialist handoff (claim 24): the switch
persists across turns, re-routes when the domain changes, and is torn down
with the conversation."""

from tests.test_capabilities import as_owner, make_interactor, make_profile


def _wire(client):
    """A primary profile with mental-health and finance specialists, plus an
    interactor. Returns (primary, mh_specialist, fin_specialist, user)."""
    primary = make_profile(client)
    mh = make_profile(client, display_name="Dr. Calm",
                      persona="A calm mental-health specialist.")
    fin = make_profile(client, display_name="Ada Ledger",
                       persona="A steady financial counselor.")
    as_owner(client, primary)
    client.put(f"/profiles/{primary['id']}/specialists", json={
        "domain": "mental_health", "specialist_profile_id": mh["id"]})
    client.put(f"/profiles/{primary['id']}/specialists", json={
        "domain": "finance", "specialist_profile_id": fin["id"]})
    return primary, mh, fin, make_interactor(client)


def test_handoff_reroutes_when_domain_changes(client):
    primary, mh, fin, user = _wire(client)
    pid = primary["id"]

    a = client.post(f"/profiles/{pid}/chat", json={
        "interactor_id": user, "message": "i'm panicking",
        "biometrics": {"stress_level": 0.9, "condition": "anxiety"}}).json()
    assert a["handoff"]["specialist_profile_id"] == mh["id"]
    assert a["handoff"]["state"] == "engaged"

    # A new domain signal re-routes to the finance specialist — a fresh
    # engagement, not a stale sustain.
    b = client.post(f"/profiles/{pid}/chat", json={
        "interactor_id": user, "message": "and i'm broke",
        "biometrics": {"condition": "financial_stress"}}).json()
    assert b["handoff"]["specialist_profile_id"] == fin["id"]
    assert b["handoff"]["domain"] == "finance"
    assert b["handoff"]["state"] == "engaged"


def test_handoff_is_per_interactor(client):
    primary, mh, fin, user = _wire(client)
    other = make_interactor(client, name="Ben")
    pid = primary["id"]

    client.post(f"/profiles/{pid}/chat", json={
        "interactor_id": user, "message": "too much",
        "biometrics": {"stress_level": 0.9, "condition": "anxiety"}})
    # A different interactor is unaffected — no handoff leaks across people.
    fresh = client.post(f"/profiles/{pid}/chat", json={
        "interactor_id": other, "message": "hi there"}).json()
    assert fresh["handoff"] is None


def test_clearing_memory_ends_the_handoff(client):
    primary, mh, fin, user = _wire(client)
    pid = primary["id"]

    client.post(f"/profiles/{pid}/chat", json={
        "interactor_id": user, "message": "overwhelmed",
        "biometrics": {"stress_level": 0.9, "condition": "anxiety"}})
    as_owner(client, primary)
    assert client.delete(
        f"/profiles/{pid}/memory/{user}").status_code == 204

    # With the conversation wiped, the next turn starts fresh as the profile.
    after = client.post(f"/profiles/{pid}/chat", json={
        "interactor_id": user, "message": "hello again"}).json()
    assert after["handoff"] is None
