import SwiftUI

/// Studio: the profile's creative surface — Compose, the Posts feed, and
/// Knowledge Excursions — grouped behind one tab so the bar stays tidy.
struct StudioView: View {
    /// Same split as `ConnectView.Tab`: raw values name the sections, the
    /// table holds the words.
    enum Tab: String, CaseIterable { case compose, posts, study, widgets }
    @EnvironmentObject var state: AppState
    @State private var tab: Tab = .compose

    var body: some View {
        VStack(spacing: 0) {
            Picker("", selection: $tab) {
                ForEach(Tab.allCases, id: \.self) { Text(L10n.t("tab.\($0.rawValue)", state.language)).tag($0) }
            }
            .pickerStyle(.segmented)
            .padding(.horizontal, 20).padding(.top, 8)

            switch tab {
            case .compose: ComposeView()
            case .posts: PostsView()
            case .study: StudyView()
            case .widgets: WidgetsView()
            }
        }
    }
}

/// Knowledge Excursions: study a topic safely. Everything outbound is
/// sanitized (private names never leave), and the sanitized brief is shown so
/// the owner can verify exactly what could leave the host.
struct StudyView: View {
    @EnvironmentObject var state: AppState
    @State private var topic = ""
    @State private var question = ""
    @State private var excursions: [Excursion] = []
    @State private var busy = false
    @State private var error: String?

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text(L10n.t("nstu", state.language)).font(.title2.bold()).foregroundStyle(Theme.txt)
                Text(L10n.t("nstu.sub", state.language))
                    .font(.footnote).foregroundStyle(Theme.t2)

                VStack(alignment: .leading, spacing: 10) {
                    field(L10n.t("ncmp.topic", state.language)) { TextField(L10n.t("nstu.topic.ph", state.language), text: $topic)
                        .foregroundStyle(Theme.txt) }
                    field(L10n.t("nstu.question", state.language)) { TextField(L10n.t("nstu.question.ph", state.language), text: $question,
                                                  axis: .vertical)
                        .lineLimit(1...3).foregroundStyle(Theme.txt) }
                    Button(action: start) {
                        HStack { if busy { ProgressView().tint(.white) }; Text(L10n.t("nstu.go", state.language)).bold() }
                            .frame(maxWidth: .infinity).padding(.vertical, 12)
                            .background(Theme.brand).foregroundStyle(.white)
                            .clipShape(RoundedRectangle(cornerRadius: 12))
                    }.disabled(topic.isEmpty || question.isEmpty || busy)
                }.card()

                if let error { Text(error).font(.footnote).foregroundStyle(Theme.red) }

                ForEach(excursions.reversed(), id: \.id) { e in
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Text(e.topic).font(.subheadline.bold()).foregroundStyle(Theme.txt)
                            Spacer()
                            Text(L10n.t(e.left_host ? "nstu.lefthost" : "nstu.stayedlocal", state.language))
                                .font(.caption2.bold())
                                .padding(.horizontal, 7).padding(.vertical, 3)
                                .background((e.left_host ? Theme.amber : Theme.green).opacity(0.16))
                                .foregroundStyle(e.left_host ? Theme.amber : Theme.green)
                                .clipShape(Capsule())
                        }
                        if e.redactions > 0 {
                            Text(L10n.fill("nstu.redacted", state.language, ["n": "\(e.redactions)"]))
                                .font(.caption).foregroundStyle(Theme.t2)
                        }
                        Text(e.findings).font(.footnote).foregroundStyle(Theme.txt)
                        if e.learned {
                            Text(L10n.t("nstu.folded", state.language))
                                .font(.caption).foregroundStyle(Theme.green)
                        } else {
                            Button(L10n.t("nstu.fold", state.language)) { learn(e) }
                                .font(.caption.bold()).foregroundStyle(.white)
                                .padding(.horizontal, 12).padding(.vertical, 7)
                                .background(Theme.brandA).clipShape(Capsule())
                        }
                    }.card()
                }
            }.padding(20)
        }
        .task { await load() }
    }

    private func field<Content: View>(_ label: String, @ViewBuilder _ content: () -> Content) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(label).font(.caption).foregroundStyle(Theme.t2)
            content()
                .padding(.horizontal, 12).padding(.vertical, 10)
                .background(Theme.scrBot).clipShape(RoundedRectangle(cornerRadius: 11))
                .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
        }
    }

    private func load() async {
        guard let pid = state.pid, let token = state.token else { return }
        excursions = (try? await ApiClient.shared.excursions(id: pid, token: token)) ?? []
    }

    private func start() {
        guard let pid = state.pid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do {
                _ = try await ApiClient.shared.startExcursion(
                    id: pid, token: token, topic: topic, question: question)
                topic = ""; question = ""
            } catch { self.error = error.localizedDescription }
            await load(); busy = false
        }
    }

    private func learn(_ excursion: Excursion) {
        guard let token = state.token else { return }
        Task {
            try? await ApiClient.shared.learn(cid: excursion.id, token: token)
            await load()
        }
    }
}

/// Widgets: small programs somebody writes for their own profile.
///
/// The code runs on the backend, in a box with no network, one directory,
/// no child processes and finite time — never on the phone, and never
/// anywhere it could read another profile. This screen is the editor and
/// the answer; `qrme/widgets.py` is the box.
///
/// A run that throws, runs too long, or is stopped by a limit comes back
/// 200 with a status, because the request was fine and the code was not.
/// The sentence beside it is the backend's, in the reader's language.
struct WidgetsView: View {
    @EnvironmentObject var state: AppState
    @State private var widgets: [WidgetRow] = []
    @State private var open: WidgetRow?
    @State private var name = ""
    @State private var source = "module.exports = () => 1;"
    @State private var answer: WidgetAnswer?
    @State private var caps: WidgetLimits?
    @State private var busy = false
    @State private var error: String?
    // The agent. Its conversation lives here rather than on the server: it
    // has no memory of its own, so leaving this screen is all of forgetting.
    @State private var reach: AgentReach?
    @State private var ask = ""
    @State private var asking = false
    @State private var showsReach = false
    @State private var talk: [[String: String]] = []
    @State private var did: AgentTurn?

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 12) {
                if let error { Text(error).foregroundColor(.red).font(.footnote) }

                Text(L10n.t("wdg.ask.title", state.language)).font(.headline)
                Text(L10n.t("wdg.ask.sub", state.language))
                    .font(.footnote).foregroundColor(.secondary)
                Button(showsReach ? L10n.t("wdg.reach.hide", state.language)
                                  : L10n.t("wdg.reach.show", state.language)) {
                    showsReach.toggle()
                }.font(.footnote)
                if showsReach, let reach {
                    ForEach(reach.can_touch, id: \.self) { line in
                        Text("• " + line).font(.footnote)
                            .foregroundColor(.secondary)
                    }
                }
                if let reach, !reach.available {
                    Text(L10n.t("wdg.ask.nomodel", state.language))
                        .font(.footnote).foregroundColor(.secondary)
                }
                TextEditor(text: $ask).frame(height: 70)
                    .font(.footnote).border(Color.secondary.opacity(0.3))
                HStack {
                    Button(asking ? L10n.t("wdg.ask.working", state.language)
                                  : L10n.t("wdg.ask.go", state.language)) { send() }
                        .disabled(asking || ask.trimmingCharacters(
                            in: .whitespacesAndNewlines).isEmpty)
                    if !talk.isEmpty {
                        Button(L10n.t("wdg.ask.forget", state.language)) {
                            talk = []; did = nil
                        }.font(.footnote)
                    }
                }
                ForEach(Array(talk.enumerated()), id: \.offset) { _, turn in
                    Text(turn["content"] ?? "").font(.footnote)
                        .foregroundColor(turn["role"] == "user" ? .primary
                                                                : .secondary)
                }
                if let did {
                    if let said = did.said {
                        Text(said).font(.footnote).foregroundColor(.secondary)
                    }
                    ForEach(did.acted) { step in
                        Text(step.said ?? "\(step.tool) — \(step.answered ?? 0)")
                            .font(.footnote).foregroundColor(.secondary)
                    }
                }
                Divider()

                if let caps, !caps.available {
                    Text(L10n.t("wdg.nobox", state.language))
                        .font(.footnote).foregroundColor(.secondary)
                }

                Text(L10n.t("wdg.yours", state.language)).font(.headline)
                if widgets.isEmpty {
                    Text(L10n.t("wdg.none", state.language))
                        .font(.footnote).foregroundColor(.secondary)
                }
                ForEach(widgets) { widget in
                    HStack {
                        Button(widget.name) { openOne(widget) }
                        Spacer()
                        Button(L10n.t("wdg.remove", state.language)) {
                            remove(widget)
                        }.font(.footnote)
                    }
                }

                Divider()
                Text(L10n.t("wdg.name", state.language)).font(.footnote)
                TextField("", text: $name).textFieldStyle(.roundedBorder)
                Text(L10n.t("wdg.code", state.language)).font(.footnote)
                TextEditor(text: $source).frame(height: 180)
                    .font(.system(.footnote, design: .monospaced))
                    .border(Color.secondary.opacity(0.3))

                HStack {
                    Button(L10n.t("wdg.save", state.language)) { save() }
                        .disabled(busy || name.isEmpty)
                    Button(L10n.t("wdg.run", state.language)) { run() }
                        .disabled(busy || open == nil || !(caps?.available ?? true))
                }

                Text(L10n.t("wdg.walls", state.language))
                    .font(.footnote).foregroundColor(.secondary)

                if let answer {
                    Divider()
                    Text(L10n.t("wdg.status.\(answer.status)", state.language))
                        .font(.headline)
                    if let said = answer.said {
                        Text(said).font(.footnote).foregroundColor(.secondary)
                    }
                    if let message = answer.message {
                        Text(message).font(.system(.footnote, design: .monospaced))
                    }
                    if let value = answer.value, !value.shown.isEmpty {
                        Text(value.shown)
                            .font(.system(.footnote, design: .monospaced))
                    }
                }
            }.padding(20)
        }
        .task { await load() }
    }

    /// Ask for it in words. Afterwards the list and the open draft are
    /// re-read rather than reasoned about: it may have written, revised or
    /// removed one, and a stale list is the one thing here that can be wrong
    /// without anybody noticing.
    private func send() {
        guard let pid = state.pid, let token = state.token else { return }
        let said = ask.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !said.isEmpty else { return }
        asking = true
        did = nil
        Task {
            defer { asking = false }
            do {
                let turn = try await ApiClient.shared.authoringTurn(
                    profileId: pid, said: said, history: talk, token: token)
                did = turn
                talk.append(["role": "user", "content": said])
                talk.append(["role": "assistant", "content": turn.reply])
                ask = ""
                await load()
                if let open { openOne(open) }
            } catch { self.error = error.localizedDescription }
        }
    }

    private func load() async {
        guard let pid = state.pid, let token = state.token else { return }
        caps = try? await ApiClient.shared.widgetLimits()
        reach = try? await ApiClient.shared.studioAgent()
        do { widgets = try await ApiClient.shared.widgets(profileId: pid, token: token).widgets }
        catch { self.error = error.localizedDescription }
    }

    /// Re-read rather than trusting the list: a list fetched a minute ago
    /// holds a draft from a minute ago, and saving over it is how an edit
    /// made on the desktop disappears.
    private func openOne(_ widget: WidgetRow) {
        open = widget; name = widget.name; source = widget.source; answer = nil
        guard let pid = state.pid, let token = state.token else { return }
        Task {
            if let fresh = try? await ApiClient.shared.widget(profileId: pid,
                                                       widgetId: widget.id,
                                                       token: token) {
                open = fresh; name = fresh.name; source = fresh.source
            }
        }
    }

    private func save() {
        guard let pid = state.pid, let token = state.token else { return }
        busy = true
        Task {
            defer { busy = false }
            do {
                let saved: WidgetRow
                if let open {
                    saved = try await ApiClient.shared.updateWidget(
                        profileId: pid, widgetId: open.id, name: name,
                        source: source, token: token)
                } else {
                    saved = try await ApiClient.shared.createWidget(
                        profileId: pid, name: name, source: source, token: token)
                }
                open = saved
                await load()
            } catch { self.error = error.localizedDescription }
        }
    }

    private func run() {
        guard let pid = state.pid, let token = state.token,
              let open else { return }
        busy = true
        answer = nil
        Task {
            defer { busy = false }
            do {
                answer = try await ApiClient.shared.runWidget(
                    profileId: pid, widgetId: open.id, token: token)
            } catch { self.error = error.localizedDescription }
        }
    }

    private func remove(_ widget: WidgetRow) {
        guard let pid = state.pid, let token = state.token else { return }
        Task {
            do {
                _ = try await ApiClient.shared.deleteWidget(profileId: pid,
                                                     widgetId: widget.id,
                                                     token: token)
                if open?.id == widget.id { open = nil }
                await load()
            } catch { self.error = error.localizedDescription }
        }
    }
}
