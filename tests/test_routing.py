"""Every literal route reaches its own handler.

FastAPI matches routes in **registration order**, so a path with a variable
segment registered before a literal one answers the literal path as well — and
the literal handler is never reached. Silently: no error, nothing in the logs,
just a different function's reply.

That has bitten this codebase twice. `/profiles/{id}/posts` once returned
another router's rows, which read as a serialisation bug for as long as it took
to find. And `/{surface}/{surface_id}/skill-grants` was written and nearly
shipped, where a two-variable prefix matches *any* three-segment path.

So rather than reviewing each new route by eye, this asserts the property for
all of them at once: for every route whose path contains a literal segment, a
request to that path must be answered by that route.
"""

import re

import pytest
from fastapi.routing import APIRoute
from starlette.routing import Match

from qrme.api import create_app


def _routes(app):
    """Every APIRoute in the app, including the ones nested in included routers.

    FastAPI wraps `include_router` results in an internal object rather than
    flattening them into `app.routes`, so a naive list comprehension over
    `app.routes` finds four routes out of three hundred — and a check that
    inspects four routes passes for the wrong reason.
    """
    found, seen = [], set()

    def walk(routes):
        for r in routes:
            if isinstance(r, APIRoute):
                if id(r) not in seen:
                    seen.add(id(r))
                    found.append(r)
            inner = getattr(r, "routes", None)
            if inner:
                walk(inner)
            wrapped = getattr(r, "original_router", None)
            if wrapped is not None:
                walk(wrapped.routes)

    walk(app.routes)
    return found


def _winner(app, path: str, method: str):
    """Which route actually answers this request, by Starlette's own matching.

    Descends into included routers rather than stopping at the wrapper, because
    the wrapper is what `app.routes` holds and reporting *it* as the winner
    would make every comparison below fail for a reason that has nothing to do
    with shadowing.
    """
    scope = {"type": "http", "method": method, "path": path, "headers": [],
             "query_string": b"", "root_path": ""}

    def dig(routes):
        partial = None
        for route in routes:
            match, _ = route.matches(scope)
            inner = getattr(route, "original_router", None)
            if match is Match.FULL:
                if inner is not None:
                    got = dig(inner.routes)
                    if got is not None:
                        return got
                    continue
                return route
            if match is Match.PARTIAL and partial is None:
                partial = dig(inner.routes) if inner is not None else route
        return partial

    return dig(app.routes)


def _sample(path: str) -> str:
    """A concrete URL for a route, with each variable filled by a plain id."""
    return re.sub(r"\{[^}]+\}", "smpl1", path)


def test_no_route_is_shadowed_by_an_earlier_variable_route():
    """The invariant. Registration order is load-bearing, so it is checked."""
    app = create_app()
    shadowed = []
    for route in _routes(app):
        # Only routes with a literal segment can be shadowed; a fully variable
        # path is the fallback rather than the victim.
        segments = route.path.strip("/").split("/")
        if not any(s and not s.startswith("{") for s in segments):
            continue
        url = _sample(route.path)
        for method in sorted(route.methods - {"HEAD", "OPTIONS"}):
            won = _winner(app, url, method)
            if won is not None and won is not route:
                shadowed.append(
                    f"{method} {route.path} is answered by {won.path}")
    assert not shadowed, "shadowed routes:\n  " + "\n  ".join(shadowed)


def test_a_planted_shadow_is_caught():
    """The check is only worth having if it fails when it should.

    A variable route registered ahead of a literal one is exactly the mistake
    the test exists for, so it is made on purpose here and the detection is
    asserted rather than assumed.
    """
    from fastapi import FastAPI
    bad = FastAPI()

    @bad.get("/things/{thing_id}")
    def by_id(thing_id: str):            # registered first — swallows the next
        return {"id": thing_id}

    @bad.get("/things/special")
    def special():
        return {"special": True}

    literal = [r for r in _routes(bad) if r.path == "/things/special"][0]
    assert _winner(bad, "/things/special", "GET") is not literal


def test_the_two_that_already_bit_us_stay_fixed(client):
    """Named, because a general check does not say which cases taught it."""
    app = create_app()
    for path, method in (("/profiles/{profile_id}/wall", "GET"),
                         ("/surfaces/{surface}/{surface_id}/skill-grants", "GET"),
                         ("/exchanges/vocabulary", "GET"),
                         ("/skill-grants/vocabulary", "GET"),
                         ("/profiles/{profile_id}/friends/suggested", "GET")):
        # Matched on path *and* method: several of these paths carry a GET and
        # a POST, and selecting the first by path alone compares a GET request
        # against the POST handler and fails for no reason.
        route = [r for r in _routes(app)
                 if r.path == path and method in r.methods]
        assert route, f"{method} {path} is gone — update this test"
        assert _winner(app, _sample(path), method) is route[0], path
