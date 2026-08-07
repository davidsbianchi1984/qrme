"""Kotlin declares nothing, and reads everything by name.

The Windows client says what it expects in records, and Swift in structs, so
0.56.4 through 0.56.8 could ask both of them the same question: is every
declared field a key the route sends, in a shape the declared type can decode.
Nineteen defects in C#, nine in Swift, every Swift one already fixed in C# and
never carried across.

The 0.56.8 changelog left Kotlin out with a hedge:

> *it parses `JSONObject` by hand rather than declaring shapes, so there is
> nothing to compare — which is either a reason it cannot have this defect, or
> the reason nobody would find it.*

It was the second one. This client declares nothing, but every line of it is
two claims at once:

    val o = JSONObject(request("/profiles/$id/wearables", token = token))
    val worn = o.optJSONObject("kinds_worn")

`"kinds_worn"` says the route sends that key. `optJSONObject` says it is an
object. Both can be wrong, and the way they go wrong here is worse than
elsewhere, because `org.json` does not throw:

* `optString` on a key the route never sends returns `""`;
* `optInt` on a string returns `0`;
* `optJSONArray` on an object returns `null`, and the `?:` beside it quietly
  substitutes an empty one.

A C# client with the wrong type throws and somebody sees a crash. This one
draws a screen with nothing on it, and that is the harder defect to notice —
so *no declarations* was never a reason it could not have this defect. It was
a reason it would never be found.

    asked     does the client declare the right shape
    mattered  does the client ask for the right thing

## What is checked

Every `suspend fun` that binds a `JSONObject` to the result of a GET, and each
key read **off that object by name** — not off a nested one, because
`worn.optString(k)` inside the same function is a claim about `kinds_worn`'s
contents rather than about the response.

Scalar accessors are held to the coercion `org.json` actually performs:
`optString` on a number or a boolean is a deliberate stringification and is
allowed. `optString` on an *object* or an *array* is not, and neither is
`optInt` on a string — those are the reads that return a plausible wrong
answer instead of failing.
"""

import json
import pathlib
import re

from .test_the_shape_the_client_expects import _returned_keys, _shape_of

REPO = pathlib.Path(__file__).resolve().parents[1]
ANDROID_CLIENT = (
    REPO / "native/android/app/src/main/java/app/qrme/studio/ApiClient.kt")
RECORD = pathlib.Path(__file__).resolve().parent / "android_keys_unverified.txt"

_SRC = ANDROID_CLIENT.read_text(encoding="utf-8")

# One entry per function, so a key read in one cannot be attributed to the
# route another one calls. Splitting on `suspend fun` alone was not enough:
# a plain `fun` helper sitting between two of them stayed in the preceding
# chunk, and because `o` is the conventional name for the decoded body here,
# its reads were credited to whatever route that chunk began with. The
# voiceprint route was accused of reading thirteen shop fields.
_FUNCTION = re.compile(r'\n    (?=(?:private )?(?:suspend )?fun )')
# The binding must be the *whole* response. `val f = JSONObject(request(...))
# .getJSONObject("funnel")` binds the funnel, and crediting its keys to the
# top level accused the placements route of three fields it never reads there.
# So: no chained accessor between the closing paren and the end of the line.
_BOUND = re.compile(
    r'val (\w+) = JSONObject\(\s*request\(\s*"([^"]+)"([^\n]*)')
# A binding whose statement chains straight into `.getJSONObject(...)` binds
# that nested object, not the response. Checked on the statement text rather
# than in the pattern above, because the chain often sits on the next line
# and a multi-line regex for it was wrong twice.
_CHAINED = re.compile(r'\)\s*\)\s*\.(?:opt|get)JSON')
_INLINE = re.compile(
    r'JSONObject\(\s*request\(\s*"([^"]+)"([^\n]*)\)\s*\)\s*\n?\s*'
    r'\.(opt\w+|get\w+)\(\s*"([\w_]+)"')

# What org.json will hand back without complaining.
ACCEPTS = {
    "optString": {"string", "number", "bool"},
    "getString": {"string"},
    "optInt": {"number"}, "getInt": {"number"},
    "optLong": {"number"}, "optDouble": {"number"}, "getDouble": {"number"},
    "optBoolean": {"bool"}, "getBoolean": {"bool"},
    "optJSONArray": {"list"}, "getJSONArray": {"list"},
    "optJSONObject": {"object"}, "getJSONObject": {"object"},
}


def _is_get(rest: str) -> bool:
    """Whether the call is a GET.

    This client passes the verb *positionally* — `request(path, "DELETE",
    null, token)` — so a check for the word `method` sees a GET. That is how
    the revoke-voiceprint and pair-wearable replies were read as though they
    were what `GET` of those paths returns.
    """
    return not any(v in rest for v in ('"POST"', '"PUT"', '"DELETE"',
                                       '"PATCH"'))


def _reads() -> list[tuple[str, list[tuple[str, str]]]]:
    """[(path template, [(accessor, key)])] for every GET this client reads."""
    out = []
    for body in _FUNCTION.split(_SRC):
        bound = _BOUND.search(body)
        if not bound:
            continue
        var, path, rest = bound.groups()
        if not _is_get(rest):
            continue
        if _CHAINED.search(body[bound.start():bound.start() + 240]):
            continue
        keys = re.findall(
            r'\b%s\.(opt\w+|get\w+)\(\s*"([\w_]+)"' % re.escape(var), body)
        if keys:
            out.append((path, keys))
    for path, rest, accessor, key in _INLINE.findall(_SRC):
        # `request("/feedback", "POST", body, token)` is not a GET, and the
        # key it reads off the *reply* to a write says nothing about what the
        # GET of that path returns.
        if not _is_get(rest):
            continue
        out.append((path, [(accessor, key)]))
    return out


def _recorded() -> set[str]:
    rows = (line.split("#")[0].strip()
            for line in RECORD.read_text(encoding="utf-8").splitlines())
    return {row for row in rows if row}


def _drive(client, profile_id: str, interactor_id: str):
    """Every readable GET, driven. Yields (path, findings|None)."""
    subs = {"id": profile_id, "profileId": profile_id, "pid": profile_id,
            "interactorId": interactor_id, "uid": interactor_id,
            "interactor": interactor_id}
    for template, keys in _reads():
        path = template
        for name, value in subs.items():
            path = path.replace("$" + name, value).replace(
                "${" + name + "}", value)
        if "$" in path or "{" in path:
            yield template, None
            continue
        response = client.get(path)
        if response.status_code != 200:
            yield template, None
            continue
        try:
            body = response.json()
        except (ValueError, json.JSONDecodeError):
            yield template, None
            continue
        if not isinstance(body, dict):
            yield template, None
            continue
        found = []
        # Rows name the route, not the id a fixture happened to mint.
        shown = re.sub(r'(prf|usr)_[0-9a-f]+', '{id}', path)
        for accessor, key in keys:
            if key not in body:
                found.append(f"{shown} reads {key!r} — not on the wire")
                continue
            shape = _shape_of(body[key])
            allowed = ACCEPTS.get(accessor)
            if allowed and shape not in allowed and shape != "null":
                found.append(f"{shown} reads {key!r} with {accessor} "
                             f"and it arrives as a {shape}")
        yield template, found


# --- the guard ---------------------------------------------------------------

def test_the_android_client_asks_for_what_the_route_sends(
        client, profile_id, interactor_id):
    """`org.json` does not throw. A key this client asks for and does not get
    is an empty string on a screen, which is the defect nobody reports."""
    loose = []
    for _, found in _drive(client, profile_id, interactor_id):
        for row in found or []:
            key = re.search(r"reads '([\w_]+)'", row).group(1)
            path = row.split(" reads ")[0]
            if f"{path} {key}" not in _recorded():
                loose.append(row)
    assert not loose, (
        "the Android client asks for these and the route disagrees:\n    "
        + "\n    ".join(sorted(set(loose)))
        + "\n  Read the key the route actually sends, with the accessor its "
          "type deserves — or record `<path> <key>` with the state that "
          "produces it. Recording is ratcheted.")


def test_the_unverified_record_only_shrinks():
    text = RECORD.read_text(encoding="utf-8")
    ceiling = int(re.search(r"^# ceiling: (\d+)$", text, re.M).group(1))
    assert len(_recorded()) <= ceiling, (
        f"{len(_recorded())} rows recorded, above the {ceiling} ceiling")


# --- the scan has to be able to see, and to fail -----------------------------

def test_the_extractor_reads_this_clients_calls():
    """Neither the C# nor the Swift pattern finds anything in a file that
    declares no shapes, and nothing found reads as nothing wrong."""
    reads = _reads()
    assert len(reads) >= 120, len(reads)
    assert sum(len(k) for _, k in reads) >= 200, sum(len(k) for _, k in reads)


def test_no_function_body_swallowed_the_next_one():
    """Third time this assertion is written, in the third language — and the
    first time the assertion itself was wrong. It counted `suspend fun` when
    the split needed to be on any `fun`, so a plain helper between two
    suspend functions kept its reads in the preceding chunk and passed this
    check while poisoning the results. Counting the thing you split on is the
    whole point."""
    for body in _FUNCTION.split(_SRC)[1:]:
        # Counting the thing the split matches: a declaration at this file's
        # member indent. A *local* `fun` nested inside one — this client has
        # `fun strings(key)` inside `exchangeVocabulary` — is part of that
        # body and not a boundary the split should have found.
        assert len(re.findall(r'^    (?:private )?(?:suspend )?fun ',
                              body, re.M)) <= 1, body[:160]


def test_the_scan_reaches_a_real_share_of_the_routes(
        client, profile_id, interactor_id):
    driven = [f for _, f in _drive(client, profile_id, interactor_id)
              if f is not None]
    assert len(driven) >= 25, (
        f"only {len(driven)} route(s) were reachable — the fixture or the "
        f"extractor has stopped working")


def test_the_guard_holds_org_json_to_the_coercions_it_actually_performs():
    """`optString` on a number is a deliberate stringification and is allowed.
    `optString` on an object is the read that returns a plausible wrong
    answer, and is not."""
    assert "number" in ACCEPTS["optString"]
    assert "object" not in ACCEPTS["optString"]
    assert "list" not in ACCEPTS["optString"]
    assert ACCEPTS["optInt"] == {"number"}
