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
curl -s https://sntheticprofiles.com/api/models | python3 -c \
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
