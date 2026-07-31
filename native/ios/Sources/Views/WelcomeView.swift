import SwiftUI

/// First-run: name + persona + kind + birthdate -> POST /profiles.
struct WelcomeView: View {
    @EnvironmentObject var state: AppState
    @State private var name = ""
    @State private var persona = ""
    @State private var kind = "self"
    @State private var languages: [LanguageInfo] = []
    @State private var language = "en"
    @State private var birthdate = Date(timeIntervalSince1970: 441_763_200) // 1984-01-01
    @State private var busy = false
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
                    Text("Create your synthetic profile").font(.title2.bold()).foregroundStyle(Theme.txt)
                    Text("A profile speaks in a voice you define — grounded in a persona, on your terms.")
                        .font(.footnote).foregroundStyle(Theme.t2)
                        .multilineTextAlignment(.center)
                }

                VStack(alignment: .leading, spacing: 14) {
                    field("Display name") {
                        TextField("e.g. Ada", text: $name).textFieldStyle(.plain).foregroundStyle(Theme.txt)
                    }
                    field("Persona") {
                        TextField("Core identity: voice, history, values.", text: $persona, axis: .vertical)
                            .lineLimit(2...4).foregroundStyle(Theme.txt)
                    }
                    field("Kind") {
                        Picker("", selection: $kind) {
                            ForEach(kinds, id: \.self) { Text($0.replacingOccurrences(of: "_", with: " ").capitalized).tag($0) }
                        }.pickerStyle(.segmented)
                    }
                    field("Birthdate") {
                        DatePicker("", selection: $birthdate, displayedComponents: .date)
                            .labelsHidden().colorScheme(.dark)
                    }
                    field("Language") {
                        Picker("", selection: $language) {
                            Text("English").tag("en")
                            ForEach(languages.filter { $0.code != "en" }, id: \.code) { l in
                                Text(l.label).tag(l.code)
                            }
                        }.pickerStyle(.menu).tint(Theme.brandA)
                    }
                }.card()

                if let error { Text(error).font(.footnote).foregroundStyle(Theme.red) }

                Button(action: create) {
                    HStack { if busy { ProgressView().tint(.white) }; Text("Create profile").bold() }
                        .frame(maxWidth: .infinity).padding(.vertical, 14)
                        .background(Theme.brand).foregroundStyle(.white)
                        .clipShape(RoundedRectangle(cornerRadius: 13))
                }
                .disabled(name.isEmpty || persona.isEmpty || busy)
                .opacity(name.isEmpty || persona.isEmpty ? 0.5 : 1)

                Text("By creating a profile you agree to the Terms of Service — profiles are AI-generated synthetic content, never professional advice; you assume the risks of AI interactions. Full terms: GET /terms · docs/terms.md")
                    .font(.caption2).foregroundStyle(Theme.t3)

                // The other reason somebody opens this app: they have found a
                // synthetic profile of themselves, or they were sent
                // something and want to know whether a person wrote it. Both
                // routes are public on the backend and both were reachable
                // only from inside a signed-in tab bar — which asked the
                // person objecting to a profile to make one first.
                VStack(spacing: 6) {
                    Text("Here about a profile, not for one?")
                        .font(.footnote).foregroundStyle(Theme.t2)
                    Button("A profile depicts me · Is this genuine?") {
                        publicDoor = true
                    }
                    .font(.footnote.bold()).foregroundStyle(Theme.brandA)
                    Text("Neither needs an account.")
                        .font(.caption2).foregroundStyle(Theme.t3)
                }.padding(.top, 4)

                Text("Start the backend:  QRME_CORS_ORIGINS=* uvicorn qrme.api:app")
                    .font(.system(size: 10, design: .monospaced)).foregroundStyle(Theme.t3)
            }.padding(20)
        }
        .sheet(isPresented: $publicDoor) { WithoutAnAccountView() }
        .task {
            languages = (try? await ApiClient.shared.languages())?.languages ?? []
        }
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

    private func create() {
        busy = true; error = nil
        Task {
            do {
                let r = try await ApiClient.shared.createProfile(name: name, persona: persona,
                                                                 kind: kind, birthdate: iso,
                                                                 language: language)
                state.signIn(r)
            } catch {
                self.error = "Couldn't reach QRME — is the backend running? (\(error.localizedDescription))"
            }
            busy = false
        }
    }
}
