"""Shops: standalone storefronts for goods and services.

A shop is not a desk. The desk is a service *counter* — sessions, consent,
connections, lent programs, all of it scoped to a live exchange between two
people. A shop opens nothing and lends nothing: it lists what a business or
a person sells, takes an order, and settles it. Conflating the two would
hang the whole connection apparatus on "buy a candle", which is exactly the
weight a storefront must not carry.

The rules, in the order a buyer meets them:

1. **One shop per profile.** "Whose shop is this" has one answer, and the
   marketplace card can say it. A business is a profile like any other.
2. **An offering says what it is.** Goods or a service, a price with its
   own currency, and an availability the seller states rather than an
   inventory the platform pretends to count.
3. **The buyer is an interactor.** JIM places orders through the same
   per-user interactor its tandem already maintains, so a purchase is
   attributable and revocable the way a conversation is — and nothing
   about the buyer crosses that the interactor record doesn't already hold.
4. **Money is simulated; the accounting is real.** Fulfilment credits the
   creator ledger exactly as a pack sale does — `shop_sale`, attributed to
   the shop profile's owner, in the offering's own currency.
5. **Both sides can let go.** The buyer cancels while an order is only
   `placed`; the seller declines or advances it. Nothing is charged before
   fulfilment, so there is nothing to refund — declining is free, in both
   senses.
"""

from __future__ import annotations

from . import db, ledger

OFFERING_KINDS = ("goods", "service")
AVAILABILITY = ("in_stock", "made_to_order", "unavailable")

#: placed -> accepted -> fulfilled, with two exits. One table rather than
#: per-route ifs, so "what may happen next" is a fact, not a scatter.
_NEXT = {
    "placed": {"seller": ("accepted", "declined"), "buyer": ("cancelled",)},
    "accepted": {"seller": ("fulfilled", "declined"), "buyer": ()},
    "fulfilled": {"seller": (), "buyer": ()},
    "declined": {"seller": (), "buyer": ()},
    "cancelled": {"seller": (), "buyer": ()},
}


class ShopError(ValueError):
    pass


def open_shop(profile_id: str, name: str, blurb: str | None,
              tag: str | None) -> dict:
    """Open the profile's shop, or update it — one per profile, so a second
    open is an edit rather than a duplicate."""
    if not (name or "").strip():
        raise ShopError("a shop needs a name people can find it by")
    conn = db.connect()
    row = conn.execute("SELECT id FROM shops WHERE profile_id=?",
                       (profile_id,)).fetchone()
    if row is None:
        shop_id = db.new_id("shp")
        conn.execute(
            "INSERT INTO shops (id, profile_id, name, blurb, tag, status,"
            " created_at) VALUES (?,?,?,?,?,'open',?)",
            (shop_id, profile_id, name.strip(), blurb, tag, db.utcnow()))
    else:
        shop_id = row["id"]
        conn.execute(
            "UPDATE shops SET name=?, blurb=?, tag=?, status='open'"
            " WHERE id=?", (name.strip(), blurb, tag, shop_id))
    conn.commit()
    return shop(shop_id)


def add_offering(shop_id: str, kind: str, title: str, blurb: str | None,
                 price: float, currency: str = "USD",
                 availability: str = "in_stock") -> dict:
    if kind not in OFFERING_KINDS:
        raise ShopError(
            f"unknown offering kind {kind!r}; a shop sells goods or a "
            "service")
    if not (title or "").strip():
        raise ShopError("an offering needs a title")
    if price < 0:
        raise ShopError("a price is zero or more — free is allowed, owed "
                        "is not")
    if availability not in AVAILABILITY:
        raise ShopError(
            f"unknown availability {availability!r}; expected one of "
            f"{', '.join(AVAILABILITY)}")
    _shop_row(shop_id)                        # exists, or raises
    conn = db.connect()
    offering_id = db.new_id("off")
    conn.execute(
        "INSERT INTO shop_offerings (id, shop_id, kind, title, blurb,"
        " price, currency, availability, retired, created_at)"
        " VALUES (?,?,?,?,?,?,?,?,0,?)",
        (offering_id, shop_id, kind, title.strip(), blurb, float(price),
         currency, availability, db.utcnow()))
    conn.commit()
    return _offering(offering_id)


def retire_offering(shop_id: str, offering_id: str) -> dict:
    """Off the shelf, not out of the record — orders that reference it keep
    their meaning."""
    off = _offering(offering_id)
    if off["shop_id"] != shop_id:
        raise ShopError("that offering belongs to another shop")
    conn = db.connect()
    conn.execute("UPDATE shop_offerings SET retired=1 WHERE id=?",
                 (offering_id,))
    conn.commit()
    return _offering(offering_id)


def shops(tag: str | None = None) -> list[dict]:
    """Every open shop, newest last — with its profile's public face, so a
    card is a card without a second lookup."""
    conn = db.connect()
    rows = conn.execute(
        "SELECT s.*, p.display_name AS seller FROM shops s"
        " JOIN profiles p ON p.id = s.profile_id"
        " WHERE s.status='open' ORDER BY s.created_at").fetchall()
    out = []
    for r in rows:
        if tag and (r["tag"] or "").lower() != tag.lower():
            continue
        d = dict(r)
        d["offerings"] = _count_offerings(r["id"])
        out.append(d)
    return out


def shop(shop_id: str) -> dict:
    row = _shop_row(shop_id)
    conn = db.connect()
    seller = conn.execute("SELECT display_name FROM profiles WHERE id=?",
                          (row["profile_id"],)).fetchone()
    out = dict(row)
    out["seller"] = seller["display_name"] if seller else None
    out["offerings"] = [dict(r) for r in conn.execute(
        "SELECT * FROM shop_offerings WHERE shop_id=? AND retired=0"
        " ORDER BY created_at", (shop_id,)).fetchall()]
    return out


def place_order(shop_id: str, offering_id: str, buyer_id: str,
                quantity: int = 1, note: str | None = None) -> dict:
    off = _offering(offering_id)
    if off["shop_id"] != shop_id:
        raise ShopError("that offering belongs to another shop")
    if off["retired"]:
        raise ShopError("that offering has been retired")
    if off["availability"] == "unavailable":
        raise ShopError("the seller lists that as unavailable right now")
    if quantity < 1:
        raise ShopError("quantity is at least one")
    if off["kind"] == "service" and quantity != 1:
        raise ShopError("a service is ordered once, not by quantity")
    conn = db.connect()
    order_id = db.new_id("ord")
    conn.execute(
        "INSERT INTO shop_orders (id, shop_id, offering_id, buyer_id,"
        " quantity, amount, currency, note, status, placed_at, settled_at)"
        " VALUES (?,?,?,?,?,?,?,?,'placed',?,NULL)",
        (order_id, shop_id, offering_id, buyer_id, int(quantity),
         round(off["price"] * quantity, 2), off["currency"], note,
         db.utcnow()))
    conn.commit()
    return order(order_id)


def advance_order(order_id: str, party: str, to: str) -> dict:
    """One transition at a time, by whoever may make it. Fulfilment is the
    money event: the ledger is credited here and nowhere else."""
    row = order(order_id)
    allowed = _NEXT[row["status"]].get(party, ())
    if to not in allowed:
        raise ShopError(
            f"an order that is {row['status']} cannot become {to} by the "
            f"{party}" + (f"; open moves: {', '.join(allowed)}" if allowed
                          else " — it is settled"))
    conn = db.connect()
    settled = to in ("fulfilled", "declined", "cancelled")
    conn.execute(
        "UPDATE shop_orders SET status=?, settled_at=? WHERE id=?",
        (to, db.utcnow() if settled else None, order_id))
    conn.commit()
    if to == "fulfilled":
        shop_row = _shop_row(row["shop_id"])
        owner = db.connect().execute(
            "SELECT owner_id FROM profiles WHERE id=?",
            (shop_row["profile_id"],)).fetchone()
        if owner and owner["owner_id"]:
            ledger.credit(owner["owner_id"], "shop_sale", order_id,
                          row["amount"], row["currency"],
                          memo=row["offering_id"])
    return order(order_id)


def order(order_id: str) -> dict:
    row = db.connect().execute(
        "SELECT o.*, f.title, f.kind FROM shop_orders o"
        " JOIN shop_offerings f ON f.id = o.offering_id"
        " WHERE o.id=?", (order_id,)).fetchone()
    if row is None:
        raise ShopError("no such order")
    return dict(row)


def orders_for_shop(shop_id: str) -> list[dict]:
    return [order(r["id"]) for r in db.connect().execute(
        "SELECT id FROM shop_orders WHERE shop_id=? ORDER BY placed_at",
        (shop_id,)).fetchall()]


def orders_for_buyer(buyer_id: str) -> list[dict]:
    return [order(r["id"]) for r in db.connect().execute(
        "SELECT id FROM shop_orders WHERE buyer_id=? ORDER BY placed_at",
        (buyer_id,)).fetchall()]


# -- internals ---------------------------------------------------------------

def _shop_row(shop_id: str):
    row = db.connect().execute("SELECT * FROM shops WHERE id=?",
                               (shop_id,)).fetchone()
    if row is None:
        raise ShopError("no such shop")
    return row


def _offering(offering_id: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM shop_offerings WHERE id=?", (offering_id,)).fetchone()
    if row is None:
        raise ShopError("no such offering")
    return dict(row)


def _count_offerings(shop_id: str) -> int:
    return db.connect().execute(
        "SELECT COUNT(*) AS n FROM shop_offerings WHERE shop_id=? AND"
        " retired=0", (shop_id,)).fetchone()["n"]
