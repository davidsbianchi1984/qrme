"""The screen was in ten languages and the answers were in one.

## The finding

`test_the_stranger_has_a_language_too.py` fixed the accountless screen's
*frame*: `navigator.languages` is read, twenty-four sentences are in ten
languages, and the only English left on `Public.tsx` is the brand name.

Every sentence the **server** contributes to that page was still English, and
`qrme/i18n.py` says why in its own signature — `get_language(profile_id)`.
The reader of that screen has no profile. That module could not have answered
them even if something had asked it to.

So a visitor in Osaka got a Japanese page, pasted in a piece of text, pressed
a Japanese button, and was told in English:

    no stamped work shares any wording with this text

which is the answer to the only question they came with. Alongside it:
`profile restricted pending review; the owner must re-attest their rights
basis` after opening an objection, the consistency `guarantee`, the
synthetic-media `disclosure`, the recovery `method`, and every refusal —
`profile not found`, `objection not found`.

The audit's recurring shape, one layer in from the round that localized the
screen:

    asked     is the surface localized
    mattered  is the answer

## The state words are deliberately not translated

`status`, `profile_status` and `prior_status` come back in the API's own
vocabulary. The first version of this round translated them too, and driving
it caught what that costs: `Contest.tsx` reads `status.status === "open"` to
decide whether to show the card that lets a standing party end a case
immediately, so a Japanese browser would have made that card disappear from a
signed-in screen. What a person reads is translated; what a client compares
is not. `Public.tsx` translates them for display through `pub.state.*`, which
is where a display decision belongs.

## What this file checks

It drives the four public routes with an `Accept-Language` header and asks
whether anything English came back. Derived from `_PUBLIC` rather than
listed, so a sentence added to one of these routes next year is covered the
day somebody translates it, and fails loudly the day they do not.
"""

from __future__ import annotations

import pytest

from qrme import i18n, watermark

#: Everything but English. Read from the module so a tenth language cannot
#: leave this behind.
OTHERS = tuple(code for code in i18n.SUPPORTED if code != i18n.DEFAULT)

#: A passage long enough for the five-word windows to have something to
#: overlap on. The recovered branch is a different page to the reader — it is
#: the one that names an author — and a fixture that never produces it leaves
#: `disclosure`, `method` and `state` untested, which is the same
#: branch-shaped gap that let one of JIM's two foot paragraphs stay English.
PASSAGE = (
    "The garden was my grandmother's before it was mine, and she kept the "
    "roses along the south fence because that is where the light lingers "
    "longest in the afternoon. She never wrote any of it down."
)

#: The values that are the API's vocabulary rather than prose. Excluded from
#: the "nothing English survives" sweep because they are *supposed* to come
#: back in English — see the module docstring.
#: `state` is deliberately *not* here. On a watermark it is "unaltered" or
#: "altered but traceable" — prose the screen prints in bold, and nothing in
#: any client compares it. The objection states are the ones a client reads.
MACHINE_KEYS = frozenset({"status", "profile_status", "prior_status", "kind",
                          "id", "profile_id", "watermark_id", "issued_at",
                          "objection_id", "objector_ref", "signature", "name",
                          "mark", "label"})


def _public_answers(client, profile_id: str, language: str) -> list:
    """Everything the four accountless routes say, in one language."""
    head = {"Accept-Language": language} if language else {}
    watermark.stamp(profile_id, "post", PASSAGE)
    said = []

    said.append(("recover, nothing",
                 client.post("/watermarks/recover", json={"content": ""},
                             headers=head).json()))
    said.append(("recover, recovered",
                 client.post("/watermarks/recover", json={"content": PASSAGE},
                             headers=head).json()))
    said.append(("recover, edited but traceable",
                 client.post("/watermarks/recover",
                             json={"content": PASSAGE.replace(
                                 "grandmother's", "grandmothers")},
                             headers=head).json()))
    said.append(("recover, no match",
                 client.post("/watermarks/recover",
                             json={"content": "an unrelated sentence that "
                                              "nobody here has ever stamped"},
                             headers=head).json()))
    said.append(("same profile",
                 client.get(f"/profiles/{profile_id}/embodiment-consistency",
                            headers=head).json()))
    said.append(("same profile, unknown",
                 client.get("/profiles/prf_nothing/embodiment-consistency",
                            headers=head).json()))
    opened = client.post("/objections",
                         json={"profile_id": profile_id,
                               "objector_ref": "id-check-42"},
                         headers=head)
    said.append(("objection opened", opened.json()))
    if opened.status_code < 300:
        said.append(("objection status",
                     client.get(f"/objections/{opened.json()['id']}",
                                headers=head).json()))
    said.append(("objection unknown",
                 client.get("/objections/obj_nothing", headers=head).json()))
    return said


def _sentences(payload) -> list[str]:
    """Every string in a response that is not the API's own vocabulary."""
    out: list[str] = []

    def walk(node, key=None):
        if isinstance(node, dict):
            for k, v in node.items():
                walk(v, k)
        elif isinstance(node, list):
            for v in node:
                walk(v, key)
        elif isinstance(node, str) and key not in MACHINE_KEYS:
            out.append(node)

    walk(payload)
    return out


def test_no_english_survives_on_a_public_answer(client, profile_id):
    """The check that would have failed before this round, on every route.

    Derived: any sentence the English run produced that is in the table must
    be gone from the translated run.
    """
    # `profile_id` authenticates the client as the owner; these routes take no
    # credential and must be exercised without one, the way a stranger meets
    # them.
    client.headers.pop("authorization", None)

    english = {label: _sentences(body)
               for label, body in _public_answers(client, profile_id, "en")}
    left = []
    for language in OTHERS:
        for label, body in _public_answers(client, profile_id, language):
            for said in _sentences(body):
                if said not in i18n._PUBLIC:
                    continue
                if said in english.get(label, []):
                    left.append(f"{language} / {label}: {said[:56]!r}")
    assert not left, (
        "these public routes still answer in English for somebody whose "
        "browser asked for another language:\n    " + "\n    ".join(left)
        + "\n  The caller of these four has no account by construction, so "
          "there is no stored preference to fall back to — English here is "
          "not a default, it is a guess about who is asking.")


def test_every_sentence_a_public_route_says_is_in_the_table(client,
                                                            profile_id):
    """The mirror, and the one that finds a sentence nobody has translated.

    A route that grows a new explanatory string ships it in English to every
    reader in the world, silently, and no amount of adding translations helps
    because nothing looks it up. This is what noticed that the recovery
    `method` and the consistency `guarantee` were never in any table.
    """
    client.headers.pop("authorization", None)
    missing = []
    for label, body in _public_answers(client, profile_id, "en"):
        for said in _sentences(body):
            # Ids, names, timestamps and single words are not prose. The bar
            # is a sentence: something with a space in it and some length.
            if len(said) < 18 or " " not in said:
                continue
            if said not in i18n._PUBLIC:
                missing.append(f"{label}: {said[:70]!r}")
    assert not missing, (
        "these sentences are said to somebody with no account and are not in "
        "`qrme.i18n._PUBLIC`, so every reader outside the anglosphere gets "
        "them in English:\n    " + "\n    ".join(sorted(set(missing))))


def test_the_table_is_complete_in_every_language():
    """Ten or none. A half-translated answer reads as broken software rather
    than as software in another language, and the reader is deciding whether
    to believe something about their own likeness."""
    ragged = {text: sorted(set(OTHERS) - set(row))
              for text, row in i18n._PUBLIC.items()
              if set(OTHERS) - set(row)}
    assert not ragged, (
        "these public sentences are missing languages:\n    "
        + "\n    ".join(f"{t[:44]!r}: {m}" for t, m in sorted(ragged.items())))


def test_the_state_words_stay_in_the_apis_vocabulary(client, profile_id):
    """The mistake this round made first, kept from coming back.

    Translating `status` server-side would hide `Contest.tsx`'s "End it now"
    card — the shortcut a subject or an estate uses to terminate a profile
    without waiting out a review — from every non-English browser. It is a
    signed-in screen, so nothing on the accountless surface would have shown
    it, and the console would simply have been missing a control.
    """
    client.headers.pop("authorization", None)
    opened = client.post("/objections",
                         json={"profile_id": profile_id, "objector_ref": "r"},
                         headers={"Accept-Language": "ja"})
    assert opened.status_code == 201, opened.text
    body = opened.json()
    assert body["status"] == "open", (
        f"the objection's status came back as {body['status']!r} — "
        "`Contest.tsx` compares this against the literal \"open\"")
    assert body["profile_status"] == "restricted"
    assert body["prior_status"] in ("active", "departed")

    for word in ("open", "restricted", "active"):
        assert word not in i18n._PUBLIC, (
            f"{word!r} is back in the server's table; it is a value a client "
            "compares, and `Public.tsx` translates it for display through "
            "`pub.state.*` instead")


@pytest.mark.parametrize("header,expected", [
    ("ja-JP,en;q=0.4", "ja"),
    ("es-419", "es"),                      # region dropped
    ("tlh,fr", "fr"),                      # unknown tags skipped
    ("fr;q=0.3,de;q=0.8", "de"),           # q honoured
    ("fr,es", "fr"),                       # equal q keeps header order
    ("ar;q=0", "en"),                      # q=0 means not this one
    ("ZH-hans", "zh"),                     # case-insensitive
    ("xx,yy", "en"),
    ("", "en"),
    (None, "en"),
])
def test_the_header_is_read_the_way_a_browser_writes_one(header, expected):
    assert i18n.negotiate(header) == expected


def test_the_console_translates_the_states_it_is_handed(client, profile_id):
    """The other half of the split, on the client side.

    The server hands back `open`; something has to turn that into a word a
    person reads. If `l10n.ts` loses the row, `Public.tsx` renders the literal
    key `pub.state.open` to somebody contesting a profile of themselves.
    """
    from pathlib import Path
    import re

    l10n = (Path(__file__).resolve().parents[1] / "app" / "src" / "l10n.ts")
    text = l10n.read_text(encoding="utf-8")
    for state in ("active", "restricted", "departed", "open", "upheld",
                  "dismissed"):
        assert f'"pub.state.{state}"' in text, (
            f"l10n.ts has no pub.state.{state} row, so the public screen "
            "shows the raw key where a state word belongs")
    public = (Path(__file__).resolve().parents[1] / "app" / "src" / "screens"
              / "Public.tsx").read_text(encoding="utf-8")
    code = re.sub(r"/\*.*?\*/|//[^\n]*|\{/\*.*?\*/\}", "", public, flags=re.S)
    assert "pub.state." in code, (
        "Public.tsx no longer looks the state up, so it is rendering the "
        "API's vocabulary at somebody instead of a word in their language")
