package app.qrme.studio.ui

import androidx.compose.foundation.background
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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import app.qrme.studio.ApiClient
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
            Text("Create your synthetic profile", color = Qrme.Txt, fontSize = 22.sp,
                fontWeight = FontWeight.Bold, modifier = Modifier.align(Alignment.CenterHorizontally))
            Text("A profile speaks in a voice you define — grounded in a persona, on your terms.",
                color = Qrme.T2, fontSize = 13.sp, modifier = Modifier.align(Alignment.CenterHorizontally))

            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                labeledField("Display name", name, "e.g. Ada") { name = it }
                labeledField("Persona", persona, "Voice, history, values.") { persona = it }
                Text("Kind", color = Qrme.T2, fontSize = 12.sp)
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    kinds.forEach { k ->
                        FilterChip(
                            selected = kind == k, onClick = { kind = k },
                            label = { Text(k.replace('_', ' '), fontSize = 12.sp) },
                            colors = FilterChipDefaults.filterChipColors(
                                selectedContainerColor = Qrme.BrandA,
                                selectedLabelColor = Color.White,
                                labelColor = Qrme.T2,
                            ),
                        )
                    }
                }
                labeledField("Birthdate", birthdate, "yyyy-MM-dd") { birthdate = it }
                if (languages.isNotEmpty()) {
                    Text("Language", color = Qrme.T2, fontSize = 12.sp)
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
            BrandButton("Create profile", enabled = name.isNotBlank() && persona.isNotBlank(), busy = busy) {
                error = null
                vm.createProfile(name, persona, kind, birthdate, language,
                    onError = { error = it }, onBusy = { busy = it })
            }
            Text("By creating a profile you agree to the Terms of Service — profiles are " +
                 "AI-generated synthetic content, never professional advice; you assume the " +
                 "risks of AI interactions. Full terms: GET /terms · docs/terms.md",
                color = Qrme.T3, fontSize = 9.sp)
            // The other reason somebody opens this app: they have found a
            // synthetic profile of themselves, or were sent something and
            // want to know whether a person wrote it. Both routes are public
            // on the backend and both sat behind the sign-in gate.
            Text("Here about a profile, not for one?", color = Qrme.T2, fontSize = 13.sp)
            TextButton(onClick = { publicDoor = true }) {
                Text("A profile depicts me · Is this genuine?",
                    color = Qrme.BrandA, fontSize = 13.sp)
            }
            Text("Neither needs an account.", color = Qrme.T3, fontSize = 11.sp)

            Text("Start the backend:  QRME_CORS_ORIGINS=* uvicorn qrme.api:app",
                color = Qrme.T3, fontSize = 10.sp)
        }
    }
}

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
                       L10n.t("pub.tab.mark", lang))
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
                                 "prf_…") { profileId = it }
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
            } else {
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
            Text("Profile live", color = Qrme.Green, fontSize = 12.sp, fontWeight = FontWeight.Bold)
        }
        Text(vm.displayName, color = Qrme.Txt, fontSize = 28.sp, fontWeight = FontWeight.Bold)
        Text("Your synthetic profile, as the world sees it.", color = Qrme.T2, fontSize = 14.sp)

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text("Public card", color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            when {
                !loaded -> CircularProgressIndicator(color = Qrme.BrandA, modifier = Modifier.size(22.dp))
                card == null -> Text("Couldn't load the card — is the backend running?",
                    color = Qrme.T2, fontSize = 13.sp)
                else -> {
                    cardRow("Kind", card!!.kind.replace('_', ' '))
                    cardRow("Status", card!!.status ?: "active")
                    cardRow("ID", card!!.id)
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
        Text("Compose", color = Qrme.Txt, fontSize = 22.sp, fontWeight = FontWeight.Bold)
        Text("Give a topic — your profile writes a post in its own voice.", color = Qrme.T2, fontSize = 13.sp)
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            labeledField("Topic", topic, "What should it post about?") { topic = it }
        }
        BrandButton("Compose post", enabled = topic.isNotBlank(), busy = busy) {
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
                p.provenance?.let { ProvenanceFooter(it) }
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
        Text("Posts", color = Qrme.Txt, fontSize = 22.sp, fontWeight = FontWeight.Bold)
        Text("Everything your profile has posted.", color = Qrme.T2, fontSize = 13.sp)
        when {
            posts == null -> CircularProgressIndicator(color = Qrme.BrandA, modifier = Modifier.size(22.dp))
            posts!!.isEmpty() -> Column(Modifier.card()) {
                Text("No posts yet — write one in Compose.", color = Qrme.T2, fontSize = 13.sp)
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
        Text("Robots", color = Qrme.Txt, fontSize = 22.sp, fontWeight = FontWeight.Bold)
        Text("Same persona · a physical body. Commands follow a per-body allowlist.",
            color = Qrme.T2, fontSize = 13.sp)

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("Bind a robot", color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
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
            BrandButton("Bind", enabled = catalog.isNotEmpty(), busy = busy) {
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
                labeledField("Topic for \"say\"", topic, "What should it speak about?") { topic = it }
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
                            Text("Say", color = Qrme.BrandA, fontSize = 13.sp) }
                    if ("clean" in rob.commands)
                        TextButton(onClick = { command(rob, "clean", null) }) {
                            Text("Clean", color = Qrme.BrandA, fontSize = 13.sp) }
                    if ("patrol" in rob.commands)
                        TextButton(onClick = { command(rob, "patrol", null) }) {
                            Text("Patrol", color = Qrme.BrandA, fontSize = 13.sp) }
                    TextButton(onClick = { command(rob, "dock", null) }) {
                        Text("Dock", color = Qrme.T2, fontSize = 13.sp) }
                }
            }
        }

        lastResult?.let { res ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text("Result", color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
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
        ProblemReportingCard()
            fontWeight = FontWeight.Bold)

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("Model", color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            Text("Which LLM powers this profile. Unconfigured providers fall back to the offline stub.",
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
                    Text(if (p.configured) "ready" else "no key",
                        color = if (p.configured) Qrme.Green else Qrme.T3, fontSize = 12.sp)
                }
            }
            if (effective.isNotEmpty())
                Text("Effective now: $effective", color = Qrme.T2, fontSize = 12.sp)
        }

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("Language", color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            Text("The profile speaks this language everywhere it appears — chat, posts, rooms, robot speech.",
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
                    Text("Speak it natively (pre-translate)", color = Qrme.Txt, fontSize = 13.sp)
                    Text("Off keeps the original voice — translate selectively below.",
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
            Text("Translate anything", color = Qrme.Txt, fontSize = 13.sp,
                fontWeight = FontWeight.Bold)
            labeledField("", translateInput, "Paste or type text…") { translateInput = it }
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
                Text("engine: ${t.engine}" + (t.note?.let { " — $it" } ?: ""),
                    color = Qrme.T3, fontSize = 10.sp)
            }
        }

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("Watermark", color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            Text("Every piece of work your profile composes or generates carries this mark — on all textual and visual renders, at all times. Design it your way; the AI designation always stays.",
                color = Qrme.T2, fontSize = 12.sp)
            if (wmLine.isNotEmpty())
                Text(wmLine, color = Qrme.T2, fontSize = 12.sp, fontWeight = FontWeight.Bold,
                    modifier = Modifier.clip(RoundedCornerShape(12.dp))
                        .background(Qrme.ScrBot).padding(horizontal = 10.dp, vertical = 6.dp))
            labeledField("Mark", wmMark, "✦") { wmMark = it }
            labeledField("Label", wmLabel, "AI · ${vm.displayName}") { wmLabel = it }
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp),
                verticalAlignment = Alignment.CenterVertically) {
                SmallAction("Save design") {
                    vm.call({ ApiClient.setWatermarkDesign(vm.pid!!, vm.token!!, wmMark, wmLabel) }) { r ->
                        r.onSuccess { wmLine = it.line; wmCustom = it.custom; wmSaved = true }
                         .onFailure { error = it.message }
                    }
                }
                if (wmCustom) SmallAction("Reset to default") {
                    vm.call({ ApiClient.setWatermarkDesign(vm.pid!!, vm.token!!, null, null) }) { r ->
                        r.onSuccess {
                            wmLine = it.line; wmCustom = it.custom
                            wmMark = ""; wmLabel = ""; wmSaved = false
                        }
                    }
                }
                if (wmSaved) Text("✓ saved", color = Qrme.Green, fontSize = 12.sp)
            }
        }

        WhoWroteThisCard(vm)
        ObjectToAProfileCard(vm)

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("Objections", color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            if (objections.isEmpty()) {
                Text("No objections — nobody has contested this profile.",
                    color = Qrme.T2, fontSize = 13.sp)
            } else objections.forEach { o ->
                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    Text(o.status.uppercase(), fontSize = 12.sp, fontWeight = FontWeight.Bold,
                        color = if (o.status == "open") Qrme.Amber else Qrme.T2)
                    o.reason?.let { Text(it, color = Qrme.Txt, fontSize = 13.sp) }
                    if (o.status == "open" && o.reattested == 0) {
                        TextButton(onClick = {
                            vm.call({ ApiClient.attest(vm.pid!!, o.id, vm.token!!) }) { reload() }
                        }) { Text("Re-attest my rights basis", color = Qrme.BrandA, fontSize = 13.sp) }
                    } else if (o.reattested == 1) {
                        Text("Basis re-attested · awaiting review", color = Qrme.Green, fontSize = 12.sp)
                    }
                }
            }
        }

        SteeringPanel(vm)

        RelationshipPanel(vm)

        FeedbackPanel(vm)

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
    val groupLabels = mapOf("system" to "System", "behavior" to "Behavior",
        "intimacy" to "Intimacy (18+)")

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
        Text("Steering", color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
        Text("Shape how the profile comes across — tone, pace, manner, look, age. " +
             "Steering, not piloting: it acts on its own within this shape.",
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
                label = { Text("Appearance — how they look and present") },
                modifier = Modifier.fillMaxWidth())
            Row(verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                OutlinedTextField(value = baseAge, onValueChange = { baseAge = it },
                    label = { Text("Base age") }, modifier = Modifier.width(110.dp))
                Text("Ages over time", color = Qrme.Txt, fontSize = 13.sp)
                Switch(checked = agingEnabled, onCheckedChange = { agingEnabled = it },
                    colors = SwitchDefaults.colors(checkedTrackColor = Qrme.Green))
            }
            h.effectiveAge?.let {
                Text("Effective age now: $it", color = Qrme.T3, fontSize = 11.sp)
            }
            SmallAction("Apply steering") {
                status = null
                vm.call({
                    ApiClient.setSteeringHub(vm.pid!!, vm.token!!,
                        values.mapValues { it.value.toInt() },
                        baseAge.toIntOrNull(), agingEnabled,
                        appearance.ifBlank { null })
                }) { r ->
                    r.onSuccess { hub = it
                        status = "Steering applied — it rides on every reply." }
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
        Text("Your relationship", color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        Text("How the profile relates to you in chat — its framing, your nickname, the tone it takes.",
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
            label = { Text("Nickname it calls you (optional)") },
            modifier = Modifier.fillMaxWidth())
        OutlinedTextField(value = tone, onValueChange = { tone = it },
            label = { Text("Tone (e.g. gentle, playful) — optional") },
            modifier = Modifier.fillMaxWidth())
        SmallAction("Save relationship") {
            status = null
            vm.call({
                val interactor = vm.interactorId
                    ?: ApiClient.createInteractor("You")
                        .also { vm.rememberInteractor(it.id, it.token) }.id
                ApiClient.setRelationship(vm.pid!!, vm.token!!, interactor,
                    type, nickname, tone)
            }) { r ->
                r.onSuccess { status = "Saved — it now treats you as ${it.replace('_', ' ')}." }
                 .onFailure { status = it.message }
            }
        }
        status?.let { Text(it, color = Qrme.Green, fontSize = 12.sp) }
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
        Text("Help us improve", color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        Text("Tell us how to make this better — an idea, a rough edge, a bug, " +
             "or what you love. It goes straight to the team.",
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
            label = { Text("What's on your mind?") }, minLines = 2,
            modifier = Modifier.fillMaxWidth())
        Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
            (1..5).forEach { n ->
                Text(if (n <= rating) "★" else "☆",
                    color = if (n <= rating) Qrme.Amber else Qrme.T3, fontSize = 18.sp,
                    modifier = Modifier.clickable { rating = if (rating == n) 0 else n })
            }
        }
        SmallAction("Send feedback") {
            if (message.isNotBlank())
                vm.call({ ApiClient.submitFeedback(vm.token, category,
                    message.trim(), rating.takeIf { it > 0 }) }) {
                    status = "Thank you — sent."; message = ""; rating = 0
                    reload()
                }
        }
        status?.let { Text(it, color = Qrme.Green, fontSize = 12.sp) }
        state?.takeIf { it.total > 0 }?.let { s ->
            Text("So far: " + categories.filter { (s.tally[it] ?: 0) > 0 }
                .joinToString(" · ") { "${s.tally[it]} $it" },
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
                            Bubble(false, "ⓘ ${prov.generatedBy} · persona + " +
                                "${prov.sourceItems} source item(s) · moderated: " +
                                prov.moderationStatus +
                                (prov.licensedFrom?.let { " · licensed from $it" } ?: ""),
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
            Text("Chat", color = Qrme.Txt, fontSize = 22.sp, fontWeight = FontWeight.Bold)
            Text("Talk with ${vm.displayName} — replies are in character and moderated.",
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
                labeledField("", draft, "Say something…") { draft = it }
            }
            BrandButtonSmall(if (busy) "…" else "Send", enabled = draft.isNotBlank() && !busy) { send() }
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
            listOf("Compose", "Posts", "Study").forEachIndexed { i, t ->
                Tab(selected = seg == i, onClick = { seg = i },
                    text = { Text(t, fontSize = 13.sp) })
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
        Text("Knowledge Excursions", color = Qrme.Txt, fontSize = 22.sp, fontWeight = FontWeight.Bold)
        Text("Send your profile out to study. Private names are redacted from everything outbound; findings come home for you to fold in.",
            color = Qrme.T2, fontSize = 13.sp)

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            labeledField("Topic", topic, "e.g. container gardening") { topic = it }
            labeledField("Question", question, "What should it find out?") { question = it }
            BrandButton("Go study", enabled = topic.isNotBlank() && question.isNotBlank(), busy = busy) {
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
                    Text(if (e.leftHost) "left host" else "stayed local",
                        color = if (e.leftHost) Qrme.Amber else Qrme.Green,
                        fontSize = 11.sp, fontWeight = FontWeight.Bold)
                }
                if (e.redactions > 0)
                    Text("${e.redactions} private term(s) redacted from the outbound brief",
                        color = Qrme.T2, fontSize = 12.sp)
                Text(e.findings, color = Qrme.Txt, fontSize = 13.sp)
                if (e.learned)
                    Text("✓ folded into the profile's knowledge", color = Qrme.Green, fontSize = 12.sp)
                else
                    TextButton(onClick = {
                        vm.call({ ApiClient.learn(e.id, vm.token!!) }) { reload() }
                    }) { Text("Fold into knowledge", color = Qrme.BrandA, fontSize = 13.sp) }
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
            listOf("Social", "Apps", "Robots").forEachIndexed { i, t ->
                Tab(selected = seg == i, onClick = { seg = i },
                    text = { Text(t, fontSize = 13.sp) })
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
            Text("Social platforms", color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            Text("Collect pulls the account's content in to grow the profile; publish runs the profile on the platform (moderated).",
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
            labeledField("Handle (optional)", handle, "@you") { handle = it }
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                SmallAction("Connect to collect") { connect("collect") }
                SmallAction("Connect to publish") { connect("publish") }
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
                Text(if (c.direction == "collect") "${c.collected} item(s) collected"
                     else "${c.published} post(s) published",
                    color = Qrme.T2, fontSize = 12.sp)
                if (c.status == "revoked") {
                    Text("revoked", color = Qrme.Red, fontSize = 12.sp)
                } else {
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp),
                        verticalAlignment = Alignment.CenterVertically) {
                        if (c.direction == "collect") {
                            SmallAction("Collect sample") {
                                vm.call({ ApiClient.socialCollect(c.id, vm.token!!,
                                    "sample post from ${c.platform}") }) { r ->
                                    r.onSuccess { status = "collected one item from ${c.platform} — it now feeds training" }
                                        .onFailure { error = it.message }
                                    reload()
                                }
                            }
                        } else {
                            SmallAction("Publish update") {
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
                        }) { Text("Disconnect", color = Qrme.Red, fontSize = 12.sp) }
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
            Text("Connected apps", color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            Text("Apple, Google, Microsoft, and Canva apps the profile's agents can collect from, act through, and produce with.",
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
                    }) { Text("Connect", color = Qrme.BrandA, fontSize = 13.sp, fontWeight = FontWeight.Bold) }
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
                    Text("revoked", color = Qrme.Red, fontSize = 12.sp)
                } else {
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        SmallAction("Collect") {
                            vm.call({ ApiClient.appCollect(c.id, vm.token!!,
                                "sample context from ${c.app}") }) { r ->
                                r.onSuccess { status = "collected from ${c.label} — it now feeds training" }
                                    .onFailure { error = it.message }
                            }
                        }
                        c.capabilities.firstOrNull()?.let { cap ->
                            SmallAction("Invoke $cap") {
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
            listOf("Profile", "Stranger", "Rooms").forEachIndexed { i, t ->
                Tab(selected = seg == i, onClick = { seg = i },
                    text = { Text(t, fontSize = 13.sp) })
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
                Text("Meet a stranger", color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
                Text("Anonymous matchmaking — they see only your alias, and either side can end it.",
                    color = Qrme.T2, fontSize = 12.sp)
                Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                    listOf("friendly" to "Friendly", "rated" to "Rated 18+").forEach { (t, label) ->
                        val on = tier == t
                        Text(label, color = if (on) Color.White else Qrme.Txt, fontSize = 12.sp,
                            modifier = Modifier.clip(RoundedCornerShape(50))
                                .background(if (on) Qrme.BrandA else Qrme.ScrBot)
                                .clickable { tier = t }
                                .padding(horizontal = 12.dp, vertical = 7.dp))
                    }
                }
                if (tier == "rated" && !vm.interactorVerified) {
                    Text("The rated tier needs a verified 18+ identity. Enter your birthdate " +
                         "to verify — both sides of a rated match are verified adults.",
                        color = Qrme.Amber, fontSize = 11.sp)
                    labeledField("Birthdate", birthdate, "YYYY-MM-DD") { birthdate = it }
                }
                labeledField("Alias (optional)", alias, "Stranger") { alias = it }
                BrandButton(if (waiting) "Waiting for a match — check again" else "Find a match",
                    enabled = tier != "rated" || vm.interactorVerified || birthdate.isNotBlank()) { join() }
            }
        } else {
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text("Talking with ${matchedWith ?: "a stranger"}", color = Qrme.Txt,
                        fontSize = 16.sp, fontWeight = FontWeight.Bold)
                    TextButton(onClick = {
                        vm.interactorId?.let { me ->
                            vm.call({ ApiClient.endConnection(cid, me, vm.interactorToken.orEmpty()) }) {
                                connectionId = null; matchedWith = null
                                messages = emptyList(); waiting = false
                            }
                        }
                    }) { Text("End", color = Qrme.Red, fontSize = 12.sp) }
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
                            Text("blocked — only you can see this", color = Qrme.Red, fontSize = 10.sp)
                    }
                }
                labeledField("", draft, "Say something…") { draft = it }
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    SmallAction("Send") {
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
                        Text("Refresh", color = Qrme.BrandA, fontSize = 12.sp)
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
    var room by remember { mutableStateOf<RoomCreated?>(null) }
    var transcript by remember { mutableStateOf<List<RoomMsg>>(emptyList()) }
    var draft by remember { mutableStateOf("") }
    var busy by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }

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
                Text("Open a room", color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
                Text("A group chat with you and ${vm.displayName}. Every profile turn is moderated; a room with a minor always runs strict.",
                    color = Qrme.T2, fontSize = 12.sp)
                labeledField("Topic", topic, "What's the room about?") { topic = it }
                BrandButton("Open room", enabled = topic.isNotBlank(), busy = busy) {
                    busy = true; error = null
                    withInteractor(vm, { error = it; busy = false }) { me ->
                        vm.call({ ApiClient.createRoom(topic, vm.pid!!, me) }) { r ->
                            busy = false
                            r.onSuccess { room = it; topic = ""; transcript = emptyList() }
                                .onFailure { error = it.message }
                        }
                    }
                }
            }
        } else {
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text(current.topic, color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
                    TextButton(onClick = { room = null; transcript = emptyList() }) {
                        Text("Leave", color = Qrme.Red, fontSize = 12.sp)
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
                labeledField("", draft, "Say something…") { draft = it }
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    SmallAction("Send") {
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
                    SmallAction("Let them talk") {
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
            listOf("General", "Summon", "Market", "Packs", "Gaming", "License", "Earn", "Sign", "Voice", "Desk", "Shop", "Corner", "People", "Counter", "Trade", "Deals").forEachIndexed { i, t ->
                Tab(selected = seg == i, onClick = { seg = i },
                    text = { Text(t, fontSize = 12.sp) })
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
            Text("Earnings", color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            Text("Everything this creator earns — pack sales, license fees, and verified " +
                 "venue-placement views — written to the ledger at transaction time.",
                color = Qrme.T2, fontSize = 12.sp)
            statement?.let { s ->
                Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                    listOf(Triple("Accrued", s.accrued, Qrme.Green),
                           Triple("Paid", s.paid, Qrme.T2),
                           Triple("Lifetime", s.lifetime, Qrme.BrandA)).forEach { (l, v, c) ->
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
                BrandButton("Request payout", enabled = s.accrued > 0) {
                    error = null
                    vm.call({ ApiClient.requestPayout(vm.pid!!, vm.token!!) }) { r ->
                        r.onSuccess { receipt = it; reload() }
                         .onFailure { error = it.message }
                    }
                }
                receipt?.let {
                    Text("Payout ${it.payoutId}: ${money(it.total, s.currency)} across " +
                         "${it.entries} entries (simulated transfer).",
                        color = Qrme.Green, fontSize = 12.sp)
                }
            } ?: CircularProgressIndicator(color = Qrme.BrandA, modifier = Modifier.size(22.dp))
        }
        statement?.takeIf { it.entries.isNotEmpty() }?.let { s ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text("Ledger", color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
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
            Text("Play alongside", color = Qrme.Txt, fontSize = 16.sp,
                fontWeight = FontWeight.Bold)
            Text("Bring this profile into a game as a companion or teammate. " +
                 "It talks in character and moderated — and always plays " +
                 "within the game's rules; it never cheats.",
                color = Qrme.T2, fontSize = 12.sp)
            Text("Platform", color = Qrme.T3, fontSize = 11.sp)
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
            labeledField("Game title", game, "Halo Infinite") { game = it }
            SmallAction("Start session") {
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
                Text("${s.role.replace("_", " ")} · ${s.callouts} callouts",
                    color = Qrme.T2, fontSize = 11.sp)
                if (s.status == "active") {
                    if (openSession == s.id) {
                        labeledField("Situation", situation,
                            "enemy on the flag, low shields") { situation = it }
                        Row(Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically) {
                            Text("Minor in lobby (forces strict)",
                                color = Qrme.T2, fontSize = 11.sp)
                            Switch(checked = minorPresent,
                                onCheckedChange = { minorPresent = it })
                        }
                        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            SmallAction("Call it") {
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
                            }) { Text("End", color = Qrme.Red, fontSize = 12.sp) }
                        }
                        lastLine?.let { l ->
                            if (l.status == "spoken" && l.line != null)
                                Text("🎙 ${l.line}", color = Qrme.Green, fontSize = 12.sp)
                            else Text("⚠️ held — ${l.flagReason ?: "moderation"}",
                                color = Qrme.Amber, fontSize = 11.sp)
                        }
                    } else {
                        TextButton(onClick = { openSession = s.id; lastLine = null }) {
                            Text("Open", color = Qrme.BrandA, fontSize = 12.sp)
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
            onClose = { scanning = false })
        return
    }

    screenScroll {
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("@handle", color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            Text("A unique name anyone can summon the profile by.", color = Qrme.T2, fontSize = 12.sp)
            labeledField("Handle", handle, "rosa_the_gardener") { handle = it }
            SmallAction("Claim") {
                if (handle.isNotBlank()) {
                    error = null
                    vm.call({ ApiClient.claimHandle(vm.pid!!, handle,
                        vm.token.orEmpty()) }) { r ->
                        r.onSuccess { claimed = it; handle = "" }
                            .onFailure { error = it.message }
                    }
                }
            }
            claimed?.let { Text("claimed $it", color = Qrme.Green, fontSize = 12.sp) }
        }

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("Beacons", color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            Text("Leave the profile behind somewhere physical — a placed QR that summons it. Pick it back up any time.",
                color = Qrme.T2, fontSize = 12.sp)
            labeledField("Label", label, "Rosa's garden bench") { label = it }
            labeledField("Location (optional)", location, "the community garden") { location = it }
            SmallAction("Place beacon") {
                if (label.isNotBlank()) {
                    error = null
                    vm.call({ ApiClient.placeBeacon(vm.pid!!, label, location) }) { r ->
                        r.onSuccess { lastQr = it.qrSvg; label = ""; location = "" }
                            .onFailure { error = it.message }
                        reload()
                    }
                }
            }
            lastQr?.let { Text("QR: $it", color = Qrme.T3, fontSize = 10.sp) }
        }

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("Scan a beacon", color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            Text("Point the camera at a QRME sticker and the profile appears on it — no page, no tap. A stock camera app can only open the link; this one can draw on the code.",
                color = Qrme.T2, fontSize = 12.sp)
            SmallAction("Open scanner") { scanning = true }
        }

        beacons.forEach { b ->
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text(b.label, color = Qrme.Txt, fontSize = 14.sp, fontWeight = FontWeight.Bold)
                    if (b.active) {
                        TextButton(onClick = {
                            vm.call({ ApiClient.pickUpBeacon(b.id) }) { reload() }
                        }) { Text("Pick up", color = Qrme.Red, fontSize = 12.sp) }
                    } else Text("picked up", color = Qrme.T3, fontSize = 12.sp)
                }
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text(b.location ?: "", color = Qrme.T2, fontSize = 12.sp)
                    Text("${b.scans} scan(s)", color = Qrme.T3, fontSize = 12.sp)
                }
            }
        }

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("Try a summon", color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            labeledField("Reference", ref, "@handle · #tag · beacon id") { ref = it }
            SmallAction("Summon") {
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
                    Text("beacon \"${f.label ?: ""}\" · ${f.scans ?: 0} scan(s)",
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
            Text("List this profile", color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            Text("Share it on the marketplace — discoverable by #tag summons too.",
                color = Qrme.T2, fontSize = 12.sp)
            labeledField("Title", title, "Rosa — gardening wisdom") { title = it }
            labeledField("Blurb (optional)", blurb, "What makes it worth summoning?") { blurb = it }
            labeledField("Tags, comma separated", tags, "gardening, herbs") { tags = it }
            SmallAction("Create listing") {
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
            Text("Wellbeing & quick browse", color = Qrme.Txt, fontSize = 14.sp,
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
            Text("The wellbeing starters — Dr. Lena Whitcomb (anxiety), " +
                 "Dr. Marcus Adeyemi (mood), Dr. Priya Nair (relationships) — " +
                 "offer education and support, never a substitute for " +
                 "professional care. In crisis, call or text 988.",
                color = Qrme.T3, fontSize = 10.sp)
        }

        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            labeledField("Filter by tag", filterTag, "gardening") { filterTag = it }
            SmallAction("Browse") { reload() }
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
                        }) { Text("Remove", color = Qrme.Red, fontSize = 12.sp) }
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
                    "installed — the body can now be commanded with these tasks"
                else "installed — the pack now grounds this profile"
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
            Text("Knowledge packs", color = Qrme.Txt, fontSize = 16.sp,
                fontWeight = FontWeight.Bold)
            Text("Make this profile smarter: a pack's curated items join its " +
                 "source material, grounding what it knows — and every " +
                 "reply's provenance shows the pack honestly. 🤖 Robot task " +
                 "packs teach the body this profile embodies new commandable " +
                 "tasks, capability-checked at install.",
                color = Qrme.T2, fontSize = 12.sp)
            labeledField("Filter by industry", industry, "finance") { industry = it }
            SmallAction("Browse") { reload() }
        }
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("Pack sources", color = Qrme.Txt, fontSize = 14.sp,
                fontWeight = FontWeight.Bold)
            Text("Federated mod storefronts — sync a source and its catalog " +
                 "joins the marketplace, origin on every label.",
                color = Qrme.T3, fontSize = 10.sp)
            registries.forEach { reg ->
                Row(Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically) {
                    Column(Modifier.weight(1f)) {
                        Text(reg.name, color = Qrme.BrandA, fontSize = 12.sp,
                            fontWeight = FontWeight.Bold)
                        Text(reg.tagline, color = Qrme.T2, fontSize = 10.sp)
                        Text("${reg.synced}/${reg.available} packs synced",
                            color = Qrme.T3, fontSize = 10.sp)
                    }
                    if (reg.synced >= reg.available)
                        Text("Synced", color = Qrme.Green, fontSize = 12.sp,
                            fontWeight = FontWeight.Bold)
                    else SmallAction("Sync") {
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
                            Text("🤖 ROBOT", color = Qrme.BrandA, fontSize = 11.sp,
                                fontWeight = FontWeight.Bold)
                        Text(if (p.free) "FREE" else "%.2f %s".format(p.price, p.currency),
                            color = if (p.free) Qrme.Green else Qrme.Amber,
                            fontSize = 12.sp, fontWeight = FontWeight.Bold)
                    }
                }
                p.blurb?.let { Text(it, color = Qrme.T2, fontSize = 12.sp) }
                Text("#${p.industry} · ${p.items} items · ${p.installs} installs · ${p.publisher}",
                    color = Qrme.T3, fontSize = 11.sp)
                p.originUrl?.let {
                    Text("from $it", color = Qrme.BrandA, fontSize = 10.sp)
                }
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.End,
                    verticalAlignment = Alignment.CenterVertically) {
                    if (p.id in installed) {
                        Text("Installed", color = Qrme.Green, fontSize = 12.sp,
                            fontWeight = FontWeight.Bold)
                        TextButton(onClick = { uninstall(p) }) {
                            Text("Remove", color = Qrme.Red, fontSize = 12.sp)
                        }
                    } else {
                        SmallAction(if (p.free) "Download"
                                    else "Buy %.2f %s".format(p.price, p.currency)) {
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
            Text("License this expertise", color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            Text("consult = use as-is · finetune / clone = buyers may derive their own agent (provenance recorded). Buyers acquire with their own verified identity, outside this app.",
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
            labeledField("Price (USD)", price, "0") { price = it }
            labeledField("Terms (optional)", terms, "attribution required") { terms = it }
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalAlignment = Alignment.CenterVertically) {
                SmallAction("Set offer") {
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
                    }) { Text("Unlist", color = Qrme.Red, fontSize = 12.sp) }
                }
            }
            offer?.let {
                Text("offered: ${it.kind} · ${it.currency} ${it.price}" +
                    if (it.allowDerivatives) " · derivatives allowed" else "",
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
                    if (g.revoked) Text("revoked", color = Qrme.Red, fontSize = 12.sp)
                    else TextButton(onClick = {
                        vm.call({ ApiClient.revokeLicense(g.id, vm.token!!) }) { reload() }
                    }) { Text("Revoke", color = Qrme.Red, fontSize = 12.sp) }
                }
                g.derivedProfileId?.let {
                    Text("derived agent: $it", color = Qrme.T2, fontSize = 11.sp)
                }
            }
        }
    }
}

@Composable
private fun ProvenanceFooter(p: Provenance) {
    Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
        HorizontalDivider(color = Qrme.Line)
        Text("Generated by ${p.generatedBy} · grounded in persona + " +
            "${p.sourceItems} source item(s) · moderation: ${p.moderationStatus}",
            color = Qrme.T2, fontSize = 10.sp)
        p.licensedFrom?.let {
            Text("licensed from $it", color = Qrme.Amber, fontSize = 10.sp)
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
    var meaning by remember { mutableStateOf("I attest this is accurate and complete") }
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
            Text("Signing credentials", color = Qrme.Txt, fontSize = 16.sp,
                fontWeight = FontWeight.Bold)
            if (credentials.isEmpty()) {
                Text("None yet. A signature needs a passkey bound to this account.",
                    color = Qrme.T2, fontSize = 12.sp)
            }
            credentials.forEach { c ->
                Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                    Text(c.displayName ?: c.credentialId, color = Qrme.Txt,
                        fontSize = 13.sp, fontWeight = FontWeight.Bold)
                    Text("verified at enrolment: ${c.proofingLevel}",
                        color = Qrme.T2, fontSize = 11.sp)
                    // Surfaced rather than buried: a syncable passkey lives on
                    // every device in the user's cloud account, which is a
                    // weaker claim that only they could have signed.
                    Text(
                        if (c.deviceBound) "device-bound — cannot sync"
                        else "syncable — exists on your other devices",
                        color = if (c.deviceBound) Qrme.Green else Qrme.Red,
                        fontSize = 11.sp)
                    Text("can sign: ${c.canSign.joinToString(", ")}",
                        color = Qrme.T3, fontSize = 10.sp)
                }
            }
            SmallAction("Enrol a passkey") {
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
            Text("What you are signing", color = Qrme.Txt, fontSize = 16.sp,
                fontWeight = FontWeight.Bold)
            labeledField("Document", document, "the text being signed") { document = it }
            labeledField("Meaning", meaning, "what your signature attests") { meaning = it }
            Text("This exact text is hashed into the challenge and stored with "
                + "the signature. The system prompt cannot show it — no passkey "
                + "prompt can — so read it here. Standard and high need an "
                + "identity check beyond a passkey; until one is recorded "
                + "against your credential, only basic will sign.",
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
                Text(if (r.valid) "Verifies" else "Does not verify",
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

        Text("Passkeys are bound to a verified domain via Digital Asset Links, "
            + "so signing works only against a real deployment — not a LAN dev "
            + "server. See docs/signatures.md.",
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
                Text("Create a profile first", color = Qrme.Txt, fontSize = 16.sp,
                    fontWeight = FontWeight.Bold)
                Text("A voiceprint belongs to a profile and only its owner may "
                    + "enroll one, so there has to be one to own it.",
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
                    Text(L10n.t("corner.switch." + feature, lang), color = Qrme.T2,
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
        labeledField("kind", kind, "profiles | desks | posts | listings") { kind = it }
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
    var displayName by remember { mutableStateOf("") }
    var trade by remember { mutableStateOf("") }
    var attestor by remember { mutableStateOf("") }
    var basis by remember { mutableStateOf("") }
    var location by remember { mutableStateOf("") }
    var blurb by remember { mutableStateOf("") }
    var card by remember { mutableStateOf<DeskCard?>(null) }
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
                    }) { Text(L10n.t("counter.presence." + p, lang), color = Qrme.BrandA, fontSize = 11.sp) }
                }
            }
            TextButton(onClick = { act { ApiClient.setDeskCamera(deskId, true, deskToken) } }) {
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
    var acceptPrice by remember { mutableStateOf("") }
    var venue by remember { mutableStateOf("") }
    var offer by remember { mutableStateOf<MarketOffer?>(null) }
    var sales by remember { mutableStateOf<List<MarketSale>>(emptyList()) }
    var showOffers by remember { mutableStateOf(true) }
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
                showOffers = r.getOrDefault(true)
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
                    act { ApiClient.listInMarketplace(vm.pid!!, blurb, locality,
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
            labeledField(L10n.t("trade.accept", lang), acceptPrice, "") { acceptPrice = it }
            offer?.amount?.let {
                Text(L10n.t("trade.asking", lang) + " " + it, color = Qrme.T2, fontSize = 11.sp)
            }
            Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                TextButton(onClick = {
                    act { ApiClient.setListingOffer(listingId,
                        amount.toDoubleOrNull() ?: 0.0, acceptPrice.toDoubleOrNull(), vm.token!!) }
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
                Switch(checked = showOffers, onCheckedChange = { want ->
                    showOffers = want
                    act { ApiClient.setMarketSettings(vm.interactorId ?: "", want, vm.token!!) }
                })
                Text(L10n.t("trade.show_offers", lang), color = Qrme.T2, fontSize = 12.sp)
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
        DeskScreen(deskId = deskId.trim(), callerId = vm.interactorId,
            viewerToken = vm.interactorToken)
        return
    }
    screenScroll {
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("Open a desk", color = Qrme.Txt, fontSize = 16.sp,
                fontWeight = FontWeight.Bold)
            Text("A desk is a real person, not a synthetic profile — so nothing "
                + "there carries the AI mark. If they are away from the desk, "
                + "you can ring the bell.", color = Qrme.T2, fontSize = 12.sp)
            labeledField("Desk id", deskId, "dsk_…") { deskId = it }
            SmallAction("Open") { if (deskId.isNotBlank()) open = true }
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
        Text("Who wrote this?", color = Qrme.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        Text("Paste any passage. If a profile here produced it, this names it — " +
             "even if the wording has since been changed.",
            color = Qrme.T2, fontSize = 12.sp)
        labeledField("", text, "Paste a passage…") { text = it }
        SmallAction(if (busy) "Checking…" else "Check this text",
            enabled = !busy && text.isNotBlank()) {
            busy = true
            vm.call({ ApiClient.recoverWatermark(text) }) { r ->
                busy = false
                result = r.getOrNull()
            }
        }
        result?.let { r ->
            if (r.recovered && r.profileId != null) {
                Text(if (r.verbatim) "Written by ${r.profileId}, unaltered."
                     else "Written by ${r.profileId} — altered since.",
                    color = if (r.verbatim) Qrme.Green else Qrme.Amber,
                    fontSize = 14.sp, fontWeight = FontWeight.Bold)
                Text("${r.matchedWindows} of ${r.storedWindows} passages matched · " +
                     "similarity ${r.similarity}", color = Qrme.T2, fontSize = 12.sp)
                r.markLine?.let { Text(it, color = Qrme.T3, fontSize = 10.sp) }
                r.disclosure?.let { Text(it, color = Qrme.T3, fontSize = 10.sp) }
            } else {
                // Not "no" — the reason, so a coincidence is not read either way.
                Text(r.reason ?: "No profile here produced this text.",
                    color = Qrme.T2, fontSize = 12.sp)
                if (r.bestSimilarity != null && r.threshold != null) {
                    Text("closest overlap ${r.bestSimilarity}, below the " +
                         "${r.threshold} threshold for naming anyone",
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
        Text("Object to a profile", color = Q.Txt, fontSize = 16.sp,
            fontWeight = FontWeight.Bold)
        Text("If a synthetic profile here is of you and you did not agree to " +
             "it, say so. You do not need an account, and you do not need to " +
             "be signed in.", color = Q.T2, fontSize = 12.sp)
        OutlinedTextField(value = profileId, onValueChange = { profileId = it },
            label = { Text("Profile id") })
        OutlinedTextField(value = contact, onValueChange = { contact = it },
            label = { Text("How to reach you") })
        OutlinedTextField(value = reason, onValueChange = { reason = it },
            label = { Text("What is wrong") })
        Button(onClick = {
            vm.call({ ApiClient.openObjection(profileId.trim(), contact.trim(),
                reason) }) { result = it; error = null }
        }, enabled = profileId.isNotBlank() && reason.isNotBlank(),
            colors = ButtonDefaults.buttonColors(containerColor = Q.BrandA)) {
            Text("Raise an objection")
        }
        result?.let { r ->
            // Restricted immediately, pending review. That is the part the
            // person raising it needs told: the remedy is now, not after
            // somebody gets round to it.
            Text("Raised. The profile is ${r.profileStatus} pending review.",
                color = Q.Green, fontSize = 12.sp)
            if (r.note.isNotBlank()) {
                Text(r.note, color = Q.T2, fontSize = 11.sp)
            }
        }
        error?.let { Text(it, color = Q.Red, fontSize = 12.sp) }
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
fun ProblemReportingCard() {
    var answered by remember { mutableStateOf(Problems.noticeAnswered()) }
    var sending by remember { mutableStateOf(Problems.sendingEnabled()) }
    var showing by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()
    val owed = remember(showing, answered, sending) {
        val arr = Problems.report().optJSONArray("problems")
        (0 until (arr?.length() ?: 0)).mapNotNull { arr?.optJSONObject(it) }
    }

    Card(colors = CardDefaults.cardColors(containerColor = Qrme.Card2)) {
        Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("When something breaks", style = MaterialTheme.typography.titleSmall)

            if (Problems.collectorUrl().isEmpty()) {
                // Not a failure and not a thing to hide: this build has no
                // address compiled in, so there is nothing to consent to.
                Text("This build reports nowhere. Failures are counted on this " +
                     "device and never leave it.",
                     style = MaterialTheme.typography.bodySmall)
            } else if (!answered) {
                Text("This app can send a count of what failed — the operation " +
                     "and the HTTP status, the day, and how many times. Not " +
                     "what you typed, not who you are, not which profile. " +
                     "Nothing that identifies you or anyone else.",
                     style = MaterialTheme.typography.bodySmall)
                Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    OutlinedButton(onClick = {
                        Problems.answerNotice(true); answered = true; sending = true
                        // The first moment a send is permitted. Doing it now
                        // rather than at the next launch means the person who
                        // just agreed watches the buffer drain, instead of
                        // being told something happened later.
                        scope.launch(Dispatchers.IO) { Problems.send() }
                    }) { Text("Send counts") }
                    OutlinedButton(onClick = {
                        Problems.answerNotice(false); answered = true; sending = false
                    }) { Text("Do not send") }
                }
            } else {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text("Send failure counts", Modifier.weight(1f),
                         style = MaterialTheme.typography.bodyMedium)
                    Switch(checked = sending, onCheckedChange = {
                        sending = it; Problems.setSending(it)
                    })
                }
            }

            TextButton(onClick = { showing = !showing }) {
                Text(if (showing) "Hide what would be sent"
                     else "Show what would be sent")
            }
            if (showing) {
                if (owed.isEmpty()) {
                    Text("Nothing is owed. Either nothing has failed, or " +
                         "everything that has was already reported.",
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
