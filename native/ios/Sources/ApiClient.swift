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
}

struct Health: Decodable { let status: String }

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

struct InteractorCreated: Decodable { let id: String }

struct ChatMessage: Decodable {
    let id: String
    let role: String
    let content: String?
    let status: String
    let flag_reason: String?
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
        if let token { req.setValue("Bearer \(token)", forHTTPHeaderField: "authorization") }
        if let body { req.httpBody = try JSONSerialization.data(withJSONObject: body) }

        let (data, resp) = try await URLSession.shared.data(for: req)
        guard let http = resp as? HTTPURLResponse else { throw ApiError.http("No response") }
        guard (200..<300).contains(http.statusCode) else {
            let detail = (try? JSONSerialization.jsonObject(with: data) as? [String: Any])?["detail"] as? String
            throw ApiError.http(detail ?? "HTTP \(http.statusCode)")
        }
        return try JSONDecoder().decode(T.self, from: data)
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

    func createInteractor(name: String) async throws -> InteractorCreated {
        try await request("/interactors", method: "POST",
                          body: ["display_name": name])
    }

    func chat(id: String, token: String, interactorId: String,
              message: String) async throws -> ChatReply {
        try await request("/profiles/\(id)/chat", method: "POST",
                          body: ["interactor_id": interactorId,
                                 "message": message], token: token)
    }

    // MARK: Community — stranger connections & multiparty rooms

    func joinQueue(interactorId: String, alias: String?) async throws -> ConnJoin {
        var body: [String: Any] = ["interactor_id": interactorId, "tier": "friendly"]
        if let alias, !alias.isEmpty { body["alias"] = alias }
        return try await request("/connections/join", method: "POST", body: body)
    }

    func connectionMessages(cid: String, interactorId: String) async throws -> [ConnMsg] {
        try await request("/connections/\(cid)/messages",
                          query: ["interactor_id": interactorId])
    }

    func sendConnectionMessage(cid: String, interactorId: String,
                               message: String) async throws -> ConnMsgResult {
        try await request("/connections/\(cid)/messages", method: "POST",
                          body: ["interactor_id": interactorId, "message": message])
    }

    func endConnection(cid: String, interactorId: String) async throws {
        struct Ok: Decodable {}
        let _: Ok = try await request("/connections/\(cid)/end", method: "POST",
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

    func roomMessage(roomId: String, senderId: String,
                     message: String) async throws -> RoomPost {
        try await request("/rooms/\(roomId)/messages", method: "POST",
                          body: ["sender_id": senderId, "message": message])
    }

    func roomAdvance(roomId: String) async throws -> RoomAdvance {
        try await request("/rooms/\(roomId)/advance", method: "POST")
    }

    func roomTranscript(roomId: String) async throws -> [RoomMsg] {
        try await request("/rooms/\(roomId)/messages")
    }

    // MARK: Reach — summon (@handle + beacons), marketplace, licensing

    func claimHandle(id: String, handle: String) async throws -> HandleClaim {
        try await request("/profiles/\(id)/handle", method: "PUT",
                          body: ["handle": handle])
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
}
