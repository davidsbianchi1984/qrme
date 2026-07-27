"""The profile homepage a person builds themselves.

Every profile already had a *front page* — portrait, skills, experience,
rating — assembled by :mod:`qrme.frontpage` from what the platform knows. It is
consistent, it is useful, and it looks exactly like everybody else's, because a
generated page is the same page 34 times.

This is the other kind: the one somebody makes. A theme, a colour, a tagline in
their own words, a paragraph about themselves, and a **Top 8** — the friends
they want at the front, in the order they want them. It is the MySpace idea,
and the reason it is worth reviving is not nostalgia for its own sake. A page
somebody arranged tells you something a generated one cannot: what they thought
was worth putting first.

Three things this deliberately does not do.

**Real HTML, through an allowlist.** People can write their own markup — that
is the thing anybody actually remembers about a MySpace profile — and every tag
and attribute goes through :mod:`qrme.markup` first. Raw markup is how the Samy
worm took MySpace down in 2005: script smuggled through a profile, running in
the browser of everyone who looked at it. The nostalgia is worth keeping; that
is not. What the filter strips is reported back, so the editor can say *your
<script> was dropped* rather than silently handing back a page that does less
than its author wrote.

**The Top 8 does not reorder the friends list.** The founder pins are fixed
there, and this is a showcase rather than a second source of truth for the same
fact. Somebody's Top 8 is what they chose to feature; their friends list is who
they stand with, and those are different questions.

**About-me text is moderated like anything else a person writes.** A profile
page is a surface other people read, so it goes through the same filter as a
chat turn, and a blocked one is returned to its author with the reason rather
than vanishing.
"""

from __future__ import annotations

import json
import re

from . import db, friends, markup, moderation

# The presets, named for what they feel like rather than what they contain.
# A closed set, because "pick a theme" is a decision a person can make in two
# seconds and "write some CSS" is a decision that ends in a support ticket.
THEMES: dict[str, dict] = {
    "midnight": {"label": "Midnight", "bg": "#0b0720", "ink": "#eceaff",
                 "note": "the house style — deep indigo, neon accents"},
    "starfield": {"label": "Starfield", "bg": "#05060f", "ink": "#dfe6ff",
                  "note": "black, with the lights turned down"},
    "sunset": {"label": "Sunset", "bg": "#1d1206", "ink": "#ffe9cc",
               "note": "warm amber, late in the day"},
    "chrome": {"label": "Chrome", "bg": "#101418", "ink": "#e8eef4",
               "note": "brushed grey, all business"},
    "meadow": {"label": "Meadow", "bg": "#0c1f14", "ink": "#e2f5e8",
               "note": "green and quiet"},
    "paper": {"label": "Paper", "bg": "#f4f1e8", "ink": "#1d1a14",
              "note": "light, for people who never liked dark mode"},
}
DEFAULT_THEME = "midnight"

LAYOUTS = ("classic", "stacked", "gallery")
DEFAULT_LAYOUT = "classic"

MAX_TAGLINE = 90
MAX_ABOUT = 1200
MAX_HTML = 20000
MAX_LINKS = 12
# How much of the feed a homepage carries. Short on purpose: a page is
# somewhere you arrive, and the endless version lives on its own screen.
FEED_ON_PAGE = 6
TOP_FRIENDS = 8              # the number is the joke, and it is a good number

_HEX = re.compile(r"^#[0-9a-fA-F]{6}$")


class PageError(ValueError):
    """A page setting that cannot stand."""


def _row(profile_id: str):
    return db.connect().execute(
        "SELECT * FROM profile_pages WHERE profile_id=?",
        (profile_id,)).fetchone()


def theme_catalog() -> list[dict]:
    return [{"id": k, **v} for k, v in THEMES.items()]


def _check_links(links: list[dict]) -> list[dict]:
    """Outbound links from a page — a storefront needs somewhere to point.

    Same URL rule the markup filter applies, for the same reason: an unknown
    scheme is not a harmless one.
    """
    if len(links) > MAX_LINKS:
        raise PageError(f"a page carries at most {MAX_LINKS} links")
    out = []
    for link in links:
        label = (link.get("label") or "").strip()
        url = (link.get("url") or "").strip()
        if not label or not url:
            raise PageError("a link needs a label and a url")
        if len(label) > 60:
            raise PageError("a link label is at most 60 characters")
        if not markup._safe_url(url):
            raise PageError(
                f"{url!r} is not a link a page may carry — http, https and "
                f"mailto only")
        out.append({"label": label, "url": url})
    return out


def set_page(profile_id: str, *, theme: str | None = None,
             accent: str | None = None, layout: str | None = None,
             tagline: str | None = None, about: str | None = None,
             top_friends: list[str] | None = None,
             html: str | None = None, links: list[dict] | None = None,
             show_offers: bool | None = None,
             author: dict | None = None) -> dict:
    """Update the parts of the page the owner controls.

    Only the fields passed are touched, so a client editing the tagline cannot
    blank the about text by not sending it — the mistake that turns an edit
    form into a delete button.
    """
    if theme is not None and theme not in THEMES:
        raise PageError(
            f"unknown theme {theme!r}; pick one of {', '.join(THEMES)}")
    if layout is not None and layout not in LAYOUTS:
        raise PageError(
            f"unknown layout {layout!r}; pick one of {', '.join(LAYOUTS)}")
    if accent is not None and not _HEX.match(accent):
        raise PageError("accent must be a #rrggbb colour")
    if tagline is not None and len(tagline) > MAX_TAGLINE:
        raise PageError(f"a tagline is at most {MAX_TAGLINE} characters")
    if about is not None and len(about) > MAX_ABOUT:
        raise PageError(f"about is at most {MAX_ABOUT} characters")

    status, flag = "approved", None
    if about and about.strip():
        verdict = moderation.review(about, None, author or {"birthdate": None},
                                    maturity="general")
        if not verdict.approved:
            status, flag = "blocked", verdict.reason

    if top_friends is not None:
        top_friends = _check_top(profile_id, top_friends)

    html_removed = None
    if html is not None:
        if len(html) > MAX_HTML:
            raise PageError(f"page markup is at most {MAX_HTML} characters")
        # Stored already-safe. Sanitising on the way in rather than on the way
        # out means there is exactly one moment where unsafe markup could
        # exist, and it is before anything is written — rather than one per
        # renderer, each of which could forget.
        html, removed = markup.sanitise(html)
        html_removed = json.dumps(removed)

    if links is not None:
        links = _check_links(links)

    current = _row(profile_id)
    now = db.utcnow()
    if current is None:
        db.connect().execute(
            "INSERT INTO profile_pages (profile_id, theme, accent, layout,"
            " tagline, about, about_status, about_flag, top_friends, html,"
            " html_removed, links, show_offers, updated_at)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (profile_id, theme or DEFAULT_THEME, accent,
             layout or DEFAULT_LAYOUT, tagline, about, status, flag,
             json.dumps(top_friends or []), html, html_removed or "[]",
             json.dumps(links or []), int(bool(show_offers)), now))
    else:
        db.connect().execute(
            "UPDATE profile_pages SET theme=?, accent=?, layout=?, tagline=?,"
            " about=?, about_status=?, about_flag=?, top_friends=?, html=?,"
            " html_removed=?, links=?, show_offers=?,"
            " updated_at=? WHERE profile_id=?",
            (theme if theme is not None else current["theme"],
             accent if accent is not None else current["accent"],
             layout if layout is not None else current["layout"],
             tagline if tagline is not None else current["tagline"],
             about if about is not None else current["about"],
             status if about is not None else current["about_status"],
             flag if about is not None else current["about_flag"],
             json.dumps(top_friends) if top_friends is not None
             else current["top_friends"],
             html if html is not None else current["html"],
             html_removed if html_removed is not None
             else current["html_removed"],
             json.dumps(links) if links is not None else current["links"],
             int(bool(show_offers)) if show_offers is not None
             else current["show_offers"],
             now, profile_id))
    db.connect().commit()
    return page(profile_id, owner=True)


def _check_top(profile_id: str, ids: list[str]) -> list[str]:
    """Validate a Top 8 selection.

    Must be friends, must be distinct, and there is a hard cap. Featuring
    somebody you are not connected to would make the showcase say something
    the graph does not.
    """
    if len(ids) > TOP_FRIENDS:
        raise PageError(f"a Top {TOP_FRIENDS} holds at most {TOP_FRIENDS}")
    if len(set(ids)) != len(ids):
        raise PageError("the same friend twice is still one friend")
    allowed = {f["profile_id"] for f in friends.friends_of(profile_id)}
    for fid in ids:
        if fid not in allowed:
            raise PageError(
                f"{fid} is not on this profile's friends list — a Top "
                f"{TOP_FRIENDS} features friends, it does not create them")
    return list(ids)


def page(profile_id: str, owner: bool = False, feed: bool = True) -> dict:
    """The page as it should be rendered.

    ``owner=True`` includes a blocked about-text and why, so its author can
    see and fix it. Everyone else gets the page without it — the shape
    :mod:`qrme.audience` uses for a blocked comment, for the same reason.
    """
    row = _row(profile_id)
    theme_id = (row["theme"] if row else DEFAULT_THEME) or DEFAULT_THEME
    theme = THEMES[theme_id]

    about, blocked = None, None
    if row and row["about"]:
        if row["about_status"] == "approved":
            about = row["about"]
        elif owner:
            about, blocked = row["about"], row["about_flag"]

    top = []
    if row and row["top_friends"]:
        wanted = json.loads(row["top_friends"])
        by_id = {f["profile_id"]: f for f in friends.friends_of(profile_id)}
        # Rendered in the owner's order, and silently skipping anybody no
        # longer a friend — a Top 8 pointing at a removed friend should thin
        # out rather than 404 the page it sits on.
        top = [by_id[fid] for fid in wanted if fid in by_id]

    # The feed, on the page rather than only on its own screen. A homepage
    # that shows what you made and nothing of what anyone else is doing is a
    # business card; the reason people sat on their MySpace page was that it
    # was also where the day's news arrived. Ranked for this profile by the
    # same rules as the standalone feed — public actions only — and capped
    # short, because a page is a place you arrive rather than a place you
    # scroll forever.
    timeline = []
    if feed:
        from . import wall
        timeline = wall.for_you(profile_id, limit=FEED_ON_PAGE)

    # The storefront half: what this profile is offering, straight from the
    # marketplace rather than retyped onto the page. A second copy of a price
    # is a second price that can be wrong.
    offers = []
    if row and row["show_offers"]:
        offers = [
            {"id": r["id"], "kind": r["kind"], "title": r["title"],
             "blurb": r["blurb"], "area": r["area"]}
            for r in db.connect().execute(
                "SELECT id, kind, title, blurb, area FROM listings"
                " WHERE profile_id=? ORDER BY created_at DESC LIMIT 8",
                (profile_id,)).fetchall()]

    return {
        "profile_id": profile_id,
        "theme": {"id": theme_id, **theme},
        "accent": (row["accent"] if row else None),
        "layout": (row["layout"] if row else DEFAULT_LAYOUT) or DEFAULT_LAYOUT,
        "tagline": (row["tagline"] if row else None),
        "about": about,
        "about_blocked": blocked,
        "top_friends": top,
        # Already sanitised in storage — a renderer never sees raw markup, so
        # no renderer can forget to clean it.
        "html": (row["html"] if row else None),
        "html_removed": (json.loads(row["html_removed"]) if row else []),
        "links": (json.loads(row["links"]) if row else []),
        "offers": offers,
        "feed": timeline,
        "show_offers": bool(row["show_offers"]) if row else False,
        "customised": row is not None,
        "updated_at": (row["updated_at"] if row else None),
    }
