import SwiftUI

/// The owner's workshop, in the pocket: the workflows a profile runs, the
/// envelope somebody else may start work inside, the assistant's three
/// verbs, autonomous tasks under a revocable grant, rated placements, and
/// the specialists a profile consults.
///
/// The rules these sections render rather than invent:
///
/// * **A workflow pauses where the world has to answer.** `advance` runs
///   phases until one waits; `resume` carries the confirmation back in.
///   The two are different buttons because they are different acts.
/// * **Delegation is off until the owner declares it.** The offer is a
///   capability advertisement — readable without a token, naming phases
///   and never the grant behind them.
/// * **A task runs under a grant, and the grant can die mid-run.** Mint,
///   run, revoke: three controls, because the third is the point.
/// * **A rated placement only takes an adult-mode profile,** and every
///   ref it mints resolves through the age wall — the card repeats that
///   because the venue will not.
struct WorkSection: View {
    @EnvironmentObject var state: AppState
    @State private var flows: [WorkflowCard] = []
    @State private var goal = ""
    @State private var flowId = ""
    @State private var answer = ""
    @State private var line: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("work.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            ForEach(flows) { f in
                let phase = f.next_phase ?? "—"
                Text("\(f.goal) · \(f.status) · \(phase)")
                    .font(.caption2).foregroundStyle(Theme.t2)
            }
            HStack {
                TextField(L10n.t("work.goal", state.language), text: $goal)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("work.start", state.language)) {
                    run {
                        let made = try await ApiClient.shared.startWorkflow(
                            id: state.pid!, goal: goal, token: state.token!)
                        flowId = made.id; goal = ""
                    }
                }.font(.caption).disabled(busy || goal.isEmpty)
            }
            TextField(L10n.t("work.id", state.language), text: $flowId)
                .textFieldStyle(.roundedBorder)
            HStack {
                Button(L10n.t("work.show", state.language)) {
                    run {
                        let f = try await ApiClient.shared.workflow(
                            id: state.pid!, workflowId: flowId,
                            token: state.token!)
                        let phase = f.next_phase ?? "—"
                        line = "\(f.status) · \(phase)"
                    }
                }.font(.caption).disabled(busy || flowId.isEmpty)
                Button(L10n.t("work.advance", state.language)) {
                    run {
                        let f = try await ApiClient.shared.advanceWorkflow(
                            id: state.pid!, workflowId: flowId,
                            token: state.token!)
                        let phase = f.next_phase ?? "—"
                        line = "\(f.status) · \(phase)"
                    }
                }.font(.caption).disabled(busy || flowId.isEmpty)
                Button(L10n.t("work.cancel", state.language)) {
                    run {
                        _ = try await ApiClient.shared.cancelWorkflow(
                            id: state.pid!, workflowId: flowId,
                            token: state.token!)
                    }
                }.font(.caption).disabled(busy || flowId.isEmpty)
            }
            HStack {
                TextField(L10n.t("work.input", state.language),
                          text: $answer)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("work.resume", state.language)) {
                    run {
                        let f = try await ApiClient.shared.resumeWorkflow(
                            id: state.pid!, workflowId: flowId,
                            input: answer, token: state.token!)
                        answer = ""
                        line = f.status
                    }
                }.font(.caption).disabled(busy || flowId.isEmpty
                                          || answer.isEmpty)
            }
            if let line {
                Text(line).font(.caption2).foregroundStyle(Theme.t2)
            }
        }
        .card()
        .task { await load() }
    }

    private func load() async {
        guard let pid = state.pid, let token = state.token else { return }
        flows = (try? await ApiClient.shared.workflows(
            id: pid, token: token)) ?? []
    }

    private func run(_ op: @escaping () async throws -> Void) {
        busy = true
        Task {
            do { try await op(); await load() }
            catch { line = error.localizedDescription }
            busy = false
        }
    }
}

struct DelegationSection: View {
    @EnvironmentObject var state: AppState
    @State private var offer: DelegationOffer?
    @State private var phases = "draft,review"
    @State private var visitorId = ""
    @State private var goal = ""
    @State private var flowId = ""
    @State private var answer = ""
    @State private var line: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("dele.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            if let offer {
                let names = (offer.phases ?? []).joined(separator: ", ")
                let open = offer.delegation == true
                Text(L10n.t("dele.offer", state.language) + ": "
                     + (open ? names : "—"))
                    .font(.caption2).foregroundStyle(Theme.t2)
            }
            HStack {
                TextField(L10n.t("dele.phases", state.language),
                          text: $phases)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("dele.allow", state.language)) {
                    run {
                        offer = try await ApiClient.shared.setDelegation(
                            id: state.pid!,
                            phases: phases.split(separator: ",").map {
                                $0.trimmingCharacters(in: .whitespaces)
                            },
                            token: state.token!)
                    }
                }.font(.caption).disabled(busy || phases.isEmpty)
            }
            HStack {
                TextField(L10n.t("people.add", state.language),
                          text: $visitorId)
                    .textFieldStyle(.roundedBorder)
                TextField(L10n.t("dele.goal", state.language), text: $goal)
                    .textFieldStyle(.roundedBorder)
            }
            Button(L10n.t("dele.start", state.language)) {
                run {
                    let made =
                        try await ApiClient.shared.startDelegatedWorkflow(
                            id: state.pid!, interactorId: visitorId,
                            goal: goal, token: state.token!)
                    flowId = made.id; goal = ""
                }
            }.font(.caption).disabled(busy || visitorId.isEmpty
                                      || goal.isEmpty)
            TextField(L10n.t("dele.id", state.language), text: $flowId)
                .textFieldStyle(.roundedBorder)
            HStack {
                Button(L10n.t("dele.show", state.language)) {
                    run {
                        let f = try await ApiClient.shared.delegatedWorkflow(
                            id: state.pid!, workflowId: flowId,
                            token: state.token!)
                        let who = f.delegated_to ?? "?"
                        line = "\(f.status) · \(who)"
                    }
                }.font(.caption).disabled(busy || flowId.isEmpty)
                Button(L10n.t("dele.advance", state.language)) {
                    run {
                        let f = try await
                            ApiClient.shared.advanceDelegatedWorkflow(
                                id: state.pid!, workflowId: flowId,
                                token: state.token!)
                        line = f.status
                    }
                }.font(.caption).disabled(busy || flowId.isEmpty)
            }
            HStack {
                TextField(L10n.t("work.input", state.language),
                          text: $answer)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("dele.resume", state.language)) {
                    run {
                        let f = try await
                            ApiClient.shared.resumeDelegatedWorkflow(
                                id: state.pid!, workflowId: flowId,
                                input: answer, token: state.token!)
                        answer = ""
                        line = f.status
                    }
                }.font(.caption).disabled(busy || flowId.isEmpty
                                          || answer.isEmpty)
            }
            if let line {
                Text(line).font(.caption2).foregroundStyle(Theme.t2)
            }
        }
        .card()
        .task {
            if let pid = state.pid {
                offer = try? await ApiClient.shared.delegationOffer(id: pid)
            }
        }
    }

    private func run(_ op: @escaping () async throws -> Void) {
        busy = true
        Task {
            do { try await op() }
            catch { line = error.localizedDescription }
            busy = false
        }
    }
}

struct AssistantSection: View {
    @EnvironmentObject var state: AppState
    @State private var works: [CreativeWork] = []
    @State private var moment = ""
    @State private var draft = ""
    @State private var pile = ""
    @State private var criteria = ""
    @State private var line: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("asst.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            HStack {
                TextField(L10n.t("asst.moment", state.language),
                          text: $moment)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("asst.compose", state.language)) {
                    run {
                        let made = try await ApiClient.shared.composeNote(
                            id: state.pid!, moment: moment,
                            token: state.token!)
                        moment = ""
                        line = made.content
                    }
                }.font(.caption).disabled(busy || moment.isEmpty)
            }
            HStack {
                TextField(L10n.t("asst.text", state.language), text: $draft)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("asst.proof", state.language)) {
                    run {
                        let out = try await ApiClient.shared.proofread(
                            id: state.pid!, text: draft,
                            token: state.token!)
                        line = out.edited
                            ?? out.suggestions.joined(separator: " · ")
                    }
                }.font(.caption).disabled(busy || draft.isEmpty)
            }
            TextField(L10n.t("asst.items", state.language), text: $pile)
                .textFieldStyle(.roundedBorder)
            HStack {
                TextField(L10n.t("asst.criteria", state.language),
                          text: $criteria)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("asst.triage", state.language)) {
                    run {
                        let items = pile.split(separator: ";").enumerated()
                            .map { ["id": "i\($0.offset)",
                                    "text": String($0.element)] }
                        let out = try await ApiClient.shared.triage(
                            id: state.pid!, items: items, keep: 1,
                            criteria: criteria, token: state.token!)
                        let kept = out.kept.map(\.reason)
                        line = kept.joined(separator: " · ")
                    }
                }.font(.caption).disabled(busy || pile.isEmpty)
            }
            if !works.isEmpty {
                Text(L10n.t("asst.works", state.language))
                    .font(.caption).foregroundStyle(Theme.txt)
                ForEach(works) { w in
                    Text("\(w.kind) · \(w.moment)")
                        .font(.caption2).foregroundStyle(Theme.t2)
                }
            }
            if let line {
                Text(line).font(.caption2).foregroundStyle(Theme.t2)
            }
        }
        .card()
        .task { await load() }
    }

    private func load() async {
        guard let pid = state.pid, let token = state.token else { return }
        works = (try? await ApiClient.shared.composedWorks(
            id: pid, token: token)) ?? []
    }

    private func run(_ op: @escaping () async throws -> Void) {
        busy = true
        Task {
            do { try await op(); await load() }
            catch { line = error.localizedDescription }
            busy = false
        }
    }
}

struct TaskSection: View {
    @EnvironmentObject var state: AppState
    @State private var rows: [TaskRow] = []
    @State private var grant: TaskGrant?
    @State private var topic = ""
    @State private var line: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("task.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            ForEach(rows) { t in
                Text("\(t.topic) · \(t.status)")
                    .font(.caption2).foregroundStyle(Theme.t2)
            }
            HStack {
                Button(L10n.t("task.grant", state.language)) {
                    run {
                        grant = try await ApiClient.shared.mintTaskGrant(
                            id: state.pid!, token: state.token!)
                    }
                }.font(.caption).disabled(busy)
                if let grant {
                    let scope = grant.scope.joined(separator: ",")
                    let scopeLabel = L10n.t("task.scope", state.language)
                    Text(scopeLabel + ": " + scope)
                        .font(.caption2).foregroundStyle(Theme.t2)
                    Button(L10n.t("task.revoke", state.language)) {
                        run {
                            try await ApiClient.shared.revokeTaskGrant(
                                grantId: grant.id, token: state.token!)
                            self.grant = nil
                        }
                    }.font(.caption2).disabled(busy)
                }
            }
            HStack {
                TextField(L10n.t("task.topic", state.language),
                          text: $topic)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("task.run", state.language)) {
                    run {
                        let out = try await ApiClient.shared.runTask(
                            id: state.pid!, topic: topic,
                            grantToken: grant?.token ?? "",
                            token: state.token!)
                        topic = ""
                        line = out.reason ?? out.status
                    }
                }.font(.caption).disabled(busy || topic.isEmpty
                                          || grant == nil)
            }
            if let line {
                Text(line).font(.caption2).foregroundStyle(Theme.t2)
            }
        }
        .card()
        .task { await load() }
    }

    private func load() async {
        guard let pid = state.pid, let token = state.token else { return }
        rows = (try? await ApiClient.shared.tasksRun(
            id: pid, token: token)) ?? []
    }

    private func run(_ op: @escaping () async throws -> Void) {
        busy = true
        Task {
            do { try await op(); await load() }
            catch { line = error.localizedDescription }
            busy = false
        }
    }
}

struct PlacementSection: View {
    @EnvironmentObject var state: AppState
    @State private var venues: [VenueCard] = []
    @State private var rows: [PlacementRow] = []
    @State private var venue = ""
    @State private var label = ""
    @State private var placementId = ""
    @State private var line: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("plc.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            if !venues.isEmpty {
                Text(L10n.t("plc.venues", state.language) + ": "
                     + venues.map(\.key).joined(separator: ", "))
                    .font(.caption2).foregroundStyle(Theme.t2)
            }
            ForEach(rows) { p in
                let tag = p.label ?? p.venue_name
                Text("\(tag) · \(p.scans)")
                    .font(.caption2)
                    .foregroundStyle(p.active ? Theme.txt : Theme.t2)
            }
            HStack {
                TextField(L10n.t("plc.venue", state.language), text: $venue)
                    .textFieldStyle(.roundedBorder)
                TextField(L10n.t("plc.label", state.language), text: $label)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("plc.place", state.language)) {
                    run {
                        let made = try await ApiClient.shared.placeRated(
                            id: state.pid!, venue: venue, label: label,
                            token: state.token!)
                        placementId = made.placement_id
                        line = made.scan_url
                    }
                }.font(.caption).disabled(busy || venue.isEmpty)
            }
            HStack {
                Button(L10n.t("plc.stats", state.language)) {
                    run {
                        let s = try await
                            ApiClient.shared.placementAnalytics(
                                id: state.pid!, token: state.token!)
                        line = "\(s.funnel.resolutions) → "
                            + "\(s.funnel.verified_views) → "
                            + "\(s.funnel.unique_chatters)"
                    }
                }.font(.caption).disabled(busy)
                Button(L10n.t("plc.custody", state.language)) {
                    run {
                        let c = try await ApiClient.shared.placementCustody(
                            id: state.pid!, token: state.token!)
                        line = "\(c.count) · \(c.chain_intact)"
                    }
                }.font(.caption).disabled(busy)
            }
            HStack {
                TextField(L10n.t("plc.id", state.language),
                          text: $placementId)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("plc.remove", state.language)) {
                    run {
                        try await ApiClient.shared.removePlacement(
                            placementId: placementId, token: state.token!)
                        placementId = ""
                    }
                }.font(.caption).disabled(busy || placementId.isEmpty)
            }
            if let line {
                Text(line).font(.caption2).foregroundStyle(Theme.t2)
            }
        }
        .card()
        .task { await load() }
    }

    private func load() async {
        venues = (try? await ApiClient.shared.ratedVenues()) ?? []
        guard let pid = state.pid, let token = state.token else { return }
        rows = (try? await ApiClient.shared.placements(
            id: pid, token: token)) ?? []
    }

    private func run(_ op: @escaping () async throws -> Void) {
        busy = true
        Task {
            do { try await op(); await load() }
            catch { line = error.localizedDescription }
            busy = false
        }
    }
}

struct SpecialistSection: View {
    @EnvironmentObject var state: AppState
    @State private var rows: [SpecialistRow] = []
    @State private var domain = ""
    @State private var specialistId = ""
    @State private var line: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("spec.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            ForEach(rows, id: \.domain) { s in
                Text("\(s.domain) · \(s.specialist_profile_id)")
                    .font(.caption2).foregroundStyle(Theme.t2)
            }
            HStack {
                TextField(L10n.t("spec.domain", state.language),
                          text: $domain)
                    .textFieldStyle(.roundedBorder)
                TextField(L10n.t("spec.id", state.language),
                          text: $specialistId)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("spec.set", state.language)) {
                    run {
                        _ = try await ApiClient.shared.setSpecialist(
                            id: state.pid!, domain: domain,
                            specialistId: specialistId,
                            token: state.token!)
                        domain = ""; specialistId = ""
                    }
                }.font(.caption).disabled(busy || domain.isEmpty
                                          || specialistId.isEmpty)
            }
            if let line {
                Text(line).font(.caption2).foregroundStyle(Theme.t2)
            }
        }
        .card()
        .task { await load() }
    }

    private func load() async {
        guard let pid = state.pid, let token = state.token else { return }
        rows = (try? await ApiClient.shared.specialists(
            id: pid, token: token)) ?? []
    }

    private func run(_ op: @escaping () async throws -> Void) {
        busy = true
        Task {
            do { try await op(); await load() }
            catch { line = error.localizedDescription }
            busy = false
        }
    }
}
