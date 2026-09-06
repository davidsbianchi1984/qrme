"""The gateway answers for both products or for neither.

`docker/beta-compose.yml` runs one `cloudgw`, and the gateway does two
jobs. The box uses one of them: the error-report collector. The other —
greater-model inference and the contribution intake — is switched on by
`QRME_CLOUD_URL` and `JIM_CLOUD_URL`, and neither is set.

That decision is written down in the compose file, and so is the rule that
goes with it:

    all three go together — a box where two products use the greater model
    and the third does not is a box answering the same question two ways

Which was a sentence in a comment with nothing holding it. Setting one
variable and not the other is a one-line edit, it deploys clean, both
containers come up healthy, and the only place the split shows is two
`/health` bodies disagreeing about a field nobody reads on purpose.

    asked     is the gateway wired
    mattered  is it wired the same way for everybody behind it

## What this found

Nothing, on the day it was written — which is the point of writing it on
that day. It was written because a `/health` body was misread as `"cloud":
true` on one product and `false` on another, and answering "is that real?"
meant reading four files to prove a comment was still being obeyed.

## What it does not reach

JIM-mini is a separate repository. This guard reads the compose file that
starts JIM's container, so it sees whether JIM is wired — but it cannot
confirm `JIM_CLOUD_URL` is still the name `jim/api.py` reads. The QRME half
is checked against `qrme/api.py` directly. If JIM ever renames its
variable, this file goes on passing and JIM's own suite is what catches it.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
COMPOSE = REPO / "docker" / "beta-compose.yml"
API = (REPO / "qrme" / "api.py").read_text(encoding="utf-8")

#: The two products that can be pointed at the gateway, and the service each
#: one runs under. PDI has no `cloud` field and no switch — it is not in this
#: rule because there is nothing about it to disagree.
PRODUCTS = {"qrme": ("QRME_CLOUD_URL", "QRME_CLOUD_TOKEN"),
            "jim": ("JIM_CLOUD_URL", "JIM_CLOUD_TOKEN")}

#: Where a wired product points. One gateway on the box, one address.
GATEWAY = "http://cloudgw:8300"


def _compose() -> dict:
    return yaml.safe_load(COMPOSE.read_text(encoding="utf-8"))


def _environment(service: str) -> dict:
    env = _compose()["services"][service].get("environment") or {}
    if isinstance(env, list):  # compose accepts "NAME=value" strings too
        env = dict(e.split("=", 1) for e in env if "=" in e)
    return env


def test_the_gateway_answers_for_both_products_or_neither():
    """Both products point at the gateway, or neither does."""
    wired = {name: url_var in _environment(name)
             for name, (url_var, _) in PRODUCTS.items()}
    assert len(set(wired.values())) == 1, (
        "the gateway is wired for some products and not others: "
        + ", ".join(f"{n} {'wired' if w else 'not wired'}"
                    for n, w in sorted(wired.items()))
        + ".\n  A box where one product uses the greater model and the "
        "other does not is a box answering the same question two ways. "
        "Set both or neither."
    )


def test_a_wired_product_carries_an_address_and_a_token():
    """Half a wiring is worse than none — it fails at the first call."""
    for name, (url_var, token_var) in PRODUCTS.items():
        env = _environment(name)
        if url_var not in env:
            continue
        assert str(env[url_var]) == GATEWAY, (
            f"{name} points at {env[url_var]}, not the gateway on this box")
        assert token_var in env, (
            f"{name} names {url_var} and no {token_var}; the gateway "
            "authenticates its callers, so an untokened client is a 401 "
            "on every turn and a silent fall back to the local provider")


def test_the_names_the_compose_file_uses_are_the_names_qrme_reads():
    """The instruction cannot drift from the code that obeys it.

    The compose file spells out the edit in a comment. A comment naming a
    variable nothing reads is worse than no comment: it is followed, it
    changes nothing, and the operator concludes the gateway is broken.
    """
    text = COMPOSE.read_text(encoding="utf-8")
    for var in PRODUCTS["qrme"]:
        # `.get(NAME, "")` and `[NAME]` are both reads; the default is not
        # what is being checked here, the name is.
        assert re.search(rf'os\.environ(?:\.get)?[(\[]\s*"{var}"', API), (
            f"{var} is named in the compose file and read nowhere in qrme/api.py")
        assert var in text, (
            f"qrme/api.py reads {var} and the compose file never mentions it, "
            "so the one edit that switches the gateway on is undocumented")


def test_the_gateway_still_runs_for_the_collector():
    """Off is not the same as gone.

    The gateway's other job — taking error reports off the consoles — is in
    use, so `cloud: false` must never be read as licence to drop the
    service. It has been listed as a container running for nothing once
    already.
    """
    services = _compose()["services"]
    assert "cloudgw" in services, (
        "the gateway is gone; the consoles' error reports have nowhere to land")
    env = _environment("cloudgw")
    assert "CLOUDGW_TOKENS" in env, "the gateway authenticates nobody"
    assert "CLOUDGW_PROBLEM_READERS" in env, "no one may read the reports"
