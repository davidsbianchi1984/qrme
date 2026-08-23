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

from . import pagehead

import html
import json

from . import avatars, db, identity

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
/* A desk is a real person, so this badge is the opposite of .mark and must
   not be mistaken for it at a glance: green rather than neutral, top-right
   rather than bottom-left, and it states the claim instead of a disclaimer.
   It rides on the frame for the same reason .mark does — a screenshot of an
   unmarked photograph would carry no claim either way. */
.human{position:absolute;right:12px;top:12px;padding:7px 12px;
 border-radius:999px;background:rgba(6,32,20,.86);backdrop-filter:blur(8px);
 color:#7ce8b0;font-size:13px;font-weight:700;letter-spacing:.3px}
.status{margin-top:14px;color:#a79fd0;font-size:14px}
.dot{display:inline-block;width:8px;height:8px;border-radius:50%;
 margin-right:7px;vertical-align:1px}
.dot.here{background:#7ce8b0}
.dot.away{background:#ffcc66}
.dot.shut{background:#6f6899}
.bell{display:block;width:100%;margin-top:18px;padding:15px;border:0;
 border-radius:14px;font:inherit;font-weight:700;color:#0d0a20;
 background:linear-gradient(120deg,#ffd479,#ffb347);cursor:pointer;
 animation:rise .7s .28s cubic-bezier(.2,.8,.2,1) both}
.bell:disabled{opacity:.6;cursor:default}
.vouch{margin-top:16px;padding:12px 14px;border-radius:12px;
 background:#181233;color:#a79fd0;font-size:12.5px;line-height:1.55;
 text-align:left}
.vouch b{color:#c9c3e8}
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


def desk_age_wall() -> str:
    """A rated desk reached by sticker.

    Every sticker scan is tokenless, so this is not an edge case a verified
    adult occasionally hits — it is what *everyone* who scans an 18+ desk's
    printed code sees, and the only way past it is opening the desk in QRME
    while signed in. Says nothing about who staffs it and, above all, nothing
    about where: a performer's whereabouts on an adult listing is a safety
    matter, and a sticker is by definition somewhere physical.
    """
    return _page("18+", """
      <div class="wall">⊘</div>
      <h1>18+ only</h1>
      <p class="sub">This stream is age-restricted. Open it in QRME and sign
        in with a verified adult account to continue.</p>
      <p class="foot">QRME · live desks<br>
        The age check happens here, not at whoever placed this code.</p>""")


# The bell is the reason this page exists, so it has to work from a stranger's
# camera-app browser with no account. A plain form POST would navigate away
# from the desk and land them on JSON, so this is the one script on the page
# that does anything. It degrades honestly: without JS the button is still
# rendered but reports that it needs the app, rather than silently doing
# nothing when tapped.
_BELL_JS = """
(function(){
  var b=document.getElementById('bell'),s=document.getElementById('bs');
  if(!b)return;
  b.addEventListener('click',function(){
    b.disabled=true;s.textContent='Ringing\\u2026';
    fetch(%(endpoint)s,{method:'POST',headers:{'content-type':'application/json'},
      body:'{}'}).then(function(r){return r.json().then(function(j){
        return {ok:r.ok,j:j};});}).then(function(o){
      if(o.ok){b.textContent='Bell rung';
        s.textContent=o.j.note||'They will see it when they get back.';}
      else{b.disabled=false;
        s.textContent=(o.j&&o.j.detail)||'That did not go through.';}
    }).catch(function(){b.disabled=false;
      s.textContent='No connection \\u2014 try again in a moment.';});
  });
})();
"""


def desk_page(card: dict, label: str | None = None) -> str:
    """The reveal for a desk: an empty chair, and a bell you can reach.

    The inverse of :func:`profile_page` in the one respect that matters. That
    page marks the portrait *AI* because the person in it does not exist; this
    one states **Live person — not AI** because they do, and is careful to make
    the two badges look nothing alike. Absence of the AI mark would not be a
    disclosure — an unmarked card could be a synthetic profile whose badge got
    dropped — so the claim is positive, and it carries who vouched for it.
    """
    desk_id = card["desk_id"]
    name = card["display_name"]
    presence = card["presence"]
    view = card["feed"]["url"]

    dot, said = {
        "attended": ("here", "At the desk right now"),
        "away": ("away", "Away from the desk"),
        "closed": ("shut", "Closed — not taking callers"),
    }.get(presence, ("away", "Away from the desk"))
    if presence == "away":
        said = "Away from the desk — ring the bell and they will see it"

    waiting = int(card["bell"]["waiting"] or 0)
    queued = (f" · {waiting} waiting" if waiting else "")

    if card["bell"]["available"]:
        bell = (f'<button class="bell" id="bell">🔔 Ring the bell</button>'
                f'<p class="status" id="bs">A stranger\'s ring is limited to '
                f'one every {desks_anon_cooldown()} seconds, so nobody can '
                f'lean on it.</p>')
        # Relative, not the configured public base: the sticker was scanned
        # from whatever origin actually reached this page, which on a local
        # deployment is a LAN address rather than the public hostname. An
        # absolute URL here would ring a bell on a different machine, or none.
        script = (pagehead.script_open() + _BELL_JS % {
            "endpoint": _js(f"/desks/{desk_id}/bell")} + "</script>")
    else:
        bell = '<p class="status" id="bs">The bell is off while this desk is closed.</p>'
        script = ""

    att = card["attestation"]
    signed = ("a signed attestation" if att["signed"]
              else "recorded, not signed")
    where = (f'<p class="sub">this code is at {html.escape(label)}</p>'
             if label else "")
    trade = html.escape(card["trade"])
    blurb = (f'<p class="blurb">{html.escape(card["blurb"])}</p>'
             if card.get("blurb") else "")
    livenote = ("" if card["feed"]["live"] else
                "<br>This deployment has no camera on this desk, so the "
                "picture is a sample rather than a live view — and is not "
                "claimed to be one.")

    return _page(f"{name} · QRME", f"""
      <div class="frame"><img src="{html.escape(view)}" alt="">
        <div class="human">{html.escape(card["designation"])}</div></div>
      <h1>{html.escape(name)}</h1>
      <p class="sub">{trade}</p>
      {where}
      {blurb}
      <p class="status"><span class="dot {html.escape(dot)}"></span>{html.escape(said)}{queued}</p>
      {bell}
      <div class="vouch"><b>Who says they are real:</b>
        {html.escape(att["attestor"])} — {html.escape(att["basis"])}
        ({signed}).<br>{html.escape(att["note"])}</div>
      <p class="foot">QRME · live desks. No AI watermark on this page, on
        purpose: there is an actual person behind this desk.{livenote}</p>
      {script}""")


def desks_anon_cooldown() -> int:
    from . import desks
    return int(desks.ANON_COOLDOWN_SECONDS)


# The same table `signing_page` keeps, for the same reason: these end a
# `<script>` element or a JavaScript string literal, and written as \uXXXX
# JavaScript reads them back as the original character. In JSON they appear
# only inside string values, so rewriting the serialised text is safe for any
# shape.
_JS_HAZARDS = {
    "<": "\\u003c", ">": "\\u003e", "&": "\\u0026",
    "\u2028": "\\u2028", "\u2029": "\\u2029",
}


def _js_literal(obj) -> str:
    """Any JSON value, safe to drop **inside a `<script>` element**.

    The one primitive `_js` is built on, and the one the string table is built
    on too — because they had drifted apart. `json.dumps` escapes what would
    end a JavaScript *string*; it has nothing to say about `</script`, which
    ends the *element* whatever the JavaScript quoting says, closing the
    page's own nonced script and leaving everything after it to be parsed as
    markup.

    Deliberately **not** `html.escape`. A browser does not decode HTML
    entities inside a script element, so escaping there protects nothing and
    corrupts the value: `Terms & Conditions` reached the reader as
    `Terms &amp; Conditions`, and this is what the string table is built on.

        asked     is the value escaped
        mattered  is it escaped for the place it lands

    The page was safe by accident rather than by the mechanism written for
    it. The `.replace("</", "<\\/")` — the guard against a literal
    `</script` ending the element, which is the hazard named above — sat
    *after* an `html.escape` that had already turned `<` into `&lt;`. It
    never matched anything and never could.
    """
    text = json.dumps(obj, ensure_ascii=False)
    for char, escape in _JS_HAZARDS.items():
        text = text.replace(char, escape)
    return text


def _js(value: str) -> str:
    """A JS string literal safe to drop into an inline script."""
    return _js_literal(value)


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
    name = identity.shown_name(profile)

    # `render()` is terminal about the face: a profile with no portrait gets
    # the empty frame, so there is no second branch here to disagree with the
    # console about what a stranger sees.
    portrait = f'<img src="{html.escape(art["asset"])}" alt="" >'

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
