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


def get_language(profile_id: str) -> str:
    from . import db
    row = db.connect().execute(
        "SELECT language FROM language_prefs WHERE profile_id=?",
        (profile_id,)).fetchone()
    return row["language"] if row else DEFAULT


def set_language(profile_id: str, language: str) -> str:
    if language not in SUPPORTED:
        raise ValueError(f"unknown language {language!r}")
    from . import db
    conn = db.connect()
    conn.execute(
        "INSERT INTO language_prefs (profile_id, language, updated_at)"
        " VALUES (?,?,?)"
        " ON CONFLICT(profile_id) DO UPDATE SET language=excluded.language,"
        " updated_at=excluded.updated_at",
        (profile_id, language, db.utcnow()))
    conn.commit()
    return language


def directive(language: str) -> str:
    if language == DEFAULT:
        return ""
    return (f"\nSpeak entirely in {SUPPORTED[language]} ({language}) — every "
            "reply, post, and spoken line, while staying fully in character.")
