# QRME v0.4.2 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.4.2` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**QRME v0.4.2** — the release where the installer you download actually gets
you running. One of three interoperating products (with
[jim-mini](https://github.com/davidsbianchi1984/jim-mini) and
[pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at
this version. Every change in it came from one first-run bug report against
a real Windows install.

### The installers are named for their release now

`app/package.json` carried its own version and no cut ever bumped it, so
0.4.0 and 0.4.1 both attached installers stamped **0.3.3** — built from the
right tag, named for the wrong release, and invisible to the auto-updater.
This is the first release whose installers come out named for it, and the
guard got wider on the way: **all five version strings must now agree**
(pyproject had quietly sat at 0.4.0 through the last cut, the lockfile roots
at 0.3.3 through two — each a duplicated number with nothing to fail).

### "Failed to fetch" says something now

The installer ships only the console; the API it talks to is started by
hand. Three things stood between a fresh install and a running product, and
each is gone:

- **`python -m qrme serve` answers the packaged console by default.** The
  console calls the API cross-origin, and `serve` never set
  `QRME_CORS_ORIGINS` — so every request died as *"Failed to fetch"* against
  a backend that was running fine, including for someone following the app's
  own instructions. A loopback serve now defaults CORS open (the posture the
  in-app hint always instructed), announced on stdout, `--no-cors` to close
  it, never on a non-loopback bind. Owner and interactor endpoints still
  require their bearer tokens.
- **The console's errors name the problem.** A network-level failure now
  says which backend URL was unreachable and the command that starts one —
  which the old hint got wrong too: bare `python -m qrme` only prints the
  launcher menu.
- **The age field stops pre-filling a birthdate** — a sample date sitting in
  an age-verification box is a wrong answer already submitted.

### The default model is current

The Anthropic provider defaults to **`claude-opus-5`** (`QRME_MODEL` still
overrides). Verified against the live API: with `QRME_LLM=anthropic` every
chat is a real round-trip to api.anthropic.com, and the per-profile
switchboard (`PUT /profiles/{id}/model`) stores and honors a choice of
Claude, ChatGPT, Grok, Perplexity, Gemini, or the offline stub.

### Verification

1158 tests green. The serve-CORS default and the five-way version agreement
are both guarded, and the CORS guard is mutation-checked.

### Install

Download the installer for your OS from the assets below (built by the
`desktop-release` workflow from the `app-v0.4.2` tag — and named 0.4.2, which
is the point), run `python -m qrme` and pick your device, or open it on your
phone — see the README.

**Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
