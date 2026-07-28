# QRME v0.4.3 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.4.3` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**QRME v0.4.3** — the release where the app got a front door, and the
installer got legs. One of three interoperating products (with
[jim-mini](https://github.com/davidsbianchi1984/jim-mini) and
[pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at
this version.

### Accounts — the address is proven before sign-in works

Email + password, in the shape every mainstream flow has taught people, built
as our own screens: create-account and sign-in tabs, show/hide password
toggles, the password typed twice with a live match check, the requirement
stated up front, and **Forgot password**. Behind it, the security spine:

- `POST /signup` creates an account that **cannot sign in yet** — a 6-digit
  code goes to the address (SMTP when configured, printed to the server
  terminal otherwise) and only `POST /verify-email` proves the inbox and
  mints the first token.
- The account is what *owns*: its id is the `owner_id` profiles are created
  under and the `account_id` memberships bill to. Every profile keeps its
  own owner capability token exactly as before.
- Password reset by the same emailed-code proof — and a reset **revokes
  every account session**, so whoever prompted it, only the inbox holder
  stays signed in.
- Unknown-address and wrong-password answer identically, and neither resend
  nor reset-request reveals who has an account.
- Passwords PBKDF2 with per-account salts; codes hashed at rest, single-use,
  15-minute expiry.

### Bring your own model key

Paste your credential (Anthropic, OpenAI, xAI, Gemini) in the Control
Center: it stays on your device, rides only your requests as
`x-llm-api-key`, and the server **never stores or logs it** — a test dumps
the whole database and asserts the key is not in it. A key makes your
explicit provider choice usable with no deployment credentials at all, and
on auto it defaults to Claude rather than the stub. The deployment's env
key remains the fallback: an operator lending theirs out.

### The installer runs itself

The whole Python backend ships **frozen inside the installer** (PyInstaller,
per-OS) and the app spawns it at launch when nothing answers `/health` —
double-click-and-done: no Python install, no terminal, data under the app's
own user-data directory, the backend dying with the window. A backend you
already run is left alone.

### Verification

1174 tests green. The frozen binary was built and booted on Linux; the
account rules — code single-use, purpose-bound, reset revoking sessions,
no address oracles, nothing stored in the clear — are each a test.

### Install

Download the installer for your OS from the assets below (built by the
`desktop-release` workflow from the `app-v0.4.3` tag) and double-click —
this is the first release where that is the whole instruction. Or run
`python -m qrme` and pick your device.

**Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
