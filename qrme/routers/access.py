"""The accessibility door: ability is not a gate, and this is where you say so.

The accessibility statement (README, console, terms) makes a commitment:
anything that stands between a person and this product because of how their
body or mind works is a defect, and reporting it turns it into tracked work.
A commitment with no door is a sentence, so this router is the door.

## Three questions, and none of them is a diagnosis

A report asks what you were trying to do, what stood in the way, and — if
you want to say — what would have helped. It never asks what your disability
is. The list in the statement (blind, deaf, mute, motor, cognitive, and the
rest) exists so people know they are expected here, not so they can be
sorted: the work item is the wall, not the person, and two people with
nothing medically in common can hit the same wall.

## Deliberately account-free, deliberately unlinked

`POST /access/reports` needs no token, and the table has no submitter
column — not "optional", absent. A person telling a product it shut them
out should not have to first succeed at the signup it may have shut them
out of, and a report about ability must not become a record about a body.
The report is the person's own words plus the language they wrote in,
nothing else.

For the same reason these reports are **never** relayed to the shared
problems collector. That pipeline is content-free by design; this one is
nothing but content, so it stays on the deployment that received it. When
a PDI vault is configured the report is sealed there too, best-effort —
custody, not transmission.

## Who reads them

`GET /access/reports` is held by the reviewer token, the same role that
adjudicates objections: somebody standing for the deployment rather than
for any profile. Accepted reports become rows in `tests/a11y_backlog.txt`,
which only shrinks — that is the "tracked work" the statement promises.
"""

from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException, Request

from .. import auth, db, i18n
from ..models import AccessReportSubmit

router = APIRouter()

NEEDS_ITS_WORDS = "say what you were trying to do and what stood in the way"


@router.post("/access/reports", status_code=201)
def submit_access_report(body: AccessReportSubmit, request: Request) -> dict:
    """File an accessibility report — no account, no diagnosis, your words."""
    doing = body.doing.strip()
    wall = body.wall.strip()
    if not doing or not wall:
        raise HTTPException(422, NEEDS_ITS_WORDS)
    lang = body.lang if body.lang in i18n.SUPPORTED else "en"

    rid = db.new_id("acc")
    at = db.utcnow()

    pdi_key = None
    pdi = request.app.state.pdi
    if pdi is not None:
        pdi_key = f"qrme/access/reports/{rid}"
        payload = {"report_id": rid, "lang": lang, "doing": doing,
                   "wall": wall, "help": (body.help or "").strip() or None,
                   "at": at}
        try:
            pdi.put(pdi_key, json.dumps(payload))
        except Exception:
            pdi_key = None   # vault unreachable — the local row still stands

    conn = db.connect()
    conn.execute(
        "INSERT INTO access_reports (id, lang, doing, wall, help, status,"
        " pdi_key, created_at) VALUES (?,?,?,?,?,'received',?,?)",
        (rid, lang, doing, wall, (body.help or "").strip() or None,
         pdi_key, at))
    conn.commit()
    return {"id": rid, "status": "received",
            "note": "thank you — this becomes tracked work, and it stays "
                    "on this deployment"}


@router.get("/access/reports")
def read_access_reports(request: Request) -> dict:
    """Every report, newest first — for the person who runs this deployment."""
    auth.require_reviewer(request)
    conn = db.connect()
    reports = [dict(r) for r in conn.execute(
        "SELECT id, lang, doing, wall, help, status, pdi_key, created_at"
        " FROM access_reports"
        " ORDER BY created_at DESC, rowid DESC").fetchall()]
    return {"reports": reports, "total": len(reports)}
