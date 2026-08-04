import SwiftUI

/// The storefront, in the pocket. A shop is not a desk — this section has
/// no bell, no sessions and no connection offers, and that absence is the
/// design. Browse and buy with the interactor identity the shell already
/// holds; sell with the owner token it already holds. Every string goes
/// through L10n, because the English count behind this shell's tabs is a
/// ratchet that must not grow.
struct ShopSection: View {
    @EnvironmentObject var state: AppState
    @State private var cards: [ShopCardRow] = []
    @State private var open: ShopDetailRow?
    @State private var quantity = "1"
    @State private var mine: [ShopOrderRow] = []

    @State private var shopName = ""
    @State private var myShop: ShopDetailRow?
    @State private var book: [ShopOrderRow] = []
    @State private var offerTitle = ""
    @State private var offerPrice = ""
    @State private var offerKind = "goods"

    @State private var note: String?
    @State private var busy = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                VStack(alignment: .leading, spacing: 8) {
                    Text(L10n.t("shop.title", state.language))
                        .font(.headline).foregroundStyle(Theme.txt)
                    Text(L10n.t("shop.sub", state.language))
                        .font(.caption).foregroundStyle(Theme.t2)
                    ForEach(cards) { s in
                        HStack {
                            VStack(alignment: .leading) {
                                Text(s.name).font(.caption)
                                    .foregroundStyle(Theme.txt)
                                let meta = s.seller
                                    + (s.tag.map { " · " + $0 } ?? "")
                                Text(meta).font(.caption2)
                                    .foregroundStyle(Theme.t2)
                            }
                            Spacer()
                            Button(L10n.t("shop.browse", state.language)) {
                                browse(s.id)
                            }.font(.caption)
                        }
                    }
                }.card()

                if let shop = open {
                    VStack(alignment: .leading, spacing: 8) {
                        Text(shop.name).font(.subheadline.bold())
                            .foregroundStyle(Theme.txt)
                        TextField(L10n.t("shop.quantity", state.language),
                                  text: $quantity)
                            .keyboardType(.numberPad)
                            .textFieldStyle(.roundedBorder)
                        ForEach(shop.offerings) { o in
                            HStack {
                                VStack(alignment: .leading) {
                                    Text(o.title).font(.caption)
                                        .foregroundStyle(Theme.txt)
                                    let meta = o.kind + " · "
                                        + String(format: "%.2f", o.price)
                                        + " " + o.currency + " · "
                                        + o.availability
                                    Text(meta).font(.caption2)
                                        .foregroundStyle(Theme.t2)
                                }
                                Spacer()
                                Button(L10n.t("shop.order", state.language)) {
                                    order(shop.id, o.id)
                                }
                                .font(.caption)
                                .disabled(busy || state.interactorId == nil)
                            }
                        }
                        if !mine.isEmpty {
                            Text(L10n.t("shop.mine", state.language))
                                .font(.caption.bold())
                                .foregroundStyle(Theme.t2)
                            ForEach(mine) { o in
                                HStack {
                                    let line = o.title + " · "
                                        + String(format: "%.2f", o.amount)
                                        + " " + o.currency + " · " + o.status
                                    Text(line).font(.caption2)
                                        .foregroundStyle(Theme.t2)
                                    Spacer()
                                    if o.status == "placed" {
                                        Button(L10n.t("shop.cancel",
                                                      state.language)) {
                                            cancel(o)
                                        }.font(.caption2).disabled(busy)
                                    }
                                }
                            }
                        }
                    }.card()
                }

                VStack(alignment: .leading, spacing: 8) {
                    Text(L10n.t("shop.till", state.language))
                        .font(.subheadline.bold()).foregroundStyle(Theme.txt)
                    Text(L10n.t("shop.till_note", state.language))
                        .font(.caption2).foregroundStyle(Theme.t2)
                    TextField(L10n.t("shop.name", state.language),
                              text: $shopName)
                        .textFieldStyle(.roundedBorder)
                    Button(L10n.t("shop.open", state.language)) { openTill() }
                        .disabled(busy || shopName.isEmpty || state.pid == nil)
                    if let till = myShop {
                        TextField(L10n.t("shop.offer_title", state.language),
                                  text: $offerTitle)
                            .textFieldStyle(.roundedBorder)
                        TextField(L10n.t("shop.price", state.language),
                                  text: $offerPrice)
                            .keyboardType(.decimalPad)
                            .textFieldStyle(.roundedBorder)
                        Picker("", selection: $offerKind) {
                            ForEach(["goods", "service"], id: \.self) {
                                Text($0).tag($0)
                            }
                        }.pickerStyle(.segmented)
                        Button(L10n.t("shop.add", state.language)) {
                            addOffering(till.id)
                        }.disabled(busy || offerTitle.isEmpty)
                        ForEach(till.offerings) { o in
                            HStack {
                                let line = o.title + " · "
                                    + String(format: "%.2f", o.price)
                                    + " " + o.currency
                                Text(line).font(.caption2)
                                    .foregroundStyle(Theme.t2)
                                Spacer()
                                Button(L10n.t("shop.retire", state.language)) {
                                    retire(till.id, o.id)
                                }.font(.caption2).disabled(busy)
                            }
                        }
                        if !book.isEmpty {
                            Text(L10n.t("shop.book", state.language))
                                .font(.caption.bold())
                                .foregroundStyle(Theme.t2)
                        }
                        ForEach(book) { o in
                            HStack {
                                let line = o.title + " ×\(o.quantity) · "
                                    + String(format: "%.2f", o.amount)
                                    + " " + o.currency + " · " + o.status
                                Text(line).font(.caption2)
                                    .foregroundStyle(Theme.t2)
                                Spacer()
                                if o.status == "placed" {
                                    Button(L10n.t("shop.accept",
                                                  state.language)) {
                                        advance(o, "accepted")
                                    }.font(.caption2).disabled(busy)
                                } else if o.status == "accepted" {
                                    Button(L10n.t("shop.fulfil",
                                                  state.language)) {
                                        advance(o, "fulfilled")
                                    }.font(.caption2).disabled(busy)
                                }
                            }
                        }
                    }
                }.card()

                if let note {
                    Text(note).font(.caption).foregroundStyle(Theme.t2)
                }
            }.padding(20)
        }
        .task { cards = (try? await ApiClient.shared.listShops()) ?? [] }
    }

    private func run(_ op: @escaping () async throws -> Void) {
        busy = true; note = nil
        Task {
            do { try await op() } catch { note = error.localizedDescription }
            busy = false
        }
    }

    private func browse(_ shopId: String) {
        run { open = try await ApiClient.shared.shopCard(shopId: shopId) }
    }

    private func order(_ shopId: String, _ offeringId: String) {
        guard let bid = state.interactorId,
              let btok = state.interactorToken else { return }
        run {
            _ = try await ApiClient.shared.placeShopOrder(
                shopId: shopId, offeringId: offeringId, buyerId: bid,
                quantity: Int(quantity) ?? 1, token: btok)
            mine = try await ApiClient.shared.myShopOrders(buyerId: bid,
                                                           token: btok)
        }
    }

    private func cancel(_ o: ShopOrderRow) {
        guard let bid = state.interactorId,
              let btok = state.interactorToken else { return }
        run {
            _ = try await ApiClient.shared.advanceShopOrder(
                shopId: o.shop_id, orderId: o.id, party: "buyer",
                to: "cancelled", token: btok)
            mine = try await ApiClient.shared.myShopOrders(buyerId: bid,
                                                           token: btok)
        }
    }

    private func openTill() {
        guard let pid = state.pid, let tok = state.token else { return }
        run {
            let shop = try await ApiClient.shared.openShop(
                profileId: pid, name: shopName, blurb: nil, tag: nil,
                token: tok)
            myShop = shop
            book = try await ApiClient.shared.shopOrderBook(shopId: shop.id,
                                                            token: tok)
            cards = try await ApiClient.shared.listShops()
        }
    }

    private func addOffering(_ shopId: String) {
        guard let tok = state.token else { return }
        run {
            _ = try await ApiClient.shared.addShopOffering(
                shopId: shopId, kind: offerKind, title: offerTitle,
                price: Double(offerPrice) ?? 0, token: tok)
            offerTitle = ""; offerPrice = ""
            myShop = try await ApiClient.shared.shopCard(shopId: shopId)
        }
    }

    private func retire(_ shopId: String, _ offeringId: String) {
        guard let tok = state.token else { return }
        run {
            _ = try await ApiClient.shared.retireShopOffering(
                shopId: shopId, offeringId: offeringId, token: tok)
            myShop = try await ApiClient.shared.shopCard(shopId: shopId)
        }
    }

    private func advance(_ o: ShopOrderRow, _ to: String) {
        guard let tok = state.token, let till = myShop else { return }
        run {
            _ = try await ApiClient.shared.advanceShopOrder(
                shopId: o.shop_id, orderId: o.id, party: "seller", to: to,
                token: tok)
            book = try await ApiClient.shared.shopOrderBook(shopId: till.id,
                                                            token: tok)
        }
    }
}
