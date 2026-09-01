"""A shop is not a desk, and the difference is everything it doesn't do.

## The finding

The desk shipped as "a geek squad for any industry" — sessions, consent,
connections, lent programs. What the platform still had nowhere to put was
the ordinary case: a business or a person who simply *sells things*. The
nearest shelf was the desk, and hanging a storefront on the connection
apparatus would make "buy a candle" carry session semantics it must not.

    asked     can a specialist serve a caller at a counter
    mattered  can a business or a person sell goods and services at all

## What this file drives

`qrme/shops.py` on its five rules, each from the outside:

1. one shop per profile — a second open is an edit, not a duplicate;
2. an offering states kind, price with its own currency, and availability;
3. the buyer is an interactor — the same identity the tandem maintains;
4. money is simulated, the accounting real — fulfilment credits the ledger
   as `shop_sale`, and *only* fulfilment does;
5. both sides can let go — the buyer while `placed`, the seller by
   declining — and a settled order refuses every further move by name.

And the structural claim in the title: none of the desk-session tables gain
a row however much shopping happens.
"""

from __future__ import annotations

import pytest

from qrme import db


ADULT = {"birthdate": "1984-06-01"}


def _seller(client, name="Marta"):
    r = client.post("/profiles", json={
        "owner_id": f"own-{name.lower()}", "kind": "self",
        "display_name": name, "persona": "Maker of hand-poured candles.",
        "verification": ADULT, "plan": "pro"})
    assert r.status_code == 201, r.text
    p = r.json()
    return p["id"], {"authorization": f"Bearer {p['owner_token']}"}


def _buyer(client, name="Sam"):
    r = client.post("/interactors",
                    json={"display_name": name, "birthdate": "2000-01-15"})
    assert r.status_code == 201, r.text
    b = r.json()
    return b["id"], {"authorization": f"Bearer {b['token']}"}


def _shop(client, head, pid, name="Marta's Candles", tag="crafts"):
    r = client.post("/shops", json={"profile_id": pid, "name": name,
                                    "blurb": "Hand-poured.", "tag": tag},
                    headers=head)
    assert r.status_code == 201, r.text
    return r.json()


def _offering(client, head, shop_id, kind="goods", title="Beeswax pillar",
              price=18.0, **extra):
    r = client.post(f"/shops/{shop_id}/offerings",
                    json={"kind": kind, "title": title, "price": price,
                          **extra}, headers=head)
    assert r.status_code == 201, r.text
    return r.json()


# --- rule 1: one shop per profile -------------------------------------------

def test_a_second_open_is_an_edit_not_a_duplicate(client):
    pid, head = _seller(client)
    first = _shop(client, head, pid)
    again = client.post("/shops", json={"profile_id": pid,
                                        "name": "Marta's Candles & Wicks"},
                        headers=head).json()
    assert again["id"] == first["id"]
    assert again["name"] == "Marta's Candles & Wicks"
    n = db.connect().execute("SELECT COUNT(*) n FROM shops").fetchone()["n"]
    assert n == 1


def test_opening_somebody_elses_shop_is_refused(client):
    pid, _ = _seller(client)
    _, other_head = _seller(client, "Rival")
    r = client.post("/shops", json={"profile_id": pid, "name": "Takeover"},
                    headers=other_head)
    assert r.status_code in (401, 403), r.text


# --- rule 2: the offering says what it is -----------------------------------

def test_an_offering_needs_a_real_kind_and_a_non_negative_price(client):
    pid, head = _seller(client)
    shop = _shop(client, head, pid)
    r = client.post(f"/shops/{shop['id']}/offerings",
                    json={"kind": "vibes", "title": "x", "price": 1},
                    headers=head)
    assert r.status_code == 422 and "goods or a service" in r.json()["detail"]
    r = client.post(f"/shops/{shop['id']}/offerings",
                    json={"kind": "goods", "title": "x", "price": -1},
                    headers=head)
    assert r.status_code == 422 and "zero or more" in r.json()["detail"]


def test_the_card_carries_offerings_and_the_list_counts_them(client):
    pid, head = _seller(client)
    shop = _shop(client, head, pid)
    _offering(client, head, shop["id"])
    _offering(client, head, shop["id"], kind="service",
              title="Candle-making class", price=60.0,
              availability="made_to_order")
    cards = client.get("/shops").json()
    assert [c["offerings_count"] for c in cards] == [2]
    card = client.get(f"/shops/{shop['id']}").json()
    assert {o["kind"] for o in card["offerings"]} == {"goods", "service"}
    assert card["seller"] == "Marta"


def test_browsing_needs_no_token_and_a_tag_filters(client):
    pid, head = _seller(client)
    _shop(client, head, pid)
    pid2, head2 = _seller(client, "Beno")
    _shop(client, head2, pid2, name="Beno's Repairs", tag="electronics")
    bare = client.get("/shops")            # no auth header on this call
    assert bare.status_code == 200 and len(bare.json()) == 2
    only = client.get("/shops", params={"tag": "electronics"}).json()
    assert [s["name"] for s in only] == ["Beno's Repairs"]


def test_a_retired_offering_leaves_the_shelf_not_the_record(client):
    pid, head = _seller(client)
    shop = _shop(client, head, pid)
    off = _offering(client, head, shop["id"])
    bid, bhead = _buyer(client)
    client.post(f"/shops/{shop['id']}/orders",
                json={"offering_id": off["id"], "buyer_id": bid},
                headers=bhead)
    r = client.delete(f"/shops/{shop['id']}/offerings/{off['id']}",
                      headers=head)
    assert r.status_code == 200 and r.json()["retired"] == 1
    assert client.get(f"/shops/{shop['id']}").json()["offerings"] == []
    # The order that references it still knows what it was for.
    book = client.get(f"/shops/{shop['id']}/orders", headers=head).json()
    assert book[0]["title"] == "Beeswax pillar"
    # And nobody can order it now.
    r = client.post(f"/shops/{shop['id']}/orders",
                    json={"offering_id": off["id"], "buyer_id": bid},
                    headers=bhead)
    assert r.status_code == 422 and "retired" in r.json()["detail"]


# --- rule 3: the buyer is an interactor -------------------------------------

def test_an_order_needs_the_buyers_own_token(client):
    pid, head = _seller(client)
    shop = _shop(client, head, pid)
    off = _offering(client, head, shop["id"])
    bid, _ = _buyer(client)
    _, other_head = _buyer(client, "Mallory")
    r = client.post(f"/shops/{shop['id']}/orders",
                    json={"offering_id": off["id"], "buyer_id": bid},
                    headers=other_head)
    assert r.status_code in (401, 403), (
        "an order was placed in somebody else's name")


def test_a_service_is_ordered_once_not_by_quantity(client):
    pid, head = _seller(client)
    shop = _shop(client, head, pid)
    svc = _offering(client, head, shop["id"], kind="service",
                    title="Class", price=60.0)
    bid, bhead = _buyer(client)
    r = client.post(f"/shops/{shop['id']}/orders",
                    json={"offering_id": svc["id"], "buyer_id": bid,
                          "quantity": 3}, headers=bhead)
    assert r.status_code == 422
    assert "ordered once" in r.json()["detail"]


# --- rule 4: fulfilment is the money event ----------------------------------

def _ledger_rows():
    return [dict(r) for r in db.connect().execute(
        "SELECT * FROM ledger WHERE kind='shop_sale'").fetchall()]


def test_only_fulfilment_credits_the_ledger(client):
    pid, head = _seller(client)
    shop = _shop(client, head, pid)
    off = _offering(client, head, shop["id"])
    bid, bhead = _buyer(client)
    order = client.post(f"/shops/{shop['id']}/orders",
                        json={"offering_id": off["id"], "buyer_id": bid,
                              "quantity": 2}, headers=bhead).json()
    assert order["amount"] == 36.0
    assert _ledger_rows() == [], "money moved before anything was fulfilled"
    client.post(f"/shops/{shop['id']}/orders/{order['id']}/advance",
                json={"party": "seller", "to": "accepted"}, headers=head)
    assert _ledger_rows() == [], "acceptance is not a sale"
    done = client.post(f"/shops/{shop['id']}/orders/{order['id']}/advance",
                       json={"party": "seller", "to": "fulfilled"},
                       headers=head).json()
    assert done["status"] == "fulfilled"
    rows = _ledger_rows()
    assert len(rows) == 1 and rows[0]["amount"] == 36.0
    assert rows[0]["beneficiary"] == "own-marta"


def test_a_declined_order_costs_nobody_anything(client):
    pid, head = _seller(client)
    shop = _shop(client, head, pid)
    off = _offering(client, head, shop["id"])
    bid, bhead = _buyer(client)
    order = client.post(f"/shops/{shop['id']}/orders",
                        json={"offering_id": off["id"], "buyer_id": bid},
                        headers=bhead).json()
    client.post(f"/shops/{shop['id']}/orders/{order['id']}/advance",
                json={"party": "seller", "to": "declined"}, headers=head)
    assert _ledger_rows() == []


# --- rule 5: both sides can let go ------------------------------------------

def test_the_buyer_can_cancel_while_placed_and_not_after(client):
    pid, head = _seller(client)
    shop = _shop(client, head, pid)
    off = _offering(client, head, shop["id"])
    bid, bhead = _buyer(client)
    order = client.post(f"/shops/{shop['id']}/orders",
                        json={"offering_id": off["id"], "buyer_id": bid},
                        headers=bhead).json()
    r = client.post(f"/shops/{shop['id']}/orders/{order['id']}/advance",
                    json={"party": "buyer", "to": "cancelled"},
                    headers=bhead)
    assert r.status_code == 200 and r.json()["status"] == "cancelled"
    r = client.post(f"/shops/{shop['id']}/orders/{order['id']}/advance",
                    json={"party": "buyer", "to": "cancelled"},
                    headers=bhead)
    assert r.status_code == 422 and "settled" in r.json()["detail"]


def test_the_buyer_cannot_fulfil_their_own_order(client):
    """The party is verified against its credential and the state machine —
    a buyer who could mark an order fulfilled would be a buyer who could
    credit the seller's ledger with the seller's money."""
    pid, head = _seller(client)
    shop = _shop(client, head, pid)
    off = _offering(client, head, shop["id"])
    bid, bhead = _buyer(client)
    order = client.post(f"/shops/{shop['id']}/orders",
                        json={"offering_id": off["id"], "buyer_id": bid},
                        headers=bhead).json()
    # Lying about the party fails on the credential…
    r = client.post(f"/shops/{shop['id']}/orders/{order['id']}/advance",
                    json={"party": "seller", "to": "fulfilled"},
                    headers=bhead)
    assert r.status_code in (401, 403)
    # …and telling the truth fails on the state machine.
    r = client.post(f"/shops/{shop['id']}/orders/{order['id']}/advance",
                    json={"party": "buyer", "to": "fulfilled"},
                    headers=bhead)
    assert r.status_code == 422


def test_each_party_reads_their_own_list_and_only_theirs(client):
    pid, head = _seller(client)
    shop = _shop(client, head, pid)
    off = _offering(client, head, shop["id"])
    bid, bhead = _buyer(client)
    client.post(f"/shops/{shop['id']}/orders",
                json={"offering_id": off["id"], "buyer_id": bid},
                headers=bhead)
    assert len(client.get(f"/shops/{shop['id']}/orders",
                          headers=head).json()) == 1
    assert len(client.get(f"/shops/orders/of/{bid}",
                          headers=bhead).json()) == 1
    # The seller's book needs the seller; the buyer's list needs the buyer.
    assert client.get(f"/shops/{shop['id']}/orders",
                      headers=bhead).status_code in (401, 403)
    assert client.get(f"/shops/orders/of/{bid}",
                      headers=head).status_code in (401, 403)


# --- the title's claim ------------------------------------------------------

def test_shopping_touches_no_desk_table(client):
    """The structural half of "a shop is not a desk": a full shopping day —
    open, list, order, fulfil — writes nothing into the desk-session or
    desk-connection tables, because there is nothing to write. A shop that
    opened sessions would fail here first."""
    pid, head = _seller(client)
    shop = _shop(client, head, pid)
    off = _offering(client, head, shop["id"])
    bid, bhead = _buyer(client)
    order = client.post(f"/shops/{shop['id']}/orders",
                        json={"offering_id": off["id"], "buyer_id": bid},
                        headers=bhead).json()
    client.post(f"/shops/{shop['id']}/orders/{order['id']}/advance",
                json={"party": "seller", "to": "accepted"}, headers=head)
    client.post(f"/shops/{shop['id']}/orders/{order['id']}/advance",
                json={"party": "seller", "to": "fulfilled"}, headers=head)
    conn = db.connect()
    for table in ("desks", "desk_sessions", "desk_connections"):
        n = conn.execute(f"SELECT COUNT(*) n FROM {table}").fetchone()["n"]
        assert n == 0, f"shopping wrote into {table}"
