"""Steering: the owner shapes a profile's / robot's presentation.

The same dials for a synthetic profile persona and for a robot body it
embodies. Intimacy is an 18+-only dial, available and effective only on an
adult-mode profile. Owner-set, and it is steering, not piloting — it shapes
how the entity comes across (tone, voice, pace, manner); the entity still
acts on its own within its embodiments. Steering shapes style/pace/behavior
and never touches identity, boundaries, age-gating, or the command allowlist.
"""

from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from .. import db, persona, steering
from ..common import profile_or_404, require_owner

router = APIRouter()


class SteeringSet(BaseModel):
    values: dict[str, int] = Field(default_factory=dict)


class SteeringAge(BaseModel):
    base_age: int | None = None
    aging_enabled: bool | None = None


class SteeringAppearance(BaseModel):
    description: str | None = None
    demographics: dict | None = None


class SteeringHub(BaseModel):
    """One surface for everything the owner steers: the dials, the age, and
    the appearance. Every section is optional — only what's present is set."""
    values: dict[str, int] | None = None
    age: SteeringAge | None = None
    appearance: SteeringAppearance | None = None


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


def _age_block(profile: dict) -> dict:
    return {"base_age": profile["base_age"],
            "aging_enabled": bool(profile["aging_enabled"]),
            "effective_age": persona.effective_age(dict(profile))}


@router.get("/profiles/{profile_id}/steering/hub")
def get_steering_hub(profile_id: str, request: Request) -> dict:
    """The unified steering hub: the tone/pace/manner dials, the profile's
    age, and its appearance — everything the owner shapes, in one place.
    The dedicated features (Avatar Studio, Aging, personality) still stand
    on their own; this composes them."""
    profile = profile_or_404(profile_id)
    require_owner(profile_id, request)
    adult = bool(profile["adult_mode"])
    return {
        "subject_id": profile_id, "adult_mode": adult,
        "dials": steering.spec(adult), "values": steering.get(profile_id),
        "age": _age_block(profile),
        "appearance": {
            "description": profile["appearance"],
            "demographics": json.loads(profile["demographics"]),
        },
    }


@router.put("/profiles/{profile_id}/steering/hub")
def set_steering_hub(profile_id: str, body: SteeringHub,
                     request: Request) -> dict:
    """Set any of the hub's sections. Dials go through the same clamps/gates
    (intimacy stays 18+-only); age and appearance update the profile and
    ride on the persona prompt from the next turn on."""
    profile = profile_or_404(profile_id)
    require_owner(profile_id, request)
    adult = bool(profile["adult_mode"])
    conn = db.connect()

    if body.values is not None:
        steering.set_dials(profile_id, body.values, adult)

    if body.age is not None:
        sets, params = [], []
        if body.age.base_age is not None:
            if body.age.base_age < 0:
                raise HTTPException(422, "base_age cannot be negative")
            sets.append("base_age=?"); params.append(body.age.base_age)
        if body.age.aging_enabled is not None:
            sets.append("aging_enabled=?")
            params.append(int(body.age.aging_enabled))
        if sets:
            conn.execute(f"UPDATE profiles SET {', '.join(sets)} WHERE id=?",
                         (*params, profile_id))

    if body.appearance is not None:
        if body.appearance.description is not None:
            conn.execute("UPDATE profiles SET appearance=? WHERE id=?",
                         (body.appearance.description, profile_id))
        if body.appearance.demographics is not None:
            conn.execute("UPDATE profiles SET demographics=? WHERE id=?",
                         (json.dumps(body.appearance.demographics), profile_id))
    conn.commit()
    return get_steering_hub(profile_id, request)


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
