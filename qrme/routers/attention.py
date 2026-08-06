"""How a profile's attention is divided — the number, offered.

Public, deliberately. The count of people a synthetic profile talks to is a
fact about the profile, not a secret earned by intimacy. Making somebody get
close before they are allowed to learn it turns an ordinary property of the
software into a betrayal, and the only thing that produced the betrayal was
the withholding.
"""

from __future__ import annotations

from fastapi import APIRouter

from .. import attention

router = APIRouter()


@router.get("/profiles/{profile_id}/attention")
def divided(profile_id: str, interactor: str | None = None) -> dict:
    """Counts, never names.

    ``interactor`` is optional and answers one extra question — *am I one of
    them* — which somebody can only ask about themselves.
    """
    return attention.divided(profile_id, viewer_interactor_id=interactor)
