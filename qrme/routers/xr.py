"""The XR shelf: which headsets and glasses can stand in the rooms.

Public and unauthenticated, like the sign-in providers list whose honesty
it borrows: somebody deciding whether to put the headset on has not
signed in yet.
"""

from __future__ import annotations

from fastapi import APIRouter

from .. import xr

router = APIRouter()


@router.get("/rooms/xr-platforms")
def xr_platforms() -> dict:
    return xr.shelf()
