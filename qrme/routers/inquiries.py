"""Asking the people, not the pages — endpoints.

Two audiences meet on the same rows and must never see the same thing.

The **owner** opens a question, reads what came back, and decides whether any
of it is worth keeping. Those routes take ``require_owner`` and return the
whole row, the owner's own words included.

The **person answering** has no account, will never have one, and is not asked
for a name. Their routes hang off ``/open-questions`` — a separate prefix,
because a route that serves both audiences from one handler is a route where
one missing branch shows a stranger somebody's private words. They see exactly
:data:`qrme.inquiries.PUBLIC_FIELDS` and nothing beside it.

See ``qrme/inquiries.py`` for what is sanitized and why it cannot be turned
off.
"""

from __future__ import annotations

import json

from fastapi import APIRouter, Header, HTTPException, Request

from .. import db, i18n, inquiries, moderation
from ..common import profile_or_404, require_owner
from ..models import InquiryAnswer, InquiryOpen

router = APIRouter()


def _inq_or_404(iid: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM inquiries WHERE id=?", (iid,)).fetchone()
    if row is None:
        raise HTTPException(404, "no such question")
    return dict(row)


def _owner_out(row: dict) -> dict:
    """The owner's view: their own words, plus exactly what went out in their
    place. A person who cannot see both cannot judge whether the trade was
    worth making."""
    return {"id": row["id"], "profile_id": row["profile_id"],
            "topic": row["topic"], "question": row["question"],
            "brief": row["brief"],            # what is on the board
            "redactions": row["redactions"],  # how much was taken out
            "closed": bool(row["closed_at"]),
            "asked_at": row["created_at"],
            "answer_count": inquiries.count_answers(row["id"])}


def _answers(inquiry_id: str, include_blocked: bool) -> list[dict]:
    sql = ("SELECT * FROM inquiry_answers WHERE inquiry_id=?"
           + ("" if include_blocked else " AND blocked=0")
           + " ORDER BY created_at, rowid")
    return [inquiries.answer_out(dict(r))
            for r in db.connect().execute(sql, (inquiry_id,)).fetchall()]


# --------------------------------------------------------------------------
# The owner's side.
# --------------------------------------------------------------------------

@router.post("/profiles/{profile_id}/inquiries", status_code=201)
def open_inquiry(profile_id: str, body: InquiryOpen, request: Request) -> dict:
    """Put a question where people can answer it.

    What goes on the board is the sanitized brief, always — ``compose`` has no
    way to be told otherwise. The owner's own ``topic`` and ``question`` are
    stored so they can see later what they meant, and are never returned by an
    accountless route.
    """
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    if not body.question.strip():
        raise HTTPException(400, "say what you want to know, in one question")
    brief, redactions = inquiries.compose(
        profile_id, body.topic, body.question, body.private)
    iid = db.new_id("inq")
    conn = db.connect()
    conn.execute(
        "INSERT INTO inquiries (id, profile_id, topic, question, brief,"
        " redactions, closed_at, created_at) VALUES (?,?,?,?,?,?,NULL,?)",
        (iid, profile_id, body.topic, body.question, brief, redactions,
         db.utcnow()))
    conn.commit()
    return _owner_out(_inq_or_404(iid))


@router.get("/profiles/{profile_id}/inquiries")
def list_inquiries(profile_id: str, request: Request) -> list[dict]:
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    rows = db.connect().execute(
        "SELECT * FROM inquiries WHERE profile_id=? ORDER BY created_at, rowid",
        (profile_id,)).fetchall()
    return [_owner_out(dict(r)) for r in rows]


@router.get("/inquiries/{iid}")
def get_inquiry(iid: str, request: Request) -> dict:
    """The owner reading their own question, blocked answers included — the
    filter stopped those on the way in, and an owner who cannot see what was
    stopped has to take the filter's word for it."""
    row = _inq_or_404(iid)
    require_owner(row["profile_id"], request)
    return {**_owner_out(row), "answers": _answers(iid, include_blocked=True)}


@router.post("/inquiries/{iid}/close")
def close_inquiry(iid: str, request: Request) -> dict:
    """Stop taking answers. What came in stays readable — closing a question
    is not deleting what people gave you."""
    row = _inq_or_404(iid)
    require_owner(row["profile_id"], request)
    if row["closed_at"]:
        raise HTTPException(409, "this question is already closed")
    conn = db.connect()
    conn.execute("UPDATE inquiries SET closed_at=? WHERE id=?",
                 (db.utcnow(), iid))
    conn.commit()
    return _owner_out(_inq_or_404(iid))


@router.post("/inquiries/{iid}/answers/{aid}/learn", status_code=201)
def learn(iid: str, aid: str, request: Request) -> dict:
    """Fold one answer into the profile as a learned ``knowledge`` source.

    This is the whole point of the round: what a stranger knew becomes
    something the offline model knows. It happens one answer at a time and
    only when the owner says so — an answer that folded itself in would make
    the board a way to write into somebody's coach.
    """
    row = _inq_or_404(iid)
    require_owner(row["profile_id"], request)
    ans = db.connect().execute(
        "SELECT * FROM inquiry_answers WHERE id=? AND inquiry_id=?",
        (aid, iid)).fetchone()
    if ans is None:
        raise HTTPException(404, "no such answer to this question")
    ans = dict(ans)
    if ans["blocked"]:
        raise HTTPException(409, "this answer was blocked by the filter and "
                                 "cannot be folded in")
    if ans["folded_src"]:
        return {"source_id": ans["folded_src"], "already_learned": True}
    pdi = request.app.state.pdi
    conn = db.connect()
    item_id = db.new_id("src")
    title = f"Answered: {row['topic']}"
    content = ans["body"] if not ans["points_to"] else (
        f"{ans['body']}\n\nPointed at: {ans['points_to']}")
    pdi_key = None
    if pdi is not None and content:
        pdi_key = f"qrme/{row['profile_id']}/sources/{item_id}"
        pdi.put(pdi_key, json.dumps({"content": content}))
        content = None
    conn.execute(
        "INSERT INTO source_items (id, profile_id, kind, title, content,"
        " pdi_key, created_at) VALUES (?,?,'knowledge',?,?,?,?)",
        (item_id, row["profile_id"], title, content, pdi_key, db.utcnow()))
    conn.execute("UPDATE inquiry_answers SET folded_src=? WHERE id=?",
                 (item_id, aid))
    conn.commit()
    return {"source_id": item_id, "already_learned": False,
            "note": "the answer folded into the profile; the local model now "
                    "uses it"}


# --------------------------------------------------------------------------
# The stranger's side. No account, and no way from here to the owner.
# --------------------------------------------------------------------------

@router.get("/open-questions")
def board(accept_language: str = Header(default="")) -> list[dict]:
    """The board: questions people have put out, oldest first.

    **In the reader's language.** Whoever is reading this has no account, so
    ``Accept-Language`` is the only preference there is — the asker's setting
    is a fact about the asker and says nothing about who is answering.
    """
    language = i18n.negotiate(accept_language)
    rows = db.connect().execute(
        "SELECT * FROM inquiries WHERE closed_at IS NULL"
        " ORDER BY created_at, rowid").fetchall()
    out = [inquiries.public(dict(r), inquiries.count_answers(r["id"]))
           for r in rows]
    return [i18n.localize_public(o, language) for o in out]


@router.get("/open-questions/{iid}")
def open_question(iid: str, accept_language: str = Header(default="")) -> dict:
    """One question and the answers already given, so somebody about to answer
    can see they are not repeating what is already there."""
    language = i18n.negotiate(accept_language)
    row = _inq_or_404(iid)
    # `replies`, not `answers`: the owner's route already puts an `answers`
    # on the wire and that one carries the blocked flag and the fold state.
    # One name, one shape — a reader who learned `answers` on the owner's
    # route must not meet a smaller thing under the same word here.
    out = {**inquiries.public(row, inquiries.count_answers(iid)),
           "replies": [{"alias": a["alias"], "body": a["body"],
                        "points_to": a["points_to"],
                        "answered_at": a["answered_at"]}
                       for a in _answers(iid, include_blocked=False)]}
    return i18n.localize_public(out, language)


@router.post("/open-questions/{iid}/answers", status_code=201)
def answer(iid: str, body: InquiryAnswer,
           accept_language: str = Header(default="")) -> dict:
    """Answer somebody's question, or point them at where to look.

    No account, no sign-in, no name required. A blocked answer is stored and
    reported as accepted-but-held rather than silently dropped: the person
    wrote something in good faith and deserves to know it did not go through.
    """
    i18n.negotiate(accept_language)
    row = _inq_or_404(iid)
    if row["closed_at"]:
        raise HTTPException(409, "this question is closed — it is not taking "
                                 "answers any more")
    text = body.body.strip()
    if not text:
        raise HTTPException(400, "an empty answer answers nothing")
    if len(text) > inquiries.MAX_ANSWER:
        raise HTTPException(400, "that answer is longer than this board takes")
    if len(body.alias) > inquiries.MAX_ALIAS:
        raise HTTPException(400, "that is a long name to be called by")
    if len(body.points_to) > inquiries.MAX_SOURCE:
        raise HTTPException(400, "that is a long direction to point in")
    # The strictest filter, deliberately: the writer has no account, so there
    # is no age to check and no relationship to consult, and a board anybody
    # can write to is the wrong place to guess generously.
    verdict = moderation.review(f"{text}\n{body.points_to}", None, {},
                                maturity="strict")
    aid = db.new_id("ans")
    conn = db.connect()
    conn.execute(
        "INSERT INTO inquiry_answers (id, inquiry_id, alias, body, points_to,"
        " blocked, folded_src, created_at) VALUES (?,?,?,?,?,?,NULL,?)",
        (aid, iid, body.alias.strip(), text, body.points_to.strip(),
         int(not verdict.approved), db.utcnow()))
    conn.commit()
    return {"id": aid, "held": not verdict.approved,
            "note": ("your answer was held by the filter and was not shown"
                     if not verdict.approved else "thank you — it is on the "
                     "question now")}
