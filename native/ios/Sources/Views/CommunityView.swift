import SwiftUI

/// The Chat tab, widened: talk to your profile, meet a stranger (anonymous,
/// consent-first matchmaking), or open a multiparty room where the profile
/// takes moderated turns of its own.
struct ChatHubView: View {
    @EnvironmentObject var state: AppState
    enum Tab: String, CaseIterable { case profile = "Profile", stranger = "Stranger", rooms = "Rooms" }
    @State private var tab: Tab = .profile

    var body: some View {
        VStack(spacing: 0) {
            Picker("", selection: $tab) {
                ForEach(Tab.allCases, id: \.self) { Text($0.rawValue).tag($0) }
            }
            .pickerStyle(.segmented)
            .padding(.horizontal, 20).padding(.top, 12)

            switch tab {
            case .profile: ChatView()
            case .stranger: StrangerSection()
            case .rooms: CommunityRoomsSection()
            }
        }
    }
}

/// Lazily mint (and remember) the device owner's interactor identity — the
/// same one Chat uses.
@MainActor
private func ensureInteractor(_ state: AppState) async throws -> String {
    if let id = state.interactorId { return id }
    let created = try await ApiClient.shared.createInteractor(name: "You")
    state.rememberInteractor(created.id, token: created.token)
    return created.id
}

// MARK: Stranger — anonymous friendly matchmaking

private struct StrangerSection: View {
    @EnvironmentObject var state: AppState
    @State private var alias = ""
    @State private var tier = "friendly"
    @State private var birthdate = ""
    @State private var waiting = false
    @State private var connectionId: String?
    @State private var matchedWith: String?
    @State private var messages: [ConnMsg] = []
    @State private var draft = ""
    @State private var error: String?

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                if let cid = connectionId {
                    conversation(cid)
                } else {
                    VStack(alignment: .leading, spacing: 10) {
                        Text(L10n.t("nc.stranger", state.language)).font(.headline).foregroundStyle(Theme.txt)
                        Text(L10n.t("nc.stranger.sub", state.language))
                            .font(.caption).foregroundStyle(Theme.t2)
                        Picker("", selection: $tier) {
                            Text(L10n.t("nc.tier.friendly", state.language)).tag("friendly")
                            Text(L10n.t("nc.tier.rated", state.language)).tag("rated")
                        }.pickerStyle(.segmented)
                        if tier == "rated" && !state.interactorVerified {
                            Text(L10n.t("nc.rated.sub", state.language))
                                .font(.caption).foregroundStyle(Theme.amber)
                            TextField(L10n.t("nc.birthdate.ph", state.language), text: $birthdate)
                                .foregroundStyle(Theme.txt).textInputAutocapitalization(.never)
                                .padding(10).background(Theme.scrBot)
                                .clipShape(RoundedRectangle(cornerRadius: 11))
                                .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                        }
                        TextField(L10n.t("nc.alias.ph", state.language), text: $alias)
                            .foregroundStyle(Theme.txt).textInputAutocapitalization(.never)
                            .padding(10).background(Theme.scrBot)
                            .clipShape(RoundedRectangle(cornerRadius: 11))
                            .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                        Button(L10n.t(waiting ? "nc.match.waiting" : "nc.match.find", state.language)) { join() }
                            .font(.subheadline.bold()).foregroundStyle(.white)
                            .frame(maxWidth: .infinity).padding(.vertical, 12)
                            .background(Theme.brand)
                            .clipShape(RoundedRectangle(cornerRadius: 12))
                            .disabled(tier == "rated" && !state.interactorVerified
                                      && birthdate.isEmpty)
                    }.card()
                }
                if let error { Text(error).font(.footnote).foregroundStyle(Theme.red) }
            }.padding(20)
        }
        // Roulette. The match is made by whichever side arrives second —
        // their join answers *them*, never the waiter — so while waiting we
        // poll our own route and drop straight into the conversation the
        // moment it exists. Never join again to ask: that re-queues us.
        .task(id: waiting) {
            while waiting && !Task.isCancelled {
                try? await Task.sleep(nanoseconds: 2_500_000_000)
                guard waiting, let token = state.interactorToken else { continue }
                if let r = try? await ApiClient.shared.myConnection(token: token),
                   r.status == "matched", let cid = r.connection_id {
                    connectionId = cid
                    matchedWith = r.matched_with
                    waiting = false
                    refresh(cid)
                }
            }
        }
    }

    @ViewBuilder
    private func conversation(_ cid: String) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Text(L10n.fill("nc.talking", state.language,
                               ["who": matchedWith ?? L10n.t("nc.a_stranger", state.language)]))
                    .font(.headline).foregroundStyle(Theme.txt)
                Spacer()
                Button(L10n.t("nc.end", state.language)) { end(cid) }
                    .font(.caption.bold()).foregroundStyle(Theme.red)
            }
            ForEach(messages, id: \.id) { m in
                HStack {
                    if m.from == "you" { Spacer(minLength: 40) }
                    VStack(alignment: .leading, spacing: 2) {
                        Text(m.content).font(.subheadline).foregroundStyle(Theme.txt)
                        if m.status == "blocked" {
                            Text(L10n.t("nc.blocked", state.language))
                                .font(.caption2).foregroundStyle(Theme.red)
                        }
                    }
                    .padding(.horizontal, 12).padding(.vertical, 9)
                    .background(m.from == "you" ? Theme.brandA.opacity(0.35)
                                                : Theme.card.opacity(0.9))
                    .clipShape(RoundedRectangle(cornerRadius: 13))
                    if m.from != "you" { Spacer(minLength: 40) }
                }
            }
            HStack(spacing: 8) {
                TextField(L10n.t("nc.say.ph", state.language), text: $draft)
                    .foregroundStyle(Theme.txt)
                    .padding(10).background(Theme.scrBot)
                    .clipShape(RoundedRectangle(cornerRadius: 11))
                    .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                Button(L10n.t("nc.send", state.language)) { send(cid) }
                    .font(.caption.bold()).foregroundStyle(.white)
                    .padding(.horizontal, 12).padding(.vertical, 10)
                    .background(Theme.brandA).clipShape(Capsule())
                    .disabled(draft.isEmpty)
                Button(L10n.t("nc.refresh", state.language)) { refresh(cid) }
                    .font(.caption).foregroundStyle(Theme.brandA)
            }
        }.card()
    }

    private func join() {
        error = nil
        Task {
            do {
                var interactor = try await ensureInteractor(state)
                var minted = false
                if tier == "rated" && !state.interactorVerified {
                    // Verify 18+: mint a fresh identity carrying the
                    // birthdate — the age wall checks it server-side.
                    let created = try await ApiClient.shared.createInteractor(
                        name: "You", birthdate: birthdate)
                    state.rememberInteractor(created.id, token: created.token)
                    interactor = created.id
                    minted = true
                }
                let r = try await ApiClient.shared.joinQueue(
                    interactorId: interactor, alias: alias, tier: tier,
                    token: state.interactorToken ?? "")
                if minted {
                    // The server admitted this identity to the rated queue,
                    // so its verification stands — remember that.
                    state.rememberInteractor(interactor, adult: true)
                }
                if r.status == "matched", let cid = r.connection_id {
                    connectionId = cid
                    matchedWith = r.matched_with
                    waiting = false
                    refresh(cid)
                } else {
                    waiting = true
                }
            } catch { self.error = error.localizedDescription }
        }
    }

    private func refresh(_ cid: String) {
        Task {
            guard let interactor = state.interactorId else { return }
            messages = (try? await ApiClient.shared.connectionMessages(
                cid: cid, interactorId: interactor,
                token: state.interactorToken ?? "")) ?? messages
        }
    }

    private func send(_ cid: String) {
        let text = draft
        draft = ""
        error = nil
        Task {
            do {
                let interactor = try await ensureInteractor(state)
                _ = try await ApiClient.shared.sendConnectionMessage(
                    cid: cid, interactorId: interactor, message: text,
                    token: state.interactorToken ?? "")
                refresh(cid)
            } catch { self.error = error.localizedDescription }
        }
    }

    private func end(_ cid: String) {
        Task {
            guard let interactor = state.interactorId else { return }
            try? await ApiClient.shared.endConnection(
                cid: cid, interactorId: interactor,
                token: state.interactorToken ?? "")
            connectionId = nil; matchedWith = nil; messages = []; waiting = false
        }
    }
}

// MARK: Rooms — multiparty; the profile takes moderated turns

private struct CommunityRoomsSection: View {
    @EnvironmentObject var state: AppState
    @State private var topic = ""
    @State private var templates: [RoomTemplate] = []
    @State private var room: RoomCreated?
    @State private var transcript: [RoomMsg] = []
    @State private var draft = ""
    @State private var busy = false
    @State private var error: String?

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                if let room {
                    roomView(room)
                } else {
                    VStack(alignment: .leading, spacing: 10) {
                        Text(L10n.t("nc.room.open", state.language)).font(.headline).foregroundStyle(Theme.txt)
                        Text(L10n.fill("nc.room.sub", state.language, ["name": state.displayName]))
                            .font(.caption).foregroundStyle(Theme.t2)
                        TextField(L10n.t("nc.topic.ph", state.language), text: $topic)
                            .foregroundStyle(Theme.txt)
                            .padding(10).background(Theme.scrBot)
                            .clipShape(RoundedRectangle(cornerRadius: 11))
                            .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                        Button(L10n.t("nc.room.here", state.language)) { create() }
                            .font(.subheadline.bold()).foregroundStyle(.white)
                            .frame(maxWidth: .infinity).padding(.vertical, 12)
                            .background(Theme.brand)
                            .clipShape(RoundedRectangle(cornerRadius: 12))
                            .disabled(topic.isEmpty || busy)
                        // The standing rooms: tapping one steps into the
                        // room itself — the live one when somebody is
                        // there, opened fresh when nobody is. The first
                        // build only filled the topic field, which minted
                        // a copy per press.
                        if !templates.isEmpty {
                            Text(L10n.t("nc.room.standing", state.language))
                                .font(.caption.bold()).foregroundStyle(Theme.t2)
                            ForEach(templates) { t in
                                let name = t.topic ?? t.key
                                let channel = t.channel ?? "chat"
                                Button("\(name) · \(channel)") {
                                    openStanding(t.key)
                                }.font(.caption2).foregroundStyle(Theme.brandA)
                            }
                        }
                    }.card()
                    .task {
                        templates = (try? await ApiClient.shared.roomTemplates()) ?? []
                    }
                }
                if let error { Text(error).font(.footnote).foregroundStyle(Theme.red) }
            }.padding(20)
        }
    }

    @ViewBuilder
    private func roomView(_ room: RoomCreated) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Text(room.topic).font(.headline).foregroundStyle(Theme.txt)
                Spacer()
                Button(L10n.t("nc.leave", state.language)) { self.room = nil; transcript = [] }
                    .font(.caption.bold()).foregroundStyle(Theme.red)
            }
            ForEach(transcript, id: \.id) { m in
                VStack(alignment: .leading, spacing: 2) {
                    Text(m.from).font(.caption2.bold())
                        .foregroundStyle(m.sender_kind == "profile" ? Theme.brandA : Theme.t2)
                    Text(m.content ?? "· blocked by moderation ·")
                        .font(.subheadline)
                        .foregroundStyle(m.content == nil ? Theme.t3 : Theme.txt)
                }
                .padding(.horizontal, 12).padding(.vertical, 8)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(Theme.card.opacity(0.9))
                .clipShape(RoundedRectangle(cornerRadius: 12))
            }
            HStack(spacing: 8) {
                TextField(L10n.t("nc.say.ph", state.language), text: $draft)
                    .foregroundStyle(Theme.txt)
                    .padding(10).background(Theme.scrBot)
                    .clipShape(RoundedRectangle(cornerRadius: 11))
                    .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                Button(L10n.t("nc.send", state.language)) { send(room.id) }
                    .font(.caption.bold()).foregroundStyle(.white)
                    .padding(.horizontal, 12).padding(.vertical, 10)
                    .background(Theme.brandA).clipShape(Capsule())
                    .disabled(draft.isEmpty || busy)
            }
            Button(busy ? "…" : "Let them talk (advance a turn)") { advance(room.id) }
                .font(.caption.bold()).foregroundStyle(Theme.brandA)
                .disabled(busy)
        }.card()
    }

    private func create() {
        guard let pid = state.pid else { return }
        busy = true; error = nil
        Task {
            do {
                let interactor = try await ensureInteractor(state)
                room = try await ApiClient.shared.createRoom(
                    topic: topic, profileId: pid, interactorId: interactor)
                topic = ""
                transcript = []
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func openStanding(_ key: String) {
        guard let pid = state.pid else { return }
        busy = true; error = nil
        Task {
            do {
                _ = try await ensureInteractor(state)
                room = try await ApiClient.shared.openStandingRoom(
                    key: key, profileId: pid,
                    token: state.interactorToken ?? "")
                transcript = []
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func reloadTranscript(_ roomId: String) async {
        guard let token = state.interactorToken else { return }
        transcript = (try? await ApiClient.shared.roomTranscript(
            roomId: roomId, token: token)) ?? transcript
    }

    private func send(_ roomId: String) {
        let text = draft
        draft = ""
        busy = true; error = nil
        Task {
            do {
                let interactor = try await ensureInteractor(state)
                _ = try await ApiClient.shared.roomMessage(
                    roomId: roomId, senderId: interactor, message: text,
                    token: state.interactorToken ?? "")
                await reloadTranscript(roomId)
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func advance(_ roomId: String) {
        busy = true; error = nil
        Task {
            do {
                _ = try await ApiClient.shared.roomAdvance(
                    roomId: roomId, token: state.interactorToken ?? "")
                await reloadTranscript(roomId)
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }
}
