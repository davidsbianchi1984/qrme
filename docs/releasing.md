# Releasing

QRME ships two artifacts: the Python backend and the desktop console. This
describes cutting a versioned release and how (optional) code-signing works.

## The three products cut together

QRME, [JIM-mini](https://github.com/davidsbianchi1984/jim-mini) and
[PDI](https://github.com/davidsbianchi1984/pdi) are built to run in tandem, and
they are versioned as **one release**: the same number, cut in the same pass,
even when a repository has nothing of its own to ship that round.

This is a deliberate reversal. Through v0.1.5 each repository cut whenever it
happened to have work, so the numbers matched only by coincidence — QRME
reached 0.1.6 alone while the other two sat at 0.1.5, and "the suite" named no
particular combination of anything. Now a version names one combination of
three products, and anyone running all three can pin one number.

Three rules make that hold up:

**A repository with nothing to ship still cuts, and says so.** Its changelog
entry reads *there are no functional changes to X in this release*, in those
words, rather than being padded with restated work. A note that inflates an
empty round teaches people to skim the ones that are not empty.

**Tag the release-prep commit, not the tip of `main`.** Work keeps landing
while a release is cut, and anything that arrives after the changelog is
sectioned belongs under `[Unreleased]` — not to the version being tagged.
Tagging the tip publishes features under notes that do not describe them.
Check what `[Unreleased]` holds before choosing the commit.

**Cut all three even when only one has content.** The moment one is skipped the
numbers drift again, and the next round has to decide whether to re-align or
let them diverge — which is the state this rule exists to end.

### v0.1.5 and v0.1.6 have no tags

They were released — changelog, notes, version bumps — but the `app-v*` tags
were never pushed, so no GitHub Release exists for either. Their CHANGELOG
entries link to the release-prep **commit** instead of a tag, which is why
those two lines look different from the rest.

They are deliberately **not** being backfilled. Pushing those tags now would
fire `desktop-release.yml`, build installers on real runners, and publish
v0.1.5 and v0.1.6 Releases dated *after* v0.1.7 — putting superseded
installers at the top of a page people download from. The dead links were the
only real problem, and pointing them at commits fixes that without publishing
anything.

## Cut a release

1. Update [CHANGELOG.md](../CHANGELOG.md) — move `Unreleased` items under the new
   version and date it. Refresh [RELEASE_NOTES.md](../RELEASE_NOTES.md). Do the
   same in the sibling repositories, in the same pass.

   **Add the link definition at the bottom of the file, and repoint
   `[Unreleased]` at the version you are cutting:**

   ```markdown
   [Unreleased]: https://github.com/davidsbianchi1984/qrme/compare/app-v0.2.1...HEAD
   [0.2.1]: https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.2.1
   ```

   This is the step that gets missed, because nothing complains. The heading
   renders fine without a definition and the damage shows up hundreds of lines
   away — a released version rendering as literal `[0.2.1]` text, and an
   `[Unreleased]` link quietly diffing against a tag three releases old.
   0.1.9, 0.2.0 and 0.2.1 were all cut without it.

2. Bump the version string in **all five places**: `pyproject.toml`, the
   `FastAPI(...)` call in `qrme/api.py`, `app/package.json`, and the **two root
   entries** in `app/package-lock.json` — the top-level `"version"` and the one
   under `packages` → `""`. Leave every other version in the lockfile alone;
   dependency pins look identical and are not yours.
3. Tag and push:

   ```bash
   git tag app-v0.1.0
   git push origin app-v0.1.0
   ```

The `app-v*` tag triggers `.github/workflows/desktop-release.yml`, which builds
the console into per-OS installers (`.dmg` / `.exe` / `.AppImage`) on real
macOS / Windows / Linux runners and attaches them to a GitHub Release, with
GitHub's generated changelog as the body.

**Leave the release body empty when you create the tag.** When that workflow
finishes, `sync-release-notes.yml` runs and lays `RELEASE_NOTES.md` over the
top — dropping the maintainer preamble above the `---`, and keeping exactly one
copy of the generated *What's Changed*. Anything typed by hand is replaced.

Only one workflow writes that body, and it is that one. Both used to: the
installer build published `RELEASE_NOTES.md` verbatim, preamble included, two
to four minutes after the sync had already published it correctly. The build
always won, so every release needed re-syncing by hand. The build no longer
sets a body at all, and the sync waits for it rather than racing it.

Tag names are **case-sensitive** to the trigger. `App-v0.1.9` matches
`tags: ["app-v*"]` in neither workflow and silently does nothing.

A manual **Run workflow** on the build workflow uploads the installers as
artifacts *without* publishing a Release — useful for a dry run. To repair an
already-published body, run **sync-release-notes** manually with the tag; it
checks out that tag, so it publishes the notes that shipped with it rather than
whatever `main` says today.

## Code signing (optional)

Signing is driven entirely by repository **secrets** — nothing is committed, and
if the secrets are absent the installers are simply built **unsigned**. Set them
under *Settings → Secrets and variables → Actions*:

| Secret | Platform | Purpose |
| --- | --- | --- |
| `CSC_LINK` | macOS | Base64 of the Apple Developer ID certificate (`.p12`) |
| `CSC_KEY_PASSWORD` | macOS | Password for the `.p12` |
| `WIN_CSC_LINK` | Windows | Base64 of the Windows code-signing certificate (`.pfx`) |
| `WIN_CSC_KEY_PASSWORD` | Windows | Password for the `.pfx` |
| `APPLE_ID` | macOS | Apple ID for notarization |
| `APPLE_APP_SPECIFIC_PASSWORD` | macOS | App-specific password for notarization |
| `APPLE_TEAM_ID` | macOS | Apple Developer Team ID |

electron-builder reads these from the environment during `npm run dist`. macOS
notarization runs only when the `APPLE_*` secrets are present. The app is
built with the hardened runtime and the entitlements in
`app/build/entitlements.mac.plist`, which notarization requires.

### Getting the certificates (one-time)

**macOS** (removes the "unidentified developer" warning entirely):

1. Join the [Apple Developer Program](https://developer.apple.com/programs/)
   ($99/yr).
2. In Xcode (or developer.apple.com → Certificates), create a
   **Developer ID Application** certificate; export it from Keychain as a
   `.p12` with a password.
3. `base64 -i cert.p12 | pbcopy` → paste as the `CSC_LINK` secret; the export
   password becomes `CSC_KEY_PASSWORD`.
4. For notarization: create an [app-specific password](https://account.apple.com/account/manage)
   for your Apple ID → `APPLE_APP_SPECIFIC_PASSWORD`; set `APPLE_ID` (the
   account email) and `APPLE_TEAM_ID` (Membership page).

**Windows** (removes the SmartScreen "unknown publisher" warning after the
certificate builds reputation):

1. Buy an **OV or EV code-signing certificate** from a CA (Sectigo, DigiCert,
   SSL.com; roughly $80–400/yr). OV is fine to start; EV clears SmartScreen
   fastest.
2. Export/download as `.pfx` with a password; `base64 -i cert.pfx` →
   `WIN_CSC_LINK`, password → `WIN_CSC_KEY_PASSWORD`.
   (Newer CAs issue on hardware tokens/cloud HSMs — those need a
   cloud-signing step instead; open an issue when you get there.)

Add the secrets in each of the three repos (or an org-level secret shared by
all three), re-run the `desktop-release` workflow or push the next tag, and
the installers come out signed — no code changes needed.

## Full-stack integration

`.github/workflows/e2e.yml` boots all three products together and runs the
end-to-end flow ([docker/README.md](../docker/README.md)); it needs a
`SUITE_REPO_TOKEN` secret with read access to the sibling repositories.
