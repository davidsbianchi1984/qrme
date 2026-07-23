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
    var interactorId by mutableStateOf<String?>(prefs.getString("interactor", null))
        private set

    val isSignedIn get() = pid != null && token != null

    fun rememberInteractor(id: String) {
        interactorId = id
        prefs.edit().putString("interactor", id).apply()
    }

    fun createProfile(
        name: String, persona: String, kind: String, birthdate: String,
        onError: (String) -> Unit, onBusy: (Boolean) -> Unit,
    ) {
        onBusy(true)
        viewModelScope.launch {
            runCatching { ApiClient.createProfile(name, persona, kind, birthdate) }
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
        prefs.edit().clear().apply()
    }

    fun <T> call(block: suspend () -> T, onResult: (Result<T>) -> Unit) {
        viewModelScope.launch { onResult(runCatching { block() }) }
    }
}
