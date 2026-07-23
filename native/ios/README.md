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
| `Sources/Views/*` | Welcome, Overview, Compose, Posts, Robots, Settings |

## Not yet wired

This is a functional scaffold, not the full screen gallery. Chat, relationships,
connections, connectors, and knowledge excursions all have backend endpoints
(`qrme/routers/`) ready to add as further screens.
