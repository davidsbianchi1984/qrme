"""A client record is a claim about a route. Drive the route and check it.

`share` was on the collision record as *a double and an int*. The int was
`DesigneeRow.share` — a percent of a legacy's proceeds, real, correct. The
double was `CompositionSource.share`, and chasing it turned up something the
collision record had no way to say:

    public record CompositionSource(
        [property: JsonPropertyName("name")] string? Name,
        [property: JsonPropertyName("share")] double? Share);

`GET /profiles/{id}/composition` has never sent `name` or `share`. It sends
`source_profile_id`, `display_name`, `weight` and `aspect`. Both fields decode
to null on every response, and the Windows blend button —

    StatusText.Text = string.Join(" · ", (c.Sources ?? []).Select(x => x.Name));

— renders a row of separators with nothing between them. Nobody had run it.

Widening the question found the same disease in fourteen records: `avatar`
promising an `ai_badge` and a `likeness_of` that no route emits, `/pair`
reading `built` where the server says `console_built`, `/tutorial` hedged
across `chapters` *and* `lessons` because the author did not know which,
`/dock/where/{face}` typing `screen` as a string where the server sends an
integer.

    asked     do the names match
    mattered  did anybody ever run the route

## What this guard does

It reads the Windows client's GET bindings — `Send<T>(Get("/path"))` — drives
each one against a live app, and asserts that every `JsonPropertyName` in `T`
is a key the route actually returned. One level of nesting is followed, so a
card's row type is checked against the rows.

The assertion is one-directional on purpose. A record *omitting* a key the
route returns is fine — a client decodes what it needs. A record *declaring* a
key the route never sends is a promise to the reader that the wire does not
keep.

## The record beside it

Not every binding is reachable from a fixture with one profile and one
interactor: some need a hybrid, a verified badge, a live desk. Those land in
`wire_shapes_unverified.txt`, which is the honest statement that nothing has
checked them — ratcheted, so the unproven surface only shrinks.

Conditional keys go there too, named with the state that produces them:
`verification.level` is real and only appears once somebody has verified, and
a guard that cannot tell that apart from a fiction would be a guard nobody
could trust.
"""

import collections
import json
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
WINDOWS_CLIENT = REPO / "native/windows/ApiClient.cs"
RECORD = pathlib.Path(__file__).resolve().parent / "wire_shapes_unverified.txt"

_SRC = WINDOWS_CLIENT.read_text(encoding="utf-8")

# `Send<CompositionCard>(Get($"/profiles/{profileId}/composition"))`
_BINDING = re.compile(
    r'Send<([\w\[\]]+)\??>\(\s*Get\(\s*\$?"([^"]+)"', re.S)
# The closing paren stays inside the captured body. Without it the field regex
# below — which needs a `,` or `)` after the property name — silently drops the
# *last* field of every record, which is where `share`, `built` and `kinds` all
# happen to sit.
# A record ends at `);`, or at `)` before a body — the second shape is
# legal C# and reading past it swallows the record declared next.
_RECORD_BLOCK = re.compile(r'public record (\w+)\((.*?\))\s*[;{]', re.S)
_FIELD = re.compile(
    r'JsonPropertyName\("([\w_]+)"\)\]\s+([\w\[\]\?<>,\.\s]+?)\s+\w+\s*[,)]')


def _records() -> dict[str, list[tuple[str, str]]]:
    """Record name -> [(wire name, declared C# type)]."""
    out = {}
    for name, body in _RECORD_BLOCK.findall(_SRC):
        out[name] = [(n, t.strip().rstrip("?"))
                     for n, t in _FIELD.findall(body)]
    return out


def _bindings() -> list[tuple[str, str]]:
    """[(record name, path template)] for every GET the client makes."""
    return [(t.replace("[]", ""), p) for t, p in _BINDING.findall(_SRC)]


def _recorded() -> set[str]:
    """Rows, with trailing reasons stripped.

    A row's reason may wrap onto the next line — an indented `#` that is not a
    row of its own. Filtering on the *result* rather than on the raw line is
    what keeps a wrapped reason from counting as an empty row.
    """
    rows = (line.split("#")[0].strip()
            for line in RECORD.read_text(encoding="utf-8").splitlines())
    return {row for row in rows if row}


def _returned_keys(body) -> set[str] | None:
    """The keys a response actually carried, or None if it carried none."""
    if isinstance(body, dict):
        return set(body)
    if isinstance(body, list):
        seen = [set(x) for x in body if isinstance(x, dict)]
        return set().union(*seen) if seen else None
    return None


def _descend(body, key):
    """The value under `key`, unwrapped from a list, or None."""
    if isinstance(body, list):
        body = next((x for x in body if isinstance(x, dict)), None)
    if not isinstance(body, dict) or key not in body:
        return None
    return body[key]


def _shape_of(value) -> str:
    """The kind of thing a JSON value is — the coarsest fact a decoder needs."""
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "list"
    if isinstance(value, dict):
        return "object"
    return "null"


def _accepts(csharp: str, shape: str) -> bool:
    """Whether a C# type can decode a value of that shape.

    Coarse on purpose: this is not a type checker, it is the check that would
    have caught `kinds` declared `string[]` for a route that sends a map, and
    `screen` declared `string` for an integer. Both were present on the wire
    under the right name, so the name check above saw nothing wrong.
    """
    t = csharp.replace(" ", "")
    if shape == "null":
        return True                      # a null tells you nothing
    if t.endswith("[]") or t.startswith("List<") or t.startswith("IReadOnlyList<"):
        return shape == "list"
    if "Dictionary<" in t:
        return shape == "object"
    if t in {"string"}:
        return shape == "string"
    if t in {"bool"}:
        return shape == "bool"
    if t in {"int", "long", "double", "float", "decimal"}:
        return shape == "number"
    if t in {"JsonElement", "object"}:
        return True                      # deliberately untyped
    return shape == "object"             # a record decodes an object


def _wrong_types(record: str, body, recs, seen=()) -> list[str]:
    """Fields whose declared C# type cannot decode what the route sent."""
    if record not in recs or record in seen:
        return []
    if not isinstance(body, dict):
        if isinstance(body, list):
            body = next((x for x in body if isinstance(x, dict)), None)
        if body is None:
            return []
    out = []
    for wire, typ in recs[record]:
        if wire not in body:
            continue
        shape = _shape_of(body[wire])
        if not _accepts(typ, shape):
            out.append(f"{record}.{wire} is declared {typ} and arrives as a "
                       f"{shape}")
            continue
        nested = typ.replace("[]", "").split(".")[-1]
        out += _wrong_types(nested, _descend(body, wire), recs, seen + (record,))
    return out


def _mismatches(record: str, body, recs, seen=()) -> list[str]:
    """Wire names `record` declares that `body` did not carry."""
    if record not in recs or record in seen:
        return []
    got = _returned_keys(body)
    if got is None:
        return []
    out = []
    for wire, typ in recs[record]:
        if wire not in got:
            out.append(f"{record}.{wire}")
            continue
        nested = typ.replace("[]", "").split(".")[-1]
        out += _mismatches(nested, _descend(body, wire), recs,
                           seen + (record,))
    return out


_typed: dict[str, list[str]] = {}


def _drive(client, profile_id: str, interactor_id: str):
    """Every binding, driven. Yields (path template, record, mismatches|None).

    `None` means the fixture could not reach the route — those are the rows
    the ratcheted record accounts for.
    """
    recs = _records()
    subs = {"profileId": profile_id, "interactorId": interactor_id,
            "subjectId": profile_id, "holderId": profile_id,
            "ownerId": profile_id, "targetId": profile_id, "id": profile_id}
    for record, template in _bindings():
        if record not in recs:
            continue
        path = template
        for key, value in subs.items():
            path = path.replace("{" + key + "}", value)
        if "{" in path:
            yield template, record, None
            continue
        response = client.get(path)
        if response.status_code != 200:
            yield template, record, None
            continue
        try:
            body = response.json()
        except (ValueError, json.JSONDecodeError):
            yield template, record, None
            continue
        if _returned_keys(body) is None:
            yield template, record, None
            continue
        _typed[record] = _wrong_types(record, body, recs)
        yield template, record, _mismatches(record, body, recs)


# --- the guard ---------------------------------------------------------------

def test_no_client_record_promises_a_field_the_route_never_sends(
        client, profile_id, interactor_id):
    """The `CompositionSource.name` shape: a field that decodes to null on
    every single response, wired to a button, shipped."""
    loose = []
    for _, record, missing in _drive(client, profile_id, interactor_id):
        for row in missing or []:
            if row not in _recorded():
                loose.append(row)
    assert not loose, (
        "these client fields are not on the wire:\n    "
        + "\n    ".join(sorted(set(loose)))
        + "\n  The route was driven and did not return them. Correct the "
          "record to the shape the route actually has, or record the row "
          "with the state that produces it — recording is ratcheted.")


def test_no_client_record_declares_a_type_the_wire_cannot_decode(
        client, profile_id, interactor_id):
    """The name check above passes when a field is present under the right
    name and the wrong shape. `/wearables` sends `kinds` as a map of kind to
    where it is worn; the record declared `string[]`, so the whole call threw
    on Windows rather than losing one field."""
    loose = []
    for _, record, missing in _drive(client, profile_id, interactor_id):
        if missing is None:
            continue
        loose += _typed[record]
    assert not loose, (
        "these client fields cannot decode what the route sends:\n    "
        + "\n    ".join(sorted(set(loose))))


def test_the_unverified_record_only_shrinks():
    text = RECORD.read_text(encoding="utf-8")
    ceiling = int(re.search(r"^# ceiling: (\d+)$", text, re.M).group(1))
    assert len(_recorded()) <= ceiling, (
        f"{len(_recorded())} rows recorded, above the {ceiling} ceiling")


def test_every_recorded_row_names_a_field_that_exists():
    """A row for a field nobody declares any more is a reader being told to
    distrust a client that is fine."""
    declared = {f"{rec}.{wire}"
                for rec, fields in _records().items() for wire, _ in fields}
    stale = sorted(_recorded() - declared)
    assert not stale, (
        "these rows name fields the client no longer declares:\n    "
        + "\n    ".join(stale) + "\n  Strike them.")


# --- the scan has to be able to see, and to fail -----------------------------

def test_the_scan_reaches_a_real_share_of_the_bindings(
        client, profile_id, interactor_id):
    """A probe that reached nothing would report this client perfect, which is
    the most flattering possible way to be broken."""
    driven = [m for _, _, m in _drive(client, profile_id, interactor_id)
              if m is not None]
    assert len(driven) >= 30, (
        f"only {len(driven)} binding(s) were reachable — the fixture or the "
        f"extractor has stopped working")


def test_the_extractor_reads_the_bindings_and_the_records():
    """Counted against the sibling guard in
    `test_one_name_one_type_on_the_wire.py`, which reads the same file with a
    flat regex. A record-aware extractor that sees fewer wire names than the
    flat one is dropping fields — this caught exactly that, a closing paren
    eaten by the block regex, before it could report a clean client."""
    names = {wire for fields in _records().values() for wire, _ in fields}
    assert len(_bindings()) >= 150, len(_bindings())
    assert len(names) >= 490, len(names)

def test_no_extracted_record_swallowed_the_next_one():
    """The block regex is non-greedy, so an unbalanced paren anywhere would let
    one record's body run on into the next — and the fields would then be
    reported against the wrong record name, which reads as a real finding and
    is not one. Seen while injecting a deliberately malformed field to check
    this guard fires.
    """
    for name, body in _RECORD_BLOCK.findall(_SRC):
        assert "public record" not in body, name


def test_the_guard_would_catch_a_fictional_field():
    """Driven against the shape `CompositionSource` had, so the check is known
    to fire rather than assumed to."""
    recs = {"Card": [("sources", "Row[]")],
            "Row": [("display_name", "string"), ("share", "double")]}
    body = {"sources": [{"display_name": "Dana", "weight": 0.6}]}
    assert _mismatches("Card", body, recs) == ["Row.share"]


def test_the_guard_allows_a_record_to_decode_less_than_it_is_sent():
    """A client need not read every key. The defect is the other direction."""
    recs = {"Row": [("display_name", "string")]}
    body = {"display_name": "Dana", "weight": 0.6, "aspect": None}
    assert _mismatches("Row", body, recs) == []
