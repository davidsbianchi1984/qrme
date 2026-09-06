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
import re
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
         "true to draw.", "{}", "[]", 0, 0, "reactive", "auto", 0,
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
    # The camera's own profile wears the founder's rendered portrait, so a
    # seat in a room shows a face rather than initials — "this one didn't
    # have my profile photo". The same file the seed gives the founder's
    # AI profile; the camera's profile is a stand-in for that one.
    # …and the field it works in, which the talk surface draws under the
    # name. A profile with none draws no line there, which is right for a
    # profile that has not said and wrong for the camera's stand-in for one
    # that has.
    founder = conn.execute(
        "SELECT p.avatar, p.industry, p.job_title FROM profiles p"
        " JOIN handles h ON h.profile_id = p.id"
        " WHERE h.handle = 'david_bianchi_ai'").fetchone()
    if founder and founder["avatar"]:
        conn.execute(
            "UPDATE profiles SET avatar=?, industry=?, job_title=? WHERE id=?",
            (founder["avatar"], founder["industry"], founder["job_title"],
             profile_id))
        conn.commit()
    # And the same profile's bound voice, so the chat is photographed
    # without the "no spoken voice bound" notice — a bound voice is the
    # state a finished profile is in, and the notice is the state of one
    # that is not finished yet.
    conn.execute(
        "INSERT OR REPLACE INTO profile_voices"
        " (profile_id, provider, voice_id, label, bound_at)"
        " SELECT ?, v.provider, v.voice_id, v.label, v.bound_at"
        "   FROM profile_voices v JOIN handles h ON h.profile_id = v.profile_id"
        "  WHERE h.handle = 'david_bianchi_ai'", (profile_id,))
    conn.commit()

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


def _rows(path: str, token: str = "") -> dict:
    """A GET, for the one place the seed has to read back what it made:
    a seat's id is minted server-side and the roster is where it is."""
    request = urllib.request.Request(
        BASE + path,
        headers={"authorization": f"Bearer {token}"} if token else {})
    with urllib.request.urlopen(request, timeout=60) as answer:
        return json.load(answer)


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
        # More conversations, so the memory vault is photographed with a
        # shelf of rows rather than one — a person reading the screen
        # should see what a vault looks like once it has been used.
        for name, line in (("Marcus Bell", "Walk me through the fee-only model again."),
                           ("Priya Raman", "Which of my services should be split first?"),
                           ("Dr. Amara Osei", "What did we say about the follow-up?"),
                           ("Elena Vasquez", "Can you plan the next lesson with me?"),
                           ("Ken Nakamura", "Remind me what we settled on for the shop hours.")):
            other = _door("/interactors", {"display_name": name})
            _door(f"/profiles/{session['profileId']}/chat",
                  {"interactor_id": other["id"], "message": line}, other["token"])
    except Exception as exc:  # noqa: BLE001 — an empty chat is still the chat
        print(f"  ? no conversation seeded ({type(exc).__name__}); "
              "the chat is photographed empty")


def furnish(session: dict) -> None:
    """A company founded and staffed, and a shop opened, through the
    product's own doors — so the company, organization and shop screens
    are photographed with rows on them rather than empty forms. Nothing
    here is drawn: every row is one the product wrote."""
    token = session["ownerToken"]
    pid = session["profileId"]
    try:
        co = _door("/companies", {"name": "Bianchi & Sons Bakery",
                                  "industry": "bakery", "headcount": 4}, token)
        for title, dept, name, duties in (
                ("Counter clerk", "Front of house", "June Okafor",
                 "Take orders, box pastries, ring up sales, keep the case stocked."),
                ("Head baker", "Kitchen", "Tomas Ferreira",
                 "Bake the morning bread, plan the week's specials, order flour."),
                ("Bookkeeper", "Back office", "Priya Raman",
                 "Reconcile the till, pay suppliers, file the quarter.")):
            seat = _door(f"/companies/{co['id']}/seats",
                         {"title": title, "department": dept}, token)
            _door(f"/companies/{co['id']}/seats/{seat['id']}/hire",
                  {"answers": [{"question": "Full name:", "answer": name},
                               {"question": "Duties:", "answer": duties},
                               {"question": "Decides alone vs escalates:",
                                "answer": "Decides the day's small calls; "
                                          "escalates money and complaints."}]},
                  token)
        # A fourth seat, left open. The three above are hired, and a
        # hired seat has no interview to draft and no study to download
        # — so with only those the two cards below could never be
        # photographed, and the recipe would report "never reached"
        # every run without saying why.
        _door(f"/companies/{co['id']}/seats",
              {"title": "Pastry chef", "department": "Kitchen"}, token)
        session["companyId"] = co["id"]
        # A second company, and the reason it exists is the exhibit
        # rather than the bakery. The study card and the kit ladder are
        # photographed on an open seat, and the bakery's open seat is a
        # pastry chef — whose skills read "recipe scaling, production
        # scheduling" and whose connections read "suppliers, shift
        # managers". True, and it says nothing a reader could not have
        # guessed from the word bakery. A home carer's do: the point of
        # a table of 45,147 positions is that the specific ones are
        # specific, and an exhibit has to be of a job somebody would not
        # already know the answer for.
        care = _door("/companies", {"name": "Bianchi Home Care",
                                    "industry": "home care",
                                    "headcount": 6}, token)
        # Both of these are rows the pool has written out by hand, and
        # that is the point of choosing them: a written row carries the
        # skills and the connections of *that job* ahead of the ones its
        # whole family shares, so the card photographs specifics rather
        # than a family heading repeated. "Home care assistant" was here
        # first and matched a physical-therapy row three families over,
        # which is the failure this exhibit is supposed to disprove.
        for title, dept in (("Care home manager", "Care"),
                            ("Housekeeper", "Household")):
            _door(f"/companies/{care['id']}/seats",
                  {"title": title, "department": dept}, token)
        # One of the two hired the way a founder actually hires: study
        # first, then sign. Every other seeded hire posts straight to
        # /hire, which leaves `connections` NULL on the seat — so the
        # employee file's "Who they reach" rendered empty and looked
        # like a missing feature rather than a seat nobody studied.
        #
        # The study's own half needs a model and this host has none. The
        # pool's half does not: `regulators, families, clients,
        # supervisors` come off the carried table, so the line
        # photographs true on a keyless host instead of blank.
        keep = [s for s in _rows(f"/companies/{care['id']}", token)["seats"]
                if s["title"] == "Housekeeper"]
        if keep:
            sid = keep[0]["id"]
            _door(f"/companies/{care['id']}/seats/{sid}/study", {}, token)
            _door(f"/companies/{care['id']}/seats/{sid}/hire",
                  {"answers": [
                      {"question": "Full name:", "answer": "Rosa Delgado"},
                      {"question": "Duties:",
                       "answer": "Keep the rooms, the linen and the "
                                 "supplies; report what needs fixing."},
                      {"question": "Decides alone vs escalates:",
                       "answer": "Decides the day's order of rooms; "
                                 "escalates damage and anything missing."}]},
                  token)
    except Exception as exc:  # noqa: BLE001 — an empty company is still the screen
        print(f"  ? no company founded ({type(exc).__name__})")
    try:
        shop = _door("/shops", {"profile_id": pid, "name": "Bianchi & Sons",
                                "blurb": "Bread at seven, pastries till they run out.",
                                "tag": "bakery"}, token)
        _door(f"/shops/{shop['id']}/offerings",
              {"kind": "goods", "title": "Sourdough loaf", "price": 9.0}, token)
        _door(f"/shops/{shop['id']}/offerings",
              {"kind": "goods", "title": "Almond croissant", "price": 4.5}, token)
    except Exception as exc:  # noqa: BLE001
        print(f"  ? no shop opened ({type(exc).__name__})")


#: A screen taller than this many phone heights is also photographed in
#: parts, one phone height each, so a reader on GitHub — where a tall
#: capture is scaled to a thumbnail — can read every part at full size.
#: The full-page capture stays; the parts stand beside it.
PARTS_ABOVE = 1.15
LONG_BEGIN = "<!-- long-screens:begin -->"
LONG_END = "<!-- long-screens:end -->"


def write_long_gallery() -> None:
    """The parts, listed in docs/gallery.md between two markers.

    Written from what is on disk rather than by hand, so a part the
    camera makes is always shown somewhere and the gallery's own guards —
    every screen shown, every reference resolving — keep holding.
    """
    gallery = REPO / "docs" / "gallery.md"
    text = gallery.read_text(encoding="utf-8")
    if LONG_BEGIN not in text:
        text = text.rstrip("\n") + (
            "\n\n## Long screens, in parts\n\nScreens taller than the glass"
            " they are read on, sliced a phone height at a time so every part"
            " reads at full size. The whole-screen capture of each is in the"
            " tour above.\n\n" + LONG_BEGIN + "\n" + LONG_END + "\n")
    groups: dict[str, list[str]] = {}
    # `-part<n>.png` exactly: a plain `*-part*` glob also matches
    # `155-party.png`, whose name simply begins that way.
    for f in sorted(OUT.glob("*.png")):
        m = re.fullmatch(r"(\d+)-([a-z0-9-]+)-part(\d+)\.png", f.name)
        if m:
            groups.setdefault(f"{m.group(1)}-{m.group(2)}", []).append(f.name)
    rows = []
    for key in sorted(groups, key=lambda k: int(k.split("-", 1)[0])):
        files = sorted(groups[key],
                       key=lambda n: int(re.search(r"part(\d+)", n).group(1)))
        number, stem = key.split("-", 1)
        # Four to a row at most: the gallery is read on a phone, and the
        # grid guard next door holds every table in this repository to
        # the same four.
        # Four to a row at most, and a table of its own for each band: the
        # gallery is read on a phone, the grid guard next door holds every
        # table here to four across, and a short row padded with blanks
        # would trip the guard that says a cell is never empty.
        tables = []
        for start in range(0, len(files), 4):
            band = files[start:start + 4]
            width = 100 // len(band)
            cells = "".join(
                f'<td align="center" width="{width}%" valign="top">'
                f'<a href="screens/{n}"><img src="screens/{n}" width="150"'
                f' alt="{stem} part {start + i + 1}"></a><br>'
                f"<sub>part {start + i + 1} of {len(files)}</sub></td>"
                for i, n in enumerate(band))
            tables.append(f"<table>\n  <tr>{cells}</tr>\n</table>")
        rows.append(f"**{number}** · {stem.replace('-', ' ')}\n\n"
                    + "\n".join(tables) + "\n")
    body = LONG_BEGIN + "\n" + "\n".join(rows) + "\n" + LONG_END
    head, _, rest = text.partition(LONG_BEGIN)
    _, _, tail = rest.partition(LONG_END)
    gallery.write_text(head + body + tail, encoding="utf-8")


#: How the console scrolls, and why a full-page capture was not the whole
#: screen. The shell is a fixed-height grid — drawer, content column,
#: dock — and the *content column* scrolls, not the document. Playwright
#: grows a `full_page` capture to the document's height, and this
#: document is exactly one phone tall on every screen, so everything
#: below the fold was cropped out of every picture in the gallery.
#:
#:     asked     photograph the whole screen
#:     mattered  the screen is taller than the glass it is shown on
#:
#: Scrolling the column and shooting each stop was the first answer and a
#: brittle one: the console re-renders under the camera and puts the
#: scroll back. So the column is *unrolled* instead — height auto, nothing
#: hidden — which grows the document, and one ordinary full-page capture
#: then holds the whole screen. The phone-height parts are slices of that
#: picture, so a part can never disagree with the whole.
_UNROLL = """() => {
  const style = document.createElement('style');
  style.id = 'qrme-camera-unroll';
  style.textContent = `
    html, body { height: auto !important; overflow: visible !important; }
    .app { height: auto !important; min-height: 100vh !important; }
    main.content, .content { height: auto !important; max-height: none !important;
      overflow: visible !important; }`;
  document.head.appendChild(style);
}"""

_ROLL_BACK = """() => {
  const style = document.getElementById('qrme-camera-unroll');
  if (style) style.remove();
}"""


def shoot_page(page, number: str, stem: str) -> list[str]:
    """Photograph a whole screen, and slice it into phone-height parts.

    The whole-screen picture is what the gallery shows; the parts stand
    beside it for the screens too tall to read at thumbnail size.
    """
    page.evaluate(_UNROLL)
    page.wait_for_timeout(400)
    target = OUT / f"{number}-{stem}.png"
    page.screenshot(path=str(target), full_page=True)
    page.evaluate(_ROLL_BACK)
    page.wait_for_timeout(150)

    from PIL import Image
    whole = Image.open(target)
    tall = VIEWPORT["height"] * SCALE
    if whole.height <= tall * PARTS_ABOVE:
        return []
    names = []
    count = -(-whole.height // tall)
    for i in range(count):
        top = i * tall
        part = whole.crop((0, top, whole.width, min(top + tall, whole.height)))
        name = f"{number}-{stem}-part{i + 1}.png"
        part.save(OUT / name)
        names.append(name)
    return names


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


#: The recipes that need a microphone, and are photographed in their own
#: browser because of it.
#:
#: Headless Chromium ships with no capture device, so the talk surface
#: photographed as "No microphone the browser can reach" — a true sentence
#: about this host and a false one about the product. Chromium's fake
#: device fixes that, and the console still takes the ordinary road to it:
#: the recogniser fails on its speech service, the recorded ear answers,
#: and the wave reads what the ear is doing.
#:
#: A second browser rather than a flag on the first, because the fake
#: device carries the fake device's NAME — Voice and Settings both list
#: what audio is playing through, and both came back saying "Fake Default
#: Audio Output". A device invented for one screen must not sign its name
#: across the others.
#:
#:     asked     can the camera give the page a microphone
#:     mattered  can it give one screen a microphone
MIC_INSIDE: tuple[tuple[str, str, str, tuple, str], ...] = (
    # What it is doing. The talk surface, opened the way a person opens it
    # — the microphone in the chat's composer — with the wave reading the
    # ear that press opened. The marker sits on the wave, so the proof is
    # the wave; the capture is the whole page, because a reading cropped
    # away from the thing it reads is not the screen.
    ("199", "what-it-is-doing", "chat", (".chat-wave",),
     '[data-screen="199"]'),
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
    # Typed rather than left blank, and typed as somebody describes the
    # work rather than names it — an empty search bar photographs the
    # head of the list in alphabetical order, which proves nothing about
    # a search. "bakes bread" was the first choice and was no better: it
    # shares a stem with Baker, so a plain substring match would have
    # found it too and the capture would show nothing the ranking does.
    # "delivers babies" shares no letter with Midwife, so the answer
    # cannot be explained by the characters typed — which is the whole
    # of what this screen is evidence for.
    #
    # The pool, opened the way a founder opens it. The tab shows the list
    # of companies, so the first press opens one — the seat form and
    # everything under it only exist inside a company. The panel is not
    # on the page until the second press, which is why this is a card
    # with a recipe rather than part of the companies tab.
    ("212", "browse-the-positions", "companies",
     (".com-row", '[data-go="browse"]',
      (".com-pool input", "delivers babies"))),
    # The same panel, asked a second way. One phrasing could be a lucky
    # row; two unrelated ones, neither sharing a letter with its answer,
    # are the ranking working rather than a coincidence photographed.
    #
    # "looks after old people" was chosen first and dropped: it answers
    # correctly — Care home manager, Support worker — and then puts a
    # zookeeper third. Cropping that row would have made a better picture
    # and a worse exhibit, so the query changed instead of the evidence.
    ("214", "reads-scans", "companies",
     (".com-row", '[data-go="browse"]',
      (".com-pool input", "reads scans")), ".com-pool"),
    # The care side, asked the way somebody asks for it. Three home-care
    # rows, none of which the typed words name.
    ("215", "cares-for-someone-at-home", "companies",
     (".com-row", '[data-go="browse"]',
      (".com-pool input", "cares for someone at home")), ".com-pool"),
    # And the money side. "advises on investments" reaches the adviser
    # under three spellings the taxonomies each chose differently —
    # Adviser, Advisor, and the plural form — which is the pool holding
    # one job under every name it is filed by rather than three jobs.
    ("216", "advises-on-investments", "companies",
     (".com-row", '[data-go="browse"]',
      (".com-pool input", "advises on investments")), ".com-pool"),
    # The study, after the interview is drafted — two presses, in the
    # order the screen requires them. Whatever answers the study is named
    # on the card, so a capture taken on a host with no model reachable
    # says so on its face rather than looking like one that had one.
    ("213", "download-knowledge", "companies",
     ("text=Bianchi Home Care", '[data-go="interview"]',
      '[data-go="study"]')),
    # The kit ladder, photographed on its third rung. Six presses and
    # not one of them leaves the seat — which is the entire claim the
    # picture is here to carry: the robot shelf used to live in
    # settings, and getting to it meant walking out of the hire you
    # were making. The two `pass` presses are the eyes and ears rungs
    # declined; only one rung is on the page at a time, so the same
    # selector means a different button each press, on purpose.
    ("217", "kitted-out-in-the-seat", "companies",
     ("text=Bianchi Home Care", '[data-go="interview"]',
      '[data-go="study"]', '[data-go="keep"]',
      '[data-go="pass"]', '[data-go="pass"]')),
    # One rung further: the trade's programs. The card is the same
    # element as 217, which is why the recipe names it — a card carries
    # one `data-screen` and this is the second screen taken of it.
    # The employee file, on a hire that was studied before it was
    # signed. "Who they reach" is the study's connections list on the
    # person it is about — the half that had nowhere to go until the
    # signature carried it.
    ("219", "who-they-reach", "companies",
     ("text=Bianchi Home Care", '[data-go="file"]'), ".com-file"),
    ("218", "the-trades-tools", "companies",
     ("text=Bianchi Home Care", '[data-go="interview"]',
      '[data-go="study"]', '[data-go="keep"]', '[data-go="pass"]',
      '[data-go="pass"]', '[data-go="pass"]'), ".com-kit"),
    ("150", "what-went-wrong", "settings", ()),
    ("22", "providers", "settings", ()),
    ("44", "avatar-studio", "identity", ()),
    ("198", "beside-the-face", "chat", ()),
    # 199 is not on this list. The wave carries the marker, but the wave
    # is 21 bars three millimetres tall — cropped to itself it is a strip
    # nobody can read, and the thing it is a reading OF is the surface
    # around it. It is photographed as a page instead, in INSIDE.
    # The reply as footage. It draws on the chat screen because that is
    # where a reply is read, and it is photographed as a card because the
    # four states it has are the whole surface — three of them have no
    # video in them, and those are the ones worth showing.
    # 209 is not on this list on purpose: the card on disk is the owner's
    # own frame of the reply as footage, stood over the console's
    # rendering bar. This host has no film service, so the camera can only
    # ever photograph the bar; a recipe here would overwrite the frame.
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


def shoot_element(page, session, where, start, presses) -> bool:
    """Walk the recipe, and say whether the card it was walking to is there.

    `where` is a selector rather than the screen number it used to be.
    Four of these recipes are the *same* card asked four different
    questions — the pool, searched four ways — and a card can carry one
    `data-screen`, so numbering the element could only ever answer for
    one of the four. The other three silently photographed nothing: the
    presses all landed, the panel was on the page, and the last line
    looked for a number that was never in the markup.
    """
    page.evaluate("s => localStorage.setItem('qrme.session', s)",
                  json.dumps(session))
    if not open_tab(page, start):
        print(f"  ? could not open the {start} tab")
        return False
    answer_the_notice(page)
    tuck_the_widgets(page)
    for press in presses:
        # Same shape as `open_inside`: a selector to click, or a
        # (selector, text) pair to type into. A search bar photographed
        # with nothing typed shows the head of the list in alphabetical
        # order, which is the one thing the search is not for.
        selector, text = press if isinstance(press, tuple) else (press, None)
        target = page.query_selector(selector)
        if target is None:
            print(f"  ? nothing matched {selector}")
            return False
        if text is None:
            target.evaluate("el => el.click()")
        else:
            target.fill(text)
            target.press("Enter")
        page.wait_for_timeout(700)
    page.wait_for_timeout(600)
    # Wait for it rather than glance once. A press that fires a request
    # — the study downloads a trade, and on a host with no model that is
    # a provider timeout before the local fallback answers — leaves the
    # card off the page well past the fixed beat above, and a single
    # look reported "never reached" for a recipe that was simply slower
    # than the harness. Two recipes walking the same three presses
    # disagreed on whether the study card existed, which is the shape of
    # a race and not of a missing card.
    for _ in range(20):
        if page.query_selector(where) is not None:
            return True
        page.wait_for_timeout(500)
    return False


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
        furnish(session)
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
                print(f"  {number}-{stem}.png")
                for part in shoot_page(page, number, stem):
                    print(f"  {part}")
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
                print(f"  {number}-{stem}.png")
                for part in shoot_page(page, number, stem):
                    print(f"  {part}")

            # The cards. Same refusal as the pages: a recipe whose element
            # is not on the page writes nothing and says so.
            for row in ELEMENTS:
                number, stem, start, presses = row[:4]
                # Which card to photograph. It defaults to the one tagged
                # with this screen's own number, and is named outright by
                # the recipes that are several screens of one element.
                where = (row[4] if len(row) > 4
                         else f'[data-screen="{number}"]')
                if not shoot_element(page, session, where, start, presses):
                    print(f"  ! {number}-{stem}: never reached — "
                          "nothing written")
                    continue
                el = page.query_selector(where)
                # `block: "start"`, not `scroll_into_view_if_needed()`.
                # That one centres what it scrolls to, which is right for
                # a control and wrong for a card: an element taller than
                # the viewport gets centred with its *top above the
                # window*, and the stitched capture renders everything
                # off-screen as black. The study card measured
                # y = -94.75 and lost its first two lines that way — a
                # heading and the sentence saying where the skills below
                # it came from, both present in the DOM and both absent
                # from the photograph.
                el.evaluate(
                    "e => e.scrollIntoView({block: 'start', "
                    "inline: 'nearest'})")
                page.wait_for_timeout(250)
                target = OUT / f"{number}-{stem}.png"
                hide_furniture(page)
                el.screenshot(path=str(target))
                show_furniture(page)
                print(f"  {target.name}")

            browser.close()

            # And the screens that need an ear, in a browser that has one.
            miked = play.chromium.launch(
                executable_path="/opt/pw-browsers/chromium",
                args=["--use-fake-device-for-media-stream",
                      "--use-fake-ui-for-media-stream"])
            mpage = miked.new_page(viewport=VIEWPORT,
                                   device_scale_factor=SCALE,
                                   permissions=["microphone"])
            mpage.goto(BASE + "/", wait_until="networkidle")
            mpage.evaluate("s => localStorage.setItem('qrme.session', s)",
                           json.dumps(session))
            mpage.reload(wait_until="networkidle")
            mpage.wait_for_timeout(600)
            answer_the_notice(mpage)
            tuck_the_widgets(mpage)
            for number, stem, start, presses, proof in MIC_INSIDE:
                if not open_inside(mpage, session, start, presses, proof):
                    print(f"  ! {number}-{stem}: never reached — "
                          "nothing written")
                    continue
                # A beat for the ear to settle into a reading: the wave is
                # the subject, and a capture taken in the quarter-second
                # before the first turn photographs it flat.
                mpage.wait_for_timeout(2500)
                mpage.evaluate("window.scrollTo(0, 0)")
                mpage.wait_for_timeout(250)
                print(f"  {number}-{stem}.png")
                for part in shoot_page(mpage, number, stem):
                    print(f"  {part}")
            miked.close()

            write_long_gallery()
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
