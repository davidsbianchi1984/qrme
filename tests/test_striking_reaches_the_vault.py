"""Transcript curation reaches the vault — no door forgets halfway.

The shelf round proved a sealed memory can be taken back by hand. This
round closes the other half of the doctrine: the doors that curate the
*transcript* — strike by checkbox, forget by words, rewrite in place,
erase the whole memory — used to delete the local turns and leave the
sealed recollection of those turns in the vault, still findable. Somebody
who struck "custody hearing" from the record could have it surface in the
profile's next reply, recalled by meaning from a seal no door had touched.

    asked     did the turn leave the transcript
    mattered  did the moment stop being findable

Every count is honest: `sealed_forgotten` says what the vault actually
let go of (profile turns are never sealed and count nothing), an edit
answers `memory_resealed`, and a tandem that is down leaves the ledger
rows standing on the shelf rather than orphaning seals nothing remembers.
"""

from __future__ import annotations

import json

from qrme import db, recollection, storage

from tests.test_the_profile_remembers_by_meaning import (
    BrokenVault, FakeResidentVault, _chat, _second_interactor)


def _pair_key(profile_id, interactor_id, ref):
    return f"qrme/{profile_id}/memory/{interactor_id}/{ref}"


def _interactor_turn(profile_id, interactor_id, words):
    return db.connect().execute(
        "SELECT id FROM messages WHERE profile_id=? AND interactor_id=?"
        " AND role='interactor' AND instr(content, ?) > 0",
        (profile_id, interactor_id, words)).fetchone()["id"]


def _profile_turn(profile_id, interactor_id):
    return db.connect().execute(
        "SELECT id FROM messages WHERE profile_id=? AND interactor_id=?"
        " AND role='profile' LIMIT 1",
        (profile_id, interactor_id)).fetchone()["id"]


# -- strike ------------------------------------------------------------------

def test_a_struck_turn_stops_being_findable(client, profile_id,
                                            interactor_id):
    vault = FakeResidentVault()
    client.app.state.pdi = vault
    _chat(client, profile_id, interactor_id, "the lake house is for sale")
    _chat(client, profile_id, interactor_id, "my dog is called Biscuit")
    ref = _interactor_turn(profile_id, interactor_id, "lake house")
    r = client.post(f"/profiles/{profile_id}/memory/{interactor_id}/strike",
                    json={"message_ids": [ref]})
    assert r.status_code == 200, r.text
    assert r.json()["sealed_forgotten"] == 1
    key = _pair_key(profile_id, interactor_id, ref)
    assert key not in vault.embedded, "the vector survived the strike"
    assert key not in vault.records, "the seal survived the strike"
    assert db.connect().execute(
        "SELECT COUNT(*) AS n FROM recollections WHERE id=?",
        (ref,)).fetchone()["n"] == 0
    # The struck moment is unfindable; the other one still is.
    assert recollection.chat_block(
        vault, profile_id, interactor_id, "tell me about the lake house") \
        is None
    assert "Biscuit" in recollection.chat_block(
        vault, profile_id, interactor_id, "what is my dog called")


def test_striking_a_profile_turn_forgets_no_seal(client, profile_id,
                                                 interactor_id):
    """Profile turns are never sealed; the count says so rather than
    claiming a forgetting that had nothing to forget."""
    vault = FakeResidentVault()
    client.app.state.pdi = vault
    _chat(client, profile_id, interactor_id, "remember the lake house")
    reply = _profile_turn(profile_id, interactor_id)
    r = client.post(f"/profiles/{profile_id}/memory/{interactor_id}/strike",
                    json={"message_ids": [reply]})
    assert r.status_code == 200, r.text
    out = r.json()
    assert out["struck_turns"] == 1
    assert out["sealed_forgotten"] == 0
    assert len(vault.embedded) == 1, "a profile turn took a seal with it"


def test_strike_survives_a_down_tandem(client, profile_id, interactor_id):
    """The strike is local truth and must land regardless; what the vault
    could not let go of is said in the count, not hidden."""
    vault = FakeResidentVault()
    client.app.state.pdi = vault
    _chat(client, profile_id, interactor_id, "remember the lake house")
    ref = _interactor_turn(profile_id, interactor_id, "lake house")
    client.app.state.pdi = BrokenVault()
    r = client.post(f"/profiles/{profile_id}/memory/{interactor_id}/strike",
                    json={"message_ids": [ref]})
    assert r.status_code == 200, r.text
    out = r.json()
    assert out["struck_turns"] == 1
    assert out["sealed_forgotten"] == 0


# -- forget by words ---------------------------------------------------------

def test_forget_by_words_takes_the_seal_too(client, profile_id,
                                            interactor_id):
    vault = FakeResidentVault()
    client.app.state.pdi = vault
    _chat(client, profile_id, interactor_id, "the lake house is for sale")
    r = client.post(f"/profiles/{profile_id}/memory/{interactor_id}/forget",
                    json={"about": "lake house"})
    assert r.status_code == 200, r.text
    assert r.json()["sealed_forgotten"] == 1
    prefix = f"qrme/{profile_id}/memory/{interactor_id}/"
    assert not any(k.startswith(prefix) for k in vault.embedded)
    assert not any(k.startswith(prefix) for k in vault.records)


# -- edit --------------------------------------------------------------------

def test_editing_reseals_the_new_words(client, profile_id, interactor_id):
    """The old words go first — vector, seal and ledger row — then the
    rewrite is sealed and embedded again under the same ref, so what is
    findable is always what the record now says."""
    vault = FakeResidentVault()
    client.app.state.pdi = vault
    _chat(client, profile_id, interactor_id, "my dog is called Biscuit")
    ref = _interactor_turn(profile_id, interactor_id, "Biscuit")
    r = client.put(
        f"/profiles/{profile_id}/memory/{interactor_id}/turns/{ref}",
        json={"content": "my cat is called Biscuit"})
    assert r.status_code == 200, r.text
    assert r.json()["memory_resealed"] is True
    key = _pair_key(profile_id, interactor_id, ref)
    assert json.loads(vault.records[key])["line"] == "my cat is called Biscuit"
    assert vault.embedded[key] == "my cat is called Biscuit"
    assert db.connect().execute(
        "SELECT COUNT(*) AS n FROM recollections WHERE id=?",
        (ref,)).fetchone()["n"] == 1


def test_editing_on_a_planless_vault_ends_the_memory(client, profile_id,
                                                     interactor_id,
                                                     monkeypatch):
    """Writes are plan-gated where deletes are not: a member who moved to
    Free can still take the old seal away, and the rewrite is simply not
    sealed — old words that stayed findable would betray the edit."""
    vault = FakeResidentVault()
    client.app.state.pdi = vault
    _chat(client, profile_id, interactor_id, "my dog is called Biscuit")
    ref = _interactor_turn(profile_id, interactor_id, "Biscuit")
    monkeypatch.setattr(storage, "vault_for", lambda plan, pdi: None)
    r = client.put(
        f"/profiles/{profile_id}/memory/{interactor_id}/turns/{ref}",
        json={"content": "my cat is called Biscuit"})
    assert r.status_code == 200, r.text
    assert r.json()["memory_resealed"] is False
    key = _pair_key(profile_id, interactor_id, ref)
    assert key not in vault.records and key not in vault.embedded
    assert db.connect().execute(
        "SELECT COUNT(*) AS n FROM recollections WHERE id=?",
        (ref,)).fetchone()["n"] == 0


# -- erase-all ---------------------------------------------------------------

def test_clearing_a_memory_sweeps_the_pair_and_only_the_pair(client,
                                                             profile_id,
                                                             interactor_id):
    vault = FakeResidentVault()
    client.app.state.pdi = vault
    bob = _second_interactor(client)
    _chat(client, profile_id, interactor_id, "the lake house is for sale")
    _chat(client, profile_id, interactor_id, "my dog is called Biscuit")
    _chat(client, profile_id, bob, "I collect vintage radios")
    r = client.delete(f"/profiles/{profile_id}/memory/{interactor_id}")
    assert r.status_code == 204, r.text
    pair = f"qrme/{profile_id}/memory/{interactor_id}/"
    assert not any(k.startswith(pair) for k in vault.embedded)
    assert not any(k.startswith(pair) for k in vault.records)
    assert db.connect().execute(
        "SELECT COUNT(*) AS n FROM recollections WHERE profile_id=?"
        " AND interactor_id=?", (profile_id, interactor_id)).fetchone()["n"] \
        == 0
    # Bob's memory of his own conversation stands untouched.
    assert any(k.startswith(f"qrme/{profile_id}/memory/{bob}/")
               for k in vault.embedded)


def test_a_down_tandem_leaves_the_shelf_standing(client, profile_id,
                                                 interactor_id,
                                                 interactor_head):
    """The local clearing lands; the rows whose seals the vault never let
    go of stay on the shelf — readable, and still individually
    forgettable once the tandem is back — rather than being orphaned."""
    vault = FakeResidentVault()
    client.app.state.pdi = vault
    _chat(client, profile_id, interactor_id, "remember the lake house")
    client.app.state.pdi = BrokenVault()
    r = client.delete(f"/profiles/{profile_id}/memory/{interactor_id}")
    assert r.status_code == 204, r.text
    assert db.connect().execute(
        "SELECT COUNT(*) AS n FROM messages WHERE profile_id=?"
        " AND interactor_id=?", (profile_id, interactor_id)).fetchone()["n"] \
        == 0
    client.app.state.pdi = vault
    shelf = client.get(f"/profiles/{profile_id}/memory/{interactor_id}"
                       "/recollections", headers=interactor_head).json()
    assert len(shelf["memories"]) == 1
    assert shelf["memories"][0]["line"] == "remember the lake house"
