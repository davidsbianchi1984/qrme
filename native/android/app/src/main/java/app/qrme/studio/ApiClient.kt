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
                val provenance: Provenance? = null, val watermarkLine: String? = null)
data class ProviderInfo(val name: String, val label: String, val configured: Boolean)
data class ModelChoice(val provider: String, val effective: String)
data class WatermarkDesign(val mark: String, val label: String, val line: String, val custom: Boolean)
data class RobotSpec(val model: String, val label: String, val maker: String, val kind: String)
data class Robot(val id: String, val model: String, val name: String, val status: String?, val commands: List<String>)
data class CommandResult(val command: String, val status: String, val spoken: String?)
data class Objection(val id: String, val status: String, val reason: String?, val reattested: Int)
data class ChatMessage(val content: String?, val status: String, val flagReason: String?,
                       val provenance: Provenance? = null, val watermarkLine: String? = null,
                       // Spec clauses 2/12: which way the profile worked, and
                       // whether the owner declared it or the wording implied it.
                       val role: String? = null, val roleHow: String? = null)
/** Extract and reconstruct: whose work is this, from the text alone. */
data class WatermarkRecovery(val recovered: Boolean, val reason: String?,
                             val profileId: String?, val verbatim: Boolean,
                             val similarity: Double, val matchedWindows: Int,
                             val storedWindows: Int, val state: String?,
                             val bestSimilarity: Double?, val threshold: Double?,
                             val markLine: String?, val disclosure: String?,
                             val method: String?)
data class Provenance(val generatedBy: String, val sourceItems: Int,
                      val licensedFrom: String?, val moderationStatus: String,
                      val disclaimer: String)
data class LanguageInfo(val code: String, val label: String)
data class FeedbackItem(val category: String, val message: String, val status: String)
data class FeedbackState(val mine: List<FeedbackItem>, val tally: Map<String, Int>, val total: Int)
data class SteeringDial(val name: String, val group: String, val label: String,
                        val low: String, val high: String, val min: Int, val max: Int)
data class SteeringHubState(val dials: List<SteeringDial>, val values: Map<String, Int>,
                            val baseAge: Int?, val agingEnabled: Boolean,
                            val effectiveAge: Int?, val appearance: String?)
data class LedgerEntry(val id: String, val kind: String, val memo: String?,
                       val amount: Double, val status: String)
data class EarningsStatement(val entries: List<LedgerEntry>, val accrued: Double,
                             val paid: Double, val lifetime: Double,
                             val byKind: Map<String, Double>, val currency: String)
data class PayoutReceipt(val payoutId: String, val total: Double, val entries: Int)
data class VoiceConsentState(val granted: Boolean, val sources: List<String>,
                            val grantedAt: String?)
data class VoiceEnrollment(val samples: Int, val seconds: Double, val turns: Int,
                           val meanTurnSeconds: Double?, val ready: Boolean,
                           val needs: List<String>, val wantSamples: Int,
                           val wantSeconds: Double, val method: String)
data class VoiceprintRecord(val id: String, val builtAt: String?, val active: Boolean)
data class VoiceprintStatus(val consent: VoiceConsentState,
                            val enrollment: VoiceEnrollment?,
                            val voiceprint: VoiceprintRecord?,
                            val disclosure: String)
data class VoiceSpoken(val basis: String, val disclosure: String)
data class VoiceRevocation(val samplesDeleted: Int, val note: String)
data class TranslateResult(val translation: String, val engine: String, val note: String?)
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
// Live desks — a real person, so never an AI watermark.
data class DeskFeed(val url: String, val live: Boolean, val note: String)
data class DeskAttestation(val attestor: String, val basis: String,
                           val signed: Boolean, val note: String)
// `ageWall` true means an 18+ stream seen without a verified-adult token:
// existence and nothing else, so the rest of the fields are absent.
data class DeskCard(val deskId: String, val displayName: String,
                    val trade: String, val location: String?,
                    val blurb: String?, val presence: String,
                    val human: Boolean, val ai: Boolean,
                    val designation: String, val attestation: DeskAttestation?,
                    val portrait: String?, val feed: DeskFeed?,
                    val bellAvailable: Boolean, val waiting: Int,
                    val rated: Boolean, val ageWall: Boolean, val note: String?)
data class InteractorCreated(val id: String, val token: String?)
data class StreamJoin(val roomId: String, val channel: String,
                      val presence: String, val ai: Boolean, val note: String)
data class RingReceipt(val ringId: String, val waiting: Int,
                       val presence: String, val note: String)

// Signatures (docs/signatures.md).
data class EnrollOptions(val challenge: String, val rpId: String,
                         val rpName: String, val userId: String,
                         val userName: String, val displayName: String)
data class SigningCredential(val id: String, val credentialId: String,
                             val proofingLevel: String, val displayName: String?,
                             val deviceBound: Boolean, val canSign: List<String>)
data class SignatureEnvelope(val envelopeId: String, val challenge: String,
                             val displayText: String, val meaning: String,
                             val tier: String)
data class SignatureReceipt(val signatureId: String, val signedAt: String,
                            val valid: Boolean, val limits: List<String>)

// What the in-camera overlay draws. Mirrors GET /b/{id}/card, and carries the
// AI watermark in the same payload as the face so the two cannot come apart.
data class BeaconCard(val profileId: String, val displayName: String,
                      val watermark: String, val initials: String,
                      val portrait: String?, val label: String?,
                      val sharedRoom: Boolean, val openUrl: String?,
                      val ageWall: Boolean)
data class SummonCard(val profileId: String, val displayName: String, val handle: String?,
                      val status: String, val note: String?)
data class SummonResult(val type: String, val label: String?, val scans: Int?,
                        val cards: List<SummonCard>)
data class Pack(val id: String, val industry: String, val audience: String,
                val title: String,
                val blurb: String?, val publisher: String, val price: Double,
                val currency: String, val free: Boolean, val origin: String,
                val originUrl: String?, val items: Int,
                val installs: Int)
data class PackRegistry(val key: String, val name: String, val url: String,
                        val audience: String, val tagline: String,
                        val available: Int, val synced: Int)
data class InstalledPack(val id: String, val title: String, val pricePaid: Double,
                         val robotId: String)
data class GameSession(val id: String, val platform: String, val game: String,
                       val role: String, val status: String, val callouts: Int)
data class GameCalloutResult(val status: String, val line: String?,
                             val flagReason: String?)
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
        val code = try {
            conn.responseCode
        } catch (e: Exception) {
            // Never reached a server. Recorded as status 0; the thrown error
            // still carries its message to the person, who owns it.
            Problems.record(method, path, 0)
            throw e
        }
        val text = (if (code in 200..299) conn.inputStream else conn.errorStream)
            ?.bufferedReader()?.use { it.readText() } ?: ""
        conn.disconnect()
        if (code !in 200..299) {
            // The status and the operation, never the detail below: these
            // messages quote what the person typed, which is theirs to read
            // and nobody's to keep.
            Problems.record(method, path, code)
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
        watermarkLineOf(o.optJSONObject("watermark")),
    )

    // The always-displayed watermark line riding on an AI render.
    private fun watermarkLineOf(o: JSONObject?): String? =
        o?.optJSONObject("display")?.optString("line", null)

    suspend fun createProfile(name: String, persona: String, kind: String, birthdate: String,
                              language: String? = null): ProfileCreated {
        val body = JSONObject()
            .put("owner_id", "owner-1")
            .put("kind", kind)
            .put("display_name", name)
            .put("persona", persona)
            .put("verification", JSONObject().put("birthdate", birthdate))
            .put("terms_consent", true)   // clickwrap: the Welcome screen displays the Terms
        if (!language.isNullOrBlank() && language != "en") body.put("language", language)
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

    // ---- watermark (the mark every AI render carries) ----

    private fun design(o: JSONObject) = WatermarkDesign(
        o.optString("mark", "\u2726"), o.optString("label", ""),
        o.optString("line", ""), o.optBoolean("custom"))

    suspend fun watermarkDesign(id: String): WatermarkDesign =
        design(JSONObject(request("/profiles/$id/watermark")))

    // Design the profile's watermark; the AI designation is invariant.
    suspend fun setWatermarkDesign(id: String, token: String, mark: String?,
                                   label: String?): WatermarkDesign {
        val body = JSONObject()
        if (!mark.isNullOrBlank()) body.put("mark", mark)
        if (!label.isNullOrBlank()) body.put("label", label)
        return design(JSONObject(request("/profiles/$id/watermark", "PUT", body, token)))
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

    /**
     * Mint an interactor identity. Returns the token as well as the id,
     * because every age-gated surface checks the *token's* verified birthdate
     * server-side — an id on its own opens nothing, which is the point.
     */
    suspend fun createInteractor(name: String,
                                 birthdate: String? = null): InteractorCreated {
        val body = JSONObject().put("display_name", name)
        if (!birthdate.isNullOrBlank()) body.put("birthdate", birthdate)
        val o = JSONObject(request("/interactors", "POST", body))
        return InteractorCreated(o.getString("id"),
            if (o.isNull("token")) null else o.optString("token"))
    }

    // ---- steering: the owner shapes how the profile comes across ----

    suspend fun steeringHub(id: String, token: String): SteeringHubState {
        val o = JSONObject(request("/profiles/$id/steering/hub", token = token))
        val dialArr = o.getJSONArray("dials")
        val dials = (0 until dialArr.length()).map { i ->
            val d = dialArr.getJSONObject(i)
            SteeringDial(d.getString("name"), d.getString("group"),
                d.getString("label"), d.optString("low", ""),
                d.optString("high", ""), d.optInt("min"), d.optInt("max", 100))
        }
        val valuesObj = o.optJSONObject("values") ?: JSONObject()
        val values = valuesObj.keys().asSequence()
            .associateWith { valuesObj.optInt(it) }
        val age = o.optJSONObject("age") ?: JSONObject()
        val appearance = o.optJSONObject("appearance") ?: JSONObject()
        return SteeringHubState(
            dials, values,
            if (age.isNull("base_age")) null else age.optInt("base_age"),
            age.optBoolean("aging_enabled"),
            if (age.isNull("effective_age")) null else age.optInt("effective_age"),
            if (appearance.isNull("description")) null
            else appearance.optString("description", null))
    }

    suspend fun setSteeringHub(id: String, token: String,
                               values: Map<String, Int>? = null,
                               baseAge: Int? = null, agingEnabled: Boolean? = null,
                               appearance: String? = null): SteeringHubState {
        val body = JSONObject()
        if (values != null) {
            val v = JSONObject(); values.forEach { (k, n) -> v.put(k, n) }
            body.put("values", v)
        }
        if (baseAge != null || agingEnabled != null) {
            val age = JSONObject()
            if (baseAge != null) age.put("base_age", baseAge)
            if (agingEnabled != null) age.put("aging_enabled", agingEnabled)
            body.put("age", age)
        }
        if (appearance != null)
            body.put("appearance", JSONObject().put("description", appearance))
        request("/profiles/$id/steering/hub", "PUT", body, token)
        return steeringHub(id, token)
    }

    // ---- earnings: the creator's statement over the ledger ----

    suspend fun earnings(id: String, token: String): EarningsStatement {
        val o = JSONObject(request("/profiles/$id/earnings", token = token))
        val arr = o.optJSONArray("entries")
        val entries = (0 until (arr?.length() ?: 0)).map { i ->
            val e = arr!!.getJSONObject(i)
            LedgerEntry(e.getString("id"), e.optString("kind", ""),
                e.optString("memo", null), e.optDouble("amount"),
                e.optString("status", ""))
        }
        val t = o.getJSONObject("totals")
        val byKindObj = t.optJSONObject("by_kind") ?: JSONObject()
        val byKind = byKindObj.keys().asSequence()
            .associateWith { byKindObj.optDouble(it) }
        return EarningsStatement(entries, t.optDouble("accrued"),
            t.optDouble("paid"), t.optDouble("lifetime"), byKind,
            o.optString("currency", "USD"))
    }

    suspend fun requestPayout(id: String, token: String): PayoutReceipt {
        val o = JSONObject(request("/profiles/$id/earnings/payout", "POST",
            JSONObject(), token))
        return PayoutReceipt(o.getString("payout_id"), o.optDouble("total"),
            o.optInt("entries"))
    }

    // ---- relationship: how the profile relates to you ----

    suspend fun setRelationship(id: String, token: String, interactorId: String,
                                type: String, nickname: String?,
                                tone: String?): String {
        val body = JSONObject().put("relationship_type", type)
        if (!nickname.isNullOrBlank()) body.put("nickname", nickname)
        if (!tone.isNullOrBlank()) body.put("tone", tone)
        val o = JSONObject(request("/profiles/$id/relationships/$interactorId",
            "PUT", body, token))
        return o.optString("relationship_type", type)
    }

    /**
     * `role` is optional on purpose: left null the profile reads the wording and
     * decides for itself, and the reply reports which way it went.
     */
    suspend fun chat(id: String, token: String, interactorId: String,
                     message: String, role: String? = null): ChatMessage {
        val body = JSONObject().put("interactor_id", interactorId)
            .put("message", message)
        if (!role.isNullOrBlank()) body.put("role", role)
        val reply = JSONObject(request("/profiles/$id/chat", "POST", body, token))
        val o = reply.getJSONObject("profile_message")
        val rc = reply.optJSONObject("role_context")
        return ChatMessage(
            if (o.isNull("content")) null else o.optString("content", null),
            o.optString("status", ""), o.optString("flag_reason", null),
            provenanceOf(reply.optJSONObject("provenance")),
            watermarkLineOf(o.optJSONObject("watermark")),
            rc?.optString("role"), rc?.optString("how"))
    }

    /**
     * Whose work is this, from the text alone — no credential id, and it keeps
     * answering after the text has been edited. Public: a counterparty must be
     * able to ask without an account here.
     */
    suspend fun recoverWatermark(content: String): WatermarkRecovery {
        val o = JSONObject(request("/watermarks/recover", "POST",
            JSONObject().put("content", content)))
        val display = o.optJSONObject("display")
        return WatermarkRecovery(
            o.optBoolean("recovered"),
            if (o.isNull("reason")) null else o.optString("reason"),
            if (o.isNull("profile_id")) null else o.optString("profile_id"),
            o.optBoolean("verbatim"), o.optDouble("similarity", 0.0),
            o.optInt("matched_windows"), o.optInt("stored_windows"),
            if (o.isNull("state")) null else o.optString("state"),
            if (o.isNull("best_similarity")) null else o.optDouble("best_similarity"),
            if (o.isNull("threshold")) null else o.optDouble("threshold"),
            if (display == null || display.isNull("line")) null else display.optString("line"),
            if (o.isNull("disclosure")) null else o.optString("disclosure"),
            if (o.isNull("method")) null else o.optString("method"))
    }

    // ---- language (the profile speaks it everywhere) ----

    suspend fun languages(): List<LanguageInfo> {
        val arr = JSONObject(request("/languages")).getJSONArray("languages")
        return (0 until arr.length()).map { i ->
            val o = arr.getJSONObject(i)
            LanguageInfo(o.getString("code"), o.getString("label"))
        }
    }

    suspend fun profileLanguage(id: String): Pair<String, String> {
        val o = JSONObject(request("/profiles/$id/language"))
        return o.getString("language") to o.optString("mode", "pre")
    }

    suspend fun setLanguage(id: String, token: String, code: String,
                            mode: String = "pre") {
        request("/profiles/$id/language", "PUT",
            JSONObject().put("language", code).put("mode", mode), token)
    }

    suspend fun submitFeedback(token: String?, category: String,
                               message: String, rating: Int?): String {
        val body = JSONObject().put("category", category).put("message", message)
        rating?.let { body.put("rating", it) }
        return JSONObject(request("/feedback", "POST", body, token))
            .optString("status", "received")
    }

    suspend fun feedback(token: String?): FeedbackState {
        val o = JSONObject(request("/feedback", token = token))
        val mineArr = o.optJSONArray("mine")
        val mine = (0 until (mineArr?.length() ?: 0)).map { i ->
            val f = mineArr!!.getJSONObject(i)
            FeedbackItem(f.optString("category", ""), f.optString("message", ""),
                f.optString("status", ""))
        }
        val t = o.optJSONObject("tally")
        val tally = listOf("idea", "improvement", "bug", "praise", "other")
            .associateWith { t?.optInt(it, 0) ?: 0 }
        return FeedbackState(mine, tally, o.optInt("total"))
    }

    suspend fun translate(id: String, token: String, text: String): TranslateResult {
        val o = JSONObject(request("/profiles/$id/translate", "POST",
            JSONObject().put("text", text), token))
        return TranslateResult(o.optString("translation", ""),
            o.optString("engine", ""), o.optString("note", null))
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

    suspend fun joinQueue(interactorId: String, alias: String?,
                          tier: String = "friendly"): ConnJoin {
        val body = JSONObject().put("interactor_id", interactorId).put("tier", tier)
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

    /**
     * The compact card behind a scanned beacon. Public — a scan carries no
     * token, exactly like the printed sticker it came from.
     *
     * A rated beacon answers `age_wall` alone: no name, no portrait. The
     * overlay renders whatever comes back, so the withholding happens at the
     * source rather than being trusted to this client.
     */
    suspend fun beaconCard(bid: String): BeaconCard {
        val o = JSONObject(request("/b/$bid/card"))
        return BeaconCard(
            o.optString("profile_id", bid),
            o.optString("display_name", ""),
            o.optString("watermark", ""),
            o.optString("initials", ""),
            if (o.isNull("portrait")) null else o.optString("portrait", null),
            if (o.isNull("label")) null else o.optString("label", null),
            !o.isNull("shared_room"),
            if (o.isNull("open_url")) null else o.optString("open_url", null),
            o.optBoolean("age_wall", false))
    }

    // ---- live desks ----

    /**
     * A desk card. Past an 18+ age wall most of the payload is absent, so
     * every nested object is read optionally rather than demanded — the wall
     * is a normal response, not an error.
     */
    suspend fun desk(id: String, token: String? = null): DeskCard {
        val o = JSONObject(request("/desks/$id", token = token))
        val f = o.optJSONObject("feed")
        val a = o.optJSONObject("attestation")
        val bell = o.optJSONObject("bell")
        return DeskCard(
            o.getString("desk_id"), o.optString("display_name", ""),
            o.optString("trade", ""),
            if (o.isNull("location")) null else o.optString("location"),
            if (o.isNull("blurb")) null else o.optString("blurb"),
            o.optString("presence", "away"), o.optBoolean("human"),
            o.optBoolean("ai"), o.optString("designation", ""),
            a?.let {
                DeskAttestation(it.optString("attestor", ""),
                    it.optString("basis", ""), it.optBoolean("signed"),
                    it.optString("note", ""))
            },
            if (o.isNull("portrait")) null else o.optString("portrait"),
            f?.let {
                DeskFeed(it.getString("url"), it.optBoolean("live"),
                    it.optString("note", ""))
            },
            bell?.optBoolean("available") ?: false,
            bell?.optInt("waiting") ?: 0,
            o.optBoolean("rated"), o.optBoolean("age_wall"),
            if (o.isNull("note")) null else o.optString("note"))
    }

    /** Join the live stream — the room whoever is watching shares. */
    suspend fun joinStream(deskId: String, token: String? = null): StreamJoin {
        val o = JSONObject(request("/desks/$deskId/join", "POST", null, token))
        return StreamJoin(o.getString("room_id"), o.optString("channel", "video"),
            o.optString("presence", ""), o.optBoolean("ai"),
            o.optString("note", ""))
    }

    /**
     * Ring the bell at an unattended desk. No token: the visitor standing in
     * front of an empty chair is exactly the person who has no account.
     */
    suspend fun ringBell(deskId: String, callerId: String? = null,
                         note: String? = null,
                         token: String? = null): RingReceipt {
        val body = JSONObject()
        if (callerId != null) body.put("caller_id", callerId)
        if (note != null) body.put("note", note)
        val o = JSONObject(request("/desks/$deskId/bell", "POST", body, token))
        return RingReceipt(o.getString("ring_id"), o.optInt("waiting"),
            o.optString("presence", ""), o.optString("note", ""))
    }

    // ---- signatures ----

    suspend fun enrollOptions(displayName: String, token: String): EnrollOptions {
        val o = JSONObject(request("/signatures/enroll/options", "POST",
            JSONObject().put("display_name", displayName), token))
        val rp = o.getJSONObject("rp")
        val user = o.getJSONObject("user")
        return EnrollOptions(o.getString("challenge"), rp.getString("id"),
            rp.optString("name", "QRME"), user.getString("id"),
            user.getString("name"), user.getString("displayName"))
    }

    suspend fun enrollCredential(credentialId: String, attestationObject: String,
                                 clientDataJson: String, challenge: String,
                                 proofingLevel: String, displayName: String,
                                 token: String): SigningCredential {
        val body = JSONObject()
            .put("credential_id", credentialId)
            .put("attestation_object", attestationObject)
            .put("client_data_json", clientDataJson)
            .put("challenge", challenge)
            .put("proofing_level", proofingLevel)
            .put("display_name", displayName)
        return signingCredential(JSONObject(
            request("/signatures/enroll", "POST", body, token)))
    }

    private fun signingCredential(o: JSONObject): SigningCredential {
        val tiers = o.optJSONArray("can_sign")
        return SigningCredential(
            o.getString("id"), o.getString("credential_id"),
            o.optString("proofing_level", ""),
            if (o.isNull("display_name")) null else o.optString("display_name"),
            o.optBoolean("device_bound"),
            (0 until (tiers?.length() ?: 0)).map { tiers!!.getString(it) })
    }

    suspend fun signingCredentials(token: String): List<SigningCredential> {
        val arr = JSONObject(request("/signatures/credentials", token = token))
            .getJSONArray("credentials")
        return (0 until arr.length()).map { signingCredential(arr.getJSONObject(it)) }
    }

    suspend fun requestSignature(document: String, meaning: String,
                                 displayText: String, tier: String,
                                 bindingKind: String?, bindingRef: String?,
                                 token: String): SignatureEnvelope {
        val body = JSONObject()
            .put("document", document).put("meaning", meaning)
            .put("display_text", displayText).put("tier", tier)
        if (bindingKind != null) body.put("binding_kind", bindingKind)
        if (bindingRef != null) body.put("binding_ref", bindingRef)
        val o = JSONObject(request("/signatures/request", "POST", body, token))
        return SignatureEnvelope(o.getString("envelope_id"),
            o.getString("challenge"), o.getString("display_text"),
            o.getString("meaning"), o.getString("tier"))
    }

    suspend fun submitSignature(envelopeId: String, a: Signing.Assertion,
                                token: String): SignatureReceipt {
        val body = JSONObject()
            .put("envelope_id", envelopeId)
            .put("credential_id", a.credentialId)
            .put("signature", a.signature)
            .put("authenticator_data", a.authenticatorData)
            .put("client_data_json", a.clientDataJson)
            // Android exposes a platform authenticator, so the ceremony
            // happens on this device rather than through a second one.
            .put("transport", "internal")
            .put("platform", Signing.PLATFORM)
        val o = JSONObject(request("/signatures/sign", "POST", body, token))
        val limits = o.optJSONArray("limits")
        return SignatureReceipt(
            o.getString("signature_id"), o.getString("signed_at"),
            o.getJSONObject("verification").optBoolean("valid"),
            (0 until (limits?.length() ?: 0)).map { limits!!.getString(it) })
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

    // ---- knowledge packs: buy/download expertise for the profile ----

    suspend fun packs(industry: String?): List<Pack> {
        val path = if (industry.isNullOrBlank()) "/packs"
        else "/packs?industry=" + java.net.URLEncoder.encode(industry, "UTF-8")
        val arr = JSONArray(request(path))
        return (0 until arr.length()).map { i ->
            val o = arr.getJSONObject(i)
            Pack(o.getString("id"), o.optString("industry", ""),
                o.optString("audience", "profile"),
                o.optString("title", ""), o.optString("blurb", null),
                o.optString("publisher", ""), o.optDouble("price", 0.0),
                o.optString("currency", "USD"), o.optBoolean("free"),
                o.optString("origin", "local"), o.optString("origin_url", null),
                o.optInt("items"), o.optInt("installs"))
        }
    }

    suspend fun packRegistries(): List<PackRegistry> {
        val arr = JSONArray(request("/packs/registries"))
        return (0 until arr.length()).map { i ->
            val o = arr.getJSONObject(i)
            PackRegistry(o.getString("key"), o.optString("name", ""),
                o.optString("url", ""), o.optString("audience", ""),
                o.optString("tagline", ""), o.optInt("available"),
                o.optInt("synced"))
        }
    }

    suspend fun syncRegistry(key: String) {
        request("/packs/registries/$key/sync", "POST")
    }

    suspend fun installedPacks(pid: String, token: String): List<InstalledPack> {
        val arr = JSONArray(request("/profiles/$pid/packs", token = token))
        return (0 until arr.length()).map { i ->
            val o = arr.getJSONObject(i)
            InstalledPack(o.getString("id"), o.optString("title", ""),
                o.optDouble("price_paid", 0.0), o.optString("robot_id", ""))
        }
    }

    suspend fun installPack(packId: String, pid: String, token: String,
                            acceptPrice: Boolean,
                            robotId: String? = null): String {
        val body = JSONObject().put("profile_id", pid)
            .put("accept_price", acceptPrice)
        robotId?.let { body.put("robot_id", it) }
        return request("/packs/$packId/install", "POST", body, token)
    }

    suspend fun uninstallPack(packId: String, pid: String, token: String) {
        request("/profiles/$pid/packs/$packId", "DELETE", null, token)
    }

    suspend fun uninstallRobotPack(packId: String, robotId: String, token: String) {
        request("/robots/$robotId/packs/$packId", "DELETE", null, token)
    }

    // ---- gaming: a profile plays alongside real players ----

    suspend fun gameSessions(pid: String, token: String): List<GameSession> {
        val arr = JSONArray(request("/profiles/$pid/gaming/sessions", token = token))
        return (0 until arr.length()).map { i ->
            val o = arr.getJSONObject(i)
            GameSession(o.getString("id"), o.optString("platform", ""),
                o.optString("game", ""), o.optString("role", ""),
                o.optString("status", ""), o.optInt("callouts"))
        }
    }

    suspend fun startGameSession(pid: String, token: String, platform: String,
                                 game: String, role: String): String =
        request("/profiles/$pid/gaming/sessions", "POST",
            JSONObject().put("platform", platform).put("game", game)
                .put("role", role), token)

    suspend fun gameCallout(sid: String, token: String, situation: String,
                            minorPresent: Boolean): GameCalloutResult {
        val o = JSONObject(request("/gaming/sessions/$sid/callout", "POST",
            JSONObject().put("situation", situation)
                .put("minor_present", minorPresent), token))
        return GameCalloutResult(o.optString("status", ""),
            o.optString("line", null), o.optString("flag_reason", null))
    }

    suspend fun endGameSession(sid: String, token: String) {
        request("/gaming/sessions/$sid/end", "POST", null, token)
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

    // ---- voiceprint: FIG. 800, in the order the drawing gates it ----

    private fun voiceprintStatusOf(o: JSONObject): VoiceprintStatus {
        val c = o.getJSONObject("consent")
        val srcArr = c.optJSONArray("sources")
        val consent = VoiceConsentState(
            c.optBoolean("granted"),
            (0 until (srcArr?.length() ?: 0)).map { srcArr!!.getString(it) },
            if (c.isNull("granted_at")) null else c.optString("granted_at"))

        val enrollment = o.optJSONObject("enrollment")?.let { e ->
            val needs = e.optJSONArray("needs")
            val th = e.getJSONObject("threshold")
            VoiceEnrollment(
                e.optInt("samples"), e.optDouble("seconds"), e.optInt("turns"),
                if (e.isNull("mean_turn_seconds")) null
                else e.optDouble("mean_turn_seconds"),
                e.optBoolean("ready"),
                (0 until (needs?.length() ?: 0)).map { needs!!.getString(it) },
                th.optInt("samples"), th.optDouble("seconds"),
                e.optString("method", ""))
        }

        val print = o.optJSONObject("voiceprint")?.let { p ->
            VoiceprintRecord(p.getString("id"),
                if (p.isNull("built_at")) null else p.optString("built_at"),
                p.optBoolean("active"))
        }
        return VoiceprintStatus(consent, enrollment, print,
            o.optString("disclosure", ""))
    }

    suspend fun voiceprint(id: String, token: String): VoiceprintStatus =
        voiceprintStatusOf(JSONObject(request("/profiles/$id/voiceprint", token = token)))

    /**
     * Step 802. `ownVoice` is fixed true here because the backend refuses the
     * grant without it — there is deliberately no path to enrolling somebody
     * else's voice, so there is nothing for a caller to toggle.
     */
    suspend fun grantVoiceConsent(id: String, token: String,
                                  sources: List<String>): VoiceprintStatus {
        val arr = JSONArray(); sources.forEach { arr.put(it) }
        val body = JSONObject().put("own_voice", true).put("sources", arr)
        return voiceprintStatusOf(JSONObject(
            request("/profiles/$id/voiceprint/consent", "PUT", body, token)))
    }

    /**
     * Steps 806–808. Only the measurements travel: how long the recording ran
     * and how many spoken turns it held. The audio stays on the device.
     */
    suspend fun addVoiceSample(id: String, token: String, source: String,
                               seconds: Double, turns: Int, reference: String? = null) {
        val body = JSONObject().put("source", source).put("seconds", seconds)
            .put("turns", turns)
        if (reference != null) body.put("reference", reference)
        request("/profiles/$id/voiceprint/samples", "POST", body, token)
    }

    suspend fun buildVoiceprint(id: String, token: String): VoiceprintStatus =
        voiceprintStatusOf(JSONObject(
            request("/profiles/$id/voiceprint", "POST", null, token)))

    suspend fun speakInVoice(id: String, token: String, text: String): VoiceSpoken {
        val o = JSONObject(request("/profiles/$id/voiceprint/speak", "POST",
            JSONObject().put("text", text), token))
        return VoiceSpoken(o.optString("basis", ""), o.optString("disclosure", ""))
    }

    /** Withdrawal: the samples go, the print retires, the withdrawal stays. */
    suspend fun revokeVoiceprint(id: String, token: String): VoiceRevocation {
        val o = JSONObject(request("/profiles/$id/voiceprint", "DELETE", null, token))
        return VoiceRevocation(o.optInt("samples_deleted"), o.optString("note", ""))
    }
}
