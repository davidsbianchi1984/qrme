"""Mint the PDI tenant tokens the QRME and JIM services need to seal records,
and drop them where each service's entrypoint sources them. Runs once, after
PDI is healthy, before QRME/JIM start.

PDI's dev-open admin mode is open only to callers on the same machine, and a
container on the compose network is not that — it reaches PDI over a routable
address, where PDI fails closed rather than leave tenant creation and token
issuance open to anything that finds it. So the harness configures an admin
token like a real deployment does, and this one-shot presents it.

Idempotent by validation rather than by flag. The first version minted on
every `up`, so each restart abandoned a tenant and its sealed records and
started a new one — invisible until somebody asked where last week's records
went. A marker file would say minting *ran*; what matters is that the token
*works*, so each saved token is presented to PDI and kept if PDI honours it.
A wiped PDI volume with a surviving shared volume — or the reverse — falls
through to minting, which is the correct answer both times.
"""

import json
import os
import urllib.error
import urllib.request

PDI = os.environ.get("PDI_URL", "http://pdi:8100")
ADMIN = os.environ.get("PDI_ADMIN_TOKEN", "")


def _post(path: str, body: dict) -> dict:
    headers = {"content-type": "application/json"}
    if ADMIN:
        headers["authorization"] = f"Bearer {ADMIN}"
    req = urllib.request.Request(
        PDI + path, data=json.dumps(body).encode(),
        headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.load(r)


def _saved_token(path: str, var: str) -> str:
    """The token a previous run wrote, or empty."""
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line.startswith(f"export {var}="):
                    return line.split("=", 1)[1]
    except OSError:
        pass
    return ""


def _honoured(token: str) -> bool:
    """Does PDI still accept this tenant token? Read-only on purpose."""
    if not token:
        return False
    req = urllib.request.Request(
        PDI + "/records", headers={"authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status == 200
    except (urllib.error.URLError, OSError):
        return False


def _ensure(name: str, path: str, var: str) -> None:
    kept = _saved_token(path, var)
    if _honoured(kept):
        print(f"bootstrap: kept {name}'s existing PDI tenant token",
              flush=True)
        return
    token = _post("/tenants", {"name": name, "retention": "forever"})["token"]
    with open(path, "w") as f:
        f.write(f"export {var}={token}\n")
    print(f"bootstrap: minted a PDI tenant token for {name}", flush=True)


def main() -> None:
    _ensure("qrme", "/shared/qrme.env", "QRME_PDI_TOKEN")
    _ensure("jim-mini", "/shared/jim.env", "JIM_PDI_TOKEN")


if __name__ == "__main__":
    main()
