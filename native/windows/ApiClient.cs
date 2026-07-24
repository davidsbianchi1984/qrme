using System;
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

public record Post(
    [property: JsonPropertyName("id")] string Id,
    [property: JsonPropertyName("topic")] string? Topic,
    [property: JsonPropertyName("content")] string? Content,
    [property: JsonPropertyName("status")] string? Status,
    [property: JsonPropertyName("provenance")] ContentProvenance? Provenance);

public record LanguageInfo(
    [property: JsonPropertyName("code")] string Code,
    [property: JsonPropertyName("label")] string Label);

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

public record InteractorCreated(
    [property: JsonPropertyName("id")] string Id);

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
    [property: JsonPropertyName("flag_reason")] string? FlagReason);

public record ChatReply(
    [property: JsonPropertyName("profile_message")] ChatMessage ProfileMessage,
    [property: JsonPropertyName("provenance")] ContentProvenance? Provenance);

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
        var res = await _http.SendAsync(req);
        var body = await res.Content.ReadAsStringAsync();
        if (!res.IsSuccessStatusCode)
        {
            string? detail = null;
            try { detail = JsonDocument.Parse(body).RootElement.GetProperty("detail").GetString(); }
            catch { /* non-JSON error body */ }
            throw new HttpRequestException(detail ?? $"HTTP {(int)res.StatusCode}");
        }
        return JsonSerializer.Deserialize<T>(body)!;
    }

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

    public Task<ChatReply> Chat(string id, string token, string interactorId,
                                string message) =>
        Send<ChatReply>(Post($"/profiles/{id}/chat",
            new { interactor_id = interactorId, message }, token));

    // -- community: stranger connections & multiparty rooms --

    public Task<ConnJoin> JoinQueue(string interactorId, string alias,
                                    string tier = "friendly") =>
        Send<ConnJoin>(Post("/connections/join",
            alias is { Length: > 0 }
                ? new { interactor_id = interactorId, tier, alias }
                : (object)new { interactor_id = interactorId, tier }));

    public Task<ConnMsg[]> ConnectionMessages(string cid, string interactorId) =>
        Send<ConnMsg[]>(new HttpRequestMessage(
            HttpMethod.Get, $"/connections/{cid}/messages?interactor_id={interactorId}"));

    public async Task SendConnectionMessage(string cid, string interactorId, string message)
    {
        var req = Post($"/connections/{cid}/messages",
            new { interactor_id = interactorId, message });
        var res = await _http.SendAsync(req);
        res.EnsureSuccessStatusCode();
    }

    public async Task EndConnection(string cid, string interactorId)
    {
        var req = Post($"/connections/{cid}/end?interactor_id={interactorId}", new { });
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

    public async Task RoomMessage(string roomId, string senderId, string message)
    {
        var req = Post($"/rooms/{roomId}/messages", new { sender_id = senderId, message });
        var res = await _http.SendAsync(req);
        res.EnsureSuccessStatusCode();
    }

    public async Task RoomAdvance(string roomId)
    {
        var req = Post($"/rooms/{roomId}/advance", new { });
        var res = await _http.SendAsync(req);
        res.EnsureSuccessStatusCode();
    }

    public Task<RoomMsg[]> RoomTranscript(string roomId) =>
        Send<RoomMsg[]>(new HttpRequestMessage(HttpMethod.Get, $"/rooms/{roomId}/messages"));

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

    public Task<HandleClaim> ClaimHandle(string id, string handle)
    {
        var req = new HttpRequestMessage(HttpMethod.Put, $"/profiles/{id}/handle")
        {
            Content = JsonContent.Create(new { handle }),
        };
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
}
