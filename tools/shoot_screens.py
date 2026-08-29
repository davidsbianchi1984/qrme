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
    return {"accountId": account,
            "accountToken": auth.issue("account", account),
            "accountEmail": email,
            "profileId": profile_id,
            "ownerToken": auth.issue("owner", profile_id)}


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
    fab = page.query_selector(".menu-fab")
    if fab and page.get_attribute(".menu-fab", "aria-expanded") != "true":
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

    proc = start_backend()
    try:
        session = seed("/tmp/shots.db")
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
            page.goto(CONSOLE, wait_until="networkidle")
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
        "leaving", "selling", "inside", "raise",
    ]
    main(numbered(TABS))
