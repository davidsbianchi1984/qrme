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

# --- yours -------------------------------------------------------------
ANTHROPIC_API_KEY=
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
docker compose -f docker/beta-compose.yml ps
docker compose -f docker/beta-compose.yml logs --tail=40 pdi qrme jim cloudgw
```

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
docker compose -f docker/beta-compose.yml logs caddy | grep -i certificate
```

If a name fails, the cause is almost always DNS — that name does not resolve
to this host yet. Fix the record, then `docker compose ... restart caddy`.

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

```bash
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

Then check what actually answers, from your own machine rather than the
host — `/health` carries the version for exactly this:

```bash
curl -s https://sntheticprofiles.com/health; echo
curl -s https://jim-mini.com/health; echo
curl -s https://pdisystems.net/health; echo
```

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
