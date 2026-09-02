# Steam: the thin launcher

The Steam build is `native/windows/QrmeStudio` published self-contained
— the same four-screen client the Windows shell already is, pointed at
the live deployment. VR needs no Steam plumbing at all: the stage's
headset road runs in the headset's own browser, and SteamVR users reach
it the same way (README, "The stage").

## What is here

- `app_build.vdf` / `depot_build.vdf` — steamcmd build scripts. The app
  and depot IDs are `<placeholders>` on purpose; they arrive with the
  Steamworks registration and are filled on the owner's machine.

## Building the depot content

```powershell
cd native\windows
dotnet publish -c Release -r win-x64 --self-contained -o ..\..\stores\steam\content
```

`content/` and `output/` are build products and stay untracked.

## The owner's steps, once the Steamworks account clears

1. Complete the [Steamworks](https://partner.steamgames.com/) signup
   (the one-time app fee) and create the app; note the App ID and the
   depot ID it creates.
2. Fill the two `<placeholders>` in the `.vdf` files locally.
3. Publish the content (above), then:
   `steamcmd +login <account> +run_app_build app_build.vdf +quit`
4. Enter `../listing.md` into the store page, upload the screenshots it
   names, set the launch option to `QrmeStudio.exe`, and submit.

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
