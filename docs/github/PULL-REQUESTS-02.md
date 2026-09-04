# qrme — pull requests

Every pull request opened against <https://github.com/davidsbianchi1984/qrme>, newest first, with the body as written. The body is the argument for the change; git keeps the diff but not the argument.

**351 pull requests, 348 merged.**

This is one part of a page GitHub is too long to render whole — see [PULL-REQUESTS.md](PULL-REQUESTS.md) for the rest.

**#240 to #132.**

## #240 — Bodies, and where a rated profile is marketed

- merged · opened 2026-07-31 · merged 2026-07-31
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/240>

> The two blocks left from the placements/robots backlog. Eleven routes, doorless backlog **100 → 89**. Screens **162** and **163**.
>
> Both were built by driving the running server, and both had a trap that a route signature hides.
>
> ## 163 — Bodies
>
> The native shells already drove the catalogue, the binding and a command button, so the three routes describing what a body has *become* had no caller anywhere. Three list-shaped things here have almost the same name and mean different things:
>
> | | is |
> |---|---|
> | `robot.commands` | what this model of body accepts at all — the buttons |
> | `GET /robots/{id}/commands` | the audit log of what it was told to do |
> | `GET /robots/{id}/skills` | task modules from a pack, which **extend** the first list |
>
> A screen built from the route names puts the log where the buttons belong, and it typechecks.
>
> **The steering write takes `values`, not `dials`.** `SteeringSet` is `{values: dict}` with a default of `{}`, so a body keyed anything else is accepted, ignored, and answered `200` with the dials unchanged — no error, no log line, nothing to notice. `dials` is the obvious guess because that is what the *read* calls the catalogue. Found by writing and reading back; both halves are guarded now.
>
> Each installed skill's `procedure` renders verbatim, because every one of them names what the body will *not* do — *reminders only: never dispense*, *companionship, not care, and never a substitute for human contact* — and that limit is the sentence somebody pointing a robot at a relative needs to read. `behavior_profile` is drawn beside the dials: pace becomes motion eagerness, autonomy becomes initiative, assertiveness becomes firmness. It is the difference between a slider and an explanation.
>
> Steering is Pro-gated, so the 402 lands as the upsell card added last round.
>
> ## 162 — Where it is marketed
>
> An adult-mode profile advertised at an adult venue — a creator platform, a directory — as a link or a printable code. Only defensible because of the sentence every venue carries, rendered verbatim and never paraphrased:
>
> > every summon of a rated profile resolves through QRME's 18+ age wall, regardless of where the QR or handle was found
>
> The wall does not travel. Shortening that to "18+" drops the load-bearing half, so a test asserts the clause is still on every venue and that the console renders `v.note` rather than keeping a second copy.
>
> Three things only the running server showed:
>
> - **`scan_url` and `summon_url` are not interchangeable.** One is where a phone camera lands and what the code encodes; the other is the JSON surface for clients. Publishing the wrong one hands somebody a page of JSON, so the screen labels both;
> - **`funnel.chat_rate` is null, not zero**, until something has got through the wall. `(null).toFixed()` is `"0"` in JavaScript rather than an error, so an unchecked screen publishes a conversion rate nobody measured. It reads *"nothing has got through yet, so there is no conversion to quote"*;
> - **taking a placement down deactivates the beacon rather than deleting it** — a code already printed at a venue stops resolving instead of being reissued to point somewhere new. That is the safety property, and the screen says it as it happens.
>
> The list and create shapes differ on both surfaces, so the screens derive what they show rather than assuming the richer response came back. The placement list's link is labelled **"open here"** on purpose: the published address uses the configured public host and this one uses whatever API the console is pointed at — same route, different host, and quietly calling this one "the link" would hand somebody the wrong address to print.
>
> ## Run, not just built
>
> Both screens driven in Chromium against a live backend: a body bound, commanded (`tidy` → queued, and in the log a second later) and steered; a placement made, its QR fetched from the API and rendered at 296×296, the funnel read with the null rate reported as an absence. Every tab including the two new ones verified clickable at 1200px and 800px — the sidebar reservation added last round still holds with two more entries in it.
>
> ## New tests
>
> `test_bodies_and_placements_have_doors.py` — 35 tests. The steering write reads back; a dial clamps rather than refusing; intimacy is never a body dial; the dials become a behaviour profile; the three lists stay three different things; a disallowed command is refused *by name* (which is why the screen can show buttons); unbinding says unbound rather than deleted; every venue still carries the clause; only an adult-mode profile is placed; both urls exist and differ; the list shape stays different from the create; the rate is absent rather than zero; walled + verified sums to scans; a takedown 410s the printed code; and the console half of each.
>
> Four injection-verified against the exact defect each describes: gutting `set_dials`, sending `{dials:…}`, dropping the null check, and softening the venue clause.
>
> **Suite: 1495 passed.**
>
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #239 — A door for the guide, a refusal with its structure kept, and the plan it names

- merged · opened 2026-07-31 · merged 2026-07-31
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/239>

> Three commits, each one found by building the door to the one before it. Doorless backlog **116 → 100**.
>
> ## `4677a10` — A door for the guide itself
>
> Twelve routes: the walkthrough (×7), the help topic index, and the helper dock (×4). The least comfortable set to have found — the product has a written walkthrough that works with no model configured, names the screens each step is about, and is held to the gallery by a test, and there was no way for anybody to take it. Screen **160**, `Guide.tsx`.
>
> Building it produced its own mistake immediately: the lesson introducing the walkthrough said it was "thirty-eight written steps", which was true when the sentence was typed and false one line later. `test_lessons_do_not_count_themselves.py` guards the shape rather than correcting the number — a count in prose is a fact about a collection embedded in a member of it, so the act of adding a member falsifies it. The live number is `total` on `GET /tutorial/progress/{id}`.
>
> ## `ad11fa3` — Keep the structure of a refusal that was built to have one
>
> Several gates answer with an **object** rather than a sentence:
>
> ```
> {"reason": "plan", "capability": "builders", "needs": "pro", "have": "free",
>  "price_usd": 130, "period": "month", "message": "…",
>  "billing": "simulated — no real funds move"}
> ```
>
> Somebody built that on purpose — it is strictly more work than returning a string and the only reason to do it is so a screen can draw a real answer. `req()` then did `JSON.stringify(detail)` and threw the result as the error message, so every screen that catches an error and shows `.message` showed the raw object. Nothing failed: the request was right, the refusal was right, and it was destroyed on delivery.
>
> `RequestError` carries `status` and the untouched `detail`, `planGate()` reads the structure back out, and `Refusal.tsx` decides how to draw it. The price and *simulated — no real funds move* render on the same line, because a screen quoting $130 a month without them would make a claim this product avoids everywhere else.
>
> ## `564457e` — The plan a refusal names
>
> Drawing the refusal properly found the next thing: there was **no plans surface**. `GET /plans` and the three `/memberships` routes had no caller either, so the console could refuse you for not having Pro and had no way to sell you Pro. That is worse than a flat no — an offer naming a plan in a product with no way to join one advertises something that appears not to exist.
>
> `Plans.tsx` is that door (screens **130**, **131** — already drawn, never claimed by a component), and `onPlans` is threaded from the shell into every screen that can be refused.
>
> Fixing the transport was also only half of it. Every screen threw the same structure away one layer up — `setError((e as Error).message)`, in all of them. They now hold the error and hand it to `Refusal`, which keeps each screen's existing look for an ordinary failure and draws a gate as a card with a button. A test fails on the flattening pattern reappearing anywhere under `app/src`.
>
> Driven against a running backend first. Two things only the live server showed:
>
> - **`period` is null on the unpaid tiers**, not `"month"` at zero — a screen printing "$0 a month" would be inventing a subscription;
> - **`visitor` and `free` are different plans that both cost nothing.** One is somebody with no account reading a public page; the other is an account whose work sits in the platform's database in the clear. A picker written from the price alone collapses them into one $0 row and hides the entire argument.
>
> Then clicked, in a real browser, which found one more. The always-on agent-lights widget is fixed to the bottom-left corner **on top of the sidebar**, and the column had grown long enough that its last three tabs were underneath it — Playwright reported the click landing on the lights. That is the same fault the phone layout was fixed for in an earlier round, when the widget covered Home and Chat and the tabs were reported as broken screens; the desktop half had simply not grown into it yet. The sidebar reserves the widget's footprint, and the test asserts the arithmetic rather than the number so the next tab is safe.
>
> Verified end to end against a live backend: a free account pressing **Buy** on a listing gets a real 402, the card renders as `PRO — marketplace` with the sentence, the price and the billing note, and **See the plans** lands on the Plans screen.
>
> ## New tests
>
> | File | Tests | What it guards |
> |---|---|---|
> | `test_lessons_do_not_count_themselves.py` | 42 | no lesson (or README, `help.py`, `api.ts`, or any `.tsx`) states how many lessons there are |
> | `test_gates_answer_in_a_shape_a_screen_can_use.py` | 12 | the gate still answers with the object, and `req()` does not stringify it again |
> | `test_the_refusal_has_somewhere_to_send_you.py` | 21 | the four plan routes have a caller, `visitor`/`free` stay apart, capabilities stay keyed the way the gate refuses, the shell threads `onPlans`, no screen flattens the error, the sidebar reserves the widget |
>
> All injection-verified — each guard was confirmed to fail against the defect it describes.
>
> **Suite: 1458 passed.**
>
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #238 — A door for contesting a profile that depicts you

- merged · opened 2026-07-31 · merged 2026-07-31
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/238>

> Nine routes with no caller, including the takedown path for a product whose whole subject is synthetic people who can be mistaken for real ones. Somebody who found a profile of themselves had no way, from here, to say so. The doorless backlog falls **125 → 116**.
>
> ## Two properties, side by side, because either alone would be unfair
>
> **Opening an objection restricts the profile immediately** — public surfaces off, no new interactors — *before* anybody reviews it. Waiting out a review while the thing you are contesting goes on meeting people is not a protection.
>
> **`prior_status` sits right beside it**, because that restriction is only defensible if it is reversible: a dismissal puts the profile back to exactly what it was, active or a departed memorial.
>
> ## Objecting needs no account, and the screen says so
>
> The route is public on purpose. A person who has just found a profile of themselves should not have to join the platform hosting it in order to object to it. What they give instead is a proof reference pointing at an identity check held elsewhere — not a login, which is precisely what lets them object without one. Left unsaid, most people would assume they had to sign up first.
>
> ## The audit panel states `vault_backed` in words
>
> *Tamper-evident* is a claim that depends on a PDI vault being configured. Where none is, the timeline is still the timeline and nothing is hash-chained — showing the events without that caveat would overstate what the deployment actually has.
>
> ## The two shortcuts, with their asymmetry named
>
> The subject may **withdraw consent**; an estate may **revoke authorization**. Both skip review entirely and terminate the profile at once, even mid-review, because a standing party's rights outweigh preserving it. Each applies to one rights basis only, and the refusal on the wrong basis names the profile's actual one.
>
> ## Checks
>
> - 1383 passed — full suite
> - 15 response shapes verified field-by-field against a running server, including the behavioural claims the screen makes: that opening really does restrict at once and record the prior status, that dismissal really does restore it, that uphold terminates, and that a shortcut used on the wrong rights basis names the profile's actual basis in its refusal
> - `npm run build` and `tsc --noEmit` clean
>
> Follows `8fa5989`, which fixed the fail-open on the reviewer gate these routes sit behind — kept as a separate commit so it is reviewable on its own.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #237 — Reviewer development mode meant everybody, not localhost

- merged · opened 2026-07-31 · merged 2026-07-31
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/237>

> `auth.require_reviewer` guards the two most destructive operations in the product:
>
> - `POST /objections/{id}/resolve` — upholding **terminates a profile and erases its content**
> - `POST /profiles/{id}/succeed` — **hands a profile to a different owner**
> - (and `GET /objections/{id}/audit`, which quotes the objector's stated reason)
>
> Both sit outside profile ownership on purpose — an owner must not adjudicate an objection against their own profile — so the gate is a deployment secret, `QRME_ADMIN_TOKEN`.
>
> **With that variable unset the function returned unconditionally, for any caller from any address.** On a deployment where nobody set it, an anonymous caller on the internet could erase any profile and take ownership of any profile.
>
> ## Why this is worth more than the four lines it took to fix
>
> **The docstring was the bug.** It said:
>
> > Unset = development mode (open, for local use only), matching PDI's admin convention
>
> Nothing enforced the local part. And it did not match that convention — `cloudgw._caller` has had the localhost check the whole time:
>
> ```python
> if not configured:
>     host = request.client.host if request.client else ""
>     if host in _LOCAL_CALLERS:
>         return "local-dev"
>     raise HTTPException(503, ...)
> ```
>
> The code did what it claimed in every respect except the one that mattered, which means reading it carefully is exactly how somebody would have concluded it was fine.
>
> **It failed open on the deployment least able to notice.** An operator who configured the token was never affected. An operator who had not — a first deploy, a staging box that got a public address, anybody following a quickstart — was the one exposed.
>
> ## The fix
>
> Fails closed the way the gateway already did: a local caller keeps the development path, a remote one gets a **503 naming the variable to set**, so the refusal is actionable rather than merely closed.
>
> ## Tests
>
> `test_reviewer_dev_mode_is_local_only.py`, 10 tests, verified by reverting the fix and watching 4 fail. They cover both halves plus two cases that are easy to lose:
>
> - **a configured token still gates by the token** — the address must not have quietly become the check, so a local caller with the wrong token is still 403 and a remote caller with the right one is allowed;
> - **the owner-fallback path still works.** `_require_owner_or_reviewer` is written as `except HTTPException: … require_owner(...)`, so making the reviewer check raise in a new case changes which branch a real request takes. An owner reading their own case must still get through.
>
> ## Checks
>
> - 1383 passed — full suite (up 10)
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #236 — Doors for what is live in a place, and one rule under three features

- merged · opened 2026-07-31 · merged 2026-07-31
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/236>

> Twenty routes with no caller: a camera being shared, a microphone lent to the profiles in a room, a face drawn over a camera. Three features that look separate and are one, because the same rule holds all of them — **whatever you put between yourself and the people around you, they are told.** The doorless backlog falls **145 → 125**.
>
> ## Three things rendered verbatim
>
> Each is an argument the backend already made carefully, and a paraphrase would be a worse version of it.
>
> **The `never` list on a live session.** A viewer cannot zoom, focus or switch lens; cannot take a photograph or start a recording from their side; cannot reach any other camera on the device or network; gets no coordinates; cannot begin a session without the holder starting it in the moment; and there is no state where it is running and not visible on the holder's own screen.
>
> **The refusal when a profile is asked to watch a person's body** — a paragraph about accountability rather than a rule name, and the most important sentence in the feature:
>
> > A profile watching a body in real time would be making judgements about it with no examination, no accountability and nobody to answer for being wrong — and unlike a still, there is no moment somebody chose to send.
>
> The screen shows it *before* the button, not after the attempt.
>
> **`why_it_is_yours` on the bystander note.** The platform declines to promise anything about who walked into shot, because it cannot see the room. A reassurance about something it cannot observe would be worth nothing, and saying so is the honest version.
>
> ## A bug this found in my own screen
>
> The camera and the microphone accept **different sets of surfaces**:
>
> | | surfaces |
> |---|---|
> | camera | `connection, desk, exchange, room` |
> | microphone | `connection, desk, party` |
>
> A watch party takes a lent microphone and refuses a shared camera; a room takes a camera and lends microphones through its own route. The first version of this screen had one picker built from the microphone's vocabulary, so sharing a camera into a party would have 422'd every time.
>
> Invisible to the typecheck — they are strings on both sides — and caught only by driving it. There are two pickers now, and the verification asserts the two sets *differ* rather than quietly using whichever happens to work.
>
> ## Checks
>
> - 1373 passed — full suite
> - 30 response shapes verified field-by-field against a running server, including that the overlay disclosure really does contain "a real person is underneath", that `liveCameras` returns a bare array rather than a wrapper, and that a profile watching a person is refused with the whole paragraph
> - `npm run build` and `tsc --noEmit` clean
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #235 — Doors for how a profile presents itself, everywhere it is seen

- merged · opened 2026-07-31 · merged 2026-07-31
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/235>

> Twelve routes with no caller, across three audiences that are not the same audience: the page somebody builds, the front page a stranger lands on from a scan, and the fixed screens the profile is shown on. The doorless backlog falls **157 → 145**.
>
> ## `/pages/themes` was written for a door that never got built
>
> It publishes the allowed HTML tags and CSS properties, with this comment beside them:
>
> > Published so an editor can grey out what it knows will be stripped, rather than letting somebody write it and lose it.
>
> Nothing was reading them. So the editor now lists the surviving tags **before** you write, and shows `html_removed` after a save — because the save succeeds either way. Without that, a `<script>` disappears and the page quietly does less than its author wrote, with no indication it ever contained anything else.
>
> Same reasoning for `about_blocked`: the owner's view carries moderation's reason so the text can be fixed rather than silently dropped.
>
> ## The display asymmetry, made visible
>
> What a given screen is **showing** is public — a fixture in a corridor displays to whoever walks past and cannot keep a secret from them. The list of an owner's screens is **not**, because that is a list of physical places. Two routes that look alike and are not, so the screen says which is which instead of rendering both as ordinary rows.
>
> The `never` list is rendered verbatim — what a fixed screen may never show, each entry with its reason. A wall panel is read by people who did not choose to look at it, and those sentences are that argument already made once, carefully. The backend refuses a forbidden face with the reason rather than the rule, for the same reason, and the screen passes it straight through.
>
> ## Scope changed mid-round, deliberately
>
> Placements were in the original cut. Reading `qrme/routers/summon.py` showed `/profiles/{id}/placements` is the **adult-venue marketing** surface — age wall, custody chain — not general placement. It does not belong in a screen about themes and wall panels, so it comes out and gets its own round rather than being a third of this one.
>
> ## Checks
>
> - 1373 passed — full suite
> - 21 response shapes verified field-by-field against a running server, including that a forbidden face is refused **with its reason**, that `html_removed` actually names the stripped tag, and that removing a display leaves the record at `live: false` rather than erasing it
> - `npm run build` and `tsc --noEmit` clean
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #234 — An identity door, and two refusals that never reached the caller

- merged · opened 2026-07-31 · merged 2026-07-31
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/234>

> Twenty routes with no caller, covering who a profile is and how it ends — including `DELETE /profiles/{id}`, so the console could make a profile and never remove one. The doorless backlog falls **177 → 157**.
>
> ## The screen (`156`)
>
> Arranged around the rule the feature turns on: **at most one of your profiles may be verified, because the badge says you are a particular real person, and said of two at once it is either false of one or a claim that you are two people.**
>
> So the roster comes first, and the badge is drawn as a thing that *sits on one profile and moves* rather than a checkbox each profile has and most fail. An invented person reads as **unverifiable** rather than as an empty box — those are different answers, and only one of them means somebody has not got round to it.
>
> The anonymity card puts `not_withheld` beside `withheld` at the same size. Anonymity here is a promise about what the platform publishes, not a promise that nobody can recognise your writing, and a screen showing only the first half would be selling the second.
>
> Both endings sit together because the difference is what happens to the people who knew the profile. Retiring leaves that readable; deleting returns a count per kind of record — twenty-five of them — which the screen itemises rather than summarising. *Deleted* is a claim; the numbers are evidence.
>
> ## Two backend bugs, found by building the door against it
>
> **A 500 with an empty body.** `POST /profiles/{id}/verification` caught `identity.IdentityError` and not `verification.VerificationError`. The two come from adjacent modules and only one was in the `except`, so an unknown proofing level — or a level above `self_asserted` with nobody named as having checked — raised straight through.
>
> The part worth recording: the exception it dropped carried the exact sentence the caller needed, naming all four valid levels. The work of explaining had been done and was then discarded by the wrong handler, which is worse than never writing it, because everything upstream looks careful.
>
> **An undiscoverable enum.** `GET /identity/vocabulary` is the route whose whole job is publishing the closed sets a client must offer. It described every rule about verification — who may hold the badge, that it moves, that an invented person is unverifiable — and omitted the four words a claim has to be made in. There was no way to build a level picker from the API; you had to read `qrme/verification.py`.
>
> Both are pinned by `test_verification_refusals_reach_the_caller.py` (8 tests), verified by reverting each fix and watching three fail. One test asserts the set the vocabulary *advertises* is the set the claim endpoint *accepts* — otherwise the fix is the original bug with a step added. Another asserts the 409 for the one-badge rule survived: a malformed claim is the caller's mistake, the one-badge rule is the product refusing something well-formed, and only the second tells you what to do instead.
>
> ## Two routes deliberately keep no door
>
> They stay in the backlog rather than getting buttons that lie:
>
> - `POST /profiles/{id}/succeed` needs a **reviewer** token by design — succession runs when the owner cannot authorise anything, so a button on the owner's own screen would 403 every press;
> - `POST /profiles/genesis` is a second creation path (a profile born from a short interview, which names itself). It belongs beside the first one in onboarding, not on a screen about a profile that already exists.
>
> ## Checks
>
> - 1373 passed — full suite (up 8)
> - 28 response shapes verified field-by-field against a running server, including the case that matters most: a profile both **verified and anonymous**, where `/badge` drops the attestor and returns `attestor_withheld` — "checked by Dr Okafor of St Mary's" would narrow an anonymous author to a city and a workplace
> - `npm run build` and `tsc --noEmit` clean
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #233 — Doors for the three two-party surfaces, and four tabs that showed their own key

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/233>

> Twenty-eight routes had no caller: the agreed exchange, the lent skill and the watch party. All three modules were complete and unreachable from the console. The doorless backlog falls **205 → 177**.
>
> ## Each screen is built around its feature's rule
>
> The mechanics are obvious and the constraint is not, so the constraint is what the screen has to carry.
>
> **Exchanges** (`153`) re-renders the whole agreement from every reply rather than patching what is on screen, so an edit that clears both signatures is something you *watch happen*. A screen that optimistically appended a row would show a signed agreement the server had already un-signed — precisely the failure the fingerprint rule exists to prevent. The `runs_warning` sits next to the signing button rather than in the manifest, because the moment to read it is before agreeing.
>
> **Lent skills** (`154`) never disables the close button by side. Two people open a grant, either one alone closes it, and the moment withdrawal matters is exactly the moment the person benefiting would not agree to it. The use log goes to both parties: a record only one side can read is not a record.
>
> **Watch together** (`155`) renders the profile's prompt instruction verbatim, in a panel of its own. A person whose profile is sitting in a room discussing a film can read what it was actually told about not having seen the video, instead of trusting that it was told anything.
>
> ## The types were checked against a running backend
>
> Written from the route signatures first, then driven against a live server — which is the only reason two of them are right:
>
> - `signatures[]` carries **`matches_current`**, the server's own computed answer to whether a signature still applies. Not the `fingerprint` field written down here from the signature alone, which does not exist on the wire — and which the screen was going to approximate by comparing truncated hashes by hand. (It is `true` in every reachable state today: the manifest can only be edited from `draft`, and `reopen` deletes the signatures on the way. So it is the backend checking its own invariant rather than assuming it, and the type says that rather than implying a live signal.)
> - `POST /exchanges/{id}/items` returns the **whole exchange**, not the item — so the new item's id comes out of the returned manifest.
> - `POST /watch-parties/{id}/members` likewise returns the whole party.
> - `channel` has **two different shapes** depending on `open`, so `ExchangeChannel` is a union rather than one type with optionals.
> - `POST /watch-parties/{id}/end` returns a summary of what it shut down and nothing party-shaped.
>
> A typecheck proves the code agrees with what was written down. It cannot prove what was written down is true. 34 shapes verified field by field on a live server.
>
> ## Four tabs have been rendering their own identifiers
>
> `t()` ends `|| key`, so a tab with no entry puts `nav.market`, `nav.delegate`, `nav.desk` and `nav.voice` in the sidebar — in every language including English. `NAV` carried the correct English `label` one line above the icon, and nothing read it: two sources of truth with the unused one looking authoritative.
>
> It also failed in the direction that hides. A blank label looks broken and gets reported; `nav.market` looks like a name somebody chose, and nobody files a bug about a tab that has a name.
>
> `test_nav_labels_are_localised` now fails on all three ways it can recur — a tab with no entry, an entry missing a language, and the unused `NAV.label` disagreeing with the l10n row. Verified by injection.
>
> ## Also
>
> - Three tutorial lessons, three gallery rows, three `ui_screens.txt` entries, helper-dock keyword routing for all three, and a console-door paragraph in each of the three README sections.
> - `*.db` never covered SQLite's `-shm`/`-wal` sidecars, so running the backend once left untracked noise in everybody's `git status`.
>
> ## Checks
>
> - 1365 passed — full suite (up 6: the new nav guard)
> - 34 response shapes verified against a running backend, exercising both parties, both refusal paths, and the void-on-edit rule
> - `npm run build` clean; `tsc --noEmit` clean
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #232 — Record what breaks on the phone and the desktop shell too

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/232>

> The console has recorded failures content-free since 0.19.0 — the operation and the status, never the message, never the path as it was actually called. The three native shells recorded nothing at all, so every failure a user hit on iOS, Android or Windows was invisible.
>
> ## The rule, in three more languages
>
> | | |
> |---|---|
> | `native/ios/Sources/Problems.swift` | `UserDefaults`, `Codable` rows |
> | `native/android/…/Problems.kt` | `SharedPreferences`, JSON rows |
> | `native/windows/Problems.cs` | `%LOCALAPPDATA%/QRME`, `System.Text.Json` |
>
> Each takes `method`, `path`, `status` and has no parameter a detail string could arrive through. The signature is the safeguard, and it matters here specifically: the backends put user input straight into their error messages — a device name, a body site, a language code. Good messages for the person reading them and the wrong thing to keep, so they are shown and never written down. Redaction happens on the way *in*, so the stored buffer never holds a value that would later have to be scrubbed.
>
> `POST /profiles/{id}/chat → 500` identifies a bug; `POST /profiles/prf_0de08e794ed0/chat` identifies a person. Only the first survives.
>
> ## Why the tests are structural
>
> One rule with four implementations drifts, and it drifts silently — a redaction narrowed on Android leaks nothing on the desktop, so nothing an ordinary test run would notice. There is no test runner for these sources here; the native workflow compiles them and stops. So `test_native_shells_record_nothing_private.py` reads them the way the TypeScript guard reads `errors.ts`: signature arity, stored fields, the four redaction patterns at full width, the FNV-1a constants, and both failure kinds at the call sites — including the request that never reached a server, which is the case an implementation forgets because it is an exception rather than a status.
>
> The suffix bound is checked by name because it has already gone wrong once: requiring six hex characters let `cap_9f2`, `req_77aa` and `usr_1` through when the console's version was written. A shell that quietly restored that bound would leak on that platform alone.
>
> What the file cannot check is behaviour: that Swift's FNV-1a and Kotlin's produce the same digits is asserted by neither, only that both are FNV-1a with the same constants. Stated in the file rather than hidden.
>
> ## The defect writing that guard exposed
>
> `Problems.attach` existed and was called nowhere. The Android shell would have recorded nothing and said nothing about it, because the recorder refuses to crash over a diagnostic — a missing attach has no symptom at all. Every structural check above passed while the feature was simply off on that platform.
>
> Worth naming as a class rather than a typo: those checks ask whether each piece is *correct*, and correctness of every piece is not the same as the feature being *on*. iOS and Windows have no equivalent step — `UserDefaults` and `%APPDATA%` are reachable from anywhere — which is exactly why the third platform's extra wire went unnoticed. `MainActivity.onCreate` now attaches, and `test_the_android_recorder_is_switched_on` fails if that line ever leaves.
>
> ## Scope
>
> These record only. Sending stays the console's job and happens only where a collector was compiled in, so native-shell failures do not reach the gateway aggregate. `native/README.md` says so rather than leaving it to be assumed.
>
> Also carries the previously-pushed gateway container deploy-path commit, which had no PR of its own: `cloudgw/Dockerfile`, the `0.2.0` contract version, and the boot banner that names what an operator has left unset.
>
> ## Checks
>
> - 1359 passed — full suite
> - 19 passed — the new guard, with the attach line removed by injection to confirm it fails
> - 51 passed — route and native path guards, since the recorder reads paths the resolver also reads
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #231 — A marketplace somebody can use, and a guard that stopped inventing work

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/231>

> Thirteen routes — the whole commercial surface, including all of the money path — existed in the backend with no caller. You could not search, place a listing in a town, put a price on one, or buy one, and a seller could not see what they had sold.
>
> **doorless: 218 → 205.** The entire `/marketplace/*` block is closed.
>
> ## The guard was aiming me at work that was already done
>
> I set out to build this door and TypeScript refused a duplicate binding: `api.marketplace()` already existed and Discover had been calling it since it was written. But `GET /marketplace` was on the doorless backlog.
>
> The cause is in `clientpaths.py`. A template literal may nest another inside an interpolation:
>
> ```ts
> `/marketplace${tag ? `?tag=${enc(tag)}` : ""}`
> ```
>
> The backtick alternative was `` [^`]* ``, which stops at the **inner** opening backtick. The captured literal became `` /marketplace${tag ? ``, the query cut landed on the literal `?` inside it, and the call normalised to a path no route matches.
>
> **This is a different failure from every earlier one in that file.** The truncating extractor, the verb read off a neighbouring call, the route table read flat instead of recursed — all made the guard too *lenient*, and those get found by the bug they let through. This one made it **invent work**, which fails more quietly: an invention is found only when somebody goes to do it and discovers it done.
>
> One route out of 218 here and none in jim-mini or pdi, so the guard was substantially right. The distinction is now written into the file, because the quiet direction is the one worth naming.
>
> Interpolations are matched by counting braces, and the optional-query marker recognises a backtick as well as a quote — the same idiom is usually written with a nested template.
>
> ## Every shape probed, not read
>
> Two would have been wrong from the route signatures alone:
>
> - the offer takes **`price`**, not `price_cents`
> - `settings/{id}` wants an **interactor** id, not a profile's
>
> The whole path was driven end to end against a running server:
>
> ```
> PUT  offer      -> seller_id is the caller; pricing is what establishes the seller
> POST purchase   -> 422 "this is your own listing — buying it would credit you
>                         with your own money and inflate your sales count"
> POST purchase   -> 201 ord_… paid, ledger led_… (as a second party)
> POST purchase   -> 422 "this costs 45.00 GBP; send accept_price=45.00 to confirm"
> GET  sales      -> the seller's statement, one order
> ```
>
> Those refusals turned out to be the best copy on the screen.
>
> ## Two sentences quoted, not paraphrased
>
> The backend states in its own reply that ranking is *"deterministic — title, tags, provider, blurb, in that order. No model reorders this."* and that the money is simulated. The screen renders both verbatim: a marketplace that quietly ranked by something else would be a different product, and money that looks real and is not is the worst thing here to be vague about.
>
> `marketAssist` is shown as suggestions for the search box only — the reply says `applied: false`, and the caption says so too.
>
> ## The surface guard earned itself
>
> The moment `Market.tsx` appeared, last round's guard failed the suite unprompted and would not pass until screen **152 Marketplace** was drawn, given a gallery row and a lesson, and made reachable by the words somebody actually types — "find a plumber", "for sale", "hire". That is the fourth docs catch-up round not happening.
>
> The screen builder also refused a card title that ran off the card, and the dock test refused the lesson until a phrasing reached it.
>
> ## Notes
>
> - No backend changes.
> - Console typechecks and builds; full suite running at time of writing.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #230 — Cut 0.19.1

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/230>

> 0.19.0 shipped its own error-reporting card and first-run notice **with no screen, no lesson and nothing for the in-app helper to point at** — while its release notes described the feature at length. The guard that now prevents that (qrme#229) and the two drawings it asked for landed on `main` after the tag, so they need a version to ship in.
>
> Companion PRs in jim-mini and pdi.
>
> ## The five strings
>
> | File | |
> |---|---|
> | `pyproject.toml` | what pip follows |
> | `qrme/api.py` | `FastAPI(version=…)`, what the release tag follows |
> | `app/package.json` | what the installer filenames and the auto-updater follow |
> | `app/package-lock.json` | **twice** — the lockfile header and the `""` entry under `"packages"` |
>
> `test_docs_gallery.py` asserts all five agree; it passes. Console builds with `0.19.1` in the bundle.
>
> ## What ships in it
>
> **No application behaviour changes.** Screens 150 and 151, their gallery rows, a lesson, helper phrasings — and the guard that fails when a surface ships with none of them.
>
> The guard is the substance. Every gallery test checks screens against the README and none asked whether a surface has a screen at all, so three features had already shipped undrawn and needed a dedicated catch-up round each. `ui_screens.txt` closes that direction: a surface nobody has classified fails in the round that introduces it, and silencing it by writing `undrawn` fails the ratchet.
>
> ## Notes
>
> - Suite green at time of writing; full run in flight.
> - Tag creation stays yours — links follow when this merges.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #229 — Fail when a surface ships with no drawing, then draw the two that did

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/229>

> Companion PRs [jim#176](https://github.com/davidsbianchi1984/jim-mini/pull/176) and [pdi#137](https://github.com/davidsbianchi1984/pdi/pull/137). Two commits: the guard, then the drawings it asks for.
>
> ## The guard
>
> `test_docs_gallery.py` checks screens against the README in both directions — a reference with no file, a file with no reference, a gap in the numbering, a filename a URL cannot carry. Every one of them starts from the screens. **None asks the opposite question: does this surface have a screen at all?**
>
> So a feature can ship with nothing drawn, nothing taught, and nothing for the helper to point at, and the suite stays green. That is not hypothetical — it has happened three times. Voice cloning, the recoverable watermark and the chat role picker each went two versions undrawn and needed a dedicated catch-up round (#100). Then the error-reporting card and its first-run notice shipped in 0.19.0 exactly the same way, while the release notes described the feature at length.
>
> It is the same shape of flaw this suite has found twice elsewhere: **a guard that only walks the relation in the direction where the answers already exist.** The doorless audit was a route with no client door. The redaction check read `doorless_routes.txt`, which shrinks as doors are built, and would have gone vacuous the day it emptied.
>
> `ui_screens.txt` is the missing direction. Every surface under `app/src/screens/` and every top-level surface component carries a screen number, `undrawn`, or `unaudited`.
>
> **Why the mapping is declared rather than inferred.** Matching component names against screen titles resolved only **ten of twenty-four**, because titles are written for the person using the app ("How Should They Work?") and component names for the person editing it ("Delegate"). Guessing the rest would have produced a mapping that looked complete and was not — the exact failure mode this round exists to close. `unaudited` is the honest seed for components that predate the file, and it is not a status a new component may use.
>
> **Both backlogs are ratcheted against a ceiling each repo declares for itself.** This test is byte-identical across three repositories with different backlogs, so one hardcoded number would be the largest of the three and leave the other two slack to grow into. A ceiling left high after the backlog falls fails too: a ratchet that stops ratcheting re-opens the ground it gained.
>
> Verified by injection, five ways — the second is the one that gives the first its teeth:
>
> ```
> unclassified surface                          -> fails
> silenced by writing `undrawn`                 -> fails (the ratchet)
> mapping points at a screen that doesn't exist -> fails
> typo'd status ("undrwan")                     -> fails
> component deleted, entry left behind          -> fails
> raising the ceiling deliberately              -> passes, and shows in the diff
> ```
>
> That last one is deliberate. Raising the ceiling is one line saying plainly that the backlog grew, which is a conversation worth having rather than one a test should win on its own.
>
> ## The drawings
>
> Screens **150 What Went Wrong** and **151 Before Anything Is Sent**, with gallery rows, a lesson, and `DIRECTIONS` phrasings for the words somebody actually types when something has broken — "it failed", "something broke", "stop sending", "opt out".
>
> The card draws an operation and a status and nothing else, because that is all the log holds. Drawing a message there would depict a product that does not exist.
>
> Both surfaces move off `undrawn`, and the ceiling drops to zero with them.
>
> ## Two existing guards earned their keep
>
> The screen builder **refused a card title that ran off the card** (`'Sent when the app opens' needs 187px, has 155px`), and the dock test **refused the lesson until a phrasing reached it** (`no phrasing reaches 'problems'`). Neither is new. They are the directions this repo was already checking — which is precisely what made the missing direction worth building rather than assuming.
>
> ## Notes
>
> - No backend behaviour changes: screens, gallery, lesson, helper phrasings and the new guard.
> - Suite green: **1340 passed**, up from 1334 — exactly the six new tests, nothing else moved.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #228 — Cut 0.19.0

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/228>

> 0.18.0 is already released, so the error-capture and send work merged in qrme#226 and qrme#227 had nowhere to ship. Cut with the siblings so the suite carries one version. Companion PRs [jim#175](https://github.com/davidsbianchi1984/jim-mini/pull/175) and [pdi#136](https://github.com/davidsbianchi1984/pdi/pull/136).
>
> ## The five strings
>
> They move together, as the releasing checklist says and as each of them has drifted at least once before — pyproject sat at 0.4.0 through the 0.4.1 cut, the lockfile roots at 0.3.3 through two:
>
> | File | |
> |---|---|
> | `pyproject.toml` | what pip follows |
> | `qrme/api.py` | `FastAPI(version=…)`, what the release tag follows |
> | `app/package.json` | what the installer filenames and the auto-updater follow |
> | `app/package-lock.json` | **twice** — npm writes the root version in the lockfile header *and* in the `""` entry under `"packages"` |
>
> `test_docs_gallery.py` asserts all five agree; it passes. Console builds with `0.19.0` in the bundle.
>
> ## What ships in it
>
> The console records every failed request and, where a build has a collector address, reports it once at launch — the operation and the status code, never the message and never the path as it was actually called. `cloudgw` gains `POST`/`GET /v1/problems` to receive them, refusing anything that is not exactly an error report rather than sanitizing it.
>
> Nothing sends before a first-run notice has been answered, and that notice renders the real payload rather than describing it.
>
> ## Two things found while cutting
>
> **`app-v0.16.0` and `app-v0.17.0` were never tagged.** Only `app-v0.15.0` and `app-v0.18.0` exist on the remote. Two versions were cut in the repo — strings bumped, changelog written, release notes staged — and then never released. The existing `[0.16.0]:` link reference points at a tag that does not exist, so it is already a dead link.
>
> This adds references for `[0.19.0]` (anticipating the tag, as the convention has always done) and `[0.18.0]` (that tag is real, and the reference was simply missing). `[0.17.0]` is deliberately left without one rather than writing a third link to nothing.
>
> **`cloudgw` stays at `0.1.0`.** It gained an endpoint pair this round and its version is what `/health` reports — but it is the gateway's own version rather than part of the product release train, and it has sat at 0.1.0 through every cut. Flagged rather than changed, since that is a convention question. Note the version-consistency test reads `qrme/api.py` specifically, so the sidecar's number cannot be confused for the product's.
>
> ## Notes
>
> - No functional changes in this commit — versions, changelog and release notes only.
> - Full suite running at time of writing; the five-string check and the console build are already green.
> - Tag creation stays yours — nothing here pushes `app-v0.19.0`.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #227 — Send the error reports, and refuse anything that is not one

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/227>

> The consoles have recorded content-free failures since qrme#226. This is the other half — they now **send** them, once at launch, alongside the update check, and `cloudgw` grows somewhere to send them to. Companion PRs [jim#174](https://github.com/davidsbianchi1984/jim-mini/pull/174) and [pdi#135](https://github.com/davidsbianchi1984/pdi/pull/135); `errors.ts`, `Problems.tsx`, `ProblemNotice.tsx` and the console test are byte-identical across the three repos.
>
> ## Nothing goes before the person has been asked
>
> Sending is opt-**out**, which only means something if the opting-out can happen *before* the first report rather than being discovered afterwards in a settings panel nobody opened. A switch nobody knows about is not a choice.
>
> So `sendProblems` refuses until a first-run notice has been answered. That notice **renders the actual payload** rather than describing it, from the same function that posts it — prose saying "we only send error codes" would be a claim you have to trust; showing the object means the notice cannot go stale while still reading honestly. Both answers are offered, and it appears only where a build has a collector at all, because interrupting somebody to explain a thing that cannot happen is how people learn these notices are noise.
>
> Driven end to end against a live gateway:
>
> ```
> first launch, notice unanswered   -> awaiting-notice   (nothing sent)
> person clicks "No thanks"         -> turned-off        (nothing sent, ever)
> fresh install, before answering   -> awaiting-notice
>               after "That's fine" -> sent
> ```
>
> The aggregate then held exactly one row — from the install that agreed. The one that declined contributed nothing.
>
> After that first answer it is opt-out as normal: automatic, with the same switch on the Settings card, changeable whenever.
>
> ## Off by absence, not by flag
>
> The collector address is compiled in at build time and unset by default:
>
> ```bash
> PROBLEM_COLLECTOR=https://gw.example.com PROBLEM_TOKEN=… npm run build
> ```
>
> Unset, and the installer has nowhere to send and no code path that could acquire one — a stronger default than a boolean, because there is no address for a later mistake to switch on. The send swallows every failure; a diagnostic that can delay a launch has stopped being worth having.
>
> Sent from the renderer rather than the Electron main process, because that is where the buffer lives — a diagnostic needing an IPC channel of its own has more ways to go wrong than the bugs it finds. It lands beside the update check anyway: `setupAutoUpdate()` runs the moment the window is created.
>
> ## Counts are deltas
>
> Each row remembers how much of itself has been reported, so reopening the app twenty times does not turn one broken screen into twenty. Nothing is deleted after a send — the row is the user's own history. A failed send moves the watermark not at all, and the next launch retries:
>
> ```
> send to a dead collector -> failed,  watermark sent=0 of 1
> retry once it is up      -> sent,    watermark sent=1 of 1
> ```
>
> ## The intake refuses rather than redacts
>
> `cloudgw/problems.py` accepts exactly five top-level keys and five per problem and **422s on anything else** — an unknown field, a `platform` string long enough to hide a sentence, a `day` carrying a time of day, a path with an unredacted id still in it:
>
> ```
> problems[0].op contains 'usr_8752921df161', which looks like an identifier
> rather than a route name. The console redacts these before storing them, so
> this build's redaction is not working. Refused rather than redacted here,
> because redacting here would hide that from the only people who can fix it.
> ```
>
> It could redact that path itself; the pattern is right there. Doing so would let a build whose redaction had broken keep working, with the only signal a server-side counter nobody reads. Refusing is also cheaper here than for contributions next door: a rejected error report costs one lost diagnostic, where a rejected contribution costs somebody their donated work.
>
> ## What survives is less than what arrives
>
> Reports are not stored as reports. They fold into counters keyed by product, version, platform, operation and status:
>
> ```
>   7  jim-mini  GET /users/{id}/captures -> 404
>   3  qrme      POST /profiles/{id}/chat -> 500
>   1  qrme      GET /users/{id}/captures/{id}/image -> 404
> ```
>
> Locale is validated and then **dropped** — every extra dimension narrows a row towards a single install, and platform plus version is what triage actually needs. Nothing records that a particular install sent anything, or when beyond the day. That is also why these counters sit in a plain file while contributions are sealed in PDI: contributions are people's own words; these have no owner to protect, and encrypting them would look careful and mean nothing.
>
> Reading the aggregate needs a narrower permission than writing to it (`CLOUDGW_PROBLEM_READERS`, unset = the local developer only). The posting token ships inside every installer and is public the moment somebody unzips one; a wrong write costs a wrong counter, while reading is a live map of what fails on every build.
>
> ## Four bugs found by checking rather than reasoning
>
> **A gap in the guard itself.** Injecting a `detail` field into the outgoing report was caught — but only by the test comparing the wire shape against the gateway, which runs only in *this* repo. In JIM and PDI, where a leak would cost the most, it would have passed. The five field names are now pinned locally too.
>
> **Every validator was wrong about its own rule.** All the intake's patterns were anchored with `$`, which in Python matches before a trailing newline as well as at end of string — so `Win32\n` and `GET /health\n` were accepted by a validator whose own error message said newlines were not allowed. All now end `\Z`, with a test, because the next person will reach for `$` too.
>
> **No CORS at all** — the one that would have made the rest pointless. The sender posts JSON with an `authorization` header, making it a non-simple request: the browser preflights with `OPTIONS` and refuses the real call unless that is answered. Every preflight would have 405'd, every report would have failed, and because the sender swallows failures the feature would have been dead in the field with nothing to show for it. Found by asking what an Electron renderer's origin actually *is*: `null`, since it loads from `file://` — which is also why no origin allowlist could have been written. Verified by deleting the middleware and watching the preflight test fail.
>
> **A 500 on the read, found by being careless rather than clever.** While driving the client, a scratch file of unrelated JSON got reused as the counter path. The aggregate loaded it — it parsed, after all — and `GET /v1/problems` then died sorting values that had no `count`. Unparseable JSON had been handled from the start; *parseable* JSON of the wrong shape had not, and that is the likelier accident: a half-written file that closes its braces, an older format, a path pointed at something already there. Rows are validated individually on load now, so a bad one is dropped and good ones beside it survive. A test written from imagination would have reached for `"{ this is not json"` again and stayed green.
>
> ## Tests
>
> Twenty-nine on the intake, nineteen on the console module. The notice gate was verified by injection twice — once by removing it, once by moving it to *after* the fetch, which would have looked like a check while being none. Beyond that: counts add across reports, the worst thing sorts first, counters survive a restart, a partly-corrupt counter file keeps its valid rows, the posting token cannot read, and an unconfigured reader list means nobody but the developer.
>
> ## Notes
>
> - No product-backend changes. No new routes on the QRME app, so the doorless backlog is unaffected.
> - All three consoles typecheck and build. Suites: PDI 299 passed / 1 skipped, JIM 745 / 1.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #226 — Record what fails, without recording anything private

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/226>

> Error collection across all three consoles, built so it cannot carry user data. Companion PRs in jim-mini and pdi; `errors.ts`, `Problems.tsx` and the test are byte-identical across the three repos.
>
> ## The obvious version would have broken the promise
>
> Every failed request already passes through one function, so catching them is ~30 lines. The hard part is what a failure may say about itself. These backends put user input straight into their error messages:
>
> ```
> no device called 'Pixel Buds' on this account
> unknown site 'knee'; one of scalp, face, eye, mouth…
> unknown language 'xx'
> ```
>
> Good messages for the person reading them, bad things to keep. In JIM they can be health content. So the message is shown to the user, who owns it, and **is never written to the log**. Same reasoning for the path: `/profiles/prf_0de08e794ed0/chat` identifies a person; `POST /profiles/{id}/chat` identifies a bug.
>
> | Recorded | Never recorded |
> |---|---|
> | operation (`POST /profiles/{id}/chat`) | the error message |
> | status (0 = never reached a server) | ids, tokens, key prefixes |
> | count, date (day only) | request or response bodies |
> | app version, platform, language | timestamps finer than a day |
>
> Redaction happens **on the way in**, so there is no moment at which the buffer holds something that would have to be scrubbed later.
>
> ## Nothing transmits
>
> Local, capped at 50, with a Settings card showing the exact payload — the same object the copy button produces, from one function, so the preview cannot drift from what is copied. The backend ships inside the installer, so for a desktop user there is no server on the other end; a copy and a paste is the honest path, not a limitation to apologise for.
>
> ## Two mistakes caught by testing, not by reasoning
>
> **The redaction under-redacted.** Requiring six hex characters let `cap_9f2`, `req_77aa` and `usr_1` through — three of the first eight real paths. Widened, then validated against **239 real route segments** across the three products to confirm it does not eat route names in the other direction.
>
> **The test checking that had the same shape of flaw.** It read segments from `doorless_routes.txt`, which shrinks every time a door is built — so it would have weakened as the backlog cleared and gone **vacuous the day it emptied**. A test that gets less thorough as the project improves is worse than no test, because nothing announces the moment it stopped meaning anything. It now reads the live route table. Discovering that app by name then picked QRME's `cloudgw` sidecar (10 segments instead of 400); only the floor caught it, so the choice became "the package with the most routes".
>
> ## Twelve tests hold the shape
>
> - `recordProblem` has no parameter a message could arrive through
> - the stored record has no field one could sit in
> - the report's keys are pinned
> - `api.ts` never hands the recorder anything but a status
> - short ids are redacted as well as long ones
> - no real route name is eaten
>
> **Verified by injection**, not assertion: a `detail` parameter added to the recorder, and the redaction narrowed back to six-hex ids. Both caught.
>
> ## Notes
>
> - No backend changes. No new routes, so the doorless backlog is unaffected.
> - All three consoles typecheck and build; suites green (PDI 293 at time of writing).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #225 — A desk you can actually staff

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/225>

> The desk is the one surface in QRME whose promise is a **person** — a real tradesperson, attested by somebody, reachable now. None of it was reachable from a client: you could not open a desk, say whether anybody was behind it, answer the bell, or let a visitor come up.
>
> The new **Desk** screen covers the counter end to end — opening one with the attestation it rests on, presence, rings, guests, the stream overlay, and beacons.
>
> ## Four things stated the backend's way, not the console's guess
>
> **A desk is not a profile.** The API answers `desk_id` and `desk_token`, so the token lives in the screen rather than the shared session — signing in as an owner does not make you the counter, and conflating them would let one person's session speak for a desk they do not staff.
>
> **Away and closed are different promises.** One says come back, the other says the counter is shut. The desk gets to make either, so both are buttons.
>
> **The attestation is shown to its own keeper**, `burned` included. A withdrawn claim is not something to find out about from a visitor.
>
> **Picking up a beacon retires it** — the sticker on the wall stops working. That is the point of picking it up, so the button says so.
>
> ## Probing caught what habit would have got wrong
>
> The desk answers `desk_id` and `desk_token`, **not** `id` and `owner_token`. My first probe used the familiar names and every follow-up call 404'd. Had I written the bindings from habit instead of from a live response, sixteen calls would have compiled, shipped, and failed against a real desk.
>
> ## `view.webp` and the beacon QR are excluded, not doored
>
> Both render in an `<img src>` rather than being fetched by the API client — the same category as the pair and medical-ID codes already in `NOT_A_CLIENT_CALL`. Counting them as doorless would have meant building a door that cannot exist.
>
> ## Coverage
>
> **Eighteen routes off the doorless list, 236 → 218** (16 real doors + the 2 image exclusions).
>
> ## Notes
>
> - `clientpaths.py` stays byte-identical across the three repos; companion commits land the same exclusion in jim-mini and pdi, and both repos' guards were re-run to confirm nothing shifted.
> - Console typechecks and builds; full suite running at time of writing.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #224 — A profile that can act for you, and a way to say how far

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/224>

> QRME's first pass at the doorless backlog — the largest of the three at 252.
>
> The whole authorisation chain existed in the backend with **no caller anywhere**: mint a revocable grant, authorise which phases may run unattended, start a workflow, advance it, answer it when it stops, cancel it. Shipping the acting half without the governing half is the wrong half to ship, and it is the half that shipped.
>
> ## The screen is ordered the way the decision is
>
> 1. **Grants first** — a phase reads the profile's own material *through* one, and it can be withdrawn mid-run. The work stops seeing what the grant covered from that moment, not at the end.
> 2. **The policy second** — it is a choice about scope, not about work.
> 3. **The runs last** — they are what the first two make possible.
>
> ## Three things are the server's judgement rendered, not the console's invention
>
> **The delegable phases come from the server.** `GET /profiles/{id}/delegation` returns them; the client does not retype the list.
>
> **`research` cannot be delegated without a grant.** The backend refuses it outright:
>
> > delegating `research` requires a grant: without one the phase reads every source item on the profile
>
> So the console sends the grant it holds, and lets that refusal reach anyone who has not minted one **with its message intact** — rather than pre-empting it with a guess that would drift from the real rule.
>
> **A stopped run shows what it is waiting for.** `awaiting` is the entire point of the pause: the profile stopped because it needs a person, and it says what for. Answering resumes it in place.
>
> ## Coverage
>
> | Family | Routes |
> |---|---|
> | grants (mint, revoke) | 2 |
> | delegation (get, set) | 2 |
> | workflows (create, list, get, advance, resume, cancel) | 6 |
> | delegated workflows (start, get, advance, resume) | 4 |
> | tasks (run, list) | 2 |
>
> **Sixteen routes off the doorless list, 252 → 236.** Bindings and screen landed together, per the rule in `clientpaths.doorless()`.
>
> ## Notes
>
> - Console typechecks and builds clean; full suite running at time of writing.
> - Every response shape was read off a live response rather than inferred from the handler.
> - Delegated workflows are kept separate from the owner's own on purpose: those are the runs somebody *other* than the owner started, under the policy the owner set.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #223 — Menus that keep their promises, and the routes with no door at all

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/223>

> **This PR now carries two rounds.** The second was pushed onto the same branch while the first was still in CI, so they merge together.
>
> ---
>
> # 1. Every option the backend offers, it now has to accept
>
> A catalog endpoint is a menu. The console and the three shells render it directly, so whatever it lists is what a user can pick. If the endpoint that *consumes* the choice refuses one of those values, the user meets an error for doing exactly what they were offered.
>
> Eight checks now send the request rather than read source: languages in both delivery modes, the same languages as translation targets, the steering dials the server describes, the providers on the model menu, the robots, the connectors, the pack registries. **All accepted — no field bug.** Verified by making `/languages` offer Arabic while the writer refused it, and watching both language tests fail.
>
> Two judgement calls, stated in the tests: a **409 is not counted as a refusal** (the server understood the value and objected to *state*), and an **empty catalog fails rather than passes**.
>
> One approach was tried and deliberately not shipped: matching client literals to backend vocabularies by field name. `role="dialog"` is ARIA, `target="_blank"` is an anchor, `platform="xbox"` is a gaming platform, and `kind` means five different things in five modules. Nearly every hit was false, and a guard that cries wolf is worse than none.
>
> ---
>
> # 2. Which routes have no door?
>
> The inverse question. The guards ask whether every call reaches a route; this asks whether every route is reachable from a door a user can open — the quieter failure by far. A call to a missing route 404s and gets reported. **A route nobody calls produces nothing at all.**
>
> ## 252 of QRME's 409 routes are in that position
>
> Spot-checked, not assumed: the console reads `/profiles/{id}/friends` and renders the list, while `DELETE /profiles/{id}/friends/{fid}` is called by nothing. **You can gain a friend and never remove one.** `/displays`, `/comments`, `/agent/lights` and 250 others are in the same position.
>
> Recorded in `tests/doorless_routes.txt` as a ratchet: it **cannot grow** (a new doorless route fails), and it **must shrink deliberately** (building a door also fails, asking for the line to be struck).
>
> ## A correction, and the test that forced it
>
> The first version of this audit reported **zero** and passed. That was wrong in the most dangerous way — vacuously. `app.routes` is not the flat list it appears to be: FastAPI wraps each `include_router` in an `_IncludedRouter` carrying no `path` or `methods` of its own, so walking the top level saw **8 routes out of 409**. `all_routes()` now recurses.
>
> Route *matching* was never affected — the wrapper implements `matches` and delegates — so the guards from #221 and #222 stand. Only enumeration was broken.
>
> `test_the_audit_is_actually_looking_at_something` caught it, by asserting the route table is not implausibly small. **It was written in the same round it went on to falsify**, which is the argument for writing them.
>
> ## Not started: building the doors
>
> 426 route+method pairs across the three products is many rounds of work, and which families come first is a product decision rather than a mechanical one.
>
> ## Notes
>
> - Local suite (round 104): **1284 passed**. Round 105's is running.
> - `tests/clientpaths.py` stays byte-identical with jim-mini's and pdi's copies.
> - Tests and docs only — no runtime behaviour changes.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #222 — Check the verb, not just the address

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/222>

> The route guard added in #221 accepted a **partial** router match — path right, method ignored. That passes a client sending `POST` where only `GET` is mounted, which answers **405**; from the user's side that is the same dead button as the 404 the guard exists to prevent. It now requires a full match.
>
> ## Reading the verb means reading four dialects
>
> None of it is guessable, so `CallForm` records where each language keeps it:
>
> | Surface | How the verb is written |
> |---|---|
> | console (TS) | labelled — `{ method: "POST" }` |
> | iOS (Swift) | labelled — `method: "PUT"` |
> | Android (Kotlin) | positional, right after the path |
> | Windows (C#) | the helper's own name — `Post(...)`, or `HttpMethod.Get` |
>
> ## Scoping to the enclosing call corrected the boundary both ways
>
> My first attempt scanned forward from a path literal and reported three "mismatches" that were all artefacts — a neighbouring call's `method:` leaked in whenever that neighbour wrote its path in double quotes. Parsing the call with balanced parens removed the guesswork and exposed two real facts:
>
> - **Double-quoted paths were skipped entirely.** In #221 I wrote a comment justifying that as safe. It happened to be true, but I had asserted it rather than checked it, and it left roughly a third of the console's call sites outside a guard that claimed to cover the console. **42 paths became 74 verb-and-path pairs.**
> - **`"/app"` stopped counting as a request.** It appears in `defaultBase()`, asking whether `window.location.pathname` starts with it — a question about where the page is served, not a call. Only something that knows what encloses a literal can tell those apart.
>
> ## Coverage
>
> | Surface | pairs checked | refused |
> |---|---|---|
> | console | 74 | 0 |
> | iOS | 89 | 0 |
> | Android | 87 | 0 |
> | Windows | 90 | 0 |
>
> **No field bug came out of this** — all 340 pairs are accepted. Saying so plainly: the value here is the guard, not a catch.
>
> ## Verified by injection, not assertion
>
> - console `POST` → `PUT` on `/interactors` → `PUT /interactors … accepted here: POST`
> - iOS call stripped of its `method:` label so it fell back to GET → `[ios] GET /profiles … accepted here: POST`
>
> Both restored to a zero diff afterward.
>
> ## A new class of guard
>
> Each language's verb reader gets its own liveness test. They are separate code and they fail quietly: if one stops matching, every call from that surface silently becomes a GET — and since most routes *do* serve a GET, the suite would stay green while checking almost nothing. A surface reaching dozens of routes and reporting a single verb is now an assertion failure.
>
> ## Notes
>
> - `tests/clientpaths.py` stays byte-identical with jim-mini's and pdi's copies (`acf4c50…`).
> - `native/README.md` updated where it described the check as path-only, keeping both stated limits: routing-level matching cannot see refusals that happen *after* dispatch, and a path assembled at runtime is invisible to any static scan.
> - Tests and docs only — no runtime behaviour changes, so nothing here needs a version cut of its own.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #221 — Guard every client path against the route table, in four languages

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/221>

> 0.17.0 fixed a 404 under every like, comment and share on the community wall, and added a test so it could not come back. **The test had a hole, and six client surfaces had no test at all.**
>
> ## The hole in the guard
>
> `test_console_routes_exist.py` cut each path at its first interpolation whenever a query followed. That is correct for `?tag=${tag}` — the path ends before the `?` anyway — and wrong for this:
>
> ```ts
> `/profiles/${profileId}/media?filename=${encodeURIComponent(file.name)}`
> ```
>
> which was being checked as bare **`/profiles`**.
>
> A prefix that *resolves* is worse than one that does not. The check passes, reports success, and the tail it exists to verify is never looked at. Two of QRME's console paths were being skipped this way — the adult feed and the **media upload added in 0.16.0**.
>
> The fix is an ordering change: fill interpolations in *before* cutting the query, with the optional-parameter idiom (`${adult ? "?adult=true" : ""}`) recognised as the one interpolation that really *is* a query, marked by a quoted `?` inside its braces.
>
> ## The gap: three shells, no guard
>
> `native.yml` proves the shells compile. A path is a string in all three languages, so this compiles perfectly, ships, and 404s in the field:
>
> ```swift
> "/post/\(id)/like"      // the Wall bug, verbatim
> ```
>
> Around **220 path literals** across iOS, Android and Windows had never once been compared with the route table.
>
> | Surface | Paths | Interpolation | Previously checked |
> |---|---|---|---|
> | console | 42 | `${x}` | partially — 2 were being skipped |
> | iOS | 74 | `\(x)` | ❌ |
> | Android | 72 | `$x` / `${x}` | ❌ |
> | Windows | 74 | `{x}` | ❌ |
>
> The singular of every `_KIND_BY_PATH` value is now banned in the native sources too, so a fix made on the web cannot be quietly undone on a phone. `test_the_shells_and_the_console_agree_on_the_wall` states that directly: 0.17.0's fix was five lines in one TypeScript file, and nothing stopped the same five paths being written the old way in Swift, Kotlin or C#.
>
> ## Two tests guard the guard
>
> **`test_each_shell_is_actually_being_scanned`** — fails if a language's pattern stops matching. A scan that silently finds nothing reads exactly like a scan that finds nothing wrong, and it would turn this whole file into a test that always passes.
>
> **`test_an_interpolated_query_does_not_truncate_the_path`** — pins the truncation bug against the two live paths that were being skipped, asserting they now reach the guard *and* resolve.
>
> ## Shared extraction
>
> `tests/clientpaths.py` holds the language table and the normaliser, used by both guards and **byte-identical in all three repos** (md5 `38e1a310…`). The repo root is located by walking up to `pyproject.toml` rather than counted in `.parent`s — this file sits at `tests/` here and `{pkg}/tests/` in the siblings, and that was the only thing that would otherwise differ.
>
> ## Result
>
> **No new field bug came out of this.** Every path all four surfaces build resolves. I'd rather say that plainly than dress up a clean audit — the value here is the guard, not a catch.
>
> Each check was verified by injecting the bug it claims to catch:
>
> | Injected | Into | Result |
> |---|---|---|
> | `"/post/\(postId)/like"` | iOS | both Wall guards fired, naming the platform |
> | `"/modles"` | Windows | `[windows] /modles (native/windows/ApiClient.cs, from '/modles')` |
>
> Every tree was restored to zero diff afterward.
>
> ## Also
>
> `native/README.md` gains a **"Do the paths resolve?"** section beside its existing "Do they compile?" claim, and states both limits rather than overselling: routing-level matching cannot see a refusal that happens *after* dispatch — which is exactly why the singular segments are banned by name — and a path assembled from pieces at runtime is invisible to any static scan.
>
> ## Tests
>
> Local suite running at time of push; the four route-guard files pass (`9 passed`) and CI runs the identical `test` job. Test count goes 1269 → 1274.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #220 — Cut 0.18.0

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/220>

> 0.18.0 across all five version strings — `pyproject.toml`, `qrme/api.py`'s `FastAPI(version=)`, `app/package.json`, and the two *root* entries of `app/package-lock.json`. Plus the changelog heading over the accumulated `[Unreleased]` content, the README history row and current-release line, and a fresh `RELEASE_NOTES.md`.
>
> The lockfile split is root-only by construction, and it earned that this time: `node_modules/react-refresh` is genuinely at version `0.17.0`, and it was correctly left alone.
>
> ## What it carries
>
> **Native parity, completed.** Provenance lookup ("Who wrote this?") and the advisor/collaborator/operator role picker reach iOS, Android and Windows. Every feature with a door in the web console now has one in the native shells — a thing two earlier rounds each named in their scope and neither finished.
>
> **The drawings caught up.** Voice cloning, the recoverable watermark and the role had all shipped with no screen, no lesson and no way for the in-app helper to point at them, for two whole versions. Screens **147 Your Own Voice**, **148 Who Wrote This?** and **149 How Should They Work?** join the gallery, each with a lesson in its proper chapter and a phrase the helper answers to.
>
> **Fixed** — `SmallAction` on Android took no `enabled` parameter, so a busy or empty action looked live and merely ignored taps.
>
> ## Verification
>
> - 1269 tests passed on this content before the cut; console builds clean (`✓ built in 1.34s`).
> - All five version strings verified per repo, and no stale root `0.17.0` anywhere.
> - Scripture confirmed still the README's closing section and deliberately not itemized as a changelog item.
>
> Cut together with [jim#167](https://github.com/davidsbianchi1984/jim-mini/pull/167) and [pdi#127](https://github.com/davidsbianchi1984/pdi/pull/127) so the suite carries one version.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #219 — Draw, teach and make findable what 0.16.0 and 0.17.0 shipped

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/219>

> Voice cloning, the recoverable watermark and the role picker each had code, a console door and (as of #218) a native door — and **no screen, no lesson, and no way for the in-app helper to point at them.** The convention here has been screen SVG + gallery row + lesson + help destination per feature; it had quietly stopped being followed for two whole versions.
>
> | # | Screen | Lesson chapter | Ask the helper |
> |---|---|---|---|
> | 147 | Your Own Voice | You are in control | "clone my voice", "sound like me" |
> | 148 | Who Wrote This? | You are in control | "who wrote this", "was this ai" |
> | 149 | How Should They Work? | Working | "just do it", "give me advice" |
>
> The help destinations are read by both the assistant *and* the dock's routing table from the same place, so one addition covers both surfaces.
>
> ## Two of this repo's own guards earned their keep
>
> **The screen builder refuses text that would overflow its box.** It caught eight strings before anything rendered — `'This is my own voice' needs 151px, has 119px` and so on. I shortened each rather than widening a card, because the guard is right about the layout.
>
> **The tutorial test requires lessons stay grouped by chapter in `CHAPTERS` order.** Appending the three at the end broke it (`At index 8 diff: 'Out in the world' != 'You are in control'`), so each lesson went into its chapter's own block instead. That constraint exists so the walkthrough never introduces a thing before the thing it depends on.
>
> I'd have shipped both defects without them.
>
> ## Verification
>
> - `test_docs_gallery`, `test_dock`, `test_tutorial`, `test_help`, `test_readme_scripture`: **71 passed.** The gallery test is a three-way check — every SVG referenced exists, every SVG is referenced, and the numeric sequence is unbroken.
> - Screen builder is deterministic: re-running before my change regenerated all 292 existing screens byte-identical, so the diff here is only the new work.
> - Helper routing verified live: `'clone my voice' -> [147]`, `'who wrote this' -> [148]`, `'just do it' -> [149]`.
> - Full suite running; CI is the gate.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #218 — The last two console-only features reach the native shells

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/218>

> Voice enrollment went native in 0.17.0; the other two features that had gained console doors did not. So iOS, Android and Windows could neither ask *who wrote this* nor choose how the profile should work a turn.
>
> | Feature | Route | Where it landed |
> |---|---|---|
> | **Who wrote this?** | `POST /watermarks/recover` | iOS `SettingsView`, Android Settings, Windows `SettingsPage` |
> | **Role picker** (spec clauses 2/12) | `role` on `POST /profiles/{id}/chat` | the chat composer on all three |
>
> Each client also gains the `RoleContext` / `WatermarkRecovery` wire models, and `chat()` takes an optional `role`.
>
> ## Two deliberate details
>
> **Recovery never answers with a bare yes.** The card shows matched passages out of stored, plus the similarity, and below the 0.25 threshold it names **nobody** — it reports the closest overlap and the threshold instead. Ordinary phrases travel between unrelated texts, and a coincidence must not read as an accusation. The failure branch shows the backend's own `reason` rather than a flat "no".
>
> **The role picker defaults to inference, and says so.** "Read my prompt" is index 0 / the empty value, which is what the backend does on its own. The reply then reports which role applied **and whether it was declared or inferred**, so an inference is never presented back as an instruction.
>
> ## Parity, finally
>
> With this, every feature with a door in the web console has one in the native shells:
>
> | | Voice | Watermark recovery | Role picker |
> |---|---|---|---|
> | iOS / Android / Windows | ✅ | ✅ | ✅ |
>
> That parity was named in the scope of two earlier native rounds and finished by neither. I verified it by grep this time rather than asserting it.
>
> ## Verification
>
> - Console builds clean (`✓ built in 1.55s`) — untouched here, checked for regressions.
> - No Swift/Kotlin/.NET toolchain in this environment, so **the iOS / Android / Windows jobs on this PR are the real check.** XAML well-formedness verified locally.
> - Caught by review before pushing: `WatermarkRecovery` needed an explicit import in Kotlin (a `mutableStateOf<T?>` type reference, unlike `WatermarkDesign` which is only ever inferred); `System.Linq` and `Microsoft.UI.Xaml.Media` were missing in the two Windows code-behinds; and one of my own edits silently no-oped against a non-existent anchor, which I only found by grepping for the result instead of trusting the script's "ok".
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #217 — Cut 0.17.0, and fix a 404 under every like, comment and share

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/217>

> ## The bug
>
> **Every like, comment and share on the community wall returned 404, and always had.**
>
> The audience routes dispatch on a leading `{kind}` and map the *plural* path segment to a singular kind (`posts` → `post`). `app/src/api.ts` was asking for the singular, so `/post/{id}/like`, `/post/{id}/comments` and `/post/{id}/share` reached the generic route and were then refused by the kind lookup. Liking a post, unliking it, reading its comments, writing one, sharing it — none of it worked in any release that shipped the buttons.
>
> Proven, not inferred:
>
> ```
> POST /post/pst_…/like       -> 404      POST /posts/pst_…/like       -> 201
> GET  /post/pst_…/comments   -> 404      GET  /posts/pst_…/comments   -> 200
> POST /post/pst_…/share      -> 404      POST /posts/pst_…/share      -> 201
> ```
>
> ## Why nothing caught it, and what now does
>
> Neither half was wrong on its own — the backend tests exercised the plural and passed, and the console compiled because a template literal is only a string. So the fix ships with `tests/test_console_routes_exist.py`, which checks the two halves *against each other*:
>
> - every path `api.ts` builds must resolve against the app's real route table;
> - no singular form of any mapped segment may appear in `api.ts` (covers all nine `{kind}` routes — like, comments, share, subscribe, subscribers, audience, gift, gifts — not just the three that were broken);
> - the singular's 404 and the plural's 200 are both observed against a live request, so the rule is not merely a spelling convention.
>
> One limit is recorded in the test rather than left to be rediscovered: **a route-table comparison would not have caught this.** `/post/x/like` matches `/{kind}/{target_id}/like` perfectly well at the routing layer, because the refusal happens after dispatch. I verified the new test fails on the old code before keeping it.
>
> ## The cut
>
> 0.17.0 across all five version strings — `pyproject.toml`, `qrme/api.py`'s `FastAPI(version=)`, `app/package.json`, and the two *root* entries of `app/package-lock.json` (root only; no dependency at the same version was touched). Plus the changelog heading over the accumulated `[Unreleased]` content, the README history row and current-release line, and a fresh `RELEASE_NOTES.md`.
>
> It carries: voice enrollment on the three native shells, the three features that gained console doors, the recoverable watermark, the Windows nav-label fix, and the Wall fix above.
>
> Also restores `The choice sticks.` to the 0.14.3 entry — a sentence describing real behaviour (the minimize state persists) that was removed while clearing the Matthew 7 paragraph out of the release notes, though it was never part of that passage.
>
> ## Verification
>
> - `test_readme_scripture`, `test_console_routes_exist`: 5 passed. Full suite ran clean before the changelog edit; CI is the gate.
> - Console builds clean.
> - Scripture confirmed still the README's closing section, and deliberately not itemized as a changelog item.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #216 — Voice enrollment reaches the device that has the microphone

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/216>

> The Voice screen shipped in the web console — which is the one surface where the owner cannot actually record anything, so it asks them to *type* how many seconds of speech they gathered. iOS, Android and Windows each gain a **Voice** screen walking the same FIG. 800 order (permission → collection → the characteristics → the print), but recording the sample and measuring it.
>
> ## What changed
>
> | Shell | Screen | Recorder |
> |---|---|---|
> | iOS | `native/ios/Sources/Views/VoiceView.swift`, reached from a new **Voice** segment in Manage | `AVAudioRecorder` + `NSMicrophoneUsageDescription` |
> | Android | `native/android/…/ui/VoiceScreen.kt`, new **Voice** tab in `ManageScreen` | `MediaRecorder` + `RECORD_AUDIO` |
> | Windows | `native/windows/Views/VoicePage.xaml`, new sidebar item | `MediaCapture` + system privacy setting |
>
> Each shell also gains the six voiceprint bindings in its API client (`voiceprint`, `grantVoiceConsent`, `addVoiceSample`, `buildVoiceprint`, `speakInVoice`, `revokeVoiceprint`) and the matching wire models.
>
> ## The privacy property is structural, not a promise
>
> The recording is written to the app's own container — `temporaryDirectory` on iOS, `cacheDir` on Android, `LocalApplicationData\QrmeStudio\voice` on Windows — and only the *measurement* crosses the wire, with `reference` naming the file. That is what the backend's `reference` field is for. No audio is uploaded, so no voice corpus can accumulate server-side; it is a consequence of where the bytes are written rather than a policy about them.
>
> ## Turn counting says which method it used
>
> iOS and Android read the platform's level meter (`averagePower(forChannel:)`, `maxAmplitude`) and count rising edges out of silence, so a turn is a stretch of speech. Windows does not meter its input, so it reports **one turn per recording** rather than deriving a count from the duration. A coarse number the app can stand behind beats a plausible one it cannot — the same reason `analyze()` reports counts instead of a quality score.
>
> ## Fixed
>
> The Windows navigation pane displayed the literal strings `tab.desk` and `tab.signatures`. Chrome localization falls back to the key when a key is missing, and those two were never added when the screens were. All three (with `tab.voice`) are now in `L10n.cs` in every supported language.
>
> ## Verification
>
> - Web console builds clean (`✓ built in 1.66s`).
> - `test_readme_scripture`, `test_docs_gallery`, `test_voiceprint`, `test_watermark_recovery`: 24 passed locally; full suite plus CI is the gate.
> - No Swift/Kotlin/.NET toolchain exists in the authoring environment, so these three files were reviewed rather than built locally — but `native.yml` compiles all three on their own runners, so the **iOS / Android / Windows jobs on this PR are the real check**.
> - Three problems were caught by review before pushing: `ApplicationData.Current` throws in an unpackaged WinUI app (switched to the same `LocalApplicationData` root `AppState` already uses), `MediaRecorder(null)` does not satisfy the API-31 constructor's non-null `Context`, and a `.map` chained off an optional inside an optional-chained Swift expression was replaced with explicit steps.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #215 — Three features come out from behind the API

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/215>

> An audit round for what had been skipped, and it found the failure this project keeps relearning: **a door nobody can open reads in the field as the feature not existing.** Voice cloning, the recoverable watermark and the advisor/collaborator/operator role all shipped as routes with no way to reach them from the app.
>
> ## Voice tab
>
> Walks FIG. 800's order rather than offering one "clone me" button, because the permission is the first box in the drawing for a reason:
>
> 1. **Permission** — with the own-voice attestation stated as what it is, and Withdraw on the same card.
> 2. **Enrollment** — add samples by source, and the readiness numbers are shown (`3 samples · 45s`, "still wants 75s more"), so a thin enrollment *looks* thin instead of hiding behind a progress bar.
> 3. **The voice** — mint the print only when it is earned, then speak, with the basis and the spoken disclosure printed under the result.
>
> ## Role picker on the composer
>
> Advisor / collaborator / operator, with **"Let it read my prompt"** as the default — which is the honest default, since that is exactly what the backend does when no role is sent. The reply's note now reports which role applied and whether it was `declared` or `inferred`.
>
> ## "Who wrote this?" in Control
>
> Paste any text; it names the profile that produced it, from the text alone, and reports `N of M passages match`, the similarity, and whether the writing is verbatim or has been altered since. When nothing matches it says so with the reason, rather than shrugging.
>
> ## Notes
>
> - No backend changes. `ChatReply` gains `role_context` and the chat request gains `role` in the typed client; everything else is new screens and bindings.
> - Console and launcher builds green.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #214 — The closing passage is not a release note

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/214>

> Founder's direction: the Matthew 7:24–25 passage **stays at the end of every README** — that standing rule is unchanged and still test-enforced — but it does not belong in the list of what an update contains. It's how the documentation closes, not a feature that shipped.
>
> ## What changed
>
> - Removed the 0.14.3 changelog paragraph that announced it.
> - Removed it from the 0.14.3 README release-history row.
>
> ## What did not change
>
> - The passage itself, byte-identical at the very end of every README.
> - `tests/test_readme_scripture.py`, which enforces that every `README*.md` closes with the root's block — still passing, so a newly added README still can't forget it.
>
> Docs-binding tests green: 13 passed. The same change is in jim-mini and pdi.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #213 — The watermark learns to survive being edited

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/213>

> Built from the field drawing: message *m* + sequence *S^N* + security key *K^D* → watermark *W* → embed → **Attack** → extract *W'* → reconstruct *m'*.
>
> ## The gap
>
> `POST /watermarks/verify` could only confirm that a piece of content matched a credential id **you already held**. One changed character made it fail, and it never said who wrote the text. The drawing asks for the other direction — recover the mark *from the content*, after the content has been attacked.
>
> ## What's new
>
> `POST /watermarks/recover` takes text with **no credential id** and answers *whose work is this?* — and keeps answering after the text has been rewritten.
>
> Every stamped text now also deposits an inverted index of **keyed five-word windows**: the normalized text cut into overlapping windows, each HMAC-SHA256'd with the deployment's watermark key (`QRME_WATERMARK_KEY`). Recovery hashes a candidate the same way and asks which stamp shares the most windows, scoring by overlap.
>
> The reply states its evidence instead of asserting a verdict:
>
> ```
> {"recovered": true, "profile_id": "prf_…", "verbatim": false,
>  "similarity": 0.62, "matched_windows": 31, "stored_windows": 44,
>  "examined_windows": 47, "state": "altered but traceable", …}
> ```
>
> It's arithmetic, not a learned detector, so the score can be checked by hand.
>
> ## Three deliberate restraints
>
> - **A coincidence is not an accusation.** Below a 0.25 similarity it names nobody — ordinary phrases travel between unrelated texts. A test feeds it a shared sentence about afternoon light and confirms it refuses.
> - **The key is what makes it a watermark rather than a fingerprint.** Without it nobody can compute matching windows, so a credential can't be forged or transplanted onto text QRME never wrote. A test swaps `QRME_WATERMARK_KEY` and watches recovery go silent.
> - **A provenance store must not become a corpus.** The stored rows are keyed hashes, so the index can't be read back as the writing it came from. A test asserts none of the passage's own words appear in the table.
>
> ## Notes
>
> - New table `watermark_shingles` with an index on `shingle` — a real inverted-index lookup rather than a scan over every stamp, and a new table (not new columns) so existing databases pick it up through `CREATE TABLE IF NOT EXISTS` with no migration.
> - `QRME_WATERMARK_KEY` unset derives a stable key from the database path so a local install still recovers its own marks. The docstring says plainly that this is a working default, not a secret.
> - Route registered before the `/watermarks/{watermark_id}` catch-all; `tests/test_routing.py` passes.
>
> ## Tests
>
> `tests/test_watermark_recovery.py` (8): verbatim recovery at similarity 1.0; an edited passage still traceable and honestly marked as altered; unrelated text recovers nobody; a shared phrase refused below threshold; the key swap silencing recovery; two profiles told apart; the route answering with no id; and the index proven non-reversible.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #212 — Voice cloning, in the order FIG. 800 draws it

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/212>

> From the field drawing: FIG. 800 is a **permission gate first and a recorder second** — 802 asks for permission to collect and use call information, 804 initializes collection, 806/808 collect from an active call, 810 analyzes it to determine the characteristics of the communication, 812 records the voice for cloning. That ordering *is* the design, so `qrme/voiceprint.py` makes it load-bearing rather than decorative.
>
> ## The flow, box by box
>
> | Step | Endpoint | What it does |
> |---|---|---|
> | 802 | `PUT /profiles/{id}/voiceprint/consent` | The permission, before anything is collected. `own_voice` is an **attestation** — QRME refuses to learn a voice on somebody else's behalf. Consent is scoped to named sources (`call` / `voice_note` / `direct`). |
> | 806–808 | `POST /profiles/{id}/voiceprint/samples` | A gathered sample. **Metadata only** — seconds, turns, transcript size, and a `reference` naming where the audio itself lives — so a voice corpus never accumulates inside the profile database. 403 with the reason when consent doesn't cover that source. |
> | 810 | (returned by every collect, and `GET …/voiceprint`) | The characteristics as arithmetic anyone can check: samples, seconds, mean turn length, mean chars per turn, sources. No opaque score. |
> | 812 | `POST /profiles/{id}/voiceprint` | Mints the print — refused until the enrollment is real (≥3 samples, ≥120s), so a thin enrollment is *called* thin instead of labelled ready. |
> | — | `POST /profiles/{id}/voiceprint/speak` | Speaks in the enrolled voice, always with the watermark credential **and** a spoken disclosure. |
> | — | `DELETE /profiles/{id}/voiceprint` | Withdrawal: samples deleted, print retired, the withdrawal itself left on record. |
>
> ## The three rules it inherits from the rest of the codebase
>
> - **Your own voice.** QRME's premise is a profile built from your own likeness; a voiceprint is that promise in another medium. Enrollment is owner-only and requires the attestation. There is no path here for a stranger, a celebrity, or a recording of someone who never agreed.
> - **The mark is not optional.** Synthesized speech leaves stamped (`qrme/watermark.py`) and carrying "this voice is synthesized … not a recording of them speaking these words." A cloned voice that doesn't say it is one is the thing this codebase exists to refuse.
> - **Revocable, and it means it.** Withdrawing deletes the samples and retires the print; the tombstone stays, which is the opposite of pretending nothing happened.
>
> ## Tests
>
> `tests/test_voiceprint.py` (9): the gate bites before collection; a non-own-voice attestation is refused; consent is scoped per source; the analysis is counted not scored; a full enrollment mints a print; speech always carries mark + disclosure; no print means no speech; withdrawal deletes samples and silences the print; and the constants are asserted directly.
>
> Full suite green: **1255 passed**.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #211 — Cut 0.16.0, and cite the publication number

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/211>

> The 0.16.0 release cut, carrying everything merged since 0.15.0.
>
> ## Publication number
>
> Application 19/056,418 (526.P002) **published as US 2025/0265659 A1 on August 21, 2025** — from the USPTO PDF in the field. A published application is citable public record, so the number now rides beside the application in the README's patent line.
>
> ## Version cut — 0.15.0 → 0.16.0
>
> Five version strings (`pyproject.toml`, `qrme/api.py`, `app/package.json`, both root entries of `app/package-lock.json`), the `[0.16.0]` heading over the changelog content the feature PRs wrote, the README release line + history row, and `RELEASE_NOTES.md`.
>
> **In this release:** wall uploads (photos, videos, files — kind decided by the bytes, caps published, never the AI mark) and pasted video links rendering as players on the nothing-loads-until-play facade; **Sign in with Google / Apple**, live only where configured; **DeepSeek** and **your own algorithm** on the model menu, the latter dark until its URL is set; the **advisor / collaborator / operator** role context (spec clauses 2 and 12) declared on a turn or read from the prompt itself; startup portrait self-repair; and the phone-layout fixes.
>
> ## Verification
>
> Full suite green (1246 at the last full run); version/changelog/README binding tests green (13); console and launcher builds green.
>
> ## Tag and release
>
> The tag is yours to push — `app-v0.16.0`. `RELEASE_NOTES.md` is the ready-to-paste body.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #210 — Two more doors on the model menu, and the role rides the turn

- merged · opened 2026-07-30 · merged 2026-07-30
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/210>

> The provider round plus the P002 clause audit, QRME side.
>
> ## What's here
>
> **DeepSeek + your own algorithm** — from the field ask: "give the users the option to plug in my algorithm … or DeepSeek or any others on the market … assign their logos to make the clickable attachments to where they can pick and choose."
> - **DeepSeek** joins the provider registry as a first-class entry (`QRME_DEEPSEEK_API_KEY` or `DEEPSEEK_API_KEY`; model override via `QRME_DEEPSEEK_MODEL`, default `deepseek-chat`).
> - **Your own algorithm** — a `custom` provider pointing at any endpoint speaking the OpenAI dialect: `QRME_CUSTOM_LLM_URL` + `QRME_CUSTOM_LLM_KEY`, optional `QRME_CUSTOM_LLM_MODEL`/`QRME_CUSTOM_LLM_LABEL`. Built as configuration so the day the founder's algorithm exists, no release is needed.
> - The custom tile **stays dark until its URL is set** (`needs_base` gate) — a key alone points at nothing. Console logo tiles for both.
>
> **Advisor, collaborator, operator (spec clauses 2/12)** — the clause-by-clause audit of the pasted P002 clauses found every embodiment already in code (simulation, environmental adaptation, watermarks, anonymity, memory, engagement, moderation, adult-consent, GPT providers) except role-specific contexts. Now real: a chat turn can declare `role: "advisor" | "collaborator" | "operator"`, or leave it unset and the profile reads the prompt itself (`qrme/roles.py` — transparent keyword inference, silent on a tie, never a hidden model call). The reply's `role_context` names the role and how it arrived (`declared`/`inferred`); frames shape *how* the profile works this turn, never *who* it is — persona, relationship, memory and moderation apply unchanged.
>
> ## Tests
>
> - `tests/test_models.py`: both new provider doors on `GET /models`; custom unconfigured until its URL lands.
> - `tests/test_roles.py` (6): declared role echoes, autonomous inference, plain turns stay plain, unknown role 422, transparent keyword unit test, declared-beats-inferred.
> - Full suite green locally (1240 at last full run + the 6 new); console `npm run build` green.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #209 — Uploads on the wall — pictures, video, files — pasted links play, and two new front doors

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/209>

> The picks from the open list (items 1 & 4) plus the composer requests, all of them.
>
> **Pictures, video, a note, files on every post.** The note is the post text; uploads carry the rest: kind decided from the file's bytes — images (JPEG/PNG/GIF/WebP), video (MP4/WebM), and **Files**: PDF by magic, the zip-family office formats (PK magic — the extension survives only from a whitelist, anything fancier becomes `.zip`), and plain text (`txt/csv/md`; a text file claiming `.html` serves as `.txt`, where markup is just characters — nothing a browser executes is ever served). Caps published at `GET /media/limits` (8 MB image / 60 MB video / 20 MB file); the uploader's filename rides as a display name only. Never the AI mark: authentic media stays authentic. Ownership checked before the post row is written.
>
> **A link dropped in the text renders the video, not just the text.** With no explicit video field, the first whitelisted URL in the body becomes the post's video — same facade contract, nothing loads from the platform until the viewer presses play. Unknown platforms' links stay text, now clickable.
>
> **Sign in with Google / Apple** (`qrme/oauth.py`): configuration decides whether the buttons are live; grey doors carry their exact setup note; the provider's word verifies the inbox; the parked session is claimable exactly once; passwordless accounts fail closed on typed passwords. Console buttons + browser flow + poll-claim.
>
> **Item 4 (Windows Hello signing)** needed no code: the WebView2 ceremony from an earlier round already talks to Windows Hello through Edge — awaiting a field test on a real machine.
>
> Tests: `test_wall_media.py` (5 — including the `.exe`→`.zip` and `<script>`→`.txt` refusals and the pasted-link auto-render), `test_oauth_signin.py` (3), wall suite green. Console upload flow verified live in a browser.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #208 — Field round: portraits self-heal, phone layout, and the Wall reaches the console

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/208>

> Field round, from live testing reports plus the transcript/photo re-audit. Everything below reproduced and verified against a running backend (screenshots in session).
>
> **Starter portraits missing over their names.** A deployment seeded before the portraits shipped has 34 starters with blank `avatar` columns, and the repair lived behind the Discover seed button nobody knows is a repair:
> - `seed.repair()` — blank-only portrait repair, run automatically at API startup. Heals starters **and the founder's two profiles**, which `_seed_one_founder`'s early return used to skip (0/36 faces → restart → 36/36, the photograph restored from the photo tree, never stamped with the AI mark). Never creates a profile.
>
> **"It wouldn't let me type in a topic for the room."** Reproduced at phone size: twelve tab labels forced the app to ~576px wide, so every form overflowed sideways and the Kind dropdown crowded the Topic box; the agent-lights circle and help fab sat on top of the bottom tab bar. The tab bar now scrolls, forms stack one column, corner widgets ride above the tabs, and Rooms-create without a profile names the requirement.
>
> **The Wall reaches the console.** The community layer (For You feed with stated reasons, posts, likes, comments, shares, shared-video links) has lived in the backend since the community round — the desktop console never got the door, which read in the field as the features not existing. New Wall tab: composer with optional video link (platform whitelist shown up front), video cards honoring the facade contract (nothing loads from the other platform until the viewer presses play), like/comment/share, and a Your-wall section so a solo owner doesn't post into apparent silence. Verified live with a YouTube link.
>
> Also: the `[0.14.5]` CHANGELOG link points at the cut commit instead of a tag that never shipped.
>
> Tests: startup-repair pair in `test_seed_backfill.py`; full suite 1230 green; console build green.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #207 — Cut 0.15.0 — the temperament dials

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/207>

> Release cut for **0.15.0**, in train with jim-mini and pdi. QRME's content this round is the temperament dial group (mood, outlook, maturity, agreeableness, confidence, curiosity) merged in #206.
>
> - CHANGELOG heading over the existing [Unreleased] story, RELEASE_NOTES.md, README current-release line and table row, five version strings.
> - Tag `app-v0.15.0` on the squash commit; release body stays empty for sync-release-notes.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #206 — The temperament dials — the field's list, verbatim

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/206>

> The transcript-mining round, QRME half. The vision video promises control over "mood, outlook, maturity, agreeableness, confidence, curiosity" — steering now has that list **verbatim**, as a fourth dial group:
>
> - **`temperament`** joins system / behavior / intimacy in `qrme/steering.py`: six dials, 0–100, default 50 = silence, each with honest low/high poles ("subdued and quiet-toned" ↔ "bright and upbeat"; "tentative, hedges" ↔ "self-assured, decisive"; …).
> - The render layer is generic, so the group flows into `GET /steering` catalogs, the persona-prompt directive, and any surface that reads the dial spec — no other code changed.
> - Test pins the group's membership and its prompt rendering (near-default dials stay silent).
>
> On the video's remaining "characteristics" list: language (the language setting), age/maturity (the aging lifecycle + the new maturity dial), and culture/background live in the freeform persona by design — the deliberate home for identity a table shouldn't flatten.
>
> Full steering suite green (7); console build green.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #205 — Cut 0.14.5 — cut with the siblings

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/205>

> Release cut for **0.14.5**, in train with jim-mini and pdi. No functional change in QRME this round — the content is JIM's (the fall path, the native crash watch, the docs web).
>
> - CHANGELOG rider + heading, RELEASE_NOTES.md, README current-release line and table row, five version strings.
> - Tag `app-v0.14.5` on the squash commit; release body stays empty for sync-release-notes.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #204 — Cut 0.14.4 — the console names a version mismatch

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/204>

> Release cut for **0.14.4**, in train with jim-mini and pdi at the same version.
>
> - CHANGELOG: 0.14.4 heading over the Unreleased content (version-mismatch banner; discovery-card faces with AI/real-photo badges; plain room labels; Blend explained; Erase all; the settings that say which secret is which; the send button clearing the fab), link definitions repointed
> - RELEASE_NOTES.md rewritten for 0.14.4
> - README: "Current release" line and release-table row
> - Version strings: pyproject.toml, qrme/api.py, app/package.json, app/package-lock.json (root entries)
>
> Tag `app-v0.14.4` on the squash commit fires the desktop-release workflow; the release body stays empty for sync-release-notes to fill.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #203 — Field feedback: faces on the cards, plain labels, erase all

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/203>

> Live-testing feedback, applied:
>
> - **Discovery cards get faces, with provenance**: `/marketplace` now returns `avatar` + `avatar_kind` per card (via `avatars.render()`, so anonymous profiles keep their silhouette and no hidden face can leak). The console draws the portrait — or initials — with an **AI** badge on generated portraits and **✓ real photo** only on an authentic photograph under `/photos`. New test: `tests/test_marketplace_cards.py`.
> - **Friends**: the "the founder stands first, on every list" subtitle is removed (the pinning itself is untouched).
> - **Rooms**: kind labels read plainly — **Text**, **Voice chat only**, **Video**, **AR**, **VR** (video was already there; nothing missing).
> - **Blend explains itself**: a new lead card says what blending *is* — it creates a brand-new openly-hybrid profile in the shares you choose; it is **not** following or friending, and the sources are untouched.
> - **Memory Vault**: **Erase all** beside the per-conversation erase, with one confirmation naming the count.
>
> (The "won't let me add anybody" / "interactor and profile" reports trace to the stale-backend issue the version guard now catches — the current console already shows real names and working add/erase.)
>
> `npm run build` green; full binding subset green.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #202 — The console names a version mismatch

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/202>

> Field report from live testing of JIM-mini: a fresh console over a stale backend answers **"Not Found"** on every newer screen while looking otherwise alive. The Electron shell already refuses to adopt a version-mismatched backend on its own port — but a **stored base address** (e.g. the LAN address saved for the phone bridge, which deliberately wins over the desktop URL) can still steer the console to an old process holding that address.
>
> The console now performs the version handshake itself, in all three products (sibling PRs in jim-mini and pdi):
>
> - `vite.config.ts` injects `__APP_VERSION__` from package.json → `CONSOLE_VERSION` in api.ts.
> - **`VersionGuard.tsx`** fetches `/health` on launch and compares versions. On mismatch: a fixed red banner on every screen — *"Two versions of QRME are answering. This app is v0.14.3, but the backend at &lt;base&gt; is v0.8.0…"* — with a one-click **"Use this app's own backend"** (clears the stored base and reloads) when the desktop shell's own backend is available, or plain instructions to end the leftover backend process otherwise. Dismissible; wraps onboarding too, since a mismatched backend at sign-up is the same trap one screen earlier.
> - A backend so old it predates the `/health` version field reads as "(older than 0.5)" instead of passing silently.
>
> `npm run build` (tsc + vite) green.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #201 — Cut 0.14.3 — the lights are always on

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/201>

> Release cut for **0.14.3**, in train with jim-mini and pdi at the same version.
>
> - CHANGELOG: 0.14.3 heading over the Unreleased content (the watch-sized minimizable lights window in the studio; the scripture closing every README, test-enforced), link definitions repointed
> - RELEASE_NOTES.md rewritten for 0.14.3
> - README: "Current release" line and release-table row
> - Version strings: pyproject.toml, qrme/api.py, app/package.json, app/package-lock.json (root entries)
>
> Tag `app-v0.14.3` on the squash commit fires the desktop-release workflow; the release body stays empty for sync-release-notes to fill.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #200 — The lights are always on + every README ends on the rock

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/200>

> Two requests in one branch:
>
> **1. The watch-sized lights window — on screen at all times, minimizable.**
> - **`app/src/WatchLights.tsx`** — a round, 176px watch-face-sized window pinned bottom-left (Help owns bottom-right), mounted in the App shell outside the tab switch so every screen has it. It shows the wrist's exact payload — 🟢 working, 🟡 needs a hand, 🔴 stopped, plus the profile chip and the approvals line — polling `GET /profiles/{id}/watch` every 15s with the owner token. The bezel ring takes the worst light's colour.
> - **Minimize** — the `–` control folds it to a 46px dot in the worst light's colour; clicking the dot restores it. The choice persists (`localStorage`), and a fetch blip keeps the last face instead of blanking.
> - README's "Where you actually see it" table gains the studio-widget row.
>
> **2. The scripture closes every README, from here on.**
> - The Matthew 7:24–25 passage (with the ark prose) that closes the root README now closes **every** README in the repo — `app/`, `launcher/`, `docker/`, `assets/design/`, and the four `native/` READMEs — byte-identical, at the very end.
> - `tests/test_readme_scripture.py` enforces the standing rule: every tracked README must end with the root README's passage block, so the next README added cannot forget it. Sibling PRs (jim-mini#145, pdi#117) apply the same rule.
>
> CHANGELOG entries for both. `npm run build` green; binding tests green.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #199 — Cut 0.14.2 — the vault posture survives suite mode

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/199>

> Release cut for **0.14.2**, in train with jim-mini and pdi at the same version.
>
> - CHANGELOG: 0.14.2 heading over the Unreleased content (gateway wires QRME's PDI tandem; `POST /suite/operations`; launcher joints; tandem-contract docs; smoke repair), link definitions repointed
> - RELEASE_NOTES.md rewritten for 0.14.2
> - README: "Current release" line and release-table row
> - Version strings: pyproject.toml, qrme/api.py, app/package.json, app/package-lock.json (root entries)
>
> Tag `app-v0.14.2` on the squash commit fires the desktop-release workflow; the release body stays empty for sync-release-notes to fill.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #198 — The launcher shows the joints

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/198>

> The suite launcher's dashboard catches up with the gateway's new surface:
>
> - **Joint lights** — the two tandems the gateway wires in-process (care-team tandem, vault sealing), read from `/suite/health`'s `tandems`. Amber means that joint runs degraded (no care team / no sealing), not that a product is down.
> - **Build my ecosystem** — one press calls `POST /suite/ecosystem`: demo org seeded in QRME, JIM's care team linked to its first desk; shows the org, its desks, and the link state. Idempotent, so pressing again finds the same one.
> - **Operations** — the owner-scoped list from `POST /suite/operations`: your coordinations as the vault recorded them, with a refresh and an empty-state pointer to JIM's Care Team tab.
>
> Launcher README documents the new dashboard section; CHANGELOG entry added. `npm run build` (tsc + vite) green.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #197 — Docs: suite mode enters the tandem contract

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/197>

> `docs/tandem.md` (kept byte-identical across qrme, jim-mini and pdi) gains a **"Suite mode — the gateway wires the tandems itself"** section under *qrme / jim-mini ✕ pdi*:
>
> - how the gateway wires both joints at startup (JIM's `QRMEClient` bridge; the `suite:qrme-vault` tenant injected as QRME's own `PDIClient`),
> - why the tenant token is a deployment credential and when the self-mint is refused (`PDI_ADMIN_TOKEN`),
> - what `GET /suite/health` `tandems` means (degraded, not down),
> - how `POST /suite/operations` re-draws PDI's per-tenant isolation **by owner** when every suite identity's seals share the one tenant.
>
> Plus a CHANGELOG entry. Sibling PRs carry the identical file to jim-mini and pdi.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #196 — The vault posture survives suite mode

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/196>

> In suite mode the mounted QRME ran with `app.state.pdi = None`, so coordinations quietly stopped sealing the moment the three products shared one origin — the vault posture was a casualty of the deployment shape.
>
> - **The gateway wires QRME's PDI tandem**: finds (or mints once, by name) a dedicated vault tenant `suite:qrme-vault` and injects QRME's own `PDIClient` over the in-process bridge. A deployment that already configured `QRME_PDI_URL` keeps its wiring; a PDI running with `PDI_ADMIN_TOKEN` refuses the mint and the operator configures the token explicitly, as they would standalone.
> - **`GET /suite/health` reports both tandems** (`jim_qrme`, `qrme_pdi`) — false means that joint runs degraded, not that it's down.
> - **`POST /suite/operations`** — the provenance view: the caller's coordinations as the vault recorded them, authenticated with their own QRME owner token and scoped by owner, because in suite mode every identity's seals share the one tenant. The vault token never leaves the process; another identity sees none of it; a forged token gets 403.
> - **Fixes `python -m suite.smoke`**, failing locally since the vault gate moved from deployment to plan: its user enrolled as a visitor, whose writes rightly stay out of the vault. The smoke now subscribes its user to a private plan before asserting the exchange sealed. (CI's qrme-only checkout skips the smoke, which is how it slipped.)
>
> Tests: `test_suite_mode_keeps_the_vault_posture` (sealing + provenance scoping + forged-token refusal), `test_the_vault_tenant_is_minted_once` (restart reuses the tenant), and the repaired smoke — 11/11 locally; suite tests skip in CI as before.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #195 — Cut 0.14.1 — the suite wires its own tandem

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/195>

> Release cut for **0.14.1**, in train with jim-mini and pdi at the same version.
>
> - CHANGELOG: 0.14.1 section under Unreleased (the suite gateway wires its own in-process tandem; `POST /suite/ecosystem` one-call bootstrap), link definitions repointed
> - RELEASE_NOTES.md rewritten for 0.14.1
> - README: "Current release" line and release-table row
> - Version strings: pyproject.toml, qrme/api.py, app/package.json, app/package-lock.json (root entries)
>
> Tag `app-v0.14.1` on the squash commit fires the desktop-release workflow; the release body stays empty for sync-release-notes to fill.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #194 — The suite wires its own tandem, and one call builds the ecosystem

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/194>

> Two seams the suite gateway was missing:
>
> - **The tandem wires itself.** In suite mode all three products share one process, but the mounted JIM had no QRME client — the care team couldn't work at all through the gateway. Now the gateway bridges JIM's `QRMEClient` to the mounted QRME app over an in-process ASGI transport: care team and specialist handoffs work with no second server and no `JIM_QRME_URL`. Skipped gracefully when either side is missing — a partial suite still comes up.
> - **`POST /suite/ecosystem`** — one call after `/suite/session`: hand back the tokens it returned (the gateway stays stateless, storing no credential) and get a working ecosystem — the demo org seeded in QRME (idempotent) and JIM's care team linked to its first desk.
>
> **Verification**: the new gateway test drives session → ecosystem → a manual coordination *through the gateway*, asserting the joint plan lands back in JIM — 8/8 suite tests green in the full-suite dev setup. CI's qrme-only checkout skips the suite tests by design (`pytestmark` skip), so the local run is the verification; the rest of CI is unaffected.
>
> Also fixed en route: this environment's sibling installs pointed at stale scratch snapshots; they now point at the live worktrees.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #193 — Cut 0.14.0 — the front page and the wrist

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/193>

> The 0.14.0 release-train cut for QRME: Home's "New in this release" card and the two new wrist faces (Proceeds, Coordination — counts only, drawn as watch faces 10-11) from #192. Cut mechanics per docs/releasing.md; siblings cut alongside.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #192 — The front page and the wrist learn the new doors

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/192>

> Two commits, one theme — the ecosystem round's features become findable and glanceable:
>
> - **Home** gains a "New in this release" card pointing at Blend, What If, Campaigns and Org. The doors existed; the front page never said so — and a door the front page doesn't name is a door testers never find.
> - **The wrist/pane** gains two faces with the same test as the four before them (a count-shaped answer to "is anything waiting on me", never the thing itself): **proceeds** — how your open campaigns are doing, never a donor's name — and **coordination** — whether the departments finished a joint plan, never the plan. Both route to their drawn screens (145, 146).
>
> Dock/agent-light suites: 43 passed; console build clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #191 — Cut 0.13.1 — demo, docs and hardening

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/191>

> The 0.13.1 release-train cut for QRME, bundling what landed after 0.13.0: the one-press demo org (#188), the docs round (#189), and the hardening caps (#190). Cut mechanics per docs/releasing.md; siblings cut alongside at the same number.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #190 — Hardening: caps and idempotency on the new surface

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/190>

> Three guards the ecosystem round's routes deserve, each with a test:
>
> - **An organization holds at most twelve departments.** A coordination is one model call per desk plus the composition pass — the department count is the request's cost multiplier, and the cap is what keeps one press from becoming a bill.
> - **The tokenless donate door gets a per-campaign daily count** (1000/day). Donations are deliberately tokenless — generosity isn't gated behind signup — which makes them the platform's one anonymous write; the count is far above any real campaign's daily traffic and low enough that the door can never become a ledger-spam hose.
> - **The demo-org button is idempotent.** Pressing it twice returns the same team instead of minting a second set of agents and grants.
>
> `tests/test_organizations.py` + `tests/test_campaigns.py`: 17 passed.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #189 — Docs round: the tandem contract + invention disclosure catch up

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/189>

> Two documents catch up with the ecosystem round, in one docs PR (siblings in jim-mini and pdi):
>
> **docs/tandem.md** — byte-identical in all three repositories (md5 `cef566d1…`):
> - **qrme ✕ jim-mini** gains "The care team is an organization": the user's own owner token (QRME's org routes stay owner-only, JIM never sneaks around that), the *stacking* trigger (drift + adherence below 75%, not severity), summaries crossing but never raw readings, once a day, calm path only.
> - **qrme / jim-mini ✕ pdi** gains the `qrme/coordination/{id}` key space and the operations journal — a view, never a side door.
>
> **docs/invention-disclosure.md** — five new dated sections for counsel: weighted hybrid personas with a public composition; predictive simulation with evidence-earned confidence; environmental context beside biometric context; proceeds designations with token-lifecycle succession; departmental agent coordination over revocable scopes.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #188 — Demo org: one press, a staffed organization

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/188>

> First PR of the next train: testers should meet the ecosystem working, not as an empty form.
>
> - `POST /organizations/demo` builds a complete team on the caller's own account: two enterprise agents (Workshop, Finance) each born with a small knowledge source and an all-scope **revocable grant**, desked into "The Demo Workshop", ready to coordinate — and ready to demonstrate revocation (revoke a grant, watch that desk's pulls stop).
> - Ownership stays honest: nothing touches the starter collection — those profiles belong to the platform, and a department may only be staffed by a profile its org's owner holds. The demo mints its agents *for* the caller and returns their owner tokens once, like profile creation does.
> - Console: the Org tab offers **"Found a demo org"** when no organization exists yet.
> - Test: the demo org is born ready — both desks scoped, a coordination runs immediately, and both agents actually pull their notes (`items_read >= 1`).
>
> Org suite: 9 passed; routing guard green; console build clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #187 — Cut 0.13.0 — the ecosystem round

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/187>

> The 0.13.0 release-train cut for QRME. This round: crowdfunding with proceeds routed where the user said (#185), the operational ecosystem (#185), and the console chrome following the profile's language (#186) — proved end-to-end against live JIM and PDI processes (care team coordinated from JIM, plan journaled in PDI, donation split exactly on the ledger).
>
> Cut mechanics per docs/releasing.md: CHANGELOG section + link definitions, RELEASE_NOTES for the `app-v0.13.0` tag, README release line + table row, five version strings (lockfile roots only — a dependency pinned at 0.12.0 stays untouched).
>
> JIM-mini and PDI cut alongside at the same number.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #186 — The console chrome follows the profile's language

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/186>

> The 0.5.x localization round covered the native reference apps (`native/ios/Sources/L10n.swift` and siblings); the Electron console — the app actually in testers' hands — still spoke English whatever the profile spoke.
>
> - `app/src/l10n.ts` carries the same chrome table as the native L10n files: all 12 nav labels plus sign-out, in the 10 backend-supported languages (en/es/fr/de/pt/it/ja/zh/hi/ar), falling back to English per key so a missing translation shows words, never a blank.
> - `App.tsx` reads `GET /profiles/{id}/language` the moment a profile is active and relabels the sidebar and sign-out; pick Español in a profile and the console frame follows.
> - Content localization was always server-side — this closes the console's frame around it, including the five tabs added this session (Blend, What If, Campaigns, Org).
>
> Console `tsc --noEmit && vite build` clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #185 — Both stones turned: crowdfunding with routed proceeds + the operational ecosystem

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/185>

> The round sweeps the two remaining unbuilt capabilities from the three founding documents — one from the QRME patent spec, one from the PDI proposal.
>
> ## 1 · Crowdfunding with proceeds routed where the user said (spec [0020], example two)
>
> > "supply crowdfunding for any loved ones, left behind or organizations for donations, wherever the proceeds might go up to the user"
>
> - `PUT /profiles/{id}/proceeds` designates loved ones and organizations with shares that must sum to exactly 100. Sunset changes nothing (the living owner keeps the pen); verified owner death (`/succeed`) revokes the old token and hands it to the chosen successor — "leave it in good hands," enforced by the token lifecycle.
> - `POST /profiles/{id}/campaigns` is **refused until a designation exists** and never opens on a rated profile — tips to a performer stay behind the age-gated gift.
> - `POST /campaigns/{id}/donate` is tokenless and capped like a gift; each donation splits at the door onto the ledger (computed in cents so shares re-add exactly); a designee with a platform account is paid on their own creator statement. The public card always shows the names — a donor gives to people, not to the platform.
> - Screen **145 · Where the Money Goes**, `proceeds` lesson, helper directions, **Campaigns** console tab.
>
> ## 2 · The operational ecosystem (PDI proposal)
>
> > "role-specific AI agents … collaborate across departments, pulling relevant data, offering smart suggestions, and coordinating efforts"
>
> - `POST /organizations` + `/departments` staff each department with one of your own profiles as its role agent — a stranger's profile is refused, and so is a rated one.
> - Department reads are scoped by the same **revocable grant** machinery as claim-25 tasks: revoke and the pulls stop instantly, the org stands (proved by test).
> - `POST /organizations/{id}/coordinate` takes one goal across every department: each agent contributes from its own scoped material in its own persona, the initiating agent composes the joint plan — watermarked synthetic, owner-only, never distributed — and with the PDI tandem configured the record is **sealed into the vault**.
> - Screen **146 · The Ecosystem**, `ecosystem` lesson, helper directions, **Org** console tab.
>
> ## Verification
>
> - `tests/test_campaigns.py` (11) + `tests/test_organizations.py` (5) + all binding suites (tutorial/dock/help/gallery/routing): **87 passed**.
> - Console `tsc --noEmit && vite build` clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #184 — Cut 0.12.0 — the specification, mined

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/184>

> The 0.12.0 release-train cut for QRME — this round's feature repo. The filed patent specification (App. 19/056,418, SYNTHETIC USER PROFILE MANAGEMENT) was read end to end and everything it describes that the apps did not yet do was built in, backend (#182) and console (#183):
>
> - **Hybrid profiles** — blended from several people, shares and borrowed aspects, honest about being a blend; Blend tab, screen 142.
> - **Real-time simulation** — the represented person's likely decision and workflow, confidence earned from evidence; What If tab, screen 143.
> - **Environmental adaptation** — replies that fit where the person actually is; 📍 toggle in Chat, screen 144.
>
> Cut mechanics per docs/releasing.md:
> - CHANGELOG 0.12.0 section + link definitions repointed
> - RELEASE_NOTES.md refreshed for the `app-v0.12.0` tag
> - README current-release line and release-table row
> - Version bumped in all five places (pyproject, `qrme/api.py`, package.json, both lockfile root entries)
>
> JIM-mini and PDI cut alongside at the same number (pdi#106 and the jim-mini cut PR), both "no functional change".
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #183 — The console shows the mined features: Blend, What If, and where you are

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/183>

> The console round for #182's three spec-mined capabilities. They existed only as API routes; now every layer that binds a feature to the product carries them — the same pipeline every feature goes through (screen → lesson → directions → gallery → console).
>
> ## Screens 142–144
> - **142 · Blend a Profile** — the hybrid's shares and borrowed aspects, the honesty rule, and the two refusals (rated never blends; strangers need a listing).
> - **143 · What Would They Do** — decision, workflow, confidence *earned* from evidence, marked as AI and private.
> - **144 · Where You Are** — location/conditions/time riding beside the claim-23 biometrics, woven in and never recited back.
>
> Drawn for both platforms (288 SVGs regenerated); the builder's width audit shaped every card title.
>
> ## Walkthrough & helper
> - New lessons `blend` ("Getting started") and `predict` ("Working"); the `talk` lesson now teaches telling the profile where you are and claims screen 144.
> - `help.DIRECTIONS` phrases for each — "both grandparents", "what would they do", "knows where i am" — so the helper can point at all three.
> - README gallery rows for 142–144.
>
> ## Console (`app/`)
> - **Blend tab** — pick ≥2 candidates (your own profile + marketplace, exactly the sources the backend accepts), set shares and a borrowed aspect each, see the live percentage, blend, view the recorded composition, and adopt the hybrid as the active profile.
> - **What If tab** — owner-only simulation runner: scenario + horizon, the prediction with its disclaimer, and the confidence shown *with* the source-items/remembered-turns basis it was earned from; past runs listed.
> - **Chat** — a 📍 toggle opens where/conditions/doing fields that ride as `environment` on the message; an adapted reply is labeled "adapted to where you are". Off until opened, empty until filled — nothing is inferred or collected.
>
> ## Verification
> - `tests/test_tutorial.py`, `test_dock.py`, `test_help.py`, `test_docs_gallery.py`, `test_spec_mined.py`: **82 passed** — every screen claimed by a lesson, every lesson reachable by the helper, gallery in sequence.
> - Console: `tsc --noEmit && vite build` clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #182 — The specification, mined: hybrid profiles, real-time simulation, environmental adaptation

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/182>

> A full read of the filed specification of App. 19/056,418 (SYNTHETIC USER PROFILE MANAGEMENT, docket 526.P002) turned up three capabilities the spec describes that the code did not yet have. Each is implemented here from the spec's own words, with tests in `tests/test_spec_mined.py` and a README section ("The specification, mined") citing the passages.
>
> ## Hybrid profiles — spec [0038]
>
> > "a combination of aspects or characteristics of several people, such as a combination of several past presidents or business leaders, a combination of trusted relatives such as grandparents who are gone"
>
> - `POST /profiles/composite` blends ≥2 source profiles into one `kind=hybrid` profile (`qrme/composite.py`): per-constituent normalized weights and an optional borrowed *aspect* ("their patience", "their storytelling"), recorded in `composite_sources`.
> - `GET /profiles/{id}/composition` publishes the blend to anyone — the same open stance as `/transparency`.
> - Sources must be the caller's own or marketplace-listed. **Departed profiles may be blended on purpose** (grandparents who are gone is the spec's own example); rated profiles never; `kind=hybrid` cannot be typed free-hand on `POST /profiles`.
> - The persona prompt carries the blend honestly: a hybrid says who it is a composite of and never claims to be any single constituent.
>
> ## Real-time simulation / predictive modeling — clauses 1 & 5
>
> > "real-time simulations of the first person's actions, workflows, and decision-making processes for predictive modeling and operational insights" · retained memory "utilized for predictive modeling"
>
> - `POST /profiles/{id}/simulate` (owner-only, `qrme/simulation.py`) predicts the decision, concrete workflow, and in-character rationale for a scenario over `immediate` / `short_term` / `long_term`, optionally conditioned on one relationship's memory and latent embedding.
> - `confidence` is **earned from evidence volume** (source items, remembered turns, embedding present) — never from how sure the model sounds. A profile with no material scores 0.2 however fluent its answer; conditioning on real memory raises it, and the test proves the ordering.
> - The narrative is watermarked synthetic, stored with its basis, and never distributed — which is also why there is no moderation step: moderation gates what leaves toward an audience, and a simulation has none.
>
> ## Environmental adaptation — clause 1
>
> > "dynamically adapt to environmental data, such as location, conditions, and user behavior, enabling contextual relevance"
>
> - `ChatRequest.environment` ({location, conditions, local_time, activity}) rides beside the claim-23 biometrics: stored in `environment_context`, rendered into the system prompt so the reply fits where the person actually is, and echoed back on `ChatResponse.environment`.
>
> ## Verification
>
> - `tests/test_spec_mined.py`: 11 new tests — blend + normalization, public composition, stranger/rated-source refusals, free-hand `kind=hybrid` refusal, hybrid chat, confidence honesty and ordering, owner-only simulation, environment storage/echo.
> - Full suite: **1205 passed** locally.
> - Live boot drive: profile → composite → simulate end-to-end against the stub provider.
>
> Console screens for the three features are left for a console round, matching how the claims 21–26 features landed (backend first, screens in 0.11.0).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #181 — Cut 0.11.1 — no functional change; cut with the siblings

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/181>

> In PDI, the desktop app finally carries its own vault. **1194 tests green**, unchanged in behaviour.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #180 — The console catches up with its backend — 0.11.0

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/180>

> Field-tested and found wanting: the backend has had friends (founder pinned first), a marketplace, a 33-profile starter collection, rooms across five channels, and live desks for many releases — and the console showed none of it.
>
> ## Three new screens
>
> - **Discover** — marketplace cards, tag search, one press to install the **33-profile starter collection** (idempotent server-side); every card is a real profile with an *Add friend* button.
> - **Friends** — the list with **David Bianchi and his synthetic profile pinned at positions one and two** (enforced by `qrme/friends.py` since the friends round — finally visible), plus suggestions.
> - **Rooms** — open and list rooms across **2D text / 2D audio / 2D video / AR / VR** (AR/VR carry an honest badge: step inside from a headset or phone; the desktop shows the room), plus **live desks** with presence and the 18+ badge where it applies. Backed by new `GET /rooms` and `GET /desks` list routes — the per-id routes existed; the doors didn't.
>
> ## The memory vault names names
>
> `GET /profiles/{id}/memories` (owner-only): one row per remembered conversation — *Dana with June Bianchi · 12 turns · last Tuesday* — never "profile" and "interactor". View any conversation; **erase exactly the one you choose**.
>
> ## Chat's fallback stopped performing a character
>
> "[stub reply in a warm tone to: hi]" was a stage direction leaking into the play. The fallback now quotes what it heard plainly, says no model answered, and names both doors out (a provider key, or Ollama). The quoted echo stays on purpose — moderation must see user-influenced text ride into the reply, end to end (the maturity-gate test depends on it and still passes).
>
> Cut **0.11.0** with the siblings.
>
> ## Verification
>
> **1194 tests green** (6 new): the vault lists conversations by real names, owner-only; erasing one conversation leaves the others; rooms list with their channels (voice/ar/vr) and participant counts; desks list with presence; the fallback carries no stage directions and names ollama.com. Console build clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #179 — A real offline model — 0.10.0

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/179>

> Same round as JIM-mini: **Ollama as a first-class Local provider**. Install it, `ollama pull deepseek-r1:1.5b`, and QRME finds the daemon on its own — the tile lights up configured, no key, nothing leaves the machine. Automatic prefers a running local model over the stub when no cloud key exists; offline mode uses it too. `QRME_OLLAMA_MODEL` / `QRME_OLLAMA_URL` override.
>
> Cut **0.10.0** with the siblings. **1188 tests green.** Console build clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #178 — Cut 0.9.1 — no functional change; cut with the siblings

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/178>

> In JIM-mini, the watch panel became honest about reachability. **1188 tests green**, unchanged in behaviour.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #177 — Cut 0.9.0 — no functional change; cut with the siblings

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/177>

> The three products are cut as one release. In JIM-mini, the medicine cabinet arrived: medications in the user's own words, a day board with humane grace, an as-needed ceiling that refuses to log past itself, and a coach that notices a missed critical dose without ever alarming.
>
> **1188 tests green**, unchanged in behaviour.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #176 — Continuity joined up — 0.8.0

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/176>

> No new routes: QRME's part of the continuity story was already built — reviewer-gated ownership succession (`POST /profiles/{id}/succession`) and the memorial sunset. What this round adds is the **join**, now documented: a JIM-mini vigil event id serves as the succession `verification_ref`, and the same reference activates PDI's new bequests — one attested absence carries through all three products.
>
> Disclosure entry added to `docs/invention-disclosure.md`. Cut **0.8.0** with the siblings.
>
> ## Verification
>
> **1188 tests green**, unchanged in behaviour. Console build clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #175 — The app keeps itself current — 0.7.0

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/175>

> Same round as the siblings: on launch the desktop shell asks GitHub Releases whether a newer version exists (`electron-updater`). Windows/Linux download in the background and offer one restart (`killBackend()` first, so the new version starts its own backend); macOS is told and taken to the download page. Every failure path silent by design.
>
> Also pays a debt the screens round left: the tutorial guard requires every drawn screen to carry a lesson, and **141 (the model picker) had none — the suite was red on `main`**. Lesson added under *You are in control*, plus helper directions ("which model", "swap the model", the provider names) so the dock can point at it.
>
> ## Verification
>
> **1188 tests green.** Console build clean; `main.cjs` syntax-checked; `electron-updater` packaged as a runtime dependency; `build.publish` set to this repo.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #174 — Screen 141: the model picker the gallery didn't show yet

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/174>

> One new screen in `docs/screens/build.py`, generated for **iOS and Android** and added to the README gallery:
>
> - **141 · Which Model Answers** — Claude speaking for the profile, five providers one tap away, the on-device key, and the amber honesty notice when a reply would come from the offline helper.
>
> (Authored first as `num=100`, which collided with *Video Full Screen* — the builder's stale-file sweep caught the strays; the number moved to 141, the next free slot. No duplicate numbers remain.)
>
> Every `docs/**.svg` referenced by the README verified present on disk.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #173 — Restore the owner's LICENSE exactly as he wrote it

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/173>

> PR #172 squash-merged a stale snapshot that still carried the license rewrite, so the rewrite reached main against the owner's explicit instruction. This restores the LICENSE byte-identical to his last deliberate license commit (`9ed125b` — "Update permission clause in LICENSE file"), along with the MIT metadata lines in `pyproject.toml` and `app/package.json` that accompanied it.
>
> The invention disclosure (`docs/invention-disclosure.md`) stays.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #172 — Record the inventions with dates

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/172>

> `docs/invention-disclosure.md` — QRME's distinctive mechanisms with dates and code anchors: the owner-governed synthetic profile with watermarked outputs, the single-chokepoint membership gate, request-scoped bring-your-own-credential inference, vault-sealed tandem custody, desk beacons, microphone lending. Written to be handed to a patent attorney, and standing as a public, git-timestamped priority-of-invention record.
>
> **The LICENSE is untouched — it stays exactly as the owner wrote it.**
>
> Not legal advice, and no substitute for counsel. No version cut: nothing behavioral changed.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #171 — Model honesty in Settings — 0.6.1

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/171>

> The silent case was the bad one: *Automatic* quietly resolving to the built-in offline stub under a screen full of provider logos.
>
> **Settings → Which model answers** now shows an amber notice when replies would come from the built-in helper (no working key on the deployment), and when a picked provider has no key so another will answer. New `.degraded` style, distinct from `.error`: nothing failed to deliver — it degraded.
>
> (In JIM-mini, the same round also stopped the coach performing distress it never detected — see its PR.)
>
> Cut **0.6.1** with the siblings.
>
> ## Verification
>
> **1188 tests green.** Console `npm run build` clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #170 — Cut 0.6.0 — no functional change; cut with the siblings

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/170>

> The three products are cut as one release, so the version moves here even though QRME gained no route, no schema and no behaviour.
>
> In JIM-mini: the Apple Watch found its way in — a Shortcuts automation drips Health readings at a per-user tokened URL, and the Health app's export seeds the baseline from months of history in one upload.
>
> ## Verification
>
> **1188 tests green**, unchanged in behaviour — which is the point.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #169 — Pick your model by its own logo — 0.5.0

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/169>

> The model picker was a dropdown of provider strings, which is a poor way to answer "who is speaking for my profile right now."
>
> **Settings → Model** now shows a tile per provider — Claude, ChatGPT, Grok, Perplexity, Gemini — each with its own glyph, drawn here rather than copied, plus *Auto* for "whichever is configured." A provider with no credential says so on its tile instead of failing later.
>
> The choice rides the provider layer that already carried the bring-your-own-key header, so a request with `x-llm-api-key` still runs on the caller's credential and still never persists or logs it.
>
> ## Release
>
> Cut **0.5.0** with the siblings: CHANGELOG, README, RELEASE_NOTES, and all five version strings.
>
> ## Verification
>
> **1188 tests green**, including that the selected provider survives a restart, that choosing a provider with no credential reports that plainly instead of silently answering from another one, and that the request-scoped key still outranks the stored one. Console `npm run build` clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #168 — Email delivery is configurable from the app itself — cut 0.4.8

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/168>

> Mirror of jim-mini's round. An app hands mail to a mail server; until now the only way to name one was an environment variable, so a desktop install could never send a verification email at all.
>
> **Settings → Email delivery** (`mail_settings`, `GET/PUT/DELETE /settings/mail`, `POST /settings/mail/test`) now takes a mail server, username, app password, from address and link address. It reports which of three sources is in force — environment > settings screen > none — and **sends a real test message on demand**, surfacing exactly what the mail server said rather than claiming success. The password goes up and never comes back down.
>
> 1188 tests green. 0.4.8 release prep included.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #167 — An upgraded app no longer adopts an older install's leftover backend — cut 0.4.7

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/167>

> Mirror of jim-mini's fix, from the root cause behind three "fixed" signups that weren't: the shell adopted whatever backend answered its port, and on Windows quitting killed the frozen backend's *launcher* while leaving the real Python process alive — so a zombie from an early install could hold 8000 across every upgrade and serve its old API to each new console.
>
> - `/health` reports the backend's **version**.
> - The shell adopts a running backend **only when that version is its own**; otherwise it takes a free port, starts its own there, and passes that exact address to the window (a stored loopback address never overrides it).
> - Quitting kills the backend's **whole process tree** (`taskkill /T` on Windows).
> - The release gate now asserts the frozen backend reports the version being packaged.
>
> 1180 tests green. 0.4.7 release prep included.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #166 — A stranded pending account is finished on a no-mail machine — cut 0.4.6

- merged · opened 2026-07-28 · merged 2026-07-28
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/166>

> Databases from older builds hold half-made accounts (0.4.3 crashed mid-signup) that nothing can ever verify where no mail can be sent — and they were resurrecting the email screen on desktop installs. Retrying signup on a no-mail deployment now finishes the pending account on the spot, under the newly-typed password. A **verified** account is never overwritten this way, on any deployment; SMTP deployments still require the emailed proof. Guard test covers both sides. 1179 tests green. 0.4.6 release prep included.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #165 — Verification matches the deployment: direct on desktop, link-first by mail — and the 0.4.5 cut

- merged · opened 2026-07-28 · merged 2026-07-28
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/165>

> Mirror of jim-mini's round, from the same 0.4.4 field report: the code screen waited for an email that can never arrive — a desktop install has no mail service.
>
> - **Desktop (no mail transport): signup activates directly.** The machine owner is trusted on a single-user local install; there is no inbox to prove. Create account → into profile creation.
> - **Hosted (SMTP): the email now leads with a clickable verify link** (`GET /verify-email/click`, human-facing result page), 6-digit code as fallback; the app polls sign-in with the credentials it already holds and continues on its own after the click.
> - A pending account left by a crashed signup routes straight to verification with a fresh code instead of stranding the retry; already-verified routes to sign-in.
> - The packaged app can open its own backend log (Electron bridge button).
> - Smoke gate updated: the frozen binary must now sign up **straight into an account session** on each OS, then create a profile and chat.
>
> 1178 tests green; frozen binary rebuilt and smoke-passed locally; consoles typecheck and build. 0.4.5 release prep included.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #164 — Release gate: the frozen backend must perform the real first run, per OS

- merged · opened 2026-07-28 · merged 2026-07-28
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/164>

> No installer ships a first run that was not performed. Before electron-builder touches anything, the exact PyInstaller binary that will be packaged runs the whole flow **on the runner's real OS** — signup, the code read from the console log the way Electron pipes it, verify, a profile under the account, a chat, sign-in — with `PYTHONIOENCODING=cp1252:strict` so the Windows console-encoding class of failure is exercised on every platform, Linux included.
>
> 0.4.3 shipped a Windows-only signup 500 this step would have refused to package. "It worked on Linux" stops being a release argument here.
>
> Verified locally against fresh frozen binaries, twice in a row each (the double-run caught and fixed a leftover-process bug in the gate itself: PyInstaller one-file spawns a child the parent's kill doesn't reach — per-run ports + process-group kill now).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #163 — Fix the Windows signup 500, and cut 0.4.4

- merged · opened 2026-07-28 · merged 2026-07-28
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/163>

> Reported from a real 0.4.3 Windows install within the hour of shipping: signup answered `Unexpected token 'I', "Internal S"… is not valid JSON`.
>
> Two stacked bugs:
>
> - **The backend 500'd**: with no mail server configured, the verification code prints to the server console — in a banner drawn with `═` box characters that the frozen Windows backend's cp1252 stdout cannot encode. The print raised mid-request. ASCII banner now; `packaging/backend_entry.py` reconfigures stdout/stderr to replace rather than raise; a test encodes the console delivery to cp1252 forever (mutation-checked: restoring one box character fails it).
> - **The console hid the real error**: `req()` assumed every body is JSON, so the person saw a JSON.parse exception instead of "Internal Server Error". Non-JSON bodies now surface as the server's own words.
>
> Plus the 0.4.4 release prep (changelog, notes, README table, five version strings under the guard). 1175 tests green.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #162 — mac: declare the frozen backend in x64ArchFiles

- merged · opened 2026-07-28 · merged 2026-07-28
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/162>

> The `app-v0.4.3` build failed on macOS only: the universal build merges the x64 and arm64 app bundles, and `@electron/universal` refuses any file identical in both that is not declared — which the PyInstaller backend binary is, being one file for both architectures. One config line: `mac.x64ArchFiles: "Contents/Resources/backend/*"`.
>
> Windows and Linux built fine; the release job skipped (and no installers attached) only because the matrix had this one failure. After merging, move the `app-v0.4.3` tag to the fix commit and the workflow will attach the full installer set.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #161 — Accounts, bring-your-own model key, the self-running installer — and the 0.4.3 cut

- merged · opened 2026-07-28 · merged 2026-07-28
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/161>

> Four commits: the QRME half of the packaging round, the account layer mirroring jim-mini's, a gitignore fix, and the 0.4.3 release prep.
>
> ### Accounts: email + password, the address verified before sign-in works
>
> The account is what *owns* — its id is the `owner_id` profiles are created under and the `account_id` memberships bill to — while every profile keeps its own owner capability token exactly as before. `POST /signup` creates an account that **cannot sign in yet**: a 6-digit code goes to the address (SMTP when `QRME_SMTP_HOST` is configured, printed to the server terminal otherwise) and only `POST /verify-email` proves the inbox and mints the first account token. `POST /signin` refuses unverified addresses and answers unknown-address and wrong-password identically; `POST /password/reset/request` + `POST /password/reset` change a forgotten password by the same emailed-code proof and **revoke every account session**. Passwords PBKDF2 with per-account salts; codes hashed at rest, single-use, 15-minute expiry, purpose-bound. The console onboarding is now two stages — the account gate (tabs, show/hide toggles, re-enter password checked live, Forgot password) and then profile creation under the signed-in account.
>
> ### Bring-your-own model key
>
> `x-llm-api-key` rides any request into a request-scoped context variable the provider layer reads — that request's generations run on the caller's credential, **never persisted, never logged** (a test dumps the whole database and asserts the key isn't in it). An explicit provider choice plus a caller key counts as configured; a key on auto defaults to Claude rather than the stub; the deployment's env key remains the fallback. The Control Center stores the key device-side only.
>
> ### The installer runs itself
>
> `packaging/backend_entry.py` freezes the whole backend with PyInstaller; the release workflow builds it per-OS and ships it via `extraResources`; Electron probes `/health`, spawns the bundled backend when nothing answers, and kills it on quit. Verified on Linux: the frozen binary boots and answers.
>
> ### Cut 0.4.3
>
> Changelog, release notes, README release table, all five version strings moved together under the five-way guard.
>
> **Verification:** 1174 tests green (16 new). `tsc --noEmit && vite build` clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #160 — Online model default, and the desktop first-run fixed

- merged · opened 2026-07-28 · merged 2026-07-28
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/160>

> Three commits, all from running the product for real today.
>
> ### Default the Anthropic provider to claude-opus-5
>
> The default model string in `qrme/llm.py` (and the two README rows quoting it) still named the previous Opus generation. `QRME_MODEL` still overrides; every other provider default untouched.
>
> Verified live: with `QRME_LLM=anthropic` the server dials the real Anthropic API on every chat (request IDs minted by api.anthropic.com), `GET /models` reports `claude-opus-5`, and the per-profile switchboard (`PUT /profiles/{id}/model`) stores and honors provider choices.
>
> ### Desktop onboarding first-run (same defects reported against JIM Guardian's Windows build)
>
> - The age-verification field shipped pre-filled with a sample birthdate; it now starts empty and Create My Profile waits for a real one. (The name field was already deliberately empty here — JIM's screen broke that rule; fixed on its side in jim-mini#111.)
> - A network-level fetch failure surfaced as "Failed to fetch"; it now names the backend URL it could not reach and how to start one.
>
> ### serve: default CORS open on loopback, so the console's own advice works
>
> Same dead-end as JIM Guardian's: the packaged console calls the API cross-origin, and `python -m qrme serve` never set `QRME_CORS_ORIGINS`, so every request died as "Failed to fetch" against a backend that was running fine. A loopback serve now defaults CORS open — the posture the in-app hint has always instructed — announced on stdout, with `--no-cors` to keep it closed, and never when binding beyond loopback or when an explicit allowlist is set. Owner and interactor endpoints still require their bearer tokens. Four tests. The console's error message now names `python -m qrme serve` (bare `python -m qrme` only prints the launcher menu).
>
> Verified: `tsc --noEmit && vite build` clean. 1158 backend tests green.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #159 — The desktop installers were labelled 0.3.3

- merged · opened 2026-07-28 · merged 2026-07-28
- `claude/qrme-viewfinder` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/159>

> Found while verifying the app-v0.4.1 release you just published: the attached installers are named `QRME-0.3.3-universal.dmg`, `QRME.Setup.0.3.3.exe`, etc.
>
> `app/package.json` carries its own version and no cut ever bumped it — the 0.4.0 and 0.4.1 releases both attached installers stamped 0.3.3. They were **built from the right tag and contain current code**; only the label is stale. The part that actually bites is the auto-updater, which compares package versions and will tell an installed app there is nothing newer.
>
> Same disease as the stale test counts and the stale refusal counts this round already fixed: a duplicated number with nothing to fail when the other copy moves.
>
> - `app/package.json` → `0.4.1`
> - A guard test asserting it always matches the API version, mutation-checked
> - The launcher's `package.json` is deliberately untouched — it versions on its own cadence and its assets are not stamped with the release number
>
> The already-published 0.4.1 installers keep working; the next tag builds correctly named ones. No re-tag needed.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #158 — Cut 0.4.1 — the round where free got honest, and the claims got checked

- merged · opened 2026-07-28 · merged 2026-07-28
- `claude/qrme-viewfinder` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/158>

> Release housekeeping only — no code beyond the version string. 1153 tests unchanged.
>
> - CHANGELOG: `[Unreleased]` → `[0.4.1] — 2026-07-28`
> - `qrme/api.py` version `0.4.0` → `0.4.1`
> - README: header to v0.4.1, a 0.4.1 row in the release-history table
> - `RELEASE_NOTES.md` rewritten as the ready-to-paste body for the `app-v0.4.1` release
>
> Two leftovers from the previous cut, fixed while passing: the CHANGELOG's `[Unreleased]` compare link still pointed at `app-v0.3.3` and no `[0.4.0]` link ref was ever added; and `RELEASE_NOTES.md` was still the 0.3.3 body.
>
> After merging: create the `app-v0.4.1` tag on the merge commit and paste `RELEASE_NOTES.md` as the release body — tags and releases are proxy-blocked for this session, so those two steps are yours.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #157 — Channel 3, a free plan under platform custody, and the guards that check the claims

- merged · opened 2026-07-28 · merged 2026-07-28
- `claude/qrme-viewfinder` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/157>

> Four rounds on one branch, because they interlock. 1153 tests pass.
>
> ## Channel 3 — sharing your camera
>
> `qrme/viewfinder.py`, 7 routes, 28 tests, screens **136** and **137**. Point your camera at the thing — a knocking engine, a boiler, a document — so somebody else can see it, like screen-share but for the room. The subject sets the rules: a thing, place or document can be watched by anyone; **a body only ever by a person, never a synthetic profile**. Two taps to open, one to close, hard time cap, disclosure on every surface, and `NEVER` (camera control, capture trigger, background start, silent run) asserted rather than intended.
>
> ## A free plan, with nothing private about it
>
> `qrme/storage.py`, 38 tests, screens **138–140**. Two postures: **open cloud** (Free — the platform's own database, in the clear) and **vault** (Basic and Pro — sealed in PDI under a key you can hold). Free and Basic reach identical capabilities — `includes("free") == includes("basic")`, asserted — so **$20 buys privacy, not features**. The disclosure is a field on every surface that states a plan, and the open posture names its readers instead of gesturing at them.
>
> Refused rather than quietly exposed, on the test *whose exposure is it*: source material about somebody else, anything behind the age gate, and **a clinician's written opinion about a real person** — which was heading for the open store because the referral flow writes through `referral.reply` rather than `add_source`, so the third-party rule never saw it. Refused at `/referrals/prepare`, before any clinician is contacted.
>
> ## Platform custody, and the vault gate that asked the wrong question
>
> The free plan is the hosted-assistant arrangement: **QRME holds the work and the person has access to it**, over ordinary HTTPS, never through a vault. Named as **custody, not ownership** — a product decides who holds and operates a record; it does not get to decide away statutory rights over personal data.
>
> The bug underneath: every seal point read `if pdi is not None` — whether the *deployment* has a vault, not whether the *account* pays for one — so a free account on a PDI-backed deployment had its work sealed into a vault it could not hold a key to. `storage.vault_for(plan, pdi)` is now the one place the question is asked, guarded by **counting vault writes**, not reading call sites. Reads, deletions and signing keep the real vault deliberately: a plan-gated vault on a read strands a downgraded account's history; on a delete it fakes erasure; on `_seal` it silently stops writing the custody chain, since signers are often interactors with no membership.
>
> ## The guards that check the claims
>
> - A hard line is never answered with a price: a rated profile of a real person is 403 at any amount, ordered before the 402 posture check.
> - No user-facing copy may hardcode a refusal count that disagrees with `len(SENSITIVE)` — this drift shipped (four places said "two" after the list grew to three), and screen 140 didn't draw the third refusal at all.
> - The README's own arithmetic is now tested: every "`module.py`, N tests" claim is verified against the files, after two were found stale.
> - A refusal test must be reached by a request that would otherwise succeed — a mutation check caught one of this PR's own tests passing with the guard removed.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #156 — v0.4.0 — the social layer, channel 2, who you are allowed to be, and a price

- merged · opened 2026-07-27 · merged 2026-07-27
- `claude/qrme-friends` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/156>

> **Cuts v0.4.0.** Fifty-four commits. Eighteen new modules, 1,086 tests, 352 endpoints, 135 phone screens, 9 watch faces, 14 desktop views.
>
> The original title said the founder *"can be removed"* and the body said `DELETE` works on him like anybody else. That was true of the first commit and stopped being true two commits later, when the pin was made unremovable. Since this squashes onto main, that description would have become the record — so it is rewritten here rather than left to be the thing somebody reads in a year. The same applies to the last line of the previous version, which said channel 2 remained held. It is now green-lit and included.
>
> ## Who you stand with
>
> `friends.py` — profile ↔ profile, deliberately **not** the existing `relationships` table, which records how a profile treats an *interactor*. A test pins them apart, because a bug that read one as the other would look exactly like working code.
>
> Directed, not mutual: `befriend` writes one row, because a friends list is a claim its owner makes and a mutual edge would let somebody else edit yours. `mutual` is reported per entry so a surface shows the difference rather than inventing it.
>
> **Two founder rows, pinned first and unremovable.** `unfriend` refuses them by name — enforced in the one function every removal path goes through, not at each call site. Position is computed from `origin`, never stored, so it cannot drift out of step with what the row says.
>
> `verification.py` gives the pair its meaning: a **photograph** with a gold VERIFIED mark burned bottom-right, and an **AI rendering** with the AI badge. *This picture is authentic* and *this profile is synthetic* are two different claims, so they live in two directories — `/photos` is never AI-marked, `/portraits` always is.
>
> ## Anonymous, several, and exactly one verified
>
> `identity.py` — 8 routes, 21 tests, screens 118 and 119. Three things a person is allowed to be, and the module is the tension between them: you may be anonymous, you may hold as many profiles as you like, and **at most one may be verified**.
>
> The badge is not a quality score. It is the sentence *this is that particular real person* — said of two profiles at once it is either false of one of them, or a claim that one human being is two authenticated people, which is precisely the primitive verification exists to deny everybody else. So it **moves rather than multiplies**: one at a time, not one forever, because a rule somebody could only satisfy by deleting a profile is a rule they would answer by lying. `checked_at` is deliberately not re-stamped — a document seen in 2019 is not a document seen today because the badge changed seats.
>
> A `fictional` profile is **unverifiable rather than unverified** and never consumes the slot; getting that backwards would let an invented character lock a real person out of their own badge.
>
> **Writing the rule found the defect underneath it.** `anonymous` was honoured by the four surfaces that *render* a profile — front-page card, landing page, prompt, watermark — and by the route that returns one, not at all. `GET /profiles/{id}` is public and handed over `display_name` in full, so the shortest way past anonymity was to ask for the profile.
>
> `owner_id` was the worse half, because it does not undo one profile's anonymity — **it undoes all of them at once**. Two anonymous profiles sharing an account are the same person, and anybody could read that field off both and match them, then read it off the named profile beside them and put a name to the pair. Both withheld from everyone but the owner now, on every profile, along with `successor_owner`.
>
> An anonymous profile's badge withholds **who checked**: "verified by Dr Okafor of St Mary's" narrows an anonymous author to a city and a workplace. What survives is the part worth having, and the reason an anonymous profile would want one — *a real person stands behind this, and somebody checked* — which is the difference between a pseudonym and a bot.
>
> And the rule immediately caught **the seed verifying both founder profiles**. They are the same man, so the platform was asserting he was two verified people, on the deployment that ships as the worked example.
>
> ## Channel 2 — lending the room's profiles your microphone
>
> Green-lit, so screen 81 comes off hold. In a voice room your microphone is carrying your voice to the other people; the profiles are reading text and have no ear. This lends them the watch on your wrist.
>
> **The disclosure is the design, so the disclosure is the screen** — it shows the other participants *by name* seeing the grant. Restoring it from the shelved branch, the text-width guard added since rejected three of its five card strings, which had run off the phone unnoticed where the screen was first drawn.
>
> **The disclosure route was the real find.** Its docstring said "readable by anyone in the room"; the code checked nothing, so "in the room" meant "knows the id" — and a room id rides in beacons and on printed QR stickers, which is what they are for. Anyone who scanned a sticker could read who was wearing a live microphone, on what, and since when. That is a privacy feature inverted. A signed-in stranger is now refused as firmly as an anonymous one.
>
> **Pairing and lending were two vocabularies for one collar clip.** The registry says `lapel_mic`; this module and `jim/mic.py` say `lapel`. Nothing joined them, so you could pair a lapel mic and be told it was an unknown microphone type — from a registry whose own comment says it exists for this feature. Translated rather than renamed, because renaming either side breaks something real.
>
> Plus `GET /microphones/vocabulary`, open, with the refusals published **by name and reason** — a client that knew only the allowed list would grey out a conference puck as though the feature were unfinished, when its absence is the whole argument.
>
> ## The page you make yourself
>
> `markup.py` is a real HTML allowlist — because the version of this that took raw markup is why the Samy worm took MySpace offline in 2005. Script, frames, forms, `on*` handlers and `javascript:`/`data:` URLs are gone, content and all. Sanitised on the way **in**, so exactly one moment of unsafe markup exists rather than one per renderer.
>
> `pages.py` carries themes, a Top 8, the profile's own marketplace listings read live rather than copied, up to twelve links under the same URL rule, and the For You feed inline.
>
> ## The wall, and the feed
>
> `wall.py`. The ranking uses **public actions only** — never memories, source material or anything vaulted, and a test parses the ranking's own SQL to hold that. Every entry says *why* it is in front of you. Popularity is capped so one loud stranger cannot outrank every friend.
>
> `embeds.py` posts video from five platforms. Nothing is copied — the platform, the id, and the title **you** typed. **No request reaches YouTube until somebody presses play.** The URL is rebuilt from the id, so a tracking parameter or `youtube.com.evil.tld` cannot ride along.
>
> `revisions.py` lets people edit and retract what they said, and the correction is what the next turn reasons from.
>
> ## Rooms, and everything full screen
>
> `watchparty.py` — synthetic profiles in the room, and the honest part: **a profile has not seen the video and cannot.** Its context reports `transcript_available: false` and *tells* the profile it has not watched. Starving a model of context and hoping is not a safeguard. The room shares a position, not a player.
>
> Seven surfaces get three full-screen states each — plain, held, sideways. A long press dims to 78% and returns the help button, which is otherwise gone from live surfaces because a floating `?` on a video is a permanent smudge sitting where the share button goes.
>
> ## Work, agreed before it moves
>
> `exchange.py`. What crosses in each direction item by item, what is included at the end and **what is not**. Both sign, and only then does anything move. **Any change voids both signatures** — stored against a hash of the agreement, not its id. Items that *run* are flagged. It grants **no device access**, and that limit is in the code.
>
> `sharing.py` lends a skill inside a room, desk, party, connection or exchange. **Two to open a grant, one to close it** — symmetric consent to start makes it a loan; asymmetric consent to end stops it being a trap.
>
> `wearables.py` pairs watches, bands, earbuds, lapel and clip-on mics at sign-up. **Room-facing microphones are refused at the door** — a smart speaker hears whoever walks in, and they did not pair it, were not asked, and may have a right not to be recorded.
>
> ## What the audit found
>
> All operations exercised with schema-derived bodies: **no 500s**. Algorithms probed at their edges — entity-encoded `javascript:`, a null byte in a scheme, `https://www.youtube.com@evil.tld` — all refused.
>
> What it did find was cost. One 25-item feed ran **584 SQL statements**, because it hydrated every candidate before ranking. Three N+1s: feed 584→6, friends list 41→3, and the feed's tag lookup from one-per-friend to one.
>
> ## Defects fixed on the way
>
> - **Three routers had no authorization at all.** An anonymous stranger could forge both signatures on somebody else's exchange, open its channel, and accept delivery of an executable on their behalf. Fixed with `require_self`/`require_one_of`, and a sweep test asserts no two-party route can be added without a way to identify its caller.
> - **Text ran off the side of the phone** on eight screens. `textwidth.py` is a *measured* advance-width table (`Companion` and `lllllllll` are both nine characters and one is nearly twice as wide), and `audit.py` measures every `<text>` in every file.
> - **`Ring the bell` was drawn below the tab bar** on Live Desks — the button that screen exists for, painted over by an opaque bar.
> - **A failed build corrupted its own output**: `open(..., "w")` truncates before the generator runs, so a raise left a zero-byte SVG. Fixed in all four builders.
> - **Stale SVGs were never pruned** — renumbering left six files still rendering a product that no longer existed.
> - **`/{surface}/{surface_id}/…` was about to ship**, and a two-variable prefix matches any three-segment path. `tests/test_routing.py` asserts it for every route, mutation-checked against a planted shadow.
> - **Nothing tied the README gallery to the screens on disk** — and this round produced the third instance of that class: inserting screen 81 into a full three-wide row pushed **82** off the page. Every file existed and every link resolved, so both existence checks would have passed while the gallery read 79, 80, 81, 83. The numeric run is now asserted too.
> - **`docs/tandem.md` was 92 lines short in PDI** — a file meant to be byte-identical in three repos was identical in two.
>
> ## Everything you present as, on every device
>
> `overlays.py`, `identity.py`, `gamelobby.py`, `displays.py` — wear a character
> over your camera, change what is behind you, hold several profiles with at most
> one badge, sit beside a game without ever being in it, and put a profile on a
> wall panel.
>
> **A live person under a mask is still marked as real.** The first cut refused
> overlays on a live desk, conflating *this face is unmodified* with *a real
> person is here*. Those are different claims and only the second is what the
> badge says: viewers arrived at a named account on purpose, and the name is at
> the top left of every live surface. So the desk keeps `NOT AI · REAL PERSON`
> whatever is worn over it — burned in, tied to the account, and the same mark
> whether the face is bare or covered. A user with facial dysmorphia gets to use
> the product without giving up the badge that says somebody is there.
>
> **A generated background says so and a real face does not have to.** Your own
> photo needs no mark; an AI-made room carries one, because a synthetic
> *background* is synthetic media even when the person is not.
>
> **No synthetic member ever occupies a player slot** — not as a second
> controller, not over Bluetooth, not on a console of its own, and not through a
> capture card, which is the workaround people actually propose: watching the
> screen in order to play *is* playing. Twelve refusals by name, on their own
> screen, because a rule nobody can see is a rule somebody will test.
>
> **Anonymous is a property of the profile, not a label on four surfaces.**
> `Anonymous NNNNNNNN`, fixed and unchangeable, with the account withheld so two
> of somebody's profiles cannot be matched to each other.
>
> ## Three-way coverage, and the audit that forced it
>
> Channel 2 got a watch face because an audit before tagging found the feature was
> phone-only — odd, since **the watch is the device being lent**. Run against
> everything else this round, the same audit found the same hole five more times.
>
> Watch faces **06 Identity, 07 On Camera, 08 Lobby, 09 Screens** are one question
> in five shapes: *what am I currently presenting as?* None of them can change
> anything; face 05 stays the single exception, because a permission you cannot
> revoke from the device running it is not really yours. Desktop views **12–14**
> are the ones a wide window earns — 13 folds overlays, backgrounds and displays
> into one view, because at a desk they are one question rather than three
> modules.
>
> The face↔permission binding test was tightened while it was open: it reads an
> explicit `face="..."` key out of the builder instead of inferring the face from
> a title. The alternative was loosening a regex that could not match "On Camera",
> which would have let a face drawn under any unmatched name pass silently.
>
> ## A guide, a pane, and directions
>
> `tutorial.py` — seventeen steps, seven chapters, in an order that introduces
> nothing before it exists. **The guide has no name and no face**, structurally: a
> tutorial guide with a persona would be the most convincing synthetic profile on
> this platform, met by every user in their first minute, at the exact moment they
> have the least idea what is synthetic here. It never taps anything for you, it
> works with no model configured, and **it cannot quietly fall behind the app** —
> each lesson names its screens and a test binds the set to the gallery in both
> directions.
>
> **Voice and text are one lesson rendered twice.** The assistant delivers it:
> *"show me around"* is not a question with an answer, so the help box starts the
> tour inline rather than handing back a paragraph about tours.
>
> `dock.py` — the watch faces in a pane that tucks into the bottom corner, for the
> people who own neither a watch nor a wall panel. It casts the *same* faces,
> bound by test to `wearables.FACES`. **It shows and it routes; it never acts** —
> the exact inversion of the watch's one exception, because nothing here is the
> device and a control floating over live video is a mis-tap on somebody's
> broadcast. **It is inside every screenshot**, so no message bodies, no memory,
> no agent names, no viewer names, and on a surface being broadcast it opens
> tucked with the preference returned alongside rather than overwritten.
>
> On the desktop it **replaced** something rather than joining it: that corner
> already held a pinned agent-lights panel with no way to close it — three
> quarters of this feature, missing a lid.
>
> And *"where do I change my background"* now gets directions instead of a
> description. `help.DIRECTIONS` is keyed by tutorial lesson, a test asserts every
> lesson is reachable, and the answer names the screen plus the dock face when
> there is one — read from `dock.ROUTES`, so the assistant and the corner cannot
> disagree about where a feature lives.
>
> ## Two more defects of the same kind
>
> - **A screen title's punctuation reached its filename.** "Where Is It?" produced
>   `129-where-is-it?.svg`, where the `?` starts a query string and the README's
>   `<img src>` draws a broken icon. A comma had done it once already. Both came
>   from the slug being written out by hand in **two places that disagreed** — the
>   sweep that deletes stale files and the write that creates them — so the
>   builder now has one `slug()`, and a test asserts no screen file is named
>   something a URL cannot carry.
> - **The desktop avatar was painted over the header pill on every view**, sitting
>   at a hard-coded 96px while `status_dot` sizes itself from its label. It read
>   as a rendering glitch on all eleven views, which is how long it survived: the
>   header is the part of a mockup nobody looks at twice.
>
> ## Membership: Basic $20/month, Pro $130/month
>
> `qrme/tiers.py`, 4 routes, 26 tests, screens 130–135.
>
> | | | |
> | --- | --- | --- |
> | **Visitor** | free | read any public page — a scanned beacon needs no account |
> | **Basic** | $20/month | make your own profiles and your own agent |
> | **Pro** | $130/month | everything that leaves your account: marketplace, connectors, skills, downloads, connections, and every modifier and builder |
>
> **Visitor is a real state, not an oversight.** The whole reach story is a
> stranger scanning a printed code and landing somewhere useful. A wall asking
> them to subscribe before they could read the page would break the feature the
> beacons exist for.
>
> **Enforcement is one table and one chokepoint.** `tiers.gate` is installed once
> as an application-wide dependency, so **no route opts in** and none can be
> forgotten at the eleventh endpoint. The alternative was a `require_plan(...)`
> call at the top of every paid handler — the exact shape this repository has
> been bitten by twice: a docstring claiming a check the code did not make.
>
> **That table is asserted against the served routes, and the first version
> failed.** It named `/steering`, `/governance` and `/licensing` as prefixes.
> None is a route here — steering lives at `/profiles/{id}/steering` — so all
> three were **paywalls in front of a wall**: they read as protection, protected
> nothing, and would have survived indefinitely, because nothing fails when a
> pattern matches no traffic. Patterns now, not prefixes, because most paid
> capabilities hang off a profile and a prefix table cannot say that without
> gating the whole `/profiles` tree.
>
> **Browsing stays open, and that is a decision.** A Basic member may look at the
> marketplace and may not transact on it. A paywall that hides the shop from the
> person you are trying to sell to argues against itself, and the catalogue is
> public to strangers anyway.
>
> **The refusal is structured, because 402 is already spoken here.**
> `POST /packs/{id}/install` answers 402 for *this pack costs money, confirm the
> price*. Both are genuinely payment-required, so the status is right for both —
> but a client must show *upgrade* for one and *confirm* for the other, and
> telling them apart by matching on prose breaks the first time somebody rewords
> a message.
>
> **A membership belongs to the account, not the profile** — per-profile would
> mean paying twice to hold two profiles, which is exactly what `identity.py`
> exists to let people do for free. Creating a profile enrols a new account on
> Basic; an existing member keeps their plan. **Cancelling keeps the profiles.**
> Money is simulated throughout, and a test asserts nothing reaches a processor.
>
> ### Signing up carries the plan
>
> Screens 132–135. The tier work landed the price list and the gate; what it did
> not do was put the choice anywhere in the journey somebody walks. First run was
> 41 → 42 → 43 → 44 → 47 with no plan step in it.
>
> **132 Pick a Plan** is in-flow and deliberately not the same screen as 130 —
> its third card lets you decline and keep looking. **133 Payment** is drawn
> rather than skipped, because a signup flow has one and pretending otherwise
> makes these mockups a worse guide than the product — but it carries the
> simulation pill and a card saying no processor is called, since a convincing
> checkout is the one place here somebody could reasonably be misled about money.
> **134 You're on Basic** names what is *not* included, which is the honest half
> of an upsell. **135 This Needs Pro** renders the structured 402.
>
> Walked end to end against the running app rather than assumed: a visitor reads
> the price list, creating a profile enrols on Basic with six capabilities
> locked, the marketplace returns `{reason: plan, needs: pro, price_usd: 130}`
> with billing disclosed, upgrading opens the same call, and browsing was never
> gated at any point.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code)_

## #155 — Release 0.3.3, and a README that leads with the screens

- merged · opened 2026-07-27 · merged 2026-07-27
- `claude/qrme-0.3.3` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/155>

> Cuts **0.3.3** across the suite, and reorders the README so the screens come first.
>
> ## The README
>
> The page opened with roughly 650 lines of prose and put the screen galleries near the bottom, which is backwards: the screens are the part you can understand at a glance, and the prose is the part you read only if the screens raised a question.
>
> New shape:
>
> 1. **Title and intro** — unchanged
> 2. **The screens** — desktop and mobile galleries, then the portraits and starter collection
> 3. **What it does** — the capability sections
> 4. **Reference** — Architecture, Run, Run it on your phone, Configuration, Test, Example flow, all under one heading at the bottom
>
> The point of the Reference block is that it has an address. If you see a command in one of the screenshots and don't know what it does, it is in one place at the end rather than scattered through the middle.
>
> Those tables are **set smaller**, because they are for looking things up in rather than reading through. Two implementation notes, since neither is obvious:
>
> - GitHub's markdown sanitiser **strips `style`**, so `<sub>` is the only size control actually available. This repo already used it for the gallery captions, so it is known to render.
> - Markdown is **not processed inside an HTML block**, so the converted cells emit their own `<code>`, `<b>` and `<a>` rather than leaving backticks and brackets to show up literally.
>
> ## Release contents
>
> The agent status light — the mapping in `qrme/agentlight.py`, screens 82 and 83, the desktop overlay on every view, and the README section explaining it. Full detail in [CHANGELOG.md](CHANGELOG.md).
>
> Version bumped in all five places (`pyproject.toml`, the `FastAPI(...)` call, `app/package.json`, and both root entries in `app/package-lock.json` — dependency pins left alone), the `[0.3.3]` link definition added, and `[Unreleased]` repointed.
>
> ## What is deliberately not in this release
>
> The held work stays under `[Unreleased]` and is named nowhere in the changelog entry or the release notes. I also checked what GitHub will auto-generate for *What's Changed*: the only PR merged since `app-v0.3.2` is #154, whose title is about the agent light. That is the surface that leaked once before, so it is checked rather than assumed.
>
> ## Verification
>
> - 633 tests pass; both starter generators idempotent under `--check`.
> - The restructure was verified by diffing the prose line-by-line against the previous README: **nothing lost**, the only differences being the version bump and the new Reference intro. The word count *drops*, which is just table pipe characters disappearing into HTML.
> - Every generated table was checked for a uniform column count, and rendered in a browser to confirm it reads as smaller without losing its code spans or links. That check caught a real bug: cells containing an escaped `\|` were being split as if it were a column separator, which invented a column and shifted the rest of the row. Fixed and re-verified.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #154 — Agent status light: watch, app, and an overlay that follows you

- merged · opened 2026-07-27 · merged 2026-07-27
- `claude/qrme-agent-light` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/154>

> One question, answered everywhere: **does this agent need me right now?**
>
> ## The mapping
>
> `qrme/agentlight.py` is the only place the meaning lives. Five workflow statuses collapse to three colours, and each colour carries a word — a colour alone cannot separate an agent that is still going from one that has finished, and those call for opposite reactions.
>
> | status | light | word |
> | --- | --- | --- |
> | `running` | green | working |
> | `completed` | green | done |
> | `awaiting_input` | amber | needs you |
> | `failed` | red | stopped |
> | `cancelled` | red | stopped |
>
> Two properties are structural rather than conventional:
>
> - **Derived, never stored.** The light is attached in `_hydrate()`, the one function every workflow read passes through, so a row cannot be persisted with a light that disagrees with its status. A test asserts no `light` column exists.
> - **Unknown statuses raise.** A new status added later without a light fails loudly instead of quietly defaulting to green — the one wrong answer that would matter.
>
> `GET /agent/lights` returns the legend, built from the mapping rather than restated alongside it. Routes 211 → 212.
>
> ## The three surfaces
>
> They do three different jobs, and that is the point.
>
> - **Watch — face 36 (in JIM).** Three lights, three counts, **no agent names**. Naming them was the first cut and was wrong: a name is something you read, and reading is the thing a glance cannot do. Which agent went amber is a question for the app, where there is room to answer it.
> - **App — screen 82.** The same three lights, each a tappable group. Somebody opening this *because* amber appeared should not have to scan a flat list for the one that changed.
> - **Overlay — screen 83, and every desktop view.** A pinned strip with the counts and a way in. An agent that reports only on its own screen is one you have to remember to check, and amber and red are exactly the states nobody thinks to go looking for. On desktop it rides on every view, because those users have no wrist to glance at.
>
> Screen 81 is left free for the held work.
>
> ## Also
>
> - Screen 65's pills read `WORKING` / `NEEDS YOU` / `STOPPED` instead of naming colours.
> - `agent_groups()` length-guards its subtitles. Two of the three ran under the chevron — visible in a render, invisible in the source — so the next one fails the build instead of arriving as a screenshot weeks later.
>
> ## Verification
>
> 633 tests pass. 9 new ones cover the mapping: every written status has a light, unknown statuses raise, only amber sets `needs_you`, exactly three colours exist, no stored column, and the light follows the status through the API and the listing. The guard was mutation-checked — a 31-character subtitle fails.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #153 — Release prep v0.3.2

- merged · opened 2026-07-27 · merged 2026-07-27
- `claude/qrme-v032` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/153>

> Cuts **v0.3.2** — the starter-card work and the rated starter's grounding.
>
> Neither had a changelog entry. They went to `main` across #151 and #152 and were
> described only in commit messages, which is not where anybody looks.
>
> ## What this release contains
>
> - **The starter gallery shows each profile's own front page.** Screen 80, not a
>   captioned thumbnail: bubble, role, the rating people left, skill chips, Memory
>   / Relationships / Engagement, a career, a review, a Talk-to button. Two columns
>   instead of five, so a phone stops slicing the fourth column mid-word.
> - **Fixed: the rated starter had no source material at all.** The Cabaret &
>   Burlesque Field Pack grounds her in theatre history and stagecraft. Seeding
>   reports `grounded: 34` where it reported 33.
> - **Fixed: a test was asserting that gap into place** —
>   `test_starter_packs_cover_every_industry` compared against `STARTERS` and not
>   `STARTERS + RATED`.
>
> ## What stays under `[Unreleased]`
>
> Channel 2, same as 0.3.1. Its code is on `main`; it is not part of a described
> release.
>
> ## Release mechanics
>
> Version moved in all five places, with the lockfile's two root entries verified
> as exactly two changed lines. Changelog sectioned, link definition added,
> `[Unreleased]` repointed at `app-v0.3.2`. README's current-release line and
> table row updated.
>
> **Tag this commit, not the tip of `main`.**
>
> ## Verification
>
> 624 tests green, 211 routes. No microphone content anywhere in the diff.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #152 — Starter cards: the whole of screen 80, career and reviews included

- merged · opened 2026-07-27 · merged 2026-07-27
- `claude/qrme-starter-cards-v2` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/152>

> Rebuilds the starter gallery cards from **screen 80** — the profile front page a
> visitor actually lands on — instead of screen 5, and carries it all the way
> through rather than stopping at the rating.
>
> ## Each card now has
>
> - avatar bubble with the AI mark burned in
> - name and role
> - **star rating and review count**
> - skill chips
> - **Memory · Relationships · Engagement**
> - **EXPERIENCE** — two posts, employer and dates
> - **REVIEWS** — a name, stars and a line
> - **Talk to …**, with the honorific where the name carries one
>
> ## What is real and what is written
>
> **Real, read out of `qrme/seed.py`:** name, role, portrait, industry, skills.
>
> **Written:** the careers and the reviews. These are invented experts — the first
> line of that README section says so — and a CV is characterisation of exactly
> the kind the bio already is. Each is drawn from that starter's own bio so the
> two cannot contradict each other.
>
> **Sample values, identical on all 34:** rating, reviews count, memory,
> relationships, engagement. A freshly seeded starter has zero of each, checked
> against a real seed rather than assumed. Thirty-four cards all reading *4.0 · 37
> reviews* is self-evidently a template rather than a measurement, and the README
> says so directly under the gallery.
>
> ## Layout
>
> Card height is derived from content — role lines, chip rows and quote lines —
> not a constant plus a nudge. One collision fixed: the experience boxes leave 6px
> and the `REVIEWS` label's cap-height takes 8, so it was sitting inside the box
> above it.
>
> ## Verification
>
> 622 tests green. Both generators idempotent under `--check`. All 34 cards clear
> their content by exactly 16px, checked programmatically across every file rather
> than eyeballed on one. Gallery measures 358px inside a 390px phone viewport with
> no overflow and no broken images.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #151 — Show each starter as the card the app gives it

- merged · opened 2026-07-26 · merged 2026-07-26
- `claude/qrme-starter-cards` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/151>

> The starter gallery was a portrait with a name and an industry captioned under
> it. That is a directory listing, not a profile — the app's own **Profile Home**
> (screen 5) gives a starter an avatar bubble, a role, stat tiles and a Chat
> button. Three published versions failed to fix this because each time the
> portrait was adjusted and never the thing around it.
>
> ## Two defects
>
> **It was five columns wide.** Five 118px thumbnails is ~590px of content and a
> phone offers ~390, so on GitHub mobile the fourth column was sliced mid-word and
> the fifth never appeared. Every starter past the third was unreachable to anyone
> reading on a phone.
>
> **Each cell showed two lines of caption**, where the product shows a card.
>
> ## What this does
>
> Each cell is now the Profile Home card itself, generated per starter into
> `docs/portraits/cards/`. Two columns of whole cards fit a phone — verified by
> rendering the real markup at 390px, not by arithmetic.
>
> **The tiles carry facts, not the mock's numbers.** Screen 5 reads *Memory 247 ·
> Relationships 12 · Engagement 92%*. That is fine for one illustrative mock and
> would be a fabrication repeated 34 times here, because nobody has talked to
> these profiles yet. Each card reports the size of the Field Pack grounding it
> and how many skills it is tagged with — both true. The rated starter has no pack
> (there is no adult-industry Field Pack, deliberately) and its card says `None`
> rather than a zero that would read as a failure.
>
> ## Generated, not hand-written
>
> Two tools, both reading `qrme/seed.py` directly, because the old gallery was a
> second hand-maintained copy of the starter list and could drift from it silently:
>
> | | |
> | --- | --- |
> | `tools/starter_cards.py` | renders the 34 cards; fails loudly on a starter with no role line rather than emitting a blank one |
> | `tools/starter_gallery.py` | rewrites the README between markers; `--check` exits 1 on drift |
>
> Roles are curated rather than regex-extracted from the bios — almost right,
> thirty-four times, is worse than a list somebody read once. They use the app's
> own lower-case phrasing (*"retired fee-only financial planner"*).
>
> ## Verification
>
> 622 tests green. Both generators are idempotent (`--check` clean immediately
> after running). All 34 card references resolve, every row has exactly 2 cells,
> and no `portraits/bubbles` reference remains inside the gallery.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #150 — Renumber this release 0.3.1, not 0.4.0

- merged · opened 2026-07-26 · merged 2026-07-26
- `claude/qrme-renumber-031` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/150>

> The jump was wrong. 0.2.2 went to 0.3.0 and this round went to 0.4.0, which
> walks through the numbers far faster than the work warrants. **The convention
> from here is to stay in the 0.3.x line and only reach 0.4.0 after 0.3.9.**
>
> ## Why this costs nothing
>
> **No `app-v0.4.0` tag was ever pushed**, in any of the three repositories.
> 0.4.0 existed only as strings in files on `main` — nothing was built, no GitHub
> Release was published, and no installer carries the number. This is a text
> change, not a retraction.
>
> ## What moved
>
> - The five version places: `pyproject.toml`, the `FastAPI(...)` call,
>   `app/package.json`, and the two root entries in `app/package-lock.json`
>   (verified as exactly two changed lines; `@malept/flatpak-bundler` and
>   `asynckit` genuinely are at 0.4.0 and are left alone)
> - `CHANGELOG.md` — the section heading and both link definitions
> - `RELEASE_NOTES.md` — title, body, and the tag it tells you to push
> - `README.md` — the current-release line, plus a row for this release in the
>   table
>
> ## Verification
>
> 622 tests green, 211 routes. No microphone content in the diff.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #149 — Release prep v0.4.0

- merged · opened 2026-07-26 · merged 2026-07-26
- `claude/qrme-v040-release` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/149>

> Cuts **v0.4.0** — the starter grounding, the bubble-glow fix, and this round's
> README work.
>
> ## What this release contains
>
> - **Starters arrive knowing something.** All 34 shipped with zero source material
>   while 37 packs sat in the marketplace. Seeding now installs each starter's own
>   industry pack, as part of the repair path so existing deployments catch up by
>   re-running rather than by hand across 34 profiles.
> - **The README says which version you are looking at**, with a release table.
> - **Fixed:** the avatar bubbles had no visible glow — the halo was blurred across
>   most of the margin, so it existed in the source and nowhere a reader would see
>   it.
>
> ## What stays under `[Unreleased]`
>
> The room-microphone entry. Its code is on `main`, but it is not part of a
> described release and these notes must not claim otherwise. `main` being ahead
> of the last tag is the normal state, and recording it that way is more honest
> than either announcing work that is being held or quietly dropping it from a
> section that claims to be complete.
>
> ## Release mechanics
>
> Version moved in all five places: `pyproject.toml`, the `FastAPI(...)` call,
> `app/package.json`, and the **two root entries** in `app/package-lock.json` —
> verified as exactly two changed lines, dependency pins untouched. Changelog
> sectioned, link definition added, `[Unreleased]` repointed at `app-v0.4.0`.
>
> **Do not tag until this is merged**, and tag this commit rather than the tip of
> `main`.
>
> ## Verification
>
> 622 tests green, 211 routes.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #148 — Say what version this is, and what each release actually added

- merged · opened 2026-07-26 · merged 2026-07-26
- `claude/qrme-readme-release-summary` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/148>

> The title said `(v1)` and the only feature section mapped the original PRD
> scope, so a reader could not tell which release they were looking at or what had
> happened since the first one. Thirteen releases of work were described nowhere a
> visitor would find them — the changelog has it all, but the changelog is not
> where somebody lands.
>
> ## What changed
>
> - Title drops `(v1)`; a line at the top names the current release (**v0.3.0**)
>   and the two products cut alongside it.
> - New **What's in the current release** table — thirteen releases, newest first,
>   saying what each one actually added.
> - The old **What's in v1** section keeps its name and position but now says what
>   it is: the PRD conformance map. It answers a different question — which
>   numbered requirement is implemented — not what shipped when.
> - The simulated-money notice moves up with it. Someone deciding whether to trust
>   the marketplace tables should not have to reach `docs/commerce.md` to learn no
>   real funds move.
>
> ## Scope
>
> README only, one file. The table stops at v0.3.0, which is the current release.
>
> ## Verification
>
> Every relative link in the file resolves, and the new table is well-formed
> (13 rows, 2 columns throughout).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #147 — Ground each starter in its own industry pack; fix the bubble glow

- merged · opened 2026-07-26 · merged 2026-07-26
- `claude/qrme-starter-grounding` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/147>

> ## The specialists knew nothing
>
> `qrme/packs.py` has always described its starter packs as *"one free Field Pack per industry, **matching the Starter Collection**"*. **The pairing was never wired.**
>
> All 34 starters shipped with **zero source material** while 37 packs sat in the marketplace. Dr. Sana Iqbal had an environment persona and no environmental knowledge. Diego Fuentes had a construction persona and no construction material. Every one of them answered from tone alone.
>
> Seeding now installs each starter's own industry pack, and it's part of the **repair** path — so deployments seeded before this catch up by re-running, rather than by hand across 34 profiles.
>
> ## Deliberately narrow
>
> Each limit is a way of not overwriting somebody else's decision:
>
> | Rule | Why |
> | --- | --- |
> | **Only the starter's own industry** | `build_system_prompt` renders `sources[:8]`. A profile that hoards material crowds out its own knowledge — one pack is three items, leaving room to grow |
> | **Only onto a profile with nothing** | An owner who added their own material, or removed the pack on purpose, isn't topped up on the next seed. The same blank-only rule the portrait backfill follows |
> | **Free packs only, no ledger credit** | A deployment grounding its own starters isn't a purchase. A priced pack stays a decision for whoever owns the profile |
> | **The rated starter is left alone** | There's no adult-industry Field Pack, and substituting one would put words in the profile the age wall exists to contain |
>
> Verified end to end: Marcus Bell gets the Personal Finance Field Pack, Dr. Sana Iqbal the Climate & Sustainability Field Pack, and both reach the system prompt.
>
> ## Also: the bubble glow was invisible
>
> The avatar bubble shipped in 0.3.0 got the rounded clip right and then blurred the halo across most of the margin — spreading the light so thin it vanished against a dark page. A glow that existed in the source and nowhere a reader would ever see it.
>
> Narrowed the blur and raised the strength so the README gallery matches the Profile Home screen it's meant to mirror. Checked by rendering against the app's own background in both light and dark, which is the only way this is checkable at all.
>
> ## Verification
>
> - **601 tests**, 12 new. Existing 589 unchanged. 209 routes.
> - **Mutation-checked**: installing over existing material, ignoring the industry match, and auto-installing a priced pack each fail the test that forbids them.
> - Worth noting on the third — **it initially survived**. Every seeded Field Pack is free, so removing the price guard changed nothing observable and the guard was real but unexercised. I added a test that prices one before re-running the mutant.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #146 — Release prep v0.3.0

- merged · opened 2026-07-26 · merged 2026-07-26
- `claude/qrme-release-v0.3.0` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/146>

> Cuts **v0.3.0** across all three products. A minor bump rather than a patch — this round added real surface.
>
> ## What's in it
>
> **The round where the tandem reaches a person.** A synthetic specialist could answer a question; now it can be handed a multi-step task, and the person talking to it can be put in front of a real clinician with the release **signed for rather than ticked**.
>
> - **Owner-authorized workflow delegation** (#143) — the workflow routes stay owner-only because a workflow reads vaulted source material unattended and a missing grant means scope `["*"]`. Delegation is a separate surface, off until an owner enables it, and delegating `research` without a grant is refused at write time.
> - **A medical referral, signed for** (#145) — a verified WebAuthn assertion at the `high` tier over the hash of the exact package, bound to that one referral, opening once. Replaces a `consent: true` boolean that was authorising a health conversation leaving the product.
> - **The clinician writes back** (#145) — sealed in the PDI vault, attributed in its own prompt block rather than filed as source material, so the patient doesn't retell everything and the profile doesn't acquire a clinical opinion it can improvise from.
> - **The README gallery renders avatar bubbles** (#144) instead of 34 black boxes.
>
> ## Release mechanics
>
> Version bumped in **all five places** per the checklist:
>
> | | |
> | --- | --- |
> | `pyproject.toml` | ✅ |
> | `FastAPI(...)` in `qrme/api.py` | ✅ |
> | `app/package.json` | ✅ |
> | `app/package-lock.json` top-level | ✅ |
> | `app/package-lock.json` → `packages` → `""` | ✅ |
>
> Dependency versions untouched. `[0.3.0]` link definition added and `[Unreleased]` repointed to `app-v0.3.0` — the step this checklist exists to stop anyone missing.
>
> ## Verification
>
> - **589 tests green**, 40 new this release. **209 routes** (was 197 at 0.2.2). `create_app().version` reads `0.3.0`.
> - All **14** changelog headings checked against their link definitions — 14 for 14.
> - Siblings run in the same pass: jim-mini **346**, pdi **192**.
> - **Nine safety properties are mutation-checked** across this release — each fails the test that forbids it: delegating research without a grant; a delegated caller widening its envelope; an owner's workflow appearing on the delegated routes; a signature raised elsewhere releasing a referral; trusting the stored hash instead of re-hashing; a referral link opening twice; dropping the clinician attribution directive; a clinician writing back repeatedly; one patient's note reaching another's conversation.
>
> ## After merge
>
> The `app-v0.3.0` tag has to be pushed by you — the git proxy here refuses `refs/tags/*`. Body can be left empty or generated; `sync-release-notes.yml` lays `RELEASE_NOTES.md` over the top once the build finishes either way. Watch the case: `app-v0.3.0` lowercase.
>
> Companion PRs: jim-mini `claude/jim-release-v0.3.0`, pdi `claude/pdi-release-v0.3.0`.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #145 — Medical referral: signed for, not consented to — and the clinician writes back

- merged · opened 2026-07-26 · merged 2026-07-26
- `claude/qrme-medical-referral` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/145>

> Reaching a **real clinician** from an AI specialist session, making the release provable, and bringing the answer back so the patient doesn't have to retell it.
>
> ## The thing that was wrong
>
> `POST /handoffs` could already package a session for a real provider. It releases on **`consent: true` — a boolean the client sets.**
>
> Meanwhile `qrme/webauthn.py` opens by describing itself as *"the layer that turns 'the app says the user agreed' into something a third party can check."* The entire signing stack — enrolment, proofing levels, device-bound credentials, envelope challenges, verified evidence packages — has been sitting **one import away** from the single endpoint that ships somebody's health conversation outside the product. A checkbox was authorising it.
>
> ## Going out: signed for
>
> **Signs at the `high` tier.** Document proofing on a device-bound credential — the platform authenticator (Face ID / Touch ID / Optic ID) rather than a passkey that roams. An account without one is *told so*, never quietly dropped to a weaker tier: that would be the checkbox again wearing a signature's name.
>
> **The signature is over the package.** The envelope's challenge *is* the hash of the exact bytes, and `release()` **re-hashes the stored package** at release time.
>
> > Worth flagging: my first draft compared `pkg["document_sha256"]` to the `document_sha256` **column** — two values written in the same breath, which agree no matter what happens to the row afterwards. It proved nothing, and the docstring claiming otherwise was false. The test written for that property caught it. The guarantee exists only because the check now reads the real bytes; the column is kept as a record and the schema says it isn't the check.
>
> **Bound to one referral** (`binding_kind="referral"` — a valid assertion raised elsewhere is not a skeleton key), and **one-time**: the link opens once, and a second attempt says so rather than quietly working, because a replayed link is something the patient should be able to discover.
>
> ## Coming back: caught up, not diagnosed
>
> Opening the link mints a **reply token** at that same moment, so the summary link stays burnt while exactly **one** note can return. Open once, reply once — a channel that needed the summary link kept alive would have traded the handover against the guarantee the patient signed for.
>
> The note is **sealed in the PDI vault** under `qrme/{profile}/clinical/…`: the same treatment source material gets, content in the vault and only a key reference held locally.
>
> **It is deliberately not a `source_items` row**, and that is the decision the rest hangs on. Source material is what a profile recalls *as its own*, and it is what `workflows._scoped_items` feeds to a `research` phase — a clinical opinion filed there could be recited as the profile's own knowledge, or drafted from into a letter. A test asserts it reaches neither.
>
> Instead it arrives in its own prompt block naming the clinician:
>
> > *These are that clinician's words, not yours.* Attribute them by name. You are not a clinician and must never present this as your own assessment, extend it into advice they did not give, or answer a new medical question by reasoning from it — for anything it does not cover, say so and point back to them.
>
> Notes are scoped to **(profile, interactor)**. Another interactor talking to the same profile sees nothing, in the prompt or through the API.
>
> ## Matching
>
> Expertise **filters**, geography only **ranks** — a cardiologist two streets away is not a substitute for a psychiatrist. No match returns nothing rather than a near miss: a confident wrong referral is somebody phoning a clinic that cannot help them. The package names the specialist `synthetic: true` inside itself, since a clinician reading a transcript should never have to work out which voice was a person.
>
> ## Verification
>
> - **573 tests**, 24 new. Existing 549 unchanged. **204 routes** (was 197).
> - **Mutation-checked**, six properties — each fails the test that forbids it: dropping the referral binding; trusting the stored hash; letting the link open twice; dropping the attribution directive; letting the clinician write repeatedly; widening the note query past the interactor.
> - The signing path runs end to end against a real ES256 authenticator double, and the vault path against a PDI double.
>
> Independent of #143 and #144. Companion: jim-mini #97.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #144 — Bake the avatar bubble into the README portraits

- merged · opened 2026-07-26 · merged 2026-07-26
- `claude/qrme-readme-avatar-bubbles` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/144>

> The starter gallery on GitHub renders **34 hard-edged black boxes** where the app shows rounded avatar bubbles.
>
> ## What was actually wrong
>
> The portraits were loading fine. They're square 512×512 **RGB with no alpha** — corner pixel `(7,7,18)`, a near-black backdrop — and the README embeds them raw.
>
> Inside the product a portrait is never shown that way: `face()` in `docs/screens/build.py` puts it in a rounded box over a soft brand glow with a hairline border, **at render time**. The README can't do that, and the obvious fix doesn't survive — GitHub's markdown sanitiser strips the `style` attribute. On a surface QRME doesn't control, the bubble is in the pixels or it doesn't happen.
>
> That's the same reasoning as `tools/mark_portraits.py`, and the same shape: run once offline, commit the result.
>
> ## Two decisions worth stating
>
> **Derived, never in place.** `tools/bubble_portraits.py` writes to `docs/portraits/bubbles/` and leaves the originals alone. `qrme/assets/portraits/` is what the API serves at `/portraits/{handle}.webp` and what the screens read — and the screens draw their *own* bubble, so baking one into the source would nest a bubble inside a bubble on every app screen.
>
> **Alpha, not a background colour.** The corners and glow margin are transparent, so the gallery sits on whatever theme the reader has. A baked-in dark backdrop would be the black box again by another route, and a grey slab in light mode. Rendered and checked in both.
>
> The rounded clip, glow and border are matched to `face()`'s values so the README and the app agree.
>
> ## On the AI mark
>
> `face()`'s docstring says its radius "stays well inside" the burned-in mark. Strictly that's not true — at radius 0.28 the mark pill's outer corner *is* trimmed. I checked by rendering rather than by reading: **the ✦ AI glyph and text stay fully legible**, because the pill has its own rounded corner and what gets clipped is mostly empty fill. The disclosure survives, which is what matters. Flagging it because the wording overstates the margin.
>
> ## Verification
>
> - **565 tests**, 2 new. Existing 563 unchanged.
> - A portrait with no bubble fails; a bubble that lost its alpha fails. That failure is invisible in the repo and sits on the project's front page, so it shouldn't depend on someone noticing.
> - Gallery rendered at GitHub's own page widths in **both light and dark** before shipping.
> - 34 files, 1.6 MB total (~47 KB each).
>
> Independent of #143 — that branch carries the delegation work and doesn't touch these files.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #143 — Owner-authorized workflow delegation

- merged · opened 2026-07-26 · merged 2026-07-26
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/143>

> Lets somebody **other than the owner** start a workflow — how JIM's Guardian hands work to a specialist rather than sending a chat turn.
>
> ## Why not just relax the workflow routes
>
> `qrme/workflows.py` already runs `research → draft → review → send → confirm` in character, carrying memory forward and surviving across sessions. Every route reaching it is `require_owner`. The obvious fix — let an interactor call those routes — is the wrong one.
>
> **A workflow is not a chat turn.** `POST /chat` composes one reply and moderates it. A workflow runs several phases unattended, and its `research` phase reads the profile's **vaulted source material** — where `workflows._scoped_items` treats a missing grant as scope `["*"]`, meaning *all of it*.
>
> A chat turn anyone may start is a considered decision. An unattended multi-phase read over everything the owner ever vaulted, startable by anyone who can reach the endpoint, is not that decision at a larger size — it's a different one.
>
> ## The envelope
>
> Delegation is **off until an owner turns it on**, and turning it on means saying what may be delegated.
>
> | Rule | |
> | --- | --- |
> | No policy → 403 | Absent row, not an empty default. The capability appears only when somebody deliberately asks for it |
> | **A grant is mandatory once `research` is delegable** | Refused at write time (422), where the owner is present to read the error — not at 3am inside somebody else's workflow. This is the one that keeps `["*"]` unreachable down this path |
> | A caller may only ask for a subset | Nobody widens their own envelope |
> | Omitting the plan gets the *owner's* set | Never `DEFAULT_PLAN`, which is every phase there is |
> | Caller must already be in conversation | Checked against `messages`, not `relationships` — those are owner-set, and requiring one would gate every handoff behind an owner action per caller |
>
> `send` **is** delegable, deliberately: the phase produces the finished deliverable, and there is no code path from a workflow phase to an outbound message.
>
> ## The two surfaces never merge
>
> An owner's own workflow has no `delegated_workflows` row, and that absence is the whole guard — it 404s on the delegated routes however the caller authenticates. Only the interactor who started one may read or advance it; the owner can see it, but through the delegated route, not by the two sets of routes converging.
>
> ## New surface
>
> 5 routes (197 → **202**), two new tables (`delegation_policies`, `delegated_workflows` — new tables, not new columns, per the schema convention).
>
> ## Verification
>
> - **563 tests**, 14 new. Existing 549 unchanged.
> - **Mutation-checked** — each of these fails the test that forbids it:
>   - dropping the grant requirement for `research`
>   - letting an omitted plan fall through to `workflows.DEFAULT_PLAN`
>   - exposing an owner's own workflow on the delegated routes
>
> Companion PRs: jim-mini `claude/jim-contribution-preview-and-task-handoff` (the caller), pdi `claude/pdi-tandem-doc-delegated-workflows` (shared doc only).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #142 — Release prep v0.2.2

- merged · opened 2026-07-26 · merged 2026-07-26
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/142>

> Cuts **v0.2.2** across all three products. A documentation release — **no code changed**: no new routes, no schema, no behaviour.
>
> ## What's in it
>
> Everything corrects something that was *described* wrongly, which this round turned out to be the thing costing real time.
>
> - **`POST /marketplace/seed` advertised the opposite of what it does.** It still said *"Idempotent — already-seeded profiles are skipped"* after v0.2.1 taught it to **repair** too. That text is served in the OpenAPI docs, so it pointed away from the one call that fixes a deployment showing bare initials instead of portraits. Corrected in four places — the endpoint, `qrme/seed.py`'s module and `seed()` docstrings, and the README's Starter Collection row. (Shipped in #140.)
>
> - **Three releases of changelog link definitions were missing**, and **the release checklist was why**. `docs/releasing.md` step 1 never mentioned them, so the step was skipped by someone following the instructions correctly; step 2 named two version locations when there are five. (Shipped in #141.)
>
> ## Release mechanics
>
> Version bumped in **exactly five places**, per the checklist this round fixed:
>
> | Location | |
> | --- | --- |
> | `pyproject.toml` | ✅ |
> | `FastAPI(...)` in `qrme/api.py` | ✅ |
> | `app/package.json` | ✅ |
> | `app/package-lock.json` top-level `"version"` | ✅ |
> | `app/package-lock.json` → `packages` → `""` | ✅ |
>
> Dependency versions in the lockfile untouched.
>
> ## Verification
>
> - **549 tests green** — the same 549, passing the same way, which is the point of a release claiming no functional change.
> - **197 routes**, also unchanged. `create_app().version` reads `0.2.2`.
> - All **13** changelog headings checked against their link definitions — 13 for 13, including the new `[0.2.2]`. `[Unreleased]` repointed to `app-v0.2.2`.
> - Siblings run in the same pass: jim-mini **312**, pdi **192**, both unchanged.
>
> ## After merge
>
> The `app-v0.2.2` tag has to be pushed by you — the git proxy here refuses `refs/tags/*` writes. Leave the release body empty when you create it; `sync-release-notes.yml` lays `RELEASE_NOTES.md` over the top once the build finishes.
>
> Companion PRs: jim-mini `claude/jim-release-v0.2.2`, pdi `claude/pdi-release-v0.2.2`.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #141 — Fix the release checklist that lost three sets of changelog links

- merged · opened 2026-07-26 · merged 2026-07-26
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/141>

> Documentation only. No behaviour change — 549 tests pass unchanged.
>
> Follow-up to #140, which repaired the changelog link definitions without touching the reason they went missing.
>
> ## Why three releases in a row lost the same thing
>
> `docs/releasing.md` step 1 said to move the `Unreleased` items under the new heading and date it, and stopped there. It never mentioned the link definition at the bottom of the file — so the step was skipped by somebody following the instructions correctly, three times.
>
> Nothing complains when you miss it. The heading renders fine without a definition, and the damage shows up hundreds of lines away from where the edit was made: a shipped version rendering as literal `[0.2.1]` bracket text, and an `[Unreleased]` link quietly diffing against a tag three releases old.
>
> Step 1 now shows the two lines to add, and says plainly that this is the step that gets missed.
>
> ## Step 2 was wrong in the same direction
>
> It named `pyproject.toml` and `app/package.json`. The version string actually lives in **five** places:
>
> | | |
> | --- | --- |
> | `pyproject.toml` | named already |
> | `app/package.json` | named already |
> | the `FastAPI(...)` call in `qrme/api.py` | **omitted** |
> | `app/package-lock.json` top-level `"version"` | **omitted** |
> | `app/package-lock.json` → `packages` → `""` → `"version"` | **omitted** |
>
> Those three had to be rediscovered every round. The step now names all five and warns off the dependency pins in the lockfile, which look identical to the two that matter.
>
> ## Across the three repos
>
> The same correction goes to jim-mini and pdi, whose link definitions had drifted identically — all three stopped at `0.1.8`. Companion PRs:
>
> - jim-mini — `claude/jim-changelog-release-links`
> - pdi — `claude/pdi-changelog-release-links`
>
> ## Verification
>
> `QRME_STUDIO_DIR=/nonexistent python3 -m pytest -q` → **549 passed**. The sibling suites were run in the same pass: jim-mini **312**, pdi **192**, both unchanged.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #140 — Correct the seed endpoint's idempotency description

- merged · opened 2026-07-26 · merged 2026-07-26
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/140>

> Documentation only. No behaviour change — 549 tests pass unchanged.
>
> ## The problem
>
> `POST /marketplace/seed` still advertised itself as *"Idempotent — already-seeded profiles are skipped"*. Since v0.2.1 that is only half the story: the endpoint also **repairs**, filling a missing portrait or appearance on a starter that already exists.
>
> The stale sentence was load-bearing in the wrong direction. It is the text served in the OpenAPI docs — which is where somebody deciding whether a call is safe to make actually reads — so a person staring at three starters rendering as bare initials would read that line and conclude the one call that fixes them cannot possibly help. Skipping is precisely what they do not want.
>
> ## What changed
>
> The claim was wrong in **four** places, not the one I first spotted:
>
> | Where | Why it matters |
> | --- | --- |
> | `qrme/routers/community.py` — the endpoint docstring | Served in the OpenAPI docs; the one most people read |
> | `qrme/seed.py` — module docstring | What you get from `help(qrme.seed)` and the source |
> | `qrme/seed.py` — `seed()`'s docstring | Did not mention the `repaired` count it now returns |
> | `README.md` — Starter Collection row | The description a new deployment reads first |
>
> All four now say idempotent **and** repairing, note that the repair is blank-only (anything an owner set is left alone), and mention `repaired` alongside `created` and `skipped` in the response.
>
> ## Also fixed
>
> The changelog's link definitions stopped at `0.1.8`. `[0.1.9]`, `[0.2.0]` and `[0.2.1]` had headings but no link definition, so three shipped versions rendered as literal `[0.2.1]` bracket text rather than links to their releases — and `[Unreleased]` still compared against `app-v0.1.8`, presenting a three-release diff as if it were an empty one.
>
> ## Verification
>
> - `QRME_STUDIO_DIR=/nonexistent python3 -m pytest -q` → **549 passed**, the same 549.
> - Rendered the OpenAPI description directly from `create_app().openapi()` to confirm the new text reaches the docs page intact.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #139 — Release prep v0.2.1

- merged · opened 2026-07-26 · merged 2026-07-26
- `claude/qrme-v0.2.1` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/139>

> Version strings in the five places, changelog cut, release notes rewritten. All three products cut together at this version.
>
> ## What this release carries
>
> - **A profile front page** — skills, experience, reviews, rating, in one call. A review requires a real interaction on record and `UNIQUE (profile_id, author_id)` makes a second one from an account impossible in the schema; experience about a real person needs the same rights basis the persona did.
> - **A help box on every screen**, structurally not a synthetic profile — no name, no face, no memory, and it refuses to be one before any model sees the question.
> - **Real portraits** where Profile Home, Avatar Studio and Live Video drew a generic orb, in rounded boxes so the AI mark burned into the top-right corner survives.
> - **Screen 80**, the front page a visitor sees as opposed to the owner's view.
> - **The seed repair** that puts a face back on a starter created before the portraits shipped — the fix for the `MB` / `OM` / `DS` initials.
>
> ## Verification
>
> **549 tests green. 197 routes. 169 SVGs parse**, and all 160 rendered screens carry the help affordance. Both front-ends build clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #138 — Real faces on the screens, and a front page behind them

- merged · opened 2026-07-26 · merged 2026-07-26
- `claude/qrme-portrait-backfill` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/138>

> Three things, all the same complaint: the profiles showed a hologram, and there was nothing behind the face to show anyway.
>
> ## 1. The initials were a bug, not a rendering problem
>
> `MB` / `OM` / `DS` are Marcus Bell, Otis Marsh and Dr. Sana Iqbal — all three ship with real portrait files. Those profiles were created **before** the portraits existed, and nothing could put them back: the seed is idempotent by @handle, and idempotent meant `continue`. So the obvious repair — re-run the seed — was exactly the thing that couldn't work.
>
> It backfills now, **blank-only**, so it's a repair and not a reset. On a live deployment: `POST /marketplace/seed`.
>
> ```
> first run :  created 34, skipped  0, repaired 0
> second run:  created  0, skipped 34, repaired 3   ← the three from the report
> ```
>
> ## 2. The screens drew a hologram where a face belongs
>
> Profile Home, Avatar Studio and Live Video drew `orb()` — a purple sphere with a generic person glyph. **The pixels were already in the repo**: all 34 starter portraits ride in `frames.PORTRAITS`, and exactly one screen used them.
>
> **A rounded box rather than a circle, and not only for taste.** `tools/mark_portraits.py` burns the AI mark into the pixels at the **top-right** — so a circular clip of a square portrait cuts off the corner the disclosure lives in. The radius stays well inside it, so the mark survives into every screen showing a face, which is the whole reason it was burned in rather than composited. Verified by rendering and looking at it.
>
> Those screens now name the character and their profession — *Marcus Bell · retired fee-only financial planner* — both sourced from `seed.py` so the face and the name cannot drift apart. "AI assistant" stays where it belongs: the chrome that genuinely cannot know who is loaded.
>
> ## 3. A profile now has a front page
>
> `qrme/frontpage.py` — skills, experience, reviews, rating, and how many people have actually talked to it, in **one call**, because the caller is a scan page on cellular and five round trips is how a page arrives in pieces.
>
> | | |
> |---|---|
> | `GET /profiles/{id}/front` | the whole page |
> | `PUT /profiles/{id}/experience` | owner-only, replaced wholesale |
> | `GET`/`POST /profiles/{id}/reviews` | one per person, edited not stacked |
>
> **A review comes from somebody who was actually there.** It checks the `engagement` row for a real interaction, and `UNIQUE (profile_id, author_id)` makes a second review from one account impossible *in the schema* rather than in a check somebody could forget. Without both, a rating is worth exactly the number of accounts somebody can make. The average always reports its own `count` — one five-star review and two hundred are different facts.
>
> **Experience about a real person is a credential.** On a `fictional` profile invented history is the point and the AI mark says so. On one depicting somebody real, *"twenty years at Accra General"* is a claim asserted on their behalf, so it's refused without the same rights basis the persona needed.
>
> **Nothing on the page outranks the mark.** A five-star average is a well-liked synthetic profile and nothing more. Reviews are moderated on the way in; a blocked one is kept, shown to its author with the reason, invisible to everyone else, and excluded from the average.
>
> The headline is **derived from the persona** rather than stored — a separate field is a second copy that starts agreeing with it and stops.
>
> ## Verification
>
> **538 tests green (15 new). 195 routes. 167 SVGs parse.** Mutation-checked four ways: restoring the seed's bare `continue`, dropping the "was actually there" check, and dropping the rights-basis check each fail the test that forbids them.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #137 — The assistant has no name any more

- merged · opened 2026-07-26 · merged 2026-07-26
- `claude/qrme-unname-the-assistant` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/137>

> "Ava" was a sample profile name that had quietly become the product's mascot:
>
> | where | said |
> |---|---|
> | studio nav | *Chat with Ava* |
> | chat bubble CSS | `.bubble.ava` |
> | screen gallery | *People in Ava's life*, *Ava wants to reply*, *Talked with Ava* |
> | desktop frames | *Ava · Online*, *Ava · AI Version Me* |
> | demo handle | `@ava.bianchi` |
> | onboarding | `useState("Ava")` |
>
> None of that is true of the product. **A QRME profile is named by whoever creates it**, so hardcoding one name in the chrome told every user their assistant was somebody else's.
>
> The chat screen was already right — it reads `session.profile.display_name`. The name only ever lived in the parts that *could not* know it.
>
> ## Now
>
> Everything that cannot know the name says **AI assistant**, and the message role is `assistant` rather than `ava` — which is what it always was.
>
> **Onboarding no longer pre-fills the name.** A default sitting in the box is the one most people never change, which is exactly how a sample name becomes a mascot. It's empty now, with *"Name your assistant"* as placeholder text.
>
> Screen 6 is `06-chat.svg` rather than `06-chat-with-ava.svg`, and the README gallery follows.
>
> ## Found by rendering, not by reading the diff
>
> The chat screen's online dot sat at a **fixed x that assumed a three-letter name** — so "AI assistant" ran straight through it. The dot and its label are measured off the label now, so a longer name cannot overwrite the status.
>
> Four strings also read badly once the name came out (*"Talked with it"*, *"People in its life"*), and were reworded rather than left as mechanical substitutions.
>
> ## Also
>
> Test fixtures that typed `"Ava"` as a `display_name` are `"Test Profile"` now. The name was perfectly fine as user input — but leaving it made the grep lie.
>
> ## Verification
>
> **523 tests green. 167 SVGs parse. The studio builds clean.**
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #136 — Release prep v0.2.0

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/qrme-v0.2.0` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/136>

> **No functional changes to QRME in this release.** The round was next door, where PDI grew a per-tenant on-call roster. The three products version as one, so this repo cuts the same number in the same pass — `docs/releasing.md` says an empty round says so plainly rather than padding.
>
> ## Why 0.2.0 rather than 0.1.10
>
> The 0.1.x line ran from a profile you could talk to, to a suite where all three products put printed codes on physical things and answer a stranger's phone with a **page rather than JSON** — desk beacons, care beacons, custody beacons, an agent at a facility gate that can speak but cannot decide, a marketplace searchable in words, and an escalation path in each product that reaches an actual human.
>
> That is a different product from 0.1.0. 0.1.10 would have undersold it.
>
> ## What is in here
>
> Version strings in the five places, changelog cut, release notes rewritten — plus the workflow race fix that merged earlier today, which is the only functional change this repo carries into 0.2.0.
>
> ## Verification
>
> **523 tests green** — the same 523, passing the same way, which is rather the point of a release claiming no functional change here. 192 routes. Both front-ends build clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #135 — Only one workflow writes the release body now

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/qrme-release-body-race` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/135>

> Two of them did.
>
> `desktop-release.yml` published the release with `body_path: RELEASE_NOTES.md` — the file **verbatim**, *"Ready-to-paste body for the GitHub Release…"* preamble and all — while `sync-release-notes.yml` published the same file with that preamble stripped. Both fired on the same tag push.
>
> ```
> 20:50:09  both workflows start
> 20:50:15  sync-release-notes  → correct body   ✓
> 20:52:43  desktop-release     → raw file       ✗ overwrites it
> ```
>
> The build always won. Every release since the sync workflow existed has shipped the maintainer preamble at the top of its notes until somebody re-ran the sync by hand — v0.1.9 included, in all three repos.
>
> The de-duplication logic already sitting in the sync workflow — *"several releases carry it twice from a body that was pasted over one that already had it"* — turns out to be scar tissue from this. It was treating the symptom of a race nobody had spotted as a race.
>
> ## Fixed at both ends
>
> **The build stops writing a body.** It attaches installers and lets GitHub generate the changelog. That alone removes the second writer.
>
> **The sync stops racing.** It now triggers on `workflow_run` when the build **completes**, rather than on the tag push, so the curated notes are the last write by construction rather than by luck:
>
> ```yaml
> workflow_run:
>   workflows: ["Desktop release"]
>   types: [completed]
> ```
>
> The tag comes from `workflow_run.head_branch`, and the job is guarded so the manual artifact-only builds — which publish no release — don't trigger a pointless sync.
>
> `types: [completed]` rather than success-only is deliberate: a build that fails *after* creating the release is exactly when a wrong body is least likely to be noticed.
>
> ## Also
>
> [docs/releasing.md](docs/releasing.md) now says to leave the release body empty when tagging, records which workflow owns it, and names the other trap in the same area — tag names are case-sensitive to `tags: ["app-v*"]`, so `App-v0.1.9` silently triggers nothing at all.
>
> ## Verification
>
> Both workflow files parse as YAML, and the `workflows:` name is checked against each repo's actual `name:` — they differ per repo (`Desktop release` / `Guardian release` / `Console release`), which is the kind of thing that would have failed silently.
>
> **523 tests green.**
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #134 — tandem.md: JIM's test count

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/qrme-tandem-counts` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/134>

> One line. `docs/tandem.md` cites each repo's suite size, and JIM's moved from 293 to 297 in [jim-mini#88](https://github.com/davidsbianchi1984/jim-mini/pull/88) — a guard against an unreadable `JIM_SITE_ROTA` taking down its escalation path.
>
> Keeping the three copies byte-identical is the property this file is supposed to have, and letting it drift by one number is how the counts got to *"QRME 59, JIM 49, PDI 20"* in the first place.
>
> No functional change. **523 tests green.**
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #133 — The tandem doc describes the architecture that exists, and v0.1.9

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/qrme-synthetic-profiles-a4t8y9` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/133>

> `docs/tandem.md` is the document every README points a new reader at, and it had drifted in three ways at once.
>
> ## It was missing an arrow
>
> For most of this project's life the topology fit in one sentence: **every arrow points into PDI**, because PDI is the bottom layer and a vault whose availability depends on a model provider is a worse vault.
>
> PDI's gate agent broke that on purpose — it asks a QRME profile for the words it speaks to somebody standing at a facility door. The document, the ASCII diagram and the section headings all still described the world before it. `pdi/qrme_client.py`'s own docstring cites *"every arrow in docs/tandem.md points into PDI"* while being the thing that made it false.
>
> There is a `pdi ✕ qrme` section now: the flow, the fallbacks, and why the model is the voice and not the decider.
>
> ## Two of the three copies were a release behind
>
> JIM's and PDI's still listed the suite gateway's erase, export, consent and metering as `[planned]` when `suite/gateway.py` had shipped them, and the docker-compose e2e harness as planned when it runs in CI. A reader in either repo was told cross-app deletion did not exist.
>
> The three copies are byte-identical again.
>
> ## The numbers were wrong
>
> *"QRME 59, JIM 49, PDI 20 tests"* — against suites of **523, 293 and 177**.
>
> ## New sections
>
> - **The beacon family.** Three products now put a printed code on a physical thing and answer three different questions with it. The shared rules were true in three places and written down in none: a scan is a page and not JSON; a dead code and a code that never existed render identically; the page renders only what the server handed it, so it cannot disclose what the card withheld.
> - **Reaching a human** — the one thing the suite genuinely cannot supply for itself, and the subject of this round's work in the siblings.
>
> ## The diagram is generated
>
> `tools/build_assets.py` writes `docs/diagrams/tandem-flow.svg` from a block identical in all three repos, so one picture cannot become three that disagree. It replaces a hand-drawn SVG that was cream-and-serif while every other asset in every repo is night-indigo — and that showed two arrows, because it was drawn when there were two.
>
> Rendered in a browser and checked for collisions rather than trusted to parse.
>
> ## Also
>
> The Starter Collection row said *33 fictional profiles* while the README, the avatars doc and the generated cover said 34. Both were right — `@vivienne_sable` seeds the rated tier from `RATED` rather than `STARTERS` — and reading them together still looked like a contradiction. Named.
>
> ## Release prep v0.1.9
>
> Version strings in the five places (`pyproject.toml`, the FastAPI app, `app/package.json`, the two root entries in its lockfile), changelog cut, release notes rewritten. All three products cut together at this version, per `docs/releasing.md`.
>
> ## Verification
>
> **523 tests green. 192 routes.** All three `docs/tandem.md` and `docs/diagrams/tandem-flow.svg` verified byte-identical across the three repositories.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #132 — Marketplace search: words, place, and a hand with the words

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/qrme-marketplace-search` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/qrme/pull/132>

> ## Why
>
> Browsing meant knowing the vocabulary — exact `kind`, exact `tag`, exact `area`. Fine if you already know the tag is `legal`; useless if what you have is *"someone who can help me read a lease."*
>
> `qrme/marketplace.py` adds free-text search, a place, saved settings, and an assistant that helps somebody name what they want. 8 routes, 23 tests, [docs/marketplace.md](https://github.com/davidsbianchi1984/qrme/blob/claude/qrme-marketplace-search/docs/marketplace.md).
>
> ## Place is not `area`
>
> `listings.area` was **already taken** and means a *subject* area — healthcare, finance, legal. So geography went into its own table. Folding them together would have made *"near me"* quietly mean *"in healthcare"* — which looks like an empty marketplace and is very hard to see.
>
> **Nothing is sniffed.** No IP geolocation, no GPS, no address parsing. A seller types where they serve; a searcher types where they are. Location a user did not enter is location they did not agree to share.
>
> Localities are **names, not points** — there is no distance maths. That's a real limitation (no "within 10 miles") and also the reason there is nothing to leak. `GET /marketplace/localities` lists what actually exists, so a searcher picks rather than typing a spelling nothing matches and concluding the place is empty.
>
> ## A rated listing can never carry a place
>
> `set_place` **refuses** one — so no row is written, so no place filter can match it, even for a verified adult.
>
> That's [desks.md](https://github.com/davidsbianchi1984/qrme/blob/main/docs/desks.md)'s line — *where a performer physically is has nothing to do with browsing them, and a place filter is a way of asking* — made **structural** rather than a check the next filter to be added could forget. The refusal is loud, because an operator who thinks they've set a location needs to know they haven't.
>
> ## Ranking is deterministic, and says why
>
> Field-weighted (title 6, tags 4, provider 3, blurb 2, area 1), prefix-matched so *nutrition* finds *nutritionist*. Every result carries `score` and `matched_on`; `hidden_by_place` is reported rather than swallowed.
>
> Two callers passing the same arguments get the same order — which is what makes *"why am I seeing this?"* answerable without trusting anybody.
>
> ## The assistant writes the box and stops
>
> `POST /marketplace/assist` turns *"I don't know what to search for"* into two or three candidate searches. It returns **suggestions and never results**, and there is deliberately **no code path from it into `search()`**.
>
> Same boundary as PDI's gate agent: a model can change what is in your search box and nothing else. It cannot filter, reorder, or decide what you're shown — so everyone gets the same explainable ranking. A marketplace where a model silently re-ranks is one where nobody, including the operator, can say why you saw what you saw.
>
> Falls back to keywords from the need itself when no provider is reachable, so nobody is stuck behind an outage.
>
> ## Two bugs worth naming
>
> **Caught by a test, not by reading:** `search_with_prefs` used `setdefault` to apply saved settings — but the route passes *every* query parameter, so an unset one arrives as an explicit `None` and the key already exists. Saved settings were never being applied at all.
>
> **Caught by rendering and looking:** `build.py`'s `button()` fell through to `ghost` for any kind it didn't recognise, so a screen's primary action silently lost its fill. Valid SVG either way, which is exactly why only the generator can catch it — it now raises on an unknown kind.
>
> ## Changes
>
> | | |
> |---|---|
> | `qrme/marketplace.py` | new |
> | `qrme/db.py` | `listing_places`, `marketplace_prefs` |
> | `qrme/routers/community.py`, `qrme/models.py` | 8 routes + schemas |
> | `tests/test_marketplace_search.py` | 23 tests |
> | `docs/screens/` | screens 77–79, + the `button()` guard |
> | `docs/marketplace.md`, `README.md`, `CHANGELOG.md` | |
>
> ## Verification
>
> **523 tests green** (was 500). 192 API paths. 195 SVGs parse; every README image reference resolves. All three new screens rendered to PNG and inspected on both platforms.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

