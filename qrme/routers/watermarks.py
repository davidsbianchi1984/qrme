"""Synthetic-media watermark verification: anyone holding a piece of
QRME-generated content can check its credential — no token required, since
the whole point is that third parties (platforms, viewers, journalists)
can verify what they're looking at."""

from __future__ import annotations

from pydantic import BaseModel

from fastapi import APIRouter, HTTPException

from .. import watermark

router = APIRouter()


class WatermarkVerify(BaseModel):
    watermark_id: str
    content: str | None = None         # present it to check for tampering


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
