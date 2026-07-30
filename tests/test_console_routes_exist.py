"""Every path the console calls must resolve to a route that exists.

The Wall's like, comment and share buttons were dead in the field for as long
as they had existed. The console asked for ``/post/{id}/like``; the audience
routes take the *path segment* and map it to a kind (``posts`` → ``post``), so
the singular reached the generic ``/{kind}/{target_id}/like`` route, which then
refused the unknown segment with a 404.

Nothing caught it. The backend tests exercised ``/posts/…`` and passed, the
console compiled because a template literal is only a string, and the button
looked fine until somebody pressed it. That is the gap this closes: the two
halves are checked against each other rather than each against itself.

Extraction and matching live in :mod:`tests.clientpaths`, shared with the
native-shell guard — the same question in four languages.
"""

from __future__ import annotations

import re

from qrme.api import app

from . import clientpaths
from .clientpaths import CONSOLE, normalise, paths, resolves

API_TS = clientpaths.REPO / "app" / "src" / "api.ts"
_COMMENTS = re.compile(r"//[^\n]*|/\*.*?\*/", re.S)


def test_every_console_call_reaches_a_route():
    """Method and path together, for every `req(...)` the console makes.

    Checking the path alone accepts a client sending POST where only GET is
    mounted. That is a 405, and from the user's side it is the same dead button
    as a 404 — so the assertion is a FULL router match, not a partial one.

    Scoping to enclosing calls is what makes that possible, and it also fixes a
    false positive: `"/app"` is a path-shaped literal in `defaultBase()`, where
    the console asks whether `window.location.pathname` starts with it. That is
    a question about where the page is served, not a request.

    Worth knowing the limit that remains: this would *not* have caught the Wall
    bug. The singular `/post/x/like` matches the generic
    `/{kind}/{target_id}/like` route perfectly well, and the 404 is raised
    inside the handler when the segment fails the kind lookup. Routing-level
    checks cannot see refusals that happen after dispatch — which is why the
    tests below assert the segment itself, and send the request.
    """
    bad = clientpaths.refused(app, CONSOLE)
    assert not bad, (
        "the console makes these requests and no route accepts them:\n  "
        + "\n  ".join(bad)
        + "\n(a 404 or 405 the user meets as a button that does nothing)"
    )


def test_an_interpolated_query_does_not_truncate_the_path():
    """The guard's own blind spot, pinned so it cannot come back.

    This test used to cut a literal at its first interpolation whenever a query
    followed, on the theory that the query was interpolated. That is true of
    `?tag=${tag}`, where the path ends before the `?` anyway — and false of
    `/profiles/${id}/media?filename=${…}`, where cutting there leaves
    `/profiles`. A prefix that resolves is worse than one that does not: the
    check passes and the tail it was meant to verify is never looked at. Both
    of QRME's such paths — the adult feed and the 0.16.0 media upload — were
    being checked as bare `/profiles`.

    So the fixture is the real shape rather than a toy: whatever else changes,
    a path must survive an interpolation that precedes its query.
    """
    assert normalise("/profiles/${id}/media?filename=${f}", CONSOLE) == (
        "/profiles/x/media"
    )
    assert normalise("/meds/${uid}/adherence?days=${d}", CONSOLE) == (
        "/meds/x/adherence"
    )
    # The optional-parameter idiom is the one interpolation that *is* the query.
    assert normalise('/profiles/${id}/feed${adult ? "?adult=true" : ""}',
                     CONSOLE) == "/profiles/x/feed"
    # And a plain interpolated query still ends where it always did.
    assert normalise("/marketplace/listings?tag=${tag}", CONSOLE) == (
        "/marketplace/listings"
    )

    # The two that were being skipped are now really in the set, and resolve.
    found = paths(CONSOLE)
    for path in ("/profiles/x/feed", "/profiles/x/media"):
        assert path in found, f"{path} is still not reaching the guard"
        assert resolves(app, path), f"{path} reaches no route"


def test_the_check_is_really_method_aware():
    """Pinned against the live app, so it cannot quietly relax to path-only.

    The earlier version of this guard accepted a partial router match — path
    right, method ignored. That passes a client sending PUT where only POST is
    mounted, which answers 405 and looks to the user exactly like the 404 the
    guard exists to prevent. Asserting a real verb difference on a real route is
    what keeps the distinction alive; asserting it on a fixture would not.
    """
    assert clientpaths.accepts(app, "POST", "/interactors")
    assert not clientpaths.accepts(app, "PUT", "/interactors")
    assert clientpaths.methods_for(app, "/interactors") == ["POST"]

    # And every call the console makes is recorded with a verb, not a bare path.
    made = clientpaths.calls(CONSOLE)
    assert made, "no console calls were extracted at all"
    verbs = {method for method, _ in made}
    assert verbs <= set(clientpaths.VERBS), f"unexpected verbs: {verbs}"
    assert {"GET", "POST"} <= verbs, (
        f"the console surely does more than {verbs} — the verb reader has "
        "probably stopped matching"
    )


def test_the_wall_buttons_use_the_mapped_segment():
    """The specific regression, both directions.

    `_KIND_BY_PATH` maps a plural path segment to a singular kind, so `/posts/`
    is the reachable form and `/post/` is not. Asserting both keeps a future
    rename from quietly re-breaking one side.
    """
    from qrme.routers.audience import _KIND_BY_PATH

    assert "posts" in _KIND_BY_PATH and _KIND_BY_PATH["posts"] == "post"
    assert "post" not in _KIND_BY_PATH

    text = API_TS.read_text(encoding="utf-8")
    for verb in ("like", "comments", "share"):
        assert f"`/posts/${{postId}}/{verb}`" in text, (
            f"api.ts should call /posts/…/{verb} — the plural segment is the "
            "one the audience routes map to a kind"
        )
        assert f"`/post/${{postId}}/{verb}`" not in text, (
            f"api.ts calls the singular /post/…/{verb}, which 404s"
        )


def test_the_console_never_uses_a_singular_mapped_segment():
    """The whole class, not just the Wall.

    Nine routes dispatch on a leading `{kind}` — like, comments, share,
    subscribe, subscribers, audience, gift, gifts — and each rejects an
    unrecognised segment from inside the handler. Every one of them is a
    silent-404 waiting to happen if a caller reaches for the singular, so the
    singular of each mapped segment is banned outright rather than checked
    route by route.
    """
    from qrme.routers.audience import _KIND_BY_PATH

    text = _COMMENTS.sub("", API_TS.read_text(encoding="utf-8"))
    offenders = []
    for plural, singular in _KIND_BY_PATH.items():
        # `/profile/${...}` and friends: the singular kind used as a path.
        if re.search(rf"`/{re.escape(singular)}/\$\{{", text):
            offenders.append(f"/{singular}/ (should be /{plural}/)")
    assert not offenders, (
        "api.ts uses singular segments the kind lookup will refuse:\n  "
        + "\n  ".join(offenders)
    )


def test_the_singular_form_really_does_fail(client, profile_id):
    """Proof the mapping is what makes the difference, not a typo elsewhere.

    Without this the test above is just a spelling rule; here the two paths are
    actually sent and the 404 is observed.
    """
    # The profile_id fixture already authenticates the client as this
    # profile's owner, so compose needs no headers of its own here.
    post = client.post(f"/profiles/{profile_id}/compose",
                       json={"topic": "the dock lights"})
    assert post.status_code == 201, post.text
    pid = post.json()["id"]
    assert client.get(f"/post/{pid}/comments").status_code == 404
    assert client.get(f"/posts/{pid}/comments").status_code == 200
