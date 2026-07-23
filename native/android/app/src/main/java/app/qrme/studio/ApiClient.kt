package app.qrme.studio

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

// MARK: wire models (mirror qrme/models.py + routers)

data class ProfileCreated(val id: String, val displayName: String, val kind: String, val ownerToken: String)
data class ProfileCard(val id: String, val displayName: String, val kind: String, val status: String?)
data class Post(val id: String, val topic: String?, val content: String, val status: String?)
data class ProviderInfo(val name: String, val label: String, val configured: Boolean)
data class ModelChoice(val provider: String, val effective: String)
data class RobotSpec(val model: String, val label: String, val maker: String, val kind: String)
data class Robot(val id: String, val model: String, val name: String, val status: String?, val commands: List<String>)
data class CommandResult(val command: String, val status: String, val spoken: String?)
data class Objection(val id: String, val status: String, val reason: String?, val reattested: Int)
data class ChatMessage(val content: String?, val status: String, val flagReason: String?)
data class Excursion(val id: String, val topic: String, val redactions: Int,
                     val leftHost: Boolean, val findings: String, val learned: Boolean)

class ApiException(message: String) : Exception(message)

/**
 * Coroutine client for the QRME backend.
 *
 * The Android emulator reaches the host machine at 10.0.2.2, so that is the
 * default. On a physical device, set your machine's LAN IP via [base].
 */
object ApiClient {
    @Volatile var base: String = "http://10.0.2.2:8000"

    private suspend fun request(
        path: String, method: String = "GET",
        body: JSONObject? = null, token: String? = null,
    ): String = withContext(Dispatchers.IO) {
        val conn = (URL(base + path).openConnection() as HttpURLConnection).apply {
            requestMethod = method
            setRequestProperty("content-type", "application/json")
            token?.let { setRequestProperty("authorization", "Bearer $it") }
            connectTimeout = 8000; readTimeout = 8000
            if (body != null) {
                doOutput = true
                outputStream.use { it.write(body.toString().toByteArray()) }
            }
        }
        val code = conn.responseCode
        val text = (if (code in 200..299) conn.inputStream else conn.errorStream)
            ?.bufferedReader()?.use { it.readText() } ?: ""
        conn.disconnect()
        if (code !in 200..299) {
            val detail = runCatching { JSONObject(text).optString("detail") }.getOrNull()
            throw ApiException(if (detail.isNullOrBlank()) "HTTP $code" else detail)
        }
        text
    }

    private fun post(o: JSONObject) = Post(
        o.getString("id"),
        o.optString("topic", null),
        o.optString("content", ""),
        o.optString("status", null),
    )

    suspend fun createProfile(name: String, persona: String, kind: String, birthdate: String): ProfileCreated {
        val body = JSONObject()
            .put("owner_id", "owner-1")
            .put("kind", kind)
            .put("display_name", name)
            .put("persona", persona)
            .put("demographics", JSONObject().put("language", "en"))
            .put("verification", JSONObject().put("birthdate", birthdate))
        val o = JSONObject(request("/profiles", "POST", body))
        return ProfileCreated(o.getString("id"), o.getString("display_name"),
            o.getString("kind"), o.getString("owner_token"))
    }

    suspend fun profile(id: String): ProfileCard {
        val o = JSONObject(request("/profiles/$id"))
        return ProfileCard(o.getString("id"), o.getString("display_name"),
            o.getString("kind"), o.optString("status", null))
    }

    suspend fun compose(id: String, token: String, topic: String): Post {
        val o = JSONObject(request("/profiles/$id/compose", "POST",
            JSONObject().put("topic", topic), token))
        return post(o)
    }

    suspend fun posts(id: String): List<Post> {
        val arr = JSONArray(request("/profiles/$id/posts"))
        return (0 until arr.length()).map { post(arr.getJSONObject(it)) }
    }

    // ---- model selection ----

    suspend fun models(): List<ProviderInfo> {
        val arr = JSONObject(request("/models")).getJSONArray("providers")
        return (0 until arr.length()).map { i ->
            val o = arr.getJSONObject(i)
            ProviderInfo(o.getString("name"), o.getString("label"), o.optBoolean("configured"))
        }
    }

    suspend fun profileModel(id: String): ModelChoice {
        val o = JSONObject(request("/profiles/$id/model"))
        return ModelChoice(o.getString("provider"), o.getString("effective"))
    }

    suspend fun setModel(id: String, token: String, provider: String): ModelChoice {
        val o = JSONObject(request("/profiles/$id/model", "PUT",
            JSONObject().put("provider", provider), token))
        return ModelChoice(o.getString("provider"), o.getString("effective"))
    }

    // ---- robotic embodiment ----

    private fun robot(o: JSONObject): Robot {
        val cmds = o.optJSONArray("commands")
        return Robot(o.getString("id"), o.optString("model", ""),
            o.optString("name", ""), o.optString("status", null),
            (0 until (cmds?.length() ?: 0)).map { cmds!!.getString(it) })
    }

    suspend fun roboticsCatalog(): List<RobotSpec> {
        val arr = JSONObject(request("/robotics/catalog")).getJSONArray("robots")
        return (0 until arr.length()).map { i ->
            val o = arr.getJSONObject(i)
            RobotSpec(o.getString("model"), o.getString("label"),
                o.getString("maker"), o.getString("kind"))
        }
    }

    suspend fun robots(id: String, token: String): List<Robot> {
        val arr = JSONArray(request("/profiles/$id/robots", token = token))
        return (0 until arr.length()).map { robot(arr.getJSONObject(it)) }
    }

    suspend fun bindRobot(id: String, token: String, model: String): Robot {
        return robot(JSONObject(request("/profiles/$id/robots", "POST",
            JSONObject().put("model", model), token)))
    }

    suspend fun commandRobot(rid: String, token: String, command: String, arg: String?): CommandResult {
        val body = JSONObject().put("command", command)
        if (!arg.isNullOrBlank()) body.put("arg", arg)
        val o = JSONObject(request("/robots/$rid/command", "POST", body, token))
        return CommandResult(o.getString("command"), o.optString("status", ""),
            o.optString("spoken", null))
    }

    // ---- objections (governance) ----

    suspend fun objections(id: String, token: String): List<Objection> {
        val arr = JSONArray(request("/profiles/$id/objections", token = token))
        return (0 until arr.length()).map { i ->
            val o = arr.getJSONObject(i)
            Objection(o.getString("id"), o.optString("status", ""),
                o.optString("reason", null), o.optInt("reattested"))
        }
    }

    suspend fun attest(id: String, objectionId: String, token: String) {
        request("/profiles/$id/objections/$objectionId/attest", "POST", null, token)
    }

    // ---- chat (the core loop) ----

    suspend fun createInteractor(name: String): String {
        val o = JSONObject(request("/interactors", "POST",
            JSONObject().put("display_name", name)))
        return o.getString("id")
    }

    suspend fun chat(id: String, token: String, interactorId: String,
                     message: String): ChatMessage {
        val o = JSONObject(request("/profiles/$id/chat", "POST",
            JSONObject().put("interactor_id", interactorId).put("message", message),
            token)).getJSONObject("profile_message")
        return ChatMessage(
            if (o.isNull("content")) null else o.optString("content", null),
            o.optString("status", ""), o.optString("flag_reason", null))
    }

    // ---- knowledge excursions (study safely; private data stays home) ----

    private fun excursionOf(o: JSONObject) = Excursion(
        o.getString("id"), o.optString("topic", ""), o.optInt("redactions"),
        o.optBoolean("left_host"), o.optString("findings", ""),
        o.optBoolean("learned"))

    suspend fun excursions(id: String, token: String): List<Excursion> {
        val arr = JSONArray(request("/profiles/$id/excursions", token = token))
        return (0 until arr.length()).map { excursionOf(arr.getJSONObject(it)) }
    }

    suspend fun startExcursion(id: String, token: String, topic: String,
                               question: String): Excursion {
        return excursionOf(JSONObject(request("/profiles/$id/excursions", "POST",
            JSONObject().put("topic", topic).put("question", question), token)))
    }

    suspend fun learn(cid: String, token: String) {
        request("/excursions/$cid/learn", "POST", null, token)
    }
}
