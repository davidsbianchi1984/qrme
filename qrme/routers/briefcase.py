"""Handing a profile something to read.

Five doors, all scoped to the conversation rather than to the profile: what
you hand a profile is yours, not its, and the person after you in the queue
inherits none of it. See ``briefcase.py`` for why this is deliberately not a
source item.

The upload door takes the file bytes raw, the same shape ``wall.upload_media``
uses and for the same reason — the console posts the bytes it already holds,
and the kind is read from the bytes rather than from what the sender claims.
The link door is ordinary JSON, because a URL is not a file.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from .. import briefcase, llm, media, offline
from ..common import (interactor_or_404, profile_or_404,
                      require_may_speak)

router = APIRouter()


class LinkImport(BaseModel):
    interactor_id: str
    url: str = Field(min_length=4, max_length=2000)
    title: str = ""
    note: str = ""


def _pair(profile_id: str, interactor_id: str) -> dict:
    profile = profile_or_404(profile_id)
    interactor_or_404(interactor_id)
    return dict(profile)


#: A departed or terminated profile takes nothing new.
#:
#: Importing is not a passive store: the distillation runs the profile's own
#: provider, so handing something over puts the profile to work. A memorial is
#: frozen and a terminated profile is gone, and neither should be reading on
#: somebody's behalf.
#:
#: `require_may_speak` rather than `require_may_publish`, deliberately. A
#: restricted profile may still answer somebody it already knows — `chat` keeps
#: that nuance — and a briefcase is only ever useful mid-conversation, so
#: gating it harder than the conversation it belongs to would close a door the
#: door beside it leaves open. Nothing here is published: the digest is read by
#: this pair and nobody else.
#:
#: Reading the briefcase back and taking things out of it stay open in every
#: status, for the same reason a departed profile's memory remains viewable —
#: what you handed over is yours, and a memorial must not be a place your
#: documents are stuck in.
#:
#: Called inline in each handler rather than through a helper: the guard in
#: `test_a_memorial_does_not_keep_posting.py` reads the handler's own source,
#: and a gate one indirection away is one a reader cannot see either.


@router.post("/profiles/{profile_id}/briefcase/link", status_code=201)
def import_link(profile_id: str, body: LinkImport,
                request: Request) -> dict:
    """Read a page once and keep it for the rest of the conversation.

    An offline deployment does not fetch, and a page that will not load is
    not a failure to import — the item lands unread, carrying whatever the
    person said it was, and the profile is told plainly it has not seen it.
    """
    require_may_speak(_pair(profile_id, body.interactor_id))
    url = body.url.strip()
    if not url.lower().startswith(("http://", "https://")):
        raise HTTPException(422, "a link starts with http:// or https://")
    text, was_read, page_title = briefcase.read_link(url, profile_id)
    title = (body.title or "").strip() or page_title or url
    try:
        return briefcase.add(
            profile_id, body.interactor_id, kind="link", title=title,
            text=text, read=was_read, note=body.note, source=url,
            provider=llm.provider_for_profile(
                profile_id, cloud=request.app.state.cloud))
    except briefcase.BriefcaseError as exc:
        raise HTTPException(exc.status, exc.message) from None


@router.post("/profiles/{profile_id}/briefcase/file", status_code=201)
async def import_file(profile_id: str, request: Request,
                      interactor_id: str, filename: str = "",
                      note: str = "", title: str = "") -> dict:
    """A photograph, a video or a document, raw in the request body.

    Documents are read here and never stored as files: the words come out,
    the bytes go no further. Pictures are recorded as handed over and
    explicitly *not* read — a profile that describes a photograph it
    cannot see is the worse outcome. A video is heard where the stack has
    ears (the words said in it, never the picture in the frames); without
    them it takes the same held-not-read posture.
    """
    require_may_speak(_pair(profile_id, interactor_id))
    data = await request.body()
    if not data:
        raise HTTPException(422, "the upload arrived empty")
    try:
        # `media._sniff` refuses bytes it cannot name, in a sentence that
        # lists what this deployment does take — the same refusal the wall's
        # upload door gives, because it is the same reader.
        kind, text, was_read = briefcase.read_file(data, filename or None,
                                                   on_behalf_of=profile_id)
    except media.MediaError as exc:
        raise HTTPException(exc.status, exc.message) from None
    name = (filename or "").strip()[:120]
    try:
        return briefcase.add(
            profile_id, interactor_id, kind=kind,
            title=(title or "").strip() or name or kind.capitalize(),
            text=text, read=was_read, note=note, source=name or None,
            size=len(data),
            provider=llm.provider_for_profile(
                profile_id, cloud=request.app.state.cloud))
    except briefcase.BriefcaseError as exc:
        raise HTTPException(exc.status, exc.message) from None


@router.get("/profiles/{profile_id}/briefcase")
def list_briefcase(profile_id: str, interactor_id: str,
                   limit: int = 50) -> dict:
    """What this conversation is carrying, newest first.

    ``chars`` against ``digest_chars`` is the point made visible: the long
    number was read once, the short number is what recurs.
    """
    _pair(profile_id, interactor_id)
    items = briefcase.items(profile_id, interactor_id, limit=limit)
    return {"profile_id": profile_id, "interactor_id": interactor_id,
            "items": items, "max_items": briefcase.MAX_ITEMS,
            "offline": offline.enabled()}


@router.get("/profiles/{profile_id}/briefcase/{item_id}")
def read_briefcase_item(profile_id: str, interactor_id: str,
                        item_id: str) -> dict:
    """One item with the text that was extracted, for a person to check.

    The full text lives here and only here — it is never what the prompt
    carries. Somebody who wants to know what the profile actually took from
    their file reads it on this door.
    """
    _pair(profile_id, interactor_id)
    row = briefcase.get(profile_id, interactor_id, item_id)
    if row is None:
        raise HTTPException(404, "no such imported item in this conversation")
    return {**briefcase.facade(row), "text": row["text"] or ""}


@router.delete("/profiles/{profile_id}/briefcase/{item_id}",
               status_code=204)
def remove_briefcase_item(profile_id: str, interactor_id: str,
                          item_id: str) -> None:
    """Take it back. The profile stops carrying it from the next turn on."""
    _pair(profile_id, interactor_id)
    if not briefcase.remove(profile_id, interactor_id, item_id):
        raise HTTPException(404, "no such imported item in this conversation")
