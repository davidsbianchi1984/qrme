import SwiftUI

@main
struct QrmeApp: App {
    @StateObject private var state = AppState()

    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(state)
                .preferredColorScheme(.dark)
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
