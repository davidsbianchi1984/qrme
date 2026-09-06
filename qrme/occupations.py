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

import bisect
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
         "c": "connections", "k": "keywords", "w": "written",
         "g": "group"}


@lru_cache(maxsize=1)
def _pool() -> list[dict]:
    """Every position, read once and put back together.

    The file stores what a family shares once rather than on every row —
    eight phrases repeated across a thousand rows tripled it and said
    nothing new — so a row's own skills, connections and search terms are
    added to its family's here. Callers see whole rows either way.

    **Three tiers, narrowest first.** A row's own, then its group's,
    then its family's. The group is the shape of the work — operating a
    machine, repairing one, installing one — and it exists because
    sixteen families cannot say anything specific about forty-five
    thousand jobs: `Commercial Housekeeper` inherited "till
    reconciliation" from Hospitality until a Cleaning and housekeeping
    group got there first. Duplicates are dropped as the tiers merge, so
    a phrase a group and a family both name is shown once.

    **A row's own come first.** The family's used to lead, and every
    screen that shows a few of them showed the family's few: Radiologist
    carries "image report dictation" and "prior study comparison" and
    displayed six generic health-care skills, so a browse of 45,147
    positions read as sixteen positions repeated. The specific half is
    the half worth the first six lines; the shared half fills in behind
    it.

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
    grps = raw.get("groups") or {}        # versions 1 and 2 had no groups
    if not isinstance(grps, dict):
        grps = {}
    rows = []
    for r in raw.get("positions", []):
        row = {_LONG[k]: v for k, v in r.items() if k in _LONG}
        tiers = [grps.get(row.get("group"), {}),
                 fams.get(row.get("family"), {})]
        for short, long in (("s", "skills"), ("c", "connections"),
                            ("k", "keywords")):
            out = list(row.get(long, []))
            for tier in tiers:
                out += [x for x in tier.get(short, ()) if x not in out]
            row[long] = out
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
          "inc", "llc", "plc", "corp", "corporation", "co",
          # Size and newness, which say nothing about the trade. A "small
          # artisan bakery" and "a small app studio" both hired an
          # outdoor power equipment mechanic off the word small.
          "small", "large", "big", "little", "tiny", "new", "old",
          "local", "regional", "national", "independent", "growing"}


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
def _index() -> dict[str, list[int]]:
    """Stem to the rows carrying it.

    With the taxonomies' reported titles folded in the pool is forty-five
    thousand rows, and scoring every one of them per keystroke took the
    best part of a second. A search only has to look at rows that carry at
    least one of the words typed, which is a few hundred.
    """
    index: dict[str, list[int]] = {}
    for i, row in enumerate(_pool()):
        for term in _row_terms(row):
            index.setdefault(term, []).append(i)
    return index


@lru_cache(maxsize=1)
def _keys() -> list[str]:
    """Every stem in the index, sorted, for prefix lookups."""
    return sorted(_index())


def _row_terms(row: dict) -> set[str]:
    terms = {_stem(w) for w in re.findall(r"[a-z0-9]+", row["title"].lower())}
    terms |= {_stem(w) for w in
              re.findall(r"[a-z0-9]+", " ".join(row["skills"]).lower())}
    return terms | set(row["keywords"])


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
        seen_in.update(_row_terms(row))
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


def _candidates(terms: list[str]) -> set[int]:
    """The rows worth scoring for these terms.

    A row carrying none of the words typed cannot match, so scoring the
    whole pool was forty-five thousand wasted comparisons per keystroke.
    """
    index, keys = _index(), _keys()
    found: set[int] = set()
    for term in terms:
        found.update(index.get(term, ()))
        # A compound match reaches words the term only begins, so the
        # candidates have to include them or _heads would never be asked.
        # Walking every stem to find them cost a third of a second a
        # keystroke; the stems are sorted, so the ones starting with a
        # term are one contiguous run.
        if len(term) >= 4:
            lo = bisect.bisect_left(keys, term)
            hi = bisect.bisect_left(keys, term + "\uffff")
            for word in keys[lo:hi]:
                found.update(index[word])
    return found


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
    pool = _pool()
    terms = _terms(q)
    if not terms:
        rows = [r for r in pool if family is None or r["family"] == family]
        return sorted(rows, key=lambda r: (r["family"], r["title"]))[:limit]
    candidates = _candidates(terms)
    scored = []
    want = _plain(q)
    for i in candidates:
        row = pool[i]
        if family is not None and row["family"] != family:
            continue
        matched, strength = _score(row, terms)
        if matched and _enough(matched, len(terms)):
            scored.append((matched, strength, row, _plain(row["title"]) == want))
    scored.sort(key=_rank)
    return [x[2] for x in scored[:limit]]


def _rank(scored_row: tuple) -> tuple:
    """Best first: coverage, then the exact name, then the written row.

    The written row's edge used to be a tie-break on strength, which was
    enough against a thousand taxonomy titles and useless against forty
    thousand reported ones: "flies planes" answered with a Pilot Plant
    Operator, and "fixes cars" with a Fixed-Wing Aircraft Flight Mechanic,
    because a reported title is a *name* for work somebody already does
    and there are dozens of them around every real occupation.

    So a written row now outranks strength outright. What protects the
    reported titles from disappearing is the rung above: somebody who
    types a name exactly gets that row, whoever wrote it.
    """
    matched, strength, row, exact = scored_row
    return (-matched, not exact, not row["written"], -strength, row["title"])


def same_name(a: str, b: str) -> bool:
    """Do these two name the same job?

    Capitalisation and a trailing plural are the whole difference between
    a founder's typing and a taxonomy's entry, and between two taxonomies:
    the pool carries both "Dental Hygienist" and "Dental Hygienists",
    which are not two jobs.
    """
    return _plain(a) == _plain(b)


def _plain(title: str) -> str:
    words = []
    for w in re.findall(r"[a-z0-9]+", (title or "").lower()):
        words.append(w[:-1] if w.endswith("s") and not w.endswith("ss") else w)
    return " ".join(words)


def find(title: str) -> dict | None:
    """One position by name, matched loosely enough to survive a founder's
    capitalisation and a trailing plural."""
    for row in _pool():
        if same_name(row["title"], title):
            return row
    return None


#: A taxonomy files what it could not place into a residual bucket —
#: "All Other", "not elsewhere classified". Those are real rows and stay
#: searchable, because somebody looking for one should find it. They are
#: not roles to *offer*: a founder handed "Construction and Related
#: Workers, All Other" has been handed a filing label, not a job.
_RESIDUAL = ("all other", "not elsewhere classified", "other ranks",
             "occupations, all other")


def _residual(title: str) -> bool:
    low = title.lower()
    return any(mark in low for mark in _RESIDUAL)


def for_trade(industry: str, limit: int = 50, described: str = "") -> list[dict]:
    """The roster to offer a company in this trade, most fitting first.

    The cap is the caller's, not this function's: `MAX_HEADCOUNT` governs
    how many seats a company may *open*, and has never governed how many it
    may be *shown*. Truncating the suggestions to the headcount was the old
    behaviour and it hid the roles a founder had not thought of, which is
    the whole reason to suggest anything.
    """
    trade, said = _terms(industry), _terms(described)
    pool = _pool()
    hits = _candidates(trade)
    scored, rest = [], []
    for i, row in enumerate(pool):
        if _residual(row["title"]):
            continue
        if i not in hits:
            rest.append((0, 0, row))
            continue
        matched, strength = _score(row, trade)
        if matched:
            # The founder's own words rank within the trade, never above
            # it. Scored together, "a small artisan bakery on the high
            # street" put a university lecturer second in a bakery, on
            # the strength of the word high.
            extra = _score(row, said) if said else (0, 0)
            scored.append((matched, strength, row, extra))
        else:
            rest.append((matched, strength, row))
    # A roster is read by a founder, so the written name goes first at
    # equal coverage: "Software engineer" rather than "Software and
    # applications developers and analysts not elsewhere classified",
    # which is the same job wearing a taxonomy's filing label.
    scored.sort(key=lambda x: (-x[0], not x[2]["written"], -x[1],
                              -x[3][0], -x[3][1], x[2]["title"]))
    # Half the roster at most comes from matching the founder's words. A
    # bakery "on the high street" filled its whole roster off the word
    # street — a subway operator, a highway maintenance worker — because
    # every seat was a word match and there was no room left for the job
    # the sign says.
    direct = max(1, limit // 2)
    offered = [x[2] for x in scored[:direct]]
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
