"""Model selection: let an owner pick which LLM powers their profile.

Profiles default to the platform's provider (Claude, unless the deployment sets
otherwise), but an owner is not locked in — they can route their profile's
generation through ChatGPT (OpenAI), Grok (xAI), Perplexity, or Gemini, or pin
the deterministic offline stub. The choice is stored per profile and honored on
every chat, compose, and proactive turn.

The provider name is configuration, not personal data, so it lives in the local
``model_prefs`` table rather than the PDI vault. The *change* is still made
auditable: it is written to the structured log and surfaced in the profile's
transparency view via ``GET /profiles/{id}/model``.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from .. import llm
from ..common import profile_or_404, require_owner

router = APIRouter()
logger = logging.getLogger("qrme.models")


class ModelChoice(BaseModel):
    #: A qrme.llm registry name (anthropic | openai | grok | perplexity |
    #: gemini | stub) or "auto" to defer to the platform default.
    provider: str


@router.get("/models")
def list_models() -> dict:
    """Every provider the platform knows about, with whether it is configured
    in this deployment (has credentials) so a UI can enable/disable choices."""
    return {"providers": llm.available(), "default": llm.default_name()}


@router.get("/profiles/{profile_id}/model")
def get_profile_model(profile_id: str) -> dict:
    """The profile's stored preference and the provider it actually resolves to
    right now (they differ when a chosen provider is not configured here)."""
    profile_or_404(profile_id)
    choice = llm.get_choice(profile_id)
    return {
        "profile_id": profile_id,
        "provider": choice,
        "effective": llm.resolve_choice(choice),
    }


@router.put("/profiles/{profile_id}/model")
def set_profile_model(profile_id: str, body: ModelChoice, request: Request) -> dict:
    """Owner-only. Set which provider powers this profile."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    if body.provider not in llm.CHOICES:
        raise HTTPException(
            422, f"provider must be one of {', '.join(llm.CHOICES)}")
    try:
        llm.set_choice(profile_id, body.provider)
    except ValueError as exc:  # defensive: CHOICES already validated above
        raise HTTPException(422, str(exc)) from exc
    effective = llm.resolve_choice(body.provider)
    logger.info("owner set profile %s model provider=%s (effective=%s)",
                profile_id, body.provider, effective)
    return {
        "profile_id": profile_id,
        "provider": body.provider,
        "effective": effective,
    }
