import SwiftUI

/// First-run: name + persona + kind + birthdate -> POST /profiles.
///
/// ## The language of somebody who has not made a profile yet
///
/// `L10n.deviceLanguage` was written one round earlier for
/// `WithoutAnAccountView`, whose reader has no profile to take a language
/// from. This screen has exactly the same reader — the profile does not exist
/// until the button at the bottom is pressed — and the picker in the middle of
/// it is where the profile's language gets chosen in the first place.
///
/// `state.language` is `"en"` until a profile exists, so reading it here would
/// have shown English to every reader on Earth and called it their setting.
struct WelcomeView: View {
    @EnvironmentObject var state: AppState
    private let lang = L10n.deviceLanguage
    @State private var name = ""
    @State private var persona = ""
    @State private var kind = "self"
    @State private var languages: [LanguageInfo] = []
    @State private var language = "en"
    @State private var birthdate = Date(timeIntervalSince1970: 441_763_200) // 1984-01-01
    @State private var busy = false
    @State private var cardJSON = ""
    @State private var error: String?
    /// Not everybody who opens this app wants a profile. Some are here
    /// *because* of one.
    @State private var publicDoor = false

    private let kinds = ["self", "other_person", "fictional"]

    private var iso: String {
        let f = DateFormatter(); f.dateFormat = "yyyy-MM-dd"; return f.string(from: birthdate)
    }

    var body: some View {
        ScrollView {
            VStack(spacing: 22) {
                Circle()
                    .fill(Theme.brand)
                    .frame(width: 84, height: 84)
                    .overlay(Image(systemName: "person.crop.square.badge.plus").font(.system(size: 32)).foregroundStyle(.white))
                    .shadow(color: Theme.brandA.opacity(0.5), radius: 24, y: 8)
                    .padding(.top, 40)

                VStack(spacing: 6) {
                    Text(L10n.t("nw.title", lang)).font(.title2.bold()).foregroundStyle(Theme.txt)
                    Text(L10n.t("nw.sub", lang))
                        .font(.footnote).foregroundStyle(Theme.t2)
                        .multilineTextAlignment(.center)
                }

                VStack(alignment: .leading, spacing: 14) {
                    field(L10n.t("nw.name", lang)) {
                        TextField(L10n.t("nw.name.ph", lang), text: $name).textFieldStyle(.plain).foregroundStyle(Theme.txt)
                    }
                    field(L10n.t("nw.persona", lang)) {
                        TextField(L10n.t("nw.persona.ph", lang), text: $persona, axis: .vertical)
                            .lineLimit(2...4).foregroundStyle(Theme.txt)
                    }
                    field(L10n.t("nw.kind", lang)) {
                        // Was `kind.replacingOccurrences(of: "_", with: " ").capitalized`,
                        // which renders the API's enum member as if it were a
                        // word — "Other Person" is not a label anybody wrote.
                        Picker("", selection: $kind) {
                            ForEach(kinds, id: \.self) { Text(L10n.t(kindKey($0), lang)).tag($0) }
                        }.pickerStyle(.segmented)
                    }
                    field(L10n.t("nw.birthdate", lang)) {
                        DatePicker("", selection: $birthdate, displayedComponents: .date)
                            .labelsHidden().colorScheme(.dark)
                    }
                    field(L10n.t("nw.language", lang)) {
                        // `/languages` returns English in the list with its own
                        // label. Hardcoding it here meant filtering it back out
                        // of the server's answer to avoid showing it twice.
                        Picker("", selection: $language) {
                            ForEach(languages, id: \.code) { l in
                                Text(l.label).tag(l.code)
                            }
                        }.pickerStyle(.menu).tint(Theme.brandA)
                    }
                }.card()

                if let error { Text(error).font(.footnote).foregroundStyle(Theme.red) }

                Button(action: create) {
                    HStack { if busy { ProgressView().tint(.white) }; Text(L10n.t("nw.create", lang)).bold() }
                        .frame(maxWidth: .infinity).padding(.vertical, 14)
                        .background(Theme.brand).foregroundStyle(.white)
                        .clipShape(RoundedRectangle(cornerRadius: 13))
                }
                .disabled(name.isEmpty || persona.isEmpty || busy)
                .opacity(name.isEmpty || persona.isEmpty ? 0.5 : 1)

                // Consent to terms, in the reader's language. A person cannot
                // agree to a sentence they cannot read.
                Text(L10n.t("nw.terms", lang))
                    .font(.caption2).foregroundStyle(Theme.t3)

                // Or carry in a character card: chara_card_v2/v3 JSON. What
                // the platform refuses to carry, the response names.
                VStack(alignment: .leading, spacing: 8) {
                    Text(L10n.t("nw.card", lang))
                        .font(.footnote.bold()).foregroundStyle(Theme.txt)
                    TextField(L10n.t("nw.card.ph", lang), text: $cardJSON,
                              axis: .vertical)
                        .lineLimit(2...4).font(.caption)
                        .textFieldStyle(.roundedBorder)
                    Button(L10n.t("nw.card.import", lang)) { importCard() }
                        .font(.caption.bold()).foregroundStyle(Theme.brandA)
                        .disabled(cardJSON.isEmpty || busy)
                }.card()

                // The other reason somebody opens this app: they have found a
                // synthetic profile of themselves, or they were sent
                // something and want to know whether a person wrote it. Both
                // routes are public on the backend and both were reachable
                // only from inside a signed-in tab bar — which asked the
                // person objecting to a profile to make one first.
                VStack(spacing: 6) {
                    // `pub.invite` and `pub.invite.none` are the accountless
                    // screen's own rows, ported from the console. The door is
                    // the same door; it says the same thing on both sides.
                    Text(L10n.t("pub.invite", lang))
                        .font(.footnote).foregroundStyle(Theme.t2)
                    Button(L10n.t("nw.door", lang)) {
                        publicDoor = true
                    }
                    .font(.footnote.bold()).foregroundStyle(Theme.brandA)
                    Text(L10n.t("pub.invite.none", lang))
                        .font(.caption2).foregroundStyle(Theme.t3)
                }.padding(.top, 4)

                Text(L10n.fill("nov.backend", lang,
                               ["command": "QRME_CORS_ORIGINS=* uvicorn qrme.api:app"]))
                    .font(.system(size: 10, design: .monospaced)).foregroundStyle(Theme.t3)
            }.padding(20)
        }
        .sheet(isPresented: $publicDoor) { WithoutAnAccountView() }
        .task {
            languages = (try? await ApiClient.shared.languages())?.languages ?? []
        }
    }

    /// `self` / `other_person` / `fictional` are the API's members; these are
    /// the words a person reads for them.
    private func kindKey(_ kind: String) -> String {
        kind == "other_person" ? "nw.kind.other" : "nw.kind.\(kind)"
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

    private func importCard() {
        busy = true; error = nil
        Task {
            do {
                let r = try await ApiClient.shared.importCard(
                    cardJSON: cardJSON, birthdate: iso, language: language)
                state.signIn(r)
            } catch { self.error = error.localizedDescription }
            busy = false
        }
    }

    private func create() {
        busy = true; error = nil
        Task {
            do {
                let r = try await ApiClient.shared.createProfile(name: name, persona: persona,
                                                                 kind: kind, birthdate: iso,
                                                                 language: language)
                state.signIn(r)
            } catch {
                self.error = L10n.fill("nw.unreachable", lang,
                                       ["detail": error.localizedDescription])
            }
            busy = false
        }
    }
}
