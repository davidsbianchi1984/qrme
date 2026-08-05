"""A refused request left a room behind, and the host's panel read a swap.

`Desk` is the host's console — open a desk, set your presence, point the
camera, read who rang, bring a guest up — and every route it calls is
owner-only. There was no visitor's side at all, and the visitor is the person
the feature is *for*: somebody standing in front of an empty chair with a sign
on it saying to ring the bell. Seven routes, plus `askToComeUp`, which had sat
in `api.ts` for months with no screen calling it.

Building that side found three defects, and the third was found by the
compiler after the first two were fixed.

## The room minted by a caller we were turning away

Joining as a `guest` needs an account: the host is deciding about a person,
not an anonymous request. The route said exactly that and answered `401`. It
also called ``desks.join`` first — which mints the stream's room on first
arrival, a real row, committed — and *then* asked who was calling. So an
anonymous guest request was refused and left a room behind it.

``ask_to_come_up``, the very next route in the same file, already had the
order right: gate the rating, identify the caller, then write.

## Two fields that were exactly swapped

`DeskOverlay` was written from the route's name rather than its answer, and
`Desk` rendered three fields wrong as a result:

* ``style`` is a layout object, so *laid out as a ${style}* printed
  ``[object Object]``;
* ``waiting`` is a **count** and was typed as a list, so ``waiting.length``
  printed ``undefined waiting``;
* ``comments`` is a **list** and was typed as a count, so ``{comments}``
  rendered nothing while empty — and would have thrown *Objects are not valid
  as a React child* the moment anybody said something on the stream.

`api.ts` states the rule for itself twenty lines further down, over the
marketplace block: *every shape below was read off a running server rather
than off the route signatures*. This block skipped it.

## The field that was never there

With the types corrected the compiler found the rest: `DeskGuest` carried
``state?: string`` behind an index signature, and the wire field is
``status``. So the label never rendered, and — worse — the guard
``g.state !== "accepted" && g.state !== "declined"`` was **always true**. The
host was offered *Let them up* for people already up, and *Not now* for people
already turned away.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_desks import _desk, _token  # noqa: E402

from qrme import db  # noqa: E402


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()


def _visitor(client, name="Visitor", birthdate="1990-01-01"):
    row = client.post("/interactors", json={
        "display_name": name, "birthdate": birthdate}).json()
    return row["id"], {"authorization": f"Bearer {row['token']}"}


def _room_of(desk_id: str):
    return db.connect().execute(
        "SELECT room_id FROM desks WHERE id=?", (desk_id,)).fetchone()["room_id"]


# --- the refused request that wrote anyway ---------------------------------

def test_a_refused_guest_join_mints_no_room(client):
    """The defect, stated as the invariant it broke: a caller being turned
    away cannot change what is stored on the way out."""
    desk = _desk(client).json()["desk_id"]
    assert _room_of(desk) is None

    refused = client.post(f"/desks/{desk}/join", json={"mode": "guest"})
    assert refused.status_code == 401
    assert "needs an account" in refused.json()["detail"]
    assert _room_of(desk) is None, (
        "the room was minted before the caller was identified, so a 401 left "
        "a committed row behind it")


def test_the_room_is_still_minted_for_somebody_allowed_in(client):
    """Moving the check must not move the feature."""
    desk = _desk(client).json()["desk_id"]
    joined = client.post(f"/desks/{desk}/join", json={"mode": "audience"})
    assert joined.status_code == 201
    assert _room_of(desk) == joined.json()["room_id"]


def test_a_signed_in_guest_still_gets_a_room_and_a_request(client):
    desk = _desk(client).json()["desk_id"]
    _uid, mine = _visitor(client)
    r = client.post(f"/desks/{desk}/join", json={"mode": "guest"},
                    headers=mine)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["room_id"] and body["guest_request"]["status"] == "requested"
    assert body["on_stream"] is False, (
        "asking is not being granted, and the answer says so rather than "
        "leaving a client to infer it")


def test_an_unknown_mode_is_refused_without_writing(client):
    desk = _desk(client).json()["desk_id"]
    assert client.post(f"/desks/{desk}/join",
                       json={"mode": "nonsense"}).status_code == 422
    assert _room_of(desk) is None


# --- what the visitor may do without an account ----------------------------

def test_the_card_and_the_bell_are_public(client):
    """A desk is a shopfront, and the visitor at an empty chair is exactly
    the person who has no account yet."""
    desk = _desk(client).json()["desk_id"]
    card = client.get(f"/desks/{desk}")
    assert card.status_code == 200
    assert card.json()["designation"] == "Live person — not AI"
    assert card.json()["ai"] is False and card.json()["human"] is True

    rung = client.post(f"/desks/{desk}/bell", json={"note": "at the counter"})
    assert rung.status_code == 201
    assert rung.json()["waiting"] == 1


def test_who_rang_is_the_hosts_alone(client):
    desk = _desk(client).json()
    assert client.get(f"/desks/{desk['desk_id']}/rings").status_code == 401
    assert client.get(f"/desks/{desk['desk_id']}/rings",
                      headers=_token(desk)).status_code == 200


def test_the_queue_of_raised_hands_is_the_hosts_alone(client):
    """Who asked to appear on someone's stream is theirs to see."""
    desk = _desk(client).json()
    d = desk["desk_id"]
    _uid, mine = _visitor(client)
    assert client.post(f"/desks/{d}/guests", json={"display_name": "Sam"},
                       headers=mine).status_code == 201
    assert client.get(f"/desks/{d}/guests").status_code == 401
    assert client.get(f"/desks/{d}/guests", headers=mine).status_code == 403
    assert client.get(f"/desks/{d}/guests",
                      headers=_token(desk)).status_code == 200


def test_only_the_host_brings_somebody_up(client):
    desk = _desk(client).json()
    d = desk["desk_id"]
    _uid, mine = _visitor(client)
    req = client.post(f"/desks/{d}/guests", json={}, headers=mine).json()
    _o, theirs = _visitor(client, "Stranger")
    assert client.post(f"/desks/{d}/guests/{req['id']}/accept",
                       headers=theirs).status_code == 403
    assert client.post(
        f"/desks/{d}/guests/{req['id']}/accept").status_code == 401
    assert client.post(f"/desks/{d}/guests/{req['id']}/accept",
                       headers=_token(desk)).status_code == 201


def test_a_raised_hand_reports_status_not_state(client):
    """The console read `state` for months. It was never on the wire."""
    desk = _desk(client).json()["desk_id"]
    _uid, mine = _visitor(client)
    row = client.post(f"/desks/{desk}/guests", json={}, headers=mine).json()
    assert row["status"] == "requested"
    assert "state" not in row


# --- leaving a profile somewhere -------------------------------------------

def _profile(client, account="acct_bcn", **over):
    body = {"owner_id": account, "kind": "fictional", "display_name": "Rosa",
            "purpose": "companion_coach", "persona": "a neighbour",
            "verification": {"birthdate": "1980-01-01"}}
    body.update(over)
    p = client.post("/profiles", json=body).json()
    return p["id"], {"authorization": f"Bearer {p['owner_token']}"}


def test_only_the_owner_places_lists_or_picks_up(client):
    """Each of these three checks exists because the route shipped without
    it. The list in particular is free text naming physical places a person
    frequents, and it was readable from the profile id alone."""
    pid, head = _profile(client)
    _other, theirs = _profile(client, "acct_other", display_name="Sal")

    assert client.post(f"/profiles/{pid}/beacons",
                       json={"label": "bench"}).status_code == 401
    assert client.post(f"/profiles/{pid}/beacons", json={"label": "bench"},
                       headers=theirs).status_code == 403

    made = client.post(f"/profiles/{pid}/beacons", headers=head,
                       json={"label": "the bench",
                             "location": "Rosa's garden"})
    assert made.status_code == 201, made.text
    bid = made.json()["id"]

    assert client.get(f"/profiles/{pid}/beacons").status_code == 401
    assert client.get(f"/profiles/{pid}/beacons",
                      headers=theirs).status_code == 403
    assert client.get(f"/profiles/{pid}/beacons",
                      headers=head).status_code == 200

    assert client.delete(f"/beacons/{bid}").status_code == 401
    assert client.delete(f"/beacons/{bid}", headers=theirs).status_code == 403
    assert client.delete(f"/beacons/{bid}", headers=head).status_code == 200


def test_picking_one_up_deactivates_rather_than_deletes(client):
    """The printed paper is still on the wall, so the code has to keep
    answering — with nothing."""
    pid, head = _profile(client, "acct_pickup")
    bid = client.post(f"/profiles/{pid}/beacons", headers=head,
                      json={"label": "bench"}).json()["id"]
    assert client.get(f"/b/{bid}/card").status_code == 200
    assert client.delete(f"/beacons/{bid}", headers=head).json()["active"] \
        is False
    assert client.get(f"/b/{bid}/card").status_code == 404
    rows = client.get(f"/profiles/{pid}/beacons", headers=head).json()
    assert any(r["id"] == bid for r in rows), "deactivated, not deleted"


def test_a_rated_profile_is_placed_one_to_one(client):
    """Refused rather than silently downgraded: somebody who asked for a room
    and got private threads would not find out until the fortieth person was
    talking to themselves."""
    pid, head = _profile(client, "acct_rated", adult_mode=True,
                         plan="pro")
    r = client.post(f"/profiles/{pid}/beacons", headers=head,
                    json={"label": "the club", "mode": "room"})
    assert r.status_code == 422
    assert "one-to-one" in r.json()["detail"]


def test_the_scan_card_carries_the_mark_with_the_face(client):
    """An overlay cannot draw the portrait without also having been handed
    the disclosure to draw with it."""
    pid, head = _profile(client, "acct_scan")
    bid = client.post(f"/profiles/{pid}/beacons", headers=head,
                      json={"label": "the bench"}).json()["id"]
    card = client.get(f"/b/{bid}/card")
    assert card.status_code == 200
    body = card.json()
    assert body["age_wall"] is False
    assert body["watermark"], "the mark travels with the card"
    assert "portrait_marked" in body, (
        "a surface QRME does not control needs to know whether compositing "
        "is mandatory or merely additive")


def test_a_scan_counts(client):
    pid, head = _profile(client, "acct_count")
    bid = client.post(f"/profiles/{pid}/beacons", headers=head,
                      json={"label": "bench"}).json()["id"]
    client.get(f"/b/{bid}/card")
    client.get(f"/b/{bid}/card")
    rows = client.get(f"/profiles/{pid}/beacons", headers=head).json()
    assert [r for r in rows if r["id"] == bid][0]["scans"] == 2


# --- the overlay shape, and the two fields that were swapped ---------------

def test_the_overlay_answers_a_count_and_a_list(client):
    desk = _desk(client).json()
    d = desk["desk_id"]
    client.post(f"/desks/{d}/join", json={"mode": "audience"})
    overlay = client.get(f"/desks/{d}/overlay", headers=_token(desk)).json()

    assert isinstance(overlay["waiting"], int), (
        "waiting is a count; the console read `.length` off it")
    assert isinstance(overlay["comments"], list), (
        "comments is a list; the console rendered it as a number")
    assert isinstance(overlay["style"], dict), (
        "style is a layout object; the console printed it into a sentence")
    assert set(overlay["style"]) == {"opacity", "over_video", "anchor"}


# --- the console half -------------------------------------------------------

def _src(rel: str) -> str:
    return (REPO / rel).read_text(encoding="utf-8")


def _markup(rel: str) -> str:
    s = re.sub(r"/\*.*?\*/", "", _src(rel), flags=re.S)
    return re.sub(r"^\s*//.*$", "", s, flags=re.M)


def test_the_screen_calls_every_visitor_binding():
    src = _src("app/src/screens/Visiting.tsx")
    for binding in ("api.visitDesk(", "api.ringBell(", "api.joinDesk(",
                    "api.askToComeUp(", "api.profileBeacons(",
                    "api.placeBeacon(", "api.pickUpBeacon(",
                    "api.beaconCard("):
        assert binding in src, f"{binding} is still called by nothing"


def test_the_overlay_type_matches_the_wire():
    """The type is the thing that was wrong, so the type is what is pinned."""
    src = _src("app/src/api.ts")
    assert "waiting: number;" in src
    assert "comments: { who: string; said: string }[];" in src
    assert "style: { opacity: number; over_video: boolean; anchor: string };" \
        in src


def test_the_host_panel_reads_the_count_as_a_count():
    src = _markup("app/src/screens/Desk.tsx")
    assert "overlay.waiting.length" not in src, (
        "`waiting` is a number — `.length` on it printed `undefined waiting`")
    # The line moved into the l10n table when the screen was localized; the
    # count is still handed over as the number itself, never a `.length`.
    assert "waiting: overlay.waiting," in src
    assert "overlay.comments.length" in src, (
        "and `comments` is the list, so the count comes from its length")


def test_the_host_panel_renders_the_comments_rather_than_throwing():
    """Rendering the array directly is what would have thrown the moment
    anybody said anything on the stream."""
    src = _markup("app/src/screens/Desk.tsx")
    assert "overlay.comments.map" in src


def test_the_host_panel_reads_status_rather_than_state():
    """The guard was always true, so the buttons offered to accept people
    already accepted and decline people already declined."""
    src = _markup("app/src/screens/Desk.tsx")
    assert "g.state" not in src
    assert 'g.status !== "accepted" && g.status !== "declined"' in src


def test_the_screen_says_why_the_guest_route_needs_an_account():
    flat = " ".join(_markup("app/src/screens/Visiting.tsx").split())
    assert "Nothing is minted until you are somebody" in flat


def test_the_screen_draws_the_age_wall_without_the_name():
    """The wall must render from a body that never carried what it refuses."""
    src = _markup("app/src/screens/Visiting.tsx")
    assert "scanned.age_wall ?" in src
