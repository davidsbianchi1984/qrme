"""QRME's half of the estate's address book (qrme/contacts.py).

The ask, in its owner's words: *there's no address book when users create
connections... some people might not have JIM-mini and only have QRME.* JIM
grew its half first; a grant that only exists in the product somebody does
not have is a grant they cannot give, so this is the other half — the same
shape on purpose, held here in QRME's own words.

## What these hold

* the grant is the person's, off until chosen, and its ONE switch is also
  the withdrawal — turning it off drops the book from both custodies;
* the book is a synced source: `sync` replaces, never merges, and nothing
  offers a way to type a contact in;
* the recognisable tail is all that is kept, and no door ever returns it —
  the phone already has the numbers;
* sealed into the vault where the plan has one, platform custody
  otherwise, never both;
* `whose` is the one reader: a number in, a name or nothing out, and it
  writes nothing down;
* a person's book is guarded like the photograph with their face on it —
  their own token, and nobody else's.
"""

from __future__ import annotations

import json

import pytest

from qrme import contacts, db

from .test_capabilities import as_interactor, make_interactor

MOM = "+1 555 010 2233"


class Vault:
    def __init__(self):
        self.records = {}
        self.deleted = []

    def put(self, key, value):
        self.records[key] = value

    def get(self, key):
        return self.records.get(key)

    def delete(self, key):
        self.deleted.append(key)
        return self.records.pop(key, None) is not None


def granted_person(client) -> str:
    who = make_interactor(client, "Theo", "1990-01-01")
    r = client.put(f"/interactors/{who}/contacts/grant",
                   headers=as_interactor(who), json={"consented": True})
    assert r.status_code == 200, r.text
    return who


# -- the grant, and its one switch ------------------------------------------

def test_off_until_chosen_and_the_refusal_names_what_it_reaches(client):
    who = make_interactor(client, "Theo", "1990-01-01")
    r = client.put(f"/interactors/{who}/contacts",
                   headers=as_interactor(who),
                   json={"entries": [{"name": "Mom", "number": MOM}]})
    assert r.status_code == 403, r.text
    assert "people in your phone" in r.text
    assert client.get(f"/interactors/{who}/contacts",
                      headers=as_interactor(who)).status_code == 403


def test_the_grants_switch_is_also_the_withdrawal(client):
    """Nobody should have to find a second control to make the first one
    mean what it says: consented false drops the rows, right there."""
    who = granted_person(client)
    client.put(f"/interactors/{who}/contacts",
               headers=as_interactor(who),
               json={"entries": [{"name": "Mom", "number": MOM}]})
    r = client.put(f"/interactors/{who}/contacts/grant",
                   headers=as_interactor(who), json={"consented": False})
    assert r.status_code == 200, r.text
    rows = db.connect().execute(
        "SELECT * FROM contacts WHERE interactor_id=?", (who,)).fetchall()
    assert rows == []


def test_the_book_is_its_owners_alone(client):
    """Guarded like the photograph with their face on it."""
    who = granted_person(client)
    nosy = make_interactor(client, "Nosy")
    r = client.get(f"/interactors/{who}/contacts",
                   headers=as_interactor(nosy))
    assert r.status_code in (401, 403), (
        "somebody else's address book is readable to anyone holding an id")


# -- the sync, and what it keeps --------------------------------------------

def test_a_sync_replaces_rather_than_merges(client):
    """The device's book is the truth; a merge would quietly keep people
    the person deleted from their phone months ago."""
    who = granted_person(client)
    client.put(f"/interactors/{who}/contacts", headers=as_interactor(who),
               json={"entries": [{"name": "Mom", "number": MOM},
                                 {"name": "Old Dentist",
                                  "number": "+1 555 010 9999"}]})
    r = client.put(f"/interactors/{who}/contacts",
                   headers=as_interactor(who),
                   json={"entries": [{"name": "Mom", "number": MOM}]})
    assert r.status_code == 200 and r.json()["held"] == 1
    got = client.get(f"/interactors/{who}/contacts",
                     headers=as_interactor(who)).json()
    assert [c["name"] for c in got["book"]] == ["Mom"]


def test_the_numbers_never_come_back_out(client):
    who = granted_person(client)
    client.put(f"/interactors/{who}/contacts", headers=as_interactor(who),
               json={"entries": [{"name": "Mom", "number": MOM}]})
    body = client.get(f"/interactors/{who}/contacts",
                      headers=as_interactor(who)).text
    assert "2233" not in body, "a number crossed back over the wire"


def test_a_half_row_is_skipped_rather_than_refusing_the_book(client):
    who = granted_person(client)
    r = client.put(f"/interactors/{who}/contacts", headers=as_interactor(who),
                   json={"entries": [{"name": "Mom", "number": MOM},
                                     {"name": "??", "number": "911"}]})
    assert r.status_code == 200, r.text
    assert r.json() == {"held": 1, "skipped": 1, "sealed": False}


# -- recognition -------------------------------------------------------------

def test_whose_recognises_by_tail_whatever_the_formatting(client):
    who = granted_person(client)
    client.put(f"/interactors/{who}/contacts", headers=as_interactor(who),
               json={"entries": [{"name": "Mom", "number": MOM}]})
    seen = contacts.whose(who, "555-010-2233")
    assert seen is not None and seen["name"] == "Mom"
    assert "digits" not in seen and "number" not in seen


def test_whose_refuses_without_the_grant(client):
    who = make_interactor(client, "Theo", "1990-01-01")
    with pytest.raises(contacts.NotGranted):
        contacts.whose(who, MOM)


# -- where the book lives ----------------------------------------------------

def test_a_vaulted_plan_seals_and_withdrawal_still_reaches_it(monkeypatch,
                                                              client):
    """One book, one withdrawal, whichever custody the plan chose — and the
    deletion path never asks the plan, because what has to go is what is
    there."""
    who = granted_person(client)
    vault = Vault()
    monkeypatch.setattr("qrme.contacts.tiers.plan_of_interactor",
                        lambda i: "basic")
    monkeypatch.setattr("qrme.contacts.storage.vault_for",
                        lambda plan, pdi: vault if plan == "basic" else None)
    out = contacts.sync(who, [{"name": "Mom", "number": MOM}], pdi=vault)
    assert out["sealed"] is True
    assert db.connect().execute(
        "SELECT * FROM contacts WHERE interactor_id=?", (who,)).fetchall() == []
    names = [r["name"]
             for r in json.loads(next(iter(vault.records.values())))]
    assert names == ["Mom"]
    # The reader reads it back from the seal…
    assert [c["name"] for c in contacts.book(who, pdi=vault)] == ["Mom"]
    # …and the withdrawal empties it.
    contacts.decide(who, False, pdi=vault)
    assert vault.records == {} and vault.deleted


def test_a_sealed_book_with_no_vault_raises_rather_than_knowing_nobody(
        monkeypatch, client):
    who = granted_person(client)
    vault = Vault()
    monkeypatch.setattr("qrme.contacts.tiers.plan_of_interactor",
                        lambda i: "basic")
    monkeypatch.setattr("qrme.contacts.storage.vault_for",
                        lambda plan, pdi: vault)
    contacts.sync(who, [{"name": "Mom", "number": MOM}], pdi=vault)
    with pytest.raises(contacts.VaultUnreachable):
        contacts.book(who, pdi=None)


# -- the shape stays the estate's -------------------------------------------

def test_nothing_here_offers_a_typed_contact():
    """A synced source, never something people type — the round's first
    correction, held in the source: the only write is the sync."""
    from pathlib import Path

    import qrme.contacts as mod

    src = Path(mod.__file__).read_text(encoding="utf-8")
    writes = [line for line in src.splitlines()
              if "INSERT INTO contacts" in line]
    assert len(writes) == 1, "a second write path into the book appeared"
