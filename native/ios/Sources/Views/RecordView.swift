import SwiftUI

/// The record, the veil and the exit, in the pocket: what the platform
/// holds about a profile, what its anonymity hides, and how it ends.
///
/// The rules these sections render rather than invent:
///
/// * **The memory list exists for choosing what to erase.** One row per
///   conversation, with the person's name — and the erase button next to
///   the read button, because both are the owner's.
/// * **The veil's limits are half the payload.** Somebody deciding
///   whether it is safe to post assumes "anonymous" means untraceable
///   unless told otherwise, so what it does NOT hide renders first.
/// * **The badge is a fact, not a word.** The level and who checked
///   always travel with "verified"; the roster of your other profiles
///   answers only to your own token, because that link is the whole of
///   what anonymity between them protects.
/// * **Departing is not deletion.** Sunset says farewell and freezes;
///   the memorial is public and never persona internals; delete removes
///   every trace. Three different ends, three different buttons.
struct MemorySection: View {
    @EnvironmentObject var state: AppState
    @State private var rows: [MemoryRow] = []
    @State private var visitorId = ""
    @State private var line: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("mem.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            ForEach(rows) { m in
                Text("\(m.interactor_name) · \(m.turns)")
                    .font(.caption2).foregroundStyle(Theme.t2)
            }
            TextField(L10n.t("mem.id", state.language), text: $visitorId)
                .textFieldStyle(.roundedBorder)
            HStack {
                Button(L10n.t("mem.show", state.language)) {
                    run {
                        let turns = try await ApiClient.shared.memory(
                            id: state.pid!, interactorId: visitorId,
                            token: state.token!)
                        line = turns.suffix(3).map(\.content)
                            .joined(separator: " · ")
                    }
                }.font(.caption).disabled(busy || visitorId.isEmpty)
                Button(L10n.t("mem.erase", state.language)) {
                    run {
                        try await ApiClient.shared.eraseMemory(
                            id: state.pid!, interactorId: visitorId,
                            token: state.token!)
                        visitorId = ""
                    }
                }.font(.caption).disabled(busy || visitorId.isEmpty)
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
        rows = (try? await ApiClient.shared.memories(
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

struct PairSection: View {
    @EnvironmentObject var state: AppState
    @State private var visitorId = ""
    @State private var line: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("who.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            TextField(L10n.t("mem.id", state.language), text: $visitorId)
                .textFieldStyle(.roundedBorder)
            HStack {
                Button(L10n.t("who.thread", state.language)) {
                    run {
                        let t = try await ApiClient.shared.thread(
                            id: state.pid!, interactorId: visitorId,
                            token: state.token!)
                        line = "\(t.messages.count)"
                    }
                }.font(.caption).disabled(busy || visitorId.isEmpty)
                Button(L10n.t("who.engagement", state.language)) {
                    run {
                        let e = try await ApiClient.shared.engagement(
                            id: state.pid!, interactorId: visitorId,
                            token: state.token!)
                        let sessions = e.sessions ?? 0
                        line = "\(sessions)"
                    }
                }.font(.caption).disabled(busy || visitorId.isEmpty)
            }
            HStack {
                Button(L10n.t("who.notes", state.language)) {
                    run {
                        let notes = try await ApiClient.shared.clinicalNotes(
                            id: state.pid!, interactorId: visitorId,
                            token: state.token!)
                        line = notes.compactMap(\.note)
                            .joined(separator: " · ")
                    }
                }.font(.caption).disabled(busy || visitorId.isEmpty)
                Button(L10n.t("who.embedding", state.language)) {
                    run {
                        _ = try await ApiClient.shared.embedding(
                            id: state.pid!, interactorId: visitorId,
                            token: state.token!)
                        line = "✓"
                    }
                }.font(.caption).disabled(busy || visitorId.isEmpty)
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

struct SourceSection: View {
    @EnvironmentObject var state: AppState
    @State private var rows: [SourceRow] = []
    @State private var kind = "life_event"
    @State private var name = ""
    @State private var words = ""
    @State private var line: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("src.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            ForEach(rows) { s in
                let title = s.title ?? s.id
                Text("\(s.kind) · \(title)")
                    .font(.caption2).foregroundStyle(Theme.t2)
            }
            HStack {
                TextField(L10n.t("src.kind", state.language), text: $kind)
                    .textFieldStyle(.roundedBorder)
                TextField(L10n.t("src.name", state.language), text: $name)
                    .textFieldStyle(.roundedBorder)
            }
            HStack {
                TextField(L10n.t("src.words", state.language), text: $words)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("src.add", state.language)) {
                    run {
                        _ = try await ApiClient.shared.addSource(
                            id: state.pid!, kind: kind, title: name,
                            content: words, token: state.token!)
                        name = ""; words = ""
                    }
                }.font(.caption).disabled(busy || words.isEmpty)
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
        rows = (try? await ApiClient.shared.sources(
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

struct RecordSection: View {
    @EnvironmentObject var state: AppState
    @State private var line: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("rec.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            HStack {
                Button(L10n.t("rec.transparency", state.language)) {
                    run {
                        let t = try await ApiClient.shared.transparency(
                            id: state.pid!)
                        let model = t.model_effective ?? "?"
                        line = "\(t.active_relationships) · \(model)"
                    }
                }.font(.caption).disabled(busy)
                Button(L10n.t("rec.stats", state.language)) {
                    run {
                        let s = try await ApiClient.shared.profileStats(
                            id: state.pid!, token: state.token!)
                        line = "\(s.sessions) · \(s.memory_entries) · "
                            + "\(s.interactors) · \(s.sources)"
                    }
                }.font(.caption).disabled(busy)
            }
            HStack {
                Button(L10n.t("rec.export", state.language)) {
                    run {
                        let out = try await ApiClient.shared.exportProfile(
                            id: state.pid!, token: state.token!)
                        line = "\(out.messages.count) · "
                            + "\(out.posts.count) · \(out.sources.count)"
                    }
                }.font(.caption).disabled(busy)
                Button(L10n.t("rec.feed", state.language)) {
                    run {
                        let f = try await ApiClient.shared.feed(
                            id: state.pid!)
                        line = "\(f.posts.count) · "
                            + f.ranked_on.joined(separator: ", ")
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

struct VeilSection: View {
    @EnvironmentObject var state: AppState
    @State private var line: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("veil.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            HStack {
                Button(L10n.t("veil.show", state.language)) {
                    run {
                        let v = try await ApiClient.shared.anonymity(
                            id: state.pid!, token: state.token!)
                        // What it does NOT hide renders first — the
                        // generous reading of "anonymous" is the
                        // dangerous one.
                        let limits = (v.not_withheld ?? [])
                            .joined(separator: " · ")
                        line = limits
                    }
                }.font(.caption).disabled(busy)
                Button(L10n.t("veil.on", state.language)) {
                    run {
                        _ = try await ApiClient.shared.setAnonymity(
                            id: state.pid!, anonymous: true,
                            token: state.token!)
                    }
                }.font(.caption).disabled(busy)
                Button(L10n.t("veil.off", state.language)) {
                    run {
                        _ = try await ApiClient.shared.setAnonymity(
                            id: state.pid!, anonymous: false,
                            token: state.token!)
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

struct BadgeSection: View {
    @EnvironmentObject var state: AppState
    @State private var level = "document"
    @State private var attestor = ""
    @State private var line: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("ver.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            HStack {
                Button(L10n.t("ver.show", state.language)) {
                    run {
                        let v = try await ApiClient.shared.verification(
                            id: state.pid!)
                        let lvl = v.level ?? "—"
                        let who = v.attestor ?? "—"
                        line = "\(lvl) · \(who)"
                    }
                }.font(.caption).disabled(busy)
                Button(L10n.t("ver.able", state.language)) {
                    run {
                        let v = try await ApiClient.shared.verifiable(
                            id: state.pid!, token: state.token!)
                        line = v.reason ?? "\(v.can_verify)"
                    }
                }.font(.caption).disabled(busy)
            }
            HStack {
                TextField(L10n.t("ver.level", state.language), text: $level)
                    .textFieldStyle(.roundedBorder)
                TextField(L10n.t("ver.attestor", state.language),
                          text: $attestor)
                    .textFieldStyle(.roundedBorder)
            }
            HStack {
                Button(L10n.t("ver.claim", state.language)) {
                    run {
                        _ = try await ApiClient.shared.claimVerification(
                            id: state.pid!, level: level,
                            attestor: attestor, token: state.token!)
                    }
                }.font(.caption).disabled(busy || level.isEmpty)
                Button(L10n.t("ver.move", state.language)) {
                    run {
                        _ = try await ApiClient.shared.moveBadgeHere(
                            id: state.pid!, token: state.token!)
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

struct ExitSection: View {
    @EnvironmentObject var state: AppState
    @State private var newName = ""
    @State private var newPersona = ""
    @State private var reference = ""
    @State private var line: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("exit.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            HStack {
                TextField(L10n.t("exit.rename", state.language),
                          text: $newName)
                    .textFieldStyle(.roundedBorder)
                TextField(L10n.t("exit.persona", state.language),
                          text: $newPersona)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("exit.save", state.language)) {
                    run {
                        _ = try await ApiClient.shared.editProfile(
                            id: state.pid!, displayName: newName,
                            persona: newPersona, token: state.token!)
                        newName = ""; newPersona = ""
                    }
                }.font(.caption)
                    .disabled(busy || (newName.isEmpty
                                       && newPersona.isEmpty))
            }
            HStack {
                Button(L10n.t("exit.siblings", state.language)) {
                    run {
                        let r = try await ApiClient.shared.siblings(
                            id: state.pid!, token: state.token!)
                        line = (r.profiles ?? [])
                            .map { $0.display_name ?? $0.id }
                            .joined(separator: " · ")
                    }
                }.font(.caption).disabled(busy)
                Button(L10n.t("exit.memorial", state.language)) {
                    run {
                        let m = try await ApiClient.shared.memorial(
                            id: state.pid!)
                        let name = m.display_name ?? "—"
                        let touched = m.relationships_touched ?? 0
                        line = "\(name) · \(touched)"
                    }
                }.font(.caption).disabled(busy)
            }
            HStack {
                TextField(L10n.t("exit.ref", state.language),
                          text: $reference)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("exit.succeed", state.language)) {
                    run {
                        let out = try await ApiClient.shared.succeed(
                            id: state.pid!, verificationRef: reference,
                            token: state.token!)
                        line = "\(out.succeeded)"
                    }
                }.font(.caption).disabled(busy || reference.isEmpty)
            }
            HStack {
                Button(L10n.t("exit.sunset", state.language)) {
                    run {
                        let out = try await ApiClient.shared.sunset(
                            id: state.pid!, token: state.token!)
                        let n = out.farewells ?? 0
                        line = "\(n)"
                    }
                }.font(.caption).disabled(busy)
                Button(L10n.t("exit.delete", state.language)) {
                    run {
                        try await ApiClient.shared.deleteProfile(
                            id: state.pid!, token: state.token!)
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
