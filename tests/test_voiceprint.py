"""Voice cloning, in the order FIG. 800 draws it: permission, then collection,
then the characteristics, then the print.

The figure's first box is a permission gate, and that ordering is the whole
design — so these tests hold the gate load-bearing: nothing is collected
without consent, no voice is learned on somebody else's behalf, nothing
leaves unmarked, and withdrawal actually removes what was gathered.
"""

from qrme import voiceprint


def _consent(client, profile_id, **kw):
    body = {"own_voice": True, "sources": ["call", "voice_note"], **kw}
    return client.put(f"/profiles/{profile_id}/voiceprint/consent", json=body)


def _enroll(client, profile_id, n=3, seconds=45.0):
    for _ in range(n):
        r = client.post(f"/profiles/{profile_id}/voiceprint/samples",
                        json={"source": "call", "seconds": seconds, "turns": 12,
                              "transcript_chars": 600})
        assert r.status_code == 201, r.text
    return r.json()


def test_nothing_is_collected_before_permission(client, profile_id):
    """FIG. 800 step 802: the gate comes first, and it bites."""
    r = client.post(f"/profiles/{profile_id}/voiceprint/samples",
                    json={"source": "call", "seconds": 30})
    assert r.status_code == 403
    assert "consent" in r.json()["detail"]

    status = client.get(f"/profiles/{profile_id}/voiceprint").json()
    assert status["consent"]["granted"] is False
    assert status["voiceprint"] is None


def test_qrme_will_not_learn_someone_elses_voice(client, profile_id):
    r = _consent(client, profile_id, own_voice=False)
    assert r.status_code == 422
    assert "your own" in r.json()["detail"]


def test_consent_is_scoped_to_the_sources_it_named(client, profile_id):
    _consent(client, profile_id, sources=["voice_note"])
    r = client.post(f"/profiles/{profile_id}/voiceprint/samples",
                    json={"source": "call", "seconds": 30})
    assert r.status_code == 403
    assert "not call" in r.json()["detail"]
    # The source it did name works.
    assert client.post(f"/profiles/{profile_id}/voiceprint/samples",
                       json={"source": "voice_note", "seconds": 30}
                       ).status_code == 201


def test_the_characteristics_are_counted_not_scored(client, profile_id):
    """Step 810, made auditable: the analysis is arithmetic a person can
    check, and a thin enrollment is called thin."""
    _consent(client, profile_id)
    thin = client.post(f"/profiles/{profile_id}/voiceprint/samples",
                       json={"source": "call", "seconds": 20.0, "turns": 10,
                             "transcript_chars": 400}).json()
    assert thin["samples"] == 1 and thin["seconds"] == 20.0
    assert thin["mean_turn_seconds"] == 2.0
    assert thin["ready"] is False and thin["needs"]
    assert "no opaque score" in thin["method"]

    r = client.post(f"/profiles/{profile_id}/voiceprint", json={})
    assert r.status_code == 422 and "not enough" in r.json()["detail"]


def test_a_full_enrollment_mints_a_print(client, profile_id):
    _consent(client, profile_id)
    facts = _enroll(client, profile_id)
    assert facts["ready"] is True and facts["by_source"]["call"] == 3

    built = client.post(f"/profiles/{profile_id}/voiceprint", json={}).json()
    assert built["voiceprint"]["active"] is True
    assert built["enrollment"]["seconds"] == 135.0


def test_speaking_always_carries_the_mark_and_the_disclosure(client, profile_id):
    _consent(client, profile_id)
    _enroll(client, profile_id)
    client.post(f"/profiles/{profile_id}/voiceprint", json={})

    said = client.post(f"/profiles/{profile_id}/voiceprint/speak",
                       json={"text": "I'm proud of you, kiddo."}).json()
    assert said["watermark"]["watermark_id"].startswith("wmk_")
    assert "not a recording of them" in said["disclosure"]
    assert "owner's own voice" in said["basis"]
    assert said["revocable"] is True


def test_no_print_no_speech(client, profile_id):
    _consent(client, profile_id)
    r = client.post(f"/profiles/{profile_id}/voiceprint/speak",
                    json={"text": "hello"})
    assert r.status_code == 422 and "build one first" in r.json()["detail"]


def test_withdrawal_deletes_the_samples_and_retires_the_print(client, profile_id):
    _consent(client, profile_id)
    _enroll(client, profile_id)
    client.post(f"/profiles/{profile_id}/voiceprint", json={})

    out = client.delete(f"/profiles/{profile_id}/voiceprint").json()
    assert out["revoked"] is True and out["samples_deleted"] == 3

    status = client.get(f"/profiles/{profile_id}/voiceprint").json()
    assert status["consent"]["granted"] is False
    # The print is a tombstone, not a deletion — the withdrawal is on record.
    assert status["voiceprint"]["active"] is False
    assert status["voiceprint"]["retired_at"]
    # And it will not speak again.
    assert client.post(f"/profiles/{profile_id}/voiceprint/speak",
                       json={"text": "hello"}).status_code == 422


def test_the_gate_is_a_function_anyone_can_read():
    """Unit-level: the refusal messages are the API's own words."""
    assert voiceprint.READY_SAMPLES == 3 and voiceprint.READY_SECONDS == 120.0
    assert voiceprint.SOURCES == ("call", "voice_note", "direct")
    assert "not a recording" in voiceprint.DISCLOSURE
