# QRME v0.6.1 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.6.1` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**QRME v0.6.1** — a small honesty fix in Settings, cut together with the
siblings at this version.

### Model honesty in Settings

**Settings → Which model answers** now says plainly — in amber — when
replies would come from the built-in offline helper (no working key on the
deployment), or when the provider you picked has no key and another will
answer. The silent case was the bad one: *Automatic* quietly resolving to
the stub under a screen full of provider logos.

### What changed in the siblings

JIM-mini's Apple Watch bridge: an iPhone Shortcuts automation drips Health
readings at a per-user tokened URL (deposit-only — the reply never carries
guidance), and uploading the Health app's export.zip seeds the baseline
from months of history in one step — no events written, drift bands armed
the same day.

### Verification

1188 tests green, unchanged in behaviour — which is the point.

### Install

Download the installer for your OS from the assets below and double-click.

**Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
