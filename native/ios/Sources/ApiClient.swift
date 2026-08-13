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

struct SteeringLockOut: Decodable {
    let subject_id: String
    let reason: String?
    let locked_at: String
}

struct SteeringHubState: Decodable {
    let adult_mode: Bool
    let dials: [SteeringDial]
    let values: [String: Int]
    let age: SteeringAgeBlock
    let appearance: SteeringAppearance
    let lock: SteeringLockOut?
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
    let total_amount: Double
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
    let ready_when: VoiceThreshold
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

/// The count, and the three things it refuses to be. `ranksPeople`,
/// `hasAFavourite` and `namesAnybody` arrive as fields rather than prose so a
/// screen renders the refusals beside the number instead of composing a
/// reassuring sentence of its own.
struct ProfileAttention: Decodable {
    let profile_id: String
    let people_this_week: Int
    let people_ever: Int
    let you_are_one_of_them: Bool
    let says: String
    let ranks_people: Bool
    let has_a_favourite: Bool
    let names_anybody: Bool
    let note: String
}

struct SolitudeTurns: Decodable {
    let to_profiles: Int
    let to_people: Int
}

struct SolitudeOffer: Decodable {
    let state: String
    let why: String?
    let carries: [String]?
    let does_not_carry: [String]?
}

struct Solitude: Decodable {
    let interactor_id: String
    let window_days: Int
    let turns: SolitudeTurns
    let total_turns: Int
    /// Null until there is any conversation at all to take a ratio of.
    let share_synthetic: Double?
    let enough_to_say: Bool
    let note: String
    let offer: SolitudeOffer?
}

struct SolitudeReferral: Decodable {
    let ref: String
    let window_days: Int
    let turns: SolitudeTurns
    let issued_at: String
    let product: String
}

struct SolitudeDecision: Decodable {
    let interactor_id: String
    let state: String
    let referral: SolitudeReferral?
}

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
    let status: String                 // "matched" | "waiting" | "idle"
    let connection_id: String?
    let tier: String?                  // absent when idle
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
    let available_packs: Int
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
struct AccessReceipt: Decodable { let id: String; let status: String; let note: String? }
struct AccessReportRow: Decodable {
    let id: String; let lang: String; let doing: String; let wall: String
    let help: String?; let status: String; let created_at: String
}
struct AccessReportsState: Decodable { let reports: [AccessReportRow]; let total: Int }
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

/// Accepts any JSON value and keeps nothing — the manifest's carried block
/// is a heterogeneous object and the shell only needs its key names.
enum ManifestAny: Decodable {
    case ignored
    init(from decoder: Decoder) throws { self = .ignored }
}

/// What a derivation handed over and what stayed behind, written server-side
/// at derive time. `carried` arrives as a heterogeneous object; the shell
/// shows its keys — the names of what traveled — and the typed withheld rows.
struct ManifestWithheld: Decodable {
    let item: String
    let reason: String
}

struct LicenseManifest: Decodable {
    let carried: [String: ManifestAny]
    let withholdings: [ManifestWithheld]
}

struct LicenseGrant: Decodable {
    let id: String
    let buyer_id: String
    let kind: String
    let derived_profile_id: String?
    let revoked: Bool
    let manifest: LicenseManifest?
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
    case badBody
    var errorDescription: String? { if case let .http(m) = self { return m }; return nil }
}

/// Async client for the QRME backend. Defaults to the local dev server; the
/// iOS Simulator shares the host's network, so 127.0.0.1 resolves to your Mac.
actor ApiClient {
    static let shared = ApiClient()

    /// The person's own model key, pushed in by `AppState` and sent on every
    /// request as `x-llm-api-key`. Held here rather than reached for from the
    /// request path, which is actor-isolated and must not hop to the main
    /// actor to build a header.
    private var llmKey = ""

    func useLlmKey(_ key: String) { llmKey = key }

    /// The deployment invite key: a published deployment sets
    /// QRME_SIGNUP_KEY and refuses account creation without it. Sent as
    /// `x-signup-key` on every request; the backend reads it only on the
    /// routes it gates.
    private var signupKey = ""

    func useSignupKey(_ key: String) { signupKey = key }
    var base = URL(string: "http://127.0.0.1:8000")!

    func setBase(_ s: String) {
        if let u = URL(string: s.hasSuffix("/") ? String(s.dropLast()) : s) { base = u }
    }

    /// Every request this client sends that does not go through `request`,
    /// and the one place the reader's language is attached to it.
    ///
    /// Three calls in this file built their own `URLRequest` — the licence
    /// unlist, the media upload, the raw reads — and set only
    /// `authorization`. A token that has expired is not a principal, so the
    /// refusal those calls draw falls back to the header, and the header was
    /// not there. A funnel only funnels what goes into it.
    private func dispatch(_ req: URLRequest) async throws -> (Data, URLResponse) {
        var req = req
        req.setValue(L10n.deviceLanguage, forHTTPHeaderField: "accept-language")
        // The person's own model key, if this device holds one. Sent as a
        // header rather than stored server-side: the backend puts it in a
        // context var for the length of the call and never writes it down.
        if !llmKey.isEmpty {
            req.setValue(llmKey, forHTTPHeaderField: "x-llm-api-key")
        }
        if !signupKey.isEmpty {
            req.setValue(signupKey, forHTTPHeaderField: "x-signup-key")
        }
        return try await URLSession.shared.data(for: req)
    }


    struct ProblemRow: Decodable {
        let source: String
        let app_version: String
        let platform: String
        let op: String
        let status_code: Int
        let day: String
        let count: Int
    }
    struct ProblemRows: Decodable { let rows: [ProblemRow] }

    /// The failure aggregate this backend keeps. Reading is the operator's:
    /// the problems key as the token, or nothing when asking from the
    /// machine the backend runs on.
    func problemRows(key: String) async throws -> ProblemRows {
        try await request("/v1/problems", token: key)
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
        // The person's own model key, if this device holds one. Sent as a
        // header rather than stored server-side: the backend puts it in a
        // context var for the length of the call and never writes it down.
        if !llmKey.isEmpty {
            req.setValue(llmKey, forHTTPHeaderField: "x-llm-api-key")
        }
        if !signupKey.isEmpty {
            req.setValue(signupKey, forHTTPHeaderField: "x-signup-key")
        }
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

    /// A character card as a profile seed. What is refused is named in
    /// `withholdings`; harness instructions never ride in.
    func importCard(cardJSON: String, birthdate: String,
                    language: String? = nil) async throws -> ProfileCreated {
        guard let data = cardJSON.data(using: .utf8),
              let card = try? JSONSerialization.jsonObject(with: data)
                as? [String: Any] else {
            throw ApiError.badBody
        }
        var body: [String: Any] = [
            "owner_id": "owner-1",
            "card": card,
            "verification": ["birthdate": birthdate],
            "terms_consent": true,
        ]
        if let language, language != "en" { body["language"] = language }
        return try await request("/profiles/import/card", method: "POST",
                                 body: body)
    }

    struct RehearsalRoom: Decodable {
        let id: String
        let scenario: String
        let turns: Int
        let remembered: Bool
    }

    struct RehearsalTurn: Decodable {
        let id: String
        let reply: String
        let turns: Int
        let remembered: Bool
    }

    /// Rehearsal rooms: practice the hard conversation, nothing remembered.
    func openRehearsal(id: String, interactorId: String,
                       scenario: String) async throws -> RehearsalRoom {
        try await request("/profiles/\(id)/rehearsal", method: "POST",
                          body: ["interactor_id": interactorId,
                                 "scenario": scenario])
    }

    func rehearse(id: String, rehearsalId: String,
                  message: String) async throws -> RehearsalTurn {
        try await request("/profiles/\(id)/rehearsal/\(rehearsalId)/say",
                          method: "POST", body: ["message": message])
    }

    func closeRehearsal(id: String, rehearsalId: String) async throws {
        struct Out: Decodable { let id: String }
        let _: Out = try await request(
            "/profiles/\(id)/rehearsal/\(rehearsalId)", method: "DELETE")
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

    /// The accessibility door: tokenless on purpose — the person it exists
    /// for may be the person the signup shut out. The words stay on the
    /// deployment; nothing here reaches the problems collector.
    func sendAccessReport(doing: String, wall: String, help: String?,
                          lang: String) async throws -> AccessReceipt {
        var body: [String: Any] = ["doing": doing, "wall": wall, "lang": lang]
        if let help, !help.isEmpty { body["help"] = help }
        return try await request("/access/reports", method: "POST", body: body,
                                 token: nil)
    }

    /// Reviewer-token read — the deployment's steward, never a profile owner.
    func accessReports(reviewerToken: String) async throws -> AccessReportsState {
        try await request("/access/reports", token: reviewerToken)
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

    func socialScrape(cid: String, token: String) async throws {
        struct Ok: Decodable {}
        let _: Ok = try await request("/social/\(cid)/scrape", method: "POST",
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
    /// How many people a profile is talking to.
    ///
    /// Public on purpose, and no token here on purpose: the count is a fact
    /// about the profile, not a secret earned by intimacy.
    func profileAttention(profileId: String) async throws -> ProfileAttention {
        try await request("/profiles/\(profileId)/attention")
    }

    // MARK: Your side of it

    /// How much of *this person's* talking here went to a profile rather than
    /// to a person. The mirror of `profileAttention`, and unlike it this one
    /// is scoped to the account asking: there is no owner view of it and there
    /// must never be one.
    func solitude(interactorId: String) async throws -> Solitude {
        try await request("/interactors/\(interactorId)/solitude")
    }

    /// Take the JIM-mini door or close it. Closing is recorded so the offer is
    /// not made a second time.
    func solitudeHandoff(interactorId: String,
                         accept: Bool) async throws -> SolitudeDecision {
        try await request("/interactors/\(interactorId)/solitude/handoff",
                          method: "POST", body: ["accept": accept])
    }

    /// What would travel, readable before it does — counts and a window.
    func solitudeReferral(interactorId: String) async throws -> SolitudeReferral {
        try await request("/interactors/\(interactorId)/solitude/referral")
    }

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

    // What happened to my wait. A match is made by whichever side arrives
    // second — their join answers *them*, never the waiter — so the waiter
    // polls this. Never join again to ask: that re-queues the caller.
    func myConnection(token: String) async throws -> ConnJoin {
        try await request("/connections/mine", token: token)
    }

    func connectionMessages(cid: String, interactorId: String,
                            token: String) async throws -> [ConnMsg] {
        try await request("/connections/\(cid)/messages",
                          token: token, query: ["interactor_id": interactorId])
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
                                      token: token,
                                      query: ["interactor_id": interactorId])
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
        let (_, resp) = try await dispatch(req)
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
        let (_, resp) = try await dispatch(req)
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
        struct Out: Decodable { let marked_seen: Int }
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

/// What `POST /desks` hands back, and the only place the desk token appears.
/// Deliberately not `DeskCard`: that is the public card `GET /desks/{id}`
/// returns, with the attestation a visitor reads. Both carried one name, and
/// Swift called the lookup ambiguous while C# read the pair as partial
/// declarations of one positional record.
struct DeskOpened: Decodable, Identifiable {
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
    let locality: String?
    let region: String?
    let scope: String?
    let include_remote: Bool?
    let kinds_wanted: [String]?
    let tags: [String]?
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
                  blurb: String?, token: String) async throws -> DeskOpened {
        var body: [String: Any] = [
            "owner_id": ownerId, "display_name": displayName, "trade": trade,
            "attestor": attestor, "basis": basis]
        if let location, !location.isEmpty { body["location"] = location }
        if let blurb, !blurb.isEmpty { body["blurb"] = blurb }
        return try await request("/desks", method: "POST", body: body,
                                 token: token)
    }

    func setDeskPresence(deskId: String, presence: String,
                         token: String) async throws -> DeskOpened {
        try await request("/desks/\(deskId)/presence", method: "PUT",
                          body: ["presence": presence], token: token)
    }

    func setDeskPortrait(deskId: String, asset: String?,
                         token: String) async throws -> DeskOpened {
        try await request("/desks/\(deskId)/portrait", method: "PUT",
                          body: ["asset": asset as Any], token: token)
    }

    // The route points a desk at a camera by address and clears it with an
    // empty one. `enabled` was a switch with nothing to switch on.
    func setDeskCamera(deskId: String, url: String,
                       token: String) async throws -> DeskOpened {
        try await request("/desks/\(deskId)/camera", method: "PUT",
                          body: ["url": url], token: token)
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
        struct Ok: Decodable {}
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

    // Listing takes a blurb and tags; where it is offered is `placeListing`.
    func listInMarketplace(profileId: String, blurb: String,
                           tags: [String], token: String) async throws {
        struct Ok: Decodable { let listed: Bool }
        let _: Ok = try await request(
            "/profiles/\(profileId)/marketplace", method: "POST",
            body: ["blurb": blurb, "tags": tags],
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

    func setListingOffer(listingId: String, price: Double, currency: String,
                         stock: Int?,
                         token: String) async throws -> MarketOffer {
        var body: [String: Any] = ["price": price, "currency": currency]
        if let stock { body["stock"] = stock }
        return try await request(
            "/marketplace/listings/\(listingId)/offer", method: "PUT",
            body: body, token: token)
    }

    func clearListingOffer(listingId: String, token: String) async throws {
        struct Ok: Decodable {}
        let _: Ok = try await request(
            "/marketplace/listings/\(listingId)/offer", method: "DELETE",
            token: token)
    }

    // `locality` is what ListingPlace declares — somewhere a person typed.
    // `venue` is a key from qrme.rated.VENUES and belongs to another model.
    func placeListing(listingId: String, locality: String,
                      token: String) async throws -> MarketOffer {
        try await request("/marketplace/listings/\(listingId)/place",
                          method: "PUT", body: ["locality": locality],
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

    // MarketPrefs is where "here" is and how far out to look. `show_offers`
    // was a switch for nothing.
    func setMarketSettings(interactorId: String, locality: String,
                           includeRemote: Bool,
                           token: String) async throws -> MarketSettings {
        try await request("/marketplace/settings/\(interactorId)",
                          method: "PUT",
                          body: ["locality": locality,
                                 "include_remote": includeRemote],
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

// MARK: - The crowd, the couch and the loan
//
// Three blocks the doorless records said the phones could not reach: the
// audience verbs (like, share, subscribe, gift — the quiet half of being
// seen), the watch party (a room around a posted video), and skill grants
// (a skill lent into one place, used and never copied).

struct AudienceCounts: Decodable {
    let likes: Int?
    let comments: Int?
    let shares: Int?
    let subscribers: Int?
    let you_liked: Bool?
}

struct SubscriberRow: Decodable, Identifiable {
    let id: String?
    let actor_id: String?
    let tier: String?
    var identity: String { id ?? actor_id ?? "?" }
}

struct GiftRow: Decodable, Identifiable {
    let id: String?
    let giver_id: String?
    let amount: Double?
    let note: String?
    var identity: String { id ?? "\(giver_id ?? "?")-\(amount ?? 0)" }
}

struct PartyCard: Decodable {
    let id: String?
    let party_id: String?
    let post_id: String?
    let host_id: String?
    let title: String?
    let state: String?
    let position_s: Int?
    let playing: Bool?
    let members: [PartyMember]?
    /// Whether the host put it on the public surfaces. The id stays the
    /// private door either way.
    let `public`: Bool?
    var identity: String { id ?? party_id ?? "?" }
}

/// A public browse card: counts and a facade, never member names and never
/// a line of chat — those stay members-only.
struct PublicPartyCard: Decodable, Identifiable {
    let id: String
    let title: String?
    let people: Int?
    let profiles: Int?
    let joining: String?
}

struct PartyMember: Decodable, Identifiable {
    let member_id: String
    let kind: String?
    let role: String?
    let synthetic: Bool?
    var id: String { member_id }
}

struct PartyLine: Decodable, Identifiable {
    let id: String?
    let member_id: String?
    let body: String?
    let at_position_s: Int?
    var identity: String { id ?? "\(member_id ?? "?")-\(body ?? "")" }
}

struct GrantVocabulary: Decodable {
    struct Entry: Decodable, Identifiable {
        let key: String
        let means: String
        var id: String { key }
    }
    let surfaces: [Entry]
    let skill_kinds: [Entry]
    let states: [String]
    let terms: [String]
}

struct GrantCard: Decodable, Identifiable {
    let id: String?
    let grant_id: String?
    let lender_id: String?
    let borrower_id: String?
    let surface: String?
    let surface_id: String?
    let skill_kind: String?
    let title: String?
    let state: String?
    var identity: String { id ?? grant_id ?? "?" }
}

struct GrantUse: Decodable, Identifiable {
    let id: String?
    let what: String?
    let used_at: String?
    var identity: String { id ?? used_at ?? "?" }
}

extension ApiClient {
    // -- audience: like, share, subscribe, gift --

    func like(kind: String, targetId: String, token: String) async throws {
        struct Out: Decodable { let liked: Bool? }
        let _: Out = try await request("/\(kind)/\(targetId)/like",
                                       method: "POST", token: token)
    }

    func unlike(kind: String, targetId: String, token: String) async throws {
        struct Out: Decodable { let liked: Bool? }
        let _: Out = try await request("/\(kind)/\(targetId)/like",
                                       method: "DELETE", token: token)
    }

    func share(kind: String, targetId: String,
               token: String) async throws -> [String: String] {
        struct Out: Decodable { let url: String? }
        let out: Out = try await request("/\(kind)/\(targetId)/share",
                                         method: "POST",
                                         body: ["channel": "link"],
                                         token: token)
        return ["url": out.url ?? ""]
    }

    func audienceCounts(kind: String, targetId: String,
                        token: String) async throws -> AudienceCounts {
        try await request("/\(kind)/\(targetId)/audience", token: token)
    }

    func subscribe(kind: String, subjectId: String,
                   token: String) async throws {
        struct Out: Decodable { let tier: String? }
        let _: Out = try await request("/\(kind)/\(subjectId)/subscribe",
                                       method: "POST", body: ["tier": "follow"],
                                       token: token)
    }

    func unsubscribe(kind: String, subjectId: String,
                     token: String) async throws {
        struct Out: Decodable { let cancelled: Bool? }
        let _: Out = try await request("/\(kind)/\(subjectId)/subscribe",
                                       method: "DELETE", token: token)
    }

    func subscribers(kind: String, subjectId: String,
                     token: String) async throws -> [SubscriberRow] {
        struct Box: Decodable { let subscribers: [SubscriberRow] }
        let box: Box = try await request("/\(kind)/\(subjectId)/subscribers",
                                         token: token)
        return box.subscribers
    }

    func gift(kind: String, subjectId: String, amount: Double, note: String,
              token: String) async throws -> GiftRow {
        try await request("/\(kind)/\(subjectId)/gift", method: "POST",
                          body: ["amount": amount, "note": note],
                          token: token)
    }

    func gifts(kind: String, subjectId: String,
               token: String) async throws -> [GiftRow] {
        struct Box: Decodable { let gifts: [GiftRow] }
        let box: Box = try await request("/\(kind)/\(subjectId)/gifts",
                                         token: token)
        return box.gifts
    }

    // -- the watch party --

    func startParty(postId: String, hostId: String, title: String,
                    token: String) async throws -> PartyCard {
        try await request("/watch-parties", method: "POST",
                          body: ["post_id": postId, "host_id": hostId,
                                 "title": title],
                          token: token)
    }

    func party(partyId: String, token: String) async throws -> PartyCard {
        try await request("/watch-parties/\(partyId)", token: token)
    }

    func joinParty(partyId: String, memberId: String, kind: String,
                   token: String) async throws -> PartyCard {
        try await request("/watch-parties/\(partyId)/members",
                          method: "POST",
                          body: ["member_id": memberId, "kind": kind],
                          token: token)
    }

    func leaveParty(partyId: String, memberId: String,
                    token: String) async throws {
        struct Out: Decodable {}
        let _: Out = try await request(
            "/watch-parties/\(partyId)/members/\(memberId)",
            method: "DELETE", token: token)
    }

    func seekParty(partyId: String, hostId: String, positionS: Int,
                   playing: Bool, token: String) async throws -> PartyCard {
        try await request("/watch-parties/\(partyId)/seek", method: "POST",
                          body: ["host_id": hostId, "position_s": positionS,
                                 "playing": playing],
                          token: token)
    }

    func sayInParty(partyId: String, memberId: String, body: String,
                    token: String) async throws -> PartyLine {
        try await request("/watch-parties/\(partyId)/chat", method: "POST",
                          body: ["member_id": memberId, "body": body],
                          token: token)
    }

    func partyChat(partyId: String, token: String) async throws -> [PartyLine] {
        struct Box: Decodable { let lines: [PartyLine] }
        let box: Box = try await request("/watch-parties/\(partyId)/chat",
                                         token: token)
        return box.lines
    }

    func endParty(partyId: String, token: String) async throws -> PartyCard {
        try await request("/watch-parties/\(partyId)/end", method: "POST",
                          token: token)
    }

    /// The browse door: parties whose hosts chose to be found. No token —
    /// public means public. Counts and a facade; names stay members-only.
    func publicParties() async throws -> [PublicPartyCard] {
        struct Box: Decodable { let parties: [PublicPartyCard] }
        let box: Box = try await request("/watch-parties/public")
        return box.parties
    }

    /// Host only, both directions — the id stays the private door.
    func publishParty(partyId: String, token: String) async throws -> PartyCard {
        try await request("/watch-parties/\(partyId)/listing", method: "POST",
                          token: token)
    }

    func unpublishParty(partyId: String,
                        token: String) async throws -> PartyCard {
        try await request("/watch-parties/\(partyId)/listing",
                          method: "DELETE", token: token)
    }

    /// What a synthetic member is allowed to know — including, explicitly,
    /// that it has not seen the footage.
    func partyContext(partyId: String,
                      token: String) async throws -> [String: String] {
        struct Ctx: Decodable { let you_have_not_seen_it: String? }
        let out: Ctx = try await request("/watch-parties/\(partyId)/context",
                                         token: token)
        return ["you_have_not_seen_it": out.you_have_not_seen_it ?? ""]
    }

    // -- skill grants: lent, used, never copied --

    func grantVocabulary() async throws -> GrantVocabulary {
        try await request("/skill-grants/vocabulary")
    }

    func offerGrant(lenderId: String, borrowerId: String, surface: String,
                    surfaceId: String, skillKind: String, skillRef: String,
                    title: String, token: String) async throws -> GrantCard {
        try await request("/skill-grants", method: "POST",
                          body: ["lender_id": lenderId,
                                 "borrower_id": borrowerId,
                                 "surface": surface, "surface_id": surfaceId,
                                 "skill_kind": skillKind,
                                 "skill_ref": skillRef, "title": title],
                          token: token)
    }

    func grant(grantId: String, token: String) async throws -> GrantCard {
        try await request("/skill-grants/\(grantId)", token: token)
    }

    func acceptGrant(grantId: String, actorId: String,
                     token: String) async throws -> GrantCard {
        try await request("/skill-grants/\(grantId)/accept", method: "POST",
                          body: ["actor_id": actorId], token: token)
    }

    func declineGrant(grantId: String, actorId: String,
                      token: String) async throws -> GrantCard {
        try await request("/skill-grants/\(grantId)/decline", method: "POST",
                          body: ["actor_id": actorId], token: token)
    }

    func closeGrant(grantId: String, actorId: String,
                    token: String) async throws -> GrantCard {
        try await request("/skill-grants/\(grantId)/close", method: "POST",
                          body: ["actor_id": actorId], token: token)
    }

    func useGrant(grantId: String, borrowerId: String, what: String,
                  token: String) async throws -> GrantUse {
        try await request("/skill-grants/\(grantId)/use", method: "POST",
                          body: ["borrower_id": borrowerId, "what": what],
                          token: token)
    }

    func grantUses(grantId: String, token: String) async throws -> [GrantUse] {
        struct Box: Decodable { let uses: [GrantUse] }
        let box: Box = try await request("/skill-grants/\(grantId)/uses",
                                         token: token)
        return box.uses
    }

    func grantsInSurface(surface: String, surfaceId: String,
                         token: String) async throws -> [GrantCard] {
        struct Box: Decodable { let grants: [GrantCard] }
        let box: Box = try await request(
            "/surfaces/\(surface)/\(surfaceId)/skill-grants", token: token)
        return box.grants
    }

    func myGrants(personId: String,
                  token: String) async throws -> [GrantCard] {
        struct Box: Decodable {
            let lending: [GrantCard]?
            let borrowing: [GrantCard]?
        }
        let box: Box = try await request("/people/\(personId)/skill-grants",
                                         token: token)
        return (box.lending ?? []) + (box.borrowing ?? [])
    }
}

// MARK: - The place, the camera, the organization and the tour
//
// Four more blocks off the doorless records: what is live in the place you
// are standing in (a lent microphone, a worn overlay, whose corner this
// is), the camera with its published refusals, the owner's organization,
// and the guided tour.

struct WhoseCard: Decodable {
    let surface: String?
    let surface_id: String?
    let display_name: String?
    let anonymous: Bool?
}

struct MicDisclosure: Decodable {
    struct Lent: Decodable, Identifiable {
        let interactor_id: String?
        let device: String?
        var id: String { interactor_id ?? "?" }
    }
    // The route calls it `microphones_lent`. Reading `lent` got nil, and a
    // disclosure that renders as an empty list is worse than no disclosure.
    let microphones_lent: [Lent]?
    let note: String?
}

struct WornDisclosure: Decodable {
    struct Worn: Decodable, Identifiable {
        let interactor_id: String?
        let kind: String?
        let title: String?
        var id: String { interactor_id ?? "?" }
    }
    let overlays: [Worn]?
}

struct CameraVocabulary: Decodable {
    let never: [String: String]?
    let subjects: [String: String]?
}

struct CameraSession: Decodable {
    let id: String?
    let subject: String?
    let state: String?
    let recording: Bool?
    let minutes: Int?
    let opened_at: String?
    var identity: String { id ?? "?" }
}

struct OrgCard: Decodable {
    let id: String?
    let name: String?
    let departments: [OrgDepartment]?
    var identity: String { id ?? name ?? "?" }
}

struct OrgDepartment: Decodable, Identifiable {
    let name: String?
    let role: String?
    var id: String { name ?? "?" }
}

/// AI for lease: the receipt for seating somebody else's licensed
/// specialist as a department.
struct LeaseOut: Decodable {
    let lease_id: String
    let department_id: String
}

struct Coordination: Decodable, Identifiable {
    let id: String?
    let goal: String?
    let status: String?
    var identity: String { id ?? goal ?? "?" }
}

struct TutorialOutline: Decodable {
    /// A chapter is a name and the lessons under it. `tutorial.outline`
    /// sends `{"chapter": …, "steps": [...]}`; reading `key` and `title`
    /// here made every row of the guided tour render as `?`.
    struct Chapter: Decodable, Identifiable {
        let chapter: String?
        let steps: [TutorialStep]?
        var id: String { chapter ?? "?" }
    }
    let guide: String?
    let chapters: [Chapter]?
}

struct TutorialStep: Decodable {
    let key: String?
    let chapter: String?
    let title: String?
    let try_it: String?
    // The lesson itself. `tutorial.say` calls it `what`; reading `body` got
    // nil and the screen fell back to repeating the title.
    let what: String?
}

/// Where a learner is, from `/tutorial/start`, `/progress/{id}` and `/done`.
/// All three answer with `tutorial.where`, which wraps the step — decoding
/// them as a bare `TutorialStep` left every one of those buttons blank.
struct TutorialWhere: Decodable {
    let learner_id: String?
    let guide: String?
    let step: TutorialStep?
    let done: Int?
    let total: Int?
    let finished: Bool?
    let note: String?
}

extension ApiClient {
    // -- the place: whose it is, the microphone, the overlay --

    func whose(surface: String, surfaceId: String) async throws -> WhoseCard {
        try await request("/places/\(surface)/\(surfaceId)/whose")
    }

    func lendMicrophone(surface: String, surfaceId: String,
                        interactorId: String,
                        token: String) async throws -> MicDisclosure {
        try await request("/places/\(surface)/\(surfaceId)/microphone",
                          method: "POST",
                          body: ["interactor_id": interactorId],
                          token: token)
    }

    func takeBackMicrophone(surface: String, surfaceId: String,
                            interactorId: String,
                            token: String) async throws {
        struct Out: Decodable {}
        let _: Out = try await request(
            "/places/\(surface)/\(surfaceId)/microphone", method: "DELETE",
            body: ["interactor_id": interactorId], token: token)
    }

    func microphoneDisclosure(surface: String, surfaceId: String,
                              token: String) async throws -> MicDisclosure {
        try await request("/places/\(surface)/\(surfaceId)/microphone",
                          token: token)
    }

    func wearOverlay(surface: String, surfaceId: String, interactorId: String,
                     kind: String, title: String,
                     token: String) async throws -> WornDisclosure.Worn {
        try await request("/places/\(surface)/\(surfaceId)/overlay",
                          method: "POST",
                          body: ["interactor_id": interactorId, "kind": kind,
                                 "title": title],
                          token: token)
    }

    func takeOffOverlay(surface: String, surfaceId: String,
                        interactorId: String, token: String) async throws {
        struct Out: Decodable {}
        let _: Out = try await request(
            "/places/\(surface)/\(surfaceId)/overlay", method: "DELETE",
            body: ["interactor_id": interactorId], token: token)
    }

    func wornOverlays(surface: String, surfaceId: String,
                      token: String) async throws -> WornDisclosure {
        try await request("/places/\(surface)/\(surfaceId)/overlay",
                          token: token)
    }

    // -- the camera, refusals first --

    func cameraVocabulary() async throws -> CameraVocabulary {
        try await request("/camera/vocabulary")
    }

    func bystanderGuidance(subject: String) async throws -> [String: String] {
        struct Out: Decodable { let guidance: String? }
        let out: Out = try await request("/camera/bystanders/\(subject)")
        return ["guidance": out.guidance ?? ""]
    }

    func openCamera(holderId: String, surface: String, surfaceId: String,
                    subject: String, viewerKind: String, viewerId: String,
                    minutes: Int,
                    token: String) async throws -> CameraSession {
        try await request("/camera/sessions", method: "POST",
                          body: ["holder_id": holderId, "surface": surface,
                                 "surface_id": surfaceId, "subject": subject,
                                 "viewer_kind": viewerKind,
                                 "viewer_id": viewerId, "minutes": minutes],
                          token: token)
    }

    func cameraSession(sessionId: String,
                       token: String) async throws -> CameraSession {
        try await request("/camera/sessions/\(sessionId)", token: token)
    }

    func closeCamera(sessionId: String, actorId: String,
                     token: String) async throws -> CameraSession {
        try await request("/camera/sessions/\(sessionId)/close",
                          method: "POST", body: ["actor_id": actorId],
                          token: token)
    }

    func myCameras(holderId: String,
                   token: String) async throws -> [CameraSession] {
        try await request("/camera/live/\(holderId)", token: token)
    }

    func cameraDisclosure(surface: String, surfaceId: String,
                          token: String) async throws -> [String: Bool] {
        struct Out: Decodable { let live: Bool?; let recording: Bool? }
        let out: Out = try await request(
            "/camera/disclosure/\(surface)/\(surfaceId)", token: token)
        return ["live": out.live ?? false,
                "recording": out.recording ?? false]
    }

    // -- the organization --

    func organizations(token: String) async throws -> [OrgCard] {
        try await request("/organizations", token: token)
    }

    func createOrganization(name: String,
                            token: String) async throws -> OrgCard {
        try await request("/organizations", method: "POST",
                          body: ["name": name], token: token)
    }

    func seedDemoOrganization(token: String) async throws -> OrgCard {
        try await request("/organizations/demo", method: "POST", token: token)
    }

    func organization(orgId: String, token: String) async throws -> OrgCard {
        try await request("/organizations/\(orgId)", token: token)
    }

    func addDepartment(orgId: String, name: String, role: String,
                       profileId: String,
                       token: String) async throws -> OrgDepartment {
        try await request("/organizations/\(orgId)/departments",
                          method: "POST",
                          body: ["name": name, "role": role,
                                 "profile_id": profileId],
                          token: token)
    }

    /// AI for lease: seat somebody else's licensed specialist as a
    /// department. The fee accrues to the specialist's owner, who can
    /// revoke the lease at any time.
    func leaseSpecialist(orgId: String, profileId: String, name: String,
                         role: String, token: String) async throws -> LeaseOut {
        try await request("/organizations/\(orgId)/lease", method: "POST",
                          body: ["profile_id": profileId, "name": name,
                                 "role": role],
                          token: token)
    }

    func coordinate(orgId: String, goal: String, fromDepartment: String,
                    token: String) async throws -> Coordination {
        try await request("/organizations/\(orgId)/coordinate",
                          method: "POST",
                          body: ["goal": goal,
                                 "from_department": fromDepartment],
                          token: token)
    }

    func coordinations(orgId: String,
                       token: String) async throws -> [Coordination] {
        try await request("/organizations/\(orgId)/coordinations",
                          token: token)
    }

    // -- the guided tour --

    func tutorialOutline() async throws -> TutorialOutline {
        try await request("/tutorial")
    }

    func tutorialStep(key: String) async throws -> TutorialStep {
        try await request("/tutorial/steps/\(key)")
    }

    func tutorialForScreen(number: Int) async throws -> TutorialStep {
        try await request("/tutorial/for-screen/\(number)")
    }

    func startTutorial(learnerId: String) async throws -> TutorialWhere {
        try await request("/tutorial/start", method: "POST",
                          body: ["learner_id": learnerId, "lesson": ""])
    }

    func tutorialProgress(learnerId: String) async throws -> TutorialWhere {
        try await request("/tutorial/progress/\(learnerId)")
    }

    func markTutorialDone(learnerId: String,
                          lesson: String) async throws -> TutorialWhere {
        try await request("/tutorial/done", method: "POST",
                          body: ["learner_id": learnerId, "lesson": lesson])
    }
}

// MARK: - The body, the referral, the objection, the lobby and the dock
//
// Five more blocks off the doorless records: the robot body's audit
// trail and dials, the medical referral's sign-then-release flow, the
// objection a person can read and end, the game lobby's honest roster,
// and the helper dock's own settings.

struct RobotCommandRow: Decodable {
    let id: String?
    let command: String?
    let created_at: String?
    var identity: String { id ?? created_at ?? "?" }
}

struct RobotSkillRow: Decodable, Identifiable {
    let task: String?
    let title: String?
    let pack_title: String?
    var id: String { task ?? title ?? "?" }
}

struct RobotSteering: Decodable {
    let values: [String: Double]?
    let behavior_profile: String?
}

struct ClinicianRow: Decodable, Identifiable {
    let id: String?
    let name: String?
    let expertise: String?
    var identity: String { id ?? name ?? "?" }
}

struct ReferralPackage: Decodable {
    let id: String?
    let referral_id: String?
    let status: String?
    var identity: String { id ?? referral_id ?? "?" }
}

struct ObjectionCard: Decodable {
    let id: String?
    let status: String?
    let reattested: Bool?
}

struct ObjectionAudit: Decodable {
    struct Event: Decodable {
        let id: String?
        let event: String?
        let sealed: Bool?
        var identity: String { id ?? event ?? "?" }
    }
    let status: String?
    let events: [Event]?
}

struct LobbySeat: Decodable, Identifiable {
    let member_id: String?
    let member_kind: String?
    let role: String?
    let callsign: String?
    var id: String { member_id ?? callsign ?? "?" }
}

struct DockSettings: Decodable {
    let corner: String?
    let state: String?
    let face: String?
    let wanted: String?
}

extension ApiClient {
    // -- the robot body --

    func unbindRobot(robotId: String, token: String) async throws {
        struct Out: Decodable { let unbound: Bool? }
        let _: Out = try await request("/robots/\(robotId)", method: "DELETE",
                                       token: token)
    }

    /// Owner-only audit: everything this body has been told to do.
    func robotCommands(robotId: String,
                       token: String) async throws -> [RobotCommandRow] {
        try await request("/robots/\(robotId)/commands", token: token)
    }

    func robotSkills(robotId: String,
                     token: String) async throws -> [RobotSkillRow] {
        try await request("/robots/\(robotId)/skills", token: token)
    }

    /// A body's dials — intimacy never applies to a body.
    func robotSteering(robotId: String,
                       token: String) async throws -> RobotSteering {
        try await request("/robots/\(robotId)/steering", token: token)
    }

    func steerRobot(robotId: String, values: [String: Int],
                    token: String) async throws -> RobotSteering {
        try await request("/robots/\(robotId)/steering", method: "PUT",
                          body: ["values": values], token: token)
    }

    // -- the medical referral: sign, then release --

    func matchClinicians(area: String) async throws -> [ClinicianRow] {
        try await request("/referrals/match?area=\(area)")
    }

    /// Nothing is released here: the package comes back to be read, and
    /// the signature raised covers exactly those bytes.
    func prepareReferral(interactorId: String, profileId: String,
                         providerId: String,
                         token: String) async throws -> ReferralPackage {
        try await request("/referrals/prepare", method: "POST",
                          body: ["interactor_id": interactorId,
                                 "profile_id": profileId,
                                 "provider_id": providerId],
                          token: token)
    }

    func releaseReferral(referralId: String, signatureId: String,
                         token: String) async throws -> ReferralPackage {
        try await request("/referrals/\(referralId)/release", method: "POST",
                          body: ["signature_id": signatureId], token: token)
    }

    /// The clinician's side: once, and a second attempt says so.
    func openReferral(referralId: String,
                      linkToken: String) async throws -> ReferralPackage {
        try await request("/referrals/\(referralId)?token=\(linkToken)")
    }

    func replyToReferral(referralId: String, linkToken: String,
                         content: String) async throws -> ReferralPackage {
        try await request("/referrals/\(referralId)/reply?token=\(linkToken)",
                          method: "POST", body: ["content": content])
    }

    // -- the objection --

    func objection(objectionId: String) async throws -> ObjectionCard {
        try await request("/objections/\(objectionId)")
    }

    func objectionAudit(objectionId: String,
                        token: String) async throws -> ObjectionAudit {
        try await request("/objections/\(objectionId)/audit", token: token)
    }

    func withdrawObjectionConsent(
            objectionId: String) async throws -> ObjectionCard {
        try await request("/objections/\(objectionId)/withdraw",
                          method: "POST")
    }

    func revokeObjectionBasis(
            objectionId: String) async throws -> ObjectionCard {
        try await request("/objections/\(objectionId)/revoke", method: "POST")
    }

    /// Reviewer-only: an owner cannot adjudicate an objection against
    /// their own profile, and the backend enforces it by role.
    func resolveObjection(objectionId: String, outcome: String,
                          token: String) async throws -> ObjectionCard {
        try await request("/objections/\(objectionId)/resolve",
                          method: "POST", body: ["outcome": outcome],
                          token: token)
    }

    // -- the game lobby --

    func lobbyRules() async throws -> [String] {
        struct Box: Decodable { let rules: [String]? }
        let box: Box = try await request("/gaming/lobby/vocabulary")
        return box.rules ?? []
    }

    func seatInLobby(sessionId: String, memberKind: String, memberId: String,
                     role: String, token: String) async throws -> LobbySeat {
        try await request("/gaming/sessions/\(sessionId)/lobby",
                          method: "POST",
                          body: ["member_kind": memberKind,
                                 "member_id": memberId, "role": role],
                          token: token)
    }

    func lobbyRoster(sessionId: String,
                     token: String) async throws -> [LobbySeat] {
        struct Box: Decodable { let members: [LobbySeat]? }
        let box: Box = try await request(
            "/gaming/sessions/\(sessionId)/lobby", token: token)
        return box.members ?? []
    }

    func leaveLobby(sessionId: String, memberId: String,
                    token: String) async throws {
        struct Out: Decodable {}
        let _: Out = try await request(
            "/gaming/sessions/\(sessionId)/lobby", method: "DELETE",
            body: ["member_id": memberId], token: token)
    }

    /// What a synthetic member is told — including that some of the other
    /// callsigns are synthetic too.
    func lobbyContext(sessionId: String,
                      token: String) async throws -> [String: String] {
        struct Ctx: Decodable { let note: String? }
        let out: Ctx = try await request(
            "/gaming/sessions/\(sessionId)/lobby/context", token: token)
        return ["note": out.note ?? ""]
    }

    // -- the helper dock --

    func dockFaces() async throws -> [String] {
        struct Box: Decodable { let faces: [String]? }
        let box: Box = try await request("/dock/faces")
        return box.faces ?? []
    }

    /// The dock is read-only, so every face carries a way out of it.
    func dockWhere(face: String) async throws -> [String: String] {
        struct Out: Decodable { let screen: String?; let tab: String? }
        let out: Out = try await request("/dock/where/\(face)")
        return ["screen": out.screen ?? "", "tab": out.tab ?? ""]
    }

    func dockSettings(profileId: String,
                      token: String) async throws -> DockSettings {
        try await request("/dock/\(profileId)", token: token)
    }

    func configureDock(profileId: String, corner: String, state: String,
                       token: String) async throws -> DockSettings {
        try await request("/dock/\(profileId)", method: "PUT",
                          body: ["corner": corner, "state": state],
                          token: token)
    }

    func dockFace(profileId: String, name: String,
                  token: String) async throws -> [String: String] {
        struct Out: Decodable { let face: String?; let line: String? }
        let out: Out = try await request("/dock/\(profileId)/face/\(name)",
                                         token: token)
        return ["face": out.face ?? "", "line": out.line ?? ""]
    }
}

// MARK: - The signature, the mail server, the room's ear, the wall screen,
// the plan, the handoff and the campaign
//
// Seven small blocks that close out the mid-sized doorless groups: the
// signature evidence a person can read and a stranger can verify, the
// deployment's own mail settings, the room-microphone disclosure, the
// fixed screen's faces, the membership, the consented handoff, and the
// crowdfunding campaign.

struct SignatureCertificate: Decodable {
    let printed_name: String?
    let meaning: String?
    let signed_at: String?
}

struct SignatureVerdict: Decodable {
    let valid: Bool?
    let verified: Bool?
    var stands: Bool { valid ?? verified ?? false }
}

struct MailSettingsCard: Decodable {
    let transport: String?
    let host: String?
    let sender: String?
}

struct RoomCard: Decodable, Identifiable {
    let id: String
    let topic: String?
    let channel: String?
    let participants: Int?
}

/// A standing room: a blueprint the server keeps so the Rooms door never
/// greets a newcomer with an empty list. Opening one goes through the same
/// POST /rooms as a typed topic.
struct RoomTemplate: Decodable, Identifiable {
    let key: String
    let topic: String?
    let channel: String?
    let pitch: String?
    var id: String { key }
}

struct DisplayCard: Decodable {
    let id: String?
    let kind: String?
    let faces: [String]?
    let showing: String?
}

struct MembershipCard: Decodable {
    let plan: String?
    let status: String?
}

struct HandoffCard: Decodable {
    let id: String?
    let provider: String?
    let token: String?
    let sealed: Bool?
    var identity: String { id ?? "?" }
}

struct CampaignCard: Decodable {
    let id: String?
    let title: String?
    let raised: Double?
    let goal: Double?
    let status: String?
}

extension ApiClient {
    // -- the signature --

    func signatureCertificate(
            sigId: String) async throws -> SignatureCertificate {
        try await request("/signatures/\(sigId)/certificate")
    }

    /// No token, no lookup, no trust in this deployment beyond the
    /// arithmetic.
    func verifySignaturePackage(
            package: [String: Any]) async throws -> SignatureVerdict {
        try await request("/signatures/verify", method: "POST",
                          body: ["package": package])
    }

    func reproofCredential(rowId: String, level: String, attestor: String,
                           method: String, ref: String,
                           token: String) async throws -> [String: String] {
        struct Out: Decodable { let proofing_level: String? }
        let out: Out = try await request(
            "/signatures/credentials/\(rowId)/proofing", method: "POST",
            body: ["proofing_level": level, "proofing_attestor": attestor,
                   "proofing_method": method, "proofing_ref": ref],
            token: token)
        return ["proofing_level": out.proofing_level ?? ""]
    }

    /// The WebAuthn ceremony page, served from the relying party's own
    /// origin — opened in a web view, never re-implemented in the shell.
    func signatureCeremonyUrl() -> URL {
        base.appendingPathComponent("/signatures/ceremony")
    }

    // -- the deployment's mail --

    func mailSettings() async throws -> MailSettingsCard {
        try await request("/settings/mail")
    }

    func saveMailSettings(host: String, port: Int, sender: String,
                          token: String) async throws -> MailSettingsCard {
        try await request("/settings/mail", method: "PUT",
                          body: ["host": host, "port": port,
                                 "sender": sender],
                          token: token)
    }

    func forgetMailSettings(token: String) async throws {
        struct Out: Decodable { let transport: String? }
        let _: Out = try await request("/settings/mail", method: "DELETE",
                                       token: token)
    }

    /// A settings screen that saves without ever proving it can deliver is
    /// how an app ends up insisting it emailed somebody.
    func testMailSettings(to: String, token: String) async throws {
        struct Out: Decodable { let sent: Bool? }
        let _: Out = try await request("/settings/mail/test", method: "POST",
                                       body: ["to": to], token: token)
    }

    // -- the rooms and the lent ear --

    func rooms() async throws -> [RoomCard] {
        try await request("/rooms")
    }

    func roomTemplates() async throws -> [RoomTemplate] {
        try await request("/rooms/templates")
    }

    /// Step into a live room: the token names the joiner, joining twice
    /// is being there once, and the table seats eight.
    func joinRoom(roomId: String, token: String) async throws {
        struct Out: Decodable { let id: String? }
        let _: Out = try await request("/rooms/\(roomId)/join",
                                       method: "POST", token: token)
    }

    /// Step into a standing room — the room, not a copy of it: joins the
    /// live one with a seat left, opens it fresh only when nobody is there.
    func openStandingRoom(key: String, profileId: String,
                          token: String) async throws -> RoomCreated {
        try await request("/rooms/templates/\(key)/open",
                          method: "POST", token: token,
                          query: ["profile_id": profileId])
    }

    func lendRoomMic(roomId: String, interactorId: String,
                     token: String) async throws {
        struct Out: Decodable { let lent: Bool? }
        let _: Out = try await request("/rooms/\(roomId)/mic",
                                       method: "POST",
                                       body: ["interactor_id": interactorId],
                                       token: token)
    }

    func takeBackRoomMic(roomId: String, interactorId: String,
                         token: String) async throws {
        struct Out: Decodable {}
        let _: Out = try await request(
            "/rooms/\(roomId)/mic/\(interactorId)", method: "DELETE",
            token: token)
    }

    /// Readable by anyone in the room — a disclosure only its subject can
    /// see is not a disclosure.
    func roomMicDisclosure(roomId: String,
                           token: String) async throws -> MicDisclosure {
        try await request("/rooms/\(roomId)/mic", token: token)
    }

    // -- the fixed screen --

    func displayRules() async throws -> [String] {
        struct Box: Decodable { let never: [String: String]? }
        let box: Box = try await request("/displays/vocabulary")
        return (box.never ?? [:]).values.sorted()
    }

    func display(displayId: String) async throws -> DisplayCard {
        try await request("/displays/\(displayId)")
    }

    func setDisplayFaces(displayId: String, faces: [String],
                         token: String) async throws -> DisplayCard {
        try await request("/displays/\(displayId)/faces", method: "PUT",
                          body: ["faces": faces], token: token)
    }

    func takeDownDisplay(displayId: String, token: String) async throws {
        struct Out: Decodable {}
        let _: Out = try await request("/displays/\(displayId)",
                                       method: "DELETE", token: token)
    }

    // -- the membership --

    func membership(accountId: String,
                    token: String) async throws -> MembershipCard {
        try await request("/memberships/\(accountId)", token: token)
    }

    func joinPlan(accountId: String, plan: String,
                  token: String) async throws -> MembershipCard {
        try await request("/memberships/\(accountId)", method: "POST",
                          body: ["plan": plan], token: token)
    }

    /// The account becomes a visitor and keeps its profiles — a lapsed
    /// subscription is not a reason to delete somebody's work.
    func cancelMembership(accountId: String,
                          token: String) async throws -> MembershipCard {
        try await request("/memberships/\(accountId)", method: "DELETE",
                          token: token)
    }

    // -- the handoff --

    func createHandoff(interactorId: String, profileId: String,
                       providerId: String,
                       token: String) async throws -> HandoffCard {
        try await request("/handoffs", method: "POST",
                          body: ["interactor_id": interactorId,
                                 "profile_id": profileId,
                                 "provider_id": providerId,
                                 "consent": true],
                          token: token)
    }

    func openHandoff(handoffId: String,
                     linkToken: String) async throws -> HandoffCard {
        try await request("/handoffs/\(handoffId)?token=\(linkToken)")
    }

    func revokeHandoff(handoffId: String, token: String) async throws {
        struct Out: Decodable { let revoked: Bool? }
        let _: Out = try await request("/handoffs/\(handoffId)",
                                       method: "DELETE", token: token)
    }

    // -- the campaign --

    func campaign(campaignId: String) async throws -> CampaignCard {
        try await request("/campaigns/\(campaignId)")
    }

    /// No token required — a donor arriving from a beacon scan has no
    /// account, and requiring one gates generosity behind signup.
    func donate(campaignId: String, amount: Double,
                note: String) async throws -> CampaignCard {
        try await request("/campaigns/\(campaignId)/donate", method: "POST",
                          body: ["amount": amount, "note": note])
    }

    func closeCampaign(campaignId: String,
                       token: String) async throws -> CampaignCard {
        try await request("/campaigns/\(campaignId)/close", method: "POST",
                          token: token)
    }

    // -- the owner's workshop: workflows, delegation, the assistant,
    // tasks under a grant, rated placements and specialists ---------------

    func workflows(id: String, token: String) async throws -> [WorkflowCard] {
        try await request("/profiles/\(id)/workflows", token: token)
    }

    func startWorkflow(id: String, goal: String,
                       token: String) async throws -> WorkflowCard {
        try await request("/profiles/\(id)/workflows", method: "POST",
                          body: ["goal": goal], token: token)
    }

    func workflow(id: String, workflowId: String,
                  token: String) async throws -> WorkflowCard {
        try await request("/profiles/\(id)/workflows/\(workflowId)",
                          token: token)
    }

    func advanceWorkflow(id: String, workflowId: String,
                         token: String) async throws -> WorkflowCard {
        try await request("/profiles/\(id)/workflows/\(workflowId)/advance",
                          method: "POST", token: token)
    }

    func resumeWorkflow(id: String, workflowId: String, input: String,
                        token: String) async throws -> WorkflowCard {
        try await request("/profiles/\(id)/workflows/\(workflowId)/resume",
                          method: "POST", body: ["input": input],
                          token: token)
    }

    func cancelWorkflow(id: String, workflowId: String,
                        token: String) async throws -> WorkflowCard {
        try await request("/profiles/\(id)/workflows/\(workflowId)/cancel",
                          method: "POST", token: token)
    }

    // -- delegated work: what somebody else may start here --

    /// A capability advertisement, readable without a token, so a caller
    /// can decide whether a handoff is possible before attempting one.
    func delegationOffer(id: String) async throws -> DelegationOffer {
        try await request("/profiles/\(id)/delegation")
    }

    func setDelegation(id: String, phases: [String],
                       token: String) async throws -> DelegationOffer {
        try await request("/profiles/\(id)/delegation", method: "PUT",
                          body: ["phases": phases], token: token)
    }

    func startDelegatedWorkflow(id: String, interactorId: String,
                                goal: String,
                                token: String) async throws -> WorkflowCard {
        try await request("/profiles/\(id)/delegated-workflows",
                          method: "POST",
                          body: ["goal": goal,
                                 "interactor_id": interactorId],
                          token: token)
    }

    func delegatedWorkflow(id: String, workflowId: String,
                           token: String) async throws -> WorkflowCard {
        try await request(
            "/profiles/\(id)/delegated-workflows/\(workflowId)",
            token: token)
    }

    func advanceDelegatedWorkflow(id: String, workflowId: String,
                                  token: String) async throws -> WorkflowCard {
        try await request(
            "/profiles/\(id)/delegated-workflows/\(workflowId)/advance",
            method: "POST", token: token)
    }

    func resumeDelegatedWorkflow(id: String, workflowId: String,
                                 input: String,
                                 token: String) async throws -> WorkflowCard {
        try await request(
            "/profiles/\(id)/delegated-workflows/\(workflowId)/resume",
            method: "POST", body: ["input": input], token: token)
    }

    // -- the assistant --

    func composeNote(id: String, moment: String,
                     token: String) async throws -> CreativeWork {
        try await request("/profiles/\(id)/assist/compose", method: "POST",
                          body: ["kind": "note", "moment": moment],
                          token: token)
    }

    func composedWorks(id: String,
                       token: String) async throws -> [CreativeWork] {
        try await request("/profiles/\(id)/assist/works", token: token)
    }

    func proofread(id: String, text: String,
                   token: String) async throws -> ProofreadOut {
        try await request("/profiles/\(id)/assist/proofread",
                          method: "POST", body: ["text": text], token: token)
    }

    func triage(id: String, items: [[String: String]], keep: Int,
                criteria: String,
                token: String) async throws -> TriageOut {
        try await request("/profiles/\(id)/assist/triage", method: "POST",
                          body: ["items": items, "keep": keep,
                                 "criteria": criteria],
                          token: token)
    }

    // -- autonomous tasks under a revocable grant --

    func mintTaskGrant(id: String,
                       token: String) async throws -> TaskGrant {
        try await request("/profiles/\(id)/grants", method: "POST",
                          body: ["scope": ["*"]], token: token)
    }

    func revokeTaskGrant(grantId: String, token: String) async throws {
        struct Out: Decodable { let revoked: Bool? }
        let _: Out = try await request("/grants/\(grantId)",
                                       method: "DELETE", token: token)
    }

    func runTask(id: String, topic: String, grantToken: String,
                 token: String) async throws -> TaskOut {
        try await request("/profiles/\(id)/tasks", method: "POST",
                          body: ["topic": topic, "grant_token": grantToken],
                          token: token)
    }

    func tasksRun(id: String, token: String) async throws -> [TaskRow] {
        try await request("/profiles/\(id)/tasks", token: token)
    }

    // -- rated placements: marketing at adult venues --

    func ratedVenues() async throws -> [VenueCard] {
        try await request("/venues")
    }

    func placeRated(id: String, venue: String, label: String,
                    token: String) async throws -> PlacementMade {
        try await request("/profiles/\(id)/placements", method: "POST",
                          body: label.isEmpty
                              ? ["venue": venue]
                              : ["venue": venue, "label": label],
                          token: token)
    }

    func placements(id: String,
                    token: String) async throws -> [PlacementRow] {
        try await request("/profiles/\(id)/placements", token: token)
    }

    func placementAnalytics(id: String,
                            token: String) async throws -> PlacementStats {
        try await request("/profiles/\(id)/placements/analytics",
                          token: token)
    }

    func placementCustody(id: String,
                          token: String) async throws -> PlacementCustody {
        try await request("/profiles/\(id)/placements/custody",
                          token: token)
    }

    func removePlacement(placementId: String, token: String) async throws {
        struct Out: Decodable { let removed: Bool? }
        let _: Out = try await request("/placements/\(placementId)",
                                       method: "DELETE", token: token)
    }

    // -- domain specialists --

    func specialists(id: String,
                     token: String) async throws -> [SpecialistRow] {
        try await request("/profiles/\(id)/specialists", token: token)
    }

    func setSpecialist(id: String, domain: String, specialistId: String,
                       token: String) async throws -> SpecialistRow {
        try await request("/profiles/\(id)/specialists", method: "PUT",
                          body: ["domain": domain,
                                 "specialist_profile_id": specialistId],
                          token: token)
    }

    // -- the record, the veil and the exit: what the platform holds about
    // a profile, what its anonymity hides, and how it ends ---------------

    func memories(id: String, token: String) async throws -> [MemoryRow] {
        try await request("/profiles/\(id)/memories", token: token)
    }

    func memory(id: String, interactorId: String,
                token: String) async throws -> [MemoryTurn] {
        try await request("/profiles/\(id)/memory/\(interactorId)",
                          token: token)
    }

    struct Remembrance: Decodable {
        let content: String?
        let covers: Int
    }

    /// The distilled long memory of one person — what survived the window.
    func remembrance(id: String, interactorId: String,
                     token: String) async throws -> Remembrance {
        try await request(
            "/profiles/\(id)/memory/\(interactorId)/remembrance",
            token: token)
    }

    struct MemoryAccount: Decodable {
        let remembers: String?
        let folded_turns: Int
        let recent_turns: Int
    }

    /// What do you remember about me — answered from the records.
    func memoryAccount(id: String, interactorId: String,
                       token: String) async throws -> MemoryAccount {
        try await request(
            "/profiles/\(id)/memory/\(interactorId)/account",
            token: token)
    }

    struct ForgetOut: Decodable {
        let forgotten_turns: Int
        let remembrance_reset: Bool
    }

    /// Forget that one thing; the kept memory re-folds from what remains.
    func forgetMemory(id: String, interactorId: String, about: String,
                      token: String) async throws -> ForgetOut {
        try await request(
            "/profiles/\(id)/memory/\(interactorId)/forget",
            method: "POST", body: ["about": about], token: token)
    }

    func eraseMemory(id: String, interactorId: String,
                     token: String) async throws {
        struct Out: Decodable {}
        let _: Out = try await request(
            "/profiles/\(id)/memory/\(interactorId)", method: "DELETE",
            token: token)
    }

    struct StrikeOut: Decodable {
        let struck_turns: Int
        let remembrance_reset: Bool
    }

    /// Strike selected turns by id; the kept memory re-folds from what
    /// remains — never from what was struck.
    func strikeTurns(id: String, interactorId: String, messageIds: [String],
                     token: String) async throws -> StrikeOut {
        try await request(
            "/profiles/\(id)/memory/\(interactorId)/strike",
            method: "POST", body: ["message_ids": messageIds], token: token)
    }

    struct TurnEditOut: Decodable {
        let turn: MemoryTurn
        let remembrance_reset: Bool
    }

    /// Rewrite one remembered turn. A profile turn loses its synthetic-media
    /// credential — it must not vouch for words a person rewrote.
    func editTurn(id: String, interactorId: String, messageId: String,
                  content: String, token: String) async throws -> TurnEditOut {
        try await request(
            "/profiles/\(id)/memory/\(interactorId)/turns/\(messageId)",
            method: "PUT", body: ["content": content], token: token)
    }

    // -- between the profile and one person --

    func thread(id: String, interactorId: String,
                token: String) async throws -> ThreadOut {
        try await request("/profiles/\(id)/thread/\(interactorId)",
                          token: token)
    }

    func engagement(id: String, interactorId: String,
                    token: String) async throws -> EngagementCard {
        try await request("/profiles/\(id)/engagement/\(interactorId)",
                          token: token)
    }

    /// The pair may read it — the person it is about, and the profile's
    /// owner — and nobody else: it is that person's medical information.
    func clinicalNotes(id: String, interactorId: String,
                       token: String) async throws -> [ClinicalNote] {
        try await request(
            "/profiles/\(id)/clinical-notes/\(interactorId)",
            token: token)
    }

    func embedding(id: String, interactorId: String,
                   token: String) async throws -> EmbeddingCard {
        try await request("/profiles/\(id)/embedding/\(interactorId)",
                          token: token)
    }

    // -- source material --

    func sources(id: String, token: String) async throws -> [SourceRow] {
        try await request("/profiles/\(id)/sources", token: token)
    }

    func addSource(id: String, kind: String, title: String, content: String,
                   token: String) async throws -> SourceRow {
        try await request("/profiles/\(id)/sources", method: "POST",
                          body: ["kind": kind, "title": title,
                                 "content": content],
                          token: token)
    }

    // -- the record --

    /// Public on purpose: how many relationships this profile holds, and
    /// which model actually answers for it.
    func transparency(id: String) async throws -> TransparencyCard {
        try await request("/profiles/\(id)/transparency")
    }

    func exportProfile(id: String, token: String) async throws -> ExportOut {
        try await request("/profiles/\(id)/export", token: token)
    }

    struct ExportTicket: Decodable {
        let ticket: String
        let url: String
        let qr_svg: String
        let expires_at: String
        let note: String
    }

    /// A one-time, minutes-long handoff of the export to another device:
    /// the QR carries the ticket, never the owner token.
    func exportTicket(id: String, token: String) async throws -> ExportTicket {
        try await request("/profiles/\(id)/export/ticket", method: "POST",
                          token: token)
    }

    /// The redeeming side — tokenless, the single-use ticket is the whole
    /// authority.
    func exportHandoff(id: String, ticket: String) async throws -> ExportOut {
        try await request("/profiles/\(id)/export/handoff/\(ticket)")
    }

    /// Where the scannable code lives; reading it does not consume the
    /// ticket.
    func exportHandoffQrURL(id: String, ticket: String) -> URL {
        base.appendingPathComponent(
            "/profiles/\(id)/export/handoff/\(ticket)/qr.svg")
    }

    func profileStats(id: String, token: String) async throws -> StatsCard {
        try await request("/profiles/\(id)/stats", token: token)
    }

    func feed(id: String) async throws -> FeedOut {
        try await request("/profiles/\(id)/feed")
    }

    // -- the veil --

    func anonymity(id: String, token: String) async throws -> VeilCard {
        try await request("/profiles/\(id)/anonymity", token: token)
    }

    func setAnonymity(id: String, anonymous: Bool,
                      token: String) async throws -> VeilCard {
        try await request("/profiles/\(id)/anonymity", method: "PUT",
                          body: ["anonymous": anonymous], token: token)
    }

    // -- verification --

    /// Public: a claim a stranger can see is a claim a stranger should be
    /// able to check.
    func verification(id: String) async throws -> VerificationCard {
        try await request("/profiles/\(id)/verification")
    }

    func claimVerification(id: String, level: String, attestor: String,
                           token: String) async throws -> VerificationCard {
        try await request("/profiles/\(id)/verification", method: "POST",
                          body: ["level": level, "attestor": attestor,
                                 "method": "document"],
                          token: token)
    }

    func moveBadgeHere(id: String, token: String) async throws
        -> VerificationCard {
        try await request("/profiles/\(id)/verification/move",
                          method: "POST", token: token)
    }

    func verifiable(id: String, token: String) async throws -> VerifiableOut {
        try await request("/profiles/\(id)/verifiable", token: token)
    }

    // -- the exit --

    func editProfile(id: String, displayName: String?, persona: String?,
                     token: String) async throws -> ProfilePatched {
        var body: [String: Any] = [:]
        if let displayName, !displayName.isEmpty {
            body["display_name"] = displayName
        }
        if let persona, !persona.isEmpty { body["persona"] = persona }
        return try await request("/profiles/\(id)", method: "PATCH",
                                 body: body, token: token)
    }

    func sunset(id: String, token: String) async throws -> SunsetOut {
        try await request("/profiles/\(id)/sunset", method: "POST",
                          token: token)
    }

    /// Public memorial for a departed profile — never persona internals.
    func memorial(id: String) async throws -> MemorialCard {
        try await request("/profiles/\(id)/memorial")
    }

    func siblings(id: String, token: String) async throws -> RosterOut {
        try await request("/profiles/\(id)/siblings", token: token)
    }

    func succeed(id: String, verificationRef: String,
                 token: String) async throws -> SucceedOut {
        try await request("/profiles/\(id)/succeed", method: "POST",
                          body: ["verification_ref": verificationRef],
                          token: token)
    }

    func deleteProfile(id: String, token: String) async throws {
        struct Out: Decodable {}
        let _: Out = try await request("/profiles/\(id)", method: "DELETE",
                                       token: token)
    }
}

struct WorkflowCard: Decodable, Identifiable {
    let id: String
    let goal: String
    let status: String
    let next_phase: String?
    let delegated_to: String?
}

struct DelegationOffer: Decodable {
    let delegation: Bool?
    let phases: [String]?
}

struct CreativeWork: Decodable, Identifiable {
    let id: String
    let kind: String
    let moment: String
    let content: String
}

struct ProofreadOut: Decodable {
    let edited: String?
    let suggestions: [String]
    let status: String
}

struct TriageOut: Decodable {
    struct Kept: Decodable { let id: String; let reason: String }
    let reviewed: Int
    let kept: [Kept]
    let discarded_ids: [String]
}

struct TaskGrant: Decodable, Identifiable {
    let id: String
    let token: String
    let scope: [String]
}

struct TaskOut: Decodable {
    let status: String
    let reason: String?
}

struct TaskRow: Decodable, Identifiable {
    let id: String
    let topic: String
    let status: String
}

struct VenueCard: Decodable {
    let key: String
    let name: String
    let hosts: [String]?
}

struct PlacementMade: Decodable {
    let placement_id: String
    let beacon_id: String
    let scan_url: String
    let rated: Bool
}

struct PlacementRow: Decodable, Identifiable {
    let id: String
    let venue_name: String
    let label: String?
    let scans: Int
    let active: Bool
}

struct PlacementStats: Decodable {
    struct Funnel: Decodable {
        let resolutions: Int
        let verified_views: Int
        let unique_chatters: Int
    }
    let funnel: Funnel
}

struct PlacementCustody: Decodable {
    let count: Int
    let chain_intact: Bool
}

struct SpecialistRow: Decodable {
    let domain: String
    let specialist_profile_id: String
}

extension ApiClient {
    // -- the face it shows the world: portrait, emblem, page, front,
    // surfaces, blend, bodies, dials and the wrist -----------------------

    /// Public: the portrait as it must be displayed — asset, AI badge,
    /// and whose likeness it is.
    func avatar(id: String) async throws -> AvatarCard {
        try await request("/profiles/\(id)/avatar")
    }

    func setAvatar(id: String, asset: String,
                   token: String) async throws -> AvatarCard {
        try await request("/profiles/\(id)/avatar", method: "PUT",
                          body: ["asset": asset], token: token)
    }

    /// Public because it is the honest version of "where did these faces
    /// come from": every starter portrait is an invented person, and the
    /// brief that produced it says so in its own constraints.
    func avatarBriefs() async throws -> BriefCatalog {
        try await request("/avatars/briefs")
    }

    struct MarketSource: Decodable { let key: String; let name: String; let how: String }
    struct MarketShelf: Decodable { let sources: [MarketSource]; let note: String }

    func avatarMarket() async throws -> MarketShelf {
        try await request("/avatars/market")
    }

    func importAvatar(id: String, source: String, asset: String,
                      token: String) async throws -> AvatarCard {
        try await request("/profiles/\(id)/avatar/import", method: "POST",
                          body: ["source": source, "asset": asset],
                          token: token)
    }

    func avatarBrief(handle: String) async throws -> BriefCard {
        try await request("/avatars/briefs/\(handle)")
    }

    // -- the emblem and the badge --

    func identityEmblems() async throws -> EmblemCatalog {
        try await request("/identity/emblems")
    }

    func identityVocabulary() async throws -> IdentityVocabulary {
        try await request("/identity/vocabulary")
    }

    func setEmblem(id: String, emblem: String,
                   token: String) async throws -> EmblemOut {
        try await request("/profiles/\(id)/emblem", method: "PUT",
                          body: ["emblem": emblem], token: token)
    }

    /// Public, and not the same read as /verification: on an anonymous
    /// profile the attestor is withheld, because "checked by Dr Okafor of
    /// St Mary's" narrows an anonymous author to a city and a workplace.
    func badge(id: String) async throws -> BadgeCard {
        try await request("/profiles/\(id)/badge")
    }

    // -- the page --

    func pageThemes() async throws -> ThemeCatalog {
        try await request("/pages/themes")
    }

    func page(id: String) async throws -> PageCard {
        try await request("/profiles/\(id)/page")
    }

    func editPage(id: String, theme: String?, tagline: String?,
                  about: String?, token: String) async throws -> PageCard {
        var body: [String: Any] = [:]
        if let theme, !theme.isEmpty { body["theme"] = theme }
        if let tagline, !tagline.isEmpty { body["tagline"] = tagline }
        if let about, !about.isEmpty { body["about"] = about }
        return try await request("/profiles/\(id)/page", method: "PUT",
                                 body: body, token: token)
    }

    /// Everything a visitor's first screen needs, in one call — the
    /// caller is a scan page on cellular, and five round trips is how a
    /// page arrives in pieces.
    func frontPage(id: String) async throws -> FrontCard {
        try await request("/profiles/\(id)/front")
    }

    // -- surfaces and the blend --

    func surfaces(id: String) async throws -> SurfacesCard {
        try await request("/profiles/\(id)/surfaces")
    }

    func setSurfaces(id: String, surfaces: [String],
                     token: String) async throws -> SurfacesCard {
        try await request("/profiles/\(id)/surfaces", method: "PUT",
                          body: ["surfaces": surfaces], token: token)
    }

    /// Public, the same open stance as /transparency: the blend is the
    /// profile's provenance.
    func composition(id: String) async throws -> CompositionCard {
        try await request("/profiles/\(id)/composition")
    }

    // -- the bodies it lives in --

    func embodiments(id: String,
                     token: String) async throws -> [EmbodimentRow] {
        try await request("/profiles/\(id)/embodiments", token: token)
    }

    func addEmbodiment(id: String, name: String, kind: String,
                       token: String) async throws -> EmbodimentRow {
        try await request("/profiles/\(id)/embodiments", method: "POST",
                          body: ["name": name, "kind": kind,
                                 "has_llm": false],
                          token: token)
    }

    /// Public: anyone meeting the profile through any form can verify it
    /// is the same personality.
    func embodimentConsistency(id: String) async throws -> ConsistencyCard {
        try await request("/profiles/\(id)/embodiment-consistency")
    }

    func profileDisplays(id: String,
                         token: String) async throws -> ProfileDisplayList {
        try await request("/profiles/\(id)/displays", token: token)
    }

    func addProfileDisplay(id: String, kind: String, label: String,
                           token: String) async throws -> ProfileDisplayRow {
        try await request("/profiles/\(id)/displays", method: "POST",
                          body: ["kind": kind, "label": label],
                          token: token)
    }

    // -- the dials --

    func steering(id: String, token: String) async throws -> SteeringCard {
        try await request("/profiles/\(id)/steering", token: token)
    }

    /// Dials are 0–100 integers. Intimacy is hard-clamped to 0 unless the
    /// profile is adult-mode — it can never be raised on a non-rated
    /// persona.
    func setSteering(id: String, values: [String: Int],
                     token: String) async throws -> SteeringCard {
        try await request("/profiles/\(id)/steering", method: "PUT",
                          body: ["values": values], token: token)
    }

    /// The personality nobody can move: while the lock stands, no
    /// steering write lands. The key is the owner's.
    func lockSteering(id: String, token: String,
                      reason: String?) async throws -> SteeringLockOut {
        var body: [String: Any] = [:]
        if let reason, !reason.isEmpty { body["reason"] = reason }
        return try await request("/profiles/\(id)/steering/lock",
                                 method: "POST", body: body, token: token)
    }

    func unlockSteering(id: String, token: String) async throws {
        struct Out: Decodable { let subject_id: String }
        let _: Out = try await request("/profiles/\(id)/steering/lock",
                                       method: "DELETE", token: token)
    }

    // -- the wrist --

    func watchFace(id: String, token: String) async throws -> WatchFace {
        try await request("/profiles/\(id)/watch", token: token)
    }

    func watchAct(id: String, target: String, targetId: String,
                  action: String, input: String,
                  token: String) async throws -> WatchActOut {
        var body: [String: Any] = ["target": target, "id": targetId,
                                   "action": action]
        if !input.isEmpty { body["input"] = input }
        return try await request("/profiles/\(id)/watch/act",
                                 method: "POST", body: body, token: token)
    }

    // -- the keys: the account itself --

    func signup(email: String, password: String,
                displayName: String) async throws -> SignupOut {
        var body: [String: Any] = ["email": email, "password": password]
        if !displayName.isEmpty { body["display_name"] = displayName }
        return try await request("/signup", method: "POST", body: body)
    }

    /// Unknown address and wrong password get the same answer; an
    /// unverified address cannot sign in at all.
    func signin(email: String, password: String) async throws -> SessionOut {
        try await request("/signin", method: "POST",
                          body: ["email": email, "password": password])
    }

    func verifyEmail(email: String, code: String) async throws -> SessionOut {
        try await request("/verify-email", method: "POST",
                          body: ["email": email, "code": code])
    }

    /// Same answer whether or not the address has an account — the
    /// endpoint is not an address oracle, and neither is this button.
    func resendCode(email: String) async throws -> CodeDelivery {
        try await request("/verify-email/resend", method: "POST",
                          body: ["email": email])
    }

    func requestPasswordReset(email: String) async throws -> CodeDelivery {
        try await request("/password/reset/request", method: "POST",
                          body: ["email": email])
    }

    /// Every existing account session dies with the old password.
    func resetPassword(email: String, code: String,
                       newPassword: String) async throws -> ResetOut {
        try await request("/password/reset", method: "POST",
                          body: ["email": email, "code": code,
                                 "new_password": newPassword])
    }

    func oauthProviders() async throws -> OAuthProviderList {
        try await request("/auth/oauth/providers")
    }

    func oauthStart(provider: String) async throws -> OAuthStartOut {
        try await request("/auth/oauth/\(provider)/start",
                          method: "POST", body: [:])
    }

    /// One-time pickup of a completed browser sign-in; the first
    /// successful claim spends the state.
    func oauthClaim(state: String) async throws -> OAuthClaimOut {
        try await request("/auth/oauth/claim", query: ["state": state])
    }

    // -- the till --

    /// Public — a paywall nobody can read the terms of before signing
    /// in is one people bounce off.
    func plans() async throws -> PlanCatalog {
        try await request("/plans")
    }

    func mySubscriptions(token: String) async throws -> SubscriptionList {
        try await request("/subscriptions", token: token)
    }

    /// Explicit on purpose: nothing bills on a timer, so renewing names
    /// the beneficiary every time.
    func renewSubscription(subId: String, beneficiary: String,
                           token: String) async throws -> SubscriptionRow {
        try await request("/subscriptions/\(subId)/renew", method: "POST",
                          body: ["beneficiary": beneficiary], token: token)
    }

    func myOrders(token: String) async throws -> OrderList {
        try await request("/orders", token: token)
    }

    /// Public: a donor gives to the names on this list, not to the
    /// platform.
    func proceedsOf(id: String) async throws -> ProceedsCard {
        try await request("/profiles/\(id)/proceeds")
    }

    func setProceeds(id: String, designees: [[String: Any]],
                     token: String) async throws -> ProceedsCard {
        try await request("/profiles/\(id)/proceeds", method: "PUT",
                          body: ["designees": designees], token: token)
    }

    func campaignsOf(id: String) async throws -> [CampaignRow] {
        try await request("/profiles/\(id)/campaigns")
    }

    func addCampaign(id: String, title: String, goal: Double, cause: String,
                     token: String) async throws -> CampaignRow {
        var body: [String: Any] = ["title": title, "goal": goal]
        if !cause.isEmpty { body["cause"] = cause }
        return try await request("/profiles/\(id)/campaigns",
                                 method: "POST", body: body, token: token)
    }

    // -- the lifeline --

    func cloudStatus() async throws -> CloudStatusCard {
        try await request("/cloud/status")
    }

    func offlineStatus() async throws -> OfflineStatusCard {
        try await request("/offline/status")
    }

    /// The legend is built from the mapping, so the key on this screen
    /// cannot describe lights the code does not have.
    func agentLights() async throws -> LightsLegend {
        try await request("/agent/lights")
    }

    func helpTopics() async throws -> HelpTopicList {
        try await request("/help/topics")
    }

    /// Public on purpose: every screen can be somebody's first, and it
    /// writes nothing.
    func askHelp(question: String) async throws -> HelpAnswer {
        try await request("/help", method: "POST",
                          body: ["question": question])
    }

    func localProviders() async throws -> [LocalProviderRow] {
        try await request("/providers")
    }

    func addLocalProvider(name: String, area: String, location: String,
                          contact: String,
                          business: Bool) async throws -> LocalProviderRow {
        var body: [String: Any] = ["name": name, "area": area,
                                   "business": business]
        if !location.isEmpty { body["location"] = location }
        if !contact.isEmpty { body["contact"] = contact }
        return try await request("/providers", method: "POST", body: body)
    }

    // -- the public stream --

    /// One page of the public stream. No token: a person who followed a
    /// shared link is a reader like any other, and the route says so.
    func publicFeed(cursor: String? = nil) async throws -> FeedPage {
        let tail = cursor.map { "&cursor=\($0)" } ?? ""
        return try await request("/feed?limit=12" + tail)
    }

    /// One card, for a link somebody was sent. 404 rather than an empty
    /// card when it is rated and this reader is not verified — a 403 would
    /// announce that the item exists.
    func feedItem(id: String) async throws -> FeedCard {
        try await request("/feed/\(id)")
    }

    // -- the sticker on the street --

    /// The in-camera overlay's read: who it is, one line of portrait, and
    /// the mark — never the face without the disclosure to draw with it.
    func beaconCard(id: String) async throws -> BeaconOverlayCard {
        try await request("/b/\(id)/card")
    }

    /// Where the printed QR actually points; a phone camera opens URLs.
    func beaconScanUrl(id: String) -> URL {
        base.appendingPathComponent("/b/\(id)")
    }

    func beaconQrUrl(id: String) -> URL {
        base.appendingPathComponent("/beacons/\(id)/qr.svg")
    }

    func deskScanCard(id: String) async throws -> DeskScanCard {
        try await request("/d/\(id)/card")
    }

    func deskScanUrl(id: String) -> URL {
        base.appendingPathComponent("/d/\(id)")
    }

    func socialBeacon(cid: String) async throws -> SocialBeaconCard {
        try await request("/social/\(cid)/beacon")
    }

    func socialQrUrl(cid: String) -> URL {
        base.appendingPathComponent("/social/\(cid)/qr.svg")
    }

    /// Same Wi-Fi, no app store: the console's URL on this network.
    func pairing() async throws -> PairCard {
        try await request("/pair")
    }

    func pairQrUrl() -> URL {
        base.appendingPathComponent("/pair/qr.svg")
    }

    // -- the queue --

    func moderationQueue(id: String,
                         token: String) async throws -> [HeldMessage] {
        try await request("/profiles/\(id)/moderation/queue", token: token)
    }

    func approveMessage(messageId: String,
                        token: String) async throws -> ModerationOut {
        try await request("/moderation/\(messageId)/approve",
                          method: "POST", body: [:], token: token)
    }

    func rejectMessage(messageId: String,
                       token: String) async throws -> ModerationOut {
        try await request("/moderation/\(messageId)/reject",
                          method: "POST", body: [:], token: token)
    }

    /// Moderated as a fresh message, and it carries forward — the next
    /// reply reasons from the correction rather than the original.
    func editMessage(id: String, messageId: String, interactorId: String,
                     content: String, token: String) async throws -> ModerationOut {
        try await request("/profiles/\(id)/messages/\(messageId)",
                          method: "PATCH",
                          body: ["interactor_id": interactorId,
                                 "content": content], token: token)
    }

    /// The row survives for the moderation trail; the text stops being
    /// shown.
    func retractMessage(id: String, messageId: String, interactorId: String,
                        token: String) async throws -> ModerationOut {
        try await request("/profiles/\(id)/messages/\(messageId)",
                          method: "DELETE",
                          body: ["interactor_id": interactorId],
                          token: token)
    }

    // -- the reviews --

    func reviewsOf(id: String) async throws -> ReviewBoard {
        try await request("/profiles/\(id)/reviews")
    }

    /// One per interactor, edited rather than stacked — and it requires
    /// having actually talked to it.
    func leaveReview(id: String, interactorId: String, rating: Int,
                     text: String, token: String) async throws -> ReviewOut {
        var body: [String: Any] = ["interactor_id": interactorId,
                                   "rating": rating]
        if !text.isEmpty { body["body"] = text }
        return try await request("/profiles/\(id)/reviews",
                                 method: "POST", body: body, token: token)
    }

    // -- the stamp --

    func watermarkCredential(id: String) async throws -> WatermarkCredential {
        try await request("/watermarks/\(id)")
    }

    /// Valid + whether the presented content still matches the hash
    /// issued at creation.
    func verifyWatermark(id: String,
                         content: String) async throws -> WatermarkCredential {
        var body: [String: Any] = ["watermark_id": id]
        if !content.isEmpty { body["content"] = content }
        return try await request("/watermarks/verify", method: "POST",
                                 body: body)
    }

    // -- the media --

    /// Published so a client can say so before an upload fails.
    func mediaLimits() async throws -> MediaLimits {
        try await request("/media/limits")
    }

    /// One photo, video or document, raw in the request body.
    func uploadMedia(id: String, filename: String, data: Data,
                     token: String) async throws -> MediaOut {
        var url = base.appendingPathComponent("/profiles/\(id)/media")
        if !filename.isEmpty,
           var parts = URLComponents(url: url, resolvingAgainstBaseURL: false) {
            parts.queryItems = [URLQueryItem(name: "filename",
                                             value: filename)]
            url = parts.url ?? url
        }
        var req = URLRequest(url: url)
        req.httpMethod = "POST"
        req.setValue("Bearer \(token)", forHTTPHeaderField: "authorization")
        req.httpBody = data
        let (out, resp) = try await dispatch(req)
        guard let http = resp as? HTTPURLResponse,
              (200..<300).contains(http.statusCode) else {
            throw ApiError.http("upload failed")
        }
        return try JSONDecoder().decode(MediaOut.self, from: out)
    }

    func videoPlatforms() async throws -> VideoPlatformBoard {
        try await request("/videos/platforms")
    }

    // -- the wearables --

    /// A paired device here is a screen and a set of buttons — no sensor
    /// stream, no capture, nothing about a microphone.
    func wearables(id: String, token: String) async throws -> WearableBoard {
        try await request("/profiles/\(id)/wearables", token: token)
    }

    func pairWearable(id: String, name: String, kind: String,
                      token: String) async throws -> WearableRow {
        try await request("/profiles/\(id)/wearables", method: "POST",
                          body: ["name": name, "kind": kind], token: token)
    }

    /// The record survives, so a device sent away cannot come back by
    /// re-presenting the same name.
    func unpairWearable(id: String, name: String,
                        token: String) async throws -> WearableRow {
        try await request("/profiles/\(id)/wearables/\(name)",
                          method: "DELETE", token: token)
    }

    // -- the birth --

    /// The short interview a profile is born from.
    func genesis(ownerId: String, name: String, social: String,
                 humor: String, matters: String,
                 comfort: String) async throws -> GenesisOut {
        var body: [String: Any] = [
            "owner_id": ownerId,
            "verification": ["birthdate": "1990-01-01"],
            "answers": ["social_style": social, "humor": humor,
                        "what_matters": matters, "comfort": comfort]]
        if !name.isEmpty { body["display_name"] = name }
        return try await request("/profiles/genesis", method: "POST",
                                 body: body)
    }

    /// A hybrid blended from several existing profiles; the blend is
    /// recorded per-constituent and published as its composition.
    func composite(ownerId: String, name: String,
                   sources: [String]) async throws -> GenesisOut {
        try await request("/profiles/composite", method: "POST",
                          body: ["owner_id": ownerId, "display_name": name,
                                 "terms_consent": true,
                                 "verification": ["birthdate": "1990-01-01"],
                                 "sources": sources.map {
                                     ["profile_id": $0] }])
    }

    func publishPack(industry: String, title: String,
                     token: String) async throws -> PackOut {
        try await request("/packs", method: "POST",
                          body: ["industry": industry, "title": title,
                                 "items": [["title": title,
                                            "content": title]]],
                          token: token)
    }

    /// One free Field Pack per industry.
    func seedPacks() async throws -> PackSeedOut {
        try await request("/packs/seed", method: "POST", body: [:])
    }

    // -- the mind at work --

    /// Owner-only operational insight; the narrative is watermarked
    /// synthetic and never distributed.
    func simulate(id: String, scenario: String,
                  token: String) async throws -> SimulationOut {
        try await request("/profiles/\(id)/simulate", method: "POST",
                          body: ["scenario": scenario], token: token)
    }

    func simulations(id: String,
                     token: String) async throws -> [SimulationOut] {
        try await request("/profiles/\(id)/simulations", token: token)
    }

    func finetune(id: String, token: String) async throws -> FinetuneOut {
        try await request("/profiles/\(id)/finetune", method: "POST",
                          body: [:], token: token)
    }

    /// Whether contribution is on, exactly what the next one would
    /// contain, and the log of everything that has ever left.
    func cloudContribution(id: String,
                           token: String) async throws -> ContributionView {
        try await request("/profiles/\(id)/cloud-contribution",
                          token: token)
    }

    /// Off, and everything already contributed deleted at the gateway.
    func revokeContributions(id: String,
                             token: String) async throws -> RevokeOut {
        try await request("/profiles/\(id)/cloud-contribution/revoke",
                          method: "POST", body: [:], token: token)
    }

    func excursion(cid: String, token: String) async throws -> ExcursionOut {
        try await request("/excursions/\(cid)", token: token)
    }

    // -- the reach --

    /// Allowed only when the owner opted in with proactive scope.
    func proactiveCheckin(id: String, interactorId: String,
                          token: String) async throws -> CheckinOut {
        try await request("/profiles/\(id)/proactive/\(interactorId)",
                          method: "POST", body: [:], token: token)
    }

    /// The recipient's own window; a profile may not reach out
    /// unprompted inside it.
    func setQuietHours(interactorId: String, start: Int?, end: Int?,
                       token: String) async throws -> QuietHoursOut {
        var body: [String: Any] = [:]
        if let start { body["quiet_start"] = start }
        if let end { body["quiet_end"] = end }
        return try await request(
            "/interactors/\(interactorId)/quiet-hours", method: "PUT",
            body: body, token: token)
    }

    /// A rating, from the person who is rating — never in somebody
    /// else's name.
    func giveFeedback(id: String, interactorId: String, rating: String,
                      token: String) async throws -> FeedbackOut {
        try await request(
            "/profiles/\(id)/interactions/\(interactorId)/feedback",
            method: "POST", body: ["rating": rating], token: token)
    }

    func myReferrals(interactorId: String,
                     token: String) async throws -> [ReferralRow] {
        try await request("/interactors/\(interactorId)/referrals",
                          token: token)
    }

    // -- the license --

    func acquireLicense(id: String,
                        token: String) async throws -> LicenseGrantOut {
        try await request("/profiles/\(id)/license/acquire",
                          method: "POST", body: [:], token: token)
    }

    /// The buyer derives their own specialist agent from the licensed
    /// expertise; its origin is recorded.
    func deriveAgent(id: String, grantId: String,
                     token: String) async throws -> GenesisOut {
        try await request("/profiles/\(id)/license/\(grantId)/derive",
                          method: "POST", body: [:], token: token)
    }

    // -- the senses --

    /// Hands-free guidance from what the camera recognises.
    func perceive(id: String, objects: [String], goal: String,
                  token: String) async throws -> PerceiveOut {
        var body: [String: Any] = ["objects": objects]
        if !goal.isEmpty { body["goal"] = goal }
        return try await request("/profiles/\(id)/perceive",
                                 method: "POST", body: body, token: token)
    }

    func microphonePlaces() async throws -> MicPlacesOut {
        try await request("/microphones/places")
    }

    func microphoneVocabulary() async throws -> MicVocabularyOut {
        try await request("/microphones/vocabulary")
    }

    func overlaysCatalogue() async throws -> OverlayCatalogue {
        try await request("/overlays/catalogue")
    }

    /// The whole experience list, replaced wholesale — a CV is a
    /// statement, not a set of rows to patch one at a time.
    func setExperience(id: String, entries: [[String: Any]],
                       token: String) async throws -> ExperienceOut {
        try await request("/profiles/\(id)/experience", method: "PUT",
                          body: ["entries": entries], token: token)
    }
}

struct MemoryRow: Decodable, Identifiable {
    let interactor_id: String
    let interactor_name: String
    let turns: Int
    var id: String { interactor_id }
}

struct MemoryTurn: Decodable, Identifiable {
    let id: String
    let role: String
    let content: String
    // A rewritten turn says so; absent on older servers.
    let edited: Bool?
}

struct ThreadOut: Decodable {
    struct Turn: Decodable { let role: String?; let content: String? }
    let messages: [Turn]
}

struct EngagementCard: Decodable {
    let sessions: Int?
    let score: Double?
}

struct ClinicalNote: Decodable {
    let note: String?
    let clinician: String?
}

struct EmbeddingCard: Decodable {
    let profile_id: String?
    let interactor_id: String?
}

struct SourceRow: Decodable, Identifiable {
    let id: String
    let kind: String
    let title: String?
    let vaulted: Bool?
}

struct TransparencyCard: Decodable {
    let active_relationships: Int
    let model_effective: String?
    let policy: String
}

struct ExportOut: Decodable {
    struct Msg: Decodable {}
    let messages: [Msg]
    let posts: [Msg]
    let sources: [Msg]
}

struct StatsCard: Decodable {
    let sessions: Int
    let memory_entries: Int
    let interactors: Int
    let sources: Int
}

struct FeedOut: Decodable {
    struct Entry: Decodable {}
    let posts: [Entry]
    let ranked_on: [String]
    let never_ranked_on: [String]
}

struct VeilCard: Decodable {
    let anonymous: Bool?
    let withheld: [String]?
    let not_withheld: [String]?
}

struct VerificationCard: Decodable {
    let verified: Bool?
    let level: String?
    let attestor: String?
    let means: String?
}

struct VerifiableOut: Decodable {
    let can_verify: Bool
    let reason: String?
}

struct ProfilePatched: Decodable {
    let id: String
    let display_name: String?
}

struct SunsetOut: Decodable {
    let status: String?
    let farewells: Int?
}

struct MemorialCard: Decodable {
    let display_name: String?
    let purpose: String?
    let relationships_touched: Int?
}

struct RosterOut: Decodable {
    struct Sibling: Decodable {
        let id: String
        let display_name: String?
        let anonymous: Bool?
    }
    let profiles: [Sibling]?
}

struct SucceedOut: Decodable {
    let succeeded: Bool
    let memorial: Bool?
}

struct AvatarLikeness: Decodable {
    let real_person: Bool?
    let basis: String?
    let attestor: String?
    let note: String?
}

struct AvatarCard: Decodable {
    let asset: String?
    let asset_marked: Bool?
    let placeholder: Bool?
    let likeness: AvatarLikeness?
}

struct BriefCatalog: Decodable {
    struct Brief: Decodable { let handle: String? }
    let style: String?
    let briefs: [Brief]?
}

struct BriefCard: Decodable {
    let handle: String?
    let brief: String?
}

struct EmblemCatalog: Decodable {
    struct Emblem: Decodable { let emblem: String?; let field: String? }
    let emblems: [Emblem]?
    let note: String?
}

struct IdentityVocabulary: Decodable {
    let withheld_when_anonymous: [String]
    let never_withheld: [String]
}

struct EmblemOut: Decodable {
    let emblem: String?
    let note: String?
}

struct BadgeCard: Decodable {
    let verified: Bool?
    let level: String?
    let attestor: String?
}

struct ThemeCatalog: Decodable {
    struct Theme: Decodable { let id: String?; let label: String? }
    let themes: [Theme]?
    let layouts: [String]?
}

// The theme is a card of its own — an id, a label and the colours — not the
// id on its own.
struct PageTheme: Decodable {
    let id: String?
    let label: String?
}

struct PageCard: Decodable {
    let theme: PageTheme?
    let tagline: String?
    let about: String?
}

struct FrontCard: Decodable {
    let display_name: String?
    let headline: String?
    let ai_disclosure: String?
}

struct SurfacesCard: Decodable {
    let surfaces: [String]
}

struct CompositionCard: Decodable {
    struct Source: Decodable { let name: String?; let share: Double? }
    let sources: [Source]?
    let policy: String
}

struct EmbodimentRow: Decodable {
    let name: String
    let kind: String
    let has_llm: Bool?
}

struct ConsistencyCard: Decodable {
    struct Form: Decodable { let name: String?; let kind: String? }
    let embodiments: [Form]?
    let surfaces: [String]?
}

struct ProfileDisplayRow: Decodable, Identifiable {
    let id: String
    let kind: String?
    let label: String?
}

struct ProfileDisplayList: Decodable {
    let displays: [ProfileDisplayRow]
}

struct SteeringCard: Decodable {
    struct Dial: Decodable { let name: String?; let group: String? }
    let dials: [Dial]?
    let values: [String: Int]
    let adult_mode: Bool?
}

struct WatchFace: Decodable {
    struct Chip: Decodable {
        let display_name: String?
        let light: String?
        let pending_approvals: Int?
    }
    struct Agent: Decodable {
        let id: String
        let goal: String?
        let light: String?
    }
    struct Summary: Decodable {
        let working: Int
        let needing_assistance: Int
        let stopped: Int
    }
    let profile: Chip
    let agents: [Agent]
    let summary: Summary
    let haptic: String?
}

struct WatchActOut: Decodable {
    let status: String?
}

struct SignupOut: Decodable {
    let account_id: String?
    let email: String?
    let verified: Bool?
    let code_delivery: String?
}

struct SessionOut: Decodable {
    let account_id: String?
    let email: String?
    let display_name: String?
    let account_token: String?
}

struct CodeDelivery: Decodable {
    let email: String?
    let code_delivery: String?
}

struct ResetOut: Decodable {
    let email: String?
    let reset: Bool?
}

struct OAuthProviderList: Decodable {
    struct Door: Decodable {
        let provider: String
        let name: String?
        let configured: Bool?
    }
    let providers: [Door]
}

struct OAuthStartOut: Decodable {
    let provider: String?
    let state: String?
    // The provider's authorize endpoint. Named `url` on the
    // wire; a shell that reads `authorize_url` gets nil and opens nothing.
    let url: String?
}

struct OAuthClaimOut: Decodable {
    let ready: Bool?
    let account_id: String?
    let email: String?
    let account_token: String?
}

struct PlanCatalog: Decodable {
    struct Plan: Decodable {
        let plan: String
        let title: String?
        let price_usd: Double?
        let period: String?
        let means: String?
    }
    let plans: [Plan]
    let billing: String?
}

struct SubscriptionRow: Decodable, Identifiable {
    let id: String
    let subject_kind: String?
    let subject_id: String?
    let tier: String?
    let price: Double?
    let status: String?
    let periods: Int?
    let billing: String?
}

struct SubscriptionList: Decodable {
    let subscriptions: [SubscriptionRow]
}

struct OrderRow: Decodable, Identifiable {
    let id: String
    let listing_id: String?
    let price: Double?
    let status: String?
    let created_at: String?
}

struct OrderList: Decodable {
    let orders: [OrderRow]
}

struct ProceedsCard: Decodable {
    struct Designee: Decodable {
        let name: String
        let kind: String?
        let share: Int?
    }
    let profile_id: String?
    let proceeds_to: [Designee]
}

struct CampaignRow: Decodable, Identifiable {
    let id: String
    let title: String?
    let cause: String?
    let goal: Double?
    let raised: Double?
    let donors: Int?
    let status: String?
}

struct CloudStatusCard: Decodable {
    let cloud: Bool
    let fallback: String?
    let contribution: String?
}

struct OfflineStatusCard: Decodable {
    let offline: Bool?
    let provider: String?
    let cloud_attached: Bool?
    let external_transmission_possible: Bool?
    let data_locality: String?
}

struct LightsLegend: Decodable {
    struct Row: Decodable {
        let light: String
        let labels: [String]?
        let statuses: [String]?
    }
    let order: [String]
    let legend: [Row]
    let question: String?
}

struct HelpTopicList: Decodable {
    let topics: [String]
    let disclosure: String?
}

struct HelpAnswer: Decodable {
    let answer: String
    let source: String?
    let ai: Bool?
    let refused: Bool?
}

struct LocalProviderRow: Decodable, Identifiable {
    let id: String
    let name: String?
    let area: String?
    let location: String?
    let contact: String?
    let business: Bool?
}

struct BeaconOverlayCard: Decodable {
    let profile_id: String?
    let display_name: String?
    let watermark: String?
    let age_wall: Bool?
    let rated: Bool?
    let note: String?
}

/// A page of the stream. `rules` is the server saying, in words a screen can
/// show, what it will and will not play without being asked.
struct FeedPage: Decodable {
    let items: [FeedCard]
    let cursor: String?
}

/// One card. `plays` is the server's and is never recomputed here: only
/// footage this deployment holds comes back true, so scrolling past an
/// off-site card makes no request to anybody else — see `qrme/feed.py`.
struct FeedCard: Decodable {
    let id: String
    let kind: String
    let reason: String?
    let title: String?
    let note: String?
    let plays: Bool?
    let loop: Bool?
    let src: String?
    let facade: FeedFacade?
    let topic: String?
    let channel: String?
    let people: Int?
    let entering: String?
    let display_name: String?
    let trade: String?
    let presence: String?
    let blurb: String?
    let ringing: String?
    let human: Bool?
    let ai: Bool?
    // party — a watch party whose host chose to be found. Counts and a
    // facade only; joining is the viewer's own press.
    let video: FeedFacade?
    let joining: String?
    let profiles: Int?
}

struct FeedFacade: Decodable {
    let platform_name: String?
    let url: String?
}

struct DeskScanCard: Decodable {
    let desk_id: String?
    let display_name: String?
    let trade: String?
    let age_wall: Bool?
}

struct SocialBeaconCard: Decodable {
    let connection: String
    let platform: String?
    let handle: String?
    let presence_url: String?
    let qr_svg: String?
}

struct PairCard: Decodable {
    let console_url: String?
    let console_built: Bool?
    let reachable: Bool?
    let how: [String]?
}

struct HeldMessage: Decodable, Identifiable {
    let id: String
    let interactor_id: String?
    let content: String?
    let status: String?
    let created_at: String?
}

struct ModerationOut: Decodable {
    let id: String?
    let status: String?
}

struct ReviewBoard: Decodable {
    struct Rating: Decodable {
        let average: Double?
        let count: Int?
    }
    struct Row: Decodable {
        let interactor_id: String?
        let rating: Int?
        let body: String?
    }
    let profile_id: String?
    let rating: Rating?
    let reviews: [Row]
}

struct ReviewOut: Decodable {
    let interactor_id: String?
    let rating: Int?
}

struct WatermarkCredential: Decodable {
    let watermark_id: String?
    let profile_id: String?
    let kind: String?
    let valid: Bool?
    let content_match: Bool?
    let issued_at: String?
}

// One limit per kind of media, not one limit and a list of kinds: video is
// allowed sixty megabytes where an image gets eight.
struct MediaLimit: Decodable {
    let max_bytes: Int?
    let types: [String]?
}

struct MediaLimits: Decodable {
    let image: MediaLimit?
    let video: MediaLimit?
    let file: MediaLimit?
    let note: String?
}

struct MediaOut: Decodable {
    let id: String?
    let kind: String?
    let ai_marked: Bool?
}

struct VideoPlatformBoard: Decodable {
    let platforms: [String]?
    let note: String?
}

struct WearableRow: Decodable {
    let name: String?
    let kind: String?
    let faces: [String]?
    let revoked: Bool?
}

struct WearableBoard: Decodable {
    let profile_id: String?
    let wearables: [WearableRow]
    // Maps, not lists: `faces` is face -> what it shows, `kinds_worn` is
    // kind -> where it is worn, `refusal_reasons` is kind -> why not.
    let faces: [String: String]?
    let kinds_worn: [String: String]?
    let refusal_reasons: [String: String]?
}

struct GenesisOut: Decodable {
    let id: String?
    let display_name: String?
    let kind: String?
    let owner_token: String?
}

struct PackOut: Decodable {
    let id: String?
    let title: String?
    let industry: String?
}

struct PackSeedOut: Decodable {
    let created: Int?
    let packs: Int?
}

struct SimulationOut: Decodable {
    let id: String?
    let scenario: String?
    let horizon: String?
    let narrative: String?
}

struct FinetuneOut: Decodable {
    let id: String?
    let interactors: Int?
    let messages_processed: Int?
    let external_transmission: Bool?
    let computed: String?
}

struct ContributionView: Decodable {
    let opted_in: Bool?
    let contributed: [ContributionRow]?
}

struct ContributionRow: Decodable {
    let ref: String?
    let revoked: Bool?
}

struct RevokeOut: Decodable {
    let revoked_count: Int?
    let deleted_at_gateway: Bool?
}

struct ExcursionOut: Decodable {
    let id: String?
    let topic: String?
    let status: String?
    let findings: String?
}

struct CheckinOut: Decodable {
    let message: String?
    let reason: String?
}

struct QuietHoursOut: Decodable {
    let id: String?
    let quiet_start: Int?
    let quiet_end: Int?
}

struct FeedbackOut: Decodable {
    let rating: String?
    let engagement: Double?
}

struct ReferralRow: Decodable {
    let id: String?
    let provider_id: String?
    let released: Bool?
    // A timestamp, not a flag: the row says *when* it was
    // read, and `nil` is the not-yet.
    let opened_at: String?
}

struct LicenseGrantOut: Decodable {
    let id: String?
    let profile_id: String?
    let buyer_id: String?
    let price: Double?
}

struct PerceiveOut: Decodable {
    let guidance: String?
    let watermark: WatermarkBrief?
    struct WatermarkBrief: Decodable { let line: String? }
}

struct MicPlace: Decodable {
    let surface: String?
    let why: String?
}

struct MicPlacesOut: Decodable {
    let places: [MicPlace]?
}

struct RefusedKind: Decodable {
    let kind: String?
    let why: String?
}

struct MicVocabularyOut: Decodable {
    let personal: [String]?
    let refusals: [RefusedKind]?
    let rules: [String]?
}

struct OverlayKind: Decodable {
    let kind: String?
    let covers_face: Bool?
    let means: String?
}

struct OverlayCatalogue: Decodable {
    let kinds: [OverlayKind]?
    let refusals: [RefusedKind]?
    let rules: [String]?
}

struct ExperienceOut: Decodable {
    struct Entry: Decodable {
        let title: String?
        let org: String?
        let period: String?
    }
    let profile_id: String?
    let experience: [Entry]
}
