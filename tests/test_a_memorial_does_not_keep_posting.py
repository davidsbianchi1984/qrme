"""Nobody could talk to the dead. The dead could still talk to everybody.

## The finding

`POST /profiles/{id}/chat` gets it right, and has for releases:

    if profile["status"] == "departed":
        raise HTTPException(
            410, "this profile has departed; its memory remains viewable")

`POST /profiles/{id}/compose` — which writes a public post in that profile's
voice and publishes it where anyone can read it — had no such check. Driven
against a profile that had been sunset:

    chat      410
    compose   201   ← and the post is publicly readable

So a memorial went on publishing. `succeed_profile`'s own docstring calls the
state *"frozen rather than orphaned"*; it was not frozen.

    asked     can somebody still talk to a departed profile
    mattered  can a departed profile still be made to speak

## The same hole, one status over

`open_objection` says it **"suspends the profile pending review"**, and the
refusal a restricted profile raises says it *"is not accepting new
interactors"*. Both true, and both about who may *start a conversation*. A
profile restricted pending an objection review — one whose subject is
contesting that it should exist at all — went on composing and publishing in
that person's voice throughout the review, which is the harm the objection was
raised to stop.

## The count

Nine route handlers make a profile produce new words. **Two checked its
status**: `chat` and `proactive_checkin` — the two whose subject is the person
on the *other* side of the conversation. The seven that did not included the
one that publishes.

The two gates that existed were the two whose docstrings were about a reader.
Nobody had asked the question the other way round.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from qrme import common

from . import ratchets


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()
ROUTERS = REPO / "qrme" / "routers"

#: Functions that put words in a profile's mouth, by the module that defines
#: them. Declared rather than inferred, and checked for completeness below —
#: a name-only scan matched `watchparty.chat`, a **GET** that reads a room's
#: transcript, purely because `interaction.chat` shares its name.
GENERATORS = {
    "provider_for_profile",     # qrme/llm.py — every direct generation site
    "coordinate",               # qrme/organization.py
    "run",                      # qrme/simulation.py
    "translate",                # qrme/i18n.py
}

#: Route handlers that reach a generator and are **not** required to gate, each
#: with the reason. Kept as a list with reasons rather than as silence: an
#: unexplained exemption is how the seven ungated routes looked fine.
EXEMPT = {
    ("organizations.py", "coordinate"):
        "gated one level in, at qrme/organization.py:coordinate, because an "
        "organization speaks as *each department's* agent profile and the "
        "route knows only the org. Departments whose agent is departed, "
        "terminated or contested are skipped and named in `silenced`; the "
        "initiating department's agent must be active or the whole "
        "coordination is refused.",
}


def _handlers(path: Path):
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for dec in fn.decorator_list:
            f = dec.func if isinstance(dec, ast.Call) else dec
            if (isinstance(f, ast.Attribute)
                    and f.attr in ("get", "post", "put", "delete", "patch")):
                yield fn, f.attr
                break


def _calls(fn) -> set[str]:
    return {getattr(n.func, "attr", None) or getattr(n.func, "id", "")
            for n in ast.walk(fn) if isinstance(n, ast.Call)}


def _source(mod: str, name: str) -> str:
    """One handler's own source text."""
    src = (ROUTERS / mod).read_text(encoding="utf-8")
    for fn, _ in _handlers(ROUTERS / mod):
        if fn.name == name:
            return ast.get_source_segment(src, fn) or ""
    return ""


def _generating_routes() -> list[tuple[str, str, set[str], str]]:
    out = []
    for path in sorted(ROUTERS.rglob("*.py")):
        for fn, verb in _handlers(path):
            names = _calls(fn)
            if names & GENERATORS:
                out.append((path.name, fn.name, names, verb))
    return out


def test_every_route_that_makes_a_profile_speak_checks_whether_it_may():
    """The generalisation. Seven of nine were ungated; naming the two I found
    by hand would have left the other five."""
    ungated = []
    for mod, name, names, _verb in _generating_routes():
        if (mod, name) in EXEMPT:
            continue
        # Either the shared gate, or the handler's own status logic — `chat`
        # keeps its because a restricted profile may still answer somebody it
        # already knows, which is a nuance the shared gate deliberately lacks.
        if "require_may_publish" in names or "require_may_speak" in names:
            continue
        # Or the handler's own status logic. `chat` keeps its own because a
        # restricted profile may still answer somebody it already knows —
        # a nuance the shared gate deliberately lacks. Read from the
        # handler's own source, not the module's: the first draft dumped the
        # whole module and so credited every handler in a file where any one
        # of them mentioned the status.
        if '"departed"' in _source(mod, name):
            continue
        ungated.append(f"{mod}: {name}")
    assert not ungated, (
        f"{len(ungated)} route(s) put words in a profile's mouth without "
        "asking whether it may still speak — a departed profile is a "
        "memorial and a restricted one is under objection review:\n    "
        + "\n    ".join(ungated))


def test_the_route_scan_is_finding_routes():
    """A guard on the guard: a walk that stopped matching would report nothing
    ungated and pass on an empty set."""
    found = _generating_routes()
    assert len(found) >= ratchets.floor("route.generating"), (
        f"only {len(found)} generating route(s) parsed — this codebase has "
        "nine, and the check above is passing on almost nothing")


def test_every_exemption_still_names_a_real_route():
    """An exemption for a route that no longer exists is a hole nobody is
    watching."""
    live = {(mod, name) for mod, name, _, _ in _generating_routes()}
    stale = sorted(f"{m}: {n}" for (m, n) in EXEMPT if (m, n) not in live)
    assert not stale, (
        "these exemptions name routes that no longer reach a generator — "
        "strike them:\n    " + "\n    ".join(stale))


def test_the_exempt_route_is_gated_where_it_says_it_is():
    """The exemption's own reason, checked rather than trusted.

    `organizations.coordinate` is excused at the route because the gate lives
    in `qrme/organization.py`. If that gate goes, the exemption becomes a hole
    with a paragraph in front of it.
    """
    src = (REPO / "qrme" / "organization.py").read_text(encoding="utf-8")
    fn = next(n for n in ast.walk(ast.parse(src))
              if isinstance(n, ast.FunctionDef) and n.name == "coordinate")

    # Scoped to the department loop, not to the function.
    #
    # The first draft searched the whole of `coordinate` for a status
    # comparison and for the word "silenced". Deleting the per-department gate
    # left both behind — the *initiating* department's check reads
    # `status"] != "active"` too, and `silenced = []` still stood at the top —
    # so the injection passed and the loop went back to letting a dead agent
    # contribute.
    #
    #     asked     does coordinate check a status somewhere
    #     mattered  does the loop check every department's agent
    loops = [n for n in ast.walk(fn) if isinstance(n, ast.For)
             and getattr(n.target, "id", "") == "dept"]
    assert loops, (
        "no `for dept in departments` loop in coordinate — this exemption "
        "describes a function that has been rewritten")
    loop = ast.dump(loops[0])
    assert "'active'" in loop or '"active"' in loop, (
        "the department loop no longer checks each agent profile's status, so "
        "a departed, terminated or contested agent contributes to the joint "
        "plan — and organizations.coordinate is exempt from the route gate on "
        "the grounds that this check exists")
    assert "silenced" in loop, (
        "the loop no longer records which departments could not contribute, "
        "so a joint plan reads as the whole organization's while an agent is "
        "quietly missing from it")


# --- driven ----------------------------------------------------------------

def _a_profile(client, name="Dana"):
    r = client.post("/profiles", json={
        "owner_id": "o", "kind": "self", "display_name": name,
        "persona": "A retired teacher who loves gardening.", "plan": "pro",
        "verification": {"birthdate": "1984-06-01"}})
    assert r.status_code == 201, r.text
    body = r.json()
    client.headers["authorization"] = f"Bearer {body['owner_token']}"
    return body["id"]


def test_a_departed_profile_does_not_compose(client):
    """The defect, driven. Before this round: 201, and readable by anyone."""
    pid = _a_profile(client)
    assert client.post(f"/profiles/{pid}/sunset").status_code == 200
    r = client.post(f"/profiles/{pid}/compose", json={"topic": "spring"})
    assert r.status_code == 410, (
        f"a memorial composed a new public post ({r.status_code}) — "
        "succession calls this state frozen")


def test_a_departed_profile_publishes_nothing_new(client):
    """The consequence rather than the status code: no new post exists."""
    pid = _a_profile(client)
    before = len(client.get(f"/profiles/{pid}/posts").json())
    client.post(f"/profiles/{pid}/sunset")
    client.post(f"/profiles/{pid}/compose", json={"topic": "spring"})
    assert len(client.get(f"/profiles/{pid}/posts").json()) == before, (
        "a post appeared on a departed profile's public feed")


def test_a_contested_profile_does_not_publish_while_it_is_contested(client):
    """The subject of this profile is arguing it should not exist. It went on
    publishing in their voice throughout the review."""
    pid = _a_profile(client)
    client.post("/objections", json={"profile_id": pid,
                                     "objector_ref": "ref", "reason": "that is me"})
    r = client.post(f"/profiles/{pid}/compose", json={"topic": "spring"})
    assert r.status_code == 403, r.text
    assert "objection" in r.json()["detail"]


def test_an_active_profile_still_composes(client):
    """The gate refuses three statuses and must not touch the fourth."""
    pid = _a_profile(client)
    assert client.post(f"/profiles/{pid}/compose",
                       json={"topic": "spring"}).status_code == 201


@pytest.mark.parametrize("path,body", [
    ("translate", {"text": "hello"}),
    ("simulate", {"scenario": "a job offer", "horizon": "short_term"}),
])
def test_the_other_surfaces_are_shut_too(client, path, body):
    """Not only the one that was found by hand."""
    pid = _a_profile(client)
    client.post(f"/profiles/{pid}/sunset")
    r = client.post(f"/profiles/{pid}/{path}", json=body)
    assert r.status_code == 410, (
        f"/{path} still speaks for a departed profile ({r.status_code})")


def test_the_refusal_is_one_the_reader_can_be_given_in_their_language(client):
    """A new English sentence on a refusal path is a sentence somebody meets in
    a language they did not choose. This one went into the table rather than
    the backlog, which stands at one by decision."""
    from qrme import i18n
    assert common.RESTRICTED_WHILE_CONTESTED in i18n._REFUSALS
    row = i18n._REFUSALS[common.RESTRICTED_WHILE_CONTESTED]
    missing = [c for c in i18n.SUPPORTED if c != i18n.DEFAULT and c not in row]
    assert not missing, f"the new refusal is missing {missing}"
