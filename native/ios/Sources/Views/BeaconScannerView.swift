import AVFoundation
import SwiftUI
import Vision

/// Point the phone at a beacon sticker and the profile appears **on the
/// sticker**, in the live camera feed. No tap, no page, no navigation.
///
/// What a stock camera app can do with a QR code is open a URL — that is the
/// whole of its API surface, and no third party can change it. Rendering
/// something over the viewfinder requires being the app that owns the
/// viewfinder. So this is that app: Vision reads the code, the card comes
/// back from `/b/{id}/card`, and the portrait is drawn on the quadrilateral
/// Vision reported, tracking the sticker as the phone moves.
///
/// The AI mark is drawn with the face, always, from the same payload. An
/// overlay that could show the portrait without the disclosure would be the
/// worst version of this feature: a synthetic person appearing in the real
/// world with nothing saying so.
struct BeaconScannerView: View {
    @EnvironmentObject var state: AppState
    @StateObject private var scanner = BeaconScanner()

    /// Whether the camera has been allowed, refused, or not yet asked.
    ///
    /// Until this existed, `configure()` hit `AVCaptureDevice.default(for:
    /// .video)`, failed silently, and returned — leaving the session stopped
    /// behind a `CameraPreview` that renders black, with *"point at a
    /// beacon"* floating over it. A person who declined the permission got a
    /// dead screen and no idea why.
    ///
    /// The second line matters more than the first. Android's copy of this
    /// state says **"Nothing is recorded — frames are read and discarded"**,
    /// which is a promise about what this app does with a camera. The iPhone
    /// reader was never given it, on the one screen where they are being
    /// asked to hand over a viewfinder. Both rows were sitting translated in
    /// this shell's own table, asked for by nothing.
    @State private var allowed: Bool?

    var body: some View {
        ZStack {
            if allowed == false {
                refused
            } else {
                scanning
            }
        }
        .task { allowed = await BeaconScannerView.askForCamera() }
    }

    /// What a person sees when they have said no — the reason, the promise,
    /// and a way back out, matching what Android has shown all along.
    @ViewBuilder private var refused: some View {
        VStack(spacing: 10) {
            Text(L10n.t("nbcn.camera", state.language))
                .font(.subheadline).foregroundStyle(Theme.txt)
            Text(L10n.t("nbcn.nothing", state.language))
                .font(.caption).foregroundStyle(Theme.t2)
                .multilineTextAlignment(.center)
        }
        .padding(24)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Theme.bg)
    }

    /// Asks once, and reports what the answer was.
    ///
    /// `.notDetermined` is the only state that prompts; a previous refusal is
    /// respected rather than re-asked, because a permission dialog that keeps
    /// coming back is how people learn to dismiss them without reading.
    static func askForCamera() async -> Bool {
        switch AVCaptureDevice.authorizationStatus(for: .video) {
        case .authorized: return true
        case .notDetermined:
            return await AVCaptureDevice.requestAccess(for: .video)
        default: return false
        }
    }

    @ViewBuilder private var scanning: some View {
        ZStack {
            CameraPreview(session: scanner.session).ignoresSafeArea()

            if let card = scanner.card, let quad = scanner.quad {
                BeaconOverlay(card: card, quad: quad)
                    .transition(.opacity.combined(with: .scale(scale: 0.92)))
                    .animation(.spring(response: 0.35, dampingFraction: 0.75),
                               value: card.profileId)
            }

            VStack {
                Spacer()
                Text(scanner.card == nil
                     ? L10n.t("nbcn.point", state.language)
                     : L10n.t("nbcn.tap", state.language))
                    .font(.footnote.weight(.semibold))
                    .foregroundStyle(.white.opacity(0.85))
                    .padding(.horizontal, 14).padding(.vertical, 8)
                    .background(.black.opacity(0.45), in: Capsule())
                    .padding(.bottom, 34)
            }
        }
        .task { await scanner.start(baseURL: ApiClient.shared.base.absoluteString) }
        .onDisappear { scanner.stop() }
        .onTapGesture {
            if let url = scanner.card?.openURL { UIApplication.shared.open(url) }
        }
    }
}

/// What the overlay draws. Mirrors `GET /b/{id}/card`.
struct BeaconCard: Equatable {
    let profileId: String
    let displayName: String
    let watermark: String
    let initials: String
    let portrait: URL?
    let label: String?
    let sharedRoom: Bool
    let openURL: URL?
    let ageWall: Bool
}

/// The portrait, pinned to the sticker.
private struct BeaconOverlay: View {
    let card: BeaconCard
    let quad: CGRect

    var body: some View {
        VStack(spacing: 6) {
            if card.ageWall {
                // Nothing about the profile is in the payload to leak.
                Text("18+")
                    .font(.system(size: 34, weight: .heavy))
                    .foregroundStyle(.white)
                    .frame(width: quad.width, height: quad.width)
                    .background(.black.opacity(0.72),
                                in: RoundedRectangle(cornerRadius: 18))
            } else {
                ZStack(alignment: .bottomLeading) {
                    portrait
                    // Drawn from the same payload as the face, so the two
                    // cannot come apart.
                    Text(card.watermark)
                        .font(.system(size: 11, weight: .bold))
                        .foregroundStyle(.white)
                        .padding(.horizontal, 8).padding(.vertical, 4)
                        .background(.black.opacity(0.75), in: Capsule())
                        .padding(6)
                }
                .frame(width: quad.width, height: quad.width)
                .clipShape(RoundedRectangle(cornerRadius: 18))

                Text(card.displayName)
                    .font(.headline).foregroundStyle(.white)
                    .shadow(radius: 4)
                if card.sharedRoom {
                    Text(L10n.t("nbcn.shared", state.language))
                        .font(.caption2).foregroundStyle(.white.opacity(0.8))
                }
            }
        }
        // Follow the sticker: Vision hands back where the code is, and the
        // portrait sits on it rather than in a fixed corner of the screen.
        .position(x: quad.midX, y: quad.midY - quad.height * 0.75)
    }

    @ViewBuilder private var portrait: some View {
        if let url = card.portrait {
            AsyncImage(url: url) { image in
                image.resizable().scaledToFill()
            } placeholder: { initialsTile }
        } else {
            initialsTile
        }
    }

    private var initialsTile: some View {
        ZStack {
            Color(red: 0.09, green: 0.07, blue: 0.20)
            Text(card.initials)
                .font(.system(size: quad.width * 0.34, weight: .bold))
                .foregroundStyle(Color(red: 0.49, green: 0.36, blue: 1.0))
        }
    }
}

// MARK: - camera + detection

final class BeaconScanner: NSObject, ObservableObject,
                           AVCaptureVideoDataOutputSampleBufferDelegate {
    @Published var card: BeaconCard?
    @Published var quad: CGRect?

    let session = AVCaptureSession()
    private let queue = DispatchQueue(label: "app.qrme.scanner")
    private var baseURL = ""
    private var lastResolved: String?
    private var inFlight = false

    func start(baseURL: String) {
        self.baseURL = baseURL.hasSuffix("/")
            ? String(baseURL.dropLast()) : baseURL
        queue.async { [weak self] in
            guard let self, !self.session.isRunning else { return }
            self.configure()
            self.session.startRunning()
        }
    }

    func stop() {
        queue.async { [weak self] in self?.session.stopRunning() }
    }

    private func configure() {
        session.beginConfiguration()
        session.sessionPreset = .high
        guard let device = AVCaptureDevice.default(for: .video),
              let input = try? AVCaptureDeviceInput(device: device),
              session.canAddInput(input) else {
            session.commitConfiguration()
            return
        }
        session.addInput(input)

        let output = AVCaptureVideoDataOutput()
        output.alwaysDiscardsLateVideoFrames = true
        output.setSampleBufferDelegate(self, queue: queue)
        if session.canAddOutput(output) { session.addOutput(output) }
        session.commitConfiguration()
    }

    func captureOutput(_ output: AVCaptureOutput,
                       didOutput sampleBuffer: CMSampleBuffer,
                       from connection: AVCaptureConnection) {
        guard let buffer = CMSampleBufferGetImageBuffer(sampleBuffer) else { return }
        let request = VNDetectBarcodesRequest { [weak self] request, _ in
            guard let self,
                  let result = (request.results as? [VNBarcodeObservation])?.first,
                  let payload = result.payloadStringValue else {
                DispatchQueue.main.async { self?.clear() }
                return
            }
            DispatchQueue.main.async {
                // Vision reports a normalised box with the origin at the
                // bottom-left; SwiftUI draws from the top-left.
                let box = result.boundingBox
                let screen = UIScreen.main.bounds
                self.quad = CGRect(x: box.minX * screen.width,
                                   y: (1 - box.maxY) * screen.height,
                                   width: box.width * screen.width,
                                   height: box.height * screen.height)
            }
            self.resolve(payload: payload)
        }
        request.symbologies = [.qr]
        try? VNImageRequestHandler(cvPixelBuffer: buffer,
                                   orientation: .right).perform([request])
    }

    private func clear() {
        card = nil
        quad = nil
        lastResolved = nil
    }

    /// Fetch the card once per code. The camera delivers ~30 frames a second
    /// and every one of them sees the same sticker; without this the overlay
    /// would re-request continuously and count a scan each time.
    private func resolve(payload: String) {
        guard let beaconId = Self.beaconId(from: payload) else { return }
        guard beaconId != lastResolved, !inFlight else { return }
        inFlight = true
        lastResolved = beaconId

        Task { [weak self] in
            guard let self else { return }
            defer { self.inFlight = false }
            guard let url = URL(string: "\(self.baseURL)/b/\(beaconId)/card"),
                  let (data, _) = try? await URLSession.shared.data(from: url),
                  let json = try? JSONSerialization.jsonObject(with: data)
                      as? [String: Any] else { return }

            let wall = json["age_wall"] as? Bool ?? false
            let card = BeaconCard(
                profileId: json["profile_id"] as? String ?? beaconId,
                displayName: json["display_name"] as? String ?? "",
                watermark: json["watermark"] as? String ?? "",
                initials: json["initials"] as? String ?? "",
                portrait: (json["portrait"] as? String).flatMap(URL.init),
                label: json["label"] as? String,
                sharedRoom: json["shared_room"] is String,
                openURL: (json["open_url"] as? String).flatMap(URL.init),
                ageWall: wall)
            await MainActor.run { self.card = card }
        }
    }

    /// A beacon's printed QR encodes `<base>/b/<id>`. Anything else is
    /// somebody's Wi-Fi password and is left alone.
    static func beaconId(from payload: String) -> String? {
        guard let url = URL(string: payload) else { return nil }
        let parts = url.pathComponents.filter { $0 != "/" }
        guard parts.count >= 2, parts[parts.count - 2] == "b" else { return nil }
        let id = parts[parts.count - 1]
        return id.hasPrefix("bcn_") ? id : nil
    }
}

// MARK: - preview layer

private struct CameraPreview: UIViewRepresentable {
    let session: AVCaptureSession

    func makeUIView(context: Context) -> PreviewView {
        let view = PreviewView()
        view.videoPreviewLayer.session = session
        view.videoPreviewLayer.videoGravity = .resizeAspectFill
        return view
    }

    func updateUIView(_ uiView: PreviewView, context: Context) {}

    final class PreviewView: UIView {
        override class var layerClass: AnyClass { AVCaptureVideoPreviewLayer.self }
        var videoPreviewLayer: AVCaptureVideoPreviewLayer {
            layer as! AVCaptureVideoPreviewLayer
        }
    }
}
