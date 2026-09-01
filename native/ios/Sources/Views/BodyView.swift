import SwiftUI

/// The body, the referral, the objection, the lobby and the dock — five
/// more blocks off the per-shell doorless records.
///
/// Each renders its backend's rules rather than inventing a fifth
/// opinion: a robot body's command log is the owner's audit trail and
/// intimacy is never a body dial; a referral is signed before it is
/// released and opens exactly once; an objection can be read and ended
/// by its own subject; a lobby's roster says what every callsign is; and
/// the dock reports where each face's real job lives.
struct BodySection: View {
    @EnvironmentObject var state: AppState
    @State private var robotId = ""
    @State private var log: [RobotCommandRow] = []
    @State private var skills: [RobotSkillRow] = []
    @State private var dials = ""
    @State private var pace = ""
    @State private var note: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("bot.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            TextField(L10n.t("bot.id", state.language), text: $robotId)
                .textFieldStyle(.roundedBorder)
            HStack {
                Button(L10n.t("bot.log", state.language)) {
                    run { log = try await ApiClient.shared.robotCommands(
                        robotId: robotId, token: state.token!) }
                }
                Button(L10n.t("bot.skills", state.language)) {
                    run { skills = try await ApiClient.shared.robotSkills(
                        robotId: robotId, token: state.token!) }
                }
                Button(L10n.t("bot.dials", state.language)) {
                    run {
                        let s = try await ApiClient.shared.robotSteering(
                            robotId: robotId, token: state.token!)
                        dials = "\(s.values ?? [:])"
                    }
                }
                Button(L10n.t("bot.unbind", state.language)) {
                    run { try await ApiClient.shared.unbindRobot(
                        robotId: robotId, token: state.token!) }
                }
            }.font(.caption).disabled(busy || robotId.isEmpty)
            HStack {
                TextField(L10n.t("bot.pace", state.language), text: $pace)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("bot.dials.set", state.language)) {
                    run {
                        let s = try await ApiClient.shared.steerRobot(
                            robotId: robotId,
                            values: ["pace": Int(pace) ?? 50],
                            token: state.token!)
                        dials = "\(s.values ?? [:])"
                    }
                }.disabled(busy || robotId.isEmpty || pace.isEmpty)
            }.font(.caption)
            if !dials.isEmpty {
                Text(dials).font(.caption2).foregroundStyle(Theme.t2)
            }
            ForEach(log, id: \.identity) { c in
                let what = c.command ?? ""
                let when = c.created_at ?? ""
                Text("\(when) · \(what)")
                    .font(.caption2).foregroundStyle(Theme.t2)
            }
            ForEach(skills) { s in
                let name = s.title ?? s.id
                let pack = s.pack_title ?? ""
                Text("\(name) · \(pack)")
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

struct ReferralSection: View {
    @EnvironmentObject var state: AppState
    @State private var area = ""
    @State private var clinicians: [ClinicianRow] = []
    @State private var providerId = ""
    @State private var referralId = ""
    @State private var signatureId = ""
    @State private var linkToken = ""
    @State private var replyDraft = ""
    @State private var note: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("refer.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            HStack {
                TextField(L10n.t("refer.area", state.language), text: $area)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("refer.match", state.language)) {
                    run { clinicians = try await ApiClient.shared
                        .matchClinicians(area: area) }
                }.disabled(busy || area.isEmpty)
            }.font(.caption)
            ForEach(clinicians, id: \.identity) { c in
                let name = c.name ?? c.identity
                let what = c.expertise ?? ""
                Button("\(name) · \(what)") { providerId = c.identity }
                    .font(.caption2).foregroundStyle(Theme.t2)
            }
            TextField(L10n.t("refer.provider", state.language),
                      text: $providerId)
                .textFieldStyle(.roundedBorder)
            Button(L10n.t("refer.prepare", state.language)) {
                run {
                    let p = try await ApiClient.shared.prepareReferral(
                        interactorId: state.pid!, profileId: state.pid!,
                        providerId: providerId, token: state.token!)
                    referralId = p.identity
                }
            }.font(.caption).disabled(busy || providerId.isEmpty)
            TextField(L10n.t("refer.id", state.language), text: $referralId)
                .textFieldStyle(.roundedBorder)
            HStack {
                TextField(L10n.t("refer.signature", state.language),
                          text: $signatureId)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("refer.release", state.language)) {
                    run { _ = try await ApiClient.shared.releaseReferral(
                        referralId: referralId, signatureId: signatureId,
                        token: state.token!) }
                }.disabled(busy || referralId.isEmpty || signatureId.isEmpty)
            }.font(.caption)
            TextField(L10n.t("refer.token", state.language),
                      text: $linkToken)
                .textFieldStyle(.roundedBorder)
            HStack {
                Button(L10n.t("refer.open", state.language)) {
                    run {
                        let p = try await ApiClient.shared.openReferral(
                            referralId: referralId, linkToken: linkToken)
                        note = p.status ?? ""
                    }
                }
                TextField(L10n.t("refer.words", state.language),
                          text: $replyDraft)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("refer.reply", state.language)) {
                    run { _ = try await ApiClient.shared.replyToReferral(
                        referralId: referralId, linkToken: linkToken,
                        content: replyDraft) }
                }.disabled(busy || replyDraft.isEmpty)
            }.font(.caption).disabled(busy || referralId.isEmpty
                                      || linkToken.isEmpty)
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

struct ObjectionSection: View {
    @EnvironmentObject var state: AppState
    @State private var objectionId = ""
    @State private var line = ""
    @State private var events: [ObjectionAudit.Event] = []
    @State private var note: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("object.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            TextField(L10n.t("object.id", state.language),
                      text: $objectionId)
                .textFieldStyle(.roundedBorder)
            HStack {
                Button(L10n.t("object.show", state.language)) {
                    run {
                        let o = try await ApiClient.shared.objection(
                            objectionId: objectionId)
                        line = o.status ?? ""
                    }
                }
                Button(L10n.t("object.audit", state.language)) {
                    run {
                        let a = try await ApiClient.shared.objectionAudit(
                            objectionId: objectionId, token: state.token!)
                        events = a.audit_events ?? []
                    }
                }
                Button(L10n.t("object.withdraw", state.language)) {
                    run {
                        let o = try await ApiClient.shared
                            .withdrawObjectionConsent(
                                objectionId: objectionId)
                        line = o.status ?? ""
                    }
                }
                Button(L10n.t("object.revoke", state.language)) {
                    run {
                        let o = try await ApiClient.shared
                            .revokeObjectionBasis(objectionId: objectionId)
                        line = o.status ?? ""
                    }
                }
            }.font(.caption).disabled(busy || objectionId.isEmpty)
            // The reviewer's verb, drawn with its gate named: an owner
            // cannot adjudicate an objection against their own profile.
            Button(L10n.t("object.resolve", state.language) + " — "
                   + L10n.t("object.outcome", state.language)) {
                run {
                    let o = try await ApiClient.shared.resolveObjection(
                        objectionId: objectionId, outcome: "dismiss",
                        token: state.token!)
                    line = o.status ?? ""
                }
            }.font(.caption).disabled(busy || objectionId.isEmpty)
            if !line.isEmpty {
                Text(line).font(.caption2).foregroundStyle(Theme.t2)
            }
            ForEach(events, id: \.identity) { e in
                let what = e.event ?? ""
                let mark = (e.sealed ?? false) ? " ◆" : ""
                Text("\(what)\(mark)")
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

struct LobbySection: View {
    @EnvironmentObject var state: AppState
    @State private var rules: [String] = []
    @State private var sessionId = ""
    @State private var memberKind = "profile"
    @State private var memberId = ""
    @State private var role = "teammate"
    @State private var roster: [LobbySeat] = []
    @State private var note: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("lobby.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            Button(L10n.t("lobby.rules", state.language)) {
                run { rules = try await ApiClient.shared.lobbyRules() }
            }.font(.caption).disabled(busy)
            ForEach(rules, id: \.self) { r in
                Text("· \(r)").font(.caption2).foregroundStyle(Theme.t2)
            }
            TextField(L10n.t("lobby.session", state.language),
                      text: $sessionId)
                .textFieldStyle(.roundedBorder)
            HStack {
                TextField(L10n.t("lobby.kind", state.language),
                          text: $memberKind)
                    .textFieldStyle(.roundedBorder)
                TextField(L10n.t("lobby.member", state.language),
                          text: $memberId)
                    .textFieldStyle(.roundedBorder)
                TextField(L10n.t("lobby.role", state.language), text: $role)
                    .textFieldStyle(.roundedBorder)
            }
            HStack {
                Button(L10n.t("lobby.seat", state.language)) {
                    run { _ = try await ApiClient.shared.seatInLobby(
                        sessionId: sessionId, memberKind: memberKind,
                        memberId: memberId, role: role,
                        token: state.token!) }
                }.disabled(busy || sessionId.isEmpty || memberId.isEmpty)
                Button(L10n.t("lobby.roster", state.language)) {
                    run { roster = try await ApiClient.shared.lobbyRoster(
                        sessionId: sessionId, token: state.token!) }
                }.disabled(busy || sessionId.isEmpty)
                Button(L10n.t("lobby.leave", state.language)) {
                    run { try await ApiClient.shared.leaveLobby(
                        sessionId: sessionId, memberId: memberId,
                        token: state.token!) }
                }.disabled(busy || sessionId.isEmpty || memberId.isEmpty)
                Button(L10n.t("lobby.context", state.language)) {
                    run {
                        let c = try await ApiClient.shared.lobbyContext(
                            sessionId: sessionId, token: state.token!)
                        note = c["note"]
                    }
                }.disabled(busy || sessionId.isEmpty)
            }.font(.caption)
            ForEach(roster) { s in
                // The honest roster: what each callsign *is* travels with it.
                let who = s.callsign ?? s.id
                let kind = s.member_kind ?? ""
                let seat = s.role ?? ""
                Text("\(who) · \(kind) · \(seat)")
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

struct DockSection: View {
    @EnvironmentObject var state: AppState
    @State private var faces: [String] = []
    @State private var faceName = ""
    @State private var corner = "bottom_right"
    @State private var dockState = "handle"
    @State private var line = ""
    @State private var note: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("dock.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            HStack {
                Button(L10n.t("dock.faces", state.language)) {
                    run { faces = try await ApiClient.shared.dockFaces() }
                }
                Button(L10n.t("dock.mine", state.language)) {
                    run {
                        let s = try await ApiClient.shared.dockSettings(
                            profileId: state.pid!, token: state.token!)
                        let where_ = s.corner ?? ""
                        let how = s.state ?? ""
                        line = "\(where_) · \(how)"
                    }
                }
            }.font(.caption).disabled(busy)
            ForEach(faces, id: \.self) { f in
                Button(f) { faceName = f }
                    .font(.caption2).foregroundStyle(Theme.t2)
            }
            HStack {
                TextField(L10n.t("dock.face", state.language),
                          text: $faceName)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("dock.where", state.language)) {
                    run {
                        let w = try await ApiClient.shared.dockWhere(
                            face: faceName)
                        line = "\(w["screen"] ?? "") · \(w["tab"] ?? "")"
                    }
                }
                Button(L10n.t("dock.face", state.language)) {
                    run {
                        let f = try await ApiClient.shared.dockFace(
                            profileId: state.pid!, name: faceName,
                            token: state.token!)
                        line = f["line"] ?? ""
                    }
                }
            }.font(.caption).disabled(busy || faceName.isEmpty)
            HStack {
                TextField(L10n.t("dock.corner", state.language),
                          text: $corner)
                    .textFieldStyle(.roundedBorder)
                TextField(L10n.t("dock.state", state.language),
                          text: $dockState)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("dock.set", state.language)) {
                    run { _ = try await ApiClient.shared.configureDock(
                        profileId: state.pid!, corner: corner,
                        state: dockState, token: state.token!) }
                }.disabled(busy)
            }.font(.caption)
            if !line.isEmpty {
                Text(line).font(.caption2).foregroundStyle(Theme.t2)
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
