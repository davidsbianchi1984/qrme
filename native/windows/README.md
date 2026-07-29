# QRME — Windows (WinUI 3)

A native Windows desktop app in C# / WinUI 3 (Windows App SDK), wired to the QRME
backend. Same four screens as the other targets — **Create Profile → Overview →
Compose → Posts** — behind a `NavigationView`.

## Run

Requires the **.NET 8 SDK** and the **Windows App SDK** workload (Visual Studio
2022 → *".NET Desktop"* + *"Windows App SDK"*, or `winget install
Microsoft.WindowsAppRuntime.1.6`).

**Visual Studio:** open `QrmeStudio.csproj`, pick the `x64` configuration, press
**F5**.

**Command line:**

```powershell
cd native\windows
dotnet build -c Debug -r win-x64
dotnet run -c Debug -r win-x64
```

Start the backend first (Windows reaches `localhost` directly):

```powershell
# from the repo root
$env:QRME_CORS_ORIGINS = "*"; uvicorn qrme.api:app
```

The default base URL is `http://127.0.0.1:8000` (see `ApiClient.cs`). The app is
built **unpackaged** (`WindowsPackageType=None`), so it is not subject to the
MSIX loopback restriction and can call `127.0.0.1` without an exemption.

## Layout

| File | Role |
| --- | --- |
| `QrmeStudio.csproj` | net8.0-windows target, WindowsAppSDK, unpackaged |
| `App.xaml` / `.cs` | app entry + the palette resource dictionary |
| `MainWindow.xaml` / `.cs` | root frame; routes to Welcome or Shell by state |
| `Views/ShellPage.xaml` | `NavigationView` host + sign-out |
| `Views/WelcomePage` | create-profile form → `/profiles` |
| `Views/OverviewPage` | public card (`/profiles/{id}`) |
| `Views/ChatPage` | interactor chat (`/interactors`, `/profiles/{id}/chat`) |
| `Views/ComposePage` | topic → `/profiles/{id}/compose` |
| `Views/PostsPage` | feed (`/profiles/{id}/posts`) |
| `Views/StudyPage` | knowledge excursions (`/profiles/{id}/excursions`, learn) |
| `Views/CommunityPage` | stranger / rooms (Pivot) → `/connections/join` + messages, `/rooms` + messages/advance |
| `Views/ConnectPage` | social / apps (Pivot) → `/profiles/{id}/social`, `/connectors/catalog`, `/profiles/{id}/apps` |
| `Views/RobotsPage` | bind/command robots (`/robotics/catalog`, `/robots/{rid}/command`) |
| `Views/ReachPage` | summon / market / license (Pivot) → `/profiles/{id}/handle` + beacons + `/summon`, `/marketplace/listings`, `/profiles/{id}/license` + grants |
| `Views/SettingsPage` | model picker + objections (attest) |
| `ApiClient.cs` | `HttpClient` client + records |
| `AppState.cs` | identity + token, persisted to LocalAppData |

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
