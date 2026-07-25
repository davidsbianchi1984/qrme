# Hosting QRME

Run it yourself, or let someone run it for you. This document covers the
second case honestly — what changes when a deployment is reachable from
outside your own network, and what an operator holding other people's
profiles has to settle first.

For the local flow (laptop, phone on the same Wi-Fi), see **Run it on your
phone** in the [README](../README.md); nothing here is needed for that.

## The two postures

| | Local | Published |
|---|---|---|
| Reached by | this machine and the LAN | anyone with the URL |
| Pairing advertises | the machine's LAN address | `QRME_PUBLIC_URL` |
| Who can create a profile | anyone who can reach it | holders of `QRME_SIGNUP_KEY` |
| Transport | plain HTTP is fine on your own wire | **HTTPS, always** |

The local defaults are deliberate: on your own network, reaching the API
already means being in the house. Publishing changes that, so publishing
requires the two variables below.

## Deploying

The `Dockerfile` builds the studio and the API into one image, so the UI is
served from the same origin as the API — that's what lets a phone use it
with nothing to configure.

```bash
docker build -t qrme .
docker run -p 8000:8000 -v qrme-data:/data \
  -e QRME_PUBLIC_URL=https://qrme.example.com \
  -e QRME_SIGNUP_KEY="$(openssl rand -base64 24)" \
  qrme
```

It honours `$PORT`, so container platforms that assign one work unchanged.
The database lives on the `/data` volume — **mount it**, or a restart is a
data-loss event. The container runs as a non-root user and reports health at
`/health`.

Shared cPanel-style hosting (the kind sold for PHP sites) is a poor fit: this
is a long-running ASGI process, not a request-per-script runtime. A small VPS
or any container platform is the right shape.

### Required when published

| Variable | Why |
|---|---|
| `QRME_PUBLIC_URL` | `GET /pair` advertises this address, so the QR a phone scans points somewhere it can actually reach. |
| `QRME_SIGNUP_KEY` | Without it, anyone who finds the URL can create profiles on your deployment. Give the key to the people who should have accounts. |

### TLS is not optional

Owner and interactor tokens travel in the `Authorization` header. Terminate
TLS at a reverse proxy or at the platform — the app does not do it. Over
plain HTTP on a network you don't control, a token is readable in transit and
a stolen token is that profile.

## If you host for other people

Running profiles that belong to someone else is a different undertaking from
running your own:

- **The Terms of Service** ([docs/terms.md](terms.md)) are written for the
  operator relationship — liability cap, warranty disclaimer, and the
  creator-responsibility clauses. Have counsel review them before you take
  someone else's data, and set the governing-law placeholder.
- **Encryption at rest belongs to PDI.** QRME's own database is not
  encrypted; sealing source material requires the PDI tandem
  (`QRME_PDI_URL` + `QRME_PDI_TOKEN`). If you hold other people's profiles,
  read PDI's key-custody table in its `docs/operations.md` — particularly
  that the KMS/HSM provider is an integration seam, not a finished control.
- **Erasure has to actually work.** `DELETE /profiles/{id}` purges local rows
  and vaulted copies. Test it on your deployment before promising it.

## What this does not give you

Stated plainly, so nobody infers otherwise:

- **No multi-tenancy.** One deployment is one trust boundary; profiles on it
  are isolated by capability tokens, not by tenant. Separate customers means
  separate deployments.
- **No rate limiting or abuse controls.** Put them at the proxy.
- **No backups.** Snapshot the `/data` volume on whatever schedule your
  promises to users require.
