"""The audience layer: like, comment, share, subscribe.

Everything here is what a viewer does *other* than talk. Chat and rooms
already carried conversation; this carries the quieter half — the reactions
that decide whether anyone comes back, and the subscription that says they
intend to.

Four verbs across four kinds of target, which is why targets are a
``(kind, id)`` pair rather than a column per thing. A like on a synthetic
profile, a live desk, a room message and a marketplace listing is the same
fact about the same person, and four near-identical tables would have drifted
apart within a round.

Three rules hold this together, and each exists because the obvious
implementation gets it wrong:

* **A like is a fact, not a counter.** ``reactions`` is UNIQUE on
  ``(target, actor)``, so liking twice is idempotent rather than two. A plain
  integer column would let one account manufacture popularity by calling an
  endpoint in a loop, which makes every number on the platform meaningless
  rather than just that one.

* **A comment is authored text, so it is moderated like authored text.** It
  goes through the same :mod:`~qrme.moderation` pipeline as a chat turn, at
  the target's own maturity setting, and a blocked comment is kept for its
  author and shown to nobody else — the same shape :mod:`~qrme.connections`
  already uses. A comment box that skipped moderation would be the one
  unfiltered surface on the platform, and it would be found within a day.

* **A rated target stays rated.** Liking, commenting on, sharing or
  subscribing to an 18+ desk runs the deployment's existing verified-adult
  check. This module does not implement a second one: a weaker second gate is
  the one that gets used.

Money is simulated here exactly as it is for packs and licences — a paid
subscription credits the creator's ledger and settles through the existing
payout sweep. Nothing in this repository moves real funds, and the docs say
so rather than implying a payment processor that does not exist.
"""

from __future__ import annotations

from . import db, ledger, moderation

# What can be liked, commented on or shared. Kept as a closed set so a typo
# in a path parameter cannot silently create a fifth kind of thing that no
# listing endpoint will ever read back.
TARGETS = ("profile", "desk", "message", "listing", "post")

# What can be subscribed to. A message and a listing cannot: subscribing means
# "tell me when there is more from them", and neither produces more.
SUBJECTS = ("profile", "desk")

TIERS = ("follow", "paid")

# A paid tier settles per period. The period is nominal — this simulates
# billing rather than performing it — but the ledger entries it produces are
# real rows on the same statement as pack sales and licence fees.
PERIOD_DAYS = 30


class AudienceError(ValueError):
    """A refusal with a reason worth showing the caller."""


def _check_target(kind: str) -> None:
    if kind not in TARGETS:
        raise AudienceError(
            f"unknown target kind {kind!r}; expected one of "
            f"{', '.join(TARGETS)}")


def _check_subject(kind: str) -> None:
    if kind not in SUBJECTS:
        raise AudienceError(
            f"cannot subscribe to {kind!r} — subscribing means 'tell me when "
            f"there is more from them', so it applies to "
            f"{' and '.join(SUBJECTS)}")


def target_exists(kind: str, target_id: str) -> bool:
    """Whether the thing being reacted to is real.

    Checked rather than assumed: a like on a profile id that does not exist
    would sit in the table forever, counted by nothing and cleaned by nothing,
    and the first person to notice would be whoever tried to explain a total.
    """
    table = {"profile": "profiles", "desk": "desks",
             "message": "room_messages", "listing": "listings",
             "post": "posts"}[kind]
    return db.connect().execute(
        f"SELECT 1 FROM {table} WHERE id=?", (target_id,)).fetchone() is not None


def is_rated(kind: str, target_id: str) -> bool:
    """Whether this target sits behind the verified-adult gate.

    The caller does the age check — this only reports whether one is needed,
    so that the single existing implementation of "is this viewer an adult"
    stays the only one.
    """
    if kind == "desk":
        row = db.connect().execute(
            "SELECT rated FROM desks WHERE id=?", (target_id,)).fetchone()
        return bool(row and row["rated"])
    if kind == "profile":
        row = db.connect().execute(
            "SELECT adult_mode FROM profiles WHERE id=?",
            (target_id,)).fetchone()
        return bool(row and row["adult_mode"])
    if kind == "post":
        # A post inherits the gate from whoever wrote it. Deciding it per post
        # would mean an adult profile could publish past its own wall by
        # writing something innocuous.
        row = db.connect().execute(
            "SELECT p.adult_mode FROM posts o JOIN profiles p"
            " ON p.id = o.profile_id WHERE o.id=?", (target_id,)).fetchone()
        return bool(row and row["adult_mode"])
    return False


# --- like -----------------------------------------------------------------

def like(kind: str, target_id: str, actor_id: str) -> dict:
    """Like something. Idempotent: liking twice is still one like."""
    _check_target(kind)
    if not target_exists(kind, target_id):
        raise AudienceError(f"no such {kind}")
    conn = db.connect()
    existing = conn.execute(
        "SELECT id FROM reactions WHERE target_kind=? AND target_id=? AND"
        " actor_id=?", (kind, target_id, actor_id)).fetchone()
    if existing is None:
        conn.execute(
            "INSERT INTO reactions (id, target_kind, target_id, actor_id,"
            " created_at) VALUES (?,?,?,?,?)",
            (db.new_id("rct"), kind, target_id, actor_id, db.utcnow()))
        conn.commit()
    return {"target_kind": kind, "target_id": target_id, "liked": True,
            "likes": likes(kind, target_id),
            # Reported so a client can render the button's state without a
            # second request, and so "already liked" is never an error.
            "was_already_liked": existing is not None}


def unlike(kind: str, target_id: str, actor_id: str) -> dict:
    _check_target(kind)
    conn = db.connect()
    conn.execute(
        "DELETE FROM reactions WHERE target_kind=? AND target_id=? AND"
        " actor_id=?", (kind, target_id, actor_id))
    conn.commit()
    return {"target_kind": kind, "target_id": target_id, "liked": False,
            "likes": likes(kind, target_id)}


def likes(kind: str, target_id: str) -> int:
    return db.connect().execute(
        "SELECT COUNT(*) FROM reactions WHERE target_kind=? AND target_id=?",
        (kind, target_id)).fetchone()[0]


def liked_by(kind: str, target_id: str, actor_id: str) -> bool:
    return db.connect().execute(
        "SELECT 1 FROM reactions WHERE target_kind=? AND target_id=? AND"
        " actor_id=?", (kind, target_id, actor_id)).fetchone() is not None


# --- comment --------------------------------------------------------------

def _maturity_for(kind: str, target_id: str) -> str:
    """The filter a comment on this target is held to.

    A comment lands under someone else's name, so it is filtered at *their*
    setting rather than the commenter's — the profile owner is who a visitor
    will hold responsible for what appears there.
    """
    if kind == "profile":
        row = db.connect().execute(
            "SELECT maturity FROM profiles WHERE id=?", (target_id,)).fetchone()
        return row["maturity"] if row and row["maturity"] else "balanced"
    return "balanced"


def comment(kind: str, target_id: str, author_id: str, body: str,
            author: dict | None = None) -> dict:
    """Leave a comment. Moderated on the way in.

    A blocked comment is stored and returned to its author with the reason,
    and is invisible to everyone else — the same shape connections already
    uses for a blocked message. Dropping it silently teaches the author
    nothing; showing it teaches everyone else the filter does not work.
    """
    _check_target(kind)
    if not body.strip():
        raise AudienceError("a comment needs something in it")
    if not target_exists(kind, target_id):
        raise AudienceError(f"no such {kind}")

    verdict = moderation.review(
        body, None, author or {"birthdate": None},
        maturity=_maturity_for(kind, target_id))
    row_id = db.new_id("cmt")
    conn = db.connect()
    conn.execute(
        "INSERT INTO comments (id, target_kind, target_id, author_id, body,"
        " status, flag_reason, created_at) VALUES (?,?,?,?,?,?,?,?)",
        (row_id, kind, target_id, author_id, body.strip(),
         "approved" if verdict.approved else "blocked",
         None if verdict.approved else verdict.reason, db.utcnow()))
    conn.commit()
    return {
        "id": row_id, "target_kind": kind, "target_id": target_id,
        "author_id": author_id, "body": body.strip(),
        "status": "approved" if verdict.approved else "blocked",
        "flag_reason": None if verdict.approved else verdict.reason,
        "visible": verdict.approved,
    }


def comments(kind: str, target_id: str, viewer_id: str | None = None) -> list:
    """Approved comments, plus the viewer's own blocked ones.

    The second half is the point: an author who cannot see that their comment
    was held has no way to tell moderation from a bug, and will simply post it
    again.
    """
    rows = db.connect().execute(
        "SELECT * FROM comments WHERE target_kind=? AND target_id=?"
        " ORDER BY created_at, rowid", (kind, target_id)).fetchall()
    out = []
    for r in rows:
        if r["status"] == "approved" or (viewer_id and
                                         r["author_id"] == viewer_id):
            out.append({
                "id": r["id"], "author_id": r["author_id"], "body": r["body"],
                "status": r["status"], "flag_reason": r["flag_reason"],
                "created_at": r["created_at"],
                "likes": likes("message", r["id"]),
            })
    return out


def delete_comment(comment_id: str, actor_id: str) -> dict:
    """An author can withdraw their own comment. Nobody else's."""
    conn = db.connect()
    row = conn.execute("SELECT * FROM comments WHERE id=?",
                       (comment_id,)).fetchone()
    if row is None:
        raise AudienceError("no such comment")
    if row["author_id"] != actor_id:
        raise AudienceError("not your comment")
    conn.execute("DELETE FROM comments WHERE id=?", (comment_id,))
    conn.commit()
    return {"id": comment_id, "deleted": True}


# --- share ----------------------------------------------------------------

def share(kind: str, target_id: str, actor_id: str | None = None,
          channel: str = "link") -> dict:
    """Record a share and hand back the link to share.

    Anonymous shares are allowed — someone who scanned a sticker has no
    account and is exactly the person most likely to pass it on — but the
    actor is recorded when there is one, because "shared 40 times" and
    "shared 40 times by one account" are different facts.

    The link is the public one for the target, which means a rated target's
    shared link lands the recipient on the age wall rather than on anything.
    Sharing is therefore safe to allow without an adult check on the *sharer*:
    the gate is on the destination, where it cannot be routed around.
    """
    _check_target(kind)
    if not target_exists(kind, target_id):
        raise AudienceError(f"no such {kind}")
    conn = db.connect()
    conn.execute(
        "INSERT INTO shares (id, target_kind, target_id, actor_id, channel,"
        " created_at) VALUES (?,?,?,?,?,?)",
        (db.new_id("shr"), kind, target_id, actor_id, channel, db.utcnow()))
    conn.commit()
    return {"target_kind": kind, "target_id": target_id,
            "channel": channel, "url": share_url(kind, target_id),
            "shares": share_count(kind, target_id)}


def share_url(kind: str, target_id: str) -> str:
    """Where a share points. Relative — the caller makes it absolute against
    whatever origin it is serving from."""
    # Every kind in TARGETS needs an entry. A missing one is a KeyError at the
    # moment somebody shares, which is the worst place to find out — so the
    # lookup is checked against TARGETS by a test rather than by hoping.
    return {
        "profile": f"/summon?ref={target_id}",
        "desk": f"/desks/{target_id}",
        "listing": f"/marketplace/listings?id={target_id}",
        "message": f"/rooms/messages/{target_id}",
        "post": f"/posts/{target_id}",
    }[kind]


def share_count(kind: str, target_id: str) -> int:
    return db.connect().execute(
        "SELECT COUNT(*) FROM shares WHERE target_kind=? AND target_id=?",
        (kind, target_id)).fetchone()[0]


# --- subscribe ------------------------------------------------------------

def subscribe(kind: str, subject_id: str, subscriber: str,
              tier: str = "follow", price: float = 0.0,
              beneficiary: str | None = None,
              accept_price: float | None = None) -> dict:
    """Follow (free) or subscribe (paid).

    A paid tier requires ``accept_price`` to match the price being charged.
    That is the same explicit-consent step priced packs already use, and it is
    here for the same reason: a subscription is recurring, so a viewer who did
    not mean to start one keeps paying for it, which is strictly worse than a
    single purchase they did not mean to make.

    The first period is charged on subscribe. Later periods are charged by
    :func:`renew`, so nothing is billed by the mere passage of time in a
    system nobody is watching.
    """
    _check_subject(kind)
    if tier not in TIERS:
        raise AudienceError(
            f"unknown tier {tier!r}; expected one of {', '.join(TIERS)}")
    if not target_exists(kind, subject_id):
        raise AudienceError(f"no such {kind}")

    if tier == "paid":
        if price <= 0:
            raise AudienceError(
                "a paid subscription needs a price above zero — a free one is "
                "the 'follow' tier")
        if accept_price is None or round(accept_price, 2) != round(price, 2):
            raise AudienceError(
                f"this subscription costs {price:.2f} per period and renews "
                f"until cancelled; send accept_price={price:.2f} to confirm")
        if not beneficiary:
            raise AudienceError(
                "a paid subscription has to credit someone: no beneficiary "
                "means the money would accrue to nobody")
    else:
        price = 0.0

    conn = db.connect()
    existing = conn.execute(
        "SELECT * FROM subscriptions WHERE subject_kind=? AND subject_id=?"
        " AND subscriber=?", (kind, subject_id, subscriber)).fetchone()
    now = db.utcnow()

    if existing is not None:
        # Re-subscribing reactivates the same row rather than making a second
        # one, so a lapsed-then-returned subscriber keeps one history.
        conn.execute(
            "UPDATE subscriptions SET tier=?, price=?, status='active',"
            " cancelled_at=NULL, renewed_at=? WHERE id=?",
            (tier, price, now, existing["id"]))
        sub_id = existing["id"]
        periods = existing["periods"]
    else:
        sub_id = db.new_id("sub")
        conn.execute(
            "INSERT INTO subscriptions (id, subject_kind, subject_id,"
            " subscriber, tier, price, status, started_at, renewed_at,"
            " periods) VALUES (?,?,?,?,?,?, 'active', ?,?,0)",
            (sub_id, kind, subject_id, subscriber, tier, price, now, now))
        periods = 0
    conn.commit()

    charged = None
    if tier == "paid":
        charged = _charge(sub_id, kind, subject_id, beneficiary, price,
                          periods + 1)
    return subscription(sub_id) | ({"charged": charged} if charged else {})


def _charge(sub_id: str, kind: str, subject_id: str, beneficiary: str,
            price: float, period_no: int) -> dict:
    """Credit one period to the creator's ledger.

    Simulated, like every other money movement here — but the entry is a real
    row on the same statement as pack sales and licence fees, and it settles
    through the same payout sweep.
    """
    entry_id = ledger.credit(
        beneficiary=beneficiary, kind="subscription", ref=sub_id,
        amount=price,
        memo=f"subscription period {period_no} — {kind} {subject_id}")
    conn = db.connect()
    conn.execute(
        "UPDATE subscriptions SET periods=?, renewed_at=? WHERE id=?",
        (period_no, db.utcnow(), sub_id))
    conn.commit()
    # credit() returns "" for a zero amount, which a paid tier cannot be —
    # but reporting the empty string as an id would be a small lie in a
    # money-shaped response, so it becomes None.
    return {"period": period_no, "amount": price,
            "ledger_entry": entry_id or None}


def renew(sub_id: str, beneficiary: str) -> dict:
    """Charge the next period of a paid subscription.

    Explicit rather than implicit: nothing here bills on a timer, so a
    deployment that stops running does not quietly accrue charges nobody
    authorised and nobody saw.
    """
    row = db.connect().execute(
        "SELECT * FROM subscriptions WHERE id=?", (sub_id,)).fetchone()
    if row is None:
        raise AudienceError("no such subscription")
    if row["status"] != "active":
        raise AudienceError("this subscription is cancelled — resubscribe "
                            "instead of renewing it")
    if row["tier"] != "paid":
        raise AudienceError("a free follow has nothing to renew")
    charged = _charge(sub_id, row["subject_kind"], row["subject_id"],
                      beneficiary, row["price"], row["periods"] + 1)
    return subscription(sub_id) | {"charged": charged}


def cancel(kind: str, subject_id: str, subscriber: str) -> dict:
    """Stop. Keeps the row so a lapsed subscriber stays distinguishable from
    someone who was never there — and so nothing further is charged."""
    conn = db.connect()
    row = conn.execute(
        "SELECT id FROM subscriptions WHERE subject_kind=? AND subject_id=?"
        " AND subscriber=?", (kind, subject_id, subscriber)).fetchone()
    if row is None:
        raise AudienceError("not subscribed")
    conn.execute(
        "UPDATE subscriptions SET status='cancelled', cancelled_at=?"
        " WHERE id=?", (db.utcnow(), row["id"]))
    conn.commit()
    return subscription(row["id"])


def subscription(sub_id: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM subscriptions WHERE id=?", (sub_id,)).fetchone()
    if row is None:
        return None
    return {
        "id": row["id"], "subject_kind": row["subject_kind"],
        "subject_id": row["subject_id"], "subscriber": row["subscriber"],
        "tier": row["tier"], "price": row["price"],
        "currency": row["currency"], "status": row["status"],
        "started_at": row["started_at"], "renewed_at": row["renewed_at"],
        "periods": row["periods"], "cancelled_at": row["cancelled_at"],
        # Stated on every subscription rather than in a policy page: this
        # deployment simulates billing. Implying a payment processor that does
        # not exist is the kind of claim that gets believed.
        "billing": "simulated — periods are charged explicitly, never on a "
                   "timer, and settle through the creator payout sweep",
    }


def subscribers(kind: str, subject_id: str, active_only: bool = True) -> list:
    sql = ("SELECT * FROM subscriptions WHERE subject_kind=? AND subject_id=?")
    if active_only:
        sql += " AND status='active'"
    rows = db.connect().execute(sql + " ORDER BY started_at, rowid",
                                (kind, subject_id)).fetchall()
    return [subscription(r["id"]) for r in rows]


def subscriptions_of(subscriber: str, active_only: bool = True) -> list:
    sql = "SELECT id FROM subscriptions WHERE subscriber=?"
    if active_only:
        sql += " AND status='active'"
    rows = db.connect().execute(sql + " ORDER BY started_at, rowid",
                                (subscriber,)).fetchall()
    return [subscription(r["id"]) for r in rows]


def counts(kind: str, target_id: str, viewer_id: str | None = None) -> dict:
    """The numbers a client renders next to the buttons, in one call."""
    out = {
        "likes": likes(kind, target_id),
        "comments": len([c for c in comments(kind, target_id)
                         if c["status"] == "approved"]),
        "shares": share_count(kind, target_id),
    }
    if kind in SUBJECTS:
        out["subscribers"] = len(subscribers(kind, target_id))
    if viewer_id:
        out["you_liked"] = liked_by(kind, target_id, viewer_id)
        if kind in SUBJECTS:
            sub = db.connect().execute(
                "SELECT status, tier FROM subscriptions WHERE subject_kind=?"
                " AND subject_id=? AND subscriber=?",
                (kind, target_id, viewer_id)).fetchone()
            out["your_subscription"] = (
                sub["tier"] if sub and sub["status"] == "active" else None)
    return out
