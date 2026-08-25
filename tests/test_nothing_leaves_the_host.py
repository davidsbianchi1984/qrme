"""Offline mode said "nothing leaves the host". Three of five paths obeyed.

## The finding

`qrme/offline.py` makes a guarantee in its first paragraph — *"Set
``QRME_OFFLINE=1`` and the platform makes a hard guarantee: **nothing leaves
the host**"* — and `GET /offline/status` reports
`external_transmission_possible: false` so a deployment can prove it.

The guarantee was enforced at three places and asserted at two more:

| Path | Offline mode |
|---|---|
| the model API (`llm.py`) | bypassed |
| the cloud gateway (`cloud.py`) | never attached |
| the sign-in provider (`oauth.py`) | refused |
| **`mailer.py` — SMTP** | **never consulted the flag** |
| **`pdi_client.py` — the vault** | **never consulted the flag** |

    asked     is inference offline
    mattered  is everything that can leave

A verification code is a small thing to send. The address it is sent *to* is a
person's email, handed to a third-party mail server, on a deployment configured
to keep everything on the machine.

The vault is subtler and worse to argue with, because the module's own
docstring already answers it: *"source material lives in the local database or
the on-prem PDI vault"*. That is a sentence about how somebody would deploy it,
written as though it were a property of the code — `QRME_PDI_URL` can point
anywhere. The same held for `llm.py`'s *"Ollama IS offline: it answers on
loopback"*.

## Why the fix is a host check and not a blanket refusal

Offline means *nothing leaves the machine*, not *nothing opens a socket*. The
things this platform legitimately talks to when offline are all on this side of
the wire: Ollama on loopback, an on-prem vault, a webhook on the LAN. Refusing
outright would also have silenced the escalation path in the sibling product,
whose plan-gate refusal promises in nine languages that emergency paths are
never affected.

So `offline.allow(url, what)` refuses a **non-local host**, and the assumptions
the docstrings were already making become the thing the code checks.

## What this file does

The per-call tests below are driven. The structural one is the point: it walks
the package with `ast` and finds every site that can open a connection —
`urlopen`, `smtplib.SMTP`, the Anthropic client — and holds each one to being
inside a function that consults `offline`. A new way out of the host cannot be
added without either gating it or writing down why it does not need gating.
"""

from __future__ import annotations

import ast
import os
from pathlib import Path

import pytest

from qrme import offline

from . import ratchets
import re


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()
PACKAGE = REPO / "qrme"

#: Calls that can put bytes on a wire.
EGRESS = {
    ("urllib", "request", "urlopen"): "urlopen",
    ("smtplib", "SMTP"): "smtplib.SMTP",
    ("smtplib", "SMTP_SSL"): "smtplib.SMTP_SSL",
    ("anthropic", "Anthropic"): "anthropic.Anthropic",
    ("socket", "create_connection"): "socket.create_connection",
    ("socket", "socket"): "socket.socket",
}

#: Modules that open a connection and are exempt, each for a stated reason.
#: Recorded here rather than silently skipped — an exemption somebody has to
#: justify is an exemption somebody will notice.
EXEMPT = {
    "mobile.py": (
        "opens a UDP socket to discover this host's own LAN address and "
        "sends nothing — `connect()` on a datagram socket transmits no "
        "packet. It is how the pairing QR names a reachable URL, which is a "
        "local-network feature and exactly what offline mode is for."),
}


def _gate_calls(fn: ast.AST) -> bool:
    """Does this function actually *call* the gate?

    A call, found by the parser — not the string `offline.allow` appearing
    somewhere in the file. The first version of this searched the module's
    source text, and a comment in `cloud.py` explaining the old wiring
    contained the literal `offline.enabled()`. Deleting the real gate left the
    comment behind, and the check passed.

        asked     does this module mention the gate
        mattered  does this function call it
    """
    for node in ast.walk(fn):
        if not isinstance(node, ast.Call):
            continue
        attr = getattr(node.func, "attr", "")
        base = getattr(getattr(node.func, "value", None), "id", "")
        if base == "offline" and attr in ("allow", "allow_host", "enabled"):
            return True
    return False


def _egress_sites() -> list[tuple[str, int, str, bool]]:
    """Every call in the package that can reach the network, and whether the
    function it sits in consults offline mode.

    Per *function* rather than per module: a module with two ways out and one
    gate would satisfy a per-module check while half of it still leaves.
    """
    found: list[tuple[str, int, str, bool]] = []
    for path in sorted(PACKAGE.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        holders = [n for n in ast.walk(tree)
                   if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            parts: list[str] = []
            probe = node.func
            while isinstance(probe, ast.Attribute):
                parts.append(probe.attr)
                probe = probe.value
            if isinstance(probe, ast.Name):
                parts.append(probe.id)
            key = tuple(reversed(parts))
            for signature, name in EGRESS.items():
                if key == signature or key[-len(signature):] == signature:
                    # The innermost function containing this call.
                    holder = min(
                        (h for h in holders
                         if h.lineno <= node.lineno
                         and getattr(h, "end_lineno", h.lineno) >= node.lineno),
                        key=lambda h: node.lineno - h.lineno, default=None)
                    found.append((path.name, node.lineno, name,
                                  holder is not None and _gate_calls(holder)))
                    break
    return found


def test_the_console_reads_it_rather_than_only_binding_it():
    """A binding is not a door — the estate's own lesson, ported the night
    the classifier noticed this product had the code and not the guard. The
    console binds `offlineStatus` and Settings renders it; nothing held
    either half, so a refactor could drop the screen's read and the posture
    would go back to being a route nobody meets.

        asked     does a screen mention the binding
        mattered  does a screen call it

    Comments stripped first, for the sibling's recorded reason: the injection
    that proved it necessary replaced the call with
    `null /* api.offlineStatus() */`, and a substring search called that a
    door.
    """
    console = REPO / "app" / "src"
    binding = (console / "api.ts").read_text(encoding="utf-8")
    assert "offlineStatus" in binding, "the console cannot ask for the posture"
    used = []
    for screen in (console / "screens").glob("*.tsx"):
        text = re.sub(r"/\*.*?\*/", "", screen.read_text(encoding="utf-8"),
                      flags=re.S)
        text = re.sub(r"//[^\n]*", "", text)
        if re.search(r"\bapi\s*\.\s*offlineStatus\s*\(", text):
            used.append(screen)
    assert used, (
        "`api.offlineStatus` is bound and no screen calls it, so the posture "
        "is a route nobody meets")


def test_the_extraction_finds_the_paths_out():
    """A guard on the guard. A renamed import makes the walk find nothing, and
    a check over no sites passes while every one of them is ungated."""
    sites = _egress_sites()
    assert len(sites) >= ratchets.floor("host.egress_sites"), (
        f"only {len(sites)} egress site(s) found — the AST walk has stopped "
        "matching, and the check below would pass on nothing")
    names = {name for _, _, name, _ in sites}
    assert "urlopen" in names and "smtplib.SMTP" in names, (
        f"the walk found only {sorted(names)}; it is meant to see both the "
        "HTTP and the mail paths")


def test_every_way_out_of_this_host_consults_offline_mode():
    """The defect, generalised: every call that can put bytes on a wire sits
    in a function that asks whether they may."""
    ungated = [f"{f}:{line} — {what}"
               for f, line, what, gated in _egress_sites()
               if not gated and f not in EXEMPT]
    assert not ungated, (
        f"{len(ungated)} way(s) out of this host never consult offline mode, "
        "so `nothing leaves the host` is not true of them:\n    "
        + "\n    ".join(ungated)
        + "\n  Gate it with `offline.allow(url, what)`, or add the module to "
          "EXEMPT above with the reason it cannot carry anything.")


def test_every_exemption_names_a_module_that_still_exists():
    """A stale exemption is a hole nobody is looking at."""
    live = {name for name, _, _, _ in _egress_sites()}
    stale = sorted(set(EXEMPT) - live)
    assert not stale, (
        f"{stale} are exempted and no longer open a connection — strike them, "
        "so the list stays a list of decisions rather than of leftovers")


# --- driven ----------------------------------------------------------------

@pytest.fixture()
def offline_on(monkeypatch):
    monkeypatch.setenv("QRME_OFFLINE", "1")


@pytest.mark.parametrize("host,local", [
    ("localhost", True), ("127.0.0.1", True), ("192.168.1.40", True),
    ("10.1.2.3", True), ("172.16.0.9", True),
    ("api.openai.com", False), ("8.8.8.8", False),
    ("vault.example.com", False), ("", False), (None, False),
])
def test_local_is_this_machine_or_its_own_network(host, local):
    assert offline.is_local(host) is local


def test_a_name_that_does_not_resolve_is_not_local():
    """Failing closed is the only safe direction. An unresolvable name in
    offline mode is a typo or a host that is not there, and neither is a
    reason to try the connection."""
    assert offline.is_local("nothing.invalid") is False


def test_the_vault_is_refused_when_it_is_somebody_elses_machine(offline_on):
    from qrme.pdi_client import _UrllibClient
    with pytest.raises(offline.LeftTheHost) as refused:
        _UrllibClient("https://vault.example.com").request("GET", "/health")
    assert "vault.example.com" in str(refused.value)


def test_an_on_prem_vault_is_allowed_through(offline_on):
    """The half that matters as much as the refusal. Offline mode exists for
    exactly this deployment, and blocking it would make the mode unusable."""
    from qrme.pdi_client import _UrllibClient
    try:
        _UrllibClient("http://127.0.0.1:9/health").request("GET", "/health")
    except offline.LeftTheHost:  # pragma: no cover
        pytest.fail("an on-prem vault on loopback was refused")
    except Exception:
        pass  # nothing listening on port 9 — reaching the socket is the point


def test_mail_to_another_machine_is_refused(offline_on, monkeypatch):
    monkeypatch.setenv("QRME_SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("QRME_SMTP_PORT", "587")
    monkeypatch.setenv("QRME_SMTP_FROM", "qrme@example.com")
    from qrme import mailer
    with pytest.raises(offline.LeftTheHost) as refused:
        mailer.deliver("someone@example.com", "code", "123456")
    assert "smtp.example.com" in str(refused.value)
    assert "someone@example.com" not in str(refused.value), (
        "the refusal quotes the recipient's address back — the one thing this "
        "path exists to stop sending anywhere")


def test_nothing_is_refused_when_offline_mode_is_off(monkeypatch):
    """The mode is opt-in, and a deployment that never set it must be
    untouched by any of this."""
    monkeypatch.delenv("QRME_OFFLINE", raising=False)
    offline.allow("https://api.openai.com/v1/chat", "the model")
    offline.allow_host("smtp.example.com", "mail")


def test_the_status_endpoint_still_answers_for_the_whole_posture():
    """`external_transmission_possible` is what a deployment shows an auditor.
    It was true of three paths and claimed for all of them."""
    assert offline.status()["external_transmission_possible"] is (
        not offline.enabled())
    with pytest.MonkeyPatch.context() as m:
        m.setenv("QRME_OFFLINE", "1")
        assert offline.status()["external_transmission_possible"] is False
