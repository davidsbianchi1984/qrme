import SwiftUI

/// Home: the profile's public card (GET /profiles/{id}) and a sign-out.
struct OverviewView: View {
    @EnvironmentObject var state: AppState
    @State private var card: ProfileCard?
    @State private var loading = true

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                HStack(spacing: 8) {
                    Circle().fill(Theme.green).frame(width: 8, height: 8)
                    Text(L10n.t("nov.live", state.language)).font(.caption.bold()).foregroundStyle(Theme.green)
                }
                Text(state.displayName).font(.title.bold()).foregroundStyle(Theme.txt)
                Text(L10n.t("nov.sub", state.language))
                    .font(.subheadline).foregroundStyle(Theme.t2)

                VStack(alignment: .leading, spacing: 10) {
                    Text(L10n.t("nov", state.language)).font(.headline).foregroundStyle(Theme.txt)
                    if loading {
                        ProgressView().tint(Theme.brandA)
                    } else if let c = card {
                        row("Kind", c.kind.replacingOccurrences(of: "_", with: " ").capitalized)
                        row("Status", (c.status ?? "active").capitalized)
                        row("ID", c.id)
                    } else {
                        Text(L10n.t("nov.error", state.language))
                            .font(.footnote).foregroundStyle(Theme.t2)
                    }
                }.card()

                Button(L10n.t("action.sign_out", state.language)) { state.signOut() }
                    .font(.subheadline).foregroundStyle(Theme.t2)
                    .frame(maxWidth: .infinity).padding(.vertical, 12)
                    .overlay(RoundedRectangle(cornerRadius: 12).stroke(Theme.line, lineWidth: 1))
            }.padding(20)
        }
        .refreshable { await load() }
        .task { await load() }
    }

    private func row(_ k: String, _ v: String) -> some View {
        HStack {
            Text(k).foregroundStyle(Theme.txt)
            Spacer()
            Text(v).foregroundStyle(Theme.t2).monospacedDigit()
        }.font(.subheadline)
    }

    private func load() async {
        guard let pid = state.pid else { return }
        loading = true
        card = try? await ApiClient.shared.profile(pid)
        loading = false
    }
}
