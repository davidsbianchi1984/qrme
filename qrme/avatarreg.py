"""The avatar registry: one ledger for every face, three roads in.

The design brief, in the owner's own framing: *seeding from the one
already built, prompt-to-generate, and picking from the curated list —
and keep the provider swappable.* The shape it asked for is the shape
this module is::

    profile.avatar_ref -> avatar_registry.id
        -> {source, provider, provider_asset_id, render_variants, rights}

No surface — chat, feed, wall, room, beacon, hologram — ever calls a
provider. That was already this product's law (`avatars.render` is the
one shape every surface reads); the registry slots underneath it, so a
provider swap, a re-generation, or a takedown is a **data operation**,
never a deploy.

## The three roads, and the fourth

* **curated_library** — the deployment's own shelf. The owner runs his
  avatars on ElevenLabs and asked for them to be the defaults anybody
  can claim; the provider offers no listing API for them, so the shelf
  is fed by the operator's own upload door (the signup key is the
  operator's secret) — exported once from the provider's surface,
  minted here with provenance, offered to everyone. Anybody wanting
  their own builds them on their own account and uploads to their own
  shelf. The shelf never empties: with no minted rows it serves the 34
  starter portraits, the same never-an-empty-picker rule the voice
  library keeps.
* **prompted** — painted from words by an image provider behind a seam
  (``QRME_IMAGE_KEY``); with no key configured the door refuses in a
  sentence rather than faking a face.
* **uploaded** — a person's own picture, the flow that already existed,
  now with a registry row instead of a bare string.
* **seeded** — an asset that already exists at a provider, referenced by
  its opaque id. The adapter records it; it never pretends to own it.

## The two rules the brief did not carry

The estate's own, and they ride the row rather than the surfaces. A
**synthetic** face (curated, prompted, seeded-synthetic) gets the AI
mark burned into its bytes at mint time — once, when it is made, never
per fetch. An **authentic** photograph is never marked: stamping a real
face with the AI mark is a false statement in the exact direction the
mark exists to prevent. ``rights`` is required on every row and points
at the same likeness vocabulary the objection lifecycle already
enforces — a disputed row cannot be claimed, and retiring a row clears
it off every profile it was backing, which is what makes a takedown a
data operation.
"""

from __future__ import annotations

import hashlib
import io
import json

from . import db, media

#: What a row may say about whose face this is. `invented` carries no
#: likeness rights; `granted` records that a real person said yes and the
#: objection lifecycle can withdraw it; `self` is the account's own face.
LIKENESS = ("invented", "granted", "self")

SOURCES = ("seeded", "prompted", "curated_library", "uploaded")

STATUSES = ("active", "pending", "failed", "retired", "disputed")


class NotYourRow(ValueError):
    """Refused: that registry row belongs to somebody else."""


class RowUnavailable(ValueError):
    """Refused: retired or disputed rows are not claimable."""


def _burn(data: bytes) -> bytes:
    """The AI mark, into the pixels, at mint time.

    The offline tool (`tools/mark_portraits.py`) argued against burning at
    request time — an imaging library in the runtime and a redraw on every
    fetch for a mark that never changes. Minting is the other case: the
    mark is drawn once, when the face is made, exactly like the document
    watermark. Geometry mirrors the tool's so a minted face sits beside a
    shipped one as one collection.
    """
    from PIL import Image, ImageDraw, ImageFont
    img = Image.open(io.BytesIO(data)).convert("RGB")
    w, _ = img.size
    pad = round(w * 0.035)
    size = round(w * 0.115)
    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    except OSError:                                    # pragma: no cover
        font = ImageFont.load_default()
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    text_w = draw.textlength("AI", font=font)
    box_h = round(size * 1.65)
    box_w = round(text_w + size * 2.35)
    x1, y1 = w - pad, pad + box_h
    x0, y0 = x1 - box_w, pad
    draw.rounded_rectangle((x0, y0, x1, y1), radius=box_h // 2,
                           fill=(9, 7, 24, 205))
    cx, cy = x0 + size * 0.85, (y0 + y1) / 2
    r = size * 0.42
    draw.polygon([(cx, cy - r), (cx + r * 0.42, cy - r * 0.42),
                  (cx + r, cy), (cx + r * 0.42, cy + r * 0.42),
                  (cx, cy + r), (cx - r * 0.42, cy + r * 0.42),
                  (cx - r, cy), (cx - r * 0.42, cy - r * 0.42)],
                 fill=(255, 255, 255, 235))
    draw.text((x0 + size * 1.6, cy), "AI", font=font, anchor="lm",
              fill=(255, 255, 255, 242))
    img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
    out = io.BytesIO()
    img.save(out, format="WEBP", quality=88)
    return out.getvalue()


def mint(*, data: bytes | None = None, asset: str | None = None,
         source: str, provider: str = "internal",
         provider_asset_id: str | None = None,
         owner_account_id: str | None = None,
         prompt_text: str | None = None,
         generation_params: dict | None = None,
         likeness: str = "invented", basis: str | None = None,
         store_for: str = "library") -> dict:
    """One face onto the ledger, by whichever road.

    ``data`` is master bytes (stored through `media.save`, marked first
    when the likeness is not a real person's); ``asset`` is a reference
    the provider already serves. Exactly one of the two.
    """
    from . import i18n
    if source not in SOURCES:
        raise ValueError(i18n.fill(i18n.MUST_BE_ONE_OF, field="source",
                                   choices=", ".join(SOURCES)))
    if likeness not in LIKENESS:
        raise ValueError(i18n.fill(i18n.MUST_BE_ONE_OF, field="likeness",
                                   choices=", ".join(LIKENESS)))
    if (data is None) == (asset is None):
        raise ValueError("exactly one of bytes or an asset reference")
    marked = False
    checksum = None
    if data is not None:
        # The mark rides synthetic faces only. An authentic photograph
        # (likeness `self` or `granted`) is never stamped — a false "AI"
        # is the failure the mark exists to prevent, mirrored.
        if likeness == "invented":
            data = _burn(data)
            marked = True
        checksum = hashlib.sha256(data).hexdigest()
        saved = media.save(store_for, data, name="portrait.webp",
                           alt="a portrait", ai_marked=marked)
        asset = saved["url"]
    row_id = db.new_id("ava")
    conn = db.connect()
    conn.execute(
        "INSERT INTO avatar_registry (id, owner_account_id, profile_id,"
        " source, provider, provider_asset_id, prompt_text,"
        " generation_params, asset, render_variants, rights, status,"
        " checksum, marked, created_at)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?,'active',?,?,?)",
        (row_id, owner_account_id, None, source, provider,
         provider_asset_id, prompt_text,
         json.dumps(generation_params) if generation_params else None,
         asset, json.dumps({"portrait": asset}),
         json.dumps({"likeness": likeness, "basis": basis}),
         checksum, int(marked), db.utcnow()))
    conn.commit()
    return row(row_id)


def row(registry_id: str) -> dict:
    got = db.connect().execute(
        "SELECT * FROM avatar_registry WHERE id=?",
        (registry_id,)).fetchone()
    if got is None:
        raise KeyError("no such registry row")
    out = dict(got)
    out["rights"] = json.loads(out["rights"])
    out["render_variants"] = json.loads(out["render_variants"] or "{}")
    if out["generation_params"]:
        out["generation_params"] = json.loads(out["generation_params"])
    out["marked"] = bool(out["marked"])
    return out


def shelf(owner_account_id: str | None = None) -> list[dict]:
    """The claimable shelf: the deployment's when no account is named,
    somebody's own otherwise. Retired and disputed rows stay off it —
    they are records, not offers."""
    rows = db.connect().execute(
        "SELECT id FROM avatar_registry WHERE status='active' AND "
        + ("owner_account_id IS NULL" if owner_account_id is None
           else "owner_account_id=?")
        + " ORDER BY created_at DESC, rowid DESC",
        () if owner_account_id is None else (owner_account_id,)).fetchall()
    return [row(r["id"]) for r in rows]


def claim(registry_id: str, profile_id: str) -> dict:
    """Point a profile's face at a registry row.

    The render pipeline is untouched — `avatars.set_avatar` writes the
    same asset column every surface already reads; what changes is that
    the face now has a ledger row a takedown can find."""
    got = row(registry_id)
    if got["status"] != "active":
        from . import i18n
        raise RowUnavailable(i18n.fill(
            i18n.FACE_UNAVAILABLE, status=i18n.Term(got["status"])))
    from . import avatars
    conn = db.connect()
    conn.execute("UPDATE profiles SET avatar_ref=? WHERE id=?",
                 (registry_id, profile_id))
    conn.commit()
    return avatars.set_avatar(profile_id, got["asset"])


def retire(registry_id: str, *, because: str,
           owner_account_id: str | None = None) -> dict:
    """The takedown as a data operation.

    The row keeps its record (retired, never deleted) and every profile
    it was backing falls back to the placeholder — a face withdrawn is
    withdrawn everywhere at once, which is the whole reason the ledger
    exists."""
    got = row(registry_id)
    if owner_account_id is not None \
            and got["owner_account_id"] != owner_account_id:
        raise NotYourRow("that face belongs to somebody else's shelf")
    conn = db.connect()
    conn.execute(
        "UPDATE avatar_registry SET status='retired', retired_at=?,"
        " retired_because=? WHERE id=?",
        (db.utcnow(), because, registry_id))
    conn.execute(
        "UPDATE profiles SET avatar=NULL, avatar_ref=NULL WHERE avatar_ref=?",
        (registry_id,))
    conn.commit()
    return row(registry_id)


def dispute(registry_id: str) -> dict:
    """A face somebody contests stops being claimable while the objection
    lifecycle does its work; profiles already showing it keep it until the
    dispute resolves into a retire — contested is not yet decided."""
    conn = db.connect()
    conn.execute("UPDATE avatar_registry SET status='disputed' WHERE id=?",
                 (registry_id,))
    conn.commit()
    return row(registry_id)
