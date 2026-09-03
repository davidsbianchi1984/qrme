"""Photograph the console — the real one, running, not a drawing of it.

## Why this exists

`docs/screens/` filled up with hand-drawn SVG mockups of every surface,
and the README galleries presented them as what the product looks like.
They were illustrations. The owner's words, on finding a faceless
mannequin in the gallery:

    "those screens you will never see that you have created. They never
     rendered that way. Only actual snapshots of what the application
     looks like."

He is right, and the failure is worse than cosmetic: a drawing captioned
as a product is a claim about the product. Asked to *grab* screens, I
drew them instead — the difference between a photograph and a painting,
presented as if it were the former.

So this harness does the honest thing. It starts the real backend,
serves the real built console, signs in a real seeded account, walks the
real tabs, and photographs what the browser actually shows.

## What it does NOT do

It does not invent. A surface that will not render — because it needs a
device, a camera, a second person in a room — is left alone rather than
mocked up. An empty state photographed honestly is worth more than a
populated one that never existed.
## The build is a step, not a sentence

It builds the console first, and that is not a convenience. The build used
to be a requirement written in prose — *run `npm run build` first* — and the
harness served whatever was already in `app/dist` without ever looking at
how old it was. So a gallery could be re-shot to show a stylesheet fix, and
photograph a bundle from days earlier, and every capture would look exactly
as convincing as one that showed the fix. It happened, in the round that
replaced drawings with photographs precisely *because* a photograph looks
like evidence.

    asked     is the console built
    mattered  is the console built from what is on disk now

A prose requirement is a requirement somebody skips.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PORT = int(os.environ.get("SHOT_PORT", "8099"))
BASE = f"http://localhost:{PORT}"
OUT = REPO / "docs" / "screens"

#: A viewport that shows the console the way its own people meet it: a
#: phone, because that is what the beta is being read on. Doubled so the
#: capture is legible when GitHub scales it into a gallery.
VIEWPORT = {"width": 430, "height": 932}
SCALE = 2


def seed(db_path: str) -> dict:
    """One verified account and one profile, seeded in process.

    Not through the HTTP doors, and that is deliberate rather than
    lazy: signing up sends a code to an address nobody is reading here,
    and a harness that has to defeat its own email verification is a
    harness that will one day photograph a screen the real flow cannot
    reach. The rows are made the way the product makes them and the
    tokens are minted by the product's own issuer.
    """
    os.environ["QRME_DB"] = db_path
    sys.path.insert(0, str(REPO))
    from qrme import accounts, auth, db

    db.reset()
    stamp = str(int(time.time()))
    email = f"shots+{stamp}@example.test"
    accounts.signup(email, "a-long-enough-password", "David Bianchi")
    conn = db.connect()
    conn.execute("UPDATE accounts SET verified_at=? WHERE email=?",
                 (db.utcnow(), email))
    conn.commit()
    account = conn.execute("SELECT id FROM accounts WHERE email=?",
                           (email,)).fetchone()["id"]

    profile_id = db.new_id("prf")
    from qrme import terms
    conn.execute(
        "INSERT INTO profiles (id, owner_id, kind, display_name, persona,"
        " demographics, sources, anonymous, adult_mode, interaction_scope,"
        " moderation_mode, aging_enabled, maturity, cloud_contribution,"
        " terms_version, terms_accepted_at, created_at)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (profile_id, account, "self", "David Bianchi",
         "The owner's own profile, seeded so the console has something "
         "true to draw.", "{}", "[]", 0, 0, "public", "auto", 0,
         "balanced", 0, terms.TERMS_VERSION, db.utcnow(), db.utcnow()))
    conn.commit()
    # The video road, and one render on it.
    #
    # Seeded rather than started, because starting one needs a service and
    # every one of them is behind a key this machine does not have. What is
    # photographed is still a state the product reaches on its own: the
    # road is stored the way `filming.set_road` stores it, the row is the
    # row `auto_render` inserts, and the console draws it by polling the
    # real route. Nothing here is drawn — only reached from a shorter
    # distance than a person reaches it.
    from qrme import filming
    filming.set_road(profile_id, "video", 60)
    conn.execute(
        "INSERT INTO scene_render (id, profile_id, passage, seconds, status,"
        " created_at) VALUES (?,?,?,?,'pending',?)",
        (db.new_id("ren"), profile_id,
         "Usually on the discharging team, and usually it is a gap rather "
         "than a decision.", 8, db.utcnow()))
    conn.commit()

    # The starter collection, seeded the way a deployment seeds it — the
    # thirty-five professionals with their portraits, and the founder's
    # two profiles. The seed's last step installs the standing friends on
    # every profile, this one included, so the circle and the front page
    # are photographed with the pack on them ("let's go ahead and list
    # all of them in the starter pack as friends") and a friend's
    # homepage is a real starter's, not a stand-in made here.
    from qrme import seed as collection
    collection.seed()

    return {"accountId": account,
            "accountToken": auth.issue("account", account),
            "accountEmail": email,
            "profileId": profile_id,
            "ownerToken": auth.issue("owner", profile_id)}


def build_console() -> None:
    """`npm run build`, every run, before anything is photographed.

    Not conditional on a timestamp comparison: a source file can be older
    than the bundle and still not be in it — a dependency bump, an aborted
    build, a file restored from git. The build is a few seconds and the
    thing it protects is whether these pictures mean anything.
    """
    app = REPO / "app"
    print("building the console…", flush=True)
    done = subprocess.run(["npm", "run", "build"], cwd=app,
                          capture_output=True, text=True)
    if done.returncode != 0:
        raise SystemExit(
            "the console did not build, so there is nothing honest to "
            f"photograph:\n{done.stdout[-2000:]}\n{done.stderr[-2000:]}")


def start_backend() -> subprocess.Popen:
    env = dict(os.environ)
    env["QRME_DB"] = "/tmp/shots.db"
    env["QRME_MEDIA_DIR"] = "/tmp/shots-media"
    Path("/tmp/shots.db").unlink(missing_ok=True)
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "qrme.api:create_app",
         "--factory", "--port", str(PORT)],
        cwd=REPO, env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(60):
        try:
            with urllib.request.urlopen(BASE + "/health", timeout=2):
                return proc
        except Exception:
            time.sleep(0.5)
    raise SystemExit("the backend never came up")


def _door(path: str, body: dict, token: str = "") -> dict:
    request = urllib.request.Request(
        BASE + path, data=json.dumps(body).encode(),
        headers={"content-type": "application/json",
                 **({"authorization": f"Bearer {token}"} if token else {})})
    with urllib.request.urlopen(request, timeout=120) as answer:
        return json.load(answer)


def converse(session: dict) -> None:
    """One exchange with the profile, through the product's own doors, so
    the chat screen is photographed with a conversation in it. The person
    is an interactor made the way the console makes one; the reply is
    whatever the deployment's model answers — the stub, here."""
    try:
        me = _door("/interactors", {"display_name": "A visitor"})
        session["interactorId"] = me["id"]
        session["interactorToken"] = me["token"]
        _door(f"/profiles/{session['profileId']}/chat",
              {"interactor_id": me["id"],
               "message": "What do you actually remember about me, and "
                          "where is it kept?"}, me["token"])
    except Exception as exc:  # noqa: BLE001 — an empty chat is still the chat
        print(f"  ? no conversation seeded ({type(exc).__name__}); "
              "the chat is photographed empty")


def open_tab(page, tab: str) -> bool:
    """Reach a tab the way a person does, and refuse to lie about it.

    ## Why this is not `goto("#tab")`

    It was, and every capture it took was the Home screen. This console
    has no hash router — `App.tsx` holds the tab in `useState` and the
    only thing that moves it is a press on the drawer. So `#market`
    loaded the app, changed nothing, and the harness photographed Home
    and filed it as the marketplace. Thirty-nine times.

        asked     photograph the screens
        mattered  photograph the screen you say you did

    A harness that navigates by a mechanism the product does not have
    fails silently and produces confident, wrong output — which is worse
    than the drawings it replaced, because a drawing is obviously a
    drawing and this looked like evidence.

    So it drives the actual drawer, and then **checks**: the tab the
    console marks `active` has to be the one that was asked for, or this
    returns False and the caller writes no file. A missing screen is a
    gap somebody notices. A wrong screen is a gap nobody notices.
    """
    # Reload between shots. Some surfaces put something over the drawer or
    # navigate away from the shell entirely, and one of them used to take
    # every capture after it down with it — a run that photographed
    # twenty-five screens and then failed the last fourteen in a row.
    page.goto(BASE + "/", wait_until="networkidle")
    page.wait_for_timeout(700)
    page.evaluate("window.scrollTo(0, 0)")
    # `is_visible`, not merely present. The fab is in the markup at every
    # width and only *drawn* where the sidebar is not permanent, so at a
    # desktop width this waited thirty seconds for a hidden button and
    # then failed the whole run — on a page whose drawer was already open.
    fab = page.query_selector(".menu-fab")
    if (fab and fab.is_visible()
            and page.get_attribute(".menu-fab", "aria-expanded") != "true"):
        fab.click()
        page.wait_for_timeout(300)
    # The drawer stacks its tabs under collapsible group heads; open all
    # of them rather than guessing which group a tab lives in.
    for head in page.query_selector_all(".nav-group-head"):
        if "open" not in (head.get_attribute("class") or ""):
            head.click()
            page.wait_for_timeout(80)
    target = page.query_selector(f'.nav-item[data-tab="{tab}"]')
    if target is None:
        return False
    target.click()
    page.wait_for_timeout(1200)
    active = page.query_selector(".nav-item.active")
    return bool(active
                and active.get_attribute("data-tab") == tab)



#: Where a recipe starts when there is no session yet — the screens a
#: person meets before the console has anybody in it.
SIGNED_OUT = "signed-out"
#: An account that is signed in with no profile chosen yet: the onboarding's
#: second stage, where a profile is created.
ACCOUNT_ONLY = "account-only"

#: Screens that are a page, but not one a nav tile opens.
#:
#: A recipe is: the number, the file stem, where to start, what a person
#: presses to get there, and a selector that proves it arrived. `proof`
#: exists on the screen being asked for and nowhere on the way to it, so a
#: recipe that lands somewhere else writes nothing and says so — a wrong
#: screen filed under a right number is worse than a gap.
INSIDE: tuple[tuple[str, str, str, tuple, str], ...] = (
    ("39", "sign-in", SIGNED_OUT, (), ".tabs .tab.active"),
    ("41", "log-in", SIGNED_OUT, (".tabs .tab:nth-child(2)",),
     ".tabs .tab:nth-child(2).active"),
    # Two pages the nav does not open, reached the way a person reaches
    # them: the press that goes there, named in the markup.
    ("204", "your-circle", "home", ('[data-go="circle"]',),
     '[data-screen="204"]'),
    # The first door: what a person meets with no account at all.
    ("01", "welcome", SIGNED_OUT, (), ".tabs"),
    # The second stage of onboarding: an account signed in, a profile
    # not yet made, and the form that makes one.
    ("02", "create-profile", ACCOUNT_ONLY, ("text=Or make another one",),
     "input[type=date]"),
    # The chat with a conversation in it: a question typed and sent the
    # way a person sends one, so the screen holds the exchange it drew.
    ("83", "chat", "chat",
     (('input[placeholder="Type a message…"]',
       "What do you actually remember about me, and where is it kept?"),
      ".chat-send"), ".bubble"),
    # A friend's face on Home is the door to their homepage.
    ("197", "their-homepage", "home", ('[data-go="visit"]',),
     '[data-screen="197"]'),
    # 205, the avatar stage, is not on this list on purpose. The harness's
    # profile has no portrait, so the stage it opens says "no avatar yet"
    # — true, and not the screen. The capture on disk is the owner's own,
    # taken in a running room with a figure the forge built from a
    # portrait; a recipe here would photograph over it on every run.
    # "Is this genuine?" — the watermark asked from the front door, no
    # account needed.
    ("148", "who-wrote-this", SIGNED_OUT, ("text=Is this genuine?",),
     'textarea[placeholder="paste the text"]'),
    ("173", "beginning-and-passing-on", "identity",
     ('[data-go="passing"]',), '[data-screen="173"]'),
    # The edge dock, opened: the agent lights' tab pressed and the face
    # beside it — the one screen the dock is the subject of rather than
    # a thing at the edge of.
    ("211", "the-edge-dock", "home", (".wl-tab",), ".watch-lights"),
    # The three kinds of room the front page opens: voices only, and the
    # AR and VR rooms as the console draws them on a phone with no
    # headset — the scene is the same rows either way, and WebXR only
    # gates the headset door.
    # Opening a room lands on its lobby — "knowing its id is not the same
    # as being here" — so the recipe goes in the way a person does.
    ("103", "audio-room", "home", ('text="Voice chat only"', 'text="Go in"'),
     ".room-scene"),
    ("106", "ar-room", "home", ('text="AR"', 'text="Go in"'), ".room-scene"),
    ("109", "vr-room", "home", ('text="VR"', 'text="Go in"'), ".room-scene"),
)


def open_inside(page, session, start, presses, proof) -> bool:
    """Reach a screen that is not a tab, and refuse to lie about it."""
    if start == SIGNED_OUT:
        page.goto(BASE + "/", wait_until="networkidle")
        page.evaluate("() => localStorage.clear()")
        page.goto(BASE + "/", wait_until="networkidle")
    elif start == ACCOUNT_ONLY:
        page.goto(BASE + "/", wait_until="networkidle")
        page.evaluate("() => localStorage.clear()")
        page.evaluate("s => localStorage.setItem('qrme.session', s)",
                      json.dumps({k: session[k] for k in
                                  ("accountId", "accountToken", "accountEmail")}))
        page.goto(BASE + "/", wait_until="networkidle")
        answer_the_notice(page)
    else:
        page.evaluate("s => localStorage.setItem('qrme.session', s)",
                      json.dumps(session))
        # A fresh page first: a room opened by the recipe before this one
        # has put the nav away, and the tab this one starts from is not
        # on screen until the console is reloaded out of the room.
        page.goto(BASE + "/", wait_until="networkidle")
        page.wait_for_timeout(600)
        if not open_tab(page, start):
            print(f"  ? could not open the {start} tab")
            return False
        # A signed-out recipe earlier in this run cleared `localStorage`,
        # so the notice may be asking again and the widgets may have
        # forgotten they were tucked away.
        answer_the_notice(page)
        tuck_the_widgets(page)
    page.wait_for_timeout(900)
    for press in presses:
        # A press is a selector to click, or a (selector, text) pair to
        # type into — the chat is photographed with a conversation in it
        # by typing one the way a person does, because the screen keeps
        # its messages in memory and draws nothing it did not see sent.
        selector, text = press if isinstance(press, tuple) else (press, None)
        target = page.query_selector(selector)
        if target is None:
            print(f"  ? nothing matched {selector}")
            return False
        if text is None:
            target.evaluate("el => el.click()")
        else:
            target.fill(text)
        page.wait_for_timeout(900)
    # Waited for, not glanced at: a room takes a moment to seat itself,
    # and a proof read the instant after the press called every room
    # unreachable.
    try:
        page.wait_for_selector(proof, timeout=8000)
    except Exception:  # noqa: BLE001 — the caller says which screen
        return False
    return True


def answer_the_notice(page) -> None:
    """Answer the problem-reporting consent card, if it is asking.

    It opens over everything on a browser that has never answered it, and
    it is answered once at the start of a run — but a recipe that clears
    `localStorage` to reach a signed-out screen puts it right back, and
    every capture after that one carries it. Idempotent: on a browser that
    has already answered, nothing matches and this does nothing.
    """
    for label in ("That's fine", "No thanks", "Yes, send them"):
        button = page.query_selector(f"text={label}")
        if button:
            button.click()
            page.wait_for_timeout(400)
            return


def tuck_the_widgets(page) -> None:
    """Minimise the floating widgets, the way a person does.

    The second half of the same repair: the minimise is remembered per
    browser and `localStorage.clear()` forgets it. Pressed, not hidden —
    the widget carries its own control, so what is photographed stays a
    state the product can actually be in.
    """
    for control in (".wl-min", ".vl-min", ".uw-min"):
        minimise = page.query_selector(control)
        if minimise:
            minimise.evaluate("el => el.click()")
            page.wait_for_timeout(200)


#: Screens that are a card on a screen, not a screen of their own.
#:
#: The census lets one component own several numbers, because a component
#: draws more than one thing a person meets. The tab captures the whole
#: page; these are the parts of it the gallery numbers separately, and
#: until now every one was a drawing for the same reason: the camera could
#: photograph a page and nothing smaller.
#:
#:     asked     can the camera reach every page
#:     mattered  can it reach everything the gallery numbers
#:
#: The element is found by `data-screen="<number>"` on the element that
#: owns it — the same shape as the `data-tab` the nav carries, and for the
#: same reason: a marker in the markup is a thing the camera and the
#: reader can both check, where a selector guessed from outside silently
#: starts matching the wrong card.
ELEMENTS: tuple[tuple[str, str, str, tuple[str, ...]], ...] = (
    ("150", "what-went-wrong", "settings", ()),
    ("22", "providers", "settings", ()),
    ("44", "avatar-studio", "identity", ()),
    ("198", "beside-the-face", "chat", ()),
    ("199", "what-it-is-doing", "chat", ()),
    # The reply as footage. It draws on the chat screen because that is
    # where a reply is read, and it is photographed as a card because the
    # four states it has are the whole surface — three of them have no
    # video in them, and those are the ones worth showing.
    ("209", "the-reply-as-footage", "chat", ()),
)


#: What the shell floats over every screen, hidden while a card sits for
#: its portrait. An element screenshot is a crop of the rendered page, not
#: a render of the element alone, so anything painted over that rectangle
#: lands in the picture — and all of this is `position: fixed`. Hiding it
#: here hides nothing from the gallery: each is photographed on every page
#: capture, which is where a reader meets them.
FURNITURE = (".edge-dock", ".edge-panel",
             ".underway", ".uw-dot", ".vault-light", ".vl-dot")


def hide_furniture(page) -> None:
    page.evaluate(
        """(sel) => {
          const style = document.createElement('style');
          style.id = 'qrme-camera-hide';
          style.textContent = sel.join(',') + '{visibility:hidden!important}';
          document.head.appendChild(style);
        }""", list(FURNITURE))


def show_furniture(page) -> None:
    page.evaluate(
        """() => {
          const style = document.getElementById('qrme-camera-hide');
          if (style) style.remove();
        }""")


def shoot_element(page, session, number, start, presses) -> bool:
    """Photograph one card, and refuse to photograph the wrong one."""
    page.evaluate("s => localStorage.setItem('qrme.session', s)",
                  json.dumps(session))
    if not open_tab(page, start):
        print(f"  ? could not open the {start} tab")
        return False
    answer_the_notice(page)
    tuck_the_widgets(page)
    for press in presses:
        target = page.query_selector(press)
        if target is None:
            print(f"  ? nothing matched {press}")
            return False
        target.evaluate("el => el.click()")
        page.wait_for_timeout(700)
    page.wait_for_timeout(600)
    return page.query_selector(f'[data-screen="{number}"]') is not None


#: Things that are painted past the right edge on purpose.
#:
#: `past_the_edge` exists to catch content clipped away by accident, and
#: two shipped designs park themselves off-edge deliberately. Reported
#: every run against every screen, they would bury the one row that
#: mattered — which is how a check with a false positive per capture stops
#: being read at all.
#:
#:     asked     is anything drawn past the edge
#:     mattered  is anything drawn past it that did not mean to be
#:
#: Each row names the reason, so a rule that stops being deliberate stops
#: being exempt. The element and everything inside it is skipped.
EDGE_EXEMPT = (
    (".agent-rail",
     "`flex-wrap: nowrap; overflow-x: auto` with `scroll-snap` on the "
     "chips: a rail of starters meant to be swiped, where the chips past "
     "the edge are the ones a thumb scrolls to."),
    (".loudness-rail",
     "asleep it is `translateX(72%)` — a faint sliver tucked into the "
     "edge, on the owner's instruction ('let's hide the volume button'), "
     "and it slides back on pointer enter. The vertical range input rides "
     "with it."),
)

def past_the_edge(page) -> list[str]:
    """Everything this viewport draws to the right of its own right edge.

    A page overflows horizontally in two unrelated ways and only one is
    visible to `document.scrollWidth`. When an element with its own
    `overflow` holds the too-wide content, the scroll container absorbs
    it: the document stays exactly as wide as the window, the number says
    the page fits, and the right-hand end of whatever is inside is clipped
    away.

        asked     is the document wider than the window
        mattered  is anything drawn past the window's edge
    """
    return page.evaluate("""(skip) => {
      const edge = document.documentElement.clientWidth;
      const over = [];
      for (const el of document.querySelectorAll('body *')) {
        const style = getComputedStyle(el);
        if (style.visibility === 'hidden' || style.display === 'none') continue;
        const box = el.getBoundingClientRect();
        if (box.width === 0 || box.height === 0) continue;
        if (box.right <= edge + 1) continue;
        if (skip.some((sel) => el.closest(sel))) continue;
        const name = el.tagName.toLowerCase()
          + (el.id ? '#' + el.id : '')
          + (el.className && typeof el.className === 'string'
             ? '.' + el.className.trim().split(/\\s+/).join('.') : '');
        over.push(name + ' +' + Math.round(box.right - edge) + 'px');
      }
      return over.slice(0, 6);
    }""", [s for s, _why in EDGE_EXEMPT])


def census() -> dict[str, int]:
    """Which screen number each console surface is, per `tests/ui_screens.txt`.

    This function is the fix for a defect in this file's own first version.
    The docstring below `TABS` said "the numbers are the census's, so a
    capture replaces the drawing that stood for the same surface" — and the
    code numbered the captures 1, 2, 3 in the order the tabs happen to be
    listed. So `home`, which the census calls screen 5, was written as
    `1-home.png`, claiming to be screen 1, which is Welcome.

        asked     photograph every surface
        mattered  file each photograph under the surface it is of

    A comment that describes what the author meant while the code does
    something else is worse than no comment: the next reader trusts it. The
    census is now read rather than described.
    """
    rows: dict[str, int] = {}
    for line in (REPO / "tests" / "ui_screens.txt").read_text(
            encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        first = parts[1].split(",")[0]
        if first.isdigit():
            rows[parts[0]] = int(first)
    return rows


#: The console component each tab renders, read off `App.tsx` rather than
#: written down here — a second list would drift from the first.
def components() -> dict[str, str]:
    import re
    source = (REPO / "app" / "src" / "App.tsx").read_text(encoding="utf-8")
    return {tab: name for tab, name in
            re.findall(r'tab === "([a-z]+)" && <([A-Z][A-Za-z]*)', source)}


def numbered(tabs: list[str]) -> list[tuple[str, str, str]]:
    """(census number, tab, stem) for every tab the census knows.

    A tab whose component is not in the census is skipped loudly rather
    than given a number nobody agreed on.
    """
    seen, by_tab = census(), components()
    out, orphans = [], []
    for tab in tabs:
        component = by_tab.get(tab)
        number = seen.get(component or "")
        if number is None:
            orphans.append(f"{tab} ({component or 'no component'})")
            continue
        out.append((f"{number:02d}", tab, tab))
    for orphan in orphans:
        print(f"  ? {orphan}: not in the census — no number to file it under")
    return out


def main(shots: list[tuple[str, str, str]]) -> None:
    """``shots`` is (screen number, tab id, filename stem)."""
    from playwright.sync_api import sync_playwright

    build_console()
    proc = start_backend()
    try:
        session = seed("/tmp/shots.db")
        converse(session)
        with sync_playwright() as play:
            browser = play.chromium.launch(
                executable_path="/opt/pw-browsers/chromium")
            page = browser.new_page(viewport=VIEWPORT,
                                    device_scale_factor=SCALE)
            page.goto(BASE + "/", wait_until="networkidle")
            page.evaluate("s => localStorage.setItem('qrme.session', s)",
                          json.dumps(session))
            # Reload, so the console has actually read that session.
            #
            # The sweeps below look for things only a signed-in console
            # draws — the consent card, the lights widget. Setting
            # localStorage does not re-render the page that is already on
            # screen, so without this the browser is still showing the
            # signed-out onboarding, both sweeps find nothing, and every
            # capture afterwards carries an unanswered consent card and a
            # widget nobody minimised.
            #
            #     asked     is the session set
            #     mattered  is the console showing the session
            # `BASE + "/"`, not a CONSOLE constant: this product serves its
            # console at the root, where its siblings serve theirs at
            # `/app/`. The reload was carried across from one of them
            # with the sibling's name for the address still in it, and
            # this harness has raised NameError on every run since.
            page.goto(BASE + "/", wait_until="networkidle")
            page.wait_for_timeout(1500)
            # The problem-reporting consent card opens over everything on a
            # browser that has never answered it — which is every fresh
            # browser, and so every capture taken after it. It is a real
            # screen a real person meets before any byte leaves, so it is
            # photographed on its own and then answered, rather than
            # hidden to get at the ones behind it.
            #
            # Its number comes from the census like every other screen's.
            # It was hard-coded once, and when this harness was carried to
            # a third product the number came with it — filing that
            # product's consent card under a number belonging to another
            # one. `ProblemNotice` is the component that draws it in all
            # three; the census says which screen that is in each.
            notice = census().get("ProblemNotice")
            for label in ("That's fine", "No thanks", "Yes, send them"):
                button = page.query_selector(f"text={label}")
                if button:
                    if notice is not None:
                        page.screenshot(path=str(
                            OUT / f"{notice:03d}-before-anything-is-sent.png"))
                    button.click()
                    page.wait_for_timeout(400)
                    break
            # Each console spells this control differently — `.wl-min` on
            # the lights widget, `.vl-min` in the vault, `.uw-min` on the
            # task window — so the sweep asks for all of them and a console
            # that has none simply finds nothing.
            #
            # The task window earns its place on this list the hard way. It
            # is *meant* to float over everything running, and at the phone
            # width these captures use it came to rest on the Hands
            # screen's move checkboxes: the controls that card exists to
            # offer. Clearing the tab bar fixed the half of that which was
            # a bug; a fixed float covers page content at some scroll
            # position no matter where it sits, and that half is the
            # feature. So the gallery minimises it, the way a person does.
            #
            # It is pressed, not hidden: the widget carries its own
            # minimise control, which is what a person does with it, and
            # the state is remembered per browser so one press carries
            # across every reload. What is photographed stays a state the
            # product can actually be in.
            # This console has none left: its lights are a tab on the
            # edge dock, closed until pressed, so there is nothing to
            # minimise — the sweep finds nothing here and stays for the
            # consoles it was written for.
            for control in (".wl-min", ".vl-min", ".uw-min"):
                minimise = page.query_selector(control)
                if minimise:
                    minimise.evaluate("el => el.click()")
                    page.wait_for_timeout(200)
            for number, tab, stem in shots:
                if not open_tab(page, tab):
                    print(f"  ! {tab}: never reached — nothing written")
                    continue
                # Scroll to the top so every capture starts where the
                # screen starts rather than wherever the last one left
                # the viewport.
                page.evaluate("window.scrollTo(0, 0)")
                page.wait_for_timeout(200)
                target = OUT / f"{number}-{stem}.png"
                page.screenshot(path=str(target), full_page=True)
                print(f"  {target.name}")
                for offender in past_the_edge(page):
                    print(f"      past the right edge: {offender}")

            # The pages that are not tabs. Same refusal.
            for number, stem, start, presses, proof in INSIDE:
                if not open_inside(page, session, start, presses, proof):
                    print(f"  ! {number}-{stem}: never reached — "
                          "nothing written")
                    continue
                page.evaluate("window.scrollTo(0, 0)")
                page.wait_for_timeout(250)
                target = OUT / f"{number}-{stem}.png"
                page.screenshot(path=str(target), full_page=True)
                print(f"  {target.name}")

            # The cards. Same refusal as the pages: a recipe whose element
            # is not on the page writes nothing and says so.
            for number, stem, start, presses in ELEMENTS:
                if not shoot_element(page, session, number, start, presses):
                    print(f"  ! {number}-{stem}: never reached — "
                          "nothing written")
                    continue
                el = page.query_selector(f'[data-screen="{number}"]')
                el.scroll_into_view_if_needed()
                page.wait_for_timeout(250)
                target = OUT / f"{number}-{stem}.png"
                hide_furniture(page)
                el.screenshot(path=str(target))
                show_furniture(page)
                print(f"  {target.name}")

            browser.close()
    finally:
        proc.terminate()


if __name__ == "__main__":
    # Every tab the shell routes to, in the shell's own order. The
    # numbers are the census's (tests/ui_screens.txt), so a capture
    # replaces the drawing that stood for the same surface.
    TABS = [
        "home", "agent", "feed", "guide", "chat", "discover", "market",
        "shop", "corner", "wall", "friends", "rooms", "blend", "solitude",
        "simulate", "campaigns", "org", "relationships", "memory",
        "studio", "delegate", "desk", "identity", "presence", "live",
        "contest", "exchanges", "grants", "party", "voice", "workshop",
        "assist", "referrals", "lobby", "audience", "beacons", "reaching",
        "leaving", "selling", "inside", "raise", "capabilities",
        # Sixteen tabs the nav has opened for releases and this list had
        # never named. Not a decision — an omission: the list was typed
        # once and every tab added since went in the nav and not here, so
        # each of those screens stayed a drawing while the console it was
        # drawn from shipped. `numbered()` skips loudly rather than
        # guessing, so the ones without a census row say so by name.
        "companies",
        "signing", "visiting", "allowed", "stranger", "themark", "inwords",
        "remainder", "plugins", "named", "robots", "hands", "placements",
        "plans", "access", "matters", "settings",
    ]
    main(numbered(TABS))
