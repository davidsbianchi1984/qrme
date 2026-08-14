import SwiftUI

/// Somebody else's homepage, in the pocket.
///
/// The console got this screen in the homepage round; the phones got the
/// route and no screen. Until now a friend on this shell was a row of text
/// with a remove button — you could see that somebody was your friend and
/// never see anything they had made.
///
///     asked     can the phone list your friends
///     mattered  can it open one
///
/// Every route here is visitor-readable by design: the page, the homepage
/// sandbox, the wall, the friends and the uploads are what a visitor came
/// to look at. There is no stats row, and that is not an omission —
/// `GET /profiles/{id}/stats` is `require_owner`, which is exactly why the
/// console's old inline card, having no way to fetch theirs, showed *your*
/// numbers under their name.
///
/// ## The markup is the one thing this screen does not render
///
/// A decorated page may carry the owner's own HTML — the MySpace half of
/// the promise. The console renders it in an iframe with `sandbox=""`,
/// every capability switched off, and says why: `pages.py` sanitises on the
/// way in and does it well, but the iframe is about who pays if that is
/// ever wrong.
///
/// This shell has no equivalent. Showing it would mean introducing a
/// `WKWebView` — the first in this app — to run a stranger's stored markup,
/// and a web view's default posture is nothing like `sandbox=""`. So the
/// page is rendered from its *structured* parts, which is most of it, and
/// the markup block is named rather than drawn.
///
///     asked     does the phone show their page
///     mattered  does it show it without giving a stranger's markup
///               somewhere to run
///
/// That is a real gap and it is stated on the screen, in the reader's
/// language, rather than left as a silently missing section.
struct ProfilePageView: View {
    @EnvironmentObject var state: AppState
    /// Whose page this is. Changing it reloads everything — that is how the
    /// Top 8 keeps walking without the sheet closing and reopening.
    @State var profileId: String
    var onClose: () -> Void

    @State private var who: ProfileCard?
    @State private var page: PageCard?
    @State private var home: HomepageDoc?
    @State private var posts: [WallPostRow] = []
    @State private var friends: [FriendRow] = []
    @State private var media: [MediaOut] = []
    /// Your own list, so the screen can tell which of three states this is.
    /// `social.send_message` refuses between strangers, and `_are_friends`
    /// is *mutual* on purpose — consent only one person can end is not
    /// consent. So a Message button on a stranger's page always fails, and
    /// one drawn the moment you add them still fails, which is the worse of
    /// the two because it looks like it should have worked.
    @State private var befriended: [String] = []
    @State private var pane = "wall"
    @State private var said = ""
    @State private var reply: String?
    @State private var note: String?
    @State private var busy = false

    private var mine: Bool { profileId == state.pid }
    private var name: String {
        who?.display_name ?? home?.display_name ?? profileId
    }
    private var photos: [MediaOut] { media.filter { $0.kind == "image" } }
    private var videos: [MediaOut] { media.filter { $0.kind == "video" } }
    /// Their Top 8 as they arranged it, their friends list as the fallback —
    /// a page whose owner never picked eight is still somewhere to walk on
    /// from rather than a dead end.
    private var top: [PageFriendRow] {
        let picked = page?.top_friends ?? []
        if !picked.isEmpty { return Array(picked.prefix(8)) }
        return friends.prefix(8).map {
            PageFriendRow(profile_id: $0.profile_id,
                          display_name: $0.display_name, avatar: nil)
        }
    }
    private var listedThem: Bool { befriended.contains(profileId) }
    private var listedYou: Bool {
        friends.contains { $0.profile_id == state.pid }
    }
    private var mutual: Bool { listedThem && listedYou }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                hero
                if !mine { actions }
                if !top.isEmpty { topFriends }
                panes
                paneBody
                if let offers = page?.offers, !offers.isEmpty { offerList }
                if let note {
                    Text(note).font(.caption2).foregroundStyle(Theme.t2)
                }
            }.padding(20)
        }
        .navigationTitle(name)
        .toolbar {
            ToolbarItem(placement: .cancellationAction) {
                Button(L10n.t("prf.back", state.language)) { onClose() }
            }
        }
        .task(id: profileId) { await load() }
    }

    // MARK: - the page as they decorated it

    private var hero: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("prf.theirs", state.language))
                .font(.caption2).foregroundStyle(Theme.t2)
            Text(home?.headline ?? page?.tagline ?? name)
                .font(.headline).foregroundStyle(Theme.txt)
            if let tag = page?.tagline, home?.headline != nil {
                Text(tag).font(.caption2).foregroundStyle(Theme.t2)
            }
            let about = home?.about ?? page?.about
            if let about, !about.isEmpty {
                Text(about).font(.caption).foregroundStyle(Theme.txt)
            }
            ForEach(page?.links ?? []) { link in
                // A stranger's URL opens in the system browser rather than
                // anywhere inside this app, for the same reason the markup
                // is not rendered here.
                if let url = URL(string: link.url) {
                    Link(link.label ?? link.url, destination: url)
                        .font(.caption2).foregroundStyle(Theme.brandA)
                }
            }
            // Named, not drawn. See this file's header.
            if let html = page?.html, !html.isEmpty {
                Text(L10n.t("prf.markuponweb", state.language))
                    .font(.caption2).foregroundStyle(Theme.t2)
            }
            if let page, page.customised == false {
                Text(L10n.t("prf.plain", state.language)
                        .replacingOccurrences(of: "{name}", with: name))
                    .font(.caption2).foregroundStyle(Theme.t2)
            }
        }.card()
    }

    // MARK: - what a visitor may actually do

    private var actions: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("prf.saylabel", state.language)
                    .replacingOccurrences(of: "{name}", with: name))
                .font(.caption2).foregroundStyle(Theme.t2)
            TextField(L10n.t("prf.sayhint", state.language), text: $said,
                      axis: .vertical)
                .lineLimit(2...4)
                .padding(8).background(Theme.scrBot)
                .clipShape(RoundedRectangle(cornerRadius: 9))
            HStack(spacing: 8) {
                Button(L10n.t("prf.talk", state.language)) { talk() }
                    .font(.caption.bold()).foregroundStyle(.white)
                    .padding(.horizontal, 12).padding(.vertical, 8)
                    .background(Theme.brandA).clipShape(Capsule())
                    .disabled(busy || said.trimmingCharacters(
                        in: .whitespaces).isEmpty)
                if mutual {
                    Button(L10n.t("prf.message", state.language)) { message() }
                        .font(.caption2).foregroundStyle(Theme.t2)
                        .disabled(busy || said.trimmingCharacters(
                            in: .whitespaces).isEmpty)
                } else if !listedThem {
                    Button(L10n.t("prf.befriend", state.language)) { befriend() }
                        .font(.caption2).foregroundStyle(Theme.t2)
                        .disabled(busy)
                }
                Button(L10n.t("prf.room", state.language)) { openRoom() }
                    .font(.caption2).foregroundStyle(Theme.t2)
                    .disabled(busy)
            }
            Text(mutual
                 ? L10n.t("prf.actionsnote", state.language)
                 : listedThem
                   ? L10n.t("prf.waiting", state.language)
                       .replacingOccurrences(of: "{name}", with: name)
                   : L10n.t("prf.notyetfriends", state.language))
                .font(.caption2).foregroundStyle(Theme.t2)
            if let reply {
                Text(reply).font(.caption).foregroundStyle(Theme.txt)
            }
        }.card()
    }

    // MARK: - their eight, and walking on

    private var topFriends: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("prf.topfriends", state.language)
                    .replacingOccurrences(of: "{n}", with: "\(top.count)"))
                .font(.caption2).foregroundStyle(Theme.t2)
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 10) {
                    ForEach(top) { f in
                        Button(f.display_name ?? f.profile_id) {
                            // Walk on. `task(id:)` reloads in place, so the
                            // sheet never stacks.
                            profileId = f.profile_id
                        }
                        .font(.caption2).foregroundStyle(Theme.t2)
                        .padding(.horizontal, 10).padding(.vertical, 6)
                        .background(Theme.scrBot).clipShape(Capsule())
                    }
                }
            }
        }.card()
    }

    // MARK: - wall, photos, videos, friends

    private var panes: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                chip("wall", "prf.pane.wall", posts.count)
                chip("photos", "prf.pane.photos", photos.count)
                chip("videos", "prf.pane.videos", videos.count)
                chip("friends", "prf.pane.friends", friends.count)
            }
        }
    }

    private func chip(_ key: String, _ label: String, _ n: Int) -> some View {
        Button(L10n.t(label, state.language)
                .replacingOccurrences(of: "{n}", with: "\(n)")) {
            pane = key
        }
        .font(.caption2.bold())
        .foregroundStyle(pane == key ? .white : Theme.t2)
        .padding(.horizontal, 10).padding(.vertical, 6)
        .background(pane == key ? Theme.brandA : Theme.scrBot)
        .clipShape(Capsule())
    }

    @ViewBuilder
    private var paneBody: some View {
        switch pane {
        case "wall":
            if posts.isEmpty {
                empty(L10n.t("prf.nowall", state.language)
                        .replacingOccurrences(of: "{name}", with: name))
            } else {
                ForEach(posts) { p in
                    VStack(alignment: .leading, spacing: 4) {
                        Text(p.body).font(.caption).foregroundStyle(Theme.txt)
                        if let at = p.created_at {
                            Text(String(at.prefix(10)))
                                .font(.caption2).foregroundStyle(Theme.t2)
                        }
                    }.card()
                }
            }
        case "photos":
            gallery(photos, L10n.t("prf.nophotos", state.language))
        case "videos":
            gallery(videos, L10n.t("prf.novideos", state.language))
        default:
            if friends.isEmpty {
                empty(L10n.t("prf.nofriends", state.language))
            } else {
                ForEach(friends) { f in
                    Button(f.display_name ?? f.profile_id) {
                        profileId = f.profile_id
                    }
                    .font(.caption).foregroundStyle(Theme.t2)
                }
            }
        }
    }

    /// The alt text leads each row rather than trailing it: this list is
    /// read aloud to people who cannot see any of it, and a filename tells
    /// them nothing.
    @ViewBuilder
    private func gallery(_ rows: [MediaOut], _ none: String) -> some View {
        if rows.isEmpty {
            empty(none)
        } else {
            ForEach(rows, id: \.id) { m in
                Text(m.alt ?? m.name ?? m.id ?? "—")
                    .font(.caption2).foregroundStyle(Theme.t2)
            }
        }
    }

    private func empty(_ text: String) -> some View {
        Text(text).font(.caption2).foregroundStyle(Theme.t2)
    }

    private var offerList: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(L10n.t("prf.offers", state.language))
                .font(.caption2).foregroundStyle(Theme.t2)
            ForEach(page?.offers ?? []) { o in
                Text(o.blurb.map { "\(o.title) — \($0)" } ?? o.title)
                    .font(.caption).foregroundStyle(Theme.txt)
            }
        }.card()
    }

    // MARK: - loading and the three actions

    private func load() async {
        who = nil; page = nil; home = nil; posts = []; friends = []
        media = []; pane = "wall"; reply = nil; note = nil
        who = try? await ApiClient.shared.profile(profileId)
        page = try? await ApiClient.shared.page(id: profileId)
        // A homepage kept private answers 404. That is a choice, not an
        // error, so it degrades to the decorated page rather than to a
        // broken screen.
        home = try? await ApiClient.shared.homepage(profileId: profileId)
        posts = (try? await ApiClient.shared.wall(profileId: profileId)) ?? []
        friends = (try? await ApiClient.shared.friends(
            profileId: profileId)) ?? []
        media = (try? await ApiClient.shared.profileMedia(
            profileId: profileId)) ?? []
        if let mine = state.pid {
            befriended = ((try? await ApiClient.shared.friends(
                profileId: mine)) ?? []).map(\.profile_id)
        }
    }

    private func run(_ op: @escaping () async throws -> Void) {
        busy = true; note = nil
        Task {
            do { try await op() }
            catch { note = error.localizedDescription }
            busy = false
        }
    }

    private func talk() {
        guard let interactor = state.interactorId,
              let token = state.interactorToken else {
            note = L10n.t("prf.needuser", state.language); return
        }
        run {
            let answer = try await ApiClient.shared.chat(
                id: profileId, token: token, interactorId: interactor,
                message: said.trimmingCharacters(in: .whitespaces))
            reply = answer.profile_message.content
            said = ""
        }
    }

    private func message() {
        guard let mine = state.pid, let token = state.token else { return }
        run {
            _ = try await ApiClient.shared.sendDm(
                profileId: mine, to: profileId,
                body: said.trimmingCharacters(in: .whitespaces), token: token)
            said = ""
            note = L10n.t("prf.sent", state.language)
        }
    }

    private func befriend() {
        guard let mine = state.pid, let token = state.token else { return }
        run {
            _ = try await ApiClient.shared.addFriend(
                profileId: mine, friendId: profileId, token: token)
            befriended.append(profileId)
            note = L10n.t("prf.befriended", state.language)
                .replacingOccurrences(of: "{name}", with: name)
        }
    }

    private func openRoom() {
        guard let interactor = state.interactorId else {
            note = L10n.t("prf.needuser", state.language); return
        }
        run {
            // You as a person, them as a profile — the two-participant shape
            // the backend requires, with the second one actually being them.
            _ = try await ApiClient.shared.createRoom(
                topic: "", profileId: profileId, interactorId: interactor)
            note = L10n.t("prf.roomopened", state.language)
        }
    }
}
