import SwiftUI

/// Settings: which LLM powers the profile, and the governance view — any
/// objections opened against it, with the owner's re-attest action.
struct SettingsView: View {
    @EnvironmentObject var state: AppState
    @State private var providers: [ProviderInfo] = []
    @State private var current = "auto"
    @State private var effective = ""
    @State private var objections: [Objection] = []
    @State private var languages: [LanguageInfo] = []
    @State private var language = "en"
    @State private var preTranslate = true
    @State private var translateInput = ""
    @State private var translateResult: TranslateResult?
    @State private var error: String?

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("Settings").font(.title2.bold()).foregroundStyle(Theme.txt)

                VStack(alignment: .leading, spacing: 10) {
                    Text("Model").font(.headline).foregroundStyle(Theme.txt)
                    Text("Which LLM powers this profile. Unconfigured providers fall back to the offline stub.")
                        .font(.footnote).foregroundStyle(Theme.t2)
                    ForEach(providers, id: \.name) { p in
                        Button { choose(p.name) } label: {
                            HStack {
                                Circle().fill(p.name == current ? Theme.brandA : Theme.card)
                                    .overlay(Circle().stroke(Theme.line, lineWidth: 1))
                                    .frame(width: 16, height: 16)
                                Text(p.label).font(.subheadline).foregroundStyle(Theme.txt)
                                Spacer()
                                Text(p.configured ? "ready" : "no key")
                                    .font(.caption)
                                    .foregroundStyle(p.configured ? Theme.green : Theme.t3)
                            }
                        }
                    }
                    if !effective.isEmpty {
                        Text("Effective now: \(effective)")
                            .font(.caption).foregroundStyle(Theme.t2)
                    }
                }.card()

                VStack(alignment: .leading, spacing: 8) {
                    Text("Language").font(.headline).foregroundStyle(Theme.txt)
                    Text("The profile speaks this language everywhere it appears — chat, posts, rooms, robot speech.")
                        .font(.caption).foregroundStyle(Theme.t2)
                    Picker("", selection: $language) {
                        ForEach(languages, id: \.code) { l in
                            Text(l.label).tag(l.code)
                        }
                    }
                    .pickerStyle(.menu).tint(Theme.brandA)
                    .onChange(of: language) { _ in applyLanguage() }
                    Toggle(isOn: $preTranslate) {
                        VStack(alignment: .leading, spacing: 2) {
                            Text("Speak it natively (pre-translate)")
                                .font(.subheadline).foregroundStyle(Theme.txt)
                            Text("Off keeps the original voice — translate selectively below.")
                                .font(.caption2).foregroundStyle(Theme.t2)
                        }
                    }
                    .tint(Theme.green)
                    .onChange(of: preTranslate) { _ in applyLanguage() }
                    Divider().overlay(Theme.line)
                    Text("Translate anything").font(.subheadline.bold()).foregroundStyle(Theme.txt)
                    TextField("Paste or type text…", text: $translateInput, axis: .vertical)
                        .lineLimit(1...4).foregroundStyle(Theme.txt)
                        .padding(10).background(Theme.scrBot)
                        .clipShape(RoundedRectangle(cornerRadius: 11))
                        .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                    Button("Translate") { runTranslate() }
                        .font(.caption.bold()).foregroundStyle(.white)
                        .padding(.horizontal, 12).padding(.vertical, 8)
                        .background(Theme.brandA).clipShape(Capsule())
                        .disabled(translateInput.isEmpty || language == "en")
                    if let r = translateResult {
                        Text(r.translation).font(.subheadline).foregroundStyle(Theme.txt)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding(10).background(Theme.scrBot)
                            .clipShape(RoundedRectangle(cornerRadius: 9))
                        Text("engine: \(r.engine)" + (r.note.map { " — \($0)" } ?? ""))
                            .font(.caption2).foregroundStyle(Theme.t3)
                    }
                }.card()

                VStack(alignment: .leading, spacing: 10) {
                    Text("Objections").font(.headline).foregroundStyle(Theme.txt)
                    if objections.isEmpty {
                        Text("No objections — nobody has contested this profile.")
                            .font(.footnote).foregroundStyle(Theme.t2)
                    } else {
                        ForEach(objections, id: \.id) { o in
                            VStack(alignment: .leading, spacing: 6) {
                                HStack {
                                    Circle()
                                        .fill(o.status == "open" ? Theme.amber : Theme.t3)
                                        .frame(width: 8, height: 8)
                                    Text(o.status.uppercased())
                                        .font(.caption.bold())
                                        .foregroundStyle(o.status == "open" ? Theme.amber : Theme.t2)
                                    Spacer()
                                }
                                if let reason = o.reason {
                                    Text(reason).font(.footnote).foregroundStyle(Theme.txt)
                                }
                                if o.status == "open" && o.reattested == 0 {
                                    Button("Re-attest my rights basis") { attest(o) }
                                        .font(.caption.bold()).foregroundStyle(.white)
                                        .padding(.horizontal, 12).padding(.vertical, 7)
                                        .background(Theme.brandA).clipShape(Capsule())
                                } else if o.reattested == 1 {
                                    Text("Basis re-attested · awaiting review")
                                        .font(.caption).foregroundStyle(Theme.green)
                                }
                            }
                            .padding(.vertical, 4)
                        }
                    }
                }.card()

                if let error { Text(error).font(.footnote).foregroundStyle(Theme.red) }
            }.padding(20)
        }
        .task { await load() }
    }

    private func load() async {
        guard let pid = state.pid else { return }
        providers = (try? await ApiClient.shared.models())?.providers ?? []
        if let m = try? await ApiClient.shared.profileModel(id: pid) {
            current = m.provider; effective = m.effective
        }
        if let token = state.token {
            objections = (try? await ApiClient.shared.objections(id: pid, token: token)) ?? []
        }
        languages = (try? await ApiClient.shared.languages())?.languages ?? []
        if let l = try? await ApiClient.shared.profileLanguage(id: pid) {
            language = l.language
            preTranslate = (l.mode ?? "pre") == "pre"
        }
    }

    private func applyLanguage() {
        guard let pid = state.pid, let token = state.token else { return }
        Task {
            _ = try? await ApiClient.shared.setLanguage(
                id: pid, token: token, code: language,
                mode: preTranslate ? "pre" : "on_demand")
        }
    }

    private func runTranslate() {
        guard let pid = state.pid, let token = state.token else { return }
        Task {
            translateResult = try? await ApiClient.shared.translate(
                id: pid, token: token, text: translateInput)
        }
    }

    private func choose(_ provider: String) {
        guard let pid = state.pid, let token = state.token else { return }
        error = nil
        Task {
            do {
                let m = try await ApiClient.shared.setModel(id: pid, token: token,
                                                            provider: provider)
                current = m.provider; effective = m.effective
            } catch { self.error = error.localizedDescription }
        }
    }

    private func attest(_ objection: Objection) {
        guard let pid = state.pid, let token = state.token else { return }
        Task {
            try? await ApiClient.shared.attest(id: pid, objectionId: objection.id,
                                               token: token)
            await load()
        }
    }
}
