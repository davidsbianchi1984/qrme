import SwiftUI

/// Compose one in-character public post about a topic -> POST /profiles/{id}/compose.
struct ComposeView: View {
    @EnvironmentObject var state: AppState
    @State private var topic = ""
    @State private var result: Post?
    @State private var busy = false
    @State private var error: String?

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text(L10n.t("tab.compose", state.language)).font(.title2.bold()).foregroundStyle(Theme.txt)
                Text(L10n.t("ncmp.sub", state.language))
                    .font(.footnote).foregroundStyle(Theme.t2)

                VStack(alignment: .leading, spacing: 6) {
                    Text(L10n.t("ncmp.topic", state.language)).font(.subheadline).foregroundStyle(Theme.txt)
                    TextField(L10n.t("ncmp.topic.ph", state.language), text: $topic, axis: .vertical)
                        .lineLimit(2...4).foregroundStyle(Theme.txt)
                        .padding(10).background(Theme.scrBot)
                        .clipShape(RoundedRectangle(cornerRadius: 11))
                        .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                }.card()

                Button(action: send) {
                    HStack { if busy { ProgressView().tint(.white) }; Text(L10n.t("ncmp", state.language)).bold() }
                        .frame(maxWidth: .infinity).padding(.vertical, 14)
                        .background(Theme.brand).foregroundStyle(.white)
                        .clipShape(RoundedRectangle(cornerRadius: 13))
                }.disabled(topic.isEmpty || busy)

                if let error { Text(error).font(.footnote).foregroundStyle(Theme.red) }

                if let p = result {
                    VStack(alignment: .leading, spacing: 8) {
                        HStack(spacing: 8) {
                            Circle().fill(p.status == "published" ? Theme.green : Theme.amber).frame(width: 9, height: 9)
                            Text((p.status ?? "draft").capitalized).font(.headline).foregroundStyle(Theme.txt)
                        }
                        Divider().overlay(Theme.line)
                        Text(p.content ?? "· held for review ·")
                            .font(.subheadline).foregroundStyle(Theme.txt)
                        if let prov = p.provenance {
                            ProvenanceFooter(provenance: prov, lang: state.language)
                        }
                    }.card()
                }
            }.padding(20)
        }
    }

    private func send() {
        guard let pid = state.pid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do { result = try await ApiClient.shared.compose(id: pid, token: token, topic: topic) }
            catch { self.error = error.localizedDescription }
            busy = false
        }
    }
}
