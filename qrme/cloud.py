"""Cloud Model Gateway client — a greater model, and a way to give back.

The local provider stack (Anthropic SDK or the offline stub) always works.
When a Cloud Model Gateway is configured (`QRME_CLOUD_URL` +
`QRME_CLOUD_TOKEN`, or an injected client), QRME can additionally:

- **use a greater model** — inference routes to the gateway's hosted tier
  (the latest, most capable model, e.g. `claude-fable-5`) with automatic
  fallback to the local provider if the gateway is unreachable; and
- **contribute to it** — anonymized material is sent to the gateway's
  contribution intake to improve the shared model. Two kinds, consented two
  different ways, and the difference is worth stating rather than averaging:

  * **a profile's positively-rated exchanges** — strictly opt-in per profile
    (`cloud_contribution`), off until an owner turns it on;
  * **a person's hosted memories** — the free tier's own terms. Hosted
    storage and contribution are one bargain there: the operator keeps the
    words, and they improve the shared model. It is on by default for that
    tier (`interactors.contributes`) because it is what the tier *is*, said
    where it applies rather than buried, and off is one press away.

  A memory sealed in a vault is **never** contributed, whatever any switch
  says. That is the whole of what a private plan buys, and it is enforced by
  posture rather than by the flag: `recollection.contribute` runs only for
  `open_cloud` rows.

  No profile ids, owner ids, interactor ids, or display names ever leave in
  either case. Consent is revocable on both, and revoking reaches backwards:
  the refs are meaningless at the gateway and meaningful only in this
  deployment's `contribution_log`, so an item can be deleted there without
  the gateway ever being told whose it was.

The gateway contract is documented in ``docs/cloud-model.md`` and is shared
by QRME, JIM-mini, and PDI (whose encrypted vault serves as the audited
intake where contribution data is stored).
"""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request


class _Response:
    def __init__(self, status_code: int, body: bytes):
        self.status_code = status_code
        self._body = body

    def json(self):
        return json.loads(self._body) if self._body else None


class _UrllibClient:
    def __init__(self, base_url: str):
        self._base = base_url.rstrip("/")

    def request(self, method, path, json_body=None, headers=None) -> _Response:
        data = json.dumps(json_body).encode() if json_body is not None else None
        h = {"content-type": "application/json"}
        if headers:
            h.update(headers)
        # Offline mode gated this by never *attaching* the client —
        # `api.py` does `app.state.cloud = None if offline.enabled()`. That is
        # a gate on the wiring, not on the way out: anything that builds a
        # client directly, as the tests and the suite gateway do, walks past
        # it.
        #
        #     asked     is the cloud client attached
        #     mattered  can the cloud be reached
        from . import offline
        offline.allow(self._base + path, "the cloud gateway")
        req = urllib.request.Request(
            self._base + path, data=data, method=method, headers=h)
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return _Response(r.status, r.read())
        except urllib.error.HTTPError as e:
            return _Response(e.code, e.read())


class CloudModelClient:
    """HTTP client for the Cloud Model Gateway (see docs/cloud-model.md)."""

    def __init__(self, token: str = "", base_url: str | None = None, client=None):
        self._token = token
        self._client = client
        self._urllib = _UrllibClient(base_url) if base_url else None
        if client is None and base_url is None:
            raise ValueError("CloudModelClient needs base_url or a client")

    def _auth(self):
        return {"Authorization": f"Bearer {self._token}"}

    def _do(self, method, path, body=None):
        if self._client is not None:
            fn = getattr(self._client, method.lower())
            if body is not None:
                return fn(path, json=body, headers=self._auth())
            return fn(path, headers=self._auth())
        return self._urllib.request(method, path, json_body=body,
                                    headers=self._auth())

    def generate(self, system: str, messages: list[dict]) -> dict:
        r = self._do("POST", "/v1/generate",
                     {"system": system, "messages": messages})
        if r.status_code >= 300:
            raise RuntimeError(f"cloud generate failed: {r.status_code}")
        return r.json()   # {"content": ..., "model": ...}

    def model_info(self) -> dict | None:
        try:
            r = self._do("GET", "/v1/model")
            return r.json() if r.status_code < 300 else None
        except Exception:
            return None

    def contribute(self, payload: dict) -> bool:
        r = self._do("POST", "/v1/contributions", payload)
        return r.status_code < 300

    def revoke_contributions(self, refs: list[str]) -> bool:
        """Ask the gateway to delete previously contributed items by their
        opaque refs. The refs carry no identity — only the contributor's local
        log maps them back — so revocation works without deanonymizing."""
        if not refs:
            return True
        try:
            r = self._do("POST", "/v1/contributions/revoke", {"refs": refs})
            return r.status_code < 300
        except Exception:
            return False


logger = logging.getLogger("qrme.cloud")


class CloudProvider:
    """Greater-model inference with automatic local fallback."""

    #: What this wrapper is, in the words a provenance record needs. The
    #: gateway's model is not one of the registry names, so it cannot be
    #: spelled by `resolve_choice` and has to say its own name here.
    GREATER_MODEL = "cloud greater model"

    def __init__(self, client: CloudModelClient, fallback):
        self._client = client
        self._fallback = fallback

    def generate(self, system: str, messages: list[dict]) -> str:
        from . import llm
        try:
            text = self._client.generate(system, messages)["content"].strip()
        except Exception as exc:  # noqa: BLE001 — the gateway never breaks us
            # The gateway being down never breaks the product — but it does
            # change who wrote the answer, and that is the reader's to know.
            # This branch caught the exception and said nothing at all: no
            # record, and unlike its sibling in `llm.FallbackProvider`, not
            # even a log line.
            logger.warning("cloud gateway failed, using local fallback: %s",
                           llm.scrub(exc))
            llm.note_answered_by(llm.LOCAL_FALLBACK,
                                 degraded_from=self.GREATER_MODEL)
            return self._fallback.generate(system, messages)
        llm.note_answered_by(self.GREATER_MODEL)
        return text
