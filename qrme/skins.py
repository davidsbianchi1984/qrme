"""The standing figure a starter wears — presets that ship with the platform.

## The finding

Every starter has a portrait. Thirty-five files under ``/portraits``, one per
handle, cyan hologram, the AI mark burned into the pixels and pinned by a
checksum manifest. What none of them has is a **standing figure** —
``avatar_torsos`` has no row for any starter, and ``torso_of`` returns None
for all thirty-four.

That is the asset the avatar conversation surface wants. ``avatars.py``
calls the torso "the figure that stands in a live feed or AR at 1:1", and a
full-body conversation screen has nothing else to draw, so every starter
falls back to a circular face or an orb.

    asked     does a starter have a face
    mattered  does it have a body to stand up in

The import shelf cannot close this. Bringing a skin from Ready Player Me is
an *owner's* move, and nobody owns Dr. Osei — the starters ship with the
product, so their figures have to ship with it too.

## What this module is

The figure collection, in the shape the portraits already use: a shared
**direction**, a per-starter **pose**, and a path that resolves to None until
the file exists. Briefs first, files later — which is exactly how the
portraits arrived, and it means the day the art lands every starter stands
up without a line of code changing.

A figure brief **composes** the portrait brief rather than restating it.
Two independent descriptions of one person is how the picture on the beacon
page and the figure in the room end up being different people, and this
repository has spent enough rounds on things that agreed until they didn't.
The portrait says who they are and what they are holding; the pose says how
they stand.

## The three rules still hold

Invented people, no borrowed costumes, and the mark is not optional. A
standing figure is a *bigger* render than a portrait, not a lesser one, so
nothing here relaxes them: ``FIGURE_STYLE`` carries the same constraint about
trademarked costume, and ``avatars.asset_is_marked`` reports False for
anything outside the burned collection, which keeps every surface drawing
its own badge until the burn-in tool has been over these too.
"""

from __future__ import annotations

from . import avatars

#: Served path and package directory. `/figures` is already interface
#: furniture — the emblems and the add-photo frame — and mixing a character
#: render into it would put an unburned drawing inside a tree whose manifest
#: check walks every file. Its own route, its own manifest, same as portraits.
SKIN_ROUTE = "/skins"


def skins_dir():
    from pathlib import Path
    return Path(__file__).resolve().parent / "assets" / "skins"


def skin_path(handle: str) -> str | None:
    """The served path for a starter's standing figure, or None if the file
    has not shipped yet.

    None is a real answer rather than a gap: `render` falls back to the
    portrait, and a surface that wanted a body gets a face instead of a
    broken image. Identical to `avatars.asset_path`, deliberately — the two
    collections arrive the same way and should fail the same way.
    """
    return (f"{SKIN_ROUTE}/{handle}.webp"
            if (skins_dir() / f"{handle}.webp").is_file() else None)


#: Shared direction for the standing figures, so thirty-four of them read as
#: one collection rather than thirty-four stock renders — the same job
#: `avatars.STYLE` does for the portraits, and deliberately continuous with
#: it: this is the same person, further back.
FIGURE_STYLE = (
    "Full-length standing figure of the same character, rendered as a "
    "luminous cyan hologram — fine engraved linework, edge-lit, glowing "
    "against a near-black background, as if projected. Monochrome blue "
    "throughout, matching the portrait collection exactly. Whole body in "
    "frame with a little air above the head and below the feet, weight on "
    "one leg, facing the viewer. Photographic proportions but heightened, "
    "and the subject knows they are being looked at. No text, no logos, no "
    "trademarked costume or uniform. Transparent background."
)

#: The rated figure stays outside the cyan system for the same reason its
#: portrait does — it never appears in a grid with the others, so matching
#: them buys nothing and looking different is a second signal.
RATED_FIGURE_STYLE = (
    "Warm practical light, full colour, old-Hollywood glamour, full-length "
    "standing. Outside the collection's cyan treatment on purpose. Fully "
    "and unremarkably dressed — this figure is age-walled for tone, not for "
    "skin, and the render must give a moderator nothing to weigh."
)

#: How each one stands. Short on purpose: the portrait brief already carries
#: the character, the wardrobe and the prop, and repeating them here is how
#: the two drift into describing different people.
POSES: dict[str, str] = {
    "dr_amara_osei": "Standing squarely, heart model tucked under the arm "
                     "like a ball she is not giving back.",
    "marcus_bell": "One hand in a trouser pocket, calculator still raised, "
                   "posture of a man mid-anecdote.",
    "priya_raman": "Half-turned back toward the whiteboard, marker capped, "
                   "as if you interrupted a good part.",
    "elena_vasquez": "Feet planted, arms loose, the stance of somebody used "
                     "to being listened to without raising her voice.",
    "jonathan_ashe": "Upright and still, hands clasped in front, the "
                     "practised neutrality of a man who bills by the hour.",
    "sam_whitfield": "Weight back on the heels, arms folded, faintly amused.",
    "ingrid_halvorsen": "Straight-backed and composed, hands at her sides, "
                        "chin level.",
    "diego_fuentes": "Mid-stride and stopping, as though called from across "
                     "a room.",
    "naomi_clarke": "One hand raised in a small unfinished gesture, caught "
                    "explaining.",
    "tomas_rivera": "Solid stance, sleeves pushed up, hands open at his "
                    "sides.",
    "odessa_grant": "Turned three-quarters with the head coming round to "
                    "the viewer last.",
    "ken_nakamura": "Quiet and vertical, hands behind the back.",
    "lucia_moretti": "Hip cocked, one hand resting on it, entirely at ease.",
    "ray_coleman": "Broad stance, thumbs hooked, taking up his own space.",
    "wren_okafor": "Light on the feet, one shoulder forward, curious.",
    "coach_dana_reyes": "Athletic stance, hands on hips, already waiting "
                        "for you to start.",
    "chef_henri_laurent": "Feet apart, arms crossed, the stillness of "
                          "somebody with a pan going behind him.",
    "dr_sana_iqbal": "Composed and centred, hands folded at the waist.",
    "pete_kowalski": "Leaning very slightly back, tool still in hand.",
    "grace_mwangi": "Tall and open, arms relaxed, welcoming.",
    "dr_felix_baum": "Slight forward lean, as though about to ask a "
                     "follow-up question.",
    "aisha_diallo": "Squared to the viewer, hands loose, unhurried.",
    "harold_jenkins": "Settled on both feet, one hand in a cardigan pocket.",
    "rosa_delgado": "Turned slightly, gesturing small with one hand.",
    "cmdr_ellen_park": "Parade rest, absolutely level.",
    "mimi_beaumont": "One foot crossed in front of the other, poised.",
    "jack_osei_turner": "Loose-limbed and easy, hands in pockets.",
    "nadia_petrova": "Still and exact, arms at her sides, gaze direct.",
    "bev_lindqvist": "Comfortable stance, one arm across the middle holding "
                     "the other elbow.",
    "otis_marsh": "Weight on one leg, head tilted, listening.",
    "dr_lena_whitcomb": "Upright, hands clasped low, the practised calm of "
                        "somebody who delivers hard news well.",
    "dr_marcus_adeyemi": "Squared and steady, one hand holding the other "
                         "wrist in front.",
    "dr_priya_nair": "Balanced and open, arms relaxed, attentive.",
    "vivienne_sable": "Standing tall in a floor-length gown, one hand "
                      "resting on the opposite forearm, entirely covered "
                      "and entirely composed.",
}


def brief(handle: str) -> dict | None:
    """The generation-ready brief for one standing figure.

    Composed rather than stored: the character comes from
    ``avatars.BRIEFS``, so a portrait rewritten tomorrow takes its figure
    with it and the two cannot describe different people.
    """
    portrait = avatars.BRIEFS.get(handle)
    pose = POSES.get(handle)
    if portrait is None or pose is None:
        return None
    style = (RATED_FIGURE_STYLE if handle == "vivienne_sable"
             else FIGURE_STYLE)
    return {
        "handle": handle,
        "style": style,
        "character": portrait,
        "pose": pose,
        # What a generator should receive, in one string, in the order a
        # person would say it: how it is drawn, who it is, how they stand.
        "prompt": f"{style} {portrait} {pose}",
        # None until the file ships. Present so a caller can tell "not drawn
        # yet" from "drawn and here" without a second call.
        "asset": skin_path(handle),
    }


def catalog() -> list[dict]:
    """Every figure brief, in the collection's own order."""
    return [b for b in (brief(h) for h in avatars.BRIEFS) if b is not None]


def missing() -> list[str]:
    """Handles whose figure has not shipped yet.

    Counted rather than assumed: this is the number that says how much of the
    collection can actually stand up, and a surface that wants bodies should
    be able to ask rather than discover it one starter at a time.
    """
    return [h for h in avatars.BRIEFS if skin_path(h) is None]
