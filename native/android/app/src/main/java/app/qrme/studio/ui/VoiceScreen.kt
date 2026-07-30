package app.qrme.studio.ui

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.media.MediaRecorder
import android.os.Build
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.ContextCompat
import app.qrme.studio.ApiClient
import app.qrme.studio.StudioViewModel
import app.qrme.studio.VoiceEnrollment
import app.qrme.studio.VoiceRevocation
import app.qrme.studio.VoiceSpoken
import app.qrme.studio.VoiceprintStatus
import java.io.File
import kotlinx.coroutines.delay

/**
 * Voice enrollment, walked in the order FIG. 800 gates it: permission (802),
 * then collection (806/808), then the characteristics (810), then the print
 * (812) and what speaking with it always carries.
 *
 * The phone is the device with the microphone in it, so unlike the web console
 * — which asks the owner to type how many seconds they gathered — this screen
 * records the sample and measures it. What crosses the wire is still only the
 * measurement: the recording is written to this app's private cache, and the
 * profile database is told its name rather than its bytes.
 */
@Composable
fun VoiceScreen(vm: StudioViewModel) {
    val context = LocalContext.current
    var status by remember { mutableStateOf<VoiceprintStatus?>(null) }
    var spoken by remember { mutableStateOf<VoiceSpoken?>(null) }
    var revocation by remember { mutableStateOf<VoiceRevocation?>(null) }
    var say by remember { mutableStateOf("") }
    var error by remember { mutableStateOf<String?>(null) }
    var busy by remember { mutableStateOf(false) }

    val recorder = remember { VoiceRecorder(context) }
    var recording by remember { mutableStateOf(false) }
    var elapsed by remember { mutableStateOf(0.0) }

    var micGranted by remember {
        mutableStateOf(ContextCompat.checkSelfPermission(
            context, Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED)
    }
    val askMic = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()) { micGranted = it }

    fun reload() {
        val pid = vm.pid ?: return
        val token = vm.token ?: return
        vm.call({ ApiClient.voiceprint(pid, token) }) { r ->
            r.fold({ status = it }, { error = it.message })
        }
    }
    LaunchedEffect(Unit) { reload() }

    /** Run a call, then re-read the status so the counts shown are the
     *  backend's rather than a guess made on the device. */
    fun act(block: suspend () -> Unit) {
        busy = true; error = null
        vm.call({ block() }) { r ->
            busy = false
            r.fold({ reload() }, { error = it.message })
        }
    }

    // While recording, poll the meter so the timer moves and the turn count
    // accumulates. A turn is a stretch of speech between silences.
    LaunchedEffect(recording) {
        while (recording) {
            recorder.sample()
            elapsed = recorder.elapsedSeconds
            delay(250)
        }
    }
    DisposableEffect(Unit) { onDispose { recorder.discard() } }

    val consent = status?.consent
    val consented = consent?.granted == true
    val enrol = status?.enrollment
    val print = status?.voiceprint

    screenScroll {
        // ---- 802: the permission, before anything is collected ----
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("1 · Permission", color = Qrme.Txt, fontSize = 16.sp,
                fontWeight = FontWeight.Bold)
            if (consented) {
                Text("Granted for ${consent!!.sources.joinToString(", ")}" +
                     (consent.grantedAt?.let { " · ${it.take(10)}" } ?: ""),
                    color = Qrme.T2, fontSize = 12.sp)
                Pill("Withdraw consent — delete the samples, retire the voice",
                    Qrme.Red, enabled = !busy) {
                    val pid = vm.pid ?: return@Pill
                    val token = vm.token ?: return@Pill
                    busy = true; error = null
                    vm.call({ ApiClient.revokeVoiceprint(pid, token) }) { r ->
                        busy = false
                        r.fold({ revocation = it; reload() }, { error = it.message })
                    }
                }
                revocation?.let {
                    Text("${it.samplesDeleted} sample(s) deleted. ${it.note}",
                        color = Qrme.Amber, fontSize = 11.sp)
                }
            } else {
                Text("Nothing is recorded until you say so. QRME will only learn " +
                     "your own voice — there is no path here for anybody else's.",
                    color = Qrme.T2, fontSize = 12.sp)
                Pill("This is my own voice — allow enrollment", Qrme.BrandA,
                    enabled = !busy) {
                    val pid = vm.pid ?: return@Pill
                    val token = vm.token ?: return@Pill
                    act {
                        ApiClient.grantVoiceConsent(pid, token,
                            listOf("call", "voice_note", "direct"))
                    }
                }
            }
        }

        if (consented) {
            // ---- 806/808/810: samples, and what they amount to ----
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("2 · Enrollment", color = Qrme.Txt, fontSize = 16.sp,
                    fontWeight = FontWeight.Bold)
                Text("Tap record and talk normally — a sentence or two about your " +
                     "day is better material than a read-aloud paragraph.",
                    color = Qrme.T2, fontSize = 12.sp)

                Row(verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    Pill(if (recording) "Stop" else "Record a sample",
                        if (recording) Qrme.Red else Qrme.BrandA, enabled = !busy) {
                        if (recording) {
                            recording = false
                            val taken = recorder.stop()
                            val pid = vm.pid
                            val token = vm.token
                            if (taken != null && pid != null && token != null) {
                                act {
                                    ApiClient.addVoiceSample(pid, token, "direct",
                                        taken.seconds, taken.turns, taken.reference)
                                }
                            }
                        } else if (!micGranted) {
                            askMic.launch(Manifest.permission.RECORD_AUDIO)
                        } else {
                            error = recorder.start()
                            recording = error == null
                            elapsed = 0.0
                        }
                    }
                    if (recording) {
                        Text("%.0fs".format(elapsed), color = Qrme.Green,
                            fontSize = 15.sp, fontWeight = FontWeight.Bold)
                    }
                }
                if (!micGranted) {
                    Text("Microphone access is off for QRME — recording asks for " +
                         "it the first time.", color = Qrme.T3, fontSize = 11.sp)
                }

                enrol?.let { e ->
                    Row(Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween) {
                        Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                            Text("${e.samples} sample(s) · %.1fs".format(e.seconds),
                                color = Qrme.Txt, fontSize = 14.sp,
                                fontWeight = FontWeight.Bold)
                            Text(turnLine(e) + " · needs ${e.wantSamples} samples " +
                                 "and %.0fs".format(e.wantSeconds),
                                color = Qrme.T3, fontSize = 10.sp)
                        }
                        Text(if (e.ready) "ready" else "not yet",
                            color = if (e.ready) Qrme.Green else Qrme.Amber,
                            fontSize = 11.sp, fontWeight = FontWeight.Bold)
                    }
                    if (!e.ready && e.needs.isNotEmpty()) {
                        Text("Still wants: ${e.needs.joinToString(", ")}.",
                            color = Qrme.T2, fontSize = 11.sp)
                    }
                    Text(e.method, color = Qrme.T3, fontSize = 10.sp)
                }
                Text("The recording stays on this device. Only its length and " +
                     "turn count are sent.", color = Qrme.T3, fontSize = 10.sp)
            }

            // ---- 812: the print, and speaking with it ----
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("3 · The voice", color = Qrme.Txt, fontSize = 16.sp,
                    fontWeight = FontWeight.Bold)
                if (print != null && print.active) {
                    Text("Built ${print.builtAt?.take(10) ?: "—"} · ${print.id}",
                        color = Qrme.T3, fontSize = 10.sp)
                    labeledField("Say something in it", say, "…") { say = it }
                    Pill("Speak", Qrme.BrandA, enabled = !busy && say.isNotBlank()) {
                        val pid = vm.pid ?: return@Pill
                        val token = vm.token ?: return@Pill
                        busy = true; error = null
                        vm.call({ ApiClient.speakInVoice(pid, token, say) }) { r ->
                            busy = false
                            r.fold({ spoken = it }, { error = it.message })
                        }
                    }
                    spoken?.let {
                        Text(it.basis, color = Qrme.T2, fontSize = 11.sp)
                        Text(it.disclosure, color = Qrme.Amber, fontSize = 12.sp)
                    }
                } else {
                    Text(if (enrol?.ready == true)
                             "Enough of your voice is on record — mint the voiceprint."
                         else "Record a few more samples first.",
                        color = Qrme.T2, fontSize = 12.sp)
                    Pill("Build my voiceprint", Qrme.BrandA,
                        enabled = !busy && enrol?.ready == true) {
                        val pid = vm.pid ?: return@Pill
                        val token = vm.token ?: return@Pill
                        act { ApiClient.buildVoiceprint(pid, token) }
                    }
                    if (print != null && !print.active) {
                        Text("A previous voiceprint was retired when consent was " +
                             "withdrawn. That record stays.",
                            color = Qrme.T3, fontSize = 10.sp)
                    }
                }
            }
        }

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Text("What always holds", color = Qrme.Txt, fontSize = 16.sp,
                fontWeight = FontWeight.Bold)
            listOf(
                "Anything spoken in this voice carries a watermark and says it is synthesized.",
                "Only your own voice — the permission is an attestation, not a checkbox.",
                "Withdrawing deletes the samples and silences the voice; the withdrawal stays on record.",
            ).forEach { Text("· $it", color = Qrme.T2, fontSize = 11.sp) }
            status?.disclosure?.takeIf { it.isNotBlank() }?.let {
                Text(it, color = Qrme.T3, fontSize = 10.sp)
            }
        }

        error?.let { Text(it, color = Qrme.Red, fontSize = 12.sp) }
    }
}

private fun turnLine(e: VoiceEnrollment) =
    e.meanTurnSeconds?.let { "about %.1fs a turn".format(it) }
        ?: "no turns counted yet"

@Composable
private fun Pill(text: String, tint: Color, enabled: Boolean, onClick: () -> Unit) {
    Box(
        Modifier.clip(RoundedCornerShape(50))
            .background(if (enabled) tint else Qrme.Card)
            .clickable(enabled = enabled) { onClick() }
            .padding(horizontal = 14.dp, vertical = 9.dp),
        contentAlignment = Alignment.Center,
    ) {
        Text(text, color = if (enabled) Color.White else Qrme.T3,
            fontSize = 12.sp, fontWeight = FontWeight.Bold)
    }
}

/**
 * Records to the app's private cache and reports how long it ran and how many
 * spoken stretches it heard. It never hands the audio anywhere — the file is
 * left on disk for the deployment's media policy to collect, which is what
 * the backend's `reference` field names.
 */
internal class VoiceRecorder(private val context: Context) {
    data class Sample(val seconds: Double, val turns: Int, val reference: String)

    private var recorder: MediaRecorder? = null
    private var file: File? = null
    private var startedAt = 0L
    private var turns = 0
    private var speaking = false

    /**
     * MediaRecorder reports amplitude on a 0–32767 scale. Anything above this
     * counts as speech rather than room noise; indoors the two sit comfortably
     * either side of it.
     */
    private val speechFloor = 2_500

    val elapsedSeconds: Double
        get() = if (startedAt == 0L) 0.0
                else (System.currentTimeMillis() - startedAt) / 1000.0

    /** Returns null on success, or a message the screen can show. */
    fun start(): String? {
        return try {
            val target = File(context.cacheDir, "voice-${System.currentTimeMillis()}.m4a")
            @Suppress("DEPRECATION")
            val rec = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S)
                MediaRecorder(context) else MediaRecorder()
            rec.setAudioSource(MediaRecorder.AudioSource.MIC)
            rec.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
            rec.setAudioEncoder(MediaRecorder.AudioEncoder.AAC)
            rec.setAudioSamplingRate(44_100)
            rec.setAudioChannels(1)
            rec.setOutputFile(target.absolutePath)
            rec.prepare()
            rec.start()
            recorder = rec
            file = target
            startedAt = System.currentTimeMillis()
            turns = 0
            speaking = false
            null
        } catch (e: Exception) {
            release()
            "Could not open the microphone: ${e.message}"
        }
    }

    /** Poll the meter. A turn is a rising edge from silence into speech. */
    fun sample() {
        val rec = recorder ?: return
        val loud = try { rec.maxAmplitude > speechFloor } catch (e: Exception) { false }
        if (loud && !speaking) turns++
        speaking = loud
    }

    fun stop(): Sample? {
        val seconds = elapsedSeconds
        val name = file?.name
        release()
        if (seconds <= 0 || name == null) return null
        return Sample(Math.round(seconds * 10) / 10.0, maxOf(1, turns), name)
    }

    /** Abandon an in-flight recording — leaving the mic open is worse than
     *  losing the sample, so this is safe to call from teardown. */
    fun discard() {
        release()
        file?.delete()
        file = null
    }

    private fun release() {
        try { recorder?.stop() } catch (e: Exception) { /* never started */ }
        recorder?.release()
        recorder = null
        startedAt = 0L
    }
}
