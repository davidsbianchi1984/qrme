using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Net.Http.Json;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace QrmeStudio;

// MARK: wire models (mirror qrme/models.py + routers)

public record ProfileCreated(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("display_name")] string DisplayName,
    [property: JsonPropertyName("kind")] string Kind,
    [property: JsonPropertyName("owner_token")] string OwnerToken);

public record ProfileCard(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("display_name")] string DisplayName,
    [property: JsonPropertyName("kind")] string Kind,
    [property: JsonPropertyName("status")] string? Status);

public record GroundedIn(
    [property: JsonPropertyName("persona")] bool Persona,
    [property: JsonPropertyName("source_items")] int SourceItems);

public record ModerationInfo(
    [property: JsonPropertyName("maturity")] string Maturity,
    [property: JsonPropertyName("status")] string Status,
    [property: JsonPropertyName("flag_reason")] string? FlagReason);

public record ContentProvenance(
    [property: JsonPropertyName("method")] string Method,
    [property: JsonPropertyName("generated_by")] string GeneratedBy,
    [property: JsonPropertyName("language")] string Language,
    [property: JsonPropertyName("grounded_in")] GroundedIn GroundedInInfo,
    [property: JsonPropertyName("licensed_from")] string? LicensedFrom,
    [property: JsonPropertyName("moderation")] ModerationInfo Moderation,
    [property: JsonPropertyName("disclaimer")] string Disclaimer);

// The visible mark riding on every AI render (always displayed).
public record WatermarkDisplay(
    [property: JsonPropertyName("line")] string Line);

public record WatermarkBrief(
    [property: JsonPropertyName("watermark_id")] string? WatermarkId,
    [property: JsonPropertyName("display")] WatermarkDisplay? Display);

public record WatermarkDesign(
    [property: JsonPropertyName("mark")] string Mark,
    [property: JsonPropertyName("label")] string Label,
    [property: JsonPropertyName("line")] string Line,
    [property: JsonPropertyName("custom")] bool Custom);

public record Post(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("topic")] string? Topic,
    [property: JsonPropertyName("content")] string? Content,
    [property: JsonPropertyName("status")] string? Status,
    [property: JsonPropertyName("provenance")] ContentProvenance? Provenance,
    [property: JsonPropertyName("watermark")] WatermarkBrief? Watermark);

public record LanguageInfo(
    [property: JsonPropertyName("code")] string Code,
    [property: JsonPropertyName("label")] string Label);

// MARK: Voiceprint (FIG. 800)

public record VoiceConsentState(
    [property: JsonPropertyName("granted")] bool Granted,
    [property: JsonPropertyName("sources")] string[]? Sources,
    [property: JsonPropertyName("granted_at")] string? GrantedAt);

public record VoiceThreshold(
    [property: JsonPropertyName("samples")] int Samples,
    [property: JsonPropertyName("seconds")] double Seconds);

// Every field here is a count off the enrolled samples — there is no opaque
// quality score, so a thin enrollment reads as thin.
public record VoiceEnrollment(
    [property: JsonPropertyName("samples")] int Samples,
    [property: JsonPropertyName("seconds")] double Seconds,
    [property: JsonPropertyName("turns")] int Turns,
    [property: JsonPropertyName("mean_turn_seconds")] double? MeanTurnSeconds,
    [property: JsonPropertyName("ready")] bool Ready,
    [property: JsonPropertyName("needs")] string[] Needs,
    [property: JsonPropertyName("ready_when")] VoiceThreshold ReadyWhen,
    [property: JsonPropertyName("method")] string Method);

public record VoiceprintRecord(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("built_at")] string? BuiltAt,
    [property: JsonPropertyName("active")] bool Active);

public record VoiceprintStatus(
    [property: JsonPropertyName("consent")] VoiceConsentState Consent,
    [property: JsonPropertyName("enrollment")] VoiceEnrollment? Enrollment,
    [property: JsonPropertyName("voiceprint")] VoiceprintRecord? Voiceprint,
    [property: JsonPropertyName("disclosure")] string Disclosure);

public record VoiceSpoken(
    [property: JsonPropertyName("basis")] string Basis,
    [property: JsonPropertyName("disclosure")] string Disclosure);

public record VoiceRevocation(
    [property: JsonPropertyName("samples_deleted")] int SamplesDeleted,
    [property: JsonPropertyName("note")] string Note);

public record LanguagesList(
    [property: JsonPropertyName("languages")] LanguageInfo[] Languages,
    [property: JsonPropertyName("default")] string Default);

public record FeedbackItem(
    [property: JsonPropertyName("category")] string Category,
    [property: JsonPropertyName("message")] string Message,
    [property: JsonPropertyName("status")] string Status);

public record FeedbackState(
    [property: JsonPropertyName("mine")] FeedbackItem[] Mine,
    [property: JsonPropertyName("tally")] System.Collections.Generic.Dictionary<string, int> Tally,
    [property: JsonPropertyName("total")] int Total);

public record AccessReportRow(
    [property: JsonPropertyName("doing")] string Doing,
    [property: JsonPropertyName("wall")] string Wall,
    [property: JsonPropertyName("help")] string? Help,
    [property: JsonPropertyName("lang")] string Lang,
    [property: JsonPropertyName("created_at")] string CreatedAt);

public record AccessReportsState(
    [property: JsonPropertyName("reports")] AccessReportRow[] Reports,
    [property: JsonPropertyName("total")] int Total);

public record LanguageChoice(
    [property: JsonPropertyName("language")] string Language,
    [property: JsonPropertyName("label")] string Label,
    [property: JsonPropertyName("mode")] string? Mode);

public record TranslateResult(
    [property: JsonPropertyName("text")] string Text,
    [property: JsonPropertyName("translation")] string Translation,
    [property: JsonPropertyName("language")] string Language,
    [property: JsonPropertyName("engine")] string Engine,
    [property: JsonPropertyName("note")] string? Note);

public record ProviderInfo(
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("label")] string Label,
    [property: JsonPropertyName("configured")] bool Configured);

public record ModelsList(
    [property: JsonPropertyName("providers")] ProviderInfo[] Providers,
    [property: JsonPropertyName("default")] string Default);

public record ModelChoice(
    [property: JsonPropertyName("provider")] string Provider,
    [property: JsonPropertyName("effective")] string Effective);

public record RobotSpec(
    [property: JsonPropertyName("model")] string Model,
    [property: JsonPropertyName("label")] string Label,
    [property: JsonPropertyName("maker")] string Maker,
    [property: JsonPropertyName("kind")] string Kind);

public record RoboticsCatalog(
    [property: JsonPropertyName("robots")] RobotSpec[] Robots);

public record Robot(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("model")] string Model,
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("status")] string? Status,
    [property: JsonPropertyName("commands")] string[]? Commands);

public record CommandResult(
    [property: JsonPropertyName("command")] string Command,
    [property: JsonPropertyName("status")] string Status,
    [property: JsonPropertyName("spoken")] string? Spoken);

public record Objection(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("status")] string Status,
    [property: JsonPropertyName("reason")] string? Reason,
    [property: JsonPropertyName("reattested")] bool Reattested);

/// <summary>What comes back from raising an objection. <c>ProfileStatus</c> is
/// the part that matters to the person raising it: the profile is restricted
/// straight away, pending review, not after somebody gets round to it.</summary>
public record ObjectionOpened(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("profile_id")] string ProfileId,
    [property: JsonPropertyName("status")] string Status,
    [property: JsonPropertyName("profile_status")] string? ProfileStatus,
    // What it was before, so the sentence can say what a dismissal restores.
    // Returned since objections shipped; no shell read it.
    [property: JsonPropertyName("prior_status")] string? PriorStatus,
    [property: JsonPropertyName("note")] string? Note);

/// <summary>One thing that happened on an objection. <c>Sealed</c> says the
/// row is held in the vault; it does not carry what is inside it, and neither
/// does this record — there is no <c>Detail</c> here on purpose.</summary>
public record ObjectionTimelineEvent(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("event")] string Event,
    [property: JsonPropertyName("actor")] string Actor,
    [property: JsonPropertyName("sealed")] bool Sealed,
    [property: JsonPropertyName("at")] string At);

public record ObjectionTimeline(
    [property: JsonPropertyName("objection_id")] string ObjectionId,
    [property: JsonPropertyName("profile_id")] string ProfileId,
    [property: JsonPropertyName("status")] string Status,
    [property: JsonPropertyName("reattested")] bool Reattested,
    [property: JsonPropertyName("vault_backed")] bool VaultBacked,
    [property: JsonPropertyName("note")] string Note,
    [property: JsonPropertyName("events")] ObjectionTimelineEvent[] Events);

public record InteractorCreated(
    [property: JsonPropertyName("id")] string Id,
    // The server has always returned this; the shell simply never kept it, so
    // no route could be called as this person. The room routes are the first
    // that require it.
    [property: JsonPropertyName("token")] string? Token = null);

public record SteeringDial(
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("group")] string Group,
    [property: JsonPropertyName("label")] string Label,
    [property: JsonPropertyName("low")] string Low,
    [property: JsonPropertyName("high")] string High,
    [property: JsonPropertyName("min")] int Min,
    [property: JsonPropertyName("max")] int Max);

public record SteeringAgeBlock(
    [property: JsonPropertyName("base_age")] int? BaseAge,
    [property: JsonPropertyName("aging_enabled")] bool AgingEnabled,
    [property: JsonPropertyName("effective_age")] int? EffectiveAge);

public record SteeringAppearance(
    [property: JsonPropertyName("description")] string? Description);

public record SteeringUnlocked(
    [property: JsonPropertyName("subject_id")] string SubjectId);

public record SteeringLockOut(
    [property: JsonPropertyName("subject_id")] string SubjectId,
    [property: JsonPropertyName("reason")] string? Reason,
    [property: JsonPropertyName("locked_at")] string LockedAt);

public record SteeringHubState(
    [property: JsonPropertyName("adult_mode")] bool AdultMode,
    [property: JsonPropertyName("dials")] SteeringDial[] Dials,
    [property: JsonPropertyName("values")] System.Collections.Generic.Dictionary<string, int> Values,
    [property: JsonPropertyName("age")] SteeringAgeBlock Age,
    [property: JsonPropertyName("appearance")] SteeringAppearance Appearance,
    [property: JsonPropertyName("lock")] SteeringLockOut? Lock);

public record LedgerEntry(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("kind")] string Kind,
    [property: JsonPropertyName("memo")] string? Memo,
    [property: JsonPropertyName("amount")] double Amount,
    [property: JsonPropertyName("status")] string Status);

public record EarningsTotals(
    [property: JsonPropertyName("accrued")] double Accrued,
    [property: JsonPropertyName("paid")] double Paid,
    [property: JsonPropertyName("lifetime")] double Lifetime,
    [property: JsonPropertyName("by_kind")] System.Collections.Generic.Dictionary<string, double> ByKind);

public record EarningsStatement(
    [property: JsonPropertyName("entries")] LedgerEntry[] Entries,
    [property: JsonPropertyName("totals")] EarningsTotals Totals,
    [property: JsonPropertyName("currency")] string Currency);

public record PayoutReceipt(
    [property: JsonPropertyName("payout_id")] string PayoutId,
    [property: JsonPropertyName("total_amount")] double TotalAmount,
    [property: JsonPropertyName("entries")] int Entries);

public record RelationshipState(
    [property: JsonPropertyName("relationship_type")] string RelationshipType,
    [property: JsonPropertyName("nickname")] string? Nickname,
    [property: JsonPropertyName("tone")] string? Tone);

public record ChatMessage(
    [property: JsonPropertyName("content")] string? Content,
    [property: JsonPropertyName("status")] string Status,
    [property: JsonPropertyName("flag_reason")] string? FlagReason,
    [property: JsonPropertyName("watermark")] WatermarkBrief? Watermark);

public record ChatReply(
    [property: JsonPropertyName("profile_message")] ChatMessage ProfileMessage,
    [property: JsonPropertyName("provenance")] ContentProvenance? Provenance,
    [property: JsonPropertyName("role_context")] RoleContext? RoleContext);

/// Spec clauses 2/12 — which way the profile worked this turn, and whether the
/// owner declared it or the wording implied it. Reported so an inference is
/// never mistaken for an instruction.
public record RoleContext(
    [property: JsonPropertyName("role")] string Role,
    [property: JsonPropertyName("how")] string How);

/// Extract and reconstruct: whose work is this, from the text alone. Never a
/// bare yes — the counts travel with the claim so it can be checked.
/// <summary>The count, and the three things it refuses to be. The refusals
/// arrive as fields rather than prose so a page renders them beside the
/// number instead of composing a reassuring sentence of its own.</summary>
public record SolitudeTurns(
    [property: JsonPropertyName("to_profiles")] int ToProfiles,
    [property: JsonPropertyName("to_people")] int ToPeople);

public record SolitudeOffer(
    [property: JsonPropertyName("state")] string State,
    [property: JsonPropertyName("why")] string? Why);

public record Solitude(
    [property: JsonPropertyName("interactor_id")] string InteractorId,
    [property: JsonPropertyName("window_days")] int WindowDays,
    [property: JsonPropertyName("turns")] SolitudeTurns Turns,
    [property: JsonPropertyName("total_turns")] int TotalTurns,
    // Null until there is any conversation at all to take a ratio of.
    [property: JsonPropertyName("share_synthetic")] double? ShareSynthetic,
    [property: JsonPropertyName("enough_to_say")] bool EnoughToSay,
    [property: JsonPropertyName("note")] string Note,
    [property: JsonPropertyName("offer")] SolitudeOffer? Offer);

public record SolitudeReferral(
    [property: JsonPropertyName("ref")] string Ref,
    [property: JsonPropertyName("window_days")] int WindowDays,
    [property: JsonPropertyName("turns")] SolitudeTurns Turns,
    [property: JsonPropertyName("issued_at")] string IssuedAt,
    [property: JsonPropertyName("product")] string Product);

public record SolitudeDecision(
    [property: JsonPropertyName("interactor_id")] string InteractorId,
    [property: JsonPropertyName("state")] string State,
    [property: JsonPropertyName("referral")] SolitudeReferral? Referral);

public record ProfileAttention(
    [property: JsonPropertyName("profile_id")] string ProfileId,
    [property: JsonPropertyName("people_this_week")] int PeopleThisWeek,
    [property: JsonPropertyName("people_ever")] int PeopleEver,
    [property: JsonPropertyName("you_are_one_of_them")] bool YouAreOneOfThem,
    [property: JsonPropertyName("says")] string Says,
    [property: JsonPropertyName("ranks_people")] bool RanksPeople,
    [property: JsonPropertyName("has_a_favourite")] bool HasAFavourite,
    [property: JsonPropertyName("names_anybody")] bool NamesAnybody,
    [property: JsonPropertyName("note")] string Note);

public record WatermarkRecovery(
    [property: JsonPropertyName("recovered")] bool Recovered,
    [property: JsonPropertyName("reason")] string? Reason,
    [property: JsonPropertyName("profile_id")] string? ProfileId,
    [property: JsonPropertyName("verbatim")] bool Verbatim,
    [property: JsonPropertyName("similarity")] double Similarity,
    [property: JsonPropertyName("matched_windows")] int MatchedWindows,
    [property: JsonPropertyName("stored_windows")] int StoredWindows,
    // How many windows were looked at, which is the denominator the page's
    // sentence names. iOS has carried it since the mark shipped; this did not.
    [property: JsonPropertyName("examined_windows")] int ExaminedWindows,
    [property: JsonPropertyName("state")] string? State,
    [property: JsonPropertyName("best_similarity")] double? BestSimilarity,
    [property: JsonPropertyName("threshold")] double? Threshold,
    [property: JsonPropertyName("display")] WatermarkDesign? Display,
    [property: JsonPropertyName("disclosure")] string? Disclosure,
    [property: JsonPropertyName("method")] string? Method);

public record SocialConn(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("platform")] string Platform,
    [property: JsonPropertyName("direction")] string Direction,
    [property: JsonPropertyName("handle")] string? Handle,
    [property: JsonPropertyName("status")] string? Status,
    [property: JsonPropertyName("collected")] int Collected,
    [property: JsonPropertyName("published")] int Published);

public record CatalogApp(
    [property: JsonPropertyName("app")] string App,
    [property: JsonPropertyName("label")] string Label,
    [property: JsonPropertyName("capabilities")] string[] Capabilities);

public record CatalogProvider(
    [property: JsonPropertyName("provider")] string Provider,
    [property: JsonPropertyName("label")] string Label,
    [property: JsonPropertyName("apps")] CatalogApp[] Apps);

public record AppsCatalog(
    [property: JsonPropertyName("providers")] CatalogProvider[] Providers);

public record AppConn(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("provider")] string Provider,
    [property: JsonPropertyName("app")] string App,
    [property: JsonPropertyName("label")] string Label,
    [property: JsonPropertyName("capabilities")] string[] Capabilities,
    [property: JsonPropertyName("status")] string? Status);

public record InvokeResult(
    [property: JsonPropertyName("capability")] string Capability,
    [property: JsonPropertyName("status")] string Status,
    [property: JsonPropertyName("result")] string Result);

public record ConnJoin(
    [property: JsonPropertyName("status")] string Status,
    [property: JsonPropertyName("connection_id")] string? ConnectionId,
    [property: JsonPropertyName("matched_with")] string? MatchedWith);

public record ConnMsg(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("from")] string From,
    [property: JsonPropertyName("content")] string Content,
    [property: JsonPropertyName("status")] string? Status);

public record RoomCreated(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("topic")] string Topic,
    [property: JsonPropertyName("channel")] string Channel);

public record RoomMsg(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("sender_kind")] string SenderKind,
    [property: JsonPropertyName("from")] string From,
    [property: JsonPropertyName("content")] string? Content,
    [property: JsonPropertyName("status")] string? Status);

public record HandleClaim(
    [property: JsonPropertyName("profile_id")] string ProfileId,
    [property: JsonPropertyName("handle")] string Handle,
    [property: JsonPropertyName("summon")] string Summon);

public record Beacon(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("label")] string Label,
    [property: JsonPropertyName("location")] string? Location,
    [property: JsonPropertyName("scans")] int Scans,
    [property: JsonPropertyName("active")] bool Active);

public record BeaconPlaced(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("label")] string Label,
    [property: JsonPropertyName("summon_url")] string SummonUrl,
    [property: JsonPropertyName("qr_svg")] string QrSvg);

public record SummonCard(
    [property: JsonPropertyName("profile_id")] string ProfileId,
    [property: JsonPropertyName("display_name")] string DisplayName,
    [property: JsonPropertyName("handle")] string? Handle,
    [property: JsonPropertyName("purpose")] string? Purpose,
    [property: JsonPropertyName("status")] string Status,
    [property: JsonPropertyName("note")] string? Note);

public record SummonResult(
    [property: JsonPropertyName("type")] string Type,
    [property: JsonPropertyName("ref")] string Ref,
    [property: JsonPropertyName("label")] string? Label,
    [property: JsonPropertyName("location")] string? Location,
    [property: JsonPropertyName("scans")] int? Scans,
    [property: JsonPropertyName("profile")] SummonCard? Profile,
    [property: JsonPropertyName("profiles")] SummonCard[]? Profiles);

public record Pack(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("industry")] string Industry,
    [property: JsonPropertyName("audience")] string Audience,
    [property: JsonPropertyName("title")] string Title,
    [property: JsonPropertyName("blurb")] string? Blurb,
    [property: JsonPropertyName("publisher")] string Publisher,
    [property: JsonPropertyName("price")] double Price,
    [property: JsonPropertyName("currency")] string Currency,
    [property: JsonPropertyName("free")] bool Free,
    [property: JsonPropertyName("origin")] string Origin,
    [property: JsonPropertyName("origin_url")] string? OriginUrl,
    [property: JsonPropertyName("items")] int Items,
    [property: JsonPropertyName("installs")] int Installs);

public record PackRegistry(
    [property: JsonPropertyName("key")] string Key,
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("url")] string Url,
    [property: JsonPropertyName("audience")] string Audience,
    [property: JsonPropertyName("tagline")] string Tagline,
    [property: JsonPropertyName("available_packs")] int AvailablePacks,
    [property: JsonPropertyName("synced")] int Synced);

public record InstalledPack(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("title")] string Title,
    [property: JsonPropertyName("price_paid")] double PricePaid,
    [property: JsonPropertyName("robot_id")] string? RobotId);

public record PackInstalled(
    [property: JsonPropertyName("installed_items")] int? InstalledItems,
    [property: JsonPropertyName("installed_tasks")] string[]? InstalledTasks,
    [property: JsonPropertyName("price_paid")] double PricePaid)
{
    public int Count => InstalledItems ?? InstalledTasks?.Length ?? 0;
}

public record GameSession(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("platform")] string Platform,
    [property: JsonPropertyName("platform_label")] string? PlatformLabel,
    [property: JsonPropertyName("game")] string Game,
    [property: JsonPropertyName("role")] string Role,
    [property: JsonPropertyName("status")] string Status,
    [property: JsonPropertyName("callouts")] int? Callouts);

public record GameCalloutResult(
    [property: JsonPropertyName("status")] string Status,
    [property: JsonPropertyName("line")] string? Line,
    [property: JsonPropertyName("flag_reason")] string? FlagReason,
    [property: JsonPropertyName("role")] string Role);

public record Listing(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("kind")] string Kind,
    [property: JsonPropertyName("title")] string Title,
    [property: JsonPropertyName("blurb")] string? Blurb,
    [property: JsonPropertyName("tags")] string[] Tags,
    [property: JsonPropertyName("area")] string? Area,
    [property: JsonPropertyName("provider_name")] string? ProviderName,
    [property: JsonPropertyName("business")] bool Business,
    [property: JsonPropertyName("profile_id")] string? ProfileId);

public record ListingCreated(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("kind")] string Kind,
    [property: JsonPropertyName("title")] string Title);

public record LicenseOffer(
    [property: JsonPropertyName("profile_id")] string ProfileId,
    [property: JsonPropertyName("kind")] string Kind,
    [property: JsonPropertyName("price")] double Price,
    [property: JsonPropertyName("currency")] string Currency,
    [property: JsonPropertyName("terms")] string? Terms,
    [property: JsonPropertyName("allow_derivatives")] bool AllowDerivatives);

public record ManifestWithheld(
    [property: JsonPropertyName("item")] string Item,
    [property: JsonPropertyName("reason")] string Reason);

/// <summary>What a derivation handed over and what stayed behind, written
/// server-side at derive time. Carried is a heterogeneous object; the shell
/// shows its key names.</summary>
public record LicenseManifest(
    [property: JsonPropertyName("carried")]
    System.Collections.Generic.Dictionary<string, System.Text.Json.JsonElement> Carried,
    [property: JsonPropertyName("withholdings")] ManifestWithheld[] Withholdings);

public record LicenseGrant(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("buyer_id")] string BuyerId,
    [property: JsonPropertyName("kind")] string Kind,
    [property: JsonPropertyName("derived_profile_id")] string? DerivedProfileId,
    [property: JsonPropertyName("revoked")] bool Revoked,
    [property: JsonPropertyName("manifest")] LicenseManifest? Manifest);

public record Excursion(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("topic")] string Topic,
    [property: JsonPropertyName("redactions")] int Redactions,
    [property: JsonPropertyName("left_host")] bool LeftHost,
    [property: JsonPropertyName("findings")] string Findings,
    [property: JsonPropertyName("learned")] bool Learned);

/// <summary>
// Live desks. A real person, so the card carries no AI watermark — it makes
// the opposite claim, and says who attested it.

public record DeskFeed(
    [property: JsonPropertyName("url")] string Url,
    [property: JsonPropertyName("live")] bool Live,
    [property: JsonPropertyName("note")] string Note);

public record DeskAttestation(
    [property: JsonPropertyName("attestor")] string Attestor,
    [property: JsonPropertyName("basis")] string Basis,
    [property: JsonPropertyName("signed")] bool Signed,
    [property: JsonPropertyName("note")] string Note);

public record DeskBell(
    [property: JsonPropertyName("available")] bool Available,
    [property: JsonPropertyName("waiting")] int Waiting);

public record DeskCard(
    [property: JsonPropertyName("desk_id")] string DeskId,
    [property: JsonPropertyName("display_name")] string DisplayName,
    [property: JsonPropertyName("trade")] string Trade,
    [property: JsonPropertyName("location")] string? Location,
    [property: JsonPropertyName("blurb")] string? Blurb,
    [property: JsonPropertyName("presence")] string Presence,
    [property: JsonPropertyName("human")] bool Human,
    [property: JsonPropertyName("ai")] bool Ai,
    [property: JsonPropertyName("designation")] string Designation,
    [property: JsonPropertyName("attestation")] DeskAttestation Attestation,
    [property: JsonPropertyName("feed")] DeskFeed Feed,
    [property: JsonPropertyName("bell")] DeskBell Bell);

public record RingReceipt(
    [property: JsonPropertyName("ring_id")] string RingId,
    [property: JsonPropertyName("waiting")] int Waiting,
    [property: JsonPropertyName("note")] string Note);


/// <summary>One connected thing across the counter. Token appears only in
/// the caller's own view of an active link — the desk's never carries it.</summary>
public record DeskConnection(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("session_id")] string SessionId,
    [property: JsonPropertyName("kind")] string Kind,
    [property: JsonPropertyName("target")] string Target,
    [property: JsonPropertyName("scope")] string? Scope,
    [property: JsonPropertyName("status")] string Status,
    [property: JsonPropertyName("means")] string? Means,
    [property: JsonPropertyName("token")] string? Token);

public record DeskSession(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("desk_id")] string DeskId,
    [property: JsonPropertyName("caller_id")] string CallerId,
    [property: JsonPropertyName("status")] string Status,
    [property: JsonPropertyName("desk_name")] string? DeskName,
    [property: JsonPropertyName("connections")] DeskConnection[] Connections);

// Signatures (docs/signatures.md). Windows reads and verifies; it does not
// sign — see SignaturesPage for why.

public record SigningCredential(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("credential_id")] string CredentialId,
    [property: JsonPropertyName("proofing_level")] string ProofingLevel,
    [property: JsonPropertyName("display_name")] string? DisplayName,
    [property: JsonPropertyName("device_bound")] bool DeviceBound,
    [property: JsonPropertyName("backup_eligible")] bool BackupEligible,
    [property: JsonPropertyName("can_sign")] List<string> CanSign,
    [property: JsonPropertyName("revoked_at")] string? RevokedAt);

public record SigningCredentials(
    [property: JsonPropertyName("credentials")] List<SigningCredential> Credentials);

public record SignatureVerification(
    [property: JsonPropertyName("valid")] bool Valid,
    [property: JsonPropertyName("notes")] List<string> Notes);

public record SignatureSigner(
    [property: JsonPropertyName("name")] string? Name,
    [property: JsonPropertyName("proofing_level")] string ProofingLevel);

public record SignaturePackage(
    [property: JsonPropertyName("signature_id")] string SignatureId,
    [property: JsonPropertyName("meaning")] string? Meaning,
    [property: JsonPropertyName("display_text")] string? DisplayText,
    [property: JsonPropertyName("document_sha256")] string? DocumentSha256,
    [property: JsonPropertyName("signed_at")] string SignedAt,
    [property: JsonPropertyName("tier")] string Tier,
    [property: JsonPropertyName("platform")] string? Platform,
    [property: JsonPropertyName("transport")] string? Transport,
    [property: JsonPropertyName("signer")] SignatureSigner Signer,
    [property: JsonPropertyName("verification")] SignatureVerification Verification,
    [property: JsonPropertyName("limits")] List<string> Limits);

public record EnrollRp(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("name")] string Name);

public record EnrollUser(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("displayName")] string DisplayName);

public record EnrollOptions(
    [property: JsonPropertyName("challenge")] string Challenge,
    [property: JsonPropertyName("rp")] EnrollRp Rp,
    [property: JsonPropertyName("user")] EnrollUser User);

public record SignatureEnvelope(
    [property: JsonPropertyName("envelope_id")] string EnvelopeId,
    [property: JsonPropertyName("challenge")] string Challenge,
    [property: JsonPropertyName("display_text")] string DisplayText,
    [property: JsonPropertyName("meaning")] string Meaning);

public record SignaturePolicy(
    [property: JsonPropertyName("standard")] string Standard,
    [property: JsonPropertyName("limits")] List<string> Limits);

/// Async client for the QRME backend. Windows reaches the local dev server
/// directly on 127.0.0.1.
/// </summary>
public sealed class ApiClient
{
    public static ApiClient Shared { get; } = new();

    private readonly HttpClient _http = new() { BaseAddress = new Uri("http://127.0.0.1:8000") };

    /// <summary>Every request this client sends, and the one place the
    /// reader's language is attached to it.
    ///
    /// <para>The header used to be set in <c>Send&lt;T&gt;</c>, which is the
    /// shared helper — and twenty-one calls in this file went straight to
    /// <c>_http.SendAsync</c> instead. Those are the uploads, the streams and
    /// the raw-response reads, and every refusal they draw arrived in English
    /// no matter what the machine was set to. A funnel only funnels what goes
    /// into it.</para></summary>
    private Task<HttpResponseMessage> Dispatch(HttpRequestMessage req)
    {
        req.Headers.TryAddWithoutValidation("accept-language", L10n.DeviceLanguage());
        // The person's own model key, if this machine holds one. Sent as a
        // header rather than stored server-side: the backend puts it in a
        // context var for the length of the call and never writes it down.
        var llmKey = AppState.Current.LlmKey;
        if (!string.IsNullOrEmpty(llmKey))
            req.Headers.TryAddWithoutValidation("x-llm-api-key", llmKey);
        // The deployment invite key: a published deployment sets
        // QRME_SIGNUP_KEY and refuses account creation without it. The
        // backend reads it only on the routes it gates.
        var signupKey = AppState.Current.SignupKey;
        if (!string.IsNullOrEmpty(signupKey))
            req.Headers.TryAddWithoutValidation("x-signup-key", signupKey);
        return _http.SendAsync(req);
    }

    public void SetBase(string url) => _http.BaseAddress = new Uri(url.TrimEnd('/'));

    private async Task<T> Send<T>(HttpRequestMessage req)
    {
        // The path as written, for the recorder. Read before the send, which
        // consumes `req`. Absolute and relative are both handled: these calls
        // build relative URIs against BaseAddress, but a `RequestUri` that
        // ever arrived absolute would otherwise put the host in the log —
        // not private, but not the operation either.
        var method = req.Method.Method;
        var path = req.RequestUri is { IsAbsoluteUri: true } abs
            ? abs.AbsolutePath
            : req.RequestUri?.ToString() ?? "";

        HttpResponseMessage res;
        try
        {
            res = await Dispatch(req);
        }
        catch
        {
            // Never reached a server. Recorded as status 0; the thrown error
            // still carries its message to the person, who owns it.
            Problems.Record(method, path, 0);
            throw;
        }
        var body = await res.Content.ReadAsStringAsync();
        if (!res.IsSuccessStatusCode)
        {
            // The status and the operation, never the detail below: these
            // messages quote what the person typed, which is theirs to read
            // and nobody's to keep.
            Problems.Record(method, path, (int)res.StatusCode);
            // GetString() throws on an array, which a 422's `detail` is, so the
            // catch swallowed it and the person saw the status code. `message`
            // is the sentence the backend composes beside the rows.
            string? said = null;
            try
            {
                var root = JsonDocument.Parse(body).RootElement;
                if (root.TryGetProperty("message", out var m) && m.ValueKind == JsonValueKind.String)
                    said = m.GetString();
                else if (root.TryGetProperty("detail", out var d) && d.ValueKind == JsonValueKind.String)
                    said = d.GetString();
            }
            catch { /* non-JSON error body */ }
            throw new HttpRequestException(said ?? $"HTTP {(int)res.StatusCode}");
        }
        // A 204 — or any success with an empty body — is the route saying
        // "done, nothing to report". Deserializing "" throws, which turned
        // every successful delete into an error on screen.
        return JsonSerializer.Deserialize<T>(
            string.IsNullOrWhiteSpace(body) ? "{}" : body)!;
    }

    private static HttpRequestMessage Get(string path) =>
        new(HttpMethod.Get, path);

    private static HttpRequestMessage Get(string path, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Get, path);
        req.Headers.Add("authorization", $"Bearer {token}");
        return req;
    }

    private static HttpRequestMessage Post(string path, object body, string? token = null)
    {
        var req = new HttpRequestMessage(HttpMethod.Post, path) { Content = JsonContent.Create(body) };
        if (token is not null) req.Headers.Add("authorization", $"Bearer {token}");
        return req;
    }

    private static HttpRequestMessage Put(string path, object body, string? token = null)
    {
        var req = new HttpRequestMessage(HttpMethod.Put, path) { Content = JsonContent.Create(body) };
        if (token is not null) req.Headers.Add("authorization", $"Bearer {token}");
        return req;
    }

    public Task<ProfileCreated> CreateProfile(string name, string persona, string kind,
                                              string birthdate, string? language = null) =>
        Send<ProfileCreated>(Post("/profiles",
            language is { Length: > 0 } && language != "en"
                ? new
                  {
                      owner_id = "owner-1",
                      kind,
                      display_name = name,
                      persona,
                      verification = new { birthdate },
                      language,
                      // clickwrap: the Welcome page displays the Terms
                      terms_consent = true,
                  }
                : (object)new
                  {
                      owner_id = "owner-1",
                      kind,
                      display_name = name,
                      terms_consent = true,
                      persona,
                      verification = new { birthdate },
                  }));

    public Task<ProfileCard> Profile(string id) =>
        Send<ProfileCard>(new HttpRequestMessage(HttpMethod.Get, $"/profiles/{id}"));

    public Task<Post> Compose(string id, string token, string topic) =>
        Send<Post>(Post($"/profiles/{id}/compose", new { topic }, token));

    public Task<Post[]> Posts(string id) =>
        Send<Post[]>(new HttpRequestMessage(HttpMethod.Get, $"/profiles/{id}/posts"));

    // -- watermark (the mark every AI render carries) --

    public Task<WatermarkDesign> GetWatermarkDesign(string id) =>
        Send<WatermarkDesign>(new HttpRequestMessage(
            HttpMethod.Get, $"/profiles/{id}/watermark"));

    // Design the profile's watermark; the AI designation is invariant.
    public Task<WatermarkDesign> SetWatermarkDesign(
        string id, string token, string? mark, string? label) =>
        Send<WatermarkDesign>(Put($"/profiles/{id}/watermark",
            new { mark = string.IsNullOrWhiteSpace(mark) ? null : mark,
                  label = string.IsNullOrWhiteSpace(label) ? null : label },
            token));

    // -- model selection --

    public Task<ModelsList> Models() =>
        Send<ModelsList>(new HttpRequestMessage(HttpMethod.Get, "/models"));

    public Task<ModelChoice> ProfileModel(string id) =>
        Send<ModelChoice>(new HttpRequestMessage(HttpMethod.Get, $"/profiles/{id}/model"));

    public Task<ModelChoice> SetModel(string id, string token, string provider)
    {
        var req = new HttpRequestMessage(HttpMethod.Put, $"/profiles/{id}/model")
        {
            Content = JsonContent.Create(new { provider }),
        };
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<ModelChoice>(req);
    }

    // -- language (the profile speaks it everywhere) --

    public Task<LanguagesList> Languages() =>
        Send<LanguagesList>(new HttpRequestMessage(HttpMethod.Get, "/languages"));

    public async Task<string> SubmitFeedback(string? token, string category,
                                             string message, int? rating)
    {
        object body = rating is { } r
            ? new { category, message, rating = r }
            : new { category, message };
        var res = await Dispatch(Post("/feedback", body, token));
        res.EnsureSuccessStatusCode();
        return "received";
    }

    public Task<FeedbackState> Feedback(string? token)
    {
        var req = new HttpRequestMessage(HttpMethod.Get, "/feedback");
        if (token is { Length: > 0 }) req.Headers.Add("authorization", $"Bearer {token}");
        return Send<FeedbackState>(req);
    }

    // The accessibility door: tokenless on purpose — the person it exists
    // for may be the person the signup shut out. The words stay on the
    // deployment; nothing here reaches the problems collector.
    public async Task<string> SendAccessReport(string doing, string wall,
                                               string? help, string lang)
    {
        object body = help is { Length: > 0 } h
            ? new { doing, wall, help = h, lang }
            : new { doing, wall, lang };
        var res = await Dispatch(Post("/access/reports", body, null));
        res.EnsureSuccessStatusCode();
        return "received";
    }

    // Reviewer-token read — the deployment's steward, never a profile.
    public Task<AccessReportsState> AccessReports(string reviewerToken)
    {
        var req = new HttpRequestMessage(HttpMethod.Get, "/access/reports");
        req.Headers.Add("authorization", $"Bearer {reviewerToken}");
        return Send<AccessReportsState>(req);
    }

    public Task<LanguageChoice> ProfileLanguage(string id) =>
        Send<LanguageChoice>(new HttpRequestMessage(
            HttpMethod.Get, $"/profiles/{id}/language"));

    public Task<LanguageChoice> SetLanguage(string id, string token, string code,
                                            string mode = "pre")
    {
        var req = new HttpRequestMessage(HttpMethod.Put, $"/profiles/{id}/language")
        {
            Content = JsonContent.Create(new { language = code, mode }),
        };
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<LanguageChoice>(req);
    }

    public Task<TranslateResult> Translate(string id, string token, string text) =>
        Send<TranslateResult>(Post($"/profiles/{id}/translate", new { text }, token));

    // -- robotic embodiment --

    public Task<RoboticsCatalog> Robotics() =>
        Send<RoboticsCatalog>(new HttpRequestMessage(HttpMethod.Get, "/robotics/catalog"));

    public Task<Robot[]> Robots(string id, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Get, $"/profiles/{id}/robots");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<Robot[]>(req);
    }

    public Task<Robot> BindRobot(string id, string token, string model) =>
        Send<Robot>(Post($"/profiles/{id}/robots", new { model }, token));

    public Task<CommandResult> CommandRobot(string rid, string token,
                                            string command, string? arg) =>
        Send<CommandResult>(Post($"/robots/{rid}/command",
            arg is { Length: > 0 } ? new { command, arg } : (object)new { command },
            token));

    // -- objections (governance) --

    /// <summary>Raise an objection against a profile. Takes <b>no
    /// credential</b>, and that is the point: <c>open_objection</c> says so in
    /// its own docstring — <i>the objecting party need not own an account</i>.
    ///
    /// <para>This route belongs to somebody who has found a synthetic profile
    /// of themselves, has no QRME account, and therefore has no console. Until
    /// 0.23.0 every shell carried the owner's half of governance — listing
    /// objections against your own profile, attesting to them — and none
    /// carried this one.</para></summary>
    public Task<ObjectionOpened> OpenObjection(
        string profileId, string objectorRef, string reason) =>
        Send<ObjectionOpened>(Post("/objections", new
        {
            profile_id = profileId,
            objector_ref = objectorRef,
            reason,
        }, null));

    /// <summary>The objector's view of their own case: what happened, who did
    /// it, when. No credential, because the person this belongs to has none.
    ///
    /// <para><c>/objections/{id}/audit</c> is owner- or reviewer-gated, and its
    /// reason is sound about the free text — it can quote the objector's own
    /// words back through a third party. It is wrong about who it locks out.
    /// The objector wrote that reason, and could already end the profile
    /// through the public <c>withdraw</c> and <c>revoke</c> routes:</para>
    ///
    /// <para><i>asked</i> — could the audit trail leak the objector's reason.
    /// <i>mattered</i> — who is the audit trail for.</para>
    ///
    /// <para>So this is a second view rather than a wider one. Event, actor,
    /// time, sealed. Nobody's prose, including the objector's own.</para></summary>
    public Task<ObjectionTimeline> ObjectionTimeline(string objectionId) =>
        Send<ObjectionTimeline>(new HttpRequestMessage(
            HttpMethod.Get, $"/objections/{objectionId}/timeline"));

    public Task<Objection[]> Objections(string id, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Get, $"/profiles/{id}/objections");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<Objection[]>(req);
    }

    public async Task Attest(string id, string objectionId, string token)
    {
        var req = Post($"/profiles/{id}/objections/{objectionId}/attest",
                       new { }, token);
        var res = await Dispatch(req);
        res.EnsureSuccessStatusCode();
    }

    // -- chat (the core loop) --

    public Task<InteractorCreated> CreateInteractor(string name,
                                                    string? birthdate = null) =>
        Send<InteractorCreated>(Post("/interactors",
            birthdate is { Length: > 0 }
                ? new { display_name = name, birthdate }
                : (object)new { display_name = name }));

    // -- steering: the owner shapes how the profile comes across --

    public Task<SteeringHubState> SteeringHub(string id, string token) =>
        Send<SteeringHubState>(Get($"/profiles/{id}/steering/hub", token));

    /// <summary>The personality nobody can move: while the lock stands,
    /// no steering write lands. The key is the owner's.</summary>
    public Task<SteeringLockOut> LockSteering(string pid, string token) =>
        Send<SteeringLockOut>(Post($"/profiles/{pid}/steering/lock",
            new { }, token));

    public Task<SteeringUnlocked> UnlockSteering(string pid, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
            $"/profiles/{pid}/steering/lock");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<SteeringUnlocked>(req);
    }

    public Task<SteeringHubState> SetSteeringHub(string id, string token,
        System.Collections.Generic.Dictionary<string, int>? values,
        int? baseAge, bool? agingEnabled, string? appearance)
    {
        var body = new System.Collections.Generic.Dictionary<string, object>();
        if (values is not null) body["values"] = values;
        if (baseAge is not null || agingEnabled is not null)
        {
            var age = new System.Collections.Generic.Dictionary<string, object>();
            if (baseAge is { } b) age["base_age"] = b;
            if (agingEnabled is { } a) age["aging_enabled"] = a;
            body["age"] = age;
        }
        if (appearance is not null)
            body["appearance"] = new { description = appearance };
        var req = new HttpRequestMessage(HttpMethod.Put, $"/profiles/{id}/steering/hub")
        {
            Content = JsonContent.Create(body),
        };
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<SteeringHubState>(req);
    }

    // -- earnings: the creator's statement over the ledger --

    public Task<EarningsStatement> Earnings(string id, string token) =>
        Send<EarningsStatement>(Get($"/profiles/{id}/earnings", token));

    public Task<PayoutReceipt> RequestPayout(string id, string token) =>
        Send<PayoutReceipt>(Post($"/profiles/{id}/earnings/payout", new { }, token));

    // -- relationship: how the profile relates to you --

    public Task<RelationshipState> SetRelationship(string id, string token,
        string interactorId, string type, string? nickname, string? tone)
    {
        var body = new System.Collections.Generic.Dictionary<string, object>
        {
            ["relationship_type"] = type,
        };
        if (nickname is { Length: > 0 }) body["nickname"] = nickname;
        if (tone is { Length: > 0 }) body["tone"] = tone;
        var req = new HttpRequestMessage(HttpMethod.Put,
            $"/profiles/{id}/relationships/{interactorId}")
        {
            Content = JsonContent.Create(body),
        };
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<RelationshipState>(req);
    }

    /// <summary>
    /// `role` is optional on purpose: left empty the profile reads the wording
    /// and decides for itself, and the reply reports which way it went.
    /// </summary>
    public Task<ChatReply> Chat(string id, string token, string interactorId,
                                string message, string? role = null) =>
        Send<ChatReply>(Post($"/profiles/{id}/chat",
            string.IsNullOrWhiteSpace(role)
                ? new { interactor_id = interactorId, message }
                : (object)new { interactor_id = interactorId, message, role },
            token));

    /// <summary>
    /// Whose work is this, from the text alone — no credential id, and it keeps
    /// answering after the text has been edited. No token: a counterparty must
    /// be able to ask without an account here.
    /// </summary>
    /// <summary>How many people a profile is talking to. Public, and no
    /// token here on purpose: the count is a fact about the profile, not a
    /// secret earned by intimacy.</summary>
    public Task<ProfileAttention> ProfileAttention(string profileId) =>
        Send<ProfileAttention>(Get($"/profiles/{profileId}/attention"));

    /// <summary>How much of this person's talking here went to a profile
    /// rather than to a person. The mirror of ProfileAttention — and unlike
    /// it, scoped to the account asking. There is no owner view of this and
    /// there must never be one.</summary>
    public Task<Solitude> Solitude(string interactorId) =>
        Send<Solitude>(Get($"/interactors/{interactorId}/solitude"));

    /// <summary>Take the JIM-mini door or close it. Closing is recorded so
    /// the offer is not made a second time.</summary>
    public Task<SolitudeDecision> SolitudeHandoff(string interactorId, bool accept) =>
        Send<SolitudeDecision>(
            Post($"/interactors/{interactorId}/solitude/handoff", new { accept }));

    /// <summary>What would travel, readable before it does — counts and a
    /// window, never a word anybody wrote.</summary>
    public Task<SolitudeReferral> SolitudeReferral(string interactorId) =>
        Send<SolitudeReferral>(Get($"/interactors/{interactorId}/solitude/referral"));

    public Task<WatermarkRecovery> RecoverWatermark(string content) =>
        Send<WatermarkRecovery>(Post("/watermarks/recover", new { content }));

    // -- community: stranger connections & multiparty rooms --

    // The interactor's token rides on every one of these. The id says whose
    // turn it is; the token says who is asking. Without it, two public ids
    // were enough to speak as either party, read the pair's conversation and
    // end it.
    public Task<ConnJoin> JoinQueue(string interactorId, string alias,
                                    string tier, string token) =>
        Send<ConnJoin>(Post("/connections/join",
            alias is { Length: > 0 }
                ? new { interactor_id = interactorId, tier, alias }
                : (object)new { interactor_id = interactorId, tier }, token));

    public Task<ConnMsg[]> ConnectionMessages(string cid, string interactorId,
                                              string token) =>
        Send<ConnMsg[]>(Get(
            $"/connections/{cid}/messages?interactor_id={interactorId}", token));

    public async Task SendConnectionMessage(string cid, string interactorId,
                                            string message, string token)
    {
        var req = Post($"/connections/{cid}/messages",
            new { interactor_id = interactorId, message }, token);
        var res = await Dispatch(req);
        res.EnsureSuccessStatusCode();
    }

    public async Task EndConnection(string cid, string interactorId, string token)
    {
        var req = Post($"/connections/{cid}/end?interactor_id={interactorId}",
                       new { }, token);
        var res = await Dispatch(req);
        res.EnsureSuccessStatusCode();
    }

    public Task<RoomCreated> CreateRoom(string topic, string profileId, string interactorId) =>
        Send<RoomCreated>(Post("/rooms", new
        {
            topic,
            channel = "chat",
            participants = new object[]
            {
                new { kind = "user", id = interactorId },
                new { kind = "profile", id = profileId },
            },
        }));

    // All three carry the interactor token now. The room routes used to take
    // none: the speaker was read out of `sender_id` in the body, so anybody
    // with a room id could post as a named participant, and the transcript
    // was readable by anybody at all. `sender_id` is still sent because the
    // server still accepts the field; it is ignored there, and the token is
    // what says who is speaking.
    public async Task RoomMessage(string roomId, string senderId, string message,
                                  string token)
    {
        var req = Post($"/rooms/{roomId}/messages",
                       new { sender_id = senderId, message }, token);
        var res = await Dispatch(req);
        res.EnsureSuccessStatusCode();
    }

    public async Task RoomAdvance(string roomId, string token)
    {
        var req = Post($"/rooms/{roomId}/advance", new { }, token);
        var res = await Dispatch(req);
        res.EnsureSuccessStatusCode();
    }

    public Task<RoomMsg[]> RoomTranscript(string roomId, string token) =>
        Send<RoomMsg[]>(Get($"/rooms/{roomId}/messages", token));

    // -- Connect: social platforms & the connected-apps catalog --

    public Task<SocialConn[]> SocialConnections(string id, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Get, $"/profiles/{id}/social");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<SocialConn[]>(req);
    }

    public Task<SocialConn> SocialConnect(string id, string token, string platform,
                                          string direction, string handle) =>
        Send<SocialConn>(Post($"/profiles/{id}/social",
            handle is { Length: > 0 }
                ? new { platform, direction, handle }
                : (object)new { platform, direction }, token));

    public async Task SocialCollect(string cid, string token, string content)
    {
        var req = Post($"/social/{cid}/collect",
            new { items = new[] { new { content } } }, token);
        var res = await Dispatch(req);
        res.EnsureSuccessStatusCode();
    }

    public async Task SocialScrape(string cid, string token)
    {
        var req = Post($"/social/{cid}/scrape", new { }, token);
        var res = await Dispatch(req);
        res.EnsureSuccessStatusCode();
    }

    public async Task SocialPublish(string cid, string token, string content)
    {
        var req = Post($"/social/{cid}/publish", new { content }, token);
        var res = await Dispatch(req);
        res.EnsureSuccessStatusCode();
    }

    public async Task RevokeSocial(string cid, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete, $"/social/{cid}");
        req.Headers.Add("authorization", $"Bearer {token}");
        var res = await Dispatch(req);
        res.EnsureSuccessStatusCode();
    }

    public Task<AppsCatalog> ConnectorCatalog() =>
        Send<AppsCatalog>(new HttpRequestMessage(HttpMethod.Get, "/connectors/catalog"));

    public Task<AppConn[]> AppConnections(string id, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Get, $"/profiles/{id}/apps");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<AppConn[]>(req);
    }

    public Task<AppConn> AppConnect(string id, string token, string provider, string app) =>
        Send<AppConn>(Post($"/profiles/{id}/apps", new { provider, app }, token));

    public async Task AppCollect(string cid, string token, string content)
    {
        var req = Post($"/apps/{cid}/collect",
            new { items = new[] { new { content } } }, token);
        var res = await Dispatch(req);
        res.EnsureSuccessStatusCode();
    }

    public Task<InvokeResult> AppInvoke(string cid, string token, string capability) =>
        Send<InvokeResult>(Post($"/apps/{cid}/invoke", new { capability }, token));

    // -- Reach: summon (@handle + beacons), marketplace, licensing --

    // The owner's token. Without it a stranger could replace the name a
    // profile answers to, and the old one stopped resolving.
    public Task<HandleClaim> ClaimHandle(string id, string handle, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Put, $"/profiles/{id}/handle")
        {
            Content = JsonContent.Create(new { handle }),
        };
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<HandleClaim>(req);
    }

    public Task<BeaconPlaced> PlaceBeacon(string id, string label, string location) =>
        Send<BeaconPlaced>(Post($"/profiles/{id}/beacons",
            location is { Length: > 0 }
                ? new { label, location }
                : (object)new { label }));

    public Task<Beacon[]> Beacons(string id) =>
        Send<Beacon[]>(new HttpRequestMessage(HttpMethod.Get, $"/profiles/{id}/beacons"));

    public async Task PickUpBeacon(string bid)
    {
        var res = await Dispatch(
            new HttpRequestMessage(HttpMethod.Delete, $"/beacons/{bid}"));
        res.EnsureSuccessStatusCode();
    }

    public Task<SummonResult> Summon(string reference) =>
        Send<SummonResult>(new HttpRequestMessage(
            HttpMethod.Get, $"/summon?ref={Uri.EscapeDataString(reference)}"));

    public Task<ListingCreated> CreateListing(string title, string blurb,
                                              string[] tags, string providerName,
                                              string profileId) =>
        Send<ListingCreated>(Post("/marketplace/listings",
            blurb is { Length: > 0 }
                ? new { kind = "profile", title, blurb, tags,
                        provider_name = providerName, profile_id = profileId }
                : (object)new { kind = "profile", title, tags,
                                provider_name = providerName, profile_id = profileId }));

    // -- knowledge packs: buy/download expertise for the profile --

    public Task<Pack[]> Packs(string industry) =>
        Send<Pack[]>(new HttpRequestMessage(HttpMethod.Get,
            industry is { Length: > 0 }
                ? $"/packs?industry={Uri.EscapeDataString(industry)}"
                : "/packs"));

    public Task<PackRegistry[]> PackRegistries() =>
        Send<PackRegistry[]>(new HttpRequestMessage(HttpMethod.Get,
            "/packs/registries"));

    public async Task SyncRegistry(string key)
    {
        var res = await Dispatch(
            Post($"/packs/registries/{key}/sync", new { }, null));
        res.EnsureSuccessStatusCode();
    }

    public Task<InstalledPack[]> InstalledPacks(string pid, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Get, $"/profiles/{pid}/packs");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<InstalledPack[]>(req);
    }

    public Task<PackInstalled> InstallPack(string packId, string pid,
                                           string token, bool acceptPrice,
                                           string? robotId = null) =>
        Send<PackInstalled>(Post($"/packs/{packId}/install",
            robotId is null
                ? new { profile_id = pid, accept_price = acceptPrice }
                : (object)new { profile_id = pid, accept_price = acceptPrice,
                                robot_id = robotId }, token));

    public async Task UninstallPack(string packId, string pid, string token)
    {
        var req = new HttpRequestMessage(
            HttpMethod.Delete, $"/profiles/{pid}/packs/{packId}");
        req.Headers.Add("authorization", $"Bearer {token}");
        (await Dispatch(req)).EnsureSuccessStatusCode();
    }

    public async Task UninstallRobotPack(string packId, string robotId, string token)
    {
        var req = new HttpRequestMessage(
            HttpMethod.Delete, $"/robots/{robotId}/packs/{packId}");
        req.Headers.Add("authorization", $"Bearer {token}");
        (await Dispatch(req)).EnsureSuccessStatusCode();
    }

    // -- gaming: a profile plays alongside real players --

    public Task<GameSession[]> GameSessions(string pid, string token) =>
        Send<GameSession[]>(Get($"/profiles/{pid}/gaming/sessions", token));

    public Task<GameSession> StartGameSession(string pid, string token,
                                              string platform, string game, string role) =>
        Send<GameSession>(Post($"/profiles/{pid}/gaming/sessions",
            new { platform, game, role }, token));

    public Task<GameCalloutResult> GameCallout(string sid, string token,
                                               string situation, bool minorPresent) =>
        Send<GameCalloutResult>(Post($"/gaming/sessions/{sid}/callout",
            new { situation, minor_present = minorPresent }, token));

    public async Task EndGameSession(string sid, string token)
    {
        var res = await Dispatch(Post($"/gaming/sessions/{sid}/end", new { }, token));
        res.EnsureSuccessStatusCode();
    }

    public Task<Listing[]> Listings(string tag) =>
        Send<Listing[]>(new HttpRequestMessage(HttpMethod.Get,
            tag is { Length: > 0 }
                ? $"/marketplace/listings?tag={Uri.EscapeDataString(tag)}"
                : "/marketplace/listings"));

    public async Task RemoveListing(string lid)
    {
        var res = await Dispatch(
            new HttpRequestMessage(HttpMethod.Delete, $"/marketplace/listings/{lid}"));
        res.EnsureSuccessStatusCode();
    }

    public Task<LicenseOffer> SetLicense(string id, string token, string kind,
                                         double price, string terms)
    {
        var req = new HttpRequestMessage(HttpMethod.Put, $"/profiles/{id}/license")
        {
            Content = JsonContent.Create(
                terms is { Length: > 0 }
                    ? new { kind, price, terms }
                    : (object)new { kind, price }),
        };
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<LicenseOffer>(req);
    }

    public Task<LicenseOffer> License(string id) =>
        Send<LicenseOffer>(new HttpRequestMessage(
            HttpMethod.Get, $"/profiles/{id}/license"));

    public async Task UnlistLicense(string id, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete, $"/profiles/{id}/license");
        req.Headers.Add("authorization", $"Bearer {token}");
        var res = await Dispatch(req);
        res.EnsureSuccessStatusCode();
    }

    public Task<LicenseGrant[]> LicenseGrants(string id, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Get, $"/profiles/{id}/licenses");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<LicenseGrant[]>(req);
    }

    public async Task RevokeLicense(string gid, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete, $"/licenses/{gid}");
        req.Headers.Add("authorization", $"Bearer {token}");
        var res = await Dispatch(req);
        res.EnsureSuccessStatusCode();
    }

    // -- knowledge excursions (study safely; private data stays home) --

    public Task<Excursion[]> Excursions(string id, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Get, $"/profiles/{id}/excursions");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<Excursion[]>(req);
    }

    public Task<Excursion> StartExcursion(string id, string token,
                                          string topic, string question) =>
        Send<Excursion>(Post($"/profiles/{id}/excursions",
            new { topic, question }, token));

    public async Task Learn(string cid, string token)
    {
        var req = Post($"/excursions/{cid}/learn", new { }, token);
        var res = await Dispatch(req);
        res.EnsureSuccessStatusCode();
    }

    // MARK: Live desks

    public async Task<DeskCard> GetDesk(string id) =>
        await Send<DeskCard>(new HttpRequestMessage(HttpMethod.Get, $"/desks/{id}"));

    /// <summary>
    /// Ring the bell at an unattended desk. No token: the visitor looking at
    /// an empty chair is exactly the person who has no account.
    /// </summary>
    public async Task<RingReceipt> RingBell(string deskId, string? note) =>
        await Send<RingReceipt>(Post($"/desks/{deskId}/bell", new { note }));

    /// <summary>The absolute URL of the desk's camera view.</summary>
    public string DeskViewUrl(string deskId) =>
        new Uri(_http.BaseAddress!, $"/desks/{deskId}/view.webp").ToString();


    // MARK: Connections across the counter — the desk's actual service. The
    // desk offers; only the caller's accept mints the link token, returned to
    // the caller alone. Either side ends it.

    public Task<DeskSession> OpenDeskSession(string deskId, string callerId, string token) =>
        Send<DeskSession>(Post($"/desks/{deskId}/sessions", new { caller_id = callerId }, token));

    public Task<DeskSession[]> DeskSessions(string deskId, string token) =>
        Send<DeskSession[]>(Get($"/desks/{deskId}/sessions", token));

    public Task<DeskSession> DeskSession(string sessionId, string token) =>
        Send<DeskSession>(Get($"/desk-sessions/{sessionId}", token));

    public Task<DeskConnection> OfferDeskConnection(string sessionId, string kind,
        string target, string? scope, string token) =>
        Send<DeskConnection>(Post($"/desk-sessions/{sessionId}/connections",
            new { kind, target, scope }, token));

    public Task<DeskConnection> AnswerDeskConnection(string sessionId,
        string connectionId, bool accept, string token) =>
        Send<DeskConnection>(Post(
            $"/desk-sessions/{sessionId}/connections/{connectionId}/answer",
            new { accept }, token));

    public Task<DeskConnection> EndDeskConnection(string sessionId,
        string connectionId, string token) =>
        Send<DeskConnection>(Post(
            $"/desk-sessions/{sessionId}/connections/{connectionId}/end",
            new { }, token));

    public Task<DeskSession> CloseDeskSession(string sessionId, string token) =>
        Send<DeskSession>(Post($"/desk-sessions/{sessionId}/close", new { }, token));

    public Task<DeskSession[]> MyDeskSessions(string interactorId, string token) =>
        Send<DeskSession[]>(Get($"/interactors/{interactorId}/desk-sessions", token));

    // MARK: Signatures — the ceremony runs in a WebView2 (see SignaturesPage)

    /// <summary>
    /// The URL of the embeddable WebAuthn ceremony page. Served from the
    /// deployment's own origin because WebAuthn refuses a mismatched rpId and
    /// an opaque origin has none to match.
    ///
    /// The host is rewritten from a loopback IP to <c>localhost</c>. That is
    /// not cosmetic: a relying party id must be a <em>domain</em>, and
    /// <c>127.0.0.1</c> is not one, so every ceremony fetched from the
    /// default base address was refused by the browser before Windows Hello
    /// was ever reached. <c>localhost</c> is a domain, resolves to the same
    /// backend, and counts as a secure context without a certificate.
    /// </summary>
    public string CeremonyUrl(string mode, string challenge,
                              string displayText = "", string meaning = "",
                              string userId = "", string userName = "",
                              string displayName = "")
    {
        var q = new Dictionary<string, string>
        {
            ["mode"] = mode, ["challenge"] = challenge,
            ["display_text"] = displayText, ["meaning"] = meaning,
            ["user_id"] = userId, ["user_name"] = userName,
            ["display_name"] = displayName,
        };
        var query = string.Join("&", q.Where(kv => kv.Value.Length > 0)
            .Select(kv => $"{kv.Key}={Uri.EscapeDataString(kv.Value)}"));
        var origin = new UriBuilder(_http.BaseAddress!);
        if (origin.Host is "127.0.0.1" or "::1" or "[::1]") origin.Host = "localhost";
        return new Uri(origin.Uri, $"/signatures/ceremony?{query}").ToString();
    }

    public async Task<EnrollOptions> EnrollOptions(string displayName, string token) =>
        await Send<EnrollOptions>(Post("/signatures/enroll/options",
            new { display_name = displayName }, token));

    public async Task<SigningCredential> EnrollCredential(
        string credentialId, string attestationObject, string clientDataJson,
        string challenge, string displayName, string token) =>
        await Send<SigningCredential>(Post("/signatures/enroll", new
        {
            credential_id = credentialId,
            attestation_object = attestationObject,
            client_data_json = clientDataJson,
            challenge,
            proofing_level = "self_asserted",
            display_name = displayName,
        }, token));

    public async Task<SignatureEnvelope> RequestSignature(
        string document, string meaning, string tier, string token) =>
        await Send<SignatureEnvelope>(Post("/signatures/request", new
        {
            document, meaning, display_text = document, tier,
        }, token));

    public async Task<SignaturePackage> SubmitSignature(
        string envelopeId, string credentialId, string signature,
        string authenticatorData, string clientDataJson, string token) =>
        await Send<SignaturePackage>(Post("/signatures/sign", new
        {
            envelope_id = envelopeId,
            credential_id = credentialId,
            signature,
            authenticator_data = authenticatorData,
            client_data_json = clientDataJson,
            transport = "internal",
            platform = "windows",
        }, token));

    // MARK: Signatures — read and verify. Signing needs a platform
    // authenticator, which this app does not yet reach (see SignaturesPage).

    public async Task<SignaturePolicy> GetSignaturePolicy() =>
        await Send<SignaturePolicy>(new HttpRequestMessage(HttpMethod.Get, "/signatures/policy"));

    public async Task<List<SigningCredential>> ListSigningCredentials(string token) =>
        (await Send<SigningCredentials>(Get("/signatures/credentials", token))).Credentials;

    public async Task<SignaturePackage> GetSignature(string id) =>
        await Send<SignaturePackage>(new HttpRequestMessage(HttpMethod.Get, $"/signatures/{id}"));

    /// <summary>
    /// Check an evidence package handed over from outside. No token: a
    /// counterparty must be able to verify a signature without an account
    /// here, which is what makes it a record that stands on its own.
    /// </summary>
    public async Task<SignatureVerification> VerifySignature(JsonElement package) =>
        await Send<SignatureVerification>(
            Post("/signatures/verify", new { package }));

    // MARK: Voiceprint — FIG. 800, in the order the drawing gates it

    public Task<VoiceprintStatus> Voiceprint(string id, string token) =>
        Send<VoiceprintStatus>(Get($"/profiles/{id}/voiceprint", token));

    /// <summary>
    /// Step 802. own_voice is fixed true because the backend refuses the grant
    /// without it — there is deliberately no path to enrolling somebody else's
    /// voice, so there is nothing here for a caller to toggle.
    /// </summary>
    public Task<VoiceprintStatus> GrantVoiceConsent(string id, string token,
                                                    string[] sources) =>
        Send<VoiceprintStatus>(Put($"/profiles/{id}/voiceprint/consent",
            new { own_voice = true, sources }, token));

    /// <summary>
    /// Steps 806–808. Only the measurements travel: how long the recording ran
    /// and how many spoken turns it held. The audio stays on this machine.
    /// </summary>
    public Task<VoiceEnrollment> AddVoiceSample(string id, string token, string source,
                                                double seconds, int turns,
                                                string? reference = null) =>
        Send<VoiceEnrollment>(Post($"/profiles/{id}/voiceprint/samples",
            new { source, seconds, turns, reference }, token));

    public Task<VoiceprintStatus> BuildVoiceprint(string id, string token) =>
        Send<VoiceprintStatus>(Post($"/profiles/{id}/voiceprint", new { }, token));

    public Task<VoiceSpoken> SpeakInVoice(string id, string token, string text) =>
        Send<VoiceSpoken>(Post($"/profiles/{id}/voiceprint/speak", new { text }, token));

    /// <summary>Withdrawal: the samples go, the print retires, the withdrawal
    /// itself stays — which is why this reports counts.</summary>
    public Task<VoiceRevocation> RevokeVoiceprint(string id, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete, $"/profiles/{id}/voiceprint");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<VoiceRevocation>(req);
    }

    // -- shops: storefronts, not desks (qrme/shops.py) --

    public Task<ShopCard[]> ListShops() =>
        Send<ShopCard[]>(new HttpRequestMessage(HttpMethod.Get, "/shops"));

    public Task<ShopDetail> ShopCard(string shopId) =>
        Send<ShopDetail>(new HttpRequestMessage(HttpMethod.Get, $"/shops/{shopId}"));

    public Task<ShopDetail> OpenShop(string profileId, string name, string token) =>
        Send<ShopDetail>(Post("/shops",
            new { profile_id = profileId, name }, token));

    public Task<ShopOffering> AddShopOffering(string shopId, string kind,
                                              string title, double price,
                                              string token) =>
        Send<ShopOffering>(Post($"/shops/{shopId}/offerings",
            new { kind, title, price }, token));

    public Task<ShopOffering> RetireShopOffering(string shopId,
                                                 string offeringId, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
            $"/shops/{shopId}/offerings/{offeringId}");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<ShopOffering>(req);
    }

    /// <summary>The buyer's press — signed with the interactor's own token.</summary>
    public Task<ShopOrder> PlaceShopOrder(string shopId, string offeringId,
                                          string buyerId, int quantity,
                                          string token) =>
        Send<ShopOrder>(Post($"/shops/{shopId}/orders",
            new { offering_id = offeringId, buyer_id = buyerId, quantity },
            token));

    public Task<ShopOrder[]> ShopOrderBook(string shopId, string token) =>
        Send<ShopOrder[]>(Get($"/shops/{shopId}/orders", token));

    public Task<ShopOrder[]> MyShopOrders(string buyerId, string token) =>
        Send<ShopOrder[]>(Get($"/shops/orders/of/{buyerId}", token));

    public Task<ShopOrder> AdvanceShopOrder(string shopId, string orderId,
                                            string party, string to,
                                            string token) =>
        Send<ShopOrder>(Post($"/shops/{shopId}/orders/{orderId}/advance",
            new { party, to }, token));

    // -- your corner: switches, messages, the homepage (qrme/social.py) --

    public Task<System.Collections.Generic.Dictionary<string, bool>> Features(
            string profileId, string token) =>
        Send<System.Collections.Generic.Dictionary<string, bool>>(
            Get($"/profiles/{profileId}/features", token));

    public Task<System.Collections.Generic.Dictionary<string, bool>> SetFeature(
            string profileId, string feature, bool enabled, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Put,
            $"/profiles/{profileId}/features")
        { Content = JsonContent.Create(new { feature, enabled }) };
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<System.Collections.Generic.Dictionary<string, bool>>(req);
    }

    public Task<DmMessageRow> SendDm(string profileId, string to, string body,
                                     string token) =>
        Send<DmMessageRow>(Post($"/profiles/{profileId}/messages",
            new { to, body }, token));

    public Task<DmThreadBox> DmThreads(string profileId, string token) =>
        Send<DmThreadBox>(Get($"/profiles/{profileId}/messages", token));

    public Task<DmThreadView> DmThread(string profileId, string withId,
                                       string token) =>
        Send<DmThreadView>(Get(
            $"/profiles/{profileId}/messages?with_id={withId}", token));

    public Task<HomepageDoc> HomepageOf(string profileId, string? token)
    {
        var req = new HttpRequestMessage(HttpMethod.Get,
            $"/profiles/{profileId}/homepage");
        if (token is not null) req.Headers.Add("authorization", $"Bearer {token}");
        return Send<HomepageDoc>(req);
    }

    public Task<HomepageDoc> EditHomepage(string profileId, string headline,
                                          string about, string bg,
                                          string accent, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Put,
            $"/profiles/{profileId}/homepage")
        { Content = JsonContent.Create(new { headline, about,
            theme = new { bg, accent } }) };
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<HomepageDoc>(req);
    }

    // -- the owner's workshop: workflows, delegation, the assistant,
    // tasks under a grant, rated placements and specialists ---------------

    public Task<WorkflowCard[]> Workflows(string profileId, string token) =>
        Send<WorkflowCard[]>(Get($"/profiles/{profileId}/workflows", token));

    public Task<WorkflowCard> StartWorkflow(string profileId, string goal,
        string token) =>
        Send<WorkflowCard>(Post($"/profiles/{profileId}/workflows",
            new { goal }, token));

    public Task<WorkflowCard> WorkflowOf(string profileId,
        string workflowId, string token) =>
        Send<WorkflowCard>(Get(
            $"/profiles/{profileId}/workflows/{workflowId}", token));

    public Task<WorkflowCard> AdvanceWorkflow(string profileId,
        string workflowId, string token) =>
        Send<WorkflowCard>(Post(
            $"/profiles/{profileId}/workflows/{workflowId}/advance",
            new { }, token));

    public Task<WorkflowCard> ResumeWorkflow(string profileId,
        string workflowId, string input, string token) =>
        Send<WorkflowCard>(Post(
            $"/profiles/{profileId}/workflows/{workflowId}/resume",
            new { input }, token));

    public Task<WorkflowCard> CancelWorkflow(string profileId,
        string workflowId, string token) =>
        Send<WorkflowCard>(Post(
            $"/profiles/{profileId}/workflows/{workflowId}/cancel",
            new { }, token));

    /// <summary>A capability advertisement, readable without a token, so
    /// a caller can decide whether a handoff is possible before
    /// attempting one.</summary>
    public Task<DelegationOffer> DelegationOfferOf(string profileId) =>
        Send<DelegationOffer>(Get($"/profiles/{profileId}/delegation"));

    public Task<DelegationOffer> SetDelegation(string profileId,
        string[] phases, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Put,
            $"/profiles/{profileId}/delegation")
        { Content = JsonContent.Create(new { phases }) };
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<DelegationOffer>(req);
    }

    public Task<WorkflowCard> StartDelegatedWorkflow(string profileId,
        string interactorId, string goal, string token) =>
        Send<WorkflowCard>(Post($"/profiles/{profileId}/delegated-workflows",
            new { goal, interactor_id = interactorId }, token));

    public Task<WorkflowCard> DelegatedWorkflowOf(string profileId,
        string workflowId, string token) =>
        Send<WorkflowCard>(Get(
            $"/profiles/{profileId}/delegated-workflows/{workflowId}",
            token));

    public Task<WorkflowCard> AdvanceDelegatedWorkflow(string profileId,
        string workflowId, string token) =>
        Send<WorkflowCard>(Post(
            $"/profiles/{profileId}/delegated-workflows/{workflowId}/advance",
            new { }, token));

    public Task<WorkflowCard> ResumeDelegatedWorkflow(string profileId,
        string workflowId, string input, string token) =>
        Send<WorkflowCard>(Post(
            $"/profiles/{profileId}/delegated-workflows/{workflowId}/resume",
            new { input }, token));

    public Task<CreativeWork> ComposeNote(string profileId, string moment,
        string token) =>
        Send<CreativeWork>(Post($"/profiles/{profileId}/assist/compose",
            new { kind = "note", moment }, token));

    public Task<CreativeWork[]> ComposedWorks(string profileId,
        string token) =>
        Send<CreativeWork[]>(Get($"/profiles/{profileId}/assist/works",
            token));

    public Task<ProofreadOut> Proofread(string profileId, string text,
        string token) =>
        Send<ProofreadOut>(Post($"/profiles/{profileId}/assist/proofread",
            new { text }, token));

    public Task<TriageOut> Triage(string profileId, object[] items,
        int keep, string criteria, string token) =>
        Send<TriageOut>(Post($"/profiles/{profileId}/assist/triage",
            new { items, keep, criteria }, token));

    public Task<TaskGrant> MintTaskGrant(string profileId, string token) =>
        Send<TaskGrant>(Post($"/profiles/{profileId}/grants",
            new { scope = new[] { "*" } }, token));

    public Task<TaskGrant> RevokeTaskGrant(string grantId, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
            $"/grants/{grantId}");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<TaskGrant>(req);
    }

    public Task<TaskOut> RunTask(string profileId, string topic,
        string grantToken, string token) =>
        Send<TaskOut>(Post($"/profiles/{profileId}/tasks",
            new { topic, grant_token = grantToken }, token));

    public Task<TaskRow[]> TasksRun(string profileId, string token) =>
        Send<TaskRow[]>(Get($"/profiles/{profileId}/tasks", token));

    public Task<VenueCard[]> RatedVenues() =>
        Send<VenueCard[]>(Get("/venues"));

    public Task<PlacementMade> PlaceRated(string profileId, string venue,
        string label, string token) =>
        Send<PlacementMade>(Post($"/profiles/{profileId}/placements",
            label.Length > 0 ? new { venue, label } : (object)new { venue },
            token));

    public Task<PlacementRow[]> Placements(string profileId,
        string token) =>
        Send<PlacementRow[]>(Get($"/profiles/{profileId}/placements",
            token));

    public Task<PlacementStats> PlacementAnalytics(string profileId,
        string token) =>
        Send<PlacementStats>(Get(
            $"/profiles/{profileId}/placements/analytics", token));

    public Task<PlacementCustody> PlacementCustodyOf(string profileId,
        string token) =>
        Send<PlacementCustody>(Get(
            $"/profiles/{profileId}/placements/custody", token));

    public Task<PlacementMade> RemovePlacement(string placementId,
        string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
            $"/placements/{placementId}");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<PlacementMade>(req);
    }

    public Task<SpecialistRow[]> Specialists(string profileId,
        string token) =>
        Send<SpecialistRow[]>(Get($"/profiles/{profileId}/specialists",
            token));

    public Task<SpecialistRow> SetSpecialist(string profileId,
        string domain, string specialistId, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Put,
            $"/profiles/{profileId}/specialists")
        {
            Content = JsonContent.Create(new
            { domain, specialist_profile_id = specialistId })
        };
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<SpecialistRow>(req);
    }

    // -- the record, the veil and the exit: what the platform holds about
    // a profile, what its anonymity hides, and how it ends ---------------

    public Task<MemoryRow[]> Memories(string profileId, string token) =>
        Send<MemoryRow[]>(Get($"/profiles/{profileId}/memories", token));

    public Task<MemoryTurn[]> Memory(string profileId, string interactorId,
        string token) =>
        Send<MemoryTurn[]>(Get(
            $"/profiles/{profileId}/memory/{interactorId}", token));

    // The distilled long memory of one person — what survived the window.
    public Task<RemembranceOut> Remembrance(string profileId,
        string interactorId, string token) =>
        Send<RemembranceOut>(Get(
            $"/profiles/{profileId}/memory/{interactorId}/remembrance",
            token));

    /// <summary>What do you remember about me — from the records.</summary>
    public Task<MemoryAccountOut> MemoryAccount(string profileId,
        string interactorId, string token) =>
        Send<MemoryAccountOut>(Get(
            $"/profiles/{profileId}/memory/{interactorId}/account", token));

    /// <summary>Forget that one thing; the kept memory re-folds.</summary>
    public Task<ForgetOut> ForgetMemory(string profileId,
        string interactorId, string about, string token) =>
        Send<ForgetOut>(Post(
            $"/profiles/{profileId}/memory/{interactorId}/forget",
            new { about }, token));

    public Task<MemoryTurn> EraseMemory(string profileId,
        string interactorId, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
            $"/profiles/{profileId}/memory/{interactorId}");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<MemoryTurn>(req);
    }

    public Task<ThreadOut> ThreadOf(string profileId, string interactorId,
        string token) =>
        Send<ThreadOut>(Get(
            $"/profiles/{profileId}/thread/{interactorId}", token));

    public Task<EngagementCard> EngagementOf(string profileId,
        string interactorId, string token) =>
        Send<EngagementCard>(Get(
            $"/profiles/{profileId}/engagement/{interactorId}", token));

    /// <summary>The pair may read it — the person it is about, and the
    /// profile's owner — and nobody else.</summary>
    public Task<ClinicalNote[]> ClinicalNotes(string profileId,
        string interactorId, string token) =>
        Send<ClinicalNote[]>(Get(
            $"/profiles/{profileId}/clinical-notes/{interactorId}", token));

    public Task<EmbeddingCard> EmbeddingOf(string profileId,
        string interactorId, string token) =>
        Send<EmbeddingCard>(Get(
            $"/profiles/{profileId}/embedding/{interactorId}", token));

    public Task<SourceRow[]> Sources(string profileId, string token) =>
        Send<SourceRow[]>(Get($"/profiles/{profileId}/sources", token));

    public Task<SourceRow> AddSource(string profileId, string kind,
        string title, string content, string token) =>
        Send<SourceRow>(Post($"/profiles/{profileId}/sources",
            new { kind, title, content }, token));

    /// <summary>Public on purpose: how many relationships this profile
    /// holds, and which model actually answers for it.</summary>
    public Task<TransparencyCard> TransparencyOf(string profileId) =>
        Send<TransparencyCard>(Get($"/profiles/{profileId}/transparency"));

    public Task<ExportOut> ExportProfile(string profileId, string token) =>
        Send<ExportOut>(Get($"/profiles/{profileId}/export", token));

    public Task<StatsCard> ProfileStats(string profileId, string token) =>
        Send<StatsCard>(Get($"/profiles/{profileId}/stats", token));

    public Task<FeedOut> FeedOf(string profileId) =>
        Send<FeedOut>(Get($"/profiles/{profileId}/feed"));

    public Task<VeilCard> AnonymityOf(string profileId, string token) =>
        Send<VeilCard>(Get($"/profiles/{profileId}/anonymity", token));

    public Task<VeilCard> SetAnonymity(string profileId, bool anonymous,
        string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Put,
            $"/profiles/{profileId}/anonymity")
        { Content = JsonContent.Create(new { anonymous }) };
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<VeilCard>(req);
    }

    /// <summary>Public: a claim a stranger can see is a claim a stranger
    /// should be able to check.</summary>
    public Task<VerificationCard> VerificationOf(string profileId) =>
        Send<VerificationCard>(Get($"/profiles/{profileId}/verification"));

    public Task<VerificationCard> ClaimVerification(string profileId,
        string level, string attestor, string token) =>
        Send<VerificationCard>(Post($"/profiles/{profileId}/verification",
            new { level, attestor, method = "document" }, token));

    public Task<VerificationCard> MoveBadgeHere(string profileId,
        string token) =>
        Send<VerificationCard>(Post(
            $"/profiles/{profileId}/verification/move", new { }, token));

    public Task<VerifiableOut> VerifiableOf(string profileId,
        string token) =>
        Send<VerifiableOut>(Get($"/profiles/{profileId}/verifiable",
            token));

    public Task<ProfilePatched> EditProfile(string profileId,
        string displayName, string persona, string token)
    {
        var body = new System.Collections.Generic.Dictionary<string, string>();
        if (displayName.Length > 0) body["display_name"] = displayName;
        if (persona.Length > 0) body["persona"] = persona;
        var req = new HttpRequestMessage(HttpMethod.Patch,
            $"/profiles/{profileId}")
        { Content = JsonContent.Create(body) };
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<ProfilePatched>(req);
    }

    public Task<SunsetOut> Sunset(string profileId, string token) =>
        Send<SunsetOut>(Post($"/profiles/{profileId}/sunset", new { },
            token));

    /// <summary>Public memorial for a departed profile — never persona
    /// internals.</summary>
    public Task<MemorialCard> MemorialOf(string profileId) =>
        Send<MemorialCard>(Get($"/profiles/{profileId}/memorial"));

    public Task<RosterOut> Siblings(string profileId, string token) =>
        Send<RosterOut>(Get($"/profiles/{profileId}/siblings", token));

    public Task<SucceedOut> Succeed(string profileId,
        string verificationRef, string token) =>
        Send<SucceedOut>(Post($"/profiles/{profileId}/succeed",
            new { verification_ref = verificationRef }, token));

    public Task<SucceedOut> DeleteProfile(string profileId, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
            $"/profiles/{profileId}");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<SucceedOut>(req);
    }

    // -- the face it shows the world: portrait, emblem, page, front,
    // surfaces, blend, bodies, dials and the wrist -----------------------

    /// <summary>Public: the portrait as it must be displayed — asset, AI
    /// badge, and whose likeness it is.</summary>
    public Task<AvatarCard> AvatarOf(string profileId) =>
        Send<AvatarCard>(Get($"/profiles/{profileId}/avatar"));

    public Task<AvatarCard> SetAvatar(string profileId, string asset,
        string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Put,
            $"/profiles/{profileId}/avatar")
        { Content = JsonContent.Create(new { asset }) };
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<AvatarCard>(req);
    }

    public record MarketSource(string Key, string Name, string How);
    public record MarketShelf(MarketSource[] Sources, string Note);

    public Task<MarketShelf> AvatarMarket() =>
        Send<MarketShelf>(Get("/avatars/market"));

    public Task<AvatarCard> ImportAvatar(string profileId, string source,
        string asset, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Post,
            $"/profiles/{profileId}/avatar/import")
        { Content = JsonContent.Create(new { source, asset }) };
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<AvatarCard>(req);
    }

    public Task<BriefCatalog> AvatarBriefs() =>
        Send<BriefCatalog>(Get("/avatars/briefs"));

    public Task<BriefCard> AvatarBrief(string handle) =>
        Send<BriefCard>(Get($"/avatars/briefs/{handle}"));

    public Task<EmblemCatalog> IdentityEmblems() =>
        Send<EmblemCatalog>(Get("/identity/emblems"));

    public Task<IdentityVocabulary> IdentityVocabularyOf() =>
        Send<IdentityVocabulary>(Get("/identity/vocabulary"));

    public Task<EmblemOut> SetEmblem(string profileId, string emblem,
        string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Put,
            $"/profiles/{profileId}/emblem")
        { Content = JsonContent.Create(new { emblem }) };
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<EmblemOut>(req);
    }

    /// <summary>Public, and not the same read as /verification: on an
    /// anonymous profile the attestor is withheld.</summary>
    public Task<BadgeCard> BadgeOf(string profileId) =>
        Send<BadgeCard>(Get($"/profiles/{profileId}/badge"));

    public Task<ThemeCatalog> PageThemes() =>
        Send<ThemeCatalog>(Get("/pages/themes"));

    public Task<PageCard> PageOf(string profileId) =>
        Send<PageCard>(Get($"/profiles/{profileId}/page"));

    public Task<PageCard> EditPage(string profileId, string theme,
        string tagline, string about, string token)
    {
        var body = new System.Collections.Generic.Dictionary<string, string>();
        if (theme.Length > 0) body["theme"] = theme;
        if (tagline.Length > 0) body["tagline"] = tagline;
        if (about.Length > 0) body["about"] = about;
        var req = new HttpRequestMessage(HttpMethod.Put,
            $"/profiles/{profileId}/page")
        { Content = JsonContent.Create(body) };
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<PageCard>(req);
    }

    /// <summary>Everything a visitor's first screen needs, in one
    /// call.</summary>
    public Task<FrontCard> FrontPage(string profileId) =>
        Send<FrontCard>(Get($"/profiles/{profileId}/front"));

    public Task<SurfacesCard> SurfacesOf(string profileId) =>
        Send<SurfacesCard>(Get($"/profiles/{profileId}/surfaces"));

    public Task<SurfacesCard> SetSurfaces(string profileId,
        string[] surfaces, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Put,
            $"/profiles/{profileId}/surfaces")
        { Content = JsonContent.Create(new { surfaces }) };
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<SurfacesCard>(req);
    }

    /// <summary>Public, the same open stance as /transparency: the blend
    /// is the profile's provenance.</summary>
    public Task<CompositionCard> CompositionOf(string profileId) =>
        Send<CompositionCard>(Get($"/profiles/{profileId}/composition"));

    public Task<EmbodimentRow[]> Embodiments(string profileId,
        string token) =>
        Send<EmbodimentRow[]>(Get($"/profiles/{profileId}/embodiments",
            token));

    public Task<EmbodimentRow> AddEmbodiment(string profileId, string name,
        string kind, string token) =>
        Send<EmbodimentRow>(Post($"/profiles/{profileId}/embodiments",
            new { name, kind, has_llm = false }, token));

    /// <summary>Public: anyone meeting the profile through any form can
    /// verify it is the same personality.</summary>
    public Task<ConsistencyCard> EmbodimentConsistency(string profileId) =>
        Send<ConsistencyCard>(Get(
            $"/profiles/{profileId}/embodiment-consistency"));

    public Task<ProfileDisplayList> ProfileDisplays(string profileId,
        string token) =>
        Send<ProfileDisplayList>(Get($"/profiles/{profileId}/displays",
            token));

    public Task<ProfileDisplayRow> AddProfileDisplay(string profileId,
        string kind, string label, string token) =>
        Send<ProfileDisplayRow>(Post($"/profiles/{profileId}/displays",
            new { kind, label }, token));

    public Task<SteeringCard> SteeringOf(string profileId, string token) =>
        Send<SteeringCard>(Get($"/profiles/{profileId}/steering", token));

    /// <summary>Dials are 0–100 integers. Intimacy can never be raised on
    /// a non-rated persona.</summary>
    public Task<SteeringCard> SetSteering(string profileId,
        System.Collections.Generic.Dictionary<string, int> values,
        string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Put,
            $"/profiles/{profileId}/steering")
        { Content = JsonContent.Create(new { values }) };
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<SteeringCard>(req);
    }

    public Task<WatchFaceCard> WatchFace(string profileId, string token) =>
        Send<WatchFaceCard>(Get($"/profiles/{profileId}/watch", token));

    public Task<WatchActOut> WatchAct(string profileId, string target,
        string targetId, string action, string input, string token)
    {
        var body = new System.Collections.Generic.Dictionary<string, string>
        { ["target"] = target, ["id"] = targetId, ["action"] = action };
        if (input.Length > 0) body["input"] = input;
        return Send<WatchActOut>(Post($"/profiles/{profileId}/watch/act",
            body, token));
    }

    // -- The keys: the account itself --

    public Task<SignupOut> Signup(string email, string password,
        string name)
    {
        var body = new System.Collections.Generic.Dictionary<string, string>
        { ["email"] = email, ["password"] = password };
        if (name.Length > 0) body["display_name"] = name;
        return Send<SignupOut>(Post("/signup", body));
    }

    /// <summary>Unknown address and wrong password get the same answer;
    /// an unverified address cannot sign in at all.</summary>
    public Task<SessionOut> Signin(string email, string password) =>
        Send<SessionOut>(Post("/signin", new { email, password }));

    public Task<SessionOut> VerifyEmail(string email, string code) =>
        Send<SessionOut>(Post("/verify-email", new { email, code }));

    /// <summary>Not an address oracle: same answer either way.</summary>
    public Task<CodeDeliveryOut> ResendCode(string email) =>
        Send<CodeDeliveryOut>(Post("/verify-email/resend", new { email }));

    public Task<CodeDeliveryOut> RequestPasswordReset(string email) =>
        Send<CodeDeliveryOut>(Post("/password/reset/request",
            new { email }));

    /// <summary>Every existing account session dies with the old
    /// password.</summary>
    public Task<ResetOut> ResetPassword(string email, string code,
        string newPassword) =>
        Send<ResetOut>(Post("/password/reset",
            new System.Collections.Generic.Dictionary<string, string>
            { ["email"] = email, ["code"] = code,
              ["new_password"] = newPassword }));

    public Task<OAuthProviderList> OAuthProviders() =>
        Send<OAuthProviderList>(Get("/auth/oauth/providers"));

    public Task<OAuthStartOut> OAuthStart(string provider) =>
        Send<OAuthStartOut>(Post($"/auth/oauth/{provider}/start",
            new { }));

    /// <summary>One-time pickup; the first successful claim spends the
    /// state.</summary>
    public Task<OAuthClaimOut> OAuthClaim(string state) =>
        Send<OAuthClaimOut>(Get("/auth/oauth/claim?state=" +
            Uri.EscapeDataString(state)));

    // -- The till --

    /// <summary>Public: the terms are readable before any sign-in.</summary>
    public Task<PlanCatalog> Plans() => Send<PlanCatalog>(Get("/plans"));

    public Task<SubscriptionList> MySubscriptions(string token) =>
        Send<SubscriptionList>(Get("/subscriptions", token));

    /// <summary>Explicit on purpose: nothing bills on a timer.</summary>
    public Task<SubscriptionRow> RenewSubscription(string subId,
        string beneficiary, string token) =>
        Send<SubscriptionRow>(Post($"/subscriptions/{subId}/renew",
            new { beneficiary }, token));

    public Task<OrderList> MyOrders(string token) =>
        Send<OrderList>(Get("/orders", token));

    /// <summary>Public: a donor gives to the names on this list, not the
    /// platform.</summary>
    public Task<ProceedsCard> ProceedsOf(string profileId) =>
        Send<ProceedsCard>(Get($"/profiles/{profileId}/proceeds"));

    public Task<ProceedsCard> SetProceeds(string profileId, string designee,
        string token)
    {
        var d = new System.Collections.Generic.Dictionary<string, object>
        { ["name"] = designee, ["kind"] = "loved_one", ["share"] = 100 };
        var req = new HttpRequestMessage(HttpMethod.Put,
            $"/profiles/{profileId}/proceeds")
        { Content = JsonContent.Create(new { designees = new[] { d } }) };
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<ProceedsCard>(req);
    }

    public Task<CampaignRow[]> CampaignsOf(string profileId) =>
        Send<CampaignRow[]>(Get($"/profiles/{profileId}/campaigns"));

    public Task<CampaignRow> AddCampaign(string profileId, string title,
        double goal, string token) =>
        Send<CampaignRow>(Post($"/profiles/{profileId}/campaigns",
            new { title, goal }, token));

    // -- The lifeline --

    public Task<CloudStatusCard> CloudStatus() =>
        Send<CloudStatusCard>(Get("/cloud/status"));

    public Task<OfflineStatusCard> OfflineStatus() =>
        Send<OfflineStatusCard>(Get("/offline/status"));

    /// <summary>The legend is built from the mapping the code has.</summary>
    public Task<LightsLegend> AgentLights() =>
        Send<LightsLegend>(Get("/agent/lights"));

    public Task<HelpTopicList> HelpTopics() =>
        Send<HelpTopicList>(Get("/help/topics"));

    /// <summary>Public on purpose, and it writes nothing.</summary>
    public Task<HelpAnswer> AskHelp(string question) =>
        Send<HelpAnswer>(Post("/help", new { question }));

    public Task<LocalProviderRow[]> LocalProviders() =>
        Send<LocalProviderRow[]>(Get("/providers"));

    public Task<LocalProviderRow> AddLocalProvider(string name,
        string area) =>
        Send<LocalProviderRow>(Post("/providers",
            new { name, area, business = true }));

    // -- The public stream --

    /// <summary>One page of the public stream. No token: somebody who
    /// followed a shared link is a reader like any other.</summary>
    /// <remarks><c>plays</c> is the server's and is never recomputed here.
    /// Only footage this deployment holds comes back true, so scrolling past
    /// an off-site card makes no request to another company's server.</remarks>
    public Task<FeedPage> PublicFeed(string? cursor = null) =>
        Send<FeedPage>(Get(string.IsNullOrEmpty(cursor)
            ? "/feed?limit=12"
            : $"/feed?limit=12&cursor={cursor}"));

    /// <summary>One card, for a link somebody was sent. A rated item a
    /// reader is not verified for answers 404 rather than an empty card: a
    /// 403 would announce that it exists.</summary>
    public Task<FeedCard> FeedItem(string itemId) =>
        Send<FeedCard>(Get($"/feed/{itemId}"));

    // -- The sticker on the street --

    /// <summary>The overlay's read: never the face without the
    /// disclosure.</summary>
    public Task<BeaconOverlayCard> BeaconCard(string beaconId) =>
        Send<BeaconOverlayCard>(Get($"/b/{beaconId}/card"));

    public string BeaconScanUrl(string beaconId) =>
        Get($"/b/{beaconId}").RequestUri!.ToString();

    public string BeaconQrUrl(string beaconId) =>
        Get($"/beacons/{beaconId}/qr.svg").RequestUri!.ToString();

    public Task<DeskScanCard> DeskScanCard(string beaconId) =>
        Send<DeskScanCard>(Get($"/d/{beaconId}/card"));

    public string DeskScanUrl(string beaconId) =>
        Get($"/d/{beaconId}").RequestUri!.ToString();

    public Task<SocialBeaconCard> SocialBeacon(string cid) =>
        Send<SocialBeaconCard>(Get($"/social/{cid}/beacon"));

    public string SocialQrUrl(string cid) =>
        Get($"/social/{cid}/qr.svg").RequestUri!.ToString();

    /// <summary>Same Wi-Fi, no app store.</summary>
    public Task<PairCard> Pairing() => Send<PairCard>(Get("/pair"));

    public string PairQrUrl() => Get("/pair/qr.svg").RequestUri!.ToString();

    // -- The queue --

    public Task<HeldMessage[]> ModerationQueue(string profileId,
        string token) =>
        Send<HeldMessage[]>(Get($"/profiles/{profileId}/moderation/queue",
            token));

    public Task<ModerationOut> ApproveMessage(string messageId,
        string token) =>
        Send<ModerationOut>(Post($"/moderation/{messageId}/approve",
            new { }, token));

    public Task<ModerationOut> RejectMessage(string messageId,
        string token) =>
        Send<ModerationOut>(Post($"/moderation/{messageId}/reject",
            new { }, token));

    /// <summary>Moderated as a fresh message, and it carries
    /// forward.</summary>
    public Task<ModerationOut> EditMessage(string profileId,
        string messageId, string interactorId, string content, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Patch,
            $"/profiles/{profileId}/messages/{messageId}")
        { Content = JsonContent.Create(new
            { interactor_id = interactorId, content }) };
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<ModerationOut>(req);
    }

    /// <summary>The row survives for the trail; the text stops being
    /// shown.</summary>
    public Task<ModerationOut> RetractMessage(string profileId,
        string messageId, string interactorId, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
            $"/profiles/{profileId}/messages/{messageId}")
        { Content = JsonContent.Create(new
            { interactor_id = interactorId }) };
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<ModerationOut>(req);
    }

    // -- The reviews --

    public Task<ReviewBoard> ReviewsOf(string profileId) =>
        Send<ReviewBoard>(Get($"/profiles/{profileId}/reviews"));

    /// <summary>One per interactor, edited rather than stacked.</summary>
    public Task<ReviewOut> LeaveReview(string profileId,
        string interactorId, int rating, string body, string token)
    {
        var payload = new System.Collections.Generic
            .Dictionary<string, object>
        { ["interactor_id"] = interactorId, ["rating"] = rating };
        if (body.Length > 0) payload["body"] = body;
        return Send<ReviewOut>(Post($"/profiles/{profileId}/reviews",
            payload, token));
    }

    // -- The stamp --

    public Task<WatermarkCredential> WatermarkCredentialOf(
        string watermarkId) =>
        Send<WatermarkCredential>(Get($"/watermarks/{watermarkId}"));

    /// <summary>Valid + whether the presented content still matches the
    /// hash issued at creation.</summary>
    public Task<WatermarkCredential> VerifyWatermark(string watermarkId,
        string content)
    {
        var payload = new System.Collections.Generic
            .Dictionary<string, object>
        { ["watermark_id"] = watermarkId };
        if (content.Length > 0) payload["content"] = content;
        return Send<WatermarkCredential>(Post("/watermarks/verify",
            payload));
    }

    // -- The media --

    public Task<MediaLimitsCard> MediaLimits() =>
        Send<MediaLimitsCard>(Get("/media/limits"));

    /// <summary>Raw bytes in the body; the kind is read from the
    /// bytes.</summary>
    public async Task<MediaOut> UploadMedia(string profileId,
        string filename, byte[] bytes, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Post,
            $"/profiles/{profileId}/media?filename=" +
            Uri.EscapeDataString(filename))
        { Content = new ByteArrayContent(bytes) };
        req.Headers.Add("authorization", $"Bearer {token}");
        return await Send<MediaOut>(req);
    }

    public Task<VideoPlatformBoard> VideoPlatforms() =>
        Send<VideoPlatformBoard>(Get("/videos/platforms"));

    // -- The wearables --

    /// <summary>A paired device is a screen and a set of buttons.</summary>
    public Task<WearableBoard> Wearables(string profileId, string token) =>
        Send<WearableBoard>(Get($"/profiles/{profileId}/wearables", token));

    public Task<WearableRow> PairWearable(string profileId, string name,
        string kind, string token) =>
        Send<WearableRow>(Post($"/profiles/{profileId}/wearables",
            new { name, kind }, token));

    /// <summary>The record survives, so a lost watch cannot come back by
    /// name.</summary>
    public Task<WearableRow> UnpairWearable(string profileId, string name,
        string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
            $"/profiles/{profileId}/wearables/{name}");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<WearableRow>(req);
    }

    // -- The birth --

    /// <summary>The short interview a profile is born from.</summary>
    public Task<GenesisOut> Genesis(string ownerId, string name,
        string social, string humor, string matters, string comfort)
    {
        var body = new System.Collections.Generic.Dictionary<string, object>
        {
            ["owner_id"] = ownerId,
            ["verification"] = new System.Collections.Generic
                .Dictionary<string, string> { ["birthdate"] = "1990-01-01" },
            ["answers"] = new System.Collections.Generic
                .Dictionary<string, string>
            { ["social_style"] = social, ["humor"] = humor,
              ["what_matters"] = matters, ["comfort"] = comfort },
        };
        if (name.Length > 0) body["display_name"] = name;
        return Send<GenesisOut>(Post("/profiles/genesis", body));
    }

    /// <summary>A hybrid blended from several profiles; the blend is
    /// recorded per-constituent.</summary>
    public Task<GenesisOut> Composite(string ownerId, string name,
        string[] sources) =>
        Send<GenesisOut>(Post("/profiles/composite", new
        {
            owner_id = ownerId, display_name = name, terms_consent = true,
            verification = new { birthdate = "1990-01-01" },
            sources = sources.Select(sid => new { profile_id = sid })
                .ToArray(),
        }));

    public Task<PackOut> PublishPack(string industry, string title,
        string token) =>
        Send<PackOut>(Post("/packs", new { industry, title,
            items = new[] { new { title, content = title } } },
            token));

    /// <summary>One free Field Pack per industry.</summary>
    public Task<PackSeedOut> SeedPacks() =>
        Send<PackSeedOut>(Post("/packs/seed", new { }));

    // -- The mind at work --

    /// <summary>Owner-only; the narrative is watermarked synthetic.</summary>
    public Task<SimulationOut> Simulate(string profileId, string scenario,
        string token) =>
        Send<SimulationOut>(Post($"/profiles/{profileId}/simulate",
            new { scenario }, token));

    public Task<SimulationOut[]> Simulations(string profileId,
        string token) =>
        Send<SimulationOut[]>(Get($"/profiles/{profileId}/simulations",
            token));

    public Task<FinetuneOut> Finetune(string profileId, string token) =>
        Send<FinetuneOut>(Post($"/profiles/{profileId}/finetune",
            new { }, token));

    /// <summary>Exactly what would leave, and the log of what already
    /// has.</summary>
    public Task<ContributionView> CloudContribution(string profileId,
        string token) =>
        Send<ContributionView>(Get(
            $"/profiles/{profileId}/cloud-contribution", token));

    /// <summary>Off, and everything already contributed deleted.</summary>
    public Task<RevokeOut> RevokeContributions(string profileId,
        string token) =>
        Send<RevokeOut>(Post(
            $"/profiles/{profileId}/cloud-contribution/revoke",
            new { }, token));

    public Task<ExcursionOut> Excursion(string cid, string token) =>
        Send<ExcursionOut>(Get($"/excursions/{cid}", token));

    // -- The reach --

    /// <summary>Allowed only when the owner opted in with proactive
    /// scope.</summary>
    public Task<CheckinOut> ProactiveCheckin(string profileId,
        string interactorId, string token) =>
        Send<CheckinOut>(Post(
            $"/profiles/{profileId}/proactive/{interactorId}",
            new { }, token));

    /// <summary>The recipient's own window.</summary>
    public Task<QuietHoursOut> SetQuietHours(string interactorId,
        int? start, int? end, string token)
    {
        var body = new System.Collections.Generic
            .Dictionary<string, object>();
        if (start is not null) body["quiet_start"] = start;
        if (end is not null) body["quiet_end"] = end;
        var req = new HttpRequestMessage(HttpMethod.Put,
            $"/interactors/{interactorId}/quiet-hours")
        { Content = JsonContent.Create(body) };
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<QuietHoursOut>(req);
    }

    /// <summary>From the person who is rating — never in somebody
    /// else's name.</summary>
    public Task<FeedbackOut> GiveFeedback(string profileId,
        string interactorId, string rating, string token) =>
        Send<FeedbackOut>(Post(
            $"/profiles/{profileId}/interactions/{interactorId}/feedback",
            new { rating }, token));

    public Task<ReferralRow[]> MyReferrals(string interactorId,
        string token) =>
        Send<ReferralRow[]>(Get($"/interactors/{interactorId}/referrals",
            token));

    // -- The license --

    public Task<LicenseGrantOut> AcquireLicense(string profileId,
        string token) =>
        Send<LicenseGrantOut>(Post($"/profiles/{profileId}/license/acquire",
            new { }, token));

    /// <summary>The derived agent records its origin.</summary>
    public Task<GenesisOut> DeriveAgent(string profileId, string grantId,
        string token) =>
        Send<GenesisOut>(Post(
            $"/profiles/{profileId}/license/{grantId}/derive",
            new { }, token));

    // -- The senses --

    /// <summary>Hands-free guidance from what the camera recognises.</summary>
    public Task<PerceiveOut> Perceive(string profileId, string[] objects,
        string goal, string token)
    {
        var body = new System.Collections.Generic
            .Dictionary<string, object> { ["objects"] = objects };
        if (goal.Length > 0) body["goal"] = goal;
        return Send<PerceiveOut>(Post($"/profiles/{profileId}/perceive",
            body, token));
    }

    public Task<MicPlacesOut> MicrophonePlaces() =>
        Send<MicPlacesOut>(Get("/microphones/places"));

    public Task<MicVocabularyOut> MicrophoneVocabulary() =>
        Send<MicVocabularyOut>(Get("/microphones/vocabulary"));

    public Task<OverlayCatalogue> OverlaysCatalogue() =>
        Send<OverlayCatalogue>(Get("/overlays/catalogue"));

    /// <summary>The whole list, replaced wholesale — a CV is a
    /// statement.</summary>
    public Task<ExperienceOut> SetExperience(string profileId, string title,
        string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Put,
            $"/profiles/{profileId}/experience")
        { Content = JsonContent.Create(new
            { entries = new[] { new { title } } }) };
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<ExperienceOut>(req);
    }

    // -- Doors the other shells already had --

    public Task<HealthOut> Health() => Send<HealthOut>(Get("/health"));

    /// <summary>Retire a signing credential.</summary>
    public Task<RemovedOut> RemoveSigningCredential(string rowId,
        string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
            $"/signatures/credentials/{rowId}");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<RemovedOut>(req);
    }

    /// <summary>Join the live stream whoever is watching shares.</summary>
    public Task<DeskJoinOut> JoinDeskStream(string deskId, string token) =>
        Send<DeskJoinOut>(Post($"/desks/{deskId}/join", new { }, token));

    // -- the people around a profile: friends, the wall, comments --
    // Nine routes the backend has carried since the community round; this
    // shell is the last client to get a door for them.

    public async Task<FriendRow[]> Friends(string profileId)
    {
        var box = await Send<FriendListBox>(Get($"/profiles/{profileId}/friends"));
        return box.Friends;
    }

    /// <summary>The deed, never the words: a row names the kind and the
    /// actor; the sentence for each kind is this shell's, from L10n.</summary>
    public Task<InboxPage> Inbox(string profileId, string token) =>
        Send<InboxPage>(Get($"/profiles/{profileId}/inbox", token));

    public Task<InboxSeen> MarkInboxSeen(string profileId, string token) =>
        Send<InboxSeen>(Post($"/profiles/{profileId}/inbox/seen",
            new { }, token));

    public async Task<SuggestedRow[]> SuggestedFriends(string profileId)
    {
        var box = await Send<SuggestedBox>(
            Get($"/profiles/{profileId}/friends/suggested"));
        return box.Suggested;
    }

    public Task<FriendAdded> AddFriend(string profileId, string friendId,
                                       string token) =>
        Send<FriendAdded>(Post($"/profiles/{profileId}/friends",
            new { friend_id = friendId }, token));

    /// <summary>Pinned rows refuse with 409; the list marks them so the
    /// control is left off rather than offered and failing.</summary>
    public Task<FriendAdded> RemoveFriend(string profileId, string friendId,
                                          string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
            $"/profiles/{profileId}/friends/{friendId}");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<FriendAdded>(req);
    }

    // -- the crowd, the couch and the loan --------------------------------
    // Audience verbs, the watch party, and skill grants: three blocks the
    // doorless records said this shell could not reach.

    public Task<LikeOut> Like(string kind, string targetId, string token) =>
        Send<LikeOut>(Post($"/{kind}/{targetId}/like", new { }, token));

    public Task<LikeOut> Unlike(string kind, string targetId, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
            $"/{kind}/{targetId}/like");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<LikeOut>(req);
    }

    public Task<ShareOut> Share(string kind, string targetId, string token) =>
        Send<ShareOut>(Post($"/{kind}/{targetId}/share",
            new { channel = "link" }, token));

    public Task<AudienceCounts> AudienceOf(string kind, string targetId,
                                           string token) =>
        Send<AudienceCounts>(Get($"/{kind}/{targetId}/audience", token));

    public Task<SubscribeOut> Subscribe(string kind, string subjectId,
                                        string token) =>
        Send<SubscribeOut>(Post($"/{kind}/{subjectId}/subscribe",
            new { tier = "follow" }, token));

    public Task<SubscribeOut> Unsubscribe(string kind, string subjectId,
                                          string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
            $"/{kind}/{subjectId}/subscribe");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<SubscribeOut>(req);
    }

    public Task<SubscriberBox> Subscribers(string kind, string subjectId,
                                           string token) =>
        Send<SubscriberBox>(Get($"/{kind}/{subjectId}/subscribers", token));

    /// <summary>A gift is a gift — the backend refuses to reverse it, and
    /// requires the giver to be a verified adult.</summary>
    public Task<GiftRow> Gift(string kind, string subjectId, double amount,
                              string note, string token) =>
        Send<GiftRow>(Post($"/{kind}/{subjectId}/gift",
            new { amount, note }, token));

    public Task<GiftBox> Gifts(string kind, string subjectId, string token) =>
        Send<GiftBox>(Get($"/{kind}/{subjectId}/gifts", token));

    public Task<PartyCard> StartParty(string postId, string hostId,
                                      string title, string token) =>
        Send<PartyCard>(Post("/watch-parties",
            new { post_id = postId, host_id = hostId, title }, token));

    public Task<PartyCard> Party(string partyId, string token) =>
        Send<PartyCard>(Get($"/watch-parties/{partyId}", token));

    public Task<PartyCard> JoinParty(string partyId, string memberId,
                                     string token) =>
        Send<PartyCard>(Post($"/watch-parties/{partyId}/members",
            new { member_id = memberId, kind = "profile" }, token));

    public Task<LeaveOut> LeaveParty(string partyId, string memberId,
                                     string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
            $"/watch-parties/{partyId}/members/{memberId}");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<LeaveOut>(req);
    }

    /// <summary>Moves a number; presses play on nobody's device.</summary>
    public Task<PartyCard> SeekParty(string partyId, string hostId,
                                     int positionS, string token) =>
        Send<PartyCard>(Post($"/watch-parties/{partyId}/seek",
            new { host_id = hostId, position_s = positionS, playing = true },
            token));

    public Task<PartyLine> SayInParty(string partyId, string memberId,
                                      string body, string token) =>
        Send<PartyLine>(Post($"/watch-parties/{partyId}/chat",
            new { member_id = memberId, body }, token));

    public Task<PartyChatBox> PartyChat(string partyId, string token) =>
        Send<PartyChatBox>(Get($"/watch-parties/{partyId}/chat", token));

    public Task<PartyCard> EndParty(string partyId, string token) =>
        Send<PartyCard>(Post($"/watch-parties/{partyId}/end", new { },
            token));

    /// <summary>The sentence a synthetic member carries: it has not seen
    /// the footage.</summary>
    public Task<PartyContext> PartyContextOf(string partyId, string token) =>
        Send<PartyContext>(Get($"/watch-parties/{partyId}/context", token));

    public Task<GrantVocabulary> GrantVocabulary() =>
        Send<GrantVocabulary>(Get("/skill-grants/vocabulary"));

    public Task<GrantCard> OfferGrant(string lenderId, string borrowerId,
                                      string surface, string surfaceId,
                                      string skillKind, string skillRef,
                                      string title, string token) =>
        Send<GrantCard>(Post("/skill-grants", new
        {
            lender_id = lenderId, borrower_id = borrowerId, surface,
            surface_id = surfaceId, skill_kind = skillKind,
            skill_ref = skillRef, title
        }, token));

    public Task<GrantCard> Grant(string grantId, string token) =>
        Send<GrantCard>(Get($"/skill-grants/{grantId}", token));

    public Task<GrantCard> AcceptGrant(string grantId, string actorId,
                                       string token) =>
        Send<GrantCard>(Post($"/skill-grants/{grantId}/accept",
            new { actor_id = actorId }, token));

    public Task<GrantCard> DeclineGrant(string grantId, string actorId,
                                        string token) =>
        Send<GrantCard>(Post($"/skill-grants/{grantId}/decline",
            new { actor_id = actorId }, token));

    public Task<GrantCard> CloseGrant(string grantId, string actorId,
                                      string token) =>
        Send<GrantCard>(Post($"/skill-grants/{grantId}/close",
            new { actor_id = actorId }, token));

    public Task<GrantUse> UseGrant(string grantId, string borrowerId,
                                   string what, string token) =>
        Send<GrantUse>(Post($"/skill-grants/{grantId}/use",
            new { borrower_id = borrowerId, what }, token));

    public Task<GrantUseBox> GrantUses(string grantId, string token) =>
        Send<GrantUseBox>(Get($"/skill-grants/{grantId}/uses", token));

    public Task<GrantBox> GrantsInSurface(string surface, string surfaceId,
                                          string token) =>
        Send<GrantBox>(Get($"/surfaces/{surface}/{surfaceId}/skill-grants",
            token));

    public Task<MyGrants> MyGrants(string personId, string token) =>
        Send<MyGrants>(Get($"/people/{personId}/skill-grants", token));

    // -- the place, the camera, the organization and the tour -------------
    // Four more blocks off the doorless records. Disclosure-first: who
    // here has lent a microphone and who wears what are readable by
    // everyone present.

    public Task<WhoseCard> Whose(string surface, string surfaceId) =>
        Send<WhoseCard>(Get($"/places/{surface}/{surfaceId}/whose"));

    public Task<MicDisclosure> LendMicrophone(string surface,
        string surfaceId, string interactorId, string token) =>
        Send<MicDisclosure>(Post($"/places/{surface}/{surfaceId}/microphone",
            new { interactor_id = interactorId }, token));

    public Task<MicDisclosure> TakeBackMicrophone(string surface,
        string surfaceId, string interactorId, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
            $"/places/{surface}/{surfaceId}/microphone")
        { Content = JsonContent.Create(new { interactor_id = interactorId }) };
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<MicDisclosure>(req);
    }

    public Task<MicDisclosure> MicrophoneDisclosure(string surface,
        string surfaceId, string token) =>
        Send<MicDisclosure>(Get($"/places/{surface}/{surfaceId}/microphone",
            token));

    public Task<WornRow> WearOverlay(string surface, string surfaceId,
        string interactorId, string kind, string title, string token) =>
        Send<WornRow>(Post($"/places/{surface}/{surfaceId}/overlay",
            new { interactor_id = interactorId, kind, title }, token));

    public Task<WornRow> TakeOffOverlay(string surface, string surfaceId,
        string interactorId, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
            $"/places/{surface}/{surfaceId}/overlay")
        { Content = JsonContent.Create(new { interactor_id = interactorId }) };
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<WornRow>(req);
    }

    public Task<WornDisclosure> WornOverlays(string surface, string surfaceId,
        string token) =>
        Send<WornDisclosure>(Get($"/places/{surface}/{surfaceId}/overlay",
            token));

    /// <summary>The published refusals, verbatim — a refused combination
    /// is a decision, not a missing feature.</summary>
    public Task<CameraVocabulary> CameraVocabulary() =>
        Send<CameraVocabulary>(Get("/camera/vocabulary"));

    public Task<BystanderNote> BystanderGuidance(string subject) =>
        Send<BystanderNote>(Get($"/camera/bystanders/{subject}"));

    public Task<CameraSession> OpenCamera(string holderId, string surface,
        string surfaceId, string subject, string viewerId, int minutes,
        string token) =>
        Send<CameraSession>(Post("/camera/sessions", new
        {
            holder_id = holderId, surface, surface_id = surfaceId, subject,
            viewer_kind = "person", viewer_id = viewerId, minutes
        }, token));

    public Task<CameraSession> CameraSessionOf(string sessionId,
        string token) =>
        Send<CameraSession>(Get($"/camera/sessions/{sessionId}", token));

    public Task<CameraSession> CloseCamera(string sessionId, string actorId,
        string token) =>
        Send<CameraSession>(Post($"/camera/sessions/{sessionId}/close",
            new { actor_id = actorId }, token));

    public Task<CameraSession[]> MyCameras(string holderId, string token) =>
        Send<CameraSession[]>(Get($"/camera/live/{holderId}", token));

    public Task<CameraDisclosure> CameraDisclosureOf(string surface,
        string surfaceId, string token) =>
        Send<CameraDisclosure>(Get(
            $"/camera/disclosure/{surface}/{surfaceId}", token));

    public Task<OrgCard[]> Organizations(string token) =>
        Send<OrgCard[]>(Get("/organizations", token));

    public Task<OrgCard> CreateOrganization(string name, string token) =>
        Send<OrgCard>(Post("/organizations", new { name }, token));

    public Task<OrgCard> SeedDemoOrganization(string token) =>
        Send<OrgCard>(Post("/organizations/demo", new { }, token));

    public Task<OrgCard> OrganizationOf(string orgId, string token) =>
        Send<OrgCard>(Get($"/organizations/{orgId}", token));

    public Task<OrgDepartment> AddDepartment(string orgId, string name,
        string role, string profileId, string token) =>
        Send<OrgDepartment>(Post($"/organizations/{orgId}/departments",
            new { name, role, profile_id = profileId }, token));

    /// <summary>AI for lease: seat somebody else's licensed specialist as a
    /// department; the fee accrues to its owner, who can revoke any time.
    /// </summary>
    public Task<LeaseOut> LeaseSpecialist(string orgId, string profileId,
        string name, string role, string token) =>
        Send<LeaseOut>(Post($"/organizations/{orgId}/lease",
            new { profile_id = profileId, name, role }, token));

    public Task<Coordination> Coordinate(string orgId, string goal,
        string fromDepartment, string token) =>
        Send<Coordination>(Post($"/organizations/{orgId}/coordinate",
            new { goal, from_department = fromDepartment }, token));

    public Task<Coordination[]> Coordinations(string orgId, string token) =>
        Send<Coordination[]>(Get($"/organizations/{orgId}/coordinations",
            token));

    public Task<TutorialOutline> TutorialOutline() =>
        Send<TutorialOutline>(Get("/tutorial"));

    public Task<TutorialStep> TutorialStepOf(string key) =>
        Send<TutorialStep>(Get($"/tutorial/steps/{key}"));

    public Task<TutorialStep> TutorialForScreen(int number) =>
        Send<TutorialStep>(Get($"/tutorial/for-screen/{number}"));

    public Task<TutorialProgress> StartTutorial(string learnerId) =>
        Send<TutorialProgress>(Post("/tutorial/start",
            new { learner_id = learnerId, lesson = "" }));

    /// <summary>Progress wraps the step — a learner id and where they are —
    /// rather than being one, which is why this does not decode as a
    /// <see cref="TutorialStep"/>.</summary>
    public Task<TutorialProgress> TutorialProgress(string learnerId) =>
        Send<TutorialProgress>(Get($"/tutorial/progress/{learnerId}"));

    public Task<TutorialProgress> MarkTutorialDone(string learnerId,
        string lesson) =>
        Send<TutorialProgress>(Post("/tutorial/done",
            new { learner_id = learnerId, lesson }));

    // -- the body, the referral, the objection, the lobby and the dock ----
    // Five more blocks off the doorless records, each rendering its
    // backend's rules rather than inventing a sixth opinion.

    public Task<RobotUnbound> UnbindRobot(string robotId, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
            $"/robots/{robotId}");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<RobotUnbound>(req);
    }

    /// <summary>Owner-only audit: everything this body has been told to
    /// do.</summary>
    public Task<RobotCommandRow[]> RobotCommands(string robotId,
        string token) =>
        Send<RobotCommandRow[]>(Get($"/robots/{robotId}/commands", token));

    public Task<RobotSkillRow[]> RobotSkills(string robotId, string token) =>
        Send<RobotSkillRow[]>(Get($"/robots/{robotId}/skills", token));

    /// <summary>A body's dials — intimacy never applies to a body.</summary>
    public Task<RobotSteering> RobotSteeringOf(string robotId,
        string token) =>
        Send<RobotSteering>(Get($"/robots/{robotId}/steering", token));

    public Task<RobotSteering> SteerRobot(string robotId, int pace,
        string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Put,
            $"/robots/{robotId}/steering")
        {
            Content = JsonContent.Create(new
            {
                values = new System.Collections.Generic
                    .Dictionary<string, int> { ["pace"] = pace }
            })
        };
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<RobotSteering>(req);
    }

    public Task<ClinicianRow[]> MatchClinicians(string area) =>
        Send<ClinicianRow[]>(Get($"/referrals/match?area={area}"));

    /// <summary>Nothing is released here — the package comes back to be
    /// read, and the signature raised covers exactly those bytes.</summary>
    public Task<ReferralPackage> PrepareReferral(string interactorId,
        string profileId, string providerId, string token) =>
        Send<ReferralPackage>(Post("/referrals/prepare", new
        {
            interactor_id = interactorId, profile_id = profileId,
            provider_id = providerId
        }, token));

    public Task<ReferralPackage> ReleaseReferral(string referralId,
        string signatureId, string token) =>
        Send<ReferralPackage>(Post($"/referrals/{referralId}/release",
            new { signature_id = signatureId }, token));

    /// <summary>Once — a second attempt says so rather than quietly
    /// working.</summary>
    public Task<ReferralPackage> OpenReferral(string referralId,
        string linkToken) =>
        Send<ReferralPackage>(Get(
            $"/referrals/{referralId}?token={linkToken}"));

    public Task<ReferralPackage> ReplyToReferral(string referralId,
        string linkToken, string content) =>
        Send<ReferralPackage>(Post(
            $"/referrals/{referralId}/reply?token={linkToken}",
            new { content }));

    public Task<ObjectionCard> ObjectionOf(string objectionId) =>
        Send<ObjectionCard>(Get($"/objections/{objectionId}"));

    public Task<ObjectionAudit> ObjectionAuditOf(string objectionId,
        string token) =>
        Send<ObjectionAudit>(Get($"/objections/{objectionId}/audit", token));

    public Task<ObjectionCard> WithdrawObjectionConsent(
        string objectionId) =>
        Send<ObjectionCard>(Post($"/objections/{objectionId}/withdraw",
            new { }));

    public Task<ObjectionCard> RevokeObjectionBasis(string objectionId) =>
        Send<ObjectionCard>(Post($"/objections/{objectionId}/revoke",
            new { }));

    /// <summary>Reviewer-only — an owner cannot adjudicate an objection
    /// against their own profile, and the backend enforces it by
    /// role.</summary>
    public Task<ObjectionCard> ResolveObjection(string objectionId,
        string outcome, string token) =>
        Send<ObjectionCard>(Post($"/objections/{objectionId}/resolve",
            new { outcome }, token));

    public Task<LobbyVocabulary> LobbyVocabulary() =>
        Send<LobbyVocabulary>(Get("/gaming/lobby/vocabulary"));

    public Task<LobbySeatRow> SeatInLobby(string sessionId,
        string memberKind, string memberId, string role, string token) =>
        Send<LobbySeatRow>(Post($"/gaming/sessions/{sessionId}/lobby", new
        {
            member_kind = memberKind, member_id = memberId, role
        }, token));

    /// <summary>The honest roster: what each callsign is travels with
    /// it.</summary>
    public Task<LobbyRoster> LobbyRosterOf(string sessionId, string token) =>
        Send<LobbyRoster>(Get($"/gaming/sessions/{sessionId}/lobby", token));

    public Task<LobbyLeft> LeaveLobby(string sessionId, string memberId,
        string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
            $"/gaming/sessions/{sessionId}/lobby")
        { Content = JsonContent.Create(new { member_id = memberId }) };
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<LobbyLeft>(req);
    }

    public Task<LobbyContext> LobbyContextOf(string sessionId,
        string token) =>
        Send<LobbyContext>(Get(
            $"/gaming/sessions/{sessionId}/lobby/context", token));

    public Task<DockFacesBox> DockFaces() =>
        Send<DockFacesBox>(Get("/dock/faces"));

    /// <summary>The dock is read-only, so every face carries a way out of
    /// it.</summary>
    public Task<DockWhere> DockWhereOf(string face) =>
        Send<DockWhere>(Get($"/dock/where/{face}"));

    public Task<DockSettings> DockSettingsOf(string profileId,
        string token) =>
        Send<DockSettings>(Get($"/dock/{profileId}", token));

    public Task<DockSettings> ConfigureDock(string profileId, string corner,
        string state, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Put,
            $"/dock/{profileId}")
        { Content = JsonContent.Create(new { corner, state }) };
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<DockSettings>(req);
    }

    public Task<DockFace> DockFaceOf(string profileId, string name,
        string token) =>
        Send<DockFace>(Get($"/dock/{profileId}/face/{name}", token));

    // -- the signature, the mail server, the room's ear, the wall screen,
    // the plan, the handoff and the campaign ------------------------------
    // Seven small blocks that close out the mid-sized doorless groups.

    public Task<SignatureCertificate> SignatureCertificateOf(string sigId) =>
        Send<SignatureCertificate>(Get($"/signatures/{sigId}/certificate"));

    /// <summary>No token, no lookup, no trust in this deployment beyond
    /// the arithmetic.</summary>
    public Task<SignatureVerdict> VerifySignaturePackage() =>
        Send<SignatureVerdict>(Post("/signatures/verify",
            new { package = new { } }));

    public Task<ProofingOut> ReproofCredential(string rowId, string level,
        string attestor, string token) =>
        Send<ProofingOut>(Post($"/signatures/credentials/{rowId}/proofing",
            new
            {
                proofing_level = level, proofing_attestor = attestor,
                proofing_method = "document", proofing_ref = "in-person"
            }, token));

    /// <summary>The WebAuthn ceremony page, opened in a web view — never
    /// re-implemented in the shell. The URL is taken off the same GET the
    /// view will issue, so the door and the address cannot drift.</summary>
    public string SignatureCeremonyUrl() =>
        Get("/signatures/ceremony").RequestUri!.ToString();

    public Task<MailSettingsCard> MailSettings() =>
        Send<MailSettingsCard>(Get("/settings/mail"));

    public Task<MailSettingsCard> SaveMailSettings(string host, int port,
        string sender, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Put, "/settings/mail")
        { Content = JsonContent.Create(new { host, port, sender }) };
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<MailSettingsCard>(req);
    }

    public Task<MailSettingsCard> ForgetMailSettings(string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete, "/settings/mail");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<MailSettingsCard>(req);
    }

    /// <summary>A settings screen that saves without ever proving it can
    /// deliver is how an app ends up insisting it emailed somebody.</summary>
    public Task<MailTestOut> TestMailSettings(string to, string token) =>
        Send<MailTestOut>(Post("/settings/mail/test", new { to }, token));

    public Task<RoomCard[]> Rooms() => Send<RoomCard[]>(Get("/rooms"));

    public Task<RoomTemplate[]> RoomTemplates() =>
        Send<RoomTemplate[]>(Get("/rooms/templates"));

    /// <summary>Step into a live room: the token names the joiner, joining
    /// twice is being there once, and the table seats eight.</summary>
    public Task<RoomCreated> JoinRoom(string roomId, string token) =>
        Send<RoomCreated>(Post($"/rooms/{roomId}/join", new { }, token));

    /// <summary>Step into a standing room — the room, not a copy of it:
    /// joins the live one with a seat left, opens it fresh only when nobody
    /// is there.</summary>
    public Task<RoomCreated> OpenStandingRoom(string key, string profileId,
        string token) =>
        Send<RoomCreated>(Post(
            $"/rooms/templates/{key}/open?profile_id={Uri.EscapeDataString(profileId)}",
            new { }, token));

    public Task<MicDisclosure> LendRoomMic(string roomId,
        string interactorId, string token) =>
        Send<MicDisclosure>(Post($"/rooms/{roomId}/mic",
            new { interactor_id = interactorId }, token));

    public Task<MicDisclosure> TakeBackRoomMic(string roomId,
        string interactorId, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
            $"/rooms/{roomId}/mic/{interactorId}");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<MicDisclosure>(req);
    }

    /// <summary>Readable by anyone in the room — a disclosure only its
    /// subject can see is not a disclosure.</summary>
    public Task<MicDisclosure> RoomMicDisclosure(string roomId,
        string token) =>
        Send<MicDisclosure>(Get($"/rooms/{roomId}/mic", token));

    public Task<DisplayVocabulary> DisplayVocabulary() =>
        Send<DisplayVocabulary>(Get("/displays/vocabulary"));

    public Task<DisplayCard> DisplayOf(string displayId) =>
        Send<DisplayCard>(Get($"/displays/{displayId}"));

    public Task<DisplayCard> SetDisplayFaces(string displayId,
        string[] faces, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Put,
            $"/displays/{displayId}/faces")
        { Content = JsonContent.Create(new { faces }) };
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<DisplayCard>(req);
    }

    public Task<DisplayCard> TakeDownDisplay(string displayId, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
            $"/displays/{displayId}");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<DisplayCard>(req);
    }

    public Task<MembershipCard> MembershipOf(string accountId,
        string token) =>
        Send<MembershipCard>(Get($"/memberships/{accountId}", token));

    public Task<MembershipCard> JoinPlan(string accountId, string plan,
        string token) =>
        Send<MembershipCard>(Post($"/memberships/{accountId}",
            new { plan }, token));

    /// <summary>The account becomes a visitor and keeps its profiles — a
    /// lapsed subscription is not a reason to delete somebody's
    /// work.</summary>
    public Task<MembershipCard> CancelMembership(string accountId,
        string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
            $"/memberships/{accountId}");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<MembershipCard>(req);
    }

    public Task<HandoffCard> CreateHandoff(string interactorId,
        string profileId, string providerId, string token) =>
        Send<HandoffCard>(Post("/handoffs", new
        {
            interactor_id = interactorId, profile_id = profileId,
            provider_id = providerId, consent = true
        }, token));

    public Task<HandoffCard> OpenHandoff(string handoffId,
        string linkToken) =>
        Send<HandoffCard>(Get($"/handoffs/{handoffId}?token={linkToken}"));

    public Task<HandoffCard> RevokeHandoff(string handoffId, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
            $"/handoffs/{handoffId}");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<HandoffCard>(req);
    }

    public Task<CampaignCard> CampaignOf(string campaignId) =>
        Send<CampaignCard>(Get($"/campaigns/{campaignId}"));

    /// <summary>No token required — a donor arriving from a beacon scan
    /// has no account, and requiring one gates generosity behind
    /// signup.</summary>
    public Task<CampaignCard> Donate(string campaignId, double amount,
        string note) =>
        Send<CampaignCard>(Post($"/campaigns/{campaignId}/donate",
            new { amount, note }));

    public Task<CampaignCard> CloseCampaign(string campaignId,
        string token) =>
        Send<CampaignCard>(Post($"/campaigns/{campaignId}/close", new { },
            token));

    public async Task<WallPostRow[]> Wall(string profileId)
    {
        var box = await Send<WallBox>(Get($"/profiles/{profileId}/wall"));
        return box.Posts;
    }

    public Task<WallPostRow> PostToWall(string profileId, string body,
                                        string token) =>
        Send<WallPostRow>(Post($"/profiles/{profileId}/wall",
            new { body }, token));

    public async Task<CommentRow[]> Comments(string kind, string targetId,
                                             string token)
    {
        var box = await Send<CommentBox>(
            Get($"/{kind}/{targetId}/comments", token));
        return box.Comments;
    }

    public Task<CommentRow> AddComment(string kind, string targetId,
                                       string body, string token) =>
        Send<CommentRow>(Post($"/{kind}/{targetId}/comments",
            new { body }, token));

    public Task<CommentRow> DeleteComment(string commentId, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
            $"/comments/{commentId}");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<CommentRow>(req);
    }


    // -- standing behind the counter: desks, the market, exchanges --
    // The caller's side shipped long ago; the other side of the same
    // counter never reached any shell, nor did searching, pricing,
    // selling or buying in the market, nor being party to an exchange.

    public Task<DeskBrief[]> Desks() => Send<DeskBrief[]>(Get("/desks"));

    public Task<DeskOpened> OpenDesk(string ownerId, string displayName,
                                   string trade, string attestor,
                                   string basis, string location,
                                   string blurb, string token) =>
        Send<DeskOpened>(Post("/desks", new {
            owner_id = ownerId, display_name = displayName, trade, attestor,
            basis, location, blurb }, token));

    public Task<DeskOpened> SetDeskPresence(string deskId, string presence,
                                          string token) =>
        Send<DeskOpened>(Put($"/desks/{deskId}/presence", new { presence },
                           token));

    public Task<DeskOpened> SetDeskPortrait(string deskId, string token) =>
        Send<DeskOpened>(Put($"/desks/{deskId}/portrait",
                           new { asset = (string?)null }, token));

    public Task<DeskOpened> SetDeskCamera(string deskId, string url,
                                        string token) =>
        Send<DeskOpened>(Put($"/desks/{deskId}/camera", new { url },
                           token));

    public async Task<DeskRing[]> DeskRings(string deskId, string token)
    {
        var box = await Send<DeskRingBox>(Get($"/desks/{deskId}/rings",
                                              token));
        return box.Rings;
    }

    public Task<DeskRing> AckDeskRing(string deskId, string ringId,
                                      string token) =>
        Send<DeskRing>(Post($"/desks/{deskId}/rings/{ringId}/ack",
                            new { }, token));

    public Task<DeskGuest> AskToJoinDesk(string deskId, string note,
                                         string token) =>
        Send<DeskGuest>(Post($"/desks/{deskId}/guests", new { note }, token));

    public async Task<DeskGuest[]> DeskGuests(string deskId, string token)
    {
        var box = await Send<DeskGuestBox>(Get($"/desks/{deskId}/guests",
                                                token));
        return box.Guests;
    }

    public Task<DeskGuest> AcceptDeskGuest(string deskId, string requestId,
                                           string token) =>
        Send<DeskGuest>(Post($"/desks/{deskId}/guests/{requestId}/accept",
                             new { }, token));

    public Task<DeskGuest> DeclineDeskGuest(string deskId, string requestId,
                                            string token) =>
        Send<DeskGuest>(Post($"/desks/{deskId}/guests/{requestId}/decline",
                             new { }, token));

    /// <summary>The caller's own way out — theirs to press, not the desk's.</summary>
    public Task<DeskGuest> LeaveDesk(string deskId, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
            $"/desks/{deskId}/guests/me");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<DeskGuest>(req);
    }

    public Task<DeskBeacon> AddDeskBeacon(string deskId, string label,
                                          string token) =>
        Send<DeskBeacon>(Post($"/desks/{deskId}/beacons", new { label },
                              token));

    public async Task<DeskBeacon[]> DeskBeacons(string deskId, string token)
    {
        var box = await Send<DeskBeaconBox>(Get($"/desks/{deskId}/beacons",
                                                 token));
        return box.Beacons;
    }

    public Task<DeskBeacon> RemoveDeskBeacon(string beaconId, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
            $"/desk-beacons/{beaconId}");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<DeskBeacon>(req);
    }

    /// <summary>The sticker, as bytes an image control can show. Fetched
    /// directly rather than through the JSON helper, which cannot carry an
    /// image.</summary>
    public Task<byte[]> DeskBeaconQr(string beaconId)
    {
        var req = new HttpRequestMessage(HttpMethod.Get,
            $"/desk-beacons/{beaconId}/qr.svg");
        return Dispatch(req).ContinueWith(r =>
            r.Result.Content.ReadAsByteArrayAsync().Result);
    }

    /// <summary>What the desk looks like right now, as a still.</summary>
    public Task<byte[]> DeskView(string deskId)
    {
        var req = new HttpRequestMessage(HttpMethod.Get,
            $"/desks/{deskId}/view.webp");
        return Dispatch(req).ContinueWith(r =>
            r.Result.Content.ReadAsByteArrayAsync().Result);
    }

    public Task<DeskOverlay> DeskOverlay(string deskId) =>
        Send<DeskOverlay>(Get($"/desks/{deskId}/overlay"));

    public Task<LivePerson> DeskLivePerson(string deskId) =>
        Send<LivePerson>(Get($"/desks/{deskId}/live-person"));

    // -- the market, from both sides --

    public Task<MarketCard[]> Marketplace() =>
        Send<MarketCard[]>(Get("/marketplace"));

    public Task<MarketSearchBox> MarketSearch(string query) =>
        Send<MarketSearchBox>(Get(
            $"/marketplace/search?q={Uri.EscapeDataString(query)}"));

    public Task<string[]> MarketLocalities() =>
        Send<string[]>(Get("/marketplace/localities"));

    public Task<MarketAssistBox> MarketAssist(string need) =>
        Send<MarketAssistBox>(Post("/marketplace/assist", new { need }));

    /// <summary>The demo shelf: one press and the market has something on it.</summary>
    public Task<MarketSeeded> SeedMarketplace() =>
        Send<MarketSeeded>(Post("/marketplace/seed", new { }));

    public Task<MarketListed> ListInMarketplace(string profileId,
                                                string blurb,
                                                string[] tags, string token) =>
        Send<MarketListed>(Post($"/profiles/{profileId}/marketplace",
            new { blurb, tags }, token));

    public Task<MarketListed> UnlistFromMarketplace(string profileId,
                                                    string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
            $"/profiles/{profileId}/marketplace");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<MarketListed>(req);
    }

    public Task<MarketListed> RemoveMarketListing(string listingId,
                                                  string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
            $"/marketplace/listings/{listingId}");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<MarketListed>(req);
    }

    public Task<MarketOffer> ListingOffer(string listingId) =>
        Send<MarketOffer>(Get($"/marketplace/listings/{listingId}/offer"));

    public Task<MarketOffer> SetListingOffer(string listingId, double price,
                                             int? stock,
                                             string token) =>
        Send<MarketOffer>(Put($"/marketplace/listings/{listingId}/offer",
            new { price, currency = "USD", stock },
            token));

    public Task<MarketOffer> ClearListingOffer(string listingId, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
            $"/marketplace/listings/{listingId}/offer");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<MarketOffer>(req);
    }

    public Task<MarketOffer> PlaceListing(string listingId, string locality,
                                          string token) =>
        Send<MarketOffer>(Put($"/marketplace/listings/{listingId}/place",
            new { locality }, token));

    public Task<MarketOffer> UnplaceListing(string listingId, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
            $"/marketplace/listings/{listingId}/place");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<MarketOffer>(req);
    }

    public Task<MarketSale> PurchaseListing(string listingId, string token) =>
        Send<MarketSale>(Post($"/marketplace/listings/{listingId}/purchase",
                              new { }, token));

    public async Task<MarketSale[]> MarketSales(string token)
    {
        var box = await Send<MarketSalesBox>(Get("/marketplace/sales", token));
        return box.Sales;
    }

    public Task<MarketSettings> MarketSettings(string interactorId,
                                               string token) =>
        Send<MarketSettings>(Get($"/marketplace/settings/{interactorId}",
                                 token));

    public Task<MarketSettings> SetMarketSettings(string interactorId,
                                                  string locality,
                                                  bool includeRemote,
                                                  string token) =>
        Send<MarketSettings>(Put($"/marketplace/settings/{interactorId}",
            new { locality, include_remote = includeRemote }, token));

    // -- exchanges: two parties, one manifest --

    public Task<ExchangeVocabulary> ExchangeVocabulary() =>
        Send<ExchangeVocabulary>(Get("/exchanges/vocabulary"));

    public Task<ExchangeDeal> ProposeExchange(string hostId, string guestId,
                                              string work, string industry,
                                              double fee, string token) =>
        Send<ExchangeDeal>(Post("/exchanges", new {
            host_id = hostId, guest_id = guestId, work, industry, fee },
            token));

    public Task<ExchangeDeal> Exchange(string exchangeId, string token) =>
        Send<ExchangeDeal>(Get($"/exchanges/{exchangeId}", token));

    public async Task<ExchangeDeal[]> MyExchanges(string partyId,
                                                  string token)
    {
        var box = await Send<ExchangeBox>(
            Get($"/parties/{partyId}/exchanges", token));
        return box.Exchanges;
    }

    public Task<ExchangeItemRow> AddExchangeItem(string exchangeId,
                                                 string direction,
                                                 string name, string kind,
                                                 string token) =>
        Send<ExchangeItemRow>(Post($"/exchanges/{exchangeId}/items",
            new { direction, name, kind }, token));

    public Task<ExchangeItemRow> RemoveExchangeItem(string exchangeId,
                                                    string itemId,
                                                    string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
            $"/exchanges/{exchangeId}/items/{itemId}");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<ExchangeItemRow>(req);
    }

    /// <summary>Each item is accepted separately — nothing moves by itself.</summary>
    public Task<ExchangeItemRow> AcceptExchangeItem(string exchangeId,
                                                    string itemId,
                                                    string actorId,
                                                    string token) =>
        Send<ExchangeItemRow>(Post(
            $"/exchanges/{exchangeId}/items/{itemId}/accept",
            new { actor_id = actorId }, token));

    /// <summary>Both parties sign the same manifest; any change clears both.</summary>
    public Task<ExchangeDeal> SignExchange(string exchangeId, string actorId,
                                           string token) =>
        Send<ExchangeDeal>(Post($"/exchanges/{exchangeId}/sign",
            new { actor_id = actorId }, token));

    public Task<ExchangeDeal> ReopenExchange(string exchangeId,
                                             string actorId, string token) =>
        Send<ExchangeDeal>(Post($"/exchanges/{exchangeId}/reopen",
            new { actor_id = actorId }, token));

    public Task<ExchangeDeal> WithdrawFromExchange(string exchangeId,
                                                   string actorId,
                                                   string token) =>
        Send<ExchangeDeal>(Post($"/exchanges/{exchangeId}/withdraw",
            new { actor_id = actorId }, token));

    public Task<ExchangeChannel> ExchangeChannel(string exchangeId,
                                                 string token) =>
        Send<ExchangeChannel>(Get($"/exchanges/{exchangeId}/channel", token));

}
public record DmMessageRow(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("sender_id")] string SenderId,
    [property: JsonPropertyName("body")] string Body);

public record DmThreadRow(
    [property: JsonPropertyName("other_id")] string OtherId,
    [property: JsonPropertyName("other_name")] string? OtherName,
    [property: JsonPropertyName("messages")] int Messages);

public record DmThreadBox(
    [property: JsonPropertyName("threads")] DmThreadRow[] Threads);

public record DmThreadView(
    [property: JsonPropertyName("with")] string With,
    [property: JsonPropertyName("messages")] DmMessageRow[] Messages);

public record HomepageTheme(
    [property: JsonPropertyName("bg")] string Bg,
    [property: JsonPropertyName("accent")] string Accent);

public record HomepageDoc(
    [property: JsonPropertyName("headline")] string Headline,
    [property: JsonPropertyName("about")] string About,
    [property: JsonPropertyName("theme")] HomepageTheme Theme,
    [property: JsonPropertyName("editable")] bool Editable);

public record ShopCard(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("seller")] string Seller,
    [property: JsonPropertyName("tag")] string? Tag,
    [property: JsonPropertyName("offerings")] int Offerings);

public record ShopOffering(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("kind")] string Kind,
    [property: JsonPropertyName("title")] string Title,
    [property: JsonPropertyName("price")] double Price,
    [property: JsonPropertyName("currency")] string Currency,
    [property: JsonPropertyName("availability")] string Availability,
    [property: JsonPropertyName("retired")] int Retired);

public record ShopDetail(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("blurb")] string? Blurb,
    [property: JsonPropertyName("seller")] string? Seller,
    [property: JsonPropertyName("offerings")] ShopOffering[] Offerings);

public record ShopOrder(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("shop_id")] string ShopId,
    [property: JsonPropertyName("title")] string Title,
    [property: JsonPropertyName("quantity")] int Quantity,
    [property: JsonPropertyName("amount")] double Amount,
    [property: JsonPropertyName("currency")] string Currency,
    [property: JsonPropertyName("status")] string Status);


public record FriendRow(
    [property: JsonPropertyName("profile_id")] string ProfileId,
    [property: JsonPropertyName("display_name")] string? DisplayName,
    [property: JsonPropertyName("founder")] bool Founder,
    [property: JsonPropertyName("pinned")] bool Pinned,
    [property: JsonPropertyName("mutual")] bool Mutual);

public record FriendListBox(
    [property: JsonPropertyName("friends")] FriendRow[] Friends);

public record InboxEvent(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("kind")] string Kind,
    [property: JsonPropertyName("actor_id")] string ActorId,
    [property: JsonPropertyName("actor_name")] string? ActorName,
    [property: JsonPropertyName("seen")] bool Seen);

public record InboxPage(
    [property: JsonPropertyName("events")] InboxEvent[] Events,
    [property: JsonPropertyName("unseen")] int Unseen);

public record InboxSeen(
    [property: JsonPropertyName("marked_seen")] int MarkedSeen);

public record SuggestedRow(
    [property: JsonPropertyName("profile_id")] string ProfileId,
    [property: JsonPropertyName("display_name")] string? DisplayName,
    [property: JsonPropertyName("because")] string? Because);

public record SuggestedBox(
    [property: JsonPropertyName("suggested")] SuggestedRow[] Suggested);

public record FriendAdded(
    [property: JsonPropertyName("added")] bool? Added,
    [property: JsonPropertyName("removed")] bool? Removed);

public record WallPostRow(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("body")] string Body,
    [property: JsonPropertyName("status")] string? Status,
    [property: JsonPropertyName("likes")] int? Likes);

public record WallBox(
    [property: JsonPropertyName("posts")] WallPostRow[] Posts);

public record CommentRow(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("author_id")] string AuthorId,
    [property: JsonPropertyName("body")] string Body,
    [property: JsonPropertyName("status")] string Status);

public record CommentBox(
    [property: JsonPropertyName("comments")] CommentRow[] Comments);


/// What `POST /desks` hands back, and the only place the desk token is ever
/// shown. Deliberately not `DeskCard`: that is the *public* card
/// `GET /desks/{id}` returns, with the attestation, feed and bell a visitor
/// reads. Both existed under one name and the compiler refused the file.
public record DeskOpened(
    [property: JsonPropertyName("desk_id")] string DeskId,
    [property: JsonPropertyName("display_name")] string DisplayName,
    [property: JsonPropertyName("trade")] string? Trade,
    [property: JsonPropertyName("location")] string? Location,
    [property: JsonPropertyName("presence")] string Presence,
    [property: JsonPropertyName("rated")] bool Rated,
    [property: JsonPropertyName("desk_token")] string? DeskToken);

public record DeskBrief(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("display_name")] string DisplayName,
    [property: JsonPropertyName("trade")] string? Trade,
    [property: JsonPropertyName("presence")] string Presence);

public record DeskRing(
    [property: JsonPropertyName("id")] string? Id,
    [property: JsonPropertyName("note")] string? Note);

public record DeskRingBox(
    [property: JsonPropertyName("rings")] DeskRing[] Rings);

public record DeskGuest(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("guest_id")] string GuestId,
    [property: JsonPropertyName("display_name")] string? DisplayName,
    [property: JsonPropertyName("status")] string Status);

public record DeskGuestBox(
    [property: JsonPropertyName("guests")] DeskGuest[] Guests);

public record DeskBeacon(
    [property: JsonPropertyName("id")] string? Id,
    [property: JsonPropertyName("label")] string? Label);

public record DeskBeaconBox(
    [property: JsonPropertyName("beacons")] DeskBeacon[] Beacons);

public record DeskOverlay(
    [property: JsonPropertyName("likes")] int Likes,
    [property: JsonPropertyName("shares")] int Shares,
    [property: JsonPropertyName("waiting")] int Waiting);

public record LivePerson(
    [property: JsonPropertyName("desk_id")] string DeskId,
    [property: JsonPropertyName("owner_id")] string? OwnerId);

public record MarketCard(
    [property: JsonPropertyName("profile_id")] string ProfileId,
    [property: JsonPropertyName("display_name")] string DisplayName,
    [property: JsonPropertyName("blurb")] string? Blurb);

public record MarketHit(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("title")] string Title);

public record MarketSearchBox(
    [property: JsonPropertyName("results")] MarketHit[] Results);

public record MarketAssistBox(
    [property: JsonPropertyName("suggestions")] string[] Suggestions);

public record MarketSeeded(
    [property: JsonPropertyName("created")] int Created);

public record MarketListed(
    [property: JsonPropertyName("listed")] bool? Listed);

public record MarketOffer(
    [property: JsonPropertyName("amount")] double? Amount,
    [property: JsonPropertyName("currency")] string? Currency);

public record MarketSale(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("status")] string? Status);

public record MarketSalesBox(
    [property: JsonPropertyName("sales")] MarketSale[] Sales);

public record MarketSettings(
    [property: JsonPropertyName("locality")] string? Locality,
    [property: JsonPropertyName("region")] string? Region,
    [property: JsonPropertyName("scope")] string? Scope,
    [property: JsonPropertyName("include_remote")] bool? IncludeRemote,
    [property: JsonPropertyName("kinds_wanted")] string[]? KindsWanted,
    [property: JsonPropertyName("tags")] string[]? Tags);

public record ExchangeVocabulary(
    [property: JsonPropertyName("industries")] string[] Industries,
    [property: JsonPropertyName("rules")] string[] Rules);

public record ExchangeItemRow(
    [property: JsonPropertyName("id")] string? Id,
    [property: JsonPropertyName("name")] string? Name,
    [property: JsonPropertyName("kind")] string? Kind);

public record ExchangeDeal(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("work")] string? Work,
    [property: JsonPropertyName("state")] string State,
    [property: JsonPropertyName("items")] ExchangeItemRow[]? Items);

public record ExchangeBox(
    [property: JsonPropertyName("exchanges")] ExchangeDeal[] Exchanges);

public record ExchangeChannel(
    [property: JsonPropertyName("room_id")] string? RoomId);

public record LikeOut([property: JsonPropertyName("likes")] int Likes);

public record ShareOut([property: JsonPropertyName("url")] string? Url);

public record AudienceCounts(
    [property: JsonPropertyName("likes")] int Likes,
    [property: JsonPropertyName("comments")] int Comments,
    [property: JsonPropertyName("shares")] int Shares,
    [property: JsonPropertyName("subscribers")] int Subscribers);

public record SubscribeOut([property: JsonPropertyName("tier")] string? Tier);

public record SubscriberRow(
    [property: JsonPropertyName("subscriber")] string? Subscriber,
    [property: JsonPropertyName("tier")] string? Tier);

public record SubscriberBox(
    [property: JsonPropertyName("subscribers")] SubscriberRow[] Subscribers);

public record GiftRow(
    [property: JsonPropertyName("giver_id")] string? GiverId,
    [property: JsonPropertyName("amount")] double Amount,
    [property: JsonPropertyName("note")] string? Note);

public record GiftBox(
    [property: JsonPropertyName("gifts")] GiftRow[] Gifts,
    [property: JsonPropertyName("total_amount")] double TotalAmount);

public record PartyMember(
    [property: JsonPropertyName("member_id")] string MemberId,
    [property: JsonPropertyName("kind")] string? Kind);

public record PartyCard(
    [property: JsonPropertyName("id")] string? Id,
    [property: JsonPropertyName("title")] string? Title,
    [property: JsonPropertyName("state")] string? State,
    [property: JsonPropertyName("position_s")] int PositionS,
    [property: JsonPropertyName("members")] PartyMember[]? Members);

public record PartyLine(
    [property: JsonPropertyName("member_id")] string? MemberId,
    [property: JsonPropertyName("body")] string? Body);

public record PartyChatBox(
    [property: JsonPropertyName("lines")] PartyLine[] Lines);

public record PartyContext(
    [property: JsonPropertyName("you_have_not_seen_it")]
    string? YouHaveNotSeenIt);

public record GrantVocabulary(
    [property: JsonPropertyName("terms")] string[] Terms);

public record GrantCard(
    [property: JsonPropertyName("id")] string? Id,
    [property: JsonPropertyName("title")] string? Title,
    [property: JsonPropertyName("state")] string? State,
    [property: JsonPropertyName("lender_id")] string? LenderId,
    [property: JsonPropertyName("borrower_id")] string? BorrowerId);

public record GrantBox(
    [property: JsonPropertyName("grants")] GrantCard[] Grants);

public record GrantUse(
    [property: JsonPropertyName("used_at")] string? UsedAt,
    [property: JsonPropertyName("what")] string? What);

public record GrantUseBox(
    [property: JsonPropertyName("uses")] GrantUse[] Uses);

public record MyGrants(
    [property: JsonPropertyName("lending")] GrantCard[]? Lending,
    [property: JsonPropertyName("borrowing")] GrantCard[]? Borrowing);

public record LeaveOut([property: JsonPropertyName("id")] string? Id,
    [property: JsonPropertyName("members")] PartyMember[]? Members);

public record WhoseCard(
    [property: JsonPropertyName("display_name")] string? DisplayName,
    [property: JsonPropertyName("anonymous")] bool? Anonymous);

public record LentRow(
    [property: JsonPropertyName("interactor_id")] string? InteractorId,
    [property: JsonPropertyName("device")] string? Device);

public record MicDisclosure(
    // `microphones_lent` on the wire. `lent` decoded to null on every call.
    [property: JsonPropertyName("microphones_lent")] LentRow[]? Lent);

public record WornRow(
    [property: JsonPropertyName("interactor_id")] string? InteractorId,
    [property: JsonPropertyName("kind")] string? Kind,
    [property: JsonPropertyName("title")] string? Title);

public record WornDisclosure(
    [property: JsonPropertyName("overlays")] WornRow[]? Overlays,
    [property: JsonPropertyName("note")] string? Note);

public record CameraVocabulary(
    [property: JsonPropertyName("never")]
    System.Collections.Generic.Dictionary<string, string>? Never);

public record BystanderNote(
    [property: JsonPropertyName("guidance")] string? Guidance);

public record CameraSession(
    [property: JsonPropertyName("id")] string? Id,
    [property: JsonPropertyName("subject")] string? Subject,
    [property: JsonPropertyName("state")] string? State);

public record CameraDisclosure(
    [property: JsonPropertyName("live")] bool? Live,
    [property: JsonPropertyName("recording")] bool? Recording);

public record OrgDepartment(
    [property: JsonPropertyName("name")] string? Name,
    [property: JsonPropertyName("role")] string? Role);

public record OrgCard(
    [property: JsonPropertyName("id")] string? Id,
    [property: JsonPropertyName("name")] string? Name,
    [property: JsonPropertyName("departments")] OrgDepartment[]? Departments);

/// <summary>AI for lease: the receipt for seating somebody else's licensed
/// specialist as a department.</summary>
public record LeaseOut(
    [property: JsonPropertyName("lease_id")] string LeaseId,
    [property: JsonPropertyName("department_id")] string DepartmentId);

public record Coordination(
    [property: JsonPropertyName("id")] string? Id,
    [property: JsonPropertyName("goal")] string? Goal,
    [property: JsonPropertyName("status")] string? Status);

public record TutorialStep(
    [property: JsonPropertyName("key")] string? Key,
    [property: JsonPropertyName("chapter")] string? Chapter,
    [property: JsonPropertyName("title")] string? Title,
    [property: JsonPropertyName("try_it")] string? TryIt,
    [property: JsonPropertyName("what")] string? What);

// A chapter is a name and the steps under it. It never carried a `key` or a
// `title` of its own — those belong to the steps, and reading them off the
// chapter drew a tour with no chapter names in it.
public record TutorialChapter(
    [property: JsonPropertyName("chapter")] string? Chapter,
    [property: JsonPropertyName("steps")] TutorialStep[]? Steps);

public record TutorialOutline(
    [property: JsonPropertyName("guide")] string? Guide,
    [property: JsonPropertyName("chapters")] TutorialChapter[]? Chapters);

public record TutorialProgress(
    [property: JsonPropertyName("learner_id")] string? LearnerId,
    [property: JsonPropertyName("step")] TutorialStep? Step);

public record RobotUnbound(
    [property: JsonPropertyName("unbound")] bool? Unbound);

public record RobotCommandRow(
    [property: JsonPropertyName("command")] string? Command,
    [property: JsonPropertyName("created_at")] string? CreatedAt);

public record RobotSkillRow(
    [property: JsonPropertyName("title")] string? Title,
    [property: JsonPropertyName("pack_title")] string? PackTitle);

public record RobotSteering(
    [property: JsonPropertyName("behavior_profile")]
    string? BehaviorProfile);

public record ClinicianRow(
    [property: JsonPropertyName("id")] string? Id,
    [property: JsonPropertyName("name")] string? Name,
    [property: JsonPropertyName("expertise")] string? Expertise);

public record ReferralPackage(
    [property: JsonPropertyName("id")] string? Id,
    [property: JsonPropertyName("referral_id")] string? ReferralId,
    [property: JsonPropertyName("status")] string? Status);

public record ObjectionCard(
    [property: JsonPropertyName("id")] string? Id,
    [property: JsonPropertyName("status")] string? Status);

public record ObjectionEvent(
    [property: JsonPropertyName("event")] string? Event,
    [property: JsonPropertyName("sealed")] bool? Sealed);

public record ObjectionAudit(
    [property: JsonPropertyName("status")] string? Status,
    [property: JsonPropertyName("events")] ObjectionEvent[]? Events);

public record LobbyVocabulary(
    [property: JsonPropertyName("rules")] string[]? Rules);

public record LobbySeatRow(
    [property: JsonPropertyName("member_id")] string? MemberId,
    [property: JsonPropertyName("member_kind")] string? MemberKind,
    [property: JsonPropertyName("role")] string? Role,
    [property: JsonPropertyName("callsign")] string? Callsign);

public record LobbyRoster(
    [property: JsonPropertyName("members")] LobbySeatRow[]? Members);

public record LobbyLeft([property: JsonPropertyName("seated")] bool? Seated,
    [property: JsonPropertyName("id")] string? Id);

public record LobbyContext(
    [property: JsonPropertyName("note")] string? Note);

// Maps, not lists: face -> what it shows, and thing -> why it is never
// glanced at. Declared as string[] this threw on every response.
public record DockFacesBox(
    [property: JsonPropertyName("faces")]
    System.Collections.Generic.Dictionary<string, string>? Faces,
    [property: JsonPropertyName("never")]
    System.Collections.Generic.Dictionary<string, string>? Never);

public record DockWhere(
    [property: JsonPropertyName("face")] string? Face,
    // An integer on the wire. Declared `string` here, this threw on every
    // response the button ever got.
    [property: JsonPropertyName("screen")] int? Screen,
    [property: JsonPropertyName("path")] string? Path,
    [property: JsonPropertyName("title")] string? Title);

public record DockSettings(
    [property: JsonPropertyName("corner")] string? Corner,
    [property: JsonPropertyName("state")] string? State);

public record DockFace(
    [property: JsonPropertyName("face")] string? Face,
    [property: JsonPropertyName("line")] string? Line);

public record SignatureCertificate(
    [property: JsonPropertyName("printed_name")] string? PrintedName,
    [property: JsonPropertyName("meaning")] string? Meaning,
    [property: JsonPropertyName("signed_at")] string? SignedAt);

public record SignatureVerdict(
    [property: JsonPropertyName("valid")] bool? Valid,
    [property: JsonPropertyName("verified")] bool? Verified);

public record ProofingOut(
    [property: JsonPropertyName("proofing_level")] string? ProofingLevel);

public record MailSettingsCard(
    [property: JsonPropertyName("transport")] string? Transport,
    [property: JsonPropertyName("host")] string? Host,
    [property: JsonPropertyName("sender")] string? Sender);

public record MailTestOut(
    [property: JsonPropertyName("sent")] bool? Sent);

public record RoomCard(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("topic")] string? Topic,
    [property: JsonPropertyName("channel")] string? Channel,
    [property: JsonPropertyName("participants")] int Participants);

/// <summary>A standing room: a blueprint the server keeps so the Rooms door
/// never greets a newcomer with an empty list. Opening one goes through the
/// same POST /rooms as a typed topic.</summary>
public record RoomTemplate(
    [property: JsonPropertyName("key")] string Key,
    [property: JsonPropertyName("topic")] string? Topic,
    [property: JsonPropertyName("channel")] string? Channel,
    [property: JsonPropertyName("pitch")] string? Pitch);

public record NeverShown(
    [property: JsonPropertyName("thing")] string? Thing,
    [property: JsonPropertyName("why")] string? Why);

public record DisplayVocabulary(
    [property: JsonPropertyName("never")] NeverShown[]? Never);

public record DisplayCard(
    [property: JsonPropertyName("id")] string? Id,
    [property: JsonPropertyName("kind")] string? Kind,
    [property: JsonPropertyName("faces")] string[]? Faces);

public record MembershipCard(
    [property: JsonPropertyName("plan")] string? Plan,
    [property: JsonPropertyName("status")] string? Status);

public record HandoffCard(
    [property: JsonPropertyName("id")] string? Id,
    [property: JsonPropertyName("provider")] string? Provider,
    [property: JsonPropertyName("token")] string? Token,
    [property: JsonPropertyName("sealed")] bool? Sealed);

public record CampaignCard(
    [property: JsonPropertyName("id")] string? Id,
    [property: JsonPropertyName("title")] string? Title,
    [property: JsonPropertyName("raised")] double? Raised,
    [property: JsonPropertyName("goal")] double? Goal,
    [property: JsonPropertyName("status")] string? Status);

public record WorkflowCard(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("goal")] string? Goal,
    [property: JsonPropertyName("status")] string? Status,
    [property: JsonPropertyName("next_phase")] string? NextPhase,
    [property: JsonPropertyName("delegated_to")] string? DelegatedTo);

public record DelegationOffer(
    [property: JsonPropertyName("delegation")] bool? Delegation,
    [property: JsonPropertyName("phases")] string[]? Phases);

public record CreativeWork(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("kind")] string? Kind,
    [property: JsonPropertyName("moment")] string? Moment,
    [property: JsonPropertyName("content")] string? Content);

public record ProofreadOut(
    [property: JsonPropertyName("edited")] string? Edited,
    [property: JsonPropertyName("suggestions")] string[]? Suggestions,
    [property: JsonPropertyName("status")] string? Status);

public record TriageKept(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("reason")] string? Reason);

public record TriageOut(
    [property: JsonPropertyName("reviewed")] int Reviewed,
    [property: JsonPropertyName("kept")] TriageKept[] Kept,
    [property: JsonPropertyName("discarded_ids")] string[] DiscardedIds);

public record TaskGrant(
    [property: JsonPropertyName("id")] string? Id,
    [property: JsonPropertyName("token")] string? Token,
    [property: JsonPropertyName("scope")] string[]? Scope,
    [property: JsonPropertyName("revoked")] bool? Revoked);

public record TaskOut(
    [property: JsonPropertyName("status")] string? Status,
    [property: JsonPropertyName("reason")] string? Reason);

public record TaskRow(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("topic")] string? Topic,
    [property: JsonPropertyName("status")] string? Status);

public record VenueCard(
    [property: JsonPropertyName("key")] string Key,
    [property: JsonPropertyName("name")] string? Name);

public record PlacementMade(
    [property: JsonPropertyName("placement_id")] string? PlacementId,
    [property: JsonPropertyName("beacon_id")] string? BeaconId,
    [property: JsonPropertyName("scan_url")] string? ScanUrl,
    [property: JsonPropertyName("removed")] bool? Removed);

public record PlacementRow(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("venue_name")] string? VenueName,
    [property: JsonPropertyName("label")] string? Label,
    [property: JsonPropertyName("scans")] int Scans,
    [property: JsonPropertyName("active")] bool Active);

public record PlacementFunnel(
    [property: JsonPropertyName("resolutions")] int Resolutions,
    [property: JsonPropertyName("verified_views")] int VerifiedViews,
    [property: JsonPropertyName("unique_chatters")] int UniqueChatters);

public record PlacementStats(
    [property: JsonPropertyName("funnel")] PlacementFunnel Funnel);

public record PlacementCustody(
    [property: JsonPropertyName("count")] int Count,
    [property: JsonPropertyName("chain_intact")] bool ChainIntact);

public record SpecialistRow(
    [property: JsonPropertyName("domain")] string Domain,
    [property: JsonPropertyName("specialist_profile_id")]
    string SpecialistProfileId);

public record MemoryRow(
    [property: JsonPropertyName("interactor_id")] string InteractorId,
    [property: JsonPropertyName("interactor_name")] string? InteractorName,
    [property: JsonPropertyName("turns")] int Turns);

public record RemembranceOut(
    [property: JsonPropertyName("content")] string? Content,
    [property: JsonPropertyName("covers")] int Covers);

public record MemoryAccountOut(
    [property: JsonPropertyName("remembers")] string? Remembers,
    [property: JsonPropertyName("folded_turns")] int FoldedTurns,
    [property: JsonPropertyName("recent_turns")] int RecentTurns);

public record ForgetOut(
    [property: JsonPropertyName("forgotten_turns")] int ForgottenTurns,
    [property: JsonPropertyName("remembrance_reset")] bool RemembranceReset);

public record MemoryTurn(
    [property: JsonPropertyName("id")] string? Id,
    [property: JsonPropertyName("role")] string? Role,
    [property: JsonPropertyName("content")] string? Content);

public record ThreadTurn(
    [property: JsonPropertyName("role")] string? Role,
    [property: JsonPropertyName("content")] string? Content);

public record ThreadOut(
    [property: JsonPropertyName("messages")] ThreadTurn[] Messages);

public record EngagementCard(
    [property: JsonPropertyName("sessions")] int? Sessions,
    [property: JsonPropertyName("score")] double? Score);

public record ClinicalNote(
    [property: JsonPropertyName("note")] string? Note,
    [property: JsonPropertyName("clinician")] string? Clinician);

public record EmbeddingCard(
    [property: JsonPropertyName("profile_id")] string? ProfileId,
    [property: JsonPropertyName("interactor_id")] string? InteractorId);

public record SourceRow(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("kind")] string? Kind,
    [property: JsonPropertyName("title")] string? Title,
    [property: JsonPropertyName("vaulted")] bool? Vaulted);

public record TransparencyCard(
    [property: JsonPropertyName("active_relationships")]
    int ActiveRelationships,
    [property: JsonPropertyName("model_effective")] string? ModelEffective,
    [property: JsonPropertyName("policy")] string? Policy);

public record ExportOut(
    [property: JsonPropertyName("messages")] JsonElement[] Messages,
    [property: JsonPropertyName("posts")] JsonElement[] Posts,
    [property: JsonPropertyName("sources")] JsonElement[] Sources);

public record StatsCard(
    [property: JsonPropertyName("sessions")] int Sessions,
    [property: JsonPropertyName("memory_entries")] int MemoryEntries,
    [property: JsonPropertyName("interactors")] int Interactors,
    [property: JsonPropertyName("sources")] int Sources);

public record FeedOut(
    [property: JsonPropertyName("posts")] JsonElement[] Posts,
    [property: JsonPropertyName("ranked_on")] string[] RankedOn,
    [property: JsonPropertyName("never_ranked_on")] string[] NeverRankedOn);

public record VeilCard(
    [property: JsonPropertyName("anonymous")] bool? Anonymous,
    [property: JsonPropertyName("withheld")] string[]? Withheld,
    [property: JsonPropertyName("not_withheld")] string[]? NotWithheld);

public record VerificationCard(
    [property: JsonPropertyName("verified")] bool? Verified,
    [property: JsonPropertyName("level")] string? Level,
    [property: JsonPropertyName("attestor")] string? Attestor,
    [property: JsonPropertyName("means")] string? Means);

public record VerifiableOut(
    [property: JsonPropertyName("can_verify")] bool CanVerify,
    [property: JsonPropertyName("reason")] string? Reason);

public record ProfilePatched(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("display_name")] string? DisplayName);

public record SunsetOut(
    [property: JsonPropertyName("status")] string? Status,
    [property: JsonPropertyName("farewells")] int? Farewells,
    [property: JsonPropertyName("succeeded")] bool? Succeeded,
    [property: JsonPropertyName("memorial")] bool? Memorial);

public record SucceedOut(
    [property: JsonPropertyName("succeeded")] bool? Succeeded,
    [property: JsonPropertyName("memorial")] bool? Memorial);

public record MemorialCard(
    [property: JsonPropertyName("display_name")] string? DisplayName,
    [property: JsonPropertyName("purpose")] string? Purpose,
    [property: JsonPropertyName("relationships_touched")]
    int? RelationshipsTouched);

public record RosterSibling(
    [property: JsonPropertyName("profile_id")] string ProfileId,
    [property: JsonPropertyName("display_name")] string? DisplayName,
    [property: JsonPropertyName("anonymous")] bool? Anonymous);

public record RosterOut(
    [property: JsonPropertyName("profiles")] RosterSibling[]? Profiles);

public record AvatarLikeness(
    [property: JsonPropertyName("real_person")] bool? RealPerson,
    [property: JsonPropertyName("basis")] string? Basis,
    [property: JsonPropertyName("attestor")] string? Attestor,
    [property: JsonPropertyName("note")] string? Note);

public record AvatarCard(
    [property: JsonPropertyName("asset")] string? Asset,
    [property: JsonPropertyName("asset_marked")] bool? AssetMarked,
    [property: JsonPropertyName("placeholder")] bool? Placeholder,
    [property: JsonPropertyName("likeness")] AvatarLikeness? Likeness);

public record BriefEntry(
    [property: JsonPropertyName("handle")] string? Handle);

public record BriefCatalog(
    [property: JsonPropertyName("style")] string? Style,
    [property: JsonPropertyName("briefs")] BriefEntry[]? Briefs);

public record BriefCard(
    [property: JsonPropertyName("handle")] string? Handle,
    [property: JsonPropertyName("brief")] string? Brief);

public record EmblemEntry(
    [property: JsonPropertyName("emblem")] string? Emblem,
    [property: JsonPropertyName("asset")] string? Asset,
    [property: JsonPropertyName("means")] string? Means);

public record EmblemCatalog(
    [property: JsonPropertyName("emblems")] EmblemEntry[]? Emblems,
    [property: JsonPropertyName("note")] string? Note);

public record IdentityVocabulary(
    [property: JsonPropertyName("withheld_when_anonymous")]
    string[] WithheldWhenAnonymous,
    [property: JsonPropertyName("never_withheld")] string[] NeverWithheld);

public record EmblemOut(
    [property: JsonPropertyName("emblem")] string? Emblem,
    [property: JsonPropertyName("note")] string? Note);

public record BadgeCard(
    [property: JsonPropertyName("verified")] bool? Verified,
    [property: JsonPropertyName("level")] string? Level,
    [property: JsonPropertyName("attestor")] string? Attestor);

public record ThemeEntry(
    [property: JsonPropertyName("id")] string? Id,
    [property: JsonPropertyName("label")] string? Label);

public record ThemeCatalog(
    [property: JsonPropertyName("themes")] ThemeEntry[]? Themes,
    [property: JsonPropertyName("layouts")] string[]? Layouts);

// The theme is a card of its own — an id, a label and the colours — not
// the id on its own. `theme` carries both meanings across this API and is
// on the collision record for it.
public record PageTheme(
    [property: JsonPropertyName("id")] string? Id,
    [property: JsonPropertyName("label")] string? Label);

public record PageCard(
    [property: JsonPropertyName("theme")] PageTheme? Theme,
    [property: JsonPropertyName("tagline")] string? Tagline,
    [property: JsonPropertyName("about")] string? About);

public record FrontCard(
    [property: JsonPropertyName("display_name")] string? DisplayName,
    [property: JsonPropertyName("headline")] string? Headline,
    [property: JsonPropertyName("ai_disclosure")] string? AiDisclosure);

public record SurfacesCard(
    [property: JsonPropertyName("surfaces")] string[] Surfaces);

public record CompositionSource(
    [property: JsonPropertyName("source_profile_id")] string? SourceProfileId,
    [property: JsonPropertyName("display_name")] string? DisplayName,
    [property: JsonPropertyName("weight")] double? Weight,
    [property: JsonPropertyName("aspect")] string? Aspect);

public record CompositionCard(
    [property: JsonPropertyName("sources")] CompositionSource[]? Sources,
    [property: JsonPropertyName("policy")] string? Policy);

public record EmbodimentRow(
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("kind")] string? Kind,
    [property: JsonPropertyName("has_llm")] bool? HasLlm);

public record ConsistencyForm(
    [property: JsonPropertyName("name")] string? Name,
    [property: JsonPropertyName("kind")] string? Kind);

public record ConsistencyCard(
    [property: JsonPropertyName("embodiments")]
    ConsistencyForm[]? Embodiments,
    [property: JsonPropertyName("surfaces")] string[]? Surfaces);

public record ProfileDisplayRow(
    [property: JsonPropertyName("id")] string? Id,
    [property: JsonPropertyName("kind")] string? Kind,
    [property: JsonPropertyName("label")] string? Label);

public record ProfileDisplayList(
    [property: JsonPropertyName("displays")] ProfileDisplayRow[] Displays);

public record SteeringCard(
    [property: JsonPropertyName("values")]
    System.Collections.Generic.Dictionary<string, int> Values,
    [property: JsonPropertyName("adult_mode")] bool? AdultMode);

public record WatchChip(
    [property: JsonPropertyName("display_name")] string? DisplayName,
    [property: JsonPropertyName("light")] string? Light,
    [property: JsonPropertyName("pending_approvals")]
    int? PendingApprovals);

public record WatchSummary(
    [property: JsonPropertyName("working")] int Working,
    [property: JsonPropertyName("needing_assistance")]
    int NeedingAssistance,
    [property: JsonPropertyName("stopped")] int Stopped);

public record WatchFaceCard(
    [property: JsonPropertyName("profile")] WatchChip Profile,
    [property: JsonPropertyName("summary")] WatchSummary Summary,
    [property: JsonPropertyName("haptic")] string? Haptic);

public record WatchActOut(
    [property: JsonPropertyName("status")] string? Status);

public record SignupOut(
    [property: JsonPropertyName("account_id")] string? AccountId,
    [property: JsonPropertyName("email")] string? Email,
    [property: JsonPropertyName("verified")] bool? Verified,
    [property: JsonPropertyName("code_delivery")] string? CodeDelivery);

public record SessionOut(
    [property: JsonPropertyName("account_id")] string? AccountId,
    [property: JsonPropertyName("email")] string? Email,
    [property: JsonPropertyName("display_name")] string? DisplayName,
    [property: JsonPropertyName("account_token")] string? AccountToken);

public record CodeDeliveryOut(
    [property: JsonPropertyName("email")] string? Email,
    [property: JsonPropertyName("code_delivery")] string? CodeDelivery);

public record ResetOut(
    [property: JsonPropertyName("email")] string? Email,
    [property: JsonPropertyName("reset")] bool? Reset);

public record OAuthDoor(
    [property: JsonPropertyName("provider")] string Provider,
    [property: JsonPropertyName("name")] string? Name,
    [property: JsonPropertyName("configured")] bool? Configured);

public record OAuthProviderList(
    [property: JsonPropertyName("providers")] OAuthDoor[] Providers);

public record OAuthStartOut(
    [property: JsonPropertyName("provider")] string? Provider,
    [property: JsonPropertyName("state")] string? State,
    [property: JsonPropertyName("url")] string? Url);

public record OAuthClaimOut(
    [property: JsonPropertyName("ready")] bool? Ready,
    [property: JsonPropertyName("email")] string? Email,
    [property: JsonPropertyName("account_token")] string? AccountToken);

public record PlanEntry(
    [property: JsonPropertyName("plan")] string Plan,
    [property: JsonPropertyName("title")] string? Title,
    [property: JsonPropertyName("price_usd")] double? PriceUsd,
    [property: JsonPropertyName("period")] string? Period);

public record PlanCatalog(
    [property: JsonPropertyName("plans")] PlanEntry[] Plans,
    [property: JsonPropertyName("billing")] string? Billing);

public record SubscriptionRow(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("subject_kind")] string? SubjectKind,
    [property: JsonPropertyName("subject_id")] string? SubjectId,
    [property: JsonPropertyName("tier")] string? Tier,
    [property: JsonPropertyName("status")] string? Status,
    [property: JsonPropertyName("periods")] int? Periods);

public record SubscriptionList(
    [property: JsonPropertyName("subscriptions")]
    SubscriptionRow[] Subscriptions);

public record OrderRow(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("listing_id")] string? ListingId,
    [property: JsonPropertyName("price")] double? Price,
    [property: JsonPropertyName("status")] string? Status);

public record OrderList(
    [property: JsonPropertyName("orders")] OrderRow[] Orders);

public record DesigneeRow(
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("kind")] string? Kind,
    [property: JsonPropertyName("share")] int? Share);

public record ProceedsCard(
    [property: JsonPropertyName("profile_id")] string? ProfileId,
    [property: JsonPropertyName("proceeds_to")] DesigneeRow[] ProceedsTo);

public record CampaignRow(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("title")] string? Title,
    [property: JsonPropertyName("cause")] string? Cause,
    [property: JsonPropertyName("goal")] double? Goal,
    [property: JsonPropertyName("raised")] double? Raised,
    [property: JsonPropertyName("donors")] int? Donors,
    [property: JsonPropertyName("status")] string? Status);

public record CloudStatusCard(
    [property: JsonPropertyName("cloud")] bool Cloud,
    [property: JsonPropertyName("fallback")] string? Fallback,
    [property: JsonPropertyName("contribution")] string? Contribution);

public record OfflineStatusCard(
    [property: JsonPropertyName("offline")] bool? Offline,
    [property: JsonPropertyName("provider")] string? Provider,
    [property: JsonPropertyName("cloud_attached")] bool? CloudAttached,
    [property: JsonPropertyName("external_transmission_possible")]
    bool? ExternalTransmissionPossible);

public record LightRow(
    [property: JsonPropertyName("light")] string Light,
    [property: JsonPropertyName("labels")] string[]? Labels,
    [property: JsonPropertyName("statuses")] string[]? Statuses);

public record LightsLegend(
    [property: JsonPropertyName("order")] string[] Order,
    [property: JsonPropertyName("legend")] LightRow[] Legend,
    [property: JsonPropertyName("question")] string? Question);

public record HelpTopicList(
    [property: JsonPropertyName("topics")] string[] Topics,
    [property: JsonPropertyName("disclosure")] string? Disclosure);

public record HelpAnswer(
    [property: JsonPropertyName("answer")] string Answer,
    [property: JsonPropertyName("source")] string? Source,
    [property: JsonPropertyName("ai")] bool? Ai,
    [property: JsonPropertyName("refused")] bool? Refused);

public record LocalProviderRow(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("name")] string? Name,
    [property: JsonPropertyName("area")] string? Area,
    [property: JsonPropertyName("location")] string? Location,
    [property: JsonPropertyName("business")] bool? Business);

public record FeedPage(
    [property: JsonPropertyName("items")] List<FeedCard>? Items,
    [property: JsonPropertyName("cursor")] string? Cursor);

/// <summary>One card of the public stream. <c>Plays</c> is the server's
/// word: false means nothing loads until a person presses it.</summary>
public record FeedCard(
    [property: JsonPropertyName("id")] string? Id,
    [property: JsonPropertyName("kind")] string? Kind,
    [property: JsonPropertyName("reason")] string? Reason,
    [property: JsonPropertyName("title")] string? Title,
    [property: JsonPropertyName("note")] string? Note,
    [property: JsonPropertyName("plays")] bool? Plays,
    [property: JsonPropertyName("loop")] bool? Loop,
    [property: JsonPropertyName("src")] string? Src,
    [property: JsonPropertyName("facade")] FeedFacade? Facade,
    [property: JsonPropertyName("topic")] string? Topic,
    [property: JsonPropertyName("entering")] string? Entering,
    [property: JsonPropertyName("display_name")] string? DisplayName,
    [property: JsonPropertyName("trade")] string? Trade,
    [property: JsonPropertyName("presence")] string? Presence,
    [property: JsonPropertyName("ringing")] string? Ringing,
    [property: JsonPropertyName("human")] bool? Human,
    [property: JsonPropertyName("ai")] bool? Ai);

public record FeedFacade(
    [property: JsonPropertyName("platform_name")] string? PlatformName,
    [property: JsonPropertyName("url")] string? Url);

public record BeaconOverlayCard(
    [property: JsonPropertyName("profile_id")] string? ProfileId,
    [property: JsonPropertyName("display_name")] string? DisplayName,
    [property: JsonPropertyName("watermark")] string? Watermark,
    [property: JsonPropertyName("age_wall")] bool? AgeWall,
    [property: JsonPropertyName("note")] string? Note);

public record DeskScanCard(
    [property: JsonPropertyName("desk_id")] string? DeskId,
    [property: JsonPropertyName("display_name")] string? DisplayName,
    [property: JsonPropertyName("trade")] string? Trade);

public record SocialBeaconCard(
    [property: JsonPropertyName("connection")] string Connection,
    [property: JsonPropertyName("platform")] string? Platform,
    [property: JsonPropertyName("handle")] string? Handle,
    [property: JsonPropertyName("presence_url")] string? PresenceUrl);

public record PairCard(
    [property: JsonPropertyName("console_url")] string? ConsoleUrl,
    [property: JsonPropertyName("console_built")] bool? ConsoleBuilt,
    [property: JsonPropertyName("reachable")] bool? Reachable);

public record HeldMessage(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("interactor_id")] string? InteractorId,
    [property: JsonPropertyName("content")] string? Content,
    [property: JsonPropertyName("status")] string? Status);

public record ModerationOut(
    [property: JsonPropertyName("id")] string? Id,
    [property: JsonPropertyName("status")] string? Status);

public record ReviewRating(
    [property: JsonPropertyName("average")] double? Average,
    [property: JsonPropertyName("count")] int? Count);

public record ReviewRow(
    [property: JsonPropertyName("interactor_id")] string? InteractorId,
    [property: JsonPropertyName("rating")] int? Rating,
    [property: JsonPropertyName("body")] string? Body);

public record ReviewBoard(
    [property: JsonPropertyName("profile_id")] string? ProfileId,
    [property: JsonPropertyName("rating")] ReviewRating? Rating,
    [property: JsonPropertyName("reviews")] ReviewRow[] Reviews);

public record ReviewOut(
    [property: JsonPropertyName("interactor_id")] string? InteractorId,
    [property: JsonPropertyName("rating")] int? Rating);

public record WatermarkCredential(
    [property: JsonPropertyName("watermark_id")] string? WatermarkId,
    [property: JsonPropertyName("profile_id")] string? ProfileId,
    [property: JsonPropertyName("kind")] string? Kind,
    [property: JsonPropertyName("valid")] bool? Valid,
    [property: JsonPropertyName("content_match")] bool? ContentMatches);

// One limit per kind of media, not one limit and a list of kinds: video is
// allowed sixty megabytes where an image gets eight, and a single `max_bytes`
// could only ever have been one of them.
public record MediaLimit(
    [property: JsonPropertyName("max_bytes")] long? MaxBytes,
    [property: JsonPropertyName("types")] string[]? Types);

public record MediaLimitsCard(
    [property: JsonPropertyName("image")] MediaLimit? Image,
    [property: JsonPropertyName("video")] MediaLimit? Video,
    [property: JsonPropertyName("file")] MediaLimit? File,
    [property: JsonPropertyName("detected_from")] string? DetectedFrom);

public record MediaOut(
    [property: JsonPropertyName("id")] string? Id,
    [property: JsonPropertyName("kind")] string? Kind,
    [property: JsonPropertyName("ai_marked")] bool? AiMarked);

public record VideoPlatformBoard(
    [property: JsonPropertyName("platforms")] string[]? Platforms,
    [property: JsonPropertyName("note")] string? Note);

public record WearableRow(
    [property: JsonPropertyName("name")] string? Name,
    [property: JsonPropertyName("kind")] string? Kind,
    [property: JsonPropertyName("faces")] string[]? Faces,
    [property: JsonPropertyName("revoked")] bool? Revoked);

public record WearableBoard(
    [property: JsonPropertyName("profile_id")] string? ProfileId,
    [property: JsonPropertyName("wearables")] WearableRow[] Wearables,
    [property: JsonPropertyName("faces")]
    System.Collections.Generic.Dictionary<string, string>? Faces,
    [property: JsonPropertyName("kinds_worn")]
    System.Collections.Generic.Dictionary<string, string>? KindsWorn,
    [property: JsonPropertyName("refusal_reasons")]
    System.Collections.Generic.Dictionary<string, string>? RefusalReasons);

public record GenesisOut(
    [property: JsonPropertyName("id")] string? Id,
    [property: JsonPropertyName("display_name")] string? DisplayName,
    [property: JsonPropertyName("kind")] string? Kind);

public record PackOut(
    [property: JsonPropertyName("id")] string? Id,
    [property: JsonPropertyName("title")] string? Title,
    [property: JsonPropertyName("industry")] string? Industry);

public record PackSeedOut(
    [property: JsonPropertyName("created")] int? Created,
    [property: JsonPropertyName("packs")] int? Packs);

public record SimulationOut(
    [property: JsonPropertyName("id")] string? Id,
    [property: JsonPropertyName("scenario")] string? Scenario,
    [property: JsonPropertyName("narrative")] string? Narrative);

public record FinetuneOut(
    [property: JsonPropertyName("id")] string? Id,
    [property: JsonPropertyName("interactors")] int? Interactors,
    [property: JsonPropertyName("messages_processed")] int? MessagesProcessed,
    [property: JsonPropertyName("external_transmission")]
    bool? ExternalTransmission,
    [property: JsonPropertyName("computed")] string? Computed);

public record ContributionRow(
    [property: JsonPropertyName("ref")] string? Ref,
    [property: JsonPropertyName("revoked")] bool? Revoked);

public record ContributionView(
    [property: JsonPropertyName("opted_in")] bool? Enabled,
    [property: JsonPropertyName("contributed")]
    ContributionRow[]? Contributed);

public record RevokeOut(
    [property: JsonPropertyName("revoked_count")] int? RevokedCount,
    [property: JsonPropertyName("deleted_at_gateway")]
    bool? DeletedAtGateway);

public record ExcursionOut(
    [property: JsonPropertyName("id")] string? Id,
    [property: JsonPropertyName("topic")] string? Topic,
    [property: JsonPropertyName("status")] string? Status,
    [property: JsonPropertyName("findings")] string? Findings);

public record CheckinOut(
    [property: JsonPropertyName("message")] string? Message,
    [property: JsonPropertyName("reason")] string? Reason);

public record QuietHoursOut(
    [property: JsonPropertyName("id")] string? Id,
    [property: JsonPropertyName("quiet_start")] int? QuietStart,
    [property: JsonPropertyName("quiet_end")] int? QuietEnd);

public record FeedbackOut(
    [property: JsonPropertyName("rating")] string? Rating);

public record ReferralRow(
    [property: JsonPropertyName("id")] string? Id,
    [property: JsonPropertyName("provider_id")] string? ProviderId,
    [property: JsonPropertyName("released")] bool? Released,
    [property: JsonPropertyName("opened_at")] string? OpenedAt);

public record LicenseGrantOut(
    [property: JsonPropertyName("id")] string? Id,
    [property: JsonPropertyName("profile_id")] string? ProfileId,
    [property: JsonPropertyName("price")] double? Price);

public record PerceiveWatermark(
    [property: JsonPropertyName("line")] string? Line);

public record PerceiveOut(
    [property: JsonPropertyName("guidance")] string? Guidance,
    [property: JsonPropertyName("watermark")]
    PerceiveWatermark? Watermark);

public record MicPlace(
    [property: JsonPropertyName("surface")] string? Surface,
    [property: JsonPropertyName("why")] string? Why);

public record MicPlacesOut(
    [property: JsonPropertyName("places")] MicPlace[]? Places);

public record RefusedKind(
    [property: JsonPropertyName("kind")] string? Kind,
    [property: JsonPropertyName("why")] string? Why);

public record MicVocabularyOut(
    [property: JsonPropertyName("personal")] string[]? Personal,
    [property: JsonPropertyName("refusals")] RefusedKind[]? Refusals,
    [property: JsonPropertyName("rules")] string[]? Rules);

public record OverlayKind(
    [property: JsonPropertyName("kind")] string? Kind,
    [property: JsonPropertyName("covers_face")] bool? CoversFace,
    [property: JsonPropertyName("means")] string? Means);

public record OverlayCatalogue(
    [property: JsonPropertyName("kinds")] OverlayKind[]? Kinds,
    [property: JsonPropertyName("refusals")] RefusedKind[]? Refusals,
    [property: JsonPropertyName("rules")] string[]? Rules);

public record ExperienceEntryOut(
    [property: JsonPropertyName("title")] string? Title,
    [property: JsonPropertyName("org")] string? Org,
    [property: JsonPropertyName("period")] string? Period);

public record ExperienceOut(
    [property: JsonPropertyName("profile_id")] string? ProfileId,
    [property: JsonPropertyName("experience")]
    ExperienceEntryOut[] Experience);

public record HealthOut(
    [property: JsonPropertyName("status")] string? Status,
    [property: JsonPropertyName("cloud")] bool? Cloud,
    [property: JsonPropertyName("offline")] bool? Offline);

public record RemovedOut(
    [property: JsonPropertyName("removed")] bool? Removed);

public record DeskJoinOut(
    [property: JsonPropertyName("mode")] string? Mode,
    [property: JsonPropertyName("status")] string? Status,
    [property: JsonPropertyName("room_id")] string? RoomId);
