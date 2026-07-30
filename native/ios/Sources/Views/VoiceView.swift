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
    let profileId: String
    let token: String

    @StateObject private var recorder = VoiceRecorder()
    @State private var status: VoiceprintStatus?
    @State private var say = ""
    @State private var spoken: VoiceSpoken?
    @State private var revocation: VoiceRevocation?
    @State private var error: String?
    @State private var busy = false

    private var consented: Bool { status?.consent.granted == true }

    /// Built up in steps rather than one interpolation: chaining `.map` off an
    /// optional inside an optional-chained expression is easy to get subtly
    /// wrong, and this reads as what it is.
    private var grantLine: String {
        let sources = status?.consent.sources ?? []
        var line = "Granted for " + sources.joined(separator: ", ")
        if let at = status?.consent.granted_at, at.count >= 10 {
            line += " · " + String(at.prefix(10))
        }
        return line
    }

    private var builtLine: String {
        guard let p = status?.voiceprint else { return "" }
        let day = p.built_at.map { String($0.prefix(10)) } ?? "—"
        return "Built \(day) · \(p.id)"
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                permission
                if consented {
                    enrollment
                    voiceprint
                }
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
            Text("1 · Permission").font(.headline).foregroundStyle(Theme.txt)
            if consented {
                Text(grantLine).font(.caption).foregroundStyle(Theme.t2)
                Button("Withdraw consent — delete the samples, retire the voice") {
                    act { revocation = try await ApiClient.shared
                        .revokeVoiceprint(id: profileId, token: token) }
                }
                .font(.caption.bold()).foregroundStyle(.white)
                .padding(.horizontal, 12).padding(.vertical, 9)
                .background(Theme.red).clipShape(Capsule())
                .disabled(busy)
                if let revocation {
                    Text("\(revocation.samples_deleted) sample(s) deleted. \(revocation.note)")
                        .font(.caption2).foregroundStyle(Theme.amber)
                }
            } else {
                Text("Nothing is recorded until you say so. QRME will only "
                     + "learn your own voice — there is no path here for "
                     + "anybody else's.")
                    .font(.caption).foregroundStyle(Theme.t2)
                Button("This is my own voice — allow enrollment") {
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
            Text("2 · Enrollment").font(.headline).foregroundStyle(Theme.txt)
            Text("Tap record and talk normally — a sentence or two about your "
                 + "day is better material than a read-aloud paragraph.")
                .font(.caption).foregroundStyle(Theme.t2)

            HStack(spacing: 12) {
                Button(recorder.recording ? "Stop" : "Record a sample") {
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
                        Text("\(e.samples) sample(s) · \(String(format: "%.1f", e.seconds))s")
                            .font(.subheadline.bold()).foregroundStyle(Theme.txt)
                        Text(turnLine(e) + " · needs \(e.threshold.samples) samples and "
                             + "\(String(format: "%.0f", e.threshold.seconds))s")
                            .font(.caption2).foregroundStyle(Theme.t3)
                    }
                    Spacer()
                    Text(e.ready ? "ready" : "not yet")
                        .font(.caption2.bold())
                        .foregroundStyle(e.ready ? Theme.green : Theme.amber)
                }
                if !e.ready, !e.needs.isEmpty {
                    Text("Still wants: \(e.needs.joined(separator: ", ")).")
                        .font(.caption2).foregroundStyle(Theme.t2)
                }
                Text(e.method).font(.caption2).foregroundStyle(Theme.t3)
            }

            Text("The recording stays on this device. Only its length and turn "
                 + "count are sent.")
                .font(.caption2).foregroundStyle(Theme.t3)
        }
        .card()
    }

    // MARK: 812 — the print, and speaking with it

    private var voiceprint: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("3 · The voice").font(.headline).foregroundStyle(Theme.txt)
            if let p = status?.voiceprint, p.active {
                Text(builtLine).font(.caption2).foregroundStyle(Theme.t3)
                TextField("Say something in it", text: $say, axis: .vertical)
                    .lineLimit(2...4)
                    .font(.subheadline).foregroundStyle(Theme.txt)
                    .padding(10)
                    .background(Theme.scrBot)
                    .clipShape(RoundedRectangle(cornerRadius: 10))
                Button("Speak") {
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
                     ? "Enough of your voice is on record — mint the voiceprint."
                     : "Record a few more samples first.")
                    .font(.caption).foregroundStyle(Theme.t2)
                Button("Build my voiceprint") {
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
                    Text("A previous voiceprint was retired when consent was "
                         + "withdrawn. That record stays.")
                        .font(.caption2).foregroundStyle(Theme.t3)
                }
            }
        }
        .card()
    }

    private var invariants: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text("What always holds").font(.headline).foregroundStyle(Theme.txt)
            ForEach([
                "Anything spoken in this voice carries a watermark and says it is synthesized.",
                "Only your own voice — the permission is an attestation, not a checkbox.",
                "Withdrawing deletes the samples and silences the voice; the withdrawal stays on record.",
            ], id: \.self) { line in
                Text("· " + line).font(.caption2).foregroundStyle(Theme.t2)
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
