"""Gifts and marketplace purchases — the endpoints that move money.

Two rules run through all of it.

**The payer is the token, never the body.** Buyer, giver and seller are all
taken from the caller's credential. A body-supplied identity on a money
endpoint is a way to spend as someone else or be paid as someone else, and
there is no version of that which is merely a bug.

**The age check is the deployment's existing one.** Rated targets go through
``rated.viewer_is_adult`` exactly as every other rated surface does. Gifting
additionally requires a verified adult *whoever* the recipient is — see
:mod:`~qrme.commerce` for why a gift is not a small purchase.
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

from fastapi import APIRouter, HTTPException, Request

from .. import audience, auth, commerce, db, rated

router = APIRouter()


def _actor(request: Request) -> str:
    who = auth.principal(request)
    if who is None:
        raise HTTPException(401, "authentication required")
    return who["subject_id"]


def _earner(request: Request) -> str:
    """The **account** this caller's money lands in.

    An owner token's subject is a *profile*, not an account, and the ledger is
    keyed by ``owner_id``. Attributing a sale to the token's subject therefore
    wrote the credit under a profile id, and `GET /profiles/{id}/earnings`
    — which resolves the profile to its ``owner_id`` before querying — could
    not see it. A seller who priced a listing while signed in as their
    profile's owner made the sale, got a 201 saying *the sale is recorded on
    the seller's statement*, and had an empty statement. The money sat in the
    ledger under a key nothing reads.

    Nobody noticed because the console had no way to price a listing: the
    binding existed in `api.ts` and no screen called it. It went unnoticed on
    the phone too, where the Market tab prices listings as an *interactor*,
    whose subject id already is the account.

    `commerce.beneficiary_of` has resolved a profile to its owner for gifts
    since gifts existed. This is the same rule, applied to the other half of
    the money.
    """
    who = auth.principal(request)
    if who is None:
        raise HTTPException(401, "authentication required")
    if who["role"] != "owner":
        return who["subject_id"]
    row = db.connect().execute("SELECT owner_id FROM profiles WHERE id=?",
                               (who["subject_id"],)).fetchone()
    if row is None:
        raise HTTPException(403, "this token names no profile")
    return row["owner_id"]


def _fail(exc: commerce.CommerceError):
    if str(exc).startswith("no such "):
        return HTTPException(404, str(exc))
    if str(exc) in ("not your offer",):
        return HTTPException(403, str(exc))
    return HTTPException(422, str(exc))


def _verified_adult_or_403(request: Request) -> str:
    """A gift needs a verified adult giver, whoever the recipient is.

    Not because the recipient is sensitive — because the giver is. Livestream
    tipping is the mechanic that most reliably turns into money leaving the
    accounts of people who should not be spending it, and an unverified age is
    not evidence of an adult.
    """
    who = auth.principal(request)
    if who is None:
        raise HTTPException(401, "authentication required")
    if who["role"] != "interactor":
        raise HTTPException(
            403, "gifts come from a person, so this needs an interactor token")
    row = db.connect().execute(
        "SELECT birthdate FROM interactors WHERE id=?",
        (who["subject_id"],)).fetchone()
    if row is None or not row["birthdate"]:
        raise HTTPException(
            403, "gifting requires a verified birthdate on your account — an "
                 "unverified age is not evidence of an adult")
    if rated.age_of(date.fromisoformat(row["birthdate"])) < 18:
        raise HTTPException(403, "gifting is 18+")
    return who["subject_id"]


class OfferIn(BaseModel):
    price: float
    currency: str = Field(default="USD", max_length=3)
    stock: int | None = None


class PurchaseIn(BaseModel):
    # Agreeing to a number, where the number is read from the offer rather
    # than from here — so this confirms *the* price and cannot set one.
    accept_price: float | None = None


class GiftIn(BaseModel):
    amount: float
    note: str | None = Field(default=None, max_length=200)
    currency: str = Field(default="USD", max_length=3)


# --- selling and buying ---------------------------------------------------

@router.put("/marketplace/listings/{listing_id}/offer")
def put_offer(listing_id: str, body: OfferIn, request: Request) -> dict:
    """Put a price on a listing, making it buyable.

    The seller is the caller. Anyone can create a listing — that endpoint has
    never needed a token — so the seller is established here, where money
    starts, rather than back there where it did not exist.
    """
    try:
        return commerce.offer(listing_id, _earner(request), body.price,
                              body.currency, body.stock)
    except commerce.CommerceError as exc:
        raise _fail(exc) from exc


@router.get("/marketplace/listings/{listing_id}/offer")
def get_offer(listing_id: str) -> dict:
    """The price, if this listing is for sale. Public — a price a buyer cannot
    see before authenticating is not a price."""
    found = commerce.offer_for(listing_id)
    if found is None:
        raise HTTPException(404, "this listing is not for sale")
    return found


@router.delete("/marketplace/listings/{listing_id}/offer")
def delete_offer(listing_id: str, request: Request) -> dict:
    """Stop selling. The listing stays as a shop window; past orders stay as
    receipts."""
    try:
        return commerce.withdraw(listing_id, _earner(request))
    except commerce.CommerceError as exc:
        raise _fail(exc) from exc


@router.post("/marketplace/listings/{listing_id}/purchase", status_code=201)
def purchase(listing_id: str, body: PurchaseIn, request: Request) -> dict:
    """Buy it. Requires ``accept_price`` to match the offer."""
    buyer = _actor(request)
    # A rated listing is only purchasable by a verified adult, using the same
    # gate that hides it from an unverified browse in the first place.
    row = db.connect().execute(
        "SELECT profile_id FROM listings WHERE id=?", (listing_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "no such listing")
    if row["profile_id"] and audience.is_rated("profile", row["profile_id"]) \
            and not rated.viewer_is_adult(request):
        raise HTTPException(
            403, "18+ only — present an interactor token whose verified "
                 "birthdate shows 18 or older")
    try:
        return commerce.purchase(listing_id, buyer, body.accept_price)
    except commerce.CommerceError as exc:
        raise _fail(exc) from exc


@router.get("/orders")
def my_orders(request: Request) -> dict:
    """What you bought."""
    return {"orders": commerce.orders_for_buyer(_actor(request))}


@router.get("/marketplace/sales")
def my_sales(request: Request) -> dict:
    """What you sold."""
    return {"sales": commerce.orders_for_seller(_earner(request))}


# --- gifting --------------------------------------------------------------

@router.post("/{kind}/{subject_id}/gift", status_code=201)
def gift(kind: str, subject_id: str, body: GiftIn, request: Request) -> dict:
    """Send value to whoever is behind this profile or desk.

    Nothing is delivered in return — that is what makes it a gift, and why the
    response says plainly that it cannot be reversed here.
    """
    resolved = {"profiles": "profile", "desks": "desk"}.get(kind)
    if resolved is None:
        raise HTTPException(
            404, f"nothing at /{kind} to gift; a gift goes to a person, so it "
                 f"applies to profiles and desks")
    giver = _verified_adult_or_403(request)
    # A rated desk keeps its own gate on top of the giver being an adult:
    # the two answer different questions and neither substitutes.
    if audience.is_rated(resolved, subject_id) \
            and not rated.viewer_is_adult(request):
        raise HTTPException(
            403, "18+ only — present an interactor token whose verified "
                 "birthdate shows 18 or older")
    try:
        return commerce.gift(resolved, subject_id, giver, body.amount,
                             body.note, body.currency)
    except commerce.CommerceError as exc:
        raise _fail(exc) from exc


@router.get("/{kind}/{subject_id}/gifts")
def list_gifts(kind: str, subject_id: str, request: Request) -> dict:
    """Who gave what. Public, like a tip jar you can see into — but a rated
    desk's is behind the same gate as everything else about it."""
    resolved = {"profiles": "profile", "desks": "desk"}.get(kind)
    if resolved is None:
        raise HTTPException(404, f"nothing at /{kind} to gift")
    if audience.is_rated(resolved, subject_id) \
            and not rated.viewer_is_adult(request):
        raise HTTPException(
            403, "18+ only — present an interactor token whose verified "
                 "birthdate shows 18 or older")
    return {"gifts": commerce.gifts_for(resolved, subject_id),
            "total_amount": commerce.gift_total(resolved, subject_id),
            "cap_per_gift": commerce.GIFT_MAX}
