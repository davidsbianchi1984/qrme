"""The weekly letter: a profile's week, written to its owner
(qrme/letter.py).

JIM's letter told a person what their own numbers meant; this is the
twin turned toward custody: the messages exchanged, the moments sealed,
the studies taken and what the watching noticed, as a deterministic
digest the profile's own provider turns into prose — the voice that
speaks all week is the voice that reports on it.

    asked     what kind of week did the profile have
    mattered  an account rendered only on request is an account withheld
"""

from __future__ import annotations

import json

from qrme import lookout

from tests.test_the_profile_keeps_itself_current import (StandingVault,
                                                         _allow_study,
                                                         _plant)
from tests.test_the_profile_remembers_by_meaning import _chat
from tests.test_the_voice_inside_the_vault import VoiceVault, _choose_vault


def test_the_letter_holds_the_week_and_only_the_week(client, profile_id,
                                                     interactor_id):
    answered = _chat(client, profile_id, interactor_id, "hello there")
    assert answered["profile_message"]["content"]

    r = client.post(f"/profiles/{profile_id}/letter")
    assert r.status_code == 201, r.text
    letter = r.json()
    assert letter["described_by"] == "digest"
    assert any("message" in line for line in letter["digest"])
    assert letter["week_start"]

    shelf = client.get(f"/profiles/{profile_id}/letters").json()
    assert len(shelf) == 1 and shelf[0]["body"] == letter["body"]
    assert shelf[0]["digest"]


def test_an_empty_week_gets_no_letter(client, profile_id):
    r = client.post(f"/profiles/{profile_id}/letter")
    assert r.status_code == 422
    assert "an empty week writes no letter" in r.text


def test_the_watching_reaches_the_letter(client, profile_id):
    vault = StandingVault()
    client.app.state.pdi = vault
    _allow_study(profile_id)
    planted = _plant(client, profile_id)
    vault.records[lookout.capture_key(planted["task_id"])] = json.dumps(
        {"url": "https://example.com/menu", "text": "words",
         "fetched_at": "2999-01-01T09:00:00+00:00",
         "changed_at": "2999-01-01T09:00:00+00:00"})
    r = client.post(f"/profiles/{profile_id}/letter")
    assert r.status_code == 201, r.text
    assert any(
        "watched page https://example.com/menu changed on 2999-01-01" == line
        for line in r.json()["digest"])


def test_the_chosen_voice_writes_the_letter(client, profile_id,
                                            interactor_id):
    """The voice that speaks all week is the voice that reports on it:
    a vault-voiced profile's letter is written by the resident, and
    described_by says a model wrote it."""
    vault = VoiceVault(text="A quiet week, mostly catching up.")
    client.app.state.pdi = vault
    _choose_vault(client, profile_id)
    _chat(client, profile_id, interactor_id, "hello there")

    r = client.post(f"/profiles/{profile_id}/letter")
    assert r.status_code == 201, r.text
    letter = r.json()
    assert letter["described_by"] == "model"
    assert letter["body"] == "A quiet week, mostly catching up."
