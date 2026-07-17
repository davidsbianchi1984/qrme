"""Engagement-based learning (PRD 6.3).

Tracks per-(profile, interactor) interest signals — message length, return
visits, explicit feedback — into a single 0..1 score using an exponential
moving average. The score is deliberately simple and auditable (an explicit
PRD open question) and only ever feeds *style* adaptation in the persona
prompt, never identity or boundaries.
"""

from __future__ import annotations

from datetime import datetime, timezone

from . import db

_ALPHA = 0.3            # EMA weight for new signals
_SESSION_GAP_S = 1800   # a return after 30 min counts as a new session


def _signal_from_message(message: str) -> float:
    """Longer, substantive messages signal higher interest."""
    words = len(message.split())
    return max(0.1, min(1.0, words / 40))


def record_message(profile_id: str, interactor_id: str, message: str) -> dict:
    conn = db.connect()
    row = conn.execute(
        "SELECT * FROM engagement WHERE profile_id=? AND interactor_id=?",
        (profile_id, interactor_id),
    ).fetchone()

    now = datetime.now(timezone.utc)
    signal = _signal_from_message(message)

    if row is None:
        conn.execute(
            "INSERT INTO engagement (profile_id, interactor_id, score, interactions,"
            " sessions, last_seen) VALUES (?,?,?,1,1,?)",
            (profile_id, interactor_id, signal, now.isoformat()),
        )
    else:
        new_session = (
            row["last_seen"] is None
            or (now - datetime.fromisoformat(row["last_seen"])).total_seconds()
            > _SESSION_GAP_S
        )
        if new_session:
            signal = min(1.0, signal + 0.15)  # returning is itself a signal
        score = (1 - _ALPHA) * row["score"] + _ALPHA * signal
        conn.execute(
            "UPDATE engagement SET score=?, interactions=interactions+1,"
            " sessions=sessions+?, last_seen=? WHERE profile_id=? AND interactor_id=?",
            (score, 1 if new_session else 0, now.isoformat(), profile_id, interactor_id),
        )
    conn.commit()
    return get(profile_id, interactor_id)


def record_feedback(profile_id: str, interactor_id: str, rating: str) -> dict:
    conn = db.connect()
    conn.execute(
        "INSERT OR IGNORE INTO engagement (profile_id, interactor_id) VALUES (?,?)",
        (profile_id, interactor_id),
    )
    signal = 1.0 if rating == "up" else 0.0
    column = "feedback_pos" if rating == "up" else "feedback_neg"
    conn.execute(
        f"UPDATE engagement SET score=(1-?)*score + ?*?, {column}={column}+1"
        " WHERE profile_id=? AND interactor_id=?",
        (_ALPHA, _ALPHA, signal, profile_id, interactor_id),
    )
    conn.commit()
    return get(profile_id, interactor_id)


def get(profile_id: str, interactor_id: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM engagement WHERE profile_id=? AND interactor_id=?",
        (profile_id, interactor_id),
    ).fetchone()
    return dict(row) if row else None
