"""The creator ledger: one row per money event, written at sale time.

Everything a creator earns on the marketplace — priced pack sales
(knowledge, robot task, and rated packs alike) and license fees — lands
here the moment the transaction clears, attributed to the earning
creator's ``owner_id``. A statement is therefore a record, not a
reconstruction; a payout sweeps the accrued balance and stamps every
entry with its payout id. Money is simulated, like every payment on the
platform — the accounting is real.
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


def statement(owner_id: str) -> dict:
    """The creator's full statement: every entry, newest first, with
    accrued / paid / lifetime totals and a per-kind breakdown."""
    rows = [dict(r) for r in db.connect().execute(
        "SELECT * FROM ledger WHERE beneficiary=?"
        " ORDER BY created_at DESC, rowid DESC", (owner_id,)).fetchall()]
    accrued = sum(r["amount"] for r in rows if r["status"] == "accrued")
    paid = sum(r["amount"] for r in rows if r["status"] == "paid")
    by_kind: dict[str, float] = {}
    for r in rows:
        by_kind[r["kind"]] = round(by_kind.get(r["kind"], 0) + r["amount"], 2)
    return {
        "owner_id": owner_id,
        "entries": rows,
        "totals": {"accrued": round(accrued, 2), "paid": round(paid, 2),
                   "lifetime": round(accrued + paid, 2),
                   "by_kind": by_kind},
        "currency": rows[0]["currency"] if rows else "USD",
    }


def payout(owner_id: str) -> dict | None:
    """Sweep the accrued balance into a payout (simulated transfer): every
    accrued entry is stamped paid under one payout id. None when nothing
    is accrued."""
    conn = db.connect()
    rows = conn.execute(
        "SELECT id, amount FROM ledger WHERE beneficiary=? AND"
        " status='accrued'", (owner_id,)).fetchall()
    if not rows:
        return None
    payout_id = db.new_id("pay")
    conn.execute(
        "UPDATE ledger SET status='paid', payout_id=? WHERE beneficiary=?"
        " AND status='accrued'", (payout_id, owner_id))
    conn.commit()
    return {"payout_id": payout_id, "owner_id": owner_id,
            "total": round(sum(r["amount"] for r in rows), 2),
            "entries": len(rows), "at": db.utcnow(),
            "note": "simulated transfer — entries are stamped with this "
                    "payout id"}
