"""Creator earnings: the owner statement over the ledger.

A creator authenticates as any profile they own; the statement covers
everything accrued to their ``owner_id`` — priced pack sales (knowledge,
robot task, and rated packs alike) and license fees — with a simulated
payout that sweeps the accrued balance and stamps every entry."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from .. import ledger
from ..common import profile_or_404, require_owner

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
