"""The homepage a person builds — read by anyone, edited by its owner."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from .. import pages
from ..common import profile_or_404, require_owner

router = APIRouter()


class PageEdit(BaseModel):
    """Every field optional, and absent means *leave it alone*.

    A partial edit must not blank the fields it did not mention — that is the
    difference between an edit form and a delete button, and clients get it
    wrong in exactly one direction.
    """
    theme: str | None = Field(None, description="One of GET /pages/themes.")
    accent: str | None = Field(None, description="#rrggbb.")
    layout: str | None = None
    tagline: str | None = Field(None, max_length=pages.MAX_TAGLINE)
    about: str | None = Field(None, max_length=pages.MAX_ABOUT)
    top_friends: list[str] | None = Field(
        None, description=f"Up to {pages.TOP_FRIENDS} friend profile ids, in "
                          "the order they should appear.")


@router.get("/pages/themes")
def list_themes() -> dict:
    """The theme presets. A closed set on purpose — see `qrme/pages.py`."""
    return {"themes": pages.theme_catalog(), "layouts": list(pages.LAYOUTS),
            "top_friends": pages.TOP_FRIENDS}


@router.get("/profiles/{profile_id}/page")
def get_page(profile_id: str) -> dict:
    """The page as a visitor sees it."""
    profile_or_404(profile_id)
    return pages.page(profile_id)


@router.put("/profiles/{profile_id}/page")
def edit_page(profile_id: str, body: PageEdit, request: Request) -> dict:
    """Owner edits their page. Returns the owner's view, which includes a
    blocked about-text and the reason so it can be fixed."""
    profile_or_404(profile_id)
    require_owner(profile_id, request)
    try:
        return pages.set_page(
            profile_id, theme=body.theme, accent=body.accent,
            layout=body.layout, tagline=body.tagline, about=body.about,
            top_friends=body.top_friends)
    except pages.PageError as exc:
        raise HTTPException(422, str(exc)) from None
