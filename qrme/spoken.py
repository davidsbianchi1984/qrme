"""The voice a profile speaks with — bound by its owner, synthesized on ask.

:mod:`qrme.voiceprint` is the *cloning* machinery: your own voice, enrolled
sample by sample under an attestation, watermarked on the way out. Its
``speak`` returns a descriptor and says so plainly — *synthesis itself belongs
to whichever engine the deployment configures* — and no deployment configured
one. So every place a profile talks, the sound came from the browser's own
``speechSynthesis``, or from nowhere: a field report from a room said simply
that the audio was not working, from a person who had already built the
profile a professional voice on the engine's own surface.

    asked     can the profile speak
    mattered  with the voice its owner made for it, on the box it runs on

This module is the binding and the call. It is deliberately shaped like the
avatar market next door — the voice is made and governed on the provider's
surface, QRME holds a *reference* to it — with the one difference that
synthesis runs server-side, so the deployment holds the provider credential.

## The key is the deployment's, never a row

``ELEVENLABS_API_KEY`` lives in the host's ``.env`` beside the model key, and
nothing here writes it anywhere. A missing key refuses with the variable's
name, the way the stack's other ``${VAR:?}`` refusals do — a voice that
silently fell back to nothing is how this gap survived as long as it did.

## What crosses the wire

The text of a turn that the caller already holds, and audio back. The far
side is one host, named below, and the request carries the text, the voice
reference and the key — never who asked, never the room, never the profile's
memory. ``say`` refuses text over :data:`MAX_SAY` outright: a synthesis bill
is real money, and a runaway caller should hit a wall rather than a balance.

## The mark rides along

Every synthesis is stamped through :mod:`qrme.watermark` exactly as a text
turn is, and the credential id returns beside the audio. The AI mark on the
seat disclosed the speaker already; the stamp is what makes the *utterance*
checkable afterwards, which is the standard everything generated here meets.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from . import db, i18n, offline, watermark

PROVIDERS = ("elevenlabs",)

#: One utterance's ceiling, in characters. A room turn fits with room to
#: spare; a pasted novel does not, on purpose.
MAX_SAY = 2400

_HOST = "https://api.elevenlabs.io"
_MODEL = "eleven_multilingual_v2"


class SpokenError(ValueError):
    """A binding or synthesis refusal, in a sentence a person can act on."""


def bound(profile_id: str) -> dict:
    """Which voice this profile speaks with, or the empty binding.

    One shape either way — a payload that grows keys only when something is
    bound hands every shell ``undefined`` on the case it meets most.
    """
    row = db.connect().execute(
        "SELECT * FROM profile_voices WHERE profile_id=?",
        (profile_id,)).fetchone()
    if row is None:
        return {"profile_id": profile_id, "provider": "", "voice_id": "",
                "label": "", "bound_at": None, "speaks": False}
    return {"profile_id": profile_id, "provider": row["provider"],
            "voice_id": row["voice_id"], "label": row["label"],
            "bound_at": row["bound_at"], "speaks": True}


def bind(profile_id: str, provider: str, voice_id: str,
         label: str = "") -> dict:
    """The owner points the profile at a voice. Empty ``voice_id`` unbinds.

    A reference, not an import: the voice stays governed on the provider's
    surface, where its consent and its verification live. What this row
    asserts is only *this profile speaks with that*.
    """
    conn = db.connect()
    if not voice_id.strip():
        conn.execute("DELETE FROM profile_voices WHERE profile_id=?",
                     (profile_id,))
        conn.commit()
        return bound(profile_id)
    if provider not in PROVIDERS:
        raise SpokenError(i18n.fill(i18n.MUST_BE_ONE_OF, field="provider",
                                    choices=", ".join(PROVIDERS)))
    conn.execute(
        "INSERT INTO profile_voices (profile_id, provider, voice_id, label,"
        " bound_at) VALUES (?,?,?,?,?)"
        " ON CONFLICT (profile_id) DO UPDATE SET provider=excluded.provider,"
        " voice_id=excluded.voice_id, label=excluded.label,"
        " bound_at=excluded.bound_at",
        (profile_id, provider, voice_id.strip(), label.strip(), db.utcnow()))
    conn.commit()
    return bound(profile_id)


def _synthesize(voice_id: str, text: str, key: str,
                on_behalf_of: str) -> bytes:
    """One call to the engine. Split out so a test can stand in for the
    network without standing in for any of the rules around it.

    The offline check lives here, at the socket, for the reason `visits`
    gives: a second caller added tomorrow inherits it instead of
    remembering it. ``on_behalf_of`` is the profile whose voice this is —
    the errand has an owner, so the ledger gets one.
    """
    url = f"{_HOST}/v1/text-to-speech/{voice_id}?output_format=mp3_44100_128"
    offline.allow(url, "the spoken voice", on_behalf_of)
    req = urllib.request.Request(
        url,
        data=json.dumps({"text": text, "model_id": _MODEL}).encode("utf-8"),
        headers={"content-type": "application/json", "xi-api-key": key},
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read()
    except urllib.error.HTTPError as exc:
        raise SpokenError(i18n.fill(i18n.ENGINE_REFUSED,
                                    code=exc.code)) from exc
    except urllib.error.URLError as exc:
        raise SpokenError(
            "the voice engine could not be reached from this deployment"
        ) from exc


def say(profile_id: str, text: str) -> tuple[bytes, dict]:
    """Text in, audio out, with the stamp beside it.

    Returns ``(audio_bytes, about)`` where ``about`` carries the mime type,
    the watermark credential id, and which binding spoke — everything a route
    needs to answer honestly without this module knowing about HTTP.
    """
    text = (text or "").strip()
    if not text:
        raise SpokenError("nothing to say")
    if len(text) > MAX_SAY:
        raise SpokenError(i18n.fill(i18n.SAY_CEILING, max=MAX_SAY))
    row = bound(profile_id)
    if not row["speaks"]:
        raise SpokenError(
            "this profile has no spoken voice bound — its owner sets one "
            "under Voice")
    key = os.environ.get("ELEVENLABS_API_KEY", "")
    if not key:
        raise SpokenError(
            "this deployment has no ELEVENLABS_API_KEY configured — the "
            "binding exists, the engine does not")
    audio = _synthesize(row["voice_id"], text, key, profile_id)
    credential = watermark.stamp(profile_id, "voice", text)
    return audio, {
        "mime": "audio/mpeg",
        "watermark_id": credential.get("watermark_id", ""),
        "provider": row["provider"],
        "label": row["label"],
    }
