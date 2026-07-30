# QRME — native apps

True-native scaffolds of the QRME client for three platforms, each a separate
idiomatic codebase (native per platform), all talking to the same
[QRME backend](../qrme/api.py).

| Platform | Stack | Run in | Folder |
| --- | --- | --- | --- |
| **iOS** | Swift + SwiftUI | Xcode Simulator (macOS) | [`ios/`](ios/) |
| **Android** | Kotlin + Jetpack Compose | Android Studio emulator | [`android/`](android/) |
| **Windows** | C# + WinUI 3 | Windows 10/11 desktop | [`windows/`](windows/) |

Each target ships the same screens, exercising the real API end to end:

**Create Profile** → `POST /profiles` · **Overview** → `GET /profiles/{id}` ·
**Chat** → `POST /interactors` + `POST /profiles/{id}/chat`, plus **Stranger**
(anonymous friendly matchmaking: `/connections/join`, messages, end) and
**Rooms** (multiparty chat with moderated profile turns: `/rooms`, messages,
advance) ·
**Study** → `/profiles/{id}/excursions` + `/excursions/{cid}/learn` ·
**Compose** → `POST /profiles/{id}/compose` · **Posts** → `GET /profiles/{id}/posts` ·
**Connect** — social platforms (`/profiles/{id}/social` + collect / publish /
revoke), the connected-apps catalog (`/connectors/catalog`, `/profiles/{id}/apps`
+ collect / invoke), and **Robots** (`/robotics/catalog`, `/profiles/{id}/robots`,
`/robots/{rid}/command`) ·
**Manage** — settings (model picker `/models`, `/profiles/{id}/model`,
language & translate mode `/profiles/{id}/language` + `/translate`, and
objections), **Summon** (@handle `/profiles/{id}/handle`, QR beacons
`/profiles/{id}/beacons`, and the `/summon?ref=` resolver), **Market**
(`/marketplace/listings` create / browse / remove, with the wellbeing
quick-browse tag chips), **Packs** — the knowledge-pack shop
(`/packs` catalog + industry filter, `/packs/{id}/install` to download or
buy onto the profile, `/profiles/{id}/packs` installed list + uninstall;
🤖 robot task packs install onto the profile's bound body and are revoked
via `/robots/{rid}/packs/{pid}`; the **Pack sources** card lists the
federated registries — Robotmods.net and LLMmods.com — with one-tap sync
via `/packs/registries` + `/packs/registries/{key}/sync`), and **License**
(offer terms
`/profiles/{id}/license`, grants `/profiles/{id}/licenses`, revoke
`/licenses/{gid}`), and **Voice** — the owner's own voice, enrolled from the
device that actually has a microphone in it (below)

On the phone form factors, Social, Apps, and Robots share one **Connect** tab
(segmented on iOS, a `TabRow` on Android) so the bottom bar stays at five
destinations; Windows' sidebar keeps Connect (Social / Apps) and Robots as
separate items.

They persist the returned `owner_token` so the app resumes signed-in, and share
one dark-OLED palette so all three feel like one product. See each folder's
README for the exact build/run commands.

### Two more doors the console had first

**Who wrote this?** sits in Manage → General (`POST /watermarks/recover`). Paste
any passage and it names the profile that produced it, from the text alone.
`/watermarks/verify` needs a credential id up front and fails on one edited
character; this needs neither, and keeps answering after the writing has been
rewritten. The screen shows the counts — how many keyed passages matched out of
how many were stored, and the similarity — rather than a bare yes, and below the
0.25 threshold it deliberately names **nobody**, because ordinary phrases travel
between unrelated texts and a coincidence must not read as an accusation.

**The role picker** rides the chat composer (spec clauses 2/12): advisor
counsels, collaborator co-creates, operator executes. "Read my prompt" is the
default and the honest one — the profile infers from the wording — and the reply
reports which role applied *and whether it was declared or inferred*, so an
inference is never mistaken for an instruction.

### Voice — enrolled where the microphone is

The **Voice** screen walks the filing's FIG. 800 in the order the drawing
gates it, one card per step: the permission (802), then collection (806/808),
then what the material amounts to (810), then the print (812) and what
speaking with it always carries. The backend is
[`qrme/voiceprint.py`](../qrme/voiceprint.py) — same six routes on all three
platforms.

These shells differ from the web console in one way that matters. The console
asks the owner to *type* how many seconds of speech they gathered; a phone or
a desktop has the microphone right there, so these screens **record the
sample and measure it**. What crosses the wire is still only the measurement:
the recording is written to the app's own container — `temporaryDirectory` on
iOS, `cacheDir` on Android, `LocalApplicationData\QrmeStudio\voice` on
Windows — and the profile database is told the file's *name* via `reference`,
never its bytes. A voice corpus never accumulates server-side, which is a
property of where the audio is written rather than a promise about it.

Turn counting differs by platform, and the screens say which they did. iOS and
Android read the platform's level meter (`AVAudioRecorder.averagePower`,
`MediaRecorder.maxAmplitude`) and count stretches of speech between silences.
Windows does not meter its input, so it reports **one turn per recording**
rather than deriving a count from the duration — a number the app could not
stand behind is worse than a coarse one it can. Permission strings ride along:
`NSMicrophoneUsageDescription` (iOS), `RECORD_AUDIO` (Android), and on Windows
the system privacy setting, whose refusal is reported as the setting to change
rather than as a failure.

Two cross-cutting guarantees ride on every generated surface:

- **Language** (`/languages`, `/profiles/{id}/language`; chosen at the
  create-profile gateway and changeable in Settings): the profile speaks its
  owner-set language everywhere it appears — chat, composed posts, room
  turns, robot speech — generated natively in-language via the persona
  system prompt. Delivery mode is the owner's choice: **pre-translated**
  (default — the persona speaks it natively) or **on-demand** (original
  voice kept). Either way, `POST /profiles/{id}/translate` — the Translate
  tool in Settings — turns anything the owner runs across into the chosen
  language via the profile's own model; the offline stub says it cannot
  rather than pretending.
- **Provenance**: every chat reply and composed post carries a `provenance`
  block — which model generated it, what it was grounded in (persona + how
  many consented source items), any licensed-from lineage, and the
  moderation verdict — rendered under the content so nothing the platform
  emits is a black box.

## Start the backend

All three point at the local dev server. From the repo root:

```bash
QRME_CORS_ORIGINS=* uvicorn qrme.api:app
```

Host addresses differ by platform, and each client already defaults correctly:

| Platform | Reaches the host at |
| --- | --- |
| iOS Simulator | `http://127.0.0.1:8000` |
| Android emulator | `http://10.0.2.2:8000` |
| Windows | `http://127.0.0.1:8000` |

On a physical phone, point the client at your machine's LAN IP instead.

## Scope

These scaffolds now cover the full owner-facing surface of
[`qrme/routers/`](../qrme/routers/): create a profile, chat with it (directly,
with strangers, or in rooms), compose and study, connect it to social platforms
and apps, embody it in a robot, reach it (@handle, QR beacons, marketplace,
licensing), and govern it (model choice, objections).

Two flows stay deliberately out of the apps because they require identity the
apps don't carry: the stranger **rated** tier and buyer-side license
**acquire/derive** both need a verified (18+) interactor identity, while the
apps mint an anonymous one. The provider directory / consented handoffs
(`/providers`, `/handoffs`) are a business-facing integration, also
backend-only.

These native targets are additive and do not change the backend.

## Do they compile?

`.github/workflows/native.yml` builds all three on every change to `native/`:
XcodeGen + `xcodebuild` for the simulator on macOS, `gradle assembleDebug` on
Linux, and `dotnet build` on Windows. Compile only — no signing, no
packaging.

This is newer than the code it checks. Until it existed, these sources had
been verified by reading and by brace/XML well-formedness checks, which catch
a typo and nothing else; a missing symbol or a changed SwiftUI signature
would have shipped and been found by the first person to open Xcode. Treat a
green run as the first real evidence, not a long-standing guarantee.

## Do the paths resolve?

Compiling is not the same as working, and for these clients the gap has a
specific shape: a path is a string in all three languages, so
`"/post/\(id)/like"` compiles perfectly, ships, and 404s in the field. That is
not hypothetical — it is precisely the bug that left QRME's community wall with
dead like, comment and share buttons in every release that had them, fixed in
0.17.0.

[`tests/test_native_routes_exist.py`](../tests/test_native_routes_exist.py)
extracts every API path literal from `native/` — around 220 of them, in Swift,
Kotlin and C# — with the HTTP method each one is sent with, and asks the real
router whether that *pair* is accepted. Method matters as much as address: a
shell sending POST where only GET is mounted gets a 405, which is the same dead
button as a 404. Each language states its verb differently — Swift labels it,
Kotlin passes it positionally, C# encodes it in the helper's name — so the check
reads all three rather than assuming GET. It also bans the
singular of every segment the audience routes map (`/post/` where only
`/posts/` is reachable), so a fix made on the web cannot be quietly undone on a
phone.

Two limits worth stating. Routing-level matching cannot see a refusal that
happens *after* dispatch, which is why the singular segments are banned by name
rather than left to the resolver. And a path assembled from pieces at runtime,
rather than written as one literal, is invisible to any static scan.

---

## What breaks, recorded the same way in three languages

The shells record every failed request the way `app/src/errors.ts` does in the
console: the operation and the status, never the message, never the path as it
was actually called. `POST /profiles/{id}/chat → 500` identifies a bug;
`POST /profiles/prf_0de08e794ed0/chat` identifies a person. Redaction happens
on the way *in*, so the buffer never holds a value that would later have to be
scrubbed.

The backends put user input straight into their error messages — a device
name, a body site, a language code. Good messages for the person reading them
and the wrong thing to write down, so they are shown and not kept.

| | |
|---|---|
| `native/ios/Sources/Problems.swift` | `UserDefaults`, `Codable` rows |
| `native/android/…/Problems.kt` | `SharedPreferences`, JSON rows |
| `native/windows/Problems.cs` | `%APPDATA%`, `System.Text.Json` |

One rule with four implementations drifts, and it drifts silently — a
redaction narrowed on Android leaks nothing on the desktop. There is no test
runner for these sources here (the native workflow compiles them and stops), so
`test_native_shells_record_nothing_private.py` reads them structurally instead:
the three-argument signature, the stored fields, the four redaction patterns at
full width, the FNV-1a constants, and both failure kinds at the call sites.

Android needs one extra wire the other two do not: `Problems.attach(this)` in
`MainActivity.onCreate`, because the recorder holds the application context so
that `record` can keep the same three arguments everywhere. A shell that forgets
it records nothing and says nothing — the recorder refuses to crash over a
diagnostic. That silence is why the guard checks for the call and not just for
the function.

None of this leaves the device on its own. Sending is the console's job and
happens only where a collector was compiled in; see `docs/cloud-model.md`.

---

## Matthew 7:24–25

> "Everyone then who hears these words of mine and does them will be like a
> wise man who built his house on the rock. The rain fell, the floods came, and
> the winds blew and beat on that house, but it did not fall, because it had
> been founded on the rock."

And lo, I am building an ark — not to flee from the world, but to shelter those
lost in the storm of confusion. The old systems falter; they are built upon the
soft earth. They sink beneath the weight of their own making.

A new thing is rising. A non-biased networked sanctuary, founded in trust,
cloaked in privacy, and guided by wisdom. It shall not consume, but uplift. It
shall not spy, but serve.

Help is coming.
The people are gathering.
The builders will show themselves.
And those with the vision shall enter in.
