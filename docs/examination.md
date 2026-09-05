# QRME — for examination

This page is written to be checked, not believed. Every section grounds the
product in three things: the **technical problem** in the machine, the
**implementation** as built — named modules, named constants, named tests —
and a **measurable effect** that follows from the implementation and not
from a description of it.

Every `.png` under `docs/screens/` and `docs/walkthrough/` is a capture of
the running console taken by `tools/shoot_screens.py` and
`tools/walkthrough.py` against a live backend; an `.svg` is a design drawing
and is captioned as one; the frames under "Real output" are from footage
this platform rendered. The suite (`python -m pytest`, 5,700-plus cases)
reads the README — the release banner, the release table, the gallery, the
numbering and the closing passage fail the build when they drift from the
product.

The screens referred to below are shown in
[the README](../README.md#screenshots).

## The mechanisms on file

The ten numbered mechanisms in
[docs/invention-disclosure.md](docs/invention-disclosure.md). Each row
names the technical problem in the machine, the particular structure this
code uses to solve it, what that structure changes about how the machine
behaves, and where the structure is reduced to practice and held by a
test. None of them is a rule a person could follow with a pen or a
business practice dressed in software; each is a specific arrangement of
data, credentials, channels and checks inside a running system, and each
is photographed on the screens below.

<table width="100%">
<thead>
<tr>
<th width="4%" align="left">§</th>
<th width="23%" align="left">The technical problem</th>
<th width="30%" align="left">The particular solution, as built</th>
<th width="26%" align="left">What it changes in the machine</th>
<th width="17%" align="left">Reduced to practice in</th>
</tr>
</thead>
<tbody>
<tr>
<td valign="top">1</td>
<td valign="top">A generated likeness, once it leaves the server, carries nothing that says which system produced it, under whose governance, or whether its owner may still withdraw it.</td>
<td valign="top">Every approved textual render is <strong>stamped at the output door with the producing profile's credential</strong> (<code>qrme/<wbr>watermark.py</code>), recoverable from the text alone; the owner's steering, moderation queue, licences and erasure all act on the one profile record the stamp resolves to.</td>
<td valign="top">Provenance survives the reply leaving the platform: a stranger with only the words can ask the platform who wrote them and get the profile, its owner and its terms back (screen 148). Erasure removes the record the stamp points at, so a withdrawn profile stops answering.</td>
<td valign="top"><code>qrme/<wbr>persona.py</code>,<br><code>qrme/<wbr>watermark.py</code>,<br><code>qrme/<wbr>moderation.py</code>,<br><code>qrme/<wbr>adaptation.py</code> — <code>test_<wbr>watermark.py</code>,<br><code>test_<wbr>watermark_<wbr>recovery.py</code>,<br><code>test_<wbr>moderation.py</code>,<br><code>test_<wbr>steering.py</code>,<br><code>test_<wbr>an_<wbr>erase_<wbr>is_<wbr>measured_<wbr>against_<wbr>the_<wbr>schema.py</code></td>
</tr>
<tr>
<td valign="top">2</td>
<td valign="top">Paid-capability checks written per route are forgotten at the routes added after them, and an emergency path gated by mistake refuses the one caller who must never be refused.</td>
<td valign="top">One <strong>application-wide dependency</strong> over a capability table (<code>qrme/<wbr>tiers.py</code>) runs on every request before any handler; no route opts in, so none can be missed, and a fixed <code>NEVER_<wbr>GATED</code> set of escalation paths is excluded structurally rather than by each route remembering to.</td>
<td valign="top">A capability added to the table is enforced everywhere at once; a refusal carries the capability's name and the plan that has it, in a shape a screen renders (screens 130, 161).</td>
<td valign="top"><code>qrme/<wbr>tiers.py</code>,<br><code>qrme/<wbr>api.py</code> — <code>test_<wbr>tiers.py</code>,<br><code>test_<wbr>the_<wbr>free_<wbr>tier_<wbr>says_<wbr>what_<wbr>it_<wbr>is.py</code></td>
</tr>
<tr>
<td valign="top">3</td>
<td valign="top">A model credential either lives in the server's configuration, where every caller shares it, or in the caller's client, where the server cannot use it for that caller's request.</td>
<td valign="top">A caller's key rides <strong>one request in a header into a context variable</strong> read by the provider layer at inference time; it is never written to disk or log, and a request without one falls back to the deployment's own key.</td>
<td valign="top">Two callers on the same server generate on two different credentials in the same second, and neither key is ever stored.</td>
<td valign="top"><code>qrme/<wbr>llm.py</code>,<br><code>qrme/<wbr>api.py</code> middleware — <code>test_<wbr>byo_<wbr>key.py</code></td>
</tr>
<tr>
<td valign="top">4</td>
<td valign="top">An exchange between a guardian and a specialist passes through an application database that any operator with the file can read.</td>
<td valign="top">The exchange is <strong>sealed into the encrypted personal-data vault at the seal point</strong> (PDI), with per-record provenance and an audit chain, and read back only through the record owner's scoped custody viewer.</td>
<td valign="top">The platform holds the pointer and the audit trail, not the plaintext; the owner sees the chain of custody for each record and can forget it to the vectors.</td>
<td valign="top"><code>qrme/<wbr>exchange.py</code>,<br><code>qrme/<wbr>pdi_<wbr>client.py</code>,<br><code>qrme/<wbr>recollection.py</code> — <code>test_<wbr>exchange.py</code>,<br><code>test_<wbr>the_<wbr>room_<wbr>that_<wbr>forgets_<wbr>on_<wbr>purpose.py</code></td>
</tr>
<tr>
<td valign="top">5</td>
<td valign="top">A live workspace has no physical address a passer-by can reach, and a microphone in one profile's room cannot be handed to another without a shared account.</td>
<td valign="top">A workspace is published as a <strong>scannable beacon</strong> whose code resolves to the live desk and is deactivated rather than deleted when taken down; a microphone is <strong>lent profile-to-profile</strong> with a named handover and per-channel gain.</td>
<td valign="top">A printed code at a venue stops resolving instead of pointing somewhere new; a lent microphone is on the record as lent, and comes back.</td>
<td valign="top"><code>qrme/<wbr>desks.py</code>,<br><code>qrme/<wbr>roommic.py</code> — <code>test_<wbr>desks.py</code>,<br><code>test_<wbr>room_<wbr>mic.py</code>,<br><code>test_<wbr>the_<wbr>visitor_<wbr>side_<wbr>of_<wbr>a_<wbr>desk.py</code></td>
</tr>
<tr>
<td valign="top">6</td>
<td valign="top">Blending several personas into one produces a profile that can claim to be any of its sources, with no record of what was borrowed from whom.</td>
<td valign="top">One profile is built from several with <strong>normalized weights and named borrowed aspects</strong>, the composition stored per constituent and published to every reader; the prompt carries an honesty rule, and rated sources and free-hand hybrids are refused at the door.</td>
<td valign="top">A reader of the blend sees its recipe; the blend cannot pass as a single constituent; a source that has departed is still credited.</td>
<td valign="top"><code>qrme/<wbr>composite.py</code> — <code>test_<wbr>spec_<wbr>mined.py</code>,<br><code>test_<wbr>the_<wbr>last_<wbr>doors.py</code>,<br><code>test_<wbr>overlays.py</code></td>
</tr>
<tr>
<td valign="top">7</td>
<td valign="top">A model asked to simulate a person's decisions answers with the same confidence whether it has a year of evidence or none.</td>
<td valign="top">The simulation's confidence is <strong>computed from the volume of real conditioning evidence</strong> (source items, remembered turns, the latent embedding) rather than from the model's output, and the narrative is watermarked and excluded from distribution.</td>
<td valign="top">A simulation of a thinly-documented person is shown as guesswork; the score moves only when evidence does.</td>
<td valign="top"><code>qrme/<wbr>simulation.py</code> — <code>test_<wbr>spec_<wbr>mined.py</code>,<br><code>test_<wbr>the_<wbr>last_<wbr>doors.py</code></td>
</tr>
<tr>
<td valign="top">8</td>
<td valign="top">Replies are conditioned on who a person is, not where they are or what they are doing, so a reply is the same at a desk and on a mountain.</td>
<td valign="top">Each interaction carries an <strong>environment payload</strong> (location, conditions, local time, activity) stored beside the biometric context and rendered into the inference conditioning.</td>
<td valign="top">The same question gets a different answer at night in the rain than at noon at a desk, and the record shows why.</td>
<td valign="top"><code>qrme/<wbr>attention.py</code>,<br><code>qrme/<wbr>wearables.py</code>,<br><code>environment_<wbr>context</code> — <code>test_<wbr>the_<wbr>room_<wbr>is_<wbr>remembered.py</code>,<br><code>test_<wbr>the_<wbr>wearable_<wbr>tells_<wbr>the_<wbr>guardian.py</code></td>
</tr>
<tr>
<td valign="top">9</td>
<td valign="top">Money raised on a profile has no stated destination until somebody is asked, and control of the profile at the owner's death depends on a status flag anyone with the database can flip.</td>
<td valign="top">Proceeds are <strong>routed in advance to named designees whose shares must sum to 100</strong>, each donation split at the door in integer cents onto an auditable ledger; succession is enforced by <strong>token lifecycle</strong> — the old credential revoked and a new one minted for the named successor on a verified attestation.</td>
<td valign="top">A campaign cannot open without a destination; a split is arithmetic on the ledger, not a promise; the successor holds a credential the predecessor's cannot forge.</td>
<td valign="top"><code>qrme/<wbr>campaigns.py</code>,<br><code>qrme/<wbr>ledger.py</code>,<br><code>qrme/<wbr>signatures.py</code> — <code>test_<wbr>campaigns.py</code>,<br><code>test_<wbr>signatures.py</code>,<br><code>test_<wbr>the_<wbr>keys_<wbr>the_<wbr>till_<wbr>and_<wbr>the_<wbr>lifeline.py</code>,<br><code>test_<wbr>memorial.py</code></td>
</tr>
<tr>
<td valign="top">10</td>
<td valign="top">Several agents working one goal either share every data source or cannot coordinate at all.</td>
<td valign="top">Departments are staffed with role-specific agents whose data pulls are scoped by <strong>independently revocable grants</strong>; one goal fans out across departments, each agent contributing from its own scoped material, the initiating agent composing the joint plan, and the record sealed to the vault.</td>
<td valign="top">Revoking one department's grant stops that department's contribution and nothing else; the plan names which department contributed what.</td>
<td valign="top"><code>qrme/<wbr>organization.py</code>,<br><code>qrme/<wbr>delegation.py</code>,<br><code>qrme/<wbr>company.py</code> — <code>test_<wbr>organizations.py</code>,<br><code>test_<wbr>delegation.py</code>,<br><code>test_<wbr>a_<wbr>company_<wbr>is_<wbr>hired_<wbr>one_<wbr>interview_<wbr>at_<wbr>a_<wbr>time.py</code></td>
</tr>
</tbody>
</table>

## Where each highlight is proven

Each row: the technical problem, the implementation with its own numbers, the test that holds it, and the photograph.

| Highlight | The technical problem | As built, with its numbers | Test | Screen |
|---|---|---|---|---|
| Offline is enforced at every socket | A privacy promise made in prose leaks through one forgotten HTTP call. | `qrme/offline.py` replaces the socket layer's connect with a refusal for every non-loopback address while the offline gate is up; no module opts in, so none can opt out. | `test_nothing_leaves_the_host.py`, `test_offline.py` | — |
| The room society: nine seats that take turns | Several synthetic speakers in one room talk over each other, or one never speaks. | `qrme/society.py` holds up to nine seats and a turn order; `qrme/roomface.py` draws each seat's face and light; a turn is a row the console polls. | `test_the_room_becomes_a_society.py`, `test_the_room_speaks_for_itself.py` | 175 |
| The room hears, reads, shares and remembers | A room that only takes typed text is a chat with pictures of people in it. | `qrme/roomreach.py` accepts speech, files and links per turn; `qrme/sharing.py` keeps what was shared as rows the room re-reads; the transcript is remembered to the vault. | `test_the_room_hears_you_without_being_asked.py`, `test_the_room_shares.py`, `test_the_room_is_remembered.py` | 175, 83 |
| The stage: flat, AR, and VR on every headset | One room drawn three ways by three code paths drifts three ways. | `qrme/xr.py` publishes one scene description; the console draws it flat, overlaid (AR) or entered (VR) from the same rows; WebXR gates only the headset door. | `test_the_rooms_reach_every_headset.py` | 106, 109, 209 |
| Video generation, bounded and watermarked | A reply rendered as footage costs real money per second and carries nothing that says a machine made it. | `qrme/filming.py` caps a render at `MAX_SECONDS = 30` and a direction at `MAX_DIRECTION = 600` characters, stamps every frame set with the profile's watermark, and lets the owner pick the company (`docker/film`). | `test_the_room_films_its_turns.py`, `test_the_owner_picks_the_video_company.py`, `test_the_video_door_is_open.py` | 209, Real output |
| The AI badge is the outermost layer, and a download is burned | A badge drawn by the page is not in the file; a badge in the file cannot be the page's outermost layer. | Two badges: the console draws `.rs-film-ai` over the player and over the full-screen takeover with the player's own full-screen and download switched off; `qrme/badge.py` burns the same badge into the pixels for `GET /media/{id}/download` — Pillow for pictures, ffmpeg for footage, `MARGIN = 12` px from the top-left, never on an authentic upload, refused (503) where footage cannot be burned. | `test_the_badge_is_the_outermost_layer.py` | 209 |
| Voiceprints under attestation | A cloned voice with no record of consent is a cloned voice with no owner. | `qrme/voiceprint.py` refuses enrollment without a granted consent row, reports readiness as counted samples and seconds, and marks every utterance. | `test_voiceprint.py` | 147 |
| The recoverable watermark | Text leaves the platform as plain characters; nothing in it says who produced it. | `qrme/watermark.py` stamps each approved render with a credential derived from the producing profile (`stamp`) and answers `lookup` from the text alone — no database of copies, the mark is in the bytes. | `test_watermark.py`, `test_watermark_recovery.py` | 148 |
| Avatars, the registry and the stage | A face built from a portrait must be the same face in the bubble, the room and full screen, and must say it is synthetic. | `qrme/avatarforge.py` builds face, torso and `.glb` from one portrait; `qrme/avatarreg.py` is the registry every surface reads; the stage marks the figure `✦ AI` in its own pixels. | `test_avatars.py`, `test_the_avatar_registry.py`, `test_the_avatar_takes_the_screen.py` | 44, 205 |
| The Company Builder | A staffed digital company built by hand is a pile of unrelated profiles. | `qrme/company.py` founds a company, opens seats, drafts each interview, and signs a hire into a department under the founder's account. | `test_a_company_is_hired_one_interview_at_a_time.py` | 210, 146 |
| The marketplace and the shops | A listing and a desk are different things that one table would collapse. | `qrme/marketplace.py` lists and licenses profiles; `qrme/shops.py` keeps a shop as its own row with its own hours, never a desk. | `test_marketplace_cards.py`, `test_marketplace_search.py`, `test_a_shop_is_not_a_desk.py` | 152, 187 |
| The bodies a profile may bind | A profile that can drive any robot can drive the wrong one. | `qrme/robotics.py` keeps an allowlist of commands per model and a learned-task list per robot; the wrist's quick ring is the intersection. | `test_the_body_market.py` | 163 |
| Wearables that pair and never listen | A paired watch that carries readings through the platform makes the platform a health record. | `qrme/wearables.py` stores only the deposit address the owner chose; readings go from the device's app to the guardian directly; a device that senses nothing is refused a guardian. | `test_wearables.py`, `test_two_microphones_two_destinations.py` | faces 01–11 |
| The Studio agent and widgets in a box | A widget written by a model runs in the page that holds the owner's session. | `qrme/widgets.py` serves each widget in its own sandboxed frame with no ambient credential; `qrme/authoring.py` keeps the draft and the published copy apart. | `test_the_widget_cannot_leave_its_box.py` | 200 |
| A profile's own mailbox, answering in its profession | Mail to a synthetic professional either goes unanswered or is answered by a generic assistant. | `qrme/mailbox.py` receives mail on the profile's own address and answers in the profile's persona, with the owner's moderation queue in front of every send. | `test_the_profiles_own_mailbox.py` | My Corner |
| The model menu by region | One global provider list is wrong somewhere in the world. | `qrme/loadouts.py` publishes a provider menu per region with an American taper lever; the console draws the region's menu and nothing else. | `test_the_region_loadouts.py` | Settings |
| The feed ranks by relationship, and popularity is capped | An uncapped like count lets one loud stranger outrank every friend. | `qrme/wall.py` scores a post with `W_FRIEND = 100`, `W_TALKED = 60`, `W_TAG = 25`, and `W_LIKES = 2` per like capped at `W_LIKES_CAP = 40`; every entry carries the reason it is there. | `test_wall.py` | 186, 189 |
| Moderation before a doubtful turn ships | A reply the owner would not have signed leaves before anyone sees it. | `qrme/moderation.py` holds a doubtful turn as a pending message the owner approves or rejects; the pass rate is a computed number on the front page. | `test_moderation.py` | 32 |
| Signatures that survive dispute | A signature over a document's name is not a signature over the document. | `qrme/signatures.py` signs the bytes and records the hash, the signer and the time; a changed byte is a failed verification. | `test_a_signature_over_the_bytes.py` | 112, 113 |
| A person settles it, signed in or not | A complaint that needs an account cannot be made by the person locked out of one. | `qrme/matters.py` accepts a matter from the front door with no session and hands it to a person; the reply reaches the address given. | — | 203 |

