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
data class RecolledMoment(val ref: String, val line: String?, val at: String?)
data class RecollectionShelf(val memories: List<RecolledMoment>, val readable: Boolean)
data class ProviderInfo(val name: String, val label: String, val configured: Boolean)
data class ModelChoice(val provider: String, val effective: String)
data class WatermarkDesign(val mark: String, val label: String, val line: String, val custom: Boolean)
data class RobotSpec(val model: String, val label: String, val maker: String, val kind: String)
data class Robot(val id: String, val model: String, val name: String, val status: String?, val commands: List<String>)
data class CommandResult(val command: String, val status: String, val spoken: String?)
data class Objection(val id: String, val status: String, val reason: String?, val reattested: Int)

/** What comes back from raising one. `profileStatus` is the part that matters
 *  to the person raising it: the profile is restricted straight away, pending
 *  review, rather than after somebody gets round to it. */
data class ObjectionOpened(
    val id: String, val status: String,
    val profileStatus: String,
    // What it was before, so the sentence can say what a dismissal
    // restores. Returned since objections shipped; no shell read it.
    val priorStatus: String = "active",
    val note: String,
)
data class ChatMessage(val content: String?, val status: String, val flagReason: String?,
                       val provenance: Provenance? = null, val watermarkLine: String? = null,
                       // Spec clauses 2/12: which way the profile worked, and
                       // whether the owner declared it or the wording implied it.
                       val role: String? = null, val roleHow: String? = null)
/** Extract and reconstruct: whose work is this, from the text alone. */
/** The count, and the three things it refuses to be. The refusals arrive as
 *  fields rather than prose so a screen renders them beside the number
 *  instead of composing a reassuring sentence of its own. */
data class ProfileAttention(val profileId: String, val peopleThisWeek: Int,
                            val peopleEver: Int, val youAreOneOfThem: Boolean,
                            val says: String, val ranksPeople: Boolean,
                            val hasAFavourite: Boolean, val namesAnybody: Boolean,
                            val note: String)
data class Solitude(val interactorId: String, val windowDays: Int,
                    val toProfiles: Int, val toPeople: Int, val totalTurns: Int,
                    val shareSynthetic: Double?, val enoughToSay: Boolean,
                    val note: String, val offerState: String?, val why: String?)
data class SolitudeReferral(val ref: String, val windowDays: Int,
                            val toProfiles: Int, val toPeople: Int,
                            val product: String)
data class WatermarkRecovery(val recovered: Boolean, val reason: String?,
                             val profileId: String?, val verbatim: Boolean,
                             val similarity: Double, val matchedWindows: Int,
                             val storedWindows: Int,
                             // How many windows were looked at, which is the
                             // denominator the shell's sentence names. iOS has
                             // carried it since the mark shipped; this did not.
                             val examinedWindows: Int = 0,
                             val state: String?,
                             val bestSimilarity: Double?, val threshold: Double?,
                             val markLine: String?, val disclosure: String?,
                             val method: String?)
data class Provenance(val generatedBy: String, val sourceItems: Int,
                      val licensedFrom: String?, val moderationStatus: String,
                      val disclaimer: String)
data class LanguageInfo(val code: String, val label: String)
data class FeedbackItem(val category: String, val message: String, val status: String)
data class FeedbackState(val mine: List<FeedbackItem>, val tally: Map<String, Int>, val total: Int)
data class AccessReportRow(val doing: String, val wall: String, val help: String?,
                           val lang: String, val createdAt: String)
data class MatterStep(val did: String, val note: String, val steppedAt: String)
/** One matter. Every field is filled whatever happened to it — a payload that
 *  grows keys only when something happened leaves this shell reading defaults
 *  on the case it meets most, which is the fresh one. */
data class Matter(val id: String, val concern: String, val trouble: String,
                  val standing: String, val settledBy: String,
                  val answer: String, val raisedAt: String,
                  val settledAt: String?, val anonymous: Boolean,
                  val trail: List<MatterStep>,
                  /** Only on the reply to raising one, and only without an
                   *  account. Shown once; the backend keeps only its hash. */
                  val claim: String?,
                  /** What the help box said when it did *not* recognise it. */
                  val offered: String?)
data class MattersMine(val myMatters: List<Matter>, val concerns: List<String>,
                       val standings: List<String>)
data class MatterQueue(val unsettled: List<Matter>, val standing: String,
                       val standings: List<String>)
data class SteeringDial(val name: String, val group: String, val label: String,
                        val low: String, val high: String, val min: Int, val max: Int)
data class SteeringHubState(val dials: List<SteeringDial>, val values: Map<String, Int>,
                            val baseAge: Int?, val agingEnabled: Boolean,
                            val effectiveAge: Int?, val appearance: String?,
                            val locked: Boolean)
data class LedgerEntry(val id: String, val kind: String, val memo: String?,
                       val amount: Double, val status: String)
data class EarningsStatement(val entries: List<LedgerEntry>, val accrued: Double,
                             val paid: Double, val lifetime: Double,
                             val byKind: Map<String, Double>, val currency: String)
data class PayoutReceipt(val payoutId: String, val totalAmount: Double,
                         val entries: Int)
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
data class Letter(val id: String, val weekStart: String, val body: String,
                  val describedBy: String)
data class Lookout(val id: String, val url: String, val everyHours: Double,
                   val status: String?, val nextRunAt: String?,
                   val changedAt: String?, val trouble: String?)
data class LookoutList(val lookouts: List<Lookout>, val readable: Boolean)
data class Excursion(val id: String, val topic: String, val redactions: Int,
                     val leftHost: Boolean, val findings: String, val learned: Boolean)
/** A question put to people rather than to a model. `brief` is the sanitized
 *  line that went onto the board; `topic` and `question` are the owner's own
 *  words and never leave. */
data class Inquiry(val id: String, val topic: String, val brief: String,
                   val redactions: Int, val closed: Boolean,
                   val answerCount: Int, val answers: List<InquiryAnswer>)
data class InquiryAnswer(val id: String, val alias: String, val body: String,
                         val pointsTo: String, val blocked: Boolean,
                         val folded: Boolean)
/** The same question as somebody with no account sees it — no profile, no
 *  typed question, no redaction count. A separate type so the two can never
 *  be confused for one another. */
data class OpenQuestion(val id: String, val brief: String,
                        val answerCount: Int, val closed: Boolean,
                        val replies: List<OpenAnswer>)
data class OpenAnswer(val alias: String, val body: String, val pointsTo: String)
/** One far host, and how often it has watched this profile leave. A count,
 *  never a list of visits. `stoodDown` is null on the deployment-wide view,
 *  where there is no profile to have decided. */
data class Visited(val host: String, val times: Int, val firstSeen: String,
                   val lastSeen: String, val reasons: List<String>,
                   val persistent: Boolean, val stoodDown: Boolean?)
/** One power the agent may be allowed to use, and what saying yes costs.
 *  `holds` is the half a roster usually omits; `touchesOthers` marks the ones
 *  that reach somebody who never chose this, and none of those is ever on by
 *  default. */
data class Privilege(val name: String, val mayDo: String, val holds: String,
                     val needs: List<String>, val touchesOthers: Boolean,
                     val chosen: Boolean, val byDefault: Boolean,
                     val why: String)
data class DialerPosture(val armed: Boolean, val waiver: String,
                         val sealed: Boolean, val callYourself: String)
/** `placed` is set by a call that connected, and by nothing else. */
data class Escalated(val id: String, val matter: String,
                     val dialedAt: String?, val placed: Boolean)
/** Somebody a person keeps in an area of life. `yours` separates the ones
 *  they chose from the ones the search found for them. */
data class MyPerson(val providerId: String, val name: String, val area: String,
                    val location: String?, val contact: String?,
                    val yours: Boolean, val preferred: Boolean)
data class BriefingAttachment(val kind: String, val title: String,
                              val sealed: Boolean)
data class BriefingPreview(val matter: String, val reads: String,
                           val attachments: List<BriefingAttachment>)
data class SocialConn(val id: String, val platform: String, val direction: String,
                      val handle: String?, val status: String?, val collected: Int,
                      val published: Int)
/** `needs` is the storefront lock: `nothing`, `sign-in` or `key` — what this
 *  connector must be given before it can reach the far side. */
data class CatalogApp(val provider: String, val app: String, val label: String,
                      val needsFirst: String)
data class AppConn(val id: String, val provider: String, val app: String, val label: String,
                   val capabilities: List<String>, val status: String?,
                   val needsFirst: String, val authorized: Boolean)
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

data class DeskConnection(val id: String, val sessionId: String,
                          val kind: String, val target: String,
                          val scope: String?, val status: String,
                          val means: String?,
                          // Caller's view of an active link only.
                          val token: String?)

data class DeskSession(val id: String, val deskId: String,
                       val callerId: String, val status: String,
                       val deskName: String?,
                       val connections: List<DeskConnection>)

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
                      val watermark: String,
                      val portrait: String?, val label: String?,
                      val sharedRoom: Boolean, val openUrl: String?,
                      val ageWall: Boolean)
data class FeedPage(val items: List<FeedCard>, val cursor: String?)
/** One card of the public stream. `plays` is the server's word, not this
 *  client's guess: false means nothing loads until somebody presses it. */
data class FeedCard(val id: String, val kind: String, val reason: String,
                    val title: String?, val note: String?,
                    val plays: Boolean, val loop: Boolean, val src: String?,
                    val platformName: String?, val url: String?,
                    val topic: String?, val channel: String?,
                    val people: Int, val entering: String?,
                    val displayName: String?, val trade: String?,
                    val presence: String?, val ringing: String?,
                    val human: Boolean, val ai: Boolean,
                    // party — a watch party whose host chose to be found.
                    val joining: String? = null)
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
                        val availablePacks: Int, val synced: Int)
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
/** What a derivation handed over and what stayed behind, written
 *  server-side at derive time. `carried` is a heterogeneous object; the
 *  shell keeps its key names and the typed withheld rows. */
data class ManifestWithheld(val item: String, val reason: String)
data class LicenseManifest(val carried: List<String>,
                           val withholdings: List<ManifestWithheld>)
data class LicenseGrant(val id: String, val buyerId: String, val kind: String,
                        val derivedProfileId: String?, val revoked: Boolean,
                        val manifest: LicenseManifest? = null)

class ApiException(message: String) : Exception(message)

/**
 * Coroutine client for the QRME backend.
 *
 * The Android emulator reaches the host machine at 10.0.2.2, so that is the
 * default. On a physical device, set your machine's LAN IP via [base].
 */
object ApiClient {
    /** The person's own model key, pushed in by the view model and sent on
     *  every request as `x-llm-api-key`. Empty means the deployment's. */
    @Volatile var llmKey: String = ""

    /** The deployment invite key: a published deployment sets
     *  QRME_SIGNUP_KEY and refuses account creation without it. Sent as
     *  `x-signup-key` on every request; the backend reads it only on the
     *  routes it gates. */
    @Volatile var signupKey: String = ""

    @Volatile var base: String = "http://10.0.2.2:8000"
        // Normalised on the way in, the way the console and the Windows
        // shell already do it: a pasted address with a trailing slash
        // otherwise reached every path as a double one. PDI's shell has
        // carried this setter since it was written; these two did not.
        set(value) {
            val trimmed = value.trimEnd('/')
            if (trimmed.isNotBlank()) field = trimmed
        }


    data class ProblemRow(val op: String, val statusCode: Int, val count: Int,
                          val source: String, val appVersion: String,
                          val platform: String, val day: String)

    // The failure aggregate this backend keeps. Reading is the operator's:
    // the problems key as the token, or nothing when asking from the machine
    // the backend runs on.
    suspend fun problemRows(key: String): List<ProblemRow> {
        val o = JSONObject(request("/v1/problems",
            token = key.ifBlank { null }))
        val arr = o.optJSONArray("rows") ?: return emptyList()
        return (0 until arr.length()).map { i ->
            val r = arr.getJSONObject(i)
            ProblemRow(r.optString("op"), r.optInt("status_code"),
                r.optInt("count"), r.optString("source"),
                r.optString("app_version"), r.optString("platform"),
                r.optString("day"))
        }
    }

    private suspend fun request(
        path: String, method: String = "GET",
        body: JSONObject? = null, token: String? = null,
        claim: String? = null,
    ): String = withContext(Dispatchers.IO) {
        val conn = (URL(base + path).openConnection() as HttpURLConnection).apply {
            requestMethod = method
            setRequestProperty("content-type", "application/json")
            // The other half of the accountless screen's language. `L10n`
            // covers the words this shell owns; every sentence the *backend*
            // composes for somebody with no profile is chosen from this
            // header, and no native shell was sending it.
            setRequestProperty("accept-language", L10n.deviceLanguage())
                    llmKey.takeIf { it.isNotEmpty() }?.let {
                        setRequestProperty("x-llm-api-key", it) }
                    signupKey.takeIf { it.isNotEmpty() }?.let {
                        setRequestProperty("x-signup-key", it) }
            token?.let { setRequestProperty("authorization", "Bearer $it") }
            // The claim that opens a matter raised without an account. A
            // header, never a query item: a query string is written to the
            // access log of every proxy it passes, and this one opens
            // somebody's own complaint about their own account.
            claim?.takeIf { it.isNotEmpty() }?.let {
                setRequestProperty("x-matter-claim", it) }
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
            // `optString` coerces a JSONArray through toString(), so a 422 —
            // whose `detail` is pydantic's list of rows — reached the person
            // as raw JSON. `message` is the sentence the backend composes
            // beside the rows; a string `detail` still wins for everything else.
            val said = runCatching {
                val body = JSONObject(text)
                body.optString("message").ifBlank {
                    if (body.opt("detail") is String) body.optString("detail") else ""
                }
            }.getOrNull()
            throw ApiException(if (said.isNullOrBlank()) "HTTP $code" else said)
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

    /** A character card as a profile seed; withheld pieces are named. */
    suspend fun importCard(cardJSON: String, birthdate: String,
                           language: String? = null): ProfileCreated {
        val body = JSONObject()
            .put("owner_id", "owner-1")
            .put("card", JSONObject(cardJSON))
            .put("verification", JSONObject().put("birthdate", birthdate))
            .put("terms_consent", true)
        if (!language.isNullOrBlank() && language != "en") body.put("language", language)
        val o = JSONObject(request("/profiles/import/card", "POST", body))
        return ProfileCreated(o.getString("id"), o.getString("display_name"),
            o.getString("kind"), o.getString("owner_token"))
    }

    /** Rehearsal rooms: practice the hard conversation, nothing remembered. */
    suspend fun openRehearsal(id: String, interactorId: String,
                              scenario: String): Pair<String, String> {
        val o = JSONObject(request("/profiles/$id/rehearsal", "POST",
            JSONObject().put("interactor_id", interactorId)
                .put("scenario", scenario)))
        return o.getString("id") to o.getString("scenario")
    }

    suspend fun rehearse(id: String, rehearsalId: String,
                         message: String): String {
        val o = JSONObject(request("/profiles/$id/rehearsal/$rehearsalId/say",
            "POST", JSONObject().put("message", message)))
        return o.getString("reply")
    }

    suspend fun closeRehearsal(id: String, rehearsalId: String) {
        request("/profiles/$id/rehearsal/$rehearsalId", "DELETE")
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

    /** The objector's own record. Public, like the route that opens one —
     *  built because `/audit` is owner- or reviewer-gated and the objector is
     *  neither, so they could END the profile and not read what happened.
     *  Carries no free text: event, actor, time, sealed. */
    suspend fun objectionTimeline(objectionId: String): ObjectionTimeline {
        val o = JSONObject(request("/objections/$objectionId/timeline"))
        val arr = o.optJSONArray("events")
        return ObjectionTimeline(
            o.optString("status"),
            o.optString("note"),
            (0 until (arr?.length() ?: 0)).map { i ->
                val e = arr!!.getJSONObject(i)
                ObjectionTimelineEvent(e.optString("id"), e.optString("event"),
                    e.optString("actor"), e.optBoolean("sealed"),
                    e.optString("at"))
            })
    }

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

    /**
     * Raise an objection against a profile. Takes **no credential**, and that
     * is the point: `open_objection` says so itself — *the objecting party
     * need not own an account*. This route belongs to somebody who has found
     * a synthetic profile of themselves, has no QRME account, and so has no
     * console. A phone is the surface they have; until 0.23.0 it was the
     * surface that could not do this.
     *
     * The shell already carried the other half — listing objections against
     * your own profile and attesting to them. That is the owner's side.
     */
    suspend fun openObjection(profileId: String, objectorRef: String,
                              reason: String): ObjectionOpened {
        val body = JSONObject().put("profile_id", profileId)
            .put("objector_ref", objectorRef).put("reason", reason)
        val o = JSONObject(request("/objections", "POST", body, null))
        return ObjectionOpened(
            o.getString("id"), o.optString("status", ""),
            o.optString("profile_status", ""),
            o.optString("prior_status", "active"), o.optString("note", ""))
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
            else appearance.optString("description", null),
            !o.isNull("lock"))
    }

    /** The personality nobody can move: while the lock stands, no
     *  steering write lands. The key is the owner's. */
    suspend fun lockSteering(id: String, token: String) {
        request("/profiles/$id/steering/lock", "POST", JSONObject(), token)
    }

    suspend fun unlockSteering(id: String, token: String) {
        request("/profiles/$id/steering/lock", "DELETE", token = token)
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
        return PayoutReceipt(o.getString("payout_id"), o.optDouble("total_amount"),
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
    /**
     * How many people a profile is talking to. Public, and no token here on
     * purpose: the count is a fact about the profile, not a secret earned by
     * intimacy.
     */
    suspend fun profileAttention(profileId: String): ProfileAttention {
        val o = JSONObject(request("/profiles/$profileId/attention"))
        return ProfileAttention(
            o.optString("profile_id"), o.optInt("people_this_week"),
            o.optInt("people_ever"), o.optBoolean("you_are_one_of_them"),
            o.optString("says"), o.optBoolean("ranks_people"),
            o.optBoolean("has_a_favourite"), o.optBoolean("names_anybody"),
            o.optString("note"))
    }

    // --- Your side of it ---------------------------------------------------
    // The mirror of profileAttention, scoped to the account asking. There is
    // no owner view of this and there must never be one.

    suspend fun solitude(interactorId: String): Solitude {
        val o = JSONObject(request("/interactors/$interactorId/solitude"))
        val turns = o.optJSONObject("turns") ?: JSONObject()
        val offer = o.optJSONObject("offer")
        return Solitude(
            o.optString("interactor_id"), o.optInt("window_days"),
            turns.optInt("to_profiles"), turns.optInt("to_people"),
            o.optInt("total_turns"),
            if (o.isNull("share_synthetic")) null else o.optDouble("share_synthetic"),
            o.optBoolean("enough_to_say"), o.optString("note"),
            offer?.optString("state"), offer?.optString("why"))
    }

    /** Closing the door is recorded, so the offer is not made a second time. */
    suspend fun solitudeHandoff(interactorId: String, accept: Boolean): String {
        val o = JSONObject(request("/interactors/$interactorId/solitude/handoff",
            "POST", JSONObject().put("accept", accept)))
        return o.optString("state")
    }

    /** Counts and a window — readable before they travel, never a word. */
    suspend fun solitudeReferral(interactorId: String): SolitudeReferral {
        val o = JSONObject(request("/interactors/$interactorId/solitude/referral"))
        val turns = o.optJSONObject("turns") ?: JSONObject()
        return SolitudeReferral(o.optString("ref"), o.optInt("window_days"),
            turns.optInt("to_profiles"), turns.optInt("to_people"),
            o.optString("product"))
    }

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
            o.optInt("examined_windows"),
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

    /** The accessibility door: tokenless on purpose — the person it exists
     *  for may be the person the signup shut out. The words stay on the
     *  deployment; nothing here reaches the problems collector. */
    suspend fun sendAccessReport(doing: String, wall: String, help: String?,
                                 lang: String): String {
        val body = JSONObject().put("doing", doing).put("wall", wall)
            .put("lang", lang)
        help?.takeIf { it.isNotBlank() }?.let { body.put("help", it) }
        return JSONObject(request("/access/reports", "POST", body))
            .optString("status", "received")
    }

    private fun matterOf(o: JSONObject): Matter {
        val arr = o.optJSONArray("trail")
        val trail = (0 until (arr?.length() ?: 0)).map { i ->
            val st = arr!!.getJSONObject(i)
            MatterStep(st.optString("did", ""), st.optString("note", ""),
                st.optString("stepped_at", ""))
        }
        return Matter(
            o.optString("id", ""), o.optString("concern", ""),
            o.optString("trouble", ""), o.optString("standing", ""),
            o.optString("settled_by", ""), o.optString("answer", ""),
            o.optString("raised_at", ""),
            o.optString("settled_at", "").takeIf { it.isNotBlank() },
            o.optBoolean("anonymous", false), trail,
            o.optString("claim", "").takeIf { it.isNotBlank() },
            o.optString("offered", "").takeIf { it.isNotBlank() })
    }

    /** Somebody's matter. Raising is tokenless on purpose — the person whose
     *  matter is that they cannot sign in is exactly who an authenticated
     *  support door shuts out. */
    suspend fun raiseMatter(trouble: String, concerns: String,
                            token: String? = null): Matter {
        val body = JSONObject().put("trouble", trouble).put("concerns", concerns)
        return matterOf(JSONObject(request("/matters", "POST", body, token)))
    }

    suspend fun myMatters(token: String?): MattersMine {
        val o = JSONObject(request("/matters", token = token))
        val arr = o.optJSONArray("my_matters")
        val mine = (0 until (arr?.length() ?: 0)).map { matterOf(arr!!.getJSONObject(it)) }
        val concerns = o.optJSONArray("concerns")
        val standings = o.optJSONArray("standings")
        return MattersMine(mine,
            (0 until (concerns?.length() ?: 0)).map { concerns!!.getString(it) },
            (0 until (standings?.length() ?: 0)).map { standings!!.getString(it) })
    }

    suspend fun matter(id: String, token: String? = null,
                       claim: String? = null): Matter =
        matterOf(JSONObject(request("/matters/$id", token = token, claim = claim)))

    suspend fun rejectMatterAnswer(id: String, token: String? = null,
                                   claim: String? = null): Matter =
        matterOf(JSONObject(request("/matters/$id/not-it", "POST", null,
                                    token, claim)))

    suspend fun settleMatter(id: String, answer: String, helped: Boolean = false,
                             token: String? = null, claim: String? = null): Matter {
        val body = JSONObject().put("answer", answer).put("helped", helped)
        return matterOf(JSONObject(request("/matters/$id/settle", "POST", body,
                                           token, claim)))
    }

    /** The three for whoever answers them — reviewer token, never an owner's:
     *  this queue is people's own words about their own accounts. */
    suspend fun matterQueue(reviewerToken: String): MatterQueue {
        val o = JSONObject(request("/matters/queue", token = reviewerToken))
        val arr = o.optJSONArray("unsettled")
        val waiting = (0 until (arr?.length() ?: 0)).map { matterOf(arr!!.getJSONObject(it)) }
        val standings = o.optJSONArray("standings")
        return MatterQueue(waiting, o.optString("standing", ""),
            (0 until (standings?.length() ?: 0)).map { standings!!.getString(it) })
    }

    suspend fun takeMatter(id: String, reviewerToken: String): Matter =
        matterOf(JSONObject(request("/matters/$id/take", "POST", null,
                                    reviewerToken)))

    suspend fun recordMatterStep(id: String, step: String, note: String = "",
                                 reviewerToken: String): Matter {
        val body = JSONObject().put("did", step).put("note", note)
        return matterOf(JSONObject(request("/matters/$id/used", "POST", body,
                                           reviewerToken)))
    }

    /** Reviewer-token read — the deployment's steward, never a profile. */
    suspend fun accessReports(reviewerToken: String): List<AccessReportRow> {
        val o = JSONObject(request("/access/reports", token = reviewerToken))
        val arr = o.optJSONArray("reports")
        return (0 until (arr?.length() ?: 0)).map { i ->
            val r = arr!!.getJSONObject(i)
            AccessReportRow(r.optString("doing", ""), r.optString("wall", ""),
                r.optString("help", "").takeIf { it.isNotBlank() },
                r.optString("lang", ""), r.optString("created_at", ""))
        }
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

    // The lookout: a page the vault re-reads on its schedule — the
    // profile answers from the current capture, and the watching never
    // leaves the facility.
    suspend fun lookouts(id: String, token: String): LookoutList {
        val o = JSONObject(request("/profiles/$id/lookout", token = token))
        val arr = o.optJSONArray("lookouts")
        return LookoutList(
            (0 until (arr?.length() ?: 0)).map { i ->
                val w = arr!!.getJSONObject(i)
                Lookout(
                    w.getString("id"), w.getString("url"),
                    w.getDouble("every_hours"),
                    if (w.isNull("status")) null else w.optString("status"),
                    if (w.isNull("next_run_at")) null
                    else w.optString("next_run_at"),
                    if (w.isNull("changed_at")) null
                    else w.optString("changed_at"),
                    if (w.isNull("trouble")) null
                    else w.optString("trouble"))
            },
            o.optBoolean("readable"))
    }

    suspend fun plantLookout(id: String, url: String, everyHours: Double,
                             token: String): Boolean {
        val body = JSONObject().put("url", url).put("every_hours", everyHours)
        return JSONObject(request("/profiles/$id/lookout", "POST", body,
                                  token)).optBoolean("planted")
    }

    suspend fun lookoutPage(id: String, lid: String, token: String): String {
        val o = JSONObject(request("/profiles/$id/lookout/$lid/page",
                                   token = token))
        return (if (o.isNull("fetched_at")) "\u2014"
                else o.optString("fetched_at")) +
            " \u00b7 " + o.optInt("chars")
    }

    suspend fun dropLookout(id: String, lid: String, token: String): Boolean {
        return JSONObject(request("/profiles/$id/lookout/$lid", "DELETE",
                                  null, token)).optBoolean("removed")
    }

    suspend fun writeLetter(id: String, token: String): Letter {
        val o = JSONObject(request("/profiles/$id/letter", "POST",
                                   JSONObject(), token))
        return Letter(o.getString("id"), o.getString("week_start"),
                      o.getString("body"), o.getString("described_by"))
    }

    suspend fun letters(id: String, token: String): List<Letter> {
        val arr = JSONArray(request("/profiles/$id/letters", token = token))
        return (0 until arr.length()).map { i ->
            val l = arr.getJSONObject(i)
            Letter(l.getString("id"), l.getString("week_start"),
                   l.getString("body"), l.getString("described_by"))
        }
    }

    // ---- inquiries: ask people, not pages ----

    private fun answerOf(o: JSONObject) = InquiryAnswer(
        o.getString("id"), o.optString("alias", ""), o.optString("body", ""),
        o.optString("points_to", ""), o.optBoolean("blocked"),
        o.optBoolean("folded"))

    private fun inquiryOf(o: JSONObject): Inquiry {
        val arr = o.optJSONArray("answers")
        val answers = if (arr == null) emptyList()
                      else (0 until arr.length()).map { answerOf(arr.getJSONObject(it)) }
        return Inquiry(o.getString("id"), o.optString("topic", ""),
            o.optString("brief", ""), o.optInt("redactions"),
            o.optBoolean("closed"), o.optInt("answer_count"), answers)
    }

    private fun openQuestionOf(o: JSONObject): OpenQuestion {
        val arr = o.optJSONArray("replies")
        val replies = if (arr == null) emptyList() else
            (0 until arr.length()).map {
                val a = arr.getJSONObject(it)
                OpenAnswer(a.optString("alias", ""), a.optString("body", ""),
                           a.optString("points_to", ""))
            }
        return OpenQuestion(o.getString("id"), o.optString("brief", ""),
            o.optInt("answer_count"), o.optBoolean("closed"), replies)
    }

    suspend fun inquiries(id: String, token: String): List<Inquiry> {
        val arr = JSONArray(request("/profiles/$id/inquiries", token = token))
        return (0 until arr.length()).map { inquiryOf(arr.getJSONObject(it)) }
    }

    suspend fun openInquiry(id: String, token: String, topic: String,
                            question: String): Inquiry =
        inquiryOf(JSONObject(request("/profiles/$id/inquiries", "POST",
            JSONObject().put("topic", topic).put("question", question), token)))

    suspend fun inquiry(iid: String, token: String): Inquiry =
        inquiryOf(JSONObject(request("/inquiries/$iid", token = token)))

    suspend fun closeInquiry(iid: String, token: String): Inquiry =
        inquiryOf(JSONObject(request("/inquiries/$iid/close", "POST", null, token)))

    suspend fun learnFromAnswer(iid: String, aid: String, token: String) {
        request("/inquiries/$iid/answers/$aid/learn", "POST", null, token)
    }

    // The board, and answering one. **No token on any of these three** — the
    // person answering has no account and is not asked for a name, and a
    // credential here would be a credential the board could log against them.

    suspend fun openQuestions(): List<OpenQuestion> {
        val arr = JSONArray(request("/open-questions"))
        return (0 until arr.length()).map { openQuestionOf(arr.getJSONObject(it)) }
    }

    suspend fun openQuestion(iid: String): OpenQuestion =
        openQuestionOf(JSONObject(request("/open-questions/$iid")))

    suspend fun answerOpenQuestion(iid: String, body: String, alias: String,
                                   pointsTo: String): String {
        val o = JSONObject(request("/open-questions/$iid/answers", "POST",
            JSONObject().put("body", body).put("alias", alias)
                .put("points_to", pointsTo)))
        return o.optString("note", "")
    }

    // ---- where it keeps going back to ----

    private fun visitedOf(o: JSONObject): Visited {
        val arr = o.optJSONArray("reasons")
        val reasons = if (arr == null) emptyList() else
            (0 until arr.length()).map { arr.getString(it) }
        return Visited(o.getString("host"), o.optInt("times"),
            o.optString("first_seen", ""), o.optString("last_seen", ""),
            reasons, o.optBoolean("persistent"),
            if (o.has("stood_down")) o.optBoolean("stood_down") else null)
    }

    suspend fun visits(id: String, token: String): List<Visited> {
        val arr = JSONArray(request("/profiles/$id/visits", token = token))
        return (0 until arr.length()).map { visitedOf(arr.getJSONObject(it)) }
    }

    suspend fun standDownFromHost(id: String, host: String, token: String) {
        request("/profiles/$id/visits/stand-down", "POST",
            JSONObject().put("host", host), token)
    }

    suspend fun visitHostAgain(id: String, host: String, token: String) {
        request("/profiles/$id/visits/lift", "POST",
            JSONObject().put("host", host), token)
    }

    /** Hosts and counts and no profile at any depth. Same key as the
     *  failure aggregate, deliberately. */
    suspend fun visitsAcross(key: String): List<Visited> {
        val arr = JSONArray(request("/visits/across", token = key))
        return (0 until arr.length()).map { visitedOf(arr.getJSONObject(it)) }
    }

    // ---- what the agent may do ----

    private fun privilegeOf(o: JSONObject): Privilege {
        val needs = o.optJSONArray("needs")
        return Privilege(
            o.getString("name"), o.optString("may_do", ""),
            o.optString("holds", ""),
            (0 until (needs?.length() ?: 0)).map { needs!!.getString(it) },
            o.optBoolean("touches_others"), o.optBoolean("chosen"),
            o.optBoolean("by_default"), o.optString("why", ""))
    }

    /** Readable without a token: what an agent may do on somebody's behalf is
     *  not a secret kept from the person it would be done to. */
    suspend fun privileges(profile: String, token: String? = null): List<Privilege> {
        val arr = JSONArray(request("/profiles/$profile/privileges", token = token))
        return (0 until arr.length()).map { privilegeOf(arr.getJSONObject(it)) }
    }

    /** The whole roster comes back, not the row. */
    suspend fun allowPrivilege(profile: String, name: String, on: Boolean,
                               token: String): List<Privilege> {
        val arr = JSONArray(request("/profiles/$profile/privileges/$name", "POST",
            JSONObject().put("on", on), token))
        return (0 until arr.length()).map { privilegeOf(arr.getJSONObject(it)) }
    }

    // ---- when it cannot resolve it, and the door at the end ----

    suspend fun dialerPosture(interactor: String, token: String): DialerPosture {
        val o = JSONObject(request("/interactors/$interactor/dialer", token = token))
        return DialerPosture(o.optBoolean("armed"), o.optString("waiver", ""),
            o.optBoolean("sealed"), o.optString("call_yourself", ""))
    }

    suspend fun armDialer(interactor: String, signatureId: String, token: String) {
        request("/interactors/$interactor/dialer/arm", "POST",
            JSONObject().put("signature_id", signatureId), token)
    }

    private fun escalatedOf(o: JSONObject) = Escalated(
        o.getString("id"), o.optString("matter", ""),
        o.optString("dialed_at", null), o.optBoolean("placed"))

    suspend fun cannotResolve(profile: String, interactor: String,
                              matter: String, token: String): Escalated =
        escalatedOf(JSONObject(request("/profiles/$profile/unresolved", "POST",
            JSONObject().put("interactor_id", interactor).put("matter", matter),
            token)))

    suspend fun myEscalations(interactor: String, token: String): List<Escalated> {
        val arr = JSONArray(request("/interactors/$interactor/unresolved", token = token))
        return (0 until arr.length()).map { escalatedOf(arr.getJSONObject(it)) }
    }

    /** While the deployment is sealed this always throws, and the refusal
     *  says no call was placed and gives the number to dial. */
    suspend fun dialEmergency(escalation: String, interactor: String,
                              token: String): Escalated =
        escalatedOf(JSONObject(request(
            "/escalations/$escalation/dial?interactor_id=$interactor",
            "POST", null, token)))

    // ---- your own people, and the briefing that arrives before them ----

    private fun personOf(o: JSONObject) = MyPerson(
        o.getString("provider_id"), o.optString("name", ""),
        o.optString("area", ""), o.optString("location", null),
        o.optString("contact", null), o.optBoolean("yours"),
        o.optBoolean("preferred"))

    suspend fun myPeople(interactor: String, token: String): List<MyPerson> {
        val arr = JSONArray(request("/interactors/$interactor/people", token = token))
        return (0 until arr.length()).map { personOf(arr.getJSONObject(it)) }
    }

    suspend fun peopleForArea(interactor: String, area: String,
                              token: String): List<MyPerson> {
        val q = java.net.URLEncoder.encode(area, "UTF-8")
        val arr = JSONArray(request("/interactors/$interactor/people/for-area?area=$q",
                                    token = token))
        return (0 until arr.length()).map { personOf(arr.getJSONObject(it)) }
    }

    suspend fun keepPerson(interactor: String, providerId: String, token: String) {
        request("/interactors/$interactor/people", "POST",
            JSONObject().put("provider_id", providerId), token)
    }

    suspend fun preferPerson(interactor: String, providerId: String, token: String) {
        request("/interactors/$interactor/people/$providerId/prefer", "POST", null, token)
    }

    suspend fun dropPerson(interactor: String, providerId: String, token: String) {
        request("/interactors/$interactor/people/$providerId", "DELETE", null, token)
    }

    /** Nothing is sent by this — the whole file, readable before anybody is
     *  contacted, so declining is still free. */
    suspend fun previewBriefing(interactor: String, profile: String,
                                providerId: String, matter: String,
                                grantToken: String,
                                token: String): BriefingPreview {
        val o = JSONObject(request("/briefings/preview", "POST",
            JSONObject().put("interactor_id", interactor)
                .put("profile_id", profile).put("provider_id", providerId)
                .put("matter", matter).put("grant_token", grantToken), token))
        val pkg = o.getJSONObject("package")
        val arr = pkg.optJSONArray("attachments")
        val items = if (arr == null) emptyList() else
            (0 until arr.length()).map {
                val a = arr.getJSONObject(it)
                BriefingAttachment(a.optString("kind", ""),
                    a.optString("title", ""), a.optBoolean("sealed"))
            }
        return BriefingPreview(pkg.optString("matter", ""),
            o.optString("reads", ""), items)
    }

    // ---- Community: stranger connections & multiparty rooms ----

    // Every call below carries the interactor's own token. The id in the body
    // says whose turn it is; the token says who is asking, and the server now
    // believes the second one only.
    suspend fun joinQueue(interactorId: String, alias: String?,
                          tier: String = "friendly",
                          token: String): ConnJoin {
        val body = JSONObject().put("interactor_id", interactorId).put("tier", tier)
        if (!alias.isNullOrBlank()) body.put("alias", alias)
        val o = JSONObject(request("/connections/join", "POST", body, token))
        return ConnJoin(o.getString("status"), o.optString("connection_id", null),
            o.optString("matched_with", null))
    }

    // What happened to my wait. A match is made by whichever side arrives
    // second — their join answers *them*, never the waiter — so the waiter
    // polls this. Never join again to ask: that re-queues the caller.
    suspend fun myConnection(token: String): ConnJoin {
        val o = JSONObject(request("/connections/mine", token = token))
        return ConnJoin(o.getString("status"), o.optString("connection_id", null),
            o.optString("matched_with", null))
    }

    suspend fun connectionMessages(cid: String, interactorId: String,
                                   token: String): List<ConnMsg> {
        val arr = JSONArray(request("/connections/$cid/messages?interactor_id=$interactorId",
            token = token))
        return (0 until arr.length()).map { i ->
            val o = arr.getJSONObject(i)
            ConnMsg(o.getString("id"), o.optString("from", ""), o.optString("content", ""),
                o.optString("status", null))
        }
    }

    suspend fun sendConnectionMessage(cid: String, interactorId: String,
                                      message: String, token: String) {
        request("/connections/$cid/messages", "POST",
            JSONObject().put("interactor_id", interactorId).put("message", message),
            token)
    }

    suspend fun endConnection(cid: String, interactorId: String, token: String) {
        request("/connections/$cid/end?interactor_id=$interactorId", "POST",
            token = token)
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

    // All three carry the interactor token now. The room routes used to take
    // none: the speaker was read out of `sender_id` in the body, so anybody
    // with a room id could post as a named participant, and the transcript
    // was readable by anybody at all. `sender_id` is still sent because the
    // server still accepts the field; it is ignored there, and the token is
    // what says who is speaking.
    suspend fun roomMessage(roomId: String, senderId: String, message: String,
                            token: String) {
        request("/rooms/$roomId/messages", "POST",
            JSONObject().put("sender_id", senderId).put("message", message),
            token)
    }

    suspend fun roomAdvance(roomId: String, token: String) {
        request("/rooms/$roomId/advance", "POST", null, token)
    }

    suspend fun roomTranscript(roomId: String, token: String): List<RoomMsg> {
        val arr = JSONArray(request("/rooms/$roomId/messages", token = token))
        return (0 until arr.length()).map { roomMsgOf(arr.getJSONObject(it)) }
    }

    // ---- Reach: summon (@handle + beacons), marketplace, licensing ----

    // The owner's token. Without it a stranger could replace the name a
    // profile answers to, and the old one stopped resolving.
    suspend fun claimHandle(id: String, handle: String, token: String): String {
        val o = JSONObject(request("/profiles/$id/handle", "PUT",
            JSONObject().put("handle", handle), token))
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
            if (o.isNull("portrait")) null else o.optString("portrait", null),
            if (o.isNull("label")) null else o.optString("label", null),
            !o.isNull("shared_room"),
            if (o.isNull("open_url")) null else o.optString("open_url", null),
            o.optBoolean("age_wall", false))
    }

    // ---- the public stream ----

    /**
     * One page of the public stream. No token: a person who followed a
     * shared link is a reader like any other.
     *
     * `plays` is read, never recomputed. Only footage this deployment holds
     * comes back true, so scrolling past an off-site card makes no request
     * to anybody else — `qrme/db.py` has said so about `post_videos` since
     * long before a stream existed, and a client that decided otherwise
     * would undo it for everyone on this phone.
     */
    suspend fun publicFeed(cursor: String? = null): FeedPage {
        val tail = if (cursor.isNullOrEmpty()) "" else "&cursor=$cursor"
        val o = JSONObject(request("/feed?limit=12" + tail))
        val arr = o.optJSONArray("items")
        val items = mutableListOf<FeedCard>()
        for (i in 0 until (arr?.length() ?: 0)) {
            items.add(feedCard(arr!!.getJSONObject(i)))
        }
        return FeedPage(items,
            if (o.isNull("cursor")) null else o.optString("cursor"))
    }

    /**
     * One card, for a link somebody was sent. A rated item a reader is not
     * verified for answers 404 rather than an empty card: a 403 would
     * announce that the item exists.
     */
    suspend fun feedItem(id: String): FeedCard =
        feedCard(JSONObject(request("/feed/$id")))

    private fun feedCard(o: JSONObject): FeedCard {
        // A party card carries its facade under "video"; the fields inside
        // are the same shape, so one pair of columns serves both.
        val f = o.optJSONObject("facade") ?: o.optJSONObject("video")
        return FeedCard(
            o.optString("id", ""), o.optString("kind", ""),
            o.optString("reason", ""),
            if (o.isNull("title")) null else o.optString("title"),
            if (o.isNull("note")) null else o.optString("note"),
            o.optBoolean("plays", false), o.optBoolean("loop", false),
            if (o.isNull("src")) null else o.optString("src"),
            f?.optString("platform_name"), f?.optString("url"),
            if (o.isNull("topic")) null else o.optString("topic"),
            if (o.isNull("channel")) null else o.optString("channel"),
            o.optInt("people", 0),
            if (o.isNull("entering")) null else o.optString("entering"),
            if (o.isNull("display_name")) null else o.optString("display_name"),
            if (o.isNull("trade")) null else o.optString("trade"),
            if (o.isNull("presence")) null else o.optString("presence"),
            if (o.isNull("ringing")) null else o.optString("ringing"),
            o.optBoolean("human", false), o.optBoolean("ai", false),
            if (o.isNull("joining")) null else o.optString("joining"))
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


    // ---- connections across the counter ----
    // The desk offers; only the caller's accept mints the link token, and it
    // is returned to the caller alone. Either side ends it.

    private fun deskConnection(o: JSONObject) = DeskConnection(
        o.getString("id"), o.getString("session_id"), o.getString("kind"),
        o.getString("target"),
        if (o.isNull("scope")) null else o.optString("scope"),
        o.getString("status"),
        if (o.isNull("means")) null else o.optString("means"),
        if (o.isNull("token")) null else o.optString("token"))

    private fun deskSession(o: JSONObject): DeskSession {
        val links = o.optJSONArray("connections")
        val parsed = mutableListOf<DeskConnection>()
        if (links != null) for (i in 0 until links.length())
            parsed.add(deskConnection(links.getJSONObject(i)))
        return DeskSession(
            o.getString("id"), o.getString("desk_id"),
            o.getString("caller_id"), o.getString("status"),
            if (o.isNull("desk_name")) null else o.optString("desk_name"),
            parsed)
    }

    suspend fun openDeskSession(deskId: String, callerId: String,
                                token: String): DeskSession {
        val body = JSONObject().put("caller_id", callerId)
        return deskSession(JSONObject(
            request("/desks/$deskId/sessions", "POST", body, token)))
    }

    suspend fun deskSessions(deskId: String, token: String): List<DeskSession> {
        val arr = JSONArray(request("/desks/$deskId/sessions", token = token))
        return (0 until arr.length()).map { deskSession(arr.getJSONObject(it)) }
    }

    suspend fun deskSession(sessionId: String, token: String): DeskSession =
        deskSession(JSONObject(request("/desk-sessions/$sessionId",
                                       token = token)))

    suspend fun offerDeskConnection(sessionId: String, kind: String,
                                    target: String, scope: String?,
                                    token: String): DeskConnection {
        val body = JSONObject().put("kind", kind).put("target", target)
        if (scope != null) body.put("scope", scope)
        return deskConnection(JSONObject(request(
            "/desk-sessions/$sessionId/connections", "POST", body, token)))
    }

    suspend fun answerDeskConnection(sessionId: String, connectionId: String,
                                     accept: Boolean,
                                     token: String): DeskConnection {
        val body = JSONObject().put("accept", accept)
        return deskConnection(JSONObject(request(
            "/desk-sessions/$sessionId/connections/$connectionId/answer",
            "POST", body, token)))
    }

    suspend fun endDeskConnection(sessionId: String, connectionId: String,
                                  token: String): DeskConnection =
        deskConnection(JSONObject(request(
            "/desk-sessions/$sessionId/connections/$connectionId/end",
            "POST", null, token)))

    suspend fun closeDeskSession(sessionId: String, token: String): DeskSession =
        deskSession(JSONObject(request("/desk-sessions/$sessionId/close",
                                       "POST", null, token)))

    suspend fun myDeskSessions(interactorId: String,
                               token: String): List<DeskSession> {
        val arr = JSONArray(request("/interactors/$interactorId/desk-sessions",
                                    token = token))
        return (0 until arr.length()).map { deskSession(arr.getJSONObject(it)) }
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
        // The path literal at the call site rather than one statement away in
        // a `val path`. The route audit reads a call's arguments, and cannot
        // follow a variable — so both spellings of this path read as no call
        // at all, and `GET /packs` looked like a door Android did not have.
        val arr = JSONArray(
            if (industry.isNullOrBlank()) request("/packs")
            else request("/packs?industry=" +
                         java.net.URLEncoder.encode(industry, "UTF-8")))
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
                o.optString("tagline", ""), o.optInt("available_packs"),
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
        // Inlined for the same reason as `packs` above.
        val arr = JSONArray(
            if (tag.isNullOrBlank()) request("/marketplace/listings")
            else request("/marketplace/listings?tag=" +
                         java.net.URLEncoder.encode(tag, "UTF-8")))
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
            val manifest = o.optJSONObject("manifest")?.let { m ->
                val carried = m.optJSONObject("carried")
                    ?.keys()?.asSequence()?.sorted()?.toList() ?: emptyList()
                val withheldArr = m.optJSONArray("withholdings")
                val withheld = (0 until (withheldArr?.length() ?: 0)).map { j ->
                    val w = withheldArr!!.getJSONObject(j)
                    ManifestWithheld(w.optString("item", ""),
                                     w.optString("reason", ""))
                }
                LicenseManifest(carried, withheld)
            }
            LicenseGrant(o.getString("id"), o.optString("buyer_id", ""),
                o.optString("kind", ""), o.optString("derived_profile_id", null),
                o.optBoolean("revoked"), manifest)
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

    suspend fun socialScrape(cid: String, token: String) {
        request("/social/$cid/scrape", "POST", JSONObject(), token)
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
                out += CatalogApp(p.getString("provider"), a.getString("app"),
                    a.getString("label"), a.optString("needs_first", "sign-in"))
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
            o.optString("status", null),
            o.optString("needs_first", "sign-in"), o.optBoolean("authorized", false))
    }

    suspend fun appConnections(id: String, token: String): List<AppConn> {
        val arr = JSONArray(request("/profiles/$id/apps", token = token))
        return (0 until arr.length()).map { appConnOf(arr.getJSONObject(it)) }
    }

    suspend fun appConnect(id: String, token: String, provider: String, app: String): AppConn {
        return appConnOf(JSONObject(request("/profiles/$id/apps", "POST",
            JSONObject().put("provider", provider).put("app", app), token)))
    }

    /** Uninstall. This route has existed as long as connectors have and no
     *  shell ever called it — the door guard skipped every path starting
     *  `/app`, meaning the console bundle, and `/apps` starts with it. */
    suspend fun appRevoke(cid: String, token: String) {
        request("/apps/$cid", "DELETE", null, token)
    }

    /** Give a connector its credential. It goes to the vault; this shell
     *  keeps nothing and cannot read it back. */
    suspend fun appAuthorize(cid: String, token: String, secret: String): AppConn {
        return appConnOf(JSONObject(request("/apps/$cid/authorize", "POST",
            JSONObject().put("secret", secret), token)))
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

    // ---- Everyone here: the browse pool, its head count, and the owner's
    // private switch (qrme/friends.py browse/listing) ----

    data class BrowsePool(val headCount: Int, val kinds: Map<String, Int>,
                          val profiles: List<PoolPerson>)
    data class PoolPerson(val profileId: String, val displayName: String,
                           val handle: String, val avatar: String,
                           val kind: String)
    data class PoolListing(val profileId: String, val listed: Boolean)

    private fun poolPersonOf(o: JSONObject) = PoolPerson(
        o.optString("profile_id", ""), o.optString("display_name", ""),
        o.optString("handle", ""), o.optString("avatar", ""),
        o.optString("kind", ""))

    /** Everyone here: every profile on the deployment, real and synthetic
     *  side by side, listed until its owner goes private. */
    suspend fun browsePeople(): BrowsePool {
        val o = JSONObject(request("/people/browse"))
        val arr = o.optJSONArray("profiles") ?: org.json.JSONArray()
        val kindsObj = o.optJSONObject("kind_counts") ?: JSONObject()
        val kinds = kindsObj.keys().asSequence()
            .associateWith { kindsObj.optInt(it, 0) }
        return BrowsePool(o.optInt("head_count", 0), kinds,
            (0 until arr.length()).map { poolPersonOf(arr.getJSONObject(it)) })
    }

    /** Whether this profile stands in the pool — the owner's read. */
    suspend fun listing(id: String, token: String): PoolListing {
        val o = JSONObject(request("/profiles/$id/listing", token = token))
        return PoolListing(o.optString("profile_id", ""),
                       o.optBoolean("listed", true))
    }

    /** The owner's door out of the pool and back in, per profile. */
    suspend fun setListing(id: String, token: String,
                           listed: Boolean): PoolListing {
        val o = JSONObject(request("/profiles/$id/listing", "PUT",
            JSONObject().put("listed", listed), token))
        return PoolListing(o.optString("profile_id", ""),
                       o.optBoolean("listed", true))
    }

    // ---- The spoken voice: a reference to a voice made on the engine's own
    // surface, and one utterance of audio back (qrme/spoken.py) ----

    data class SpokenBinding(val provider: String, val voiceId: String,
                             val label: String, val speaks: Boolean)

    private fun spokenBindingOf(o: JSONObject) = SpokenBinding(
        o.optString("provider", ""), o.optString("voice_id", ""),
        o.optString("label", ""), o.optBoolean("speaks", false))

    /** Which voice this profile speaks with, or the empty binding — one
     *  shape either way, so the screen never special-cases the common case. */
    suspend fun spokenVoice(id: String): SpokenBinding =
        spokenBindingOf(JSONObject(request("/profiles/$id/voice")))

    /** The owner points the profile at a voice made on the engine's own
     *  surface. An empty voiceId unbinds. QRME keeps the reference; the
     *  engine keeps the voice — and its key, which never touches this app. */
    suspend fun bindSpokenVoice(id: String, token: String, voiceId: String,
                                label: String): SpokenBinding =
        spokenBindingOf(JSONObject(request("/profiles/$id/voice", "PUT",
            JSONObject().put("voice_id", voiceId).put("label", label), token)))

    /** One utterance, synthesized server-side and watermarked there. Raw
     *  bytes rather than the shared helper, because this answer is sound. */
    suspend fun saySpoken(id: String, token: String, text: String): ByteArray =
        withContext(Dispatchers.IO) {
            val conn = (URL("$base/profiles/$id/voice/say")
                .openConnection() as HttpURLConnection).apply {
                requestMethod = "POST"
                setRequestProperty("content-type", "application/json")
                setRequestProperty("accept-language", L10n.deviceLanguage())
                setRequestProperty("authorization", "Bearer $token")
                doOutput = true
                outputStream.use {
                    it.write(JSONObject().put("text", text)
                        .toString().toByteArray()) }
            }
            val code = conn.responseCode
            if (code !in 200..299) {
                val text2 = conn.errorStream?.bufferedReader()
                    ?.use { it.readText() } ?: ""
                Problems.record("POST", "/profiles/{id}/voice/say", code)
                val said = runCatching {
                    val body = JSONObject(text2)
                    body.optString("message").ifBlank {
                        if (body.opt("detail") is String)
                            body.optString("detail") else ""
                    }
                }.getOrNull()
                throw ApiException(
                    if (said.isNullOrBlank()) "HTTP $code" else said)
            }
            conn.inputStream.use { it.readBytes() }
        }

    // ---- The open web, and the people here (qrme/websearch.py, /people) ----

    data class WebSearchRow(val title: String, val url: String, val note: String)
    data class WebSearchAnswer(val pages: List<WebSearchRow>, val moreUrl: String)

    /** A real search, keyless: the query goes out and nothing else — see the
     *  door's own docstring for why it works with no model configured. */
    suspend fun webSearch(id: String, token: String, q: String): WebSearchAnswer {
        val enc = java.net.URLEncoder.encode(q, "UTF-8")
        val o = JSONObject(request("/profiles/$id/search?q=$enc", token = token))
        val rows = mutableListOf<WebSearchRow>()
        val arr = o.optJSONArray("pages")
        if (arr != null) for (i in 0 until arr.length()) {
            val r = arr.getJSONObject(i)
            rows.add(WebSearchRow(r.optString("title", ""),
                r.optString("url", ""), r.optString("note", "")))
        }
        return WebSearchAnswer(rows, o.optString("more_url", ""))
    }

    data class FoundPerson(val profileId: String, val displayName: String,
                           val handle: String)

    /** Publicly listed profiles by name or handle — the door two beta
     *  testers needed to become friends. Anonymous profiles never match. */
    suspend fun findPeople(q: String): List<FoundPerson> {
        val enc = java.net.URLEncoder.encode(q, "UTF-8")
        val o = JSONObject(request("/people?q=$enc"))
        val out = mutableListOf<FoundPerson>()
        val arr = o.optJSONArray("found")
        if (arr != null) for (i in 0 until arr.length()) {
            val r = arr.getJSONObject(i)
            out.add(FoundPerson(r.optString("profile_id", ""),
                r.optString("display_name", ""), r.optString("handle", "")))
        }
        return out
    }

    /** Withdrawal: the samples go, the print retires, the withdrawal stays. */
    suspend fun revokeVoiceprint(id: String, token: String): VoiceRevocation {
        val o = JSONObject(request("/profiles/$id/voiceprint", "DELETE", null, token))
        return VoiceRevocation(o.optInt("samples_deleted"), o.optString("note", ""))
    }

    // ---- shops: storefronts, not desks (qrme/shops.py) ----

    private fun shopOfferingOf(o: JSONObject) = ShopOffering(
        o.getString("id"), o.optString("kind"), o.optString("title"),
        o.optDouble("price", 0.0), o.optString("currency"),
        o.optString("availability"), o.optInt("retired"))

    private fun shopOrderOf(o: JSONObject) = ShopOrder(
        o.getString("id"), o.optString("shop_id"), o.optString("title"),
        o.optInt("quantity", 1), o.optDouble("amount", 0.0),
        o.optString("currency"), o.optString("status"))

    private fun shopDetailOf(o: JSONObject): ShopDetail {
        val offs = mutableListOf<ShopOffering>()
        o.optJSONArray("offerings")?.let { a ->
            for (i in 0 until a.length()) offs.add(shopOfferingOf(a.getJSONObject(i)))
        }
        return ShopDetail(o.getString("id"), o.optString("name"),
            if (o.isNull("blurb")) null else o.optString("blurb"),
            if (o.isNull("seller")) null else o.optString("seller"), offs)
    }

    suspend fun listShops(): List<ShopCard> {
        val a = org.json.JSONArray(request("/shops"))
        return (0 until a.length()).map { i ->
            val o = a.getJSONObject(i)
            ShopCard(o.getString("id"), o.optString("name"),
                o.optString("seller"),
                if (o.isNull("tag")) null else o.optString("tag"),
                o.optInt("offerings"))
        }
    }

    suspend fun shopCard(shopId: String): ShopDetail =
        shopDetailOf(JSONObject(request("/shops/$shopId")))

    suspend fun openShop(profileId: String, name: String, token: String): ShopDetail =
        shopDetailOf(JSONObject(request("/shops", "POST",
            JSONObject().put("profile_id", profileId).put("name", name), token)))

    suspend fun addShopOffering(shopId: String, kind: String, title: String,
                                price: Double, token: String): ShopOffering =
        shopOfferingOf(JSONObject(request("/shops/$shopId/offerings", "POST",
            JSONObject().put("kind", kind).put("title", title).put("price", price),
            token)))

    suspend fun retireShopOffering(shopId: String, offeringId: String,
                                   token: String): ShopOffering =
        shopOfferingOf(JSONObject(
            request("/shops/$shopId/offerings/$offeringId", "DELETE", null, token)))

    /** The buyer's press — signed with the interactor's own token. */
    suspend fun placeShopOrder(shopId: String, offeringId: String, buyerId: String,
                               quantity: Int, token: String): ShopOrder =
        shopOrderOf(JSONObject(request("/shops/$shopId/orders", "POST",
            JSONObject().put("offering_id", offeringId).put("buyer_id", buyerId)
                .put("quantity", quantity), token)))

    suspend fun shopOrderBook(shopId: String, token: String): List<ShopOrder> {
        val a = org.json.JSONArray(request("/shops/$shopId/orders", token = token))
        return (0 until a.length()).map { shopOrderOf(a.getJSONObject(it)) }
    }

    suspend fun myShopOrders(buyerId: String, token: String): List<ShopOrder> {
        val a = org.json.JSONArray(request("/shops/orders/of/$buyerId", token = token))
        return (0 until a.length()).map { shopOrderOf(a.getJSONObject(it)) }
    }

    suspend fun advanceShopOrder(shopId: String, orderId: String, party: String,
                                 to: String, token: String): ShopOrder =
        shopOrderOf(JSONObject(request("/shops/$shopId/orders/$orderId/advance",
            "POST", JSONObject().put("party", party).put("to", to), token)))

    // ---- your corner: switches, messages, the homepage (qrme/social.py) ----

    private fun flagsOf(o: JSONObject): Map<String, Boolean> {
        val out = mutableMapOf<String, Boolean>()
        o.keys().forEach { k -> out[k] = o.getBoolean(k) }
        return out
    }

    suspend fun features(profileId: String, token: String): Map<String, Boolean> =
        flagsOf(JSONObject(request("/profiles/$profileId/features", token = token)))

    suspend fun setFeature(profileId: String, feature: String, enabled: Boolean,
                           token: String): Map<String, Boolean> =
        flagsOf(JSONObject(request("/profiles/$profileId/features", "PUT",
            JSONObject().put("feature", feature).put("enabled", enabled), token)))

    suspend fun sendDm(profileId: String, to: String, body: String, token: String) {
        request("/profiles/$profileId/messages", "POST",
                JSONObject().put("to", to).put("body", body), token)
    }

    suspend fun dmThreads(profileId: String, token: String): List<DmThread> {
        val o = JSONObject(request("/profiles/$profileId/messages", token = token))
        val a = o.optJSONArray("threads") ?: return emptyList()
        return (0 until a.length()).map { i ->
            val t = a.getJSONObject(i)
            DmThread(t.optString("other_id"),
                if (t.isNull("other_name")) null else t.optString("other_name"),
                t.optInt("messages"))
        }
    }

    suspend fun dmThread(profileId: String, withId: String,
                         token: String): List<DmMessage> {
        val o = JSONObject(request(
            "/profiles/$profileId/messages?with_id=$withId", token = token))
        val a = o.optJSONArray("messages") ?: return emptyList()
        return (0 until a.length()).map { i ->
            val m = a.getJSONObject(i)
            DmMessage(m.getString("id"), m.optString("sender_id"),
                      m.optString("body"))
        }
    }

    suspend fun homepage(profileId: String, token: String?): HomepageDoc {
        val o = JSONObject(request("/profiles/$profileId/homepage", token = token))
        val theme = o.optJSONObject("theme")
        return HomepageDoc(o.optString("headline"), o.optString("about"),
            theme?.optString("bg") ?: "#1a1333",
            theme?.optString("accent") ?: "#7b5cff")
    }

    suspend fun editHomepage(profileId: String, headline: String, about: String,
                             bg: String, accent: String, token: String): HomepageDoc {
        val body = JSONObject().put("headline", headline).put("about", about)
            .put("theme", JSONObject().put("bg", bg).put("accent", accent))
        val o = JSONObject(request("/profiles/$profileId/homepage", "PUT", body, token))
        val theme = o.optJSONObject("theme")
        return HomepageDoc(o.optString("headline"), o.optString("about"),
            theme?.optString("bg") ?: "#1a1333",
            theme?.optString("accent") ?: "#7b5cff")
    }

    // ---- the people around a profile: friends, the wall, comments ------

    suspend fun friends(profileId: String): List<FriendRow> {
        val o = JSONObject(request("/profiles/$profileId/friends"))
        val out = mutableListOf<FriendRow>()
        o.optJSONArray("friends")?.let { a ->
            for (i in 0 until a.length()) {
                val f = a.getJSONObject(i)
                out.add(FriendRow(f.getString("profile_id"),
                    if (f.isNull("display_name")) null else f.optString("display_name"),
                    f.optBoolean("founder"), f.optBoolean("pinned"),
                    f.optBoolean("mutual")))
            }
        }
        return out
    }

    suspend fun suggestedFriends(profileId: String): List<SuggestedRow> {
        val o = JSONObject(request("/profiles/$profileId/friends/suggested"))
        val out = mutableListOf<SuggestedRow>()
        o.optJSONArray("suggested")?.let { a ->
            for (i in 0 until a.length()) {
                val s = a.getJSONObject(i)
                out.add(SuggestedRow(s.getString("profile_id"),
                    if (s.isNull("display_name")) null else s.optString("display_name"),
                    if (s.isNull("because")) null else s.optString("because")))
            }
        }
        return out
    }

    suspend fun addFriend(profileId: String, friendId: String, token: String) {
        request("/profiles/$profileId/friends", "POST",
                JSONObject().put("friend_id", friendId), token)
    }

    /** The deed, never the words: a row names the kind and the actor; the
     *  sentence for each kind is this shell's, from L10n. */
    suspend fun inbox(profileId: String, token: String): InboxPage {
        val o = JSONObject(request("/profiles/$profileId/inbox", token = token))
        val out = mutableListOf<InboxEvent>()
        o.optJSONArray("events")?.let { a ->
            for (i in 0 until a.length()) {
                val e = a.getJSONObject(i)
                out.add(InboxEvent(e.getString("id"), e.getString("kind"),
                    e.getString("actor_id"),
                    if (e.isNull("actor_name")) null
                    else e.optString("actor_name"),
                    e.optBoolean("seen")))
            }
        }
        return InboxPage(out, o.optInt("unseen"))
    }

    suspend fun markInboxSeen(profileId: String, token: String) {
        request("/profiles/$profileId/inbox/seen", "POST", token = token)
    }

    /** Pinned rows refuse with 409; the list marks them so the control is
     *  left off rather than offered and failing. */
    suspend fun removeFriend(profileId: String, friendId: String, token: String) {
        request("/profiles/$profileId/friends/$friendId", "DELETE", token = token)
    }

    private fun postOf(o: JSONObject) = WallPost(
        o.getString("id"), o.optString("body"),
        o.optString("status"), o.optInt("likes"))

    suspend fun wall(profileId: String): List<WallPost> {
        val o = JSONObject(request("/profiles/$profileId/wall"))
        val out = mutableListOf<WallPost>()
        o.optJSONArray("posts")?.let { a ->
            for (i in 0 until a.length()) out.add(postOf(a.getJSONObject(i)))
        }
        return out
    }

    suspend fun postToWall(profileId: String, body: String,
                           token: String): WallPost {
        return postOf(JSONObject(request("/profiles/$profileId/wall", "POST",
            JSONObject().put("body", body), token)))
    }

    suspend fun comments(kind: String, targetId: String,
                         token: String): List<CommentRow> {
        val o = JSONObject(request("/$kind/$targetId/comments", token = token))
        val out = mutableListOf<CommentRow>()
        o.optJSONArray("comments")?.let { a ->
            for (i in 0 until a.length()) {
                val c = a.getJSONObject(i)
                out.add(CommentRow(c.getString("id"), c.optString("author_id"),
                    c.optString("body"), c.optString("status")))
            }
        }
        return out
    }

    suspend fun addComment(kind: String, targetId: String, body: String,
                           token: String) {
        request("/$kind/$targetId/comments", "POST",
                JSONObject().put("body", body), token)
    }

    suspend fun deleteComment(commentId: String, token: String) {
        request("/comments/$commentId", "DELETE", token = token)
    }


    // ---- standing behind the counter: desks, the market, exchanges ----
    //
    // The caller's side shipped long ago. What no shell could do was the
    // other side of the same counter — open a desk, staff it, decide who
    // comes through, print its sticker — nor search, price, sell or buy in
    // the market, nor be a party to an exchange at all.

    private fun deskOpenedOf(o: JSONObject) = DeskOpened(
        o.optString("desk_id"), o.optString("display_name"),
        o.optString("trade").ifBlank { null },
        o.optString("location").ifBlank { null },
        o.optString("presence"), o.optBoolean("rated"),
        o.optString("desk_token").ifBlank { null })

    suspend fun desks(): List<DeskBrief> {
        val a = JSONArray(request("/desks"))
        val out = mutableListOf<DeskBrief>()
        for (i in 0 until a.length()) {
            val d = a.getJSONObject(i)
            out.add(DeskBrief(d.getString("id"), d.optString("display_name"),
                if (d.isNull("trade")) null else d.optString("trade"),
                o2(d, "location"), d.optString("presence")))
        }
        return out
    }

    /** A 204 — or any success with an empty body — is the route saying
     *  "done, nothing to report". `JSONObject("")` throws, which turned
     *  every successful delete into an error on screen. */
    private fun bodyOf(raw: String) =
        JSONObject(if (raw.isBlank()) "{}" else raw)

    private fun o2(o: JSONObject, key: String) =
        if (o.isNull(key)) null else o.optString(key)

    suspend fun openDesk(ownerId: String, displayName: String, trade: String,
                         attestor: String, basis: String, location: String,
                         blurb: String, token: String): DeskOpened {
        val body = JSONObject().put("owner_id", ownerId)
            .put("display_name", displayName).put("trade", trade)
            .put("attestor", attestor).put("basis", basis)
        if (location.isNotBlank()) body.put("location", location)
        if (blurb.isNotBlank()) body.put("blurb", blurb)
        return deskOpenedOf(JSONObject(request("/desks", "POST", body, token)))
    }

    suspend fun setDeskPresence(deskId: String, presence: String,
                                token: String): DeskOpened {
        return deskOpenedOf(JSONObject(request("/desks/$deskId/presence", "PUT",
            JSONObject().put("presence", presence), token)))
    }

    suspend fun setDeskPortrait(deskId: String, token: String): DeskOpened {
        return deskOpenedOf(JSONObject(request("/desks/$deskId/portrait", "PUT",
            JSONObject().put("asset", JSONObject.NULL), token)))
    }

    // The route points a desk at a camera by address and clears it with an
    // empty one. `enabled` was a switch with nothing to switch on.
    suspend fun setDeskCamera(deskId: String, url: String,
                              token: String): DeskOpened {
        return deskOpenedOf(JSONObject(request("/desks/$deskId/camera", "PUT",
            JSONObject().put("url", url), token)))
    }

    suspend fun deskRings(deskId: String, token: String): List<DeskRing> {
        val o = JSONObject(request("/desks/$deskId/rings", token = token))
        val out = mutableListOf<DeskRing>()
        o.optJSONArray("rings")?.let { a ->
            for (i in 0 until a.length()) {
                val r = a.getJSONObject(i)
                out.add(DeskRing(r.getString("id"), o2(r, "note")))
            }
        }
        return out
    }

    suspend fun ackDeskRing(deskId: String, ringId: String, token: String) {
        request("/desks/$deskId/rings/$ringId/ack", "POST", token = token)
    }

    suspend fun askToJoinDesk(deskId: String, note: String, token: String) {
        request("/desks/$deskId/guests", "POST",
                JSONObject().put("note", note), token)
    }

    suspend fun deskGuests(deskId: String, token: String): List<DeskGuest> {
        val o = JSONObject(request("/desks/$deskId/guests", token = token))
        val out = mutableListOf<DeskGuest>()
        o.optJSONArray("guests")?.let { a ->
            for (i in 0 until a.length()) {
                val g = a.getJSONObject(i)
                out.add(DeskGuest(g.getString("id"), g.optString("guest_id"),
                    o2(g, "display_name"), g.optString("status")))
            }
        }
        return out
    }

    suspend fun acceptDeskGuest(deskId: String, requestId: String,
                                token: String) {
        request("/desks/$deskId/guests/$requestId/accept", "POST",
                token = token)
    }

    suspend fun declineDeskGuest(deskId: String, requestId: String,
                                 token: String) {
        request("/desks/$deskId/guests/$requestId/decline", "POST",
                token = token)
    }

    /** The caller's own way out — theirs to press, not the desk's. */
    suspend fun leaveDesk(deskId: String, token: String) {
        request("/desks/$deskId/guests/me", "DELETE", token = token)
    }

    suspend fun addDeskBeacon(deskId: String, label: String, token: String) {
        request("/desks/$deskId/beacons", "POST",
                JSONObject().put("label", label), token)
    }

    suspend fun deskBeacons(deskId: String, token: String): List<DeskBeacon> {
        val o = JSONObject(request("/desks/$deskId/beacons", token = token))
        val out = mutableListOf<DeskBeacon>()
        o.optJSONArray("beacons")?.let { a ->
            for (i in 0 until a.length()) {
                val b = a.getJSONObject(i)
                out.add(DeskBeacon(b.getString("id"), o2(b, "label")))
            }
        }
        return out
    }

    suspend fun removeDeskBeacon(beaconId: String, token: String) {
        request("/desk-beacons/$beaconId", "DELETE", token = token)
    }

    /** The sticker itself, as a URL an image view can fetch. Built with
     *  `URL(...)` like the other byte-answering routes in this shell — the
     *  JSON helper cannot carry an image, and the door is the fetch the
     *  image view does. */
    fun deskBeaconQrUrl(beaconId: String): String =
        java.net.URL("$base/desk-beacons/$beaconId/qr.svg").toString()

    /** What the desk looks like right now, as a still. */
    fun deskViewUrl(deskId: String): String =
        java.net.URL("$base/desks/$deskId/view.webp").toString()

    suspend fun deskOverlay(deskId: String): DeskOverlay {
        val o = JSONObject(request("/desks/$deskId/overlay"))
        return DeskOverlay(o.optInt("likes"), o.optInt("shares"),
                           o.optInt("waiting"))
    }

    suspend fun deskLivePerson(deskId: String): String {
        val o = JSONObject(request("/desks/$deskId/live-person"))
        return o.optString("owner_id")
    }

    // ---- the market, from both sides ----------------------------------

    suspend fun marketplace(): List<MarketCard> {
        val a = JSONArray(request("/marketplace"))
        val out = mutableListOf<MarketCard>()
        for (i in 0 until a.length()) {
            val m = a.getJSONObject(i)
            out.add(MarketCard(m.getString("profile_id"),
                m.optString("display_name"), o2(m, "blurb")))
        }
        return out
    }

    suspend fun marketSearch(query: String): List<MarketHit> {
        val o = JSONObject(request("/marketplace/search?q=" +
            java.net.URLEncoder.encode(query, "UTF-8")))
        val out = mutableListOf<MarketHit>()
        o.optJSONArray("results")?.let { a ->
            for (i in 0 until a.length()) {
                val h = a.getJSONObject(i)
                out.add(MarketHit(h.getString("id"), h.optString("title")))
            }
        }
        return out
    }

    suspend fun marketLocalities(): List<String> {
        val a = JSONArray(request("/marketplace/localities"))
        return (0 until a.length()).map { a.getString(it) }
    }

    suspend fun marketAssist(need: String): List<String> {
        val o = JSONObject(request("/marketplace/assist", "POST",
            JSONObject().put("need", need)))
        val out = mutableListOf<String>()
        o.optJSONArray("suggestions")?.let { a ->
            for (i in 0 until a.length()) out.add(a.getString(i))
        }
        return out
    }

    /** The demo shelf: one press and the market has something on it. */
    suspend fun seedMarketplace(): Int {
        val o = JSONObject(request("/marketplace/seed", "POST"))
        return o.optInt("created")
    }

    suspend fun listInMarketplace(profileId: String, blurb: String,
                                  tags: List<String>, token: String) {
        val arr = JSONArray()
        tags.forEach { arr.put(it) }
        // Listing takes a blurb and tags; where it is offered is placeListing.
        request("/profiles/$profileId/marketplace", "POST",
                JSONObject().put("blurb", blurb).put("tags", arr), token)
    }

    suspend fun unlistFromMarketplace(profileId: String, token: String) {
        request("/profiles/$profileId/marketplace", "DELETE", token = token)
    }

    suspend fun removeMarketListing(listingId: String, token: String) {
        request("/marketplace/listings/$listingId", "DELETE", token = token)
    }

    suspend fun listingOffer(listingId: String): MarketOffer {
        val o = JSONObject(request("/marketplace/listings/$listingId/offer"))
        return MarketOffer(if (o.isNull("amount")) null else o.optDouble("amount"),
                           o.optString("currency"))
    }

    suspend fun setListingOffer(listingId: String, price: Double,
                                stock: Int?, token: String) {
        // OfferIn is price / currency / stock.
        val body = JSONObject().put("price", price).put("currency", "USD")
        if (stock != null) body.put("stock", stock)
        request("/marketplace/listings/$listingId/offer", "PUT", body, token)
    }

    suspend fun clearListingOffer(listingId: String, token: String) {
        request("/marketplace/listings/$listingId/offer", "DELETE",
                token = token)
    }

    // `locality` is what ListingPlace declares — somewhere a person typed.
    // `venue` is a key from qrme.rated.VENUES and belongs to a different
    // model; sent here it 422'd, so placing a listing has never worked from
    // any native shell.
    suspend fun placeListing(listingId: String, locality: String,
                             token: String) {
        request("/marketplace/listings/$listingId/place", "PUT",
                JSONObject().put("locality", locality), token)
    }

    suspend fun unplaceListing(listingId: String, token: String) {
        request("/marketplace/listings/$listingId/place", "DELETE",
                token = token)
    }

    suspend fun purchaseListing(listingId: String, token: String) {
        request("/marketplace/listings/$listingId/purchase", "POST",
                token = token)
    }

    suspend fun marketSales(token: String): List<MarketSale> {
        val o = JSONObject(request("/marketplace/sales", token = token))
        val out = mutableListOf<MarketSale>()
        o.optJSONArray("sales")?.let { a ->
            for (i in 0 until a.length()) {
                val s = a.getJSONObject(i)
                out.add(MarketSale(s.getString("id"), s.optString("status")))
            }
        }
        return out
    }

    data class MarketPrefs(val locality: String,
                           val includeRemote: Boolean)

    suspend fun marketSettings(interactorId: String,
                               token: String): MarketPrefs {
        val o = JSONObject(request("/marketplace/settings/$interactorId",
                                   token = token))
        return MarketPrefs(o.optString("locality", ""),
                           o.optBoolean("include_remote", true))
    }

    // MarketPrefs is where "here" is and how far out to look.
    suspend fun setMarketSettings(interactorId: String, locality: String,
                                  includeRemote: Boolean, token: String) {
        request("/marketplace/settings/$interactorId", "PUT",
                JSONObject().put("locality", locality)
                    .put("include_remote", includeRemote), token)
    }

    // ---- exchanges: two parties, one manifest --------------------------

    suspend fun exchangeVocabulary(): ExchangeVocabulary {
        val o = JSONObject(request("/exchanges/vocabulary"))
        fun strings(key: String): List<String> {
            val out = mutableListOf<String>()
            o.optJSONArray(key)?.let { a ->
                for (i in 0 until a.length()) out.add(a.getString(i))
            }
            return out
        }
        return ExchangeVocabulary(strings("industries"), strings("rules"))
    }

    private fun dealOf(o: JSONObject): ExchangeDeal {
        val items = mutableListOf<ExchangeItemRow>()
        o.optJSONArray("items")?.let { a ->
            for (i in 0 until a.length()) {
                val it = a.getJSONObject(i)
                items.add(ExchangeItemRow(it.getString("id"),
                    it.optString("name"), it.optString("kind")))
            }
        }
        return ExchangeDeal(o.getString("id"), o2(o, "work"),
                            o.optString("state"), items)
    }

    suspend fun proposeExchange(hostId: String, guestId: String, work: String,
                                industry: String, fee: Double,
                                token: String): ExchangeDeal {
        return dealOf(JSONObject(request("/exchanges", "POST",
            JSONObject().put("host_id", hostId).put("guest_id", guestId)
                .put("work", work).put("industry", industry).put("fee", fee),
            token)))
    }

    suspend fun exchange(exchangeId: String, token: String): ExchangeDeal {
        return dealOf(JSONObject(request("/exchanges/$exchangeId",
                                         token = token)))
    }

    suspend fun myExchanges(partyId: String,
                            token: String): List<ExchangeDeal> {
        val o = JSONObject(request("/parties/$partyId/exchanges",
                                   token = token))
        val out = mutableListOf<ExchangeDeal>()
        o.optJSONArray("exchanges")?.let { a ->
            for (i in 0 until a.length()) out.add(dealOf(a.getJSONObject(i)))
        }
        return out
    }

    suspend fun addExchangeItem(exchangeId: String, direction: String,
                                name: String, kind: String, token: String) {
        request("/exchanges/$exchangeId/items", "POST",
                JSONObject().put("direction", direction).put("name", name)
                    .put("kind", kind), token)
    }

    suspend fun removeExchangeItem(exchangeId: String, itemId: String,
                                   token: String) {
        request("/exchanges/$exchangeId/items/$itemId", "DELETE",
                token = token)
    }

    /** Each item is accepted separately — nothing moves by itself. */
    suspend fun acceptExchangeItem(exchangeId: String, itemId: String,
                                   token: String) {
        request("/exchanges/$exchangeId/items/$itemId/accept", "POST",
                token = token)
    }

    /** Both parties sign the same manifest; any change clears both. */
    suspend fun signExchange(exchangeId: String, actorId: String,
                             token: String): ExchangeDeal {
        return dealOf(JSONObject(request("/exchanges/$exchangeId/sign", "POST",
            JSONObject().put("actor_id", actorId), token)))
    }

    suspend fun reopenExchange(exchangeId: String, actorId: String,
                               token: String): ExchangeDeal {
        return dealOf(JSONObject(request("/exchanges/$exchangeId/reopen",
            "POST", JSONObject().put("actor_id", actorId), token)))
    }

    suspend fun withdrawFromExchange(exchangeId: String, actorId: String,
                                     token: String): ExchangeDeal {
        return dealOf(JSONObject(request("/exchanges/$exchangeId/withdraw",
            "POST", JSONObject().put("actor_id", actorId), token)))
    }

    suspend fun exchangeChannel(exchangeId: String, token: String): String {
        val o = JSONObject(request("/exchanges/$exchangeId/channel",
                                   token = token))
        return o.optString("room_id")
    }

    // -- the crowd, the couch and the loan --------------------------------
    // Audience verbs, the watch party, and skill grants: three blocks the
    // doorless records said this phone could not reach.

    suspend fun like(kind: String, targetId: String, token: String) {
        request("/$kind/$targetId/like", "POST", token = token)
    }

    suspend fun unlike(kind: String, targetId: String, token: String) {
        request("/$kind/$targetId/like", "DELETE", token = token)
    }

    suspend fun share(kind: String, targetId: String, token: String): String {
        val o = JSONObject(request("/$kind/$targetId/share", "POST",
            JSONObject().put("channel", "link"), token))
        return o.optString("url")
    }

    suspend fun counts(kind: String, targetId: String,
                       token: String): AudienceCounts {
        val o = JSONObject(request("/$kind/$targetId/audience",
            token = token))
        return AudienceCounts(o.optInt("likes"), o.optInt("comments"),
            o.optInt("shares"), o.optInt("subscribers"))
    }

    suspend fun subscribe(kind: String, subjectId: String, token: String) {
        request("/$kind/$subjectId/subscribe", "POST",
            JSONObject().put("tier", "follow"), token)
    }

    suspend fun unsubscribe(kind: String, subjectId: String, token: String) {
        request("/$kind/$subjectId/subscribe", "DELETE",
            token = token)
    }

    suspend fun subscribers(kind: String, subjectId: String,
                            token: String): Int {
        val o = JSONObject(request("/$kind/$subjectId/subscribers",
            token = token))
        return o.optJSONArray("subscribers")?.length() ?: 0
    }

    // A gift is a gift: the backend refuses to reverse it, and requires the
    // giver to be a verified adult.
    suspend fun gift(kind: String, subjectId: String, amount: Double,
                     note: String, token: String) {
        request("/$kind/$subjectId/gift", "POST",
            JSONObject().put("amount", amount).put("note", note), token)
    }

    suspend fun gifts(kind: String, subjectId: String,
                      token: String): List<GiftRow> {
        val o = JSONObject(request("/$kind/$subjectId/gifts",
            token = token))
        val out = mutableListOf<GiftRow>()
        o.optJSONArray("gifts")?.let { a ->
            for (i in 0 until a.length()) {
                val g = a.getJSONObject(i)
                out.add(GiftRow(g.optString("giver_id"),
                    g.optDouble("amount", 0.0), g.optString("note")))
            }
        }
        return out
    }

    private fun partyOf(o: JSONObject) = PartyCard(
        o.optString("id", o.optString("party_id")), o.optString("title"),
        o.optString("state"), o.optInt("position_s"),
        o.optJSONArray("members")?.length() ?: 0)

    suspend fun startParty(postId: String, hostId: String, title: String,
                           token: String): PartyCard =
        partyOf(JSONObject(request("/watch-parties", "POST",
            JSONObject().put("post_id", postId).put("host_id", hostId)
                .put("title", title), token)))

    suspend fun party(partyId: String, token: String): PartyCard =
        partyOf(JSONObject(request("/watch-parties/$partyId",
            token = token)))

    suspend fun joinParty(partyId: String, memberId: String,
                          token: String): PartyCard =
        partyOf(JSONObject(request("/watch-parties/$partyId/members",
            "POST", JSONObject().put("member_id", memberId)
                .put("kind", "profile"), token)))

    suspend fun leaveParty(partyId: String, memberId: String, token: String) {
        request("/watch-parties/$partyId/members/$memberId",
            "DELETE", token = token)
    }

    // Moves a number; presses play on nobody's device.
    suspend fun seekParty(partyId: String, hostId: String, positionS: Int,
                          token: String): PartyCard =
        partyOf(JSONObject(request("/watch-parties/$partyId/seek",
            "POST", JSONObject().put("host_id", hostId)
                .put("position_s", positionS).put("playing", true), token)))

    suspend fun sayInParty(partyId: String, memberId: String, body: String,
                           token: String) {
        request("/watch-parties/$partyId/chat", "POST",
            JSONObject().put("member_id", memberId).put("body", body), token)
    }

    suspend fun partyChat(partyId: String, token: String): List<PartyLine> {
        val o = JSONObject(request("/watch-parties/$partyId/chat",
            token = token))
        val out = mutableListOf<PartyLine>()
        o.optJSONArray("lines")?.let { a ->
            for (i in 0 until a.length()) {
                val l = a.getJSONObject(i)
                out.add(PartyLine(l.optString("member_id"),
                    l.optString("body")))
            }
        }
        return out
    }

    suspend fun endParty(partyId: String, token: String): PartyCard =
        partyOf(JSONObject(request("/watch-parties/$partyId/end",
            "POST", token = token)))

    /** The browse door: parties whose hosts chose to be found. No token —
     *  public means public; counts and a facade, names stay members-only. */
    suspend fun publicParties(): List<Triple<String, String, Int>> {
        val o = JSONObject(request("/watch-parties/public"))
        val arr = o.getJSONArray("parties")
        return (0 until arr.length()).map { i ->
            val p = arr.getJSONObject(i)
            Triple(p.getString("id"), p.optString("title"), p.optInt("people"))
        }
    }

    /** Host only, both directions — the id stays the private door. */
    suspend fun publishParty(partyId: String, token: String): PartyCard =
        partyOf(JSONObject(request("/watch-parties/$partyId/listing",
            "POST", token = token)))

    suspend fun unpublishParty(partyId: String, token: String): PartyCard =
        partyOf(JSONObject(request("/watch-parties/$partyId/listing",
            "DELETE", token = token)))

    /** The sentence a synthetic member carries: it has not seen the footage. */
    suspend fun partyContext(partyId: String, token: String): String {
        val o = JSONObject(request("/watch-parties/$partyId/context",
            token = token))
        return o.optString("you_have_not_seen_it")
    }

    private fun grantOf(o: JSONObject) = GrantCard(
        o.optString("id", o.optString("grant_id")), o.optString("title"),
        o.optString("state"), o.optString("lender_id"),
        o.optString("borrower_id"))

    suspend fun grantTerms(): List<String> {
        val o = JSONObject(request("/skill-grants/vocabulary"))
        val out = mutableListOf<String>()
        o.optJSONArray("terms")?.let { a ->
            for (i in 0 until a.length()) out.add(a.getString(i))
        }
        return out
    }

    suspend fun offerGrant(lenderId: String, borrowerId: String,
                           surface: String, surfaceId: String,
                           skillKind: String, skillRef: String, title: String,
                           token: String): GrantCard =
        grantOf(JSONObject(request("/skill-grants", "POST",
            JSONObject().put("lender_id", lenderId)
                .put("borrower_id", borrowerId).put("surface", surface)
                .put("surface_id", surfaceId).put("skill_kind", skillKind)
                .put("skill_ref", skillRef).put("title", title), token)))

    suspend fun grant(grantId: String, token: String): GrantCard =
        grantOf(JSONObject(request("/skill-grants/$grantId",
            token = token)))

    suspend fun acceptGrant(grantId: String, actorId: String, token: String) {
        request("/skill-grants/$grantId/accept", "POST",
            JSONObject().put("actor_id", actorId), token)
    }

    suspend fun declineGrant(grantId: String, actorId: String, token: String) {
        request("/skill-grants/$grantId/decline", "POST",
            JSONObject().put("actor_id", actorId), token)
    }

    suspend fun closeGrant(grantId: String, actorId: String, token: String) {
        request("/skill-grants/$grantId/close", "POST",
            JSONObject().put("actor_id", actorId), token)
    }

    suspend fun useGrant(grantId: String, borrowerId: String, what: String,
                         token: String) {
        request("/skill-grants/$grantId/use", "POST",
            JSONObject().put("borrower_id", borrowerId).put("what", what),
            token)
    }

    suspend fun grantUses(grantId: String, token: String): List<GrantUse> {
        val o = JSONObject(request("/skill-grants/$grantId/uses",
            token = token))
        val out = mutableListOf<GrantUse>()
        o.optJSONArray("uses")?.let { a ->
            for (i in 0 until a.length()) {
                val u = a.getJSONObject(i)
                out.add(GrantUse(u.optString("used_at"), u.optString("what")))
            }
        }
        return out
    }

    suspend fun grantsInSurface(surface: String, surfaceId: String,
                                token: String): List<GrantCard> {
        val o = JSONObject(request(
            "/surfaces/$surface/$surfaceId/skill-grants", token = token))
        val out = mutableListOf<GrantCard>()
        o.optJSONArray("grants")?.let { a ->
            for (i in 0 until a.length()) out.add(grantOf(a.getJSONObject(i)))
        }
        return out
    }

    suspend fun myGrants(personId: String, token: String): List<GrantCard> {
        val o = JSONObject(request("/people/$personId/skill-grants",
            token = token))
        val out = mutableListOf<GrantCard>()
        for (key in listOf("lending", "borrowing")) {
            o.optJSONArray(key)?.let { a ->
                for (i in 0 until a.length()) out.add(grantOf(a.getJSONObject(i)))
            }
        }
        return out
    }

    // -- the place, the camera, the organization and the tour -------------
    // Four more blocks off the doorless records. Disclosure-first: who
    // here has lent a microphone and who wears what are readable by
    // everyone present, because a disclosure only its subject can see is
    // not a disclosure.

    suspend fun whose(surface: String, surfaceId: String): String {
        val o = JSONObject(request("/places/$surface/$surfaceId/whose"))
        return o.optString("display_name")
    }

    suspend fun lendMicrophone(surface: String, surfaceId: String,
                               interactorId: String, token: String) {
        request("/places/$surface/$surfaceId/microphone", "POST",
            JSONObject().put("interactor_id", interactorId), token)
    }

    suspend fun takeBackMicrophone(surface: String, surfaceId: String,
                                   interactorId: String, token: String) {
        request("/places/$surface/$surfaceId/microphone", "DELETE",
            JSONObject().put("interactor_id", interactorId), token)
    }

    suspend fun microphoneDisclosure(surface: String, surfaceId: String,
                                     token: String): List<String> {
        val o = JSONObject(request("/places/$surface/$surfaceId/microphone",
            token = token))
        val out = mutableListOf<String>()
        o.optJSONArray("microphones_lent")?.let { a ->
            for (i in 0 until a.length()) {
                val m = a.getJSONObject(i)
                out.add(m.optString("interactor_id") + " · " +
                    m.optString("device"))
            }
        }
        return out
    }

    suspend fun wearOverlay(surface: String, surfaceId: String,
                            interactorId: String, kind: String, title: String,
                            token: String) {
        request("/places/$surface/$surfaceId/overlay", "POST",
            JSONObject().put("interactor_id", interactorId).put("kind", kind)
                .put("title", title), token)
    }

    suspend fun takeOffOverlay(surface: String, surfaceId: String,
                               interactorId: String, token: String) {
        request("/places/$surface/$surfaceId/overlay", "DELETE",
            JSONObject().put("interactor_id", interactorId), token)
    }

    suspend fun wornOverlays(surface: String, surfaceId: String,
                             token: String): List<String> {
        val o = JSONObject(request("/places/$surface/$surfaceId/overlay",
            token = token))
        val out = mutableListOf<String>()
        o.optJSONArray("overlays")?.let { a ->
            for (i in 0 until a.length()) {
                val w = a.getJSONObject(i)
                out.add(w.optString("interactor_id") + " · " +
                    w.optString("title", w.optString("kind")))
            }
        }
        return out
    }

    /** The published refusals, verbatim — a client that knew only the
     *  allowed combinations would draw a refused one as a missing feature
     *  rather than a decision. */
    suspend fun cameraRefusals(): List<String> {
        val o = JSONObject(request("/camera/vocabulary"))
        val out = mutableListOf<String>()
        o.optJSONObject("never")?.let { n ->
            for (key in n.keys()) out.add(n.optString(key))
        }
        return out
    }

    suspend fun bystanderGuidance(subject: String): String {
        val o = JSONObject(request("/camera/bystanders/$subject"))
        return o.optString("guidance")
    }

    suspend fun openCamera(holderId: String, surface: String,
                           surfaceId: String, subject: String,
                           viewerId: String, minutes: Int,
                           token: String): String {
        val o = JSONObject(request("/camera/sessions", "POST",
            JSONObject().put("holder_id", holderId).put("surface", surface)
                .put("surface_id", surfaceId).put("subject", subject)
                .put("viewer_kind", "person").put("viewer_id", viewerId)
                .put("minutes", minutes), token))
        return o.optString("id")
    }

    suspend fun cameraSession(sessionId: String, token: String): String {
        val o = JSONObject(request("/camera/sessions/$sessionId",
            token = token))
        return o.optString("subject") + " · " + o.optString("state")
    }

    suspend fun closeCamera(sessionId: String, actorId: String,
                            token: String) {
        request("/camera/sessions/$sessionId/close", "POST",
            JSONObject().put("actor_id", actorId), token)
    }

    suspend fun myCameras(holderId: String, token: String): List<String> {
        val a = org.json.JSONArray(request("/camera/live/$holderId",
            token = token))
        val out = mutableListOf<String>()
        for (i in 0 until a.length()) {
            val s = a.getJSONObject(i)
            out.add(s.optString("id") + " · " + s.optString("subject"))
        }
        return out
    }

    suspend fun cameraDisclosure(surface: String, surfaceId: String,
                                 token: String): String {
        val o = JSONObject(request("/camera/disclosure/$surface/$surfaceId",
            token = token))
        return o.toString()
    }

    suspend fun organizations(token: String): List<Pair<String, String>> {
        val a = org.json.JSONArray(request("/organizations", token = token))
        val out = mutableListOf<Pair<String, String>>()
        for (i in 0 until a.length()) {
            val o = a.getJSONObject(i)
            out.add(o.optString("id") to o.optString("name"))
        }
        return out
    }

    suspend fun createOrganization(name: String, token: String): String {
        val o = JSONObject(request("/organizations", "POST",
            JSONObject().put("name", name), token))
        return o.optString("id")
    }

    suspend fun seedDemoOrganization(token: String): String {
        val o = JSONObject(request("/organizations/demo", "POST",
            token = token))
        return o.optString("id")
    }

    suspend fun organization(orgId: String, token: String): String {
        val o = JSONObject(request("/organizations/$orgId", token = token))
        return o.optString("name") + " · " +
            (o.optJSONArray("departments")?.length() ?: 0)
    }

    suspend fun addDepartment(orgId: String, name: String, role: String,
                              profileId: String, token: String) {
        request("/organizations/$orgId/departments", "POST",
            JSONObject().put("name", name).put("role", role)
                .put("profile_id", profileId), token)
    }

    /** AI for lease: seat somebody else's licensed specialist as a
     *  department; the fee accrues to its owner, who can revoke any time. */
    suspend fun leaseSpecialist(orgId: String, profileId: String,
                                name: String, role: String,
                                token: String): String {
        val o = JSONObject(request("/organizations/$orgId/lease", "POST",
            JSONObject().put("profile_id", profileId).put("name", name)
                .put("role", role), token))
        return o.optString("lease_id")
    }

    suspend fun coordinate(orgId: String, goal: String,
                           fromDepartment: String, token: String) {
        request("/organizations/$orgId/coordinate", "POST",
            JSONObject().put("goal", goal)
                .put("from_department", fromDepartment), token)
    }

    suspend fun coordinations(orgId: String, token: String): List<String> {
        val a = org.json.JSONArray(request(
            "/organizations/$orgId/coordinations", token = token))
        val out = mutableListOf<String>()
        for (i in 0 until a.length()) {
            val c = a.getJSONObject(i)
            out.add(c.optString("goal") + " · " + c.optString("status"))
        }
        return out
    }

    suspend fun tutorialOutline(): List<Pair<String, String>> {
        val o = JSONObject(request("/tutorial"))
        val out = mutableListOf<Pair<String, String>>()
        // A chapter is a name and the lessons under it. Reading `key` and
        // `title` off the chapter gave every row an empty pair, and
        // `lessons` was never a key the route sent.
        o.optJSONArray("chapters")?.let { a ->
            for (i in 0 until a.length()) {
                val c = a.getJSONObject(i)
                val first = c.optJSONArray("steps")?.optJSONObject(0)
                out.add(c.optString("chapter") to (first?.optString("key") ?: ""))
            }
        }
        return out
    }

    suspend fun tutorialStep(key: String): String {
        val o = JSONObject(request("/tutorial/steps/$key"))
        return o.optString("what", o.optString("title"))
    }

    suspend fun tutorialForScreen(number: Int): String {
        val o = JSONObject(request("/tutorial/for-screen/$number"))
        return o.optString("title")
    }

    suspend fun startTutorial(learnerId: String): String {
        val o = JSONObject(request("/tutorial/start", "POST",
            JSONObject().put("learner_id", learnerId).put("lesson", "")))
        // All three of these answer with `tutorial.where`, which wraps
        // the step. Reading the top level got nothing at all.
        return o.optJSONObject("step")?.optString("title") ?: o.optString("note")
    }

    suspend fun tutorialProgress(learnerId: String): String {
        val o = JSONObject(request("/tutorial/progress/$learnerId"))
        return o.optJSONObject("step")?.optString("title") ?: o.optString("note")
    }

    suspend fun markTutorialDone(learnerId: String, lesson: String): String {
        val o = JSONObject(request("/tutorial/done", "POST",
            JSONObject().put("learner_id", learnerId).put("lesson", lesson)))
        return o.optJSONObject("step")?.optString("title") ?: o.optString("note")
    }

    // -- the body, the referral, the objection, the lobby and the dock ----
    // Five more blocks off the doorless records, each rendering its
    // backend's rules: the command log is the owner's audit trail, a
    // referral is signed before released and opens once, an objection's
    // subject can end it, a roster says what every callsign is, and the
    // dock reports where each face's real job lives.

    suspend fun unbindRobot(robotId: String, token: String) {
        request("/robots/$robotId", "DELETE", token = token)
    }

    suspend fun robotCommands(robotId: String, token: String): List<String> {
        val a = org.json.JSONArray(request("/robots/$robotId/commands",
            token = token))
        val out = mutableListOf<String>()
        for (i in 0 until a.length()) {
            val c = a.getJSONObject(i)
            out.add(c.optString("created_at") + " · " +
                c.optString("command"))
        }
        return out
    }

    suspend fun robotSkills(robotId: String, token: String): List<String> {
        val a = org.json.JSONArray(request("/robots/$robotId/skills",
            token = token))
        val out = mutableListOf<String>()
        for (i in 0 until a.length()) {
            val sk = a.getJSONObject(i)
            out.add(sk.optString("title") + " · " + sk.optString("pack_title"))
        }
        return out
    }

    /** A body's dials — intimacy never applies to a body. */
    suspend fun robotSteering(robotId: String, token: String): String {
        val o = JSONObject(request("/robots/$robotId/steering",
            token = token))
        return o.optJSONObject("values")?.toString() ?: "{}"
    }

    suspend fun steerRobot(robotId: String, pace: Int,
                           token: String): String {
        val o = JSONObject(request("/robots/$robotId/steering", "PUT",
            JSONObject().put("values", JSONObject().put("pace", pace)),
            token))
        return o.optJSONObject("values")?.toString() ?: "{}"
    }

    suspend fun matchClinicians(area: String): List<Pair<String, String>> {
        val a = org.json.JSONArray(request("/referrals/match?area=$area"))
        val out = mutableListOf<Pair<String, String>>()
        for (i in 0 until a.length()) {
            val c = a.getJSONObject(i)
            out.add(c.optString("id") to (c.optString("name") + " · " +
                c.optString("expertise")))
        }
        return out
    }

    /** Nothing is released here — the package comes back to be read. */
    suspend fun prepareReferral(interactorId: String, profileId: String,
                                providerId: String, token: String): String {
        val o = JSONObject(request("/referrals/prepare", "POST",
            JSONObject().put("interactor_id", interactorId)
                .put("profile_id", profileId)
                .put("provider_id", providerId), token))
        return o.optString("id", o.optString("referral_id"))
    }

    suspend fun releaseReferral(referralId: String, signatureId: String,
                                token: String) {
        request("/referrals/$referralId/release", "POST",
            JSONObject().put("signature_id", signatureId), token)
    }

    /** Once — a second attempt says so rather than quietly working. */
    suspend fun openReferral(referralId: String, linkToken: String): String {
        val o = JSONObject(request("/referrals/$referralId?token=$linkToken"))
        return o.optString("status")
    }

    suspend fun replyToReferral(referralId: String, linkToken: String,
                                content: String) {
        request("/referrals/$referralId/reply?token=$linkToken", "POST",
            JSONObject().put("content", content))
    }

    suspend fun objection(objectionId: String): String {
        val o = JSONObject(request("/objections/$objectionId"))
        return o.optString("status")
    }

    suspend fun objectionAudit(objectionId: String,
                               token: String): List<String> {
        val o = JSONObject(request("/objections/$objectionId/audit",
            token = token))
        val out = mutableListOf<String>()
        o.optJSONArray("events")?.let { a ->
            for (i in 0 until a.length()) {
                val e = a.getJSONObject(i)
                out.add(e.optString("event") +
                    (if (e.optBoolean("sealed")) " ◆" else ""))
            }
        }
        return out
    }

    suspend fun withdrawObjectionConsent(objectionId: String): String {
        val o = JSONObject(request("/objections/$objectionId/withdraw",
            "POST"))
        return o.optString("status")
    }

    suspend fun revokeObjectionBasis(objectionId: String): String {
        val o = JSONObject(request("/objections/$objectionId/revoke", "POST"))
        return o.optString("status")
    }

    /** Reviewer-only — an owner cannot adjudicate an objection against
     *  their own profile, and the backend enforces it by role. */
    suspend fun resolveObjection(objectionId: String, outcome: String,
                                 token: String): String {
        val o = JSONObject(request("/objections/$objectionId/resolve", "POST",
            JSONObject().put("outcome", outcome), token))
        return o.optString("status")
    }

    suspend fun lobbyRules(): List<String> {
        val o = JSONObject(request("/gaming/lobby/vocabulary"))
        val out = mutableListOf<String>()
        o.optJSONArray("rules")?.let { a ->
            for (i in 0 until a.length()) out.add(a.getString(i))
        }
        return out
    }

    suspend fun seatInLobby(sessionId: String, memberKind: String,
                            memberId: String, role: String, token: String) {
        request("/gaming/sessions/$sessionId/lobby", "POST",
            JSONObject().put("member_kind", memberKind)
                .put("member_id", memberId).put("role", role), token)
    }

    /** The honest roster: what each callsign is travels with it. */
    suspend fun lobbyRoster(sessionId: String,
                            token: String): List<String> {
        val o = JSONObject(request("/gaming/sessions/$sessionId/lobby",
            token = token))
        val out = mutableListOf<String>()
        o.optJSONArray("members")?.let { a ->
            for (i in 0 until a.length()) {
                val m = a.getJSONObject(i)
                out.add(m.optString("callsign", m.optString("member_id")) +
                    " · " + m.optString("member_kind") + " · " +
                    m.optString("role"))
            }
        }
        return out
    }

    suspend fun leaveLobby(sessionId: String, memberId: String,
                           token: String) {
        request("/gaming/sessions/$sessionId/lobby", "DELETE",
            JSONObject().put("member_id", memberId), token)
    }

    suspend fun lobbyContext(sessionId: String, token: String): String {
        val o = JSONObject(request(
            "/gaming/sessions/$sessionId/lobby/context", token = token))
        return o.optString("note", o.toString())
    }

    suspend fun dockFaces(): List<String> {
        val o = JSONObject(request("/dock/faces"))
        val out = mutableListOf<String>()
        o.optJSONObject("faces")?.let { f ->
            for (key in f.keys()) out.add("$key \u00b7 ${f.optString(key)}")
        }
        return out
    }

    /** The dock is read-only, so every face carries a way out of it. */
    suspend fun dockWhere(face: String): String {
        val o = JSONObject(request("/dock/where/$face"))
        return o.optString("screen") + " · " + o.optString("title")
    }

    suspend fun dockSettings(profileId: String, token: String): String {
        val o = JSONObject(request("/dock/$profileId", token = token))
        return o.optString("corner") + " · " + o.optString("state")
    }

    suspend fun configureDock(profileId: String, corner: String,
                              state: String, token: String) {
        request("/dock/$profileId", "PUT",
            JSONObject().put("corner", corner).put("state", state), token)
    }

    suspend fun dockFace(profileId: String, name: String,
                         token: String): String {
        val o = JSONObject(request("/dock/$profileId/face/$name",
            token = token))
        return o.optString("line", o.toString())
    }

    // -- the signature, the mail server, the room's ear, the wall screen,
    // the plan, the handoff and the campaign -----------------------------
    // Seven small blocks that close out the mid-sized doorless groups.

    suspend fun signatureCertificate(sigId: String): String {
        val o = JSONObject(request("/signatures/$sigId/certificate"))
        return o.optString("printed_name") + " · " + o.optString("meaning") +
            " · " + o.optString("signed_at")
    }

    /** No token, no lookup, no trust in this deployment beyond the
     *  arithmetic. */
    suspend fun verifySignaturePackage(): String {
        val o = JSONObject(request("/signatures/verify", "POST",
            JSONObject().put("package", JSONObject())))
        return o.toString()
    }

    suspend fun reproofCredential(rowId: String, level: String,
                                  attestor: String, token: String) {
        request("/signatures/credentials/$rowId/proofing", "POST",
            JSONObject().put("proofing_level", level)
                .put("proofing_attestor", attestor)
                .put("proofing_method", "document")
                .put("proofing_ref", "in-person"), token)
    }

    /** The WebAuthn ceremony page, opened in a web view — never
     *  re-implemented in the shell. */
    fun signatureCeremonyUrl(): String =
        java.net.URL("$base/signatures/ceremony").toString()

    suspend fun mailSettings(): String {
        val o = JSONObject(request("/settings/mail"))
        return o.optString("transport") + " · " + o.optString("host")
    }

    suspend fun saveMailSettings(host: String, port: Int, sender: String,
                                 token: String) {
        request("/settings/mail", "PUT",
            JSONObject().put("host", host).put("port", port)
                .put("sender", sender), token)
    }

    suspend fun forgetMailSettings(token: String) {
        request("/settings/mail", "DELETE", token = token)
    }

    /** A settings screen that saves without ever proving it can deliver is
     *  how an app ends up insisting it emailed somebody. */
    suspend fun testMailSettings(to: String, token: String) {
        request("/settings/mail/test", "POST",
            JSONObject().put("to", to), token)
    }

    suspend fun rooms(): List<Pair<String, String>> {
        val a = org.json.JSONArray(request("/rooms"))
        val out = mutableListOf<Pair<String, String>>()
        for (i in 0 until a.length()) {
            val r = a.getJSONObject(i)
            out.add(r.getString("id") to (r.optString("topic") + " · " +
                r.optString("channel") + " · " + r.optInt("participants")))
        }
        return out
    }

    /** The standing rooms: blueprints the server keeps so the Rooms door
     *  never greets a newcomer with an empty list. (key, topic, channel). */
    suspend fun roomTemplates(): List<Triple<String, String, String>> {
        val a = org.json.JSONArray(request("/rooms/templates"))
        val out = mutableListOf<Triple<String, String, String>>()
        for (i in 0 until a.length()) {
            val t = a.getJSONObject(i)
            out.add(Triple(t.getString("key"), t.optString("topic"),
                t.optString("channel")))
        }
        return out
    }

    /** Step into a live room: the token names the joiner, joining twice
     *  is being there once, and the table seats eight. */
    suspend fun joinRoom(roomId: String, token: String) {
        request("/rooms/$roomId/join", "POST", token = token)
    }

    /** Step into a standing room — the room, not a copy of it: joins the
     *  live one with a seat left, opens it fresh only when nobody is
     *  there. */
    suspend fun openStandingRoom(key: String, profileId: String,
                                 token: String): RoomCreated {
        val o = JSONObject(request(
            "/rooms/templates/$key/open?profile_id=$profileId", "POST",
            token = token))
        return RoomCreated(o.getString("id"), o.getString("topic"),
            o.getString("channel"))
    }

    suspend fun lendRoomMic(roomId: String, interactorId: String,
                            token: String) {
        request("/rooms/$roomId/mic", "POST",
            JSONObject().put("interactor_id", interactorId), token)
    }

    suspend fun takeBackRoomMic(roomId: String, interactorId: String,
                                token: String) {
        request("/rooms/$roomId/mic/$interactorId", "DELETE", token = token)
    }

    /** Ask somebody into a room you are already in. The only route that gets
     *  a particular person into a particular room without naming them in the
     *  create body — which needs their id before the room exists. Returns
     *  whether they had already been asked: a second press is not a second
     *  event, because a button that can be pressed repeatedly into somebody's
     *  inbox is a button for filling somebody's inbox. */
    suspend fun inviteToRoom(roomId: String, profileId: String,
                             token: String): Boolean {
        val o = JSONObject(request("/rooms/$roomId/invite", "POST",
            JSONObject().put("profile_id", profileId), token))
        return o.optBoolean("already_invited", false)
    }

    /** Saying yes. Authorized as the **guest** — a host who could seat
     *  somebody from their own screen would make "invite" a word for
     *  something that is not one. */
    suspend fun acceptRoomInvite(roomId: String, profileId: String,
                                 ownerToken: String) {
        request("/rooms/$roomId/invites/accept", "POST",
            JSONObject().put("profile_id", profileId), ownerToken)
    }

    // -- what each box in the room holds --
    //
    // Three answers and all three are a box: somebody with their camera off
    // keeps theirs, at the same size. See qrme/roomface.py.

    /** Everybody's box, and who is wearing what — one call, because a client
     *  that needed a second to learn whether a face is a face would draw one
     *  frame without the disclosure. In-room only: a room id rides on printed
     *  stickers, so holding one is not being here. */
    suspend fun roomFaces(roomId: String, token: String): List<String> {
        val o = JSONObject(request("/rooms/$roomId/faces", token = token))
        val out = mutableListOf<String>()
        o.optJSONObject("faces")?.let { faces ->
            for (who in faces.keys()) {
                val f = faces.getJSONObject(who)
                out.add(who + " · " + f.optString("means"))
            }
        }
        o.optJSONArray("wearing")?.let { a ->
            for (i in 0 until a.length()) {
                out.add(a.getJSONObject(i).optString("disclosure"))
            }
        }
        o.optString("note").takeIf { it.isNotEmpty() }?.let { out.add(it) }
        return out
    }

    /** Turn your camera on, or go back to a name in a box. Yours alone: the
     *  id in the body is checked against the token rather than believed. */
    suspend fun setRoomFace(roomId: String, interactorId: String,
                            showing: String, token: String) {
        request("/rooms/$roomId/face", "PUT",
            JSONObject().put("interactor_id", interactorId)
                .put("showing", showing), token)
    }

    /** Back to a name in a box — which is still a box, and still here. */
    suspend fun clearRoomFace(roomId: String, interactorId: String,
                              token: String) {
        request("/rooms/$roomId/face?interactor_id=$interactorId", "DELETE",
            token = token)
    }

    /** The picture that stands in for you here. Raw bytes like
     *  `uploadMedia`, and for the same reason: the backend reads the kind
     *  from the file's own magic numbers rather than trusting the name.
     *  Uploading also puts it up — a first press with no visible effect is
     *  how a control ends up looking broken. */
    suspend fun uploadRoomFace(roomId: String, interactorId: String,
                               filename: String, bytes: ByteArray,
                               token: String): String =
        withContext(Dispatchers.IO) {
            val q = "?interactor_id=" +
                java.net.URLEncoder.encode(interactorId, "UTF-8") +
                "&filename=" + java.net.URLEncoder.encode(filename, "UTF-8")
            val conn = (java.net.URL("$base/rooms/$roomId/face/photo" + q)
                .openConnection() as java.net.HttpURLConnection).apply {
                requestMethod = "POST"
                setRequestProperty("accept-language", L10n.deviceLanguage())
                setRequestProperty("authorization", "Bearer $token")
                doOutput = true
            }
            conn.outputStream.use { it.write(bytes) }
            val text = (if (conn.responseCode < 300) conn.inputStream
                        else conn.errorStream).bufferedReader().readText()
            JSONObject(text).optString("showing")
        }

    /** The room's name, changed from inside it. Authorized like speaking:
     *  a participant held by their own token. */
    suspend fun renameRoom(roomId: String, interactorId: String,
                           topic: String, token: String): String =
        JSONObject(request("/rooms/$roomId", "PATCH",
                           JSONObject().put("interactor_id", interactorId)
                               .put("topic", topic),
                           token = token)).optString("topic")

    /** The picture that goes BEHIND you in this room.
     *
     *  A different object from the photo that stands in FOR you: `photo`
     *  replaces the person, a background sits under whatever the seat is
     *  showing and leaves them on top of it. Uploading one deliberately does
     *  not change what you are showing — putting scenery up should not turn
     *  your camera off or take your face down. */
    suspend fun uploadRoomBackground(roomId: String, interactorId: String,
                                     filename: String, bytes: ByteArray,
                                     token: String): String =
        withContext(Dispatchers.IO) {
            val q = "?interactor_id=" +
                java.net.URLEncoder.encode(interactorId, "UTF-8") +
                "&filename=" + java.net.URLEncoder.encode(filename, "UTF-8")
            val conn = (java.net.URL("$base/rooms/$roomId/face/background" + q)
                .openConnection() as java.net.HttpURLConnection).apply {
                requestMethod = "POST"
                setRequestProperty("accept-language", L10n.deviceLanguage())
                setRequestProperty("authorization", "Bearer $token")
                doOutput = true
            }
            conn.outputStream.use { it.write(bytes) }
            val text = (if (conn.responseCode < 300) conn.inputStream
                        else conn.errorStream).bufferedReader().readText()
            JSONObject(text).optString("background_url")
        }

    /** Your own picture, if you have put one up. Yours alone to read: a
     *  person's photograph is not a directory anybody with an id may page
     *  through. */
    suspend fun ownPicture(interactorId: String, token: String): String =
        JSONObject(request("/interactors/$interactorId/picture",
                           token = token)).optString("url")

    /** Whether this person's hosted memories feed the shared model, and
     *  how many have gone. */
    suspend fun ownContribution(interactorId: String,
                                token: String): Pair<Boolean, Int> {
        val o = JSONObject(request("/interactors/$interactorId/contribution",
                                   token = token))
        return o.optBoolean("contributes") to o.optInt("contributed_count")
    }

    /** Off, and the past pulled back with it. */
    suspend fun stopOwnContribution(interactorId: String,
                                    token: String): Pair<Int, Boolean> {
        val o = JSONObject(request("/interactors/$interactorId/contribution",
                                   "DELETE", token = token))
        return o.optInt("revoked_count") to o.optBoolean("deleted_at_gateway")
    }

    /** Everything YOU hold, across every profile you have talked to.
     *
     *  A memory is what you said, sealed in your vault on your plan, so a
     *  profile's deletion no longer takes it. Flattened to one line per
     *  moment, with the profile's name — or the fact that it is gone —
     *  standing at the head of its group. */
    suspend fun ownMemories(interactorId: String, token: String,
                            goneLabel: String): List<String> {
        val out = JSONObject(request("/interactors/$interactorId/memories",
                                     token = token))
        val talks = out.optJSONArray("conversations") ?: return emptyList()
        val lines = mutableListOf<String>()
        for (i in 0 until talks.length()) {
            val talk = talks.getJSONObject(i)
            // A deleted profile has no name to show: the name was one of
            // its own words, and erasure took it. The screen supplies the
            // sentence for that, in the reader's language — the shell does
            // not get to invent one, and a dash is an invented one.
            lines += talk.optString("display_name").ifBlank { goneLabel }
            val moments = talk.optJSONArray("memories") ?: continue
            for (j in 0 until moments.length()) {
                lines += moments.getJSONObject(j).optString("line")
            }
        }
        return lines
    }

    /** Put your own picture up — the PERSON's, not a profile's portrait. It
     *  follows you into every room rather than being set again in each one,
     *  and it is never AI-marked: a photograph of your own face is authentic
     *  media, and stamping it would be a false statement in the direction the
     *  mark exists to prevent. */
    suspend fun setOwnPicture(interactorId: String, filename: String,
                              bytes: ByteArray, token: String): String =
        withContext(Dispatchers.IO) {
            val q = "?filename=" +
                java.net.URLEncoder.encode(filename, "UTF-8")
            val conn = (java.net.URL("$base/interactors/$interactorId/picture" + q)
                .openConnection() as java.net.HttpURLConnection).apply {
                requestMethod = "POST"
                setRequestProperty("accept-language", L10n.deviceLanguage())
                setRequestProperty("authorization", "Bearer $token")
                doOutput = true
            }
            conn.outputStream.use { it.write(bytes) }
            val text = (if (conn.responseCode < 300) conn.inputStream
                        else conn.errorStream).bufferedReader().readText()
            JSONObject(text).optString("url")
        }

    /** Back to your initials. Taking your own face down is the one action
     *  where keeping the file would be the surprise. */
    suspend fun clearOwnPicture(interactorId: String, token: String): Boolean {
        request("/interactors/$interactorId/picture", "DELETE",
                token = token)
        return true
    }

    /** The voices this deployment can actually offer, asked of the engine
     *  rather than hardcoded — so the one voice an account made itself is on
     *  the list. Gender is a hint and never a gate; cloned is a label, not a
     *  gate either. */
    suspend fun voiceLibrary(): List<String> {
        val o = JSONObject(request("/voices"))
        val out = mutableListOf<String>()
        val rows = o.optJSONArray("voices") ?: return out
        for (i in 0 until rows.length()) {
            val v = rows.getJSONObject(i)
            out.add(v.optString("id") + " · " + v.optString("name"))
        }
        return out
    }

    /** Hand the room a picture, video or file. Same raw-bytes shape as the
     *  face upload; the share lands as a room message everybody reads, and
     *  never triggers profile turns — "Let them talk" stays the button. */
    suspend fun shareInRoom(roomId: String, interactorId: String,
                            filename: String, bytes: ByteArray,
                            token: String): String =
        withContext(Dispatchers.IO) {
            val q = "?interactor_id=" +
                java.net.URLEncoder.encode(interactorId, "UTF-8") +
                "&filename=" + java.net.URLEncoder.encode(filename, "UTF-8")
            val conn = (java.net.URL("$base/rooms/$roomId/share" + q)
                .openConnection() as java.net.HttpURLConnection).apply {
                requestMethod = "POST"
                setRequestProperty("accept-language", L10n.deviceLanguage())
                setRequestProperty("authorization", "Bearer $token")
                doOutput = true
            }
            conn.outputStream.use { it.write(bytes) }
            val text = (if (conn.responseCode < 300) conn.inputStream
                        else conn.errorStream).bufferedReader().readText()
            JSONObject(text).optJSONObject("shared")
                ?.optJSONObject("media")?.optString("kind") ?: ""
        }

    /** Readable by anyone in the room — a disclosure only its subject can
     *  see is not a disclosure. */
    suspend fun roomMicDisclosure(roomId: String,
                                  token: String): List<String> {
        val o = JSONObject(request("/rooms/$roomId/mic", token = token))
        val out = mutableListOf<String>()
        o.optJSONArray("microphones_lent")?.let { a ->
            for (i in 0 until a.length()) {
                val m = a.getJSONObject(i)
                out.add(m.optString("interactor_id") + " · " +
                    m.optString("device"))
            }
        }
        return out
    }

    suspend fun displayRules(): List<String> {
        val o = JSONObject(request("/displays/vocabulary"))
        val out = mutableListOf<String>()
        o.optJSONArray("never")?.let { a ->
            for (i in 0 until a.length())
                out.add(a.getJSONObject(i).optString("why"))
        }
        return out
    }

    suspend fun display(displayId: String): String {
        val o = JSONObject(request("/displays/$displayId"))
        return o.optString("kind") + " · " +
            (o.optJSONArray("faces")?.toString() ?: "[]")
    }

    suspend fun setDisplayFaces(displayId: String, faces: List<String>,
                                token: String) {
        val arr = org.json.JSONArray()
        faces.forEach { arr.put(it) }
        request("/displays/$displayId/faces", "PUT",
            JSONObject().put("faces", arr), token)
    }

    suspend fun takeDownDisplay(displayId: String, token: String) {
        request("/displays/$displayId", "DELETE", token = token)
    }

    suspend fun membership(accountId: String, token: String): String {
        val o = JSONObject(request("/memberships/$accountId", token = token))
        return o.optString("plan") + " · " + o.optString("status")
    }

    suspend fun joinPlan(accountId: String, plan: String, token: String) {
        request("/memberships/$accountId", "POST",
            JSONObject().put("plan", plan), token)
    }

    /** The account becomes a visitor and keeps its profiles — a lapsed
     *  subscription is not a reason to delete somebody's work. */
    suspend fun cancelMembership(accountId: String, token: String) {
        request("/memberships/$accountId", "DELETE", token = token)
    }

    suspend fun createHandoff(interactorId: String, profileId: String,
                              providerId: String,
                              token: String): Pair<String, String> {
        val o = JSONObject(request("/handoffs", "POST",
            JSONObject().put("interactor_id", interactorId)
                .put("profile_id", profileId)
                .put("provider_id", providerId).put("consent", true), token))
        return o.optString("id") to o.optString("token")
    }

    suspend fun openHandoff(handoffId: String, linkToken: String): String {
        val o = JSONObject(request("/handoffs/$handoffId?token=$linkToken"))
        return o.optString("provider") + " · " + o.optBoolean("sealed")
    }

    suspend fun revokeHandoff(handoffId: String, token: String) {
        request("/handoffs/$handoffId", "DELETE", token = token)
    }

    suspend fun campaign(campaignId: String): String {
        val o = JSONObject(request("/campaigns/$campaignId"))
        return o.optString("title") + " · " + o.optDouble("raised", 0.0) +
            " / " + o.optDouble("goal", 0.0) + " · " + o.optString("status")
    }

    /** No token required — a donor arriving from a beacon scan has no
     *  account, and requiring one gates generosity behind signup. */
    suspend fun donate(campaignId: String, amount: Double, note: String) {
        request("/campaigns/$campaignId/donate", "POST",
            JSONObject().put("amount", amount).put("note", note))
    }

    suspend fun closeCampaign(campaignId: String, token: String) {
        request("/campaigns/$campaignId/close", "POST", token = token)
    }

    // -- the owner's workshop: workflows, delegation, the assistant,
    // tasks under a grant, rated placements and specialists --------------

    suspend fun workflows(id: String, token: String): List<String> {
        val arr = org.json.JSONArray(request("/profiles/$id/workflows",
            token = token))
        return (0 until arr.length()).map {
            val o = arr.getJSONObject(it)
            o.optString("goal") + " \u00b7 " + o.optString("status") +
                " \u00b7 " + o.optString("next_phase", "\u2014")
        }
    }

    suspend fun startWorkflow(id: String, goal: String,
                              token: String): String {
        val o = JSONObject(request("/profiles/$id/workflows", "POST",
            JSONObject().put("goal", goal), token))
        return o.optString("id")
    }

    suspend fun workflow(id: String, workflowId: String,
                         token: String): String {
        val o = JSONObject(request("/profiles/$id/workflows/$workflowId",
            token = token))
        return o.optString("status") + " \u00b7 " +
            o.optString("next_phase", "\u2014")
    }

    suspend fun advanceWorkflow(id: String, workflowId: String,
                                token: String): String {
        val o = JSONObject(request(
            "/profiles/$id/workflows/$workflowId/advance", "POST",
            token = token))
        return o.optString("status") + " \u00b7 " +
            o.optString("next_phase", "\u2014")
    }

    suspend fun resumeWorkflow(id: String, workflowId: String,
                               input: String, token: String): String {
        val o = JSONObject(request(
            "/profiles/$id/workflows/$workflowId/resume", "POST",
            JSONObject().put("input", input), token))
        return o.optString("status")
    }

    suspend fun cancelWorkflow(id: String, workflowId: String,
                               token: String) {
        request("/profiles/$id/workflows/$workflowId/cancel", "POST",
            token = token)
    }

    /** A capability advertisement, readable without a token, so a caller
     *  can decide whether a handoff is possible before attempting one. */
    suspend fun delegationOffer(id: String): String {
        val o = JSONObject(request("/profiles/$id/delegation"))
        return if (o.optBoolean("delegation"))
            o.optJSONArray("phases").let { arr ->
                (0 until (arr?.length() ?: 0))
                    .joinToString(", ") { arr!!.getString(it) }
            }
        else "\u2014"
    }

    suspend fun setDelegation(id: String, phases: List<String>,
                              token: String) {
        request("/profiles/$id/delegation", "PUT",
            JSONObject().put("phases", org.json.JSONArray(phases)), token)
    }

    suspend fun startDelegatedWorkflow(id: String, interactorId: String,
                                       goal: String, token: String): String {
        val o = JSONObject(request("/profiles/$id/delegated-workflows",
            "POST", JSONObject().put("goal", goal)
                .put("interactor_id", interactorId), token))
        return o.optString("id")
    }

    suspend fun delegatedWorkflow(id: String, workflowId: String,
                                  token: String): String {
        val o = JSONObject(request(
            "/profiles/$id/delegated-workflows/$workflowId", token = token))
        return o.optString("status") + " \u00b7 " +
            o.optString("delegated_to")
    }

    suspend fun advanceDelegatedWorkflow(id: String, workflowId: String,
                                         token: String): String {
        val o = JSONObject(request(
            "/profiles/$id/delegated-workflows/$workflowId/advance", "POST",
            token = token))
        return o.optString("status")
    }

    suspend fun resumeDelegatedWorkflow(id: String, workflowId: String,
                                        input: String,
                                        token: String): String {
        val o = JSONObject(request(
            "/profiles/$id/delegated-workflows/$workflowId/resume", "POST",
            JSONObject().put("input", input), token))
        return o.optString("status")
    }

    suspend fun composeNote(id: String, moment: String,
                            token: String): String {
        val o = JSONObject(request("/profiles/$id/assist/compose", "POST",
            JSONObject().put("kind", "note").put("moment", moment), token))
        return o.optString("content")
    }

    suspend fun composedWorks(id: String, token: String): List<String> {
        val arr = org.json.JSONArray(request("/profiles/$id/assist/works",
            token = token))
        return (0 until arr.length()).map {
            val o = arr.getJSONObject(it)
            o.optString("kind") + " \u00b7 " + o.optString("moment")
        }
    }

    suspend fun proofread(id: String, text: String, token: String): String {
        val o = JSONObject(request("/profiles/$id/assist/proofread", "POST",
            JSONObject().put("text", text), token))
        return o.optString("edited",
            o.optJSONArray("suggestions")?.join(" \u00b7 ") ?: "")
    }

    suspend fun triage(id: String, texts: List<String>, keep: Int,
                       criteria: String, token: String): String {
        val items = org.json.JSONArray()
        texts.forEachIndexed { i, t ->
            items.put(JSONObject().put("id", "i$i").put("text", t))
        }
        val o = JSONObject(request("/profiles/$id/assist/triage", "POST",
            JSONObject().put("items", items).put("keep", keep)
                .put("criteria", criteria), token))
        val kept = o.optJSONArray("kept")
        return (0 until (kept?.length() ?: 0)).joinToString(" \u00b7 ") {
            kept!!.getJSONObject(it).optString("reason")
        }
    }

    suspend fun mintTaskGrant(id: String,
                              token: String): Pair<String, String> {
        val o = JSONObject(request("/profiles/$id/grants", "POST",
            JSONObject().put("scope", org.json.JSONArray(listOf("*"))),
            token))
        return o.optString("id") to o.optString("token")
    }

    suspend fun revokeTaskGrant(grantId: String, token: String) {
        request("/grants/$grantId", "DELETE", token = token)
    }

    suspend fun runTask(id: String, topic: String, grantToken: String,
                        token: String): String {
        val o = JSONObject(request("/profiles/$id/tasks", "POST",
            JSONObject().put("topic", topic).put("grant_token", grantToken),
            token))
        return o.optString("reason", o.optString("status"))
    }

    suspend fun tasksRun(id: String, token: String): List<String> {
        val arr = org.json.JSONArray(request("/profiles/$id/tasks",
            token = token))
        return (0 until arr.length()).map {
            val o = arr.getJSONObject(it)
            o.optString("topic") + " \u00b7 " + o.optString("status")
        }
    }

    suspend fun ratedVenues(): List<String> {
        val arr = org.json.JSONArray(request("/venues"))
        return (0 until arr.length()).map {
            arr.getJSONObject(it).optString("key")
        }
    }

    suspend fun placeRated(id: String, venue: String, label: String,
                           token: String): Pair<String, String> {
        val body = JSONObject().put("venue", venue)
        if (label.isNotEmpty()) body.put("label", label)
        val o = JSONObject(request("/profiles/$id/placements", "POST",
            body, token))
        return o.optString("placement_id") to o.optString("scan_url")
    }

    suspend fun placements(id: String, token: String): List<String> {
        val arr = org.json.JSONArray(request("/profiles/$id/placements",
            token = token))
        return (0 until arr.length()).map {
            val o = arr.getJSONObject(it)
            o.optString("label", o.optString("venue_name")) + " \u00b7 " +
                o.optInt("scans")
        }
    }

    suspend fun placementAnalytics(id: String, token: String): String {
        val f = JSONObject(request("/profiles/$id/placements/analytics",
            token = token)).getJSONObject("funnel")
        return f.optInt("resolutions").toString() + " \u2192 " +
            f.optInt("verified_views") + " \u2192 " +
            f.optInt("unique_chatters")
    }

    suspend fun placementCustody(id: String, token: String): String {
        val o = JSONObject(request("/profiles/$id/placements/custody",
            token = token))
        return o.optInt("count").toString() + " \u00b7 " +
            o.optBoolean("chain_intact")
    }

    suspend fun removePlacement(placementId: String, token: String) {
        request("/placements/$placementId", "DELETE", token = token)
    }

    suspend fun specialists(id: String, token: String): List<String> {
        val arr = org.json.JSONArray(request("/profiles/$id/specialists",
            token = token))
        return (0 until arr.length()).map {
            val o = arr.getJSONObject(it)
            o.optString("domain") + " \u00b7 " +
                o.optString("specialist_profile_id")
        }
    }

    suspend fun setSpecialist(id: String, domain: String,
                              specialistId: String, token: String) {
        request("/profiles/$id/specialists", "PUT",
            JSONObject().put("domain", domain)
                .put("specialist_profile_id", specialistId), token)
    }

    // -- the record, the veil and the exit: what the platform holds about
    // a profile, what its anonymity hides, and how it ends ---------------

    suspend fun memories(id: String, token: String): List<String> {
        val arr = org.json.JSONArray(request("/profiles/$id/memories",
            token = token))
        return (0 until arr.length()).map {
            val o = arr.getJSONObject(it)
            o.optString("interactor_name") + " \u00b7 " + o.optInt("turns")
        }
    }

    suspend fun memory(id: String, interactorId: String,
                       token: String): List<String> {
        val arr = org.json.JSONArray(request(
            "/profiles/$id/memory/$interactorId", token = token))
        // Ids ride along so the strike/rewrite doors below have something
        // to be given; a rewritten turn wears its mark.
        return (0 until arr.length()).map {
            val o = arr.getJSONObject(it)
            o.optString("id") + " — " + o.optString("content") +
                (if (o.optBoolean("edited")) " ✎" else "")
        }
    }

    // The distilled long memory of one person — what survived the window.
    suspend fun remembrance(id: String, interactorId: String,
                            token: String): String? {
        val o = org.json.JSONObject(request(
            "/profiles/$id/memory/$interactorId/remembrance", token = token))
        return if (o.isNull("content")) null else o.optString("content")
    }

    // What do you remember about me — answered from the records.
    suspend fun memoryAccount(id: String, interactorId: String,
                              token: String): String {
        val o = org.json.JSONObject(request(
            "/profiles/$id/memory/$interactorId/account", token = token))
        val kept = if (o.isNull("remembers")) "" else o.optString("remembers")
        return kept + " · " + o.optInt("folded_turns") + "+" +
            o.optInt("recent_turns")
    }

    // The pair's sealed shelf — what the vault remembers of this
    // conversation, read back line by line.
    suspend fun recollections(id: String, interactorId: String,
                              token: String): RecollectionShelf {
        val o = org.json.JSONObject(request(
            "/profiles/$id/memory/$interactorId/recollections",
            token = token))
        val arr = o.getJSONArray("memories")
        val out = mutableListOf<RecolledMoment>()
        for (i in 0 until arr.length()) {
            val m = arr.getJSONObject(i)
            out.add(RecolledMoment(
                m.getString("ref"),
                if (m.isNull("line")) null else m.optString("line"),
                if (m.isNull("at")) null else m.optString("at")))
        }
        return RecollectionShelf(out, o.optBoolean("readable"))
    }

    // Take one sealed moment back the whole way: the vector, the seal
    // and the ledger row go together.
    suspend fun forgetRecollection(id: String, interactorId: String,
                                   ref: String, token: String): Boolean {
        val o = org.json.JSONObject(request(
            "/profiles/$id/memory/$interactorId/recollections/$ref",
            "DELETE", token = token))
        return o.optBoolean("forgotten")
    }

    // Forget that one thing; the kept memory re-folds from what remains.
    suspend fun forgetMemory(id: String, interactorId: String, about: String,
                             token: String): String {
        val o = org.json.JSONObject(request(
            "/profiles/$id/memory/$interactorId/forget", "POST",
            JSONObject().put("about", about), token = token))
        // Turns struck, then sealed memories the vault let go of with them.
        return o.optInt("forgotten_turns").toString() + " · " +
            o.optInt("sealed_forgotten")
    }

    suspend fun eraseMemory(id: String, interactorId: String,
                            token: String) {
        request("/profiles/$id/memory/$interactorId", "DELETE",
            token = token)
    }

    // Strike selected turns by id; the kept memory re-folds from what
    // remains — never from what was struck.
    suspend fun strikeTurns(id: String, interactorId: String,
                            messageIds: List<String>,
                            token: String): String {
        val o = JSONObject(request(
            "/profiles/$id/memory/$interactorId/strike", "POST",
            JSONObject().put("message_ids",
                org.json.JSONArray(messageIds)), token = token))
        // Turns struck, then sealed memories the vault let go of with them.
        return o.optInt("struck_turns").toString() + " · " +
            o.optInt("sealed_forgotten")
    }

    // Rewrite one remembered turn. A profile turn loses its synthetic-media
    // credential — it must not vouch for words a person rewrote.
    suspend fun editTurn(id: String, interactorId: String, messageId: String,
                         content: String, token: String): String {
        val o = JSONObject(request(
            "/profiles/$id/memory/$interactorId/turns/$messageId", "PUT",
            JSONObject().put("content", content), token = token))
        return o.optJSONObject("turn")?.optString("content") ?: ""
    }

    suspend fun thread(id: String, interactorId: String,
                       token: String): String {
        val o = JSONObject(request("/profiles/$id/thread/$interactorId",
            token = token))
        return (o.optJSONArray("messages")?.length() ?: 0).toString()
    }

    suspend fun engagement(id: String, interactorId: String,
                           token: String): String {
        val o = JSONObject(request(
            "/profiles/$id/engagement/$interactorId", token = token))
        return o.optInt("sessions").toString()
    }

    /** The pair may read it — the person it is about, and the profile's
     *  owner — and nobody else: it is that person's medical information. */
    suspend fun clinicalNotes(id: String, interactorId: String,
                              token: String): List<String> {
        val arr = org.json.JSONArray(request(
            "/profiles/$id/clinical-notes/$interactorId", token = token))
        return (0 until arr.length()).map {
            arr.getJSONObject(it).optString("note")
        }
    }

    suspend fun embedding(id: String, interactorId: String,
                          token: String) {
        request("/profiles/$id/embedding/$interactorId", token = token)
    }

    suspend fun sources(id: String, token: String): List<String> {
        val arr = org.json.JSONArray(request("/profiles/$id/sources",
            token = token))
        return (0 until arr.length()).map {
            val o = arr.getJSONObject(it)
            o.optString("kind") + " \u00b7 " + o.optString("title")
        }
    }

    suspend fun addSource(id: String, kind: String, title: String,
                          content: String, token: String) {
        request("/profiles/$id/sources", "POST",
            JSONObject().put("kind", kind).put("title", title)
                .put("content", content), token)
    }

    /** Public on purpose: how many relationships this profile holds, and
     *  which model actually answers for it. */
    suspend fun transparency(id: String): String {
        val o = JSONObject(request("/profiles/$id/transparency"))
        return o.optInt("active_relationships").toString() + " \u00b7 " +
            o.optString("model_effective")
    }

    // A one-time, minutes-long handoff of the export to another device:
    // the QR carries the ticket, never the owner token.
    suspend fun exportTicket(id: String, token: String): Pair<String, String> {
        val o = JSONObject(request("/profiles/$id/export/ticket", "POST",
            token = token))
        return o.optString("ticket") to o.optString("note")
    }

    // The redeeming side — tokenless, the single-use ticket is the whole
    // authority.
    suspend fun exportHandoff(id: String, ticket: String): String {
        val o = JSONObject(request("/profiles/$id/export/handoff/$ticket"))
        return o.keys().asSequence().joinToString(", ")
    }

    // Where the scannable code lives; reading it does not consume the
    // ticket. Built through URL() so the door audit reads the address the
    // same way it reads every direct-connection fetch.
    fun exportHandoffQrUrl(id: String, ticket: String): String =
        URL("$base/profiles/$id/export/handoff/$ticket/qr.svg").toString()

    suspend fun exportProfile(id: String, token: String): String {
        val o = JSONObject(request("/profiles/$id/export", token = token))
        return (o.optJSONArray("messages")?.length() ?: 0).toString() +
            " \u00b7 " + (o.optJSONArray("posts")?.length() ?: 0) +
            " \u00b7 " + (o.optJSONArray("sources")?.length() ?: 0)
    }

    suspend fun profileStats(id: String, token: String): String {
        val o = JSONObject(request("/profiles/$id/stats", token = token))
        return o.optInt("sessions").toString() + " \u00b7 " +
            o.optInt("memory_entries") + " \u00b7 " +
            o.optInt("interactors") + " \u00b7 " + o.optInt("sources")
    }

    suspend fun feed(id: String): String {
        val o = JSONObject(request("/profiles/$id/feed"))
        val ranked = o.optJSONArray("ranked_on")
        return (o.optJSONArray("posts")?.length() ?: 0).toString() +
            " \u00b7 " + (ranked?.join(", ") ?: "")
    }

    suspend fun anonymity(id: String, token: String): String {
        val o = JSONObject(request("/profiles/$id/anonymity",
            token = token))
        // What it does NOT hide renders first — the generous reading of
        // "anonymous" is the dangerous one.
        return o.optJSONArray("not_withheld")?.join(" \u00b7 ") ?: ""
    }

    suspend fun setAnonymity(id: String, anonymous: Boolean,
                             token: String) {
        request("/profiles/$id/anonymity", "PUT",
            JSONObject().put("anonymous", anonymous), token)
    }

    /** Public: a claim a stranger can see is a claim a stranger should be
     *  able to check. */
    suspend fun verification(id: String): String {
        val o = JSONObject(request("/profiles/$id/verification"))
        return o.optString("level", "\u2014") + " \u00b7 " +
            o.optString("attestor", "\u2014")
    }

    suspend fun claimVerification(id: String, level: String,
                                  attestor: String, token: String) {
        request("/profiles/$id/verification", "POST",
            JSONObject().put("level", level).put("attestor", attestor)
                .put("method", "document"), token)
    }

    suspend fun moveBadgeHere(id: String, token: String) {
        request("/profiles/$id/verification/move", "POST", token = token)
    }

    suspend fun verifiable(id: String, token: String): String {
        val o = JSONObject(request("/profiles/$id/verifiable",
            token = token))
        return o.optString("reason", o.optBoolean("can_verify").toString())
    }

    suspend fun editProfile(id: String, displayName: String,
                            persona: String, token: String) {
        val body = JSONObject()
        if (displayName.isNotEmpty()) body.put("display_name", displayName)
        if (persona.isNotEmpty()) body.put("persona", persona)
        request("/profiles/$id", "PATCH", body, token)
    }

    suspend fun sunset(id: String, token: String): String {
        val o = JSONObject(request("/profiles/$id/sunset", "POST",
            token = token))
        return o.optInt("farewells").toString()
    }

    /** Public memorial for a departed profile — never persona internals. */
    suspend fun memorial(id: String): String {
        val o = JSONObject(request("/profiles/$id/memorial"))
        return o.optString("display_name") + " \u00b7 " +
            o.optInt("relationships_touched")
    }

    suspend fun siblings(id: String, token: String): String {
        val o = JSONObject(request("/profiles/$id/siblings",
            token = token))
        val arr = o.optJSONArray("profiles")
        return (0 until (arr?.length() ?: 0)).joinToString(" \u00b7 ") {
            arr!!.getJSONObject(it).optString("display_name")
        }
    }

    suspend fun succeed(id: String, verificationRef: String,
                        token: String): String {
        val o = JSONObject(request("/profiles/$id/succeed", "POST",
            JSONObject().put("verification_ref", verificationRef), token))
        return o.optBoolean("succeeded").toString()
    }

    suspend fun deleteProfile(id: String, token: String) {
        request("/profiles/$id", "DELETE", token = token)
    }

    // -- the face it shows the world: portrait, emblem, page, front,
    // surfaces, blend, bodies, dials and the wrist -----------------------

    /** Public: the portrait as it must be displayed — asset, AI badge,
     *  and whose likeness it is. */
    suspend fun avatar(id: String): String {
        val o = JSONObject(request("/profiles/$id/avatar"))
        return (if (o.optBoolean("asset_marked")) "AI" else "\u2014") +
            " \u00b7 " + (o.optJSONObject("likeness")
                ?.optString("note") ?: "\u2014")
    }


    // One row of the skin shelf: the system, its name, and the provider's own
    // export route. `how` is the useful half and no shell was carrying it.
    data class MarketSource(val key: String, val name: String, val how: String)

    suspend fun setAvatar(id: String, asset: String, token: String) {
        request("/profiles/$id/avatar", "PUT",
            JSONObject().put("asset", asset), token)
    }

    /**
     * The eight systems a face can be brought from, and how to export from
     * each in that provider's own words.
     *
     * This returned an `Int` — the length of the array it had just decoded —
     * so the shell could say "8" and had no way to name any of them. The
     * caller then imported everything as `other`, which is the provenance
     * this route exists to preserve, discarded at the last step.
     */
    suspend fun avatarMarket(): List<MarketSource> {
        val o = JSONObject(request("/avatars/market"))
        val arr = o.optJSONArray("sources") ?: JSONArray()
        return (0 until arr.length()).map {
            val s = arr.getJSONObject(it)
            MarketSource(s.getString("key"), s.optString("name", ""),
                s.optString("how", ""))
        }
    }

    suspend fun importAvatar(id: String, source: String, asset: String, token: String) {
        request("/profiles/$id/avatar/import", "POST",
            JSONObject().put("source", source).put("asset", asset), token)
    }

    suspend fun avatarBriefs(): String {
        val o = JSONObject(request("/avatars/briefs"))
        return (o.optJSONArray("briefs")?.length() ?: 0).toString()
    }

    suspend fun avatarBrief(handle: String): String {
        val o = JSONObject(request("/avatars/briefs/$handle"))
        return o.optString("brief")
    }

    suspend fun identityEmblems(): String {
        val arr = JSONObject(request("/identity/emblems"))
            .optJSONArray("emblems")
        return (0 until (arr?.length() ?: 0)).joinToString(" \u00b7 ") {
            arr!!.getJSONObject(it).optString("emblem")
        }
    }

    suspend fun identityVocabulary(): String {
        val o = JSONObject(request("/identity/vocabulary"))
        return o.optJSONArray("withheld_when_anonymous")
            ?.join(" \u00b7 ") ?: ""
    }

    suspend fun setEmblem(id: String, emblem: String, token: String) {
        request("/profiles/$id/emblem", "PUT",
            JSONObject().put("emblem", emblem), token)
    }

    /** Public, and not the same read as /verification: on an anonymous
     *  profile the attestor is withheld. */
    suspend fun badge(id: String): String {
        val o = JSONObject(request("/profiles/$id/badge"))
        return o.optString("level", "\u2014") + " \u00b7 " +
            o.optString("attestor", "\u2014")
    }

    suspend fun pageThemes(): String {
        val arr = JSONObject(request("/pages/themes"))
            .optJSONArray("themes")
        return (0 until (arr?.length() ?: 0)).joinToString(" \u00b7 ") {
            arr!!.getJSONObject(it).optString("id")
        }
    }

    suspend fun page(id: String): String {
        val o = JSONObject(request("/profiles/$id/page"))
        return (o.optJSONObject("theme")?.optString("label") ?: "\u2014") +
            " \u00b7 " + o.optString("tagline", "\u2014")
    }

    /**
     * The same route, read whole.
     *
     * `page` above flattens it to "theme · tagline" for a one-line card, and
     * that was every field this shell had ever read. The accent they picked,
     * the eight faces they arranged, their links, what they offer and
     * whether they decorated the page at all were all on the wire and shown
     * nowhere — which is why there was no screen that could open a friend.
     *
     *     asked     does the shell call the page route
     *     mattered  does it read what the page route answers
     */
    suspend fun pageCard(id: String): PageCardFull {
        val o = JSONObject(request("/profiles/$id/page"))
        val top = mutableListOf<PageFriendRow>()
        o.optJSONArray("top_friends")?.let { a ->
            for (i in 0 until a.length()) {
                val f = a.getJSONObject(i)
                top.add(PageFriendRow(f.getString("profile_id"),
                    if (f.isNull("display_name")) null
                    else f.optString("display_name")))
            }
        }
        val links = mutableListOf<PageLink>()
        o.optJSONArray("links")?.let { a ->
            for (i in 0 until a.length()) {
                val l = a.getJSONObject(i)
                links.add(PageLink(l.optString("label"), l.optString("url")))
            }
        }
        val offers = mutableListOf<PageOffer>()
        o.optJSONArray("offers")?.let { a ->
            for (i in 0 until a.length()) {
                val f = a.getJSONObject(i)
                offers.add(PageOffer(f.optString("title"),
                    if (f.isNull("blurb")) null else f.optString("blurb")))
            }
        }
        return PageCardFull(
            if (o.isNull("tagline")) null else o.optString("tagline"),
            if (o.isNull("about")) null else o.optString("about"),
            if (o.isNull("accent")) null else o.optString("accent"),
            top, links, offers,
            if (o.isNull("html")) null else o.optString("html"),
            o.optBoolean("customised", false))
    }

    /**
     * The uploads as rows rather than as sentences. `profileMedia` above
     * formats each one for a single strip; a screen that offers Photos and
     * Videos as two doors has to be able to tell them apart.
     */
    suspend fun profileMediaRows(id: String): List<MediaRow> {
        val rows = JSONObject(request("/profiles/$id/media"))
            .optJSONArray("media") ?: return emptyList()
        return (0 until rows.length()).map { i ->
            val m = rows.getJSONObject(i)
            MediaRow(m.optString("kind", ""), m.optString("alt"),
                     m.optString("name"), m.optString("id"))
        }
    }

    suspend fun editPage(id: String, theme: String, tagline: String,
                         about: String, token: String) {
        val body = JSONObject()
        if (theme.isNotEmpty()) body.put("theme", theme)
        if (tagline.isNotEmpty()) body.put("tagline", tagline)
        if (about.isNotEmpty()) body.put("about", about)
        request("/profiles/$id/page", "PUT", body, token)
    }

    /** Everything a visitor's first screen needs, in one call. */
    suspend fun frontPage(id: String): String {
        val o = JSONObject(request("/profiles/$id/front"))
        return o.optString("display_name", "\u2014") + " \u00b7 " +
            o.optString("headline", "\u2014")
    }

    suspend fun surfaces(id: String): String {
        val o = JSONObject(request("/profiles/$id/surfaces"))
        return o.optJSONArray("surfaces")?.join(" \u00b7 ") ?: ""
    }

    suspend fun setSurfaces(id: String, surfaces: List<String>,
                            token: String) {
        request("/profiles/$id/surfaces", "PUT",
            JSONObject().put("surfaces", org.json.JSONArray(surfaces)),
            token)
    }

    /** Public, the same open stance as /transparency: the blend is the
     *  profile's provenance. */
    suspend fun composition(id: String): String {
        val arr = JSONObject(request("/profiles/$id/composition"))
            .optJSONArray("sources")
        return (0 until (arr?.length() ?: 0)).joinToString(" \u00b7 ") {
            arr!!.getJSONObject(it).optString("name")
        }
    }

    suspend fun embodiments(id: String, token: String): List<String> {
        val arr = org.json.JSONArray(request("/profiles/$id/embodiments",
            token = token))
        return (0 until arr.length()).map {
            val o = arr.getJSONObject(it)
            o.optString("name") + " \u00b7 " + o.optString("kind")
        }
    }

    suspend fun addEmbodiment(id: String, name: String, kind: String,
                              token: String) {
        request("/profiles/$id/embodiments", "POST",
            JSONObject().put("name", name).put("kind", kind)
                .put("has_llm", false), token)
    }

    /** Public: anyone meeting the profile through any form can verify it
     *  is the same personality. */
    suspend fun embodimentConsistency(id: String): String {
        val arr = JSONObject(request("/profiles/$id/embodiment-consistency"))
            .optJSONArray("embodiments")
        return (0 until (arr?.length() ?: 0)).joinToString(" \u00b7 ") {
            arr!!.getJSONObject(it).optString("name")
        }
    }

    suspend fun profileDisplays(id: String, token: String): String {
        val arr = JSONObject(request("/profiles/$id/displays",
            token = token)).optJSONArray("displays")
        return (0 until (arr?.length() ?: 0)).joinToString(" \u00b7 ") {
            arr!!.getJSONObject(it).optString("label")
        }
    }

    suspend fun addProfileDisplay(id: String, kind: String, label: String,
                                  token: String) {
        request("/profiles/$id/displays", "POST",
            JSONObject().put("kind", kind).put("label", label), token)
    }

    suspend fun steering(id: String, token: String): String {
        val vals = JSONObject(request("/profiles/$id/steering",
            token = token)).optJSONObject("values")
        return vals?.keys()?.asSequence()?.sorted()
            ?.joinToString(" \u00b7 ") { "$it ${vals.optInt(it)}" } ?: ""
    }

    /** Dials are 0\u2013100 integers. Intimacy can never be raised on a
     *  non-rated persona. */
    suspend fun setSteering(id: String, values: Map<String, Int>,
                            token: String) {
        val v = JSONObject()
        values.forEach { (k, n) -> v.put(k, n) }
        request("/profiles/$id/steering", "PUT",
            JSONObject().put("values", v), token)
    }

    suspend fun watchFace(id: String, token: String): String {
        val o = JSONObject(request("/profiles/$id/watch", token = token))
        val sum = o.getJSONObject("summary")
        return o.getJSONObject("profile").optString("light") +
            " \u00b7 " + sum.optInt("working") + " \u00b7 " +
            sum.optInt("needing_assistance") + " \u00b7 " +
            sum.optInt("stopped")
    }

    suspend fun watchAct(id: String, target: String, targetId: String,
                         action: String, input: String,
                         token: String): String {
        val body = JSONObject().put("target", target).put("id", targetId)
            .put("action", action)
        if (input.isNotEmpty()) body.put("input", input)
        val o = JSONObject(request("/profiles/$id/watch/act", "POST",
            body, token))
        return o.optString("status")
    }

    // ---- The keys: the account itself ----

    suspend fun signup(email: String, password: String,
                       name: String): String {
        val body = JSONObject().put("email", email).put("password", password)
        if (name.isNotEmpty()) body.put("display_name", name)
        return JSONObject(request("/signup", "POST", body))
            .optString("code_delivery")
    }

    /** Unknown address and wrong password get the same answer; an
     *  unverified address cannot sign in at all. */
    /**
     * The account *and* its token.
     *
     * This returned only a display name until the roster below existed, and
     * threw the token away — which was fine while nothing could be done with
     * it, and is exactly what left somebody able to sign in and reach none of
     * their own profiles.
     */
    data class AccountSession(val accountId: String, val accountToken: String,
                              val name: String)

    suspend fun signin(email: String, password: String): AccountSession {
        val o = JSONObject(request("/signin", "POST",
            JSONObject().put("email", email).put("password", password)))
        return AccountSession(
            o.optString("account_id"), o.optString("account_token"),
            o.optString("display_name", o.optString("email")))
    }

    /** One row of the roster reached through the account token. */
    data class HeldProfile(val profileId: String, val kind: String,
                           val shownAs: String)

    /**
     * What this account holds. `siblings` above answers the same question and
     * asks for an owner token first — the thing a reinstalled phone no longer
     * has, because it is minted once in the create response.
     *
     * Carries no credential. Opening one is [mintOwnerToken].
     */
    suspend fun heldProfiles(accountId: String,
                             token: String): List<HeldProfile> {
        val arr = JSONObject(request("/accounts/$accountId/profiles",
            token = token)).optJSONArray("profiles")
        return (0 until (arr?.length() ?: 0)).map {
            val o = arr!!.getJSONObject(it)
            HeldProfile(o.optString("profile_id"), o.optString("kind"),
                // An anonymous profile is anonymous on its owner's own
                // screen too, so the server sends both and this picks.
                o.optString("shown_as", o.optString("display_name")))
        }
    }

    /**
     * A fresh owner capability for a profile this account holds, shown once.
     * Additive — the tokens already on other devices keep working.
     */
    suspend fun mintOwnerToken(accountId: String, profileId: String,
                               token: String): Pair<String, String> {
        val o = JSONObject(request(
            "/accounts/$accountId/profiles/$profileId/owner-token",
            "POST", JSONObject(), token))
        return Pair(o.optString("profile_id"), o.optString("owner_token"))
    }

    suspend fun verifyEmail(email: String, code: String): String {
        return JSONObject(request("/verify-email", "POST",
            JSONObject().put("email", email).put("code", code)))
            .optString("email")
    }

    /** Not an address oracle: same answer either way. */
    suspend fun resendCode(email: String): String {
        return JSONObject(request("/verify-email/resend", "POST",
            JSONObject().put("email", email))).optString("code_delivery")
    }

    suspend fun requestPasswordReset(email: String): String {
        return JSONObject(request("/password/reset/request", "POST",
            JSONObject().put("email", email))).optString("code_delivery")
    }

    /** Every existing account session dies with the old password. */
    suspend fun resetPassword(email: String, code: String,
                              newPassword: String): Boolean {
        return JSONObject(request("/password/reset", "POST",
            JSONObject().put("email", email).put("code", code)
                .put("new_password", newPassword))).optBoolean("reset")
    }

    suspend fun oauthProviders(): List<String> {
        val arr = JSONObject(request("/auth/oauth/providers"))
            .getJSONArray("providers")
        return (0 until arr.length()).map {
            arr.getJSONObject(it).getString("provider")
        }
    }

    suspend fun oauthStart(provider: String): Pair<String, String> {
        val o = JSONObject(request("/auth/oauth/$provider/start", "POST",
            JSONObject()))
        return o.optString("state") to o.optString("url")
    }

    /** One-time pickup; the first successful claim spends the state. */
    suspend fun oauthClaim(state: String): String {
        val o = JSONObject(request("/auth/oauth/claim?state=" +
            java.net.URLEncoder.encode(state, "UTF-8")))
        return if (o.optBoolean("ready")) o.optString("email", "\u2713")
               else "\u2026"
    }

    // ---- The till ----

    /** Public: the terms are readable before any sign-in. */
    suspend fun plans(): String {
        val arr = JSONObject(request("/plans")).getJSONArray("plans")
        return (0 until arr.length()).joinToString(" \u00b7 ") {
            arr.getJSONObject(it).getString("plan")
        }
    }

    suspend fun mySubscriptions(token: String): Int {
        return JSONObject(request("/subscriptions", token = token))
            .getJSONArray("subscriptions").length()
    }

    /** Explicit on purpose: nothing bills on a timer. */
    suspend fun renewSubscription(subId: String, beneficiary: String,
                                  token: String): Int {
        return JSONObject(request("/subscriptions/$subId/renew", "POST",
            JSONObject().put("beneficiary", beneficiary), token))
            .optInt("periods")
    }

    suspend fun myOrders(token: String): Int {
        return JSONObject(request("/orders", token = token))
            .getJSONArray("orders").length()
    }

    /** Public: a donor gives to the names on this list, not the platform. */
    suspend fun proceedsOf(id: String): String {
        val arr = JSONObject(request("/profiles/$id/proceeds"))
            .getJSONArray("proceeds_to")
        return (0 until arr.length()).joinToString(" \u00b7 ") {
            arr.getJSONObject(it).getString("name")
        }
    }

    suspend fun setProceeds(id: String, designee: String, token: String) {
        val d = JSONObject().put("name", designee).put("kind", "loved_one")
            .put("share", 100)
        request("/profiles/$id/proceeds", "PUT",
            JSONObject().put("designees", org.json.JSONArray().put(d)), token)
    }

    suspend fun campaignsOf(id: String): Int {
        return org.json.JSONArray(request("/profiles/$id/campaigns")).length()
    }

    suspend fun addCampaign(id: String, title: String, goal: Double,
                            token: String): String {
        return JSONObject(request("/profiles/$id/campaigns", "POST",
            JSONObject().put("title", title).put("goal", goal), token))
            .optString("title")
    }

    // ---- The lifeline ----

    suspend fun cloudStatus(): String {
        val o = JSONObject(request("/cloud/status"))
        return (if (o.optBoolean("cloud")) "\u2601" else "\u2014") +
            " \u00b7 " + o.optString("fallback")
    }

    suspend fun offlineStatus(): String {
        return JSONObject(request("/offline/status")).optString("provider")
    }

    /** The legend is built from the mapping the code has. */
    suspend fun agentLights(): String {
        val arr = JSONObject(request("/agent/lights")).getJSONArray("order")
        return (0 until arr.length()).joinToString(" \u00b7 ") {
            arr.getString(it)
        }
    }

    suspend fun helpTopics(): Int {
        return JSONObject(request("/help/topics")).getJSONArray("topics")
            .length()
    }

    /** Public on purpose, and it writes nothing. */
    suspend fun askHelp(question: String): String {
        return JSONObject(request("/help", "POST",
            JSONObject().put("question", question))).optString("answer")
    }

    suspend fun localProviders(): Int {
        return org.json.JSONArray(request("/providers")).length()
    }

    suspend fun addLocalProvider(name: String, area: String): String {
        return JSONObject(request("/providers", "POST",
            JSONObject().put("name", name).put("area", area)
                .put("business", true))).optString("name")
    }

    // ---- The sticker on the street ----

    /** The overlay's read: never the face without the disclosure. */
    suspend fun beaconOverlayCard(id: String): String {
        val o = JSONObject(request("/b/$id/card"))
        return if (o.optBoolean("age_wall")) o.optString("note", "18+")
               else o.optString("display_name") + " \u00b7 " +
                   o.optString("watermark")
    }

    fun beaconScanUrl(id: String): String =
        java.net.URL("$base/b/$id").toString()

    fun beaconQrUrl(id: String): String =
        java.net.URL("$base/beacons/$id/qr.svg").toString()

    suspend fun deskScanCard(id: String): String {
        val o = JSONObject(request("/d/$id/card"))
        return o.optString("display_name", o.optString("desk_id"))
    }

    fun deskScanUrl(id: String): String =
        java.net.URL("$base/d/$id").toString()

    suspend fun socialBeacon(cid: String): String {
        val o = JSONObject(request("/social/$cid/beacon"))
        return o.optString("platform") + " \u00b7 " + o.optString("handle")
    }

    fun socialQrUrl(cid: String): String =
        java.net.URL("$base/social/$cid/qr.svg").toString()

    /** Same Wi-Fi, no app store. */
    suspend fun pairing(): String {
        return JSONObject(request("/pair")).optString("console_url")
    }

    fun pairQrUrl(): String = java.net.URL("$base/pair/qr.svg").toString()

    // ---- The queue ----

    suspend fun moderationQueue(id: String, token: String): Int {
        return org.json.JSONArray(
            request("/profiles/$id/moderation/queue", token = token)).length()
    }

    suspend fun approveMessage(messageId: String, token: String): String {
        return JSONObject(request("/moderation/$messageId/approve", "POST",
            JSONObject(), token)).optString("status")
    }

    suspend fun rejectMessage(messageId: String, token: String): String {
        return JSONObject(request("/moderation/$messageId/reject", "POST",
            JSONObject(), token)).optString("status")
    }

    /** Moderated as a fresh message, and it carries forward. */
    suspend fun editMessage(id: String, messageId: String,
                            interactorId: String, content: String,
                            token: String): String {
        return JSONObject(request("/profiles/$id/messages/$messageId",
            "PATCH", JSONObject().put("interactor_id", interactorId)
                .put("content", content), token)).optString("status")
    }

    /** The row survives for the trail; the text stops being shown. */
    suspend fun retractMessage(id: String, messageId: String,
                               interactorId: String, token: String): String {
        return JSONObject(request("/profiles/$id/messages/$messageId",
            "DELETE", JSONObject().put("interactor_id", interactorId),
            token)).optString("status")
    }

    // ---- The reviews ----

    suspend fun reviewsOf(id: String): String {
        val o = JSONObject(request("/profiles/$id/reviews"))
        val n = o.getJSONArray("reviews").length()
        val avg = o.optJSONObject("rating")?.optDouble("average") ?: 0.0
        return "$n \u00b7 $avg"
    }

    /** One per interactor, edited rather than stacked. */
    suspend fun leaveReview(id: String, interactorId: String, rating: Int,
                            text: String, token: String): Int {
        val body = JSONObject().put("interactor_id", interactorId)
            .put("rating", rating)
        if (text.isNotEmpty()) body.put("body", text)
        return JSONObject(request("/profiles/$id/reviews", "POST", body,
            token)).optInt("rating")
    }

    // ---- The stamp ----

    suspend fun watermarkCredential(id: String): String {
        val o = JSONObject(request("/watermarks/$id"))
        return o.optString("profile_id") + " \u00b7 " + o.optString("kind")
    }

    suspend fun verifyWatermark(id: String, content: String): String {
        val body = JSONObject().put("watermark_id", id)
        if (content.isNotEmpty()) body.put("content", content)
        val o = JSONObject(request("/watermarks/verify", "POST", body))
        return (if (o.optBoolean("valid")) "\u2713" else "\u2717") +
            " \u00b7 " + o.optString("content_match", "\u2014")
    }

    // ---- The media ----

    suspend fun mediaLimits(): String {
        val o = JSONObject(request("/media/limits"))
        // One limit per kind, not one limit: video gets sixty megabytes
        // where an image gets eight.
        return listOf("image", "video", "file").joinToString(" \u00b7 ") {
            "$it ${(o.optJSONObject(it)?.optInt("max_bytes") ?: 0) / 1048576}MB"
        }
    }

    /**
     * What came through the upload door, newest first. The upload has
     * been here since 0.42.x with nothing that lists it — media was
     * findable only through the wall post it happened to ride on, so one
     * attached to nothing was invisible from the first second.
     *
     *     asked     can somebody put a photograph here
     *     mattered  can anybody find it afterwards
     *
     * The alt text leads each row rather than trailing it: this list is
     * read aloud to people who cannot see any of it, and a filename tells
     * them nothing.
     */
    suspend fun profileMedia(id: String): List<String> {
        // No `?kind=` here on purpose: this strip shows everything the
        // profile has put up, and the route's filter exists for a screen
        // that offers Photos and Videos as two doors.
        val rows = JSONObject(request("/profiles/$id/media"))
            .optJSONArray("media") ?: return emptyList()
        return (0 until rows.length()).map { i ->
            val m = rows.getJSONObject(i)
            val said = m.optString("alt").ifEmpty {
                m.optString("name").ifEmpty { m.optString("id", "\u2014") } }
            "${m.optString("kind", "\u2014")} \u00b7 $said"
        }
    }

    /** Raw bytes in the body; the kind is read from the bytes. */
    suspend fun uploadMedia(id: String, filename: String, bytes: ByteArray,
                            token: String): String =
        withContext(Dispatchers.IO) {
            val q = if (filename.isEmpty()) ""
                    else "?filename=" +
                        java.net.URLEncoder.encode(filename, "UTF-8")
            val conn = (java.net.URL("$base/profiles/$id/media" + q)
                .openConnection() as java.net.HttpURLConnection).apply {
                    // The second connection in this file, and the one the
                    // shared helper's accept-language line never reached.
                    setRequestProperty("accept-language", L10n.deviceLanguage())
                    llmKey.takeIf { it.isNotEmpty() }?.let {
                        setRequestProperty("x-llm-api-key", it) }
                requestMethod = "POST"
                setRequestProperty("authorization", "Bearer $token")
                    signupKey.takeIf { it.isNotEmpty() }?.let {
                        setRequestProperty("x-signup-key", it) }
                doOutput = true
            }
            conn.outputStream.use { it.write(bytes) }
            val text = (if (conn.responseCode < 300) conn.inputStream
                        else conn.errorStream).bufferedReader().readText()
            JSONObject(text).optString("kind", JSONObject(text)
                .optString("id"))
        }

    // ---- The briefcase: what you hand a profile, read once and kept ----

    /**
     * Scoped to the pair, not to the profile: `interactorId` is who the
     * material belongs to, and the next visitor inherits none of it.
     */
    suspend fun briefcase(profileId: String,
                          interactorId: String): BriefcaseBoard {
        val who = java.net.URLEncoder.encode(interactorId, "UTF-8")
        val o = JSONObject(
            request("/profiles/$profileId/briefcase?interactor_id=$who"))
        val rows = o.optJSONArray("items") ?: JSONArray()
        return BriefcaseBoard(
            (0 until rows.length()).map { briefcaseRow(rows.getJSONObject(it)) },
            o.optInt("max_items", 0), o.optBoolean("offline", false))
    }

    /**
     * The text that was actually extracted, for somebody who wants to check
     * what the profile took from their file. Never what the prompt carries.
     */
    suspend fun briefcaseItem(profileId: String, interactorId: String,
                              itemId: String): BriefcaseRow {
        val who = java.net.URLEncoder.encode(interactorId, "UTF-8")
        return briefcaseRow(JSONObject(request(
            "/profiles/$profileId/briefcase/$itemId?interactor_id=$who")))
    }

    suspend fun importLink(profileId: String, interactorId: String,
                           url: String, note: String): BriefcaseRow {
        val body = JSONObject()
            .put("interactor_id", interactorId).put("url", url)
            .put("note", note)
        return briefcaseRow(JSONObject(
            request("/profiles/$profileId/briefcase/link", "POST", body)))
    }

    /**
     * Raw bytes, like `uploadMedia` above and for the same reason: the
     * backend reads the kind from the bytes, and the filename is a display
     * hint that only a whitelisted extension survives.
     */
    suspend fun importFile(profileId: String, interactorId: String,
                           filename: String, note: String,
                           bytes: ByteArray): BriefcaseRow =
        withContext(Dispatchers.IO) {
            fun enc(s: String) = java.net.URLEncoder.encode(s, "UTF-8")
            // The `?` is in the literal, not appended after it: the route
            // audit truncates a path at its first `?`, so a trailing `$q`
            // left the path reading `/briefcase/filex` — a route that does
            // not exist, and a door that read as missing.
            val q = enc(interactorId) + "&filename=" + enc(filename) +
                "&note=" + enc(note)
            val conn = (java.net.URL(
                "$base/profiles/$profileId/briefcase/file?interactor_id=$q")
                .openConnection() as java.net.HttpURLConnection).apply {
                // First in the block, not last: the route audit reads the
                // verb within a window below the URL, and three header lines
                // ahead of it pushed `requestMethod` out of range. Absent a
                // verb the audit assumes GET — HttpURLConnection's own
                // default — so this registered as a GET of a POST-only route
                // and the door read as missing on this shell alone.
                requestMethod = "POST"
                doOutput = true
                setRequestProperty("accept-language", L10n.deviceLanguage())
                llmKey.takeIf { it.isNotEmpty() }?.let {
                    setRequestProperty("x-llm-api-key", it) }
                signupKey.takeIf { it.isNotEmpty() }?.let {
                    setRequestProperty("x-signup-key", it) }
            }
            conn.outputStream.use { it.write(bytes) }
            val code = conn.responseCode
            val text = (if (code < 300) conn.inputStream else conn.errorStream)
                .bufferedReader().readText()
            if (code >= 300) {
                Problems.record("POST", "/profiles/{id}/briefcase/file", code)
                // `message` first, `detail` only when it is a string: a 422's
                // `detail` is pydantic's list of rows, and `optString`
                // coerces a JSONArray through toString(), so reading it
                // first hands the person raw JSON. Same order as the shared
                // helper, for the same reason.
                val said = runCatching {
                    val body = JSONObject(text)
                    body.optString("message").ifBlank {
                        if (body.opt("detail") is String)
                            body.optString("detail") else ""
                    }
                }.getOrNull()
                throw ApiException(
                    if (said.isNullOrBlank()) "HTTP $code" else said)
            }
            briefcaseRow(JSONObject(text))
        }

    suspend fun forgetImport(profileId: String, interactorId: String,
                             itemId: String) {
        val who = java.net.URLEncoder.encode(interactorId, "UTF-8")
        request("/profiles/$profileId/briefcase/$itemId?interactor_id=$who",
                "DELETE")
    }

    private fun briefcaseRow(o: JSONObject) = BriefcaseRow(
        o.optString("id"), o.optString("kind"), o.optString("title"),
        if (o.isNull("note")) null else o.optString("note"),
        if (o.isNull("source")) null else o.optString("source"),
        o.optBoolean("read", false), o.optString("digest"),
        o.optInt("chars", 0), o.optInt("digest_chars", 0),
        if (o.isNull("text")) null else o.optString("text"))

    suspend fun videoPlatforms(): String {
        val arr = JSONObject(request("/videos/platforms"))
            .optJSONArray("platforms") ?: org.json.JSONArray()
        return (0 until arr.length()).joinToString(" \u00b7 ") {
            arr.getString(it)
        }
    }

    // ---- The wearables ----

    /** A paired device is a screen and a set of buttons. */
    suspend fun wearables(id: String, token: String): String {
        val o = JSONObject(request("/profiles/$id/wearables", token = token))
        val worn = o.optJSONObject("kinds_worn") ?: JSONObject()
        return o.getJSONArray("wearables").length().toString() +
            " \u00b7 " + worn.keys().asSequence().joinToString(
                " \u00b7 ") { "$it ${worn.optString(it)}" }
    }

    suspend fun pairWearable(id: String, name: String, kind: String,
                             token: String): String {
        val o = JSONObject(request("/profiles/$id/wearables", "POST",
            JSONObject().put("name", name).put("kind", kind), token))
        return o.optString("name") + " \u00b7 " + o.optString("kind")
    }

    /** The record survives, so a lost watch cannot come back by name. */
    suspend fun unpairWearable(id: String, name: String,
                               token: String): Boolean {
        return JSONObject(request("/profiles/$id/wearables/$name",
            "DELETE", token = token)).optBoolean("revoked")
    }

    // ---- The birth ----

    /** The short interview a profile is born from. */
    suspend fun genesis(ownerId: String, name: String, social: String,
                        humor: String, matters: String,
                        comfort: String): String {
        val body = JSONObject()
            .put("owner_id", ownerId)
            .put("verification", JSONObject().put("birthdate", "1990-01-01"))
            .put("answers", JSONObject().put("social_style", social)
                .put("humor", humor).put("what_matters", matters)
                .put("comfort", comfort))
        if (name.isNotEmpty()) body.put("display_name", name)
        val o = JSONObject(request("/profiles/genesis", "POST", body))
        return o.optString("display_name", o.optString("id"))
    }

    /** A hybrid blended from several profiles; the blend is recorded. */
    suspend fun composite(ownerId: String, name: String,
                          sources: List<String>): String {
        val arr = org.json.JSONArray()
        sources.forEach { arr.put(JSONObject().put("profile_id", it)) }
        val o = JSONObject(request("/profiles/composite", "POST",
            JSONObject().put("owner_id", ownerId).put("display_name", name)
                .put("terms_consent", true)
                .put("verification",
                    JSONObject().put("birthdate", "1990-01-01"))
                .put("sources", arr)))
        return o.optString("display_name", o.optString("id"))
    }

    suspend fun publishPack(industry: String, title: String,
                            token: String): String {
        val items = org.json.JSONArray().put(
            JSONObject().put("title", title).put("content", title))
        return JSONObject(request("/packs", "POST",
            JSONObject().put("industry", industry).put("title", title)
                .put("items", items), token)).optString("title")
    }

    /** One free Field Pack per industry. */
    suspend fun seedPacks(): Int {
        val o = JSONObject(request("/packs/seed", "POST", JSONObject()))
        return o.optInt("created", o.optInt("packs"))
    }

    // ---- The mind at work ----

    /** Owner-only; the narrative is watermarked synthetic. */
    suspend fun simulate(id: String, scenario: String,
                         token: String): String {
        val o = JSONObject(request("/profiles/$id/simulate", "POST",
            JSONObject().put("scenario", scenario), token))
        return o.optString("narrative", o.optString("id"))
    }

    suspend fun simulations(id: String, token: String): Int {
        return org.json.JSONArray(request("/profiles/$id/simulations",
            token = token)).length()
    }

    suspend fun finetune(id: String, token: String): String {
        val o = JSONObject(request("/profiles/$id/finetune", "POST",
            JSONObject(), token))
        return o.optInt("messages_processed").toString() + " · " +
            o.optString("computed")
    }

    /** Exactly what would leave, and the log of what already has. */
    suspend fun cloudContribution(id: String, token: String): String {
        val o = JSONObject(request("/profiles/$id/cloud-contribution",
            token = token))
        val n = o.optJSONArray("contributed")?.length() ?: 0
        return (if (o.optBoolean("opted_in")) "on" else "off") +
            " \u00b7 " + n
    }

    /** Off, and everything already contributed deleted. */
    suspend fun revokeContributions(id: String, token: String): Int {
        return JSONObject(request(
            "/profiles/$id/cloud-contribution/revoke", "POST",
            JSONObject(), token)).optInt("revoked_count")
    }

    suspend fun excursion(cid: String, token: String): String {
        val o = JSONObject(request("/excursions/$cid", token = token))
        return o.optString("status") + " \u00b7 " + o.optString("findings")
    }

    // ---- The reach ----

    /** Allowed only when the owner opted in with proactive scope. */
    suspend fun proactiveCheckin(id: String, interactorId: String,
                                 token: String): String {
        val o = JSONObject(request("/profiles/$id/proactive/$interactorId",
            "POST", JSONObject(), token))
        return o.optString("message", o.optString("reason"))
    }

    /** The recipient's own window. */
    suspend fun setQuietHours(interactorId: String, start: Int?, end: Int?,
                              token: String): String {
        val body = JSONObject()
        if (start != null) body.put("quiet_start", start)
        if (end != null) body.put("quiet_end", end)
        val o = JSONObject(request("/interactors/$interactorId/quiet-hours",
            "PUT", body, token))
        return o.optInt("quiet_start", -1).toString() + "\u2013" +
            o.optInt("quiet_end", -1)
    }

    /** From the person who is rating — never in somebody else's name. */
    suspend fun giveFeedback(id: String, interactorId: String,
                             rating: String, token: String): String {
        return JSONObject(request(
            "/profiles/$id/interactions/$interactorId/feedback", "POST",
            JSONObject().put("rating", rating), token)).optString("rating")
    }

    suspend fun myReferrals(interactorId: String, token: String): Int {
        return org.json.JSONArray(request(
            "/interactors/$interactorId/referrals", token = token)).length()
    }

    // ---- The license ----

    suspend fun acquireLicense(id: String, token: String): String {
        return JSONObject(request("/profiles/$id/license/acquire", "POST",
            JSONObject(), token)).optString("id")
    }

    /** The derived agent records its origin. */
    suspend fun deriveAgent(id: String, grantId: String,
                            token: String): String {
        val o = JSONObject(request("/profiles/$id/license/$grantId/derive",
            "POST", JSONObject(), token))
        return o.optString("display_name", o.optString("id"))
    }

    // ---- The senses ----

    /** Hands-free guidance from what the camera recognises. */
    suspend fun perceive(id: String, objects: List<String>, goal: String,
                         token: String): String {
        val arr = org.json.JSONArray(); objects.forEach { arr.put(it) }
        val body = JSONObject().put("objects", arr)
        if (goal.isNotEmpty()) body.put("goal", goal)
        return JSONObject(request("/profiles/$id/perceive", "POST", body,
            token)).optString("guidance")
    }

    suspend fun microphonePlaces(): Int {
        return (JSONObject(request("/microphones/places"))
            .optJSONArray("places") ?: org.json.JSONArray()).length()
    }

    suspend fun microphoneVocabulary(): Int {
        return (JSONObject(request("/microphones/vocabulary"))
            .optJSONArray("refusals") ?: org.json.JSONArray()).length()
    }

    suspend fun overlaysCatalogue(): String {
        val o = JSONObject(request("/overlays/catalogue"))
        val kinds = o.optJSONArray("kinds") ?: org.json.JSONArray()
        val refusals = o.optJSONArray("refusals") ?: org.json.JSONArray()
        return kinds.length().toString() + " \u00b7 " + refusals.length()
    }

    /** The whole list, replaced wholesale — a CV is a statement. */
    suspend fun setExperience(id: String, title: String,
                              token: String): Int {
        val entries = org.json.JSONArray()
            .put(JSONObject().put("title", title))
        return JSONObject(request("/profiles/$id/experience", "PUT",
            JSONObject().put("entries", entries), token))
            .getJSONArray("experience").length()
    }

    // ---- Doors the other shells already had ----

    suspend fun health(): String {
        return JSONObject(request("/health")).optString("status", "ok")
    }

    /**
     * The backend's own version, for the guard that compares it with this
     * build's. Empty when the field is absent, which is a real answer and
     * not an error: a backend old enough to predate the field is exactly
     * the deployment the guard exists to name. `health` above reads the
     * same response and throws this away, which is why nothing on this
     * shell could tell a stale backend from a current one.
     */
    suspend fun backendVersion(): String {
        return JSONObject(request("/health")).optString("version", "")
    }

    suspend fun marketplaceListings(): Int {
        return org.json.JSONArray(request("/marketplace/listings")).length()
    }

    suspend fun listPacks(): Int {
        return org.json.JSONArray(request("/packs")).length()
    }

    suspend fun signaturePolicy(): String {
        return JSONObject(request("/signatures/policy")).toString()
            .take(80)
    }

    /** Retire a signing credential. */
    suspend fun removeSigningCredential(rowId: String, token: String) {
        request("/signatures/credentials/$rowId", "DELETE", token = token)
    }


    // ---- Widgets ----
    //
    // Small programs somebody writes for their own profile. Owner-scoped
    // at the door and again in the query behind it, so a widget id from
    // another profile is not found rather than refused. The code runs on
    // the backend in a box with no network, one directory, no child
    // processes and finite time — never on the phone.

    suspend fun widgetLimits(): WidgetCaps {
        val o = JSONObject(request("/studio/limits"))
        val caps = o.optJSONObject("allowances")
        return WidgetCaps(caps?.optInt("wall_seconds") ?: 0,
            caps?.optInt("heap_mb") ?: 0, o.optBoolean("available"))
    }

    /** What the agent may touch, published so somebody can read the whole
     *  list before letting it near anything. */
    suspend fun studioAgent(): AgentReach {
        val o = JSONObject(request("/studio/agent"))
        val rows = o.optJSONArray("can_touch")
        return AgentReach(
            (0 until (rows?.length() ?: 0)).map { rows!!.getString(it) },
            o.optBoolean("available"))
    }

    /** One turn. The conversation is the shell's to keep — the agent has no
     *  memory of its own, so leaving the screen is all of forgetting. */
    suspend fun authoringTurn(profileId: String, said: String,
                              history: List<Pair<String, String>>,
                              token: String): AgentTurn {
        val turns = org.json.JSONArray()
        history.forEach {
            turns.put(JSONObject().put("role", it.first).put("content", it.second))
        }
        val body = JSONObject().put("said", said).put("history", turns)
        val o = JSONObject(request("/profiles/$profileId/authoring/turn",
            "POST", body, token))
        val rows = o.optJSONArray("acted")
        val steps = (0 until (rows?.length() ?: 0)).map {
            val step = rows!!.getJSONObject(it)
            AgentStep(step.optString("tool"), step.optInt("answered"),
                step.optString("said").ifEmpty { null })
        }
        val asking = o.optJSONObject("asks")
        return AgentTurn(o.optString("reply"), steps,
            o.optString("said").ifEmpty { null },
            asking?.let {
                AgentAsks(it.optString("tool"),
                    it.optJSONObject("arguments") ?: JSONObject(),
                    it.optString("says"))
            })
    }

    /** The press. No prose and no model — the arguments go back as the JSON
     *  the turn handed over, which is what makes the sentence on the screen
     *  the thing agreed to rather than a summary of it. */
    suspend fun authoringAct(profileId: String, tool: String,
                             arguments: JSONObject,
                             token: String): AgentStep {
        val body = JSONObject().put("tool", tool).put("arguments", arguments)
        val o = JSONObject(request("/profiles/$profileId/authoring/act",
            "POST", body, token))
        return AgentStep(o.optString("tool"), o.optInt("answered"),
            o.optString("says").ifEmpty { null })
    }

    private fun widgetOf(o: JSONObject) = WidgetRow(
        o.optString("id"), o.optString("name"), o.optString("source"),
        o.optInt("version", 1))

    suspend fun widgets(profileId: String, token: String): List<WidgetRow> {
        val rows = JSONObject(request("/profiles/$profileId/widgets", token = token))
            .optJSONArray("widgets") ?: return emptyList()
        return (0 until rows.length()).map { widgetOf(rows.getJSONObject(it)) }
    }

    suspend fun widget(profileId: String, widgetId: String, token: String) =
        widgetOf(JSONObject(request("/profiles/$profileId/widgets/$widgetId", token = token)))

    suspend fun createWidget(profileId: String, name: String, source: String,
                             token: String): WidgetRow {
        val body = JSONObject().put("name", name).put("source", source)
        return widgetOf(JSONObject(request("/profiles/$profileId/widgets", "POST", body, token)))
    }

    suspend fun updateWidget(profileId: String, widgetId: String, name: String,
                             source: String, token: String): WidgetRow {
        val body = JSONObject().put("name", name).put("source", source)
        return widgetOf(JSONObject(
            request("/profiles/$profileId/widgets/$widgetId", "PUT", body, token)))
    }

    /** Answers the id that is gone, so a caller can say which one. */
    suspend fun deleteWidget(profileId: String, widgetId: String, token: String): String =
        JSONObject(request("/profiles/$profileId/widgets/$widgetId", "DELETE", token = token))
            .optString("widget_id")

    suspend fun runWidget(profileId: String, widgetId: String,
                          token: String): WidgetAnswer {
        val o = JSONObject(request("/profiles/$profileId/widgets/$widgetId/run",
            "POST", JSONObject(), token))
        val value = if (o.isNull("value")) null else o.get("value").toString()
        return WidgetAnswer(o.optString("status"), o.optInt("ms"),
            o.optString("said").ifEmpty { null },
            o.optString("message").ifEmpty { null }, value)
    }
}

data class DmThread(val otherId: String, val otherName: String?, val messages: Int)
data class DmMessage(val id: String, val senderId: String, val body: String)
data class HomepageDoc(val headline: String, val about: String,
                       val bg: String, val accent: String)

data class ShopCard(val id: String, val name: String, val seller: String,
                    val tag: String?, val offerings: Int)
data class ShopOffering(val id: String, val kind: String, val title: String,
                        val price: Double, val currency: String,
                        val availability: String, val retired: Int)
data class ShopDetail(val id: String, val name: String, val blurb: String?,
                      val seller: String?, val offerings: List<ShopOffering>)
data class ShopOrder(val id: String, val shopId: String, val title: String,
                     val quantity: Int, val amount: Double,
                     val currency: String, val status: String)

data class ObjectionTimelineEvent(val id: String, val event: String,
                                  val actor: String, val sealed: Boolean,
                                  val at: String)
data class ObjectionTimeline(val status: String, val note: String,
                             val events: List<ObjectionTimelineEvent>)


data class FriendRow(val profileId: String, val displayName: String?,
                     val founder: Boolean, val pinned: Boolean,
                     val mutual: Boolean)

/**
 * A profile's decorated page, as a visitor receives it — the whole answer
 * rather than the one line `page` flattens it to. `customised` is false when
 * they never decorated it: the route replies with a full default instead of
 * 404, so without this a bare page and a styled one look the same.
 */
data class PageCardFull(val tagline: String?, val about: String?,
                        val accent: String?,
                        val topFriends: List<PageFriendRow>,
                        val links: List<PageLink>,
                        val offers: List<PageOffer>,
                        /** Sanitised in storage, deliberately not rendered
                         *  here — see `ProfilePagePanel`. */
                        val html: String?,
                        val customised: Boolean)

data class PageFriendRow(val profileId: String, val displayName: String?)
data class PageLink(val label: String?, val url: String)
data class PageOffer(val title: String, val blurb: String?)
data class MediaRow(val kind: String, val alt: String, val name: String,
                    val id: String)

/**
 * One thing handed to a profile mid-conversation. `chars` against
 * `digestChars` is the point made visible: the long number was read once,
 * the short one is what every later turn carries. `read` false means the
 * bytes arrived and nobody could turn them into words — a photograph, a
 * video, a scan — and the screen says so rather than implying otherwise.
 */
data class BriefcaseRow(val id: String, val kind: String, val title: String,
                        val note: String?, val source: String?,
                        val read: Boolean, val digest: String,
                        val chars: Int, val digestChars: Int,
                        val text: String?)

data class BriefcaseBoard(val items: List<BriefcaseRow>, val maxItems: Int,
                          val offline: Boolean)

data class InboxEvent(val id: String, val kind: String, val actorId: String,
                      val actorName: String?, val seen: Boolean)

data class InboxPage(val events: List<InboxEvent>, val unseen: Int)

data class SuggestedRow(val profileId: String, val displayName: String?,
                        val because: String?)

data class WallPost(val id: String, val body: String, val status: String,
                    val likes: Int)

data class CommentRow(val id: String, val authorId: String,
                      val body: String, val status: String)


/// What `POST /desks` hands back, and the only place the desk token appears.
/// Deliberately not `DeskCard`: that is the public card `GET /desks/{id}`
/// returns, with the attestation a visitor reads. Both carried one name in
/// all three shells at once.
data class DeskOpened(val deskId: String, val displayName: String,
                      val trade: String?, val location: String?,
                      val presence: String, val rated: Boolean,
                      val deskToken: String?)

data class DeskBrief(val id: String, val displayName: String,
                     val trade: String?, val location: String?,
                     val presence: String)

data class DeskRing(val id: String, val note: String?)

data class DeskGuest(val id: String, val guestId: String,
                     val displayName: String?, val status: String)

data class DeskBeacon(val id: String, val label: String?)

data class DeskOverlay(val likes: Int, val shares: Int, val waiting: Int)

data class MarketCard(val profileId: String, val displayName: String,
                      val blurb: String?)

data class MarketHit(val id: String, val title: String)

data class MarketOffer(val amount: Double?, val currency: String)

data class MarketSale(val id: String, val status: String)

data class ExchangeVocabulary(val industries: List<String>,
                              val rules: List<String>)

data class ExchangeItemRow(val id: String, val name: String,
                           val kind: String)

data class ExchangeDeal(val id: String, val work: String?,
                        val state: String, val items: List<ExchangeItemRow>)
// Audience verbs, the watch party, and skill grants: three blocks the
// doorless records said this phone could not reach.

data class AudienceCounts(val likes: Int, val comments: Int, val shares: Int,
                          val subscribers: Int)

data class GiftRow(val giverId: String, val amount: Double, val note: String)

data class PartyCard(val id: String, val title: String, val state: String,
                     val positionS: Int, val members: Int)

data class PartyLine(val memberId: String, val body: String)

data class GrantCard(val id: String, val title: String, val state: String,
                     val lenderId: String, val borrowerId: String)

data class GrantUse(val usedAt: String, val what: String)


// -- Widgets ------------------------------------------------------------------
//
// Small programs somebody writes for their own profile. Owner-scoped at the
// door and again in the query behind it, so a widget id from another profile
// is not found rather than refused. The code runs on the backend in a box
// with no network, one directory, no child processes and finite time — never
// on the phone.

data class WidgetRow(val id: String, val name: String, val source: String, val revision: Int)

/** What a run said. `status` is ok, error, timeout, killed or refused; the
 *  value is kept as text because a widget's answer is its author's shape. */
data class WidgetAnswer(val status: String, val ms: Int, val said: String?,
                        val message: String?, val value: String?)

data class WidgetCaps(val wallSeconds: Int, val heapMb: Int, val available: Boolean)

data class AgentReach(val canTouch: List<String>, val available: Boolean)

/** What one turn did, under what it said. An agent that describes an edit in
 *  prose is asking to be believed; the steps are the part that can be checked. */
data class AgentStep(val tool: String, val answered: Int, val said: String?)

data class AgentTurn(val reply: String, val acted: List<AgentStep>,
                     val said: String?, val asks: AgentAsks?)

/** What it stopped to ask about, when it reached for a step that cannot be
 *  taken back. `says` is the roster's own sentence — the same words the list
 *  of what it can touch used — so the thing being agreed to is the thing that
 *  was promised. `arguments` is what it chose, carried as the JSON that
 *  arrived so the press sends back exactly what the screen showed. */
data class AgentAsks(val tool: String, val arguments: JSONObject,
                     val says: String)

