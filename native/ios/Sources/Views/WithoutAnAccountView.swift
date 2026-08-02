import SwiftUI

/// The two things this app lets a stranger do, on the one screen a stranger
/// can reach.
///
/// `RootView` renders `WelcomeView` unless `state.isSignedIn`, and everything
/// else lives inside the tab bar behind it. So `openObjection` — wired into
/// `SettingsView` one release ago precisely because a phone is the surface an
/// objector reaches for — sat inside **Manage**, five taps past a profile the
/// objector does not have and should not have to make.
///
/// The route says what it is in its own docstring: *"public: the objecting
/// party need not own an account."* The guard written to check that was
/// satisfied by the call site existing anywhere in the app, which is how a
/// public route ended up behind a private door on all four clients at once.
///
/// Nothing here reads a token, and nothing here is the owner's half: listing
/// objections against your own profile and attesting to them stays in Manage,
/// where the credential is.
struct WithoutAnAccountView: View {
    enum Pane: String, CaseIterable { case object, mark }

    @Environment(\.dismiss) private var dismiss
    @State private var pane: Pane = .object

    /// The reader of this screen has no profile, so there is no profile
    /// language to read. Resolved once here rather than at twenty call sites,
    /// where one of them would eventually be `state.language`.
    private var lang: String { L10n.deviceLanguage }

    // Objecting
    @State private var profileId = ""
    @State private var objectorRef = ""
    @State private var reason = ""
    @State private var opened: ObjectionOpened?
    @State private var timeline: ObjectionTimeline?

    // The mark
    @State private var content = ""
    @State private var found: WatermarkRecovery?

    @State private var busy = false
    @State private var error: String?

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    Picker("", selection: $pane) {
                        Text(L10n.t("pub.object.title", lang)).tag(Pane.object)
                        Text(L10n.t("pub.tab.mark", lang)).tag(Pane.mark)
                    }.pickerStyle(.segmented)

                    if pane == .object { objectPane } else { markPane }

                    if let error {
                        Text(error).font(.footnote).foregroundStyle(Theme.red)
                    }

                    Text(L10n.t("pub.notoken", lang))
                        .font(.caption2).foregroundStyle(Theme.t3)
                }.padding(20)
            }
            .background(Theme.bg.ignoresSafeArea())
            .navigationTitle(L10n.t("pub.sub", lang))
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button(L10n.t("pub.back.short", lang)) { dismiss() }
                }
            }
        }
    }

    // MARK: - objecting

    @ViewBuilder private var objectPane: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(L10n.t("pub.object.title", lang)).font(.headline).foregroundStyle(Theme.txt)
            Text(L10n.t("pub.object.restricts", lang))
                .font(.footnote).foregroundStyle(Theme.t2)

            field(L10n.t("pub.object.profileId", lang), $profileId)
            field(L10n.t("pub.object.ref", lang), $objectorRef)
            field(L10n.t("pub.object.reason", lang), $reason)

            Text(L10n.t("pub.object.ref.note", lang))
                .font(.caption2).foregroundStyle(Theme.t3)

            Button(action: object) {
                HStack {
                    if busy { ProgressView().tint(.white) }
                    Text(L10n.t("pub.object.open", lang)).bold()
                }
                .frame(maxWidth: .infinity).padding(.vertical, 12)
                .background(Theme.brand).foregroundStyle(.white)
                .clipShape(RoundedRectangle(cornerRadius: 12))
            }
            .disabled(busy || profileId.isEmpty || objectorRef.isEmpty)
            .opacity(profileId.isEmpty || objectorRef.isEmpty ? 0.5 : 1)
        }.card()

        if let opened {
            VStack(alignment: .leading, spacing: 6) {
                Text(L10n.fill("pub.object.opened", lang, ["id": opened.id])).font(.headline).foregroundStyle(Theme.txt)
                if let note = opened.note {
                    Text(note).font(.footnote).foregroundStyle(Theme.t2)
                }
                if let status = opened.profile_status {
                    Text(L10n.fill("pub.object.opened.status", lang, [
                        "now": L10n.t("pub.state.\(status)", lang),
                        "before": L10n.t(
                            "pub.state.\(opened.prior_status ?? "active")", lang)]))
                        .font(.footnote).foregroundStyle(Theme.t2)
                }
                Text(L10n.t("pub.object.writeitdown", lang))
                    .font(.caption2).foregroundStyle(Theme.t3)
            }.card()

            // The record of their own case. Until this release the objector
            // could end the profile from this very screen and could not read
            // what had happened to it: `/audit` is owner- or reviewer-gated,
            // and they are neither.
            VStack(alignment: .leading, spacing: 6) {
                Text(L10n.t("obj.timeline.title", lang))
                    .font(.headline).foregroundStyle(Theme.txt)
                if let timeline {
                    Text(timeline.note).font(.caption2).foregroundStyle(Theme.t2)
                    if timeline.events.isEmpty {
                        Text(L10n.t("obj.timeline.empty", lang))
                            .font(.caption2).foregroundStyle(Theme.t3)
                    }
                    ForEach(timeline.events, id: \.id) { e in
                        Text(L10n.t("obj.event.\(e.event)", lang)
                             + " · " + L10n.t("obj.actor.\(e.actor)", lang)
                             + " · " + e.at
                             + (e.sealed
                                ? " · " + L10n.t("obj.timeline.sealed", lang)
                                : ""))
                            .font(.caption2).foregroundStyle(Theme.t2)
                    }
                } else {
                    Button(L10n.t("obj.timeline.go", lang)) {
                        showTimeline(opened.id)
                    }.font(.caption).tint(Theme.brandA).disabled(busy)
                }
            }.card()
        }
    }

    private func showTimeline(_ objectionId: String) {
        busy = true; error = nil
        Task {
            do { timeline = try await ApiClient.shared
                    .objectionTimeline(objectionId: objectionId) }
            catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    // MARK: - the mark

    @ViewBuilder private var markPane: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(L10n.t("pub.mark.title", lang)).font(.headline).foregroundStyle(Theme.txt)
            Text(L10n.t("pub.mark.explain", lang))
                .font(.footnote).foregroundStyle(Theme.t2)

            TextField(L10n.t("pub.mark.paste", lang), text: $content, axis: .vertical)
                .lineLimit(4...10).foregroundStyle(Theme.txt)
                .padding(.horizontal, 12).padding(.vertical, 10)
                .background(Theme.scrBot).clipShape(RoundedRectangle(cornerRadius: 11))
                .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))

            Button(action: recover) {
                HStack {
                    if busy { ProgressView().tint(.white) }
                    Text(L10n.t("pub.mark.ask", lang)).bold()
                }
                .frame(maxWidth: .infinity).padding(.vertical, 12)
                .background(Theme.brand).foregroundStyle(.white)
                .clipShape(RoundedRectangle(cornerRadius: 12))
            }
            .disabled(busy || content.isEmpty)
            .opacity(content.isEmpty ? 0.5 : 1)
        }.card()

        if let found {
            VStack(alignment: .leading, spacing: 6) {
                if found.recovered {
                    Text(L10n.fill("pub.mark.producedby", lang,
                                   ["state": found.state ?? ""]))
                        .font(.headline).foregroundStyle(Theme.txt)
                    Text(L10n.fill("pub.mark.windows", lang, [
                        "matched": "\(found.matched_windows ?? 0)",
                        "stored": "\(found.stored_windows ?? 0)",
                        "examined": "\(found.examined_windows ?? 0)",
                        "similarity": String(format: "%.2f", found.similarity ?? 0)]))
                        .font(.caption2).foregroundStyle(Theme.t3)
                    if found.verbatim == false {
                        Text(L10n.t("pub.mark.altered", lang))
                            .font(.caption2).foregroundStyle(Theme.t3)
                    }
                } else {
                    Text(L10n.t("pub.mark.unknown", lang)).font(.headline).foregroundStyle(Theme.txt)
                    if let reason = found.reason {
                        Text(reason).font(.footnote).foregroundStyle(Theme.t2)
                    }
                    Text(L10n.fill("pub.mark.unknown.explain", lang, ["here": L10n.t("pub.mark.here", lang)]))
                        .font(.caption2).foregroundStyle(Theme.t3)
                }
            }.card()
        }
    }

    // MARK: -

    private func field(_ label: String, _ text: Binding<String>) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(label).font(.caption).foregroundStyle(Theme.t2)
            TextField("", text: text).textFieldStyle(.plain).foregroundStyle(Theme.txt)
                .padding(.horizontal, 12).padding(.vertical, 10)
                .background(Theme.scrBot).clipShape(RoundedRectangle(cornerRadius: 11))
                .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
        }
    }

    private func object() {
        busy = true; error = nil
        Task {
            do {
                opened = try await ApiClient.shared.openObjection(
                    profileId: profileId.trimmingCharacters(in: .whitespaces),
                    objectorRef: objectorRef.trimmingCharacters(in: .whitespaces),
                    reason: reason)
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func recover() {
        busy = true; error = nil; found = nil
        Task {
            do { found = try await ApiClient.shared.recoverWatermark(content: content) }
            catch { self.error = error.localizedDescription }
            busy = false
        }
    }
}
