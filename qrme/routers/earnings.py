"""Creator earnings: the owner statement over the ledger.

A creator authenticates as any profile they own; the statement covers
everything accrued to their ``owner_id`` — priced pack sales (knowledge,
robot task, and rated packs alike) and license fees — with a simulated
payout that sweeps the accrued balance and stamps every entry."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from .. import campaigns, ledger
from ..common import interactor_or_404, profile_or_404, require_owner
from ..models import CampaignCreate, DonationCreate, ProceedsSet

router = APIRouter()


def _owner_of(profile_id: str, request: Request) -> str:
    profile = profile_or_404(profile_id)
    require_owner(profile_id, request)
    return profile["owner_id"]


@router.get("/profiles/{profile_id}/earnings")
def earnings(profile_id: str, request: Request) -> dict:
    """The creator's statement: every ledger entry accrued to this
    profile's owner, newest first, with accrued / paid / lifetime totals
    and a per-kind breakdown."""
    return ledger.statement(_owner_of(profile_id, request))


@router.post("/profiles/{profile_id}/earnings/payout", status_code=201)
def request_payout(profile_id: str, request: Request) -> dict:
    """Sweep the accrued balance into a payout (simulated transfer). 409
    when nothing is accrued — a payout of nothing is not a payout."""
    receipt = ledger.payout(_owner_of(profile_id, request))
    if receipt is None:
        raise HTTPException(409, "nothing accrued — the balance is zero")
    return receipt


# -- Crowdfunding: proceeds where the user said (spec [0020] ex. two) --------

@router.put("/profiles/{profile_id}/proceeds")
def set_proceeds(profile_id: str, body: ProceedsSet, request: Request) -> dict:
    """Designate the loved ones and organizations campaign money goes to.
    Owner-token gated on purpose: sunset leaves the living owner the pen,
    and verified owner death (/succeed) revokes it and hands a fresh one
    to the person they chose."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        return {"profile_id": profile_id,
                "proceeds_to": campaigns.designate(profile_id, body.designees)}
    except campaigns.CampaignError as e:
        raise HTTPException(422, str(e))


@router.get("/profiles/{profile_id}/proceeds")
def get_proceeds(profile_id: str) -> dict:
    """Public: a donor gives to the names on this list, not to the
    platform — so anyone may read it."""
    profile_or_404(profile_id)
    return {"profile_id": profile_id,
            "proceeds_to": campaigns.designation(profile_id)}


@router.post("/profiles/{profile_id}/campaigns", status_code=201)
def create_campaign(profile_id: str, body: CampaignCreate,
                    request: Request) -> dict:
    profile = profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        return campaigns.create(profile, body.title, body.goal, body.cause)
    except campaigns.CampaignError as e:
        raise HTTPException(422, str(e))


@router.get("/profiles/{profile_id}/campaigns")
def list_campaigns(profile_id: str) -> list[dict]:
    profile_or_404(profile_id)
    return campaigns.list_for(profile_id)


@router.get("/campaigns/{campaign_id}")
def get_campaign(campaign_id: str) -> dict:
    out = campaigns.view(campaign_id)
    if out is None:
        raise HTTPException(404, "campaign not found")
    return out


@router.post("/campaigns/{campaign_id}/donate", status_code=201)
def donate(campaign_id: str, body: DonationCreate) -> dict:
    """Give to an open campaign. No token required — a donor arriving from
    a beacon scan has no account, and requiring one gates generosity behind
    signup. A named giver is verified to exist; an anonymous gift is fine."""
    if body.giver_id:
        interactor_or_404(body.giver_id)
    try:
        return campaigns.donate(campaign_id, body.giver_id, body.amount,
                                note=body.note,
                                on_behalf_of=body.on_behalf_of)
    except campaigns.CampaignError as e:
        code = 404 if "no such" in str(e) else 422
        raise HTTPException(code, str(e))


@router.post("/campaigns/{campaign_id}/close")
def close_campaign(campaign_id: str, request: Request) -> dict:
    row = campaigns.view(campaign_id)
    if row is None:
        raise HTTPException(404, "campaign not found")
    require_owner(row["profile_id"], request)
    try:
        return campaigns.close(campaign_id)
    except campaigns.CampaignError as e:
        raise HTTPException(409, str(e))
