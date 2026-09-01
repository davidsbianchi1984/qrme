# Viveport: the same launcher on HTC's shelf

Viveport takes the identical publish output the Steam depot ships —
`native/windows/QrmeStudio`, self-contained — uploaded through the
[Viveport developer console](https://developer.viveport.com/) instead
of steamcmd. HTC headsets reach the VR stage the honest way every
headset does: through their own browser.

## What is here

- `app.json` — the listing parameters this counter needs; the version
  rides the release train and the guard holds it current.

## The owner's steps, once the developer account clears

1. Register the title in the Viveport developer console.
2. Publish the launcher (see `../steam/README.md`, same command) and
   zip the output.
3. Upload the zip, enter `../listing.md`, set the binary to
   `QrmeStudio.exe`, and submit for review.
