# Releasing

QRME ships two artifacts: the Python backend and the desktop console. This
describes cutting a versioned release and how (optional) code-signing works.

## Cut a release

1. Update [CHANGELOG.md](../CHANGELOG.md) — move `Unreleased` items under the new
   version and date it. Refresh [RELEASE_NOTES.md](../RELEASE_NOTES.md).
2. Bump `version` in `pyproject.toml` and `app/package.json` if changed.
3. Tag and push:

   ```bash
   git tag app-v0.1.0
   git push origin app-v0.1.0
   ```

The `app-v*` tag triggers `.github/workflows/desktop-release.yml`, which builds
the console into per-OS installers (`.dmg` / `.exe` / `.AppImage`) on real
macOS / Windows / Linux runners and attaches them to a GitHub Release. Paste
`RELEASE_NOTES.md` into the release body.

A manual **Run workflow** builds and uploads the installers as artifacts
*without* publishing a Release — useful for a dry run.

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
