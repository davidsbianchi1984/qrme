"""Messaging, feature switches, and the homepage — the routes.

Reads of a homepage are public the way a profile card is: the page exists
to be looked at, and its sandbox is what makes that safe. Everything else
is the owner's: the switches, the outbox, and the editor. The owner is
detected on the homepage read rather than demanded, so one route serves
the stranger's view and the owner's sandbox without a second door.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from fastapi import APIRouter, HTTPException, Request

from .. import auth, social

router = APIRouter()


class FeatureSet(BaseModel):
    feature: str = Field(max_length=40)
    enabled: bool


class MessageSend(BaseModel):
    to: str = Field(max_length=80)
    body: str = Field(max_length=2000)


class HomepageSet(BaseModel):
    headline: str | None = Field(default=None, max_length=120)
    about: str | None = Field(default=None, max_length=2000)
    theme: dict | None = None
    links: list[dict] | None = None
    top_friends: list[str] | None = None


def _fail(exc: social.SocialError):
    return HTTPException(422, str(exc))


@router.get("/profiles/{profile_id}/features")
def get_features(profile_id: str, request: Request) -> dict:
    auth.require(request, "owner", profile_id)
    return social.features_of(profile_id)


@router.put("/profiles/{profile_id}/features")
def set_feature(profile_id: str, body: FeatureSet, request: Request) -> dict:
    auth.require(request, "owner", profile_id)
    try:
        return social.set_feature(profile_id, body.feature, body.enabled)
    except social.SocialError as exc:
        raise _fail(exc) from exc


@router.post("/profiles/{profile_id}/messages", status_code=201)
def send_message(profile_id: str, body: MessageSend,
                 request: Request) -> dict:
    auth.require(request, "owner", profile_id)
    try:
        return social.send_message(profile_id, body.to, body.body)
    except social.SocialError as exc:
        raise _fail(exc) from exc


@router.get("/profiles/{profile_id}/messages")
def read_messages(profile_id: str, request: Request,
                  with_id: str | None = None) -> dict:
    """The thread list, or — `?with_id=` — one conversation."""
    auth.require(request, "owner", profile_id)
    if with_id:
        return {"with": with_id,
                "messages": social.thread(profile_id, with_id)}
    return {"threads": social.threads(profile_id)}


@router.get("/profiles/{profile_id}/homepage")
def view_homepage(profile_id: str, request: Request) -> dict:
    """The page, for whoever is looking. The owner sees their own sandbox
    even with the switch off — it is theirs to edit; only *showing* it is
    what the switch governs."""
    is_owner = False
    try:
        auth.require(request, "owner", profile_id)
        is_owner = True
    except HTTPException:
        pass
    try:
        return social.homepage(profile_id, viewer_is_owner=is_owner)
    except social.SocialError as exc:
        raise HTTPException(404, "this homepage is not public") from exc


@router.put("/profiles/{profile_id}/homepage")
def edit_homepage(profile_id: str, body: HomepageSet,
                  request: Request) -> dict:
    auth.require(request, "owner", profile_id)
    try:
        return social.set_homepage(profile_id, body.model_dump(
            exclude_none=True))
    except social.SocialError as exc:
        raise _fail(exc) from exc
