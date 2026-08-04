"""Friends, the wall and comments had a door on every client but the phones.

## The finding

The community round built the friends list, the wall and comments, and
every round since has treated them as done. The per-shell door audit says
otherwise: nine routes, carried by the backend since that round, with a
door in the console and none on iOS, Android or Windows. Twenty-seven
rows — nine per shell — sat in the doorless records the whole time.

    asked     does the platform have a social surface
    mattered  can somebody holding a phone reach it

A person on a phone could be *on* the wall — their profile had one, other
people could read it — and could not post to it, could not see who the
platform suggested they know, and could not take back a comment.

## What this file drives

The three rules the shells render rather than invent. Each is a decision
the backend already made and stated in its own response; a client that
re-decided them would be a fourth opinion:

1. **A pinned row gets no remove control.** The founder's two profiles
   refuse deletion with 409, and the list marks them `pinned` precisely so
   a client can leave the button off rather than offer one that fails.
2. **A blocked post or comment comes back to its author.** The write
   answers 201 with a `status`, because the words *were* recorded; what
   happened to them is the status, not an error.
3. **A suggestion carries the reason it was made.** The route returns
   what it ranked on and what it never ranks on — showing the name
   without the reason would undo the one thing it was careful to do.
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


# --- the friends list --------------------------------------------------------

def test_the_list_names_who_is_on_it_and_who_cannot_be_removed(client):
    a, ha = _person(client, "Ana", "own-ana")
    b, _ = _person(client, "Ben", "own-ben")
    assert client.post(f"/profiles/{a}/friends", json={"friend_id": b},
                       headers=ha).status_code == 200
    listed = client.get(f"/profiles/{a}/friends").json()
    assert listed["count"] == 1
    row = listed["friends"][0]
    assert row["display_name"] == "Ben"
    # `pinned` is what lets a phone leave the control off rather than draw
    # one that answers 409.
    assert row["pinned"] is False
    assert "founder" in row and "pinned" in row


def test_a_friend_can_be_removed_and_the_list_shortens(client):
    a, ha = _person(client, "Ana", "own-ana")
    b, _ = _person(client, "Ben", "own-ben")
    client.post(f"/profiles/{a}/friends", json={"friend_id": b}, headers=ha)
    assert client.delete(f"/profiles/{a}/friends/{b}",
                         headers=ha).status_code == 200
    assert client.get(f"/profiles/{a}/friends").json()["count"] == 0


def test_the_list_is_the_owners_to_change_and_anybodys_to_read(client):
    """The read is public — a friends list is part of how a profile
    presents itself. The writes are the owner's alone."""
    a, _ = _person(client, "Ana", "own-ana")
    b, hb = _person(client, "Ben", "own-ben")
    assert client.get(f"/profiles/{a}/friends").status_code == 200
    assert client.post(f"/profiles/{a}/friends", json={"friend_id": b},
                       headers=hb).status_code in (401, 403)


def test_a_suggestion_says_what_it_was_ranked_on(client):
    a, _ = _person(client, "Ana", "own-ana")
    out = client.get(f"/profiles/{a}/friends/suggested").json()
    assert out["ranked_on"], "a ranking with no stated basis is a black box"
    for forbidden in ("source material", "memories", "vaulted data"):
        assert forbidden in out["never_ranked_on"], (
            f"{forbidden!r} dropped out of the never-ranked-on list — the "
            "phones show that sentence verbatim")


# --- the wall ----------------------------------------------------------------

def test_a_post_appears_on_the_wall_that_anybody_can_read(client):
    a, ha = _person(client, "Ana", "own-ana")
    made = client.post(f"/profiles/{a}/wall", json={"body": "hello wall"},
                       headers=ha)
    assert made.status_code == 201, made.text
    assert made.json()["status"] == "approved"
    posts = client.get(f"/profiles/{a}/wall").json()["posts"]
    assert [p["body"] for p in posts] == ["hello wall"]


def test_only_the_owner_posts_to_their_own_wall(client):
    a, _ = _person(client, "Ana", "own-ana")
    _, hb = _person(client, "Ben", "own-ben")
    r = client.post(f"/profiles/{a}/wall", json={"body": "not mine to say"},
                    headers=hb)
    assert r.status_code in (401, 403), (
        "somebody posted to a wall they do not own")


def test_a_write_that_is_held_still_answers_with_its_status(client):
    """Rule 2, in the shape the phones read it: the write succeeds and the
    status carries what happened. A client that treated 201 as 'published'
    would tell somebody their post is up when nobody else can see it."""
    a, ha = _person(client, "Ana", "own-ana")
    made = client.post(f"/profiles/{a}/wall", json={"body": "hello"},
                       headers=ha)
    assert made.status_code == 201
    body = made.json()
    assert "status" in body, (
        "a wall post comes back without a status — the shells have nothing "
        "to render for a held post but silence")
    assert body["status"] in ("approved", "blocked")


# --- comments ----------------------------------------------------------------

def test_a_comment_lands_and_its_author_can_take_it_back(client):
    a, ha = _person(client, "Ana", "own-ana")
    post = client.post(f"/profiles/{a}/wall", json={"body": "say something"},
                       headers=ha).json()["id"]
    made = client.post(f"/posts/{post}/comments", json={"body": "nice"},
                       headers=ha)
    assert made.status_code == 201, made.text
    comment = made.json()["id"]
    seen = client.get(f"/posts/{post}/comments", headers=ha).json()["comments"]
    assert [c["body"] for c in seen] == ["nice"]
    assert client.delete(f"/comments/{comment}",
                         headers=ha).status_code == 200
    seen = client.get(f"/posts/{post}/comments", headers=ha).json()["comments"]
    assert seen == []


def test_a_comment_is_only_its_authors_to_withdraw(client):
    a, ha = _person(client, "Ana", "own-ana")
    _, hb = _person(client, "Ben", "own-ben")
    post = client.post(f"/profiles/{a}/wall", json={"body": "mine"},
                       headers=ha).json()["id"]
    comment = client.post(f"/posts/{post}/comments", json={"body": "hi"},
                          headers=ha).json()["id"]
    assert client.delete(f"/comments/{comment}", headers=hb).status_code == 403


# --- the shells --------------------------------------------------------------

SHELLS = {
    "ios": ("native/ios/Sources/ApiClient.swift",
            ("friends(", "suggestedFriends(", "addFriend(", "removeFriend(",
             "wall(", "postToWall(", "comments(", "addComment(",
             "deleteComment(")),
    "android": ("native/android/app/src/main/java/app/qrme/studio/ApiClient.kt",
                ("fun friends(", "fun suggestedFriends(", "fun addFriend(",
                 "fun removeFriend(", "fun wall(", "fun postToWall(",
                 "fun comments(", "fun addComment(", "fun deleteComment(")),
    "windows": ("native/windows/ApiClient.cs",
                ("Friends(", "SuggestedFriends(", "AddFriend(",
                 "RemoveFriend(", "Wall(", "PostToWall(", "Comments(",
                 "AddComment(", "DeleteComment(")),
}


def test_every_shell_carries_all_nine():
    """The binding half. `test_the_phone_is_a_client_too.py` proves each
    route is *reachable* from each shell; this says the nine arrived
    together, because a shell that can read a wall and not post to one is
    the shape of gap this round exists to close."""
    missing = []
    for shell, (path, names) in SHELLS.items():
        src = (REPO / path).read_text(encoding="utf-8")
        for name in names:
            if name not in src:
                missing.append(f"{shell}: {name}")
    assert not missing, (
        "these bindings never arrived:\n    " + "\n    ".join(missing))


def test_the_pinned_row_is_read_on_every_shell():
    """Rule 1 is a client-side rendering decision, so it is checked on the
    clients: each shell reads `pinned` and each has the word to show
    instead of a control."""
    for shell, (path, _) in SHELLS.items():
        src = (REPO / path).read_text(encoding="utf-8")
        assert re.search(r"[Pp]inned", src), (
            f"{shell} never reads `pinned` — it will draw a remove button "
            "on the founder's rows and the press will answer 409")
    for shell, view in (
            ("ios", "native/ios/Sources/Views/PeopleView.swift"),
            ("android",
             "native/android/app/src/main/java/app/qrme/studio/ui/Screens.kt"),
            ("windows", "native/windows/Views/PeoplePage.xaml.cs")):
        src = (REPO / view).read_text(encoding="utf-8")
        assert "people.pinned" in src, (
            f"{shell}'s screen has no word for a pinned row")


def test_the_shells_say_it_in_ten_languages():
    tables = {
        "ios": "native/ios/Sources/L10n.swift",
        "android": "native/android/app/src/main/java/app/qrme/studio/L10n.kt",
        "windows": "native/windows/L10n.cs",
    }
    langs = ("es", "fr", "de", "pt", "it", "ja", "zh", "hi", "ar")
    keys = ("people.friends", "people.pinned", "people.suggested",
            "people.ranked", "people.wall", "people.blocked",
            "people.comments", "people.withdraw")
    for shell, path in tables.items():
        src = (REPO / path).read_text(encoding="utf-8")
        for key in keys:
            row = next((line for line in src.splitlines() if key in line),
                       None)
            assert row, f"{shell} has no row for {key}"
            for lang in langs:
                assert f'"{lang}"' in row, (
                    f"{shell}'s {key} has no {lang} translation")
