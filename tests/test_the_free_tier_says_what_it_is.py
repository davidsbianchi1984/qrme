"""Hosted storage and contribution are one bargain, and it is stated.

David, choosing how the free tier's memories are consented: *the tier's
terms are the consent* — being on the hosted tier means your memories feed
model improvement, said plainly at the point it matters, with a switch to
turn it off.

That is a real change to a written promise, and the honest way to make it is
to change the promise rather than let the code quietly stop matching it.
`qrme/cloud.py` said contribution was *strictly opt-in per profile*; it now
says there are two kinds consented two different ways, and this file holds
the code to that.

    asked     may this improve the shared model
    mattered  is anybody who did not choose it caught by it

## The line that does not move

A memory sealed in a vault is **never** contributed, whatever any switch
says. That is the whole of what a private plan buys, and it is enforced by
the row's posture rather than by the flag — so a paying member who somehow
had `contributes=1` still contributes nothing. A guard on the flag alone
would pass while the property it exists for was false.
"""

from __future__ import annotations

from qrme import db, recollection, tiers

from .conftest import enrol
from .test_the_profile_remembers_by_meaning import FakeResidentVault, _chat


class FakeCloud:
    """A gateway that accepts everything and remembers what it was sent."""

    def __init__(self):
        self.sent: list[dict] = []
        self.revoked: list[str] = []
        self.refuse = False

    def contribute(self, payload):
        if self.refuse:
            return False
        self.sent.append(payload)
        return True

    def revoke_contributions(self, refs):
        self.revoked.extend(refs)
        return True


def _free(client, interactor_id):
    tiers.subscribe(f"acct-{interactor_id}", "free")


# -- the bargain --------------------------------------------------------------

def test_a_hosted_memory_is_contributed(client, profile_id, interactor_id):
    """The free tier's terms, doing what they say."""
    client.app.state.pdi = FakeResidentVault()
    cloud = FakeCloud()
    client.app.state.cloud = cloud
    _free(client, interactor_id)
    _chat(client, profile_id, interactor_id, "my sister lives in Lisbon")
    assert len(cloud.sent) == 1
    assert cloud.sent[0]["exchange"]["said"] == "my sister lives in Lisbon"


def test_nothing_that_points_back_at_the_person_leaves(client, profile_id,
                                                       interactor_id):
    """The ref is meaningless at the gateway and meaningful only here.

    Asserted over the whole payload rather than by naming the fields that
    should be absent: a check that lists what must not leave stops being
    true the moment somebody adds a field it does not know to look for.
    """
    client.app.state.pdi = FakeResidentVault()
    cloud = FakeCloud()
    client.app.state.cloud = cloud
    _free(client, interactor_id)
    _chat(client, profile_id, interactor_id, "the lake house is for sale")
    flat = repr(cloud.sent[0])
    for identifying in (profile_id, interactor_id, f"acct-{interactor_id}",
                        "Dana", "Sam"):
        assert identifying not in flat, (
            f"{identifying!r} left this deployment inside a contribution")


def test_a_sealed_memory_is_never_contributed(client, profile_id,
                                              interactor_id):
    """The line a private plan buys, tested against the flag being wrong.

    `contributes` is left at its default of 1 on purpose. If contribution
    were gated on the flag rather than on the posture, this would send —
    and a paying member's sealed conversation would be in the corpus.
    """
    client.app.state.pdi = FakeResidentVault()
    cloud = FakeCloud()
    client.app.state.cloud = cloud
    enrol(interactor_id, "pro")
    assert db.connect().execute(
        "SELECT contributes FROM interactors WHERE id=?",
        (interactor_id,)).fetchone()["contributes"] == 1
    _chat(client, profile_id, interactor_id, "something private")
    assert cloud.sent == [], (
        "a memory sealed in a vault was contributed — the whole of what a "
        "private plan buys is that this cannot happen")


def test_a_visitor_contributes_nothing_because_nothing_is_kept(
        client, profile_id, visitor_interactor):
    client.app.state.pdi = FakeResidentVault()
    cloud = FakeCloud()
    client.app.state.cloud = cloud
    _chat(client, profile_id, visitor_interactor, "said by a stranger")
    assert cloud.sent == []


# -- the switch ---------------------------------------------------------------

def test_the_switch_is_on_and_says_how_much_has_gone(client, profile_id,
                                                     interactor_id,
                                                     interactor_head):
    client.app.state.pdi = FakeResidentVault()
    client.app.state.cloud = FakeCloud()
    _free(client, interactor_id)
    _chat(client, profile_id, interactor_id, "one thing")
    _chat(client, profile_id, interactor_id, "another thing")
    out = client.get(f"/interactors/{interactor_id}/contribution",
                     headers=interactor_head)
    assert out.status_code == 200, out.text
    assert out.json() == {"contributes": True, "contributed_count": 2}


def test_turning_it_off_reaches_backwards(client, profile_id, interactor_id,
                                          interactor_head):
    """*From now on* is the weaker half of the promise.

    The refs carry no identity, so the past can be pulled back without the
    gateway ever being told whose it was.
    """
    client.app.state.pdi = FakeResidentVault()
    cloud = FakeCloud()
    client.app.state.cloud = cloud
    _free(client, interactor_id)
    _chat(client, profile_id, interactor_id, "said while it was on")
    sent_refs = [p["ref"] for p in cloud.sent]
    assert sent_refs

    off = client.delete(f"/interactors/{interactor_id}/contribution",
                        headers=interactor_head)
    assert off.status_code == 200, off.text
    body = off.json()
    assert body["contributes"] is False
    assert body["revoked_count"] == len(sent_refs)
    assert body["deleted_at_gateway"] is True
    assert sorted(cloud.revoked) == sorted(sent_refs)

    # And nothing new goes after it.
    _chat(client, profile_id, interactor_id, "said after it was off")
    assert [p["ref"] for p in cloud.sent] == sent_refs, (
        "a memory was contributed after the switch was turned off")


def test_the_flag_goes_down_even_when_the_gateway_cannot_be_reached(
        client, profile_id, interactor_id, interactor_head):
    """A deployment that cannot reach the gateway must still stop, and must
    not claim the past was reached when it was not."""
    client.app.state.pdi = FakeResidentVault()
    cloud = FakeCloud()
    client.app.state.cloud = cloud
    _free(client, interactor_id)
    _chat(client, profile_id, interactor_id, "said while it was on")
    client.app.state.cloud = None

    body = client.delete(f"/interactors/{interactor_id}/contribution",
                         headers=interactor_head).json()
    assert body["contributes"] is False
    assert body["deleted_at_gateway"] is False, (
        "the past was reported deleted with no gateway to delete it at")
    assert db.connect().execute(
        "SELECT contributes FROM interactors WHERE id=?",
        (interactor_id,)).fetchone()["contributes"] == 0
    assert db.connect().execute(
        "SELECT COUNT(*) AS n FROM contribution_log WHERE interactor_id=?"
        " AND revoked=0", (interactor_id,)).fetchone()["n"] == 1, (
        "rows were marked revoked without the gateway confirming it")


def test_the_switch_is_the_persons_alone(client, profile_id, interactor_id):
    client.app.state.pdi = FakeResidentVault()
    client.app.state.cloud = FakeCloud()
    for call in (client.get, client.delete):
        assert call(
            f"/interactors/{interactor_id}/contribution").status_code in (
            401, 403)
        assert call(f"/interactors/{interactor_id}/contribution",
                    headers={"authorization": "Bearer nope"}
                    ).status_code in (401, 403)


def test_a_refused_gateway_never_breaks_the_conversation(client, profile_id,
                                                         interactor_id):
    """Memory never breaks the doing, and neither does giving back."""
    client.app.state.pdi = FakeResidentVault()
    cloud = FakeCloud()
    cloud.refuse = True
    client.app.state.cloud = cloud
    _free(client, interactor_id)
    answered = _chat(client, profile_id, interactor_id, "still a conversation")
    assert answered["profile_message"]["content"]
    assert db.connect().execute(
        "SELECT COUNT(*) AS n FROM recollections", ()).fetchone()["n"] == 1, (
        "a refused contribution took the memory down with it")
