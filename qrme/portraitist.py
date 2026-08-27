"""Painted from words: the prompted road into the avatar registry.

The briefs have said since the collection shipped that they exist "so a
generator, an illustrator, or a contractor can be handed the exact text"
— and no generator was ever wired. This is the wire, behind a seam:
``QRME_IMAGE_KEY`` (an OpenAI-images key today; the constant below is
the only place the provider lives), and with no key the door refuses in
a sentence rather than faking a face.

Two facts ride every painted portrait. It is painted **in the house
style** (`avatars.STYLE`), so a minted face sits beside the shipped
collection as one deliberate set. And it is painted **at the profile's
effective age** — the persona has aged for as long as `aging_enabled`
profiles have existed, and the face never did; screen 44 promised "the
face, aged as you choose," and this is the half that makes it true.
Ask again next year and the portrait is a year older.

Fictional profiles only. Painting a face for a ``self`` or
``other_person`` profile would be fabricating a likeness for a real
person — the exact thing the rights machinery exists to prevent — so
the door refuses those outright; a real face arrives by photograph and
recorded grant, never by prompt.
"""

from __future__ import annotations

import base64
import json
import os
import urllib.request

from . import avatars, offline, persona

_URL = "https://api.openai.com/v1/images/generations"
_MODEL_ENV = "QRME_IMAGE_MODEL"
_KEY_ENV = "QRME_IMAGE_KEY"
_DEFAULT_MODEL = "gpt-image-1"


class PaintingUnavailable(RuntimeError):
    """No image service is configured — said, never faked."""


def describe(profile: dict, words: str = "") -> str:
    """The exact text a generator is handed — the brief's own promise.

    The house style, the persona's own description, the profile's age as
    it is *today*, the invented-person constraint that survives being
    pasted anywhere, and whatever the owner added in their own words.
    """
    parts = [avatars.STYLE]
    age = persona.effective_age(profile)
    if age is not None:
        parts.append(f"The subject reads as about {age} years old.")
    about = (profile.get("persona") or "").strip()
    if about:
        parts.append(f"Character: {about[:600]}")
    if words.strip():
        parts.append(f"Direction from the owner: {words.strip()[:300]}")
    parts.append(
        "This is an invented person — not a likeness of any real "
        "individual, living or dead.")
    return "\n".join(parts)


def paint(profile: dict, words: str = "") -> tuple[bytes, str, dict]:
    """Portrait bytes for one profile, plus the prompt and params that
    made them — kept for the registry row, so the face's provenance
    survives next to the face."""
    key = os.environ.get(_KEY_ENV, "").strip()
    if not key:
        raise PaintingUnavailable(
            "no painting service is configured — the deployment has no "
            "image key")
    prompt = describe(profile, words)
    params = {"model": os.environ.get(_MODEL_ENV, _DEFAULT_MODEL),
              "size": "1024x1024", "quality": "medium"}
    offline.allow(_URL, "painting a portrait from this profile's brief",
                  on_behalf_of=profile["id"])
    body = json.dumps({"prompt": prompt, **params}).encode()
    req = urllib.request.Request(
        _URL, data=body,
        headers={"authorization": f"Bearer {key}",
                 "content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as answer:
        got = json.loads(answer.read())
    data = base64.b64decode(got["data"][0]["b64_json"])
    return data, prompt, params
