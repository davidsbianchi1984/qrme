import SwiftUI

/// A live desk: an actual person offering a service, waiting behind a camera
/// view of their own counter.
///
/// The screen is deliberately the mirror image of `BeaconScannerView`. There,
/// a synthetic profile appears and the AI mark is drawn from the same payload
/// as the face, so the two cannot come apart. Here there is **no mark at all**,
/// because stamping "AI" on a real person is not a cautious default — it tells
/// the visitor the human they are waiting for does not exist.
///
/// Absence of a badge would be ambiguous on its own, so the claim is made
/// positively: *a person, not AI*, with the attestation behind it visible
/// rather than filed in a policy somewhere. Who vouched is the whole question.
///
/// And when the chair is empty, there is a bell. The sign taped to the chair
/// says to ring it; this is that bell, on the screen the visitor is already
/// looking at.
struct DeskView: View {
    let deskId: String
    var callerId: String? = nil
    /// The viewer's interactor token. An 18+ stream checks its verified
    /// birthdate server-side, so without one the card is an age wall.
    var viewerToken: String? = nil

    @State private var card: DeskCard?
    @State private var joined: StreamJoin?
    @State private var receipt: RingReceipt?
    @State private var note = ""
    @State private var error: String?
    @State private var ringing = false
    @State private var base = ""

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                if card?.age_wall == true {
                    ageWall
                } else {
                    deskView
                    header
                    stream
                    bell
                    attestation
                }
                if let error {
                    Text(error).font(.footnote).foregroundStyle(.red)
                }
            }
            .padding(20)
        }
        .navigationTitle(card?.display_name ?? "Desk")
        .task { await load() }
    }

    // MARK: the age wall

    /// What an unverified viewer of an 18+ stream sees. Existence and nothing
    /// else — no name, no view, and no location, because where a performer
    /// physically is has nothing to do with watching them.
    @ViewBuilder private var ageWall: some View {
        VStack(alignment: .leading, spacing: 10) {
            Image(systemName: "18.circle.fill")
                .font(.system(size: 44)).foregroundStyle(.orange)
            Text("18+ only").font(.title3.weight(.bold))
            Text(card?.note ?? "")
                .font(.footnote).foregroundStyle(.secondary)
            // Still true here, and worth saying: there is a person behind
            // this, so it never carries the AI mark.
            Label("A live person — not AI", systemImage: "person.fill")
                .font(.caption).foregroundStyle(.secondary)
        }
    }

    // MARK: the view of the desk

    @ViewBuilder private var deskView: some View {
        ZStack(alignment: .bottomLeading) {
            if let card, let feed = card.feed,
               let url = URL(string: base + feed.url) {
                AsyncImage(url: url) { image in
                    image.resizable().scaledToFill()
                } placeholder: {
                    Rectangle().fill(Color(red: 0.07, green: 0.06, blue: 0.16))
                }
            } else {
                Rectangle().fill(Color(red: 0.07, green: 0.06, blue: 0.16))
            }

            if let feed = card?.feed {
                // Never a watermark here. The one label this image carries
                // says whether it is live — which is the thing a person
                // staring at an empty chair actually needs to know.
                Text(feed.live ? "● LIVE" : "SAMPLE VIEW")
                    .font(.caption2.weight(.bold))
                    .foregroundStyle(feed.live ? .red : .white.opacity(0.8))
                    .padding(.horizontal, 8).padding(.vertical, 4)
                    .background(.black.opacity(0.6), in: Capsule())
                    .padding(10)
            }
        }
        .aspectRatio(4.0 / 3.0, contentMode: .fit)
        .clipShape(RoundedRectangle(cornerRadius: 16))

        if let feed = card?.feed, !feed.live {
            Text(feed.note).font(.caption2).foregroundStyle(.secondary)
        }
    }

    // MARK: who this is

    @ViewBuilder private var header: some View {
        if let card {
            VStack(alignment: .leading, spacing: 6) {
                Text(card.display_name ?? "").font(.title3.weight(.bold))
                Text((card.trade ?? "") + (card.location.map { " · \($0)" } ?? ""))
                    .font(.subheadline).foregroundStyle(.secondary)

                // The positive claim, in place of the mark a synthetic
                // profile would carry here.
                Label(card.designation ?? "", systemImage: "person.fill.checkmark")
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(.green)

                Text(presenceLine(card.presence ?? "away"))
                    .font(.subheadline)
                    .foregroundStyle(card.presence == "attended" ? .green : .orange)
                if let blurb = card.blurb {
                    Text(blurb).font(.footnote).foregroundStyle(.secondary)
                }
            }
        }
    }

    private func presenceLine(_ presence: String) -> String {
        switch presence {
        case "attended": return "At the desk"
        case "closed": return "Closed — not taking callers"
        default: return "Away from the desk"
        }
    }

    // MARK: joining the stream

    @ViewBuilder private var stream: some View {
        if card != nil {
            VStack(alignment: .leading, spacing: 8) {
                Button {
                    Task { await joinStream() }
                } label: {
                    HStack(spacing: 10) {
                        Image(systemName: "video.fill")
                        Text(joined == nil ? "Join the live stream" : "Joined")
                            .font(.headline)
                    }
                    .frame(maxWidth: .infinity).padding(14)
                    .background(Color.secondary.opacity(0.18))
                    .clipShape(RoundedRectangle(cornerRadius: 14))
                }
                if let joined {
                    Text(joined.note).font(.footnote).foregroundStyle(.secondary)
                    Text("Room \(joined.room_id)")
                        .font(.caption2.monospaced()).foregroundStyle(.secondary)
                }
            }
        }
    }

    // MARK: the bell

    @ViewBuilder private var bell: some View {
        if let card, card.bell?.available == true {
            VStack(alignment: .leading, spacing: 10) {
                TextField("Anything they should know? (optional)", text: $note)
                    .textFieldStyle(.roundedBorder)

                Button {
                    Task { await ring() }
                } label: {
                    HStack(spacing: 10) {
                        Image(systemName: "bell.fill")
                        Text(ringing ? "Ringing…" : "Ring the bell")
                            .font(.headline)
                    }
                    .frame(maxWidth: .infinity).padding(14)
                    .background(Theme.brand)
                    .clipShape(RoundedRectangle(cornerRadius: 14))
                    .foregroundStyle(.white)
                }
                .disabled(ringing)

                if let receipt {
                    Label(receipt.note, systemImage: "checkmark.circle.fill")
                        .font(.footnote).foregroundStyle(.green)
                } else if let waiting = card.bell?.waiting, waiting > 0 {
                    Text("\(waiting) waiting")
                        .font(.caption).foregroundStyle(.secondary)
                }
            }
        } else if card != nil {
            Text("The bell is off while this desk is closed.")
                .font(.footnote).foregroundStyle(.secondary)
        }
    }

    // MARK: who says they are a person

    @ViewBuilder private var attestation: some View {
        if let card {
            if let att = card.attestation {
            VStack(alignment: .leading, spacing: 4) {
                Text("Attested by \(att.attestor)")
                    .font(.caption.weight(.semibold))
                Text(att.basis)
                    .font(.caption2).foregroundStyle(.secondary)
                if att.signed {
                    Label("Signed", systemImage: "checkmark.seal.fill")
                        .font(.caption2).foregroundStyle(.green)
                }
                // Shipped with the claim, always. "Recorded" and "proven" are
                // different words and the difference is the whole point.
                Text(att.note)
                    .font(.caption2).foregroundStyle(.secondary)
            }
            .padding(12)
            .background(Color.secondary.opacity(0.12),
                        in: RoundedRectangle(cornerRadius: 12))
            }
        }
    }

    // MARK: actions

    private func load() async {
        base = await ApiClient.shared.base.absoluteString
        if base.hasSuffix("/") { base = String(base.dropLast()) }
        do { card = try await ApiClient.shared.desk(deskId, token: viewerToken) }
        catch { self.error = error.localizedDescription }
    }

    private func joinStream() async {
        do {
            joined = try await ApiClient.shared.joinStream(
                deskId: deskId, token: viewerToken)
        } catch {
            self.error = error.localizedDescription
        }
    }

    private func ring() async {
        ringing = true; error = nil
        defer { ringing = false }
        do {
            receipt = try await ApiClient.shared.ringBell(
                deskId: deskId, callerId: callerId,
                note: note.isEmpty ? nil : note, token: viewerToken)
            card = try? await ApiClient.shared.desk(deskId, token: viewerToken)
        } catch {
            self.error = error.localizedDescription
        }
    }
}
