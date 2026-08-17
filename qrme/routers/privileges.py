"""What the agent may do — endpoints.

Two readers, deliberately, and the difference is the whole point of the round.

**The owner** reads the roster to decide, and is the only one who can change
it. **A visitor** reads the same roster to find out what this profile can
actually do for them — which until now was discoverable only mid-conversation,
when a profile happened to offer it. A person who wants to know whether this
one can hand their matter to a real professional should be able to look.

Nothing here decides anything. The refusal lives at each power's own last hop
(see :func:`qrme.privileges.require`), because a check in a route is a check
the second caller walks past.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from .. import i18n, privileges
from ..common import profile_or_404, require_owner
from ..models import PrivilegeChoice

router = APIRouter()


@router.get("/profiles/{profile_id}/privileges")
def whats_allowed(profile_id: str, request: Request) -> list[dict]:
    """The whole roster, off rows included, in the reader's language.

    Open to anyone who can see the profile. What an agent is permitted to do
    on somebody's behalf is not a secret kept from the person it would be done
    to — and the ones that are *off* are the half that makes the list mean
    anything.
    """
    profile_or_404(profile_id)
    return i18n.localize_public(privileges.roster(profile_id),
                                i18n.refusal_language(request))


@router.post("/profiles/{profile_id}/privileges/{name}")
def choose(profile_id: str, name: str, body: PrivilegeChoice,
           request: Request) -> list[dict]:
    """Say yes or no to one, and get the whole roster back.

    The whole roster rather than the row: a client that re-reads one row shows
    a screen that agrees with itself about that row and nothing else.
    """
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        chosen = privileges.choose(profile_id, name, body.on)
    except privileges.NotChosen as exc:
        raise HTTPException(422, i18n.raised(exc)) from None
    return i18n.localize_public(chosen, i18n.refusal_language(request))
