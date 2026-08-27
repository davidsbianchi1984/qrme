import Contacts
import SwiftUI

/// The people in your phone (qrme/contacts.py) — the shell's own road.
///
/// The console carries this with the Web Contact Picker where a browser
/// offers one, and says honestly that most do not. A phone is where the
/// contacts actually live, which is why these three doors sat in this
/// shell's doorless backlog from the day they opened: granted, synced,
/// read back, withdrawn, on the interactor's own token.
///
/// Three facts the section keeps on its face, the same three the console
/// states: the sync REPLACES the book (it is the phone's current truth,
/// not an accretion), names stay while numbers never come back out, and
/// withdrawing the grant drops the book server-side — the switch is the
/// withdrawal, not a pause.
struct ContactsBookSection: View {
    @EnvironmentObject var state: AppState
    @State private var book: [ApiClient.ContactRow] = []
    @State private var held = 0
    @State private var granted = false
    @State private var note: String?
    @State private var busy = false

    var body: some View {
        if let iam = state.interactorId, let token = state.interactorToken {
            VStack(alignment: .leading, spacing: 10) {
                Text(L10n.t("book.title", state.language))
                    .font(.headline).foregroundStyle(Theme.txt)
                Text(L10n.t("book.lead", state.language))
                    .font(.footnote).foregroundStyle(Theme.t2)
                Button {
                    Task { await sync(iam: iam, token: token) }
                } label: {
                    Text(busy ? "…" : L10n.t("book.sync", state.language))
                }
                .disabled(busy)
                if held > 0 {
                    Text(L10n.t("book.held", state.language)
                        .replacingOccurrences(of: "{n}", with: String(held)))
                        .font(.footnote).foregroundStyle(Theme.t2)
                    ForEach(book.prefix(30), id: \.id) { row in
                        HStack {
                            Text(row.name).font(.subheadline)
                                .foregroundStyle(Theme.txt)
                            if row.holds_account {
                                Text(L10n.t("book.account", state.language))
                                    .font(.caption2).foregroundStyle(Theme.brandA)
                            }
                            Spacer()
                        }
                    }
                    Button(role: .destructive) {
                        Task { await withdraw(iam: iam, token: token) }
                    } label: {
                        Text(L10n.t("book.withdraw", state.language))
                    }
                    .disabled(busy)
                }
                if let note {
                    Text(note).font(.footnote).foregroundStyle(Theme.t2)
                }
            }
            .task { await load(iam: iam, token: token) }
        }
    }

    private func load(iam: String, token: String) async {
        guard let got = try? await ApiClient.shared.contactsBook(
            interactorId: iam, token: token) else { return }
        book = got.book
        held = got.held
        granted = got.held > 0
    }

    /// The whole ceremony on one press: the grant (its own door, so the
    /// decision is on the record before any name moves), then the device's
    /// contacts — name and first number only — replacing the book.
    private func sync(iam: String, token: String) async {
        busy = true
        defer { busy = false }
        note = nil
        let store = CNContactStore()
        let allowed = (try? await store.requestAccess(for: .contacts)) ?? false
        guard allowed else {
            // The permission is the person's to refuse, and the refusal is
            // said rather than swallowed — with where the switch lives.
            note = L10n.t("book.denied", state.language)
            return
        }
        var entries: [[String: String]] = []
        let keys = [CNContactGivenNameKey, CNContactFamilyNameKey,
                    CNContactPhoneNumbersKey] as [CNKeyDescriptor]
        let ask = CNContactFetchRequest(keysToFetch: keys)
        try? store.enumerateContacts(with: ask) { person, _ in
            let name = [person.givenName, person.familyName]
                .filter { !$0.isEmpty }.joined(separator: " ")
            guard let number = person.phoneNumbers.first?.value.stringValue,
                  !name.isEmpty else { return }
            entries.append(["name": name, "number": number])
        }
        do {
            _ = try await ApiClient.shared.decideContacts(
                interactorId: iam, consented: true, token: token)
            _ = try await ApiClient.shared.syncContacts(
                interactorId: iam, entries: entries, token: token)
            granted = true
            await load(iam: iam, token: token)
        } catch {
            note = error.localizedDescription
        }
    }

    private func withdraw(iam: String, token: String) async {
        busy = true
        defer { busy = false }
        do {
            _ = try await ApiClient.shared.decideContacts(
                interactorId: iam, consented: false, token: token)
            book = []
            held = 0
            granted = false
        } catch {
            note = error.localizedDescription
        }
    }
}
