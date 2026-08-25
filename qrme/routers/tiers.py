"""Membership — the pricing page, and joining or leaving a plan.

The gate itself is not here. It is an application-wide dependency installed in
`api.py`, for the reason `qrme/tiers.py` gives: a check per paid route is a
check somebody forgets at the eleventh one. These routes are only the account's
own view of its membership, and the public price list.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from .. import auth, tiers
from .. import i18n

router = APIRouter()


class Subscribe(BaseModel):
    plan: str = Field(description="basic | pro")


def _require_account(account_id: str, request: Request) -> None:
    """The caller must hold an owner token for a profile on this account.

    An account id is not a secret and not a credential — it is whatever string
    the owner supplied at profile creation — so `?account_id=` on its own
    proves nothing. Without this, reading somebody's plan (and cancelling it)
    would take only a guess at their owner id.
    """
    who = auth.principal(request)
    if who is None:
        raise HTTPException(401, "authentication required")
    if who.get("role") != "owner":
        raise HTTPException(403, "not authorized for this account")
    from .. import db

    row = db.connect().execute(
        "SELECT owner_id FROM profiles WHERE id=?",
        (who["subject_id"],)).fetchone()
    if row is None or row["owner_id"] != account_id:
        raise HTTPException(403, "not authorized for this account")


@router.get("/plans")
def plans() -> dict:
    """The price list. Public — a paywall nobody can read the terms of before
    signing in is one people bounce off.

    Generated from the same table the gate reads, so the page and the refusal
    cannot disagree about what a plan includes.
    """
    return tiers.catalogue()


@router.get("/memberships/{account_id}")
def membership(account_id: str, request: Request) -> dict:
    """What this account holds, what it reaches, and what is locked."""
    _require_account(account_id, request)
    return tiers.membership(account_id)


@router.post("/memberships/{account_id}")
def subscribe(account_id: str, body: Subscribe, request: Request) -> dict:
    """Join a plan, or move between them. Billing is simulated and the
    response says so in its own body, like every other money-bearing surface
    in this repository."""
    _require_account(account_id, request)
    try:
        return tiers.subscribe(account_id, body.plan)
    except tiers.TierError as exc:
        raise HTTPException(422, i18n.raised(exc)) from None


@router.delete("/memberships/{account_id}")
def cancel(account_id: str, request: Request) -> dict:
    """End it. The account becomes a visitor and **keeps its profiles** — a
    lapsed subscription is not a reason to delete somebody's work, and a
    product that deleted it is one nobody could safely try."""
    _require_account(account_id, request)
    return tiers.cancel(account_id)
