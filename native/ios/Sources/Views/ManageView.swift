import SwiftUI

/// Manage: the owner's console — settings, the profile's public reach
/// (@handle + placed QR beacons), its marketplace listing, and the
/// training-data license it is offered under.
struct ManageView: View {
    enum Tab: String, CaseIterable { case general = "General", summon = "Summon", market = "Market", packs = "Packs", license = "License" }
    @State private var tab: Tab = .general

    var body: some View {
        VStack(spacing: 0) {
            Picker("", selection: $tab) {
                ForEach(Tab.allCases, id: \.self) { Text($0.rawValue).tag($0) }
            }
            .pickerStyle(.segmented)
            .padding(.horizontal, 20).padding(.top, 12)

            switch tab {
            case .general: SettingsView()
            case .summon: SummonSection()
            case .market: MarketSection()
            case .packs: ScrollView { PacksSection().padding(20) }
            case .license: LicenseSection()
            }
        }
    }
}

// MARK: Summon — @handle and placed QR beacons

private struct SummonSection: View {
    @EnvironmentObject var state: AppState
    @State private var handle = ""
    @State private var claimed: String?
    @State private var beaconLabel = ""
    @State private var beaconLocation = ""
    @State private var beacons: [Beacon] = []
    @State private var lastPlaced: BeaconPlaced?
    @State private var ref = ""
    @State private var found: SummonResult?
    @State private var error: String?

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                VStack(alignment: .leading, spacing: 10) {
                    Text("@handle").font(.headline).foregroundStyle(Theme.txt)
                    Text("A unique name anyone can summon the profile by.")
                        .font(.caption).foregroundStyle(Theme.t2)
                    HStack(spacing: 8) {
                        TextField("handle", text: $handle)
                            .foregroundStyle(Theme.txt).textInputAutocapitalization(.never)
                            .padding(10).background(Theme.scrBot)
                            .clipShape(RoundedRectangle(cornerRadius: 11))
                            .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                        Button("Claim") { claim() }
                            .font(.caption.bold()).foregroundStyle(.white)
                            .padding(.horizontal, 12).padding(.vertical, 10)
                            .background(Theme.brandA).clipShape(Capsule())
                            .disabled(handle.isEmpty)
                    }
                    if let claimed {
                        Text("claimed \(claimed)").font(.caption).foregroundStyle(Theme.green)
                    }
                }.card()

                VStack(alignment: .leading, spacing: 10) {
                    Text("Beacons").font(.headline).foregroundStyle(Theme.txt)
                    Text("Leave the profile behind somewhere physical — a placed QR that summons it. Pick it back up any time.")
                        .font(.caption).foregroundStyle(Theme.t2)
                    TextField("label (e.g. Rosa's garden bench)", text: $beaconLabel)
                        .foregroundStyle(Theme.txt)
                        .padding(10).background(Theme.scrBot)
                        .clipShape(RoundedRectangle(cornerRadius: 11))
                        .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                    TextField("location (optional)", text: $beaconLocation)
                        .foregroundStyle(Theme.txt)
                        .padding(10).background(Theme.scrBot)
                        .clipShape(RoundedRectangle(cornerRadius: 11))
                        .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                    Button("Place beacon") { place() }
                        .font(.caption.bold()).foregroundStyle(.white)
                        .padding(.horizontal, 12).padding(.vertical, 10)
                        .background(Theme.brandA).clipShape(Capsule())
                        .disabled(beaconLabel.isEmpty)
                    if let p = lastPlaced {
                        Text("QR: \(p.qr_svg)").font(.caption2).foregroundStyle(Theme.t3)
                    }
                }.card()

                ForEach(beacons, id: \.id) { b in
                    VStack(alignment: .leading, spacing: 4) {
                        HStack {
                            Text(b.label).font(.subheadline.bold()).foregroundStyle(Theme.txt)
                            Spacer()
                            if b.active {
                                Button("Pick up") { pickUp(b) }
                                    .font(.caption.bold()).foregroundStyle(Theme.red)
                            } else {
                                Text("picked up").font(.caption).foregroundStyle(Theme.t3)
                            }
                        }
                        HStack {
                            if let loc = b.location { Text(loc).font(.caption).foregroundStyle(Theme.t2) }
                            Spacer()
                            Text("\(b.scans) scan(s)").font(.caption).foregroundStyle(Theme.t3)
                        }
                    }.card()
                }

                VStack(alignment: .leading, spacing: 10) {
                    Text("Try a summon").font(.headline).foregroundStyle(Theme.txt)
                    HStack(spacing: 8) {
                        TextField("@handle · #tag · beacon id", text: $ref)
                            .foregroundStyle(Theme.txt).textInputAutocapitalization(.never)
                            .padding(10).background(Theme.scrBot)
                            .clipShape(RoundedRectangle(cornerRadius: 11))
                            .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                        Button("Summon") { resolve() }
                            .font(.caption.bold()).foregroundStyle(.white)
                            .padding(.horizontal, 12).padding(.vertical, 10)
                            .background(Theme.brandA).clipShape(Capsule())
                            .disabled(ref.isEmpty)
                    }
                    if let found {
                        ForEach(cards(found), id: \.profile_id) { c in
                            VStack(alignment: .leading, spacing: 2) {
                                Text(c.display_name).font(.subheadline.bold()).foregroundStyle(Theme.txt)
                                if let h = c.handle { Text(h).font(.caption).foregroundStyle(Theme.brandA) }
                                Text(c.status).font(.caption).foregroundStyle(Theme.t2)
                                if let n = c.note { Text(n).font(.caption2).foregroundStyle(Theme.t3) }
                            }
                        }
                        if found.type == "beacon", let scans = found.scans {
                            Text("beacon \"\(found.label ?? "")\" · \(scans) scan(s)")
                                .font(.caption).foregroundStyle(Theme.t2)
                        }
                    }
                }.card()

                if let error { Text(error).font(.footnote).foregroundStyle(Theme.red) }
            }.padding(20)
        }
        .task { await load() }
    }

    private func cards(_ r: SummonResult) -> [SummonCard] {
        if let one = r.profile { return [one] }
        return r.profiles ?? []
    }

    private func load() async {
        guard let pid = state.pid else { return }
        beacons = (try? await ApiClient.shared.beacons(id: pid)) ?? []
    }

    private func claim() {
        guard let pid = state.pid else { return }
        error = nil
        Task {
            do {
                let r = try await ApiClient.shared.claimHandle(id: pid, handle: handle)
                claimed = r.handle
                handle = ""
            } catch { self.error = error.localizedDescription }
        }
    }

    private func place() {
        guard let pid = state.pid else { return }
        error = nil
        Task {
            do {
                lastPlaced = try await ApiClient.shared.placeBeacon(
                    id: pid, label: beaconLabel, location: beaconLocation)
                beaconLabel = ""; beaconLocation = ""
            } catch { self.error = error.localizedDescription }
            await load()
        }
    }

    private func pickUp(_ b: Beacon) {
        Task {
            try? await ApiClient.shared.pickUpBeacon(bid: b.id)
            await load()
        }
    }

    private func resolve() {
        error = nil; found = nil
        Task {
            do { found = try await ApiClient.shared.summon(ref: ref) }
            catch { self.error = error.localizedDescription }
        }
    }
}

// MARK: Market — list the profile; browse everything

private struct MarketSection: View {
    @EnvironmentObject var state: AppState
    @State private var title = ""
    @State private var blurb = ""
    @State private var tags = ""
    @State private var listings: [Listing] = []
    @State private var filterTag = ""
    @State private var status: String?
    @State private var error: String?

    // Quick-browse tags: the wellbeing starters first, then popular areas.
    private let quickTags = ["mental-health", "mood", "relationships",
                             "healthcare", "finance", "fitness", "food"]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                VStack(alignment: .leading, spacing: 10) {
                    Text("List this profile").font(.headline).foregroundStyle(Theme.txt)
                    Text("Share it on the marketplace — discoverable by #tag summons too.")
                        .font(.caption).foregroundStyle(Theme.t2)
                    TextField("title", text: $title)
                        .foregroundStyle(Theme.txt)
                        .padding(10).background(Theme.scrBot)
                        .clipShape(RoundedRectangle(cornerRadius: 11))
                        .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                    TextField("blurb (optional)", text: $blurb)
                        .foregroundStyle(Theme.txt)
                        .padding(10).background(Theme.scrBot)
                        .clipShape(RoundedRectangle(cornerRadius: 11))
                        .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                    TextField("tags, comma separated", text: $tags)
                        .foregroundStyle(Theme.txt).textInputAutocapitalization(.never)
                        .padding(10).background(Theme.scrBot)
                        .clipShape(RoundedRectangle(cornerRadius: 11))
                        .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                    Button("Create listing") { create() }
                        .font(.caption.bold()).foregroundStyle(.white)
                        .padding(.horizontal, 12).padding(.vertical, 10)
                        .background(Theme.brandA).clipShape(Capsule())
                        .disabled(title.isEmpty)
                }.card()

                if let error { Text(error).font(.footnote).foregroundStyle(Theme.red) }
                if let status { Text(status).font(.caption).foregroundStyle(Theme.green) }

                VStack(alignment: .leading, spacing: 8) {
                    Text("Wellbeing & quick browse")
                        .font(.caption.bold()).foregroundStyle(Theme.txt)
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: 8) {
                            ForEach(quickTags, id: \.self) { tag in
                                Button("#\(tag)") {
                                    filterTag = tag
                                    Task { await load() }
                                }
                                .font(.caption)
                                .foregroundStyle(filterTag == tag ? .white : Theme.txt)
                                .padding(.horizontal, 10).padding(.vertical, 6)
                                .background(filterTag == tag ? Theme.brandA : Theme.scrBot)
                                .clipShape(Capsule())
                                .overlay(Capsule().stroke(Theme.line, lineWidth: 1))
                            }
                        }
                    }
                    Text("The wellbeing starters — Dr. Lena Whitcomb (anxiety), Dr. Marcus Adeyemi (mood), Dr. Priya Nair (relationships) — offer education and support, never a substitute for professional care. In crisis, call or text 988.")
                        .font(.caption2).foregroundStyle(Theme.t3)
                }.card()

                HStack(spacing: 8) {
                    TextField("filter by tag", text: $filterTag)
                        .foregroundStyle(Theme.txt).textInputAutocapitalization(.never)
                        .padding(10).background(Theme.scrBot)
                        .clipShape(RoundedRectangle(cornerRadius: 11))
                        .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                    Button("Browse") { Task { await load() } }
                        .font(.caption.bold()).foregroundStyle(.white)
                        .padding(.horizontal, 12).padding(.vertical, 10)
                        .background(Theme.brandA).clipShape(Capsule())
                }

                ForEach(listings, id: \.id) { l in
                    VStack(alignment: .leading, spacing: 4) {
                        HStack {
                            Text(l.title).font(.subheadline.bold()).foregroundStyle(Theme.txt)
                            Spacer()
                            Text(l.kind).font(.caption).foregroundStyle(Theme.brandA)
                        }
                        if let b = l.blurb { Text(b).font(.caption).foregroundStyle(Theme.t2) }
                        HStack {
                            if !l.tags.isEmpty {
                                Text(l.tags.map { "#\($0)" }.joined(separator: " "))
                                    .font(.caption2).foregroundStyle(Theme.t3)
                            }
                            Spacer()
                            if l.profile_id == state.pid {
                                Button("Remove") { remove(l) }
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
        listings = (try? await ApiClient.shared.listings(tag: filterTag)) ?? []
    }

    private func create() {
        guard let pid = state.pid else { return }
        error = nil; status = nil
        Task {
            do {
                let tagList = tags.split(separator: ",")
                    .map { $0.trimmingCharacters(in: .whitespaces) }
                    .filter { !$0.isEmpty }
                _ = try await ApiClient.shared.createListing(
                    kind: "profile", title: title, blurb: blurb, tags: tagList,
                    area: nil, providerName: state.displayName, profileId: pid)
                status = "listed — summonable by tag"
                title = ""; blurb = ""; tags = ""
            } catch { self.error = error.localizedDescription }
            await load()
        }
    }

    private func remove(_ l: Listing) {
        Task {
            try? await ApiClient.shared.removeListing(lid: l.id)
            await load()
        }
    }
}

// MARK: License — offer the profile's expertise; see and revoke grants

private struct LicenseSection: View {
    @EnvironmentObject var state: AppState
    @State private var kind = "consult"
    @State private var price = ""
    @State private var terms = ""
    @State private var offer: LicenseOffer?
    @State private var grants: [LicenseGrant] = []
    @State private var error: String?

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                VStack(alignment: .leading, spacing: 10) {
                    Text("License this expertise").font(.headline).foregroundStyle(Theme.txt)
                    Text("consult = use as-is · finetune / clone = buyers may derive their own agent (provenance recorded). Buyers acquire with their own verified identity, outside this app.")
                        .font(.caption).foregroundStyle(Theme.t2)
                    Picker("", selection: $kind) {
                        ForEach(["consult", "finetune", "clone"], id: \.self) {
                            Text($0).tag($0)
                        }
                    }.pickerStyle(.segmented)
                    TextField("price (USD)", text: $price)
                        .keyboardType(.decimalPad)
                        .foregroundStyle(Theme.txt)
                        .padding(10).background(Theme.scrBot)
                        .clipShape(RoundedRectangle(cornerRadius: 11))
                        .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                    TextField("terms (optional)", text: $terms)
                        .foregroundStyle(Theme.txt)
                        .padding(10).background(Theme.scrBot)
                        .clipShape(RoundedRectangle(cornerRadius: 11))
                        .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                    HStack(spacing: 8) {
                        Button("Set offer") { set() }
                            .font(.caption.bold()).foregroundStyle(.white)
                            .padding(.horizontal, 12).padding(.vertical, 10)
                            .background(Theme.brandA).clipShape(Capsule())
                        if offer != nil {
                            Button("Unlist") { unlist() }
                                .font(.caption).foregroundStyle(Theme.red)
                        }
                    }
                    if let offer {
                        Text("offered: \(offer.kind) · \(offer.currency) \(String(format: "%.2f", offer.price))\(offer.allow_derivatives ? " · derivatives allowed" : "")")
                            .font(.caption).foregroundStyle(Theme.green)
                    }
                }.card()

                if let error { Text(error).font(.footnote).foregroundStyle(Theme.red) }

                if !grants.isEmpty {
                    Text("Grants").font(.headline).foregroundStyle(Theme.txt)
                }
                ForEach(grants, id: \.id) { g in
                    VStack(alignment: .leading, spacing: 4) {
                        HStack {
                            Text("\(g.kind) → \(g.buyer_id)")
                                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
                            Spacer()
                            if g.revoked {
                                Text("revoked").font(.caption).foregroundStyle(Theme.red)
                            } else {
                                Button("Revoke") { revoke(g) }
                                    .font(.caption.bold()).foregroundStyle(Theme.red)
                            }
                        }
                        if let d = g.derived_profile_id {
                            Text("derived agent: \(d)").font(.caption).foregroundStyle(Theme.t2)
                        }
                    }.card()
                }
            }.padding(20)
        }
        .task { await load() }
    }

    private func load() async {
        guard let pid = state.pid, let token = state.token else { return }
        offer = try? await ApiClient.shared.license(id: pid)
        grants = (try? await ApiClient.shared.licenseGrants(id: pid, token: token)) ?? []
    }

    private func set() {
        guard let pid = state.pid, let token = state.token else { return }
        error = nil
        Task {
            do {
                offer = try await ApiClient.shared.setLicense(
                    id: pid, token: token, kind: kind,
                    price: Double(price) ?? 0, terms: terms)
            } catch { self.error = error.localizedDescription }
        }
    }

    private func unlist() {
        guard let pid = state.pid, let token = state.token else { return }
        Task {
            try? await ApiClient.shared.unlistLicense(id: pid, token: token)
            offer = nil
        }
    }

    private func revoke(_ g: LicenseGrant) {
        guard let token = state.token else { return }
        Task {
            try? await ApiClient.shared.revokeLicense(gid: g.id, token: token)
            await load()
        }
    }
}
