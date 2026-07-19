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
Purpose = Literal[
    "legacy_memorial", "family", "creator_persona",
    "social_fan", "companion_coach", "enterprise_agent",
]
Maturity = Literal["strict", "balanced", "open"]
SourceKind = Literal[
    "photo", "conversation", "social_post", "writing",
    "voice_note", "life_event", "knowledge", "linked_account",
]
Modality = Literal["text", "voice", "image", "video"]


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
    purpose: Purpose | None = None
    maturity: Maturity = "balanced"
    # Opt-in: contribute positively-rated, anonymized exchanges to improve
    # the shared cloud model. Off by default; revocable anytime.
    cloud_contribution: bool = False


class ProfileUpdate(BaseModel):
    """Owner control: edit the profile anytime."""

    display_name: str | None = None
    persona: str | None = None
    moderation_mode: ModerationMode | None = None
    interaction_scope: InteractionScope | None = None
    purpose: Purpose | None = None
    maturity: Maturity | None = None
    aging_enabled: bool | None = None
    successor_owner: str | None = None
    cloud_contribution: bool | None = None


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
    purpose: Purpose | None
    maturity: Maturity
    cloud_contribution: bool
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
    modality: Modality = "text"        # requested output modality
    surface: str | None = None         # which registered surface this is from
    # Real-time biometric monitoring context (claim 23): e.g. stress_level
    # (0..1), heart_rate, condition — typically supplied by JIM-mini.
    biometrics: dict | None = None


class SpecialistSet(BaseModel):
    domain: str                        # mental_health | medical | finance | …
    specialist_profile_id: str


class GenesisAnswers(BaseModel):
    """The short interview a profile is born from."""

    social_style: str                  # e.g. "warm but needs quiet evenings"
    humor: str                         # e.g. "dry, gentle teasing"
    what_matters: str                  # e.g. "family, honesty, the garden"
    comfort: str                       # how they comfort someone


class GenesisCreate(BaseModel):
    owner_id: str
    verification: Verification
    answers: GenesisAnswers
    display_name: str | None = None    # omit to let the profile name itself
    kind: ProfileKind = "fictional"
    purpose: Purpose | None = "companion_coach"
    interaction_scope: InteractionScope = "reactive"
    maturity: Maturity = "balanced"


class ConnectionJoin(BaseModel):
    interactor_id: str
    tier: Literal["friendly", "rated"] = "friendly"
    alias: str | None = None           # anonymous handle shown to the match


class ConnectionMessage(BaseModel):
    interactor_id: str
    message: str


Channel = Literal["chat", "voice", "video", "ar", "vr"]


class RoomParticipant(BaseModel):
    kind: Literal["user", "profile"]
    id: str


class RoomCreate(BaseModel):
    topic: str
    channel: Channel = "chat"
    participants: list[RoomParticipant] = Field(min_length=2, max_length=8)


class RoomMessage(BaseModel):
    sender_id: str                     # must be a user participant
    message: str


class ListingCreate(BaseModel):
    kind: Literal["profile", "content", "expertise", "service"]
    title: str
    blurb: str | None = None
    tags: list[str] = Field(default_factory=list)
    area: str | None = None            # healthcare | finance | relationships | …
    provider_name: str
    business: bool = False
    profile_id: str | None = None      # required when kind == "profile"


class ProviderCreate(BaseModel):
    name: str
    area: str                          # healthcare | medical | mental_health |
                                       # finance | relationships | career | …
    location: str | None = None
    contact: str | None = None
    business: bool = True


class HandoffCreate(BaseModel):
    interactor_id: str
    provider_id: str
    profile_id: str | None = None      # the AI specialist session to package
    consent: bool = False              # explicit user consent required


class HandleSet(BaseModel):
    handle: str = Field(pattern=r"^@?[A-Za-z0-9_]{2,30}$",
                        description="Unique @handle; stored lowercase.")


class BeaconCreate(BaseModel):
    label: str                         # e.g. "Rosa's garden bench"
    location: str | None = None        # free-text place description


class EmbodimentAdd(BaseModel):
    name: str                          # e.g. kitchen_speaker, companion_bot
    kind: Literal["speaker", "earpiece", "hologram", "robot",
                  "humanoid", "other"]
    has_llm: bool = False


class MarketplaceList(BaseModel):
    tags: list[str] = Field(default_factory=list)
    blurb: str | None = None


class GrantCreate(BaseModel):
    scope: list[str] | None = None     # source-item ids; None = all sources


class TaskRun(BaseModel):
    kind: str = "compose_from_sources"
    topic: str
    grant_token: str


class SourceAdd(BaseModel):
    kind: SourceKind
    title: str | None = None
    content: str | None = None         # text body / transcript / description


class SurfacesSet(BaseModel):
    surfaces: list[str] = Field(default_factory=list)


class ComposeRequest(BaseModel):
    topic: str
    surface: str | None = None


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
    # Multi-modal output descriptor: how the reply renders beyond text
    # (voice basis, image/video treatment). None for plain text.
    modality: dict | None = None
    # Set when biometric signals routed the reply to a domain specialist
    # (claim 24): {domain, specialist_profile_id, reason}.
    handoff: dict | None = None


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
