import AVFoundation
import SwiftUI

/// Voice enrollment, walked in the order FIG. 800 gates it: permission (802),
/// then collection (806/808), then the characteristics (810), then the print
/// (812) and what speaking with it always carries.
///
/// The phone is where this feature belongs — it is the device with the
/// microphone in it. So unlike the web console, which asks the owner to type
/// how many seconds they gathered, this screen records the sample itself and
/// measures it. What travels to the backend is still only the measurement:
/// the recording stays in this app's container and the profile database is
/// told its name, never its bytes.
struct VoiceView: View {
    @EnvironmentObject var state: AppState
    let profileId: String
    let token: String

    @StateObject private var recorder = VoiceRecorder()
    @State private var status: VoiceprintStatus?
    @State private var say = ""
    @State private var spoken: VoiceSpoken?
    @State private var revocation: VoiceRevocation?
    @State private var error: String?
    @State private var busy = false
    // The spoken voice: a reference to a voice made on the engine's own
    // surface — a different thing from the voiceprint above, which is why it
    // does not sit behind the enrollment consent.
    @State private var binding: ApiClient.SpokenBinding?
    @State private var bindId = ""
    @State private var bindLabel = ""
    @State private var sayLine = ""
    @State private var player: AVAudioPlayer?

    private var consented: Bool { status?.consent.granted == true }

    /// Built up in steps rather than one interpolation: chaining `.map` off an
    /// optional inside an optional-chained expression is easy to get subtly
    /// wrong, and this reads as what it is.
    private var grantLine: String {
        let sources = status?.consent.sources ?? []
        var line = L10n.fill("nvoi.granted", state.language,
                             ["sources": sources.joined(separator: ", ")])
        if let at = status?.consent.granted_at, at.count >= 10 {
            line += " · " + String(at.prefix(10))
        }
        return line
    }

    private var builtLine: String {
        guard let p = status?.voiceprint else { return "" }
        let day = p.built_at.map { String($0.prefix(10)) } ?? "—"
        return L10n.fill("nvoi.built", state.language, ["date": day]) + " · \(p.id)"
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                permission
                if consented {
                    enrollment
                    voiceprint
                }
                spokenVoice
                invariants
                if let error {
                    Text(error).font(.footnote).foregroundStyle(Theme.red)
                }
            }
            .padding(20)
        }
        .task { await load() }
        // Walking away mid-recording must not leave the microphone open.
        .onDisappear { recorder.discard() }
    }

    // MARK: 802 — the permission, before anything is collected

    private var permission: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(L10n.t("nvoi.step1", state.language)).font(.headline).foregroundStyle(Theme.txt)
            if consented {
                Text(grantLine).font(.caption).foregroundStyle(Theme.t2)
                Button(L10n.t("nvoi.withdraw", state.language)) {
                    act { revocation = try await ApiClient.shared
                        .revokeVoiceprint(id: profileId, token: token) }
                }
                .font(.caption.bold()).foregroundStyle(.white)
                .padding(.horizontal, 12).padding(.vertical, 9)
                .background(Theme.red).clipShape(Capsule())
                .disabled(busy)
                if let revocation {
                    Text(L10n.fill("nvoi.deleted", state.language,
                                   ["n": "\(revocation.samples_deleted)",
                                    "note": revocation.note]))
                        .font(.caption2).foregroundStyle(Theme.amber)
                }
            } else {
                Text(L10n.t("nvoi.nothing", state.language))
                    .font(.caption).foregroundStyle(Theme.t2)
                Button(L10n.t("nvoi.attest", state.language)) {
                    act {
                        status = try await ApiClient.shared.grantVoiceConsent(
                            id: profileId, token: token,
                            sources: ["call", "voice_note", "direct"])
                    }
                }
                .font(.caption.bold()).foregroundStyle(.white)
                .padding(.horizontal, 12).padding(.vertical, 9)
                .background(Theme.brandA).clipShape(Capsule())
                .disabled(busy)
            }
        }
        .card()
    }

    // MARK: 806/808/810 — samples, and what they amount to

    private var enrollment: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(L10n.t("nvoi.step2", state.language)).font(.headline).foregroundStyle(Theme.txt)
            Text(L10n.t("nvoi.tap", state.language))
                .font(.caption).foregroundStyle(Theme.t2)

            HStack(spacing: 12) {
                Button(L10n.t(recorder.recording ? "nvoi.stop" : "nvoi.sample", state.language)) {
                    if recorder.recording { finishRecording() } else { startRecording() }
                }
                .font(.caption.bold()).foregroundStyle(.white)
                .padding(.horizontal, 14).padding(.vertical, 10)
                .background(recorder.recording ? Theme.red : Theme.brandA)
                .clipShape(Capsule())
                .disabled(busy)

                if recorder.recording {
                    Text(String(format: "%.0fs", recorder.elapsed))
                        .font(.subheadline.bold()).monospacedDigit()
                        .foregroundStyle(Theme.green)
                }
            }

            if let e = status?.enrollment {
                HStack(alignment: .top) {
                    VStack(alignment: .leading, spacing: 2) {
                        Text(L10n.fill("nvoi.samples", state.language,
                              ["n": "\(e.samples)",
                               "secs": String(format: "%.1fs", e.seconds)]))
                            .font(.subheadline.bold()).foregroundStyle(Theme.txt)
                        Text(turnLine(e) + " · needs \(e.ready_when.samples) samples and "
                             + "\(String(format: "%.0f", e.ready_when.seconds))s")
                            .font(.caption2).foregroundStyle(Theme.t3)
                    }
                    Spacer()
                    Text(L10n.t(e.ready ? "nvoi.ready" : "nvoi.notyet", state.language))
                        .font(.caption2.bold())
                        .foregroundStyle(e.ready ? Theme.green : Theme.amber)
                }
                if !e.ready, !e.needs.isEmpty {
                    Text(L10n.fill("nvoi.needs", state.language,
                              ["needs": e.needs.joined(separator: ", ")]))
                        .font(.caption2).foregroundStyle(Theme.t2)
                }
                Text(e.method).font(.caption2).foregroundStyle(Theme.t3)
            }

            Text(L10n.t("nvoi.stays", state.language))
                .font(.caption2).foregroundStyle(Theme.t3)
        }
        .card()
    }

    // MARK: 812 — the print, and speaking with it

    private var voiceprint: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(L10n.t("nvoi.step3", state.language)).font(.headline).foregroundStyle(Theme.txt)
            if let p = status?.voiceprint, p.active {
                Text(builtLine).font(.caption2).foregroundStyle(Theme.t3)
                TextField(L10n.t("nvoi.say", state.language), text: $say, axis: .vertical)
                    .lineLimit(2...4)
                    .font(.subheadline).foregroundStyle(Theme.txt)
                    .padding(10)
                    .background(Theme.scrBot)
                    .clipShape(RoundedRectangle(cornerRadius: 10))
                Button(L10n.t("nvoi.speak", state.language)) {
                    act {
                        spoken = try await ApiClient.shared.speakInVoice(
                            id: profileId, token: token, text: say)
                    }
                }
                .font(.caption.bold()).foregroundStyle(.white)
                .padding(.horizontal, 12).padding(.vertical, 9)
                .background(Theme.brandA).clipShape(Capsule())
                .disabled(busy || say.trimmingCharacters(in: .whitespaces).isEmpty)
                if let spoken {
                    VStack(alignment: .leading, spacing: 4) {
                        Text(spoken.basis).font(.caption2).foregroundStyle(Theme.t2)
                        Text(spoken.disclosure).font(.caption)
                            .foregroundStyle(Theme.amber)
                    }
                }
            } else {
                Text(status?.enrollment?.ready == true
                     ? L10n.t("nvoi.enough", state.language)
                     : L10n.t("nvoi.more", state.language))
                    .font(.caption).foregroundStyle(Theme.t2)
                Button(L10n.t("nvoi.build", state.language)) {
                    act {
                        status = try await ApiClient.shared
                            .buildVoiceprint(id: profileId, token: token)
                    }
                }
                .font(.caption.bold()).foregroundStyle(.white)
                .padding(.horizontal, 12).padding(.vertical, 9)
                .background(Theme.brandA).clipShape(Capsule())
                .disabled(busy || status?.enrollment?.ready != true)
                if let p = status?.voiceprint, !p.active {
                    Text(L10n.t("nvoi.retired", state.language))
                        .font(.caption2).foregroundStyle(Theme.t3)
                }
            }
        }
        .card()
    }

    // MARK: the spoken voice — the binding, and a line said aloud

    private var spokenVoice: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(L10n.t("nsv.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            Text(L10n.t("nsv.lead", state.language))
                .font(.caption2).foregroundStyle(Theme.t2)
            if let b = binding, b.speaks {
                Text(L10n.t("nsv.bound", state.language) + " "
                     + (b.label.isEmpty ? b.voice_id : b.label))
                    .font(.caption).foregroundStyle(Theme.txt)
                TextField(L10n.t("nsv.test", state.language), text: $sayLine)
                    .font(.subheadline).foregroundStyle(Theme.txt)
                    .padding(10).background(Theme.scrBot)
                    .clipShape(RoundedRectangle(cornerRadius: 10))
                HStack(spacing: 8) {
                    Button(L10n.t("nsv.test", state.language)) {
                        act {
                            let audio = try await ApiClient.shared.saySpoken(
                                id: profileId, token: token, text: sayLine)
                            player = try AVAudioPlayer(data: audio)
                            player?.play()
                        }
                    }
                    .font(.caption.bold()).foregroundStyle(.white)
                    .padding(.horizontal, 12).padding(.vertical, 9)
                    .background(Theme.brandA).clipShape(Capsule())
                    .disabled(busy || sayLine.trimmingCharacters(in: .whitespaces).isEmpty)
                    Button(L10n.t("nsv.unbind", state.language)) {
                        act {
                            binding = try await ApiClient.shared.bindSpokenVoice(
                                id: profileId, token: token, voiceId: "", label: "")
                        }
                    }
                    .font(.caption).foregroundStyle(Theme.t2)
                    .disabled(busy)
                }
            } else {
                TextField(L10n.t("nsv.id.ph", state.language), text: $bindId)
                    .font(.subheadline).foregroundStyle(Theme.txt)
                    .padding(10).background(Theme.scrBot)
                    .clipShape(RoundedRectangle(cornerRadius: 10))
                TextField(L10n.t("nsv.label.ph", state.language), text: $bindLabel)
                    .font(.subheadline).foregroundStyle(Theme.txt)
                    .padding(10).background(Theme.scrBot)
                    .clipShape(RoundedRectangle(cornerRadius: 10))
                Button(L10n.t("nsv.save", state.language)) {
                    act {
                        binding = try await ApiClient.shared.bindSpokenVoice(
                            id: profileId, token: token,
                            voiceId: bindId, label: bindLabel)
                    }
                }
                .font(.caption.bold()).foregroundStyle(.white)
                .padding(.horizontal, 12).padding(.vertical, 9)
                .background(Theme.brandA).clipShape(Capsule())
                .disabled(busy || bindId.trimmingCharacters(in: .whitespaces).isEmpty)
            }
        }
        .card()
    }

    private var invariants: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(L10n.t("nvoi.holds", state.language)).font(.headline).foregroundStyle(Theme.txt)
            // The bullet lives in the row rather than being prepended here:
            // an RTL reader gets it on the correct side that way. Android's
            // copy of this block has carried that note since it was written;
            // this shell prepended "· " and said all three lines in English.
            ForEach(["nvoi.holds.mark", "nvoi.holds.own", "nvoi.holds.withdraw"],
                    id: \.self) { key in
                Text(L10n.t(key, state.language))
                    .font(.caption2).foregroundStyle(Theme.t2)
            }
            if let d = status?.disclosure {
                Text(d).font(.caption2).foregroundStyle(Theme.t3)
            }
        }
        .card()
    }

    // MARK: recording

    private func startRecording() {
        error = nil
        recorder.requestPermission { ok in
            guard ok else {
                error = "Microphone access is off for QRME — turn it on in "
                      + "Settings to enroll a voice."
                return
            }
            error = recorder.start()
        }
    }

    /// Stop, then post what the recording measured. `turns` is the number of
    /// spoken stretches the recorder counted between silences — the same
    /// quantity the backend averages into `mean_turn_seconds`.
    private func finishRecording() {
        guard let sample = recorder.stop() else { return }
        act {
            _ = try await ApiClient.shared.addVoiceSample(
                id: profileId, token: token, source: "direct",
                seconds: sample.seconds, turns: sample.turns,
                reference: sample.reference)
        }
    }

    private func turnLine(_ e: VoiceEnrollment) -> String {
        guard let mean = e.mean_turn_seconds else { return "no turns counted yet" }
        return "about \(String(format: "%.1f", mean))s a turn"
    }

    // MARK: plumbing

    private func load() async {
        do { status = try await ApiClient.shared.voiceprint(id: profileId, token: token) }
        catch { self.error = error.localizedDescription }
        // The binding reads the same for bound and not, so a failure here is
        // a failure worth showing, not an empty state to paper over.
        do { binding = try await ApiClient.shared.spokenVoice(id: profileId) }
        catch { self.error = error.localizedDescription }
    }

    /// Run a call, then re-read the status so the counts on screen are the
    /// backend's rather than a guess made locally.
    private func act(_ work: @escaping () async throws -> Void) {
        busy = true
        error = nil
        Task {
            do { try await work(); await load() }
            catch { self.error = error.localizedDescription }
            busy = false
        }
    }
}

/// Records to the app's container and reports how long it ran and how many
/// spoken stretches it heard. It never hands the audio anywhere — the file is
/// left on disk for the deployment's media policy to collect, which is what
/// the backend's `reference` field names.
final class VoiceRecorder: ObservableObject {
    struct Sample { let seconds: Double; let turns: Int; let reference: String }

    @Published private(set) var recording = false
    @Published private(set) var elapsed: Double = 0

    private var recorder: AVAudioRecorder?
    private var timer: Timer?
    private var turns = 0
    private var speaking = false

    /// Anything above this on the recorder's dB meter counts as speech rather
    /// than room noise. -35 dBFS sits comfortably between the two indoors.
    private let speechFloor: Float = -35

    /// Ask for the microphone unless the answer is already known. `then` runs
    /// on the main queue with the verdict.
    func requestPermission(_ then: @escaping (Bool) -> Void) {
        let session = AVAudioSession.sharedInstance()
        switch session.recordPermission {
        case .granted: then(true)
        case .denied: then(false)
        default:
            session.requestRecordPermission { ok in
                DispatchQueue.main.async { then(ok) }
            }
        }
    }

    /// Returns nil on success, or a message the screen can show.
    func start() -> String? {
        do {
            let session = AVAudioSession.sharedInstance()
            try session.setCategory(.record, mode: .default)
            try session.setActive(true)

            let url = FileManager.default.temporaryDirectory
                .appendingPathComponent("voice-\(Int(Date().timeIntervalSince1970)).m4a")
            let rec = try AVAudioRecorder(url: url, settings: [
                AVFormatIDKey: Int(kAudioFormatMPEG4AAC),
                AVSampleRateKey: 44_100,
                AVNumberOfChannelsKey: 1,
            ])
            rec.isMeteringEnabled = true
            rec.record()
            recorder = rec
            recording = true
            elapsed = 0
            turns = 0
            speaking = false
            timer = Timer.scheduledTimer(withTimeInterval: 0.25, repeats: true) {
                [weak self] _ in self?.tick()
            }
            return nil
        } catch {
            release()
            return "Could not open the microphone: \(error.localizedDescription)"
        }
    }

    func stop() -> Sample? {
        guard let rec = recorder else { return nil }
        let seconds = rec.currentTime
        let reference = rec.url.lastPathComponent
        release()
        guard seconds > 0 else { return nil }
        return Sample(seconds: (seconds * 10).rounded() / 10,
                      turns: max(1, turns), reference: reference)
    }

    /// Abandon an in-flight recording. Leaving the microphone open is a worse
    /// outcome than losing the sample, so this is safe to call from teardown.
    func discard() { release() }

    private func tick() {
        guard let rec = recorder else { return }
        rec.updateMeters()
        elapsed = rec.currentTime
        let loud = rec.averagePower(forChannel: 0) > speechFloor
        // A turn is a stretch of speech, so count the rising edge only.
        if loud, !speaking { turns += 1 }
        speaking = loud
    }

    private func release() {
        timer?.invalidate()
        timer = nil
        recorder?.stop()
        recorder = nil
        recording = false
        try? AVAudioSession.sharedInstance().setActive(false)
    }
}
