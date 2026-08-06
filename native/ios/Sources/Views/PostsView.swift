import SwiftUI

/// The profile's published feed (GET /profiles/{id}/posts).
struct PostsView: View {
    @EnvironmentObject var state: AppState
    @State private var posts: [Post] = []
    @State private var loading = true

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text(L10n.t("tab.posts", state.language)).font(.title2.bold()).foregroundStyle(Theme.txt)
                Text(L10n.t("npst.sub", state.language)).font(.footnote).foregroundStyle(Theme.t2)

                if loading {
                    ProgressView().tint(Theme.brandA).frame(maxWidth: .infinity)
                } else if posts.isEmpty {
                    Text(L10n.t("npst.none", state.language))
                        .font(.footnote).foregroundStyle(Theme.t2).card()
                } else {
                    ForEach(posts, id: \.id) { p in
                        VStack(alignment: .leading, spacing: 8) {
                            HStack(spacing: 8) {
                                Circle().fill(p.status == "published" ? Theme.green : Theme.amber).frame(width: 8, height: 8)
                                Text((p.status ?? "draft").capitalized).font(.caption.bold())
                                    .foregroundStyle(p.status == "published" ? Theme.green : Theme.amber)
                                Spacer()
                                if let t = p.topic { Text(t).font(.caption).foregroundStyle(Theme.t3) }
                            }
                            Text(p.content ?? "· held for review ·")
                                .font(.subheadline).foregroundStyle(Theme.txt)
                            Text(p.watermark?.display?.line ?? "✦ AI")
                                .font(.caption2).foregroundStyle(Theme.t3)
                        }.card()
                    }
                }

                // The wall's posts, and beneath them the public stream those
                // posts feed into — the same rows, ranked for nobody.
                StreamSection()
                SharedCardSection()
            }.padding(20)
        }
        .refreshable { await load() }
        .task { await load() }
        .refreshable { await load() }
    }

    private func load() async {
        guard let pid = state.pid else { return }
        loading = true
        posts = (try? await ApiClient.shared.posts(id: pid)) ?? []
        loading = false
    }
}
