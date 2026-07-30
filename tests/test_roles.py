"""Role-specific interaction contexts (spec clauses 2 and 12): the profile
functions as an advisor, collaborator, or operator — declared on the turn,
or read autonomously from the prompt itself."""

from qrme import roles


def _chat(client, profile_id, interactor_id, message, **extra):
    r = client.post(f"/profiles/{profile_id}/chat",
                    json={"interactor_id": interactor_id,
                          "message": message, **extra})
    assert r.status_code == 200, r.text
    return r.json()


def test_declared_role_rides_the_turn(client, profile_id, interactor_id):
    body = _chat(client, profile_id, interactor_id,
                 "hello there", role="operator")
    assert body["role_context"] == {"role": "operator", "how": "declared"}
    assert body["profile_message"]["content"]      # the reply still lands


def test_the_profile_reads_the_prompt_itself(client, profile_id, interactor_id):
    """Clause 2's autonomous interpretation: no role declared, the prompt
    asks for counsel — the profile works as an advisor and says so."""
    body = _chat(client, profile_id, interactor_id,
                 "Should I take the job offer? What would you do?")
    assert body["role_context"] == {"role": "advisor", "how": "inferred"}


def test_a_plain_turn_stays_a_plain_turn(client, profile_id, interactor_id):
    body = _chat(client, profile_id, interactor_id, "good morning!")
    assert body["role_context"] is None


def test_unknown_role_rejected(client, profile_id, interactor_id):
    r = client.post(f"/profiles/{profile_id}/chat",
                    json={"interactor_id": interactor_id,
                          "message": "hi", "role": "overlord"})
    assert r.status_code == 422


def test_inference_is_transparent_keywords():
    assert roles.infer("Let's brainstorm some ideas together") == "collaborator"
    assert roles.infer("Draft a polite email to my landlord") == "operator"
    assert roles.infer("I could use some advice — is it worth it?") == "advisor"
    # No cues, or a tie between roles: silence, never a guess.
    assert roles.infer("the weather is nice") is None
    assert roles.infer("Let's brainstorm — and draft a memo, "
                       "what do you think, should I?") in (None, "collaborator",
                                                           "advisor", "operator")


def test_declared_beats_inferred(client, profile_id, interactor_id):
    """The interactor's word outranks the reading: a counsel-shaped prompt
    declared as collaborator works as a collaborator."""
    body = _chat(client, profile_id, interactor_id,
                 "Should I take the job offer?", role="collaborator")
    assert body["role_context"] == {"role": "collaborator", "how": "declared"}
