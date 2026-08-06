import SwiftUI

/// Gaming: this profile plays alongside real players — a companion, teammate,
/// or practice partner on a console/PC platform, agent-operated. Its comms
/// are generated in character and moderated; fair play is enforced, not a
/// toggle.
struct GamingSection: View {
    @EnvironmentObject var state: AppState
    @State private var platform = "xbox"
    @State private var game = ""
    @State private var role = "teammate"
    @State private var sessions: [GameSession] = []
    @State private var openSession: String?
    @State private var situation = ""
    @State private var minorPresent = false
    @State private var lastLine: GameCalloutResult?
    @State private var error: String?

    private let platforms = ["playstation", "xbox", "nintendo", "steam", "pc"]
    private let roles = ["companion", "teammate", "practice_partner"]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                VStack(alignment: .leading, spacing: 10) {
                    Text(L10n.t("ngam", state.language)).font(.headline).foregroundStyle(Theme.txt)
                    Text(L10n.t("ngam.sub.full", state.language))
                        .font(.caption).foregroundStyle(Theme.t2)
                    Picker(L10n.t("ngam.platform", state.language), selection: $platform) {
                        ForEach(platforms, id: \.self) { Text($0.capitalized).tag($0) }
                    }.pickerStyle(.menu).tint(Theme.brandA)
                    Picker(L10n.t("ngam.role", state.language), selection: $role) {
                        ForEach(roles, id: \.self) {
                            Text($0.replacingOccurrences(of: "_", with: " ")).tag($0)
                        }
                    }.pickerStyle(.menu).tint(Theme.brandA)
                    TextField(L10n.t("ngam.game", state.language), text: $game)
                        .foregroundStyle(Theme.txt)
                        .padding(10).background(Theme.scrBot)
                        .clipShape(RoundedRectangle(cornerRadius: 11))
                        .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                    Button(L10n.t("ngam.start", state.language)) { start() }
                        .font(.caption.bold()).foregroundStyle(.white)
                        .padding(.horizontal, 12).padding(.vertical, 10)
                        .background(Theme.brandA).clipShape(Capsule())
                        .disabled(game.isEmpty)
                }.card()

                if let error { Text(error).font(.footnote).foregroundStyle(Theme.red) }

                ForEach(sessions, id: \.id) { s in
                    VStack(alignment: .leading, spacing: 6) {
                        HStack {
                            Text("\(s.game) · \(s.platform_label ?? s.platform)")
                                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
                            Spacer()
                            Text(s.status.uppercased()).font(.caption2.bold())
                                .foregroundStyle(s.status == "active" ? Theme.green : Theme.t3)
                        }
                        Text(L10n.fill("ngam.session", state.language,
                             ["role": s.role.replacingOccurrences(of: "_", with: " "),
                              "n": "\(s.callouts ?? 0)"]))
                            .font(.caption2).foregroundStyle(Theme.t2)
                        if s.status == "active" {
                            if openSession == s.id {
                                TextField(L10n.t("ngam.situation.ph", state.language), text: $situation)
                                    .foregroundStyle(Theme.txt)
                                    .padding(8).background(Theme.scrBot)
                                    .clipShape(RoundedRectangle(cornerRadius: 9))
                                Toggle(L10n.t("ngam.minor", state.language), isOn: $minorPresent)
                                    .font(.caption).foregroundStyle(Theme.t2).tint(Theme.amber)
                                HStack {
                                    Button(L10n.t("ngam.callit", state.language)) { callout(s) }
                                        .font(.caption.bold()).foregroundStyle(.white)
                                        .padding(.horizontal, 12).padding(.vertical, 8)
                                        .background(Theme.brandA).clipShape(Capsule())
                                    Button(L10n.t("ngam.end", state.language)) { end(s) }
                                        .font(.caption).foregroundStyle(Theme.red)
                                }
                                if let l = lastLine {
                                    if l.status == "spoken", let line = l.line {
                                        Text("🎙 \(line)").font(.caption).foregroundStyle(Theme.green)
                                    } else {
                                        Text(L10n.fill("ngam.held", state.language,
                                              ["reason": l.flag_reason
                                                  ?? L10n.t("ngam.held.default", state.language)]))
                                            .font(.caption2).foregroundStyle(Theme.amber)
                                    }
                                }
                            } else {
                                Button(L10n.t("nmg.open", state.language)) { openSession = s.id; lastLine = nil }
                                    .font(.caption.bold()).foregroundStyle(Theme.brandA)
                            }
                        }
                    }.card()
                }
            }.padding(20)
        }
        .task { await load() }
    }

    private func load() async {
        guard let pid = state.pid, let token = state.token else { return }
        sessions = (try? await ApiClient.shared.gameSessions(pid: pid, token: token)) ?? []
    }

    private func start() {
        guard let pid = state.pid, let token = state.token else { return }
        error = nil
        Task {
            do {
                _ = try await ApiClient.shared.startGameSession(
                    pid: pid, token: token, platform: platform, game: game, role: role)
                game = ""
            } catch { self.error = error.localizedDescription }
            await load()
        }
    }

    private func callout(_ s: GameSession) {
        guard let token = state.token, !situation.isEmpty else { return }
        Task {
            lastLine = try? await ApiClient.shared.gameCallout(
                sid: s.id, token: token, situation: situation,
                minorPresent: minorPresent)
            await load()
        }
    }

    private func end(_ s: GameSession) {
        guard let token = state.token else { return }
        Task {
            try? await ApiClient.shared.endGameSession(sid: s.id, token: token)
            openSession = nil
            await load()
        }
    }
}
