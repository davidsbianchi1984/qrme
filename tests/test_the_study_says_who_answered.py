"""The study says who answered.

The excursion row was already the audit trail for what could have left —
the sanitized brief, the redaction count, `left_host`. What it could not
say was who wrote what came back: a study whose model degraded to the
stub, or whose vault turned out to be an older tandem, was recorded
exactly like one the chosen model answered.

    asked     which model was this study sent to
    mattered  which model actually wrote these findings

`answered_by` closes that gap with the letter's own honesty rules: the
name on the record is whoever wrote the words — the model's registry
name, `vault` for the resident, `local fallback` for a degrade, `stub`
for the local provider asked directly — read from the request-scoped
record the provenance stamp trusts, never from the choice that was
asked for.
"""

from __future__ import annotations

from qrme import llm

from tests.test_the_voice_inside_the_vault import (DoorlessVault, VoiceVault,
                                                   _choose_vault)


def _study(client, profile_id):
    r = client.post(f"/profiles/{profile_id}/excursions", json={
        "topic": "hydration",
        "question": "how much water does an older adult need daily",
    })
    assert r.status_code == 201, r.text
    return r.json()


class _Speaks:
    def generate(self, system, messages):
        return "General notes on the topic."


class _Refuses:
    def generate(self, system, messages):
        raise RuntimeError("expired key")


def test_the_local_study_is_named_stub(client, profile_id):
    """No cloud, no keys: the deterministic provider answers, and the
    record names it as itself rather than leaving the reader to guess."""
    exc = _study(client, profile_id)
    assert exc["answered_by"] == "stub"
    listed = client.get(f"/profiles/{profile_id}/excursions").json()
    assert listed[-1]["answered_by"] == "stub"


def test_a_models_study_carries_the_models_name(client, profile_id,
                                                monkeypatch):
    provider = llm.FallbackProvider("anthropic", _Speaks(),
                                    llm.StubProvider())
    monkeypatch.setattr(llm, "get_provider", lambda *a, **k: provider)
    exc = _study(client, profile_id)
    assert exc["answered_by"] == "anthropic"


def test_a_degraded_study_is_not_dressed_as_the_model(client, profile_id,
                                                      monkeypatch):
    """The point of the round: an expired key used to leave a row
    indistinguishable from one the chosen model wrote. The record now
    says the fallback answered, in the fallback's own name."""
    provider = llm.FallbackProvider("anthropic", _Refuses(),
                                    llm.StubProvider())
    monkeypatch.setattr(llm, "get_provider", lambda *a, **k: provider)
    exc = _study(client, profile_id)
    assert exc["answered_by"] == llm.LOCAL_FALLBACK
    assert exc["findings"], "the degrade still brought findings home"


def test_the_vault_study_is_named_vault(client, profile_id):
    client.app.state.pdi = VoiceVault(text="Notes made inside the facility.")
    _choose_vault(client, profile_id)
    exc = _study(client, profile_id)
    assert exc["answered_by"] == "vault"
    assert exc["left_host"] is False


def test_an_older_tandem_is_not_dressed_as_the_vault(client, profile_id):
    """A doorless PDI falls to the local provider — and the record calls
    that the degrade it is, never the vault the owner chose."""
    client.app.state.pdi = DoorlessVault()
    _choose_vault(client, profile_id)
    exc = _study(client, profile_id)
    assert exc["answered_by"] == llm.LOCAL_FALLBACK


def test_an_earlier_note_does_not_describe_this_study(client, profile_id):
    """The record is cleared before the gather and put back after: a
    degrade noted earlier on the same context must not be written down
    as this study's author."""
    llm.note_answered_by("anthropic")
    try:
        exc = _study(client, profile_id)
    finally:
        llm.clear_answered_by()
    assert exc["answered_by"] == "stub"
