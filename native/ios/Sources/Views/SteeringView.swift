import SwiftUI

/// Steering, not piloting: the owner shapes how the profile comes across —
/// tone, pace, manner — plus its appearance and age, in one hub. The profile
/// still acts autonomously within that shape.
struct SteeringCard: View {
    @EnvironmentObject var state: AppState
    @State private var hub: SteeringHubState?
    @State private var values: [String: Double] = [:]
    @State private var appearance = ""
    @State private var baseAge = ""
    @State private var agingEnabled = false
    @State private var status: String?

    private let groupKeys = ["system": "ns.st.g.system",
                             "behavior": "ns.st.g.behavior",
                             "intimacy": "ns.st.g.intimacy"]

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(L10n.t("ns.st", state.language)).font(.headline).foregroundStyle(Theme.txt)
            Text(L10n.fill("ns.st.sub", state.language, ["name": state.displayName.isEmpty
                                        ? L10n.t("ns.st.the_profile", state.language)
                                        : state.displayName]))
                .font(.caption).foregroundStyle(Theme.t2)

            if let hub {
                ForEach(["system", "behavior", "intimacy"], id: \.self) { group in
                    let dials = hub.dials.filter { $0.group == group }
                    if !dials.isEmpty {
                        Text(L10n.t(groupKeys[group] ?? group, state.language))
                            .font(.caption.bold()).foregroundStyle(Theme.brandA)
                        ForEach(dials) { dial in
                            dialRow(dial)
                        }
                    }
                }

                Divider().overlay(Theme.line)
                Text(L10n.t("ns.st.appearance", state.language)).font(.caption.bold()).foregroundStyle(Theme.brandA)
                TextField(L10n.t("ns.st.appearance.ph", state.language), text: $appearance, axis: .vertical)
                    .lineLimit(1...3).foregroundStyle(Theme.txt)
                    .padding(10).background(Theme.scrBot)
                    .clipShape(RoundedRectangle(cornerRadius: 11))
                    .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))

                Text(L10n.t("ns.st.age", state.language)).font(.caption.bold()).foregroundStyle(Theme.brandA)
                HStack(spacing: 10) {
                    TextField(L10n.t("ns.st.baseage", state.language), text: $baseAge)
                        .keyboardType(.numberPad).frame(width: 80)
                        .foregroundStyle(Theme.txt)
                        .padding(8).background(Theme.scrBot)
                        .clipShape(RoundedRectangle(cornerRadius: 9))
                    Toggle(L10n.t("ns.st.aging", state.language), isOn: $agingEnabled)
                        .font(.caption).foregroundStyle(Theme.txt)
                        .tint(Theme.green)
                }
                if let eff = hub.age.effective_age {
                    Text(L10n.fill("ns.st.effective", state.language, ["age": "\(eff)"]))
                        .font(.caption2).foregroundStyle(Theme.t3)
                }

                Button(L10n.t("ns.st.apply", state.language)) { apply() }
                    .font(.caption.bold()).foregroundStyle(.white)
                    .padding(.horizontal, 12).padding(.vertical, 9)
                    .background(Theme.brandA).clipShape(Capsule())
                if let status {
                    Text(status).font(.caption).foregroundStyle(Theme.green)
                }
            } else {
                ProgressView().tint(Theme.brandA)
            }
        }.card()
        .task { await load() }
    }

    @ViewBuilder
    private func dialRow(_ dial: SteeringDial) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            HStack {
                Text(dial.label).font(.subheadline).foregroundStyle(Theme.txt)
                Spacer()
                Text("\(Int(values[dial.name] ?? 50))")
                    .font(.caption.bold()).foregroundStyle(Theme.brandA)
                    .monospacedDigit()
            }
            Slider(value: Binding(
                get: { values[dial.name] ?? 50 },
                set: { values[dial.name] = $0 }
            ), in: Double(dial.min)...Double(dial.max))
            .tint(Theme.brandA)
            HStack {
                Text(dial.low).font(.caption2).foregroundStyle(Theme.t3)
                Spacer()
                Text(dial.high).font(.caption2).foregroundStyle(Theme.t3)
            }
        }
    }

    private func load() async {
        guard let pid = state.pid, let token = state.token else { return }
        if let h = try? await ApiClient.shared.steeringHub(id: pid, token: token) {
            hub = h
            values = h.values.mapValues(Double.init)
            appearance = h.appearance.description ?? ""
            baseAge = h.age.base_age.map(String.init) ?? ""
            agingEnabled = h.age.aging_enabled
        }
    }

    private func apply() {
        guard let pid = state.pid, let token = state.token else { return }
        status = nil
        Task {
            do {
                let h = try await ApiClient.shared.setSteeringHub(
                    id: pid, token: token,
                    values: values.mapValues { Int($0) },
                    baseAge: Int(baseAge),
                    agingEnabled: agingEnabled,
                    appearance: appearance.isEmpty ? nil : appearance)
                hub = h
                status = L10n.t("ns.st.applied", state.language)
            } catch { status = error.localizedDescription }
        }
    }
}

/// How the profile relates to *you*: the owner sets the relationship type,
/// a nickname, tone, and boundaries for their own interactor identity.
struct RelationshipCard: View {
    @EnvironmentObject var state: AppState
    @State private var type = "friend"
    @State private var nickname = ""
    @State private var tone = ""
    @State private var status: String?

    private let types = ["family", "grandchild", "friend", "romantic_partner",
                         "professional", "fan", "stranger"]

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(L10n.t("ns.rel", state.language)).font(.headline).foregroundStyle(Theme.txt)
            Text(L10n.t("ns.rel.sub", state.language))
                .font(.caption).foregroundStyle(Theme.t2)
            Picker("", selection: $type) {
                // `$0.replacingOccurrences(…).capitalized` renders the API's
                // member as if it were a word. The seven labels are the
                // console's own `rel.t.*` rows, ported rather than rewritten.
                ForEach(types, id: \.self) {
                    Text(L10n.t("ns.rel.t.\($0)", state.language)).tag($0)
                }
            }
            .pickerStyle(.menu).tint(Theme.brandA)
            TextField(L10n.t("ns.rel.nick.ph", state.language), text: $nickname)
                .foregroundStyle(Theme.txt)
                .padding(10).background(Theme.scrBot)
                .clipShape(RoundedRectangle(cornerRadius: 11))
                .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
            TextField(L10n.t("ns.rel.tone.ph", state.language), text: $tone)
                .foregroundStyle(Theme.txt)
                .padding(10).background(Theme.scrBot)
                .clipShape(RoundedRectangle(cornerRadius: 11))
                .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
            Button(L10n.t("ns.rel.save", state.language)) { save() }
                .font(.caption.bold()).foregroundStyle(.white)
                .padding(.horizontal, 12).padding(.vertical, 9)
                .background(Theme.brandA).clipShape(Capsule())
            if let status { Text(status).font(.caption).foregroundStyle(Theme.green) }
        }.card()
    }

    private func save() {
        guard let pid = state.pid, let token = state.token else { return }
        status = nil
        Task {
            do {
                var interactor = state.interactorId
                if interactor == nil {
                    let created = try await ApiClient.shared.createInteractor(name: "You")
                    state.rememberInteractor(created.id, token: created.token)
                    interactor = created.id
                }
                let r = try await ApiClient.shared.setRelationship(
                    id: pid, token: token, interactorId: interactor!,
                    type: type, nickname: nickname, tone: tone)
                status = L10n.fill("ns.rel.saved", state.language,
                                   ["type": L10n.t("ns.rel.t.\(r.relationship_type)", state.language)])
            } catch { status = error.localizedDescription }
        }
    }
}
