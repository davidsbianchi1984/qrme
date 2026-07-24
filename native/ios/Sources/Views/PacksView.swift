import SwiftUI

/// Knowledge packs: downloadable clusters of curated expertise on the
/// marketplace. Installing one grows this profile's knowledge base — the
/// items become source material that grounds every reply (and shows in its
/// provenance). Free packs download; priced packs are bought explicitly.
struct PacksSection: View {
    @EnvironmentObject var state: AppState
    @State private var catalog: [Pack] = []
    @State private var installed: Set<String> = []
    @State private var industry = ""
    @State private var status: String?
    @State private var error: String?
    @State private var busyPack: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            VStack(alignment: .leading, spacing: 8) {
                Text("Knowledge packs").font(.headline).foregroundStyle(Theme.txt)
                Text("Make this profile smarter: a pack's curated items join its source material, grounding what it knows — and every reply's provenance shows the pack honestly.")
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

            if let error { Text(error).font(.footnote).foregroundStyle(Theme.red) }
            if let status { Text(status).font(.caption).foregroundStyle(Theme.green) }

            ForEach(catalog, id: \.id) { pack in
                VStack(alignment: .leading, spacing: 6) {
                    HStack {
                        Text(pack.title).font(.subheadline.bold()).foregroundStyle(Theme.txt)
                        Spacer()
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
                    HStack {
                        Spacer()
                        if installed.contains(pack.id) {
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

    private func load() async {
        catalog = (try? await ApiClient.shared.packs(
            industry: industry.trimmingCharacters(in: .whitespaces))) ?? []
        if let pid = state.pid, let token = state.token {
            let mine = (try? await ApiClient.shared.installedPacks(
                pid: pid, token: token)) ?? []
            installed = Set(mine.map(\.id))
        }
    }

    private func install(_ pack: Pack) {
        guard let pid = state.pid, let token = state.token else { return }
        busyPack = pack.id; error = nil; status = nil
        Task {
            do {
                // Buying a priced pack is an explicit tap on the priced
                // button — that tap is the accept_price consent.
                let r = try await ApiClient.shared.installPack(
                    packId: pack.id, pid: pid, token: token,
                    acceptPrice: !pack.free)
                status = pack.free
                    ? "downloaded — \(r.installed_items) items now ground this profile"
                    : String(format: "bought for %.2f — %d items now ground this profile",
                             r.price_paid, r.installed_items)
            } catch { self.error = error.localizedDescription }
            busyPack = nil
            await load()
        }
    }

    private func uninstall(_ pack: Pack) {
        guard let pid = state.pid, let token = state.token else { return }
        Task {
            try? await ApiClient.shared.uninstallPack(
                packId: pack.id, pid: pid, token: token)
            status = "removed — the knowledge base shrank back"
            await load()
        }
    }
}
