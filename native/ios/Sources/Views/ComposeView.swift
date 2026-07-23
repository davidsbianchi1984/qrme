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
                Text("Compose").font(.title2.bold()).foregroundStyle(Theme.txt)
                Text("Give a topic — your profile writes a post in its own voice.")
                    .font(.footnote).foregroundStyle(Theme.t2)

                VStack(alignment: .leading, spacing: 6) {
                    Text("Topic").font(.subheadline).foregroundStyle(Theme.txt)
                    TextField("What should it post about?", text: $topic, axis: .vertical)
                        .lineLimit(2...4).foregroundStyle(Theme.txt)
                        .padding(10).background(Theme.scrBot)
                        .clipShape(RoundedRectangle(cornerRadius: 11))
                        .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                }.card()

                Button(action: send) {
                    HStack { if busy { ProgressView().tint(.white) }; Text("Compose post").bold() }
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
                        Text(p.content).font(.subheadline).foregroundStyle(Theme.txt)
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
