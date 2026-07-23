import SwiftUI

/// Connect: where the profile touches the outside world — social-platform
/// connections, the connected-apps catalog, and robotic embodiment — behind
/// one tab so the bar stays at five.
struct ConnectView: View {
    enum Tab: String, CaseIterable { case social = "Social", apps = "Apps", robots = "Robots" }
    @State private var tab: Tab = .social

    var body: some View {
        VStack(spacing: 0) {
            Picker("", selection: $tab) {
                ForEach(Tab.allCases, id: \.self) { Text($0.rawValue).tag($0) }
            }
            .pickerStyle(.segmented)
            .padding(.horizontal, 20).padding(.top, 12)

            switch tab {
            case .social: SocialSection()
            case .apps: AppsSection()
            case .robots: RobotsView()
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
                    Text("Social platforms").font(.headline).foregroundStyle(Theme.txt)
                    Text("Collect pulls the account's content in to grow the profile; publish runs the profile on the platform (moderated).")
                        .font(.caption).foregroundStyle(Theme.t2)
                    Picker("", selection: $platform) {
                        ForEach(platforms, id: \.self) { Text($0.capitalized).tag($0) }
                    }.pickerStyle(.menu).tint(Theme.brandA)
                    TextField("handle (optional)", text: $handle)
                        .foregroundStyle(Theme.txt).textInputAutocapitalization(.never)
                        .padding(10).background(Theme.scrBot)
                        .clipShape(RoundedRectangle(cornerRadius: 11))
                        .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                    HStack(spacing: 8) {
                        smallButton("Connect to collect") { connect("collect") }
                        smallButton("Connect to publish") { connect("publish") }
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
                             ? "\(c.collected) item(s) collected"
                             : "\(c.published) post(s) published")
                            .font(.caption).foregroundStyle(Theme.t2)
                        if c.status == "revoked" {
                            Text("revoked").font(.caption).foregroundStyle(Theme.red)
                        } else {
                            HStack(spacing: 8) {
                                if c.direction == "collect" {
                                    smallButton("Collect sample") { collect(c) }
                                } else {
                                    smallButton("Publish update") { publish(c) }
                                }
                                Button("Disconnect") { revoke(c) }
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
    @State private var flat: [(key: String, provider: String, app: String, label: String)] = []
    @State private var conns: [AppConn] = []
    @State private var status: String?
    @State private var error: String?

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Connected apps").font(.headline).foregroundStyle(Theme.txt)
                    Text("Apple, Google, Microsoft, and Canva apps the profile's agents can collect from, act through, and produce with.")
                        .font(.caption).foregroundStyle(Theme.t2)
                    ForEach(flat.prefix(12), id: \.key) { entry in
                        HStack {
                            Text(entry.label).font(.subheadline).foregroundStyle(Theme.txt)
                            Text(entry.provider).font(.caption).foregroundStyle(Theme.t3)
                            Spacer()
                            Button("Connect") { connect(entry.provider, entry.app) }
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
                            Text("revoked").font(.caption).foregroundStyle(Theme.red)
                        } else {
                            HStack(spacing: 8) {
                                smallButton("Collect") { collect(c) }
                                if let cap = c.capabilities.first {
                                    smallButton("Invoke \(cap)") { invoke(c, cap) }
                                }
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
            flat = cat.providers.flatMap { p in
                p.apps.map { (key: "\(p.provider)/\($0.app)", provider: p.provider,
                              app: $0.app, label: $0.label) }
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
