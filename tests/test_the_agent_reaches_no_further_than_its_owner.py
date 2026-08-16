"""The Studio agent has the owner's reach and not the owner's authority.

## The distinction this file holds

An agent driven with an owner's token could call anything that owner can
call. That is true about authority and wrong about design: the owner can
also end their profile, and nobody typing *make my page darker* means *and
be free to delete me if you misread it*.

    asked     does the agent have the owner's authority
    mattered  does it have the owner's intent

So the reach is a list — `qrme/authoring.TOOLS` — and this file is what
makes the list load-bearing rather than decorative. Every row is resolved
against the app's own route table: a row naming a path that does not exist
fails here, and so does a row landing on a route that is not owner-scoped
on that profile.

## Why the host guard lives here too

The other way an agent widens is by being told more about where it runs.
Every person who signs up gets one of these, on a host that also holds
JIM-mini's clinical captures and PDI's tenant vaults, so the prompt is read
for hostnames, paths, environment variables and service names — in the
system text *and* in the sentences written for people, because a leak is as
likely to arrive in prose as in a prompt.
"""
from __future__ import annotations

import inspect
import re

import pytest

from qrme import authoring
from qrme.api import app

from . import clientpaths


def _routes() -> dict[tuple[str, str], object]:
    """Every route the app actually serves, by (method, path).

    Through `clientpaths.all_routes` rather than `app.routes`, which is not
    the flat list it looks like: FastAPI wraps each `include_router` in an
    `_IncludedRouter` that carries no path of its own, so the top level sees
    a handful of routes against the app's real couple of hundred. A registry
    resolved against that shorter list would fail on rows that are perfectly
    real — and, worse, would keep passing rows that had quietly stopped
    being.
    """
    found: dict[tuple[str, str], object] = {}
    for route in clientpaths.all_routes(app):
        for method in (route.methods or set()) - {"HEAD", "OPTIONS"}:
            found[(method, route.path)] = route
    return found


def test_every_tool_names_a_route_that_exists():
    """A row that names nothing is a promise the console renders and the
    agent cannot keep."""
    served = _routes()
    missing = [tool["name"] for tool in authoring.TOOLS
               if tuple(tool["route"]) not in served]
    assert not missing, (
        f"{missing} name routes this app does not serve — either the path "
        "moved and the registry did not, or the row was written from memory")


def test_every_tool_that_changes_something_goes_through_the_owner_s_door():
    """The guard the registry exists for.

    Owner scope is read from the handler's own source rather than trusted: a
    route in this list that stopped requiring the owner is exactly the kind
    of change that looks harmless in a diff about something else. Both of
    the estate's idioms count — `require_owner` and the `auth.require` call
    it wraps — because which one a router happens to use is a fact about its
    age, not about how guarded it is.

    Matched on a word boundary, and that is the whole of the difference
    between this check working and this check being decorative. `in source`
    was the first version, and this estate also has `require_owner_or_
    interactor` — a *weaker* door, admitting anybody the profile is talking
    to — which contains the string `require_owner` and read as passing. The
    round that widened the roster to forty-one rows had a rehearsal route on
    its shortlist protected by exactly that, and it would have gone in under
    a green suite.

        asked     does the handler mention the owner
        mattered  does the handler require the owner

    Reads are exempt on purpose. `GET .../page` is what a visitor sees and
    has no owner to demand; what keeps the agent from reading a stranger's
    is not that door but `call`, which fills the profile in from the session
    — which is why the next test is not optional.
    """
    served = _routes()
    astray = []
    demands = re.compile(r'\brequire_owner\b|"owner"')
    for tool in authoring.TOOLS:
        if not tool["writes"]:
            continue
        source = inspect.getsource(served[tuple(tool["route"])].endpoint)
        if not demands.search(source):
            astray.append(f"{tool['name']} -> {tool['route'][0]} "
                          f"{tool['route'][1]}")
    assert not astray, (
        "these tools change something through a route that does not require "
        "the owner of that profile:\n    " + "\n    ".join(astray)
        + "\n  An agent anybody can drive must not hold a door somebody "
          "else's session can walk through.")


def test_the_model_never_says_whose_profile_it_is():
    """The reach guarantee, and the reason a read may go through a public
    door.

    The profile is bound from the session by `call`. A model that answers
    `{"profile_id": "<somebody else>"}` — because it was asked to, or
    because it read those words in a page it was handed — must not be able
    to move the request off the person driving it.
    """
    seen = {}

    def _spy(app, method, path, body, headers):
        seen.update(method=method, path=path, body=body)
        return 200, {}

    original = authoring._request
    authoring._request = _spy
    try:
        authoring.call("read_widget",
                       {"profile_id": "someone-else", "widget_id": "w1"},
                       app=None, profile_id="mine", authorization=None)
        assert seen["path"] == "/profiles/mine/widgets/w1", seen["path"]

        authoring.call("edit_page", {"profile_id": "someone-else",
                                     "tagline": "hi"},
                       app=None, profile_id="mine", authorization=None)
        assert seen["path"] == "/profiles/mine/page", seen["path"]
        assert "profile_id" not in seen["body"], (
            "the model's profile survived into the body, where a route that "
            "reads one from the body would honour it")
    finally:
        authoring._request = original


def test_a_path_the_model_supplied_stays_one_segment():
    """`{widget_id}` does come from the model. Everything it puts there is
    escaped, so `../` is a widget nobody has rather than a route nobody
    meant to expose."""
    seen = {}
    original = authoring._request
    authoring._request = lambda app, method, path, body, headers: (
        seen.update(path=path) or (200, {}))
    try:
        authoring.call("read_widget", {"widget_id": "../../profiles/them"},
                       app=None, profile_id="mine", authorization=None)
        assert seen["path"] == (
            "/profiles/mine/widgets/..%2F..%2Fprofiles%2Fthem"), seen["path"]
    finally:
        authoring._request = original


_WORDS = {
    "eleven": 11, "twelve": 12, "twenty": 20, "thirty": 30, "forty": 40,
    "fifty": 50, "sixty": 60,
}


def test_the_lesson_names_the_number_of_tools_there_actually_are():
    """The lesson tells somebody how far this thing reaches before they use
    it, and it says so as a number. A count in prose is the part that goes
    stale first — this list grew from eleven to forty-three in one round, and
    the sentence describing it did not move on its own.

        asked     does the lesson describe the agent
        mattered  does it still describe this agent
    """
    from qrme import tutorial

    lesson = tutorial.LESSONS[tutorial._index("agent")]
    said = re.search(
        r"list of ((?:" + "|".join(_WORDS) + r")(?:-\w+)?|\d+) tools",
        lesson["what"])
    assert said, (
        "the Agent lesson no longer says 'list of N tools'. That phrase is "
        "what a person reads to know how far this reaches, and this guard is "
        "the only thing keeping it honest — so it is part of the contract.")
    word = said.group(1)
    if word.isdigit():
        count = int(word)
    else:
        tens, _, units = word.partition("-")
        count = _WORDS[tens] + (_WORDS.get(units, 0) if units else 0)
        if units:
            count = _WORDS[tens] + {"one": 1, "two": 2, "three": 3, "four": 4,
                                    "five": 5, "six": 6, "seven": 7,
                                    "eight": 8, "nine": 9}[units]
    assert count == len(authoring.TOOLS), (
        f"the lesson says {count} tools and the roster holds "
        f"{len(authoring.TOOLS)}")


def test_the_guard_on_the_owner_door_can_tell_two_doors_apart():
    """A guard on the guard, written the day the substring version was found.

    `require_owner_or_interactor` is a real function in this estate and a
    weaker door than `require_owner`. If the pattern above ever goes back to
    a substring, this is what says so.
    """
    demands = re.compile(r'\brequire_owner\b|"owner"')
    assert demands.search("    require_owner(profile_id, request)")
    assert demands.search('    auth.require(request, "owner", profile_id)')
    assert not demands.search(
        "    require_owner_or_interactor(profile_id, who, request)"), (
        "the owner-door check cannot tell `require_owner` from "
        "`require_owner_or_interactor`, which lets anybody the profile is "
        "talking to through a door this list says is the owner's")


# --- a door wider than the intent behind reaching for it --------------------

def test_a_narrowed_row_names_fields_the_door_actually_takes():
    """`only` is a claim about a request body, and a claim nobody checks is a
    typo waiting to be a hole. Every field named has to be one the door's own
    model accepts, or the row is narrowing something that was never there."""
    from qrme import models

    bodies = {("PATCH", "/profiles/{profile_id}"): models.ProfileUpdate}
    for tool in authoring.TOOLS:
        if not tool.get("only"):
            continue
        model = bodies.get(tuple(tool["route"]))
        assert model is not None, (
            f"{tool['name']} narrows a door this test does not know the body "
            "of — add it to `bodies` so the field names stay checked")
        unknown = sorted(set(tool["only"]) - set(model.model_fields))
        assert not unknown, (
            f"{tool['name']} says it sets {unknown}, which "
            f"{model.__name__} has no such field for — a narrowing that "
            "narrows nothing")


def test_the_profile_door_is_narrowed_because_it_is_wider_than_it_looks():
    """The reason `only` exists at all, pinned to the fields that made it
    necessary. `PATCH /profiles/{id}` is how somebody renames their profile
    and rewrites its persona; it is also how they name who inherits it and
    mark it adult. The row takes the first two.

        asked     is this door the owner's
        mattered  is this door the sentence the person typed
    """
    from qrme import models

    only = authoring._only("edit_persona")
    assert only == ("display_name", "persona"), only
    for consequential in ("successor_owner", "maturity", "moderation_mode",
                          "cloud_contribution"):
        assert consequential in models.ProfileUpdate.model_fields, (
            f"{consequential} is gone from the door — if it moved, this row's "
            "narrowing may no longer be pointed at anything")
        assert consequential not in only, (
            f"the agent can set {consequential} from a sentence")


@pytest.mark.parametrize("astray", ["successor_owner", "maturity",
                                    "cloud_contribution"])
def test_a_field_outside_the_row_is_refused_rather_than_dropped(astray):
    """Refused, not filtered.

    Dropping it silently would leave the model free to report a change that
    did not happen — *I've marked your profile adult* over a profile that is
    not — and the reply is the part a person takes on trust. A refusal is a
    turn in the conversation and reaches the screen as a step that did not
    run.
    """
    reached = []
    original = authoring._request
    authoring._request = lambda *a, **k: (reached.append(a) or (200, {}))
    try:
        with pytest.raises(authoring.AgentError) as refusal:
            authoring.call("edit_persona",
                           {"persona": "warmer", astray: "somebody-else"},
                           app=None, profile_id="mine", authorization=None)
        assert str(refusal.value) == "agent.field_not_yours"
        assert not reached, (
            "the request went out anyway — the check has to happen before "
            "the door, not after it")
    finally:
        authoring._request = original


def test_the_fields_a_narrowed_row_does_take_still_go_through():
    """The other half. A narrowing that refused everything would pass the
    test above and break the feature."""
    seen = {}
    original = authoring._request
    authoring._request = lambda app, method, path, body, headers: (
        seen.update(body=body, path=path) or (200, {}))
    try:
        authoring.call("edit_persona",
                       {"display_name": "Rosa", "persona": "keeps bees"},
                       app=None, profile_id="mine", authorization=None)
        assert seen["body"] == {"display_name": "Rosa",
                                "persona": "keeps bees"}, seen["body"]
        assert seen["path"] == "/profiles/mine"
    finally:
        authoring._request = original


def test_the_roster_tells_the_model_which_fields_a_narrowed_row_takes():
    """A limit the model discovers by being refused is a limit it spends a
    step on. The roster is the only place it can be told first."""
    said = authoring.roster()
    assert "sets only: display_name, persona" in said, said


def test_the_tools_are_scoped_to_one_profile():
    """Every row acts on a named profile. A tool whose path has no
    `{profile_id}` acts on something that is not somebody's own."""
    loose = [tool["name"] for tool in authoring.TOOLS
             if "{profile_id}" not in tool["route"][1]]
    assert not loose, (
        f"{loose} act on a route with no profile in it, so 'their own' is "
        "not a thing the path can express")


def test_nothing_that_ends_or_bills_or_unlocks_is_in_reach():
    """Refused by absence rather than by a check, and named here so the
    absence is deliberate rather than an oversight nobody noticed."""
    paths = {tool["route"][1] for tool in authoring.TOOLS}
    methods = {(tool["route"][0], tool["route"][1]) for tool in authoring.TOOLS}
    for forbidden in ("/memberships", "/plans", "/keys", "/moderation",
                      "/objections", "/messages", "/exit", "/erase"):
        touching = sorted(p for p in paths if forbidden in p)
        assert not touching, (
            f"the agent can reach {touching} — ending, billing, key material, "
            "moderation and messaging other people are not what 'edit my own "
            "app' means")
    assert ("DELETE", "/profiles/{profile_id}") not in methods, (
        "the agent can delete the profile it was asked to decorate")


def test_every_tool_says_what_it_does_in_a_sentence_a_person_reads():
    """The list is shown to somebody before they let this near anything, so
    a row without a sentence is a row they cannot consent to."""
    silent = [tool["name"] for tool in authoring.TOOLS
              if not tool.get("says", "").strip()]
    assert not silent, f"{silent} have nothing to say for themselves"
    assert len(authoring.what_it_can_touch()) == len(authoring.TOOLS)


def test_a_name_the_model_invented_is_not_a_tool():
    """The lookup is membership, not interpolation. A model that answers
    with `delete_profile` gets a refusal rather than a request."""
    assert authoring.is_a_tool("edit_page")
    for invented in ("delete_profile", "edit_page; drop table", "",
                     "../../etc/passwd", "EDIT_PAGE", "read_page "):
        assert not authoring.is_a_tool(invented), (
            f"{invented!r} was accepted as a tool name")


def test_the_agent_is_told_nothing_about_the_host():
    """The prompt is the other way an agent widens.

    Every person who signs up drives one of these, on a machine that also
    holds JIM-mini's clinical captures and PDI's tenant vaults. What the
    agent knows about that machine is nothing, and this is what keeps it
    nothing when somebody later tries to make it more helpful.
    """
    leaked = authoring.mentions_the_host(authoring.SYSTEM)
    assert not leaked, (
        f"the agent's own instructions name {leaked} — an agent that knows "
        "the host is a map of it, handed to whoever is driving")
    for tool in authoring.TOOLS:
        said = authoring.mentions_the_host(tool["says"])
        assert not said, (
            f"{tool['name']}'s sentence names {said}; the words a person "
            "reads reach the model too")


def test_the_host_guard_can_still_see():
    """A guard on the guard. If the word list stopped matching, every check
    above would pass on a prompt full of hostnames."""
    assert authoring.mentions_the_host("we run on nginx at /var/qrme")
    assert authoring.mentions_the_host("set QRME_ADMIN_TOKEN first")
    assert not authoring.mentions_the_host(
        "you help one person change their own profile")


def test_the_agent_is_told_what_a_widget_cannot_do():
    """The most likely wrong answer this thing can give is a widget that
    fetches something, written confidently, that fails in the box. The
    instructions have to say so before somebody asks."""
    said = authoring.SYSTEM.lower()
    assert "no network" in said and "cannot reach the network" in said, (
        "the agent is not told that a widget has no network, so it will "
        "write one that does and hand somebody code that cannot work")
