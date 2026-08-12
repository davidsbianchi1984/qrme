"""Character-card import: a V2/V3 card as a profile seed.

The interoperability ask the research heard most often from persona
hobbyists: years of character cards (the SillyTavern `chara_card_v2` /
`chara_card_v3` shape, as raw JSON or embedded in a PNG's text chunk)
that no platform lets them carry in. This module reads both forms and
maps what a card honestly is — a name, a described identity, a greeting,
example dialogue — onto QRME's own profile shape.

What it refuses to carry, it names. A card's `system_prompt`,
`post_history_instructions` and jailbreak blocks are instructions aimed
at somebody else's model harness; importing them verbatim would hand a
downloaded file the same authority as the platform's own guardrails.
They are withheld, and the response says so item by item — the same
honest shape the license manifest uses, because a quiet omission and a
lie differ only in tense.
"""

from __future__ import annotations

import base64
import json
import struct
import zlib


class CardError(ValueError):
    """A card that cannot be read as one."""


#: Card fields that never ride in: harness instructions, not identity.
WITHHELD_FIELDS = ("system_prompt", "post_history_instructions", "jailbreak")

#: PNG text-chunk keywords the ecosystem embeds cards under.
_PNG_KEYWORDS = (b"chara", b"ccv3")

_PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def _png_embedded_card(raw: bytes) -> dict:
    """Walk the PNG chunks for a `chara`/`ccv3` text chunk and decode the
    base64 JSON inside it. Pure structure — no image library, no pixels."""
    if not raw.startswith(_PNG_MAGIC):
        raise CardError("not a PNG — a card image starts with the PNG "
                        "signature")
    pos = len(_PNG_MAGIC)
    while pos + 8 <= len(raw):
        length, kind = struct.unpack(">I4s", raw[pos:pos + 8])
        data = raw[pos + 8:pos + 8 + length]
        pos += 12 + length            # length + kind + data + crc
        if kind == b"tEXt":
            keyword, _, text = data.partition(b"\x00")
        elif kind == b"iTXt":
            keyword, _, rest = data.partition(b"\x00")
            if len(rest) < 4:
                continue
            compressed = rest[0:1] == b"\x01"
            # compression method byte, then two null-terminated fields
            tail = rest[2:]
            for _ in range(2):
                _, _, tail = tail.partition(b"\x00")
            text = zlib.decompress(tail) if compressed else tail
        else:
            continue
        if keyword in _PNG_KEYWORDS:
            try:
                return json.loads(base64.b64decode(text))
            except Exception:
                raise CardError("the image carries a card chunk that does "
                                "not decode as one") from None
    raise CardError("no character card is embedded in this image — the "
                    "PNG has no chara/ccv3 text chunk")


def parse(card: dict | None, content_b64: str | None) -> dict:
    """Normalize a card from raw JSON (``card``) or a PNG (``content``,
    base64). Returns the fields carried and the ones withheld, named."""
    if card is None and not content_b64:
        raise CardError("hand over a card: `card` as JSON, or `content` "
                        "as a base64 PNG with one embedded")
    if card is None:
        try:
            raw = base64.b64decode(content_b64, validate=True)
        except Exception:
            raise CardError("the image could not be read — it is not "
                            "base64") from None
        card = _png_embedded_card(raw)

    spec = card.get("spec")
    if spec not in ("chara_card_v2", "chara_card_v3"):
        raise CardError("unrecognized card: expected spec chara_card_v2 "
                        "or chara_card_v3")
    data = card.get("data") or {}
    name = (data.get("name") or "").strip()
    if not name:
        raise CardError("the card names nobody — `data.name` is empty")

    persona_parts = [
        (data.get("description") or "").strip(),
        (data.get("personality") or "").strip(),
        (data.get("scenario") or "").strip(),
    ]
    persona = "\n\n".join(p for p in persona_parts if p)
    if not persona:
        raise CardError("the card carries no identity — description, "
                        "personality and scenario are all empty")

    withholdings = [
        {"item": field,
         "reason": "harness instructions from the card's home platform, "
                   "not identity; the platform's own guardrails stand"}
        for field in WITHHELD_FIELDS if (data.get(field) or "").strip()
    ]

    return {
        "name": name,
        "persona": persona,
        "greeting": (data.get("first_mes") or "").strip() or None,
        "example_dialogue": (data.get("mes_example") or "").strip() or None,
        "creator_notes": (data.get("creator_notes") or "").strip() or None,
        "tags": [t for t in (data.get("tags") or []) if isinstance(t, str)],
        "spec": spec,
        "withholdings": withholdings,
    }
