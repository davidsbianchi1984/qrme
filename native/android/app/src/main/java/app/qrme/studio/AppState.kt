package app.qrme.studio

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import kotlinx.coroutines.launch

/**
 * App-wide state: the created profile id + owner token (persisted to
 * SharedPreferences) and the async calls the screens invoke.
 */
class StudioViewModel(app: Application) : AndroidViewModel(app) {
    private val prefs = app.getSharedPreferences("qrme", 0)

    var pid by mutableStateOf<String?>(prefs.getString("pid", null))
        private set
    var token by mutableStateOf<String?>(prefs.getString("token", null))
        private set
    var displayName by mutableStateOf(prefs.getString("name", "") ?: "")
        private set
    // The device owner's interactor identity for Chat, minted lazily.
    // `interactorVerified` is true when the identity was minted with an 18+
    // birthdate — the key that opens the rated stranger tier.
    var interactorId by mutableStateOf<String?>(prefs.getString("interactor", null))

    /** The person's own model key, held on this device only and sent per
     *  request as `x-llm-api-key`. The console has offered this since 0.4.3
     *  and the phones never did — so a key set in the console was used there
     *  and the deployment's key used here, on the same account. */
    var llmKey by mutableStateOf(prefs.getString("llmKey", "") ?: "")
    var signupKey by mutableStateOf(prefs.getString("signupKey", "") ?: "")
        private set
    var interactorVerified by mutableStateOf(prefs.getBoolean("interactor_adult", false))
        private set
    // The profile's chosen language also drives the app chrome via L10n.
    var language by mutableStateOf(prefs.getString("lang", "en") ?: "en")
        private set

    val isSignedIn get() = pid != null && token != null

    fun rememberLanguage(code: String) {
        language = code
        prefs.edit().putString("lang", code).apply()
    }

    // The bearer token for that identity, needed by every age-gated surface.
    var interactorToken by mutableStateOf<String?>(prefs.getString("interactor_token", null))
        private set

    fun rememberInteractor(id: String, token: String? = null,
                           adult: Boolean = false) {
        interactorId = id
        interactorVerified = adult
        if (token != null) interactorToken = token
        prefs.edit().putString("interactor", id)
            .putString("interactor_token", token ?: interactorToken)
            .putBoolean("interactor_adult", adult).apply()
    }

    fun createProfile(
        name: String, persona: String, kind: String, birthdate: String,
        language: String? = null,
        onError: (String) -> Unit, onBusy: (Boolean) -> Unit,
    ) {
        onBusy(true)
        viewModelScope.launch {
            runCatching { ApiClient.createProfile(name, persona, kind, birthdate, language) }
                .onSuccess { r ->
                    pid = r.id; token = r.ownerToken; displayName = r.displayName
                    prefs.edit().putString("pid", r.id).putString("token", r.ownerToken)
                        .putString("name", r.displayName).apply()
                }
                .onFailure { e ->
                    // A refusal keeps the server's own sentence — already in
                    // the reader's language. Only a failure to REACH the
                    // server gets this shell's wording, and that wording
                    // comes from the table like the iPhone's, not from a
                    // hardcoded English string only one reader could use.
                    onError(if (e is java.io.IOException)
                        L10n.fill("nw.unreachable", L10n.deviceLanguage(),
                            mapOf("detail" to (e.message ?: "")))
                    else (e.message ?: ""))
                }
            onBusy(false)
        }
    }

    fun importCard(
        cardJSON: String, birthdate: String, language: String? = null,
        onError: (String) -> Unit, onBusy: (Boolean) -> Unit,
    ) {
        onBusy(true)
        viewModelScope.launch {
            runCatching { ApiClient.importCard(cardJSON, birthdate, language) }
                .onSuccess { r ->
                    pid = r.id; token = r.ownerToken; displayName = r.displayName
                    prefs.edit().putString("pid", r.id).putString("token", r.ownerToken)
                        .putString("name", r.displayName).apply()
                }
                .onFailure { onError(it.message ?: "") }
            onBusy(false)
        }
    }

    /**
     * Open a profile this account already holds.
     *
     * The other two entrances to a signed-in session — [createProfile] and
     * [importCard] — both *make* something. This is the third and it was
     * missing: an owner token is minted once, in the create response, and a
     * reinstalled phone had no way to ask for another. So the only route back
     * into a profile made on another device was to make a second one.
     *
     * The account token stays with the caller and is never persisted; what
     * lands in prefs is the same (pid, owner token) pair the other two write.
     */
    fun openHeldProfile(
        accountId: String, accountToken: String, profileId: String,
        shownAs: String,
        onError: (String) -> Unit, onBusy: (Boolean) -> Unit,
    ) {
        onBusy(true)
        viewModelScope.launch {
            runCatching {
                ApiClient.mintOwnerToken(accountId, profileId, accountToken)
            }.onSuccess { (id, owner) ->
                pid = id; token = owner; displayName = shownAs
                prefs.edit().putString("pid", id).putString("token", owner)
                    .putString("name", shownAs).apply()
            }.onFailure { onError(it.message ?: "") }
            onBusy(false)
        }
    }

    fun signOut() {
        pid = null; token = null; displayName = ""
        interactorId = null; interactorToken = null; interactorVerified = false
        prefs.edit().clear().apply()
    }

    fun <T> call(block: suspend () -> T, onResult: (Result<T>) -> Unit) {
        viewModelScope.launch { onResult(runCatching { block() }) }
    }

    init { ApiClient.llmKey = llmKey; ApiClient.signupKey = signupKey }

    /** Store or clear it. Empty is the clear: no key means the deployment's,
     *  and there is no flag to leave switched on by mistake. */
    fun rememberLlmKey(key: String) {
        val trimmed = key.trim()
        llmKey = trimmed
        ApiClient.llmKey = trimmed
        prefs.edit().apply {
            if (trimmed.isEmpty()) remove("llmKey") else putString("llmKey", trimmed)
        }.apply()
    }

    /** The deployment invite key, same clearing rule: empty means none, and
     *  a deployment that never gated signup never needs one. */
    fun rememberSignupKey(key: String) {
        val trimmed = key.trim()
        signupKey = trimmed
        ApiClient.signupKey = trimmed
        prefs.edit().apply {
            if (trimmed.isEmpty()) remove("signupKey") else putString("signupKey", trimmed)
        }.apply()
    }
}
