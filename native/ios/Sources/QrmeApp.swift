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
                    ComposeView().tabItem { Label("Compose", systemImage: "square.and.pencil") }
                    PostsView().tabItem { Label("Posts", systemImage: "text.bubble") }
                    RobotsView().tabItem { Label("Robots", systemImage: "figure.walk.motion") }
                    SettingsView().tabItem { Label("Settings", systemImage: "gearshape") }
                }
                .tint(Theme.brandA)
            } else {
                WelcomeView()
            }
        }
    }
}
