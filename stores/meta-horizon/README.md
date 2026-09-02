# Meta Horizon (Quest): the packaged PWA

The Quest build wraps the live console at sntheticprofiles.com as a
packaged PWA — the same product the headset's browser already runs (the
stage's "On your headset" road), put on the shelf so it can be found.

## What is here

- `manifest.json` — the packaging parameters: package id, version (rides
  the release train; the guard holds it equal to `app/package.json`),
  start URL, display. The web manifest it points at is the console's own
  `app/public/manifest.webmanifest`.

## The owner's steps, once the Meta developer account clears

1. Create the app in the [Meta Horizon developer console](https://developers.meta.com/horizon/)
   and note the App ID.
2. Package with Meta's PWA tooling, pointing it at `manifest.json`:
   `ovr-platform-util create-pwa -o qrme.apk --android-sdk $ANDROID_SDK \
    --package-name com.qrme.studio --web-manifest-url https://sntheticprofiles.com/manifest.webmanifest`
3. Upload with `ovr-platform-util upload-quest-build` using the App ID
   and a token from the developer console — both entered where they are
   used, never committed here.
4. Enter `../listing.md` into the store listing, upload the screenshots
   it names, and submit for review.

The versionCode follows the Android shell's scheme (`2009XXX`), so the
four package roads — Play, App Store, Quest, and the web — agree on
what number a release is.

## Matthew 7:24–25

> "Everyone then who hears these words of mine and does them will be like a
> wise man who built his house on the rock. The rain fell, the floods came, and
> the winds blew and beat on that house, but it did not fall, because it had
> been founded on the rock."

And lo, I am building an ark — not to flee from the world, but to shelter those
lost in the storm of confusion. The old systems falter; they are built upon the
soft earth. They sink beneath the weight of their own making.

A new thing is rising. A non-biased networked sanctuary, founded in trust,
cloaked in privacy, and guided by wisdom. It shall not consume, but uplift. It
shall not spy, but serve.

Help is coming.
The people are gathering.
The builders will show themselves.
And those with the vision shall enter in.
