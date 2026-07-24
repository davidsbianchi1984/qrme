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
        private set
    var interactorVerified by mutableStateOf(prefs.getBoolean("interactor_adult", false))
        private set

    val isSignedIn get() = pid != null && token != null

    fun rememberInteractor(id: String, adult: Boolean = false) {
        interactorId = id
        interactorVerified = adult
        prefs.edit().putString("interactor", id)
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
                .onFailure { onError(it.message ?: "Couldn't reach QRME — is the backend running?") }
            onBusy(false)
        }
    }

    fun signOut() {
        pid = null; token = null; displayName = ""
        interactorId = null; interactorVerified = false
        prefs.edit().clear().apply()
    }

    fun <T> call(block: suspend () -> T, onResult: (Result<T>) -> Unit) {
        viewModelScope.launch { onResult(runCatching { block() }) }
    }
}
