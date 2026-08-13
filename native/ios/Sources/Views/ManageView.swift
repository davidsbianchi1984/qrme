import SwiftUI

/// Manage: the owner's console — settings, the profile's public reach
/// (@handle + placed QR beacons), its marketplace listing, and the
/// training-data license it is offered under.
struct ManageView: View {
    /// The raw values are the API-side names of the sections; the words a
    /// person reads come from the table. They used to be the same string,
    /// which is how this console ended up with an untranslated tab bar of its
    /// own sitting behind the translated one.
    enum Tab: String, CaseIterable {
        case general, summon, market, packs, gaming, license, earnings,
             signatures, voice, desk, counter, trade, deals

        var key: String {
            switch self {
            case .earnings: return "nmg.t.earn"
            case .signatures: return "nmg.t.sign"
            default: return "nmg.t.\(rawValue)"
            }
        }
    }
    @EnvironmentObject var state: AppState
    @State private var tab: Tab = .general

    var body: some View {
        VStack(spacing: 0) {
            Picker("", selection: $tab) {
                ForEach(Tab.allCases, id: \.self) { Text(L10n.t($0.key, state.language)).tag($0) }
            }
            .pickerStyle(.menu).tint(Theme.brandA)
            .padding(.horizontal, 20).padding(.top, 12)

            switch tab {
            case .general: SettingsView()
            case .summon: SummonSection()
            case .market: MarketSection()
            case .packs: ScrollView { PacksSection().padding(20) }
            case .gaming: GamingSection()
            case .license: ManageLicenseSection()
            case .earnings: EarningsSection()
            case .signatures: SignatureSection()
            case .voice: VoiceSection()
            case .desk: DeskSection()
            case .counter: CounterSection()
            case .trade: TradeSection()
            case .deals: DealsSection()
            }
        }
    }
}

// MARK: Earnings — the creator's statement over the ledger

private struct EarningsSection: View {
    @EnvironmentObject var state: AppState
    @State private var statement: EarningsStatement?
    @State private var receipt: PayoutReceipt?
    @State private var error: String?

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                VStack(alignment: .leading, spacing: 10) {
                    Text(L10n.t("nmg.earnings", state.language)).font(.headline).foregroundStyle(Theme.txt)
                    Text(L10n.t("nmg.earnings.sub", state.language))
                        .font(.caption).foregroundStyle(Theme.t2)
                    if let s = statement {
                        HStack(spacing: 12) {
                            stat(L10n.t("nmg.accrued", state.language), s.totals.accrued, s.currency, Theme.green)
                            stat(L10n.t("nmg.paid", state.language), s.totals.paid, s.currency, Theme.t2)
                            stat(L10n.t("nmg.lifetime", state.language), s.totals.lifetime, s.currency, Theme.brandA)
                        }
                        if !s.totals.by_kind.isEmpty {
                            Text(s.totals.by_kind.sorted { $0.key < $1.key }
                                .map { "\($0.key.replacingOccurrences(of: "_", with: " ")): \(money($0.value, s.currency))" }
                                .joined(separator: " · "))
                                .font(.caption2).foregroundStyle(Theme.t3)
                        }
                        Button(L10n.t("nmg.payout.request", state.language)) { payout() }
                            .font(.caption.bold()).foregroundStyle(.white)
                            .padding(.horizontal, 12).padding(.vertical, 9)
                            .background(Theme.brandA).clipShape(Capsule())
                            .disabled(s.totals.accrued <= 0)
                        if let receipt {
                            Text(L10n.fill("nmg.payout.done", state.language,
                                           ["id": receipt.payout_id,
                                            "total": money(receipt.total_amount, s.currency),
                                            "n": "\(receipt.entries)"]))
                                .font(.caption).foregroundStyle(Theme.green)
                        }
                    } else {
                        ProgressView().tint(Theme.brandA)
                    }
                }.card()

                if let s = statement, !s.entries.isEmpty {
                    VStack(alignment: .leading, spacing: 8) {
                        Text(L10n.t("nmg.ledger", state.language)).font(.headline).foregroundStyle(Theme.txt)
                        ForEach(s.entries.prefix(20)) { e in
                            HStack {
                                VStack(alignment: .leading, spacing: 1) {
                                    Text(e.kind.replacingOccurrences(of: "_", with: " "))
                                        .font(.caption.bold()).foregroundStyle(Theme.txt)
                                    if let memo = e.memo {
                                        Text(memo).font(.caption2)
                                            .foregroundStyle(Theme.t3).lineLimit(1)
                                    }
                                }
                                Spacer()
                                VStack(alignment: .trailing, spacing: 1) {
                                    Text(money(e.amount, s.currency))
                                        .font(.caption.bold()).monospacedDigit()
                                        .foregroundStyle(e.status == "paid" ? Theme.t2 : Theme.green)
                                    Text(e.status).font(.caption2)
                                        .foregroundStyle(Theme.t3)
                                }
                            }
                            .padding(.vertical, 3)
                        }
                    }.card()
                }
                if let error { Text(error).font(.footnote).foregroundStyle(Theme.red) }
            }.padding(20)
        }
        .task { await load() }
    }

    private func stat(_ label: String, _ value: Double, _ currency: String,
                      _ tint: Color) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(money(value, currency)).font(.subheadline.bold())
                .foregroundStyle(tint).monospacedDigit()
            Text(label).font(.caption2).foregroundStyle(Theme.t2)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }

    private func money(_ v: Double, _ c: String) -> String {
        "\(c == "USD" ? "$" : c + " ")" + String(format: "%.2f", v)
    }

    private func load() async {
        guard let pid = state.pid, let token = state.token else { return }
        statement = try? await ApiClient.shared.earnings(id: pid, token: token)
    }

    private func payout() {
        guard let pid = state.pid, let token = state.token else { return }
        error = nil
        Task {
            do {
                receipt = try await ApiClient.shared.requestPayout(id: pid, token: token)
                await load()
            } catch { self.error = error.localizedDescription }
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
    @State private var scanning = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                // The other half of placing a beacon: finding one. Opens the
                // camera and draws the profile onto the sticker rather than
                // sending anyone to a URL.
                Button { scanning = true } label: {
                    VStack(spacing: 4) {
                        HStack(spacing: 8) {
                            Image(systemName: "viewfinder")
                            Text(L10n.t("nmg.beacon.scan", state.language)).font(.subheadline.weight(.semibold))
                        }
                        Text(L10n.t("nmg.beacon.scan.sub", state.language))
                            .font(.caption2).multilineTextAlignment(.center)
                    }
                    .frame(maxWidth: .infinity).padding(12)
                    .background(Theme.brand)
                    .clipShape(RoundedRectangle(cornerRadius: 12))
                    .foregroundStyle(.white)
                }
                .fullScreenCover(isPresented: $scanning) {
                    ZStack(alignment: .topTrailing) {
                        BeaconScannerView()
                        Button(L10n.t("nmg.done", state.language)) { scanning = false }
                            .padding().foregroundStyle(.white)
                    }
                }

                VStack(alignment: .leading, spacing: 10) {
                    Text(L10n.t("nmg.handle", state.language)).font(.headline).foregroundStyle(Theme.txt)
                    Text(L10n.t("nmg.handle.sub", state.language))
                        .font(.caption).foregroundStyle(Theme.t2)
                    HStack(spacing: 8) {
                        TextField(L10n.t("nmg.handle.ph", state.language), text: $handle)
                            .foregroundStyle(Theme.txt).textInputAutocapitalization(.never)
                            .padding(10).background(Theme.scrBot)
                            .clipShape(RoundedRectangle(cornerRadius: 11))
                            .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                        Button(L10n.t("nmg.claim", state.language)) { claim() }
                            .font(.caption.bold()).foregroundStyle(.white)
                            .padding(.horizontal, 12).padding(.vertical, 10)
                            .background(Theme.brandA).clipShape(Capsule())
                            .disabled(handle.isEmpty)
                    }
                    if let claimed {
                        Text(L10n.fill("nmg.claimed", state.language, ["handle": claimed])).font(.caption).foregroundStyle(Theme.green)
                    }
                }.card()

                VStack(alignment: .leading, spacing: 10) {
                    Text(L10n.t("nmg.beacons", state.language)).font(.headline).foregroundStyle(Theme.txt)
                    Text(L10n.t("nmg.beacons.sub", state.language))
                        .font(.caption).foregroundStyle(Theme.t2)
                    TextField(L10n.t("nmg.beacon.label.ph", state.language), text: $beaconLabel)
                        .foregroundStyle(Theme.txt)
                        .padding(10).background(Theme.scrBot)
                        .clipShape(RoundedRectangle(cornerRadius: 11))
                        .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                    TextField(L10n.t("nmg.beacon.loc.ph", state.language), text: $beaconLocation)
                        .foregroundStyle(Theme.txt)
                        .padding(10).background(Theme.scrBot)
                        .clipShape(RoundedRectangle(cornerRadius: 11))
                        .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                    Button(L10n.t("nmg.beacon.place", state.language)) { place() }
                        .font(.caption.bold()).foregroundStyle(.white)
                        .padding(.horizontal, 12).padding(.vertical, 10)
                        .background(Theme.brandA).clipShape(Capsule())
                        .disabled(beaconLabel.isEmpty)
                    if let p = lastPlaced {
                        Text(L10n.fill("nmg.qr", state.language, ["svg": p.qr_svg])).font(.caption2).foregroundStyle(Theme.t3)
                    }
                }.card()

                ForEach(beacons, id: \.id) { b in
                    VStack(alignment: .leading, spacing: 4) {
                        HStack {
                            Text(b.label).font(.subheadline.bold()).foregroundStyle(Theme.txt)
                            Spacer()
                            if b.active {
                                Button(L10n.t("nmg.beacon.pickup", state.language)) { pickUp(b) }
                                    .font(.caption.bold()).foregroundStyle(Theme.red)
                            } else {
                                Text(L10n.t("nmg.beacon.pickedup", state.language)).font(.caption).foregroundStyle(Theme.t3)
                            }
                        }
                        HStack {
                            if let loc = b.location { Text(loc).font(.caption).foregroundStyle(Theme.t2) }
                            Spacer()
                            Text(L10n.fill("nmg.beacon.scans", state.language, ["n": "\(b.scans)"])).font(.caption).foregroundStyle(Theme.t3)
                        }
                    }.card()
                }

                VStack(alignment: .leading, spacing: 10) {
                    Text(L10n.t("nmg.trysummon", state.language)).font(.headline).foregroundStyle(Theme.txt)
                    HStack(spacing: 8) {
                        TextField(L10n.t("nmg.summon.ph", state.language), text: $ref)
                            .foregroundStyle(Theme.txt).textInputAutocapitalization(.never)
                            .padding(10).background(Theme.scrBot)
                            .clipShape(RoundedRectangle(cornerRadius: 11))
                            .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                        Button(L10n.t("nmg.t.summon", state.language)) { resolve() }
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
                            Text(L10n.fill("nmg.found.beacon", state.language,
                                 ["label": found.label ?? "", "n": "\(scans)"]))
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
                let r = try await ApiClient.shared.claimHandle(
                    id: pid, handle: handle,
                    token: state.token ?? "")
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
                    Text(L10n.t("nmg.list", state.language)).font(.headline).foregroundStyle(Theme.txt)
                    Text(L10n.t("nmg.list.sub", state.language))
                        .font(.caption).foregroundStyle(Theme.t2)
                    TextField(L10n.t("nmg.title.ph", state.language), text: $title)
                        .foregroundStyle(Theme.txt)
                        .padding(10).background(Theme.scrBot)
                        .clipShape(RoundedRectangle(cornerRadius: 11))
                        .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                    TextField(L10n.t("nmg.blurb.ph", state.language), text: $blurb)
                        .foregroundStyle(Theme.txt)
                        .padding(10).background(Theme.scrBot)
                        .clipShape(RoundedRectangle(cornerRadius: 11))
                        .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                    TextField(L10n.t("nmg.tags.ph", state.language), text: $tags)
                        .foregroundStyle(Theme.txt).textInputAutocapitalization(.never)
                        .padding(10).background(Theme.scrBot)
                        .clipShape(RoundedRectangle(cornerRadius: 11))
                        .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                    Button(L10n.t("nmg.create", state.language)) { create() }
                        .font(.caption.bold()).foregroundStyle(.white)
                        .padding(.horizontal, 12).padding(.vertical, 10)
                        .background(Theme.brandA).clipShape(Capsule())
                        .disabled(title.isEmpty)
                }.card()

                if let error { Text(error).font(.footnote).foregroundStyle(Theme.red) }
                if let status { Text(status).font(.caption).foregroundStyle(Theme.green) }

                VStack(alignment: .leading, spacing: 8) {
                    Text(L10n.t("nmg.wellbeing.head", state.language))
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
                    // Was "In crisis, call or text 988." — a US number, shown to readers
                    // in ten languages. The sibling product settled this: name the
                    // category, not a number that only works in one country.
                    Text(L10n.t("nmg.wellbeing", state.language))
                        .font(.caption2).foregroundStyle(Theme.t3)
                }.card()

                HStack(spacing: 8) {
                    TextField(L10n.t("nmg.filter.tag", state.language), text: $filterTag)
                        .foregroundStyle(Theme.txt).textInputAutocapitalization(.never)
                        .padding(10).background(Theme.scrBot)
                        .clipShape(RoundedRectangle(cornerRadius: 11))
                        .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                    Button(L10n.t("nmg.browse", state.language)) { Task { await load() } }
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
                                Button(L10n.t("nmg.remove", state.language)) { remove(l) }
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

private struct ManageLicenseSection: View {
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
                    Text(L10n.t("nmg.license", state.language)).font(.headline).foregroundStyle(Theme.txt)
                    Text(L10n.t("nmg.license.sub", state.language))
                        .font(.caption).foregroundStyle(Theme.t2)
                    Text(L10n.t("nmg.license.kind", state.language))
                        .font(.caption2).foregroundStyle(Theme.t2)
                    Picker("", selection: $kind) {
                        ForEach(["consult", "finetune", "clone"], id: \.self) {
                            Text($0).tag($0)
                        }
                    }.pickerStyle(.segmented)
                    TextField(L10n.t("nmg.price.ph", state.language), text: $price)
                        .keyboardType(.decimalPad)
                        .foregroundStyle(Theme.txt)
                        .padding(10).background(Theme.scrBot)
                        .clipShape(RoundedRectangle(cornerRadius: 11))
                        .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                    TextField(L10n.t("nmg.terms.ph", state.language), text: $terms)
                        .foregroundStyle(Theme.txt)
                        .padding(10).background(Theme.scrBot)
                        .clipShape(RoundedRectangle(cornerRadius: 11))
                        .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                    HStack(spacing: 8) {
                        Button(L10n.t("nmg.setoffer", state.language)) { set() }
                            .font(.caption.bold()).foregroundStyle(.white)
                            .padding(.horizontal, 12).padding(.vertical, 10)
                            .background(Theme.brandA).clipShape(Capsule())
                        if offer != nil {
                            Button(L10n.t("nmg.unlist", state.language)) { unlist() }
                                .font(.caption).foregroundStyle(Theme.red)
                        }
                    }
                    if let offer {
                        Text(L10n.fill(offer.allow_derivatives
                                       ? "nmg.offered.derivatives" : "nmg.offered", state.language,
                                       ["kind": offer.kind, "currency": offer.currency,
                                        "price": String(format: "%.2f", offer.price)]))
                            .font(.caption).foregroundStyle(Theme.green)
                    }
                }.card()

                if let error { Text(error).font(.footnote).foregroundStyle(Theme.red) }

                if !grants.isEmpty {
                    Text(L10n.t("nmg.grants", state.language)).font(.headline).foregroundStyle(Theme.txt)
                }
                ForEach(grants, id: \.id) { g in
                    VStack(alignment: .leading, spacing: 4) {
                        HStack {
                            Text("\(g.kind) → \(g.buyer_id)")
                                .font(.subheadline.bold()).foregroundStyle(Theme.txt)
                            Spacer()
                            if g.revoked {
                                Text(L10n.t("nmg.revoked", state.language)).font(.caption).foregroundStyle(Theme.red)
                            } else {
                                Button(L10n.t("nmg.revoke", state.language)) { revoke(g) }
                                    .font(.caption.bold()).foregroundStyle(Theme.red)
                            }
                        }
                        if let d = g.derived_profile_id {
                            Text(L10n.fill("nmg.derived", state.language, ["id": d])).font(.caption).foregroundStyle(Theme.t2)
                        }
                        if let m = g.manifest {
                            Text(L10n.t("nmg.manifest.carried", state.language)
                                 + ": " + m.carried.keys.sorted().joined(separator: ", "))
                                .font(.caption).foregroundStyle(Theme.t2)
                            Text(L10n.t("nmg.manifest.withheld", state.language)
                                 + ": " + m.withholdings.map(\.item).joined(separator: ", "))
                                .font(.caption).foregroundStyle(Theme.t2)
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


// MARK: Signatures — a passkey assertion instead of the app's own say-so

/// Bridges the shared app state into `SignatureView`, which needs an account
/// token: a signature is attributed to the enrolled account, never to a value
/// the client supplies.
private struct SignatureSection: View {
    @EnvironmentObject private var state: AppState

    var body: some View {
        if let pid = state.pid, let token = state.token {
            NavigationStack { SignatureView(profileId: pid, token: token) }
        } else {
            VStack(spacing: 8) {
                Text(L10n.t("nmg.needprofile", state.language)).font(.subheadline.weight(.semibold))
                Text(L10n.t("nsig.needaccount", state.language))
                    .font(.caption).foregroundStyle(.secondary)
                    .multilineTextAlignment(.center)
            }
            .padding(24)
        }
    }
}


// MARK: Voice — the owner's own voice, enrolled from the device that has the mic

private struct VoiceSection: View {
    @EnvironmentObject private var state: AppState

    var body: some View {
        if let pid = state.pid, let token = state.token {
            VoiceView(profileId: pid, token: token)
        } else {
            VStack(spacing: 8) {
                Text(L10n.t("nmg.needprofile", state.language)).font(.subheadline.weight(.semibold))
                Text(L10n.t("nvoi.needprofile", state.language))
                    .font(.caption).foregroundStyle(.secondary)
                    .multilineTextAlignment(.center)
            }
            .padding(24)
        }
    }
}


// MARK: A live desk — the person behind the counter, and the bell

/// Look up a desk by id and hand off to `DeskView`. A visitor normally arrives
/// from a beacon rather than by typing an id; this is the way in until desk
/// beacons are placed.
private struct DeskSection: View {
    @EnvironmentObject private var state: AppState
    @State private var deskId = ""
    @State private var open = false

    var body: some View {
        NavigationStack {
            Form {
                Section(L10n.t("nmg.t.desk", state.language)) {
                    let deskHint = "dsk_…"
                    TextField(deskHint, text: $deskId)
                        .autocorrectionDisabled()
                        .textInputAutocapitalization(.never)
                    Button(L10n.t("nmg.open", state.language)) { open = true }
                        .disabled(deskId.isEmpty)
                }
                Section {
                    Text(L10n.t("ndsk.note", state.language))
                        .font(.caption2).foregroundStyle(.secondary)
                }
            }
            .navigationDestination(isPresented: $open) {
                DeskView(deskId: deskId, callerId: state.interactorId,
                         viewerToken: state.interactorToken)
            }
        }
    }
}
