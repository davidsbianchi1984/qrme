package app.qrme.studio

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.media.MediaPlayer
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.speech.tts.TextToSpeech
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import java.io.File
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.util.Locale

/**
 * The conversation that keeps going when this app is not on screen.
 *
 * The console's walk-along strip carries a conversation across a tab change
 * and stops dead when the browser puts the page away. That is not a
 * shortcoming of the strip — a backgrounded web page has its recogniser
 * ended by the browser — and the strip says so rather than pretending.
 *
 *     asked     can the conversation survive a screen change
 *     mattered  can it survive leaving the application
 *
 * On a phone the answer can be yes, and the price is a foreground service
 * holding a microphone while the person is in another app entirely. The
 * notification it must show is not a platform tax to be minimised: it is the
 * whole difference between *the conversation you took with you* and *an app
 * recording you after you left it*, and the two are the same code with
 * different honesty.
 *
 * ## Two conversations, one service
 *
 * A synthetic profile answers through `POST /profiles/{id}/chat`; the agent
 * answers through the authoring turn and keeps no memory of its own, so the
 * thread has to be carried here. The console met the same fork and answered
 * it by handing the strip a callback — the screen knows its own wire and the
 * strip stays ignorant. A Service cannot be handed a lambda across a
 * `startForegroundService`, so this one is told *which kind* instead, in one
 * extra, and the fork is two branches in `take` rather than two services.
 *
 *     asked     can the service carry this conversation
 *     mattered  how many wires does it have to know
 *
 * ## The designation travels
 *
 * Whoever is being talked to here is a synthetic profile, and a person must
 * know that at all times — including in a notification glanced at from
 * another app, which is the moment they have the least context. So the title
 * carries the profile's watermark line, the same designation the chat bubble
 * wears, rather than the bare display name.
 *
 * ## Written without a compiler
 *
 * There is no Android toolchain in the environment this was written in, so
 * the guard beside it reads the declarations rather than the behaviour: the
 * permissions and service type, the foreground start, the notification and
 * its stop. Those are the parts whose absence is a microphone with no
 * indicator. The loop itself has been reasoned about and not run.
 */
object Walking {

    var underway by mutableStateOf(false)
        internal set
    var heard by mutableStateOf("")
        internal set
    var said by mutableStateOf("")
        internal set
    /** Why it stopped, when it stopped for a reason. Empty when somebody
     *  pressed End — they know. */
    var trouble by mutableStateOf("")
        internal set

    /** Bumped every time a walk begins, so the shell can land the person on
     *  the front page. The point of taking a conversation with you is going
     *  somewhere, and the screen you were on is the one place you have
     *  finished with.
     *
     *  A counter rather than a flag: a second walk started from the front
     *  page must still land there, and a boolean already true would say
     *  nothing happened. */
    var landings by mutableStateOf(0)
        internal set

    /** True when the last turn was answered by the local fallback rather
     *  than by the model this profile is set to. Not a failure — a
     *  deployment with no key still answers — but not the voice somebody
     *  chose either, and out here there is no amber banner to notice it on. */
    var offline by mutableStateOf(false)
        internal set

    /** Carry a conversation with a synthetic profile. */
    fun start(context: Context, profileId: String, token: String,
              interactorId: String, shownName: String, lang: String) {
        begin(context, WalkService.KIND_PROFILE, profileId, token,
              interactorId, shownName, lang)
    }

    /** Carry the console's agent. No interactor — the authoring turn is the
     *  owner's own door — and the thread lives in the service, because the
     *  agent keeps no memory of its own. */
    fun startAgent(context: Context, profileId: String, token: String,
                   shownName: String, lang: String) {
        begin(context, WalkService.KIND_AGENT, profileId, token, "",
              shownName, lang)
    }

    private fun begin(context: Context, kind: String, profileId: String,
                      token: String, interactorId: String, shownName: String,
                      lang: String) {
        val intent = Intent(context, WalkService::class.java)
            .putExtra(WalkService.EXTRA_KIND, kind)
            .putExtra(WalkService.EXTRA_PROFILE, profileId)
            .putExtra(WalkService.EXTRA_TOKEN, token)
            .putExtra(WalkService.EXTRA_INTERACTOR, interactorId)
            .putExtra(WalkService.EXTRA_NAME, shownName)
            .putExtra(WalkService.EXTRA_LANG, lang)
        // `startForegroundService`: the service has one window to call
        // `startForeground` and the system kills it if it does not, which is
        // the platform enforcing the same rule this file is about.
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            context.startForegroundService(intent)
        } else {
            context.startService(intent)
        }
    }

    fun stop(context: Context) {
        context.startService(
            Intent(context, WalkService::class.java)
                .setAction(WalkService.ACTION_STOP))
    }
}

class WalkService : Service() {

    companion object {
        const val EXTRA_KIND = "kind"
        /** A synthetic profile, answering through its own chat door. */
        const val KIND_PROFILE = "profile"
        /** The console's agent, answering through the authoring turn. */
        const val KIND_AGENT = "agent"
        const val EXTRA_PROFILE = "profile"
        const val EXTRA_TOKEN = "token"
        const val EXTRA_INTERACTOR = "interactor"
        const val EXTRA_NAME = "name"
        const val EXTRA_LANG = "lang"
        const val ACTION_STOP = "app.qrme.studio.WALK_STOP"
        private const val CHANNEL = "walk"
        private const val NOTE_ID = 4201
    }

    private val main = Handler(Looper.getMainLooper())
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private var recogniser: SpeechRecognizer? = null
    private var speaker: TextToSpeech? = null
    /** The profile's own voice. Held, so leaving ends it with everything
     *  else — a bound voice talking on under a stopped walk is the same
     *  defect as an indicator that outlives the microphone. */
    private var player: MediaPlayer? = null
    private var kind: String = KIND_PROFILE
    /** The agent's thread. It keeps no memory of its own — which is the
     *  cheaper design and the one where *forget this* is something a person
     *  can actually do — so whoever is talking to it holds the transcript.
     *  Out here that is this service, and it goes when the service does. */
    private val thread = mutableListOf<Pair<String, String>>()
    private var profileId: String = ""
    private var token: String = ""
    private var interactorId: String = ""
    private var shownName: String = ""
    private var lang: String = "en"
    /** Every opening of the ear carries a number, and a late callback from a
     *  superseded one is ignored. The console learned this the hard way: one
     *  shared flag meant a stale error closed the ear that had replaced it,
     *  and the microphone died a fifth of a second after it opened. */
    private var turn = 0
    private var wants = false

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (intent?.action == ACTION_STOP) {
            close(reason = "")
            return START_NOT_STICKY
        }
        kind = intent?.getStringExtra(EXTRA_KIND) ?: KIND_PROFILE
        profileId = intent?.getStringExtra(EXTRA_PROFILE).orEmpty()
        token = intent?.getStringExtra(EXTRA_TOKEN).orEmpty()
        interactorId = intent?.getStringExtra(EXTRA_INTERACTOR).orEmpty()
        shownName = intent?.getStringExtra(EXTRA_NAME).orEmpty()
        lang = intent?.getStringExtra(EXTRA_LANG) ?: "en"
        // The agent needs no interactor: the authoring turn is the owner's
        // own door, reached with the owner's own token.
        if (profileId.isEmpty() || token.isEmpty()
            || (kind == KIND_PROFILE && interactorId.isEmpty())) {
            stopSelf()
            return START_NOT_STICKY
        }
        goForeground()
        Walking.underway = true
        Walking.trouble = ""
        Walking.landings += 1
        speaker = TextToSpeech(this) { }.also {
            it.language = Locale.forLanguageTag(lang)
        }
        wants = true
        main.post { hear() }
        // NOT sticky. A service the system restarts after killing it is a
        // microphone that reopens without anybody pressing anything, which
        // is the one thing this must never be.
        return START_NOT_STICKY
    }

    override fun onDestroy() {
        close(reason = "")
        scope.cancel()
        super.onDestroy()
    }

    // -- the notification ----------------------------------------------------

    private fun goForeground() {
        val manager = getSystemService(NotificationManager::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            manager.createNotificationChannel(
                NotificationChannel(CHANNEL,
                    L10n.t("walk.note.channel", lang),
                    // Low, not minimum: visible in the shade for as long as
                    // the microphone is open, and silent between turns.
                    NotificationManager.IMPORTANCE_LOW))
        }
        val stop = PendingIntent.getService(
            this, 0,
            Intent(this, WalkService::class.java).setAction(ACTION_STOP),
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT)
        // The designation, in the one place a person has the least context.
        // `shownName` is handed in already carrying the profile's watermark
        // line; this is the belt to that braces, so a name that arrived bare
        // still says what it is.
        // A synthetic profile stands in for a person and must say it is an
        // AI. The agent is the console's own tool and is named as itself —
        // prepending a designation to it would be noise, and noise is how a
        // designation stops being read where it matters.
        val who = if (kind == KIND_AGENT
                      || shownName.lowercase().contains("ai")) shownName
                  else L10n.t("walk.note.ai", lang) + " " + shownName
        val note: Notification = Notification.Builder(this, CHANNEL)
            .setContentTitle(L10n.fill("walk.note.title", lang,
                                       mapOf("who" to who)))
            .setContentText(
                if (Walking.offline)
                    L10n.t("walk.note.body", lang) + " "
                        + L10n.t("walk.offline", lang)
                else L10n.t("walk.note.body", lang))
            .setSmallIcon(android.R.drawable.ic_btn_speak_now)
            .setOngoing(true)
            .addAction(Notification.Action.Builder(
                null, L10n.t("nc.end", lang), stop).build())
            .build()
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(NOTE_ID, note,
                ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE)
        } else {
            startForeground(NOTE_ID, note)
        }
    }

    // -- one turn ------------------------------------------------------------

    private fun hear() {
        if (!wants) return
        if (!SpeechRecognizer.isRecognitionAvailable(this)) {
            close(reason = L10n.t("walk.trouble.norecogniser", lang))
            return
        }
        val mine = ++turn
        fun live() = mine == turn && wants
        val rec = SpeechRecognizer.createSpeechRecognizer(this)
        recogniser = rec
        rec.setRecognitionListener(object : RecognitionListener {
            override fun onResults(results: android.os.Bundle?) {
                if (!live()) return
                val text = results
                    ?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                    ?.firstOrNull()
                    .orEmpty()
                    .trim()
                if (text.isEmpty()) { main.post { hear() }; return }
                Walking.heard = text
                take(mine, text)
            }

            override fun onError(code: Int) {
                if (!live()) return
                // Quiet is not a failure in a standing conversation — the
                // microphone simply opens again. Everything else stops and
                // says which failure it was, because a refused microphone
                // reported as quiet is a loop that reopens forever with
                // nothing to hear and nothing to say about it.
                when (code) {
                    SpeechRecognizer.ERROR_NO_MATCH,
                    SpeechRecognizer.ERROR_SPEECH_TIMEOUT ->
                        main.post { hear() }
                    SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS ->
                        close(reason = L10n.t("walk.trouble.permission", lang))
                    SpeechRecognizer.ERROR_NETWORK,
                    SpeechRecognizer.ERROR_NETWORK_TIMEOUT ->
                        close(reason = L10n.t("walk.trouble.network", lang))
                    else ->
                        close(reason = L10n.t("walk.trouble.stopped", lang))
                }
            }

            override fun onReadyForSpeech(params: android.os.Bundle?) {}
            override fun onBeginningOfSpeech() {}
            override fun onRmsChanged(rms: Float) {}
            override fun onBufferReceived(buffer: ByteArray?) {}
            override fun onEndOfSpeech() {}
            override fun onPartialResults(partial: android.os.Bundle?) {}
            override fun onEvent(type: Int, params: android.os.Bundle?) {}
        })
        rec.startListening(
            Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
                .putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                          RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                .putExtra(RecognizerIntent.EXTRA_LANGUAGE, lang))
    }

    private fun take(mine: Int, message: String) {
        scope.launch {
            // Set by the profile branch below. The authoring turn reports no
            // provenance, so the agent's branch leaves this alone rather than
            // claiming a model answered — a false `false` is still a claim.
            var fromStore = false
            val text = if (kind == KIND_AGENT) {
                val turnTaken = runCatching {
                    ApiClient.authoringTurn(profileId, message,
                                            thread.toList(), token)
                }.getOrNull()
                if (mine != turn || !wants) return@launch
                // A row that cannot be taken back comes back as a proposal
                // rather than an act, and answering it needs a press on a
                // screen. Out here there is no screen, so the walk says what
                // it would do and leaves it — a yes spoken into a phone in
                // somebody's pocket is not the press that row is asking for.
                //
                //     asked     may this person do this
                //     mattered  did this person mean this
                if (turnTaken?.asks != null) {
                    val says = turnTaken.asks.says
                    thread.add("user" to message)
                    thread.add("assistant" to says)
                    L10n.fill("walk.agent.asks", lang, mapOf("what" to says))
                } else {
                    val reply = turnTaken?.reply.orEmpty()
                    if (reply.isNotEmpty()) {
                        thread.add("user" to message)
                        thread.add("assistant" to reply)
                    }
                    reply
                }
            } else {
                val reply = runCatching {
                    ApiClient.chat(profileId, token, interactorId, message)
                }.getOrNull()
                if (mine != turn || !wants) return@launch
                // A held or refused turn has no content, and the moderation
                // status is the reason. Speaking nothing and carrying on
                // would make a refusal indistinguishable from a quiet
                // moment.
                // Who actually wrote it, not who the profile is set to. An
                // owner whose key expired used to read stub-written text
                // under the name of the model they picked.
                fromStore = reply?.provenance?.generatedBy == "stub"
                if (reply?.status == "approved") reply.content.orEmpty() else ""
            }
            withContext(Dispatchers.Main) {
                if (mine != turn || !wants) return@withContext
                if (text.isEmpty()) {
                    Walking.said = L10n.t("walk.lost", lang)
                } else {
                    Walking.said = text
                    sayAloud(text)
                }
                // The notification is the only surface a person walking
                // about has. Rewritten under the same id rather than posted
                // fresh, so one notification stays one notification.
                if (fromStore != Walking.offline) {
                    Walking.offline = fromStore
                    goForeground()
                }
                // The next turn opens after the answer is handed to the
                // speaker rather than after it finishes: a person may
                // interrupt, and a conversation where interrupting is
                // impossible is a broadcast.
                hear()
            }
        }
    }

    /**
     * Say it in the profile's own voice, and fall back to the phone's only
     * when there is no such voice to be had.
     *
     * This is the point of the product, and the walk was missing it. The
     * first draft called [TextToSpeech] and stopped there — the generic
     * Android voice, for a profile whose whole identity includes how it
     * sounds, while `ApiClient.saySpoken` sat in the same package returning
     * watermarked audio in the bound voice and nothing called it. A field
     * report on the web strip put it plainly: *the voice is robotic again,
     * it should be my voice when I'm talking to my AI*. That was the strip;
     * this is the same thing out here, and JIM-mini's three shells had it as
     * well.
     *
     *     asked     did the reply get spoken
     *     mattered  in whose voice
     *
     * Both kinds go through it. An agent carries a profile id too, and a
     * deployment that bound a voice to that profile meant it to be used.
     *
     * The direction of the fallback is load-bearing: a bound voice that
     * fails must not leave silence, because the words are already on the
     * notification. The phone's own voice used *first* would be a different
     * thing — it never fails, so the bound voice would never be reached and
     * nobody would find out it was configured.
     *
     * The turn number rides along because this is a network call now. Audio
     * that arrives after the person has moved on must not talk over the turn
     * that replaced it — the rule the ear in this file already knows.
     */
    private fun sayAloud(text: String) {
        val mine = turn
        scope.launch {
            val audio = try {
                if (profileId.isEmpty() || token.isEmpty()) null
                else ApiClient.saySpoken(profileId, token, text)
                    .takeIf { it.isNotEmpty() }
            } catch (_: Exception) {
                null
            }
            withContext(Dispatchers.Main) {
                if (mine != turn || !wants) return@withContext
                if (audio == null) {
                    speaker?.speak(text, TextToSpeech.QUEUE_FLUSH, null, "walk")
                    return@withContext
                }
                try {
                    val file = File.createTempFile("walk", ".mp3", cacheDir)
                    file.writeBytes(audio)
                    player?.release()
                    player = MediaPlayer().apply {
                        setDataSource(file.absolutePath)
                        // Deleted when it finishes rather than kept. A
                        // watermarked utterance in somebody's enrolled voice
                        // is not a thing to leave lying in a cache.
                        setOnCompletionListener {
                            release(); file.delete()
                            if (player === this) player = null
                        }
                        prepare()
                        start()
                    }
                } catch (_: Exception) {
                    speaker?.speak(text, TextToSpeech.QUEUE_FLUSH, null, "walk")
                }
            }
        }
    }

    private fun close(reason: String) {
        wants = false
        turn += 1
        recogniser?.destroy()
        recogniser = null
        speaker?.stop()
        speaker?.shutdown()
        speaker = null
        try { player?.release() } catch (_: Exception) { }
        player = null
        thread.clear()
        Walking.underway = false
        Walking.offline = false
        Walking.trouble = reason
        stopForeground(STOP_FOREGROUND_REMOVE)
        stopSelf()
    }
}
