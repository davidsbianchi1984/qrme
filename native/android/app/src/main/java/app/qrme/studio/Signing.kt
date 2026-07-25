package app.qrme.studio

import android.content.Context
import androidx.credentials.CreatePublicKeyCredentialRequest
import androidx.credentials.CreatePublicKeyCredentialResponse
import androidx.credentials.CredentialManager
import androidx.credentials.GetCredentialRequest
import androidx.credentials.GetPublicKeyCredentialOption
import androidx.credentials.PublicKeyCredential
import org.json.JSONArray
import org.json.JSONObject

/**
 * The signing ceremony, driven by the platform's own passkey UI.
 *
 * This is the client half of `docs/signatures.md`. The gesture is the
 * fingerprint or face prompt the user already knows; what leaves the device is
 * an assertion signed inside StrongBox (or the TEE), over a challenge that
 * **is** the document being signed. The app never sees the private key and
 * cannot manufacture the result — which is the point, because a
 * `BiometricPrompt` success callback is the app's word, and the app's word is
 * what a dispute is about.
 *
 * Two things differ from the iOS path and are worth knowing:
 *
 * * **Credential Manager speaks WebAuthn JSON, not fields.** The request is a
 *   JSON string and the response is a JSON string, so this file builds the one
 *   and takes the other apart. The server wants discrete fields, and doing the
 *   parsing here keeps that shape identical across platforms.
 * * **Passkeys need Digital Asset Links.** The relying party must serve
 *   `/.well-known/assetlinks.json` naming this app's signing certificate. That
 *   cannot exist for a LAN dev server, so signing works only against a real
 *   deployment — a hosting step, not a code one.
 */
object Signing {

    const val PLATFORM = "android"

    class SigningUnavailable(message: String) : Exception(message)

    data class Registration(
        val credentialId: String,
        val attestationObject: String,
        val clientDataJson: String,
    )

    data class Assertion(
        val credentialId: String,
        val signature: String,
        val authenticatorData: String,
        val clientDataJson: String,
    )

    /**
     * Build the registration request. `userVerification: "required"` is the
     * load-bearing field: without it the ceremony can be satisfied by a tap,
     * and every signature made with the credential would be a tap.
     */
    private fun registrationJson(rpId: String, rpName: String, challenge: String,
                                 userId: String, userName: String,
                                 displayName: String): String =
        JSONObject().apply {
            put("challenge", challenge)
            put("rp", JSONObject().put("id", rpId).put("name", rpName))
            put("user", JSONObject()
                .put("id", userId)
                .put("name", userName)
                .put("displayName", displayName))
            put("pubKeyCredParams", JSONArray().apply {
                put(JSONObject().put("type", "public-key").put("alg", -7))
                put(JSONObject().put("type", "public-key").put("alg", -257))
            })
            // Direct attestation so the evidence records which authenticator
            // model produced the signature.
            put("attestation", "direct")
            put("authenticatorSelection", JSONObject()
                .put("userVerification", "required")
                .put("residentKey", "required"))
        }.toString()

    private fun assertionJson(rpId: String, challenge: String): String =
        JSONObject().apply {
            put("challenge", challenge)
            put("rpId", rpId)
            put("userVerification", "required")
        }.toString()

    suspend fun register(context: Context, rpId: String, rpName: String,
                         challenge: String, userId: String, userName: String,
                         displayName: String): Registration {
        val response = CredentialManager.create(context).createCredential(
            context,
            CreatePublicKeyCredentialRequest(
                registrationJson(rpId, rpName, challenge, userId, userName,
                    displayName)),
        )
        val json = (response as? CreatePublicKeyCredentialResponse)
            ?.registrationResponseJson
            ?: throw SigningUnavailable("the credential manager returned no passkey")
        val o = JSONObject(json)
        val inner = o.getJSONObject("response")
        return Registration(
            credentialId = o.getString("id"),
            attestationObject = inner.getString("attestationObject"),
            clientDataJson = inner.getString("clientDataJSON"),
        )
    }

    suspend fun assert(context: Context, rpId: String,
                       challenge: String): Assertion {
        val response = CredentialManager.create(context).getCredential(
            context,
            GetCredentialRequest(
                listOf(GetPublicKeyCredentialOption(assertionJson(rpId, challenge)))),
        )
        val credential = response.credential as? PublicKeyCredential
            ?: throw SigningUnavailable("no passkey was returned for signing")
        val o = JSONObject(credential.authenticationResponseJson)
        val inner = o.getJSONObject("response")
        return Assertion(
            credentialId = o.getString("id"),
            signature = inner.getString("signature"),
            authenticatorData = inner.getString("authenticatorData"),
            clientDataJson = inner.getString("clientDataJSON"),
        )
    }
}
