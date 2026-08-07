"""The platform could do things to you and never tell you.

Every 0.42.x round built a way for one person to act on another — a
message sent, a comment left, a friendship extended, an exchange signed,
a place on a stream granted — and every one of them shared a silence:
the thing happened, and the person it happened to found out only by
going to look. Five surfaces, five separate places to check, none of
which say anything changed since last time.

    asked     can the platform do this to a person
    mattered  does the person ever hear about it

The inbox answers with three rules, each tested here because each is
the kind that erodes: it names the deed and never the words; your own
deeds never land in your own inbox; and a blocked comment produces no
event at all, because announcing a thing the recipient can never see
would be the filter advertising its own catch.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import clientpaths  # noqa: E402

REPO = Path(__file__).resolve().parent.parent

ADULT = {"birthdate": "1984-06-01"}


def _mk(client, name):
    r = client.post("/profiles", json={
        "owner_id": f"owner-{name}", "kind": "self", "display_name": name,
        "persona": "A person with a long history of doing things on time.",
        "verification": ADULT, "plan": "pro"})
    assert r.status_code == 201, r.text
    body = r.json()
    return body["id"], {"authorization": f"Bearer {body['owner_token']}"}


def test_a_friendship_extended_reaches_the_other_person(client):
    a, ha = _mk(client, "Ana")
    b, hb = _mk(client, "Ben")
    r = client.post(f"/profiles/{a}/friends", json={"friend_id": b},
                    headers=ha)
    assert r.status_code in (200, 201), r.text
    page = client.get(f"/profiles/{b}/inbox", headers=hb).json()
    kinds = [e["kind"] for e in page["events"]]
    assert "friend" in kinds
    assert page["unseen"] == 1
    # And the actor is named by display name, so the list reads as a list.
    ev = next(e for e in page["events"] if e["kind"] == "friend")
    assert ev["actor_name"] == "Ana"


def test_a_message_arrives_as_a_deed_and_not_as_words(client):
    a, ha = _mk(client, "Ana")
    b, hb = _mk(client, "Ben")
    client.post(f"/profiles/{a}/friends", json={"friend_id": b}, headers=ha)
    client.post(f"/profiles/{b}/friends", json={"friend_id": a}, headers=hb)
    r = client.post(f"/profiles/{a}/messages",
                    json={"to": b, "body": "the words themselves"},
                    headers=ha)
    assert r.status_code == 201, r.text
    page = client.get(f"/profiles/{b}/inbox", headers=hb).json()
    ev = next(e for e in page["events"] if e["kind"] == "message")
    # The deed, never the words: nothing in the event carries the body.
    assert "the words themselves" not in str(ev)


def test_your_own_deed_never_lands_in_your_own_inbox(client):
    a, ha = _mk(client, "Ana")
    b, hb = _mk(client, "Ben")
    client.post(f"/profiles/{a}/friends", json={"friend_id": b}, headers=ha)
    page = client.get(f"/profiles/{a}/inbox", headers=ha).json()
    # Ben has done nothing; Ana has acted once. Her inbox stays empty —
    # telling somebody what they just did is noise wearing the coat of news.
    assert page["events"] == []
    assert page["unseen"] == 0


def test_an_approved_comment_lands_and_a_blocked_one_does_not(client):
    a, ha = _mk(client, "Ana")
    b, hb = _mk(client, "Ben")
    r = client.post(f"/profiles/{b}/comments",
                    json={"body": "what a lovely garden"}, headers=ha)
    assert r.status_code == 201 and r.json()["status"] == "approved"
    r = client.post(f"/profiles/{b}/comments",
                    json={"body": "my ssn is 123-45-6789"}, headers=ha)
    assert r.status_code == 201 and r.json()["status"] == "blocked"
    kinds = [e["kind"] for e in
             client.get(f"/profiles/{b}/inbox", headers=hb).json()["events"]]
    # One comment event, not two: a blocked comment is invisible to
    # everyone but its author, and an inbox row announcing it would be
    # the filter advertising its own catch.
    assert kinds.count("comment") == 1


def test_a_signature_reaches_the_party_who_did_not_sign(client):
    a, ha = _mk(client, "Ana")
    b, hb = _mk(client, "Ben")
    ex = client.post("/exchanges", json={
        "host_id": a, "guest_id": b, "work": "a logo",
        "industry": "design"}, headers=ha).json()["id"]
    client.post(f"/exchanges/{ex}/items",
                json={"direction": "host_to_guest", "name": "draft",
                      "kind": "document"}, headers=ha)
    r = client.post(f"/exchanges/{ex}/sign", json={"actor_id": a},
                    headers=ha)
    assert r.status_code == 200, r.text
    kinds_b = [e["kind"] for e in
               client.get(f"/profiles/{b}/inbox", headers=hb).json()["events"]]
    assert "exchange_signed" in kinds_b
    # And the countersignature travels the other way.
    client.post(f"/exchanges/{ex}/sign", json={"actor_id": b}, headers=hb)
    kinds_a = [e["kind"] for e in
               client.get(f"/profiles/{a}/inbox", headers=ha).json()["events"]]
    assert "exchange_signed" in kinds_a


def test_a_place_on_a_stream_reaches_the_guest_and_a_decline_does_not(client):
    a, ha = _mk(client, "Ana")
    b, hb = _mk(client, "Ben")
    c, hc = _mk(client, "Cal")
    desk = client.post("/desks", json={
        "owner_id": a, "display_name": "Ana's desk", "trade": "design",
        "attestor": "owner-Ana", "basis": "long acquaintance"},
        headers=ha).json()
    hd = {"authorization": f"Bearer {desk['desk_token']}"}
    req_b = client.post(f"/desks/{desk['desk_id']}/guests",
                        json={"guest_id": b}, headers=hb).json()
    req_c = client.post(f"/desks/{desk['desk_id']}/guests",
                        json={"guest_id": c}, headers=hc).json()
    client.post(f"/desks/{desk['desk_id']}/guests/{req_b['id']}/accept",
                headers=hd)
    client.post(f"/desks/{desk['desk_id']}/guests/{req_c['id']}/decline",
                headers=hd)
    kinds_b = [e["kind"] for e in
               client.get(f"/profiles/{b}/inbox", headers=hb).json()["events"]]
    assert "guest_accepted" in kinds_b
    # The yes is an invitation to act; the no delivers nothing the person
    # can do anything with, so it stays out.
    page_c = client.get(f"/profiles/{c}/inbox", headers=hc).json()
    assert page_c["events"] == []


def test_looking_clears_the_count_and_keeps_the_record(client):
    a, ha = _mk(client, "Ana")
    b, hb = _mk(client, "Ben")
    client.post(f"/profiles/{a}/friends", json={"friend_id": b}, headers=ha)
    r = client.post(f"/profiles/{b}/inbox/seen", headers=hb)
    assert r.status_code == 200 and r.json()["marked_seen"] == 1
    page = client.get(f"/profiles/{b}/inbox", headers=hb).json()
    # A window, not a to-do list: the rows stay readable, only the count
    # goes to zero — and seeing twice is zero the second time.
    assert page["unseen"] == 0
    assert len(page["events"]) == 1 and page["events"][0]["seen"] is True
    assert client.post(f"/profiles/{b}/inbox/seen",
                       headers=hb).json()["marked_seen"] == 0


def test_the_inbox_is_the_owners_alone(client):
    a, ha = _mk(client, "Ana")
    b, hb = _mk(client, "Ben")
    assert client.get(f"/profiles/{b}/inbox").status_code == 401
    assert client.get(f"/profiles/{b}/inbox", headers=ha).status_code == 403
    assert client.post(f"/profiles/{b}/inbox/seen",
                       headers=ha).status_code == 403


def test_every_client_has_a_door_on_both_routes(client):
    """Console, iOS, Android, Windows — each reaches the window and the
    'I have looked'. A capability nobody is told about is reachable the
    way a doorless route is: technically."""
    from qrme.api import create_app
    app = create_app()
    for lang in (clientpaths.CONSOLE, *clientpaths.NATIVE):
        made = clientpaths.calls(lang)
        assert ("GET", "/profiles/x/inbox") in made, lang.name
        assert ("POST", "/profiles/x/inbox/seen") in made, lang.name


def test_the_deed_sentences_speak_ten_languages_on_every_shell(client):
    """Each shell composes the sentence from its own vocabulary — which is
    exactly what lets the check be a grep. Every inbox key, every kind in
    the backend's closed set, all ten languages, all three shells."""
    from qrme import inbox
    shells = {
        "ios": REPO / "native/ios/Sources/L10n.swift",
        "android": (REPO / "native/android/app/src/main/java/app/qrme/"
                           "studio/L10n.kt"),
        "windows": REPO / "native/windows/L10n.cs",
    }
    langs = ("es", "fr", "de", "pt", "it", "ja", "zh", "hi", "ar")
    for shell, path in shells.items():
        src = path.read_text(encoding="utf-8")
        for kind in inbox.KINDS:
            row = re.search(rf'"inbox\.kind\.{kind}"[^\n]*', src)
            assert row, f"{shell}: no sentence for the {kind} deed"
            for lang in langs:
                assert f'"{lang}"' in row.group(0), \
                    f"{shell}: inbox.kind.{kind} missing {lang}"
        for key in ("inbox.title", "inbox.new", "inbox.seen"):
            assert f'"{key}"' in src, f"{shell}: missing {key}"


def test_the_kinds_are_a_closed_set_and_note_refuses_a_stranger(client):
    """The vocabulary contract: every kind the backend records is one the
    shells can say, because a kind invented in passing would render as its
    raw identifier in ten languages at once."""
    from qrme import inbox
    import pytest
    with pytest.raises(inbox.InboxError):
        inbox.note("prf_x", "poked", "prf_y")
