import SwiftUI

/// The people around a profile, in the pocket: the friends list, who the
/// platform suggests and why, the wall, and the comments under a post.
///
/// The backend has carried all nine of these routes since the community
/// round; every client but the phones had a door for them. Three rules
/// this screen keeps rather than invents:
///
/// * **A pinned row gets no remove control.** The founder's two profiles
///   refuse deletion with 409, and the list says `pinned` precisely so a
///   client can leave the button off instead of offering one that fails.
/// * **A blocked post or comment comes back to its author.** The write
///   answers 201 with a `status`, because the words *were* recorded —
///   what happened to them is the status, not an error.
/// * **Suggestions say what they were ranked on.** The route returns the
///   reason with each name; showing the name without the reason would be
///   the one thing the route was careful not to do.
///
/// Strings go through L10n so the English count behind this shell's tabs
/// does not grow; refusals arrive from the server already in the
/// reader's language and are shown verbatim.
struct PeopleSection: View {
    @EnvironmentObject var state: AppState
    @State private var friends: [FriendRow] = []
    @State private var suggested: [SuggestedRow] = []
    @State private var posts: [WallPostRow] = []
    @State private var comments: [CommentRow] = []
    @State private var addId = ""
    @State private var draft = ""
    @State private var openPost: String?
    @State private var commentDraft = ""
    @State private var note: String?
    @State private var busy = false
    @State private var inboxPage: InboxPage?

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                // What happened while you were away. The deed, never the
                // words: a row names the kind and the actor, and the words
                // stay behind their own doors below.
                if let page = inboxPage, !page.events.isEmpty {
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Text(L10n.t("inbox.title", state.language))
                                .font(.headline).foregroundStyle(Theme.txt)
                            if page.unseen > 0 {
                                Text("\(page.unseen) " +
                                     L10n.t("inbox.new", state.language))
                                    .font(.caption2)
                                    .foregroundStyle(Theme.brandA)
                            }
                        }
                        ForEach(page.events) { e in
                            HStack {
                                Text(e.actor_name ?? e.actor_id)
                                    .font(.caption).bold()
                                    .foregroundStyle(
                                        e.seen ? Theme.t2 : Theme.txt)
                                Text(L10n.t("inbox.kind.\(e.kind)",
                                            state.language))
                                    .font(.caption)
                                    .foregroundStyle(Theme.t2)
                                Spacer()
                            }
                        }
                        if page.unseen > 0 {
                            Button(L10n.t("inbox.seen", state.language)) {
                                run {
                                    try await ApiClient.shared.markInboxSeen(
                                        profileId: state.pid!,
                                        token: state.token!)
                                }
                            }.font(.caption).disabled(busy)
                        }
                    }
                    .padding(12)
                    .background(Theme.card)
                    .clipShape(RoundedRectangle(cornerRadius: 14))
                }
                VStack(alignment: .leading, spacing: 8) {
                    Text(L10n.t("people.friends", state.language))
                        .font(.headline).foregroundStyle(Theme.txt)
                    ForEach(friends) { f in
                        HStack {
                            let who = f.display_name ?? f.profile_id
                            let line = f.founder ? who + " ★" : who
                            Text(line).font(.caption)
                                .foregroundStyle(Theme.txt)
                            Spacer()
                            if f.pinned {
                                // Pinned rows refuse deletion: no control
                                // rather than one that fails.
                                Text(L10n.t("people.pinned", state.language))
                                    .font(.caption2).foregroundStyle(Theme.t2)
                            } else {
                                Button(L10n.t("people.remove",
                                              state.language)) {
                                    remove(f.profile_id)
                                }.font(.caption2).disabled(busy)
                            }
                        }
                    }
                    HStack {
                        TextField(L10n.t("people.add", state.language),
                                  text: $addId)
                            .textFieldStyle(.roundedBorder)
                        Button(L10n.t("people.add.go", state.language)) {
                            add()
                        }.disabled(busy || addId.isEmpty)
                    }
                }.card()

                if !suggested.isEmpty {
                    VStack(alignment: .leading, spacing: 8) {
                        Text(L10n.t("people.suggested", state.language))
                            .font(.subheadline.bold())
                            .foregroundStyle(Theme.txt)
                        Text(L10n.t("people.ranked", state.language))
                            .font(.caption2).foregroundStyle(Theme.t2)
                        ForEach(suggested) { s in
                            HStack {
                                let who = s.display_name ?? s.profile_id
                                let why = s.because ?? ""
                                let line = why.isEmpty ? who
                                    : who + " · " + why
                                Text(line).font(.caption2)
                                    .foregroundStyle(Theme.t2)
                                Spacer()
                                Button(L10n.t("people.add.go",
                                              state.language)) {
                                    addId = s.profile_id
                                    add()
                                }.font(.caption2).disabled(busy)
                            }
                        }
                    }.card()
                }

                VStack(alignment: .leading, spacing: 8) {
                    Text(L10n.t("people.wall", state.language))
                        .font(.subheadline.bold()).foregroundStyle(Theme.txt)
                    HStack {
                        TextField(L10n.t("people.say", state.language),
                                  text: $draft)
                            .textFieldStyle(.roundedBorder)
                        Button(L10n.t("people.post", state.language)) {
                            publish()
                        }.disabled(busy || draft.isEmpty)
                    }
                    ForEach(posts) { p in
                        VStack(alignment: .leading, spacing: 4) {
                            Text(p.body).font(.caption)
                                .foregroundStyle(Theme.txt)
                            HStack {
                                if p.status == "blocked" {
                                    Text(L10n.t("people.blocked",
                                                state.language))
                                        .font(.caption2)
                                        .foregroundStyle(Theme.t2)
                                }
                                Spacer()
                                Button(L10n.t("people.comments",
                                              state.language)) {
                                    open(p.id)
                                }.font(.caption2).disabled(busy)
                            }
                        }
                    }
                }.card()

                if let openPost {
                    VStack(alignment: .leading, spacing: 8) {
                        Text(L10n.t("people.comments", state.language))
                            .font(.subheadline.bold())
                            .foregroundStyle(Theme.txt)
                        ForEach(comments) { c in
                            HStack {
                                Text(c.body).font(.caption2)
                                    .foregroundStyle(Theme.t2)
                                Spacer()
                                if c.author_id == state.pid {
                                    Button(L10n.t("people.withdraw",
                                                  state.language)) {
                                        withdraw(c.id)
                                    }.font(.caption2).disabled(busy)
                                }
                            }
                        }
                        HStack {
                            TextField(L10n.t("people.reply", state.language),
                                      text: $commentDraft)
                                .textFieldStyle(.roundedBorder)
                            Button(L10n.t("people.send", state.language)) {
                                comment(openPost)
                            }.disabled(busy || commentDraft.isEmpty)
                        }
                    }.card()
                }

                CrowdSection()
                PartySection()
                LendingSection()
                PlaceSection()
                CameraSection()
                OrgSection()
                TourSection()
                BodySection()
                ReferralSection()
                ObjectionSection()
                LobbySection()
                DockSection()
                SealSection()
                MailSection()
                RoomsSection()
                WallScreenSection()
                PlanSection()
                HandoffSection()
                CampaignSection()
                WorkSection()
                DelegationSection()
                AssistantSection()
                TaskSection()
                PlacementSection()
                SpecialistSection()
                MemorySection()
                PairSection()
                SourceSection()
                RecordSection()
                VeilSection()
                BadgeSection()
                ExitSection()
                AvatarSection()
                EmblemSection()
                PageSection()
                SurfaceSection()
                EmbodimentSection()
                SteeringSection()
                WristSection()
                KeysSection()
                TillSection()
                LifelineSection()

                if let note {
                    Text(note).font(.caption).foregroundStyle(Theme.t2)
                }
            }.padding(20)
        }
        .task { await load() }
    }

    private func load() async {
        guard let pid = state.pid else { return }
        friends = (try? await ApiClient.shared.friends(profileId: pid)) ?? []
        suggested = (try? await ApiClient.shared.suggestedFriends(
            profileId: pid)) ?? []
        posts = (try? await ApiClient.shared.wall(profileId: pid)) ?? []
        if let token = state.token {
            inboxPage = try? await ApiClient.shared.inbox(
                profileId: pid, token: token)
        }
    }

    private func run(_ op: @escaping () async throws -> Void) {
        busy = true; note = nil
        Task {
            do { try await op(); await load() }
            catch { note = error.localizedDescription }
            busy = false
        }
    }

    private func add() {
        run {
            _ = try await ApiClient.shared.addFriend(
                profileId: state.pid!, friendId: addId, token: state.token!)
            addId = ""
        }
    }

    private func remove(_ friendId: String) {
        run {
            try await ApiClient.shared.removeFriend(
                profileId: state.pid!, friendId: friendId,
                token: state.token!)
        }
    }

    private func publish() {
        run {
            let made = try await ApiClient.shared.postToWall(
                profileId: state.pid!, body: draft, token: state.token!)
            draft = ""
            if made.status == "blocked" {
                note = L10n.t("people.blocked", state.language)
            }
        }
    }

    private func open(_ postId: String) {
        openPost = postId
        run {
            comments = try await ApiClient.shared.comments(
                kind: "posts", targetId: postId, token: state.token!)
        }
    }

    private func comment(_ postId: String) {
        run {
            _ = try await ApiClient.shared.addComment(
                kind: "posts", targetId: postId, body: commentDraft,
                token: state.token!)
            commentDraft = ""
            comments = try await ApiClient.shared.comments(
                kind: "posts", targetId: postId, token: state.token!)
        }
    }

    private func withdraw(_ commentId: String) {
        run {
            try await ApiClient.shared.deleteComment(
                commentId: commentId, token: state.token!)
            if let openPost {
                comments = try await ApiClient.shared.comments(
                    kind: "posts", targetId: openPost, token: state.token!)
            }
        }
    }
}
