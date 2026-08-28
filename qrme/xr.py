"""Where the AR and VR rooms can be stood in — every headset on the market.

The owner's brief, three messages wide: Steam outputs for the VR rooms,
Meta and Apple for the glasses, "and any others that are available in the
market — let's go ahead and cover all the competitors and offer their
tools."

The honest architecture first: these rooms are web pages, and their AR
and VR stages run on WebXR — so the road into them from a headset is the
headset's OWN browser, today, with no listing fee and no gatekeeper in
between. The catalog says that per platform, names the browser, and marks
what is NOT built (native apps, platform sign-ins) as planned rather than
pretending. A row that overstates a platform is the same defect as a
button that dead-ends — qrme/oauth.py's grey-button doctrine, one shelf
up.
"""

from __future__ import annotations

from . import oauth

#: The market, by vendor. `wears` is what the hardware does — vr, ar or
#: both. `browser` is the road that works today, named as the products
#: name themselves (proper nouns travel untranslated); every row has one
#: because the rooms are pages. `signin_road` points at the OAuth door
#: the platform's account arrives through, where oauth.py holds one.
_SHELF = [
    {"platform": "phone", "name": "Any phone or tablet",
     "wears": ["ar", "vr"], "browser": "Safari / Chrome",
     "signin_road": None},
    {"platform": "meta", "name": "Meta Quest",
     "wears": ["vr", "ar"], "browser": "Meta Quest Browser",
     "signin_road": None},
    {"platform": "apple", "name": "Apple Vision Pro",
     "wears": ["vr", "ar"], "browser": "Safari (visionOS)",
     "signin_road": "apple"},
    {"platform": "steam", "name": "Valve SteamVR",
     "wears": ["vr"], "browser": "Chrome + SteamVR",
     "signin_road": None},
    {"platform": "pico", "name": "PICO",
     "wears": ["vr"], "browser": "PICO Browser", "signin_road": None},
    {"platform": "htc", "name": "HTC Vive",
     "wears": ["vr"], "browser": "Vive Browser / SteamVR",
     "signin_road": None},
    {"platform": "android_xr", "name": "Android XR",
     "wears": ["vr", "ar"], "browser": "Chrome",
     "signin_road": "google"},
]

#: Platform account doors that are on the map and not in the wall —
#: Steam's OpenID (which hands back a steamid and no verified email, so
#: linking it is a design step, not a button) and Meta's account door.
#: Named so the shelf says "planned" about exactly these and "none" about
#: vendors whose users sign in with an ordinary account here.
_SIGNIN_PLANNED = {"steam", "meta"}


def shelf() -> dict:
    """The catalog, with sign-in states read from the real doors.

    `signin` is four honest words: `live` (the OAuth door is configured on
    this deployment), `unconfigured` (built in oauth.py, not switched on
    here), `planned` (not built), and `none` (the platform brings no
    account of its own to this product).
    """
    doors = {p["provider"]: p["configured"]
             for p in oauth.providers()["signin_providers"]}
    rows = []
    for spec in _SHELF:
        road = spec["signin_road"]
        if road is not None:
            signin = "live" if doors.get(road) else "unconfigured"
        elif spec["platform"] in _SIGNIN_PLANNED:
            signin = "planned"
        else:
            signin = "none"
        rows.append({"platform": spec["platform"], "name": spec["name"],
                     "wears": spec["wears"], "browser": spec["browser"],
                     "open_now": True, "native_app": "planned",
                     "signin": signin})
    return {"xr_platforms": rows}
