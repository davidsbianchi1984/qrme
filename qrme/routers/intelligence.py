"""Adaptation & autonomy: embeddings, specialists, grants/tasks, offline
fine-tuning, and the cloud model tier."""

from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException, Request

from .. import (adaptation, agentlight, db, delegation, offline, simulation,
                tasks, workflows)
from ..common import (
    anonymized_exchange, interactor_or_404, profile_or_404,
    require_interactor, require_owner, require_owner_or_interactor,
)
from ..models import (
    DelegatedWorkflowCreate, DelegationSet, GrantCreate, SimulationRun,
    SpecialistSet, TaskRun, WorkflowCreate, WorkflowResume,
)

router = APIRouter()


@router.get("/agent/lights")
def agent_lights() -> dict:
    """What the three status lights mean, and which states drive each.

    Published so a client renders the same key the screens do. The legend is
    built from the mapping rather than written out beside it — a legend that
    is maintained separately eventually describes a mapping the code does not
    have, and it is the legend people trust.
    """
    return {"order": list(agentlight.ORDER), "legend": agentlight.legend(),
            "question": "does this agent need me right now?"}


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


# -- Autonomous multi-step workflows (claim 25, extended) --------------------

def _workflow_or_404(profile_id: str, workflow_id: str) -> dict:
    wf = workflows.get(profile_id, workflow_id)
    if wf is None:
        raise HTTPException(404, "workflow not found")
    return wf


@router.post("/profiles/{profile_id}/workflows", status_code=201)
def create_workflow(profile_id: str, body: WorkflowCreate,
                    request: Request) -> dict:
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    grant_id = None
    if body.grant_token:
        grant = tasks._grant_for(profile_id, body.grant_token)
        if grant is None or grant["revoked"]:
            raise HTTPException(403, "grant revoked or unknown")
        grant_id = grant["id"]
    try:
        return workflows.create(profile_id, body.goal, body.plan, grant_id)
    except ValueError as e:
        raise HTTPException(422, str(e))


@router.get("/profiles/{profile_id}/workflows")
def list_workflows(profile_id: str, request: Request) -> list[dict]:
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    return workflows.list_for(profile_id)


@router.get("/profiles/{profile_id}/workflows/{workflow_id}")
def get_workflow(profile_id: str, workflow_id: str, request: Request) -> dict:
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    return _workflow_or_404(profile_id, workflow_id)


@router.post("/profiles/{profile_id}/workflows/{workflow_id}/advance")
def advance_workflow(profile_id: str, workflow_id: str,
                     request: Request) -> dict:
    profile = profile_or_404(profile_id)
    require_owner(profile_id, request)
    wf = _workflow_or_404(profile_id, workflow_id)
    return workflows.advance(profile, wf, pdi=request.app.state.pdi,
                             cloud=request.app.state.cloud)


@router.post("/profiles/{profile_id}/workflows/{workflow_id}/resume")
def resume_workflow(profile_id: str, workflow_id: str, body: WorkflowResume,
                    request: Request) -> dict:
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    wf = _workflow_or_404(profile_id, workflow_id)
    try:
        return workflows.resume(profile_id, wf, body.input)
    except ValueError as e:
        raise HTTPException(409, str(e))


@router.post("/profiles/{profile_id}/workflows/{workflow_id}/cancel")
def cancel_workflow(profile_id: str, workflow_id: str,
                    request: Request) -> dict:
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    wf = _workflow_or_404(profile_id, workflow_id)
    return workflows.cancel(profile_id, wf)


# -- Delegated workflows: somebody else starting one -------------------------
#
# The routes above are owner-only and stay that way. These are the separate
# surface an interactor reaches — JIM's Guardian handing work to a specialist
# it is already in conversation with. See qrme/delegation.py for why relaxing
# the owner routes would have been the wrong fix.

def _delegated_or_404(profile_id: str, workflow_id: str,
                      request: Request) -> tuple[dict, str]:
    """Resolve a delegated workflow and authorize the caller.

    A workflow the owner started has no `delegated_workflows` row, so it 404s
    here however the caller authenticates — the two surfaces never merge.
    """
    who = delegation.started_by(profile_id, workflow_id)
    if who is None:
        raise HTTPException(404, "no delegated workflow with that id")
    require_owner_or_interactor(profile_id, who, request)
    wf = workflows.get(profile_id, workflow_id)
    if wf is None:                    # pragma: no cover - FK makes this unreachable
        raise HTTPException(404, "workflow not found")
    return wf, who


@router.put("/profiles/{profile_id}/delegation")
def set_delegation(profile_id: str, body: DelegationSet,
                   request: Request) -> dict:
    """Declare which workflow phases somebody else may start on this profile.

    Off until this is called. A policy that delegates `research` without a
    grant is refused here, where the owner can read the reason.
    """
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    grant_id = None
    if body.grant_token:
        grant = tasks._grant_for(profile_id, body.grant_token)
        if grant is None or grant["revoked"]:
            raise HTTPException(403, "grant revoked or unknown")
        grant_id = grant["id"]
    try:
        return delegation.set_policy(profile_id, body.phases, grant_id,
                                     body.enabled)
    except ValueError as e:
        raise HTTPException(422, str(e))


@router.get("/profiles/{profile_id}/delegation")
def get_delegation(profile_id: str) -> dict:
    """What a caller may ask this profile to do — readable without a token.

    It is a capability advertisement, so a client can decide whether a handoff
    is possible before attempting one. Reports the permitted phases and never
    the grant behind them.
    """
    profile_or_404(profile_id)
    return delegation.offer(profile_id)


@router.post("/profiles/{profile_id}/delegated-workflows", status_code=201)
def start_delegated_workflow(profile_id: str, body: DelegatedWorkflowCreate,
                             request: Request) -> dict:
    """Start a workflow on this profile as an interactor, inside the owner's
    policy. Requires an existing conversation — delegated work is for somebody
    already talking to the profile, not a stranger holding its id."""
    profile_or_404(profile_id)
    interactor_or_404(body.interactor_id)
    require_interactor(body.interactor_id, request)
    if not delegation.in_conversation(profile_id, body.interactor_id):
        raise HTTPException(
            403, "not in conversation with this profile; delegated work is "
                 "for somebody already talking to it")
    try:
        return delegation.start(profile_id, body.interactor_id, body.goal,
                                body.plan)
    except delegation.DelegationError as e:
        raise HTTPException(403, str(e))
    except ValueError as e:
        raise HTTPException(422, str(e))


@router.get("/profiles/{profile_id}/delegated-workflows/{workflow_id}")
def get_delegated_workflow(profile_id: str, workflow_id: str,
                           request: Request) -> dict:
    profile_or_404(profile_id)
    wf, who = _delegated_or_404(profile_id, workflow_id, request)
    return {**wf, "delegated_to": who}


@router.post("/profiles/{profile_id}/delegated-workflows/{workflow_id}/advance")
def advance_delegated_workflow(profile_id: str, workflow_id: str,
                               request: Request) -> dict:
    """Run the next phase. Without this the handoff would be inert — the owner
    would have to advance work they did not ask for."""
    profile = profile_or_404(profile_id)
    wf, who = _delegated_or_404(profile_id, workflow_id, request)
    out = workflows.advance(profile, wf, pdi=request.app.state.pdi,
                            cloud=request.app.state.cloud)
    return {**out, "delegated_to": who}


@router.post("/profiles/{profile_id}/delegated-workflows/{workflow_id}/resume")
def resume_delegated_workflow(profile_id: str, workflow_id: str,
                              body: WorkflowResume, request: Request) -> dict:
    profile_or_404(profile_id)
    wf, who = _delegated_or_404(profile_id, workflow_id, request)
    try:
        return {**workflows.resume(profile_id, wf, body.input),
                "delegated_to": who}
    except ValueError as e:
        raise HTTPException(409, str(e))


# -- Real-time simulation / predictive modeling (spec clauses 1 & 5) ---------

@router.post("/profiles/{profile_id}/simulate", status_code=201)
def simulate(profile_id: str, body: SimulationRun, request: Request) -> dict:
    """Run a real-time simulation of the represented person's actions,
    workflow, and decision-making in a scenario. Owner-only operational
    insight; the narrative is watermarked synthetic and never distributed."""
    profile = profile_or_404(profile_id)
    require_owner(profile_id, request)
    if body.interactor_id:
        interactor_or_404(body.interactor_id)
    return simulation.run(profile, body.scenario, body.horizon,
                          body.interactor_id, pdi=request.app.state.pdi,
                          cloud=request.app.state.cloud)


@router.get("/profiles/{profile_id}/simulations")
def list_simulations(profile_id: str, request: Request) -> list[dict]:
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    return simulation.list_runs(profile_id)


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


# -- Cloud contribution: preview, history, revoke ----------------------------

@router.get("/profiles/{profile_id}/cloud-contribution")
def contribution_view(profile_id: str, request: Request) -> dict:
    """Owner view of the contribution loop: whether it's on, **exactly** what
    the next contribution would contain (a dry-run preview, nothing is sent),
    and the log of everything that has ever left."""
    profile = profile_or_404(profile_id)
    require_owner(profile_id, request)
    conn = db.connect()

    # Dry-run preview: the anonymized exchange that would be contributed if
    # the most recently active interactor up-rated right now.
    preview = None
    latest = conn.execute(
        "SELECT interactor_id FROM messages WHERE profile_id=?"
        " AND status='approved' ORDER BY created_at DESC, rowid DESC LIMIT 1",
        (profile_id,)).fetchone()
    if latest:
        exchange = anonymized_exchange(profile, profile_id,
                                       latest["interactor_id"])
        if exchange:
            preview = {"source": "qrme", "kind": "rated_exchange",
                       "quality": "positive", "purpose": profile["purpose"],
                       "exchange": exchange}

    history = [{"ref": r["ref"], "at": r["contributed_at"],
                "revoked": bool(r["revoked"]),
                "payload": json.loads(r["payload"])}
               for r in conn.execute(
                   "SELECT * FROM contribution_log WHERE profile_id=?"
                   " ORDER BY contributed_at, rowid", (profile_id,)).fetchall()]
    return {
        "opted_in": bool(profile["cloud_contribution"]),
        "policy": "only positively-rated exchanges, anonymized (no profile, "
                  "owner, or interactor ids; the persona name replaced); "
                  "each item carries a random ref so it can be deleted at the "
                  "gateway without identifying anyone",
        "preview_next": preview,
        "contributed": history,
    }


@router.post("/profiles/{profile_id}/cloud-contribution/revoke")
def revoke_contributions(profile_id: str, request: Request) -> dict:
    """Turn contribution off **and** delete everything already contributed:
    the gateway is asked to drop each item by its opaque ref."""
    profile = profile_or_404(profile_id)
    require_owner(profile_id, request)
    conn = db.connect()
    conn.execute("UPDATE profiles SET cloud_contribution=0 WHERE id=?",
                 (profile_id,))
    refs = [r["ref"] for r in conn.execute(
        "SELECT ref FROM contribution_log WHERE profile_id=? AND revoked=0",
        (profile_id,)).fetchall()]
    cloud = request.app.state.cloud
    if not refs:
        deleted_at_gateway = True          # nothing ever left
    elif cloud is None:
        deleted_at_gateway = False         # nothing to ask; flag still turned off
    else:
        deleted_at_gateway = cloud.revoke_contributions(refs)
    conn.execute("UPDATE contribution_log SET revoked=1 WHERE profile_id=?",
                 (profile_id,))
    conn.commit()
    return {
        "opted_in": False,
        "revoked": len(refs),
        "deleted_at_gateway": bool(deleted_at_gateway),
        "note": "future contributions stopped; past items were requested "
                "deleted by their anonymous refs",
    }


# -- Offline-first posture ---------------------------------------------------

@router.get("/offline/status")
def offline_status(request: Request) -> dict:
    """Report the offline posture: whether the platform is running fully
    on-host and what that guarantees."""
    return offline.status(request.app)
