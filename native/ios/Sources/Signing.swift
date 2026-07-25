import AuthenticationServices
import SwiftUI

/// The signing ceremony, driven by the platform's own passkey UI.
///
/// This is the client half of `docs/signatures.md`. The gesture is the Face ID
/// (or Touch ID, or Optic ID) prompt the user already knows; what leaves the
/// device is an assertion signed inside the Secure Enclave, over a challenge
/// that **is** the document being signed. The app never sees the private key
/// and cannot manufacture the result — which is the entire point, because a
/// `LAContext.evaluatePolicy` boolean is the app's word and the app's word is
/// what a dispute is about.
///
/// Two constraints worth knowing before wiring this to a server:
///
/// * **Passkeys need an associated domain.** `ASAuthorizationPlatformPublicKey`
///   credentials are bound to a relying-party identifier that Apple verifies
///   against `apple-app-site-association` at `webcredentials:<domain>`. They do
///   not work against a bare IP or `127.0.0.1`, so the LAN dev flow that runs
///   the rest of this app cannot exercise signing. That is a deployment step,
///   not a code one, and it is why `SignatureView` says so on screen instead of
///   failing with a system error nobody can read.
/// * **There is no trusted display.** The system prompt says "Sign in to
///   qrme.app"; it cannot say what is being signed. So the document is rendered
///   here, immediately before the prompt, and the server records the exact text
///   it sent. That is a control, not a guarantee, and the spec says so.
enum Signing {

    /// Base64url without padding — what the API speaks in both directions.
    static func b64url(_ data: Data) -> String {
        data.base64EncodedString()
            .replacingOccurrences(of: "+", with: "-")
            .replacingOccurrences(of: "/", with: "_")
            .replacingOccurrences(of: "=", with: "")
    }

    static func data(fromB64url s: String) -> Data? {
        var t = s.replacingOccurrences(of: "-", with: "+")
            .replacingOccurrences(of: "_", with: "/")
        t += String(repeating: "=", count: (4 - t.count % 4) % 4)
        return Data(base64Encoded: t)
    }

    /// visionOS satisfies `userVerification: required` with Optic ID, and its
    /// prompt is composited by the system — the same position iOS is in with
    /// Face ID. Reported so the evidence package can say where a signature was
    /// made; the server decides what that means.
    static var platform: String {
        #if os(visionOS)
        return "visionos"
        #else
        return "ios"
        #endif
    }

    // MARK: - registration

    struct Registration {
        let credentialId: String
        let attestationObject: String
        let clientDataJSON: String
    }

    static func register(rpId: String, challenge: String, userId: String,
                         userName: String) async throws -> Registration {
        guard let rawChallenge = data(fromB64url: challenge),
              let rawUserId = data(fromB64url: userId) else {
            throw ApiError.http("the server sent a challenge this device cannot read")
        }
        let provider = ASAuthorizationPlatformPublicKeyCredentialProvider(
            relyingPartyIdentifier: rpId)
        let request = provider.createCredentialRegistrationRequest(
            challenge: rawChallenge, name: userName, userID: rawUserId)
        // Without this the ceremony can be satisfied by a button press, and
        // every signature made with the credential would be a tap.
        request.userVerificationPreference = .required
        // Direct attestation so the evidence can record the AAGUID — which
        // authenticator model produced the signature.
        request.attestationPreference = .direct

        let result = try await Ceremony.perform(request)
        guard let reg = result as? ASAuthorizationPlatformPublicKeyCredentialRegistration,
              let attestation = reg.rawAttestationObject else {
            throw ApiError.http("registration returned no attestation")
        }
        return Registration(credentialId: b64url(reg.credentialID),
                            attestationObject: b64url(attestation),
                            clientDataJSON: b64url(reg.rawClientDataJSON))
    }

    // MARK: - assertion

    struct Assertion {
        let credentialId: String
        let signature: String
        let authenticatorData: String
        let clientDataJSON: String
    }

    static func assert(rpId: String, challenge: String) async throws -> Assertion {
        guard let rawChallenge = data(fromB64url: challenge) else {
            throw ApiError.http("the server sent a challenge this device cannot read")
        }
        let provider = ASAuthorizationPlatformPublicKeyCredentialProvider(
            relyingPartyIdentifier: rpId)
        let request = provider.createCredentialAssertionRequest(
            challenge: rawChallenge)
        request.userVerificationPreference = .required

        let result = try await Ceremony.perform(request)
        guard let a = result as? ASAuthorizationPlatformPublicKeyCredentialAssertion else {
            throw ApiError.http("signing returned no assertion")
        }
        return Assertion(credentialId: b64url(a.credentialID),
                         signature: b64url(a.signature),
                         authenticatorData: b64url(a.rawAuthenticatorData),
                         clientDataJSON: b64url(a.rawClientDataJSON))
    }
}

/// Bridges `ASAuthorizationController`'s delegate callbacks into `async`.
///
/// The controller does not retain its delegate, so the instance holds itself
/// until one of the callbacks fires. Getting this wrong deallocates the
/// delegate mid-ceremony and the continuation never resumes — the prompt
/// appears and the app hangs afterwards.
private final class Ceremony: NSObject, ASAuthorizationControllerDelegate,
                              ASAuthorizationControllerPresentationContextProviding {
    private var continuation: CheckedContinuation<ASAuthorizationCredential, Error>?
    private var keepAlive: Ceremony?

    static func perform(_ request: ASAuthorizationRequest) async throws
        -> ASAuthorizationCredential {
        let ceremony = Ceremony()
        return try await withCheckedThrowingContinuation { cont in
            ceremony.continuation = cont
            ceremony.keepAlive = ceremony
            let controller = ASAuthorizationController(authorizationRequests: [request])
            controller.delegate = ceremony
            controller.presentationContextProvider = ceremony
            controller.performRequests()
        }
    }

    private func finish(_ result: Result<ASAuthorizationCredential, Error>) {
        continuation?.resume(with: result)
        continuation = nil
        keepAlive = nil
    }

    func authorizationController(controller: ASAuthorizationController,
                                 didCompleteWithAuthorization auth: ASAuthorization) {
        finish(.success(auth.credential))
    }

    func authorizationController(controller: ASAuthorizationController,
                                 didCompleteWithError error: Error) {
        finish(.failure(error))
    }

    func presentationAnchor(for controller: ASAuthorizationController)
        -> ASPresentationAnchor {
        #if os(visionOS)
        return UIApplication.shared.connectedScenes
            .compactMap { ($0 as? UIWindowScene)?.keyWindow }.first ?? UIWindow()
        #else
        return UIApplication.shared.connectedScenes
            .compactMap { $0 as? UIWindowScene }
            .flatMap(\.windows).first { $0.isKeyWindow } ?? UIWindow()
        #endif
    }
}
