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
    let content: String
    let status: String?
    let surface: String?
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

struct ChatReply: Decodable {
    let interactor_message: ChatMessage
    let profile_message: ChatMessage
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
                                       body: [String: Any]? = nil, token: String? = nil) async throws -> T {
        var req = URLRequest(url: base.appendingPathComponent(path))
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
                       birthdate: String) async throws -> ProfileCreated {
        try await request("/profiles", method: "POST", body: [
            "owner_id": "owner-1",
            "kind": kind,
            "display_name": name,
            "persona": persona,
            "demographics": ["language": "en"],
            "verification": ["birthdate": birthdate],
        ])
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
