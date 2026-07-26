# QRME v0.2.2 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.2.2` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**QRME v0.2.2** — a documentation release. **No code changed**: no new routes,
no schema, no behaviour. Everything here corrects something that was
*described* wrongly, which on this round turned out to be the thing costing
real time. One of three interoperating products (with
[jim-mini](https://github.com/davidsbianchi1984/jim-mini) and
[pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at this
version.

### Fixed

- **`POST /marketplace/seed` advertised the opposite of what it does.** Its
  docstring — the text served in the OpenAPI docs, which is where somebody
  deciding whether a call is safe to make actually reads — still said
  *"Idempotent — already-seeded profiles are skipped"*. v0.2.1 made that only
  half true: the endpoint now also **repairs**, filling a missing portrait or
  appearance on a starter that already exists.

  The stale sentence pointed away from the fix. Anyone looking at three
  starters rendering as bare initials would read that line and conclude the one
  call that repairs them could not possibly help, because skipping is precisely
  what they do not want. The claim was wrong in **four** places — the endpoint,
  `qrme/seed.py`'s module and `seed()` docstrings, and the README's Starter
  Collection row — and all four now say idempotent *and* repairing, blank-only,
  reporting `repaired` alongside `created` and `skipped`.

  **To repair a live deployment, this is still the one call:**
  `POST /marketplace/seed`.

- **Three releases of changelog links were missing.** `[0.1.9]`, `[0.2.0]` and
  `[0.2.1]` had headings but no link definitions, so three shipped versions
  rendered as literal `[0.2.1]` bracket text rather than linking anywhere, and
  `[Unreleased]` still compared against `app-v0.1.8` — presenting a
  three-release diff as though it were an empty one.

- **The release checklist is why that kept happening**, and is the entry that
  matters most here. `docs/releasing.md` step 1 said to move the `Unreleased`
  items under the new heading and date it, and stopped — it never mentioned the
  link definition at the bottom of the file. The step was skipped three
  releases running by someone following the instructions correctly, and nothing
  complains when you miss it: the heading renders fine, and the damage appears
  hundreds of lines from where the edit was made.

  Step 2 was wrong in the same direction. It named `pyproject.toml` and
  `app/package.json` when the version string lives in **five** places — the two
  it omitted being the `FastAPI(...)` call in `qrme/api.py` and the second root
  entry in `app/package-lock.json`, both of which had to be rediscovered each
  round. Both steps now say what they meant, in all three repositories.

### Money here is still simulated

Subscriptions, gifts and purchases write **real rows** on the creator's
statement and settle through the same payout sweep as pack sales and licence
fees — but **no real funds move**, and every money-bearing response says so in
its own body. [docs/commerce.md](docs/commerce.md) lists what is absent.

### Verification

549 tests green — **the same 549, passing the same way**, which is the point of
a release that claims no functional change. 197 routes, also unchanged. Version
strings moved in exactly five places: `pyproject.toml`, the FastAPI app,
`app/package.json`, and the two root entries in its lockfile (dependency
versions untouched). Every version heading in the changelog was checked against
its link definition — 12 for 12.

### Install

Download the installer for your OS from the assets below (built by the
`desktop-release` workflow from the `app-v0.2.2` tag), run `python -m qrme`
and pick your device, or open it on your phone — see the README.

**Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
