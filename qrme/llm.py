"""LLM provider layer.

Profiles are powered by Claude via the official Anthropic SDK by default. When
no Anthropic credentials are configured (or ``QRME_LLM=stub``), a deterministic
stub provider keeps the platform — and its tests — fully functional offline.

Owners are not locked to Claude. A profile can pick any registered provider —
**Claude (Anthropic)**, **ChatGPT (OpenAI)**, **Grok (xAI)**, **Perplexity**,
or **Gemini (Google)** — via ``PUT /profiles/{id}/model``; the choice is stored
per profile and honored on every generation. OpenAI, Grok, and Perplexity all
speak the OpenAI ``/chat/completions`` shape, so one adapter covers them;
Gemini has its own adapter.

Design rules honored here:

* **Deterministic stub is the floor.** Any network provider that errors (bad
  key, outage, missing SDK) degrades to the stub instead of failing the
  request, and the degrade is logged. The platform never hard-breaks on a
  third-party model.
* **Offline is absolute.** In ``QRME_OFFLINE`` mode every network provider is
  bypassed regardless of the per-profile choice — nothing leaves the host.
* **Auditable selection.** ``get_provider`` resolves a single, explainable
  provider name; ``available()`` reports what is configured so a caller (or the
  ``/models`` endpoint) can show the user exactly what they can pick.
"""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request
from contextvars import ContextVar
from typing import Protocol

logger = logging.getLogger("qrme.llm")

# Bring-your-own key: a caller may send ``x-llm-api-key`` and the request's
# generations run on *their* credential instead of the deployment's. The key
# lives in a request-scoped context variable set by API middleware — it is
# never persisted, never logged, and gone when the request ends. The
# deployment's own env key (the operator lending theirs out) stays the
# fallback for requests that bring none.
_REQUEST_KEY: ContextVar[str | None] = ContextVar("qrme_llm_request_key",
                                                  default=None)


# How much room a reply gets, and what happens when it runs out.
#
# This was 1024 with the comment "chat replies are deliberately short", and
# short is right for a chat turn — but the same door answers a question like
# "write me the migration" or "explain both patents", and a long answer met the
# wall mid-sentence and simply stopped. Five times the room is the field call
# — it went to ten for a while, and the field called it back down: a spoken
# conversation waits for the whole reply before it says a word, and ten
# times the room was minutes of orb where a talk turn wants seconds. Five
# held for a release, and the same reviewer sent it back once more —
# "still a long delay while waiting for a response — drop it to 2.5" —
# so two and a half rooms is the ceiling now. The floor under this
# staircase is the truncation notice below: shrinking the wall is safe
# exactly because hitting it is said out loud rather than read as a
# model losing the thread.
#
# A bigger wall is still a wall, so the second half matters more than the
# first: when the model stops because it ran out of room rather than because it
# finished, the reply says so. Silence at the cut is the failure — a person
# reading a sentence that ends in the middle has no way to tell a truncation
# from a model that lost the thread, and the two call for opposite responses.
MAX_REPLY_TOKENS = 2560

#: Appended when, and only when, the room ran out. The platform speaking, not
#: the persona — so it is registered in `i18n._PUBLIC` and travels through
#: `tr_public` like every other sentence this platform says to a person, rather
#: than being generated in whatever language the model happened to be using.
CONTINUES = "— cut off here, not finished. Ask me to continue."


def _capped(text: str, ran_out: bool) -> str:
    """One place, so five providers cannot disagree about the wording."""
    text = (text or "").strip()
    if not ran_out:
        return text
    return f"{text}\n\n{CONTINUES}" if text else CONTINUES


def set_request_key(key: str | None):
    """Install a caller-supplied API key for the current request; returns the
    reset token. Middleware owns the set/reset pairing."""
    return _REQUEST_KEY.set(key or None)


def reset_request_key(token) -> None:
    _REQUEST_KEY.reset(token)


def request_key() -> str | None:
    return _REQUEST_KEY.get()


# Who actually generated this request's content.
#
# Every network provider here degrades to the local stub rather than failing —
# a model outage should not break the product, and that decision stands. What
# did not stand is what the platform then *said* about the result:
# `common.content_provenance` stamped `generated_by` from the profile's stored
# choice, so a person whose own key had expired got stub-written text labelled
# with the model they had chosen, watermarked and published.
#
#     asked     which model was this profile set to
#     mattered  which model actually wrote this
#
# The sibling product had already written the rule in its own FallbackProvider:
# *a log line the user will never read is not disclosure*. This is that rule,
# in the product whose premise is that generated content carries a trustworthy
# account of where it came from.
#
# Request-scoped like the key above, because the provider is built and
# discarded inline at every call site — `provider_for_profile(id).generate(…)`
# — so there is no instance for a caller to interrogate afterwards.
_ANSWERED_BY: ContextVar[tuple[str, str | None] | None] = ContextVar(
    "qrme_llm_answered_by", default=None)

#: What answers when a network provider will not. Named rather than spelled
#: `"stub"` at each site: the person reading a provenance record needs to know
#: this text came from the machine in front of them, not from the model they
#: chose, and "stub" is this repository's word rather than theirs.
LOCAL_FALLBACK = "local fallback"


def note_answered_by(name: str, degraded_from: str | None = None) -> None:
    """Record who produced this request's content, and what was asked for
    instead when they are not the same."""
    _ANSWERED_BY.set((name, degraded_from))


def answered_by() -> tuple[str, str | None] | None:
    """``(actual_provider, provider_asked_for_or_None)``, or None when nothing
    on this request went through a degrading wrapper."""
    return _ANSWERED_BY.get()


def clear_answered_by(token=None):
    """Middleware owns this: one request's degrade must not describe the next
    one's content."""
    if token is not None:
        _ANSWERED_BY.reset(token)
        return None
    return _ANSWERED_BY.set(None)


def scrub(text: object) -> str:
    """A provider's failure, with the caller's own credential taken out.

    The reason for a degrade is shown to the person and written to the log, and
    it comes from an exception this codebase did not raise. Some HTTP clients
    put the request — headers included — into the string form of their errors,
    and on this path the interesting header is the caller's API key. It is
    never ours to repeat.
    """
    said = str(text)
    key = request_key()
    if key:
        said = said.replace(key, "<the key you sent>")
    return said[:200]


MODEL = os.environ.get("QRME_MODEL", "claude-opus-5")

# Per-provider default models are overridable by env so an operator can pin a
# specific version without a code change.
_OPENAI_MODEL = os.environ.get("QRME_OPENAI_MODEL", "gpt-4o")
_GROK_MODEL = os.environ.get("QRME_GROK_MODEL", "grok-2-latest")
_PPLX_MODEL = os.environ.get("QRME_PERPLEXITY_MODEL", "sonar")
_GEMINI_MODEL = os.environ.get("QRME_GEMINI_MODEL", "gemini-2.0-flash")
_DEEPSEEK_MODEL = os.environ.get("QRME_DEEPSEEK_MODEL", "deepseek-chat")
# The founder's own algorithm, or anything speaking the OpenAI dialect:
# point QRME_CUSTOM_LLM_URL at it and it becomes a first-class provider
# tile — configuration, so the day the algorithm exists no release is
# needed.
_CUSTOM_BASE = os.environ.get("QRME_CUSTOM_LLM_URL", "")
_CUSTOM_MODEL = os.environ.get("QRME_CUSTOM_LLM_MODEL", "default")
_CUSTOM_LABEL = os.environ.get("QRME_CUSTOM_LLM_LABEL", "Your own algorithm")
# The local model: whatever the user pulled into Ollama. deepseek-r1:1.5b
# is small enough for most machines; QRME_OLLAMA_MODEL overrides.
# `or`, not a get() default: compose forwards these as empty strings on
# a box whose operator left them blank in .env (§8 of the deploy page
# fills them in), and an empty string standing in for the default is how
# a dial connected to nothing turns into a broken door.
_OLLAMA_MODEL = os.environ.get("QRME_OLLAMA_MODEL") or "deepseek-r1:1.5b"
_OLLAMA_BASE = (os.environ.get("QRME_OLLAMA_URL")
                or "http://127.0.0.1:11434") + "/v1"

_TIMEOUT = int(os.environ.get("QRME_LLM_TIMEOUT", "30"))


class Provider(Protocol):
    def generate(self, system: str, messages: list[dict]) -> str: ...


# --------------------------------------------------------------------------- #
# Providers
# --------------------------------------------------------------------------- #

class AnthropicProvider:
    """Claude via the official Anthropic SDK."""

    def __init__(self, api_key: str | None = None) -> None:
        import anthropic

        # Gated here and not only in `provider_for_profile`. Offline mode
        # bypassed this by never *choosing* it — a gate on the factory, which
        # anything constructing a provider directly walks past.
        #
        #     asked     does offline mode pick a local provider
        #     mattered  can a remote one still be built and used
        from . import offline
        if offline.enabled():
            raise offline.LeftTheHost(
                "offline mode is on, so the Anthropic API cannot be reached. "
                "Nothing leaves this machine while QRME_OFFLINE is set.")
        self._client = (anthropic.Anthropic(api_key=api_key) if api_key
                        else anthropic.Anthropic())

    def generate(self, system: str, messages: list[dict]) -> str:
        response = self._client.messages.create(
            model=MODEL,
            max_tokens=MAX_REPLY_TOKENS,
            thinking={"type": "adaptive"},
            system=system,
            messages=messages,
        )
        text = "".join(b.text for b in response.content if b.type == "text")
        return _capped(text, response.stop_reason == "max_tokens")


class OpenAICompatibleProvider:
    """Any OpenAI ``/chat/completions``-shaped API: OpenAI, xAI (Grok),
    Perplexity. The only differences are the base URL, the bearer key, and the
    model id — all injected at construction."""

    def __init__(self, name: str, base_url: str, api_key: str, model: str) -> None:
        self.name = name
        self._base = base_url.rstrip("/")
        self._key = api_key
        self._model = model

    def generate(self, system: str, messages: list[dict]) -> str:
        payload = {
            "model": self._model,
            "max_tokens": MAX_REPLY_TOKENS,
            "messages": [{"role": "system", "content": system}, *messages],
        }
        body = _post_json(
            f"{self._base}/chat/completions",
            payload,
            {"Authorization": f"Bearer {self._key}"},
        )
        try:
            choice = body["choices"][0]
            return _capped(choice["message"]["content"],
                           choice.get("finish_reason") == "length")
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"{self.name}: unexpected response shape") from exc


class GeminiProvider:
    """Google Gemini via the Generative Language REST API. Its request/response
    shape differs from OpenAI's, so it gets its own adapter."""

    def __init__(self, api_key: str, model: str) -> None:
        self._key = api_key
        self._model = model

    def generate(self, system: str, messages: list[dict]) -> str:
        contents = [
            {
                "role": "model" if m.get("role") == "assistant" else "user",
                "parts": [{"text": m.get("content", "")}],
            }
            for m in messages
        ]
        payload = {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": contents,
            "generationConfig": {"maxOutputTokens": MAX_REPLY_TOKENS},
        }
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self._model}:generateContent?key={self._key}"
        )
        body = _post_json(url, payload, {})
        try:
            candidate = body["candidates"][0]
            parts = candidate["content"]["parts"]
            return _capped("".join(p.get("text", "") for p in parts),
                           candidate.get("finishReason") == "MAX_TOKENS")
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("gemini: unexpected response shape") from exc


class StubProvider:
    """Deterministic in-character reply used offline and in tests.

    The stub honors the same prompt contract as the real provider: it reads
    the persona name, nickname, and tone hints out of the system prompt so
    relationship-aware behavior is observable end to end.
    """

    def generate(self, system: str, messages: list[dict]) -> str:
        # The stub still honors the prompt contract (nickname and tone are
        # read out of the system prompt, so relationship-aware behavior
        # stays observable end to end) — but it no longer performs a
        # character. "[stub reply in a warm tone to: hi]" in a chat bubble
        # is a stage direction leaking into the play; the only honest stub
        # reply is an explanation of itself and the two doors out.
        last_user = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"), ""
        )
        nickname = _extract(system, "Address them as: ")
        tone = _extract(system, "Tone: ") or "warm"
        greeting = f"{nickname} — " if nickname else ""
        # A field report pressed "Let them talk" twice and got the whole
        # setup speech twice \u2014 a wall of the same apology, which reads as
        # a broken room rather than an honest one. The instructions are
        # said once. After that the stub keeps holding the thread: still
        # honest that no model answered, but shorter, and ending with a
        # question back that references what was said, so the conversation
        # has somewhere to go.
        said_already = any(
            m.get("role") == "assistant"
            and "no model answered" in m.get("content", "")
            for m in messages)
        if said_already:
            if last_user:
                return (
                    f"{greeting}Still here, still without a model \u2014 no "
                    "model answered this request either. But I'm holding "
                    f"on to \u201c{last_user[:80]}\u201d: what would a "
                    f"good answer to that need to get right? (tone: {tone})"
                )
            return (
                f"{greeting}Nothing new to work from yet, and still no "
                "model behind me \u2014 no model answered this request. Say "
                "something and I will keep it for the day I can answer "
                f"properly. What brought you in? (tone: {tone})"
            )
        # The echo stays (moderation must be able to see user-influenced
        # text ride into the reply, end to end) but as a plain quotation,
        # not a stage direction: no brackets, no "stub reply in a warm
        # tone" leaking into a chat bubble.
        return (
            f"{greeting}I heard you: \u201c{last_user[:80]}\u201d. I can't "
            "answer as this profile yet — no model answered this request. "
            "Your message is saved. To bring this profile to life, add a "
            "provider key in Settings → Model, or install Ollama "
            "(ollama.com) and pull a model like deepseek-r1:1.5b — free, "
            f"offline, found automatically. (tone: {tone})"
        )


#: The memory prefix the vault provider may ground on, set around a
#: generation by whoever knows whose conversation this is (the chat
#: route). A contextvar rather than a constructor argument because
#: providers are built per call, below the layer that knows the pair.
_GROUND_PREFIX: ContextVar[str | None] = ContextVar("qrme_ground_prefix",
                                                    default=None)


def ground_on(prefix: str | None):
    """Install the pair's memory prefix for this generation; returns the
    reset token. The caller owns the set/reset pairing."""
    return _GROUND_PREFIX.set(prefix)


def ground_reset(token) -> None:
    _GROUND_PREFIX.reset(token)


class VaultProvider:
    """The vault's own local model, through PDI's resident voice door.

    The prompt travels the same authenticated channel every seal uses and
    goes no further: `/resident/infer` runs it on the facility's own
    inference server, and the audit line there carries the prompt's
    length, never its words — a profile that speaks from inside the
    building the data never leaves. A vault with *no* local model raises
    rather than speaking the resident's operational stub sentence in a
    persona's voice; `FallbackProvider` then hands the turn to this
    product's own stub, and the reason is in the log.
    """

    #: Whether the last answer was grounded in the pair's own seals —
    #: read by the chat route for the provenance disclosure.
    grounded = False
    drew_on: list = []

    def generate(self, system: str, messages: list[dict]) -> str:
        from . import pdi_client
        client = pdi_client.active()
        if client is None:
            raise RuntimeError("no PDI tandem is configured")
        self.grounded, self.drew_on = False, []
        turns = "\n".join(
            ("Person: " if m["role"] == "user" else "You: ") + m["content"]
            for m in messages)
        prefix = _GROUND_PREFIX.get()
        out = None
        if prefix and messages:
            # Grounded: the vault ranks this pair's own seals against the
            # last thing said and answers from them — retrieval and
            # generation both inside the facility, with the prefix as the
            # per-pair wall inside the shared tenant. An older PDI
            # without the ask door answers None and the voice door below
            # still speaks, ungrounded and said so.
            question = messages[-1]["content"]
            ask = getattr(client, "resident_ask", None)
            out = ask(question, prefix=prefix,
                      system=system + "\n\nThe conversation so far:\n"
                      + turns) if ask else None
            if out is not None:
                self.grounded = True
                self.drew_on = list(out.get("drew_on") or [])
        if out is None:
            out = client.resident_infer(system + "\n\n" + turns + "\nYou: ")
        if out is None:
            raise RuntimeError("this PDI has no voice door (older tandem)")
        if out.get("model") == "stub":
            raise RuntimeError("the vault has no local model installed")
        text = (out.get("text") or "").strip()
        if not text:
            raise RuntimeError("the vault's model answered nothing")
        return text


class FallbackProvider:
    """Wraps a network provider so any failure degrades to a local fallback
    (the stub) instead of surfacing an error to the caller.

    The degrade is **recorded as well as logged**. It used to be only logged,
    and `content_provenance` went on stamping the provider the profile had
    chosen — so an expired key produced stub text labelled with the model the
    owner thought had written it. A log line the user will never read is not
    disclosure.
    """

    def __init__(self, name: str, primary: Provider, fallback: Provider) -> None:
        self.name = name
        self._primary = primary
        self._fallback = fallback

    def generate(self, system: str, messages: list[dict]) -> str:
        try:
            text = self._primary.generate(system, messages)
        except Exception as exc:  # noqa: BLE001 — any provider failure degrades
            reason = scrub(exc)
            logger.warning("provider %s failed, using local fallback: %s",
                           self.name, reason)
            note_answered_by(LOCAL_FALLBACK, degraded_from=self.name)
            return self._fallback.generate(system, messages)
        note_answered_by(self.name)
        return text


# --------------------------------------------------------------------------- #
# Registry
# --------------------------------------------------------------------------- #

# Each entry describes how to detect and build one provider. ``env`` lists the
# environment variables that, if any is set, count the provider as configured.
_REGISTRY: dict[str, dict] = {
    "stub": {
        "label": "Deterministic stub (offline)",
        "kind": "stub",
        "network": False,
        "env": [],
        "model": "stub",
    },
    "anthropic": {
        "label": "Claude (Anthropic)",
        "kind": "anthropic",
        "network": True,
        "env": ["ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"],
        "model": MODEL,
    },
    "openai": {
        "label": "ChatGPT (OpenAI)",
        "kind": "openai",
        "network": True,
        "env": ["OPENAI_API_KEY"],
        "base": "https://api.openai.com/v1",
        "model": _OPENAI_MODEL,
    },
    "grok": {
        "label": "Grok (xAI)",
        "kind": "openai",
        "network": True,
        "env": ["XAI_API_KEY", "GROK_API_KEY"],
        "base": "https://api.x.ai/v1",
        "model": _GROK_MODEL,
    },
    "perplexity": {
        "label": "Perplexity",
        "kind": "openai",
        "network": True,
        "env": ["PERPLEXITY_API_KEY", "PPLX_API_KEY"],
        "base": "https://api.perplexity.ai",
        "model": _PPLX_MODEL,
    },
    "gemini": {
        "label": "Gemini (Google)",
        "kind": "gemini",
        "network": True,
        "env": ["GEMINI_API_KEY", "GOOGLE_API_KEY"],
        "model": _GEMINI_MODEL,
    },
    "deepseek": {
        "label": "DeepSeek",
        "kind": "openai",
        "network": True,
        "env": ["QRME_DEEPSEEK_API_KEY", "DEEPSEEK_API_KEY"],
        "base": "https://api.deepseek.com/v1",
        "model": _DEEPSEEK_MODEL,
    },
    # See _CUSTOM_BASE above: any OpenAI-dialect endpoint, the founder's
    # own algorithm first among them. Configured once the URL is set.
    "custom": {
        "label": _CUSTOM_LABEL,
        "kind": "openai",
        "network": True,
        "env": ["QRME_CUSTOM_LLM_KEY"],
        "base": _CUSTOM_BASE,
        "model": _CUSTOM_MODEL,
        "needs_base": True,
    },
    # A real offline model: Ollama (ollama.com) runs models like
    # deepseek-r1:1.5b on the user's own machine — free, no key, nothing
    # leaves the host. The daemon running IS the configuration.
    "ollama": {
        "label": "Local (Ollama)",
        "kind": "openai",
        "network": False,
        "env": [],
        "base": _OLLAMA_BASE,
        "model": _OLLAMA_MODEL,
    },
    "vault": {
        "label": "The vault's local model (PDI resident)",
        "kind": "vault",
        "network": True,
        "env": [],
        "model": "resident-local",
    },
}

#: Valid values for a stored preference: any registry name, or ``auto`` (let
#: the platform decide with the default resolution order).
CHOICES = ("auto", *_REGISTRY.keys())


def _env_value(name: str) -> str | None:
    for key in _REGISTRY[name].get("env", []):
        val = os.environ.get(key)
        if val:
            return val
    return None


_OLLAMA_PROBE: dict = {"at": 0.0, "alive": False}


def _ollama_alive() -> bool:
    """Is a local Ollama daemon answering? Probed (there is no key to
    check), cached briefly so the settings screen doesn't knock on the
    port for every tile."""
    import time
    if time.monotonic() - _OLLAMA_PROBE["at"] < 10:
        return _OLLAMA_PROBE["alive"]
    alive = False
    try:
        probe = _OLLAMA_BASE.rsplit("/v1", 1)[0] + "/api/version"
        # "Ollama IS offline: it answers on loopback" was true of the default
        # and never checked — QRME_OLLAMA_URL can name any host. Offline mode
        # allows a local daemon and refuses a remote one, which is what that
        # sentence always meant.
        from . import offline
        offline.allow(probe, "the local model daemon")
        req = urllib.request.Request(probe)
        with urllib.request.urlopen(req, timeout=0.5) as r:
            alive = r.status == 200
    except Exception:  # noqa: BLE001 — not running is the common case
        alive = False
    _OLLAMA_PROBE.update(at=time.monotonic(), alive=alive)
    return alive


def is_configured(name: str) -> bool:
    """True when a provider can actually be used in this environment. The stub
    is always available; ``anthropic`` also counts as configured when
    ``QRME_LLM=anthropic`` is set explicitly (the SDK may hold ambient creds)."""
    if name == "stub":
        return True
    if name == "anthropic" and os.environ.get("QRME_LLM") == "anthropic":
        return True
    if name == "ollama":
        return _ollama_alive()
    if name == "vault":
        # Configured when a PDI tandem is attached: the model itself lives
        # on the vault's host, and a facility without one answers honestly
        # at generation time.
        from . import pdi_client
        return pdi_client.active() is not None
    if name not in _REGISTRY:
        return False
    # A provider whose whole point is a user-supplied endpoint (the
    # founder's own algorithm) is configured only once the URL is set —
    # a key alone points at nothing.
    if _REGISTRY[name].get("needs_base") and not _REGISTRY[name].get("base"):
        return False
    return _env_value(name) is not None


def available() -> list[dict]:
    """Describe every provider for the ``/models`` endpoint / a settings UI."""
    return [
        {
            "name": name,
            "label": spec["label"],
            "network": spec["network"],
            "model": spec["model"],
            "configured": is_configured(name),
        }
        for name, spec in _REGISTRY.items()
    ]


def default_name() -> str:
    """The provider used when a caller expresses no preference. Preserves the
    historical behavior: honor ``QRME_LLM`` if it names something usable, else
    Claude when its credentials are present, else the stub."""
    env = os.environ.get("QRME_LLM")
    if env in _REGISTRY and is_configured(env):
        return env
    # A caller who typed a key in wants a real model, not the stub — and the
    # product's default model is Claude.
    if is_configured("anthropic") or request_key():
        return "anthropic"
    # No key anywhere, but a local model is running: a real answer beats a
    # canned one, and it never leaves the machine.
    if is_configured("ollama"):
        return "ollama"
    return "stub"


def resolve_choice(choice: str | None) -> str:
    """Turn a requested preference into a concrete, usable provider name.

    ``None``/``"auto"`` defer to :func:`default_name`. An explicit choice that
    is unknown or unconfigured is logged and falls back to the default, so a
    stored preference can never wedge generation."""
    if choice and choice != "auto":
        if choice in _REGISTRY and (is_configured(choice) or request_key()):
            # A caller-supplied key IS the configuration for their explicit
            # choice — the deployment needing no credential of its own is the
            # whole point of bring-your-own.
            return choice
        logger.warning("requested provider %r is not available; using default",
                       choice)
    return default_name()


def _build(name: str) -> Provider:
    """Construct a provider by registry name, wrapping any network provider so
    a construction or call failure degrades to the stub."""
    spec = _REGISTRY.get(name, _REGISTRY["stub"])
    stub = StubProvider()
    if name == "stub":
        return stub
    # The request's own key outranks the deployment's env key: somebody who
    # typed their credential in expects their requests billed to it.
    key = request_key() or _env_value(name)
    try:
        if spec["kind"] == "anthropic":
            primary: Provider = AnthropicProvider(api_key=request_key())
        elif spec["kind"] == "openai":
            primary = OpenAICompatibleProvider(
                name, spec["base"], key or "", spec["model"])
        elif spec["kind"] == "gemini":
            primary = GeminiProvider(key or "", spec["model"])
        elif spec["kind"] == "vault":
            primary = VaultProvider()
        else:  # unknown kind — safety net
            return stub
    except Exception as exc:  # noqa: BLE001 — e.g. missing SDK
        logger.warning("could not build provider %s: %s", name, exc)
        return stub
    return FallbackProvider(name, primary, stub)


def get_provider(cloud=None, choice: str | None = None) -> Provider:
    """Return the provider to generate with.

    ``choice`` is an explicit per-profile preference (a registry name or
    ``auto``). ``cloud`` is an optional CloudModelClient (the "greater model"
    gateway).

    Resolution:

    * **Offline** (``QRME_OFFLINE``) always returns the local stub — no network
      provider, no cloud, regardless of ``choice``.
    * An **explicit** ``choice`` (anything but ``auto``/``None``) is honored
      directly and is *not* wrapped by the cloud gateway — the user asked for a
      specific model, so they get it (with stub fallback on failure).
    * Otherwise the platform **default** is used, optionally routed through the
      cloud gateway's greater model with local fallback (unchanged behavior).
    """
    from . import offline
    if offline.enabled():
        # Offline is absolute for the network — but Ollama IS offline: it
        # answers on loopback and nothing leaves the machine.
        if is_configured("ollama"):
            return _build("ollama")
        return StubProvider()

    explicit = bool(choice) and choice != "auto"
    name = resolve_choice(choice)
    base = _build(name)

    if not explicit and cloud is not None:
        from .cloud import CloudProvider
        return CloudProvider(cloud, fallback=base)
    return base


# --------------------------------------------------------------------------- #
# Per-profile preference (stored in the ``model_prefs`` table)
# --------------------------------------------------------------------------- #

def get_choice(profile_id: str) -> str:
    """The stored provider preference for a profile, or ``auto`` if unset."""
    from . import db
    row = db.connect().execute(
        "SELECT provider FROM model_prefs WHERE profile_id=?", (profile_id,)
    ).fetchone()
    return row["provider"] if row else "auto"


def set_choice(profile_id: str, provider: str) -> str:
    """Persist a profile's provider preference. Validates against CHOICES; the
    caller (router) is responsible for auth and audit."""
    if provider not in CHOICES:
        raise ValueError(f"unknown provider {provider!r}")
    from . import db
    conn = db.connect()
    conn.execute(
        "INSERT INTO model_prefs (profile_id, provider, updated_at)"
        " VALUES (?,?,?)"
        " ON CONFLICT(profile_id) DO UPDATE SET provider=excluded.provider,"
        " updated_at=excluded.updated_at",
        (profile_id, provider, db.utcnow()),
    )
    conn.commit()
    logger.info("profile %s set model provider -> %s", profile_id, provider)
    return provider


def is_network(name: str) -> bool:
    """Whether a resolved provider name reaches an external host — the
    registry's own `network` column, published rather than re-guessed by
    each caller. Unknown names answer False — a door not in the registry
    is not a door to the internet. Note the vault answers True: a socket
    does open; whether that counts as *leaving* is the caller's question
    (the excursions and the letter both say the facility's own wire does
    not)."""
    return bool(_REGISTRY.get(name, {}).get("network"))


def provider_for_profile(profile_id: str, cloud=None) -> Provider:
    """The provider a given profile should generate with — its stored choice,
    resolved through :func:`get_provider`."""
    return get_provider(cloud=cloud, choice=get_choice(profile_id))


def _extract(text: str, marker: str) -> str | None:
    for line in text.splitlines():
        if marker in line:
            return line.split(marker, 1)[1].strip().rstrip(".")
    return None


# --------------------------------------------------------------------------- #
# Low-level HTTP (stdlib only, matching qrme.cloud / qrme.pdi_client)
# --------------------------------------------------------------------------- #

def _post_json(url: str, payload: dict, headers: dict) -> dict:
    data = json.dumps(payload).encode()
    h = {"content-type": "application/json", **headers}
    from . import offline
    offline.allow(url, "the model provider")
    req = urllib.request.Request(url, data=data, method="POST", headers=h)
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")[:200]
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"network error: {exc}") from exc
