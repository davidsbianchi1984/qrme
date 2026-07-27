"""The agreement two people sign before work changes hands.

Mounted at ``/exchanges``. Every mutation names the party doing it, because
almost every rule here is about *which* of the two is acting: only the
receiving side accepts an item, either side may reopen or withdraw, and neither
side's signature alone opens anything.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .. import exchange

router = APIRouter()


def _fail(exc: Exception) -> HTTPException:
    return HTTPException(422, str(exc))


class ProposeIn(BaseModel):
    host_id: str
    guest_id: str
    work: str = Field(min_length=1, max_length=exchange.MAX_TEXT)
    industry: str
    includes: list[str] = []
    excludes: list[str] = []
    fee: float = 0.0
    desk_id: str | None = None


class ItemIn(BaseModel):
    direction: str
    name: str = Field(min_length=1, max_length=exchange.MAX_NAME)
    kind: str
    bytes: int = 0
    note: str = ""


class PartyIn(BaseModel):
    actor_id: str


@router.get("/exchanges/vocabulary")
def vocabulary() -> dict:
    """The closed sets a client should offer, and what each kind means.

    Published rather than kept internal so an editor can show the industries
    and item kinds up front instead of letting somebody type one and find out
    it was refused — and so the two kinds that *run on the receiving machine*
    can be flagged in the picker rather than only in the warning afterwards.
    """
    return {
        "industries": list(exchange.INDUSTRIES),
        "kinds": [{"key": k, "means": v, "runs": k in ("source", "build")}
                  for k, v in exchange.KINDS.items()],
        "states": list(exchange.STATES),
        "directions": ["host_to_guest", "guest_to_host"],
        "max_items": exchange.MAX_ITEMS,
        "rules": [
            "both parties sign the same manifest before anything can move",
            "any change to the manifest clears both signatures",
            "each item is accepted separately — nothing downloads by itself",
            "an exchange moves the listed items and grants no device access",
        ],
    }


@router.post("/exchanges", status_code=201)
def propose(body: ProposeIn) -> dict:
    """Start the document. It is a draft — nothing can move yet."""
    try:
        return exchange.propose(
            body.host_id, body.guest_id, body.work, body.industry,
            includes=body.includes, excludes=body.excludes, fee=body.fee,
            desk_id=body.desk_id)
    except exchange.ExchangeError as exc:
        raise _fail(exc) from None


@router.get("/exchanges/{exchange_id}")
def read(exchange_id: str) -> dict:
    """The whole agreement: manifest, signatures, and whether it is open.

    `signatures[].matches_current` is the field worth reading — a signature
    that no longer matches the manifest is shown rather than hidden, so a
    surface can say *they signed an earlier version of this*.
    """
    try:
        return exchange.get(exchange_id)
    except exchange.ExchangeError as exc:
        raise HTTPException(404, str(exc)) from None


@router.post("/exchanges/{exchange_id}/items", status_code=201)
def add_item(exchange_id: str, body: ItemIn) -> dict:
    """List one thing that will cross. Draft only."""
    try:
        return exchange.add_item(exchange_id, body.direction, body.name,
                                 body.kind, body.bytes, body.note)
    except exchange.ExchangeError as exc:
        raise _fail(exc) from None


@router.delete("/exchanges/{exchange_id}/items/{item_id}")
def remove_item(exchange_id: str, item_id: str) -> dict:
    try:
        return exchange.remove_item(exchange_id, item_id)
    except exchange.ExchangeError as exc:
        raise _fail(exc) from None


@router.post("/exchanges/{exchange_id}/sign")
def sign(exchange_id: str, body: PartyIn) -> dict:
    """Agree to exactly this manifest, and to nothing it becomes later."""
    try:
        return exchange.sign(exchange_id, body.actor_id)
    except exchange.ExchangeError as exc:
        raise _fail(exc) from None


@router.post("/exchanges/{exchange_id}/reopen")
def reopen(exchange_id: str, body: PartyIn) -> dict:
    """Make it editable again. Both signatures go; both are needed afresh."""
    try:
        return exchange.reopen(exchange_id, body.actor_id)
    except exchange.ExchangeError as exc:
        raise _fail(exc) from None


@router.get("/exchanges/{exchange_id}/channel")
def channel(exchange_id: str) -> dict:
    """Whether anything may move, and what. The one call a transport asks."""
    try:
        return exchange.channel(exchange_id)
    except exchange.ExchangeError as exc:
        raise HTTPException(404, str(exc)) from None


@router.post("/exchanges/{exchange_id}/items/{item_id}/accept")
def accept(exchange_id: str, item_id: str, body: PartyIn) -> dict:
    """Take delivery of one item — the receiving side only."""
    try:
        return exchange.accept_item(exchange_id, item_id, body.actor_id)
    except exchange.ExchangeError as exc:
        raise _fail(exc) from None


@router.post("/exchanges/{exchange_id}/withdraw")
def withdraw(exchange_id: str, body: PartyIn) -> dict:
    try:
        return exchange.withdraw(exchange_id, body.actor_id)
    except exchange.ExchangeError as exc:
        raise _fail(exc) from None


@router.get("/parties/{party_id}/exchanges")
def for_party(party_id: str) -> dict:
    """Everything this person has agreed to, or been asked to."""
    return {"party_id": party_id, "exchanges": exchange.for_party(party_id)}
