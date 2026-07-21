"""Full-stack end-to-end flow against the three **booted** services over HTTP.

Unlike the in-process tandem tests (which wire the apps together in one
process), this boots PDI, QRME, and JIM as separate containers on one network
and drives a real cross-service flow across the HTTP seams:

    PDI      seal → read → audit verify           (the vault stands alone)
    QRME     create a specialist profile, chat    (profiles answer)
    JIM      enroll → monitor → detect →          (guardian delegates to the
             delegate to the QRME specialist       real QRME over HTTP)
    erase    JIM /data + QRME profile             (right to be forgotten)

Exit non-zero on the first failed assertion; the compose harness uses this
container's exit code as the CI verdict.
"""

import json
import os
import sys
import urllib.error
import urllib.request

QRME = os.environ.get("QRME_URL", "http://qrme:8000")
JIM = os.environ.get("JIM_URL", "http://jim:8200")
PDI = os.environ.get("PDI_URL", "http://pdi:8100")


def call(base: str, method: str, path: str, body=None, token=None):
    headers = {"content-type": "application/json"}
    if token:
        headers["authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(base + path, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            raw = r.read()
            return r.status, (json.loads(raw) if raw else None)
    except urllib.error.HTTPError as e:
        raw = e.read()
        return e.code, (json.loads(raw) if raw else None)


def check(label: str, cond: bool, detail="") -> None:
    print(f"  {'OK ' if cond else 'FAIL'}  {label}" + (f"  — {detail}" if detail else ""),
          flush=True)
    if not cond:
        sys.exit(1)


def main() -> None:
    print("== PDI: vault stands alone ==", flush=True)
    st, tenant = call(PDI, "POST", "/tenants", {"name": "e2e", "retention": "forever"})
    check("create tenant", st == 201, str(st))
    tok = tenant["token"]
    st, _ = call(PDI, "PUT", "/records", {"key": "e2e/secret", "value": "hunter2"}, tok)
    check("seal record", st == 200, str(st))
    st, rec = call(PDI, "GET", "/records/e2e/secret", token=tok)
    check("read decrypts", st == 200 and rec["value"] == "hunter2")
    st, v = call(PDI, "GET", "/audit/verify", token=tok)
    check("audit chain intact", st == 200 and v["intact"] is True)

    print("== QRME: a specialist profile answers ==", flush=True)
    st, prof = call(QRME, "POST", "/profiles", {
        "owner_id": "e2e", "kind": "self", "display_name": "Dr. Calm",
        "persona": "A steady, reassuring guide for anxiety.",
        "verification": {"birthdate": "1980-01-01"}, "purpose": "companion_coach"})
    check("create profile", st in (200, 201), str(st))
    profile_id, owner_token = prof["id"], prof["owner_token"]
    st, inter = call(QRME, "POST", "/interactors",
                     {"display_name": "Sam", "birthdate": "1990-05-05"})
    check("create interactor", st in (200, 201), str(st))
    st, chat = call(QRME, "POST", f"/profiles/{profile_id}/chat",
                    {"interactor_id": inter["id"], "message": "hello"})
    check("profile chats over HTTP", st == 200, str(st))

    print("== JIM: guardian delegates to the real QRME specialist ==", flush=True)
    st, _ = call(JIM, "POST", "/specialists", {
        "condition": "anxiety", "mode": "tandem", "qrme_profile_id": profile_id})
    check("register tandem specialist", st in (200, 201), str(st))
    st, user = call(JIM, "POST", "/enroll", {
        "display_name": "Sam", "birthdate": "1990-05-05", "terms_consent": True})
    check("enroll user", st == 201, str(st))
    uid, utok = user["id"], user["user_token"]
    st, mon = call(JIM, "POST", f"/monitor/{uid}", {
        "heart_rate": 120, "respiratory_rate": 22, "note": "my chest is tight"},
        token=utok)
    check("monitor detects + delegates", st == 200, str(st))
    g = (mon or {}).get("guidance", {})
    check("guidance came from the QRME tandem seam",
          g.get("source") == "tandem" and g.get("qrme_profile_id") == profile_id,
          json.dumps(g))

    print("== erase: right to be forgotten ==", flush=True)
    st, _ = call(JIM, "DELETE", f"/data/{uid}", token=utok)
    check("erase JIM user", st in (200, 204), str(st))
    st, _ = call(QRME, "DELETE", f"/profiles/{profile_id}", token=owner_token)
    check("erase QRME profile", st in (200, 204), str(st))
    st, _ = call(QRME, "GET", f"/profiles/{profile_id}")
    check("QRME profile is gone", st == 404, str(st))

    print("\nfull-stack end-to-end flow PASSED", flush=True)


if __name__ == "__main__":
    main()
