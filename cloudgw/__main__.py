"""Run the gateway: ``python -m cloudgw`` (add ``--host``/``--port``)."""

from __future__ import annotations

import argparse
import os
import sys


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="python -m cloudgw",
        description="Cloud Model Gateway — greater-model inference and the "
                    "contribution intake for QRME, JIM-mini and PDI.")
    p.add_argument("--host", default="0.0.0.0")
    p.add_argument("--port", type=int, default=8300)
    args = p.parse_args(argv)

    # Say out loud what this gateway is and is not configured for. An operator
    # who thinks they are serving a hosted model from a stub, or collecting
    # contributions into a vault that isn't there, should find out at boot.
    from . import model, store
    provider, vault = model.provider_from_env(), store.vault_from_env()
    print(f"model:  {provider.name} ({provider.tier})")
    if provider.tier == "stub":
        print("        no ANTHROPIC_API_KEY — serving the stub, not a "
              "hosted model")
    intake = "PDI vault" if vault.configured else (
        "none — contributions will be refused")
    print(f"intake: {intake}")
    if not os.environ.get("CLOUDGW_TOKENS"):
        print("auth:   no CLOUDGW_TOKENS — open to callers on this machine "
              "only, closed to everyone else")

    import uvicorn
    uvicorn.run("cloudgw.api:app", host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    sys.exit(main())
