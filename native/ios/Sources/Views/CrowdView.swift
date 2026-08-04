import SwiftUI

/// The crowd, the couch and the loan — three blocks the doorless records
/// said this phone could not reach.
///
/// **The crowd**: like, share, subscribe and gift — the audience verbs the
/// console has carried since the audience round. The backend reports the
/// numbers and the caller's own state in one call (`/audience`), so the
/// buttons render without a second trip.
///
/// **The couch**: a watch party around a posted video. Seek moves a number
/// and presses play on nobody's device; the context route says out loud
/// that a synthetic member has not seen the footage.
///
/// **The loan**: a skill lent into one place, used and never copied. The
/// vocabulary's terms are the backend's own sentences, shown verbatim.
struct CrowdSection: View {
    @EnvironmentObject var state: AppState
    @State private var kind = "profiles"
    @State private var targetId = ""
    @State private var counts: AudienceCounts?
    @State private var subs: [SubscriberRow] = []
    @State private var giftList: [GiftRow] = []
    @State private var giftAmount = ""
    @State private var giftNote = ""
    @State private var note: String?
    @State private var busy = false

    private let kinds = ["profiles", "desks", "posts", "listings"]

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("crowd.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            Picker("", selection: $kind) {
                ForEach(kinds, id: \.self) { Text($0) }
            }.pickerStyle(.segmented)
            TextField(L10n.t("crowd.target", state.language),
                      text: $targetId)
                .textFieldStyle(.roundedBorder)
            HStack {
                Button(L10n.t("crowd.like", state.language)) {
                    run { try await ApiClient.shared.like(
                        kind: kind, targetId: targetId, token: state.token!) }
                }
                Button(L10n.t("crowd.unlike", state.language)) {
                    run { try await ApiClient.shared.unlike(
                        kind: kind, targetId: targetId, token: state.token!) }
                }
                Button(L10n.t("crowd.share", state.language)) {
                    run {
                        let out = try await ApiClient.shared.share(
                            kind: kind, targetId: targetId,
                            token: state.token!)
                        note = out["url"]
                    }
                }
            }.font(.caption).disabled(busy || targetId.isEmpty)
            HStack {
                Button(L10n.t("crowd.counts", state.language)) {
                    run { counts = try await ApiClient.shared.audienceCounts(
                        kind: kind, targetId: targetId, token: state.token!) }
                }
                Button(L10n.t("crowd.follow", state.language)) {
                    run { try await ApiClient.shared.subscribe(
                        kind: kind, subjectId: targetId,
                        token: state.token!) }
                }
                Button(L10n.t("crowd.unfollow", state.language)) {
                    run { try await ApiClient.shared.unsubscribe(
                        kind: kind, subjectId: targetId,
                        token: state.token!) }
                }
                Button(L10n.t("crowd.subscribers", state.language)) {
                    run { subs = try await ApiClient.shared.subscribers(
                        kind: kind, subjectId: targetId,
                        token: state.token!) }
                }
            }.font(.caption).disabled(busy || targetId.isEmpty)
            if let counts {
                Text("♥ \(counts.likes ?? 0) · 💬 \(counts.comments ?? 0)"
                     + " · ↗ \(counts.shares ?? 0)"
                     + " · ⊕ \(counts.subscribers ?? 0)")
                    .font(.caption2).foregroundStyle(Theme.t2)
            }
            ForEach(subs, id: \.identity) { s in
                let who = s.actor_id ?? "?"
                let tier = s.tier ?? ""
                Text("\(who) · \(tier)")
                    .font(.caption2).foregroundStyle(Theme.t2)
            }
            // The gift half. The backend requires a verified adult and says
            // plainly that a gift cannot be reversed; this card repeats it
            // beside the button rather than after the mistake.
            Text(L10n.t("crowd.gift.note", state.language))
                .font(.caption2).foregroundStyle(Theme.t2)
            HStack {
                TextField(L10n.t("crowd.gift.amount", state.language),
                          text: $giftAmount)
                    .textFieldStyle(.roundedBorder)
                TextField(L10n.t("crowd.gift.words", state.language),
                          text: $giftNote)
                    .textFieldStyle(.roundedBorder)
            }
            HStack {
                Button(L10n.t("crowd.gift", state.language)) {
                    run { _ = try await ApiClient.shared.gift(
                        kind: kind, subjectId: targetId,
                        amount: Double(giftAmount) ?? 0, note: giftNote,
                        token: state.token!) }
                }.disabled(busy || targetId.isEmpty || giftAmount.isEmpty)
                Button(L10n.t("crowd.gifts", state.language)) {
                    run { giftList = try await ApiClient.shared.gifts(
                        kind: kind, subjectId: targetId,
                        token: state.token!) }
                }.disabled(busy || targetId.isEmpty)
            }.font(.caption)
            ForEach(giftList, id: \.identity) { g in
                let giver = g.giver_id ?? "?"
                let words = g.note ?? ""
                Text("\(giver) · \(g.amount ?? 0) · \(words)")
                    .font(.caption2).foregroundStyle(Theme.t2)
            }
            if let note {
                Text(note).font(.caption2).foregroundStyle(Theme.t2)
            }
        }.card()
    }

    private func run(_ op: @escaping () async throws -> Void) {
        busy = true; note = nil
        Task {
            do { try await op() }
            catch { note = error.localizedDescription }
            busy = false
        }
    }
}

struct PartySection: View {
    @EnvironmentObject var state: AppState
    @State private var postId = ""
    @State private var partyTitle = ""
    @State private var partyId = ""
    @State private var card: PartyCard?
    @State private var lines: [PartyLine] = []
    @State private var draft = ""
    @State private var seekTo = ""
    @State private var context = ""
    @State private var note: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("party.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            TextField(L10n.t("party.post", state.language), text: $postId)
                .textFieldStyle(.roundedBorder)
            HStack {
                TextField(L10n.t("party.name", state.language),
                          text: $partyTitle)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("party.start", state.language)) {
                    run {
                        let out = try await ApiClient.shared.startParty(
                            postId: postId, hostId: state.pid!,
                            title: partyTitle, token: state.token!)
                        partyId = out.identity
                        card = out
                    }
                }.disabled(busy || postId.isEmpty)
            }.font(.caption)
            TextField(L10n.t("party.id", state.language), text: $partyId)
                .textFieldStyle(.roundedBorder)
            HStack {
                Button(L10n.t("party.join", state.language)) {
                    run { card = try await ApiClient.shared.joinParty(
                        partyId: partyId, memberId: state.pid!,
                        kind: "profile", token: state.token!) }
                }
                Button(L10n.t("party.show", state.language)) {
                    run {
                        card = try await ApiClient.shared.party(
                            partyId: partyId, token: state.token!)
                        lines = try await ApiClient.shared.partyChat(
                            partyId: partyId, token: state.token!)
                    }
                }
                Button(L10n.t("party.leave", state.language)) {
                    run { try await ApiClient.shared.leaveParty(
                        partyId: partyId, memberId: state.pid!,
                        token: state.token!) }
                }
                Button(L10n.t("party.end", state.language)) {
                    run { card = try await ApiClient.shared.endParty(
                        partyId: partyId, token: state.token!) }
                }
            }.font(.caption).disabled(busy || partyId.isEmpty)
            if let card {
                let name = card.title ?? ""
                let state = card.state ?? ""
                Text("\(name) · \(state) · \(card.position_s ?? 0)"
                     + " · \(card.members?.count ?? 0)")
                    .font(.caption2).foregroundStyle(Theme.t2)
            }
            HStack {
                TextField(L10n.t("party.seek", state.language), text: $seekTo)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("party.seek.go", state.language)) {
                    run { card = try await ApiClient.shared.seekParty(
                        partyId: partyId, hostId: state.pid!,
                        positionS: Int(seekTo) ?? 0, playing: true,
                        token: state.token!) }
                }.disabled(busy || partyId.isEmpty || seekTo.isEmpty)
            }.font(.caption)
            ForEach(lines, id: \.identity) { l in
                let who = l.member_id ?? "?"
                let said = l.body ?? ""
                Text("\(who): \(said)")
                    .font(.caption2).foregroundStyle(Theme.t2)
            }
            HStack {
                TextField(L10n.t("party.say", state.language), text: $draft)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("people.send", state.language)) {
                    run {
                        _ = try await ApiClient.shared.sayInParty(
                            partyId: partyId, memberId: state.pid!,
                            body: draft, token: state.token!)
                        draft = ""
                        lines = try await ApiClient.shared.partyChat(
                            partyId: partyId, token: state.token!)
                    }
                }.disabled(busy || partyId.isEmpty || draft.isEmpty)
            }.font(.caption)
            Button(L10n.t("party.context", state.language)) {
                run {
                    let out = try await ApiClient.shared.partyContext(
                        partyId: partyId, token: state.token!)
                    context = out["you_have_not_seen_it"] ?? ""
                }
            }.font(.caption).disabled(busy || partyId.isEmpty)
            if !context.isEmpty {
                // The one sentence the backend insists a synthetic member
                // carries: it has not seen the footage.
                Text(context).font(.caption2).foregroundStyle(Theme.t2)
            }
            if let note {
                Text(note).font(.caption2).foregroundStyle(Theme.t2)
            }
        }.card()
    }

    private func run(_ op: @escaping () async throws -> Void) {
        busy = true; note = nil
        Task {
            do { try await op() }
            catch { note = error.localizedDescription }
            busy = false
        }
    }
}

struct LendingSection: View {
    @EnvironmentObject var state: AppState
    @State private var vocabulary: GrantVocabulary?
    @State private var mine: [GrantCard] = []
    @State private var borrowerId = ""
    @State private var surface = "room"
    @State private var surfaceId = ""
    @State private var skillKind = ""
    @State private var skillRef = ""
    @State private var grantTitle = ""
    @State private var grantId = ""
    @State private var uses: [GrantUse] = []
    @State private var what = ""
    @State private var note: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("lend.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            Button(L10n.t("lend.rules", state.language)) {
                run { vocabulary = try await ApiClient.shared
                    .grantVocabulary() }
            }.font(.caption).disabled(busy)
            if let vocabulary {
                // The backend's own terms, verbatim — the shell renders the
                // rules it enforces rather than paraphrasing them.
                ForEach(vocabulary.terms, id: \.self) { t in
                    Text("· \(t)").font(.caption2).foregroundStyle(Theme.t2)
                }
            }
            TextField(L10n.t("lend.borrower", state.language),
                      text: $borrowerId)
                .textFieldStyle(.roundedBorder)
            HStack {
                TextField(L10n.t("lend.surface", state.language),
                          text: $surface)
                    .textFieldStyle(.roundedBorder)
                TextField(L10n.t("lend.surface.id", state.language),
                          text: $surfaceId)
                    .textFieldStyle(.roundedBorder)
            }
            HStack {
                TextField(L10n.t("lend.kind", state.language),
                          text: $skillKind)
                    .textFieldStyle(.roundedBorder)
                TextField(L10n.t("lend.ref", state.language),
                          text: $skillRef)
                    .textFieldStyle(.roundedBorder)
            }
            HStack {
                TextField(L10n.t("lend.name", state.language),
                          text: $grantTitle)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("lend.offer", state.language)) {
                    run {
                        let out = try await ApiClient.shared.offerGrant(
                            lenderId: state.pid!, borrowerId: borrowerId,
                            surface: surface, surfaceId: surfaceId,
                            skillKind: skillKind, skillRef: skillRef,
                            title: grantTitle, token: state.token!)
                        grantId = out.identity
                    }
                }.disabled(busy || borrowerId.isEmpty || grantTitle.isEmpty)
            }.font(.caption)
            Button(L10n.t("lend.mine", state.language)) {
                run {
                    mine = try await ApiClient.shared.myGrants(
                        personId: state.pid!, token: state.token!)
                    _ = try await ApiClient.shared.grantsInSurface(
                        surface: surface,
                        surfaceId: surfaceId.isEmpty ? "x" : surfaceId,
                        token: state.token!)
                }
            }.font(.caption).disabled(busy)
            ForEach(mine, id: \.identity) { g in
                let name = g.title ?? g.identity
                let state = g.state ?? ""
                Button("\(name) · \(state)") {
                    grantId = g.identity
                }.font(.caption2).foregroundStyle(Theme.t2)
            }
            TextField(L10n.t("lend.id", state.language), text: $grantId)
                .textFieldStyle(.roundedBorder)
            HStack {
                Button(L10n.t("lend.accept", state.language)) {
                    run { _ = try await ApiClient.shared.acceptGrant(
                        grantId: grantId, actorId: state.pid!,
                        token: state.token!) }
                }
                Button(L10n.t("lend.decline", state.language)) {
                    run { _ = try await ApiClient.shared.declineGrant(
                        grantId: grantId, actorId: state.pid!,
                        token: state.token!) }
                }
                Button(L10n.t("lend.close", state.language)) {
                    run { _ = try await ApiClient.shared.closeGrant(
                        grantId: grantId, actorId: state.pid!,
                        token: state.token!) }
                }
                Button(L10n.t("lend.show", state.language)) {
                    run {
                        let g = try await ApiClient.shared.grant(
                            grantId: grantId, token: state.token!)
                        note = "\(g.title ?? "") · \(g.state ?? "")"
                    }
                }
            }.font(.caption).disabled(busy || grantId.isEmpty)
            HStack {
                TextField(L10n.t("lend.what", state.language), text: $what)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("lend.use", state.language)) {
                    run { _ = try await ApiClient.shared.useGrant(
                        grantId: grantId, borrowerId: state.pid!,
                        what: what, token: state.token!) }
                }
                Button(L10n.t("lend.uses", state.language)) {
                    run { uses = try await ApiClient.shared.grantUses(
                        grantId: grantId, token: state.token!) }
                }
            }.font(.caption).disabled(busy || grantId.isEmpty)
            ForEach(uses, id: \.identity) { u in
                let when = u.used_at ?? ""
                let what = u.what ?? ""
                Text("\(when) · \(what)")
                    .font(.caption2).foregroundStyle(Theme.t2)
            }
            if let note {
                Text(note).font(.caption2).foregroundStyle(Theme.t2)
            }
        }.card()
    }

    private func run(_ op: @escaping () async throws -> Void) {
        busy = true; note = nil
        Task {
            do { try await op() }
            catch { note = error.localizedDescription }
            busy = false
        }
    }
}
