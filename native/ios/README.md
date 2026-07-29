# QRME — iOS (SwiftUI)

A native SwiftUI app for iPhone, wired to the QRME backend. Four screens —
**Create Profile → Overview → Compose → Posts** — hitting the real `/profiles`,
`/profiles/{id}`, `/profiles/{id}/compose`, and `/profiles/{id}/posts` endpoints.

## Run in the Simulator (macOS)

Requires Xcode 15+ and [XcodeGen](https://github.com/yonyz/XcodeGen)
(`brew install xcodegen`).

```bash
cd native/ios
xcodegen generate          # writes QrmeStudio.xcodeproj from project.yml
open QrmeStudio.xcodeproj  # then ⌘R with an iPhone simulator selected
```

Start the backend first, on the host (the Simulator shares your Mac's network,
so `127.0.0.1` resolves):

```bash
# from the repo root
QRME_CORS_ORIGINS=* uvicorn qrme.api:app
```

The default base URL is `http://127.0.0.1:8000` (see `Sources/ApiClient.swift`).
`Info` in `project.yml` sets `NSAllowsLocalNetworking` so the Simulator can reach
plain-http localhost.

## Layout

| File | Role |
| --- | --- |
| `project.yml` | XcodeGen spec (bundle id, iOS 16 target, ATS exception) |
| `Sources/QrmeApp.swift` | `@main` app + root tab bar / create-profile switch |
| `Sources/ApiClient.swift` | async `URLSession` client + wire models |
| `Sources/AppState.swift` | created profile id + owner token, persisted |
| `Sources/Theme.swift` | the dark-OLED palette |
| `Sources/Views/*` | Welcome, Overview, Chat (Profile/Stranger/Rooms), Studio (Compose/Posts/Study), Connect (Social/Apps/Robots), Manage (General/Summon/Market/License) |

The tab bar holds five destinations: **Chat** groups the profile conversation
with Stranger matchmaking and multiparty Rooms, **Studio** groups Compose /
Posts / Study, **Connect** groups the social-platform connections, the
connected-apps catalog, and robotic embodiment, and **Manage** groups settings
with the profile's @handle + QR beacons, marketplace listing, and license
offer.

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
