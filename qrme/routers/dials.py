"""Dials: a profile's / robot's disposition — throttle + behavior sliders.

The same dials for a synthetic profile persona and for a robot body it
embodies. Intimacy is an 18+-only dial, available and effective only on an
adult-mode profile. Owner-set, but not a remote control — they describe the
entity's temperament; the entity acts on its own within its embodiments.
The dials shape style/pace/behavior and never touch identity, boundaries,
age-gating, or the command allowlist.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from .. import db, dials
from ..common import profile_or_404, require_owner

router = APIRouter()


class DialsSet(BaseModel):
    values: dict[str, int] = Field(default_factory=dict)


@router.get("/profiles/{profile_id}/dials")
def get_profile_dials(profile_id: str, request: Request) -> dict:
    """The dial catalog + current values for a profile. The intimacy dial
    appears only on an adult-mode profile."""
    profile = profile_or_404(profile_id)
    require_owner(profile_id, request)
    adult = bool(profile["adult_mode"])
    return {"subject": "profile", "subject_id": profile_id,
            "dials": dials.spec(adult), "values": dials.get(profile_id),
            "adult_mode": adult}


@router.put("/profiles/{profile_id}/dials")
def set_profile_dials(profile_id: str, body: DialsSet,
                      request: Request) -> dict:
    """Set a profile's dials. Intimacy is hard-clamped to 0 unless the
    profile is adult-mode — it can never be raised on a non-rated persona."""
    profile = profile_or_404(profile_id)
    require_owner(profile_id, request)
    adult = bool(profile["adult_mode"])
    values = dials.set_dials(profile_id, body.values, adult)
    return {"subject": "profile", "subject_id": profile_id,
            "values": values, "adult_mode": adult}


def _robot_owned(robot_id: str, request: Request) -> dict:
    row = db.connect().execute("SELECT * FROM robots WHERE id=?",
                               (robot_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "robot not found")
    require_owner(row["profile_id"], request)
    return dict(row)


@router.get("/robots/{robot_id}/dials")
def get_robot_dials(robot_id: str, request: Request) -> dict:
    """A robot body's dials. Intimacy never applies to a body — a robot is
    dialed on pace, autonomy, and behavior only."""
    _robot_owned(robot_id, request)
    body_dials = [d for d in dials.spec(adult=False)
                  if d["group"] != "intimacy"]
    return {"subject": "robot", "subject_id": robot_id, "dials": body_dials,
            "values": dials.get(robot_id),
            "behavior_profile": dials.robot_profile(robot_id)}


@router.put("/robots/{robot_id}/dials")
def set_robot_dials(robot_id: str, body: DialsSet, request: Request) -> dict:
    """Set a robot's dials (intimacy is not a body dial and is ignored)."""
    _robot_owned(robot_id, request)
    values = body.values.copy()
    values.pop("intimacy", None)
    dials.set_dials(robot_id, values, adult=False)
    return {"subject": "robot", "subject_id": robot_id,
            "values": dials.get(robot_id),
            "behavior_profile": dials.robot_profile(robot_id)}
