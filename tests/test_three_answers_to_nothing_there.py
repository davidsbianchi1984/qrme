"""Taking something back, and the three different answers to "there was
nothing there".

Three deletes sit next to each other in this product, and they disagree about
the one case a console most needs to get right:

| | nothing to remove | somebody else's |
|---|---|---|
| a comment | **404** `no such comment` | **403** `not your comment` |
| a directory listing | **404** `profile is not listed` | 403 |
| a friend | **200**, `removed: false` | — (owner-only) |

The third is the one that bites. A caller reading only the status code reports
*Removed.* for a row that was never there — so the friends screen reads the
flag, and the other two let the refusal carry the fact.

None of this is a bug in any one route; it is three reasonable local choices
that do not agree once a screen has to speak for all of them. Recorded rather
than unified, because changing a delete's status code changes it for every
client already written against it.

The founder's two profiles are pinned and answer **409**. The list marks them
with `pinned`, which the backend's own docstring says exists *so a client can
render those rows without a remove control rather than offering one that
fails* — so the control is absent there rather than present and refused.
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


def _profile(client, account="acct_take", name="Rosa"):
    p = client.post("/profiles", json={
        "owner_id": account, "kind": "fictional", "display_name": name,
        "purpose": "creator_persona", "persona": "warm",
        "verification": {"birthdate": "1990-01-01"}}).json()
    head = {"authorization": f"Bearer {p['owner_token']}"}
    client.post(f"/memberships/{account}", json={"plan": "pro"}, headers=head)
    return p, head


# --- the three answers ------------------------------------------------------

def test_unlisting_something_never_listed_is_a_404(client):
    p, head = _profile(client, "acct_unlist")
    r = client.request("DELETE", f"/profiles/{p['id']}/marketplace",
                       headers=head)
    assert r.status_code == 404
    assert "not listed" in r.json()["detail"]


def test_deleting_a_comment_that_is_not_there_is_a_404(client):
    _, head = _profile(client, "acct_nocomment")
    r = client.request("DELETE", "/comments/cmt_nothing", headers=head)
    assert r.status_code == 404


def test_unfriending_a_stranger_is_a_200_that_says_it_did_nothing(client):
    """The one that bites. It succeeds, and the only thing distinguishing it
    from a real removal is a flag in the body."""
    p, head = _profile(client, "acct_nofriend")
    r = client.request("DELETE", f"/profiles/{p['id']}/friends/prf_nobody",
                       headers=head)
    assert r.status_code == 200
    assert r.json()["removed"] is False
    assert r.json().get("reason")


def test_the_three_disagree_and_that_is_the_point(client):
    """Asserted together. Any future round that unifies them should change
    this test on purpose rather than discover the difference in the field."""
    p, head = _profile(client, "acct_three")
    codes = {
        "listing": client.request(
            "DELETE", f"/profiles/{p['id']}/marketplace",
            headers=head).status_code,
        "comment": client.request(
            "DELETE", "/comments/cmt_nothing", headers=head).status_code,
        "friend": client.request(
            "DELETE", f"/profiles/{p['id']}/friends/prf_nobody",
            headers=head).status_code,
    }
    assert codes == {"listing": 404, "comment": 404, "friend": 200}


def test_the_friends_screen_reads_the_flag_not_the_status(client):
    """Without this it says "removed" for somebody who was never there."""
    src = _markup("app/src/screens/Friends.tsx")
    assert "r.removed" in src
    # The sentence moved into the l10n table, so the screen is asked for the
    # lookup and the table is asked for the words. Matching the sentence in
    # the screen would now match nothing; matching the key alone would pass
    # with the table saying anything at all.
    assert 'tr("frn.nothingtoremove", lang)' in src
    assert "Nothing to remove" in _markup("app/src/l10n.ts")


# --- who may take what back -------------------------------------------------

def test_a_comment_is_withdrawn_by_the_person_who_wrote_it(client):
    p, head = _profile(client, "acct_mine")
    fan = client.post("/interactors", json={"display_name": "Ana"}).json()
    fhead = {"authorization": f"Bearer {fan['token']}"}
    c = client.post(f"/profiles/{p['id']}/comments", headers=fhead,
                    json={"body": "lovely"}).json()

    other = client.post("/interactors", json={"display_name": "Nosy"}).json()
    denied = client.request(
        "DELETE", f"/comments/{c['id']}",
        headers={"authorization": f"Bearer {other['token']}"})
    assert denied.status_code == 403
    assert "not your comment" in denied.json()["detail"]

    ok = client.request("DELETE", f"/comments/{c['id']}", headers=fhead)
    assert ok.status_code == 200 and ok.json()["deleted"] is True


def test_the_subject_of_a_comment_cannot_delete_it_either(client):
    """The profile being commented on is not the comment's author. Removing
    criticism from your own page is a different power from withdrawing your
    own words, and this route only grants the second."""
    p, head = _profile(client, "acct_subject")
    fan = client.post("/interactors", json={"display_name": "Ana"}).json()
    c = client.post(f"/profiles/{p['id']}/comments",
                    headers={"authorization": f"Bearer {fan['token']}"},
                    json={"body": "not for me"}).json()
    assert client.request("DELETE", f"/comments/{c['id']}",
                          headers=head).status_code == 403


def test_the_wall_offers_withdraw_only_on_your_own():
    assert "c.author_id === session.profileId" in _markup(
        "app/src/screens/Wall.tsx")


def test_only_the_owner_lists_a_profile_in_the_directory(client):
    p, head = _profile(client, "acct_dir")
    fan = client.post("/interactors", json={"display_name": "Ana"}).json()
    assert client.post(
        f"/profiles/{p['id']}/marketplace", json={"tags": ["x"]},
        headers={"authorization": f"Bearer {fan['token']}"}
    ).status_code == 403


# --- listing is idempotent --------------------------------------------------

def test_listing_twice_replaces_rather_than_duplicates(client):
    """One profile is in the directory once. A second row would show the
    same face twice under two sets of tags."""
    p, head = _profile(client, "acct_twice")
    client.post(f"/profiles/{p['id']}/marketplace", headers=head,
                json={"tags": ["coach", "calm"], "blurb": "a steady voice"})
    client.post(f"/profiles/{p['id']}/marketplace", headers=head,
                json={"tags": ["coach"], "blurb": "changed"})
    rows = [r for r in client.get("/marketplace").json()
            if r["profile_id"] == p["id"]]
    assert len(rows) == 1
    assert rows[0]["tags"] == ["coach"] and rows[0]["blurb"] == "changed"


def test_the_directory_card_carries_no_persona(client):
    """Display information only. The persona is the thing somebody would pay
    for, and a browse endpoint that leaked it would give it away."""
    p, head = _profile(client, "acct_leak")
    client.post(f"/profiles/{p['id']}/marketplace", headers=head,
                json={"tags": ["coach"]})
    card = next(r for r in client.get("/marketplace").json()
                if r["profile_id"] == p["id"])
    assert "persona" not in card
    assert "warm" not in str(card)


def test_the_screen_says_listing_again_replaces():
    assert 'tr("mkt.replaces", lang)' in _markup("app/src/screens/Market.tsx")
    assert "replaces the tags" in _markup("app/src/l10n.ts"), (
        "the sentence left the l10n table, so the screen looks up nothing")


# --- the pinned rows --------------------------------------------------------

def test_the_list_marks_which_rows_cannot_be_removed(client):
    """`pinned` exists so a client can render those rows without a remove
    control — the backend's own words. A screen that ignored it would offer
    a button that always answers 409."""
    p, head = _profile(client, "acct_pinned")
    view = client.get(f"/profiles/{p['id']}/friends", headers=head).json()
    assert "founder_handles" in view
    for row in view["friends"]:
        assert "pinned" in row


def test_the_friends_screen_hides_remove_on_those_rows():
    src = _markup("app/src/screens/Friends.tsx")
    assert "!isFounder && (" in src, (
        "the remove control is offered on the pinned rows, which answer 409")


# --- the console half -------------------------------------------------------

def _src(rel: str) -> str:
    return (REPO / rel).read_text(encoding="utf-8")


def _markup(rel: str) -> str:
    s = re.sub(r"/\*.*?\*/", "", _src(rel), flags=re.S)
    return re.sub(r"^\s*//.*$", "", s, flags=re.M)


@pytest.mark.parametrize("binding,screen", [
    ("api.removeFriend(", "app/src/screens/Friends.tsx"),
    ("api.deleteComment(", "app/src/screens/Wall.tsx"),
    ("api.listOnMarketplace(", "app/src/screens/Market.tsx"),
    ("api.unlistFromMarketplace(", "app/src/screens/Market.tsx"),
])
def test_each_control_lives_where_the_thing_it_undoes_does(binding, screen):
    """No new screen this round on purpose. A take-it-back control belongs
    beside the thing it takes back; a fourth screen collecting all the
    deletes would be a place nobody would look."""
    assert binding in _src(screen)
