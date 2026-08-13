"""The agreement two people sign before work changes hands.

The tests worth having are not about creating an exchange. They are about the
four rules that make it more than a form: neither signature alone opens
anything, an edit voids both, nothing arrives on its own, and no part of this
grants access to anybody's machine.
"""

import pytest

from qrme import exchange


HOST, GUEST, OTHER = "hst_1", "gst_1", "oth_1"


def _drafted(work="Build the checkout flow", industry="software"):
    x = exchange.propose(HOST, GUEST, work, industry,
                         includes=["source", "a handover call"],
                         excludes=["hosting", "ongoing support"])
    exchange.add_item(x["id"], "guest_to_host", "spec.pdf", "document", 240_000)
    exchange.add_item(x["id"], "host_to_guest", "checkout.zip", "source", 1_400_000)
    return exchange.get(x["id"])


# -- neither signature alone opens anything ---------------------------------

def test_a_fresh_exchange_is_shut(client):
    x = _drafted()
    assert x["channel"]["open"] is False
    assert sorted(x["unsigned"]) == sorted([HOST, GUEST])


def test_one_signature_does_not_open_it(client):
    """A one-sided agreement is not an agreement."""
    x = _drafted()
    exchange.sign(x["id"], HOST)
    after = exchange.get(x["id"])
    assert after["channel"]["open"] is False
    assert after["unsigned"] == [GUEST]
    assert after["state"] == "proposed"


def test_both_signatures_open_it(client):
    x = _drafted()
    exchange.sign(x["id"], HOST)
    exchange.sign(x["id"], GUEST)
    after = exchange.get(x["id"])
    assert after["state"] == "signed"
    assert after["channel"]["open"] is True
    assert len(after["channel"]["items"]) == 2


def test_a_stranger_cannot_sign(client):
    x = _drafted()
    with pytest.raises(exchange.ExchangeError):
        exchange.sign(x["id"], OTHER)


def test_an_empty_manifest_cannot_be_signed(client):
    """The state people sign by accident: a document that agrees to nothing in
    particular, which afterwards means whatever the other side says."""
    x = exchange.propose(HOST, GUEST, "Something", "software")
    with pytest.raises(exchange.ExchangeError) as err:
        exchange.sign(x["id"], HOST)
    assert "nothing on the manifest" in str(err.value)


# -- the rule the whole design turns on -------------------------------------

def test_changing_the_manifest_voids_both_signatures(client):
    """Without this, you agree to two items and the other side appends a third,
    and your signature sits on a document you never read."""
    x = _drafted()
    exchange.sign(x["id"], HOST)
    exchange.sign(x["id"], GUEST)
    assert exchange.channel(x["id"])["open"] is True

    exchange.reopen(x["id"], HOST)
    exchange.add_item(x["id"], "host_to_guest", "extra.bin", "build", 9_000_000)

    after = exchange.get(x["id"])
    assert after["state"] == "draft"
    assert after["channel"]["open"] is False
    assert sorted(after["unsigned"]) == sorted([HOST, GUEST])


def test_the_fingerprint_moves_when_the_document_does(client):
    """Signatures are stored against the fingerprint, which is what makes the
    rule above a fact about the data rather than a promise about the code."""
    x = _drafted()
    before = exchange.fingerprint(x["id"])
    exchange.add_item(x["id"], "host_to_guest", "notes.md", "document", 900)
    assert exchange.fingerprint(x["id"]) != before


def test_a_signature_can_never_go_stale(client):
    """Stronger than "stale signatures are shown": there is no way to make one.

    This test started out asserting that an out-of-date signature is displayed
    rather than hidden, and it failed — because the document freezes the moment
    *anybody* signs, not when both do. So the only route to an edit is
    `reopen`, and that deletes the signatures on its way past. Both exits from
    a signed manifest are closed, and the invariant is that the pair
    (signature, manifest) is either current or absent.

    `matches_current` stays on the record anyway. It costs a hash, it is what a
    reviewer looks for, and an invariant that is only true because two other
    functions happen to agree is worth being able to check at a glance."""
    x = _drafted()
    exchange.sign(x["id"], HOST)

    # Frozen after one signature, not two.
    with pytest.raises(exchange.ExchangeError):
        exchange.add_item(x["id"], "host_to_guest", "late.txt", "document", 10)

    # And the only way out drops the signature rather than outdating them.
    exchange.reopen(x["id"], GUEST)
    assert exchange.get(x["id"])["signatures"] == []

    exchange.add_item(x["id"], "host_to_guest", "late.txt", "document", 10)
    exchange.sign(x["id"], HOST)
    exchange.sign(x["id"], GUEST)
    assert all(s["matches_current"]
               for s in exchange.get(x["id"])["signatures"])


def test_a_signed_manifest_cannot_be_edited_in_place(client):
    x = _drafted()
    exchange.sign(x["id"], HOST)
    exchange.sign(x["id"], GUEST)
    with pytest.raises(exchange.ExchangeError) as err:
        exchange.add_item(x["id"], "host_to_guest", "sneaky.bin", "build", 1)
    assert "not editable" in str(err.value)


def test_only_a_party_can_reopen(client):
    x = _drafted()
    with pytest.raises(exchange.ExchangeError):
        exchange.reopen(x["id"], OTHER)


# -- nothing arrives on its own ---------------------------------------------

def test_signing_does_not_deliver_anything(client):
    """Consent to an agreement is not consent to a file landing on your disk."""
    x = _drafted()
    exchange.sign(x["id"], HOST)
    exchange.sign(x["id"], GUEST)
    after = exchange.get(x["id"])
    assert after["channel"]["auto_download"] is False
    assert all(i["accepted_at"] is None for i in after["items"])


def test_each_item_is_accepted_by_its_receiver_only(client):
    """The sender cannot accept on the recipient's behalf, which would make the
    per-item step decorative."""
    x = _drafted()
    exchange.sign(x["id"], HOST)
    exchange.sign(x["id"], GUEST)
    theirs = [i for i in x["items"] if i["direction"] == "host_to_guest"][0]
    with pytest.raises(exchange.ExchangeError) as err:
        exchange.accept_item(x["id"], theirs["id"], HOST)
    assert "only the side receiving" in str(err.value)
    exchange.accept_item(x["id"], theirs["id"], GUEST)


def test_nothing_can_be_accepted_before_both_sign(client):
    x = _drafted()
    exchange.sign(x["id"], HOST)
    with pytest.raises(exchange.ExchangeError):
        exchange.accept_item(x["id"], x["items"][0]["id"], GUEST)


def test_delivered_only_once_every_item_is_taken(client):
    x = _drafted()
    exchange.sign(x["id"], HOST)
    exchange.sign(x["id"], GUEST)
    a, b = x["items"]
    recv = {"host_to_guest": GUEST, "guest_to_host": HOST}
    exchange.accept_item(x["id"], a["id"], recv[a["direction"]])
    assert exchange.get(x["id"])["state"] == "signed"
    exchange.accept_item(x["id"], b["id"], recv[b["direction"]])
    assert exchange.get(x["id"])["state"] == "delivered"


# -- what a person is actually agreeing to ----------------------------------

def test_the_manifest_says_what_runs_on_your_machine(client):
    """`source` and `build` execute if anybody double-clicks them. A surface
    should be able to say so without inspecting a filename."""
    x = _drafted()
    assert "checkout.zip" in x["runs_on_your_machine"]
    assert "spec.pdf" not in x["runs_on_your_machine"]
    assert "not a review of what the code does" in x["runs_warning"]


def test_exclusions_are_carried_not_implied(client):
    """An absent exclusion reads as an inclusion to whoever paid."""
    x = _drafted()
    assert "hosting" in x["excludes"]
    assert "a handover call" in x["includes"]


def test_it_grants_no_device_access(client):
    """Stated on the object rather than in the docs, because this is the line
    somebody will assume is elsewhere."""
    x = _drafted()
    assert "device" in x["does_not_grant"]
    assert x["grants"] == "the listed items, once accepted"


def test_the_fee_says_it_is_simulated(client):
    x = exchange.propose(HOST, GUEST, "Work", "trades", fee=250.0)
    assert x["fee"] == 250.0
    assert "no funds move" in x["fee_note"]


def test_every_industry_is_offered(client):
    """It is a business exchange in any trade, not a software feature that
    other industries are allowed to borrow."""
    for ind in exchange.INDUSTRIES:
        assert exchange.propose(HOST, GUEST, "Work", ind)["industry"] == ind
    with pytest.raises(exchange.ExchangeError):
        exchange.propose(HOST, GUEST, "Work", "astrology")


def test_either_side_can_walk_away(client):
    x = _drafted()
    exchange.sign(x["id"], HOST)
    exchange.sign(x["id"], GUEST)
    exchange.withdraw(x["id"], GUEST)
    assert exchange.channel(x["id"]) == {"open": False, "reason": "withdrawn"}


def test_an_exchange_needs_two_parties(client):
    with pytest.raises(exchange.ExchangeError):
        exchange.propose(HOST, HOST, "Work", "software")


def test_the_route_publishes_its_own_rules(client):
    r = client.get("/exchanges/vocabulary").json()
    assert "any change to the manifest clears both signatures" in r["rules"]
    runs = {k["key"] for k in r["kinds"] if k["runs"]}
    assert runs == {"source", "build"}


# -- the whole road, over HTTP, with every kind on the manifest --------------

def test_the_whole_exchange_goes_through_over_http(client):
    """A field report asked to "make sure the process completely goes
    through as if they've agreed upon an exchange... across every one of
    those variables". So: two real people with real tokens drive the full
    lifecycle through the routes — propose, list one item of *every* kind
    the vocabulary offers (both directions), both sign, the receiving side
    accepts each item — and the exchange lands on `delivered` with nothing
    left waiting.
    """
    from qrme import exchange as x
    from tests.test_capabilities import as_interactor, make_interactor
    host = make_interactor(client, "Host", "1990-01-01")
    guest = make_interactor(client, "Guest", "1991-01-01")
    hh, gh = as_interactor(host), as_interactor(guest)

    kinds = client.get("/exchanges/vocabulary").json()["kinds"]
    assert {k["key"] for k in kinds} == set(x.KINDS)

    r = client.post("/exchanges", headers=hh, json={
        "host_id": host, "guest_id": guest,
        "work": "One of everything, both ways",
        "industry": "software",
        "includes": ["every kind the vocabulary names"],
        "excludes": ["anything not on the manifest"]})
    assert r.status_code == 201, r.text
    xid = r.json()["id"]

    directions = ["host_to_guest", "guest_to_host"]
    for i, kind in enumerate(sorted(x.KINDS)):
        r = client.post(f"/exchanges/{xid}/items", headers=hh, json={
            "direction": directions[i % 2],
            "name": f"the-{kind}", "kind": kind, "bytes": 1000 + i})
        assert r.status_code == 201, (kind, r.text)

    # Nothing moves on one signature; everything is offered on two.
    client.post(f"/exchanges/{xid}/sign", headers=hh,
                json={"actor_id": host})
    assert client.get(f"/exchanges/{xid}/channel",
                      headers=hh).json()["open"] is False
    client.post(f"/exchanges/{xid}/sign", headers=gh,
                json={"actor_id": guest})
    chan = client.get(f"/exchanges/{xid}/channel", headers=gh).json()
    assert chan["open"] is True and chan["auto_download"] is False
    assert len(chan["items"]) == len(x.KINDS)

    # The executable kinds carry their warning across the wire.
    doc = client.get(f"/exchanges/{xid}", headers=gh).json()
    assert sorted(doc["runs_on_your_machine"]) == ["the-build", "the-source"]
    assert doc["runs_warning"] is not None

    # Each item is accepted by the side receiving it — and only that side.
    for item in chan["items"]:
        receiver, their = ((guest, gh) if item["direction"] == "host_to_guest"
                           else (host, hh))
        sender, senders = (host, hh) if receiver == guest else (guest, gh)
        r = client.post(f"/exchanges/{xid}/items/{item['id']}/accept",
                        headers=senders, json={"actor_id": sender})
        assert r.status_code == 422, "the sender accepted on their behalf"
        r = client.post(f"/exchanges/{xid}/items/{item['id']}/accept",
                        headers=their, json={"actor_id": receiver})
        assert r.status_code == 200, (item["kind"], r.text)

    done = client.get(f"/exchanges/{xid}", headers=hh).json()
    assert done["state"] == "delivered"
    assert all(i["accepted_at"] for i in done["items"])
