import Foundation

// MARK: - Wire models (mirror qrme/models.py + routers)

struct ProfileCreated: Decodable {
    let id: String
    let display_name: String
    let kind: String
    let owner_token: String
}

struct ProfileCard: Decodable {
    let id: String
    let display_name: String
    let kind: String
    let status: String?
}

struct Post: Decodable {
    let id: String
    let topic: String?
    let content: String?
    let status: String?
    let surface: String?
    let provenance: ContentProvenance?
    let watermark: WatermarkBrief?
}

struct Health: Decodable { let status: String }

// MARK: Live desks — a real person, so never an AI watermark

struct DeskFeed: Decodable {
    let url: String
    let live: Bool
    let note: String
}

struct DeskAttestation: Decodable {
    let attestor: String
    let basis: String
    let signed: Bool
    let note: String
}

struct DeskBell: Decodable { let available: Bool; let waiting: Int }

struct DeskCard: Decodable {
    let desk_id: String
    // Present only past the age wall — an unverified viewer of an 18+ stream
    // gets existence and nothing else.
    let age_wall: Bool?
    let rated: Bool?
    let display_name: String?
    let trade: String?
    let location: String?
    let blurb: String?
    let presence: String?
    let human: Bool
    let ai: Bool
    let designation: String?
    let attestation: DeskAttestation?
    let portrait: String?
    let feed: DeskFeed?
    let bell: DeskBell?
    let note: String?
}

struct StreamJoin: Decodable {
    let room_id: String
    let channel: String
    let presence: String
    let ai: Bool
    let note: String
}


struct DeskConnection: Decodable, Identifiable {
    let id: String
    let session_id: String
    let kind: String
    let target: String
    let scope: String?
    let status: String
    let means: String?
    // The caller's view of an active link only — the desk's never carries it.
    let token: String?
}

struct DeskSession: Decodable, Identifiable {
    let id: String
    let desk_id: String
    let caller_id: String
    let status: String
    let desk_name: String?
    let trade: String?
    let connections: [DeskConnection]
}

struct RingReceipt: Decodable {
    let ring_id: String
    let waiting: Int
    let presence: String
    let note: String
}

// MARK: Signatures

struct SignaturePolicy: Decodable {
    let proofing_levels: [String]
    let standard: String
    let limits: [String]
}

struct EnrollUser: Decodable { let id: String; let name: String; let displayName: String }
struct EnrollRp: Decodable { let id: String; let name: String }

struct EnrollOptions: Decodable {
    let challenge: String
    let rp: EnrollRp
    let user: EnrollUser
}

struct SigningCredential: Decodable, Identifiable {
    let id: String
    let credential_id: String
    let proofing_level: String
    let display_name: String?
    let backup_eligible: Bool
    let device_bound: Bool
    let can_sign: [String]
    let revoked_at: String?
}

struct SignatureEnvelope: Decodable {
    let envelope_id: String
    let challenge: String
    let display_text: String
    let meaning: String
    let tier: String
    let expires_at: String
}

struct SignatureVerification: Decodable { let valid: Bool; let notes: [String] }

struct SignatureReceipt: Decodable {
    let signature_id: String
    let meaning: String?
    let signed_at: String
    let tier: String
    let verification: SignatureVerification
    let limits: [String]
}

struct ProviderInfo: Decodable {
    let name: String
    let label: String
    let configured: Bool
}

struct ModelsList: Decodable {
    let providers: [ProviderInfo]
    let defaultName: String
    enum CodingKeys: String, CodingKey {
        case providers
        case defaultName = "default"
    }
}

struct ModelChoice: Decodable { let provider: String; let effective: String }

struct RobotSpec: Decodable {
    let model: String
    let label: String
    let maker: String
    let kind: String
    let llm_capable: Bool
}

struct RoboticsCatalog: Decodable { let robots: [RobotSpec] }

struct Robot: Decodable {
    let id: String
    let model: String
    let name: String
    let status: String?
    let commands: [String]?
}

struct CommandResult: Decodable {
    let command: String
    let status: String
    let spoken: String?
}

struct Objection: Decodable {
    let id: String
    let status: String
    let reason: String?
    let reattested: Int
}

/// What comes back from raising an objection. `profile_status` is the part
/// that matters to the person raising it: the profile is restricted straight
/// away, pending review, rather than after somebody gets round to it.
struct ObjectionOpened: Decodable {
    let id: String
    let profile_id: String
    let status: String
    let profile_status: String?
    /// What it was before, so the sentence can say what a dismissal
    /// restores. Returned since objections shipped; no shell read it.
    let prior_status: String?
    let note: String?
}

struct InteractorCreated: Decodable { let id: String; let token: String? }

struct SteeringDial: Decodable, Identifiable {
    let name: String
    let group: String        // system | behavior | intimacy
    let label: String
    let low: String
    let high: String
    let min: Int
    let max: Int
    var id: String { name }
}

struct SteeringAgeBlock: Decodable {
    let base_age: Int?
    let aging_enabled: Bool
    let effective_age: Int?
}

struct SteeringAppearance: Decodable { let description: String? }

struct SteeringHubState: Decodable {
    let adult_mode: Bool
    let dials: [SteeringDial]
    let values: [String: Int]
    let age: SteeringAgeBlock
    let appearance: SteeringAppearance
}

struct LedgerEntry: Decodable, Identifiable {
    let id: String
    let kind: String         // pack_sale | license_fee | placement | …
    let memo: String?
    let amount: Double
    let status: String       // accrued | paid
    let created_at: String?
}

struct EarningsTotals: Decodable {
    let accrued: Double
    let paid: Double
    let lifetime: Double
    let by_kind: [String: Double]
}

struct EarningsStatement: Decodable {
    let entries: [LedgerEntry]
    let totals: EarningsTotals
    let currency: String
}

struct PayoutReceipt: Decodable {
    let payout_id: String
    let total: Double
    let entries: Int
}

// MARK: Voiceprint (FIG. 800)

struct VoiceConsentState: Decodable {
    let granted: Bool
    let sources: [String]?
    let granted_at: String?
    let note: String?
}

struct VoiceThreshold: Decodable {
    let samples: Int
    let seconds: Double
}

/// What the enrolled material actually amounts to. Everything here is a count
/// off the samples — there is no opaque quality score to hide behind.
struct VoiceEnrollment: Decodable {
    let samples: Int
    let seconds: Double
    let turns: Int
    let mean_turn_seconds: Double?
    let ready: Bool
    let needs: [String]
    let threshold: VoiceThreshold
    let method: String
}

struct VoiceprintRecord: Decodable {
    let id: String
    let built_at: String?
    let retired_at: String?
    let active: Bool
}

struct VoiceprintStatus: Decodable {
    let consent: VoiceConsentState
    let enrollment: VoiceEnrollment?
    let voiceprint: VoiceprintRecord?
    let disclosure: String
}

struct VoiceRevocation: Decodable {
    let revoked: Bool
    let samples_deleted: Int
    let note: String
}

struct VoiceSpoken: Decodable {
    let voiceprint_id: String
    let basis: String
    let disclosure: String
    let revocable: Bool
}

struct RelationshipState: Decodable {
    let relationship_type: String
    let nickname: String?
    let tone: String?
}

struct ChatMessage: Decodable {
    let id: String
    let role: String
    let content: String?
    let status: String
    let flag_reason: String?
    let watermark: WatermarkBrief?
}

/// The visible mark riding on every AI render (always displayed).
struct WatermarkDisplay: Decodable { let line: String }

struct WatermarkBrief: Decodable {
    let watermark_id: String?
    let display: WatermarkDisplay?
}

struct WatermarkDesign: Decodable {
    let mark: String
    let label: String
    let line: String
    let custom: Bool
}

struct GroundedIn: Decodable { let persona: Bool; let source_items: Int }

struct ModerationInfo: Decodable {
    let maturity: String
    let status: String
    let flag_reason: String?
}

struct ContentProvenance: Decodable {
    let method: String
    let generated_by: String
    let language: String
    let grounded_in: GroundedIn
    let licensed_from: String?
    let moderation: ModerationInfo
    let disclaimer: String
}

struct ChatReply: Decodable {
    let interactor_message: ChatMessage
    let profile_message: ChatMessage
    let provenance: ContentProvenance?
    /// Spec clauses 2/12 — which way the profile worked this turn, and whether
    /// the owner declared it or the wording implied it.
    let role_context: RoleContext?
}

struct RoleContext: Decodable {
    let role: String
    /// "declared" or "inferred": the reply says which, so an inference is never
    /// mistaken for an instruction.
    let how: String
}

// MARK: Extract and reconstruct — whose work is this, from the text alone

struct WatermarkRecovery: Decodable {
    let recovered: Bool
    let reason: String?
    let profile_id: String?
    let watermark_id: String?
    let verbatim: Bool?
    let similarity: Double?
    let matched_windows: Int?
    let stored_windows: Int?
    let examined_windows: Int?
    /// "unaltered" or "altered but traceable" — never a bare yes.
    let state: String?
    let best_similarity: Double?
    let threshold: Double?
    let disclosure: String?
    let display: WatermarkDesign?
    let method: String?
}

struct LanguageInfo: Decodable { let code: String; let label: String }

struct LanguagesList: Decodable {
    let languages: [LanguageInfo]
    let defaultCode: String
    enum CodingKeys: String, CodingKey {
        case languages
        case defaultCode = "default"
    }
}

struct LanguageChoice: Decodable { let language: String; let label: String; let mode: String? }

struct TranslateResult: Decodable {
    let text: String
    let translation: String
    let language: String
    let engine: String
    let note: String?
}

struct SocialConn: Decodable {
    let id: String
    let platform: String
    let direction: String
    let handle: String?
    let status: String?
    let collected: Int
    let published: Int
}

struct CatalogApp: Decodable { let app: String; let label: String; let capabilities: [String] }
struct CatalogProvider: Decodable { let provider: String; let label: String; let apps: [CatalogApp] }
struct AppsCatalog: Decodable { let providers: [CatalogProvider] }

struct AppConn: Decodable {
    let id: String
    let provider: String
    let app: String
    let label: String
    let capabilities: [String]
    let status: String?
}

struct InvokeResult: Decodable {
    let capability: String
    let status: String
    let result: String
}

struct ConnJoin: Decodable {
    let status: String                 // "matched" | "waiting"
    let connection_id: String?
    let tier: String
    let matched_with: String?
}

struct ConnMsgResult: Decodable { let id: String; let status: String; let flag_reason: String? }

struct ConnMsg: Decodable {
    let id: String
    let from: String                   // "you" or the partner's alias
    let content: String
    let status: String?
}

struct RoomCreated: Decodable { let id: String; let topic: String; let channel: String; let presence: String }

struct RoomMsg: Decodable {
    let id: String
    let sender_kind: String            // "user" | "profile"
    let from: String
    let content: String?               // nil when blocked
    let status: String?
}

struct RoomPost: Decodable { let message: RoomMsg; let replies: [RoomMsg] }
struct RoomAdvance: Decodable { let replies: [RoomMsg] }

struct HandleClaim: Decodable { let profile_id: String; let handle: String; let summon: String }

struct Beacon: Decodable {
    let id: String
    let label: String
    let location: String?
    let scans: Int
    let active: Bool
}

struct BeaconPlaced: Decodable {
    let id: String
    let label: String
    let location: String?
    let summon_url: String
    let qr_svg: String
}

struct SummonCard: Decodable {
    let profile_id: String
    let display_name: String
    let handle: String?
    let purpose: String?
    let status: String
    let note: String?
}

struct SummonResult: Decodable {
    let type: String                   // "handle" | "tag" | "beacon"
    let ref: String
    let label: String?                 // beacon only
    let location: String?
    let scans: Int?
    let profile: SummonCard?           // handle / beacon
    let profiles: [SummonCard]?        // tag
}

struct Pack: Decodable {
    let id: String
    let industry: String
    let audience: String               // "profile" | "robot"
    let title: String
    let blurb: String?
    let publisher: String
    let price: Double
    let currency: String
    let free: Bool
    let origin: String                 // "local" | a registry key
    let origin_url: String?            // the federated storefront
    let items: Int
    let installs: Int
}

struct PackRegistry: Decodable {
    let key: String
    let name: String                   // e.g. "Robotmods.net"
    let url: String
    let audience: String
    let tagline: String
    let available: Int
    let synced: Int
}

struct InstalledPack: Decodable {
    let id: String
    let industry: String
    let title: String
    let publisher: String
    let price_paid: Double
    let robot_id: String?              // non-empty when installed on a body
}

struct PackInstalled: Decodable {
    let installed_items: Int?          // profile packs: knowledge items added
    let installed_tasks: [String]?     // robot packs: commandable verbs added
    let price_paid: Double

    var count: Int { installed_items ?? installed_tasks?.count ?? 0 }
}

struct FeedbackReceipt: Decodable { let id: String; let status: String; let note: String? }
struct FeedbackItem: Decodable {
    let id: String
    let category: String
    let message: String
    let status: String
}
struct FeedbackState: Decodable {
    let mine: [FeedbackItem]
    let tally: [String: Int]
    let total: Int
    let categories: [String]
}

struct GameSession: Decodable {
    let id: String
    let platform: String
    let platform_label: String?
    let game: String
    let role: String
    let status: String
    let callouts: Int?
}

struct GameCalloutResult: Decodable {
    let status: String                 // "spoken" | "held"
    let line: String?
    let flag_reason: String?
    let role: String
}

struct Listing: Decodable {
    let id: String
    let kind: String
    let title: String
    let blurb: String?
    let tags: [String]
    let area: String?
    let provider_name: String?
    let business: Bool
    let profile_id: String?
}

struct ListingCreated: Decodable { let id: String; let kind: String; let title: String }

struct LicenseOffer: Decodable {
    let profile_id: String
    let kind: String                   // consult | finetune | clone
    let price: Double
    let currency: String
    let terms: String?
    let allow_derivatives: Bool
}

struct LicenseGrant: Decodable {
    let id: String
    let buyer_id: String
    let kind: String
    let derived_profile_id: String?
    let revoked: Bool
}

struct Excursion: Decodable {
    let id: String
    let topic: String
    let brief: String
    let redactions: Int
    let left_host: Bool
    let findings: String
    let learned: Bool
}

// MARK: - Client

enum ApiError: LocalizedError {
    case http(String)
    var errorDescription: String? { if case let .http(m) = self { return m }; return nil }
}

/// Async client for the QRME backend. Defaults to the local dev server; the
/// iOS Simulator shares the host's network, so 127.0.0.1 resolves to your Mac.
actor ApiClient {
    static let shared = ApiClient()
    var base = URL(string: "http://127.0.0.1:8000")!

    func setBase(_ s: String) {
        if let u = URL(string: s.hasSuffix("/") ? String(s.dropLast()) : s) { base = u }
    }

    private func request<T: Decodable>(_ path: String, method: String = "GET",
                                       body: [String: Any]? = nil, token: String? = nil,
                                       query: [String: String]? = nil) async throws -> T {
        var url = base.appendingPathComponent(path)
        if let query, var parts = URLComponents(url: url, resolvingAgainstBaseURL: false) {
            parts.queryItems = query.map { URLQueryItem(name: $0.key, value: $0.value) }
            url = parts.url ?? url
        }
        var req = URLRequest(url: url)
        req.httpMethod = method
        req.setValue("application/json", forHTTPHeaderField: "content-type")
        // The other half of the accountless screen's language. `L10n` covers
        // the words this shell owns; every sentence the *backend* composes for
        // somebody with no profile — the objection it just opened, the profile
        // it just terminated, the timeline note — is chosen from this header,
        // and no native shell was sending it. The browser sends it for free,
        // which is exactly why the phones were the ones still answering in
        // English after the routes learned to speak.
        req.setValue(L10n.deviceLanguage, forHTTPHeaderField: "accept-language")
        if let token { req.setValue("Bearer \(token)", forHTTPHeaderField: "authorization") }
        if let body { req.httpBody = try JSONSerialization.data(withJSONObject: body) }

        let data: Data
        let resp: URLResponse
        do {
            (data, resp) = try await URLSession.shared.data(for: req)
        } catch {
            // Never reached a server. Recorded as status 0, and the thrown
            // error still carries its message to the person, who owns it —
            // the log gets the operation and nothing else.
            Problems.record(method: method, path: path, status: 0)
            throw error
        }
        guard let http = resp as? HTTPURLResponse else {
            Problems.record(method: method, path: path, status: 0)
            throw ApiError.http("No response")
        }
        guard (200..<300).contains(http.statusCode) else {
            // The status and the operation, never the detail below: these
            // messages quote what the person typed, which is theirs to read
            // and nobody's to keep.
            Problems.record(method: method, path: path, status: http.statusCode)
            // A 422 answers with a *list* of rows, not a string, so `as? String`
            // gave nil and the person saw the status code — less than they saw
            // before their language was ever considered. `message` is the
            // sentence the backend composes beside the rows; read it first.
            let body = (try? JSONSerialization.jsonObject(with: data)) as? [String: Any]
            let said = (body?["message"] as? String) ?? (body?["detail"] as? String)
            throw ApiError.http(said ?? "HTTP \(http.statusCode)")
        }
        // A 204 — or any success with an empty body — is the route saying
        // "done, nothing to report". Decoding zero bytes throws, which
        // turned every successful delete into a failure message on the
        // screen. An empty object decodes into any shape whose fields are
        // optional, and still throws for one that genuinely needed content.
        //
        //     asked     did the response parse
        //     mattered  did the request succeed
        let payload = data.isEmpty ? Data("{}".utf8) : data
        return try JSONDecoder().decode(T.self, from: payload)
    }

    func health() async throws -> Health { try await request("/health") }

    /// Create a synthetic profile (the enroll equivalent). `verification.birthdate`
    /// must be an adult past date; the owner token is returned once, here.
    func createProfile(name: String, persona: String, kind: String,
                       birthdate: String,
                       language: String? = nil) async throws -> ProfileCreated {
        var body: [String: Any] = [
            "owner_id": "owner-1",
            "kind": kind,
            "display_name": name,
            "persona": persona,
            "verification": ["birthdate": birthdate],
            "terms_consent": true,   // clickwrap: the Welcome screen displays the Terms
        ]
        if let language, language != "en" { body["language"] = language }
        return try await request("/profiles", method: "POST", body: body)
    }

    func profile(_ id: String) async throws -> ProfileCard {
        try await request("/profiles/\(id)")
    }

    /// Compose one in-character public post about `topic`. Creates a post row.
    func compose(id: String, token: String, topic: String) async throws -> Post {
        try await request("/profiles/\(id)/compose", method: "POST",
                          body: ["topic": topic], token: token)
    }

    func posts(id: String) async throws -> [Post] {
        try await request("/profiles/\(id)/posts")
    }

    // MARK: Watermark — the mark every AI render carries

    func watermarkDesign(id: String) async throws -> WatermarkDesign {
        try await request("/profiles/\(id)/watermark")
    }

    /// Design the profile's watermark. The AI designation is invariant —
    /// whatever the label, the rendered line always declares AI.
    func setWatermarkDesign(id: String, token: String, mark: String?,
                            label: String?) async throws -> WatermarkDesign {
        var body: [String: Any] = [:]
        if let mark, !mark.isEmpty { body["mark"] = mark }
        if let label, !label.isEmpty { body["label"] = label }
        return try await request("/profiles/\(id)/watermark", method: "PUT",
                                 body: body, token: token)
    }

    // MARK: Model selection (which LLM powers the profile)

    func models() async throws -> ModelsList { try await request("/models") }

    func profileModel(id: String) async throws -> ModelChoice {
        try await request("/profiles/\(id)/model")
    }

    func languages() async throws -> LanguagesList { try await request("/languages") }

    func profileLanguage(id: String) async throws -> LanguageChoice {
        try await request("/profiles/\(id)/language")
    }

    func setLanguage(id: String, token: String, code: String,
                     mode: String = "pre") async throws -> LanguageChoice {
        try await request("/profiles/\(id)/language", method: "PUT",
                          body: ["language": code, "mode": mode], token: token)
    }

    func submitFeedback(token: String?, category: String, message: String,
                        rating: Int?) async throws -> FeedbackReceipt {
        var body: [String: Any] = ["category": category, "message": message]
        if let rating { body["rating"] = rating }
        return try await request("/feedback", method: "POST", body: body,
                                 token: token)
    }

    func feedback(token: String?) async throws -> FeedbackState {
        try await request("/feedback", token: token)
    }

    func translate(id: String, token: String, text: String,
                   to: String? = nil) async throws -> TranslateResult {
        var body: [String: Any] = ["text": text]
        if let to { body["to"] = to }
        return try await request("/profiles/\(id)/translate", method: "POST",
                                 body: body, token: token)
    }

    func setModel(id: String, token: String, provider: String) async throws -> ModelChoice {
        try await request("/profiles/\(id)/model", method: "PUT",
                          body: ["provider": provider], token: token)
    }

    // MARK: Robotic embodiment

    func roboticsCatalog() async throws -> RoboticsCatalog {
        try await request("/robotics/catalog")
    }

    func robots(id: String, token: String) async throws -> [Robot] {
        try await request("/profiles/\(id)/robots", token: token)
    }

    func bindRobot(id: String, token: String, model: String) async throws -> Robot {
        try await request("/profiles/\(id)/robots", method: "POST",
                          body: ["model": model], token: token)
    }

    func commandRobot(rid: String, token: String, command: String,
                      arg: String?) async throws -> CommandResult {
        var body: [String: Any] = ["command": command]
        if let arg, !arg.isEmpty { body["arg"] = arg }
        return try await request("/robots/\(rid)/command", method: "POST",
                                 body: body, token: token)
    }

    // MARK: Connect — social platforms & the connected-apps catalog

    func socialConnections(id: String, token: String) async throws -> [SocialConn] {
        try await request("/profiles/\(id)/social", token: token)
    }

    func socialConnect(id: String, token: String, platform: String,
                       direction: String, handle: String?) async throws -> SocialConn {
        var body: [String: Any] = ["platform": platform, "direction": direction]
        if let handle, !handle.isEmpty { body["handle"] = handle }
        return try await request("/profiles/\(id)/social", method: "POST",
                                 body: body, token: token)
    }

    func socialCollect(cid: String, token: String, content: String) async throws {
        struct Ok: Decodable {}
        let _: Ok = try await request("/social/\(cid)/collect", method: "POST",
                                      body: ["items": [["content": content]]],
                                      token: token)
    }

    func socialPublish(cid: String, token: String, content: String) async throws {
        struct Ok: Decodable {}
        let _: Ok = try await request("/social/\(cid)/publish", method: "POST",
                                      body: ["content": content], token: token)
    }

    func revokeSocial(cid: String, token: String) async throws {
        struct Ok: Decodable {}
        let _: Ok = try await request("/social/\(cid)", method: "DELETE",
                                      token: token)
    }

    func appsCatalog() async throws -> AppsCatalog {
        try await request("/connectors/catalog")
    }

    func appConnections(id: String, token: String) async throws -> [AppConn] {
        try await request("/profiles/\(id)/apps", token: token)
    }

    func appConnect(id: String, token: String, provider: String,
                    app: String) async throws -> AppConn {
        try await request("/profiles/\(id)/apps", method: "POST",
                          body: ["provider": provider, "app": app], token: token)
    }

    func appCollect(cid: String, token: String, content: String) async throws {
        struct Ok: Decodable {}
        let _: Ok = try await request("/apps/\(cid)/collect", method: "POST",
                                      body: ["items": [["content": content]]],
                                      token: token)
    }

    func appInvoke(cid: String, token: String,
                   capability: String) async throws -> InvokeResult {
        try await request("/apps/\(cid)/invoke", method: "POST",
                          body: ["capability": capability], token: token)
    }

    // MARK: Objections (governance)

    /// Raise an objection against a profile. Takes **no credential**, and
    /// that is the whole point: `open_objection` says so in its own docstring
    /// — *the objecting party need not own an account*. The person this route
    /// is for has found a synthetic profile of themselves, has no QRME
    /// account, and therefore has no console. A phone is the surface they
    /// have, and until 0.23.0 it was the surface that could not do this.
    ///
    /// The shell already carried the other half — listing objections against
    /// your own profile, and attesting to them. That is the owner's side.
    func openObjection(profileId: String, objectorRef: String,
                       reason: String) async throws -> ObjectionOpened {
        try await request("/objections", method: "POST",
                          body: ["profile_id": profileId,
                                 "objector_ref": objectorRef,
                                 "reason": reason])
    }

    /// The objector's own record of their case. Public, like the route that
    /// opens one — and it had to be built, because `/audit` is owner- or
    /// reviewer-gated and the objector is neither. They could already END the
    /// profile from this screen and could not read what happened.
    ///
    ///     asked     could the audit trail leak the objector's reason
    ///     mattered  who is the audit trail for
    ///
    /// Carries no free text: event, actor, time, sealed. Nobody's prose.
    func objectionTimeline(objectionId: String) async throws -> ObjectionTimeline {
        try await request("/objections/\(objectionId)/timeline")
    }

    func objections(id: String, token: String) async throws -> [Objection] {
        try await request("/profiles/\(id)/objections", token: token)
    }

    func attest(id: String, objectionId: String, token: String) async throws {
        struct Ok: Decodable {}
        let _: Ok = try await request(
            "/profiles/\(id)/objections/\(objectionId)/attest",
            method: "POST", token: token)
    }

    // MARK: Chat (the core loop: an interactor talks with the profile)

    func createInteractor(name: String,
                          birthdate: String? = nil) async throws -> InteractorCreated {
        var body: [String: Any] = ["display_name": name]
        if let birthdate, !birthdate.isEmpty { body["birthdate"] = birthdate }
        return try await request("/interactors", method: "POST", body: body)
    }

    // MARK: Steering — the owner shapes how the profile comes across

    func steeringHub(id: String, token: String) async throws -> SteeringHubState {
        try await request("/profiles/\(id)/steering/hub", token: token)
    }

    func setSteeringHub(id: String, token: String,
                        values: [String: Int]? = nil,
                        baseAge: Int? = nil, agingEnabled: Bool? = nil,
                        appearance: String? = nil) async throws -> SteeringHubState {
        var body: [String: Any] = [:]
        if let values { body["values"] = values }
        var age: [String: Any] = [:]
        if let baseAge { age["base_age"] = baseAge }
        if let agingEnabled { age["aging_enabled"] = agingEnabled }
        if !age.isEmpty { body["age"] = age }
        if let appearance { body["appearance"] = ["description": appearance] }
        return try await request("/profiles/\(id)/steering/hub", method: "PUT",
                                 body: body, token: token)
    }

    // MARK: Earnings — the creator's statement over the ledger

    func earnings(id: String, token: String) async throws -> EarningsStatement {
        try await request("/profiles/\(id)/earnings", token: token)
    }

    func requestPayout(id: String, token: String) async throws -> PayoutReceipt {
        try await request("/profiles/\(id)/earnings/payout", method: "POST",
                          token: token)
    }

    // MARK: Relationship — how the profile relates to you

    func setRelationship(id: String, token: String, interactorId: String,
                         type: String, nickname: String?,
                         tone: String?) async throws -> RelationshipState {
        var body: [String: Any] = ["relationship_type": type]
        if let nickname, !nickname.isEmpty { body["nickname"] = nickname }
        if let tone, !tone.isEmpty { body["tone"] = tone }
        return try await request("/profiles/\(id)/relationships/\(interactorId)",
                                 method: "PUT", body: body, token: token)
    }

    /// `role` is optional on purpose: left nil the profile reads the wording and
    /// decides for itself, and the reply reports which way it went.
    func chat(id: String, token: String, interactorId: String,
              message: String, role: String? = nil) async throws -> ChatReply {
        var body: [String: Any] = ["interactor_id": interactorId,
                                   "message": message]
        if let role, !role.isEmpty { body["role"] = role }
        return try await request("/profiles/\(id)/chat", method: "POST",
                                 body: body, token: token)
    }

    /// Whose work is this, from the text alone — no credential id, and it keeps
    /// answering after the text has been edited. Public: a counterparty must be
    /// able to ask without an account here.
    func recoverWatermark(content: String) async throws -> WatermarkRecovery {
        try await request("/watermarks/recover", method: "POST",
                          body: ["content": content])
    }

    // MARK: Community — stranger connections & multiparty rooms

    // Each of these carries the interactor's own token. The id says whose
    // turn it is; the token says who is asking, and only the second is
    // believed — otherwise two public ids were enough to speak as either
    // party, read the pair's whole conversation, and end it.
    func joinQueue(interactorId: String, alias: String?,
                   tier: String = "friendly",
                   token: String) async throws -> ConnJoin {
        var body: [String: Any] = ["interactor_id": interactorId, "tier": tier]
        if let alias, !alias.isEmpty { body["alias"] = alias }
        return try await request("/connections/join", method: "POST",
                                 body: body, token: token)
    }

    func connectionMessages(cid: String, interactorId: String,
                            token: String) async throws -> [ConnMsg] {
        try await request("/connections/\(cid)/messages",
                          query: ["interactor_id": interactorId], token: token)
    }

    func sendConnectionMessage(cid: String, interactorId: String,
                               message: String,
                               token: String) async throws -> ConnMsgResult {
        try await request("/connections/\(cid)/messages", method: "POST",
                          body: ["interactor_id": interactorId, "message": message],
                          token: token)
    }

    func endConnection(cid: String, interactorId: String,
                       token: String) async throws {
        struct Ok: Decodable {}
        let _: Ok = try await request("/connections/\(cid)/end", method: "POST",
                                      query: ["interactor_id": interactorId],
                                      token: token)
    }

    func createRoom(topic: String, profileId: String,
                    interactorId: String) async throws -> RoomCreated {
        try await request("/rooms", method: "POST", body: [
            "topic": topic, "channel": "chat",
            "participants": [["kind": "user", "id": interactorId],
                             ["kind": "profile", "id": profileId]],
        ])
    }

    // All three carry the interactor token now. The room routes used to take
    // none: the speaker was read out of `sender_id` in the body, so anybody
    // with a room id could post as a named participant, and the transcript
    // was readable by anybody at all. `sender_id` is still sent because the
    // server still accepts the field; it is ignored there, and the token is
    // what says who is speaking.
    func roomMessage(roomId: String, senderId: String, message: String,
                     token: String) async throws -> RoomPost {
        try await request("/rooms/\(roomId)/messages", method: "POST",
                          body: ["sender_id": senderId, "message": message],
                          token: token)
    }

    func roomAdvance(roomId: String, token: String) async throws -> RoomAdvance {
        try await request("/rooms/\(roomId)/advance", method: "POST",
                          token: token)
    }

    func roomTranscript(roomId: String, token: String) async throws -> [RoomMsg] {
        try await request("/rooms/\(roomId)/messages", token: token)
    }

    // MARK: Reach — summon (@handle + beacons), marketplace, licensing

    // The owner's token. Without it a stranger could replace the name a
    // profile answers to, and the old one stopped resolving.
    func claimHandle(id: String, handle: String,
                     token: String) async throws -> HandleClaim {
        try await request("/profiles/\(id)/handle", method: "PUT",
                          body: ["handle": handle], token: token)
    }

    func placeBeacon(id: String, label: String,
                     location: String?) async throws -> BeaconPlaced {
        var body: [String: Any] = ["label": label]
        if let location, !location.isEmpty { body["location"] = location }
        return try await request("/profiles/\(id)/beacons", method: "POST", body: body)
    }

    func beacons(id: String) async throws -> [Beacon] {
        try await request("/profiles/\(id)/beacons")
    }

    func pickUpBeacon(bid: String) async throws {
        struct Ok: Decodable {}
        let _: Ok = try await request("/beacons/\(bid)", method: "DELETE")
    }

    func summon(ref: String) async throws -> SummonResult {
        try await request("/summon", query: ["ref": ref])
    }

    func createListing(kind: String, title: String, blurb: String?, tags: [String],
                       area: String?, providerName: String,
                       profileId: String?) async throws -> ListingCreated {
        var body: [String: Any] = ["kind": kind, "title": title,
                                   "tags": tags, "provider_name": providerName]
        if let blurb, !blurb.isEmpty { body["blurb"] = blurb }
        if let area, !area.isEmpty { body["area"] = area }
        if let profileId { body["profile_id"] = profileId }
        return try await request("/marketplace/listings", method: "POST", body: body)
    }

    // MARK: knowledge packs — buy/download expertise for the profile

    func packs(industry: String?) async throws -> [Pack] {
        var query: [String: String] = [:]
        if let industry, !industry.isEmpty { query["industry"] = industry }
        return try await request("/packs", query: query.isEmpty ? nil : query)
    }

    func packRegistries() async throws -> [PackRegistry] {
        try await request("/packs/registries")
    }

    func syncRegistry(key: String) async throws {
        struct Ok: Decodable { let created: Int }
        let _: Ok = try await request("/packs/registries/\(key)/sync",
                                      method: "POST")
    }

    func installedPacks(pid: String, token: String) async throws -> [InstalledPack] {
        try await request("/profiles/\(pid)/packs", token: token)
    }

    func installPack(packId: String, pid: String, token: String,
                     acceptPrice: Bool,
                     robotId: String? = nil) async throws -> PackInstalled {
        var body: [String: Any] = ["profile_id": pid,
                                   "accept_price": acceptPrice]
        if let robotId { body["robot_id"] = robotId }
        return try await request("/packs/\(packId)/install", method: "POST",
                                 body: body, token: token)
    }

    func uninstallPack(packId: String, pid: String, token: String) async throws {
        struct Ok: Decodable { let removed_items: Int }
        let _: Ok = try await request("/profiles/\(pid)/packs/\(packId)",
                                      method: "DELETE", token: token)
    }

    func uninstallRobotPack(packId: String, robotId: String,
                            token: String) async throws {
        struct Ok: Decodable { let removed_tasks: Int }
        let _: Ok = try await request("/robots/\(robotId)/packs/\(packId)",
                                      method: "DELETE", token: token)
    }

    // MARK: gaming — a profile plays alongside real players

    func gameSessions(pid: String, token: String) async throws -> [GameSession] {
        try await request("/profiles/\(pid)/gaming/sessions", token: token)
    }

    func startGameSession(pid: String, token: String, platform: String,
                          game: String, role: String) async throws -> GameSession {
        try await request("/profiles/\(pid)/gaming/sessions", method: "POST",
                          body: ["platform": platform, "game": game,
                                 "role": role], token: token)
    }

    func gameCallout(sid: String, token: String, situation: String,
                     minorPresent: Bool) async throws -> GameCalloutResult {
        try await request("/gaming/sessions/\(sid)/callout", method: "POST",
                          body: ["situation": situation,
                                 "minor_present": minorPresent], token: token)
    }

    func endGameSession(sid: String, token: String) async throws {
        struct Ok: Decodable { let status: String }
        let _: Ok = try await request("/gaming/sessions/\(sid)/end",
                                      method: "POST", token: token)
    }

    func listings(tag: String?) async throws -> [Listing] {
        var query: [String: String] = [:]
        if let tag, !tag.isEmpty { query["tag"] = tag }
        return try await request("/marketplace/listings",
                                 query: query.isEmpty ? nil : query)
    }

    func removeListing(lid: String) async throws {
        var req = URLRequest(url: base.appendingPathComponent("/marketplace/listings/\(lid)"))
        req.httpMethod = "DELETE"
        let (_, resp) = try await URLSession.shared.data(for: req)
        guard let http = resp as? HTTPURLResponse,
              (200..<300).contains(http.statusCode) else {
            throw ApiError.http("remove failed")
        }
    }

    func setLicense(id: String, token: String, kind: String, price: Double,
                    terms: String?) async throws -> LicenseOffer {
        var body: [String: Any] = ["kind": kind, "price": price]
        if let terms, !terms.isEmpty { body["terms"] = terms }
        return try await request("/profiles/\(id)/license", method: "PUT",
                                 body: body, token: token)
    }

    func license(id: String) async throws -> LicenseOffer {
        try await request("/profiles/\(id)/license")
    }

    func unlistLicense(id: String, token: String) async throws {
        var req = URLRequest(url: base.appendingPathComponent("/profiles/\(id)/license"))
        req.httpMethod = "DELETE"
        req.setValue("Bearer \(token)", forHTTPHeaderField: "authorization")
        let (_, resp) = try await URLSession.shared.data(for: req)
        guard let http = resp as? HTTPURLResponse,
              (200..<300).contains(http.statusCode) else {
            throw ApiError.http("unlist failed")
        }
    }

    func licenseGrants(id: String, token: String) async throws -> [LicenseGrant] {
        try await request("/profiles/\(id)/licenses", token: token)
    }

    func revokeLicense(gid: String, token: String) async throws {
        struct Ok: Decodable {}
        let _: Ok = try await request("/licenses/\(gid)", method: "DELETE",
                                      token: token)
    }

    // MARK: Knowledge excursions (study safely; private data stays home)

    func excursions(id: String, token: String) async throws -> [Excursion] {
        try await request("/profiles/\(id)/excursions", token: token)
    }

    func startExcursion(id: String, token: String, topic: String,
                        question: String) async throws -> Excursion {
        try await request("/profiles/\(id)/excursions", method: "POST",
                          body: ["topic": topic, "question": question],
                          token: token)
    }

    func learn(cid: String, token: String) async throws {
        struct Ok: Decodable {}
        let _: Ok = try await request("/excursions/\(cid)/learn",
                                      method: "POST", token: token)
    }

    // MARK: Live desks

    func desk(_ id: String, token: String? = nil) async throws -> DeskCard {
        try await request("/desks/\(id)", token: token)
    }

    /// Ring the bell at an unattended desk. No token: the visitor standing in
    /// front of an empty chair is exactly the person who has no account.
    func ringBell(deskId: String, callerId: String? = nil,
                  note: String? = nil,
                  token: String? = nil) async throws -> RingReceipt {
        var body: [String: Any] = [:]
        if let callerId { body["caller_id"] = callerId }
        if let note { body["note"] = note }
        return try await request("/desks/\(deskId)/bell", method: "POST",
                                 body: body, token: token)
    }

    /// Join the live stream — the room whoever is watching shares.
    func joinStream(deskId: String, token: String? = nil)
        async throws -> StreamJoin {
        try await request("/desks/\(deskId)/join", method: "POST",
                          token: token)
    }


    // MARK: Connections across the counter — the desk's actual service.
    // The desk offers; only the caller's accept mints the link token, and it
    // is returned to the caller alone. Either side ends it.

    func openDeskSession(deskId: String, callerId: String,
                         token: String) async throws -> DeskSession {
        try await request("/desks/\(deskId)/sessions", method: "POST",
                          body: ["caller_id": callerId], token: token)
    }

    func deskSessions(deskId: String,
                      token: String) async throws -> [DeskSession] {
        try await request("/desks/\(deskId)/sessions", token: token)
    }

    func deskSession(sessionId: String,
                     token: String) async throws -> DeskSession {
        try await request("/desk-sessions/\(sessionId)", token: token)
    }

    func offerDeskConnection(sessionId: String, kind: String, target: String,
                             scope: String?, token: String)
        async throws -> DeskConnection {
        var body: [String: Any] = ["kind": kind, "target": target]
        if let scope { body["scope"] = scope }
        return try await request("/desk-sessions/\(sessionId)/connections",
                                 method: "POST", body: body, token: token)
    }

    func answerDeskConnection(sessionId: String, connectionId: String,
                              accept: Bool, token: String)
        async throws -> DeskConnection {
        try await request(
            "/desk-sessions/\(sessionId)/connections/\(connectionId)/answer",
            method: "POST", body: ["accept": accept], token: token)
    }

    func endDeskConnection(sessionId: String, connectionId: String,
                           token: String) async throws -> DeskConnection {
        try await request(
            "/desk-sessions/\(sessionId)/connections/\(connectionId)/end",
            method: "POST", token: token)
    }

    func closeDeskSession(sessionId: String,
                          token: String) async throws -> DeskSession {
        try await request("/desk-sessions/\(sessionId)/close",
                          method: "POST", token: token)
    }

    func myDeskSessions(interactorId: String,
                        token: String) async throws -> [DeskSession] {
        try await request("/interactors/\(interactorId)/desk-sessions",
                          token: token)
    }

    // MARK: Signatures (docs/signatures.md)

    func signaturePolicy() async throws -> SignaturePolicy {
        try await request("/signatures/policy")
    }

    func enrollOptions(displayName: String,
                       token: String) async throws -> EnrollOptions {
        try await request("/signatures/enroll/options", method: "POST",
                          body: ["display_name": displayName], token: token)
    }

    func enrollCredential(credentialId: String, attestationObject: String,
                          clientDataJSON: String, challenge: String,
                          proofingLevel: String, displayName: String,
                          attestor: String?,
                          token: String) async throws -> SigningCredential {
        var body: [String: Any] = [
            "credential_id": credentialId,
            "attestation_object": attestationObject,
            "client_data_json": clientDataJSON,
            "challenge": challenge,
            "proofing_level": proofingLevel,
            "display_name": displayName,
        ]
        if let attestor { body["proofing_attestor"] = attestor }
        return try await request("/signatures/enroll", method: "POST",
                                 body: body, token: token)
    }

    func signingCredentials(token: String) async throws -> [SigningCredential] {
        struct Wrapper: Decodable { let credentials: [SigningCredential] }
        let w: Wrapper = try await request("/signatures/credentials", token: token)
        return w.credentials
    }

    func revokeCredential(id: String, token: String) async throws {
        struct Ok: Decodable {}
        let _: Ok = try await request("/signatures/credentials/\(id)",
                                      method: "DELETE", token: token)
    }

    func requestSignature(document: String, meaning: String, displayText: String,
                          tier: String, bindingKind: String? = nil,
                          bindingRef: String? = nil,
                          token: String) async throws -> SignatureEnvelope {
        var body: [String: Any] = [
            "document": document, "meaning": meaning,
            "display_text": displayText, "tier": tier,
        ]
        if let bindingKind { body["binding_kind"] = bindingKind }
        if let bindingRef { body["binding_ref"] = bindingRef }
        return try await request("/signatures/request", method: "POST",
                                 body: body, token: token)
    }

    func submitSignature(envelopeId: String, assertion: Signing.Assertion,
                         platform: String,
                         token: String) async throws -> SignatureReceipt {
        try await request("/signatures/sign", method: "POST", body: [
            "envelope_id": envelopeId,
            "credential_id": assertion.credentialId,
            "signature": assertion.signature,
            "authenticator_data": assertion.authenticatorData,
            "client_data_json": assertion.clientDataJSON,
            // Optic ID and Face ID are both platform authenticators, so the
            // ceremony happens on this device rather than via a second one.
            "transport": "internal",
            "platform": platform,
        ], token: token)
    }

    // MARK: Voiceprint — FIG. 800, in the order the drawing gates it

    func voiceprint(id: String, token: String) async throws -> VoiceprintStatus {
        try await request("/profiles/\(id)/voiceprint", token: token)
    }

    /// Step 802. `ownVoice` is an attestation, not a checkbox: the backend
    /// refuses the grant without it, so there is no path here to anyone else.
    func grantVoiceConsent(id: String, token: String, sources: [String],
                           note: String? = nil) async throws -> VoiceprintStatus {
        var body: [String: Any] = ["own_voice": true, "sources": sources]
        if let note { body["note"] = note }
        return try await request("/profiles/\(id)/voiceprint/consent",
                                 method: "PUT", body: body, token: token)
    }

    /// Steps 806–808. Only the measurements travel — seconds, turns, where it
    /// came from. The audio itself is never posted or stored.
    func addVoiceSample(id: String, token: String, source: String,
                        seconds: Double, turns: Int,
                        reference: String? = nil) async throws -> VoiceEnrollment {
        var body: [String: Any] = ["source": source, "seconds": seconds,
                                   "turns": turns]
        // Names the recording without carrying it: the audio stays on device.
        if let reference { body["reference"] = reference }
        return try await request("/profiles/\(id)/voiceprint/samples",
                                 method: "POST", body: body, token: token)
    }

    func buildVoiceprint(id: String, token: String) async throws -> VoiceprintStatus {
        try await request("/profiles/\(id)/voiceprint", method: "POST", token: token)
    }

    func speakInVoice(id: String, token: String,
                      text: String) async throws -> VoiceSpoken {
        try await request("/profiles/\(id)/voiceprint/speak", method: "POST",
                          body: ["text": text], token: token)
    }

    /// Withdrawal. The samples are deleted and the print retires; the record
    /// of the withdrawal itself stays, which is why this reports counts.
    func revokeVoiceprint(id: String, token: String) async throws -> VoiceRevocation {
        try await request("/profiles/\(id)/voiceprint", method: "DELETE",
                          token: token)
    }
}

struct ObjectionTimelineEvent: Decodable {
    let id: String
    let event: String
    let actor: String
    let sealed: Bool
    let at: String
}

struct ObjectionTimeline: Decodable {
    let objection_id: String
    let profile_id: String
    let status: String
    let reattested: Bool
    let vault_backed: Bool
    let note: String
    let events: [ObjectionTimelineEvent]
}

// MARK: - Shops — storefronts, not desks (qrme/shops.py)

/// A storefront card. `offerings` is a count on the list and the rows on
/// the detail — two types rather than one optional, so neither lies.
struct ShopCardRow: Decodable, Identifiable {
    let id: String
    let profile_id: String
    let name: String
    let blurb: String?
    let tag: String?
    let seller: String
    let offerings: Int
}

struct ShopOfferingRow: Decodable, Identifiable {
    let id: String
    let shop_id: String
    let kind: String
    let title: String
    let blurb: String?
    let price: Double
    let currency: String
    let availability: String
    let retired: Int
}

struct ShopDetailRow: Decodable {
    let id: String
    let profile_id: String
    let name: String
    let blurb: String?
    let tag: String?
    let seller: String?
    let offerings: [ShopOfferingRow]
}

struct ShopOrderRow: Decodable, Identifiable {
    let id: String
    let shop_id: String
    let offering_id: String
    let buyer_id: String
    let quantity: Int
    let amount: Double
    let currency: String
    let status: String
    let title: String
    let kind: String
}

extension ApiClient {
    func listShops(tag: String? = nil) async throws -> [ShopCardRow] {
        let q = tag.flatMap {
            $0.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed)
        }
        return try await request("/shops" + (q.map { "?tag=\($0)" } ?? ""))
    }

    func shopCard(shopId: String) async throws -> ShopDetailRow {
        try await request("/shops/\(shopId)")
    }

    func openShop(profileId: String, name: String, blurb: String?,
                  tag: String?, token: String) async throws -> ShopDetailRow {
        var body: [String: Any] = ["profile_id": profileId, "name": name]
        if let blurb, !blurb.isEmpty { body["blurb"] = blurb }
        if let tag, !tag.isEmpty { body["tag"] = tag }
        return try await request("/shops", method: "POST", body: body,
                                 token: token)
    }

    func addShopOffering(shopId: String, kind: String, title: String,
                         price: Double,
                         token: String) async throws -> ShopOfferingRow {
        try await request("/shops/\(shopId)/offerings", method: "POST",
                          body: ["kind": kind, "title": title, "price": price],
                          token: token)
    }

    func retireShopOffering(shopId: String, offeringId: String,
                            token: String) async throws -> ShopOfferingRow {
        try await request("/shops/\(shopId)/offerings/\(offeringId)",
                          method: "DELETE", token: token)
    }

    /// The buyer's press — signed with the interactor's own token, the same
    /// identity a conversation runs on.
    func placeShopOrder(shopId: String, offeringId: String, buyerId: String,
                        quantity: Int,
                        token: String) async throws -> ShopOrderRow {
        try await request("/shops/\(shopId)/orders", method: "POST",
                          body: ["offering_id": offeringId,
                                 "buyer_id": buyerId, "quantity": quantity],
                          token: token)
    }

    func shopOrderBook(shopId: String,
                       token: String) async throws -> [ShopOrderRow] {
        try await request("/shops/\(shopId)/orders", token: token)
    }

    func myShopOrders(buyerId: String,
                      token: String) async throws -> [ShopOrderRow] {
        try await request("/shops/orders/of/\(buyerId)", token: token)
    }

    func advanceShopOrder(shopId: String, orderId: String, party: String,
                          to: String, token: String) async throws -> ShopOrderRow {
        try await request("/shops/\(shopId)/orders/\(orderId)/advance",
                          method: "POST", body: ["party": party, "to": to],
                          token: token)
    }
}

// MARK: - Your corner: switches, messages, the homepage (qrme/social.py)

struct DmThreadRow: Decodable, Identifiable {
    let other_id: String
    let other_name: String?
    let messages: Int
    let last_at: String
    var id: String { other_id }
}

struct DmMessageRow: Decodable, Identifiable {
    let id: String
    let sender_id: String
    let body: String
    let sent_at: String
}

struct HomepageDoc: Decodable {
    struct Theme: Decodable { let bg: String; let accent: String }
    struct Link: Decodable { let label: String; let url: String }
    struct Top: Decodable { let profile_id: String; let display_name: String }
    let profile_id: String
    let display_name: String?
    let headline: String
    let about: String
    let theme: Theme
    let links: [Link]
    let top_friends: [Top]
    let editable: Bool
}

extension ApiClient {
    func features(profileId: String,
                  token: String) async throws -> [String: Bool] {
        try await request("/profiles/\(profileId)/features", token: token)
    }

    func setFeature(profileId: String, feature: String, enabled: Bool,
                    token: String) async throws -> [String: Bool] {
        try await request("/profiles/\(profileId)/features", method: "PUT",
                          body: ["feature": feature, "enabled": enabled],
                          token: token)
    }

    func sendDm(profileId: String, to: String, body: String,
                token: String) async throws -> DmMessageRow {
        try await request("/profiles/\(profileId)/messages", method: "POST",
                          body: ["to": to, "body": body], token: token)
    }

    func dmThreads(profileId: String, token: String) async throws -> [DmThreadRow] {
        struct Box: Decodable { let threads: [DmThreadRow] }
        let box: Box = try await request("/profiles/\(profileId)/messages",
                                         token: token)
        return box.threads
    }

    func dmThread(profileId: String, withId: String,
                  token: String) async throws -> [DmMessageRow] {
        struct Box: Decodable { let messages: [DmMessageRow] }
        let q = withId.addingPercentEncoding(
            withAllowedCharacters: .urlQueryAllowed) ?? withId
        let box: Box = try await request(
            "/profiles/\(profileId)/messages?with_id=\(q)", token: token)
        return box.messages
    }

    func homepage(profileId: String,
                  token: String? = nil) async throws -> HomepageDoc {
        try await request("/profiles/\(profileId)/homepage", token: token)
    }

    func editHomepage(profileId: String, headline: String, about: String,
                      bg: String, accent: String,
                      token: String) async throws -> HomepageDoc {
        try await request("/profiles/\(profileId)/homepage", method: "PUT",
                          body: ["headline": headline, "about": about,
                                 "theme": ["bg": bg, "accent": accent]],
                          token: token)
    }
}

// MARK: - The people around a profile: friends, the wall, and comments

struct FriendRow: Decodable, Identifiable {
    let profile_id: String
    let display_name: String?
    let handle: String?
    let founder: Bool
    let pinned: Bool
    let mutual: Bool
    var id: String { profile_id }
}

struct SuggestedRow: Decodable, Identifiable {
    let profile_id: String
    let display_name: String?
    let because: String?
    var id: String { profile_id }
}

struct WallPostRow: Decodable, Identifiable {
    let id: String
    let profile_id: String
    let body: String
    let created_at: String?
    let likes: Int?
    let status: String?
}

struct CommentRow: Decodable, Identifiable {
    let id: String
    let author_id: String
    let body: String
    let status: String
    let flag_reason: String?
}

/// One deed done to this profile — the inbox names the deed, never the
/// words. The sentence for each `kind` is this shell's, from L10n.
struct InboxEvent: Decodable, Identifiable {
    let id: String
    let kind: String
    let actor_id: String
    let actor_name: String?
    let ref: String?
    let created_at: String
    let seen: Bool
}

struct InboxPage: Decodable {
    let events: [InboxEvent]
    let unseen: Int
}

extension ApiClient {
    func inbox(profileId: String, token: String) async throws -> InboxPage {
        try await request("/profiles/\(profileId)/inbox", token: token)
    }

    func markInboxSeen(profileId: String, token: String) async throws {
        struct Out: Decodable { let seen: Int }
        let _: Out = try await request("/profiles/\(profileId)/inbox/seen",
                                       method: "POST", token: token)
    }

    func friends(profileId: String) async throws -> [FriendRow] {
        struct Box: Decodable { let friends: [FriendRow] }
        let box: Box = try await request("/profiles/\(profileId)/friends")
        return box.friends
    }

    func suggestedFriends(profileId: String) async throws -> [SuggestedRow] {
        struct Box: Decodable { let suggested: [SuggestedRow] }
        let box: Box = try await request(
            "/profiles/\(profileId)/friends/suggested")
        return box.suggested
    }

    func addFriend(profileId: String, friendId: String,
                   token: String) async throws -> [String: Bool] {
        struct Added: Decodable { let added: Bool }
        let out: Added = try await request(
            "/profiles/\(profileId)/friends", method: "POST",
            body: ["friend_id": friendId], token: token)
        return ["added": out.added]
    }

    /// The pinned rows refuse with 409 — the list marks them `pinned` so a
    /// client can leave the control off rather than offer one that fails.
    func removeFriend(profileId: String, friendId: String,
                      token: String) async throws {
        struct Gone: Decodable { let removed: Bool? }
        let _: Gone = try await request(
            "/profiles/\(profileId)/friends/\(friendId)", method: "DELETE",
            token: token)
    }

    func wall(profileId: String) async throws -> [WallPostRow] {
        struct Box: Decodable { let posts: [WallPostRow] }
        let box: Box = try await request("/profiles/\(profileId)/wall")
        return box.posts
    }

    func postToWall(profileId: String, body: String,
                    token: String) async throws -> WallPostRow {
        try await request("/profiles/\(profileId)/wall", method: "POST",
                          body: ["body": body], token: token)
    }

    func comments(kind: String, targetId: String,
                  token: String) async throws -> [CommentRow] {
        struct Box: Decodable { let comments: [CommentRow] }
        let box: Box = try await request("/\(kind)/\(targetId)/comments",
                                         token: token)
        return box.comments
    }

    func addComment(kind: String, targetId: String, body: String,
                    token: String) async throws -> CommentRow {
        try await request("/\(kind)/\(targetId)/comments", method: "POST",
                          body: ["body": body], token: token)
    }

    func deleteComment(commentId: String, token: String) async throws {
        struct Gone: Decodable { let deleted: Bool? }
        let _: Gone = try await request("/comments/\(commentId)",
                                        method: "DELETE", token: token)
    }
}

// MARK: - Standing behind the counter: desks, the market, exchanges
//
// The caller's side of a desk shipped long ago — ring the bell, join the
// stream, open a session. What never reached a phone was the *other*
// side: opening a desk, staffing it, deciding who comes through, and
// putting its QR sticker on a wall. Same shape in the market (a card
// could go up; nothing could search, price, sell or buy) and in
// exchanges, which no shell had at all.

struct DeskCard: Decodable, Identifiable {
    let desk_id: String
    let display_name: String
    let trade: String?
    let location: String?
    let blurb: String?
    let presence: String
    let rated: Bool
    let desk_token: String?
    var id: String { desk_id }
}

struct DeskBrief: Decodable, Identifiable {
    let id: String
    let display_name: String
    let trade: String?
    let location: String?
    let presence: String
    let rated: Int?
}

struct DeskRing: Decodable, Identifiable {
    let id: String
    let caller_id: String?
    let note: String?
    let acked: Bool?
    let at: String?
}

struct DeskGuest: Decodable, Identifiable {
    let id: String
    let guest_id: String
    let display_name: String?
    let note: String?
    let status: String
}

struct DeskBeacon: Decodable, Identifiable {
    let id: String
    let label: String?
    let url: String?
}

struct DeskOverlay: Decodable {
    let comments: [String]?
    let likes: Int
    let shares: Int
    let gift_total: Double?
    let waiting: Int
}

struct LivePerson: Decodable {
    let desk_id: String
    let owner_id: String?
}

struct MarketCard: Decodable, Identifiable {
    let profile_id: String
    let display_name: String
    let purpose: String?
    let blurb: String?
    let tags: [String]?
    var id: String { profile_id }
}

struct MarketHit: Decodable, Identifiable {
    let id: String
    let kind: String?
    let title: String
    let blurb: String?
}

struct MarketSearch: Decodable {
    let query: String
    let scope: String?
    let results: [MarketHit]
}

struct MarketAssist: Decodable {
    let need: String
    let suggestions: [String]
    let note: String?
}

struct MarketOffer: Decodable {
    let listing_id: String?
    let amount: Double?
    let currency: String?
    let accept_price: Double?
    let status: String?
}

struct MarketSale: Decodable, Identifiable {
    let id: String
    let listing_id: String?
    let amount: Double?
    let currency: String?
    let status: String?
}

struct MarketSettings: Decodable {
    let interactor_id: String?
    let show_offers: Bool?
}

struct ExchangeVocabulary: Decodable {
    let industries: [String]
    let states: [String]
    let directions: [String]
    let max_items: Int
    let rules: [String]
}

struct ExchangeItem: Decodable, Identifiable {
    let id: String
    let direction: String
    let name: String
    let kind: String
    let accepted: Bool?
}

struct ExchangeDeal: Decodable, Identifiable {
    let id: String
    let host_id: String?
    let guest_id: String?
    let work: String?
    let industry: String?
    let state: String
    let items: [ExchangeItem]?
    let signed_by: [String]?
}

extension ApiClient {

    // -- the desk, from behind it ---------------------------------------

    func desks() async throws -> [DeskBrief] {
        try await request("/desks")
    }

    func openDesk(ownerId: String, displayName: String, trade: String,
                  attestor: String, basis: String, location: String?,
                  blurb: String?, token: String) async throws -> DeskCard {
        var body: [String: Any] = [
            "owner_id": ownerId, "display_name": displayName, "trade": trade,
            "attestor": attestor, "basis": basis]
        if let location, !location.isEmpty { body["location"] = location }
        if let blurb, !blurb.isEmpty { body["blurb"] = blurb }
        return try await request("/desks", method: "POST", body: body,
                                 token: token)
    }

    func setDeskPresence(deskId: String, presence: String,
                         token: String) async throws -> DeskCard {
        try await request("/desks/\(deskId)/presence", method: "PUT",
                          body: ["presence": presence], token: token)
    }

    func setDeskPortrait(deskId: String, asset: String?,
                         token: String) async throws -> DeskCard {
        try await request("/desks/\(deskId)/portrait", method: "PUT",
                          body: ["asset": asset as Any], token: token)
    }

    func setDeskCamera(deskId: String, enabled: Bool,
                       token: String) async throws -> DeskCard {
        try await request("/desks/\(deskId)/camera", method: "PUT",
                          body: ["enabled": enabled], token: token)
    }

    func deskRings(deskId: String, token: String) async throws -> [DeskRing] {
        struct Box: Decodable { let rings: [DeskRing] }
        let box: Box = try await request("/desks/\(deskId)/rings",
                                         token: token)
        return box.rings
    }

    func ackDeskRing(deskId: String, ringId: String,
                     token: String) async throws {
        struct Ok: Decodable { let acked: Bool? }
        let _: Ok = try await request(
            "/desks/\(deskId)/rings/\(ringId)/ack", method: "POST",
            token: token)
    }

    /// Knocking: the caller asks to come through to the desk.
    func askToJoinDesk(deskId: String, note: String?,
                       token: String) async throws -> DeskGuest {
        try await request("/desks/\(deskId)/guests", method: "POST",
                          body: ["note": note as Any], token: token)
    }

    func deskGuests(deskId: String, token: String) async throws -> [DeskGuest] {
        struct Box: Decodable { let guests: [DeskGuest] }
        let box: Box = try await request("/desks/\(deskId)/guests",
                                         token: token)
        return box.guests
    }

    func acceptDeskGuest(deskId: String, requestId: String,
                         token: String) async throws -> DeskGuest {
        try await request("/desks/\(deskId)/guests/\(requestId)/accept",
                          method: "POST", token: token)
    }

    func declineDeskGuest(deskId: String, requestId: String,
                          token: String) async throws -> DeskGuest {
        try await request("/desks/\(deskId)/guests/\(requestId)/decline",
                          method: "POST", token: token)
    }

    /// The caller's own way out — theirs to press, not the desk's.
    func leaveDesk(deskId: String, token: String) async throws {
        struct Ok: Decodable { let left: Bool? }
        let _: Ok = try await request("/desks/\(deskId)/guests/me",
                                      method: "DELETE", token: token)
    }

    func addDeskBeacon(deskId: String, label: String,
                       token: String) async throws -> DeskBeacon {
        try await request("/desks/\(deskId)/beacons", method: "POST",
                          body: ["label": label], token: token)
    }

    func deskBeacons(deskId: String,
                     token: String) async throws -> [DeskBeacon] {
        struct Box: Decodable { let beacons: [DeskBeacon] }
        let box: Box = try await request("/desks/\(deskId)/beacons",
                                         token: token)
        return box.beacons
    }

    func removeDeskBeacon(beaconId: String, token: String) async throws {
        struct Ok: Decodable { let removed: Bool? }
        let _: Ok = try await request("/desk-beacons/\(beaconId)",
                                      method: "DELETE", token: token)
    }

    /// The sticker itself. A URL rather than bytes: the sticker is drawn
    /// by an image view, and handing it a URL is one fetch, not two.
    func deskBeaconQrUrl(beaconId: String) -> URL {
        base.appendingPathComponent("/desk-beacons/\(beaconId)/qr.svg")
    }

    func deskOverlay(deskId: String) async throws -> DeskOverlay {
        try await request("/desks/\(deskId)/overlay")
    }

    func deskLivePerson(deskId: String) async throws -> LivePerson {
        try await request("/desks/\(deskId)/live-person")
    }

    /// What the desk looks like right now, as a still.
    func deskViewUrl(deskId: String) -> URL {
        base.appendingPathComponent("/desks/\(deskId)/view.webp")
    }

    // -- the market, from both sides ------------------------------------

    func marketplace() async throws -> [MarketCard] {
        try await request("/marketplace")
    }

    func marketSearch(_ query: String) async throws -> MarketSearch {
        try await request("/marketplace/search", query: ["q": query])
    }

    func marketLocalities() async throws -> [String] {
        try await request("/marketplace/localities")
    }

    func marketAssist(need: String) async throws -> MarketAssist {
        try await request("/marketplace/assist", method: "POST",
                          body: ["need": need])
    }

    /// The demo shelf: one press and the market has something on it.
    func seedMarketplace() async throws -> [String: Int] {
        struct Seeded: Decodable { let created: Int }
        let out: Seeded = try await request("/marketplace/seed",
                                            method: "POST")
        return ["created": out.created]
    }

    func listInMarketplace(profileId: String, blurb: String, locality: String,
                           tags: [String], token: String) async throws {
        struct Ok: Decodable { let listed: Bool }
        let _: Ok = try await request(
            "/profiles/\(profileId)/marketplace", method: "POST",
            body: ["blurb": blurb, "locality": locality, "tags": tags],
            token: token)
    }

    func unlistFromMarketplace(profileId: String,
                               token: String) async throws {
        struct Ok: Decodable { let listed: Bool? }
        let _: Ok = try await request("/profiles/\(profileId)/marketplace",
                                      method: "DELETE", token: token)
    }

    func removeListing(listingId: String, token: String) async throws {
        struct Ok: Decodable { let removed: Bool? }
        let _: Ok = try await request("/marketplace/listings/\(listingId)",
                                      method: "DELETE", token: token)
    }

    func listingOffer(listingId: String) async throws -> MarketOffer {
        try await request("/marketplace/listings/\(listingId)/offer")
    }

    func setListingOffer(listingId: String, amount: Double, currency: String,
                         acceptPrice: Double?,
                         token: String) async throws -> MarketOffer {
        var body: [String: Any] = ["amount": amount, "currency": currency]
        if let acceptPrice { body["accept_price"] = acceptPrice }
        return try await request(
            "/marketplace/listings/\(listingId)/offer", method: "PUT",
            body: body, token: token)
    }

    func clearListingOffer(listingId: String, token: String) async throws {
        struct Ok: Decodable { let cleared: Bool? }
        let _: Ok = try await request(
            "/marketplace/listings/\(listingId)/offer", method: "DELETE",
            token: token)
    }

    func placeListing(listingId: String, venue: String,
                      token: String) async throws -> MarketOffer {
        try await request("/marketplace/listings/\(listingId)/place",
                          method: "PUT", body: ["venue": venue],
                          token: token)
    }

    func unplaceListing(listingId: String, token: String) async throws {
        struct Ok: Decodable { let placed: Bool? }
        let _: Ok = try await request(
            "/marketplace/listings/\(listingId)/place", method: "DELETE",
            token: token)
    }

    func purchaseListing(listingId: String,
                         token: String) async throws -> MarketSale {
        try await request("/marketplace/listings/\(listingId)/purchase",
                          method: "POST", token: token)
    }

    func marketSales(token: String) async throws -> [MarketSale] {
        struct Box: Decodable { let sales: [MarketSale] }
        let box: Box = try await request("/marketplace/sales", token: token)
        return box.sales
    }

    func marketSettings(interactorId: String,
                        token: String) async throws -> MarketSettings {
        try await request("/marketplace/settings/\(interactorId)",
                          token: token)
    }

    func setMarketSettings(interactorId: String, showOffers: Bool,
                           token: String) async throws -> MarketSettings {
        try await request("/marketplace/settings/\(interactorId)",
                          method: "PUT", body: ["show_offers": showOffers],
                          token: token)
    }

    // -- exchanges: two parties, one manifest ---------------------------

    func exchangeVocabulary() async throws -> ExchangeVocabulary {
        try await request("/exchanges/vocabulary")
    }

    func proposeExchange(hostId: String, guestId: String, work: String,
                         industry: String, fee: Double,
                         token: String) async throws -> ExchangeDeal {
        try await request("/exchanges", method: "POST",
                          body: ["host_id": hostId, "guest_id": guestId,
                                 "work": work, "industry": industry,
                                 "fee": fee], token: token)
    }

    func exchange(exchangeId: String,
                  token: String) async throws -> ExchangeDeal {
        try await request("/exchanges/\(exchangeId)", token: token)
    }

    func addExchangeItem(exchangeId: String, direction: String, name: String,
                         kind: String,
                         token: String) async throws -> ExchangeItem {
        try await request("/exchanges/\(exchangeId)/items", method: "POST",
                          body: ["direction": direction, "name": name,
                                 "kind": kind], token: token)
    }

    func removeExchangeItem(exchangeId: String, itemId: String,
                            token: String) async throws {
        struct Ok: Decodable { let removed: Bool? }
        let _: Ok = try await request(
            "/exchanges/\(exchangeId)/items/\(itemId)", method: "DELETE",
            token: token)
    }

    /// Each item is accepted separately — nothing moves by itself.
    func acceptExchangeItem(exchangeId: String, itemId: String,
                            token: String) async throws -> ExchangeItem {
        try await request(
            "/exchanges/\(exchangeId)/items/\(itemId)/accept",
            method: "POST", token: token)
    }

    /// Both parties sign the same manifest; any change clears both.
    func signExchange(exchangeId: String, actorId: String,
                      token: String) async throws -> ExchangeDeal {
        try await request("/exchanges/\(exchangeId)/sign", method: "POST",
                          body: ["actor_id": actorId], token: token)
    }

    func reopenExchange(exchangeId: String, actorId: String,
                        token: String) async throws -> ExchangeDeal {
        try await request("/exchanges/\(exchangeId)/reopen", method: "POST",
                          body: ["actor_id": actorId], token: token)
    }

    func withdrawFromExchange(exchangeId: String, actorId: String,
                              token: String) async throws -> ExchangeDeal {
        try await request("/exchanges/\(exchangeId)/withdraw",
                          method: "POST", body: ["actor_id": actorId],
                          token: token)
    }

    /// Every deal this party is in — the list a phone needs before it can
    /// open one, which is why it belongs beside the rest of the block.
    func myExchanges(partyId: String,
                     token: String) async throws -> [ExchangeDeal] {
        struct Box: Decodable { let exchanges: [ExchangeDeal] }
        let box: Box = try await request("/parties/\(partyId)/exchanges",
                                         token: token)
        return box.exchanges
    }

    func exchangeChannel(exchangeId: String,
                         token: String) async throws -> [String: String] {
        struct Channel: Decodable { let room_id: String? }
        let out: Channel = try await request(
            "/exchanges/\(exchangeId)/channel", token: token)
        return ["room_id": out.room_id ?? ""]
    }
}
