"""Per-profile language: the persona speaks it everywhere.

A synthetic profile has one voice across every surface — chat, composed
posts, room turns, robot speech. Setting a language makes that voice speak
it natively: the directive rides on the persona system prompt, so every
generation site inherits it without per-endpoint plumbing. Owner-set,
like the model preference.
"""

from __future__ import annotations

SUPPORTED: dict[str, str] = {
    "en": "English",
    "es": "Español",
    "fr": "Français",
    "de": "Deutsch",
    "pt": "Português",
    "it": "Italiano",
    "ja": "日本語",
    "zh": "中文",
    "hi": "हिन्दी",
    "ar": "العربية",
}

DEFAULT = "en"

# "pre": the persona speaks the language natively everywhere (default).
# "on_demand": the persona keeps its original voice; the owner translates
# selectively via POST /profiles/{id}/translate.
MODES = ("pre", "on_demand")


def get_pref(profile_id: str) -> tuple[str, str]:
    from . import db
    row = db.connect().execute(
        "SELECT language, mode FROM language_prefs WHERE profile_id=?",
        (profile_id,)).fetchone()
    return (row["language"], row["mode"]) if row else (DEFAULT, "pre")


def get_language(profile_id: str) -> str:
    return get_pref(profile_id)[0]


def effective_language(profile_id: str) -> str:
    language, mode = get_pref(profile_id)
    return language if mode == "pre" else DEFAULT


def set_language(profile_id: str, language: str, mode: str = "pre") -> str:
    if language not in SUPPORTED:
        raise ValueError(f"unknown language {language!r}")
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}")
    from . import db
    conn = db.connect()
    conn.execute(
        "INSERT INTO language_prefs (profile_id, language, mode, updated_at)"
        " VALUES (?,?,?,?)"
        " ON CONFLICT(profile_id) DO UPDATE SET language=excluded.language,"
        " mode=excluded.mode, updated_at=excluded.updated_at",
        (profile_id, language, mode, db.utcnow()))
    conn.commit()
    return language


def translate(profile_id: str, text: str, to: str | None = None,
              cloud=None) -> dict:
    """Translate anything the owner runs across — an interactor's message,
    a room turn, a listing — using the profile's own model. The offline stub
    cannot translate free text, and says so instead of pretending."""
    from . import llm
    target = to or get_language(profile_id)
    if target not in SUPPORTED:
        raise ValueError(f"unknown language {target!r}")
    if target == DEFAULT:
        return {"text": text, "translation": text, "language": target,
                "engine": "none", "note": "target language is English"}
    effective = llm.resolve_choice(llm.get_choice(profile_id))
    if effective == "stub":
        return {"text": text, "translation": text, "language": target,
                "engine": "stub",
                "note": "the offline stub cannot translate free text — "
                        "configure a model provider for live translation"}
    system = (f"You are a precise translator. Translate the user's text into "
              f"{SUPPORTED[target]} ({target}). Preserve meaning, tone, and "
              "formatting. Output only the translation.")
    translation = llm.provider_for_profile(profile_id, cloud=cloud).generate(
        system, [{"role": "user", "content": text}])
    return {"text": text, "translation": translation, "language": target,
            "engine": effective}


def directive(language: str) -> str:
    if language == DEFAULT:
        return ""
    return (f"\nSpeak entirely in {SUPPORTED[language]} ({language}) — every "
            "reply, post, and spoken line, while staying fully in character.")
