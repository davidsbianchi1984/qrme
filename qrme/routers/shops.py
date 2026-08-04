"""Shops: the storefront routes.

A shop is not a desk, and the split shows in what these routes do *not*
carry: no sessions, no rings, no connection offers, no lent skills. Reads
are public the way the marketplace is — a storefront that requires a token
to window-shop is a storefront with the lights off. Writes split two ways:
the shop's own management needs the profile owner's token, and placing an
order needs an interactor's — the buyer JIM's tandem already maintains for
its user, so a purchase is attributable the way a conversation is.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from fastapi import APIRouter, HTTPException, Request

from .. import auth, shops
from .interaction import require_interactor

router = APIRouter()


class ShopOpen(BaseModel):
    profile_id: str = Field(max_length=80)
    name: str = Field(max_length=120)
    blurb: str | None = Field(default=None, max_length=300)
    tag: str | None = Field(default=None, max_length=60)


class OfferingAdd(BaseModel):
    kind: str = Field(max_length=20)
    title: str = Field(max_length=120)
    blurb: str | None = Field(default=None, max_length=300)
    price: float
    currency: str = Field(default="USD", max_length=8)
    availability: str = Field(default="in_stock", max_length=20)


class OrderPlace(BaseModel):
    offering_id: str = Field(max_length=80)
    buyer_id: str = Field(max_length=80)
    quantity: int = 1
    note: str | None = Field(default=None, max_length=300)


class OrderAdvance(BaseModel):
    to: str = Field(max_length=20)
    # Who is moving it: the seller presents the shop profile's owner token,
    # the buyer their interactor token. Stated, then verified — never
    # inferred from which transition was asked for.
    party: str = Field(max_length=10)


def _fail(exc: shops.ShopError):
    return HTTPException(422, str(exc))


def _require_seller(shop_id: str, request: Request) -> None:
    row = shops._shop_row(shop_id)
    auth.require(request, "owner", row["profile_id"])


@router.post("/shops", status_code=201)
def open_shop(body: ShopOpen, request: Request) -> dict:
    """Open the profile's shop, or edit it — one per profile."""
    auth.require(request, "owner", body.profile_id)
    try:
        return shops.open_shop(body.profile_id, body.name, body.blurb,
                               body.tag)
    except shops.ShopError as exc:
        raise _fail(exc) from exc


@router.get("/shops")
def list_shops(tag: str | None = None) -> list[dict]:
    return shops.shops(tag)


@router.get("/shops/{shop_id}")
def shop_card(shop_id: str) -> dict:
    try:
        return shops.shop(shop_id)
    except shops.ShopError as exc:
        raise HTTPException(404, "no such shop") from exc


@router.post("/shops/{shop_id}/offerings", status_code=201)
def add_offering(shop_id: str, body: OfferingAdd, request: Request) -> dict:
    _require_seller(shop_id, request)
    try:
        return shops.add_offering(shop_id, body.kind, body.title, body.blurb,
                                  body.price, body.currency,
                                  body.availability)
    except shops.ShopError as exc:
        raise _fail(exc) from exc


@router.delete("/shops/{shop_id}/offerings/{offering_id}")
def retire_offering(shop_id: str, offering_id: str, request: Request) -> dict:
    _require_seller(shop_id, request)
    try:
        return shops.retire_offering(shop_id, offering_id)
    except shops.ShopError as exc:
        raise _fail(exc) from exc


@router.post("/shops/{shop_id}/orders", status_code=201)
def place_order(shop_id: str, body: OrderPlace, request: Request) -> dict:
    """The buyer's press. Their interactor token is the credential — the
    same identity the tandem thread already runs on."""
    require_interactor(body.buyer_id, request)
    try:
        return shops.place_order(shop_id, body.offering_id, body.buyer_id,
                                 body.quantity, body.note)
    except shops.ShopError as exc:
        raise _fail(exc) from exc


@router.get("/shops/{shop_id}/orders")
def order_book(shop_id: str, request: Request) -> list[dict]:
    """The seller's order book. The buyer's history is theirs, read through
    their own door below — one list per party, never a shared one."""
    _require_seller(shop_id, request)
    return shops.orders_for_shop(shop_id)


@router.get("/shops/orders/of/{buyer_id}")
def buyer_orders(buyer_id: str, request: Request) -> list[dict]:
    require_interactor(buyer_id, request)
    return shops.orders_for_buyer(buyer_id)


@router.post("/shops/{shop_id}/orders/{order_id}/advance")
def advance_order(shop_id: str, order_id: str, body: OrderAdvance,
                  request: Request) -> dict:
    """One transition, by whoever may make it. The stated party is verified
    against its own credential before the state machine is consulted."""
    try:
        row = shops.order(order_id)
    except shops.ShopError as exc:
        raise HTTPException(404, "no such order") from exc
    if row["shop_id"] != shop_id:
        raise HTTPException(404, "no such order")
    if body.party == "seller":
        _require_seller(shop_id, request)
    elif body.party == "buyer":
        require_interactor(row["buyer_id"], request)
    else:
        raise HTTPException(422, "party is seller or buyer")
    try:
        return shops.advance_order(order_id, body.party, body.to)
    except shops.ShopError as exc:
        raise _fail(exc) from exc
