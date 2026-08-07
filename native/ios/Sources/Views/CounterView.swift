import SwiftUI

/// Standing behind the counter — the half of trade the phones never had.
///
/// The caller's side shipped long ago: `DeskView` rings a bell, joins a
/// stream, opens a session. What no shell could do was the other side of
/// the same counter — open a desk, staff it, decide who comes through,
/// print its sticker. `MarketSection` could put a card up and could not
/// search, price, sell or buy. Exchanges — two parties, one manifest —
/// existed on no phone at all.
///
///     asked     can a phone be found on the platform
///     mattered  can a phone do business on it
///
/// Every string goes through L10n; the server's refusals arrive already
/// in the reader's language and are shown verbatim.

// MARK: The counter — a desk, from behind it

struct CounterSection: View {
    @EnvironmentObject var state: AppState
    @State private var deskId = ""
    @State private var deskToken = ""
    @State private var camUrl = ""
    @State private var displayName = ""
    @State private var trade = ""
    @State private var attestor = ""
    @State private var basis = ""
    @State private var location = ""
    @State private var blurb = ""
    @State private var card: DeskCard?
    @State private var nearby: [DeskBrief] = []
    @State private var rings: [DeskRing] = []
    @State private var guests: [DeskGuest] = []
    @State private var beacons: [DeskBeacon] = []
    @State private var beaconLabel = ""
    @State private var overlay: DeskOverlay?
    @State private var staffedBy: String?
    @State private var knockNote = ""
    @State private var note: String?
    @State private var busy = false

    /// The three presences the backend accepts. Offered as a closed set
    /// because it *is* one — the refusal names all three, and a free text
    /// field would earn that refusal on every typo.
    private let presences = ["attended", "away", "closed"]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                VStack(alignment: .leading, spacing: 8) {
                    Text(L10n.t("counter.open", state.language))
                        .font(.headline).foregroundStyle(Theme.txt)
                    Text(L10n.t("counter.attested", state.language))
                        .font(.caption2).foregroundStyle(Theme.t2)
                    TextField(L10n.t("counter.name", state.language),
                              text: $displayName)
                        .textFieldStyle(.roundedBorder)
                    TextField(L10n.t("counter.trade", state.language),
                              text: $trade)
                        .textFieldStyle(.roundedBorder)
                    TextField(L10n.t("counter.attestor", state.language),
                              text: $attestor)
                        .textFieldStyle(.roundedBorder)
                    TextField(L10n.t("counter.basis", state.language),
                              text: $basis)
                        .textFieldStyle(.roundedBorder)
                    TextField(L10n.t("counter.where", state.language),
                              text: $location)
                        .textFieldStyle(.roundedBorder)
                    TextField(L10n.t("counter.blurb", state.language),
                              text: $blurb)
                        .textFieldStyle(.roundedBorder)
                    Button(L10n.t("counter.open.go", state.language)) {
                        openDesk()
                    }.disabled(busy || displayName.isEmpty || trade.isEmpty
                               || attestor.isEmpty || basis.isEmpty)
                }.card()

                VStack(alignment: .leading, spacing: 8) {
                    Text(L10n.t("counter.mine", state.language))
                        .font(.subheadline.bold()).foregroundStyle(Theme.txt)
                    TextField(L10n.t("counter.desk_id", state.language),
                              text: $deskId)
                        .textFieldStyle(.roundedBorder)
                    TextField(L10n.t("counter.desk_token", state.language),
                              text: $deskToken)
                        .textFieldStyle(.roundedBorder)
                    if let card {
                        let line = card.display_name + " · " + card.presence
                        Text(line).font(.caption).foregroundStyle(Theme.t2)
                    }
                    HStack {
                        ForEach(presences, id: \.self) { p in
                            Button(presenceLabel(p,
                                          state.language)) {
                                setPresence(p)
                            }.font(.caption2).disabled(busy || deskId.isEmpty)
                        }
                    }
                    TextField(L10n.t("counter.camera.url", state.language),
                              text: $camUrl)
                        .textFieldStyle(.roundedBorder).font(.caption2)
                    Button(L10n.t("counter.camera", state.language)) {
                        run { card = try await ApiClient.shared.setDeskCamera(
                            deskId: deskId, url: camUrl, token: deskToken) }
                    }.font(.caption2).disabled(busy || deskId.isEmpty)
                    Button(L10n.t("counter.portrait", state.language)) {
                        run { card = try await ApiClient.shared.setDeskPortrait(
                            deskId: deskId, asset: nil, token: deskToken) }
                    }.font(.caption2).disabled(busy || deskId.isEmpty)
                    if !deskId.isEmpty {
                        AsyncImage(url: ApiClient.shared.deskViewUrl(
                            deskId: deskId)) { image in
                            image.resizable().scaledToFit()
                                .frame(maxHeight: 160)
                        } placeholder: { EmptyView() }
                    }
                }.card()

                VStack(alignment: .leading, spacing: 8) {
                    Text(L10n.t("counter.bell", state.language))
                        .font(.subheadline.bold()).foregroundStyle(Theme.txt)
                    ForEach(rings) { r in
                        HStack {
                            Text(r.note ?? r.id).font(.caption2)
                                .foregroundStyle(Theme.t2)
                            Spacer()
                            Button(L10n.t("counter.ack", state.language)) {
                                run { try await ApiClient.shared.ackDeskRing(
                                    deskId: deskId, ringId: r.id,
                                    token: deskToken) }
                            }.font(.caption2).disabled(busy)
                        }
                    }
                    Text(L10n.t("counter.guests", state.language))
                        .font(.caption).foregroundStyle(Theme.txt)
                    ForEach(guests) { g in
                        HStack {
                            let who = g.display_name ?? g.guest_id
                            let line = who + " · " + g.status
                            Text(line).font(.caption2)
                                .foregroundStyle(Theme.t2)
                            Spacer()
                            Button(L10n.t("counter.accept", state.language)) {
                                run { _ = try await ApiClient.shared
                                    .acceptDeskGuest(deskId: deskId,
                                                     requestId: g.id,
                                                     token: deskToken) }
                            }.font(.caption2).disabled(busy)
                            Button(L10n.t("counter.decline", state.language)) {
                                run { _ = try await ApiClient.shared
                                    .declineDeskGuest(deskId: deskId,
                                                      requestId: g.id,
                                                      token: deskToken) }
                            }.font(.caption2).disabled(busy)
                        }
                    }
                    if let overlay {
                        let waiting = L10n.t("counter.waiting", state.language)
                        Text(waiting + " " + String(overlay.waiting))
                            .font(.caption2).foregroundStyle(Theme.t2)
                    }
                    if let staffedBy {
                        Text(staffedBy).font(.caption2)
                            .foregroundStyle(Theme.t2)
                    }
                }.card()

                VStack(alignment: .leading, spacing: 8) {
                    Text(L10n.t("counter.sticker", state.language))
                        .font(.subheadline.bold()).foregroundStyle(Theme.txt)
                    Text(L10n.t("counter.sticker.note", state.language))
                        .font(.caption2).foregroundStyle(Theme.t2)
                    HStack {
                        TextField(L10n.t("counter.sticker.label",
                                         state.language),
                                  text: $beaconLabel)
                            .textFieldStyle(.roundedBorder)
                        Button(L10n.t("counter.sticker.make",
                                      state.language)) {
                            run {
                                _ = try await ApiClient.shared.addDeskBeacon(
                                    deskId: deskId, label: beaconLabel,
                                    token: deskToken)
                                beaconLabel = ""
                            }
                        }.disabled(busy || beaconLabel.isEmpty)
                    }
                    ForEach(beacons) { b in
                        HStack {
                            Text(b.label ?? b.id).font(.caption2)
                                .foregroundStyle(Theme.t2)
                            Spacer()
                            AsyncImage(url: ApiClient.shared
                                .deskBeaconQrUrl(beaconId: b.id)) { image in
                                image.resizable().frame(width: 44, height: 44)
                            } placeholder: { EmptyView() }
                            Button(L10n.t("counter.sticker.drop",
                                          state.language)) {
                                run { try await ApiClient.shared
                                    .removeDeskBeacon(beaconId: b.id,
                                                      token: deskToken) }
                            }.font(.caption2).disabled(busy)
                        }
                    }
                }.card()

                VStack(alignment: .leading, spacing: 8) {
                    Text(L10n.t("counter.walkup", state.language))
                        .font(.subheadline.bold()).foregroundStyle(Theme.txt)
                    ForEach(nearby) { d in
                        HStack {
                            let line = d.display_name + " · " + d.presence
                            Text(line).font(.caption2)
                                .foregroundStyle(Theme.t2)
                            Spacer()
                            Button(L10n.t("counter.pick", state.language)) {
                                deskId = d.id
                            }.font(.caption2)
                        }
                    }
                    TextField(L10n.t("counter.knock.note", state.language),
                              text: $knockNote)
                        .textFieldStyle(.roundedBorder)
                    HStack {
                        Button(L10n.t("counter.knock", state.language)) {
                            run {
                                _ = try await ApiClient.shared.askToJoinDesk(
                                    deskId: deskId, note: knockNote,
                                    token: state.interactorToken ?? "")
                                knockNote = ""
                            }
                        }.disabled(busy || deskId.isEmpty)
                        Button(L10n.t("counter.leave", state.language)) {
                            run { try await ApiClient.shared.leaveDesk(
                                deskId: deskId,
                                token: state.interactorToken ?? "") }
                        }.disabled(busy || deskId.isEmpty)
                    }
                }.card()

                if let note {
                    Text(note).font(.caption).foregroundStyle(Theme.t2)
                }
            }.padding(20)
        }
        .task { await load() }
    }

    private func load() async {
        nearby = (try? await ApiClient.shared.desks()) ?? []
        guard !deskId.isEmpty else { return }
        overlay = try? await ApiClient.shared.deskOverlay(deskId: deskId)
        if let live = try? await ApiClient.shared.deskLivePerson(
                deskId: deskId) {
            staffedBy = live.owner_id
        }
        guard !deskToken.isEmpty else { return }
        rings = (try? await ApiClient.shared.deskRings(
            deskId: deskId, token: deskToken)) ?? []
        guests = (try? await ApiClient.shared.deskGuests(
            deskId: deskId, token: deskToken)) ?? []
        beacons = (try? await ApiClient.shared.deskBeacons(
            deskId: deskId, token: deskToken)) ?? []
    }

    private func run(_ op: @escaping () async throws -> Void) {
        busy = true; note = nil
        Task {
            do { try await op(); await load() }
            catch { note = error.localizedDescription }
            busy = false
        }
    }

    private func openDesk() {
        run {
            let made = try await ApiClient.shared.openDesk(
                ownerId: state.pid ?? "", displayName: displayName,
                trade: trade, attestor: attestor, basis: basis,
                location: location, blurb: blurb, token: state.token ?? "")
            card = made
            deskId = made.desk_id
            deskToken = made.desk_token ?? ""
        }
    }

    private func setPresence(_ presence: String) {
        run {
            card = try await ApiClient.shared.setDeskPresence(
                deskId: deskId, presence: presence, token: deskToken)
        }
    }
}

// MARK: Trade — the market, from both sides of it

struct TradeSection: View {
    @EnvironmentObject var state: AppState
    @State private var cards: [MarketCard] = []
    @State private var localities: [String] = []
    @State private var query = ""
    @State private var hits: [MarketHit] = []
    @State private var need = ""
    @State private var suggestions: [String] = []
    @State private var listingId = ""
    @State private var amount = ""
    @State private var locality = ""
    @State private var offer: MarketOffer?
    @State private var sales: [MarketSale] = []
    @State private var includeRemote = true
    @State private var prefLocality = ""
    @State private var blurb = ""
    @State private var tags = ""
    @State private var note: String?
    @State private var busy = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                VStack(alignment: .leading, spacing: 8) {
                    Text(L10n.t("trade.find", state.language))
                        .font(.headline).foregroundStyle(Theme.txt)
                    HStack {
                        TextField(L10n.t("trade.query", state.language),
                                  text: $query)
                            .textFieldStyle(.roundedBorder)
                        Button(L10n.t("trade.search", state.language)) {
                            run { hits = try await ApiClient.shared
                                .marketSearch(query).results }
                        }.disabled(busy || query.isEmpty)
                    }
                    ForEach(hits) { h in
                        Text(h.title).font(.caption2)
                            .foregroundStyle(Theme.t2)
                    }
                    HStack {
                        TextField(L10n.t("trade.need", state.language),
                                  text: $need)
                            .textFieldStyle(.roundedBorder)
                        Button(L10n.t("trade.assist", state.language)) {
                            run { suggestions = try await ApiClient.shared
                                .marketAssist(need: need).suggestions }
                        }.disabled(busy || need.isEmpty)
                    }
                    if !suggestions.isEmpty {
                        Text(suggestions.joined(separator: " · "))
                            .font(.caption2).foregroundStyle(Theme.t2)
                    }
                    if !localities.isEmpty {
                        Text(localities.joined(separator: " · "))
                            .font(.caption2).foregroundStyle(Theme.t2)
                    }
                    ForEach(cards) { c in
                        Text(c.display_name).font(.caption2)
                            .foregroundStyle(Theme.t2)
                    }
                    Button(L10n.t("trade.seed", state.language)) {
                        run { _ = try await ApiClient.shared
                            .seedMarketplace() }
                    }.font(.caption2).disabled(busy)
                }.card()

                VStack(alignment: .leading, spacing: 8) {
                    Text(L10n.t("trade.stand", state.language))
                        .font(.subheadline.bold()).foregroundStyle(Theme.txt)
                    TextField(L10n.t("trade.blurb", state.language),
                              text: $blurb)
                        .textFieldStyle(.roundedBorder)
                    TextField(L10n.t("trade.tags", state.language),
                              text: $tags)
                        .textFieldStyle(.roundedBorder)
                    HStack {
                        Button(L10n.t("trade.list", state.language)) {
                            run { try await ApiClient.shared
                                .listInMarketplace(
                                    profileId: state.pid ?? "", blurb: blurb,
                                    tags: tags.split(separator: ",")
                                        .map { String($0)
                                            .trimmingCharacters(in: .whitespaces) },
                                    token: state.token ?? "") }
                        }.disabled(busy)
                        Button(L10n.t("trade.unlist", state.language)) {
                            run { try await ApiClient.shared
                                .unlistFromMarketplace(
                                    profileId: state.pid ?? "",
                                    token: state.token ?? "") }
                        }.disabled(busy)
                    }
                }.card()

                VStack(alignment: .leading, spacing: 8) {
                    Text(L10n.t("trade.price", state.language))
                        .font(.subheadline.bold()).foregroundStyle(Theme.txt)
                    TextField(L10n.t("trade.listing", state.language),
                              text: $listingId)
                        .textFieldStyle(.roundedBorder)
                    TextField(L10n.t("trade.amount", state.language),
                              text: $amount)
                        .textFieldStyle(.roundedBorder)
                    if let offer, let shown = offer.amount {
                        let line = L10n.t("trade.asking", state.language)
                            + " " + String(shown)
                        Text(line).font(.caption2).foregroundStyle(Theme.t2)
                    }
                    HStack {
                        Button(L10n.t("trade.set", state.language)) {
                            run {
                                offer = try await ApiClient.shared
                                    .setListingOffer(
                                        listingId: listingId,
                                        price: Double(amount) ?? 0,
                                        currency: "USD",
                                        stock: nil,
                                        token: state.token ?? "")
                            }
                        }.disabled(busy || listingId.isEmpty)
                        Button(L10n.t("trade.show", state.language)) {
                            run { offer = try await ApiClient.shared
                                .listingOffer(listingId: listingId) }
                        }.disabled(busy || listingId.isEmpty)
                        Button(L10n.t("trade.clear", state.language)) {
                            run { try await ApiClient.shared
                                .clearListingOffer(listingId: listingId,
                                                   token: state.token ?? "") }
                        }.disabled(busy || listingId.isEmpty)
                    }
                    TextField(L10n.t("trade.venue", state.language),
                              text: $locality)
                        .textFieldStyle(.roundedBorder)
                    HStack {
                        Button(L10n.t("trade.place", state.language)) {
                            run { _ = try await ApiClient.shared
                                .placeListing(listingId: listingId,
                                              locality: locality,
                                              token: state.token ?? "") }
                        }.disabled(busy || listingId.isEmpty || locality.isEmpty)
                        Button(L10n.t("trade.unplace", state.language)) {
                            run { try await ApiClient.shared
                                .unplaceListing(listingId: listingId,
                                                token: state.token ?? "") }
                        }.disabled(busy || listingId.isEmpty)
                        Button(L10n.t("trade.pull", state.language)) {
                            run { try await ApiClient.shared
                                .removeListing(listingId: listingId,
                                               token: state.token ?? "") }
                        }.disabled(busy || listingId.isEmpty)
                    }
                    Button(L10n.t("trade.buy", state.language)) {
                        run { _ = try await ApiClient.shared
                            .purchaseListing(listingId: listingId,
                                             token: state.interactorToken ?? "") }
                    }.disabled(busy || listingId.isEmpty)
                }.card()

                VStack(alignment: .leading, spacing: 8) {
                    Text(L10n.t("trade.sales", state.language))
                        .font(.subheadline.bold()).foregroundStyle(Theme.txt)
                    ForEach(sales) { s in
                        let line = s.id + " · " + (s.status ?? "")
                        Text(line).font(.caption2).foregroundStyle(Theme.t2)
                    }
                    TextField(L10n.t("trade.locality", state.language),
                              text: $prefLocality, onCommit: { savePrefs() })
                        .textFieldStyle(.roundedBorder).font(.caption2)
                    Toggle(isOn: Binding(get: { includeRemote },
                                         set: { includeRemote = $0
                                                savePrefs() })) {
                        Text(L10n.t("trade.include_remote", state.language))
                            .font(.caption).foregroundStyle(Theme.t2)
                    }.disabled(busy)
                }.card()

                if let note {
                    Text(note).font(.caption).foregroundStyle(Theme.t2)
                }
            }.padding(20)
        }
        .task { await load() }
    }

    private func load() async {
        cards = (try? await ApiClient.shared.marketplace()) ?? []
        localities = (try? await ApiClient.shared.marketLocalities()) ?? []
        guard let token = state.token else { return }
        sales = (try? await ApiClient.shared.marketSales(token: token)) ?? []
        if let interactor = state.interactorId,
           let settings = try? await ApiClient.shared.marketSettings(
                interactorId: interactor, token: token) {
            prefLocality = settings.locality ?? ""
            includeRemote = settings.include_remote ?? true
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

    // MarketPrefs is where "here" is and how far out to look.
    private func savePrefs() {
        run {
            _ = try await ApiClient.shared.setMarketSettings(
                interactorId: state.interactorId ?? "",
                locality: prefLocality, includeRemote: includeRemote,
                token: state.token ?? "")
        }
    }
}

// MARK: Deals — two parties, one manifest

struct DealsSection: View {
    @EnvironmentObject var state: AppState
    @State private var vocabulary: ExchangeVocabulary?
    @State private var guestId = ""
    @State private var work = ""
    @State private var industry = "software"
    @State private var fee = ""
    @State private var exchangeId = ""
    @State private var deal: ExchangeDeal?
    @State private var itemName = ""
    @State private var itemKind = "source"
    @State private var direction = "host_to_guest"
    @State private var channel: String?
    @State private var mine: [ExchangeDeal] = []
    @State private var note: String?
    @State private var busy = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                VStack(alignment: .leading, spacing: 8) {
                    Text(L10n.t("deals.propose", state.language))
                        .font(.headline).foregroundStyle(Theme.txt)
                    if let vocabulary {
                        Text(vocabulary.rules.joined(separator: " · "))
                            .font(.caption2).foregroundStyle(Theme.t2)
                        Picker("", selection: $industry) {
                            ForEach(vocabulary.industries, id: \.self) {
                                Text($0).tag($0)
                            }
                        }.pickerStyle(.menu).tint(Theme.brandA)
                    }
                    TextField(L10n.t("deals.guest", state.language),
                              text: $guestId)
                        .textFieldStyle(.roundedBorder)
                    TextField(L10n.t("deals.work", state.language),
                              text: $work)
                        .textFieldStyle(.roundedBorder)
                    TextField(L10n.t("deals.fee", state.language), text: $fee)
                        .textFieldStyle(.roundedBorder)
                    Button(L10n.t("deals.propose.go", state.language)) {
                        propose()
                    }.disabled(busy || guestId.isEmpty || work.isEmpty)
                }.card()

                VStack(alignment: .leading, spacing: 8) {
                    Text(L10n.t("deals.manifest", state.language))
                        .font(.subheadline.bold()).foregroundStyle(Theme.txt)
                    TextField(L10n.t("deals.id", state.language),
                              text: $exchangeId)
                        .textFieldStyle(.roundedBorder)
                    ForEach(mine) { d in
                        HStack {
                            let row = (d.work ?? d.id) + " · " + d.state
                            Text(row).font(.caption2)
                                .foregroundStyle(Theme.t2)
                            Spacer()
                            Button(L10n.t("deals.pick", state.language)) {
                                exchangeId = d.id
                            }.font(.caption2)
                        }
                    }
                    if let deal {
                        let line = (deal.work ?? "") + " · " + deal.state
                        Text(line).font(.caption).foregroundStyle(Theme.t2)
                        ForEach(deal.items ?? []) { item in
                            HStack {
                                let row = item.name + " · " + item.kind
                                Text(row).font(.caption2)
                                    .foregroundStyle(Theme.t2)
                                Spacer()
                                Button(L10n.t("deals.take",
                                              state.language)) {
                                    run { _ = try await ApiClient.shared
                                        .acceptExchangeItem(
                                            exchangeId: exchangeId,
                                            itemId: item.id,
                                            token: state.token ?? "") }
                                }.font(.caption2).disabled(busy)
                                Button(L10n.t("deals.drop",
                                              state.language)) {
                                    run { try await ApiClient.shared
                                        .removeExchangeItem(
                                            exchangeId: exchangeId,
                                            itemId: item.id,
                                            token: state.token ?? "") }
                                }.font(.caption2).disabled(busy)
                            }
                        }
                    }
                    TextField(L10n.t("deals.item", state.language),
                              text: $itemName)
                        .textFieldStyle(.roundedBorder)
                    Button(L10n.t("deals.add", state.language)) {
                        run {
                            _ = try await ApiClient.shared.addExchangeItem(
                                exchangeId: exchangeId, direction: direction,
                                name: itemName, kind: itemKind,
                                token: state.token ?? "")
                            itemName = ""
                        }
                    }.disabled(busy || exchangeId.isEmpty || itemName.isEmpty)
                }.card()

                VStack(alignment: .leading, spacing: 8) {
                    Text(L10n.t("deals.sign", state.language))
                        .font(.subheadline.bold()).foregroundStyle(Theme.txt)
                    Text(L10n.t("deals.sign.note", state.language))
                        .font(.caption2).foregroundStyle(Theme.t2)
                    HStack {
                        Button(L10n.t("deals.sign.go", state.language)) {
                            run { deal = try await ApiClient.shared
                                .signExchange(exchangeId: exchangeId,
                                              actorId: state.pid ?? "",
                                              token: state.token ?? "") }
                        }.disabled(busy || exchangeId.isEmpty)
                        Button(L10n.t("deals.reopen", state.language)) {
                            run { deal = try await ApiClient.shared
                                .reopenExchange(exchangeId: exchangeId,
                                                actorId: state.pid ?? "",
                                                token: state.token ?? "") }
                        }.disabled(busy || exchangeId.isEmpty)
                        Button(L10n.t("deals.withdraw", state.language)) {
                            run { deal = try await ApiClient.shared
                                .withdrawFromExchange(
                                    exchangeId: exchangeId,
                                    actorId: state.pid ?? "",
                                    token: state.token ?? "") }
                        }.disabled(busy || exchangeId.isEmpty)
                    }
                    Button(L10n.t("deals.channel", state.language)) {
                        run {
                            let box = try await ApiClient.shared
                                .exchangeChannel(exchangeId: exchangeId,
                                                 token: state.token ?? "")
                            channel = box["room_id"]
                        }
                    }.font(.caption2).disabled(busy || exchangeId.isEmpty)
                    if let channel {
                        Text(channel).font(.caption2)
                            .foregroundStyle(Theme.t2)
                    }
                }.card()

                if let note {
                    Text(note).font(.caption).foregroundStyle(Theme.t2)
                }
            }.padding(20)
        }
        .task { await load() }
    }

    private func load() async {
        vocabulary = try? await ApiClient.shared.exchangeVocabulary()
        if let pid = state.pid, let token = state.token {
            mine = (try? await ApiClient.shared.myExchanges(
                partyId: pid, token: token)) ?? []
        }
        guard !exchangeId.isEmpty, let token = state.token else { return }
        deal = try? await ApiClient.shared.exchange(exchangeId: exchangeId,
                                                    token: token)
    }

    private func run(_ op: @escaping () async throws -> Void) {
        busy = true; note = nil
        Task {
            do { try await op(); await load() }
            catch { note = error.localizedDescription }
            busy = false
        }
    }

    private func propose() {
        run {
            let made = try await ApiClient.shared.proposeExchange(
                hostId: state.pid ?? "", guestId: guestId, work: work,
                industry: industry, fee: Double(fee) ?? 0,
                token: state.token ?? "")
            deal = made
            exchangeId = made.id
        }
    }
}

/// The three presence states, in the reader's language.
///
/// A switch rather than a key built by concatenating the prefix with the API
/// value. A key assembled at runtime is a key no guard can see being asked
/// for — the dead-key check reads literals, so all three rows would read as
/// *nothing asks for this*, and the fix somebody reaches for when a guard
/// says that is to delete the row.
///
///     asked     does the screen ask the table for this word
///     mattered  can anything tell that it does
func presenceLabel(_ state: String, _ lang: String) -> String {
    switch state {
    case "attended": return L10n.t("counter.presence.attended", lang)
    case "away": return L10n.t("counter.presence.away", lang)
    default: return L10n.t("counter.presence.closed", lang)
    }
}
