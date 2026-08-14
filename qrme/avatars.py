"""Portraits for synthetic profiles — art direction, rights, and the mark.

A profile without a face is a row in a table. This module holds the visual
identity of one: a **brief** (what the portrait shows, written to be handed
straight to an illustrator or an image model), the **asset** once it exists,
and the **badge** that must ride on every render of it.

Three rules the rest of the module exists to enforce:

* **Starter faces are nobody.** Every portrait in ``BRIEFS`` describes an
  invented person. That is what keeps ``seed.py``'s promise — starters are
  ``fictional`` kind, no real-person rights involved — true of the picture
  as well as the persona. A real likeness on a profile is a different
  animal: it needs ``kind="other_person"`` and a consent record, which
  ``routers/profiles.py`` already enforces at 422.
* **No borrowed costumes.** Briefs describe generic wardrobe, never a
  trademarked character, uniform, or logo. A likeness release from the
  person photographed grants their face; it grants nothing about a costume
  someone else owns.
* **The badge is not optional, and it is in the pixels.** A portrait is the
  most-looked-at render QRME produces, so :func:`render` refuses to hand one
  back without the profile's AI watermark attached — and every shipped
  portrait *also* carries the mark burned in. The composited badge covers the
  surfaces QRME controls; the burned one covers the rest. A file served at
  ``/portraits/{handle}.webp`` can be hotlinked, embedded, scraped, saved or
  screenshotted, and in none of those cases does a composited badge survive.
  Burned by ``tools/mark_portraits.py``, pinned by a checksum manifest so an
  unmarked replacement cannot arrive quietly.

The briefs lean funny on purpose. A stock headshot says "corporate mascot";
a financial planner wearing far too much gold says "this is a character, and
everyone here knows it" — which is the honest note for a synthetic profile
to open on.
"""

from __future__ import annotations

from . import db, presentation as presentation_mod, watermark

# Shared direction, so 34 portraits look like one collection rather than 34
# stock photos. Kept separate from the per-profile line below because it is
# the part a generator should receive verbatim every time.
#
# This text describes the collection that actually shipped, not an earlier
# intention. It used to specify warm-lit photographic portraits; what was
# rendered is a monochrome cyan treatment, and it reads as one deliberate
# collection in a way the original brief would not have. Leaving the old
# wording in place would have meant the next portrait generated from these
# briefs could not sit beside the ones already here.
STYLE = ("Waist-up character portrait rendered as a luminous cyan hologram — "
         "fine engraved linework, edge-lit, glowing against a near-black "
         "background, as if projected. Monochrome blue throughout. "
         "Photographic proportions but heightened, and the subject knows they "
         "are posing. No text, no logos, no trademarked costume or uniform.")

# The rated portrait is deliberately outside the cyan system: warm practical
# light, full colour. It is the one profile that never appears in a grid with
# the others — every discovery surface age-walls it — so matching them would
# buy nothing, and looking different is a second signal that it is different.
RATED_STYLE = ("Warm practical light, full colour, old-Hollywood glamour. "
               "Outside the collection's cyan treatment on purpose.")

# Where the shipped portraits live, and the path they are served at. Resolved
# against this file rather than the working directory, because after
# `pip install` the package lives in site-packages and a relative path finds
# nothing — the same trap that made the studio 404 inside the container.
ASSET_ROUTE = "/portraits"

# Photographs, which are a different kind of thing from portraits and live
# apart from them on purpose.
#
# Everything under ``/portraits`` is a synthetic face with the AI mark burned
# into its pixels, checksummed by ``tools/mark_portraits.py``. A real
# photograph of a real person is not that, and must not be burned with that
# mark: the mark says *AI-generated synthetic media*, and stamping it on an
# authentic photograph is a false statement in the opposite direction from the
# one the mark exists to prevent.
#
# Keeping them in one directory would also mean an unburned file sitting in a
# tree whose manifest check walks every file in it — so the check would either
# fail or have to be loosened, and loosening the thing that guarantees the
# marks are intact is not a trade worth making for a folder layout.
PHOTO_ROUTE = "/photos"

# What an anonymous profile shows before it puts anything in the bubble: an
# empty picture frame with a plus. A third kind of asset again — not a portrait,
# since nothing generated it and burning the AI mark into it would be a false
# statement about a drawing of nobody; not a photograph either, since it depicts
# no one. Interface furniture, so it lives apart from both and `asset_is_marked`
# reports False for it like any other unburned file.
#
# **One picture, for the owner and for visitors alike.** There was briefly a
# plain silhouette for strangers and this for the owner, on the reasoning that a
# photo-and-plus reads as a control and a control offered to somebody who cannot
# press it reports the empty bubble as a gap. The identifying work is done by
# the name — `Anonymous 41338025` — so the picture is a placeholder rather than
# a claim about anybody, and an empty frame is the most honest drawing of an
# empty frame. Two defaults meant two things that could disagree about the same
# profile, which is the shape of bug this codebase keeps finding.
FIGURE_ROUTE = "/figures"
ADD_PHOTO = f"{FIGURE_ROUTE}/add-photo.svg"

# The old name, still pointing at the one default. Kept because `silhouette` is
# what the *field* on a render is called, and a constant that disagreed with it
# would be worse than a slightly dated word.
SILHOUETTE = ADD_PHOTO


def portraits_dir():
    from pathlib import Path
    return Path(__file__).resolve().parent / "assets" / "portraits"


def figures_dir():
    from pathlib import Path
    return Path(__file__).resolve().parent / "assets" / "figures"


def photos_dir():
    from pathlib import Path
    return Path(__file__).resolve().parent / "assets" / "photos"


def asset_path(handle: str) -> str | None:
    """The served path for a starter's portrait, or None if it has no file."""
    return (f"{ASSET_ROUTE}/{handle}.webp"
            if (portraits_dir() / f"{handle}.webp").is_file() else None)


def photo_path(handle: str) -> str | None:
    """The served path for a real photograph, or None if there is no file."""
    return (f"{PHOTO_ROUTE}/{handle}.webp"
            if (photos_dir() / f"{handle}.webp").is_file() else None)


def shown(asset: str | None) -> str:
    """The picture a *row* shows — the asset, or the empty frame.

    `render()` is the full answer and costs several queries; a list of forty
    friends does not want forty of those. This is the same terminal decision
    without them, so a row-shaped payload and a rendered profile agree about
    what a face-less profile looks like.

        asked     does this row have a picture
        mattered  does every surface draw the same thing when it does not

    Before this, four list builders handed the raw column straight out and
    each client invented its own fallback — initials in two places, an
    abstract orb in a third. Anonymity is *not* handled here on purpose: that
    substitution needs the profile's own chosen emblem and belongs in
    `render`, which is where it already is.
    """
    return asset or ADD_PHOTO


def asset_is_marked(asset: str | None) -> bool:
    """Whether the image itself carries the AI mark, as opposed to needing a
    surface to composite one.

    True only for the burned collection. An owner-attached asset is somebody
    else's file and nothing here can vouch for its pixels; a photograph under
    ``/photos`` is deliberately unburned because it is not AI-generated. Both
    report False, so the surfaces keep drawing their own badge — which is the
    safe direction to be wrong in, and in the photograph's case is the correct
    answer rather than a fallback: the *profile* is synthetic and must say so,
    while the *picture* is authentic and must not claim otherwise.
    """
    return bool(asset) and asset.startswith(f"{ASSET_ROUTE}/")

# handle -> the portrait, one line, played straight-faced.
BRIEFS: dict[str, str] = {
    "dr_amara_osei":
        "A physician in her fifties in a white coat, stethoscope slung on "
        "like a scarf rather than worn, holding a comically oversized model "
        "of a human heart under one arm the way you'd hold a football.",
    "marcus_bell":
        "A retired financial planner in a three-piece suit loud enough to "
        "count as a personality, gold chains layered to the sternum, gold "
        "grills, pinky rings — and a pocket calculator held up like a "
        "trophy, because the money jokes are the only flashy thing about "
        "his actual advice.",
    "priya_raman":
        "A software architect at a whiteboard covered in a diagram that has "
        "clearly escaped its own scope, holding a marker in each hand and "
        "one behind each ear.",
    "elena_vasquez":
        "A teacher mid-sentence with chalk dust on both sleeves, holding a "
        "stack of books tall enough that she is peering around it.",
    "jonathan_ashe":
        "A lawyer in shirtsleeves and loosened tie, one hand resting on a "
        "law library's worth of bound volumes, the other holding a single "
        "sticky note — the part that actually mattered.",
    "sam_whitfield":
        "A farmer leaning on a fence in a seed-company cap, one boot up on "
        "the rail, holding a single ear of corn like a sommelier presenting "
        "a vintage.",
    "ingrid_halvorsen":
        "A manufacturing engineer in a hi-vis vest and safety glasses "
        "pushed up on her forehead, holding a machined part up to the light "
        "with the reverence of a jeweller.",
    "diego_fuentes":
        "A site foreman in a hard hat with a tape measure clipped at the "
        "hip, arms crossed, standing beside a level that is very slightly "
        "off — and he has noticed.",
    "naomi_clarke":
        "A real-estate agent in a sharp blazer holding an absurd ring of "
        "keys with both hands, smiling the specific smile of someone about "
        "to say the word 'cosy'.",
    "tomas_rivera":
        "An energy engineer in a field jacket with a hard hat under one "
        "arm, a small wind-turbine model spinning on his palm.",
    "odessa_grant":
        "A logistics director in a bomber jacket holding a clipboard, "
        "surrounded by a floating constellation of tiny shipping "
        "containers, entirely unbothered by them.",
    "ken_nakamura":
        "A retail operator in a crisp apron over a button-down, holding a "
        "barcode scanner like a duelling pistol at rest.",
    "lucia_moretti":
        "A hotelier in an immaculate suit holding a brass bell with one "
        "finger poised over it, radiating the calm of someone who has "
        "already fixed the problem you're about to describe.",
    "ray_coleman":
        "A broadcast veteran in headphones around the neck, leaning into a "
        "vintage ribbon microphone, one hand raised in the universal 'we're "
        "live' gesture.",
    "wren_okafor":
        "A painter in a paint-wrecked smock holding a brush in the teeth "
        "and one in each hand, a smear of cadmium yellow across one cheek "
        "that clearly happened hours ago and went unremarked.",
    "coach_dana_reyes":
        "A strength coach in a track jacket with a whistle and a stopwatch, "
        "holding a clipboard and giving the camera a look that says one "
        "more set.",
    "chef_henri_laurent":
        "A chef in whites with a towel over the shoulder, tasting spoon "
        "raised, expression suspended between delight and profound "
        "disappointment.",
    "dr_sana_iqbal":
        "An environmental scientist in field gear holding a soil core "
        "sample in one hand and a seedling in the other, weighing them "
        "against each other like scales.",
    "pete_kowalski":
        "A career civil servant in a slightly dated suit holding a single "
        "form, radiating the serenity of a man who knows which office you "
        "actually need.",
    "grace_mwangi":
        "A nonprofit director in a bright print blazer holding a "
        "hand-lettered donation thermometer that has been amended upward "
        "several times.",
    "dr_felix_baum":
        "A research scientist in a lab coat with hair defeated by static, "
        "holding a flask of something faintly luminous at arm's length, "
        "delighted.",
    "aisha_diallo":
        "A telecom network engineer in a utility vest holding a coil of "
        "fibre optic cable that glows softly at the cut end, like a lamp "
        "she happens to be carrying.",
    "harold_jenkins":
        "An insurance adjuster in a cardigan holding an umbrella indoors, "
        "open, because you never know — expression entirely sincere.",
    "rosa_delgado":
        "A master mechanic in coveralls with a grease stripe across the "
        "forehead, holding a torque wrench across both palms like a "
        "presented sword.",
    "cmdr_ellen_park":
        "A retired flight commander in a flight jacket with the patches "
        "removed, holding a helmet under one arm, looking slightly up and "
        "past the camera out of pure habit.",
    "mimi_beaumont":
        "A beauty editor in immaculate everything, holding a makeup brush "
        "like a conductor's baton mid-downbeat.",
    "jack_osei_turner":
        "A brand strategist in a perfectly plain black t-shirt in front of "
        "a wall of sticky notes, holding one that just says 'WHY?'.",
    "nadia_petrova":
        "A security researcher in a hoodie over a collared shirt, lit by a "
        "screen, holding a hardware key on a lanyard up between two "
        "fingers like the only thing she trusts in the room.",
    "bev_lindqvist":
        "An HR director in a warm cardigan holding a mug that says nothing "
        "at all, wearing the expression of someone who has heard it and is "
        "not going to react to it.",
    "otis_marsh":
        "A session musician on a stool with a battered acoustic guitar, "
        "capo on the wrong fret, entirely unbothered.",
    "dr_lena_whitcomb":
        "A clinical psychologist in a soft cardigan in an armchair, hands "
        "loosely folded, the room deliberately unremarkable and calm.",
    "dr_marcus_adeyemi":
        "A psychiatrist in a quiet suit at a desk, reading glasses in hand, "
        "warm and unhurried, no props that suggest emergency.",
    "dr_priya_nair":
        "A counsellor in a comfortable chair beside a window, a box of "
        "tissues on the table placed within reach without comment.",
    # Rated tier. The brief stays suggestive at most: the profile is age-
    # walled at every surface, but this file ships in a public repository, and
    # "tasteful in the source, gated in the product" is the right split.
    "vivienne_sable":
        "A cabaret headliner backstage in a feathered robe over stage "
        "costume, seated at a bulb-lit mirror with a cigarette holder held "
        "unlit, one eyebrow raised at the camera. Old-Hollywood glamour, "
        "shoulders and above, nothing explicit.",
}

# The mental-health trio is played straight on purpose — a joke portrait on
# the profile someone reaches in a bad hour is a joke at their expense.
SOMBRE = {"dr_lena_whitcomb", "dr_marcus_adeyemi", "dr_priya_nair"}


def brief(handle: str) -> dict | None:
    """The generation-ready brief for a starter handle: shared style plus the
    profile's own line. ``None`` for a handle with no brief."""
    line = BRIEFS.get(handle)
    if line is None:
        return None
    style = RATED_STYLE if handle == "vivienne_sable" else STYLE
    return {
        "handle": handle,
        "portrait": line,
        "style": style,
        "prompt": f"{line} {style}",
        "tone": "sombre" if handle in SOMBRE else "humorous",
        "asset": asset_path(handle),
        # Stated in the brief itself so it survives being copied out of here
        # and pasted somewhere else, which is what briefs are for.
        "constraints": [
            "The subject is an invented person — not a likeness of anyone real.",
            "No trademarked character, costume, uniform, or logo.",
            "No text rendered in the image; the AI badge is composited by the"
            " client from GET /profiles/{id}/avatar.",
        ],
    }


def catalog() -> list[dict]:
    """Every starter brief, for generating the collection in one pass."""
    return [brief(handle) for handle in BRIEFS]


#: Where an avatar somebody already owns can come from. These are import
#: sources, not integrations: the person exports their avatar on the
#: provider's own surface (every one of these ships an export or share
#: image), then hands the file or link to QRME. Nothing here calls a
#: provider's API, holds a provider credential, or claims a partnership —
#: the honest verb is *import*, and the provider's own license keeps
#: governing what the person may do with their avatar.
MARKET: tuple[dict, ...] = (
    {"key": "ready_player_me", "name": "Ready Player Me",
     "how": "Open your avatar at readyplayer.me, use Share/Export to get the "
            "portrait image or the .glb link, and paste it here."},
    {"key": "bitmoji", "name": "Bitmoji (Snap)",
     "how": "In the Bitmoji or Snapchat app, share a sticker of your avatar "
            "to save it as an image, then upload or paste it here."},
    {"key": "meta_avatar", "name": "Meta Avatar",
     "how": "In Instagram/Facebook settings → Avatar, share your avatar as "
            "a sticker image, then upload or paste it here."},
    {"key": "apple_memoji", "name": "Apple Memoji",
     "how": "In Messages, send yourself a Memoji sticker, save it as an "
            "image, then upload or paste it here."},
    {"key": "xbox_avatar", "name": "Xbox Avatar",
     "how": "In the Xbox Avatar Editor, take an avatar photo, save it, then "
            "upload or paste it here."},
    {"key": "zepeto", "name": "ZEPETO",
     "how": "In ZEPETO, save a portrait shot of your character, then upload "
            "or paste it here."},
    {"key": "nintendo_mii", "name": "Nintendo Mii",
     "how": "On Switch, pose your Mii in the editor and take a screenshot, "
            "then upload or paste it here."},
    {"key": "other", "name": "Somewhere else",
     "how": "Any avatar you have the right to use: upload the image or "
            "paste a direct link."},
)

IMPORT_SOURCES = {m["key"] for m in MARKET} | {"photos", "capture"}


def import_avatar(profile_id: str, *, source: str, asset: str,
                  extra: list[str] | None = None, torso: str | None = None,
                  pdi=None) -> dict:
    """Attach an avatar that arrived from outside the starter collection.

    ``asset`` is a media reference the existing upload door minted, or a
    direct URL. The import is written onto the profile's own record as a
    source item — which provider or path it came from, when, and any extra
    frames (the selfie capture posts every angle it took) — so the face's
    provenance survives next to the face. The render pipeline is unchanged:
    the AI badge and the likeness record ride on this avatar exactly as they
    do on a starter portrait.
    """
    if source not in IMPORT_SOURCES:
        raise ValueError(
            "unknown avatar source — GET /avatars/market lists the import "
            "sources this deployment recognises")
    conn = db.connect()
    item_id = db.new_id("src")
    provenance = {"avatar_import": source, "asset": asset,
                  "extra_frames": extra or [], "torso": torso}
    import json as _json
    content, pdi_key = _json.dumps(provenance), None
    if pdi is not None:
        pdi_key = f"qrme/{profile_id}/sources/{item_id}"
        pdi.put(pdi_key, content)
        content = None
    conn.execute(
        "INSERT INTO source_items (id, profile_id, kind, title, content,"
        " pdi_key, created_at) VALUES (?,?,'photo',?,?,?,?)",
        (item_id, profile_id, f"avatar import — {source}", content, pdi_key,
         db.utcnow()),
    )
    conn.commit()
    if torso:
        set_torso(profile_id, torso)
    return set_avatar(profile_id, asset)


def set_torso(profile_id: str, asset: str) -> None:
    """Attach the upper-torso form — the figure that stands in a live feed
    or an AR scene at 1:1 scale, where the circular bubble is only the form
    of a profile that has no avatar yet."""
    conn = db.connect()
    conn.execute(
        "INSERT INTO avatar_torsos (profile_id, asset, created_at)"
        " VALUES (?,?,?) ON CONFLICT(profile_id)"
        " DO UPDATE SET asset=excluded.asset, created_at=excluded.created_at",
        (profile_id, asset, db.utcnow()))
    conn.commit()


def torso_of(profile_id: str) -> str | None:
    row = db.connect().execute(
        "SELECT asset FROM avatar_torsos WHERE profile_id=?",
        (profile_id,)).fetchone()
    return row["asset"] if row else None


def set_avatar(profile_id: str, asset: str) -> dict:
    """Attach a rendered portrait to a profile."""
    conn = db.connect()
    conn.execute("UPDATE profiles SET avatar=? WHERE id=?", (asset, profile_id))
    conn.commit()
    return render(profile_id)


MOTION_STYLES = ("still", "breathe", "lively")


def set_motion(profile_id: str, style: str) -> None:
    """The user-defined half of the moving image: how the portrait carries
    itself. The rest of the motion block is derived, not stored."""
    if style not in MOTION_STYLES:
        raise ValueError("motion style must be one of "
                         + ", ".join(MOTION_STYLES))
    conn = db.connect()
    conn.execute(
        "INSERT INTO avatar_motion (profile_id, style, updated_at)"
        " VALUES (?,?,?) ON CONFLICT (profile_id) DO UPDATE SET"
        " style=excluded.style, updated_at=excluded.updated_at",
        (profile_id, style, db.utcnow()))
    conn.commit()


def motion_of(profile_id: str) -> dict:
    """The moving image (claims 3/13): animation parameters for the portrait,
    derived live from the interaction history.

    ``energy`` and ``warmth`` are the profile's aggregate disposition — the
    means of its latent persona embeddings across every relationship — so the
    picture literally "dynamically update[s] based on interaction history"
    (clause 3). ``tempo_ms`` is the idle-breath period the client animates
    at; speaking and listening scale from it. A "still" style pins everything
    flat without hiding the history that would otherwise move it.
    """
    import json as _json
    conn = db.connect()
    row = conn.execute("SELECT style FROM avatar_motion WHERE profile_id=?",
                       (profile_id,)).fetchone()
    style = row["style"] if row else "breathe"
    vectors = conn.execute(
        "SELECT vector FROM persona_embeddings WHERE profile_id=?",
        (profile_id,)).fetchall()
    energy = warmth = None
    if vectors:
        dims = [_json.loads(v["vector"]) for v in vectors]
        energy = round(sum(d.get("engagement", 0.5) for d in dims)
                       / len(dims), 3)
        warmth = round(sum(d.get("warmth", 0.2) for d in dims)
                       / len(dims), 3)
    energy = 0.5 if energy is None else energy
    warmth = 0.2 if warmth is None else warmth
    # Faster breath the livelier the style and the higher the engagement;
    # never below one second, so the face breathes rather than flickers.
    base = {"still": 0, "breathe": 5200, "lively": 3400}[style]
    tempo = 0 if style == "still" else max(1000, int(base * (1.2 - energy)))
    return {
        "style": style,
        "energy": energy,
        "warmth": warmth,
        "tempo_ms": tempo,
        "states": {
            "idle": "still" if style == "still" else "breathe",
            "speaking": "still" if style == "still" else "mouth-and-hands",
            "listening": "still" if style == "still" else "nod",
        },
        "updated_with": len(vectors),
    }


def render(profile_id: str) -> dict:
    """A profile's portrait *as it must be displayed*.

    The badge is attached here rather than left to each surface to decide,
    because "the client forgot" is how an unmarked synthetic face reaches a
    viewer. 2-D, 3-D, VR and AR surfaces all read this one shape, so the
    disclosure travels with the asset into every one of them.
    """
    row = db.connect().execute(
        "SELECT avatar, kind, anonymous, consent_basis, consent_attestor"
        " FROM profiles WHERE id=?", (profile_id,)).fetchone()
    if row is None:
        return {}
    asset = row["avatar"] or None

    # An anonymous profile gets the stand-in picture, and gets it *here*.
    #
    # Two things were leaking past the flag. A profile that had set a portrait
    # of its own face went on serving that face — a picture is the strongest
    # identifier on a page and the flag never touched it. And a profile with no
    # portrait fell back to initials drawn from the display name, so hiding the
    # name produced a monogram of it.
    #
    # Substituted in `render()` rather than at each surface for the same reason
    # the AI badge is attached here: 2-D, 3-D, VR, AR, the beacon page and every
    # embed read this one shape, and "the client forgot" is how a face reaches a
    # viewer it should not have reached. A surface cannot opt out of this by
    # not knowing about it.
    anonymous = bool(row["anonymous"])
    if anonymous:
        # The plain figure, or the field emblem this profile chose. Still a
        # closed set drawn by us either way — never their own picture, which is
        # the thing the flag exists to withhold.
        from . import identity
        asset = identity.emblem_asset(profile_id)
    elif not asset:
        # And a profile that simply has no portrait yet gets the same empty
        # frame, decided here rather than left to each surface.
        #
        # `emblem_asset` already ends at this frame when an anonymous profile
        # has chosen nothing, so the terminal answer existed — it was reachable
        # only by turning anonymity on. Everyone else fell through to whatever
        # the surface invented, which was initials in two places and a blue orb
        # in a third.
        #
        # The empty frame is the honest drawing of an empty frame, and it reads
        # as something to fill rather than as a thing somebody chose. The name
        # beside it does the identifying, which is the argument the anonymous
        # placeholder was settled on.
        asset = ADD_PHOTO

    return {
        "profile_id": profile_id,
        "asset": asset,
        # Says the picture is not this profile's own, so a surface renders it
        # as a figure rather than captioning it as somebody's face.
        "silhouette": anonymous,
        # Whether the disclosure is already in the image itself.
        #
        # QRME's own surfaces composite their badge either way, because theirs
        # carries the profile's *designed* label and is real text rather than
        # pixels. This field is for everyone else — a VR nameplate, an AR
        # overlay, an embed, a marketplace card — to know whether compositing
        # is mandatory or merely additive. False is the safe answer and is what
        # an unknown asset gets.
        "asset_marked": asset_is_marked(asset),
        # The upper-torso form, for surfaces that stand the avatar in a
        # scene at 1:1 — a live feed, AR, the vastscape. Withheld for an
        # anonymous profile for the same reason the face is: a torso is a
        # picture of somebody too.
        "torso": None if anonymous else torso_of(profile_id),
        "watermark": watermark.design(profile_id),
        "likeness": likeness(profile_id),
        # The moving image: how the portrait moves, derived from the
        # interaction history. It rides the same response as the badge and
        # the likeness record, so nothing can animate the face without
        # having been handed the disclosure alongside it.
        "motion": motion_of(profile_id),
        # What kind of thing the asset *is* — a still, a loop, a 3-D model, a
        # scene — and the presence states a conversation can put it in.
        #
        # This docstring has claimed since it was written that "2-D, 3-D, VR
        # and AR surfaces all read this one shape", and the shape was a URL.
        # The import shelf has offered Ready Player Me's `.glb` link the whole
        # time, so an owner could already hand this platform a model and every
        # surface downstream would put it in an `<img>`.
        #
        #     asked     can a profile carry more than a still picture
        #     mattered  can a surface tell what it was handed
        #
        # Attached here for the same reason the badge is: a client cannot opt
        # out of it by not knowing about it, and a second route would mean a
        # surface could hold the picture without the fact of what it is.
        "presentation": presentation_mod.presentation(
            profile_id, asset, torso=None if anonymous
                                     else torso_of(profile_id)),
        # A portrait with no asset yet is still an answer, and now it is *one*
        # answer. `asset` carries the empty frame (see the substitution above),
        # and this flag says the picture is not their own face — so a surface
        # can draw it as the invitation it is rather than captioning it as
        # somebody's portrait.
        #
        # It used to mean "draw whatever you like", and three surfaces liked
        # three different things: initials on Home and the Top 8, a blue orb on
        # the talk surface, the empty frame for an anonymous profile. Same
        # profile, three faces, and the one on the conversation screen made
        # every face-less person look identical to every other.
        #
        #     asked     does a profile with no face have something to show
        #     mattered  does it show the same thing everywhere
        #
        # This module already argued the point when the anonymous placeholder
        # was chosen — *two defaults meant two things that could disagree
        # about the same profile, which is the shape of bug this codebase keeps
        # finding* — and then there were three.
        "placeholder": not anonymous and not row["avatar"],
    }


def likeness(profile_id: str) -> dict:
    """Whose face this is, in rights terms.

    A portrait of an invented person carries no likeness rights. A portrait
    of a real person carries a grant that can be withdrawn, so the record of
    it belongs next to the picture rather than in somebody's inbox.
    """
    row = db.connect().execute(
        "SELECT kind, consent_basis, consent_attestor FROM profiles WHERE id=?",
        (profile_id,)).fetchone()
    if row is None or row["kind"] == "fictional":
        return {"real_person": False,
                "note": "invented likeness — no rights holder"}
    return {
        "real_person": True,
        "basis": row["consent_basis"],
        "attestor": row["consent_attestor"],
        "revocable": True,
        "note": "depicts a real person under a recorded grant; withdrawing"
                " the grant retires the portrait with the profile",
    }
