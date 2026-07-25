"""Where contributions land — PDI, as the architecture always said.

docs/cloud-model.md is explicit that the gateway is a *tenant of PDI*: every
contribution is sealed with AES-256-GCM under a ``contributions/`` key and
recorded in the tamper-evident audit chain, so the training corpus is
encrypted at rest, tenant-isolated, and auditable end to end. PDI already
serves that intake (``POST``/``GET``/``DELETE /contributions``); this is the
gateway's side of the wire.

The interesting case is what happens when no vault is configured. A gateway
that quietly wrote contributions to a plain file would be the exact thing the
architecture exists to prevent — an unencrypted, unauditable pile of other
people's data. So an unconfigured gateway **refuses contributions** and keeps
serving inference, which is the half that needs no vault. Never storing is a
better failure than storing badly.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from fastapi import HTTPException


class NoVault:
    """No intake configured: inference works, contributions are refused."""

    configured = False

    def describe(self) -> dict:
        return {"configured": False,
                "note": "no PDI vault configured (CLOUDGW_PDI_URL + "
                        "CLOUDGW_PDI_TOKEN) — contributions are refused "
                        "rather than stored unencrypted"}

    def put(self, source: str, ref: str, payload: dict) -> bool:
        raise HTTPException(
            503, "this gateway has no contribution vault configured. "
                 "Contributions are refused rather than written somewhere "
                 "unencrypted and unauditable; set CLOUDGW_PDI_URL and "
                 "CLOUDGW_PDI_TOKEN (see docs/cloud-model.md).")

    def delete(self, refs: list[str]) -> int:
        return 0


class PDIVault:
    """The real intake. Talks to PDI over HTTP as an ordinary tenant, so the
    gateway gets no privileges the contract does not give every tenant."""

    configured = True

    def __init__(self, base_url: str, token: str, client=None):
        self._base = base_url.rstrip("/")
        self._token = token
        self._client = client            # injected for tests

    def describe(self) -> dict:
        return {"configured": True, "kind": "pdi", "url": self._base}

    def _call(self, method: str, path: str, body=None):
        if self._client is not None:
            fn = getattr(self._client, method.lower())
            headers = {"authorization": f"Bearer {self._token}"}
            return (fn(path, json=body, headers=headers) if body is not None
                    else fn(path, headers=headers))
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(
            self._base + path, data=data, method=method,
            headers={"content-type": "application/json",
                     "authorization": f"Bearer {self._token}"})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return _Resp(r.status, r.read())
        except urllib.error.HTTPError as e:
            return _Resp(e.code, e.read())

    def put(self, source: str, ref: str, payload: dict) -> bool:
        # PDI's ContributionIn takes `payload` as an object, not a JSON
        # string. Sending a string gets a 422 that only shows up against a
        # real PDI — a stub vault accepts either happily.
        r = self._call("POST", "/contributions",
                       {"source": source, "kind": "cloud_contribution",
                        "ref": ref, "payload": payload})
        status = getattr(r, "status_code", 500)
        if status >= 300:
            raise HTTPException(
                502, f"contribution vault refused the write ({status})")
        return True

    def delete(self, refs: list[str]) -> int:
        deleted = 0
        for ref in refs:
            r = self._call("DELETE", f"/contributions/{ref}")
            if getattr(r, "status_code", 500) < 300:
                deleted += 1
        return deleted


class _Resp:
    def __init__(self, status_code: int, body: bytes):
        self.status_code = status_code
        self._body = body

    def json(self):
        return json.loads(self._body) if self._body else None


def vault_from_env():
    url = os.environ.get("CLOUDGW_PDI_URL")
    token = os.environ.get("CLOUDGW_PDI_TOKEN", "")
    return PDIVault(url, token) if url else NoVault()
