import SwiftUI

/// The last doors, in the pocket: the birth (genesis, hybrids, packs),
/// the mind at work (simulation, fine-tuning, the cloud-contribution
/// ledger, excursions), the reach (proactive check-ins, quiet hours,
/// feedback, referrals), the license, and the senses (perceive, the
/// lending vocabulary, overlays, experience). With these, no route in
/// the table lacks a door on this shell.
///
/// The rules these sections render rather than invent:
///
/// * **A simulation is the owner's operational insight** — watermarked
///   synthetic, never distributed.
/// * **The contribution ledger shows exactly what would leave** before
///   it leaves, and revoke deletes what already did.
/// * **The profile initiates only when its owner opted in,** and never
///   inside the recipient's quiet hours.
/// * **A rating comes from the person who is rating** — it moves the
///   engagement score the profile then behaves from.
/// * **A derived agent records its origin.**
struct BirthSection: View {
    @EnvironmentObject var state: AppState
    @State private var owner = ""
    @State private var name = ""
    @State private var social = ""
    @State private var humor = ""
    @State private var matters = ""
    @State private var comfort = ""
    @State private var sources = ""
    @State private var industry = ""
    @State private var packTitle = ""
    @State private var line: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("born.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            HStack {
                TextField(L10n.t("born.owner", state.language), text: $owner)
                    .textFieldStyle(.roundedBorder)
                TextField(L10n.t("born.name", state.language), text: $name)
                    .textFieldStyle(.roundedBorder)
            }
            HStack {
                TextField(L10n.t("born.social", state.language),
                          text: $social)
                    .textFieldStyle(.roundedBorder)
                TextField(L10n.t("born.humor", state.language), text: $humor)
                    .textFieldStyle(.roundedBorder)
            }
            HStack {
                TextField(L10n.t("born.matters", state.language),
                          text: $matters)
                    .textFieldStyle(.roundedBorder)
                TextField(L10n.t("born.comfort", state.language),
                          text: $comfort)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("born.make", state.language)) {
                    run {
                        let g = try await ApiClient.shared.genesis(
                            ownerId: owner, name: name, social: social,
                            humor: humor, matters: matters, comfort: comfort)
                        line = g.display_name ?? g.id ?? "—"
                    }
                }.font(.caption).disabled(busy || owner.isEmpty
                                          || social.isEmpty || humor.isEmpty
                                          || matters.isEmpty
                                          || comfort.isEmpty)
            }
            HStack {
                TextField(L10n.t("born.sources", state.language),
                          text: $sources)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("born.blend", state.language)) {
                    run {
                        let ids = sources.split(separator: ",")
                            .map { $0.trimmingCharacters(in: .whitespaces) }
                        let g = try await ApiClient.shared.composite(
                            ownerId: owner, name: name, sources: ids)
                        line = g.display_name ?? g.id ?? "—"
                    }
                }.font(.caption).disabled(busy || owner.isEmpty
                                          || name.isEmpty
                                          || sources.isEmpty)
            }
            HStack {
                TextField(L10n.t("born.pack.industry", state.language),
                          text: $industry)
                    .textFieldStyle(.roundedBorder)
                TextField(L10n.t("born.pack.title", state.language),
                          text: $packTitle)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("born.pack.publish", state.language)) {
                    run {
                        let o = try await ApiClient.shared.publishPack(
                            industry: industry, title: packTitle,
                            token: state.token!)
                        line = o.title ?? o.id ?? "—"
                        packTitle = ""
                    }
                }.font(.caption).disabled(busy || industry.isEmpty
                                          || packTitle.isEmpty)
                Button(L10n.t("born.pack.seed", state.language)) {
                    run {
                        let o = try await ApiClient.shared.seedPacks()
                        line = "\(o.created ?? o.packs ?? 0)"
                    }
                }.font(.caption).disabled(busy)
            }
            if let line {
                Text(line).font(.caption2).foregroundStyle(Theme.t2)
            }
        }.card()
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

struct MindSection: View {
    @EnvironmentObject var state: AppState
    @State private var scenario = ""
    @State private var cid = ""
    @State private var line: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("mind.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            HStack {
                TextField(L10n.t("mind.scenario", state.language),
                          text: $scenario)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("mind.simulate", state.language)) {
                    run {
                        let o = try await ApiClient.shared.simulate(
                            id: state.pid!, scenario: scenario,
                            token: state.token!)
                        line = o.narrative ?? o.id ?? "—"
                        scenario = ""
                    }
                }.font(.caption).disabled(busy || scenario.isEmpty)
                Button(L10n.t("mind.runs", state.language)) {
                    run {
                        let l = try await ApiClient.shared.simulations(
                            id: state.pid!, token: state.token!)
                        line = "\(l.count)"
                    }
                }.font(.caption).disabled(busy)
                Button(L10n.t("mind.tune", state.language)) {
                    run {
                        let o = try await ApiClient.shared.finetune(
                            id: state.pid!, token: state.token!)
                        line = "\(o.messages_processed ?? 0) · "
                             + (o.computed ?? "")
                    }
                }.font(.caption).disabled(busy)
            }
            HStack {
                Button(L10n.t("mind.cloud", state.language)) {
                    run {
                        let v = try await ApiClient.shared.cloudContribution(
                            id: state.pid!, token: state.token!)
                        line = ((v.opted_in ?? false) ? "on" : "off")
                            + " · \((v.contributed ?? []).count)"
                    }
                }.font(.caption).disabled(busy)
                Button(L10n.t("mind.revoke", state.language)) {
                    run {
                        let o = try await ApiClient.shared
                            .revokeContributions(id: state.pid!,
                                                 token: state.token!)
                        line = "\(o.revoked_count ?? 0)"
                    }
                }.font(.caption).disabled(busy)
                TextField(L10n.t("people.add", state.language), text: $cid)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("mind.excursion", state.language)) {
                    run {
                        let o = try await ApiClient.shared.excursion(
                            cid: cid, token: state.token!)
                        line = (o.status ?? "—") + " · "
                            + (o.findings ?? "")
                    }
                }.font(.caption).disabled(busy || cid.isEmpty)
            }
            if let line {
                Text(line).font(.caption2).foregroundStyle(Theme.t2)
            }
        }.card()
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

struct ReachSection: View {
    @EnvironmentObject var state: AppState
    @State private var quietStart = ""
    @State private var quietEnd = ""
    @State private var line: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("reach.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            HStack {
                Button(L10n.t("reach.checkin", state.language)) {
                    run {
                        let o = try await ApiClient.shared.proactiveCheckin(
                            id: state.pid!,
                            interactorId: state.interactorId ?? "",
                            token: state.token!)
                        line = o.message ?? o.reason ?? "—"
                    }
                }.font(.caption).disabled(busy
                                          || state.interactorId == nil)
                Button(L10n.t("reach.rate.up", state.language)) {
                    run {
                        let o = try await ApiClient.shared.giveFeedback(
                            id: state.pid!,
                            interactorId: state.interactorId ?? "",
                            rating: "up",
                            token: state.interactorToken ?? "")
                        line = o.rating ?? "—"
                    }
                }.font(.caption).disabled(busy
                                          || state.interactorId == nil)
                Button(L10n.t("reach.rate.down", state.language)) {
                    run {
                        let o = try await ApiClient.shared.giveFeedback(
                            id: state.pid!,
                            interactorId: state.interactorId ?? "",
                            rating: "down",
                            token: state.interactorToken ?? "")
                        line = o.rating ?? "—"
                    }
                }.font(.caption).disabled(busy
                                          || state.interactorId == nil)
            }
            HStack {
                TextField(L10n.t("reach.quiet.start", state.language),
                          text: $quietStart)
                    .textFieldStyle(.roundedBorder)
                TextField(L10n.t("reach.quiet.end", state.language),
                          text: $quietEnd)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("reach.quiet.set", state.language)) {
                    run {
                        let o = try await ApiClient.shared.setQuietHours(
                            interactorId: state.interactorId ?? "",
                            start: Int(quietStart), end: Int(quietEnd),
                            token: state.interactorToken ?? "")
                        line = "\(o.quiet_start ?? -1)–\(o.quiet_end ?? -1)"
                    }
                }.font(.caption).disabled(busy
                                          || state.interactorId == nil)
                Button(L10n.t("reach.referrals", state.language)) {
                    run {
                        let l = try await ApiClient.shared.myReferrals(
                            interactorId: state.interactorId ?? "",
                            token: state.interactorToken ?? "")
                        line = "\(l.count)"
                    }
                }.font(.caption).disabled(busy
                                          || state.interactorId == nil)
            }
            if let line {
                Text(line).font(.caption2).foregroundStyle(Theme.t2)
            }
        }.card()
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

struct LicenseSection: View {
    @EnvironmentObject var state: AppState
    @State private var grantId = ""
    @State private var line: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("lic.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            HStack {
                Button(L10n.t("lic.acquire", state.language)) {
                    run {
                        let g = try await ApiClient.shared.acquireLicense(
                            id: state.pid!,
                            token: state.interactorToken ?? "")
                        grantId = g.id ?? ""
                        line = g.id ?? "—"
                    }
                }.font(.caption).disabled(busy)
                TextField(L10n.t("lic.grant", state.language),
                          text: $grantId)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("lic.derive", state.language)) {
                    run {
                        let g = try await ApiClient.shared.deriveAgent(
                            id: state.pid!, grantId: grantId,
                            token: state.interactorToken ?? "")
                        line = g.display_name ?? g.id ?? "—"
                    }
                }.font(.caption).disabled(busy || grantId.isEmpty)
            }
            if let line {
                Text(line).font(.caption2).foregroundStyle(Theme.t2)
            }
        }.card()
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

struct SensesSection: View {
    @EnvironmentObject var state: AppState
    @State private var scene = ""
    @State private var goal = ""
    @State private var expTitle = ""
    @State private var line: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("sens.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            HStack {
                TextField(L10n.t("sens.scene", state.language), text: $scene)
                    .textFieldStyle(.roundedBorder)
                TextField(L10n.t("wrist.input", state.language), text: $goal)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("sens.perceive", state.language)) {
                    run {
                        let objects = scene.split(separator: ",")
                            .map { $0.trimmingCharacters(in: .whitespaces) }
                        let o = try await ApiClient.shared.perceive(
                            id: state.pid!, objects: objects, goal: goal,
                            token: state.token!)
                        line = o.guidance ?? "—"
                        scene = ""; goal = ""
                    }
                }.font(.caption).disabled(busy || scene.isEmpty)
            }
            HStack {
                Button(L10n.t("sens.mics", state.language)) {
                    run {
                        let o = try await ApiClient.shared.microphonePlaces()
                        line = "\((o.places ?? []).count)"
                    }
                }.font(.caption).disabled(busy)
                Button(L10n.t("sens.vocab", state.language)) {
                    run {
                        let o = try await ApiClient.shared
                            .microphoneVocabulary()
                        line = (o.personal ?? []).joined(separator: " · ")
                    }
                }.font(.caption).disabled(busy)
                Button(L10n.t("sens.overlays", state.language)) {
                    run {
                        let o = try await ApiClient.shared.overlaysCatalogue()
                        line = "\((o.kinds ?? []).count) · "
                            + "\((o.refusals ?? []).count)"
                    }
                }.font(.caption).disabled(busy)
            }
            HStack {
                TextField(L10n.t("sens.exp", state.language),
                          text: $expTitle)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("sens.exp.set", state.language)) {
                    run {
                        let o = try await ApiClient.shared.setExperience(
                            id: state.pid!,
                            entries: [["title": expTitle]],
                            token: state.token!)
                        line = "\(o.experience.count)"
                        expTitle = ""
                    }
                }.font(.caption).disabled(busy || expTitle.isEmpty)
            }
            if let line {
                Text(line).font(.caption2).foregroundStyle(Theme.t2)
            }
        }.card()
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
