import SwiftUI

/// The public stream, in the pocket: one card at a time, a button for the
/// next one.
///
/// Three things this screen renders and does not decide, because deciding
/// them in four clients is how a promise becomes four promises:
///
/// * **`plays`** is the server's. Only footage this deployment holds comes
///   back `true`; anything on somebody else's platform stays a card until a
///   person presses it, so flicking past fifty videos does not announce this
///   reader to fifty other companies. `qrme/db.py` has said so about
///   `post_videos` since long before a stream existed.
/// * **`entering`** and **`ringing`** are shown *before* the button. A live
///   room and a desk reach a human being, and somebody who swipes into a room
///   should know that walking in puts them in it.
/// * **`reason`** rides every card. A stream that cannot say why something is
///   in front of you is one nobody can audit.
///
/// No gesture swiping here yet — Previous and Next are buttons, and the
/// reason is honest rather than aesthetic: a stream a person can only use by
/// dragging is one somebody with a motor impairment cannot use at all, and
/// the buttons work for everybody while the gesture is built.
struct StreamSection: View {
    @EnvironmentObject var state: AppState
    @State private var cards: [FeedCard] = []
    @State private var cursor: String?
    @State private var at = 0
    @State private var opened: Set<String> = []
    @State private var line: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("feed.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            Text(L10n.t("feed.sub", state.language))
                .font(.footnote).foregroundStyle(Theme.t2)

            if cards.isEmpty {
                Text(L10n.t("feed.empty", state.language))
                    .font(.footnote).foregroundStyle(Theme.t2)
            } else if at < cards.count {
                card(cards[at])
                HStack {
                    Button(L10n.t("feed.back", state.language)) {
                        at = max(0, at - 1)
                    }.font(.caption).disabled(at == 0)
                    Spacer()
                    Text("\(at + 1) / \(cards.count)")
                        .font(.caption2).foregroundStyle(Theme.t3)
                    Spacer()
                    Button(L10n.t("feed.next", state.language)) { next() }
                        .font(.caption).disabled(busy)
                }
            }
            if let l = line {
                Text(l).font(.caption2).foregroundStyle(Theme.t3)
            }
        }
        .card()
        .task { await load(nil) }
    }

    /// Spelled out rather than built from the kind. A key assembled at
    /// runtime is invisible to the guard that checks every asked-for key
    /// exists, and the screen would render the key name at somebody.
    private func kindLabel(_ kind: String) -> String {
        switch kind {
        case "video": return L10n.t("feed.kind.video", state.language)
        case "offsite": return L10n.t("feed.kind.offsite", state.language)
        case "room": return L10n.t("feed.kind.room", state.language)
        case "party": return L10n.t("feed.kind.party", state.language)
        default: return L10n.t("feed.kind.desk", state.language)
        }
    }

    @ViewBuilder
    private func card(_ c: FeedCard) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack {
                Text(kindLabel(c.kind))
                    .font(.caption.bold()).foregroundStyle(Theme.brandA)
                Spacer()
                if let r = c.reason {
                    Text(r).font(.caption2).foregroundStyle(Theme.t3)
                }
            }
            switch c.kind {
            case "video":
                Text(c.title ?? "—").font(.subheadline).foregroundStyle(Theme.txt)
                if let n = c.note {
                    Text(n).font(.caption2).foregroundStyle(Theme.t3)
                }
            case "offsite":
                Text(c.title ?? "—").font(.subheadline).foregroundStyle(Theme.txt)
                Text(c.facade?.platform_name ?? "—")
                    .font(.caption).foregroundStyle(Theme.t2)
                // Nothing is requested until this press. Opening it is the
                // reader's own act, which is the whole of the rule.
                if !opened.contains(c.id) {
                    Button(L10n.t("feed.play", state.language)) {
                        opened.insert(c.id)
                        if let u = c.facade?.url, let url = URL(string: u) {
                            line = url.absoluteString
                        }
                    }.font(.caption)
                }
                if let n = c.note {
                    Text(n).font(.caption2).foregroundStyle(Theme.t3)
                }
            case "room":
                Text(c.topic ?? L10n.t("feed.room.untitled", state.language))
                    .font(.subheadline).foregroundStyle(Theme.txt)
                let heads = c.people ?? 0
                Text((c.channel ?? "") + " · " + String(heads))
                    .font(.caption).foregroundStyle(Theme.t2)
                // Before the button, deliberately.
                if let e = c.entering {
                    Text(e).font(.caption2).foregroundStyle(Theme.t3)
                }
                Button(L10n.t("feed.enter", state.language)) {
                    line = c.entering
                }.font(.caption)
            case "party":
                Text(c.title ?? "—").font(.subheadline).foregroundStyle(Theme.txt)
                Text((c.video?.platform_name ?? "") + " · "
                     + String(c.people ?? 0))
                    .font(.caption).foregroundStyle(Theme.t2)
                // Before the button. Joining puts your name in the room.
                if let j = c.joining {
                    Text(j).font(.caption2).foregroundStyle(Theme.t3)
                }
                Button(L10n.t("party.join", state.language)) {
                    Task {
                        do {
                            _ = try await ApiClient.shared.joinParty(
                                partyId: c.id, memberId: state.pid ?? "",
                                kind: "profile", token: state.token ?? "")
                            line = c.title
                        } catch { line = error.localizedDescription }
                    }
                }.font(.caption)
            default:
                Text(c.display_name ?? "—")
                    .font(.subheadline).foregroundStyle(Theme.txt)
                Text((c.trade ?? "") + " · " + (c.presence ?? ""))
                    .font(.caption).foregroundStyle(Theme.t2)
                if let r = c.ringing {
                    Text(r).font(.caption2).foregroundStyle(Theme.t3)
                }
                Button(L10n.t("feed.ring", state.language)) {
                    line = c.ringing
                }.font(.caption)
            }
        }
    }

    /// One page ahead of the end, so the next press never waits on a request.
    private func next() {
        at = min(cards.count - 1, at + 1)
        if let c = cursor, at >= cards.count - 2, !busy {
            Task { await load(c) }
        }
    }

    private func load(_ after: String?) async {
        busy = true
        defer { busy = false }
        do {
            let page = try await ApiClient.shared.publicFeed(cursor: after)
            cards = after == nil ? page.cards : cards + page.cards
            cursor = page.cursor
        } catch {
            // A stream that cannot load is a quiet shelf, not an error page.
            line = nil
        }
    }
}

/// A link somebody was sent, opened by the same rules as the stream: the
/// card comes from `/feed/{id}`, so a rated item a reader is not verified
/// for is a 404 here too rather than an empty card.
struct SharedCardSection: View {
    @EnvironmentObject var state: AppState
    @State private var itemId = ""
    @State private var line: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                TextField("", text: $itemId)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("feed.play", state.language)) {
                    Task {
                        do {
                            let c = try await ApiClient.shared.feedItem(
                                id: itemId)
                            line = (c.title ?? c.display_name ?? c.id)
                                + " · " + ((c.plays ?? false) ? "▶" : "—")
                        } catch {
                            line = nil
                        }
                    }
                }.font(.caption).disabled(itemId.isEmpty)
            }
            if let l = line {
                Text(l).font(.caption2).foregroundStyle(Theme.t3)
            }
        }.card()
    }
}
