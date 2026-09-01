import SwiftUI

/// Connect: where the profile touches the outside world — social-platform
/// connections, the connected-apps catalog, and robotic embodiment — behind
/// one tab so the bar stays at five.
struct ConnectView: View {
    /// Raw values are the section names; the words come from the table. They
    /// were the same string until this round, which is how a translated tab
    /// bar ended up with an English tab bar directly under it — the third
    /// picker of exactly this shape in three releases.
    enum Tab: String, CaseIterable {
        case social, apps, robots, shop, corner, people

        var key: String {
            switch self {
            case .social: return "ncon.tab.social"
            case .apps: return "ncon.tab.apps"
            case .shop: return "tab.shops"
            default: return "tab.\(rawValue)"
            }
        }
    }
    @EnvironmentObject var state: AppState
    @State private var tab: Tab = .social

    var body: some View {
        VStack(spacing: 0) {
            Picker("", selection: $tab) {
                ForEach(Tab.allCases, id: \.self) { Text(L10n.t($0.key, state.language)).tag($0) }
            }
            .pickerStyle(.segmented)
            .padding(.horizontal, 20).padding(.top, 12)

            switch tab {
            case .social: SocialSection()
            case .apps: AppsSection()
            case .robots: RobotsView()
            case .shop: ShopSection()
            case .corner: CornerSection()
            case .people: PeopleSection()
            }
        }
    }
}

// MARK: Social — collect builds the profile, publish runs it on the platform

private struct SocialSection: View {
    @EnvironmentObject var state: AppState
    @State private var platform = "instagram"
    @State private var handle = ""
    @State private var conns: [SocialConn] = []
    @State private var status: String?
    @State private var error: String?

    private let platforms = ["instagram", "x", "tiktok", "facebook", "linkedin",
                             "youtube", "reddit", "threads", "whatsapp", "meta",
                             "mastodon", "twitch", "snapchat", "roblox",
                             "pinterest", "discord"]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                VStack(alignment: .leading, spacing: 10) {
                    Text(L10n.t("ncon.social", state.language)).font(.headline).foregroundStyle(Theme.txt)
                    Text(L10n.t("ncon.social.sub", state.language))
                        .font(.caption).foregroundStyle(Theme.t2)
                    Picker("", selection: $platform) {
                        ForEach(platforms, id: \.self) { Text($0.capitalized).tag($0) }
                    }.pickerStyle(.menu).tint(Theme.brandA)
                    TextField(L10n.t("ncon.handle.ph", state.language), text: $handle)
                        .foregroundStyle(Theme.txt).textInputAutocapitalization(.never)
                        .padding(10).background(Theme.scrBot)
                        .clipShape(RoundedRectangle(cornerRadius: 11))
                        .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                    HStack(spacing: 8) {
                        smallButton(L10n.t("ncon.to.collect", state.language)) { connect("collect") }
                        smallButton(L10n.t("ncon.to.publish", state.language)) { connect("publish") }
                    }
                }.card()

                if let error { Text(error).font(.footnote).foregroundStyle(Theme.red) }
                if let status { Text(status).font(.caption).foregroundStyle(Theme.green) }

                ForEach(conns, id: \.id) { c in
                    VStack(alignment: .leading, spacing: 6) {
                        HStack {
                            Text("\(c.platform.capitalized) · \(c.direction)")
                                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
                            Spacer()
                            if let h = c.handle { Text(h).font(.caption).foregroundStyle(Theme.t3) }
                        }
                        Text(c.direction == "collect"
                             ? L10n.fill("ncon.collected", state.language, ["n": "\(c.collected)"])
                             : L10n.fill("ncon.published", state.language, ["n": "\(c.published)"]))
                            .font(.caption).foregroundStyle(Theme.t2)
                        if c.status == "revoked" {
                            Text(L10n.t("nmg.revoked", state.language)).font(.caption).foregroundStyle(Theme.red)
                        } else {
                            HStack(spacing: 8) {
                                if c.direction == "collect" {
                                    smallButton(L10n.t("ncon.collect.sample", state.language)) { collect(c) }
                                    if let h = c.handle, !h.isEmpty {
                                        smallButton(L10n.t("ncon.scrape", state.language)) { scrape(c) }
                                    }
                                } else {
                                    smallButton(L10n.t("ncon.publish.update", state.language)) { publish(c) }
                                }
                                Button(L10n.t("ncon.disconnect", state.language)) { revoke(c) }
                                    .font(.caption).foregroundStyle(Theme.red)
                            }
                        }
                    }.card()
                }
            }.padding(20)
        }
        .task { await load() }
    }

    private func load() async {
        guard let pid = state.pid, let token = state.token else { return }
        conns = (try? await ApiClient.shared.socialConnections(id: pid, token: token)) ?? []
    }

    private func connect(_ direction: String) {
        guard let pid = state.pid, let token = state.token else { return }
        error = nil; status = nil
        Task {
            do {
                _ = try await ApiClient.shared.socialConnect(
                    id: pid, token: token, platform: platform,
                    direction: direction, handle: handle)
                handle = ""
            } catch { self.error = error.localizedDescription }
            await load()
        }
    }

    private func collect(_ c: SocialConn) {
        guard let token = state.token else { return }
        Task {
            do {
                try await ApiClient.shared.socialCollect(
                    cid: c.id, token: token, content: "sample post from \(c.platform)")
                status = "collected one item from \(c.platform) — it now feeds training"
            } catch { self.error = error.localizedDescription }
            await load()
        }
    }

    private func scrape(_ c: SocialConn) {
        guard let token = state.token else { return }
        Task {
            do {
                try await ApiClient.shared.socialScrape(cid: c.id, token: token)
                status = "fetched \(c.platform) — the page now feeds training"
            } catch { self.error = error.localizedDescription }
            await load()
        }
    }

    private func publish(_ c: SocialConn) {
        guard let token = state.token else { return }
        Task {
            do {
                try await ApiClient.shared.socialPublish(
                    cid: c.id, token: token, content: "An update from my synthetic profile.")
                status = "published to \(c.platform)"
            } catch { self.error = error.localizedDescription }
            await load()
        }
    }

    private func revoke(_ c: SocialConn) {
        guard let token = state.token else { return }
        Task {
            try? await ApiClient.shared.revokeSocial(cid: c.id, token: token)
            await load()
        }
    }
}

// MARK: Apps — the AI-integrated apps catalog (collect · act · produce)

private struct AppsSection: View {
    @EnvironmentObject var state: AppState
    @State private var flat: [(key: String, provider: String, app: String,
                               label: String, needs: String)] = []
    @State private var conns: [AppConn] = []
    @State private var status: String?
    @State private var error: String?
    @State private var find = ""
    /// Which connector is having its credential typed, and into what. The
    /// secret is held only as long as the field is open — it goes to the
    /// vault through `appAuthorize` and is never stored on this device.
    @State private var signing: String?
    @State private var secret = ""

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                VStack(alignment: .leading, spacing: 8) {
                    Text(L10n.t("ncon.apps", state.language)).font(.headline).foregroundStyle(Theme.txt)
                    Text(L10n.t("ncon.apps.sub", state.language))
                        .font(.caption).foregroundStyle(Theme.t2)
                    // The whole board, searchable. It used to be
                    // `flat.prefix(12)` against a catalogue of a hundred and
                    // three — a shop that shows a twelfth of its shelves and
                    // gives you no way to ask for the rest.
                    TextField(L10n.t("ncon.apps.find", state.language), text: $find)
                        .textFieldStyle(.roundedBorder)
                    ForEach(shown, id: \.key) { entry in
                        HStack {
                            Text(entry.label).font(.subheadline).foregroundStyle(Theme.txt)
                            Text(entry.provider).font(.caption).foregroundStyle(Theme.t3)
                            if entry.needs_first != "nothing" {
                                Text(entry.needs_first == "key" ? "🔑" : "🔒").font(.caption)
                            }
                            Spacer()
                            Button(L10n.t("tab.connect", state.language)) { connect(entry.provider, entry.app) }
                                .font(.caption.bold()).foregroundStyle(Theme.brandA)
                        }
                    }
                }.card()

                if let error { Text(error).font(.footnote).foregroundStyle(Theme.red) }
                if let status { Text(status).font(.caption).foregroundStyle(Theme.green) }

                ForEach(conns, id: \.id) { c in
                    VStack(alignment: .leading, spacing: 6) {
                        HStack {
                            Text(c.label).font(.subheadline.bold()).foregroundStyle(Theme.txt)
                            Spacer()
                            Text(c.provider).font(.caption).foregroundStyle(Theme.t3)
                        }
                        if c.status == "revoked" {
                            Text(L10n.t("nmg.revoked", state.language)).font(.caption).foregroundStyle(Theme.red)
                        } else {
                            Text(c.authorized
                                 ? L10n.t("ncon.on", state.language)
                                 : L10n.t("ncon.needs.\(c.needs_first)", state.language))
                                .font(.caption)
                                .foregroundStyle(c.authorized ? Theme.green : Theme.t3)
                            HStack(spacing: 8) {
                                smallButton(L10n.t("ncon.collect", state.language)) { collect(c) }
                                if let cap = c.capabilities.first {
                                    smallButton("Invoke \(cap)") { invoke(c, cap) }
                                }
                                if !c.authorized && c.needs_first != "nothing" {
                                    smallButton(L10n.t("ncon.signin", state.language)) {
                                        signing = c.id; secret = ""
                                    }
                                }
                                // Uninstall. Until this round no shell had it.
                                smallButton(L10n.t("ncon.remove", state.language)) { revoke(c) }
                            }
                            if signing == c.id {
                                SecureField(L10n.t("ncon.secret", state.language), text: $secret)
                                    .textFieldStyle(.roundedBorder)
                                smallButton(L10n.t("ncon.signin", state.language)) { authorize(c) }
                            }
                        }
                    }.card()
                }
            }.padding(20)
        }
        .task { await load() }
    }

    private func load() async {
        guard let pid = state.pid, let token = state.token else { return }
        if let cat = try? await ApiClient.shared.appsCatalog() {
            flat = cat.app_providers.flatMap { p in
                p.apps.map { (key: "\(p.provider)/\($0.app)", provider: p.provider,
                              app: $0.app, label: $0.label, needs: $0.needs_first) }
            }
        }
        conns = (try? await ApiClient.shared.appConnections(id: pid, token: token)) ?? []
    }

    private func connect(_ provider: String, _ app: String) {
        guard let pid = state.pid, let token = state.token else { return }
        error = nil
        Task {
            do {
                _ = try await ApiClient.shared.appConnect(
                    id: pid, token: token, provider: provider, app: app)
                status = "connected \(provider)/\(app)"
            } catch { self.error = error.localizedDescription }
            await load()
        }
    }

    private func collect(_ c: AppConn) {
        guard let token = state.token else { return }
        Task {
            do {
                try await ApiClient.shared.appCollect(
                    cid: c.id, token: token, content: "sample context from \(c.app)")
                status = "collected from \(c.label) — it now feeds training"
            } catch { self.error = error.localizedDescription }
        }
    }

    /// The board, filtered. No `prefix` — a search that hides the answer
    /// below row twelve is not a search.
    private var shown: [(key: String, provider: String, app: String,
                         label: String, needs: String)] {
        let needle = find.trimmingCharacters(in: .whitespaces).lowercased()
        if needle.isEmpty { return Array(flat.prefix(24)) }
        return flat.filter {
            $0.label.lowercased().contains(needle)
                || $0.app.lowercased().contains(needle)
                || $0.provider.lowercased().contains(needle)
        }
    }

    private func revoke(_ c: AppConn) {
        guard let token = state.token else { return }
        Task {
            do { try await ApiClient.shared.appRevoke(cid: c.id, token: token) }
            catch { self.error = error.localizedDescription }
            await load()
        }
    }

    private func authorize(_ c: AppConn) {
        guard let token = state.token, !secret.isEmpty else { return }
        Task {
            do {
                _ = try await ApiClient.shared.appAuthorize(
                    cid: c.id, token: token, secret: secret)
                signing = nil; secret = ""
            } catch { self.error = error.localizedDescription }
            await load()
        }
    }

    private func invoke(_ c: AppConn, _ capability: String) {
        guard let token = state.token else { return }
        Task {
            do {
                let r = try await ApiClient.shared.appInvoke(
                    cid: c.id, token: token, capability: capability)
                status = r.result
            } catch { self.error = error.localizedDescription }
        }
    }
}

// MARK: shared

private func smallButton(_ label: String, _ action: @escaping () -> Void) -> some View {
    Button(label, action: action)
        .font(.caption.bold()).foregroundStyle(.white)
        .padding(.horizontal, 12).padding(.vertical, 8)
        .background(Theme.brandA).clipShape(Capsule())
}
