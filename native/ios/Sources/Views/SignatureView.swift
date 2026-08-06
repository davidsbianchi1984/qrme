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
    @EnvironmentObject var state: AppState
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
            Section(L10n.t("nsig.creds", state.language)) {
                if credentials.isEmpty {
                    Text(L10n.t("nsig.none", state.language))
                        .font(.footnote).foregroundStyle(.secondary)
                }
                ForEach(credentials) { c in
                    VStack(alignment: .leading, spacing: 3) {
                        Text(c.display_name ?? c.credential_id)
                            .font(.subheadline.weight(.semibold))
                        Text(L10n.fill("nsig.proofing", state.language,
                                       ["level": L10n.t("nsig.level.\(c.proofing_level)", state.language)]))
                            .font(.caption).foregroundStyle(.secondary)
                        // Surfaced rather than buried: a syncable passkey lives
                        // on every device in the user's cloud account, which is
                        // a weaker claim that only they could have signed.
                        Text(c.device_bound
                             ? "device-bound — cannot sync"
                             : "syncable — exists on your other devices")
                            .font(.caption2)
                            .foregroundStyle(c.device_bound ? .green : .orange)
                        Text(L10n.fill("nsig.cansign", state.language, ["levels":
                            c.can_sign.map { L10n.t("nsig.level.\($0)", state.language) }
                                     .joined(separator: ", ")]))
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
                            Text(L10n.t("nsig.revoke.this", state.language)).font(.caption)
                        }
                        .disabled(busy)
                    }
                }
                Button(L10n.t("nsig.enrol", state.language)) { Task { await enrol() } }
                    .disabled(busy)
            }

            Section(L10n.t("nsig.signing", state.language)) {
                TextField(L10n.t("nsig.doc", state.language), text: $document, axis: .vertical)
                    .lineLimit(3...8)
                TextField(L10n.t("nsig.means", state.language), text: $meaning, axis: .vertical)
                Picker("Assurance", selection: $tier) {
                    Text(L10n.t("nsig.level.basic", state.language)).tag("basic")
                    Text(L10n.t("nsig.level.standard", state.language)).tag("standard")
                    Text(L10n.t("nsig.level.high", state.language)).tag("high")
                }
                Text(L10n.t("nsig.hashed", state.language))
                    .font(.caption2).foregroundStyle(.secondary)
                Text(L10n.t("nsig.tiers", state.language))
                    .font(.caption2).foregroundStyle(.secondary)
                Button(L10n.t("nsig.faceid", state.language)) { Task { await sign() } }
                    .disabled(busy || document.isEmpty || meaning.isEmpty)
            }

            if let receipt {
                Section(L10n.t("nsig.signed", state.language)) {
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
                Section(L10n.t("nsig.level.standard", state.language)) {
                    Text(policy.standard).font(.caption2).foregroundStyle(.secondary)
                }
            }

            if let error {
                Section { Text(error).font(.footnote).foregroundStyle(.red) }
            }

            Section {
                Text(L10n.t("nsig.domain", state.language))
                    .font(.caption2).foregroundStyle(.secondary)
            }
        }
        .confirmationDialog("Revoke this credential?",
                           isPresented: .constant(revoking != nil),
                           titleVisibility: .visible) {
            Button(L10n.t("nsig.revoke", state.language), role: .destructive) {
                if let id = revoking { Task { await revoke(id) } }
                revoking = nil
            }
            Button(L10n.t("nsig.keep", state.language), role: .cancel) { revoking = nil }
        } message: {
            Text(L10n.t("nsig.revoked.note", state.language))
        }
        .navigationTitle(L10n.t("nsig", state.language))
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
