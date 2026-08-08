import SwiftUI

/// Holds the created profile id + owner token, persisted to UserDefaults so the
/// app resumes signed-in. Drives the root switch between Welcome and the tab bar.
@MainActor
final class AppState: ObservableObject {
    @Published var pid: String?
    @Published var token: String?
    @Published var displayName: String = ""
    // The device owner's interactor identity for the Chat screen, created
    // lazily on first send and reused across launches. `interactorVerified`
    // is true when the identity was minted with an 18+ birthdate — the key
    // that opens the rated stranger tier.
    @Published var interactorId: String?
    // The bearer token for that identity. Needed because every age-gated
    // surface checks the *token's* verified birthdate server-side — an id
    // alone opens nothing, which is the point.
    @Published var interactorToken: String?
    @Published var interactorVerified = false
    // The profile's chosen language also drives the app chrome (tab names,
    // common actions) through L10n.
    @Published var language = "en"


    /// The person's own model key, held on this device only and sent per
    /// request as `x-llm-api-key`.
    ///
    /// The console has offered this since 0.4.3 and the phones never did — so
    /// somebody who set their key in the console had it used there and the
    /// deployment's key used here, on the same profile, with nothing saying
    /// so. Never in the account and never on the wire except as the header.
    @Published var llmKey = ""

    private let d = UserDefaults.standard

    init() {
        pid = d.string(forKey: "qrme.pid")
        token = d.string(forKey: "qrme.token")
        displayName = d.string(forKey: "qrme.name") ?? ""
        interactorId = d.string(forKey: "qrme.interactor")
        interactorToken = d.string(forKey: "qrme.interactor.token")
        interactorVerified = d.bool(forKey: "qrme.interactor.adult")
        language = d.string(forKey: "qrme.lang") ?? "en"
        llmKey = d.string(forKey: "qrme.llmKey") ?? ""
        let held = llmKey
        Task { await ApiClient.shared.useLlmKey(held) }
    }

    /// Store or clear it. An empty string is the clear: there is no flag to
    /// leave switched on by mistake, and no key means the deployment's.
    func rememberLlmKey(_ key: String) {
        let trimmed = key.trimmingCharacters(in: .whitespacesAndNewlines)
        llmKey = trimmed
        if trimmed.isEmpty { d.removeObject(forKey: "qrme.llmKey") }
        else { d.set(trimmed, forKey: "qrme.llmKey") }
        Task { await ApiClient.shared.useLlmKey(trimmed) }
    }

    func rememberLanguage(_ code: String) {
        language = code
        d.set(code, forKey: "qrme.lang")
    }

    func rememberInteractor(_ id: String, token: String? = nil,
                            adult: Bool = false) {
        interactorId = id
        interactorVerified = adult
        if let token {
            interactorToken = token
            d.set(token, forKey: "qrme.interactor.token")
        }
        d.set(id, forKey: "qrme.interactor")
        d.set(adult, forKey: "qrme.interactor.adult")
    }

    var isSignedIn: Bool { pid != nil && token != nil }

    func signIn(_ r: ProfileCreated) {
        pid = r.id; token = r.owner_token; displayName = r.display_name
        d.set(r.id, forKey: "qrme.pid")
        d.set(r.owner_token, forKey: "qrme.token")
        d.set(r.display_name, forKey: "qrme.name")
    }

    func signOut() {
        pid = nil; token = nil; displayName = ""
        interactorId = nil; interactorToken = nil; interactorVerified = false
        ["qrme.pid", "qrme.token", "qrme.name", "qrme.interactor",
         "qrme.interactor.token",
         "qrme.interactor.adult"].forEach { d.removeObject(forKey: $0) }
    }
}
