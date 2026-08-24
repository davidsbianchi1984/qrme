"""The record, the veil and the exit, on the phones.

Seven more blocks off the per-shell doorless record — the memory list,
the record between the profile and one person, source material, the
profile's own ledger (transparency, export, stats, feed), anonymity,
verification, and the ways a profile ends — and what they share is
that every one is a promise the product makes in its own marketing:
you own it, you can read it, you can erase it, and you can leave.
A promise that can only be exercised at a desktop is a promise with
office hours. The phones now keep it too.

The rules these screens render rather than invent:

* **The memory list exists for choosing what to erase.** One row per
  conversation with the person's name, and erase sits next to read.
* **The pair reads the pair's record.** Thread, engagement, clinical
  notes, embedding — the owner and the person, and nobody else.
* **The veil's limits are half the payload.** What anonymity does NOT
  hide renders first, because the generous reading is the dangerous
  one.
* **The badge is a fact, not a word.** Level and attestor travel with
  "verified"; the roster of your other profiles answers only to your
  own token.
* **Departing, memorializing and deleting are three different ends.**
  Sunset freezes and says farewell; the memorial is public and never
  persona internals; delete removes every trace.
"""

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import clientpaths  # noqa: E402

from tests.test_capabilities import (as_interactor, auth_header,
                                     make_interactor, make_profile)
from . import ratchets, shelltables

REPO = Path(__file__).resolve().parent.parent


def _talk(client, p, name="Sam"):
    uid = make_interactor(client, name)
    r = client.post(f"/profiles/{p['id']}/chat",
                    json={"interactor_id": uid, "message": "hello there"})
    assert r.status_code == 200, r.text
    return uid


# -- the memory list --------------------------------------------------------

def test_the_memory_list_exists_for_choosing_what_to_erase(client):
    p = make_profile(client)
    uid = _talk(client, p)
    rows = client.get(f"/profiles/{p['id']}/memories",
                      headers=auth_header(p)).json()
    assert rows and rows[0]["interactor_id"] == uid
    # The row carries the person's name, not just an id.
    assert rows[0]["interactor_name"]
    turns = client.get(f"/profiles/{p['id']}/memory/{uid}",
                       headers=auth_header(p)).json()
    assert turns
    # Erasing is the point of the list — and it really erases.
    r = client.delete(f"/profiles/{p['id']}/memory/{uid}",
                      headers=auth_header(p))
    assert r.status_code == 204
    assert client.get(f"/profiles/{p['id']}/memory/{uid}",
                      headers=auth_header(p)).json() == []
    # The list is the owner's alone.
    q = make_profile(client, owner_id="owner-2", display_name="Quinn")
    assert client.get(f"/profiles/{p['id']}/memories",
                      headers=auth_header(q)).status_code == 403


# -- between the profile and one person -------------------------------------

def test_the_pair_reads_the_pairs_record_and_nobody_else(client):
    p = make_profile(client)
    uid = _talk(client, p)
    mine = as_interactor(uid)
    # Both parties read; a stranger's perfectly valid token does not.
    stranger = as_interactor(make_interactor(client, "Nosy"))
    # The raw conversation is the most sensitive read of the four — an
    # injection that unguarded it walked straight past a version of this
    # test that only checked the other three.
    for path in (f"/profiles/{p['id']}/memory/{uid}",
                 f"/profiles/{p['id']}/thread/{uid}",
                 f"/profiles/{p['id']}/engagement/{uid}",
                 f"/profiles/{p['id']}/clinical-notes/{uid}"):
        assert client.get(path, headers=auth_header(p)).status_code == 200, \
            path
        assert client.get(path, headers=mine).status_code == 200, path
        assert client.get(path, headers=stranger).status_code == 403, path
    # And a stranger cannot erase what two people remember.
    assert client.delete(f"/profiles/{p['id']}/memory/{uid}",
                         headers=stranger).status_code == 403


# -- source material --------------------------------------------------------

def test_source_material_is_the_owners_to_add_and_read(client):
    p = make_profile(client)
    made = client.post(f"/profiles/{p['id']}/sources", json={
        "kind": "life_event", "title": "the 1998 road trip",
        "content": "We drove the coast road."}, headers=auth_header(p))
    assert made.status_code == 201, made.text
    rows = client.get(f"/profiles/{p['id']}/sources",
                      headers=auth_header(p)).json()
    assert any(r["title"] == "the 1998 road trip" for r in rows)
    q = make_profile(client, owner_id="owner-2", display_name="Quinn")
    assert client.get(f"/profiles/{p['id']}/sources",
                      headers=auth_header(q)).status_code == 403


# -- the record -------------------------------------------------------------

def test_the_ledger_is_readable_and_the_feed_says_why(client):
    p = make_profile(client)
    _talk(client, p)
    # Transparency is public on purpose.
    t = client.get(f"/profiles/{p['id']}/transparency",
                   headers={"authorization": ""}).json()
    assert "acknowledges its other relationships" in t["policy"]
    # The numbers and the export are the owner's.
    s = client.get(f"/profiles/{p['id']}/stats",
                   headers=auth_header(p)).json()
    assert s["memory_entries"] >= 2
    out = client.get(f"/profiles/{p['id']}/export",
                     headers=auth_header(p)).json()
    assert len(out["messages"]) >= 2
    q = make_profile(client, owner_id="owner-2", display_name="Quinn")
    assert client.get(f"/profiles/{p['id']}/export",
                      headers=auth_header(q)).status_code == 403
    # The feed returns its own ranking rules, so it can be argued with.
    f = client.get(f"/profiles/{p['id']}/feed").json()
    assert "source material" in f["never_ranked_on"]


# -- the veil ---------------------------------------------------------------

def test_the_veils_limits_are_half_the_payload(client):
    p = make_profile(client)
    client.put(f"/profiles/{p['id']}/anonymity", json={"anonymous": True},
               headers=auth_header(p))
    v = client.get(f"/profiles/{p['id']}/anonymity",
                   headers=auth_header(p)).json()
    assert v["not_withheld"], \
        "what anonymity does NOT withhold is half the payload"
    q = make_profile(client, owner_id="owner-2", display_name="Quinn")
    assert client.get(f"/profiles/{p['id']}/anonymity",
                      headers=auth_header(q)).status_code == 403


# -- verification -----------------------------------------------------------

def test_the_badge_is_a_fact_and_the_roster_is_yours_alone(client):
    p = make_profile(client)
    made = client.post(f"/profiles/{p['id']}/verification",
                       json={"level": "document",
                             "attestor": "clinic-registrar"},
                       headers=auth_header(p))
    assert made.status_code == 201, made.text
    # Public read: the level and who checked travel with the word.
    v = client.get(f"/profiles/{p['id']}/verification",
                   headers={"authorization": ""}).json()
    assert v["verified"] is True and v["level"] == "document"
    # One badge per person: the second profile can read why it cannot.
    p2 = client.post("/profiles", json={
        "owner_id": "owner-1", "kind": "self", "display_name": "Dana Two",
        "persona": "The same person, elsewhere.",
        "verification": {"birthdate": "1984-06-01"}, "plan": "pro"}).json()
    h2 = {"authorization": f"Bearer {p2['owner_token']}"}
    able = client.get(f"/profiles/{p2['id']}/verifiable", headers=h2).json()
    assert able["can_verify"] is False
    # The badge moves rather than duplicates.
    moved = client.post(f"/profiles/{p2['id']}/verification/move",
                        headers=h2)
    assert moved.status_code == 200, moved.text
    assert client.get(
        f"/profiles/{p['id']}/verification").json()["verified"] is False
    # The roster answers only to the owner's own token.
    q = make_profile(client, owner_id="owner-2", display_name="Quinn")
    assert client.get(f"/profiles/{p['id']}/siblings",
                      headers=auth_header(q)).status_code == 403
    roster = client.get(f"/profiles/{p['id']}/siblings",
                        headers=auth_header(p)).json()
    assert len(roster["profiles"]) >= 2


# -- the exit ---------------------------------------------------------------

def test_departing_memorializing_and_deleting_are_three_ends(client):
    p = make_profile(client)
    _talk(client, p)
    # Edit is the gentlest exit: the profile changes and stays.
    r = client.patch(f"/profiles/{p['id']}",
                     json={"display_name": "Dana Renamed"},
                     headers=auth_header(p))
    assert r.status_code == 200 and r.json()["display_name"] == "Dana Renamed"
    # The memorial refuses while the profile lives.
    assert client.get(f"/profiles/{p['id']}/memorial").status_code == 409
    # Succession is reviewer-verified — the owner token is exactly the
    # thing that may be unavailable. From localhost with no admin token
    # the gate stands open (the development path), so the refusal is
    # asserted in the posture every reachable deployment runs in.
    os.environ["QRME_ADMIN_TOKEN"] = "reviewer-secret"
    try:
        assert client.post(f"/profiles/{p['id']}/succeed",
                           json={"verification_ref": "case-1"},
                           headers=auth_header(p)).status_code == 403
    finally:
        del os.environ["QRME_ADMIN_TOKEN"]
    # Sunset freezes; the memorial opens, public, never persona internals.
    out = client.post(f"/profiles/{p['id']}/sunset",
                      headers=auth_header(p)).json()
    assert out["status"] == "departed"
    m = client.get(f"/profiles/{p['id']}/memorial",
                   headers={"authorization": ""}).json()
    assert m["display_name"] and "persona" not in m
    # Delete removes every trace — a stranger cannot.
    q = make_profile(client, owner_id="owner-2", display_name="Quinn")
    assert client.delete(f"/profiles/{p['id']}",
                         headers=auth_header(q)).status_code == 403
    assert client.delete(f"/profiles/{p['id']}",
                         headers=auth_header(p)).status_code == 200
    assert client.get(f"/profiles/{p['id']}").status_code == 404


# -- the doors and their languages ------------------------------------------

def test_every_shell_has_doors_on_all_seven_blocks(client):
    for lang in clientpaths.NATIVE:
        made = clientpaths.calls(lang)
        assert ("GET", "/profiles/x/memories") in made, \
            f"{lang.name}: the memory list is unreadable"
        assert ("GET", "/profiles/x/thread/x") in made, \
            f"{lang.name}: the pair's record is unreadable"
        assert ("GET", "/profiles/x/sources") in made, \
            f"{lang.name}: the source material is unreadable"
        assert ("GET", "/profiles/x/export") in made, \
            f"{lang.name}: You Own It has office hours"
        assert ("PUT", "/profiles/x/anonymity") in made, \
            f"{lang.name}: the veil cannot be put on"
        assert ("GET", "/profiles/x/verification") in made, \
            f"{lang.name}: the badge is unreadable"
        assert ("POST", "/profiles/x/sunset") in made, \
            f"{lang.name}: no way to depart"
        assert ("DELETE", "/profiles/x") in made, \
            f"{lang.name}: no way to leave"


def test_the_seven_blocks_speak_ten_languages_on_every_shell(client):
    """Every mem/who/src/rec/veil/ver/exit key the iOS table carries,
    complete on all three shells — the full-list rule, never a sample."""
    keys = shelltables.ios_keys("record")
    assert len(keys) >= ratchets.floor("l10n.block.record"), \
        f"the iOS table lost rows: {len(keys)}"
    problems = shelltables.missing_rows(keys)
    assert not problems, (
        f"{len(problems)} gap(s) in the shell tables:\n    "
        + "\n    ".join(problems[:12]))
