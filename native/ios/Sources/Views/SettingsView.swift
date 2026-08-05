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
                Text(L10n.t("tab.settings", state.language))
                    .font(.title2.bold()).foregroundStyle(Theme.txt)

                VStack(alignment: .leading, spacing: 10) {
                    Text(L10n.t("ns.model", state.language)).font(.headline).foregroundStyle(Theme.txt)
                    Text(L10n.t("ns.model.sub", state.language))
                        .font(.footnote).foregroundStyle(Theme.t2)
                    ForEach(providers, id: \.name) { p in
                        Button { choose(p.name) } label: {
                            HStack {
                                Circle().fill(p.name == current ? Theme.brandA : Theme.card)
                                    .overlay(Circle().stroke(Theme.line, lineWidth: 1))
                                    .frame(width: 16, height: 16)
                                Text(p.label).font(.subheadline).foregroundStyle(Theme.txt)
                                Spacer()
                                Text(L10n.t(p.configured ? "ns.model.ready" : "ns.model.nokey", state.language))
                                    .font(.caption)
                                    .foregroundStyle(p.configured ? Theme.green : Theme.t3)
                            }
                        }
                    }
                    if !effective.isEmpty {
                        Text(L10n.fill("ns.model.effective", state.language, ["name": effective]))
                            .font(.caption).foregroundStyle(Theme.t2)
                    }
                }.card()

                VStack(alignment: .leading, spacing: 8) {
                    Text(L10n.t("ns.lang", state.language)).font(.headline).foregroundStyle(Theme.txt)
                    Text(L10n.t("ns.lang.sub", state.language))
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
                            Text(L10n.t("ns.lang.pre", state.language))
                                .font(.subheadline).foregroundStyle(Theme.txt)
                            Text(L10n.t("ns.lang.pre.sub", state.language))
                                .font(.caption2).foregroundStyle(Theme.t2)
                        }
                    }
                    .tint(Theme.green)
                    .onChange(of: preTranslate) { _ in applyLanguage() }
                    Divider().overlay(Theme.line)
                    Text(L10n.t("ns.tr", state.language)).font(.subheadline.bold()).foregroundStyle(Theme.txt)
                    TextField(L10n.t("ns.tr.ph", state.language), text: $translateInput, axis: .vertical)
                        .lineLimit(1...4).foregroundStyle(Theme.txt)
                        .padding(10).background(Theme.scrBot)
                        .clipShape(RoundedRectangle(cornerRadius: 11))
                        .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                    Button(L10n.t("action.translate", state.language)) { runTranslate() }
                        .font(.caption.bold()).foregroundStyle(.white)
                        .padding(.horizontal, 12).padding(.vertical, 8)
                        .background(Theme.brandA).clipShape(Capsule())
                        .disabled(translateInput.isEmpty || language == "en")
                    if let r = translateResult {
                        Text(r.translation).font(.subheadline).foregroundStyle(Theme.txt)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding(10).background(Theme.scrBot)
                            .clipShape(RoundedRectangle(cornerRadius: 9))
                        Text(L10n.fill("ns.tr.engine", state.language, ["engine": r.engine])
                             + (r.note.map { " — \($0)" } ?? ""))
                            .font(.caption2).foregroundStyle(Theme.t3)
                    }
                }.card()

                VStack(alignment: .leading, spacing: 10) {
                    Text(L10n.t("ns.obj", state.language)).font(.headline).foregroundStyle(Theme.txt)
                    if objections.isEmpty {
                        Text(L10n.t("ns.obj.none", state.language))
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
                                    Button(L10n.t("ns.obj.attest", state.language)) { attest(o) }
                                        .font(.caption.bold()).foregroundStyle(.white)
                                        .padding(.horizontal, 12).padding(.vertical, 7)
                                        .background(Theme.brandA).clipShape(Capsule())
                                } else if o.reattested == 1 {
                                    Text(L10n.t("ns.obj.attested", state.language))
                                        .font(.caption).foregroundStyle(Theme.green)
                                }
                            }
                            .padding(.vertical, 4)
                        }
                    }
                }.card()

                SteeringCard()

                WatermarkCard()
                WhoWroteThisCard()
                ObjectToAProfileCard()
                ProblemReportingCard()

                RelationshipCard()

                FeedbackCard()

                if let error { Text(error).font(.footnote).foregroundStyle(Theme.red) }
            }.padding(20)
        }
        .refreshable { await load() }
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
            state.rememberLanguage(l.language)   // chrome follows the profile
        }
    }

    private func applyLanguage() {
        guard let pid = state.pid, let token = state.token else { return }
        state.rememberLanguage(language)
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

/// Design the profile's watermark — the visible mark that rides on every
/// AI render, textual or visual. The AI designation itself is invariant.
struct WatermarkCard: View {
    @EnvironmentObject var state: AppState
    @State private var mark = ""
    @State private var label = ""
    @State private var line = ""
    @State private var custom = false
    @State private var saved = false

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(L10n.t("ns.wm", state.language)).font(.headline).foregroundStyle(Theme.txt)
            Text(L10n.t("ns.wm.sub", state.language))
                .font(.footnote).foregroundStyle(Theme.t2)
            if !line.isEmpty {
                Text(line).font(.caption.bold()).foregroundStyle(Theme.t2)
                    .padding(.horizontal, 10).padding(.vertical, 6)
                    .background(Theme.scrBot)
                    .clipShape(Capsule())
            }
            HStack(spacing: 8) {
                TextField(L10n.t("ns.wm.mark", state.language), text: $mark)
                    .foregroundStyle(Theme.txt)
                    .padding(.horizontal, 10).padding(.vertical, 8)
                    .background(Theme.scrBot)
                    .clipShape(RoundedRectangle(cornerRadius: 10))
                    .frame(width: 90)
                TextField(L10n.fill("ns.wm.label.ph", state.language,
                                    ["name": state.displayName]), text: $label)
                    .foregroundStyle(Theme.txt)
                    .padding(.horizontal, 10).padding(.vertical, 8)
                    .background(Theme.scrBot)
                    .clipShape(RoundedRectangle(cornerRadius: 10))
            }
            HStack(spacing: 10) {
                Button(L10n.t("ns.wm.save", state.language)) { Task { await save() } }
                    .font(.caption.bold()).foregroundStyle(.white)
                    .padding(.horizontal, 12).padding(.vertical, 7)
                    .background(Theme.brand).clipShape(Capsule())
                if custom {
                    Button(L10n.t("ns.wm.reset", state.language)) { Task { await reset() } }
                        .font(.caption).foregroundStyle(Theme.t2)
                }
                if saved {
                    Text(L10n.t("ns.wm.saved", state.language)).font(.caption).foregroundStyle(Theme.green)
                }
            }
        }.card()
        .task { await load() }
    }

    private func load() async {
        guard let pid = state.pid else { return }
        if let d = try? await ApiClient.shared.watermarkDesign(id: pid) {
            line = d.line; custom = d.custom
        }
    }

    private func save() async {
        guard let pid = state.pid, let token = state.token else { return }
        if let d = try? await ApiClient.shared.setWatermarkDesign(
            id: pid, token: token, mark: mark, label: label) {
            line = d.line; custom = d.custom; saved = true
        }
    }

    private func reset() async {
        guard let pid = state.pid, let token = state.token else { return }
        if let d = try? await ApiClient.shared.setWatermarkDesign(
            id: pid, token: token, mark: nil, label: nil) {
            line = d.line; custom = d.custom
            mark = ""; label = ""; saved = false
        }
    }
}

/// The other direction of the watermark: paste any text and it names the
/// profile that produced it, from the text alone.
///
/// `/watermarks/verify` needs a credential id up front and fails on one edited
/// character. This asks "whose work is this" with no id, and keeps answering
/// after the text has been rewritten — so the counts are shown rather than a
/// bare yes, and below the threshold it deliberately names nobody.
struct WhoWroteThisCard: View {
    @EnvironmentObject var state: AppState
    @State private var text = ""
    @State private var result: WatermarkRecovery?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(L10n.t("ns.who", state.language)).font(.headline).foregroundStyle(Theme.txt)
            Text(L10n.t("ns.who.sub", state.language))
                .font(.footnote).foregroundStyle(Theme.t2)
            TextField(L10n.t("ns.who.ph", state.language), text: $text, axis: .vertical)
                .lineLimit(3...6)
                .font(.subheadline).foregroundStyle(Theme.txt)
                .padding(10).background(Theme.scrBot)
                .clipShape(RoundedRectangle(cornerRadius: 11))
            Button(L10n.t(busy ? "ns.who.checking" : "ns.who.check", state.language)) { check() }
                .font(.caption.bold()).foregroundStyle(.white)
                .padding(.horizontal, 12).padding(.vertical, 9)
                .background(Theme.brandA).clipShape(Capsule())
                .disabled(busy || text.trimmingCharacters(in: .whitespaces).isEmpty)

            if let r = result {
                if r.recovered, let pid = r.profile_id {
                    Text(L10n.fill(r.state == "unaltered" ? "ns.who.by" : "ns.who.by.altered",
                                   state.language, ["id": pid]))
                        .font(.subheadline.bold())
                        .foregroundStyle(r.verbatim == true ? Theme.green : Theme.amber)
                    if let matched = r.matched_windows, let stored = r.stored_windows {
                        Text(L10n.fill("ns.who.matched", state.language,
                                       ["matched": "\(matched)", "stored": "\(stored)"])
                             + (r.similarity.map { " · similarity \($0)" } ?? ""))
                            .font(.caption).monospacedDigit().foregroundStyle(Theme.t2)
                    }
                    if let mark = r.display?.line {
                        Text(mark).font(.caption2).foregroundStyle(Theme.t3)
                    }
                    if let d = r.disclosure {
                        Text(d).font(.caption2).foregroundStyle(Theme.t3)
                    }
                } else {
                    // Not "no" — the reason, because a coincidence must not
                    // read as an accusation either way.
                    Text(r.reason ?? L10n.t("ns.who.none", state.language))
                        .font(.caption).foregroundStyle(Theme.t2)
                    if let best = r.best_similarity, let threshold = r.threshold {
                        Text(L10n.fill("ns.who.below", state.language,
                                       ["best": "\(best)", "threshold": "\(threshold)"]))
                            .font(.caption2).foregroundStyle(Theme.t3)
                    }
                }
                if let method = r.method {
                    Text(method).font(.caption2).foregroundStyle(Theme.t3)
                }
            }
        }
        .card()
    }

    private func check() {
        busy = true
        Task {
            result = try? await ApiClient.shared.recoverWatermark(content: text)
            busy = false
        }
    }
}

/// Raising an objection — the half of governance that belongs to the person
/// who is *not* the profile's owner.
///
/// This shell already carried the owner's half: list the objections against
/// your own profile, and attest to them. It carried nothing for the person on
/// the other side of that, and `open_objection` is explicit about who they
/// are — *the objecting party need not own an account*.
///
/// Somebody who finds a synthetic profile of themselves has, by construction,
/// no QRME account and therefore no console. A phone is the surface they have.
/// It is placed beside "Who wrote this?" because it is the same person at the
/// next step: they have identified the profile, and now they want it stopped.
struct ObjectToAProfileCard: View {
    @EnvironmentObject var state: AppState
    @State private var profileId = ""
    @State private var contact = ""
    @State private var reason = ""
    @State private var result: ObjectionOpened?
    @State private var busy = false
    @State private var error: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(L10n.t("ns.object", state.language)).font(.headline).foregroundStyle(Theme.txt)
            Text(L10n.t("ns.object.sub", state.language))
                .font(.footnote).foregroundStyle(Theme.t2)

            TextField(L10n.t("ns.object.pid", state.language), text: $profileId)
                .textFieldStyle(.roundedBorder).autocapitalization(.none)
            TextField(L10n.t("ns.object.contact", state.language), text: $contact)
                .textFieldStyle(.roundedBorder).autocapitalization(.none)
            TextField(L10n.t("ns.object.reason", state.language), text: $reason, axis: .vertical)
                .textFieldStyle(.roundedBorder).lineLimit(2...4)

            Button {
                Task {
                    busy = true; error = nil
                    do {
                        result = try await Api.shared.openObjection(
                            profileId: profileId.trimmingCharacters(in: .whitespaces),
                            objectorRef: contact.trimmingCharacters(in: .whitespaces),
                            reason: reason)
                    } catch { self.error = error.localizedDescription }
                    busy = false
                }
            } label: {
                Text(L10n.t("ns.object.go", state.language)).frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent).tint(Theme.brandA)
            .disabled(busy || profileId.trimmingCharacters(in: .whitespaces).isEmpty
                      || reason.trimmingCharacters(in: .whitespaces).isEmpty)

            if let r = result {
                // The profile is restricted immediately, pending review. That
                // is the part the person raising it needs told — the remedy is
                // now, not after somebody gets round to it.
                Text(L10n.fill("ns.object.raised", state.language,
                               ["status": r.profile_status ?? "restricted"]))
                    .font(.footnote).foregroundStyle(Theme.green)
                if let n = r.note {
                    Text(n).font(.caption2).foregroundStyle(Theme.t2)
                }
            }
            if let e = error {
                Text(e).font(.footnote).foregroundStyle(Theme.red)
            }
        }
        .padding(14)
        .background(Theme.card).clipShape(RoundedRectangle(cornerRadius: 12))
    }
}
