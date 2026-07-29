# QRME v0.14.1 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.14.1` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**QRME v0.14.1** — the suite wires its own tandem.

In suite mode the gateway bridges JIM's QRME client to the mounted QRME
app in-process, so the care team and specialist handoffs work with no
second server and no configuration. `POST /suite/ecosystem` takes the
tokens `/suite/session` returned and builds the working ecosystem in one
call — demo org seeded, care team linked — with the gateway storing no
credential of its own.

### Verification

Full suite green.

### Install

If you have 0.7.0 or later, this arrives on its own — one restart when
prompted.

**Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
