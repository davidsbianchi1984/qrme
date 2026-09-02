"""The model menu, by region — a loadout per market, and a lever to taper.

The registry (:mod:`qrme.llm`) knows every provider and where it is from. This
module decides which of them an account is *offered*, and the answer depends on
where the person signed up:

* **A per-region loadout.** Each region gets its own particular set — its home
  providers first, then a curated few popular foreign ones for that market. A
  US account sees American models plus a handful of the foreign ones people
  actually ask for; a Chinese account sees Qwen, DeepSeek, Kimi and GLM first;
  Europe leads with Mistral. Anywhere not mapped gets the widest sensible set.
* **A lever, not a rewrite.** ``QRME_MODEL_POLICY=american`` tapers the
  *American-region* loadout to American, local and self-supplied providers —
  the change the government might one day ask for, made in one line and
  affecting only the accounts it would apply to. Other regions are not bound
  by it. Default is ``all``, which is the beta posture.
* **The region is a fact on the account**, chosen at sign-up and editable
  (``accounts.region``), never inferred from an address later. A profile
  inherits its owner's region; a profile whose owner is not an account here
  (the suite's ``owner-1``, an imported roster) stands on the default.

Two menus read this: the model tiles a profile picks from, and the video
services a profile's presence can render through. One table to curate. The
same table, word for word, sits in JIM-mini (`jim/loadouts.py`): one decision
about a market should be one decision.
"""

from __future__ import annotations

import logging
import os

from . import db, llm

logger = logging.getLogger("qrme.loadouts")

#: The sign-up choices. Short codes, and `other` for anywhere unmapped.
REGIONS = ("us", "ca", "eu", "uk", "cn", "in", "jp", "kr", "br", "au", "other")
DEFAULT_REGION = "us"
POLICIES = ("all", "american")

#: The American set, in the order the menu shows it. Anthropic leads — it is
#: the beta default (the platform's own key carries users until they bring
#: their own).
_AMERICAN = ("anthropic", "openai", "gemini", "grok", "meta", "azure", "bedrock",
             "perplexity", "groq", "together", "fireworks", "nvidia")
#: The ones that never leave the machine, or point at the user's own endpoint.
#: Offered everywhere, under every policy.
_LOCAL = ("ollama", "vault", "custom", "stub")

#: region -> the providers offered there, home first, then a curated few
#: popular foreign. Edit here to grow a region; nothing else needs to change.
LOADOUTS: dict[str, tuple[str, ...]] = {
    "us": _AMERICAN + ("deepseek", "mistral", "qwen", "moonshot"),
    "ca": _AMERICAN + ("cohere", "mistral", "deepseek"),
    "eu": ("mistral",) + _AMERICAN + ("cohere", "deepseek", "qwen"),
    "uk": _AMERICAN + ("mistral", "cohere", "deepseek"),
    "cn": ("qwen", "deepseek", "moonshot", "zhipu") + _AMERICAN + ("mistral",),
    "in": _AMERICAN + ("deepseek", "qwen", "mistral", "cohere"),
    "jp": _AMERICAN + ("deepseek", "qwen", "mistral"),
    "kr": _AMERICAN + ("deepseek", "qwen", "mistral"),
    "br": _AMERICAN + ("deepseek", "mistral", "qwen"),
    "au": _AMERICAN + ("deepseek", "mistral", "cohere"),
    "other": _AMERICAN + ("deepseek", "mistral", "qwen", "moonshot", "zhipu",
                          "cohere"),
}

#: Where each video house on the shelf (:data:`qrme.filming.PROVIDERS`) is
#: from. The shelf says what this platform can send to; this says who is
#: offered it.
VIDEO_ORIGINS: dict[str, str] = {
    "veo": "US", "runway": "US", "luma": "US", "pika": "US",
    "moonvalley": "US", "higgsfield": "US",
    "ltx": "IL",
    "seedance": "CN", "happyhorse": "CN", "kling": "CN", "hailuo": "CN",
    "vidu": "CN",
}
_VIDEO_AMERICAN = ("veo", "runway", "luma", "pika", "moonvalley", "higgsfield")
_VIDEO_CHINESE = ("kling", "seedance", "hailuo", "happyhorse", "vidu")
VIDEO_LOADOUTS: dict[str, tuple[str, ...]] = {
    "us": _VIDEO_AMERICAN + ("kling", "seedance", "hailuo", "ltx"),
    "cn": _VIDEO_CHINESE + _VIDEO_AMERICAN + ("ltx",),
    "other": _VIDEO_AMERICAN + _VIDEO_CHINESE + ("ltx",),
}


def policy() -> str:
    got = os.environ.get("QRME_MODEL_POLICY", "all").strip().lower()
    return got if got in POLICIES else "all"


def account_region(account_id: str | None) -> str:
    """The region on an account row, or the default when there is none."""
    if not account_id:
        return DEFAULT_REGION
    try:
        row = db.connect().execute(
            "SELECT region FROM accounts WHERE id=?", (account_id,)).fetchone()
    except Exception:  # noqa: BLE001 — a database older than the column
        return DEFAULT_REGION
    region = (row["region"] if row else None) or DEFAULT_REGION
    return region if region in REGIONS else "other"


def region_of(profile_id: str) -> str:
    """A profile's region is its owner's. `owner_id` is an account id when
    the profile was made from a signed-in console, and something else (a
    roster's label, the suite's `owner-1`) when it was not — those stand on
    the default rather than being refused a menu."""
    row = db.connect().execute(
        "SELECT owner_id FROM profiles WHERE id=?", (profile_id,)).fetchone()
    return account_region(row["owner_id"] if row else None)


def set_region(account_id: str, region: str) -> dict:
    region = (region or "").strip().lower()
    if region not in REGIONS:
        raise ValueError("that is not a region this product offers a menu for")
    conn = db.connect()
    conn.execute("UPDATE accounts SET region=? WHERE id=?", (region, account_id))
    conn.commit()
    logger.info("account %s set region -> %s", account_id, region)
    return {"account_id": account_id, "region": region,
            "providers": loadout_for(region)}


def _tapered(names: tuple[str, ...], region: str) -> list[str]:
    """Apply the policy. `american` narrows the American-region loadout to
    American, local and self-supplied providers; every other region keeps its
    own loadout — the rule is about US accounts, not about the world."""
    if policy() == "american" and region == DEFAULT_REGION:
        return [n for n in names
                if llm.origin_of(n) in ("US", "local", "any")]
    return list(names)


def loadout_for(region: str) -> list[str]:
    base = LOADOUTS.get(region, LOADOUTS["other"])
    names = tuple(dict.fromkeys(base + _LOCAL))     # ordered, de-duplicated
    return [n for n in _tapered(names, region) if n in llm._REGISTRY]


def providers_for(profile_id: str) -> list[str]:
    return loadout_for(region_of(profile_id))


def allowed(profile_id: str, name: str) -> bool:
    return name == "auto" or name in providers_for(profile_id)


def offered(profile_id: str) -> list[dict]:
    """The registry rows this profile is offered, in loadout order, each
    carrying its origin so a screen can say where a model is from."""
    by_name = {p["name"]: p for p in llm.available()}
    return [by_name[n] for n in providers_for(profile_id) if n in by_name]


def video_loadout_for(region: str) -> list[str]:
    """The video houses a region is offered, restricted to what the shelf
    can actually send to (:data:`qrme.filming.PROVIDERS`)."""
    from . import filming
    base = VIDEO_LOADOUTS.get(region, VIDEO_LOADOUTS["other"])
    if policy() == "american" and region == DEFAULT_REGION:
        base = tuple(n for n in base if VIDEO_ORIGINS.get(n) == "US")
    return [n for n in base if n in filming.PROVIDERS]


def video_providers_for(profile_id: str) -> list[str]:
    return video_loadout_for(region_of(profile_id))


def video_allowed(profile_id: str, name: str | None) -> bool:
    """`None` and `"none"` are "leave it" and "hand it back" — neither picks
    a house, so neither is refused."""
    return name in (None, "none") or name in video_providers_for(profile_id)
