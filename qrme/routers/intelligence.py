"""Adaptation & autonomy: embeddings, specialists, grants/tasks, offline
fine-tuning, and the cloud model tier."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from .. import adaptation, db, tasks
from ..common import profile_or_404, require_owner
from ..models import GrantCreate, SpecialistSet, TaskRun

router = APIRouter()


# -- Latent persona embeddings (claims 21/22) --------------------------------

@router.get("/profiles/{profile_id}/embedding/{interactor_id}")
def get_embedding(profile_id: str, interactor_id: str,
                  request: Request) -> dict:
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    embedding = adaptation.get(profile_id, interactor_id)
    if embedding is None:
        raise HTTPException(404, "no embedding yet — interact first")
    return embedding


# -- Domain specialists (claim 24) -------------------------------------------

@router.put("/profiles/{profile_id}/specialists")
def set_specialist(profile_id: str, body: SpecialistSet,
                   request: Request) -> dict:
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    profile_or_404(body.specialist_profile_id)
    conn = db.connect()
    conn.execute(
        "INSERT INTO specialists (profile_id, domain,"
        " specialist_profile_id, created_at) VALUES (?,?,?,?)"
        " ON CONFLICT (profile_id, domain) DO UPDATE SET"
        " specialist_profile_id=excluded.specialist_profile_id",
        (profile_id, body.domain, body.specialist_profile_id, db.utcnow()),
    )
    conn.commit()
    return {"profile_id": profile_id, "domain": body.domain,
            "specialist_profile_id": body.specialist_profile_id}


@router.get("/profiles/{profile_id}/specialists")
def get_specialists(profile_id: str, request: Request) -> list[dict]:
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    rows = db.connect().execute(
        "SELECT domain, specialist_profile_id FROM specialists"
        " WHERE profile_id=?", (profile_id,)).fetchall()
    return [dict(r) for r in rows]


# -- Revocable grants & autonomous tasks (claim 25) --------------------------

@router.post("/profiles/{profile_id}/grants", status_code=201)
def create_grant(profile_id: str, body: GrantCreate, request: Request) -> dict:
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    return tasks.create_grant(profile_id, body.scope)


@router.delete("/grants/{grant_id}")
def revoke_grant(grant_id: str, request: Request) -> dict:
    row = db.connect().execute(
        "SELECT profile_id FROM grants WHERE id=?", (grant_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "grant not found")
    require_owner(row["profile_id"], request)
    tasks.revoke_grant(grant_id)
    return {"id": grant_id, "revoked": True}


@router.post("/profiles/{profile_id}/tasks", status_code=201)
def run_task(profile_id: str, body: TaskRun, request: Request) -> dict:
    profile = profile_or_404(profile_id)
    require_owner(profile_id, request)
    result = tasks.run(profile, body.kind, body.topic, body.grant_token,
                       pdi=request.app.state.pdi,
                       cloud=request.app.state.cloud)
    if result["status"] == "failed" and "grant" in result.get("reason", ""):
        raise HTTPException(403, result["reason"])
    return result


@router.get("/profiles/{profile_id}/tasks")
def list_tasks(profile_id: str, request: Request) -> list[dict]:
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    return tasks.list_tasks(profile_id)


# -- Offline fine-tuning (claim 26) ------------------------------------------

@router.post("/profiles/{profile_id}/finetune", status_code=201)
def finetune(profile_id: str, request: Request) -> dict:
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    return adaptation.finetune(profile_id, pdi=request.app.state.pdi)


# -- Cloud model tier --------------------------------------------------------

@router.get("/cloud/status")
def cloud_status(request: Request) -> dict:
    """Whether a Cloud Model Gateway is configured, and what it serves."""
    cloud = request.app.state.cloud
    info = cloud.model_info() if cloud is not None else None
    return {
        "cloud": cloud is not None,
        "model": info,
        "fallback": "local provider (Anthropic SDK or offline stub)",
        "contribution": "opt-in per profile via cloud_contribution; "
                        "anonymized rated exchanges only; revocable anytime",
    }
