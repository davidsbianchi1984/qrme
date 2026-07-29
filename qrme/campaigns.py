"""Crowdfunding on a profile, with proceeds routed where the user said.

Spec [0020], example two: a departed actor's persona keeps working —
"corporations might use this gentleman in commercial and supply crowdfunding
for any loved ones, left behind or organizations for donations, wherever the
proceeds might go up to the user."

Two rules carry the whole feature:

- **The user routes the money, in advance.** A profile's owner designates
  loved ones and organizations with percentage shares that must sum to 100.
  Sunsetting the profile changes nothing here — that is the living owner's
  own act, and the pen stays theirs. It is verified owner death that moves
  it: ``/succeed`` revokes the old owner token and mints one for the person
  the owner chose. That *is* "leave it to set parameters or in good hands,"
  enforced by the token lifecycle rather than a status check.
- **No campaign before a designation.** A campaign that collected money with
  nowhere to send it would be the platform holding a departed person's
  donations, which is exactly whose money it must never be.

Every donation splits across the designees by share at the moment it is
given, each share landing on the ledger — a designee with a platform account
sees it on their own creator statement; one without accrues under the
designation itself until somebody claims it. Rated profiles are refused:
tipping a performer already exists as an age-gated gift, and a crowdfunding
surface must never become a second, unwalled door to the same money.
"""

from __future__ import annotations

from . import db, ledger

DONATION_MAX = 500.0     # same stance as commerce.GIFT_MAX: one tap, capped

# The donate route is deliberately tokenless (generosity is not gated behind
# signup), which makes it the platform's one anonymous write. A daily
# per-campaign count keeps that door from becoming a ledger-spam hose while
# staying far above any real campaign's daily traffic.
DONATIONS_PER_DAY = 1000


class CampaignError(ValueError):
    """Refusal with a reason a person can read."""


def designate(profile_id: str, designees: list) -> list[dict]:
    """Replace the profile's proceeds designation. Shares must be positive
    and sum to exactly 100 — money that routes to 97% of its recipients is
    a bug wearing a rounding error."""
    if not designees:
        raise CampaignError("name at least one loved one or organization")
    total = sum(d.share for d in designees)
    if total != 100:
        raise CampaignError(
            f"shares must sum to exactly 100, got {total}")
    if any(d.share <= 0 for d in designees):
        raise CampaignError("every share must be above zero")
    conn = db.connect()
    conn.execute("DELETE FROM proceeds_designations WHERE profile_id=?",
                 (profile_id,))
    for d in designees:
        conn.execute(
            "INSERT INTO proceeds_designations (id, profile_id, name, kind,"
            " account_id, share, created_at) VALUES (?,?,?,?,?,?,?)",
            (db.new_id("des"), profile_id, d.name, d.kind, d.account_id,
             d.share, db.utcnow()))
    conn.commit()
    return designation(profile_id)


def designation(profile_id: str) -> list[dict]:
    rows = db.connect().execute(
        "SELECT * FROM proceeds_designations WHERE profile_id=?"
        " ORDER BY share DESC, name", (profile_id,)).fetchall()
    return [{"id": r["id"], "name": r["name"], "kind": r["kind"],
             "share": r["share"],
             "has_account": bool(r["account_id"])} for r in rows]


def create(profile: dict, title: str, goal: float,
           cause: str | None) -> dict:
    if profile["adult_mode"]:
        raise CampaignError(
            "no campaigns on a rated profile — tips to a performer go "
            "through the age-gated gift, never an open donation page")
    if goal <= 0:
        raise CampaignError("a campaign needs a goal above zero")
    if not designation(profile["id"]):
        raise CampaignError(
            "say where the money goes first — designate loved ones or "
            "organizations (PUT /profiles/{id}/proceeds) before asking "
            "anyone for it")
    conn = db.connect()
    campaign_id = db.new_id("cmp")
    conn.execute(
        "INSERT INTO campaigns (id, profile_id, title, cause, goal, status,"
        " created_at) VALUES (?,?,?,?,?,'open',?)",
        (campaign_id, profile["id"], title, cause, goal, db.utcnow()))
    conn.commit()
    return view(campaign_id)


def view(campaign_id: str) -> dict | None:
    """The public card: progress, and — always — where the money goes.
    A donor gives to the names on this card, not to the platform."""
    conn = db.connect()
    row = conn.execute("SELECT * FROM campaigns WHERE id=?",
                       (campaign_id,)).fetchone()
    if row is None:
        return None
    raised, donors = conn.execute(
        "SELECT COALESCE(SUM(amount),0), COUNT(*) FROM campaign_donations"
        " WHERE campaign_id=?", (campaign_id,)).fetchone()
    return {
        "id": row["id"], "profile_id": row["profile_id"],
        "title": row["title"], "cause": row["cause"], "goal": row["goal"],
        "status": row["status"], "raised": round(raised, 2),
        "donors": donors, "created_at": row["created_at"],
        "proceeds_to": designation(row["profile_id"]),
        "payment": "simulated — no real funds move; the accounting is real",
    }


def list_for(profile_id: str) -> list[dict]:
    rows = db.connect().execute(
        "SELECT id FROM campaigns WHERE profile_id=?"
        " ORDER BY created_at, rowid", (profile_id,)).fetchall()
    return [view(r["id"]) for r in rows]


def _split(amount: float, designees: list[dict]) -> list[tuple[dict, float]]:
    """Shares of one donation, in cents so they re-add to the exact amount;
    the remainder cent lands on the largest share."""
    cents = round(amount * 100)
    out, allocated = [], 0
    for d in designees[1:]:
        cut = (cents * d["share"]) // 100
        allocated += cut
        out.append((d, cut / 100))
    out.insert(0, (designees[0], (cents - allocated) / 100))
    return out


def donate(campaign_id: str, giver_id: str | None, amount: float,
           note: str | None = None, on_behalf_of: str | None = None,
           currency: str = "USD") -> dict:
    campaign = view(campaign_id)
    if campaign is None:
        raise CampaignError("no such campaign")
    if campaign["status"] != "open":
        raise CampaignError("this campaign is closed")
    if amount <= 0:
        raise CampaignError("a donation needs an amount above zero")
    if amount > DONATION_MAX:
        raise CampaignError(
            f"a single donation is capped at {DONATION_MAX:.2f} — give "
            "less, or give more than once, so one tap cannot empty an "
            "account")

    conn = db.connect()
    today = db.utcnow()[:10]
    given_today = conn.execute(
        "SELECT COUNT(*) FROM campaign_donations WHERE campaign_id=?"
        " AND created_at >= ?", (campaign_id, today)).fetchone()[0]
    if given_today >= DONATIONS_PER_DAY:
        raise CampaignError(
            "this campaign has reached today's donation count — the "
            "tokenless door is rate-limited so it can never become a "
            "ledger-spam hose; give again tomorrow")
    rows = [dict(r) for r in conn.execute(
        "SELECT * FROM proceeds_designations WHERE profile_id=?"
        " ORDER BY share DESC, name", (campaign["profile_id"],)).fetchall()]
    donation_id = db.new_id("don")
    conn.execute(
        "INSERT INTO campaign_donations (id, campaign_id, giver_id,"
        " on_behalf_of, amount, currency, note, created_at)"
        " VALUES (?,?,?,?,?,?,?,?)",
        (donation_id, campaign_id, giver_id, on_behalf_of, amount, currency,
         note, db.utcnow()))
    splits = []
    for designee, cut in _split(amount, rows):
        # A designee with a platform account is paid on their own statement;
        # one without accrues under the designation until claimed.
        beneficiary = designee["account_id"] or designee["id"]
        entry = ledger.credit(
            beneficiary=beneficiary, kind="campaign", ref=donation_id,
            amount=cut, currency=currency,
            memo=f"campaign {campaign['title']!r} — for {designee['name']}")
        conn.execute(
            "INSERT INTO campaign_splits (donation_id, designation_id,"
            " amount, ledger_ref) VALUES (?,?,?,?)",
            (donation_id, designee["id"], cut, entry or None))
        splits.append({"name": designee["name"], "kind": designee["kind"],
                       "amount": cut})
    conn.commit()
    return {
        "id": donation_id, "campaign_id": campaign_id, "amount": amount,
        "currency": currency, "on_behalf_of": on_behalf_of,
        "split": splits,
        "payment": "simulated — no real funds moved; every share is on "
                   "the ledger",
        "refundable": False,
        "note_to_giver": "A donation is not a purchase — nothing is "
                         "delivered in return, and it cannot be reversed "
                         "here.",
    }


def close(campaign_id: str) -> dict:
    conn = db.connect()
    changed = conn.execute(
        "UPDATE campaigns SET status='closed', closed_at=? WHERE id=?"
        " AND status='open'", (db.utcnow(), campaign_id)).rowcount
    conn.commit()
    if not changed:
        raise CampaignError("campaign not found or already closed")
    return view(campaign_id)
