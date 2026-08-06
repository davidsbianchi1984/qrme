import SwiftUI

/// Studio: the profile's creative surface — Compose, the Posts feed, and
/// Knowledge Excursions — grouped behind one tab so the bar stays tidy.
struct StudioView: View {
    /// Same split as `ConnectView.Tab`: raw values name the sections, the
    /// table holds the words.
    enum Tab: String, CaseIterable { case compose, posts, study }
    @EnvironmentObject var state: AppState
    @State private var tab: Tab = .compose

    var body: some View {
        VStack(spacing: 0) {
            Picker("", selection: $tab) {
                ForEach(Tab.allCases, id: \.self) { Text(L10n.t("tab.\($0.rawValue)", state.language)).tag($0) }
            }
            .pickerStyle(.segmented)
            .padding(.horizontal, 20).padding(.top, 8)

            switch tab {
            case .compose: ComposeView()
            case .posts: PostsView()
            case .study: StudyView()
            }
        }
    }
}

/// Knowledge Excursions: study a topic safely. Everything outbound is
/// sanitized (private names never leave), and the sanitized brief is shown so
/// the owner can verify exactly what could leave the host.
struct StudyView: View {
    @EnvironmentObject var state: AppState
    @State private var topic = ""
    @State private var question = ""
    @State private var excursions: [Excursion] = []
    @State private var busy = false
    @State private var error: String?

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text(L10n.t("nstu", state.language)).font(.title2.bold()).foregroundStyle(Theme.txt)
                Text(L10n.t("nstu.sub", state.language))
                    .font(.footnote).foregroundStyle(Theme.t2)

                VStack(alignment: .leading, spacing: 10) {
                    field(L10n.t("ncmp.topic", state.language)) { TextField(L10n.t("nstu.topic.ph", state.language), text: $topic)
                        .foregroundStyle(Theme.txt) }
                    field(L10n.t("nstu.question", state.language)) { TextField(L10n.t("nstu.question.ph", state.language), text: $question,
                                                  axis: .vertical)
                        .lineLimit(1...3).foregroundStyle(Theme.txt) }
                    Button(action: start) {
                        HStack { if busy { ProgressView().tint(.white) }; Text(L10n.t("nstu.go", state.language)).bold() }
                            .frame(maxWidth: .infinity).padding(.vertical, 12)
                            .background(Theme.brand).foregroundStyle(.white)
                            .clipShape(RoundedRectangle(cornerRadius: 12))
                    }.disabled(topic.isEmpty || question.isEmpty || busy)
                }.card()

                if let error { Text(error).font(.footnote).foregroundStyle(Theme.red) }

                ForEach(excursions.reversed(), id: \.id) { e in
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Text(e.topic).font(.subheadline.bold()).foregroundStyle(Theme.txt)
                            Spacer()
                            Text(e.left_host ? "left host" : "stayed local")
                                .font(.caption2.bold())
                                .padding(.horizontal, 7).padding(.vertical, 3)
                                .background((e.left_host ? Theme.amber : Theme.green).opacity(0.16))
                                .foregroundStyle(e.left_host ? Theme.amber : Theme.green)
                                .clipShape(Capsule())
                        }
                        if e.redactions > 0 {
                            Text(L10n.fill("nstu.redacted", state.language, ["n": "\(e.redactions)"]))
                                .font(.caption).foregroundStyle(Theme.t2)
                        }
                        Text(e.findings).font(.footnote).foregroundStyle(Theme.txt)
                        if e.learned {
                            Text(L10n.t("nstu.folded", state.language))
                                .font(.caption).foregroundStyle(Theme.green)
                        } else {
                            Button(L10n.t("nstu.fold", state.language)) { learn(e) }
                                .font(.caption.bold()).foregroundStyle(.white)
                                .padding(.horizontal, 12).padding(.vertical, 7)
                                .background(Theme.brandA).clipShape(Capsule())
                        }
                    }.card()
                }
            }.padding(20)
        }
        .task { await load() }
    }

    private func field<Content: View>(_ label: String, @ViewBuilder _ content: () -> Content) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(label).font(.caption).foregroundStyle(Theme.t2)
            content()
                .padding(.horizontal, 12).padding(.vertical, 10)
                .background(Theme.scrBot).clipShape(RoundedRectangle(cornerRadius: 11))
                .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
        }
    }

    private func load() async {
        guard let pid = state.pid, let token = state.token else { return }
        excursions = (try? await ApiClient.shared.excursions(id: pid, token: token)) ?? []
    }

    private func start() {
        guard let pid = state.pid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do {
                _ = try await ApiClient.shared.startExcursion(
                    id: pid, token: token, topic: topic, question: question)
                topic = ""; question = ""
            } catch { self.error = error.localizedDescription }
            await load(); busy = false
        }
    }

    private func learn(_ excursion: Excursion) {
        guard let token = state.token else { return }
        Task {
            try? await ApiClient.shared.learn(cid: excursion.id, token: token)
            await load()
        }
    }
}
