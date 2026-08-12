package app.qrme.studio.ui

import androidx.compose.foundation.background
import app.qrme.studio.MainActivity
import app.qrme.studio.Problems
import org.json.JSONObject
import org.json.JSONArray
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.material3.pulltorefresh.PullToRefreshBox
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalUriHandler
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import app.qrme.studio.AccessReportRow
import app.qrme.studio.ApiClient
import app.qrme.studio.AudienceCounts
import app.qrme.studio.CommentRow
import app.qrme.studio.DeskBeacon
import app.qrme.studio.DeskBrief
import app.qrme.studio.DeskGuest
import app.qrme.studio.DeskOpened
import app.qrme.studio.DeskOverlay
import app.qrme.studio.DeskRing
import app.qrme.studio.DmMessage
import app.qrme.studio.DmThread
import app.qrme.studio.ExchangeDeal
import app.qrme.studio.ExchangeVocabulary
import app.qrme.studio.FeedCard
import app.qrme.studio.FriendRow
import app.qrme.studio.GiftRow
import app.qrme.studio.GrantCard
import app.qrme.studio.GrantUse
import app.qrme.studio.InboxPage
import app.qrme.studio.MarketCard
import app.qrme.studio.MarketHit
import app.qrme.studio.MarketOffer
import app.qrme.studio.MarketSale
import app.qrme.studio.PartyCard
import app.qrme.studio.PartyLine
import app.qrme.studio.ProfileAttention
import app.qrme.studio.ShopCard
import app.qrme.studio.ShopDetail
import app.qrme.studio.ShopOrder
import app.qrme.studio.Solitude
import app.qrme.studio.SolitudeReferral
import app.qrme.studio.SuggestedRow
import app.qrme.studio.WallPost
import app.qrme.studio.AppConn
import app.qrme.studio.L10n
import app.qrme.studio.Beacon
import app.qrme.studio.CatalogApp
import app.qrme.studio.ConnMsg
import app.qrme.studio.EarningsStatement
import app.qrme.studio.Excursion
import app.qrme.studio.FeedbackState
import app.qrme.studio.PayoutReceipt
import app.qrme.studio.SteeringHubState
import app.qrme.studio.GameCalloutResult
import app.qrme.studio.GameSession
import app.qrme.studio.InstalledPack
import app.qrme.studio.LanguageInfo
import app.qrme.studio.LicenseGrant
import app.qrme.studio.LicenseOffer
import app.qrme.studio.Listing
import app.qrme.studio.Objection
import app.qrme.studio.ObjectionOpened
import app.qrme.studio.ObjectionTimeline
import app.qrme.studio.Pack
import app.qrme.studio.PackRegistry
import app.qrme.studio.Post
import app.qrme.studio.ProfileCard
import app.qrme.studio.Provenance
import app.qrme.studio.ProviderInfo
import app.qrme.studio.Robot
import app.qrme.studio.RobotSpec
import app.qrme.studio.RoomCreated
import app.qrme.studio.RoomMsg
import app.qrme.studio.SocialConn
import app.qrme.studio.StudioViewModel
import app.qrme.studio.SummonResult
import app.qrme.studio.TranslateResult
import app.qrme.studio.WatermarkRecovery
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.platform.LocalContext
import app.qrme.studio.SignatureReceipt
import app.qrme.studio.Signing
import app.qrme.studio.SigningCredential
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

@Composable
internal fun screenScroll(content: @Composable ColumnScope.() -> Unit) =
    Column(
        Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
        content = content,
    )

@Composable
private fun BrandButton(text: String, enabled: Boolean = true, busy: Boolean = false, onClick: () -> Unit) {
    Box(
        Modifier.fillMaxWidth().clip(RoundedCornerShape(13.dp))
            .background(Qrme.Card.copy(alpha = 0.4f))
            .then(if (enabled) Modifier.background(Qrme.Brand) else Modifier)
            .clickable(enabled = enabled && !busy) { onClick() }
            .padding(vertical = 14.dp),
        contentAlignment = Alignment.Center,
    ) {
        if (busy) CircularProgressIndicator(color = Color.White, strokeWidth = 2.dp, modifier = Modifier.size(20.dp))
        else Text(text, color = Color.White, fontWeight = FontWeight.Bold)
    }
}

@Composable
internal fun labeledField(label: String, value: String, placeholder: String, onChange: (String) -> Unit) {
    Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
        Text(label, color = Qrme.T2, fontSize = 12.sp)
        OutlinedTextField(
            value = value, onValueChange = onChange,
            placeholder = { Text(placeholder, color = Qrme.T3) },
            modifier = Modifier.fillMaxWidth(),
            colors = OutlinedTextFieldDefaults.colors(
                focusedTextColor = Qrme.Txt, unfocusedTextColor = Qrme.Txt,
                focusedBorderColor = Qrme.BrandA, unfocusedBorderColor = Qrme.Line,
                focusedContainerColor = Qrme.ScrBot, unfocusedContainerColor = Qrme.ScrBot,
            ),
        )
    }
}

// ---- Welcome / create profile ----

@Composable
fun WelcomeScreen(vm: StudioViewModel) {
    // Not everybody who opens this app wants a profile. Some are here
    // *because* of one — see WithoutAnAccountScreen below.
    var publicDoor by remember { mutableStateOf(false) }
    if (publicDoor) { WithoutAnAccountScreen(vm) { publicDoor = false }; return }

    // The reader of this screen has no profile, so there is no profile
    // language to read — the same case `WithoutAnAccountScreen` below already
    // resolves this way, and `vm.language` is "en" until a profile exists.
    val lang = L10n.deviceLanguage()
    var name by remember { mutableStateOf("") }
    var languages by remember { mutableStateOf<List<LanguageInfo>>(emptyList()) }
    var language by remember { mutableStateOf("en") }
    LaunchedEffect(Unit) {
        runCatching { ApiClient.languages() }.onSuccess { languages = it }
    }
    var persona by remember { mutableStateOf("") }
    var kind by remember { mutableStateOf("self") }
    var birthdate by remember { mutableStateOf("1984-01-01") }
    var busy by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    val kinds = listOf("self", "other_person", "fictional")

    Box(Modifier.fillMaxSize().background(Qrme.Bg)) {
        screenScroll {
            Spacer(Modifier.height(28.dp))
            Box(Modifier.align(Alignment.CenterHorizontally).size(84.dp).clip(CircleShape).background(Qrme.Brand),
                contentAlignment = Alignment.Center) {
                Text("✦", fontSize = 34.sp, color = Color.White)
            }
            Text(L10n.t("nw.title", lang), color = Qrme.Txt, fontSize = 22.sp,
                fontWeight = FontWeight.Bold, modifier = Modifier.align(Alignment.CenterHorizontally))
            Text(L10n.t("nw.sub", lang),
                color = Qrme.T2, fontSize = 13.sp, modifier = Modifier.align(Alignment.CenterHorizontally))

            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                labeledField(L10n.t("nw.name", lang), name, L10n.t("nw.name.ph", lang)) { name = it }
                labeledField(L10n.t("nw.persona", lang), persona, L10n.t("nw.persona.ph", lang)) { persona = it }
                Text(L10n.t("nw.kind", lang), color = Qrme.T2, fontSize = 12.sp)
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    kinds.forEach { k ->
                        FilterChip(
                            selected = kind == k, onClick = { kind = k },
                            // `k.replace('_', ' ')` rendered the API's enum
                            // member as if it were a word nobody wrote.
                            label = { Text(L10n.t(kindKey(k), lang), fontSize = 12.sp) },
                            colors = FilterChipDefaults.filterChipColors(
                                selectedContainerColor = Qrme.BrandA,
                                selectedLabelColor = Color.White,
                                labelColor = Qrme.T2,
                            ),
                        )
                    }
                }
                labeledField(L10n.t("nw.birthdate", lang), birthdate, L10n.t("nw.birthdate.ph", lang)) { birthdate = it }
                if (languages.isNotEmpty()) {
                    Text(L10n.t("nw.language", lang), color = Qrme.T2, fontSize = 12.sp)
                    languages.chunked(3).forEach { row ->
                        Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                            row.forEach { l ->
                                FilterChip(
                                    selected = language == l.code,
                                    onClick = { language = l.code },
                                    label = { Text(l.label, fontSize = 11.sp) },
                                    colors = FilterChipDefaults.filterChipColors(
                                        selectedContainerColor = Qrme.BrandA,
                                        selectedLabelColor = Color.White, labelColor = Qrme.T2,
                                    ),
                                )
                            }
                        }
                    }
                }
            }
            error?.let { Text(it, color = Qrme.Red, fontSize = 13.sp) }
            BrandButton(L10n.t("nw.create", lang), enabled = name.isNotBlank() && persona.isNotBlank(), busy = busy) {
                error = null
                vm.createProfile(name, persona, kind, birthdate, language,
                    onError = { error = it }, onBusy = { busy = it })
            }
            // Consent to terms, in the reader's language. Built by `+` before
            // this round, which is a sentence no table could ever hold.
            Text(L10n.t("nw.terms", lang), color = Qrme.T3, fontSize = 9.sp)
            // The other reason somebody opens this app: they have found a
            // synthetic profile of themselves, or were sent something and
            // want to know whether a person wrote it. Both routes are public
            // on the backend and both sat behind the sign-in gate.
            Text(L10n.t("pub.invite", lang), color = Qrme.T2, fontSize = 13.sp)
            TextButton(onClick = { publicDoor = true }) {
                Text(L10n.t("nw.door", lang),
                    color = Qrme.BrandA, fontSize = 13.sp)
            }
            Text(L10n.t("pub.invite.none", lang), color = Qrme.T3, fontSize = 11.sp)

            Text(L10n.fill("nov.backend", lang,
                    mapOf("command" to "QRME_CORS_ORIGINS=* uvicorn qrme.api:app")),
                color = Qrme.T3, fontSize = 10.sp)
        }
    }
}

/** `self` / `other_person` / `fictional` are the API's members; these are the
 *  words a person reads for them. */
private fun kindKey(kind: String) =
    if (kind == "other_person") "nw.kind.other" else "nw.kind.$kind"

// ---- Without an account ----

/**
 * The two things this app lets a stranger do, on the one screen a stranger
 * can reach.
 *
 * `MainActivity` renders `WelcomeScreen` unless `vm.isSignedIn`, so
 * `openObjection` — wired into the settings screen one release ago precisely
 * because a phone is the surface an objector reaches for — sat inside a
 * signed-in tab, past a profile the objector does not have.
 *
 * `ApiClient.recoverWatermark` says it in its own comment: *"Public: a
 * counterparty must be able to ask without an account here."* It was written
 * beside a call site that required one.
 *
 * Nothing here passes a token, and nothing here is the owner's half: listing
 * objections against your own profile and attesting to them stays where the
 * credential is.
 */
@Composable
fun WithoutAnAccountScreen(vm: StudioViewModel, onBack: () -> Unit) {
    // The reader of this screen has no profile, so there is no profile
    // language to read. Resolved once here rather than at twenty call sites,
    // where one of them would eventually be the profile's setting.
    val lang = L10n.deviceLanguage()
    var pane by remember { mutableIntStateOf(0) }
    var profileId by remember { mutableStateOf("") }
    var objectorRef by remember { mutableStateOf("") }
    var reason by remember { mutableStateOf("") }
    var opened by remember { mutableStateOf<ObjectionOpened?>(null) }
    var timeline by remember { mutableStateOf<ObjectionTimeline?>(null) }
    var content by remember { mutableStateOf("") }
    var found by remember { mutableStateOf<WatermarkRecovery?>(null) }
    var countId by remember { mutableStateOf("") }
    var counted by remember { mutableStateOf<ProfileAttention?>(null) }
    var busy by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }

    Box(Modifier.fillMaxSize().background(Qrme.Bg)) {
        screenScroll {
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text(L10n.t("pub.sub", lang), color = Qrme.Txt, fontSize = 20.sp,
                    fontWeight = FontWeight.Bold)
                TextButton(onClick = onBack) {
                    Text(L10n.t("pub.back.short", lang), color = Qrme.BrandA,
                        fontSize = 13.sp) }
            }
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                listOf(L10n.t("pub.object.title", lang),
                       L10n.t("pub.tab.mark", lang),
                       L10n.t("pub.count.title", lang))
                    .forEachIndexed { i, label ->
                        FilterChip(
                            selected = pane == i, onClick = { pane = i },
                            label = { Text(label, fontSize = 12.sp) },
                            colors = FilterChipDefaults.filterChipColors(
                                selectedContainerColor = Qrme.BrandA,
                                selectedLabelColor = Color.White, labelColor = Qrme.T2,
                            ),
                        )
                    }
            }

            if (pane == 0) {
                Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Text(L10n.t("pub.object.restricts", lang),
                        color = Qrme.T2, fontSize = 12.sp)
                    labeledField(L10n.t("pub.object.profileId", lang), profileId,
                                 L10n.t("nw.profile.ph", lang)) { profileId = it }
                    labeledField(L10n.t("pub.object.ref", lang), objectorRef,
                                 L10n.t("pub.object.ref.ph", lang)) { objectorRef = it }
                    labeledField(L10n.t("pub.object.reason", lang), reason, "") { reason = it }
                    Text(L10n.t("pub.object.ref.note", lang),
                        color = Qrme.T3, fontSize = 11.sp)
                    BrandButton(L10n.t("pub.object.open", lang),
                        enabled = profileId.isNotBlank() && objectorRef.isNotBlank(),
                        busy = busy) {
                        busy = true; error = null
                        vm.call({ ApiClient.openObjection(profileId.trim(),
                                                          objectorRef.trim(), reason) }) { r ->
                            busy = false
                            r.onSuccess { opened = it }.onFailure { error = it.message }
                        }
                    }
                }
                opened?.let { o ->
                    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        Text(L10n.fill("pub.object.opened", lang, mapOf("id" to o.id)),
                            color = Qrme.Txt, fontSize = 15.sp,
                            fontWeight = FontWeight.Bold)
                        Text(o.note, color = Qrme.T2, fontSize = 12.sp)
                        Text(L10n.fill("pub.object.opened.status", lang, mapOf(
                                "now" to L10n.t("pub.state.${o.profileStatus}", lang),
                                "before" to L10n.t("pub.state.${o.priorStatus}", lang))),
                            color = Qrme.T2, fontSize = 12.sp)
                        Text(L10n.t("pub.object.writeitdown", lang),
                            color = Qrme.T3, fontSize = 11.sp)
                    }
                    // The record of their own case. Until this release the
                    // objector could end the profile from this very screen and
                    // could not read what had happened to it: `/audit` is
                    // owner- or reviewer-gated, and they are neither.
                    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        Text(L10n.t("obj.timeline.title", lang), color = Qrme.Txt,
                            fontSize = 15.sp, fontWeight = FontWeight.Bold)
                        val tl = timeline
                        if (tl == null) {
                            BrandButton(L10n.t("obj.timeline.go", lang), busy = busy) {
                                busy = true; error = null
                                vm.call({ ApiClient.objectionTimeline(o.id) }) { r ->
                                    busy = false
                                    r.onSuccess { timeline = it }
                                     .onFailure { error = it.message }
                                }
                            }
                        } else {
                            Text(tl.note, color = Qrme.T2, fontSize = 12.sp)
                            if (tl.events.isEmpty()) {
                                Text(L10n.t("obj.timeline.empty", lang),
                                    color = Qrme.T3, fontSize = 11.sp)
                            }
                            tl.events.forEach { e ->
                                val seal = if (e.sealed)
                                    " \u00b7 " + L10n.t("obj.timeline.sealed", lang) else ""
                                Text(L10n.t("obj.event.${e.event}", lang) + " \u00b7 " +
                                     L10n.t("obj.actor.${e.actor}", lang) + " \u00b7 " +
                                     e.at + seal,
                                    color = Qrme.T2, fontSize = 11.sp)
                            }
                        }
                    }
                }
            } else if (pane == 1) {
                Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Text(L10n.t("pub.mark.explain", lang),
                        color = Qrme.T2, fontSize = 12.sp)
                    labeledField(L10n.t("pub.mark.paste", lang), content, "") { content = it }
                    BrandButton(L10n.t("pub.mark.ask", lang), enabled = content.isNotBlank(),
                                busy = busy) {
                        busy = true; error = null; found = null
                        vm.call({ ApiClient.recoverWatermark(content) }) { r ->
                            busy = false
                            r.onSuccess { found = it }.onFailure { error = it.message }
                        }
                    }
                }
                found?.let { f ->
                    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        if (f.recovered) {
                            Text(L10n.fill("pub.mark.producedby", lang,
                                    mapOf("state" to (f.state ?: ""))),
                                color = Qrme.Txt, fontSize = 15.sp,
                                fontWeight = FontWeight.Bold)
                            Text(L10n.fill("pub.mark.windows", lang, mapOf(
                                    "matched" to f.matchedWindows.toString(),
                                    "stored" to f.storedWindows.toString(),
                                    "examined" to f.examinedWindows.toString(),
                                    "similarity" to f.similarity.toString())),
                                color = Qrme.T3, fontSize = 11.sp)
                            if (!f.verbatim) {
                                Text(L10n.t("pub.mark.altered", lang),
                                    color = Qrme.T3, fontSize = 11.sp)
                            }
                        } else {
                            Text(L10n.t("pub.mark.unknown", lang), color = Qrme.Txt,
                                fontSize = 15.sp, fontWeight = FontWeight.Bold)
                            f.reason?.let { Text(it, color = Qrme.T2, fontSize = 12.sp) }
                            Text(L10n.fill("pub.mark.unknown.explain", lang,
                                    mapOf("here" to L10n.t("pub.mark.here", lang))),
                                color = Qrme.T3, fontSize = 11.sp)
                        }
                    }
                }
            } else {
                // How many people is this thing talking to. Here rather than
                // behind sign-in: making somebody get an account before they
                // may learn the number is the same withholding with a form in
                // front of it, and the withholding is the whole harm.
                Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    labeledField(L10n.t("pub.count.id", lang), countId,
                                 L10n.t("nw.profile.ph", lang)) { countId = it }
                    BrandButton(L10n.t("pub.count.ask", lang),
                                enabled = countId.isNotBlank(), busy = busy) {
                        busy = true; error = null; counted = null
                        vm.call({ ApiClient.profileAttention(countId.trim()) }) { r ->
                            busy = false
                            r.onSuccess { counted = it }.onFailure { error = it.message }
                        }
                    }
                }
                counted?.let { c ->
                    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        Row {
                            Text("" + c.peopleThisWeek + " \u00b7 "
                                    + L10n.t("pub.count.week", lang),
                                color = Qrme.Txt, fontSize = 15.sp,
                                fontWeight = FontWeight.Bold,
                                modifier = Modifier.weight(1f))
                            Text("" + c.peopleEver + " \u00b7 "
                                    + L10n.t("pub.count.ever", lang),
                                color = Qrme.T3, fontSize = 11.sp)
                        }
                        Text(c.says, color = Qrme.Txt, fontSize = 12.sp)
                        Text(c.note, color = Qrme.T3, fontSize = 11.sp)
                    }
                }
            }

            error?.let { Text(it, color = Qrme.Red, fontSize = 13.sp) }
            Text(L10n.t("pub.notoken", lang), color = Qrme.T3, fontSize = 10.sp)
        }
    }
}

// ---- Overview ----

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun OverviewScreen(vm: StudioViewModel) {
    var card by remember { mutableStateOf<ProfileCard?>(null) }
    var loaded by remember { mutableStateOf(false) }
    var refreshing by remember { mutableStateOf(false) }
    fun reload() {
        vm.call({ ApiClient.profile(vm.pid!!) }) { r ->
            card = r.getOrNull(); loaded = true; refreshing = false
        }
    }
    LaunchedEffect(Unit) { reload() }
    PullToRefreshBox(isRefreshing = refreshing,
        onRefresh = { refreshing = true; reload() }) {
    screenScroll {
        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Box(Modifier.size(8.dp).clip(CircleShape).background(Qrme.Green))
            Text(L10n.t("nov.live", vm.language), color = Qrme.Green, fontSize = 12.sp, fontWeight = FontWeight.Bold)
        }
        Text(vm.displayName, color = Qrme.Txt, fontSize = 28.sp, fontWeight = FontWeight.Bold)
        Text(L10n.t("nov.sub", vm.language), color = Qrme.T2, fontSize = 14.sp)

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text(L10n.t("nov", vm.language), color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            when {
                !loaded -> CircularProgressIndicator(color = Qrme.BrandA, modifier = Modifier.size(22.dp))
                card == null -> Text(L10n.t("nov.error", vm.language),
                    color = Qrme.T2, fontSize = 13.sp)
                else -> {
                    cardRow(L10n.t("nw.kind", vm.language), card!!.kind.replace('_', ' '))
                    cardRow(L10n.t("life.status", vm.language), card!!.status ?: "active")
                    cardRow(L10n.t("nov.id", vm.language), card!!.id)
                }
            }
        }
        OutlinedButton(onClick = { vm.signOut() }, modifier = Modifier.fillMaxWidth(),
            border = androidx.compose.foundation.BorderStroke(1.dp, Qrme.Line)) {
            Text(L10n.t("action.sign_out", vm.language), color = Qrme.T2)
        }
    }
    }
}

@Composable
private fun cardRow(k: String, v: String) {
    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
        Text(k, color = Qrme.Txt, fontSize = 14.sp)
        Text(v, color = Qrme.T2, fontSize = 14.sp)
    }
}

// ---- Compose ----

@Composable
fun ComposeScreen(vm: StudioViewModel) {
    var topic by remember { mutableStateOf("") }
    var busy by remember { mutableStateOf(false) }
    var result by remember { mutableStateOf<Post?>(null) }

    screenScroll {
        Text(L10n.t("tab.compose", vm.language), color = Qrme.Txt, fontSize = 22.sp, fontWeight = FontWeight.Bold)
        Text(L10n.t("ncmp.sub", vm.language), color = Qrme.T2, fontSize = 13.sp)
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            labeledField(L10n.t("nc.topic.ph", vm.language), topic, L10n.t("ncmp.topic.ph", vm.language)) { topic = it }
        }
        BrandButton(L10n.t("ncmp", vm.language), enabled = topic.isNotBlank(), busy = busy) {
            busy = true
            vm.call({ ApiClient.compose(vm.pid!!, vm.token!!, topic) }) {
                result = it.getOrNull(); busy = false
            }
        }
        result?.let { p ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Box(Modifier.size(9.dp).clip(CircleShape)
                        .background(if (p.status == "published") Qrme.Green else Qrme.Amber))
                    Text((p.status ?: "draft").replaceFirstChar { it.uppercase() },
                        color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
                }
                HorizontalDivider(color = Qrme.Line)
                Text(p.content ?: "· held for review ·", color = Qrme.Txt, fontSize = 14.sp)
                Text(p.watermarkLine ?: "✦ AI", color = Qrme.T3, fontSize = 10.sp)
                p.provenance?.let { ProvenanceFooter(it, vm.language) }
            }
        }
    }
}

// ---- Posts ----

@Composable
fun PostsScreen(vm: StudioViewModel) {
    var posts by remember { mutableStateOf<List<Post>?>(null) }
    LaunchedEffect(Unit) {
        vm.call({ ApiClient.posts(vm.pid!!) }) { r -> posts = r.getOrDefault(emptyList()) }
    }
    screenScroll {
        Text(L10n.t("tab.posts", vm.language), color = Qrme.Txt, fontSize = 22.sp, fontWeight = FontWeight.Bold)
        Text(L10n.t("npst.sub", vm.language), color = Qrme.T2, fontSize = 13.sp)
        when {
            posts == null -> CircularProgressIndicator(color = Qrme.BrandA, modifier = Modifier.size(22.dp))
            posts!!.isEmpty() -> Column(Modifier.card()) {
                Text(L10n.t("npst.none", vm.language), color = Qrme.T2, fontSize = 13.sp)
            }
            else -> posts!!.forEach { p ->
                Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        Box(Modifier.size(8.dp).clip(CircleShape)
                            .background(if (p.status == "published") Qrme.Green else Qrme.Amber))
                        Text((p.status ?: "draft").replaceFirstChar { it.uppercase() },
                            color = if (p.status == "published") Qrme.Green else Qrme.Amber,
                            fontSize = 12.sp, fontWeight = FontWeight.Bold)
                    }
                    Text(p.content ?: "· held for review ·", color = Qrme.Txt, fontSize = 14.sp)
                    Text(p.watermarkLine ?: "✦ AI", color = Qrme.T3, fontSize = 10.sp)
                }
            }
        }
        // The wall's posts, and beneath them the public stream those posts
        // feed into — the same rows, ranked for nobody.
        StreamSection(vm)
    }
}

// ---- the public stream ----

/**
 * The stream, one card at a time.
 *
 * `plays` is read from the server and never recomputed: only footage this
 * deployment holds comes back true, so scrolling past an off-site card makes
 * no request to another company's server. `entering` and `ringing` are shown
 * *before* their buttons, because a live room and a desk reach a person.
 */
@Composable
fun StreamSection(vm: StudioViewModel) {
    var cards by remember { mutableStateOf<List<FeedCard>>(emptyList()) }
    var cursor by remember { mutableStateOf<String?>(null) }
    var at by remember { mutableStateOf(0) }
    var opened by remember { mutableStateOf<Set<String>>(emptySet()) }
    var line by remember { mutableStateOf<String?>(null) }
    LaunchedEffect(Unit) {
        vm.call({ ApiClient.publicFeed() }) { r ->
            r.getOrNull()?.let { cards = it.items; cursor = it.cursor }
        }
    }
    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Text(L10n.t("feed.title", vm.language), color = Qrme.Txt, fontSize = 18.sp, fontWeight = FontWeight.Bold)
        Text(L10n.t("feed.sub", vm.language), color = Qrme.T2, fontSize = 13.sp)
        if (cards.isEmpty()) {
            Column(Modifier.card()) {
                Text(L10n.t("feed.empty", vm.language), color = Qrme.T2, fontSize = 13.sp)
            }
        } else {
            val c = cards[at.coerceIn(0, cards.size - 1)]
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                // Spelled out: a key built at runtime is invisible to the
                // guard that checks every asked-for key exists.
                val kindLabel = when (c.kind) {
                    "video" -> L10n.t("feed.kind.video", vm.language)
                    "offsite" -> L10n.t("feed.kind.offsite", vm.language)
                    "room" -> L10n.t("feed.kind.room", vm.language)
                    else -> L10n.t("feed.kind.desk", vm.language)
                }
                Text(kindLabel, color = Qrme.BrandA,
                    fontSize = 12.sp, fontWeight = FontWeight.Bold)
                Text(c.reason, color = Qrme.T3, fontSize = 10.sp)
                when (c.kind) {
                    "offsite" -> {
                        Text(c.title ?: "—", color = Qrme.Txt, fontSize = 14.sp)
                        Text(c.platformName ?: "—", color = Qrme.T2, fontSize = 12.sp)
                        // Nothing is requested until this press.
                        if (!opened.contains(c.id)) {
                            TextButton(onClick = { opened = opened + c.id; line = c.url }) {
                                Text(L10n.t("feed.play", vm.language), color = Qrme.BrandA, fontSize = 12.sp)
                            }
                        }
                        Text(c.note ?: "", color = Qrme.T3, fontSize = 10.sp)
                    }
                    "room" -> {
                        Text(c.topic ?: L10n.t("feed.room.untitled", vm.language),
                            color = Qrme.Txt, fontSize = 14.sp)
                        Text(c.entering ?: "", color = Qrme.T3, fontSize = 10.sp)
                        TextButton(onClick = { line = c.entering }) {
                            Text(L10n.t("feed.enter", vm.language), color = Qrme.BrandA, fontSize = 12.sp)
                        }
                    }
                    "desk" -> {
                        Text(c.displayName ?: "—", color = Qrme.Txt, fontSize = 14.sp)
                        Text((c.trade ?: "") + " · " + (c.presence ?: ""), color = Qrme.T2, fontSize = 12.sp)
                        Text(c.ringing ?: "", color = Qrme.T3, fontSize = 10.sp)
                        TextButton(onClick = { line = c.ringing }) {
                            Text(L10n.t("feed.ring", vm.language), color = Qrme.BrandA, fontSize = 12.sp)
                        }
                    }
                    else -> {
                        Text(c.title ?: "—", color = Qrme.Txt, fontSize = 14.sp)
                        Text(c.note ?: "", color = Qrme.T3, fontSize = 10.sp)
                    }
                }
            }
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                TextButton(onClick = { at = (at - 1).coerceAtLeast(0) }) {
                    Text(L10n.t("feed.back", vm.language), color = Qrme.T2, fontSize = 12.sp)
                }
                TextButton(onClick = {
                    at = (at + 1).coerceAtMost(cards.size - 1)
                    val more = cursor
                    if (more != null && at >= cards.size - 2) {
                        vm.call({ ApiClient.publicFeed(more) }) { r ->
                            r.getOrNull()?.let { cards = cards + it.items; cursor = it.cursor }
                        }
                    }
                }) {
                    Text(L10n.t("feed.next", vm.language), color = Qrme.BrandA, fontSize = 12.sp)
                }
            }
        }
        // A link somebody was sent, opened by the same rules as the stream.
        var itemId by remember { mutableStateOf("") }
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            OutlinedTextField(value = itemId, onValueChange = { itemId = it },
                singleLine = true)
            TextButton(onClick = {
                vm.call({ ApiClient.feedItem(itemId) }) { r ->
                    line = r.getOrNull()?.let { (it.title ?: it.displayName ?: it.id) }
                }
            }) {
                Text(L10n.t("feed.play", vm.language), color = Qrme.BrandA, fontSize = 12.sp)
            }
            line?.let { Text(it, color = Qrme.T3, fontSize = 10.sp) }
        }
    }
}

// ---- Robots (robotic embodiment) ----

@Composable
fun RobotsScreen(vm: StudioViewModel) {
    var catalog by remember { mutableStateOf<List<RobotSpec>>(emptyList()) }
    var chosen by remember { mutableStateOf("neo") }
    var robots by remember { mutableStateOf<List<Robot>>(emptyList()) }
    var topic by remember { mutableStateOf("") }
    var lastResult by remember { mutableStateOf<String?>(null) }
    var busy by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }

    fun reload() {
        vm.call({ ApiClient.robots(vm.pid!!, vm.token!!) }) { r -> robots = r.getOrDefault(emptyList()) }
    }
    LaunchedEffect(Unit) {
        vm.call({ ApiClient.roboticsCatalog() }) { r -> catalog = r.getOrDefault(emptyList()) }
        reload()
    }

    fun command(rob: Robot, cmd: String, arg: String?) {
        error = null
        vm.call({ ApiClient.commandRobot(rob.id, vm.token!!, cmd, arg) }) { r ->
            r.onSuccess { lastResult = it.spoken ?: "${it.command}: ${it.status}" }
             .onFailure { error = it.message }
            reload()
        }
    }

    screenScroll {
        Text(L10n.t("tab.robots", vm.language), color = Qrme.Txt, fontSize = 22.sp, fontWeight = FontWeight.Bold)
        Text(L10n.t("nrob.sub", vm.language),
            color = Qrme.T2, fontSize = 13.sp)

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("nrob.bind", vm.language), color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            catalog.chunked(2).forEach { row ->
                Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                    row.forEach { s ->
                        FilterChip(
                            selected = chosen == s.model, onClick = { chosen = s.model },
                            label = { Text(s.label, fontSize = 11.sp) },
                            colors = FilterChipDefaults.filterChipColors(
                                selectedContainerColor = Qrme.BrandA,
                                selectedLabelColor = Color.White, labelColor = Qrme.T2,
                            ),
                        )
                    }
                }
            }
            BrandButton(L10n.t("nrob.bind.go", vm.language), enabled = catalog.isNotEmpty(), busy = busy) {
                busy = true; error = null
                vm.call({ ApiClient.bindRobot(vm.pid!!, vm.token!!, chosen) }) { r ->
                    busy = false
                    r.onFailure { error = it.message }
                    reload()
                }
            }
        }
        error?.let { Text(it, color = Qrme.Red, fontSize = 13.sp) }

        if (robots.isNotEmpty()) {
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                labeledField(L10n.t("nrob.topic", vm.language), topic, L10n.t("nrob.topic.ph", vm.language)) { topic = it }
            }
        }

        robots.forEach { rob ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text(rob.name, color = Qrme.Txt, fontSize = 14.sp, fontWeight = FontWeight.Bold)
                    Text((rob.status ?: "docked").replaceFirstChar { it.uppercase() },
                        color = Qrme.T2, fontSize = 12.sp)
                }
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    if ("say" in rob.commands)
                        TextButton(onClick = { command(rob, "say", topic) }) {
                            Text(L10n.t("nrob.say", vm.language), color = Qrme.BrandA, fontSize = 13.sp) }
                    if ("clean" in rob.commands)
                        TextButton(onClick = { command(rob, "clean", null) }) {
                            Text(L10n.t("nrob.clean", vm.language), color = Qrme.BrandA, fontSize = 13.sp) }
                    if ("patrol" in rob.commands)
                        TextButton(onClick = { command(rob, "patrol", null) }) {
                            Text(L10n.t("nrob.patrol", vm.language), color = Qrme.BrandA, fontSize = 13.sp) }
                    TextButton(onClick = { command(rob, "dock", null) }) {
                        Text(L10n.t("nrob.dock", vm.language), color = Qrme.T2, fontSize = 13.sp) }
                }
            }
        }

        lastResult?.let { res ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text(L10n.t("nrob.result", vm.language), color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
                Text(res, color = Qrme.Txt, fontSize = 14.sp)
            }
        }
    }
}

// ---- Settings (model picker + objections) ----

@Composable
fun SettingsScreen(vm: StudioViewModel) {
    var providers by remember { mutableStateOf<List<ProviderInfo>>(emptyList()) }
    var current by remember { mutableStateOf("auto") }
    var effective by remember { mutableStateOf("") }
    var objections by remember { mutableStateOf<List<Objection>>(emptyList()) }
    var languages by remember { mutableStateOf<List<LanguageInfo>>(emptyList()) }
    var language by remember { mutableStateOf("en") }
    var preTranslate by remember { mutableStateOf(true) }
    var translateInput by remember { mutableStateOf("") }
    var translated by remember { mutableStateOf<TranslateResult?>(null) }
    var wmMark by remember { mutableStateOf("") }
    var wmLabel by remember { mutableStateOf("") }
    var wmLine by remember { mutableStateOf("") }
    var wmCustom by remember { mutableStateOf(false) }
    var wmSaved by remember { mutableStateOf(false) }
    var llmKey by remember { mutableStateOf(vm.llmKey) }
    var inviteKey by remember { mutableStateOf(vm.signupKey) }
    var error by remember { mutableStateOf<String?>(null) }

    fun reload() {
        vm.call({ ApiClient.models() }) { r -> providers = r.getOrDefault(emptyList()) }
        vm.call({ ApiClient.languages() }) { r -> languages = r.getOrDefault(emptyList()) }
        vm.call({ ApiClient.profileLanguage(vm.pid!!) }) { r ->
            r.getOrNull()?.let { (lang, mode) ->
                language = lang; preTranslate = mode == "pre"
                vm.rememberLanguage(lang)   // chrome follows the profile
            }
        }
        vm.call({ ApiClient.profileModel(vm.pid!!) }) { r ->
            r.getOrNull()?.let { current = it.provider; effective = it.effective }
        }
        vm.call({ ApiClient.objections(vm.pid!!, vm.token!!) }) { r ->
            objections = r.getOrDefault(emptyList())
        }
        vm.call({ ApiClient.watermarkDesign(vm.pid!!) }) { r ->
            r.getOrNull()?.let { wmLine = it.line; wmCustom = it.custom }
        }
    }
    LaunchedEffect(Unit) { reload() }

    screenScroll {
        Text(L10n.t("tab.settings", vm.language), color = Qrme.Txt, fontSize = 22.sp,
            fontWeight = FontWeight.Bold)

        // 0.58.0. The console has offered this since 0.4.3 and the phones
        // never did: a key set there was used there, and the deployment's key
        // used here, on the same account.
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("set.key", vm.language), color = Qrme.Txt, fontSize = 16.sp,
                fontWeight = FontWeight.Bold)
            Text(L10n.t("set.key.lead", vm.language), color = Qrme.T2, fontSize = 12.sp)
            labeledField(L10n.t("set.key.label", vm.language), llmKey,
                L10n.t("set.key.ph", vm.language)) { llmKey = it }
            SmallAction(L10n.t("action.save", vm.language)) { vm.rememberLlmKey(llmKey) }
        }

        // The deployment invite key. A published deployment gates account
        // creation behind one; this phone talks to whichever backend the
        // connection above names, so it needs the same door the console has.
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("set.invite", vm.language), color = Qrme.Txt, fontSize = 16.sp,
                fontWeight = FontWeight.Bold)
            Text(L10n.t("set.invite.lead", vm.language), color = Qrme.T2, fontSize = 12.sp)
            labeledField(L10n.t("set.invite", vm.language), inviteKey,
                L10n.t("set.invite", vm.language)) { inviteKey = it }
            SmallAction(L10n.t("action.save", vm.language)) { vm.rememberSignupKey(inviteKey) }
        }

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("ns.model", vm.language), color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            Text(L10n.t("ns.model.sub", vm.language),
                color = Qrme.T2, fontSize = 12.sp)
            providers.forEach { p ->
                Row(Modifier.fillMaxWidth().clickable {
                    error = null
                    vm.call({ ApiClient.setModel(vm.pid!!, vm.token!!, p.name) }) { r ->
                        r.onSuccess { current = it.provider; effective = it.effective }
                         .onFailure { error = it.message }
                    }
                }, verticalAlignment = Alignment.CenterVertically) {
                    Box(Modifier.size(16.dp).clip(CircleShape)
                        .background(if (p.name == current) Qrme.BrandA else Qrme.Card))
                    Text(p.label, color = Qrme.Txt, fontSize = 14.sp,
                        modifier = Modifier.weight(1f).padding(start = 10.dp))
                    Text(L10n.t(if (p.configured) "ns.model.ready" else "ns.model.nokey", vm.language),
                        color = if (p.configured) Qrme.Green else Qrme.T3, fontSize = 12.sp)
                }
            }
            if (effective.isNotEmpty())
                Text(L10n.fill("ns.model.effective", vm.language, mapOf("name" to effective)),
                    color = Qrme.T2, fontSize = 12.sp)
        }

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("ns.lang", vm.language), color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            Text(L10n.t("ns.lang.sub", vm.language),
                color = Qrme.T2, fontSize = 12.sp)
            languages.chunked(3).forEach { row ->
                Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                    row.forEach { l ->
                        FilterChip(
                            selected = language == l.code,
                            onClick = {
                                vm.call({ ApiClient.setLanguage(vm.pid!!, vm.token!!, l.code,
                                    if (preTranslate) "pre" else "on_demand") }) {
                                    language = l.code
                                    vm.rememberLanguage(l.code)
                                }
                            },
                            label = { Text(l.label, fontSize = 11.sp) },
                            colors = FilterChipDefaults.filterChipColors(
                                selectedContainerColor = Qrme.BrandA,
                                selectedLabelColor = Color.White, labelColor = Qrme.T2,
                            ),
                        )
                    }
                }
            }
            Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                Column(Modifier.weight(1f)) {
                    Text(L10n.t("ns.lang.pre", vm.language), color = Qrme.Txt, fontSize = 13.sp)
                    Text(L10n.t("ns.lang.pre.sub", vm.language),
                        color = Qrme.T2, fontSize = 10.sp)
                }
                Switch(
                    checked = preTranslate,
                    onCheckedChange = { on ->
                        preTranslate = on
                        vm.call({ ApiClient.setLanguage(vm.pid!!, vm.token!!, language,
                            if (on) "pre" else "on_demand") }) { }
                    },
                    colors = SwitchDefaults.colors(checkedTrackColor = Qrme.Green),
                )
            }
            HorizontalDivider(color = Qrme.Line)
            Text(L10n.t("ns.tr", vm.language), color = Qrme.Txt, fontSize = 13.sp,
                fontWeight = FontWeight.Bold)
            labeledField("", translateInput, L10n.t("ns.tr.ph", vm.language)) { translateInput = it }
            SmallAction(L10n.t("action.translate", vm.language)) {
                if (translateInput.isNotBlank() && language != "en") {
                    vm.call({ ApiClient.translate(vm.pid!!, vm.token!!, translateInput) }) { r ->
                        translated = r.getOrNull()
                    }
                }
            }
            translated?.let { t ->
                Text(t.translation, color = Qrme.Txt, fontSize = 13.sp,
                    modifier = Modifier.fillMaxWidth().clip(RoundedCornerShape(9.dp))
                        .background(Qrme.ScrBot).padding(10.dp))
                Text(L10n.fill("ns.tr.engine", vm.language, mapOf("engine" to t.engine))
                        + (t.note?.let { " — $it" } ?: ""),
                    color = Qrme.T3, fontSize = 10.sp)
            }
        }

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("ns.wm", vm.language), color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            Text(L10n.t("ns.wm.sub", vm.language),
                color = Qrme.T2, fontSize = 12.sp)
            if (wmLine.isNotEmpty())
                Text(wmLine, color = Qrme.T2, fontSize = 12.sp, fontWeight = FontWeight.Bold,
                    modifier = Modifier.clip(RoundedCornerShape(12.dp))
                        .background(Qrme.ScrBot).padding(horizontal = 10.dp, vertical = 6.dp))
            labeledField(L10n.t("ns.wm.mark", vm.language), wmMark, "✦") { wmMark = it }
            labeledField(L10n.t("ns.wm.label", vm.language), wmLabel,
                L10n.t("ns.wm.label.example", vm.language).replace("{name}", vm.displayName)) { wmLabel = it }
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp),
                verticalAlignment = Alignment.CenterVertically) {
                SmallAction(L10n.t("ns.wm.save", vm.language)) {
                    vm.call({ ApiClient.setWatermarkDesign(vm.pid!!, vm.token!!, wmMark, wmLabel) }) { r ->
                        r.onSuccess { wmLine = it.line; wmCustom = it.custom; wmSaved = true }
                         .onFailure { error = it.message }
                    }
                }
                if (wmCustom) SmallAction(L10n.t("ns.wm.reset", vm.language)) {
                    vm.call({ ApiClient.setWatermarkDesign(vm.pid!!, vm.token!!, null, null) }) { r ->
                        r.onSuccess {
                            wmLine = it.line; wmCustom = it.custom
                            wmMark = ""; wmLabel = ""; wmSaved = false
                        }
                    }
                }
                if (wmSaved) Text(L10n.t("ns.wm.saved", vm.language), color = Qrme.Green, fontSize = 12.sp)
            }
        }

        WhoWroteThisCard(vm)
        YourSideCard(vm)
        ObjectToAProfileCard(vm)
        // Was spliced between two arguments of the `Text(…)` above — a call
        // in an argument list, which does not parse. It belongs here, beside
        // the other cards, where the iOS shell has always had it.
        ProblemReportingCard(vm.language)

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("ns.obj", vm.language), color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            if (objections.isEmpty()) {
                Text(L10n.t("ns.obj.none", vm.language),
                    color = Qrme.T2, fontSize = 13.sp)
            } else objections.forEach { o ->
                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    Text(o.status.uppercase(), fontSize = 12.sp, fontWeight = FontWeight.Bold,
                        color = if (o.status == "open") Qrme.Amber else Qrme.T2)
                    o.reason?.let { Text(it, color = Qrme.Txt, fontSize = 13.sp) }
                    if (o.status == "open" && o.reattested == 0) {
                        TextButton(onClick = {
                            vm.call({ ApiClient.attest(vm.pid!!, o.id, vm.token!!) }) { reload() }
                        }) { Text(L10n.t("ns.obj.attest", vm.language), color = Qrme.BrandA, fontSize = 13.sp) }
                    } else if (o.reattested == 1) {
                        Text(L10n.t("ns.obj.attested", vm.language), color = Qrme.Green, fontSize = 12.sp)
                    }
                }
            }
        }

        SteeringPanel(vm)

        RelationshipPanel(vm)

        FeedbackPanel(vm)
        AccessPanel(vm)

        error?.let { Text(it, color = Qrme.Red, fontSize = 13.sp) }
    }
}

// ---- Steering: the owner shapes how the profile comes across ----

@Composable
private fun SteeringPanel(vm: StudioViewModel) {
    var hub by remember { mutableStateOf<SteeringHubState?>(null) }
    var values by remember { mutableStateOf<Map<String, Float>>(emptyMap()) }
    var appearance by remember { mutableStateOf("") }
    var baseAge by remember { mutableStateOf("") }
    var agingEnabled by remember { mutableStateOf(false) }
    var status by remember { mutableStateOf<String?>(null) }
    // Labels, not ids. The keys on the left are what the steering API
    // matches on and stay English; the words on the right are read.
    val groupLabels = mapOf(
        "system" to L10n.t("ns.st.g.system", vm.language),
        "behavior" to L10n.t("ns.st.g.behavior", vm.language),
        "intimacy" to L10n.t("ns.st.g.intimacy", vm.language))

    LaunchedEffect(Unit) {
        vm.call({ ApiClient.steeringHub(vm.pid!!, vm.token!!) }) { r ->
            r.getOrNull()?.let { h ->
                hub = h
                values = h.values.mapValues { it.value.toFloat() }
                appearance = h.appearance ?: ""
                baseAge = h.baseAge?.toString() ?: ""
                agingEnabled = h.agingEnabled
            }
        }
    }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("ns.st", vm.language), color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
        Text(L10n.fill("ns.st.sub", vm.language,
                mapOf("name" to L10n.t("ns.st.the_profile", vm.language))),
            color = Qrme.T2, fontSize = 12.sp)
        hub?.let { h ->
            listOf("system", "behavior", "intimacy").forEach { group ->
                val dials = h.dials.filter { it.group == group }
                if (dials.isNotEmpty()) {
                    Text(groupLabels[group] ?: group, color = Qrme.BrandA,
                        fontSize = 12.sp, fontWeight = FontWeight.Bold)
                    dials.forEach { d ->
                        Column {
                            Row(Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween) {
                                Text(d.label, color = Qrme.Txt, fontSize = 13.sp)
                                Text("${(values[d.name] ?: 50f).toInt()}",
                                    color = Qrme.BrandA, fontSize = 12.sp,
                                    fontWeight = FontWeight.Bold)
                            }
                            Slider(
                                value = values[d.name] ?: 50f,
                                onValueChange = { values = values + (d.name to it) },
                                valueRange = d.min.toFloat()..d.max.toFloat(),
                                colors = SliderDefaults.colors(
                                    thumbColor = Qrme.BrandA,
                                    activeTrackColor = Qrme.BrandA),
                            )
                            Row(Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween) {
                                Text(d.low, color = Qrme.T3, fontSize = 10.sp)
                                Text(d.high, color = Qrme.T3, fontSize = 10.sp)
                            }
                        }
                    }
                }
            }
            OutlinedTextField(value = appearance, onValueChange = { appearance = it },
                label = { Text(L10n.t("ns.st.appearance.ph", vm.language)) },
                modifier = Modifier.fillMaxWidth())
            Row(verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                OutlinedTextField(value = baseAge, onValueChange = { baseAge = it },
                    label = { Text(L10n.t("ns.st.baseage", vm.language)) }, modifier = Modifier.width(110.dp))
                Text(L10n.t("ns.st.aging", vm.language), color = Qrme.Txt, fontSize = 13.sp)
                Switch(checked = agingEnabled, onCheckedChange = { agingEnabled = it },
                    colors = SwitchDefaults.colors(checkedTrackColor = Qrme.Green))
            }
            h.effectiveAge?.let {
                Text(L10n.fill("ns.st.effective", vm.language, mapOf("age" to it.toString())),
                    color = Qrme.T3, fontSize = 11.sp)
            }
            // The personality nobody can move: while the lock stands,
            // no steering write lands.
            if (h.locked) {
                Text(L10n.t("ns.st.locked", vm.language), color = Qrme.Amber, fontSize = 12.sp)
                SmallAction(L10n.t("ns.st.unlock", vm.language)) {
                    vm.call({ ApiClient.unlockSteering(vm.pid!!, vm.token!!)
                        ApiClient.steeringHub(vm.pid!!, vm.token!!) }) { r ->
                        r.getOrNull()?.let { hub = it } }
                }
            } else {
                SmallAction(L10n.t("ns.st.lock", vm.language)) {
                    vm.call({ ApiClient.lockSteering(vm.pid!!, vm.token!!)
                        ApiClient.steeringHub(vm.pid!!, vm.token!!) }) { r ->
                        r.getOrNull()?.let { hub = it } }
                }
            }
            SmallAction(L10n.t("ns.st.apply", vm.language), enabled = !h.locked) {
                status = null
                vm.call({
                    ApiClient.setSteeringHub(vm.pid!!, vm.token!!,
                        values.mapValues { it.value.toInt() },
                        baseAge.toIntOrNull(), agingEnabled,
                        appearance.ifBlank { null })
                }) { r ->
                    r.onSuccess { hub = it
                        status = L10n.t("ns.st.applied", vm.language) }
                     .onFailure { status = it.message }
                }
            }
            status?.let { Text(it, color = Qrme.Green, fontSize = 12.sp) }
        } ?: CircularProgressIndicator(color = Qrme.BrandA, modifier = Modifier.size(22.dp))
    }
}

// ---- Relationship: how the profile relates to you ----

@Composable
private fun RelationshipPanel(vm: StudioViewModel) {
    val types = listOf("family", "grandchild", "friend", "romantic_partner",
        "professional", "fan", "stranger")
    var type by remember { mutableStateOf("friend") }
    var nickname by remember { mutableStateOf("") }
    var tone by remember { mutableStateOf("") }
    var status by remember { mutableStateOf<String?>(null) }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("ns.rel", vm.language), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        Text(L10n.t("ns.rel.sub", vm.language),
            color = Qrme.T2, fontSize = 12.sp)
        Row(Modifier.horizontalScroll(rememberScrollState()),
            horizontalArrangement = Arrangement.spacedBy(6.dp)) {
            types.forEach { t ->
                val on = type == t
                Text(t.replace('_', ' '), color = if (on) Color.White else Qrme.Txt,
                    fontSize = 11.sp,
                    modifier = Modifier.clip(RoundedCornerShape(50))
                        .background(if (on) Qrme.BrandA else Qrme.ScrBot)
                        .clickable { type = t }
                        .padding(horizontal = 10.dp, vertical = 6.dp))
            }
        }
        OutlinedTextField(value = nickname, onValueChange = { nickname = it },
            label = { Text(L10n.t("ns.rel.nick.ph", vm.language)) },
            modifier = Modifier.fillMaxWidth())
        OutlinedTextField(value = tone, onValueChange = { tone = it },
            label = { Text(L10n.t("ns.rel.tone.ph", vm.language)) },
            modifier = Modifier.fillMaxWidth())
        SmallAction(L10n.t("ns.rel.save", vm.language)) {
            status = null
            vm.call({
                val interactor = vm.interactorId
                    ?: ApiClient.createInteractor("You")
                        .also { vm.rememberInteractor(it.id, it.token) }.id
                ApiClient.setRelationship(vm.pid!!, vm.token!!, interactor,
                    type, nickname, tone)
            }) { r ->
                r.onSuccess { status = L10n.fill("ns.rel.saved", vm.language,
                        mapOf("type" to it.replace('_', ' '))) }
                 .onFailure { status = it.message }
            }
        }
        status?.let { Text(it, color = Qrme.Green, fontSize = 12.sp) }
    }
}

/** Ability is not a gate: the accessibility report door. Three questions,
 *  none a diagnosis, sent with no token — the person this card exists for
 *  may be the person the signup shut out. The reviewer row reads them back
 *  with the deployment's own token, never a profile's. */
@Composable
private fun AccessPanel(vm: StudioViewModel) {
    var doing by remember { mutableStateOf("") }
    var wall by remember { mutableStateOf("") }
    var help by remember { mutableStateOf("") }
    var status by remember { mutableStateOf<String?>(null) }
    var reviewer by remember { mutableStateOf("") }
    var reports by remember { mutableStateOf<List<AccessReportRow>?>(null) }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("ns.acc", vm.language), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        Text(L10n.t("ns.acc.lead", vm.language), color = Qrme.T2, fontSize = 12.sp)
        // The per-need statement the console makes, not just its form.
        Text(L10n.t("ns.acc.needs.title", vm.language), color = Qrme.Txt,
            fontSize = 13.sp, fontWeight = FontWeight.Bold)
        listOf("blind", "deaf", "mute", "motor", "cognitive",
            "dyslexia", "motion").forEach { need ->
            Text("• " + L10n.t("ns.acc.needs.$need", vm.language),
                color = Qrme.T2, fontSize = 12.sp)
        }
        Text(L10n.t("ns.acc.needs.more", vm.language), color = Qrme.T2,
            fontSize = 12.sp, fontStyle = FontStyle.Italic)
        OutlinedTextField(value = doing, onValueChange = { doing = it },
            label = { Text(L10n.t("ns.acc.doing.ph", vm.language)) },
            modifier = Modifier.fillMaxWidth())
        OutlinedTextField(value = wall, onValueChange = { wall = it },
            label = { Text(L10n.t("ns.acc.wall.ph", vm.language)) }, minLines = 2,
            modifier = Modifier.fillMaxWidth())
        OutlinedTextField(value = help, onValueChange = { help = it },
            label = { Text(L10n.t("ns.acc.help.ph", vm.language)) },
            modifier = Modifier.fillMaxWidth())
        SmallAction(L10n.t("ns.acc.send", vm.language)) {
            if (doing.isNotBlank() && wall.isNotBlank())
                vm.call({ ApiClient.sendAccessReport(doing.trim(), wall.trim(),
                    help.trim(), vm.language) }) {
                    status = L10n.t("ns.acc.sent", vm.language)
                    doing = ""; wall = ""; help = ""
                }
        }
        status?.let { Text(it, color = Qrme.Green, fontSize = 12.sp) }

        OutlinedTextField(value = reviewer, onValueChange = { reviewer = it },
            label = { Text(L10n.t("ns.acc.token.ph", vm.language)) },
            modifier = Modifier.fillMaxWidth())
        SmallAction(L10n.t("ns.acc.load", vm.language)) {
            vm.call({ ApiClient.accessReports(reviewer.trim()) }) { r ->
                reports = r.getOrNull()
            }
        }
        reports?.let { rs ->
            if (rs.isEmpty())
                Text(L10n.t("ns.acc.none", vm.language), color = Qrme.T3, fontSize = 11.sp)
            else rs.take(6).forEach { r ->
                Text(r.doing, color = Qrme.Txt, fontSize = 12.sp,
                    fontWeight = FontWeight.Bold)
                Text(r.wall, color = Qrme.T2, fontSize = 11.sp)
                r.help?.let { h -> Text(h, color = Qrme.T2, fontSize = 11.sp) }
                Text("${r.lang} · ${r.createdAt}", color = Qrme.T3, fontSize = 10.sp)
            }
        }
    }
}

@Composable
private fun FeedbackPanel(vm: StudioViewModel) {
    val categories = listOf("idea", "improvement", "bug", "praise", "other")
    var category by remember { mutableStateOf("idea") }
    var message by remember { mutableStateOf("") }
    var rating by remember { mutableIntStateOf(0) }
    var state by remember { mutableStateOf<FeedbackState?>(null) }
    var status by remember { mutableStateOf<String?>(null) }

    fun reload() {
        vm.call({ ApiClient.feedback(vm.token) }) { r -> state = r.getOrNull() }
    }
    LaunchedEffect(Unit) { reload() }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("ns.fb", vm.language), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        Text(L10n.t("ns.fb.sub", vm.language),
            color = Qrme.T2, fontSize = 12.sp)
        Row(Modifier.horizontalScroll(rememberScrollState()),
            horizontalArrangement = Arrangement.spacedBy(6.dp)) {
            categories.forEach { c ->
                val on = category == c
                Text(c, color = if (on) Color.White else Qrme.Txt, fontSize = 11.sp,
                    modifier = Modifier.clip(RoundedCornerShape(50))
                        .background(if (on) Qrme.BrandA else Qrme.ScrBot)
                        .clickable { category = c }
                        .padding(horizontal = 10.dp, vertical = 6.dp))
            }
        }
        OutlinedTextField(value = message, onValueChange = { message = it },
            label = { Text(L10n.t("ns.fb.msg.ph", vm.language)) }, minLines = 2,
            modifier = Modifier.fillMaxWidth())
        Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
            (1..5).forEach { n ->
                Text(if (n <= rating) "★" else "☆",
                    color = if (n <= rating) Qrme.Amber else Qrme.T3, fontSize = 18.sp,
                    modifier = Modifier.clickable { rating = if (rating == n) 0 else n })
            }
        }
        SmallAction(L10n.t("ns.fb.send", vm.language)) {
            if (message.isNotBlank())
                vm.call({ ApiClient.submitFeedback(vm.token, category,
                    message.trim(), rating.takeIf { it > 0 }) }) {
                    status = "Thank you — sent."; message = ""; rating = 0
                    reload()
                }
        }
        status?.let { Text(it, color = Qrme.Green, fontSize = 12.sp) }
        state?.takeIf { it.total > 0 }?.let { s ->
            // The tally named its categories in English inside a sentence
            // that is otherwise translated.
            Text(L10n.fill("ns.fb.sofar", vm.language, mapOf("tally" to
                categories.filter { (s.tally[it] ?: 0) > 0 }.joinToString(" · ") {
                    "${s.tally[it]} ${L10n.t("ns.fb.c.$it", vm.language)}"
                })),
                color = Qrme.T3, fontSize = 11.sp)
            s.mine.take(4).forEach { f ->
                Text("[${f.category}] ${f.message} · ${f.status}",
                    color = Qrme.T2, fontSize = 11.sp, maxLines = 1)
            }
        }
    }
}

// ---- Chat (the core loop: an interactor talks with the profile) ----

private data class Bubble(val mine: Boolean, val text: String, val pending: Boolean,
                          val mark: String? = null)

@Composable
fun ChatScreen(vm: StudioViewModel) {
    var messages by remember { mutableStateOf<List<Bubble>>(emptyList()) }
    var draft by remember { mutableStateOf("") }
    var busy by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    // Spec clauses 2/12. Empty means "read my prompt and decide", which is what
    // the backend does on its own — and the reply says which way it went.
    var role by remember { mutableStateOf("") }

    fun send() {
        val text = draft
        if (text.isBlank()) return
        draft = ""
        messages = messages + Bubble(true, text, false)
        busy = true; error = null
        vm.call({
            var interactor = vm.interactorId
            var minted: String? = null
            if (interactor == null) {
                val created = ApiClient.createInteractor("You")
                interactor = created.id
                minted = created.token
            }
            Triple(interactor!!, minted,
                ApiClient.chat(vm.pid!!, vm.token!!, interactor, text,
                    role.ifBlank { null }))
        }) { r ->
            busy = false
            r.onSuccess { (interactor, mintedToken, reply) ->
                vm.rememberInteractor(interactor, mintedToken)
                messages = messages + if (reply.content != null && reply.status == "approved") {
                    listOfNotNull(
                        Bubble(false, reply.content, false,
                               mark = reply.watermarkLine ?: "\u2726 AI"),
                        reply.role?.let { r0 ->
                            Bubble(false, "◈ worked as $r0" +
                                (reply.roleHow?.let { " ($it)" } ?: ""), true)
                        },
                        reply.provenance?.let { prov ->
                            Bubble(false, "ⓘ " + L10n.fill("nprv.generated", vm.language,
                                    mapOf("model" to prov.generatedBy,
                                          "n" to prov.sourceItems.toString(),
                                          "status" to prov.moderationStatus)) +
                                (prov.licensedFrom?.let {
                                    " · " + L10n.fill("nprv.licensed", vm.language,
                                                      mapOf("source" to it)) } ?: ""),
                                true)
                        },
                    )
                } else listOf(
                    Bubble(false, "⏳ Held for review" +
                        (reply.flagReason?.let { " — $it" } ?: ""), true))
            }.onFailure { error = it.message }
        }
    }

    Column(Modifier.fillMaxSize()) {
        Column(
            Modifier.weight(1f).verticalScroll(rememberScrollState()).padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            Text(L10n.t("tab.chat", vm.language), color = Qrme.Txt, fontSize = 22.sp, fontWeight = FontWeight.Bold)
            Text(L10n.fill("nchat.sub", vm.language, mapOf("name" to vm.displayName)),
                color = Qrme.T2, fontSize = 13.sp)
            messages.forEach { m ->
                Row(Modifier.fillMaxWidth(),
                    horizontalArrangement = if (m.mine) Arrangement.End else Arrangement.Start) {
                    Column(Modifier
                            .clip(RoundedCornerShape(13.dp))
                            .background(if (m.mine) Qrme.BrandA.copy(alpha = 0.35f)
                                        else Qrme.Card.copy(alpha = 0.9f))
                            .padding(horizontal = 12.dp, vertical = 9.dp),
                        verticalArrangement = Arrangement.spacedBy(3.dp)) {
                        Text(m.text,
                            color = if (m.pending) Qrme.T2 else Qrme.Txt, fontSize = 14.sp)
                        // The watermark rides on every AI render, always visible.
                        m.mark?.let { Text(it, color = Qrme.T3, fontSize = 10.sp) }
                    }
                }
            }
            error?.let { Text(it, color = Qrme.Red, fontSize = 13.sp) }
        }
        // Spec clauses 2/12 — advisor counsels, collaborator co-creates,
        // operator executes. "Read my prompt" is the honest default: the
        // profile infers from the wording and the reply says which.
        Row(Modifier.padding(horizontal = 20.dp).padding(bottom = 6.dp),
            horizontalArrangement = Arrangement.spacedBy(6.dp)) {
            listOf("" to "Read my prompt", "advisor" to "Advisor",
                   "collaborator" to "Collaborator", "operator" to "Operator")
                .forEach { (value, label) ->
                    Box(Modifier.clip(RoundedCornerShape(50))
                            .background(if (role == value) Qrme.BrandA else Qrme.Card)
                            .clickable { role = value }
                            .padding(horizontal = 10.dp, vertical = 6.dp)) {
                        Text(label, fontSize = 11.sp,
                            color = if (role == value) Color.White else Qrme.T2)
                    }
                }
        }
        Row(Modifier.padding(horizontal = 20.dp).padding(bottom = 12.dp),
            horizontalArrangement = Arrangement.spacedBy(10.dp),
            verticalAlignment = Alignment.CenterVertically) {
            Box(Modifier.weight(1f)) {
                labeledField("", draft, L10n.t("nc.say.ph", vm.language)) { draft = it }
            }
            BrandButtonSmall(if (busy) "…" else L10n.t("nc.send", vm.language), enabled = draft.isNotBlank() && !busy) { send() }
        }
    }
}

@Composable
private fun BrandButtonSmall(text: String, enabled: Boolean, onClick: () -> Unit) {
    Box(
        Modifier.clip(RoundedCornerShape(12.dp))
            .background(if (enabled) Qrme.BrandA else Qrme.Card)
            .clickable(enabled = enabled) { onClick() }
            .padding(horizontal = 18.dp, vertical = 12.dp),
        contentAlignment = Alignment.Center,
    ) { Text(text, color = Color.White, fontWeight = FontWeight.Bold, fontSize = 13.sp) }
}

// ---- Studio (Compose · Posts · Study behind one tab) ----

@Composable
fun StudioScreen(vm: StudioViewModel) {
    var seg by remember { mutableIntStateOf(0) }
    Column(Modifier.fillMaxSize()) {
        TabRow(selectedTabIndex = seg, containerColor = Qrme.Card, contentColor = Qrme.BrandA) {
            listOf("tab.compose", "tab.posts", "tab.study").forEachIndexed { i, t ->
                Tab(selected = seg == i, onClick = { seg = i },
                    text = { Text(L10n.t(t, vm.language), fontSize = 13.sp) })
            }
        }
        Box(Modifier.weight(1f)) {
            when (seg) {
                0 -> ComposeScreen(vm)
                1 -> PostsScreen(vm)
                else -> StudyScreen(vm)
            }
        }
    }
}

// ---- Study (knowledge excursions: private data stays home) ----

@Composable
fun StudyScreen(vm: StudioViewModel) {
    var topic by remember { mutableStateOf("") }
    var question by remember { mutableStateOf("") }
    var excursions by remember { mutableStateOf<List<Excursion>>(emptyList()) }
    var busy by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }

    fun reload() { vm.call({ ApiClient.excursions(vm.pid!!, vm.token!!) }) { r -> excursions = r.getOrDefault(emptyList()) } }
    LaunchedEffect(Unit) { reload() }

    screenScroll {
        Text(L10n.t("nstu", vm.language), color = Qrme.Txt, fontSize = 22.sp, fontWeight = FontWeight.Bold)
        Text(L10n.t("nstu.sub", vm.language),
            color = Qrme.T2, fontSize = 13.sp)

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            labeledField(L10n.t("ncmp.topic", vm.language), topic,
                         L10n.t("nstu.topic.ph", vm.language)) { topic = it }
            labeledField(L10n.t("nstu.question", vm.language), question, L10n.t("nstu.question.ph", vm.language)) { question = it }
            BrandButton(L10n.t("nstu.go", vm.language), enabled = topic.isNotBlank() && question.isNotBlank(), busy = busy) {
                busy = true; error = null
                vm.call({ ApiClient.startExcursion(vm.pid!!, vm.token!!, topic, question) }) { r ->
                    busy = false
                    r.onSuccess { topic = ""; question = "" }
                     .onFailure { error = it.message }
                    reload()
                }
            }
        }
        error?.let { Text(it, color = Qrme.Red, fontSize = 13.sp) }

        excursions.asReversed().forEach { e ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text(e.topic, color = Qrme.Txt, fontSize = 14.sp, fontWeight = FontWeight.Bold)
                    Text(L10n.t(if (e.leftHost) "nstu.lefthost" else "nstu.stayedlocal", vm.language),
                        color = if (e.leftHost) Qrme.Amber else Qrme.Green,
                        fontSize = 11.sp, fontWeight = FontWeight.Bold)
                }
                if (e.redactions > 0)
                    Text(L10n.fill("nstu.redacted", vm.language, mapOf("n" to "${e.redactions}")),
                        color = Qrme.T2, fontSize = 12.sp)
                Text(e.findings, color = Qrme.Txt, fontSize = 13.sp)
                if (e.learned)
                    Text(L10n.t("nstu.folded", vm.language), color = Qrme.Green, fontSize = 12.sp)
                else
                    TextButton(onClick = {
                        vm.call({ ApiClient.learn(e.id, vm.token!!) }) { reload() }
                    }) { Text(L10n.t("nstu.fold", vm.language), color = Qrme.BrandA, fontSize = 13.sp) }
            }
        }
    }
}

// ---- Connect (Social · Apps · Robots behind one tab) ----

@Composable
fun ConnectScreen(vm: StudioViewModel) {
    var seg by remember { mutableIntStateOf(0) }
    Column(Modifier.fillMaxSize()) {
        TabRow(selectedTabIndex = seg, containerColor = Qrme.Card, contentColor = Qrme.BrandA) {
            listOf("ncon.tab.social", "ncon.tab.apps", "tab.robots").forEachIndexed { i, t ->
                Tab(selected = seg == i, onClick = { seg = i },
                    text = { Text(L10n.t(t, vm.language), fontSize = 13.sp) })
            }
        }
        Box(Modifier.weight(1f)) {
            when (seg) {
                0 -> SocialPanel(vm)
                1 -> AppsPanel(vm)
                else -> RobotsScreen(vm)
            }
        }
    }
}

@Composable
private fun SocialPanel(vm: StudioViewModel) {
    val platforms = listOf("instagram", "x", "tiktok", "facebook", "linkedin", "youtube",
        "reddit", "threads", "whatsapp", "meta", "mastodon", "twitch", "snapchat",
        "roblox", "pinterest", "discord")
    var platform by remember { mutableStateOf(platforms.first()) }
    var handle by remember { mutableStateOf("") }
    var conns by remember { mutableStateOf<List<SocialConn>>(emptyList()) }
    var status by remember { mutableStateOf<String?>(null) }
    var error by remember { mutableStateOf<String?>(null) }
    fun reload() { vm.call({ ApiClient.socialConnections(vm.pid!!, vm.token!!) }) { r -> conns = r.getOrDefault(emptyList()) } }
    LaunchedEffect(Unit) { reload() }

    fun connect(direction: String) {
        error = null; status = null
        vm.call({ ApiClient.socialConnect(vm.pid!!, vm.token!!, platform, direction, handle) }) { r ->
            r.onSuccess { handle = "" }.onFailure { error = it.message }
            reload()
        }
    }

    screenScroll {
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("ncon.social", vm.language), color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            Text(L10n.t("ncon.social.sub", vm.language),
                color = Qrme.T2, fontSize = 12.sp)
            platforms.chunked(4).forEach { row ->
                Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                    row.forEach { pname ->
                        FilterChip(
                            selected = platform == pname, onClick = { platform = pname },
                            label = { Text(pname, fontSize = 11.sp) },
                            colors = FilterChipDefaults.filterChipColors(
                                selectedContainerColor = Qrme.BrandA,
                                selectedLabelColor = Color.White, labelColor = Qrme.T2,
                            ),
                        )
                    }
                }
            }
            labeledField(L10n.t("ncon.h.handle", vm.language), handle, L10n.t("ncon.handle.example", vm.language)) { handle = it }
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                SmallAction(L10n.t("ncon.to.collect", vm.language)) { connect("collect") }
                SmallAction(L10n.t("ncon.to.publish", vm.language)) { connect("publish") }
            }
        }
        error?.let { Text(it, color = Qrme.Red, fontSize = 13.sp) }
        status?.let { Text(it, color = Qrme.Green, fontSize = 12.sp) }

        conns.forEach { c ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text("${c.platform} · ${c.direction}", color = Qrme.Txt,
                        fontSize = 14.sp, fontWeight = FontWeight.Bold)
                    c.handle?.let { Text(it, color = Qrme.T3, fontSize = 12.sp) }
                }
                Text(if (c.direction == "collect")
                         L10n.fill("ncon.collected", vm.language,
                                   mapOf("n" to "${c.collected}"))
                     else L10n.fill("ncon.published", vm.language,
                                    mapOf("n" to "${c.published}")),
                    color = Qrme.T2, fontSize = 12.sp)
                if (c.status == "revoked") {
                    Text(L10n.t("nmg.revoked", vm.language), color = Qrme.Red, fontSize = 12.sp)
                } else {
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp),
                        verticalAlignment = Alignment.CenterVertically) {
                        if (c.direction == "collect") {
                            SmallAction(L10n.t("ncon.collect.sample", vm.language)) {
                                vm.call({ ApiClient.socialCollect(c.id, vm.token!!,
                                    "sample post from ${c.platform}") }) { r ->
                                    r.onSuccess { status = "collected one item from ${c.platform} — it now feeds training" }
                                        .onFailure { error = it.message }
                                    reload()
                                }
                            }
                            val h = c.handle
                            if (h != null && h.isNotEmpty()) {
                                SmallAction(L10n.t("ncon.scrape", vm.language)) {
                                    vm.call({ ApiClient.socialScrape(c.id, vm.token!!) }) { r ->
                                        r.onSuccess { status = "fetched ${c.platform} — the page now feeds training" }
                                            .onFailure { error = it.message }
                                        reload()
                                    }
                                }
                            }
                        } else {
                            SmallAction(L10n.t("ncon.publish.update", vm.language)) {
                                vm.call({ ApiClient.socialPublish(c.id, vm.token!!,
                                    "An update from my synthetic profile.") }) { r ->
                                    r.onSuccess { status = "published to ${c.platform}" }
                                        .onFailure { error = it.message }
                                    reload()
                                }
                            }
                        }
                        TextButton(onClick = {
                            vm.call({ ApiClient.revokeSocial(c.id, vm.token!!) }) { reload() }
                        }) { Text(L10n.t("ncon.disconnect", vm.language), color = Qrme.Red, fontSize = 12.sp) }
                    }
                }
            }
        }
    }
}

@Composable
private fun AppsPanel(vm: StudioViewModel) {
    var catalog by remember { mutableStateOf<List<CatalogApp>>(emptyList()) }
    var conns by remember { mutableStateOf<List<AppConn>>(emptyList()) }
    var status by remember { mutableStateOf<String?>(null) }
    var error by remember { mutableStateOf<String?>(null) }
    fun reload() {
        vm.call({ ApiClient.appsCatalog() }) { r -> catalog = r.getOrDefault(emptyList()) }
        vm.call({ ApiClient.appConnections(vm.pid!!, vm.token!!) }) { r -> conns = r.getOrDefault(emptyList()) }
    }
    LaunchedEffect(Unit) { reload() }

    screenScroll {
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("ncon.apps", vm.language), color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            Text(L10n.t("ncon.apps.sub", vm.language),
                color = Qrme.T2, fontSize = 12.sp)
            catalog.take(12).forEach { entry ->
                Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                    Column(Modifier.weight(1f)) {
                        Text(entry.label, color = Qrme.Txt, fontSize = 14.sp)
                        Text(entry.provider, color = Qrme.T3, fontSize = 11.sp)
                    }
                    TextButton(onClick = {
                        error = null
                        vm.call({ ApiClient.appConnect(vm.pid!!, vm.token!!,
                            entry.provider, entry.app) }) { r ->
                            r.onSuccess { status = "connected ${entry.provider}/${entry.app}" }
                                .onFailure { error = it.message }
                            reload()
                        }
                    }) { Text(L10n.t("tab.connect", vm.language), color = Qrme.BrandA, fontSize = 13.sp, fontWeight = FontWeight.Bold) }
                }
            }
        }
        error?.let { Text(it, color = Qrme.Red, fontSize = 13.sp) }
        status?.let { Text(it, color = Qrme.Green, fontSize = 12.sp) }

        conns.forEach { c ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text(c.label, color = Qrme.Txt, fontSize = 14.sp, fontWeight = FontWeight.Bold)
                    Text(c.provider, color = Qrme.T3, fontSize = 12.sp)
                }
                if (c.status == "revoked") {
                    Text(L10n.t("nmg.revoked", vm.language), color = Qrme.Red, fontSize = 12.sp)
                } else {
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        SmallAction(L10n.t("ncon.collect", vm.language)) {
                            vm.call({ ApiClient.appCollect(c.id, vm.token!!,
                                "sample context from ${c.app}") }) { r ->
                                r.onSuccess { status = "collected from ${c.label} — it now feeds training" }
                                    .onFailure { error = it.message }
                            }
                        }
                        c.capabilities.firstOrNull()?.let { cap ->
                            SmallAction(L10n.t("ncon.invoke", vm.language).replace("{cap}", cap)) {
                                vm.call({ ApiClient.appInvoke(c.id, vm.token!!, cap) }) { r ->
                                    r.onSuccess { status = it.result }
                                        .onFailure { error = it.message }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun SmallAction(text: String, enabled: Boolean = true,
                        onClick: () -> Unit) {
    // `enabled` defaults true so the existing call sites are untouched. Both
    // backgrounds are Colors here (unlike JIM's, where the brand is a Brush),
    // so one ternary is enough rather than layering two background() calls.
    Box(
        Modifier.clip(RoundedCornerShape(50))
            .background(if (enabled) Qrme.BrandA else Qrme.Card)
            .clickable(enabled = enabled) { onClick() }
            .padding(horizontal = 12.dp, vertical = 8.dp),
    ) {
        Text(text, color = if (enabled) Color.White else Qrme.T3,
            fontSize = 12.sp, fontWeight = FontWeight.Bold)
    }
}

// ---- Chat hub (Profile · Stranger · Rooms behind one tab) ----

@Composable
fun ChatHubScreen(vm: StudioViewModel) {
    var seg by remember { mutableIntStateOf(0) }
    Column(Modifier.fillMaxSize()) {
        TabRow(selectedTabIndex = seg, containerColor = Qrme.Card, contentColor = Qrme.BrandA) {
            listOf("nc.t.profile", "nc.t.stranger", "nc.rooms").forEachIndexed { i, t ->
                Tab(selected = seg == i, onClick = { seg = i },
                    text = { Text(L10n.t(t, vm.language), fontSize = 13.sp) })
            }
        }
        Box(Modifier.weight(1f)) {
            when (seg) {
                0 -> ChatScreen(vm)
                1 -> StrangerPanel(vm)
                else -> RoomsPanel(vm)
            }
        }
    }
}

/// Mint (and remember) the device owner's interactor identity — the same one
/// Chat uses — before running [block] with it.
private fun withInteractor(vm: StudioViewModel, onError: (String) -> Unit,
                           block: (String) -> Unit) {
    vm.interactorId?.let { return block(it) }
    vm.call({ ApiClient.createInteractor("You") }) { r ->
        r.onSuccess { vm.rememberInteractor(it.id, it.token); block(it.id) }
            .onFailure { onError(it.message ?: "couldn't create your identity") }
    }
}

@Composable
private fun StrangerPanel(vm: StudioViewModel) {
    var alias by remember { mutableStateOf("") }
    var tier by remember { mutableStateOf("friendly") }
    var birthdate by remember { mutableStateOf("") }
    var waiting by remember { mutableStateOf(false) }
    var connectionId by remember { mutableStateOf<String?>(null) }
    var matchedWith by remember { mutableStateOf<String?>(null) }
    var messages by remember { mutableStateOf<List<ConnMsg>>(emptyList()) }
    var draft by remember { mutableStateOf("") }
    var error by remember { mutableStateOf<String?>(null) }

    fun refresh(cid: String) {
        val me = vm.interactorId ?: return
        vm.call({ ApiClient.connectionMessages(cid, me, vm.interactorToken.orEmpty()) }) { r ->
            r.onSuccess { messages = it }
        }
    }

    fun joinAs(me: String, minted: Boolean) {
        vm.call({ ApiClient.joinQueue(me, alias, tier, vm.interactorToken.orEmpty()) }) { r ->
            r.onSuccess {
                // The server admitted this identity to the queue — a rated
                // admit proves the 18+ verification stands.
                if (minted) vm.rememberInteractor(me, adult = true)
                if (it.status == "matched" && it.connectionId != null) {
                    connectionId = it.connectionId
                    matchedWith = it.matchedWith
                    waiting = false
                    refresh(it.connectionId)
                } else waiting = true
            }.onFailure { error = it.message }
        }
    }

    fun join() {
        error = null
        if (tier == "rated" && !vm.interactorVerified) {
            // Verify 18+: mint a fresh identity carrying the birthdate —
            // the age wall checks it server-side.
            vm.call({ ApiClient.createInteractor("You", birthdate) }) { r ->
                r.onSuccess {
                    vm.rememberInteractor(it.id, it.token)
                    joinAs(it.id, minted = true)
                }.onFailure { error = it.message }
            }
        } else withInteractor(vm, { error = it }) { me -> joinAs(me, minted = false) }
    }

    screenScroll {
        val cid = connectionId
        if (cid == null) {
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                Text(L10n.t("nc.stranger", vm.language), color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
                Text(L10n.t("nc.stranger.sub", vm.language),
                    color = Qrme.T2, fontSize = 12.sp)
                Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                    listOf("friendly" to L10n.t("nc.tier.friendly", vm.language),
                           "rated" to L10n.t("nc.tier.rated", vm.language)).forEach { (t, label) ->
                        val on = tier == t
                        Text(label, color = if (on) Color.White else Qrme.Txt, fontSize = 12.sp,
                            modifier = Modifier.clip(RoundedCornerShape(50))
                                .background(if (on) Qrme.BrandA else Qrme.ScrBot)
                                .clickable { tier = t }
                                .padding(horizontal = 12.dp, vertical = 7.dp))
                    }
                }
                if (tier == "rated" && !vm.interactorVerified) {
                    Text(L10n.t("nc.rated.sub", vm.language),
                        color = Qrme.Amber, fontSize = 11.sp)
                    labeledField(L10n.t("nw.birthdate", vm.language), birthdate, L10n.t("nw.birthdate.ph", vm.language)) { birthdate = it }
                }
                labeledField(L10n.t("nc.alias.ph", vm.language), alias, L10n.t("nc.alias.example", vm.language)) { alias = it }
                BrandButton(L10n.t(if (waiting) "nc.match.waiting" else "nc.match.find", vm.language),
                    enabled = tier != "rated" || vm.interactorVerified || birthdate.isNotBlank()) { join() }
            }
        } else {
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text(L10n.fill("nc.talking", vm.language, mapOf("who" to
                        (matchedWith ?: L10n.t("nc.a_stranger", vm.language)))), color = Qrme.Txt,
                        fontSize = 16.sp, fontWeight = FontWeight.Bold)
                    TextButton(onClick = {
                        vm.interactorId?.let { me ->
                            vm.call({ ApiClient.endConnection(cid, me, vm.interactorToken.orEmpty()) }) {
                                connectionId = null; matchedWith = null
                                messages = emptyList(); waiting = false
                            }
                        }
                    }) { Text(L10n.t("nc.end", vm.language), color = Qrme.Red, fontSize = 12.sp) }
                }
                messages.forEach { m ->
                    Column(
                        Modifier.fillMaxWidth().clip(RoundedCornerShape(12.dp))
                            .background(if (m.from == "you") Qrme.BrandA.copy(alpha = 0.35f)
                                        else Qrme.Card.copy(alpha = 0.9f))
                            .padding(horizontal = 12.dp, vertical = 8.dp),
                    ) {
                        Text(m.from, color = Qrme.T3, fontSize = 10.sp)
                        Text(m.content, color = Qrme.Txt, fontSize = 13.sp)
                        if (m.status == "blocked")
                            Text(L10n.t("nc.blocked", vm.language), color = Qrme.Red, fontSize = 10.sp)
                    }
                }
                labeledField("", draft, L10n.t("nc.say.ph", vm.language)) { draft = it }
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    SmallAction(L10n.t("nc.send", vm.language)) {
                        val text = draft
                        if (text.isNotBlank()) {
                            draft = ""; error = null
                            withInteractor(vm, { error = it }) { me ->
                                vm.call({ ApiClient.sendConnectionMessage(cid, me, text, vm.interactorToken.orEmpty()) }) { r ->
                                    r.onFailure { error = it.message }
                                    refresh(cid)
                                }
                            }
                        }
                    }
                    TextButton(onClick = { refresh(cid) }) {
                        Text(L10n.t("nc.refresh", vm.language), color = Qrme.BrandA, fontSize = 12.sp)
                    }
                }
            }
        }
        error?.let { Text(it, color = Qrme.Red, fontSize = 13.sp) }
    }
}

@Composable
private fun RoomsPanel(vm: StudioViewModel) {
    var topic by remember { mutableStateOf("") }
    var templates by remember {
        mutableStateOf<List<Triple<String, String, String>>>(emptyList())
    }
    var room by remember { mutableStateOf<RoomCreated?>(null) }
    var transcript by remember { mutableStateOf<List<RoomMsg>>(emptyList()) }
    var draft by remember { mutableStateOf("") }
    var busy by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }

    LaunchedEffect(Unit) {
        vm.call({ ApiClient.roomTemplates() }) { r ->
            r.onSuccess { templates = it }
        }
    }

    fun reload(roomId: String) {
        val tok = vm.interactorToken ?: return
        vm.call({ ApiClient.roomTranscript(roomId, tok) }) { r ->
            r.onSuccess { transcript = it }
        }
    }

    screenScroll {
        val current = room
        if (current == null) {
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                Text(L10n.t("nc.room.open", vm.language), color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
                Text(L10n.fill("nc.room.sub", vm.language, mapOf("name" to vm.displayName)),
                    color = Qrme.T2, fontSize = 12.sp)
                labeledField(L10n.t("nc.topic.ph", vm.language), topic, L10n.t("nc.room.topic.ph", vm.language)) { topic = it }
                BrandButton(L10n.t("nc.room.here", vm.language), enabled = topic.isNotBlank(), busy = busy) {
                    busy = true; error = null
                    withInteractor(vm, { error = it; busy = false }) { me ->
                        vm.call({ ApiClient.createRoom(topic, vm.pid!!, me) }) { r ->
                            busy = false
                            r.onSuccess { room = it; topic = ""; transcript = emptyList() }
                                .onFailure { error = it.message }
                        }
                    }
                }
                // The standing rooms: tapping one steps into the room
                // itself — the live one when somebody is there, opened
                // fresh when nobody is. The first build only filled the
                // topic field, which minted a copy per press.
                if (templates.isNotEmpty()) {
                    Text(L10n.t("nc.room.standing", vm.language), color = Qrme.T2,
                        fontSize = 12.sp, fontWeight = FontWeight.Bold)
                    templates.forEach { (tKey, tTopic, tChannel) ->
                        TextButton(onClick = {
                            busy = true; error = null
                            withInteractor(vm, { error = it; busy = false }) { _ ->
                                vm.call({ ApiClient.openStandingRoom(tKey,
                                    vm.pid!!, vm.interactorToken.orEmpty()) }) { r ->
                                    busy = false
                                    r.onSuccess { room = it; transcript = emptyList() }
                                        .onFailure { error = it.message }
                                }
                            }
                        }) {
                            Text("$tTopic · $tChannel", color = Qrme.BrandA,
                                fontSize = 11.sp)
                        }
                    }
                }
            }
        } else {
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text(current.topic, color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
                    TextButton(onClick = { room = null; transcript = emptyList() }) {
                        Text(L10n.t("nc.leave", vm.language), color = Qrme.Red, fontSize = 12.sp)
                    }
                }
                transcript.forEach { m ->
                    Column(
                        Modifier.fillMaxWidth().clip(RoundedCornerShape(12.dp))
                            .background(Qrme.Card.copy(alpha = 0.9f))
                            .padding(horizontal = 12.dp, vertical = 8.dp),
                    ) {
                        Text(m.from, fontSize = 10.sp, fontWeight = FontWeight.Bold,
                            color = if (m.senderKind == "profile") Qrme.BrandA else Qrme.T2)
                        Text(m.content ?: "· blocked by moderation ·",
                            color = if (m.content == null) Qrme.T3 else Qrme.Txt, fontSize = 13.sp)
                    }
                }
                labeledField("", draft, L10n.t("nc.say.ph", vm.language)) { draft = it }
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    SmallAction(L10n.t("nc.send", vm.language)) {
                        val text = draft
                        if (text.isNotBlank() && !busy) {
                            draft = ""; busy = true; error = null
                            withInteractor(vm, { error = it; busy = false }) { me ->
                                vm.call({ ApiClient.roomMessage(
                                    current.id, me, text,
                                    vm.interactorToken ?: "") }) { r ->
                                    busy = false
                                    r.onFailure { error = it.message }
                                    reload(current.id)
                                }
                            }
                        }
                    }
                    SmallAction(L10n.t("nc.lettalk", vm.language)) {
                        if (!busy) {
                            busy = true; error = null
                            vm.call({ ApiClient.roomAdvance(
                                current.id, vm.interactorToken ?: "") }) { r ->
                                busy = false
                                r.onFailure { error = it.message }
                                reload(current.id)
                            }
                        }
                    }
                }
            }
        }
        error?.let { Text(it, color = Qrme.Red, fontSize = 13.sp) }
    }
}

// ---- Manage (General · Summon · Market · License behind one tab) ----

@Composable
fun ManageScreen(vm: StudioViewModel) {
    var seg by remember { mutableIntStateOf(0) }
    Column(Modifier.fillMaxSize()) {
        ScrollableTabRow(selectedTabIndex = seg, containerColor = Qrme.Card,
            contentColor = Qrme.BrandA, edgePadding = 0.dp) {
            listOf("nmg.t.general", "nmg.t.summon", "nmg.t.market", "nmg.t.packs", "tab.gaming", "nmg.t.license", "nmg.t.earn", "nsig.sign", "nmg.t.voice", "nmg.t.desk", "nmg.t.shop", "nmg.t.corner", "nmg.t.people", "nmg.t.counter", "nmg.t.trade", "nmg.t.deals").forEachIndexed { i, t ->
                Tab(selected = seg == i, onClick = { seg = i },
                    text = { Text(L10n.t(t, vm.language), fontSize = 12.sp) })
            }
        }
        Box(Modifier.weight(1f)) {
            when (seg) {
                0 -> SettingsScreen(vm)
                1 -> SummonPanel(vm)
                2 -> MarketPanel(vm)
                3 -> PacksPanel(vm)
                4 -> GamingPanel(vm)
                5 -> LicensePanel(vm)
                6 -> EarningsPanel(vm)
                7 -> SignaturePanel(vm)
                8 -> VoicePanel(vm)
                9 -> DeskPanel(vm)
                10 -> ShopPanel(vm)
                11 -> CornerPanel(vm)
                12 -> PeoplePanel(vm)
                13 -> CounterPanel(vm)
                14 -> TradePanel(vm)
                else -> DealsPanel(vm)
            }
        }
    }
}

// ---- Earnings: the creator's statement over the ledger ----

@Composable
private fun EarningsPanel(vm: StudioViewModel) {
    var statement by remember { mutableStateOf<EarningsStatement?>(null) }
    var receipt by remember { mutableStateOf<PayoutReceipt?>(null) }
    var error by remember { mutableStateOf<String?>(null) }

    fun money(v: Double, c: String) =
        (if (c == "USD") "$" else "$c ") + "%.2f".format(v)

    fun reload() {
        vm.call({ ApiClient.earnings(vm.pid!!, vm.token!!) }) { r ->
            statement = r.getOrNull()
        }
    }
    LaunchedEffect(Unit) { reload() }

    screenScroll {
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("nmg.earnings", vm.language), color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            Text(L10n.t("nmg.earnings.sub", vm.language),
                color = Qrme.T2, fontSize = 12.sp)
            statement?.let { s ->
                Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                    listOf(Triple("Accrued", s.accrued, Qrme.Green),
                           Triple("Paid", s.paid, Qrme.T2),
                           Triple(L10n.t("nmg.lifetime", vm.language), s.lifetime, Qrme.BrandA)).forEach { (l, v, c) ->
                        Column {
                            Text(money(v, s.currency), color = c, fontSize = 15.sp,
                                fontWeight = FontWeight.Bold)
                            Text(l, color = Qrme.T2, fontSize = 10.sp)
                        }
                    }
                }
                if (s.byKind.isNotEmpty())
                    Text(s.byKind.entries.sortedBy { it.key }
                        .joinToString(" · ") { "${it.key.replace('_', ' ')}: ${money(it.value, s.currency)}" },
                        color = Qrme.T3, fontSize = 10.sp)
                BrandButton(L10n.t("nmg.payout.request", vm.language), enabled = s.accrued > 0) {
                    error = null
                    vm.call({ ApiClient.requestPayout(vm.pid!!, vm.token!!) }) { r ->
                        r.onSuccess { receipt = it; reload() }
                         .onFailure { error = it.message }
                    }
                }
                receipt?.let {
                    Text(L10n.fill("nmg.payout.done", vm.language,
                             mapOf("id" to it.payoutId,
                                   "total" to money(it.totalAmount, s.currency),
                                   "n" to "${it.entries}")),
                        color = Qrme.Green, fontSize = 12.sp)
                }
            } ?: CircularProgressIndicator(color = Qrme.BrandA, modifier = Modifier.size(22.dp))
        }
        statement?.takeIf { it.entries.isNotEmpty() }?.let { s ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text(L10n.t("nmg.ledger", vm.language), color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
                s.entries.take(20).forEach { e ->
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                        Column(Modifier.weight(1f)) {
                            Text(e.kind.replace('_', ' '), color = Qrme.Txt, fontSize = 12.sp,
                                fontWeight = FontWeight.Bold)
                            e.memo?.let { Text(it, color = Qrme.T3, fontSize = 10.sp, maxLines = 1) }
                        }
                        Column(horizontalAlignment = Alignment.End) {
                            Text(money(e.amount, s.currency),
                                color = if (e.status == "paid") Qrme.T2 else Qrme.Green,
                                fontSize = 12.sp, fontWeight = FontWeight.Bold)
                            Text(e.status, color = Qrme.T3, fontSize = 10.sp)
                        }
                    }
                }
            }
        }
        error?.let { Text(it, color = Qrme.Red, fontSize = 13.sp) }
    }
}

@Composable
private fun GamingPanel(vm: StudioViewModel) {
    val platforms = listOf("playstation", "xbox", "nintendo", "steam", "pc")
    val roles = listOf("companion", "teammate", "practice_partner")
    var platform by remember { mutableStateOf("xbox") }
    var role by remember { mutableStateOf("teammate") }
    var game by remember { mutableStateOf("") }
    var sessions by remember { mutableStateOf<List<GameSession>>(emptyList()) }
    var openSession by remember { mutableStateOf<String?>(null) }
    var situation by remember { mutableStateOf("") }
    var minorPresent by remember { mutableStateOf(false) }
    var lastLine by remember { mutableStateOf<GameCalloutResult?>(null) }
    var error by remember { mutableStateOf<String?>(null) }

    fun reload() {
        vm.call({ ApiClient.gameSessions(vm.pid!!, vm.token!!) }) { r ->
            sessions = r.getOrDefault(emptyList())
        }
    }
    LaunchedEffect(Unit) { reload() }

    screenScroll {
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("ngam", vm.language), color = Qrme.Txt, fontSize = 16.sp,
                fontWeight = FontWeight.Bold)
            Text(L10n.t("ngam.sub", vm.language),
                color = Qrme.T2, fontSize = 12.sp)
            Text(L10n.t("ngam.platform", vm.language), color = Qrme.T3, fontSize = 11.sp)
            Row(Modifier.horizontalScroll(rememberScrollState()),
                horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                platforms.forEach { p ->
                    val on = platform == p
                    Text(p, color = if (on) Color.White else Qrme.Txt, fontSize = 11.sp,
                        modifier = Modifier.clip(RoundedCornerShape(50))
                            .background(if (on) Qrme.BrandA else Qrme.ScrBot)
                            .clickable { platform = p }
                            .padding(horizontal = 10.dp, vertical = 6.dp))
                }
            }
            Row(Modifier.horizontalScroll(rememberScrollState()),
                horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                roles.forEach { rl ->
                    val on = role == rl
                    Text(rl.replace("_", " "),
                        color = if (on) Color.White else Qrme.Txt, fontSize = 11.sp,
                        modifier = Modifier.clip(RoundedCornerShape(50))
                            .background(if (on) Qrme.BrandA else Qrme.ScrBot)
                            .clickable { role = rl }
                            .padding(horizontal = 10.dp, vertical = 6.dp))
                }
            }
            labeledField(L10n.t("ngam.game", vm.language), game, L10n.t("ngam.game.ph", vm.language)) { game = it }
            SmallAction(L10n.t("ngam.start", vm.language)) {
                if (game.isNotBlank()) {
                    error = null
                    vm.call({ ApiClient.startGameSession(vm.pid!!, vm.token!!,
                        platform, game, role) }) { r ->
                        r.onSuccess { game = "" }.onFailure { error = it.message }
                        reload()
                    }
                }
            }
        }
        error?.let { Text(it, color = Qrme.Red, fontSize = 13.sp) }

        sessions.forEach { s ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text("${s.game} · ${s.platform}", color = Qrme.Txt,
                        fontSize = 14.sp, fontWeight = FontWeight.Bold)
                    Text(s.status.uppercase(),
                        color = if (s.status == "active") Qrme.Green else Qrme.T3,
                        fontSize = 11.sp, fontWeight = FontWeight.Bold)
                }
                Text(L10n.fill("ngam.session", vm.language,
                    mapOf("role" to s.role.replace("_", " "), "n" to "${s.callouts}")),
                    color = Qrme.T2, fontSize = 11.sp)
                if (s.status == "active") {
                    if (openSession == s.id) {
                        labeledField(L10n.t("ngam.situation", vm.language), situation,
                            L10n.t("ngam.situation.example", vm.language)) { situation = it }
                        Row(Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically) {
                            Text(L10n.t("ngam.minor", vm.language),
                                color = Qrme.T2, fontSize = 11.sp)
                            Switch(checked = minorPresent,
                                onCheckedChange = { minorPresent = it })
                        }
                        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            SmallAction(L10n.t("ngam.callit", vm.language)) {
                                if (situation.isNotBlank())
                                    vm.call({ ApiClient.gameCallout(s.id, vm.token!!,
                                        situation, minorPresent) }) { r ->
                                        lastLine = r.getOrNull(); reload()
                                    }
                            }
                            TextButton(onClick = {
                                vm.call({ ApiClient.endGameSession(s.id, vm.token!!) }) {
                                    openSession = null; reload()
                                }
                            }) { Text(L10n.t("ngam.end", vm.language), color = Qrme.Red, fontSize = 12.sp) }
                        }
                        lastLine?.let { l ->
                            if (l.status == "spoken" && l.line != null)
                                Text("🎙 ${l.line}", color = Qrme.Green, fontSize = 12.sp)
                            else Text(L10n.fill("ngam.held", vm.language, mapOf("reason" to
                                    (l.flagReason ?: L10n.t("ngam.held.default", vm.language)))),
                                color = Qrme.Amber, fontSize = 11.sp)
                        }
                    } else {
                        TextButton(onClick = { openSession = s.id; lastLine = null }) {
                            Text(L10n.t("nmg.open", vm.language), color = Qrme.BrandA, fontSize = 12.sp)
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun SummonPanel(vm: StudioViewModel) {
    var handle by remember { mutableStateOf("") }
    var claimed by remember { mutableStateOf<String?>(null) }
    var label by remember { mutableStateOf("") }
    var location by remember { mutableStateOf("") }
    var beacons by remember { mutableStateOf<List<Beacon>>(emptyList()) }
    var lastQr by remember { mutableStateOf<String?>(null) }
    var ref by remember { mutableStateOf("") }
    var found by remember { mutableStateOf<SummonResult?>(null) }
    var error by remember { mutableStateOf<String?>(null) }
    var scanning by remember { mutableStateOf(false) }
    val uriHandler = LocalUriHandler.current
    fun reload() { vm.call({ ApiClient.beacons(vm.pid!!) }) { r -> beacons = r.getOrDefault(emptyList()) } }
    LaunchedEffect(Unit) { reload() }

    if (scanning) {
        BeaconScannerScreen(
            onOpen = { url -> scanning = false; runCatching { uriHandler.openUri(url) } },
            onClose = { scanning = false }, lang = vm.language)
        return
    }

    screenScroll {
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("nmg.handle", vm.language), color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            Text(L10n.t("nmg.handle.sub", vm.language), color = Qrme.T2, fontSize = 12.sp)
            labeledField(L10n.t("nmg.f.handle", vm.language), handle, L10n.t("nmg.handle.example", vm.language)) { handle = it }
            SmallAction(L10n.t("nmg.claim", vm.language)) {
                if (handle.isNotBlank()) {
                    error = null
                    vm.call({ ApiClient.claimHandle(vm.pid!!, handle,
                        vm.token.orEmpty()) }) { r ->
                        r.onSuccess { claimed = it; handle = "" }
                            .onFailure { error = it.message }
                    }
                }
            }
            claimed?.let { Text(L10n.fill("nmg.claimed", vm.language, mapOf("handle" to it)), color = Qrme.Green, fontSize = 12.sp) }
        }

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("nmg.beacons", vm.language), color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            Text(L10n.t("nmg.beacons.sub", vm.language),
                color = Qrme.T2, fontSize = 12.sp)
            labeledField(L10n.t("ns.wm.label", vm.language), label, L10n.t("nmg.beacon.label.example", vm.language)) { label = it }
            labeledField(L10n.t("nmg.h.location", vm.language), location, L10n.t("nmg.location.example", vm.language)) { location = it }
            SmallAction(L10n.t("nmg.beacon.place", vm.language)) {
                if (label.isNotBlank()) {
                    error = null
                    vm.call({ ApiClient.placeBeacon(vm.pid!!, label, location) }) { r ->
                        r.onSuccess { lastQr = it.qrSvg; label = ""; location = "" }
                            .onFailure { error = it.message }
                        reload()
                    }
                }
            }
            lastQr?.let { Text(L10n.fill("nmg.qr", vm.language, mapOf("svg" to it)), color = Qrme.T3, fontSize = 10.sp) }
        }

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("nmg.beacon.scan", vm.language), color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            Text(L10n.t("nmg.beacon.scan.sub", vm.language),
                color = Qrme.T2, fontSize = 12.sp)
            SmallAction(L10n.t("nmg.beacon.scan.go", vm.language)) { scanning = true }
        }

        beacons.forEach { b ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text(b.label, color = Qrme.Txt, fontSize = 14.sp, fontWeight = FontWeight.Bold)
                    if (b.active) {
                        TextButton(onClick = {
                            vm.call({ ApiClient.pickUpBeacon(b.id) }) { reload() }
                        }) { Text(L10n.t("nmg.beacon.pickup", vm.language), color = Qrme.Red, fontSize = 12.sp) }
                    } else Text(L10n.t("nmg.beacon.pickedup", vm.language), color = Qrme.T3, fontSize = 12.sp)
                }
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text(b.location ?: "", color = Qrme.T2, fontSize = 12.sp)
                    Text(L10n.fill("nmg.beacon.scans", vm.language, mapOf("n" to "${b.scans}")), color = Qrme.T3, fontSize = 12.sp)
                }
            }
        }

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("nmg.trysummon", vm.language), color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            labeledField(L10n.t("nmg.summon.ref", vm.language), ref, L10n.t("nmg.summon.ph", vm.language)) { ref = it }
            SmallAction(L10n.t("nmg.t.summon", vm.language)) {
                if (ref.isNotBlank()) {
                    error = null; found = null
                    vm.call({ ApiClient.summon(ref) }) { r ->
                        r.onSuccess { found = it }.onFailure { error = it.message }
                    }
                }
            }
            found?.let { f ->
                f.cards.forEach { c ->
                    Column {
                        Text(c.displayName, color = Qrme.Txt, fontSize = 13.sp,
                            fontWeight = FontWeight.Bold)
                        c.handle?.let { Text(it, color = Qrme.BrandA, fontSize = 11.sp) }
                        Text(c.status, color = Qrme.T2, fontSize = 11.sp)
                        c.note?.let { Text(it, color = Qrme.T3, fontSize = 10.sp) }
                    }
                }
                if (f.type == "beacon")
                    Text(L10n.fill("nmg.found.beacon", vm.language,
                            mapOf("label" to (f.label ?: ""), "n" to "${f.scans ?: 0}")),
                        color = Qrme.T2, fontSize = 11.sp)
            }
        }
        error?.let { Text(it, color = Qrme.Red, fontSize = 13.sp) }
    }
}

// Quick-browse tags: the wellbeing starters first, then popular areas.
private val QUICK_TAGS = listOf("mental-health", "mood", "relationships",
    "healthcare", "finance", "fitness", "food")

@Composable
private fun MarketPanel(vm: StudioViewModel) {
    var title by remember { mutableStateOf("") }
    var blurb by remember { mutableStateOf("") }
    var tags by remember { mutableStateOf("") }
    var filterTag by remember { mutableStateOf("") }
    var listings by remember { mutableStateOf<List<Listing>>(emptyList()) }
    var status by remember { mutableStateOf<String?>(null) }
    var error by remember { mutableStateOf<String?>(null) }
    fun reload() { vm.call({ ApiClient.listings(filterTag) }) { r -> listings = r.getOrDefault(emptyList()) } }
    LaunchedEffect(Unit) { reload() }

    screenScroll {
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("nmg.list", vm.language), color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            Text(L10n.t("nmg.list.sub", vm.language),
                color = Qrme.T2, fontSize = 12.sp)
            labeledField(L10n.t("nmg.h.title", vm.language), title, L10n.t("nmg.title.example", vm.language)) { title = it }
            labeledField(L10n.t("nmg.h.blurb", vm.language), blurb, L10n.t("nmg.blurb.ph", vm.language)) { blurb = it }
            labeledField(L10n.t("nmg.h.tags", vm.language), tags, L10n.t("nmg.tags.example", vm.language)) { tags = it }
            SmallAction(L10n.t("nmg.create", vm.language)) {
                if (title.isNotBlank()) {
                    error = null; status = null
                    val tagList = tags.split(",").map { it.trim() }.filter { it.isNotEmpty() }
                    vm.call({ ApiClient.createListing(title, blurb, tagList,
                        vm.displayName, vm.pid!!) }) { r ->
                        r.onSuccess { status = "listed — summonable by tag"; title = ""; blurb = ""; tags = "" }
                            .onFailure { error = it.message }
                        reload()
                    }
                }
            }
        }
        error?.let { Text(it, color = Qrme.Red, fontSize = 13.sp) }
        status?.let { Text(it, color = Qrme.Green, fontSize = 12.sp) }

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("nmg.wellbeing.head", vm.language), color = Qrme.Txt, fontSize = 14.sp,
                fontWeight = FontWeight.Bold)
            Row(Modifier.horizontalScroll(rememberScrollState()),
                horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                QUICK_TAGS.forEach { tag ->
                    val selected = filterTag == tag
                    Text("#$tag",
                        color = if (selected) Color.White else Qrme.Txt,
                        fontSize = 12.sp,
                        modifier = Modifier
                            .clip(RoundedCornerShape(50))
                            .background(if (selected) Qrme.BrandA else Qrme.ScrBot)
                            .clickable { filterTag = tag; reload() }
                            .padding(horizontal = 10.dp, vertical = 6.dp))
                }
            }
            Text(L10n.t("nmg.wellbeing", vm.language),
                color = Qrme.T3, fontSize = 10.sp)
        }

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            labeledField(L10n.t("nmg.f.tag", vm.language), filterTag, L10n.t("nmg.filter.tag.example", vm.language)) { filterTag = it }
            SmallAction(L10n.t("nmg.browse", vm.language)) { reload() }
        }

        listings.forEach { l ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text(l.title, color = Qrme.Txt, fontSize = 14.sp, fontWeight = FontWeight.Bold)
                    Text(l.kind, color = Qrme.BrandA, fontSize = 12.sp)
                }
                l.blurb?.let { Text(it, color = Qrme.T2, fontSize = 12.sp) }
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically) {
                    Text(l.tags.joinToString(" ") { "#$it" }, color = Qrme.T3, fontSize = 11.sp)
                    if (l.profileId == vm.pid) {
                        TextButton(onClick = {
                            vm.call({ ApiClient.removeListing(l.id) }) { reload() }
                        }) { Text(L10n.t("nmg.remove", vm.language), color = Qrme.Red, fontSize = 12.sp) }
                    }
                }
            }
        }
    }
}

@Composable
private fun PacksPanel(vm: StudioViewModel) {
    var industry by remember { mutableStateOf("") }
    var catalog by remember { mutableStateOf<List<Pack>>(emptyList()) }
    var registries by remember { mutableStateOf<List<PackRegistry>>(emptyList()) }
    // pack id -> robot id ("" when installed on the profile itself)
    var installed by remember { mutableStateOf<Map<String, String>>(emptyMap()) }
    var status by remember { mutableStateOf<String?>(null) }
    var error by remember { mutableStateOf<String?>(null) }

    fun reload() {
        vm.call({ ApiClient.packRegistries() }) { r ->
            registries = r.getOrDefault(emptyList())
        }
        vm.call({ ApiClient.packs(industry.trim()) }) { r ->
            catalog = r.getOrDefault(emptyList())
        }
        vm.call({ ApiClient.installedPacks(vm.pid!!, vm.token!!) }) { r ->
            installed = r.getOrDefault(emptyList()).associate { it.id to it.robotId }
        }
    }

    fun install(p: Pack) {
        error = null; status = null
        vm.call({
            // Robot task packs install onto the profile's bound body.
            val robotId = if (p.audience == "robot") {
                ApiClient.robots(vm.pid!!, vm.token!!).firstOrNull()?.id
                    ?: throw IllegalStateException(
                        "bind a robot first (Robots tab) — task packs install onto a body")
            } else null
            // Tapping the priced button is the accept_price consent.
            ApiClient.installPack(p.id, vm.pid!!, vm.token!!, !p.free, robotId)
        }) { r ->
            r.onSuccess {
                status = if (p.audience == "robot")
                    L10n.t("nmg.pack.installed.robot", vm.language)
                else L10n.t("nmg.pack.installed.pack", vm.language)
            }.onFailure { error = it.message }
            reload()
        }
    }

    fun uninstall(p: Pack) {
        val robotId = installed[p.id].orEmpty()
        vm.call({
            if (robotId.isNotEmpty())
                ApiClient.uninstallRobotPack(p.id, robotId, vm.token!!)
            else ApiClient.uninstallPack(p.id, vm.pid!!, vm.token!!)
        }) {
            status = if (robotId.isNotEmpty())
                "removed — the body's tasks were revoked"
            else "removed — the knowledge base shrank back"
            reload()
        }
    }
    LaunchedEffect(Unit) { reload() }

    screenScroll {
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("nmg.packs", vm.language), color = Qrme.Txt, fontSize = 16.sp,
                fontWeight = FontWeight.Bold)
            Text(L10n.t("nmg.packs.sub", vm.language),
                color = Qrme.T2, fontSize = 12.sp)
            labeledField(L10n.t("nmg.f.industry", vm.language), industry, L10n.t("nmg.filter.industry.example", vm.language)) { industry = it }
            SmallAction(L10n.t("nmg.browse", vm.language)) { reload() }
        }
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("nmg.packs.sources", vm.language), color = Qrme.Txt, fontSize = 14.sp,
                fontWeight = FontWeight.Bold)
            Text(L10n.t("nmg.packs.sources.sub", vm.language),
                color = Qrme.T3, fontSize = 10.sp)
            registries.forEach { reg ->
                Row(Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically) {
                    Column(Modifier.weight(1f)) {
                        Text(reg.name, color = Qrme.BrandA, fontSize = 12.sp,
                            fontWeight = FontWeight.Bold)
                        Text(reg.tagline, color = Qrme.T2, fontSize = 10.sp)
                        Text(L10n.fill("nmg.packs.count", vm.language,
                    mapOf("synced" to "${reg.synced}", "available" to "${reg.availablePacks}")),
                            color = Qrme.T3, fontSize = 10.sp)
                    }
                    if (reg.synced >= reg.availablePacks)
                        Text(L10n.t("nmg.packs.synced", vm.language), color = Qrme.Green, fontSize = 12.sp,
                            fontWeight = FontWeight.Bold)
                    else SmallAction(L10n.t("nmg.packs.sync", vm.language)) {
                        vm.call({ ApiClient.syncRegistry(reg.key) }) {
                            status = "${reg.name} synced — its packs joined the marketplace"
                            reload()
                        }
                    }
                }
            }
        }

        error?.let { Text(it, color = Qrme.Red, fontSize = 13.sp) }
        status?.let { Text(it, color = Qrme.Green, fontSize = 12.sp) }

        catalog.forEach { p ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text(p.title, color = Qrme.Txt, fontSize = 14.sp,
                        fontWeight = FontWeight.Bold)
                    Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                        if (p.audience == "robot")
                            Text(L10n.t("nmg.pack.robot.tasks", vm.language), color = Qrme.BrandA, fontSize = 11.sp,
                                fontWeight = FontWeight.Bold)
                        Text(if (p.free) L10n.t("nmg.pack.free", vm.language)
                             else "%.2f %s".format(p.price, p.currency),
                            color = if (p.free) Qrme.Green else Qrme.Amber,
                            fontSize = 12.sp, fontWeight = FontWeight.Bold)
                    }
                }
                p.blurb?.let { Text(it, color = Qrme.T2, fontSize = 12.sp) }
                Text(L10n.fill("nmg.pack.meta", vm.language,
                            mapOf("industry" to p.industry, "items" to "${p.items}",
                                  "installs" to "${p.installs}", "publisher" to p.publisher)),
                    color = Qrme.T3, fontSize = 11.sp)
                p.originUrl?.let {
                    Text(L10n.fill("nmg.pack.from", vm.language, mapOf("source" to it)), color = Qrme.BrandA, fontSize = 10.sp)
                }
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.End,
                    verticalAlignment = Alignment.CenterVertically) {
                    if (p.id in installed) {
                        Text(L10n.t("nmg.packs.installed", vm.language), color = Qrme.Green, fontSize = 12.sp,
                            fontWeight = FontWeight.Bold)
                        TextButton(onClick = { uninstall(p) }) {
                            Text(L10n.t("nmg.remove", vm.language), color = Qrme.Red, fontSize = 12.sp)
                        }
                    } else {
                        SmallAction(if (p.free) L10n.t("nmg.packs.download", vm.language)
                                    else L10n.fill("nmg.packs.buy", vm.language,
                                                   mapOf("price" to "%.2f".format(p.price),
                                                         "currency" to p.currency))) {
                            install(p)
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun LicensePanel(vm: StudioViewModel) {
    val kinds = listOf("consult", "finetune", "clone")
    var kind by remember { mutableStateOf(kinds.first()) }
    var price by remember { mutableStateOf("") }
    var terms by remember { mutableStateOf("") }
    var offer by remember { mutableStateOf<LicenseOffer?>(null) }
    var grants by remember { mutableStateOf<List<LicenseGrant>>(emptyList()) }
    var error by remember { mutableStateOf<String?>(null) }
    fun reload() {
        vm.call({ ApiClient.license(vm.pid!!) }) { r -> offer = r.getOrNull() }
        vm.call({ ApiClient.licenseGrants(vm.pid!!, vm.token!!) }) { r -> grants = r.getOrDefault(emptyList()) }
    }
    LaunchedEffect(Unit) { reload() }

    screenScroll {
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("nmg.license", vm.language), color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            Text(L10n.t("nmg.license.sub", vm.language),
                color = Qrme.T2, fontSize = 12.sp)
            Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                kinds.forEach { k ->
                    FilterChip(
                        selected = kind == k, onClick = { kind = k },
                        label = { Text(k, fontSize = 11.sp) },
                        colors = FilterChipDefaults.filterChipColors(
                            selectedContainerColor = Qrme.BrandA,
                            selectedLabelColor = Color.White, labelColor = Qrme.T2,
                        ),
                    )
                }
            }
            labeledField(L10n.t("nmg.h.price", vm.language), price, "0") { price = it }
            labeledField(L10n.t("nmg.h.terms", vm.language), terms, L10n.t("nmg.terms.example", vm.language)) { terms = it }
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalAlignment = Alignment.CenterVertically) {
                SmallAction(L10n.t("nmg.setoffer", vm.language)) {
                    error = null
                    vm.call({ ApiClient.setLicense(vm.pid!!, vm.token!!, kind,
                        price.toDoubleOrNull() ?: 0.0, terms) }) { r ->
                        r.onSuccess { offer = it }.onFailure { error = it.message }
                    }
                }
                if (offer != null) {
                    TextButton(onClick = {
                        vm.call({ ApiClient.unlistLicense(vm.pid!!, vm.token!!) }) {
                            offer = null
                        }
                    }) { Text(L10n.t("nmg.unlist", vm.language), color = Qrme.Red, fontSize = 12.sp) }
                }
            }
            offer?.let {
                Text(L10n.fill(if (it.allowDerivatives) "nmg.offered.derivatives"
                               else "nmg.offered", vm.language,
                        mapOf("kind" to it.kind, "currency" to it.currency,
                              "price" to "${it.price}")),
                    color = Qrme.Green, fontSize = 12.sp)
            }
        }
        error?.let { Text(it, color = Qrme.Red, fontSize = 13.sp) }

        grants.forEach { g ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically) {
                    Text("${g.kind} → ${g.buyerId}", color = Qrme.Txt, fontSize = 13.sp,
                        fontWeight = FontWeight.Bold)
                    if (g.revoked) Text(L10n.t("nmg.revoked", vm.language), color = Qrme.Red, fontSize = 12.sp)
                    else TextButton(onClick = {
                        vm.call({ ApiClient.revokeLicense(g.id, vm.token!!) }) { reload() }
                    }) { Text(L10n.t("nmg.revoke", vm.language), color = Qrme.Red, fontSize = 12.sp) }
                }
                g.derivedProfileId?.let {
                    Text(L10n.fill("nmg.derived", vm.language, mapOf("id" to it)), color = Qrme.T2, fontSize = 11.sp)
                }
                g.manifest?.let { m ->
                    Text(L10n.t("nmg.manifest.carried", vm.language)
                            + ": " + m.carried.joinToString(", "),
                        color = Qrme.T2, fontSize = 11.sp)
                    Text(L10n.t("nmg.manifest.withheld", vm.language)
                            + ": " + m.withholdings.joinToString(", ") { it.item },
                        color = Qrme.T2, fontSize = 11.sp)
                }
            }
        }
    }
}

@Composable
private fun ProvenanceFooter(p: Provenance, lang: String) {
    Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
        HorizontalDivider(color = Qrme.Line)
        Text(L10n.fill("nprv.generated", lang,
                mapOf("model" to p.generatedBy, "n" to "${p.sourceItems}",
                      "status" to p.moderationStatus)),
            color = Qrme.T2, fontSize = 10.sp)
        p.licensedFrom?.let {
            Text(L10n.fill("nprv.licensed", lang, mapOf("source" to it)), color = Qrme.Amber, fontSize = 10.sp)
        }
        Text(p.disclaimer, color = Qrme.T3, fontSize = 10.sp)
    }
}


// ---- Signatures: a passkey assertion instead of the app's own say-so ----

/**
 * Enrol a passkey, then sign a document with it.
 *
 * Built around the one thing WebAuthn cannot do: it has no trusted display, so
 * the system prompt can never say what is being signed. The document is shown
 * here in full and the button under it is the last thing touched before the
 * prompt, and the server stores that exact text — so a dispute reproduces the
 * screen rather than arguing about it.
 */
@Composable
private fun SignaturePanel(vm: StudioViewModel) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    var credentials by remember { mutableStateOf<List<SigningCredential>>(emptyList()) }
    var document by remember { mutableStateOf("") }
    // `meaning` is free text the server stores as given (max 300), so the
    // default belongs in the reader's language: somebody signs in the words
    // they would use, not in the ones this app happens to be written in.
    var meaning by remember { mutableStateOf(L10n.t("nsig.attest", vm.language)) }
    var receipt by remember { mutableStateOf<SignatureReceipt?>(null) }
    var error by remember { mutableStateOf<String?>(null) }
    var busy by remember { mutableStateOf(false) }

    fun reload() {
        val token = vm.token ?: return
        vm.call({ ApiClient.signingCredentials(token) }) { r ->
            credentials = r.getOrDefault(emptyList())
        }
    }
    LaunchedEffect(Unit) { reload() }

    screenScroll {
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("nsig.creds", vm.language), color = Qrme.Txt, fontSize = 16.sp,
                fontWeight = FontWeight.Bold)
            if (credentials.isEmpty()) {
                Text(L10n.t("nsig.none", vm.language),
                    color = Qrme.T2, fontSize = 12.sp)
            }
            credentials.forEach { c ->
                Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                    Text(c.displayName ?: c.credentialId, color = Qrme.Txt,
                        fontSize = 13.sp, fontWeight = FontWeight.Bold)
                    Text(L10n.fill("nsig.proofing", vm.language, mapOf("level" to
                            L10n.t("nsig.level.${c.proofingLevel}", vm.language))),
                        color = Qrme.T2, fontSize = 11.sp)
                    // Surfaced rather than buried: a syncable passkey lives on
                    // every device in the user's cloud account, which is a
                    // weaker claim that only they could have signed.
                    Text(
                        L10n.t(if (c.deviceBound) "nsig.devicebound"
                               else "nsig.syncable", vm.language),
                        color = if (c.deviceBound) Qrme.Green else Qrme.Red,
                        fontSize = 11.sp)
                    Text(L10n.fill("nsig.cansign", vm.language, mapOf("levels" to
                            c.canSign.joinToString(", ") { L10n.t("nsig.level.$it", vm.language) })),
                        color = Qrme.T3, fontSize = 10.sp)
                }
            }
            SmallAction(L10n.t("nsig.enrol", vm.language)) {
                val token = vm.token ?: return@SmallAction
                error = null; busy = true
                scope.launch {
                    runCatching {
                        val o = ApiClient.enrollOptions("QRME owner", token)
                        val reg = Signing.register(context, o.rpId, o.rpName,
                            o.challenge, o.userId, o.userName, o.displayName)
                        ApiClient.enrollCredential(reg.credentialId,
                            reg.attestationObject, reg.clientDataJson,
                            o.challenge, "self_asserted", o.displayName, token)
                    }.onFailure { error = it.message }
                    busy = false
                    reload()
                }
            }
        }

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("nsig.signing", vm.language), color = Qrme.Txt, fontSize = 16.sp,
                fontWeight = FontWeight.Bold)
            labeledField(L10n.t("nsig.doc", vm.language), document, "") { document = it }
            labeledField(L10n.t("nsig.means", vm.language), meaning, "") { meaning = it }
            Text(L10n.t("nsig.hashed", vm.language) + " " + L10n.t("nsig.tiers", vm.language),
                color = Qrme.T3, fontSize = 11.sp)
            SmallAction(if (busy) "Working…" else "Sign") {
                val token = vm.token ?: return@SmallAction
                if (document.isBlank() || busy) return@SmallAction
                error = null; busy = true; receipt = null
                scope.launch {
                    runCatching {
                        val env = ApiClient.requestSignature(document, meaning,
                            // `basic` is what a self-asserted credential can
                            // sign, and self-asserted is all this panel can
                            // enrol. Asking for `standard` shipped a happy
                            // path that always failed at the server.
                            document, "basic", "profile", vm.pid, token)
                        val rpId = ApiClient.base.substringAfter("://")
                            .substringBefore("/").substringBefore(":")
                        val a = Signing.assert(context, rpId, env.challenge)
                        ApiClient.submitSignature(env.envelopeId, a, token)
                    }.onSuccess { receipt = it }
                        .onFailure { error = it.message }
                    busy = false
                }
            }
        }

        receipt?.let { r ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Text(L10n.t(if (r.valid) "nsig.verifies" else "nsig.noverify", vm.language),
                    color = if (r.valid) Qrme.Green else Qrme.Red,
                    fontSize = 14.sp, fontWeight = FontWeight.Bold)
                Text(r.signatureId, color = Qrme.T2, fontSize = 11.sp)
                Text(r.signedAt, color = Qrme.T3, fontSize = 11.sp)
                // The guarantee never travels without them.
                r.limits.forEach {
                    Text("• $it", color = Qrme.T3, fontSize = 10.sp)
                }
            }
        }

        Text(L10n.t("nsig.domain.android", vm.language),
            color = Qrme.T3, fontSize = 11.sp)
        error?.let { Text(it, color = Qrme.Red, fontSize = 13.sp) }
    }
}


// ---- Voice: the owner's own voice, enrolled from the device with the mic ----

/**
 * Gate [VoiceScreen] on there being a profile to own the voiceprint. Only the
 * owner may enroll one, so an ownerless shell has nothing to show here.
 */
@Composable
private fun VoicePanel(vm: StudioViewModel) {
    if (vm.pid == null || vm.token == null) {
        screenScroll {
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(L10n.t("nmg.needprofile", vm.language), color = Qrme.Txt, fontSize = 16.sp,
                    fontWeight = FontWeight.Bold)
                Text(L10n.t("nvoi.needprofile", vm.language),
                    color = Qrme.T2, fontSize = 12.sp)
            }
        }
        return
    }
    VoiceScreen(vm)
}


// ---- Your corner: switches, messages, the homepage ----

// Strings through L10n; the server's refusal sentences — including the
// ones that name a switch — arrive in the reader's language and are
// shown verbatim.
@Composable
private fun CornerPanel(vm: StudioViewModel) {
    val lang = L10n.deviceLanguage()
    var flags by remember { mutableStateOf<Map<String, Boolean>>(emptyMap()) }
    var headline by remember { mutableStateOf("") }
    var about by remember { mutableStateOf("") }
    var bg by remember { mutableStateOf("#1a1333") }
    var accent by remember { mutableStateOf("#7b5cff") }
    var threads by remember { mutableStateOf<List<DmThread>>(emptyList()) }
    var withId by remember { mutableStateOf("") }
    var thread by remember { mutableStateOf<List<DmMessage>>(emptyList()) }
    var draft by remember { mutableStateOf("") }
    var note by remember { mutableStateOf<String?>(null) }

    fun reload() {
        vm.call({ ApiClient.homepage(vm.pid!!, vm.token) }) { r ->
            r.getOrNull()?.let { headline = it.headline; about = it.about
                bg = it.bg; accent = it.accent }
        }
        vm.call({ ApiClient.features(vm.pid!!, vm.token!!) }) { r ->
            flags = r.getOrDefault(emptyMap())
        }
        vm.call({ ApiClient.dmThreads(vm.pid!!, vm.token!!) }) { r ->
            threads = r.getOrDefault(emptyList())
        }
    }
    LaunchedEffect(Unit) { reload() }

    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("corner.title", lang), color = Qrme.Txt, fontSize = 16.sp,
                fontWeight = FontWeight.Bold)
            Text(L10n.t("corner.walls", lang), color = Qrme.T2, fontSize = 11.sp)
            labeledField(L10n.t("corner.headline", lang), headline, "") { headline = it }
            labeledField(L10n.t("corner.about", lang), about, "") { about = it }
            labeledField(L10n.t("corner.bg", lang), bg, "") { bg = it }
            labeledField(L10n.t("corner.accent", lang), accent, "") { accent = it }
            BrandButton(L10n.t("corner.save", lang)) {
                vm.call({ ApiClient.editHomepage(vm.pid!!, headline, about, bg,
                    accent, vm.token!!) }) { r ->
                    r.exceptionOrNull()?.let { note = it.message }
                }
            }
        }
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Text(L10n.t("corner.switches", lang), color = Qrme.Txt, fontSize = 14.sp,
                fontWeight = FontWeight.Bold)
            flags.entries.sortedBy { it.key }.forEach { (feature, on) ->
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Switch(checked = on, onCheckedChange = { next ->
                        vm.call({ ApiClient.setFeature(vm.pid!!, feature, next,
                            vm.token!!) }) { r -> flags = r.getOrDefault(flags) }
                    })
                    Text(cornerSwitchLabel(feature, lang), color = Qrme.T2,
                        fontSize = 12.sp)
                }
            }
        }
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Text(L10n.t("corner.messages", lang), color = Qrme.Txt, fontSize = 14.sp,
                fontWeight = FontWeight.Bold)
            Text(L10n.t("corner.friends_only", lang), color = Qrme.T2, fontSize = 11.sp)
            threads.forEach { t ->
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text(t.otherName ?: t.otherId, color = Qrme.Txt, fontSize = 12.sp)
                    TextButton(onClick = {
                        withId = t.otherId
                        vm.call({ ApiClient.dmThread(vm.pid!!, t.otherId, vm.token!!) }) { r ->
                            thread = r.getOrDefault(emptyList())
                        }
                    }) { Text(L10n.t("corner.open", lang), color = Qrme.BrandA, fontSize = 12.sp) }
                }
            }
            labeledField(L10n.t("corner.to", lang), withId, "") { withId = it }
            thread.forEach { m ->
                val line = (if (m.senderId == vm.pid) "→ " else "← ") + m.body
                Text(line, color = Qrme.T3, fontSize = 11.sp)
            }
            labeledField(L10n.t("corner.send", lang), draft, "") { draft = it }
            BrandButton(L10n.t("corner.send", lang),
                        enabled = draft.isNotBlank() && withId.isNotBlank()) {
                vm.call({ ApiClient.sendDm(vm.pid!!, withId, draft, vm.token!!) }) { r ->
                    r.exceptionOrNull()?.let { note = it.message }
                    draft = ""
                    vm.call({ ApiClient.dmThread(vm.pid!!, withId, vm.token!!) }) { t ->
                        thread = t.getOrDefault(emptyList())
                    }
                }
            }
        }
        note?.let { Text(it, color = Qrme.T2, fontSize = 12.sp) }
    }
}


// ---- The people around a profile: friends, the wall, comments ----
//
// Nine routes the backend has carried since the community round, with a
// door on every client but the phones. Three rules kept rather than
// invented: a pinned row gets no remove control (deletion refuses with
// 409 and the list says so); a blocked post or comment comes back to its
// author with its status, because the words were recorded; and a
// suggestion is shown with the reason the route returned for it.
@Composable
private fun PeoplePanel(vm: StudioViewModel) {
    val lang = L10n.deviceLanguage()
    var friends by remember { mutableStateOf<List<FriendRow>>(emptyList()) }
    var suggested by remember { mutableStateOf<List<SuggestedRow>>(emptyList()) }
    var posts by remember { mutableStateOf<List<WallPost>>(emptyList()) }
    var comments by remember { mutableStateOf<List<CommentRow>>(emptyList()) }
    var addId by remember { mutableStateOf("") }
    var draft by remember { mutableStateOf("") }
    var openPost by remember { mutableStateOf<String?>(null) }
    var commentDraft by remember { mutableStateOf("") }
    var note by remember { mutableStateOf<String?>(null) }
    var inboxPage by remember { mutableStateOf<InboxPage?>(null) }

    fun reload() {
        vm.call({ ApiClient.friends(vm.pid!!) }) { r ->
            friends = r.getOrDefault(emptyList()) }
        vm.call({ ApiClient.suggestedFriends(vm.pid!!) }) { r ->
            suggested = r.getOrDefault(emptyList()) }
        vm.call({ ApiClient.wall(vm.pid!!) }) { r ->
            posts = r.getOrDefault(emptyList()) }
        vm.call({ ApiClient.inbox(vm.pid!!, vm.token!!) }) { r ->
            inboxPage = r.getOrNull() }
    }
    LaunchedEffect(Unit) { reload() }

    fun openComments(postId: String) {
        openPost = postId
        vm.call({ ApiClient.comments("posts", postId, vm.token!!) }) { r ->
            comments = r.getOrDefault(emptyList())
            r.exceptionOrNull()?.let { note = it.message }
        }
    }

    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)) {
        // What happened while you were away — the deed, never the words.
        inboxPage?.takeIf { it.events.isNotEmpty() }?.let { page ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text(L10n.t("inbox.title", lang), color = Qrme.Txt,
                        fontSize = 16.sp, fontWeight = FontWeight.Bold)
                    if (page.unseen > 0) {
                        Text("${page.unseen} " + L10n.t("inbox.new", lang),
                            color = Qrme.BrandA, fontSize = 11.sp)
                    }
                }
                page.events.forEach { e ->
                    Row(Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                        Text(e.actorName ?: e.actorId,
                            color = if (e.seen) Qrme.T3 else Qrme.Txt,
                            fontSize = 12.sp, fontWeight = FontWeight.Bold)
                        Text(L10n.t("inbox.kind.${e.kind}", lang),
                            color = Qrme.T3, fontSize = 12.sp)
                    }
                }
                if (page.unseen > 0) {
                    BrandButton(L10n.t("inbox.seen", lang)) {
                        vm.call({ ApiClient.markInboxSeen(vm.pid!!,
                            vm.token!!) }) { r ->
                            r.exceptionOrNull()?.let { note = it.message }
                            reload()
                        }
                    }
                }
            }
        }
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("people.friends", lang), color = Qrme.Txt, fontSize = 16.sp,
                fontWeight = FontWeight.Bold)
            friends.forEach { f ->
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    val who = f.displayName ?: f.profileId
                    Text(if (f.founder) "$who ★" else who, color = Qrme.Txt, fontSize = 12.sp)
                    if (f.pinned) {
                        Text(L10n.t("people.pinned", lang), color = Qrme.T3, fontSize = 11.sp)
                    } else {
                        TextButton(onClick = {
                            vm.call({ ApiClient.removeFriend(vm.pid!!, f.profileId,
                                vm.token!!) }) { r ->
                                r.exceptionOrNull()?.let { note = it.message }
                                reload()
                            }
                        }) { Text(L10n.t("people.remove", lang), color = Qrme.Red, fontSize = 11.sp) }
                    }
                }
            }
            labeledField(L10n.t("people.add", lang), addId, "") { addId = it }
            BrandButton(L10n.t("people.add.go", lang), enabled = addId.isNotBlank()) {
                val who = addId.trim(); addId = ""
                vm.call({ ApiClient.addFriend(vm.pid!!, who, vm.token!!) }) { r ->
                    r.exceptionOrNull()?.let { note = it.message }
                    reload()
                }
            }
        }

        if (suggested.isNotEmpty()) {
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text(L10n.t("people.suggested", lang), color = Qrme.Txt, fontSize = 14.sp,
                    fontWeight = FontWeight.Bold)
                Text(L10n.t("people.ranked", lang), color = Qrme.T2, fontSize = 11.sp)
                suggested.forEach { s ->
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                        val who = s.displayName ?: s.profileId
                        val line = if (s.because.isNullOrBlank()) who else who + " · " + s.because
                        Text(line, color = Qrme.T2, fontSize = 11.sp)
                        TextButton(onClick = {
                            vm.call({ ApiClient.addFriend(vm.pid!!, s.profileId,
                                vm.token!!) }) { r ->
                                r.exceptionOrNull()?.let { note = it.message }
                                reload()
                            }
                        }) { Text(L10n.t("people.add.go", lang), color = Qrme.BrandA, fontSize = 11.sp) }
                    }
                }
            }
        }

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Text(L10n.t("people.wall", lang), color = Qrme.Txt, fontSize = 14.sp,
                fontWeight = FontWeight.Bold)
            labeledField(L10n.t("people.say", lang), draft, "") { draft = it }
            BrandButton(L10n.t("people.post", lang), enabled = draft.isNotBlank()) {
                val words = draft; draft = ""
                vm.call({ ApiClient.postToWall(vm.pid!!, words, vm.token!!) }) { r ->
                    r.exceptionOrNull()?.let { note = it.message }
                    if (r.getOrNull()?.status == "blocked") {
                        note = L10n.t("people.blocked", lang)
                    }
                    reload()
                }
            }
            posts.forEach { p ->
                Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                    Text(p.body, color = Qrme.Txt, fontSize = 12.sp)
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                        if (p.status == "blocked") {
                            Text(L10n.t("people.blocked", lang), color = Qrme.T3, fontSize = 11.sp)
                        } else {
                            Text("", color = Qrme.T3, fontSize = 11.sp)
                        }
                        TextButton(onClick = { openComments(p.id) }) {
                            Text(L10n.t("people.comments", lang), color = Qrme.BrandA, fontSize = 11.sp)
                        }
                    }
                }
            }
        }

        openPost?.let { postId ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text(L10n.t("people.comments", lang), color = Qrme.Txt, fontSize = 14.sp,
                    fontWeight = FontWeight.Bold)
                comments.forEach { c ->
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                        Text(c.body, color = Qrme.T2, fontSize = 11.sp)
                        if (c.authorId == vm.pid) {
                            TextButton(onClick = {
                                vm.call({ ApiClient.deleteComment(c.id, vm.token!!) }) { r ->
                                    r.exceptionOrNull()?.let { note = it.message }
                                    openComments(postId)
                                }
                            }) { Text(L10n.t("people.withdraw", lang), color = Qrme.Red, fontSize = 11.sp) }
                        }
                    }
                }
                labeledField(L10n.t("people.reply", lang), commentDraft, "") { commentDraft = it }
                BrandButton(L10n.t("people.send", lang), enabled = commentDraft.isNotBlank()) {
                    val words = commentDraft; commentDraft = ""
                    vm.call({ ApiClient.addComment("posts", postId, words, vm.token!!) }) { r ->
                        r.exceptionOrNull()?.let { note = it.message }
                        openComments(postId)
                    }
                }
            }
        }

        CrowdBlock(vm) { note = it }
        PartyBlock(vm) { note = it }
        LendBlock(vm) { note = it }
        PlaceBlock(vm) { note = it }
        CameraBlock(vm) { note = it }
        OrgBlock(vm) { note = it }
        TourBlock(vm) { note = it }
        BotBlock(vm) { note = it }
        ReferBlock(vm) { note = it }
        ObjectBlock(vm) { note = it }
        LobbyBlock(vm) { note = it }
        DockBlock(vm) { note = it }
        SealBlock(vm) { note = it }
        MailBlock(vm) { note = it }
        RoomsBlock(vm) { note = it }
        WallScreenBlock(vm) { note = it }
        PlanBlock(vm) { note = it }
        HandBlock(vm) { note = it }
        CampBlock(vm) { note = it }
        WorkBlock(vm) { note = it }
        DeleBlock(vm) { note = it }
        AsstBlock(vm) { note = it }
        TaskBlock(vm) { note = it }
        PlcBlock(vm) { note = it }
        SpecBlock(vm) { note = it }
        MemBlock(vm) { note = it }
        PairBlock(vm) { note = it }
        SrcBlock(vm) { note = it }
        RecBlock(vm) { note = it }
        VeilBlock(vm) { note = it }
        BadgeBlock(vm) { note = it }
        ExitBlock(vm) { note = it }
        AvaBlock(vm) { note = it }
        EmblBlock(vm) { note = it }
        PgBlock(vm) { note = it }
        SurfBlock(vm) { note = it }
        FormBlock(vm) { note = it }
        SteerBlock(vm) { note = it }
        WristBlock(vm) { note = it }
        AcctBlock(vm) { note = it }
        TillBlock(vm) { note = it }
        LifeBlock(vm) { note = it }
        BcnBlock(vm) { note = it }
        ModqBlock(vm) { note = it }
        RevwBlock(vm) { note = it }
        WmBlock(vm) { note = it }
        MedBlock(vm) { note = it }
        WearBlock(vm) { note = it }
        BornBlock(vm) { note = it }
        MindBlock(vm) { note = it }
        ReachBlock(vm) { note = it }
        LicBlock(vm) { note = it }
        SensBlock(vm) { note = it }

        note?.let { Text(it, color = Qrme.T2, fontSize = 12.sp) }
    }
}

// The crowd, the couch and the loan — three blocks the doorless records
// said this phone could not reach. Audience verbs first: the backend
// reports the numbers and the caller's own state in one call, so the
// buttons render without a second trip.
@Composable
private fun CrowdBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var kind by remember { mutableStateOf("profiles") }
    var targetId by remember { mutableStateOf("") }
    var counts by remember { mutableStateOf<AudienceCounts?>(null) }
    var gifts by remember { mutableStateOf<List<GiftRow>>(emptyList()) }
    var amount by remember { mutableStateOf("") }
    var giftNote by remember { mutableStateOf("") }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("crowd.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        labeledField(L10n.t("crowd.target", lang), targetId, "") { targetId = it }
        labeledField(L10n.t("nmg.f.kind", vm.language), kind, L10n.t("nmg.f.kind.ph", vm.language)) { kind = it }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("crowd.like", lang), enabled = targetId.isNotBlank()) {
                vm.call({ ApiClient.like(kind, targetId, vm.token!!) }) { r ->
                    onNote(r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("crowd.unlike", lang), enabled = targetId.isNotBlank()) {
                vm.call({ ApiClient.unlike(kind, targetId, vm.token!!) }) { r ->
                    onNote(r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("crowd.share", lang), enabled = targetId.isNotBlank()) {
                vm.call({ ApiClient.share(kind, targetId, vm.token!!) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
        }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("crowd.counts", lang), enabled = targetId.isNotBlank()) {
                vm.call({ ApiClient.counts(kind, targetId, vm.token!!) }) { r ->
                    counts = r.getOrNull()
                    onNote(r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("crowd.follow", lang), enabled = targetId.isNotBlank()) {
                vm.call({ ApiClient.subscribe(kind, targetId, vm.token!!) }) { r ->
                    onNote(r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("crowd.unfollow", lang), enabled = targetId.isNotBlank()) {
                vm.call({ ApiClient.unsubscribe(kind, targetId, vm.token!!) }) { r ->
                    onNote(r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("crowd.subscribers", lang), enabled = targetId.isNotBlank()) {
                vm.call({ ApiClient.subscribers(kind, targetId, vm.token!!) }) { r ->
                    onNote(r.getOrNull()?.toString() ?: r.exceptionOrNull()?.message) }
            }
        }
        counts?.let {
            Text("♥ ${it.likes} · 💬 ${it.comments} · ↗ ${it.shares} · ⊕ ${it.subscribers}",
                color = Qrme.T3, fontSize = 11.sp)
        }
        // A gift is a gift: said beside the button, not after the mistake.
        Text(L10n.t("crowd.gift.note", lang), color = Qrme.T3, fontSize = 11.sp)
        labeledField(L10n.t("crowd.gift.amount", lang), amount, "") { amount = it }
        labeledField(L10n.t("crowd.gift.words", lang), giftNote, "") { giftNote = it }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("crowd.gift", lang),
                enabled = targetId.isNotBlank() && amount.isNotBlank()) {
                vm.call({ ApiClient.gift(kind, targetId,
                    amount.toDoubleOrNull() ?: 0.0, giftNote, vm.token!!) }) { r ->
                    onNote(r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("crowd.gifts", lang), enabled = targetId.isNotBlank()) {
                vm.call({ ApiClient.gifts(kind, targetId, vm.token!!) }) { r ->
                    gifts = r.getOrDefault(emptyList())
                    onNote(r.exceptionOrNull()?.message) }
            }
        }
        gifts.forEach { g ->
            Text("${g.giverId} · ${g.amount} · ${g.note}", color = Qrme.T3,
                fontSize = 11.sp)
        }
    }
}

// The watch party: a room around a posted video. Seek moves a number and
// presses play on nobody's device.
@Composable
private fun PartyBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var postId by remember { mutableStateOf("") }
    var title by remember { mutableStateOf("") }
    var partyId by remember { mutableStateOf("") }
    var card by remember { mutableStateOf<PartyCard?>(null) }
    var lines by remember { mutableStateOf<List<PartyLine>>(emptyList()) }
    var draft by remember { mutableStateOf("") }
    var seekTo by remember { mutableStateOf("") }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("party.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        labeledField(L10n.t("party.post", lang), postId, "") { postId = it }
        labeledField(L10n.t("party.name", lang), title, "") { title = it }
        BrandButton(L10n.t("party.start", lang), enabled = postId.isNotBlank()) {
            vm.call({ ApiClient.startParty(postId, vm.pid!!, title,
                vm.token!!) }) { r ->
                r.getOrNull()?.let { partyId = it.id; card = it }
                onNote(r.exceptionOrNull()?.message) }
        }
        labeledField(L10n.t("party.id", lang), partyId, "") { partyId = it }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("party.join", lang), enabled = partyId.isNotBlank()) {
                vm.call({ ApiClient.joinParty(partyId, vm.pid!!, vm.token!!) }) { r ->
                    card = r.getOrNull(); onNote(r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("party.show", lang), enabled = partyId.isNotBlank()) {
                vm.call({ ApiClient.party(partyId, vm.token!!) }) { r ->
                    card = r.getOrNull(); onNote(r.exceptionOrNull()?.message) }
                vm.call({ ApiClient.partyChat(partyId, vm.token!!) }) { r ->
                    lines = r.getOrDefault(emptyList()) }
            }
            BrandButton(L10n.t("party.leave", lang), enabled = partyId.isNotBlank()) {
                vm.call({ ApiClient.leaveParty(partyId, vm.pid!!, vm.token!!) }) { r ->
                    onNote(r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("party.end", lang), enabled = partyId.isNotBlank()) {
                vm.call({ ApiClient.endParty(partyId, vm.token!!) }) { r ->
                    card = r.getOrNull(); onNote(r.exceptionOrNull()?.message) }
            }
        }
        card?.let {
            Text("${it.title} · ${it.state} · ${it.positionS} · ${it.members}",
                color = Qrme.T3, fontSize = 11.sp)
        }
        labeledField(L10n.t("party.seek", lang), seekTo, "") { seekTo = it }
        BrandButton(L10n.t("party.seek.go", lang),
            enabled = partyId.isNotBlank() && seekTo.isNotBlank()) {
            vm.call({ ApiClient.seekParty(partyId, vm.pid!!,
                seekTo.toIntOrNull() ?: 0, vm.token!!) }) { r ->
                card = r.getOrNull(); onNote(r.exceptionOrNull()?.message) }
        }
        lines.forEach { l ->
            Text("${l.memberId}: ${l.body}", color = Qrme.T3, fontSize = 11.sp)
        }
        labeledField(L10n.t("party.say", lang), draft, "") { draft = it }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("people.send", lang),
                enabled = partyId.isNotBlank() && draft.isNotBlank()) {
                val words = draft; draft = ""
                vm.call({ ApiClient.sayInParty(partyId, vm.pid!!, words,
                    vm.token!!) }) { r ->
                    onNote(r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("party.context", lang), enabled = partyId.isNotBlank()) {
                vm.call({ ApiClient.partyContext(partyId, vm.token!!) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
        }
    }
}

// Skill grants: a skill lent into one place, used and never copied. The
// terms shown are the backend's own sentences, verbatim.
@Composable
private fun LendBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var terms by remember { mutableStateOf<List<String>>(emptyList()) }
    var mine by remember { mutableStateOf<List<GrantCard>>(emptyList()) }
    var borrowerId by remember { mutableStateOf("") }
    var surface by remember { mutableStateOf("room") }
    var surfaceId by remember { mutableStateOf("") }
    var skillKind by remember { mutableStateOf("") }
    var skillRef by remember { mutableStateOf("") }
    var title by remember { mutableStateOf("") }
    var grantId by remember { mutableStateOf("") }
    var what by remember { mutableStateOf("") }
    var uses by remember { mutableStateOf<List<GrantUse>>(emptyList()) }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("lend.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        BrandButton(L10n.t("lend.rules", lang)) {
            vm.call({ ApiClient.grantTerms() }) { r ->
                terms = r.getOrDefault(emptyList())
                onNote(r.exceptionOrNull()?.message) }
        }
        terms.forEach { Text("· $it", color = Qrme.T3, fontSize = 11.sp) }
        labeledField(L10n.t("lend.borrower", lang), borrowerId, "") { borrowerId = it }
        labeledField(L10n.t("lend.surface", lang), surface, "") { surface = it }
        labeledField(L10n.t("lend.surface.id", lang), surfaceId, "") { surfaceId = it }
        labeledField(L10n.t("lend.kind", lang), skillKind, "") { skillKind = it }
        labeledField(L10n.t("lend.ref", lang), skillRef, "") { skillRef = it }
        labeledField(L10n.t("lend.name", lang), title, "") { title = it }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("lend.offer", lang),
                enabled = borrowerId.isNotBlank() && title.isNotBlank()) {
                vm.call({ ApiClient.offerGrant(vm.pid!!, borrowerId, surface,
                    surfaceId, skillKind, skillRef, title, vm.token!!) }) { r ->
                    r.getOrNull()?.let { grantId = it.id }
                    onNote(r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("lend.mine", lang)) {
                vm.call({ ApiClient.myGrants(vm.pid!!, vm.token!!) }) { r ->
                    mine = r.getOrDefault(emptyList())
                    onNote(r.exceptionOrNull()?.message) }
                vm.call({ ApiClient.grantsInSurface(surface,
                    surfaceId.ifBlank { "x" }, vm.token!!) }) { _ -> }
            }
        }
        mine.forEach { g ->
            Text("${g.id} · ${g.title} · ${g.state}", color = Qrme.T3,
                fontSize = 11.sp)
        }
        labeledField(L10n.t("lend.id", lang), grantId, "") { grantId = it }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("lend.accept", lang), enabled = grantId.isNotBlank()) {
                vm.call({ ApiClient.acceptGrant(grantId, vm.pid!!, vm.token!!) }) { r ->
                    onNote(r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("lend.decline", lang), enabled = grantId.isNotBlank()) {
                vm.call({ ApiClient.declineGrant(grantId, vm.pid!!, vm.token!!) }) { r ->
                    onNote(r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("lend.close", lang), enabled = grantId.isNotBlank()) {
                vm.call({ ApiClient.closeGrant(grantId, vm.pid!!, vm.token!!) }) { r ->
                    onNote(r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("lend.show", lang), enabled = grantId.isNotBlank()) {
                vm.call({ ApiClient.grant(grantId, vm.token!!) }) { r ->
                    onNote(r.getOrNull()?.let { "${it.title} · ${it.state}" }
                        ?: r.exceptionOrNull()?.message) }
            }
        }
        labeledField(L10n.t("lend.what", lang), what, "") { what = it }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("lend.use", lang), enabled = grantId.isNotBlank()) {
                vm.call({ ApiClient.useGrant(grantId, vm.pid!!, what,
                    vm.token!!) }) { r ->
                    onNote(r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("lend.uses", lang), enabled = grantId.isNotBlank()) {
                vm.call({ ApiClient.grantUses(grantId, vm.token!!) }) { r ->
                    uses = r.getOrDefault(emptyList())
                    onNote(r.exceptionOrNull()?.message) }
            }
        }
        uses.forEach { u ->
            Text("${u.usedAt} · ${u.what}", color = Qrme.T3, fontSize = 11.sp)
        }
    }
}


// The place, the camera, the organization and the tour — four more blocks
// off the doorless records. Disclosure-first: what everyone present may
// read comes ahead of what one person may do.
@Composable
private fun PlaceBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var surface by remember { mutableStateOf("room") }
    var surfaceId by remember { mutableStateOf("") }
    var maskKind by remember { mutableStateOf("avatar") }
    var maskName by remember { mutableStateOf("") }
    var rows by remember { mutableStateOf<List<String>>(emptyList()) }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("place.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        labeledField(L10n.t("place.surface", lang), surface, "") { surface = it }
        labeledField(L10n.t("place.surface.id", lang), surfaceId, "") { surfaceId = it }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("place.whose", lang), enabled = surfaceId.isNotBlank()) {
                vm.call({ ApiClient.whose(surface, surfaceId) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("place.mic.lend", lang), enabled = surfaceId.isNotBlank()) {
                vm.call({ ApiClient.lendMicrophone(surface, surfaceId, vm.pid!!,
                    vm.token!!) }) { r -> onNote(r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("place.mic.back", lang), enabled = surfaceId.isNotBlank()) {
                vm.call({ ApiClient.takeBackMicrophone(surface, surfaceId,
                    vm.pid!!, vm.token!!) }) { r -> onNote(r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("place.mic.who", lang), enabled = surfaceId.isNotBlank()) {
                vm.call({ ApiClient.microphoneDisclosure(surface, surfaceId,
                    vm.token!!) }) { r ->
                    rows = r.getOrDefault(emptyList())
                    onNote(r.exceptionOrNull()?.message) }
            }
        }
        labeledField(L10n.t("place.mask.kind", lang), maskKind, "") { maskKind = it }
        labeledField(L10n.t("place.mask.name", lang), maskName, "") { maskName = it }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("place.mask.wear", lang),
                enabled = surfaceId.isNotBlank() && maskName.isNotBlank()) {
                vm.call({ ApiClient.wearOverlay(surface, surfaceId, vm.pid!!,
                    maskKind, maskName, vm.token!!) }) { r ->
                    onNote(r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("place.mask.off", lang), enabled = surfaceId.isNotBlank()) {
                vm.call({ ApiClient.takeOffOverlay(surface, surfaceId, vm.pid!!,
                    vm.token!!) }) { r -> onNote(r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("place.mask.who", lang), enabled = surfaceId.isNotBlank()) {
                vm.call({ ApiClient.wornOverlays(surface, surfaceId,
                    vm.token!!) }) { r ->
                    rows = r.getOrDefault(emptyList())
                    onNote(r.exceptionOrNull()?.message) }
            }
        }
        rows.forEach { Text(it, color = Qrme.T3, fontSize = 11.sp) }
    }
}

// The camera opens with its published refusals — a client that knew only
// the allowed combinations would draw a refused one as a missing feature.
@Composable
private fun CameraBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var surface by remember { mutableStateOf("room") }
    var surfaceId by remember { mutableStateOf("") }
    var subject by remember { mutableStateOf("object") }
    var viewerId by remember { mutableStateOf("") }
    var minutes by remember { mutableStateOf("10") }
    var sessionId by remember { mutableStateOf("") }
    var rows by remember { mutableStateOf<List<String>>(emptyList()) }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("cam.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        BrandButton(L10n.t("cam.rules", lang)) {
            vm.call({ ApiClient.cameraRefusals() }) { r ->
                rows = r.getOrDefault(emptyList())
                onNote(r.exceptionOrNull()?.message) }
            vm.call({ ApiClient.bystanderGuidance(subject) }) { _ -> }
        }
        rows.forEach { Text("· $it", color = Qrme.T3, fontSize = 11.sp) }
        labeledField(L10n.t("place.surface", lang), surface, "") { surface = it }
        labeledField(L10n.t("place.surface.id", lang), surfaceId, "") { surfaceId = it }
        labeledField(L10n.t("cam.subject", lang), subject, "") { subject = it }
        labeledField(L10n.t("cam.viewer", lang), viewerId, "") { viewerId = it }
        labeledField(L10n.t("cam.minutes", lang), minutes, "") { minutes = it }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("cam.open", lang),
                enabled = surfaceId.isNotBlank() && viewerId.isNotBlank()) {
                vm.call({ ApiClient.openCamera(vm.pid!!, surface, surfaceId,
                    subject, viewerId, minutes.toIntOrNull() ?: 10,
                    vm.token!!) }) { r ->
                    r.getOrNull()?.let { sessionId = it }
                    onNote(r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("cam.mine", lang)) {
                vm.call({ ApiClient.myCameras(vm.pid!!, vm.token!!) }) { r ->
                    rows = r.getOrDefault(emptyList())
                    onNote(r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("cam.disclosure", lang), enabled = surfaceId.isNotBlank()) {
                vm.call({ ApiClient.cameraDisclosure(surface, surfaceId,
                    vm.token!!) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
        }
        labeledField(L10n.t("cam.session", lang), sessionId, "") { sessionId = it }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("cam.show", lang), enabled = sessionId.isNotBlank()) {
                vm.call({ ApiClient.cameraSession(sessionId, vm.token!!) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("cam.close", lang), enabled = sessionId.isNotBlank()) {
                vm.call({ ApiClient.closeCamera(sessionId, vm.pid!!,
                    vm.token!!) }) { r -> onNote(r.exceptionOrNull()?.message) }
            }
        }
    }
}

@Composable
private fun OrgBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var orgName by remember { mutableStateOf("") }
    var orgId by remember { mutableStateOf("") }
    var orgs by remember { mutableStateOf<List<Pair<String, String>>>(emptyList()) }
    var deptName by remember { mutableStateOf("") }
    var deptRole by remember { mutableStateOf("") }
    var deptProfile by remember { mutableStateOf("") }
    var goal by remember { mutableStateOf("") }
    var fromDept by remember { mutableStateOf("") }
    var log by remember { mutableStateOf<List<String>>(emptyList()) }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("org.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        labeledField(L10n.t("org.name", lang), orgName, "") { orgName = it }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("org.create", lang), enabled = orgName.isNotBlank()) {
                vm.call({ ApiClient.createOrganization(orgName, vm.token!!) }) { r ->
                    r.getOrNull()?.let { orgId = it }
                    onNote(r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("org.list", lang)) {
                vm.call({ ApiClient.organizations(vm.token!!) }) { r ->
                    orgs = r.getOrDefault(emptyList())
                    onNote(r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("org.demo", lang)) {
                vm.call({ ApiClient.seedDemoOrganization(vm.token!!) }) { r ->
                    r.getOrNull()?.let { orgId = it }
                    onNote(r.exceptionOrNull()?.message) }
            }
        }
        orgs.forEach { (id, name) ->
            TextButton(onClick = { orgId = id }) {
                Text(name, color = Qrme.T3, fontSize = 11.sp)
            }
        }
        labeledField(L10n.t("org.id", lang), orgId, "") { orgId = it }
        BrandButton(L10n.t("org.show", lang), enabled = orgId.isNotBlank()) {
            vm.call({ ApiClient.organization(orgId, vm.token!!) }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        labeledField(L10n.t("org.dept.name", lang), deptName, "") { deptName = it }
        labeledField(L10n.t("org.dept.role", lang), deptRole, "") { deptRole = it }
        labeledField(L10n.t("org.dept.profile", lang), deptProfile, "") { deptProfile = it }
        BrandButton(L10n.t("org.dept.add", lang),
            enabled = orgId.isNotBlank() && deptName.isNotBlank()) {
            vm.call({ ApiClient.addDepartment(orgId, deptName, deptRole,
                deptProfile, vm.token!!) }) { r ->
                onNote(r.exceptionOrNull()?.message) }
        }
        // AI for lease: same three fields, but the profile id names somebody
        // else's licensed specialist; the fee goes to its owner.
        BrandButton(L10n.t("org.lease", lang),
            enabled = orgId.isNotBlank() && deptName.isNotBlank()
                && deptProfile.isNotBlank()) {
            vm.call({ ApiClient.leaseSpecialist(orgId, deptProfile, deptName,
                deptRole, vm.token!!) }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        labeledField(L10n.t("org.goal", lang), goal, "") { goal = it }
        labeledField(L10n.t("org.department", lang), fromDept, "") { fromDept = it }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("org.go", lang),
                enabled = orgId.isNotBlank() && goal.isNotBlank()
                    && fromDept.isNotBlank()) {
                vm.call({ ApiClient.coordinate(orgId, goal, fromDept,
                                               vm.token!!) }) { r ->
                    onNote(r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("org.log", lang), enabled = orgId.isNotBlank()) {
                vm.call({ ApiClient.coordinations(orgId, vm.token!!) }) { r ->
                    log = r.getOrDefault(emptyList())
                    onNote(r.exceptionOrNull()?.message) }
            }
        }
        log.forEach { Text(it, color = Qrme.T3, fontSize = 11.sp) }
    }
}

@Composable
private fun TourBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var chapters by remember { mutableStateOf<List<Pair<String, String>>>(emptyList()) }
    var stepKey by remember { mutableStateOf("") }
    var screenNo by remember { mutableStateOf("") }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("tut.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("tut.outline", lang)) {
                vm.call({ ApiClient.tutorialOutline() }) { r ->
                    chapters = r.getOrDefault(emptyList())
                    onNote(r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("tut.start", lang)) {
                vm.call({ ApiClient.startTutorial(vm.pid ?: "walk-in") }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("tut.progress", lang)) {
                vm.call({ ApiClient.tutorialProgress(vm.pid ?: "walk-in") }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
        }
        chapters.forEach { (key, title) ->
            TextButton(onClick = { stepKey = key }) {
                Text(title, color = Qrme.T3, fontSize = 11.sp)
            }
        }
        labeledField(L10n.t("tut.step", lang), stepKey, "") { stepKey = it }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("cam.show", lang), enabled = stepKey.isNotBlank()) {
                vm.call({ ApiClient.tutorialStep(stepKey) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("tut.done", lang), enabled = stepKey.isNotBlank()) {
                vm.call({ ApiClient.markTutorialDone(vm.pid ?: "walk-in",
                    stepKey) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
        }
        labeledField(L10n.t("tut.screen", lang), screenNo, "") { screenNo = it }
        BrandButton(L10n.t("tut.screen", lang), enabled = screenNo.isNotBlank()) {
            vm.call({ ApiClient.tutorialForScreen(screenNo.toIntOrNull()
                ?: 1) }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
    }
}

// The body, the referral, the objection, the lobby and the dock — five
// more blocks off the doorless records, each rendering its backend's
// rules rather than inventing a sixth opinion.
@Composable
private fun BotBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var robotId by remember { mutableStateOf("") }
    var pace by remember { mutableStateOf("") }
    var rows by remember { mutableStateOf<List<String>>(emptyList()) }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("bot.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        labeledField(L10n.t("bot.id", lang), robotId, "") { robotId = it }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("bot.log", lang), enabled = robotId.isNotBlank()) {
                vm.call({ ApiClient.robotCommands(robotId, vm.token!!) }) { r ->
                    rows = r.getOrDefault(emptyList())
                    onNote(r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("bot.skills", lang), enabled = robotId.isNotBlank()) {
                vm.call({ ApiClient.robotSkills(robotId, vm.token!!) }) { r ->
                    rows = r.getOrDefault(emptyList())
                    onNote(r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("bot.dials", lang), enabled = robotId.isNotBlank()) {
                vm.call({ ApiClient.robotSteering(robotId, vm.token!!) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("bot.unbind", lang), enabled = robotId.isNotBlank()) {
                vm.call({ ApiClient.unbindRobot(robotId, vm.token!!) }) { r ->
                    onNote(r.exceptionOrNull()?.message) }
            }
        }
        labeledField(L10n.t("bot.pace", lang), pace, "") { pace = it }
        BrandButton(L10n.t("bot.dials.set", lang),
            enabled = robotId.isNotBlank() && pace.isNotBlank()) {
            vm.call({ ApiClient.steerRobot(robotId,
                pace.toIntOrNull() ?: 50, vm.token!!) }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        rows.forEach { Text(it, color = Qrme.T3, fontSize = 11.sp) }
    }
}

@Composable
private fun ReferBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var area by remember { mutableStateOf("") }
    var providerId by remember { mutableStateOf("") }
    var referralId by remember { mutableStateOf("") }
    var signatureId by remember { mutableStateOf("") }
    var linkToken by remember { mutableStateOf("") }
    var reply by remember { mutableStateOf("") }
    var found by remember { mutableStateOf<List<Pair<String, String>>>(emptyList()) }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("refer.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        labeledField(L10n.t("refer.area", lang), area, "") { area = it }
        BrandButton(L10n.t("refer.match", lang), enabled = area.isNotBlank()) {
            vm.call({ ApiClient.matchClinicians(area) }) { r ->
                found = r.getOrDefault(emptyList())
                onNote(r.exceptionOrNull()?.message) }
        }
        found.forEach { (id, line) ->
            TextButton(onClick = { providerId = id }) {
                Text(line, color = Qrme.T3, fontSize = 11.sp)
            }
        }
        labeledField(L10n.t("refer.provider", lang), providerId, "") { providerId = it }
        BrandButton(L10n.t("refer.prepare", lang), enabled = providerId.isNotBlank()) {
            vm.call({ ApiClient.prepareReferral(vm.pid!!, vm.pid!!,
                providerId, vm.token!!) }) { r ->
                r.getOrNull()?.let { referralId = it }
                onNote(r.exceptionOrNull()?.message) }
        }
        labeledField(L10n.t("refer.id", lang), referralId, "") { referralId = it }
        labeledField(L10n.t("refer.signature", lang), signatureId, "") { signatureId = it }
        BrandButton(L10n.t("refer.release", lang),
            enabled = referralId.isNotBlank() && signatureId.isNotBlank()) {
            vm.call({ ApiClient.releaseReferral(referralId, signatureId,
                vm.token!!) }) { r -> onNote(r.exceptionOrNull()?.message) }
        }
        labeledField(L10n.t("refer.token", lang), linkToken, "") { linkToken = it }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("refer.open", lang),
                enabled = referralId.isNotBlank() && linkToken.isNotBlank()) {
                vm.call({ ApiClient.openReferral(referralId, linkToken) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
        }
        labeledField(L10n.t("refer.words", lang), reply, "") { reply = it }
        BrandButton(L10n.t("refer.reply", lang),
            enabled = referralId.isNotBlank() && linkToken.isNotBlank()
                && reply.isNotBlank()) {
            vm.call({ ApiClient.replyToReferral(referralId, linkToken,
                reply) }) { r -> onNote(r.exceptionOrNull()?.message) }
        }
    }
}

@Composable
private fun ObjectBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var objectionId by remember { mutableStateOf("") }
    var rows by remember { mutableStateOf<List<String>>(emptyList()) }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("object.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        labeledField(L10n.t("object.id", lang), objectionId, "") { objectionId = it }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("object.show", lang), enabled = objectionId.isNotBlank()) {
                vm.call({ ApiClient.objection(objectionId) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("object.audit", lang), enabled = objectionId.isNotBlank()) {
                vm.call({ ApiClient.objectionAudit(objectionId, vm.token!!) }) { r ->
                    rows = r.getOrDefault(emptyList())
                    onNote(r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("object.withdraw", lang), enabled = objectionId.isNotBlank()) {
                vm.call({ ApiClient.withdrawObjectionConsent(objectionId) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("object.revoke", lang), enabled = objectionId.isNotBlank()) {
                vm.call({ ApiClient.revokeObjectionBasis(objectionId) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
        }
        // The reviewer's verb, drawn with its gate named: an owner cannot
        // adjudicate an objection against their own profile.
        BrandButton(L10n.t("object.resolve", lang) + " — " +
            L10n.t("object.outcome", lang), enabled = objectionId.isNotBlank()) {
            vm.call({ ApiClient.resolveObjection(objectionId, "dismiss",
                vm.token!!) }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        rows.forEach { Text(it, color = Qrme.T3, fontSize = 11.sp) }
    }
}

@Composable
private fun LobbyBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var sessionId by remember { mutableStateOf("") }
    var memberKind by remember { mutableStateOf("profile") }
    var memberId by remember { mutableStateOf("") }
    var role by remember { mutableStateOf("teammate") }
    var rows by remember { mutableStateOf<List<String>>(emptyList()) }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("lobby.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        BrandButton(L10n.t("lobby.rules", lang)) {
            vm.call({ ApiClient.lobbyRules() }) { r ->
                rows = r.getOrDefault(emptyList())
                onNote(r.exceptionOrNull()?.message) }
        }
        labeledField(L10n.t("lobby.session", lang), sessionId, "") { sessionId = it }
        labeledField(L10n.t("lobby.kind", lang), memberKind, "") { memberKind = it }
        labeledField(L10n.t("lobby.member", lang), memberId, "") { memberId = it }
        labeledField(L10n.t("lobby.role", lang), role, "") { role = it }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("lobby.seat", lang),
                enabled = sessionId.isNotBlank() && memberId.isNotBlank()) {
                vm.call({ ApiClient.seatInLobby(sessionId, memberKind,
                    memberId, role, vm.token!!) }) { r ->
                    onNote(r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("lobby.roster", lang), enabled = sessionId.isNotBlank()) {
                vm.call({ ApiClient.lobbyRoster(sessionId, vm.token!!) }) { r ->
                    rows = r.getOrDefault(emptyList())
                    onNote(r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("lobby.leave", lang),
                enabled = sessionId.isNotBlank() && memberId.isNotBlank()) {
                vm.call({ ApiClient.leaveLobby(sessionId, memberId,
                    vm.token!!) }) { r -> onNote(r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("lobby.context", lang), enabled = sessionId.isNotBlank()) {
                vm.call({ ApiClient.lobbyContext(sessionId, vm.token!!) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
        }
        rows.forEach { Text(it, color = Qrme.T3, fontSize = 11.sp) }
    }
}

@Composable
private fun DockBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var faceName by remember { mutableStateOf("") }
    var corner by remember { mutableStateOf("bottom_right") }
    var state by remember { mutableStateOf("handle") }
    var rows by remember { mutableStateOf<List<String>>(emptyList()) }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("dock.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("dock.faces", lang)) {
                vm.call({ ApiClient.dockFaces() }) { r ->
                    rows = r.getOrDefault(emptyList())
                    onNote(r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("dock.mine", lang)) {
                vm.call({ ApiClient.dockSettings(vm.pid!!, vm.token!!) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
        }
        rows.forEach { f ->
            TextButton(onClick = { faceName = f }) {
                Text(f, color = Qrme.T3, fontSize = 11.sp)
            }
        }
        labeledField(L10n.t("dock.face", lang), faceName, "") { faceName = it }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("dock.where", lang), enabled = faceName.isNotBlank()) {
                vm.call({ ApiClient.dockWhere(faceName) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("dock.face", lang), enabled = faceName.isNotBlank()) {
                vm.call({ ApiClient.dockFace(vm.pid!!, faceName,
                    vm.token!!) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
        }
        labeledField(L10n.t("dock.corner", lang), corner, "") { corner = it }
        labeledField(L10n.t("dock.state", lang), state, "") { state = it }
        BrandButton(L10n.t("dock.set", lang)) {
            vm.call({ ApiClient.configureDock(vm.pid!!, corner, state,
                vm.token!!) }) { r -> onNote(r.exceptionOrNull()?.message) }
        }
    }
}

// Seven small blocks that close out the mid-sized doorless groups: the
// signature a person can read and a stranger can verify, the mail
// settings, the room's lent ear, the wall screen, the plan, the
// consented handoff and the campaign.
@Composable
private fun SealBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var sigId by remember { mutableStateOf("") }
    var credId by remember { mutableStateOf("") }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("sig.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        labeledField(L10n.t("sig.id", lang), sigId, "") { sigId = it }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("sig.certificate", lang), enabled = sigId.isNotBlank()) {
                vm.call({ ApiClient.signatureCertificate(sigId) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("sig.verify", lang)) {
                vm.call({ ApiClient.verifySignaturePackage() }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("sig.ceremony", lang)) {
                onNote(ApiClient.signatureCeremonyUrl())
            }
        }
        labeledField(L10n.t("sig.credential", lang), credId, "") { credId = it }
        BrandButton(L10n.t("sig.proofing", lang), enabled = credId.isNotBlank()) {
            vm.call({ ApiClient.reproofCredential(credId, "verified",
                vm.pid!!, vm.token!!) }) { r ->
                onNote(r.exceptionOrNull()?.message) }
        }
    }
}

@Composable
private fun MailBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var host by remember { mutableStateOf("") }
    var port by remember { mutableStateOf("587") }
    var sender by remember { mutableStateOf("") }
    var to by remember { mutableStateOf("") }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("mail.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        BrandButton(L10n.t("mail.title", lang)) {
            vm.call({ ApiClient.mailSettings() }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        labeledField(L10n.t("mail.host", lang), host, "") { host = it }
        labeledField(L10n.t("mail.port", lang), port, "") { port = it }
        labeledField(L10n.t("mail.sender", lang), sender, "") { sender = it }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("mail.save", lang), enabled = host.isNotBlank()) {
                vm.call({ ApiClient.saveMailSettings(host,
                    port.toIntOrNull() ?: 587, sender, vm.token!!) }) { r ->
                    onNote(r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("mail.forget", lang)) {
                vm.call({ ApiClient.forgetMailSettings(vm.token!!) }) { r ->
                    onNote(r.exceptionOrNull()?.message) }
            }
        }
        labeledField(L10n.t("mail.to", lang), to, "") { to = it }
        BrandButton(L10n.t("mail.test", lang), enabled = to.isNotBlank()) {
            vm.call({ ApiClient.testMailSettings(to, vm.token!!) }) { r ->
                onNote(r.exceptionOrNull()?.message) }
        }
    }
}

@Composable
private fun RoomsBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var rooms by remember { mutableStateOf<List<Pair<String, String>>>(emptyList()) }
    var roomId by remember { mutableStateOf("") }
    var rows by remember { mutableStateOf<List<String>>(emptyList()) }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("room.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        BrandButton(L10n.t("room.list", lang)) {
            vm.call({ ApiClient.rooms() }) { r ->
                rooms = r.getOrDefault(emptyList())
                onNote(r.exceptionOrNull()?.message) }
        }
        rooms.forEach { (id, line) ->
            TextButton(onClick = { roomId = id }) {
                Text(line, color = Qrme.T3, fontSize = 11.sp)
            }
        }
        labeledField(L10n.t("room.id", lang), roomId, "") { roomId = it }
        // The list used to show rooms nobody could enter — the door in
        // was frozen at creation. Joining takes the interactor token; a
        // room id alone is not being here.
        BrandButton(L10n.t("room.join", lang), enabled = roomId.isNotBlank()) {
            vm.call({ ApiClient.joinRoom(roomId, vm.interactorToken.orEmpty()) }) { r ->
                onNote(r.exceptionOrNull()?.message) }
        }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("room.mic.lend", lang), enabled = roomId.isNotBlank()) {
                vm.call({ ApiClient.lendRoomMic(roomId, vm.pid!!,
                    vm.token!!) }) { r -> onNote(r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("room.mic.back", lang), enabled = roomId.isNotBlank()) {
                vm.call({ ApiClient.takeBackRoomMic(roomId, vm.pid!!,
                    vm.token!!) }) { r -> onNote(r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("room.mic.who", lang), enabled = roomId.isNotBlank()) {
                vm.call({ ApiClient.roomMicDisclosure(roomId, vm.token!!) }) { r ->
                    rows = r.getOrDefault(emptyList())
                    onNote(r.exceptionOrNull()?.message) }
            }
        }
        rows.forEach { Text(it, color = Qrme.T3, fontSize = 11.sp) }
    }
}

@Composable
private fun WallScreenBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var rules by remember { mutableStateOf<List<String>>(emptyList()) }
    var displayId by remember { mutableStateOf("") }
    var faces by remember { mutableStateOf("") }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("disp.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        BrandButton(L10n.t("disp.rules", lang)) {
            vm.call({ ApiClient.displayRules() }) { r ->
                rules = r.getOrDefault(emptyList())
                onNote(r.exceptionOrNull()?.message) }
        }
        rules.forEach { Text("· $it", color = Qrme.T3, fontSize = 11.sp) }
        labeledField(L10n.t("disp.id", lang), displayId, "") { displayId = it }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("disp.show", lang), enabled = displayId.isNotBlank()) {
                vm.call({ ApiClient.display(displayId) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("disp.down", lang), enabled = displayId.isNotBlank()) {
                vm.call({ ApiClient.takeDownDisplay(displayId, vm.token!!) }) { r ->
                    onNote(r.exceptionOrNull()?.message) }
            }
        }
        labeledField(L10n.t("disp.faces", lang), faces, "") { faces = it }
        BrandButton(L10n.t("disp.faces", lang),
            enabled = displayId.isNotBlank() && faces.isNotBlank()) {
            vm.call({ ApiClient.setDisplayFaces(displayId,
                faces.split(",").map { it.trim() }, vm.token!!) }) { r ->
                onNote(r.exceptionOrNull()?.message) }
        }
    }
}

@Composable
private fun PlanBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var accountId by remember { mutableStateOf("") }
    var plan by remember { mutableStateOf("basic") }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("member.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        labeledField(L10n.t("member.account", lang), accountId, "") { accountId = it }
        labeledField(L10n.t("member.plan", lang), plan, "") { plan = it }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("member.show", lang), enabled = accountId.isNotBlank()) {
                vm.call({ ApiClient.membership(accountId, vm.token!!) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("member.join", lang),
                enabled = accountId.isNotBlank() && plan.isNotBlank()) {
                vm.call({ ApiClient.joinPlan(accountId, plan, vm.token!!) }) { r ->
                    onNote(r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("member.cancel", lang), enabled = accountId.isNotBlank()) {
                vm.call({ ApiClient.cancelMembership(accountId, vm.token!!) }) { r ->
                    onNote(r.exceptionOrNull()?.message) }
            }
        }
    }
}

@Composable
private fun HandBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var providerId by remember { mutableStateOf("") }
    var handoffId by remember { mutableStateOf("") }
    var linkToken by remember { mutableStateOf("") }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("hand.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        labeledField(L10n.t("hand.provider", lang), providerId, "") { providerId = it }
        BrandButton(L10n.t("hand.create", lang), enabled = providerId.isNotBlank()) {
            vm.call({ ApiClient.createHandoff(vm.pid!!, vm.pid!!, providerId,
                vm.token!!) }) { r ->
                r.getOrNull()?.let { handoffId = it.first; linkToken = it.second }
                onNote(r.exceptionOrNull()?.message) }
        }
        labeledField(L10n.t("hand.id", lang), handoffId, "") { handoffId = it }
        labeledField(L10n.t("hand.token", lang), linkToken, "") { linkToken = it }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("hand.open", lang),
                enabled = handoffId.isNotBlank() && linkToken.isNotBlank()) {
                vm.call({ ApiClient.openHandoff(handoffId, linkToken) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("hand.revoke", lang), enabled = handoffId.isNotBlank()) {
                vm.call({ ApiClient.revokeHandoff(handoffId, vm.token!!) }) { r ->
                    onNote(r.exceptionOrNull()?.message) }
            }
        }
    }
}

@Composable
private fun CampBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var campaignId by remember { mutableStateOf("") }
    var amount by remember { mutableStateOf("") }
    var words by remember { mutableStateOf("") }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("camp.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        labeledField(L10n.t("camp.id", lang), campaignId, "") { campaignId = it }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("camp.show", lang), enabled = campaignId.isNotBlank()) {
                vm.call({ ApiClient.campaign(campaignId) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("camp.close", lang), enabled = campaignId.isNotBlank()) {
                vm.call({ ApiClient.closeCampaign(campaignId, vm.token!!) }) { r ->
                    onNote(r.exceptionOrNull()?.message) }
            }
        }
        labeledField(L10n.t("camp.amount", lang), amount, "") { amount = it }
        labeledField(L10n.t("crowd.gift.words", lang), words, "") { words = it }
        BrandButton(L10n.t("camp.give", lang),
            enabled = campaignId.isNotBlank() && amount.isNotBlank()) {
            vm.call({ ApiClient.donate(campaignId,
                amount.toDoubleOrNull() ?: 0.0, words) }) { r ->
                onNote(r.exceptionOrNull()?.message) }
        }
    }
}


// The owner's workshop: a workflow pauses where the world has to answer,
// delegation is off until the owner declares it, a task's grant can die
// mid-run, and a rated placement resolves through the age wall.
@Composable
private fun WorkBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var flows by remember { mutableStateOf(listOf<String>()) }
    var goal by remember { mutableStateOf("") }
    var flowId by remember { mutableStateOf("") }
    var answer by remember { mutableStateOf("") }
    LaunchedEffect(vm.pid) {
        vm.call({ ApiClient.workflows(vm.pid!!, vm.token!!) }) { r ->
            flows = r.getOrNull() ?: emptyList() }
    }
    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("work.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        flows.forEach { Text(it, color = Qrme.T2, fontSize = 12.sp) }
        labeledField(L10n.t("work.goal", lang), goal, "") { goal = it }
        BrandButton(L10n.t("work.start", lang), enabled = goal.isNotBlank()) {
            vm.call({ ApiClient.startWorkflow(vm.pid!!, goal, vm.token!!) }) { r ->
                r.getOrNull()?.let { flowId = it; goal = "" }
                onNote(r.exceptionOrNull()?.message) }
        }
        labeledField(L10n.t("work.id", lang), flowId, "") { flowId = it }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("work.show", lang), enabled = flowId.isNotBlank()) {
                vm.call({ ApiClient.workflow(vm.pid!!, flowId, vm.token!!) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("work.advance", lang), enabled = flowId.isNotBlank()) {
                vm.call({ ApiClient.advanceWorkflow(vm.pid!!, flowId, vm.token!!) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("work.cancel", lang), enabled = flowId.isNotBlank()) {
                vm.call({ ApiClient.cancelWorkflow(vm.pid!!, flowId, vm.token!!) }) { r ->
                    onNote(r.exceptionOrNull()?.message) }
            }
        }
        labeledField(L10n.t("work.input", lang), answer, "") { answer = it }
        BrandButton(L10n.t("work.resume", lang),
            enabled = flowId.isNotBlank() && answer.isNotBlank()) {
            vm.call({ ApiClient.resumeWorkflow(vm.pid!!, flowId, answer,
                vm.token!!) }) { r ->
                answer = ""
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
    }
}

@Composable
private fun DeleBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var offer by remember { mutableStateOf("") }
    var phases by remember { mutableStateOf("draft,review") }
    var visitorId by remember { mutableStateOf("") }
    var goal by remember { mutableStateOf("") }
    var flowId by remember { mutableStateOf("") }
    var answer by remember { mutableStateOf("") }
    LaunchedEffect(vm.pid) {
        vm.call({ ApiClient.delegationOffer(vm.pid!!) }) { r ->
            offer = r.getOrNull() ?: "" }
    }
    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("dele.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        if (offer.isNotEmpty())
            Text(L10n.t("dele.offer", lang) + ": " + offer,
                color = Qrme.T2, fontSize = 12.sp)
        labeledField(L10n.t("dele.phases", lang), phases, "") { phases = it }
        BrandButton(L10n.t("dele.allow", lang), enabled = phases.isNotBlank()) {
            vm.call({ ApiClient.setDelegation(vm.pid!!,
                phases.split(",").map { it.trim() }, vm.token!!) }) { r ->
                onNote(r.exceptionOrNull()?.message) }
        }
        labeledField(L10n.t("people.add", lang), visitorId, "") { visitorId = it }
        labeledField(L10n.t("dele.goal", lang), goal, "") { goal = it }
        BrandButton(L10n.t("dele.start", lang),
            enabled = visitorId.isNotBlank() && goal.isNotBlank()) {
            vm.call({ ApiClient.startDelegatedWorkflow(vm.pid!!, visitorId,
                goal, vm.token!!) }) { r ->
                r.getOrNull()?.let { flowId = it; goal = "" }
                onNote(r.exceptionOrNull()?.message) }
        }
        labeledField(L10n.t("dele.id", lang), flowId, "") { flowId = it }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("dele.show", lang), enabled = flowId.isNotBlank()) {
                vm.call({ ApiClient.delegatedWorkflow(vm.pid!!, flowId,
                    vm.token!!) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("dele.advance", lang), enabled = flowId.isNotBlank()) {
                vm.call({ ApiClient.advanceDelegatedWorkflow(vm.pid!!, flowId,
                    vm.token!!) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
        }
        labeledField(L10n.t("work.input", lang), answer, "") { answer = it }
        BrandButton(L10n.t("dele.resume", lang),
            enabled = flowId.isNotBlank() && answer.isNotBlank()) {
            vm.call({ ApiClient.resumeDelegatedWorkflow(vm.pid!!, flowId,
                answer, vm.token!!) }) { r ->
                answer = ""
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
    }
}

@Composable
private fun AsstBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var works by remember { mutableStateOf(listOf<String>()) }
    var moment by remember { mutableStateOf("") }
    var draft by remember { mutableStateOf("") }
    var pile by remember { mutableStateOf("") }
    var criteria by remember { mutableStateOf("") }
    LaunchedEffect(vm.pid) {
        vm.call({ ApiClient.composedWorks(vm.pid!!, vm.token!!) }) { r ->
            works = r.getOrNull() ?: emptyList() }
    }
    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("asst.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        works.forEach { Text(it, color = Qrme.T2, fontSize = 12.sp) }
        labeledField(L10n.t("asst.moment", lang), moment, "") { moment = it }
        BrandButton(L10n.t("asst.compose", lang), enabled = moment.isNotBlank()) {
            vm.call({ ApiClient.composeNote(vm.pid!!, moment, vm.token!!) }) { r ->
                moment = ""
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        labeledField(L10n.t("asst.text", lang), draft, "") { draft = it }
        BrandButton(L10n.t("asst.proof", lang), enabled = draft.isNotBlank()) {
            vm.call({ ApiClient.proofread(vm.pid!!, draft, vm.token!!) }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        labeledField(L10n.t("asst.items", lang), pile, "") { pile = it }
        labeledField(L10n.t("asst.criteria", lang), criteria, "") { criteria = it }
        BrandButton(L10n.t("asst.triage", lang), enabled = pile.isNotBlank()) {
            vm.call({ ApiClient.triage(vm.pid!!,
                pile.split(";").map { it.trim() }, 1, criteria,
                vm.token!!) }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
    }
}

@Composable
private fun TaskBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var rows by remember { mutableStateOf(listOf<String>()) }
    var grantId by remember { mutableStateOf("") }
    var grantToken by remember { mutableStateOf("") }
    var topic by remember { mutableStateOf("") }
    LaunchedEffect(vm.pid) {
        vm.call({ ApiClient.tasksRun(vm.pid!!, vm.token!!) }) { r ->
            rows = r.getOrNull() ?: emptyList() }
    }
    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("task.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        rows.forEach { Text(it, color = Qrme.T2, fontSize = 12.sp) }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("task.grant", lang)) {
                vm.call({ ApiClient.mintTaskGrant(vm.pid!!, vm.token!!) }) { r ->
                    r.getOrNull()?.let { grantId = it.first
                        grantToken = it.second }
                    onNote(r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("task.revoke", lang),
                enabled = grantId.isNotBlank()) {
                vm.call({ ApiClient.revokeTaskGrant(grantId, vm.token!!) }) { r ->
                    grantId = ""; grantToken = ""
                    onNote(r.exceptionOrNull()?.message) }
            }
        }
        labeledField(L10n.t("task.topic", lang), topic, "") { topic = it }
        BrandButton(L10n.t("task.run", lang),
            enabled = topic.isNotBlank() && grantToken.isNotBlank()) {
            vm.call({ ApiClient.runTask(vm.pid!!, topic, grantToken,
                vm.token!!) }) { r ->
                topic = ""
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
    }
}

@Composable
private fun PlcBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var venues by remember { mutableStateOf(listOf<String>()) }
    var rows by remember { mutableStateOf(listOf<String>()) }
    var venue by remember { mutableStateOf("") }
    var label by remember { mutableStateOf("") }
    var placementId by remember { mutableStateOf("") }
    LaunchedEffect(vm.pid) {
        vm.call({ ApiClient.ratedVenues() }) { r ->
            venues = r.getOrNull() ?: emptyList() }
        vm.call({ ApiClient.placements(vm.pid!!, vm.token!!) }) { r ->
            rows = r.getOrNull() ?: emptyList() }
    }
    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("plc.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        if (venues.isNotEmpty())
            Text(L10n.t("plc.venues", lang) + ": " +
                venues.joinToString(", "), color = Qrme.T2, fontSize = 12.sp)
        rows.forEach { Text(it, color = Qrme.T2, fontSize = 12.sp) }
        labeledField(L10n.t("plc.venue", lang), venue, "") { venue = it }
        labeledField(L10n.t("plc.label", lang), label, "") { label = it }
        BrandButton(L10n.t("plc.place", lang), enabled = venue.isNotBlank()) {
            vm.call({ ApiClient.placeRated(vm.pid!!, venue, label,
                vm.token!!) }) { r ->
                r.getOrNull()?.let { placementId = it.first
                    onNote(it.second) }
                if (r.isFailure) onNote(r.exceptionOrNull()?.message) }
        }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("plc.stats", lang)) {
                vm.call({ ApiClient.placementAnalytics(vm.pid!!,
                    vm.token!!) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("plc.custody", lang)) {
                vm.call({ ApiClient.placementCustody(vm.pid!!,
                    vm.token!!) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
        }
        labeledField(L10n.t("plc.id", lang), placementId, "") { placementId = it }
        BrandButton(L10n.t("plc.remove", lang),
            enabled = placementId.isNotBlank()) {
            vm.call({ ApiClient.removePlacement(placementId, vm.token!!) }) { r ->
                placementId = ""
                onNote(r.exceptionOrNull()?.message) }
        }
    }
}

@Composable
private fun SpecBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var rows by remember { mutableStateOf(listOf<String>()) }
    var domain by remember { mutableStateOf("") }
    var specialistId by remember { mutableStateOf("") }
    LaunchedEffect(vm.pid) {
        vm.call({ ApiClient.specialists(vm.pid!!, vm.token!!) }) { r ->
            rows = r.getOrNull() ?: emptyList() }
    }
    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("spec.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        rows.forEach { Text(it, color = Qrme.T2, fontSize = 12.sp) }
        labeledField(L10n.t("spec.domain", lang), domain, "") { domain = it }
        labeledField(L10n.t("spec.id", lang), specialistId, "") { specialistId = it }
        BrandButton(L10n.t("spec.set", lang),
            enabled = domain.isNotBlank() && specialistId.isNotBlank()) {
            vm.call({ ApiClient.setSpecialist(vm.pid!!, domain, specialistId,
                vm.token!!) }) { r ->
                domain = ""; specialistId = ""
                onNote(r.exceptionOrNull()?.message) }
        }
    }
}


// The record, the veil and the exit: the memory list exists for choosing
// what to erase; the veil's limits are half the payload; the badge is a
// fact, not a word; and departing, memorializing and deleting are three
// different ends with three different buttons.
@Composable
private fun MemBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var rows by remember { mutableStateOf(listOf<String>()) }
    var visitorId by remember { mutableStateOf("") }
    var forgetWords by remember { mutableStateOf("") }
    LaunchedEffect(vm.pid) {
        vm.call({ ApiClient.memories(vm.pid!!, vm.token!!) }) { r ->
            rows = r.getOrNull() ?: emptyList() }
    }
    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("mem.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        rows.forEach { Text(it, color = Qrme.T2, fontSize = 12.sp) }
        labeledField(L10n.t("mem.id", lang), visitorId, "") { visitorId = it }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("mem.show", lang), enabled = visitorId.isNotBlank()) {
                // The remembrance leads: what the profile still carries of
                // this person past the recent window, then the last turns.
                vm.call({
                    val kept = runCatching {
                        ApiClient.remembrance(vm.pid!!, visitorId, vm.token!!)
                    }.getOrNull()
                    val recent = ApiClient.memory(vm.pid!!, visitorId,
                        vm.token!!).takeLast(3)
                    (listOfNotNull(kept) + recent).joinToString(" \u00b7 ")
                }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("mem.erase", lang), enabled = visitorId.isNotBlank()) {
                vm.call({ ApiClient.eraseMemory(vm.pid!!, visitorId,
                    vm.token!!) }) { r ->
                    visitorId = ""
                    onNote(r.exceptionOrNull()?.message) }
            }
            // The account: the kept paragraph and the honest counts.
            BrandButton(L10n.t("mem.account", lang), enabled = visitorId.isNotBlank()) {
                vm.call({ ApiClient.memoryAccount(vm.pid!!, visitorId,
                    vm.token!!) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
        }
        // Forget that one thing — the scalpel beside the erase-all.
        labeledField(L10n.t("mem.forget", lang), forgetWords,
            L10n.t("mem.forget.ph", lang)) { forgetWords = it }
        BrandButton(L10n.t("mem.forget", lang),
            enabled = visitorId.isNotBlank() && forgetWords.isNotBlank()) {
            vm.call({ ApiClient.forgetMemory(vm.pid!!, visitorId,
                forgetWords, vm.token!!) }) { r ->
                forgetWords = ""
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
    }
}

@Composable
private fun PairBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var visitorId by remember { mutableStateOf("") }
    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("who.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        labeledField(L10n.t("mem.id", lang), visitorId, "") { visitorId = it }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("who.thread", lang), enabled = visitorId.isNotBlank()) {
                vm.call({ ApiClient.thread(vm.pid!!, visitorId, vm.token!!) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("who.engagement", lang), enabled = visitorId.isNotBlank()) {
                vm.call({ ApiClient.engagement(vm.pid!!, visitorId,
                    vm.token!!) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
        }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("who.notes", lang), enabled = visitorId.isNotBlank()) {
                vm.call({ ApiClient.clinicalNotes(vm.pid!!, visitorId,
                    vm.token!!) }) { r ->
                    onNote(r.getOrNull()?.joinToString(" \u00b7 ")
                        ?: r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("who.embedding", lang), enabled = visitorId.isNotBlank()) {
                vm.call({ ApiClient.embedding(vm.pid!!, visitorId,
                    vm.token!!) }) { r ->
                    onNote(r.exceptionOrNull()?.message ?: "\u2713") }
            }
        }
    }
}

@Composable
private fun SrcBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var rows by remember { mutableStateOf(listOf<String>()) }
    var kind by remember { mutableStateOf("life_event") }
    var title by remember { mutableStateOf("") }
    var words by remember { mutableStateOf("") }
    LaunchedEffect(vm.pid) {
        vm.call({ ApiClient.sources(vm.pid!!, vm.token!!) }) { r ->
            rows = r.getOrNull() ?: emptyList() }
    }
    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("src.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        rows.forEach { Text(it, color = Qrme.T2, fontSize = 12.sp) }
        labeledField(L10n.t("src.kind", lang), kind, "") { kind = it }
        labeledField(L10n.t("src.name", lang), title, "") { title = it }
        labeledField(L10n.t("src.words", lang), words, "") { words = it }
        BrandButton(L10n.t("src.add", lang), enabled = words.isNotBlank()) {
            vm.call({ ApiClient.addSource(vm.pid!!, kind, title, words,
                vm.token!!) }) { r ->
                title = ""; words = ""
                onNote(r.exceptionOrNull()?.message) }
        }
    }
}

@Composable
private fun RecBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("rec.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("rec.transparency", lang)) {
                vm.call({ ApiClient.transparency(vm.pid!!) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("rec.stats", lang)) {
                vm.call({ ApiClient.profileStats(vm.pid!!, vm.token!!) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
        }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("rec.export", lang)) {
                vm.call({ ApiClient.exportProfile(vm.pid!!, vm.token!!) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("rec.feed", lang)) {
                vm.call({ ApiClient.feed(vm.pid!!) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
        }
    }
}

@Composable
private fun VeilBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("veil.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("veil.show", lang)) {
                vm.call({ ApiClient.anonymity(vm.pid!!, vm.token!!) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("veil.on", lang)) {
                vm.call({ ApiClient.setAnonymity(vm.pid!!, true,
                    vm.token!!) }) { r ->
                    onNote(r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("veil.off", lang)) {
                vm.call({ ApiClient.setAnonymity(vm.pid!!, false,
                    vm.token!!) }) { r ->
                    onNote(r.exceptionOrNull()?.message) }
            }
        }
    }
}

@Composable
private fun BadgeBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var level by remember { mutableStateOf("document") }
    var attestor by remember { mutableStateOf("") }
    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("ver.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("ver.show", lang)) {
                vm.call({ ApiClient.verification(vm.pid!!) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("ver.able", lang)) {
                vm.call({ ApiClient.verifiable(vm.pid!!, vm.token!!) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
        }
        labeledField(L10n.t("ver.level", lang), level, "") { level = it }
        labeledField(L10n.t("ver.attestor", lang), attestor, "") { attestor = it }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("ver.claim", lang), enabled = level.isNotBlank()) {
                vm.call({ ApiClient.claimVerification(vm.pid!!, level,
                    attestor, vm.token!!) }) { r ->
                    onNote(r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("ver.move", lang)) {
                vm.call({ ApiClient.moveBadgeHere(vm.pid!!, vm.token!!) }) { r ->
                    onNote(r.exceptionOrNull()?.message) }
            }
        }
    }
}

@Composable
private fun ExitBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var newName by remember { mutableStateOf("") }
    var newPersona by remember { mutableStateOf("") }
    var reference by remember { mutableStateOf("") }
    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("exit.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        labeledField(L10n.t("exit.rename", lang), newName, "") { newName = it }
        labeledField(L10n.t("exit.persona", lang), newPersona, "") { newPersona = it }
        BrandButton(L10n.t("exit.save", lang),
            enabled = newName.isNotBlank() || newPersona.isNotBlank()) {
            vm.call({ ApiClient.editProfile(vm.pid!!, newName, newPersona,
                vm.token!!) }) { r ->
                newName = ""; newPersona = ""
                onNote(r.exceptionOrNull()?.message) }
        }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("exit.siblings", lang)) {
                vm.call({ ApiClient.siblings(vm.pid!!, vm.token!!) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("exit.memorial", lang)) {
                vm.call({ ApiClient.memorial(vm.pid!!) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
        }
        labeledField(L10n.t("exit.ref", lang), reference, "") { reference = it }
        BrandButton(L10n.t("exit.succeed", lang),
            enabled = reference.isNotBlank()) {
            vm.call({ ApiClient.succeed(vm.pid!!, reference, vm.token!!) }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("exit.sunset", lang)) {
                vm.call({ ApiClient.sunset(vm.pid!!, vm.token!!) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("exit.delete", lang)) {
                vm.call({ ApiClient.deleteProfile(vm.pid!!, vm.token!!) }) { r ->
                    onNote(r.exceptionOrNull()?.message) }
            }
        }
    }
}


// The face it shows the world: the portrait carries its own honesty, the
// badge a reader sees withholds what would undo a veil, the blend is
// provenance, the same personality lives in every body, and dials are
// 0-100 integers that never raise intimacy on a non-rated persona.
@Composable
private fun AvaBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var asset by remember { mutableStateOf("") }
    var handle by remember { mutableStateOf("") }
    var importUrl by remember { mutableStateOf("") }
    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("ava.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("ava.show", lang)) {
                vm.call({ ApiClient.avatar(vm.pid!!) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("ava.briefs", lang)) {
                vm.call({ ApiClient.avatarBriefs() }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
        }
        labeledField(L10n.t("ava.asset", lang), asset, "") { asset = it }
        BrandButton(L10n.t("ava.set", lang), enabled = asset.isNotBlank()) {
            vm.call({ ApiClient.setAvatar(vm.pid!!, asset, vm.token!!) }) { r ->
                asset = ""
                onNote(r.exceptionOrNull()?.message) }
        }
        labeledField(L10n.t("people.add", lang), handle, "") { handle = it }
        BrandButton(L10n.t("ava.brief", lang), enabled = handle.isNotBlank()) {
            vm.call({ ApiClient.avatarBrief(handle) }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        Text(L10n.t("ava.market", lang), color = Qrme.Txt, fontSize = 13.sp,
            fontWeight = FontWeight.Bold)
        labeledField(L10n.t("ava.url.ph", lang), importUrl, "") { importUrl = it }
        BrandButton(L10n.t("ava.import", lang), enabled = importUrl.isNotBlank()) {
            vm.call({
                val n = ApiClient.avatarMarket()
                ApiClient.importAvatar(vm.pid!!, "other", importUrl, vm.token!!)
                n
            }) { r ->
                importUrl = ""
                onNote(r.getOrNull()?.toString() ?: r.exceptionOrNull()?.message) }
        }
    }
}

@Composable
private fun EmblBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var emblem by remember { mutableStateOf("") }
    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("embl.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("embl.list", lang)) {
                vm.call({ ApiClient.identityEmblems() }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("embl.rules", lang)) {
                vm.call({ ApiClient.identityVocabulary() }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("embl.badge", lang)) {
                vm.call({ ApiClient.badge(vm.pid!!) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
        }
        labeledField(L10n.t("embl.pick", lang), emblem, "") { emblem = it }
        BrandButton(L10n.t("embl.set", lang), enabled = emblem.isNotBlank()) {
            vm.call({ ApiClient.setEmblem(vm.pid!!, emblem, vm.token!!) }) { r ->
                emblem = ""
                onNote(r.exceptionOrNull()?.message) }
        }
    }
}

@Composable
private fun PgBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var theme by remember { mutableStateOf("") }
    var tagline by remember { mutableStateOf("") }
    var about by remember { mutableStateOf("") }
    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("pg.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("pg.show", lang)) {
                vm.call({ ApiClient.page(vm.pid!!) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("pg.themes", lang)) {
                vm.call({ ApiClient.pageThemes() }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("front.show", lang)) {
                vm.call({ ApiClient.frontPage(vm.pid!!) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
        }
        labeledField(L10n.t("pg.theme", lang), theme, "") { theme = it }
        labeledField(L10n.t("pg.tagline", lang), tagline, "") { tagline = it }
        labeledField(L10n.t("pg.about", lang), about, "") { about = it }
        BrandButton(L10n.t("pg.save", lang),
            enabled = theme.isNotBlank() || tagline.isNotBlank() ||
                about.isNotBlank()) {
            vm.call({ ApiClient.editPage(vm.pid!!, theme, tagline, about,
                vm.token!!) }) { r ->
                theme = ""; tagline = ""; about = ""
                onNote(r.exceptionOrNull()?.message) }
        }
    }
}

@Composable
private fun SurfBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var listed by remember { mutableStateOf("") }
    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("surf.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("surf.list", lang)) {
                vm.call({ ApiClient.surfaces(vm.pid!!) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("comp.show", lang)) {
                vm.call({ ApiClient.composition(vm.pid!!) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
        }
        labeledField(L10n.t("surf.title", lang), listed, "") { listed = it }
        BrandButton(L10n.t("surf.set", lang), enabled = listed.isNotBlank()) {
            vm.call({ ApiClient.setSurfaces(vm.pid!!,
                listed.split(",").map { it.trim() }, vm.token!!) }) { r ->
                listed = ""
                onNote(r.exceptionOrNull()?.message) }
        }
    }
}

@Composable
private fun FormBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var rows by remember { mutableStateOf(listOf<String>()) }
    var name by remember { mutableStateOf("") }
    var kind by remember { mutableStateOf("speaker") }
    var screenLabel by remember { mutableStateOf("") }
    LaunchedEffect(vm.pid) {
        vm.call({ ApiClient.embodiments(vm.pid!!, vm.token!!) }) { r ->
            rows = r.getOrNull() ?: emptyList() }
    }
    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("form.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        rows.forEach { Text(it, color = Qrme.T2, fontSize = 12.sp) }
        labeledField(L10n.t("form.name", lang), name, "") { name = it }
        labeledField(L10n.t("form.kind", lang), kind, "") { kind = it }
        BrandButton(L10n.t("form.add", lang), enabled = name.isNotBlank()) {
            vm.call({ ApiClient.addEmbodiment(vm.pid!!, name, kind,
                vm.token!!) }) { r ->
                name = ""
                onNote(r.exceptionOrNull()?.message) }
        }
        BrandButton(L10n.t("form.same", lang)) {
            vm.call({ ApiClient.embodimentConsistency(vm.pid!!) }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        labeledField(L10n.t("plc.label", lang), screenLabel, "") { screenLabel = it }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            BrandButton(L10n.t("disp.title", lang)) {
                vm.call({ ApiClient.profileDisplays(vm.pid!!, vm.token!!) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
            BrandButton(L10n.t("src.add", lang),
                enabled = screenLabel.isNotBlank()) {
                vm.call({ ApiClient.addProfileDisplay(vm.pid!!, "wall_panel",
                    screenLabel, vm.token!!) }) { r ->
                    screenLabel = ""
                    onNote(r.exceptionOrNull()?.message) }
            }
        }
    }
}

@Composable
private fun SteerBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var pace by remember { mutableStateOf("") }
    var autonomy by remember { mutableStateOf("") }
    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("steer.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        BrandButton(L10n.t("steer.show", lang)) {
            vm.call({ ApiClient.steering(vm.pid!!, vm.token!!) }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        labeledField(L10n.t("steer.pace", lang), pace, "") { pace = it }
        labeledField(L10n.t("steer.autonomy", lang), autonomy, "") { autonomy = it }
        BrandButton(L10n.t("steer.set", lang),
            enabled = pace.isNotBlank() || autonomy.isNotBlank()) {
            vm.call({
                val values = buildMap {
                    pace.toIntOrNull()?.let { put("pace", it) }
                    autonomy.toIntOrNull()?.let { put("autonomy", it) }
                }
                ApiClient.setSteering(vm.pid!!, values, vm.token!!)
            }) { r ->
                pace = ""; autonomy = ""
                onNote(r.exceptionOrNull()?.message) }
        }
    }
}

@Composable
private fun WristBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var target by remember { mutableStateOf("workflow") }
    var targetId by remember { mutableStateOf("") }
    var action by remember { mutableStateOf("advance") }
    var answer by remember { mutableStateOf("") }
    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("wrist.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        BrandButton(L10n.t("wrist.show", lang)) {
            vm.call({ ApiClient.watchFace(vm.pid!!, vm.token!!) }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        labeledField(L10n.t("wrist.target", lang), target, "") { target = it }
        labeledField(L10n.t("wrist.id", lang), targetId, "") { targetId = it }
        labeledField(L10n.t("wrist.action", lang), action, "") { action = it }
        labeledField(L10n.t("wrist.input", lang), answer, "") { answer = it }
        BrandButton(L10n.t("wrist.act", lang),
            enabled = targetId.isNotBlank() && action.isNotBlank()) {
            vm.call({ ApiClient.watchAct(vm.pid!!, target, targetId, action,
                answer, vm.token!!) }) { r ->
                answer = ""
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
    }
}


@Composable
private fun AcctBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var name by remember { mutableStateOf("") }
    var code by remember { mutableStateOf("") }
    var newPassword by remember { mutableStateOf("") }
    var oauthState by remember { mutableStateOf("") }
    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("acct.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        labeledField(L10n.t("acct.email", lang), email, "") { email = it }
        labeledField(L10n.t("acct.password", lang), password, "") {
            password = it }
        labeledField(L10n.t("acct.name", lang), name, "") { name = it }
        BrandButton(L10n.t("acct.signup", lang),
            enabled = email.isNotBlank() && password.isNotBlank()) {
            vm.call({ ApiClient.signup(email, password, name) }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        BrandButton(L10n.t("acct.signin", lang),
            enabled = email.isNotBlank() && password.isNotBlank()) {
            vm.call({ ApiClient.signin(email, password) }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        labeledField(L10n.t("acct.code", lang), code, "") { code = it }
        BrandButton(L10n.t("acct.verify", lang),
            enabled = email.isNotBlank() && code.isNotBlank()) {
            vm.call({ ApiClient.verifyEmail(email, code) }) { r ->
                code = ""
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        BrandButton(L10n.t("acct.resend", lang),
            enabled = email.isNotBlank()) {
            vm.call({ ApiClient.resendCode(email) }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        BrandButton(L10n.t("acct.reset.request", lang),
            enabled = email.isNotBlank()) {
            vm.call({ ApiClient.requestPasswordReset(email) }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        labeledField(L10n.t("acct.reset.new", lang), newPassword, "") {
            newPassword = it }
        BrandButton(L10n.t("acct.reset.do", lang),
            enabled = email.isNotBlank() && code.isNotBlank() &&
                newPassword.isNotBlank()) {
            vm.call({ ApiClient.resetPassword(email, code, newPassword) }) {
                r -> newPassword = ""
                onNote(if (r.getOrNull() == true) "\u2713"
                       else r.exceptionOrNull()?.message) }
        }
        BrandButton(L10n.t("acct.oauth", lang)) {
            vm.call({
                val doors = ApiClient.oauthProviders()
                if (doors.isEmpty()) "\u2014" else {
                    val (st, url) = ApiClient.oauthStart(doors.first())
                    oauthState = st
                    doors.first() + " \u00b7 " + url
                }
            }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        if (oauthState.isNotBlank()) {
            BrandButton("\u21bb") {
                vm.call({ ApiClient.oauthClaim(oauthState) }) { r ->
                    onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
            }
        }
    }
}

@Composable
private fun TillBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var subId by remember { mutableStateOf("") }
    var beneficiary by remember { mutableStateOf("") }
    var designee by remember { mutableStateOf("") }
    var campTitle by remember { mutableStateOf("") }
    var campGoal by remember { mutableStateOf("") }
    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("till.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        BrandButton(L10n.t("till.plans", lang)) {
            vm.call({ ApiClient.plans() }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        BrandButton(L10n.t("till.subs", lang)) {
            vm.call({ ApiClient.mySubscriptions(vm.token!!) }) { r ->
                onNote(r.getOrNull()?.toString()
                    ?: r.exceptionOrNull()?.message) }
        }
        BrandButton(L10n.t("till.orders", lang)) {
            vm.call({ ApiClient.myOrders(vm.token!!) }) { r ->
                onNote(r.getOrNull()?.toString()
                    ?: r.exceptionOrNull()?.message) }
        }
        labeledField(L10n.t("wrist.id", lang), subId, "") { subId = it }
        labeledField(L10n.t("till.beneficiary", lang), beneficiary, "") {
            beneficiary = it }
        BrandButton(L10n.t("till.renew", lang),
            enabled = subId.isNotBlank() && beneficiary.isNotBlank()) {
            vm.call({ ApiClient.renewSubscription(subId, beneficiary,
                vm.token!!) }) { r ->
                onNote(r.getOrNull()?.toString()
                    ?: r.exceptionOrNull()?.message) }
        }
        BrandButton(L10n.t("till.proceeds", lang)) {
            vm.call({ ApiClient.proceedsOf(vm.pid!!) }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        labeledField(L10n.t("till.designees", lang), designee, "") {
            designee = it }
        BrandButton(L10n.t("till.set", lang),
            enabled = designee.isNotBlank()) {
            vm.call({ ApiClient.setProceeds(vm.pid!!, designee,
                vm.token!!) }) { r ->
                designee = ""
                onNote(if (r.isSuccess) "\u2713"
                       else r.exceptionOrNull()?.message) }
        }
        BrandButton(L10n.t("till.campaigns", lang)) {
            vm.call({ ApiClient.campaignsOf(vm.pid!!) }) { r ->
                onNote(r.getOrNull()?.toString()
                    ?: r.exceptionOrNull()?.message) }
        }
        labeledField(L10n.t("till.camp.title", lang), campTitle, "") {
            campTitle = it }
        labeledField(L10n.t("till.camp.goal", lang), campGoal, "") {
            campGoal = it }
        BrandButton(L10n.t("till.camp.add", lang),
            enabled = campTitle.isNotBlank() && campGoal.isNotBlank()) {
            vm.call({ ApiClient.addCampaign(vm.pid!!, campTitle,
                campGoal.toDoubleOrNull() ?: 0.0, vm.token!!) }) { r ->
                campTitle = ""; campGoal = ""
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
    }
}

@Composable
private fun LifeBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var question by remember { mutableStateOf("") }
    var provName by remember { mutableStateOf("") }
    var provArea by remember { mutableStateOf("") }
    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("life.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        BrandButton(L10n.t("life.cloud", lang)) {
            vm.call({ ApiClient.cloudStatus() }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        BrandButton(L10n.t("life.offline", lang)) {
            vm.call({ ApiClient.offlineStatus() }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        BrandButton(L10n.t("life.lights", lang)) {
            vm.call({ ApiClient.agentLights() }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        BrandButton(L10n.t("life.help.topics", lang)) {
            vm.call({ ApiClient.helpTopics() }) { r ->
                onNote(r.getOrNull()?.toString()
                    ?: r.exceptionOrNull()?.message) }
        }
        labeledField(L10n.t("life.help", lang), question, "") {
            question = it }
        BrandButton(L10n.t("life.help.ask", lang),
            enabled = question.isNotBlank()) {
            vm.call({ ApiClient.askHelp(question) }) { r ->
                question = ""
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        BrandButton(L10n.t("life.providers", lang)) {
            vm.call({ ApiClient.localProviders() }) { r ->
                onNote(r.getOrNull()?.toString()
                    ?: r.exceptionOrNull()?.message) }
        }
        labeledField(L10n.t("life.prov.name", lang), provName, "") {
            provName = it }
        labeledField(L10n.t("life.prov.area", lang), provArea, "") {
            provArea = it }
        BrandButton(L10n.t("life.prov.add", lang),
            enabled = provName.isNotBlank() && provArea.isNotBlank()) {
            vm.call({ ApiClient.addLocalProvider(provName, provArea) }) { r ->
                provName = ""; provArea = ""
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
    }
}


@Composable
private fun BcnBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var beaconId by remember { mutableStateOf("") }
    var cid by remember { mutableStateOf("") }
    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("bcn.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        labeledField(L10n.t("bcn.id", lang), beaconId, "") { beaconId = it }
        BrandButton(L10n.t("bcn.card", lang),
            enabled = beaconId.isNotBlank()) {
            vm.call({ ApiClient.beaconOverlayCard(beaconId) }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        BrandButton(L10n.t("bcn.desk", lang),
            enabled = beaconId.isNotBlank()) {
            vm.call({ ApiClient.deskScanCard(beaconId) }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        BrandButton(L10n.t("bcn.qr", lang),
            enabled = beaconId.isNotBlank()) {
            onNote(ApiClient.beaconQrUrl(beaconId) + " \u00b7 " +
                ApiClient.beaconScanUrl(beaconId) + " \u00b7 " +
                ApiClient.deskScanUrl(beaconId))
        }
        labeledField(L10n.t("people.add", lang), cid, "") { cid = it }
        BrandButton(L10n.t("bcn.social", lang), enabled = cid.isNotBlank()) {
            vm.call({ ApiClient.socialBeacon(cid) +
                " \u00b7 " + ApiClient.socialQrUrl(cid) }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        BrandButton(L10n.t("bcn.pair", lang)) {
            vm.call({ ApiClient.pairing() + " \u00b7 " +
                ApiClient.pairQrUrl() }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
    }
}

@Composable
private fun ModqBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var messageId by remember { mutableStateOf("") }
    var interactorId by remember { mutableStateOf("") }
    var content by remember { mutableStateOf("") }
    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("modq.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        BrandButton(L10n.t("modq.show", lang)) {
            vm.call({ ApiClient.moderationQueue(vm.pid!!, vm.token!!) }) { r ->
                onNote(r.getOrNull()?.toString()
                    ?: r.exceptionOrNull()?.message) }
        }
        labeledField(L10n.t("modq.msg", lang), messageId, "") {
            messageId = it }
        BrandButton(L10n.t("modq.approve", lang),
            enabled = messageId.isNotBlank()) {
            vm.call({ ApiClient.approveMessage(messageId, vm.token!!) }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        BrandButton(L10n.t("modq.reject", lang),
            enabled = messageId.isNotBlank()) {
            vm.call({ ApiClient.rejectMessage(messageId, vm.token!!) }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        labeledField(L10n.t("people.add", lang), interactorId, "") {
            interactorId = it }
        labeledField(L10n.t("modq.edit", lang), content, "") { content = it }
        BrandButton(L10n.t("modq.edit", lang),
            enabled = messageId.isNotBlank() && interactorId.isNotBlank() &&
                content.isNotBlank()) {
            vm.call({ ApiClient.editMessage(vm.pid!!, messageId,
                interactorId, content, vm.token!!) }) { r ->
                content = ""
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        BrandButton(L10n.t("modq.retract", lang),
            enabled = messageId.isNotBlank() && interactorId.isNotBlank()) {
            vm.call({ ApiClient.retractMessage(vm.pid!!, messageId,
                interactorId, vm.token!!) }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
    }
}

@Composable
private fun RevwBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var interactorId by remember { mutableStateOf("") }
    var rating by remember { mutableStateOf("") }
    var text by remember { mutableStateOf("") }
    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("revw.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        BrandButton(L10n.t("revw.show", lang)) {
            vm.call({ ApiClient.reviewsOf(vm.pid!!) }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        labeledField(L10n.t("people.add", lang), interactorId, "") {
            interactorId = it }
        labeledField(L10n.t("revw.rating", lang), rating, "") { rating = it }
        labeledField(L10n.t("revw.body", lang), text, "") { text = it }
        BrandButton(L10n.t("revw.leave", lang),
            enabled = interactorId.isNotBlank() && rating.isNotBlank()) {
            vm.call({ ApiClient.leaveReview(vm.pid!!, interactorId,
                rating.toIntOrNull() ?: 0, text, vm.token!!) }) { r ->
                text = ""
                onNote(r.getOrNull()?.toString()
                    ?: r.exceptionOrNull()?.message) }
        }
    }
}

@Composable
private fun WmBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var wmId by remember { mutableStateOf("") }
    var content by remember { mutableStateOf("") }
    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("wm.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        labeledField(L10n.t("wm.id", lang), wmId, "") { wmId = it }
        BrandButton(L10n.t("wm.resolve", lang), enabled = wmId.isNotBlank()) {
            vm.call({ ApiClient.watermarkCredential(wmId) }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        labeledField(L10n.t("wm.content", lang), content, "") { content = it }
        BrandButton(L10n.t("wm.verify", lang), enabled = wmId.isNotBlank()) {
            vm.call({ ApiClient.verifyWatermark(wmId, content) }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
    }
}

@Composable
private fun MedBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var filename by remember { mutableStateOf("") }
    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("med.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        BrandButton(L10n.t("med.limits", lang)) {
            vm.call({ ApiClient.mediaLimits() }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        BrandButton(L10n.t("med.platforms", lang)) {
            vm.call({ ApiClient.videoPlatforms() }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        labeledField(L10n.t("wear.name", lang), filename, "") {
            filename = it }
        BrandButton(L10n.t("med.upload", lang),
            enabled = filename.isNotBlank()) {
            vm.call({ ApiClient.uploadMedia(vm.pid!!, filename,
                "QRME".toByteArray(), vm.token!!) }) { r ->
                filename = ""
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
    }
}

@Composable
private fun WearBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var name by remember { mutableStateOf("") }
    var kind by remember { mutableStateOf("watch") }
    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("wear.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        BrandButton(L10n.t("wear.list", lang)) {
            vm.call({ ApiClient.wearables(vm.pid!!, vm.token!!) }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        labeledField(L10n.t("wear.name", lang), name, "") { name = it }
        labeledField(L10n.t("wear.kind", lang), kind, "") { kind = it }
        BrandButton(L10n.t("wear.pair", lang),
            enabled = name.isNotBlank() && kind.isNotBlank()) {
            vm.call({ ApiClient.pairWearable(vm.pid!!, name, kind,
                vm.token!!) }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        BrandButton(L10n.t("wear.unpair", lang),
            enabled = name.isNotBlank()) {
            vm.call({ ApiClient.unpairWearable(vm.pid!!, name,
                vm.token!!) }) { r ->
                name = ""
                onNote(if (r.getOrNull() == true) "\u2713"
                       else r.exceptionOrNull()?.message) }
        }
    }
}


@Composable
private fun BornBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var owner by remember { mutableStateOf("") }
    var name by remember { mutableStateOf("") }
    var social by remember { mutableStateOf("") }
    var humor by remember { mutableStateOf("") }
    var matters by remember { mutableStateOf("") }
    var comfort by remember { mutableStateOf("") }
    var sources by remember { mutableStateOf("") }
    var industry by remember { mutableStateOf("") }
    var packTitle by remember { mutableStateOf("") }
    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("born.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        labeledField(L10n.t("born.owner", lang), owner, "") { owner = it }
        labeledField(L10n.t("born.name", lang), name, "") { name = it }
        labeledField(L10n.t("born.social", lang), social, "") { social = it }
        labeledField(L10n.t("born.humor", lang), humor, "") { humor = it }
        labeledField(L10n.t("born.matters", lang), matters, "") {
            matters = it }
        labeledField(L10n.t("born.comfort", lang), comfort, "") {
            comfort = it }
        BrandButton(L10n.t("born.make", lang),
            enabled = owner.isNotBlank() && social.isNotBlank() &&
                humor.isNotBlank() && matters.isNotBlank() &&
                comfort.isNotBlank()) {
            vm.call({ ApiClient.genesis(owner, name, social, humor,
                matters, comfort) }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        labeledField(L10n.t("born.sources", lang), sources, "") {
            sources = it }
        BrandButton(L10n.t("born.blend", lang),
            enabled = owner.isNotBlank() && name.isNotBlank() &&
                sources.isNotBlank()) {
            vm.call({ ApiClient.composite(owner, name,
                sources.split(",").map { it.trim() }) }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        labeledField(L10n.t("born.pack.industry", lang), industry, "") {
            industry = it }
        labeledField(L10n.t("born.pack.title", lang), packTitle, "") {
            packTitle = it }
        BrandButton(L10n.t("born.pack.publish", lang),
            enabled = industry.isNotBlank() && packTitle.isNotBlank()) {
            vm.call({ ApiClient.publishPack(industry, packTitle,
                vm.token!!) }) { r ->
                packTitle = ""
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        BrandButton(L10n.t("born.pack.seed", lang)) {
            vm.call({ ApiClient.seedPacks() }) { r ->
                onNote(r.getOrNull()?.toString()
                    ?: r.exceptionOrNull()?.message) }
        }
    }
}

@Composable
private fun MindBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var scenario by remember { mutableStateOf("") }
    var cid by remember { mutableStateOf("") }
    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("mind.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        labeledField(L10n.t("mind.scenario", lang), scenario, "") {
            scenario = it }
        BrandButton(L10n.t("mind.simulate", lang),
            enabled = scenario.isNotBlank()) {
            vm.call({ ApiClient.simulate(vm.pid!!, scenario,
                vm.token!!) }) { r ->
                scenario = ""
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        BrandButton(L10n.t("mind.runs", lang)) {
            vm.call({ ApiClient.simulations(vm.pid!!, vm.token!!) }) { r ->
                onNote(r.getOrNull()?.toString()
                    ?: r.exceptionOrNull()?.message) }
        }
        BrandButton(L10n.t("mind.tune", lang)) {
            vm.call({ ApiClient.finetune(vm.pid!!, vm.token!!) }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        BrandButton(L10n.t("mind.cloud", lang)) {
            vm.call({ ApiClient.cloudContribution(vm.pid!!,
                vm.token!!) }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        BrandButton(L10n.t("mind.revoke", lang)) {
            vm.call({ ApiClient.revokeContributions(vm.pid!!,
                vm.token!!) }) { r ->
                onNote(r.getOrNull()?.toString()
                    ?: r.exceptionOrNull()?.message) }
        }
        labeledField(L10n.t("people.add", lang), cid, "") { cid = it }
        BrandButton(L10n.t("mind.excursion", lang),
            enabled = cid.isNotBlank()) {
            vm.call({ ApiClient.excursion(cid, vm.token!!) }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
    }
}

@Composable
private fun ReachBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var quietStart by remember { mutableStateOf("") }
    var quietEnd by remember { mutableStateOf("") }
    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("reach.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        BrandButton(L10n.t("reach.checkin", lang),
            enabled = vm.interactorId != null) {
            vm.call({ ApiClient.proactiveCheckin(vm.pid!!,
                vm.interactorId!!, vm.token!!) }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        BrandButton(L10n.t("reach.rate.up", lang),
            enabled = vm.interactorId != null) {
            vm.call({ ApiClient.giveFeedback(vm.pid!!, vm.interactorId!!,
                "up", vm.interactorToken!!) }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        BrandButton(L10n.t("reach.rate.down", lang),
            enabled = vm.interactorId != null) {
            vm.call({ ApiClient.giveFeedback(vm.pid!!, vm.interactorId!!,
                "down", vm.interactorToken!!) }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        labeledField(L10n.t("reach.quiet.start", lang), quietStart, "") {
            quietStart = it }
        labeledField(L10n.t("reach.quiet.end", lang), quietEnd, "") {
            quietEnd = it }
        BrandButton(L10n.t("reach.quiet.set", lang),
            enabled = vm.interactorId != null) {
            vm.call({ ApiClient.setQuietHours(vm.interactorId!!,
                quietStart.toIntOrNull(), quietEnd.toIntOrNull(),
                vm.interactorToken!!) }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        BrandButton(L10n.t("reach.referrals", lang),
            enabled = vm.interactorId != null) {
            vm.call({ ApiClient.myReferrals(vm.interactorId!!,
                vm.interactorToken!!) }) { r ->
                onNote(r.getOrNull()?.toString()
                    ?: r.exceptionOrNull()?.message) }
        }
    }
}

@Composable
private fun LicBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var grantId by remember { mutableStateOf("") }
    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("lic.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        BrandButton(L10n.t("lic.acquire", lang),
            enabled = vm.interactorId != null) {
            vm.call({ ApiClient.acquireLicense(vm.pid!!,
                vm.interactorToken!!) }) { r ->
                grantId = r.getOrNull() ?: grantId
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        labeledField(L10n.t("lic.grant", lang), grantId, "") { grantId = it }
        BrandButton(L10n.t("lic.derive", lang),
            enabled = grantId.isNotBlank() && vm.interactorId != null) {
            vm.call({ ApiClient.deriveAgent(vm.pid!!, grantId,
                vm.interactorToken!!) }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
    }
}

@Composable
private fun SensBlock(vm: StudioViewModel, onNote: (String?) -> Unit) {
    val lang = L10n.deviceLanguage()
    var scene by remember { mutableStateOf("") }
    var goal by remember { mutableStateOf("") }
    var expTitle by remember { mutableStateOf("") }
    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("sens.title", lang), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        labeledField(L10n.t("sens.scene", lang), scene, "") { scene = it }
        labeledField(L10n.t("wrist.input", lang), goal, "") { goal = it }
        BrandButton(L10n.t("sens.perceive", lang),
            enabled = scene.isNotBlank()) {
            vm.call({ ApiClient.perceive(vm.pid!!,
                scene.split(",").map { it.trim() }, goal,
                vm.token!!) }) { r ->
                scene = ""; goal = ""
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        BrandButton(L10n.t("sens.mics", lang)) {
            vm.call({ ApiClient.microphonePlaces() }) { r ->
                onNote(r.getOrNull()?.toString()
                    ?: r.exceptionOrNull()?.message) }
        }
        BrandButton(L10n.t("sens.vocab", lang)) {
            vm.call({ ApiClient.microphoneVocabulary() }) { r ->
                onNote(r.getOrNull()?.toString()
                    ?: r.exceptionOrNull()?.message) }
        }
        BrandButton(L10n.t("sens.overlays", lang)) {
            vm.call({ ApiClient.overlaysCatalogue() }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        labeledField(L10n.t("sens.exp", lang), expTitle, "") { expTitle = it }
        BrandButton(L10n.t("sens.exp.set", lang),
            enabled = expTitle.isNotBlank()) {
            vm.call({ ApiClient.setExperience(vm.pid!!, expTitle,
                vm.token!!) }) { r ->
                expTitle = ""
                onNote(r.getOrNull()?.toString()
                    ?: r.exceptionOrNull()?.message) }
        }
        BrandButton(L10n.t("life.status", lang)) {
            vm.call({ ApiClient.health() + " \u00b7 " +
                ApiClient.marketplaceListings() + " \u00b7 " +
                ApiClient.listPacks() + " \u00b7 " +
                ApiClient.signaturePolicy() }) { r ->
                onNote(r.getOrNull() ?: r.exceptionOrNull()?.message) }
        }
        labeledField(L10n.t("lic.grant", lang), expTitle, "") { expTitle = it }
        BrandButton(L10n.t("exit.delete", lang),
            enabled = expTitle.isNotBlank()) {
            vm.call({ ApiClient.removeSigningCredential(expTitle,
                vm.token!!) }) { r ->
                onNote(if (r.isSuccess) "\u2713"
                       else r.exceptionOrNull()?.message) }
        }
    }
}

// ---- Standing behind the counter: desks, the market, exchanges ----
//
// The caller's side shipped long ago. What no shell could do was the
// other side of the same counter — open a desk, staff it, decide who
// comes through, print its sticker — nor search, price, sell or buy in
// the market, nor be a party to an exchange at all.
@Composable
private fun CounterPanel(vm: StudioViewModel) {
    val lang = L10n.deviceLanguage()
    var deskId by remember { mutableStateOf("") }
    var deskToken by remember { mutableStateOf("") }
    var camUrl by remember { mutableStateOf("") }
    var displayName by remember { mutableStateOf("") }
    var trade by remember { mutableStateOf("") }
    var attestor by remember { mutableStateOf("") }
    var basis by remember { mutableStateOf("") }
    var location by remember { mutableStateOf("") }
    var blurb by remember { mutableStateOf("") }
    var card by remember { mutableStateOf<DeskOpened?>(null) }
    var nearby by remember { mutableStateOf<List<DeskBrief>>(emptyList()) }
    var rings by remember { mutableStateOf<List<DeskRing>>(emptyList()) }
    var guests by remember { mutableStateOf<List<DeskGuest>>(emptyList()) }
    var beacons by remember { mutableStateOf<List<DeskBeacon>>(emptyList()) }
    var beaconLabel by remember { mutableStateOf("") }
    var overlay by remember { mutableStateOf<DeskOverlay?>(null) }
    var staffedBy by remember { mutableStateOf<String?>(null) }
    var knockNote by remember { mutableStateOf("") }
    var note by remember { mutableStateOf<String?>(null) }

    // The three presences the backend accepts, offered as the closed set
    // it is — a free field would earn the refusal on every typo.
    val presences = listOf("attended", "away", "closed")

    fun reload() {
        vm.call({ ApiClient.desks() }) { r -> nearby = r.getOrDefault(emptyList()) }
        if (deskId.isBlank()) return
        vm.call({ ApiClient.deskOverlay(deskId) }) { r -> overlay = r.getOrNull() }
        vm.call({ ApiClient.deskLivePerson(deskId) }) { r -> staffedBy = r.getOrNull() }
        if (deskToken.isBlank()) return
        vm.call({ ApiClient.deskRings(deskId, deskToken) }) { r -> rings = r.getOrDefault(emptyList()) }
        vm.call({ ApiClient.deskGuests(deskId, deskToken) }) { r -> guests = r.getOrDefault(emptyList()) }
        vm.call({ ApiClient.deskBeacons(deskId, deskToken) }) { r -> beacons = r.getOrDefault(emptyList()) }
    }
    LaunchedEffect(Unit) { reload() }

    fun act(op: suspend () -> Unit) {
        note = null
        vm.call({ op() }) { r ->
            r.exceptionOrNull()?.let { note = it.message }
            reload()
        }
    }

    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("counter.open", lang), color = Qrme.Txt, fontSize = 16.sp,
                fontWeight = FontWeight.Bold)
            Text(L10n.t("counter.attested", lang), color = Qrme.T2, fontSize = 11.sp)
            labeledField(L10n.t("counter.name", lang), displayName, "") { displayName = it }
            labeledField(L10n.t("counter.trade", lang), trade, "") { trade = it }
            labeledField(L10n.t("counter.attestor", lang), attestor, "") { attestor = it }
            labeledField(L10n.t("counter.basis", lang), basis, "") { basis = it }
            labeledField(L10n.t("counter.where", lang), location, "") { location = it }
            labeledField(L10n.t("counter.blurb", lang), blurb, "") { blurb = it }
            BrandButton(L10n.t("counter.open.go", lang),
                        enabled = displayName.isNotBlank() && trade.isNotBlank()
                                  && attestor.isNotBlank() && basis.isNotBlank()) {
                vm.call({ ApiClient.openDesk(vm.pid!!, displayName, trade, attestor,
                    basis, location, blurb, vm.token!!) }) { r ->
                    r.exceptionOrNull()?.let { note = it.message }
                    r.getOrNull()?.let {
                        card = it; deskId = it.deskId; deskToken = it.deskToken ?: ""
                    }
                    reload()
                }
            }
        }

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("counter.mine", lang), color = Qrme.Txt, fontSize = 14.sp,
                fontWeight = FontWeight.Bold)
            labeledField(L10n.t("counter.desk_id", lang), deskId, "") { deskId = it }
            labeledField(L10n.t("counter.desk_token", lang), deskToken, "") { deskToken = it }
            card?.let { Text(it.displayName + " · " + it.presence, color = Qrme.T2, fontSize = 12.sp) }
            Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                presences.forEach { p ->
                    TextButton(onClick = {
                        vm.call({ ApiClient.setDeskPresence(deskId, p, deskToken) }) { r ->
                            card = r.getOrNull()
                            r.exceptionOrNull()?.let { note = it.message }
                        }
                    }) { Text(presenceLabel(p, lang), color = Qrme.BrandA, fontSize = 11.sp) }
                }
            }
            labeledField(L10n.t("counter.camera.url", lang), camUrl, "") { camUrl = it }
            TextButton(onClick = { act { ApiClient.setDeskCamera(deskId, camUrl, deskToken) } }) {
                Text(L10n.t("counter.camera", lang), color = Qrme.BrandA, fontSize = 11.sp)
            }
            TextButton(onClick = { act { ApiClient.setDeskPortrait(deskId, deskToken) } }) {
                Text(L10n.t("counter.portrait", lang), color = Qrme.BrandA, fontSize = 11.sp)
            }
            if (deskId.isNotBlank()) {
                Text(ApiClient.deskViewUrl(deskId), color = Qrme.T3, fontSize = 10.sp)
            }
        }

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Text(L10n.t("counter.bell", lang), color = Qrme.Txt, fontSize = 14.sp,
                fontWeight = FontWeight.Bold)
            rings.forEach { r ->
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text(r.note ?: r.id, color = Qrme.T2, fontSize = 11.sp)
                    TextButton(onClick = { act { ApiClient.ackDeskRing(deskId, r.id, deskToken) } }) {
                        Text(L10n.t("counter.ack", lang), color = Qrme.BrandA, fontSize = 11.sp)
                    }
                }
            }
            Text(L10n.t("counter.guests", lang), color = Qrme.Txt, fontSize = 12.sp)
            guests.forEach { g ->
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text((g.displayName ?: g.guestId) + " · " + g.status, color = Qrme.T2, fontSize = 11.sp)
                    Row {
                        TextButton(onClick = { act { ApiClient.acceptDeskGuest(deskId, g.id, deskToken) } }) {
                            Text(L10n.t("counter.accept", lang), color = Qrme.BrandA, fontSize = 11.sp)
                        }
                        TextButton(onClick = { act { ApiClient.declineDeskGuest(deskId, g.id, deskToken) } }) {
                            Text(L10n.t("counter.decline", lang), color = Qrme.Red, fontSize = 11.sp)
                        }
                    }
                }
            }
            overlay?.let {
                Text(L10n.t("counter.waiting", lang) + " " + it.waiting, color = Qrme.T3, fontSize = 11.sp)
            }
            staffedBy?.let { Text(it, color = Qrme.T3, fontSize = 11.sp) }
        }

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Text(L10n.t("counter.sticker", lang), color = Qrme.Txt, fontSize = 14.sp,
                fontWeight = FontWeight.Bold)
            Text(L10n.t("counter.sticker.note", lang), color = Qrme.T2, fontSize = 11.sp)
            labeledField(L10n.t("counter.sticker.label", lang), beaconLabel, "") { beaconLabel = it }
            BrandButton(L10n.t("counter.sticker.make", lang), enabled = beaconLabel.isNotBlank()) {
                val label = beaconLabel; beaconLabel = ""
                act { ApiClient.addDeskBeacon(deskId, label, deskToken) }
            }
            beacons.forEach { b ->
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text((b.label ?: b.id), color = Qrme.T2, fontSize = 11.sp)
                    Text(ApiClient.deskBeaconQrUrl(b.id), color = Qrme.T3, fontSize = 9.sp)
                    TextButton(onClick = { act { ApiClient.removeDeskBeacon(b.id, deskToken) } }) {
                        Text(L10n.t("counter.sticker.drop", lang), color = Qrme.Red, fontSize = 11.sp)
                    }
                }
            }
        }

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Text(L10n.t("counter.walkup", lang), color = Qrme.Txt, fontSize = 14.sp,
                fontWeight = FontWeight.Bold)
            nearby.forEach { d ->
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text(d.displayName + " · " + d.presence, color = Qrme.T2, fontSize = 11.sp)
                    TextButton(onClick = { deskId = d.id }) {
                        Text(L10n.t("counter.pick", lang), color = Qrme.BrandA, fontSize = 11.sp)
                    }
                }
            }
            labeledField(L10n.t("counter.knock.note", lang), knockNote, "") { knockNote = it }
            Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                BrandButton(L10n.t("counter.knock", lang), enabled = deskId.isNotBlank()) {
                    val why = knockNote; knockNote = ""
                    act { ApiClient.askToJoinDesk(deskId, why, vm.interactorToken ?: "") }
                }
                TextButton(onClick = { act { ApiClient.leaveDesk(deskId, vm.interactorToken ?: "") } }) {
                    Text(L10n.t("counter.leave", lang), color = Qrme.Red, fontSize = 12.sp)
                }
            }
        }

        note?.let { Text(it, color = Qrme.T2, fontSize = 12.sp) }
    }
}

@Composable
private fun TradePanel(vm: StudioViewModel) {
    val lang = L10n.deviceLanguage()
    var cards by remember { mutableStateOf<List<MarketCard>>(emptyList()) }
    var localities by remember { mutableStateOf<List<String>>(emptyList()) }
    var query by remember { mutableStateOf("") }
    var hits by remember { mutableStateOf<List<MarketHit>>(emptyList()) }
    var need by remember { mutableStateOf("") }
    var suggestions by remember { mutableStateOf<List<String>>(emptyList()) }
    var listingId by remember { mutableStateOf("") }
    var amount by remember { mutableStateOf("") }
    var venue by remember { mutableStateOf("") }
    var offer by remember { mutableStateOf<MarketOffer?>(null) }
    var sales by remember { mutableStateOf<List<MarketSale>>(emptyList()) }
    var includeRemote by remember { mutableStateOf(true) }
    var prefLocality by remember { mutableStateOf("") }
    var blurb by remember { mutableStateOf("") }
    var locality by remember { mutableStateOf("") }
    var tags by remember { mutableStateOf("") }
    var note by remember { mutableStateOf<String?>(null) }

    fun reload() {
        vm.call({ ApiClient.marketplace() }) { r -> cards = r.getOrDefault(emptyList()) }
        vm.call({ ApiClient.marketLocalities() }) { r -> localities = r.getOrDefault(emptyList()) }
        vm.call({ ApiClient.marketSales(vm.token!!) }) { r -> sales = r.getOrDefault(emptyList()) }
        vm.interactorId?.let { who ->
            vm.call({ ApiClient.marketSettings(who, vm.token!!) }) { r ->
                r.getOrNull()?.let {
                    prefLocality = it.locality; includeRemote = it.includeRemote
                }
            }
        }
    }
    LaunchedEffect(Unit) { reload() }

    fun act(op: suspend () -> Unit) {
        note = null
        vm.call({ op() }) { r ->
            r.exceptionOrNull()?.let { note = it.message }
            reload()
        }
    }

    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("trade.find", lang), color = Qrme.Txt, fontSize = 16.sp,
                fontWeight = FontWeight.Bold)
            labeledField(L10n.t("trade.query", lang), query, "") { query = it }
            BrandButton(L10n.t("trade.search", lang), enabled = query.isNotBlank()) {
                vm.call({ ApiClient.marketSearch(query) }) { r ->
                    hits = r.getOrDefault(emptyList())
                    r.exceptionOrNull()?.let { note = it.message }
                }
            }
            hits.forEach { Text(it.title, color = Qrme.T2, fontSize = 11.sp) }
            labeledField(L10n.t("trade.need", lang), need, "") { need = it }
            BrandButton(L10n.t("trade.assist", lang), enabled = need.isNotBlank()) {
                vm.call({ ApiClient.marketAssist(need) }) { r ->
                    suggestions = r.getOrDefault(emptyList())
                }
            }
            if (suggestions.isNotEmpty()) {
                Text(suggestions.joinToString(" · "), color = Qrme.T3, fontSize = 11.sp)
            }
            if (localities.isNotEmpty()) {
                Text(localities.joinToString(" · "), color = Qrme.T3, fontSize = 11.sp)
            }
            cards.forEach { Text(it.displayName, color = Qrme.T2, fontSize = 11.sp) }
            TextButton(onClick = { act { ApiClient.seedMarketplace() } }) {
                Text(L10n.t("trade.seed", lang), color = Qrme.BrandA, fontSize = 11.sp)
            }
        }

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Text(L10n.t("trade.stand", lang), color = Qrme.Txt, fontSize = 14.sp,
                fontWeight = FontWeight.Bold)
            labeledField(L10n.t("trade.blurb", lang), blurb, "") { blurb = it }
            labeledField(L10n.t("trade.locality", lang), locality, "") { locality = it }
            labeledField(L10n.t("trade.tags", lang), tags, "") { tags = it }
            Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                BrandButton(L10n.t("trade.list", lang)) {
                    act { ApiClient.listInMarketplace(vm.pid!!, blurb,
                        tags.split(",").map { it.trim() }.filter { it.isNotEmpty() },
                        vm.token!!) }
                }
                TextButton(onClick = { act { ApiClient.unlistFromMarketplace(vm.pid!!, vm.token!!) } }) {
                    Text(L10n.t("trade.unlist", lang), color = Qrme.Red, fontSize = 12.sp)
                }
            }
        }

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Text(L10n.t("trade.price", lang), color = Qrme.Txt, fontSize = 14.sp,
                fontWeight = FontWeight.Bold)
            labeledField(L10n.t("trade.listing", lang), listingId, "") { listingId = it }
            labeledField(L10n.t("trade.amount", lang), amount, "") { amount = it }
            offer?.amount?.let {
                Text(L10n.t("trade.asking", lang) + " " + it, color = Qrme.T2, fontSize = 11.sp)
            }
            Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                TextButton(onClick = {
                    act { ApiClient.setListingOffer(listingId,
                        amount.toDoubleOrNull() ?: 0.0, null, vm.token!!) }
                }) { Text(L10n.t("trade.set", lang), color = Qrme.BrandA, fontSize = 11.sp) }
                TextButton(onClick = {
                    vm.call({ ApiClient.listingOffer(listingId) }) { r -> offer = r.getOrNull() }
                }) { Text(L10n.t("trade.show", lang), color = Qrme.BrandA, fontSize = 11.sp) }
                TextButton(onClick = { act { ApiClient.clearListingOffer(listingId, vm.token!!) } }) {
                    Text(L10n.t("trade.clear", lang), color = Qrme.Red, fontSize = 11.sp)
                }
            }
            labeledField(L10n.t("trade.venue", lang), venue, "") { venue = it }
            Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                TextButton(onClick = { act { ApiClient.placeListing(listingId, venue, vm.token!!) } }) {
                    Text(L10n.t("trade.place", lang), color = Qrme.BrandA, fontSize = 11.sp)
                }
                TextButton(onClick = { act { ApiClient.unplaceListing(listingId, vm.token!!) } }) {
                    Text(L10n.t("trade.unplace", lang), color = Qrme.BrandA, fontSize = 11.sp)
                }
                TextButton(onClick = { act { ApiClient.removeMarketListing(listingId, vm.token!!) } }) {
                    Text(L10n.t("trade.pull", lang), color = Qrme.Red, fontSize = 11.sp)
                }
            }
            BrandButton(L10n.t("trade.buy", lang), enabled = listingId.isNotBlank()) {
                act { ApiClient.purchaseListing(listingId, vm.interactorToken ?: "") }
            }
        }

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Text(L10n.t("trade.sales", lang), color = Qrme.Txt, fontSize = 14.sp,
                fontWeight = FontWeight.Bold)
            sales.forEach { Text(it.id + " · " + it.status, color = Qrme.T2, fontSize = 11.sp) }
            Row(verticalAlignment = Alignment.CenterVertically) {
                Switch(checked = includeRemote, onCheckedChange = { want ->
                    includeRemote = want
                    act { ApiClient.setMarketSettings(vm.interactorId ?: "",
                        prefLocality, want, vm.token!!) }
                })
                Text(L10n.t("trade.include_remote", lang), color = Qrme.T2, fontSize = 12.sp)
            }
        }

        note?.let { Text(it, color = Qrme.T2, fontSize = 12.sp) }
    }
}

@Composable
private fun DealsPanel(vm: StudioViewModel) {
    val lang = L10n.deviceLanguage()
    var vocabulary by remember { mutableStateOf<ExchangeVocabulary?>(null) }
    var guestId by remember { mutableStateOf("") }
    var work by remember { mutableStateOf("") }
    var industry by remember { mutableStateOf("software") }
    var fee by remember { mutableStateOf("") }
    var exchangeId by remember { mutableStateOf("") }
    var deal by remember { mutableStateOf<ExchangeDeal?>(null) }
    var mine by remember { mutableStateOf<List<ExchangeDeal>>(emptyList()) }
    var itemName by remember { mutableStateOf("") }
    var channel by remember { mutableStateOf<String?>(null) }
    var note by remember { mutableStateOf<String?>(null) }

    fun reload() {
        vm.call({ ApiClient.exchangeVocabulary() }) { r -> vocabulary = r.getOrNull() }
        vm.call({ ApiClient.myExchanges(vm.pid!!, vm.token!!) }) { r ->
            mine = r.getOrDefault(emptyList()) }
        if (exchangeId.isBlank()) return
        vm.call({ ApiClient.exchange(exchangeId, vm.token!!) }) { r -> deal = r.getOrNull() }
    }
    LaunchedEffect(Unit) { reload() }

    fun act(op: suspend () -> Unit) {
        note = null
        vm.call({ op() }) { r ->
            r.exceptionOrNull()?.let { note = it.message }
            reload()
        }
    }

    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("deals.propose", lang), color = Qrme.Txt, fontSize = 16.sp,
                fontWeight = FontWeight.Bold)
            vocabulary?.let { v ->
                Text(v.rules.joinToString(" · "), color = Qrme.T2, fontSize = 11.sp)
                Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                    v.industries.take(6).forEach { ind ->
                        TextButton(onClick = { industry = ind }) {
                            Text(ind, color = Qrme.BrandA, fontSize = 10.sp)
                        }
                    }
                }
            }
            labeledField(L10n.t("deals.guest", lang), guestId, "") { guestId = it }
            labeledField(L10n.t("deals.work", lang), work, "") { work = it }
            labeledField(L10n.t("deals.fee", lang), fee, "") { fee = it }
            BrandButton(L10n.t("deals.propose.go", lang),
                        enabled = guestId.isNotBlank() && work.isNotBlank()) {
                vm.call({ ApiClient.proposeExchange(vm.pid!!, guestId, work, industry,
                    fee.toDoubleOrNull() ?: 0.0, vm.token!!) }) { r ->
                    r.exceptionOrNull()?.let { note = it.message }
                    r.getOrNull()?.let { deal = it; exchangeId = it.id }
                    reload()
                }
            }
        }

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Text(L10n.t("deals.manifest", lang), color = Qrme.Txt, fontSize = 14.sp,
                fontWeight = FontWeight.Bold)
            labeledField(L10n.t("deals.id", lang), exchangeId, "") { exchangeId = it }
            mine.forEach { d ->
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text((d.work ?: d.id) + " · " + d.state, color = Qrme.T2, fontSize = 11.sp)
                    TextButton(onClick = { exchangeId = d.id }) {
                        Text(L10n.t("deals.pick", lang), color = Qrme.BrandA, fontSize = 11.sp)
                    }
                }
            }
            deal?.let { d ->
                Text((d.work ?: "") + " · " + d.state, color = Qrme.Txt, fontSize = 12.sp)
                d.items.forEach { item ->
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                        Text(item.name + " · " + item.kind, color = Qrme.T2, fontSize = 11.sp)
                        Row {
                            TextButton(onClick = {
                                act { ApiClient.acceptExchangeItem(exchangeId, item.id, vm.token!!) }
                            }) { Text(L10n.t("deals.take", lang), color = Qrme.BrandA, fontSize = 11.sp) }
                            TextButton(onClick = {
                                act { ApiClient.removeExchangeItem(exchangeId, item.id, vm.token!!) }
                            }) { Text(L10n.t("deals.drop", lang), color = Qrme.Red, fontSize = 11.sp) }
                        }
                    }
                }
            }
            labeledField(L10n.t("deals.item", lang), itemName, "") { itemName = it }
            BrandButton(L10n.t("deals.add", lang),
                        enabled = exchangeId.isNotBlank() && itemName.isNotBlank()) {
                val name = itemName; itemName = ""
                act { ApiClient.addExchangeItem(exchangeId, "host_to_guest", name,
                    "source", vm.token!!) }
            }
        }

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Text(L10n.t("deals.sign", lang), color = Qrme.Txt, fontSize = 14.sp,
                fontWeight = FontWeight.Bold)
            Text(L10n.t("deals.sign.note", lang), color = Qrme.T2, fontSize = 11.sp)
            Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                TextButton(onClick = {
                    vm.call({ ApiClient.signExchange(exchangeId, vm.pid!!, vm.token!!) }) { r ->
                        deal = r.getOrNull()
                        r.exceptionOrNull()?.let { note = it.message }
                    }
                }) { Text(L10n.t("deals.sign.go", lang), color = Qrme.BrandA, fontSize = 11.sp) }
                TextButton(onClick = {
                    vm.call({ ApiClient.reopenExchange(exchangeId, vm.pid!!, vm.token!!) }) { r ->
                        deal = r.getOrNull()
                    }
                }) { Text(L10n.t("deals.reopen", lang), color = Qrme.BrandA, fontSize = 11.sp) }
                TextButton(onClick = {
                    vm.call({ ApiClient.withdrawFromExchange(exchangeId, vm.pid!!, vm.token!!) }) { r ->
                        deal = r.getOrNull()
                    }
                }) { Text(L10n.t("deals.withdraw", lang), color = Qrme.Red, fontSize = 11.sp) }
            }
            TextButton(onClick = {
                vm.call({ ApiClient.exchangeChannel(exchangeId, vm.token!!) }) { r ->
                    channel = r.getOrNull()
                }
            }) { Text(L10n.t("deals.channel", lang), color = Qrme.BrandA, fontSize = 11.sp) }
            channel?.let { Text(it, color = Qrme.T3, fontSize = 11.sp) }
        }

        note?.let { Text(it, color = Qrme.T2, fontSize = 12.sp) }
    }
}

// ---- Shops: storefronts, not desks ----

// No bell, no sessions, no connection offers — that absence is the design.
// Browsing and buying use the interactor identity the shell already holds;
// the till uses the profile owner's token. Strings go through L10n so the
// English count behind this shell's tabs does not grow.
@Composable
private fun ShopPanel(vm: StudioViewModel) {
    val lang = L10n.deviceLanguage()
    var cards by remember { mutableStateOf<List<ShopCard>>(emptyList()) }
    var open by remember { mutableStateOf<ShopDetail?>(null) }
    var mine by remember { mutableStateOf<List<ShopOrder>>(emptyList()) }
    var myShop by remember { mutableStateOf<ShopDetail?>(null) }
    var book by remember { mutableStateOf<List<ShopOrder>>(emptyList()) }
    var shopName by remember { mutableStateOf("") }
    var offerTitle by remember { mutableStateOf("") }
    var offerPrice by remember { mutableStateOf("") }
    var note by remember { mutableStateOf<String?>(null) }

    fun reload() { vm.call({ ApiClient.listShops() }) { r -> cards = r.getOrDefault(emptyList()) } }
    LaunchedEffect(Unit) { reload() }

    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Text(L10n.t("shop.title", lang), color = Qrme.Txt, fontSize = 16.sp,
                fontWeight = FontWeight.Bold)
            Text(L10n.t("shop.sub", lang), color = Qrme.T2, fontSize = 12.sp)
            cards.forEach { s ->
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    val meta = s.name + " · " + s.seller + (s.tag?.let { " · " + it } ?: "")
                    Text(meta, color = Qrme.Txt, fontSize = 12.sp)
                    TextButton(onClick = {
                        vm.call({ ApiClient.shopCard(s.id) }) { r -> open = r.getOrNull() }
                    }) { Text(L10n.t("shop.browse", lang), color = Qrme.BrandA, fontSize = 12.sp) }
                }
            }
        }

        open?.let { shop ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text(shop.name, color = Qrme.Txt, fontSize = 14.sp, fontWeight = FontWeight.Bold)
                shop.offerings.forEach { o ->
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                        val line = o.title + " · " + o.kind + " · " +
                            "%.2f".format(o.price) + " " + o.currency
                        Text(line, color = Qrme.T2, fontSize = 12.sp)
                        TextButton(enabled = vm.interactorId != null, onClick = {
                            vm.call({ ApiClient.placeShopOrder(shop.id, o.id,
                                vm.interactorId!!, 1, vm.interactorToken!!) }) { r ->
                                r.exceptionOrNull()?.let { note = it.message }
                                vm.call({ ApiClient.myShopOrders(vm.interactorId!!,
                                    vm.interactorToken!!) }) { m -> mine = m.getOrDefault(emptyList()) }
                            }
                        }) { Text(L10n.t("shop.order", lang), color = Qrme.BrandA, fontSize = 12.sp) }
                    }
                }
                if (mine.isNotEmpty()) {
                    Text(L10n.t("shop.mine", lang), color = Qrme.T2, fontSize = 12.sp,
                        fontWeight = FontWeight.Bold)
                }
                mine.forEach { o ->
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                        val line = o.title + " · " + "%.2f".format(o.amount) + " " +
                            o.currency + " · " + o.status
                        Text(line, color = Qrme.T3, fontSize = 11.sp)
                        if (o.status == "placed") {
                            TextButton(onClick = {
                                vm.call({ ApiClient.advanceShopOrder(o.shopId, o.id,
                                    "buyer", "cancelled", vm.interactorToken!!) }) { _ ->
                                    vm.call({ ApiClient.myShopOrders(vm.interactorId!!,
                                        vm.interactorToken!!) }) { m -> mine = m.getOrDefault(emptyList()) }
                                }
                            }) { Text(L10n.t("shop.cancel", lang), color = Qrme.Red, fontSize = 11.sp) }
                        }
                    }
                }
            }
        }

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Text(L10n.t("shop.till", lang), color = Qrme.Txt, fontSize = 14.sp,
                fontWeight = FontWeight.Bold)
            Text(L10n.t("shop.till_note", lang), color = Qrme.T2, fontSize = 11.sp)
            labeledField(L10n.t("shop.name", lang), shopName, "") { shopName = it }
            BrandButton(L10n.t("shop.open", lang), enabled = shopName.isNotBlank()) {
                vm.call({ ApiClient.openShop(vm.pid!!, shopName, vm.token!!) }) { r ->
                    r.exceptionOrNull()?.let { note = it.message }
                    myShop = r.getOrNull()
                    myShop?.let { till ->
                        vm.call({ ApiClient.shopOrderBook(till.id, vm.token!!) }) { b ->
                            book = b.getOrDefault(emptyList())
                        }
                    }
                    reload()
                }
            }
            myShop?.let { till ->
                labeledField(L10n.t("shop.offer_title", lang), offerTitle, "") { offerTitle = it }
                labeledField(L10n.t("shop.price", lang), offerPrice, "") { offerPrice = it }
                BrandButton(L10n.t("shop.add", lang), enabled = offerTitle.isNotBlank()) {
                    vm.call({ ApiClient.addShopOffering(till.id, "goods", offerTitle,
                        offerPrice.toDoubleOrNull() ?: 0.0, vm.token!!) }) { r ->
                        r.exceptionOrNull()?.let { note = it.message }
                        offerTitle = ""; offerPrice = ""
                        vm.call({ ApiClient.shopCard(till.id) }) { d -> myShop = d.getOrNull() }
                    }
                }
                till.offerings.forEach { o ->
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                        val line = o.title + " · " + "%.2f".format(o.price) + " " + o.currency
                        Text(line, color = Qrme.T2, fontSize = 12.sp)
                        TextButton(onClick = {
                            vm.call({ ApiClient.retireShopOffering(till.id, o.id, vm.token!!) }) { _ ->
                                vm.call({ ApiClient.shopCard(till.id) }) { d -> myShop = d.getOrNull() }
                            }
                        }) { Text(L10n.t("shop.retire", lang), color = Qrme.Red, fontSize = 11.sp) }
                    }
                }
                if (book.isNotEmpty()) {
                    Text(L10n.t("shop.book", lang), color = Qrme.T2, fontSize = 12.sp,
                        fontWeight = FontWeight.Bold)
                }
                book.forEach { o ->
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                        val line = o.title + " ×" + o.quantity + " · " +
                            "%.2f".format(o.amount) + " " + o.currency + " · " + o.status
                        Text(line, color = Qrme.T3, fontSize = 11.sp)
                        val next = when (o.status) {
                            "placed" -> "accepted"
                            "accepted" -> "fulfilled"
                            else -> null
                        }
                        next?.let { move ->
                            TextButton(onClick = {
                                vm.call({ ApiClient.advanceShopOrder(o.shopId, o.id,
                                    "seller", move, vm.token!!) }) { _ ->
                                    vm.call({ ApiClient.shopOrderBook(till.id, vm.token!!) }) { b ->
                                        book = b.getOrDefault(emptyList())
                                    }
                                }
                            }) {
                                val label = if (move == "accepted")
                                    L10n.t("shop.accept", lang) else L10n.t("shop.fulfil", lang)
                                Text(label, color = Qrme.BrandA, fontSize = 11.sp)
                            }
                        }
                    }
                }
            }
        }
        note?.let { Text(it, color = Qrme.T2, fontSize = 12.sp) }
    }
}

// ---- A live desk: the person behind the counter, and the bell ----

/**
 * Look up a desk by id and hand off to [DeskScreen]. A visitor normally
 * arrives from a beacon rather than by typing an id; this is the way in until
 * desk beacons are placed.
 */
@Composable
private fun DeskPanel(vm: StudioViewModel) {
    var deskId by remember { mutableStateOf("") }
    var open by remember { mutableStateOf(false) }

    if (open && deskId.isNotBlank()) {
        DeskScreen(deskId = deskId.trim(), lang = vm.language,
                   callerId = vm.interactorId,
            viewerToken = vm.interactorToken)
        return
    }
    screenScroll {
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("ndsk.open", vm.language), color = Qrme.Txt, fontSize = 16.sp,
                fontWeight = FontWeight.Bold)
            Text(L10n.t("ndsk.note", vm.language), color = Qrme.T2, fontSize = 12.sp)
            labeledField(L10n.t("ndsk.id", vm.language), deskId, L10n.t("ndsk.id.ph", vm.language)) { deskId = it }
            SmallAction(L10n.t("corner.open", vm.language)) { if (deskId.isNotBlank()) open = true }
        }
    }
}

// ---- Who wrote this? The other direction of the watermark ----

/**
 * Paste any passage and it names the profile that produced it, from the text
 * alone.
 *
 * `/watermarks/verify` needs a credential id up front and fails on one edited
 * character. This asks "whose work is this" with no id and keeps answering after
 * the text has been rewritten — so the counts are shown rather than a bare yes,
 * and below the threshold it deliberately names nobody, because ordinary phrases
 * travel between unrelated texts and a coincidence must not read as an
 * accusation.
 */
@Composable
private fun WhoWroteThisCard(vm: StudioViewModel) {
    var text by remember { mutableStateOf("") }
    var result by remember { mutableStateOf<WatermarkRecovery?>(null) }
    var busy by remember { mutableStateOf(false) }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("ns.who", vm.language), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        Text(L10n.t("ns.who.sub", vm.language),
            color = Qrme.T2, fontSize = 12.sp)
        labeledField("", text, L10n.t("ns.who.ph", vm.language)) { text = it }
        SmallAction(L10n.t(if (busy) "ns.who.checking" else "ns.who.check", vm.language),
            enabled = !busy && text.isNotBlank()) {
            busy = true
            vm.call({ ApiClient.recoverWatermark(text) }) { r ->
                busy = false
                result = r.getOrNull()
            }
        }
        result?.let { r ->
            if (r.recovered && r.profileId != null) {
                Text(L10n.fill(if (r.verbatim) "ns.who.by" else "ns.who.by.altered",
                               vm.language, mapOf("id" to r.profileId)),
                    color = if (r.verbatim) Qrme.Green else Qrme.Amber,
                    fontSize = 14.sp, fontWeight = FontWeight.Bold)
                Text(L10n.fill("ns.who.matched", vm.language,
                        mapOf("matched" to r.matchedWindows.toString(),
                              "stored" to r.storedWindows.toString()))
                        + " · ${r.similarity}", color = Qrme.T2, fontSize = 12.sp)
                r.markLine?.let { Text(it, color = Qrme.T3, fontSize = 10.sp) }
                r.disclosure?.let { Text(it, color = Qrme.T3, fontSize = 10.sp) }
            } else {
                // Not "no" — the reason, so a coincidence is not read either way.
                Text(r.reason ?: L10n.t("ns.who.none", vm.language),
                    color = Qrme.T2, fontSize = 12.sp)
                if (r.bestSimilarity != null && r.threshold != null) {
                    Text(L10n.fill("ns.who.below", vm.language,
                            mapOf("best" to r.bestSimilarity.toString(),
                                  "threshold" to r.threshold.toString())),
                        color = Qrme.T3, fontSize = 10.sp)
                }
            }
            r.method?.let { Text(it, color = Qrme.T3, fontSize = 10.sp) }
        }
    }
}

/**
 * Raising an objection — the half of governance that belongs to the person who
 * is *not* the profile's owner.
 *
 * This shell already carried the owner's half: list the objections against
 * your own profile, and attest to them. It carried nothing for the person on
 * the other side, and `open_objection` is explicit about who they are — *the
 * objecting party need not own an account*.
 *
 * Somebody who finds a synthetic profile of themselves has, by construction,
 * no QRME account and therefore no console. A phone is the surface they have.
 * Placed beside "Who wrote this?" because it is the same person one step on:
 * they have identified the profile, and now they want it stopped.
 */
@Composable
private fun ObjectToAProfileCard(vm: StudioViewModel) {
    var profileId by remember { mutableStateOf("") }
    var contact by remember { mutableStateOf("") }
    var reason by remember { mutableStateOf("") }
    var result by remember { mutableStateOf<ObjectionOpened?>(null) }
    var error by remember { mutableStateOf<String?>(null) }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Text(L10n.t("ns.object", vm.language), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        Text(L10n.t("ns.object.sub", vm.language),
             color = Qrme.T2, fontSize = 12.sp)
        OutlinedTextField(value = profileId, onValueChange = { profileId = it },
            label = { Text(L10n.t("ns.object.pid", vm.language)) })
        OutlinedTextField(value = contact, onValueChange = { contact = it },
            label = { Text(L10n.t("ns.object.contact", vm.language)) })
        OutlinedTextField(value = reason, onValueChange = { reason = it },
            label = { Text(L10n.t("ns.object.reason", vm.language)) })
        Button(onClick = {
            vm.call({ ApiClient.openObjection(profileId.trim(), contact.trim(),
                reason) }) { result = it.getOrNull(); error = it.exceptionOrNull()?.message }
        }, enabled = profileId.isNotBlank() && reason.isNotBlank(),
            colors = ButtonDefaults.buttonColors(containerColor = Qrme.BrandA)) {
            Text(L10n.t("ns.object.go", vm.language))
        }
        result?.let { r ->
            // Restricted immediately, pending review. That is the part the
            // person raising it needs told: the remedy is now, not after
            // somebody gets round to it.
            Text(L10n.fill("ns.object.raised", vm.language,
                    mapOf("status" to r.profileStatus)),
                color = Qrme.Green, fontSize = 12.sp)
            if (r.note.isNotBlank()) {
                Text(r.note, color = Qrme.T2, fontSize = 11.sp)
            }
        }
        error?.let { Text(it, color = Qrme.Red, fontSize = 12.sp) }
    }
}

/**
 * The notice that has to be answered before anything leaves the device, and
 * the switch that turns it off afterwards.
 *
 * The sending half landed last round and answers AWAITING_NOTICE on every
 * launch, because there was no surface to answer it on. Safe to be wrong in
 * that direction, and still wrong: a mechanism nobody can reach is a
 * mechanism nobody chose.
 *
 * Two rules this card keeps:
 *
 *  * **Show the report, do not describe it.** A card that says "we collect
 *    anonymous diagnostics" asks somebody to take our word for it.
 *    `Problems.report` is the same function the sender posts, so what is on
 *    screen is the payload. A preview that could drift from the message would
 *    be worse than none, because it would look like a promise.
 *  * **No pre-ticked answer.** Neither button is the emphasised one. A dialog
 *    with a bright Yes and a grey No has made the choice already.
 */
@Composable
// `lang` is passed in rather than read from a singleton: this card is the
// one place in the app that asks for consent, and consent is asked in the
// reader's language or it is not asked.
fun ProblemReportingCard(lang: String) {
    var answered by remember { mutableStateOf(Problems.noticeAnswered()) }
    var sending by remember { mutableStateOf(Problems.sendingEnabled()) }
    var showing by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()
    val owed = remember(showing, answered, sending) {
        val arr = Problems.report().optJSONArray("problems")
        (0 until (arr?.length() ?: 0)).mapNotNull { arr?.optJSONObject(it) }
    }

    Card(colors = CardDefaults.cardColors(containerColor = Qrme.Card)) {
        Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(L10n.t("ns.pr", lang), style = MaterialTheme.typography.titleSmall)

            if (Problems.collectorUrl().isEmpty()) {
                // Not a failure and not a thing to hide: this build has no
                // address compiled in, so there is nothing to consent to.
                Text(L10n.t("ns.pr.nowhere", lang),
                     style = MaterialTheme.typography.bodySmall)
            } else if (!answered) {
                // Two wordings of one sentence — this said "the day" where
                // the iOS shell said "the day it happened". One row now.
                Text(L10n.t("ns.pr.explain", lang),
                     style = MaterialTheme.typography.bodySmall)
                Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    OutlinedButton(onClick = {
                        Problems.answerNotice(true); answered = true; sending = true
                        // The first moment a send is permitted. Doing it now
                        // rather than at the next launch means the person who
                        // just agreed watches the buffer drain, instead of
                        // being told something happened later.
                        scope.launch(Dispatchers.IO) { Problems.send() }
                    }) { Text(L10n.t("ns.pr.send", lang)) }
                    OutlinedButton(onClick = {
                        Problems.answerNotice(false); answered = true; sending = false
                    }) { Text(L10n.t("ns.pr.dont", lang)) }
                }
            } else {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(L10n.t("ns.pr.toggle", lang), Modifier.weight(1f),
                         style = MaterialTheme.typography.bodyMedium)
                    Switch(checked = sending, onCheckedChange = {
                        sending = it; Problems.setSending(it)
                    })
                }
            }

            TextButton(onClick = { showing = !showing }) {
                Text(L10n.t(if (showing) "ns.pr.hide" else "ns.pr.show", lang))
            }
            if (showing) {
                if (owed.isEmpty()) {
                    Text(L10n.t("ns.pr.owed", lang),
                         style = MaterialTheme.typography.bodySmall)
                } else {
                    owed.forEach { r ->
                        Text("${r.optString("op")} → ${r.optInt("status")}  " +
                             "×${r.optInt("count")}  ${r.optString("day")}",
                             style = MaterialTheme.typography.bodySmall)
                    }
                }
            }
        }
    }
}

/**
 * The three presence states and the two corner switches, in the reader's
 * language.
 *
 * A `when` rather than a key built by concatenating the prefix with the API
 * value: a key assembled at runtime is a key no guard can see being asked for,
 * and the dead-key check would report all five rows as asked for by nobody.
 */
private fun presenceLabel(state: String, lang: String): String = when (state) {
    "attended" -> L10n.t("counter.presence.attended", lang)
    "away" -> L10n.t("counter.presence.away", lang)
    else -> L10n.t("counter.presence.closed", lang)
}

private fun cornerSwitchLabel(feature: String, lang: String): String =
    if (feature == "homepage") L10n.t("corner.switch.homepage", lang)
    else L10n.t("corner.switch.messaging", lang)

/**
 * The other half of the multiplicity disclosure, on this phone.
 *
 * Deliberately a card somebody opens rather than a banner that appears: a card
 * that showed itself when the ratio crossed a line would be the notification
 * the backend refuses to send, moved into the shell. The two buttons are the
 * same size and neither is highlighted, because a default is a thumb on the
 * scale of a consent.
 */
@Composable
private fun YourSideCard(vm: StudioViewModel) {
    var shape by remember { mutableStateOf<Solitude?>(null) }
    var referral by remember { mutableStateOf<SolitudeReferral?>(null) }
    var busy by remember { mutableStateOf(false) }

    Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(L10n.t("ns.side", vm.language), color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        Text(L10n.t("ns.side.sub", vm.language), color = Qrme.T2, fontSize = 12.sp)
        val who = vm.interactorId
        if (who.isNullOrBlank()) {
            // Said rather than left to a 404. Without an interactor there is
            // no "your own logs" to read, and a button that always failed
            // would be the shell blaming the network for a missing account.
            Text(L10n.t("ns.side.signin", vm.language), color = Qrme.T3,
                fontSize = 12.sp)
        } else {
            SmallAction(L10n.t("ns.side.read", vm.language), enabled = !busy) {
                busy = true
                vm.call({ ApiClient.solitude(who) }) { r ->
                    busy = false
                    shape = r.getOrNull()
                }
            }
        }
        shape?.let { s ->
            Row {
                Text(L10n.t("ns.side.toprofiles", vm.language), color = Qrme.T2,
                    fontSize = 13.sp, modifier = Modifier.weight(1f))
                Text("" + s.toProfiles, color = Qrme.Txt, fontSize = 13.sp,
                    fontWeight = FontWeight.Bold)
            }
            Row {
                Text(L10n.t("ns.side.topeople", vm.language), color = Qrme.T2,
                    fontSize = 13.sp, modifier = Modifier.weight(1f))
                Text("" + s.toPeople, color = Qrme.Txt, fontSize = 13.sp,
                    fontWeight = FontWeight.Bold)
            }
            // The server's own sentence, shown rather than paraphrased.
            // Rewording it here is how a count becomes a verdict.
            Text(s.note, color = Qrme.T3, fontSize = 11.sp)
            when (s.offerState) {
                "available" -> {
                    s.why?.let { Text(it, color = Qrme.T2, fontSize = 12.sp) }
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        SmallAction(L10n.t("ns.side.take", vm.language)) {
                            vm.call({ ApiClient.solitudeHandoff(who ?: "", true) }) { _ ->
                                vm.call({ ApiClient.solitude(who ?: "") }) { r ->
                                    shape = r.getOrNull() }
                            }
                        }
                        SmallAction(L10n.t("counter.decline", vm.language)) {
                            vm.call({ ApiClient.solitudeHandoff(who ?: "", false) }) { _ ->
                                vm.call({ ApiClient.solitude(who ?: "") }) { r ->
                                    shape = r.getOrNull() }
                            }
                        }
                    }
                }
                "declined" -> Text(L10n.t("ns.side.declined", vm.language),
                    color = Qrme.T3, fontSize = 12.sp)
                "accepted" -> {
                    val ref = referral
                    if (ref == null) {
                        SmallAction(L10n.t("ns.side.show", vm.language)) {
                            vm.call({ ApiClient.solitudeReferral(who ?: "") }) { r ->
                                referral = r.getOrNull() }
                        }
                    } else {
                        Text(ref.ref, color = Qrme.BrandA, fontSize = 13.sp,
                            fontWeight = FontWeight.Bold)
                        Text(L10n.t("ns.side.thatisall", vm.language),
                            color = Qrme.T3, fontSize = 11.sp)
                    }
                }
            }
        }
    }
}
