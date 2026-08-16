import SwiftUI

/// The core loop: chat with the profile as an interactor. The interactor
/// identity is created lazily on first send and remembered; replies held by
/// moderation render as pending rather than silently vanishing.
struct ChatView: View {
    struct Bubble: Identifiable {
        let id = UUID()
        let mine: Bool
        let text: String
        let pending: Bool
        // The always-displayed watermark line on AI renders (never on yours).
        var mark: String? = nil
    }

    @EnvironmentObject var state: AppState
    @State private var messages: [Bubble] = []
    @State private var draft = ""
    @State private var busy = false
    @State private var error: String?
    // Spec clauses 2/12. Empty means "read my prompt and decide", which is what
    // the backend does on its own — and the reply says which way it went.
    @State private var role = ""
    @State private var rehearsal: ApiClient.RehearsalRoom?
    @State private var rhScenario = ""

    // Bringing somebody real into it. `people` is yours-first for whatever
    // area was asked about; `brief` is the whole file, read before anybody is
    // contacted, so declining is still free.
    @State private var realOpen = false
    @State private var realArea = ""
    @State private var people: [MyPerson] = []
    @State private var matter = ""
    @State private var grantToken = ""
    @State private var brief: BriefingPreview?

    var body: some View {
        VStack(spacing: 0) {
            ScrollViewReader { proxy in
                ScrollView {
                    VStack(alignment: .leading, spacing: 10) {
                        Text(L10n.t("tab.chat", state.language)).font(.title2.bold()).foregroundStyle(Theme.txt)
                        Text(L10n.fill("nchat.sub", state.language, ["name": state.displayName]))
                            .font(.footnote).foregroundStyle(Theme.t2)

                        // --- bring somebody real into this ---------------
                        Text(L10n.t("real.hdr", state.language))
                            .font(.headline).foregroundStyle(Theme.txt)
                        Text(L10n.t("real.pitch", state.language))
                            .font(.caption).foregroundStyle(Theme.t2)
                        if !realOpen {
                            Button(L10n.t("real.open", state.language)) {
                                realOpen = true
                                // Yours first, before any area is typed.
                                loadMyPeople()
                            }.font(.caption.bold()).foregroundStyle(Theme.brandA)
                        } else {
                            TextField(L10n.t("real.area.ph", state.language),
                                      text: $realArea)
                                .font(.footnote).foregroundStyle(Theme.txt)
                            Button(L10n.t("real.find", state.language)) {
                                findPeople()
                            }.font(.caption.bold()).foregroundStyle(Theme.brandA)
                            ForEach(people, id: \.provider_id) { p in
                                VStack(alignment: .leading, spacing: 3) {
                                    Text(p.name).font(.caption.bold())
                                        .foregroundStyle(Theme.txt)
                                    Text((p.yours
                                          ? L10n.t("real.yours", state.language)
                                          : L10n.t("real.found", state.language))
                                         + (p.preferred == true
                                            ? " · " + L10n.t("real.first", state.language)
                                            : ""))
                                        .font(.caption2).foregroundStyle(Theme.t2)
                                    if p.yours {
                                        if p.preferred != true {
                                            Button(L10n.t("real.prefer", state.language)) {
                                                preferPerson(p)
                                            }.font(.caption2).foregroundStyle(Theme.brandA)
                                        }
                                        Button(L10n.t("real.drop", state.language)) {
                                            dropPerson(p)
                                        }.font(.caption2).foregroundStyle(Theme.t2)
                                        Button(L10n.fill("real.preview", state.language,
                                                         ["name": p.name])) {
                                            previewFor(p)
                                        }.font(.caption2.bold()).foregroundStyle(Theme.brandA)
                                    } else {
                                        Button(L10n.t("real.keep", state.language)) {
                                            keepPerson(p)
                                        }.font(.caption2).foregroundStyle(Theme.brandA)
                                    }
                                }
                            }
                            TextField(L10n.t("real.matter.ph", state.language),
                                      text: $matter)
                                .font(.footnote).foregroundStyle(Theme.txt)
                            SecureField(L10n.t("real.grant.ph", state.language),
                                        text: $grantToken)
                                .font(.footnote).foregroundStyle(Theme.txt)
                            if let brief {
                                Text(brief.reads).font(.caption)
                                    .foregroundStyle(Theme.txt)
                                ForEach(brief.package.attachments, id: \.title) { a in
                                    Text("\(a.kind) · \(a.title)"
                                         + (a.sealed
                                            ? " · " + L10n.t("real.sealed", state.language)
                                            : ""))
                                        .font(.caption2).foregroundStyle(Theme.t2)
                                }
                            }
                        }

                        ForEach(messages) { m in
                            HStack {
                                if m.mine { Spacer(minLength: 40) }
                                VStack(alignment: .leading, spacing: 3) {
                                    Text(m.text)
                                        .font(.subheadline)
                                        .foregroundStyle(m.pending ? Theme.t2 : Theme.txt)
                                    if let mark = m.mark {
                                        Text(mark).font(.caption2).foregroundStyle(Theme.t3)
                                    }
                                }
                                .padding(.horizontal, 12).padding(.vertical, 9)
                                .background(m.mine ? Theme.brandA.opacity(0.35)
                                                   : Theme.card.opacity(0.9))
                                .clipShape(RoundedRectangle(cornerRadius: 13))
                                if !m.mine { Spacer(minLength: 40) }
                            }
                            .id(m.id)
                        }

                        if let error {
                            Text(error).font(.footnote).foregroundStyle(Theme.red)
                        }
                    }.padding(20)
                }
                .onChange(of: messages.count) { _ in
                    if let last = messages.last { proxy.scrollTo(last.id) }
                }
            }

            // Rehearsal: practice the hard conversation — the transcript
            // lives only in the room, and closing the room wipes it.
            HStack(spacing: 8) {
                if let room = rehearsal {
                    Text("🎭 " + room.scenario)
                        .font(.caption).foregroundStyle(Theme.t2)
                        .lineLimit(1)
                    Spacer()
                    Button(L10n.t("cht.rh.close", state.language)) { closeRoom() }
                        .font(.caption.bold()).foregroundStyle(Theme.red)
                } else {
                    TextField(L10n.t("cht.rh.scenario.ph", state.language),
                              text: $rhScenario)
                        .font(.caption).textFieldStyle(.roundedBorder)
                    Button(L10n.t("cht.rh.open", state.language)) { openRoom() }
                        .font(.caption.bold()).foregroundStyle(Theme.brandA)
                        .disabled(rhScenario.isEmpty || busy)
                }
            }
            .padding(.horizontal, 20).padding(.bottom, 6)

            // Spec clauses 2/12 — advisor counsels, collaborator co-creates,
            // operator executes. "Read my prompt" is the honest default: the
            // profile infers from the wording and the reply says which.
            Picker("", selection: $role) {
                Text(L10n.t("nchat.role.read", state.language)).tag("")
                Text(L10n.t("nchat.role.advisor", state.language)).tag("advisor")
                Text(L10n.t("nchat.role.collaborator", state.language)).tag("collaborator")
                Text(L10n.t("nchat.role.operator", state.language)).tag("operator")
            }
            .pickerStyle(.segmented)
            .padding(.horizontal, 20).padding(.bottom, 6)

            HStack(spacing: 10) {
                TextField(L10n.t("nchat.type.ph", state.language), text: $draft)
                    .foregroundStyle(Theme.txt)
                    .padding(.horizontal, 12).padding(.vertical, 10)
                    .background(Theme.scrBot)
                    .clipShape(RoundedRectangle(cornerRadius: 12))
                    .overlay(RoundedRectangle(cornerRadius: 12).stroke(Theme.line, lineWidth: 1))
                Button(action: send) {
                    if busy { ProgressView().tint(.white) }
                    else { Image(systemName: "paperplane.fill") }
                }
                .frame(width: 44, height: 40)
                .background(Theme.brand).foregroundStyle(.white)
                .clipShape(RoundedRectangle(cornerRadius: 12))
                .disabled(draft.isEmpty || busy)
            }
            .padding(.horizontal, 20).padding(.bottom, 12)
        }
    }

    private func loadMyPeople() {
        guard let iid = state.interactorId, let tok = state.interactorToken
        else { return }
        Task { people = (try? await ApiClient.shared.myPeople(
            interactor: iid, token: tok)) ?? [] }
    }

    private func findPeople() {
        guard let iid = state.interactorId, let tok = state.interactorToken
        else { return }
        Task { people = (try? await ApiClient.shared.peopleForArea(
            interactor: iid, area: realArea, token: tok)) ?? [] }
    }

    private func keepPerson(_ p: MyPerson) {
        guard let iid = state.interactorId, let tok = state.interactorToken
        else { return }
        Task {
            try? await ApiClient.shared.keepPerson(
                interactor: iid, providerId: p.provider_id, token: tok)
            findPeople()
        }
    }

    private func preferPerson(_ p: MyPerson) {
        guard let iid = state.interactorId, let tok = state.interactorToken
        else { return }
        Task {
            try? await ApiClient.shared.preferPerson(
                interactor: iid, providerId: p.provider_id, token: tok)
            loadMyPeople()
        }
    }

    private func dropPerson(_ p: MyPerson) {
        guard let iid = state.interactorId, let tok = state.interactorToken
        else { return }
        Task {
            try? await ApiClient.shared.dropPerson(
                interactor: iid, providerId: p.provider_id, token: tok)
            loadMyPeople()
        }
    }

    /// Nothing is sent by this — see ApiClient.previewBriefing.
    private func previewFor(_ p: MyPerson) {
        guard let iid = state.interactorId, let tok = state.interactorToken,
              let pid = state.pid else { return }
        Task {
            brief = try? await ApiClient.shared.previewBriefing(
                interactor: iid, profile: pid, providerId: p.provider_id,
                matter: matter, grantToken: grantToken, token: tok)
        }
    }

    private func openRoom() {
        guard let pid = state.pid else { return }
        busy = true; error = nil
        Task {
            do {
                var interactor = state.interactorId
                if interactor == nil {
                    let created = try await ApiClient.shared.createInteractor(name: "You")
                    state.rememberInteractor(created.id, token: created.token)
                    interactor = created.id
                }
                rehearsal = try await ApiClient.shared.openRehearsal(
                    id: pid, interactorId: interactor!, scenario: rhScenario)
                rhScenario = ""
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func closeRoom() {
        guard let pid = state.pid, let room = rehearsal else { return }
        Task {
            try? await ApiClient.shared.closeRehearsal(
                id: pid, rehearsalId: room.id)
            rehearsal = nil
        }
    }

    private func send() {
        guard let pid = state.pid, let token = state.token else { return }
        let text = draft
        draft = ""
        messages.append(Bubble(mine: true, text: text, pending: false))
        busy = true; error = nil
        Task {
            do {
                // Lazily mint the device owner's interactor identity once.
                var interactor = state.interactorId
                if interactor == nil {
                    let created = try await ApiClient.shared.createInteractor(name: "You")
                    state.rememberInteractor(created.id, token: created.token)
                    interactor = created.id
                }
                // An open rehearsal room takes the turn: nothing lands in
                // the remembered conversation, and the bubble says so.
                if let room = rehearsal {
                    let turn = try await ApiClient.shared.rehearse(
                        id: pid, rehearsalId: room.id, message: text)
                    messages.append(Bubble(
                        mine: false, text: turn.reply, pending: false,
                        mark: "🎭 " + room.scenario))
                    busy = false
                    return
                }
                let reply = try await ApiClient.shared.chat(
                    id: pid, token: token, interactorId: interactor!,
                    message: text, role: role.isEmpty ? nil : role)
                let p = reply.profile_message
                if let content = p.content, p.status == "approved" {
                    messages.append(Bubble(
                        mine: false, text: content, pending: false,
                        mark: p.watermark?.display?.line ?? "✦ AI"))
                    if let rc = reply.role_context {
                        messages.append(Bubble(
                            mine: false,
                            text: "◈ worked as \(rc.role) (\(rc.how))",
                            pending: true))
                    }
                    if let prov = reply.provenance {
                        messages.append(Bubble(
                            mine: false,
                            text: "ⓘ " + L10n.fill("nprv.generated", state.language,
                                                   ["model": prov.generated_by,
                                                    "n": "\(prov.grounded_in.source_items)",
                                                    "status": prov.moderation.status])
                                  + (prov.licensed_from.map {
                                        " · " + L10n.fill("nprv.licensed",
                                                          state.language,
                                                          ["source": $0]) } ?? ""),
                            pending: true))
                    }
                } else {
                    messages.append(Bubble(
                        mine: false,
                        text: "⏳ Held for review" +
                              (p.flag_reason.map { " — \($0)" } ?? ""),
                        pending: true))
                }
            } catch {
                self.error = error.localizedDescription
            }
            busy = false
        }
    }
}
