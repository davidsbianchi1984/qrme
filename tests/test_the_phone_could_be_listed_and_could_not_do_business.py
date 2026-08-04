"""The phone could be found on the platform. It could not trade on it.

## The finding

Three blocks of the per-shell doorless record, read together, say one
thing. The caller's side of a desk shipped long ago — `DeskView` rings
the bell, joins the stream, opens a session — and no shell could ever
*staff* one: open a desk, set its presence, decide who comes through,
print the QR sticker that is its front door. `MarketSection` could put a
card up and could not search the market, price a listing, place it, sell
it or buy from it. And exchanges — two parties, one manifest, the
platform's whole apparatus for agreeing to work — existed on no shell at
all.

    asked     can a phone be found on the platform
    mattered  can a phone do business on it

Forty-six routes, forty-six rows in each of three records. The console
has had doors for all of them since the rounds that built them; the
grind is what carried the phones the rest of the way.

## The three rules the screens render rather than invent

1. **Presence is a closed set.** `attended`, `away`, `closed` — the
   refusal names all three, so a free text field would earn it on every
   typo. The screens offer the set.
2. **Both parties sign the same manifest, and any change clears both
   signatures.** Each item is accepted separately; nothing moves by
   itself. The vocabulary route states these rules and the screens show
   them, because a client that summarised them would be a fourth party
   to the agreement.
3. **A desk is a real person.** Opening one takes an attestor and a
   basis — somebody who vouches for the trade — and the form asks for
   both rather than letting the refusal do it.

## The guard gap this round also closed

`clientpaths.IOS` knew one call shape: paths handed to `request(...)`.
A route that answers **bytes** — the QR sticker, the still of a desk —
is not fetched that way: the shell builds a URL and an image view does
the GET. Two live doors read as absent.

This is the third time the same lesson has come round. Android's `URL(`
form is in the file for it, PDI's ported verb assumption was the second,
and this was the third.

    asked     does the shell call the transport helper for this route
    mattered  does the shell fetch this route at all
"""

from __future__ import annotations

import re
from pathlib import Path


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()
ADULT = {"birthdate": "1984-06-01"}


def _person(client, name, owner):
    r = client.post("/profiles", json={
        "owner_id": owner, "kind": "self", "display_name": name,
        "persona": "A person on the platform.", "verification": ADULT,
        "plan": "pro"})
    assert r.status_code == 201, r.text
    p = r.json()
    return p["id"], {"authorization": f"Bearer {p['owner_token']}"}


def _desk(client, pid, headers, name="Ana's bench"):
    made = client.post("/desks", json={
        "owner_id": pid, "display_name": name, "trade": "computer repair",
        "attestor": "City Licensing", "basis": "trade license",
        "location": "Austin", "blurb": "fix laptops"}, headers=headers)
    assert made.status_code == 201, made.text
    d = made.json()
    return d["desk_id"], {"authorization": f"Bearer {d['desk_token']}"}


# --- rule 1: presence is a closed set ----------------------------------------

def test_presence_is_a_closed_set_and_the_refusal_names_it(client):
    a, ha = _person(client, "Ana", "own-ana")
    desk, hd = _desk(client, a, ha)
    for presence in ("attended", "away", "closed"):
        r = client.put(f"/desks/{desk}/presence", json={"presence": presence},
                       headers=hd)
        assert r.status_code == 200, r.text
    r = client.put(f"/desks/{desk}/presence", json={"presence": "open"},
                   headers=hd)
    assert r.status_code == 422
    said = r.json()["detail"]
    for presence in ("attended", "away", "closed"):
        assert presence in said, (
            "the refusal stopped naming the whole set — the shells offer "
            f"exactly these three because it does: {said}")


# --- rule 2: a desk is a real person, vouched for -----------------------------

def test_opening_a_desk_takes_an_attestor_and_a_basis(client):
    a, ha = _person(client, "Ana", "own-ana")
    r = client.post("/desks", json={"owner_id": a, "display_name": "bench",
                                    "trade": "computer repair"}, headers=ha)
    assert r.status_code == 422
    missing = {row["loc"][-1] for row in r.json()["detail"]}
    assert {"attestor", "basis"} <= missing, (
        "a desk opened with nobody vouching for the trade — the form asks "
        "for both because the route requires both")


# --- the counter: staffing one, not knocking at one --------------------------

def test_the_bell_rings_through_to_the_person_behind_the_counter(client):
    a, ha = _person(client, "Ana", "own-ana")
    b, hb = _person(client, "Ben", "own-ben")
    desk, hd = _desk(client, a, ha)
    rung = client.post(f"/desks/{desk}/bell", json={"note": "knock"},
                       headers=hb)
    assert rung.status_code == 201, rung.text
    rings = client.get(f"/desks/{desk}/rings", headers=hd).json()["rings"]
    assert rings, "the bell rang and the counter's own list stayed empty"
    ring_id = rings[0]["id"]
    assert client.post(f"/desks/{desk}/rings/{ring_id}/ack",
                       headers=hd).status_code == 200


def test_who_comes_through_is_the_desks_decision(client):
    a, ha = _person(client, "Ana", "own-ana")
    b, hb = _person(client, "Ben", "own-ben")
    desk, hd = _desk(client, a, ha)
    asked = client.post(f"/desks/{desk}/guests", json={}, headers=hb)
    assert asked.status_code == 201, asked.text
    req = asked.json()["id"]
    assert asked.json()["status"] == "requested"
    waiting = client.get(f"/desks/{desk}/guests", headers=hd).json()["guests"]
    assert [g["id"] for g in waiting] == [req]
    let_in = client.post(f"/desks/{desk}/guests/{req}/accept", headers=hd)
    assert let_in.status_code == 201, let_in.text
    # And the caller's own way out is the caller's to press.
    assert client.delete(f"/desks/{desk}/guests/me",
                         headers=hb).status_code == 200


def test_the_sticker_is_the_desks_front_door(client):
    a, ha = _person(client, "Ana", "own-ana")
    desk, hd = _desk(client, a, ha)
    made = client.post(f"/desks/{desk}/beacons", json={"label": "front window"},
                       headers=hd)
    assert made.status_code == 201, made.text
    beacons = client.get(f"/desks/{desk}/beacons", headers=hd).json()["beacons"]
    assert beacons, "a sticker was made and the desk's list stayed empty"
    beacon = beacons[0]["id"]
    qr = client.get(f"/desk-beacons/{beacon}/qr.svg")
    assert qr.status_code == 200
    assert "svg" in qr.headers.get("content-type", ""), (
        "the sticker stopped being an image — the shells fetch it as one")
    assert client.delete(f"/desk-beacons/{beacon}",
                         headers=hd).status_code == 200


def test_the_still_of_a_desk_is_an_image(client):
    """The other byte-answering route, and the reason the iOS extractor
    needed a second call shape this round."""
    a, ha = _person(client, "Ana", "own-ana")
    desk, _ = _desk(client, a, ha)
    still = client.get(f"/desks/{desk}/view.webp")
    assert still.status_code == 200
    assert still.headers.get("content-type", "").startswith("image/")


# --- the market, from both sides ---------------------------------------------

def test_the_market_can_be_searched_and_says_what_it_searched(client):
    client.post("/marketplace/seed", json={})
    out = client.get("/marketplace/search", params={"q": "counseling"}).json()
    assert out["query"] == "counseling"
    assert "results" in out


def test_a_stand_goes_up_and_comes_down(client):
    a, ha = _person(client, "Ana", "own-ana")
    up = client.post(f"/profiles/{a}/marketplace",
                     json={"blurb": "I fix things", "locality": "Austin",
                           "tags": ["repair"]}, headers=ha)
    assert up.status_code == 201 and up.json()["listed"] is True
    down = client.delete(f"/profiles/{a}/marketplace", headers=ha)
    assert down.status_code in (200, 204)


def test_the_assist_suggests_and_does_not_search(client):
    """It hands back words for the search box. A client that treated them
    as results would show somebody a search nobody ran."""
    out = client.post("/marketplace/assist",
                      json={"need": "someone to fix a laptop"}).json()
    assert out["suggestions"], "the assist stopped suggesting anything"
    assert out.get("applied") is False, (
        "the assist now claims to have applied itself — the screens say it "
        "only suggests")


# --- exchanges: two parties, one manifest ------------------------------------

def test_the_vocabulary_states_the_rules_the_screens_show(client):
    out = client.get("/exchanges/vocabulary").json()
    assert out["industries"] and out["states"] and out["directions"]
    rules = " ".join(out["rules"]).lower()
    for claim in ("sign", "clears both", "separately"):
        assert claim in rules, (
            f"the vocabulary stopped stating {claim!r} — every shell renders "
            f"these rules verbatim: {out['rules']}")


def test_a_deal_is_proposed_and_carries_its_state(client):
    a, ha = _person(client, "Ana", "own-ana")
    b, _ = _person(client, "Ben", "own-ben")
    made = client.post("/exchanges", json={
        "host_id": a, "guest_id": b, "work": "a website",
        "industry": "software", "fee": 500.0}, headers=ha)
    assert made.status_code == 201, made.text
    deal = made.json()
    assert deal["state"], "a deal came back with no state to render"


# --- the shells --------------------------------------------------------------

SHELLS = {
    "ios": "native/ios/Sources/ApiClient.swift",
    "android": "native/android/app/src/main/java/app/qrme/studio/ApiClient.kt",
    "windows": "native/windows/ApiClient.cs",
}

#: One representative path per block per verb family. Checked as paths
#: rather than binding names, because the three shells name their
#: functions in three conventions and the route is what a person reaches.
PATHS = (
    "/desks",
    "/presence",
    "/rings",
    "/guests",
    "/beacons",
    "/desk-beacons/",
    "qr.svg",
    "view.webp",
    "/overlay",
    "/live-person",
    "/marketplace/search",
    "/marketplace/localities",
    "/marketplace/assist",
    "/marketplace/sales",
    "/marketplace/settings/",
    "/offer",
    "/place",
    "/purchase",
    "/exchanges/vocabulary",
    "/exchanges",
    "/items",
    "/sign",
    "/reopen",
    "/withdraw",
    "/channel",
    "/parties/",
)


def test_every_shell_reaches_every_block():
    missing = []
    for shell, path in SHELLS.items():
        src = (REPO / path).read_text(encoding="utf-8")
        for wanted in PATHS:
            if wanted not in src:
                missing.append(f"{shell}: {wanted}")
    assert not missing, (
        "these routes never reached a shell:\n    " + "\n    ".join(missing))


def test_the_closed_set_is_closed_on_every_shell():
    """Rule 1 is a client-side rendering decision, so it is checked on the
    clients: each shell offers the three presences rather than a free
    field that earns the refusal."""
    for shell, view in (
            ("ios", "native/ios/Sources/Views/CounterView.swift"),
            ("android",
             "native/android/app/src/main/java/app/qrme/studio/ui/Screens.kt"),
            ("windows", "native/windows/Views/CounterPage.xaml.cs")):
        src = (REPO / view).read_text(encoding="utf-8")
        assert re.search(r'"attended",\s*"away",\s*"closed"', src), (
            f"{shell} no longer offers the closed set of presences — a free "
            "field earns the refusal on every typo")


def test_the_signing_rules_are_shown_not_summarised():
    """Rule 2: the shells render the vocabulary's own `rules` list. A
    client that wrote its own sentence would be a fourth party to an
    agreement between two."""
    for shell, view in (
            ("ios", "native/ios/Sources/Views/CounterView.swift"),
            ("android",
             "native/android/app/src/main/java/app/qrme/studio/ui/Screens.kt"),
            ("windows", "native/windows/Views/CounterPage.xaml.cs")):
        src = (REPO / view).read_text(encoding="utf-8")
        assert "rules" in src.lower(), (
            f"{shell} stopped showing the vocabulary's rules")


def test_the_shells_say_it_in_ten_languages():
    tables = {
        "ios": "native/ios/Sources/L10n.swift",
        "android": "native/android/app/src/main/java/app/qrme/studio/L10n.kt",
        "windows": "native/windows/L10n.cs",
    }
    langs = ("es", "fr", "de", "pt", "it", "ja", "zh", "hi", "ar")
    keys = ("counter.open", "counter.attested", "counter.sticker.note",
            "counter.presence.attended", "trade.find", "trade.price",
            "deals.propose", "deals.sign.note")
    for shell, path in tables.items():
        src = (REPO / path).read_text(encoding="utf-8")
        for key in keys:
            row = next((line for line in src.splitlines() if key in line),
                       None)
            assert row, f"{shell} has no row for {key}"
            for lang in langs:
                assert f'"{lang}"' in row, (
                    f"{shell}'s {key} has no {lang} translation")


def test_the_extractor_knows_the_image_door_shape():
    """The guard-gap half. A route answering bytes is fetched by an image
    view, not the JSON helper; the Swift rule knew only `request(`."""
    src = (REPO / "tests/clientpaths.py").read_text(encoding="utf-8")
    ios = src[src.index("IOS = Language("):src.index("ANDROID = Language(")]
    # The *rule*, not the word: the first draft of this assertion looked for
    # the name anywhere in the block and passed against an injection that
    # deleted the CallForm and left the comment explaining it. A comment is
    # not a rule.
    assert re.search(r"CallForm\([^)]*appendingPathComponent", ios), (
        "the Swift extractor is back to one call shape — the QR sticker and "
        "the desk still are live doors it cannot see")
