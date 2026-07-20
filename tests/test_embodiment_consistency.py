"""Embodiment personality-consistency: a profile keeps one identity — the same
persona signature and memory — across voice, text, and a hologram."""

from tests.test_capabilities import as_owner, make_interactor, make_profile


def test_signature_is_invariant_across_modality_and_embodiment(client):
    p = make_profile(client)
    as_owner(client, p)
    # Register embodiments the profile can inhabit.
    client.post(f"/profiles/{p['id']}/embodiments",
                json={"name": "hologram", "kind": "hologram"})
    client.post(f"/profiles/{p['id']}/embodiments",
                json={"name": "living-room-speaker", "kind": "speaker"})
    client.put(f"/profiles/{p['id']}/surfaces",
               json={"surfaces": ["chat", "hologram", "living-room-speaker"]})
    user = make_interactor(client)

    # Talk through three different forms.
    text = client.post(f"/profiles/{p['id']}/chat", json={
        "interactor_id": user, "message": "hi", "modality": "text"}).json()
    voice = client.post(f"/profiles/{p['id']}/chat", json={
        "interactor_id": user, "message": "still you?", "modality": "voice",
        "surface": "living-room-speaker"}).json()
    holo = client.post(f"/profiles/{p['id']}/chat", json={
        "interactor_id": user, "message": "and now?", "surface": "hologram"}).json()

    # One identity across all three — the signature never changes.
    sigs = {text["persona_signature"], voice["persona_signature"],
            holo["persona_signature"]}
    assert len(sigs) == 1 and next(iter(sigs))
    # The embodiment the turn came through is reported.
    assert voice["embodiment"] == "living-room-speaker"
    assert holo["embodiment"] == "hologram"
    assert text["embodiment"] is None


def test_consistency_endpoint_lists_forms(client):
    p = make_profile(client)
    as_owner(client, p)
    client.post(f"/profiles/{p['id']}/embodiments",
                json={"name": "robo", "kind": "robot", "has_llm": True})
    # Public: no auth needed to verify the identity.
    r = client.get(f"/profiles/{p['id']}/embodiment-consistency", headers={})
    assert r.status_code == 200
    body = r.json()
    assert body["signature"] and body["name"] == "Dana"
    assert "hologram" in body["invariant_across"]
    assert body["embodiments"][0]["name"] == "robo"


def test_signature_changes_when_identity_changes_not_when_form_does(client):
    p = make_profile(client)
    before = client.get(
        f"/profiles/{p['id']}/embodiment-consistency", headers={}).json()["signature"]

    # Adding an embodiment (a new form) must NOT change identity.
    as_owner(client, p)
    client.post(f"/profiles/{p['id']}/embodiments",
                json={"name": "earpiece", "kind": "earpiece"})
    after_form = client.get(
        f"/profiles/{p['id']}/embodiment-consistency", headers={}).json()["signature"]
    assert after_form == before

    # Editing the core persona DOES change identity.
    client.patch(f"/profiles/{p['id']}",
                 json={"persona": "A totally different character now."})
    after_edit = client.get(
        f"/profiles/{p['id']}/embodiment-consistency", headers={}).json()["signature"]
    assert after_edit != before
