"""Mint the PDI tenant tokens the QRME and JIM services need to seal records,
and drop them where each service's entrypoint sources them. Runs once, after
PDI is healthy, before QRME/JIM start.

PDI is left in dev-open admin mode in this harness (no PDI_ADMIN_TOKEN), so
tenant creation needs no admin credential — this is a test harness, not a
production deployment.
"""

import json
import os
import urllib.request

PDI = os.environ.get("PDI_URL", "http://pdi:8100")


def _post(path: str, body: dict) -> dict:
    req = urllib.request.Request(
        PDI + path, data=json.dumps(body).encode(),
        headers={"content-type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.load(r)


def main() -> None:
    qrme_token = _post("/tenants", {"name": "qrme", "retention": "forever"})["token"]
    jim_token = _post("/tenants", {"name": "jim-mini", "retention": "forever"})["token"]
    with open("/shared/qrme.env", "w") as f:
        f.write(f"export QRME_PDI_TOKEN={qrme_token}\n")
    with open("/shared/jim.env", "w") as f:
        f.write(f"export JIM_PDI_TOKEN={jim_token}\n")
    print("bootstrap: minted PDI tenant tokens for qrme + jim-mini", flush=True)


if __name__ == "__main__":
    main()
