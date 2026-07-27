"""Like, comment, share, subscribe — the endpoints the buttons call.

Reads are public, because the counts under a profile card are part of the card
and a stranger who scanned a sticker should see them. Writes need a token: a
like from nobody in particular is a number anyone can manufacture, and the
whole point of :mod:`~qrme.audience` treating a like as a fact about a person
is that there is a person.

A rated target keeps its gate here. Every write below runs the deployment's
existing verified-adult check when the target is rated, rather than a second
implementation of it — the weaker of two gates is always the one that gets
used.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from fastapi import APIRouter, HTTPException, Request

from .. import audience, auth, db, rated

router = APIRouter()


# The path segment is the plural resource name the rest of the API already
# uses (`/profiles/…`, `/desks/…`), while audience.py works in singular kinds.
# Mapping here rather than exposing `/profile/{id}/like` keeps these endpoints
# reading like the routes they sit beside instead of like a separate API.
_KIND_BY_PATH = {"profiles": "profile", "desks": "desk",
                 "messages": "message", "listings": "listing",
                 "posts": "post"}


def _kind(path_kind: str) -> str:
    kind = _KIND_BY_PATH.get(path_kind)
    if kind is None:
        raise HTTPException(
            404, f"nothing at /{path_kind} to react to; expected one of "
                 f"{', '.join(sorted(_KIND_BY_PATH))}")
    return kind


def _actor(request: Request) -> str:
    who = auth.principal(request)
    if who is None:
        raise HTTPException(401, "authentication required")
    return who["subject_id"]


def _actor_row(request: Request) -> dict:
    """The caller as moderation sees them — birthdate included, because a
    minor is held to the strict filter whatever the target is set to."""
    who = auth.principal(request)
    if who is None or who["role"] != "interactor":
        return {"birthdate": None}
    row = db.connect().execute(
        "SELECT birthdate FROM interactors WHERE id=?",
        (who["subject_id"],)).fetchone()
    return {"birthdate": row["birthdate"] if row else None}


def _fail(exc: audience.AudienceError):
    # "no such profile" is a missing resource, not a malformed request — 404
    # keeps it consistent with every other resource lookup in the API. A 422
    # here would read as "your body was wrong" when the body was fine.
    if str(exc).startswith("no such "):
        return HTTPException(404, str(exc))
    return HTTPException(422, str(exc))


def _gate(kind: str, target_id: str, request: Request) -> None:
    """Refuse a rated target to a caller who is not a verified adult."""
    if audience.is_rated(kind, target_id) and not rated.viewer_is_adult(request):
        raise HTTPException(
            403, "18+ only — present an interactor token whose verified "
                 "birthdate shows 18 or older")


class CommentIn(BaseModel):
    body: str = Field(max_length=2000)


class ShareIn(BaseModel):
    channel: str = Field(default="link", max_length=40)


class SubscribeIn(BaseModel):
    tier: str = "follow"
    price: float = 0.0
    beneficiary: str | None = Field(default=None, max_length=80)
    # Explicit consent to a recurring charge, mirroring priced packs. A
    # subscription a viewer did not mean to start keeps costing them.
    accept_price: float | None = None


# --- like -----------------------------------------------------------------

@router.post("/{kind}/{target_id}/like", status_code=201)
def like(kind: str, target_id: str, request: Request) -> dict:
    """Like something. Calling twice is still one like, and not an error."""
    kind = _kind(kind)
    _gate(kind, target_id, request)
    try:
        return audience.like(kind, target_id, _actor(request))
    except audience.AudienceError as exc:
        raise _fail(exc) from exc


@router.delete("/{kind}/{target_id}/like")
def unlike(kind: str, target_id: str, request: Request) -> dict:
    kind = _kind(kind)
    try:
        return audience.unlike(kind, target_id, _actor(request))
    except audience.AudienceError as exc:
        raise _fail(exc) from exc


# --- comment --------------------------------------------------------------

@router.post("/{kind}/{target_id}/comments", status_code=201)
def add_comment(kind: str, target_id: str, body: CommentIn,
                request: Request) -> dict:
    """Leave a comment. Moderated at the target's own maturity setting.

    A blocked comment comes back to its author with the reason and is shown to
    nobody else — 201 rather than 422, because the comment *was* accepted and
    recorded; what happened to it is in ``status``.
    """
    kind = _kind(kind)
    _gate(kind, target_id, request)
    try:
        return audience.comment(kind, target_id, _actor(request), body.body,
                                author=_actor_row(request))
    except audience.AudienceError as exc:
        raise _fail(exc) from exc


@router.get("/{kind}/{target_id}/comments")
def list_comments(kind: str, target_id: str, request: Request) -> dict:
    """Approved comments, plus the caller's own blocked ones if they have any."""
    kind = _kind(kind)
    _gate(kind, target_id, request)
    who = auth.principal(request)
    return {"comments": audience.comments(
        kind, target_id, who["subject_id"] if who else None)}


@router.delete("/comments/{comment_id}")
def delete_comment(comment_id: str, request: Request) -> dict:
    """Withdraw your own comment."""
    try:
        return audience.delete_comment(comment_id, _actor(request))
    except audience.AudienceError as exc:
        if str(exc) == "no such comment":
            raise HTTPException(404, str(exc)) from exc
        if str(exc) == "not your comment":
            raise HTTPException(403, str(exc)) from exc
        raise _fail(exc) from exc


# --- share ----------------------------------------------------------------

@router.post("/{kind}/{target_id}/share", status_code=201)
def share(kind: str, target_id: str, body: ShareIn, request: Request) -> dict:
    """Record a share and hand back the link.

    Deliberately open to a caller with no token: someone who scanned a sticker
    is exactly the person most likely to pass it on, and has no account. The
    adult gate is not applied to the *sharer* because it is applied at the
    destination — a rated target's shared link opens the age wall, which is a
    gate that cannot be routed around by whoever sent it.
    """
    kind = _kind(kind)
    who = auth.principal(request)
    try:
        return audience.share(kind, target_id,
                              who["subject_id"] if who else None, body.channel)
    except audience.AudienceError as exc:
        raise _fail(exc) from exc


# --- subscribe ------------------------------------------------------------

@router.post("/{kind}/{subject_id}/subscribe", status_code=201)
def subscribe(kind: str, subject_id: str, body: SubscribeIn,
              request: Request) -> dict:
    """Follow (free) or subscribe (paid, recurring, simulated)."""
    kind = _kind(kind)
    _gate(kind, subject_id, request)
    try:
        return audience.subscribe(
            kind, subject_id, _actor(request), tier=body.tier,
            price=body.price, beneficiary=body.beneficiary,
            accept_price=body.accept_price)
    except audience.AudienceError as exc:
        raise _fail(exc) from exc


@router.delete("/{kind}/{subject_id}/subscribe")
def unsubscribe(kind: str, subject_id: str, request: Request) -> dict:
    kind = _kind(kind)
    try:
        return audience.cancel(kind, subject_id, _actor(request))
    except audience.AudienceError as exc:
        if str(exc) == "not subscribed":
            raise HTTPException(404, str(exc)) from exc
        raise _fail(exc) from exc


@router.post("/subscriptions/{sub_id}/renew", status_code=201)
def renew(sub_id: str, body: SubscribeIn, request: Request) -> dict:
    """Charge the next period.

    Explicit on purpose: nothing here bills on a timer, so a deployment left
    running does not accrue charges nobody authorised and nobody saw.
    """
    _actor(request)
    if not body.beneficiary:
        raise HTTPException(422, "renewing charges a period, so it needs the "
                                 "beneficiary the money accrues to")
    try:
        return audience.renew(sub_id, body.beneficiary)
    except audience.AudienceError as exc:
        if str(exc) == "no such subscription":
            raise HTTPException(404, str(exc)) from exc
        raise _fail(exc) from exc


@router.get("/subscriptions")
def my_subscriptions(request: Request, active: bool = True) -> dict:
    """Everything the caller subscribes to."""
    return {"subscriptions": audience.subscriptions_of(_actor(request),
                                                       active_only=active)}


@router.get("/{kind}/{subject_id}/subscribers")
def list_subscribers(kind: str, subject_id: str, request: Request,
                     active: bool = True) -> dict:
    """Who subscribes to this. Public: a subscriber count is part of a card."""
    kind = _kind(kind)
    _gate(kind, subject_id, request)
    try:
        audience._check_subject(kind)
    except audience.AudienceError as exc:
        raise _fail(exc) from exc
    return {"subscribers": audience.subscribers(kind, subject_id,
                                                active_only=active)}


# --- the numbers under the buttons ----------------------------------------

@router.get("/{kind}/{target_id}/audience")
def audience_counts(kind: str, target_id: str, request: Request) -> dict:
    """Likes, comments, shares, subscribers — and the caller's own state, so a
    client can render the buttons without a second round trip.

    Named *audience* rather than *engagement* because this codebase already
    uses "engagement" for the per-relationship EMA score that conditions the
    persona prompt. Two different numbers under one word would have been
    read as one number by whoever came next.
    """
    kind = _kind(kind)
    _gate(kind, target_id, request)
    who = auth.principal(request)
    try:
        audience._check_target(kind)
    except audience.AudienceError as exc:
        raise _fail(exc) from exc
    if not audience.target_exists(kind, target_id):
        raise HTTPException(404, f"no such {kind}")
    return audience.counts(kind, target_id,
                           who["subject_id"] if who else None)
