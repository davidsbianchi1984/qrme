import SwiftUI

/// Holds the created profile id + owner token, persisted to UserDefaults so the
/// app resumes signed-in. Drives the root switch between Welcome and the tab bar.
@MainActor
final class AppState: ObservableObject {
    @Published var pid: String?
    @Published var token: String?
    @Published var displayName: String = ""
    // The device owner's interactor identity for the Chat screen, created
    // lazily on first send and reused across launches.
    @Published var interactorId: String?

    private let d = UserDefaults.standard

    init() {
        pid = d.string(forKey: "qrme.pid")
        token = d.string(forKey: "qrme.token")
        displayName = d.string(forKey: "qrme.name") ?? ""
        interactorId = d.string(forKey: "qrme.interactor")
    }

    func rememberInteractor(_ id: String) {
        interactorId = id
        d.set(id, forKey: "qrme.interactor")
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
        interactorId = nil
        ["qrme.pid", "qrme.token", "qrme.name",
         "qrme.interactor"].forEach { d.removeObject(forKey: $0) }
    }
}
