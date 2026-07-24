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
**Manage** — settings (model picker `/models`, `/profiles/{id}/model` +
objections), **Summon** (@handle `/profiles/{id}/handle`, QR beacons
`/profiles/{id}/beacons`, and the `/summon?ref=` resolver), **Market**
(`/marketplace/listings` create / browse / remove), and **License**
(offer terms `/profiles/{id}/license`, grants `/profiles/{id}/licenses`,
revoke `/licenses/{gid}`)

On the phone form factors, Social, Apps, and Robots share one **Connect** tab
(segmented on iOS, a `TabRow` on Android) so the bottom bar stays at five
destinations; Windows' sidebar keeps Connect (Social / Apps) and Robots as
separate items.

They persist the returned `owner_token` so the app resumes signed-in, and share
one dark-OLED palette so all three feel like one product. See each folder's
README for the exact build/run commands.

Two cross-cutting guarantees ride on every generated surface:

- **Language** (`/languages`, `/profiles/{id}/language`, picker in Settings):
  the profile speaks its owner-set language everywhere it appears — chat,
  composed posts, room turns, robot speech — generated natively in-language
  via the persona system prompt.
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
