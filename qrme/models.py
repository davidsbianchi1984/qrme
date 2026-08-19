"""Pydantic request/response schemas."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ProfileKind = Literal["self", "other_person", "fictional", "hybrid"]
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
    # Clickwrap: first-party apps display the Terms (GET /terms) and send an
    # explicit acceptance; the accepted version + timestamp are recorded on
    # the profile. An explicit refusal is refused.
    terms_consent: bool = True
    owner_id: str
    # The plan this account joins on. Omitted means Basic for a new account,
    # and *no change* for an existing member — making a second profile must not
    # quietly move somebody off Pro. See qrme/routers/profiles.py:_enrol.
    plan: str | None = None
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
    language: str | None = None        # chosen at the setup gateway


class CardImport(BaseModel):
    """A character card as a profile seed (qrme/cardimport.py): the card
    as raw JSON in ``card``, or a PNG with one embedded as base64 in
    ``content`` — the same name every upload door uses."""
    terms_consent: bool = True
    owner_id: str
    plan: str | None = None
    verification: Verification
    card: dict | None = None
    content: str | None = None
    language: str | None = None


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
    proactive_min_interval_hours: int | None = None   # anti-spam rate cap


class ProfileOut(BaseModel):
    id: str
    # Null to anyone but the owner. It is an account identifier, and on this
    # platform an account may hold several profiles — so publishing it lets a
    # reader match two anonymous profiles to each other, and match both to the
    # named one beside them. No visitor needs it; see `common.profile_out`.
    owner_id: str | None
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
    status: str                        # active | restricted | departed | terminated
    licensed_from: str | None = None   # source profile if a licensed derivative
    created_at: str


class InteractorCreate(BaseModel):
    display_name: str
    birthdate: date | None = None


class MemoryForget(BaseModel):
    # The words to strike: turns containing them are deleted and the
    # distilled remembrance is re-folded from what remains.
    about: str


class MemoryStrike(BaseModel):
    # The turns to strike, chosen by id in the transcript. Deleted
    # together, and the remembrance re-folds from what remains.
    message_ids: list[str]


class TurnEdit(BaseModel):
    # What the remembered turn should say instead.
    content: str


class QuietHoursSet(BaseModel):
    # UTC-hour window [start, end) during which no unprompted outreach is sent;
    # both None clears it. A window may wrap midnight (start > end).
    quiet_start: int | None = Field(default=None, ge=0, le=23)
    quiet_end: int | None = Field(default=None, ge=0, le=23)


class RelationshipSet(BaseModel):
    relationship_type: RelationshipType = "stranger"
    nickname: str | None = None
    tone: str | None = None
    boundaries: list[str] = Field(default_factory=list)


class RehearsalOpen(BaseModel):
    """A practice room: the hard conversation, with nothing remembered."""
    interactor_id: str
    scenario: str


class RehearsalSay(BaseModel):
    message: str


class ChatRequest(BaseModel):
    interactor_id: str
    message: str
    modality: Modality = "text"        # requested output modality
    surface: str | None = None         # which registered surface this is from
    # Real-time biometric monitoring context (claim 23): e.g. stress_level
    # (0..1), heart_rate, condition — typically supplied by JIM-mini.
    biometrics: dict | None = None
    # Environmental context (spec clause 1): where the person is and what's
    # around them — location, conditions, local_time, activity. The reply
    # adapts to it; the raw payload is stored beside the biometric context.
    environment: dict | None = None
    # Role-specific context (spec clauses 2/12): how the profile should
    # function this turn — an advisor counsels, a collaborator co-creates,
    # an operator executes. Unset = the profile reads the prompt itself
    # (transparent keyword inference), or simply stays itself.
    role: Literal["advisor", "collaborator", "operator"] | None = None


class VoiceConsent(BaseModel):
    """FIG. 800 step 802 — the permission, before any collection.

    ``own_voice`` is an attestation: QRME will not learn a voice on somebody
    else's behalf, so without it enrollment is refused (qrme/voiceprint.py).
    """

    own_voice: bool
    sources: list[Literal["call", "voice_note", "direct"]] | None = None
    note: str | None = None


class VoiceSample(BaseModel):
    """Steps 806-808 — a gathered sample, as metadata. The audio itself lives
    wherever the deployment's media policy puts it (``reference``)."""

    source: Literal["call", "voice_note", "direct"] = "voice_note"
    seconds: float
    turns: int = 1
    transcript_chars: int = 0
    reference: str | None = None


class VoiceBind(BaseModel):
    provider: str = "elevenlabs"       # see qrme.spoken.PROVIDERS
    voice_id: str = ""                 # empty unbinds
    label: str = ""


class VoiceSay(BaseModel):
    text: str


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
    # The plan this account joins on. Omitted means Basic for a new account,
    # and *no change* for an existing member — making a second profile must not
    # quietly move somebody off Pro. See qrme/routers/profiles.py:_enrol.
    plan: str | None = None
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


class RoomInvite(BaseModel):
    """Who is being asked into a room, or who is answering.

    One model for both doors on purpose: the invite names the guest and the
    acceptance names the same guest, so a client that can build one can build
    the other. The *authority* differs — the host holds a room seat, the guest
    holds their own owner token — and that is checked at each route rather
    than expressed as two shapes on the wire.
    """

    profile_id: str


class RoomFace(BaseModel):
    """What your box in the room scene holds.

    `media_id` and `media_url` are optional on every call: the upload route
    sets them, and a later switch between `camera` and `voice` leaves the
    picture where it was. Sending neither means "keep whatever is there",
    which is what somebody toggling a camera expects to happen.
    """

    interactor_id: str
    showing: Literal["voice", "photo", "camera"]
    media_id: str | None = None
    media_url: str | None = None


class RoomCreate(BaseModel):
    # Optional, and the only reader that ever thought otherwise was this
    # line. `create_room` writes it straight through, the rooms list declares
    # `topic?: string | null`, and the console has always sent nothing when
    # the field is left blank — so leaving the topic empty answered 422
    # "Topic — Field required" on a form that offers it as a blank you may
    # skip. A room opened *with a person* is named by who is in it.
    #
    #     asked     may a room be opened without a topic
    #     mattered  does the button that offers to do it work
    topic: str | None = None
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


class RoomMicLend(BaseModel):
    """Lend a room's profiles your wearable microphone (see qrme/roommic.py).
    Everyone in the room is shown that you did."""
    interactor_id: str
    device: str = "smart_watch"
    # Both vocabularies, because a device may be named the way the pairing
    # registry named it (`lapel_mic`) or the way this module and jim/mic.py do
    # (`lapel`). `roommic.FROM_WEARABLE` translates; the schema accepts either
    # so a client holding a paired device can send what it already has.
    #
    # The room-facing kinds are listed and then refused by the module rather
    # than rejected by the schema, because a 422 from a Literal says "not a
    # valid value" and the true answer is "that microphone would pick up the
    # other people in the room". The reason is the feature.
    mic_type: Literal["watch", "earbuds", "headset", "lapel", "clip_on",
                      "bone_conduction", "glasses", "collar_tag", "handheld",
                      "lapel_mic", "clip_on_mic",
                      "speakerphone", "conference", "console", "laptop",
                      "room_array", "doorbell",
                      "smart_speaker", "conference_puck", "tabletop_mic",
                      "desk_mic"] = "watch"
    # The lender's own gain setting. Accepted so one client can send it to
    # either product, but a room grant always runs near-field — a room has
    # other people in it, and a channel wide enough to hear them is a channel
    # lending their voices. See qrme/roommic.py:ROOM_GAIN.
    gain: Literal["near_field", "normal", "wide"] = "near_field"


class ReferralPrepare(BaseModel):
    """Build a medical referral package and raise the signature that would
    authorise releasing it. Nothing leaves until the assertion verifies."""
    interactor_id: str
    profile_id: str                    # the AI specialist session to package
    provider_id: str


class ReferralRelease(BaseModel):
    # The verified signature raised for *this* referral. Deliberately not a
    # consent boolean: see qrme/referral.py.
    signature_id: str


class ReferralReply(BaseModel):
    """The clinician's note back — what brings the profile up to speed so the
    patient does not have to retell it."""
    content: str


class TriageItem(BaseModel):
    id: str
    text: str


class TriageRequest(BaseModel):
    items: list[TriageItem] = Field(min_length=1)
    keep: int = Field(ge=1)            # how many of the best to keep
    criteria: str | None = None        # what "best" means to the user


class ProofreadRequest(BaseModel):
    text: str


class PerceiveRequest(BaseModel):
    objects: list[str] = Field(default_factory=list)
    people: list[str] = Field(default_factory=list)
    gestures: list[str] = Field(default_factory=list)
    place: str | None = None
    goal: str | None = None            # e.g. "guide me to the exit"


class ComposeCreative(BaseModel):
    kind: Literal["music", "poem", "note", "lyric"] = "note"
    moment: str                        # the moment to capture


class HandleSet(BaseModel):
    handle: str = Field(pattern=r"^@?[A-Za-z0-9_]{2,30}$",
                        description="Unique @handle; stored lowercase.")


class BeaconCreate(BaseModel):
    label: str                         # e.g. "Rosa's garden bench"
    location: str | None = None        # free-text place description
    # "chat" (default): each scan opens that person's own conversation.
    # "room": every scan joins one shared room, so the people who found the
    # same sticker are talking to the profile together — a workshop, a
    # meeting, a class. Left running until the beacon is picked up.
    mode: Literal["chat", "room"] = "chat"
    topic: str | None = None           # room mode: what the gathering is about


class EmbodimentAdd(BaseModel):
    name: str                          # e.g. kitchen_speaker, companion_bot
    kind: Literal["speaker", "earpiece", "hologram", "robot",
                  "humanoid", "other"]
    has_llm: bool = False


class MarketplaceList(BaseModel):
    tags: list[str] = Field(default_factory=list)
    blurb: str | None = None


class CompositeSource(BaseModel):
    """One constituent of a hybrid profile (spec [0038])."""

    profile_id: str
    weight: float = Field(default=1.0, gt=0)   # relative; normalized on create
    aspect: str | None = None          # e.g. "leadership", "storytelling"


class CompositeCreate(BaseModel):
    """A hybrid profile: 'a combination of aspects or characteristics of
    several people, such as a combination of several past presidents or
    business leaders, a combination of trusted relatives such as grandparents
    who are gone' (spec [0038])."""

    terms_consent: bool = True
    owner_id: str
    plan: str | None = None
    display_name: str
    sources: list[CompositeSource] = Field(min_length=2)
    verification: Verification
    anonymous: bool = False
    purpose: Purpose | None = None
    maturity: Maturity = "balanced"
    language: str | None = None


class SimulationRun(BaseModel):
    """Ask a profile to simulate the represented person's actions, workflow,
    and decision-making in a scenario (spec clause 1) — predictive modeling
    from retained memory (clause 5). Owner-only; never distributed."""

    scenario: str
    horizon: Literal["immediate", "short_term", "long_term"] = "short_term"
    interactor_id: str | None = None   # condition on this relationship's history


class OrganizationCreate(BaseModel):
    name: str


class DepartmentAdd(BaseModel):
    name: str                          # e.g. Finance
    role: str                          # what its agent does for the team
    profile_id: str                    # the role-specific agent
    grant_token: str | None = None     # revocable scope for its data pulls


class LeaseRequest(BaseModel):
    """AI for lease: somebody else's licensed specialist, seated as a
    department under a revocable lease."""
    profile_id: str                    # the specialist offered for license
    name: str                          # department name it will hold
    role: str                          # what it does for the team


class CoordinateRequest(BaseModel):
    goal: str
    from_department: str               # department id that leads the plan


class Designee(BaseModel):
    """One recipient of a profile's proceeds (spec [0020] example two)."""

    name: str
    kind: Literal["loved_one", "organization"]
    share: int                         # percent; a designation sums to 100
    account_id: str | None = None      # platform account, when they have one


class ProceedsSet(BaseModel):
    designees: list[Designee] = Field(min_length=1)


class CampaignCreate(BaseModel):
    title: str
    goal: float
    cause: str | None = None


class DonationCreate(BaseModel):
    amount: float
    giver_id: str | None = None        # interactor; omitted = anonymous
    note: str | None = None
    on_behalf_of: str | None = None    # a company backing the campaign


class GrantCreate(BaseModel):
    scope: list[str] | None = None     # source-item ids; None = all sources


class TaskRun(BaseModel):
    kind: str = "compose_from_sources"
    topic: str
    grant_token: str


class WorkflowCreate(BaseModel):
    goal: str
    # Ordered phase names from workflows.PHASES; omit for the default plan
    # (research → draft → review → send → confirm).
    plan: list[str] | None = None
    grant_token: str | None = None     # scopes vault reads; revocable mid-run


class WorkflowResume(BaseModel):
    input: str                         # the awaited external confirmation


class DelegationSet(BaseModel):
    """Owner-declared envelope for workflows somebody else may start."""
    phases: list[str]                  # from delegation.DELEGABLE
    # Scopes every delegated vault read. Required when `research` is in
    # `phases` — without it that phase reads every source item on the profile.
    grant_token: str | None = None
    enabled: bool = True


class DelegatedWorkflowCreate(BaseModel):
    goal: str
    # Omit to get the owner's whole permitted set, never the product default.
    plan: list[str] | None = None
    interactor_id: str


class ObjectionOpen(BaseModel):
    profile_id: str
    objector_ref: str                  # out-of-band proof-of-identity reference
    reason: str | None = None


class ObjectionResolve(BaseModel):
    outcome: str                       # uphold | dismiss


class SucceedRequest(BaseModel):
    # Out-of-band verification reference (death certificate / power of
    # attorney) reviewed before ownership passes.
    verification_ref: str


class LicenseOffer(BaseModel):
    kind: str                          # consult | finetune | clone
    price: float = 0
    currency: str = "USD"
    terms: str | None = None
    allow_derivatives: bool = False    # may a buyer derive their own agent


class RatedPlacementCreate(BaseModel):
    venue: str                         # a key from qrme.rated.VENUES
    label: str | None = None           # e.g. "pinned post", "bio link"


class PackItemIn(BaseModel):
    title: str
    content: str
    task: str | None = None            # robot packs: the command verb added
    requires: list[str] = Field(default_factory=list)  # capabilities needed


class PackPublish(BaseModel):
    industry: str
    audience: Literal["profile", "robot"] = "profile"
    title: str
    blurb: str | None = None
    price: float = 0                   # 0 = free download
    currency: str = "USD"
    publisher: str = "independent"
    publisher_owner_id: str | None = None  # who the sales accrue to
    rated: bool = False                # 18+ commerce: age-gated to see and buy
    items: list[PackItemIn] = Field(default_factory=list)


class PackInstall(BaseModel):
    profile_id: str
    robot_id: str | None = None        # required for robot-audience packs
    accept_price: bool = False         # explicit consent to a priced pack


class SourceAdd(BaseModel):
    kind: SourceKind
    title: str | None = None
    content: str | None = None         # text body / transcript / description


class SurfacesSet(BaseModel):
    surfaces: list[str] = Field(default_factory=list)


SocialPlatform = Literal[
    "instagram", "x", "tiktok", "facebook", "linkedin", "youtube", "reddit",
    "threads", "whatsapp", "meta", "mastodon", "twitch", "snapchat", "roblox",
    "pinterest", "discord",
]


class SocialConnect(BaseModel):
    platform: SocialPlatform
    direction: Literal["collect", "publish"]
    handle: str | None = None          # the account handle on that platform
    scope: list[str] = Field(default_factory=list)  # posts, photos, bio, ...


class SocialItem(BaseModel):
    content: str                       # the post / caption / bio text
    title: str | None = None


class SocialCollect(BaseModel):
    items: list[SocialItem] = Field(default_factory=list)


class SocialPublish(BaseModel):
    content: str
    topic: str | None = None


class AppConnect(BaseModel):
    provider: str                      # apple | google | microsoft | canva
    app: str                           # photos | calendar | mail | ...
    capabilities: list[str] = Field(default_factory=list)  # empty = grant all the app offers


class AppItem(BaseModel):
    content: str
    title: str | None = None


class AppCollect(BaseModel):
    items: list[AppItem] = Field(default_factory=list)


class AppInvoke(BaseModel):
    capability: str
    input: str | None = None


class AppAuthorize(BaseModel):
    """The credential a connector needs, on its way to the vault.

    ``secret`` never lands in this deployment's own database — the route
    seals it into PDI and keeps the key. A deployment with no vault has
    nowhere safe to put it and refuses rather than storing it in the clear.
    """
    secret: str
    account: str | None = None         # which account on the far side, if named


class FeedbackSubmit(BaseModel):
    category: str = "idea"             # idea | improvement | bug | praise | other
    message: str
    rating: int | None = None         # optional 1..5 satisfaction


class MatterRaise(BaseModel):
    trouble: str                       # what is wrong, in their own words
    concerns: str = "app"              # app | profiles | platform


class MatterSettle(BaseModel):
    answer: str                        # what settled it
    helped: bool = False               # the raiser saying the offered answer did it


class MatterStep(BaseModel):
    did: str                           # see qrme.matters.STEPS
    note: str = ""


class AccessReportSubmit(BaseModel):
    doing: str                         # what you were trying to do
    wall: str                          # what stood in the way
    help: str | None = None           # what would help, in your words
    lang: str = "en"                  # the language the report is written in


class GameSessionCreate(BaseModel):
    platform: str                      # a catalog gaming app key
    game: str                          # free-text title
    role: str = "companion"            # companion | teammate | practice_partner
    mode: str = "online_multiplayer"   # online_multiplayer | co_op | practice


class GameCallout(BaseModel):
    situation: str                     # what's happening in the match
    minor_present: bool = False        # a minor in the lobby forces strict


class ExcursionStart(BaseModel):
    topic: str
    question: str
    private: list[str] = Field(default_factory=list)  # extra caller-marked private terms


class DialArm(BaseModel):
    # A verified signature over escalation.WAIVER, and nothing else.
    signature_id: str


class Unresolved(BaseModel):
    interactor_id: str
    matter: str                # what the profile could not resolve


class PrivilegeChoice(BaseModel):
    # Yes or no to one power, named in the path. Required rather than
    # defaulted: a body that can be empty is a body that turns something on by
    # arriving.
    on: bool


class PersonAttach(BaseModel):
    provider_id: str
    note: str | None = None
    # Their area is read off the provider row, never taken from here.
    preferred: bool = False


class BriefingPreview(BaseModel):
    interactor_id: str
    profile_id: str
    provider_id: str
    matter: str                # what this is about, in the user's own words
    # The revocable grant that decides what may travel. No grant, no briefing.
    grant_token: str


class StandDown(BaseModel):
    # A whole URL is accepted and reduced to its host, because the thing a
    # person has in their hand is the address they were shown.
    host: str


class InquiryOpen(BaseModel):
    topic: str
    question: str
    # More can be withheld. Nothing here can withhold less — the sanitizer is
    # not reachable from the wire. See qrme.inquiries.compose.
    private: list[str] = Field(default_factory=list)


class InquiryAnswer(BaseModel):
    body: str
    alias: str = ""          # what the answerer chose to be called; may be empty
    points_to: str = ""      # a direction to look, never followed automatically


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
    # Synthetic-media credential riding on profile turns: id, verify path,
    # disclosure, and the profile's always-displayed watermark design.
    watermark: dict | None = None
    # A rewritten turn says so — the fact of the edit is part of the
    # record even though the earlier words are not. Set on memory reads.
    edited: bool = False


class LookoutCreate(BaseModel):
    url: str
    every_hours: float


class ChatResponse(BaseModel):
    interactor_message: MessageOut
    profile_message: MessageOut
    # The verifiable basis of the profile's reply: model, grounding,
    # licensed lineage, and the moderation verdict (see content_provenance).
    provenance: dict | None = None
    # Multi-modal output descriptor: how the reply renders beyond text
    # (voice basis, image/video treatment). None for plain text.
    modality: dict | None = None
    # Set when biometric signals routed the reply to a domain specialist
    # (claim 24): {domain, specialist_profile_id, reason}.
    handoff: dict | None = None
    # Invariant identity fingerprint of the profile being addressed — the same
    # across every embodiment/modality, so a client can prove personality
    # continuity when a relationship moves from voice → text → hologram.
    persona_signature: str | None = None
    embodiment: str | None = None      # the embodiment this turn came through
    # Echo of the environmental context the reply adapted to (spec clause 1);
    # None when the request carried none.
    environment: dict | None = None
    # The role the profile worked in this turn (spec clauses 2/12):
    # {"role": "advisor"|"collaborator"|"operator", "how": "declared"|
    # "inferred"}. None = a plain turn, the profile as itself.
    role_context: dict | None = None


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


class ListingPlace(BaseModel):
    """Where a listing is offered — a locality somebody typed, never anything
    sniffed from a device. Refused for rated listings."""

    locality: str
    region: str | None = None
    remote: bool = False               # also served from anywhere


class MarketPrefs(BaseModel):
    """One interactor's saved marketplace settings. Defaults for a search,
    never a cage: anything passed explicitly to the search wins."""

    locality: str | None = None
    region: str | None = None
    scope: Literal["locality", "region", "anywhere"] | None = None
    include_remote: bool | None = None
    kinds: list[Literal["profile", "content", "expertise", "service"]] | None = None
    tags: list[str] | None = None


class MarketAssist(BaseModel):
    """"I don't know what to search for." Returns suggestions for the search
    box — never results, and nothing is filtered on the caller's behalf."""

    need: str


class ExperienceEntry(BaseModel):
    """One line of a profile's history.

    Strict, for the reason `SteeringSet` is: `period` is the field, and
    `years` is what anybody writing a CV form reaches for first. An unknown
    key was accepted and dropped, so the row saved with no dates and the
    request answered 200. Refusing by name is the smaller surprise.
    """

    model_config = ConfigDict(extra="forbid")

    title: str
    org: str | None = None
    period: str | None = None
    detail: str | None = None


class ExperienceSet(BaseModel):
    """The whole experience list, replaced wholesale — a CV is a statement,
    not a set of rows to patch one at a time."""

    entries: list[ExperienceEntry] = []


class ReviewIn(BaseModel):
    """A review by somebody who talked to the profile. One per interactor,
    edited rather than stacked."""

    interactor_id: str
    rating: int
    body: str | None = None


class HelpAsk(BaseModel):
    """A question about using QRME — not a message to a profile."""

    question: str = ""
    # `voice` renders the same answer for listening rather than reading. It is
    # a mode on the existing box rather than a second endpoint, because a
    # spoken help assistant and a written one answering differently is two
    # products, and the spoken one would be the one nobody re-read.
    mode: str = "text"
