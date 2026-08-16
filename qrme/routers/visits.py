"""Where the agent keeps going back to — endpoints.

Two readers, and the split between them is the point rather than a detail.

The **owner** reads the far hosts their own profiles reached, and can stand
one down. Scoped by ``require_owner``, like everything else that is theirs.

The **operator** reads the deployment's totals: which far hosts this address
has been seen leaving for, and how often. That is the view that shows real
correlation exposure — one IP, several households, one far end watching all of
it — and it is precisely the view that would otherwise tell one owner what
another owner's agent reads. So it carries hosts and counts and no profile at
any depth, and it sits behind the same gate the failure aggregate uses.

See ``qrme/visits.py`` for what is recorded and what deliberately is not.
"""

from __future__ import annotations

import os
import secrets

from fastapi import APIRouter, HTTPException, Request

from .. import visits
from ..common import profile_or_404, require_owner
from ..models import StandDown

router = APIRouter()

#: TestClient calls arrive as "testclient"; a developer's own machine as
#: loopback. Both are the operator, not the public. Same list the failure
#: aggregate keeps, for the same reason.
_LOCAL = {"127.0.0.1", "::1", "localhost", "testclient"}


def _require_reader(request: Request) -> None:
    """The deployment-wide view is the operator's.

    Deliberately the same key as the failure map rather than a second one: an
    operator holding two keys for two aggregates is an operator who will set
    one of them.
    """
    key = os.environ.get("QRME_PROBLEMS_KEY", "")
    if key:
        presented = (request.headers.get("authorization") or "")
        if not presented.startswith("Bearer "):
            raise HTTPException(401, "reading where this deployment has been "
                                     "requires the QRME_PROBLEMS_KEY bearer "
                                     "token")
        if not secrets.compare_digest(presented[len("Bearer "):], key):
            raise HTTPException(403, "wrong problems key")
        return
    host = request.client.host if request.client else ""
    if host not in _LOCAL:
        raise HTTPException(
            403, "where this deployment has been is readable from this "
                 "machine only until QRME_PROBLEMS_KEY is set — behind a "
                 "proxy, set it")


@router.get("/profiles/{profile_id}/visits")
def profile_visits(profile_id: str, request: Request) -> list[dict]:
    """Every far host this profile's agent has reached, most-visited first.

    One row per host, not per visit: the count is the answer, and a list of
    individual times would be the movement log this feature exists to warn
    about. ``persistent`` is the sentence worth reading — not *you visited
    this*, but *this one has seen you enough times to know you*.
    """
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    return visits.for_profile(profile_id)


@router.post("/profiles/{profile_id}/visits/stand-down", status_code=201)
def stand_down(profile_id: str, body: StandDown, request: Request) -> dict:
    """Stop visiting a host.

    Enforced where the socket opens, not here — a refusal that lived in this
    route would be one every other caller of the fetcher walks straight past.
    """
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    host = visits.host_of(body.host) or body.host.strip().lower()
    if not host:
        raise HTTPException(400, "name the host to stop visiting")
    return visits.stand_down(profile_id, host)


@router.post("/profiles/{profile_id}/visits/lift")
def lift(profile_id: str, body: StandDown, request: Request) -> dict:
    """Start visiting it again. What was recorded stays recorded — lifting a
    stand-down is not unremembering the visits that led to it."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    host = visits.host_of(body.host) or body.host.strip().lower()
    if not host:
        raise HTTPException(400, "name the host to visit again")
    return visits.lift(profile_id, host)


@router.get("/visits/across")
def across(request: Request) -> list[dict]:
    """What this address looks like from outside, in aggregate.

    Hosts and counts. **No profile appears here at any depth** — a tool built
    to measure correlation must not be a way to correlate people, and one
    owner learning which forum another owner's agent reads would be exactly
    that.
    """
    _require_reader(request)
    return visits.across_the_deployment()
