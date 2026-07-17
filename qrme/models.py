"""Pydantic request/response schemas."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

ProfileKind = Literal["self", "other_person", "fictional"]
InteractionScope = Literal["reactive", "proactive"]
ModerationMode = Literal["auto", "manual"]
RelationshipType = Literal[
    "family", "grandchild", "friend", "romantic_partner",
    "professional", "fan", "stranger",
]


class Verification(BaseModel):
    """Age/identity verification captured at profile creation (PRD 6.1)."""

    birthdate: date
    guardian_consent: bool = False


class Consent(BaseModel):
    """Rights basis for representing a real third party (PRD 9)."""

    basis: Literal["subject_consent", "estate_authorization", "public_figure_commentary"]
    attestor: str


class ProfileCreate(BaseModel):
    owner_id: str
    kind: ProfileKind
    display_name: str
    persona: str = Field(description="Core identity: voice, history, values.")
    demographics: dict = Field(default_factory=dict)
    sources: list[str] = Field(default_factory=list)
    verification: Verification
    consent: Consent | None = None
    anonymous: bool = False
    adult_mode: bool = False
    interaction_scope: InteractionScope = "reactive"
    moderation_mode: ModerationMode = "auto"
    aging_enabled: bool = False
    base_age: int | None = None
    successor_owner: str | None = None


class ProfileOut(BaseModel):
    id: str
    owner_id: str
    kind: ProfileKind
    display_name: str
    persona: str
    demographics: dict
    sources: list[str]
    anonymous: bool
    adult_mode: bool
    interaction_scope: InteractionScope
    moderation_mode: ModerationMode
    aging_enabled: bool
    base_age: int | None
    effective_age: int | None
    successor_owner: str | None
    created_at: str


class InteractorCreate(BaseModel):
    display_name: str
    birthdate: date | None = None


class RelationshipSet(BaseModel):
    relationship_type: RelationshipType = "stranger"
    nickname: str | None = None
    tone: str | None = None
    boundaries: list[str] = Field(default_factory=list)


class ChatRequest(BaseModel):
    interactor_id: str
    message: str


class MessageOut(BaseModel):
    id: str
    role: Literal["interactor", "profile"]
    content: str | None
    status: Literal["approved", "pending", "rejected"]
    flag_reason: str | None = None
    created_at: str


class ChatResponse(BaseModel):
    interactor_message: MessageOut
    profile_message: MessageOut


class Feedback(BaseModel):
    rating: Literal["up", "down"]


class EngagementOut(BaseModel):
    profile_id: str
    interactor_id: str
    score: float
    interactions: int
    sessions: int
    feedback_pos: int
    feedback_neg: int


# -- JIM-mini / Guardian ----------------------------------------------------

Condition = Literal[
    "anxiety", "depression", "financial_stress", "relationship", "physical_distress"
]


class GuardianEnroll(BaseModel):
    terms_consent: bool
    guardian_consent: bool = False
    emergency_name: str | None = None
    emergency_phone: str | None = None
    contact_consent: bool = False
    device_paired: bool = False
    resting_heart_rate: int | None = None
    goals: str | None = None


class SpecialistRegister(BaseModel):
    condition: Condition
    profile_id: str


class BiometricSample(BaseModel):
    heart_rate: int | None = None
    resting_heart_rate: int | None = None
    respiratory_rate: int | None = None
    blood_oxygen: float | None = None
    note: str | None = None
