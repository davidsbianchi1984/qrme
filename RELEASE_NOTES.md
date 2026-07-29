# QRME v0.10.0 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.10.0` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**QRME v0.10.0** — a real offline model, cut together with the siblings.

### The Local (Ollama) tile

Install **Ollama** from [ollama.com](https://ollama.com), pull a model
(`ollama pull deepseek-r1:1.5b`), and QRME finds the running daemon on
its own: the **Local (Ollama)** tile in Settings → Model lights up
configured — no key, no account, and **nothing ever leaves your
machine**. *Automatic* prefers the local model over the canned stub
whenever no cloud key is set; offline mode uses it too.

### Verification

1188 tests green.

### Install

If you have 0.7.0 or later, this arrives on its own — one restart when
prompted. Otherwise, download the installer for your OS from the assets
below.

**Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
