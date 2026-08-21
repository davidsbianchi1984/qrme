import PhotosUI
import SwiftUI

/// Seven small blocks that close out the mid-sized doorless groups: the
/// signature a person can read and a stranger can verify, the
/// deployment's own mail settings, the room-microphone disclosure, the
/// fixed screen, the membership, the consented handoff, and the
/// crowdfunding campaign.
struct SealSection: View {
    @EnvironmentObject var state: AppState
    @State private var sigId = ""
    @State private var credId = ""
    @State private var line = ""
    @State private var note: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("sig.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            TextField(L10n.t("sig.id", state.language), text: $sigId)
                .textFieldStyle(.roundedBorder)
            HStack {
                Button(L10n.t("sig.certificate", state.language)) {
                    run {
                        let c = try await ApiClient.shared
                            .signatureCertificate(sigId: sigId)
                        let who = c.printed_name ?? ""
                        let why = c.meaning ?? ""
                        line = "\(who) · \(why) · \(c.signed_at ?? "")"
                    }
                }.disabled(busy || sigId.isEmpty)
                Button(L10n.t("sig.verify", state.language)) {
                    // A deliberately malformed package: the point the door
                    // proves is that the verifier answers a stranger at
                    // all, and its refusal names what a package must be.
                    run {
                        let v = try await ApiClient.shared
                            .verifySignaturePackage(package: [:])
                        line = "\(v.stands)"
                    }
                }
                Button(L10n.t("sig.ceremony", state.language)) {
                    let url = ApiClient.shared.signatureCeremonyUrl()
                    note = url.absoluteString
                }
            }.font(.caption)
            TextField(L10n.t("sig.credential", state.language),
                      text: $credId)
                .textFieldStyle(.roundedBorder)
            Button(L10n.t("sig.proofing", state.language)) {
                run { _ = try await ApiClient.shared.reproofCredential(
                    rowId: credId, level: "verified", attestor: state.pid!,
                    method: "document", ref: "in-person",
                    token: state.token!) }
            }.font(.caption).disabled(busy || credId.isEmpty)
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

struct MailSection: View {
    @EnvironmentObject var state: AppState
    @State private var host = ""
    @State private var port = "587"
    @State private var sender = ""
    @State private var testTo = ""
    @State private var line = ""
    @State private var note: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("mail.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            Button(L10n.t("mail.title", state.language)) {
                run {
                    let m = try await ApiClient.shared.mailSettings()
                    let how = m.transport ?? ""
                    let via = m.host ?? ""
                    line = "\(how) · \(via)"
                }
            }.font(.caption).disabled(busy)
            HStack {
                TextField(L10n.t("mail.host", state.language), text: $host)
                    .textFieldStyle(.roundedBorder)
                TextField(L10n.t("mail.port", state.language), text: $port)
                    .textFieldStyle(.roundedBorder)
                TextField(L10n.t("mail.sender", state.language),
                          text: $sender)
                    .textFieldStyle(.roundedBorder)
            }
            HStack {
                Button(L10n.t("mail.save", state.language)) {
                    run { _ = try await ApiClient.shared.saveMailSettings(
                        host: host, port: Int(port) ?? 587, sender: sender,
                        token: state.token!) }
                }.disabled(busy || host.isEmpty)
                Button(L10n.t("mail.forget", state.language)) {
                    run { try await ApiClient.shared.forgetMailSettings(
                        token: state.token!) }
                }.disabled(busy)
            }.font(.caption)
            HStack {
                TextField(L10n.t("mail.to", state.language), text: $testTo)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("mail.test", state.language)) {
                    run { try await ApiClient.shared.testMailSettings(
                        to: testTo, token: state.token!) }
                }.disabled(busy || testTo.isEmpty)
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

struct RoomsSection: View {
    @EnvironmentObject var state: AppState
    @State private var list: [RoomCard] = []
    @State private var roomId = ""
    @State private var micList: [MicDisclosure.Lent] = []
    @State private var note: String?
    @State private var busy = false
    @State private var guestId = ""
    @State private var scene: RoomFaces?
    @State private var pick: PhotosPickerItem?
    @State private var share: PhotosPickerItem?

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("room.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            Button(L10n.t("room.list", state.language)) {
                run { list = try await ApiClient.shared.rooms() }
            }.font(.caption).disabled(busy)
            ForEach(list) { r in
                let topic = r.topic ?? r.id
                let channel = r.channel ?? ""
                Button("\(topic) · \(channel) · \(r.participants ?? 0)") {
                    roomId = r.id
                }.font(.caption2).foregroundStyle(Theme.t2)
            }
            TextField(L10n.t("room.id", state.language), text: $roomId)
                .textFieldStyle(.roundedBorder)
            // The list used to show rooms nobody could enter — the door
            // in was frozen at creation. Joining takes the interactor
            // token; a room id alone is not being here.
            Button(L10n.t("room.join", state.language)) {
                run { try await ApiClient.shared.joinRoom(
                    roomId: roomId, token: state.interactorToken ?? "") }
            }.font(.caption).disabled(busy || roomId.isEmpty
                                      || state.interactorToken == nil)
            HStack {
                Button(L10n.t("room.mic.lend", state.language)) {
                    run { try await ApiClient.shared.lendRoomMic(
                        roomId: roomId, interactorId: state.pid!,
                        token: state.token!) }
                }
                Button(L10n.t("room.mic.back", state.language)) {
                    run { try await ApiClient.shared.takeBackRoomMic(
                        roomId: roomId, interactorId: state.pid!,
                        token: state.token!) }
                }
                Button(L10n.t("room.mic.who", state.language)) {
                    run {
                        let d = try await ApiClient.shared.roomMicDisclosure(
                            roomId: roomId, token: state.token!)
                        micList = d.microphones_lent ?? []
                    }
                }
            }.font(.caption).disabled(busy || roomId.isEmpty)
            ForEach(micList) { m in
                let who = m.interactor_id ?? "?"
                let device = m.device ?? ""
                Text("\(who) · \(device)")
                    .font(.caption2).foregroundStyle(Theme.t2)
            }

            // Asking somebody in. Without this the only way to get a
            // particular person into a particular room was to name them in
            // the create body, which needs their id before the room exists.
            Divider().overlay(Theme.line)
            TextField(L10n.t("room.ask.who", state.language), text: $guestId)
                .textFieldStyle(.roundedBorder)
            HStack {
                Button(L10n.t("room.ask", state.language)) {
                    run {
                        let again = try await ApiClient.shared.inviteToRoom(
                            roomId: roomId, profileId: guestId,
                            token: state.interactorToken ?? state.token ?? "")
                        note = L10n.t(again ? "room.ask.already" : "room.asked",
                                      state.language)
                    }
                }.disabled(busy || roomId.isEmpty || guestId.isEmpty)
                // Authorized as the guest, so this is the profile owner's
                // press and not the host's — the half that makes it an
                // invitation rather than a seating chart.
                Button(L10n.t("room.ask.accept", state.language)) {
                    run { try await ApiClient.shared.acceptRoomInvite(
                        roomId: roomId, profileId: state.pid ?? "",
                        ownerToken: state.token ?? "") }
                }.disabled(busy || roomId.isEmpty || state.pid == nil)
            }.font(.caption)

            // What each box in the room holds. All three answers are a box,
            // so turning a camera off keeps you in the scene — see
            // qrme/roomface.py.
            Divider().overlay(Theme.line)
            Text(L10n.t("room.face.title", state.language))
                .font(.subheadline).foregroundStyle(Theme.txt)
            HStack {
                Button(L10n.t("room.face.camera", state.language)) {
                    run { try await ApiClient.shared.setRoomFace(
                        roomId: roomId, interactorId: state.interactorId ?? "",
                        showing: "camera",
                        token: state.interactorToken ?? "")
                        scene = try await ApiClient.shared.roomFaces(
                            roomId: roomId,
                            token: state.interactorToken ?? "") }
                }
                Button(L10n.t("room.face.plain", state.language)) {
                    run { try await ApiClient.shared.clearRoomFace(
                        roomId: roomId, interactorId: state.interactorId ?? "",
                        token: state.interactorToken ?? "")
                        scene = try await ApiClient.shared.roomFaces(
                            roomId: roomId,
                            token: state.interactorToken ?? "") }
                }
                Button(L10n.t("room.face.who", state.language)) {
                    run { scene = try await ApiClient.shared.roomFaces(
                        roomId: roomId,
                        token: state.interactorToken ?? "") }
                }
            }.font(.caption).disabled(busy || roomId.isEmpty
                                      || state.interactorToken == nil)
            // A real picker rather than a filename field: the photograph
            // this asks for is one already on the phone, and typing its name
            // is not how anybody has ever chosen a picture.
            PhotosPicker(selection: $pick, matching: .images) {
                Text(L10n.t("room.face.photo", state.language)).font(.caption)
            }.disabled(busy || roomId.isEmpty || state.interactorToken == nil)
            // Sharing INTO the room, not standing in for you: the picture
            // or video lands as a turn everybody here reads. Same picker
            // discipline as the face — a thing already on the phone.
            PhotosPicker(selection: $share, matching: .any(of: [.images, .videos])) {
                Text(L10n.t("room.share", state.language)).font(.caption)
            }.disabled(busy || roomId.isEmpty || state.interactorToken == nil)
            if let scene {
                // Everybody's, not just mine. A scene each person draws from
                // their own state alone is not a scene.
                ForEach(Array((scene.faces ?? [:]).keys.sorted()), id: \.self) { who in
                    let f = scene.faces?[who]
                    Text("\(who) · \(f?.means ?? "")")
                        .font(.caption2).foregroundStyle(Theme.t2)
                }
                // The masks ride with the scene, so a face that is not a
                // face says so on the frame it is drawn in.
                ForEach(scene.wearing ?? []) { w in
                    Text(w.disclosure ?? w.title ?? "")
                        .font(.caption2).foregroundStyle(Theme.t2)
                }
                if let line = scene.note {
                    Text(line).font(.caption2).foregroundStyle(Theme.t2)
                }
            }

            if let note {
                Text(note).font(.caption2).foregroundStyle(Theme.t2)
            }
        }.card()
        .onChange(of: pick) { item in
            guard let item else { return }
            run {
                guard let data = try await item.loadTransferable(
                    type: Data.self) else { return }
                _ = try await ApiClient.shared.uploadRoomFace(
                    roomId: roomId, interactorId: state.interactorId ?? "",
                    filename: "face.jpg", data: data,
                    token: state.interactorToken ?? "")
                scene = try await ApiClient.shared.roomFaces(
                    roomId: roomId, token: state.interactorToken ?? "")
                pick = nil
            }
        }
        .onChange(of: share) { item in
            guard let item else { return }
            run {
                guard let data = try await item.loadTransferable(
                    type: Data.self) else { return }
                let shared = try await ApiClient.shared.shareInRoom(
                    roomId: roomId, interactorId: state.interactorId ?? "",
                    filename: "shared.bin", data: data,
                    token: state.interactorToken ?? "")
                note = shared.message.from
                share = nil
            }
        }
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

struct WallScreenSection: View {
    @EnvironmentObject var state: AppState
    @State private var rules: [String] = []
    @State private var displayId = ""
    @State private var faces = ""
    @State private var line = ""
    @State private var note: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("disp.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            Button(L10n.t("disp.rules", state.language)) {
                run { rules = try await ApiClient.shared.displayRules() }
            }.font(.caption).disabled(busy)
            ForEach(rules, id: \.self) { r in
                Text("· \(r)").font(.caption2).foregroundStyle(Theme.t2)
            }
            TextField(L10n.t("disp.id", state.language), text: $displayId)
                .textFieldStyle(.roundedBorder)
            HStack {
                Button(L10n.t("disp.show", state.language)) {
                    run {
                        let d = try await ApiClient.shared.display(
                            displayId: displayId)
                        let kind = d.kind ?? ""
                        line = "\(kind) · \(d.faces ?? [])"
                    }
                }
                TextField(L10n.t("disp.faces", state.language),
                          text: $faces)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("disp.faces", state.language)) {
                    run { _ = try await ApiClient.shared.setDisplayFaces(
                        displayId: displayId,
                        faces: faces.split(separator: ",").map {
                            $0.trimmingCharacters(in: .whitespaces) },
                        token: state.token!) }
                }.disabled(busy || faces.isEmpty)
                Button(L10n.t("disp.down", state.language)) {
                    run { try await ApiClient.shared.takeDownDisplay(
                        displayId: displayId, token: state.token!) }
                }
            }.font(.caption).disabled(busy || displayId.isEmpty)
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

struct PlanSection: View {
    @EnvironmentObject var state: AppState
    @State private var accountId = ""
    @State private var plan = "basic"
    @State private var line = ""
    @State private var note: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("member.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            TextField(L10n.t("member.account", state.language),
                      text: $accountId)
                .textFieldStyle(.roundedBorder)
            HStack {
                Button(L10n.t("member.show", state.language)) {
                    run {
                        let m = try await ApiClient.shared.membership(
                            accountId: accountId, token: state.token!)
                        let held = m.plan ?? ""
                        line = "\(held) · \(m.status ?? "")"
                    }
                }
                TextField(L10n.t("member.plan", state.language), text: $plan)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("member.join", state.language)) {
                    run { _ = try await ApiClient.shared.joinPlan(
                        accountId: accountId, plan: plan,
                        token: state.token!) }
                }.disabled(busy || plan.isEmpty)
                Button(L10n.t("member.cancel", state.language)) {
                    run { _ = try await ApiClient.shared.cancelMembership(
                        accountId: accountId, token: state.token!) }
                }
            }.font(.caption).disabled(busy || accountId.isEmpty)
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

struct HandoffSection: View {
    @EnvironmentObject var state: AppState
    @State private var providerId = ""
    @State private var handoffId = ""
    @State private var linkToken = ""
    @State private var line = ""
    @State private var note: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("hand.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            HStack {
                TextField(L10n.t("hand.provider", state.language),
                          text: $providerId)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("hand.create", state.language)) {
                    run {
                        let h = try await ApiClient.shared.createHandoff(
                            interactorId: state.pid!, profileId: state.pid!,
                            providerId: providerId, token: state.token!)
                        handoffId = h.identity
                        linkToken = h.token ?? ""
                    }
                }.disabled(busy || providerId.isEmpty)
            }.font(.caption)
            TextField(L10n.t("hand.id", state.language), text: $handoffId)
                .textFieldStyle(.roundedBorder)
            TextField(L10n.t("hand.token", state.language),
                      text: $linkToken)
                .textFieldStyle(.roundedBorder)
            HStack {
                Button(L10n.t("hand.open", state.language)) {
                    run {
                        let h = try await ApiClient.shared.openHandoff(
                            handoffId: handoffId, linkToken: linkToken)
                        let who = h.provider ?? ""
                        line = "\(who) · \(h.sealed ?? false)"
                    }
                }.disabled(busy || handoffId.isEmpty || linkToken.isEmpty)
                Button(L10n.t("hand.revoke", state.language)) {
                    run { try await ApiClient.shared.revokeHandoff(
                        handoffId: handoffId, token: state.token!) }
                }.disabled(busy || handoffId.isEmpty)
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

struct CampaignSection: View {
    @EnvironmentObject var state: AppState
    @State private var campaignId = ""
    @State private var amount = ""
    @State private var words = ""
    @State private var line = ""
    @State private var note: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("camp.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            TextField(L10n.t("camp.id", state.language), text: $campaignId)
                .textFieldStyle(.roundedBorder)
            HStack {
                Button(L10n.t("camp.show", state.language)) {
                    run {
                        let c = try await ApiClient.shared.campaign(
                            campaignId: campaignId)
                        let name = c.title ?? ""
                        line = "\(name) · \(c.raised ?? 0)"
                             + " / \(c.goal ?? 0) · \(c.status ?? "")"
                    }
                }
                Button(L10n.t("camp.close", state.language)) {
                    run { _ = try await ApiClient.shared.closeCampaign(
                        campaignId: campaignId, token: state.token!) }
                }
            }.font(.caption).disabled(busy || campaignId.isEmpty)
            HStack {
                TextField(L10n.t("camp.amount", state.language),
                          text: $amount)
                    .textFieldStyle(.roundedBorder)
                TextField(L10n.t("crowd.gift.words", state.language),
                          text: $words)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("camp.give", state.language)) {
                    run { _ = try await ApiClient.shared.donate(
                        campaignId: campaignId,
                        amount: Double(amount) ?? 0, note: words) }
                }.disabled(busy || campaignId.isEmpty || amount.isEmpty)
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
