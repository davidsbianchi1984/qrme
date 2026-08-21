# Standing the beta up

**Status: run once, for real.** First stood up in August 2026 on a 4 GB VPS
with all four names live. The prediction below — *the first run will find
something* — held: every container came up healthy, certificates issued
themselves, and all three consoles rendered as blank dark pages, because the
nonce Content-Security-Policy meant for the server-rendered pages was also
stamped on the console bundles, whose external scripts no nonce can reach.
Fixed in each product's `pagehead.console_policy`, and the bare domain now
redirects to `/app/`. Where a step below is a guess rather than a fact, it
still says so.

Four containers behind a reverse proxy on one box: the three products, each
serving its own console and API on one origin, plus the shared gateway.

| | | |
|---|---|---|
| `sntheticprofiles.com` | QRME | synthetic profiles |
| `jim-mini.com` | JIM-mini | the health guardian |
| `pdisystems.net` | PDI | the vault |
| `gw.pdisystems.net` | cloudgw | greater model, contributions, error reports |

This is a **beta** topology, not a production one. What that means concretely
is in *What this is not* at the bottom — read it before putting anybody
else's data in.

---

## 0. Before you start

- A host with Docker. 4 GB of RAM is comfortable; the spike is the build,
  not the running.
- All four names resolving to it. `dig +short sntheticprofiles.com` must
  print the host's address before you go on — the proxy cannot obtain a
  certificate for a name that does not point at it.
- An Anthropic API key, typed on the host and nowhere else.

## 1. The three repositories, as siblings

The compose file's build contexts default to this layout:

```bash
mkdir -p /srv && cd /srv
git clone git@github.com:davidsbianchi1984/qrme.git
git clone git@github.com:davidsbianchi1984/jim-mini.git
git clone git@github.com:davidsbianchi1984/pdi.git
```

A read-only deploy key per repository is the right shape — the host needs to
fetch and nothing else. `docs/cloudgw-deploy.md` step 4 has the exact
commands.

Override `QRME_CONTEXT` / `JIM_CONTEXT` / `PDI_CONTEXT` for a different
layout.

## 2. The secrets, generated on the host

Three of these are generated and never seen again; two stay empty while the
beta runs open; one you paste. All of them live in exactly one file, which
never enters git.

```bash
cd /srv/qrme
umask 077
cat > .env <<EOF
# --- generated ---------------------------------------------------------
PDI_MASTER_KEY=$(openssl rand -base64 32)
PDI_ADMIN_TOKEN=$(openssl rand -hex 24)

# --- empty while signup is open ----------------------------------------
# Fill these in (openssl rand -base64 24) when account creation should
# need an invite key; the signup screens start asking for one on the next
# restart, and existing accounts are untouched.
QRME_SIGNUP_KEY=
JIM_SIGNUP_KEY=
CLOUDGW_TOKENS=consoles:$(openssl rand -hex 24),ops:$(openssl rand -hex 24)

# --- the public names --------------------------------------------------
QRME_PUBLIC_URL=https://sntheticprofiles.com
JIM_PUBLIC_URL=https://jim-mini.com
PDI_PUBLIC_URL=https://pdisystems.net

# --- the vault's heartbeat ---------------------------------------------
# Seconds between beats of PDI's in-process pulse: the resident re-runs
# its standing tasks (lookouts, appointments) on this clock. Empty means
# no heartbeat — standing tasks stand still.
PDI_RESIDENT_PULSE=60

# --- yours -------------------------------------------------------------
ANTHROPIC_API_KEY=

# --- optional: the agent's spoken voice ---------------------------------
# From the voice engine's own dashboard. Empty means profiles can bind a
# voice and the say route refuses, naming this variable.
ELEVENLABS_API_KEY=

# --- optional: the vault's real voice (section 8) ------------------------
# Empty means PDI's resident answers with its honest stub and QRME's
# offline provider points at loopback. Section 8 measures the box, picks
# a model, runs the daemon, and fills these in.
PDI_OLLAMA_URL=
PDI_RESIDENT_MODEL=
QRME_OLLAMA_URL=
QRME_OLLAMA_MODEL=
EOF

nano .env      # paste the key on the last line
```

Then **copy the whole file into a password manager.** Two of these are not
recoverable in any useful sense:

- **`PDI_MASTER_KEY`** — whoever holds it can decrypt the vault. Lose it and
  the sealed records are gone; leak it and the sealing meant nothing. PDI's
  own hosting doc puts it plainly: *if the operator sets `PDI_MASTER_KEY`,
  the operator can decrypt.*
- **the `consoles` token** — it gets compiled into every installer you ship.

The signup keys are the one deliberate exception: the compose file defaults
them to empty, and empty means open signup — the beta's posture. Everything
else is `${VAR:?}`, so a missing value stops the stack with the variable's
name rather than starting it quietly degraded.

## 3. Up

```bash
cd /srv/qrme
docker compose -f docker/beta-compose.yml --env-file .env up -d --build
```

First build pulls two base images and installs dependencies for four
services — several minutes, and the one moment RAM matters.

```bash
docker compose -f docker/beta-compose.yml --env-file .env ps
docker compose -f docker/beta-compose.yml --env-file .env logs --tail=40 pdi qrme jim cloudgw
```

**`--env-file .env` is on every one of these, not only on `up`.** Compose
interpolates the whole file before it does anything at all, so a subcommand
that changes nothing needs the values just as much as the one that builds.
And it cannot find them on its own: `.env` is at `/srv/qrme/.env`, while
compose looks for one beside the compose file it was handed — `docker/` —
which is a different directory.

    asked     does the page have the commands
    mattered  do they run in the directory the page put you in

Section 2 makes every variable `${VAR:?}` deliberately, so what comes back is
ten lines naming ten missing variables rather than a stack started quietly
degraded. That is the guard doing its job, and on a read-only subcommand it
reads exactly like a broken deploy — which is how this was found, by running
`ps` against a stack that was already up and answering.

Startup order is enforced rather than hoped for: PDI must report healthy,
then `bootstrap` mints a PDI tenant token for each of QRME and JIM and
writes them where each service's entrypoint sources them, and only then do
the two products start. If `bootstrap` fails, QRME and JIM never start — by
design, because a product that starts without its vault is degraded in a way
its callers cannot see.

## 4. Certificates

Nothing to do. Caddy requests one per name on first request and renews
without being asked. Watch it happen:

```bash
docker compose -f docker/beta-compose.yml --env-file .env logs caddy | grep -i certificate
```

If a name fails, the cause is almost always DNS — that name does not resolve
to this host yet. Fix the record, then restart the one container:

```bash
docker compose -f docker/beta-compose.yml --env-file .env restart caddy
```

Written out rather than abbreviated to `docker compose ... restart caddy`,
for the reason the Windows lines in § 7 are written out: an elided command is
a described command, and the part an ellipsis swallows here is the flag
without which it does not run.

## 5. Check it from somewhere else

From your own machine, not the host — that is the path a tester takes.

| Check | Expected |
|---|---|
| `https://sntheticprofiles.com` | QRME's console |
| `https://jim-mini.com` | JIM's console |
| `https://pdisystems.net` | PDI's console |
| `https://gw.pdisystems.net/health` | `200`, no credential |
| `GET gw.pdisystems.net/v1/problems` with the **ops** token | `200` |
| the same with the **consoles** token | `403` |
| the same with no token | `401` |

If ops gets `403` and consoles `200`, the two are the wrong way round in
`.env`.

### Which model actually answers

A stack can be green on every row above and still answer with the stub —
which reads, on the What If screen, as *no model answered this request*.
The stub is the deployment saying `ANTHROPIC_API_KEY` never reached the
process (or is not a working key), not the feature being broken. Ask the
box itself:

```bash
curl -s https://sntheticprofiles.com/models | python3 -c \
  "import json,sys; d=json.load(sys.stdin); print('default:', d['default'])"
```

`default: anthropic` is the healthy answer. `default: stub` means the key
is missing from `/srv/qrme/.env` or the container came up before it was
added — fix the file, then re-run § 7 so the containers restart with it.
A key that exists but is refused by the provider (spent, revoked) also
lands on the stub; the same check catches it after a key rotation.

## 6. Back up the three databases

Running, not instructions: the `backup` service copies each SQLite file
(via `sqlite3 .backup`, so a mid-write copy cannot ship a corrupt file) and
the collector's ledger into `/root/backups` on the host once a day, and
keeps fourteen days. Check it worked:

```bash
ls -la /root/backups
```

What it does **not** do is leave the machine. A dead disk takes the copies
with it. Downloading `/root/backups` somewhere else now and then — or
pointing a cron job at it from another box — is still a manual step, and
the one that matters in the fire that actually burns.

The loop also writes a freshness marker after every successful pass, and
a loop that died silently is worse than none — it keeps the shape of a
backup while holding yesterday's. Check the marker, not the folder:

```bash
cat /root/backups/.last-ok
```

A date older than a day means the loop is dead: `docker compose -f
docker/beta-compose.yml --env-file .env restart backup`, then look again.

## 6a. The restore drill

A backup you haven't restored from is a belief. Every other failure on
this page costs a redeploy to fix; a dead backup discovered beside a dead
disk costs everything sealed since the beginning, permanently, by design —
envelope encryption means losing `PDI_MASTER_KEY` doesn't degrade the
vault, it deletes it. So the drill proves three things at once, none of
them provable any other way: the dumps restore, the audit chain in them is
intact, and **the password manager's copies of the two unrecoverable
secrets are the real ones** — the drill types them from there, never from
the box's `.env`, because the fire that burns the disk burns the `.env`
with it.

**On the host.** Boot the newest dump in a scratch container on a spare
port. Every command below fits on one short line and is complete on its
own — the first run of this drill was driven from a handheld whose
clipboard broke long lines wherever the chat window had wrapped them,
and a backslash-continued `docker run` arrived as five fragments, four
of them errors. A block that survives being pasted badly is part of
what makes a runbook a runbook.

    asked     do the commands work
    mattered  do they survive the copy

```bash
ssh root@your-host

mkdir -p /root/drill && cd /root/drill
cp "$(ls -t /root/backups/pdi-*.db | head -1)" pdi.db
ls -l pdi.db
IMG=$(docker ps --format '{{.Image}}' --filter name=pdi | head -1)
echo "IMG=$IMG"
```

The two secrets come from the password manager, never from the box's
`.env` — that is the point of the drill. Use the manager's **copy**
button and paste into the silent prompt: the first run tried keying 44
characters of base64 by hand and produced eight different keys in
eight attempts, none of them the key. The silent prompt keeps the
value off the screen, out of the scrollback, and out of any
photograph. Paste these **one at a time**: `read` swallows the next
pasted line as its answer, so pasting them together feeds one prompt
to the other.

```bash
read -rsp 'master key: ' MK; printf %s "$MK" | sha256sum | cut -c1-12
```

```bash
read -rsp 'admin token: ' AT; echo ok
```

The master-key line prints a 12-character fingerprint of what actually
arrived — never the key itself. While the live box still stands, ask
the running vault for the fingerprint of the key *it* operates under,
and compare before booting anything:

```bash
C=$(docker ps --format '{{.Names}}' | grep pdi | grep -v drill)
H='printf %s "$PDI_MASTER_KEY" | sha256sum'
docker exec $C sh -c "$H" | cut -c1-12
```

A mismatch caught here costs a re-paste; the same mismatch discovered
after boot arrives as a decryption error wearing the costume of a dead
backup. And if the pasted value matches *itself* run after run while
still differing from the container's, the drill has found its real
prize: **the escrowed copy is wrong.** Fix it the same day, while the
`.env` still holds the truth, and verify the fix as a closed loop —
copy the key from the `.env` into the manager, copy it *back out of
the manager*, paste it into the master-key prompt, and only a
fingerprint matching the container's counts as repaired. Eyes do not
verify keys; fingerprints do.

The container takes its settings as a file rather than as `-e` flags —
four short lines instead of one long one — and runs as root (`-u 0:0`).
That flag is load-bearing: the image's own unprivileged user cannot
write a root-owned bind mount, and the vault writes on every connection
(`journal_mode=WAL`), so without it every door except `/health` answers
`server_error`. Production never meets this — its named volume is owned
by the image's user — which is exactly the kind of fact only a drill
surfaces.

```bash
echo "PDI_MASTER_KEY=$MK" > drill.env
echo "PDI_ADMIN_TOKEN=$AT" >> drill.env
echo "PDI_DB=/data/pdi.db" >> drill.env
cut -d= -f1 drill.env
V="-v /root/drill:/data --env-file /root/drill/drill.env"
docker run -d -u 0:0 --name pdi-drill -p 8199:8100 $V "$IMG"
sleep 3
curl -s http://localhost:8199/health; echo
```

Three settings and no more — the drill deliberately skips
`PDI_PUBLIC_URL`, which only shapes QR links and whose absence is one
fewer line for a bad paste to lose. The `cut` prints the three setting
*names* — a split paste loses lines, and this catches the loss without
ever printing a value. Health answers a small JSON; an empty answer
means the curl beat the container awake — run that one line again
before deciding anything failed.

Then the three proofs, in order. The chain first — create a drill tenant
(any tenant may verify the whole chain) and walk it end to end:

```bash
U=http://localhost:8199
A="authorization: Bearer $AT"
C='content-type: application/json'
B='{"name":"restore-drill"}'
R=$(curl -s -X POST $U/tenants -H "$A" -H "$C" -d "$B")
echo "$R"
DRILL=$(echo "$R" | sed 's/.*"token":"//;s/".*//')
curl -s $U/audit/verify -H "authorization: Bearer $DRILL"; echo
```

`{"intact": true, ...}` with a non-zero entry count is the chain proof.
Then the key proof — read a record **sealed before today** back through
the drill key. A freshly sealed record round-tripping proves nothing (any
key round-trips with itself); only old data can vouch for the key. The
live QRME tenant's token is in the shared bootstrap volume:

```bash
SV=$(docker volume ls -q | grep shared | head -1)
MP=$(docker volume inspect --format '{{.Mountpoint}}' $SV)
TOK=$(grep 'QRME_PDI_TOKEN=' $MP/qrme.env | cut -d= -f2)
echo ${#TOK}
Q="authorization: Bearer $TOK"
KEY=$(curl -s $U/records -H "$Q" | sed 's/.*"keys":\["//;s/".*//')
echo "KEY=$KEY"
curl -s "$U/records/$KEY" -H "$Q" | head -c 300; echo
```

(`/records` answers `{"keys": [...]}`; the sed takes the first key.
The grep is deliberately unanchored: bootstrap writes the line as
`export QRME_PDI_TOKEN=...` so compose can source the file, and an
anchored grep matches nothing — an empty token here reads as a 401
wearing the drill's clothes. The `echo ${#TOK}` prints the token's
*length*, never the token: a zero means stop and look at the volume,
anything else means proceed.)

A record with a readable `value` is the key proof: the dump decrypted
under the password manager's copy. A decryption error here, with the chain
intact, means the password manager holds the wrong key — **stop and fix
that today**, while the box still has the right one in `.env` to re-copy.
Tear down and log:

```bash
docker rm -f pdi-drill
rm -rf /root/drill
unset MK AT DRILL TOK
```

Write the drill's date next to `PDI_MASTER_KEY` in the password manager.
Run it quarterly, and after any key rotation — the two moments a stale
copy is born.

## 6b. The eyes

The stack carries a rendering sidecar (`docker/renderer`): a real browser
in its own container, one door, `POST /render {url}` answering a page's
text as a person meets it. The vault's `fetch.render` tool asks here —
named by `PDI_RENDERER_URL` in the compose file, topology rather than a
secret — so a lookout pointed at a JavaScript application stops reading
as a title and a dozen characters.

Two boundaries, both enforced inside the sidecar rather than assumed:
the eyes look outward only (private, loopback and stack-internal
addresses are refused for the target *and* for every subresource a page
tries to load), and every render starts a fresh browser — no cookies or
storage bleeding between one tenant's lookout and another's.

A deployment without the sidecar still answers: `fetch.render` falls
back to the plain fetch and the seal says so (`rendered: false`, with
the reason) — an honest shell beats a silent one. To check the eyes are
up after a deploy:

```bash
docker compose -f docker/beta-compose.yml --env-file .env ps renderer
docker compose -f docker/beta-compose.yml --env-file .env logs --tail 3 renderer
```

`ps` proves the container restarts politely; the log tail proves it
booted — the beta host once carried a renderer that had crash-looped
from its first deploy, invisibly, because the check stopped at `ps`.
A healthy tail ends with `Uvicorn running`.

## 6c. The ears

The stack carries a transcription sidecar (`docker/ears`): a local
speech-to-text model in its own container, one door,
`POST /transcribe {url}` answering the words said in a recording — audio
or video, ffmpeg makes one shape of either. The vault's `fetch.listen`
tool asks here, named by `PDI_EARS_URL` in the compose file. The words
are made on this machine: a recording fetched on someone's behalf never
leaves the facility to become text, and the sidecar keeps no copy — the
file is transcribed in a temp directory and deleted with it.

The same outward-only boundary as the eyes: private, loopback and
stack-internal addresses are refused inside the sidecar. Recordings are
capped at 200MB — an errand's size, not an archive's. A second door,
`POST /transcribe-file`, takes bytes already in hand — a video handed to
the briefcase — with the same cap and the same temp-directory custody;
nothing is fetched on that door, so the inward gate has no business on
it.

Unlike the eyes there is no fallback: the bytes of a recording are not
its words, so on a deployment without this sidecar `fetch.listen` fails
in words (the runs ledger carries the reason) rather than sealing
silence. The first build downloads the model weights once
(`base`, ~150MB — override with `EARS_MODEL`); after that the stack
never reaches out for them. To check the ears are up after a deploy:

```bash
docker compose -f docker/beta-compose.yml --env-file .env ps ears
docker compose -f docker/beta-compose.yml --env-file .env logs --tail 3 ears
```

The same two-part check as the eyes: a healthy tail ends with
`Uvicorn running`.

## 7. Updating a running beta

Everything above stands the beta up once. This is the other thing, and it
was missing from this page long enough that the four commands lived only in
a chat message — which is the shape of every other drift this estate keeps
finding in itself.

**On the host.** Sections 0–6 are written for somebody already standing on
the box, and say so in their own way. This section was added later, lifted
out of that chat message, and arrived without the sentence that had been
implicit around it — so it opens on `cd /srv/qrme` with nothing saying whose
machine that is.

    asked     does the page have the commands
    mattered  does it say where to type them

`/srv/qrme` does not exist on a laptop and `docker` is usually not installed
there either, so the first attempt fails twice over with two errors that
each look like a broken deploy rather than a wrong room. It has happened
twice: once before this section existed, and once after — from a handheld,
in PowerShell, against a page that already carried the warning.

    asked     does the page say to get on the host
    mattered  is that line inside the block somebody copies

The second time is the one that changed this text. `ssh` was here, correct,
in a fenced block of its own above the deploy — and a block of its own is a
block you can skip. What gets pasted is the thing that looks like the
procedure, and the procedure looked like the four lines below it. So the
`ssh` is now the first line of that block rather than a preamble to it:

```bash
ssh root@your-host

cd /srv/qrme     && git pull --ff-only
cd /srv/jim-mini && git pull --ff-only
cd /srv/pdi      && git pull --ff-only

cd /srv/qrme
docker compose -f docker/beta-compose.yml --env-file .env up -d --build
```

All three, every time, even for a release that changed only one of them —
the version guard in each console compares itself against the backend
answering the port, and a box carrying two versions reports the mismatch to
whoever is using it rather than to you.

There is no migration step and there is not meant to be one. Each product
runs its schema on connect with `CREATE TABLE IF NOT EXISTS`, and columns
added to tables somebody already has are applied there too, so a table
added in a release appears the first time the new code opens the file. The
databases live in named volumes and the rebuild does not touch them.

Then check what actually answers **from your own machine** rather than the
host — that is the path a visitor takes, and `/health` carries the version
for exactly this.

    asked     does the page say to leave the host
    mattered  can the reader actually get there

**Open a new terminal window on your own machine.** Not `exit` — a new
window. Leave the deploy's window where it is.

That instruction is the third shape this step has had, and the first that
runs. It was a sentence between the blocks, which everybody skipped, and the
checks went in on the host: the one place they prove nothing, because they
answer from inside the network they exist to test from outside. So `exit`
was moved to the first line of the check block, on the reasoning that it was
*the same repair as the `ssh` at the top of the deploy block.*

That reasoning was wrong, and the next deploy proved it in one paste. The
two are not symmetric:

* `ssh host` followed by more lines works, because ssh takes the rest as
  standard input and runs it on the far side;
* `exit` followed by more lines does **not**, because the shell tears down
  and the rest of the pasted text goes into a session that is already
  closing. It echoes, and then it is gone.

    root@ubuntu:/srv/qrme# exit
    curl -s https://sntheticprofiles.com/health;
    echo
    …
    logout
    Connection to 74.208.19.30 closed.

A deploy that had gone perfectly, three checks that never ran, and no error
to say so. The first version made the step easy to skip; the second made it
impossible to perform. A new window is the only shape where the block a
person pastes contains no change of machine at all.

**Then run one of the two blocks below, not both.** They are the same three
checks for two different machines, and which one you want is decided by what
you are sitting at rather than by what you just deployed to.

If your own machine runs a Unix shell:

```bash
curl -s https://sntheticprofiles.com/health; echo
curl -s https://jim-mini.com/health; echo
curl -s https://pdisystems.net/health; echo
```

If your own machine is Windows, in PowerShell:

```powershell
curl.exe -s https://sntheticprofiles.com/health
curl.exe -s https://jim-mini.com/health
curl.exe -s https://pdisystems.net/health
```

If the terminal you use is an SSH client with the connection saved, a new
window may reconnect to the host on its own — mine does. Three browser tabs
at the same three URLs is the same check from the same place, and it is the
one that always works from a phone.

The two blocks are marked as a choice for the same reason. The Windows one
used to read *on Windows, use these instead* and sit where the next step
goes, so a reader working down the page ran the Unix three, saw three health
objects, and then ran the Windows three in the same shell —
`curl.exe: command not found`, three times, after a deploy that had gone
perfectly. An alternative laid out as a sequence is read as a sequence.

The Windows lines are written out rather than described, because describing
them is what failed. This page used to say *add `.exe` to each* — a correct
instruction attached to three lines that also carry `; echo`, which is the
half it did not mention. `echo` in PowerShell is `Write-Output`, and `Write-
Output` at the end of a pipeline with nothing feeding it stops and prompts
for input:

    cmdlet Write-Output at command pipeline position 1
    Supply values for the following parameters:

So a reader who followed the instruction exactly still got an error, after
a deploy that had gone perfectly — and the error names a cmdlet nobody
typed. Bare `curl` is worse and quieter about it: PowerShell aliases it to
`Invoke-WebRequest`, which has no `-s`, reads `https:` as a drive letter,
and reports *a drive with the name 'https' does not exist*.

    asked     does the page name the Windows form
    mattered  is the Windows form something you can paste

Real `curl` prints the body and PowerShell adds the newline itself, so the
`; echo` the Unix lines need has nothing to do here.

Three self-contained lines rather than a loop, and that is the whole
reason they look like this. The loop this replaces was three lines of
`for … do … done`, which is correct in a terminal and *breaks* when it is
pasted into a phone: the client wraps it, bash sees an incomplete
pipeline, and you get `syntax error near unexpected token` twice with no
hint that the deploy above it went perfectly. It happened on the first
deploy after this page was written. Each line here survives being pasted
one at a time, on a keyboard held in one hand, which is where a deploy
actually gets checked.

Each prints that product's whole health object; the field to read is
`"version":"…"`, and all three should carry the version you just
deployed. A name still reporting the old one is a container that did not
rebuild, not a slow rollout — there is one host and nothing behind it to
lag.

`jq -r .version` will trim it to the number alone if the host has `jq`,
but it is not worth a second line in this file: the object is short, and
the other fields in it — `console`, `pdi`, `tandem`, `signup_key` — are
worth a glance while you are looking anyway.

---

## 8. The vault's real voice — a local model on the box

PDI's resident engine plans, fetches, tabulates and searches without a
model, and answers generation with an honest stub that says so. QRME's
offline provider points at loopback and refuses honestly when nothing
listens. This section is the opt-in that upgrades both: one Ollama daemon
on the stack's own network, one pulled model, four `.env` lines.

Opt-in **by capacity**, which is why it starts with a measurement instead
of an instruction. This estate's box is the 4 GB VPS from the top of this
page, so its row in the table below is the smallest one — but the table is
the decision, so a bigger box someday changes the answer without changing
the page.

### 8a. Measure the box

```
free -h
```

```
nproc
```

Read the `available` column of `free -h` — not `free`; Linux lends spare
RAM to caches and takes it back — and pick the row you can afford **while
the stack is running**:

| `available` RAM | model to pull | what to expect |
|---|---|---|
| under 2 GiB | none — stop here | the stub is the honest answer for this box; a model that sends the host into swap takes the whole beta down with it |
| 2–4 GiB | `llama3.2:1b` | short answers in seconds on 2 vCPUs; the 4 GB VPS's row |
| 4–8 GiB | `llama3.2` (3B) | PDI's coded default; noticeably better prose, noticeably slower |
| 8 GiB and up | `qwen2.5:7b` | a real assistant's answers, at CPU patience |

CPU-only arithmetic, so nobody is surprised: a 1B model on two vCPUs
writes a few words a second; a 7B model writes a word a second on a good
day. The resident reads its answers into sealed records rather than a
person's waiting eyes, which is why patience is acceptable here at all.

### 8b. The daemon, on the stack's own network

The stack's containers are named `docker-…-1`, so its network is
`docker_default` — confirm rather than trust, because a renamed project
renames the network:

```
docker network ls
```

Then run the daemon beside the stack, its weights in a named volume:

```
docker run -d --name ollama --restart unless-stopped --network docker_default -v ollama:/root/.ollama ollama/ollama
```

Pull the model the table picked (the 4 GB row shown; substitute yours):

```
docker exec ollama ollama pull llama3.2:1b
```

The pull is the slow part — a gigabyte-scale download into the volume,
once. Prove the daemon holds it:

```
docker exec ollama ollama list
```

No port is published. The daemon is reachable only by name, only from
containers on `docker_default` — the same standing the ears and the eyes
have, and PDI's offline gate resolves that name to a private address and
lets it through even with `PDI_OFFLINE` set, because nothing leaves the
host.

### 8c. Point the stack at it

Open the env file (no photographs while this file is open — it holds the
master key):

```
nano /srv/qrme/.env
```

Fill the four section-8 lines in, model name matching what you pulled:

```
PDI_OLLAMA_URL=http://ollama:11434
```

```
PDI_RESIDENT_MODEL=llama3.2:1b
```

```
QRME_OLLAMA_URL=http://ollama:11434
```

```
QRME_OLLAMA_MODEL=llama3.2:1b
```

An environment change needs a recreate, not a rebuild:

```
cd /srv/qrme && docker compose -f docker/beta-compose.yml --env-file .env up -d pdi qrme
```

### 8d. Prove it end to end

The daemon holding a model was proved in 8b; this proves the products
reach it. The vault now answers this question itself — one authenticated
read of its posture:

```
curl -s -H "Authorization: Bearer $PDI_TOKEN" https://pdisystems.net/resident | python3 -c "import sys,json; print(json.load(sys.stdin)['local_model_standing'])"
```

`{'reachable': True, ..., 'pulled': True, 'note': None}` is the whole
proof: the daemon answered from inside the stack's network, and the
configured model is actually pulled. Anything else, the `note` names the
fix — `ollama pull …` when the daemon answers but the model is missing,
or the container/network to check when it does not answer at all. (An
ask against a dead daemon no longer raises a socket error either — it
answers a sentence under model `local-unreachable`.)

Then prove it as a person would: ask the vault something from its
console (pdisystems.net → ask) — the answer's provenance reads
`local:llama3.2:1b` instead of `stub`. On QRME, the model picker's
offline row stops saying nothing listens.

And prove the box survived it — the measurement from 8a, taken again
under load:

```
free -h
```

If `available` went to nothing and swap grew, the box cannot afford the
row you picked: take the smaller row, or remove the daemon —

```
docker rm -f ollama && docker volume rm ollama
```

— blank the four `.env` lines, recreate `pdi` and `qrme` again, and the
stub resumes telling the truth.

## What this is not

Stated plainly, so nobody infers otherwise:

- **Backups do not leave the host.** The nightly job in section 6 covers a
  bad deploy or a wrong deletion; it does not cover the disk dying.
- **One host, no redundancy.** The box goes down, everything goes down.
- **No log aggregation, no alerting, no metrics.** `docker compose logs` is
  the whole observability story.
- **The error collector reaches nothing already shipped.** Its address is
  compiled into installers at build time, so the payoff starts at the next
  release. See `docs/cloudgw-deploy.md` § 8.
- **Encryption at rest is PDI's, and only for what is sealed into it.**
  QRME's and JIM's own SQLite files are not encrypted. If you are holding
  other people's data, read the *If you host for other people* section of
  each product's `docs/hosting.md` first — particularly that the KMS/HSM
  provider is an integration seam rather than a finished control.

## Where the variables are documented

Not here — in each product's own hosting doc, which is where they are
maintained:

- `docs/hosting.md` (QRME) — `QRME_PUBLIC_URL`, `QRME_SIGNUP_KEY`
- `../jim-mini/docs/hosting.md` — `JIM_PUBLIC_URL`, `JIM_SIGNUP_KEY`
- `../pdi/docs/hosting.md` — `PDI_MASTER_KEY`, `PDI_ADMIN_TOKEN`
- `docs/cloudgw-deploy.md` — `CLOUDGW_TOKENS` and the gateway's own deploy

A second copy of those tables would be a second thing to drift, which is the
defect this estate keeps finding in itself. So this file names the variables
and points at the documents that define them.
