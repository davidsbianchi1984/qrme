"""Help us improve: product feedback anyone using the app can send.

A user submits an idea, improvement, bug report, or praise (optionally with
a 1–5 satisfaction rating). Feedback is private — a submitter sees only
their own; everyone can see the aggregate tally (how many ideas, bugs, …)
so the "you're heard" loop is visible without exposing anyone's words.

Open to anyone: an authenticated caller's role/subject is recorded so they
can find their submissions again; otherwise it's anonymous.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from .. import auth, db
from ..models import FeedbackSubmit

router = APIRouter()

CATEGORIES = ("idea", "improvement", "bug", "praise", "other")


def _submitter(request: Request) -> str:
    who = auth.principal(request)
    return f"{who['role']}:{who['subject_id']}" if who else "anonymous"


@router.post("/feedback", status_code=201)
def submit_feedback(body: FeedbackSubmit, request: Request) -> dict:
    """Send feedback on how to improve the app."""
    if body.category not in CATEGORIES:
        raise HTTPException(
            422, f"category must be one of {', '.join(CATEGORIES)}")
    message = body.message.strip()
    if not message:
        raise HTTPException(422, "a message is required")
    if body.rating is not None and not (1 <= body.rating <= 5):
        raise HTTPException(422, "rating must be 1–5")
    conn = db.connect()
    fid = db.new_id("fbk")
    conn.execute(
        "INSERT INTO feedback (id, submitter, category, message, rating,"
        " status, created_at) VALUES (?,?,?,?,?,'received',?)",
        (fid, _submitter(request), body.category, message, body.rating,
         db.utcnow()))
    conn.commit()
    return {"id": fid, "category": body.category, "status": "received",
            "note": "thank you — this goes straight to the team"}


@router.get("/feedback")
def my_feedback(request: Request) -> dict:
    """The caller's own submissions (newest first) plus the public tally by
    category — never anyone else's words."""
    conn = db.connect()
    submitter = _submitter(request)
    mine = []
    if submitter != "anonymous":
        mine = [dict(r) for r in conn.execute(
            "SELECT id, category, message, rating, status, created_at"
            " FROM feedback WHERE submitter=?"
            " ORDER BY created_at DESC, rowid DESC", (submitter,)).fetchall()]
    tally = {c: 0 for c in CATEGORIES}
    for row in conn.execute(
            "SELECT category, COUNT(*) AS n FROM feedback GROUP BY category"
            ).fetchall():
        if row["category"] in tally:
            tally[row["category"]] = row["n"]
    return {"mine": mine, "tally": tally,
            "total": sum(tally.values()),
            "categories": list(CATEGORIES)}
