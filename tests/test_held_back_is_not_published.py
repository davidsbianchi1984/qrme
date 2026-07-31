"""A post the filter refused was published by the route that lists what was
published.

`compose_post` runs every public post through the **strict** moderation filter,
because a public post faces the widest audience there is. When the filter holds
one — or when the owner has set this profile to approve its own posts by hand —
the post is stored `pending`, and the route is deliberate about what it hands
back:

    "content": content if status == "approved" else None

`content: None`, **to the owner who just asked for it**. That is a considered
rule, written into the response of the function that creates the thing.

Fourteen lines further down, `list_posts` returned ``{**dict(r)}`` — every
column of every row, whatever its status — to anybody, with no token at all. So
the hold was enforced against the author and against nobody else. A post the
strict filter refused was readable in full, by a stranger, from the route whose
entire job is to list what this profile has *published* — carrying
``flag_reason`` with it, which is the sentence naming the rule the text broke.

Two things are true at once and the route now says both: an approved post is
public, and a held one is a queue. The owner sees their own queue; nobody else
sees it at all.

The rest of this file pins the other two surfaces the same screen opens, both
of which were already right and are worth holding still:

* the **designation cannot be designed away** — an owner may choose the glyph
  and the label, and the line comes back with `AI ·` in front of whatever they
  chose;
* an owner **cannot resolve an objection against their own profile**. All they
  may do is re-attest the basis they claim the right on. Resolving is the
  reviewer's, because an owner who could dismiss it would be deciding their
  own case.
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


def _profile(client, account="acct_mark", **over):
    body = {"owner_id": account, "kind": "fictional", "display_name": "Rosa",
            "purpose": "creator_persona", "persona": "a neighbour",
            "verification": {"birthdate": "1980-01-01"}}
    body.update(over)
    p = client.post("/profiles", json=body).json()
    return p["id"], {"authorization": f"Bearer {p['owner_token']}"}


def _held(client, account="acct_held"):
    """A profile whose posts wait for the owner, and one post waiting."""
    pid, head = _profile(client, account, moderation_mode="manual")
    made = client.post(f"/profiles/{pid}/compose", headers=head,
                       json={"topic": "a quiet morning"})
    assert made.status_code == 201, made.text
    assert made.json()["status"] == "pending"
    return pid, head, made.json()


# --- the defect -------------------------------------------------------------

def test_the_author_is_not_shown_a_held_post(client):
    """The rule the listing route was undoing. Stated first because it is the
    thing that makes the rest a contradiction rather than a preference."""
    _pid, _head, made = _held(client, "acct_author")
    assert made["content"] is None
    assert made["flag_reason"] == "owner approval required"


def test_a_held_post_is_not_public(client):
    _pid, _head, _made = _held(client, "acct_public")
    rows = client.get(f"/profiles/{_pid}/posts")
    assert rows.status_code == 200
    assert rows.json() == [], (
        "a post the profile is still holding was listed, in full, to a caller "
        "with no credential at all")


def test_the_reason_it_was_held_is_not_public_either(client):
    """`flag_reason` names the rule the text broke. That is a moderation
    signal about a post nobody may read yet."""
    pid, _head, _made = _held(client, "acct_reason")
    body = client.get(f"/profiles/{pid}/posts").text
    assert "owner approval required" not in body


def test_the_owner_sees_their_own_queue(client):
    pid, head, _made = _held(client, "acct_queue")
    rows = client.get(f"/profiles/{pid}/posts", headers=head).json()
    assert [r["status"] for r in rows] == ["pending"]
    assert rows[0]["content"], "the owner's queue is useless without the text"
    assert rows[0]["flag_reason"] == "owner approval required"


def test_another_owner_sees_nothing_of_it(client):
    """A valid token, for the wrong profile."""
    pid, _head, _made = _held(client, "acct_mine")
    _other, theirs = _profile(client, "acct_theirs", display_name="Sal")
    assert client.get(f"/profiles/{pid}/posts", headers=theirs).json() == []


def test_an_approved_post_stays_public(client):
    """The fix must not close the route it was protecting."""
    pid, head = _profile(client, "acct_open")
    made = client.post(f"/profiles/{pid}/compose", headers=head,
                       json={"topic": "a quiet morning"}).json()
    assert made["status"] == "approved"
    rows = client.get(f"/profiles/{pid}/posts").json()
    assert len(rows) == 1
    assert rows[0]["content"] == made["content"]


def test_every_listed_post_carries_its_credential(client):
    """A public post is synthetic media leaving the platform, so it travels
    with the mark rather than beside it."""
    pid, head = _profile(client, "acct_cred")
    client.post(f"/profiles/{pid}/compose", headers=head,
                json={"topic": "morning"})
    row = client.get(f"/profiles/{pid}/posts").json()[0]
    assert row["watermark"]["watermark_id"] == row["watermark_id"]
    assert "AI" in row["watermark"]["disclosure"]


# --- the designation --------------------------------------------------------

def test_the_mark_is_readable_by_anyone(client):
    """Every render of this profile's work carries the line, so anybody
    looking at one can check what it should say."""
    pid, _head = _profile(client, "acct_read")
    got = client.get(f"/profiles/{pid}/watermark")
    assert got.status_code == 200
    assert got.json()["always_displayed"] is True
    assert got.json()["custom"] is False


def test_only_the_owner_designs_it(client):
    pid, head = _profile(client, "acct_design")
    _o, theirs = _profile(client, "acct_design2", display_name="Sal")
    assert client.put(f"/profiles/{pid}/watermark",
                      json={"label": "Rosa"}).status_code == 401
    assert client.put(f"/profiles/{pid}/watermark", headers=theirs,
                      json={"label": "Rosa"}).status_code == 403
    assert client.put(f"/profiles/{pid}/watermark", headers=head,
                      json={"label": "Rosa"}).status_code == 200


def test_the_designation_cannot_be_designed_away(client):
    """Ask for a label with no AI in it and get one with AI in it."""
    pid, head = _profile(client, "acct_away")
    out = client.put(f"/profiles/{pid}/watermark", headers=head,
                     json={"mark": "✦", "label": "Rosa"}).json()
    assert out["label"] == "AI · Rosa"
    assert out["line"].startswith("✦ AI")
    assert out["custom"] is True


def test_clearing_it_returns_the_default(client):
    pid, head = _profile(client, "acct_clear")
    client.put(f"/profiles/{pid}/watermark", headers=head,
               json={"mark": "✦", "label": "Rosa"})
    back = client.put(f"/profiles/{pid}/watermark", headers=head,
                      json={"mark": "", "label": ""}).json()
    assert back["custom"] is False
    assert "AI" in back["line"]


# --- being contested --------------------------------------------------------

def _objected(client, account="acct_obj"):
    pid, head = _profile(client, account)
    opened = client.post("/objections", json={
        "profile_id": pid, "objector_ref": "estate-doc-4471",
        "reason": "likeness used without consent"})
    assert opened.status_code == 201, opened.text
    return pid, head, opened.json()


def test_opening_one_restricts_the_profile_at_once(client):
    _pid, _head, opened = _objected(client, "acct_restrict")
    assert opened["profile_status"] == "restricted"
    assert opened["prior_status"] == "active"
    assert "re-attest" in opened["note"]


def test_the_list_is_the_owners_alone(client):
    pid, head, _o = _objected(client, "acct_list")
    _x, theirs = _profile(client, "acct_list2", display_name="Sal")
    assert client.get(f"/profiles/{pid}/objections").status_code == 401
    assert client.get(f"/profiles/{pid}/objections",
                      headers=theirs).status_code == 403
    assert len(client.get(f"/profiles/{pid}/objections",
                          headers=head).json()) == 1


def test_the_owner_re_attests_and_nothing_more(client):
    pid, head, opened = _objected(client, "acct_attest")
    done = client.post(f"/profiles/{pid}/objections/{opened['id']}/attest",
                       headers=head)
    assert done.status_code == 200
    assert done.json()["reattested"] is True
    assert "awaiting reviewer" in done.json()["note"]


def test_an_owner_token_does_not_adjudicate_their_own_case(monkeypatch,
                                                           client):
    """Resolving sits behind the reviewer role rather than ownership, and
    this is the sentence `resolve_objection` gives for it: an owner must not
    adjudicate an objection against their own profile.

    `QRME_ADMIN_TOKEN` is set here on purpose. Unset, `require_reviewer`
    takes its documented development path — open to localhost, `503` to
    anything further away — and a test that ran on that path would be
    asserting about the deployment it is not describing.
    """
    monkeypatch.setenv("QRME_ADMIN_TOKEN", "reviewer-secret")
    pid, head, opened = _objected(client, "acct_adjudicate")
    assert client.post(f"/objections/{opened['id']}/resolve", headers=head,
                       json={"outcome": "dismiss"}).status_code == 403
    assert client.post(f"/objections/{opened['id']}/resolve",
                       json={"outcome": "dismiss"}).status_code == 401
    allowed = client.post(
        f"/objections/{opened['id']}/resolve",
        headers={"authorization": "Bearer reviewer-secret"},
        json={"outcome": "dismiss"})
    assert allowed.status_code == 200
    assert client.get(f"/profiles/{pid}").json()["status"] == "active", (
        "a dismissal restores whatever the profile was before the objection")


def test_a_stranger_cannot_re_attest_for_them(client):
    pid, _head, opened = _objected(client, "acct_stranger")
    _x, theirs = _profile(client, "acct_stranger2", display_name="Sal")
    assert client.post(
        f"/profiles/{pid}/objections/{opened['id']}/attest").status_code == 401
    assert client.post(f"/profiles/{pid}/objections/{opened['id']}/attest",
                       headers=theirs).status_code == 403


def test_an_objection_from_another_profile_is_a_404(client):
    _pid, _head, opened = _objected(client, "acct_cross")
    other, ohead = _profile(client, "acct_cross2", display_name="Sal")
    assert client.post(f"/profiles/{other}/objections/{opened['id']}/attest",
                       headers=ohead).status_code == 404


# --- the console half -------------------------------------------------------

def _src(rel: str) -> str:
    return (REPO / rel).read_text(encoding="utf-8")


def _markup(rel: str) -> str:
    s = re.sub(r"/\*.*?\*/", "", _src(rel), flags=re.S)
    return re.sub(r"^\s*//.*$", "", s, flags=re.M)


def test_the_screen_calls_every_binding():
    src = _src("app/src/screens/TheMark.tsx")
    for binding in ("api.watermarkDesign(", "api.setWatermarkDesign(",
                    "api.profilePosts(", "api.profileObjections(",
                    "api.reattestBasis("):
        assert binding in src, f"{binding} is still called by nothing"


def test_the_screen_shows_the_answer_rather_than_the_request():
    """Typing a label and being shown your own text back would teach the
    wrong lesson about what the control does."""
    src = _markup("app/src/screens/TheMark.tsx")
    assert "design.line" in src
    assert "setDesign(d)" in src


def test_the_screen_separates_held_from_published():
    src = _markup("app/src/screens/TheMark.tsx")
    assert 'p.status !== "approved"' in src
    assert 'p.status === "approved"' in src
    flat = " ".join(src.split())
    assert "Only you see this" in flat


def test_the_screen_says_the_owner_cannot_resolve_it():
    flat = " ".join(_markup("app/src/screens/TheMark.tsx").split())
    assert "deciding their own case" in flat


def test_the_posts_binding_can_be_called_without_a_token():
    """It is a public route, and the console reads it as the public too — a
    binding that demanded a token would have hidden the defect."""
    src = _src("app/src/api.ts")
    sig = src[src.index("  profilePosts:"):]
    assert "token?: string" in sig[:200]
