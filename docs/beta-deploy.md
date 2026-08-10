# Standing the beta up

**Status: written, never yet run.** The compose file and proxy config were
built by reading the three Dockerfiles and the existing test harness, and
nothing here has met a real host. The first run will find something. Where a
step is a guess rather than a fact, it says so.

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

Five of these are generated and never seen again; one you paste. All of them
live in exactly one file, which never enters git.

```bash
cd /srv/qrme
umask 077
cat > .env <<EOF
# --- generated ---------------------------------------------------------
PDI_MASTER_KEY=$(openssl rand -base64 32)
PDI_ADMIN_TOKEN=$(openssl rand -hex 24)
QRME_SIGNUP_KEY=$(openssl rand -base64 24)
JIM_SIGNUP_KEY=$(openssl rand -base64 24)
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

Nothing in the compose file has a default for any of these. Each one is
`${VAR:?}`, so a missing value stops the stack with the variable's name
rather than starting it quietly degraded.

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

SQLite files on named volumes. They survive a redeploy; they do not survive
the volume being removed, and nothing here copies them anywhere else.

```bash
docker run --rm -v qrme_pdi-data:/d -v /root/backups:/b alpine \
  sh -c 'cp /d/pdi.db /b/pdi-$(date +%F).db'
```

Same shape for `qrme-data` and `jim-data`. Put it in `cron`. This is the
step most likely to be skipped and most expensive to have skipped.

---

## What this is not

Stated plainly, so nobody infers otherwise:

- **`bootstrap` is not idempotent.** It mints tenants on every `up`, so a
  restart creates a second tenant rather than reusing the first. The newest
  token is the one the services source, so it works — but old tenants
  accumulate, and that is a real thing to fix before this stops being a
  beta.
- **No backups are configured.** Section 6 is instructions, not a running
  job.
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
