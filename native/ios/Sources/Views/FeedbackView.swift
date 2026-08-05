import SwiftUI

/// Help us improve: send an idea, improvement, bug, or praise. You see your
/// own submissions and the running tally — never anyone else's words.
struct FeedbackCard: View {
    @EnvironmentObject var state: AppState
    @State private var category = "idea"
    @State private var message = ""
    @State private var rating = 0
    @State private var st: FeedbackState?
    @State private var status: String?

    private let categories = ["idea", "improvement", "bug", "praise", "other"]

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(L10n.t("ns.fb", state.language)).font(.headline).foregroundStyle(Theme.txt)
            Text(L10n.t("ns.fb.sub", state.language))
                .font(.caption).foregroundStyle(Theme.t2)

            Picker("", selection: $category) {
                ForEach(categories, id: \.self) { Text(L10n.t("ns.fb.c.\($0)", state.language)).tag($0) }
            }.pickerStyle(.segmented)

            TextField(L10n.t("ns.fb.msg.ph", state.language), text: $message, axis: .vertical)
                .lineLimit(2...5).foregroundStyle(Theme.txt)
                .padding(10).background(Theme.scrBot)
                .clipShape(RoundedRectangle(cornerRadius: 11))
                .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))

            HStack(spacing: 6) {
                Text(L10n.t("ns.fb.rating", state.language)).font(.caption).foregroundStyle(Theme.t2)
                ForEach(1...5, id: \.self) { n in
                    Button { rating = (rating == n ? 0 : n) } label: {
                        Image(systemName: n <= rating ? "star.fill" : "star")
                            .foregroundStyle(n <= rating ? Theme.amber : Theme.t3)
                    }
                }
            }

            Button(L10n.t("ns.fb.send", state.language)) { send() }
                .font(.caption.bold()).foregroundStyle(.white)
                .padding(.horizontal, 12).padding(.vertical, 9)
                .background(Theme.brandA).clipShape(Capsule())
                .disabled(message.trimmingCharacters(in: .whitespaces).isEmpty)

            if let status { Text(status).font(.caption).foregroundStyle(Theme.green) }

            if let st, st.total > 0 {
                Divider().overlay(Theme.line)
                // The tally named its categories in English inside a
                // sentence that is otherwise translated.
                Text(L10n.fill("ns.fb.sofar", state.language, ["tally":
                    categories.compactMap { c in
                        (st.tally[c] ?? 0) > 0
                            ? "\(st.tally[c]!) \(L10n.t("ns.fb.c.\(c)", state.language))" : nil
                    }.joined(separator: " · ")]))
                    .font(.caption2).foregroundStyle(Theme.t3)
                if !st.mine.isEmpty {
                    Text(L10n.t("ns.fb.mine", state.language)).font(.caption.bold()).foregroundStyle(Theme.txt)
                    ForEach(st.mine.prefix(4), id: \.id) { f in
                        HStack {
                            Text("[\(f.category)] \(f.message)")
                                .font(.caption2).foregroundStyle(Theme.t2)
                                .lineLimit(1)
                            Spacer()
                            Text(f.status).font(.caption2).foregroundStyle(Theme.brandA)
                        }
                    }
                }
            }
        }.card()
        .task { await load() }
    }

    private func load() async {
        st = try? await ApiClient.shared.feedback(token: state.token)
    }

    private func send() {
        Task {
            do {
                _ = try await ApiClient.shared.submitFeedback(
                    token: state.token, category: category,
                    message: message.trimmingCharacters(in: .whitespaces),
                    rating: rating == 0 ? nil : rating)
                status = "Thank you — sent."
                message = ""; rating = 0
            } catch { status = error.localizedDescription }
            await load()
        }
    }
}
