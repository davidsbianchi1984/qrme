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


def test_the_letter_accounts_for_the_asking(client, profile_id):
    client.post(f"/profiles/{profile_id}/privileges/ask_people",
                json={"on": True})
    r = client.post(f"/profiles/{profile_id}/inquiries",
                    json={"topic": "old radiators",
                          "question": "what is this valve called"})
    assert r.status_code == 201, r.text
    inq = r.json()
    posted = client.post(f"/open-questions/{inq['id']}/answers", json={
        "body": "A thermostatic radiator valve."})
    assert posted.status_code == 201, posted.text

    r = client.post(f"/profiles/{profile_id}/letter")
    assert r.status_code == 201, r.text
    digest = r.json()["digest"]
    assert any("1 question asked on the open board" == line
               for line in digest), digest
    assert any("1 answer came back" == line for line in digest), digest


def test_a_network_voice_gets_the_sanitized_digest(client, profile_id,
                                                   monkeypatch):
    """The letter is not the looser door: the study path sanitizes what
    leaves and says that it left, and the letter now keeps the same
    promise. The week's digest names the person the profile talked with
    most; the network model receives that line with the name taken out,
    while the owner's own letter keeps it."""
    from qrme import llm, research

    sam = client.post("/interactors", json={
        "display_name": "Sam", "birthdate": "2000-01-15"}).json()["id"]
    kim = client.post("/interactors", json={
        "display_name": "Kim", "birthdate": "1999-03-03"}).json()["id"]
    _chat(client, profile_id, sam, "hello there")
    _chat(client, profile_id, sam, "hello again")
    _chat(client, profile_id, kim, "hi")

    sent = {}

    class Capture:
        def generate(self, system, messages):
            sent["content"] = messages[0]["content"]
            return "A week, retold without names."

    monkeypatch.setattr(llm, "provider_for_profile",
                        lambda pid, cloud=None: Capture())
    monkeypatch.setattr(llm, "resolve_choice", lambda c: "anthropic")

    r = client.post(f"/profiles/{profile_id}/letter")
    assert r.status_code == 201, r.text
    letter = r.json()
    assert letter["left_host"] is True
    assert letter["redactions"] >= 1
    assert "Sam" not in sent["content"]
    assert research.REDACTION in sent["content"]
    # The owner's own letter keeps the real digest — sanitizing is about
    # what leaves, never about what they may read of their own week.
    assert any("Sam" in line for line in letter["digest"])

    shelf = client.get(f"/profiles/{profile_id}/letters").json()
    assert shelf[0]["left_host"] is True and shelf[0]["redactions"] >= 1


def test_a_voice_that_stays_home_reads_the_full_digest(client, profile_id,
                                                       interactor_id):
    """The vault's voice studies inside: nothing leaves, the digest goes
    whole, and left_host says so — the same word the excursions use."""
    vault = VoiceVault(text="A quiet week.")
    client.app.state.pdi = vault
    _choose_vault(client, profile_id)
    _chat(client, profile_id, interactor_id, "hello there")

    r = client.post(f"/profiles/{profile_id}/letter")
    assert r.status_code == 201, r.text
    letter = r.json()
    assert letter["left_host"] is False and letter["redactions"] == 0
