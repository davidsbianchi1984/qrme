"""Whose account a remembered conversation lives in.

David, on finding that a profile's memories sat in the profile's account:
*"I don't think the data should be stored in the synthetic profile's
account. I think it should go to the user that's engaging with a synthetic
profile's account. Because that would be useless data if the user never
returns."*

That is the whole argument in one sentence. A memory of a conversation is
worth keeping **because the person comes back** — so it belongs on the side
of the person who might. It used to be sealed under
`qrme/{profile}/memory/{who}/` and gated on the profile owner's plan, which
meant three things at once, all wrong:

  * whether your conversation was remembered depended on whether **somebody
    else** was paying for it;
  * the record of what you said lived in **their** account, under their key,
    where you could not read it and could not take it;
  * and it died the day they stopped paying, or deleted the profile.

    asked     may this be remembered
    mattered  whose is it

## The one that had to move with it

Erasure. `forget_profile` swept `qrme/{profile}/memory/` by prefix, which is
correct for exactly as long as the profile is the root of the key. After the
move that prefix matches nothing — and `resident_forget` returns a count, and
zero is an ordinary count, so erasure would have reported a clean sweep having
deleted nothing at all. An erasure that quietly erases nothing is worse than
one that fails loudly, because the second gets fixed.

Everything therefore resolves keys through the `recollections` ledger, which
records every key as its seal is cut. That is also what makes this change
safe for conversations that already happened: their keys are in the ledger
too, under the old shape, and nothing reads shape any more.
"""

from __future__ import annotations

from qrme import db, recollection, tiers

from .conftest import ADULT_VERIFICATION, enrol
from .test_the_profile_remembers_by_meaning import FakeResidentVault, _chat


def _ledger(profile_id):
    return [r["pdi_key"] for r in db.connect().execute(
        "SELECT pdi_key FROM recollections WHERE profile_id=?",
        (profile_id,)).fetchall()]


# -- whose plan decides -------------------------------------------------------

def test_the_key_is_rooted_in_the_person(client, profile_id, interactor_id):
    """The person, then the profile — not the other way round."""
    vault = FakeResidentVault()
    client.app.state.pdi = vault
    _chat(client, profile_id, interactor_id, "my sister lives in Lisbon")
    keys = _ledger(profile_id)
    assert len(keys) == 1
    assert keys[0].startswith(f"qrme/{interactor_id}/"), (
        f"{keys[0]} is not rooted in the person who said it — a record of "
        "somebody's conversation is sitting inside somebody else's account")
    assert f"/memory/{profile_id}/" in keys[0]


def test_a_paying_person_is_remembered_by_a_profile_whose_owner_is_not(
        client, profile_id, interactor_id):
    """The reversal, stated directly.

    The person pays; the profile's owner does not. Under the old gate this
    was silence — the owner's plan decided, and it said no. It is the
    person's conversation and the person's vault, so it is kept.
    """
    vault = FakeResidentVault()
    client.app.state.pdi = vault
    conn = db.connect()
    conn.execute("UPDATE memberships SET ended_at=? WHERE account_id=?",
                 (db.utcnow(), "owner-1"))
    conn.commit()
    # Proven, not assumed: the owner really is off a private plan now, so a
    # memory that lands can only have been gated on the person.
    assert tiers.plan_of_profile(profile_id) == "visitor"
    assert tiers.plan_of_interactor(interactor_id) != "visitor"
    _chat(client, profile_id, interactor_id, "remember the lake house")
    assert _ledger(profile_id), (
        "the person holds the plan and it is their conversation, but "
        "nothing was kept — the gate is still asking about the owner")


def test_a_signed_out_visitor_is_not_remembered_and_is_told_why(
        client, profile_id, visitor_interactor):
    """No account, so nowhere of their own for it to live.

    This is the honest end of the same rule rather than a gap in it. The
    reason is returned rather than left blank, because "we did not keep
    this" and "we kept this somewhere you cannot see" are the two answers
    a person deserves to be able to tell apart.
    """
    vault = FakeResidentVault()
    client.app.state.pdi = vault
    _chat(client, profile_id, visitor_interactor, "something about me")
    assert not _ledger(profile_id), (
        "a signed-out visitor's words were sealed into a vault they hold "
        "no key to and did not ask for")
    out = recollection.remember(None, profile_id, visitor_interactor,
                                "ref1", "something about me")
    assert out["remembered"] is False
    assert out["why"], "a refusal to remember with no reason given"


def test_the_plan_read_is_the_persons(client, interactor_id,
                                      visitor_interactor):
    """`plan_of_interactor` resolves through the person's own account."""
    assert tiers.plan_of_interactor(interactor_id) != "visitor"
    assert tiers.plan_of_interactor(visitor_interactor) == "visitor"
    assert tiers.plan_of_interactor("nobody-at-all") == "visitor"


# -- the hole the move opens --------------------------------------------------

def test_erasure_still_reaches_memories_after_the_key_moved(
        client, profile_id, interactor_id):
    """The regression that would have been silent.

    Deliberately asserted against the resident's index as well as the
    records: a seal deleted while its vector survives is a memory that is
    unreadable and still findable, which is not forgotten.
    """
    vault = FakeResidentVault()
    client.app.state.pdi = vault
    _chat(client, profile_id, interactor_id, "the thing to be forgotten")
    keys = _ledger(profile_id)
    assert keys and all(k in vault.embedded for k in keys)
    removed = recollection.forget_profile(vault, profile_id)
    assert removed == len(keys), (
        f"erasure reported {removed} vectors gone out of {len(keys)} — a "
        "prefix sweep that matches nothing returns 0 and reads as success")
    assert not [k for k in keys if k in vault.embedded]


def test_erasure_reaches_a_memory_sealed_under_the_old_shape(
        client, profile_id, interactor_id):
    """The conversations this product has already had.

    A memory sealed before the key changed is in the ledger under the old
    shape. Nothing reads shape, so it is found and forgotten with the rest
    — which is the entire reason the ledger is the index. A prefix filter
    would have stranded every one of them.
    """
    vault = FakeResidentVault()
    client.app.state.pdi = vault
    old_key = f"qrme/{profile_id}/memory/{interactor_id}/ancient"
    vault.put(old_key, '{"line": "said long ago", "at": "2020-01-01T00:00:00Z"}')
    vault.resident_embed(old_key, "said long ago")
    conn = db.connect()
    conn.execute(
        "INSERT INTO recollections (id, profile_id, interactor_id, pdi_key,"
        " created_at) VALUES (?,?,?,?,?)",
        ("ancient", profile_id, interactor_id, old_key, db.utcnow()))
    conn.commit()

    # It is on the pair's shelf, read back through the ledger.
    shelf = recollection.shelf(vault, profile_id, interactor_id)
    assert any(m["ref"] == "ancient" for m in shelf["memories"])

    # And a forgetting reaches it, by key rather than by shape.
    gone = recollection.forget(vault, profile_id, interactor_id, "ancient")
    assert gone["forgotten"] is True
    assert old_key not in vault.records
    assert old_key not in vault.embedded


def test_forgetting_reads_the_key_it_does_not_recompute_it(
        client, profile_id, interactor_id):
    """`_key` mints where a NEW moment goes; the ledger says where an old
    one lives. Recomputing would delete a key that does not exist, report
    success, and leave the real seal standing."""
    vault = FakeResidentVault()
    client.app.state.pdi = vault
    old_key = f"qrme/{profile_id}/memory/{interactor_id}/legacy"
    vault.put(old_key, '{"line": "before the move", "at": "2020-01-01T00:00:00Z"}')
    vault.resident_embed(old_key, "before the move")
    conn = db.connect()
    conn.execute(
        "INSERT INTO recollections (id, profile_id, interactor_id, pdi_key,"
        " created_at) VALUES (?,?,?,?,?)",
        ("legacy", profile_id, interactor_id, old_key, db.utcnow()))
    conn.commit()
    assert recollection._key(profile_id, interactor_id, "legacy") != old_key, (
        "this test is meaningless unless the minted key differs from the "
        "stored one")
    recollection.forget(vault, profile_id, interactor_id, "legacy")
    assert old_key not in vault.records, (
        "the seal survived: forget() deleted the key it would mint today "
        "rather than the key this memory actually has")


# -- the door on the person ---------------------------------------------------

def test_the_record_survives_the_profile_and_still_has_a_door(
        client, profile_id, interactor_id, interactor_head):
    """The whole ruling, end to end.

    David: *the user's record survives, profile erasure redacts its own
    words.* Sparing the record from the sweep is only half of that — a
    record kept where its owner cannot reach it is data being held, not a
    record surviving. The old door began by looking the profile up, so it
    shut the moment the profile went.
    """
    vault = FakeResidentVault()
    client.app.state.pdi = vault
    _chat(client, profile_id, interactor_id, "the lake house is for sale")

    # Before: readable, and the profile is named.
    mine = client.get(f"/interactors/{interactor_id}/memories",
                      headers=interactor_head)
    assert mine.status_code == 200, mine.text
    body = mine.json()
    assert body["readable"] is True
    assert len(body["conversations"]) == 1
    talk = body["conversations"][0]
    assert talk["gone"] is False
    assert talk["display_name"]
    assert [m["line"] for m in talk["memories"]] == [
        "the lake house is for sale"]

    assert client.delete(f"/profiles/{profile_id}?mode=erase").status_code == 200

    # After: still there, still readable, and honest that the other party
    # has gone. The name is omitted rather than invented — a deleted
    # profile's name is one of its own words.
    mine = client.get(f"/interactors/{interactor_id}/memories",
                      headers=interactor_head)
    assert mine.status_code == 200, mine.text
    body = mine.json()
    assert len(body["conversations"]) == 1
    talk = body["conversations"][0]
    assert talk["gone"] is True
    assert talk["display_name"] is None
    assert [m["line"] for m in talk["memories"]] == [
        "the lake house is for sale"], (
        "the person's own words did not survive the other party's erasure")


def test_the_door_is_the_persons_alone(client, profile_id, interactor_id):
    """One person's whole record in one answer is the most private read in
    this product. No token is not a lesser case of the wrong token."""
    vault = FakeResidentVault()
    client.app.state.pdi = vault
    _chat(client, profile_id, interactor_id, "something of mine")
    assert client.get(
        f"/interactors/{interactor_id}/memories").status_code in (401, 403)
    assert client.get(
        f"/interactors/{interactor_id}/memories",
        headers={"authorization": "Bearer not-your-token"}
    ).status_code in (401, 403)


def test_the_door_groups_by_conversation(client, profile_id, interactor_id,
                                         interactor_head):
    """One person talks to many profiles; each is its own conversation."""
    vault = FakeResidentVault()
    client.app.state.pdi = vault
    other = client.post("/profiles", json={
        "owner_id": "owner-2", "kind": "fictional", "display_name": "Wren",
        "persona": "A lighthouse keeper who writes letters.",
        "verification": ADULT_VERIFICATION,
        "plan": "pro",
    })
    assert other.status_code == 201, other.text
    second = other.json()["id"]
    _chat(client, profile_id, interactor_id, "told the first one this")
    _chat(client, second, interactor_id, "told the second one that")

    body = client.get(f"/interactors/{interactor_id}/memories",
                      headers=interactor_head).json()
    by_id = {c["profile_id"]: c for c in body["conversations"]}
    assert set(by_id) == {profile_id, second}
    assert [m["line"] for m in by_id[profile_id]["memories"]] == [
        "told the first one this"]
    assert [m["line"] for m in by_id[second]["memories"]] == [
        "told the second one that"]


# -- what the free tier is, and what it says about itself ---------------------

def _plan(interactor_id, plan):
    """Put this person on a plan."""
    account = enrol(interactor_id, plan) if plan != "visitor" else None
    return account


def test_free_is_hosted_not_forgotten(client, profile_id, interactor_id):
    """A profile remembers people who are not paying.

    David: *"we will use the cloud contributor version and I host that data
    for the basic tier."* The tier that stored nothing was the free one, and
    storing nothing is the version of this product nobody comes back to — a
    memory is only worth keeping because the person returns.

        asked     was this kept
        mattered  under which arrangement
    """
    vault = FakeResidentVault()
    client.app.state.pdi = vault
    tiers.subscribe(f"acct-{interactor_id}", "free")
    _chat(client, profile_id, interactor_id, "my sister lives in Lisbon")
    row = db.connect().execute(
        "SELECT posture, line, pdi_key FROM recollections"
        " WHERE profile_id=?", (profile_id,)).fetchone()
    assert row is not None, "the free tier's turn was not kept at all"
    assert row["posture"] == "open_cloud"
    assert row["line"] == "my sister lives in Lisbon"
    assert row["pdi_key"] == ""
    assert not vault.records, (
        "a free account's words were sealed into a vault it holds no key to")


def test_a_hosted_memory_is_still_found_by_meaning(client, profile_id,
                                                   interactor_id):
    """Hosting the words costs nothing the person can feel.

    The resident index stores a hash of the text and never the text, so
    embedding a hosted memory hands over no more than embedding a sealed
    one — and recall by meaning, which is the whole feature, works the same.
    """
    vault = FakeResidentVault()
    client.app.state.pdi = vault
    tiers.subscribe(f"acct-{interactor_id}", "free")
    _chat(client, profile_id, interactor_id, "my sister lives in Lisbon")
    found = recollection.recall(vault, profile_id, interactor_id,
                                "tell me about Lisbon")
    assert [m["line"] for m in found] == ["my sister lives in Lisbon"]


def test_a_hosted_memory_is_readable_when_the_tandem_is_down(
        client, profile_id, interactor_id, interactor_head):
    """Its words are in this database, so a dead vault cannot hide them."""
    vault = FakeResidentVault()
    client.app.state.pdi = vault
    tiers.subscribe(f"acct-{interactor_id}", "free")
    _chat(client, profile_id, interactor_id, "the lake house is for sale")
    client.app.state.pdi = None
    body = client.get(f"/interactors/{interactor_id}/memories",
                      headers=interactor_head).json()
    talk = body["conversations"][0]
    assert [m["line"] for m in talk["memories"]] == [
        "the lake house is for sale"]
    assert body["readable"] is True


def test_the_posture_is_the_rows_not_the_plans(client, profile_id,
                                               interactor_id,
                                               interactor_head):
    """Upgrading changes what happens next, never what already happened.

    Somebody on free has hosted rows. If the screen read their *current*
    plan, upgrading would describe those retroactively as sealed and
    private — a claim about the past that paying does not make true, and
    exactly the kind somebody would rely on.
    """
    vault = FakeResidentVault()
    client.app.state.pdi = vault
    tiers.subscribe(f"acct-{interactor_id}", "free")
    _chat(client, profile_id, interactor_id, "said while I was on free")
    tiers.subscribe(f"acct-{interactor_id}", "pro")
    _chat(client, profile_id, interactor_id, "said after I upgraded")

    rows = db.connect().execute(
        "SELECT posture, line FROM recollections WHERE profile_id=?"
        " ORDER BY created_at, rowid", (profile_id,)).fetchall()
    assert [r["posture"] for r in rows] == ["open_cloud", "vault"], (
        "the arrangement was read from the plan at display time rather "
        "than recorded when the memory was made")

    body = client.get(f"/interactors/{interactor_id}/memories",
                      headers=interactor_head).json()
    talk = body["conversations"][0]
    assert sorted(talk["postures"]) == ["open_cloud", "vault"], (
        "one badge over the whole conversation would be false about half "
        "of it, in whichever direction it leaned")


def test_a_visitor_still_has_nowhere_for_it_to_live(client, profile_id,
                                                    visitor_interactor):
    """No account is not a tier. There is nothing to attach a record to,
    and manufacturing a home for somebody who has not asked for one is not
    a kindness."""
    vault = FakeResidentVault()
    client.app.state.pdi = vault
    _chat(client, profile_id, visitor_interactor, "something about me")
    assert not db.connect().execute(
        "SELECT COUNT(*) AS n FROM recollections WHERE profile_id=?",
        (profile_id,)).fetchone()["n"]
