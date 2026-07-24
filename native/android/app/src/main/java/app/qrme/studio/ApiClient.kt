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
data class Post(val id: String, val topic: String?, val content: String?, val status: String?,
                val provenance: Provenance? = null)
data class ProviderInfo(val name: String, val label: String, val configured: Boolean)
data class ModelChoice(val provider: String, val effective: String)
data class RobotSpec(val model: String, val label: String, val maker: String, val kind: String)
data class Robot(val id: String, val model: String, val name: String, val status: String?, val commands: List<String>)
data class CommandResult(val command: String, val status: String, val spoken: String?)
data class Objection(val id: String, val status: String, val reason: String?, val reattested: Int)
data class ChatMessage(val content: String?, val status: String, val flagReason: String?,
                       val provenance: Provenance? = null)
data class Provenance(val generatedBy: String, val sourceItems: Int,
                      val licensedFrom: String?, val moderationStatus: String,
                      val disclaimer: String)
data class LanguageInfo(val code: String, val label: String)
data class Excursion(val id: String, val topic: String, val redactions: Int,
                     val leftHost: Boolean, val findings: String, val learned: Boolean)
data class SocialConn(val id: String, val platform: String, val direction: String,
                      val handle: String?, val status: String?, val collected: Int,
                      val published: Int)
data class CatalogApp(val provider: String, val app: String, val label: String)
data class AppConn(val id: String, val provider: String, val app: String, val label: String,
                   val capabilities: List<String>, val status: String?)
data class InvokeResult(val capability: String, val status: String, val result: String)
data class ConnJoin(val status: String, val connectionId: String?, val matchedWith: String?)
data class ConnMsg(val id: String, val from: String, val content: String, val status: String?)
data class RoomCreated(val id: String, val topic: String, val channel: String)
data class RoomMsg(val id: String, val senderKind: String, val from: String,
                   val content: String?, val status: String?)
data class Beacon(val id: String, val label: String, val location: String?,
                  val scans: Int, val active: Boolean)
data class BeaconPlaced(val id: String, val label: String, val qrSvg: String)
data class SummonCard(val profileId: String, val displayName: String, val handle: String?,
                      val status: String, val note: String?)
data class SummonResult(val type: String, val label: String?, val scans: Int?,
                        val cards: List<SummonCard>)
data class Listing(val id: String, val kind: String, val title: String, val blurb: String?,
                   val tags: List<String>, val profileId: String?)
data class LicenseOffer(val kind: String, val price: Double, val currency: String,
                        val allowDerivatives: Boolean)
data class LicenseGrant(val id: String, val buyerId: String, val kind: String,
                        val derivedProfileId: String?, val revoked: Boolean)

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

    private fun provenanceOf(o: JSONObject?): Provenance? {
        if (o == null) return null
        val grounded = o.optJSONObject("grounded_in")
        val mod = o.optJSONObject("moderation")
        return Provenance(o.optString("generated_by", ""),
            grounded?.optInt("source_items") ?: 0,
            o.optString("licensed_from", null),
            mod?.optString("status", "") ?: "",
            o.optString("disclaimer", ""))
    }

    private fun post(o: JSONObject) = Post(
        o.getString("id"),
        o.optString("topic", null),
        if (o.isNull("content")) null else o.optString("content", null),
        o.optString("status", null),
        provenanceOf(o.optJSONObject("provenance")),
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
        val reply = JSONObject(request("/profiles/$id/chat", "POST",
            JSONObject().put("interactor_id", interactorId).put("message", message),
            token))
        val o = reply.getJSONObject("profile_message")
        return ChatMessage(
            if (o.isNull("content")) null else o.optString("content", null),
            o.optString("status", ""), o.optString("flag_reason", null),
            provenanceOf(reply.optJSONObject("provenance")))
    }

    // ---- language (the profile speaks it everywhere) ----

    suspend fun languages(): List<LanguageInfo> {
        val arr = JSONObject(request("/languages")).getJSONArray("languages")
        return (0 until arr.length()).map { i ->
            val o = arr.getJSONObject(i)
            LanguageInfo(o.getString("code"), o.getString("label"))
        }
    }

    suspend fun profileLanguage(id: String): String {
        return JSONObject(request("/profiles/$id/language")).getString("language")
    }

    suspend fun setLanguage(id: String, token: String, code: String) {
        request("/profiles/$id/language", "PUT",
            JSONObject().put("language", code), token)
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

    // ---- Community: stranger connections & multiparty rooms ----

    suspend fun joinQueue(interactorId: String, alias: String?): ConnJoin {
        val body = JSONObject().put("interactor_id", interactorId).put("tier", "friendly")
        if (!alias.isNullOrBlank()) body.put("alias", alias)
        val o = JSONObject(request("/connections/join", "POST", body))
        return ConnJoin(o.getString("status"), o.optString("connection_id", null),
            o.optString("matched_with", null))
    }

    suspend fun connectionMessages(cid: String, interactorId: String): List<ConnMsg> {
        val arr = JSONArray(request("/connections/$cid/messages?interactor_id=$interactorId"))
        return (0 until arr.length()).map { i ->
            val o = arr.getJSONObject(i)
            ConnMsg(o.getString("id"), o.optString("from", ""), o.optString("content", ""),
                o.optString("status", null))
        }
    }

    suspend fun sendConnectionMessage(cid: String, interactorId: String, message: String) {
        request("/connections/$cid/messages", "POST",
            JSONObject().put("interactor_id", interactorId).put("message", message))
    }

    suspend fun endConnection(cid: String, interactorId: String) {
        request("/connections/$cid/end?interactor_id=$interactorId", "POST")
    }

    private fun roomMsgOf(o: JSONObject) = RoomMsg(
        o.getString("id"), o.optString("sender_kind", ""), o.optString("from", ""),
        if (o.isNull("content")) null else o.optString("content", null),
        o.optString("status", null))

    suspend fun createRoom(topic: String, profileId: String, interactorId: String): RoomCreated {
        val body = JSONObject().put("topic", topic).put("channel", "chat")
            .put("participants", JSONArray()
                .put(JSONObject().put("kind", "user").put("id", interactorId))
                .put(JSONObject().put("kind", "profile").put("id", profileId)))
        val o = JSONObject(request("/rooms", "POST", body))
        return RoomCreated(o.getString("id"), o.optString("topic", ""), o.optString("channel", ""))
    }

    suspend fun roomMessage(roomId: String, senderId: String, message: String) {
        request("/rooms/$roomId/messages", "POST",
            JSONObject().put("sender_id", senderId).put("message", message))
    }

    suspend fun roomAdvance(roomId: String) {
        request("/rooms/$roomId/advance", "POST")
    }

    suspend fun roomTranscript(roomId: String): List<RoomMsg> {
        val arr = JSONArray(request("/rooms/$roomId/messages"))
        return (0 until arr.length()).map { roomMsgOf(arr.getJSONObject(it)) }
    }

    // ---- Reach: summon (@handle + beacons), marketplace, licensing ----

    suspend fun claimHandle(id: String, handle: String): String {
        val o = JSONObject(request("/profiles/$id/handle", "PUT",
            JSONObject().put("handle", handle)))
        return o.getString("handle")
    }

    suspend fun placeBeacon(id: String, label: String, location: String?): BeaconPlaced {
        val body = JSONObject().put("label", label)
        if (!location.isNullOrBlank()) body.put("location", location)
        val o = JSONObject(request("/profiles/$id/beacons", "POST", body))
        return BeaconPlaced(o.getString("id"), o.optString("label", ""),
            o.optString("qr_svg", ""))
    }

    suspend fun beacons(id: String): List<Beacon> {
        val arr = JSONArray(request("/profiles/$id/beacons"))
        return (0 until arr.length()).map { i ->
            val o = arr.getJSONObject(i)
            Beacon(o.getString("id"), o.optString("label", ""),
                o.optString("location", null), o.optInt("scans"),
                o.optBoolean("active"))
        }
    }

    suspend fun pickUpBeacon(bid: String) {
        request("/beacons/$bid", "DELETE")
    }

    private fun summonCardOf(o: JSONObject) = SummonCard(
        o.optString("profile_id", ""), o.optString("display_name", ""),
        o.optString("handle", null), o.optString("status", ""),
        o.optString("note", null))

    suspend fun summon(ref: String): SummonResult {
        val o = JSONObject(request("/summon?ref=" +
            java.net.URLEncoder.encode(ref, "UTF-8")))
        val cards = mutableListOf<SummonCard>()
        o.optJSONObject("profile")?.let { cards += summonCardOf(it) }
        o.optJSONArray("profiles")?.let { arr ->
            for (i in 0 until arr.length()) cards += summonCardOf(arr.getJSONObject(i))
        }
        return SummonResult(o.optString("type", ""), o.optString("label", null),
            if (o.has("scans")) o.optInt("scans") else null, cards)
    }

    suspend fun createListing(title: String, blurb: String?, tags: List<String>,
                              providerName: String, profileId: String) {
        val body = JSONObject().put("kind", "profile").put("title", title)
            .put("tags", JSONArray(tags)).put("provider_name", providerName)
            .put("profile_id", profileId)
        if (!blurb.isNullOrBlank()) body.put("blurb", blurb)
        request("/marketplace/listings", "POST", body)
    }

    suspend fun listings(tag: String?): List<Listing> {
        val path = if (tag.isNullOrBlank()) "/marketplace/listings"
        else "/marketplace/listings?tag=" + java.net.URLEncoder.encode(tag, "UTF-8")
        val arr = JSONArray(request(path))
        return (0 until arr.length()).map { i ->
            val o = arr.getJSONObject(i)
            val tagsArr = o.optJSONArray("tags")
            Listing(o.getString("id"), o.optString("kind", ""), o.optString("title", ""),
                o.optString("blurb", null),
                (0 until (tagsArr?.length() ?: 0)).map { tagsArr!!.getString(it) },
                o.optString("profile_id", null))
        }
    }

    suspend fun removeListing(lid: String) {
        request("/marketplace/listings/$lid", "DELETE")
    }

    private fun offerOf(o: JSONObject) = LicenseOffer(
        o.optString("kind", ""), o.optDouble("price", 0.0),
        o.optString("currency", "USD"), o.optBoolean("allow_derivatives"))

    suspend fun setLicense(id: String, token: String, kind: String,
                           price: Double, terms: String?): LicenseOffer {
        val body = JSONObject().put("kind", kind).put("price", price)
        if (!terms.isNullOrBlank()) body.put("terms", terms)
        return offerOf(JSONObject(request("/profiles/$id/license", "PUT", body, token)))
    }

    suspend fun license(id: String): LicenseOffer {
        return offerOf(JSONObject(request("/profiles/$id/license")))
    }

    suspend fun unlistLicense(id: String, token: String) {
        request("/profiles/$id/license", "DELETE", null, token)
    }

    suspend fun licenseGrants(id: String, token: String): List<LicenseGrant> {
        val arr = JSONArray(request("/profiles/$id/licenses", token = token))
        return (0 until arr.length()).map { i ->
            val o = arr.getJSONObject(i)
            LicenseGrant(o.getString("id"), o.optString("buyer_id", ""),
                o.optString("kind", ""), o.optString("derived_profile_id", null),
                o.optBoolean("revoked"))
        }
    }

    suspend fun revokeLicense(gid: String, token: String) {
        request("/licenses/$gid", "DELETE", null, token)
    }

    // ---- Connect: social platforms & the connected-apps catalog ----

    private fun socialConnOf(o: JSONObject) = SocialConn(
        o.getString("id"), o.optString("platform", ""), o.optString("direction", ""),
        o.optString("handle", null), o.optString("status", null),
        o.optInt("collected"), o.optInt("published"))

    suspend fun socialConnections(id: String, token: String): List<SocialConn> {
        val arr = JSONArray(request("/profiles/$id/social", token = token))
        return (0 until arr.length()).map { socialConnOf(arr.getJSONObject(it)) }
    }

    suspend fun socialConnect(id: String, token: String, platform: String,
                              direction: String, handle: String?): SocialConn {
        val body = JSONObject().put("platform", platform).put("direction", direction)
        if (!handle.isNullOrBlank()) body.put("handle", handle)
        return socialConnOf(JSONObject(request("/profiles/$id/social", "POST", body, token)))
    }

    suspend fun socialCollect(cid: String, token: String, content: String) {
        request("/social/$cid/collect", "POST",
            JSONObject().put("items", JSONArray().put(JSONObject().put("content", content))),
            token)
    }

    suspend fun socialPublish(cid: String, token: String, content: String) {
        request("/social/$cid/publish", "POST", JSONObject().put("content", content), token)
    }

    suspend fun revokeSocial(cid: String, token: String) {
        request("/social/$cid", "DELETE", null, token)
    }

    suspend fun appsCatalog(): List<CatalogApp> {
        val providers = JSONObject(request("/connectors/catalog")).getJSONArray("providers")
        val out = mutableListOf<CatalogApp>()
        for (i in 0 until providers.length()) {
            val p = providers.getJSONObject(i)
            val apps = p.getJSONArray("apps")
            for (j in 0 until apps.length()) {
                val a = apps.getJSONObject(j)
                out += CatalogApp(p.getString("provider"), a.getString("app"), a.getString("label"))
            }
        }
        return out
    }

    private fun appConnOf(o: JSONObject): AppConn {
        val caps = o.optJSONArray("capabilities")
        return AppConn(
            o.getString("id"), o.optString("provider", ""), o.optString("app", ""),
            o.optString("label", ""),
            (0 until (caps?.length() ?: 0)).map { caps!!.getString(it) },
            o.optString("status", null))
    }

    suspend fun appConnections(id: String, token: String): List<AppConn> {
        val arr = JSONArray(request("/profiles/$id/apps", token = token))
        return (0 until arr.length()).map { appConnOf(arr.getJSONObject(it)) }
    }

    suspend fun appConnect(id: String, token: String, provider: String, app: String): AppConn {
        return appConnOf(JSONObject(request("/profiles/$id/apps", "POST",
            JSONObject().put("provider", provider).put("app", app), token)))
    }

    suspend fun appCollect(cid: String, token: String, content: String) {
        request("/apps/$cid/collect", "POST",
            JSONObject().put("items", JSONArray().put(JSONObject().put("content", content))),
            token)
    }

    suspend fun appInvoke(cid: String, token: String, capability: String): InvokeResult {
        val o = JSONObject(request("/apps/$cid/invoke", "POST",
            JSONObject().put("capability", capability), token))
        return InvokeResult(o.optString("capability", ""), o.optString("status", ""),
            o.optString("result", ""))
    }
}
