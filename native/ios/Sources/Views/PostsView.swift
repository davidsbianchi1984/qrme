import SwiftUI

/// The profile's published feed (GET /profiles/{id}/posts).
struct PostsView: View {
    @EnvironmentObject var state: AppState
    @State private var posts: [Post] = []
    @State private var loading = true

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("Posts").font(.title2.bold()).foregroundStyle(Theme.txt)
                Text("Everything your profile has posted.").font(.footnote).foregroundStyle(Theme.t2)

                if loading {
                    ProgressView().tint(Theme.brandA).frame(maxWidth: .infinity)
                } else if posts.isEmpty {
                    Text("No posts yet — write one in Compose.")
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
                        }.card()
                    }
                }
            }.padding(20)
        }
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
