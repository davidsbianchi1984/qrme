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
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import app.qrme.studio.ApiClient
import app.qrme.studio.AppConn
import app.qrme.studio.Beacon
import app.qrme.studio.CatalogApp
import app.qrme.studio.ConnMsg
import app.qrme.studio.Excursion
import app.qrme.studio.GameCalloutResult
import app.qrme.studio.GameSession
import app.qrme.studio.InstalledPack
import app.qrme.studio.LanguageInfo
import app.qrme.studio.LicenseGrant
import app.qrme.studio.LicenseOffer
import app.qrme.studio.Listing
import app.qrme.studio.Objection
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

@Composable
private fun screenScroll(content: @Composable ColumnScope.() -> Unit) =
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
private fun labeledField(label: String, value: String, placeholder: String, onChange: (String) -> Unit) {
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
            Text("Start the backend:  QRME_CORS_ORIGINS=* uvicorn qrme.api:app",
                color = Qrme.T3, fontSize = 10.sp)
        }
    }
}

// ---- Overview ----

@Composable
fun OverviewScreen(vm: StudioViewModel) {
    var card by remember { mutableStateOf<ProfileCard?>(null) }
    var loaded by remember { mutableStateOf(false) }
    LaunchedEffect(Unit) {
        vm.call({ ApiClient.profile(vm.pid!!) }) { r -> card = r.getOrNull(); loaded = true }
    }
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
            Text("Sign out", color = Qrme.T2)
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
    var error by remember { mutableStateOf<String?>(null) }

    fun reload() {
        vm.call({ ApiClient.models() }) { r -> providers = r.getOrDefault(emptyList()) }
        vm.call({ ApiClient.languages() }) { r -> languages = r.getOrDefault(emptyList()) }
        vm.call({ ApiClient.profileLanguage(vm.pid!!) }) { r ->
            r.getOrNull()?.let { (lang, mode) ->
                language = lang; preTranslate = mode == "pre"
            }
        }
        vm.call({ ApiClient.profileModel(vm.pid!!) }) { r ->
            r.getOrNull()?.let { current = it.provider; effective = it.effective }
        }
        vm.call({ ApiClient.objections(vm.pid!!, vm.token!!) }) { r ->
            objections = r.getOrDefault(emptyList())
        }
    }
    LaunchedEffect(Unit) { reload() }

    screenScroll {
        Text("Settings", color = Qrme.Txt, fontSize = 22.sp, fontWeight = FontWeight.Bold)

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
            SmallAction("Translate") {
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
        error?.let { Text(it, color = Qrme.Red, fontSize = 13.sp) }
    }
}

// ---- Chat (the core loop: an interactor talks with the profile) ----

private data class Bubble(val mine: Boolean, val text: String, val pending: Boolean)

@Composable
fun ChatScreen(vm: StudioViewModel) {
    var messages by remember { mutableStateOf<List<Bubble>>(emptyList()) }
    var draft by remember { mutableStateOf("") }
    var busy by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }

    fun send() {
        val text = draft
        if (text.isBlank()) return
        draft = ""
        messages = messages + Bubble(true, text, false)
        busy = true; error = null
        vm.call({
            var interactor = vm.interactorId
            if (interactor == null) {
                interactor = ApiClient.createInteractor("You")
            }
            interactor!! to ApiClient.chat(vm.pid!!, vm.token!!, interactor, text)
        }) { r ->
            busy = false
            r.onSuccess { (interactor, reply) ->
                vm.rememberInteractor(interactor)
                messages = messages + if (reply.content != null && reply.status == "approved") {
                    listOfNotNull(
                        Bubble(false, reply.content, false),
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
                    Text(m.text,
                        color = if (m.pending) Qrme.T2 else Qrme.Txt, fontSize = 14.sp,
                        modifier = Modifier
                            .clip(RoundedCornerShape(13.dp))
                            .background(if (m.mine) Qrme.BrandA.copy(alpha = 0.35f)
                                        else Qrme.Card.copy(alpha = 0.9f))
                            .padding(horizontal = 12.dp, vertical = 9.dp))
                }
            }
            error?.let { Text(it, color = Qrme.Red, fontSize = 13.sp) }
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
private fun SmallAction(text: String, onClick: () -> Unit) {
    Box(
        Modifier.clip(RoundedCornerShape(50)).background(Qrme.BrandA)
            .clickable { onClick() }
            .padding(horizontal = 12.dp, vertical = 8.dp),
    ) {
        Text(text, color = Color.White, fontSize = 12.sp, fontWeight = FontWeight.Bold)
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
        r.onSuccess { vm.rememberInteractor(it); block(it) }
            .onFailure { onError(it.message ?: "couldn't create your identity") }
    }
}

@Composable
private fun StrangerPanel(vm: StudioViewModel) {
    var alias by remember { mutableStateOf("") }
    var waiting by remember { mutableStateOf(false) }
    var connectionId by remember { mutableStateOf<String?>(null) }
    var matchedWith by remember { mutableStateOf<String?>(null) }
    var messages by remember { mutableStateOf<List<ConnMsg>>(emptyList()) }
    var draft by remember { mutableStateOf("") }
    var error by remember { mutableStateOf<String?>(null) }

    fun refresh(cid: String) {
        val me = vm.interactorId ?: return
        vm.call({ ApiClient.connectionMessages(cid, me) }) { r ->
            r.onSuccess { messages = it }
        }
    }

    fun join() {
        error = null
        withInteractor(vm, { error = it }) { me ->
            vm.call({ ApiClient.joinQueue(me, alias) }) { r ->
                r.onSuccess {
                    if (it.status == "matched" && it.connectionId != null) {
                        connectionId = it.connectionId
                        matchedWith = it.matchedWith
                        waiting = false
                        refresh(it.connectionId)
                    } else waiting = true
                }.onFailure { error = it.message }
            }
        }
    }

    screenScroll {
        val cid = connectionId
        if (cid == null) {
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                Text("Meet a stranger", color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
                Text("Anonymous, friendly matchmaking — they see only your alias, and either side can end it. (The rated tier needs age verification, which this app doesn't do.)",
                    color = Qrme.T2, fontSize = 12.sp)
                labeledField("Alias (optional)", alias, "Stranger") { alias = it }
                BrandButton(if (waiting) "Waiting for a match — check again" else "Find a match") { join() }
            }
        } else {
            Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text("Talking with ${matchedWith ?: "a stranger"}", color = Qrme.Txt,
                        fontSize = 16.sp, fontWeight = FontWeight.Bold)
                    TextButton(onClick = {
                        vm.interactorId?.let { me ->
                            vm.call({ ApiClient.endConnection(cid, me) }) {
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
                                vm.call({ ApiClient.sendConnectionMessage(cid, me, text) }) { r ->
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
        vm.call({ ApiClient.roomTranscript(roomId) }) { r ->
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
                                vm.call({ ApiClient.roomMessage(current.id, me, text) }) { r ->
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
                            vm.call({ ApiClient.roomAdvance(current.id) }) { r ->
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
        TabRow(selectedTabIndex = seg, containerColor = Qrme.Card, contentColor = Qrme.BrandA) {
            listOf("General", "Summon", "Market", "Packs", "Gaming", "License").forEachIndexed { i, t ->
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
                else -> LicensePanel(vm)
            }
        }
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
    fun reload() { vm.call({ ApiClient.beacons(vm.pid!!) }) { r -> beacons = r.getOrDefault(emptyList()) } }
    LaunchedEffect(Unit) { reload() }

    screenScroll {
        Column(Modifier.card(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("@handle", color = Qrme.Txt, fontSize = 16.sp, fontWeight = FontWeight.Bold)
            Text("A unique name anyone can summon the profile by.", color = Qrme.T2, fontSize = 12.sp)
            labeledField("Handle", handle, "rosa_the_gardener") { handle = it }
            SmallAction("Claim") {
                if (handle.isNotBlank()) {
                    error = null
                    vm.call({ ApiClient.claimHandle(vm.pid!!, handle) }) { r ->
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
