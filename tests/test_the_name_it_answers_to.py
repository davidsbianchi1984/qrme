"""Anybody could take away the name a profile answers to.

`PUT /profiles/{id}/handle` took no credential of any kind — no `request`
parameter, no `require_owner`, nothing. And the damage is not that a stranger
could give a profile a second name to be found by. Claiming a handle runs

    DELETE FROM handles WHERE profile_id=?

first, because that is how *changing* your handle works. So anybody could take
`@rosa` away from Rosa: the handle she had published stopped resolving, the one
the stranger chose resolved to her profile instead, and every printed
reference, shared link and beacon that named her went dead at once — with the
name she now answered to picked by whoever did it.

The three beacon routes sitting immediately below this one in the same file
were given exactly this check in an earlier pass. `place_beacon` states the
reason in words that fit here without changing a syllable:

    It was anybody's, which meant a stranger could print stickers pointing at
    somebody else's profile, in places its owner never chose and cannot see.

That pass hardened placing, listing and picking up, and walked past the handle
route directly above them.

The rest of this file is the door the round built: the language a profile
speaks, translating something it ran across, and composing a post — four owner
controls the console could not reach.
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


def _profile(client, account="acct_words", **over):
    body = {"owner_id": account, "kind": "fictional", "display_name": "Rosa",
            "purpose": "creator_persona", "persona": "a neighbour",
            "verification": {"birthdate": "1980-01-01"}}
    body.update(over)
    p = client.post("/profiles", json=body).json()
    return p["id"], {"authorization": f"Bearer {p['owner_token']}"}


# --- the defect -------------------------------------------------------------

def test_nobody_takes_the_name_off_somebody_elses_profile(client):
    """The whole round in one test: the handle Rosa published must survive
    a stranger asking for a different one."""
    rosa, mine = _profile(client, "acct_rosa")
    assert client.put(f"/profiles/{rosa}/handle", headers=mine,
                      json={"handle": "rosa"}).status_code == 200
    assert client.get("/summon?ref=@rosa").status_code == 200

    stolen = client.put(f"/profiles/{rosa}/handle", json={"handle": "notrosa"})
    assert stolen.status_code == 401, (
        "a caller with no credential at all renamed somebody else's profile")

    assert client.get("/summon?ref=@rosa").status_code == 200, (
        "the handle she published stopped resolving")
    assert client.get("/summon?ref=@notrosa").status_code == 404


def test_another_owners_token_is_not_enough_either(client):
    rosa, mine = _profile(client, "acct_r2")
    _sal, theirs = _profile(client, "acct_s2", display_name="Sal")
    client.put(f"/profiles/{rosa}/handle", headers=mine,
               json={"handle": "rosatwo"})
    assert client.put(f"/profiles/{rosa}/handle", headers=theirs,
                      json={"handle": "notrosatwo"}).status_code == 403
    assert client.get("/summon?ref=@rosatwo").status_code == 200


def test_the_owner_can_still_change_their_own(client):
    """The fix must not take the feature away — replacing your own handle is
    the thing the DELETE is there for."""
    rosa, mine = _profile(client, "acct_r3")
    client.put(f"/profiles/{rosa}/handle", headers=mine,
               json={"handle": "rosathree"})
    assert client.put(f"/profiles/{rosa}/handle", headers=mine,
                      json={"handle": "rosanew"}).status_code == 200
    assert client.get("/summon?ref=@rosanew").status_code == 200
    assert client.get("/summon?ref=@rosathree").status_code == 404, (
        "changing it is meant to release the old one")


def test_a_handle_somebody_else_holds_is_refused(client):
    rosa, mine = _profile(client, "acct_r4")
    _sal, theirs = _profile(client, "acct_s4", display_name="Sal")
    client.put(f"/profiles/{rosa}/handle", headers=mine,
               json={"handle": "taken"})
    clash = client.put(f"/profiles/{_sal}/handle", headers=theirs,
                       json={"handle": "taken"})
    assert clash.status_code == 409
    assert "already claimed" in clash.json()["detail"]


# --- the language -----------------------------------------------------------

def test_the_catalogue_is_public(client):
    """A static registry, and a client needs it before it can offer a
    choice."""
    got = client.get("/languages")
    assert got.status_code == 200
    codes = [row["code"] for row in got.json()["languages"]]
    assert got.json()["default"] in codes
    assert "en" in codes


def test_only_the_owner_sets_the_language(client):
    pid, mine = _profile(client, "acct_lang")
    _o, theirs = _profile(client, "acct_lang2", display_name="Sal")
    body = {"language": "es", "mode": "pre"}
    assert client.put(f"/profiles/{pid}/language",
                      json=body).status_code == 401
    assert client.put(f"/profiles/{pid}/language", headers=theirs,
                      json=body).status_code == 403
    out = client.put(f"/profiles/{pid}/language", headers=mine, json=body)
    assert out.status_code == 200
    assert out.json()["label"] == "Español"


def test_an_unknown_language_or_mode_is_named_in_the_refusal(client):
    pid, mine = _profile(client, "acct_langbad")
    bad = client.put(f"/profiles/{pid}/language", headers=mine,
                     json={"language": "xx", "mode": "pre"})
    assert bad.status_code == 422 and "language must be one of" in \
        bad.json()["detail"]
    mode = client.put(f"/profiles/{pid}/language", headers=mine,
                      json={"language": "en", "mode": "sometimes"})
    assert mode.status_code == 422 and "mode must be one of" in \
        mode.json()["detail"]


def test_the_stored_preference_is_readable(client):
    pid, mine = _profile(client, "acct_langread")
    client.put(f"/profiles/{pid}/language", headers=mine,
               json={"language": "ja", "mode": "on_demand"})
    got = client.get(f"/profiles/{pid}/language").json()
    assert got["language"] == "ja" and got["mode"] == "on_demand"


# --- translating ------------------------------------------------------------

def test_only_the_owner_translates(client):
    pid, mine = _profile(client, "acct_tr")
    _o, theirs = _profile(client, "acct_tr2", display_name="Sal")
    body = {"text": "good morning"}
    assert client.post(f"/profiles/{pid}/translate",
                       json=body).status_code == 401
    assert client.post(f"/profiles/{pid}/translate", headers=theirs,
                       json=body).status_code == 403
    assert client.post(f"/profiles/{pid}/translate", headers=mine,
                       json=body).status_code == 200


def test_it_says_when_it_cannot_translate(client):
    """The offline stub answers `engine: none` with a reason rather than
    handing the input back as though it had done the work."""
    pid, mine = _profile(client, "acct_trnone")
    out = client.post(f"/profiles/{pid}/translate", headers=mine,
                      json={"text": "good morning"}).json()
    assert out["engine"] == "none"
    assert out["note"], "a refusal without a reason is unfixable from outside"


# --- composing --------------------------------------------------------------

def test_only_the_owner_composes(client):
    pid, mine = _profile(client, "acct_comp")
    _o, theirs = _profile(client, "acct_comp2", display_name="Sal")
    body = {"topic": "a quiet morning"}
    assert client.post(f"/profiles/{pid}/compose",
                       json=body).status_code == 401
    assert client.post(f"/profiles/{pid}/compose", headers=theirs,
                       json=body).status_code == 403
    assert client.post(f"/profiles/{pid}/compose", headers=mine,
                       json=body).status_code == 201


def test_a_composed_post_carries_a_credential_from_the_start(client):
    """It is synthetic media leaving the platform the moment it exists."""
    pid, mine = _profile(client, "acct_compcred")
    out = client.post(f"/profiles/{pid}/compose", headers=mine,
                      json={"topic": "morning"}).json()
    assert out["watermark"]["watermark_id"]
    assert "AI" in out["watermark"]["disclosure"]


# --- the clients ------------------------------------------------------------

def _src(rel: str) -> str:
    return (REPO / rel).read_text(encoding="utf-8")


def test_the_screen_calls_every_binding():
    src = _src("app/src/screens/InWords.tsx")
    for binding in ("api.languages(", "api.profileLanguage(",
                    "api.setProfileLanguage(", "api.translate(",
                    "api.claimHandle(", "api.composePost("):
        assert binding in src, f"{binding} is still called by nothing"


def test_the_console_handle_binding_carries_a_token():
    src = _src("app/src/api.ts")
    sig = src[src.index("  claimHandle:"):]
    assert "token: string" in sig[:200]


def test_every_native_shell_sends_the_owner_token(client=None):
    """All three claimed handles with no credential, so a backend that now
    refuses them without a fixed client would be a break rather than a fix."""
    kt = _src("native/android/app/src/main/java/app/qrme/studio/ApiClient.kt")
    body = kt[kt.index("suspend fun claimHandle("):]
    assert "token: String" in body[:300] and "token)" in body[:400]

    swift = _src("native/ios/Sources/ApiClient.swift")
    body = swift[swift.index("func claimHandle("):]
    assert "token: token" in body[:400]

    cs = _src("native/windows/ApiClient.cs")
    body = cs[cs.index("public Task<HandleClaim> ClaimHandle("):]
    assert "Bearer {token}" in body[:600]


def test_every_native_call_site_passes_one():
    kt = _src("native/android/app/src/main/java/app/qrme/studio/ui/Screens.kt")
    assert "claimHandle(vm.pid!!, handle," in kt and "vm.token" in kt

    swift = _src("native/ios/Sources/Views/ManageView.swift")
    site = swift[swift.index("claimHandle("):]
    assert "state.token" in site[:300]

    cs = _src("native/windows/Views/ReachPage.xaml.cs")
    site = cs[cs.index("ClaimHandle("):]
    assert "s.Token" in site[:300]


def test_the_screen_says_what_claiming_replaces():
    src = re.sub(r"^\s*//.*$", "", _src("app/src/screens/InWords.tsx"),
                 flags=re.M)
    flat = " ".join(src.split())
    assert "the old one stops resolving" in flat


def test_the_screen_treats_language_as_more_than_a_display_setting():
    flat = " ".join(_src("app/src/screens/InWords.tsx").split())
    assert "Not a display setting" in flat


def test_the_screen_reports_an_untranslated_answer_honestly():
    src = _src("app/src/screens/InWords.tsx")
    assert 'done.engine === "none"' in src
