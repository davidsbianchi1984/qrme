"""One screen falling over must not take the console with it.

## What happened

`api.feed` was declared in `app/src/api.ts` as answering `{ posts }`. The
route has only ever answered `{ feed_posts }`. So the Wall screen read
`undefined`, put it in state, rendered `posts.length` — and React, with no
error boundary anywhere in the tree, unmounted the **entire application**.
Pressing *Wall* gave a tester a white page: no drawer to leave by, no
message, no way back except reloading the browser.

    asked     does the screen work
    mattered  what the rest of the console does when it doesn't

Two separate failures, and this file holds both ends of them.

**The type lie.** A hand-written response shape that the server has never
sent is worse than no type at all, because the checker then enforces it:
`tsc` was clean on every line of the broken code. So the shapes the
console declares for its GET bindings are checked against what the routes
actually answer.

**The missing boundary.** A crash will happen again — that is what a crash
is. What is a choice is whether it costs one card or the whole session.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()
APP = REPO / "app" / "src"


# --------------------------------------------------------------------------
# The boundary


def test_the_screens_are_rendered_inside_a_boundary():
    source = (APP / "App.tsx").read_text(encoding="utf-8")
    assert "<Boundary" in source, (
        "the tab switch renders every screen; nothing catches one that "
        "throws, so a single bad render blanks the whole console")
    # Keyed by tab: without the key React keeps one boundary across a tab
    # change, and a screen that failed once leaves the next one showing
    # its notice instead of itself.
    assert re.search(r"<Boundary[^>]*key=\{tab\}", source), (
        "the boundary must be keyed by tab, or a failure on one screen is "
        "carried onto the next")


def test_the_boundary_catches_reports_and_offers_a_way_out():
    source = (APP / "Boundary.tsx").read_text(encoding="utf-8")
    assert "getDerivedStateFromError" in source
    assert "componentDidCatch" in source
    # The failure is a report, not somebody's memory of a white page.
    assert "recordProblem" in source
    # And the screen can be tried again without reloading the browser.
    assert "setState({ failed: null })" in source


def test_the_boundary_says_the_rest_still_works():
    """A person looking at a broken card needs to know whether the app is
    gone or one screen is."""
    source = (APP / "Boundary.tsx").read_text(encoding="utf-8")
    assert "Everything else still works" in source


# --------------------------------------------------------------------------
# The type lie


#: Bindings whose declared shape is checked against the live route. Each is
#: (api.ts binding name, path built from one seeded profile). Kept as an
#: explicit list rather than parsed out of every binding in the file: this
#: guard is about the ones a screen renders with `.length`, and a list
#: somebody adds to deliberately is a list somebody reads.
CHECKED = [
    ("feed", "/profiles/{pid}/feed"),
    ("myWall", "/profiles/{pid}/wall"),
    ("handGrants", "/profiles/{pid}/hands/grants"),
    ("routines", "/profiles/{pid}/hands/routines"),
    ("handsVocabulary", "/hands/vocabulary"),
]


def _declared(name: str) -> set[str]:
    """The top-level keys `api.ts` says this binding answers with.

    Two forms, because both are used: an inline `req<{ a: X; b: Y }>` and
    a `req<NamedType>` whose `export type` is resolved here. A guard that
    read only the inline form would silently skip every binding written
    the other way, which is the same class of quiet gap it exists for.
    """
    source = (APP / "api.ts").read_text(encoding="utf-8")
    match = re.search(rf"^  {re.escape(name)}: \([^)]*\) =>\s*\n?\s*"
                      r"req<(\{[^}]*\}|\w+)>", source, re.M)
    if match is None:
        pytest.fail(f"no binding named {name!r} in api.ts")
    body = match.group(1)
    if body.startswith("{"):
        body = body[1:-1]        # the inline form's own braces
    else:
        named = re.search(rf"^export type {re.escape(body)} = \{{(.*?)^\}};",
                          source, re.M | re.S)
        if named is None:
            pytest.fail(f"api.{name} answers {body!r} and no such type here")
        body = named.group(1)
    # Top-level keys only. Nested objects are elided first, by brace
    # depth rather than by indentation — `caps: { steps; minutes }` is
    # written on one line and its members are not keys of the response.
    flat, depth = [], 0
    for char in body:
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        elif depth == 0:
            flat.append(char)
    return {m.group(1) for m in re.finditer(r"(?:^|[;,\n])\s*(\w+)\s*:",
                                            "".join(flat))}


def test_the_shape_the_console_declares_is_the_shape_it_gets(client,
                                                             profile_id):
    """The one that would have caught the white page.

    A declared key the route does not send becomes `undefined` in state,
    and a screen that renders it as a list crashes on the first `.length`.
    """
    wrong = []
    for name, template in CHECKED:
        declared = _declared(name)
        assert declared, name
        got = client.get(template.format(pid=profile_id))
        assert got.status_code == 200, (name, got.text)
        answered = set(got.json().keys())
        missing = sorted(declared - answered)
        if missing:
            wrong.append(f"api.{name} declares {missing} — the route answers "
                         f"{sorted(answered)}")
    assert not wrong, "\n".join(wrong)


def test_the_wall_survives_a_feed_with_no_posts(client, profile_id):
    """The screen's own defence, in the shape the crash took: whatever the
    route answers, what reaches `.length` is a list."""
    source = (APP / "screens" / "Wall.tsx").read_text(encoding="utf-8")
    for setter in ("setPosts(", "setMine("):
        line = next(ln for ln in source.splitlines() if setter in ln
                    and "useState" not in ln)
        assert "|| []" in line, (
            f"{setter} can put undefined in state, and this screen renders "
            "that value with .length")


def test_the_feed_route_still_answers_feed_posts(client, profile_id):
    """Pinned in both directions. If the route is ever renamed to `posts`
    this fails, and somebody looks at the console before shipping it."""
    body = client.get(f"/profiles/{profile_id}/feed").json()
    assert "feed_posts" in body
    assert isinstance(body["feed_posts"], list)


# --------------------------------------------------------------------------
# The harness that photographed the wrong screen


def test_the_camera_checks_what_it_photographed():
    """`tools/shoot_screens.py` navigated by `#tab`. This console has no
    hash router, so every capture it took was the Home screen — filed
    under thirty-nine different names. A harness that navigates by a
    mechanism the product does not have fails silently and produces
    confident, wrong output.
    """
    source = (REPO / "tools" / "shoot_screens.py").read_text(encoding="utf-8")
    assert 'data-tab=' in source, (
        "the camera must reach a tab the way a person does — by pressing "
        "it in the drawer")
    # And then check: the tab the console marks active has to be the one
    # that was asked for, or nothing is written.
    assert ".nav-item.active" in source
    assert "nothing written" in source


def test_the_drawer_names_its_tabs_in_the_markup():
    """The attribute the camera and any future test press by. A label
    would work until somebody reads the console in Spanish."""
    source = (APP / "App.tsx").read_text(encoding="utf-8")
    assert source.count("data-tab={n.id}") == 2, (
        "both the ungrouped and the grouped nav items need it")
