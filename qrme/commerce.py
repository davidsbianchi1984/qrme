"""Gifts, and buying things on the marketplace.

The audience layer was about attention. This is about money, and the two need
different care: an over-counted like is embarrassing, a mis-credited payment is
a dispute.

**Money here is simulated.** Nothing in this repository moves real funds. What
it does do is write real rows on the creator's statement, alongside pack sales,
licence fees and venue placements, settling through the same payout sweep — so
the accounting is honest even though the payment is not real. Every response
that involves money says so in its own body rather than leaving it to a policy
page, because implying a payment processor that does not exist is the kind of
claim that gets believed.

Two structural decisions do most of the safety work here:

**A listing is a shop window; an offer is what makes it a shop.**
``POST /marketplace/listings`` needs no token and never has, so anybody can
create a listing naming any ``provider_name`` they like. That was harmless
while listings were discovery-only, and would stop being harmless the moment a
price could be attached to one. So the price and the seller live in a separate
``listing_offers`` row that only a token-holder can create, and the seller is
taken from that token rather than from the request body. A listing with no
offer cannot be bought — not by a check that could be forgotten, but because
there is nowhere for a price to be.

**A gift is not a small purchase.** A purchase exchanges money for a thing; a
gift sends money to a person and receives nothing, which is exactly the shape
that livestream tipping has repeatedly turned into a mechanism for exploiting
people who should not be spending. So gifts carry rules purchases do not:

* the giver must be a **verified adult**, whoever they are gifting;
* a single gift is capped (:data:`GIFT_MAX`);
* gifting a rated desk additionally runs the deployment's existing adult gate,
  as every other rated surface does.

Those are proportionate, not sufficient. A production deployment needs real
spend controls — running totals, cooling-off, parental controls, chargeback
handling — and this module does not pretend to be them. That gap is stated in
the docs rather than papered over, because a half-built safety feature that
looks whole is worse than an absent one.
"""

from __future__ import annotations

from . import db, ledger

# The most one gift can be. A cap does not make gifting safe; it removes the
# single worst outcome — one tap that empties an account — while the rest of
# the problem stays honestly out of scope.
GIFT_MAX = 500.0

GIFT_SUBJECTS = ("profile", "desk")


class CommerceError(ValueError):
    """A refusal with a reason worth showing the caller."""


# --- selling --------------------------------------------------------------

def offer(listing_id: str, seller_id: str, price: float,
          currency: str = "USD", stock: int | None = None) -> dict:
    """Put a price on a listing, making it buyable.

    ``seller_id`` comes from the caller's token, never from a request body:
    a body-supplied seller would let anyone route someone else's sales — or
    their own — through a listing they do not own.
    """
    if price <= 0:
        raise CommerceError(
            "an offer needs a price above zero; a listing with nothing to pay "
            "is already what a plain listing is")
    if stock is not None and stock < 0:
        raise CommerceError("stock cannot be negative")
    row = db.connect().execute(
        "SELECT id FROM listings WHERE id=?", (listing_id,)).fetchone()
    if row is None:
        raise CommerceError("no such listing")

    conn = db.connect()
    existing = conn.execute(
        "SELECT seller_id FROM listing_offers WHERE listing_id=?",
        (listing_id,)).fetchone()
    if existing and existing["seller_id"] != seller_id:
        raise CommerceError(
            "this listing is already offered for sale by someone else")
    if existing:
        conn.execute(
            "UPDATE listing_offers SET price=?, currency=?, stock=?,"
            " status='open' WHERE listing_id=?",
            (price, currency, stock, listing_id))
    else:
        conn.execute(
            "INSERT INTO listing_offers (listing_id, seller_id, price,"
            " currency, stock, status, created_at)"
            " VALUES (?,?,?,?,?, 'open', ?)",
            (listing_id, seller_id, price, currency, stock, db.utcnow()))
    conn.commit()
    return offer_for(listing_id)


def offer_for(listing_id: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM listing_offers WHERE listing_id=?",
        (listing_id,)).fetchone()
    if row is None:
        return None
    return {
        "listing_id": row["listing_id"], "seller_id": row["seller_id"],
        "price": row["price"], "currency": row["currency"],
        "stock": row["stock"], "status": row["status"],
        "created_at": row["created_at"],
        "sold": sold_count(listing_id),
        "payment": "simulated — the sale is recorded on the seller's "
                   "statement and settles through the creator payout sweep",
    }


def withdraw(listing_id: str, seller_id: str) -> dict:
    """Stop selling. The listing survives as a shop window, and past orders
    survive as receipts."""
    row = db.connect().execute(
        "SELECT seller_id FROM listing_offers WHERE listing_id=?",
        (listing_id,)).fetchone()
    if row is None:
        raise CommerceError("this listing is not for sale")
    if row["seller_id"] != seller_id:
        raise CommerceError("not your offer")
    conn = db.connect()
    conn.execute("UPDATE listing_offers SET status='closed' WHERE listing_id=?",
                 (listing_id,))
    conn.commit()
    return offer_for(listing_id)


def sold_count(listing_id: str) -> int:
    return db.connect().execute(
        "SELECT COUNT(*) FROM orders WHERE listing_id=? AND status='paid'",
        (listing_id,)).fetchone()[0]


# --- buying ---------------------------------------------------------------

def purchase(listing_id: str, buyer_id: str,
             accept_price: float | None = None) -> dict:
    """Buy a listing.

    ``accept_price`` must match, the same explicit step priced packs use. The
    price is read from the offer rather than the request, so agreeing to a
    number is agreeing to *the* number and not merely stating one.
    """
    conn = db.connect()
    listing = conn.execute("SELECT * FROM listings WHERE id=?",
                           (listing_id,)).fetchone()
    if listing is None:
        raise CommerceError("no such listing")

    row = conn.execute("SELECT * FROM listing_offers WHERE listing_id=?",
                       (listing_id,)).fetchone()
    if row is None:
        raise CommerceError(
            "this listing is a shop window, not a shop — nobody has offered "
            "it for sale, so there is no price and no seller to pay")
    if row["status"] != "open":
        raise CommerceError("this listing is no longer for sale")
    if row["seller_id"] == buyer_id:
        raise CommerceError(
            "this is your own listing — buying it would credit you with your "
            "own money and inflate your sales count")
    if row["stock"] is not None and row["stock"] <= 0:
        raise CommerceError("this listing is sold out")

    price = row["price"]
    if accept_price is None or round(accept_price, 2) != round(price, 2):
        raise CommerceError(
            f"this costs {price:.2f} {row['currency']}; send "
            f"accept_price={price:.2f} to confirm")

    order_id = db.new_id("ord")
    entry_id = ledger.credit(
        beneficiary=row["seller_id"], kind="listing_sale", ref=order_id,
        amount=price, currency=row["currency"],
        memo=f"marketplace sale — {listing['title']}")
    conn.execute(
        "INSERT INTO orders (id, listing_id, title, buyer_id, seller_id,"
        " price, currency, ledger_ref, status, created_at)"
        " VALUES (?,?,?,?,?,?,?,?, 'paid', ?)",
        (order_id, listing_id, listing["title"], buyer_id, row["seller_id"],
         price, row["currency"], entry_id or None, db.utcnow()))
    if row["stock"] is not None:
        conn.execute(
            "UPDATE listing_offers SET stock = stock - 1 WHERE listing_id=?",
            (listing_id,))
    conn.commit()
    return order(order_id)


def order(order_id: str) -> dict | None:
    row = db.connect().execute("SELECT * FROM orders WHERE id=?",
                               (order_id,)).fetchone()
    if row is None:
        return None
    return {
        "id": row["id"], "listing_id": row["listing_id"],
        # Copied at purchase rather than joined: a receipt that changes when
        # the seller edits the listing is not a receipt.
        "title": row["title"], "buyer_id": row["buyer_id"],
        "seller_id": row["seller_id"], "price": row["price"],
        "currency": row["currency"], "status": row["status"],
        "ledger_entry": row["ledger_ref"], "created_at": row["created_at"],
        "payment": "simulated — no real funds moved; the sale is recorded on "
                   "the seller's statement",
    }


def orders_for_buyer(buyer_id: str) -> list[dict]:
    rows = db.connect().execute(
        "SELECT id FROM orders WHERE buyer_id=? ORDER BY created_at DESC,"
        " rowid DESC", (buyer_id,)).fetchall()
    return [order(r["id"]) for r in rows]


def orders_for_seller(seller_id: str) -> list[dict]:
    rows = db.connect().execute(
        "SELECT id FROM orders WHERE seller_id=? ORDER BY created_at DESC,"
        " rowid DESC", (seller_id,)).fetchall()
    return [order(r["id"]) for r in rows]


# --- gifting --------------------------------------------------------------

def beneficiary_of(kind: str, subject_id: str) -> str | None:
    """Whose statement a gift to this subject lands on.

    Read from the subject rather than accepted from the giver: a
    body-supplied beneficiary would let anyone direct a gift meant for a
    performer into their own balance.
    """
    conn = db.connect()
    if kind == "desk":
        row = conn.execute("SELECT owner_id FROM desks WHERE id=?",
                           (subject_id,)).fetchone()
    elif kind == "profile":
        row = conn.execute("SELECT owner_id FROM profiles WHERE id=?",
                           (subject_id,)).fetchone()
    else:
        return None
    return row["owner_id"] if row else None


def gift(kind: str, subject_id: str, giver_id: str, amount: float,
         note: str | None = None, currency: str = "USD") -> dict:
    """Send value to whoever is behind this profile or desk.

    The age check is *not* done here — the router runs the deployment's single
    existing verified-adult implementation and refuses before calling in. This
    function refuses everything that is not about age, so the two cannot drift
    into disagreeing about what a valid gift is.
    """
    if kind not in GIFT_SUBJECTS:
        raise CommerceError(
            f"cannot gift a {kind!r}; a gift goes to a person, so it applies "
            f"to {' and '.join(GIFT_SUBJECTS)}")
    if amount <= 0:
        raise CommerceError("a gift needs an amount above zero")
    if amount > GIFT_MAX:
        raise CommerceError(
            f"a single gift is capped at {GIFT_MAX:.2f} — send less, or send "
            f"more than once, so one tap cannot empty an account")

    beneficiary = beneficiary_of(kind, subject_id)
    if beneficiary is None:
        raise CommerceError(f"no such {kind}")
    if beneficiary == giver_id:
        raise CommerceError(
            "this is yours — gifting it would move money from you to you and "
            "leave a gift on the record that nobody sent")

    gift_id = db.new_id("gft")
    entry_id = ledger.credit(
        beneficiary=beneficiary, kind="gift", ref=gift_id, amount=amount,
        currency=currency, memo=f"gift on {kind} {subject_id}")
    conn = db.connect()
    conn.execute(
        "INSERT INTO gifts (id, subject_kind, subject_id, giver_id,"
        " beneficiary, amount, currency, note, ledger_ref, created_at)"
        " VALUES (?,?,?,?,?,?,?,?,?,?)",
        (gift_id, kind, subject_id, giver_id, beneficiary, amount, currency,
         note, entry_id or None, db.utcnow()))
    conn.commit()
    return {
        "id": gift_id, "subject_kind": kind, "subject_id": subject_id,
        "giver_id": giver_id, "amount": amount, "currency": currency,
        "note": note, "ledger_entry": entry_id or None,
        "payment": "simulated — no real funds moved; the gift is recorded on "
                   "the recipient's statement",
        # Said at the point of giving, not in a policy page: a gift buys
        # nothing, so there is nothing to fail to deliver and nothing to
        # return.
        "refundable": False,
        "note_to_giver": "A gift is not a purchase — nothing is delivered in "
                         "return, and it cannot be reversed here.",
    }


def gifts_for(kind: str, subject_id: str) -> list[dict]:
    rows = db.connect().execute(
        "SELECT * FROM gifts WHERE subject_kind=? AND subject_id=?"
        " ORDER BY created_at DESC, rowid DESC",
        (kind, subject_id)).fetchall()
    return [{"id": r["id"], "giver_id": r["giver_id"], "amount": r["amount"],
             "currency": r["currency"], "note": r["note"],
             "created_at": r["created_at"]} for r in rows]


def gift_total(kind: str, subject_id: str) -> float:
    total = db.connect().execute(
        "SELECT COALESCE(SUM(amount), 0) FROM gifts WHERE subject_kind=? AND"
        " subject_id=?", (kind, subject_id)).fetchone()[0]
    return round(total, 2)
