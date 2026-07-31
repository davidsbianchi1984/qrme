import SwiftUI

/// Enrol a passkey, then sign a document with it.
///
/// The screen is built around the one thing WebAuthn cannot do for us: it has
/// no trusted display, so the system prompt can never say what is being
/// signed. The document text is therefore shown here, in full, and the button
/// under it is the last thing touched before the prompt appears. The server
/// stores that exact text alongside the signature, so a dispute reproduces the
/// screen rather than arguing about it.
struct SignatureView: View {
    let profileId: String
    let token: String

    @State private var credentials: [SigningCredential] = []
    @State private var revoking: String?
    @State private var policy: SignaturePolicy?
    @State private var document = ""
    @State private var meaning = "I attest this is accurate and complete"
    // `basic` is what a self-asserted credential can sign, and self-asserted
    // is all this screen can enrol. Defaulting to `standard` shipped a happy
    // path that always failed at the server.
    @State private var tier = "basic"
    @State private var receipt: SignatureReceipt?
    @State private var error: String?
    @State private var busy = false
    // The relying party is the deployment's domain, read from the client's
    // base URL. Resolved once on appear because `base` is actor-isolated.
    @State private var rpId = "qrme.app"

    var body: some View {
        List {
            Section("Signing credentials") {
                if credentials.isEmpty {
                    Text("None yet. A signature needs a passkey bound to this account.")
                        .font(.footnote).foregroundStyle(.secondary)
                }
                ForEach(credentials) { c in
                    VStack(alignment: .leading, spacing: 3) {
                        Text(c.display_name ?? c.credential_id)
                            .font(.subheadline.weight(.semibold))
                        Text("verified at enrolment: \(c.proofing_level)")
                            .font(.caption).foregroundStyle(.secondary)
                        // Surfaced rather than buried: a syncable passkey lives
                        // on every device in the user's cloud account, which is
                        // a weaker claim that only they could have signed.
                        Text(c.device_bound
                             ? "device-bound — cannot sync"
                             : "syncable — exists on your other devices")
                            .font(.caption2)
                            .foregroundStyle(c.device_bound ? .green : .orange)
                        Text("can sign: \(c.can_sign.joined(separator: ", "))")
                            .font(.caption2).foregroundStyle(.secondary)

                        // The screen enrolled these and could not take one
                        // away. A signing credential signs documents as you,
                        // and the moment you most need this button is the
                        // moment the device holding that credential is not in
                        // your hand — so it belongs on the phone you still
                        // have, beside the credential it revokes.
                        Button(role: .destructive) {
                            revoking = c.credential_id
                        } label: {
                            Text("Revoke this credential").font(.caption)
                        }
                        .disabled(busy)
                    }
                }
                Button("Enrol a passkey") { Task { await enrol() } }
                    .disabled(busy)
            }

            Section("What you are signing") {
                TextField("The document text", text: $document, axis: .vertical)
                    .lineLimit(3...8)
                TextField("What your signature means", text: $meaning, axis: .vertical)
                Picker("Assurance", selection: $tier) {
                    Text("basic").tag("basic")
                    Text("standard").tag("standard")
                    Text("high").tag("high")
                }
                Text("This exact text is hashed into the challenge and stored "
                     + "with the signature. The system prompt cannot show it — "
                     + "no passkey prompt can — so read it here.")
                    .font(.caption2).foregroundStyle(.secondary)
                Text("Standard and high need an identity check beyond a "
                     + "passkey — that is what the tier buys. Until one is "
                     + "recorded against your credential, only basic will "
                     + "sign.")
                    .font(.caption2).foregroundStyle(.secondary)
                Button("Sign with Face ID") { Task { await sign() } }
                    .disabled(busy || document.isEmpty || meaning.isEmpty)
            }

            if let receipt {
                Section("Signed") {
                    Label(receipt.verification.valid ? "Verifies" : "Does not verify",
                          systemImage: receipt.verification.valid
                          ? "checkmark.seal.fill" : "xmark.seal.fill")
                        .foregroundStyle(receipt.verification.valid ? .green : .red)
                    Text(receipt.signature_id).font(.caption.monospaced())
                    Text(receipt.signed_at).font(.caption).foregroundStyle(.secondary)
                    // The guarantee never travels without them.
                    ForEach(receipt.limits, id: \.self) { limit in
                        Text("• \(limit)").font(.caption2).foregroundStyle(.secondary)
                    }
                }
            }

            if let policy {
                Section("Standard") {
                    Text(policy.standard).font(.caption2).foregroundStyle(.secondary)
                }
            }

            if let error {
                Section { Text(error).font(.footnote).foregroundStyle(.red) }
            }

            Section {
                Text("Passkeys are bound to a verified domain. Against a LAN "
                     + "dev server there is no such domain, so signing works "
                     + "only on a deployment with associated domains "
                     + "configured — see docs/signatures.md.")
                    .font(.caption2).foregroundStyle(.secondary)
            }
        }
        .confirmationDialog("Revoke this credential?",
                           isPresented: .constant(revoking != nil),
                           titleVisibility: .visible) {
            Button("Revoke", role: .destructive) {
                if let id = revoking { Task { await revoke(id) } }
                revoking = nil
            }
            Button("Keep it", role: .cancel) { revoking = nil }
        } message: {
            Text("Signatures already made stay valid and stay in the audit "
                 + "trail. This stops the credential being used again — which "
                 + "is what you want if the device holding it is gone.")
        }
        .navigationTitle("Signatures")
        .task { await load() }
    }

    private func load() async {
        // A bare host with a port is not a valid rp id and Apple rejects it
        // before any prompt appears, so fall back to the deployment domain.
        if let host = await ApiClient.shared.base.host, host.contains(".") {
            rpId = host
        }
        policy = try? await ApiClient.shared.signaturePolicy()
        credentials = (try? await ApiClient.shared.signingCredentials(token: token)) ?? []
    }

    private func revoke(_ credentialId: String) async {
        busy = true; error = nil
        defer { busy = false }
        do {
            try await ApiClient.shared.revokeCredential(id: credentialId,
                                                        token: token)
            credentials = (try? await ApiClient.shared.signingCredentials(
                token: token)) ?? []
        } catch { self.error = error.localizedDescription }
    }

    private func enrol() async {
        busy = true; error = nil
        defer { busy = false }
        do {
            let options = try await ApiClient.shared.enrollOptions(
                displayName: "QRME owner", token: token)
            let reg = try await Signing.register(
                rpId: options.rp.id, challenge: options.challenge,
                userId: options.user.id, userName: options.user.name)
            _ = try await ApiClient.shared.enrollCredential(
                credentialId: reg.credentialId,
                attestationObject: reg.attestationObject,
                clientDataJSON: reg.clientDataJSON,
                challenge: options.challenge,
                proofingLevel: "self_asserted",
                displayName: options.user.displayName,
                attestor: nil, token: token)
            await load()
        } catch {
            self.error = error.localizedDescription
        }
    }

    private func sign() async {
        busy = true; error = nil; receipt = nil
        defer { busy = false }
        do {
            let envelope = try await ApiClient.shared.requestSignature(
                document: document, meaning: meaning, displayText: document,
                tier: tier, bindingKind: "profile", bindingRef: profileId,
                token: token)
            let assertion = try await Signing.assert(
                rpId: rpId, challenge: envelope.challenge)
            receipt = try await ApiClient.shared.submitSignature(
                envelopeId: envelope.envelope_id, assertion: assertion,
                platform: Signing.platform, token: token)
        } catch {
            self.error = error.localizedDescription
        }
    }
}
