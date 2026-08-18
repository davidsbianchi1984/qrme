import SwiftUI

/// Somebody's matter, from saying it to seeing what happened to it.
///
/// The support door behind the remit `privileges.swift`'s server-side twin
/// opens with: something wrong with the app, with your profiles, or with the
/// platform.
///
/// Four things this card will not smooth over:
///
/// - **raising takes no token, and the claim is shown once and said to be.**
///   The person whose matter is that they cannot sign in is exactly who an
///   authenticated support door shuts out. What comes back is one string, held
///   in view state and written nowhere — the backend keeps only its hash, and
///   a shell that quietly stored it would undo that.
/// - **`answered` is drawn as a question.** The server refuses to let the help
///   box settle anything; a card that rendered `answered` as a tick would put
///   the closure back that the server took out. It reads *an answer is waiting
///   on you*, with both buttons and neither preselected.
/// - **`offered` is labelled as not being an answer** — when help did not
///   recognise the question it still says something, and that something is a
///   model's sentence or a list of what it covers.
/// - **the standings are the server's closed set**, said here in the reader's
///   language rather than composed. Ten languages of a sentence about
///   `with_a_person` is ten chances to disagree with the backend about what it
///   means.
struct MatterCard: View {
    @EnvironmentObject var state: AppState

    @State private var trouble = ""
    @State private var concerns = "app"
    @State private var raised: Matter?
    @State private var claim = ""
    @State private var mine: [Matter] = []
    @State private var answer = ""
    @State private var reviewer = ""
    @State private var queue: MatterQueue?
    @State private var status: String?

    private var lang: String { state.language }

    /// The server's closed set of standings, said one literal at a time.
    ///
    /// Written out rather than interpolated. Building the key by appending
    /// the standing to a prefix reads fine and is invisible to the guard that
    /// counts English literals behind a translated tab bar — it cannot tell a
    /// composed key from a bare sentence, and reported this file as showing
    /// untranslated English. The guard that checks every key a shell asks for
    /// then reads the prefix as a key of its own. A switch is longer, and it
    /// is the thing both guards can check.
    private func standingLabel(_ standing: String) -> String {
        switch standing {
        case "open": return L10n.t("ns.mtr.st.open", lang)
        case "answered": return L10n.t("ns.mtr.st.answered", lang)
        case "with_a_person": return L10n.t("ns.mtr.st.with_a_person", lang)
        case "settled": return L10n.t("ns.mtr.st.settled", lang)
        default: return standing
        }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(L10n.t("ns.mtr", lang)).font(.headline).foregroundStyle(Theme.txt)
            Text(L10n.t("ns.mtr.lead", lang))
                .font(.caption).foregroundStyle(Theme.t2)

            Picker("", selection: $concerns) {
                Text(L10n.t("ns.mtr.app", lang)).tag("app")
                Text(L10n.t("ns.mtr.profiles", lang)).tag("profiles")
                Text(L10n.t("ns.mtr.platform", lang)).tag("platform")
            }
            .pickerStyle(.segmented)

            TextField("", text: $trouble, axis: .vertical)
                .lineLimit(2...5)
                .textFieldStyle(.roundedBorder)

            Button(L10n.t("ns.mtr.send", lang)) { send() }
                .font(.caption.bold()).foregroundStyle(.white)
                .padding(.horizontal, 12).padding(.vertical, 9)
                .background(Theme.brandA, in: Capsule())
                .disabled(trouble.trimmingCharacters(in: .whitespaces).isEmpty)

            if !claim.isEmpty {
                Text(L10n.t("ns.mtr.claim", lang))
                    .font(.caption2.bold()).foregroundStyle(Theme.amber)
                Text(claim).font(.caption2.monospaced()).foregroundStyle(Theme.txt)
                    .textSelection(.enabled)
            }

            if let matter = raised {
                Text(standingLabel(matter.standing))
                    .font(.caption.bold()).foregroundStyle(Theme.txt)
                if !matter.answer.isEmpty {
                    Text(matter.answer).font(.caption).foregroundStyle(Theme.t2)
                }
                if let offered = matter.offered, !offered.isEmpty {
                    Text(L10n.t("ns.mtr.offered", lang))
                        .font(.caption2).foregroundStyle(Theme.t2)
                    Text(offered).font(.caption2).foregroundStyle(Theme.t2)
                }
                if matter.standing == "answered" {
                    HStack {
                        Button(L10n.t("ns.mtr.wasit", lang)) {
                            settle(matter, helped: true)
                        }.font(.caption)
                        Button(L10n.t("ns.mtr.notit", lang)) { reject(matter) }
                            .font(.caption)
                    }
                }
                if matter.standing != "settled" {
                    TextField("", text: $answer).textFieldStyle(.roundedBorder)
                    Button(L10n.t("ns.mtr.settle", lang)) {
                        settle(matter, helped: false)
                    }
                    .font(.caption)
                    .disabled(answer.trimmingCharacters(in: .whitespaces).isEmpty)
                }
                ForEach(matter.trail, id: \.stepped_at) { step in
                    Text("• \(step.did) — \(step.stepped_at)")
                        .font(.caption2).foregroundStyle(Theme.t2)
                }
            }

            if mine.isEmpty {
                Text(L10n.t("ns.mtr.empty", lang))
                    .font(.caption2).foregroundStyle(Theme.t2)
            }
            ForEach(mine, id: \.id) { matter in
                Text("\(matter.trouble) — \(standingLabel(matter.standing))")
                    .font(.caption2).foregroundStyle(Theme.t2)
            }

            // Whoever answers them. Typed here rather than held in the app's
            // session: the deployment's steward is not whoever is signed in on
            // this phone, and storing it would blur the two.
            SecureField(L10n.t("ns.acc.token.ph", lang), text: $reviewer)
                .textFieldStyle(.roundedBorder)
            if !reviewer.isEmpty {
                Button(L10n.t("ns.mtr.queue", lang)) { loadQueue() }.font(.caption)
            }
            if let waiting = queue?.unsettled {
                ForEach(waiting, id: \.id) { matter in
                    HStack {
                        Text(matter.trouble).font(.caption2).foregroundStyle(Theme.t2)
                        if matter.standing != "with_a_person" {
                            Button(L10n.t("ns.mtr.take", lang)) { take(matter) }
                                .font(.caption2)
                        }
                    }
                }
            }

            if let status { Text(status).font(.caption2).foregroundStyle(Theme.t2) }
        }
        .padding(14)
        .background(Theme.card, in: RoundedRectangle(cornerRadius: 14))
        .task { await refresh() }
    }

    private func refresh() async {
        if let listed = try? await ApiClient.shared.myMatters(token: state.token) {
            mine = listed.my_matters
        }
    }

    private func send() {
        Task {
            do {
                let matter = try await ApiClient.shared.raiseMatter(
                    trouble: trouble, concerns: concerns, token: state.token)
                raised = matter
                claim = matter.claim ?? ""
                trouble = ""
                await refresh()
            } catch { status = error.localizedDescription }
        }
    }

    private func settle(_ matter: Matter, helped: Bool) {
        Task {
            do {
                raised = try await ApiClient.shared.settleMatter(
                    id: matter.id,
                    answer: helped ? matter.answer : answer, helped: helped,
                    token: state.token,
                    claim: claim.isEmpty ? nil : claim)
                answer = ""
                await refresh()
            } catch { status = error.localizedDescription }
        }
    }

    private func reject(_ matter: Matter) {
        Task {
            do {
                raised = try await ApiClient.shared.rejectMatterAnswer(
                    id: matter.id, token: state.token,
                    claim: claim.isEmpty ? nil : claim)
                await refresh()
            } catch { status = error.localizedDescription }
        }
    }

    private func loadQueue() {
        Task {
            do {
                queue = try await ApiClient.shared.matterQueue(reviewerToken: reviewer)
            } catch { status = error.localizedDescription }
        }
    }

    private func take(_ matter: Matter) {
        Task {
            do {
                _ = try await ApiClient.shared.takeMatter(id: matter.id,
                                                   reviewerToken: reviewer)
                _ = try await ApiClient.shared.recordMatterStep(
                    id: matter.id, step: "handed_to_a_person",
                    reviewerToken: reviewer)
                // Read it back through the claim path so the card shows the
                // matter as its raiser will see it, not as the queue does.
                if !claim.isEmpty {
                    raised = try await ApiClient.shared.matter(id: matter.id,
                                                        claim: claim)
                }
                loadQueue()
            } catch { status = error.localizedDescription }
        }
    }
}
