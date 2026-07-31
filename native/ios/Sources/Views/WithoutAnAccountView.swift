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

    // Objecting
    @State private var profileId = ""
    @State private var objectorRef = ""
    @State private var reason = ""
    @State private var opened: ObjectionOpened?

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
                        Text("A profile depicts me").tag(Pane.object)
                        Text("Is this genuine?").tag(Pane.mark)
                    }.pickerStyle(.segmented)

                    if pane == .object { objectPane } else { markPane }

                    if let error {
                        Text(error).font(.footnote).foregroundStyle(Theme.red)
                    }

                    Text("Nothing on this screen sends a credential. You do not need a profile to use it, and making one is not the price of objecting to one.")
                        .font(.caption2).foregroundStyle(Theme.t3)
                }.padding(20)
            }
            .background(Theme.bg.ignoresSafeArea())
            .navigationTitle("Without an account")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Back") { dismiss() }
                }
            }
        }
    }

    // MARK: - objecting

    @ViewBuilder private var objectPane: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("A profile depicts me").font(.headline).foregroundStyle(Theme.txt)
            Text("Opening an objection restricts the profile straight away — public surfaces off, no new interactors — before anybody reviews it. A dismissal puts it back to exactly what it was.")
                .font(.footnote).foregroundStyle(Theme.t2)

            field("The profile's id", $profileId)
            field("Your proof reference", $objectorRef)
            field("Why — in your own words", $reason)

            Text("The proof reference points at an identity check held outside this system. It is not a login, and it is what lets you object without one.")
                .font(.caption2).foregroundStyle(Theme.t3)

            Button(action: object) {
                HStack {
                    if busy { ProgressView().tint(.white) }
                    Text("Open it").bold()
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
                Text("Opened — \(opened.id)").font(.headline).foregroundStyle(Theme.txt)
                if let note = opened.note {
                    Text(note).font(.footnote).foregroundStyle(Theme.t2)
                }
                if let status = opened.profile_status {
                    Text("The profile is \(status) from this moment.")
                        .font(.footnote).foregroundStyle(Theme.t2)
                }
                Text("Write the id down. It is how you follow this case without an account — there is no inbox here to come back to.")
                    .font(.caption2).foregroundStyle(Theme.t3)
            }.card()
        }
    }

    // MARK: - the mark

    @ViewBuilder private var markPane: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("Somebody sent me this").font(.headline).foregroundStyle(Theme.txt)
            Text("Paste it. This asks whose work it is with no credential id, and keeps answering after the text has been reworded — which is the state text usually arrives in.")
                .font(.footnote).foregroundStyle(Theme.t2)

            TextField("paste the text", text: $content, axis: .vertical)
                .lineLimit(4...10).foregroundStyle(Theme.txt)
                .padding(.horizontal, 12).padding(.vertical, 10)
                .background(Theme.scrBot).clipShape(RoundedRectangle(cornerRadius: 11))
                .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))

            Button(action: recover) {
                HStack {
                    if busy { ProgressView().tint(.white) }
                    Text("Ask who wrote it").bold()
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
                    Text(found.state ?? "recovered").font(.headline)
                        .foregroundStyle(Theme.txt)
                    Text("Produced by a QRME synthetic profile.")
                        .font(.footnote).foregroundStyle(Theme.t2)
                    Text("\(found.matched_windows ?? 0) of \(found.stored_windows ?? 0) stored windows matched, out of \(found.examined_windows ?? 0) examined.")
                        .font(.caption2).foregroundStyle(Theme.t3)
                    if found.verbatim == false {
                        Text("The wording has changed since it was stamped. That does not make it less traceable — it is what the score is measuring.")
                            .font(.caption2).foregroundStyle(Theme.t3)
                    }
                } else {
                    Text("Not recognised").font(.headline).foregroundStyle(Theme.txt)
                    if let reason = found.reason {
                        Text(reason).font(.footnote).foregroundStyle(Theme.t2)
                    }
                    Text("This says nothing about whether a person wrote it. It says no profile on this deployment has stamped work sharing enough wording with it.")
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
