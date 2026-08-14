"""How a synthetic profile is shown, as distinct from what it is.

## The finding

``avatars.render`` opens by saying "2-D, 3-D, VR and AR surfaces all read
this one shape", and the shape is a URL. The import shelf has offered Ready
Player Me since it was written — *"use Share/Export to get the portrait image
**or the .glb link**"* — so an owner could already hand this platform a 3-D
model, and every surface downstream would put it in an ``<img>``.

    asked     can a profile carry more than a still picture
    mattered  can a surface tell what it was handed

Nothing carried the answer. A renderer had a URL and a guess.

## What this module is

The presentation layer: the **kind** of thing an avatar asset is, and the
**presence** a conversation is currently in. Neither belongs to the profile —
a profile is identity, memory, personality, relationship and permission, and
what it looks like on one screen is a fact about the screen. The avatar is
the presentation of the profile; it is not the profile.

Kinds are read from the asset, not from what the sender said it is — the same
rule ``media._sniff`` follows for uploads, and for the same reason: a name is
a claim and an extension is a hint. An asset this deployment cannot classify
is ``image``, because that is what every surface already does with an unknown
URL and a guess that changes nothing is the safe one.

## What it refuses to pretend

``supported`` is per-kind and per-surface, and it is honest in the direction
that costs us. A console that cannot run a 3-D model says so and shows the
still it does have; it does not silently render the poster and let the owner
believe their model is on screen. That is the same call
``ProfilePageView`` makes about a stranger's markup — name the gap rather
than paper over it.
"""

from __future__ import annotations

from . import db

#: What an avatar asset can be. Ordered by how much a surface must be able to
#: do to show it, which is also the order a fallback walks back down.
KINDS = ("image", "video", "model", "scene")

#: Extensions that decide a kind. A URL with none of these is an image, which
#: is what every surface already assumed.
_EXTS: dict[str, tuple[str, ...]] = {
    "video": (".mp4", ".webm", ".mov", ".m4v"),
    "model": (".glb", ".gltf", ".vrm", ".usdz", ".fbx"),
}

#: Where a conversation is, which is the only thing an avatar's expression,
#: motion and glow should be driven by. Named for what the person can observe
#: rather than for what the code is doing — `thinking` is the pause after they
#: stop talking, `processing` is work that is not a reply (an import being
#: read, a file being distilled).
PRESENCE = ("idle", "listening", "thinking", "speaking",
            "paused", "processing", "error")

#: The presence a surface falls back to. Not `error`: a client that has not
#: yet been taught the states should look calm, not broken.
DEFAULT_PRESENCE = "idle"


def kind_of(asset: str | None) -> str:
    """What kind of thing this asset is, read from the asset itself.

    A query string is stripped first: a signed URL ending
    ``…/figure.glb?sig=…`` is still a model, and reading the tail literally
    would have called it an image.
    """
    if not asset:
        return "image"
    path = asset.split("?", 1)[0].split("#", 1)[0].lower()
    for kind, exts in _EXTS.items():
        if path.endswith(exts):
            return kind
    # A page rather than a file: a provider's live avatar, an AR/VR scene.
    # Only when it is plainly a document route — a bare host is somebody's
    # image CDN more often than it is a scene.
    if path.endswith((".html", ".htm")) or "/scene/" in path:
        return "scene"
    return "image"


def set_kind(profile_id: str, kind: str | None) -> None:
    """Record the owner's own answer, for an asset that carries no clue.

    A provider that serves a model from ``/v1/avatar/8831`` with the type in
    a header is not something this deployment can read from the string, and
    guessing wrong there is worse than asking. Absent an override, `kind_of`
    decides — so this is a correction, never the primary route.
    """
    conn = db.connect()
    if kind is None:
        conn.execute("DELETE FROM avatar_presentation WHERE profile_id=?",
                     (profile_id,))
        conn.commit()
        return
    if kind not in KINDS:
        raise ValueError("presentation kind is one of " + ", ".join(KINDS))
    conn.execute(
        "INSERT INTO avatar_presentation (profile_id, kind, created_at)"
        " VALUES (?,?,?) ON CONFLICT(profile_id) DO UPDATE SET kind=excluded.kind",
        (profile_id, kind, db.utcnow()))
    conn.commit()


def declared_kind(profile_id: str) -> str | None:
    row = db.connect().execute(
        "SELECT kind FROM avatar_presentation WHERE profile_id=?",
        (profile_id,)).fetchone()
    return row["kind"] if row else None


def presentation(profile_id: str, asset: str | None,
                 torso: str | None = None) -> dict:
    """What a renderer needs, beside the asset it was already given.

    Rides inside ``avatars.render`` rather than on a route of its own. Every
    surface already reads that one shape — that is the whole point of
    attaching the badge there — and a second door would mean a client could
    have the picture without the fact of what it is, which is the state this
    module exists to end.
    """
    declared = declared_kind(profile_id)
    kind = declared or kind_of(asset)
    return {
        "kind": kind,
        # True when the owner said so rather than the string saying so, which
        # a surface may want to weigh differently before trusting it.
        "declared": declared is not None,
        # What to show when this surface cannot render `kind`. The torso is
        # the better still — it is the whole figure — and the portrait stands
        # in when there is no torso.
        "still": torso or (asset if kind == "image" else None),
        # The states this profile's avatar can be asked to be in. Sent so a
        # client renders the set the backend knows about rather than a set it
        # was compiled with, which is how one shell ends up the odd one out.
        "presence_states": list(PRESENCE),
        "presence_default": DEFAULT_PRESENCE,
    }
