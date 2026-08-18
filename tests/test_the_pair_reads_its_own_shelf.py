"""The sealed shelf, shown and curatable — the interactor's own door.

JIM's round put the coach's remembered moments in front of the person they
are about; this is QRME's twin, one wall stricter. `recollection.shelf`
reads the pair's `recollections` ledger rows — the same rows erasure walks
— and reads each line back from the vault, so the answer is exactly what
recall can surface, not a claim about it. The forget door takes one moment
back the whole way: the vector, the seal and the ledger row together,
while the chat turn it came from stays in the transcript — forgetting the
sealed memory is not striking the conversation.

    asked     does the profile remember through the vault
    mattered  can the person see what it remembers, and take one back
"""

from __future__ import annotations

from qrme import db, recollection

from tests.test_the_profile_remembers_by_meaning import (
    BrokenVault, FakeResidentVault, _chat, _second_interactor)


def _shelf(client, profile_id, interactor_id, headers=None):
    r = client.get(f"/profiles/{profile_id}/memory/{interactor_id}"
                   "/recollections", headers=headers or {})
    assert r.status_code == 200, r.text
    return r.json()


# -- the shelf ---------------------------------------------------------------

def test_the_shelf_lists_what_the_vault_holds_of_this_pair(client, profile_id,
                                                           interactor_id,
                                                           interactor_head):
    vault = FakeResidentVault()
    client.app.state.pdi = vault
    _chat(client, profile_id, interactor_id,
          "my sister is visiting from Lisbon next week")
    out = _shelf(client, profile_id, interactor_id, interactor_head)
    assert out["readable"] is True
    assert len(out["memories"]) == 1
    moment = out["memories"][0]
    assert moment["line"] == "my sister is visiting from Lisbon next week"
    assert moment["at"]
    # The ref is the ledger's own id — the handle the forget door takes.
    row = db.connect().execute(
        "SELECT id FROM recollections WHERE profile_id=?",
        (profile_id,)).fetchone()
    assert moment["ref"] == row["id"]


def test_bobs_shelf_never_lists_what_alice_said(client, profile_id,
                                                interactor_id):
    """One profile, many people. The pair scoping is in the SQL: the shelf
    for Bob is empty however much Alice has told it."""
    vault = FakeResidentVault()
    client.app.state.pdi = vault
    bob = _second_interactor(client)
    _chat(client, profile_id, interactor_id,
          "I am worried about my custody hearing")
    out = _shelf(client, profile_id, bob)
    assert out["memories"] == []


def test_the_shelf_answers_only_to_the_pair(client, profile_id,
                                            interactor_id):
    """A stranger's token opens nothing. The shelf is a list of what
    somebody told a profile in confidence — the same standing as the
    engagement record two doors down."""
    from qrme import auth
    stranger = _second_interactor(client, "Nosy")
    head = {"authorization": f"Bearer {auth.issue('interactor', stranger)}"}
    r = client.get(f"/profiles/{profile_id}/memory/{interactor_id}"
                   "/recollections", headers=head)
    assert r.status_code in (401, 403), r.text


def test_a_down_tandem_says_unreadable_rather_than_empty(client, profile_id,
                                                         interactor_id,
                                                         interactor_head):
    """"I hold a moment I cannot show you right now" and "I hold nothing"
    are different answers, and the person deciding whether to trust this
    profile is owed the difference."""
    vault = FakeResidentVault()
    client.app.state.pdi = vault
    _chat(client, profile_id, interactor_id, "remember the lake house")
    client.app.state.pdi = BrokenVault()
    out = _shelf(client, profile_id, interactor_id, interactor_head)
    assert out["readable"] is False
    assert len(out["memories"]) == 1
    assert out["memories"][0]["line"] is None
    assert out["memories"][0]["ref"]


def test_no_vault_configured_reads_the_same_way(client, profile_id,
                                                interactor_id):
    vault = FakeResidentVault()
    client.app.state.pdi = vault
    _chat(client, profile_id, interactor_id, "remember the lake house")
    client.app.state.pdi = None
    out = _shelf(client, profile_id, interactor_id)
    assert out == {"memories": [{"ref": out["memories"][0]["ref"],
                                 "line": None, "at": None}],
                   "readable": False}


# -- the forget door ---------------------------------------------------------

def test_forgetting_one_moment_unmakes_it_the_whole_way(client, profile_id,
                                                        interactor_id,
                                                        interactor_head):
    """The vector, the seal and the ledger row go together — and the chat
    turn stays: forgetting the sealed memory is not striking the
    transcript."""
    vault = FakeResidentVault()
    client.app.state.pdi = vault
    _chat(client, profile_id, interactor_id, "the lake house is for sale")
    _chat(client, profile_id, interactor_id, "my dog is called Biscuit")
    out = _shelf(client, profile_id, interactor_id, interactor_head)
    doomed = next(m for m in out["memories"]
                  if "lake house" in m["line"])
    r = client.delete(
        f"/profiles/{profile_id}/memory/{interactor_id}/recollections/"
        f"{doomed['ref']}", headers=interactor_head)
    assert r.status_code == 200, r.text
    assert r.json() == {"forgotten": True, "vectors_removed": 1}
    key = f"qrme/{profile_id}/memory/{interactor_id}/{doomed['ref']}"
    assert key not in vault.embedded, "the vector survived"
    assert key not in vault.records, "the seal survived"
    left = _shelf(client, profile_id, interactor_id, interactor_head)
    assert [m["line"] for m in left["memories"]] == ["my dog is called Biscuit"]
    # The transcript still carries the turn: the ref is its message id.
    row = db.connect().execute(
        "SELECT content FROM messages WHERE id=?", (doomed["ref"],)).fetchone()
    assert row["content"] == "the lake house is for sale"


def test_a_borrowed_ref_forgets_nothing(client, profile_id, interactor_id):
    """Bob holding Alice's ref strikes nothing: the ref is scoped to the
    pair's own ledger before the vault is asked anything."""
    from qrme import auth
    vault = FakeResidentVault()
    client.app.state.pdi = vault
    bob = _second_interactor(client)
    _chat(client, profile_id, interactor_id, "remember the lake house")
    ref = db.connect().execute(
        "SELECT id FROM recollections WHERE profile_id=?",
        (profile_id,)).fetchone()["id"]
    head = {"authorization": f"Bearer {auth.issue('interactor', bob)}"}
    r = client.delete(f"/profiles/{profile_id}/memory/{bob}/recollections/"
                      f"{ref}", headers=head)
    assert r.status_code == 404, r.text
    assert len(vault.embedded) == 1, "a borrowed ref reached the vault"


def test_forgetting_through_a_down_tandem_is_said_not_hidden(client,
                                                             profile_id,
                                                             interactor_id,
                                                             interactor_head):
    """Non-fatal like everything in recollection: the answer says what
    happened, and the ledger row stays until the vault actually let go —
    a forget that only forgot the bookkeeping would strand the vector."""
    vault = FakeResidentVault()
    client.app.state.pdi = vault
    _chat(client, profile_id, interactor_id, "remember the lake house")
    ref = db.connect().execute(
        "SELECT id FROM recollections WHERE profile_id=?",
        (profile_id,)).fetchone()["id"]
    client.app.state.pdi = BrokenVault()
    r = client.delete(
        f"/profiles/{profile_id}/memory/{interactor_id}/recollections/"
        f"{ref}", headers=interactor_head)
    assert r.status_code == 200, r.text
    out = r.json()
    assert out["forgotten"] is False
    assert "OSError" in out["why"]
    client.app.state.pdi = vault
    still = _shelf(client, profile_id, interactor_id, interactor_head)
    assert len(still["memories"]) == 1, "the ledger let go before the vault"


def test_no_vault_no_forgetting_no_pretending(client, profile_id,
                                              interactor_id):
    out = recollection.forget(None, profile_id, interactor_id, "m1")
    assert out == {"forgotten": False, "why": "no vault for this plan"}
