import SwiftUI

@main
struct QrmeApp: App {
    @StateObject private var state = AppState()

    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(state)
                .preferredColorScheme(.dark)
                // What the buffer is for. Detached and unawaited: a
                // diagnostic must never be the reason a launch is slow, and
                // `send` returns an outcome rather than throwing, so there is
                // nothing here to handle. It answers `.awaitingNotice` until
                // somebody has been told and chosen.
                .task { await Problems.send() }
        }
    }
}

/// Switches between the create-profile flow and the signed-in tab bar.
struct RootView: View {
    @EnvironmentObject var state: AppState

    var body: some View {
        ZStack {
            Theme.bg.ignoresSafeArea()
            if state.isSignedIn {
                TabView {
                    OverviewView().tabItem { Label(L10n.t("tab.overview", state.language), systemImage: "circle.grid.cross") }
                    ChatHubView().tabItem { Label(L10n.t("tab.chat", state.language), systemImage: "bubble.left.and.bubble.right") }
                    StudioView().tabItem { Label(L10n.t("tab.studio", state.language), systemImage: "square.and.pencil") }
                    ConnectView().tabItem { Label(L10n.t("tab.connect", state.language), systemImage: "link") }
                    ManageView().tabItem { Label(L10n.t("tab.manage", state.language), systemImage: "gearshape") }
                }
                .tint(Theme.brandA)
            } else {
                WelcomeView()
            }
        }
    }
}
