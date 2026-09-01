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

from .. import auth, company as companies, db

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
