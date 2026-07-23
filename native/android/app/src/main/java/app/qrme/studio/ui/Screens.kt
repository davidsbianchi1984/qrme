package app.qrme.studio.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
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
import app.qrme.studio.CatalogApp
import app.qrme.studio.Excursion
import app.qrme.studio.Objection
import app.qrme.studio.Post
import app.qrme.studio.ProfileCard
import app.qrme.studio.ProviderInfo
import app.qrme.studio.Robot
import app.qrme.studio.RobotSpec
import app.qrme.studio.SocialConn
import app.qrme.studio.StudioViewModel

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
            }
            error?.let { Text(it, color = Qrme.Red, fontSize = 13.sp) }
            BrandButton("Create profile", enabled = name.isNotBlank() && persona.isNotBlank(), busy = busy) {
                error = null
                vm.createProfile(name, persona, kind, birthdate, onError = { error = it }, onBusy = { busy = it })
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
                Text(p.content, color = Qrme.Txt, fontSize = 14.sp)
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
                    Text(p.content, color = Qrme.Txt, fontSize = 14.sp)
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
    var error by remember { mutableStateOf<String?>(null) }

    fun reload() {
        vm.call({ ApiClient.models() }) { r -> providers = r.getOrDefault(emptyList()) }
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
                messages = messages + if (reply.content != null && reply.status == "approved")
                    Bubble(false, reply.content, false)
                else
                    Bubble(false, "⏳ Held for review" +
                        (reply.flagReason?.let { " — $it" } ?: ""), true)
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
