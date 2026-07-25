package app.qrme.studio.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import coil.compose.AsyncImage
import app.qrme.studio.ApiClient
import app.qrme.studio.DeskCard
import app.qrme.studio.RingReceipt
import kotlinx.coroutines.launch

/**
 * A live desk: an actual person offering a service, waiting behind a camera
 * view of their own counter.
 *
 * Deliberately the mirror image of [BeaconScannerScreen]. There, a synthetic
 * profile appears and the AI mark is drawn from the same payload as the face
 * so the two cannot come apart. Here there is **no mark at all** — stamping
 * "AI" on a real person is not a cautious default, it tells the visitor the
 * human they are waiting for does not exist.
 *
 * Absence of a badge would be ambiguous on its own, so the claim is positive:
 * *a person, not AI*, with the attestation behind it on screen rather than
 * filed in a policy somewhere.
 *
 * And when the chair is empty there is a bell. The sign taped to the chair
 * says to ring it; this is that bell, on the screen the visitor is already
 * looking at.
 */
@Composable
fun DeskScreen(deskId: String, callerId: String? = null) {
    val scope = rememberCoroutineScope()
    var card by remember { mutableStateOf<DeskCard?>(null) }
    var receipt by remember { mutableStateOf<RingReceipt?>(null) }
    var note by remember { mutableStateOf("") }
    var error by remember { mutableStateOf<String?>(null) }
    var ringing by remember { mutableStateOf(false) }

    suspend fun reload() {
        runCatching { ApiClient.desk(deskId) }
            .onSuccess { card = it }
            .onFailure { error = it.message }
    }
    LaunchedEffect(deskId) { reload() }

    screenScroll {
        val c = card
        Box(
            Modifier.fillMaxWidth().aspectRatio(4f / 3f)
                .clip(RoundedCornerShape(16.dp)).background(Qrme.Card),
        ) {
            if (c != null) {
                AsyncImage(
                    model = ApiClient.base.trimEnd('/') + c.feed.url,
                    contentDescription = "The desk",
                    contentScale = ContentScale.Crop,
                    modifier = Modifier.fillMaxWidth().aspectRatio(4f / 3f))
            }
            // The one label this image carries says whether it is live —
            // which is what somebody staring at an empty chair actually needs
            // to know. Never a watermark: it is a photograph of a real room.
            if (c != null) {
                Box(
                    Modifier.align(Alignment.BottomStart).padding(10.dp)
                        .clip(CircleShape)
                        .background(Color.Black.copy(alpha = 0.6f))
                        .padding(horizontal = 8.dp, vertical = 4.dp),
                ) {
                    Text(
                        if (c.feed.live) "● LIVE" else "SAMPLE VIEW",
                        color = if (c.feed.live) Qrme.Red
                        else Color.White.copy(alpha = 0.85f),
                        fontSize = 11.sp, fontWeight = FontWeight.Bold)
                }
            }
        }

        if (c != null) {
            if (!c.feed.live) {
                Text(c.feed.note, color = Qrme.T3, fontSize = 11.sp)
            }
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text(c.displayName, color = Qrme.Txt, fontSize = 20.sp,
                    fontWeight = FontWeight.Bold)
                Text(c.trade + (c.location?.let { " · $it" } ?: ""),
                    color = Qrme.T2, fontSize = 13.sp)
                // The positive claim, in place of the mark a synthetic profile
                // would carry here.
                Text("✓ ${c.designation}", color = Qrme.Green, fontSize = 12.sp,
                    fontWeight = FontWeight.Bold)
                Text(
                    when (c.presence) {
                        "attended" -> "At the desk"
                        "closed" -> "Closed — not taking callers"
                        else -> "Away from the desk"
                    },
                    color = if (c.presence == "attended") Qrme.Green else Qrme.T2,
                    fontSize = 14.sp)
                c.blurb?.let { Text(it, color = Qrme.T2, fontSize = 12.sp) }
            }

            if (c.bellAvailable) {
                Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    labeledField("Anything they should know? (optional)", note,
                        "need a key cut") { note = it }
                    Box(
                        Modifier.fillMaxWidth().clip(RoundedCornerShape(14.dp))
                            .background(Qrme.BrandA)
                            .clickable(enabled = !ringing) {
                                ringing = true; error = null
                                scope.launch {
                                    runCatching {
                                        ApiClient.ringBell(
                                            deskId, callerId,
                                            note.ifBlank { null })
                                    }.onSuccess { receipt = it }
                                        .onFailure { error = it.message }
                                    ringing = false
                                    reload()
                                }
                            }
                            .padding(vertical = 14.dp),
                        Alignment.Center,
                    ) {
                        Text(if (ringing) "Ringing…" else "🔔  Ring the bell",
                            color = Color.White, fontSize = 16.sp,
                            fontWeight = FontWeight.Bold)
                    }
                    val done = receipt
                    if (done != null) {
                        Text(done.note, color = Qrme.Green, fontSize = 12.sp)
                    } else if (c.waiting > 0) {
                        Text("${c.waiting} waiting", color = Qrme.T3,
                            fontSize = 11.sp)
                    }
                }
            } else {
                Text("The bell is off while this desk is closed.",
                    color = Qrme.T2, fontSize = 12.sp)
            }

            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Text("Attested by ${c.attestation.attestor}", color = Qrme.Txt,
                    fontSize = 12.sp, fontWeight = FontWeight.Bold)
                Text(c.attestation.basis, color = Qrme.T2, fontSize = 11.sp)
                if (c.attestation.signed) {
                    Text("✓ Signed", color = Qrme.Green, fontSize = 11.sp)
                }
                // Shipped with the claim, always: "recorded" and "proven" are
                // different words and the difference is the whole point.
                Text(c.attestation.note, color = Qrme.T3, fontSize = 10.sp)
            }
        }

        error?.let { Text(it, color = Qrme.Red, fontSize = 13.sp) }
    }
}
