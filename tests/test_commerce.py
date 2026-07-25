"""Gifts and marketplace purchases — the endpoints that move money.

An over-counted like is embarrassing; a mis-credited payment is a dispute. So
most of this file is about who gets paid and who is allowed to pay, rather
than about the happy path.

Two properties get the most attention, because both are structural rather than
incidental: a listing nobody has offered for sale cannot be bought at all, and
a gift needs a verified adult behind it whoever it is going to.
"""

from qrme import commerce


def _who(client, name="Bea", birthdate="1990-01-01"):
    made = client.post("/interactors", json={
        "display_name": name, "birthdate": birthdate, "verified": True}).json()
    return {"authorization": f"Bearer {made['token']}"}


def _listing(client, **over):
    body = {"kind": "content", "title": "Pruning, properly",
            "provider_name": "Sam's Garden", "tags": ["garden"]}
    body.update(over)
    return client.post("/marketplace/listings", json=body).json()


def _desk(client, **over):
    body = {"owner_id": "bev", "display_name": "Bev Okafor",
            "trade": "Locksmith", "attestor": "bev", "basis": "met in person"}
    body.update(over)
    return client.post("/desks", json=body).json()


# --- a listing is a shop window until somebody offers it ------------------

def test_a_listing_nobody_offered_cannot_be_bought(client):
    """`POST /marketplace/listings` needs no token and never has, so anyone
    can create one naming any provider. That is harmless until a price can be
    attached — so the price lives somewhere only a token-holder can put it."""
    listing = _listing(client)
    out = client.post(f"/marketplace/listings/{listing['id']}/purchase",
                      json={"accept_price": 5.0}, headers=_who(client))
    assert out.status_code == 422
    assert "shop window" in out.json()["detail"]


def test_the_seller_is_the_token_not_the_body(client):
    listing = _listing(client)
    seller = _who(client, "Sam", "1985-01-01")
    offered = client.put(f"/marketplace/listings/{listing['id']}/offer",
                         json={"price": 12.5}, headers=seller).json()
    assert offered["price"] == 12.5
    # There is no field in OfferIn that could have named a different seller.
    assert offered["seller_id"]


def test_someone_else_cannot_take_over_an_offer(client):
    listing = _listing(client)
    client.put(f"/marketplace/listings/{listing['id']}/offer",
               json={"price": 12.5}, headers=_who(client, "Sam", "1985-01-01"))
    hijack = client.put(f"/marketplace/listings/{listing['id']}/offer",
                        json={"price": 1.0}, headers=_who(client, "Mal"))
    assert hijack.status_code == 422
    assert "someone else" in hijack.json()["detail"]


def test_an_offer_needs_a_price_above_zero(client):
    listing = _listing(client)
    out = client.put(f"/marketplace/listings/{listing['id']}/offer",
                     json={"price": 0.0}, headers=_who(client))
    assert out.status_code == 422


# --- buying ---------------------------------------------------------------

def test_buying_needs_the_price_confirmed(client):
    listing = _listing(client)
    client.put(f"/marketplace/listings/{listing['id']}/offer",
               json={"price": 12.5}, headers=_who(client, "Sam", "1985-01-01"))
    buyer = _who(client, "Bea")

    assert client.post(f"/marketplace/listings/{listing['id']}/purchase",
                       json={}, headers=buyer).status_code == 422
    assert client.post(f"/marketplace/listings/{listing['id']}/purchase",
                       json={"accept_price": 1.0},
                       headers=buyer).status_code == 422
    assert client.post(f"/marketplace/listings/{listing['id']}/purchase",
                       json={"accept_price": 12.5},
                       headers=buyer).status_code == 201


def test_a_purchase_credits_the_seller(client):
    from qrme import ledger

    listing = _listing(client)
    seller = _who(client, "Sam", "1985-01-01")
    offered = client.put(f"/marketplace/listings/{listing['id']}/offer",
                         json={"price": 12.5}, headers=seller).json()
    client.post(f"/marketplace/listings/{listing['id']}/purchase",
                json={"accept_price": 12.5}, headers=_who(client, "Bea"))

    totals = ledger.statement(offered["seller_id"])["totals"]
    assert totals["by_kind"]["listing_sale"] == 12.5
    assert totals["accrued"] == 12.5


def test_a_receipt_keeps_the_title_it_was_bought_under(client):
    """A receipt that changes when the seller edits the listing is not a
    receipt."""
    listing = _listing(client, title="Pruning, properly")
    client.put(f"/marketplace/listings/{listing['id']}/offer",
               json={"price": 5.0}, headers=_who(client, "Sam", "1985-01-01"))
    order = client.post(f"/marketplace/listings/{listing['id']}/purchase",
                        json={"accept_price": 5.0},
                        headers=_who(client, "Bea")).json()
    assert order["title"] == "Pruning, properly"
    assert order["status"] == "paid"
    assert "simulated" in order["payment"]


def test_you_cannot_buy_your_own_listing(client):
    """It would credit the seller with their own money and inflate the sales
    count on the listing at the same time."""
    listing = _listing(client)
    seller = _who(client, "Sam", "1985-01-01")
    client.put(f"/marketplace/listings/{listing['id']}/offer",
               json={"price": 5.0}, headers=seller)
    out = client.post(f"/marketplace/listings/{listing['id']}/purchase",
                      json={"accept_price": 5.0}, headers=seller)
    assert out.status_code == 422
    assert "your own listing" in out.json()["detail"]


def test_stock_runs_out(client):
    listing = _listing(client)
    client.put(f"/marketplace/listings/{listing['id']}/offer",
               json={"price": 5.0, "stock": 1},
               headers=_who(client, "Sam", "1985-01-01"))
    assert client.post(f"/marketplace/listings/{listing['id']}/purchase",
                       json={"accept_price": 5.0},
                       headers=_who(client, "Bea")).status_code == 201
    sold_out = client.post(f"/marketplace/listings/{listing['id']}/purchase",
                           json={"accept_price": 5.0},
                           headers=_who(client, "Cy", "1991-01-01"))
    assert sold_out.status_code == 422
    assert "sold out" in sold_out.json()["detail"]


def test_withdrawing_an_offer_keeps_the_listing_and_the_receipts(client):
    listing = _listing(client)
    seller = _who(client, "Sam", "1985-01-01")
    client.put(f"/marketplace/listings/{listing['id']}/offer",
               json={"price": 5.0}, headers=seller)
    buyer = _who(client, "Bea")
    client.post(f"/marketplace/listings/{listing['id']}/purchase",
                json={"accept_price": 5.0}, headers=buyer)

    client.request("DELETE", f"/marketplace/listings/{listing['id']}/offer",
                   headers=seller)
    refused = client.post(f"/marketplace/listings/{listing['id']}/purchase",
                          json={"accept_price": 5.0},
                          headers=_who(client, "Cy", "1991-01-01"))
    assert refused.status_code == 422
    # The shop window and the receipt both survive.
    assert any(x["id"] == listing["id"]
               for x in client.get("/marketplace/listings").json())
    assert len(client.get("/orders", headers=buyer).json()["orders"]) == 1


def test_only_the_seller_can_withdraw(client):
    listing = _listing(client)
    client.put(f"/marketplace/listings/{listing['id']}/offer",
               json={"price": 5.0}, headers=_who(client, "Sam", "1985-01-01"))
    out = client.request("DELETE",
                         f"/marketplace/listings/{listing['id']}/offer",
                         headers=_who(client, "Mal"))
    assert out.status_code == 403


def test_orders_and_sales_are_two_sides_of_the_same_row(client):
    listing = _listing(client)
    seller = _who(client, "Sam", "1985-01-01")
    buyer = _who(client, "Bea")
    client.put(f"/marketplace/listings/{listing['id']}/offer",
               json={"price": 5.0}, headers=seller)
    client.post(f"/marketplace/listings/{listing['id']}/purchase",
                json={"accept_price": 5.0}, headers=buyer)

    bought = client.get("/orders", headers=buyer).json()["orders"]
    sold = client.get("/marketplace/sales", headers=seller).json()["sales"]
    assert len(bought) == len(sold) == 1
    assert bought[0]["id"] == sold[0]["id"]


# --- gifting --------------------------------------------------------------

def test_gifting_needs_a_verified_adult(client):
    """Not because the recipient is sensitive — because the giver is. An
    unverified age is not evidence of an adult."""
    desk = _desk(client)
    did = desk["desk_id"]

    assert client.post(f"/desks/{did}/gift",
                       json={"amount": 10}).status_code == 401

    unaged = client.post("/interactors", json={"display_name": "Anon"}).json()
    no_birthdate = {"authorization": f"Bearer {unaged['token']}"}
    out = client.post(f"/desks/{did}/gift", json={"amount": 10},
                      headers=no_birthdate)
    assert out.status_code == 403
    assert "verified birthdate" in out.json()["detail"]

    minor = _who(client, "Kid", "2015-01-01")
    assert client.post(f"/desks/{did}/gift", json={"amount": 10},
                       headers=minor).status_code == 403

    assert client.post(f"/desks/{did}/gift", json={"amount": 10},
                       headers=_who(client)).status_code == 201


def test_a_gift_credits_the_person_behind_the_desk(client):
    from qrme import ledger

    desk = _desk(client, owner_id="bev")
    client.post(f"/desks/{desk['desk_id']}/gift",
                json={"amount": 10, "note": "thanks!"}, headers=_who(client))
    totals = ledger.statement("bev")["totals"]
    assert totals["by_kind"]["gift"] == 10.0


def test_the_beneficiary_cannot_be_chosen_by_the_giver(client):
    """A body-supplied beneficiary would let anyone route a gift meant for a
    performer into their own balance."""
    from qrme import ledger

    desk = _desk(client, owner_id="bev")
    client.post(f"/desks/{desk['desk_id']}/gift",
                json={"amount": 10, "beneficiary": "attacker"},
                headers=_who(client))
    assert ledger.statement("attacker")["totals"]["accrued"] == 0
    assert ledger.statement("bev")["totals"]["accrued"] == 10.0


def test_a_single_gift_is_capped(client):
    """A cap does not make gifting safe; it removes the one-tap-empties-an-
    account outcome while the rest stays honestly out of scope."""
    desk = _desk(client)
    out = client.post(f"/desks/{desk['desk_id']}/gift",
                      json={"amount": commerce.GIFT_MAX + 1},
                      headers=_who(client))
    assert out.status_code == 422
    assert "capped" in out.json()["detail"]


def test_a_gift_says_it_buys_nothing_and_cannot_be_reversed(client):
    desk = _desk(client)
    out = client.post(f"/desks/{desk['desk_id']}/gift", json={"amount": 5},
                      headers=_who(client)).json()
    assert out["refundable"] is False
    assert "simulated" in out["payment"]
    assert "not a purchase" in out["note_to_giver"]


def test_a_gift_needs_an_amount_above_zero(client):
    desk = _desk(client)
    assert client.post(f"/desks/{desk['desk_id']}/gift", json={"amount": 0},
                       headers=_who(client)).status_code == 422


def test_only_a_person_can_be_gifted(client):
    """A gift goes to somebody. A listing and a room message are not
    somebody."""
    desk = _desk(client)
    assert client.post(f"/listings/{desk['desk_id']}/gift", json={"amount": 5},
                       headers=_who(client)).status_code == 404


def test_gifting_a_rated_desk_needs_the_adult_gate_too(client):
    """The giver being an adult and the surface being 18+ answer different
    questions, and neither substitutes for the other."""
    desk = _desk(client, owner_id="perf", attestor="perf",
                 display_name="Vivienne Marlowe", rated=True,
                 view_style="stage")
    did = desk["desk_id"]
    assert client.post(f"/desks/{did}/gift", json={"amount": 10},
                       headers=_who(client, "Kid", "2015-01-01")
                       ).status_code == 403
    assert client.post(f"/desks/{did}/gift", json={"amount": 10},
                       headers=_who(client)).status_code == 201
    # And the tip jar is behind the same gate as everything else about it.
    assert client.get(f"/desks/{did}/gifts",
                      headers=_who(client, "Kid2", "2015-02-02")
                      ).status_code == 403


def test_the_tip_jar_totals_up(client):
    desk = _desk(client)
    client.post(f"/desks/{desk['desk_id']}/gift", json={"amount": 5},
                headers=_who(client, "Bea"))
    client.post(f"/desks/{desk['desk_id']}/gift", json={"amount": 7.5},
                headers=_who(client, "Cy", "1991-01-01"))
    jar = client.get(f"/desks/{desk['desk_id']}/gifts").json()
    assert jar["total"] == 12.5
    assert len(jar["gifts"]) == 2
    assert jar["cap_per_gift"] == commerce.GIFT_MAX


def test_gifting_something_that_does_not_exist_is_404(client):
    assert client.post("/desks/dsk_nope/gift", json={"amount": 5},
                       headers=_who(client)).status_code == 404
