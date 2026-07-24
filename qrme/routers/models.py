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

from .. import i18n, llm
from ..common import profile_or_404, require_owner

router = APIRouter()
logger = logging.getLogger("qrme.models")


class ModelChoice(BaseModel):
    #: A qrme.llm registry name (anthropic | openai | grok | perplexity |
    #: gemini | stub) or "auto" to defer to the platform default.
    provider: str


class LanguageChoice(BaseModel):
    #: A qrme.i18n.SUPPORTED code, e.g. "es".
    language: str
    #: "pre" (persona speaks it natively, default) | "on_demand".
    mode: str = "pre"


class TranslateRequest(BaseModel):
    text: str                          # anything the owner ran across
    to: str | None = None              # target; None -> profile's language


@router.get("/languages")
def list_languages() -> dict:
    """Languages a profile can speak. The persona generates natively in the
    chosen language on every surface — chat, posts, rooms, robot speech."""
    return {"languages": [{"code": c, "label": l}
                          for c, l in i18n.SUPPORTED.items()],
            "default": i18n.DEFAULT}


@router.get("/profiles/{profile_id}/language")
def get_profile_language(profile_id: str) -> dict:
    profile_or_404(profile_id)
    code, mode = i18n.get_pref(profile_id)
    return {"profile_id": profile_id, "language": code,
            "label": i18n.SUPPORTED[code], "mode": mode}


@router.put("/profiles/{profile_id}/language")
def set_profile_language(profile_id: str, body: LanguageChoice,
                         request: Request) -> dict:
    """Owner-only. The profile speaks this language everywhere it appears."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    if body.language not in i18n.SUPPORTED:
        raise HTTPException(
            422, f"language must be one of {', '.join(i18n.SUPPORTED)}")
    if body.mode not in i18n.MODES:
        raise HTTPException(
            422, f"mode must be one of {', '.join(i18n.MODES)}")
    i18n.set_language(profile_id, body.language, body.mode)
    logger.info("owner set profile %s language=%s mode=%s",
                profile_id, body.language, body.mode)
    return {"profile_id": profile_id, "language": body.language,
            "label": i18n.SUPPORTED[body.language], "mode": body.mode}


@router.post("/profiles/{profile_id}/translate")
def translate_text(profile_id: str, body: TranslateRequest,
                   request: Request) -> dict:
    """Owner-only. Translate anything run across — an interactor's message,
    a room turn, a listing — into the profile's language (or an explicit
    target), using the profile's own model. The offline stub says it cannot
    translate rather than pretending."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        return i18n.translate(profile_id, body.text, body.to,
                              cloud=request.app.state.cloud)
    except ValueError as exc:
        raise HTTPException(422, str(exc))


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
