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
