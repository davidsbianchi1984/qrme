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
    // The finder: beta testers looking for each other by the name they know.
    @State private var findQ = ""
    @State private var foundPeople: [ApiClient.FoundPerson] = []
    @State private var searched = false
    // Everyone here: the browse pool and its honest head count — every
    // profile on the deployment, listed until its owner goes private.
    @State private var pool: ApiClient.BrowsePool?
    @State private var listedHere: Bool?
    @State private var draft = ""
    @State private var openPost: String?
    @State private var commentDraft = ""
    @State private var note: String?
    @State private var busy = false
    @State private var inboxPage: InboxPage?
    /// Whose page is open over this one, or nil. A sheet rather than a push:
    /// their Top 8 walks onward *inside* the sheet, so the stack never grows
    /// however far somebody wanders.
    @State private var visiting: String?

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
                // Find people: publicly listed profiles by name or handle —
                // the door two beta testers needed to become friends.
                VStack(alignment: .leading, spacing: 8) {
                    Text(L10n.t("nfp.title", state.language))
                        .font(.headline).foregroundStyle(Theme.txt)
                    HStack(spacing: 8) {
                        TextField(L10n.t("nfp.ph", state.language), text: $findQ)
                            .font(.subheadline).foregroundStyle(Theme.txt)
                            .padding(10).background(Theme.scrBot)
                            .clipShape(RoundedRectangle(cornerRadius: 10))
                        Button(L10n.t("nfp.title", state.language)) {
                            run {
                                let r = try await ApiClient.shared.findPeople(q: findQ)
                                foundPeople = r.found
                                searched = true
                            }
                        }
                        .font(.caption.bold())
                        .disabled(busy || findQ.trimmingCharacters(in: .whitespaces).isEmpty)
                    }
                    if searched && foundPeople.isEmpty {
                        Text(L10n.t("nfp.none", state.language))
                            .font(.caption2).foregroundStyle(Theme.t2)
                    }
                    ForEach(foundPeople, id: \.profile_id) { p in
                        HStack {
                            Button(p.display_name) { visiting = p.profile_id }
                                .font(.caption).foregroundStyle(Theme.txt)
                            if let h = p.handle {
                                Text("@" + h).font(.caption2)
                                    .foregroundStyle(Theme.t3)
                            }
                            Spacer()
                            if friends.contains(where: { $0.profile_id == p.profile_id }) {
                                Text(L10n.t("nfp.already", state.language))
                                    .font(.caption2).foregroundStyle(Theme.t2)
                            } else {
                                Button(L10n.t("people.add", state.language)) {
                                    add(p.profile_id)
                                }.font(.caption2).disabled(busy)
                            }
                        }
                    }
                }
                .padding(12)
                .background(Theme.card)
                .clipShape(RoundedRectangle(cornerRadius: 14))

                // Everyone here: real people and synthetic profiles side by
                // side, with the honest head count — the whole pool unless
                // an owner went private. The switch below the count is this
                // profile's own door out and back in.
                if let pool {
                    VStack(alignment: .leading, spacing: 8) {
                        Text(L10n.t("frn.pool", state.language))
                            .font(.headline).foregroundStyle(Theme.txt)
                        Text(L10n.t("frn.pool.count", state.language)
                            .replacingOccurrences(of: "{n}",
                                                  with: String(pool.head_count)))
                            .font(.caption).foregroundStyle(Theme.t2)
                        if let listedHere {
                            HStack(spacing: 8) {
                                Text(L10n.t(listedHere ? "frn.pool.listed"
                                                       : "frn.pool.private",
                                            state.language))
                                    .font(.caption2).foregroundStyle(Theme.t2)
                                Button(L10n.t(listedHere ? "frn.pool.goprivate"
                                                         : "frn.pool.golisted",
                                              state.language)) { flipListing() }
                                    .font(.caption2).disabled(busy)
                            }
                        }
                        ForEach(pool.found, id: \.profile_id) { p in
                            HStack {
                                Button(p.display_name) { visiting = p.profile_id }
                                    .font(.caption).foregroundStyle(Theme.txt)
                                Text(L10n.t("frn.kind.\(p.kind)",
                                            state.language))
                                    .font(.caption2).foregroundStyle(Theme.t3)
                                Spacer()
                                if p.profile_id == state.pid {
                                    Text(L10n.t("frn.pool.you", state.language))
                                        .font(.caption2)
                                        .foregroundStyle(Theme.t2)
                                } else if friends.contains(
                                    where: { $0.profile_id == p.profile_id }) {
                                    Text(L10n.t("nfp.already", state.language))
                                        .font(.caption2)
                                        .foregroundStyle(Theme.t2)
                                } else {
                                    Button(L10n.t("people.add",
                                                  state.language)) {
                                        add(p.profile_id)
                                    }.font(.caption2).disabled(busy)
                                }
                            }
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
                            // The name is the door. Until this round a
                            // friend on this shell was a row of text with a
                            // remove button: you could see that somebody was
                            // your friend and never see anything they made.
                            Button(line) { visiting = f.profile_id }
                                .font(.caption)
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
                BeaconSection()
                QueueSection()
                ReviewSection()
                StampSection()
                MediaSection()
                WearableSection()
                BirthSection()
                MindSection()
                ReachSection()
                LicenseSection()
                SensesSection()
                AllowedSection()

                if let note {
                    Text(note).font(.caption).foregroundStyle(Theme.t2)
                }
            }.padding(20)
        }
        .task { await load() }
        .sheet(item: Binding(get: { visiting.map(Visited.init) },
                             set: { visiting = $0?.id })) { v in
            NavigationStack {
                ProfilePageView(profileId: v.id) { visiting = nil }
                    .environmentObject(state)
            }
        }
    }

    /// `sheet(item:)` wants something `Identifiable`; the id is the whole
    /// value here, and wrapping it keeps the sheet re-presenting when the
    /// visited profile changes rather than going stale on the first one.
    private struct Visited: Identifiable { let id: String }

    private func load() async {
        guard let pid = state.pid else { return }
        friends = (try? await ApiClient.shared.friends(profileId: pid)) ?? []
        suggested = (try? await ApiClient.shared.suggestedFriends(
            profileId: pid)) ?? []
        posts = (try? await ApiClient.shared.wall(profileId: pid)) ?? []
        pool = try? await ApiClient.shared.browsePeople()
        if let token = state.token {
            inboxPage = try? await ApiClient.shared.inbox(
                profileId: pid, token: token)
            listedHere = (try? await ApiClient.shared.listing(
                id: pid, token: token))?.listed
        }
    }

    private func flipListing() {
        run {
            _ = try await ApiClient.shared.setListing(
                id: state.pid!, listed: !(listedHere ?? true),
                token: state.token!)
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

    private func add(_ friendId: String) {
        run {
            _ = try await ApiClient.shared.addFriend(
                profileId: state.pid!, friendId: friendId, token: state.token!)
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
