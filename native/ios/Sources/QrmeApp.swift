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
                    OverviewView().tabItem { Label("Overview", systemImage: "circle.grid.cross") }
                    ChatHubView().tabItem { Label("Chat", systemImage: "bubble.left.and.bubble.right") }
                    StudioView().tabItem { Label("Studio", systemImage: "square.and.pencil") }
                    ConnectView().tabItem { Label("Connect", systemImage: "link") }
                    ManageView().tabItem { Label("Manage", systemImage: "gearshape") }
                }
                .tint(Theme.brandA)
            } else {
                WelcomeView()
            }
        }
    }
}
