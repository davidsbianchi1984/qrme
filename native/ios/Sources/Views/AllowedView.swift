import SwiftUI

/// What the agent may do, one row at a time.
///
/// The product grew powers faster than it grew a place to see them: studying
/// the open web, asking strangers, briefing a real professional, running a job
/// over granted material, reaching emergency services. Until this list existed
/// the only way to find out was to meet one mid-conversation.
///
/// Two people read it. The **owner** decides, and is the only one who can
/// change anything. Anyone else reads the same rows to learn what this profile
/// is able to do for them — which is why the rows that are *off* are here too:
/// a roster that hides what nobody chose is a roster you cannot read anything
/// from.
///
/// *What it keeps* sits on every row rather than behind a tap. "Summarise your
/// meetings" and "summarise your meetings, and keep the recording" are
/// different agreements, and only one of them is what the code does.
struct AllowedSection: View {
    @EnvironmentObject var state: AppState
    @State private var rows: [Privilege] = []
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("may.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            Text(L10n.t("may.lead", state.language))
                .font(.caption).foregroundStyle(Theme.t2)
            if state.token == nil {
                Text(L10n.t("may.visitor", state.language))
                    .font(.caption).foregroundStyle(Theme.t2)
            }
            ForEach(rows, id: \.name) { row in
                VStack(alignment: .leading, spacing: 4) {
                    Text(row.may_do).foregroundStyle(Theme.txt)
                    Text(L10n.t("may.keeps", state.language) + " "
                         + (row.holds.isEmpty
                            ? L10n.t("may.keeps.nothing", state.language)
                            : row.holds))
                        .font(.caption).foregroundStyle(Theme.t2)
                    if !row.needs.isEmpty {
                        Text(L10n.t("may.needs", state.language) + " "
                             + row.needs.joined(separator: " · "))
                            .font(.caption).foregroundStyle(Theme.t2)
                    }
                    if row.touches_others {
                        Text(L10n.t("may.others", state.language))
                            .font(.caption).foregroundStyle(Theme.txt)
                    }
                    Text(row.chosen ? L10n.t("may.on", state.language)
                                    : L10n.t("may.off", state.language))
                        .font(.caption).foregroundStyle(Theme.t2)
                    if let token = state.token, let pid = state.pid {
                        Button(row.chosen
                               ? L10n.t("may.turnoff", state.language)
                               : L10n.t("may.turnon", state.language)) {
                            decide(pid, row, !row.chosen, token)
                        }.disabled(busy)
                    }
                }.padding(.vertical, 4)
            }
        }
        .padding(12)
        .background(Theme.card)
        .task { await load() }
    }

    private func load() async {
        guard let pid = state.pid else { return }
        rows = (try? await ApiClient.shared.privileges(
            profile: pid, token: state.token)) ?? []
    }

    /// The whole roster comes back from the press, so the screen is replaced
    /// rather than patched — one row re-read is a screen that agrees with
    /// itself about that row and nothing else.
    private func decide(_ pid: String, _ row: Privilege, _ on: Bool,
                        _ token: String) {
        busy = true
        Task {
            rows = (try? await ApiClient.shared.allowPrivilege(
                profile: pid, name: row.name, on: on, token: token)) ?? rows
            busy = false
        }
    }
}
