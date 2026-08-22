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
    """Another ordinary signed-in person — enrolled, like Sam.

    Bob is here so the pair rule has a second pair to be about: what Alice
    told the profile must never surface in its reply to Bob, and clearing
    Alice's memory must leave Bob's standing. Both of those are claims
    about a memory Bob actually has, and a memory belongs to the person
    now — so an accountless Bob has none, and the tests would pass by
    proving nothing was there.
    """
    from .conftest import enrol

    r = client.post("/interactors",
                    json={"display_name": name, "birthdate": "1998-03-03"})
    assert r.status_code == 201, r.text
    who = r.json()["id"]
    enrol(who)
    return who


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
    prefix = f"qrme/{interactor_id}/memory/{profile_id}/"
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
    assert f"qrme/{interactor_id}/memory/{profile_id}/m3" in vault.records


def test_a_memory_is_a_line_not_a_transcript(client, profile_id,
                                             interactor_id):
    vault = FakeResidentVault()
    recollection.remember(vault, profile_id, interactor_id, "m4", "x" * 5000)
    key = f"qrme/{interactor_id}/memory/{profile_id}/m4"
    assert len(json.loads(vault.records[key])["line"]) == recollection.MAX_LINE


# -- erasure -----------------------------------------------------------------

def test_erasure_leaves_the_persons_record_and_takes_the_profiles_words(
        client, profile_id, interactor_id):
    """Deleting a profile does not reach into somebody else's account.

    This test used to assert the opposite, and it was right to until the
    memory moved. A memory holds what the **person** said — only their own
    turns are ever sealed — and it now lives in their vault, under their
    key, on their plan. A profile's erasure right is a right over the
    profile's own words; it was quietly also taking the other party's
    record of having spoken.

    David, ruling on it: *the user's record survives, profile erasure
    redacts its own words.* Both halves are asserted here.

        asked     did we delete every trace of the profile
        mattered  did we delete somebody else's record while we were in there
    """
    vault = FakeResidentVault()
    client.app.state.pdi = vault
    _chat(client, profile_id, interactor_id, "remember this about me")
    keys = [r["pdi_key"] for r in db.connect().execute(
        "SELECT pdi_key FROM recollections WHERE profile_id=?",
        (profile_id,)).fetchall()]
    assert keys and all(k in vault.records for k in keys)

    gone = client.delete(f"/profiles/{profile_id}?mode=erase")
    assert gone.status_code == 200, gone.text

    # The person's half stands: seal, vector and ledger row.
    assert all(k in vault.records for k in keys), (
        "the profile's erasure took the other party's sealed memories out "
        "of their own vault")
    assert all(k in vault.embedded for k in keys)
    assert db.connect().execute(
        "SELECT COUNT(*) AS n FROM recollections WHERE profile_id=?",
        (profile_id,)).fetchone()["n"] == len(keys)

    # The profile's half is gone: its words, and its own view of the talk.
    assert db.connect().execute(
        "SELECT COUNT(*) AS n FROM messages WHERE profile_id=?",
        (profile_id,)).fetchone()["n"] == 0
    assert db.connect().execute(
        "SELECT COUNT(*) AS n FROM remembrances WHERE profile_id=?",
        (profile_id,)).fetchone()["n"] == 0, (
        "the profile's distilled view of the conversation is its own "
        "words and must go with it")
    assert db.connect().execute(
        "SELECT COUNT(*) AS n FROM profiles WHERE id=?",
        (profile_id,)).fetchone()["n"] == 0


def test_the_person_can_still_erase_what_the_profile_could_not(
        client, profile_id, interactor_id, interactor_head):
    """The record survives the profile, and the person still commands it.

    Sparing it from the profile's erasure would be hoarding if the person
    had no way to end it themselves. `forget_profile` is still exactly the
    sweep it was — a profile's deletion is simply no longer what fires it.
    """
    vault = FakeResidentVault()
    client.app.state.pdi = vault
    _chat(client, profile_id, interactor_id, "the thing to end later")
    keys = [r["pdi_key"] for r in db.connect().execute(
        "SELECT pdi_key FROM recollections WHERE profile_id=?",
        (profile_id,)).fetchall()]
    assert keys
    r = client.delete(f"/profiles/{profile_id}/memory/{interactor_id}",
                      headers=interactor_head)
    assert r.status_code == 204, r.text
    assert not [k for k in keys if k in vault.records]
    assert not [k for k in keys if k in vault.embedded]


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


def test_a_forgetting_takes_the_vector_with_the_seal(client, profile_id,
                                                     interactor_id):
    """A memory somebody erased must stop being findable, not merely stop
    being readable.

    The subject is a *forgetting* now rather than a profile deletion — the
    two came apart when the record moved to the person's side — but the
    property is the one that always mattered: a seal deleted while its
    vector survives is a memory that is unreadable and still ranks.
    """
    vault = FakeResidentVault()
    client.app.state.pdi = vault
    _chat(client, profile_id, interactor_id, "remember the lake house")
    assert len(vault.embedded) == 1
    removed = recollection.forget_pair(vault, profile_id, interactor_id)
    assert removed == 1
    assert vault.embedded == {}, "memory vectors survived the forgetting"
    assert vault.records == {}, "sealed memories survived the forgetting"


def test_recall_survives_a_move_to_an_open_plan(client, profile_id,
                                                interactor_id, monkeypatch):
    """Reads are never gated by the plan, and a move to Free changes the
    arrangement rather than ending it.

    Two halves, and the second one changed. Recall is a read, so somebody
    who paid last year keeps being recalled from what was sealed then —
    that was always the rule and still is.

    What their NEW turns get used to be nothing at all. Free is hosted
    now: the words in this deployment's own database, contributed as the
    tier's terms say. The old assertion here — *an open plan's turn was
    sealed* — was guarding against a free account's work landing in a
    vault it holds no key to, and that is still true: nothing new is
    sealed. It is kept, and the row says under what.
    """
    from qrme import db as db_mod, storage
    from qrme.routers import interaction as interaction_mod  # noqa: F401
    vault = FakeResidentVault()
    client.app.state.pdi = vault
    _chat(client, profile_id, interactor_id,
          "my sister is visiting from Lisbon in October")
    assert len(vault.embedded) == 1
    monkeypatch.setattr(storage, "memory_for",
                        lambda plan, pdi: (None, "open_cloud"))
    seen = {}
    orig = recollection.chat_block

    def spy(pdi_arg, *a, **k):
        seen["pdi"] = pdi_arg
        return orig(pdi_arg, *a, **k)

    monkeypatch.setattr(recollection, "chat_block", spy)
    answered = _chat(client, profile_id, interactor_id,
                     "what should I cook when my sister arrives")
    assert answered["profile_message"]["content"]
    assert seen["pdi"] is vault, "recall was gated behind the plan"
    sealed = [r["id"] for r in db_mod.connect().execute(
        "SELECT id FROM recollections WHERE posture='vault'").fetchall()]
    assert len(sealed) == 1, (
        "an open plan's turn was sealed into a vault it holds no key to")
    hosted = [r["line"] for r in db_mod.connect().execute(
        "SELECT line FROM recollections WHERE posture='open_cloud'").fetchall()]
    assert hosted == ["what should I cook when my sister arrives"], (
        "the open plan's turn was not kept at all — free is hosted, not "
        "forgotten, or a profile stops remembering everybody who is not "
        "paying and there is nothing to come back to")
