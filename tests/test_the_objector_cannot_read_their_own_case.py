"""They could end the profile. They could not read the record of doing it.

## The finding

`GET /objections/{id}/audit` is owner- or reviewer-gated, and its docstring
gives the reason in its own words:

    Owner- or reviewer-gated (it can quote the objector's reason).

That gate is right about the free text and wrong about who it locks out. The
objector **wrote** that reason. Keeping them out of the timeline of their own
case, in order to protect them from their own words, leaves the one party on
this surface with no account — a contested person, sometimes a bereaved
estate — unable to see what was done about the thing they raised.

    asked     could the audit trail leak the objector's reason
    mattered  who is the audit trail for

And they were not a bystander. `POST /objections/{id}/withdraw` and
`/revoke` are both **public**, and both **terminate the profile and erase its
content**. The objector could pull the lever and could not read the record.

## The second half, on the same four routes

Of the four public routes on this surface:

| route | what it does | spoke the visitor's language |
|---|---|---|
| `POST /objections` | opens one | yes |
| `GET /objections/{id}` | status check | yes |
| `POST …/withdraw` | **terminates the profile** | no |
| `POST …/revoke` | **terminates the profile** | no |

The two that merely open or read an objection negotiated `Accept-Language`
and returned a translated sentence. The two that end a synthetic profile of a
real person returned `{"id": …, "status": "withdrawn", "profile_status":
"terminated"}` — three enum values and no sentence, in any language.

`test_the_stranger_has_a_language_too.py` did not catch it, and is not wrong:
it checks that the public *strings* are translated. A route that produces no
sentence at all has no string to find.

    asked     are the public strings translated
    mattered  does every public route accept the visitor's language

## What was built rather than reversed

The `/audit` gate stays exactly as it is — `test_audit_is_owner_or_reviewer_gated`
still passes, and the decision it encodes about free text is sound. What was
missing was a second view, not a wider one:

`GET /objections/{id}/timeline` is public and localized, and carries **event,
actor, time, sealed** and no `detail` at all. Not the objector's reason, not
the reviewer's note, not the owner's. The shape of what happened is theirs;
nobody's prose is.

## Why the scope is this router and not every public route

A guard needs a definition of "public" it can defend. Across `api.py` the
gates are expressed half a dozen ways and a structural walk mislabels them,
which would produce a check that fires on the wrong things — the exact
failure this audit exists to refuse. Here the four routes say what they are
in their own docstrings, and the rule holds inside one file: **in this router,
a route that is not owner- or reviewer-gated negotiates the visitor's
language.**
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.test_capabilities import ADULT  # noqa: F401 — shared fixture module

from . import ratchets


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


GOVERNANCE = _repo_root() / "qrme" / "routers" / "governance.py"

#: How this router expresses "the caller must be somebody in particular".
_GATES = {"require_owner", "require_reviewer", "_require_owner_or_reviewer"}


def _route_handlers() -> list[ast.FunctionDef]:
    tree = ast.parse(GOVERNANCE.read_text(encoding="utf-8"))
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for dec in node.decorator_list:
            fn = dec.func if isinstance(dec, ast.Call) else dec
            if (isinstance(fn, ast.Attribute)
                    and fn.attr in ("get", "post", "put", "delete", "patch")):
                out.append(node)
                break
    return out


def _is_gated(fn: ast.AST) -> bool:
    for node in ast.walk(fn):
        if isinstance(node, ast.Call):
            name = (getattr(node.func, "attr", None)
                    or getattr(node.func, "id", None))
            if name in _GATES:
                return True
    return False


def _negotiates(fn: ast.FunctionDef) -> bool:
    """Takes the header **and** does something with it.

    Both halves, because they fail differently and both have happened in this
    codebase: a handler that declares `accept_language` and never passes it on
    answers in English while looking localized, and a handler that calls
    `negotiate` on a header it never accepted always gets the default.
    """
    declared = any(a.arg == "accept_language"
                   for a in fn.args.args + fn.args.kwonlyargs)
    used = any(isinstance(n, ast.Call)
               and getattr(n.func, "attr", None) in ("negotiate",)
               for n in ast.walk(fn))
    passes_on = any(isinstance(n, ast.Name) and n.id == "accept_language"
                    for n in ast.walk(fn))
    return declared and (used or passes_on)


def test_every_public_governance_route_accepts_the_visitors_language():
    """The defect, generalised. The caller here has no account by design, so
    `Accept-Language` is the only language there is — `i18n.negotiate` says so
    in its own docstring, quoting this very router."""
    silent = [f"line {fn.lineno}: {fn.name}" for fn in _route_handlers()
              if not _is_gated(fn) and not _negotiates(fn)]
    assert not silent, (
        f"{len(silent)} public governance route(s) never look at "
        "Accept-Language, so a Spanish speaker contesting a profile of "
        "themselves is answered in English on the step that matters "
        "most:\n    " + "\n    ".join(silent))


def test_the_route_scan_is_finding_routes():
    """A guard on the guard. A decorator walk that stopped matching would
    report a router with no ungated routes and pass on nothing."""
    handlers = _route_handlers()
    assert len(handlers) >= ratchets.floor("governance.route_handlers"), (
        f"only {len(handlers)} route handler(s) parsed from governance.py — "
        "the decorator walk has stopped matching")
    assert any(_is_gated(fn) for fn in handlers), (
        "no gated route found, so the check above cannot tell an owner route "
        "from a public one and would demand a language of every handler")
    assert any(not _is_gated(fn) for fn in handlers), (
        "no public route found, so the check above passes on an empty set")


# --- driven ----------------------------------------------------------------

def _third_party(client, basis="subject_consent", **extra):
    body = {"owner_id": "owner-1", "kind": "other_person",
            "display_name": "Real Person", "persona": "A public commentator.",
            "verification": ADULT,
            "consent": {"basis": basis, "attestor": "the standing party"}}
    body.update(extra)
    r = client.post("/profiles", json=body)
    assert r.status_code == 201, r.text
    out = r.json()
    client.headers["authorization"] = f"Bearer {out['owner_token']}"
    return out


def _open(client, profile_id, reason="that is me"):
    r = client.post("/objections", json={"profile_id": profile_id,
                                         "objector_ref": "ref-1",
                                         "reason": reason})
    assert r.status_code == 201, r.text
    return r.json()


def test_the_objector_can_read_the_timeline_of_their_own_case(client, monkeypatch):
    """Without a token, in production posture — the state in which they were
    previously locked out."""
    p = _third_party(client)
    obj = _open(client, p["id"])
    client.post(f"/profiles/{p['id']}/objections/{obj['id']}/attest")

    monkeypatch.setenv("QRME_ADMIN_TOKEN", "reviewer-secret")
    client.headers.pop("authorization", None)

    r = client.get(f"/objections/{obj['id']}/timeline")
    assert r.status_code == 200, r.text
    body = r.json()
    assert [e["event"] for e in body["timeline_events"]] == ["opened", "reattested"]
    assert [e["actor"] for e in body["timeline_events"]] == ["objector", "owner"]
    assert body["status"] == "open" and body["reattested"] is True


def test_the_full_audit_is_still_owner_or_reviewer_gated(client, monkeypatch):
    """The decision that gate encodes was not reversed. A second view was
    built; the first one still guards the free text."""
    p = _third_party(client)
    obj = _open(client, p["id"])
    monkeypatch.setenv("QRME_ADMIN_TOKEN", "reviewer-secret")
    client.headers.pop("authorization", None)
    assert client.get(f"/objections/{obj['id']}/audit").status_code in (401, 403)


def test_the_timeline_carries_no_free_text_from_anybody(client):
    """The reason the gate existed, honoured rather than argued with.

    Checked over the whole serialized response, because a nested `detail`
    would satisfy a check that only looked at the top-level keys — and the
    reason lives exactly one level down.
    """
    secret = "he stole my late father's voice"
    p = _third_party(client)
    obj = _open(client, p["id"], reason=secret)
    client.headers.pop("authorization", None)

    raw = client.get(f"/objections/{obj['id']}/timeline").text
    for word in ("stole", "father", "voice"):
        assert word not in raw, (
            f"the objector's timeline repeats {word!r} from a free-text "
            "reason — the timeline carries what happened, not what anybody "
            "wrote")
    body = client.get(f"/objections/{obj['id']}/timeline").json()
    assert all("detail" not in e for e in body["timeline_events"])


@pytest.mark.parametrize("action,expected", [
    ("withdraw", "consentimiento retirado"),
    ("revoke", "autorización revocada"),
])
def test_ending_a_profile_answers_in_the_visitors_language(
        client, action, expected):
    """The most consequential public action on this surface, and the one that
    used to answer with three enum values and no sentence."""
    basis = "subject_consent" if action == "withdraw" else "estate_authorization"
    p = _third_party(client, basis=basis)
    obj = _open(client, p["id"])
    client.headers.pop("authorization", None)

    r = client.post(f"/objections/{obj['id']}/{action}",
                    headers={"Accept-Language": "es"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["profile_status"] == "terminated"
    assert expected in body["note"], (
        f"the {action} response is not in Spanish: {body.get('note')!r}")
    assert body["timeline"].endswith("/timeline"), (
        "the response does not point at the record of what just happened — "
        "the person who ended a profile has to be told where to read it")


def test_the_timeline_is_localized_too(client):
    p = _third_party(client)
    obj = _open(client, p["id"])
    client.headers.pop("authorization", None)
    body = client.get(f"/objections/{obj['id']}/timeline",
                      headers={"Accept-Language": "de"}).json()
    assert "Akte Ihres eigenen Falls" in body["note"], (
        f"the timeline's own sentence is not in German: {body['note']!r}")


def test_a_timeline_for_an_objection_that_does_not_exist_is_a_404(client):
    assert client.get("/objections/obj_nope/timeline").status_code == 404
