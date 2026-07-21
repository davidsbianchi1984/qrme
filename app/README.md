# QRME desktop app

A **runnable** front-end for QRME — React + Vite + TypeScript, wrapped in
**Electron** so it's an actual desktop app you can run and package into an
installable binary. It talks to the QRME FastAPI backend over HTTP.

It's a real client: create a profile, chat with it (persona-, relationship-,
and engagement-conditioned replies), manage relationships, view and clear the
vaulted memory, and watch offline status — all against live API endpoints.

## 1. Start the backend (with CORS for the app)

From the repo root:

```bash
pip install -e .[dev]
QRME_CORS_ORIGINS=* uvicorn qrme.api:app        # http://127.0.0.1:8000
```

No API key needed — without `ANTHROPIC_API_KEY` the deterministic stub provider
answers, so the whole thing runs offline.

## 2. Run the front-end

```bash
cd app
npm install
```

- **In the browser** (fastest): `npm run dev` → open http://localhost:5173
- **As a desktop window** (Electron): `npm run electron:dev`
- **Build the web bundle**: `npm run build` → `dist/`
- **Package an installable binary**: `npm run dist` → `release/`
  (produces a `.dmg` on macOS, `.exe`/NSIS on Windows, `.AppImage` on Linux —
  run on the target OS; code-signing is left to you).

The backend URL is configurable in the app under **Control Center → API
connection** (default `http://127.0.0.1:8000`).

## What it's wired to

| Screen | Endpoints |
|---|---|
| Onboarding | `POST /profiles`, `POST /interactors`, `PUT /profiles/{id}/relationships/{interactor}` |
| Home | `GET /profiles/{id}`, `GET /profiles/{id}/stats` |
| Chat | `POST /profiles/{id}/chat` (shows moderation / specialist-handoff state) |
| Relationships | `GET /profiles/{id}/transparency`, add via interactor + relationship |
| Memory Vault | `GET`/`DELETE /profiles/{id}/memory/{interactor}` |
| Control Center | `GET /offline/status`, base-URL config, sign out |

## Layout

```
app/
├─ electron/         Electron main + preload (the desktop wrapper)
├─ src/
│  ├─ api.ts         typed QRME API client
│  ├─ store.tsx      session state (persisted to localStorage)
│  ├─ App.tsx        shell + sidebar nav
│  └─ screens/       Onboarding, Home, Chat, Relationships, Memory, Settings
└─ vite.config.ts
```
