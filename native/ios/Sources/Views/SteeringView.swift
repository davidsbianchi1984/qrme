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

    private let groupLabels = ["system": "System", "behavior": "Behavior",
                               "intimacy": "Intimacy (18+)"]

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("Steering").font(.headline).foregroundStyle(Theme.txt)
            Text("Shape how \(state.displayName.isEmpty ? "the profile" : state.displayName) comes across — tone, pace, manner, look, age. Steering, not piloting: it acts on its own within this shape.")
                .font(.caption).foregroundStyle(Theme.t2)

            if let hub {
                ForEach(["system", "behavior", "intimacy"], id: \.self) { group in
                    let dials = hub.dials.filter { $0.group == group }
                    if !dials.isEmpty {
                        Text(groupLabels[group] ?? group.capitalized)
                            .font(.caption.bold()).foregroundStyle(Theme.brandA)
                        ForEach(dials) { dial in
                            dialRow(dial)
                        }
                    }
                }

                Divider().overlay(Theme.line)
                Text("Appearance").font(.caption.bold()).foregroundStyle(Theme.brandA)
                TextField("How they look and present…", text: $appearance, axis: .vertical)
                    .lineLimit(1...3).foregroundStyle(Theme.txt)
                    .padding(10).background(Theme.scrBot)
                    .clipShape(RoundedRectangle(cornerRadius: 11))
                    .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))

                Text("Age").font(.caption.bold()).foregroundStyle(Theme.brandA)
                HStack(spacing: 10) {
                    TextField("base age", text: $baseAge)
                        .keyboardType(.numberPad).frame(width: 80)
                        .foregroundStyle(Theme.txt)
                        .padding(8).background(Theme.scrBot)
                        .clipShape(RoundedRectangle(cornerRadius: 9))
                    Toggle("Ages over time", isOn: $agingEnabled)
                        .font(.caption).foregroundStyle(Theme.txt)
                        .tint(Theme.green)
                }
                if let eff = hub.age.effective_age {
                    Text("Effective age now: \(eff)")
                        .font(.caption2).foregroundStyle(Theme.t3)
                }

                Button("Apply steering") { apply() }
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
                status = "Steering applied — it rides on every reply."
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
            Text("Your relationship").font(.headline).foregroundStyle(Theme.txt)
            Text("How the profile relates to you in chat — its framing, your nickname, the tone it takes.")
                .font(.caption).foregroundStyle(Theme.t2)
            Picker("", selection: $type) {
                ForEach(types, id: \.self) {
                    Text($0.replacingOccurrences(of: "_", with: " ").capitalized).tag($0)
                }
            }
            .pickerStyle(.menu).tint(Theme.brandA)
            TextField("nickname it calls you (optional)", text: $nickname)
                .foregroundStyle(Theme.txt)
                .padding(10).background(Theme.scrBot)
                .clipShape(RoundedRectangle(cornerRadius: 11))
                .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
            TextField("tone (e.g. gentle, playful) — optional", text: $tone)
                .foregroundStyle(Theme.txt)
                .padding(10).background(Theme.scrBot)
                .clipShape(RoundedRectangle(cornerRadius: 11))
                .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
            Button("Save relationship") { save() }
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
                    state.rememberInteractor(created.id)
                    interactor = created.id
                }
                let r = try await ApiClient.shared.setRelationship(
                    id: pid, token: token, interactorId: interactor!,
                    type: type, nickname: nickname, tone: tone)
                status = "Saved — it now treats you as \(r.relationship_type.replacingOccurrences(of: "_", with: " "))."
            } catch { status = error.localizedDescription }
        }
    }
}
