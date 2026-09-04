# qrme — release notes

Every release published to <https://github.com/davidsbianchi1984/qrme/releases>, newest first. GitHub keeps these in its own database, not in the repository; this page is the copy that travels with a clone.

**282 releases.**

This is one part of a page GitHub is too long to render whole — see [RELEASE-NOTES.md](RELEASE-NOTES.md) for the rest.

**app-v3.1.5 to app-v0.54.0.**

## app-v3.1.5 — QRME Studios 3.1.5 — the face says what it is and what it does

- Published: 2026-09-04
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v3.1.5>

> Screen 199 was the last one the camera could not reach. Reaching it turned up a defect underneath.
>
> **The ear that could hear and said it could not.** `audio-capture` is the recogniser reporting that *it* could not get audio — not the same fact as the browser being unable to. A handheld that hands its microphone to a call, and a desktop whose recogniser loses the device while `getUserMedia` still opens it, both landed on "No microphone the browser can reach" over a microphone that was there. It joins the three faults beside it on the road to the recorded ear, in all four ears, and stays self-correcting: where the device really is gone, the recording fails at `getUserMedia` and says so.
>
> **One badge, on the picture, hung off its corner.** The talk face, the room seat, the full-screen stage and the card each had their own mark — a band, a 7px tint, a grey pill — so one fact about one kind of profile looked like three. All wear `.ai-pill` now, above everything the picture can do to it, where a round frame used to crop it in half. The name is said once.
>
> **The four panels beside the face are readable.** Their tabs carried full sentences into a 60-pixel column, cut to "Who the… / What th… / What yo… / How the…". Each gets a word — Who, Memory, Us, Manner — in ten languages; the sentence stays as the tooltip and for a screen reader.
>
> **A name is not an introduction.** Profiles carry a `job_title` beside the field: settable by their owner, filled for the thirty-four starters, and taken from the seat's own title when a company hires somebody — "Founder, QRME", "Bookkeeper, Bianchi & Sons Bakery". One `Trade` component draws it on the talk surface, the pool, the circle and the friends list.
>
> 5726 passed, 3 skipped. Every screen reached; 211, 45 and 20 numbered screens audited across the trio, unbroken from 1
>
> ## What's Changed
> * The face says what it is and what it does by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/351
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v3.1.4...app-v3.1.5

## app-v3.1.4 — QRME Studios 3.1.4 — a screenshot is the whole screen

- Published: 2026-09-03
- Commit: `0c7d89b7e949ad5a9e9cde638e93556ca6eaffcf`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v3.1.4>

> A screenshot is the whole screen.
>
> The console is a fixed-height shell whose content column scrolls, so a full-page capture measured one phone height whatever the screen actually held: Home was losing nine hundred pixels including a whole card, and Identity, Connections and Your circle were each losing ten screenfuls. The camera unrolls the column before the shutter, so a capture is the whole screen; screens taller than the glass are also sliced a phone height at a time (163 slices), listed in a gallery section written from what is on disk.
>
> The camera's own profile wears the founder's portrait and bound voice, so a seat, a chat header and the front page show a face rather than initials and the chat carries no missing-voice notice. Forty-five hologram portraits in the older drawings are the starters' own photographs now, matched by the names beside them, and the starter cards are rebuilt from the same set. Screens 194 and 32 are redrawn in the console's design; 209 stands the founder's own rendered frame over the rendering bar; 44 marks the avatar studio rather than the video-company picker. The camera furnishes what it photographs — a shelf of conversations, a company staffed three seats deep, a shop with two offerings. The README gathers the agent, the profile, its connections and its permissions in one place
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v3.1.3...app-v3.1.4

## app-v3.1.3 — QRME Studios 3.1.3 — the AI badge is the outermost layer, and a download is burned

- Published: 2026-09-03
- Commit: `be01812546d0c157919882231af9e83afeb71249`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v3.1.3>

> The AI badge is the outermost layer, and a download is burned.
>
> On screen the badge on rendered footage is drawn by the console over the player and over the full-screen takeover — never in the pixels — and the player's own full-screen and download are switched off, so expanding cannot hide it and the only download offered is the burned copy. GET /media/{id}/download serves synthetic media with the badge burned into the image (Pillow for pictures, ffmpeg for footage); an authentic upload is never stamped; a deployment without ffmpeg refuses footage rather than serving it unmarked. The image ships ffmpeg. The voice, AR and VR rooms and the chat are photographs; the vastscape and moderation are redrawn in the console's design; the starter collection stands in the README as the console draws it; every highlight names its technical problem, its implementation with its own numbers, and its test
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v3.1.2...app-v3.1.3

## app-v3.1.2 — QRME Studios 3.1.2 — the edge dock, and the whole starter pack as friends

- Published: 2026-09-03
- Commit: `b9794b03f75e100e8c7c79182547592bfa77261a`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v3.1.2>

> The edge dock, and the whole starter pack as friends.
>
> The help box and the agent lights are tabs on the right edge of the glass — the lights a stoplight, minimized, opening to the round watch face, whose rows press to name which agent is working, waiting or stopped; the stack moves up or down by its grip and stays where it is left. The footsteps count leaves the console (everyone with an account shows in Discover). Every profile gets the starter collection as standing friends after the founder pins. The onboarding card fits a phone, the avatar stage says "no avatar yet" instead of blowing up the empty frame, seat names wrap. Screens 01, 02, 148, 197, 204 and 205 are captures now, 211 photographs the dock, and the ten mechanisms on file are set out for examination
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v3.1.1...app-v3.1.2

## app-v3.1.1 — QRME Studios 3.1.1 — cut with the siblings

- Published: 2026-09-03
- Commit: `3b3ab47d4912e7ff42d7c61ad1a32d20b36f78d3`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v3.1.1>

> No functional changes to QRME — cut with the siblings.
>
> JIM-mini's image gained what its box runs (pytest, and JIM_SOURCE_DIR naming the tree); the three products keep one number
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v3.1.0...app-v3.1.1

## app-v3.1.0 — QRME Studios 3.1.0 — the assistant's box opens on the hosted cloud

- Published: 2026-09-03
- Commit: `2f7776ab4ee7fecc3b0516163f41b60139b72476`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v3.1.0>

> One number across the three, and the assistant's box opens on the hosted cloud.
>
> **The assistant's box opens on the hosted cloud.** JIM's coding assistant tries a drafted edit inside user, mount, network and pid namespaces, and Docker's defaults refused it: the default seccomp profile denies unshare and mount to a container without CAP_SYS_ADMIN, the default AppArmor profile denies every mount and, on Ubuntu 24.04, the user namespace itself. Two files widen exactly that, for the jim service only: docker/jim-box.seccomp.json, Docker's default profile with unshare, mount, umount2 and the new mount API allowed; docker/jim-box.apparmor, Docker's default profile with mounts allowed and user namespaces permitted. docker/jim-box-install.sh loads the AppArmor half into the host's kernel, idempotently, and the deploy page runs it before every up. A guard holds the profiles to Docker's default plus those calls and nothing more.
>
> **One number across the three.** QRME, JIM-mini and PDI are cut together at 3.1.0.
>
> Suite: 5706 passed, plus the stores guard green after the Steam description fix
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v3.0.6...app-v3.1.0

## app-v3.0.6 — QRME Studios 3.0.6 — the voice door answers

- Published: 2026-09-03
- Commit: `b3894730dff61e33cdf19d5430bfe5a2306a5254`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v3.0.6>

> The voice door answers.
>
> **The line answers (3.0.6).** The sidecar gains two inbound doors per house — the number's voice URL and its status URL — so a contact calling the line back reaches JIM 3.0.10's conversation about their reach-out. The standing read reports both URLs to point the number at and, for a house that can be asked, whether it is pointed there already. The vendor doors run their blocking work off the event loop, the same as the outbound side.
>
> **For examination.** The README carries the components including every sidecar, the ten mechanisms on file, the highlights index, and the console photographed again from the current build.
>
> Suite: 5702 passed
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v3.0.5...app-v3.0.6

## app-v3.0.5 — QRME Studios 3.0.5 — the voice door

- Published: 2026-09-03
- Commit: `5ba5244e008826c385166eacb8ddfee14922ed6f`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v3.0.5>

> ## What's Changed
> * QRME Studios 3.0.5 — the voice door: the phone line JIM rings emergency contacts on by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/350
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v3.0.4...app-v3.0.5

## app-v3.0.4 — QRME Studios 3.0.4 — the inbound wire: mail arrives in a profile's mailbox on its own

- Published: 2026-09-03
- Commit: `27ec3015727272950a6d8675cd9fe057ca12b7e6`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v3.0.4>

> 3.0.3 built the mailbox and said, honestly, that inbound was the wiring step. This is the wire, in two shapes.
>
> **The inbound address.** Every profile has a webhook any mail provider's inbound-parse can post to, opened by a token its owner mints from the corner — shown once, hashed at rest, rotated by minting again — and reading the field names SendGrid, Mailgun, Postmark and a plain JSON post all use, multipart included, with no parsing dependency the image lacks.
>
> **The poll.** The attached Gmail, Outlook or Mail connector is read over IMAP with the credential it was authorized with, sealed in the vault: on a press from the corner, or on the deployment's own poller when QRME_MAIL_POLL_MINUTES is set. Each connector reports what happened to it rather than the poll failing as a whole; offline mode keeps it home.
>
> Either way the message lands as one handed in — the profile drafts in its profession, screens, answers on its own in auto mode, holds for the owner in manual — and the posture says which wire is connected.
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v3.0.3...app-v3.0.4

## app-v3.0.3 — QRME Studios 3.0.3 — a menu per region, the profiles work their own mail, and the corner carries your name

- Published: 2026-09-02
- Commit: `02803048df7767f1af71881cd187d82be87a5497`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v3.0.3>

> **The model menu is a loadout per region.** Where you sign up from is a fact on the account — chosen at sign-up, editable on Settings — and the tiles a profile is offered are the loadout for its owner's region: home providers first, then a curated few popular foreign ones. Twenty-two providers, each naming its home (Anthropic leads as the beta default). A provider off the loadout is refused with the menu. QRME_MODEL_POLICY=american tapers only the American-region menu, in one line. The video shelf is the same shape — Higgsfield, Hailuo and Vidu join it, and the Identity picker draws the region's menu.
>
> **Every synthetic profile has its own mailbox and works it itself.** It reads, drafts in its profession, screens the reply through the same moderation a chat turn passes, and in auto mode answers on its own (sent over SMTP when wired, staged and held when not); manual mode holds the reply for the owner, and a flagged reply is held whatever the mode. Your corner is the review desk over every mailbox your account is answerable for — your profiles and your companies' seats.
>
> **No company emblems**, and *My Space* is *My Corner* — *Dana's corner once a profile is signed in.
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v3.0.2...app-v3.0.3

## app-v3.0.2 — QRME Studios 3.0.2 — the video road is owner-only, and the glyph fills the box

- Published: 2026-09-02
- Commit: `ae2de392c928f0643f0baeafa08083dac7b6cfb5`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v3.0.2>

> Security: the door that puts a profile on the video road, sets its daily spend ceiling, and picks its render provider took no token at all — a profile id off a printed sticker was enough to spend that owner's budget. It is owner-gated now, set and read both. Fix: the purple box stayed black because a profile only films when its owner has put it on the video road, and the room's glyph was viewer-only. Pressing the video glyph on a seat you own now puts that profile on the video road, so its next room turn renders through fal.ai — your own seats only, and a peek restores the road it was on so it never keeps spending.
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v3.0.1...app-v3.0.2

## app-v3.0.1 — QRME Studios 3.0.1 — the room films its turns, and the ladder holds

- Published: 2026-09-02
- Commit: `ad64a1dbc500e84162495427acdd95eeaa0fb049`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v3.0.1>

> Three field reports from one phone, closed on their own evidence. The room's video frame could only ever say "no footage yet" — ordering a render was the chat door's habit and never the room's; an approved room turn now orders footage on the same ceremony, gated by the seat's own road and ceiling. A one-request model outage stopped posting its apology into the rotation as a turn. And the invite panel stopped sliding under the room: the scrim clears the room's takeover, the version guard clears the scrim, so the "two versions are answering" banner can never again be buried by the screen it warns.
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v3.0.0...app-v3.0.1

## app-v3.0.0 — QRME Studios 3.0.0 — every avenue functions properly inside the apps

- Published: 2026-09-02
- Commit: `3abe410c09f7f214065ed38d83553dcddae6c730`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v3.0.0>

> The celebration release the ROADMAP reserved. The gate was a person, not a checklist: pick any road on the map — chat, voice, avatar, video, AR, VR, the watch, a profile acting through its own connections — and drive it to the end without finding a wall. tools/walkthrough.py drives all of them over real doors: thirty steps, zero walls, six photographs of the driven console in docs/walkthrough/. Store distribution ships as a funded follow-up by the owner's recorded decision — the tag waited on the roads, not on a fee.
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v2.9.17...app-v3.0.0

## app-v2.9.17 — QRME 2.9.17 — the connection is real

- Published: 2026-09-02
- Commit: `034b1b3c53321a17baa3ac3ee946838fe0731843`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v2.9.17>

> The connection is real.
>
> Pairing a wearable stops being a typed claim: one press opens the console's own Bluetooth session beside the device, and whatever it advertised for itself lands on the pairing as its voucher — verified and unverified told apart on the same screen, a re-pair taking the old voucher off with the claim it vouched for, and a browser without a radio saying so instead of pretending.
>
> The ROADMAP records the owner's call: store distribution is a funded follow-up, and 3.0.0 does not wait on a fee.
>
> Full suite: 5477 passed, 3 skipped
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v2.9.16...app-v2.9.17

## app-v2.9.16 — QRME 2.9.16 — the wearable tells the guardian

- Published: 2026-09-02
- Commit: `d5254fe244718c12fa723dfd1ef79502fed2a6c4`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v2.9.16>

> The wearable tells the guardian.
>
> Every kind of worn device now declares what it can sense — heart rate, steps, sleep, temperature, respiration, falls, gait — sensing or empty, every kind decides. A sensing device's settings row takes the deposit address the owner's JIM-mini guardian minted, and readings travel from the device's own app straight to that address: this platform stores only where the owner chose to send them, holds no reading at any point, and refuses the setting by name — in ten languages — on a device that senses nothing a guardian could watch.
>
> The gallery is re-photographed current, and the record drops the one section whose images were compositions rather than screenshots.
>
> Full suite: 5470 passed, 3 skipped
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v2.9.15...app-v2.9.16

## app-v2.9.15 — QRME 2.9.15 — the eye, and the scene that knows its professional

- Published: 2026-09-02
- Commit: `130d24ab3dae21ef616b456302363bebbe97cb7c`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v2.9.15>

> The eye, the answered reports, and the scene that knows its professional.
>
> **The AR stage grows eyes** — one pill shares the current passthrough frame into the room through the share door the room already has, read on the way in so the next reply grounds on what the camera actually saw. One press, one frame, on the record — never a stream, and a guard holds it there.
>
> **Three phone reports, fixed at their roots** — the invitation overlay rises above every layer a room draws; the glyph rail stays a vertical road that scrolls instead of wrapping sideways off frame; the film frame wears its paint — wide, black, 16:9 whether footage exists yet or not, keyed on the newest turn so arriving footage shows.
>
> **The scene knows its professional** — before an owner writes a direction, a profile renders with a composed character sheet: the hired seat's trade, dressed as one in that trade's own workplace, who they are from their own persona. The purple box's edit bar attaches any change to that profile's next submission and every one after, chats and rooms alike. And the service shelf says on screen which road every model travels — read from the film adapter's own health.
>
> Full suite: 5462 passed, 3 skipped
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v2.9.14...app-v2.9.15

## app-v2.9.14 — QRME 2.9.14 — the stage holds its shape

- Published: 2026-09-02
- Commit: `787a89ce71695614c8303cc2e7da3d9d590c4a5a`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v2.9.14>

> The stage holds its shape.
>
> **No seat lunges** — a seat whose angle plus yaw neared 180 degrees crossed the CSS camera plane and rendered enormous and half off-screen. Past 112 degrees a seat now fades out with a quarter-second breath: the room stays a circle you look around, never a card that lunges. The ring geometry is untouched, so the flat stage and the headset still agree.
>
> **The hint clears the strip** — the stage's drag/AR note sat inside the band the chat strip owns and the two overlapped on every phone. It now lives in the top band under the two corner pills, the one strip of the stage nothing else occupies.
>
> Full suite: 5456 passed, 3 skipped
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v2.9.13...app-v2.9.14

## app-v2.9.13 — QRME 2.9.13 — the stores room, and the record

- Published: 2026-09-02
- Commit: `13fb6c24536bc8b8f3e166dac108c16d55112f5c`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v2.9.13>

> The stores room, the record the attorneys can stand on, and the name.
>
> **QRME Studios** — the product's name, now one word everywhere it is a name: the browser tab, the web manifest, the icon's own label, the phone-pairing banner, and all three store shelves.
>
> **The stores room** — `stores/` holds the three storefront counters on the road to 3.0.0: Meta Horizon as a packaged PWA over the live console, Steam and Viveport as thin launchers over the Windows shell. One shared listing (description, screenshots, an honest content-rating sheet), per-counter owner steps for when the developer accounts clear, credentials and app IDs deliberately absent from the repo, and a guard holding every shelf's version equal to the app's.
>
> **The record** — the README defines the Company Builder feature by feature and the stage's three renderings of the one room, each stated plainly enough to be checked against the code and found true or false, with photographs of the running console beside the behaviours they show.
>
> Full suite: 5456 passed, 3 skipped
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v2.9.12...app-v2.9.13

## app-v2.9.12 — QRME 2.9.12 — the employee file

- Published: 2026-09-01
- Commit: `258d4674946c995065f37a9aaeea27c0c050a6c6`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v2.9.12>

> The employee file — embodiment and the hand-out, inside the company builder.
>
> **Where they work** — every hired seat opens its file in place: the employee's bodies and screens; the whole American robot shelf inline, grouped by maker with availability told honestly (announced stays un-bindable rather than hidden); one press binds a body through the same embodiment rails as everywhere else; fixed screens placed with a kind and a name; and the nearby-device code opens the studio on anything with a camera on the same Wi-Fi.
>
> **Hand them out** — each employee can be given away as a code to input, a QR code, a link, or a downloadable file. The scan roads ride a single-use, ten-minute handoff ticket; the founder's key never leaves the screen.
>
> Not one new server door: the release is the Companies screen composing rails that already stood, plus tests pinning that a profile minted by an interview is exactly as embodiable and exactly as portable as one minted any other way.
>
> Full suite: 5451 passed, 3 skipped
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v2.9.11...app-v2.9.12

## app-v2.9.11 — QRME 2.9.11: the study, the plan, and bring-your-own

- Published: 2026-09-01
- Commit: `63e8adbed017667028dc1e5108a61de338590224`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v2.9.11>

> Every interview now begins with the platform studying the trade — the occupation's daily work, its skills, the tools, what it escalates and to whom, who it works with, and the profession's working knowledge — through the excursion machinery that already owns the posture: sanitized before it leaves, answered by the local provider while offline, who-answered on the record. The interview is drafted from the study, and on hire the findings file into the employee's source material as "The trade" — the hire arrives knowing its profession.
>
> The staffing plan turns "what this store is meant to be" into a predicted roster for a fully functioning business — title, department, and a why per role, capped at the headcount — suggestions never walls, and never deeds: nothing opens a seat but the founder's own press, with an honest floor when the model's answer does not parse.
>
> And bring-your-own: an open seat lists the founder's held profiles — hybrids built in Blend included — and one press seats them, same-account only, colleagues connected, the record saying brought rather than interviewed.
>
> Full changelog: https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v2.9.10...app-v2.9.11

## app-v2.9.10 — QRME 2.9.10: open for business

- Published: 2026-09-01
- Commit: `c69081677af68775a9f90282c5b72579f24ff462`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v2.9.10>

> A founded, staffed company enters the digital marketplace inside the app with one press. The storefront rides the shop rails that already exist — anchored on the front-desk hire, named for the company, tagged with its industry so Discover files it where people browse — and each staffed department becomes a service offering whose blurb names who answers. A company with nobody hired cannot open for business, and the refusal says so in ten languages. Closing the storefront is a status flip: listings hide it, the company keeps working privately, republishing is the edit it always was, and a stranger's publish answers 404. The round also carries the Companies screen's photograph into the gallery, its door onto the product map, and the founder's lesson into the walkthrough.
>
> Full changelog: https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v2.9.9...app-v2.9.10

## app-v2.9.9 — QRME 2.9.9: the Company Builder

- Published: 2026-09-01
- Commit: `4db9af76723537275210967836a1db8cd227697f`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v2.9.9>

> Found a digital company — a name, any industry in the founder's words, a headcount between 1 and 50, an organization behind it — then open seats for any title on Earth, and hire one interview at a time. The platform writes each role's interview at the founder's own role-mapping questionnaire's caliber, in the role's own vocabulary, with an honest role-blind core when no model is reachable. Signing is hiring: a profile under the founder's account, the charter in the persona and filed into source material, colleagues connected, the seat filled in its department. Licensed and physical duties are assisted, never performed. Oversight is ownership: every employee answers to the owner doors that already exist, organised under the company folder, and a stranger's GET answers 404.
>
> Full changelog: https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v2.9.8...app-v2.9.9

## app-v2.9.8 — QRME 2.9.8: the screens render

- Published: 2026-09-01
- Commit: `3f8efed309dd190b2c53905f9da628d634fc4243`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v2.9.8>

> The stage offers "On your headset" wherever the browser can answer for one, and opens the same room as a WebXR session in the headset's own browser — Quest's, Vision Pro's, no app store and no second codebase. No Steam and no store is required: a PC headset's browser drives SteamVR itself, as plumbing the person never sees.
>
> The figures stand in it. A seat with a body — the same .glb the avatar road opens — stands at its place in the visor, face card up only until the body arrives; pressing a seat on the flat AR stage opens its avatar over the user's own real environment. VR grows five surroundings of your choosing — studio, dusk, forest, shore, the dark — drawn by the product's own scene code; AR keeps the actual room on purpose, and gains film chips that float each seat's rendered video reply over the passthrough.
>
> One ring module, one photo resolver, one model resolver and one palette table keep every rendering the same room, guards hold the headset's source to the stage's no-capture promise, and a band pairs with every face a watch may hold.
>
> Full changelog: https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v2.9.7...app-v2.9.8

## app-v2.9.7 — QRME 2.9.7: every worn thing in America can be added

- Published: 2026-09-01
- Commit: `91bbef6f1c469b845873102b47f5fd58b547471c`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v2.9.7>

> The pairing menu grows from nine kinds to twenty: VR headsets, AR glasses, ankle monitors, chest straps, health patches, hearing aids, headbands, insoles, alert buttons, smart clothing — and audio earrings, asked for by name. Each kind answered its two questions the day it landed: whether it carries a microphone (the head-worn ones do, and land on the mic type whose geometry they share; an alert button's two-way voice stays the emergency service's, not the owner's to lend) and whether it has a screen the console can render on (the watch, the band, and the two eyes-covering kinds — said in the picker before pairing, not discovered after).
>
> A short American-market catalogue per kind — Quest and Vision Pro, Xreal and Viture, Oura and Galaxy Ring, Dexcom and Libre, Polar straps, Limitless pendants, Nova H1 audio earrings — is served by the backend so all four clients offer one list, and reaches the console's name box as suggestions, never requirements: an unlisted device pairs exactly as well.
>
> Also in this cut: Dr. Amara Osei's full-body still joins the portrait families, with the phone photo library's buttons reconstructed off her sneakers.
>
> Full changelog: https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v2.9.6...app-v2.9.7

## app-v2.9.6 — QRME 2.9.6: AR and VR move onto the seat, and the stage gets its screen back

- Published: 2026-09-01
- Commit: `7faed57e5b3d8ba2b670fe13cda74390748beec3`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v2.9.6>

> The "Step in" button under the seats is gone: AR and VR joined the avatar and the film as roads beside each face, straight up and down in the lane the tile already reserves. The new pair are letters in a ring, read from the language table like every other label — a French seat says RA and RV, matching the road's own tooltip. The stage follows the viewer's own chosen format rather than the room's kind, so any room can be stepped into, and stepping out is the same act as pressing a lit road.
>
> Fixed: the gear is back off your seat now that both gestures work on a phone, and the stage was repaired — three rules written against the bare `room-stage` class caught the participant card AND the immersive stage, flattening the stage into the page, pinning its composer across the transcript, and drawing the room's close button over the stage's own. All three now name the card, and the stage stands above the room's chrome.
>
> Full changelog: https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v2.9.5...app-v2.9.6

## app-v2.9.5 — QRME 2.9.5 — the export becomes a face here, and the mouth comes with it

- Published: 2026-09-01
- Commit: `5930170d71f2df6c8a3990c734e6ac0f386e2ebc`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v2.9.5>

> The avatar shelf's first row is the only one that hands over a **model** rather than a picture, and it ended in an instruction:
>
> > an FBX export needs converting to .glb first (Blender: File → Import → FBX, then File → Export → glTF 2.0, leaving Shape Keys checked so the mouth survives)
>
> Every word of that was true, and it was still a shelf row with a manual taped to it. Worse, it could not be followed halfway: `media.save` proves a format from the bytes themselves, an FBX matches nothing it knows, so an FBX upload came back *"unrecognized file"* no matter how willing somebody was.
>
> ### Why Blender, measured rather than assumed
>
> The forge carries it, which costs that image about a gigabyte. It is the tool those instructions already named, so the automatic path cannot produce a different face from the documented one — and the alternative was tested rather than dismissed.
>
> `assimp` is a tenth the size and installs in seconds. Round-tripping a MetaPerson avatar through it:
>
> | | |
> |---|---|
> | morph targets | 114 → **111** — the three missing from `AvatarHead` and `AvatarTeethLower`, the two meshes that move when a face speaks |
> | target names | 114 → **0** — its glTF writer emits no `extras.targetNames` at all |
>
> The names are the fatal half. The console drives the mouth **by name** — `jawOpen`, `CH`, `DD`, `E`, `FF` — so 111 nameless targets is a face no viseme can find its way into. It loads perfectly and it cannot speak.
>
> Verified against a real MetaPerson export and the provider's own `.glb` of the same avatar, rather than a fixture this repo made:
>
> | | reference | from the .fbx | from the .zip |
> |---|---|---|---|
> | meshes | 8 | 8 | 8 |
> | morph targets | 114 | **114** | **114** |
> | named | 114 | **114** | **114** |
> | nodes | 82 | 82 | 82 |
> | skins | 1 | 1 | 1 |
>
> Per-mesh identical too — head 66, eyelashes 29, lower teeth 19.
>
> ### Both shapes, because both are real
>
> A bare `.fbx` for somebody with their own pipeline, and the `.zip` as it downloads, which is what a person actually has after pressing export. Unpacking it by hand was the other instruction nobody should need.
>
> An archive is not a file, so it is opened under rules a file does not need: exactly one `.fbx`, no member whose path escapes the directory, no symlinks, a ceiling on the unpacked size, and nothing written to disk while reading it. The door reads the bytes rather than the name — a name is a claim, and a door is the wrong place to believe one.
>
> ### What survived, said out loud
>
> The screen reports the counts: *"Converted — 114 mouth shapes came through, so this face can speak."* A conversion that dropped the visemes would still return a model, and it would still load. The only place anybody would find out is a face that has quietly stopped being able to speak — which is not a bug report a person can write, because from the outside it looks like the voice broke.
>
> ### Two things the guards caught
>
> `test_nothing_leaves_the_host` refused the new call: it opened a socket without consulting offline mode. The forge is a container on this stack's own network and the model never leaves the host — but that is a property of somebody's deployment, not of this code, and `QRME_FORGE_URL` can name any host at all.
>
> And `host.egress_sites` stood at 12 against 25 real calls, so half the ways out of this package could have gone without a word. Raised to 20.
>
> `/health` opens the FBX importer rather than asking Blender its version, because a Blender with no numpy prints its version happily and throws `ModuleNotFoundError` at the first file — this container shipped exactly that way for one build while this was being written.
>
> Full suite: **5409 passed, 3 skipped**
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v2.9.4...app-v2.9.5

## app-v2.9.4 — QRME 2.9.4 — nobody is called "You", and the seat's two gestures reach a phone

- Published: 2026-09-01
- Commit: `b8a22551af853854ecce53936eff0bbebd8adf0a`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v2.9.4>

> Three reports from one screen, and the third one turned out to be people.
>
> ### The people who were never there
>
> A live room came back holding two interactors with no account, no picture, and the stored name `You` — the word the *surface* uses for the reader's own seat — each drawing a red ON AIR circle for somebody who had never been in the room.
>
> Three faults, any one of which would have done it:
>
> - onboarding called `POST /interactors` with the literal `display_name: "You"`;
> - it called it on **every pass**, with no account to be idempotent on, so each visit minted another person and seated them — `accounts.interactor_for` is careful about exactly this and says so in its docstring, but this was not that door;
> - nothing on the way in refused the word.
>
> Onboarding reuses the person the session already carries, which signing in provides, so for anybody signed in nothing is minted at all. `accounts.a_person_name` is now the single rule both write doors go through: a pronoun in any of the ten shipped languages, or an empty name, stores as `Someone`. Names that merely begin with one — Yousef, Tuomas, Duncan — are untouched.
>
> A startup repair unseats the ones already there and clears the camera state with them. Deliberately narrow, because these rows look like people: no account, **and** that pronoun for a name, **and** never spoke, **and** never put a face up. Anybody who said a word stays exactly where they are, and it unseats rather than deletes.
>
> ### Two gestures that never reached the device they were reported from
>
> Long press and double tap both reveal the seat's controls, and on iOS neither did. `dblclick` is a mouse event and Safari spends the double tap on zoom; the hold died because a long press on a picture raises the copy-and-save callout, which cancels the pointer stream before 550ms. Both doors shut — on a screen whose third door, the gear, a later sweep had set to `display: none`.
>
> The double tap is counted off the pointer stream now, `touch-action` and the callout rules stop the browser taking the press, and the gear is back as the visible twin it was written to be.
>
> That fix had a bug of its own, caught by measuring: a browser that *does* synthesise `dblclick` then had two handlers for one gesture — the count turned the panel on and the synthesised event turned it straight back off. Two taps, no change, which reads exactly like a dead gesture and is the opposite.
>
> Driven on a touch pointer:
>
> | gesture | result |
> |---|---|
> | double tap | controls and upload input appear |
> | tap again | controls gone |
> | long press | controls and upload input appear |
>
> ### The gold plate names a person
>
> A synthetic seat was marked from the profile's own verification record without asking what the seat was drawing — and in a room a profile seat draws its AI portrait. One circle carried both the sparkle saying *this is a rendering* and the gold plate saying *this likeness is checked*, while the human seat beside it went bare.
>
> The mark follows the face the seat is drawing, and a profile seat never carries it. The record is not deleted and the profile page still shows it; it is simply not a claim that seat can make.
>
> ### Guards
>
> No room seat laid out from its middle; `--face-top` stays on the seat it measures; no pronoun in any shipped language becomes a name; the repair leaves anybody who ever spoke where they are.
>
> Full suite: **5391 passed, 3 skipped**
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v2.9.3...app-v2.9.4

## app-v2.9.3 — QRME 2.9.3 — the room opens in audio, and the mark stops drawing twice

- Published: 2026-09-01
- Commit: `5a58c882e1fbd40880db068c5a7f5bff87fb6313`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v2.9.3>

> Every chat starts in voices and photographs, and the seat's two glyphs are the chooser again — they had been hidden on the reasoning that the format was already picked by the time you reached the rail, which stopped being true when the room started opening in audio.
>
> The seats are four across in two rows, filled from the top left, with **Add someone** keeping the last place in line. The composer is no longer clipped beneath them: measured at five phone heights, the type bar sits 47px inside the card and the button row 11px, identically in both formats.
>
> ### The mark that drew twice
>
> Every starter portrait carries the AI mark burned into its own pixels, and the console draws it again on the outermost layer so a circle cannot slice a disclosure in half. That reads as one mark only if the drawn one lands on the burned one — and it did not, in any of the four layouts.
>
> The drawn mark is placed a fixed distance down the tile, which is one distance only if every seat's face starts at the same height. The seats are grid items, a grid stretches every item in a row to the tallest, and the tiles centred their contents inside that: a seat whose field wrapped to two lines had its face ride up. Measured on a phone, four seats in one room, faces at 9px and 16.1px against a mark drawn at a single offset.
>
> The seats pack from the top now, so a face begins at the tile's own padding on every seat. All three offsets were then read off the live page rather than reasoned about — the phone said 17 where the padding is 8, the desktop said 96 and 12 where the face's box is at 92 and 10.
>
> | layout | width | drawn | burned |
> |---|---|---|---|
> | all-seats | 1280 | .5625 / .0350 | .5625 / .0352 |
> | rail | 1280 | .5625 / .0349 | .5625 / .0352 |
> | all-seats | 430 | .5625 / .0350 | .5625 / .0352 |
> | rail | 430 | .5625 / .0349 | .5625 / .0352 |
>
> ### VERIFIED is back on your own circle
>
> A picture you put up used to draw full-bleed, so the marks had no sphere to be fractions of and went to the tile's corner instead. Both layouts draw it as a circle now, so that rule was the only thing still holding the gold plate 1.46 face-heights down the tile, below the name and the glyphs. It lands at .2969 / .8143 against a burn at .2969 / .8145.
>
> ### The badge fits its word on fonts this machine cannot render
>
> The plates were pinned to exactly the burn's width — which fits the burning tool's font and not the reader's. Here there is 37.4px of box for 30.5px of text; in SF the same string is wider and fell out of both rounded ends. The measurement is a floor now, so the badge takes whatever its own text needs and can only ever be bigger than the burn it covers. Proved by widening the run 30%: the plate grows 37.4 → 49.1px with nothing spilling.
>
> Every seat also keeps room for two lines of field, so a wrapping profession and a short one put their glyphs on the same line.
>
> ### Guards
>
> One refuses any rule laying the room's seats out from their middle; one keeps `--face-top` declared on the seat it measures. Neither asserts the offsets — those are measurements, and a test repeating them would only agree with whatever was typed.
>
> Full suite: **5357 passed, 3 skipped**
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v2.9.2...app-v2.9.3

## app-v2.9.2 — QRME 2.9.2 — The button that would not stay pressed

- Published: 2026-08-31
- Commit: `33ccecec15fe7afa4348b40fbfb48cc7a0d69f21`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v2.9.2>

> Pressing **Video generation** on the Identity screen lit the button, showed the options for an instant, and snapped back to *Profile photo*. Reported three times — "it comes in and out too quick and goes away", "shows up for a split second... goes right back to avatars" — and chased twice as a layout fault. It was not one.
>
> `req` in `app/src/api.ts` serialises the body it is given. Three callers handed it a body they had already serialised, so the wire carried the JSON **of a string**; FastAPI parsed it to a `str`, found no fields, and answered 422 every time:
>
> ```
> {"detail":[{"type":"model_attributes_type","loc":["body"],
>   "msg":"Input should be a valid dictionary or object..."}]}
> ```
>
> All three were the video road — setting the road, amending the scene direction, starting a render — so the feature was unreachable from the console **however the deployment was configured**. Which means the adapter and provider picker shipped in 2.9.1 could not have worked either, whatever the box's environment said.
>
> The screen hid it well: `chooseRoad` sets the road optimistically, the POST fails, and the catch re-reads the server and puts the road back. What a person sees is a button that will not stay pressed.
>
> Found by driving the screen and watching the network, not by reading it — the call sites look completely ordinary, and the one that was correct (`sayInProfileVoice`, raw `fetch` with its own headers) looks identical at a glance. A guard now refuses any `req` caller that stringifies its own body, and pins the rule it depends on so the premise cannot invert unnoticed.
>
> Proven the way it was caught. Before: four reverts to *Profile photo*, no panel. After: `HTTP 200`, `set: true`, the panel at 1739px, heading present at 150ms, 600ms, 1.5s and 4s.
>
> ### Also fixed
>
> - **The road's panel opens where it was pressed.** The two panels share one drawer with its own ground and a notch pointing at the button row, and choosing a road scrolls it into view. That was the other half of "it goes away" — and on its own it fixed nothing, which is what the test above established.
> - **The room gives its empty bands back to the seats on a phone.** Measured: an 860px card where the seats had 194 of it. The transcript reserve came down from five rows to three (fixed on purpose, so the buttons below do not travel as the conversation grows), the frame 263 → 200, the strip 52 → 32, and a 62px reservation for a chat strip that no longer hovers was released. Seats now 336px — two full rows with the third in sight. `aspect-ratio: 4/3` was setting the frame's height, not `min-height`, so the first cap never bit.
> - **The photograph behind the VERIFIED badge is a plain photograph again** — no burn, no filter, no synthetic backdrop. Every version in history was checked and all carried the gold plate, so it was replaced rather than recovered.
> - **The ears refuse in a person's words** — dictation and playback are separate doors and only one was shut. `QRME_EARS_URL` moved to an `X-QRME-Fix` header, where an operator fact belongs.
> - **`_restore_face`** puts a shipped portrait back on a starter wearing a face this deployment minted, on registry evidence only, at startup rather than behind a button.
>
> 5355 passed, 3 skipped
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v2.9.1...app-v2.9.2

## app-v2.9.1 — QRME 2.9.1 — The camera gets an adapter, and the company is a choice

- Published: 2026-08-31
- Commit: `b721940f47b9c8bcbfc3bb0c6f7ade75b09bb8c1`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v2.9.1>

> Video was selected on a profile and nothing rendered, whatever service was picked. Two faults, one on top of the other.
>
> **The picker had no handler.** `onPick={() => undefined}` — it drew all the providers, lit whichever one the deployment's environment named, and dropped every click. Choosing Seedance and choosing nothing were the same act. There was no per-profile provider anywhere either: `filming.render` read the environment variable in five separate places, so a choice could not have been honoured even if one had been stored. `presence_road` now carries a `provider` column, nullable because NULL is a real answer meaning "whatever the deployment named".
>
> **Underneath it, `QRME_FILM_URL` had nothing to point at.** `filming.py` speaks one submit-and-poll shape and said from the day it was written that it is "one adapter away from any vendor whose own API differs" — and the adapter was never built. `docker/film` is it, the third sidecar on the pattern the ears and the forge already follow. The credential lives on the adapter; the product holds the address of a door, never a video house's key.
>
> **Five more houses, and a house pick.** Pika and Moonvalley join Veo, Runway and Luma — Marey trains only on licensed footage — beside Seedance, Happy Horse, Kling and LTX. Veo is the default: strongest on a plain prompt, generates its own audio, and Google will still be answering that endpoint next year, which is not a small thing on a shelf that has already lost Sora and Ready Player Me inside fifteen months. `provider()` used to answer `none` when unset, so one wrong letter in a deploy script silently ended video for a whole box; it falls back to the house pick now and the typo stays visible.
>
> Nano Banana is recorded in `NOT_OFFERED` beside Sora with the reason: it is Google's image model and there is no video in it.
>
> ### Also fixed
>
> - **The room's frames stopped overflowing on a phone.** Measured, not eyeballed: the card is a fixed 860px flex column that *hides* its overflow, and the seats rail took `flex: 1 1 auto` and ate 502 of it — so the framing chips and the lower half of the control rail fell outside a box with nowhere to scroll.
> - **The expand button came out from behind the pencil.** Both pinned to the same right edge, one of them growing upward into the other. A ceiling at 44px.
> - **Seats above the figure, and smaller.** The frame carried `order: -1`; the seats are ordered forward instead, and the boxes come down from 172px to 128 with the face at 84.
> - **The two marks are computed from one number.** The geometry was typed three times over and had already drifted — the rail set a 112px face against marks solving for 104. Measuring afterwards showed the AI plate landing three pixels left of the burn on every seat; corrected from the live boxes.
> - **Joining a standing room raised instead of answering** — `NameError` on `room_id` in the join branch, the path that endpoint takes most.
>
> 5340 passed, 3 skipped
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v2.9.0...app-v2.9.1

## app-v2.9.0 — QRME 2.9.0 — the room holds the second key

- Published: 2026-08-31
- Commit: `db5bf301441ab5591af5e3e30a17b9b6a7f3d01c`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v2.9.0>

> The room's permission window, and the marks that came off the photographs.
>
> ## The room holds the second key
>
> A profile's owner decides what that profile can ever do. That was the only
> key this product had, and it is not enough — a profile in a room is very
> often somebody else's. The owner's grant says *this profile may drive a
> browser*; it does not say *for you, now, in here*.
>
> So the room holds a second key, and nothing opens unless both are turned.
> Either can be withdrawn alone, and a reach reads both sides every time.
>
> The record card became that window: every synthetic seat listed with an
> Add friend button, a bar reading skills *n* of 180 and connections *n* of
> 103, and one seat opening at a time over all nine providers, all 103
> connectors and each connector's own skills. A row its owner has not
> connected is shown and cannot be ticked.
>
> ## The marks are labels now, not burned pixels
>
> `AI` and `VERIFIED` were painted into the images. Every surface here draws
> a face as a circle, and a mark in the corner of a square is exactly what a
> circle crops — so both shipped sliced through the middle. They are drawn
> on the sphere now, in the same corners, half on the photograph and half
> off its edge.
>
> **The cost, stated rather than discovered:** a portrait fetched straight
> from `/portraits/{handle}.webp` no longer carries the disclosure in its
> bytes. `docs/media-provenance.md` carries the rule and the cost.
>
> ## What the guards caught
>
> Twenty-nine failures across two rounds, every one this branch's own. Six
> were real defects, including a door counted on three phones that none of
> them has, the per-turn play button that is the fallback when a browser
> refuses autoplay, and a care-team reader that had been looping over an
> empty list since a wire rename.
>
> Full suite: 5300 passed, 3 skipped.
>
> ## What's Changed
> * The three roads out, and the video one renders every reply by itself by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/349
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v2.8.0...app-v2.9.0

## app-v2.8.0 — QRME 2.8.0 — The capability register, and the rail opens whole windows

- Published: 2026-08-30
- Commit: `f9245b67e7ba9adc7d7a79354727b5ebf2b83655`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v2.8.0>

> Nine faculties on one page, in this product's own words — Channel 3, Channel 2, the voiceprint, the avatar, self-steering — each beside its live state, the permission it rests on, and the screen that withdraws it.
>
> **The talk rail's four buttons open a whole window again.** Measured on a sideways handheld (932×430) the panel drew 258px of 430 — 60vh to the pixel — because its short-screen override sat between two copies of the rule it was overriding, and a media query adds no specificity. After: 406px docked, 390px in the overlay.
>
> Seven more dead declarations were found by the guard written for that one.
>
> Full suite: 5193 passed, 3 skipped.
>
> ## What's Changed
> * The capability register: nine faculties, on one page, beside their permissions by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/348
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v2.7.1...app-v2.8.0

## app-v2.7.1 — QRME 2.7.1 — the camera works, and the light is a circle

- Published: 2026-08-30
- Commit: `f8b8c589755057a316a9c05dddf1cbeefaa076a8`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v2.7.1>

> **The screenshot harness had been raising `NameError` on every invocation**
> since the round that taught it to reload before looking for a signed-in screen.
> The reload was carried across from a sibling with the sibling's name for the
> console address still in it, and this product serves its console at the root
> where the other two serve theirs at `/app/`. Nothing said so until somebody ran
> it. This gallery is the first shot here since.
>
> **And it builds first.** The build was a requirement written in prose and never
> checked, so a gallery could be re-shot to show a fix and photograph a bundle
> from days earlier, looking exactly as convincing as one that showed it.
>
> **The minimized light is a circle again.** It rendered 22 wide and 44 tall — an
> ellipse. It is a `<button>`, and the phone block sets `button { min-height:
> 44px }` so every control is a real tap target; `min-height` beats `height`, and
> the guard read the declared 22 and 22 and passed. The button is the tap target
> now and carries no paint; a face inside it is the circle.
>
> **Every numeric floor in the suite is registered and audited.** Seven rows left
> the backlog; three were decoration, including one standing at a fifth of what it
> measured.
>
> A patch: no wire changes, no schema changes, nothing a client must be rebuilt
> against. Tested together with JIM-mini 2.7.1 and PDI 2.7.1.
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v2.7.0...app-v2.7.1

## app-v2.7.0 — QRME 2.7.0 — a body is a surface

- Published: 2026-08-29
- Commit: `c1dc93285ace96d69e564e69ffde3d9e85ae1be1`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v2.7.0>

> **A body is a surface, and moving one is refused with its reasons.**
> `qrme/robotics.py` has carried a catalogue of bodies for several releases and
> none of it was ever attached to a grant, a reach, a ledger or a refusal.
>
> `body` now joins the hands' surfaces — because a surface a product silently
> does not support is indistinguishable from one it forgot. Watching through one
> is allowed, since seeing and saying what is there carries none of the risk.
> Acting on one is refused, and the refusal names all four bounds a screen never
> needed: where the body may be (which is not a list of app names), a ceiling on
> force and speed (which a step budget does not give), a stop within reach of the
> person standing next to it, and a landing reported by a sensor rather than by
> the thing that was asked to move.
>
> A person told "not supported" learns nothing; a person told what is missing can
> decide whether to supply it.
>
> **Changed — the trio is back on one number.** Each product's README promises
> that one version names one tested combination of all three, and three hands
> rounds here alone drifted that apart. All three are cut at 2.7.0.
>
> Since the cut, the front-page gallery is **real photographs of the running
> console** rather than drawings, shot against a real backend, a real build and a
> real enrolment.
>
> Tested together with JIM-mini 2.7.0 and PDI 2.7.0.
>
> ## What's Changed
> * A body is a surface, and the cut is 2.7.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/347
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v2.5.0...app-v2.7.0

## app-v2.5.0 — QRME 2.5.0 — the photograph speaks

- Published: 2026-08-29
- Commit: `be45d0dc2405f3ebd249b42d95a661b3ee9fd4a2`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v2.5.0>

> The photograph is what speaks.
>
> The forge built a head out of MediaPipe's 478 face landmarks — and a landmark set is a face region: no skull, no hair, no ears, no neck. However well it is textured and lit, that mesh can only ever be a mask. So nothing is rebuilt any more. A new /speak door measures the picture — where the face's points sit, how they join up, how a mouth moves in the picture's own plane — and the console lays that mesh flat over the photograph it already has, with the picture as its own texture at the places it was measured. At rest the mesh is a copy of the picture over the picture and cannot be seen. The only thing that ever moves is a mouth.
>
> Also fixed in this cut: the head's texture was embedded as a JPEG under a declared image/png, and the lighting multiplied the skin past white. The 3-D head stays, second on its card and behind a fold that says what it is.
>
> Full changelog: https://github.com/davidsbianchi1984/qrme/blob/app-v2.5.0/CHANGELOG.md
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v2.4.0...app-v2.5.0

## app-v2.4.0 — QRME 2.4.0 — the hands

- Published: 2026-08-29
- Commit: `80e732c407847e6ee08b1565f2c0de6535dac42b`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v2.4.0>

> The hands: a profile can work a screen under a grant that names its apps, its moves, its minutes and its steps — given from a menu or simply said out loud. It will not type a password, cannot widen itself from anything written on a screen, and says plainly that no iPhone can be driven by anything.
>
> Also in this cut, from the field round: the Wall crash that blanked the whole console; a boundary so a crash costs one card instead of the session; a capture harness that had photographed the same screen thirty-nine times; a transcriber stutter posted into rooms as somebody's own words; and the microphone that would open over a voice already speaking.
>
> Full changelog: https://github.com/davidsbianchi1984/qrme/blob/app-v2.4.0/CHANGELOG.md
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v2.3.1...app-v2.4.0

## app-v2.3.1 — QRME 2.3.1 — the head is actually drawn, and the forge works

- Published: 2026-08-28
- Commit: `5b4f0ce5351816faf59775cd3589ebd3c754056d`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v2.3.1>

> ## 2.3.1 — 2026-08-28
>
> ### Fixed
>
> - **The head the forge builds is actually drawn.** Avatar3D shipped in 2.3.0 written, catalogued in the census and given a door on the product map — and imported by nothing. It now stands on the avatar stage and in a room seat's second circle, its jaw moving with the voice already in the air.
> - **The avatar market is a picker again.** SkinTiles, written to replace the dropdown its own note calls "a form, not a picker", was mounted by nothing either.
> - **The forge could not build anything, and said it was ready.** Two bugs: MediaPipe 1.0 removed the legacy Solutions API the topology lookup used (the triangulation is computed from the landmarks now), and the container lacked libEGL.so.1, which MediaPipe loads lazily — so the module imported cleanly and died on first use. /health now builds a landmarker and runs it, so a broken forge says so at startup.
> - A guard: a component in app/src that nothing imports fails the suite.
>
> Tandem release with JIM-mini 2.3.1 and PDI 2.3.1.
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v2.3.0...app-v2.3.1

## app-v2.3.0 — QRME 2.3.0 — the forge, the sit-out, and two rooms repaired

- Published: 2026-08-28
- Commit: `4e45abfd0d727fe3a1cb5ce35cb6a8d88922e3ef`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v2.3.0>

> ## 2.3.0 — 2026-08-28
>
> ### Added
>
> - **The forge — a face built here, not bought**. The avatar shelf was an import list and said so; the road chosen to fix it (Ready Player Me) was bought by Netflix and shut down on 31 January 2026, and the two production replacements price their API at eight hundred dollars a month. So the road that MAKES a face runs on the deployment's own hardware: a MediaPipe sidecar turns one photograph — framed as the face, the upper torso, or the full body — into a textured 3-D head whose morph targets carry ARKit's own names. No vendor, no monthly bill.
> - **The face speaks** — the renderer drives jawOpen from the audio the room already plays, looking morph targets up BY NAME, so a bought avatar animates through the same code.
> - **The sit-out** — a person's seat steps out of the room's waiting so the profiles keep their own rotation, and steps back in on a tap.
>
> ### Fixed
>
> - Ready Player Me struck from the shelf with its reason recorded; no client opens its picker on a dead row.
> - An aimed turn is answered even when the marker sits mid-paragraph and even when the model mistypes the name.
> - The room's ear re-opens the moment it falls quiet — a turn arriving mid-playback no longer stays silent until the next message.
> - A glTF binary is stored under its own name, proved by the format's magic bytes.
>
> Tandem release with JIM-mini 2.3.0 and PDI 2.3.0.
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v2.1.0...app-v2.3.0

## app-v2.1.0 — QRME 2.1.0 — Raise: grow your own

- Published: 2026-08-28
- Commit: `2a4925244d4e445524340fd05fb04d00a6216c4b`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v2.1.0>

> The fourth profile kind: a raised character started from a temperament seed and a chosen life stage, taught word by word. Stage doors are earned through milestones, never aged into; the whole life lives in an append-only Album; the four preset doors are only switch bundles; mortality says its warning every time it turns on; and the law holds — a character raised from a childhood is family forever.
>
> Tandem release with jim-mini 2.1.0 and pdi 2.1.0
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v2.0.0...app-v2.1.0

## app-v2.0.0 — QRME 2.0.0 — the avatar takes the screen

- Published: 2026-08-28
- Commit: `22ad1392d5fa6e0898f39a1a67067fb0747e5d02`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v2.0.0>

> The avatar takes the screen, and every headset has a road in.
>
> - A second ring beside every portrait — room seats, your own seat, the chat header — opens the avatar full-screen with a rail of hidden windows: prompt, wardrobe, physique & gender. Every window rides the one painting door: house style, the profile's own age, the AI mark burned in.
> - Guests may restyle the profile they're talking with — on by default, the owner's switch closes the wardrobe, and a real person's face is never painted from words.
> - The avatar deck opens on the deployment's default faces: one tap to wear, claimed through the registry so takedowns reach every wearer. A new pull door tries the provider's catalog under the deployment key and answers honestly while that API stays closed; imports carry the provider's own asset id into provenance.
> - The Rooms screen's XR shelf covers Steam, Meta Quest, Apple Vision Pro, PICO, HTC Vive, Android XR and the phone — each with the browser road that works today, and sign-in/native-app futures said as futures.
> - Screen 205 joins the gallery with its walkthrough lesson; ten record-keeping guards keep every new door in the books.
>
> See CHANGELOG.md for the full record
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v1.9.0...app-v2.0.0

## app-v1.9.0 — 1.9.0 — The room hears an iPhone

- Published: 2026-08-28
- Commit: `47ca7b79e3d68b9fd75efe2149df14e3f4ed8188`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v1.9.0>

> The room stops sitting deaf on iPhones: Safari's second refusal mask forks to the recorded ear, the hear-loop primes to the present, the voice queue wears a watchdog, and a blocked voice says so on screen instead of dying silently. Seats grow a visible settings gear beside the double-tap, a background-only seat stops painting its circle, and the dock mints owner tokens for every held profile so all four panels stand. The wire-collision ledger closes its whole twenty-one-row backlog across the backend and all four clients, two floors join the live-measured registry, and the front page leads with the three postures. docs/raise.md publishes the Raise disclosure.
>
> Released in tandem with JIM-mini 1.9.0 and PDI 1.9.0
>
> ## What's Changed
> * Carry the voice waiver to the three native shells by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/346
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v1.8.9...app-v1.9.0

## app-v1.8.9 — app v1.8.9 — One face ledger, three roads in

- Published: 2026-08-27
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v1.8.9>

> One face ledger, three roads in.
>
> - The avatar registry: every face a ledger row — source, provider, prompt and params kept for reproducibility, rights required, status, checksum — and no surface ever calls a provider, so a swap, a re-generation or a takedown is a data operation. Retire clears a face from every profile at once; disputed refuses new claims.
> - The deployment's shelf, stocked from the owner's ElevenLabs exports and never empty (the starters back it); personal shelves on account tokens; named faces — yours says "David Bianchi", not a source word. The import market grows to the model-keys format: Roblox, VRoid Hub, Avaturn, DiceBear, Gravatar and HeyGen join ElevenLabs, Ready Player Me, Bitmoji, Memoji, Meta, Xbox, ZEPETO and Mii, each with honest export instructions.
> - Painted from words: the house style, the profile's own brief, at its age today — the aging the persona always had, finally reaching the face. A synthetic face gets the AI mark burned in at mint; an authentic photograph never does; a real person's face is never painted from words.
> - The room strip slims — the microphone lend and "Let it talk first" move into the room's settings card. The invite that "never showed up a new frame" now stands as a dimmed waiting seat until its owner says yes. The four-panels dock compacts so all four fit every phone.
>
> Full detail in [CHANGELOG.md](https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md)
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v1.8.8...app-v1.8.9

## app-v1.8.8 — app v1.8.8 — The estate answers for itself

- Published: 2026-08-27
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v1.8.8>

> The estate answers for itself.
>
> - Ask a profile to change how it comes across — any of it, not just humor — and it turns its own dials: +25, -25, max, none, or `all`, with nine new dials on the catalog (empathy, encouragement, patience, storytelling, technicality, spontaneity, sarcasm, emoji, and adult-only profanity, clamped like intimacy). The guidance teaches every dial by both of its ends.
> - The four panels have their exits: tap anywhere outside to minimise, or the little red close at the top.
> - The paperclip is the phone's own chooser — photo, camera, file, in place — and the carried-things card opens only from its own menu row, with its own red close. "Show it something" is Camera; "Document" is File.
> - The room walks with you: the person-walking button hands the room to the walk-along strip — every seat's reply named and spoken in its own bound voice, announced through the room's echo door.
> - The people in your phone reach all three native shells — iOS reads the device's contacts, Android too, Windows takes typed rows; grant first, sync replaces, names stay, numbers never come back out, withdrawal drops the book.
> - The README shows the screens you'll meet: twenty-eight, grouped by journey, each with what it does.
>
> Full detail in [CHANGELOG.md](https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md)
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v1.8.7...app-v1.8.8

## app-v1.8.7 — app v1.8.7 — The room grows hands, eyes and a memory

- Published: 2026-08-26
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v1.8.7>

> The room grows hands, eyes and a memory — and the circle is only yours.
>
> - A link pasted into a room is fetched once and read to every seat; a page that cannot be read enters as an honest absence, never a guess.
> - A room profile hands documents over as real files — and as multi-page PDFs when asked, from a built-in writer proven by our own PDF reader. A stuttered fence files the furthest draft.
> - Your own profile remembers you in a room: briefcase and recalled moments walk in when the room's one human is the other half of the pair. A second human keeps all pair memory out.
> - The profile turns its own dials when asked — +25, -25, max, none, or `all` — through the same store the sliders write; the owner's steering lock is the veto.
> - The four panels (who they are, what they hold, what you are to each other, how they behave) dock in every chat and room, under the loudness rail.
> - "See all" opens Your circle: friends only, in the descriptive card style. Discover's card of somebody already added says Friends.
> - The Windows 👤+ panel fixed, your own profile seats on the press, rooms open with a live green mic, the lend button says which way it points, the rail sleeps until touched, multi-file share says what it is reading, and the README shows the screens you'll meet.
>
> Full detail in [CHANGELOG.md](https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md)
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v1.8.6...app-v1.8.7

## app-v1.8.6 — QRME 1.8.6

- Published: 2026-08-26
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v1.8.6>

> ### Added
> - **The deployment has eyes.** Scanned PDFs and files whose fonts hide their character maps are read now — an OCR pass reads the pages the way a person would when the text reader comes back empty, gated by the same is-this-language check as everything else.
> - **The people in your phone.** The estate's address book reaches QRME: synced from your device under a grant only you hold, names kept and numbers never returned, sealed into the vault where your plan has one, and withdrawing the grant drops the book. The card lives on the Identity screen.
> - **The voice follows what is already connected**, and the loudness rail rides every screen — floated above the talk face and the room, so you can dial down mid-sentence.
>
> ### Fixed
> - **The talk face converses at speed.** The send fires the moment your finished sentence comes back (about four seconds sooner), replies no longer stutter in an earbud, the first sentence waits out the earbud's switch back to music mode, and the roll of the conversation scrolls — thirty turns, pinned to the newest line.
> - **Rooms listen the moment you step in — every room, no buttons.** The text bar stays for those who type; the mic button is the mute. Barge-in works mid-reply on iPhone, the composer's mic records, your seat wears your photo, the ✕ home is always on screen, the chat scrolls, typing doesn't zoom, one paperclip, and the strip says "Let it talk first" in words.
> - **The invite panel offers your own profiles** above your friends, and the list fills the screen before it scrolls.
>
> ### For JIM holders
> - The coach→JIM ladder now winds itself on the day's own traffic, and the synced address book has doors — see JIM-mini 1.8.6.
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v1.8.5...app-v1.8.6

## app-v1.8.5 — QRME 1.8.5

- Published: 2026-08-26
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v1.8.5>

> ### Added
> - **A voice its owner released is everybody's.** Owner-only release control on the Spoken voice card: while the release stands, any account can bind that voice. Reclaiming is personal and takes every other account's binding with it. The watermark is untouched, on every utterance.
> - **Premade library voices are unclaimable.** The claim stops where nobody's throat begins.
> - **Full blast by default, with a dial-down rail.** Spoken audio plays at the loudest a page may play; a fixed vertical slider on the Voice screen's right edge attenuates, remembered per device.
> - **The talk face holds a conversation.** Four and a half seconds of silence sends the turn on its own — no more hunting for Send mid-sentence. While the profile speaks the caption says *speaking* (the ear stays open the whole time, so interrupting still works). And the roll of the back-and-forth sits on the surface, pinned to its newest line, fading out a few lines up.
>
> ### Fixed
> - An iPhone refusing its own recogniser now falls back to the recorded ear on Chat and Agent, as it already did in rooms.
> - Voiceprint enrollment sends its credential — "This is my own voice" works while signed in.
> - The room's talk toggle is a mic glyph, lit and dim — not a slashed speaker.
> - The frame shows its owner's picture (or a silhouette, never a letter), and double-tap or long-press clears the controls off the frame in every state.
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v1.8.4...app-v1.8.5

## app-v1.8.4 — app-v1.8.4 — the field afternoon

- Published: 2026-08-25
- Commit: `0562c19ff0bf5c9ac733322a3c3c1d289c7a1b94`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v1.8.4>

> The field afternoon: three devices, silent no more.
>
> - Audio is on by default, with the mute remembered per browser.
> - The playback unlock arms on the gestures WebKit actually counts and retries until granted -- the iPhone speaks.
> - When the browser's recogniser has no speech service, the deployment's ears transcribe the recorded turn (talk overlay, recording bar, studio orb).
> - A refused bound voice no longer silences a room: the device's voice stands in, and the refusal sentence is shown on screen.
> - Dictation draws a voice-memo bar instead of summoning the keyboard; Send is a round arrow.
> - Live microphones are red, muted green; the split-wording ledger closed.
> - The portrait sits beside the chat title, the talk face is small so the panels get the room, and the voice door is the studio microphone.
>
> Full suite: 4809 passed. Cut together with jim-mini app-v1.8.4; pdi stays at 1.8.3 (no changes)
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v1.8.3...app-v1.8.4

## app-v1.8.3 — QRME 1.8.3 — the platform refuses in the reader's language

- Published: 2026-08-25
- Commit: `ef135f3f032b15bed241c5eb967ca6123041a96d`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v1.8.3>

> The 143 recorded refusals plus 28 the widened sweep surfaced become registered templates: six generic families, ~94 bespoke sentences, seven frames shared with JIM so the tandem refuses in one voice. i18n.raised counts as stringifying now; seven status slots ride i18n.Term; the fill-sites floor rises 24 -> 152. Suite: 4809 passed.
>
> Ships in tandem with JIM-mini 1.8.3 and PDI 1.8.3
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v1.8.2...app-v1.8.3

## app-v1.8.2 — app-v1.8.2 — The last answer does not depend on anything that can fail

- Published: 2026-08-25
- Commit: `8a46f1e96aaeb4f2250606a0e9e4c030b8a8feb6`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v1.8.2>

> The last answer does not depend on anything that can fail: the catch-all that turns a crashed route into an answer the console can read no longer builds its 500 through a translator that can itself fail. When it did, the answer left without the CORS header and a crash read as an unreachable backend. Fixed and guarded in all three products, with a constant English fallback. Alongside it, the night audit of the guards' guards: floor registries measuring every floor against what it stands over, unlabelled-field records verified as decisions and guarded, and the three-suite divergence record read to zero unread rows. See CHANGELOG.md for the full account
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v1.8.1...app-v1.8.2

## app-v1.8.1 — QRME 1.8.1 — every refusal in the reader's language, and the profile's own voice

- Published: 2026-08-24
- Commit: `b61e71633890e41ac6b3a53e13cef8b80a955019`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v1.8.1>

> ### Every refusal reaches the reader in their own language
>
> The last 82 English sentences in `_REFUSALS`, translated into all nine. That backlog is closed: **165 → 142 → 82 → 0** across four rounds.
>
>     asked     did the caller state a language
>     mattered  did the sentence we told them no in
>
> What was left was the whole middle of the product — consent and likeness, the card and image import family, the validation a wrong keystroke raises, and the organization rules. An owner on a Portuguese account met the model in Portuguese, the sidebar in Portuguese, and then a 409 in English at the one moment they were being refused.
>
> ### An exemption that did not survive being reread
>
> One sentence stayed English by decision for four releases — the 503 from `require_reviewer` when a deployment is reachable beyond localhost with no admin token. The recorded argument was that only an operator can act on it.
>
>     asked     who can act on this sentence
>     mattered  who receives it
>
> The operator is who can act. The receiver is whoever made the request, and that branch fires precisely when the caller is *not* local. The variable name survives translation verbatim, so the exemption cost a reader their language and bought the operator nothing.
>
> ### The voice the profile was given
>
> Reported from a Windows machine against the web strip: *the voice is robotic again, it should be my voice when I'm talking to my AI*. The strip was fixed and the Android shell was never asked. It had it — `TextToSpeech`, the generic phone voice, for a profile whose whole identity includes how it sounds — while `ApiClient.saySpoken` sat in the same package returning watermarked audio in the bound voice, uncalled.
>
> Both kinds go through the bound voice now. The audio is deleted when the utterance ends rather than cached, because a watermarked recording in somebody's enrolled voice is not a thing to leave on a disk.
>
> ### Guards
>
> - `test_a_translation_in_the_wrong_script.py` — the backlog counted only *missing* translations, so it could reach zero with `как` inside a Chinese string. Both real instances were caught by eye, not by anything.
> - `test_a_claim_about_a_platform.py` — holds the console to what it actually tested about a minimised window.
> - Two on the voice, both watched failing on an injected regression before being kept.
>
> One of mine, fixed the same round: a comment stripper that treated `/*` **inside a string literal** as a comment.
>
> Suites: **4543 passed, 3 skipped.**
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v1.8.0...app-v1.8.1

## app-v1.8.0 — QRME v1.8.0 — Every profile knows the application it lives in

- Published: 2026-08-24
- Commit: `654083bc1deb083bf87c7bfd93263a337cf77545`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v1.8.0>

> A synthetic profile knew everything about the person it represents and nothing about the place it stands in. Asked where to change what it is allowed to do, a mechanic answered like a mechanic who had never seen the app. The agent had the same gap: told its eleven tools and nothing else.
>
> All sixty-eight screens now ride the prompt builder rather than the routes, so a profile created a second from now stands in the same building. Naming a door is not permission to open one — the delegation policy still decides — and a mechanic who can point at the Permissions tab is still a mechanic.
>
> And a conversation you can take with you, on both surfaces: surviving a minimised browser window, and leaving the application entirely on Android and iOS. The notification carries the profile's AI designation, because a notification glanced at from inside another app is where somebody has the least context and the last place to leave *is this a person* to a guess.
>
> Suite: 4532 passed, 3 skipped.
>
> Not compiled: the Kotlin and Swift have never been built — no toolchain was available
>
> ## What's Changed
> * Every profile knows the application it lives in, and the conversation can leave it by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/345
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v1.7.0...app-v1.8.0

## app-v1.7.0 — QRME 1.7.0

- Published: 2026-08-24
- Commit: `d6f784fd97d1dac54df199844ee954976a3d8b16`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v1.7.0>

> ## The chat ear closed after one sentence
>
> Pressing *speak* listened for about a second and dropped back to *tap to talk*. `SpeechRecognition.continuous` defaults to **false** — the engine stops itself the moment it decides one utterance has ended — and nothing reopened it.
>
>     asked     did the microphone open
>     mattered  is it still open when the person is still talking
>
> The ear runs continuous with interim results now, accumulates finalised phrases instead of replacing the box on every event, and reopens itself in `onend` while the listener is still wanted. Chrome ends a session on its own silence timeout even with `continuous` set, so the reopen is what actually keeps it listening. The talk overlay gained the composer's share menu; the avatar box under the composer is gone.
>
> ## German finishes the informal register
>
> **380 rows** across the console and the three native shells. What stays counted is third-person `Sie`/`Ihr` — `Sie haengt am Brett` is the question, `Sie ist passwortgeschuetzt` is the briefcase — each named in the ledger.
>
> Also: `chat.talk.stop` and `chat.talk.again` were read through `tr(cond ? "a" : "b", lang)`. The guard that finds translated keys nobody uses reported both, and it was right: a static reader cannot follow a key assembled at runtime.
>
> ## Two guards that were measuring the wrong thing
>
> The refusal backlog counted two constructor preconditions raised while the app is wired — sentences no reader can reach. Its ratchet also had **82 rows of slack**: ceiling 164 against 82 recorded rows, never brought down as rows were struck. And `len(_REFUSALS) >= 9` was a floor against a table of **335** — it would have passed with 97% of the table deleted.
>
> Full suite green: 4465 passed, 3 skipped
>
> ## What's Changed
> * Informal register, the chat ear, and two refusal guards that were measuring the wrong thing by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/344
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v1.6.2...app-v1.7.0

## app-v1.6.2 — QRME app-v1.6.2

- Published: 2026-08-24
- Commit: `88d659a02f51779ce2be50580834979231b9099a`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v1.6.2>

> ## Discover showed 3 profiles on a deployment holding 38
>
> The screen rendered `GET /marketplace` — the opt-**in** listing a profile enters only when somebody explicitly lists it. Nobody's privacy setting was involved: the other 35 had simply never been listed into a table this screen should not have been reading.
>
>     asked     is this profile listed
>     mattered  does this profile exist here
>
> `GET /people/browse` is the pool, and it already carried the rule the product means — every active, non-anonymous profile, with the owner's private switch (`profiles.unlisted`, default `0`) as the door out. Its docstring has said so all along: *listing is the default and privacy is the door out*. **Friends read that pool; Discover did not**, and nothing checked that two surfaces onto the same deployment agreed about who was on it. A beta cohort could not find each other.
>
> Discover reads the pool now and merges the marketplace over it, so a listing makes a card richer rather than deciding whether the card exists. The Marketplace screen still reads the marketplace — opt-in is right for a storefront; it was only ever wrong here.
>
> Three things came with it. Pool rows carry `avatar_kind`, because the AI badge is not optional and a card built from a pool row could not draw one — and the rule now lives once, in `avatars.kind_of`, rather than inline in the marketplace route and nowhere else. A verified profile shows a badge, so the verified people in a cohort are visible as such. And the screen prints the pool's own head count: three cards out of thirty-eight looked like a quiet deployment rather than a screen reading the wrong table, and a number says which.
>
> The public-row guard was updated rather than routed around. It pins the exact key set a public search row exposes, and `avatar_kind` widened it — but `avatar_kind` is derived from `avatar`, which the row already hands out, and a caller can read `/photos/…` against `/portraits/…` for themselves. *Asked: did the row grow a key. Mattered: did the row grow a fact.*
>
> ## A script was being escaped like a page
>
> `_js_literal` builds the JSON and JavaScript literals the landing page drops inside a `<script>` element — including the translated string table — and it called `html.escape`. A browser does not decode HTML entities inside a script element, so escaping there protects nothing and corrupts the value: `Terms & Conditions` reached the reader as `Terms &amp; Conditions`, in every language that ships.
>
> The page was safe, but by accident. Its docstring named the real hazard correctly — a literal `</script` ends the element whatever the JavaScript quoting says — and the line written to stop it sat *after* an `html.escape` that had already turned `<` into `&lt;`. It never matched anything and never could.
>
> ## Three rows in the escaping ledger were never defects
>
> The sweep behind `unescaped_markup.txt` scanned every f-string twice — once inside its own function, once walking the whole module — and reported the union. Each pass had a blind spot the other did not, so each blind spot became a permanent row. The ledger goes from 8 rows to 2.
>
> ## A Microsoft dependency pin read as one of this release's own version fields
>
> At 1.6.2 the release guard reported `Microsoft.WindowsAppSDK` at `1.6.240923002`, because `1.6.2` is a *substring* of it. Acting on that would have been the worst available fix: the next bump would have rewritten Microsoft's version. The third-party exemption now covers MSBuild's `<PackageReference>` as well as Gradle's coordinate triple.
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v1.6.1...app-v1.6.2

## app-v1.6.1 — QRME app-v1.6.1

- Published: 2026-08-23
- Commit: `fa574e1b3a319f311027fb3163bc55dbd2dff826`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v1.6.1>

> ## A transient mail outage could lock an address out of signup
>
> `accounts.signup` writes the account row and commits it, and only then sends the verification code. That send was never wrapped — reasonably, because until this stack had a mail host `mailer.deliver` printed on the server and returned. It could not fail.
>
>     asked     did the code go
>     mattered  can this person ever sign up
>
> An unhandled refusal costs more than the letter. The caller gets a 500, the pending account survives the request that failed, and the next attempt from the same address is turned away as *already pending* — naming a code nobody ever received. One bad minute at the mail host, and that address cannot create an account.
>
> Signup and `resend` both answer now with `code_delivery: "failed"`, and the password reset with them: a reset that 500s tells somebody already locked out of an account nothing at all.
>
> JIM-mini carries the identical shape and the identical fix. Buying the two mailboxes for this stack is what made it reachable in both.
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v1.6.0...app-v1.6.1

## app-v1.6.0 — QRME app-v1.6.0

- Published: 2026-08-23
- Commit: `fad014738ce38a4ac5d24ee2f5bda85c93604243`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v1.6.0>

> ## A visitor is refused in their own language, not just an owner
>
> The English-only refusal ledger stood at 109. It is 84, and the twenty-five that left are not an arbitrary twenty-five: they are the ones a **visitor** hits. A room that has closed, a party whose host has left, a game session that ended, a comment on a post, a friend request to a profile that is not yours, a microphone you were not lent.
>
>     asked     is the sentence translated
>     mattered  who is standing in front of it
>
> The eleven translated before this are the ones an **owner** meets — credentials, ownership, subscription. An owner has an account, a chosen language and a console. A visitor scanning a code has none of that: they arrive through a link, in whatever language their phone is set to, and the one sentence this product ever says to them may well be a refusal. Handing that person English because the backlog happened to be sorted by module is the wrong order to have worked in. All nine languages; the eighty-four rows that remain are all behind a login.
>
> ## A person's own words stop being cut mid-sentence
>
> The last two silent slices in this product were what somebody typed, and both reach a prompt: the **note** on a document arrives as *"They said: …"*, and the **caption** on a room share lands in the transcript every profile in the room reads. Cut bare at 400 and 500 characters they ended mid-word, which reads to a model as somebody trailing off rather than as a sentence this product shortened. A clinician's letter is material *about* somebody; these two are the person's own writing.
>
> ## Nothing assembled into a prompt is cut inside a word, and a cut says so
>
> `wall.parts` already stated that *a cut inside a word is the one outcome this refuses*. Everything building a PROMPT went on slicing with a bare `[:n]` — the same defect facing the model instead of a reader, and worse there, because a reader sees a word end mid-air and distrusts it while a model reads straight on. A clinician's letter now clips at 1200 rather than 400, behind a marker saying outright that a qualification, a negation or a caveat may sit in the part not shown, and to ask rather than conclude.
>
> ## The cap holds a filing now, and a document that was cut says so
>
> `MAX_TEXT` said *generous for a filing* at 20,000 characters, which a filing routinely exceeds — two thirds of a patent went silently missing. It is 120,000, the clip happens at a boundary, and a document that was shortened reports how much of it is present rather than presenting a fragment as the whole.
>
> ## A guard that nothing a profile does on its own can reach money
>
> A profile has no hands on the money. This makes that a guard rather than a belief.
>
> ## The two prompt caps have names, and the test compares them
>
> The life-entry cap (160) and the clinician's-letter cap (1200) were literals at their call sites, and the test holding the letter to more room than the entry asserted against a third number — a bare `400` that belonged to neither. `tests/ratchets.py` caught it as an unregistered floor, which is what it was. The caps are `LIFE_SNIPPET_CHARS` and `CLINICAL_LETTER_CHARS` now, and the test asserts the relationship between them.
>
> ## 170 of 256 released versions rendered as literal text
>
> The same defect in all three products: a Keep a Changelog heading without a link definition renders as literal `[1.5.0]` text, and `[Unreleased]` had no definition at all. All are defined now, held by `test_every_release_heading_is_a_link.py`.
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v1.5.0...app-v1.6.0

## app-v1.5.0 — app-v1.5.0

- Published: 2026-08-23
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v1.5.0>

> An iPhone gets a voice in a room, interrupting works, and a filing arrives as
> words. Full detail in CHANGELOG.md — this is the shape of it.
>
> ### Added
>
> - **An iPhone can speak in a room.** On iOS the browser's speech recogniser
>   constructor exists and the service always refuses, so the phone this
>   product is mostly used on had a microphone button and no way to speak.
>   Reported twice. `POST /rooms/{id}/heard` takes recorded audio and answers
>   with words, gated exactly like sharing a file. The audio is not stored.
>
>       asked     does this browser have a recogniser
>       mattered  can this person speak in the room
>
> - **A profile answering an interruption knows where it was cut off.** Cutting
>   one off mid-paragraph leaves you holding a prefix of what it said, and the
>   next reply was built from a transcript that showed the whole turn as though
>   you had sat through it. The voice plays sentence by sentence, so the
>   interruption lands on a known boundary; what reached the room now rides on
>   the interrupted turn itself and the model reads it as a stated fact. A turn
>   heard through its last sentence is reported as finished, not as a loss.
>
> ### Fixed
>
> - **A filing written in embedded fonts arrives as words, not as a filename.**
>   Reported four times. A composite font with `/Encoding /Identity-H` writes
>   glyph numbers in its own subset — there is no encoding under which those
>   bytes are language. `/ToUnicode` is the map back and these files carry it.
>   Followed now, including behind the compressed `/Type /ObjStm` layout every
>   recent generator uses. A `/Differences` encoding is followed too, which is
>   the more dangerous half: it produces bytes that *are* letters, the wrong
>   ones, and "See © 2.14 of the specification" passes every readability test
>   and arrives as a document somebody believes.
>
> - **"Held, not read" says which kind of unread.** A scan needs somebody's
>   eyes, a locked file needs its password, and a font this reader cannot
>   follow is a gap in this code. One sentence covered all three, so there was
>   no way to tell a limit from a bug without opening the file by hand. Said by
>   the profile, on the briefcase item, and on the room's attachment line.
>
> - **Barge-in comes back, and the room stops prompting itself.** A recorded
>   turn has an analyser and the browser's own echo cancellation, so
>   `sendPending` asks which ear brought the words rather than only the clock.
>
> - **The seat stops resizing.** Seven chips and a mask picker were wrapping
>   onto three rows and growing the tile. Measured in a browser rather than
>   argued about.
>
> - **Whatever you put up in a room, you can take back down.** Removing the
>   "Just my name" chip on request took out the only caller of the one route
>   that removes an uploaded picture or background from the server. The
>   taking-down half is back, offered only when there is something up.
>
> - **Two door guards that contradicted each other.** One states that recording
>   a deferred route is allowed; another asserted the per-shell records were
>   empty. The second had been reporting a legitimate deferral as a defect. The
>   snapshot is gone, the promise is kept with more teeth: nothing doorless on
>   every surface at once, and every recorded deferral names a real route and
>   carries its reason.
>
> Suite green over this tree: 4368 passed, 3 skipped
>
> ## What's Changed
> * The interrupted turn says how far it got, and a picture comes back down by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/343
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v1.4.1...app-v1.5.0

## app-v1.4.1 — app-v1.4.1

- Published: 2026-08-23
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v1.4.1>

> Three things the room did wrong, all reported from a device rather than found by a test.
>
> **The room stops prompting itself.** The profile's own voice came out of the speaker, went back in the microphone and was sent as a prompt — so it answered itself, in a conversation about somebody's psychiatric care. The echo guard needs 70% of the words to line up, which catches a clean echo and not a misheard one.
>
>     asked     did the room hear something
>     mattered  was it somebody in it
>
> The certain test is not what the words were, it is *when they arrived* — and the flag saying so was already there, unread. Cost stated plainly: speaking over the profile no longer interrupts it.
>
> **The log stops growing and the strip stops moving.** Five rows of conversation pushed the composer and the seven round controls 135px down the page and off a phone. The log was capped, not fixed — a maximum stops the log growing and not the strip moving. Measured in a browser, not argued about. The oldest line fades at the top and still scrolls back.
>
> **The room's ear says why it cannot hear.** The recogniser had no `onerror` at all, and on iOS the constructor exists while the service always refuses — so the mic lit, the refusal fell through to `onend`, and `onend` stood another recogniser, forever. A lit microphone that cannot hear is worse than no microphone, because the person keeps talking to it. This does not give an iPhone a voice in a room — only an honest message
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v1.4.0...app-v1.4.1

## app-v1.4.0 — app-v1.4.0

- Published: 2026-08-23
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v1.4.0>

> Four things that worked and could not be seen to work.
>
> One thread through all four: the work was done and the answer was dropped.
>
> * **A PDF comes back as words, or it comes back as nothing.** Reported three times. Against a real text-bearing PDF the reader produced 1,818 characters of mojibake and declared it read; the same file now reads as 4,295 characters of English. ASCII85 streams were appended still encoded, hex strings were never matched, and `len(text) >= 40` stood in for "is this text". Two of six filter arrangements read before; six do now.
> * **The add-friend button says what happened.** Fired, refused, or returned in silence — all three looked identical.
> * **The room shows you who you know.** The invite worked all along and could only be aimed by typing a profile id nobody has.
> * **A slept tab does not go quietly deaf.** Two relight loops restarting into a page that could not hear
>
> ## What's Changed
> * 1.4.0 — four things that worked and could not be seen to work by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/342
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v1.3.0...app-v1.4.0

## app-v1.3.0 — app-v1.3.0

- Published: 2026-08-22
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v1.3.0>

> QRME 1.3.0 — a profile hands you a page.
>
> It could always write. What it could not do was **give you anything** — ask one to prepare a report and it arrived as a wall of chat, gone up the scroll on the next turn. The reading half of this pipe has existed since 1.0.0: hand a room a PDF and the profiles there discuss it. This is the same pipe pointed the other way.
>
> **How it sends.** Through the channel that already exists. The provider contract is `generate(system, messages) -> str` — one string back, and every provider here implements exactly that, the offline stub and the vault's resident included. A tool channel would have meant changing all of them for a payload that is text the model already knows how to write. So the profile is told it may fence a composition; the fence comes out of what you read and becomes the file.
>
> **How you receive it.** As a real Markdown file on the turn, marked as synthetic media at the moment it is made. The turn carries the document's **card, not its body** — a transcript is polled, and a document in every poll is the document sent again on every poll.
>
> **How it renders.** A card you can open and keep in the console, and a named row on each of iOS, Android and Windows. On every surface it gets its own row rather than being appended to the reply: the words are what was said, the file is what was given.
>
> Two orderings that are load-bearing. The split happens **before** moderation and the body is reviewed together with the words, because splitting after would let a document past a check its covering sentence had to pass. And an unapproved turn writes no file — a refused reply does not get to leave something behind that outlives the refusal.
>
> **`ai_marked` stopped being a constant.** It has been a field in this API since media existed and the literal `False` in every path, because nothing here generated a file. `media.py` already stated the half of the rule that was true: a person's own photograph is never marked, since stamping an authentic picture is a false statement in exactly the direction the mark exists to prevent. A composed document is the mirror of that case.
>
> **And the room is a card on the page again.** The last round moved the transparent bar and its controls down off the faces — which was asked for — and made the room full-screen, which was not: *"in this photo the frames are perfect size and scale."* They were. Every rule that resized them is out, the seat is the 179px tile and 72px face it is drawn at, and the way out is an X.
>
> Suite: 4249 passed, 3 skipped
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v1.2.0...app-v1.3.0

## app-v1.2.0 — app-v1.2.0

- Published: 2026-08-22
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v1.2.0>

> QRME 1.2.0 — whose memory it is.
>
> A conversation's record used to live in the synthetic profile's account, gated on the profile owner's plan. Three things followed, all wrong: whether you were remembered depended on whether **somebody else** was paying; the record of what you said sat in their account, under their key, where you could not read it or take it; and it died the day they stopped paying.
>
> **It is yours now.** Your plan decides whether it is kept, your key seals it, and `GET /interactors/{id}/memories` opens it — across every profile you have talked to, including ones that no longer exist. Nothing reads the key's shape any more: the ledger records every key as its seal is cut, so the arrangement could change without stranding a single conversation this product has already had.
>
> **Deleting a profile takes the profile's own words and stops taking yours.** Its replies, its distilled view of the conversation, its persona, its sources — all still go, in full. What it was also taking was the other party's record of having spoken. The guard that holds the erase and the export in step found the sharper half: a profile's owner downloading their bundle was being handed every interactor's memories, in a file that gets mailed and copied.
>
> **The free plan is hosted rather than forgotten.** Gating memory on a private vault meant a profile forgot everybody who was not paying, and a memory is only worth keeping because the person comes back. Free keeps the words in the deployment's own database, and they improve the shared model — that is what the tier is, said where it applies, with the switch and the count beside it. Turning it off reaches backwards: the refs are meaningless at the gateway, so the past is pulled back without it ever being told whose it was. **A memory sealed in a vault is never contributed, whatever that switch says** — enforced by the row's posture, not the flag.
>
> The arrangement is written on each row rather than read from the plan, so upgrading changes what happens next and never what already happened.
>
> **And the bound voice plays on a phone again.** Every piece was a fresh element built after the synthesis fetch, so the press that started the turn was over and every phone refused it — silently, because the refusal was being swallowed as "this piece is finished".
>
> Suite: 4238 passed, 3 skipped
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v1.1.0...app-v1.2.0

## app-v1.1.0 — app-v1.1.0

- Published: 2026-08-22
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v1.1.0>

> QRME 1.1.0 — the room is a place you walk into.
>
> Every entry here is one sentence somebody said sitting in front of the thing. The through-line is that the room had been built as a page.
>
> **Going in is a press.** An id in the box used to *be* being in the room, so the moment an id existed the console joined and drew the faces — which made the button below them look like it had already been pressed.
>
> **The card that asked which room now names the one you are in.** Room name and Save, over a new `PATCH /rooms/{id}` authorized exactly like speaking: a participant held by their own token.
>
> **Guests are chosen before the door opens.** The invite panel moved onto the way-in screen. The door's rule that you must be in a room to invite to it is untouched — the picks queue and go the instant the join lands.
>
> **The strip stopped resting on the faces.** Reported three times, twice "fixed" by adjusting a number. It was absolutely positioned inside the seat grid over a hardcoded 104px — right the day it was written, wrong the moment the transcript grew. It is a sibling of the scene now: it takes the space it needs and the scene gives back exactly that much.
>
> **One control, one place.** Three duplicate cards collapsed into the band along the bottom. "Let them talk" moved rather than went, because deleting the only door to a capability is not the same act as removing a second copy of one.
>
> Fixed on the way out: the room's new name reaches all three phones (the binding had shipped with no screen, so the route counted as doored while being reachable nowhere), the blank-rename refusal is translated instead of English-only, and four keys the deleted cards left behind are gone.
>
> Suite: 4205 passed, 3 skipped
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v1.0.0...app-v1.1.0

## app-v1.0.0 — app-v1.0.0

- Published: 2026-08-22
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v1.0.0>

> One-point-oh. Everything here came from somebody sitting in front of the thing and saying what did not work.
>
> A document handed to a room is read on the way in, so the profiles there can discuss it instead of naming the file — and what cannot be turned into words is labelled unread rather than guessed at.
>
> The transcript scrolls four rows deep instead of dropping the fourth turn, and a long line wraps rather than ending in an ellipsis mid-sentence.
>
> A person holds their own picture, on the person rather than borrowed from a profile, and it fills the frame in every room. A background sits behind you instead of replacing you. The seat's controls open on an empty seat, which is the one state that needed them.
>
> There is a way out of a full-screen room again — the door existed the whole time and was painted where nobody could reach it.
>
> A profile is told who its maker is, instead of being instructed to treat them as a stranger. Recognition is knowledge, never authority: money and credentials stay ask-first for the owner exactly as for anyone.
>
> Every profile field an owner should control has a door, with adult mode shown and deliberately shut — its three checks live at creation and a switch here would route around all of them.
>
> All five new routes reach the iPhone, Android and the desktop in the same round they reach the console.
>
> Full suite green: 4191 passed, 3 skipped
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.99.1...app-v1.0.0

## app-v0.99.1 — app-v0.99.1

- Published: 2026-08-22
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.99.1>

> A room is a place, not a page. Entering one takes the window: the navigation steps aside, the faces come first and largest in the two columns the design draws, and the room grows its own door.
>
> The ear opens on the way in and the microphone control becomes a mute; four and a half seconds of your own silence sends what you said, so neither starting nor finishing is a button. An echo guard keeps the room's own voices out of your mouth without going deaf while they speak — short interjections are never echoes, because those are the interruptions worth having.
>
> The bottom strip's five controls all do something: a link, an attachment, mute, an invitation, and handing somebody the room. On a phone, press and hold (or double tap) for Help, Landscape and Back to app; tilting reflows to three columns.
>
> Suite: 4114 passed, 3 skipped
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.99.0...app-v0.99.1

## app-v0.99.0 — app-v0.99.0

- Published: 2026-08-22
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.99.0>

> A voice room is a voice room — a room opened for audio arrives speaking, with no type bar to contradict it and the microphone as the way in; leaving any screen ends its voices, the transcript keeps itself current, and the talking light follows the voice actually being heard.
>
> Suite: 4071 passed, 3 skipped
>
> ## What's Changed
> * A voice room is a voice room by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/340
> * Release prep 0.99.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/341
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.98.0...app-v0.99.0

## app-v0.98.0 — app-v0.98.0

- Published: 2026-08-21
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.98.0>

> **The room comes alive.**
>
> Multi-party rooms became real rooms: they speak, listen, stay current on their own, and know who is talking.
>
> **Highlights**
> - **The room speaks for itself, and listens** — auto-hear reads new turns aloud (the backlog stays silent), a dictation mic types into the box and never sends, and the send is the compact arrow.
> - **The room keeps itself current** — the transcript polls every four seconds: other people's turns land on their own, and your own message appears while the profiles are still writing their replies.
> - **The room knows who is talking** — every profile reads labelled history with a cast list (a person, another synthetic profile) and never speaks for anybody else; the talking light follows the voice actually being heard, matched by identity, never by display name.
> - **The room passes things around** — pictures, videos, and files shared between the people in the room, under the transcript's own rules: the bytes decide the kind, the sharer is the token, captions ride moderation, and sharing never makes a profile speak.
> - **The answer begins before it ends** — every bound voice (agent orb, pair chat, room ear, per-turn press) speaks piece by piece; a long reply no longer falls out of the bound voice into the browser's robot.
> - **The starters sound like themselves** — women's voices for the women, a man's that is not the coach's for the men, with a startup repair for already-seeded decks.
> - **The orb says why it cannot hear** — named sentences for the blocked mic, the missing mic, and the unreachable service, instead of a glowing lie.
> - **Leaving the screen ends the voices** — the orb, the room's ear (including across room switches), and the chat overlay all stop on the way out.
> - Plus: the reply ceiling settles at 2.5x, and §8 of the deploy runbook proves the local model with the vault's own posture read.
>
> Full detail: [CHANGELOG.md](https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md)
>
> ## What's Changed
> * Section 8: the vault's real voice — a local model on the box by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/333
> * The starters sound like themselves by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/334
> * The room speaks for itself, and listens by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/335
> * The answer begins before it ends by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/336
> * The room keeps itself current, and the light follows the voice by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/337
> * Leaving the screen ends the voices by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/338
> * Release prep 0.98.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/339
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.97.0...app-v0.98.0

## app-v0.97.0 — app-v0.97.0

- Published: 2026-08-21
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.97.0>

> ### Added
>
> - **Everyone here — the browse pool.** The field asked for it in
>   head-count terms: every profile made on the deployment goes on the
>   browse list under Friends, real people and synthetic ones side by
>   side, with the honest total and a per-kind breakdown. Listing is the
>   default; privacy is the door out — **Go private** takes a profile out
>   of the pool and the name search both, reversibly, per profile. The
>   two standing exclusions hold: anonymous profiles never appear, and
>   only active profiles greet strangers. The pool stands on every
>   surface: the console's Friends screen and real doors on all three
>   native shells, each in its own ten-language table.
>
>       asked     who is here
>       mattered  a deployment whose people cannot see each other is a
>                 hallway of closed doors
>
> - **The voice binds to the account that brought it.** The binding read
>   is public on purpose — a voice a stranger can hear is a voice a
>   stranger should be able to check — which put every voice id one
>   screen away from every other tester, on a deployment whose engine
>   key is shared. The warning was given the day the key went
>   deployment-wide: anyone who learns an id can bind it and speak with
>   somebody else's cloned voice. The first account to bind an id holds
>   it now — their own profiles may share it, another account is refused
>   with the reason, and unbinding everywhere releases the claim.
>
>       asked     whose voice is a bound voice
>       mattered  a claimable clone of a real throat is impersonation
>                 with extra steps
>
> ### Fixed
>
> - **The bound voice reaches the conversation.** A profile whose owner
>   had made and bound a real voice still answered the agent's orb and
>   the chat screen in the browser's robot — the binding worked
>   everywhere except where the profile talks back. Both now speak
>   through the bound voice first (the deployment's engine, the
>   watermark riding in the header), with the device's voice standing in
>   when there is no binding, no engine key, or the reply outruns the
>   synthesis ceiling; the orb's relight contract and the chat face's
>   "speaking" state carry over either mouth.
>
>       asked     whose voice answers
>       mattered  the voice somebody made, or a robot wearing their name
>
> - **The orb tells the truth, and the conversation bows out.** A silent
>   stretch ends the browser's recogniser on its own, and the agent's
>   orb kept saying "listening" over a dead microphone. It relights now,
>   and the conversation ends itself after two quiet minutes — the same
>   number JIM's rooms settled on — instead of holding the mic open all
>   afternoon. While the reply is being spoken the orb says so ("Speaking
>   — it listens again after", ten languages), a failed turn relights the
>   mic instead of stranding the orb, and the idle clock restarts when a
>   reply finishes, so a long answer never eats into the person's two
>   minutes.
>
>       asked     is the orb's word the microphone's state
>       mattered  a voice UI that lies about listening is unusable twice
>                 over — once hot, once dead
>
> ## What's Changed
> * The voice binds to the account that brought it, and the orb tells the truth by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/330
> * Everyone here is the default, and the bound voice reaches the conversation by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/331
> * Release prep 0.97.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/332
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.96.0...app-v0.97.0

## app-v0.96.0 — app-v0.96.0

- Published: 2026-08-20
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.96.0>

> ### Changed
>
> - **The picture goes up like the camera.** Putting a picture up in a
>   room met a small circle with the buttons still showing. The photo is
>   full-bleed in the tile now, for every seat — a face is a face
>   whether pixels stream or stand still — and on your own tile the
>   controls hide behind the same double-tap or hold the camera taught,
>   with the same hint. Behind the reveal: a different photo, the
>   camera, the plain name, the masks — the four ways out a person
>   standing in the room reaches for.
>
> - **Connecting a device reads like the phone's own Bluetooth page.**
>   The wearables card was prose. It is the settings shape now: a "My
>   devices" group of rows — name, Connected or Not connected on the
>   right, an ⓘ opening the detail with the unpair door — and an "Other
>   devices" section holding the scan (the browser's own chooser; the
>   web cannot passively list what is nearby, and this page does not
>   pretend to) and the manual add. Ten languages.
>
> - **The reply ceiling comes back to five.** `MAX_REPLY_TOKENS` went
>   from 1024 to five times the room when long answers met the wall
>   mid-sentence, then to ten — and the field called ten back down: a
>   spoken conversation waits for the whole reply before it says a word,
>   and ten times the room was minutes of orb where a talk turn wants
>   seconds. Back to 5120, which held both ends when it was first tried.
>   The truncation honesty is unchanged — a reply that hits the wall
>   still says so instead of stopping mid-sentence.
>
>       asked     how long may a reply run
>       mattered  how long a person mid-conversation waits to hear it
>
> ## What's Changed
> * The eyes open on the beta host by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/327
> * The spoken turn, the picture up, and the device page by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/328
> * Release prep 0.96.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/329
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.95.0...app-v0.96.0

## app-v0.95.0 — app-v0.95.0

- Published: 2026-08-20
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.95.0>

> Everything handed over is heard. The ears arc reaches every briefcase door: a read-once link that is a recording comes back as the words said in it (and is honestly held, not read, without ears — the plain fetch never again seals media bytes as a reading); an uploaded video or .m4a voice memo is heard through the ears' new bytes door, with the socket gated and the visit witnessed against the profile the upload belongs to; and true audio files — MP3, WAV, Ogg, FLAC — stop being refused as unrecognized and land as a recording of their own. The suffix list that decides what counts as a recording lives in one place, shared by the briefcase and the lookout.
>
> Full changelog: https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
>
> ## What's Changed
> * The briefcase hears by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/323
> * The upload hears by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/324
> * The voice memo lands by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/325
> * Release prep 0.95.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/326
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.94.0...app-v0.95.0

## app-v0.94.0 — app-v0.94.0

- Published: 2026-08-20
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.94.0>

> The stack grows ears. A transcription sidecar joins the deploy stack — a local speech-to-text model in its own container, outward-looking only, keeping no copy: a recording fetched on someone's behalf never leaves the facility to become words. The lookout twin hears: a media URL stands a listening appointment with the same change-memory the pages keep, and the letter calls a watched recording what it is. The study says who answered — recorded beside what could have left, carried into the vault's own ledger, and worn on the owner's screens in ten languages.
>
> Full changelog: https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
>
> ## What's Changed
> * The study says who answered by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/320
> * The stack grows ears by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/321
> * The lookout grows ears, and the release cuts by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/322
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.93.0...app-v0.94.0

## app-v0.93.0 — app-v0.93.0

- Published: 2026-08-20
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.93.0>

> The stack grows eyes, and the letters keep every promise. A rendering sidecar joins the deploy stack — a real browser, outward-looking only, a fresh browser per render — and everything reading a page on someone's behalf uses it: the briefcase's read-once links carry the page a person meets instead of 'read once — 12 characters', and the lookout twin watches rendered pages. The weekly letter is sanitized before any voice that leaves the host and discloses left_host; it rebuilds from what the tables still hold after any forgetting, and a week whose facts are gone loses its letter. A standing guard now proves every documented variable reaches its container, both directions.
>
> Full changelog: https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
>
> ## What's Changed
> * The stack grows eyes by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/316
> * Complete context rides the briefcase and the lookouts by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/317
> * Every documented variable reaches its container by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/318
> * The letter is not the looser door by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/319
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.92.0...app-v0.93.0

## app-v0.92.0 — app-v0.92.0

- Published: 2026-08-20
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.92.0>

> A backup you haven't restored from is a belief. The deploy page grows the restore drill: the newest dump booted in a scratch container, the audit chain proven intact end to end, and a record sealed before today read back through the escrowed master key — every command one short paste-safe line, field-tested live as it was written. The drill's first run caught a wrong escrowed key while the right one still existed: the exact ending it exists to prevent, converted into a same-day fix. The backup loop now writes a freshness marker so a quietly dead loop is a line you can check, and the deploy-day gaps — the unforwarded pulse, the wrong models path — are written down as what they were.
>
> Full changelog: https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
>
> ## What's Changed
> * The pulse reaches the container by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/312
> * The models check asks a door that exists by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/313
> * The changelog says what the fixes were by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/314
> * A backup you haven't restored from is a belief by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/315
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.91.0...app-v0.92.0

## app-v0.91.0 — app-v0.91.0

- Published: 2026-08-19
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.91.0>

> The profile reports to its owner. The excursion honors the voice choice: a vault-voiced profile studies inside, the cloud sees nothing, left_host honestly false. And the weekly letter arrives — the pair's week composed from what it actually held: messages and with whom, moments sealed, studies taken, watched pages that changed or are failing, questions asked on the open board and the answers that came back — a deterministic digest the profile's own provider turns into prose, described_by disclosing whether a model or the digest wrote the body, an empty week refusing translated, a shelf of past letters on all four clients.
>
> Full changelog: https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
>
> ## What's Changed
> * The excursion honors the voice choice by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/308
> * The week in the pair's words by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/309
> * The letter accounts for the asking by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/310
> * Release prep 0.91.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/311
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.90.0...app-v0.91.0

## app-v0.90.0 — app-v0.90.0

- Published: 2026-08-19
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.90.0>

> The watching answers to its owner. The lookout list and the capture read-back say when each watched page last actually changed — "Changed {when}", translated on all four clients — and the profile's prompt block wears the change date beside the capture date, so a persona can say how fresh the menu it quotes really is. When the vault's latest round on a lookout failed, its why rides the row in red: only the latest round speaks, an older vault says nothing rather than guessing, and a lookout in trouble never makes the list itself fail.
>
> Full changelog: https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
>
> ## What's Changed
> * The lookout says when the page changed by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/305
> * The lookout says why it fails by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/306
> * Release prep 0.90.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/307
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.89.0...app-v0.90.0

## app-v0.89.0 — app-v0.89.0

- Published: 2026-08-19
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.89.0>

> The profile speaks from what it keeps, and keeps itself current. With the vault provider chosen, the resident ranks the pair's own seals against the last thing said and answers from them — retrieval and generation both inside the facility, the pair prefix standing as the wall inside the shared tenant, grounded_in_vault disclosed in the provenance. And the lookout twin: an owner plants “keep an eye on this page” as one standing appointment in the vault whose single fetch re-seals the current capture every cycle, and the latest captures ride the chat prompt dated and capped — a persona whose menu changed this morning speaks this morning's menu. Consent-gated behind study_the_web, erasure-honest, on all four clients.
>
> Full changelog: https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
>
> ## What's Changed
> * The profile answers grounded in the vault by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/302
> * The profile keeps itself current: the lookout twin by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/303
> * Release prep 0.89.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/304
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.88.0...app-v0.89.0

## app-v0.88.0 — app-v0.88.0

- Published: 2026-08-19
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.88.0>

> The voice inside the vault. A vault provider routes a profile's generation through PDI's resident inference: the words are made on the facility's own hardware, the prompt travels the one authenticated channel every seal uses (audited by length, never by words), and a vault with no local model falls honestly to the product's own stub rather than speaking an operational sentence in a persona's voice. Recall keeps the real vault: a member who moved to Free keeps being recalled from the pair's sealed moments while their new turns are honestly not sealed at all.
>
> Full changelog: https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
>
> ## What's Changed
> * The voice inside the vault by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/299
> * Recall keeps the real vault by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/300
> * Release prep 0.88.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/301
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.87.0...app-v0.88.0

## app-v0.87.0 — app-v0.87.0

- Published: 2026-08-19
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.87.0>

> Profiles remember by meaning, and the pair holds the eraser. Each thing a person tells a profile is sealed into the tandem and embedded under the same key, recalled pair-scoped — what Alice said never surfaces for Bob. The pair's sealed shelf lists every remembered moment with a per-moment forget, and every transcript door — strike, forget by words, rewrite, erase-all — reaches the vault, so nothing struck stays findable.
>
> Full changelog: https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
>
> ## What's Changed
> * The profile remembers by meaning, through the vault by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/294
> * Profile erasure takes the memory vectors too by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/295
> * The sealed shelf, shown and curatable — the interactor's own door by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/296
> * Transcript curation reaches the vault — no door forgets halfway by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/297
> * Release prep 0.87.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/298
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.86.0...app-v0.87.0

## app-v0.86.0 — app-v0.86.0

- Published: 2026-08-18
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.86.0>

> The AR and VR rooms become places to stand in. The room screen now reads the channel the join answer always carried: AR anchors every seat over the device's own passthrough (drawn only for you — nothing streamed or stored), VR renders a floor grid under a turntable of seats you drag to look around, and both keep the scene's rules with the last thing said riding the stage.
>
> Full changelog: https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
>
> ## What's Changed
> * The AR and VR rooms become places to stand in by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/292
> * Release prep 0.86.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/293
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.85.0...app-v0.86.0

## app-v0.85.0 — v0.85.0

- Published: 2026-08-18
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.85.0>

> The beta round, worked end to end — the room's camera, masks and faces; spoken voices for every starter; the agent screen as corrected, with a keyless web search on all four clients; the field-reported fixes from the feed to the blend; the grouped menu and its renames; and available finally meaning somebody real answers. Full notes in CHANGELOG.md
>
> ## What's Changed
> * Four commands on the deploy page that had never been typed by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/286
> * The agent's remit, which was prose in a docstring by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/287
> * The beta round: the room, the agent, the doors, and the menu by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/288
> * The words inside match the doors outside by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/289
> * Available means somebody real answers by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/290
> * Release prep 0.85.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/291
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.84.0...app-v0.85.0

## app-v0.84.0 — QRME 0.84.0 — The step that was impossible to perform

- Published: 2026-08-18
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.84.0>

> ## The step that was impossible to perform
>
> 0.83.0 moved `exit` to the first line of each check block on the deploy page, reasoning that it was the same repair as the `ssh` at the top of the deploy block. The reasoning was wrong and the next deploy proved it in one paste.
>
>     asked     does the page say to leave the host
>     mattered  can the reader actually get there
>
> The two are not symmetric. `ssh host` followed by more lines works, because ssh takes the rest as standard input and runs it on the far side. `exit` followed by more lines does not: the shell tears down and the remainder goes into a session that is already closing. It echoes, and it is gone — a deploy that had gone perfectly, three checks that never ran, and no error to say so.
>
> The first version made the step easy to skip; the second made it impossible to perform, which is worse. A skipped step at least leaves a prompt you can still type into.
>
> Getting to your own machine is **a new window**, and that is prose because it is not a command. The guard is inverted to match: a check block must now contain no change of machine at all, where it previously required one.
>
> Its companion was too loose on the first pass and had to be tightened before it could catch anything — it accepted a bare *new window*, which the paragraphs explaining why it is a new window also contain, so deleting the instruction left it green. That is the second guard on this page in two days to match its own surrounding prose. A guard that can be satisfied by the explanation of a rule is not checking the rule.
>
> ---
>
> **Full changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.83.0...app-v0.84.0

## app-v0.83.0 — QRME 0.83.0 — The page somebody pastes, one step down

- Published: 2026-08-17
- Commit: `main`
- Assets: 0
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.83.0>

> 0.82.0 put `ssh` inside the block you copy, because a fenced block of its own is a block you skip. The next deploy found the identical defect one step down, twice in the same paste.
>
> ## The check that ran in the wrong room
>
> The version checks after the deploy are meant to run **from your own machine**, and the line that gets you there was a sentence between the two blocks — *then `exit`, and check from your own machine* — with a paragraph beneath them explaining why it mattered. Both were true; neither was run.
>
> The three checks went in on the host, which is the one place they prove nothing: they answer from inside the network they exist to test from outside, so they printed the right version and confirmed nothing about what a visitor gets.
>
>     asked     does the page say to leave the host
>     mattered  is that line inside the block somebody copies
>
> ## An alternative laid out as a sequence
>
> The Windows block, correct in every character, sat where the next step goes under the words *on Windows, use these instead*. A reader working down the page ran the Unix three, saw three health objects, and ran the Windows three in the same shell — `curl.exe: command not found`, three times, after a deploy that had again gone perfectly.
>
> ## What changed
>
> `exit` is the first line of each check block now, for the reason `ssh` is the first line of the deploy. The two blocks are marked as a choice rather than laid out as a sequence. And each carries all three products, because a block somebody runs on its own has to check all three on its own.
>
> ## The guard that was itself too loose
>
> One of the three new guards accepted the word *either*, which § 7 already contains four paragraphs up in *docker is usually not installed there either* — so it passed on a page carrying no marker at all. A guard whose word can arrive by accident reports on the prose rather than on the shape. Each of the three was then checked by breaking the page deliberately and watching it go red.
>
> ---
>
> On the console, on iOS, on Android and on Windows. 3824 tests passing, 2 skipped.
>
> **Full changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.82.0...app-v0.83.0

## app-v0.82.0 — QRME 0.82.0 — Right in one place, wrong where it was used

- Published: 2026-08-17
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.82.0>

> Two rounds, and both are about a thing being right in one place and wrong everywhere it was actually used.
>
> ## The deploy page had the room and not the doorway
>
> `docs/beta-deploy.md` § 7 warned that `/srv/qrme` is on the host, then put `ssh root@your-host` in a fenced block of its own above the deploy. A block of its own is a block you skip — what gets pasted is the thing that looks like the procedure.
>
> It was pasted into PowerShell on a handheld and failed twice: no such path, and no `docker`.
>
>     asked     does the page say to get on the host
>     mattered  is that line inside the block somebody copies
>
> The Windows check lines had the same shape one layer down. The page said *on PowerShell, add `.exe` to each* — true, and attached to three lines that also carry `; echo`. In PowerShell `echo` is `Write-Output`, which at the end of a pipeline with nothing feeding it stops and prompts for input. Following the instruction exactly still produced an error naming a cmdlet nobody typed, after a deploy that had gone perfectly.
>
> Both are one failure: a correction written *about* a command instead of *as* one. The `ssh` is the first line of the deploy block now, the PowerShell form is written out as its own block, and `tests/test_the_deploy_page_is_paste_ready.py` holds the shape — the page may be rewritten, and its commands have to stay runnable by the reader they are addressed to.
>
> ## A guard on the sentence that forgets how it was built
>
> 0.81.0 fixed the sealed-dialer sentence going out in English in every language — `str()` on a `Templated` returns a plain `str`, and the template goes with it — but fixed it at the one site that was known.
>
>     asked     is the refusal translated
>     mattered  did it still know how it was built when it got there
>
> The guard that makes the class of defect impossible landed after the tag, and it found a second site immediately: the excursion route, written in the same round as the fix, laundering the privilege refusal exactly the same way.
>
> `test_a_built_sentence_is_not_laundered_through_str` reads which of this product's own exceptions carry a built sentence, then fails any route that catches one and passes on `str(exc)`. It is carried by all three products, where this class of defect has always lived — JIM-mini and PDI have no such exception today, and the guard is what makes the first one safe rather than the thing that ships the defect again.
>
> *(It went on to find one in JIM-mini the day after, in the day's-budget refusal.)*
>
> ---
>
> On the console, on iOS, on Android and on Windows. 3822 tests passing, 2 skipped.
>
> **Full changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.81.0...app-v0.82.0

## app-v0.81.0 — QRME 0.81.0 — What the agent may do

- Published: 2026-08-17
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.81.0>

> ## What the agent may do
>
> The product grew powers faster than it grew a place to see them. A profile could go and study the open web, put a question to strangers, package a history for a professional, run a job over vaulted material and reach emergency services — and the only way to find out was to read a changelog or to meet one mid-conversation.
>
>     asked     can the agent do this
>     mattered  did the person decide it could, knowing what it costs
>
> Every row is on one list now. It says what the agent would be allowed to do, in the words a person would use for it afterwards. It says **what it keeps**, which is the half these lists usually omit: "summarise your meetings" and "summarise your meetings, and keep the recording" are different agreements, and only one of them is what the code does. And it says whether exercising it reaches somebody who never chose it.
>
> That last one is a field rather than a paragraph so it can be checked. Anything that reaches people who did not choose it is off until somebody turns it on, whatever else is true about it, and a guard reads the table and refuses. One row is on by default — going out to read — and it carries the written reason why, beside the sanitiser and the visits ledger that make it answerable.
>
> The check sits at each power's own last hop and never in the route above it. The refusal names the thing rather than the identifier, and arrives in the reader's own language. Visitors read the same list: what an agent may do on somebody's behalf is not a secret kept from the person it would be done to.
>
> ## Also in this release
>
> **Forty more refusals stopped speaking English to everyone.** The backlog of untranslated refusals fell from 149 to 109.
>
> **Bringing somebody real into it, in every area of life.** A profile can hand its matter to a butcher, a broker, a physiotherapist or a doctor — the people you already keep, per area of life, yours before the search — and catch them up before they arrive, so nobody tells the story twice. What travels is decided by a revocable grant and by nothing else.
>
> **A real dialer, an explicit press, and a door that will not open in beta.** The waiver is signed ahead in calm conditions over those exact words, the press is explicit, and the last hop refuses: the call is attempted and stopped where it would leave, and what comes back says plainly that no call was placed and gives the number to dial.
>
> **A fix to that last one.** Its sealed-call sentence was translated into nine languages and reaching none of them — `str()` on a built sentence forgets how it was built.
>
> ## The shape of it
>
> On the console, on iOS, on Android and on Windows. 3,815 tests passing.
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.80.0...app-v0.81.0

## app-v0.80.0 — QRME 0.80.0 — The agent asks people, and somebody is counting the visits

- Published: 2026-08-16
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.80.0>

> An excursion asks a model and gets back what was already written down. An **inquiry** asks people: the question goes on an open board anybody can answer with no account and no name, and an answer the owner accepts folds into the profile as a knowledge source — so the offline model ends up knowing something it could not have looked up, and the person who knew it never learns whose question it was.
>
> The sanitiser cannot be told not to — a guard fails any boolean parameter and any branch inside it — and the board carries the scrubbed line and nothing beside it: not the profile, not the typed question, not even the redaction count, because two questions with the same unusual count are a thread to pull.
>
> Beside it, the case a scrubber never covered. Offline mode answered *did anything leave*; nothing answered *who has watched us leave, and how often*. Every outbound connection is witnessed now at the one function every socket already passes through — **host only, never the path**, because in a profile fetch that tail is the subject's own handle — and standing a host down refuses at the socket, so it binds every fetcher rather than the screen that listed it. The deployment-wide totals carry no profile at any depth: a tool for measuring correlation must not become a way to correlate people.
>
> Console, iOS, Android and Windows. Full changelog: https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.79.0...app-v0.80.0

## app-v0.79.0 — app-v0.79.0

- Published: 2026-08-16
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.79.0>

> ## The shop, the lock, and the button nobody ever had
>
> ### A plug-in storefront, and the whole board on it
>
> The connector catalogue has existed since the connected-apps round and the only way to see it was a dropdown of providers inside another screen — chosen before you knew what any of them were.
>
> ```
> asked     can a profile connect to an outside service
> mattered  can a person find out which ones, and what happens then
> ```
>
> It was also forty-two rows of device AI. It is **103 rows across nine families** now: the inbox, the calendar, the drive, the docs, the chat, the issue tracker, the CRM, the payment processor, the design tool, the papers; the open web; and the public social pages a profile reads without ever posting to them. The storefront is a new tab on the console and the same board on all three phones.
>
> ### The lock is a posture now, not a picture
>
> `invoke` answered *performed* for every connector on the board, whatever credential it did or did not have. A Gmail connector with no Google account behind it reported that it had summarised the inbox.
>
> ```
> asked     did the call succeed
> mattered  did anything happen on the other end
> ```
>
> Every row declares what it needs first — nothing, your own sign-in, or an operator key. A row that needs nothing works the moment it is added; everything else is installed and inert until the credential is given, and `invoke` refuses it by name until then. The credential is sealed into the vault and this database keeps only the key; with no vault there is nowhere safe to put it, so it is refused rather than held in the clear.
>
> **Upgrade note:** connectors on a running deployment become unauthorized and refuse `invoke` until signed in. That is the correction, not a regression — they were never reaching anything.
>
> ### `/apps` starts with `/app`
>
> The door guard skipped every path beginning `/openapi`, `/docs`, `/redoc` or `/app`. The last meant *the console bundle mounted at /app*, and `startswith` does not know that.
>
> ```
> asked     is this route the documentation or the bundle
> mattered  is `/apps` a prefix of `/app`
> ```
>
> The whole connected-apps block was invisible to it on every surface, for as long as the guard has existed. What that hid: **uninstalling a connector had no door on any client.** Somebody could connect their inbox to a profile and had no way to disconnect it. The console could also neither collect from a connector nor use one. All four are on the storefront now.
>
> ---
>
> JIM-mini and PDI carry no code changes at 0.79.0; the three move together so the version guard has one answer.
>
> Suite green over this tree: 3724 passed, 2 skipped.
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.78.0...app-v0.79.0

## app-v0.78.0 — app-v0.78.0 — A front door, not a poster

- Published: 2026-08-16
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.78.0>

> **The Agent tab was a card with a textarea, not a front door.** What 0.77.0 shipped was a poster at full width, a sentence, and a card headed *Ask for it in words* holding a textarea. The tab is the way in to a collaborator for the whole app, and a person opening it met an illustration and had to scroll to type.
>
>     asked     is there a way to talk to the agent
>     mattered  is it the first thing on the screen
>
> It is a composer now: one pill with `+` inside on the left, the box, then the microphone, the room and send on the right.
>
> The `+` opens a vertical popover — Camera, Photos, Files, Plugins, Write or edit — and each of the five opens a screen that exists. Above it, a rail of nineteen destinations scrolling sideways, each chip named from the same row the navigation reads. Three openings sit above the composer for somebody who has the screen and not the sentence.
>
> **The poster is the tab's, and only the tab's.** It sat on the screen as well, above everything — a poster inside the room it is the door to.
>
> **Fixed:** the deploy page had the commands and not the room. `docs/beta-deploy.md` §7 opened on `cd /srv/qrme` with nothing saying which machine that is. It has an `ssh` step now, an `exit` before the health checks, and a note that PowerShell needs `curl.exe`.
>
> Full suite green over this tree: 3712 passed, 2 skipped.
>
> JIM-mini and PDI stay at 0.77.0 — neither has a commit since that tag.
>
> [Changelog](https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md#0780---2026-08-16)
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.77.0...app-v0.78.0

## app-v0.77.0 — app-v0.77.0 — The Agent, opened up

- Published: 2026-08-16
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.77.0>

> **The Agent has its own tab, and a reach worth opening it for.** The agent that can rewrite your page, edit your homepage sandbox and write your widgets had existed since the Studio shipped, and the only way to reach it was to open the widget workshop first.
>
>     asked     can an agent edit this person's app
>     mattered  can the person find the agent
>
> It is now the second tab, behind the QRME poster cropped to a box.
>
> **Its roster went from eleven rows to 113.** The profile itself, what it knows, the face it wears, proving it is really you, the wall, money, the things that exist — stickers, robots, watches — messages, what it remembers of people, and how it ends.
>
> **Twelve rows ask instead of doing.** A step that cannot be taken back stops mid-turn and returns what it *would* do — the roster's own sentence and the arguments it chose, both shown. No prose reaches the press and no model is asked.
>
>     asked     may this person do this
>     mattered  did this person mean this
>
> *Wind it down* and *wind that thread down* are one word apart, and no prompt gets that to zero; a button does.
>
> **Also:** the room is a scene — every person in their own square, the talker's square lit, and the box is where somebody turns on video, uploads a photo or wears a mask. A reply that runs out of room now says so instead of stopping mid-sentence, in whichever of the ten languages the platform is speaking.
>
> **Fixed in the guards:** a check that could not tell `require_owner` from `require_owner_or_interactor`; a route guarded by a helper that read as unguarded; a value on iOS that only survived as its caption.
>
> Full suite green over this tree: 3712 passed, 2 skipped.
>
> [Changelog](https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md#0770---2026-08-16)
>
> ## What's Changed
> * A room you could open, walk into, and ask nobody into by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/284
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.76.0...app-v0.77.0

## app-v0.76.0 — app-v0.76.0

- Published: 2026-08-15
- Commit: `ef2338e935f1e8c97a1484e91403dde0031bc2da`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.76.0>

> ## Added
>
> **Signing in reaches what you own.** An owner token is minted once, in the create response. Two new doors reach the roster through the credential a person actually has — the account token behind an email and a password — and mint a fresh owner token on request, shown once. A profile on another account answers exactly as one that does not exist.
>
> **Thirty-four friends pictures, one blank page behind all of them.** A face in a friends grid is a link, and the Starter Collection is the one place a fresh deployment has a full grid. Every face opened the same blank purple page. Each starter's homepage is now composed from the dossier it is already grounded in — expertise and services as the about, three skill chips as the headline, a palette by family of trade. No invented links: a fictional physician has no website.
>
> ## Fixed
>
> **The Studio's run button answered a 500.** `widgets.run` asked a row-mapper's output for the column name it renames on the way out, and raised `KeyError` before the widget started — every press, since the Studio shipped. Nineteen sandbox cases proved all four walls and not one ran a *stored* widget.
>
> **The guard that catches vocabulary drift was the one QRME did not have.** Ported from its siblings, and it fired on arrival: a shared field label read one way here and another in JIM-mini.
>
> ---
>
> One of three products cut together at this number. Full suite green: 3643 passed.
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.75.0...app-v0.76.0

## app-v0.75.0 — QRME v0.75.0 — a bare "s" is not a word

- Published: 2026-08-15
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.75.0>

> The console-untranslated ceiling goes back to 1.
>
> It was 1, then 58 when the reader learned to see a sentence chosen at render time, and the file said the next rounds would take it back down. This is those rounds: fifty-seven strings across Settings, Robots, Selling, Workshop, Referrals, Assist, Desk, Identity, Lobby and Remainder now carry a key and ten translations each.
>
> Two of the fifty-seven were never translation work. Lobby rendered a bare "s" as its own node after a session count — English pluralisation as a suffix, which is not how the plural works in most of the other nine languages — and Remainder did the same with thing/things. Both are one whole sentence per number now. A reader looking only for untranslated words would have found "s" and shrugged; the reason it is on the list is that it is not a word.
>
> The row that stays is `AI ·`, quoted rather than written: the server hardcodes those two characters, and a translated `IA ·` would be a mark the product never produces.
>
> One correction the full suite caught that the guards beside the work did not: a global replace intended for a new key also hit `ref.creds.none`, which had its own call site. The key went dead and the screen went back to English. Restored.
>
> Cut with jim-mini and pdi on one number.
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.74.0...app-v0.75.0

## app-v0.74.0 — app-v0.74.0 — A post that stops inside a word

- Published: 2026-08-15
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.74.0>

> A profile asked for a specification answered at length, the wall took the first two thousand characters, and the reader got a sentence that ended mid-word — then asked it to finish, five times.
>
> The cap is 20000 now. Past it, `parts()` makes a numbered series where every piece says where it sits and every piece but the last says it continues — a reader who lands on part three knows they have missed two. A cut is allowed; a silent one is not.
>
> Also: the importer filed every face from a phone under "somewhere else" while the shelf had named eight avatar systems for releases, and the console guard checked the sidebar and none of the other forty-nine files.
>
> One of three products cut together at 0.74.0. Full detail in CHANGELOG.md.
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.73.0...app-v0.74.0

## app-v0.73.0 — QRME 0.73.0 — the briefcase, the avatar that is not the profile, and one face for a face that is not there

- Published: 2026-08-14
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.73.0>

> A profile can be handed something to read and still have it on the next turn. A link pasted into a conversation was already fetched and read — and then evaporated, so discussing a document meant pasting it again and paying its full length again, and a photograph, a filing or a spreadsheet had no way in at all. The briefcase reads what you hand over once, distils it to a digest, and it is the digest every later turn carries. It is scoped to the two of you, so the next visitor inherits none of it. What this deployment cannot see, it says it cannot see: a photograph, a video and a scanned PDF import anyway, marked unread, with the profile forbidden to describe them.
>
> A portrait can now be a video loop, a rigged model or a character skin bought from the market rather than only an image — picked the way a voice is, from drawn tiles with a URL box and an upload beside them — and all 34 starter profiles have a standing figure instead of a head and nothing below the collar.
>
> Memory follows the person rather than the browser. Signing in on a laptop and then a phone met the same profile as two strangers, and clearing a browser lost the relationship outright; a visitor now attaches to an account.
>
> And a profile with no portrait had five different faces depending on where you met it — initials twice in the console, a blue orb on the conversation screen, initials again on the beacon page, and an Android camera overlay that drew a monogram always and never read the portrait it was sent. On a profile whose name is hidden, that monogram was the hidden name. There is one frame now, everywhere.
>
> Also fixed, and the reason to take this release: `CREATE TABLE IF NOT EXISTS` does nothing to a database that already has the table, so a new indexed column existed on fresh installs and on no existing one. The index named a column the old table did not have, and the backend refused to open its database at all. Existing databases are migrated in place on first connect.
>
> Cut in step with JIM-mini 0.73.0 and PDI 0.73.0.
>
> ## What's Changed
> * The briefcase: read once, and still there on the next turn by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/283
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.72.0...app-v0.73.0

## app-v0.72.0 — QRME app-v0.72.0

- Published: 2026-08-14
- Commit: `a6bf082222c1dc4de480679f0397240de97b205e`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.72.0>

> Their homepage, and the phones that can now open one.
>
> Pressing a friend's face used to open a card showing the signed-in profile's memory count, engagement and moderation rate under somebody else's name — four friends, four identical screens, because only the header was ever theirs. The new screen carries their page as they decorated it, their Top 8 walking onward, their wall, their photographs and footage, and the three things a visitor may actually do. It carries no numbers row at all, and that absence is the fix: /stats is owner-only, which is exactly how the old card came to be showing yours in place of theirs.
>
> iOS, Android and Windows get the same screen. Their PageCard bindings were three fields out of a payload carrying eight — Android's flattened the whole answer to "theme · tagline" — which is why no shell had a screen it could have built.
>
> GET /profiles/{id}/media gives the upload door its other side: uploads were accepted since 0.42.x with nothing that listed them.
>
> Also: a room can be opened without a topic again, and the Swift reader in the translation audit no longer counts a property name as an English sentence.
>
> ## What's Changed
> * Their homepage: where pressing a face actually takes you by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/282
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.71.1...app-v0.72.0

## app-v0.71.1 — QRME app-v0.71.1

- Published: 2026-08-14
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.71.1>

> ## The API did not import on Windows
>
> `qrme/widgets.py` imported `resource` at module scope. It is POSIX-only, and `qrme/api.py` reaches it through `routers/studio`, so this was never "the sandbox is unavailable on Windows" — it was the whole API failing to import there. The frozen desktop backend died on first run with `ModuleNotFoundError: No module named 'resource'`, which failed the Windows installer job, which skipped the release job — which is why 0.70.0 and 0.70.1 published with no installers attached at all, not even the macOS and Linux ones that had built cleanly.
>
>     asked     does the module import
>     mattered  does it import on every platform we ship
>
> Absent, `resource` is the missing-wall case wearing different clothes, so it is handled the way this module already handles a host with no `unshare`: the import is allowed to fail, `sandbox_available` returns `widgets.no_rlimits` in the reader's own language, and every other route on the API still answers. A widget still never runs with three walls instead of four.
>
> The guard is a property of the text rather than a run, because a suite that only runs on Linux can never import its way to this. No module under `qrme/` may import at module scope a name some target platform lacks, unless the import is wrapped in a handler for its absence — and a `try` alone does not satisfy it, since `except ValueError` would silence the guard and leave the process dying exactly as before.
>
> Also here, and older than this release: the `[0.71.0]` link definition was missing from the changelog, so `[Unreleased]` was diffing against a tag two releases old. And `docs/beta-deploy.md` learned to update a running beta rather than only stand one up.
>
> ---
>
> Cut with JIM-mini 0.71.1 and PDI 0.71.1. Full local suite green — 3441 passed, 2 skipped.
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.71.0...app-v0.71.1

## app-v0.71.0 — QRME app-v0.71.0

- Published: 2026-08-14
- Commit: `019da950520b8a8f492d9492fb04987dfdc226a3`
- Assets: 0
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.71.0>

> ## The player learned the origin, and the deck became the screen
>
> **A player handed no origin will not play.** From the beta, on a phone: a
> YouTube post on the Wall rendering a grey panel reading *Error 153 — video
> player configuration error*. The link was fine and the embed was fine.
> `pagehead.HEADERS` sends `referrer-policy: no-referrer` on every HTML
> response, and the reason is written where it is set — a page reached from a QR
> sticker must not tell the next host which sticker somebody knelt over, because
> the referrer *is* the beacon. Right for that page, and it applied to the
> console too, which embeds other platforms' players. A player handed no
> referrer cannot check whether it may embed on the site it finds itself in, so
> it does not play, and what a person reads is the other platform's error code.
>
>     asked     does the page carry the header
>     mattered  does the thing inside the page still work
>
> `referrerPolicy` on the element overrides the document's policy for that one
> subresource, so the beacon pages keep `no-referrer` and the two players get
> `strict-origin-when-cross-origin`: the host, never the path. The platform
> learns the origin of an embed it is already serving, which the request itself
> told it, and learns it only when somebody presses play — until then there is
> no request at all. House-held footage was never affected; it is our own
> `<video>`, with no third party to satisfy, which is why the defect looked like
> one broken post rather than a broken feature.
>
> **The frame was never the screen.** From the beta: the deck swiped, and what
> it swiped between was still a card — a header above the frame, a caption below
> it, and the screen's own title above all of that, so the video got whatever
> height was left over, which on a phone is about half.
>
>     asked     can you swipe to the next one
>     mattered  is the one you are on the screen
>
> A pane holding footage is now the footage, and the words are on top of it: the
> media fills the pane absolutely and the pill, the position and the caption
> ride over it at the two edges, on scrims rather than panels, so nothing sits
> between the reader and the picture. The screen's own header is gone from this
> deck — its two lines moved onto the rules pane, which is the one that already
> explains what the feed is. A pane that is a room, a desk or a party has no
> frame to ride on and keeps the ordinary stacked layout, decided by the item's
> own kind rather than by whether a frame happened to load. Back and Next stay,
> on the bottom scrim, for the keyboard, the mouse and any gesture that does not
> land.
>
> ---
>
> Cut with JIM-mini 0.71.0 and PDI 0.71.0. Full local suite green over this tree.

## app-v0.70.1 — QRME app-v0.70.1

- Published: 2026-08-13
- Commit: `0c2ea9b19e76d212fcdabdad31d1073a83477a4f`
- Assets: 0
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.70.1>

> %23%23 The sandbox could lie about itself%0A%0AThe widget runner asked whether %2Aan%2A interpreter existed and never whether it was new enough. The filesystem wall is node%27s own permission model%2C which arrives in Node 20 %E2%80%94 so a host carrying Node 18 or 19 reported **ready**%2C lit the run button%2C and then failed every widget on a flag its author never typed.%0A%0AA binary that cannot build the wall is the missing-wall case wearing different clothes%2C and this module%27s promise is that it refuses rather than running with three walls instead of four. `MIN_NODE` is 20%2C the probe reads `node --version`%2C and an interpreter that will not say counts as too old %E2%80%94 every other reading ends with a lit button on a host where nothing runs. Its own refusal%2C in ten languages.%0A%0AThe floor is guarded by measurement rather than by a literal. `assert MIN_NODE %3E%3D 20` would be a number with nothing to compare it against %E2%80%94 20 is a fact about node%27s release history%2C which nothing in this repository can measure. So the guard asserts the consequence%3A the interpreter this host offers either passes the floor or does not%2C and either accepts the flag or does not%2C and those two answers have to agree. A floor lowered under an interpreter that rejects the flag fails%3B so does one raised above one that accepts it.%0A%0A%23%23 Who this is for%0A%0AFound on a live host%2C not in review. `app-v0.70.0` was tagged before this landed%2C so its installers carry the check that cannot see the version. If you run 0.70.0 on a machine with Node 18 or 19%2C Widgets will offer to run and fail%3B this release says so instead.%0A%0AA deployment with no interpreter at all %E2%80%94 which is every containerised one%2C where node lives in the build stage and not the runtime image %E2%80%94 is reported honestly by both%2C so nothing changes there.%0A%0ANothing else in this release.%0A%0A%2A%2A3424 tests passing.%2A%2A%0A%0AFull notes%3A %5BCHANGELOG.md%5D%28https%3A%2F%2Fgithub.com%2Fdavidsbianchi1984%2Fqrme%2Fblob%2Fmain%2FCHANGELOG.md%29

## app-v0.70.0 — QRME app-v0.70.0

- Published: 2026-08-13
- Commit: `44f3790c4d13531c403b17e2db455da100bab0c3`
- Assets: 0
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.70.0>

> ## Widgets — somebody's own code, in a box
>
> A widget is a function its author wrote, kept against their profile and run on the backend in a namespace with no interfaces, one readable directory, no child processes, a capped heap and a wall clock. Sixteen escape attempts run through the real runner prove the walls hold. If the network cut cannot be built on a host, the runner refuses to run anything at all rather than running with three walls instead of four. Six owner-scoped routes, a console screen, and a page on all three shells.
>
> ## An agent that edits somebody's own app
>
> Say what you want changed and it does it, through the same doors you would have used yourself. Its reach is a written allowlist of ten, and two guards make the list load-bearing: every row resolves against the app's own route table and every row that *changes* something must land on a door that demands the owner, and the profile is bound from the session rather than named by the model — so a model answering with somebody else's id does not move the request off the person driving it.
>
> `GET /studio/agent` publishes the ten sentences, so *what can this thing do to my account* can be read before it is used. What it did is listed under what it said — one line per door it went through — because an agent that describes an edit in prose is asking to be believed. The conversation stays on the client: the agent has no memory of its own, so *forget this* actually forgets. Nothing in its instructions names this machine, its paths, its environment or its sibling services.
>
> ## The Feed is a deck you swipe
>
> One item fills the screen and a swipe up brings the next, snapped by the browser's own scroll-snap rather than a gesture handler guessing from a wheel delta. Vertical footage fills the frame; horizontal is letterboxed rather than cropped into a shape nobody shot it in. Footage this deployment holds plays muted the moment its pane is in front of you, one decoder at a time; footage held elsewhere is a full-frame facade that waits for a press. `feed.autoplay` turns that off — off by default, kept on the device.
>
> ## Also in this release
>
> Turns are selected and struck or rewritten in place, with the edit recorded but never the old words. An export QR carries a single-use ten-minute ticket and never the owner token. The console's own CSP stopped blanking every video player. The failure reports come home to this backend. The extractor now reads a ternary's branches, which found nine English buttons on the screen a stranger meets.
>
> ## Fixed on the way through
>
> A memorial does not redecorate: the agent's turn and a widget's run both drove a profile without asking whether it may still act. The console's l10n table had stopped being readable in one place, and the Feed's own autoplay switch had fallen out of the audited set. Three wire names carried two shapes each.
>
> ## Running widgets
>
> A widget needs two things from the host: a way to cut the network (`unshare -rn`, i.e. unprivileged user namespaces), and Node 20 or newer — the filesystem wall is node's own permission model, which arrives in 20.
>
> `GET /studio/limits` reports whether the box can be built here and says which wall is missing when it cannot. On a containerised deployment there is usually no interpreter in the runtime image at all, so widgets report unavailable: the editor still opens and widgets can be written and kept, and the run button says why it will not press.
>
> **Known gap in this build:** the check asks whether an interpreter exists, not whether it is new enough, so a host carrying Node 18 or 19 reports ready and then fails every run. If that is you, take [app-v0.70.1](https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.70.1) instead — it is this release plus the version floor and nothing else. A deployment with no interpreter at all is reported honestly by both.
>
> **3421 tests passing.**
>
> Full notes: [CHANGELOG.md](https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md)

## app-v0.67.0 — 0.67.0 — The licence carries the substance

- Published: 2026-08-12
- Commit: `e956cadd94a308da0831a69abfb627f079d9805e`
- Assets: 0
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.67.0>

> A finetune or clone derive now hands the buyer the profile's substance — its own knowledge items, steering dials, appearance and demographics; a clone adds an aggregate adaptation summary (dimension means across every relationship, count only). Interactor messages and per-relationship embeddings, the voice print, vaulted content and marketplace pack items never travel, and every derivation writes a manifest of what crossed and what stayed, readable by both parties in the console and all three shells.
>
> Organizations can now lease somebody else's licensed specialist as a department: the fee accrues to the specialist's owner at seating time, the lease rides the owner's licences list beside grants, and a revoked lease — or a terminated source profile — leaves the desk standing but silent, named in every coordination it no longer speaks in.
>
> The portrait moves: the avatar response carries a motion block (still / breathe / lively) whose energy, warmth and tempo derive live from the interaction history, riding the same response as the AI badge. And a persona remembers the room: a turn without fresh environment context recalls the latest stored context within six hours, marked as remembered so clients can tell fresh from recalled.
>
> Full suite: 3320 passed.

## app-v0.66.0 — QRME app-v0.66.0

- Published: 2026-08-12
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.66.0>

> **QRME v0.66.0** — **cut in step.**
>
> No QRME code changed this round. The work was JIM-mini's offline coach stack — the add-and-norm pipeline over stored knowledge and current readings, the jampacked pack, the deposits paid model turns leave behind, and the curriculum JIM studies from. The three products are cut together, so one number names one combination of all three.
>
> **Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.65.0...app-v0.66.0

## app-v0.65.0 — QRME app-v0.65.0

- Published: 2026-08-12
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.65.0>

> **QRME v0.65.0** — **the rooms keep their word.**
>
> - **The door into a live room.** The lobby's pitch had promised "step in beside them" while every press opened a fresh, empty room. `POST /rooms/{room_id}/join` gives the promise behavior: eight seats, the same seat held on a second knock, "this room has closed" and "this room is full — eight seats, and every one taken" refused in the speaker's language. Join buttons on the console's live rows, and all three phones walk through the same door.
> - **A standing room is one place, not a stamp.** Pressing a standing room's name used to mint a copy of it — twelve presses of "The front porch" made twelve empty porches. `POST /rooms/templates/{key}/open` now joins the newest live room holding that topic when one has a free seat, and only opens it fresh when nobody has it open — with you and your profile in it. A full porch gets a second table. The response says which happened, and the console, iOS, Android and Windows each press through it.
> - **A face is a door to the person.** Tapping a friend's picture on the home screen landed on the list of friends; it now opens that friend's own page — portrait, tagline, about, links. Reported from the field, fixed the same day.
>
> **Full changelog:** https://github.com/davidsbianchi1984/qrme/blob/main/CHANGELOG.md
>
> ## What's Changed
> * The door into a live room by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/270
> * 0.65.0: the rooms keep their word, and the three cut together by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/271
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.64.0...app-v0.65.0

## app-v0.64.0 — QRME app-v0.64.0

- Published: 2026-08-12
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.64.0>

> Eight rounds since 0.63.0, cut as one.
>
> **The remembrance** — what a profile keeps of a person between conversations, distilled, carried into every reply, erased when the memory is. **The handed link** — paste a URL into the chat and the profile reads the page's public words before answering. **The pasted link connects the account** — the host names the platform, the path names the account, and a hashtag is refused with a sentence that explains itself. **The torso form** — an avatar can carry an upper-torso render; the talk overlay stands it at full figure, scaled 1:1 in the live feed. **Marketplace folders**, **top friends on the front page**, and **the vastscape** — watch-together on a TV, drawn as screens 194 and 195.
>
> **The connections catalog steps out** — the connected-apps card asks the forty-app catalog across six providers instead of offering one hardcoded button. **The standing rooms** — twelve blueprints at GET /rooms/templates, one press from real on the console and all three phones. **The footsteps** — how many people hold accounts, riding /health into every console's corner as an aggregate, in ten languages.
>
> Fixed: the vault hiccup no longer silences the chat; the </script> escape guard now has the test it always deserved, in all three suites; and **the login wall is not source material** — the social scrape recognises a platform's login page by its title and refuses in ten languages instead of feeding the wall's words into a profile's training. The chat also handed back its walls: presence rendering belongs to the rooms and the vastscape — a text thread is its own scene.
>
> ## What's Changed
> * Round 20: the link handed mid-conversation + the remembrance past the window by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/265
> * The catalog steps out, the rooms stand ready, the footsteps show by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/266
> * The chip shrinks to a footprint, and the chat hands back its walls by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/267
> * The login wall is not source material by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/268
> * 0.64.0: the tour comes home, and the three cut together by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/269
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.63.0...app-v0.64.0

## app-v0.63.0 — QRME app-v0.63.0

- Published: 2026-08-11
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.63.0>

> ### Added
>
> - **The chat follows the conversation.** The reply used to land below the
>   fold and stay there; the log now scrolls to the newest message as it
>   commits — an effect keyed to the messages themselves rather than a
>   callback racing the render — and an approved profile's replies are
>   spoken aloud while talk mode is open, through the same approved-only
>   speech gate the speaker toggle uses.
> - **The talk surface shows the face.** The microphone was a button that
>   filled the composer; it now opens a full-screen talk surface with the
>   profile's portrait front and centre, pulsing while it listens, the
>   transcript shown as it is heard, the reply spoken back. The sibling
>   product's Guardian is a voice with no face, so its surface is an orb;
>   a synthetic profile is a persona, and a persona has a face. The orb
>   appears only for a profile with no portrait yet, next to a pointer at
>   where to get one.
> - **The avatar deck.** Identity's portrait card becomes a deck with
>   three shelves. *Pick a character*: the starter portraits as a tappable
>   grid — the asset path comes from the brief itself, because the server
>   names where its portraits live and the client never spells a path.
>   *Your own face*: import a photo through the existing media door, or
>   capture it with the camera from five angles — front, left, right, up,
>   down — every frame uploaded and kept as provenance, the front frame
>   becoming the portrait. *An avatar you already have*: Ready Player Me,
>   Bitmoji, Meta Avatars, Apple Memoji, Xbox, ZEPETO, Mii — imports, not
>   integrations: the person exports on the provider's own surface and
>   hands QRME the image; nothing calls a provider API or holds a provider
>   credential, and the provider's license keeps governing the avatar.
>   `GET /avatars/market` lists the shelf with the how-to for every
>   source; `POST /profiles/{id}/avatar/import` (owner-only) sets the
>   portrait through the same pipeline as a starter face — the AI badge
>   and the likeness record ride on the render — and writes the import
>   onto the profile's record as a source item. Doors on the console and
>   all three native shells.
> - **The imported link, finally visited.** A social connection has
>   carried the account's public address since the day it was pasted, and
>   the profile only ever knew the handle. `POST /social/{cid}/scrape`
>   goes to the address and keeps what a browser would show anybody — the
>   title, the metadata bio, the visible text — as a source item on the
>   profile's own record, provenance written in. An offline deployment
>   refuses before any socket opens; the gate lives inside the fetcher
>   itself, so a second caller added tomorrow inherits the check.
>
> ### Fixed
>
> - **The console fits the phone it runs on.** Two layout defects, one
>   root: a grid item refuses to shrink below its content, so the content
>   pane grew past its track, the app overflowed the viewport, and the
>   page itself half-scrolled instead of the pane. `min-height` and
>   `min-width` zero let the tracks clamp; the app height tracks `100dvh`
>   where the browser has it, so the bottom row sits above the URL bar;
>   the sidebar scrolls on its own where a landscape phone gets the
>   desktop column; the onboarding card no longer overflows a narrow
>   screen. The same defect was in all three consoles and is fixed in all
>   three.
>
> ## What's Changed
> * Round 18: the chat follows the conversation, gains a voice, and visits the link it imports by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/263
> * Round 19: the talk surface shows the face, the face has a deck + 0.63.0 cut by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/264
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.62.0...app-v0.63.0

## app-v0.62.0 — QRME app-v0.62.0

- Published: 2026-08-11
- Commit: `e6bad34bc1e17dcbd69d62a6dd49ba2c709f96b3`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.62.0>

> ### Version alignment
>
> The three products are cut together, so one number names one combination
> of all three. JIM's phones reached parity with its console — eleven rounds in one branch: every backend route gained a door on iOS, Android and Windows (the doorless ledgers close at the four by-design rows), the voice pair landed on all three shells with the device's own voice as fallback, Android learned to say PATCH through a test-pinned override, and the most-touched screens swapped their English for the ten-language tables. No QRME code changed.
>
> ## What's Changed
> * 0.62.0: cut together at one version by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/262
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.61.1...app-v0.62.0

## app-v0.61.1 — QRME app-v0.61.1

- Published: 2026-08-11
- Commit: `51b2018feaec009d1302623d1cd280fa37361a97`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.61.1>

> **Ability is not a gate.** An accessibility statement with a door under it, on every client: the console's Accessibility screen — reachable before sign-in via `#access` — names the needs this product is built for (blind, deaf, mute, motor, cognitive, dyslexia, motion sensitivity), and under it sit three questions: what were you trying to do, what stood in the way, what would help. `POST /access/reports` takes those answers with no account, no token and no name — the table has no identity column to fill — seals them to the PDI vault when one is configured, and reads them back only under the deployment's reviewer token. The iOS, Android and Windows shells carry the same statement and form.
>
> The wall's uploads say what they show: the composer asks for a description, and it returns on every read as the image's alt. The chat log is an aria-live region, so a screen reader hears the reply arrive. The known-gaps ledger (`tests/a11y_backlog.txt`) opened at three admitted barriers and closes at zero, every closure held by a test — one shared across the three products, taking the common guard manifest to 461.
>
> Signup opens for the beta: `QRME_SIGNUP_KEY` gains a keyhole — set, it gates signup with an invite key; empty, signup is open, which is the shipped default. Free tiers stand while testing lasts, and Terms 1.2 says all of this in the no-claims-without-behavior voice.
>
> Cut together with JIM-mini and PDI at 0.61.1. Suite: 3262 passed.
>
> ## What's Changed
> * The gate gets a keyhole, plans go free, and the terms say beta by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/257
> * The door defaults open: signup keys become optional in the beta compose file by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/258
> * Ability is not a gate: the accessibility statement, behavior, guards and report door by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/259
> * The backlog the statement promised, run to zero by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/260
> * 0.61.1: cut together at one version by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/261
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.61.0...app-v0.61.1

## app-v0.61.0 — QRME app-v0.61.0

- Published: 2026-08-10
- Commit: `dcfea6f20b602f2172abef7fa85d67d19ed72948`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.61.0>

> ### Fixed
>
> - **The console was blanked by its own Content-Security-Policy.** The nonce
>   policy written for the server-rendered pages was stamped on every HTML
>   response — including the console's `index.html`, whose script and stylesheet
>   are external files no per-response nonce can reach. A browser refused the
>   bundle and rendered a dark, empty page: HTML 200, nothing running. That is
>   what the first real deployment served on all three domains, while every
>   in-process test passed, because a `TestClient` reads the policy and enforces
>   none of it. `pagehead.console_policy` now names `'self'` where the page
>   policy names a nonce — still refusing inline script — and the over-HTTP
>   suite builds its own console dist so the measurement runs on CI whether or
>   not `app/` was built.
> - **The release-bodies sweep could not start, and then measured the fetch.**
>   An edit had left its embedded Python unparseable, so every scheduled run
>   died before deciding anything — in a place no interpreter, linter or test
>   reads. Repaired, its first honest run accused the kept `app-v0.24.0` of
>   losing a frozen body it visibly still carries: paginated output was re-split
>   by a regex that matched a `]` `[` pair inside a release body's own markdown,
>   and dropped what it broke. `gh api --slurp` now returns pagination as one
>   JSON document, a guard proves the fetch returned every release the record
>   names, and two local tests hold the line: the workflows' scripts must parse,
>   and the staleness decision is driven with this product's own frozen opening.
>
> ### Added
>
> - **The beta topology.** `docker/beta-compose.yml`, `docker/beta.Caddyfile`
>   and `docs/beta-deploy.md`: the three products and the shared gateway behind
>   one reverse proxy on one host, real secrets from a single `.env` that fails
>   closed on any missing value, certificates obtained and renewed unattended.
>   First stood up on a real host this release, which is how the console
>   blanking above was found.
> - **The front door.** The bare domain answered `{"detail": "Not Found"}`,
>   because the console lives under `/app` and nothing said so. `/` now
>   redirects to `/app/` whenever a console is mounted — headless deployments
>   keep their honest 404.
> - **Nightly backups, running rather than written down.** A `backup` service
>   takes a `sqlite3 .backup` of each database and a copy of the collector
>   ledger into `/root/backups` daily, keeping fourteen days. The copies do not
>   leave the host, and the deploy doc says so.
> - **Bootstrap is idempotent by validation.** A saved PDI tenant token the
>   vault still honours is kept; minting happens only when there is none or it
>   is refused — so a restart reuses the first tenant instead of abandoning its
>   sealed records.
>
> ## What's Changed
> * The console the policy blanked by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/253
> * The checker that could not start, and the copies that finally run by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/254
> * The sweep measured the fetch, not the releases by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/255
> * 0.61.0: the beta stands up by @davidsbianchi1984 in https://github.com/davidsbianchi1984/qrme/pull/256
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.60.9...app-v0.61.0

## app-v0.60.9 — QRME app-v0.60.9

- Published: 2026-08-10
- Commit: `cbccca979bdf5c406d5b743e787ea284331fcd0a`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.60.9>

> No change to this product.
>
> The release-body work reaches its end, and both findings apply here.
>
> ## The record reaches zero
>
> Every release that inherited the frozen v0.24.0 body has been rebuilt from its own CHANGELOG entry. `stale_release_bodies.txt` reaches a ceiling of **0** with `app-v0.24.0` kept deliberately — its body *is* the v0.24.0 notes and is correct for it, so it moved out of the count rather than out of the file.
>
>     asked     how many rows are left
>     mattered  how many releases are still wrong
>
> ## Three checks that reported success while doing nothing
>
> A staleness test keyed to a sentinel that was one product's number, so this product's sweep read zero stale while a hundred and twelve releases remained wrong. A backfill that trusted the record instead of the releases, spending three runs rewriting work already done. And a record guard whose header pattern required a plural and crashed when the count reached one.
>
> All three are fixed. `generate_release_notes` is settled too: 0.60.8 published with a curated body and the body came back intact.
>
> ---
>
> Suites: QRME 3242 passed, 1 skipped · JIM-mini 1748 passed, 3 skipped · PDI 1091 passed, 5 skipped.
>
> **Full Changelog**: https://github.com/davidsbianchi1984/qrme/compare/app-v0.60.8...app-v0.60.9

## app-v0.60.8 — QRME app-v0.60.8

- Published: 2026-08-10
- Commit: `fdfa655c656d54252ebd04aed75770d10ee8f6e2`
- Assets: 0
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.60.8>

> No change to this product.
>
> Two findings carried from PDI's round, both of which apply here.
>
> ## A release checklist that names its fields
>
> 0.60.7 was bumped from a prose list that named Android's two version fields and left iOS's unnamed — and a build code shares no characters with the marketing version it belongs to. `release_fields.txt` replaces it: byte-identical in all three products, thirteen rows, each naming its file, field, shape and locator. Three guards read it rather than trusting that anybody did.
>
> ## The release body had three sources and no reader
>
> 412 of 530 published releases across the three products carried the same v0.24.0 prose, because `RELEASE_NOTES.md` was published verbatim over every curated release body since v0.24.0. It and `sync-release-notes.yml` are deleted; `release-integrity.yml` replaces them, and reads rather than writes.
>
> PDI's console also reached a floor of zero — thirty-two strings across its last six screens, and a record that is no longer a backlog.
>
> ---
>
> Suites: QRME 3238 passed, 1 skipped · JIM-mini 1744 passed, 3 skipped · PDI 1087 passed, 5 skipped.

## app-v0.60.7 — QRME app-v0.60.7

- Published: 2026-08-10
- Commit: `1dc75d6e163410625e07b3926056e7714a52141b`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.60.7>

> ### No change to this product
>
> PDI's console round: the finding that a screen importing the translator is not
> a translated screen. Two of its screens had been counted as localized since
> 0.48.3 while still holding fifteen English strings between them, six of which
> were strings its table already carried in all ten languages. A guard now holds
> the claim that a screen asking the table for a word may not also hard-code
> one, and five further screens were localized. 91 → 32.
>
> Recorded here only to keep the three changelogs in step at one version.

## app-v0.60.6 — QRME app-v0.60.6

- Published: 2026-08-09
- Commit: `f9aaa876e8334fbc861fbb36ff70b5db44b1e680`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.60.6>

> ### No change to this product
>
> PDI's console round: Positions and Bridges localized, and its English count
> corrected a third time — the reader asked for a letter, a space and a letter,
> which no heading joined by `&amp;` or a hyphen has. 154 → 168 → 91. Recorded
> here only to keep the three changelogs in step at one version.
>
> The portable part is the shape rather than the code. This product's console
> reader records every extracted string verbatim in both directions, so it has no
> phrase test to be wrong about; the defect could not occur here. That is worth
> stating rather than assuming, which is why it was checked before the round was
> called PDI-only.

## app-v0.60.5 — QRME app-v0.60.5

- Published: 2026-08-09
- Commit: `38beb853c5fb8818b94fcb976409a4573878fa82`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.60.5>

> ### No change to this product
>
> PDI's console round: Carriers and Exchange localized, 225 → 154, on the
> honest count 0.60.4 established. Recorded here only to keep the three
> changelogs in step at one version.
>
> One thing in it belongs to all three. Two guards in that product still greped
> their screens for English sentences, and localizing the screens turned them
> red — the 0.48.2 lesson, *localizing a screen blinds the guards that grep it*,
> arriving in the last two guards that had not had it. Both now follow the
> sentence to wherever it lives rather than asserting the English is in the
> file. Worth a look here the next time a screen in this product moves its words
> into a table.

## app-v0.60.4 — QRME app-v0.60.4

- Published: 2026-08-09
- Commit: `6bd2059204497511e3b8c9ef9c47981c172b744a`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.60.4>

> ### The reader this product already had turned out to be the one that was right
>
> No change to this product. The round was PDI's, and it is recorded here
> because the finding is about a method all three share.
>
> PDI read its console's English with three regexes, the first being
> `>\s*([A-Z][^<>{}\n]{2,})\s*<`. This product moved off that shape rounds ago
> to `app/scripts/jsx-text.mjs`, which parses with TypeScript's own parser and
> returns every `JsxText` node. Nobody had run the two side by side until now.
>
>     asked     how much English does this pattern match
>     mattered  how much English does a person read
>
> **233 against 177**: a quarter of PDI's console prose was invisible to it —
> every wrapped sentence, every sentence with a value interpolated into the
> middle, every phrase not starting with a capital. Hidden in the direction that
> makes a ratchet look satisfied, and two of that product's localization rounds
> were graded against the low number.
>
> The lesson is not about regexes. It is that two products can carry the same
> guard by name and not by reach, and the only thing that finds it is running
> both readers over the same file and comparing. `shared_guards.txt` says the
> three suites ask the same questions; it cannot say they answer them as well.

## app-v0.60.3 — QRME app-v0.60.3

- Published: 2026-08-09
- Commit: `6310068e42c790be819f9df60c7d17c9003278a3`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.60.3>

> ### A check that cannot fail before the merge is not a check
>
> 0.60.2 found `native.yml` red for a hundred and twenty-three consecutive runs.
> Nothing was wrong with what it ran. What was wrong was *when*: it fired on
> `pull_request`, which never opens here because releases are fast-forward
> merges, and on `push` to `main`, which happens after somebody has decided to
> ship.
>
> `ci.yml` carried the identical trigger. It had been red for twenty-nine
> consecutive runs.
>
>     asked     does the workflow pass
>     mattered  can the workflow's answer still change the decision
>
> - **The four red guards.** They shell out to `app/scripts/jsx-text.mjs`, a
>   TypeScript-AST reader used because three separate regexes over the same
>   source each hid real strings. It imports `typescript` from the app's own
>   `node_modules`, which the job running pytest never installed. Those guards
>   are written to fail loudly rather than report a comfortable zero, and that
>   is exactly what they did — into a log nothing read. The job installs the
>   app's dependencies now.
> - **The trigger** is any branch push, the same fix `native.yml` got.
> - **`test_a_check_that_cannot_fail_before_the_merge.py`** reads the checked-in
>   triggers and fails when a gating workflow cannot fire before a merge. Three
>   workflows are deliberately post-merge — the container e2e run and the two
>   that fire on a release tag — and each is named in `POST_MERGE` with its
>   reason. Naming one is a decision; the failure this exists for was nobody
>   having made the decision at all. A named exception for a deleted workflow
>   fails too: the exemption must not outlive its reason.
>
>   It cannot tell whether a workflow is passing. It can tell whether a failure
>   would arrive in time to matter, which is the part that was missing.

## app-v0.60.2 — QRME app-v0.60.2

- Published: 2026-08-09
- Commit: `c5eaa3f3395f050d3365a0da99e8061145cb2820`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.60.2>

> ### The compiler was in the room the whole time and nothing listened
>
> `native.yml` builds the Swift, Kotlin and C# shells on three runners. It had
> been failing for 123 consecutive runs and no part of the loop read it: the
> workflow fired on `pull_request`, which never opens here because releases are
> fast-forward merges, and on `push` to `main`, which happens *after* the
> decision to ship. The trigger is any branch push now, and the result is the
> first green board this repo has ever had.
>
>     asked     do the shells read the members they name
>     mattered  do the shells compile
>
> Everything below was found by a compiler, not by reading.
>
> - **The Android shell could not be built at all.** `L10n.kt` is one `mapOf`
>   of 1,125 rows, which compiles into the object's static initializer, and the
>   JVM caps a single method at 64 KB. Past that there is no diagnostic to act
>   on — codegen fails with `Method too large` and no class is emitted. The
>   table is twelve functions now, joined by `table`
> - **Half of `ApiClient` was not in `ApiClient`.** 944 lines — friends, the
>   wall, the audience verbs, watch parties, skill grants, exchanges — sat
>   inside `record PackInstalled`'s body, where they could not see `Send`,
>   `Get` or `Post`, and where `PeoplePage` could not see them. A record body
>   is legal C#, so the file parsed; thirty methods the pages call did not
>   exist
> - **A defaulted parameter in the middle of a record's list** silently
>   swallows the last argument of every positional call. `WatermarkRecovery`
>   lost `method`; `ObjectionOpened` lost `note`
> - `AppState.kt` carried `private set` twice, a syntax error that hid every
>   member declared after it
> - `deskCardOf` built a seven-field shape out of a seventeen-field record and
>   had no caller left; `BeaconCameraSurface` read a `lang` it never took;
>   `Problems.send()` required an `appVersion` its caller does not pass
> - Names that were never there: `RevokeOut.Revoked` (it is `RevokedCount`),
>   `MicVocabularyOut.widths`, `WearableBoard.kinds`, `TutorialProgress.Next`,
>   `RosterSibling.Id`, a fifth `Api.shared` where the client is `ApiClient`
> - `AttestButton` and `BlockedNote` are `x:Name`d inside a `DataTemplate`,
>   which mints no code-behind field, so the localizer was setting text on
>   nothing. Both labels ride on the row now
> - Two `using` lists and one import list that did not ask for what the file
>   reaches for; two iOS calls that passed `query:` before `token:`; one
>   timeline row of five chained string operands the type checker gave up on
>
> Both C# record readers in `tests/` now end a record where C# does — at `);`,
> or at `)` before a body — after the move above took away the accident that
> had been hiding a bug in them.

## app-v0.60.1 — QRME app-v0.60.1

- Published: 2026-08-09
- Commit: `4367a64fffb1730fbbee52cb34de05dfa1142a9f`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.60.1>

> ### A fix to the cascade fixes the next delete, not the last one
>
> 0.59.9 derived the profile delete from the schema. Every profile ended
> *before* that release was ended by a list of twenty-four table names against a
> schema of sixty-six, and the forty-two tables it missed are still sitting in
> every deployment that has been running since.
>
> Nothing in the product will ever look at them again, and that is the whole
> problem. The `profiles` row is gone, so the API answers 404, so no code path
> visits those rows — not visible, not reachable, still there.
>
>     asked     does the delete work now
>     mattered  what did it leave the last time it did not
>
> ### Added
>
> - `python -m qrme.orphans` — a one-off maintenance sweep for the residue.
>   `survey()` reads and the command is **dry by default**; `--apply` is the
>   only thing that deletes, and `--json` gives the same survey machine-readable.
> - Its scope is the cascade's own reader (`common.profile_scoped_tables()`
>   minus `common.ERASE_KEEPS`) rather than a second list — this is that cascade
>   applied retroactively, and two readers of *which tables hold a profile's
>   data* is two things to keep in step.
> - A row counts as an orphan only when its `profile_id` names a profile not in
>   `profiles`. Rows with a NULL or empty subject are left alone: they are not
>   the residue of a deleted profile, and a command written for one problem does
>   not get to decide about a different one.
> - `test_what_the_old_cascade_left_behind.py`. The sharp property is not *does
>   it find the orphans* but **does it leave a living profile alone**, checked
>   with a live profile seeded beside the stranded one. Both directions were
>   confirmed by injection: a broken liveness filter reports 56 tables of a
>   living account's data, and a hand-written scope reports 52 tables the survey
>   cannot see.
>
> ### Fixed
>
> - `test_the_member_that_isnt_there.py` read `AppState.Current.X` only when a
>   page spelled it out in full. A page that puts the singleton in a local first
>   — `var st = AppState.Current;` then `st.Uid` — was read as reaching for
>   nothing at all, and a row's floor stayed comfortably met on the call sites
>   it *could* see. Aliases are now expanded, and **only** when the name is
>   bound to that singleton and nothing else anywhere in the file: the first cut
>   rewrote whole files and reported twenty-eight perfectly real members as
>   missing, which is the failure mode this guard's own docstring is about.

## app-v0.60.0 — QRME app-v0.60.0

- Published: 2026-08-09
- Commit: `be44d19f4cb3afe5c4ed2721d8b8261d4287e573`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.60.0>

> ### An export is measured against the schema too — and drops the credentials
>
> 0.59.9 derived the **erase** from the schema in all three products, because the
> lists that stood in for it had gone stale: an operation advertised as *every
> trace* reached a third of the tables. The export is the same question turned
> round.
>
>     asked     can a person delete everything we hold
>     mattered  can a person see everything we hold
>
> ### What it was
>
> `GET /profiles/{id}/export` says *full data export — access everything,
> anytime (You Own It)*. The README's capability table points at it under **You
> own it / total control**. The suite gateway's GDPR Article 20 bundle is built
> on it — the tandem's whole answer to *give me my data*.
>
> It returned **six tables of sixty-six**: the profile, its sources,
> relationships, messages, engagement, posts and surfaces. The clinical notes and
> the media behind them, the watermarks tying a rendered likeness back to a
> person, the homepage, the friendships, the inbox — none of it was in the file
> somebody downloaded to see what we have.
>
> ### Two properties, and the second is not the first
>
> An export must be **complete** and must **not hand back a live credential**.
> Those pull in opposite directions, and the honest resolution is per column
> rather than per table: a row is the person's own history, and a token inside it
> is a credential in whatever they do with the file — a bundle gets downloaded,
> mailed to a clinician, dropped in a cloud folder.
>
> The redaction is a **rule** rather than a list, and that is not tidiness. The
> first cut was a list of exact column names, and the new guard caught it on its
> first run — three credential columns in tables the export now reaches, none of
> them in the list. A list of columns goes stale exactly the way the cascade's
> list of tables did.
>
> Deliberately *not* the bare word `hash`: a hash-linked audit record is what a
> person verifies their own export with, and a credential is what somebody can
> present. The two are not the same and the rule says so.
>
> ### The symmetry, asserted
>
> A table the erase clears and the export omits is a person who can delete
> something they were never shown. A table the export carries and the erase
> misses is 0.59.9's defect. The guard compares the two sets directly.
>
> There is one deliberate asymmetry, and only in the vault: its audit chain
> survives a wipe because it is the proof the wipe happened, and a bequest is
> *retired* rather than deleted so an heir's credential fails with **revoked**
> instead of silence. Both are still the tenant's to read, so the export carries
> what the erase keeps — the one place these two answers differ on purpose.

## app-v0.59.9 — QRME app-v0.59.9

- Published: 2026-08-09
- Commit: `39df070483f7327e7b6b84c5538eb2921de7018f`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.59.9>

> ### An erase is measured against the schema, not against a list somebody wrote
>
> `DELETE /profiles/{id}` says *delete the profile and every trace of it —
> anytime*. It named twenty-four tables in a tuple. This schema has **sixty-six**
> with a `profile_id` column, so the delete left forty-two standing:
>
>     anonymous_pictures   clinical_notes   media          media_watermarks
>     homepages            friendships      inbox_events   displays
>     embodiments          excursions       campaigns      game_sessions
>     departments          delegated_workflows             environment_context
>     …and twenty-eight more
>
> `clinical_notes` and `media` are the sharp ones: a clinical note and the
> photographs behind it, belonging to a profile the API answers 404 for.
> `media_watermarks` is the identifier tying a rendered likeness back to the
> person it was made from.
>
> The sibling vault had already fixed this shape and the fix had not travelled.
> Its docstring already said the general thing: *a migration that adds a table
> is covered by writing it, not by remembering this function.*
>
>     asked     did we delete what the handler names
>     mattered  did we delete what the schema holds
>
> ### Why the list kept losing
>
> It was not neglect. Both siblings' lists had been *corrected*, more than once,
> and every correction was right. JIM-mini's most recent one found a watch
> channel outliving its account and added three tables — `watch_channels`,
> `contribution_log`, `waivers` — because those three carried a live credential
> rather than a record. That fix was correct and did nothing about the next
> table, and `crash_watches` and `vigils` are the same kind of row and were
> still standing after it.
>
> A list is a claim about a schema, made once, by somebody who could see the
> schema that day.
>
> ### How it is checked
>
> By writing a row into **every** scoped table, erasing, and looking. Not by
> exercising features until rows appear: the tables a test can reach through the
> API are the tables somebody thought to wire, which is the same blind spot as
> the list. The rows are synthetic and go in through SQL — the question is
> whether the cascade reaches a table, and a row is a row.
>
> Plus the structural half, which is the part that survives the next migration:
> the handler must not carry a list of table names at all, and must ask the
> schema.
>
> ### The test does not borrow the reader it is checking
>
> The first cut planted rows in the cascade's own table reader. Narrowing the
> cascade narrowed the planting with it, so injecting the old hand-written list
> reported *a blind reader* rather than *forty-odd surviving tables*. It reads
> the schema itself now, and the injection names every table by name.

## app-v0.59.8 — QRME app-v0.59.8

- Published: 2026-08-08
- Commit: `a5bfee0134e7013f57eb1ab8370424d980fbc1fb`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.59.8>

> ### The check that covered one client of four
>
> 0.59.7 asked whether the shape a screen declares is the shape its route
> answers with, found two screens throwing `.map is not a function` during
> render, and asked the question of **the console alone**. The three native
> shells decode the same answers into their own types, and a wrong one there is
> the same failure with a different stack trace: `JSONArray` on an object throws
> exactly like `.map` on one.
>
> *No disagreement* from a check that was never run reads exactly like *no
> disagreement* from a check that passed. That sentence is most of this arc.
>
> ### What each client says, and where
>
>     console   req<T>(…)                     the generic
>     ios       let x: T = try await request  the annotated decode
>     windows   Send<T>(…)                    the generic
>     android   JSONObject(body) / JSONArray  the parse itself
>
> Android is the one worth reading twice: Kotlin has no decode type at these
> call sites, so the *parse* is the claim being checked.
>
> ### What it found
>
> No disagreements — the three shells were already right. What it found instead
> was how unevenly the clients can be read at all:
>
>     console 422   iOS 300   Android 316   Windows 342
>
> JIM-mini's Android shell names a shape on **three calls out of a hundred and
> fourteen**, because it discards the body on the rest. That is not a reader
> failing; a client that never reads an answer cannot be wrong about one. But
> three and three hundred cannot share a floor, so the per-client reach is a
> **record that must not go down** rather than a number chosen by hand — the
> same instrument the estate uses everywhere a count is honest but lopsided.
>
> ### Two readers this round got wrong first
>
> Both are kept as prose beside the code that fixes them, because both reported
> *clean*:
>
> * a Swift `[K: V]` dictionary counted as a list, because both spellings start
>   with a bracket — three false disagreements;
> * the Windows shell spells its verb `Post(…)`, not `HttpMethod.Post`, so
>   twenty-one calls defaulted to GET and every one was reported wrong.
>
> Injections confirmed red before the round closed: a `GameSession[]` narrowed
> to `GameSession` is named by client, file, route and declared type; and a
> single character removed from the Android reader drops its reach from 316 to
> 310 and fails on the record rather than passing quietly.

## app-v0.59.7 — QRME app-v0.59.7

- Published: 2026-08-08
- Commit: `53c89bba0a28a48d7bfcc0648025b8937b53dee4`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.59.7>

> ### `req<T>` is a cast, and a cast is a claim about the server nothing checks
>
> 0.59.6 read the requirement out of the application — which headers a route
> needs — and asked whether the callers could meet it. This is the same question
> pointed the other way: the route **answers** with a shape, the screen
> **declares** one, and between them sits `req<T>`, which is a TypeScript cast
> over a body parsed by `JSON.parse`. The compiler is satisfied. The screen
> crashes.
>
>     asked     does this call compile
>     mattered  is the shape it names the shape that arrives
>
> ### What it was, next door
>
> PDI's `GET /hosting/{tenant_id}/history` answers an object, and its Custody
> screen called `.map` on it — `TypeError: history.map is not a function`,
> thrown during render, on any vault that had ever been moved. JIM-mini had the
> same on `GET /users/{uid}/referral/clinicians`.
>
> This console agrees with its backend on all **422** typed calls, and the one
> place it hedges names both shapes on purpose.
>
> ### Why nothing else covers it
>
> The route audit asks whether a path resolves and a method is accepted. The
> door audit asks whether a route has a screen. Both were fully satisfied: the
> path resolved, the method matched, the screen existed and called it. Nothing
> asked what came back. `tsc` cannot help either, and that is structural rather
> than an oversight — `req<T>` is generic over a type the caller supplies, and
> the parsed body is `any`.
>
> ### The reader, and its own blind spot
>
> Per **call expression**, not per path. The first cut keyed on the path literal
> and reported sixty-odd disagreements, every one of them the reader pairing a
> `POST` with the `GET` that shares its path; reading each `req<T>(…)` call and
> taking the verb from that call's own body dropped it to one per product, and
> all of those were real.
>
> Before that, an earlier cut read **zero** call sites — its pattern stopped one
> character short of the opening backtick — and reported that the consoles
> agreed with their backends everywhere. It was right about every call it looked
> at, because it looked at none. That is why this file carries a registered
> floor (`console.calls_typed`) rather than trusting its own silence, and why
> the verb reader is asserted per verb.
>
> A union naming both shapes satisfies either: a client that copes with what
> arrives is defensive rather than wrong.

## app-v0.59.6 — QRME app-v0.59.6

- Published: 2026-08-08
- Commit: `bd96756fd5ba882744f83943c32a57a50918bde9`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.59.6>

> ### The clients agreed with each other, and they were all wrong
>
> 0.58.0 asked whether the three shells sent every header the console sent, found
> `x-llm-api-key` in one client and no other, and fixed it. It has held since.
> This round found what it cannot see.
>
> **Parity is a relative check, and a relative check is satisfied by everybody
> being equally wrong.**
>
> The instance is PDI's and the shape is the estate's: a vault under customer
> custody required `x-tenant-key` on every record route, and no client in that
> product sent it outside two heir routes. The comparison passed the whole time,
> because both sides of it were wrong in the same direction — which is exactly
> the case a comparison cannot report.
>
> This product has no such header today. The guard is here anyway, because the
> question is not about that header, and a guard that arrives after the second
> instance is a guard that was written twice.
>
>     asked     do the clients send the same headers as each other
>     mattered  do the clients send the headers the routes require
>
> ### The guard, in all three suites
>
> `test_a_header_a_route_needs_is_a_header_its_callers_send.py` reads the
> requirement out of the **application** rather than out of any client. FastAPI
> already resolves each route's header parameters through its whole dependency
> tree, so a header required by an auth dependency is attributed to every route
> that depends on it — the case a reader of function signatures misses entirely.
> Then, per client, per route that client actually calls: can it present what
> that route requires?
>
> A header set in a client's shared dispatcher rides every request. A header set
> beside one call rides that call. The first cut of this guard counted the two as
> one, and that alone let the console pass on a header it sends to two routes out
> of the eighty that need it.
>
> The half no dependency walk can reach — a header taken straight off the request
> inside a handler — is asked as a product-wide question, because the attribution
> is genuinely unavailable. `x-signup-key` is recorded there with its reason: an
> operator who sets it is closing registration to everybody, and a client able to
> present it would reopen the door the operator shut.
>
> ### Liveness without a number
>
> The three products lean on the two readers in opposite proportions — 103 routes
> declare a header in one and a single route does in another — so a floor per
> product would be three numbers to keep honest. The question is asked the other
> way instead: every non-transport header a client sends must be one some reader
> here found. A client sending a header no reader knows about is either talking
> to itself or looking at a reader that has gone blind.

## app-v0.59.5 — QRME app-v0.59.5

- Published: 2026-08-08
- Commit: `520e5bd767e15b9191da3d4f1e87e48705fa7bec`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.59.5>

> ### A value inside a script is not markup, and neither escaper knows both
>
> 0.59.3 shipped a Content-Security-Policy with a nonce and called it the second
> line of defence. 0.59.4 made the first line — escaping into HTML — a guard.
> This is the third sink, and it is the one where **both of those miss.**
>
> Inside a `<script>` element the HTML parser ends the element at the first
> `</script`, whatever the JavaScript quoting says. A value carrying `</script>`
> closes the script early and everything after it is parsed as markup — in the
> page's own nonced script, which the policy exists to permit.
>
>     json.dumps    escapes what would end a JavaScript *string*  — not the element
>     html.escape   escapes what would open an HTML *tag*         — not a JS string
>
>     asked     is the value a valid JavaScript string
>     mattered  can the value end the script element
>
> This product's `_js` composed both correctly. JIM-mini's and PDI's were bare
> `json.dumps`. A helper written once and copied into three
> repositories, where the copy that drifted is the one whose entire job is to be
> safe — the shape 0.59.0 found in a floor and 0.59.1 in a guard, now in a
> security primitive.
>
> **Not currently reachable.** Every value passing through these helpers is a
> database identifier or a translated constant, and a path segment cannot carry
> `</script>` because the slash breaks routing before the page is built. A
> latent hole, fixed anyway: the next value somebody escapes with it is exactly
> the one it was written for.
>
> ### One primitive, and a whitelist checked rather than trusted
>
> `_js_literal` is now the single place that knows what ends a script element,
> and `_js` and the string table are both built on it. Two helpers escaping for
> the same sink is two chances to drift, and they had already taken one each.
>
> The guard's own first draft is worth recording. Its call-site check allows a
> value through if it arrives via `_js(` or `_strings(` — and when that was
> written, one product's `_strings` was a bare `json.dumps`. **The guard would
> have excused, by name, precisely the defect it exists to catch.** A whitelist
> is a claim about behaviour; it is checked as one now.
>
> ### The consoles, swept and clean
>
> The same question in TypeScript is `dangerouslySetInnerHTML`, `innerHTML =`,
> `document.write`, `eval` and `new Function`. All three consoles have none of
> them. The community wall's linkifier was read too: it splits on `https?://`
> and gates on `startsWith("http")`, so a `javascript:` scheme cannot reach an
> `href`.
>
> That is a floor rather than a backlog — nothing to pay down, and the cheapest
> time to keep it that way is while it is still true.
>
> ### Also
>
> - Versions moved to 0.59.5 across the console, the backend, and the iOS,
>   Android and Windows projects (build 59005).
> - `shared_guards.txt` regenerated at 405 names; the divergence record holds at
>   136.

## app-v0.59.4 — QRME app-v0.59.4

- Published: 2026-08-08
- Commit: `a74b83e1255adc8b57cd11ef907b821387a0dada`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.59.4>

> ### The sweep that found the last one, kept
>
> 0.59.3 found reflected cross-site scripting on the sign-in callback by walking
> every f-string that builds markup — **by hand, once, and then throwing the
> walk away.** That round shipped the second line of defence, a
> Content-Security-Policy with a nonce, and left the first one unguarded.
>
> Escaping is the first line. So the walk is a guard now.
>
>     asked     is this page correct
>     mattered  can the next value somebody interpolates be markup
>
> ### Following the escape rather than looking for it
>
> Most of this estate escapes one line above the template:
>
>     ref = html.escape(card["reference"])
>     body = f'<p class="ref">{ref}</p>'
>
> A sweep that only asks whether `html.escape` appears between the braces
> reports **32 rows** here, of which the six real ones are buried. Following
> single assignments, and functions whose every return is escaped, and
> conditionals and joins whose every branch is safe, cuts it to **8** — and all
> eight are composites the analysis cannot follow rather than values a reader
> supplies. A record that is four-fifths noise is a record nobody reads.
>
> It also refuses to read prose as markup. The first draft matched any f-string
> containing `<` and `>`, which flagged a WebAuthn diagnostic containing
> `http://localhost:<port>`. It now wants a closing tag, or an opening tag
> carrying an attribute.
>
> ### What it catches
>
> Put 0.59.3's defect back and the guard names it — file, line and expression:
>
>     9 unescaped interpolations into markup, above the 8 recorded:
>         routers/accounts.py:247: {error or 'no code came back'}
>
> Four hundred releases of invisibility, and it was never hard to see. Nothing
> was looking.
>
> ### Three attribute interpolations escaped on the way past
>
> `<html lang="{language}">` depended on the caller having negotiated one of ten
> known codes; `<option value="{value}">` on a hard-coded tuple; the policy
> nonce on `secrets.token_urlsafe`. All three were safe and all three now escape
> where they are written, which costs nothing and removes a permanent row from
> the record.
>
> ### Also
>
> - Versions moved to 0.59.4 across the console, the backend, and the iOS,
>   Android and Windows projects (build 59004).
> - `shared_guards.txt` regenerated at 397 names; the divergence record holds at
>   136.

## app-v0.59.3 — QRME app-v0.59.3

- Published: 2026-08-08
- Commit: `959ad5f92c1699e9f2b3def2b5fe5711ad3f433d`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.59.3>

> ### What a page promises a browser before it says anything else
>
> 0.59.2 built a harness that talks to a real server, because the rules a
> browser enforces are invisible to an in-process client. This round pointed it
> at the surface where that matters most: the HTML these products serve to
> someone **without an account, on a device that is not theirs** — the sticker a
> stranger kneels over, the sealed-carrier card, the page a sign-in provider
> sends a browser back to.
>
> Measured over HTTP, every one of those pages in all three products went out
> with **no `Content-Security-Policy`, no `X-Content-Type-Options`, no
> `X-Frame-Options` and no `Referrer-Policy`.**
>
> That was the standing invitation. Then a sweep of every f-string that builds
> markup found what had walked through it.
>
> ### Reflected cross-site scripting on the sign-in callback
>
> `GET /auth/oauth/{provider}/callback?error=…` interpolated the query parameter
> straight into its HTML. Driven over HTTP:
>
>     ?error=<script>alert(document.domain)</script>
>     →  400, and the payload comes back verbatim inside <p>…</p>
>
> Anyone who could get a person to follow a link ran script on this product's
> own origin — in a browser holding a session, or inside the packaged console's
> window. Two more values on the same route went in unescaped: the provider's
> error message and the address it returns.
>
> Escaped at the interpolation, which is the fix. The policy below is the second
> line, not the first.
>
> ### A policy with a nonce, because one without is decoration
>
> `script-src 'unsafe-inline'` permits exactly what an injected `<script>` needs
> and would have stopped nothing above. So `pagehead.py` mints a nonce per
> response, the pages that carry an inline script stamp it through
> `script_open()`, and the policy names that nonce and nothing else:
>
>     default-src 'none'; img-src 'self' data:; style-src 'unsafe-inline';
>     script-src 'nonce-…'; connect-src 'self'; form-action 'self';
>     base-uri 'none'; frame-ancestors 'none'
>
> `style-src` keeps `'unsafe-inline'`: the stylesheets are constants in the
> package and no page interpolates into them.
>
> Verified in real Chromium against a real server — the beacon page renders
> with **no CSP violations**, styles applied, its own script running.
>
> ### What the guard checks
>
> `test_what_the_browser_enforces.py` grew from four questions to a dozen: the
> headers on every stranger-facing page, that the policy names a nonce rather
> than permitting everything, that the page and its policy **agree** about that
> nonce, that the reflected parameter comes back escaped, and that JSON is left
> alone.
>
> The nonce-agreement check is the one worth keeping. If the header and the tag
> ever drift apart, the policy is still perfect and the page's own script
> silently stops running — and that check's first draft failed against correct
> code, because it read the header from one request and the body from another.
> Two requests, two nonces. It reads both from one response now.
>
> ### Also
>
> - Versions moved to 0.59.3 across the console, the backend, and the iOS,
>   Android and Windows projects (build 59003).

## app-v0.59.2 — QRME app-v0.59.2

- Published: 2026-08-08
- Commit: `a7379d3ae04537cab6902adc11d0f388d37693de`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.59.2>

> ### A crash the browser threw away
>
> 0.59.1 found a CORS defect in a sibling product by comparing three
> repositories rather than by testing behaviour — because **no test in this
> estate could have found it.** Every one of them calls the app through a
> `TestClient`, which never sends an `Origin`, never runs a preflight, and never
> drops a response for want of a header. The whole class is invisible.
>
>     asked     does the server answer
>     mattered  does the answer reach the reader
>
> Asking the question properly found a second one, in all three products at
> once.
>
> An unhandled exception is rendered by Starlette's `ServerErrorMiddleware`,
> which sits **outside** every middleware the factory adds — including CORS. So
> a 500 went back to a browser with no `access-control-allow-origin`, and the
> browser discarded the entire response. Measured over HTTP:
>
>     GET /health   200   access-control-allow-origin: *
>     a 500         500   access-control-allow-origin: None
>
> The consequence is worse than a missing header. These consoles distinguish
> *the backend is unreachable* from *the backend refused* — the version-mismatch
> guard and the content-free problem reporter both depend on it — and a 500 the
> browser throws away is indistinguishable from the first. **Every crash in
> every one of the three products reached its user as "Failed to fetch."**
>
> ### Why the obvious fix is not the fix
>
> Registering `@app.exception_handler(Exception)` does not help: Starlette hands
> that handler to `ServerErrorMiddleware`, which is still outside the CORS
> layer. It has to be a middleware, and it has to sit *inside* CORS.
>
> So each factory now ends with a catch-all middleware followed by the CORS
> block, in that order — `add_middleware` inserts at the front, so the last one
> registered is the outermost. The body it returns says nothing about what
> broke: the traceback is logged on the machine and what leaves is a status and
> a sentence, the same posture every other refusal here takes.
>
> That ordering is now checked rather than assumed, and it needed to be: the
> three products disagreed about it. Two added CORS before their request-scoped
> middleware and one after, and nothing was comparing them.
>
> ### A test that starts a server
>
> `test_what_the_browser_enforces.py` boots the app under uvicorn on an
> ephemeral port and talks to it with a plain HTTP client, sending the header a
> browser sends. It checks that a 500, a refusal and a preflight all come back
> readable, and that CORS is still the outermost layer.
>
> Its last test is the point of the exercise: it makes the same failing request
> through a `TestClient` and shows it passing, with the header absent. Three
> thousand tests can pass on an API no console can read.
>
> ### Also
>
> - Versions moved to 0.59.2 across the console, the backend, and the iOS,
>   Android and Windows projects (build 59002).
> - `shared_guards.txt` regenerated at 383 names; the divergence record holds at
>   136.

## app-v0.59.1 — QRME app-v0.59.1

- Published: 2026-08-08
- Commit: `e9bbab1fe6e0708aaf0d99f2c142e25c201ec583`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.59.1>

> ### Three suites, and nothing comparing what they ask
>
> 0.59.0 closed on the observation that a literal copied into three
> repositories is calibrated for whichever of them was smallest. That is a
> special case of something larger: **every guard in this estate exists in three
> copies, and the copies drift silently in both directions.** A fix made in one
> product and not ported looks exactly like a product that never needed it.
>
> Nothing anywhere was comparing them.
>
>     asked     does this product pass its own suite
>     mattered  do the three suites ask the same questions
>
> A sweep of every `def test_*` across the three suites found **370 names
> carried by all three and 140 carried by exactly two** — 91 absent from PDI, 29
> from QRME, 16 from JIM-mini.
>
> ### Four of those rows were one defect
>
> `test_serve_cors.py` existed in QRME and JIM-mini and not in PDI, and so did
> the code it guards. Both siblings' `serve` opens CORS for a loopback bind,
> because the packaged console calls the API from its own origin and dies as
> "Failed to fetch" otherwise. PDI's frozen backend in
> `packaging/backend_entry.py` does the same, so the **installed** app worked.
> `python -m pdi serve` — the documented from-source path — set nothing.
>
> Measured over HTTP with the console's origin on the request, because CORS is a
> browser rule and an in-process test client never sends an `Origin` at all:
>
>     OPTIONS /terms   →  405, no access-control headers at all
>     GET     /terms   →  200, no access-control-allow-origin
>
> and after the fix:
>
>     OPTIONS /terms   →  200, access-control-allow-origin: *
>
> Every in-process test in that product passed throughout. Loopback binds only —
> a non-loopback bind is somebody serving a vault to a network, and that is the
> last place to open CORS by default; `--no-cors` restores the closed posture,
> and an explicit `PDI_CORS_ORIGINS` is never overwritten.
>
> ### The mechanism, and why it is a written record
>
> The three repositories are rarely checked out together, so a live comparison
> skips in CI — and this estate has already been bitten by that: the sibling
> vocabulary check in `test_the_refusal_names_the_field_on_the_form.py` carries
> a comment saying its first draft looked in the wrong place and skipped every
> run. *A check that never runs is not a check.*
>
> So the shared vocabulary is written down, byte-identical in all three
> repositories:
>
> - `tests/shared_guards.txt` — 377 names carried by all three.
> - `tests/guard_divergences.txt` — 136 names carried by exactly two, each row
>   naming the product that lacks it. Ratcheted: it may shrink, never grow.
>
> Each product then verifies its own half with nothing but itself. Every name in
> the manifest must exist here. Every divergence naming *another* product must
> exist here. Every divergence naming *this* product must still be absent, so a
> port that lands without being recorded fails rather than passing quietly.
> Three checks, no sibling checkout required — and the live three-way comparison
> runs on top whenever the siblings are on disk.
>
> ### A name is not a behaviour
>
> This compares function names. A guard ported under a different name reads as
> missing; one that kept its name while its body was gutted reads as present.
> PDI reports its version from `/health` under a differently-named test, and the
> record holds that as a row rather than pretending otherwise.
>
> The limit is worth the check, because the failure it catches is the one that
> actually happens: not a renamed guard, but a fix that never travelled.
>
> ### Also
>
> - Versions moved to 0.59.1 across the console, the backend, and the iOS,
>   Android and Windows projects (build 59001).

## app-v0.59.0 — QRME app-v0.59.0

- Published: 2026-08-08
- Commit: `528216481552fffb3029c3d312ea4d818e44bf03`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.59.0>

> ### A floor nobody raised is a floor nobody is standing on
>
> 0.58.8 found the route reader had one floor and four clients. 0.58.9 found the
> localizer's floor was ten against nine hundred and forty-five. Twice in a row,
> the same defect in a different instrument: a number written when the surface
> was small, correct on the day, never raised.
>
> Fixing them one file at a time does not generalise. This round swept every
> floor in the suite instead.
>
> ### The two questions
>
> A floor answers one question on every run — *is the number satisfied* — and
> that is exactly the question that keeps passing after the number stops meaning
> anything.
>
>     asked     is the number satisfied
>     mattered  is the number still near what it measures
>
> The standard is the one 0.58.8 set for its own table and 0.58.9 kept: a floor
> under **half** of what it measures is not holding anything. Applied to
> everything reachable in this product, every one of them failed it:
>
>     l10n asked, per shell        10 against 945-961     ratio 0.01
>     l10n held, per shell         20 against 1087-1115   ratio 0.02
>     path literals, all surfaces  40 against 1407        ratio 0.03
>     console call sites          200 against 429         ratio 0.47
>
> The last one is worth reading twice, because 0.58.8 wrote that *the console is
> protected* and built a round on top of that sentence. It was protected against
> being blinded outright — 351 down to 74 does trip a floor of 200. It was never
> protected against being halved, and half of a route reader is half an audit.
> The sentence was true about the failure it was tested against and false about
> the one nobody tested.
>
> **91 floors in this product** carried their own literal, across 56 files.
>
> ### The finding underneath the finding
>
> The rows that **passed** are as informative as the ones that did not. The same
> literals appear in all three products, copied across when a guard was ported.
> `assert len(made) > 200` is four-fifths of JIM-mini's console and 0.47 of
> QRME's. `assert len(made) > 20` is a real floor against PDI's thirty-five
> native call sites and a twentieth of QRME's four hundred and thirty.
>
> **One number written to work in three repositories is calibrated for whichever
> of them was smallest when it was written.** It reads as fine in the small
> products forever, and ages into decoration in the large one, and nothing in
> any of the three could tell the difference — because none of them had the
> measurement attached.
>
> `test_the_console_is_a_client_too.py` even carried the reason in its own
> docstring: the floor was set low deliberately *because the three products'
> shells differ by a factor of three in size*. That is a true sentence about why
> the number is small and a false one about what it holds.
>
> ### The convention, because the sweep needed one first
>
> A floor is spelled a dozen ways — `assert len(found) > 20`, `assert total >=
> 40`, a `FLOORS` tuple, a bare `_MIN_PATHS`. Nothing could walk them all,
> because the number is not the hard part: the **measurement** is. A literal
> inside an assertion has none attached, which is precisely why it can drift to
> a fiftieth of the truth with every run passing.
>
> `tests/ratchets.py` is a floor plus the way to read the same quantity now:
>
>     Ratchet("route.calls.console", 340, _calls("console"),
>             "call sites the route audit reads out of the console")
>
> Registering one has three effects. The number lives in one place instead of
> inside an assertion. `test_a_floor_is_within_sight_of_what_it_measures.py`
> checks it against reality on every run, in both directions. And because the
> assertion now reads `ratchets.floor("name")` — a call, not a constant — the
> AST sweep stops seeing it, so registering removes a row from the backlog with
> nobody editing a list.
>
> ### What is left is counted, not guessed at
>
> The remaining bare floors are held in `unregistered_floors.txt` with a
> ceiling, the way every backlog in this estate is. Not all of them are wrong;
> some are small fixed cardinalities that will never drift. Telling those apart
> from the decoration requires knowing what each one measures, which is the work
> of registering it. A **new** bare floor now fails at the moment it is written
> rather than three releases later.
>
> ### Also
>
> - Versions moved to 0.59.0 across the console, the backend, and the iOS,
>   Android and Windows projects (build 59000).

## app-v0.58.9 — QRME app-v0.58.9

- Published: 2026-08-08
- Commit: `1a5d6f46eb1fcbbfa3fbfcac474fe29f50d26717`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.58.9>

> ### Ten against nine hundred and forty-five
>
> 0.58.8 audited the route reader and found the three native shells had no floor
> at all, closing by naming the next reader with the same shape available and
> unused: the one that reads the L10n tables. It has the same hole, and worse
> numbers.
>
> `test_a_shell_asks_for_a_key_it_has.py` asserts each shell extracts **at least
> ten** localizer calls and holds **at least twenty** table rows, as a canary
> against the pattern silently ceasing to match. It was written when that was a
> meaningful fraction. The tables now hold 1087, 1100 and 1115 rows and the
> screens make 945, 950 and 961 calls.
>
>     ten against nine hundred and forty-five
>
> A floor at one percent of the truth is not holding anything.
>
> ### Why the rest of the file does not cover for it
>
> Two of the three readers in that file are protected in both directions. If the
> table reader goes blind, every key a screen asks for stops being in the table
> and the first check reports hundreds of missing rows. If the reachability
> reader moves either way, the dead-row backlog reports undecided or stale rows.
>
> The **call** reader going blind is silent, because reachability falls back to
> a pattern that finds every dotted string literal in the sources whether or not
> a localizer call sits in front of it.
>
> Measured rather than argued. Narrowing the call pattern so it matches only
> `L10n.t("…")` — no whitespace, lowercase method — is an ordinary-looking tidy
> that blinds C# alone, because Windows spells it `L10n.T(`:
>
>     ios      950 call sites
>     android  961 call sites
>     windows   52 call sites
>
> **294 tests pass.** The one failure names four rows — `ncmp`, `ndsk`, `nov`,
> `nstu` — as *translated rows nothing asks for*, and those four are visible
> only because they are the shell's only keys without a dot in them. Nothing in
> that message says the reader stopped reading.
>
>     asked     does every key a screen wants have a row
>     mattered  can the reader still see the screens asking
>
> ### Two floors, because they fail differently
>
> **Absolute, per shell, on both halves** — the extracted call sites and the
> parsed table rows — set at roughly four-fifths of what each reader reaches
> today. That catches the slow case: a form dropped here, a suffix there, over
> several rounds, which no single diff makes obvious.
>
> **A spread across the three shells**, which needs no number chosen by hand.
> iOS, Android and Windows are one client written three times: the same screens,
> ported by hand, so their tables are near-identical in size. Measured, the
> quietest shell sits at 98% of the busiest in QRME, 89% in JIM-mini and 77% in
> PDI. A shell at a twentieth of its ports is not a smaller shell.
>
> The console is deliberately not a fourth port, and the reason is measured
> rather than assumed: it shares 82 rows with QRME's shells, 62 with JIM-mini's
> and **none at all** with PDI's. The desktop frame and the phone screens are
> separate vocabularies, so neither a spread rule nor a superset rule between
> them would mean anything.
>
> ### And the comparison the backlog files never made
>
> `native_dead_keys.txt` carries a per-shell count — 73, 97 and 103 in QRME —
> that has never been compared across shells. The ratchet asks whether the
> number is going up; it does not ask whether one shell is carrying far more of
> it than its ports. Most of those rows are not waste: the file's own header
> says they are screens that exist on three shells and say less on one. That is
> exactly a per-shell comparison, and it was sitting in the file unmade. It is
> one-sided on purpose — a shell below its ports has paid its debt down.
>
> ### Also
>
> - Versions moved to 0.58.9 across the console, the backend, and the iOS,
>   Android and Windows projects (build 58009).

## app-v0.58.8 — QRME app-v0.58.8

- Published: 2026-08-08
- Commit: `77a1880b561e20ad10b1a51dec4333645b06d384`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.58.8>

> ### The route reader had one floor and four clients
>
> 0.58.7 found a missing brace by auditing a reader rather than the thing it
> read, and closed by naming the general case: **a blind instrument is
> indistinguishable from a clean repository.** The route audit's reader is the
> oldest and most load-bearing in the estate — six other files ask `clientpaths`
> what each client calls, and a route table read short narrows all of them at
> once, silently, in the safe direction. So this round went there.
>
> ### What the probe found
>
> The console *is* protected. `test_the_audit_is_actually_looking_at_something`
> asserts `calls(CONSOLE) > 200`, written when the console was the only client.
> Blinding the console's template-literal reader drops it 351 → 74 call sites
> and fails four tests including that one.
>
> **The three native shells had no floor at all.** Their protection was
> incidental — a scatter of per-block and per-form tests from earlier rounds
> that happen to name routes those readers see. Blinding the iOS `request(`
> form drops it **430 → 11** call sites; what fails is a handful of block
> guards, not one of them saying *the iOS reader has stopped reading*. A
> narrowing that misses the blocks those tests happen to cover passes in
> silence, and `doorless` still reports zero throughout, because the other
> three clients cover for the blind one.
>
> ```
> asked     do the clients call every route
> mattered  can the reader still see the clients
> ```
>
> ### Added
>
> - `test_the_reader_can_still_see.py`, in all three products. Two floors,
>   because they fail differently. **An absolute floor per client**, set at
>   about four-fifths of what each reader reaches today, catches the slow case —
>   a reader narrowed a form at a time until it covers a fraction of the
>   surface. **A spread check across the three native shells** catches the fast
>   case without a hand-chosen number: iOS, Android and Windows are one client
>   ported three times, so one reader at a third of the other two is the reader
>   breaking rather than the shell shrinking.
> - The console sits outside the spread comparison, and the reason is measured
>   rather than assumed: JIM-mini's console extracts 251 call sites against 114
>   on each phone, PDI's 121 against 35. Those consoles carry surface the phones
>   do not, so a rule spanning all four would have to be loosened until it
>   caught nothing. The absolute floor is what holds the console.
> - A floor on the route table itself. `app.routes` is not the route table — it
>   showed 8 of 409 once, and the first doorless audit built on it reported a
>   clean bill.
>
> The floors are ratchets, not targets. Raising one when a client grows is
> ordinary; lowering one takes a deliberate edit that shows up in a diff, and
> the only honest reason is a client that genuinely got smaller.
>
>
> Suites: **1547 + 1533 = 3,080** across 218 files.

## app-v0.58.7 — QRME app-v0.58.7

- Published: 2026-08-08
- Commit: `18531a2b368d54fd9e1110d27ae7fbe42f670350`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.58.7>

> ### A wire model is data, and data has no methods
>
> 0.58.6 closed by naming its own hole: a pin whose reader goes blind reads a
> model as **empty**, an empty set is a subset of anything, and the pin passes
> against nothing while looking exactly like a pin that is holding. That is the
> only way this table can lie, so this round went after it rather than after
> more surface.
>
> ### Added
>
> - Every pin now asserts on **both ends**: the model read something, and what
>   it read shares at least one key with the contract. Deliberately not a size
>   floor — `MicPlacesOut` and `ChainState` are honest one-property wrappers,
>   and a floor that called those defects would be the file inventing work.
> - Three checks read the readers themselves against a second opinion. Every
>   struct whose conformance list mentions `Decodable` must be one the pattern
>   can see; every C# record read by the finder must survive paren-matching;
>   every property the language declares must be one the property pattern finds,
>   located by where a declaration *starts* rather than where it ends.
>
> ### Fixed
>
> **The second opinion did not find a reader bug on its first run. It found a
> missing brace.**
>
> `struct SpecialistRow: Decodable {` was never closed, and the
> `extension ApiClient {` that should have followed it was never opened.
> **Ninety-five client methods** — the whole *face it shows the world* block,
> avatar through experience — were declared as members of a two-field wire model
> rather than on the client. Every screen calling `ApiClient.shared.avatar(…)`
> had nothing to call.
>
> Three guards were in a position to see it and none did:
>
> ```
> brace balance (0.57.5)   passed — the file balances; one brace has the
>                          wrong opener
> the member check (0.58.1) passed — the methods are in ApiClient.swift,
>                          just nested inside a struct
> this file's own pins     passed — SpecialistRow is not pinned
> ```
>
> What gave it away was a check written to audit the reader rather than the
> code, and what it caught was the thing nobody had thought to assert, because
> it is too obviously true to say out loud: **a wire model is data, and data has
> no methods.** That assertion is here now, and it costs one line to run.
>
>
> Suites: **1547 + 1528 = 3,075** across 217 files.

## app-v0.58.6 — QRME app-v0.58.6

- Published: 2026-08-08
- Commit: `bce03f882a92cd3e65320b75ead37019dec75bcf`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.58.6>

> ### The refusal surfaces, and a reader that read a struct as empty
>
> 0.58.5 closed by naming this batch — the screens that render what the platform
> will **not** do, from data rather than prose, so the screen cannot drift from
> the behaviour. An empty render of one of those does not read as a bug. It
> reads as *no limits*, which is the worst failure mode a consent screen has.
>
> Five of them, read at both ends across all three shells: the overlay
> catalogue's kinds and its refusals, the microphone vocabulary's refusals, the
> places a wearable may be lent, and the cloud-contribution log. **All correct.**
>
> Two rounds running the finding was on every shell at once rather than on one —
> the shells agree with each other and disagree with the server. Cross-checking
> the clients against each other would have found neither the guided tour nor the
> microphone disclosure. This table is the only instrument in the repository that
> catches that, which is the argument for growing it on a round where it finds
> nothing.
>
> ### Added
>
> - Nine more pinned rows: `OverlayCatalogue` with its kinds and refusals,
>   `MicVocabularyOut`, `MicPlacesOut` with its places, and `ContributionView`
>   with its log — plus the Kotlin reads of the same three routes.
> - The reader learned three more lookups, all still inside the one pinned
>   function or the module it lives in. `{**dict(r), …}` over
>   `conn.execute("SELECT id, condition, … FROM …")` — the column list is a
>   string literal right there, so the keys `dict(r)` carries are readable;
>   `SELECT *` is not, and is refused. A `**spec` bound by a *comprehension*
>   generator rather than a `for` statement. And `list(TABLE.values())` over a
>   module table written as a dict comprehension.
>
> ### The trap it walked into first
>
> Injecting a defect into PDI's `ComplianceProgram` did not fail the guard, and
> that was the guard's fault rather than the injection's. PDI declares
> `struct X: Decodable { let a: T; let b: T }` on one line, and the property
> pattern required end-of-line — so it read that struct as **empty**, and an
> empty model passes every comparison. The pin had been checking nothing since
> the day it was written. Semicolon-separated properties are read now, computed
> ones are still excluded, and the round that found it is the round that
> injected rather than the round that wrote the pin.
>
> Suites: **1547 + 1520 = 3,067** across 217 files.

## app-v0.58.5 — QRME app-v0.58.5

- Published: 2026-08-08
- Commit: `01c100a1f10b72d2a538f8626a6180984b906b11`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.58.5>

> ### The disclosure that showed nobody
>
> 0.58.4 shipped a pinned table — each row a shell model held against the backend
> function whose `return` is its contract — and closed by naming where it should
> grow: the surfaces where an empty render reads as *nothing to report* rather
> than as a bug. The first one checked was worse than the guided tour.
>
> `GET /rooms/{id}/mic` and `GET /places/{surface}/{id}/microphone` answer with
> **`microphones_lent`**. All three shells read `lent`. The disclosure naming who
> in a room has lent the profiles an open microphone — device, gain, and since
> when — rendered as **nobody**, on the iPhone, on the Android and on Windows.
>
> The route's own docstring spends a paragraph on why that disclosure is readable
> by everyone present rather than by its subject alone, because a disclosure only
> its subject can see is not a disclosure. One that nobody can see is less than
> that.
>
> The inbox and the overlay disclosure were checked in the same pass and are
> correct. They are pinned anyway: a row that passes on the day it is written is
> the point of the table, not a wasted one.
>
> ### Added
>
> - Six more pinned rows here, and the reader learned to follow three more
>   shapes, all of them assignment inside the one pinned function: `out = {...}`
>   with `out["k"] = …` after it, `rows = [{...} for r in …]`, and `rows = []`
>   with `rows.append(row)`. 0.58.4 named the last of those as a limit and
>   refused to guess past it. It is read now rather than guessed.
> - A `**spec` is resolved the same way — to a module-level dict of dicts whose
>   values all carry the same keys, directly or through the
>   `for _k, spec in SOMETHING.items()` that produced it — and refused outright
>   when it is anything else. The refusal is the feature: a pin this file cannot
>   read is one it must not invent.
>
> ### Fixed
>
> - The live-microphone disclosure reads `microphones_lent` on the iPhone, the
>   Android (both the room and the place route) and Windows. It was reading
>   `lent`, and showing nobody.
>
> Suites: **1547 + 1520 = 3,067** across 217 files.

## app-v0.58.4 — QRME app-v0.58.4

- Published: 2026-08-08
- Commit: `668c6a0a01beaacd71d7e8b6b58fde7397c62964`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.58.4>

> ### The key was right and the shape was wrong
>
> 0.58.3 checked that every key a shell decodes is one the backend can send, and
> left a named gap: the check is a *union*, so a key read off the **wrong**
> response passes. The obvious next step was to bind each decode site to the
> route it calls and compare per route.
>
> ### Four attempts at that, and why none of them shipped
>
> The binding is not derivable by reading this backend, and every narrowing that
> removed a false positive removed real coverage with it:
>
> 1. **Route to handler to return.** Handlers delegate, wrap (`{"beacons": [...]}`)
>    and merge (`{**metrics}`). One level of following resolved 141 of some 400
>    routes, and the mismatch list was 41 rows of which the ones checked by hand
>    were the reader's fault.
> 2. **Flat-only on both sides.** Coverage fell to 52 sites and the mismatch
>    rate stayed above four in ten.
> 3. **Bind on the container key** — `chapters: [{...}]`. The first run reported
>    five defects that are not there: `llm.py` builds `{"messages": [...]}` as an
>    outbound *request*, and the backend's inputs share a vocabulary with its
>    outputs. Restricting to route-reachable returns fixed that and hid the real
>    finding instead.
> 4. **Disjointness rather than subset**, to survive a key with two shapes. It
>    survives them by not judging them.
>
> The rule narrow enough to be sound covers two sites per product and finds
> nothing. That is the honest ceiling of inference here, and it is worth writing
> down rather than shipping a guard whose failures are mostly its own.
>
> ### Added
>
> - `test_the_shape_inside_the_shape.py`, in all three products. It infers
>   nothing: each row **pins** a shell model to the backend function whose
>   `return` is that model's contract. A human read both ends once; the file
>   holds them together from then on. It is small on purpose and meant to grow
>   one verified row at a time.
>
> ### Fixed
>
> The guided tour, broken on both phones and correct on Windows:
>
> - `/tutorial` sends `chapters: [{chapter, steps}]`. The iPhone read `key` and
>   `title` off the chapter, so every row of the outline rendered as `?`; the
>   Android read the same two and built a list of empty pairs. It also looped
>   over a `lessons` key the route has never sent.
> - `/tutorial/start`, `/tutorial/progress/{id}` and `/tutorial/done` all answer
>   with `tutorial.where`, which **wraps** the step. Both phones decoded the
>   wrapper as a bare step and read `title`, `key` and `next` off the top level.
>   All three buttons showed an empty line.
> - `/tutorial/steps/{key}` sends the lesson text as `what`. The iPhone read
>   `body`, got nil, and fell back to repeating the title.
>
> Windows had all four right — and carried a comment saying a chapter never had
> a `key` or a `title` of its own. Somebody fixed one shell and the note never
> crossed to the others, which is the argument for a file rather than a comment.
>
> Suites: **1547 + 1520 = 3,067** across 217 files.

## app-v0.58.3 — QRME app-v0.58.3

- Published: 2026-08-08
- Commit: `c161a4a8b9601790b5d547985594225d711e2c1f`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.58.3>

> ### The key the server never sends
>
> 0.58.2 closed by naming where the seam goes next. The receivers whose type is
> known for free are checked now; the tier past them is the receiver whose
> members are *keyed* rather than named — `optString("worn")`,
> `GetProperty("mode")`, a `Decodable` property whose name **is** the wire key.
> A renamed backend field is the same silent break as a renamed method, except
> it does not fail on a build machine. It fails on a phone, as an empty list or
> a nil string, and the screen renders as though the server had nothing to say.
>
> Matching a key to the route it came from needs a type checker this machine
> does not have. Matching it to the backend's whole vocabulary does not, so the
> guard asks only what it can answer honestly:
>
> ```
> is this key one the server can emit anywhere at all
> ```
>
> Four live breaks, each of them a screen that renders empty:
>
> * `GET /places/{surface}/{id}/overlay` answers with `overlays`. The iPhone and
>   the Android read `worn`. That is the disclosure naming who in a place is
>   wearing a face over their camera — the reason the feature is allowed at all
>   — and on both phones it was always the empty list.
> * `POST /auth/oauth/{provider}/start` answers with `url`. Both phones read
>   `authorize_url`, got nil, and had nothing to open. **Sign in with Google and
>   Apple could not start on either.**
> * `/dock/where/{face}` answers with `screen`, `path` and `title`. The Android
>   helper printed `screen · tab`, so half of every *where does this live*
>   answer was blank.
> * `/interactors/{id}/referrals` answers with `provider_id` and `opened_at`.
>   All three shells read `specialist_profile_id` and a boolean `opened`.
>
> Windows had the overlay, the sign-in and the fine-tuning run right and the
> referral wrong; the iPhone had all four wrong. There is no shell that is
> reliably the correct one, which is the argument for checking all three.
>
> ### Added
>
> - `test_the_key_the_server_never_sends.py`, in all three products: every key
>   a shell decodes must be one the backend can put on a response — read from
>   all four places a key reaches the wire (a dict literal, a key assigned after
>   the dict is built, a model field, and `dict(row)`, which makes every column
>   a key).
>
> ### Fixed
>
> - The overlay disclosure on iPhone and Android reads `overlays`. It was
>   reading `worn`, and showing nobody.
> - Sign in with Google and Apple on iPhone and Android reads `url`. It was
>   reading `authorize_url`, and opening nothing.
> - The Android helper's *where does this live* line reads `title`, not `tab`.
> - The referral list on all three shells reads `provider_id` and `opened_at`.
> - The fine-tuning run on iPhone and Android reads the metrics the route
>   returns rather than a `status` and an `examples` count it never had.
> - Nine `Decodable` structs whose result is discarded named keys the routes do
>   not send. Nothing read them, so nothing broke — they were documentation of a
>   wire shape that was never true, and they are empty structs now.
>
> ### The traps it walked into first
>
> Three, all in the reader. A regex that ends a struct at the first `\n}`
> swallows everything after a nested one, and `CustodyProvenance` has three.
> `var stands: Bool { valid ?? verified ?? false }` is a computed property and
> `let _: Ok = try await …` is a discarded binding; neither is a key.
> `case profileId = "profile_id"` renames it, so reporting `profileId` reports
> the shell's own spelling as the server's. And a fourth in the vocabulary
> rather than the reader: reading only dict literals reported some sixty fields
> that are on the wire every day.
>
> Suites: **1542 + 1518 = 3,060** across 216 files.

## app-v0.58.2 — QRME app-v0.58.2

- Published: 2026-08-08
- Commit: `fd0b2ad05818a3c34101eac66e8e1d80bb39ebd9`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.58.2>

> ### The colour that wasn't in the palette
>
> 0.58.1 closed by naming where it should go next. `state.x` is not the only
> receiver in these trees whose type is known for free — it is only the first.
> Any receiver that exactly one file declares can be looked up the same way,
> and there are eight of them per product:
>
> ```
> iOS      state.x  ApiClient.shared.x  Theme.x
> Android  vm.x     ApiClient.x         Qrme.x
> Windows  AppState.Current.X           ApiClient.Shared.X   {StaticResource X}
> ```
>
> Widening it found one, and it is the cheapest kind of break there is. The
> Android problem-report card painted itself with `Qrme.Card2`; the theme
> declares `Card` and has never declared a second. Both sibling products paint
> the same card with `Card`, so it was a one-character slip no amount of reading
> the diff would have caught — and Compose has no fallback for an unresolved
> colour, so the whole screen file fails to compile with it.
>
> ```
> asked     is the thing a screen reaches for on its state object there
> mattered  is the thing it reaches for on *anything* there
> ```
>
> The API clients came back clean — **1,613 call sites across nine shells**,
> every one naming a method the client actually has. That is worth asserting
> anyway. 0.58.1's own defect had been sitting in `main` for rounds; the value
> of a guard is not only what it finds on the day it is written.
>
> ### Added
>
> - Every member reached on an API client, a theme object or `App.xaml` is now
>   read against the one file that declares it, alongside the state objects
>   0.58.1 covered — eight receivers per product, with a floor under each so a
>   moved file cannot quietly empty the comparison.
>
> ### Fixed
>
> - The Android problem-report card asked the theme for `Qrme.Card2`. It now
>   asks for `Qrme.Card`, which exists.
>
> ### The trap it walked into first
>
> Widening the check to the API clients immediately reported two methods that
> are right there in the file — `Features` and `SetFeature` on the Windows
> client, whose return type is
> `Task<System.Collections.Generic.Dictionary<string, bool>>`. The C#
> declaration pattern had no dot in it. Narrow and true is the standing rule
> here, and this is the other edge of it: a pattern narrower than the language
> reports defects that do not exist. Both the dot and a test for it are in now.
>
> Suites: **1542 + 1509 = 3,051** across 215 files.

## app-v0.58.1 — QRME app-v0.58.1

- Published: 2026-08-08
- Commit: `309bfdbfcc3d1a39b8e72b059e083f08ed4ab9e4`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.58.1>

> ### The member that isn't there
>
> 0.58.0 ended by restating the standing gap: no Swift, Kotlin or C# toolchain
> on this machine, so the native UI is asserted by reading and not by running —
> and that round widened the amount of screen riding on it. The honest response
> is not to pretend a compiler exists. It is to keep taking the classes of
> compile error that *can* be caught by reading. 0.57.5 took duplicate
> declarations and unbalanced braces; 0.57.6 took the markup; this takes the
> next one.
>
> Each shell has exactly one object the screens read their session from, and
> exactly one file that declares it — so `state.x` is not a guess about types.
> It is the one receiver in these trees whose declaration is known without
> resolving anything.
>
> ```
> asked     do the screens parse, and do they say the right things
> mattered  is the thing they reach for actually there
> ```
>
> ### Added
>
> - `test_the_member_that_isnt_there.py`, in all three products: every member a
>   screen reaches for on its shell's state object must be declared by it.
>
> Clean here on the first run — the finding was next door, and this product
> gets the check because the next one could be here.
>
> ### The trap it walked into first
>
> The first extractor reported four defects that were not there: `call` on the
> Kotlin view models and `IsSignedIn` / `IsEnrolled` on the C# ones. `fun <T>
> call(` puts a type parameter between the keyword and the name, and
> `public bool IsSignedIn => …` is expression-bodied with no `{` or `(` after
> it. Both shapes are matched now and tested for; a guard that reports four
> defects that are not there is one nobody reads.
>
> Suites: **1542 + 1502 = 3,044** across 215 files.

## app-v0.58.0 — QRME app-v0.58.0

- Published: 2026-08-08
- Commit: `07cb044014ba1a23a3b00ef4e7ee015115ae9d19`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.58.0>

> ### The key the phones never carried
>
> 0.57.9 ended by naming the shape: a guard that verifies *a* line rather than
> *every* path has a blind spot, and the same audit run on a different header
> would probably be productive. It was — but not the way it was expected to be.
> Asked of every header the console attaches to every request, the answer was
> not *some paths miss it*. It was **one header the shells do not send at all.**
>
> ```
> x-llm-api-key
> ```
>
> The person's own model key. Pasted into the console since 0.4.3, read by the
> backend per request into a context var and never written down, and sent by no
> native shell. A key set on the desktop was used on the desktop, and the
> deployment's key was used on the phone — same account, same profile, two
> different credentials, and nothing anywhere saying so. The phones even drew
> the provider list with *ready* / *no key* beside each row, which is the
> **deployment's** key state: the screen showed a fact about somebody else's
> credential and offered no way to supply your own.
>
> ```
> asked     does every request carry the headers this client sends
> mattered  does this client send the headers the product has
> ```
>
> ### Added
>
> - The key on all three shells: held on the device (UserDefaults,
>   SharedPreferences, the app's local state) and never in the account, pushed
>   into the API client once and sent from the same place the language header
>   goes.
> - A field to set it, under the four rows the console has had since 0.4.3 —
>   the same keys and the same words, so no new console/native split appears.
>   Saving an empty box is the clear; there is no flag to leave switched on.
> - `test_every_header_the_console_sends_the_shells_send_too`, which reads the
>   console's own shared helper rather than a list written in the test, so a
>   header added there cannot quietly stay there.
>
> ### Changed
>
> - `native_dead_keys.txt`: 276 → 273 rows, ceiling 104 → 103. `action.save`
>   was dead on all three shells because no shell had a form to save.
>
> Suites: **1518 + 1520 = 3,038** across 214 files.

## app-v0.57.9 — QRME app-v0.57.9

- Published: 2026-08-08
- Commit: `2518c040e8b0278b48748b97898db3e5de88a340`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.57.9>

> ### A funnel only funnels what goes into it
>
> 0.57.8 ended by naming its own next question: guards get written in one repo
> and not ported, so compare the three `tests/` directories. Twenty-four files
> exist in exactly two of the three, and most of those are genuine product
> differences. One was not.
>
> `test_the_language_nobody_was_sending.py` exists in JIM-mini and PDI and not
> in QRME — the product whose premise is a profile that speaks in a person's
> language, and which built an accountless *stranger* surface over three
> rounds. Every refusal it raises goes through `refusal_language`, which reads
> `Accept-Language` whenever the caller is not an owner.
>
> **A first pass said QRME's shells never sent the header. That was a
> case-sensitive grep and it was wrong** — all three send it, lower-case, from
> their shared request helper. What the guard could not ask, in any of the three
> products, is the question that mattered:
>
> ```
> asked     does this client set the header with the resolver
> mattered  does every request this client makes carry it
> ```
>
> Because the answer was **no**, everywhere:
>
> ```
> QRME      Windows 21 of 22 sends, iOS 3 of 4, Android 1 of 2
> JIM-mini  Windows 15 of 16, iOS 1 of 2,  Android 4 of 5
> PDI       Windows  3 of 4
> ```
>
> Uploads, streams and raw-response reads, each building its own request beside
> the shared helper and setting only `authorization`. Those calls carry a token,
> so a *valid* token still picks the owner's stored language — but an expired
> one is not a principal, and the refusal falls back to a header that was not
> there. Forty-four requests across three products.
>
> ### Fixed
>
> - One dispatcher per shell rather than one line per call site, because a line
>   per call site is precisely the thing that went missing forty-four times.
>   C# gained `Dispatch(HttpRequestMessage)`, Swift a `dispatch(_:)`, and the
>   Kotlin clients' remaining connections got the header where they are built.
>
> ### Added
>
> - `test_every_place_a_request_leaves_the_shell_carries_the_header`, which
>   walks every dispatch site rather than every line that mentions the header —
>   the half the original could not see, in the product that had it and the two
>   that did not.
> - The guard itself, in QRME, four releases after it was written next door.
>
> Suites: **1518 + 1518 = 3,036** across 214 files.

## app-v0.57.8 — QRME app-v0.57.8

- Published: 2026-08-08
- Commit: `563b9928c9951df2774a76f2a4c5d47151061b33`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.57.8>

> ### The rows the guard skipped were the interesting ones
>
> `test_a_shell_does_not_print_what_it_translated.py` has, since 0.54.0, opened
> its row reader with
>
> ```python
> if "{" in english:
>     continue
> ```
>
> Every row with a slot in it went unchecked, for four releases. That is not a
> corner of the table: a row with a slot is a row *about something*, which is
> most of what a screen actually says — and a sentence assembled around a value
> is the one a screen is most likely to hand-build, because building it is what
> the code is already doing.
>
> ```
> ? $"closest overlap {best}, below the {th} threshold for naming anyone"
> ```
>
> against `ns.who.below` — *"closest overlap {best}, below the {threshold}
> threshold for naming anyone"* — the same sentence, hole for hole, in that same
> shell's table in ten languages.
>
> ```
> asked     does a screen print a whole English row verbatim
> mattered  does a screen print an English row the reader will never see
>           translated, however it is spelled
> ```
>
> Found from the other side and by accident: 0.57.7 was fixing a Windows page
> that would not parse, read the code-behind while deciding a rename, and saw
> seven of these on one screen. This closes the general case rather than the
> seven.
>
> **A slotted row is compared by its fragments**, not by rebuilding the
> sentence — the shell's holes are not the table's, and `{en.Seconds:F1}s` is
> not `{secs}`. The row is split at its slots and the literal text between them
> is matched. Fragments shorter than a phrase are dropped, so `Built {date}`
> contributes nothing; that is a deliberate miss and the file says so.
>
> ### Two false findings, caught before they shipped
>
> The check's own first run against the sibling products reported two defects
> that were the reader's, not the code's, and both are now tested against:
>
> * `L10n.t("cw.sensitivity", …)` is a screen *asking* for a row, and the
>   fragment *"sensitivity"* is inside that key. A key is not something a reader
>   sees.
> * `$"{(int)Math.Round(p.Confidence * 100)}"` matched the row *"Confidence
>   {pct}% — earned from…"* on the word `Confidence`, which is a C# property
>   there and a heading here. The holes come out of the shown string too — the
>   same removal that is done to the row.
>
> Same lesson as the eighty-six protocol values that shaped the original: strip
> what is not prose before comparing prose.
>
> ### Fixed
>
> Twenty-seven sites across the three shells, twenty-four of them on the desktop:
>
> * the whole provenance footer — *Generated by … grounded in … source item(s) ·
>   moderation …* — hand-built in English on the Windows compose and chat pages
>   **and on both phones**, beside `nprv.generated` and `nprv.licensed` which the
>   iPhone's own `ProvenanceFooter` was already using one file over;
> * the watermark-recovery verdict, the objection status, the relationship
>   confirmation, the effective-model and effective-age lines, the licence offer,
>   the pack-sync count, the payout receipt, the held-listing reason and the
>   match line;
> * the signing credential list, which printed *verified at enrolment: basic* —
>   three `nsig.level.*` rows the iPhone had been reading all along while the
>   desktop printed the wire value raw.
>
> ### Changed
>
> - `native_dead_keys.txt`: 300 → 276 rows, ceiling 127 → 104. Every struck row
>   was struck because a screen started asking for it. The two files ask the
>   same question from opposite ends and this is the first round where the
>   answers met in the middle.
> - One new row, `nsig.registered`, for a line the Windows signature page typed
>   out in English beside the tier names it was also typing out.
>
> Suites: **1518 + 1512 = 3,030** across 213 files.

## app-v0.57.7 — QRME app-v0.57.7

- Published: 2026-08-08
- Commit: `faebad16c653e1c859e469940c57b614c77eaf4e`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.57.7>

> ### The files the release never touched
>
> 0.57.6 ended by naming its own next question: whatever a guard checks, ask
> first which files it does not open. Asked of the release itself, the answer is
> three files per product.
>
> A cut bumps `pyproject.toml`, `<pkg>/api.py`, `app/package.json`, the lock
> file, the README banner, the README release row and the changelog. That number
> reaches everything a *server* or a *console* reports. The three native shells
> report their own version from three build files no step in that list touches:
>
> ```
> native/ios/project.yml               MARKETING_VERSION: "0.1.0"
> native/android/…/build.gradle.kts    versionName = "0.1.0"
> native/windows/*.csproj              (no <Version> at all)
> ```
>
> ```
> asked     does the product carry the version it cut
> mattered  does the thing a person installs carry it
> ```
>
> Nine declarations across three products, every one of them `0.1.0` or absent,
> through every release since the shells were written.
>
> This is not cosmetic in the way a stale README is. `versionName` is the string
> on the Play listing and in Settings › Apps; `MARKETING_VERSION` is the App
> Store version and the one a crash report is filed against; the `.csproj`
> version is what Windows shows in a file's Properties. An install reporting
> `0.1.0` cannot be told apart from any other install — and these products ship
> a problem collector, which is the part that makes the omission bite.
> `versionCode` was worse: Android refuses an upload whose code does not
> increase, so a store submission was going to fail on the first try regardless.
>
> ### Added
>
> - `test_the_files_the_release_never_touched.py`. The three build files are
>   read against `pyproject.toml`; `versionCode` and `CURRENT_PROJECT_VERSION`
>   are **derived** from the version rather than kept by hand, because a counter
>   beside a version string is two things to forget instead of one.
> - The same files carry what a shell is allowed to do — the plist usage
>   strings, the `uses-permission` rows — and those are checked against the
>   platform APIs each shell actually calls. iOS *terminates* an app that opens
>   a camera with no `NSCameraUsageDescription`; Android throws.
>
> ### Fixed
>
> - All nine declarations now carry the release. The `.csproj` files gained
>   `<Version>`, `<AssemblyVersion>` and `<FileVersion>`, which they had never
>   had.
>
> ### A trap walked into while writing this
>
> The first pass at the capability check read `LAContext` in QRME's
> `Signing.swift` and `BiometricPrompt` in `Signing.kt` and was ready to report
> two missing declarations. Both are in **comments** — prose explaining why the
> shells use WebAuthn instead, since a local biometric check is the app's own
> word about itself and an assertion is not. A guard that counts a mention as a
> use invents a defect, which is worse than missing one. Comments are stripped
> before anything is counted, and a test holds that line.
>
> Suites: **1511 + 1502 = 3,013** across 213 files.

## app-v0.57.6 — QRME app-v0.57.6

- Published: 2026-08-08
- Commit: `b729fba03609f004f08daad14b843a4e27783d08`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.57.6>

> ### The half of the Windows shell that is not code
>
> 0.57.5 added a parse check for the native shells, globbed `*.swift`, `*.kt`
> and `*.cs`, and reported all three parseable. The Windows shell's **screens
> are not C#** — they are XAML, 3,700 lines of it, more than every `.cs` file in
> `Views/` put together — and the check never opened one.
>
> ```
> asked     do the files that look like code still parse
> mattered  do the shells' screens still parse
> ```
>
> Five pages across two products do not parse. Two of them are here. Each is a
> single element carrying `x:Name` twice:
>
> ```xml
> <TextBlock x:Name="ConsentText" TextWrapping="Wrap" FontSize="12"
>            Foreground="{StaticResource QrmeT2Brush}"
>            x:Name="NothingNote" />
> ```
>
> Duplicate attributes are forbidden by XML itself, so no conformant reader gets
> past the tag and the build stops there. It is 0.57.4's Swift defect in markup,
> arrived at the same way: a second name was needed and it went onto the element
> that was already there.
>
> ### Added
>
> - Four markup checks in `test_the_shells_still_parse.py`, all of them things a
>   XAML compiler refuses outright rather than things a reviewer would prefer —
>   the page is well-formed XML; no two elements in it share a name; every
>   handler it names exists in its code-behind; every control the code-behind
>   drives is named in the page. Reach floors on all four, and four injected
>   defects confirming each can fail.
> - A state the desktop voice screen never had: with no profile it read
>   `AppState.Current.Pid`, found nothing and returned, leaving three cards of
>   headings over buttons that answered nothing. `nvoi.needprofile` — *Create a
>   profile first* — was in the table already, translated ten ways, asked for by
>   nobody.
>
> ### Fixed
>
> - `SignaturesPage.xaml` and `VoicePage.xaml` each carried a duplicate
>   `x:Name`, and in both cases the code-behind drove **both** names, so the
>   rename had to decide which control was meant rather than drop an attribute.
> - The Windows voice screen printed seven sentences in English beside their own
>   translations — the consent line, the sample counts, what enrolment still
>   wants, when the voiceprint was built, what happens to a retired one, and how
>   many samples a withdrawal deleted. The iPhone built two of the same four the
>   same way. `test_a_shell_does_not_print_what_it_translated.py` compares
>   *literals* against the table, and every one of these is interpolated, so the
>   only signal was a row nothing asked for.
> - `nvoi.record` and `nvoi.sample` are both *Record a sample* in all ten
>   languages. Windows labelled one button from the first at load and the second
>   after a recording — one button changing which translation it answers to
>   halfway through. One key now; the short row is deleted from all three tables.
>
> ### Changed
>
> - `native_dead_keys.txt`: 311 → 300 rows, ceiling 134 → 127.

## app-v0.57.5 — QRME app-v0.57.5

- Published: 2026-08-07
- Commit: `52a3946bbcf554d146de0055e4bb6ccf00754ece`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.57.5>

> ### Nothing here builds the phones, so nothing here noticed when they stopped
>
> 0.57.4 shipped a fix and a defect in the same release. Renaming iOS's `venue`
> to `locality` collided with a `locality` already declared in the same
> `TradeSection` — two stored properties of one name in one type, which does not
> compile. It reached `main` and sat there for a release.
>
> The reason is worth writing down rather than apologising for: **every guard in
> these repos reads the shell sources as text.** The request-body guard extracts
> call shapes; the response guards extract declarations; none of them parse, so
> none of them can see a syntax error. `tsc --noEmit` covers the console. There
> is no Swift, Kotlin or C# toolchain on the machine these run on, so there is
> nothing to compile with.
>
>     asked     do the shells say the right things to the server
>     mattered  do the shells still compile
>
> ### What this checks, and what it does not
>
> `test_the_shells_still_parse.py` does not typecheck. It checks the one class
> of breakage that is invisible to a text-reading guard, cheap to detect without
> a compiler, and *certain* to stop a build:
>
> * a name declared twice in one scope — a Swift type's stored properties, a
>   Compose function's `remember`ed state, a C# type's fields;
> * braces that do not balance, counting through strings and comments.
>
> A green run here does not mean the shells build. It means they do not contain
> the specific mistake that got past everything else. That is a narrow claim,
> and it is stated narrowly in the file: the whole arc since 0.56.4 has been
> guards that measured slightly the wrong thing and passed, and a check that
> promised "these compile" would be the next one.
>
> The scope reader counts braces rather than matching a regex, because a pattern
> that stops at the first `}` reads half a type — and half a type has no
> duplicates in the half it did not read. Nested declarations are excluded: a
> `var` inside a closure is not a member, and an inner type's property belongs
> to the inner type.
>
> Three defects were injected and confirmed to fail it, the first being 0.57.4's
> own, put back verbatim.

## app-v0.57.4 — QRME app-v0.57.4

- Published: 2026-08-07
- Commit: `908e3f178f89bf6d22e293cfa5831633ef2b72d0`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.57.4>

> ### The inputs the shells never asked for
>
> 0.57.3 found seven defects in what the native clients send, fixed one, and
> recorded six with the same sentence beside each: *this needs an input the
> shell does not collect*. Recording was honest — inventing the missing value
> is what this family of guards exists to stop — but a recorded defect is still
> a dead button. This release collects the inputs.
>
> * **Coordination.** `CoordinateRequest` requires `from_department` as well as
>   a goal, and all three screens asked only for the goal, so coordinating an
>   organization answered 422 everywhere. Windows, iOS and Android now have a
>   department field beside the goal.
> * **The desk camera.** `CameraSet` takes a URL — "point the desk at its own
>   camera, or clear it back to the sample view" — and all three sent
>   `enabled: true`, a switch for a thing with no address. There is a camera
>   address field now, and clearing it clears the camera.
> * **Marketplace settings.** `MarketPrefs` is where "here" is and how far out
>   to look. The shells sent `show_offers`, which no model has ever had, and
>   Android read it back off the response as the whole answer. The screens now
>   carry a locality and an **include things offered remotely** switch, which
>   is the boolean that actually exists.
> * **Listing a profile.** The listing takes a blurb and tags; where it is
>   offered is `/place`'s job. The `locality` the shells also sent was
>   discarded on arrival, and its box is gone from the listing card — the place
>   card has always had its own.
> * **Putting a price on a listing.** `OfferIn` is price / currency / stock.
>   Windows and Android sent `amount`, iOS sent it too through a body the guard
>   could not read, and none sent the required `price`. "Lowest you would take"
>   collected a counter-offer floor the server has no concept of, and that box
>   is gone rather than left to look like it does something.
> * **Accepting an exchange item.** Windows sent an empty body where `actor_id`
>   is required; it now sends the signed-in interactor.
>
> `tests/native_bodies_unverified.txt` is empty, at a ceiling of zero.
>
> ### A compile error 0.57.3 shipped
>
> Renaming iOS's `venue` to `locality` collided with a `locality` already
> declared in the same `TradeSection` — two `@State` properties of one name,
> which does not compile. Nothing here builds Swift, so nothing said so, and
> the request-body guard cannot see a syntax error because it reads the file as
> text. The duplicate is gone with the listing card's dead locality box.
>
> Worth stating plainly: the guard that found seven real defects would not have
> found that one, and the release that fixed them introduced it.
>
> ### Also removed
>
> `trade.accept` and `trade.show_offers` are gone from all three L10n tables —
> ten languages each, for two controls that no longer exist.

## app-v0.57.3 — QRME app-v0.57.3

- Published: 2026-08-07
- Commit: `7ae2e0f088b79d77a01126478c0914bc4e47761e`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.57.3>

> ### The guard read one client and the finding came from four
>
> 0.57.2 checked what the console sends against the model FastAPI validates
> with, and the defect that motivated it — a field all four clients sent and no
> model declared — was found by reading the four clients *by hand*. The guard
> read one.
>
>     asked     does the console send a body the route can accept
>     mattered  does any client send a body the route can accept
>
> So this release reads the other three. The comparison is the same and
> imported; only extraction differs, and it has to, because these clients share
> nothing:
>
>     C#      Post($"/organizations", new { name }, token)
>     Swift   request("/rooms", method: "POST", body: ["topic": t])
>     Kotlin  request("/profiles/$id/compose", "POST", JSONObject().put("topic", t))
>
> ### Seven defects, each in every client that makes the call
>
> That agreement is the evidence: three independently written shells do not
> drift the same way by accident. **Placing a marketplace listing has never
> worked from any native surface.** `ListingPlace` requires `locality` —
> somewhere a person typed — and Windows, iOS and Android all send `venue`, a
> key from `qrme.rated.VENUES` belonging to a different model. Every press
> answered 422. All three now send `locality`.
>
> The other six are recorded rather than fixed, at a ceiling of sixteen rows,
> because each needs an input the shell does not collect or a decision about
> what a control should mean: coordination requires `from_department` and the
> screens ask only for a goal; `CameraSet` takes a URL where all three send an
> `enabled` boolean; `MarketPrefs` has no counterpart for the `show_offers`
> switch all three send *and* Android reads back; listing a profile takes blurb
> and tags while the shells also send a `locality` the route discards; and
> Windows puts a price on a listing with `amount` and `accept_price` where
> `OfferIn` requires `price`. Correcting a field name alone would move those
> 422s rather than remove them.
>
> ### Thirteen of the first twenty findings were the extractor
>
> Two faults, both already familiar:
>
> * **C# infers a property name.** `new { name }` declares `name`; reading only
>   the `x = y` form found `learner_id = learnerId` and missed every inferred
>   one, accusing eleven routes of never sending fields they send on every call.
>   Fifth time in this arc the extractor wrote the findings it reported.
> * **Nested keys are not top-level keys.** Swift's
>   `body: ["items": [["content": c]]]` sends `items`; a flat scan also found
>   `content`, and `/rooms` supplied `id` and `kind` from inside `participants`.
>   Sixth time — the console guard has `_top_level` for exactly this, and the
>   idea did not travel with the file.
>
> Kotlin needed the opposite of the Swift fix: the key sits *inside* the
> `.put(` parentheses, so emptying nested brackets removed every key in the file
> and turned the Android client into a hundred and forty false "never sends
> required". Depth has to be measured at the `.put`, not applied to the text.
>
> ### And the reach floors caught a seventh
>
> Ported to PDI, the Windows reader found **zero writes**. That client builds
> its messages by hand — `new HttpRequestMessage(HttpMethod.Put, "/records") {
> Content = JsonContent.Create(new { key, value }) }` — where QRME wraps them in
> a helper. Zero found is indistinguishable from zero wrong, and only the
> per-client floor said so. The reader now knows both shapes, which also took
> QRME's own Windows count from 170 writes to 196.
>
> | | Windows | iOS | Android | found |
> |---|---|---|---|---|
> | QRME | 196 (181 readable) | 194 (129) | 194 (128) | **7** |
> | JIM-mini | 55 (51) | 55 (37) | 55 (37) | 0 |
> | PDI | 13 (12) | 12 (7) | 12 (9) | 0 |

## app-v0.57.2 — QRME app-v0.57.2

- Published: 2026-08-07
- Commit: `a893a7e3687afcf210914f3fb9ee7abce3261d47`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.57.2>

> ### Every guard in this family reads the answer. None of them read the question
>
> 0.56.4 through 0.57.1 asked four clients the same thing — C# records, Swift
> structs, Kotlin `org.json` reads, TypeScript type arguments — and the question
> was always *does this client understand what comes back*. Thirty-three defects
> across the four.
>
> Not one looked at what a client **sends**. The console guard makes that
> explicit in code: it skips any call carrying `method:`, which in this client is
> 194 of them. Those calls were checked by nothing, in either direction, and a
> request body is the same defect in mirror image. If the model calls a field
> `title` and the client sends `name`, FastAPI either answers 422 — a button that
> does nothing, forever — or drops the value silently and stores the row without
> it. Both are invisible from the client, which sent something and got a
> response.
>
>     asked     does the client understand the answer
>     mattered  does the route understand the question
>
> ### What it is checked against
>
> `app.openapi()`, not a regex over the Pydantic classes. The schema FastAPI
> publishes *is* what FastAPI validates against, so this guard cannot describe a
> rule the app does not enforce. Reading the models by hand would have been a
> fifth extractor to get wrong.
>
> Three questions: a required field the client never sends; a field the client
> sends that the model has no property for; and a write with no body at all to a
> route whose model requires one — listed separately because a guard that only
> walks bodies finds nothing wrong with sending none.
>
> | | writes | readable | matched a model | found |
> |---|---|---|---|---|
> | QRME | 192 | 162 | 158 | 0 |
> | JIM-mini | 113 | 70 | 92 | **2** |
> | PDI | 42 | 33 | 34 | 0 |
>
> QRME's writes are correct. That is a result, not an absence: three injected
> defects were confirmed to fail this guard before it shipped.
>
> ### The first run's eighty-two findings were all mine
>
> A body written as the bare identifier `body` gets its shape from the enclosing
> function's parameter. The first version searched backwards for `(body: {` with
> no left edge, found the parameter of a *previous* property in the same object,
> and credited its fields to this call — `POST /profiles/{id}/chat` was reported
> as sending `birthdate` and `display_name`, which belong to `createProfile`
> forty lines above. Fifteen of forty-two lookups landed in the wrong function,
> and between them produced eighty-two findings, every one phrased as somebody
> else's defect. Bounding the search to the member fixed it, and the count went
> to zero.
>
> A spread produced the eighty-third: `{ ...(to ? { to } : {}), text }` became a
> field called `...(to ? {}`. A body this guard cannot read is now a body it
> refuses to judge — inventing a defect is worse than missing one.
>
> ### And then the ratio caught a fourth
>
> Green in all three, and JIM-mini read 28 of its 113 writes against QRME's 162
> of 192. The parameter may be first or fifth: QRME writes `(body: { ... })` and
> JIM-mini writes `(uid, body: { ... }, token)`, and a pattern anchored on the
> opening paren reads one whole and the other at a quarter. Fourth time in this
> arc a borrowed pattern has read one product and quietly skipped another, and
> the first time the run was green either way — because a body it cannot read is
> a body it does not judge.
>
> Reach after the fix: QRME 99 → 162 readable, JIM-mini 28 → 70, PDI 25 → 33.
> JIM-mini's two findings only appeared on the far side of it.

## app-v0.57.1 — QRME app-v0.57.1

- Published: 2026-08-07
- Commit: `03575336f8aa50987ba61c691112c0a5c0546d5d`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.57.1>

> ### The fourth client, and it was the only one wrong
>
> 0.56.4 through 0.57.0 built one guard three times — for the Windows client's
> C# records, the iOS client's Swift structs, and the Android client's `org.json`
> reads. Nineteen defects in C#, nine in Swift, eight in Kotlin, and the running
> lesson of all three was that fixing a defect in one client is not fixing the
> defect.
>
> There is a fourth client, and it is the one most people use.
> `test_the_console_is_a_client_too.py` was written in 0.44 for exactly this
> blind spot — it found sixty-four routes a desktop owner could not reach — and
> it asks whether the console *calls* each route. It never asked what the
> console does with the answer.
>
>     asked     can the console reach every route
>     mattered  does the console read back what the route sends
>
> This client declares more than the other three combined: 246 shapes, 1,712
> fields, 194 GET bindings, each carrying its expected shape as a type argument.
> And TypeScript is erased at build time, so nothing checks a declaration
> against reality at runtime. A field the route does not send is `undefined`,
> and `{undefined}` in JSX renders as *nothing* — the layout closes up around it
> and the screen looks finished.
>
> ### What it found — four, all real, all visible
>
> **The delegation screen could not delegate.** `/profiles/{id}/delegation`
> sends `{"delegation": false, "phases": [...]}` — a boolean, with the list
> beside it. The console declared `delegation` as an object-or-null and read
> `policy.delegation.phases` and `policy.delegation.enabled` off it. Both are
> `undefined` on a boolean, so the screen showed every profile as un-delegated
> and drew no phase toggles, and with no toggles there was no way to switch it
> on. Thirty lines further down the *same file* reads `offer.delegation` as a
> boolean and `offer.phases` at the top level, correctly. One screen, one
> response, two readings, and only one of them right.
>
> The route was also wrong to advertise only the chosen phases: a capability
> advertisement that lists what an owner has already picked says nothing while
> they have picked nothing. It now sends `delegable` — the vocabulary — beside
> `phases`, the choice.
>
> **A dashboard tile that has never shown a number.** Home reads
> `stats.engagement_average`; the route sends `engagement_avg`. The tile has
> rendered `—` since the day the field was named.
>
> **Suggested friends was always empty.** The route sends `suggested`; the
> console declared `suggestions`, in *both arms* of a union so neither could
> match, and the reader's `?? []` fired every time.
>
> **`Stats.surfaces` declared `number`** where the route sends a list.
>
> ### The other three clients had none of them
>
> That is the inversion worth recording. Every release since 0.56.4 found the
> same defect sitting unfixed in a client nobody had checked yet. This one
> checked Windows, iOS and Android against all four findings and they were
> right in every case — `optBoolean("delegation")` in Kotlin,
> `JsonPropertyName("suggested")` in C#, `let suggested: [SuggestedRow]` in
> Swift. Three clients correct, one wrong, and the wrong one is the one a
> desktop owner actually opens.
>
> ### Three of the first findings were the guard's own
>
> Thirty of the first run's thirty-eight findings came from reading the verb on
> one line. This client writes
>
>     req<WallPost>(`/profiles/${profileId}/wall`,
>       { method: "POST", body, token }),
>
> with the verb on the *second* line, so 174 writes were driven as GETs and
> compared against whatever the list route returns — every field missing, in
> five types at once. It is the third release running in which the check for
> *is this a GET* was itself the defect. Arguments are now read to the call's
> own closing paren.
>
> Emptying a nested type body instead of deleting it fixed a second: `delegation:
> { ... } | null` had become `delegation: | null`, and the guard reported a real
> field as *declared `| null`*. And a union is satisfied by any arm, not by its
> first — the friends call was reported against a shape it never claimed to be
> the only one. It was wrong anyway, but a guard that is right by accident will
> be wrong on purpose next time.
>
> ### Ported, and the ports found more
>
> | | shapes | fields | GETs | driven | found |
> |---|---|---|---|---|---|
> | QRME | 246 | 1,712 | 194 | 85 | **4** |
> | JIM-mini | 100 | 623 | 110 | 49 | **2** |
> | PDI | 33 | 224 | 60 | 27 | 0 |
>
> All six are fixed rather than recorded, and all three record files sit at a
> ceiling of zero. This client marks a field optional when it genuinely comes
> and goes, so a missing required field is missing — there is no legitimate
> state to record, only a declaration to correct or a `?` to add. That is a
> deliberate difference from the Swift guard, and it is why this one reads as a
> list of defects rather than a list of states.
>
> ### The declaration now has teeth
>
> Putting the old delegation read back with the corrected type no longer
> renders wrong — it fails to compile: *Property 'phases' does not exist on type
> 'boolean'*. The lie was invisible only because the declaration agreed with it.

## app-v0.57.0 — QRME app-v0.57.0

- Published: 2026-08-07
- Commit: `c50af23434cb888df6ee475609119defcc6b8c7a`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.57.0>

> ### Twelve routes out of forty-two, and twelve looked like all there were
>
> 0.56.9 built a guard that reads the Kotlin client the way the C# and Swift
> guards read theirs, and closed by saying the next thing to do was give
> JIM-mini and PDI their own binding patterns. Handing the pattern across is
> where this went wrong, and the way it went wrong is the way it has gone wrong
> in every release since 0.56.4.
>
> QRME's `request` returns a `String`, so every read in that client wraps it:
>
>     val o = JSONObject(request("/profiles/$id/wearables", token = token))
>
> A pattern that requires the wrapper reads this client completely — 135 routes,
> 252 keys, eight defects found. JIM-mini's `request` returns a `JSONObject`
> already, so its ordinary line is
>
>     val o = request("/money/$uid", token = token)
>
> and the wrapper is not there to match. Forty-two GETs in that client. The
> guard found twelve, reported nothing beyond the six states already recorded
> against the Swift client, and passed.
>
> Twelve found reads exactly like twelve is all there are. That is the whole
> defect: a borrowed pattern that finds *some* of a file is worse than one that
> finds none, because none is obviously broken and some is not. The C# guard
> learned this in 0.56.5 — where PDI's client makes its calls in a shape the
> borrowed regex could not see, and zero found looked like zero wrong — and the
> lesson did not survive the change of language.
>
>     asked     does the guard travel
>     mattered  does the guard see the same share of each file it travels to
>
> ### What changed
>
> The constructor is now optional, which is one character of regex and most of
> this guard's reach. Two shapes were being dropped along with it and are now
> read: a call handed straight to a parse helper, and a call whose response is
> chained into immediately — `request("/models").getJSONArray("providers")`,
> where the chained key is a claim about the response and what hangs off it is
> not.
>
> | | routes read | keys read | GETs driven |
> |---|---|---|---|
> | QRME | 135 → **169** | 252 → **379** | 25 → **85** |
> | JIM-mini | 12 → **44** | 79 → **161** | 5 → **32** |
> | PDI | 13 → **18** | 26 → **31** | 5 → **15** |
>
> The floors under all three moved up to what each one honestly finds, so the
> reach cannot quietly fall back.
>
> ### Two findings that were the guard's own defect, not the client's
>
> The first version of the chained-key read searched a 240-character window for
> `).accessor("key")`, and in two different functions found a chain that
> belonged to something else:
>
>     val o = JSONObject(request("/displays/vocabulary"))
>     o.optJSONArray("never")?.let { a ->
>         out.add(a.getJSONObject(i).optString("why"))
>
> `why` is a key on the objects *inside* `never`. `light`, in the watch face, is
> a key inside `profile`. Both were reported as missing from the response, and
> both routes send exactly what the client reads. The check now walks the call's
> own parentheses to their close and takes the chain only if it attaches there.
>
> The third was subtler and would have been recorded rather than noticed.
> JIM-mini builds one URL by concatenation:
>
>     request("/circle/$uid/messages?with_id=" +
>             java.net.URLEncoder.encode(withId, "UTF-8"), token = token)
>
> The extractor sees the literal prefix, because the value is on the next line
> and is not a literal at all. Driving `?with_id=` with nothing after it asks
> for the *thread list*, which the route answers with a different shape that has
> no `messages` key in it — and the client was reported for reading a key that
> route sends perfectly well. A half-built query string is not a path this
> fixture can drive, so it is unreachable rather than recorded. Recording it
> would have put this guard's own defect into the ratchet file and called it a
> backlog.
>
> ### The record files, and a check that they still describe something
>
> JIM-mini records six rows: `note` on the adaptation profile, visible only
> while `built` is false, and five `ContinuityState` keys that need a history of
> check-ins and coach turns no route can manufacture. They are the same six the
> Swift guard recorded in 0.56.8 — the same routes, the same states, reached
> through a different language. Two independent extractors agreeing is the
> evidence that neither is inventing. PDI records none, at a ceiling of zero.
>
> All three files also gained a check that every recorded row still names a read
> the client makes. A row that describes nothing is a ratchet that has stopped
> ratcheting: it holds the ceiling up for a defect nobody has fixed.

## app-v0.56.9 — QRME app-v0.56.9

- Published: 2026-08-07
- Commit: `15f5661bf99a4a806a2f827f4cec91b419ac3bef`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.56.9>

> ### The client that declares nothing was the one guessing hardest
>
> 0.56.8 left Kotlin out with a hedge:
>
> > *it parses `JSONObject` by hand rather than declaring shapes, so there is
> > nothing to compare — which is either a reason it cannot have this defect, or
> > the reason nobody would find it.*
>
> It was the second one. This client declares nothing, but every line is two
> claims at once — `o.optJSONObject("kinds_worn")` says the route sends that
> key *and* that it is an object — and both can be wrong. The way they go wrong
> here is worse than elsewhere, because `org.json` does not throw: `optString`
> on a missing key returns `""`, `optInt` on a string returns `0`, and
> `optJSONArray` on an object returns `null` into the `?:` beside it. A C#
> client with the wrong type crashes and somebody sees it. This one draws an
> empty screen.
>
>     asked     does the client declare the right shape
>     mattered  does the client ask for the right thing
>
> **Eight wrong reads, and every one was already fixed in C#** — six of them in
> Swift too. `ai_badge` and `likeness_of` on the avatar, `purpose` on the front,
> `max_bytes` on media limits, `theme` read as a string when it is a card,
> `places` and `never` read as maps when they are lists, `faces` read as a list
> when it is a map. Third client, third time the same eight-or-so defects were
> sitting there after being fixed elsewhere.
>
> #### Five faults in my own extractor, and I shipped none of them
>
> The first run reported fifty-odd findings. Almost none were real:
>
> 1. the split was on `suspend fun`, so a plain `fun` helper between two of them
>    kept its reads in the preceding chunk — and because `o` is this client's
>    conventional name for a decoded body, they were credited to whatever route
>    that chunk began with. The voiceprint route was accused of reading thirteen
>    shop fields;
> 2. `val f = JSONObject(request(...)).getJSONObject("funnel")` binds the
>    *funnel*, and its keys were read as the response's;
> 3. `_INLINE` matched a POST reply and compared it to what GET returns;
> 4. the GET check looked for the keyword `method` — this client passes the verb
>    **positionally**, `request(path, "DELETE", null, token)`, so a DELETE and a
>    POST were read as GETs. That fault was already fixed in one of the two
>    places it lived and not the other;
> 5. and the boundary assertion, written for the third time in three languages,
>    **counted `suspend fun` when the split was on any `fun`** — so it passed
>    while the results were poisoned. Counting something other than the thing
>    you split on is not an assertion.
>
> Every one of those made the guard report things that were not true. None of
> them reached a release, because a list of findings is not a finding until each
> row has been read — but a fifth of this release was spent proving my own
> measurement wrong, which is the honest shape of the work and worth writing
> down rather than tidying away.
>
> Two thresholds were also mine rather than the code's: the reachable-route
> count and the key count, both set before the extractor tightened. They are set
> from what it actually finds now.
>
> #### The record
>
> Five rows, and they are the same conditionals the C# and Swift records hold —
> the solitude offer, and the attestor and level on a badge that nobody has
> verified yet. Rows are `<path> <key>` because this client has no struct to
> name. JIM-mini and PDI have the guard now too.

## app-v0.56.8 — QRME app-v0.56.8

- Published: 2026-08-07
- Commit: `7a7aa9514ed4ee6f0386836224c9812c51e353a3`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.56.8>

> ### Fixing a defect in one client was not fixing the defect
>
> 0.56.4 and 0.56.7 found nineteen defects in the Windows client and fixed them
> there. Then, chasing something else last release, I read the Swift file and
> found `MicVocabularyOut.widths` — a field no route has ever sent — sitting
> exactly where the Windows record's copy of it had been deleted two releases
> earlier. Four more like it. **Nothing would have told me.** The 0.56.7
> changelog said so and named this as the gap.
>
>     asked     is the client we check correct
>     mattered  is every client checked
>
> `test_the_shape_the_swift_client_expects.py` drives every GET binding in
> `native/ios/Sources/ApiClient.swift` and asks both halves of the same
> question: is each declared field a key the route returns, and can its declared
> type decode the shape that arrives.
>
> Nine fictions in this repo's Swift client, and **every one of them was already
> fixed on the Windows side**:
>
> | struct | what it declared | fixed on Windows in |
> |---|---|---|
> | `AvatarCard.ai_badge`, `.likeness_of` | fields no route emits | 0.56.4 |
> | `PairCard.built` | the server says `console_built` | 0.56.4 |
> | `FrontCard.purpose` | the front sends `headline` | 0.56.4 |
> | `DelegationOffer.enabled` | the server says `delegation` | 0.56.4 |
> | `MediaLimits.max_bytes`, `.kinds` | one limit for three media kinds | 0.56.4 |
> | `MicPlacesOut.places` | a map declared for a list | 0.56.7 |
> | `PageCard.theme` | a string for a card | 0.56.7 |
>
> All nine corrected, with the screens that read them.
>
> #### The extractor made the same mistake twice, in two languages
>
> Its first run reported fifty-odd findings. Most were artifacts: this client
> writes `struct Health: Decodable { let status: String }` on one line, and a
> pattern anchored on `\n}` misses that closing brace and runs on to the *next*
> struct's — reporting that struct's fields under this one's name. `ModelChoice`
> was accused of six fields that belong to `RobotSpec`.
>
> That is the same defect the C# guard grew an assertion for last release, for a
> different reason. So Swift has the same assertion now, and the reason it is
> written down twice is that writing it down once did not stop it happening
> again.
>
> #### What the siblings said
>
> JIM-mini and PDI both came back with **no fictions**, the third time in four
> releases those two clients have answered a new check cleanly. JIM records
> twenty-two conditional fields — continuity vectors, help tallies, presence
> areas — that appear only once an account has a history. Unlike the crash watch
> and the adaptation profile, which the fixture builds in two calls, continuity
> is derived from accumulated check-ins over time and has no route that builds
> one. A fixture that faked that history would be asserting against its own
> fiction, so the rows are recorded with the state named instead.
>
> Kotlin is still unread. It parses `JSONObject` by hand rather than declaring
> shapes, so there is nothing to compare — which is either a reason it cannot
> have this defect, or the reason nobody would find it.

## app-v0.56.7 — QRME app-v0.56.7

- Published: 2026-08-07
- Commit: `9f536869fa4ccf5e44c3c39ca9b3d8416d19707f`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.56.7>

> ### `kinds` meant three things, and one of them crashed the client
>
> The two names 0.56.4 could not strike were `kinds` and `refused` — collisions
> that were always on the server and only became visible once the Windows client
> stopped under-declaring the wire. Splitting them turned up something better
> than a naming problem.
>
> `GET /profiles/{id}/wearables` sends `kinds` as a **map** — kind to where it is
> worn — and the Windows record declared `string[]`. `System.Text.Json` does not
> coerce an object into an array; it throws. So that call did not lose a field,
> it failed outright, and had done since the wearables board was written.
>
>     asked     do the names match
>     mattered  can the declared type decode what arrives
>
> #### Three meanings, three names
>
> **`kinds`** was a vocabulary of records, a map, and a filter selection:
>
> * the vocabularies (overlays, displays, exchanges, the lobby) keep `kinds`;
> * the wearables board's map becomes **`kinds_worn`** — kind → where it is worn;
> * a reader's marketplace preferences become **`kinds_wanted`**, because a
>   saved filter is a choice, not a vocabulary.
>
> **`refused`** was a boolean, a list of records, and a map:
>
> * the help answer's *did this refuse* keeps `refused`, the only boolean;
> * the vocabularies' lists become **`refusals`**;
> * the dock's and the wearables board's maps become **`refusal_reasons`**.
>
> Collision record 23 → 21.
>
> #### The check the guard did not have
>
> `test_the_shape_the_client_expects.py` compares declared **names** against the
> keys a route returns. `kinds` was returned, under exactly that name, as
> exactly the wrong kind of thing — so the guard saw nothing. `DockWhere.screen`
> declared `string` for an integer got through the same hole in 0.56.4 and was
> only caught by reading it.
>
> There is now a second assertion: drive the route, and check that each declared
> C# type *can decode the shape that arrived*. Coarse on purpose — list, object,
> string, number, bool — because that is the distinction a decoder actually
> throws on.
>
> It found five more, every one a live crash rather than a blank field:
>
> | record | declared | arrives as |
> |---|---|---|
> | `WearableBoard.faces` | `string[]` | a map |
> | `DockFacesBox.faces` | `string[]` | a map |
> | `MicPlacesOut.places` | `Dictionary` | a list |
> | `DisplayVocabulary.never` | `Dictionary` | a list |
> | `PageCard.theme` | `string` | a card with an id, a label and colours |
>
> All five corrected, with the screens that read them. The same check is now in
> JIM-mini and PDI, where both clients came back clean — as they did for the
> name check in 0.56.5.
>
> #### The other client that was guessing
>
> iOS carried the same fictions the Windows client did — `MicVocabularyOut.widths`
> and `OverlayCatalogue.overlays`/`refused` are fields no route has ever sent,
> and `WearableBoard.kinds`/`faces` were lists for maps. Corrected here. The
> shape guard reads the Windows client because it is the one place every wire
> name is declared with its type; nothing yet reads Swift or Kotlin the same
> way, and that is the next thing this guard is missing.

## app-v0.56.6 — QRME app-v0.56.6

- Published: 2026-08-07
- Commit: `f902b5f10c3750a03c813ac2f0fdcd2643c9a172`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.56.6>

> ### Reported from a phone: eight watch faces that were not on the page
>
> > *"On the readme in JIM-mini 5, 10, 15, 20, 25, 30, 35, 36 are not visible on
> > a mobile device."*
>
> That is exactly the set of cells in the last column, and the reason was two
> layers deep.
>
> An HTML table is as wide as its **longest row**. JIM's watch gallery had six
> rows of five and one row of six, so the table was six columns wide — every
> five-cell row rendered a sixth empty column, and a phone clipped the whole
> thing past the fourth. QRME's main gallery was worse: one `<tr>` carrying
> **fifteen** cells beside rows of three, which made that table fifteen columns
> wide and left twelve blank columns on almost every row. That is the *gaps and
> spaces* in the same report.
>
>     asked     is every screen in the gallery
>     mattered  is every screen in the gallery *on the page*
>
> `test_docs_gallery.py` had been checking that every drawing is referenced and
> every reference resolves, and it passed the whole time — correctly. A cell can
> be present in the markup and pushed off the visible page by the row it sits
> in, and only the shape of the table can tell you that. Its own docstring even
> records an earlier version of this ("inserting one screen into a three-wide
> row pushed the last cell out"), which is a defect the file knew about and had
> no assertion for.
>
> #### Four across
>
> Every gallery is now a uniform grid: screens and watch faces four per row at
> `width="25%"`, desktop frames two at 50%. Four is the number because four is
> what fits the phone the report came from; a fifth column is the column that
> went missing.
>
> Eighteen tables were reflowed across the three repos. Five cells that held no
> picture at all — literal blank squares — were dropped on the way through.
>
> | | rows before | rows after |
> |---|---|---|
> | QRME screens (the big one) | `3,3,4,3,…,15,3,3,3` | 26 rows of 4 |
> | QRME desktop | `2,2,2,2,3,2,1` | 7 rows of 2 |
> | JIM screens | `4,4,…,3,…,5,1` | 27 rows of 4 |
> | JIM watch | `5,5,5,5,5,5,6` | 9 rows of 4 |
> | PDI screens | `3,2,3,3,3,3,2,…` | 8 rows of 4 |
>
> #### The guard
>
> `test_the_gallery_is_a_grid.py`, in all three repos. It finds every table
> whose picture cells all point at one folder under `docs/`, and asserts three
> things: no row wider than four, every row the same length as the one above it
> (the last may be short), and no cell without a picture in it.
>
> It reads the **widest** row rather than the first, because JIM's gallery
> opened with five rows of five and put the sixth cell in the last row —
> anything reading row one would have called it fine.

## app-v0.56.5 — QRME app-v0.56.5

- Published: 2026-08-07
- Commit: `10c7947270bc21da7db165acf75564314aac63f4`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.56.5>

> ### The guard travelled, and the two clients it met were not the same
>
> 0.56.4 named the port of `test_the_shape_the_client_expects.py` to JIM-mini
> and PDI as this round's work. It is done, and the finding is what it says
> about the three clients rather than about any one of them.
>
> **Both siblings came out clean.** Every field their Windows clients declare is
> a field their routes send. Only QRME's client had been written from
> imagination — fourteen records guessing at shapes nobody had driven — and the
> guard travelling is what turns that from *a bug we fixed* into *a fact we
> know*.
>
> PDI's copy could not be a copy. Its client builds each `HttpRequestMessage`
> itself and carries the tenant token beside it, so a binding regex written for
> this product's `Get(path)` helper finds zero calls over there — and zero found
> reads exactly like zero wrong. Its version asserts on its own extractor for
> that reason. JIM's copy arms the crash watch and builds an adaptation profile
> before it drives, because twelve of its fields only exist once the feature is
> on and driving into a state beats recording that you did not.
>
> #### Two things the port fixed here as well
>
> The record parser counted a wrapped reason — an indented `#` continuing the
> line above — as an empty row. This repo's record has no wrapped lines yet, so
> nothing was failing; JIM's does, and it failed there first. Fixed in all
> three, because the next reason worth writing here will be too long for one
> line.
>
> And a deliberately malformed injection, made while checking JIM's guard fires,
> showed the record-block regex will run one record's body into the next when a
> paren is unbalanced — reporting fields against the wrong record name, which
> reads as a real finding and is not one. All three now assert that no extracted
> body contains another record.

## app-v0.56.4 — QRME app-v0.56.4

- Published: 2026-08-07
- Commit: `5a1e968242e55f6721deefe23ae96b8c392c3a25`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.56.4>

> ### A client record is a claim about a route, and nobody had checked one
>
> `share` sat on the collision record as *a double and an int*. The int was
> `DesigneeRow.share` — a percent of a legacy's proceeds, real and correct. The
> double was `CompositionSource.share`, and chasing it turned up something the
> collision record had no way to say:
>
> ```csharp
> public record CompositionSource(
>     [property: JsonPropertyName("name")] string? Name,
>     [property: JsonPropertyName("share")] double? Share);
> ```
>
> `GET /profiles/{id}/composition` has never sent `name` or `share`. It sends
> `source_profile_id`, `display_name`, `weight` and `aspect`. Both fields
> decoded to null on every response the route ever returned, and the Windows
> blend button —
>
> ```csharp
> string.Join(" · ", (c.Sources ?? []).Select(x => x.Name));
> ```
>
> — drew a row of separators with nothing between them. It had never been run.
>
> **Fourteen records had the same disease.** `avatar` promised an `ai_badge` and
> a `likeness_of` that no route in this product emits. `/pair` read `built`
> where the server says `console_built`. `/tutorial` hedged across `chapters`
> *and* `lessons`, because whoever wrote it did not know which. `/dock/where`
> typed `screen` as a string for a value that is an integer. `/tutorial/start`,
> `/tutorial/done` and `/tutorial/progress` all decoded as a step when all three
> return a wrapper *around* a step. `RosterSibling` read `id` where the roster
> sends `profile_id`. Every one of them was a guess at a shape, written without
> driving the route, and every one shipped.
>
>     asked     do the names match
>     mattered  did anybody ever run the route
>
> #### The guard
>
> `tests/test_the_shape_the_client_expects.py` reads the Windows client's GET
> bindings — `Send<T>(Get("/path"))` — drives each against a live app, and
> asserts that every `JsonPropertyName` in `T` is a key the route actually
> returned. One level of nesting is followed, so a card's row type is checked
> against the rows.
>
> The assertion is one-directional on purpose. A record *omitting* a key is
> fine; a client decodes what it needs. A record *declaring* a key the route
> never sends is a promise the wire does not keep.
>
> Its own extractor was the first thing it caught. The regex that carves a
> record out of the file consumed the closing paren, so the field regex — which
> needs a `,` or a `)` after each property name — silently dropped the **last**
> field of every record. That is where `share`, `built` and `kinds` all sit. A
> count of wire names below the sibling guard's flat count now fails the suite.
>
> #### What the record says now
>
> Eight rows are in `tests/wire_shapes_unverified.txt`: fields that are real and
> simply absent in the fixture's state. `verification.level` appears the moment
> somebody has verified the profile. Each row names the state that produces it,
> because a guard that cannot tell a conditional field from a fiction is a guard
> nobody can trust. Ratcheted.
>
> #### The collisions the client had been hiding
>
> Correcting the records made the sibling guard fail with two names it had never
> seen: `kinds` and `refused`. Both were always colliding on the server — a
> string list of pairable device kinds beside an object list of overlay kinds; a
> boolean *this answer refused* beside a list of refusals. The client simply had
> not declared enough of the wire for the count to be true.
>
> The ratchet forbids the record growing, and that is the ratchet working: the
> answer is to pay down, not to record. Three names were split so each meaning
> has its own —
>
> * `total` → `total_amount` on the payout receipt and the gift box (money),
>   leaving `total` to the counts it also meant;
> * `threshold` → `ready_when` on voice enrollment (a samples-and-seconds
>   object), leaving `threshold` to the watermark's actual float threshold;
> * `share`, struck, once `CompositionSource` stopped inventing one.
>
> The record closes at 23, down from 24, with two names in it that were true all
> along and invisible.

## app-v0.56.3 — QRME app-v0.56.3

- Published: 2026-08-07
- Commit: `06037a170789add73bf517a26ec3d996fbbbe7de`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.56.3>

> ### The count and the state wore the same name
>
> 0.56.2 recorded 28 wire names in this product carrying more than one type, and
> said the record was the finding. Four of them turn out to be the *same*
> finding, four times over: **a boolean state and a count of that state sharing
> one field name.**
>
> | name | the state | the count |
> |---|---|---|
> | `seen` | has this inbox item been seen | how many were just marked seen |
> | `available` | is this desk free right now | how many packs a registry has |
> | `revoked` | is this grant revoked | how many contributions were revoked |
>
> That is the sharp kind of collision. A decoder handed `1` where it expects a
> boolean coerces rather than refusing, so a client asking *is this desk
> available* against the wrong route gets **yes** from a count of one — a
> plausible answer, arrived at from the wrong evidence, with nothing anywhere
> that would notice.
>
> The counts are renamed: `marked_seen`, `available_packs`, `revoked_count`. The
> states keep the names they always deserved. `InboxPage.unseen` already had the
> instinct next door.
>
> ### The fourth was a client bug, not a collision
>
> `reattested` is a boolean on the wire everywhere — every route coerces the
> 0/1 column with `bool()` before it leaves. The Windows client declared
> `int Reattested`, which means its decoder would have thrown on every objection
> status fetch. Nothing in the collision record could have told the two cases
> apart; reading the backend did.
>
> The record drops from 28 rows to 24, and the ceiling with it.

## app-v0.56.2 — QRME app-v0.56.2

- Published: 2026-08-07
- Commit: `ea902a18d5aec1b92fc93428dae315cfc0e486fd`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.56.2>

> ### The compiler nobody ran
>
> JIM-mini shipped a TypeScript error on `main` for several releases —
> `PresenceSpoken incorrectly extends PresenceBeat`, because one wire field name
> carried three incompatible types across its API. It survived because **no suite
> in any of these three repositories ran `tsc`**.
>
> This console typechecks clean and always did, but that was luck rather than a
> guarantee: nothing was checking. `tests/test_one_name_one_type_on_the_wire.py`
> now runs `tsc --noEmit` here too, and adds the general guard — reading every
> `JsonPropertyName` in the Windows client and failing when one wire name carries
> two types.
>
> **28 collisions found in this product**, recorded and ratcheted: `sources` is
> four different types, `messages` and `watermark` are three each, and `seen`,
> `revoked`, `reattested` and `available` are each a boolean in one place and a
> count in another — the sharp kind, because a decoder coerces rather than
> refusing and the reader gets a plausible wrong answer.
>
> Nothing is renamed here this round. The record is the finding; fixing 28 names
> across a console and three shells is its own work, and doing it badly in a
> hurry is how a rename becomes an outage.

## app-v0.56.1 — QRME app-v0.56.1

- Published: 2026-08-07
- Commit: `e7ced059224e6db186f0176c0a5fe18099addb31`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.56.1>

> ### Cut together at one version
>
> The three products are cut at one version, so this release exists here to keep
> that true. **No code changes in this repo this round.**
>
> JIM-mini gained an offline fine-tune: a pass that reads a user's own answered
> follow-ups and trains weights by gradient descent, on their machine, with the
> network blocked — beside the adaptation profile that conditions a prompt, and
> deliberately in a separate table, because a reader who cannot tell which of the
> two they have has been told nothing useful.
>
> PDI implemented its KMS/HSM key provider, which had been a documented
> `NotImplementedError`. It unwraps a stored blob rather than fetching a key, binds
> the blob to the deployment with an encryption context, and refuses rather than
> falling back to a local key when the key store is unreachable.

## app-v0.56.0 — QRME app-v0.56.0

- Published: 2026-08-07
- Commit: `9527a72bc199ae45c2abe02284bf70c2ca65a1b9`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.56.0>

> ### The count of what was synthetic
>
> `attention.py` closed one half of the multiplicity problem: a profile talks to
> many people at once, and the number is offered rather than discovered. The
> other half was never reported at all. **A person can spend months here in
> conversation that is entirely synthetic, and the platform is the only party in
> a position to see it.**
>
>     asked     does a profile disclose how divided its attention is
>     mattered  does anybody tell the person how one-sided theirs has been
>
> `qrme/solitude.py` counts the turns in this account's own logs over 28 days —
> how many went to a profile, how many reached a person through a matched
> connection or a room — and reports the two numbers to that person and nobody
> else. Above 95%, with at least twenty turns behind it, the answer also carries
> a door: JIM-mini, which is built around somebody's own week rather than around
> keeping them here.
>
> ### What it refuses to be, and what holds each refusal
>
> The counting is thirty lines. Nearly all of the work is the four things this
> must never become, because each is what a product with a growth target would
> build instead — and each has a test that the wrong version fails:
>
> * **Not a diagnosis.** The module does not decide anybody is lonely and the
>   word appears nowhere in what it returns. It cannot know: somebody with a full
>   life may talk to a profile every evening for reasons of their own. A count is
>   a fact; *"you seem lonely"* is a verdict this software has no standing to
>   reach and no way to check.
> * **Not a notification.** Nothing is pushed and no beat fires. A product that
>   watched somebody's conversations and then messaged them about it would be
>   performing the surveillance the count exists to disclose.
> * **Not readable by anybody else.** No route reaches it from outside the
>   person's own account — no owner view, no aggregate, no moderation queue. The
>   moment a second party can read it, it becomes a tool for finding the visitors
>   who have nobody else.
> * **Never carries a word anybody wrote.** The handoff is counts and a window.
>   JIM-mini is a health guardian; a referral from here carrying conversation
>   content would hand a medical product the transcript of somebody's private
>   evenings under the banner of helping.
>
> Declining is recorded and the offer does not return. An offer somebody declined
> that reappears next month is the product overriding an answer it already got,
> and the second asking is worse than the first.

## app-v0.55.0 — QRME app-v0.55.0

- Published: 2026-08-07
- Commit: `7249c0ab91310999956b9443863d480fefab3da9`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.55.0>

> ### The rule the record stated, with something behind it at last
>
> `tests/field_labels_unmapped.txt` records the request-model fields that keep
> their API identifier in a 422 instead of the label a form shows, and its header
> gives a sound reason for each of them: enum members a control sets, ids a
> client fills in from the resource it is already looking at, flags a switch
> owns. Then it states the condition under which a row stops being defensible:
>
> > Map one when a form starts asking a person for it; the ceiling does not move
> > up.
>
> That sentence was the whole policy, and **nothing was checking it**. The
> ceiling stops the list growing. It says nothing about a field already on the
> list that a screen quietly grew an input for — the record would go on
> shrinking, every test would stay green, and the field would sit there being
> typed into a box by a person and named by an identifier in the refusal
> underneath it.
>
> It had already happened. `app/src/screens/Blend.tsx` has been asking for
> **share** and **their…** — labelled, in ten languages — since the blend screen
> was localized, and posting both up as `sources[].weight` and `sources[].aspect`.
> A German reader who left the box empty was told:
>
>     Quellprofile, kommagetrennt.0.weight — Pflichtfeld
>
> a sentence in their language with the API's English name for the box in the
> middle of it. Both fields now carry the label the form shows, borrowing the
> form's own noun in each language so the refusal and the box agree by
> construction rather than by somebody keeping them in step. The record drops
> from 123 rows to 121 and the ceiling follows it down.
>
> ### The part that outlasts the two fields
>
> `tests/test_a_form_that_asks_for_it_has_a_label_for_it.py` reads the screens
> and asks the question the record could not: is any field **both** bound to a
> form control and sent in a request body, without a label? The AND is the whole
> guard — screens are full of object literals, and control bindings alone match
> local state that never leaves the browser. Either half alone reported dozens of
> fields no person types into; together they find exactly the population
> `_FIELD_LABELS` exists for, and QRME's is 52 fields, all of them now labelled.
>
> The guard earned its place on its first run by failing on work done ten minutes
> earlier: the Arabic label read *الجانب الذي يخصّه* where the form says
> *ما يخصّه…*, close enough to look finished and not the same words. The label
> was changed, not the check.
>
> Ported to JIM-mini and PDI in the same shape. PDI's copy of the record admits
> in its own header that a 0.46.4 sweep found **forty** rows with a control on a
> form and no label beside it — that sweep was somebody reading every screen by
> hand, and when it finished nothing was left behind to notice the forty-first.
> Now something is.

## app-v0.54.1 — QRME app-v0.54.1

- Published: 2026-08-07
- Commit: `945763a8923e5a5795213b6eceec149f8e5f59c2`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.54.1>

> ### The twenty-four, read one at a time
>
> 0.54.0's new guard recorded twenty-four literals a shell shows that its own
> table already translates, and said sorting them was the work rather than a
> sweep. It was, and the split came out clean: **twelve were labels and are now
> keys; twelve are values and stay English.**
>
> The labels: the steering group headings — *Behavior*, *Intimacy (18+)* — on
> Android and Windows, the tier names *Friendly* and *Rated 18+* and the
> *Lifetime* total on Android, the packs **Download** button on both phones, and
> the signature attestation. That last one is the one worth naming: *"I attest
> this is accurate and complete"* was pre-filled in English on two shells while
> `nsig.attest` sat translated ten ways beside it. `meaning` is free text the
> server stores as given, so somebody signs in the words **they** would use
> rather than the ones this app happens to be written in.
>
> The values are values, and each was read rather than skipped: `stranger`,
> `professional` and `grandchild` are relationship kinds the steering API
> matches on; `standard` is a SwiftUI `.tag()` whose label was localized all
> along, so the guard was seeing the tag beside it; `restricted` is the fallback
> when the server does not name a profile status, so it must be the word the
> server would have sent. Translating any of them turns a working form into a
> 422.
>
> ### A split the sort exposed
>
> `nmg.pack.robot` (*🤖 ROBOT*) and `nmg.pack.robot.tasks` (*🤖 ROBOT TASKS*)
> were **both held by all three shells** for the same badge on the same kind of
> pack — iOS rendering one, Windows the other, Android the short one. One badge,
> one word, one key: all three now use `.tasks`, and the short row is deleted
> from all three tables rather than left translated ten ways for nobody.
>
> Dead-key ratchet: **328 → 311**, ceiling **139 → 134**.
>
> Cut together with JIM-mini and PDI at **app-v0.54.1**.

## app-v0.54.0 — QRME app-v0.54.0

- Published: 2026-08-07
- Commit: `a97e9b1f788297a4ea9826babdb6ee789c98261c`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/qrme/releases/tag/app-v0.54.0>

> ### The shells that say less
>
> `native_dead_keys.txt` has held ~335 rows for several releases: strings a
> shell has translated into ten languages that nothing in that shell asks for.
> 0.47.9 corrected what the number *means* — 263 of them are asked for by a
> **different** shell, so they are not waste, they are a to-do list about
> screens. Each is the same question: this screen exists on all three shells, so
> why does one of them say less?
>
> This round answers it for the two the record had named, and then builds the
> guard that finds the rest.
>
> **The iPhone had no camera-permission state.** `configure()` hit
> `AVCaptureDevice.default(for: .video)`, failed, and returned — leaving a black
> `CameraPreview` with *"point at a beacon"* floating over it. Somebody who
> declined got a dead screen and no reason. `nbcn.camera` and `nbcn.nothing`
> were sitting in that shell's own table, translated ten ways, read by nothing.
> The second is the one that mattered: *"Nothing is recorded — frames are read
> and discarded"* is a promise about what this app does with a camera, and only
> Android readers had ever been given it.
>
> **Windows was printing "scan(s)" and "picked up" in English.**
> `ReachPage.ReloadBeacons` built its detail line from string literals while
> `nmg.beacon.scans` and `nmg.beacon.pickedup` sat translated beside them. An
> owner reading the app in German saw *"Garten · 3 scan(s) · picked up"* —
> translated chrome around the two words carrying the meaning.
>
> ### Then the guard, and what the guard's own injection found
>
> `test_a_shell_does_not_print_what_it_translated.py` extracts every string
> literal from every screen and compares it against that shell's own table. It
> found three more immediately: Windows typing out *"Enter a display name and a
> persona to continue."* and *"No profile here produced this text."*, Android
> typing out *"Steering applied — it rides on every reply."*
>
> **The first version of that guard could not see the bug it was written for.**
> It matched assignments into display properties — `.Text =`, `.Content =` — and
> the beacon line was a literal inside an interpolated string in an object
> initializer. It reported all three shells clean. The injection pass caught it,
> and the detector now extracts literals rather than matching positions.
>
> A first, broader draft reported 88 hits of which 86 were protocol values —
> JSON field names, defaults a form posts back. That version is not in the
> repo: a guard that cries wolf 86 times out of 88 is one nobody reads. What
> ships skips single short words and reads only the view directories, with 24
> rows recorded and ratcheted. Sorting those is real work rather than a sweep —
> a **label** is read, a **value** is posted back to a route that compares
> against English, and translating one of those turns a working form into a
> 422.
>
> Dead-key ratchet: **335 → 328**, ceiling **143 → 139**.
>
> Cut together with JIM-mini and PDI at **app-v0.54.0**.

