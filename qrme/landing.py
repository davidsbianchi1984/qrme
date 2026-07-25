"""The page a stranger lands on after scanning a beacon.

A beacon is a profile left somewhere physical — a sticker on a wall, a card
on a table. Until now its QR pointed at ``/summon?ref=…``, which answers
JSON: a phone's camera app would open that and show the person a wall of
braces. This is the page that should have been there.

The constraints are unusual enough to be worth stating, because they are why
this is hand-written HTML rather than a route into the studio:

* **It opens inside a camera app's in-app browser**, on cellular, from a
  cold start. So it is one self-contained document — inline CSS, no scripts
  that matter, no font or image fetches. The portrait is the only network
  request after the HTML itself.
* **The viewer is a stranger.** No token, no session, no idea what QRME is.
  They pointed a phone at a sticker. The page has about one second to be
  legible and it must never look like a login wall.
* **They are the exact person the AI disclosure exists for.** Someone in
  the studio knows they are looking at a synthetic profile. Someone who
  scanned a sticker in a bathroom does not, so the mark is rendered on the
  portrait itself rather than in a corner of the chrome.

The reveal — the portrait fading up as the page loads — is a CSS animation.
It is not augmented reality and this module does not pretend otherwise: a
stock camera app scanning a QR can only open a URL. Anchoring a portrait to
the sticker in 3D needs WebXR or the native apps; see docs/beacons.md.
"""

from __future__ import annotations

import html

from . import avatars, db

# Night indigo, matching the studio and the printed QR's dark ink.
_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0d0a20;color:#f4f1ff;min-height:100dvh;display:flex;
 align-items:center;justify-content:center;padding:24px;
 font:16px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
 -webkit-font-smoothing:antialiased}
.card{width:100%;max-width:420px;text-align:center}
.frame{position:relative;width:100%;aspect-ratio:1;border-radius:24px;
 overflow:hidden;background:#181233;box-shadow:0 24px 60px rgba(0,0,0,.55);
 animation:rise .7s cubic-bezier(.2,.8,.2,1) both}
.frame img{width:100%;height:100%;object-fit:cover;display:block}
.initials{width:100%;height:100%;display:flex;align-items:center;
 justify-content:center;font-size:84px;font-weight:700;color:#7c5cff;
 letter-spacing:2px}
/* The AI mark rides on the portrait, not the chrome — a stranger who
   screenshots this still carries the disclosure with the image. */
.mark{position:absolute;left:12px;bottom:12px;padding:7px 12px;
 border-radius:999px;background:rgba(13,10,32,.82);backdrop-filter:blur(8px);
 font-size:13px;font-weight:700;letter-spacing:.3px}
h1{font-size:26px;margin:20px 0 4px;animation:rise .7s .1s cubic-bezier(.2,.8,.2,1) both}
.sub{color:#a79fd0;font-size:14px;animation:rise .7s .16s cubic-bezier(.2,.8,.2,1) both}
.blurb{color:#c9c3e8;font-size:15px;margin-top:14px;
 animation:rise .7s .22s cubic-bezier(.2,.8,.2,1) both}
.cta{display:block;margin-top:22px;padding:15px;border-radius:14px;
 background:linear-gradient(120deg,#7c5cff,#4d8dff);color:#fff;
 font-weight:700;text-decoration:none;
 animation:rise .7s .28s cubic-bezier(.2,.8,.2,1) both}
.foot{margin-top:18px;color:#6f6899;font-size:12px;line-height:1.6}
.wall{font-size:52px;margin-bottom:8px}
@keyframes rise{from{opacity:0;transform:translateY(14px) scale(.985)}
 to{opacity:1;transform:none}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""


def _page(title: str, body: str) -> str:
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1,'
        'viewport-fit=cover"><meta name="theme-color" content="#0d0a20">'
        f"<title>{html.escape(title)}</title><style>{_CSS}</style></head>"
        f'<body><main class="card">{body}</main></body></html>')


# Honorifics that are not what anyone calls a person. Without this the
# call to action on "Dr. Sana Iqbal" reads "Talk to Dr."
_HONORIFICS = {"dr", "dr.", "mr", "mr.", "ms", "ms.", "mrs", "mrs.",
               "prof", "prof.", "chef", "coach", "cmdr", "cmdr.", "capt",
               "capt.", "rev", "rev.", "sgt", "sgt."}


def first_name(display_name: str) -> str:
    """What to call them on a button. Falls back to the whole name rather
    than to something wrong."""
    for part in display_name.split():
        if part.lower().strip(".,") not in {h.strip(".") for h in _HONORIFICS}:
            return part
    return display_name


def _initials(name: str) -> str:
    parts = [p for p in name.replace(".", " ").split() if p]
    return "".join(p[0] for p in parts[:2]).upper() or "?"


def gone(what: str = "beacon") -> str:
    """A beacon that was picked up, or never existed. Says so plainly — a
    stranger who scanned a stale sticker should not get a stack trace."""
    return _page("Nothing here", f"""
      <div class="wall">◌</div>
      <h1>Nothing here any more</h1>
      <p class="sub">This {html.escape(what)} was picked up, so it no longer
        summons anyone.</p>
      <p class="foot">QRME · synthetic profiles</p>""")


def age_wall() -> str:
    """A rated profile scanned without a verified-adult token — which is what
    every sticker scan is, since a stranger has no token at all."""
    return _page("18+", """
      <div class="wall">⊘</div>
      <h1>18+ only</h1>
      <p class="sub">This profile is age-restricted. Open it in QRME and
        sign in with a verified adult account to continue.</p>
      <p class="foot">QRME · synthetic profiles<br>
        The age check happens here, not at whoever placed this code.</p>""")


def profile_page(profile: dict, base: str, label: str | None = None,
                 room_id: str | None = None) -> str:
    """The reveal: portrait, name, and one way in.

    ``base`` is the public origin, so the call to action works from a phone
    that has never heard of this deployment. ``room_id`` switches the way in
    from a private conversation to the shared room everyone scanning this
    code joins — a class, a workshop, a meeting.
    """
    pid = profile["id"]
    art = avatars.render(pid)
    watermark = art["watermark"]["line"]
    name = ("anonymous persona" if profile["anonymous"]
            else profile["display_name"])

    if art["asset"]:
        portrait = f'<img src="{html.escape(art["asset"])}" alt="" >'
    else:
        # No portrait yet: initials rather than a stock face, which would be
        # a stranger's first impression of a person who does not exist.
        portrait = f'<div class="initials">{html.escape(_initials(name))}</div>'

    blurb = db.connect().execute(
        "SELECT blurb FROM marketplace WHERE profile_id=?", (pid,)).fetchone()
    blurb_html = (f'<p class="blurb">{html.escape(blurb["blurb"])}</p>'
                  if blurb and blurb["blurb"] else "")
    where = (f'<p class="sub">left at {html.escape(label)}</p>'
             if label else "")

    if room_id:
        # Shared mode: everyone who scans this code lands in one conversation
        # together, rather than each in a private thread with the profile.
        cta = (f'<a class="cta" href="{html.escape(base)}/app/#/rooms/'
               f'{html.escape(room_id)}">Join the conversation</a>')
        footnote = ("Everyone who scans this code joins the same room, so "
                    "you may not be the only one here.")
    else:
        cta = (f'<a class="cta" href="{html.escape(base)}/app/#/summon?'
               f'ref={html.escape(pid)}">Talk to '
               f'{html.escape(first_name(name))}</a>')
        footnote = "Someone left this code here on purpose."

    return _page(f"{name} · QRME", f"""
      <div class="frame">{portrait}
        <div class="mark">{html.escape(watermark)}</div></div>
      <h1>{html.escape(name)}</h1>
      {where}
      {blurb_html}
      {cta}
      <p class="foot">{html.escape(art["watermark"]["disclosure"])}.<br>
        {footnote}</p>""")
