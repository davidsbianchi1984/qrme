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
**Chat** → `POST /interactors` + `POST /profiles/{id}/chat` ·
**Study** → `/profiles/{id}/excursions` + `/excursions/{cid}/learn` ·
**Compose** → `POST /profiles/{id}/compose` · **Posts** → `GET /profiles/{id}/posts` ·
**Connect** — social platforms (`/profiles/{id}/social` + collect / publish /
revoke), the connected-apps catalog (`/connectors/catalog`, `/profiles/{id}/apps`
+ collect / invoke), and **Robots** (`/robotics/catalog`, `/profiles/{id}/robots`,
`/robots/{rid}/command`) ·
**Settings** → model picker (`/models`, `/profiles/{id}/model`) + objections
(`/profiles/{id}/objections`, attest)

On the phone form factors, Social, Apps, and Robots share one **Connect** tab
(segmented on iOS, a `TabRow` on Android) so the bottom bar stays at five
destinations; Windows' sidebar keeps Connect (Social / Apps) and Robots as
separate items.

They persist the returned `owner_token` so the app resumes signed-in, and share
one dark-OLED palette so all three feel like one product. See each folder's
README for the exact build/run commands.

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

These scaffolds cover the core owner-facing loop end to end: create a profile,
chat with it, compose and study, connect it to social platforms and apps,
embody it in a robot, and govern it (model choice, objections). The remaining
surfaces (relationships, community, licensing, summons) have backend endpoints
under [`qrme/routers/`](../qrme/routers/) to grow into further native screens.

These native targets are additive and do not change the backend.
