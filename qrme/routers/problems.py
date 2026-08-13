"""The error reports come home.

Every client keeps a content-free log of failed requests — an operation and a
status code, never a message, because the messages quote what people typed.
Until now the only place those reports could go was the Cloud Model Gateway,
a separate deployment most installs never configure; a field report read the
console's honest admission ("this build has no collector configured, so
nothing is sent anywhere") and asked the obvious question: why doesn't it
funnel back to where the corrections get made?

So the product's own backend accepts the same report at the same path. A
deployment with no gateway collects its own failures, and the person running
it reads them here. Two decisions carried over from the gateway, because they
are about the data rather than the deployment:

* **The intake is a whitelist**, shared verbatim (:mod:`cloudgw.problems`
  does the screening). A report with anything extra in it is refused with a
  422 naming the field, never quietly trimmed — a client whose redaction has
  stopped working needs to hear about it.

* **Reading is narrower than writing.** Anyone may post (a wrong write costs
  a wrong counter), but the aggregate is a live map of what fails on every
  version, so reading needs ``QRME_PROBLEMS_KEY`` — or a caller on the same
  machine, which is the self-hosted case where the operator and the user are
  one person. Behind a reverse proxy every caller looks local, so a published
  deployment must set the key; the refusal says so.
"""

from __future__ import annotations

import os
import secrets

from fastapi import APIRouter, HTTPException, Request

from cloudgw import problems as intake
from .. import db

router = APIRouter()

# TestClient calls arrive as "testclient"; a developer's own machine as
# loopback. Both are the operator, not the public.
_LOCAL = {"127.0.0.1", "::1", "localhost", "testclient"}


def _require_reader(request: Request) -> None:
    key = os.environ.get("QRME_PROBLEMS_KEY", "")
    if key:
        presented = (request.headers.get("authorization") or "")
        if not presented.startswith("Bearer "):
            raise HTTPException(401, "reading the failure map requires the "
                                     "QRME_PROBLEMS_KEY bearer token")
        if not secrets.compare_digest(presented[len("Bearer "):], key):
            raise HTTPException(403, "wrong problems key")
        return
    host = request.client.host if request.client else ""
    if host not in _LOCAL:
        raise HTTPException(
            403, "the failure aggregate is readable from this machine only "
                 "until QRME_PROBLEMS_KEY is set — behind a proxy, set it")


@router.post("/v1/problems", status_code=202)
async def report_problems(request: Request) -> dict:
    """What broke, from any of this deployment's own clients.

    Accepted or refused whole, like the gateway: a partial accept would leave
    the sender believing its redaction is fine while the half that proved
    otherwise was silently binned.
    """
    try:
        payload = intake.screen(await request.json())
    except intake.Rejected as exc:
        raise HTTPException(422, str(exc)) from exc
    conn = db.connect()
    folded = 0
    for p in payload["problems"]:
        conn.execute(
            "INSERT INTO problem_reports (source, app_version, platform, op,"
            " status, day, count, last_seen) VALUES (?,?,?,?,?,?,?,?)"
            " ON CONFLICT(source, app_version, platform, op, status)"
            " DO UPDATE SET count = count + excluded.count,"
            " day = excluded.day, last_seen = excluded.last_seen",
            (payload["source"], payload["app_version"], payload["platform"],
             p["op"], p["status"], p["day"], p["count"], db.utcnow()))
        folded += p["count"]
    conn.commit()
    return {"accepted": True, "problems": len(payload["problems"]),
            "failures": folded}


@router.get("/v1/problems")
def list_problems(request: Request) -> dict:
    """The aggregate, worst first — for whoever is fixing the bugs."""
    _require_reader(request)
    rows = db.connect().execute(
        "SELECT * FROM problem_reports"
        " ORDER BY count DESC, last_seen DESC").fetchall()
    return {"rows": [dict(r) for r in rows]}
