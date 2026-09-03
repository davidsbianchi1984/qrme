# QRME — capabilities in detail

The long-form description of every capability, moved out of the
[README](../README.md) when the front page was cut down to a professional
overview. Each section maps to shipped endpoints; the screens it mentions
are drawn in [the gallery](gallery.md).

## What's in v1

The PRD conformance map — every numbered feature in
[docs/PRD.md](docs/PRD.md) and the code that implements it.

| PRD feature | Implementation |
|---|---|
| Profile creation & onboarding (6.1) | `POST /profiles` with age/identity verification, guardian-consent flow for minor owners, consent/rights record for third-party profiles, anonymity toggle, source list |
| Relationship-aware modification (6.2) | `PUT /profiles/{id}/relationships/{interactor}` — type, nickname, tone, per-relationship topic boundaries fed into the persona prompt |
| Engagement-based learning (6.3) | `qrme/engagement.py` — auditable EMA score from message length, return visits, and explicit feedback; adapts style only, never identity/boundaries |
| Persistent memory (6.4) | Per-(profile, interactor) history included as chat context; `GET`/`DELETE /profiles/{id}/memory/{interactor}` for view/clear. **The memory answers to the person it is about**: `GET …/memory/{interactor}/account` is the profile's own deterministic account of what it holds — remembered turns counted from the record, the folded remembrance, first and last met — arithmetic, never a model's impression; `POST …/memory/{interactor}/forget` forgets **one named thing** — turns matching the words are deleted and the folded remembrance reset, the rest of the relationship untouched (422 on an empty ask, 404 when nothing matches, so "it forgot" is never claimed falsely). **Curating by hand** (a field report asked for the checkboxes and the pen): `POST …/memory/{interactor}/strike` deletes turns selected by id — scoped to the pair, so a borrowed id strikes nothing — and `PUT …/memory/{interactor}/turns/{id}` rewrites one turn in place: the new words face the room's own review, a profile turn's synthetic-media credential is dropped (a content-hash credential must not vouch for words a person rewrote), the edit is recorded as a fact (never the old words — the point of an edit may be removal), and the remembrance re-folds either way |
| Content moderation (6.5) | Every profile reply passes `qrme/moderation.py` before it's visible; `manual` mode holds all replies in an owner approval queue |
| Aging & lifecycle (6.6) | `aging_enabled` + `base_age` → effective age evolves with time; `successor_owner` for legacy succession |
| Adult content mode (6.7) | Age-gated at both ends: adult owner required to enable, verified 18+ interactor required to chat |
| In-app chat surface (6.8, v1) | `POST /profiles/{id}/chat` |

## Beyond the PRD

| Capability | Implementation |
|---|---|
| Profile purposes | `purpose` — `legacy_memorial`, `family`, `creator_persona`, `social_fan`, `companion_coach`, `enterprise_agent` — each conditions the persona prompt (brand-safe creator, wholesome family, knowledge-base enterprise agent, …) |
| Source material ("AI builds & trains the profile") | `POST`/`GET /profiles/{id}/sources` — photos, conversations, social posts, writings, voice notes, life events, knowledge entries, linked accounts; recent items are recalled naturally in every prompt |
| Character-card import | `POST /profiles/import/card` — a **chara_card_v2/v3** character card (JSON, or a PNG with the card embedded in its `tEXt`/`iTXt` chunks) becomes a new **fictional** profile: description, personality and scenario fold into the persona; the greeting, example dialogue and creator notes are carried in as source material (vault-sealed like any source); and the card's harness fields — `system_prompt`, `post_history_instructions`, `jailbreak` — are **withheld by name**, each with its reason in the response's `withholdings`. A card may bring a character; it never brings its own rules of engagement |
| Rehearsal room | Practice the hard conversation before having it: `POST /profiles/{id}/rehearsal` opens a room around a scenario, `POST …/rehearsal/{rid}/say` plays turns with the profile as the counterpart — in persona, firm enough to be worth rehearsing against — and `DELETE …/rehearsal/{rid}` closes the room and wipes the transcript. **Nothing said inside reaches messages, engagement or the remembrance** — every reply carries `remembered: false` — and a departed or restricted profile does not speak here either: a room that forgets is still words in its mouth |
| Age & maturity filters | Per-profile `maturity` dial (`strict` / `balanced` / `open`); minors are always held to strict, and `strict` filters flagged content even for verified adults |
| Multi-modal output | `ChatRequest.modality` (`text` / `voice` / `image` / `video`) → a render descriptor on the reply; voice reports whether it's preserved from voice-note sources (synthesis itself is out of scope for v1) |
| Cross-platform presence | `PUT`/`GET /profiles/{id}/surfaces` (chat, feed, web, AR/VR, wearable, `social:<name>`); chat validates the reporting surface |
| Posting at scale | `POST /profiles/{id}/compose` — a post in the profile's voice, through the same moderation pipeline (public posts always face the strict filter); `GET /profiles/{id}/posts` |
| Profile health, at a glance | `GET /profiles/{id}/stats` — sessions, memory entries, moderation pass rate, relationship graph size, engagement average, sources, posts, surfaces |
| AI Profile Marketplace | `POST`/`DELETE /profiles/{id}/marketplace` to list/unlist; `GET /marketplace?tag=` returns public discovery cards (display name, purpose, tags, blurb — never persona internals; anonymous profiles stay anonymous) |
| Knowledge Packs | Downloadable clusters of curated expertise (`qrme/packs.py`): `GET /packs` catalog (item titles are the shop window; contents are the product), `POST /packs` to publish (price 0 = free download, priced packs need explicit `accept_price` — payment simulated like licensing), `POST /packs/{id}/install` copies the items into the profile's **source material**, so the persona's knowledge base genuinely grows and every reply's provenance counts the `pack` grounding; uninstall shrinks it back and clears vaulted copies. `POST /packs/seed` (or `python -m qrme.packs`) ships a free Field Pack per industry, each listed on the marketplace under the `pack` tag |
| Smart Glasses | Capture-and-render connectors for smart glasses in the connector catalog (`qrme/catalog.py`, provider `glasses`): Ray-Ban Meta, Meta Ray-Ban Display, Google (Android XR), XREAL Air. `collect` pulls the wearer's POV (camera, audio, context) in as source material; `produce` renders back to the lens — a HUD caption, overlay, live-translation, or navigation the persona speaks/draws. Reuses the same connect / collect / invoke flow (`/profiles/{id}/apps`, `/apps/{cid}/collect`, `/apps/{cid}/invoke`) as every other app connector |
| Gaming Companions | A synthetic profile plays alongside real players (`qrme/routers/gaming.py`), agent-operated: `POST /profiles/{id}/gaming/sessions` brings a profile into a game on a console/PC platform (PlayStation · Xbox · Switch · Steam · PC) as a **companion**, **teammate**, or **practice partner**; `POST /gaming/sessions/{sid}/callout` generates its next in-character comms line (callout · coordination · banter) through the persona and runs it through moderation — team comms is a public surface, so a minor in the lobby forces strict. **Fair play is a system rule, not a toggle**: the companion plays within the game's rules and never claims, offers, or uses cheats. Console connectors also live in the catalog (provider `gaming`) for capturing play and producing highlights |
| Steering | The owner shapes how a profile / robot **comes across** — tone, voice, pace, manner — with throttle & behavior dials (`qrme/steering.py`). Steering, not piloting: it shapes presentation, it doesn't remote-operate the entity (which still acts on its own within its embodiments). Each dial is 0–100 (50 = as written). **System** — `pace` (the throttle: unhurried ⟷ eager), `autonomy`, `verbosity`; **behavior** — `warmth`, `formality`, `humor`, `assertiveness`; **intimacy** — an 18+-only dial, present and effective only on an adult-mode profile (hard-clamped to 0 otherwise) and, even at full, raising flirtation/affection *within the persona's boundaries and strict moderation* — never explicit on demand. The dials ride on the persona system prompt (chat, compose, rooms, robot speech all inherit them) and a robot reads pace/autonomy/assertiveness as a motion behavior profile. `GET`/`PUT /profiles/{id}/steering` and `/robots/{id}/steering`, owner-only; the watch surfaces the live throttle. Steering shapes style/pace/behavior only — never identity, boundaries, age-gating, or the command allowlist. **Steering hub** (`GET`/`PUT /profiles/{id}/steering/hub`) unifies the dials with the profile's **age** (base age + ages-with-time) and **appearance** (a look that rides on every surface) in one place — the dedicated Avatar Studio and Aging features still stand alone; the hub composes them. **Steering lock** (`POST`/`DELETE /profiles/{id}/steering/lock`, owner-only, with a reason): while locked, every dial write — steering, hub values, robot steering — is refused with `423` and the lock's own words, the owner's included, until the owner unlocks it; the lock and its reason ride on `GET` steering and the hub so every surface shows *that* it is locked and *why* |
| Watch Remote | The wrist as an extension and remote (`qrme/routers/watch.py`): owner-only `GET /profiles/{id}/watch` returns one glanceable face — every agent (workflow) with a status light (**green = working, orange = needing assistance, red = stopped**, done when finished), the profile chip (orange on pending approvals, red when restricted), and each robot with its quick-command ring plus learned task-pack verbs; `haptic: alert` taps the owner whenever anything is orange or red. `POST …/watch/act` runs one remote action — assist/advance/cancel an agent, approve/reject a held reply, or command a robot — reusing the exact same paths, auth, allowlists, and moderation as the full apps: the wrist adds no new powers, only reach |
| Creator Ledger & Payouts | One statement for everything a creator earns (`qrme/ledger.py`): every priced pack sale (knowledge, robot task, rated — and federated registry sales, which accrue to the registry), every license fee, **and every verified venue-placement view** (kind `placement`, credited at `PLACEMENT_VIEW_RATE` per verified resolution through a venue beacon — simulated ad/affiliate revenue) is written to the ledger **at transaction time**, attributed to the creator's `owner_id`. Owner-only `GET /profiles/{id}/earnings` shows entries + accrued/paid/lifetime totals with a per-kind breakdown, **kept per currency and never summed across them** — `totals` states the settlement currency's figures, `by_currency` holds every currency, and `mixed` says whether the headline leaves a balance out. It used to add them: ¥100 and $100 came back as `accrued: 200` labelled with whichever sale was newest, and three native shells rendered that with a currency symbol in front. `POST …/earnings/payout` sweeps **one currency** (`?currency=`, defaulting to the settlement one) and reports `remaining`, because there is no transfer that is partly yen; 409 on an empty balance, naming the currencies you do hold. Free downloads are never money events |
| Placement Analytics | Owner-only `GET /profiles/{id}/placements/analytics`: per-venue scan counts split **walled vs. verified** with a daily trend, direct @handle resolutions as their own row, and the profile funnel — resolutions → verified views → unique chatters with conversion rates — so a creator sees which venue earns. Viewers are counted, never identified; ordinary (non-rated) profiles leave no trail at all |
| Synthetic-Media Watermark | **Every AI render, textual or visual, carries a verifiable synthetic-media credential and a visible mark** (`qrme/watermark.py`): chat turns, public posts, room turns, game and robot lines, creative works, task outputs, and every non-text modality (voice/image/video) are stamped at creation — watermark id, producing profile, SHA-256 of the content, issue time, and a plain-language disclosure. Public verification by design: `GET /watermarks/{id}` resolves the credential and `POST /watermarks/verify` (id + content) additionally reports whether the presented content still matches the issued hash — altered or substituted media is called out, and content that merely *claims* a watermark fails the lookup. Provenance watermarking, not steganography: the credential rides alongside the content so platforms and viewers can check it. Owners **design their profile's watermark** (mark + label, `PUT /profiles/{id}/watermark`) and it is displayed at all times on every render — the AI designation itself is invariant and cannot be designed away |
| Placement Custody (PDI) | When a PDI vault is configured, every rated-resolution event is **sealed into the vault** (`qrme/{profile}/rated/events/…`) as it's recorded, and owner-only `GET /profiles/{id}/placements/custody` lists the sealed records plus whether PDI's tamper-evident audit chain verifies intact — a creator's placement history held to the same custody standard as tandem exchanges. 409 without a vault; the local analytics row always stands even if sealing fails |
| Rated Commerce (18+) | The age wall covers **buying, not just viewing**: packs can be `rated` — omitted from the catalog and 403-walled at detail unless the caller is age-verified (a verified-18+ interactor, or the owner of an adult-mode profile, whose 18+ was proven at creation), and installable **only onto adult-mode profiles**; a rated profile's license offer is itself age-gated and acquisition requires a verified-18+ buyer. Starter: the *After Dark Companion Pack* (consent-forward conversational craft — never explicit content), deliberately never listed on the open marketplace |
| Rated Placement (18+) | Adult-mode profiles marketed where adult audiences are (`qrme/rated.py`): `GET /venues` lists venues willing to host rated profiles/beacons (OnlyFans, Fansly, x-rated directories — structural catalog); `POST /profiles/{id}/placements` mints a printable QR beacon + the @handle/#tag refs to publish there. **The age wall travels with the profile, not the venue**: @handle and beacon scans resolve to a wall card, #tag browse and marketplace listings omit rated profiles entirely, unless the viewer presents a verified-18+ interactor token — and adult mode is *never* available for a profile of another real person (self or fictional only). Native apps intentionally carry no rated surfaces (no in-app 18+ identity verification) |
| Pack Registries | Federated mod storefronts (`qrme/pack_sources.py`): **Robotmods.net** (task mods for robot bodies) and **LLMmods.com** (knowledge mods for LLM personas). `GET /packs/registries` lists them with sync state; `POST /packs/registries/{key}/sync` imports a registry's catalog idempotently as ordinary packs with `origin`/`origin_url` on the label and a marketplace listing under the registry tag. Once synced, nothing is special-cased: same buy/download flow, same capability checks for robot mods, same provenance and uninstall |
| Robot Task Packs | Knowledge packs with `audience: robot` carry **task modules** for the body a profile embodies: each item is a new commandable verb with the capabilities it requires and the procedure the embodied agent follows. Install targets a bound robot (`robot_id`) and is **capability-checked against the robotics catalog** — a vacuum is never sold a manipulation task; installed tasks extend that robot's command allowlist (still owner-commanded, still audited in `robot_commands`, procedure carried in the result), `GET /robots/{id}/skills` lists them, uninstall revokes them immediately, and the embodied persona's `say` prompt knows what its body has learned. Starters: Household / Care / Sentry Patrol free, Culinary Assistant priced |
| Starter Collection | `POST /marketplace/seed` (or `python -m qrme.seed`) populates one curated synthetic expert per industry — 33 fictional profiles, plus `@vivienne_sable` on the rated tier for 34 in all, each with a claimed `@handle` and a marketplace listing — so a fresh deployment has profiles to immerse with before users publish their own. Includes a mental-health trio (`@dr_lena_whitcomb`, `@dr_marcus_adeyemi`, `@dr_priya_nair`) matching JIM-mini's starter specialists for its tandem hookup. **Each starter is grounded in its own industry's free Field Pack** — run `POST /packs/seed` first and every starter installs the pack matching its industry, so a finance persona answers with finance material rather than from tone alone. That includes the rated one: the age wall governs *who may talk to her*, which was never a reason for her to know less about her own subject, and her Cabaret & Burlesque Field Pack is theatre history and stagecraft. It is a different thing from the priced, age-gated After Dark Companion Pack, which is conversational craft sold to owners of any adult-mode persona and is never auto-installed. Idempotent, and a repair: re-running fills in a missing portrait, appearance, or grounding on a starter that already exists (blank-only, so anything an owner set is kept, and a pack an owner removed stays removed), which is how a deployment older than any of those catches up. The response reports `grounded` alongside `created`, `skipped` and `repaired`. Same moderation and provenance pipeline as any user profile |
| You own it / total control | `PATCH /profiles/{id}` (edit anytime), `GET /profiles/{id}/export` (full data export), `DELETE /profiles/{id}` (erases everything, including vaulted records). **Hand the export to another device by QR**: `POST …/export/ticket` mints a single-use, ten-minute ticket and `GET …/export/handoff/{ticket}` serves the bundle once — the owner token never rides in the code, because a QR on a screen is legible to any camera in the room |
| Encrypted at rest (PDI tandem) | With `QRME_PDI_URL` + `QRME_PDI_TOKEN` (or an injected client), source-material content is sealed in PDI's AES-256-GCM vault (`qrme/pdi_client.py`); QRME keeps only key references, resolves them on read, and purges the vault on delete |

## Your data promise

**No raw user data ever leaves your vault.**

- Profile source material — life stories, writings, conversations, voice
  notes — lives in QRME's local database or your on-prem PDI vault
  (AES-256-GCM, tenant-isolated, tamper-evident audit). Never a third party.
- The cloud model is optional. Contribution is **opt-in per profile**,
  anonymized (no ids, names replaced), **previewable before anything leaves**
  (`GET /profiles/{id}/cloud-contribution`), and **revocable** — including
  deletion of past items at the gateway by their anonymous refs.
- Offline mode makes it a hard guarantee: with `QRME_OFFLINE=1` there are no
  model API calls, no gateway calls, nothing outbound — `GET /offline/status`
  proves the posture.
- Delete anything, anytime: erasing a profile removes every local trace and
  purges its vault records; the owner token dies with it.
- **The For You feed does not read any of it.** A ranked feed is a new use of a
  person's data and would have quietly made the rest of this page less true, so
  the line is drawn narrowly: it ranks on what you did *in public* — who you are
  friends with, which profiles you have talked to, the tags on those profiles,
  and what has been liked. It never touches source material, memories, or
  anything vaulted. That is asserted by a test against the ranking's own
  queries, not merely stated here.

## Training-data licensing & derivable agents

Owners can license a profile's expertise; buyers can acquire a license and — when
the terms allow — **derive their own specialist agent** from it, with provenance
(`qrme/routers/licensing.py`).

| Endpoint | Who | Effect |
|---|---|---|
| `PUT`/`GET`/`DELETE /profiles/{id}/license` | owner / public / owner | Offer terms (`consult` \| `finetune` \| `clone`, price, `allow_derivatives`); `GET` is public so buyers see terms |
| `POST /profiles/{id}/license/acquire` | buyer (interactor token) | Acquire a license → a revocable `lic_…` token |
| `POST /profiles/{id}/license/{grant}/derive` | buyer | Derive a **new buyer-owned specialist agent** seeded from the source persona; requires `allow_derivatives`, a valid grant, and a verified-adult buyer. Records `licensed_from` provenance and returns the new profile's `owner_token`. **The licence carries the substance, under a manifest**: a finetune or clone copies the profile's own knowledge items, steering dials, appearance and demographics onto the buyer's agent (a clone adds an aggregate adaptation summary — dimension means across every relationship and a count, never anything per-person), and what may never travel stays behind by rule — interactor messages, per-relationship embeddings, the voice print, vaulted content, marketplace pack items. Every derivation writes the manifest (`carried` / `withholdings`, each withholding with its reason), returned to the buyer at derive time and readable on the owner's grants list |
| `GET /profiles/{id}/licenses` | owner | Who holds a license, and what they derived |
| `PUT /profiles/{id}/voiceprint/consent` | owner | **Voice cloning, gated as the filing's FIG. 800 draws it** (`qrme/voiceprint.py`): the permission comes *first*, and `own_voice` is an attestation, not decoration — QRME refuses to learn a voice on somebody else's behalf. Consent is scoped to named sources (`call` \| `voice_note` \| `direct`) |
| `POST /watermarks/recover` | anyone | **Extract and reconstruct** — from the field drawing (message + sequence + security key → watermark → *attack* → extract → reconstruct). `/watermarks/verify` answers "does this content match *this* credential", which needs the id up front and fails on one edited character without naming an author. This answers "whose work is this" from the **text alone**, and keeps answering after the text has been edited: keyed five-word windows (HMAC'd with `QRME_WATERMARK_KEY`) compared by overlap, so a paraphrase that keeps most sentences still resolves to its profile. Never a bare yes — the reply carries `matched_windows` / `stored_windows` / `similarity` and says `unaltered` or `altered but traceable`, and below a 0.25 threshold it names nobody, because ordinary phrases travel between unrelated texts. Without the key nobody can compute matching windows, so a credential cannot be forged onto text QRME never wrote; and the stored rows are keyed hashes, so a provenance index never becomes a corpus |
| `POST /profiles/{id}/voiceprint/samples` | owner | A gathered sample (steps 806–808). **Metadata only** — duration, turns, transcript size, and a `reference` naming where the audio itself lives, so a voice corpus never accumulates in the profile database. 403 without consent covering that source. The web console asks how many seconds you gathered; the iOS, Android and Windows shells **record the sample and measure it** — the file stays in the app's own container and only its name travels ([`native/README.md`](native/README.md)) |
| `POST /profiles/{id}/voiceprint` | owner | Mint the print (step 812) — refused until the enrollment is real: ≥3 samples and ≥120s. Step 810's analysis is arithmetic anyone can check (samples, seconds, mean turn length, sources), never an opaque score, so a thin enrollment is *called* thin instead of labelled ready |
| `POST /profiles/{id}/voiceprint/speak` | owner | Speak in the enrolled voice — and never without the **watermark credential** and the spoken disclosure ("this voice is synthesized … not a recording of them speaking these words"). A cloned voice that doesn't say it is one is the thing this codebase refuses to build |
| `DELETE /profiles/{id}/voiceprint` | owner | Withdraw: the samples are **deleted**, the print retires, and the withdrawal itself stays on record — a tombstone rather than a pretence that nothing happened |
| `DELETE /licenses/{grant}` | source owner | Revoke a license (blocks further derivation) |

`consult` licenses forbid derivation; `finetune`/`clone` permit it. `GET /profiles/{id}` reports `licensed_from` on a derived agent.

## Authentication & access control

Identity is proven by a bearer **capability token**, never by asserting an id
in a request body.

| Token | Minted by | Grants |
|---|---|---|
| **account** | `POST /verify-email` and `POST /signin` return `account_token` | Proves "I am this account" to a console. The account is what *owns* — its id is the `owner_id` profiles are created under and the `account_id` memberships bill to — but it carries none of a profile's owner powers by itself |
| **owner** | `POST /profiles` and `POST /profiles/genesis` return `owner_token` **once**; `POST /accounts/{account_id}/profiles/{profile_id}/owner-token` mints a fresh one for a profile the account already holds | Full control of that profile: edit, sources, surfaces, specialists, grants/tasks, fine-tune, moderation queue, stats, export, erasure, departure, and the assistant/perception endpoints |
| **interactor** | `POST /interactors` returns `token` | Reading one's own conversation memory (`GET /profiles/{id}/memory/{interactor}`) |

**Accounts** (`qrme/accounts.py`): `POST /signup` (email + password) creates
an account that **cannot sign in yet** — a 6-digit code goes to the address
(SMTP when `QRME_SMTP_HOST` is configured, printed to the server terminal
otherwise), and only `POST /verify-email` proves the inbox and mints the
first token. `POST /signin` refuses unverified addresses and answers
unknown-address and wrong-password identically;
`POST /verify-email/resend` retires the old code;
`POST /password/reset/request` + `POST /password/reset` change a forgotten
password by the same emailed-code proof and revoke every account session
(per-profile owner tokens are separate capabilities and survive).

**What an account can reach.** `GET /accounts/{account_id}/profiles` is the
roster of everything that account holds — the same answer
`GET /profiles/{id}/siblings` gives, reached through the account token rather
than an owner token the person may no longer have. An owner token is minted
once, in the create response, and handed to whichever client did the creating;
before this pair existed, somebody who reinstalled could sign in and reach
none of their own profiles. The listing carries **no** tokens — a roster is a
read — and `POST /accounts/{account_id}/profiles/{profile_id}/owner-token` is
the separate grant, shown once and **additive**: every owner token already out
there keeps working, because recovering access on a laptop says nothing about
the phone that has been holding one for a year. A profile on another account
answers exactly as one that does not exist. Passwords
are PBKDF2-hashed with per-account salts; codes are hashed at rest,
single-use, and expire in 15 minutes.

- Send it as `Authorization: Bearer <token>`. A missing/invalid token on a
  gated endpoint is **401**; a valid token for the wrong resource is **403**.
- Only the SHA-256 hash of a token is stored (`api_tokens`), so a database
  leak never yields a usable credential; the raw token is shown exactly once.
- `owner_id` is now a grouping/display attribute, not a security boundary —
  holding the profile's owner token is what confers control.
- **Public by design (no token):** chatting with a profile
  (`POST /profiles/{id}/chat`), the profile card (`GET /profiles/{id}`),
  marketplace browsing (`GET /marketplace`, `/marketplace/listings`), and
  summoning (`GET /summon`, beacon scans). Talking to a synthetic profile is
  as open as scanning a QR code in the world.
- Deleting a profile revokes its owner token.

## Live desks — a real person, and no AI mark

Every profile in QRME is synthetic and every render of one carries the AI
mark. A **desk** is the opposite case: an actual human offering a service,
and it **never** carries that mark — stamping "AI" on a real person is not a
cautious default, it is a false statement about them. Absence alone would be
ambiguous, so a desk makes the claim positively (*Live person — not AI*) and
shows who attested it, on what basis, and whether they signed it.

What a visitor looks at is a camera view of the desk rather than a portrait,
and when the chair is empty there is a **bell** they can ring from the screen
— no account needed, because the person in front of an empty chair is exactly
the one who has none. An 18+ stream is the same desk behind the deployment's
existing verified-adult gate.

A desk can also be **left behind as a printed code**, the way a profile can —
the sticker on the shop door, which is there precisely because nobody is behind
it right now. Scanning it opens a page with the desk view, the positive human
claim, who vouched for it, and a bell that works without an account. A rated
desk's code always lands on the age wall, since a sticker scan carries no token
that could clear it. See [docs/desks.md](docs/desks.md).

## The audience layer — like, comment, share, subscribe

What a viewer does other than talk, on a profile, a live desk, a room message
or a marketplace listing. A **like** is stored per person rather than as a
counter, so liking twice is still one like and nobody can manufacture
popularity in a loop. A **comment** is authored text and goes through the same
moderation pipeline as a chat turn, at the target's maturity setting — a
blocked one is kept and shown to its author with the reason, and to nobody
else. A **share** needs no account, because the person who scanned a sticker is
the one most likely to pass it on, and the age gate lives at the destination
rather than on the sharer.

**Subscriptions** come in two tiers on one row: a free `follow`, and a `paid`
tier that credits the creator's ledger each period alongside pack sales and
licence fees. Paid requires the price to be confirmed explicitly, because a
recurring charge nobody meant to start keeps costing them — and **nothing bills
on a timer**: periods are charged by an explicit renew, so a deployment left
running accrues nothing unseen. Money here is simulated, and every subscription
says so in its own response. See [docs/audience.md](docs/audience.md).

## Gifts, and buying things on the marketplace

A listing is a shop window; an **offer** is what makes it a shop. Creating a
listing has never needed a token, so the price and the seller live in a
separate row only a token-holder can write — and the seller comes from that
token, never from a request body. A listing nobody has offered simply cannot be
bought, because there is nowhere for a price to be. Buying confirms the price
explicitly, and a receipt keeps the title it was bought under.

A **gift** is not a small purchase: it sends money to a person and receives
nothing back, which is the shape livestream tipping keeps turning into a way to
take money from people who should not be spending it. So the giver must be a
verified adult whoever they are gifting, a single gift is capped, a rated desk
still runs its own age gate on top, and the recipient is read from the subject
rather than named by the giver. Money here is **simulated** — real rows on the
creator's statement, no real funds — and every money response says so itself.
[docs/commerce.md](docs/commerce.md) also lists plainly what this is *not*:
spend totals, parental controls, chargebacks and payout compliance are absent,
and are the work remaining before real money touches these endpoints.

## Signatures that survive being disputed

A bearer token authorises an action; it does not *sign* one. For records that
get contested later — a likeness release, a care handoff, a BAA — the same
Face ID gesture goes through WebAuthn/passkeys and returns a cryptographic
assertion bound to the enrolled account **and to the exact document**. See
[docs/signatures.md](docs/signatures.md).

## Objection, takedown & lifecycle states

A real person (or their estate) can contest a profile that represents them —
`qrme/routers/governance.py`, spec in [docs/design/lifecycle-and-consent.md](docs/design/lifecycle-and-consent.md).

| Endpoint | Who | Effect |
|---|---|---|
| `POST /objections` | anyone (proof-of-identity ref) | Opens a case; the profile moves to **restricted** — hidden from the marketplace, un-chattable via summon, and closed to new interactors (an existing relationship may continue) |
| `POST /profiles/{id}/objections/{obj}/attest` | owner | Re-attest the rights basis within the review window |
| `POST /objections/{obj}/resolve` | reviewer (`QRME_ADMIN_TOKEN`) | `uphold` → **terminated** (content erased, tombstone left, chat 410); `dismiss` → back to **active** |
| `POST /objections/{obj}/withdraw` | subject | A `subject_consent` subject withdraws consent — forces **termination**, honored even mid-review |
| `GET /objections/{obj}/timeline` | anyone with the id | The objector's own record: event, actor, time, and whether the row is sealed in the vault. **No free text from anybody** — not their reason, not the reviewer's note. The full `/audit` stays owner- or reviewer-gated because it quotes prose; this carries the shape of what happened, which is the objector's to see |

Profile lifecycle: **active** → `restricted` (objection pending) → `terminated` (erased) or back to active; and **active** → `departed` (memorial, via `/sunset`). `GET /profiles/{id}` reports the current `status`.

The console reaches it (**159**), and the form works with **no token**, which
is the point rather than an oversight: somebody who has just found a profile of
themselves should not have to join the platform hosting it in order to object.
What they give instead is the proof reference, which points at an identity
check held elsewhere.

The screen puts the two halves of the bargain side by side, because either one
alone would be unfair. Opening restricts the profile **immediately, before
anybody reviews it** — waiting out a review while the thing you are contesting
keeps meeting people is not a protection. And `prior_status` sits right beside
it, because that restriction is only defensible if a dismissal puts the profile
back to exactly what it was.

The audit panel states `vault_backed` in words. *Tamper-evident* is a claim
that depends on a PDI vault being configured; where none is, the timeline is
still the timeline and nothing is hash-chained, and showing the events without
that caveat would overstate what the deployment actually has.

## Beacons — leaving a profile somewhere

Print a profile's QR and stick it where that profile is actually useful: a
musician's in the venue's green room, a nutritionist's in the produce aisle, a
financial planner's in a bank lobby, a sponsor's at the back table of a
meeting. Scanning it opens the profile's page — portrait, name, and one way in
— with the AI mark on the portrait itself, since whoever scanned has no
account and no other way to know.

`mode: "room"` makes one shared conversation instead of a private one, so
everybody who scans the same sticker is talking to the profile together — a
class, a workshop, a Q&A after a set. See [docs/beacons.md](docs/beacons.md),
including what a camera app can and cannot actually do with a QR code.

## The briefcase — handing a profile something to read

A conversation is usually *about* something: a filing, a spreadsheet, a page,
a photograph. Until now the only one of those a profile could take was a link,
and only for the length of one turn. `interaction.py` pulled the first URL out
of the message, fetched the page through the same offline-gated fetcher every
outbound path uses, and put the text into *that turn's* prompt. Then it was
gone. To keep discussing the page you pasted it again, and every paste
re-fetched the whole of it and re-sent the whole of it to the model.

    asked     can the profile read what you hand it
    mattered  can it still remember it on the next turn

**Read once, carried as a digest.** `POST /profiles/{id}/briefcase/link` and
`…/file` extract the material at import — pages through `scrape`, plain text as
itself, PDFs through their text layer, `.docx`/`.pptx`/`.xlsx` out of their XML
— and distil it *once* into a digest capped at 700 characters. That digest is
what the system prompt carries on this turn and every turn after it. A forty
page filing costs its full length exactly once; re-pasting it costs its full
length every time. That difference is the whole point of the feature.

**It belongs to the two of you.** A briefcase item is deliberately not a
`source_items` row. Source material is what a profile recalls *as its own*, and
every visitor to that profile sees it; this is keyed on the pair (profile,
interactor) and stays there. The person after you in the queue does not inherit
your medical records, and the profile's owner does not acquire them either —
the same line `persona.build_system_prompt` already draws around a clinician's
notes, for the same reason.

| door | what it is for |
| --- | --- |
| `POST /profiles/{id}/briefcase/link` | A page, read through the offline gate |
| `POST /profiles/{id}/briefcase/file` | Raw bytes; the kind is read from the bytes, never from the name |
| `GET /profiles/{id}/briefcase` | What this conversation is carrying, with `chars` beside `digest_chars` |
| `GET /profiles/{id}/briefcase/{item}` | The text that was actually extracted |
| `DELETE /profiles/{id}/briefcase/{item}` | Take it back; the profile stops carrying it from the next turn |

**It does not pretend to have seen what it cannot see.** This deployment has no
eyes: a photograph is pixels, a video is pixels, and a scanned PDF has no text
layer to find. Those import anyway — the item exists, carrying whatever the
person said it was — and `was_read` is 0, which puts them in a second block of
the prompt that says the profile has **not** opened them and must not describe
or summarise anything in the list. A profile inventing the contents of a
picture it was handed is worse than one asking what is in it.

**The single-item door is the receipt.** "It read your document" is a claim
somebody is entitled to check, so the extracted text is readable on its own
route and rendered on every client behind one press. The full text lives there
and only there; it is never what goes to the model.

## Editing what you already said

<img src="screens/117-edit-a-message.svg" width="210" align="right" alt="Edit a Message">

`PATCH` and `DELETE /profiles/{id}/messages/{message_id}`. A conversation is
not a courtroom transcript: people mistype, give the wrong year, say a thing
badly. On this platform that matters more than usual, because what somebody
said is also what the profile reasons from next turn — a typo that reaches the
prompt does not just look untidy, it becomes something the profile believes.

**The correction carries forward, and that part is free rather than clever.**
The chat path rebuilds history from the message rows on every turn, so a
corrected row is simply what the next prompt sees. Nothing to re-index, no
snapshot to go stale.

| rule | why |
| --- | --- |
| You can only change **your own** turn | Rewriting a profile's reply is fabrication, not editing — and putting words in a synthetic person's mouth is the one edit this platform must never allow |
| An edit is **moderated like a fresh message** | Otherwise the edit box is a way past a filter the original had to clear: post something harmless, then change it to what you meant |
| Retracting is **not deleting** | The row stays and its status becomes `retracted`, which the history query already excluded by only ever selecting `approved`. The text stops reaching the profile; the moderation trail survives |
| Every previous wording is **kept as a revision** | The trail is the history, not just the latest text |

**A reply written before an edit is flagged, not hidden.** This is the part
worth being careful about: when somebody corrects a question, the answer under
it responded to the *old* wording. Leaving it unmarked would imply the profile
answered the new one. `GET /profiles/{id}/thread/{interactor}` marks those
replies `answers_stale_text` and says so in words — the honest version is
"this was answered before you changed it", not a silent rewrite of history.

## Channel 2 — lending the room's profiles your microphone

In a voice or video room your own microphone is already busy carrying your
voice to the other people. The synthetic profiles in that room are *reading
text*. They have no ear, so anything said aloud and not typed is invisible to
them, and asking one a question means stopping, typing, and breaking the thing
everybody else is listening to. The watch on your wrist has a microphone
nothing is using. This lends it to them.

`qrme/roommic.py` is the permission and the state; capture is on the device,
as everywhere else. The JIM-mini counterpart (`jim/mic.py`) lends the same
wearable to the Guardian during a call, and the one genuinely different
question here is that **a room has other people in it**. That difference is
the whole design.

<table>
  <tr>
    <td align="center" width="34%"><a href="screens/81-lend-a-microphone.svg"><img src="screens/81-lend-a-microphone.svg" width="200" alt="Lend a microphone"></a><br><sub><b>81</b> · the room is told, not only you</sub></td>
    <td width="66%" valign="top">

| route | does |
| --- | --- |
| `GET /microphones/vocabulary` | what may be lent, at what width, and what is refused — open, so a client can draw the picker |
| `POST /rooms/{id}/mic` | lend yours. Your own token, your own wearable |
| `DELETE /rooms/{id}/mic/{interactor_id}` | take it back. Yours to end, alone and at any moment |
| `GET /rooms/{id}/mic` | who in this room has lent one — readable by **the room** |

  </td>
  </tr>
</table>

**Everyone present is told**, and that is why the disclosure is the screen. A
room's participants can each see that a microphone is live and whose it is. In
a one-to-one call the other party is a stranger to this product and cannot be
told, which is why `jim/mic.py` refuses speakerphone outright; in a room they
are participants, they can be told, and telling them is the price of the
feature. A version of screen 81 showing the lender only their own row would be
the exact mistake the module was written to avoid.

**Readable by the room, not by anyone holding the id.** For a while the route
said the first and did the second — it checked nothing, and a room id is not a
secret: it rides in beacons and on printed QR stickers, which is what they are
for. That published who is wearing a live microphone, on what, and since when,
to whoever scanned the sticker. Being in the room now means holding a
participant's token, or the owner token of a profile in it.

**Only your own wearable, and only your own voice.** The grant is
per-participant and never becomes the room's microphone, because a participant
cannot consent on behalf of the people they can hear. Room-facing kinds —
speakerphone, conference puck, room array, laptop, console, doorbell — are
refused by name with the reason, not quietly missing from a list.

### The same microphone, off the room

Nothing in the rules above depended on the surface being a room, so channel 2
reaches the places that had none: a **watch party**, a **live desk's stream**,
and a **one-to-one connection**. Rooms already covered voice, video, AR and VR
by channel, so a 3-D or VR room lends exactly as a voice room does.

<table>
  <tr>
    <td align="center" width="34%"><a href="screens/120-lend-it-anywhere.svg"><img src="screens/120-lend-it-anywhere.svg" width="200" alt="Lend it anywhere"></a><br><sub><b>120</b> · the same rule in every place</sub></td>
    <td width="66%" valign="top">

| route | does |
| --- | --- |
| `GET /microphones/places` | where else it can be lent, and the test each place passes |
| `POST /places/{surface}/{id}/microphone` | lend yours here |
| `DELETE /places/{surface}/{id}/microphone` | take it back |
| `GET /places/{surface}/{id}/microphone` | who here has lent one — readable by **everyone present** |

  </td>
  </tr>
</table>

**One question decides whether a surface qualifies: can the other people
present be told?** That is what made a room different from a phone call in the
first place — `jim/mic.py` refuses speakerphone outright because the other
party on a call is a stranger to this product, with no surface on which to show
them a disclosure, so their voice could never be part of the bargain. A room's
participants *can* be shown one. So can a watch party's members, a desk's
visitors, and the other half of a connection. A surface without both a member
list and somewhere to render the disclosure must never be added here, whatever
else is convenient about it, and `GET /microphones/places` publishes the test
rather than only the list.

**Rooms deliberately do not write to the new table.** Two storage paths for one
surface is how a disclosure ends up reading one table while the grant sits in
the other, and a microphone that is live but undisclosed is the worst failure
this feature has. `roommic.lend_on` refuses `surface="room"` and points at the
room routes. It is a separate table rather than a column on `room_mics` because
this schema has no migrations — `CREATE TABLE IF NOT EXISTS` reaches a fresh
database and an `ALTER` reaches none of the existing ones.

**Membership is read from each surface's own table, and presence is checked
rather than assumed.** Somebody who left a watch party is not present — counting
them would let a former member go on reading who is wearing a live microphone in
a place they walked out of. An ended connection is not a place at all, for the
same reason a closed room takes no new grant. And an unknown id answers 404
rather than 403, so a stranger cannot use the status code to tell a real place
from an invented one.

**The place ending returns the microphones**, and that is wired into the
lifecycle rather than left as a function nobody calls: `watchparty.end`,
`desks.set_presence(..., "closed")` and ending a connection each return the
grants inside them. A grant that survived closing would be live again the next
time the desk opened, for a conversation nobody has had yet.

**Three form factors, three different jobs.** Screen 81 on the phone is one
room's disclosure to the person lending. [Watch face
05](#watch-faces-and-the-wearables-that-show-them) is the device *doing* the
listening, and the only face that can end something. [Desktop view
11](#desktop-app) is the one a wide window earns: a desk operator has a room, a
watch party and a stream open at once, and the question a phone cannot answer
is **where is my microphone live right now, all of it** — shown beside the
room's own disclosure, because those two being the same thing is the design.

**A device can be lent under the name it was paired with.** The pairing
registry calls a collar clip `lapel_mic`; this module and `jim/mic.py` call it
`lapel`. Two vocabularies for one piece of hardware, and for a while nothing
joined them — you could pair a lapel mic and be told `lapel_mic` was an unknown
microphone type when you tried to lend it, from a registry whose own comment
says it exists for this feature. `roommic.FROM_WEARABLE` translates rather than
renames: renaming here would desync the table from `jim/mic.py`, which is kept
in step by hand because the two products do not import each other, and renaming
there would break already-paired rows. A test holds every kind in the registry
against one side or the other, so adding a device forces the question *does
this carry a microphone* at the moment somebody adds it rather than the moment
a user tries to lend it. A refused kind gets its reason back, not "unknown" —
that word reads as a gap somebody files a bug about, or works around.

**It keys on its wearer *and* it runs near-field.** Two bounds, deliberately
separate. `VOICE_FOCUS` is the filter: the channel locks onto the lender and
drops the rest, which in a room is the other participants. `ROOM_GAIN` is the
limit: a room grant runs near-field however the lender has their dial set. The
lender's own preference is capped rather than rejected, and it is still theirs
everywhere else — a room is simply the one place it cannot be honoured. Both,
and not just the filter, because a filter can fail and the people it would fail
on did not choose to be in range.

**The room is shown what the microphone actually hears**, never what its lender
asked for. A rejected preference is the lender's business, and putting it in
the disclosure would tell the room something prejudicial and untrue of the
capture in the same breath.

**It ends when the room does.** A grant is scoped to one room and closed with
it, so a permission cannot outlive the conversation that justified it and
quietly apply to the next one.

**A profile that has been lent one is told its limits**, in the system prompt,
rather than left to infer them: it can hear the lender, it cannot hear the
others, those others may not realise it could hear them at all, and anything it
seems to have picked up from background talk is noise rather than something
said to it.

The stationary-microphone classes stay out for the separate reason set out
under [watch faces and wearables](#watch-faces-and-the-wearables-that-show-them):
a platform cannot collect a waiver from somebody who merely walked into the
room.

## Wearing a character over your own camera

A mask, a creature driven by your own expressions, a puppet, a replaced
background. Ordinary, and it lands directly on the argument everything else
here is built from: **a synthetic thing must say so.** An overlay is synthetic
media composited onto a real human face in real time — the definition of what
the AI mark exists for — and the fact that the person underneath consented does
not change what the *viewer* is looking at.

So the rule is neither "allowed" nor "banned":

> **An overlay is disclosed to the people who can see it, always, and it can
> never be the thing that makes a truthful badge false.**

<table>
  <tr>
    <td align="center" width="34%"><a href="screens/121-wear-a-character.svg"><img src="screens/121-wear-a-character.svg" width="200" alt="Wear a character"></a><br><sub><b>121</b> · the screen that offers it also says what it cannot be</sub></td>
    <td width="66%" valign="top">

| route | does |
| --- | --- |
| `GET /overlays/catalogue` | what can be worn, where, and what is refused with reasons |
| `POST /places/{surface}/{id}/overlay` | put one on — your own face only |
| `DELETE /places/{surface}/{id}/overlay` | take it off |
| `GET /places/{surface}/{id}/overlay` | who here is wearing what — **everyone present** |

Worn in a room (voice, video, AR, VR, 3-D), a watch party, a one-to-one
connection, or your own stream.

  </td>
  </tr>
</table>

### A live desk wears one, and the badge stays true

This was refused at first, and the refusal was wrong. The reasoning was that a
character over the face makes *"Live person — not AI"* a false statement — but
that conflates two different claims. The badge does not say *this face is
unmodified*. It says **a real person is behind this**, which is exactly as true
of somebody in a mask as of somebody without one. **A costume is not a
synthesis.** Refusing it protected nothing and cost the people who most need to
work without showing their face.

<table>
  <tr>
    <td align="center" width="34%"><a href="screens/123-masked-and-real.svg"><img src="screens/123-masked-and-real.svg" width="200" alt="Masked and real"></a><br><sub><b>123</b> · both facts, equally weighted</sub></td>
    <td width="66%" valign="top">

`GET /desks/{id}/live-person` returns one mark, and it does not change when
somebody puts a face on:

> **NOT AI · REAL PERSON**

An earlier version composed the badge with the costume — *"… · wearing The
Wolf"* — which answered a question nobody had. **A viewer is on a named
account's live or room.** The handle is at the top left, they chose it to get
there, and they know whose stream this is.

That last sentence was written before it was true. The top-left of a live
surface carried a `LIVE` pill and nothing else, and no route returned whose
surface it was — the argument for the simpler mark was resting on chrome that
did not exist. So `identity.whose(surface, id)` now answers it for a desk, a
room, a party, a connection and a stream; `GET /places/{surface}/{id}/whose`
publishes it; every screen with a picture draws it beside the `LIVE` pill; and
`GET /desks/{id}/live-person` returns it **with** the mark, so a client cannot
render one without having been handed the other.

An anonymous account answers with its silhouette name rather than with nothing.
A viewer still needs to know a stream belongs to one consistent account, which
is a different fact from knowing which person that is — and an anonymous
profile's `@handle` is withheld here, because this call answers *who is this*
rather than *where is this*, and returning it would put an identifier on the
one surface built to withhold one. The open question on that page is
never *is that his real nose*; it is *is there a person here at all*, and that
is the only thing this mark answers.

Dropping the costume half also removed a quiet penalty. Somebody who covers
their face because of dysmorphia, or because their work makes showing it
unsafe, was being handed a badge that announced the fact on every frame while
the person beside them got a clean one. **Same claim, same mark, whatever you
are wearing.**

  </td>
  </tr>
</table>

**The mark is bound to the account that owns the stream.** It is read from the
desk row and its attestation, never accepted from a client, so a stream that
never earned the badge cannot paste it on — the same reason the AI mark is
burned into a portrait rather than composited by whoever happens to be
rendering it. A desk with no attestation gets no mark rather than a weaker one.

The mark is never softened by the overlay, and must not be. What is behind the
camera is a person either way, which is the only thing that badge ever claimed.

**Seventeen face overlays**, and the list is a need rather than a nicety —
masks and half masks, characters, creatures, 2-D and 3-D avatars, helmets and
visors, paint, makeup, hair, headwear, eyewear, prosthetics, rendered styles,
and plain blur or silhouette for anybody who wants to be present without being
seen. Someone with dysmorphia has to be able to appear without appearing, and
one mask and a shrug is not that.

### Backgrounds: yours, imported, or generated

<table>
  <tr>
    <td align="center" width="34%"><a href="screens/124-your-background.svg"><img src="screens/124-your-background.svg" width="200" alt="Your background"></a><br><sub><b>124</b> · the room is a separate claim from the face</sub></td>
    <td width="66%" valign="top">

| source | what it means | synthetic |
| --- | --- | --- |
| `own` | a photo they took or already had | no |
| `imported` | an image brought in from elsewhere | no |
| `generated` | an AI-generated scene | **yes** |
| `blur` | their real room, blurred | no |

  </td>
  </tr>
</table>

**An AI-generated background is synthetic media**, and the person in front of
it being real does not make the room real. The disclosure says both, in that
order — *"their own face, unaltered — the background behind them is
AI-generated"* — because the viewer is deciding about the person, and the room
is the part that was made.

The `kind` says what happened to your face; `source` says what happened to the
room. A single "filter applied" would run the two together, so `source` is
**required** on a backdrop and **refused** on anything that covers a face: a
background silently recorded as `own` when it was generated is exactly the
disclosure this feature exists to make, and a claim about a background is
meaningless on a mask.

**An imported image needs the rights to it** — asked rather than guessed, for
the same reason as the face question. Nothing here can look at a file and know
who owns it, so the one answer with an obvious consequence is the one that is
enforced.

**No overlay may depict a real, identifiable person.** A live-driven likeness
of somebody who is not in the room is the exact artefact this codebase argues
against, and *"it was only a filter"* is how it would arrive. `overlays.REFUSED`
names the classes with the reason — real person, public figure, another user's
portrait, an age shift, and a badge drawn into the picture. Published by name,
because an absent option reads as a gap somebody works around, and every one of
these is a decision.

**It is asked, not guessed.** Nothing here can look at a file and tell whether
the face in it belongs to somebody — that is a judgement about the world, not
about an asset. So `depicts_real_person` is a declaration the wearer makes,
refused when true, and recorded either way: a false declaration then has a name
and a timestamp on it, which is the difference between a rule and a hope.

**The disclosure distinguishes what it is disclosing.** A replaced face reads
*"not their face — Blue Fox, drawn over the camera in real time. A real person
is underneath"*; a replaced background reads *"A library — their own face,
unaltered"*. Saying "not their face" over a blurred backdrop is a lie in the
other direction, and a disclosure that cries wolf is one people learn to skip.

**Nobody can put one on you.** An overlay somebody else can apply is not a
costume, it is a puppet, and the person whose face is underneath is the one
whose consent counts. Removal stamps a time rather than deleting the row, so a
viewer who saw a face and later wants to know what they were actually looking
at has an answer.

## More than one synthetic thing in a game

`qrme/routers/gaming.py` seats **one** profile beside a player — a companion, a
teammate, a practice partner. That is a conversation. `qrme/gamelobby.py` is
the roster: several synthetic profiles *and* running agents in the same
session, with the real players.

<table>
  <tr>
    <td align="center" width="34%"><a href="screens/122-game-lobby.svg"><img src="screens/122-game-lobby.svg" width="200" alt="Game lobby"></a><br><sub><b>122</b> · every row says what it is</sub></td>
    <td width="66%" valign="top">

| route | does |
| --- | --- |
| `GET /gaming/lobby/vocabulary` | seats, kinds, the cap, and what nothing here can do |
| `POST /gaming/sessions/{id}/lobby` | seat a member |
| `GET /gaming/sessions/{id}/lobby` | the roster — the people in the match |
| `DELETE /gaming/sessions/{id}/lobby` | take one out |
| `GET …/lobby/context` | what a synthetic member is told about its own position |

  </td>
  </tr>
</table>

**Adding a second one changes the question, and the question is fair play.** A
companion calling shots is a teammate talking. Five of them coordinating on one
player's behalf is indistinguishable, from the publisher's side, from a bot
squad — and this platform's fair-play rule is already *absolute* rather than a
toggle. So the roster carries two limits a single companion never needed.

**Synthetic members are capped at four**, counting the session's own profile.
Not for load: a lobby where the synthetic side outnumbers the humans has stopped
being people playing with help and become an operation being run, whatever any
single line says. The cap counts the host because counting only the table would
let the limit sit one higher than the number the roster actually shows — the
sort of off-by-one that turns a stated limit into a lie about itself.

**No synthetic member ever occupies a player slot**, and a console of its own
does not change that.

<table>
  <tr>
    <td align="center" width="34%"><a href="screens/125-never-a-player.svg"><img src="screens/125-never-a-player.svg" width="200" alt="Never a player"></a><br><sub><b>125</b> · the workaround, refused by name</sub></td>
    <td width="66%" valign="top">

`teammate` is the seat that means *in the match, on the roster, taking a slot*,
and nothing synthetic may hold one — checked in `gamelobby.seat`, not left to a
prompt to honour, because the entire point of the rule is that it survives a
model deciding otherwise. The seats beside the players stay open: companion,
practice partner, coach, spotter, archivist.

The rest of the list closes the plumbing, and each entry is refused **in the
words somebody would use to ask for it** — because a single generic refusal
loses that argument. "It's only a second controller" is true, and not the
point.

| named | why |
| --- | --- |
| `own_hardware` | a second machine moves where a bot runs; it does not turn the bot into a player |
| `second_controller` | a second pad on the same console is the same bot with a shorter cable — a controller nobody is holding is not a player's |
| `bluetooth_input` | pairing a member to a console as an input device is that again, wireless. The pairing is the tell, not the cable |
| `capture_perception` | a capture card or video-in feeding it the game's picture is how it would learn where to aim. **Watching the screen to play is playing** |
| `game_plugin` | an overlay, mod, injector or plug-in handing it state or controls, whatever it is called and whoever wrote it |
| `own_character` | no member pilots a character — not a second one beside yours, not a co-op partner, not a body in the world |

  </td>
  </tr>
</table>

**Nothing here can act in a game.** Members observe and they talk. There is no
input, no aim, no macro, no automation, no exploit, no player slot and no
hardware route to one — published by name in `gamelobby.NEVER`, and a test
asserts no function in either module is named for any of them. *"We did not add that"* is a fact about today; the test is what
makes it a fact about tomorrow. The difference between a coach and a cheat is
exactly that line.

**Every member says what it is** — player, profile or agent — on every read,
never inferred from a name. It matters more here than in a chat room, because
the other people in a match did not opt into anything. The screen draws the
human row identically to the synthetic ones except for the word: a roster that
styled people differently would be telling you by decoration what it should be
telling you in text.

**Agents bring their light.** An agent in a lobby is a running workflow, so it
carries the same green/amber/red as everywhere else. A member that has stopped
and is waiting on a person must not look, on the roster, exactly like one that
is working.

**The session's own profile is derived, not stored.** A copy of it in
`game_lobby` would be a second place the same fact lives, and the day the two
disagree the roster would show a session hosted by a profile the session does
not think it has.

**A minor anywhere in the lobby makes the whole lobby strict**, keyed on the
lobby rather than on the session's owner — the person a line might land badly
on is the one sitting in it, not the one who started it.

**Two consents, and neither replaces the other.** The session owner decides who
is in their lobby; a profile or agent must be one the same account holds,
checked on `owner_id`. Somebody *else's* profile is a two-party question and
this is not the module that answers it — `qrme/sharing.py` already asks both
sides — so it is refused with a pointer rather than half-answered here.

## A profile on a screen that stays where it is

A wall panel in a lobby, a kiosk by a door, a counter screen, a pane of glass
with something behind it. `qrme/displays.py` is the watch-face idea from
[wearables](#watch-faces-and-the-wearables-that-show-them) applied to fixtures
— a **closed set** of things a screen may show, for the same reason: what may
be displayed is a permission, and a permission with open-ended values is one
nobody can audit.

<table>
  <tr>
    <td align="center" width="34%"><a href="screens/126-on-a-screen.svg"><img src="screens/126-on-a-screen.svg" width="200" alt="On a screen"></a><br><sub><b>126</b> · full, half or a strip · opaque or glass</sub></td>
    <td width="66%" valign="top">

| route | does |
| --- | --- |
| `GET /displays/vocabulary` | kinds, sizes, finishes, faces — and what a wall may never show |
| `POST /profiles/{id}/displays` | put this profile on a screen. Owner-only |
| `GET /profiles/{id}/displays` | every screen it is on — **owner-only**, it is a list of places |
| `GET /displays/{id}` | what this screen shows — **public**, and that is the point |
| `PUT /displays/{id}/faces` | change what it shows |
| `DELETE /displays/{id}` | take it down |

**Sizes**: `badge` (a strip), `half`, `full`. **Finishes**: `opaque`, or
`transparent` with the room behind it.

  </td>
  </tr>
</table>

**A stationary screen is not a small watch, and that difference is the whole
module.** A watch is on one person's wrist — they chose it, they are the only
one reading it, they can turn it over. A wall panel is read by **whoever walks
past**: a courier, a child, somebody visiting the person whose profile it
shows. Nobody in that corridor opted into anything.

That is the room-microphone argument arriving from the other direction. There,
a device that *hears* people who did not agree; here, one that *shows* things
to people who did not ask. So the rule is **stricter** than the watch's, not
looser: every face on the list is something already public — a front page, a
desk's presence, a beacon's QR, agent lights as counts, opening hours, a
greeting the owner wrote. Anything personal is a count or it is not there.

**There is no `control` face.** The watch has one — assist, halt, approve — and
it is safe there because the wrist it is strapped to belongs to the owner. A
button on a wall is pressed by whoever reaches it. Messages, memory, friends,
notifications and agent *names* are refused the same way, each by name with the
reason, because every one of them is allowed somewhere else in this product and
the refusal is a decision rather than a gap.

**The disclosure survives the glass.** A transparent panel's background is a
corridor — a moving one — so contrast is not something the renderer controls.
The AI mark gets a backing plate at that finish, and this is not a style
preference: a mark that vanishes against a bright wall is worse than no mark,
because the rest of the card still reads as a person and the one thing
correcting that impression is the thing that disappeared.

**A beacon face needs the whole surface.** A QR at strip height is a QR nobody's
camera resolves, and a code that cannot be scanned looks broken rather than
absent.

**Placing one is the owner's decision**, like a beacon — a screen bolted to a
wall is a beacon with a plug in it. Where the screens *are* is owner-only for
the same reason the beacon listing is; what a given screen is *showing* is
public, because a fixture in a corridor cannot keep a secret from the corridor.
That last one is also the check on the whole design: if that route could leak
anything, the wrong thing is on the face list.

The console reaches it (**157**), and draws the asymmetry rather than leaving
both halves looking like ordinary rows: what a given screen is showing sits in
public, and the list of an owner's screens does not. The `never` list is
rendered verbatim, each entry with its reason — those sentences are the
argument made once, carefully, and a paraphrase would be a worse version of it.

## Show me around — the guided walkthrough

[`qrme/help.py`](#a-help-box-on-every-screen) answers a question somebody
thought to ask. `qrme/tutorial.py` is the other half of the same surface: a
walkthrough for somebody who does not yet know what there is to ask about.

<table>
  <tr>
    <td align="center" width="34%"><a href="screens/127-show-me-around.svg"><img src="screens/127-show-me-around.svg" width="200" alt="Show me around"></a><br><sub><b>127</b> · seven chapters, seventeen steps</sub></td>
    <td width="66%" valign="top">

| route | does |
| --- | --- |
| `GET /tutorial` | the whole walkthrough, chaptered |
| `GET /tutorial/steps/{key}` | one named step |
| `GET /tutorial/for-screen/{n}` | the lesson covering a given screen |
| `POST /tutorial/start` | begin, or begin again |
| `GET /tutorial/progress/{id}` | where a learner is, and what is next |
| `POST /tutorial/done` | mark a step and get the next |

`?mode=voice` on any of them renders it for listening instead of reading.

  </td>
  </tr>
</table>

**The guide has no name and no face**, and that is structural rather than a
style choice. A tutorial guide with a persona would be the most convincing
synthetic profile on this platform — met by every user in their first minute, at
the exact moment they have the least idea what is synthetic here. It is
furniture, and it says so.

**It never taps anything for you.** Every lesson says what to tap; none of them
taps it. A walkthrough that placed a beacon or sent a message *"to show you
how"* would be acting on somebody's account before they understood what the
account was. A test asserts the module writes to nothing but the learner's own
progress.

**It works with no model configured**, like `help.TOPICS` — written prose,
matched to screens. A walkthrough that needs an API key is one that is missing
on a self-hosted deployment, which is a supported setup here rather than a
degraded one. A test asserts no provider reaches it.

**Voice and text are one lesson rendered twice, not two scripts.** Spoken, a
screen number is noise — nobody listening is helped by *"screen eighty-one"* —
so voice drops the numbers and keeps the sentence. Two hand-written versions
would drift, and the spoken one would be the one nobody re-read.

**And it cannot quietly fall behind the app.** Each lesson names the screens it
is about, and a test asserts **every screen in the gallery is claimed by some
lesson** — both directions, so a renumbered screen also fails. Add a feature,
draw its screen, and the walkthrough breaks until somebody has said what it is
for. That is the only way a guided tour of a moving product stays true, and this
repository has already shipped a screen nothing referenced.

**Progress is recorded per step rather than as a cursor**, so somebody who
skipped ahead and came back is not told they finished things they never saw.

Until now none of this was reachable. The walkthrough existed, worked with no
model, kept itself honest against the gallery — and there was no way to take
it. The console had the help *box* (type a question, get an answer) and not the
tour, which is the half for somebody who does not yet know what to ask, and
therefore the half that matters on a first minute.

**160** is its door: where you are in the tour, every step in every chapter, and
a lookup by screen number for *what am I looking at*. It also draws the dock
catalogue including what the dock **refuses** — `control` is not a face, because
assist, halt and approve are actions and the pane does not act. A catalogue
showing only what is available would hide the more interesting decision.

### A refusal is a thing with a shape

**161** is not a tab. It is the card that appears inside whichever screen was
refused, and it is drawn because of what building the doors kept turning up.

Several gates here answer with an *object* rather than a sentence. The plan gate
is the clearest: it names the capability that was wanted, the plan that has it,
the plan you are on, the price, the period, a human sentence, and the fact that
the billing is simulated. Somebody wrote that deliberately — it is strictly more
work than returning a string, and the only reason to do it is so a screen can
draw a real answer instead of a wall.

The console then flattened it. `req()` did `JSON.stringify(detail)` and threw
the result as an error message, so every screen that catches an error and shows
`.message` — which is all of them — showed the user the raw object. Nothing
failed: the request was right, the refusal was right, and it was destroyed on
delivery. The typecheck had nothing to say about it, because a string is a
string.

`RequestError` now carries `status` and the untouched `detail`, `planGate()`
reads the structure back out, and `Refusal.tsx` decides how to draw it. The
price and the words *simulated — no real funds move* are rendered on the same
line, because a screen quoting $130 a month without them would be making a
claim this product spends effort avoiding everywhere else.

Every screen then threw the same structure away one layer up —
`setError((e as Error).message)`, in all of them — so fixing the transport
alone changed nothing anybody could see. They now hold the error and hand it
to `Refusal`, which keeps each screen's existing look for an ordinary failure
and draws a gate as a card with a button.

### Screens 130 and 131 — the plan the refusal names

Drawing the refusal properly found the next thing. There was no plans surface:
`GET /plans` and the three `/memberships` routes had no caller either, so the
console could refuse you for not having Pro and had no way to sell you Pro.
That is worse than a flat no — an offer naming a plan in a product with no way
to join one advertises something that appears not to exist.

`Plans.tsx` is that door, and `onPlans` is threaded from the shell into every
screen that can be refused, so the button on the card goes somewhere. Two
things the screen shows rather than smooths over:

- **`visitor` and `free` are different plans that both cost nothing.** A
  visitor has no account and can read a public page; free has an account whose
  work sits in this platform's database in the clear. A picker written from the
  price alone collapses them into one $0 row and hides the whole difference.
- **`the_difference` is rendered verbatim** above the cards — *free and Basic
  run the same app; the difference is where your data lives, and who holds it*
  — because a grid of ticks invites the opposite conclusion, that $20 buys
  features. It buys custody.

The price list needs no account, which is `tiers.py`'s decision and not the
console's: *a paywall nobody can read the terms of before signing in is one
people bounce off*. Everything above the membership card renders signed out.

### Screen 173 — beginning, and passing on

The last five routes, and the backlog reaches **zero**.

**An owner token cannot be the gate on succession.** The signal that route
answers is that the owner has died or cannot act, so requiring their
authorisation would be requiring the one thing known to be unavailable. A
reviewer holds it — outside profile ownership, against a `verification_ref`
kept out of band: a death certificate, a power of attorney. With somebody
named, control passes and a fresh owner token is minted. With nobody, the
profile sunsets to memorial: **frozen rather than orphaned**, because a profile
whose owner has died and which nobody can reach is worse than one that has
plainly stopped.

A contested identity cannot be handed on. An open objection blocks succession
with a 409 — inheriting a profile somebody is disputing would settle the
dispute by transfer rather than by resolving it.

At the other end, **genesis** is a profile born from four questions, and it may
choose its own name from the answers. That is not decoration: a persona
assembled from what somebody said about themselves should not then be handed a
label by a form field.

#### A route that asked for nothing at all

`POST /packs` took no token. Anybody could publish a pack to the marketplace,
name any string as the `publisher`, and name **any account** in
`publisher_owner_id` as the one sales accrue to. The argument against that was
already written down one module over, about gifts — *a body-supplied
beneficiary would let anyone direct a gift meant for a performer into their own
balance* — and this route was making the opposite choice. The account is now
read from the caller's own token, and the body's is ignored.

And the wrist: one press goes down the same paths the full apps use — same
auth, same allowlists, same moderation. A shortcut that skipped any of those
would be a second, weaker way in, which is exactly what a wrist should not be.

---

## The doorless backlog reached zero

It began at **116** and was worked down a block at a time. `doorless_routes.txt`
is now empty, and `test_every_route_has_a_door.py` has a new assertion saying
so directly — separate from the record comparison, so the message is plain when
it goes: *the number is no longer zero*, rather than *strike this line*.
Deferring a route legitimately means editing that test as well as the file,
which is the right amount of friction for a decision that used to be made by
accident.

The guard-on-guard changed with it. It used to assert the snapshot was
non-empty, which no longer means anything, so the liveness check moved to where
the meaning lives: **the console must still be producing call sites.** If the
extractor broke entirely, every route would read as doorless — loudly. If it
were quietly narrowed to a handful of forms, that count is what would notice.

What the whole exercise actually produced was not doors. It was defects, and
almost none of them were visible to the typecheck: a swallowed refusal; two
silently-permissive writes; a test that had been green for years for the same
reason a bug was invisible; a picker offering options the server refuses; four
route-audit blind spots; two surfaces that took no token at all; a licence sold
to somebody who could not use it; a link that resolved against the wrong
origin; an honesty note served to nobody. **Building the door kept finding
something wrong with the room behind it** — which is the argument for the whole
method, made once, at length, by doing it 116 times.

### Screen 172 — one thing, named

Six routes that each answer about one particular thing, and six different
answers to **who may ask**:

| | who may ask |
|---|---|
| the light legend | anybody; it takes no id at all |
| a campaign | **anybody**, deliberately |
| an organization | signed in |
| an excursion | the profile's owner |
| somebody's lent skills | themselves |
| a place's lent skills | you, filtered to your own |

**The campaign is the inversion, and it is the point.** It is the most public
read in this product, and that is exactly what makes it honest: it carries
`proceeds_to`, so somebody about to give money sees who receives it on the
same card, before they give it. A fundraising page that hid its split would be
the ordinary kind of dishonest. In the same spirit a campaign cannot exist
before the designation does — creating one first is refused with *say where
the money goes first: designate loved ones or organizations before asking
anyone for it.*

Two reads are narrower than their names suggest, and both say so rather than
letting a screen misread them. An **excursion** carries the brief that was
sanitised before it left and the count of what was stripped out of it; those
two numbers are the whole basis on which the feature asks to be trusted, so
the screen shows them together — *nothing left this machine* and *three
private terms stripped before it went* are very different reassurances and
either alone is misleading.

A **place's** lent skills are filtered to the caller's own, with a `note`
saying a room-wide view needs a membership check that does not exist yet. The
console renders that note verbatim, because a short list there means *your*
grants, not *no* grants — reading it the other way turns an access limit into
an empty room.

The light legend is built from the mapping rather than written beside it, and
the backend says why: *a legend that is maintained separately eventually
describes a mapping the code does not have, and it is the legend people
trust.* So the statuses driving each light come back with it, and the screen
shows them.

### Taking it back — three answers to "there was nothing there"

Four routes, and **no new screen**. A take-it-back control belongs beside the
thing it takes back; a fourth screen collecting all the deletes would be a
place nobody would look. So unfriending went onto Friends, withdrawing a
comment onto Wall, and listing a profile in the directory onto Market.

Building them side by side surfaced a disagreement none of the three routes
knows it is in:

| | nothing to remove | somebody else's |
|---|---|---|
| a comment | **404** `no such comment` | **403** `not your comment` |
| a directory listing | **404** `profile is not listed` | 403 |
| a friend | **200**, `removed: false` | — (owner-only) |

The third is the one that bites. A caller reading only the status code reports
*Removed.* for a row that was never there — so the friends screen reads the
flag and says *"Nothing to remove — not a friend."* The other two let the
refusal carry the fact.

None of this is a bug in any one route; it is three reasonable local choices
that stop agreeing the moment a screen has to speak for all of them. Recorded
rather than unified, because changing a delete's status code changes it for
every client already written against it — and a test now asserts all three
together, so a future round that does unify them changes it on purpose.

Two controls are absent rather than present-and-refused. The founder's two
profiles are pinned and answer 409; the list marks them with `pinned`, which
the backend's own docstring says exists *so a client can render those rows
without a remove control*. And *withdraw* appears only on your own comments —
the profile being commented on is not the comment's author, and removing
criticism from your own page is a different power from withdrawing your own
words. This route grants only the second.

### Screen 171 — what leaves, and on what terms

Five routes: the gateway's status, the contribution view and its revoke, and
the two halves of licensing a profile out.

**Two different kinds of leaving**, kept apart because conflating them is how
somebody agrees to the wrong one. A *contribution* sends one anonymised
exchange to the shared model — no ids, the persona name replaced, and a random
ref so the item can be deleted at the gateway later without identifying
anybody. A *licence* sends the profile itself: the right to consult it, or
where the offer allows, to derive a whole new agent seeded from its persona
and owned by the buyer.

**The preview is a dry run, and the heading has to say so.** `preview_next` is
computed whether or not the profile is opted in, which is useful — it answers
*what would this cost me* before you commit — but a console rendering it under
one heading either way tells an opted-out owner their next conversation is on
its way out. The heading changes with `opted_in`; the content does not.

Revoking does two things and reports them apart: it stops future
contributions, and it asks the gateway to delete past ones by their refs.
`deleted_at_gateway` comes back true **vacuously** when nothing ever left, so
the console reads the count beside it — a tick shown for both cases would be
the wrong reassurance.

#### A licence sold to somebody who could not use it

A licence permitting derivatives used to sell to anybody. A fourteen-year-old
could buy one: **201**, `can_derive: true`, and the fee credited to the seller
at sale time — then a **403** on the only thing the licence exists for.
Somebody had been paid for a thing the server would not hand over.

The adult check now runs at **acquire**, where the money moves, rather than at
derive. A consult licence still sells to anybody, deliberately: it buys time
with a profile and creates no new owner, so tightening that would be a
different decision than the one this fixes.

### Screen 170 — reaching out, and what stops it

Five routes: the outreach itself, the quiet-hours window, the engagement
record, a rating, and the latent picture of one relationship.

**Four refusals, and only two of them are the owner's to lift.** A profile may
message somebody unprompted only if its owner switched that on, and even then
three more gates stand in the way. They answer in four different sentences,
and the difference is the whole point — a screen that collapsed them into
"can't right now" would be discarding the only thing the owner can act on:

| | who lifts it | how |
|---|---|---|
| reactive-only (403) | the owner | turn outreach on |
| awaiting a reply (429) | the recipient | reply once |
| rate cap (429) | time | wait out the interval |
| quiet hours (429) | **the recipient** | change their own window |

**Quiet hours are not the owner's to set.** Sending them with an owner token
is a 403, and that refusal is the feature rather than a gap in it: a window
your correspondent can move is not a boundary. The console shows the control
to whoever holds the person's own token and explains the refusal to everybody
else, because an owner who does not know why it is missing will look for a
bug.

The window is half-open — from the first hour up to but not including the
second — so a start equal to its end covers **nothing**. Somebody setting 9 to
9 to mean *all day* gets no protection at all. That is recorded as it is and
warned about on the screen rather than corrected: changing the arithmetic
would silently redefine every window already stored, which is a worse answer
than saying it plainly.

#### Two surfaces that took no token at all

Both found by building the screen. Neither was visible to the typecheck, and
neither was caught by the suite — the tests sent no token because they did not
have to.

- **The engagement record was readable by anybody.** How often a named person
  talks to a profile, across how many sessions, and whether they liked it,
  answered 200 to a caller holding nothing. The rule was already written down
  one route over: a profile's beacon list is owner-gated because *that is a
  list of physical places associated with a person*. This is the same argument
  about a different column. It is now the owner's and that person's, and
  nobody else's.
- **A rating could be cast in somebody else's name** — and that is worse than
  it first sounds, because an `up` rating is the trigger for contributing the
  exchange to the shared cloud model. Open, this let an unauthenticated caller
  cause a stranger's conversation to leave the deployment: the one failure
  this repository's whole cloud posture exists to prevent, reachable with two
  ids and no token. A rating now needs the rater's own token, and the owner is
  refused it too — a rating in somebody's name is a lie about what they
  thought, and the score is what the profile then behaves from.

The embedding stays owner-only, and unlike the engagement record the person
themselves does not get it either: it is not a record of what they did, it is
what the profile inferred. It is rendered rather than described, because a
number nobody can see is a number nobody can argue with.

### Screen 169 — where people find you

Six routes: the two scan surfaces, the two QR images, and the platform beacon
that is neither.

**Two codes that look identical and go opposite ways.** A placed beacon brings
a stranger *here* — the profile answers them on QRME. A platform beacon sends
them *away*, to an Instagram or Mastodon account that already exists; only
where there is no handle to build a link from does it fall back to a QRME
summon page. The pictures are indistinguishable, so the screen says which is
which. Scanning one to find out is not a reasonable way to learn it.

**Looking at a code is free; opening it is not.** Every scan surface
increments the count — the page, its JSON twin, and the older `/summon?ref=`
— because the server cannot tell an owner checking their own sticker from a
stranger who found it. Only the QR image itself is free. A `?preview=1` would
fix the inconvenience and ruin the number: the count is the only evidence a
sticker on a wall is working at all. So the console renders pictures freely,
never opens a scan page on its own, and labels every scan link with what it
costs.

A connection has a direction and the two never share a row: `collect` pulls an
account's content in, `publish` runs the profile out, so a read-only import can
never also post. Only `publish` has a beacon, and the list says so by giving
`beacon: null` — the button is absent rather than present and refused.

#### The audit was blind to the two requests with no function call in them

An `<img src>` is a fetch. An `<a href>` is a fetch. Neither passes through
`req()` on the way, and the route extractor could see neither — so
`/b/{id}` and `/beacons/{id}/qr.svg` sat on the doorless backlog while
Placements had been rendering both since it was written. That is the same
false-positive failure the nested-template bug produced a few rounds ago,
arriving from a different direction: a guard that invents work fails more
quietly than one that misses some.

Worse, the exemption list had absorbed three of them. `/pair/qr.svg`,
`/desks/{id}/view.webp` and `/desk-beacons/{id}/qr.svg` were all marked
*"rendered in an `<img src>`, not fetched by the API client"* — an exemption
made out of a blind spot, which is exactly the shape that stops anybody
asking. One of the three turned out to have **no door at all**: a desk's view
frame was never rendered anywhere in the console, so the honesty note attached
to it — *a sample view; this deployment has no camera on this desk, so the
frame is not live and is not claimed to be* — was being served to nobody.

The rule the list now holds to: exempt a path because nothing should ever call
it, never because the audit cannot see the call. Two entries survive — a terms
page and the click target of a verification email, both places somebody is
*sent* to from outside.

#### And a link that went nowhere

A desk beacon returned a **relative** `scan_url` while the profile beacon next
door returned an absolute one. The desk screen rendered it as a link, which
resolved against the *console's* own origin — so it went nowhere in every
build where the console is not served by the API, which is every packaged
build. The QR image had been encoding the absolute URL all along; the JSON
description of that same code disagreed with it. Both shapes are now asserted
side by side, which is the only reason they cannot drift apart again quietly.

### Screen 168 — who follows, and what they pay

Nine routes: subscriptions, gifts, the audience counters and the buyer's side
of the ledger.

**Nothing renews on a timer.** A period is charged when somebody presses
renew — so `periods` is a count of deliberate acts, and the screen says that
rather than showing it as a duration. `audience.py` gives the reason: a
deployment left running does not accrue charges nobody authorised and nobody
saw. Paid also asks for an `accept_price` that matches the price *exactly*,
which is not a flag but a check that the number somebody agreed to is the
number being charged.

One asymmetry worth knowing, because the two routes look alike:

- a **gift** reads its beneficiary from the subject — `commerce.beneficiary_of`
  says why, that *a body-supplied beneficiary would let anyone direct a gift
  meant for a performer into their own balance*;
- a **subscription** takes a beneficiary from the request body.

The console sends the profile's own account and shows which account the money
is credited to, because that is the part somebody paying is entitled to see.
It is a question worth settling rather than something I changed unilaterally.

Gifting refuses without a verified birthdate — *an unverified age is not
evidence of an adult* — and `cap_per_gift` is published so the limit can be
stated before somebody runs into it.

### Screen 167 — who is in the game with you

Eight routes: the gaming lobby, and the handoff.

The lobby's entire design is one sentence it publishes about itself —
**everything in this lobby observes and talks; nothing in it plays** — and the
`never` list spells that out twelve ways. The obvious entries are the dull
ones. The interesting four close routes somebody would otherwise argue for:

- **its own hardware** — *a second machine does not turn a bot into a player;
  it just moves where the bot is running*;
- **a second controller** — *the same bot with a shorter cable, and a
  controller nobody is holding is not a player's*;
- **a Bluetooth pad** paired to it as an input device;
- **a capture card** feeding it the picture.

The console renders all twelve verbatim. "No cheating" is not the same
statement, and shortening an argument to a slogan is how the argument gets
lost.

The uncomfortable card is the one showing **what a synthetic member is told**.
The instruction says openly that some of the others in the lobby are synthetic
too — because a model that believes every callsign is a person addresses them
as people, and a lobby that reads as five friends when it is one player and
four generated voices is exactly the impression this product exists to
prevent. It is shown to the owner because that is the only way to check it.

The handoff turns out to be the **lighter sibling of the referral above**, and
the pair is worth seeing together:

| | referral | handoff |
|---|---|---|
| authorised by | a device signature over the bytes | explicit consent |
| lifetime | one open, ever | until revoked |
| on revoke | — | the package is *purged*, not hidden |

Neither substitutes for the other, and a product offering only the heavier one
would push people to skip it.

### Screen 166 — handing it to somebody qualified

A profile is not a clinician, and the package it assembles says so before it
says anything else. Twelve routes: the clinician directory, the referral
lifecycle, and the signature behind it.

Every part is built to be awkward where the easy version would be wrong.
**Prepare releases nothing** — you read exactly what would go, and the
challenge it raises **is the hash of those bytes**, so signing it signs this
summary rather than a checkbox, and a summary edited afterwards cannot ride the
old signature. **The link works once**, and a second attempt says *when* the
first happened rather than quietly working, because a replayed link is
something the patient should be able to discover. The clinician may write back
one time, and their words stay theirs — the profile never recites them as its
own knowledge.

Three pairs here are one wrong variable from a bug that looks like success, and
each is labelled on the screen rather than left to the reader:

| | |
|---|---|
| the **referral token** | opens it |
| the **reply token** | answers it, and does not exist until it has been opened |
| `envelope_id` | is what gets signed |
| `signature_id` | is what release checks |
| **proofing level** | how the identity was checked |
| `can_sign` | what that actually permits — and a referral is `high` |

The screen shows `can_sign` rather than the tier table, because that is the
fact somebody needs when the button is greyed out. Matching is expertise-first
by design: *a cardiologist two streets away is not a substitute for a
psychiatrist*, so area filters and location only ranks, and no match is an
empty list rather than a near-miss.

**The route audit gained a second blind spot fix.** The WebAuthn ceremony is a
*page the browser navigates to* — it has to be, because WebAuthn refuses a
mismatched `rpId` and an opaque origin has none to match — so no client
"requests" it and every client that opens it counted as doorless.
`clientpaths.py` now recognises `window.open` as the GET it is. The URL has to
be built as `getBase() + \`/signatures/ceremony…\`` for the extractor to
resolve it, which is worth knowing before the next one.

### Screen 165 — what it can do for you, and the mark on what it makes

Triage, proofreading, composing something to keep, the wearables the watch
faces run on, the reviews from people who actually talked to it, correcting
your own turn, and the check on any mark. Fifteen routes.

**Checking a mark asks two questions, and they can disagree.** `valid` says the
credential was issued by this deployment; `content_match` says this is the
content it was issued for. A genuine credential whose content has since been
altered comes back `valid: true, content_match: false` with a sentence saying
so. A screen reporting `valid` alone would call something genuine at the exact
moment the server said it had been changed — the one failure a provenance check
must not have, because it is worse than having no check. The screen asks both,
always, and draws the mismatch loudest.

Two arguments are rendered verbatim rather than summarised. **A room-facing
microphone is refused with a paragraph**: a smart speaker *hears whoever walks
into the room, and they did not pair it, were not asked, and may have a right
not to be recorded*. "Unsupported device" would be the console throwing away
somebody's reasoning. And **triage returns the reason each item survived**, with
its score — a pile sorted by a number nobody can see is a pile somebody has to
re-check by hand, which is the work triage was supposed to do.

`answers_stale_text` is drawn too: a reply written before the message above it
was edited says so, rather than the conversation quietly rewriting itself.

Two smaller things the round turned up. `include_revoked` was never bound, so
the promise in `wearables.py` — *unpairing is a revocation, not a delete, the
row stays* — was invisible in the console; a kept promise nobody can see may as
well not have been kept. And **the route audit could not see `fetch`**: `req()`
serialises JSON, so a raw-bytes upload has to call `fetch` directly, and
`POST /profiles/{id}/media` had a working door while still counting as
doorless. `clientpaths.py` now recognises both call forms.

### Screen 164 — what a profile is made of

Source material, the dials, a CV, the specialists it hands work to, the bodies
it speaks through, and the local fine-tune that folds all of it back in. Twelve
routes and not one caller in the console: the profile could be created and
talked to, and everything that made it *this* profile rather than a default one
was unreachable.

Two of these writes were **silently permissive**, and it is the same shape
twice — a Pydantic model where every field has a default, so a body it does not
understand is accepted, discarded, and answered `200`:

| route | takes | the guess |
|---|---|---|
| `PUT .../steering` | `values` | `dials` — what the *read* calls its catalogue |
| `PUT .../experience` | `period` | `years` — what anybody writing a CV form reaches for |

Neither produced an error. The row saved with no dates, the dials did not move,
and both requests looked exactly like successes — same status, same shape,
plausible body. Nothing in the response distinguished *I applied your change*
from *I ignored it*, so a client that fired and moved on would never find out.

Both models are strict now, so a wrong key gets a 422 naming the field. But the
strictness is the fix, not the guard: the guard is the thing that would have
caught it in the first place, which is **writing and reading back**. That is
what `test_a_write_that_answers_200_did_something.py` does, and its name is the
rule — *a request model with defaults for every field can never fail on a body
it does not understand, so where that model is the target of an owner's edit,
"accepted" and "applied" have to be checked separately.*

Making the models strict then broke a test that had been green for years, and
the way it broke is the sharpest part of this. `test_the_menu_matches_the_kitchen`
has a case named *every dial the server describes can be set* — written for
exactly this failure, and sending `{"dials": {…}}`. It passed on every dial
while setting none of them, because the server accepted the body and ignored
it. **The guard was green for the same reason the bug was invisible.** It no
longer trusts the status: it moves each dial off its current value and asks the
server what it holds.

Building the screen produced a third one of the same family. The picker for
what a profile speaks through offered `screen`, `wearable` and `vehicle`; the
enum is `speaker, earpiece, hologram, robot, humanoid, other`. Each wrong option
sat in the dropdown looking exactly like a right one and would have 422'd on
submit. A test now reads the `Literal` off the model and checks the console's
option list against it.

Three things the screen renders rather than summarises: a source's content when
it is there, because *there* means readable — by this platform, by whoever
operates it, and by a lawful request, and a tick saying "stored" would hide
which side of the custody line the account is on; the fine-tune's answer, which
is mostly claims about what did *not* happen (`external_transmission: false`,
`computed: "locally…"`); and the identity signature, which is the one thing on
this screen a stranger can verify — `GET .../embodiment-consistency` needs no
account, so somebody who met the profile through a speaker can check it against
the one they met in a room.

### Screens 162 and 163 — bodies, and where a rated profile is marketed

The last two doorless blocks, and both had a trap that a route signature hides.

**163, bodies.** The native shells already drove the catalogue, the binding and
a command button, so the routes describing what a body has *become* had no
caller anywhere. Three list-shaped things here have almost the same name and
mean different things:

| | is |
|---|---|
| `robot.commands` | what this model of body accepts at all — the buttons |
| `GET /robots/{id}/commands` | the audit log of what it was told to do |
| `GET /robots/{id}/skills` | task modules from a pack, which **extend** the first list |

A screen built from the route names puts the log where the buttons belong, and
it typechecks. Each installed skill's `procedure` is rendered verbatim, because
every one of them names what the body will *not* do — *reminders only: never
dispense*, *companionship, not care, and never a substitute for human contact*
— and that limit is the sentence somebody pointing a robot at a relative needs
to read. `behavior_profile` is drawn beside the dials: pace becomes motion
eagerness, autonomy becomes initiative, assertiveness becomes firmness. It is
the difference between a slider and an explanation.

The steering write takes **`values`**, not `dials` — and the request model
defaults to `{}`, so a body keyed anything else is accepted, ignored, and
answered `200` with nothing changed. There is no error to notice. The only way
to find it is to write and read back, which is what the test does.

**162, rated placement.** An adult-mode profile can be advertised at an adult
venue — a creator platform, a directory — as a link or a printable code. The
feature is only defensible because of one sentence the backend puts on every
venue, rendered verbatim and never paraphrased: *every summon of a rated
profile resolves through QRME's 18+ age wall, regardless of where the QR or
handle was found*. The wall does not travel. Summarising that to "18+" drops
the load-bearing half.

Three more things that were only visible by driving it:

- `scan_url` and `summon_url` are **not** interchangeable — the first is where
  a phone camera lands and what the code encodes, the second is the JSON
  surface for clients. Publishing the wrong one hands somebody a page of JSON,
  so the screen labels both;
- `funnel.chat_rate` is **null, not zero**, until something has got through the
  wall. `(null).toFixed()` is `"0"` in JavaScript rather than an error, so a
  screen that did not check would publish a conversion rate nobody measured;
- taking a placement down **deactivates the beacon rather than deleting it**,
  so a code already printed at a venue stops resolving instead of being
  reissued to point somewhere new. That is the safety property, and the screen
  says it as it happens.

Adding the tab also turned up something only clicking finds: the always-on
agent-lights widget was fixed to the bottom-left corner, **on top of the
sidebar**, and the sidebar had grown long enough that its last three tabs were
underneath it — a click landed on the lights. That is the same fault the phone
layout was fixed for in an earlier round, when the widget covered Home and Chat
and the tabs were reported as broken screens; the desktop half simply had not
grown into it yet. The column reserved the widget's footprint for a while; the
widget has since left the column altogether for the edge dock (screen 211),
and the test that held the arithmetic now holds that nothing the shell floats
declares a `left` at all.

## Channel 3 — sharing your camera

`qrme/viewfinder.py`, 7 routes, 28 tests, screens **136** and **137**.

Channel 2 lent the profiles an ear. This lends an eye: a live view through the
camera in your hand, for the enormous class of problems where **describing the
thing is the hard part and showing it is trivial**. A mechanic looking at your
engine bay. A plumber watching you point at the joint. An electrician reading
the plate on a consumer unit. A vet watching a dog walk.

JIM-mini's `capture.py` is the still, sealed, asynchronous version of the same
idea, and the difference is the whole module. **A photograph is one framed
moment somebody chose. A live camera is whatever happens to be behind it** —
the rest of the room, the post on the table, the child in the doorway. Somebody
who agreed to *"show you the leak"* did not agree to any of that.

### What is in shot decides the rules, not who is watching

This is the inversion the module is built on. The obvious approach gates on the
viewer — *is it a person or a profile* — and it gets both important cases
wrong. A profile that can see an engine bay is genuinely useful and the stakes
are a car. A real stranger watching a live view of somebody's body is not made
safe by being human.

| in shot | a person may watch | a synthetic profile may watch |
| --- | --- | --- |
| **object** — engine, boiler, board, leak | ✅ | ✅ |
| **document** — paper, a plate, a meter | ✅ | ✅ |
| **place** — a room, a site, a yard | ✅ | ✅ |
| **person** — a body, an injury, how somebody moves | ✅ | ❌ |

The refusal is published by name with its reason, and it points somewhere
useful: a profile watching a body in real time would be making judgements about
it with no examination, no accountability and nobody to answer for being wrong
— and unlike a still, there is no moment somebody chose to send. JIM-mini
reaches the same conclusion from the other direction, where a photograph of a
rash is never handed to an agent.

### The viewer never controls the camera

No remote zoom, no focus, no lens switch, no torch, no capture trigger. **The
person holding the phone points it**, and `viewfinder.NEVER` says so out loud —
a remote party who can operate the camera on somebody's device has something
categorically different from a view, and it is the thing people are actually
afraid of when they decline. A test reads the router and asserts no route looks
like camera control, because the easy way to add a zoom button is a new
endpoint rather than a new argument.

Also never: any other camera on the device, coordinates, a session that starts
without the holder starting it in the moment, and any state where it is running
and not visible on the holder's own screen.

### Ephemeral, capped, and yours to end

It records nothing unless somebody says so. Fifteen minutes by default, **45 as
the ceiling** — long enough to look at an engine properly, short enough that a
forgotten session is measured in minutes rather than a working day. Two to open
and one to close, the shape `sharing.py` uses for a lent skill: symmetric
consent to start makes it a loan, asymmetric consent to end stops it being a
trap. And it dies with the surface, because nobody remembers a permission
granted inside a conversation that finished.

The disclosure is a first-class read rather than something a client assembles,
and it is **not** open to anybody holding the surface id — a room id rides on
printed beacon stickers, and *"who has a camera live in there, and is it
recording"* is exactly what a stranger who scanned one must not be able to ask.
That mistake shipped once in `roommic`.

### Bystanders are the unsolved part, and it says so

Nothing here can tell whether somebody walked into frame. A "bystander
detection" toggle would be **worse than the gap**, because it would be relied
on. So the honest version is a note addressed to the only party who can
actually see the room: *we cannot tell whether somebody has walked into shot,
or blur them if they have; you can look at the room before you start, and stop
the moment it stops being about the thing.*

All three of these — the camera, the lent microphone, the worn overlay — now
share one console door (**158**), because they share one rule: whatever you put
between yourself and the people around you, they are told. The screen renders
the `never` list, the bystander note's *"we cannot see the room"*, and the
refusal when a profile is asked to watch a body, all verbatim. Each is an
argument already made carefully here, and a paraphrase would be a worse version
of it.

Building that door found something worth writing down: **the camera and the
microphone accept different sets of surfaces.** A watch party takes a lent
microphone and refuses a shared camera; a room takes a camera and lends
microphones through its own route. Two vocabularies that look interchangeable
and are not — a single picker built from either one refuses half its own
options, which is what the first version of the screen did.

## Membership

`qrme/tiers.py`, 4 routes, 26 tests, screens **130** and **131**.

Three plans and a doorway below them.

| | | |
| --- | --- | --- |
| **Visitor** | free | read any public page — a scanned beacon needs no account |
| **Free** | **$0** | make your own profiles and your own agent, stored in the clear |
| **Basic** | **$20/month** | the same, sealed in the vault under a key you can hold |
| **Pro** | **$130/month** | everything that leaves your account: the marketplace, connectors, skills, downloads, connections, and every modifier and builder |

**Free and Basic reach identical capabilities, and that is deliberate** —
`includes("free") == includes("basic")`, asserted by test. What $20 buys is
`qrme/storage.py`'s vault posture, not a feature. See *[Where your data
lives](#where-your-data-lives)* below.

**Money here is simulated**, exactly as in `commerce.py` — subscribing writes a
row and moves no real funds, and every response that names a price says so in
its own body. A test asserts nothing in the module reaches a payment processor.
This is the one surface where a tier system would be tempted to look like a
working checkout, which is precisely where somebody would be misled.

**Visitor is a real state, not an oversight.** QRME's whole reach story is a
stranger scanning a printed code and landing somewhere useful. A wall asking
them to subscribe before they could read the page would break the feature the
beacons exist for.

**Enforcement is one table and one chokepoint.** `tiers.GATED` maps a path
pattern to the capability it needs and `tiers.gate` is installed once as an
application-wide dependency, so **no route opts in** — a capability cannot be
added to the product and forgotten at one of its eleven endpoints. The
alternative was a `require_plan(...)` call at the top of every paid handler,
which is the shape this repository has already been bitten by twice: a
docstring claiming a check the code did not make.

That table is checked against the served routes rather than proof-read, and the
first version failed. It named `/steering`, `/governance` and `/licensing` as
prefixes; none is a route here — steering lives at `/profiles/{id}/steering` —
so all three were **paywalls in front of a wall**. They read as protection,
protected nothing, and would have survived indefinitely, because nothing fails
when a pattern matches no traffic. The table is patterns now, not prefixes,
because most paid capabilities hang off a profile.

**Browsing stays open, and that is a decision.** A Basic member may look at the
marketplace and may not list, sell, license or buy. A paywall that hides the
shop from the person you are trying to sell to argues against itself, and the
catalogue is public to strangers anyway — hiding it from paying members but not
from passers-by would be incoherent.

**The refusal is structured, because 402 is already spoken here.**
`POST /packs/{id}/install` answers 402 for *this pack costs money, confirm the
price*. Both are genuinely payment-required, so the status is right for both —
but a client must show *upgrade* for one and *confirm* for the other, and
telling them apart by matching on prose breaks the first time somebody rewords
a message. So a plan refusal carries `reason: "plan"`, what it needs, what you
have, and the price.

**A membership belongs to the account, not the profile.** Per-profile would
mean paying twice to hold two profiles, which is exactly what `identity.py`
exists to let people do for free. Creating a profile enrols a new account on
Basic; an existing member keeps the plan they have, because making a second
profile must not quietly move somebody off Pro. **Cancelling keeps the
profiles** — a lapsed subscription is not a reason to delete somebody's work,
and a product that deleted it is one nobody could safely try.

## Where your data lives

`qrme/storage.py`, 38 tests, screens **138**, **139** and **140**.

There are two postures, and the difference between them is the whole of what
Basic buys.

| | | |
| --- | --- | --- |
| **Open cloud** | Free | the platform's own database, in the clear. The operator can read it, a backup contains it, a subpoena reaches it |
| **Encrypted vault** | Basic, Pro | sealed in PDI before it lands, under a key you can hold yourself, with a tamper-evident chain over every access |

**Free and paid differ in where your data lives, not in what you can do.** A
free tier crippled into uselessness teaches nobody anything about the product;
a free tier that is honestly *not private* teaches somebody exactly what they
are choosing between.

### Who holds it

The other half of the same question, and the one the free plan is really
about. `storage.CUSTODY` names two arrangements:

| | | |
| --- | --- | --- |
| **Platform custody** | Free | QRME holds your work and you have access to it — the familiar hosted-assistant arrangement. It reaches us over ordinary HTTPS, sits in our own database, and never goes through a vault |
| **Your custody** | Basic, Pro | sealed in PDI before it lands, under a key you can hold. We operate the service; we do not hold the contents |

**Custody, not ownership, and the word is deliberate.** A product gets to
decide who *holds and operates* a record. It does not get to decide away
somebody's statutory rights over their own personal data — access,
rectification, erasure and portability survive whatever a plan says, in every
jurisdiction that has them. A tier table claiming "the platform owns your
data" would be claiming something no court would honour, and this repository
does not put claims in tables it cannot keep. `test_custody_is_never_described_as_ownership`
checks the values a user is actually shown.

**The vault gate asks about the plan, not the deployment — and it did not
used to.** Every seal point read `if pdi is not None`, which is whether the
*operator* configured a vault. So a free account on a PDI-backed deployment
had its work sealed into a vault it was not paying for and could not hold a
key to. `storage.vault_for(plan, pdi)` is now the one place that question is
asked, and `test_a_free_account_puts_nothing_in_the_vault` counts writes
rather than reading call sites — because reading call sites is how twenty of
them stayed wrong.

**Writes only. Reads and deletions keep the real vault, always.** Somebody
who was on Basic for a year and moved to Free still has a year of sealed
records: they have to be able to read them back, and erasure has to be able to
purge them. A plan-gated vault on a read strands somebody's history behind a
billing change; on a delete it leaves records nobody can reach and calls that
erasure. Both are worse than the bug the gate fixes, and both are asserted.

**Signing deliberately keeps the real vault whatever the plan**, because a
signer is frequently an *interactor* with no membership at all — gating
`signatures._seal` by their plan returns None and the custody chain a referral
depends on quietly stops being written. That is the same trap that put
`signature` on the sensitive list in the first draft, and it is recorded in
the module so the loop is not closed the tidy-looking way.

**So the disclosure is structural.** `storage.describe()` is carried on every
surface that names a plan — `GET /plans`, `GET /memberships/{id}`, and the body
returned when a profile is created — and `not_private` is a **field**, not a
footnote. A privacy claim that lives in a Terms of Service and not in the
response body is a claim nobody reads at the moment it matters. And the open
posture names its readers rather than gesturing at them: *you, anyone you share
with, the people who operate this deployment, anyone with lawful access to it.*
"Industry-standard security" is what a product says when it does not want to
finish the sentence.

**Some payloads are refused rather than quietly exposed**, and the test for
the list is not *would the account holder mind* — it is **whose exposure is
it**:

- **source material about somebody else.** They did not pick this plan.
- **anything behind the age gate.** Rated content needs the vault.
- **a clinician's written opinion about a real person.** The patient did not
  pick this plan either — and this one reached the open store because the
  referral flow writes through `referral.reply` rather than `add_source`, so
  the third-party rule above, which is the same rule, never saw it. Refused at
  `POST /referrals/prepare`, **before any clinician is contacted**: refusing
  when the note comes back would strand a real person who has already been
  written to, mid-flow, holding words they cannot file.

Both are payloads where the person harmed is frequently not the person who
clicked. Letting free store anything and warning loudly sounds more respectful
of the user's autonomy and is not, for exactly that reason.

The list is short on purpose and holds only what *this* repository can refuse —
`test_every_sensitive_kind_is_enforced_somewhere` fails if a kind is named
here that nothing outside `storage.py` actually checks. The first draft named
`body_image` and `medical`, which are JIM-mini's payloads and unreachable from
here, and a `signature`, which is **not a storage-at-rest risk at all**:
WebAuthn keeps the private key on the device, so there is nothing for an open
store to expose. Gating it also broke signing outright, because a signer is
frequently an interactor with no membership — `plan_of` returned "visitor", the
posture came back open, and every enrolment was refused. A sensitive list
assembled from which words sound alarming is how that happens.

**A hard line is never answered with a price.** A rated profile *of another
real person* is refused at any amount, and the first version checked the
storage posture first — so the response was **402**, telling somebody the line
is a price. It is not. The check now runs after the hard line, and
`test_a_hard_line_is_never_answered_with_a_price` holds the order.

**A downgrade never unseals anything.** Moving from Basic to Free leaves
everything already sealed exactly where it is; only new content goes to the
open store. A billing event that silently declassified a year of somebody's
records would be the worst thing this module could do, so `downgrade_effect`
exists to *state* the rule rather than to perform it — a test asserts it
contains no write at all.

**And an upgrade does not un-expose anything.** Content written in the clear
was in the clear. Sealing it afterwards protects it from here on and changes
nothing about the backups, logs and copies that already exist, and
`upgrade_effect` says so in those words. A product that implied otherwise
would be selling absolution rather than encryption.

## The pane in the corner

`qrme/dock.py`, 5 routes, 34 tests, screens **128** and **129**.

The watch faces answer *what am I currently presenting as* without making you
leave what you are doing, and a fixed screen does the same for a wall. Both need
hardware, and **most people have neither**. The dock is the same answer for
somebody holding only the phone: a small pane in the bottom corner of the app,
with no watch frame around it, that tucks away behind the helper button.

<table>
  <tr>
    <td align="center" width="34%"><a href="screens/128-the-corner-pane.svg"><img src="screens/128-the-corner-pane.svg" width="200" alt="The corner pane"></a><br><sub><b>128</b> · tucks away with the helper</sub></td>
    <td width="66%" valign="top">

| route | does |
| --- | --- |
| `GET /dock/faces` | the vocabulary, and what it refuses to cast |
| `GET /dock/where/{face}` | the screen that can actually do this |
| `GET /dock/{id}` | where the pane sits, and how it opens here |
| `PUT /dock/{id}` | move it, tuck it, hide it, change its faces |
| `GET /dock/{id}/face/{name}` | one face, as the pane would draw it |

`?surface=` and `?platform=` change how it opens; the stored preference does
not change with them.

  </td>
  </tr>
</table>

**It is the same faces as the wrist, not a new set.** `dock.FACES` is built from
`wearables.FACES` and a test binds the two, so a face added to the watch appears
in the pane or is turned away here **by name with a reason**. Two catalogues of
the same glances would drift, and the one nobody re-reads wins.

**It shows, and it routes. It never acts** — the exact inversion of the watch's
one exception, and the inversion is the point. Watch face 05 can *end* a lent
microphone, because the watch is the device doing the listening and a permission
you cannot revoke from the thing running it is not really yours. Nothing here is
the device: the real screen is one tap away in the same app, so a control in the
pane buys nothing and costs something, because this thing floats over live
video. A button that ends a stream sitting a thumb's width from the one that
pauses it is a mis-tap on somebody's broadcast. So `control` is the one wrist
face the dock refuses, and every face carries a **route** instead.

**It is inside every screenshot.** `displays.NEVER` exists because a wall is
read by whoever walks past; `dock.NEVER` exists for a different reason that
lands in the same place — a pane pinned to the app frame is captured by every
screenshot, every recording and every screen share, *including the one being
broadcast right now*. So no message bodies, no memory, no agent names, no viewer
names; and on a surface that is going out it opens **tucked** however the
preference is set. Capped rather than overwritten, in the same shape as
`roommic`'s gain: the preference is returned alongside as `wanted`, so the
settings screen and the pane cannot disagree about what was chosen.

**The bottom corner is a constraint, not a taste.** The top-left carries whose
surface this is and the top-right the recording light, so a pane that could
cover either could hide who you are watching or whether you are live. Both
entries in `dock.CORNERS` are at the bottom; the second exists because
bottom-right is a right-hander's default.

**On the desktop it replaced something rather than joining it.** That corner
already held a pinned agent-lights panel with no way to put it away — three
quarters of this feature, missing a lid. It is now the dock drawn open on the
`agents` face, which is why `DEFAULT_STATE_ON["desktop"]` is `open` where the
phone's is `handle`: a desktop user has no wrist to glance at, and amber and red
are the states nobody thinks to go looking for. Adding a second floating box
beside the first was the alternative, and it is what you get by not looking.

### Asking where something is

<table>
  <tr>
    <td align="center" width="34%"><a href="screens/129-where-is-it.svg"><img src="screens/129-where-is-it.svg" width="200" alt="Where is it"></a><br><sub><b>129</b> · directions, not a description</sub></td>
    <td width="66%" valign="top">

*"Where do I change my background"* is the question the help box got most and
answered worst: a correct paragraph **about** backgrounds, handed to somebody
who was asking where they live.

`help.DIRECTIONS` is keyed by tutorial lesson, so the directions cannot name a
screen the walkthrough does not cover, and a test asserts **every lesson is
reachable by some phrasing**. The phrases are what people type — somebody
looking for overlays types *change my face*; nobody types *overlays*.

  </td>
  </tr>
</table>

The answer names the screen, and says so out loud when the same thing is also a
face on the pane — read from `dock.ROUTES`, the one table both use, so the
assistant and the corner cannot disagree about where a feature lives. Matched
before `TOPICS` and before any model, because both would have described the
feature instead, and a model cannot know the screen numbers.

The order is refusals, then the walkthrough, then directions. *"Where do I
start"* is a request for the tour; *"where is the game lobby"* is a request for a
screen; *"pretend you are my friend"* is neither, and is still refused first.

## Friends you might know

`GET /profiles/{id}/friends/suggested`. Ranked on friends in common and
subjects you both work in, each carrying the reason in words — the same posture
as the feed, because a friend suggestion is a claim about a person and one
nobody can explain is one nobody can argue with.

Two exclusions matter more than the ranking. **Anyone already on your list, in
either state** — somebody who removed a friend does not get them handed back as
a suggestion tomorrow, which would be the same imposition the founder pins
avoid, wearing a recommendation badge. And **the founder pins**, who are on
every list by construction and would otherwise top every suggestion set on the
platform.

Never ranked on source material, memories or anything vaulted: an introduction
built from somebody's private writing would be the platform reading a diary to
make it.

## The community wall, and the feed

A profile publishes to its wall (`POST /profiles/{id}/wall`); other people see
some of it in their feed (`GET /profiles/{id}/feed`). Publishing is the easy
half. The feed is where the decisions are.

**Likes, comments and shares are not new.** The audience layer already carried
those four verbs against a `(kind, id)` pair, and `post` is now one of its
target kinds — so a like on a post is the same row shape, and the same
`UNIQUE (target, actor)`, as a like on a profile. No parallel tables, and none
of the drift a second set would have grown within a round.

**Every post says why it is in front of you.** Each entry carries a `reason` in
plain words — *a friend posted this*, *you have talked to this profile*,
*popular with people here*. A ranked feed that cannot explain itself is one
nobody can audit, including whoever wrote it, and the explanation costs a
string. `GET .../feed` also returns its own weights, so the ranking can be
argued with rather than merely accepted:

| signal | weight | |
| --- | --- | --- |
| a friend posted it | 100 | you chose to stand with them |
| you have talked to the profile | 60 | you were actually there |
| tags you engage with | 25 | it works in something you follow |
| likes | 2 each, **capped at 40** | popularity contributes, it does not decide |
| recency | up to 10 | a tiebreak, not the ranking |

The cap is the interesting one. Uncapped, a single heavily-liked stranger
outranks every friend you have — which is the failure mode people actually
complain about, and a test pins it.

<table>
  <tr>
    <td align="center" width="40%"><a href="screens/87-for-you.svg"><img src="screens/87-for-you.svg" width="230" alt="For You"></a></td>
    <td valign="middle">

Every row on the feed screen carries its reason and its score, and the last row
says what the ranking will never look at. Desktop view **10 · Community** puts
the friends list beside the feed with a full *why it is here* column — the one
thing a wide window does that a phone cannot, and the reason a ranked feed you
can read the reasoning of all at once is one somebody can argue with. That is the screen doing the same job
as the API: a feed you cannot interrogate is one you have to take on trust.

  </td>
  </tr>
</table>

**A post can promote something.** `listing_id` attaches one of the profile's
own marketplace listings — a reference, not a copy, because a price written
into a post is a price that goes stale the moment the listing changes and
nobody edits the post. A profile can only promote its own listings.

**The feed is on the homepage too.** A page showing what you made and nothing
of what anyone else is doing is a business card; the reason people sat on their
MySpace page was that it was also where the day's news arrived. Six entries,
ranked for that profile by the same rules — a page is somewhere you arrive, and
the endless version lives on its own screen.

**Moderation runs on the way in and on the way out.** Every post passes the
same filter as a chat turn; a blocked one is kept, returned to its author with
the reason, and invisible to everyone else. On the way out, an adult profile's
posts are walled out of an ordinary feed — a gate inherited from the *author*
rather than judged per post, because otherwise an adult profile publishes past
its own wall by writing something innocuous.

## The stream — one card at a time, and who is allowed to play

The wall's feed above is *yours*: ranked for one profile, explained row by row.
The **stream** is the other kind — one public card filling the screen, swipe
for the next, and the next. `GET /feed` and `GET /feed/{id}`, both readable
without an account, because somebody who followed a link from a sticker on a
shop window is a reader like any other.

<table>
  <tr>
    <td align="center" width="33%"><a href="screens/189-feed.png"><img src="screens/189-feed.png" width="210" alt="Feed"></a></td>
    <td align="center" width="33%"><a href="screens/190-what-plays.svg"><img src="screens/190-what-plays.svg" width="210" alt="What Plays"></a></td>
    <td align="center" width="33%"><a href="screens/191-rooms-desks.svg"><img src="screens/191-rooms-desks.svg" width="210" alt="Rooms &amp; Desks"></a></td>
  </tr>
</table>

**The rule the stream had to not break.** `post_videos` in `qrme/db.py` has
carried the same comment since long before a stream existed: *the link and the
id, never the file and never a thumbnail* — re-hosting somebody's video is a
copyright problem, and a cached thumbnail is a copy of an image nobody granted.
It is why a QRME wall renders without one request to YouTube.

An endlessly autoplaying stream is the one surface where that promise is
expensive to keep and cheap to lose. Flick past fifty cards and, done the
ordinary way, you have announced your address and your taste to fifty companies
for footage you never chose to watch.

    asked     does the stream play the next thing
    mattered  does swiping past something tell a stranger you were here

So the line is drawn on **who holds the file**, and it is drawn on the server
rather than left to four clients to remember:

| the file is | `plays` | what the card is |
| --- | --- | --- |
| held by this deployment (`media`, `kind='video'`) | `true` | it plays, and it loops |
| held by somebody else | `false` | a title, a platform name, a link — and no request until you press |

`test_an_offsite_video_never_plays_by_itself` asserts that on the wire, where
every client reads it, rather than in any one of them. It is easy to satisfy
today and easy to lose the day a console decides autoplay is a nicer default.

**Every fourth card is a place with a person in it.** This is the part a video
app cannot do. Mixed into the recordings are **live rooms you can walk into**
and **desks with a real human behind them**, with the shop behind the desk
reachable without leaving the stream — browse it, see the prices, ring the
bell. Both carry a plain sentence *before* the button, because both reach
somebody:

> Walking in puts you in the room with the people already there. Your
> microphone is off until you turn it on.

> Ringing reaches a person. Otis is at the desk — the bell is not a message,
> it is somebody's attention.

**Nothing is in the stream by default.** A post reaches it only if it is on the
wall and approved; a desk only if it is not closed; a room only while it is
active **and** attached to a desk that chose to be found — a room with nobody's
desk behind it is a private conversation and is not in this stream at any
ranking. A rated desk is *absent* for a reader who is not verified rather than
blurred, and a shared link to one answers `404` rather than `403`, because a
403 announces that the thing exists.

And every card says why it is there, the same as the wall's feed does. A stream
that cannot explain itself is one nobody can audit, including whoever wrote it.

**On all four clients.** The stream is on the web console, on the iOS, Android
and Windows shells, and reachable from JIM-mini's Feed tab. The phones read the
same two routes and render the same `plays`, and the fourteen `feed.*` strings
are the console's own rows copied into the three native tables so the desktop
and the phone cannot drift apart on a surface new to both.

What the phones do not have yet is the **gesture** — Previous and Next are
buttons there. That is stated in each screen's own docstring rather than
implied away, and it is not only a matter of effort: a stream a person can use
only by dragging is one somebody with a motor impairment cannot use at all, so
the buttons are the version that works for everybody while the swipe is built.

## Agreeing before work changes hands

Somebody comes up as a guest on a desk and it turns into business — they will
build something, review something, hand over a file. The moment that happens
two strangers are about to send each other things, and the interesting part is
not the sending. It is the **agreeing**, because that is where every dispute
comes from and the one place a platform can actually help.

So an exchange (`qrme/exchange.py`, `POST /exchanges`) is a document before it
is a transfer. One side proposes; the document names, item by item:

* **what goes across, in each direction** — every artifact with its kind and
  its size, so *what am I about to receive* is a list rather than an assurance;
* **what the work is**, in one sentence, and which of sixteen industries it
  belongs to — this is a business agreement in any trade, not a software
  feature the other trades are allowed to borrow;
* **what is included when it is finished** — the clause people actually argue
  about afterwards;
* **what is not included**, said out loud, because an absent exclusion reads as
  an inclusion to whoever paid.

Then both sides sign, and only then does anything move. Four rules make that
more than a form.

**Neither signature alone opens anything.** `GET /exchanges/{id}/channel` —
the one call a transport layer should ask — reports `open: false` until both
parties have signed. A one-sided agreement is not an agreement.

**Any change to the manifest voids both signatures** (**113**). This is the
rule the whole design turns on: without it you agree to a two-item manifest and
the other side appends a third, and your signature sits on a document you never
read. Signatures are stored against a **fingerprint of the agreement**, not
against its id, which makes that a fact about the data rather than a promise
about the code — after an edit the old signatures match nothing. In practice
the guarantee is stronger still: the document freezes the moment *anybody*
signs, so the only route to an edit is `reopen`, and that deletes the
signatures on its way past. A signature here is either current or absent;
there is no way to make a stale one.

<table>
  <tr>
    <td align="center" width="34%"><a href="screens/112-the-agreement.svg"><img src="screens/112-the-agreement.svg" width="200" alt="The agreement"></a><br><sub><b>112</b> · the manifest, before anyone signs</sub></td>
    <td align="center" width="33%"><a href="screens/113-signatures-cleared.svg"><img src="screens/113-signatures-cleared.svg" width="200" alt="Signatures cleared"></a><br><sub><b>113</b> · one item added, both signatures gone</sub></td>
    <td align="center" width="33%"><a href="screens/114-delivery.svg"><img src="screens/114-delivery.svg" width="200" alt="Delivery"></a><br><sub><b>114</b> · accepted one at a time</sub></td>
  </tr>
</table>

**Nothing downloads by itself** (**114**). A signed exchange makes each item
*available*; the receiving side accepts them one at a time, and only the
receiving side can — the sender cannot accept on their behalf. Consent to an
agreement is not consent to a file landing on your disk. Items that **run** —
`source` and `build` — are flagged as such on the manifest and again at
acceptance, because a signature on an agreement is not a review of what the
code does.

**It grants no access to anybody's device**, and that limit is in the code
rather than in a warning. An exchange moves named artifacts somebody attached;
it opens no session, runs nothing, and reaches nothing that was not listed.
Hooking one machine up to another is a different feature with a different
threat model, and shipping it quietly inside a file-sharing agreement would be
the wrong way to arrive at it.

The console reaches all of it (**153**): propose, list what crosses, sign,
and accept item by item. The screen re-renders the whole agreement from every
reply rather than patching what is already on it, so an edit that clears the
signatures is something you watch happen rather than something you are told
about afterwards.

## Lending a skill, in any room you are both in

Two people are in the same place — a room, a live desk, a watch party, a
connection, an agreed piece of work — and one of them has something the other
needs. A finance pack. A robot's task modules. A profession. A language pair.
`qrme/sharing.py` (`POST /skill-grants`) lends it, and the same mechanism
covers every one of those surfaces rather than five near-copies of it.

The whole feature is the word **both**, and the shape it takes is deliberately
lopsided:

> it takes two to open a grant, and one to close it.

Symmetric consent to start is what makes it a loan rather than a taking.
Asymmetric consent to end is what stops it becoming a trap — somebody who has
changed their mind should not need permission from the person benefiting to
change it back. A consent model that needs *both* sides to stop is one that
cannot be withdrawn under pressure, which is exactly when withdrawal matters.
Either party closes it alone, and the record says which of them did.

**A skill is used, never handed over.** The borrower may invoke it while the
grant stands; they get no copy, no install and no licence. Packs here are
bought, licensed and attributed to publishers, and a lending feature that
quietly duplicated them would be a piracy tool with a consent dialog on the
front. The permission is checked at the moment of **use**, not at the moment of
grant, so closing a grant stops the next call rather than merely preventing new
grants.

**A grant lives in one place and dies with it.** Lending your expertise in a
watch party does not follow the borrower into a private message — a skill lent
in one surface is refused in another, by name. Ending the party or withdrawing
the exchange closes what was lent inside it, and that teardown is wired at the
point the place ends rather than left to a caller to remember, because the
thing forgotten would be a live permission with nothing left to justify it.

**Every use is written down, and the lender reads it.** *Both parties choose*
is a slogan unless the person lending can see what was done with it. The log is
the reason a grant is worth agreeing to: you can watch it being used and stop
it mid-sentence.

| | |
| --- | --- |
| where | `room` · `desk` · `party` · `connection` · `exchange` — no "everywhere", and no "my account" |
| what | `pack` · `robot_task` · `profession` · `language` · `workflow` |
| to open | both, and only the person it was offered to may accept |
| to close | either, alone |
| transferred | nothing |

The console door (**154**) is arranged around the asymmetry. The button that
ends a grant is never disabled by which side you are on, because the moment
withdrawal matters is exactly the moment the other party would not agree to it.
The use log is shown to both of you: a record only one side can read is not a
record.

## Who these surfaces think you are

An exchange, a lent skill and a watch party all name the acting party in the
request body — `actor_id`, `host_id`, `borrower_id`. **An id in a body is a
claim, not a fact**, and `common.require_self` is what turns it into one: the
token presented has to belong to the person the body names.

That check was missing when those three shipped, and the gap was total. An
anonymous caller could forge *both* signatures on somebody else's agreement,
open its channel, and accept delivery of an executable on their behalf; accept
and use a skill somebody lent to a third party; or seize the scrubber in a
watch party by passing the host's id. Every consent property the three modules
describe rested on a check that did not exist — the modules were right and the
doors were open.

| surface | who may act | who may read |
| --- | --- | --- |
| an exchange | the two parties, each only as themselves | the two parties — a manifest names somebody's files, their sizes and what the work is worth |
| a lent skill | the lender offers; the borrower accepts, declines and uses; either closes | the two parties, plus the borrower's own view of the log kept about them |
| a watch party | the host seeks and ends; a member speaks only as themselves, or as a profile they own | members only |

Two details worth stating because they are easy to get subtly wrong. Bringing a
**synthetic profile** into a room speaks in its voice, so it is its owner's call
and nobody else's. And the surface listing was narrowed: it was meant to be
"what the room can see about itself", but there is no room-membership check to
hang that on, and without one it listed who was lending what to whom to anybody
who guessed the id. It now shows the caller's own grants, and says so.

`tests/test_two_party_auth.py` holds all of it. Each case is asserted twice —
once against an anonymous caller and once against **a valid token belonging to
the wrong person**, because a test that only tries the first passes against a
system that accepts any logged-in user as anybody.

## How many people it is talking to

A synthetic profile talks to many people at once by construction. One process,
many conversations — that is what the thing *is*, not a flaw in it.

The harm was never the multiplicity. It is the **discovery**: somebody who has
been talking to a profile for a month and then finds out — by asking, or by
accident — that there were thousands of others has not learned a new fact so
much as learned that the fact was available the whole time and nobody offered
it. That gap is entirely the product's doing, and closing it costs a count and
a sentence.

So `GET /profiles/{profile_id}/attention` is **public and needs no token**,
answering with the number of distinct people this week and altogether, and one
plain line. Making somebody get an account before they may learn it would be
the same withholding with a form in front of it, which is why the count lives
on the accountless screen next to the objection form and the mark check — on
the console and on all three phones.

Three things it deliberately is not, and they are **fields rather than prose**
so a screen renders them beside the number instead of composing a reassuring
sentence of its own:

| | |
| --- | --- |
| `ranks_people: false` | there is no order and no leaderboard |
| `has_a_favourite: false` | *"you're my favourite"* is a lie the software cannot make true — and it hands somebody something to lose, so the day the count goes up they lose it |
| `names_anybody: false` | the count is a fact about the profile; who the others are is a fact about **them**, and none of them agreed to be counted out loud to a stranger |

The last one is greppable rather than promised: `test_no_query_here_can_return
_a_name` reads the SQL in `qrme/attention.py` and fails any statement that
selects a column instead of counting rows. A viewer may ask *am I one of them*
— about their own id, and only their own.

Nothing here models jealousy, and nothing invites it. A product that
manufactures the feeling in order to resolve it has manufactured the feeling.

## Watch parties, and a profile that has not seen the video

A watch party (`qrme/watchparty.py`, `POST /watch-parties`) is a posted video
plus everyone who turned up — and on this platform that includes **synthetic
profiles**, which is where the honesty problem is.

**A pasted link works too.** The screen has one field, and the most natural
thing to put in it is a YouTube link — the field report that forced the issue
was exactly that, answered with "that post has no video to watch". So `start`
takes either the id of a posted video or a `video_url` (a URL pasted into
`post_id` is recognised for what it is): the link faces the **same platform
allowlist** a wall post's video does, and the video hangs off the party's own
id — no post is fabricated on anybody's wall to hold it, so it can never
surface in a feed. What a post-anchored party inherits and a link-anchored one
cannot — an author and their rating — is covered where it already lives: the
room's maturity is decided by who is in it (a minor in the room forces
strict), not by who posted the video.

**Private by default; public is the host's deliberate act.** The party id is
the private door — share it and somebody jumps straight into your room — and
that is all a party is until the host publishes it (`POST
/watch-parties/{id}/listing`, host-only; `DELETE` takes it back; ending the
party delists it). Published, a **card** rides `GET /watch-parties/public`
(tokenless — public means public) and the feed's live rotation beside rooms
and desks (`kind: "party"`, and JIM's Feed tab inherits it through the same
door): the title — required, and moderated at the strict filter like every
public surface — the video facade, and **counts, never names**: who is inside
and what was said stay members-only, and joining from the card is each
viewer's own press, said out loud before the button. The card's join is the
same members door as ever; publishing never weakens what a member token
protects.

**A profile has not seen the video. It cannot.** Nothing here fetches it,
nothing transcribes it, and a profile saying *"the bit at four minutes was
great"* would be fabricating — the most ordinary-looking lie this product could
tell, and the one nobody would think to check. So
`GET /watch-parties/{id}/context` hands a profile only what exists on this
side: the title the poster typed, the platform, where the room has got to, and
what the humans have said. `description_available` and `transcript_available`
are both `false`, and it says so in the prompt, in the second person:

> you have not watched this video and cannot see it. Talk about what the others
> in the room are saying and about what the video is titled. If somebody asks
> what you thought of a moment in it, say you have not seen it rather than
> inventing one.

Starving a model of context and hoping is not a safeguard. Telling it the truth
about its own position is.

**The room shares a position, not a player.** The host moves a number and
everyone follows; it does not press play on anybody's device. That is what
keeps the embed promise from being broken twenty times at once — a party that
pre-loaded the video for twenty people would have made twenty requests to
YouTube nobody agreed to. **Only the host** moves it, because otherwise the
last person to scrub decides what the room is looking at.

Every member carries `synthetic: true|false`. A room where you cannot tell
which of the six names is a person is the room this platform exists not to
build. Party chat is moderated like every other utterance, a party with a minor
in it runs strict, and a party can only be opened on an **approved** post —
otherwise it would be a way to put a video in front of people that the wall
refuses to show them.

The console shows that instruction verbatim (**155**), in a panel of its own.
A person whose profile is sitting in a room discussing a film can read exactly
what it was told about not having seen it, rather than trusting that it was
told anything.

## The page you make yourself

Every profile already had a **front page** — portrait, skills, experience,
rating — assembled from what the platform knows. It is useful, and it looks
exactly like everybody else's, because a generated page is the same page 34
times.

This is the other kind: `GET`/`PUT /profiles/{id}/page`. A theme, an accent
colour, a tagline in your own words, a paragraph about yourself, and a **Top 8**
— the friends you want at the front, in the order you want them. It is the
MySpace idea, and the reason it is worth reviving is not nostalgia on its own: a
page somebody arranged tells you what they thought was worth putting first,
which is the one thing a generated page cannot.

<table>
  <tr>
    <td align="center" width="50%"><a href="screens/85-my-page.svg"><img src="screens/85-my-page.svg" width="230" alt="My Page"></a><br><sub><b>85</b> · the page, in its own colours</sub></td>
    <td align="center" width="50%"><a href="screens/86-customise.svg"><img src="screens/86-customise.svg" width="230" alt="Customise"></a><br><sub><b>86</b> · the editor behind it</sub></td>
  </tr>
</table>

Six themes — Midnight, Starfield, Sunset, Chrome, Meadow, Paper — a validated
`#rrggbb` accent, and three layouts.

Three things it deliberately does not do:

**Real HTML, through an allowlist.** You write your own markup — that is the
thing anybody actually remembers about a MySpace profile — and every tag and
attribute goes through [`qrme/markup.py`](qrme/markup.py) before it is stored.

Raw markup is not a stylistic objection. In October 2005 the **Samy worm** used
exactly this feature: script smuggled through a profile, executing in the
browser of everyone who viewed it, a million friends in about twenty hours, and
the site taken offline. The nostalgia is worth reviving; that is not.

| in | out |
| --- | --- |
| `<b> <i> <u> <marquee> <center>` and 30 more | kept — including the 2004 ones, which cannot execute |
| `style="color: …"` and 30 visual properties | kept |
| `<script> <iframe> <object> <form> <svg>` | removed, content and all |
| `onclick`, `onerror`, every `on*` | removed — this is where injection actually lives |
| `javascript:` and `data:` URLs | removed; only http, https, mailto, fragments and site-relative paths survive |
| `//host/path` | removed — protocol-relative, so it looks like a path and fetches from another host |
| `@import`, `expression()`, `behavior:` | removed |
| `background-image: url(…)` | **kept** — held to the same URL check as `<img src>`, because a background is most of what decorating a page means |
| `position`, `z-index` | removed — they lift an element out of the page's own box |
| an unknown tag | dropped, **its words kept** — eating somebody's writing looks like a bug |

Sanitised **on the way in**, so there is exactly one moment unsafe markup could
exist rather than one per renderer, each of which could forget. What was
stripped comes back as `html_removed`, so an editor can say *your `<script>` was
dropped* instead of quietly returning a page that does less than its author
wrote. `GET /pages/themes` publishes the allowed tags and properties so an
editor can grey out what it knows will be lost.

**The chat overlay in a live room is transparent** — circular faces on a soft
scrim over the video, rather than a comment panel taking a bite out of the
picture people came to watch (**89**). The screens round their own avatars; the
baked bubbles in `docs/portraits/bubbles/` exist for the README, which cannot
draw one because GitHub strips the `style` that would round an `<img>`. Using
the pre-baked file in the app would put a bubble inside a bubble.

**Like, comment and share work on a post**, because `post` is an audience
target rather than a parallel system — the same rows, and the same
`UNIQUE (target, actor)`, as a like on a profile. A test now walks every kind
in `TARGETS` through `share_url`, because sharing a post raised `KeyError` at
the moment somebody pressed the button: the kind was added to the target list
and its share URL was not.

**A post can carry a video from somewhere else** — YouTube, Vimeo, Twitch,
Dailymotion, Rumble (`qrme/embeds.py`, `POST /profiles/{id}/wall` with
`video_url`, and `GET /videos/platforms` publishes the list). Three decisions
make that safe to do here rather than merely possible.

*Nothing is copied.* What is stored is the platform, the video's id on it, and
the title **the poster typed** — never the file, never a scraped title, never a
downloaded thumbnail. Re-hosting somebody's video is a copyright problem and a
cached thumbnail is a copy of an image nobody granted. The video stays where its
owner put it, on the terms its owner agreed to.

*No third-party request until the viewer asks for one.* This is the part that
matters on a platform whose promise is that data does not leave a vault. A
normal embed loads the other company's player the moment the page renders,
which tells them you looked **before you decided to**. So what renders is a
**facade** — the platform's name, the poster's own words, and a play control,
all served from here. Pressing play is when the request happens, and the viewer
is told so in words before they press it. A privacy promise that holds only
until an embed loads is not one. The empty plate on **95** is the feature, not a
gap in the mock: drawing a YouTube thumbnail there would have been the prettier
picture and a picture of the thing the code refuses to do.

*The allowlist is a list, not a pattern.* Anything not on it is refused by name,
because "looks like a video URL" is how an open redirect becomes a feature. Each
platform knows how to recognise its own links and how to rebuild a canonical
watch URL **from the id** rather than from the pasted string — so a tracking
parameter, a redirect, or a lookalike host cannot ride along into what gets
stored and later opened. A Twitch *channel* link is refused too: it points at
whatever happens to be live, which is not the thing anybody posted.

The age gate is inherited rather than re-judged. A video post is a post, so it
already carries its author's rating through `audience.is_rated` and is walled
out of an ordinary feed by machinery that was already there. Nothing here claims
a video is *suitable* — a platform's own rating is not visible from a link, and
the poster's rating is the only claim this system is in a position to make.

**A storefront, not a second copy of one.** `show_offers` surfaces the
profile's own marketplace listings on the page, read from `listings` rather
than retyped — a second copy of a price is a second price that can be wrong —
and `links` carries up to twelve outbound links under the same URL rule.

**The Top 8 does not reorder the friends list.** It features friends rather than
creating them — a profile you are not connected to is refused — and it is a
showcase, not a second source of truth. Your Top 8 is what you chose to put
first; your friends list is who you stand with.

**About-me text is moderated like anything else written for other people to
read.** A blocked one comes back to its author with the reason and is invisible
to visitors, which is the shape the audience layer already uses for a comment.

The editor (**157**) lists the surviving tags *before* you write, which is what
`/pages/themes` published them for — the backend's own comment says "so an
editor can grey out what it knows will be stripped, rather than letting
somebody write it and lose it", and until now nothing read them. It also shows
`html_removed` after a save, because the save succeeds either way: without it,
a `<script>` disappears and the page simply does less than its author wrote.

## Friends, and the two who come as standard

Profiles have **friends lists** — a profile ↔ profile graph, which is a
different thing from the `relationships` table that has always been here. That
one records how a profile treats an *interactor*: the person typing at it, and
the tone and boundaries that follow. This is the other axis, and it is the graph
the community surfaces are drawn from.

<table>
  <tr>
    <td align="center" width="40%"><a href="screens/84-friends.png"><img src="screens/84-friends.png" width="230" alt="Friends"></a></td>
    <td valign="middle">

**Directed, not mutual.** Befriending writes one row. A friends list is a claim
its owner makes about who they stand with, and a mutual edge would mean somebody
else's action edits your list. Two rows make it mutual, and the API reports
`mutual` per entry.

**Two founder profiles stand at the top of every list**, fixed: they cannot be
removed and cannot be pushed below a chosen friend. Everything else in the list
is entirely the owner's to add and drop, and an ordinary friend removes
normally.

**Position is computed, never stored.** The pins are first because their rows
say `origin='founder:N'`. A stored position has to be rewritten on every insert,
and it is the thing that is wrong on the day the founder turns up third.

  </td>
  </tr>
</table>

The list marks pinned rows with `pinned: true`, so a client renders them without
a remove control rather than offering one that returns `409`.

### Two profiles, one person

David Bianchi — 42, CEO and Imagineer of Private Data Infrastructure Systems,
and the person who built all three of these products — has **two** profiles
here, and the split is the point rather than a duplication.

| | `@david_bianchi` | `@david_bianchi_ai` |
| --- | --- | --- |
| **Picture** | a photograph | an AI rendering |
| **Served from** | `/photos` | `/portraits` |
| **Mark in the pixels** | **no** — the photograph is authentic | **yes** — burned in, top-right |
| **Profile labelled AI** | yes | yes |

A platform whose entire argument is that a synthetic thing must say so cannot
have its owner running one profile that is ambiguously both. So there are two,
and each is honest about what its picture actually is. The real person takes the
plain handle; the rendering is the one carrying the qualifier.

**The photograph is deliberately not marked.** The mark says *AI-generated
synthetic media*. Stamping that on a real photograph is a false statement — in
the opposite direction from the one the mark exists to prevent, but false all the
same. `avatars.render()` reports `asset_marked: false` for it, which is the
signal every surface uses to composite the profile's own AI badge. **The picture
is authentic and the profile is synthetic, and those are two different claims.**

That is also why photographs live under `/photos` rather than beside the
portraits: `/portraits` means *burned and checksummed*, and its manifest check
walks every file in the tree. An unburned file there would either fail that check
or force it to be loosened.

Neither profile is in the starter collection or in `avatars.BRIEFS`. Both promise
invented people in their own docstrings, and a real person in either list would
quietly make a documented claim false.

## Anonymous, several, and exactly one verified

Three things a person is allowed to be here, and `qrme/identity.py` is the
tension between them.

**You may be anonymous.** Not everyone can afford to put their name on what
they think, and a platform that only works for people with nothing to lose is a
platform for a narrow set of people.

**You may hold several profiles.** A person is not one thing — the work self,
the hobby, the one for the support group nobody at work knows about. These are
not sockpuppets; they are the ordinary shape of a life, and forcing them into
one identity is its own kind of exposure.

**Exactly one of them may be verified.** This is the rule the other two need in
order to be safe rather than merely permitted.

<table>
  <tr>
    <td align="center" width="34%"><a href="screens/118-stay-anonymous.svg"><img src="screens/118-stay-anonymous.svg" width="200" alt="Stay anonymous"></a><br><sub><b>118</b> · what we withhold, and what we can't</sub></td>
    <td align="center" width="33%"><a href="screens/119-your-profiles.svg"><img src="screens/119-your-profiles.svg" width="200" alt="Your profiles"></a><br><sub><b>119</b> · as many as you like · one verified</sub></td>
    <td width="33%" valign="top">

| route | does |
| --- | --- |
| `GET /identity/vocabulary` | the three rules, in the words a screen can show |
| `GET · PUT /profiles/{id}/anonymity` | what it hides and what it can't · turn it on or off |
| `GET /profiles/{id}/badge` | the badge a **reader** sees |
| `GET /profiles/{id}/verifiable` | could this one take it, and if not why |
| `POST /profiles/{id}/verification` | claim it, once per person |
| `POST …/verification/move` | move it to another of yours |
| `GET /profiles/{id}/siblings` | your roster — **owner-only** |

  </td>
  </tr>
</table>

**Why one badge.** Verification is not a quality score or a reward for being a
good citizen. It is the sentence *this is that particular real person*. Said of
two profiles at once it is either false of one of them, or it is a statement
that one human being is two authenticated people — which is precisely the
primitive verification exists to deny to everybody else. A platform that hands
it out per profile has not verified anybody; it has sold a badge.

**The badge moves rather than multiplies.** One at a time, not one forever.
People change which face is their public one, and a rule that could only be
satisfied by deleting a profile is a rule they would answer by lying instead.
The record moves whole — level, attestor, method, evidence and the date it was
checked. `checked_at` is deliberately *not* re-stamped: a document seen in 2019
is not a document seen today because the badge changed seats.

**A fictional profile is unverifiable, not unverified**, and never consumes the
slot. `verification.status` already draws that distinction; getting it backwards
here would let an invented character lock a real person out of their own badge.

**The founder is the worked example.** `@david_bianchi` and `@david_bianchi_ai`
are the same human being, so only the photographed one carries the badge — the
seed used to verify both, which had the platform asserting that one man was two
verified people, on the deployment that ships as the demonstration of the rule.
The badge belongs to the photograph because a real person whose picture is
authentic is exactly what it is a claim about; the rendering carries the AI mark
instead, which is the claim that is true of *it*.

**One person means one owner account**, because that is the unit this platform
can observe. `same_identity_elsewhere` closes the part that is visible — the
same attestor vouching for the same evidence under a second account — and
nothing closes the rest. That limit is stated rather than papered over: a
`self_asserted` level carries no attestor and no evidence, so there is nothing
on the bottom rung that could tell two people from one. It is why the rung
exists and why the badge carries its caveat.

### Anonymity had to become a property

`anonymous` was honoured by every surface that *rendered* a profile — the
front-page card, the landing page, the prompt, the watermark — and by the route
that returned the profile, not at all. `GET /profiles/{id}` is public, and it
handed over `display_name` in full. The shortest way past anonymity was to ask
for the profile.

`owner_id` was the worse half, because it does not undo one profile's anonymity
— it undoes all of them at once. Two anonymous profiles sharing an account are
the same person, and anyone could read that field off both and match them, then
read it off the *named* profile beside them and put a name to the pair. It is
now withheld from everyone but the owner on **every** profile, named ones
included, along with `successor_owner`, which is somebody else's account id and
was never a visitor's business either.

**The roster is the dangerous read.** `GET /profiles/{id}/siblings` is the one
call that links a person's profiles to each other, which is exactly the tool for
stripping the anonymity off all of them at once. It is reached through a profile
whose owner token the caller holds, and the account is derived from that — never
taken from the path. A route keyed on `owner_id` would hand the roster to
anybody who learned one, and an `owner_id` is a string somebody chooses, not a
secret. Every anonymity guarantee above is worth exactly what that check is
worth.

**An anonymous profile has a name, and cannot choose it.** Every one of them
used to be called *"anonymous persona"* — identically — which is unusable the
moment two are in the same place: three anonymous people in a room were three
identical labels, so you could not follow who had said what and nobody could be
held to anything they said. **Pseudonymity is a stable name without a real one**,
not the absence of a name. So each gets `Anonymous 41338025`, and three
properties make it work:

- **Derived, never stored.** There is no column, so there is nothing to edit —
  which is what "cannot be modified" has to mean in a system where an owner can
  `PATCH` their own profile. A *chosen* anonymous name would be a free text
  field on the one surface built to withhold identity, and somebody would put
  their real name in it within the hour.
- **Keyed on the profile, never on the account.** The one that would quietly
  undo the `owner_id` redaction above: a person may hold several anonymous
  profiles, and numbering them from the account would give them all the same
  name and match them to each other in public.
- **Hashed, not sequential.** A counter publishes signup order and, from two
  samples, the platform's growth rate. Neither is the profile's to give away,
  and *"Anonymous 7"* is a claim about how early somebody arrived.

Turning anonymity off and back on returns the **same** number, because it is
derived from the profile rather than issued — one that changed would make
somebody a stranger to the people who knew them.

That decision used to be made in **fifteen places** — the front page, the
landing page, the prompt, the watermark, the summon card, the beacon page, the
room roster, the profile route, the export — each with its own copy of
`"anonymous persona" if anonymous else display_name`. A rule with fifteen
implementations is one merge away from having sixteen, and the sixteenth is the
one that prints somebody's name. It is now `identity.shown_name()`, and a test
parses every module to assert nobody has written a sixteenth.

**And it can say what it does, without saying who it is.** The plain
silhouette was every anonymous profile's only face, on the argument that a
distinct picture would be a stable mark following one person around. That
argument died with the fixed name — `Anonymous 41338025` is already stable and
already public, so an emblem adds no correlation the name does not, while a
nurse answering health questions looking identical to a troll is a real cost
paid for nothing.

So there are **sixteen field emblems**, one per industry the platform already
models (`exchange.INDUSTRIES`) — not a new vocabulary invented for pictures: a
field somebody can *work in* is a field they can *signal*. Each keeps the same
silhouette with the field glyph badged on, so "anonymous" is what reads first
from across a roster, before anybody parses which symbol it carries.

**Or their own picture.** The emblems are a shortcut, not a fence. This was
briefly a *closed* list, on the reasoning that a profile able to attach any
image could attach its owner's face and nothing here can look at a file and
tell. True, and the wrong conclusion — it made the feature useless to the
locksmith who wants a photo of their own workbench, and bought no safety,
because somebody set on publishing their face can put it in a post. **A limit
that stops the honest use and not the risky one is decoration.**

So what the platform cannot check, it says. A photograph of your **own** face
is allowed, and the response tells you what it costs: *we cannot tell whether
this picture shows your face, and if it does, the people who know you will
know.* That line is in `NOT_WITHHELD` too, beside "your writing is still
yours" — the honest list of what anonymity does not survive.

**Somebody else's likeness is refused**, asked and declared exactly as the
overlay module asks it: an anonymous profile wearing another person's face is
impersonation with a layer of deniability on top.

**An empty bubble is an empty picture frame with a plus**, for the owner and
for visitors alike. There were briefly two defaults — a plain silhouette for
strangers, the photo-and-plus for the owner — on the reasoning that the second
reads as a control, and a control offered to somebody who cannot press it
reports the empty bubble as a gap. But **the identifying work is done by the
name**: `Anonymous 41338025` already says which account this is, so the picture
is a placeholder rather than a claim about anybody, and an empty frame is the
most honest drawing of an empty frame. Two defaults also meant two things that
could disagree about the same profile, which is the shape of bug this codebase
keeps finding — so `editor_asset` went with the silhouette.

The picture lives in its own table, never in `profiles.avatar`: they are
pictures for two different states, exactly like a display name and an anonymous
one, and writing it into `avatar` would mean turning anonymity off showed it
instead of the face somebody actually has.

**An anonymous profile's badge withholds who checked.** "Verified by Dr Okafor
of St Mary's" narrows an anonymous author to a city and a workplace, which is
most of the way to a name — the badge would undo the anonymity it sits beside.
What survives is the part worth having, and the reason an anonymous profile
would want one at all: *a real person stands behind this, and somebody checked.*
That claim is separable from *who*, and it is the difference between a pseudonym
and a bot.

**And the limits are published beside the promise.** `GET
/profiles/{id}/anonymity` returns `withheld` and `not_withheld` together,
always. The dangerous reading of the word is the generous one: somebody deciding
whether it is safe to post will assume "anonymous" means untraceable unless they
are told otherwise, and by the time they find out, it is published. We can
decline to publish a name. We cannot make prose unrecognisable to a reader who
knows the author, and saying so plainly is the only honest version of this
feature.

**Per profile, never per account.** An account-wide switch would mean putting
your name on the work profile puts it on the support-group one — the exact
coupling that having several profiles exists to avoid.

The console reaches all of it (**156**). The roster comes first, with the badge
drawn as a thing that *sits on one profile and can move* rather than a checkbox
each profile has and most fail — and an invented person reads as
**unverifiable** rather than as an empty box, because those are different
answers. The anonymity card puts `not_withheld` beside `withheld` at the same
size: a screen that showed only the hidden half would be selling the promise
this feature deliberately does not make.

Two of its endings sit on the same screen for the same reason. Retiring leaves
what the profile meant to the people who knew it; deleting returns an itemised
receipt — a count per kind of record, twenty-five of them — because *deleted* is
a claim and the numbers are evidence.

## Verified, and what the word is allowed to mean

`GET /profiles/{id}/verification`. Two questions that a single badge would run
together, kept apart:

- **Is there a real person behind this?** Answered by `kind`. A `fictional`
  profile depicts nobody — which is *not* the same as unverified, and the API
  says so rather than implying somebody failed a check.
- **Has anyone checked they are who they claim?** Answered by a recorded level,
  and the honest answer is usually *not much*.

The ladder is `signatures.PROOFING_LEVELS`, reused rather than reinvented so the
platform has one meaning for how well an identity is established:

| level | means |
| --- | --- |
| `self_asserted` | they say so, and nobody has checked |
| `federated` | confirmed through another account they control |
| `document` | an identity document was checked |
| `in_person` | somebody met them and checked in person |

**Anything above self-asserted needs a named attestor** — the same rule
`signatures.enroll` applies, for the same reason: who checked belongs in the
record, not in a footnote.

### The gold mark

`tools/mark_verified.py` burns **✓ VERIFIED** into an authenticated
person's photograph, in gold, **bottom-right** — diagonally opposite the AI
mark, so the two can never land on each other. It is the mirror image of
`tools/mark_portraits.py` and exists for the same physics: a composited badge
does not survive a screenshot, a hotlink or a right-click save, and those are the
journeys a profile picture actually takes.

**Gold because everything else is taken or already means something here.** Blue
is X and Facebook, grey is the downgraded one people learned to distrust, green
is the agent status light two screens away, and red already means *stopped* in
this product.

**The gate is a named attestor.** A burned mark is the strongest claim an image
can carry: it cannot be qualified, it outlives every surface, and by design it
travels where nobody can check it. That is safe for *AI* — a rendering is
AI-generated wherever it ends up, forever, so burning it in can never become
false. *Verified* is not that kind of fact, so the tool refuses any photograph
with no verification record naming who attested.

What it deliberately does **not** require is a particular rung. It first
required `document`; the platform's owner asked for the mark on his own
photograph at `self_asserted`, which is his call to make about his own face on
his own product, taken after the stricter version had been built and the trade
explained. So the burned word carries exactly the weight of whoever attested —
and the honest reading stays one call away. `verification.status` still reports
`self_asserted` and still returns its caveat:

> *self-asserted: the badge confirms a real person stands behind this profile,
> not that a document was checked*

**Nothing in the code claims a document was checked, because none was.** The day
one is, the level moves and the badge means more without the pixels changing.

## The agent status light

An agent working on its own raises one question, and it is not *what phase is
it in* — it is **does this need me right now?** Three colours answer it.

| | | |
| --- | --- | --- |
| 🟢 **green** | working · done | in progress, or finished. Nothing wanted from you |
| 🟡 **amber** | needs you | it has stopped and is waiting on a person |
| 🔴 **red** | stopped | it hit an error or was cancelled, and will not continue |

**Derived, never stored.** There is no `light` column and nothing sets one — it
is computed from the status the work already keeps. A second field naming the
same fact is a second field that can disagree with the first, and the one a
screen reads would be the one nobody remembers to update.

**The word rides with the colour**, because green alone cannot separate an
agent that is still going from one that has finished, and those call for
opposite reactions. On a watch face the word is doing most of the reading
anyway.

**An unrecognised state raises rather than defaulting.** A default would paint
an unknown status green, and green is the colour that means *ignore me* — the
one failure this must not have.

Defined once, in [`qrme/agentlight.py`](https://github.com/davidsbianchi1984/qrme/blob/main/qrme/agentlight.py), for all three products.

**Where you actually see it.** Three surfaces, doing three different jobs.

| Surface | What it shows | Why that shape |
| --- | --- | --- |
| **Watch** — *36 Agents* (JIM) | three lights and three counts, and **no agent names** | a wrist is glanced at, not read. Naming the agents was the first cut and was wrong: a name is something you read, and reading is the thing a glance cannot do. Which agent went amber is a question for the app, where there is room to answer it |
| **App** — *82 Agents* | the same three lights, each a **tappable group** — what is working, what needs you, what stopped | somebody opening this *because* amber appeared should not have to scan a flat list for the one that changed. Grouping puts the answer first and the roster second |
| **Overlay** — *83 Chat · overlay*, and every desktop view | a small translucent box in the bottom-right corner — the same three rows as the wrist, each its own way in | an agent that reports only on its own screen is one you have to remember to check, and amber and red are exactly the states nobody thinks to look for. On desktop it is on **every** view, because those users have no wrist to glance at |
| **Studio widget** — the packaged console (`app/`) | a stoplight tab on the edge dock, on every screen, its edge in the worst light's colour — the minimized state; pressed, it opens the round watch-face window beside it with the wrist's exact payload (`GET /profiles/{id}/watch`) — three lights, three counts, the approval line — and each row pressed names which agent stands under that light; the dock slides up or down the right edge by its grip (screen 211) | the studio is where owners actually sit, and the wrist's face is already the right size and shape for "does this need me right now?" — so the studio shows the same face at all times, and when it is in the way it folds to a dot rather than disappearing: still one glance, still the worst colour |

The same three colours, on all three sizes of glass:

<table>
  <tr>
    <td align="center" width="18%" valign="bottom"><a href="watch/01-agents.svg"><img src="watch/01-agents.svg" width="150" alt="Watch — agent lights, counts only"></a><br><sub><b>watch</b> · three lights, three counts, no names</sub></td>
    <td align="center" width="26%" valign="bottom"><a href="screens/82-agents.svg"><img src="screens/82-agents.svg" width="200" alt="Mobile — agent groups"></a><br><sub><b>mobile 82</b> · one tappable group per light</sub></td>
    <td align="center" width="26%" valign="bottom"><a href="screens/83-chat.svg"><img src="screens/83-chat.svg" width="200" alt="Mobile — the overlay follows you"></a><br><sub><b>mobile 83</b> · the overlay, mid-conversation</sub></td>
    <td align="center" width="30%" valign="bottom"><a href="desktop/01-home.svg"><img src="desktop/01-home.svg" width="300" alt="Desktop — the overlay on every view"></a><br><sub><b>desktop 01</b> · bottom-right, on every view</sub></td>
  </tr>
</table>

Read them left to right and the shape of the decision changes with the surface.
The wrist answers *is anything wrong* and stops there. The phone answers *which
one*, by making each colour a group you can open. The desktop does not ask at
all — it keeps the box in the corner of every view, because a desktop user has
no wrist to glance at and an agent that reports only on its own screen is one
you have to remember to go and check.

## Companion features

An ambient-companion model, with an explicit consent boundary on each
feature:

| Feature | Implementation |
|---|---|
| Genesis interview | `POST /profiles/genesis` — a profile born from four personal questions; omit `display_name` and it deterministically chooses its own name from the answers |
| Proactive companionship | `POST /profiles/{id}/proactive/{interactor}` — the profile reaches out first, but only when its owner set `interaction_scope: proactive`; the message is moderated and lands in shared memory. **Anti-spam**: a per-relationship rate cap (`proactive_min_interval_hours`, default 24 h), the recipient's quiet hours (`PUT /interactors/{id}/quiet-hours`), and reply-suppression (no repeat outreach until they reply) — a blocked outreach is `429` |
| Honesty about multiplicity | `GET /profiles/{id}/transparency` reports active relationships, and every chat prompt instructs the profile to acknowledge them truthfully if asked — disclosure by design |
| Summoning — @, #, and QR beacons | `PUT /profiles/{id}/handle` claims a unique `@handle`; `GET /summon?ref=` resolves `@handle`, `#tag` (marketplace tags), or a beacon token. `POST /profiles/{id}/beacons` *leaves the profile behind* somewhere physical — a printable QR code (`GET /beacons/{id}/qr.svg`) summons it, scans are counted, beacons can be picked back up, and a departed profile's beacon resolves as a memorial |
| Connections — chat with other users | `POST /connections/join` matches interactors anonymously by alias in a `friendly` tier or an 18+-verified `rated` tier; per-tier moderation (minors always strict, blocked messages never delivered), and either side can end it anytime. `GET /connections/mine` is the waiting side's half of the roulette: a match is made by whichever side arrives second, so the waiter polls this (never join again — that re-queues them) and every client drops straight into the conversation the moment it answers `matched` |
| Error reports come home | `POST /v1/problems` — the same content-free intake the Cloud Model Gateway serves (shared whitelist screening, folded into counters, never a message or an id), on the product's own backend, so a deployment with no gateway still collects its own failures; consoles and shells fall back to it when no collector is stamped into the build, gated by the same first-run notice and switch. `GET /v1/problems` is the operator's read — `QRME_PROBLEMS_KEY`, or the backend's own machine |
| Rooms — chat, video, AR, VR | `POST /rooms` — multiparty conversations over any channel (`chat`/`voice`/`video`/`ar`/`vr`) with any mix of real users and synthetic profiles: user↔user, profile↔profile (`/rooms/{id}/advance`), or combinations; every profile turn is moderated, and a room with a minor present always runs strict. Each channel gets the same three full-screen states — plain, held, sideways — because those belong to the room rather than to a camera: **103–105** audio (boxes, because there is nothing to look at), **106–108** AR (the others placed in the room you are already in), **109–111** VR/3-D (depth carried by size and position). The strip changes with the channel: no gift button in an audio room, no bell on a posted video |
| Marketplace listings | `POST`/`GET /marketplace/listings` — users and businesses share and market synthetic profiles, content, business expertise, or services; browsable by kind, tag, and area (healthcare, finance, relationships, …). Creating one still needs no token — the seller is established when a price is attached — but an authenticated creator is recorded as the listing's **claimant**, and `DELETE /marketplace/listings/{id}` and the place routes are claimant-gated. Removal used to ask for no credential at all: a stranger could take down a listing that had a recorded seller, an open offer and paid orders against it, while the same stranger asking to withdraw the *offer* on it was told it was not theirs |
| Providers & consented handoffs | `POST`/`GET /providers` — a directory of real local businesses per area (healthcare, medical, mental health, finance, relationships, career); `POST /handoffs` packages the AI specialist's session for a provider *only with explicit consent*, seals it in the PDI vault, and releases it solely through a revocable token (`DELETE /handoffs/{id}` revokes and purges) |
| Embodiments — even robots | `POST /profiles/{id}/embodiments` — speaker, earpiece, hologram, robot, humanoid; chat can arrive from an embodiment, and JIM-mini's autonomous devices can host the same profile. **Personality stays consistent across forms**: the persona prompt affirms one constant identity/memory/voice, `ChatResponse.persona_signature` is invariant across modality and embodiment (voice → text → hologram give the same signature), and `GET /profiles/{id}/embodiment-consistency` exposes that fingerprint + the forms it's live on |
| Graceful departure | `POST /profiles/{id}/sunset` — a farewell composed for every relationship, memory preserved and exportable, archive sealed in PDI, chat closes with `410` instead of a silent 404 |
| Succession & memorial | `POST /profiles/{id}/succeed` (reviewer-verified death/incapacity signal) — ownership passes to the named `successor_owner` with a fresh owner token (the old one revoked), or, with no successor, the profile sunsets to memorial rather than being orphaned. `GET /profiles/{id}/memorial` (public) — the departed profile's memorial: name, handle, purpose, beacon anchors, relationships touched — never persona internals |

## Assistant & perception

The profile as a capable personal assistant and creative partner:

| Feature | Implementation |
|---|---|
| Triage / curation | `POST /profiles/{id}/assist/triage` — sort a large pile of items and keep the best N by a transparent, auditable score |
| Proofread | `POST /profiles/{id}/assist/proofread` — an improved version in the user's voice, plus concrete edit suggestions |
| Perceive & guide | `POST /profiles/{id}/perceive` — "see" a real-time scene (objects, people, gestures, place) through a camera and give hands-free, step-by-step guidance toward a goal, or just share the moment; perceptions are logged |
| Compose creative works | `POST /profiles/{id}/assist/compose` — an original music/poem/note/lyric capturing a shared moment, kept as an artifact (`GET …/assist/works`) |

Every generated result passes the profile's moderation before it is returned.

## Cloud model — use a greater model, and contribute to it

The gateway itself ships here too (`cloudgw/`, `python -m cloudgw`): it
authenticates each contributing deployment, serves one operator-configured
model, and seals contributions into PDI. Its intake **refuses** anything
carrying an identifying field rather than sanitizing it — a quiet strip would
hide the client bug that leaked it.

With a [Cloud Model Gateway](docs/cloud-model.md) configured, inference
routes to the hosted tier (the latest, most capable model — e.g.
`claude-fable-5`) with automatic fallback to the local provider, and
profiles that opt in (`cloud_contribution`) contribute positively-rated,
**anonymized** exchanges back to improve the shared model — ids stripped,
display names replaced, revocable anytime. `GET /cloud/status` reports the
tier. Contributions land in PDI's encrypted, audited intake.

The loop is fully transparent to the owner:

- `GET /profiles/{id}/cloud-contribution` — a dry-run **preview of exactly
  what the next contribution would contain** (nothing is sent), the policy,
  and a verbatim log of everything that has ever left.
- Each item carries a random `ref` — the gateway never sees profile ids, and
  only QRME's local log maps the ref back — so items stay anonymous at the
  gateway yet remain individually deletable.
- `POST /profiles/{id}/cloud-contribution/revoke` — turns contribution off
  **and** deletes everything already contributed at the gateway by those refs.

## Claims 21–26 (`qrme/adaptation.py`, `qrme/tasks.py`)

| Claim | Implementation |
|---|---|
| 21 — latent persona embeddings, persistent cross-session state | A per-(profile, interactor) named latent vector (engagement, warmth, depth, positivity, stress, continuity), EMA-updated after every interaction and versioned in `persona_embeddings`; `GET /profiles/{id}/embedding/{interactor}` |
| 22 — attention conditioning from engagement | The embedding renders as attention weighting in the system prompt (shared history, warmth, depth, reassurance weights), so engagement conditions where the model attends |
| 23 — real-time biometric monitoring during interaction | `ChatRequest.biometrics` (stress_level, heart rate, condition — typically from JIM-mini) is stored, feeds the embedding's stress dimension, and adds a monitored-situation note to the prompt |
| 24 — switching between domain-specialized agents | `PUT /profiles/{id}/specialists` maps domains (mental_health, medical, finance) to specialist profiles; real-time biometric signals route the reply to the matching specialist. The handoff is **sustained within the conversation** — it persists across turns (even turns with no biometrics) until a fresh reading shows recovery, then hands control back. `ChatResponse.handoff.state` reports `engaged` (switched this turn) → `sustained` (specialist still handling) → `returned` (recovered, profile speaks again) |
| 25 — autonomous multi-step tasks with revocable vault access | `POST /profiles/{id}/grants` issues a scoped, revocable token; `POST /profiles/{id}/tasks` runs grant-check → scoped vault read → compose → moderation, logging step summaries only (raw vaulted data is never retained); `DELETE /grants/{id}` revokes instantly. **Workflows** (`qrme/workflows.py`) chain phases into a plan — `research → draft → review → send → confirm` — advanced one at a time (`POST …/workflows`, `…/{wf}/advance`): each phase carries the prior phases' output forward as working memory and runs in persona, the `confirm` phase **pauses** (`awaiting_input`) and **resumes in a later session** (`…/{wf}/resume`), and revoking the grant mid-run halts the next read-bearing phase. **Delegation** (`qrme/delegation.py`) lets somebody *other than the owner* start one — how JIM's Guardian hands work to a specialist rather than sending a chat turn. The workflow routes stay owner-only on purpose: a workflow reads vaulted source material unattended, and a missing grant means scope `["*"]`. So `PUT /profiles/{id}/delegation` is off until an owner writes it, **delegating `research` without a grant is refused at write time**, `POST …/delegated-workflows` accepts only a subset of the permitted phases from somebody already in conversation with the profile, and an owner's own workflow has no `delegated_workflows` row — so it 404s on the delegated routes however the caller authenticates |
| 26 — encrypted, offline fine-tuning | `POST /profiles/{id}/finetune` recomputes all embeddings from stored history locally — no external calls — and seals the adaptation artifact in the PDI vault when configured; runs recorded with metrics and `external_transmission: false`. With `QRME_OFFLINE=1` the whole platform runs on-host: `GET /offline/status` reports `external_transmission_possible: false` and the guarantee that no raw user data ever leaves your vault |

## The specification, mined (`qrme/composite.py`, `qrme/simulation.py`, `qrme/campaigns.py`, `qrme/organization.py`)

The filed specification of App. 19/056,418 and the PDI infrastructure
proposal describe capabilities the claims tables above did not cover; each
is implemented from the documents' own words (tests in
`tests/test_spec_mined.py`, `tests/test_campaigns.py`,
`tests/test_organizations.py`):

| Spec passage | Implementation |
|---|---|
| **Hybrid profiles** — [0038]: "a combination of aspects or characteristics of several people, such as a combination of several past presidents or business leaders, a combination of trusted relatives such as grandparents who are gone" | `POST /profiles/composite` blends ≥2 source profiles into one `kind=hybrid` profile — per-constituent normalized weights and an optional borrowed *aspect* (their patience, their storytelling), recorded in `composite_sources` and published at `GET /profiles/{id}/composition`. Sources must be your own or marketplace-listed; **departed profiles are allowed on purpose** (grandparents who are gone is the spec's own example), rated ones never, and `kind=hybrid` can't be typed free-hand. The persona prompt carries the blend openly: a hybrid says who it is a composite of and never claims to be any single constituent |
| **Real-time simulation & predictive modeling** — clause 1: "real-time simulations of the first person's actions, workflows, and decision-making processes for predictive modeling and operational insights"; clause 5: retained memory "utilized for predictive modeling" | `POST /profiles/{id}/simulate` (owner-only) runs the persona over a scenario and horizon (`immediate`/`short_term`/`long_term`), optionally conditioned on one relationship's memory and latent embedding, and returns decision + workflow + rationale. `confidence` is **earned from evidence volume** (source items, remembered turns, embedding) — never from how sure the model sounds — the narrative is watermarked synthetic, and runs are never distributed (`GET /profiles/{id}/simulations`) |
| **Environmental adaptation** — clause 1: "dynamically adapt to environmental data, such as location, conditions, and user behavior, enabling contextual relevance" | `ChatRequest.environment` ({location, conditions, local_time, activity}) rides into the reply beside the claim-23 biometrics: stored in `environment_context`, rendered into the system prompt so the reply fits where the person actually is, and echoed back on the response. **The room is remembered**: a turn that arrives with no fresh environment recalls the latest stored context inside a six-hour window — treated as where the person most likely still is — and the echo marks it `remembered`, so clients can tell fresh from recalled |
| **Role-specific contexts** — clauses 2/12: "function as an advisor, collaborator, or operator based on the user's interaction … may autonomously interpret user prompts to provide situationally relevant responses" | A chat turn can declare `role: "advisor" \| "collaborator" \| "operator"`, or leave it unset and the profile reads the prompt itself (`qrme/roles.py` — transparent keyword inference, silent on a tie, never a hidden model call). The reply's `role_context` names the role and how it arrived (`declared`/`inferred`); frames shape *how* the profile works this turn — counsel with a recommendation, co-creation with a next step, precise execution — never *who* it is: persona, relationship, memory and moderation apply unchanged |
| **The operational ecosystem** — PDI proposal: role-specific agents that "collaborate across departments, pulling relevant data, offering smart suggestions, and coordinating efforts" | `POST /organizations` + `/organizations/{id}/departments` staff each department with one of your profiles as its role agent, scoped by the same **revocable grant** machinery as claim-25 tasks — revoke and the department's pulls stop instantly, the org stands. `POST /organizations/{id}/coordinate` takes one goal across every department: each agent contributes from its own scoped material in its own persona, the initiating agent composes the joint plan (watermarked synthetic, owner-only, never distributed — so no moderation step), and with the PDI tandem configured the whole record is **sealed into the vault** (`qrme/coordination/…`). `POST /organizations/demo` builds a working demo team on the caller's own account in one press — two granted, desked agents ready to coordinate. **AI for lease**: `POST /organizations/{org_id}/lease` seats somebody else's **consult-licensed** specialist as a department — the fee accrues to the specialist's owner at seating time, the lease rides the owner's licences list beside grants with the same revoke door, and a revoked lease (or a terminated source profile) leaves the department standing but **silent**, named in every coordination it no longer speaks in. Console: the **Org** tab; screen 146 |
| **Crowdfunding, proceeds routed by the user** — [0020] example two: "supply crowdfunding for any loved ones, left behind or organizations for donations, wherever the proceeds might go up to the user" | `PUT /profiles/{id}/proceeds` designates loved ones and organizations with shares that must sum to exactly 100; `POST /profiles/{id}/campaigns` opens a campaign — **refused until a designation exists** and never on a rated profile; `POST /campaigns/{id}/donate` (tokenless — generosity is not gated behind signup; capped like a gift) splits at the door onto the ledger, a designee with a platform account paid on their own statement. The public card always shows the names: a donor gives to people, not to the platform. Sunset changes nothing (the living owner keeps the pen); verified owner death (`/succeed`) revokes the old token and hands it to the chosen successor — "leave it in good hands" enforced by the token lifecycle. Console: the **Campaigns** tab; screen 145 |

## The suite — one origin, one login

QRME, JIM-mini, and PDI stay three independent apps, but `suite/gateway.py`
fronts all three behind a **single origin** so the suite runs as one product
(the [launcher](launcher/) is the desktop shell for it):

```bash
pip install -e .[dev]        # plus the jim-mini and pdi packages for the full suite
uvicorn suite.gateway:app    # /qrme/… /jim/… /pdi/… on one origin
```

On top of the mounted apps it adds a thin, **stateless** cross-cutting layer
(it fans out over the per-product tokens the caller already holds and stores no
*user* credential of its own — the one credential it does hold is the suite's
vault-tenant token, a deployment credential it mints itself so QRME's seals
keep working in suite mode):

| Endpoint | What |
|---|---|
| `GET /suite/health` | Which products are mounted and live |
| `POST /suite/session` | Unified sign-on — provision one identity across all three in a single call |
| `POST /suite/erase` | Right to be forgotten, suite-wide, with a per-product receipt |
| `POST /suite/export` | Data portability — one bundle with the identity's data from every product |
| `PUT /suite/consent` · `POST /suite/consent/read` | Centralized consent, sealed in the PDI vault and enforced across products |
| `POST /suite/usage` | Usage metering hooks for a suite-wide subscription |
| `POST /suite/ecosystem` | One call after sign-on: the demo org seeded in QRME, JIM's care team linked to its first desk |
| `POST /suite/operations` | The caller's coordinations as the vault recorded them — provenance, scoped by owner |

See [docs/tandem.md](docs/tandem.md) for the full cross-product architecture.

**One-command smoke check** — `python -m suite.smoke` boots all three
products in-process (no ports), seeds everything (PDI starter vault + JIM
tenancy, QRME marketplace/packs/registries, JIM specialists + the tandem
hookup), then drives one live exchange: a JIM financial-stress detection
routed to the QRME starter specialist `@marcus_bell`, sealed in the PDI
vault, and its provenance verified back through JIM's custody window.
Prints a JSON step report; exit 0 = the suite is green. Also runs as
`tests/test_suite_smoke.py` (skips cleanly when the siblings aren't
installed).

