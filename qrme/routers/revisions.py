"""Editing and retracting your own turn in a conversation."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from .. import revisions
from ..common import profile_or_404, require_owner_or_interactor
from .. import i18n

router = APIRouter()


class MessageEdit(BaseModel):
    interactor_id: str = Field(min_length=1, max_length=64)
    content: str = Field(min_length=1, max_length=4000)


class MessageRetract(BaseModel):
    interactor_id: str = Field(min_length=1, max_length=64)


@router.patch("/profiles/{profile_id}/messages/{message_id}")
def edit_message(profile_id: str, message_id: str, body: MessageEdit,
                 request: Request) -> dict:
    """Change something you already said. Moderated as a fresh message, and it
    carries forward — the chat path rebuilds history from these rows, so the
    next reply reasons from the correction rather than the original."""
    profile_or_404(profile_id)
    require_owner_or_interactor(profile_id, body.interactor_id, request)
    try:
        return revisions.edit(message_id, body.content, body.interactor_id)
    except revisions.RevisionError as exc:
        raise HTTPException(422, i18n.raised(exc)) from None


@router.delete("/profiles/{profile_id}/messages/{message_id}")
def retract_message(profile_id: str, message_id: str, body: MessageRetract,
                    request: Request) -> dict:
    """Take it back. The row survives for the moderation trail; the text stops
    reaching the profile and stops being shown."""
    profile_or_404(profile_id)
    require_owner_or_interactor(profile_id, body.interactor_id, request)
    try:
        return revisions.retract(message_id, body.interactor_id)
    except revisions.RevisionError as exc:
        raise HTTPException(422, i18n.raised(exc)) from None


@router.get("/profiles/{profile_id}/thread/{interactor_id}")
def thread(profile_id: str, interactor_id: str, request: Request) -> dict:
    """The conversation with edits visible — including which replies were
    written before the message above them was changed."""
    profile_or_404(profile_id)
    require_owner_or_interactor(profile_id, interactor_id, request)
    return {"profile_id": profile_id, "interactor_id": interactor_id,
            "thread_turns": revisions.thread(profile_id, interactor_id)}
