# QRME v0.5.0 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.5.0` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**QRME v0.5.0** — the round where you pick your model by its own logo.
One of three interoperating products, all three cut together at this
version.

### Pick your model, by its own logo

The model picker is no longer a dropdown of strings. **Settings → Model**
shows a tile per provider — Claude, ChatGPT, Grok, Perplexity, Gemini —
each with its own glyph, drawn here rather than copied, so you can see at
a glance which one is speaking for your profile and switch with one click.
*Auto* stays available for "whichever is configured," and the tile for a
provider you have no key for says so rather than failing later.

The choice rides on the same provider layer that already carried the
bring-your-own-key header: a request with `x-llm-api-key` runs on the
caller's credential, which is never persisted and never logged, and a
request without one uses the deployment's key.

### Verification

1188 tests green, including that the selected provider survives a restart,
that choosing a provider with no credential reports that plainly instead
of silently answering from another one, and that the request-scoped key
still outranks the stored one.

### Install

Download the installer for your OS from the assets below and double-click.

**Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
