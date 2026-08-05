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
    [property: JsonPropertyName("threshold")] VoiceThreshold Threshold,
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
    [property: JsonPropertyName("reattested")] int Reattested);

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

public record SteeringHubState(
    [property: JsonPropertyName("adult_mode")] bool AdultMode,
    [property: JsonPropertyName("dials")] SteeringDial[] Dials,
    [property: JsonPropertyName("values")] System.Collections.Generic.Dictionary<string, int> Values,
    [property: JsonPropertyName("age")] SteeringAgeBlock Age,
    [property: JsonPropertyName("appearance")] SteeringAppearance Appearance);

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
    [property: JsonPropertyName("total")] double Total,
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
    [property: JsonPropertyName("available")] int Available,
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

    public Task<Coordination> Coordinate(string orgId, string goal,
        string token) =>
        Send<Coordination>(Post($"/organizations/{orgId}/coordinate",
            new { goal }, token));

    public Task<Coordination[]> Coordinations(string orgId, string token) =>
        Send<Coordination[]>(Get($"/organizations/{orgId}/coordinations",
            token));

    public Task<TutorialOutline> TutorialOutline() =>
        Send<TutorialOutline>(Get("/tutorial"));

    public Task<TutorialStep> TutorialStepOf(string key) =>
        Send<TutorialStep>(Get($"/tutorial/steps/{key}"));

    public Task<TutorialStep> TutorialForScreen(int number) =>
        Send<TutorialStep>(Get($"/tutorial/for-screen/{number}"));

    public Task<TutorialStep> StartTutorial(string learnerId) =>
        Send<TutorialStep>(Post("/tutorial/start",
            new { learner_id = learnerId, lesson = "" }));

    public Task<TutorialStep> TutorialProgress(string learnerId) =>
        Send<TutorialStep>(Get($"/tutorial/progress/{learnerId}"));

    public Task<TutorialStep> MarkTutorialDone(string learnerId,
        string lesson) =>
        Send<TutorialStep>(Post("/tutorial/done",
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

    public Task<DeskCard> OpenDesk(string ownerId, string displayName,
                                   string trade, string attestor,
                                   string basis, string location,
                                   string blurb, string token) =>
        Send<DeskCard>(Post("/desks", new {
            owner_id = ownerId, display_name = displayName, trade, attestor,
            basis, location, blurb }, token));

    public Task<DeskCard> SetDeskPresence(string deskId, string presence,
                                          string token) =>
        Send<DeskCard>(Put($"/desks/{deskId}/presence", new { presence },
                           token));

    public Task<DeskCard> SetDeskPortrait(string deskId, string token) =>
        Send<DeskCard>(Put($"/desks/{deskId}/portrait",
                           new { asset = (string?)null }, token));

    public Task<DeskCard> SetDeskCamera(string deskId, bool enabled,
                                        string token) =>
        Send<DeskCard>(Put($"/desks/{deskId}/camera", new { enabled },
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
        return _http.SendAsync(req).ContinueWith(r =>
            r.Result.Content.ReadAsByteArrayAsync().Result);
    }

    /// <summary>What the desk looks like right now, as a still.</summary>
    public Task<byte[]> DeskView(string deskId)
    {
        var req = new HttpRequestMessage(HttpMethod.Get,
            $"/desks/{deskId}/view.webp");
        return _http.SendAsync(req).ContinueWith(r =>
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
                                                string locality,
                                                string[] tags, string token) =>
        Send<MarketListed>(Post($"/profiles/{profileId}/marketplace",
            new { blurb, locality, tags }, token));

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

    public Task<MarketOffer> SetListingOffer(string listingId, double amount,
                                             double? acceptPrice,
                                             string token) =>
        Send<MarketOffer>(Put($"/marketplace/listings/{listingId}/offer",
            new { amount, currency = "USD", accept_price = acceptPrice },
            token));

    public Task<MarketOffer> ClearListingOffer(string listingId, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete,
            $"/marketplace/listings/{listingId}/offer");
        req.Headers.Add("authorization", $"Bearer {token}");
        return Send<MarketOffer>(req);
    }

    public Task<MarketOffer> PlaceListing(string listingId, string venue,
                                          string token) =>
        Send<MarketOffer>(Put($"/marketplace/listings/{listingId}/place",
            new { venue }, token));

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
                                                  bool showOffers,
                                                  string token) =>
        Send<MarketSettings>(Put($"/marketplace/settings/{interactorId}",
            new { show_offers = showOffers }, token));

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
                                                    string token) =>
        Send<ExchangeItemRow>(Post(
            $"/exchanges/{exchangeId}/items/{itemId}/accept", new { }, token));

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

public record LicenseGrant(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("buyer_id")] string BuyerId,
    [property: JsonPropertyName("kind")] string Kind,
    [property: JsonPropertyName("derived_profile_id")] string? DerivedProfileId,
    [property: JsonPropertyName("revoked")] bool Revoked);

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

        // The other half of the accountless screen's language. `L10n` covers
        // the words this shell owns; every sentence the *backend* composes for
        // somebody with no profile is chosen from this header, and no native
        // shell was sending it.
        req.Headers.TryAddWithoutValidation("accept-language", L10n.DeviceLanguage());

        HttpResponseMessage res;
        try
        {
            res = await _http.SendAsync(req);
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
        var res = await _http.SendAsync(Post("/feedback", body, token));
        res.EnsureSuccessStatusCode();
        return "received";
    }

    public Task<FeedbackState> Feedback(string? token)
    {
        var req = new HttpRequestMessage(HttpMethod.Get, "/feedback");
        if (token is { Length: > 0 }) req.Headers.Add("authorization", $"Bearer {token}");
        return Send<FeedbackState>(req);
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
        var res = await _http.SendAsync(req);
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
        var res = await _http.SendAsync(req);
        res.EnsureSuccessStatusCode();
    }

    public async Task EndConnection(string cid, string interactorId, string token)
    {
        var req = Post($"/connections/{cid}/end?interactor_id={interactorId}",
                       new { }, token);
        var res = await _http.SendAsync(req);
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
        var res = await _http.SendAsync(req);
        res.EnsureSuccessStatusCode();
    }

    public async Task RoomAdvance(string roomId, string token)
    {
        var req = Post($"/rooms/{roomId}/advance", new { }, token);
        var res = await _http.SendAsync(req);
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
        var res = await _http.SendAsync(req);
        res.EnsureSuccessStatusCode();
    }

    public async Task SocialPublish(string cid, string token, string content)
    {
        var req = Post($"/social/{cid}/publish", new { content }, token);
        var res = await _http.SendAsync(req);
        res.EnsureSuccessStatusCode();
    }

    public async Task RevokeSocial(string cid, string token)
    {
        var req = new HttpRequestMessage(HttpMethod.Delete, $"/social/{cid}");
        req.Headers.Add("authorization", $"Bearer {token}");
        var res = await _http.SendAsync(req);
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
        var res = await _http.SendAsync(req);
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
        var res = await _http.SendAsync(
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
        var res = await _http.SendAsync(
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
        (await _http.SendAsync(req)).EnsureSuccessStatusCode();
    }

    public async Task UninstallRobotPack(string packId, string robotId, string token)
    {
        var req = new HttpRequestMessage(
            HttpMethod.Delete, $"/robots/{robotId}/packs/{packId}");
        req.Headers.Add("authorization", $"Bearer {token}");
        (await _http.SendAsync(req)).EnsureSuccessStatusCode();
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
        var res = await _http.SendAsync(Post($"/gaming/sessions/{sid}/end", new { }, token));
        res.EnsureSuccessStatusCode();
    }

    public Task<Listing[]> Listings(string tag) =>
        Send<Listing[]>(new HttpRequestMessage(HttpMethod.Get,
            tag is { Length: > 0 }
                ? $"/marketplace/listings?tag={Uri.EscapeDataString(tag)}"
                : "/marketplace/listings"));

    public async Task RemoveListing(string lid)
    {
        var res = await _http.SendAsync(
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
        var res = await _http.SendAsync(req);
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
        var res = await _http.SendAsync(req);
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
        var res = await _http.SendAsync(req);
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
    [property: JsonPropertyName("seen")] int Seen);

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


public record DeskCard(
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
    [property: JsonPropertyName("show_offers")] bool? ShowOffers);

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
    [property: JsonPropertyName("total")] double Total);

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

public record LeaveOut([property: JsonPropertyName("left")] bool? Left);

public record WhoseCard(
    [property: JsonPropertyName("display_name")] string? DisplayName,
    [property: JsonPropertyName("anonymous")] bool? Anonymous);

public record LentRow(
    [property: JsonPropertyName("interactor_id")] string? InteractorId,
    [property: JsonPropertyName("device")] string? Device);

public record MicDisclosure(
    [property: JsonPropertyName("lent")] LentRow[]? Lent);

public record WornRow(
    [property: JsonPropertyName("interactor_id")] string? InteractorId,
    [property: JsonPropertyName("kind")] string? Kind,
    [property: JsonPropertyName("title")] string? Title);

public record WornDisclosure(
    [property: JsonPropertyName("worn")] WornRow[]? Worn);

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

public record Coordination(
    [property: JsonPropertyName("id")] string? Id,
    [property: JsonPropertyName("goal")] string? Goal,
    [property: JsonPropertyName("status")] string? Status);

public record TutorialChapter(
    [property: JsonPropertyName("key")] string? Key,
    [property: JsonPropertyName("title")] string? Title);

public record TutorialOutline(
    [property: JsonPropertyName("chapters")] TutorialChapter[]? Chapters,
    [property: JsonPropertyName("lessons")] TutorialChapter[]? Lessons);

public record TutorialStep(
    [property: JsonPropertyName("key")] string? Key,
    [property: JsonPropertyName("title")] string? Title,
    [property: JsonPropertyName("body")] string? Body,
    [property: JsonPropertyName("next")] string? Next);

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

public record LobbyLeft([property: JsonPropertyName("left")] bool? Left);

public record LobbyContext(
    [property: JsonPropertyName("note")] string? Note);

public record DockFacesBox(
    [property: JsonPropertyName("faces")] string[]? Faces);

public record DockWhere(
    [property: JsonPropertyName("screen")] string? Screen,
    [property: JsonPropertyName("tab")] string? Tab);

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

public record DisplayVocabulary(
    [property: JsonPropertyName("never")]
    System.Collections.Generic.Dictionary<string, string>? Never);

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
    [property: JsonPropertyName("phases")] string[]? Phases,
    [property: JsonPropertyName("enabled")] bool? Enabled);

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
