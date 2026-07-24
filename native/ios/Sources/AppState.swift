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
    @Published var interactorVerified = false

    private let d = UserDefaults.standard

    init() {
        pid = d.string(forKey: "qrme.pid")
        token = d.string(forKey: "qrme.token")
        displayName = d.string(forKey: "qrme.name") ?? ""
        interactorId = d.string(forKey: "qrme.interactor")
        interactorVerified = d.bool(forKey: "qrme.interactor.adult")
    }

    func rememberInteractor(_ id: String, adult: Bool = false) {
        interactorId = id
        interactorVerified = adult
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
        interactorId = nil; interactorVerified = false
        ["qrme.pid", "qrme.token", "qrme.name",
         "qrme.interactor", "qrme.interactor.adult"].forEach { d.removeObject(forKey: $0) }
    }
}
