package app.qrme.studio.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
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
import app.qrme.studio.DeskSession
import app.qrme.studio.L10n
import app.qrme.studio.DeskCard
import app.qrme.studio.RingReceipt
import app.qrme.studio.StreamJoin
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
fun DeskScreen(deskId: String, callerId: String? = null,
               viewerToken: String? = null, lang: String = "en") {
    val scope = rememberCoroutineScope()
    var card by remember { mutableStateOf<DeskCard?>(null) }
    var receipt by remember { mutableStateOf<RingReceipt?>(null) }
    var note by remember { mutableStateOf("") }
    var error by remember { mutableStateOf<String?>(null) }
    var ringing by remember { mutableStateOf(false) }
    var joined by remember { mutableStateOf<StreamJoin?>(null) }
    // The counter: the caller's sessions (offers to answer, links to end)
    // and, with a pasted desk token, the staffer's half.
    var mySessions by remember { mutableStateOf<List<DeskSession>>(emptyList()) }
    var deskToken by remember { mutableStateOf("") }
    var staffSessions by remember { mutableStateOf<List<DeskSession>>(emptyList()) }
    var newCallerId by remember { mutableStateOf("") }
    var offerTarget by remember { mutableStateOf("") }
    var offerScope by remember { mutableStateOf("") }

    suspend fun reload() {
        runCatching { ApiClient.desk(deskId, viewerToken) }
            .onSuccess { card = it }
            .onFailure { error = it.message }
    }
    LaunchedEffect(deskId) { reload() }

    screenScroll {
        val c = card
        if (c != null && c.ageWall) {
            // Existence and nothing else: no name, no view, and no location,
            // because where a performer physically is has nothing to do with
            // watching them. Still never marked AI — a real person is here.
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(L10n.t("ndsk.adult", lang), color = Qrme.Txt, fontSize = 20.sp,
                    fontWeight = FontWeight.Bold)
                Text(c.note ?: "", color = Qrme.T2, fontSize = 12.sp)
                Text(L10n.t("ndsk.human", lang), color = Qrme.T3, fontSize = 11.sp)
            }
            return@screenScroll
        }
        Box(
            Modifier.fillMaxWidth().aspectRatio(4f / 3f)
                .clip(RoundedCornerShape(16.dp)).background(Qrme.Card),
        ) {
            if (c != null) {
            if (c?.feed != null) {
                AsyncImage(
                    model = ApiClient.base.trimEnd('/') + c.feed.url,
                    contentDescription = "The desk",
                    contentScale = ContentScale.Crop,
                    modifier = Modifier.fillMaxWidth().aspectRatio(4f / 3f))
            }
            }
            // The one label this image carries says whether it is live —
            // which is what somebody staring at an empty chair actually needs
            // to know. Never a watermark: it is a photograph of a real room.
            if (c?.feed != null) {
                Box(
                    Modifier.align(Alignment.BottomStart).padding(10.dp)
                        .clip(CircleShape)
                        .background(Color.Black.copy(alpha = 0.6f))
                        .padding(horizontal = 8.dp, vertical = 4.dp),
                ) {
                    Text(
                        L10n.t(if (c.feed.live) "ndsk.live" else "ndsk.sample", lang),
                        color = if (c.feed.live) Qrme.Red
                        else Color.White.copy(alpha = 0.85f),
                        fontSize = 11.sp, fontWeight = FontWeight.Bold)
                }
            }
        }

        if (c != null) {
            if (c.feed != null && !c.feed.live) {
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

            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Box(
                    Modifier.fillMaxWidth().clip(RoundedCornerShape(14.dp))
                        .background(Qrme.Card)
                        .clickable {
                            scope.launch {
                                runCatching {
                                    ApiClient.joinStream(deskId, viewerToken)
                                }.onSuccess { joined = it }
                                    .onFailure { error = it.message }
                            }
                        }
                        .padding(vertical = 14.dp),
                    Alignment.Center,
                ) {
                    Text(L10n.t(if (joined == null) "ndsk.join" else "ndsk.joined", lang),
                        color = Qrme.Txt, fontSize = 15.sp,
                        fontWeight = FontWeight.Bold)
                }
                joined?.let {
                    Text(it.note, color = Qrme.T2, fontSize = 12.sp)
                    Text(L10n.fill("ndsk.room", lang, mapOf("id" to it.roomId)),
                        color = Qrme.T3, fontSize = 10.sp)
                }
            }

            if (c.bellAvailable) {
                Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    labeledField(L10n.t("ndsk.note.ph", lang), note,
                        L10n.t("ndsk.needkey", lang)) { note = it }
                    Box(
                        Modifier.fillMaxWidth().clip(RoundedCornerShape(14.dp))
                            .background(Qrme.BrandA)
                            .clickable(enabled = !ringing) {
                                ringing = true; error = null
                                scope.launch {
                                    runCatching {
                                        ApiClient.ringBell(
                                            deskId, callerId,
                                            note.ifBlank { null }, viewerToken)
                                    }.onSuccess { receipt = it }
                                        .onFailure { error = it.message }
                                    ringing = false
                                    reload()
                                }
                            }
                            .padding(vertical = 14.dp),
                        Alignment.Center,
                    ) {
                        Text(L10n.t(if (ringing) "ndsk.ringing" else "ndsk.bell", lang),
                            color = Color.White, fontSize = 16.sp,
                            fontWeight = FontWeight.Bold)
                    }
                    val done = receipt
                    if (done != null) {
                        Text(done.note, color = Qrme.Green, fontSize = 12.sp)
                    } else if (c.waiting > 0) {
                        Text(L10n.fill("ndsk.waiting", lang, mapOf("n" to "${c.waiting}")),
                            color = Qrme.T3,
                            fontSize = 11.sp)
                    }
                }
            } else {
                Text(L10n.t("ndsk.bell.off", lang),
                    color = Qrme.T2, fontSize = 12.sp)
            }

            val att = c.attestation
            if (att != null) {
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Text(L10n.fill("ndsk.attested", lang, mapOf("attestor" to att.attestor)),
                    color = Qrme.Txt,
                    fontSize = 12.sp, fontWeight = FontWeight.Bold)
                Text(att.basis, color = Qrme.T2, fontSize = 11.sp)
                if (att.signed) {
                    Text("✓ " + L10n.t("ndsk.signed", lang), color = Qrme.Green, fontSize = 11.sp)
                }
                // Shipped with the claim, always: "recorded" and "proven" are
                // different words and the difference is the whole point.
                Text(att.note, color = Qrme.T3, fontSize = 10.sp)
            }
            }
        }


        // ---- your side of the counter -----------------------------------
        // Nothing a desk offers is connected until you say yes; the link
        // token comes to you alone, and any link — or the whole session —
        // ends the moment you want it back.
        if (callerId != null && viewerToken != null) {
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text(L10n.t("desk.counter", L10n.deviceLanguage()), color = Qrme.Txt,
                    fontSize = 14.sp, fontWeight = FontWeight.Bold)
                Text(L10n.t("desk.counter.show", L10n.deviceLanguage()), color = Qrme.Green, fontSize = 12.sp,
                    modifier = Modifier.clickable {
                        scope.launch {
                            runCatching {
                                ApiClient.myDeskSessions(callerId, viewerToken)
                            }.onSuccess { mySessions = it }
                                .onFailure { error = it.message }
                        }
                    })
                mySessions.forEach { session ->
                    Text("${session.deskName ?: session.deskId} · ${session.status}",
                        color = Qrme.T2, fontSize = 12.sp)
                    if (session.status == "open") {
                        Text(L10n.t("desk.counter.close_all", L10n.deviceLanguage()), color = Qrme.Red, fontSize = 11.sp,
                            modifier = Modifier.clickable {
                                scope.launch {
                                    runCatching {
                                        ApiClient.closeDeskSession(session.id,
                                            viewerToken)
                                    }.onFailure { error = it.message }
                                    runCatching {
                                        ApiClient.myDeskSessions(callerId,
                                            viewerToken)
                                    }.onSuccess { mySessions = it }
                                }
                            })
                    }
                    session.connections.forEach { link ->
                        Text("${link.kind} · ${link.target} · ${link.status}",
                            color = Qrme.Txt, fontSize = 11.sp)
                        link.means?.let {
                            Text(it, color = Qrme.T3, fontSize = 10.sp)
                        }
                        if (link.status == "offered") {
                            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                                Text(L10n.t("desk.counter.connect", L10n.deviceLanguage()), color = Qrme.Green,
                                    fontSize = 11.sp,
                                    modifier = Modifier.clickable {
                                        scope.launch {
                                            runCatching {
                                                ApiClient.answerDeskConnection(
                                                    link.sessionId, link.id,
                                                    true, viewerToken)
                                            }.onFailure { error = it.message }
                                            runCatching {
                                                ApiClient.deskSession(
                                                    link.sessionId, viewerToken)
                                            }.onSuccess { fresh ->
                                                mySessions = mySessions.map {
                                                    if (it.id == fresh.id) fresh
                                                    else it
                                                }
                                            }
                                        }
                                    })
                                Text(L10n.t("desk.counter.decline", L10n.deviceLanguage()), color = Qrme.Red, fontSize = 11.sp,
                                    modifier = Modifier.clickable {
                                        scope.launch {
                                            runCatching {
                                                ApiClient.answerDeskConnection(
                                                    link.sessionId, link.id,
                                                    false, viewerToken)
                                            }.onFailure { error = it.message }
                                        }
                                    })
                            }
                        }
                        if (link.status == "active") {
                            link.token?.let {
                                Text(it, color = Qrme.T3, fontSize = 10.sp)
                            }
                            Text(L10n.t("desk.counter.end", L10n.deviceLanguage()), color = Qrme.Red,
                                fontSize = 11.sp,
                                modifier = Modifier.clickable {
                                    scope.launch {
                                        runCatching {
                                            ApiClient.endDeskConnection(
                                                link.sessionId, link.id,
                                                viewerToken)
                                        }.onFailure { error = it.message }
                                    }
                                })
                        }
                    }
                }
            }
        }

        // ---- staffing the counter ---------------------------------------
        // Holding the desk token is what makes you the desk. The offer
        // grants nothing; the caller's accept does.
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Text(L10n.t("desk.counter.staff", L10n.deviceLanguage()), color = Qrme.Txt, fontSize = 14.sp,
                fontWeight = FontWeight.Bold)
            labeledField(L10n.t("desk.counter.staff.token", L10n.deviceLanguage()), deskToken, L10n.t("ndsk.id.ph", lang)) { deskToken = it }
            if (deskToken.isNotBlank()) {
                labeledField(L10n.t("desk.counter.staff.caller", L10n.deviceLanguage()), newCallerId, L10n.t("ndsk.caller.ph", lang)) { newCallerId = it }
                Text(L10n.t("desk.counter.staff.open", L10n.deviceLanguage()), color = Qrme.Green, fontSize = 12.sp,
                    modifier = Modifier.clickable {
                        scope.launch {
                            runCatching {
                                ApiClient.openDeskSession(deskId, newCallerId,
                                    deskToken)
                            }.onFailure { error = it.message }
                            runCatching {
                                ApiClient.deskSessions(deskId, deskToken)
                            }.onSuccess { staffSessions = it }
                        }
                    })
                staffSessions.forEach { session ->
                    Text("${session.callerId} · ${session.status}",
                        color = Qrme.T2, fontSize = 12.sp)
                    if (session.status == "open") {
                        labeledField(L10n.t("desk.counter.staff.target", L10n.deviceLanguage()), offerTarget, L10n.t("ndsk.computer.ph", lang)) { offerTarget = it }
                        labeledField(L10n.t("desk.counter.staff.scope", L10n.deviceLanguage()), offerScope,
                            L10n.t("ndsk.program.ph", lang)) { offerScope = it }
                        Text(L10n.t("desk.counter.staff.offer", L10n.deviceLanguage()), color = Qrme.Green,
                            fontSize = 11.sp,
                            modifier = Modifier.clickable {
                                scope.launch {
                                    runCatching {
                                        ApiClient.offerDeskConnection(
                                            session.id, "screen_share",
                                            offerTarget,
                                            offerScope.ifBlank { null },
                                            deskToken)
                                    }.onFailure { error = it.message }
                                }
                            })
                    }
                }
            }
        }

        error?.let { Text(it, color = Qrme.Red, fontSize = 13.sp) }
    }
}
