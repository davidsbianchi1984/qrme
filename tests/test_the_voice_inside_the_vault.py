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


class GroundedVault(VoiceVault):
    """A PDI with the ask door: retrieval and generation both inside."""

    def __init__(self, **kw):
        super().__init__(**kw)
        self.asked: list[dict] = []

    def resident_ask(self, question, prefix=None, system=None):
        self.asked.append({"question": question, "prefix": prefix,
                           "system": system})
        return {"model": self.model, "text": self.text,
                "leaves_host": False,
                "drew_on": [prefix + "m1"] if prefix else []}


def test_a_profile_answers_grounded_in_the_pairs_seals(client, profile_id,
                                                       interactor_id):
    """Retrieval and generation both inside the facility: the vault ranks
    the pair's own seals against the last thing said and answers from
    them — the prefix is the per-pair wall inside the shared tenant, and
    the provenance says the grounding actually happened."""
    vault = GroundedVault()
    client.app.state.pdi = vault
    _choose_vault(client, profile_id)
    answered = _chat(client, profile_id, interactor_id,
                     "what should I cook when my sister arrives")
    assert answered["profile_message"]["content"] == vault.text
    assert answered["provenance"]["grounded_in_vault"] is True
    ask = vault.asked[-1]
    assert ask["question"] == "what should I cook when my sister arrives"
    assert ask["prefix"] == f"qrme/{interactor_id}/memory/{profile_id}/"
    assert ask["system"], "the persona was dropped on the way to the vault"
    # And recall stepped aside: the resident reads the same seals, so
    # fetching the lines here too would say them twice.
    assert "Moments you remember" not in ask["system"]


def test_grounding_is_pair_scoped(client, profile_id, interactor_id):
    from tests.test_the_profile_remembers_by_meaning import _second_interactor
    vault = GroundedVault()
    client.app.state.pdi = vault
    _choose_vault(client, profile_id)
    bob = _second_interactor(client)
    _chat(client, profile_id, bob, "hello from Bob")
    assert vault.asked[-1]["prefix"] == \
        f"qrme/{bob}/memory/{profile_id}/"


def test_an_older_pdi_speaks_ungrounded_and_says_so(client, profile_id,
                                                    interactor_id):
    """A PDI with the voice door but not the ask door still speaks —
    ungrounded, and the provenance says so rather than pretending."""
    vault = VoiceVault()          # has resident_infer, no resident_ask
    client.app.state.pdi = vault
    _choose_vault(client, profile_id)
    answered = _chat(client, profile_id, interactor_id, "hello there")
    assert answered["profile_message"]["content"] == vault.text
    assert answered["provenance"]["grounded_in_vault"] is False


# -- the study speaks with the same voice ------------------------------------

def _study(client, profile_id):
    r = client.post(f"/profiles/{profile_id}/excursions", json={
        "topic": "hydration",
        "question": "how much water does an older adult need daily",
    })
    assert r.status_code == 201, r.text
    return r.json()


def test_the_excursion_studies_inside_when_the_owner_chose_the_vault(
        client, profile_id):
    """The choice the owner made for conversation is a choice about
    where this profile's words are made — the study path gets no
    different answer. The brief goes to the resident, the cloud sees
    nothing, and left_host says so."""
    vault = VoiceVault(text="About two litres a day, spread out.")
    client.app.state.pdi = vault
    _choose_vault(client, profile_id)

    calls = {"n": 0}

    class Cloud:
        def generate(self, system, messages):
            calls["n"] += 1
            return "cloudy findings"
    client.app.state.cloud = Cloud()

    exc = _study(client, profile_id)
    assert exc["findings"] == "About two litres a day, spread out."
    assert exc["left_host"] is False, (
        "a brief answered inside the facility did not leave the host")
    assert calls["n"] == 0, "the cloud must see nothing"
    assert any("hydration" in p for p in vault.prompts)


def test_an_older_vault_studies_at_home_never_by_shipping_anyway(
        client, profile_id):
    """The honest fallback for "never send it out" is a worse answer
    made at home — the deterministic local provider — not a better one
    made by quietly using the cloud after all."""
    client.app.state.pdi = DoorlessVault()
    _choose_vault(client, profile_id)

    calls = {"n": 0}

    class Cloud:
        def generate(self, system, messages):
            calls["n"] += 1
            return "cloudy findings"
    client.app.state.cloud = Cloud()

    exc = _study(client, profile_id)
    assert exc["findings"]
    assert exc["findings"] != "cloudy findings"
    assert exc["left_host"] is False
    assert calls["n"] == 0, "the cloud must see nothing"


def test_a_default_profile_still_studies_through_the_cloud(client,
                                                           profile_id):
    client.app.state.pdi = VoiceVault()

    class Cloud:
        def generate(self, system, messages):
            return {"content": "cloudy findings"}
    client.app.state.cloud = Cloud()

    exc = _study(client, profile_id)
    assert exc["findings"] == "cloudy findings"
    assert exc["left_host"] is True
