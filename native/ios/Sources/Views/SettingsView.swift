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

                SteeringCard()

                WatermarkCard()
                WhoWroteThisCard()
                ObjectToAProfileCard()

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
            Text("Watermark").font(.headline).foregroundStyle(Theme.txt)
            Text("Every piece of work your profile composes or generates carries this mark — on all textual and visual renders, at all times. Design it your way; the AI designation always stays.")
                .font(.footnote).foregroundStyle(Theme.t2)
            if !line.isEmpty {
                Text(line).font(.caption.bold()).foregroundStyle(Theme.t2)
                    .padding(.horizontal, 10).padding(.vertical, 6)
                    .background(Theme.scrBot)
                    .clipShape(Capsule())
            }
            HStack(spacing: 8) {
                TextField("mark (✦)", text: $mark)
                    .foregroundStyle(Theme.txt)
                    .padding(.horizontal, 10).padding(.vertical, 8)
                    .background(Theme.scrBot)
                    .clipShape(RoundedRectangle(cornerRadius: 10))
                    .frame(width: 90)
                TextField("label (AI · \(state.displayName))", text: $label)
                    .foregroundStyle(Theme.txt)
                    .padding(.horizontal, 10).padding(.vertical, 8)
                    .background(Theme.scrBot)
                    .clipShape(RoundedRectangle(cornerRadius: 10))
            }
            HStack(spacing: 10) {
                Button("Save design") { Task { await save() } }
                    .font(.caption.bold()).foregroundStyle(.white)
                    .padding(.horizontal, 12).padding(.vertical, 7)
                    .background(Theme.brand).clipShape(Capsule())
                if custom {
                    Button("Reset to default") { Task { await reset() } }
                        .font(.caption).foregroundStyle(Theme.t2)
                }
                if saved {
                    Text("✓ saved").font(.caption).foregroundStyle(Theme.green)
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
    @State private var text = ""
    @State private var result: WatermarkRecovery?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("Who wrote this?").font(.headline).foregroundStyle(Theme.txt)
            Text("Paste any passage. If a profile here produced it, this names "
                 + "it — even if the wording has since been changed.")
                .font(.footnote).foregroundStyle(Theme.t2)
            TextField("Paste a passage…", text: $text, axis: .vertical)
                .lineLimit(3...6)
                .font(.subheadline).foregroundStyle(Theme.txt)
                .padding(10).background(Theme.scrBot)
                .clipShape(RoundedRectangle(cornerRadius: 11))
            Button(busy ? "Checking…" : "Check this text") { check() }
                .font(.caption.bold()).foregroundStyle(.white)
                .padding(.horizontal, 12).padding(.vertical, 9)
                .background(Theme.brandA).clipShape(Capsule())
                .disabled(busy || text.trimmingCharacters(in: .whitespaces).isEmpty)

            if let r = result {
                if r.recovered, let pid = r.profile_id {
                    Text(r.state == "unaltered"
                         ? "Written by \(pid), unaltered."
                         : "Written by \(pid) — altered since.")
                        .font(.subheadline.bold())
                        .foregroundStyle(r.verbatim == true ? Theme.green : Theme.amber)
                    if let matched = r.matched_windows, let stored = r.stored_windows {
                        Text("\(matched) of \(stored) passages matched"
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
                    Text(r.reason ?? "No profile here produced this text.")
                        .font(.caption).foregroundStyle(Theme.t2)
                    if let best = r.best_similarity, let threshold = r.threshold {
                        Text("closest overlap \(best), below the \(threshold) "
                             + "threshold for naming anyone")
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
    @State private var profileId = ""
    @State private var contact = ""
    @State private var reason = ""
    @State private var result: ObjectionOpened?
    @State private var busy = false
    @State private var error: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("Object to a profile").font(.headline).foregroundStyle(Theme.txt)
            Text("If a synthetic profile here is of you and you did not agree "
                 + "to it, say so. You do not need an account, and you do not "
                 + "need to be signed in.")
                .font(.footnote).foregroundStyle(Theme.t2)

            TextField("Profile id", text: $profileId)
                .textFieldStyle(.roundedBorder).autocapitalization(.none)
            TextField("How to reach you", text: $contact)
                .textFieldStyle(.roundedBorder).autocapitalization(.none)
            TextField("What is wrong", text: $reason, axis: .vertical)
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
                Text("Raise an objection").frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent).tint(Theme.brandA)
            .disabled(busy || profileId.trimmingCharacters(in: .whitespaces).isEmpty
                      || reason.trimmingCharacters(in: .whitespaces).isEmpty)

            if let r = result {
                // The profile is restricted immediately, pending review. That
                // is the part the person raising it needs told — the remedy is
                // now, not after somebody gets round to it.
                Text("Raised. The profile is \(r.profile_status ?? "restricted") "
                     + "pending review.")
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
