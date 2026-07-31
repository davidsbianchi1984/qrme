"""The creator ledger: one row per money event, written at sale time.

Everything a creator earns on the marketplace — priced pack sales
(knowledge, robot task, and rated packs alike) and license fees — lands
here the moment the transaction clears, attributed to the earning
creator's ``owner_id``. A statement is therefore a record, not a
reconstruction; a payout sweeps the accrued balance and stamps every
entry with its payout id. Money is simulated, like every payment on the
platform — the accounting is real.

**A currency is part of an amount, not a label on it.** A creator may price
one profile in dollars and another in yen — nothing stops them, and nothing
should — and this file used to add the two together. ¥100 plus $100 came back
as ``accrued: 200``, tagged with whichever currency happened to be newest,
and the payout swept both into one figure called ``total``. Three native
shells rendered that number with a currency symbol in front of it.

Nothing was wrong with the entries; each row carried its own currency all
along. The arithmetic over them was wrong, in the one place where a wrong
number looks exactly like a right one. So totals are now kept **per currency**
throughout, and a payout settles **one currency at a time** — which is what a
transfer is anyway; there is no such thing as a payment of ¥100 plus $100.
"""

from __future__ import annotations

from . import db


def credit(beneficiary: str, kind: str, ref: str, amount: float,
           currency: str = "USD", memo: str | None = None) -> str:
    """Record one earning at transaction time. No-op for zero amounts —
    free downloads are not money events."""
    if amount <= 0:
        return ""
    conn = db.connect()
    entry_id = db.new_id("led")
    conn.execute(
        "INSERT INTO ledger (id, beneficiary, kind, ref, memo, amount,"
        " currency, status, payout_id, created_at)"
        " VALUES (?,?,?,?,?,?,?,'accrued',NULL,?)",
        (entry_id, beneficiary, kind, ref, memo, amount, currency,
         db.utcnow()))
    conn.commit()
    return entry_id


def _totals(rows: list[dict]) -> dict:
    """accrued / paid / lifetime and a per-kind breakdown over one currency's
    worth of entries. Called once per currency, never across them."""
    accrued = sum(r["amount"] for r in rows if r["status"] == "accrued")
    paid = sum(r["amount"] for r in rows if r["status"] == "paid")
    by_kind: dict[str, float] = {}
    for r in rows:
        by_kind[r["kind"]] = round(by_kind.get(r["kind"], 0) + r["amount"], 2)
    return {"accrued": round(accrued, 2), "paid": round(paid, 2),
            "lifetime": round(accrued + paid, 2), "by_kind": by_kind}


def settlement_currency(rows: list[dict]) -> str:
    """Which currency this account's headline figures are stated in.

    The most-earned-in one — most entries, ties broken by the largest lifetime
    and then alphabetically, so the same account always answers the same way.
    It used to be ``rows[0]["currency"]``: whichever sale happened to be most
    recent, which made the headline change currency as sales arrived without
    any of the numbers under it changing.
    """
    if not rows:
        return "USD"
    seen: dict[str, tuple[int, float]] = {}
    for r in rows:
        n, total = seen.get(r["currency"], (0, 0.0))
        seen[r["currency"]] = (n + 1, total + r["amount"])
    return sorted(seen, key=lambda c: (-seen[c][0], -seen[c][1], c))[0]


def statement(owner_id: str) -> dict:
    """The creator's full statement: every entry, newest first, with totals
    kept per currency and never summed across them.

    ``totals`` states the settlement currency's figures — the one a payout
    would sweep if asked for no currency in particular — and ``by_currency``
    holds every currency including that one, so a caller reading only the
    headline is reading something true rather than something averaged.
    ``mixed`` says whether there is anything the headline leaves out, which is
    the question a screen needs answered before it draws a single figure.
    """
    rows = [dict(r) for r in db.connect().execute(
        "SELECT * FROM ledger WHERE beneficiary=?"
        " ORDER BY created_at DESC, rowid DESC", (owner_id,)).fetchall()]
    currencies = sorted({r["currency"] for r in rows})
    by_currency = {c: _totals([r for r in rows if r["currency"] == c])
                   for c in currencies}
    settle = settlement_currency(rows)
    totals = dict(by_currency.get(settle) or _totals([]))
    totals["mixed"] = len(currencies) > 1
    return {
        "owner_id": owner_id,
        "entries": rows,
        "totals": totals,
        "by_currency": by_currency,
        "currencies": currencies,
        "currency": settle,
    }


def payout(owner_id: str, currency: str | None = None) -> dict | None:
    """Sweep one currency's accrued balance into a payout (simulated
    transfer): every accrued entry in that currency is stamped paid under one
    payout id. None when nothing is accrued in it.

    One currency, because a transfer is a movement of money and there is no
    money that is partly yen. ``currency=None`` means the settlement currency
    — so a client that has never thought about this (all three native shells
    post an empty body) sweeps the account's main balance and gets a receipt
    that names it, rather than one figure covering two kinds of money.

    ``remaining`` lists the currencies still holding a balance afterwards, so
    a caller can tell "you have been paid" from "you have been paid some of
    it" without a second request.
    """
    conn = db.connect()
    every = [dict(r) for r in conn.execute(
        "SELECT id, amount, currency, status FROM ledger WHERE beneficiary=?",
        (owner_id,)).fetchall()]
    accrued = [r for r in every if r["status"] == "accrued"]
    if not accrued:
        return None
    # The default is the currency the statement puts at the top, so pressing
    # the button pays out the figure the screen was showing. Settled over the
    # whole ledger rather than over what is accrued, so the headline does not
    # change currency the moment a payout clears — and falling back to the
    # accrued rows when the headline currency is already paid, because "your
    # main balance is empty" is not a reason to refuse the other one.
    settle = currency or settlement_currency(every)
    rows = [r for r in accrued if r["currency"] == settle]
    if not rows and currency is None:
        settle = settlement_currency(accrued)
        rows = [r for r in accrued if r["currency"] == settle]
    if not rows:
        return None
    payout_id = db.new_id("pay")
    conn.execute(
        "UPDATE ledger SET status='paid', payout_id=? WHERE beneficiary=?"
        " AND status='accrued' AND currency=?",
        (payout_id, owner_id, settle))
    conn.commit()
    remaining = sorted({r["currency"] for r in accrued
                        if r["currency"] != settle})
    return {"payout_id": payout_id, "owner_id": owner_id,
            "total": round(sum(r["amount"] for r in rows), 2),
            "currency": settle,
            "entries": len(rows), "at": db.utcnow(),
            "remaining": remaining,
            "note": "simulated transfer — entries are stamped with this "
                    "payout id"}
