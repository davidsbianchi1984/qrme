# Suite launcher

One launcher, **one login, one origin** — QRME, JIM-mini, and PDI as a single
product. React + Vite + Electron, wired to the **suite gateway**
([`suite/gateway.py`](../suite/gateway.py)), which mounts all three APIs under a
single origin and provisions one identity across them in a single call.

## 1. Start the suite gateway

The gateway needs all three packages importable (install the jim-mini and pdi
packages alongside this one), then:

```bash
SUITE_CORS_ORIGINS='*' \
PDI_MASTER_KEY=$(python -c "import base64,os;print(base64.b64encode(os.urandom(32)).decode())") \
  uvicorn suite.gateway:app          # http://127.0.0.1:8000
```

- `GET /suite/health` — which products are mounted and live
- `POST /suite/session` — **unified sign-on**: `{display_name, birthdate}` →
  provisions a QRME profile, a JIM user, and a PDI tenant, returning all tokens
- `/qrme/...`, `/jim/...`, `/pdi/...` — each product, on the one origin

## 2. Run the launcher

```bash
cd launcher
npm install
npm run dev            # http://localhost:5173
npm run electron:dev   # desktop window
npm run dist           # installable binary → release/
```

Sign in once; the launcher shows each product's live status and a link to open
its console. To open the product consoles too, run each repo's `app/` (they
each read a configurable base URL — point them at the gateway prefix, e.g.
`http://127.0.0.1:8000/qrme`).

Below the product cards the dashboard shows the two **joints** the gateway
wires in-process (the care-team tandem and vault sealing, from
`/suite/health`'s `tandems` — amber means degraded, not down), a one-press
**Build my ecosystem** (`POST /suite/ecosystem`: demo org seeded in QRME,
JIM's care team linked to its first desk, idempotent), and the
**operations** list (`POST /suite/operations`): your coordinations as the
vault recorded them, scoped to your own owner token.

## 3. Installers

Built in CI on per-OS runners the same way as the product apps — see the
`desktop-release.yml` workflow.

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
