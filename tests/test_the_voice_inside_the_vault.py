"""The voice inside the vault: a profile that speaks through PDI.

The resident round gave the vault `infer.local` inside plans; PDI 0.88's
`/resident/infer` is the same engine behind a single door, and `vault`
in the provider registry is QRME's side of it: an owner picks "The
vault's local model" on the existing model screen and the profile's
words are generated on the facility's own inference server — the prompt
travels the one authenticated channel every seal uses and goes no
further, and PDI's audit line carries its length, never its words.

    asked     can a profile speak from inside the building
    mattered  does the prompt ever leave it

Honesty rules: a vault with no local model raises rather than speaking
the resident's operational stub sentence in a persona's voice — the
fallback hands the turn to this product's own stub; an older tandem
without the voice door does the same; and with no tandem at all the
choice is simply not configured, so a stored preference can never wedge
generation.
"""

from __future__ import annotations

from qrme import llm

from tests.test_the_profile_remembers_by_meaning import (FakeResidentVault,
                                                         _chat)


class VoiceVault(FakeResidentVault):
    """A tandem with the voice door: records every prompt it was handed."""

    def __init__(self, model="local:llama3.2",
                 text="I remember the lake house fondly."):
        super().__init__()
        self.model, self.text = model, text
        self.prompts: list[str] = []

    def resident_infer(self, prompt):
        self.prompts.append(prompt)
        return {"model": self.model, "text": self.text, "leaves_host": False}


class DoorlessVault(FakeResidentVault):
    """An older PDI: no /resident/infer, the client answers None."""

    def resident_infer(self, prompt):
        return None


def _choose_vault(client, profile_id):
    r = client.put(f"/profiles/{profile_id}/model",
                   json={"provider": "vault"})
    assert r.status_code == 200, r.text
    return r.json()


def test_a_profile_speaks_through_the_vault(client, profile_id,
                                            interactor_id):
    vault = VoiceVault()
    client.app.state.pdi = vault
    chosen = _choose_vault(client, profile_id)
    assert chosen["effective"] == "vault"
    answered = _chat(client, profile_id, interactor_id,
                     "tell me about the lake house")
    assert answered["profile_message"]["content"] == vault.text
    # The whole turn reached the facility: the persona system prompt and
    # the person's words, framed for a completion engine.
    assert "tell me about the lake house" in vault.prompts[-1]
    assert vault.prompts[-1].endswith("You: ")


def test_the_models_list_carries_the_vault(client, profile_id):
    client.app.state.pdi = VoiceVault()
    out = client.get("/models").json()
    row = next(p for p in out["providers"] if p["name"] == "vault")
    assert row["configured"] is True


def test_a_vault_with_no_model_speaks_no_operational_sentence(client,
                                                              profile_id,
                                                              interactor_id):
    """The resident's stub answers honestly on PDI's own console; in a
    persona's mouth it would be an operational message wearing a face.
    The turn falls back to this product's own stub voice instead."""
    vault = VoiceVault(model="stub",
                       text="No local model is installed on this host.")
    client.app.state.pdi = vault
    _choose_vault(client, profile_id)
    answered = _chat(client, profile_id, interactor_id, "hello there")
    content = answered["profile_message"]["content"]
    assert content
    assert "No local model" not in content


def test_an_older_tandem_without_the_door_falls_back_too(client, profile_id,
                                                         interactor_id):
    client.app.state.pdi = DoorlessVault()
    _choose_vault(client, profile_id)
    answered = _chat(client, profile_id, interactor_id, "hello there")
    assert answered["profile_message"]["content"]


def test_no_tandem_means_the_choice_is_not_configured(client, profile_id):
    client.app.state.pdi = None
    assert llm.is_configured("vault") is False
    # A stored preference can never wedge generation: the choice resolves
    # to the platform default rather than a provider that cannot answer.
    assert llm.resolve_choice("vault") == llm.default_name()
