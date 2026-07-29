# QRME v0.14.2 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.14.2` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**QRME v0.14.2** — the vault posture survives suite mode.

In suite mode the mounted QRME used to run with no PDI tandem, so
coordinations quietly stopped sealing. The gateway now finds (or mints
once, by name) a dedicated vault tenant — `suite:qrme-vault` — and
injects QRME's own PDIClient over the in-process bridge.
`GET /suite/health` reports both tandems, and `POST /suite/operations`
is the provenance view: your coordinations as the vault recorded them,
authenticated with your own owner token and scoped by owner. The
launcher shows the two joints as lights, builds the ecosystem in one
press, and lists your operations. The tandem contract (docs/tandem.md)
documents suite mode, and `python -m suite.smoke` is repaired (its user
now joins a private plan before asserting the exchange sealed).

### Verification

Full suite green.

### Install

If you have 0.7.0 or later, this arrives on its own — one restart when
prompted.

**Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
