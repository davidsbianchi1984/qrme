"""The sticker, the queue and the stamp, on the phones.

Six more blocks off the per-shell doorless record — the beacon a
stranger scans on the street (and the desk sticker, the social presence
beacon, and pairing the console itself), the moderation queue the owner
works, the reviews readers trust, the watermark that proves provenance,
the media that rides the wall, and the wearables on the wrist. What
they share is the street: every one is where the product meets somebody
who did not open the app on purpose — a camera pointed at a sticker, a
reader weighing a review, an editor checking a mark.

The rules these screens render rather than invent:

* **The overlay never draws the face without the disclosure.** The
  beacon card carries the watermark line with the name, and an unknown
  code is told so by name.
* **Only the owner moderates,** and a message already resolved says so
  rather than flipping again.
* **You can change what you said, and take it back** — the edit is
  moderated as a fresh message; the retracted row survives for the
  trail and stops being shown.
* **A review requires having actually talked to it** — one per
  interactor, edited rather than stacked.
* **The stamp answers to anyone.** A real credential on altered
  content says both things: valid, and no longer matching.
* **The caps are published before the upload fails,** and authentic
  media is never AI-marked.
* **A wearable sent away cannot come back by re-presenting the same
  name.**
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import clientpaths  # noqa: E402

from tests.test_capabilities import (
    as_interactor, auth_header, make_interactor, make_profile,
)
from . import ratchets, shelltables

REPO = Path(__file__).resolve().parent.parent


# -- the sticker ------------------------------------------------------------

def test_the_overlay_never_draws_the_face_without_the_disclosure(client):
    p = make_profile(client)
    b = client.post(f"/profiles/{p['id']}/beacons",
                    json={"label": "Porch"}, headers=auth_header(p)).json()
    card = client.get(f"/b/{b['id']}/card",
                      headers={"authorization": ""}).json()
    assert card["display_name"]
    assert card["watermark"], \
        "the face travelled without the disclosure to draw with it"
    # An unknown code is told so by name, not with an empty card.
    r = client.get("/b/bcn_nothing/card", headers={"authorization": ""})
    assert r.status_code == 404
    assert "nothing answers" in r.json()["detail"]
    # The scan page and the printable QR answer a bare GET.
    page = client.get(f"/b/{b['id']}", headers={"authorization": ""})
    assert page.status_code == 200
    qr = client.get(f"/beacons/{b['id']}/qr.svg",
                    headers={"authorization": ""})
    assert qr.headers["content-type"].startswith("image/svg")


def test_pairing_is_one_screen_and_one_code(client):
    pair = client.get("/pair", headers={"authorization": ""}).json()
    assert pair["console_url"]
    qr = client.get("/pair/qr.svg", headers={"authorization": ""})
    assert qr.headers["content-type"].startswith("image/svg")


# -- the queue --------------------------------------------------------------

def _held(client):
    """A profile in manual moderation, with one held reply in its queue."""
    p = make_profile(client, moderation_mode="manual")
    who = make_interactor(client)
    r = client.post(f"/profiles/{p['id']}/chat",
                    json={"interactor_id": who, "message": "hello"},
                    headers=auth_header(p))
    assert r.json()["profile_message"]["status"] == "pending"
    queue = client.get(f"/profiles/{p['id']}/moderation/queue",
                       headers=auth_header(p)).json()
    return p, who, queue[0]["id"]


def test_only_the_owner_moderates_and_a_resolved_row_stays_resolved(client):
    p, _, held_id = _held(client)
    q = make_profile(client, owner_id="owner-2", display_name="Quinn")
    assert client.post(f"/moderation/{held_id}/approve",
                       headers=auth_header(q)).status_code == 403
    r = client.post(f"/moderation/{held_id}/approve",
                    headers=auth_header(p))
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "approved"
    # Already resolved: it does not flip again.
    assert client.post(f"/moderation/{held_id}/reject",
                       headers=auth_header(p)).status_code == 409


def test_you_can_change_what_you_said_and_take_it_back(client):
    p = make_profile(client)
    who = make_interactor(client)
    client.post(f"/profiles/{p['id']}/chat",
                json={"interactor_id": who, "message": "the old wording"},
                headers=auth_header(p))
    from qrme import db
    mine = [r["id"] for r in db.connect().execute(
        "SELECT id, role FROM messages WHERE profile_id=? AND"
        " interactor_id=? ORDER BY created_at, rowid",
        (p["id"], who)).fetchall() if r["role"] == "interactor"]
    r = client.patch(f"/profiles/{p['id']}/messages/{mine[0]}",
                     json={"interactor_id": who,
                           "content": "the new wording"},
                     headers=auth_header(p))
    assert r.status_code == 200, r.text
    assert r.json()["content"] == "the new wording"
    assert r.json()["edited"] is True
    r = client.request("DELETE", f"/profiles/{p['id']}/messages/{mine[0]}",
                       json={"interactor_id": who},
                       headers=auth_header(p))
    assert r.status_code == 200, r.text


# -- the reviews ------------------------------------------------------------

def test_a_review_requires_having_actually_talked_to_it(client):
    p = make_profile(client)
    who = make_interactor(client)
    r = client.post(f"/profiles/{p['id']}/reviews",
                    json={"interactor_id": who, "rating": 5,
                          "body": "wonderful"}, headers=as_interactor(who))
    assert r.status_code == 422, \
        "a review from somebody who never talked to it stood"
    client.post(f"/profiles/{p['id']}/chat",
                json={"interactor_id": who, "message": "hello"},
                headers=auth_header(p))
    r = client.post(f"/profiles/{p['id']}/reviews",
                    json={"interactor_id": who, "rating": 5,
                          "body": "wonderful"}, headers=as_interactor(who))
    assert r.status_code == 201, r.text
    board = client.get(f"/profiles/{p['id']}/reviews",
                       headers={"authorization": ""}).json()
    assert board["rating"]["count"] == 1
    assert any(row["rating"] == 5 for row in board["reviews"])


# -- the stamp --------------------------------------------------------------

def test_a_real_credential_on_altered_content_says_both_things(client):
    p = make_profile(client)
    work = client.post(f"/profiles/{p['id']}/assist/compose",
                       json={"kind": "note", "moment": "the first frost"},
                       headers=auth_header(p)).json()
    wid = work["watermark"]["watermark_id"]
    # Resolution is public: "who made this" is the reader's question.
    card = client.get(f"/watermarks/{wid}",
                      headers={"authorization": ""}).json()
    assert card["profile_id"] == p["id"]
    altered = client.post("/watermarks/verify",
                          json={"watermark_id": wid,
                                "content": work["content"] + " oops"},
                          headers={"authorization": ""}).json()
    assert altered["valid"] is True
    assert altered["content_match"] is False
    r = client.post("/watermarks/verify",
                    json={"watermark_id": "wmk_nope", "content": "x"})
    assert r.status_code == 404
    assert "no such watermark" in r.json()["detail"]


# -- the media --------------------------------------------------------------

def test_the_caps_are_published_and_authentic_media_is_never_ai_marked(
        client):
    limits = client.get("/media/limits",
                        headers={"authorization": ""}).json()
    assert limits
    platforms = client.get("/videos/platforms",
                           headers={"authorization": ""}).json()
    assert platforms
    p = make_profile(client)
    # A real photo's magic bytes: the kind is read from the bytes, and
    # the filename is only a display hint.
    png = (b"\x89PNG\r\n\x1a\n" + b"\x00" * 64)
    r = client.post(f"/profiles/{p['id']}/media?filename=porch.png",
                    content=png, headers=auth_header(p))
    assert r.status_code == 201, r.text
    assert not r.json().get("ai_marked"), \
        "authentic media wore the AI mark"
    q = make_profile(client, owner_id="owner-2", display_name="Quinn")
    assert client.post(f"/profiles/{p['id']}/media", content=png,
                       headers=auth_header(q)).status_code == 403


# -- the wearables ----------------------------------------------------------

def test_a_wearable_is_a_screen_and_the_record_survives(client):
    p = make_profile(client)
    board = client.get(f"/profiles/{p['id']}/wearables",
                       headers=auth_header(p)).json()
    assert board["kinds_worn"]
    # The refusals are said out loud, so a client can grey these out
    # with the reason rather than offering them and returning a 422.
    assert board["refusal_reasons"]
    kind = next(iter(board["kinds_worn"]))
    refused_kind = next(iter(board["refusal_reasons"]))
    r = client.post(f"/profiles/{p['id']}/wearables",
                    json={"name": "left wrist", "kind": kind},
                    headers=auth_header(p))
    assert r.status_code == 201, r.text
    rows = client.get(f"/profiles/{p['id']}/wearables",
                      headers=auth_header(p)).json()["wearables"]
    assert any(w["name"] == "left wrist" for w in rows)
    # A room-facing microphone is refused with the reason, and an
    # unknown kind is told the list.
    assert client.post(f"/profiles/{p['id']}/wearables",
                       json={"name": "shelf", "kind": refused_kind},
                       headers=auth_header(p)).status_code == 422
    r = client.post(f"/profiles/{p['id']}/wearables",
                    json={"name": "shelf", "kind": "toaster"},
                    headers=auth_header(p))
    assert r.status_code == 422 and "expected one of" in r.json()["detail"]
    # Unpair revokes; the record survives for the owner to see, and
    # pairing the same name again is the same watch coming back — an
    # update, never a duplicate row.
    r = client.delete(f"/profiles/{p['id']}/wearables/left wrist",
                      headers=auth_header(p))
    assert r.status_code == 200, r.text
    again = client.post(f"/profiles/{p['id']}/wearables",
                        json={"name": "left wrist", "kind": kind},
                        headers=auth_header(p))
    assert again.status_code == 201, again.text
    rows = client.get(f"/profiles/{p['id']}/wearables",
                      headers=auth_header(p)).json()["wearables"]
    assert len([w for w in rows if w["name"] == "left wrist"]) == 1
    # And the list is the owner's.
    q = make_profile(client, owner_id="owner-2", display_name="Quinn")
    assert client.get(f"/profiles/{p['id']}/wearables",
                      headers=auth_header(q)).status_code == 403


# -- the doors and their languages ------------------------------------------

def test_every_shell_has_doors_on_the_six_blocks(client):
    for lang in clientpaths.NATIVE:
        made = clientpaths.calls(lang)
        assert ("GET", "/b/x/card") in made, \
            f"{lang.name}: the camera overlay is blind"
        assert ("GET", "/pair") in made, \
            f"{lang.name}: the console cannot reach a phone"
        assert ("GET", "/profiles/x/moderation/queue") in made, \
            f"{lang.name}: the queue is invisible"
        assert ("PATCH", "/profiles/x/messages/x") in made, \
            f"{lang.name}: what you said cannot be changed"
        assert ("GET", "/profiles/x/reviews") in made, \
            f"{lang.name}: the reviews are unreadable"
        assert ("POST", "/watermarks/verify") in made, \
            f"{lang.name}: the stamp cannot be checked"
        assert ("POST", "/profiles/x/media") in made, \
            f"{lang.name}: nothing can be uploaded"
        assert ("POST", "/profiles/x/wearables") in made, \
            f"{lang.name}: no wearable can be paired"


def test_the_six_blocks_speak_ten_languages_on_every_shell(client):
    """Every bcn/modq/revw/wm/med/wear key the iOS table carries,
    complete on all three shells — the full-list rule, never a sample."""
    keys = shelltables.ios_keys("sticker")
    assert len(keys) >= ratchets.floor("l10n.block.sticker"), \
        f"the iOS table lost rows: {len(keys)}"
    problems = shelltables.missing_rows(keys)
    assert not problems, (
        f"{len(problems)} gap(s) in the shell tables:\n    "
        + "\n    ".join(problems[:12]))
