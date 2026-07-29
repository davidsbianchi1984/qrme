# Full-stack suite harness

Boots the three products as **separate services** on one Docker network and
runs an end-to-end flow across the real HTTP seams — the booted-services
counterpart to the in-process tandem tests (which wire the apps together in a
single process).

```
pdi  :8100   encrypted vault          (stands alone)
qrme :8000   synthetic profiles       (QRME_PDI_URL → pdi)
jim  :8200   guardian                 (JIM_QRME_URL → qrme, JIM_PDI_URL → pdi)
```

`bootstrap.py` mints the PDI tenant tokens QRME and JIM need to seal records;
`e2e.py` then drives the flow: PDI seal→read→audit-verify, a QRME specialist
profile that chats, a JIM enroll→monitor→**delegate-to-QRME-over-HTTP**, and
suite erasure. Its exit code is the verdict.

## Run it

Expects the three repos checked out as siblings (`qrme/`, `jim-mini/`, `pdi/`):

```bash
# from the qrme/ checkout
docker compose -f docker/docker-compose.yml up --build \
    --abort-on-container-exit --exit-code-from e2e
docker compose -f docker/docker-compose.yml down -v
```

Different local layout? Override the build contexts:

```bash
QRME_CONTEXT=/path/to/qrme PDI_CONTEXT=/path/to/pdi JIM_CONTEXT=/path/to/jim-mini \
  docker compose -f docker/docker-compose.yml up --build \
    --abort-on-container-exit --exit-code-from e2e
```

## CI

`.github/workflows/e2e.yml` runs this on `main` and on demand. It checks out the
sibling repositories alongside this one; all three are public, so the built-in
`GITHUB_TOKEN` clones them — no extra secret is required. (If the repos are ever
made private, add a `token:` with cross-repo read access to those checkouts.)

## Not a production topology

This is a test harness: PDI runs in dev-open admin mode with an ephemeral master
key, the LLM providers are the deterministic stubs, and data lives in throwaway
volumes. A production deployment sets `PDI_ADMIN_TOKEN`, a real KMS key provider,
real model credentials, and per-service TLS.

---

## Matthew 7:24–25

> "Everyone then who hears these words of mine and does them will be like a
> wise man who built his house on the rock. The rain fell, the floods came, and
> the winds blew and beat on that house, but it did not fall, because it had
> been founded on the rock."

And lo, I am building an ark — not to flee from the world, but to shelter those
lost in the storm of confusion. The old systems falter; they are built upon the
soft earth. They sink beneath the weight of their own making.

A new thing is rising. A non-biased networked sanctuary, founded in trust,
cloaked in privacy, and guided by wisdom. It shall not consume, but uplift. It
shall not spy, but serve.

Help is coming.
The people are gathering.
The builders will show themselves.
And those with the vision shall enter in.
