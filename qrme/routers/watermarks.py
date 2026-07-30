"""Synthetic-media watermark verification: anyone holding a piece of
QRME-generated content can check its credential — no token required, since
the whole point is that third parties (platforms, viewers, journalists)
can verify what they're looking at."""

from __future__ import annotations

from pydantic import BaseModel, Field

from fastapi import APIRouter, HTTPException, Request

from .. import watermark
from ..common import profile_or_404, require_owner

router = APIRouter()


class WatermarkVerify(BaseModel):
    watermark_id: str
    content: str | None = None         # present it to check for tampering


class WatermarkRecover(BaseModel):
    """Text on its own, with no credential id — who wrote it?"""

    content: str


class WatermarkDesignSet(BaseModel):
    """The owner's custom display watermark. Empty fields fall back to the
    defaults; clearing both resets to the default design. The AI designation
    cannot be designed away — a label without "AI" is rendered with it."""
    mark: str | None = Field(default=None, max_length=8)
    label: str | None = Field(default=None, max_length=60)


@router.get("/profiles/{profile_id}/watermark")
def get_watermark_design(profile_id: str) -> dict:
    """The profile's display watermark — public, since every render of the
    profile's generated work carries it."""
    profile_or_404(profile_id)
    return watermark.design(profile_id)


@router.put("/profiles/{profile_id}/watermark")
def set_watermark_design(profile_id: str, body: WatermarkDesignSet,
                         request: Request) -> dict:
    """Owner designs the profile's watermark (mark + label). Whatever the
    design, the rendered line always declares AI."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    return watermark.set_design(profile_id, body.mark, body.label)


@router.post("/watermarks/verify")
def watermark_check(body: WatermarkVerify) -> dict:
    """Verify content against its credential: valid + whether the presented
    content still matches the hash issued at creation."""
    result = watermark.verify(body.watermark_id, body.content)
    if result is None:
        raise HTTPException(
            404, "no such watermark — this content was not credentialed by "
                 "this QRME deployment")
    return result


@router.post("/watermarks/recover")
def watermark_recover(body: WatermarkRecover) -> dict:
    """The other direction: who produced this text, from the text alone.

    `/watermarks/verify` answers "does this content match *this* credential",
    which needs the id up front and fails on a single edited character. This
    answers "whose work is this", with no id, and keeps answering after the
    text has been edited — the field drawing's extract-and-reconstruct step.
    Never a bare yes: the reply carries the matched-window counts and the
    similarity so the claim can be checked.
    """
    return watermark.recover(body.content)


# Registered *after* every literal `/watermarks/...` route, and it has to stay
# that way. Starlette matches in registration order, so a variable segment
# placed first answers the literal paths too, and the literal handler is never
# reached — silently, with no error and nothing in the logs.
#
# It does not fix everything: `GET /watermarks/verify` still lands here, because
# there is no GET route at that path and `verify` is a legal watermark id. A 404
# is the right answer to "fetch the watermark called verify". What the ordering
# buys is that adding one later works rather than being quietly unreachable.
# `tests/test_routing.py` asserts the property for every route in the app.
@router.get("/watermarks/{watermark_id}")
def watermark_credential(watermark_id: str) -> dict:
    """Resolve a synthetic-media credential: which profile produced the
    media, what kind it is, when it was issued, and the content hash."""
    result = watermark.verify(watermark_id)
    if result is None:
        raise HTTPException(
            404, "no such watermark — this content was not credentialed by "
                 "this QRME deployment")
    return result
