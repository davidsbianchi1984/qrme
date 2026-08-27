"""The crowd, the couch and the loan — the phones get the quiet half.

Three blocks of the per-shell doorless record, read together: the phone
could be liked and could not like anybody (nine audience routes), could
be invited to a watch party the console started and could not start,
seek, or speak in one (ten routes), and could neither lend a skill nor
borrow one (ten routes).

    asked     is the surface built
    mattered  can somebody holding a phone stand in the crowd

Twenty-nine routes gain doors on iOS, Android and Windows in one cut,
and the rules each block renders are the backend's, not the shell's:
the numbers under the buttons come from one call; seek moves a number
and presses play on nobody's device; a synthetic party guest carries
the sentence that it has not seen the footage; a grant's terms are the
vocabulary's own sentences, verbatim; and a gift is a gift — refused
without a verified adult, irreversible by design.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import clientpaths  # noqa: E402
from . import ratchets, shelltables

REPO = Path(__file__).resolve().parent.parent

ADULT = {"birthdate": "1984-06-01"}
VIDEO = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


def _mk(client, name):
    r = client.post("/profiles", json={
        "owner_id": f"owner-{name}", "kind": "self", "display_name": name,
        "persona": "A person who shows up on time and stays to the end.",
        "verification": ADULT, "plan": "pro"})
    assert r.status_code == 201, r.text
    body = r.json()
    return body["id"], {"authorization": f"Bearer {body['owner_token']}"}


def test_the_numbers_under_the_buttons_come_from_one_call(client):
    a, ha = _mk(client, "Ana")
    b, hb = _mk(client, "Ben")
    r = client.post(f"/profiles/{b}/like", headers=ha)
    assert r.status_code == 201, r.text
    counts = client.get(f"/profiles/{b}/audience", headers=ha).json()
    assert counts["likes"] == 1 and counts["you_liked"] is True
    r = client.delete(f"/profiles/{b}/like", headers=ha)
    assert r.status_code == 200
    assert client.get(f"/profiles/{b}/audience",
                      headers=ha).json()["likes"] == 0


def test_a_share_hands_back_a_link_and_a_follow_is_listed(client):
    a, ha = _mk(client, "Ana")
    b, hb = _mk(client, "Ben")
    r = client.post(f"/profiles/{b}/share", json={"channel": "link"},
                    headers=ha)
    assert r.status_code == 201 and r.json().get("url"), r.text
    r = client.post(f"/profiles/{b}/subscribe", json={"tier": "follow"},
                    headers=ha)
    assert r.status_code == 201, r.text
    subs = client.get(f"/profiles/{b}/subscribers", headers=hb).json()
    assert len(subs["subscribers"]) == 1
    r = client.delete(f"/profiles/{b}/subscribe", headers=ha)
    assert r.status_code == 200
    assert client.get(f"/profiles/{b}/subscribers",
                      headers=hb).json()["subscribers"] == []


def test_a_gift_needs_a_verified_adult_and_says_it_cannot_be_reversed(client):
    a, ha = _mk(client, "Ana")
    b, hb = _mk(client, "Ben")
    # An owner token is not an age: the giver has to be a verified adult
    # interactor, and the refusal says so rather than failing vaguely.
    r = client.post(f"/profiles/{b}/gift", json={"amount": 5.0, "note": "!"},
                    headers=ha)
    assert r.status_code == 403, r.text
    sam = client.post("/interactors", json={
        "display_name": "Sam", "birthdate": "1990-01-15"}).json()
    hs = {"authorization": f"Bearer {sam['token']}"}
    r = client.post(f"/profiles/{b}/gift", json={"amount": 5.0,
                    "note": "for the garden"}, headers=hs)
    assert r.status_code == 201, r.text
    jar = client.get(f"/profiles/{b}/gifts", headers=hb).json()
    assert jar["total_amount"] == 5.0 and len(jar["gifts"]) == 1


def _party(client):
    a, ha = _mk(client, "Ana")
    b, hb = _mk(client, "Ben")
    post = client.post(f"/profiles/{a}/wall",
                       json={"body": f"movie night {VIDEO}"},
                       headers=ha).json()
    assert post["video"], post
    party = client.post("/watch-parties", json={
        "post_id": post["id"], "host_id": a, "title": "premiere"},
        headers=ha).json()
    return a, ha, b, hb, party


def test_the_couch_seats_a_guest_and_the_host_holds_the_remote(client):
    a, ha, b, hb, party = _party(client)
    pid = party["id"]
    r = client.post(f"/watch-parties/{pid}/members",
                    json={"member_id": b, "kind": "person"}, headers=hb)
    assert r.status_code == 201, r.text
    # Seek is the host's: the guest holding the remote is refused by
    # token, not by honor system.
    r = client.post(f"/watch-parties/{pid}/seek",
                    json={"host_id": b, "position_s": 30}, headers=hb)
    assert r.status_code in (403, 422), r.text
    r = client.post(f"/watch-parties/{pid}/seek",
                    json={"host_id": a, "position_s": 30, "playing": True},
                    headers=ha)
    assert r.status_code == 200 and r.json()["position_s"] == 30
    r = client.post(f"/watch-parties/{pid}/chat",
                    json={"member_id": b, "body": "great scene"}, headers=hb)
    assert r.status_code == 201
    lines = client.get(f"/watch-parties/{pid}/chat", headers=hb).json()
    assert any(l["body"] == "great scene" for l in lines["lines"])
    r = client.post(f"/watch-parties/{pid}/end", headers=ha)
    assert r.status_code == 200


def test_a_synthetic_guest_is_told_it_has_not_seen_the_footage(client):
    a, ha, b, hb, party = _party(client)
    ctx = client.get(f"/watch-parties/{party['id']}/context",
                     headers=ha).json()
    # The most ordinary-looking lie this product could tell is a model's
    # plausible opinion about footage nobody showed it. The context says
    # so out loud, and the shells render the sentence verbatim.
    assert ctx.get("you_have_not_seen_it"), ctx


def test_a_skill_is_lent_used_written_down_and_ends_when_closed(client):
    a, ha = _mk(client, "Ana")
    b, hb = _mk(client, "Ben")
    vocab = client.get("/skill-grants/vocabulary").json()
    assert any("never copied" in t for t in vocab["ground_rules"])
    surface = vocab["surfaces"][0]["key"]
    kind = vocab["skill_kinds"][0]["key"]
    grant = client.post("/skill-grants", json={
        "lender_id": a, "borrower_id": b, "surface": surface,
        "surface_id": "room-1", "skill_kind": kind, "skill_ref": "sk-1",
        "title": "cold reads"}, headers=ha).json()
    gid = grant["id"]
    # Nothing usable until the second consent.
    r = client.post(f"/skill-grants/{gid}/use",
                    json={"borrower_id": b}, headers=hb)
    assert r.status_code == 422, r.text
    client.post(f"/skill-grants/{gid}/accept", json={"actor_id": b},
                headers=hb)
    r = client.post(f"/skill-grants/{gid}/use",
                    json={"borrower_id": b, "what": "opening line"},
                    headers=hb)
    assert r.status_code == 201, r.text
    uses = client.get(f"/skill-grants/{gid}/uses", headers=ha).json()
    assert len(uses["uses"]) == 1
    mine = client.get(f"/people/{a}/skill-grants", headers=ha).json()
    assert len(mine["lending"]) == 1
    listed = client.get(f"/surfaces/{surface}/room-1/skill-grants",
                        headers=ha).json()
    assert len(listed["grants"]) == 1
    # Either side alone closes it, and the next call stops.
    client.post(f"/skill-grants/{gid}/close", json={"actor_id": a},
                headers=ha)
    r = client.post(f"/skill-grants/{gid}/use",
                    json={"borrower_id": b, "what": "again"}, headers=hb)
    assert r.status_code == 422, r.text


def test_every_shell_has_doors_on_all_three_blocks(client):
    """One representative door per block per shell, by method and path —
    the ratchet counts the rest."""
    for lang in clientpaths.NATIVE:
        made = clientpaths.calls(lang)
        assert ("POST", "/x/x/like") in made, f"{lang.name}: no like door"
        assert ("POST", "/watch-parties") in made, \
            f"{lang.name}: no party door"
        assert ("POST", "/skill-grants") in made, \
            f"{lang.name}: no grant door"
        assert ("GET", "/skill-grants/vocabulary") in made, \
            f"{lang.name}: the terms are not readable"


def test_the_crowd_speaks_ten_languages_on_every_shell(client):
    """Every key, not a sample. The first draft spot-checked eight keys
    and an injection walked straight past it: a row outside the sample
    lost a language and the test stayed green. So the key list is read
    off the iOS table and required, complete, on all three shells — which
    also catches a key present on one shell and absent on another."""
    keys = shelltables.ios_keys("crowd")
    assert len(keys) >= ratchets.floor("l10n.block.crowd"), \
        f"the iOS table lost rows: {len(keys)}"
    problems = shelltables.missing_rows(keys)
    assert not problems, (
        f"{len(problems)} gap(s) in the shell tables:\n    "
        + "\n    ".join(problems[:12]))


def test_the_seek_field_earned_its_label(client):
    """`position_s` left the unmapped residue this round because a form
    now asks a person for it — the evidence rule, applied in the one
    direction it allows."""
    from qrme import i18n
    said = i18n.field_label("position_s", "de")
    assert said == "Position, in Sekunden"
    residue = (REPO / "tests/field_labels_unmapped.txt").read_text()
    assert "\nposition_s\n" not in residue
