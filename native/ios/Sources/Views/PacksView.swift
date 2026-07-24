import SwiftUI

/// Knowledge packs: downloadable clusters of curated expertise on the
/// marketplace. Installing one grows this profile's knowledge base — the
/// items become source material that grounds every reply (and shows in its
/// provenance). Free packs download; priced packs are bought explicitly.
struct PacksSection: View {
    @EnvironmentObject var state: AppState
    @State private var catalog: [Pack] = []
    @State private var registries: [PackRegistry] = []
    @State private var installed: [String: String] = [:]  // pack id -> robot id ("" = profile)
    @State private var industry = ""
    @State private var status: String?
    @State private var error: String?
    @State private var busyPack: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            VStack(alignment: .leading, spacing: 8) {
                Text("Knowledge packs").font(.headline).foregroundStyle(Theme.txt)
                Text("Make this profile smarter: a pack's curated items join its source material, grounding what it knows — and every reply's provenance shows the pack honestly. 🤖 Robot task packs teach the body this profile embodies new commandable tasks, capability-checked at install.")
                    .font(.caption).foregroundStyle(Theme.t2)
                HStack(spacing: 8) {
                    TextField("filter by industry (e.g. finance)", text: $industry)
                        .foregroundStyle(Theme.txt).textInputAutocapitalization(.never)
                        .padding(10).background(Theme.scrBot)
                        .clipShape(RoundedRectangle(cornerRadius: 11))
                        .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                    Button("Browse") { Task { await load() } }
                        .font(.caption.bold()).foregroundStyle(.white)
                        .padding(.horizontal, 12).padding(.vertical, 10)
                        .background(Theme.brandA).clipShape(Capsule())
                }
            }.card()

            VStack(alignment: .leading, spacing: 8) {
                Text("Pack sources").font(.subheadline.bold()).foregroundStyle(Theme.txt)
                Text("Federated mod storefronts — sync a source and its catalog joins the marketplace, origin on every label.")
                    .font(.caption2).foregroundStyle(Theme.t3)
                ForEach(registries, id: \.key) { reg in
                    HStack(spacing: 8) {
                        VStack(alignment: .leading, spacing: 1) {
                            Text(reg.name).font(.caption.bold()).foregroundStyle(Theme.brandA)
                            Text(reg.tagline).font(.caption2).foregroundStyle(Theme.t2)
                            Text("\(reg.synced)/\(reg.available) packs synced")
                                .font(.caption2).foregroundStyle(Theme.t3)
                        }
                        Spacer()
                        Button(reg.synced >= reg.available ? "Synced" : "Sync") {
                            sync(reg)
                        }
                        .font(.caption.bold())
                        .foregroundStyle(reg.synced >= reg.available ? Theme.green : .white)
                        .padding(.horizontal, 12).padding(.vertical, 8)
                        .background(reg.synced >= reg.available
                                    ? Theme.green.opacity(0.16) : Theme.brandA)
                        .clipShape(Capsule())
                        .disabled(reg.synced >= reg.available)
                    }
                }
            }.card()

            if let error { Text(error).font(.footnote).foregroundStyle(Theme.red) }
            if let status { Text(status).font(.caption).foregroundStyle(Theme.green) }

            ForEach(catalog, id: \.id) { pack in
                VStack(alignment: .leading, spacing: 6) {
                    HStack {
                        Text(pack.title).font(.subheadline.bold()).foregroundStyle(Theme.txt)
                        Spacer()
                        if pack.audience == "robot" {
                            Text("🤖 ROBOT TASKS").font(.caption2.bold())
                                .padding(.horizontal, 7).padding(.vertical, 3)
                                .background(Theme.brandA.opacity(0.16))
                                .foregroundStyle(Theme.brandA)
                                .clipShape(Capsule())
                        }
                        Text(pack.free ? "FREE"
                             : String(format: "%.2f %@", pack.price, pack.currency))
                            .font(.caption2.bold())
                            .padding(.horizontal, 7).padding(.vertical, 3)
                            .background((pack.free ? Theme.green : Theme.amber).opacity(0.16))
                            .foregroundStyle(pack.free ? Theme.green : Theme.amber)
                            .clipShape(Capsule())
                    }
                    if let blurb = pack.blurb {
                        Text(blurb).font(.caption).foregroundStyle(Theme.t2)
                    }
                    Text("#\(pack.industry) · \(pack.items) items · \(pack.installs) installs · \(pack.publisher)")
                        .font(.caption2).foregroundStyle(Theme.t3)
                    if let url = pack.origin_url {
                        Text("from \(url)").font(.caption2).foregroundStyle(Theme.brandA)
                    }
                    HStack {
                        Spacer()
                        if installed.keys.contains(pack.id) {
                            Text("Installed").font(.caption.bold()).foregroundStyle(Theme.green)
                            Button("Remove") { uninstall(pack) }
                                .font(.caption).foregroundStyle(Theme.red)
                        } else {
                            Button(pack.free ? "Download"
                                   : String(format: "Buy %.2f %@", pack.price, pack.currency)) {
                                install(pack)
                            }
                            .font(.caption.bold()).foregroundStyle(.white)
                            .padding(.horizontal, 12).padding(.vertical, 8)
                            .background(pack.free ? Theme.green : Theme.brandA)
                            .clipShape(Capsule())
                            .disabled(busyPack == pack.id)
                        }
                    }
                }.card()
            }
        }
        .task { await load() }
    }

    private func sync(_ reg: PackRegistry) {
        Task {
            do {
                try await ApiClient.shared.syncRegistry(key: reg.key)
                status = "\(reg.name) synced — its packs joined the marketplace"
            } catch { self.error = error.localizedDescription }
            await load()
        }
    }

    private func load() async {
        registries = (try? await ApiClient.shared.packRegistries()) ?? []
        catalog = (try? await ApiClient.shared.packs(
            industry: industry.trimmingCharacters(in: .whitespaces))) ?? []
        if let pid = state.pid, let token = state.token {
            let mine = (try? await ApiClient.shared.installedPacks(
                pid: pid, token: token)) ?? []
            installed = Dictionary(uniqueKeysWithValues:
                mine.map { ($0.id, $0.robot_id ?? "") })
        }
    }

    private func install(_ pack: Pack) {
        guard let pid = state.pid, let token = state.token else { return }
        busyPack = pack.id; error = nil; status = nil
        Task {
            do {
                // Robot task packs install onto the profile's bound body.
                var robotId: String? = nil
                if pack.audience == "robot" {
                    let robots = try await ApiClient.shared.robots(
                        id: pid, token: token)
                    guard let first = robots.first else {
                        error = "bind a robot first (Robots tab) — task packs install onto a body"
                        busyPack = nil
                        return
                    }
                    robotId = first.id
                }
                // Buying a priced pack is an explicit tap on the priced
                // button — that tap is the accept_price consent.
                let r = try await ApiClient.shared.installPack(
                    packId: pack.id, pid: pid, token: token,
                    acceptPrice: !pack.free, robotId: robotId)
                let what = pack.audience == "robot"
                    ? "tasks the body can now be commanded with"
                    : "items now grounding this profile"
                status = pack.free
                    ? "downloaded — \(r.count) \(what)"
                    : String(format: "bought for %.2f — %d %@",
                             r.price_paid, r.count, what)
            } catch { self.error = error.localizedDescription }
            busyPack = nil
            await load()
        }
    }

    private func uninstall(_ pack: Pack) {
        guard let pid = state.pid, let token = state.token else { return }
        Task {
            if let robotId = installed[pack.id], !robotId.isEmpty {
                try? await ApiClient.shared.uninstallRobotPack(
                    packId: pack.id, robotId: robotId, token: token)
                status = "removed — the body's tasks were revoked"
            } else {
                try? await ApiClient.shared.uninstallPack(
                    packId: pack.id, pid: pid, token: token)
                status = "removed — the knowledge base shrank back"
            }
            await load()
        }
    }
}
