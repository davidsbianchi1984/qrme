# Deploying the Cloud Model Gateway

**Status: verified locally, never yet deployed.** The gateway was built, run,
and driven end to end in a sandbox — every route, every refusal, and the
fail-closed defaults — but no host has been chosen, so nothing here has met a
real certificate or a real client. Where that matters, it is said in place.

`cloudgw/` is a separate image from the QRME app on purpose. It is the one
component several deployments share — it serves the greater model, takes
contributions, and receives the content-free error reports — so it has a
different lifecycle, a different blast radius, and no reason to carry a Node
toolchain or a studio build.

---

## What was verified, and what was not

Driven against a running instance:

* Boots, and the banner names **every** unconfigured gap out loud rather than
  starting quietly degraded.
* Well-formed reports accepted (`202`), counters incremented, two products.
* Four leak classes refused whole with actionable `422`s: a message body on a
  problem, an un-redacted profile id in the route, a timestamp where a day
  belongs, an unknown product.
* The aggregate is counters only — `op`, `status`, `count`, `day`,
  `fingerprint`. Nothing readable.
* Disk persistence at `CLOUDGW_PROBLEMS_PATH`, written atomically.
* Token scopes are separate: the posting token gets **403** on `GET`, and only
  names in `CLOUDGW_PROBLEM_READERS` may read.
* **Fail-closed confirmed.** With no `CLOUDGW_TOKENS`, loopback gets
  200/202/200 and the wire gets 200 on `/health` but **503 on both
  `/v1/problems` routes**.

Not verified: **the image build itself.** There is no Docker daemon in the
sandbox this was written in, so `python -m cloudgw` was run directly. The
image layer is thin — pip install, `COPY`, a non-root user, a healthcheck —
but thin is not the same as tested.

---

## 0. Choose the hostname

Everything below uses `gw.example.com`. Substitute yours.

## 1. A host

The smallest VPS any provider sells is enough: this is a thin FastAPI process,
and `/v1/generate` only proxies to Anthropic. 1 GB of RAM is comfortable.

## 2. DNS

One `A` record for the subdomain, pointing at the host. **Confirm it resolves
before going on** — the reverse proxy cannot obtain a certificate until it
does:

```bash
dig +short gw.example.com
```

## 3. Docker on the host

```bash
apt-get update && apt-get install -y ca-certificates curl git
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" \
  > /etc/apt/sources.list.d/docker.list
apt-get update && apt-get install -y docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin

ufw allow 22/tcp && ufw allow 80/tcp && ufw allow 443/tcp && ufw --force enable
```

## 4. The code

A **read-only** deploy key, so the host can fetch and nothing else:

```bash
ssh-keygen -t ed25519 -C "cloudgw deploy" -f /root/.ssh/qrme_deploy -N ""
cat /root/.ssh/qrme_deploy.pub     # add under Settings → Deploy keys, write access OFF
cat >> /root/.ssh/config <<'EOF'
Host github.com
  IdentityFile /root/.ssh/qrme_deploy
  IdentitiesOnly yes
EOF
git clone git@github.com:davidsbianchi1984/qrme.git /srv/qrme
```

## 5. Compose, proxy, secrets

`/srv/qrme/Caddyfile`:

```
gw.example.com {
    reverse_proxy cloudgw:8300
}
```

`/srv/qrme/cloudgw-compose.yml`:

```yaml
services:
  cloudgw:
    build:
      context: .
      dockerfile: cloudgw/Dockerfile
    restart: unless-stopped
    environment:
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:-}
      CLOUDGW_TOKENS: ${CLOUDGW_TOKENS}
      CLOUDGW_PROBLEM_READERS: ops
      CLOUDGW_PROBLEMS_PATH: /data/problems.json
    volumes:
      - cloudgw-data:/data
    expose:
      - "8300"

  caddy:
    image: caddy:2
    restart: unless-stopped
    ports: ["80:80", "443:443"]
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy-data:/data
      - caddy-config:/config

volumes:
  cloudgw-data:
  caddy-data:
  caddy-config:
```

`expose` rather than `ports` on the gateway is deliberate: 8300 is reachable
only by the proxy on the compose network, never from the internet. The gateway
speaks plain HTTP and the consoles post a bearer token, so terminating TLS in
front of it is not optional.

Two tokens, generated on the host and never committed:

```bash
umask 077
cat > /srv/qrme/.env <<EOF
CLOUDGW_TOKENS=consoles:$(openssl rand -hex 24),ops:$(openssl rand -hex 24)
EOF
```

`ANTHROPIC_API_KEY` is only for `/v1/model` and `/v1/generate`. If this box is
purely the error collector, leave it out — the model routes then refuse with a
message saying why, which is the correct behaviour rather than a degraded one.
`CLOUDGW_PDI_URL` / `CLOUDGW_PDI_TOKEN` are likewise absent above, so
`/v1/contributions` refuses: contributions without a vault would be
unencrypted and unauditable, and the store says so instead of accepting them.

## 6. Up

```bash
cd /srv/qrme
docker compose -f cloudgw-compose.yml --env-file .env up -d --build
docker compose -f cloudgw-compose.yml logs cloudgw
```

The banner in those logs naming what is unconfigured is expected and healthy.

## 7. Verify from somewhere else

Not from the host — from a machine that has to cross the internet to reach it,
because that is the path a console takes.

| Check | Expected |
| --- | --- |
| `GET /health`, no credential | `200` |
| `GET /v1/problems` with the **ops** token | `200` |
| `GET /v1/problems` with the **consoles** token | `403` |
| `GET /v1/problems` with no token | `401` |

If the ops token gets `403` and the consoles token `200`, the two are swapped
in `.env`.

## 8. The two build-time variables

This is the point of the box. `app/vite.config.ts` bakes the address into the
bundle, and **unset means an installer with nowhere to send** — which is the
default, and a stronger one than a runtime flag, because there is no address
for a later mistake to switch on.

```bash
PROBLEM_COLLECTOR=https://gw.example.com \
PROBLEM_TOKEN=<the consoles token> \
npm run build
```

Base URL only — `errors.ts` appends `/v1/problems` itself. The same two
variables, the same `consoles` token, in **all three** repositories' console
builds; each stamps its own `__APP_SOURCE__`, so the gateway files them apart.

The native shells read the same pair from their own build systems: an
`Info.plist` key on iOS, a gradle `buildConfigField` on Android, and
`AssemblyMetadata` on Windows — see `native/windows/BuildConfig.cs`.

## 9. Keep the secrets

Both tokens belong in a password manager, labelled. The `consoles` one is
compiled into every installer you ship; the `ops` one is the only way to read
the aggregate.

---

## What this buys, and what it does not

**Buys:** rows like `qrme · 0.28.0 · win32 · GET /profiles/{id} · 500 · ×3`,
across every client that has an address compiled in. That is the difference
between *somebody said the app is broken* and *this route is failing this
often on this build*.

**Does not buy:** a reproduction. Counters cannot tell you why. There is no
stack trace, no request body, no user — the deliberate consequence of
recording nothing that could identify anybody, and the reason the intake
refuses reports that carry content rather than sanitising them.

It also cannot reach installers already in the field: the address is compiled
in, so the payoff starts at the next release, not on the day the box comes up.
