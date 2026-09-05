"""The pool of positions the app carries, and the way in through the search bar.

    asked     which roles can a founder open
    mattered  which roles exist

`company.plan_company` asked a model for a roster and, when the answer did
not parse, fell back to three canned seats — "Industry lead", "Front desk",
"Bookkeeper". On a deployment answering from the local stub that fallback
*is* the feature: the owner's photograph of the Company Builder showed
exactly those three, on a platform whose whole promise is a person for any
job on earth.

So the app carries the pool. Every row is one position with the two light
halves — the **digital skills** a synthetic one needs to perform it, and
the **connections** it must be able to reach to finish the work. That is
enough to browse, to search, and to fill a seat's card the moment somebody
picks it, with no model and no network.

## What is deliberately not here

The working knowledge of the profession. That is the heavy half, it is
fetched per seat by `company.study_seat()` at setup, and it is stored on
the seat and filed into the hire's own source material — so it is offline
from then on. Keeping it out is what lets an exhaustive pool stay a few
hundred kilobytes instead of a few hundred megabytes.

## Typing stays as good as picking

`search` is a way to find a row, never a wall. A founder who types a job
this pool has never heard of gets that title through unchanged — the seat
opens, `study_seat` researches it, and the result is the same seat as one
picked off the list. The pool answers the common case; it does not own the
question.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from functools import lru_cache
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data" / "occupations.json"

#: A row's stored shape is short-keyed to keep the shipped file small.
#: Nothing outside this module sees those keys.
_LONG = {"t": "title", "f": "family", "s": "skills",
         "c": "connections", "k": "keywords", "w": "written"}


@lru_cache(maxsize=1)
def _pool() -> list[dict]:
    """Every position, read once and put back together.

    The file stores what a family shares once rather than on every row —
    eight phrases repeated across a thousand rows tripled it and said
    nothing new — so a row's own skills, connections and search terms are
    added to its family's here. Callers see whole rows either way.

    A missing or unreadable file is an empty pool rather than an exception:
    the Company Builder must still open, and typing your own is always
    allowed.
    """
    try:
        raw = json.loads(DATA.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 — a broken pool is not a broken app
        return []
    fams = raw.get("families") or {}
    if not isinstance(fams, dict):        # version 1 listed names only
        fams = {}
    rows = []
    for r in raw.get("positions", []):
        row = {_LONG[k]: v for k, v in r.items() if k in _LONG}
        shared = fams.get(row.get("family"), {})
        row["skills"] = list(shared.get("s", ())) + row.get("skills", [])
        row["connections"] = list(shared.get("c", ())) + row.get("connections", [])
        row["keywords"] = row.get("keywords", []) + list(shared.get("k", ()))
        row["written"] = bool(row.get("written"))
        rows.append(row)
    return rows


def families() -> list[str]:
    """The headings a browser can walk, in the order they are shown."""
    return sorted({r["family"] for r in _pool()})


def count() -> int:
    return len(_pool())


#: Words that carry no occupation. A person types "someone who fixes
#: pipes"; only "fixes" and "pipes" say anything about the job.
_NOISE = {"the", "and", "of", "for", "to", "in", "on", "with", "who", "what",
          "someone", "somebody", "person", "that", "does", "do", "a", "an",
          "job", "role", "position", "work", "works", "working",
          # A trade is described as "a software company", "a haulage
          # firm". The legal wrapper says nothing about the trade, and
          # leaving it in put an investment analyst at the top of a
          # roster for a lorry business.
          "company", "companies", "firm", "business", "ltd", "limited",
          "inc", "llc", "plc", "corp", "corporation", "co"}


def _stem(w: str) -> str:
    """Enough stemming that "welding" reaches the welder — the same chop the
    pool was indexed with, so the two meet in the middle."""
    for suffix in ("ings", "ing", "ers", "er", "ies", "ied", "ed", "es", "s",
                   "y"):
        if len(w) - len(suffix) >= 4 and w.endswith(suffix):
            return w[: -len(suffix)]
    return w


def _terms(q: str) -> list[str]:
    out = []
    for w in re.findall(r"[a-z0-9]+", (q or "").lower()):
        if len(w) > 1 and w not in _NOISE:
            s = _stem(w)
            if s not in out:
                out.append(s)
    return out


@lru_cache(maxsize=1)
def _rarity() -> dict[str, float]:
    """How much each term is worth, by how few rows carry it.

    Every field weight below is a constant, so before this a common word
    matched in a title beat a rare word matched in the keywords every
    time: "cleans teeth" returned Building Cleaning Workers, because
    "clean" sits in the title of sixty rows and "teeth" only in the search
    terms of three. Weighting by rarity puts the distinctive half of a
    question in charge of the answer.
    """
    rows = _pool()
    seen_in = Counter()
    for row in rows:
        terms = {_stem(w) for w in
                 re.findall(r"[a-z0-9]+", row["title"].lower())}
        terms |= {_stem(w) for w in
                  re.findall(r"[a-z0-9]+", " ".join(row["skills"]).lower())}
        terms |= set(row["keywords"])
        seen_in.update(terms)
    n = max(len(rows), 1)
    # A term on every row still counts for something, so the floor is not 0.
    return {t: max(math.log(n / c), 0.25) for t, c in seen_in.items()}


def _heads(term: str, words: set[str]) -> bool:
    """Does this term begin a compound word in the title?

    A compound title should not lose to a hyphenated one for having no
    space in it. "puts out fires" met "Fire-fighters", whose title splits
    into two words and matched "fire" outright, and "Firefighter", where
    the same term could only be found as a substring and scored 12 against
    20. Same word, same job, and the difference was the punctuation.

    What is left over after the term has to be a word the pool itself
    uses, which is what makes this a compound rather than a coincidence.
    Without that clause "houses" matched "housekeeping" — leaving "ekeep"
    behind — and "builds houses" answered with housekeeping supervisors.
    """
    if len(term) < 4:
        return False                      # "car" stays out of "cardiologist"
    vocab = _rarity()
    for word in words:
        if word == term or not word.startswith(term):
            continue
        if _stem(word[len(term):]) in vocab:
            return True
    return False


def _score(row: dict, terms: list[str]) -> tuple[int, int]:
    """How well a row answers what was typed: (terms matched, strength).

    Two numbers rather than one, because a sum lets a single strong hit
    beat two weak ones — which is how "looks after old people" returned a
    scaffolder, on the strength of one keyword and nothing else. Coverage
    is ranked first and strength only breaks its ties, so a row that
    answers more of the question wins.

    A title match outranks a skill match, which outranks a keyword match:
    somebody typing "radiologist" wants the radiologist first, and
    somebody typing "reads scans" is happy to be *shown* the radiologist.
    """
    title = row["title"].lower()
    words = {_stem(w) for w in re.findall(r"[a-z0-9]+", title)}
    blob = {_stem(w) for w in
            re.findall(r"[a-z0-9]+", " ".join(row["skills"]).lower())}
    keys = set(row["keywords"])
    rare = _rarity()
    matched, strength = 0, 0.0
    for term in terms:
        weight = rare.get(term, math.log(max(len(_pool()), 1)))
        if term in words or _heads(term, words):
            hit = 20
        elif term in title:
            hit = 12
        elif term in blob:
            hit = 5
        elif term in keys:
            hit = 3
        else:
            continue
        matched, strength = matched + 1, strength + hit * weight
    if matched and title.startswith(" ".join(terms)):
        strength += 100
    if row["written"]:
        # A written row carries skills and connections of its own, so at
        # comparable relevance it is the more useful answer. A tie-break
        # alone was not enough: "puts out fires" put the taxonomy's
        # "Fire-fighters" above the written Firefighter purely because the
        # hyphen split the title into two words and turned a substring
        # match into a whole-word one. The edge is small enough that a
        # genuinely better match still wins.
        strength *= 1.1
    return matched, int(strength)


#: How much of a multi-word question a row has to answer before it is shown.
#: One word out of four is not an answer; it is the row that happened to
#: contain "people".
def _enough(matched: int, terms: int) -> bool:
    if terms <= 2:
        return matched >= 1
    return matched * 2 >= terms


def search(q: str, limit: int = 25, family: str | None = None) -> list[dict]:
    """Positions matching what was typed, best first.

    An empty query is a browse rather than a search: it returns the head of
    the pool (optionally within one family) so the list is never blank
    while somebody is deciding what to type.
    """
    rows = [r for r in _pool() if family is None or r["family"] == family]
    terms = _terms(q)
    if not terms:
        return sorted(rows, key=lambda r: (r["family"], r["title"]))[:limit]
    scored = []
    for row in rows:
        matched, strength = _score(row, terms)
        if matched and _enough(matched, len(terms)):
            scored.append((matched, strength, row))
    scored.sort(key=_rank)
    return [r for _, _, r in scored[:limit]]


def _rank(scored_row: tuple) -> tuple:
    """Best first, and on a tie the row that says more.

    A written role and a taxonomy title can answer a question equally
    well — "fixes cars" reaches both the Auto mechanic and every row with
    "mechanic" in its name — and the tie used to fall to whichever sorted
    first alphabetically, which is how a query for a car put agricultural
    machinery at the top. The written row carries skills and connections
    of its own, so it is the more useful of two equal answers.
    """
    matched, strength, row = scored_row
    return (-matched, -strength, not row["written"], row["title"])


def find(title: str) -> dict | None:
    """One position by name, matched loosely enough to survive a founder's
    capitalisation and a trailing plural."""
    want = (title or "").strip().lower().rstrip("s")
    for row in _pool():
        if row["title"].lower().rstrip("s") == want:
            return row
    return None


def for_trade(industry: str, limit: int = 50) -> list[dict]:
    """The roster to offer a company in this trade, most fitting first.

    The cap is the caller's, not this function's: `MAX_HEADCOUNT` governs
    how many seats a company may *open*, and has never governed how many it
    may be *shown*. Truncating the suggestions to the headcount was the old
    behaviour and it hid the roles a founder had not thought of, which is
    the whole reason to suggest anything.
    """
    terms = _terms(industry)
    scored, rest = [], []
    for row in _pool():
        matched, strength = _score(row, terms)
        (scored if matched else rest).append((matched, strength, row))
    scored.sort(key=_rank)
    offered = [r for _, _, r in scored[:limit]]
    if len(offered) >= limit:
        return offered

    # A trade is not a word search. "software company" names rows carrying
    # the word "software" and stops at fifteen, and a founder who asked for
    # a roster was handed a third of one — no finance seat, no operations
    # seat, none of the roles they had not thought of, which is the whole
    # reason to suggest anything. So the families the direct hits landed in
    # fill the rest, most-represented family first.
    weight: dict[str, int] = {}
    for row in offered:
        weight[row["family"]] = weight.get(row["family"], 0) + 1
    weight.setdefault("Business, people & operations", 0)
    taken = {r["title"] for r in offered}
    pool = [r for _, _, r in rest if r["family"] in weight
            and r["title"] not in taken]
    pool.sort(key=lambda r: (-weight[r["family"]], not r["written"], r["title"]))
    return offered + pool[:limit - len(offered)]
