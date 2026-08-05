"""Two codes that look identical and go opposite ways.

A **placed beacon** brings a stranger to QRME — the profile answers them here.
A **platform beacon** sends them away, to an account that already exists. Only
where there is no handle to build a link from does the second fall back to a
QRME page. The pictures are indistinguishable, so the difference has to be
said rather than discovered by scanning one.

And the fact that shaped the screen: **there is no way to look at a scan
without adding to the count.** Every scan surface increments — the page, its
JSON twin, and the older `/summon?ref=` — because the server cannot tell an
owner checking their own sticker from a stranger who found it. Only the QR
image itself is free. So the console renders pictures freely and never opens a
scan page on its own; the links are deliberate presses, labelled with what
they cost.

Two defects this round found, both invisible to the typecheck:

* a desk beacon returned a **relative** `scan_url` while the profile beacon
  next door returned an absolute one. The console rendered it as a link, which
  resolved against the *console's* own origin — so the desk screen's scan link
  went nowhere in every build where the console is not served by the API,
  which is every packaged build;
* a desk's view frame — the picture that carries *not live, and not claimed to
  be* — was **never rendered anywhere in the console**. It had been sitting on
  the audit's exemption list, marked "rendered in an `<img src>`, not fetched
  by the API client", and no such `<img src>` existed. The exemption was made
  out of a blind spot, and it stopped anybody asking.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()


def _src(rel: str) -> str:
    return (REPO / rel).read_text(encoding="utf-8")


def _markup(rel: str) -> str:
    """The file with comments stripped — a claim in a docstring is not a
    claim on the screen, and a guard that reads the whole file passes on the
    prose that explains the decision instead of on the decision."""
    s = re.sub(r"/\*.*?\*/", "", _src(rel), flags=re.S)
    return re.sub(r"^\s*//.*$", "", s, flags=re.M)


def _profile(client, account="acct_bcn"):
    p = client.post("/profiles", json={
        "owner_id": account, "kind": "fictional", "display_name": "Rosa",
        "purpose": "companion_coach", "persona": "warm",
        "verification": {"birthdate": "1990-01-01"}}).json()
    head = {"authorization": f"Bearer {p['owner_token']}"}
    client.post(f"/memberships/{account}", json={"plan": "pro"}, headers=head)
    return p, head


# --- what a scan costs ------------------------------------------------------

def test_asking_for_the_picture_is_not_a_scan(client):
    """The one read that is free, and the reason the screen can render every
    code at once without touching anybody's numbers."""
    p, head = _profile(client, "acct_free_look")
    b = client.post(f"/profiles/{p['id']}/beacons", headers=head,
                    json={"label": "Porch"}).json()

    def scans():
        rows = client.get(f"/profiles/{p['id']}/beacons", headers=head).json()
        return next(r["scans"] for r in rows if r["id"] == b["id"])

    assert scans() == 0
    client.get(f"/beacons/{b['id']}/qr.svg")
    assert scans() == 0, "fetching the picture counted as somebody scanning it"


def test_every_way_of_reading_a_scan_counts_it(client):
    """Recorded rather than worked around. A `?preview=1` would let any
    scanner opt out of being counted, and the count is the only evidence a
    sticker on a wall is working at all — so the honest answer is that
    checking your own code costs one, and the console says so."""
    p, head = _profile(client, "acct_counts")
    b = client.post(f"/profiles/{p['id']}/beacons", headers=head,
                    json={"label": "Porch"}).json()

    def scans():
        rows = client.get(f"/profiles/{p['id']}/beacons", headers=head).json()
        return next(r["scans"] for r in rows if r["id"] == b["id"])

    client.get(f"/summon?ref={b['id']}")
    assert scans() == 1, "the JSON surface stopped counting"
    client.get(f"/b/{b['id']}")
    assert scans() == 2, "the scan page stopped counting"


def test_the_console_says_a_scan_link_costs_one():
    """Rendered, not just documented. An owner who follows one of these
    without being told inflates the number they were checking."""
    # Both screens' copy now lives in the l10n table; each must still look
    # its own key up, and the table must still say it.
    assert 'tr("plc.openhere", lang)' in _markup(
        "app/src/screens/Placements.tsx")
    assert 'tr("desk.beacons.open"' in _markup("app/src/screens/Desk.tsx")
    l10n = _markup("app/src/l10n.ts")
    assert l10n.count("counts as a scan") >= 2, (
        "one of the two screens has stopped warning that following the "
        "link inflates the number somebody is checking")


# --- the two directions -----------------------------------------------------

def test_a_platform_beacon_points_away_from_qrme(client):
    p, head = _profile(client, "acct_away")
    cid = client.post(f"/profiles/{p['id']}/social", headers=head, json={
        "platform": "instagram", "direction": "publish",
        "handle": "rosa"}).json()["id"]
    view = client.get(f"/social/{cid}/beacon").json()
    assert view["presence_url"].startswith("https://instagram.com/")


def test_with_no_handle_it_falls_back_to_a_qrme_page(client):
    """There is nothing else it could point at, and a code that resolves
    nowhere is worse than one that brings people home."""
    p, head = _profile(client, "acct_nohandle")
    cid = client.post(f"/profiles/{p['id']}/social", headers=head, json={
        "platform": "mastodon", "direction": "publish"}).json()["id"]
    view = client.get(f"/social/{cid}/beacon").json()
    assert view["handle"] is None
    assert "/summon?ref=soc:" in view["presence_url"]


def test_a_placed_beacon_points_at_qrme(client):
    """The opposite direction, asserted beside its twin so the pair cannot
    drift apart quietly."""
    p, head = _profile(client, "acct_home")
    b = client.post(f"/profiles/{p['id']}/beacons", headers=head,
                    json={"label": "Porch"}).json()
    assert b["scan_url"].endswith(f"/b/{b['id']}")


def test_the_screen_says_the_two_go_opposite_ways():
    src = _markup("app/src/screens/Beacons.tsx")
    assert "away" in src and "here" in src


# --- collect and publish never share a row ----------------------------------

def test_a_collect_connection_has_no_beacon(client):
    p, head = _profile(client, "acct_collect")
    cid = client.post(f"/profiles/{p['id']}/social", headers=head, json={
        "platform": "x", "direction": "collect", "handle": "rosa"}).json()["id"]
    assert client.get(f"/social/{cid}/beacon").status_code == 409
    assert client.get(f"/social/{cid}/qr.svg").status_code == 409


def test_the_list_says_so_before_anybody_is_refused(client):
    """`beacon: null` is how the screen knows not to offer a button that
    would answer 409. Being refused is a worse way to learn it."""
    p, head = _profile(client, "acct_saysso")
    client.post(f"/profiles/{p['id']}/social", headers=head, json={
        "platform": "x", "direction": "collect"})
    client.post(f"/profiles/{p['id']}/social", headers=head, json={
        "platform": "instagram", "direction": "publish", "handle": "r"})
    rows = client.get(f"/profiles/{p['id']}/social", headers=head).json()
    by_dir = {r["direction"]: r["beacon"] for r in rows}
    assert by_dir["collect"] is None
    assert by_dir["publish"] is not None


def test_the_screen_only_offers_a_code_where_there_is_one():
    """The button is conditional on `c.beacon`, not on the direction string:
    the server's own answer, rather than the console's guess at it."""
    assert "c.beacon &&" in _markup("app/src/screens/Beacons.tsx")


# --- the relative scan_url --------------------------------------------------

def test_a_desk_beacon_scan_url_is_absolute(client):
    """It describes what the printed code encodes, and a code on a shop door
    has no origin to be relative to. It was a bare path until a console link
    went to use it and resolved against the console's own origin."""
    p, head = _profile(client, "acct_desk")
    d = client.post("/desks", headers=head, json={
        "owner_id": "acct_desk", "display_name": "Bakery", "trade": "baker",
        "attestor": "Marco", "basis": "I staff it"}).json()
    dhead = {"authorization": f"Bearer {d['desk_token']}"}
    b = client.post(f"/desks/{d['desk_id']}/beacons", headers=dhead,
                    json={"label": "Shop door"}).json()
    assert b["scan_url"].startswith("http"), (
        "a relative scan_url resolves against whatever origin renders it, "
        "which is not the one the printed code carries")
    assert b["scan_url"].endswith(f"/d/{b['id']}")


def test_both_beacon_kinds_answer_the_same_shape(client):
    """The pair, asserted together. They disagreed for as long as nobody put
    them side by side."""
    p, head = _profile(client, "acct_pair")
    d = client.post("/desks", headers=head, json={
        "owner_id": "acct_pair", "display_name": "Bakery", "trade": "baker",
        "attestor": "Marco", "basis": "I staff it"}).json()
    dhead = {"authorization": f"Bearer {d['desk_token']}"}
    desk_b = client.post(f"/desks/{d['desk_id']}/beacons", headers=dhead,
                         json={"label": "Door"}).json()
    prof_b = client.post(f"/profiles/{p['id']}/beacons", headers=head,
                         json={"label": "Porch"}).json()
    for b in (desk_b, prof_b):
        assert b["scan_url"].startswith("http")
        assert b["qr_svg"].startswith("/"), (
            "the QR path is fetched against the API this client is already "
            "talking to, so it stays a path")


# --- the frame nobody was shown ---------------------------------------------

def test_a_desk_feed_carries_its_own_honesty_note(client):
    p, head = _profile(client, "acct_feed")
    d = client.post("/desks", headers=head, json={
        "owner_id": "acct_feed", "display_name": "Bakery", "trade": "baker",
        "attestor": "Marco", "basis": "I staff it"}).json()
    assert d["feed"]["live"] is False
    assert "not live" in d["feed"]["note"].lower()


def test_the_console_actually_renders_that_frame():
    """It did not, for as long as the route sat on the audit's exemption
    list. The note is the whole point of the block, and it was being served
    to nobody."""
    src = _markup("app/src/screens/Desk.tsx")
    assert "/view.webp" in src, "the desk's frame is not rendered anywhere"
    assert "desk.feed" in src, "the frame is shown without its note"


# --- the exemption list -----------------------------------------------------

def test_nothing_is_exempt_merely_because_the_audit_cannot_see_it():
    """The rule the list now holds to. Three entries were on it because an
    `<img src>` was invisible to the extractor — and one of those three
    turned out to have no door at all, which is precisely what an exemption
    made out of a blind spot hides."""
    import sys
    sys.path.insert(0, str(REPO / "tests"))
    import clientpaths as cp

    for path in cp.NOT_A_CLIENT_CALL:
        assert "qr.svg" not in path or "medical-id" in path, (
            f"{path} is exempted as un-callable, but a QR is an `<img src>` "
            "and an `<img src>` is a door — teach the extractor instead")


@pytest.mark.parametrize("markup", [
    '<img src={getBase() + `/beacons/${id}/qr.svg`} />',
    '<a href={getBase() + `/b/${id}`}>open</a>',
])
def test_the_extractor_reads_markup_requests(markup):
    """A browser fetching a URL is a request whether or not a function was
    called to make it happen. Asserted by matching the markup rather than by
    reading the pattern's source, so a rewritten regex that stops working
    still fails."""
    import sys
    sys.path.insert(0, str(REPO / "tests"))
    import clientpaths as cp

    hits = [f for f in cp.CONSOLE.calls if f.opener.search(markup)]
    assert hits, (
        "no call form matches this markup, so every door written that way "
        f"counts as missing: {markup}")
    form = hits[0]
    body = cp._call_body(markup, form.opener.search(markup).end() - 1,
                         form.delims)
    lit = cp.CONSOLE.literal.search(body)
    assert lit, f"the path was not read out of {body!r}"
    path = cp.normalise(next(g for g in lit.groups() if g is not None),
                        cp.CONSOLE)
    assert path.startswith("/b"), path


# --- the console half -------------------------------------------------------

def test_the_beacons_screen_exists():
    assert (REPO / "app/src/screens/Beacons.tsx").exists()


@pytest.mark.parametrize("binding", [
    "api.socialConnections(", "api.connectSocial(",
    "api.disconnectSocial(", "api.socialBeacon(",
])
def test_the_beacons_screen_calls_it(binding):
    assert binding in _src("app/src/screens/Beacons.tsx")


def test_the_desk_screen_shows_what_a_scanner_receives():
    assert "api.deskScanCard(" in _src("app/src/screens/Desk.tsx")
