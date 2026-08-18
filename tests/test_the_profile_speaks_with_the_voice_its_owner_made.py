"""The agent's audio, from a field report that said only: it is not working.

The person reporting had done their half. The voice existed — made, named and
verified on the engine's own surface — and the room's transcript carried the
agent's turns. What did not exist was any path from one to the other:
`voiceprint.speak` returns a descriptor and says synthesis belongs to
whichever engine the deployment configures, and no deployment configured one.

    asked     can the profile speak
    mattered  with the voice its owner made for it, on the box it runs on

## What these hold

**A reference, not an import.** The binding row carries a provider and an id.
The voice itself — its consent, its verification, its license — stays on the
provider's surface, exactly the shape the avatar market next door uses.

**The key is the deployment's.** `ELEVENLABS_API_KEY` comes from the host's
`.env` and is never written by this module. A missing key refuses *naming the
variable*, because a voice that silently fell back to nothing is how this gap
survived long enough to be field-reported.

**The mark rides along.** Every utterance is stamped through `watermark`
exactly as a text turn is, and the credential id returns beside the audio.

**The ceiling is real.** Synthesis is billed per character; `say` refuses over
`MAX_SAY` outright rather than letting a runaway caller find the wall on the
statement.
"""

from __future__ import annotations

import pytest

from qrme import db, spoken


def a_profile(client):
    r = client.post("/profiles", json={
        "owner_id": "owner-v", "kind": "self", "display_name": "Dana",
        "persona": "A retired teacher who likes gardening and dry humor.",
        "verification": {"birthdate": "1984-06-01"}, "plan": "pro"})
    assert r.status_code == 201, r.text
    return r.json()["id"], r.json()["owner_token"]


def head(token):
    return {"authorization": f"Bearer {token}"}


# --- the binding ------------------------------------------------------------

def test_the_binding_reads_the_same_bound_or_not(client):
    pid, tok = a_profile(client)
    empty = client.get(f"/profiles/{pid}/voice").json()
    client.put(f"/profiles/{pid}/voice",
               json={"voice_id": "v-1", "label": "My voice"},
               headers=head(tok))
    full = client.get(f"/profiles/{pid}/voice").json()
    assert set(empty) == set(full), (
        "the payload grows keys when a voice is bound, so every shell reads "
        "undefined on the case it meets most")
    assert empty["speaks"] is False and full["speaks"] is True


def test_only_the_owner_binds(client):
    pid, _ = a_profile(client)
    assert client.put(f"/profiles/{pid}/voice",
                      json={"voice_id": "v-1"}).status_code == 401


def test_an_empty_voice_id_unbinds(client):
    pid, tok = a_profile(client)
    client.put(f"/profiles/{pid}/voice", json={"voice_id": "v-1"},
               headers=head(tok))
    out = client.put(f"/profiles/{pid}/voice", json={"voice_id": ""},
                     headers=head(tok)).json()
    assert out["speaks"] is False
    assert db.connect().execute(
        "SELECT COUNT(*) AS n FROM profile_voices WHERE profile_id=?",
        (pid,)).fetchone()["n"] == 0


def test_an_unknown_provider_is_refused_naming_the_choices(client):
    pid, tok = a_profile(client)
    r = client.put(f"/profiles/{pid}/voice",
                   json={"provider": "acme", "voice_id": "v"},
                   headers=head(tok))
    assert r.status_code == 422
    assert "elevenlabs" in r.json()["detail"]


# --- the refusals a person can act on ---------------------------------------

def test_saying_without_a_binding_names_the_missing_step(client):
    pid, tok = a_profile(client)
    r = client.post(f"/profiles/{pid}/voice/say", json={"text": "hello"},
                    headers=head(tok))
    assert r.status_code == 422
    assert "no spoken voice bound" in r.json()["detail"]


def test_saying_without_the_key_names_the_variable(client, monkeypatch):
    pid, tok = a_profile(client)
    client.put(f"/profiles/{pid}/voice", json={"voice_id": "v-1"},
               headers=head(tok))
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    r = client.post(f"/profiles/{pid}/voice/say", json={"text": "hello"},
                    headers=head(tok))
    assert r.status_code == 422
    assert "ELEVENLABS_API_KEY" in r.json()["detail"], (
        "the refusal does not name the variable, so the operator reading it "
        "cannot act on it — which is how this gap went unreported")


def test_a_stranger_cannot_run_up_the_bill(client):
    pid, tok = a_profile(client)
    client.put(f"/profiles/{pid}/voice", json={"voice_id": "v-1"},
               headers=head(tok))
    assert client.post(f"/profiles/{pid}/voice/say",
                       json={"text": "hello"}).status_code == 401


def test_the_ceiling_refuses_rather_than_billing(client, monkeypatch):
    pid, tok = a_profile(client)
    client.put(f"/profiles/{pid}/voice", json={"voice_id": "v-1"},
               headers=head(tok))
    monkeypatch.setenv("ELEVENLABS_API_KEY", "k")
    called = []
    monkeypatch.setattr(spoken, "_synthesize",
                        lambda v, t, k, who: called.append(1) or b"x")
    r = client.post(f"/profiles/{pid}/voice/say",
                    json={"text": "x" * (spoken.MAX_SAY + 1)},
                    headers=head(tok))
    assert r.status_code == 422
    assert not called, "the engine was reached before the ceiling was asked"


# --- the audio, and what rides with it --------------------------------------

def test_audio_comes_back_with_the_mark_beside_it(client, monkeypatch):
    pid, tok = a_profile(client)
    client.put(f"/profiles/{pid}/voice", json={"voice_id": "v-1"},
               headers=head(tok))
    monkeypatch.setenv("ELEVENLABS_API_KEY", "k")
    asked = {}
    monkeypatch.setattr(
        spoken, "_synthesize",
        lambda v, t, k, who: asked.update(voice=v, text=t, key=k,
                                          who=who) or b"MP3")
    r = client.post(f"/profiles/{pid}/voice/say", json={"text": "hello"},
                    headers=head(tok))
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("audio/mpeg")
    assert r.content == b"MP3"
    assert r.headers["x-watermark-id"].startswith("wmk_"), (
        "the utterance left without a credential")
    assert asked == {"voice": "v-1", "text": "hello", "key": "k",
                     "who": pid}, (
        "the errand left without naming whose it was")


def test_the_key_is_never_stored(client, monkeypatch):
    """The row holds the reference; the credential stays in the process
    environment. A table that held the engine key would put it in every
    backup of a database whose job is other people's likenesses."""
    pid, tok = a_profile(client)
    client.put(f"/profiles/{pid}/voice",
               json={"voice_id": "v-1", "label": "x"}, headers=head(tok))
    row = db.connect().execute(
        "SELECT * FROM profile_voices WHERE profile_id=?", (pid,)).fetchone()
    assert set(row.keys()) == {"profile_id", "provider", "voice_id", "label",
                               "bound_at"}


def test_a_room_turn_names_its_speaker(client):
    """`sender_id` on the transcript is what lets a client follow a profile's
    turn to the voice route. It names a fellow participant — who the read is
    already scoped to — and nothing more."""
    pid, tok = a_profile(client)
    joiner = client.post("/interactors",
                         json={"display_name": "Sam"}).json()
    room = client.post("/rooms", json={
        "participants": [{"kind": "profile", "id": pid},
                         {"kind": "user", "id": joiner["id"]}]})
    assert room.status_code == 201, room.text
    room_id = room.json()["id"]
    ihead = {"authorization": f"Bearer {joiner['token']}"}
    client.post(f"/rooms/{room_id}/join", headers=ihead)
    said = client.post(f"/rooms/{room_id}/messages",
                       json={"sender_id": joiner["id"],
                             "message": "hello there"}, headers=ihead)
    assert said.status_code == 201, said.text
    rows = client.get(f"/rooms/{room_id}/messages", headers=ihead).json()
    profile_turns = [r for r in rows if r["sender_kind"] == "profile"]
    assert profile_turns, "no profile answered in the room"
    assert all(r.get("sender_id") == pid for r in profile_turns), (
        "a profile turn does not name its speaker, so no client can offer "
        "to say it aloud")
