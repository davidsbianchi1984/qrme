import SwiftUI

/// The sticker, the queue and the stamp, in the pocket: the beacon a
/// stranger scans on the street, the moderation queue the owner works,
/// the reviews readers trust, the watermark that proves provenance, the
/// media that rides the wall, and the wearables on the wrist.
///
/// The rules these sections render rather than invent:
///
/// * **The overlay never draws the face without the disclosure.** The
///   beacon card carries the watermark line with the name.
/// * **A rated beacon's card sends nothing** to a viewer who has not
///   proven adulthood — the age wall renders without the name or the
///   portrait ever travelling.
/// * **Only the owner moderates,** and a message already resolved says
///   so rather than flipping again.
/// * **A review requires having actually talked to it** — one per
///   interactor, edited rather than stacked.
/// * **The stamp answers to anyone.** Watermark resolution and
///   tamper-checking are public because "who made this" is the
///   reader's question, not the owner's.
/// * **A paired wearable is a screen and a set of buttons** — no
///   sensor stream, no capture, nothing about a microphone.
struct BeaconSection: View {
    @EnvironmentObject var state: AppState
    @State private var beaconId = ""
    @State private var cid = ""
    @State private var line: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("bcn.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            HStack {
                TextField(L10n.t("bcn.id", state.language), text: $beaconId)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("bcn.card", state.language)) {
                    run {
                        let c = try await ApiClient.shared.beaconCard(
                            id: beaconId)
                        line = (c.age_wall ?? false)
                            ? (c.note ?? "18+")
                            : (c.display_name ?? "—") + " · "
                              + (c.watermark ?? "")
                    }
                }.font(.caption).disabled(busy || beaconId.isEmpty)
                Button(L10n.t("bcn.desk", state.language)) {
                    run {
                        let c = try await ApiClient.shared.deskScanCard(
                            id: beaconId)
                        line = c.display_name ?? c.desk_id ?? "—"
                    }
                }.font(.caption).disabled(busy || beaconId.isEmpty)
                Button(L10n.t("bcn.qr", state.language)) {
                    line = ApiClient.shared.beaconQrUrl(id: beaconId)
                        .absoluteString + " · "
                        + ApiClient.shared.beaconScanUrl(id: beaconId)
                            .absoluteString + " · "
                        + ApiClient.shared.deskScanUrl(id: beaconId)
                            .absoluteString
                }.font(.caption).disabled(busy || beaconId.isEmpty)
            }
            HStack {
                TextField(L10n.t("people.add", state.language), text: $cid)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("bcn.social", state.language)) {
                    run {
                        let b = try await ApiClient.shared.socialBeacon(
                            cid: cid)
                        line = (b.platform ?? "—") + " · "
                            + (b.handle ?? "")
                            + " · " + ApiClient.shared.socialQrUrl(cid: cid)
                                .absoluteString
                    }
                }.font(.caption).disabled(busy || cid.isEmpty)
                Button(L10n.t("bcn.pair", state.language)) {
                    run {
                        let pc = try await ApiClient.shared.pairing()
                        line = (pc.console_url ?? "—") + " · "
                            + ApiClient.shared.pairQrUrl().absoluteString
                    }
                }.font(.caption).disabled(busy)
            }
            if let line {
                Text(line).font(.caption2).foregroundStyle(Theme.t2)
            }
        }.card()
    }

    private func run(_ op: @escaping () async throws -> Void) {
        busy = true
        Task {
            do { try await op() }
            catch { line = error.localizedDescription }
            busy = false
        }
    }
}

struct QueueSection: View {
    @EnvironmentObject var state: AppState
    @State private var messageId = ""
    @State private var interactorId = ""
    @State private var content = ""
    @State private var line: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("modq.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            HStack {
                Button(L10n.t("modq.show", state.language)) {
                    run {
                        let q = try await ApiClient.shared.moderationQueue(
                            id: state.pid!, token: state.token!)
                        line = "\(q.count)"
                    }
                }.font(.caption).disabled(busy)
                TextField(L10n.t("modq.msg", state.language),
                          text: $messageId)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("modq.approve", state.language)) {
                    run {
                        let o = try await ApiClient.shared.approveMessage(
                            messageId: messageId, token: state.token!)
                        line = o.status ?? "—"
                    }
                }.font(.caption).disabled(busy || messageId.isEmpty)
                Button(L10n.t("modq.reject", state.language)) {
                    run {
                        let o = try await ApiClient.shared.rejectMessage(
                            messageId: messageId, token: state.token!)
                        line = o.status ?? "—"
                    }
                }.font(.caption).disabled(busy || messageId.isEmpty)
            }
            HStack {
                TextField(L10n.t("people.add", state.language),
                          text: $interactorId)
                    .textFieldStyle(.roundedBorder)
                TextField(L10n.t("modq.edit", state.language),
                          text: $content)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("modq.edit", state.language)) {
                    run {
                        let o = try await ApiClient.shared.editMessage(
                            id: state.pid!, messageId: messageId,
                            interactorId: interactorId, content: content,
                            token: state.token!)
                        line = o.status ?? "—"
                        content = ""
                    }
                }.font(.caption).disabled(busy || messageId.isEmpty
                                          || interactorId.isEmpty
                                          || content.isEmpty)
                Button(L10n.t("modq.retract", state.language)) {
                    run {
                        let o = try await ApiClient.shared.retractMessage(
                            id: state.pid!, messageId: messageId,
                            interactorId: interactorId,
                            token: state.token!)
                        line = o.status ?? "—"
                    }
                }.font(.caption).disabled(busy || messageId.isEmpty
                                          || interactorId.isEmpty)
            }
            if let line {
                Text(line).font(.caption2).foregroundStyle(Theme.t2)
            }
        }.card()
    }

    private func run(_ op: @escaping () async throws -> Void) {
        busy = true
        Task {
            do { try await op() }
            catch { line = error.localizedDescription }
            busy = false
        }
    }
}

struct ReviewSection: View {
    @EnvironmentObject var state: AppState
    @State private var interactorId = ""
    @State private var rating = ""
    @State private var text = ""
    @State private var line: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("revw.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            HStack {
                Button(L10n.t("revw.show", state.language)) {
                    run {
                        let b = try await ApiClient.shared.reviewsOf(
                            id: state.pid!)
                        let avg = b.rating?.average ?? 0
                        line = "\(b.reviews.count) · \(avg)"
                    }
                }.font(.caption).disabled(busy)
                TextField(L10n.t("people.add", state.language),
                          text: $interactorId)
                    .textFieldStyle(.roundedBorder)
                TextField(L10n.t("revw.rating", state.language),
                          text: $rating)
                    .textFieldStyle(.roundedBorder)
            }
            HStack {
                TextField(L10n.t("revw.body", state.language), text: $text)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("revw.leave", state.language)) {
                    run {
                        let o = try await ApiClient.shared.leaveReview(
                            id: state.pid!, interactorId: interactorId,
                            rating: Int(rating) ?? 0, text: text,
                            token: state.token!)
                        line = "\(o.rating ?? 0)"
                        text = ""
                    }
                }.font(.caption).disabled(busy || interactorId.isEmpty
                                          || rating.isEmpty)
            }
            if let line {
                Text(line).font(.caption2).foregroundStyle(Theme.t2)
            }
        }.card()
    }

    private func run(_ op: @escaping () async throws -> Void) {
        busy = true
        Task {
            do { try await op() }
            catch { line = error.localizedDescription }
            busy = false
        }
    }
}

struct StampSection: View {
    @EnvironmentObject var state: AppState
    @State private var wmId = ""
    @State private var content = ""
    @State private var line: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("wm.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            HStack {
                TextField(L10n.t("wm.id", state.language), text: $wmId)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("wm.resolve", state.language)) {
                    run {
                        let c = try await ApiClient.shared
                            .watermarkCredential(id: wmId)
                        line = (c.profile_id ?? "—") + " · "
                            + (c.kind ?? "")
                    }
                }.font(.caption).disabled(busy || wmId.isEmpty)
            }
            HStack {
                TextField(L10n.t("wm.content", state.language),
                          text: $content)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("wm.verify", state.language)) {
                    run {
                        let c = try await ApiClient.shared.verifyWatermark(
                            id: wmId, content: content)
                        let match = c.content_match
                        line = (c.valid ?? false ? "✓" : "✗") + " · "
                            + (match == nil ? "—" : (match! ? "✓" : "✗"))
                    }
                }.font(.caption).disabled(busy || wmId.isEmpty)
            }
            if let line {
                Text(line).font(.caption2).foregroundStyle(Theme.t2)
            }
        }.card()
    }

    private func run(_ op: @escaping () async throws -> Void) {
        busy = true
        Task {
            do { try await op() }
            catch { line = error.localizedDescription }
            busy = false
        }
    }
}

struct MediaSection: View {
    @EnvironmentObject var state: AppState
    @State private var filename = ""
    @State private var line: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("med.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            HStack {
                Button(L10n.t("med.limits", state.language)) {
                    run {
                        let l = try await ApiClient.shared.mediaLimits()
                        line = "image \((l.image?.max_bytes ?? 0) / 1_048_576)MB · "
                            + "video \((l.video?.max_bytes ?? 0) / 1_048_576)MB"
                    }
                }.font(.caption).disabled(busy)
                Button(L10n.t("med.platforms", state.language)) {
                    run {
                        let v = try await ApiClient.shared.videoPlatforms()
                        line = (v.platforms ?? []).joined(separator: " · ")
                    }
                }.font(.caption).disabled(busy)
            }
            HStack {
                TextField(L10n.t("wear.name", state.language),
                          text: $filename)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("med.upload", state.language)) {
                    run {
                        let o = try await ApiClient.shared.uploadMedia(
                            id: state.pid!, filename: filename,
                            data: Data("QRME".utf8), token: state.token!)
                        line = o.kind ?? o.id ?? "—"
                        filename = ""
                    }
                }.font(.caption).disabled(busy || filename.isEmpty)
            }
            if let line {
                Text(line).font(.caption2).foregroundStyle(Theme.t2)
            }
        }.card()
    }

    private func run(_ op: @escaping () async throws -> Void) {
        busy = true
        Task {
            do { try await op() }
            catch { line = error.localizedDescription }
            busy = false
        }
    }
}

struct WearableSection: View {
    @EnvironmentObject var state: AppState
    @State private var name = ""
    @State private var kind = "watch"
    @State private var line: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("wear.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            HStack {
                Button(L10n.t("wear.list", state.language)) {
                    run {
                        let b = try await ApiClient.shared.wearables(
                            id: state.pid!, token: state.token!)
                        line = "\(b.wearables.count) · "
                            + (b.kinds_worn ?? [:]).map { "\($0.key) \($0.value)" }
                                .sorted().joined(separator: " · ")
                    }
                }.font(.caption).disabled(busy)
                TextField(L10n.t("wear.name", state.language), text: $name)
                    .textFieldStyle(.roundedBorder)
                TextField(L10n.t("wear.kind", state.language), text: $kind)
                    .textFieldStyle(.roundedBorder)
            }
            HStack {
                Button(L10n.t("wear.pair", state.language)) {
                    run {
                        let w = try await ApiClient.shared.pairWearable(
                            id: state.pid!, name: name, kind: kind,
                            token: state.token!)
                        line = (w.name ?? "—") + " · " + (w.kind ?? "")
                    }
                }.font(.caption).disabled(busy || name.isEmpty
                                          || kind.isEmpty)
                Button(L10n.t("wear.unpair", state.language)) {
                    run {
                        let w = try await ApiClient.shared.unpairWearable(
                            id: state.pid!, name: name,
                            token: state.token!)
                        line = (w.revoked ?? false) ? "✓" : "—"
                        name = ""
                    }
                }.font(.caption).disabled(busy || name.isEmpty)
            }
            if let line {
                Text(line).font(.caption2).foregroundStyle(Theme.t2)
            }
        }.card()
    }

    private func run(_ op: @escaping () async throws -> Void) {
        busy = true
        Task {
            do { try await op() }
            catch { line = error.localizedDescription }
            busy = false
        }
    }
}
