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
            # The problem-reporting consent card opens over everything on
            # a browser that has never answered it — which is every fresh
            # browser, and so every capture taken after it. It is a real
            # screen a real person meets, so it is answered here rather
            # than hidden, and the screens behind it are then the screens
            # the gallery is actually about.
            page.goto(f"{BASE}/#home", wait_until="networkidle")
            page.wait_for_timeout(1500)
            for label in ("That's fine", "No thanks"):
                button = page.query_selector(f"text={label}")
                if button:
                    button.click()
                    page.wait_for_timeout(500)
                    break
            # The problem-reporting consent card opens over everything on
            # a browser that has never answered it, which is every fresh
            # browser — and it is a real screen a real person meets, not
            # something to hide. It gets photographed once, on its own,
            # and answered so the screens behind it are the screens the
            # gallery is about.
            page.goto(f"{BASE}/#home", wait_until="networkidle")
            page.wait_for_timeout(1200)
            asked = page.query_selector("text=That's fine")
            if asked:
                page.screenshot(path=str(OUT / "0-first-question.png"))
                asked.click()
                page.wait_for_timeout(400)
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
    main([(str(i + 1), tab, tab) for i, tab in enumerate(TABS)])
