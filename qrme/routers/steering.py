"""Steering: the owner shapes a profile's / robot's presentation.

The same dials for a synthetic profile persona and for a robot body it
embodies. Intimacy is an 18+-only dial, available and effective only on an
adult-mode profile. Owner-set, and it is steering, not piloting — it shapes
how the entity comes across (tone, voice, pace, manner); the entity still
acts on its own within its embodiments. Steering shapes style/pace/behavior
and never touches identity, boundaries, age-gating, or the command allowlist.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from .. import db, steering
from ..common import profile_or_404, require_owner

router = APIRouter()


class SteeringSet(BaseModel):
    values: dict[str, int] = Field(default_factory=dict)


@router.get("/profiles/{profile_id}/steering")
def get_profile_steering(profile_id: str, request: Request) -> dict:
    """The dial catalog + current values for a profile. The intimacy dial
    appears only on an adult-mode profile."""
    profile = profile_or_404(profile_id)
    require_owner(profile_id, request)
    adult = bool(profile["adult_mode"])
    return {"subject": "profile", "subject_id": profile_id,
            "dials": steering.spec(adult), "values": steering.get(profile_id),
            "adult_mode": adult}


@router.put("/profiles/{profile_id}/steering")
def set_profile_steering(profile_id: str, body: SteeringSet,
                         request: Request) -> dict:
    """Steer a profile. Intimacy is hard-clamped to 0 unless the profile is
    adult-mode — it can never be raised on a non-rated persona."""
    profile = profile_or_404(profile_id)
    require_owner(profile_id, request)
    adult = bool(profile["adult_mode"])
    values = steering.set_dials(profile_id, body.values, adult)
    return {"subject": "profile", "subject_id": profile_id,
            "values": values, "adult_mode": adult}


def _robot_owned(robot_id: str, request: Request) -> dict:
    row = db.connect().execute("SELECT * FROM robots WHERE id=?",
                               (robot_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "robot not found")
    require_owner(row["profile_id"], request)
    return dict(row)


@router.get("/robots/{robot_id}/steering")
def get_robot_steering(robot_id: str, request: Request) -> dict:
    """A robot body's dials. Intimacy never applies to a body — a robot is
    steered on pace, autonomy, and behavior only."""
    _robot_owned(robot_id, request)
    body_dials = [d for d in steering.spec(adult=False)
                  if d["group"] != "intimacy"]
    return {"subject": "robot", "subject_id": robot_id, "dials": body_dials,
            "values": steering.get(robot_id),
            "behavior_profile": steering.robot_profile(robot_id)}


@router.put("/robots/{robot_id}/steering")
def set_robot_steering(robot_id: str, body: SteeringSet,
                       request: Request) -> dict:
    """Steer a robot (intimacy is not a body dial and is ignored)."""
    _robot_owned(robot_id, request)
    values = body.values.copy()
    values.pop("intimacy", None)
    steering.set_dials(robot_id, values, adult=False)
    return {"subject": "robot", "subject_id": robot_id,
            "values": steering.get(robot_id),
            "behavior_profile": steering.robot_profile(robot_id)}
