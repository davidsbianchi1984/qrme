import SwiftUI

/// The face a profile shows the world, in the pocket: the portrait and
/// where the starter faces came from, the emblem and the badge, the page
/// a visitor lands on, the surfaces it renders to, what a hybrid is
/// blended from, the bodies it lives in, the dials that steer it, and
/// the wrist that watches it all.
///
/// The rules these sections render rather than invent:
///
/// * **The portrait carries its own honesty.** The AI badge and whose
///   likeness it is travel with the asset, and the starter briefs are
///   public because "where did these faces come from" deserves a real
///   answer.
/// * **The badge a reader sees is not the owner's verification read.**
///   On an anonymous profile the attestor is withheld — a name and a
///   workplace narrow an anonymous author to a city.
/// * **The blend is provenance.** A hybrid acknowledges openly that it
///   is a blend and never claims to be any single constituent.
/// * **The same personality, in every body.** The consistency read is
///   public so anyone meeting the profile on a speaker or in a room can
///   verify it is the same one.
/// * **Dials are 0–100 integers,** and intimacy can never be raised on
///   a non-rated persona.
struct AvatarSection: View {
    @EnvironmentObject var state: AppState
    @State private var asset = ""
    @State private var handle = ""
    @State private var importUrl = ""
    @State private var line: String?
    @State private var busy = false
    /// The shelf, and which of it this import is coming from. Read once and
    /// held: eight systems is a picker, and re-fetching per tap is what the
    /// old block did with the answer it then threw away.
    @State private var shelf: [ApiClient.MarketSource] = []
    /// Empty rather than a named row: this was hard-coded to
    /// "ready_player_me" and that service was shut down, which is how a
    /// picker comes to open on a door nobody can walk through. The
    /// shelf's own first row decides once it arrives.
    @State private var chosenSource = ""

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("ava.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            HStack {
                Button(L10n.t("ava.show", state.language)) {
                    run {
                        let a = try await ApiClient.shared.avatar(
                            id: state.pid!)
                        let badge = (a.asset_marked ?? false) ? "AI" : "—"
                        let who = a.likeness?.note ?? "—"
                        line = badge + " · " + who
                    }
                }.font(.caption).disabled(busy)
                Button(L10n.t("ava.briefs", state.language)) {
                    run {
                        let c = try await ApiClient.shared.avatarBriefs()
                        line = "\((c.briefs ?? []).count)"
                    }
                }.font(.caption).disabled(busy)
            }
            HStack {
                TextField(L10n.t("ava.asset", state.language), text: $asset)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("ava.set", state.language)) {
                    run {
                        _ = try await ApiClient.shared.setAvatar(
                            id: state.pid!, asset: asset,
                            token: state.token!)
                        asset = ""
                    }
                }.font(.caption).disabled(busy || asset.isEmpty)
            }
            HStack {
                TextField(L10n.t("people.add", state.language),
                          text: $handle)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("ava.brief", state.language)) {
                    run {
                        let b = try await ApiClient.shared.avatarBrief(
                            handle: handle)
                        line = b.brief
                    }
                }.font(.caption).disabled(busy || handle.isEmpty)
            }
            // Which system the face came from, picked rather than assumed.
            //
            // This block used to fetch the shelf, count it, and then post
            // `source: "other"` — so eight named systems were on the wire, a
            // number off them went on screen, and every import from a phone
            // was filed under the one that means "somewhere else". The whole
            // reason `import_avatar` takes a source is that the provenance
            // survives beside the face; "other" is that provenance thrown
            // away at the last step.
            //
            //     asked     did the import go through
            //     mattered  does the record say where it came from
            Text(L10n.t("ava.market", state.language))
                .font(.caption.bold()).foregroundStyle(Theme.txt)
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 6) {
                    ForEach(shelf, id: \.key) { source in
                        Button(source.name) { chosenSource = source.key }
                            .font(.caption2)
                            .padding(.horizontal, 10).padding(.vertical, 6)
                            .background(chosenSource == source.key
                                        ? Theme.brand : Theme.scrBot)
                            .foregroundStyle(chosenSource == source.key
                                             ? .white : Theme.txt)
                            .clipShape(Capsule())
                    }
                }
            }
            // The provider's own export route, in their words. It is the
            // useful half of the shelf and no shell was showing it.
            if let how = shelf.first(where: { $0.key == chosenSource })?.how {
                Text(how).font(.caption2).foregroundStyle(Theme.t2)
            }
            HStack {
                TextField(L10n.t("ava.url.ph", state.language),
                          text: $importUrl)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("ava.import", state.language)) {
                    run {
                        _ = try await ApiClient.shared.importAvatar(
                            id: state.pid!, source: chosenSource,
                            asset: importUrl, token: state.token!)
                        line = L10n.t("ava.imported", state.language)
                        importUrl = ""
                    }
                }.font(.caption).disabled(busy || importUrl.isEmpty)
            }
            if let line {
                Text(line).font(.caption2).foregroundStyle(Theme.t2)
            }
        }
        .card()
        .task {
            if shelf.isEmpty,
               let s = try? await ApiClient.shared.avatarMarket() {
                shelf = s.skin_sources
                if !s.skin_sources.contains(where: { $0.key == chosenSource }),
                   let first = s.skin_sources.first {
                    chosenSource = first.key
                }
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

struct EmblemSection: View {
    @EnvironmentObject var state: AppState
    @State private var emblem = ""
    @State private var line: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("embl.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            HStack {
                Button(L10n.t("embl.list", state.language)) {
                    run {
                        let c = try await ApiClient.shared.identityEmblems()
                        line = (c.emblems ?? []).compactMap(\.emblem)
                            .joined(separator: " · ")
                    }
                }.font(.caption).disabled(busy)
                Button(L10n.t("embl.rules", state.language)) {
                    run {
                        let v = try await
                            ApiClient.shared.identityVocabulary()
                        line = v.withheld_when_anonymous
                            .joined(separator: " · ")
                    }
                }.font(.caption).disabled(busy)
                Button(L10n.t("embl.badge", state.language)) {
                    run {
                        let b = try await ApiClient.shared.badge(
                            id: state.pid!)
                        let lvl = b.level ?? "—"
                        let who = b.attestor ?? "—"
                        line = lvl + " · " + who
                    }
                }.font(.caption).disabled(busy)
            }
            HStack {
                TextField(L10n.t("embl.pick", state.language),
                          text: $emblem)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("embl.set", state.language)) {
                    run {
                        _ = try await ApiClient.shared.setEmblem(
                            id: state.pid!, emblem: emblem,
                            token: state.token!)
                        emblem = ""
                    }
                }.font(.caption).disabled(busy || emblem.isEmpty)
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

struct PageSection: View {
    @EnvironmentObject var state: AppState
    @State private var theme = ""
    @State private var tagline = ""
    @State private var about = ""
    @State private var line: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("pg.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            HStack {
                Button(L10n.t("pg.show", state.language)) {
                    run {
                        let p = try await ApiClient.shared.page(
                            id: state.pid!)
                        let t = p.tagline ?? "—"
                        line = (p.page_theme?.label ?? "—") + " · " + t
                    }
                }.font(.caption).disabled(busy)
                Button(L10n.t("pg.themes", state.language)) {
                    run {
                        let c = try await ApiClient.shared.pageThemes()
                        line = (c.themes ?? []).compactMap(\.id)
                            .joined(separator: " · ")
                    }
                }.font(.caption).disabled(busy)
                Button(L10n.t("front.show", state.language)) {
                    run {
                        let f = try await ApiClient.shared.frontPage(
                            id: state.pid!)
                        let name = f.display_name ?? "—"
                        line = name + " · " + (f.headline ?? "—")
                    }
                }.font(.caption).disabled(busy)
            }
            HStack {
                TextField(L10n.t("pg.theme", state.language), text: $theme)
                    .textFieldStyle(.roundedBorder)
                TextField(L10n.t("pg.tagline", state.language),
                          text: $tagline)
                    .textFieldStyle(.roundedBorder)
            }
            HStack {
                TextField(L10n.t("pg.about", state.language), text: $about)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("pg.save", state.language)) {
                    run {
                        _ = try await ApiClient.shared.editPage(
                            id: state.pid!, theme: theme, tagline: tagline,
                            about: about, token: state.token!)
                        theme = ""; tagline = ""; about = ""
                    }
                }.font(.caption)
                    .disabled(busy || (theme.isEmpty && tagline.isEmpty
                                       && about.isEmpty))
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

struct SurfaceSection: View {
    @EnvironmentObject var state: AppState
    @State private var listed = ""
    @State private var line: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("surf.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            HStack {
                Button(L10n.t("surf.list", state.language)) {
                    run {
                        let s = try await ApiClient.shared.surfaces(
                            id: state.pid!)
                        line = s.surfaces.joined(separator: " · ")
                    }
                }.font(.caption).disabled(busy)
                Button(L10n.t("comp.show", state.language)) {
                    run {
                        let c = try await ApiClient.shared.composition(
                            id: state.pid!)
                        line = (c.composition_sources ?? []).compactMap(\.name)
                            .joined(separator: " · ")
                    }
                }.font(.caption).disabled(busy)
            }
            HStack {
                TextField(L10n.t("surf.title", state.language),
                          text: $listed)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("surf.set", state.language)) {
                    run {
                        let parts = listed.split(separator: ",").map {
                            $0.trimmingCharacters(in: .whitespaces)
                        }
                        _ = try await ApiClient.shared.setSurfaces(
                            id: state.pid!, surfaces: parts,
                            token: state.token!)
                        listed = ""
                    }
                }.font(.caption).disabled(busy || listed.isEmpty)
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

struct EmbodimentSection: View {
    @EnvironmentObject var state: AppState
    @State private var rows: [EmbodimentRow] = []
    @State private var name = ""
    @State private var kind = "speaker"
    @State private var screenLabel = ""
    @State private var line: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("form.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            ForEach(rows, id: \.name) { r in
                Text("\(r.name) · \(r.kind)")
                    .font(.caption2).foregroundStyle(Theme.t2)
            }
            HStack {
                TextField(L10n.t("form.name", state.language), text: $name)
                    .textFieldStyle(.roundedBorder)
                TextField(L10n.t("form.kind", state.language), text: $kind)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("form.add", state.language)) {
                    run {
                        _ = try await ApiClient.shared.addEmbodiment(
                            id: state.pid!, name: name, kind: kind,
                            token: state.token!)
                        name = ""
                    }
                }.font(.caption).disabled(busy || name.isEmpty)
            }
            Button(L10n.t("form.same", state.language)) {
                run {
                    let c = try await
                        ApiClient.shared.embodimentConsistency(
                            id: state.pid!)
                    let forms = (c.embodiments ?? []).compactMap(\.name)
                    line = forms.joined(separator: " · ")
                }
            }.font(.caption).disabled(busy)
            HStack {
                TextField(L10n.t("plc.label", state.language),
                          text: $screenLabel)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("disp.title", state.language)) {
                    run {
                        let screens = try await
                            ApiClient.shared.profileDisplays(
                                id: state.pid!, token: state.token!)
                        line = screens.displays.compactMap(\.label)
                            .joined(separator: " · ")
                    }
                }.font(.caption).disabled(busy)
                Button(L10n.t("src.add", state.language)) {
                    run {
                        _ = try await ApiClient.shared.addProfileDisplay(
                            id: state.pid!, kind: "wall_panel",
                            label: screenLabel, token: state.token!)
                        screenLabel = ""
                    }
                }.font(.caption).disabled(busy || screenLabel.isEmpty)
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
        rows = (try? await ApiClient.shared.embodiments(
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

struct SteeringSection: View {
    @EnvironmentObject var state: AppState
    @State private var pace = ""
    @State private var autonomy = ""
    @State private var line: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("steer.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            Button(L10n.t("steer.show", state.language)) {
                run {
                    let s = try await ApiClient.shared.steering(
                        id: state.pid!, token: state.token!)
                    line = s.values.map { "\($0.key) \($0.value)" }
                        .sorted().joined(separator: " · ")
                }
            }.font(.caption).disabled(busy)
            HStack {
                TextField(L10n.t("steer.pace", state.language), text: $pace)
                    .textFieldStyle(.roundedBorder)
                TextField(L10n.t("steer.autonomy", state.language),
                          text: $autonomy)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("steer.set", state.language)) {
                    run {
                        var values: [String: Int] = [:]
                        if let p = Int(pace) { values["pace"] = p }
                        if let a = Int(autonomy) { values["autonomy"] = a }
                        _ = try await ApiClient.shared.setSteering(
                            id: state.pid!, values: values,
                            token: state.token!)
                        pace = ""; autonomy = ""
                    }
                }.font(.caption)
                    .disabled(busy || (pace.isEmpty && autonomy.isEmpty))
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

struct WristSection: View {
    @EnvironmentObject var state: AppState
    @State private var target = "workflow"
    @State private var targetId = ""
    @State private var action = "advance"
    @State private var answer = ""
    @State private var line: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("wrist.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            Button(L10n.t("wrist.show", state.language)) {
                run {
                    let f = try await ApiClient.shared.watchFace(
                        id: state.pid!, token: state.token!)
                    let light = f.profile.light ?? "—"
                    line = light + " · \(f.summary.working) · "
                        + "\(f.summary.needing_assistance) · "
                        + "\(f.summary.stopped)"
                }
            }.font(.caption).disabled(busy)
            HStack {
                TextField(L10n.t("wrist.target", state.language),
                          text: $target)
                    .textFieldStyle(.roundedBorder)
                TextField(L10n.t("wrist.id", state.language),
                          text: $targetId)
                    .textFieldStyle(.roundedBorder)
            }
            HStack {
                TextField(L10n.t("wrist.action", state.language),
                          text: $action)
                    .textFieldStyle(.roundedBorder)
                TextField(L10n.t("wrist.input", state.language),
                          text: $answer)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("wrist.act", state.language)) {
                    run {
                        let out = try await ApiClient.shared.watchAct(
                            id: state.pid!, target: target,
                            targetId: targetId, action: action,
                            input: answer, token: state.token!)
                        answer = ""
                        line = out.status
                    }
                }.font(.caption).disabled(busy || targetId.isEmpty
                                          || action.isEmpty)
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
