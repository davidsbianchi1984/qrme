"""The rule the record states, with something behind it at last.

`tests/field_labels_unmapped.txt` explains why 123 request-model fields kept
their identifiers, and the explanation is a good one:

    These are the rest: enum members a control sets, ids a client fills in
    from the resource it is already looking at, and flags a switch owns. A 422
    naming one of them is a client bug rather than something a person
    mistyped.

Then it states the condition under which a row stops being defensible:

    Map one when a form starts asking a person for it; the ceiling does not
    move up.

That sentence was the whole policy, and **nothing was checking it**. The
ceiling stops the list growing; it says nothing about a field already on the
list that a screen quietly grew an input for. The record would keep shrinking,
every test would stay green, and the field would sit there being asked for by
a form and named by an identifier in the refusal.

It had already happened twice. `app/src/screens/Blend.tsx` has asked a person
for **share** and **their…** since the blend screen was localized:

    <label>{tr("bld.share", lang)}
      <input type="number" min={1} max={9} value={pick.weight}
             onChange={(e) => setPick(c.profile_id, {weight: ...})} />

and posts both up in the request body. The form found ten words for the label
above the box and the refusal below it said `weight`.

## How a form asking for something is recognised

Two conditions, and the AND is the whole guard:

* the field is **bound to a form control** — it is the `value` or the target
  of the `onChange` of an `<input>`, `<textarea>` or `<select>`;
* the field is **a key in an object literal** in the same screen, which is
  what being sent in a request body looks like from the source.

Either half alone is noise. Screens are full of object literals — inline
styles, component state, table rows — so keys alone reported 37 fields, almost
none of which any person types into. Control bindings alone match local UI
state that never leaves the browser. A field that is both is one a person
fills in and the API then validates, which is exactly the population
`_FIELD_LABELS` exists for.
"""

from __future__ import annotations

import re
from pathlib import Path

from qrme import i18n
from tests.test_the_refusal_names_the_field_on_the_form import REPO, _declared
from . import ratchets

SCREENS = REPO / "app/src/screens"


def _controls(src: str) -> str:
    """Every form control's opening tag, run together.

    Taken as tags rather than lines because a control's `value` and its
    `onChange` are routinely three lines apart, and the binding is a property
    of the tag rather than of any one line of it.
    """
    return " ".join(re.findall(r'<(?:input|textarea|select)\b[^>]*>', src, re.S))


def _body_keys(src: str) -> set[str]:
    """Every object-literal key in the file.

    Deliberately not narrowed to the argument of an `api.*` call. A screen
    builds its payload in pieces — a `sources` list comprehension here, a
    spread there — and following that would be a parser. The narrowing that
    matters is the AND with :func:`_controls`, not this half.
    """
    return set(re.findall(r'^\s*(\w+):\s', src, re.M))


def _asked_for() -> dict[str, set[str]]:
    """Field → the screens whose forms ask a person for it."""
    out: dict[str, set[str]] = {}
    fields = _declared()
    for path in sorted(SCREENS.rglob("*.tsx")):
        src = path.read_text(encoding="utf-8")
        controls, keys = _controls(src), _body_keys(src)
        for field in fields:
            if field not in keys:
                continue
            bound = re.escape(field)
            if (re.search(rf'value=\{{[^}}]*\b{bound}\b', controls)
                    or re.search(rf'onChange=\{{[^}}]*\b{bound}\b', controls)):
                out.setdefault(field, set()).add(path.name)
    return out


# --- the rule ---------------------------------------------------------------

def test_a_field_a_form_asks_for_has_the_label_the_form_shows():
    """The record's own condition, enforced.

    A field here is one a person is typing into a box right now. Whatever was
    true of it when it was recorded — that a control set it, that a client
    filled it in — stopped being true the day a screen grew an input for it,
    and the refusal is now the one place in the product that calls it by a
    name the person cannot see anywhere.
    """
    unlabelled = {f: sorted(where) for f, where in _asked_for().items()
                  if f not in i18n._FIELD_LABELS}
    assert not unlabelled, "\n    ".join(
        [""] + [f"{f} — asked for by {', '.join(w)}, and the refusal that "
                f"names it has no label for it" for f, w in
                sorted(unlabelled.items())]
    ) + ("\n  A recorded field stops being recordable when a form starts "
         "asking for it. Give it the label the form shows.")


# --- the scan has to be able to see, and to fail ----------------------------

def test_the_scan_can_still_see_the_forms():
    """A guard nobody has watched fail is a guard nobody should trust, and a
    scan of an entire console reporting nothing is far likelier to be broken
    than to be good news — which is what a rewrite of either regex produces.
    """
    controls = sum(len(_controls(p.read_text(encoding="utf-8")))
                   for p in SCREENS.rglob("*.tsx"))
    assert controls > 10_000, (
        f"the control extractor matched {controls} character(s) across every "
        f"screen — it has stopped seeing form controls")
    assert len(_asked_for()) >= ratchets.floor("form.asked_for"), (
        f"only {len(_asked_for())} field(s) read as form-bound and sent — the "
        f"AND has stopped matching and this guard is checking nothing")


def test_the_scan_would_catch_the_next_one():
    """Driven against the shape of the two this round found, so the check is
    known to fire rather than assumed to."""
    src = '''
      const out = await api.createThing({
        aging_enabled: pick.aging_enabled,
      });
      <input value={pick.aging_enabled}
             onChange={(e) => setPick({ aging_enabled: e.target.value })} />
    '''
    assert "aging_enabled" in _body_keys(src)
    assert re.search(r'value=\{[^}]*\baging_enabled\b', _controls(src))
    assert "aging_enabled" not in i18n._FIELD_LABELS, (
        "this example field was labelled since the test was written — pick "
        "another unlabelled one, or the check proves nothing")


# --- the two it found -------------------------------------------------------

def test_the_blend_share_is_named_the_way_the_form_names_it():
    """`weight` — the number box under *share*, posted as `sources[].weight`.

    The nested `loc` is what a person actually gets back, so it is what the
    refusal is read out of here rather than a flat field name that would have
    passed without the screen's payload ever being shaped like this.
    """
    said = i18n.validation_message(
        [{"loc": ["body", "sources", 0, "weight"], "msg": "Field required"}],
        "de")
    assert "weight" not in said, said
    assert "Anteil an der Mischung" in said, said


def test_the_blend_aspect_is_named_the_way_the_form_names_it():
    said = i18n.validation_message(
        [{"loc": ["body", "sources", 0, "aspect"], "msg": "Field required"}],
        "ja")
    assert "aspect" not in said, said
    assert "その人の要素" in said, said


def test_both_labels_borrow_the_console_s_own_word():
    """Ported, not written twice — the same construction
    `test_the_form_and_the_refusal_use_the_same_words` holds the sign-up
    fields to, applied to the two this round mapped.

    Not an equality check: the form's label sits above a box in a row of them
    and can be a fragment — *share*, *their…* — where the refusal names the
    field in a sentence of its own and has to stand alone. What must hold is
    that the noun is the same one, in every language, so a reader matches the
    refusal to the box without translating between two vocabularies.
    """
    console = (REPO / "app/src/l10n.ts").read_text(encoding="utf-8")
    for field, key in (("weight", "bld.share"), ("aspect", "bld.their.label")):
        block = re.search(rf'"{re.escape(key)}":\s*\{{(.*?)\n  \}}',
                          console, re.S)
        assert block, f"the console no longer has {key}"
        for lang in i18n.SUPPORTED:
            shown = re.search(rf'\b{lang}:\s*"((?:[^"\\]|\\.)*)"',
                              block.group(1))
            assert shown, f"{key} lost its {lang} row"
            word = shown.group(1).strip(" ……").casefold()
            assert word in i18n.field_label(field, lang).casefold(), (
                f"the form says {shown.group(1)!r} for {field} in {lang} and "
                f"the refusal says {i18n.field_label(field, lang)!r}")
