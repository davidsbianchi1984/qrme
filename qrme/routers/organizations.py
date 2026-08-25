"""The operational ecosystem: organizations, department agents, coordination.

Auth model: an organization belongs to an *account* (``owner_id``), but
tokens are per-profile — so every org route authenticates the caller as the
owner of some profile, then checks that profile belongs to the org's
account. That is the identity-router pattern: the profile id is the handle,
never the guessable ``owner_id`` string.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from .. import auth, db, organization
from ..common import profile_or_404
from ..models import (CoordinateRequest, DepartmentAdd, LeaseRequest,
                      OrganizationCreate)
from .. import i18n

router = APIRouter()


def _caller_owner_id(request: Request) -> str:
    """The account behind the presented owner token."""
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


def _org_or_404(org_id: str, request: Request) -> dict:
    org = organization.get(org_id)
    if org is None:
        raise HTTPException(404, "organization not found")
    if _caller_owner_id(request) != org["owner_id"]:
        raise HTTPException(403, "not this organization's owner")
    return org


@router.post("/organizations", status_code=201)
def create_organization(body: OrganizationCreate, request: Request) -> dict:
    owner_id = _caller_owner_id(request)
    try:
        return organization.create(owner_id, body.name)
    except organization.OrganizationError as e:
        raise HTTPException(422, i18n.raised(e))


@router.get("/organizations")
def list_organizations(request: Request) -> list[dict]:
    return organization.list_for(_caller_owner_id(request))


@router.post("/organizations/demo", status_code=201)
def seed_demo_organization(request: Request) -> dict:
    """One press, a staffed organization on the caller's own account —
    two enterprise agents with a little knowledge each, granted and
    desked, ready to coordinate."""
    return organization.seed_demo(_caller_owner_id(request))


@router.get("/organizations/{org_id}")
def get_organization(org_id: str, request: Request) -> dict:
    _org_or_404(org_id, request)
    return organization.view(org_id)


@router.post("/organizations/{org_id}/departments", status_code=201)
def add_department(org_id: str, body: DepartmentAdd,
                   request: Request) -> dict:
    org = _org_or_404(org_id, request)
    profile = profile_or_404(body.profile_id)
    try:
        return organization.add_department(org, body.name, body.role,
                                           profile, body.grant_token)
    except organization.OrganizationError as e:
        raise HTTPException(422, i18n.raised(e))


@router.post("/organizations/{org_id}/lease", status_code=201)
def lease_specialist(org_id: str, body: LeaseRequest,
                     request: Request) -> dict:
    """AI for lease: seat somebody else's licensed specialist as one of this
    organization's departments. The fee accrues to the specialist's owner;
    the lease is revocable from the owner's side at any time."""
    org = _org_or_404(org_id, request)
    source = profile_or_404(body.profile_id)
    try:
        return organization.lease_department(org, source, body.name,
                                             body.role)
    except organization.OrganizationError as e:
        raise HTTPException(422, i18n.raised(e))


@router.post("/organizations/{org_id}/coordinate", status_code=201)
def coordinate(org_id: str, body: CoordinateRequest,
               request: Request) -> dict:
    org = _org_or_404(org_id, request)
    try:
        return organization.coordinate(org, body.goal, body.from_department,
                                       pdi=request.app.state.pdi,
                                       cloud=request.app.state.cloud)
    except organization.OrganizationError as e:
        raise HTTPException(422, i18n.raised(e))


@router.get("/organizations/{org_id}/coordinations")
def list_coordinations(org_id: str, request: Request) -> list[dict]:
    _org_or_404(org_id, request)
    return organization.coordinations_for(org_id)
