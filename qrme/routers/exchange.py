"""The agreement two people sign before work changes hands.

Mounted at ``/exchanges``. Every route establishes **who is calling** before it
does anything, because almost every rule here is about which of the two parties
is acting — and an id in a request body is a claim, not a fact.

That was not true when this router was first written: the acting party came
from the body and was never checked against the caller's token, so an anonymous
stranger could forge both signatures on somebody else's agreement, open its
channel, and accept delivery of an executable on their behalf. Every consent
property `qrme/exchange.py` describes rested on a check that did not exist.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from .. import exchange
from ..common import require_one_of, require_self

router = APIRouter()


def _fail(exc: Exception) -> HTTPException:
    return HTTPException(422, str(exc))


def _parties(exchange_id: str) -> list[str]:
    """The two people on an exchange, or 404. Read before authorizing, so a
    stranger cannot use the difference between 403 and 404 to discover which
    exchange ids exist."""
    try:
        row = exchange.get(exchange_id)
    except exchange.ExchangeError as exc:
        raise HTTPException(404, str(exc)) from None
    return [row["host_id"], row["guest_id"]]


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

    The one open route here: it describes the feature rather than anybody's
    agreement, and a client needs it before there is anything to be a party to.
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
            "only the two parties can read or act on an exchange",
        ],
    }


@router.post("/exchanges", status_code=201)
def propose(body: ProposeIn, request: Request) -> dict:
    """Start the document. It is a draft — nothing can move yet.

    The proposer must be one of the two parties: an exchange invented by a
    third party, naming two people who never spoke, is a phishing primitive.
    """
    require_one_of([body.host_id, body.guest_id], request)
    try:
        return exchange.propose(
            body.host_id, body.guest_id, body.work, body.industry,
            includes=body.includes, excludes=body.excludes, fee=body.fee,
            desk_id=body.desk_id)
    except exchange.ExchangeError as exc:
        raise _fail(exc) from None


@router.get("/exchanges/{exchange_id}")
def read(exchange_id: str, request: Request) -> dict:
    """The whole agreement: manifest, signatures, and whether it is open.

    Readable by the two parties only. A manifest names somebody's files, their
    sizes and what the work is worth — it is the private part, not the public
    one.
    """
    parties = _parties(exchange_id)
    require_one_of(parties, request)
    return exchange.get(exchange_id)


@router.post("/exchanges/{exchange_id}/items", status_code=201)
def add_item(exchange_id: str, body: ItemIn, request: Request) -> dict:
    """List one thing that will cross. Draft only, and by a party only."""
    require_one_of(_parties(exchange_id), request)
    try:
        return exchange.add_item(exchange_id, body.direction, body.name,
                                 body.kind, body.bytes, body.note)
    except exchange.ExchangeError as exc:
        raise _fail(exc) from None


@router.delete("/exchanges/{exchange_id}/items/{item_id}")
def remove_item(exchange_id: str, item_id: str, request: Request) -> dict:
    require_one_of(_parties(exchange_id), request)
    try:
        return exchange.remove_item(exchange_id, item_id)
    except exchange.ExchangeError as exc:
        raise _fail(exc) from None


@router.post("/exchanges/{exchange_id}/sign")
def sign(exchange_id: str, body: PartyIn, request: Request) -> dict:
    """Agree to exactly this manifest, and to nothing it becomes later.

    The signature is bound to the caller's token, not to the id they typed.
    Forging the other side's signature is the one thing that would make this
    whole module theatre.
    """
    _parties(exchange_id)
    require_self(body.actor_id, request)
    try:
        return exchange.sign(exchange_id, body.actor_id)
    except exchange.ExchangeError as exc:
        raise _fail(exc) from None


@router.post("/exchanges/{exchange_id}/reopen")
def reopen(exchange_id: str, body: PartyIn, request: Request) -> dict:
    """Make it editable again. Both signatures go; both are needed afresh."""
    _parties(exchange_id)
    require_self(body.actor_id, request)
    try:
        return exchange.reopen(exchange_id, body.actor_id)
    except exchange.ExchangeError as exc:
        raise _fail(exc) from None


@router.get("/exchanges/{exchange_id}/channel")
def channel(exchange_id: str, request: Request) -> dict:
    """Whether anything may move, and what. The one call a transport asks."""
    require_one_of(_parties(exchange_id), request)
    return exchange.channel(exchange_id)


@router.post("/exchanges/{exchange_id}/items/{item_id}/accept")
def accept(exchange_id: str, item_id: str, body: PartyIn,
           request: Request) -> dict:
    """Take delivery of one item — the receiving side only, and only itself.

    Accepting on somebody's behalf is how a `build` lands on a machine whose
    owner never agreed to it.
    """
    _parties(exchange_id)
    require_self(body.actor_id, request)
    try:
        return exchange.accept_item(exchange_id, item_id, body.actor_id)
    except exchange.ExchangeError as exc:
        raise _fail(exc) from None


@router.post("/exchanges/{exchange_id}/withdraw")
def withdraw(exchange_id: str, body: PartyIn, request: Request) -> dict:
    _parties(exchange_id)
    require_self(body.actor_id, request)
    try:
        return exchange.withdraw(exchange_id, body.actor_id)
    except exchange.ExchangeError as exc:
        raise _fail(exc) from None


@router.get("/parties/{party_id}/exchanges")
def for_party(party_id: str, request: Request) -> dict:
    """Everything this person has agreed to, or been asked to. Themselves
    only — it is a list of who they are doing business with."""
    require_self(party_id, request)
    return {"party_id": party_id, "exchanges": exchange.for_party(party_id)}
