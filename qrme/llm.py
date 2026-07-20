"""LLM provider layer.

Profiles are powered by Claude via the official Anthropic SDK. When no
Anthropic credentials are configured (or ``QRME_LLM=stub``), a deterministic
stub provider keeps the platform — and its tests — fully functional offline.
"""

from __future__ import annotations

import os
from typing import Protocol

MODEL = os.environ.get("QRME_MODEL", "claude-opus-4-8")


class Provider(Protocol):
    def generate(self, system: str, messages: list[dict]) -> str: ...


class AnthropicProvider:
    def __init__(self) -> None:
        import anthropic

        self._client = anthropic.Anthropic()

    def generate(self, system: str, messages: list[dict]) -> str:
        response = self._client.messages.create(
            model=MODEL,
            max_tokens=1024,  # chat replies are deliberately short
            thinking={"type": "adaptive"},
            system=system,
            messages=messages,
        )
        return "".join(b.text for b in response.content if b.type == "text").strip()


class StubProvider:
    """Deterministic in-character reply used offline and in tests.

    The stub honors the same prompt contract as the real provider: it reads
    the persona name, nickname, and tone hints out of the system prompt so
    relationship-aware behavior is observable end to end.
    """

    def generate(self, system: str, messages: list[dict]) -> str:
        last_user = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"), ""
        )
        nickname = _extract(system, "Address them as: ")
        tone = _extract(system, "Tone: ") or "warm"
        greeting = f"{nickname}, " if nickname else ""
        return (
            f"{greeting}thanks for telling me about that. "
            f"[stub reply in a {tone} tone to: {last_user[:120]}]"
        )


def _extract(text: str, marker: str) -> str | None:
    for line in text.splitlines():
        if marker in line:
            return line.split(marker, 1)[1].strip().rstrip(".")
    return None


def get_provider(cloud=None) -> Provider:
    """``cloud`` is an optional CloudModelClient: when present, inference
    routes to the gateway's greater model with local fallback."""
    from . import offline
    if offline.enabled():
        # Hard offline: the only truly local provider, no cloud wrapping. Any
        # network-bound provider (Anthropic SDK, cloud gateway) is bypassed.
        return StubProvider()
    choice = os.environ.get("QRME_LLM")
    if choice == "stub":
        base: Provider = StubProvider()
    elif choice == "anthropic" or os.environ.get("ANTHROPIC_API_KEY") or os.environ.get(
        "ANTHROPIC_AUTH_TOKEN"
    ):
        base = AnthropicProvider()
    else:
        base = StubProvider()
    if cloud is not None:
        from .cloud import CloudProvider
        return CloudProvider(cloud, fallback=base)
    return base
