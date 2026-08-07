import SwiftUI

/// The place, the camera, the organization and the tour — four more
/// blocks off the per-shell doorless records.
///
/// The place card is disclosure-first: whose corner this is, who here
/// has lent a microphone, who wears what over their face — each readable
/// by everyone present, because a disclosure only its subject can see is
/// not a disclosure. The camera opens with its published refusals. The
/// organization is the owner's; the tour is anybody's.
struct PlaceSection: View {
    @EnvironmentObject var state: AppState
    @State private var surface = "room"
    @State private var surfaceId = ""
    @State private var whoseLine = ""
    @State private var micList: [MicDisclosure.Lent] = []
    @State private var wornList: [WornDisclosure.Worn] = []
    @State private var maskKind = "avatar"
    @State private var maskName = ""
    @State private var note: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("place.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            HStack {
                TextField(L10n.t("place.surface", state.language),
                          text: $surface)
                    .textFieldStyle(.roundedBorder)
                TextField(L10n.t("place.surface.id", state.language),
                          text: $surfaceId)
                    .textFieldStyle(.roundedBorder)
            }
            Button(L10n.t("place.whose", state.language)) {
                run {
                    let card = try await ApiClient.shared.whose(
                        surface: surface, surfaceId: surfaceId)
                    let who = card.display_name ?? ""
                    whoseLine = who
                }
            }.font(.caption).disabled(busy || surfaceId.isEmpty)
            if !whoseLine.isEmpty {
                Text(whoseLine).font(.caption2).foregroundStyle(Theme.t2)
            }
            HStack {
                Button(L10n.t("place.mic.lend", state.language)) {
                    run { _ = try await ApiClient.shared.lendMicrophone(
                        surface: surface, surfaceId: surfaceId,
                        interactorId: state.pid!, token: state.token!) }
                }
                Button(L10n.t("place.mic.back", state.language)) {
                    run { try await ApiClient.shared.takeBackMicrophone(
                        surface: surface, surfaceId: surfaceId,
                        interactorId: state.pid!, token: state.token!) }
                }
                Button(L10n.t("place.mic.who", state.language)) {
                    run {
                        let d = try await ApiClient.shared
                            .microphoneDisclosure(
                                surface: surface, surfaceId: surfaceId,
                                token: state.token!)
                        micList = d.lent ?? []
                    }
                }
            }.font(.caption).disabled(busy || surfaceId.isEmpty)
            ForEach(micList) { m in
                let who = m.interactor_id ?? "?"
                let device = m.device ?? ""
                Text("\(who) · \(device)")
                    .font(.caption2).foregroundStyle(Theme.t2)
            }
            HStack {
                TextField(L10n.t("place.mask.kind", state.language),
                          text: $maskKind)
                    .textFieldStyle(.roundedBorder)
                TextField(L10n.t("place.mask.name", state.language),
                          text: $maskName)
                    .textFieldStyle(.roundedBorder)
            }
            HStack {
                Button(L10n.t("place.mask.wear", state.language)) {
                    run { _ = try await ApiClient.shared.wearOverlay(
                        surface: surface, surfaceId: surfaceId,
                        interactorId: state.pid!, kind: maskKind,
                        title: maskName, token: state.token!) }
                }.disabled(busy || surfaceId.isEmpty || maskName.isEmpty)
                Button(L10n.t("place.mask.off", state.language)) {
                    run { try await ApiClient.shared.takeOffOverlay(
                        surface: surface, surfaceId: surfaceId,
                        interactorId: state.pid!, token: state.token!) }
                }.disabled(busy || surfaceId.isEmpty)
                Button(L10n.t("place.mask.who", state.language)) {
                    run {
                        let d = try await ApiClient.shared.wornOverlays(
                            surface: surface, surfaceId: surfaceId,
                            token: state.token!)
                        wornList = d.worn ?? []
                    }
                }.disabled(busy || surfaceId.isEmpty)
            }.font(.caption)
            ForEach(wornList) { w in
                let who = w.interactor_id ?? "?"
                let what = w.title ?? w.kind ?? ""
                Text("\(who) · \(what)")
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

struct CameraSection: View {
    @EnvironmentObject var state: AppState
    @State private var surface = "room"
    @State private var surfaceId = ""
    @State private var subject = "object"
    @State private var viewerId = ""
    @State private var minutes = "10"
    @State private var sessionId = ""
    @State private var sessions: [CameraSession] = []
    @State private var refusals: [String] = []
    @State private var note: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("cam.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            Button(L10n.t("cam.rules", state.language)) {
                run {
                    let v = try await ApiClient.shared.cameraVocabulary()
                    refusals = (v.never ?? [:]).values.sorted()
                    _ = try await ApiClient.shared.bystanderGuidance(
                        subject: subject)
                }
            }.font(.caption).disabled(busy)
            ForEach(refusals, id: \.self) { r in
                // The published refusals, verbatim: a client that knew only
                // the allowed combinations would draw a refused one as a
                // missing feature rather than a decision.
                Text("· \(r)").font(.caption2).foregroundStyle(Theme.t2)
            }
            HStack {
                TextField(L10n.t("place.surface", state.language),
                          text: $surface)
                    .textFieldStyle(.roundedBorder)
                TextField(L10n.t("place.surface.id", state.language),
                          text: $surfaceId)
                    .textFieldStyle(.roundedBorder)
            }
            HStack {
                TextField(L10n.t("cam.subject", state.language),
                          text: $subject)
                    .textFieldStyle(.roundedBorder)
                TextField(L10n.t("cam.viewer", state.language),
                          text: $viewerId)
                    .textFieldStyle(.roundedBorder)
                TextField(L10n.t("cam.minutes", state.language),
                          text: $minutes)
                    .textFieldStyle(.roundedBorder)
            }
            HStack {
                Button(L10n.t("cam.open", state.language)) {
                    run {
                        let s = try await ApiClient.shared.openCamera(
                            holderId: state.pid!, surface: surface,
                            surfaceId: surfaceId, subject: subject,
                            viewerKind: "person", viewerId: viewerId,
                            minutes: Int(minutes) ?? 10,
                            token: state.token!)
                        sessionId = s.identity
                    }
                }.disabled(busy || surfaceId.isEmpty || viewerId.isEmpty)
                Button(L10n.t("cam.mine", state.language)) {
                    run { sessions = try await ApiClient.shared.myCameras(
                        holderId: state.pid!, token: state.token!) }
                }.disabled(busy)
                Button(L10n.t("cam.disclosure", state.language)) {
                    run {
                        let d = try await ApiClient.shared.cameraDisclosure(
                            surface: surface, surfaceId: surfaceId,
                            token: state.token!)
                        note = "\(d)"
                    }
                }.disabled(busy || surfaceId.isEmpty)
            }.font(.caption)
            TextField(L10n.t("cam.session", state.language),
                      text: $sessionId)
                .textFieldStyle(.roundedBorder)
            HStack {
                Button(L10n.t("cam.show", state.language)) {
                    run {
                        let s = try await ApiClient.shared.cameraSession(
                            sessionId: sessionId, token: state.token!)
                        let what = s.subject ?? ""
                        let how = s.state ?? ""
                        note = "\(what) · \(how)"
                    }
                }
                Button(L10n.t("cam.close", state.language)) {
                    run { _ = try await ApiClient.shared.closeCamera(
                        sessionId: sessionId, actorId: state.pid!,
                        token: state.token!) }
                }
            }.font(.caption).disabled(busy || sessionId.isEmpty)
            ForEach(sessions, id: \.identity) { s in
                let what = s.subject ?? ""
                let how = s.state ?? ""
                Text("\(s.identity) · \(what) · \(how)")
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

struct OrgSection: View {
    @EnvironmentObject var state: AppState
    @State private var orgName = ""
    @State private var orgId = ""
    @State private var orgs: [OrgCard] = []
    @State private var deptName = ""
    @State private var deptRole = ""
    @State private var deptProfile = ""
    @State private var goal = ""
    @State private var fromDept = ""
    @State private var log: [Coordination] = []
    @State private var note: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("org.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            HStack {
                TextField(L10n.t("org.name", state.language), text: $orgName)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("org.create", state.language)) {
                    run {
                        let o = try await ApiClient.shared.createOrganization(
                            name: orgName, token: state.token!)
                        orgId = o.identity
                    }
                }.disabled(busy || orgName.isEmpty)
            }.font(.caption)
            HStack {
                Button(L10n.t("org.list", state.language)) {
                    run { orgs = try await ApiClient.shared.organizations(
                        token: state.token!) }
                }
                Button(L10n.t("org.demo", state.language)) {
                    run {
                        let o = try await ApiClient.shared
                            .seedDemoOrganization(token: state.token!)
                        orgId = o.identity
                    }
                }
            }.font(.caption).disabled(busy)
            ForEach(orgs, id: \.identity) { o in
                let name = o.name ?? o.identity
                Button(name) { orgId = o.identity }
                    .font(.caption2).foregroundStyle(Theme.t2)
            }
            TextField(L10n.t("org.id", state.language), text: $orgId)
                .textFieldStyle(.roundedBorder)
            Button(L10n.t("org.show", state.language)) {
                run {
                    let o = try await ApiClient.shared.organization(
                        orgId: orgId, token: state.token!)
                    let name = o.name ?? ""
                    note = "\(name) · \(o.departments?.count ?? 0)"
                }
            }.font(.caption).disabled(busy || orgId.isEmpty)
            HStack {
                TextField(L10n.t("org.dept.name", state.language),
                          text: $deptName)
                    .textFieldStyle(.roundedBorder)
                TextField(L10n.t("org.dept.role", state.language),
                          text: $deptRole)
                    .textFieldStyle(.roundedBorder)
            }
            HStack {
                TextField(L10n.t("org.dept.profile", state.language),
                          text: $deptProfile)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("org.dept.add", state.language)) {
                    run { _ = try await ApiClient.shared.addDepartment(
                        orgId: orgId, name: deptName, role: deptRole,
                        profileId: deptProfile, token: state.token!) }
                }.disabled(busy || orgId.isEmpty || deptName.isEmpty)
            }.font(.caption)
            HStack {
                TextField(L10n.t("org.goal", state.language), text: $goal)
                    .textFieldStyle(.roundedBorder)
                TextField(L10n.t("org.department", state.language),
                          text: $fromDept)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("org.go", state.language)) {
                    run { _ = try await ApiClient.shared.coordinate(
                        orgId: orgId, goal: goal, fromDepartment: fromDept,
                        token: state.token!) }
                }.disabled(busy || orgId.isEmpty || goal.isEmpty
                           || fromDept.isEmpty)
                Button(L10n.t("org.log", state.language)) {
                    run { log = try await ApiClient.shared.coordinations(
                        orgId: orgId, token: state.token!) }
                }.disabled(busy || orgId.isEmpty)
            }.font(.caption)
            ForEach(log, id: \.identity) { c in
                let what = c.goal ?? ""
                let how = c.status ?? ""
                Text("\(what) · \(how)")
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

struct TourSection: View {
    @EnvironmentObject var state: AppState
    @State private var chapters: [TutorialOutline.Chapter] = []
    @State private var stepKey = ""
    @State private var screenNo = ""
    @State private var line = ""
    @State private var note: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("tut.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            HStack {
                Button(L10n.t("tut.outline", state.language)) {
                    run {
                        let o = try await ApiClient.shared.tutorialOutline()
                        chapters = o.chapters ?? o.lessons ?? []
                    }
                }
                Button(L10n.t("tut.start", state.language)) {
                    run {
                        let s = try await ApiClient.shared.startTutorial(
                            learnerId: state.pid ?? "walk-in")
                        line = s.title ?? s.key ?? ""
                    }
                }
                Button(L10n.t("tut.progress", state.language)) {
                    run {
                        let s = try await ApiClient.shared.tutorialProgress(
                            learnerId: state.pid ?? "walk-in")
                        line = s.title ?? s.next ?? ""
                    }
                }
            }.font(.caption).disabled(busy)
            ForEach(chapters) { c in
                let name = c.title ?? c.id
                Button(name) { stepKey = c.key ?? "" }
                    .font(.caption2).foregroundStyle(Theme.t2)
            }
            HStack {
                TextField(L10n.t("tut.step", state.language), text: $stepKey)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("tut.done", state.language)) {
                    run {
                        let s = try await ApiClient.shared.markTutorialDone(
                            learnerId: state.pid ?? "walk-in",
                            lesson: stepKey)
                        line = s.next ?? ""
                    }
                }.disabled(busy || stepKey.isEmpty)
            }.font(.caption)
            HStack {
                TextField(L10n.t("tut.screen", state.language),
                          text: $screenNo)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("cam.show", state.language)) {
                    run {
                        if let n = Int(screenNo) {
                            let s = try await ApiClient.shared
                                .tutorialForScreen(number: n)
                            line = s.title ?? ""
                        } else if !stepKey.isEmpty {
                            let s = try await ApiClient.shared.tutorialStep(
                                key: stepKey)
                            line = s.body ?? s.title ?? ""
                        }
                    }
                }.disabled(busy || (screenNo.isEmpty && stepKey.isEmpty))
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
