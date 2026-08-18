"""Recollection: what a profile remembers by meaning (qrme/recollection.py).

`remembrance` distills forward, in order; this finds the moment that is
*about* what was just said, however long ago. Each interactor turn is
sealed into the tandem and embedded under the same key through PDI's
resident index (which stores a hash, never the text). The rules held here
are the JIM round's three, plus one stricter: the recall prefix carries
the profile *and the interactor*, because one profile talks to many
people and what Alice told it must never surface in its reply to Bob.
"""

from __future__ import annotations

import json

import pytest

from qrme import db, recollection, research


class FakeResidentVault:
    """A PDI client the way `recollection` sees one: sealed records, an
    embedding index, a naive-but-honest search (token overlap), and the
    resident task doors `tabulate` drives."""

    def __init__(self):
        self.records: dict[str, str] = {}
        self.embedded: dict[str, str] = {}
        self.tabulated: list[tuple[str, list, str | None]] = []
        self.has_resident = True

    def put(self, key, value):
        self.records[key] = value

    def get(self, key):
        return self.records.get(key)

    def delete(self, key):
        return self.records.pop(key, None) is not None

    def resident_embed(self, key, text):
        if not self.has_resident:
            return False
        self.embedded[key] = text
        return True

    def resident_search(self, query, top_k=5):
        want = set(query.lower().split())
        scored = []
        for key, text in self.embedded.items():
            overlap = len(want & set(text.lower().split()))
            if overlap:
                scored.append((overlap, key))
        scored.sort(reverse=True)
        return [{"key": k, "score": float(s)} for s, k in scored[:top_k]]

    def resident_forget(self, key, prefix=False):
        doomed = ([k for k in self.embedded if k.startswith(key)]
                  if prefix else [k for k in self.embedded if k == key])
        for k in doomed:
            del self.embedded[k]
        return len(doomed)

    def resident_tabulate(self, dataset, rows, source_ref=None):
        if not self.has_resident:
            return False
        self.tabulated.append((dataset, rows, source_ref))
        return True


class BrokenVault:
    """A tandem that is down: every method raises."""

    def __getattr__(self, name):
        def boom(*a, **k):
            raise OSError("tandem unreachable")
        return boom


def _second_interactor(client, name="Robin"):
    r = client.post("/interactors",
                    json={"display_name": name, "birthdate": "1998-03-03"})
    assert r.status_code == 201, r.text
    return r.json()["id"]


def _chat(client, profile_id, interactor_id, message):
    r = client.post(f"/profiles/{profile_id}/chat",
                    json={"interactor_id": interactor_id,
                          "message": message})
    assert r.status_code == 200, r.text
    return r.json()


# -- remember ----------------------------------------------------------------

def test_a_chat_turn_becomes_a_sealed_indexed_memory(client, profile_id,
                                                     interactor_id):
    vault = FakeResidentVault()
    client.app.state.pdi = vault
    _chat(client, profile_id, interactor_id,
          "my sister is visiting from Lisbon next week")
    prefix = f"qrme/{profile_id}/memory/{interactor_id}/"
    keys = [k for k in vault.embedded if k.startswith(prefix)]
    assert len(keys) == 1
    sealed = json.loads(vault.records[keys[0]])
    assert sealed["line"] == "my sister is visiting from Lisbon next week"
    # And the ledger row erasure reads, written beside the seal.
    row = db.connect().execute(
        "SELECT * FROM recollections WHERE profile_id=?",
        (profile_id,)).fetchone()
    assert row["pdi_key"] == keys[0]
    assert row["interactor_id"] == interactor_id


def test_the_reply_finds_the_moment_this_question_is_about(client, profile_id,
                                                           interactor_id):
    vault = FakeResidentVault()
    client.app.state.pdi = vault
    _chat(client, profile_id, interactor_id,
          "my sister is visiting from Lisbon in October")
    block = recollection.chat_block(
        vault, profile_id, interactor_id,
        "what should I cook when my sister arrives")
    assert block is not None
    assert "Lisbon" in block
    assert block.startswith("Moments you remember")


def test_what_alice_said_never_surfaces_for_bob(client, profile_id,
                                                interactor_id):
    """One profile, many people. The prefix carries both ids, so recall
    drops the other person's moments before it fetches a word."""
    vault = FakeResidentVault()
    client.app.state.pdi = vault
    bob = _second_interactor(client)
    _chat(client, profile_id, interactor_id,
          "I am worried about my custody hearing")
    assert recollection.chat_block(
        vault, profile_id, bob, "tell me about custody hearings") is None


def test_no_vault_for_this_plan_means_no_memory_and_no_pretending(client,
                                                                  profile_id,
                                                                  interactor_id):
    out = recollection.remember(None, profile_id, interactor_id, "m1",
                                "words")
    assert out == {"remembered": False, "why": "no vault for this plan"}
    assert recollection.chat_block(None, profile_id, interactor_id,
                                   "anything") is None
    # And the chat still answers with no vault configured at all.
    client.app.state.pdi = None
    answered = _chat(client, profile_id, interactor_id, "hello there")
    assert answered["profile_message"]["content"]


def test_memory_never_breaks_the_chat(client, profile_id, interactor_id):
    """A turn that lands and is not remembered beats a turn refused
    because the tandem was down."""
    client.app.state.pdi = BrokenVault()
    answered = _chat(client, profile_id, interactor_id,
                     "are you still there")
    assert answered["profile_message"]["content"]
    out = recollection.remember(BrokenVault(), profile_id, interactor_id,
                                "m2", "words")
    assert out["remembered"] is False
    assert "OSError" in out["why"]


def test_an_older_vault_without_the_resident_is_said_not_hidden(client,
                                                                profile_id,
                                                                interactor_id):
    vault = FakeResidentVault()
    vault.has_resident = False
    out = recollection.remember(vault, profile_id, interactor_id, "m3",
                                "the words")
    assert out == {"remembered": False,
                   "why": "the vault has no memory index"}
    # Sealed anyway: the words are safe even where they are not findable.
    assert f"qrme/{profile_id}/memory/{interactor_id}/m3" in vault.records


def test_a_memory_is_a_line_not_a_transcript(client, profile_id,
                                             interactor_id):
    vault = FakeResidentVault()
    recollection.remember(vault, profile_id, interactor_id, "m4", "x" * 5000)
    key = f"qrme/{profile_id}/memory/{interactor_id}/m4"
    assert len(json.loads(vault.records[key])["line"]) == recollection.MAX_LINE


# -- erasure -----------------------------------------------------------------

def test_erasure_purges_the_memories_with_the_profile(client, profile_id,
                                                      interactor_id):
    """The lesson the JIM round learned mid-flight, applied here before the
    first key was cut: the ledger row lands beside the seal, and the
    profile-erasure sweep reads it."""
    vault = FakeResidentVault()
    client.app.state.pdi = vault
    _chat(client, profile_id, interactor_id, "remember this about me")
    assert any(k.startswith(f"qrme/{profile_id}/memory/")
               for k in vault.records)
    gone = client.delete(f"/profiles/{profile_id}?mode=erase")
    assert gone.status_code == 200, gone.text
    assert not any(k.startswith(f"qrme/{profile_id}/memory/")
                   for k in vault.records), "sealed memories survived erasure"


# -- tabulate: the study ledger in the vault's tables ------------------------

def test_a_study_writes_its_ledger_row_into_the_vault(client, profile_id,
                                                      monkeypatch):
    vault = FakeResidentVault()
    monkeypatch.setattr(research, "gather",
                        lambda brief, cloud: "findings text")
    from qrme import privileges
    privileges.choose(profile_id, "study_the_web", True)
    cid = research.excursion(profile_id, "tomato blight", "how to treat it",
                             pdi=vault)
    assert cid
    dataset, rows, source = vault.tabulated[0]
    assert dataset == "qrme_studies"
    assert rows[0]["topic"] == "tomato blight"
    assert "findings" not in rows[0], (
        "the findings stay in this deployment's row — the vault table gets "
        "the ledger, never the content")
    assert source == profile_id


def test_a_down_tandem_keeps_the_study(client, profile_id, monkeypatch):
    monkeypatch.setattr(research, "gather",
                        lambda brief, cloud: "findings text")
    from qrme import privileges
    privileges.choose(profile_id, "study_the_web", True)
    cid = research.excursion(profile_id, "sleep", "how much is enough",
                             pdi=BrokenVault())
    row = db.connect().execute(
        "SELECT * FROM excursions WHERE id=?", (cid,)).fetchone()
    assert row["topic"] == "sleep"


def test_erasure_takes_the_memory_vectors_too(client, profile_id,
                                              interactor_id):
    """The seal dies with the ledger row; the vector dies here — a memory
    somebody erased must stop being findable, not merely stop being
    readable."""
    vault = FakeResidentVault()
    client.app.state.pdi = vault
    _chat(client, profile_id, interactor_id, "remember the lake house")
    assert len(vault.embedded) == 1
    gone = client.delete(f"/profiles/{profile_id}?mode=erase")
    assert gone.status_code == 200, gone.text
    assert vault.embedded == {}, "memory vectors survived erasure"
