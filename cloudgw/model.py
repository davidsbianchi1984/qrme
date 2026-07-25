"""What the gateway actually serves inference from.

The gateway's whole reason to exist is that it runs a *greater* model than a
laptop can: one operator holds the API credentials and the rest of the
deployments route through them. So the provider here is the operator's
choice, configured once.

``CLOUDGW_MODEL`` names it; ``ANTHROPIC_API_KEY`` authorizes it. With no key
configured the gateway serves a stub, which keeps the suite's end-to-end
tests honest — they exercise the real routing, fallback, and intake paths
without anyone's key or bill.
"""

from __future__ import annotations

import os

DEFAULT_MODEL = "claude-fable-5"


class StubProvider:
    """Deterministic stand-in. Present so a gateway can be run, tested, and
    demonstrated without credentials — never as a silent fallback for a
    misconfigured production one, which is why it names itself as a stub in
    every response and in /health."""

    tier = "stub"

    def __init__(self, name: str = "stub"):
        self.name = name

    def generate(self, system: str, messages: list[dict]) -> str:
        last = messages[-1].get("content", "") if messages else ""
        return f"[gateway stub reply to: {last[:120]}]"


class AnthropicProvider:
    """The hosted tier. Errors propagate: the client's job is to fall back to
    its own local provider, and swallowing the failure here would turn a
    visible outage into silently degraded answers."""

    tier = "hosted"

    def __init__(self, name: str, api_key: str):
        self.name = name
        self._key = api_key

    def generate(self, system: str, messages: list[dict]) -> str:
        import anthropic
        client = anthropic.Anthropic(api_key=self._key)
        reply = client.messages.create(
            model=self.name, max_tokens=1024, system=system,
            messages=[{"role": m.get("role", "user"),
                       "content": m.get("content", "")} for m in messages])
        return "".join(block.text for block in reply.content
                       if getattr(block, "type", "") == "text")


def provider_from_env():
    key = os.environ.get("ANTHROPIC_API_KEY")
    name = os.environ.get("CLOUDGW_MODEL", DEFAULT_MODEL)
    return AnthropicProvider(name, key) if key else StubProvider()
