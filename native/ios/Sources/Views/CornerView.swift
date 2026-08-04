import SwiftUI

/// Your corner, in the pocket: the homepage sandbox, friends-only
/// messages, and the switches that govern both. Strings go through L10n
/// so the English count behind this shell's tabs does not grow; refusal
/// sentences arrive from the server in the reader's language and are
/// shown verbatim — including the ones that name a switch.
struct CornerSection: View {
    @EnvironmentObject var state: AppState
    @State private var flags: [String: Bool] = [:]
    @State private var headline = ""
    @State private var about = ""
    @State private var bg = "#1a1333"
    @State private var accent = "#7b5cff"
    @State private var threads: [DmThreadRow] = []
    @State private var withId = ""
    @State private var thread: [DmMessageRow] = []
    @State private var draft = ""
    @State private var note: String?
    @State private var busy = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                VStack(alignment: .leading, spacing: 8) {
                    Text(L10n.t("corner.title", state.language))
                        .font(.headline).foregroundStyle(Theme.txt)
                    Text(L10n.t("corner.walls", state.language))
                        .font(.caption2).foregroundStyle(Theme.t2)
                    TextField(L10n.t("corner.headline", state.language),
                              text: $headline)
                        .textFieldStyle(.roundedBorder)
                    TextField(L10n.t("corner.about", state.language),
                              text: $about)
                        .textFieldStyle(.roundedBorder)
                    TextField(L10n.t("corner.bg", state.language), text: $bg)
                        .textFieldStyle(.roundedBorder)
                    TextField(L10n.t("corner.accent", state.language),
                              text: $accent)
                        .textFieldStyle(.roundedBorder)
                    Button(L10n.t("corner.save", state.language)) { save() }
                        .disabled(busy || state.pid == nil)
                }.card()

                VStack(alignment: .leading, spacing: 8) {
                    Text(L10n.t("corner.switches", state.language))
                        .font(.subheadline.bold()).foregroundStyle(Theme.txt)
                    ForEach(flags.keys.sorted(), id: \.self) { feature in
                        Toggle(isOn: Binding(
                            get: { flags[feature] ?? true },
                            set: { on in flip(feature, on) })) {
                            Text(L10n.t("corner.switch.\(feature)",
                                        state.language))
                                .font(.caption).foregroundStyle(Theme.t2)
                        }.disabled(busy)
                    }
                }.card()

                VStack(alignment: .leading, spacing: 8) {
                    Text(L10n.t("corner.messages", state.language))
                        .font(.subheadline.bold()).foregroundStyle(Theme.txt)
                    Text(L10n.t("corner.friends_only", state.language))
                        .font(.caption2).foregroundStyle(Theme.t2)
                    ForEach(threads) { t in
                        HStack {
                            Text(t.other_name ?? t.other_id).font(.caption)
                                .foregroundStyle(Theme.txt)
                            Spacer()
                            Button(L10n.t("corner.open", state.language)) {
                                open(t.other_id)
                            }.font(.caption2)
                        }
                    }
                    TextField(L10n.t("corner.to", state.language),
                              text: $withId)
                        .textFieldStyle(.roundedBorder)
                    ForEach(thread) { m in
                        let line = (m.sender_id == state.pid ? "→ " : "← ")
                            + m.body
                        Text(line).font(.caption2).foregroundStyle(Theme.t2)
                    }
                    HStack {
                        TextField("", text: $draft)
                            .textFieldStyle(.roundedBorder)
                        Button(L10n.t("corner.send", state.language)) {
                            send()
                        }.disabled(busy || draft.isEmpty || withId.isEmpty)
                    }
                }.card()

                if let note {
                    Text(note).font(.caption).foregroundStyle(Theme.t2)
                }
            }.padding(20)
        }
        .task { await load() }
    }

    private func load() async {
        guard let pid = state.pid, let token = state.token else { return }
        if let page = try? await ApiClient.shared.homepage(
                profileId: pid, token: token) {
            headline = page.headline; about = page.about
            bg = page.theme.bg; accent = page.theme.accent
        }
        flags = (try? await ApiClient.shared.features(profileId: pid,
                                                      token: token)) ?? [:]
        threads = (try? await ApiClient.shared.dmThreads(
            profileId: pid, token: token)) ?? []
    }

    private func run(_ op: @escaping () async throws -> Void) {
        busy = true; note = nil
        Task {
            do { try await op() } catch { note = error.localizedDescription }
            busy = false
        }
    }

    private func save() {
        run {
            _ = try await ApiClient.shared.editHomepage(
                profileId: state.pid!, headline: headline, about: about,
                bg: bg, accent: accent, token: state.token!)
        }
    }

    private func flip(_ feature: String, _ on: Bool) {
        run {
            flags = try await ApiClient.shared.setFeature(
                profileId: state.pid!, feature: feature, enabled: on,
                token: state.token!)
        }
    }

    private func open(_ other: String) {
        withId = other
        run {
            thread = try await ApiClient.shared.dmThread(
                profileId: state.pid!, withId: other, token: state.token!)
        }
    }

    private func send() {
        run {
            _ = try await ApiClient.shared.sendDm(
                profileId: state.pid!, to: withId, body: draft,
                token: state.token!)
            draft = ""
            thread = try await ApiClient.shared.dmThread(
                profileId: state.pid!, withId: withId, token: state.token!)
            threads = try await ApiClient.shared.dmThreads(
                profileId: state.pid!, token: state.token!)
        }
    }
}
