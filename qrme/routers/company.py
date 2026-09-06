"""The Company Builder's doors: found, draft, interview, hire, oversee.

Auth is the organizations pattern verbatim: a company belongs to an
*account*, tokens are per-profile, so every route authenticates the
caller as the owner of some profile and then checks that profile's
account against the company's — the handle is never the guessable
owner_id string.

The marketplace door (publish) is deliberately absent this release: a
company opens for business through the shops the founder already has,
and a dedicated storefront composition lands with the marketplace round.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from .. import auth, company as companies, db, occupations

router = APIRouter()


def _caller_owner_id(request: Request) -> str:
    """The account behind the presented owner token — the organizations
    pattern verbatim, because a company's folder boundary IS an account
    boundary and nothing looser."""
    who = auth.principal(request)
    if who is None:
        raise HTTPException(401, "authentication required")
    if who["role"] != "owner":
        raise HTTPException(403, "an owner token is required")
    row = db.connect().execute("SELECT owner_id FROM profiles WHERE id=?",
                               (who["subject_id"],)).fetchone()
    if row is None:
        raise HTTPException(403, "token does not resolve to a profile")
    return row["owner_id"]


def _company_or_404(company_id: str, request: Request) -> dict:
    row = companies.get(company_id)
    if row is None or row["owner_id"] != _caller_owner_id(request):
        # One answer for absent and not-yours: knowing the id is not
        # being here.
        raise HTTPException(404, "no such company")
    return row


def _fail(exc: companies.CompanyError):
    raise HTTPException(422, str(exc))


class CompanyFound(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    industry: str = Field(
        min_length=1, max_length=80,
        description="Any industry, in the founder's words — no list.")
    headcount: int = Field(ge=companies.MIN_HEADCOUNT,
                           le=companies.MAX_HEADCOUNT,
                           description="How many seats this company is "
                                       "founded for.")


class SeatAdd(BaseModel):
    title: str = Field(min_length=1, max_length=80,
                       description="Any job on Earth, in the founder's words.")
    department: str = Field(
        min_length=1, max_length=80,
        description="The department this seat belongs to — the founder's "
                    "word, like the title.")


class InterviewAnswer(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    answer: str = Field(min_length=1, max_length=4000)


class SeatHire(BaseModel):
    answers: list[InterviewAnswer] = Field(min_length=3, max_length=40)


class StudyKeep(BaseModel):
    skills: list[str] = Field(default_factory=list, max_length=60)
    connections: list[str] = Field(default_factory=list, max_length=60)


@router.post("/companies", status_code=201)
def found_company(body: CompanyFound, request: Request) -> dict:
    try:
        return companies.found(_caller_owner_id(request), body.name,
                               body.industry, body.headcount)
    except companies.CompanyError as exc:
        _fail(exc)


@router.get("/companies")
def list_companies(request: Request) -> list[dict]:
    return companies.list_for(_caller_owner_id(request))


@router.get("/companies/{company_id}")
def company_roster(company_id: str, request: Request) -> dict:
    row = _company_or_404(company_id, request)
    return {**row, "seats": companies.seats(row["id"])}


@router.post("/companies/{company_id}/seats", status_code=201)
def add_seat(company_id: str, body: SeatAdd, request: Request) -> dict:
    row = _company_or_404(company_id, request)
    try:
        return companies.add_seat(row, body.title, body.department)
    except companies.CompanyError as exc:
        _fail(exc)


@router.post("/companies/{company_id}/seats/{seat_id}/interview",
             status_code=201)
def draft_interview(company_id: str, seat_id: str, request: Request) -> dict:
    """The platform writes the interview for this seat — the exemplar's
    caliber, the role's own vocabulary, a suggested answer per question.
    The founder edits everything; nothing is hired here."""
    row = _company_or_404(company_id, request)
    try:
        return {"questions": companies.draft_interview(
            row, seat_id, cloud=getattr(request.app.state, "cloud", None))}
    except companies.CompanyError as exc:
        _fail(exc)


@router.get("/occupations")
def browse_occupations(request: Request, q: str = "", family: str = "",
                       limit: int = 25) -> dict:
    """Browse the pool the app carries — the way into forty-five thousand
    positions without a model and without the network.

    An empty query is a browse rather than a search: it answers with the
    head of the pool, or of one family, so the list is never blank while
    somebody is deciding what to type. Typing a job the pool has never
    heard of is not an error either — the founder's own title stays
    exactly as good as a picked one.
    """
    _caller_owner_id(request)
    rows = occupations.search(q, limit=max(1, min(limit, 100)),
                              family=family or None)
    return {"positions": [
        {"title": r["title"], "family": r["family"],
         "skills": r["skills"], "connections": r["connections"]}
        for r in rows], "total": occupations.count()}


@router.get("/occupations/families")
def occupation_families(request: Request) -> dict:
    """The headings a founder can walk the pool by."""
    _caller_owner_id(request)
    return {"families": occupations.families()}


@router.post("/companies/{company_id}/seats/{seat_id}/study",
             status_code=201)
def study_seat(company_id: str, seat_id: str, request: Request) -> dict:
    """Download what this seat has to know.

    The working knowledge is fetched and stored on the seat, which is
    what makes the hire offline afterwards. The skills and connections
    are two halves: what the study found about *this* job leads, and
    what the carried pool knows about its family fills in behind — so
    the lists stay readable with nothing reachable and get specific when
    something is. `tailored` counts the first half. Nothing is hired
    here; this is the step before the founder reads what was found.
    """
    row = _company_or_404(company_id, request)
    try:
        return companies.study_seat(
            row, seat_id, cloud=getattr(request.app.state, "cloud", None))
    except companies.CompanyError as exc:
        _fail(exc)


@router.post("/companies/{company_id}/seats/{seat_id}/study/keep")
def keep_study(company_id: str, seat_id: str, body: StudyKeep,
               request: Request) -> dict:
    """The founder's edits to what the study found — a skill this
    business does not want comes off, one the pool never thought of goes
    on. Still nobody hired; the signature does that."""
    row = _company_or_404(company_id, request)
    try:
        return companies.keep_study(row, seat_id, body.skills,
                                    body.connections)
    except companies.CompanyError as exc:
        _fail(exc)


@router.post("/companies/{company_id}/seats/{seat_id}/hire", status_code=201)
def hire(company_id: str, seat_id: str, body: SeatHire,
         request: Request) -> dict:
    """The signature is the hire — see qrme/company.py for everything a
    signed interview becomes."""
    row = _company_or_404(company_id, request)
    try:
        return companies.hire(row, seat_id,
                              [a.model_dump() for a in body.answers])
    except companies.CompanyError as exc:
        _fail(exc)


class CompanyPlan(BaseModel):
    description: str | None = Field(
        default=None, max_length=2000,
        description="What the store is meant to be, in the founder's "
                    "words.")


class SeatAssign(BaseModel):
    profile_id: str = Field(max_length=80)


@router.post("/companies/{company_id}/plan", status_code=201)
def plan(company_id: str, body: CompanyPlan, request: Request) -> dict:
    """The predicted roster — suggestions, never walls; nothing here
    opens a seat."""
    row = _company_or_404(company_id, request)
    try:
        return {"suggestions": companies.plan_company(
            row, body.description or "",
            cloud=getattr(request.app.state, "cloud", None))}
    except companies.CompanyError as exc:
        _fail(exc)


@router.post("/companies/{company_id}/seats/{seat_id}/assign",
             status_code=201)
def assign(company_id: str, seat_id: str, body: SeatAssign,
           request: Request) -> dict:
    """Bring your own hire — an existing or blended profile takes the
    seat; see qrme/company.py."""
    row = _company_or_404(company_id, request)
    try:
        return companies.fill_seat(row, seat_id, body.profile_id)
    except companies.CompanyError as exc:
        _fail(exc)


class CompanyPublish(BaseModel):
    tagline: str | None = Field(
        default=None, max_length=300,
        description="What the storefront says this company does.")


@router.post("/companies/{company_id}/publish", status_code=201)
def publish(company_id: str, body: CompanyPublish, request: Request) -> dict:
    """Open for business — see qrme/company.py for what a storefront is."""
    row = _company_or_404(company_id, request)
    try:
        return companies.publish(row, body.tagline)
    except companies.CompanyError as exc:
        _fail(exc)


@router.post("/companies/{company_id}/unpublish")
def unpublish(company_id: str, request: Request) -> dict:
    row = _company_or_404(company_id, request)
    try:
        return companies.unpublish(row)
    except companies.CompanyError as exc:
        _fail(exc)


@router.post("/companies/{company_id}/seats/{seat_id}/retire")
def retire(company_id: str, seat_id: str, request: Request) -> dict:
    row = _company_or_404(company_id, request)
    try:
        return companies.retire(row, seat_id)
    except companies.CompanyError as exc:
        _fail(exc)
